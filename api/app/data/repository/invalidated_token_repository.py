from sqlalchemy.orm import Session
from ..models import invalidated_token as invalidated_token_model
from datetime import datetime
from uuid import UUID


class InvalidatedTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_invalidated_token(self, token: str, expires_at: datetime, user_id: UUID):
        db_invalidated_token = invalidated_token_model.InvalidatedToken(
            token=token, expires_at=expires_at, user_id=user_id
        )
        self.db.add(db_invalidated_token)
        self.db.flush()

    def is_token_invalid(self, token: str):
        return (
            self.db.query(invalidated_token_model.InvalidatedToken)
            .filter(invalidated_token_model.InvalidatedToken.token == token)
            .first()
            is not None
        )
