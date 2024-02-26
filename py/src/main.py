import sqlite3
import zipfile

jwfile1 = "files/bkp1.jwlibrary"
jwfile2 = "files/bkp2.jwlibrary"

# descompactar bkp1
with zipfile.ZipFile(jwfile1, 'r') as zip_ref:
    files = zip_ref.namelist()
    zip_ref.extractall("./data-1")

    uploadedDb = "files/bkp1.jwlibrary".format(
        [zipname for zipname in files if zipname.endswith(".db")][0])

    print(uploadedDb)
