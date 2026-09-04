import os
import io
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Bianco Market - Assistant & Inventory AI",
    layout="wide"
)

# ---------------------------------------------------------
# MAPPATURA UFFICIALE FILIALI E CATEGORIE
# ---------------------------------------------------------
MAPPA_FILIALI = {
    'C_01': 'Magazzino',
    'C_02': 'Sciacca',
    'C_03': 'Menfi',
    'C_04': 'Marsala',
    'C_05': 'Trapani',
    'C_06': 'Ragusa',
    'C_07': 'Sabella',
    'C_08': 'Mazara',
    'C_09': 'Casa Market',
    'C_10': 'Sport Market'
}

CATEGORIE_L1 = [
    "ACCESSORI", "ARREDO BAGNO", "ARREDO CASA", "ARREDO GIARDINO", "ARTICOLI DA REGALO",
    "BIANCHERIA BAGNO", "BIANCHERIA CASA", "BIANCHERIA INTIMA", "BIANCHERIA LETTO",
    "CERAMICA", "CERE", "COLLANTERIA", "CONFEZIONE", "CORSETTERIA", "CUCINA",
    "ELETTRODOMESTICI", "ESENTE IVA", "GIOCATTOLI", "IGIENE CASA", "IGIENE PERSONA",
    "INFANZIA", "IVA 10", "IVA 5", "MAGLIERIA", "MARE", "MATERASSI", "MUTANDERIA",
    "NATALIZIO", "PARTY", "PENTOLAME", "PIGIAMERIA", "PLASTICA", "PRODOTTI PER ANIMALI",
    "REPARTO ANIMALI", "REPARTO22", "REPARTO37", "SCUOLA", "TAPPETI", "TEMPO LIBERO", "TENDE"
]

CATEGORIE_L2 = [
    "ABITO", "ACCAPPATOIO", "ASCIUGAMANI", "BARATTOLO", "BASTONE TENDA", "BAVETTE",
    "BERRETTO", "BODY", "BORRACCE", "BORSA MARE", "BORSONE", "BOXER", "BRALETTE",
    "BRASILIANA", "CALCIO", "CALZA CORTA", "CALZA LUNGA", "CAMICE LAVORO", "CAMICIA",
    "CAMICIA DA NOTTE", "CANOTTA", "CAPPELLO", "CARTA REGALO", "CENTRI 3 PEZZI",
    "CENTROTAVOLA", "CERATA AL METRO", "CIABATTA", "CIOTOLA", "COLLANT",
    "COMPLETINO CALCIO", "COMPLETO", "COMPLETO LENZUOLA", "COORDINATO", "COPERTA",
    "COPERTINA", "COPPIA ASCIUGAMANI", "COPRIABITO", "COPRIASSE", "COPRICOSTUMI",
    "COPRIDIVANO", "COPRIFORNELLI", "COPRIFORNO", "COPRILAVATRICE",
    "COPRILETTI", "COPRIMACCHIA", "COPRIMATERASSO", "COPRIPIUMINO", "COPRIPOLTRONA",
    "COPRIRETE", "COPRISEDIE", "COPRISEDUTE", "COPRITAVOLA", "COPRITUTTO", "COSTUMI",
    "CUFFIA", "CULOTTA", "CUSCINO", "DIETROVETRI", "FANTASMINI", "FASCIA", "FAZZOLETTI",
    "FEDERE", "FELPE", "FERMAPORTA", "FERMATENDA", "GIACCA", "GIACCA A VENTO",
    "GIUBBOTTI", "GONNA", "GREMBIULE", "GUAINA", "GUANCIALE", "GUANTI", "GUANTO DA FORNO",
    "HOTEL", "IMBOTTITURA", "INFRADITO", "JEANS", "JOGGER", "KIMONO", "LANTERNE",
    "LAVETTE", "LEGGINGS", "LENZUOLO", "LONETA", "LUPETTO", "MAGLIA", "MAGLIONE",
    "MATERASSO", "MINICALZA", "MUTANDONE", "OSPITE", "PALLONE", "PANCA", "PANCERA",
    "PANTALONI", "PANTOFOLE", "PARURE BAGNO", "PASSATOIA", "PIGIAMA", "PIUMINO",
    "PLAID", "POLO", "PONCHO", "PORTABIANCHERIA", "POUF", "PRESINE", "QUADRATO NEONATO",
    "QUARTER", "REGGISENO", "RETE", "SALVAPIEDE", "SCALDASONNO", "SCALDOTTO", "SCARPE",
    "SCIARPE", "SET ASCIUGAMANI", "SHORT", "SLIP", "SLIP MAXI", "SLIP MIDI", "SLIP PIZZO",
    "SLIP VITA ALTA", "SLIP VITA BASSA", "SMANICATO", "SNEAKERS", "SOTTOGONNA",
    "SOTTOVESTE", "SPEZZATO", "STROFINACCI", "T-SHIRT", "TAPPETO", "TAZZE", "TELO",
    "TENDA DOCCIA", "TENNIS", "TOP", "TOPPER", "TOVAGLIA", "TRAPUNTE", "TRAPUNTINI",
    "TRIS SPUGNA", "TUTE", "TUTINA", "VESTAGLIA", "VESTITINO", "ZANZARIERE"
]

