import pandas as pd

# Dataset original: "Movie Industry" (Kaggle, danielgrijalvas/movies), lasat neschimbat
PATH_RAW = 'movies.csv'
# Copia pregatita pentru Recombee, folosita de recombee_properties.py
PATH_CLEAN = 'movies_recombee.csv'


def parse_release(text):
    """Imparte 'June 13, 1980 (United States)' in data si tara lansarii.
    Unele filme au doar luna si anul ('April 1991') sau doar anul ('1985');
    acestea primesc prima zi a lunii, respectiv a anului."""
    if pd.isna(text):
        return pd.NaT, None
    date_part, _, country = text.partition(' (')
    country = country.rstrip(')') or None
    for fmt in ('%B %d, %Y', '%B %Y', '%Y'):
        try:
            return pd.to_datetime(date_part.strip(), format=fmt), country
        except ValueError:
            pass
    return pd.NaT, country


def main():
    df = pd.read_csv(PATH_RAW)

    # Identificatorul unic (itemId in Recombee) - nu se inregistreaza ca proprietate
    df.insert(0, 'item_id', [f'movie_{i}' for i in range(1, len(df) + 1)])

    released = df['released'].apply(parse_release)
    df['release_date'] = pd.to_datetime(released.str[0]).dt.strftime('%Y-%m-%d')
    df['release_country'] = released.str[1]

    # Nume de coloane identice cu proprietatile din Recombee
    df = df.rename(columns={'name': 'title', 'rating': 'age_rating'})
    df = df.drop(columns=['released'])

    # votes si runtime sunt float in CSV doar din cauza valorilor lipsa
    for col in ('votes', 'runtime'):
        df[col] = df[col].astype('Int64')

    df.to_csv(PATH_CLEAN, index=False)
    print(f'Scris {PATH_CLEAN}: {len(df)} randuri, {len(df.columns)} coloane')
    print(f"Date de lansare necitite: {df['release_date'].isna().sum()}")


if __name__ == '__main__':
    main()
