import json
import tempfile
import os

import streamlit as st
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from st_files_connection import FilesConnection

import logging

logging.basicConfig(level=logging.INFO)

db_path = {
    "prod": "nekoconnect-database/nekoconnect_db.json",
    "dev": "nekoconnect-database/nekoconnect_db_dev.json"
}


class DB:
    def __init__(self, env):
        self.env = env
        self.conn = st.connection('gcs', type=FilesConnection)
        assert self.env in db_path, "Invalid environment"
        self.current_db_path = db_path[self.env]
        db_dict = self.conn.read(self.current_db_path, input_format="json", ttl=0)
        self.db = TinyDB(storage=MemoryStorage)
        self.db.storage.read = lambda: db_dict
        self.users_table = self.db.table('users')
        self.check_data_integrity()

    def check_data_integrity(self):
        users = self.users_table.all()
        for user in users:
            modified = False
            if 'credits' not in user:
                user['credits'] = 0
                modified = True
            if 'notes' not in user:
                user['notes'] = ""
                modified = True
            if modified:
                self.users_table.upsert(user, Query().phone_number == user['phone_number'])
                
        self.save()

    def table(self, table_name):
        return self.db.table(table_name)

    def save(self):
        # Convert the database to a JSON string
        db_json = json.dumps(self.db.storage.read())

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            # Write the JSON string to the temporary file
            temp_file.write(db_json)
            temp_file.flush()

            # Use the put method to upload the file
            self.conn._instance.put(temp_file.name, self.current_db_path)

        os.unlink(temp_file.name)

    def download_all_data(self):
        db_dict = self.conn.read(self.current_db_path, input_format="json", ttl=0)
        return db_dict