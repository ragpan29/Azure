import os
import sys
import pytest
sys.path.append(os.getcwd())
from app.util import *
from app import appvar

class fakeRequest():
    def __init__(self,filedict):
        self.files = filedict

class fakeFile():
    def __init__(self, fname):
        self.filename = fname

def test_save_image_fails_if_no_file():
    # Setup a fake Request
    r = fakeRequest(filedict={"test":None})

    with pytest.raises(FileNotFoundError) as e_info:
        save_image(r, "photofile")

def test_save_image_fails_if_no_filename():
    # Setup a fake Request and fake File
    f = fakeFile("")
    r = fakeRequest(filedict={"photofile":f})

    with pytest.raises(FileNotFoundError) as e_info:
        save_image(r, "photofile")
    
def test_save_image_fails_no_extension():
    # Setup a fake Request and fake File
    f = fakeFile("anEmployeePhoto.bmp")
    r = fakeRequest(filedict={"photofile":f})

    with pytest.raises(ValueError) as e_info:
        save_image(r, "photofile")

def test_generate_img_url():
    acct_name = appvar.config["BLOB_ACCT"]
    blob_name = "example.png"
    sas = "test=123&test2=456"
    expected = "https://{}.blob.core.windows.net/images/{}?{}".format(acct_name, blob_name, sas)

    results = generate_img_url(blob_name, sas)

    assert results == expected