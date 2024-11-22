from sqlalchemy.orm import Session
from ..repository.role_repository import RoleRepository


class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.role_repository = RoleRepository(db)

    def get_roles(self):
        roles = self.role_repository.find_all()
        return [role.name for role in roles]
