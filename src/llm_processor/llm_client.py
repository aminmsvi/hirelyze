from abc import ABC, abstractmethod


class LlmClient(ABC):
    """
    Abstract base class for LLM clients.
    """

    @abstractmethod
    def send_message(self, message: str) -> str:
        pass
