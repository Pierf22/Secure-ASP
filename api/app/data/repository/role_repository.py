from sqlalchemy.orm import Session
from ..models import role as role_model
from ..models import user as user_model


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_name(self, name: str):
        return (
            self.db.query(role_model.Role).filter(role_model.Role.name == name).first()
        )

    def find_all(self):
        return self.db.query(role_model.Role).all()
    def is_user(self, user_id):
        return self.db.query(user_model.User).join(user_model.User.roles).filter(user_model.User.id == user_id and role_model.Role.name == "ROLE_USER").first() is not None
