import os
from groq import Groq
import re

SYSTEM_PROMPT = """
Sei l'assistente AI aziendale di Bianco Market. Il tuo compito è rispondere alle domande commerciali, di magazzino e di riassortimento.
Per farlo, converti la domanda dell'utente in una query SQL valida per DuckDB.

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
- Rispondi ESCLUSIVAMENTE con il codice SQL puro, senza commenti né spiegazioni. Racchiudilo tra ```sql e ```.
"""

def get_active_model(client: Groq) -> str:
    """Interroga l'API di Groq e seleziona il miglior modello attivo disponibile."""
    try:
        model_list = client.models.list()
        active_ids = [m.id for m in model_list.data]
        
        # Ordine di preferenza per modelli intelligenti e veloci
        preferences = [
            "llama-3.3-70b-versatile",
            "llama-3.2-90b-text-preview",
            "llama-3.2-11b-text-preview",
            "llama-3.2-3b-preview",
            "llama-3.2-1b-preview",
            "llama-3.1-8b-instant",
            "llama3-70b-8192",
            "llama3-8b-8192"
        ]
        
        for pref in preferences:
            if pref in active_ids:
                return pref
                
        # Se nessuno dei preferiti è nella lista, usa il primo disponibile che non sia audio/whisper
        text_models = [m_id for m_id in active_ids if "whisper" not in m_id.lower()]
        if text_models:
            return text_models[0]
            
    except Exception:
        pass
        
    # Fallback standard
    return "llama-3.1-8b-instant"

def clean_sql(raw_text: str) -> str:
    match = re.search(r"```(?:sql)?\s*(.*?)\s*```", raw_text, re.DOTALL | re.IGNORECASE)
    if match:
        query = match.group(1).strip()
    else:
        query = raw_text.strip()
    return query.rstrip(';')

def get_sql_query(user_question: str, api_key: str) -> str:
    client = Groq(api_key=api_key)
    model = get_active_model(client)
    
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

def explain_results(user_question: str, df_results, api_key: str) -> str:
    if df_results.empty:
        return "⚠️ Nessun dato trovato per questa ricerca. Prova a verificare i criteri digitati."

    client = Groq(api_key=api_key)
    model = get_active_model(client)

    prompt = f"""
    Domanda dell'utente Bianco Market: "{user_question}"
    Dati estratti dal database gestionale:
    {df_results.head(15).to_markdown()}

    Fornisci una risposta commerciale, chiara e professionale:
    - Riassumi i totali chiave (pezzi venduti, giacenze residue per sede).
    - Se l'utente chiedeva un riassortimento o un ordine fornitore, specifica le quantità consigliate.
    - Usa elenchi puntati.
    """
    
    res = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return res.choices[0].message.content
