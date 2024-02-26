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
    now = datetime.now(pytz.timezone('America/Santarem'))
    now_date = now.strftime("%Y-%m-%d")
    hour_minute_second = now.strftime("%H-%M-%S")
    now_iso = now.isoformat("T", "seconds")
    now_utc = now.astimezone(pytz.UTC)
    now_utc_iso = now_utc.isoformat("T", "seconds").replace('+00:00', 'Z')
    schema_version = 11

    j = '{{"name":"jwlibrary-plus-backup_{0}","creationDate":"{1}","version":1,"type":0,"userDataBackup":{{"lastModifiedDate":"{2}","deviceName":"jwlibrary-plus","databaseName":"userData.db","schemaVersion":{3}}}}}'.format(
        now_date, now_date, now_iso, schema_version)
    manifest = json.loads(j)

    with open('./data-3/manifest.json', 'w') as f:
            json.dump(manifest, f)


def createNewDataBase():
    con = sqlite3.connect("./data-3/userData.db")
    
    cur = con.cursor()
    
    cur.execute('CREATE TABLE IF NOT EXISTS Location (LocationId, BookNumber, ChapterNumber, DocumentId, Track, IssueTagNumber, KeySymbol, MepsLanguage, "Type", Title)')
    cur.execute('CREATE TABLE IF NOT EXISTS Tag (TagId, "Type", Name)')
    cur.execute('CREATE TABLE IF NOT EXISTS TagMap (TagMapId, PlaylistItemId, LocationId, NoteId, TagId, "Position")')
    cur.execute('CREATE TABLE IF NOT EXISTS Note (NoteId, Guid, UserMarkId, LocationId, Title, Content, LastModified, Created, BlockType, BlockIdentifier)')
    cur.execute('CREATE TABLE IF NOT EXISTS Bookmark (BookmarkId, LocationId, PublicationLocationId, Slot, Title, Snippet, BlockType, BlockIdentifier)')
    cur.execute('CREATE TABLE IF NOT EXISTS UserMark (UserMarkId, ColorIndex, LocationId, StyleIndex, UserMarkGuid, Version)')
    cur.execute('CREATE TABLE IF NOT EXISTS BlockRange (BlockRangeId, BlockType, Identifier, StartToken, EndToken, UserMarkId)')
    cur.execute('CREATE TABLE IF NOT EXISTS InputField (LocationId, TextTag, Value)')
    cur.execute('CREATE TABLE IF NOT EXISTS LastModified (LastModified)')
    cur.execute('CREATE TABLE IF NOT EXISTS IndependentMedia (IndependentMediaId, OriginalFilename, FilePath, MimeType, Hash)')
    cur.execute('CREATE TABLE IF NOT EXISTS PlaylistItem (PlaylistItemId, Label, StartTrimOffsetTicks, EndTrimOffsetTicks, Accuracy, EndAction, ThumbnailFilePath)')
    cur.execute('CREATE TABLE IF NOT EXISTS PlaylistItemAccuracy (PlaylistItemAccuracyId, Description)')
    cur.execute('CREATE TABLE IF NOT EXISTS PlaylistItemIndependentMediaMap (PlaylistItemId, IndependentMediaId, DurationTicks)')
    cur.execute('CREATE TABLE IF NOT EXISTS PlaylistItemLocationMap (PlaylistItemId, LocationId, MajorMultimediaType, BaseDurationTicks)')
    cur.execute('CREATE TABLE IF NOT EXISTS PlaylistItemMarker (PlaylistItemMarkerId, PlaylistItemId, Label, StartTimeTicks, DurationTicks, EndTransitionDurationTicks)')
    cur.execute('CREATE TABLE IF NOT EXISTS PlaylistItemMarkerParagraphMap (PlaylistItemMarkerId, MepsDocumentId, ParagraphIndex, MarkerIndexWithinParagraph)')
    cur.execute('CREATE TABLE IF NOT EXISTS PlaylistItemMarkerBibleVerseMap (PlaylistItemMarkerId, VerseId)')
    
    con.commit()


def getDataFromDb1():
    con1 = sqlite3.connect("./data-1/userData.db")
    con2 = sqlite3.connect("./data-2/userData.db")
    con3 = sqlite3.connect("./data-3/userData.db")

    cur1 = con1.cursor()
    cur2 = con2.cursor()
    cur3 = con3.cursor()

    Location = cur1.execute("SELECT * FROM Location").fetchall()
    cur3.executemany("INSERT INTO Location VALUES(?,?,?,?,?,?,?,?,?,?)", Location)
   
    Tag = cur1.execute("SELECT * FROM Tag").fetchall()
    cur3.executemany("INSERT INTO Tag VALUES(?,?,?)", Tag)
  
    TagMap = cur1.execute("SELECT * FROM TagMap").fetchall()
    cur3.executemany("INSERT INTO TagMap VALUES(?,?,?,?,?,?)", TagMap)
   
    Note = cur1.execute("SELECT * FROM Note").fetchall()
    cur3.executemany("INSERT INTO Note VALUES(?,?,?,?,?,?,?,?,?,?)", Note)
   
    Bookmark = cur1.execute("SELECT * FROM Bookmark").fetchall()
    cur3.executemany("INSERT INTO Bookmark VALUES(?,?,?,?,?,?,?,?)", Bookmark)
    
    UserMark = cur1.execute("SELECT * FROM UserMark").fetchall()
    cur3.executemany("INSERT INTO UserMark VALUES(?,?,?,?,?,?)", UserMark)
    
    BlockRange = cur1.execute("SELECT * FROM BlockRange").fetchall()
    cur3.executemany("INSERT INTO BlockRange VALUES(?,?,?,?,?,?,?,?)", BlockRange)

    # commit all
    con1.commit()
    con2.commit()
    con3.commit()


def createNewBkpFIle():
    zf = zipfile.ZipFile('./merged.jwlibrary', "w",
                         compression=zipfile.ZIP_DEFLATED)
    for file in os.listdir('./data-3'):
        zf.write(f"./data-3/{file}", arcname=file)

    zf.close()

if __name__ == "__main__":
    print('<<< Iniciando...>>>\n\n>> Limpando pastas...')
    clearDir("./data-1")
    clearDir("./data-2")
    clearDir("./data-3")

    print(">> Lendo bkp 1")
    # sleep(.2)
    readData1()

    print(">> Lendo bkp 2")
    # sleep(.2)
    readData2()

    print(">> Copiando todos os arquivos de /data-1 e /data-2 para /data-3")
    # sleep(.2)
    copyAllFilesToData3()

    print(">> Copiando default_thumbnail.png para /data-3")
    # sleep(.2)
    copyThumbNail()

    print(">> Criando e copiando manifest.json para /data-3")
    # sleep(.2)
    manifestGenerator()

    print(">> Criando nova base de dados")
    # sleep(.2)
    createNewDataBase()

    print(">> Copiando dados da base-1 para a nova base")
    # sleep(.2)
    getDataFromDb1()

    print(">> Criando novo .jwlibrary")
    # sleep(.2)
    createNewBkpFIle()

    print('>> Limpando pastas...')
    # sleep(.2)
    clearDir("./data-1")
    clearDir("./data-2")
    clearDir("./data-3")

    print('\n<<< FIM >>>')
