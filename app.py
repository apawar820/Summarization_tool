import pymongo
from pymongo import MongoClient
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

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://akhileshpawar820:<Akhi8011*>@summarizer.nqpip6t.mongodb.net/")
db = client["summarizer"]
collection = db["Project 0"]

# Configure the API key
genai.configure(api_key=os.getenv('GEN_AI_API_KEY') or "AIzaSyAlFMg7vWhcZLGqtYThySxY19r0hOnxLAw")

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

        # Insert data into MongoDB
        user_name = st.text_input("Enter Your Name")
        if user_name:
            data = {"user_name": user_name, "file_name": uploaded_file.name if uploaded_file else "Pasted Text",
                    "summary": summary}
            collection.insert_one(data)
            st.success("Summary data successfully saved to MongoDB.")
        else:
            st.warning("Please enter your name to save the summary data.")


if __name__ == "__main__":
    main()
