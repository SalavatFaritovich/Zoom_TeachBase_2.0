import os
import time
import requests
import base64
from urllib.parse import quote_plus
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta


class ZoomHandler:
    def __init__(self):
        load_dotenv()

        self.DATE = os.getenv('DATE')

        self.ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
        self.CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
        self.CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')

        self.base_url = "https://api.zoom.us/v2/"
        self.redirect_uri = "https://mayak.study/"

        # получаем токен
        credentials = self.CLIENT_ID + ":" + self.CLIENT_SECRET
        authorization = "Basic " + base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        token_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": authorization,
        }

        token_body = {
            "grant_type": "account_credentials",
            "account_id": self.ACCOUNT_ID
        }

        re = requests.post(url="https://zoom.us/oauth/token", headers=token_header, data=token_body)
        self.access_token = re.json()['access_token']

        print(f"Got access token to zoom!")

        self.header = {
            "Authorization": f"Bearer {self.access_token}"
        }

    def del_pass_code(self, m_id):
        if m_id.startswith("/") or "//" in m_id:
            m_id = quote_plus(quote_plus(m_id))

        recs_settings = requests.get(url=self.base_url + f"meetings/{m_id}/recordings/settings", headers=self.header)
        # print(recs_settings)
        # print(recs_settings.json())
        payload = recs_settings.json()

        if payload["password"] != "":
            payload["password"] = ""

            del_pass_header = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }

            requests.patch(
                url=self.base_url + f"meetings/{m_id}/recordings/settings",
                headers=del_pass_header,
                json=payload
            )
        # url_re = requests.get(url=base_url + f"meetings/{m_id}/recordings/settings", headers=header)

    def get_link(self, meeting_id, user_id):
        list_of_urls = []
        meeting_id = int(meeting_id)

        payl = {
            "from": self.DATE,
            "to": self.DATE,
            "meeting_id": meeting_id
        }

        rec = requests.get(url=self.base_url + f"users/{user_id}/recordings", headers=self.header, params=payl)
        print(rec.json())

        for meeting in rec.json()["meetings"]:
            self.del_pass_code(meeting["uuid"])

        rec_url = requests.get(url=self.base_url + f"users/{user_id}/recordings", headers=self.header, params=payl)

        for meeting in rec_url.json()["meetings"]:
            if meeting["duration"] > 5:
                list_of_urls.append(meeting["share_url"])

        return list_of_urls

    def get_list_of_meetings(self):
        """Возвращает список прошедших встреч за прошлую неделю"""
        payl = {
            "type": "previous_meetings",
            "from": datetime.today().strftime('%Y-%m-%d'),
            "to": (datetime.today()-timedelta(days=7)).strftime('%Y-%m-%d'),
        }
        users_list = [
            "admin@mayak.study",
            "websfromhome@mayak.study",
            "info@mayak.study",
            "sc@mayak.study",
            "websfromhome2@mayak.study",
            "websfromhome3@gmail.com",
            "websfromhome4@mayak.study",
            "websfromhome5@mayak.study",
            "websfromhome6@mayak.study",
            "websfromhome7@mayak.study",
            "websfromhome8@mayak.study",
            "websfromhome9@mayak.study",
            "websfromhome10@mayak.study",
            "ufa@mayak.study",
            "ufa2@mayak.study",
            "ufa3@mayak.study",
            "ufa4@mayak.study",
            "tumen@mayak.study",
            "tumen2@mayak.study",
            "tumen3@mayak.study",
            "tumen4mayak@gmail.com",
            "webinar5@mayak.study",
            "samara@mayak.study",
            "samara2@mayak.study",
            "krasnodar@mayak.study",
            "krasnodar2@mayak.study",
            "kazan@mayak.study",
        ]

        d = {}
        ind = 0
        for user in users_list:
            time.sleep(0.2)
            rec = requests.get(url=self.base_url + f"users/{user}/meetings", headers=self.header, params=payl)
            for meeting in rec.json()["meetings"]:
                ind = ind + 1
                d.update(
                    {ind: dict(
                        meeting_id=meeting["id"],
                        topic=meeting["topic"],
                        duration=meeting["duration"],
                        email=user
                    )}
                )

        df = pd.DataFrame.from_dict(d).transpose()
        # Удаляем всё, что длится не 120 или 90 минут
        df.drop(df[~((df["duration"] == 120) | (df["duration"] == 90))].index, inplace=True)
        # df.to_excel("data/zoom_meetings.xlsx")
        print("Got list of meetings!")
        return df


def rename_topics(row):
    s = row["topic"]
    if ":" in s:
        return s[:s.index(":")-6] + s[s.index(":")+3:]
    else:
        return s


def parity(row):
    if row["duration"] == 90:
        return "even"
    else:
        return "odd"
