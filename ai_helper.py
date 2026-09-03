import os
from groq import Groq
import re

SYSTEM_PROMPT = """
Sei l'assistente AI aziendale di Bianco Market. Il tuo compito è rispondere alle domande commerciali, di magazzino e di riassortimento.
Per farlo, converti le domande dell'utente in una query SQL valida per DuckDB.

SCHEMA TABELLE DISPONIBILI:
1. articoli(codice, barcode, descrizione, um, categoria, marca, fornitore, iva, prezzo_base, costo_base)
2. giacenze(codice, Magazzino, Sciacca, Menfi, Marsala, Trapani, Ragusa, Sabella, "Mazara del Vallo", "Casa Market", "Sport Market")
3. storico_movimenti(tipo_mov, data, doc_rif, codice, qta, listino, sconto, prezzo_effettivo, filiale_cod, filiale_nome)

REGOLE SQL TASSATIVE:
- Nelle vendite (tipo_mov = 'S' o 'F'), la qta nel database è negativa (es: -2). Quindi per calcolare i pezzi venduti usa SUM(ABS(qta)) oppure -SUM(qta).
- tipo_mov = 'T' indica trasferimenti interni da magazzino a filiale.
- Per il riassortimento calcola: (Venduto del periodo) - (Giacenza Attuale della filiale o di magazzino).
- Usa sempre la clausola ILIKE con il carattere percentuale per le ricerche testuali su descrizioni, marche e categorie (es: descrizione ILIKE '%PIGIAMA%').
- Fai JOIN tra articoli, giacenze e storico_movimenti usando sempre il campo 'codice'.
- Seleziona sempre le colonne più descrittive (es. codice, descrizione, qta venduta, giacenze).
- Rispondi ESCLUSIVAMENTE con il codice SQL racchiuso tra ```sql e ```. Nessun testo prima o dopo.
"""

def get_sql_query(user_question: str, api_key: str):
    client = Groq(api_key=api_key)
    
    # Lista di modelli supportati in ordine di preferenza
    models_to_try = [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ]
    
    last_error = None
    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.0
            )
            content = response.choices[0].message.content
            match = re.search(r"```sql\s*(.*?)\s*```", content, re.DOTALL)
            if match:
                return match.group(1)
            return content.strip()
        except Exception as e:
            last_error = e
            continue

    raise last_error

def explain_results(user_question: str, df_results, api_key: str):
    client = Groq(api_key=api_key)
    
    prompt = f"""
    L'utente ha chiesto: "{user_question}"
    I dati estratti dal database di Bianco Market sono i seguenti (primi 15 record):
    {df_results.head(15).to_markdown()}

    Fornisci una risposta da consulente commerciale di Bianco Market:
    - Sii chiaro, sintetico e professionale.
    - Se l'utente ha chiesto un riassortimento o giacenze, evidenzia le criticità (es. scorte esaurite o sottoscorta).
    - Usa elenchi puntati per facilitare la lettura.
    """
    
    models_to_try = [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768"
    ]
    
    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception:
            continue
            
    return "Ecco i risultati elaborati dal database in base alla tua richiesta:"
