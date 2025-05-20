import logging

import streamlit as st

from config import settings
from llm_processor.open_ai_client import OpenAiClient
from prompt_loader import load_prompt
from services.analysis_service import AnalysisService
from services.pdf_service import PdfService

logger = logging.getLogger(__name__)

file_handler = PdfService()
analysis_service = AnalysisService(
    llm_client=OpenAiClient(
        model_name=settings.LLM_MODEL,
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        system_prompt=load_prompt("talent_aquisition_assistant_system_prompt"),
        temperature=0.1
    )
)

def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = None
    if 'ai_response' not in st.session_state:
        st.session_state.ai_response = None
    if 'processing_error' not in st.session_state:
        st.session_state.processing_error = None
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = None

def display_ui_elements():
    """Sets up and displays the main UI elements."""
    st.title("Resume Analyzer")
    st.write("Drag and drop your PDF file below or click to browse.")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_uploader")

    st.subheader("Job Description")
    job_description = st.text_area("Paste the job description here:", height=200, key="job_desc_input")

    analyze_button_pressed = st.button("Analyze with AI ✨", key="analyze_button")

    return uploaded_file, job_description, analyze_button_pressed

def handle_file_upload(uploaded_file):
    """Handles the PDF file upload using FileHandlerService."""
    if uploaded_file and (st.session_state.uploaded_file_name != uploaded_file.name or not st.session_state.extracted_text):
        st.session_state.extracted_text = None
        st.session_state.ai_response = None # Clear previous AI response on new file
        st.session_state.processing_error = None
        st.session_state.uploaded_file_name = uploaded_file.name

        logger.info(f"Processing uploaded file: {uploaded_file.name}")
        with st.spinner(f"Extracting text from '{uploaded_file.name}'..."):
            try:
                extracted_text, error_message = file_handler.handle_uploaded_file(
                    uploaded_file.getbuffer(),
                    uploaded_file.name
                )
                if error_message:
                    st.error(f"Error processing PDF: {error_message}")
                    st.session_state.processing_error = error_message
                else:
                    st.write(f"Successfully extracted text from '{uploaded_file.name}'.")
                    st.session_state.extracted_text = extracted_text
                    logger.info(f"Successfully extracted text from {uploaded_file.name}.") # Text not displayed to user log
            except Exception as e: # Catch errors from service instantiation if raised there
                logger.error(f"Failed to initialize or use FileHandlerService: {e}", exc_info=True)
                st.error(f"File processing system error: {e}")
                st.session_state.processing_error = f"File system error: {e}"
    elif not uploaded_file and st.session_state.uploaded_file_name:
        # File was removed by the user
        logger.info(f"File '{st.session_state.uploaded_file_name}' was removed by the user.")
        st.session_state.extracted_text = None
        st.session_state.ai_response = None
        st.session_state.processing_error = None
        st.session_state.uploaded_file_name = None

def perform_ai_analysis(job_description, analyze_button_pressed):
    """Performs AI analysis if conditions are met."""
    if analyze_button_pressed and st.session_state.extracted_text and job_description:
        st.session_state.ai_response = None # Clear previous response
        st.session_state.processing_error = None # Clear previous errors

        logger.info("Analyze button pressed. Starting AI analysis.")
        with st.spinner(f"Analyzing with {settings.LLM_MODEL}... This may take a moment."):
            try:
                ai_response, error_message = analysis_service.analyze_resume(
                    job_description,
                    st.session_state.extracted_text
                )
                if error_message:
                    st.error(f"AI Analysis Error: {error_message}")
                    st.session_state.processing_error = error_message
                else:
                    st.session_state.ai_response = ai_response
                    logger.info("Successfully received and stored AI analysis response.")
            except Exception as e: # Catch errors from service instantiation if raised there
                logger.error(f"Failed to initialize or use AnalysisService: {e}", exc_info=True)
                st.error(f"AI system error: {e}")
                st.session_state.processing_error = f"AI system error: {e}"

    elif analyze_button_pressed and not st.session_state.extracted_text:
        st.warning("Please upload and process a resume PDF before analyzing.")
        logger.warning("Analyze button pressed but no extracted text available.")
    elif analyze_button_pressed and not job_description:
        st.warning("Please provide a job description before analyzing.")
        logger.warning("Analyze button pressed but no job description provided.")

def display_results():
    """Displays AI analysis results or processing errors."""
    if st.session_state.ai_response:
        st.write("---")
        st.subheader("AI Analysis Result:")
        st.markdown(st.session_state.ai_response)
        logger.info("Displayed AI analysis result.")
    elif st.session_state.processing_error and not st.session_state.ai_response:
        # Only show this if there isn't already an AI response displayed (e.g. PDF error)
        st.warning(f"Could not complete the process due to: {st.session_state.processing_error}")
        logger.info(f"Displayed processing error: {st.session_state.processing_error}")

def main():
    """Main function to run the Streamlit application."""
    initialize_session_state()
    uploaded_file, job_description, analyze_button_pressed = display_ui_elements()

    handle_file_upload(uploaded_file)
    perform_ai_analysis(job_description, analyze_button_pressed)
    display_results()

if __name__ == "__main__":
    main()
