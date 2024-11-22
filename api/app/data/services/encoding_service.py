from typing import Optional
from sqlalchemy.orm import Session
from ..repository.encoding_repository import EncodingRepository
from ..repository.user_encoding_repository import UserEncodingRepository
from ..repository.user_repository import UserRepository
from ..repository.tag_repository import TagRepository
from ...schemas.encoding_schema import EncodingIn, EncodingPublicDetail, EncodingPatch
from ...data.models.encoding import Encoding
from ...data.models.user_encoding import UserEncoding
from ...data.models.tag import Tag
from ...schemas.encoding_schema import EncodingCount
from ...data.models.change import Change
import uuid
import datetime
from ...data.repository.change_repository import ChangeRepository
from ..models.enums.ownership import Ownership
from ...util import cryptography
from ...data.models.enums.sort_type import Sort
from ...data.models.enums.user_encoding_sort import UserEncodingSort
from fastapi import UploadFile
from ...schemas import token_schemas
from ...util import token
import logging


logger = logging.getLogger(__name__)


class EncodingService:
    def __init__(self, db: Session):
        self.db = db
        self.encoding_repository = EncodingRepository(db)
        self.tag_repository = TagRepository(db)
        self.user_encoding_repository = UserEncodingRepository(db)
        self.user_repository = UserRepository(db)
        self.change_repository = ChangeRepository(db)

    async def save_encoding(
        self,
        user_id: uuid.UUID,
        encoding_in: EncodingIn,
        signature: UploadFile,
        encoding: UploadFile,
    ):
        # getting user
        user = self.user_repository.find_by_id(user_id)
        if user is None or user.public_key is None:
            logger.warning(f"User {user_id} not found or has no public key")
            return

        encoding_to_save = Encoding()  # saving encoding

        encoding_to_save.name = encoding_in.name
        encoding_to_save.description = encoding_in.description
        encoding_to_save.is_public = encoding_in.is_public
        encoding_to_save.owner_username = user.username
        try:
            # Reset the pointer to the beginning of the file (encoding)
            await encoding.seek(0)
            file_content = await encoding.read()

            # Reset the pointer to the beginning of the file (signature)
            await signature.seek(0)
            signature_content = await signature.read()
            encoding_to_save.file = cryptography.generate_encoding_file(
                file_content, signature_content, encoding_to_save.owner_username, encoding_to_save.name
            )
        except Exception as e:
            logger.error(f"Error reading files: {e}")
            raise e
        saved_encoding = self.encoding_repository.save(encoding_to_save)

        new_change = Change()  # saving change
        new_change.description = "Encoding created"
        new_change.updated_by = user.username
        new_change.encoding = saved_encoding
        self.change_repository.save(new_change)

        user_owner = UserEncoding()  # saving user as owner
        user_owner.user = user
        user_owner.encoding = saved_encoding
        user_owner.ownership = Ownership.OWNER
        self.user_encoding_repository.save(user_owner)
        for team in encoding_in.teams:  # saving others team members
            user = self.user_repository.find_user_by_username(team.name)
            if user is None:
                logger.warning(f"User {team.name} not found")
                continue
            user_to_save = UserEncoding()
            user_to_save.user = user
            user_to_save.encoding = saved_encoding
            user_to_save.ownership = team.ownership
            self.user_encoding_repository.save(user_to_save)
        for tag in encoding_in.tags:  # saving tags
            saved_tag = self.tag_repository.find_by_name(tag.name)
            if saved_tag is None:
                new_tag = Tag()
                new_tag.name = tag.name
                saved_tag = self.tag_repository.save(new_tag)
            saved_tag.encodings.add(saved_encoding)
            self.tag_repository.save(saved_tag)
        self.db.commit()
        return

    def check_encoding_signature(
        self, encoding: UploadFile, signature: UploadFile, user_id: uuid.UUID
    ):
        user = self.user_repository.find_by_id(user_id)
        if user is None or user.public_key is None:
            logger.warning(f"User {user_id} not found or has no public key")
            return False
        encoding_file = encoding.file.read()
        signature_file = signature.file.read().decode("utf-8")
        value = cryptography.check_signature(
            encoding_file, signature_file, user.public_key
        )
        return value

    def get_user_encodings(
        self,
        user_id: uuid.UUID,
        order: Sort,
        sort: UserEncodingSort | None,
        filters: dict,
    ):
        if sort is None:
            return self.user_encoding_repository.get_encoding_by_user_id_with_filters(
                user_id, filters
            )
        return (
            self.user_encoding_repository.get_encoding_by_user_id_with_filers_and_sort(
                user_id=user_id, order=order, sort=sort, filters=filters
            )
        )

    def exists_by_name_and_user_id(self, name: str, user_id: uuid.UUID):
        return self.user_encoding_repository.exists_by_name_and_user_id(name, user_id)

    def exists_by_id(self, encoding_id: int):
        return self.encoding_repository.exists_by_id(encoding_id)

    def find_by_id(self, encoding_id):
        return self.encoding_repository.find_by_id(encoding_id)

    def get_encoding_file(self, encoding_id):
        encoding = self.encoding_repository.find_by_id(encoding_id)
        if encoding is None:
            return None
        return encoding.file

    def get_encoding_by_user_id_and_name(
        self, user_id: uuid.UUID, name: str, base_url: str, owner_username: str
    ):
        user = self.user_repository.find_by_id(user_id)
        owner = self.user_repository.find_user_by_username(owner_username)
        if user is None or owner is None:
            return None
        encoding = self.encoding_repository.find_by_owner_username_and_current_user(
            name, owner.id
        )
        if encoding is None:
            return None
        encoding_out = None
        for user_encoding in encoding.user_encodings:
            if user_encoding.user_id == user_id:
                encoding_out = EncodingPublicDetail.model_validate(encoding)
                encoding_out.file_url = f"{base_url}/v1/encodings/{encoding.id}/file"
                if user_encoding.ownership != Ownership.OWNER:
                    encoding_out.capability_token = None
                    encoding_out.user_encodings = []
                return encoding_out

        return encoding_out

    def get_encoding_by_encoding_id(self, encoding_id: uuid.UUID, base_url: str):
        encoding = self.encoding_repository.find_by_id(encoding_id)
        if encoding is None:
            return None
        encoding_out = None

        encoding_out = EncodingPublicDetail.model_validate(encoding)
        encoding_out.file_url = f"{base_url}/v1/encodings/{encoding.id}/file"
        return encoding_out

        return encoding_out

    def get_changes(self, encoding_id):
        return self.change_repository.get_changes_by_encoding_id(encoding_id)

    def create_token(self, encoding_id: uuid.UUID, current_user_username: str):
        encoding = self.encoding_repository.find_by_id(encoding_id)
        new_token = token.create_encoding_token(encoding_id.__str__())
        encoding.capability_token = new_token
        self.encoding_repository.save(encoding)
        new_change = Change()
        new_change.description = "Create a sharing link"
        new_change.updated_by = current_user_username
        new_change.encoding = encoding
        self.change_repository.save(new_change)
        self.db.commit()
        return token_schemas.TokenEncodingOut(token=new_token)

    def get_encoding_by_token(self, token_string: str):
        encoding_id = token.get_encoding_if_from_token(token_string)
        if encoding_id is None:
            return None
        encoding = self.encoding_repository.find_by_id(uuid.UUID(encoding_id))
        if encoding.capability_token != token_string:
            return None
        return encoding

    def delete_token(self, encoding_id: uuid.UUID, username: str):
        encoding = self.encoding_repository.find_by_id(encoding_id)
        if encoding is None:
            return
        encoding.capability_token = None
        self.encoding_repository.save(encoding)
        new_change = Change()
        new_change.description = "Delete a sharing link"
        new_change.encoding = encoding
        new_change.updated_by = username
        self.change_repository.save(new_change)
        self.db.commit()
        return

    def delete_encoding(self, encoding_id: uuid.UUID):
        encoding = self.encoding_repository.find_by_id(encoding_id)
        if encoding is None:
            return
        self.encoding_repository.delete(encoding)
        self.db.commit()
        return

    async def update_encoding(
        self,
        user_id: uuid.UUID,
        encoding_id: uuid.UUID,
        encoding_in: EncodingPatch,
        signature: Optional[UploadFile] = None,
        encoding: Optional[UploadFile] = None,
    ):
        # getting user
        user = self.user_repository.find_by_id(user_id)
        if user is None or user.public_key is None:
            logger.warning(f"User {user_id} not found or has no public key")
            return
        encoding_to_update = self.encoding_repository.find_by_id(encoding_id)
        if encoding_to_update is None:
            logger.warning(f"Encoding {encoding_id} not found")
            return
        changes = []
        if encoding_in.name is not None:
            changes.append(
                f"Name changed from {encoding_to_update.name} to {encoding_in.name}"
            )
            encoding_to_update.name = encoding_in.name
        if encoding_in.description is not None:
            changes.append(
                f"Description changed from {encoding_to_update.description} to {encoding_in.description}"
            )
            encoding_to_update.description = encoding_in.description
        if encoding_in.is_public is not None:
            changes.append(
                f"Encoding set to {'public' if encoding_in.is_public else 'private'}"
            )
            encoding_to_update.is_public = encoding_in.is_public
        if signature is not None and encoding is not None:
            changes.append("Signature and encoding updated")
            try:
                # Reset the pointer to the beginning of the file (encoding)
                await encoding.seek(0)
                file_content = await encoding.read()

                # Reset the pointer to the beginning of the file (signature)
                await signature.seek(0)
                signature_content = await signature.read()
                encoding_to_update.file = cryptography.generate_encoding_file(
                    file_content, signature_content, encoding_to_update.owner_username, encoding_to_update.name
                )
            except Exception as e:
                logger.error(f"Error reading files: {e}")
                return
    
        saved_encoding = self.encoding_repository.save(encoding_to_update)

        if len(encoding_in.teams) > 0:
            self.user_encoding_repository.delete_user_encoding_by_encoding_id(
                encoding_id
            )

        for team in encoding_in.teams:  # saving others team members
            if team.ownership == Ownership.OWNER:
                continue
            user = self.user_repository.find_user_by_username(team.name)
            if user is None:
                logger.warning(f"User {team.name} not found")
                continue
            if team.ownership != Ownership.OWNER:
                user_to_save = UserEncoding()
                user_to_save.user = user
                user_to_save.encoding = saved_encoding
                user_to_save.ownership = team.ownership
                self.user_encoding_repository.save(user_to_save)

        if len(encoding_in.tags) > 0:
            self.tag_repository.delete_tags_by_encoding_id(encoding_id)

        for tag in encoding_in.tags:  # saving tags
            saved_tag = self.tag_repository.find_by_name(tag.name)
            if saved_tag is None:
                new_tag = Tag()
                new_tag.name = tag.name
                saved_tag = self.tag_repository.save(new_tag)
            if all(encoding.id != encoding_id for encoding in saved_tag.encodings):
                changes.append(f"Tag {tag.name} added")

            saved_tag.encodings.add(saved_encoding)
            self.tag_repository.save(saved_tag)
        for change in changes:
            new_change = Change()
            new_change.description = change
            new_change.updated_by = user.username
            new_change.encoding = saved_encoding
            self.change_repository.save(new_change)
        self.db.commit()
        return

    def get_encoding_count(self):
        encoding_counts = self.encoding_repository.get_encoding_count()

        counts_list = [(month, count) for month, count in encoding_counts.items()]

        return EncodingCount(count=counts_list)

    def find_by_user_id_and_encoding_file(
        self, user_id: uuid.UUID, encoding_file: bytes
    ):
        return self.encoding_repository.find_by_user_id_and_encoding_file(
            user_id, encoding_file
        )

    def decrypt_encoding_file(self, encoding_file: bytes, public_key: str):
        decrypted_file = cryptography.decrypt(encoding_file)
        logger.debug(f"Decrypted file: {decrypted_file}")
        signature, file = cryptography.split_encoding_and_signature(decrypted_file)

        if not cryptography.check_signature(file, signature, public_key):
            return None
        return decrypted_file

    def get_user_owner(self, encoding_id: uuid.UUID):
        return self.user_encoding_repository.get_user_owner(encoding_id)
