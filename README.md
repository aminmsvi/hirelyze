# Resume Analyzer

This project is a Streamlit web application that analyzes resumes against job descriptions using a Large Language Model (LLM).

## Features

- [x] Analyze a PDF resume based on job description and provide a detailed analysis.
- [ ] Perform analysis based on the candidate's linkedin profile if available.
- [ ] Analyze candidate's github profile if available.

## Setup

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd resume-analyzer
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies:**
    The `Makefile` provides a convenient way to install dependencies.

    ```bash
    make deps-dev
    ```

4. **Set up Environment Variables:**
    Create a `.env` file in the root of the project. This file is used to configure the LLM model.
    Example `.env` content:

    ```env
    LLM_MODEL="gemma3:12b" # Or any other Ollama model you have running
    ```

    Refer to `config.py` for how `LLM_MODEL` is used. The default is "gemma3:12b". Ensure you have Ollama installed and the specified model pulled (e.g., `ollama pull gemma3:12b`).

## Running the Application

Once the setup is complete, you can run the Streamlit application using the `Makefile`:

```bash
make run
```

This will typically start the application on `http://localhost:8501`.

## Usage

1. Open the application in your web browser.
2. Upload a resume in PDF format.
3. Paste the job description into the text area.
4. Click the "Analyze with AI ✨" button.
5. The analysis results will be displayed on the page.

## Development

### Linting and Formatting

This project uses Ruff for linting and Black (via Ruff) for formatting, along with isort for import sorting.

* **Check for linting issues and formatting:**

    ```bash
    make lint
    ```

* **Fix linting issues and format code:**

    ```bash
    make format
    ```
