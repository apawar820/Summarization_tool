import streamlit as st
import pymongo

# Connect to MongoDB Atlas
def connect_to_mongodb():
    # Replace these values with your MongoDB Atlas connection string
    username = "your_username"
    password = "your_password"
    cluster_name = "your_cluster_name"
    database_name = "your_database_name"

    try:
        client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@{cluster_name}.mongodb.net/{database_name}?retryWrites=true&w=majority")
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
