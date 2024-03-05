import os
import sqlite3
import zipfile
from shutil import copy, rmtree
from datetime import datetime
import pytz
import json
from hashlib import sha256
import uuid
from os import makedirs, listdir, remove

FINALFILENAME = "Merged_Backup.jwlibrary"
HASH = "<=hash>="


def createDirs():
    makedirs("data-4", exist_ok=True)


def copyThumbNail():
    copy("extra/default_thumbnail.png", "data-4/default_thumbnail.png")


def copyDatabase():
    copy("extra/userData.db", "data-4/userData.db")


def hashCalc():
    global HASH
    with open("data-4/userData.db", "rb") as f:
        HASH = sha256(f.read()).hexdigest()


def manifestGenerator():
    now = datetime.now(pytz.timezone("America/Santarem"))
    now_date = now.strftime("%Y-%m-%d")
    hour_minute_second = now.strftime("%H-%M-%S")
    now_iso = now.isoformat("T", "seconds")
    now_utc = now.astimezone(pytz.UTC)
    now_utc_iso = now_utc.isoformat("T", "seconds").replace("+00:00", "Z")
    schema_version = 11

    j = f"{{\"name\":\"{FINALFILENAME}\",\"creationDate\":\"{now_date}\",\"version\":1,\"type\":0,\"userDataBackup\":{{\"lastModifiedDate\":\"{now_iso}\",\"deviceName\":\"saulotarsobc\",\"databaseName\":\"userData.db\",\"hash\":\"{HASH}\",\"schemaVersion\":{schema_version}}}}}"
    manifest = json.loads(j)

    with open("data-4/manifest.json", "w") as f:
        json.dump(manifest, f)


if __name__ == "__main__":
    print("<<< Iniciando...>>>")

    print("> Criando diretorion")
    createDirs()

    print(">> Copiando nova base de dados")
    copyDatabase()

    print(">> Copiando default_thumbnail.png para /data-3")
    copyThumbNail()

    print(">> Gerando nova hash")
    hashCalc()

    print(">> Criando e copiando manifest.json para /data-3")
    manifestGenerator()
