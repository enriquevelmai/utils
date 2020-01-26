# CREATES THE AUTOCOMPLETE FOR MAYA CMDS module, it's need to have the maya.cmds devkit autocomplete in order to get a
# Full list with the commands and do not have some of them lost
# module imports
import maya.cmds as mc
import os
import time

import requests
from bs4 import BeautifulSoup
import zipfile
import StringIO

# available maya mapping type
TYPE_MAPPER = {
    "boolean": "bool()",
    "string": "str()",
    "script": "str()",
    "name": "str()",
    "int": "int()",
    "int64": "int()",
    "uint": "int()",
    "linear": "float()",
    "float": "float()",
    "angle": "float()",
    # '[float, float, float]': "list()",
    # '[linear, linear, linear]': "list()",
    # "[time, time, float]": "list()",
    # "[float, float, float, float]": "list()",
    # "[angle, angle, angle]": "list()",
    # "[string, string]": "list()",
    # "[string, string, int, string]": "list()",
    # "[string, boolean]": "list()",
    # "[string, string, int]": "list()",
    # "[string, string, int, int]": "list()",
    # "[float, float]": "list()",
    # "[uint, uint]": "list()",
    # "[int, string]": "list()",
    "floatrange": "tuple()",  # could be an integer as well
    "timerange": "tuple()",  # could be an integer as well
    "time": "int()"  # could be an string as well
}

# globals
DOWNLOAD_LINK = "http://download.autodesk.com/us/support/maya_2019.2/maya-2019.2-user-guide_enu_offline.zip"
DOWNLOAD_DEVKIT_LINK = "https://autodesk-adn-transfer.s3-us-west-2.amazonaws.com/ADN+Extranet/M%26E/Maya/devkit+2020/Autodesk_Maya_2020_DEVKIT_Windows.zip"
DOWNLOAD_PATH = os.path.join(os.environ["USERPROFILE"], "Downloads")
COMPLETION_CREATION_PATH = os.path.join(os.environ["USERPROFILE"], "Documents")


def run():
    # Constants and variables
    start_time = time.time()
    maya_path = os.path.join(COMPLETION_CREATION_PATH, "maya")
    cmds_path = os.path.join(maya_path, "cmds")

    ####################
    # Download MAYA HELP
    # is fast to download it and query the pages than accessing to the online files
    FILE_NAME = os.path.split(DOWNLOAD_LINK)[1]
    if os.path.splitext(FILE_NAME)[0] not in os.listdir(DOWNLOAD_PATH):
        r = requests.get(DOWNLOAD_LINK, stream=True)
        print("DOWNLOADED: ", DOWNLOAD_LINK)
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        print ("PREPARED FOR UNZIP")
        target_dir = os.path.join(DOWNLOAD_PATH, os.path.splitext(FILE_NAME)[0])
        os.makedirs(target_dir)
        z.extractall(target_dir)
        print ('FILE: {} unziped'.format(FILE_NAME))

    else:
        print("File: {} already exists".format(os.path.splitext(FILE_NAME)[0]))

    #######################################################
    #######################################################
    # create analogous folders for saving the competition
    if "maya" not in os.listdir(COMPLETION_CREATION_PATH):
        os.makedirs(maya_path)
        with open(os.path.join(maya_path, "__init__.py"), "wb") as f:
            f.close()
    if "cmds" not in os.listdir(maya_path):
        os.makedirs(cmds_path)

    with open(os.path.join(cmds_path, "__init__.py"), 'w+') as f:
        keys = mc.__dict__.keys()
        print("Create data structure")
        for i, method in enumerate(keys):
            if '__' in method:
                print("Skipped")
                continue

            html_path = "{}.html".format(
                os.path.join(DOWNLOAD_PATH, os.path.splitext(FILE_NAME)[0], "CommandsPython", method))
            variables = str()
            try:
                with open(html_path, "r") as page:
                    soup = BeautifulSoup(page.read(), 'html.parser')
                    filtered = soup.find_all(attrs={'bgcolor': '#EEEEEE'})
                    for part in filtered:
                        try:
                            flag, value = part.find_all('code')
                            flag = flag.text
                            value = value.text
                            long_name = flag.split('(')[0]
                            if '[' in value:
                                variables = variables + "{} = list(),".format(long_name)
                            else:
                                variables = variables + "{} = {},".format(long_name, TYPE_MAPPER[value])
                        except ValueError:
                            print('NO ATTRIBUTE on method: ' + method)

            except IOError:
                print(method, " Not in PYTHON COMMANDS help")
            variables = "def {}(".format(method) + variables + " *args, **keywords): pass\n"
            f.write(variables)
        f.close()
    print("It takes {} seconds".format(time.time() - start_time))


if __name__ == "__main__":
    run()
