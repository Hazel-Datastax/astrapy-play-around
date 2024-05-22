import astrapy
import os
from dotenv import load_dotenv
import json

# Load the .env file and get the environment variables
load_dotenv(".env")
token = os.getenv('ASTRA_DB_APPLICATION_TOKEN')
endpoint = os.getenv('ASTRA_DB_API_ENDPOINT')

# Define the variables
collection_name = "demo"
dimension = 1536
metric = astrapy.constants.VectorMetric.COSINE
service = {
    "provider": "openai",
    "modelName": "text-embedding-3-small",
}

# Connect to the database
client = astrapy.DataAPIClient(token)
database = client.get_database_by_api_endpoint(endpoint)

# Create a vector collection
collection_vector = database.create_collection(
    collection_name,
    dimension=dimension,
    metric=metric,
    service=service
)

# Truncate the collection
collection_vector.delete_all()

# Load the data
movies = json.load(open("movies.json"))

# Insert the data into the collection - split movies into 50 batches(20 docs per batch)
batch_size = 20
for i in range(0, len(movies), batch_size):
    batch = movies[i:i + batch_size]
    collection_vector.insert_many(batch)
