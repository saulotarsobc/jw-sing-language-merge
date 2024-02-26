import sqlite3
import zipfile

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
