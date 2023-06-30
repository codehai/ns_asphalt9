import json
import requests
from bs4 import BeautifulSoup

cars = []
r = requests.get("https://www.infoasphalt.com/en/iav3-carsmaster/")
soup = BeautifulSoup(r.text, "html.parser")

trs = soup.find_all("tr")

for tr in trs:
    tds = tr.find_all("td")
    if len(tds) >= 3 and tds[2].text in ["A", "B", "C", "D", "S"]:
        cars.append({"name": tds[0].text, "class": tds[2].text})

with open("cars.json", "w") as f:
    f.write(json.dumps(cars, indent=2))
