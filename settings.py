
import logging
import os
from pymongo import MongoClient
import pytz
from utils import read_json
ENVIRONMENT = os.environ['ENVIRONMENT']

logging.info(f"Environment : {ENVIRONMENT}")

if ENVIRONMENT == "dev":
    logging.info(f"Loading .env file")

    from dotenv import load_dotenv

    load_dotenv()

MONGO_CONNECTION = os.environ['MONGO_CONNECTION']
CONTACTACTS_DB = os.environ['CONTACTACTS_DB']
CONTACTS_COLLECTION = os.environ['CONTACTS_COLLECTION']
LINKS_COLLECTION = os.environ['LINKS_COLLECTION']
INDUSTRIES_COLLECTION = os.environ['INDUSTRIES_COLLECTION']

SYNC_M_COLLECTION = os.environ['SYNC_M_COLLECTION']
N_LINKS_TO_SKIP_LINKS_SCROLL = int(os.environ.get('N_LINKS_TO_SKIP_LINKS_SCROLL',50))

logging.info(f"Mongo connection: {MONGO_CONNECTION}")
db= MongoClient(MONGO_CONNECTION)[CONTACTACTS_DB]

contacts_collection = db[CONTACTS_COLLECTION]
links_collection = db[LINKS_COLLECTION]

sync_management_collection = db[SYNC_M_COLLECTION]
industries_collection = db[INDUSTRIES_COLLECTION]






def check_index_existence(db,collection_name,*fields ): 
    for _,value in db[collection_name].index_information().items():
        if len(value['key'])!= len(fields):
            continue
        not_match = False
        for vfield,direction in value['key']:
            if vfield not in fields:
                not_match = True
                break
        if not_match == False:
            return True
    return False


if not check_index_existence(db,LINKS_COLLECTION,"link"):
    links_collection.create_index("link",unique=True)

if not check_index_existence(db,CONTACTS_COLLECTION,"place_id"):
    contacts_collection.create_index("place_id",unique=True)
if not check_index_existence(db,CONTACTS_COLLECTION,"link"):
    contacts_collection.create_index("link",unique=True)

# if not check_index_existence(db,RESOURCES_COLLECTION,"az_id"):
#     db[RESOURCES_COLLECTION].create_index("az_id",unique=True)


# if not check_index_existence(db,RESOURCES_COLLECTION,"rocket_id"):
#     db[RESOURCES_COLLECTION].create_index("rocket_id",unique=True,\
#     partialFilterExpression={"rocket_id":{"$type":"string"}})

# if not check_index_existence(db,RESOURCES_COLLECTION,"rocket_id"):
#     db[RESOURCES_COLLECTION].create_index("rocket_id",unique=True,\
#     partialFilterExpression={"rocket_id":{"$type":"string"}})

# if not check_index_existence(db,RESOURCE_GROUPS_COLLECTION,"az_id"):
#     db[RESOURCE_GROUPS_COLLECTION].create_index("az_id",unique=True)

# if not check_index_existence(db,RESOURCE_GROUPS_COLLECTION,"az_id"):
#     db[RESOURCE_GROUPS_COLLECTION].create_index("az_id",unique=True)

# if not check_index_existence(db,SUBSCRIPTIONS_COLLECTION,"subscription_id"):
#     db[SUBSCRIPTIONS_COLLECTION].create_index("subscription_id",unique=True)

# if not check_index_existence(db,SUBSCRIPTIONS_COLLECTION,"subscription_id"):
#     db[SUBSCRIPTIONS_COLLECTION].create_index("subscription_id",unique=True)

