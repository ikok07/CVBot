from starlette import status
from starlette.requests import Request

from src.models.errors.api import APIError
from src.models.i18n.supported_languages import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, SupportedLanguage


async def locale_parser(request: Request) -> SupportedLanguage:
    language = request.headers.get("Accept-Language")
    try:
        if not language or SupportedLanguage(language) not in SUPPORTED_LANGUAGES:
            return DEFAULT_LANGUAGE

        return SupportedLanguage(language)
    except ValueError:
        raise APIError(status_code=status.HTTP_400_BAD_REQUEST, message=f"Invalid language: {language}. Supported languages: {','.join([lang.value for lang in SUPPORTED_LANGUAGES])}")
    except Exception as e:
        print(e)
        raise APIError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Something went wrong!")