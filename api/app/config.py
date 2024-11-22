from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
def get_settings():
    return Settings()


class Settings(BaseSettings):
    sqlalchemy_database_url: str
    github_client_id: str
    github_client_secret: str
    origins: list[str]
    base_url: str

    model_config = SettingsConfigDict(env_file=".env")


allowed_types: list[str] = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
max_file_size: int = 10 * 1024 * 1024  # 10 MB in bytes
allowed_mime_type_csr = "application/x-x509-ca-cert"
max_file_size_csr = 10 * 1024 * 1024  # 10 MB
allowed_encoding_types: list[str] = [
    "text/plain",  # for .txt files
    "application/octet-stream",  # for files with no extension
    "application/x-asp",
]  # for .asp files
allowed_signature_types: list[str] = [
    "application/vnd.sealed.sig",  # for .sig files
    "application/vnd.sealed.sign",  # for .sign files
    "application/sha256",  # for sha256 hash files
    "application/octet-stream",  # for generic binary files  and .bin
]
max_encoding_size: int = 100 * 1024 * 1024  # 100 MB in bytes
max_signature_size: int = 1 * 1024 * 1024  # 1 MB in bytes
