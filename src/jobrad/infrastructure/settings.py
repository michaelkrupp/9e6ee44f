import logging
from typing import Final, Required

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME: Final[str] = __name__.split(".")[0]
ENV_PREFIX: Final[str] = APP_NAME.upper() + "_"

load_dotenv("etc/environment")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=ENV_PREFIX)
