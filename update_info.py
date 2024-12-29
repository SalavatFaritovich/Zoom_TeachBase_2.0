"""
    1. получаем schedule, данные из битрикса, курсы в тичбейс, данные из зума
    2. К schedule джоиним битрикс
    3. джоиним зум
    4. джоиним тичейс
    5. сохраняем всё в full_info.xlsx
"""
import pandas as pd


from preparations.schedule import make_schedule
from preparations.from_teachbase import get_teachbase_cources
from preparations.from_b24 import get_bitrix_ids_and_names
from zoom import ZoomHandler, rename_topics, parity


make_schedule()     # создали файл schedule.csv
schedule_df = pd.read_csv(filepath_or_buffer='data/schedule.csv', encoding='utf-8')

bitrix_df = get_bitrix_ids_and_names()
teachbase_df = get_teachbase_cources()

zoom_df = ZoomHandler().get_list_of_meetings()
zoom_df["name"] = zoom_df.apply(rename_topics, axis=1)
zoom_df["parity"] = zoom_df.apply(parity, axis=1)

# zoom_df.to_excel("data/temp_zoom_df.xlsx")

sch_bit_df = pd.merge(schedule_df, bitrix_df, on="ID", how="left")
sch_bit_teach_df = pd.merge(sch_bit_df, teachbase_df, on="teachbase_name", how="left")

# sch_bit_teach_df.to_excel("data/sch_bit_teach_df.xlsx")

full = pd.merge(sch_bit_teach_df, zoom_df, on="name", how="left")

full.drop_duplicates(inplace=True)
full.drop(full[full["parity_x"] != full["parity_y"]].index, inplace=True)
full.drop(columns=["parity_x", "parity_y"], axis=1, inplace=True)

full.to_excel("data/full_info.xlsx")

# задать правильные имена столбцам, убрать лишние

