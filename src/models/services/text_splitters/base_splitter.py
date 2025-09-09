from abc import ABC, abstractmethod
from typing import Coroutine, Any

from langchain_core.documents import Document


class BaseSplitter(ABC):

    @abstractmethod
    async def split(self, file_content: bytes) -> tuple[list[Document], str]:
        """

        :param file_content: Buffer of the file that needs to be split in chunks
        :return: 1. The generated chunks 2. A markdown version of the text
        """
        pass