from PIL import Image
import pytesseract
import glob
import os
import csv
import datetime

BASE_DIR = "/home/greg/repos/commute_analysis/"

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"


def timer_image_to_string(path, crop):
    #  if crop == (200, 800, 900, 1200):
    #      import pdb; pdb.set_trace()
    im = Image.open(path)
    im = im.crop(crop)
    string = pytesseract.image_to_string(im)
    string = string.replace(" ", "")
    #  print(path, string)
    return string


def read_times_from_images():
    image_paths = glob.glob(os.path.join(BASE_DIR, "data/raw/images/*.jpg"))

    image_file_to_string = {}
    for image_path in image_paths:
        if "Clock" in image_path:
            timerstr = timer_image_to_string(image_path, (200, 800, 900, 1200))
        else:
            timerstr = timer_image_to_string(image_path, (450, 1100, 1000, 1400))
        image_file_to_string[os.path.basename(image_path)] = timerstr

    csv_file = os.path.join(BASE_DIR, "data", "raw", "drive_times.csv")
    with open(csv_file, "w") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "time"])
        writer.writeheader()
        writer.writerows(
            {"filename": fname, "time": timerstr}
            for fname, timerstr in image_file_to_string.items()
        )


def clean_time_csv():
    reader = csv.reader(open(os.path.join(BASE_DIR, "data/raw/drive_times.csv"), "r"))
    headers = next(reader)
    existing_ts = set()
    writer = csv.writer(open(os.path.join(BASE_DIR, "data/processed/drives.csv"), "w"))
    writer.writerow(["start_date_local", "elapsed_time", "moving_time"])
    for filename, timer in reader:
        try:
            # in filename, 11:26 gets the timestamp
            screenshot_time = os.path.basename(filename)[11:26]
            ride_end = datetime.datetime.strptime(screenshot_time, "%Y%m%d-%H%M%S")
            minutes, seconds = timer.split(":")
            elapsed_time = datetime.timedelta(minutes=float(minutes), seconds=float(seconds))
        except Exception as e:
            Image.open(os.path.join(BASE_DIR, "data", "raw", "images", filename)).show()
            getting_time = True
            while getting_time:
                try:
                    timer = input()
                    minutes, seconds = timer.split(":")
                    elapsed_time = datetime.timedelta(minutes=float(minutes), seconds=float(seconds))
                    getting_time = False
                except Exception:
                    pass
        finally:
            if elapsed_time != 0:
                ride_start = ride_end - elapsed_time
                print(ride_start, elapsed_time)
                writer.writerow([ride_start, elapsed_time, elapsed_time])


if __name__ == "__main__":
    #  read_times_from_images()
    clean_time_csv()
