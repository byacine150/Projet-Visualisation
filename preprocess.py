'''
    Contains some functions to preprocess the data used in the visualisations.
'''
import os
import pandas as pd
from modes import MODE_TO_COLUMN

_DIR = os.path.dirname(__file__)

# Fusions de PDQ selon les réorganisations du SPVM
# PDQ 11 → 9  : https://rapportspvm2020.ca/grands-dossiers/pdq%E2%80%AF9-et-11%E2%80%AF-integrer-pour-mieux-servir/
# PDQ 22 → 21 : https://ici.radio-canada.ca/nouvelle/2150663/spvm-poste-quartier-centre-ville-police-drogue-securite
# PDQ 24 → 26 : https://spvm.qc.ca/fr/PDQ26/Actualites/14249
# PDQ 33 → 31 : https://spvm.qc.ca/fr/PDQ31/Actualites/15106
PDQ_MERGES = {'11': '9', '22': '21', '24': '26', '33': '31'}

# PDQ neighbourhood names — source: spvm.qc.ca
_pdq_noms_df = pd.read_csv(
    os.path.join(_DIR, 'assets', 'data', 'pdq_noms.csv'),
    dtype={'PDQ': str},
)
PDQ_NOMS = _pdq_noms_df.set_index('PDQ')['Quartier']


def group_by_year(dataframe):
    '''
        Groups the data by year extracted from the DATE column.

        Args:
            dataframe: The dataframe to group.
        Returns:
            The grouped dataframe with counts by year.
    '''
    dataframe['Year'] = pd.to_datetime(dataframe['DATE']).dt.year
    return dataframe.groupby('Year').size()


def prepare_pdq_data(df):
    '''
    Applies SPVM merge rules.
    '''
    df = df.dropna(subset=['PDQ']).copy()
    df['PDQ'] = df['PDQ'].astype(int).astype(str).replace(PDQ_MERGES)
    return df


def prepare_monthly_crime_data(df, categories=None):
    '''
    Returns a pivot table of crime counts per month and year.

    Args:
        df        : The raw crimes dataframe (actes-criminels.csv).
        categories: Optional list of CATEGORIE values to filter on.
    Returns:
        A DataFrame with years as index and month numbers (1-12) as columns.
    '''
    df = df.copy()
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['Annee'] = df['DATE'].dt.year
    df['Mois'] = df['DATE'].dt.month
    df = df[(df['Annee'] >= 2015) & (df['Annee'] <= 2024)]

    if categories:
        df = df[df['CATEGORIE'].isin(categories)]

    counts = df.groupby(['Annee', 'Mois']).size().reset_index(name='Total_crimes')
    pivot = counts.pivot(index='Annee', columns='Mois', values='Total_crimes').fillna(0).astype(int)
    pivot = pivot.reindex(columns=range(1, 13), fill_value=0)
    return pivot


def prepare_crime_rate_data(df):
    '''
    Computes crime counts per year and category, merged with population data
    to produce a rate per 100k inhabitants.

    Args:
        df: The raw crimes dataframe (actes-criminels.csv).
    Returns:
        A dataframe with columns: Annee, CATEGORIE, Nombre_Crimes, Population, Taux_100k.
    '''
    pop_path = os.path.join(_DIR, 'assets', 'data', 'population.csv')
    df_pop = pd.read_csv(pop_path)
    df_pop['Annee'] = df_pop['Annee'].astype(int)
    df_pop['Population'] = df_pop['Population'].astype(int)

    df = df.copy()
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['Annee'] = df['DATE'].dt.year
    df = df[df['Annee'] >= 2015]

    df_grouped = df.groupby(['Annee', 'CATEGORIE']).size().reset_index(name='Nombre_Crimes')
    df_merged = pd.merge(df_grouped, df_pop, on='Annee', how='inner')
    df_merged['Taux_100k'] = (df_merged['Nombre_Crimes'] / df_merged['Population']) * 100000

    return df_merged


def prepare_moment_journee_data(df):
    '''
    Computes crime counts per category and time of day (QUART).

    Args:
        df: The raw crimes dataframe (actes-criminels.csv).
    Returns:
        A DataFrame with columns: CATEGORIE, QUART, Nombre.
    '''
    df = df.copy()
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['Annee'] = df['DATE'].dt.year
    df = df[(df['Annee'] >= 2015)]
    df = df.dropna(subset=['QUART'])

    grouped = df.groupby(['CATEGORIE', 'QUART']).size().reset_index(name='Nombre')
    return grouped


def count_by_pdq(df, geojson):
    '''
    Returns a dataframe with crime counts per PDQ, including PDQs with zero crimes.

    Args:
        df      : crimes dataframe (already prepared via prepare_pdq_data)
        geojson : PDQ GeoJSON dict (used to get the full list of PDQs)
    '''
    all_pdqs = pd.DataFrame({
        'PDQ': [str(int(feat['properties']['PDQ'])) for feat in geojson['features']]
    })
    counts = df.groupby('PDQ').size().reset_index(name='Nombre de crimes')
    counts = all_pdqs.merge(counts, on='PDQ', how='left').fillna(0)
    counts['Nombre de crimes'] = counts['Nombre de crimes'].astype(int)
    counts['Quartier'] = counts['PDQ'].map(PDQ_NOMS)
    return counts

def prepare_tendances_data(df):
    '''
    Computes crime proportions (%) per year and category.
 
    Args:
        df: The raw crimes dataframe (actes-criminels.csv).
    Returns:
        A DataFrame with each category as columns and proportions for every year as value.
    '''
    df = df.copy()
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['Annee'] = df['DATE'].dt.year
    df = df[df['Annee'].between(2015, 2025)]
 
    pct = df.groupby(['Annee', 'CATEGORIE']).size().unstack().fillna(0)
    pct = pct.div(pct.sum(axis=1), axis=0) * 100
    return pct