CATEGORIE_L3 = [
    "1 PIAZZA E MEZZO", "1 POSTO", "2 POSTI", "3 POSTI", "4 POSTI", "BAMBINI",
    "BIMBA", "BIMBO", "CULLA", "DONNA", "DONNA CAL", "KING SIZE", "MATRIMONIALE",
    "NEONATA", "NEONATI", "NEONATO", "RAGAZZA", "RAGAZZI", "RAGAZZO", "ROTONDO",
    "SINGOLO", "UNISEX", "UOMO", "UOMO CAL", "X12", "X18", "X24", "X4", "X6", "X8"
]

CATEGORIE_L4 = [
    "ALOE VERA", "BIELASTICO", "C/COTONE", "CINIGLIA", "CORAL", "COTONE", "COTONE U/T",
    "CUSCINO ARREDO", "DAMASCO", "FELPATA", "FIBRA", "FILO DI SCOZIA", "FIOCCO MEMORY",
    "FLANELLA", "GARZA", "GOBELIN", "HOTELLERIA", "LANA", "LINO", "MEMORY",
    "MICROFIBRA", "NIDO APE", "P.MILANO", "PELLICCIA", "PERCALLE", "PILE", "POP CORN",
    "PVC", "RASO", "SEAMLESS", "SETA", "SPUGNA", "TRAPUNTATO", "TRIACETATO", "VELVET", "VISCOSA"
]

# ---------------------------------------------------------
# UTILITY PER RICERCA FILE CSV
# ---------------------------------------------------------
def find_file(filename, possible_dirs=None):
    if possible_dirs is None:
        possible_dirs = ["data/current", "data", "."]
        
    for d in possible_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower() == filename.lower():
                    return os.path.join(d, f)
    return None

# ---------------------------------------------------------
# CARICAMENTO DATI CACHATO
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def load_articoli():
    path = find_file("ARTICOLI.csv")
    if not path:
        return pd.DataFrame()
    
    df = pd.read_csv(path, encoding='latin1', on_bad_lines='skip', dtype=str)
    
    rename_dict = {
        'CODICE_CAT': 'CAT_L1_REPARTO',
        'GRUPPO': 'CAT_L2_ARTICOLO',
        'SOTTOGRUPPO': 'CAT_L3_GENERE',
        'CAT_LEVEL_4': 'CAT_L4_TESSUTO'
    }
    df = df.rename(columns=rename_dict)
    
    text_cols = ['DESCRIZION', 'CODICE_FOR', 'CODICE_MAR', 'CAT_L1_REPARTO', 'CAT_L2_ARTICOLO', 'CAT_L3_GENERE', 'CAT_L4_TESSUTO']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna('-').str.strip()
            
    return df

