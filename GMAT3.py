import requests
from bs4 import BeautifulSoup
import re
import gspread
from google.oauth2.service_account import Credentials 

url = 'https://www.fundamentus.com.br/detalhes.php?papel=GMAT3'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Referer": "https://www.google.com/"
}

request = requests.get(url, headers=headers, timeout=15)
print(request.status_code)

dados_pagina = BeautifulSoup(request.text, 'html.parser')

label_list = []
data_list = []

clabel = dados_pagina.find_all('td', class_=re.compile(r"^label"))
for label in clabel:
    span = label.find('span', class_='txt')
    spanlabel = span.get_text(strip=True) if span else label.get_text(strip=True)
    label_list.append(spanlabel)

cdata = dados_pagina.find_all('td', class_=re.compile(r"^data"))
for data in cdata:
    span = data.find('span', class_='txt')
    spandata = span.get_text(strip=True) if span else data.get_text(strip=True)
    data_list.append(spandata)


n = min(len(label_list), len(data_list))

rows = [["Campo", "Valor"]]

for i in range(n):
    rows.append([label_list[i], data_list[i]])


SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
gc = gspread.authorize(creds)


sh = gc.open("Fundamentus")   
worksheet = sh.worksheet("dadosGMAT3")  

worksheet.clear()
worksheet.update("A1", rows)

print("Dados gravados no Google Sheets com sucesso.")


