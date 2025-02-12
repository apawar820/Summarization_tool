import streamlit as st
import pymongo
import google.generativeai as genai
import os
from PyPDF2 import PdfReader
from langdetect import detect
from rake_nltk import Rake
import spacy
import pandas as pd
import re
from docx import Document
import uuid  # Import UUID module

# Initialize MongoDB client
def connect_to_mongodb():
    try:
        # Replace these values with your MongoDB Atlas connection details
        username = ""
        password = "*"
        cluster_name = ""
        database_name = ""

        # Construct the MongoDB URI
        uri = 
        # Attempt to connect to MongoDB
        client = pymongo.MongoClient(uri)
        db = client[database_name]
        return db
    except pymongo.errors.ConfigurationError as e:
        st.error("MongoDB Configuration Error: Please double-check your MongoDB Atlas connection settings.")
        st.stop()
    except pymongo.errors.ConnectionFailure as e:
        st.error("Failed to connect to MongoDB Atlas. Please ensure that your MongoDB cluster is accessible.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred while connecting to MongoDB Atlas: {str(e)}")
        st.stop()

# Connect to MongoDB
db = connect_to_mongodb()

# Check if GEN AI API Key is set
gen_ai_api_key = os.getenv('') or ""
if gen_ai_api_key == "YOUR_API_KEY_HERE":
    st.error("Please set your GEN AI API Key.")
    st.stop()

# Configure the API key
genai.configure(api_key=gen_ai_api_key)

# Initialize the Gemini Pro model
model = genai.GenerativeModel('gemini-pro')

# Load English language model for NER
nlp = spacy.load("en_core_web_sm")

# Function to generate a summary
def generate_summary(text):
    response = model.generate_content(text)
    return response.text

# Function to extract keywords
def extract_keywords(text):
    r = Rake()
    r.extract_keywords_from_text(text)
    phrases_with_scores = r.get_ranked_phrases_with_scores()
    keyword_freq = {}
    for score, phrase in phrases_with_scores:
        # Removing leading/trailing whitespaces and converting to lowercase for consistency
        clean_phrase = phrase.strip().lower()
        if clean_phrase not in keyword_freq:
            keyword_freq[clean_phrase] = 1
        else:
            keyword_freq[clean_phrase] += 1
    return keyword_freq

# Function to detect language
def detect_language(text):
    return detect(text)

# Function to perform named entity recognition (NER)
def ner(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))
    return entities

# Function to read text from PDF
def read_pdf(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    # Read each page of the PDF
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to read text from .doc and .docx files
def read_docx(uploaded_file):
    doc = Document(uploaded_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Function to extract URLs from text
def extract_urls(text):
    # Regular expression pattern for finding URLs
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    return urls

# Function to generate a unique ID based on user's name
def generate_unique_id(name):
    # Concatenate user's name with a unique UUID
    unique_id = f"{name}_{uuid.uuid4().hex}"
    return unique_id
# Function to read text from pasted text
def read_pasted_text(text):
    return text

# Streamlit App
def main():
    st.set_page_config(layout="wide")

    st.title("PDF, DOCUMENT, TEXT ANALYSIS & SUMMARY GENERATION ")

    # Requirements Sidebar
    st.sidebar.header("Requirements")
    uploaded_file = st.sidebar.file_uploader("Upload PDF, DOC, or TXT", type=["pdf", "doc", "docx", "txt"])
    pasted_text = st.sidebar.text_area("Paste Text")
    user_name = st.sidebar.text_input("Enter Your Name", "")

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension == "pdf":
            text = read_pdf(uploaded_file)
        elif file_extension == "doc" or file_extension == "docx":
            text = read_docx(uploaded_file)
        elif file_extension == "txt":
            text = uploaded_file.getvalue().decode("utf-8")
        else:
            st.error("Unsupported file format. Please upload a PDF, DOC, or TXT file.")
            return
    elif pasted_text != "":
        text = read_pasted_text(pasted_text)  # Read text from pasted text
        st.write("Pasted Text:")
        st.write(text)
    else:
        st.warning("Please upload a PDF, DOC, or TXT file or paste text.")
        return  # Exit early if neither file uploaded nor text pasted

    # Word Count
    col1, col2 = st.columns([1, 1])
    with col1:
        word_count = len(text.split())
        st.markdown(f"**Word Count:** {word_count}")
    with col2:
        language = detect_language(text)
        if language == "en":
            st.markdown("**Language:** English")
        else:
            st.markdown(f"**Language:** {language}")

    # Keyword Extraction
    keyword_freq = extract_keywords(text)
    df_keywords = pd.DataFrame({"Keyword": list(keyword_freq.keys()), "Frequency": list(keyword_freq.values())})
    st.markdown("**Keywords:**")
    st.write(df_keywords)

    # Named Entity Recognition (NER)
    entities = ner(text)
    df_entities = pd.DataFrame(entities, columns=["Entity", "Label"])
    st.markdown("**Named Entities:**")
    st.write(df_entities)

    # Extract URLs
    urls = extract_urls(text)
    if urls:
        df_urls = pd.DataFrame({"URLs": urls})
        st.markdown("**URLs:**")
        st.write(df_urls)
    else:
        st.markdown("**URLs:**")
        st.write("No URLs found in the text.")

    # Generate Summary
    if st.button("Summarize"):
        summary = generate_summary(text)
        st.markdown("**Summary:**")
        st.write(summary)

        # Word Count of Summary
        summary_word_count = len(summary.split())
        st.markdown(f"**Summary Word Count:** {summary_word_count}")

        # Generate Unique ID
        unique_id = generate_unique_id(user_name)

        # Determine file name for MongoDB insertion
        if uploaded_file is not None:
            file_name = uploaded_file.name
        else:
            file_name = "pasted_text"

        # Write to MongoDB
        try:
            collection = db["summaries"]
            data = {"unique_id": unique_id, "user_name": user_name, "file_name": file_name, "summary": summary, "summary_word_count": summary_word_count}
            collection.insert_one(data)
            st.success("Summary data written to MongoDB successfully!")
        except pymongo.errors.PyMongoError as e:
            st.error("Failed to write summary data to MongoDB.")
            st.error(str(e))

if __name__ == "__main__":
    main()
