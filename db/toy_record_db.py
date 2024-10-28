import json
import tempfile
import os
import io

from PIL import Image

import streamlit as st
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from st_files_connection import FilesConnection

import logging

logging.basicConfig(level=logging.INFO)

db_path = {
    "prod": "nekoconnect-database/toy_record_db.json",
    "cloud": "nekoconnect-database/toy_record_db.json",
    "dev": "nekoconnect-database/toy_record_db_dev.json",
}


class BlobDB:
    def __init__(self, env):
        self.env = env
        self.bucket = "nekoconnect-database"
        self.conn = st.connection('gcs', type=FilesConnection)
        assert self.env in db_path, "Invalid environment"
        self.current_db_path = db_path[self.env]
        db_dict = self.conn.read(self.current_db_path, input_format="json", ttl=0)
        self.db = TinyDB(storage=MemoryStorage)
        self.db.storage.read = lambda: db_dict
        self.users_table = self.db.table('users')

    def table(self, table_name):
        return self.db.table(table_name)

    def delete_file(self, path):
        full_path = f"{self.bucket}/{path}"
        self.conn._instance.delete(full_path)

    def save(self):
        # Convert the current database to a JSON string
        db_json = json.dumps(self.db.storage.read())

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            # Write the JSON string to the temporary file
            temp_file.write(db_json)
            temp_file.flush()

            # Use the put method to upload the file
            self.conn._instance.put(temp_file.name, self.current_db_path)

        try:
            # Use the put method to upload the file
            self.conn._instance.put(temp_file.name, self.current_db_path)
        except Exception as e:
            logging.error(f"Error saving database: {e}")
        finally:
            # Clean up the temporary file
            os.unlink(temp_file.name)
            
    def download_all_data(self):
        db_dict = self.conn.read(self.current_db_path, input_format="json", ttl=0)
        return db_dict

    def download_file(self, path):
        full_path = f"{self.bucket}/{path}"
        with self.conn._instance.open(full_path, 'rb') as f:
            content = f.read()
            return content

    def upload_file(self, file: io.BytesIO, path: str, compress: bool = False):
        full_path = f"{self.bucket}/{path}"

        if compress:
            # downsample the image to width 512 and rotate to portrait
            image = Image.open(file)
            if image.width > image.height:
                image = image.rotate(-90, expand=True)
                image = image.resize((512, int(image.height * 512 / image.width)))
            else:
                image = image.resize((512, int(image.height * 512 / image.width)))
            file = io.BytesIO()
            image.save(file, format="JPEG")
            file.seek(0)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as temp_file:
            if isinstance(file, io.BytesIO):
                # Seek to the beginning of the file
                file.seek(0)
                # Write the content of the BytesIO object to the temp file
                temp_file.write(file.read())
            elif isinstance(file, str):
                # If it's a file path, read the file and write to temp file
                with open(file, 'rb') as f:
                    temp_file.write(f.read())
            else:
                raise ValueError("File must be either a BytesIO object or a file path string")
            
            # Ensure all data is written to disk
            temp_file.flush()
            os.fsync(temp_file.fileno())

        try:
            # Use put method to upload the temporary file
            logging.info(f"Uploading file to {path}")
            logging.info(f"File: {temp_file.name}")
            self.conn._instance.put(temp_file.name, full_path)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file.name)