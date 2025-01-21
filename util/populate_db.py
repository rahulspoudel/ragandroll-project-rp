import os
from git import Repo
import streamlit as st
import snowflake.connector

# Clone the GitHub repository
repo_url = 'git@github.com:Lyrics/lyrics-database.git'
repo_dir = '/tmp/lyrics-database'
if not os.path.exists(repo_dir):
    Repo.clone_from(repo_url, repo_dir)

# Snowflake connection parameters
SNOWFLAKE_USER = st.secrets["snowflakeconnection"]["user"]
SNOWFLAKE_PASSWORD = st.secrets["snowflakeconnection"]["password"]
SNOWFLAKE_ACCOUNT = st.secrets["snowflakeconnection"]["account"]
SNOWFLAKE_DATABASE = st.secrets["snowflakeconnection"]["database"]
SNOWFLAKE_SCHEMA = st.secrets["snowflakeconnection"]["schema"]
SNOWFLAKE_WAREHOUSE = st.secrets["snowflakeconnection"]["warehouse"]
SNOWFLAKE_TABLE = "LYLYRIC"

# Connect to Snowflake
conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA
)
cur = conn.cursor()

# Create table if not exists
create_table_query = f"""
CREATE TABLE IF NOT EXISTS {SNOWFLAKE_TABLE} (
    artist STRING,
    album STRING,
    song_title STRING,
    lyrics STRING
)
"""
cur.execute(create_table_query)

# Function to insert lyrics into Snowflake


def insert_lyrics(artist, album, song_title, lyrics):
    insert_query = f"""
    INSERT INTO {SNOWFLAKE_TABLE} (artist, album, song_title, lyrics)
    VALUES (%s, %s, %s, %s)
    """
    cur.execute(insert_query, (artist, album, song_title, lyrics))


# Traverse the cloned repository and insert lyrics into Snowflake
for root, dirs, files in os.walk(repo_dir):
    for file in files:
        # Extract artist, album, and song title from the directory structure
        path_parts = root.split(os.sep)
        artist = path_parts[-2] if len(path_parts) >= 2 else "Unknown"
        album = path_parts[-1] if len(path_parts) >= 1 else "Unknown"
        song_title = file  # Since file doesn't have an extension
        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
            lyrics = f.read()
            insert_lyrics(artist, album, song_title, lyrics)

# Close the connection
cur.close()
conn.close()
