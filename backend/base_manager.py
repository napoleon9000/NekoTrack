from db.toy_record_db import BlobDB
from db.firestore import FirestoreDB
from utils import get_image_by_path, get_image_by_path_no_cache

class Manager:
    def __init__(self, env):
        self.blob_db = BlobDB(env)
        self.firestore_db = FirestoreDB(env)

    def get_image_by_path(self, path, cache=True):
        if cache:
            return get_image_by_path(path, self.blob_db)
        else:
            return get_image_by_path_no_cache(path, self.blob_db)

    
