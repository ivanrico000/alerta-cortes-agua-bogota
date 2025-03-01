import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
from urllib.parse import urljoin

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

url = "https://bogota.gov.co/"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    div_element = soup.find(id="reporte1")

    if div_element:
        a_element = div_element.find("a")

        if a_element:
            enlace = a_element.get("href", "No encontrado")
            enlace_completo = urljoin(url, enlace)

            subResponse = requests.get(enlace_completo, headers=headers)

            if subResponse.status_code == 200:
                subSoup = BeautifulSoup(subResponse.text, "html.parser")
                titlesElements = subSoup.find_all("h1")

                for title in titlesElements:
                    textTitle = title.get_text(strip=True)

                    if "Racionamiento" in textTitle:
                        match = re.search(r"¡(.*?)!", textTitle)
                        cycle = match.group(1) if match else "No encontrado"

                        strMenssage = ""
                        
                        if cycle.lower() == "turno 3":
                            strMenssage = "Mañana Corte de Agua!"
                        elif cycle.lower() == "turno 4":
                            strMenssage = "HOY Corte de Agua!"

                        if strMenssage:
                            subUrl = "https://api.callmebot.com/whatsapp.php?source=web&phone=+573115777165&apikey=6959101&text=" + urllib.parse.quote(strMenssage)
                            responseWhats = requests.get(subUrl, headers=headers)
                        break 
