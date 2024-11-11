from astrapy import DataAPIClient
from astrapy.api_options import APIOptions, WireFormatOptions
from astrapy.data_types import DataAPIVector
from dotenv import load_dotenv
import numpy as np
import time
import os

# optional. Comment out for a less verbose logging (uncommented: shows all payloads, responses, headers etc)
# import logging
# logging.basicConfig(level=logging.DEBUG)

load_dotenv(".env")
token = os.getenv('ASTRA_DB_APPLICATION_TOKEN')
endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')

db = DataAPIClient(
    environment="prod",
    api_options=APIOptions(
        database_additional_headers={"Feature-Flag-tables": "true"},
        wire_format_options=WireFormatOptions(
            binary_encode_vectors=False,           # False to disable default bin-encoding in client (but DataAPIVectors are still forcibly bin-encoded)
            custom_datatypes_in_reading=True,     # False to return lists instead of DataAPIVector's
            coerce_iterables_to_vectors=False,    # True to accept generators, lazy stuff & other "vector-likes" in payloads
        ),
    ),
).get_database(endpoint, token=token)
db.get_database_admin().create_keyspace("default_keyspace", update_db_keyspace=True)

# create a collection and write to it
v3 = db.create_collection('test-binary-vector', dimension=1000)

v3.insert_one({"$vector": np.random.rand(1000).tolist()})                 # will be sent according to `binary_encode_vectors`
v3.insert_one({"$vector": DataAPIVector(np.random.rand(1000).tolist())})  # will be sent as binary nevertheless
v3.delete_many({})

vector = [{"$vector": np.random.rand(1000).tolist()} for _ in range(1000)]
binary_vector = [{"$vector": DataAPIVector(np.random.rand(1000).tolist())} for _ in range(1000)]

vector_start_time = time.time()
for i in range(1000):
    v3.insert_one(vector[i])
vector_end_time = time.time()
print(f"Inserting 1000 raw vectors took {vector_end_time - vector_start_time} seconds")

binary_vector_start_time = time.time()
for i in range(1000):
    v3.insert_one(binary_vector[i])
binary_vector_end_time = time.time()
print(f"Inserting 1000 binary vectors took {binary_vector_end_time - binary_vector_start_time} seconds")