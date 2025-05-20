import logging
import os
import tempfile

import fitz

logger = logging.getLogger(__name__)

TEMP_PDF_DIR_NAME = "temp_pdf_uploads"

class PdfService:
    """
    Handles PDF file uploads, temporary storage, text extraction, and cleanup.
    """

    def __init__(self, temp_dir_name: str = TEMP_PDF_DIR_NAME):
        self.temp_base_dir = temp_dir_name
        self._ensure_temp_dir_exists()

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extracts text content from a PDF file.

        Args:
            pdf_path: The path to the PDF file.

        Returns:
            The text content of the PDF as a string, or an error message.
        """
        try:
            document = fitz.open(pdf_path)
            text = ""
            for page_num in range(len(document)):
                page = document.load_page(page_num)
                text += page.get_text()
            logger.info(f"Successfully extracted text from {pdf_path}")
            return text
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}", exc_info=True)
            return f"Error processing PDF: {e}"

    def _ensure_temp_dir_exists(self):
        """Ensures the temporary directory for uploads exists."""
        if not os.path.exists(self.temp_base_dir):
            try:
                os.makedirs(self.temp_base_dir)
                logger.info(f"Created temporary directory: {self.temp_base_dir}")
            except OSError as e:
                logger.error(f"Failed to create temporary directory {self.temp_base_dir}: {e}")
                # This error should be propagated or handled to inform the user
                raise

    def handle_uploaded_file(self, uploaded_file_content: bytes, original_file_name: str) -> tuple[str | None, str | None]:
        """
        Saves the uploaded file temporarily and extracts text.

        Args:
            uploaded_file_content (bytes): The content of the uploaded file.
            original_file_name (str): The original name of the uploaded file.

        Returns:
            tuple[str | None, str | None]: A tuple containing (extracted_text, error_message).
                                           extracted_text is None if an error occurred.
                                           error_message is None if successful.
        """
        temp_file_path = None
        try:
            # Create temp dir if it was removed (e.g. by cleanup)
            self._ensure_temp_dir_exists()

            with tempfile.NamedTemporaryFile(dir=self.temp_base_dir, suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(uploaded_file_content)
                temp_file_path = tmp_file.name
            logger.info(f"Uploaded file '{original_file_name}' saved temporarily to '{temp_file_path}'")

            extracted_text = self._extract_text_from_pdf(temp_file_path)

            if extracted_text.startswith("Error processing PDF:"):
                logger.warning(f"Failed to extract text from {original_file_name}: {extracted_text}")
                return None, extracted_text
            else:
                logger.info(f"Successfully extracted text from {original_file_name}.")
                return extracted_text, None

        except Exception as e:
            logger.error(f"An error occurred during file processing or text extraction for {original_file_name}: {e}", exc_info=True)
            return None, f"File processing error: {e}"
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                self.cleanup_temp_file(temp_file_path)

    def cleanup_temp_file(self, file_path: str):
        """Removes a specific temporary file."""
        try:
            os.remove(file_path)
            logger.info(f"Successfully removed temporary file: {file_path}")
        except OSError as e:
            logger.error(f"Failed to remove temporary file {file_path}: {e}")

    def cleanup_temp_directory(self):
        """Removes the temporary directory if it's empty."""
        if os.path.exists(self.temp_base_dir) and not os.listdir(self.temp_base_dir):
            try:
                os.rmdir(self.temp_base_dir)
                logger.info(f"Successfully removed empty temporary directory: {self.temp_base_dir}")
            except OSError as e:
                logger.warning(f"Could not remove temporary directory {self.temp_base_dir}: {e}")
