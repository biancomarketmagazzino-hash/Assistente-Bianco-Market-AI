import os
from groq import Groq
import re

SYSTEM_PROMPT = """
Sei l'assistente AI aziendale di Bianco Market. Il tuo compito è rispondere alle domande commerciali, di magazzino e di riassortimento.
Per farlo, converti la domanda dell'utente in una query SQL compatibile con DuckDB.

SCHEMA DEL DATABASE:
1. articoli(codice, barcode, descrizione, um, categoria, marca, fornitore, iva, prezzo_base, costo_base)
2. giacenze(codice, Magazzino, Sciacca, Menfi, Marsala, Trapani, Ragusa, Sabella, "Mazara del Vallo", "Casa Market", "Sport Market")
   IMPORTANTE: Le colonne con spazi come "Mazara del Vallo", "Casa Market", "Sport Market" devono avere i doppi apici!
3. storico_movimenti(tipo_mov, data, doc_rif, codice, qta, listino, sconto, prezzo_effettivo, filiale_cod, filiale_nome)

REGOLE SQL TASSATIVE:
- Nelle vendite (tipo_mov = 'S' o 'F'), la quantità (qta) è negativa. Per calcolare i pezzi venduti usa SEMPRE: SUM(ABS(qta)) oppure -SUM(qta).
- tipo_mov = 'T' indica trasferimenti interni tra Magazzino e Filiali.
- Se l'utente chiede il "riassortimento", confronta il venduto (SUM(ABS(qta))) con la giacenza attuale.
- Usa sempre la clausola ILIKE per le ricerche testuali con il carattere jolly % (es: a.descrizione ILIKE '%PIGIAMA%').
- Fai JOIN tra le tabelle usando il campo 'codice'.
- Quando usi GROUP BY, includi tutte le colonne non aggregate presenti nella SELECT.
- Rispondi ESCLUSIVAMENTE con il codice SQL puro, senza commenti, spiegazioni o saluti. Racchiudilo tra ```sql e ```.
"""

def clean_sql(raw_text: str) -> str:
    """Estrae solo la stringa SQL pulita."""
    match = re.search(r"```(?:sql)?\s*(.*?)\s*```", raw_text, re.DOTALL | re.IGNORECASE)
    if match:
        query = match.group(1).strip()
    else:
        query = raw_text.strip()
    # Rimuove eventuali punti e virgola finali o spazi superflui
    return query.rstrip(';')

def get_sql_query(user_question: str, api_key: str) -> str:
    client = Groq(api_key=api_key)
    
    # Solo modelli attivi su Groq Cloud
    models = ["llama-3.1-8b-instant", "gemma2-9b-it"]
    
    last_err = None
    for model in models:
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.0
            )
            raw_content = res.choices[0].message.content
            return clean_sql(raw_content)
        except Exception as e:
            last_err = e
            continue
            
    raise last_err

def explain_results(user_question: str, df_results, api_key: str) -> str:
    client = Groq(api_key=api_key)
    
    # Se il dataframe è vuoto, rispondiamo subito
    if df_results.empty:
        return "⚠️ La ricerca non ha prodotto risultati. Verifica se i termini usati (descrizione, filiale o codice) sono corretti."

    prompt = f"""
    Domanda dell'utente Bianco Market: "{user_question}"
    Dati estratti dal database (primi record):
    {df_results.head(15).to_markdown()}

    Fornisci una risposta commerciale, chiara e professionale:
    - Evidenzia i numeri principali (pezzi venduti, scorte rimaste, filiali coinvolte).
    - Se l'utente chiedeva un riassortimento, indica chiaramente cosa ordinare con urgenza.
    - Usa elenchi puntati per facilitare la lettura.
    """
    
    models = ["llama-3.1-8b-instant", "gemma2-9b-it"]
    for model in models:
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return res.choices[0].message.content
        except Exception:
            continue

    return "Ecco i dati estratti in base alla tua richiesta:"
