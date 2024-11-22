from ..repository.invalidated_token_repository import InvalidatedTokenRepository
from sqlalchemy.orm import Session


class InvalidatedTokenService:
    def __init__(self, db: Session):
        self.db = db
        self.invalidated_token_repository = InvalidatedTokenRepository(db)

    def is_token_invalid(self, token: str):
        return self.invalidated_token_repository.is_token_invalid(token)

    def save_invalidated_token(self, token: str, expires_at, user_id):
        self.invalidated_token_repository.save_invalidated_token(
            token, expires_at, user_id
        )
        self.db.commit()
