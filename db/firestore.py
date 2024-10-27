from google.cloud import firestore
from models.users import User
from typing import Dict, Any, List
from google.cloud.firestore import FieldFilter
import streamlit as st
from google.oauth2 import service_account

class FirestoreDB:
    def __init__(self, env):
        if env == 'dev':
            database_name = 'nekoconnect-dev-db'
        elif env == 'cloud' or env == 'prod':
            database_name = 'nekoconnect-db'
        config = dict(st.secrets['Firestore'])
        project_name = config['project_id']
        del config['project_id']
        credentials = service_account.Credentials.from_service_account_info(config)
        self.db = firestore.Client(credentials=credentials, database=database_name, project=project_name)


        self.users_collection = self.db.collection('users')
        self.machines_collection = self.db.collection('machines')
        self.records_collection = self.db.collection('records')

    def create_user(self, user: User):
        self.users_collection.document(user.phone_number).set(user.to_dict())

    def update_user(self, phone_number: str, updates: Dict[str, Any]):
        self.users_collection.document(phone_number).update(updates)

    def delete_user(self, phone_number: str):
        self.users_collection.document(phone_number).delete()

    def find_user(self, phone_number: str):
        doc = self.users_collection.document(phone_number).get()
        if doc.exists:
            return User(**doc.to_dict())
        return None

    def all_users(self):
        return [User(**doc.to_dict()) for doc in self.users_collection.stream()]

    # Machine operations
    def create_machine(self, machine_dict: Dict[str, Any]):
        self.machines_collection.document(machine_dict['id']).set(machine_dict)

    def get_all_machines(self) -> List[Dict[str, Any]]:
        return [doc.to_dict() for doc in self.machines_collection.stream()]

    def get_machine_by_id(self, machine_id: str) -> Dict[str, Any]:
        doc = self.machines_collection.document(machine_id).get()
        return doc.to_dict() if doc.exists else None

    def update_machine(self, machine_id: str, machine_dict: Dict[str, Any]):
        self.machines_collection.document(machine_id).set(machine_dict)

    def delete_machine(self, machine_id: str):
        self.machines_collection.document(machine_id).delete()

    # Record operations
    def create_record(self, record_dict: Dict[str, Any]):
        self.records_collection.document(record_dict['id']).set(record_dict)

    def get_all_records(self) -> List[Dict[str, Any]]:
        return [doc.to_dict() for doc in self.records_collection.stream()]

    def get_records_by_machine_id(self, machine_id: str) -> List[Dict[str, Any]]:
        query = self.records_collection.where(
            filter=FieldFilter('machine_id', '==', machine_id)
        )
        return [doc.to_dict() for doc in query.stream()]

    def save_record(self, record_dict: Dict[str, Any]):
        self.records_collection.document(record_dict['id']).set(record_dict)


