import json
from db import SQLiteError, DBError, open_connection
from embedding_util import generate_embeddings

# Hardcoded data to insert into the posts table
HARDCODED_DATA = [
    (1, '2023-01-01 00:00:00',
     'The quick brown fox jumps over the lazy dog.', 'Jumping Fox'),
    (1, '2023-01-02 00:00:00',
     'Sunsets on Mars appear blue to human observers.', 'Blue Mars Sunsets'),
    (1, '2023-01-03 00:00:00', 'Honey never spoils; archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly good to eat.', 'Eternal Honey'),
    (1, '2023-01-04 00:00:00', 'A day on Venus is longer than a year on Venus; it takes Venus 243 Earth-days to fully rotate on its axis, but only 225 Earth-days to orbit the Sun.', 'Venusian Time'),
    (1, '2023-01-05 00:00:00',
     'Bananas are berries, but strawberries are not.', 'Berry Confusion'),
    (1, '2023-01-06 00:00:00',
     'Shakespeare invented the name Jessica for his play Merchant of Venice.', 'Shakespearean Name'),
    (1, '2023-01-07 00:00:00',
     'The Eiffel Tower can be 15 cm taller during the summer when its iron structure expands due to the heat.', 'Expanding Eiffel'),
    (1, '2023-01-08 00:00:00',
     'A group of flamingos is called a "flamboyance".', 'Flamingo Group'),
    (1, '2023-01-09 00:00:00',
     'Octopuses have three hearts, but two of them actually stop beating when they swim.', 'Octopus Hearts'),
    (1, '2023-01-10 00:00:00',
     'The shortest war in history was between Zanzibar and England in 1896; Zanzibar surrendered after 38 minutes.', 'Shortest War')
]

# Path to the SQLite extensions and database
vector_extension_path = "./vector0.dylib"
vss_extension_path_vss = "./vss0.dylib"

# SQL query using "INSERT OR IGNORE" to handle potential conflicts with existing data
insert_query = """
INSERT OR IGNORE INTO posts (author, published, content, title) VALUES 
(?, ?, ?, ?)
"""

# SQL query to insert into the vss_chatHistory virtual table
insert_vss_query = """
INSERT INTO vss_posts (rowid, content_embedding) VALUES (?, ?)
"""


def add_test_data(db):
    try:
        cursor = db.cursor()
        # Execute the insert query for each wp_posts data entry
        for post_data in HARDCODED_DATA:
            # Insert post data into wp_posts
            cursor.execute(insert_query, post_data)

            # Get the last inserted row ID
            last_row_id = cursor.lastrowid

            # Assuming post content is to be used for message embedding
            message_embedding = json.dumps(
                generate_embeddings(post_data[3]))  # Example embedding

            # Insert data into vss_chatHistory virtual table
            cursor.execute(insert_vss_query, (last_row_id, message_embedding))

        # Commit the changes to the database
        cursor.close()
        db.commit()

    except SQLiteError.Error as err:
        print("Error:", err)
        cursor.rollback()

    finally:
        # Close the cursor and connection
        db.close()


def setup_db():
    db = open_connection()

    # Check VSS version
    try:
        db.execute("SELECT vss_version() AS version").fetchone()
    except DBError as err:
        print("Error running vss_version()", err)
        raise

    # Create the chatHistory table and vss_chatHistory virtual table
    try:
        db.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                author INT,
                published TEXT,
                content TEXT,
                title TEXT
            );
        ''')
        db.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS vss_posts USING vss0(content_embedding(768));
        ''')
    except DBError as err:
        print("Error creating tables", err)
        raise
    try:
        add_test_data(db)
    except Exception as err:
        print('failed', str(err))

    return db
