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
        # Generazione tabella HTML per la stampa
        html_table = df_display.to_html(index=False, classes="print-table-content")
        
        # Componente HTML con CSS per la stampa e pulsante diretto
        print_component = f"""
        <style>
            .print-btn {{
                background-color: #ff4b4b;
                color: white;
                border: none;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                cursor: pointer;
                width: 100%;
                text-align: center;
            }}
            .print-btn:hover {{
                background-color: #e03e3e;
            }}
            
            /* Stili applicati ESCLUSIVAMENTE quando si attiva la stampa */
            @media print {{
                /* Nasconde tutto l'interfaccia Streamlit, sidebar e pulsanti */
                header, footer, [data-testid="stSidebar"], .stButton, button, .print-btn {{
                    display: none !important;
                }}
                body {{
                    background: white !important;
                    color: black !important;
                    margin: 0 !important;
                }}
                .print-container {{
                    display: block !important;
                    width: 100% !important;
                }}
                table.print-table-content {{
                    width: 100% !important;
                    border-collapse: collapse !important;
                    font-size: 8pt !important;
                }}
                table.print-table-content th, table.print-table-content td {{
                    border: 1px solid #444 !important;
                    padding: 4px !important;
                    text-align: center !important;
                }}
                table.print-table-content th {{
                    background-color: #eee !important;
                    font-weight: bold !important;
                }}
                @page {{
                    size: A4 landscape; /* Imposta l'orientamento orizzontale */
                    margin: 8mm;
                }}
            }}
        </style>

        <button class="print-btn" onclick="triggerPrint()">🖨️ Stampa Tabella (Anteprima & Stampante)</button>

        <div id="print-area" style="display:none;" class="print-container">
            <h3 style="text-align:center;">Bianco Market - Report Giacenze Filiali</h3>
            {html_table}
        </div>

        <script>
            function triggerPrint() {{
                // Invia il comando di stampa alla finestra principale del browser
                window.parent.print();
            }}
        </script>
        """
        
        components.html(print_component, height=45)