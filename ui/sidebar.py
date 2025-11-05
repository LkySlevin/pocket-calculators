"""
Sidebar-Komponente mit allgemeinen Parametern
"""
import streamlit as st
from .config import HELP_TEXTS
from utils.tax_calculator import calculate_retirement_tax_rate


def render_sidebar():
    """
    Rendert die Sidebar mit allgemeinen Parametern

    Returns:
        dict: Dictionary mit allen Sidebar-Parametern
    """
    st.sidebar.header("⚙️ Allgemeine Parameter")

    monthly_contribution = st.sidebar.number_input(
        "Monatlicher Sparbeitrag (€)",
        min_value=50.0,
        max_value=5000.0,
        value=160.0,
        step=50.0,
        help=HELP_TEXTS["monthly_contribution"]
    )

    years = st.sidebar.slider(
        "Anlagedauer (Jahre)",
        min_value=5,
        max_value=50,
        value=30,
        help=HELP_TEXTS["years"]
    )

    tax_rate = st.sidebar.slider(
        "Persönlicher Steuersatz (%)",
        min_value=0,
        max_value=50,
        value=42,
        help=HELP_TEXTS["tax_rate"]
    ) / 100

    initial_investment = st.sidebar.number_input(
        "💰 Starteinzahlung (€)",
        min_value=0.0,
        max_value=1000000.0,
        value=0.0,
        step=5000.0,
        help="""**Einmaliger Betrag** zu Beginn der Ansparphase.

**Gilt für:**
- ✅ ETF-Sparplan
- ✅ Basisrente (Rürup)
- ❌ Riester (keine Einmalzahlung üblich)

**Typische Anlässe:**
- Erbschaft oder Schenkung
- Jahresbonus oder Abfindung
- Verkaufserlös (Immobilie, etc.)
- Aufgelöstes altes Depot

**Beispiel:**
20.000€ bei 7% Rendite nach 30 Jahren:
→ ca. 152.000€ (vor Steuern)

**Steuerlicher Vorteil bei Basisrente:**
- Einmalzahlung voll absetzbar!
- Bei 42% Steuersatz: 8.400€ Ersparnis bei 20.000€
    """
    )

    st.sidebar.markdown("---")
    st.sidebar.header("👴 Renteneinkommen (für Steuerberechnung)")

    state_pension = st.sidebar.number_input(
        "Erwartete gesetzliche Rente (€/Monat, brutto)",
        min_value=0.0,
        max_value=5000.0,
        value=2500.0,
        step=100.0,
        help=HELP_TEXTS["state_pension"]
    )

    company_pension = st.sidebar.number_input(
        "Erwartete Betriebsrente (€/Monat, brutto)",
        min_value=0.0,
        max_value=3000.0,
        value=1000.0,
        step=100.0,
        help=HELP_TEXTS["company_pension"]
    )

    # Berechne realistischen Steuersatz im Alter basierend auf Gesamteinkommen
    yearly_pension_income = (state_pension + company_pension) * 12
    tax_rate_retirement_calculated = calculate_retirement_tax_rate(yearly_pension_income)

    st.sidebar.info(f"""
**Berechneter Steuersatz im Ruhestand:** {tax_rate_retirement_calculated * 100:.1f}%

Basierend auf:
- Gesetzliche Rente: {state_pension * 12:,.0f}€/Jahr
- Betriebsrente: {company_pension * 12:,.0f}€/Jahr
- **Gesamt: {yearly_pension_income:,.0f}€/Jahr**
""")

    tax_rate_retirement = st.sidebar.slider(
        "Steuersatz im Ruhestand (%) - Anpassbar",
        min_value=0,
        max_value=50,
        value=int(tax_rate_retirement_calculated * 100),
        help=HELP_TEXTS["tax_rate_retirement"]
    ) / 100

    st.sidebar.markdown("---")
    st.sidebar.header("📊 Produkte auswählen")

    # Checkboxen für Produktauswahl
    include_etf = st.sidebar.checkbox("ETF-Sparplan", value=True)
    include_basisrente = st.sidebar.checkbox("Basisrente (Rürup)", value=True)
    include_riester = st.sidebar.checkbox("Riester-Rente", value=True)

    return {
        "monthly_contribution": monthly_contribution,
        "years": years,
        "tax_rate": tax_rate,
        "initial_investment": initial_investment,
        "state_pension": state_pension,
        "company_pension": company_pension,
        "yearly_pension_income": yearly_pension_income,
        "tax_rate_retirement": tax_rate_retirement,
        "include_etf": include_etf,
        "include_basisrente": include_basisrente,
        "include_riester": include_riester,
    }