@st.cache_data(ttl=3600)
def load_giacenze():
    path = find_file("Sit_filiali.csv")
    if not path:
        return pd.DataFrame()
    
    df = pd.read_csv(path, encoding='latin1', on_bad_lines='skip', dtype=str)
    
    num_cols = [c for c in df.columns if c != 'CODICE_ART']
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    return df

@st.cache_data(ttl=3600)
def load_vendite():
    path = find_file("VENDITE.csv") or find_file("Venduto.csv")
    if not path:
        return pd.DataFrame()
    
    df = pd.read_csv(path, encoding='latin1', on_bad_lines='skip', dtype=str)
    if 'DATA' in df.columns:
        df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce')
    if 'QUANTITA' in df.columns:
        df['QUANTITA'] = pd.to_numeric(df['QUANTITA'], errors='coerce').fillna(0).astype(int)
    return df

# ---------------------------------------------------------
# FUNZIONE PER ESPORTAZIONE EXCEL (XLSX)
# ---------------------------------------------------------
def convert_df_to_excel(df, sheet_name='Data'):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

# ---------------------------------------------------------
# CARICAMENTO E PREPARAZIONE DATI
# ---------------------------------------------------------
st.title("🛍️ Bianco Market - Gestione Esistenze & Ordini")

df_art = load_articoli()
df_giac = load_giacenze()
df_vend = load_vendite()

if df_art.empty or df_giac.empty:
    st.warning("⚠️ Impossibile caricare `ARTICOLI.csv` o `Sit_filiali.csv`.")
    st.stop()

df_master = pd.merge(df_art, df_giac, on='CODICE_ART', how='left')

# ---------------------------------------------------------
# FUNZIONE PER APPLICARE FILTRI
# ---------------------------------------------------------
def applica_filtri_catalogo(df, search, l1, l2, l3, l4, forn, marca):
    df_f = df.copy()
    if search.strip():
        words = search.strip().split()
        combined_text = df_f['DESCRIZION'].fillna('') + ' ' + df_f['CODICE_ART'].fillna('')
        mask = pd.Series(True, index=df_f.index)
        for word in words:
            mask = mask & combined_text.str.contains(word, case=False, regex=False)
        df_f = df_f[mask]

    if l1 and 'CAT_L1_REPARTO' in df_f.columns:
        df_f = df_f[df_f['CAT_L1_REPARTO'].isin(l1)]
    if l2 and 'CAT_L2_ARTICOLO' in df_f.columns:
        df_f = df_f[df_f['CAT_L2_ARTICOLO'].isin(l2)]
    if l3 and 'CAT_L3_GENERE' in df_f.columns:
        df_f = df_f[df_f['CAT_L3_GENERE'].isin(l3)]
    if l4 and 'CAT_L4_TESSUTO' in df_f.columns:
        df_f = df_f[df_f['CAT_L4_TESSUTO'].isin(l4)]
    if forn and 'CODICE_FOR' in df_f.columns:
        df_f = df_f[df_f['CODICE_FOR'].isin(forn)]
    if marca and 'CODICE_MAR' in df_f.columns:
        df_f = df_f[df_f['CODICE_MAR'].isin(marca)]
    return df_f

# ---------------------------------------------------------
# NAVIGAZIONE TRAMITE SEZIONI (TAB)
# ---------------------------------------------------------
tab_giacenze, tab_ordini, tab_statistiche = st.tabs([
    "📦 Giacenze & Catalogo", 
    "🛒 Gestione Ordini & Reintegro Venduto", 
    "📊 Statistiche & Performance"
])

