import sqlite3

from src.database import DATABASE_PATH


def main():

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM update_days
        WHERE update_date = ?
    """, ("2026-09-11",))

    connection.commit()

    connection.close()

    print("Test update day removed.")


if __name__ == "__main__":
    main()