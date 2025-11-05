#!/usr/bin/env python3
"""
Streamlit Web-App für Altersvorsorge-Vergleich - Erweiterte Version
Mit detaillierten Kosten, Tooltips und Rentensteuer-Berechnung
"""
import streamlit as st
from calculators.etf_calculator import ETFCalculator
from calculators.basisrente_calculator import BasisrenteCalculator
from calculators.riester_calculator import RiesterCalculator
from calculators.comparison import Comparison
from ui.config import setup_page
from ui.sidebar import render_sidebar
from ui.product_tabs import render_product_tabs
from ui.results import display_results


# Seitenkonfiguration
setup_page()

# Titel
st.title("💰 Altersvorsorge-Vergleichsrechner")
st.markdown("""
Vergleichen Sie verschiedene Altersvorsorge-Produkte mit **detaillierten Kostenanalysen** und
**realistischer Rentensteuer-Berechnung**.
""")

# Sidebar rendern und Parameter erhalten
sidebar_params = render_sidebar()

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

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Pocket Calculator - Altersvorsorge-Vergleichsrechner (Erweiterte Version)</p>
    <p style='font-size: 0.8em;'>Keine Anlageberatung. Alle Berechnungen ohne Gewähr.</p>
    <p style='font-size: 0.8em;'>Mit realen Kostenbeispielen von Trade Republic, flatex und typischen Versicherungstarifen.</p>
</div>
""", unsafe_allow_html=True)
