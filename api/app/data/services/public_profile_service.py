from sqlalchemy.orm import Session
from app.data.repository.user_repository import UserRepository
from ...schemas.user_schemas import UserPublic
from ...schemas.encoding_schema import EncodingPublicDetail
from app.data.repository.user_encoding_repository import UserEncodingRepository
from app.data.repository.encoding_repository import EncodingRepository


class PublicProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.encoding_repository = EncodingRepository(db)
        self.user_encoding_repository = UserEncodingRepository(db)

    def get_public_profile(self, username: str):
        user = self.user_repository.find_user_by_username(username)
        if user is None:
            return None
        public_profile = UserPublic(username=user.username, full_name=user.full_name)
        return public_profile

    def get_public_encodings(self, username: str):
        user = self.user_repository.find_user_by_username(username)
        if user is None:
            return None
        return self.user_encoding_repository.find_public_encodings_by_user_id(user.id)

    def get_public_encoding(self, username: str, encoding_name: str, base_url: str):
        user = self.user_repository.find_user_by_username(username)
        if user is None:
            return None
        encoding = (
            self.encoding_repository.find_public_encoding_by_user_id_and_encoding_name(
                user.id, encoding_name
            )
        )
        if encoding is None:
            return None
        encoding_out = EncodingPublicDetail.model_validate(encoding)
        encoding_out.file_url = f"{base_url}/v1/encodings/{encoding.id}/file"
        return encoding_out
