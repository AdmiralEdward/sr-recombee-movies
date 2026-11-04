# Sisteme de Recomandare - Laborator 2: proprietăți Recombee

Catalogul unui sistem de recomandare de filme, definit în [Recombee](https://www.recombee.com/). Acest laborator înregistrează proprietățile (atributele) produselor și tipul lor de date. Filmele propriu-zise vor fi încărcate în laboratorul următor.

## Domeniul ales: filme

Sistemul va recomanda filme. Pentru fiecare film avem date despre conținut (gen, regizor, actor principal), despre public (nota și numărul de voturi IMDb) și despre producție (buget, încasări, studio). Aceste atribute pot fi folosite ulterior atât pentru recomandări bazate pe conținut, cât și pentru filtre (de ex. doar filme cu nota peste 7).

## Dataset-ul

- **Nume:** Movie Industry - Four decades of movies
- **Sursă:** [Kaggle - danielgrijalvas/movies](https://www.kaggle.com/datasets/danielgrijalvas/movies), date preluate de pe IMDb
- **Volum:** 7.668 de filme, lansate între 1980 și 2020
- **Fișier original:** [`movies.csv`](movies.csv), păstrat neschimbat
- **Fișier folosit:** [`movies_recombee.csv`](movies_recombee.csv), generat de [`prepare_dataset.py`](prepare_dataset.py)

Câteva caracteristici ale datelor:
- 19 genuri; cele mai frecvente sunt Comedy (2.245), Action (1.705) și Drama (1.518).
- Filme din 59 de țări de producție, dintre care aproximativ 71% din Statele Unite.
- Nota IMDb variază între 1,9 și 9,3, cu media 6,39.
- Durata variază între 55 și 366 de minute.

### Pregătirea datelor

`prepare_dataset.py` citește `movies.csv` și scrie `movies_recombee.csv`, cu următoarele modificări:

1. Adaugă coloana `item_id` (`movie_1` … `movie_7668`), identificatorul unic al fiecărui film. Dataset-ul original nu are un ID.
2. Împarte coloana `released` (ex. `June 13, 1980 (United States)`) în `release_date` (`1980-06-13`) și `release_country` (`United States`). 57 de filme au doar luna și anul sau doar anul; pentru acestea se folosește prima zi a lunii, respectiv a anului.
3. Redenumește `name` în `title` și `rating` în `age_rating`, ca să nu fie confundată clasificarea de vârstă cu nota IMDb (`score`).

Rândurile cu valori lipsă au fost păstrate. Valorile lipsă rămân goale (cele mai multe la `budget`: 2.171 de filme).

## Proprietățile înregistrate în Recombee

`item_id` nu este înregistrat ca proprietate: Recombee îl gestionează ca `itemId` la încărcarea filmelor.

| Proprietate | Tip | Descriere | Exemplu |
| --- | --- | --- | --- |
| `title` | string | Titlul filmului | The Shining |
| `age_rating` | string | Clasificarea de vârstă (MPAA) | R |
| `genre` | string | Genul principal | Drama |
| `year` | int | Anul lansării | 1980 |
| `release_date` | timestamp | Data lansării | 1980-06-13 |
| `release_country` | string | Țara primei lansări | United States |
| `score` | double | Nota IMDb (1-10) | 8.4 |
| `votes` | int | Numărul de voturi IMDb | 927000 |
| `director` | string | Regizorul | Stanley Kubrick |
| `writer` | string | Scenaristul | Stephen King |
| `star` | string | Actorul principal | Jack Nicholson |
| `country` | string | Țara de producție | United Kingdom |
| `budget` | double | Bugetul, în USD | 19000000 |
| `gross` | double | Încasările, în USD | 46998772 |
| `company` | string | Studioul de producție | Warner Bros. |
| `runtime` | int | Durata, în minute | 146 |

În total: 16 proprietăți (9 string, 3 int, 3 double, 1 timestamp).

## Rulare

Necesită Python 3.11 sau mai nou (cerință pandas 3).

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Credențialele Recombee se citesc din fișierul `.env`, care nu este inclus în repository. Copiați `.env.example` în `.env` și completați datele din Recombee Admin UI (*Settings → API ID & Tokens*):

```
RECOMBEE_DB=id_baza_de_date
RECOMBEE_REGION=eu-west
RECOMBEE_PRIVATE_TOKEN=token_privat
```

Apoi:

```bash
python prepare_dataset.py         # generează movies_recombee.csv din movies.csv
python recombee_properties.py     # înregistrează proprietățile în Recombee și le listează
```

Rularea repetată este sigură: proprietățile deja existente sunt raportate și sărite.

## Modificări față de codul de pornire

- Credențialele sunt citite din `.env` cu `python-dotenv`, ca tokenul privat să nu ajungă în repository.
- Regiunea este transmisă ca enum-ul `Region` (ex. `Region.EU_WEST`). Versiunea 6 a SDK-ului `recombee-api-client` nu mai acceptă string-ul `'eu-west'` și oprește scriptul cu `ValueError: Unknown region given`.

## Laborator 4: ontologie în WebProtégé

[`lab04/pizza_ontology.owl`](lab04/pizza_ontology.owl) este ontologia exportată din WebProtégé (format RDF/XML), construită pornind de la exemplul clasic cu pizza.

- **Clase:** `Pizza` (MargheritaPizza, DiavolaPizza, ProsciuttoPizza), `Topping` (Mozzarella, Pepperoni, Prosciutto), `PizzaBase` (ThinNoSauce, ThinPlusSauce) și `Student`.
- **Proprietăți de obiect:** `hasTopping`, `isToppingOf`, `hasBase`, `likesPizza`.
- **Proprietăți de date:** `hasPrice`, `hasCalories`, `hasDiameterCm`, `hasUserHash`.
- **Indivizi:** `margheritaPizza1`, `diavolaPizza1`, `mozzarella1`, `pepperoni1`, `prosciutto1`, `thinSauceBase1` și `euStudent`. Individul `euStudent` are ca valoare pentru `hasUserHash` hash-ul SHA-256 al emailului instituțional.
