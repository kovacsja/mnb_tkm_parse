from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
from datetime import datetime

url: str = (
    "https://tkm.mnb.hu/?it=1&sp=&fpt=1&page=1&pagesize=100&orderCol=5&desc=False"
)

browser = webdriver.Chrome("chromedriver")
tkm_html = browser.get(url)
browser.implicitly_wait(10)
institutes = browser.find_elements_by_class_name("institute-name")

for i in institutes:
    i.click()
    browser.implicitly_wait(10)

soup = BeautifulSoup(browser.page_source, "lxml")

browser.close()
rows = soup.find_all("tr", {"class": ["prow", "subtabletr"]})

df_input = []
for r in rows:
    res = []
    if r.find("div", class_="first-column"):
        inst = r.find("div", class_="institute-name").text.strip()
        prod = r.find("td", class_="td-notfirst").text.strip()
    elif "%" in r.text:
        res.append(inst)
        res.append(prod)
        for d in r.find_all("td"):
            res.append(d.text.strip())
    if len(res) > 0:
        df_input.append(res)

df = pd.DataFrame(df_input)

# fejlécek beállítása
df.columns = ["Intézmény", "Termék", "Alap", "Y5", "Y10", "Y15", "Y20", "Y30"]

# szöveges számformátumok átalakítása
df["Y5"] = df["Y5"].str.replace("%", "")
df["Y10"] = df["Y10"].str.replace("%", "")
df["Y15"] = df["Y15"].str.replace("%", "")
df["Y20"] = df["Y20"].str.replace("%", "")
df["Y30"] = df["Y30"].str.replace("%", "")

df["Y5"] = df["Y5"].str.replace(",", ".")
df["Y10"] = df["Y10"].str.replace(",", ".")
df["Y15"] = df["Y15"].str.replace(",", ".")
df["Y20"] = df["Y20"].str.replace(",", ".")
df["Y30"] = df["Y30"].str.replace(",", ".")

# üres értékek cseréje
df = df.replace("", np.NaN)

# ha valami még mindig szöveg maradt, akkor itt meg fog akadni a folyamat
df["Y5"] = df["Y5"].astype(float)
df["Y10"] = df["Y10"].astype(float)
df["Y15"] = df["Y15"].astype(float)
df["Y20"] = df["Y20"].astype(float)
df["Y30"] = df["Y30"].astype(float)

# az eredménytábla kimentése excelbe
td: str = datetime.now().strftime("%Y%m%d")

df.to_excel(f"tkm_{td}.xlsx")