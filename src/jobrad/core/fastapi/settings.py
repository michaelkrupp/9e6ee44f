from typing import Final

from ...infrastructure.logging import SettingsMixin as LoggingSettingsMixin
from ...infrastructure.settings import Settings as SettingsBase


class Settings(SettingsBase, LoggingSettingsMixin):
    pass


settings: Final[Settings] = Settings()
