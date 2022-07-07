from ffmpeg import probe
from PIL import Image
import pandas as pd
from datetime import datetime
import os
from pathlib import Path
from easygui import diropenbox
from dateutil.parser import parse
from tqdm import tqdm

img_formats = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng']
vid_formats = ['mov', 'avi', 'mp4', 'mpg', 'mpeg', 'm4v', 'wmv', 'mkv']

dir_path = diropenbox()
if not dir_path:
    exit()

output_name = Path(dir_path).stem

def read_time(dir_path):

    data = {
        "file_path": [],
        "file_name": [],
        "datetime": [],
    }

    files = os.listdir(dir_path)
    for file in tqdm(files):
        file_type = file.split(".")[-1].lower()
        file_path = os.path.join(dir_path, file)

        if file_type in img_formats:
            c_dt = datetime.strptime(Image.open(file_path)._getexif()[36867], '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
        elif file_type in vid_formats:
            c_dt = parse(probe(file_path)["streams"][0]["tags"]["creation_time"]).strftime('%Y-%m-%d %H:%M:%S')
            pass
        else:
            continue
        data['file_path'].append(file_path)
        data['file_name'].append(file)
        data['datetime'].append(c_dt)
    return pd.DataFrame(data)

def hr_freq(data):
    data["datetime"] = pd.to_datetime(data["datetime"]).apply(lambda x: x.strftime('%Y-%m-%d %H%M'))
    data["count"] = 1
    data["date"] = pd.to_datetime(data["datetime"]).apply(lambda x: x.strftime('%Y-%m-%d'))
    data["time"] = pd.to_datetime(data["datetime"]).apply(lambda x: x.strftime('%H%M'))
    data["hour"] = pd.to_datetime(data["datetime"]).apply(lambda x: x.strftime('%H'))
    data = data[["date", "hour", "time", "count"]].drop_duplicates()
    data = data.groupby(["date", "hour"]).sum().reset_index()[["date", "hour", "count"]]
    data["parent_dir"] = output_name
    return data

def save_csv(dir_path):
    directory = Path("./results")
    directory.mkdir(parents=True, exist_ok=True)
    dirs = os.listdir(directory)
    time_now = datetime.now().strftime("%y-%m-%d_%H%M")
    index = 0
    dir_name = "exp"
    while True:
        if dir_name + str(index) not in dirs:
            os.mkdir("./results/" + dir_name + str(index))
            break
        else:
            index+=1

    data = read_time(dir_path)
    data.to_csv("./results/" + dir_name + str(index) + "/" + time_now + "_%s_precent.csv" % output_name, index=False)
    data = hr_freq(data)
    data.to_csv("./results/" + dir_name + str(index) + "/" + time_now + "_%s_hourcount.csv" % output_name, index=False)
    print("資料儲存在 ./results/%s" % dir_name + str(index))

if __name__ == "__main__":

    try:
        save_csv(dir_path)
    except Exception as e:
        print(e)
        input()
