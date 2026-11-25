import json
import re
from html import unescape
from html.parser import HTMLParser

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Dataset: produse Tesco, fiecare cu un camp "description" (text cu tag-uri HTML)
PATH_DATASET = 'tesco_sample.json'
PATH_MATRICE = 'similarity_matrix.csv'
TOP_PERECHI = 25


class TextExtractor(HTMLParser):
    """Pastreaza doar textul dintre tag-uri, separat prin spatii."""

    def __init__(self):
        super().__init__()
        self.bucati = []

    def handle_data(self, data):
        self.bucati.append(data)


def elimina_html(text):
    parser = TextExtractor()
    parser.feed(text or '')
    return unescape(' '.join(parser.bucati))


def preproceseaza(text):
    """Pasii din tutorial: litere mici, fara cifre si caractere speciale.
    Cuvintele de legatura (stop words) le elimina TfidfVectorizer."""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def main():
    with open(PATH_DATASET, encoding='utf-8') as f:
        produse = pd.DataFrame(json.load(f))
    print(f'Produse incarcate: {len(produse)}')

    # Fisierul contine acelasi produs de mai multe ori (acelasi SKU); pastram o singura copie
    produse = produse.drop_duplicates(subset='sku').reset_index(drop=True)
    print(f'Produse unice (dupa SKU): {len(produse)}')

    # Unele produse au in descriere doar titlul "Information" si adresa Tesco, deci texte
    # identice (scor 1.0 intre o palnie si un prosop). Adaugam numele produsului la text
    # si scoatem adresa, care apare la aproape toate produsele.
    descrieri = produse['description'].apply(elimina_html).str.replace(
        r'Return to Tesco Stores Ltd.*?U\.?K\.?', ' ', regex=True)
    produse['text'] = (produse['name'] + ' ' + descrieri).apply(preproceseaza)

    # Matricea TF-IDF: un rand per produs, o coloana per cuvant din vocabular
    tfidf = TfidfVectorizer(stop_words='english')
    vectori = tfidf.fit_transform(produse['text'])
    print(f'Vocabular: {len(tfidf.vocabulary_)} cuvinte')

    # Matricea de similaritate: scorul cosine pentru fiecare pereche de produse
    scoruri = cosine_similarity(vectori)
    etichete = [f'{i}: {nume}' for i, nume in enumerate(produse['name'])]
    pd.DataFrame(scoruri, index=etichete, columns=etichete).round(4).to_csv(PATH_MATRICE)
    print(f'Matricea de similaritate ({len(produse)} x {len(produse)}) salvata in {PATH_MATRICE}')

    # Cele mai asemanatoare perechi (fara perechile unui produs cu el insusi)
    perechi = [
        (scoruri[i, j], i, j)
        for i in range(len(produse))
        for j in range(i + 1, len(produse))
    ]
    perechi.sort(reverse=True)
    print(f'\nTop {TOP_PERECHI} perechi de produse asemanatoare:')
    for scor, i, j in perechi[:TOP_PERECHI]:
        print(f'  {scor:.3f}  [{i}] {produse.at[i, "name"]}  <->  [{j}] {produse.at[j, "name"]}')


if __name__ == '__main__':
    main()
