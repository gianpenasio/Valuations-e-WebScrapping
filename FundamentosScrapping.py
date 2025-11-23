import requests
from bs4 import BeautifulSoup
import re
import gspread
from google.oauth2.service_account import Credentials 
from collections import OrderedDict

papel = ["GMAT3", "PETR4", "JHSF3", "CMIG3", "BBAS3"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Referer": "https://www.google.com/"
}

def scrap(papel):
    url = f'https://www.fundamentus.com.br/detalhes.php?papel={papel}'
    request = requests.get(url, headers=HEADERS, timeout=15)
    print(request.status_code)

    dados_pagina = BeautifulSoup(request.text, 'html.parser')

    label_list = []
    data_list = []

    labels = dados_pagina.find_all('td', class_=re.compile(r"^label"))
    for label in labels:
        span = label.find('span', class_='txt')
        spanlabel = span.get_text(strip=True) if span else label.get_text(strip=True)
        label_list.append(spanlabel)

    datas = dados_pagina.find_all('td', class_=re.compile(r"^data"))
    for data in datas:
        span = data.find('span', class_='txt')
        spandata = span.get_text(strip=True) if span else data.get_text(strip=True)
        data_list.append(spandata)

    od = []
    n = min(len(label_list), len(data_list))
    for i in range(n):
        od.append([label_list[i], data_list[i]])

    return od

def parear(papel_dicts):
    all_labels = []
    seen = set()

    for t in papel:
        lista = papel_dicts.get(t, [])
        for par in lista:  # par = [label, valor]
            if len(par) < 2:
                continue
            lab = par[0]
            if lab not in seen:
                seen.add(lab)
                all_labels.append(lab)

    rows = []
    header = ["Campo"] + papel
    rows.append(header)

    for lab in all_labels:
        row = [lab]
        for t in papel:
            lista = papel_dicts.get(t, [])
            valor = ""
            for par in lista:
                if par[0] == lab:
                    valor = par[1]
                    break
            row.append(valor)
        rows.append(row)

    return rows


def main():
    papel_data = {}
    for t in papel:
        try:
            print(f"Buscando {t} ...", end=" ")
            od = scrap(t)
            papel_data[t] = od
            print("ok")
        except Exception as e:
            print("falhou:", e)
            papel_data[t] = OrderedDict()

    rows = parear(papel_data)

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    gc = gspread.authorize(creds)

    sh = gc.open("Fundamentus")
    sheet_name = "dados"
    worksheet = sh.worksheet(sheet_name)

    worksheet.clear()
    worksheet.update("A1", rows)

    print("Dados Integrados", sheet_name)

if __name__ == "__main__":
    main()

    
