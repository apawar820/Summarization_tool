import streamlit as st
import os
import pymongo
from PyPDF2 import PdfReader
from docx import Document
from langdetect import detect
from rake_nltk import Rake
import spacy
import pandas as pd
import re

# Connect to MongoDB Atlas
def connect_to_mongodb():
    try:
        # Replace these values with your MongoDB Atlas connection string
        username = "akhileshpawar820"
        password = "Akhi8011*"
        cluster_name = "cluster"
        database_name = "cluster"

        client = pymongo.MongoClient(f"mongodb+srv://akhileshpawar820:Akhi8011*@cluster.1dwu2os.mongodb.net/?retryWrites=true&w=majority&appName=cluster")
        db = client[database_name]
        return db
    except pymongo.errors.OperationFailure as e:
        st.error("Failed to connect to MongoDB Atlas. Please check your connection settings.")
        st.stop()

# Function to insert data into MongoDB
def insert_data(data):
    db = connect_to_mongodb()
    if db is not None:
        example_collection = db['example_collection']
        example_collection.insert_one(data)
        st.success("Data inserted successfully into MongoDB Atlas.")

# Initialize Streamlit app
def main():
    st.title("PDF, DOCUMENT, TEXT ANALYSIS & SUMMARY GENERATION ")

    # Requirements Sidebar
    st.sidebar.header("Requirements")
    name = st.sidebar.text_input("Enter Your Name")
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
    word_count = len(text.split())
    st.markdown(f"**Word Count:** {word_count}")

    # Language Detection
    language = detect(text)
    if language == "en":
        st.markdown("**Language:** English")
    else:
        st.markdown(f"**Language:** {language}")

    # Keyword Extraction
    r = Rake()
    r.extract_keywords_from_text(text)
    keywords = r.get_ranked_phrases()
    st.markdown("**Keywords:**")
    st.write(keywords)

    # Named Entity Recognition (NER)
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    st.markdown("**Named Entities:**")
    st.write(entities)

    # Generate Summary
    if st.button("Summarize"):
        summary = generate_summary(text)
        st.markdown("**Summary:**")
        st.write(summary)

        # Insert analysis data into MongoDB
        insert_data({
            "name": name,
            "file_name": uploaded_file.name if uploaded_file else "Pasted Text",
            "file_type": file_extension if uploaded_file else "Pasted Text",
            "word_count": word_count,
            "summary": summary
        })

# Function to generate a summary
def generate_summary(text):
    # Dummy summary generation for demonstration purposes
    return "This is a summary of the input text."

# Function to read text from PDF
def read_pdf(uploaded_file):
    with open(uploaded_file.name, "rb") as f:
        pdf_reader = PdfReader(f)
        text = ""
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

if __name__ == "__main__":
    main()
