import streamlit as st
import pymongo

# Connect to MongoDB Atlas
def connect_to_mongodb():
    # Replace these values with your MongoDB Atlas connection string
    username = "akhileshpawar820"
    password = "Akhi8011"
    cluster_name = "Cluster"
    database_name = "Cluster"

    try:
        client = pymongo.MongoClient(f"mongodb+srv://akhileshpawar820:<Akhi8011*>@cluster.2neubhc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster")
        db = client[database_name]
        return db
    except Exception as e:
        st.error(f"Error connecting to MongoDB Atlas: {e}")

# Main function to run the Streamlit app
def main():
    # Title of the web app
    st.title("MongoDB Atlas Streamlit Web App")

    # Connect to MongoDB Atlas
    db = connect_to_mongodb()

    # Display data from MongoDB
    if db:
        # Example: Display a collection named 'example_collection'
        example_collection = db['example_collection']
        st.write("Data from MongoDB Atlas:")
        data = example_collection.find()
        for item in data:
            st.write(item)
    else:
        st.error("Failed to connect to MongoDB Atlas. Please check your connection settings.")

if __name__ == "__main__":
    main()
