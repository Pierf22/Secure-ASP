from fastapi import APIRouter, Depends
from ...data.services.auth_service import is_admin
from ...util.database import get_db
from sqlalchemy.orm import Session
from typing import Annotated
from ...data.services.role_service import RoleService
from ...schemas.message_schema import ErrorMessage

router = APIRouter(prefix="/v1/roles", tags=["roles"], dependencies=[Depends(is_admin)])


@router.get(
    "",
    description="Get all roles",
    response_model=list[str],
    responses={
        401: {"description": "Incorrect username or password", "model": ErrorMessage},
        403: {"description": "Unauthorized", "model": ErrorMessage},
    },
)
async def get_roles(db: Annotated[Session, Depends(get_db)]):
    _role_service = RoleService(db)
    return _role_service.get_roles()
