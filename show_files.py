from pymongo import MongoClient
from pprint import pprint

def display_audio_files():
    # Connect to MongoDB
    client = MongoClient('localhost', 27017)

    # Select the database
    db = client['audiodb']

    # Select the collection
    collection = db['audiofiles']

    # Fetch all documents
    documents = collection.find()

    # Print each document in a nice, readable format
    for document in documents:
        pprint(document)

# Call the function
display_audio_files()
