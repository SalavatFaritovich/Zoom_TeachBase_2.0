import pandas as pd
from pathlib import Path

"""
    На основе файл ОП создаёт таблицу group_id, date, lesson_num, city
    Сохраняет в data/schedule.csv
"""


def converter(df, city):
    df.loc[0, "ID"] = "ID"

    drop_columns_list = ['Код группы ', 'Преподаватель', 'Unnamed: 2', 'Unnamed: 3',
                     'Город', 'Тип группы', 'Формат ', 'Продолжительность',
                     'Предмет ', 'Тип курса', 'Дата старта', 'Год окончания',
                     'Итого (мин)', 'Итого (час)', 'Дней до экзамена']
    df.drop(drop_columns_list, axis=1, inplace=True)

    df.columns = df.iloc[0]
    df.drop([0, 1], axis=0, inplace=True)
    df.drop(df[df["ID"].isna()].index, inplace=True)

    d = {}
    ind = 0
    for col in df.columns.values:
        for i in df.index.values:
            if col != "ID":
                if pd.notna(df[col][i]) and df[col][i] != 'к':
                    ind = ind + 1
                    d.update(
                        {ind: dict(ID=df['ID'][i], date=col, lesson_num=df[col][i], city=city)}
                    )
    return pd.DataFrame.from_dict(d).transpose()


def parity(row):
    if row["lesson_num"] % 2 == 0:
        return "even"
    else:
        return "odd"


def make_schedule():
    """На основе файла ОП.xlsx создаёт файл schedule.csv"""
    path_to_data = Path('data/').resolve()
    base_table = pd.read_excel(io=path_to_data / 'ОП.xlsx', sheet_name=None)
    base_table.pop('Общая таблица')

    list_of_tables = []
    for name in base_table.keys():
        list_of_tables.append(converter(base_table[name], name))

    schedule = pd.concat(objs=list_of_tables, ignore_index=True)
    # schedule.astype({'lesson_num': 'int32'})
    schedule.drop(schedule[(schedule["lesson_num"] % 2 == 1) & (schedule["city"] != "Онлайн")].index, inplace=True)

    schedule["parity"] = schedule.apply(parity, axis=1)

    schedule.to_csv(path_or_buf=path_to_data / 'schedule.csv', encoding='utf-8')

