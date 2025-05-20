import logging

import ollama

from llm_processor.llm_client import LlmClient

logger = logging.getLogger(__name__)

class OllamaClient(LlmClient):
    """
    A client for interacting with an Ollama language model.

    This class allows initializing a connection to a specific Ollama model
    with a predefined system prompt. It provides a method to send user
    messages to the model and retrieve its responses.
    """

    def __init__(self, model_name: str, system_prompt: str, temperature: float = 1.0):
        """
        Initializes the OllamaClient.

        Args:
            model_name (str): The name of the Ollama model to use (e.g., "llama2").
            system_prompt (str): The system prompt to set the context for the model.

        Raises:
            ValueError: If model_name or system_prompt is empty.
        """
        if not model_name:
            raise ValueError("Model name cannot be empty.")
        if not system_prompt:
            raise ValueError("System prompt cannot be empty.")

        self.model_name = model_name
        self.system_prompt = system_prompt
        self.temperature = temperature
        try:
            self._client = ollama.Client()
            logger.info(f"Ollama client initialized for model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}", exc_info=True)
            # Depending on desired behavior, you might re-raise or handle this to allow offline use/testing
            raise ConnectionError(f"Could not connect to Ollama. Ensure Ollama is running. Details: {e}")


    def send_message(self, user_message: str) -> str:
        """
        Sends a message to the configured Ollama model and returns its response.

        Args:
            user_message (str): The message from the user to send to the model.

        Returns:
            str: The content of the model's response.

        Raises:
            ValueError: If user_message is empty.
            RuntimeError: If there's an error communicating with the Ollama API
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
            logger.info(f"Sending message to Ollama model {self.model_name}")
            response = self._client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": self.temperature
                }
            )

            if response and 'message' in response and 'content' in response['message']:
                model_response_content = response['message']['content']
                logger.info(f"Received response from Ollama model {self.model_name}: '{model_response_content[:100]}...'")
                return model_response_content
            else:
                logger.error(f"Unexpected response structure from Ollama: {response}")
                raise RuntimeError("Received an unexpected response structure from Ollama.")

        except ollama.ResponseError as e:
            logger.error(f"Ollama API ResponseError for model {self.model_name}: {e.status_code} - {e.error}", exc_info=True)
            raise RuntimeError(f"Ollama API error: {e.status_code} - {e.error}") from e
        except Exception as e:
            logger.error(f"An unexpected error occurred while communicating with Ollama model {self.model_name}: {e}", exc_info=True)
            raise RuntimeError(f"An unexpected error occurred: {e}") from e
