from sqlalchemy.orm import Session
from ..models.user_encoding import UserEncoding
from fastapi_pagination.ext.sqlalchemy import paginate
from ..models.enums.user_encoding_sort import UserEncodingSort
from ..models.enums.sort_type import Sort
from ..models.enums.ownership import Ownership
from ..models.tag import Tag
from ..models.encoding import Encoding
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.sql import func


class UserEncodingRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, user_encoding: UserEncoding):
        self.db.add(user_encoding)
        self.db.flush()
        self.db.refresh(user_encoding)
        return user_encoding

    def get_encoding_by_user_id_with_filters(self, user_id, filters: dict):
        query = self._get_encoding_by_user_id(user_id)
        query = self._get_user_encoding_filter_query(filters, query)
        return paginate(query)

    def get_encoding_by_user_id_with_filers_and_sort(
        self, user_id, filters: dict, order: UserEncodingSort | None, sort: Sort
    ):
        query = self._get_encoding_by_user_id(user_id)
        if sort is not None:
            query = self._get_user_encoding_sort_query(sort, query, order)
        query = self._get_user_encoding_filter_query(filters, query)
        return paginate(query)

    def _get_encoding_by_user_id(self, user_id):
        return (
            self.db.query(UserEncoding)
            .filter(UserEncoding.user_id == user_id)
            .join(UserEncoding.encoding)
        )

    def _get_user_encoding_sort_query(self, sort: UserEncodingSort, query, order: Sort):
        sort_mapping = {
            UserEncodingSort.NAME: Encoding.name,
            UserEncodingSort.VISIBILITY: Encoding.is_public,
            UserEncodingSort.ROLE: UserEncoding.ownership,
            UserEncodingSort.UPLOAD_DATE: Encoding.upload_date,
        }
        order_by = sort_mapping.get(sort)
        if order == Sort.DESC:
            order_by = order_by.desc()
        return query.order_by(order_by)

    def _get_user_encoding_filter_query(self, filters: dict, query):
        if "name" in filters:
            query = query.filter(Encoding.name.contains(filters["name"]))
        if "start_upload_date" in filters:
            query = query.filter(Encoding.upload_date >= filters["start_upload_date"])
        if "end_upload_date" in filters:
            query = query.filter(Encoding.upload_date <= filters["end_upload_date"])
        if "tags" in filters:
            # comment line 55 and 61 for a or filter, uncomment for an and filter
            tag_count = len(filters["tags"])  # Number of tags to match
            query = query.join(Encoding.tags).filter(Tag.name.in_(filters["tags"]))
            # Join the Tag table ( Encoding has a many-to-many relationship with Tag through a join table)

            # Group by the encoding and ensure the number of distinct matching tags is equal to the number of tags in the filter
            query = query.group_by(Encoding.id).having(
                func.count(func.distinct(Tag.name)) == tag_count
            )
            # query = query.filter(Tag.name.in_(filters['tags']))
            query = query.filter(Encoding.tags != None)

        return query

    def exists_by_name_and_user_id(self, name: str, user_id: str):
        return (
            self.db.query(UserEncoding)
            .filter(
                UserEncoding.user_id == user_id
                and UserEncoding.ownership == Ownership.OWNER
            )
            .join(UserEncoding.encoding)
            .filter(Encoding.name == name)
            .first()
            is not None
        )

    def find_public_encodings_by_user_id(self, user_id):
        query = (
            self.db.query(UserEncoding)
            .filter(UserEncoding.user_id == user_id)
            .join(UserEncoding.encoding)
            .filter(Encoding.is_public == True)
        )
        return paginate(self.db, query)

    def delete_user_encoding_by_encoding_id(self, encoding_id):
        self.db.query(UserEncoding).filter(
            UserEncoding.encoding_id == encoding_id,
            UserEncoding.ownership != Ownership.OWNER,
        ).delete()
        self.db.flush()

    def get_user_owner(self, encoding_id):
        return (
            self.db.query(UserEncoding)
            .filter(
                UserEncoding.encoding_id == encoding_id,
                UserEncoding.ownership == Ownership.OWNER,
            )
            .first()
        )
