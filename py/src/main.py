import os
import sqlite3
import zipfile
import shutil
from time import sleep
from datetime import datetime, timedelta
import pytz
import json


JWFILE1 = "files/bkp1.jwlibrary"
JWFILE2 = "files/bkp2.jwlibrary"


os.makedirs("./data-3", exist_ok=True)


def clearDir(dir):
    for file in os.listdir(dir):
        os.remove(f"{dir}/{file}")


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


def copyThumbNail():
    shutil.copy("./extra/default_thumbnail.png",
                "./data-3/default_thumbnail.png")


def manifestGenerator():
    now = datetime.now(pytz.timezone('Europe/Madrid'))
    now_date = now.strftime("%Y-%m-%d")
    hour_minute_second = now.strftime("%H-%M-%S")
    now_iso = now.isoformat("T", "seconds")
    now_utc = now.astimezone(pytz.UTC)
    now_utc_iso = now_utc.isoformat("T", "seconds").replace('+00:00', 'Z')
    schema_version = 14

    j = '{{"name":"jwlibrary-plus-backup_{0}","creationDate":"{1}","version":1,"type":0,"userDataBackup":{{"lastModifiedDate":"{2}","deviceName":"jwlibrary-plus","databaseName":"userData.db","schemaVersion":{3}}}}}'.format(
        now_date, now_date, now_iso, schema_version)
    manifest = json.loads(j)

    print(manifest)


def db3():
    con = sqlite3.connect("./data-3/userData.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS Tag(TagId, Type, Name)")


if __name__ == "__main__":
    print('>> Limpando pastas...')
    clearDir("./data-1")
    clearDir("./data-2")
    clearDir("./data-3")

    print(">> Lendo bkp 1")
    sleep(.3)
    readData1()

    print(">> Lendo bkp 2")
    sleep(.3)
    readData2()

    print(">> Copiando todos os arquivos para /data-3")
    sleep(.3)
    copyAllFilesToData3()

    print(">> Copiando default_thumbnail.png para /data-3")
    sleep(.3)
    copyThumbNail()

    print(">> Criando e copiando manifest.json para /data-3")
    sleep(.3)
    manifestGenerator()

    # print('>> Limpando pastas...')
    # sleep(.3)
    # clearDir("./data-1")
    # clearDir("./data-2")
    # clearDir("./data-3")

    print('<<< FIM >>>')
