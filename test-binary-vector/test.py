from astrapy import DataAPIClient
from astrapy.api_options import APIOptions, WireFormatOptions
from astrapy.data_types import DataAPIVector
from dotenv import load_dotenv
import numpy as np
import time
import os
import inspect

load_dotenv("../.env")
token = os.getenv('ASTRA_DB_APPLICATION_TOKEN')
endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')

db = DataAPIClient(
    environment="test",
    api_options=APIOptions(
        database_additional_headers={"Feature-Flag-tables": "true"},
        wire_format_options=WireFormatOptions(
            binary_encode_vectors=False,
            # False to disable default bin-encoding in client (but DataAPIVectors are still forcibly bin-encoded)
            custom_datatypes_in_reading=True,  # False to return lists instead of DataAPIVector's
            coerce_iterables_to_vectors=False,
            # True to accept generators, lazy stuff & other "vector-likes" in payloads
        ),
    ),
).get_database(endpoint, token=token)
db.get_database_admin().create_keyspace("default_keyspace", update_db_keyspace=True)


def vector_insert_one(count: int, dimension: int):
    vector = [{"$vector": np.random.rand(dimension).tolist()} for _ in range(count)]
    collection_name = inspect.currentframe().f_code.co_name
    # create a collection and write to it
    collection = db.create_collection(collection_name, dimension=dimension)
    start = time.time()
    for i in range(count):
        collection.insert_one(vector[i])
    end = time.time()
    db.drop_collection(collection_name)
    return end - start


def vector_insert_many(count: int, dimension: int):
    vector = [{"$vector": np.random.rand(dimension).tolist()} for _ in range(count)]
    collection_name = inspect.currentframe().f_code.co_name
    # create a collection and write to it
    collection = db.create_collection(collection_name, dimension=dimension)
    start = time.time()
    collection.insert_many(vector)
    end = time.time()
    db.drop_collection(collection_name)
    return end - start


def binary_vector_insert_one(count: int, dimension: int):
    binary_vector = [{"$vector": DataAPIVector(np.random.rand(dimension).tolist())} for _ in range(count)]
    collection_name = inspect.currentframe().f_code.co_name
    collection = db.create_collection(collection_name, dimension=dimension)
    start = time.time()
    for i in range(count):
        collection.insert_one(binary_vector[i])
    end = time.time()
    db.drop_collection(collection_name)
    return end - start


def binary_vector_insert_many(count: int, dimension: int):
    binary_vector = [{"$vector": DataAPIVector(np.random.rand(dimension).tolist())} for _ in range(count)]
    collection_name = inspect.currentframe().f_code.co_name
    collection = db.create_collection(collection_name, dimension=dimension)
    start = time.time()
    collection.insert_many(binary_vector)
    end = time.time()
    db.drop_collection(collection_name)
    return end - start


def main():
    results = []
    for func in [vector_insert_one, vector_insert_many, binary_vector_insert_one, binary_vector_insert_many]:
        result = func(1000, 1000)
        results.append((func.__name__, result))

    results.sort(key=lambda x: x[1])
    slowest = results[-1][1]
    for name, duration in results:
        print(f"{name}: \t{duration:.12f} seconds \t {duration / slowest:.2f}x")


if __name__ == "__main__":
    main()
