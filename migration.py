from google.cloud import firestore
import json


destination_env = 'prod'
local_user_file = 'data/nekoconnect_db.json'
local_record_file = 'data/toy_record_db.json'
remove_previous = True

if destination_env == 'prod' or destination_env == '':
    firestore_db = firestore.Client.from_service_account_json('.streamlit/firestore_key.json', database=f'nekoconnect-db')
else:   
    firestore_db = firestore.Client.from_service_account_json('.streamlit/firestore_key.json', database=f'nekoconnect-{destination_env}-db')


def delete_collection(collection_name, batch_size=500):
    # if the collection doesn't exist, don't delete it
    if not firestore_db.collection(collection_name).get():
        return

    collection_ref = firestore_db.collection(collection_name)
    docs = collection_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        return delete_collection(collection_ref, batch_size)


# migrate users
local_file = local_user_file

# load local file
with open(local_file, 'r') as f:
    data = json.load(f)

# clear firestore users collection
if remove_previous:
    delete_collection('users')

# iterate through data and upload to firestore, use phone number as id
for id, user in data['users'].items():
    firestore_id = user['phone_number']
    doc_ref = firestore_db.collection('users').document(firestore_id)
    user['tokens'] = 0
    doc_ref.set(user)
    print(f'uploaded {firestore_id}')

# migrate toy records
local_file = local_record_file

# load local file
with open(local_file, 'r') as f:
    data = json.load(f)

machine_data = data['machines']
record_data = data['records']

# clear firestore machines collection
if remove_previous:
    delete_collection('machines')

# iterate through data and upload to firestore, use id as id
for id, record in machine_data.items():
    if 'doc_id' in record:
        del record['doc_id']
    machine_id = record['id']
    doc_ref = firestore_db.collection('machines').document(machine_id)
    doc_ref.set(record)
    print(f'uploaded {machine_id}')

# clear firestore records collection
if remove_previous:
    delete_collection('records')

for id, record in record_data.items():
    record_id = f'{record["date"]}#{record["machine_id"]}'
    doc_ref = firestore_db.collection('records').document(record_id)
    doc_ref.set(record)
    print(f'uploaded {record_id}')