import logging

from openai import OpenAI

from llm_processor.llm_client import LlmClient

logger = logging.getLogger(__name__)

class OpenAiClient(LlmClient):
    """
    A client for interacting with an OpenAI or compatible language model API.

    This class allows initializing a connection to a specific model
    via a given base_url and using an api_key. It provides a method
    to send messages to the model and retrieve its responses.
    """

    def __init__(self, model_name: str, api_key: str, base_url: str, system_prompt: str | None = None, temperature: float = 1.0):
        """
        Initializes the OpenAiClient.

        Args:
            model_name (str): The name of the OpenAI model to use (e.g., "gpt-3.5-turbo").
            api_key (str): The API key for authentication.
            base_url (str): The base URL of the API.
            system_prompt (str, optional): The system prompt to set the context for the model.
            temperature (float): The sampling temperature to use.
        """
        if not model_name:
            raise ValueError("Model name cannot be empty.")
        if not api_key:
            raise ValueError("API key cannot be empty.")

        self.model_name = model_name
        self.system_prompt = system_prompt if system_prompt else "You are a helpful assistant."
        self.temperature = temperature

        try:
            self._client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            logger.info(f"OpenAI client initialized for model: {self.model_name} at URL: {base_url}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}", exc_info=True)
            raise ConnectionError(f"Could not initialize OpenAI client. Details: {e}")

    def send_message(self, user_message: str) -> str:
        """
        Sends a message to the configured OpenAI-compatible model and returns its response.

        Args:
            user_message (str): The message from the user to send to the model.

        Returns:
            str: The content of the model's response.

        Raises:
            ValueError: If user_message is empty.
            RuntimeError: If there's an error communicating with the API
                          or if the response format is unexpected.
        """
        if not user_message:
            logger.warning("Attempted to send an empty user message.")
            raise ValueError("User message cannot be empty.")

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]

        try:
            logger.info(f"Sending message to OpenAI model {self.model_name}")
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature
            )

            if response and response.choices and response.choices[0].message and response.choices[0].message.content:
                model_response_content = response.choices[0].message.content
                logger.info(f"Received response from OpenAI model {self.model_name}: '{model_response_content[:100]}...'")
                return model_response_content
            else:
                logger.error(f"Unexpected response structure from OpenAI: {response}")
                raise RuntimeError("Received an unexpected response structure from OpenAI.")

        except Exception as e: # Broad catch for API errors, can be refined
            logger.error(f"OpenAI API error for model {self.model_name}: {e}", exc_info=True)
            # Attempt to get more specific error details if available
            error_message = str(e)
            if hasattr(e, 'status_code'):
                error_message = f"Status Code {e.status_code}: {error_message}"
            raise RuntimeError(f"OpenAI API error: {error_message}") from e
