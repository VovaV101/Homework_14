import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from mongomock import MongoClient as MockMongoClient

env_path = Path(__file__).parent.parent.joinpath(".env")
if env_path.is_file:
    print(env_path)
    load_dotenv(env_path)

MongoDB_USER = os.getenv('MongoDB_USER')
MongoDB_PASSWORD = os.getenv('MongoDB_PASSWORD')
MongoDB_HOST = os.getenv('MongoDB_HOST')
MongoDB_NAME = os.getenv('MongoDB_NAME')

client = None

if MongoDB_USER:
    URI = f"mongodb+srv://{MongoDB_USER}:{MongoDB_PASSWORD}@{MongoDB_HOST}/?retryWrites=true&w=majority"
    try:
        client = MongoClient(URI)
    except errors.ConfigurationError:
        print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
    except errors as e:
         print("pymongo error:", e)
else:
    print("not defined MongoDB_USER. Database not connected")

print(f"{URI=}")

if client:
    db = client.get_database(MongoDB_NAME)
else:
    db = MockMongoClient().get_database(MongoDB_NAME)  #
