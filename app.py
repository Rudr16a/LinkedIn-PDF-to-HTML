from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
import os
import openai
from PyPDF2 import PdfReader
import json
from werkzeug.utils import secure_filename
import traceback
import logging

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'pdf_file' not in request.files:
            app.logger.error("No file part in the request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['pdf_file']
        api_key = request.form['api_key']
        
        app.logger.info(f"Received file: {file.filename}")
        app.logger.info(f"API Key received (first 5 chars): {api_key[:5]}...")
        
        if file.filename == '':
            app.logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            app.logger.info(f"File saved to {file_path}")
            
            try:
                # Process the PDF and generate HTML
                resume_html = process_pdf(file_path, api_key)
                
                # Save the HTML file
                html_filename = f"{os.path.splitext(filename)[0]}.html"
                html_path = os.path.join(app.config['GENERATED_FOLDER'], html_filename)
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(resume_html)
                
                app.logger.info(f"HTML file generated: {html_path}")
                
                # Clean up the uploaded PDF
                os.remove(file_path)
                app.logger.info(f"Removed uploaded PDF: {file_path}")
                
                return send_file(html_path, as_attachment=True)
            except Exception as e:
                app.logger.error(f"Error in processing PDF: {str(e)}")
                app.logger.error(traceback.format_exc())
                return jsonify({'error': str(e)}), 500
        
        app.logger.error("Invalid file type")
        return jsonify({'error': 'Invalid file type'}), 400
    
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'An unexpected error occurred'}), 500

def process_pdf(file_path, api_key):
    app.logger.info("Starting PDF processing")
    # Extract text from PDF
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    app.logger.info(f"Extracted {len(text)} characters from PDF")
    
    # Use OpenAI API to structure the resume data
    openai.api_key = api_key
    try:
        app.logger.info("Sending request to OpenAI API")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured resume information from text."},
                {"role": "user", "content": f"Extract structured resume information from the following text and return it as JSON. Include fields for name, email, phone, summary, experience (list of jobs with company, title, date, and description), education (list of schools with name, degree, date), and skills:\n\n{text}"}
            ]
        )
        
        resume_data = json.loads(response.choices[0].message.content)
        app.logger.info("Successfully received and parsed OpenAI API response")
    except Exception as e:
        app.logger.error(f"Error in OpenAI API call: {str(e)}")
        app.logger.error(traceback.format_exc())
        raise Exception(f"Error in OpenAI API call: {str(e)}")
    
    # Generate HTML from structured data
    html = generate_html_resume(resume_data)
    app.logger.info("Generated HTML resume")
    
    return html

# The generate_html_resume function remains the same

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)
    app.run(debug=True)