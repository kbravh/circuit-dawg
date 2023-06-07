import zipfile

def words100k():
    zip_name = "tests/words100k.zip"
    zf = zipfile.ZipFile(zip_name)
    txt = zf.open(zf.namelist()[0]).read().decode('utf8')
    return txt.splitlines()
