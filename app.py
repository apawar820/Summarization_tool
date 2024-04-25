import streamlit as st
import pymongo

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
    if db is not None:  # Compare with None directly
        example_collection = db['example_collection']
        example_collection.insert_one(data)
        st.success("Data inserted successfully into MongoDB Atlas.")

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
    if db is not None:  # Compare with None directly
        example_collection = db['example_collection']
        data = example_collection.find()
        for item in data:
            st.write(item)

if __name__ == "__main__":
    main()
