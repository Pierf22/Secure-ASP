from ..repository.user_repository import UserRepository
from ..repository.certification_request_repository import CertificationRequestRepository
from sqlalchemy.orm import Session
from ..repository.role_repository import RoleRepository
from ...util import storage
from ...schemas import user_schemas
from ...data.models import user as user_model
from ...data.repository.encoding_repository import EncodingRepository
from ...util import bcrypt
from uuid import UUID
from ...data.models.enums import sort_type, user_sort
from ...data.models.enums.request_status import RequestStatus


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.certification_request_repository = CertificationRequestRepository(db)
        self.encoding_repository = EncodingRepository(db)
        self.role_repository = RoleRepository(db)
    

    def find_by_id(self, id):
        return self.user_repository.find_by_id(id)

    def delete_user(self, user_id):
        certification_request = self.certification_request_repository.find_by_user_id(
            user_id=user_id
        )
        if certification_request:
            storage.delete_directory_user_documents(str(certification_request.id))
        self.encoding_repository.delete_encodings_by_user_id_owner(user_id)
        self.user_repository.delete_user(user_id)

        self.db.commit()

    def find_user_by_email(self, email):
        return self.user_repository.find_user_by_email(email)

    def find_user_by_username(self, username):
        return self.user_repository.get_user(username)

    def update_user(self, user_id: UUID, user: user_schemas.UserEdit):
        db_user = self.user_repository.find_by_id(user_id)
        if user.email is not None:
            db_user.email = user.email
        if user.username is not None:
            db_user.username = user.username
        if user.full_name is not None:
            db_user.full_name = user.full_name
        if user.disabled is not None:
            db_user.disabled = user.disabled
        if user.roles is not None:
            roles = set()
            for role_name in user.roles:
                role = self.role_repository.find_by_name(role_name)
                if role is not None:
                    roles.add(role)
            db_user.roles = roles
        if self.role_repository.is_user(user_id):
            self.encoding_repository.delete_encodings_by_user_id_owner(user_id)

        if user.password is not None:
            db_user.hashed_password = bcrypt.get_password_hash(user.password)
        self.user_repository.update_user(db_user)
        self.db.commit()

    def find_user_from_id_and_roles(self, user_id, roles):
        return self.user_repository.get_user_from_id_and_roles(user_id, roles)

    def find_user_by_email_or_username(self, email, username):
        return self.user_repository.find_user_by_email_or_username(email, username)

    def create_user(self, user: user_schemas.UserCreate, oauth2_user=False):
        role = self.role_repository.find_by_name("ROLE_USER")
        roles = {role}
        saved_user = self.user_repository.create_user(
            oauth2_user=oauth2_user,
            email=user.email,
            full_name=user.full_name,
            password=user.password,
            username=user.username,
            roles=roles,
        )
        self.db.commit()
        return saved_user

    def get_user_count(self):
        total_users = self.user_repository.get_users_count()
        disabled_users = self.user_repository.get_users_count(disabled=True)
        active_users = self.user_repository.get_users_count(disabled=False)
        oauth2_users = self.user_repository.get_users_count(oauth2_user=True)
        username_password_users = self.user_repository.get_users_count(
            oauth2_user=False
        )
        return user_schemas.UserCount(
            active=active_users,
            disabled=disabled_users,
            total=total_users,
            oauth2=oauth2_users,
            username_password=username_password_users,
        )

    def get_users(
        self, order: sort_type.Sort, sort: user_sort.UserSort | None, filters: dict
    ):
        if sort is None:
            return self.user_repository.get_users(filters)
        return self.user_repository.get_users(order=order, sort=sort, filters=filters)

    def is_certificated(self, user: user_model.User):
        return (
            user.certification_request is not None
            and user.certification_request.status == RequestStatus.APPROVED
        )

    def get_usernames(self, username: str | None, userId: UUID):
        if username is None:
            return (
                self.user_repository.get_usernames_with_role_user_without_current_user(
                    userId
                )
            )
        return self.user_repository.get_users_by_usernames_with_role_user_without_current_user(
            username, userId
        )

    def is_not_only_admin_by_username(self, username: str):
        return self.user_repository.is_not_only_admin_by_username(username)

    def update_public_key(self, user_id: UUID, public_key: str):
        user = self.user_repository.find_by_id(user_id)
        if user.public_key is not None:
            self.encoding_repository.delete_encodings_by_user_id_owner(user_id)
        user.public_key = public_key
        self.user_repository.update_user(user)
        self.db.commit()

    def is_admin(self, user_id: UUID):
        return self.user_repository.is_admin(user_id)
