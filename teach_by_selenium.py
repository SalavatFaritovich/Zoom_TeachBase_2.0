from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
from dotenv import load_dotenv

"""
    С помощью selenium вставляет ссылку в курс. 
"""


class Teachbase:
    def __init__(self):
        self.service = Service(executable_path="chromedriver.exe")
        self.driver = webdriver.Chrome(service=self.service)

    def enter_teachbase(self):
        load_dotenv()
        login = os.getenv('TEACHBASE_LOGIN')
        password = os.getenv('TEACHBASE_PASSWORD')

        self.driver.get("https://mayak.teachbase.ru/login/briliant")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "user_login_form_login"))
        )

        input_element = self.driver.find_element(By.ID, "user_login_form_login")
        input_element.clear()
        input_element.send_keys(login)

        input_element = self.driver.find_element(By.ID, "user_login_form_password")
        input_element.clear()
        input_element.send_keys(password + Keys.ENTER)

        self.driver.implicitly_wait(10)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/hinted-modal/div[2]/div/div/div[2]/div[1]/button'))
            )
        except:
            print("no Готово button")
        else:
            self.driver.find_element(By.XPATH, '/html/body/hinted-modal/div[2]/div/div/div[2]/div[1]/button').click()

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[text()="Нет"]'))
            )
        except:
            print("no Нет button")
        else:
            self.driver.find_element(By.XPATH, '//button[text()="Нет"]').click()

        self.driver.implicitly_wait(1)

    def fill_in_inputs(self, name, link):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[text()="Добавить"]'))
        )

        button = self.driver.find_elements(By.XPATH, '//button[text()="Добавить"]')[1]
        self.driver.execute_script("arguments[0].scrollIntoView();", button)
        self.driver.execute_script("arguments[0].click();", button)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[text()="Встроить ресурс"]'))
        )

        resource = self.driver.find_element(By.XPATH, '//div[text()="Встроить ресурс"]')
        self.driver.execute_script("arguments[0].scrollIntoView();", resource)
        self.driver.execute_script("arguments[0].click();", resource)

        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        )

        lesson_name = self.driver.find_elements(By.TAG_NAME, "input")[1]
        lesson_name.send_keys(name)

        minutes = self.driver.find_elements(By.TAG_NAME, "input")[2]
        minutes.clear()
        minutes.send_keys("0")

        seconds = self.driver.find_elements(By.TAG_NAME, "input")[3]
        seconds.clear()
        seconds.send_keys("0")

        url_field = self.driver.find_elements(By.TAG_NAME, "input")[4]
        url_field.send_keys(link)

        save_button = self.driver.find_element(By.XPATH, '//button[text()="Сохранить"]')
        save_button.click()

    def edit_course(self, row):
        """Вставляем ссылку"""
        course_id = int(row["teachbase_id"])
        lesson_num = int(row["lesson_num"])
        links = row["share_urls"]

        # if "', '" in text:
        #     links = text[2:][:-2].split("', '")
        # elif text == "[]":
        #     print("skip")
        #     return "skip"
        # else:
        #     links = [text[2:][:-2]]

        self.driver.get(f"https://mayak.teachbase.ru/manager/courses/{course_id}/edit")
        print(row["teachbase_name"])

        if not links:
            return "нет записи"

        print(len(links))
        if len(links) > 1:
            for i in range(len(links)):
                try:
                    self.fill_in_inputs(name=f"Урок {lesson_num}.{i+1}", link=links[i])
                    self.driver.implicitly_wait(1)
                except Exception as e:
                    print(e)
                    return f"error: {e}"
        else:
            try:
                self.fill_in_inputs(name=f"Урок {lesson_num}", link=links[0])
            except Exception as e:
                print(e)
                return f"error: {e}"
        self.driver.implicitly_wait(1)
        print("OK")
        return "OK"

    def exit_teachbase(self):
        self.driver.quit()

    # df = pd.read_excel(io=f"data/by_date/{DATE}_with_links.xlsx")
    #
    # df["status"] = df.apply(edit_course, axis=1)
    #
    # df.to_excel(f"data/by_date/{DATE}_status.xlsx")

