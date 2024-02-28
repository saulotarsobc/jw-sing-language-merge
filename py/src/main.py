import os
import sqlite3
import zipfile
import shutil
from datetime import datetime, timedelta
import pytz
import json
import hashlib


JWFILE1 = "./bkp1.jwlibrary"
JWFILE2 = "./bkp2.jwlibrary"
FINALFILENAME = "new_backup.jwlibrary"
HASH = ""


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

def hashCalc():
    global HASH
    with open("./data-3/userData.db", "rb") as f:
        bytes = f.read() # read entire file as bytes
        HASH = hashlib.sha256(bytes).hexdigest()

def manifestGenerator():
    now = datetime.now(pytz.timezone("America/Santarem"))
    now_date = now.strftime("%Y-%m-%d")
    hour_minute_second = now.strftime("%H-%M-%S")
    now_iso = now.isoformat("T", "seconds")
    now_utc = now.astimezone(pytz.UTC)
    now_utc_iso = now_utc.isoformat("T", "seconds").replace("+00:00", "Z")
    schema_version = 11

    j = f"{{\"name\":\"{FINALFILENAME}\",\"creationDate\":\"{now_date}\",\"version\":1,\"type\":0,\"userDataBackup\":{{\"lastModifiedDate\":\"{now_iso}\",\"deviceName\":\"saulotarsobc\",\"databaseName\":\"userData.db\",\"schemaVersion\":{schema_version}}}}}"
    manifest = json.loads(j)

    with open("./data-3/manifest.json", "w") as f:
        json.dump(manifest, f)


