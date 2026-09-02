import os
import pandas as pd

def load_data():
    # Ricava il percorso assoluto della cartella in cui si trova il progetto
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Costruisce i percorsi ai file
    path_articoli = os.path.join(BASE_DIR, "data", "ARTICOLI.TXT")
    path_storcar = os.path.join(BASE_DIR, "data", "STOR_CAR.TXT")
    path_sit = os.path.join(BASE_DIR, "data", "Sit_filiali.TXT")
    
    # Verifica esistenza file prima di caricarli (debug chiaro)
    if not os.path.exists(path_articoli):
        raise FileNotFoundError(f"File non trovato in: {path_articoli}. Verifica il nome preciso e la cartella 'data/'.")

    df_articoli = pd.read_csv(path_articoli, sep="\t", on_bad_lines="skip", low_memory=False)
    df_storcar = pd.read_csv(path_storcar, sep="\t", on_bad_lines="skip", low_memory=False)
    df_sit = pd.read_csv(path_sit, sep="\t", on_bad_lines="skip", low_memory=False)
    
    return df_articoli, df_storcar, df_sit
