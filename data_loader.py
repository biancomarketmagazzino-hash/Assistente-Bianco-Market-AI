import os
import pandas as pd

FILIALI_MAP = {
    '00': 'Magazzino', '01': 'Menfi', '02': 'Mazara del Vallo', '03': 'Marsala',
    '04': 'Casa Market', '05': 'Sabella', '06': 'Sciacca', '07': 'Ragusa',
    '08': 'Sport Market', '09': 'Trapani'
}

COL_FILIALI_MAP = {
    'C_01': 'Magazzino', 'C_02': 'Sciacca', 'C_03': 'Menfi', 'C_04': 'Marsala',
    'C_05': 'Trapani', 'C_06': 'Ragusa', 'C_07': 'Sabella', 'C_08': 'Mazara del Vallo',
    'C_09': 'Casa Market', 'C_10': 'Sport Market'
}

def trova_file_case_insensitive(directory, nome_target):
    """Cerca un file nella cartella ignorando maiuscole/minuscole."""
    if not os.path.exists(directory):
        raise FileNotFoundError(f"La cartella '{directory}' non esiste sul server GitHub.")
    
    file_presenti = os.listdir(directory)
    for file in file_presenti:
        if file.lower() == nome_target.lower():
            return os.path.join(directory, file)
            
    raise FileNotFoundError(
        f"File '{nome_target}' non trovato in '{directory}'. "
        f"File effettivamente presenti nella cartella: {file_presenti}"
    )

def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")

    # Ricerca dinamica dei file ignorando Maiuscole/Minuscole
    path_articoli = trova_file_case_insensitive(DATA_DIR, "ARTICOLI.TXT")
    path_storcar = trova_file_case_insensitive(DATA_DIR, "STOR_CAR.TXT")
    path_sit = trova_file_case_insensitive(DATA_DIR, "Sit_filiali.TXT")

    # 1. Articoli
    df_articoli = pd.read_csv(path_articoli, sep="\t", on_bad_lines="skip", low_memory=False, dtype=str)
    df_articoli.columns = df_articoli.columns.str.strip()

    # 2. Storcar
    df_storcar = pd.read_csv(path_storcar, sep="\t", on_bad_lines="skip", low_memory=False, dtype=str)
    df_storcar.columns = df_storcar.columns.str.strip()
    
    for col_num in ['QTA', 'LIST./COSTO AGG', 'SCONTO']:
        if col_num in df_storcar.columns:
            df_storcar[col_num] = pd.to_numeric(df_storcar[col_num].str.replace(',', '.'), errors='coerce').fillna(0)

    if 'FILIALE' in df_storcar.columns:
        df_storcar['FILIALE_NOME'] = df_storcar['FILIALE'].str.zfill(2).map(FILIALI_MAP).fillna('Sconosciuta')

    # 3. Sit Filiali
    df_sit = pd.read_csv(path_sit, sep="\t", on_bad_lines="skip", low_memory=False, dtype=str)
    df_sit.columns = df_sit.columns.str.strip()
    df_sit.rename(columns=COL_FILIALI_MAP, inplace=True)

    for nome_filiale in COL_FILIALI_MAP.values():
        if nome_filiale in df_sit.columns:
            df_sit[nome_filiale] = pd.to_numeric(df_sit[nome_filiale].str.replace(',', '.'), errors='coerce').fillna(0)

    return df_articoli, df_storcar, df_sit
