import pymongo
import os
client = pymongo.MongoClient(os.environ["MONGODB_URI"])
db = client['SeriesDB']
notes_collection = db["notes"]
repeat_notes_collection = db["repeat_notes"]

def insert_document(collection, data):
    return collection.insert_one(data).inserted_id

def find_document(collection, elements, multiple=False):
    if multiple:
        results = collection.find(elements)
        return [r for r in results]
    else:
        return collection.find_one(elements)

def update_document(collection, query_elements, new_values):
    collection.update_one(query_elements, {'$set': new_values})

def delete_document(collection, query):
    collection.delete_one(query)