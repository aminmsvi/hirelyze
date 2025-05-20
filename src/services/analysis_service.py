import logging

from llm_processor.llm_client import LlmClient
from prompt_loader import load_prompt

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Handles the AI analysis of resume text against a job description.
    """

    def __init__(self, llm_client: LlmClient):
        """
        Initializes the AnalysisService.

        Args:
            llm_client (LlmClient): The LLM client to use.
        """
        self._llm_client = llm_client

    def analyze_resume(self, job_description: str, resume_text: str) -> tuple[str | None, str | None]:
        """
        Performs AI analysis using the configured LLM client.

        Args:
            job_description (str): The job description text.
            resume_text (str): The extracted text from the candidate's resume.

        Returns:
            tuple[str | None, str | None]: A tuple containing (ai_response, error_message).
                                           ai_response is None if an error occurred.
                                           error_message is None if successful.
        """
        if not job_description:
            logger.warning("Job description is empty. Cannot perform analysis.")
            return None, "Job description cannot be empty."
        if not resume_text:
            logger.warning("Resume text is empty. Cannot perform analysis.")
            return None, "Resume text cannot be empty."

        try:
            candidate_analysis_prompt = load_prompt("talent_aquisition_assistant_user_prompt") \
                .replace("{{ job_description }}", job_description) \
                .replace("{{ candidate_resume }}", resume_text)

            ai_response = self._llm_client.send_message(candidate_analysis_prompt)
            logger.info("Successfully received AI analysis from LLM client.")
            return ai_response, None

        except ConnectionError as ce:
            logger.error(f"LLM client connection error during analysis: {ce}", exc_info=True)
            return None, f"Could not connect to AI service: {ce}"
        except ValueError as ve: # From LLMClient (e.g., empty prompt, though unlikely here)
            logger.error(f"Input error for LLM client: {ve}", exc_info=True)
            return None, f"AI input error: {ve}"
        except RuntimeError as rte: # From LLMClient (API errors, unexpected responses)
            logger.error(f"LLM client runtime error during analysis: {rte}", exc_info=True)
            return None, f"AI communication error: {rte}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during AI analysis: {e}", exc_info=True)
            return None, f"Unexpected AI analysis error: {e}"
