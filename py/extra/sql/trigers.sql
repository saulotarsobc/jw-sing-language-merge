CREATE TRIGGER TR_Update_LastModified_Delete_Tag DELETE ON Tag BEGIN
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