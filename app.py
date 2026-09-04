import streamlit.components.v1 as components

# ---------------------------------------------------------
# METRICHE E VISUALIZZAZIONE CONDIZIONATA
# ---------------------------------------------------------
if not ha_filtri_attivi:
    st.info("👈 **Seleziona un filtro o digita un termine di ricerca nel menu a sinistra per visualizzare la tabella dei prodotti.**")
else:
    k1, k2 = st.columns(2)
    k1.metric("Totale Articoli Trovati", f"{len(df_display):,}")
    k2.metric("Quantità Totale Giacenza", f"{df_display['Quantità Totale Selezionata'].sum():,}")

    colonne_da_colorare = nomi_filiali_selezionate
    styled_df = applica_colori_giacenza(df_display_table, colonne_da_colorare)

    st.dataframe(styled_df, use_container_width=True, height=550)

    # ---------------------------------------------------------
    # PULSANTI DOWNLOAD ED ESPORTAZIONE / STAMPA
    # ---------------------------------------------------------
    col_dl, col_print = st.columns([1, 1])

    with col_dl:
        csv_data = df_display.to_csv(index=False).encode('latin1')
        st.download_button(
            label="📥 Scarica Tabella in CSV",
            data=csv_data,
            file_name="Giacenze_Filiali_Bianco_Market.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_print:
        # Generazione HTML stampabile
        html_table = df_display.to_html(index=False, classes="print-table")
        
        print_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h2 {{ text-align: center; font-size: 18px; margin-bottom: 5px; }}
            p {{ text-align: center; font-size: 12px; color: #555; margin-top: 0; }}
            table.print-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 10px;
            }}
            table.print-table th, table.print-table td {{
                border: 1px solid #ccc;
                padding: 4px 6px;
                text-align: center;
            }}
            table.print-table th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            @media print {{
                @page {{
                    size: A4 landscape; /* Orientamento orizzontale per far entrare tutte le colonne */
                    margin: 8mm;
                }}
                body {{ margin: 0; }}
                button {{ display: none; }}
            }}
            .btn-print {{
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                cursor: pointer;
                width: 100%;
            }}
            .btn-print:hover {{
                background-color: #0056b3;
            }}
        </style>
        </head>
        <body>
            <button class="btn-print" onclick="window.print()">🖨️ Stampa Tabella Completa</button>
            <script>
                function apriStampa() {{
                    var w = window.open('', '_blank');
                    w.document.write(`
                        <html>
                        <head>
                            <title>Stampa Tabella - Bianco Market</title>
                            <style>
                                body {{ font-family: Arial, sans-serif; margin: 15px; }}
                                h3 {{ text-align: center; margin-bottom: 5px; }}
                                table {{ width: 100%; border-collapse: collapse; font-size: 10px; }}
                                th, td {{ border: 1px solid #999; padding: 4px; text-align: center; }}
                                th {{ background-color: #eee; }}
                                @page {{ size: A4 landscape; margin: 8mm; }}
                            </style>
                        </head>
                        <body>
                            <h3>Bianco Market - Prospetto Giacenze Filiali</h3>
                            {html_table}
                            <script>
                                window.onload = function() {{ window.print(); }}
                            <\\/script>
                        </body>
                        </html>
                    `);
                    w.document.close();
                }}
            </script>
        </body>
        </html>
        """
        
        # Pulsante che attiva il popup/finestra di stampa
        if st.button("🖨️ Prepara Stampa Tabella", use_container_width=True):
            components.html(
                f"""
                <script>
                    var w = window.open('', '_blank');
                    w.document.write(`
                        <html>
                        <head>
                            <title>Stampa Tabella Giacenze - Bianco Market</title>
                            <style>
                                body {{ font-family: Arial, sans-serif; margin: 10px; }}
                                h3 {{ text-align: center; font-size: 16px; margin-bottom: 5px; }}
                                table {{ width: 100%; border-collapse: collapse; font-size: 9px; }}
                                th, td {{ border: 1px solid #666; padding: 3px 5px; text-align: center; }}
                                th {{ background-color: #e6e6e6; font-weight: bold; }}
                                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                                @page {{ size: A4 landscape; margin: 6mm; }}
                            </style>
                        </head>
                        <body>
                            <h3>Bianco Market - Report Giacenze Filiali</h3>
                            {html_table}
                            <script>
                                window.onload = function() {{ window.print(); }}
                            <\\/script>
                        </body>
                        </html>
                    `);
                    w.document.close();
                </script>
                """,
                height=0
            )