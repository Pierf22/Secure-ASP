from sqlalchemy.orm import Session
from ...data.models.tag import Tag
from ...data.models.encoding import encoding_tag_table
from fastapi_pagination.ext.sqlalchemy import paginate


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_all(self):
        query = self.db.query(Tag)
        return paginate(self.db, query)

    def find_by_contains_name(self, name: str):
        query = self.db.query(Tag).filter(Tag.name.contains(name))
        return paginate(self.db, query)

    def find_by_name(self, name: str):
        query = self.db.query(Tag).filter(Tag.name == name)
        return query.first()

    def save(self, tag: Tag):
        self.db.add(tag)
        self.db.flush()
        self.db.refresh(tag)
        return tag

    def delete_tags_by_encoding_id(self, encoding_id):
        self.db.query(encoding_tag_table).filter(
            encoding_tag_table.c.encoding == encoding_id
        ).delete()
