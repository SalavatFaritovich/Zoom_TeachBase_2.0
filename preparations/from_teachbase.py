import time
import requests
import sys
import os
from dotenv import load_dotenv
import pandas as pd

"""
    Выгружает список всех курсов из teachbase: teachbase_id, name 
"""


def get_teachbase_cources():
    load_dotenv()
    teachbase_id = os.getenv('TEACHBASE_CLIENT_ID')
    teachbase_secret = os.getenv('TEACHBASE_CLIENT_SECRET')

    # Получаем токен в teachbase

    token_data = {
        "client_secret": teachbase_secret,
        "grant_type": "client_credentials",
        "client_id": teachbase_id,
        "scope": "public"
    }

    re = requests.post(url="https://go.teachbase.ru/oauth/token", data=token_data)
    access_token = re.json()['access_token']

    if re.status_code != 200:
        print("Не получили токен teachbase")
        print(re.status_code)
        print(re.json())
        sys.exit(1)

    # Вытягиваем id курсов из teachbase
    header = {
        "Authorization": f"Bearer {access_token}"
    }

    d = {}
    ind = 0
    page = 0

    response_is_empty = False
    while not response_is_empty:
        courses_list_params = {
            "page": page,
            "per_page": 50,
        }

        req_courses_list = requests.get(
            url=f"https://go.teachbase.ru/endpoint/v1/courses",
            headers=header,
            params=courses_list_params
        )

        for g in req_courses_list.json():
            ind = ind + 1
            d.update(
                {ind: dict(teachbase_id=g['id'], teachbase_name=g['name'])}
            )

        page += 1
        time.sleep(0.2)
        response_is_empty = True if req_courses_list.json() == [] else False

    teachbase_ids = pd.DataFrame.from_dict(d).transpose()   # .to_excel("data/teachbase_courses_ids.xlsx")
    print("Got ids from teachbase!")
    return teachbase_ids
