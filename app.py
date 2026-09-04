import os
import glob
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------
# CONFIGURAZIONE PAGINA STREAMLIT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Bianco Market - Assistant & Inventory AI",
    layout="wide"
)

# ---------------------------------------------------------
# MAPPATURA UFFICIALE FILIALI BIANCO MARKET
# ---------------------------------------------------------
FILIALI_MAP = {
    '01': {'nome': 'Magazzino Centrale', 'col_c': 'C_01', 'col_s': 'S_01', 'cod_stor': '00'},
    '02': {'nome': 'Sciacca',            'col_c': 'C_02', 'col_s': 'S_02', 'cod_stor': '06'},
    '03': {'nome': 'Menfi',              'col_c': 'C_03', 'col_s': 'S_03', 'cod_stor': '01'},
    '04': {'nome': 'Marsala',            'col_c': 'C_04', 'col_s': 'S_04', 'cod_stor': '03'},
    '05': {'nome': 'Trapani',            'col_c': 'C_05', 'col_s': 'S_05', 'cod_stor': '09'},
    '06': {'nome': 'Ragusa',             'col_c': 'C_06', 'col_s': 'S_06', 'cod_stor': '07'},
    '07': {'nome': 'Sabella',            'col_c': 'C_07', 'col_s': 'S_07', 'cod_stor': '05'},
    '08': {'nome': 'Mazara del Vallo',   'col_c': 'C_08', 'col_s': 'S_08', 'cod_stor': '02'},
    '09': {'nome': 'Casa Market',        'col_c': 'C_09', 'col_s': 'S_09', 'cod_stor': '04'},
    '10': {'nome': 'Sport Market',       'col_c': 'C_10', 'col_s': 'S_10', 'cod_stor': '08'}
}

# ---------------------------------------------------------
# UTILITY PER RICERCA FILE FLESSIBILE (FLEXIBLE FILE FINDER)
# ---------------------------------------------------------
def find_file(filename, possible_dirs=None):
    """Cerca un file ignorando la differenza tra maiuscole/minuscole."""
    if possible_dirs is None:
        possible_dirs = ["data/current", "data", "."]
        
    for d in possible_dirs:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.lower() == filename.lower():
                    return os.path.join(d, f)
    return None

# ---------------------------------------------------------
# FUNZIONI DI CARICAMENTO DATI CACHATE
# ---------------------------------------------------------

@st.cache_data(ttl=3600)
def load_articoli():
    path = find_file("ARTICOLI.TXT")
    if not path:
        return pd.DataFrame()
    
    df = pd.read_csv(
        path, 
        sep='\t', 
        header=None, 
        encoding='latin1', 
        on_bad_lines='skip',
        dtype=str
    )
    
    col_mapping = {
        0: 'CODICE_ART',
        1: 'CODICE_ALT',
        2: 'DESCRIZION',
        3: 'UM',
        4: 'CODICE_CAT',      # Macro Categoria
        5: 'CODICE_FOR',      # Fornitore
        6: 'CODICE_MAR',      # Marca
        22: 'PRZ_ACQ',        # Prezzo Acquisto
        32: 'GRUPPO',          # Sotto Categoria / Articolo
        33: 'SOTTOGRUPPO',      # Genere / Misura / Taglia
        36: 'CAT_LEVEL_4',    # Materiale / Tessuto (Cat. 4)
        37: 'CAT_LEVEL_5'     # Sede Magazzino (Cat. 5)
    }
    
    df = df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns})
    
    text_cols = ['DESCRIZION', 'CODICE_CAT', 'CODICE_FOR', 'CODICE_MAR', 'GRUPPO', 'SOTTOGRUPPO', 'CAT_LEVEL_4', 'CAT_LEVEL_5']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna('NON DEFINITO').str.strip()
            
    if 'PRZ_ACQ' in df.columns:
        df['PRZ_ACQ'] = pd.to_numeric(df['PRZ_ACQ'].str.replace(',', '.'), errors='coerce').fillna(0.0)
        
    return df

@st.cache_data(ttl=3600)
def load_giacenze():
    path = find_file("Sit_filiali.TXT")
    if not path:
        return pd.DataFrame()
    
    df = pd.read_csv(
        path, 
        sep='\t', 
        header=None, 
        encoding='latin1', 
        on_bad_lines='skip',
        dtype=str
    )
    
    columns_names = ['CODICE_ART']
    for i in range(1, 11):
        num = f"{i:02d}"
        columns_names.extend([f"C_{num}", f"S_{num}"])
        
    df.columns = columns_names[:len(df.columns)]
    
    num_cols = [c for c in df.columns if c != 'CODICE_ART']
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    return df

