import pandas as pd
from time import sleep
all_data = {"data":None}
print("you came to d_files")

def update_data():
    global iv
    df = pd.read_feather("./data/final.feather")
    all_data["data"] = df
    sleep(1.0/12)
