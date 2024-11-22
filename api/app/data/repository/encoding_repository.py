from uuid import UUID
from sqlalchemy.orm import Session
from ..models.encoding import Encoding
from ..models.user_encoding import UserEncoding
from ..models.enums.ownership import Ownership
from ..models.user import User
from datetime import datetime
from sqlalchemy.sql import func, extract, or_
import logging
logger = logging.getLogger(__name__)


class EncodingRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, encoding: Encoding):
        self.db.add(encoding)
        return encoding

    def get_encoding_by_username(self, username):
        return (
            self.db.query(Encoding)
            .join(UserEncoding)
            .join(User)
            .filter(User.username == username)
            .all()
        )

    def get_encoding_by_username_and_name(self, username, name):
        return (
            self.db.query(Encoding)
            .join(UserEncoding)
            .join(User)
            .filter(User.username == username)
            .filter(Encoding.name == name)
        )

    def find_public_encoding_by_user_id_and_encoding_name(self, user_id, encoding_name):
        return (
            self.db.query(Encoding)
            .join(UserEncoding)
            .filter(
                UserEncoding.user_id == user_id
                and UserEncoding.ownership == Ownership.OWNER
            )
            .filter(Encoding.name == encoding_name)
            .filter(Encoding.is_public == True)
            .first()
        )

    def exists_by_id(self, id):
        return self.db.query(Encoding).filter(Encoding.id == id).count() > 0

    def find_by_id(self, id):
        return self.db.query(Encoding).filter(Encoding.id == id).first()

    def find_by_owner_username_and_current_user(
        self, encoding_name: str, owner_id: UUID
    ):
        # Step 1: Query the Encoding and filter by owner_id and encoding_name
        query = (
            self.db.query(Encoding)
            .join(UserEncoding)
            .filter(
                UserEncoding.user_id == owner_id,
                UserEncoding.ownership == Ownership.OWNER,
                Encoding.name == encoding_name,
            )
        )

        return query.first()

    def delete(self, encoding: Encoding):
        self.db.delete(encoding)

    def delete_encodings_by_user_id_owner(self, user_id):
        encodings_to_delete = (
            self.db.query(Encoding)
            .join(UserEncoding)
            .filter(
                UserEncoding.user_id == user_id
            )
            .all()
        )
        logger.info(f"Deleting {len(encodings_to_delete)} encodings")
        for encoding in encodings_to_delete:
            self.db.delete(encoding)
        self.db.flush()

    def get_encoding_count(self):
        today = datetime.today()
        months = [
            (
                (today.year, today.month - i)
                if today.month - i > 0
                else (today.year - 1, 12 + (today.month - i))
            )
            for i in range(1, 13)
        ]
        results = []
        for year, month in months:
            count = (
                self.db.query(func.count(Encoding.upload_date))
                .filter(extract("year", Encoding.upload_date) == year)
                .filter(extract("month", Encoding.upload_date) == month)
                .scalar()
            )
            results.append((month, count))

        return dict(results)

    def find_by_user_id_and_encoding_file(self, user_id: UUID, file: bytes):
        return (
            self.db.query(UserEncoding)
            .join(Encoding)
            .filter(or_(UserEncoding.user_id == user_id , Encoding.is_public == True))
            .filter(Encoding.file == file)
            .first()
        )
