from PIL import Image
import pytesseract
import glob
import os

BASE_DIR = "/home/greg/repos/commute_analysis/"

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"


def timer_image_to_string(path):
    im = Image.open(path)
    im = im.crop((450, 1100, 1000, 1400))
    string = pytesseract.image_to_string(im)
    string = string.replace(" ", "")
    return string


image_paths = glob.glob(os.path.join(BASE_DIR, "data/raw/images/test/*"))

for image_path in image_paths:
    print(image_path, timer_image_to_string(image_path))
