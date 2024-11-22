from sqlalchemy.orm import Session
from ..models import user as user_model
from ..models import role
from ...util import bcrypt
from sqlalchemy.sql import func
from ..models import certification_request as certification_request_model
from fastapi_pagination.ext.sqlalchemy import paginate
from ...data.models.enums import user_sort
from ..models import role as role_model
from ...data.models.enums import sort_type
from uuid import UUID


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def _get_user_query(self):
        return (
            self.db.query(
                user_model.User.id,
                user_model.User.email,
                user_model.User.username,
                user_model.User.full_name,
                user_model.User.oauth2_user,
                user_model.User.disabled,
                certification_request_model.CertificationRequest.status.label(
                    "certification_status"
                ),
                func.group_concat(role.Role.name).label("roles"),
            )
            .join(user_model.User.certification_request, isouter=True)
            .join(user_model.User.roles, isouter=True)
            .group_by(user_model.User.id)
        )

    def _get_user_filter_query(self, filters: dict, query):
        if "username" in filters:
            query = query.filter(user_model.User.username.contains(filters["username"]))
        if "email" in filters:
            query = query.filter(user_model.User.email.contains(filters["email"]))
        if "full_name" in filters:
            query = query.filter(
                user_model.User.full_name.contains(filters["full_name"])
            )
        return query

    def _get_user_sort_query(
        self, sort: user_sort.UserSort, query, order: sort_type.Sort
    ):
        sort_mapping = {
            user_sort.UserSort.USERNAME: user_model.User.username,
            user_sort.UserSort.EMAIL: user_model.User.email,
            user_sort.UserSort.FULL_NAME: user_model.User.full_name,
            user_sort.UserSort.DISABLED: user_model.User.disabled,
            user_sort.UserSort.OAUTH2_USER: user_model.User.oauth2_user,
            user_sort.UserSort.ROLES: role_model.Role.name,
            user_sort.UserSort.CERTIFICATION_STATUS: certification_request_model.CertificationRequest.status,
        }
        order_by = sort_mapping.get(sort)
        if order == sort_type.Sort.DESC:
            order_by = order_by.desc()
        return query.order_by(order_by)

    def get_users(
        self,
        filters: dict,
        sort: user_sort.UserSort | None = None,
        order: sort_type.Sort = sort_type.Sort.ASC,
    ):
        query = self._get_user_query()
        if sort is not None:
            query = self._get_user_sort_query(sort, query, order)
        query = self._get_user_filter_query(filters, query)
        return paginate(self.db, query)

    def get_user(self, username: str):
        return (
            self.db.query(user_model.User)
            .filter(user_model.User.username == username)
            .first()
        )

    def find_by_id(self, id: str):
        return self.db.query(user_model.User).filter(user_model.User.id == id).first()

    def get_user_from_id_and_roles(self, user_id: str, roles: set[str]):
        user = (
            self.db.query(user_model.User).filter(user_model.User.id == user_id).first()
        )
        if not user:
            return None
        for role in user.roles:
            if role.name not in roles:
                return None
        return user

    def create_user(
        self,
        email: str,
        username: str,
        full_name: str,
        password: str,
        roles: set[role.Role],
        oauth2_user: bool = False,
    ):
        hashed_password = bcrypt.get_password_hash(password=password)
        new_user = user_model.User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            roles=roles,
            oauth2_user=oauth2_user,
        )
        self.db.add(new_user)
        self.db.flush()
        self.db.refresh(new_user)
        return new_user

    def find_user_by_email_or_username(self, email: str, username: str):
        return (
            self.db.query(user_model.User)
            .filter(
                (user_model.User.email == email)
                | (user_model.User.username == username)
            )
            .first()
        )

    def find_user_by_email(self, email: str):
        return (
            self.db.query(user_model.User)
            .filter(user_model.User.email == email)
            .first()
        )

    def delete_user(self, user_id: str):
        self.db.query(user_model.User).filter(user_model.User.id == user_id).delete()

    def find_user_by_username(self, username: str):
        return (
            self.db.query(user_model.User)
            .filter(user_model.User.username == username)
            .first()
        )

    def update_user(self, user: user_model.User):
        self.db.add(user)
        self.db.flush()

    def get_users_count(
        self, disabled: bool | None = None, oauth2_user: bool | None = None
    ):
        query = self.db.query(user_model.User)
        if disabled is not None and oauth2_user is not None:
            query = query.filter(
                user_model.User.disabled == disabled,
                user_model.User.oauth2_user == oauth2_user,
            )
            return query.count()
        if disabled is not None:
            query = query.filter(user_model.User.disabled == disabled)
        if oauth2_user is not None:
            query = query.filter(user_model.User.oauth2_user == oauth2_user)
        return query.count()

    def get_users_by_usernames_with_role_user_without_current_user(
        self, username: str, user_id: UUID
    ):
        query = self.db.query(user_model.User).filter(
            user_model.User.username.contains(username)
        )
        query = query.join(role.Role, user_model.User.roles, isouter=True)
        query = query.filter(role.Role.name == "ROLE_USER")
        query = query.filter(user_model.User.id != user_id)
        return paginate(self.db, query)

    def get_usernames_with_role_user_without_current_user(self, user_id: UUID):
        query = self.db.query(user_model.User)
        query = query.join(role.Role, user_model.User.roles, isouter=True)
        query = query.filter(role.Role.name == "ROLE_USER")
        query = query.filter(user_model.User.id != user_id)
        return paginate(self.db, query)

    def is_not_only_admin_by_username(self, username: str):
        # Query the user by username
        query = self.db.query(user_model.User).filter(
            user_model.User.username == username
        )

        # Join the user with the roles table
        query = query.join(user_model.User.roles)

        # Check if there is any role that is not 'ROLE_ADMIN'
        return query.filter(role.Role.name != "ROLE_ADMIN").count() > 0

    def is_admin(self, user_id: UUID):
        query = self.db.query(user_model.User).filter(user_model.User.id == user_id)
        query = query.join(user_model.User.roles)
        return query.filter(role.Role.name == "ROLE_ADMIN").count() > 0