def createNewDataBase():
    con = sqlite3.connect("./data-3/userData.db")

    cur = con.cursor()

    # Create tables
    cur.executescript('''CREATE TABLE -- IndependentMedia definition
            IndependentMedia (
                IndependentMediaId INTEGER NOT NULL PRIMARY KEY,
                OriginalFilename TEXT NOT NULL,
                FilePath TEXT NOT NULL UNIQUE,
                MimeType TEXT NOT NULL,
                Hash TEXT NOT NULL,
                CHECK (length (OriginalFilename) > 0),
                CHECK (length (FilePath) > 0),
                CHECK (length (MimeType) > 0),
                CHECK (length (Hash) > 0)
            );

        -- LastModified definition
        CREATE TABLE
            LastModified (LastModified TEXT NOT NULL);

        -- Location definition
        CREATE TABLE
            Location (
                LocationId INTEGER NOT NULL PRIMARY KEY,
                BookNumber INTEGER,
                ChapterNumber INTEGER,
                DocumentId INTEGER,
                Track INTEGER,
                IssueTagNumber INTEGER NOT NULL DEFAULT 0,
                KeySymbol TEXT,
                MepsLanguage INTEGER,
                Type INTEGER NOT NULL,
                Title TEXT,
                UNIQUE (
                    BookNumber,
                    ChapterNumber,
                    KeySymbol,
                    MepsLanguage,
                    Type
                ),
                UNIQUE (
                    KeySymbol,
                    IssueTagNumber,
                    MepsLanguage,
                    DocumentId,
                    Track,
                    Type
                ),
                CHECK (
                    (
                        Type = 0
                        AND ( -- Document or Bible chapter
                            (
                                DocumentId IS NOT NULL
                                AND DocumentId != 0
                            )
                            OR ( -- Track based. Requires DocumentId or KeySymbol.
                                Track IS NOT NULL
                                AND (
                                    (
                                        KeySymbol IS NOT NULL
                                        AND (length (KeySymbol) > 0)
                                    )
                                    OR (
                                        DocumentId IS NOT NULL
                                        AND DocumentId != 0
                                    )
                                )
                            )
                            OR ( -- Bible book. Requires KeySymbol.
                                BookNumber IS NOT NULL
                                AND BookNumber != 0
                                AND KeySymbol IS NOT NULL
                                AND (length (KeySymbol) > 0)
                                AND (
                                    ChapterNumber IS NULL
                                    OR ChapterNumber = 0
                                )
                            )
                            OR ( -- Bible chapter. Requires KeySymbol and BookNumber.
                                ChapterNumber IS NOT NULL
                                AND ChapterNumber != 0
                                AND BookNumber IS NOT NULL
                                AND BookNumber != 0
                                AND KeySymbol IS NOT NULL
                                AND (length (KeySymbol) > 0)
                            )
                        )
                    )
                    OR Type != 0
                ),
                CHECK (
                    (
                        Type = 1 -- Bible
                        AND (
                            BookNumber IS NULL
                            OR BookNumber = 0
                        )
                        AND (
                            ChapterNumber IS NULL
                            OR ChapterNumber = 0
                        )
                        AND (
                            DocumentId IS NULL
                            OR DocumentId = 0
                        )
                        AND KeySymbol IS NOT NULL
                        AND (length (KeySymbol) > 0)
                        AND Track IS NULL
                    )
                    OR Type != 1
                ),
                CHECK (
                    (
                        Type IN (2, 3) -- Mediator audio/video
                        AND (
                            BookNumber IS NULL
                            OR BookNumber = 0
                        )
                        AND (
                            ChapterNumber IS NULL
                            OR ChapterNumber = 0
                        )
                    )
                    OR Type NOT IN (2, 3)
                )
            );

        CREATE INDEX IX_Location_KeySymbol_MepsLanguage_BookNumber_ChapterNumber ON Location (
            KeySymbol,
            MepsLanguage,
            BookNumber,
            ChapterNumber
        );

        CREATE INDEX IX_Location_MepsLanguage_DocumentId ON Location (MepsLanguage, DocumentId);

        -- PlaylistItemAccuracy definition
        CREATE TABLE
            PlaylistItemAccuracy (
                PlaylistItemAccuracyId INTEGER NOT NULL PRIMARY KEY,
                Description TEXT NOT NULL UNIQUE
            );

        -- Tag definition
        CREATE TABLE
            Tag (
                TagId INTEGER NOT NULL PRIMARY KEY,
                Type INTEGER NOT NULL,
                Name TEXT NOT NULL,
                UNIQUE (Type, Name),
                CHECK (length (Name) > 0),
                CHECK (Type IN (0, 1, 2))
            );

        CREATE INDEX IX_Tag_Name_Type_TagId ON Tag (Name, Type, TagId);

        -- Bookmark definition
        CREATE TABLE
            Bookmark (
                BookmarkId INTEGER NOT NULL PRIMARY KEY,
                LocationId INTEGER NOT NULL,
                PublicationLocationId INTEGER NOT NULL,
                Slot INTEGER NOT NULL,
                Title TEXT NOT NULL,
                Snippet TEXT,
                BlockType INTEGER NOT NULL DEFAULT 0,
                BlockIdentifier INTEGER,
                FOREIGN KEY (LocationId) REFERENCES Location (LocationId),
                FOREIGN KEY (PublicationLocationId) REFERENCES Location (LocationId),
                CONSTRAINT PublicationLocationId_Slot UNIQUE (PublicationLocationId, Slot),
                CHECK (
                    (
                        BlockType = 0
                        AND BlockIdentifier IS NULL
                    )
                    OR (
                        (BlockType BETWEEN 1 AND 2)
                        AND BlockIdentifier IS NOT NULL
                    )
                )
            );

        -- InputField definition
        CREATE TABLE
            InputField (
                LocationId INTEGER NOT NULL,
                TextTag TEXT NOT NULL,
                Value TEXT NOT NULL,
                FOREIGN KEY (LocationId) REFERENCES Location (LocationId),
                CONSTRAINT LocationId_TextTag PRIMARY KEY (LocationId, TextTag)
            );

        -- PlaylistItem definition
        CREATE TABLE
            PlaylistItem (
                PlaylistItemId INTEGER NOT NULL PRIMARY KEY,
                Label TEXT NOT NULL,
                StartTrimOffsetTicks INTEGER,
                EndTrimOffsetTicks INTEGER,
                Accuracy INTEGER NOT NULL,
                EndAction INTEGER NOT NULL,
                ThumbnailFilePath TEXT,
                FOREIGN KEY (Accuracy) REFERENCES PlaylistItemAccuracy (PlaylistItemAccuracyId),
                FOREIGN KEY (ThumbnailFilePath) REFERENCES IndependentMedia (FilePath),
                CHECK (length (Label) > 0),
                CHECK (EndAction IN (0, 1, 2, 3))
            );

        CREATE INDEX IX_PlaylistItem_ThumbnailFilePath ON PlaylistItem (ThumbnailFilePath);

        -- PlaylistItemIndependentMediaMap definition
        CREATE TABLE
            PlaylistItemIndependentMediaMap (
                PlaylistItemId INTEGER NOT NULL,
                IndependentMediaId INTEGER NOT NULL,
                DurationTicks INTEGER NOT NULL,
                PRIMARY KEY (PlaylistItemId, IndependentMediaId),
                FOREIGN KEY (PlaylistItemId) REFERENCES PlaylistItem (PlaylistItemId),
                FOREIGN KEY (IndependentMediaId) REFERENCES IndependentMedia (IndependentMediaId)
            ) WITHOUT ROWID;

        CREATE INDEX IX_PlaylistItemIndependentMediaMap_IndependentMediaId ON PlaylistItemIndependentMediaMap (IndependentMediaId);

        -- PlaylistItemLocationMap definition
        CREATE TABLE
            PlaylistItemLocationMap (
                PlaylistItemId INTEGER NOT NULL,
                LocationId INTEGER NOT NULL,
                MajorMultimediaType INTEGER NOT NULL,
                BaseDurationTicks INTEGER,
                PRIMARY KEY (PlaylistItemId, LocationId),
                FOREIGN KEY (PlaylistItemId) REFERENCES PlaylistItem (PlaylistItemId),
                FOREIGN KEY (LocationId) REFERENCES Location (LocationId)
            ) WITHOUT ROWID;

        CREATE INDEX IX_PlaylistItemLocationMap_LocationId ON PlaylistItemLocationMap (LocationId);

        -- PlaylistItemMarker definition
        CREATE TABLE
            PlaylistItemMarker (
                PlaylistItemMarkerId INTEGER NOT NULL PRIMARY KEY,
                PlaylistItemId INTEGER NOT NULL,
                Label TEXT NOT NULL,
                StartTimeTicks INTEGER NOT NULL,
                DurationTicks INTEGER NOT NULL,
                EndTransitionDurationTicks INTEGER NOT NULL,
                UNIQUE (PlaylistItemId, StartTimeTicks),
                FOREIGN KEY (PlaylistItemId) REFERENCES PlaylistItem (PlaylistItemId)
            );

        -- PlaylistItemMarkerBibleVerseMap definition
        CREATE TABLE
            PlaylistItemMarkerBibleVerseMap (
                PlaylistItemMarkerId INTEGER NOT NULL,
                VerseId INTEGER NOT NULL,
                PRIMARY KEY (PlaylistItemMarkerId, VerseId),
                FOREIGN KEY (PlaylistItemMarkerId) REFERENCES PlaylistItemMarker (PlaylistItemMarkerId)
            ) WITHOUT ROWID;

        -- PlaylistItemMarkerParagraphMap definition
        CREATE TABLE
            PlaylistItemMarkerParagraphMap (
                PlaylistItemMarkerId INTEGER NOT NULL,
                MepsDocumentId INTEGER NOT NULL,
                ParagraphIndex INTEGER NOT NULL,
                MarkerIndexWithinParagraph INTEGER NOT NULL,
                PRIMARY KEY (
                    PlaylistItemMarkerId,
                    MepsDocumentId,
                    ParagraphIndex,
                    MarkerIndexWithinParagraph
                ),
                FOREIGN KEY (PlaylistItemMarkerId) REFERENCES PlaylistItemMarker (PlaylistItemMarkerId)
            ) WITHOUT ROWID;

        -- UserMark definition
        CREATE TABLE
            UserMark (
                UserMarkId INTEGER NOT NULL PRIMARY KEY,
                ColorIndex INTEGER NOT NULL,
                LocationId INTEGER NOT NULL,
                StyleIndex INTEGER NOT NULL,
                UserMarkGuid TEXT NOT NULL UNIQUE,
                Version INTEGER NOT NULL,
                FOREIGN KEY (LocationId) REFERENCES Location (LocationId)
            );

        CREATE INDEX IX_UserMark_LocationId ON UserMark (LocationId);

        -- BlockRange definition
        CREATE TABLE
            BlockRange (
                BlockRangeId INTEGER NOT NULL PRIMARY KEY,
                BlockType INTEGER NOT NULL,
                Identifier INTEGER NOT NULL,
                StartToken INTEGER,
                EndToken INTEGER,
                UserMarkId INTEGER NOT NULL,
                CHECK (BlockType BETWEEN 1 AND 2),
                FOREIGN KEY (UserMarkId) REFERENCES UserMark (UserMarkId)
            );

        CREATE INDEX IX_BlockRange_UserMarkId ON BlockRange (UserMarkId);

        -- Note definition
        CREATE TABLE
            Note (
                NoteId INTEGER NOT NULL PRIMARY KEY,
                Guid TEXT NOT NULL UNIQUE,
                UserMarkId INTEGER,
                LocationId INTEGER,
                Title TEXT,
                Content TEXT,
                LastModified TEXT NOT NULL DEFAULT (strftime ('%Y-%m-%dT%H:%M:%SZ', 'now')),
                Created TEXT NOT NULL DEFAULT (strftime ('%Y-%m-%dT%H:%M:%SZ', 'now')),
                BlockType INTEGER NOT NULL DEFAULT 0,
                BlockIdentifier INTEGER,
                CHECK (
                    (
                        BlockType = 0
                        AND BlockIdentifier IS NULL
                    )
                    OR (
                        (BlockType BETWEEN 1 AND 2)
                        AND BlockIdentifier IS NOT NULL
                    )
                ),
                FOREIGN KEY (UserMarkId) REFERENCES UserMark (UserMarkId),
                FOREIGN KEY (LocationId) REFERENCES Location (LocationId)
            );

        CREATE INDEX IX_Note_LastModified_LocationId ON Note (LastModified, LocationId);

        CREATE INDEX IX_Note_LocationId_BlockIdentifier ON Note (LocationId, BlockIdentifier);

        -- TagMap definition
        CREATE TABLE
            TagMap (
                TagMapId INTEGER NOT NULL PRIMARY KEY,
                PlaylistItemId INTEGER,
                LocationId INTEGER,
                NoteId INTEGER,
                TagId INTEGER NOT NULL,
                Position INTEGER NOT NULL,
                FOREIGN KEY (TagId) REFERENCES Tag (TagId),
                FOREIGN KEY (PlaylistItemId) REFERENCES PlaylistItem (PlaylistItemId),
                FOREIGN KEY (LocationId) REFERENCES Location (LocationId),
                FOREIGN KEY (NoteId) REFERENCES Note (NoteId),
                CONSTRAINT TagId_Position UNIQUE (TagId, Position),
                CONSTRAINT TagId_NoteId UNIQUE (TagId, NoteId),
                CONSTRAINT TagId_LocationId UNIQUE (TagId, LocationId),
                CONSTRAINT TagId_PlaylistItemId UNIQUE (TagId, PlaylistItemId),
                CHECK (
                    (
                        NoteId IS NULL
                        AND LocationId IS NULL
                        AND PlaylistItemId IS NOT NULL
                    )
                    OR (
                        LocationId IS NULL
                        AND PlaylistItemId IS NULL
                        AND NoteId IS NOT NULL
                    )
                    OR (
                        PlaylistItemId IS NULL
                        AND NoteId IS NULL
                        AND LocationId IS NOT NULL
                    )
                )
            );

        CREATE INDEX IX_TagMap_TagId ON TagMap (TagId);
        CREATE INDEX IX_TagMap_PlaylistItemId_TagId_Position ON TagMap (PlaylistItemId, TagId, Position);
        CREATE INDEX IX_TagMap_LocationId_TagId_Position ON TagMap (LocationId, TagId, Position);
        CREATE INDEX IX_TagMap_NoteId_TagId_Position ON TagMap (NoteId, TagId, Position);
    ''')

    # Create trigers
    cur.executescript('''CREATE TRIGGER TR_Update_LastModified_Delete_Tag DELETE ON Tag BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Insert_Tag INSERT ON Tag BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Update_Tag
        UPDATE ON Tag BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Delete_TagMap DELETE ON TagMap BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Insert_TagMap INSERT ON TagMap BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Update_TagMap
        UPDATE ON TagMap BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Delete_Note DELETE ON Note BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Insert_Note INSERT ON Note BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Update_Note
        UPDATE ON Note BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Delete_Bookmark DELETE ON Bookmark BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Insert_Bookmark INSERT ON Bookmark BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Update_Bookmark
        UPDATE ON Bookmark BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Delete_UserMark DELETE ON UserMark BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Insert_UserMark INSERT ON UserMark BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Update_UserMark
        UPDATE ON UserMark BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Delete_BlockRange DELETE ON BlockRange BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Insert_BlockRange INSERT ON BlockRange BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Update_BlockRange
        UPDATE ON BlockRange BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Delete_InputField DELETE ON InputField BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Insert_InputField INSERT ON InputField BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Update_InputField
        UPDATE ON InputField BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Delete_IndependentMedia DELETE ON IndependentMedia BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Insert_IndependentMedia INSERT ON IndependentMedia BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Update_IndependentMedia
        UPDATE ON IndependentMedia BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Delete_PlaylistItem DELETE ON PlaylistItem BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Insert_PlaylistItem INSERT ON PlaylistItem BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Update_LastModified_Update_PlaylistItem
        UPDATE ON PlaylistItem BEGIN
        UPDATE LastModified
        SET
            LastModified = strftime ('%Y-%m-%dT%H:%M:%SZ', 'now');

        END;

        CREATE TRIGGER TR_Raise_Error_Before_Delete_LastModified BEFORE DELETE ON LastModified BEGIN
        SELECT
            RAISE (FAIL, 'DELETE FROM LastModified not allowed');

        END;

        CREATE TRIGGER TR_Raise_Error_Before_Insert_LastModified BEFORE INSERT ON LastModified BEGIN
        SELECT
            RAISE (FAIL, 'INSERT INTO LastModified not allowed');

        END;
    ''')

    con.commit()
    con.close()

