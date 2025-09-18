from enum import Enum


class SupportedLanguage(Enum):
    en = "en"
    bg = "bg"

SUPPORTED_LANGUAGES: list[SupportedLanguage] = [SupportedLanguage.en, SupportedLanguage.bg]
DEFAULT_LANGUAGE = SupportedLanguage.en