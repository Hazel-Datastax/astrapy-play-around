import astrapy
import os
from dotenv import load_dotenv
import json
import pandas as pd
from astrapy.database import CollectionVectorServiceOptions

# Load the .env file and get the environment variables
load_dotenv(".env")
token = os.getenv('ASTRA_DB_APPLICATION_TOKEN')
endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')
provider_key = os.getenv('ASTRA_DB_EMBEDDING_API_KEY')

# Connect to the database
client = astrapy.DataAPIClient(token)
database = client.get_database_by_api_endpoint(endpoint)

# creat a vector collection
collection_vector = database.create_collection(
    "jinaAI",
    dimension=768,
    metric=astrapy.constants.VectorMetric.COSINE,
    embedding_api_key=provider_key,
    service=CollectionVectorServiceOptions(
        provider="jinaAI",
        model_name="jina-embeddings-v2-base-de"
    ))

# Truncate the collection
# collection_vector.delete_all()

# Load the data
with open("movies.json", "r") as f:
    movies = json.load(f)
    for movie in movies:
        movie["$vectorize"] = movie["Description"]
    del movie["Description"]
    collection_vector.insert_many(movies)

# Define the prompts
query = "Something like cars and escaping"

filter = {
    # "Rate": {"$gte": 8},
    # "Duration" : {"$lte": 120},
    # "Year" : {"$lte": 1990},
    # "Genre": {"$in": ["Comedy"]}
}

resp = collection_vector.find(
      filter=filter,
      sort={"$vectorize": query},
      projection={"_id": 0, "$vectorize": 1, "$vector": 0},
      limit = 5)


for result in resp:
    print(f"{result['summary']}: {result['$similarity']}")

resp_df = pd.DataFrame(list(resp))
