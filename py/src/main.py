import sqlite3
import zipfile

jwfile1 = "files/bkp1.jwlibrary"
jwfile2 = "files/bkp2.jwlibrary"

# descompactar bkp1
with zipfile.ZipFile(jwfile1, 'r') as zip_ref:
    files = zip_ref.namelist()
    zip_ref.extractall("./data-1")

    # uploadedDb = "./data-1/{0}".format([zipname for zipname in files if zipname.endswith(".db")][0])
    uploadedDb = "./data-1/userData.db"

    connection = sqlite3.connect(uploadedDb)
    cursor = connection.cursor()
    cursor.execute("SELECT Count(*) FROM Tag")
    totoalTags = cursor.fetchall()[0][0]
    print(f"Total de tags: {totoalTags}")

# descompactar bkp2
with zipfile.ZipFile(jwfile2, 'r') as zip_ref:
    files = zip_ref.namelist()
    zip_ref.extractall("./data-2")

    # uploadedDb = "./data-2/{0}".format([zipname for zipname in files if zipname.endswith(".db")][0])
    uploadedDb = "./data-2/userData.db"

    connection = sqlite3.connect(uploadedDb)
    cursor = connection.cursor()
    cursor.execute("SELECT Count(*) FROM Tag")
    totoalTags = cursor.fetchall()[0][0]
    print(f"Total de tags: {totoalTags}")
