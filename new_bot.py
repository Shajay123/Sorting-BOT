import tkinter.filedialog
from pyzbar.pyzbar import decode
from PIL import Image
import os
import cv2
import zxing
from multiprocessing.pool import ThreadPool as Pool
from threading import Thread
import time
from google.cloud import vision
import io
import re
import fuzzywuzzy
import pandas
import random
from fuzzywuzzy import process as fuzprocess
from tkinter import filedialog
from tkinter.messagebox import askyesno
from fuzzywuzzy import fuzz
import hashlib



def remove_after_hyphen(string):
    if string.count("-") == 5:
        name, uqid, category, count, total, repeat = string.rsplit('-', maxsplit=5)
        return name
    else:
        return string



def removethaagam(visionout):
    visionout = visionout.replace("www.THAAGAM.ORG", "")
    visionout = visionout.replace("thaagam.org/qr", "")
    visionout = visionout.replace("thaagam.org/qr/", "")
    visionout = visionout.replace("thaagam.org.qr", "")
    visionout = visionout.replace("@thaagamfoundation", "")
    visionout = visionout.replace("FOUNDATION", "")
    visionout = visionout.replace("THAAGAM", "")
    visionout = visionout.replace("thaagamfoundation", "")
    visionout = visionout.replace("THAAGAM", "")
    visionout = visionout.replace("THAAGAM.ORG", "")
    visionout = visionout.replace("www.THAAGAN.ORG", "")
    visionout = visionout.replace("HTHAAGAM", "")
    return visionout

def Rename(ipath, str_dir, name):
    import re
    name = re.sub(r'\W+', ' ', name)
    name = name.strip()
    xloop = 1
    new_folder = (str_dir + "/" + name)
    print("NEW folder DIR 233:", new_folder)
    if os.path.isfile(new_folder) == True:
        xlist = os.listdir(new_folder)  # dir is your directory path
        xloop = len(xlist) + 1

    if os.path.isfile(new_folder) == False:

        try:
            os.makedirs(new_folder)
            xlist = os.listdir(new_folder)  # dir is your directory path
            xloop = len(xlist) + 1
        except WindowsError as e:
            xlist = os.listdir(new_folder)  # dir is your directory path
            xloop = len(xlist) + 1

        except Exception as e:
            print(e)

    rename_text = (name + str(xloop) + ".jpg")
    renamed_image = (str_dir + "/" + name + "/" + rename_text)
    print(name)

    try:
        os.rename(ipath, renamed_image)
    except FileExistsError as e:
        try:
            random_number = random.randint(100, 9999)
            rename_text = (name + str(random_number) + ".jpg")
            renamed_image = (str_dir + "/" + name + "/" + rename_text)
            os.rename(ipath, renamed_image)
        except FileExistsError as e:
            random_number = random.randint(100, 9999)
            rename_text = (name + str(random_number) + ".jpg")
            renamed_image = (str_dir + "/" + name + "/" + rename_text)
            os.rename(ipath, renamed_image)


def occuncompress(name):
    name = str(name)

    bea = re.compile(re.escape("b'"))
    name = bea.sub("", name)

    hbdre = re.compile(re.escape("<HBD>"))
    name = hbdre.sub("Happy Birthday", name)

    haare = re.compile(re.escape("<HAA>"))
    name = haare.sub("Happy anniversary", name)

    irore = re.compile(re.escape("<IRO>"))
    name = irore.sub("in remembrance of", name)

    name_list.append(name)

    return name


def Vision_Raja(Pimg):
    try:
        with io.open(Pimg, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
        client = vision.ImageAnnotatorClient()
        response = client.text_detection(image=image)
        texts = response.text_annotations

        for text in texts:
            strtext = ''.join(map(str, text.description))
            goutput = strtext
            break
        goutput = goutput.replace("\n", " ")

        strtext = removethaagam(goutput)
        strtext = remove_after_hyphen(strtext)  # Call the remove_after_hyphen function
        result = fuzprocess.extractOne(strtext, name_list, scorer=fuzz.token_set_ratio)
        adict.update({Pimg: {"Method": "Google Vision", "Response": strtext, "Fuzzy": result}})
        result, fratio = result

        if fratio > 85:
            return result
        if fratio < 85:
            return None

    except Exception as e:
        print(e)

def delete_duplicate_images(folder_path):
    # Create a dictionary to store the hash values of the images
    hash_values = {}

    # Iterate through all the files in the folder
    for file_name in os.listdir(folder_path):
        # Ignore files that are not images
        if not file_name.endswith(".jpg") and not file_name.endswith(".png"):
            continue

        # Calculate the hash value of the image
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "rb") as f:
            hash_value = hashlib.sha256(f.read()).hexdigest()

        # If the hash value is already in the dictionary, delete the image
        if hash_value in hash_values:
            removelist.append(file_path)
        else:
            # Add the hash value to the dictionary
            hash_values[hash_value] = True