# =========================================================
# TAB 1: GIACENZE E CATALOGO
# =========================================================
with tab_giacenze:
    st.sidebar.header("🔍 Filtri Catalogo")

    search_term = st.sidebar.text_input("🔎 Ricerca Descrizione / Codice ART", "", placeholder="Es: STROFINACCI", key="g_search")
    sel_l1 = st.sidebar.multiselect("Livello 1: Reparto", CATEGORIE_L1, key="g_l1")
    sel_l2 = st.sidebar.multiselect("Livello 2: Tipologia Articolo", CATEGORIE_L2, key="g_l2")
    sel_l3 = st.sidebar.multiselect("Livello 3: Genere / Misura", CATEGORIE_L3, key="g_l3")
    sel_l4 = st.sidebar.multiselect("Livello 4: Materiale / Tessuto", CATEGORIE_L4, key="g_l4")

    fornitori = sorted([f for f in df_master['CODICE_FOR'].unique() if f != '-']) if 'CODICE_FOR' in df_master.columns else []
    sel_fornitore = st.sidebar.multiselect("Fornitore", fornitori, key="g_forn")

    marche = sorted([m for m in df_master['CODICE_MAR'].unique() if m != '-']) if 'CODICE_MAR' in df_master.columns else []
    sel_marca = st.sidebar.multiselect("Marca", marche, key="g_marca")

    ha_filtri_attivi = bool(search_term.strip() or sel_l1 or sel_l2 or sel_l3 or sel_l4 or sel_fornitore or sel_marca)

    df_filtered = applica_filtri_catalogo(df_master, search_term, sel_l1, sel_l2, sel_l3, sel_l4, sel_fornitore, sel_marca)

    filiali_scelte_keys = st.multiselect(
        "Seleziona le Filiali da includere in tabella:",
        options=list(MAPPA_FILIALI.keys()),
        format_func=lambda x: MAPPA_FILIALI[x],
        default=list(MAPPA_FILIALI.keys()),
        key="g_filiali"
    )

    if not filiali_scelte_keys:
        st.info("Seleziona almeno una filiale per visualizzare i dati.")
    else:
        df_filtered['Quantità Totale Selezionata'] = df_filtered[filiali_scelte_keys].sum(axis=1)
        df_filtered = df_filtered[df_filtered['Quantità Totale Selezionata'] > 0]

        colonne_mappate = {k: MAPPA_FILIALI[k] for k in filiali_scelte_keys}
        nomi_filiali_selezionate = list(colonne_mappate.values())

        df_display = df_filtered[[
            'CODICE_ART', 'DESCRIZION', 'CODICE_FOR', 'CODICE_MAR'
        ] + filiali_scelte_keys + ['Quantità Totale Selezionata']].copy()

        df_display = df_display.rename(columns={
            'CODICE_ART': 'Codice Articolo',
            'DESCRIZION': 'Descrizione',
            'CODICE_FOR': 'Fornitore',
            'CODICE_MAR': 'Marca',
            **colonne_mappate
        })

        df_display_table = df_display.set_index('Codice Articolo')

        def get_cell_color_styles(val, v_max):
            if not isinstance(val, (int, float)) or val <= 0 or pd.isna(val):
                return "", ""
            ratio = 0.15 + 0.70 * (val / v_max)
            r = int(225 - (185 * ratio))
            g = int(238 - (150 * ratio))
            b = int(250 - (70 * ratio))
            text_color = "white" if ratio > 0.55 else "black"
            return f"rgb({r}, {g}, {b})", text_color

        def applica_colori_giacenza(df, colonne_numeric):
            v_max = df[colonne_numeric].max().max() if not df.empty else 1
            if pd.isna(v_max) or v_max <= 0:
                v_max = 1

            def colora_cella(val):
                bg_color, text_color = get_cell_color_styles(val, v_max)
                if not bg_color:
                    return ''
                return f'background-color: {bg_color}; color: {text_color}; font-weight: bold;'

            return df.style.map(colora_cella, subset=colonne_numeric)

        if not ha_filtri_attivi:
            st.info("👈 **Seleziona un filtro o digita un termine di ricerca nel menu a sinistra per visualizzare la tabella dei prodotti.**")
        elif df_display.empty:
            st.warning("⚠️ Nessun articolo trovato con giacenza maggiore di 0 per i filtri selezionati.")
        else:
            k1, k2 = st.columns(2)
            k1.metric("Totale Articoli Trovati (Giacenza > 0)", f"{len(df_display):,}")
            k2.metric("Quantità Totale Giacenza", f"{df_display['Quantità Totale Selezionata'].sum():,}")

            colonne_da_colorare = nomi_filiali_selezionate
            styled_df = applica_colori_giacenza(df_display_table, colonne_da_colorare)

            st.dataframe(styled_df, use_container_width=True, height=550)

            c1, c2, c3 = st.columns([1, 1, 1])

            with c1:
                csv_data = df_display.to_csv(index=False).encode('latin1')
                st.download_button("📥 Scarica in CSV", csv_data, "Giacenze_Bianco_Market.csv", "text/csv", use_container_width=True)

            with c2:
                excel_data = convert_df_to_excel(df_display, sheet_name='Giacenze')
                st.download_button("📊 Scarica in Excel (.xlsx)", excel_data, "Giacenze_Bianco_Market.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

            with c3:
                v_max_print = df_display[nomi_filiali_selezionate].max().max() if not df_display.empty else 1
                if pd.isna(v_max_print) or v_max_print <= 0:
                    v_max_print = 1

                headers_html = "".join([f"<th>{col}</th>" for col in df_display.columns])
                rows_html = []
                for _, row in df_display.iterrows():
                    row_cells = []
                    for col in df_display.columns:
                        val = row[col]
                        if col in nomi_filiali_selezionate:
                            bg_c, txt_c = get_cell_color_styles(val, v_max_print)
                            cell_style = f"background-color: {bg_c}; color: {txt_c}; font-weight: bold;" if bg_c else ""
                            row_cells.append(f'<td style="{cell_style}">{val}</td>')
                        else:
                            row_cells.append(f'<td>{val}</td>')
                    rows_html.append(f"<tr>{''.join(row_cells)}</tr>")
                
                clean_html_table = f"<table><thead><tr>{headers_html}</tr></thead><tbody>{''.join(rows_html)}</tbody></table>"

                print_script = f"""
                <style>
                    .print-btn {{ background-color: #ff4b4b; color: white; border: none; padding: 9px 16px; font-size: 14px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; text-align: center; }}
                    .print-btn:hover {{ background-color: #e03e3e; }}
                </style>
                <button class="print-btn" onclick="openPrintWindow()">🖨️ Stampa Tabella Colorata</button>
                <script>
                    function openPrintWindow() {{
                        var printWin = window.open('', '_blank', 'width=1100,height=800');
                        printWin.document.write(`
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <title>Report Giacenze Filiali - Bianco Market</title>
                                <style>
                                    body {{ font-family: Arial, sans-serif; margin: 15px; color: #333; }}
                                    h2 {{ text-align: center; margin-bottom: 15px; font-size: 18px; }}
                                    table {{ width: 100%; border-collapse: collapse; font-size: 10px; }}
                                    th, td {{ border: 1px solid #777; padding: 5px 6px; text-align: center; }}
                                    th {{ background-color: #f2f2f2; font-weight: bold; }}
                                    @media print {{ body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
                                    @page {{ size: A4 landscape; margin: 8mm; }}
                                </style>
                            </head>
                            <body>
                                <h2>Bianco Market - Report Giacenze Filiali</h2>
                                {clean_html_table}
                            </body>
                            </html>
                        `);
                        printWin.document.close();
                        printWin.focus();
                        setTimeout(function() {{ printWin.print(); }}, 500);
                    }}
                </script>
                """
                components.html(print_script, height=45)

# =========================================================
# TAB 2: GESTIONE ORDINI & REINTEGRO VENDUTO (OPZIONE A)
# =========================================================
with tab_ordini:
    st.header("🛒 Gestione Ordini & Reintegro Venduto")
    st.info("💡 **Logica Applicata (Opzione A - Reintegro Puro)**: La quantità da ordinare equivale al totale dei pezzi venduti nel periodo per ripristinare il livello ottimale di scorta.")

    # --- CONTROLLI E DATE IN ALTO ---
    col_d1, col_d2, col_d3 = st.columns([1.5, 1.5, 1])
    with col_d1:
        date_range = st.date_input(
            "📅 Seleziona Intervallo Date Venduto:",
            value=(pd.to_datetime("2026-01-01").date(), pd.to_datetime("2026-03-31").date()),
            key="o_date_range"
        )
    with col_d2:
        filiali_ord_keys = st.multiselect(
            "Filiali di riferimento per la Giacenza:",
            options=list(MAPPA_FILIALI.keys()),
            format_func=lambda x: MAPPA_FILIALI[x],
            default=list(MAPPA_FILIALI.keys()),
            key="o_filiali"
        )
    with col_d3:
        solo_venduto = st.checkbox("Mostra solo articoli venduti (>0 pz)", value=True)

    # --- FILTRI CATALOGO COMPLETI PER GLI ORDINI ---
    st.subheader("🔍 Filtri Selezione Prodotti Catalogo")
    oc1, oc2, oc3, oc4 = st.columns(4)
    with oc1:
        o_search = st.text_input("🔎 Cerca Descrizione / Codice", "", key="o_search")
    with oc2:
        o_l1 = st.multiselect("Reparto (L1)", CATEGORIE_L1, key="o_l1")
    with oc3:
        o_forn = st.multiselect("Fornitore", fornitori, key="o_forn")
    with oc4:
        o_marca = st.multiselect("Marca", marche, key="o_marca")

    with st.expander("Filtri Avanzati Catalogo (Tipologia L2, Genere L3, Tessuto L4)"):
        ex1, ex2, ex3 = st.columns(3)
        with ex1:
            o_l2 = st.multiselect("Tipologia (L2)", CATEGORIE_L2, key="o_l2")
        with ex2:
            o_l3 = st.multiselect("Genere/Misura (L3)", CATEGORIE_L3, key="o_l3")
        with ex3:
            o_l4 = st.multiselect("Tessuto/Materiale (L4)", CATEGORIE_L4, key="o_l4")

    # Applica i filtri catalogo
    df_ord_filtered = applica_filtri_catalogo(df_master, o_search, o_l1, o_l2, o_l3, o_l4, o_forn, o_marca)

    if not filiali_ord_keys:
        st.warning("Seleziona almeno una filiale per visualizzare la giacenza attuale.")
    else:
        # Giacenza Attuale nelle filiali selezionate
        df_ord_filtered['Giacenza Attuale (Pz)'] = df_ord_filtered[filiali_ord_keys].sum(axis=1)

        # Calcolo del Venduto Reale dal file delle vendite
        if not df_vend.empty and 'DATA' in df_vend.columns and len(date_range) == 2:
            d_start, d_end = date_range[0], date_range[1]
            mask_date = (df_vend['DATA'].dt.date >= d_start) & (df_vend['DATA'].dt.date <= d_end)
            df_v_periodo = df_vend[mask_date]
            
            if 'CODICE_ART' in df_v_periodo.columns and 'QUANTITA' in df_v_periodo.columns:
                venduto_per_art = df_v_periodo.groupby('CODICE_ART')['QUANTITA'].sum().reset_index()
                venduto_per_art.columns = ['CODICE_ART', 'Venduto nel Periodo (Pz)']
                df_ord_filtered = pd.merge(df_ord_filtered, venduto_per_art, on='CODICE_ART', how='left')
                df_ord_filtered['Venduto nel Periodo (Pz)'] = df_ord_filtered['Venduto nel Periodo (Pz)'].fillna(0).astype(int)
            else:
                df_ord_filtered['Venduto nel Periodo (Pz)'] = 0
        else:
            df_ord_filtered['Venduto nel Periodo (Pz)'] = 0

        # --- APPLICAZIONE OPZIONE A: REINTEGRO DEL VENDUTO ---
        df_ord_filtered['Quantità da Ordinare (Pz)'] = df_ord_filtered['Venduto nel Periodo (Pz)']

        # Indicatore dello Stato della Giacenza
        def calcola_stato(row):
            if row['Giacenza Attuale (Pz)'] == 0 and row['Venduto nel Periodo (Pz)'] > 0:
                return "⚠️ ESAURITO (Giacenza 0)"
            elif row['Giacenza Attuale (Pz)'] < 3 and row['Venduto nel Periodo (Pz)'] > 0:
                return "⚡ SCORTA CRITICA (<3 pz)"
            elif row['Venduto nel Periodo (Pz)'] > 0:
                return "OK - In Reintegro"
            else:
                return "Nessuna Vendita"

        df_ord_filtered['Stato Giacenza'] = df_ord_filtered.apply(calcola_stato, axis=1)

        # Filtro per mostrare solo il venduto/da ordinare
        if solo_venduto:
            df_ord_filtered = df_ord_filtered[df_ord_filtered['Quantità da Ordinare (Pz)'] > 0]

        df_ord_display = df_ord_filtered[[
            'CODICE_ART', 'DESCRIZION', 'CODICE_FOR', 'CODICE_MAR', 
            'Giacenza Attuale (Pz)', 'Venduto nel Periodo (Pz)', 'Quantità da Ordinare (Pz)', 'Stato Giacenza'
        ]].copy()

        df_ord_display.columns = [
            'Codice Articolo', 'Descrizione', 'Fornitore', 'Marca', 
            'Giacenza Attuale (Pz)', 'Venduto nel Periodo (Pz)', 'Quantità da Ordinare (Pz)', 'Stato Giacenza'
        ]

        # Metriche in evidenza
        m1, m2, m3 = st.columns(3)
        m1.metric("Articoli da Reintegrare", f"{len(df_ord_display):,}")
        m2.metric("Totale Pezzi Venduti", f"{df_ord_display['Venduto nel Periodo (Pz)'].sum():,} pz")
        m3.metric("TOTALE DA ORDINARE (REINTEGRO)", f"{df_ord_display['Quantità da Ordinare (Pz)'].sum():,} pz")

        # Tabella Ordini
        st.dataframe(df_ord_display.set_index('Codice Articolo'), use_container_width=True, height=480)

        # Pulsanti Esportazione
        o_col1, o_col2 = st.columns(2)
        with o_col1:
            csv_ord = df_ord_display.to_csv(index=False).encode('latin1')
            st.download_button(
                "📥 Scarica Ordine di Reintegro (CSV)", 
                csv_ord, 
                "Ordine_Reintegro_Bianco_Market.csv", 
                "text/csv", 
                use_container_width=True
            )
        with o_col2:
            excel_ord = convert_df_to_excel(df_ord_display, sheet_name='Proposta Ordine')
            st.download_button(
                "📊 Scarica Ordine di Reintegro (Excel .xlsx)", 
                excel_ord, 
                "Ordine_Reintegro_Bianco_Market.xlsx", 
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                use_container_width=True
            )

# =========================================================
# TAB 3: STATISTICHE & PERFORMANCE
# =========================================================
with tab_statistiche:
    st.header("📊 Statistiche Giacenze & Distribuzione Filiali")
    
    st_c1, st_c2 = st.columns(2)

    with st_c1:
        st.subheader("Totale Pezzi per Filiale")
        totali_filiali = df_master[list(MAPPA_FILIALI.keys())].sum().reset_index()
        totali_filiali.columns = ['Codice', 'Quantità Totale']
        totali_filiali['Filiale'] = totali_filiali['Codice'].map(MAPPA_FILIALI)
        
        st.bar_chart(totali_filiali.set_index('Filiale')['Quantità Totale'])

    with st_c2:
        st.subheader("Distribuzione Top 10 Reparti (L1)")
        if 'CAT_L1_REPARTO' in df_master.columns:
            tot_reparti = df_master.groupby('CAT_L1_REPARTO')[list(MAPPA_FILIALI.keys())].sum().sum(axis=1)
            top10_reparti = tot_reparti.sort_values(ascending=False).head(10)
            st.bar_chart(top10_reparti)