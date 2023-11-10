import json
import sqlite3
from db import open_connection
from embedding_util import generate_embeddings


def vector_search(arguments):
    arg_object = json.loads(arguments)
    query = arg_object['query']
    query_embedding = generate_embeddings(query)

    db_connection = open_connection()
    cursor = db_connection.cursor()

    try:
        # Perform the SQL query and fetch the results
        cursor.execute(
            '''
            with matches as (
                select rowid,
                distance
                from vss_posts where vss_search(content_embedding, (?))
                limit 10
            )
            select
            posts.content,
            posts.published,
            matches.distance
            from matches 
            left join posts on posts.rowid = matches.rowid
            ''',
            [json.dumps(
                query_embedding)]
        )
        result = cursor.fetchall()
        return result
    except sqlite3.Error as err:
        # Handle the error as appropriate
        print("An error occurred:", err)
    finally:
        # Close the cursor and the connection
        cursor.close()
        db_connection.close()
