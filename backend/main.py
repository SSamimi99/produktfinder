
# Backend: Multi-Plattform Produkt-Finder mit CSV & Zeitplan

import random
import csv
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

plattformen = ["AliExpress", "Amazon", "eBay"]
kategorien = ["Elektronik", "Haushalt", "Beauty", "Fitness", "Mode", "Gadgets"]

data_store = []  # Zwischenspeicher für Produkte

def scrape_mock_platform(name):
    daten = []
    for i in range(330):
        preis = round(random.uniform(5, 30), 2)
        verkaufspreis = round(preis * random.uniform(1.8, 2.5), 2)
        marge = round(verkaufspreis - preis, 2)
        score = round((marge * random.uniform(0.8, 1.2)) + random.randint(10, 100), 2)
        versandtage = random.randint(3, 7)
        daten.append({
            "Produktname": f"{name} Produkt {i + 1}",
            "Plattform": name,
            "Kategorie": random.choice(kategorien),
            "Einkaufspreis": preis,
            "Verkaufspreis": verkaufspreis,
            "Marge": marge,
            "Bewertungen": random.randint(100, 5000),
            "Rating": round(random.uniform(3.5, 5.0), 1),
            "Versandzeit (Tage)": versandtage,
            "Profit-Score": score
        })
    return daten

def aktualisiere_daten():
    global data_store
    aliexpress = scrape_mock_platform("AliExpress")
    amazon = scrape_mock_platform("Amazon")
    ebay = scrape_mock_platform("eBay")
    data_store = aliexpress + amazon + ebay
    print(f"[Update] {len(data_store)} Produkte aktualisiert: {datetime.now().strftime('%H:%M:%S')}")

@app.get("/api/produkte")
def get_all_products():
    return JSONResponse(content=data_store)

@app.get("/export")
def exportiere_csv():
    if not data_store:
        aktualisiere_daten()
    dateiname = f"produktdaten_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    with open(dateiname, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data_store[0].keys())
        writer.writeheader()
        writer.writerows(data_store)
    return FileResponse(dateiname, filename=dateiname)

@app.get("/")
def root():
    return {"message": "Multi-Plattform Produkt-API mit CSV & Auto-Update aktiv."}

# Starte stündliche Datenerneuerung
scheduler = BackgroundScheduler()
scheduler.add_job(aktualisiere_daten, "interval", hours=1)
scheduler.start()

# Initialdaten beim Start
aktualisiere_daten()
