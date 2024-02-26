import os
import sqlite3
import zipfile
import shutil
from time import sleep


JWFILE1 = "files/bkp1.jwlibrary"
JWFILE2 = "files/bkp2.jwlibrary"


os.makedirs("./data-3", exist_ok=True)

for file in os.listdir("./data-3"):
    os.remove(f"./data-3/{file}")


def readData1():
    with zipfile.ZipFile(JWFILE1, "r") as zip_ref:
        files = zip_ref.namelist()
        zip_ref.extractall("./data-1")


def readData2():
    with zipfile.ZipFile(JWFILE2, "r") as zip_ref:
        files = zip_ref.namelist()
        zip_ref.extractall("./data-2")


def copyAllFilesToData3():
    for file in os.listdir("./data-1"):
        if file != "userData.db" and file != "manifest.json" and file != "default_thumbnail.png":
            shutil.copy(f"./data-1/{file}", f"./data-3/{file}")

    for file in os.listdir("./data-2"):
        if file != "userData.db" and file != "manifest.json" and file != "default_thumbnail.png":
            shutil.copy(f"./data-2/{file}", f"./data-3/{file}")


def db3():
    con = sqlite3.connect("./data-3/userData.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS Tag(TagId, Type, Name)")


if __name__ == "__main__":
    print("Lendo bkp 1")
    sleep(1)
    readData1()

    print("Lendo bkp 2")
    sleep(1)
    readData2()

    print("Copiando todos os arquivos para /data-3")
    sleep(1)
    copyAllFilesToData3()

    print('<<< FIM >>>')
