import os
from pydantic_settings import BaseSettings, SettingsConfigDict

_env_file_path = os.path.join(os.path.dirname(__file__), ".env")
class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=_env_file_path, extra="ignore")
    URI: str
config = Config()