def qr3sort(imgpath):
    data = decode(Image.open(imgpath))
    global x
    x = x + 1
    if data == []:
        cimg = cv2.imread(os.path.join(imgpath))
        detector = cv2.QRCodeDetector()
        data, bbox, straight_qrcode = detector.detectAndDecode(cimg)
        if data == "":
            try:
                reader = zxing.BarCodeReader()
                barcode = reader.decode(imgpath)
                data = barcode.parsed
            except Exception as e:
                data = ""
            if data == "":
                data = Vision_Raja(imgpath)
                if data == None:
                    return ""
                else:
                    data = occuncompress(data)
                    data = remove_after_hyphen(data)  # Call the remove_after_hyphen function
                    return data
            else:
                adict.update({imgpath: {"Method": "Zxing", "Data": data}})
                data = occuncompress(data)
                data = remove_after_hyphen(data)  # Call the remove_after_hyphen function
                return data
        else:
            adict.update({imgpath: {"Method": "OpenCV", "Data": data}})
            data = occuncompress(data)
            data = remove_after_hyphen(data)  # Call the remove_after_hyphen function
            return data
    else:
        adict.update({imgpath: {"Method": "pyzbar", "Response": data[0].data.decode('utf-8')}})
        data = data[0].data.decode('utf-8')
        data = occuncompress(data)
        data = remove_after_hyphen(data)  # Call the remove_after_hyphen function
        return data


def data_val(data, img):
    global fa
    global sa
    total = len(img_list)

    if data == "":
        print("No QR code detected")
        fa = fa + 1
        print("Failed:", fa, "Success:", sa, "total:", total)
        adict[img].update({"Data": data, "Status": "Failed", })
        return False
    else:
        print("QR code detected")
        print(data)
        sa = sa + 1
        print("Failed:", fa, "Success:", sa, "total:", total)
        adict[img].update({"Data": data, "Status": "Success"})
        return True
    print("____________________________________________________________________")

def savedict():
    global adict
    df = pandas.DataFrame.from_dict(adict, orient='index')
    df.to_excel(fr"{img_dir}\Log_Data.xlsx")

def jointprocess(imgpath):
    data = qr3sort(imgpath)
    if data_val(data, imgpath) is True:
        Rename(imgpath, img_dir, data)

name_list = []
img_dir = filedialog.askdirectory(initialdir="/", title="Select A Folder")

excel = filedialog.askopenfilename(initialdir="/", title="Select A File", filetypes=(("Excel File", "*.xlsx"),
                                                                                     ("all files", "*.*")))
removelist = []
delete_duplicate_images(img_dir)
if removelist != []:
    if askyesno("Delete Duplicate Images", f"Do you want to delete {len(removelist)} duplicate images?") == True:
        for i in removelist:
            os.remove(i)

df = pandas.read_excel(excel)
for i in range(len(df)):
    ename = (df.loc[i, df.columns[0]])
    name_list.append(ename)

global fa
global sa
global x
fa = 0
sa = 0
x = 0
# import Thread

pool = Pool(60)

credential_path = r"auto-image-sending-5be9dadf7c1a.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

threads = []

start_time = time.time()
adict = {}
img_list = []

for img in os.listdir(img_dir):
    if img.endswith(".jpg") or img.endswith(".png"):
        img = os.path.join(img_dir, img)
        img_list.append(img)

for ii in range(len(img_list)):
    process = Thread(target=jointprocess, args=(img_list[ii],))
    process.start()
    threads.append(process)

for process in threads:
    process.join()

savedict()

print("TOTAL TIME TAKEN") 
print("--- %s seconds ---" % (time.time() - start_time))