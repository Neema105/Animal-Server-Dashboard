from pymongo import MongoClient
from bson.objectid import ObjectId

class AnimalShelter(object):
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self, username, password):
        USER = 'aacuser'
        PASS = 'SNHU1234'
        HOST = 'localhost'
        PORT = 27017
        DB = 'aac'
        COL = 'animals'
        
        self.client = MongoClient(f"mongodb://{USER}:{PASS}@{HOST}:{PORT}")
        self.database = self.client[DB]
        self.collection = self.database[COL]

# create
    def create(self, data):
        if data is not None:
            try:
                self.collection.insert_one(data)
                return True
            except Exception as e:
                print(f"Create Error: {e}")
                return False
        else:
            raise Exception("Nothing to save, the data parameter is empty.")

# read
    def read(self, query):
        if query is not None:
            try:
                result = list(self.collection.find(query))
                return result
            except Exception as e:
                print(f"Read Error: {e}")
                return []
        else:
            return []

#update
    def update(self, query, new_values):

        if query is None or new_values is None:
            return 0

        try:
            update_data = {"$set": new_values}
            result = self.collection.update_many(query, update_data)
            return result.modified_count
        except Exception as e:
            print(f"Update Error: {e}")
            return 0

#delete
    def delete(self, query):
    
        if query is None:
            return 0

        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            print(f"Delete Error: {e}")
            return 0
