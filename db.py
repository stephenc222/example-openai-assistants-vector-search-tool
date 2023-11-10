# Same api as sqlite3, but allows loading custom extensions
import sqlean as sqlite3

db_path = "./blog.sqlite"
# Path to the SQLite extensions and database
vector_extension_path = "./vector0.dylib"
vss_extension_path_vss = "./vss0.dylib"


class SQLiteError(sqlite3.Error):
    pass


class DBError(sqlite3.DatabaseError):
    pass


def load_extension(db, path):
    db.enable_load_extension(True)
    db.load_extension(path)


# NOTE: Every sqlite db connection needs the sqlite-vss extension loaded.
def open_connection():
    db = sqlite3.connect(db_path)
    try:
        load_extension(db, vector_extension_path)
    except DBError as err:
        print("Failed to load vector extension", err)
        raise
    try:
        load_extension(db, vss_extension_path_vss)
    except DBError as err:
        print("Failed to load VSS extension", err)
        raise

    return db
