def explain_results(user_question: str, df_results, api_key: str) -> str:
    if df_results.empty:
        return "⚠️ Nessun dato trovato per questa ricerca. Prova a verificare i criteri digitati."

    client = Groq(api_key=api_key)
    model = get_active_model(client)

    # Convertiamo il dataframe in testo formattato senza richiedere 'tabulate'
    table_text = df_results.head(15).to_string(index=False)

    prompt = f"""
    Domanda dell'utente Bianco Market: "{user_question}"
    Dati estratti dal database gestionale:
    {table_text}

    Fornisci una risposta commerciale, chiara e professionale:
    - Riassumi i totali chiave (pezzi venduti, giacenze residue per sede).
    - Se l'utente chiedeva un riassortimento o un ordine fornitore, specifica le quantità consigliate.
    - Usa elenchi puntati ed emoji professionali.
    """
    
    res = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return res.choices[0].message.content
