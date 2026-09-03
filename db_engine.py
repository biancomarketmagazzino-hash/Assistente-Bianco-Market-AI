import duckdb
import pandas as pd
import os

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

def find_file(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(base_dir, "data", filename),
        os.path.join(base_dir, filename),
        os.path.join(base_dir, "data", filename.lower()),
        os.path.join(base_dir, filename.lower()),
        os.path.join(base_dir, "data", filename.upper()),
        os.path.join(base_dir, filename.upper()),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"File {filename} non trovato.")

def parse_data(art_source, sit_source, stor_source):
    con = duckdb.connect(database=':memory:')

    # 1. ARTICOLI
    df_art = pd.read_csv(art_source, sep='\t', header=None, dtype=str, on_bad_lines='skip')
    df_art = df_art.iloc[:, [0, 1, 2, 3, 4, 5, 6, 8, 9, 21]]
    df_art.columns = ['codice', 'barcode', 'descrizione', 'um', 'categoria', 'marca', 'fornitore', 'iva', 'prezzo_base', 'costo_base']
    df_art['prezzo_base'] = pd.to_numeric(df_art['prezzo_base'], errors='coerce').fillna(0)
    df_art['costo_base'] = pd.to_numeric(df_art['costo_base'], errors='coerce').fillna(0)
    con.register('articoli', df_art)

    # 2. SIT_FILIALI
    df_sit = pd.read_csv(sit_source, sep='\t', header=None, dtype=str, on_bad_lines='skip')
    cols_idx = [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    df_sit = df_sit.iloc[:, cols_idx]
    df_sit.columns = ['codice', 'Magazzino', 'Sciacca', 'Menfi', 'Marsala', 'Trapani', 'Ragusa', 'Sabella', 'Mazara del Vallo', 'Casa Market', 'Sport Market']
    for col in df_sit.columns[1:]:
        df_sit[col] = pd.to_numeric(df_sit[col], errors='coerce').fillna(0)
    con.register('giacenze', df_sit)

    # 3. STOR_CAR
    df_stor = pd.read_csv(stor_source, sep='\t', header=None, dtype=str, on_bad_lines='skip')
    df_stor = df_stor.iloc[:, [0, 1, 2, 4, 5, 6, 7, 8, 23]]
    df_stor.columns = ['tipo_mov', 'data', 'doc_rif', 'codice', 'qta', 'listino', 'sconto', 'prezzo_effettivo', 'filiale_cod']
    df_stor = df_stor[df_stor['tipo_mov'].isin(['S', 'F', 'T'])].copy()
    df_stor['qta'] = pd.to_numeric(df_stor['qta'], errors='coerce').fillna(0)
    df_stor['sconto'] = pd.to_numeric(df_stor['sconto'], errors='coerce').fillna(0)
    df_stor['prezzo_effettivo'] = pd.to_numeric(df_stor['prezzo_effettivo'], errors='coerce').fillna(0)
    df_stor['filiale_nome'] = df_stor['filiale_cod'].map(FILIALI_MAP).fillna('Altro')
    con.register('storico_movimenti', df_stor)

    return con

def load_data():
    path_articoli = find_file("ARTICOLI.TXT")
    path_sit = find_file("Sit_filiali.TXT")
    path_stor = find_file("STOR_CAR.txt")
    return parse_data(path_articoli, path_sit, path_stor)

def load_data_from_uploads(file_art, file_sit, file_stor):
    return parse_data(file_art, file_sit, file_stor)
