import pandas as pd
import json

# Load the data
df = pd.read_csv("IMDB_top_1000.csv")

# Drop the index column
df = df.drop(columns=["Unnamed: 0"])

# Remove the number in the Title column
df["Title"] = df["Title"].str.replace(r"^\d+\.\s*", "", regex=True)
# Remove the year in the Title column and create a new column for the year
df["Year"] = df["Title"].str.extract(r"\((\d{4})\)").astype(int)
df["Title"] = df["Title"].str.replace(r"\s*\(\d{4}\)$", "", regex=True)
# Remove the min in the Duration column and convert it to an integer
df["Duration"] = df["Duration"].str.replace(" min", "").astype(int)
# Make the Genre column a list of genres
df["Genre"] = df["Genre"].str.split(", ")
# Drop Metascore column
df = df.drop(columns=["Metascore"])
# Fill NaN values in the Certificate column with "Not Rated"
df["Certificate"] = df["Certificate"].fillna("Not Rated")

# Convert the DataFrame to a list of dictionaries
movies = df.to_dict(orient="records")
# export the data to a json file
with open("movies.json", "w") as f:
    json.dump(movies, f, indent=4)

