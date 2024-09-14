

# LinkedIn PDF to HTML Resume Converter

This web application converts LinkedIn PDF resumes to HTML format using OpenAI's GPT-3.5 model.

## Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd <repository-name>
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open a web browser and go to `http://localhost:5000` to use the application.

## Usage

1. Upload your LinkedIn PDF resume.
2. Enter your OpenAI API key.
3. Click "Generate HTML Resume".
4. Wait for the process to complete, and the HTML resume will be downloaded automatically.

## Deployment

To deploy this application, you can use platforms like Heroku or PythonAnywhere. Make sure to set up environment variables for sensitive information like API keys.

## Note

This application requires an OpenAI API key to function. Make sure you have a valid API key before using the application.
