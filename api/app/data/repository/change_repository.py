from sqlalchemy.orm import Session
from ...data.models.change import Change
from fastapi_pagination.ext.sqlalchemy import paginate


class ChangeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_changes_by_encoding_id(self, encoding_id):
        return paginate(
            self.db,
            self.db.query(Change)
            .filter(Change.encoding_id == encoding_id)
            .order_by(Change.timestamp.desc()),
        )

    def save(self, change: Change):
        self.db.add(change)
