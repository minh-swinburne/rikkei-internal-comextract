from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, page_text: str) -> list[dict]:
        """Extracts structured company info from a page of text."""
        raise NotImplementedError