def copyDatabase():
    shutil.copy("./extra/userData.db",
            "./data-3/userData.db")

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

    # data = cur1.execute("SELECT * FROM LastModified").fetchall()
    # cur3.executemany("INSERT INTO LastModified VALUES(?)", data)

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

    # close all
    con1.close()
    con3.close()


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
        "PlaylistItemAccuracy": {},
        "PlaylistItem": {},
        "IndependentMedia": {},
        "TagMap": {},
        "PlaylistItemMarker": {},
    }

    # Location
    data = cur2.execute("SELECT * FROM Location").fetchall()
    nextId = cur3.execute("SELECT MAX(LocationId) FROM Location").fetchone()[0]

    for r in data:
        nextId += 1
        existing_data = cur3.execute("SELECT * FROM Location WHERE BookNumber = ? AND ChapterNumber = ? AND KeySymbol = ? AND MepsLanguage = ? AND Type = ?", (r[1], r[2], r[6], r[7], r[8])).fetchone()
        if existing_data is None:
            mapId['Location'][r[0]] = nextId
            cur3.execute("INSERT INTO Location VALUES(?,?,?,?,?,?,?,?,?,?)", (nextId, r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]))
        else:
            print(">> ⚠️ Mapenado IDs para a tabela Location")
            mapId['Location'][r[0]] = existing_data[0]

    # Tag
    # todo: renomear as playlists com nome repetido
    data = cur2.execute("SELECT * FROM Tag").fetchall()
    nextId = cur3.execute("SELECT MAX(TagId) FROM Tag").fetchone()[0]
    for r in data:
        nextId += 1
        mapId['Tag'][r[0]] = nextId
        cur3.execute("INSERT INTO Tag VALUES(?,?,?)", (nextId, r[1], r[2]))
    
    # Bookmark
    data = cur2.execute("SELECT * FROM Bookmark").fetchall()
    nextId = cur3.execute("SELECT MAX(BookmarkId) FROM Bookmark").fetchone()[0]
    for r in data:
        nextId += 1
        mapId['Bookmark'][r[0]] = nextId
        cur3.execute("INSERT INTO Bookmark VALUES(?,?,?,?,?,?,?,?)", (nextId, mapId["Location"][r[1]], r[2], r[3], r[4], r[5], r[6], r[7]))
    
    # InputField
    data = cur2.execute("SELECT * FROM InputField").fetchall()
    cur3.executemany("INSERT INTO InputField VALUES(?,?,?)", data)

    # UserMark
    data = cur2.execute("SELECT * FROM UserMark").fetchall()
    nextId = cur3.execute("SELECT MAX(UserMarkId) FROM UserMark").fetchone()[0]
    for r in data:
        nextId += 1
        mapId['UserMark'][r[0]] = nextId
        cur3.execute("INSERT INTO UserMark VALUES(?,?,?,?,?)", (nextId, mapId["Location"][r[1]], r[2], r[3], r[4], r[5]))
   
    # BlockRange
    data = cur2.execute("SELECT * FROM BlockRange").fetchall()
    nextId = cur3.execute("SELECT MAX(BlockRangeId) FROM BlockRange").fetchone()[0]
    for r in data:
        nextId += 1
        mapId['BlockRange'][r[0]] = nextId
        cur3.execute("INSERT INTO BlockRange VALUES(?,?,?,?,?)", (nextId, r[1], r[2], r[3], mapId["UserMark"][r[4]]))
    
    # Note
    data = cur2.execute("SELECT * FROM Note").fetchall()
    nextId = cur3.execute("SELECT MAX(NoteId) FROM Note").fetchone()[0]
    for r in data:
        nextId += 1
        mapId['Note'][r[0]] = nextId
        cur3.execute("INSERT INTO Note VALUES(?,?,?,?,?,?,?,?,?,?)", (nextId, mapId["UserMark"][r[1]], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]))

    # PlaylistItemAccuracy
    data = cur2.execute("SELECT * FROM PlaylistItemAccuracy").fetchall()
    nextId = cur3.execute("SELECT MAX(PlaylistItemAccuracyId) FROM PlaylistItemAccuracy").fetchone()[0]

    for r in data:
        nextId += 1
        existing_data = cur3.execute("SELECT * FROM PlaylistItemAccuracy WHERE Description = ?", (r[1],)).fetchone()
        if existing_data is None:
            cur3.execute("INSERT INTO PlaylistItemAccuracy VALUES(?,?)", (nextId, r[1]))
            mapId['PlaylistItemAccuracy'][r[0]] = nextId
        else:
            print(">> ⚠️ Mapeando IDs para a tabela PlaylistItemAccuracy")
            mapId['PlaylistItemAccuracy'][r[0]] = existing_data[0]


    # PlaylistItem
    data = cur2.execute("SELECT * FROM PlaylistItem").fetchall()
    nextId = cur3.execute("SELECT MAX(PlaylistItemId) FROM PlaylistItem").fetchone()[0]
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
    nextId = cur3.execute("SELECT MAX(IndependentMediaId) FROM IndependentMedia").fetchone()[0]
    for r in data:
        existing_data = cur3.execute("SELECT IndependentMediaId FROM IndependentMedia WHERE FilePath = ?", (r[2],)).fetchone()
        if existing_data:
            existing_id = existing_data[0]
            mapId['IndependentMedia'][r[0]] = existing_id
        else:
            nextId += 1
            cur3.execute("INSERT INTO IndependentMedia VALUES(?,?,?,?,?)", (nextId, r[1], r[2], r[3], r[4]))
            mapId['IndependentMedia'][r[0]] = nextId
    
    # TagMap
    data = cur2.execute("SELECT * FROM TagMap").fetchall()
    nextId = cur3.execute("SELECT MAX(TagMapId) FROM TagMap").fetchone()[0]
    for r in data:
        nextId += 1
        mapId['TagMap'][r[0]] = nextId
        cur3.execute("INSERT INTO TagMap VALUES(?,?,?,?,?,?)", (nextId, mapId["PlaylistItem"][r[1]], mapId["Location"].get(r[2]), mapId["Note"].get(r[3]), mapId["Tag"][r[4]], r[5]))
    
    # PlaylistItemIndependentMediaMap
    data = cur2.execute("SELECT * FROM PlaylistItemIndependentMediaMap").fetchall()
    for r in data:
        nextId += 1
        cur3.execute("INSERT INTO PlaylistItemIndependentMediaMap VALUES(?,?,?)", (mapId["PlaylistItem"][r[0]], mapId["IndependentMedia"][r[1]], r[2]))

    # PlaylistItemMarker
    data = cur2.execute("SELECT * FROM PlaylistItemMarker").fetchall()
    nextId = cur3.execute("SELECT MAX(PlaylistItemMarkerId) FROM PlaylistItemMarker").fetchone()[0]
    for r in data:
        nextId += 1
        mapId['PlaylistItemMarker'][r[0]] = nextId
        cur3.execute("INSERT INTO PlaylistItemMarker VALUES(?,?,?,?,?,?)", (nextId, mapId["PlaylistItem"][r[1]], r[2], r[3], r[4], r[5]))
   
    # PlaylistItemMarkerParagraphMap
    data = cur2.execute("SELECT * FROM PlaylistItemMarkerParagraphMap").fetchall()
    for r in data:
        cur3.execute("INSERT INTO PlaylistItemMarkerParagraphMap VALUES(?,?,?,?)", (mapId["PlaylistItemMarker"][r[0]], r[1], r[2], r[3]))
   
    # PlaylistItemMarkerBibleVerseMap
    data = cur2.execute("SELECT * FROM PlaylistItemMarkerBibleVerseMap").fetchall()
    for r in data:
        cur3.execute("INSERT INTO PlaylistItemMarkerBibleVerseMap VALUES(?,?)", (mapId["PlaylistItemMarker"][r[0]], r[1]))

    # commit all
    con2.commit()
    con3.commit()

    # close all
    con2.close()
    con3.close()


