# moodule imports
import maya.cmds as mc
import os
import time
import requests
from bs4 import BeautifulSoup
import zipfile
import StringIO

# Constants and variables
start_time = time.time()
path = "C:\\Users\\enriq\\Documents"
maya_path = os.path.join(path, "maya")
cmds_path = os.path.join(maya_path, "cmds")
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

####################
# Download MAYA HELP

DOWNLOAD_LINK = "http://download.autodesk.com/us/support/files/maya_2018.4_update/MayaHelp2018_4_Update_enu.zip"
DOWNLOAD_PATH = 'C:\\Users\\enriq\\Downloads'
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
if "maya" not in os.listdir(path):
    os.makedirs(maya_path)
    with open(os.path.join(maya_path, "__init__.py"), "wb") as f:
        f.close()
if "cmds" not in os.listdir(maya_path):
    os.makedirs(cmds_path)

with open(os.path.join(cmds_path, "__init__.py"), 'w+') as f:
    keys = mc.__dict__.keys()
    max_methods = str(len(keys))
    for i, method in enumerate(keys):
        print(method + " ---- " + str(i) + " out of " + max_methods)
        if '__' in method:
            print("Skipped")
            continue
        if i == 50:
            raise Exception
        # DEPRECATED FOR WEBSITES
        # page = requests.get(
        #     "http://help.autodesk.com/cloudhelp/2018/ENU/Maya-Tech-Docs/CommandsPython/{}.html".format(method))
        html_path = "{}.html".format(os.path.join(DOWNLOAD_PATH, os.path.splitext(FILE_NAME)[0], "CommandsPython", method))
        variables = str()
        try:
            with open(html_path, "r") as page:
                # Deprecated for websites
                # soup = BeautifulSoup(page.text, 'html.parser')
                soup = BeautifulSoup(page.read(), 'html.parser')
                filtered = soup.find_all(attrs={'bgcolor': '#EEEEEE'})
                get = soup.find_all(attrs={'colspan':'3'})
                print method
                all_help =list()
                for g in get:
                    for line in g.find_all('tr'):
                        if line:
                            print str(line)
                            # all_help.append(str(line.find_all('td')[1]).replace('<td>', "").replace('</td>', '').replace("\n"," "))
                            print '---------------'
                j = 0
                for part in filtered:
                    try:
                        flag, value = part.find_all('code')
                        flag = flag.text
                        value = value.text
                        long_name = flag.split('(')[0]
                        if '[' in value:
                            variables = variables + "{} = list(),".format(long_name)
                        else:
                            variables = variables + "{} = {}".format(long_name, TYPE_MAPPER[value])
                        # print flag, all_help[j]
                        j += 1
                    except ValueError:
                        print('NO ATTRIBUTE on method: ' + method)

        except IOError:
            print(method, " Not in PYTHON COMMANDS help")
        variables = "def {}(".format(method) + variables + " *args, **keywords): pass\n"
        f.write(variables)
    f.close()
print()
print()
print()
print("It takes {} seconds".format(time.time() - start_time))
