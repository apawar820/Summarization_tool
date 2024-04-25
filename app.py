import streamlit as st
import pymongo

# Connect to MongoDB Atlas
def connect_to_mongodb():
    # Replace these values with your MongoDB Atlas connection string
    username = "akhileshpawar820"
    password = "Akhi8011*"
    cluster_name = "Cluster"
    database_name = "summary"

    try:
        client = pymongo.MongoClient(f"mongodb+srv://akhileshpawar820:<Akhi8011*>@cluster.2neubhc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster")
        db = client[database_name]
        return db
    except Exception as e:
        st.error(f"Error connecting to MongoDB Atlas: {e}")

# Function to insert data into MongoDB
def insert_data(data):
    db = connect_to_mongodb()
    if db:
        example_collection = db['example_collection']
        example_collection.insert_one(data)
        st.success("Data inserted successfully into MongoDB Atlas.")
    else:
        st.error("Failed to connect to MongoDB Atlas. Please check your connection settings.")

# Main function to run the Streamlit app
def main():
    # Title of the web app
    st.title("MongoDB Atlas Streamlit Web App")

    # Input form to add data
    st.header("Add Data to MongoDB Atlas")
    name = st.text_input("Enter Name")
    age = st.number_input("Enter Age")
    email = st.text_input("Enter Email")

    # Button to submit data
    if st.button("Submit"):
        data = {"name": name, "age": age, "email": email}
        insert_data(data)

    # Display data from MongoDB
    st.header("Data from MongoDB Atlas")
    db = connect_to_mongodb()
    if db:
        example_collection = db['example_collection']
        data = example_collection.find()
        for item in data:
            st.write(item)
    else:
        st.error("Failed to connect to MongoDB Atlas. Please check your connection settings.")

if __name__ == "__main__":
    main()
