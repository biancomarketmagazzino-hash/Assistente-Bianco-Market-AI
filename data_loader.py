import os
import pandas as pd

# ==============================================================================
# MAPPATURA COSTANTI FILIALI E COLONNE
# ==============================================================================

# Mappatura dei codici numerici del file storcar
FILIALI_MAP = {
    '00': 'Magazzino',
    '01': 'Menfi',
    '02': 'Mazara del Vallo',
    '03': 'Marsala',
    '04': 'Casa Market',
    '05': 'Sabella',
    '06': 'Sciacca',
    '07': 'Ragusa',
    '08': 'Sport Market',
    '09': 'Trapani'
}

# Mappatura delle colonne della matrice sit_filiali
COL_FILIALI_MAP = {
    'C_01': 'Magazzino',
    'C_02': 'Sciacca',
    'C_03': 'Menfi',
    'C_04': 'Marsala',
    'C_05': 'Trapani',
    'C_06': 'Ragusa',
    'C_07': 'Sabella',
    'C_08': 'Mazara del Vallo',
    'C_09': 'Casa Market',
    'C_10': 'Sport Market'
}


# ==============================================================================
# FUNZIONE DI CARICAMENTO E PRE-ELABORAZIONE DATI
# ==============================================================================

def load_data():
    """
    Carica e pulisce i file gestionali dalla cartella 'data/'.
    Ritorna i tre DataFrame pronti per l'analisi e il chatbot AI.
    """
    # Determinazione dinamica del percorso root del progetto
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # Percorsi dei singoli file
    path_articoli = os.path.join(DATA_DIR, "ARTICOLI.TXT")
    path_storcar = os.path.join(DATA_DIR, "STOR_CAR.TXT")
    path_sit = os.path.join(DATA_DIR, "Sit_filiali.TXT")

    # Controllo preventivo dell'esistenza dei file
    for p in [path_articoli, path_storcar, path_sit]:
        if not os.path.exists(p):
            raise FileNotFoundError(
                f"File non trovato nel percorso: '{p}'. "
                f"Verifica che i file siano presenti dentro la cartella 'data/' e che il nome sia corretto."
            )

    # --------------------------------------------------------------------------
    # 1. Caricamento Anagrafica Articoli
    # --------------------------------------------------------------------------
    df_articoli = pd.read_csv(
        path_articoli,
        sep="\t",
        on_bad_lines="skip",
        low_memory=False,
        dtype=str
    )
    # Pulizia nomi colonne da spazi bianchi extra
    df_articoli.columns = df_articoli.columns.str.strip()

    # --------------------------------------------------------------------------
    # 2. Caricamento Storico Movimenti (storcar)
    # --------------------------------------------------------------------------
    df_storcar = pd.read_csv(
        path_storcar,
        sep="\t",
        on_bad_lines="skip",
        low_memory=False,
        dtype=str
    )
    df_storcar.columns = df_storcar.columns.str.strip()

    # Conversione campi numerici per il calcolo di venduto e trasferimenti
    for col_num in ['QTA', 'LIST./COSTO AGG', 'SCONTO']:
        if col_num in df_storcar.columns:
            df_storcar[col_num] = pd.to_numeric(
                df_storcar[col_num].str.replace(',', '.'), 
                errors='coerce'
            ).fillna(0)

    # Mappatura dei nomi filiale nel file storcar
    if 'FILIALE' in df_storcar.columns:
        df_storcar['FILIALE_NOME'] = df_storcar['FILIALE'].str.zfill(2).map(FILIALI_MAP).fillna('Sconosciuta')

    # --------------------------------------------------------------------------
    # 3. Caricamento Giacenze e Rilevazioni Filiali (sit_filiali)
    # --------------------------------------------------------------------------
    df_sit = pd.read_csv(
        path_sit,
        sep="\t",
        on_bad_lines="skip",
        low_memory=False,
        dtype=str
    )
    df_sit.columns = df_sit.columns.str.strip()

    # Rinomina colonne C_01...C_10 nei nomi reali delle Filiali per facilità d'uso
    df_sit.rename(columns=COL_FILIALI_MAP, inplace=True)

    # Converti colonne giacenza in formato numerico
    for nome_filiale in COL_FILIALI_MAP.values():
        if nome_filiale in df_sit.columns:
            df_sit[nome_filiale] = pd.to_numeric(
                df_sit[nome_filiale].str.replace(',', '.'), 
                errors='coerce'
            ).fillna(0)

    return df_articoli, df_storcar, df_sit


# ==============================================================================
# FUNZIONI UTILI PER L'ANALISI DEI DATI / CHATBOT AI
# ==============================================================================

def calcola_venduto_articolo(df_storcar, codice_articolo=None, filiale_nome=None):
    """
    Filtra le vendite effettivi (movimenti S ed F) escludendo carichi (C).
    """
    df_vendite = df_storcar[df_storcar['TIPO'].isin(['S', 'F'])].copy()
    
    if codice_articolo:
        df_vendite = df_vendite[df_vendite['CODICE'] == str(codice_articolo)]
        
    if filiale_nome:
        df_vendite = df_vendite[df_vendite['FILIALE_NOME'] == filiale_nome]
        
    return df_vendite
