import os
from groq import Groq
import re

SYSTEM_PROMPT = """
Sei l'assistente AI aziendale di Bianco Market. Il tuo compito è rispondere alle domande commerciali, di magazzino e di riassortimento.
Per farlo, converti le domande dell'utente in una query SQL valida per DuckDB.

SCHEMA TABELLE:
1. articoli(codice, barcode, descrizione, um, categoria, marca, fornitore, iva, prezzo_base, costo_base)
2. giacenze(codice, Magazzino, Sciacca, Menfi, Marsala, Trapani, Ragusa, Sabella, "Mazara del Vallo", "Casa Market", "Sport Market")
3. storico_movimenti(tipo_mov, data, doc_rif, codice, qta, listino, sconto, prezzo_effettivo, filiale_cod, filiale_nome)

REGOLE IMPORTANTI:
- tipo_mov = 'S' o 'F' indicano VENDITE. La qta nelle vendite è negativa: per ottenere il venduto reale calcola SUM(ABS(qta)) o -SUM(qta).
- tipo_mov = 'T' indica TRASFERIMENTI interni tra Magazzino e Filiali.
- Se l'utente chiede il "riassortimento", calcola: (Vendite del periodo) - (Giacenza Attuale della filiale o di magazzino). Se positivo, suggerisci l'ordine.
- Usa sempre la clausola ILIKE per le ricerche testuali su descrizioni, marche e categorie (es: descrizione ILIKE '%PIGIAMA%').
- Rispondi ESCLUSIVAMENTE con il blocco SQL racchiuso tra ```sql e ```. Nessun preambolo.
"""

def get_sql_query(user_question: str, api_key: str):
    client = Groq(api_key=api_key)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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

def explain_results(user_question: str, df_results, api_key: str):
    client = Groq(api_key=api_key)
    prompt = f"""
    L'utente ha chiesto: "{user_question}"
    I dati estratti dal database di Bianco Market sono i seguenti (primi record):
    {df_results.head(15).to_markdown()}

    Fornisci una risposta da consulente commerciale:
    - Sii preciso, chiaro ed esaustivo.
    - Se si tratta di riassortimento, evidenzia gli articoli in rottura di stock o da ordinare subito.
    - Usa elenchi puntati ed emoji professionali.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content
