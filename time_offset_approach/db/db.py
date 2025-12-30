from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"

client = MongoClient(MONGO_URI)

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