def createNewBkpFIle():
    zf = zipfile.ZipFile( FINALFILENAME, "w", compression=zipfile.ZIP_DEFLATED)
    for file in os.listdir('./data-3'):
        zf.write(f"./data-3/{file}", arcname=file)

    zf.close()


if __name__ == "__main__":
    print("<<< Iniciando...>>>")
    print(">> Limpando pastas...")
    clearDir("./data-1")
    clearDir("./data-2")
    clearDir("./data-3")

    print(">> Descopactando bkp 1 e compiando seus arquivos para data-1")
    readData1()

    print(">> Descopactando bkp 2 e compiando seus arquivos para data-2")
    readData2()

    print(">> Copiando todos os arquivos de /data-1 e /data-2 para /data-3")
    copyAllFilesToData3()

    print(">> Criando nova base de dados")
    createNewDataBase()

    # print(">> Copiando nova base de dados")
    # copyDatabase()

    print(">> Copiando dados da base-1 para a nova base")
    getDataFromDb1()

    print(">> Copiando dados da base-2 para a nova base")
    getDataFromDb2()

    print(">> Copiando default_thumbnail.png para /data-3")
    copyThumbNail()

    # print(">> Gerando nova hash")
    # hashCalc()

    print(">> Criando e copiando manifest.json para /data-3")
    manifestGenerator()

    print(">> Criando novo .jwlibrary")
    createNewBkpFIle()

    print(">> Limpando pastas...")
    clearDir("./data-1")
    clearDir("./data-2")
    clearDir("./data-3")

    print("\n<<< FIM >>>")