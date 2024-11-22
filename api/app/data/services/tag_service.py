from sqlalchemy.orm import Session
from ..repository.tag_repository import TagRepository


class TagService:
    def __init__(self, db: Session):
        self.db = db
        self.role_repository = TagRepository(db)

    def get_tags(self, name: str | None):
        if name:
            return self.role_repository.find_by_contains_name(name)
        return self.role_repository.find_all()
