import os
import pandas as pd
from dotenv import load_dotenv
from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import AddItemProperty, ListItemProperties
from recombee_api_client.exceptions import APIException

# TODO 1: Configurare credentiale Recombee
# Credentialele se citesc din fisierul .env (exclus din git), vezi .env.example
load_dotenv()
DB_NAME = os.environ['RECOMBEE_DB']
PRIVATE_TOKEN = os.environ['RECOMBEE_PRIVATE_TOKEN']
# SDK-ul v6 cere enum-ul Region, nu string-ul 'eu-west'
REGION = Region[os.environ.get('RECOMBEE_REGION', 'eu-west').upper().replace('-', '_')]

# Initializarea clientului Recombee
client = RecombeeClient(DB_NAME, PRIVATE_TOKEN, region=REGION)

# TODO 2: Configurare dataset propriu
# Descarcati un dataset (CSV) de pe Kaggle/data.world (100-10K de intrari)
# Urcati fisierul in acelasi folder cu acest script si setati numele in variabila de mai jos
# Generat din movies.csv (Kaggle, danielgrijalvas/movies) cu prepare_dataset.py
PATH_DATASET = 'movies_recombee.csv'

# TODO 3: Definirea schemei de date (minim 3 proprietati)
# Adaptati aceasta lista in functie de coloanele din dataset-ul ales
# Tipurile de date suportate de Recombee includ: 'string', 'int', 'double', 'boolean', 'timestamp'
# Coloana item_id NU apare aici: Recombee o foloseste ca itemId la incarcarea produselor
PROPRIETATI_CATALOG = [
    {"name": "title", "type": "string"},
    {"name": "age_rating", "type": "string"},       # ex.: R, PG-13
    {"name": "genre", "type": "string"},
    {"name": "year", "type": "int"},
    {"name": "release_date", "type": "timestamp"},
    {"name": "release_country", "type": "string"},
    {"name": "score", "type": "double"},            # nota IMDb, 1-10
    {"name": "votes", "type": "int"},               # numar de voturi IMDb
    {"name": "director", "type": "string"},
    {"name": "writer", "type": "string"},
    {"name": "star", "type": "string"},             # actorul principal
    {"name": "country", "type": "string"},          # tara de productie
    {"name": "budget", "type": "double"},           # USD
    {"name": "gross", "type": "double"},            # incasari, USD
    {"name": "company", "type": "string"},          # studioul
    {"name": "runtime", "type": "int"},             # minute
]

def load_dataset():
    """Functie helper care citeste si verifica dataset-ul"""
    try:
        df = pd.read_csv(PATH_DATASET)
        total_randuri = len(df)
        print(f"Dataset incarcat cu succes! Total randuri: {total_randuri}")
        
        # Verificare numar de randuri (100 - 10K)
        if total_randuri < 100:
            print("ATENTIE: Dataset-ul are sub 100 de produse!")
        elif total_randuri > 10 * 1000:
            print("ATENTIE: Dataset-ul este prea mare! Limitati-l la primele 10K randuri.")
            
        print("\nPreview primele 3 randuri:")
        print(df.head(3))
        print("-" * 50)
        return df
    except FileNotFoundError:
        print(f"Eroare: Fisierul '{PATH_DATASET}' nu a fost gasit!")
        return None

def set_properties():
    """Functie care trimite structura coloanelor catre Recombee"""
    print(f"\nIncepe definirea proprietatilor pentru baza de date: '{DB_NAME}'...")
    
    for prop in PROPRIETATI_CATALOG:
        # Validare nume proprietati valide
        if "nume_proprietate" in prop["name"]:
            print("Eroare: Trebuie sa schimbati 'nume_proprietate_x' cu denumirile reale din coloanele fisierul vostru!")
            continue
            
        try:
            # Request API Recombee pentru adaugarea proprietatii (echivalentul adaugarii unei coloane intr-un tabel)
            client.send(AddItemProperty(prop["name"], prop["type"]))
            print(f"Proprietatea '{prop['name']}' ({prop['type']}) a fost adaugata cu succes.")
        except APIException as e:
            # Recombee returnează eroare daca proprietatea a fost deja definita la o rulare anterioara
            if "already exists" in str(e).lower():
                print(f"Proprietatea '{prop['name']}' exista deja in Recombee.")
            else:
                print(f"Eroare API la proprietatea '{prop['name']}': {e}")

def verify():
    """Interogheaza API-ul pentru a lista toate proprietatile active dsin cont"""
    print("Se verifica structura finala din Recombee Admin UI...")
    try:
        atribute_active = client.send(ListItemProperties())
        print("Proprietatile configurate in acest moment in baza ta de date:")
        for atribute in atribute_active:
            print(f"- {atribute['name']} => tip de date: {atribute['type']}")
    except APIException as e:
        print(f"Nu s-a putut efectua verificarea. Detalii eroare: {e}")

if __name__ == "__main__":
    # Verificam daca fisierul CSV local se citeste corect
    dataset_ok = load_dataset()
    
    if dataset_ok is not None:
        # Trimitem proprietatile catre Recombee prin API
        set_properties()
        
        # Listam ce s-a salvat in baza de date pentru confirmare
        verify()
