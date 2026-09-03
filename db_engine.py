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

def load_data():
    con = duckdb.connect(database=':memory:')

    # 1. Carica ARTICOLI
    # Struttura fissa estratta dai TXT
    df_art = pd.read_csv('data/ARTICOLI.TXT', sep='\t', header=None, dtype=str)
    df_art = df_art.iloc[:, [0, 1, 2, 3, 4, 5, 6, 8, 9, 21]]
    df_art.columns = ['codice', 'barcode', 'descrizione', 'um', 'categoria', 'marca', 'fornitore', 'iva', 'prezzo_base', 'costo_base']
    df_art['prezzo_base'] = pd.to_numeric(df_art['prezzo_base'], errors='coerce').fillna(0)
    df_art['costo_base'] = pd.to_numeric(df_art['costo_base'], errors='coerce').fillna(0)
    con.register('articoli', df_art)

    # 2. Carica SIT_FILIALI
    df_sit = pd.read_csv('data/Sit_filiali.TXT', sep='\t', header=None, dtype=str)
    # Mappatura colonne: Codice, poi le 10 filiali alternate a 0
    # C_01 Magazzino (1), C_02 Sciacca (3), C_03 Menfi (5), C_04 Marsala (7), C_05 Trapani (9),
    # C_06 Ragusa (11), C_07 Sabella (13), C_08 Mazara (15), C_09 Casa Market (17), C_10 Sport Market (19)
    cols_idx = [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    df_sit = df_sit.iloc[:, cols_idx]
    df_sit.columns = ['codice', 'Magazzino', 'Sciacca', 'Menfi', 'Marsala', 'Trapani', 'Ragusa', 'Sabella', 'Mazara del Vallo', 'Casa Market', 'Sport Market']
    
    # Rendi numeriche le giacenze
    for col in df_sit.columns[1:]:
        df_sit[col] = pd.to_numeric(df_sit[col], errors='coerce').fillna(0)
        
    con.register('giacenze', df_sit)

    # 3. Carica STOR_CAR
    df_stor = pd.read_csv('data/STOR_CAR.txt', sep='\t', header=None, dtype=str)
    # Prendiamo solo i campi chiave
    # Tipo, Data, Rif, Causale, Codice, Qta, Listino, Sconto, PrezzoEffettivo, Marca, Filiale (col 23 circa)
    df_stor = df_stor.iloc[:, [0, 1, 2, 4, 5, 6, 7, 8, 23]]
    df_stor.columns = ['tipo_mov', 'data', 'doc_rif', 'codice', 'qta', 'listino', 'sconto', 'prezzo_effettivo', 'filiale_cod']
    
    # Filtra: Escludi 'C' (carichi fornitore)
    df_stor = df_stor[df_stor['tipo_mov'].isin(['S', 'F', 'T'])].copy()
    
    df_stor['qta'] = pd.to_numeric(df_stor['qta'], errors='coerce').fillna(0)
    df_stor['sconto'] = pd.to_numeric(df_stor['sconto'], errors='coerce').fillna(0)
    df_stor['prezzo_effettivo'] = pd.to_numeric(df_stor['prezzo_effettivo'], errors='coerce').fillna(0)
    df_stor['filiale_nome'] = df_stor['filiale_cod'].map(FILIALI_MAP).fillna('Altro')
    
    con.register('storico_movimenti', df_stor)

    return con
