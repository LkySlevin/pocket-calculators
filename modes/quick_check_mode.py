"""
Quick Check Mode - Schnelle Vertragsüberprüfung durch Upload
"""
import streamlit as st


def render_quick_check_mode():
    """
    Rendert den Quick Check Mode.

    Dieser Modus ermöglicht es Nutzern, bestehende Verträge hochzuladen
    und schnell zu prüfen, ob diese geeignet sind.
    """
    st.title("⚡ Quick Check Mode")

    st.markdown("""
    Laden Sie Ihren bestehenden Altersvorsorge-Vertrag hoch und erhalten Sie eine
    schnelle Einschätzung, ob dieser für Ihre Situation geeignet ist.
    """)

    st.markdown("---")

    # Upload-Bereich
    st.subheader("📄 Vertrag hochladen")

    uploaded_file = st.file_uploader(
        "Laden Sie Ihren Vertragsunterlagen hoch (PDF, JPG, PNG)",
        type=["pdf", "jpg", "jpeg", "png"],
        help="Unterstützte Formate: PDF, JPG, PNG"
    )

    if uploaded_file is not None:
        st.success(f"✅ Datei '{uploaded_file.name}' erfolgreich hochgeladen!")

        with st.expander("🔍 Vorschau", expanded=True):
            st.info("Vorschau-Funktion wird in einer zukünftigen Version verfügbar sein.")

        st.markdown("---")

        # Manuelle Eingabe für MVP
        st.subheader("📝 Vertragsdaten (manuelle Eingabe)")

        st.info("""
        **🚧 OCR-Erkennung in Entwicklung**

        Aktuell geben Sie bitte die wichtigsten Vertragsdaten manuell ein.
        In einer zukünftigen Version werden diese automatisch aus dem Dokument extrahiert.
        """)

        col1, col2 = st.columns(2)

        with col1:
            contract_type = st.selectbox(
                "Vertragstyp",
                ["ETF-Sparplan", "Basisrente (Rürup)", "Riester-Rente", "Privatrente", "Andere"]
            )

            monthly_contribution = st.number_input(
                "Monatlicher Beitrag (€)",
                min_value=0.0,
                max_value=5000.0,
                value=200.0,
                step=50.0
            )

            contract_duration = st.number_input(
                "Restlaufzeit (Jahre)",
                min_value=1,
                max_value=50,
                value=25,
                step=1
            )

        with col2:
            expected_return = st.number_input(
                "Erwartete Rendite (% p.a.)",
                min_value=0.0,
                max_value=15.0,
                value=5.0,
                step=0.1
            )

            total_costs = st.number_input(
                "Gesamtkosten (% p.a.)",
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                step=0.1,
                help="Alle Kosten zusammen: Abschluss-, Verwaltungs-, Fondskosten"
            )

        st.markdown("---")
        st.subheader("📈 Dynamiken (optional)")

        col1, col2 = st.columns(2)

        with col1:
            contribution_dynamics = st.slider(
                "Beitragsdynamik (%/Jahr)",
                min_value=0.0,
                max_value=5.0,
                value=2.0,
                step=0.5,
                help="Jährliche Steigerung der Sparrate"
            ) / 100

        with col2:
            inflation_rate = st.slider(
                "Erwartete Inflation (%/Jahr)",
                min_value=0.0,
                max_value=5.0,
                value=2.0,
                step=0.5,
                help="Zur Berechnung der realen Kaufkraft"
            ) / 100

        st.markdown("---")

        if st.button("🔍 Vertrag analysieren", type="primary", use_container_width=True):
            # Analyse durchführen
            st.subheader("📊 Analyse-Ergebnis")

            # Berechne Nettorendite
            net_return = expected_return - total_costs
            net_return_decimal = net_return / 100

            # Endwert berechnen (mit Dynamik falls > 0)
            if contribution_dynamics > 0:
                from calculators.dynamics import calculate_with_contribution_dynamics
                final_value, _, total_paid = calculate_with_contribution_dynamics(
                    initial_monthly_contribution=monthly_contribution,
                    annual_dynamics_rate=contribution_dynamics,
                    years=contract_duration,
                    annual_return=net_return_decimal,
                    initial_investment=0
                )
            else:
                # Ohne Dynamik: Standard-Formel
                months = contract_duration * 12
                monthly_rate = net_return_decimal / 12
                if monthly_rate > 0:
                    final_value = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
                else:
                    final_value = monthly_contribution * months
                total_paid = monthly_contribution * months

            # Inflation berücksichtigen (reale Kaufkraft)
            if inflation_rate > 0:
                from calculators.dynamics import calculate_real_return
                real_return = calculate_real_return(net_return_decimal, inflation_rate)
                real_return_percent = real_return * 100
                real_final_value = final_value / ((1 + inflation_rate) ** contract_duration)
            else:
                real_return_percent = net_return
                real_final_value = final_value

            # Bewertung
            if net_return < 2.0:
                rating = "❌ **Nicht empfehlenswert**"
                color = "#ff4444"
                explanation = f"""
                Die Nettorendite von {net_return:.1f}% ist sehr niedrig.
                Nach Abzug der Kosten bleibt zu wenig Rendite übrig.
                """
            elif net_return < 4.0:
                rating = "⚠️ **Durchschnittlich**"
                color = "#ffaa00"
                explanation = f"""
                Die Nettorendite von {net_return:.1f}% ist akzeptabel, aber es gibt
                bessere Alternativen am Markt.
                """
            else:
                rating = "✅ **Empfehlenswert**"
                color = "#44ff44"
                explanation = f"""
                Die Nettorendite von {net_return:.1f}% ist gut.
                Der Vertrag scheint angemessen zu sein.
                """

            st.markdown(f"""
            <div style="background: {color}; color: white; padding: 2rem; border-radius: 10px;
                        text-align: center; font-size: 1.5rem; margin-bottom: 1rem;">
                {rating}
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Bruttorendite", f"{expected_return:.1f}%")
            with col2:
                st.metric("Kosten", f"{total_costs:.1f}%")
            with col3:
                st.metric("Nettorendite (nominal)", f"{net_return:.1f}%")
            with col4:
                st.metric("Nettorendite (real)", f"{real_return_percent:.1f}%")

            st.markdown(explanation)

            # Zusätzliche Metriken für Endwert
            st.markdown("---")
            st.subheader("💰 Prognostizierter Endwert")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Eingezahlt gesamt", f"{total_paid:,.0f} €")
            with col2:
                st.metric("Endwert (nominal)", f"{final_value:,.0f} €")
            with col3:
                st.metric("Endwert (Kaufkraft)", f"{real_final_value:,.0f} €")

            profit = final_value - total_paid
            if total_paid > 0:
                roi = (profit / total_paid) * 100
                st.info(f"**Gewinn:** {profit:,.0f} € (+{roi:.1f}%)")

            if contribution_dynamics > 0:
                st.caption(f"✓ Beitragsdynamik von {contribution_dynamics*100:.1f}% p.a. berücksichtigt")
            if inflation_rate > 0:
                st.caption(f"✓ Inflation von {inflation_rate*100:.1f}% p.a. berücksichtigt (Kaufkraft-Anzeige)")

            # Vergleich mit Alternativen
            st.markdown("---")
            st.subheader("💡 Vergleich mit Alternativen")

            alternatives = {
                "ETF-Sparplan (kostengünstig)": {"return": 7.0, "costs": 0.3, "net": 6.7},
                "Basisrente (Nettotarif)": {"return": 7.0, "costs": 0.8, "net": 6.2},
                "Riester (fondsgebunden)": {"return": 3.0, "costs": 1.5, "net": 1.5},
            }

            for name, data in alternatives.items():
                difference = data["net"] - net_return
                if difference > 0:
                    st.info(f"""
                    **{name}**
                    - Nettorendite: {data['net']:.1f}% p.a.
                    - **{difference:.1f}% höher** als Ihr Vertrag
                    """)

            st.markdown("---")

            st.info("""
            💡 **Tipp:** Nutzen Sie den **Learning Mode** für eine detaillierte Analyse
            verschiedener Altersvorsorge-Produkte.
            """)

            if st.button("📚 Zum Learning Mode", use_container_width=True):
                st.session_state.selected_mode = "learning"
                st.rerun()

    else:
        st.info("""
        👆 **Laden Sie zunächst Ihre Vertragsunterlagen hoch**

        Unterstützte Dokumenttypen:
        - Vertragsübersicht / Produktinformationsblatt
        - Jahresabrechnung / Standmitteilung
        - Kostenaufstellung
        """)

        st.markdown("---")

        st.markdown("""
        ### 🔮 Geplante Features:

        - **📸 OCR-Texterkennung**: Automatische Extraktion aller Vertragsdaten
        - **🤖 KI-Analyse**: Intelligente Bewertung basierend auf Tausenden von Verträgen
        - **📊 Vergleichsrechnung**: Direkter Vergleich mit optimalen Alternativen
        - **💰 Wechselkosten-Berechnung**: Lohnt sich ein Wechsel?
        - **📈 Prognose**: Langfristige Entwicklung des Vertrags
        """)
