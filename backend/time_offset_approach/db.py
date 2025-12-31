
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://echoid_user:echoid_user1202@echoid-cluster.pqcxbji.mongodb.net/?appName=echoid-cluster"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.audio_matcher

songs_col = db.songs
fingerprints_col = db.fingerprints


#to check the collection!

# for doc in fingerprints_col.find({'song_id': 'Uchhal Matt'}).limit(15):
#     print(doc)

# for doc in songs_col.find():
#     print(doc)


# count = songs_col.count_documents({})


# print(count)

if __name__ == "__main__": 
    print(songs_col.count_documents({}))
    print(fingerprints_col.count_documents({}))

    songs_col.insert_one({"test": "hello"})


