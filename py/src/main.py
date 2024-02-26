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
    now = datetime.now(pytz.timezone("America/Santarem"))
    now_date = now.strftime("%Y-%m-%d")
    hour_minute_second = now.strftime("%H-%M-%S")
    now_iso = now.isoformat("T", "seconds")
    now_utc = now.astimezone(pytz.UTC)
    now_utc_iso = now_utc.isoformat("T", "seconds").replace("+00:00", "Z")
    schema_version = 11

    j = f"{{\"name\":\"saulotarsobc_{now_date}\",\"creationDate\":\"{now_date}\",\"version\":1,\"type\":0,\"userDataBackup\":{{\"lastModifiedDate\":\"{now_iso}\",\"deviceName\":\"saulotarsobc\",\"databaseName\":\"userData.db\",\"schemaVersion\":{schema_version}}}}}"
    manifest = json.loads(j)

    with open("./data-3/manifest.json", "w") as f:
        json.dump(manifest, f)


def createNewDataBase():
    con = sqlite3.connect("./data-3/userData.db")

    cur = con.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS Location (LocationId, BookNumber, ChapterNumber, DocumentId, Track, IssueTagNumber, KeySymbol, MepsLanguage, Type, Title)')
    cur.execute('CREATE TABLE IF NOT EXISTS Tag (TagId, Type, Name)')
    cur.execute('CREATE TABLE IF NOT EXISTS TagMap (TagMapId, PlaylistItemId, LocationId, NoteId, TagId, Position)')
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
    con.close()


def getDataFromDb1():
    con1 = sqlite3.connect("./data-1/userData.db")
    con3 = sqlite3.connect("./data-3/userData.db")

    cur1 = con1.cursor()
    cur3 = con3.cursor()

    data = cur1.execute("SELECT * FROM Location").fetchall()
    cur3.executemany("INSERT INTO Location VALUES(?,?,?,?,?,?,?,?,?,?)", data)

    data = cur1.execute("SELECT * FROM Tag").fetchall()
    cur3.executemany("INSERT INTO Tag VALUES(?,?,?)", data)

    data = cur1.execute("SELECT * FROM TagMap").fetchall()
    cur3.executemany("INSERT INTO TagMap VALUES(?,?,?,?,?,?)", data)

    data = cur1.execute("SELECT * FROM Note").fetchall()
    cur3.executemany("INSERT INTO Note VALUES(?,?,?,?,?,?,?,?,?,?)", data)

    data = cur1.execute("SELECT * FROM Bookmark").fetchall()
    cur3.executemany("INSERT INTO Bookmark VALUES(?,?,?,?,?,?,?,?)", data)

    data = cur1.execute("SELECT * FROM UserMark").fetchall()
    cur3.executemany("INSERT INTO UserMark VALUES(?,?,?,?,?,?)", data)

    data = cur1.execute("SELECT * FROM BlockRange").fetchall()
    cur3.executemany("INSERT INTO BlockRange VALUES(?,?,?,?,?,?)", data)

    data = cur1.execute("SELECT * FROM InputField").fetchall()
    cur3.executemany("INSERT INTO InputField VALUES(?,?,?)", data)

    data = cur1.execute("SELECT * FROM LastModified").fetchall()
    cur3.executemany("INSERT INTO LastModified VALUES(?)", data)

    data = cur1.execute("SELECT * FROM IndependentMedia").fetchall()
    cur3.executemany("INSERT INTO IndependentMedia VALUES(?,?,?,?,?)", data)

    data = cur1.execute("SELECT * FROM PlaylistItem").fetchall()
    cur3.executemany("INSERT INTO PlaylistItem VALUES(?,?,?,?,?,?,?)", data)

    data = cur1.execute("SELECT * FROM PlaylistItemAccuracy").fetchall()
    cur3.executemany("INSERT INTO PlaylistItemAccuracy VALUES(?,?)", data)

    data = cur1.execute("SELECT * FROM PlaylistItemIndependentMediaMap").fetchall()
    cur3.executemany("INSERT INTO PlaylistItemIndependentMediaMap VALUES(?,?,?)", data)

    data = cur1.execute("SELECT * FROM PlaylistItemLocationMap").fetchall()
    cur3.executemany("INSERT INTO PlaylistItemLocationMap VALUES(?,?,?,?)", data)

    data = cur1.execute("SELECT * FROM PlaylistItemMarker").fetchall()
    cur3.executemany("INSERT INTO PlaylistItemMarker VALUES(?,?,?,?,?,?)", data)

    data = cur1.execute("SELECT * FROM PlaylistItemMarkerParagraphMap").fetchall()
    cur3.executemany("INSERT INTO PlaylistItemMarkerParagraphMap VALUES(?,?,?,?)", data)

    data = cur1.execute("SELECT * FROM PlaylistItemMarkerBibleVerseMap").fetchall()
    cur3.executemany("INSERT INTO PlaylistItemMarkerBibleVerseMap VALUES(?,?)", data)

    # commit all
    con1.commit()
    con3.commit()



