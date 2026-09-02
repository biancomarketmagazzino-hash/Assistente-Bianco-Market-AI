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
# UTILITY PER RICERCA FILE E DECODIFICA SAFE
# ==============================================================================

def trova_file_case_insensitive(directory, nome_target):
    """Cerca un file nella cartella ignorando maiuscole e minuscole."""
    if not os.path.exists(directory):
        raise FileNotFoundError(f"La cartella '{directory}' non esiste sul server.")
    
    file_presenti = os.listdir(directory)
    for file in file_presenti:
        if file.lower() == nome_target.lower():
            return os.path.join(directory, file)
            
    raise FileNotFoundError(
        f"File '{nome_target}' non trovato in '{directory}'. "
        f"File presenti nella cartella: {file_presenti}"
    )


def read_csv_safe(path_file, sep="\t"):
    """
    Legge un file CSV/TXT provando prima la codifica 'latin1' (gestionali Windows)
    e poi 'cp1252' o 'utf-8' per prevenire UnicodeDecodeError.
    """
    for enc in ["latin1", "cp1252", "utf-8", "iso-8859-1"]:
        try:
            df = pd.read_csv(
                path_file,
                sep=sep,
                on_bad_lines="skip",
                low_memory=False,
                dtype=str,
                encoding=enc
            )
            df.columns = df.columns.str.strip()
            return df
        except (UnicodeDecodeError, Exception):
            continue
            
    # Se tutte le codifiche falliscono, forza la lettura ignorando gli errori di carattere
    return pd.read_csv(
        path_file,
        sep=sep,
        on_bad_lines="skip",
        low_memory=False,
        dtype=str,
        encoding="latin1",
        encoding_errors="ignore"
    )


# ==============================================================================
# FUNZIONE PRINCIPALE DI CARICAMENTO DATI
# ==============================================================================

def load_data():
    """
    Carica e pulisce i 3 file gestionali dalla cartella 'data/'.
    Ritorna i tre DataFrame pronti per Streamlit e per il Chatbot AI.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # Ricerca dinamica dei file ignorando Maiuscole/Minuscole
    path_articoli = trova_file_case_insensitive(DATA_DIR, "ARTICOLI.TXT")
    path_storcar = trova_file_case_insensitive(DATA_DIR, "STOR_CAR.TXT")
    path_sit = trova_file_case_insensitive(DATA_DIR, "Sit_filiali.TXT")

    # 1. Caricamento Anagrafica Articoli
    df_articoli = read_csv_safe(path_articoli)

    # 2. Caricamento Storico Movimenti (storcar)
    df_storcar = read_csv_safe(path_storcar)
    
    # Conversione colonne numeriche (gestisce anche la virgola decimale italiana)
    for col_num in ['QTA', 'LIST./COSTO AGG', 'SCONTO']:
        if col_num in df_storcar.columns:
            df_storcar[col_num] = pd.to_numeric(
                df_storcar[col_num].str.replace(',', '.'), 
                errors='coerce'
            ).fillna(0)

    # Mappatura Codice Filiale -> Nome Filiale
    if 'FILIALE' in df_storcar.columns:
        df_storcar['FILIALE_NOME'] = (
            df_storcar['FILIALE']
            .astype(str)
            .str.zfill(2)
            .map(FILIALI_MAP)
            .fillna('Sconosciuta')
        )

    # 3. Caricamento Giacenze e Rilevazione Filiali (sit_filiali)
    df_sit = read_csv_safe(path_sit)
    
    # Rinomina colonne C_01...C_10 con i nomi delle filiali
    df_sit.rename(columns=COL_FILIALI_MAP, inplace=True)

    # Conversione colonne giacenza in valori numerici
    for nome_filiale in COL_FILIALI_MAP.values():
        if nome_filiale in df_sit.columns:
            df_sit[nome_filiale] = pd.to_numeric(
                df_sit[nome_filiale].astype(str).str.replace(',', '.'), 
                errors='coerce'
            ).fillna(0)

    return df_articoli, df_storcar, df_sit


# ==============================================================================
# FUNZIONE HELPER PER IL CHATBOT AI
# ==============================================================================

def calcola_venduto_articolo(df_storcar, codice_articolo=None, filiale_nome=None):
    """
    Filtra le vendite effettive (movimenti S ed F) escludendo carichi (C).
    """
    df_vendite = df_storcar[df_storcar['TIPO'].isin(['S', 'F'])].copy()
    
    if codice_articolo:
        df_vendite = df_vendite[df_vendite['CODICE'] == str(codice_articolo)]
        
    if filiale_nome:
        df_vendite = df_vendite[df_vendite['FILIALE_NOME'] == filiale_nome]
        
    return df_vendite
