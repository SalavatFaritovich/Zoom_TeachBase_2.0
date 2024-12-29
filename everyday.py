import os
import sys
from dotenv import load_dotenv

import pandas as pd
from zoom import ZoomHandler
from teach_by_selenium import Teachbase

load_dotenv()
DATE = os.getenv('DATE')

if os.path.exists(f"results/{DATE}.xlsx"):
    check1 = input(f"Внимание! Отчёт о вставке за {DATE} уже существует. \n"
                   f"Для подтверждения введите 'y'. \n"
                   f"Если дата неверна, исправьте DATE в .env и перезапустите программу \n"
                   f"Для выхода нажмите Enter.\n")

    if check1 != 'y':
        print("Exiting...")
        sys.exit(0)

check2 = input(f"Вы хотите вставить записи вебинаров прошедших {DATE}. \n"
               f"Для подтверждения введите 'y'. \n"
               f"Если дата неверна, исправьте DATE в .env и перезапустите программу \n"
               f"Для выхода нажмите Enter.\n")

if check2 != 'y':
    print("Exiting...")
    sys.exit(0)
else:
    print("Starting...")


full_info = pd.read_excel(io="data/full_info.xlsx")
df = full_info[full_info["date"] == DATE + " 00:00:00"].reset_index()

# ----------------------------------------------------------------------------------------------------------------------
zm = ZoomHandler()

share_urls = []
for index, row in df.iterrows():
    share_urls.append(zm.get_link(meeting_id=row["meeting_id"], user_id=row["email"]))

df["share_urls"] = share_urls
# df.to_excel("trash/temp.xlsx")
# check = input("Проверь файл temp.xlsx \n Нажми 'y', чтобы продолжить")
# if check != 'y':
#     print("Exiting...")
#     sys.exit(0)
# else:
#     print("Продолжаем")

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
teach = Teachbase()
teach.enter_teachbase()

status = []
for index, row in df.iterrows():
    status.append(teach.edit_course(row))

teach.exit_teachbase()

df["status"] = status

df.to_excel(f"results/{DATE}.xlsx")

print(f"Проверь {DATE}.xlsx в папке results")
