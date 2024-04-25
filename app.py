import pymongo
import streamlit as st
import nltk
nltk.download('punkt')
nltk.download('stopwords')
import google.generativeai as genai
import os
from PyPDF2 import PdfReader
from langdetect import detect
from rake_nltk import Rake
import spacy
import pandas as pd
import re
from docx import Document
import time

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
def insert_data(file_name, file_size, time, date, words_summary):
    db = connect_to_mongodb()
    if db is not None:
        example_collection = db['example_collection']
        data = {
            "file_name": file_name,
            "file_size": file_size,
            "time": time,
            "date": date,
            "words_summary": words_summary
        }
        example_collection.insert_one(data)
        st.success("Data inserted successfully into MongoDB Atlas.")

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
        if uploaded_file is not None:
            current_time = time.strftime("%H:%M:%S")
            current_date = time.strftime("%Y-%m-%d")
            insert_data(uploaded_file.name, uploaded_file.size, current_time, current_date, summary_word_count)

if __name__ == "__main__":
    main()
