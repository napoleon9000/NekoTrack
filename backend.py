from tinydb import TinyDB, Query
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import uuid
from typing import List
from db import DB
import json



@dataclass
class Redemption:
    item: str
    date: str
    credits: int


@dataclass
class User:
    uuid: str
    phone_number: str
    registration_date: str
    credits: int = 0
    name: str = ""
    notes: str = ""
    redemption_history: List[Redemption] = None
    
    def __post_init__(self):
        if self.redemption_history is None:
            self.redemption_history = []

class Manager:
    def __init__(self, env):
        self.db = DB(env)
        self.users_table = self.db.table('users')


    # Create a new user
    def create_user(self, phone_number, name=None, credits=0, notes=""):
        registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_uuid = str(uuid.uuid4())
        user = User(user_uuid, phone_number, registration_date, name=name, credits=credits, notes=notes)
        self.users_table.upsert(user.__dict__, Query().phone_number == phone_number)
        self.db.save()

    # Edit user information
    def edit_user(self, phone_number, name=None, credits=None, notes=None):
        UserQuery = Query()
        updates = {}
        if name:
            updates['name'] = name
        if credits is not None:
            updates['credits'] = credits
        if notes:
            updates['notes'] = notes
        self.users_table.update(updates, UserQuery.phone_number == phone_number)
        self.db.save()
    # Delete a user
    def delete_user(self, phone_number):
        UserQuery = Query()
        self.users_table.remove(UserQuery.phone_number == phone_number)
        self.db.save()

    # Find a user
    def find_user(self, phone_number):
        UserQuery = Query()
        return self.users_table.search(UserQuery.phone_number == phone_number)

    # all users to pandas dataframe
    def all_users_to_df(self):
        return pd.DataFrame(self.users_table.all())

    # display user info on home page
    def display_user_info(self):
        display_keys = ['phone_number', 'name', 'credits', 'registration_date']
        all_users = self.all_users_to_df()
        if all_users.empty:
            return None
        return all_users[display_keys]

    # record redemption
    def record_redemption(self, phone_number, item, credits):
        user_data = self.find_user(phone_number)
        if user_data:
            UserQuery = Query()
            user = user_data[0]
            current_history = user['redemption_history']
            current_credits = user['credits']
            current_history.append({"item": item, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "credits": credits})
            new_credits = current_credits - credits
            if new_credits < 0:
                raise ValueError("Not enough credits!")

            updates = {'redemption_history': current_history, 'credits': new_credits}
            self.users_table.update(updates, UserQuery.phone_number == phone_number)
            self.db.save()

    # download all data in json format
    def download_all_data(self):
        # Convert the entire database to JSON format
        all_data = self.db.download_all_data()
        return json.dumps(all_data, indent=2)