def getDataFromDb2():
    con2 = sqlite3.connect("./data-2/userData.db")
    con3 = sqlite3.connect("./data-3/userData.db")

    cur2 = con2.cursor()
    cur3 = con3.cursor()

    # mapped ids
    mapId = {
        "Location": {},
        "Tag": {},
        "Bookmark": {},
        "UserMark": {},
        "Note": {},
        "PlaylistItem": {},
        "IndependentMedia": {},
        "TagMap": {},
        "PlaylistItemMarker": {},
    }

    # Location
    data = cur2.execute("SELECT * FROM Location").fetchall()
    nextId = cur3.execute("SELECT MAX(LocationId) FROM Location").fetchall()[0][0]
    for r in data:
        nextId += 1
        mapId['Location'][r[0]] = nextId
        cur3.execute("INSERT INTO Location VALUES(?,?,?,?,?,?,?,?,?,?)", (nextId, r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]))

    # Tag
    data = cur2.execute("SELECT * FROM Tag").fetchall()
    nextId = cur3.execute("SELECT MAX(TagId) FROM Tag").fetchall()[0][0]
    for r in data:
        nextId += 1
        mapId['Tag'][r[0]] = nextId
        cur3.execute("INSERT INTO Tag VALUES(?,?,?)", (nextId, r[1], r[2]))
    
    # Bookmark
    data = cur2.execute("SELECT * FROM Bookmark").fetchall()
    nextId = cur3.execute("SELECT MAX(BookmarkId) FROM Bookmark").fetchall()[0][0]
    for r in data:
        nextId += 1
        mapId['Bookmark'][r[0]] = nextId
        cur3.execute("INSERT INTO Bookmark VALUES(?,?,?,?,?,?,?,?)", (nextId, mapId["Location"][r[1]], r[2], r[3], r[4], r[5], r[6], r[7]))
    
    # InputField
    data = cur2.execute("SELECT * FROM InputField").fetchall()
    cur3.executemany("INSERT INTO InputField VALUES(?,?,?)", data)

    # UserMark
    data = cur2.execute("SELECT * FROM UserMark").fetchall()
    nextId = cur3.execute("SELECT MAX(UserMarkId) FROM UserMark").fetchall()[0][0]
    for r in data:
        nextId += 1
        mapId['UserMark'][r[0]] = nextId
        cur3.execute("INSERT INTO UserMark VALUES(?,?,?,?,?)", (nextId, mapId["Location"][r[1]], r[2], r[3], r[4], r[5]))
   
    # BlockRange
    data = cur2.execute("SELECT * FROM BlockRange").fetchall()
    nextId = cur3.execute("SELECT MAX(BlockRangeId) FROM BlockRange").fetchall()[0][0]
    for r in data:
        nextId += 1
        mapId['BlockRange'][r[0]] = nextId
        cur3.execute("INSERT INTO BlockRange VALUES(?,?,?,?,?)", (nextId, r[1], r[2], r[3], mapId["UserMark"][r[4]]))
    
    # Note
    data = cur2.execute("SELECT * FROM Note").fetchall()
    nextId = cur3.execute("SELECT MAX(NoteId) FROM Note").fetchall()[0][0]
    for r in data:
        nextId += 1
        mapId['Note'][r[0]] = nextId
        cur3.execute("INSERT INTO Note VALUES(?,?,?,?,?,?,?,?,?,?)", (nextId, mapId["UserMark"][r[1]], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]))
    
    # PlaylistItem
    data = cur2.execute("SELECT * FROM PlaylistItem").fetchall()
    nextId = cur3.execute("SELECT MAX(PlaylistItemId) FROM PlaylistItem").fetchall()[0][0]
    for r in data:
        nextId += 1
        mapId['PlaylistItem'][r[0]] = nextId
        cur3.execute("INSERT INTO PlaylistItem VALUES(?,?,?,?,?,?,?)", (nextId, r[1], r[2], r[3], r[4], r[5], r[6]))
   
    # PlaylistItemLocationMap
    data = cur2.execute("SELECT * FROM PlaylistItemLocationMap").fetchall()
    for r in data:
        cur3.execute("INSERT INTO PlaylistItemLocationMap VALUES(?,?,?,?)", (mapId["PlaylistItem"][r[0]], mapId["Location"][r[1]], r[2], r[3]))
   
    # IndependentMedia
    data = cur2.execute("SELECT * FROM IndependentMedia").fetchall()
    nextId = cur3.execute("SELECT MAX(IndependentMediaId) FROM IndependentMedia").fetchall()[0][0]
    for r in data:
        nextId += 1
        mapId['IndependentMedia'][r[0]] = nextId
        cur3.execute("INSERT INTO IndependentMedia VALUES(?,?,?,?,?)", (nextId, r[1], r[2], r[3], r[4]))
    
    # TagMap
    data = cur2.execute("SELECT * FROM TagMap").fetchall()
    nextId = cur3.execute("SELECT MAX(TagMapId) FROM TagMap").fetchall()[0][0]
    for r in data:
        nextId += 1
        mapId['TagMap'][r[0]] = nextId
        cur3.execute("INSERT INTO TagMap VALUES(?,?,?,?,?,?)", (nextId, mapId["PlaylistItem"][r[1]], r[2], r[3], mapId["Tag"][r[4]], r[5]))
        # TODO: Acima o LocationId sempre e None. Alerta para caso o dado não exista! Vericar dps...
    
    # PlaylistItemIndependentMediaMap
    data = cur2.execute("SELECT * FROM PlaylistItemIndependentMediaMap").fetchall()
    for r in data:
        nextId += 1
        cur3.execute("INSERT INTO PlaylistItemIndependentMediaMap VALUES(?,?,?)", (mapId["PlaylistItem"][r[0]], mapId["IndependentMedia"][r[1]], r[2]))

    # PlaylistItemMarker
    data = cur2.execute("SELECT * FROM PlaylistItemMarker").fetchall()
    nextId = cur3.execute("SELECT MAX(PlaylistItemMarkerId) FROM PlaylistItemMarker").fetchall()[0][0]
    for r in data:
        nextId += 1
        mapId['PlaylistItemMarker'][r[0]] = nextId
        cur3.execute("INSERT INTO PlaylistItemMarker VALUES(?,?,?,?,?,?)", (nextId, mapId["PlaylistItem"][r[1]], r[2], r[3], r[4], r[5]))
   
    # PlaylistItemMarkerParagraphMap
    data = cur2.execute("SELECT * FROM PlaylistItemMarkerParagraphMap").fetchall()
    for r in data:
        cur3.execute("INSERT INTO PlaylistItemMarkerParagraphMap VALUES(?,?,?,?)", (mapId["PlaylistItemMarker"][r[1]], r[2], r[3]))
   
    # PlaylistItemMarkerBibleVerseMap
    data = cur2.execute("SELECT * FROM PlaylistItemMarkerBibleVerseMap").fetchall()
    for r in data:
        cur3.execute("INSERT INTO PlaylistItemMarkerBibleVerseMap VALUES(?,?)", (mapId["PlaylistItemMarker"][r[0]], r[1]))
   
    # PlaylistItemAccuracy ???
    # LastModified ???

    # commit all
    con2.commit()
    con3.commit()

    # close all
    con2.close()
    con3.close()


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

    print(">> Descopactando bkp 1 e compiando seus arquivos para data-1")
    # sleep(.2)
    readData1()

    print(">> Descopactando bkp 2 e compiando seus arquivos para data-2")
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

    print(">> Copiando dados da base-2 para a nova base\n\n")
    # sleep(.2)
    getDataFromDb2()

    print(">> Criando novo .jwlibrary")
    # sleep(.2)
    createNewBkpFIle()

    print('>> Limpando pastas...')
    # sleep(.2)
    # clearDir("./data-1")
    # clearDir("./data-2")
    # clearDir("./data-3")

    print('\n<<< FIM >>>')