@st.cache_data(ttl=3600)
def load_storico_vendite(anni_selezionati):
    dfs = []
    for anno in anni_selezionati:
        possible_paths = [
            f"data/storici/{anno}/STOR_CAR.TXT",
            f"data/storici/{anno}/stor_car.txt",
            f"storici/{anno}/STOR_CAR.TXT",
            f"{anno}/STOR_CAR.TXT"
        ]
        path_found = None
        for p in possible_paths:
            if os.path.exists(p):
                path_found = p
                break
                
        if path_found:
            try:
                df = pd.read_csv(path_found, sep='\t', header=None, encoding='latin1', on_bad_lines='skip', dtype=str)
                df = df[[0, 1, 4, 5, 6, 9]].copy()
                df.columns = ['Tipo_Movimento', 'Data', 'CODICE_ART', 'Cod_Filiale_Stor', 'Prezzo', 'Quantita']
                df['Anno'] = str(anno)
                dfs.append(df)
            except Exception:
                pass
                
    if not dfs:
        return pd.DataFrame()
        
    full_df = pd.concat(dfs, ignore_index=True)
    full_df['Quantita'] = pd.to_numeric(full_df['Quantita'].str.replace(',', '.'), errors='coerce').fillna(0)
    full_df['Prezzo'] = pd.to_numeric(full_df['Prezzo'].str.replace(',', '.'), errors='coerce').fillna(0.0)
    full_df['Data'] = pd.to_datetime(full_df['Data'], format='%d/%m/%Y', errors='coerce')
    
    reverse_map = {v['cod_stor']: key for key, v in FILIALI_MAP.items()}
    full_df['Cod_Filiale_Key'] = full_df['Cod_Filiale_Stor'].str.zfill(2).map(reverse_map)
    
    return full_df

# ---------------------------------------------------------
# INTERFACCIA E LOGICA PRINCIPALE
# ---------------------------------------------------------

st.title("🛍️ Bianco Market - Assistant & Inventory AI")
st.markdown("Sistema integrato per la gestione esistenze, analisi vendite e riassortimento automatizzato.")

df_art = load_articoli()
df_giac = load_giacenze()

# Controllo presenza dati senza blocco irreversibile dell'app
if df_art.empty or df_giac.empty:
    st.warning("⚠️ File dati non trovati. Assicurati che i file `ARTICOLI.TXT` e `Sit_filiali.TXT` siano stati caricati su GitHub nella cartella `data/current/`.")
    st.info("💡 Struttura cartelle richiesta:\n"
            "- `data/current/ARTICOLI.TXT`\n"
            "- `data/current/Sit_filiali.TXT`\n"
            "- `data/storici/2026/STOR_CAR.TXT`")
    st.stop()

# Join Master Data
df_master = pd.merge(df_art, df_giac, on='CODICE_ART', how='left')

# ---------------------------------------------------------
# SIDEBAR - FILTRI CATOLOGO
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtri Avanzati Catalogo")

sedi = sorted([s for s in df_master['CAT_LEVEL_5'].unique() if s]) if 'CAT_LEVEL_5' in df_master.columns else []
sel_sede = st.sidebar.multiselect("Sede Magazzino (Cat. 5)", sedi)

macro = sorted([m for m in df_master['CODICE_CAT'].unique() if m]) if 'CODICE_CAT' in df_master.columns else []
sel_macro = st.sidebar.multiselect("Macro Categoria (Codice Cat)", macro)

gruppi = sorted([g for g in df_master['GRUPPO'].unique() if g]) if 'GRUPPO' in df_master.columns else []
sel_gruppo = st.sidebar.multiselect("Sotto Categoria (Gruppo)", gruppi)

sottogruppi = sorted([sg for sg in df_master['SOTTOGRUPPO'].unique() if sg]) if 'SOTTOGRUPPO' in df_master.columns else []
sel_sottogruppo = st.sidebar.multiselect("Genere / Taglia (Sottogruppo)", sottogruppi)

cat4 = sorted([c for c in df_master['CAT_LEVEL_4'].unique() if c]) if 'CAT_LEVEL_4' in df_master.columns else []
sel_cat4 = st.sidebar.multiselect("Materiale / Tessuto (Cat. 4)", cat4)

fornitori = sorted([f for f in df_master['CODICE_FOR'].unique() if f]) if 'CODICE_FOR' in df_master.columns else []
sel_fornitore = st.sidebar.multiselect("Fornitore", fornitori)

