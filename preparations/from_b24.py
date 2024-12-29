import requests
import os
from dotenv import load_dotenv
import pandas as pd
import time


def get_teachbase_name(row):
    if "онл" in row["name"]:
        return row["name"][:-3] + "Вебинары"
    else:
        return row["name"] + " Вебинары"


def get_regular_name(row):
    if "онл" in row["name"]:
        return row["name"][:-4]
    else:
        return row["name"]


def get_bitrix_ids_and_names():
    load_dotenv()

    bitrix_url = os.getenv('BITRIX_WEBHOOK')

    header = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    params = {
        "entityTypeId": 132,
        }
    first_body = {
        "select": ["id", "title"],
        "filter": {"ufCrm5Season": 1330},   #2024/2025
        "start": 0
        }

    first_req = requests.post(url=bitrix_url+"crm.item.list", headers=header, params=params, json=first_body)

    pages = first_req.json()["total"] // 50 + 1    #кол-во батчей по 50

    batch_list = []
    for i in range(pages):
        time.sleep(0.2)
        body = {
            "select": ["id", "title"],
            "filter": {"ufCrm5Season": 1330},   #2024/2025
            "start": i * 50
        }

        r = requests.post(url=bitrix_url+"crm.item.list", headers=header, params=params, json=body)
        # print(f"page {i}, status = {r.status_code}")
        batch_list.append(pd.DataFrame.from_records(data=r.json()["result"]["items"]))

    df = pd.concat(batch_list)
    df.rename(columns={"id": "ID", "title": "name"}, inplace=True)
    df["teachbase_name"] = df.apply(get_teachbase_name, axis=1)
    df["name"] = df.apply(get_regular_name, axis=1)

    print("Got ids from bitrix!")
    return df

    # df.to_csv(path_or_buf='from_b24.csv', sep=";")
