"""
Learning Mode - Vollständiger Zugriff auf alle Parameter mit Erklärungen
"""
import streamlit as st
from calculators.etf_calculator import ETFCalculator
from calculators.basisrente_calculator import BasisrenteCalculator
from calculators.riester_calculator import RiesterCalculator
from calculators.privatrente_calculator import PrivatrenteCalculator
from calculators.comparison import Comparison
from ui.sidebar import render_sidebar
from ui.product_tabs import render_product_tabs
from ui.results import display_results
from ui.user_profiling import render_user_profile_form, display_pension_gap_analysis


def render_learning_mode():
    """
    Rendert den Learning Mode - das ist der bisherige Standard-Modus
    mit allen Parametern und detaillierten Erklärungen.
    """
    # Prüfen ob Profil bereits erstellt wurde
    if "user_profile" not in st.session_state or st.session_state.user_profile is None:
        # Profil-Formular anzeigen
        profile = render_user_profile_form()

        if profile:
            # Profil speichern
            st.session_state.user_profile = profile
            st.rerun()
        return

    # Profil existiert bereits - zeige Rechner
    profile = st.session_state.user_profile

    st.title("💰 Altersvorsorge-Vergleichsrechner")
    st.markdown("""
    Vergleichen Sie verschiedene Altersvorsorge-Produkte mit **detaillierten Kostenanalysen** und
    **realistischer Rentensteuer-Berechnung**.

    Im **Learning Mode** haben Sie vollen Zugriff auf alle Parameter und erhalten ausführliche
    Erklärungen zu allen Konzepten.
    """)

    # Sidebar rendern und Parameter erhalten (mit Profil-Daten vorbelegen)
    sidebar_params = render_sidebar(user_profile=profile)

    # Produkt-Tabs rendern
    product_params = render_product_tabs(
        sidebar_params["monthly_contribution"],
        sidebar_params["years"]
    )

    # Berechnung durchführen
    st.markdown("---")

    if st.button("🚀 Berechnung starten", type="primary", use_container_width=True):
        results = []

        # ETF berechnen
        if sidebar_params["include_etf"]:
            with st.spinner("Berechne ETF-Sparplan..."):
                etf_calc = ETFCalculator(
                    monthly_contribution=sidebar_params["monthly_contribution"],
                    years=sidebar_params["years"],
                    annual_return=product_params["etf"]["return"],
                    tax_rate=sidebar_params["tax_rate"],
                    ter=product_params["etf"]["ter"],
                    tax_allowance=product_params["etf"]["tax_allowance"],
                    order_fee=product_params["etf"]["order_fee"],
                    depot_fee_yearly=product_params["etf"]["depot_fee"],
                    spread=product_params["etf"]["spread"],
                    initial_investment=sidebar_params["initial_investment"],
                    rebalancing_count=product_params["etf"]["rebalancing_count"]
                )
                results.append(etf_calc.calculate())

        # Basisrente berechnen
        if sidebar_params["include_basisrente"]:
            with st.spinner("Berechne Basisrente..."):
                basis_calc = BasisrenteCalculator(
                    monthly_contribution=sidebar_params["monthly_contribution"],
                    years=sidebar_params["years"],
                    annual_return=product_params["basisrente"]["return"],
                    tax_rate=sidebar_params["tax_rate"],
                    tax_rate_retirement=sidebar_params["tax_rate_retirement"],
                    effective_costs=product_params["basisrente"]["effective_costs"],
                    honorar_fee=product_params["basisrente"]["honorar_fee"],
                    initial_investment=sidebar_params["initial_investment"]
                )
                results.append(basis_calc.calculate())

        # Riester berechnen
        if sidebar_params["include_riester"]:
            with st.spinner("Berechne Riester-Rente..."):
                riester_calc = RiesterCalculator(
                    monthly_contribution=sidebar_params["monthly_contribution"],
                    years=sidebar_params["years"],
                    annual_return=product_params["riester"]["return"],
                    tax_rate=sidebar_params["tax_rate"],
                    tax_rate_retirement=sidebar_params["tax_rate_retirement"],
                    effective_costs=product_params["riester"]["effective_costs"],
                    children_allowance=product_params["riester"]["children"] * 300,
                    lump_sum_percentage=product_params["riester"]["lump_sum"]
                )
                results.append(riester_calc.calculate())

        # Privatrente berechnen
        if sidebar_params["include_privatrente"]:
            with st.spinner("Berechne Privatrente..."):
                privat_calc = PrivatrenteCalculator(
                    monthly_contribution=sidebar_params["monthly_contribution"],
                    years=sidebar_params["years"],
                    annual_return=product_params["privatrente"]["return"],
                    tax_rate=sidebar_params["tax_rate"],
                    tax_rate_retirement=sidebar_params["tax_rate_retirement"],
                    effective_costs=product_params["privatrente"]["effective_costs"],
                    honorar_fee=product_params["privatrente"]["honorar_fee"],
                    initial_investment=sidebar_params["initial_investment"],
                    payout_option=product_params["privatrente"]["payout_option"],
                    retirement_age=product_params["privatrente"]["retirement_age"]
                )
                results.append(privat_calc.calculate())

        if not results:
            st.warning("⚠️ Bitte wählen Sie mindestens ein Produkt aus!")
        else:
            # Vergleich erstellen
            comp = Comparison(results)

            # Alle Parameter für Ergebnisanzeige zusammenfassen
            all_params = {
                **sidebar_params,
                **product_params,
                "riester_lump_sum": product_params["riester"]["lump_sum"]
            }

            # Ergebnisse anzeigen
            display_results(comp, all_params)

    # Rentenlücken-Analyse anzeigen
    st.markdown("---")
    with st.expander("📊 Ihre persönliche Rentenlücke", expanded=False):
        display_pension_gap_analysis(profile)

    # ChatBot-Bereich
    st.markdown("---")
    with st.expander("💬 Altersvorsorge-Berater (ChatBot)", expanded=False):
        st.markdown("""
        ### 🤖 Ihr persönlicher Altersvorsorge-Berater

        Stellen Sie Fragen zur Altersvorsorge und erhalten Sie fundierte Antworten!

        **Mögliche Fragen:**
        - "Was ist der Unterschied zwischen Riester und Rürup?"
        - "Lohnt sich eine Privatrente für mich?"
        - "Wie hoch sollte mein ETF-Anteil sein?"
        - "Welche steuerlichen Vorteile habe ich bei der Basisrente?"
        """)

        st.info("""
        🚧 **ChatBot in Entwicklung**

        Der KI-gestützte Berater wird in einer zukünftigen Version verfügbar sein und:
        - Individuelle Beratung basierend auf Ihrem Profil
        - Erklärungen zu komplexen Finanzthemen
        - Hilfe bei der Produktauswahl
        - Vergleich verschiedener Strategien
        """)

        # Placeholder für ChatBot
        user_question = st.text_input(
            "Ihre Frage:",
            placeholder="z.B. Sollte ich eher in ETF oder Riester investieren?",
            disabled=True
        )

        if st.button("💬 Frage stellen", disabled=True):
            st.info("ChatBot wird in einer zukünftigen Version verfügbar sein.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Pocket Calculator - Altersvorsorge-Vergleichsrechner</p>
        <p style='font-size: 0.8em;'>Keine Anlageberatung. Alle Berechnungen ohne Gewähr.</p>
    </div>
    """, unsafe_allow_html=True)
