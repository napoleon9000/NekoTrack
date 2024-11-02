from db.toy_record_db import BlobDB
from db.firestore import FirestoreDB


class Manager:
    def __init__(self, env):
        self.blob_db = BlobDB(env)
        self.firestore_db = FirestoreDB(env)

    