marche = sorted([m for m in df_master['CODICE_MAR'].unique() if m]) if 'CODICE_MAR' in df_master.columns else []
sel_marca = st.sidebar.multiselect("Marca", marche)

search_term = st.sidebar.text_input("🔎 Cerca per Descrizione o Codice ART", "")

df_filtered = df_master.copy()

if sel_sede:
    df_filtered = df_filtered[df_filtered['CAT_LEVEL_5'].isin(sel_sede)]
if sel_macro:
    df_filtered = df_filtered[df_filtered['CODICE_CAT'].isin(sel_macro)]
if sel_gruppo:
    df_filtered = df_filtered[df_filtered['GRUPPO'].isin(sel_gruppo)]
if sel_sottogruppo:
    df_filtered = df_filtered[df_filtered['SOTTOGRUPPO'].isin(sel_sottogruppo)]
if sel_cat4:
    df_filtered = df_filtered[df_filtered['CAT_LEVEL_4'].isin(sel_cat4)]
if sel_fornitore:
    df_filtered = df_filtered[df_filtered['CODICE_FOR'].isin(sel_fornitore)]
if sel_marca:
    df_filtered = df_filtered[df_filtered['CODICE_MAR'].isin(sel_marca)]
if search_term:
    df_filtered = df_filtered[
        df_filtered['DESCRIZION'].str.contains(search_term, case=False, na=False) |
        df_filtered['CODICE_ART'].str.contains(search_term, case=False, na=False)
    ]

# ---------------------------------------------------------
# TABS SCHERMATE PRINCIPALI
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Esistenze & Giacenze", 
    "📈 Analisi Vendite", 
    "💡 Algoritmo Riassortimento", 
    "🖨️ Reportistica & Export"
])

# TAB 1: ESISTENZE
with tab1:
    st.subheader("Consultazione Giacenze per Filiale")
    
    filiali_scelte = st.multiselect(
        "Seleziona le Filiali da visualizzare:",
        options=list(FILIALI_MAP.keys()),
        format_func=lambda x: f"{x} - {FILIALI_MAP[x]['nome']}",
        default=list(FILIALI_MAP.keys())
    )
    
    if filiali_scelte:
        c_cols = [FILIALI_MAP[f]['col_c'] for f in filiali_scelte if FILIALI_MAP[f]['col_c'] in df_filtered.columns]
        df_filtered['Totale_Giacenza_Selezionata'] = df_filtered[c_cols].sum(axis=1) if c_cols else 0
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Articoli Filtrati", f"{len(df_filtered):,}")
        kpi2.metric("Pezzi Totali in Giacenza", f"{df_filtered['Totale_Giacenza_Selezionata'].sum():,}")
        kpi3.metric("Filiali Incluse", len(filiali_scelte))
        
        cols_base = ['CODICE_ART', 'DESCRIZION', 'CODICE_FOR', 'CODICE_MAR', 'CODICE_CAT', 'GRUPPO', 'SOTTOGRUPPO', 'CAT_LEVEL_4', 'CAT_LEVEL_5']
        cols_presenti = [c for c in cols_base if c in df_filtered.columns]
        cols_to_show = cols_presenti + c_cols + ['Totale_Giacenza_Selezionata']
        
        st.dataframe(df_filtered[cols_to_show], use_container_width=True, height=400)
        
        st.subheader("📊 Ripartizione Giacenze per Punto Vendita")
        giac_totali = {
            FILIALI_MAP[f]['nome']: df_filtered[FILIALI_MAP[f]['col_c']].sum() 
            for f in filiali_scelte if FILIALI_MAP[f]['col_c'] in df_filtered.columns
        }
        
        if giac_totali:
            fig = px.bar(
                x=list(giac_totali.keys()), 
                y=list(giac_totali.values()),
                labels={'x': 'Punto Vendita', 'y': 'Giacenza (Pezzi)'},
                title="Distribuzione Pezzi tra le Filiali",
                color_discrete_sequence=['#0056b3']
            )
            st.plotly_chart(fig, use_container_width=True)

