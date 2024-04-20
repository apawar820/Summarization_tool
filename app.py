# Import NLTK and download necessary resources
import nltk
nltk.download('punkt')
nltk.download('stopwords')

# Continue with the rest of your imports
import streamlit as st
import google.generativeai as genai
import os
from PyPDF2 import PdfReader
from langdetect import detect
from rake_nltk import Rake
import spacy
import pandas as pd
import re
from docx import Document

# Configure the API key
genai.configure(api_key=os.getenv('GEN_AI_API_KEY') or "AIzaSyAlFMg7vWhcZLGqtYThySxY19r0hOnxLAw")

# Initialize the Gemini Pro model
model = genai.GenerativeModel('gemini-pro')

# Load English language model for NER
nlp = spacy.load("en_core_web_sm")

# Function to generate a summary
def generate_summary(text):
    try:
        response = model.generate_content(text)
        if response.safety_ratings:
            st.error("The response was blocked or contained invalid content. Please try again with different input.")
            return None
        elif response.parts:
            return response.text
        else:
            st.error("No text found in the response. Please try again.")
            return None
    except Exception as e:
        st.error("An error occurred during summary generation. Please try again.")
        st.error(str(e))  # Display the specific error message
        return None

# Function to extract keywords
def extract_keywords_with_frequency(text):
    r = Rake()
    r.extract_keywords_from_text(text)
    keyword_scores = r.get_word_degrees()  # Get keyword scores (frequencies)
    return keyword_scores

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
    
# Streamlit App
def main():
    st.set_page_config(layout="wide")

    st.title("PDF, DOCUMENT, TEXT ANALYSIS & SUMMARY GENERATION ")

    # Requirements Sidebar
    st.sidebar.header("Requirements")
    uploaded_file = st.sidebar.file_uploader("Upload PDF, DOC, or TXT", type=["pdf", "doc", "docx", "txt"])
    pasted_text = st.sidebar.text_area("Paste Text")

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
        text = pasted_text
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
    keyword_scores = extract_keywords_with_frequency(text)
    df_keywords = pd.DataFrame({"Keyword": keyword_scores.keys(), "Frequency": keyword_scores.values()})
    df_keywords = df_keywords.sort_values(by="Frequency", ascending=False)
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
        if summary is not None:
            st.markdown("**Summary:**")
            st.write(summary)

            # Word Count of Summary
            summary_word_count = len(summary.split())
            st.markdown(f"**Summary Word Count:** {summary_word_count}")

if __name__ == "__main__":
    main()
