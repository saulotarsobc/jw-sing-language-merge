import sqlite3
import zipfile

con = sqlite3.connect("data-3/userData.db")

JWFILE1 = "files/bkp1.jwlibrary"
JWFILE2 = "files/bkp2.jwlibrary"

# descompactar bkp1


def readData1():
    with zipfile.ZipFile(JWFILE1, 'r') as zip_ref:
        files = zip_ref.namelist()
        zip_ref.extractall("./data-1")

        uploadedDb = "./data-1/userData.db"

        connection = sqlite3.connect(uploadedDb)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Tag")
        Tags = cursor.fetchall()
        print(Tags)

        data = [
            ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
            ("Monty Python's The Meaning of Life", 1983, 7.5),
            ("Monty Python's Life of Brian", 1979, 8.0),
        ]
        cur.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)
        # Remember to commit the transaction after executing INSERT.
        con.commit()


def readData2():
    with zipfile.ZipFile(JWFILE2, 'r') as zip_ref:
        files = zip_ref.namelist()
        zip_ref.extractall("./data-2")

        uploadedDb = "./data-2/userData.db"

        connection = sqlite3.connect(uploadedDb)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Tag")
        Tags = cursor.fetchall()
        print(Tags)


if __name__ == "__main__":
    readData1()
    readData2()