# TAB 2: VENDITE
with tab2:
    st.subheader("Analisi Storico Vendite")
    
    col_a, col_b = st.columns(2)
    with col_a:
        anni_disponibili = ['2024', '2025', '2026', '2027']
        anni_sel = st.multiselect("Anni Storico da Analizzare:", anni_disponibili, default=['2026'])
    with col_b:
        tipi_mov = st.multiselect("Tipi Movimento:", ['S', 'F'], default=['S', 'F'])
        
    if anni_sel:
        df_stor = load_storico_vendite(anni_sel)
        if not df_stor.empty:
            df_stor = df_stor[df_stor['Tipo_Movimento'].isin(tipi_mov)]
            art_validi = set(df_filtered['CODICE_ART'])
            df_stor_filt = df_stor[df_stor['CODICE_ART'].isin(art_validi)]
            
            st.markdown("---")
            k1, k2, k3 = st.columns(3)
            tot_pezzi = df_stor_filt['Quantita'].sum()
            tot_valore = (df_stor_filt['Quantita'] * df_stor_filt['Prezzo']).sum()
            
            k1.metric("Pezzi Venduti nel Periodo", f"{int(tot_pezzi):,}")
            k2.metric("Valore Stimato Vendite", f"€ {tot_valore:,.2f}")
            k3.metric("Numero Movimenti", f"{len(df_stor_filt):,}")
            
            if not df_stor_filt.empty and 'Data' in df_stor_filt.columns:
                df_trend = df_stor_filt.dropna(subset=['Data']).set_index('Data').groupby(pd.Grouper(freq='M'))['Quantita'].sum().reset_index()
                fig_trend = px.line(
                    df_trend, 
                    x='Data', 
                    y='Quantita', 
                    title="Andamento Mensile Vendite (Pezzi)",
                    markers=True
                )
                st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Nessun dato storico trovato per gli anni selezionati.")

# TAB 3: RIASSORTIMENTO
with tab3:
    st.subheader("💡 Consigli Automatici di Riassortimento")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        filiale_target = st.selectbox(
            "Seleziona la Filiale per cui generare il riassortimento:",
            options=list(FILIALI_MAP.keys()),
            format_func=lambda x: f"{x} - {FILIALI_MAP[x]['nome']}"
        )
    with col_r2:
        percentuale_scorta = st.slider("Incremento Scorta di Sicurezza (%)", 0, 50, 10)
        
    col_c = FILIALI_MAP[filiale_target]['col_c']
    col_s = FILIALI_MAP[filiale_target]['col_s']
    
    df_reorder = df_filtered.copy()
    if col_c in df_reorder.columns and col_s in df_reorder.columns:
        df_reorder['Giacenza_Attuale'] = df_reorder[col_c]
        df_reorder['Scorta_Minima_Base'] = df_reorder[col_s]
        df_reorder['Scorta_Calcolata'] = (df_reorder['Scorta_Minima_Base'] * (1 + percentuale_scorta/100)).astype(int)
        df_reorder['Proposta_Ordine'] = (df_reorder['Scorta_Calcolata'] - df_reorder['Giacenza_Attuale']).clip(lower=0)
        
        df_da_ordinare = df_reorder[df_reorder['Proposta_Ordine'] > 0]
        
        st.warning(f"⚠️ Trovati **{len(df_da_ordinare)}** articoli da riassortire per **{FILIALI_MAP[filiale_target]['nome']}**")
        
        cols_ordine_base = ['CODICE_ART', 'DESCRIZION', 'CODICE_FOR', 'CODICE_MAR', 'GRUPPO', 'SOTTOGRUPPO', 'Giacenza_Attuale', 'Scorta_Minima_Base', 'Proposta_Ordine']
        cols_ordine = [c for c in cols_ordine_base if c in df_da_ordinare.columns]
        st.dataframe(df_da_ordinare[cols_ordine], use_container_width=True)

# TAB 4: REPORTISTICA
with tab4:
    st.subheader("🖨️ Generazione e Download Report")
    
    scelta_report = st.radio("Scegli il tipo di file da esportare:", [
        "Report Giacenze Completo (Articoli Filtrati)", 
        "Piano Ordine Riassortimento Fornitore"
    ])
    
    if scelta_report == "Report Giacenze Completo (Articoli Filtrati)":
        csv_full = df_filtered.to_csv(index=False).encode('latin1')
        st.download_button(
            label="📥 Scarica Report Giacenze in CSV",
            data=csv_full,
            file_name="Bianco_Market_Giacenze.csv",
            mime="text/csv"
        )
    else:
        if 'df_da_ordinare' in locals() and not df_da_ordinare.empty:
            csv_ord = df_da_ordinare[cols_ordine].to_csv(index=False).encode('latin1')
            st.download_button(
                label="📥 Scarica Ordine Suggerito in CSV",
                data=csv_ord,
                file_name=f"Ordine_Riassortimento_{FILIALI_MAP[filiale_target]['nome']}.csv",
                mime="text/csv"
            )
        else:
            st.info("Nessun ordine suggerito presente da esportare per la filiale selezionata.")