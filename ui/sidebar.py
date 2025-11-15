"""
Sidebar-Komponente mit allgemeinen Parametern
"""
import streamlit as st
from .config import HELP_TEXTS
from utils.tax_calculator import calculate_retirement_tax_rate


def render_sidebar(user_profile: dict = None):
    """
    Rendert die Sidebar mit allgemeinen Parametern

    Args:
        user_profile: Optional - User-Profil für automatische Wert-Vorbelegung

    Returns:
        dict: Dictionary mit allen Sidebar-Parametern
    """
    st.sidebar.header("⚙️ Allgemeine Parameter")

    # Standardwerte aus Profil übernehmen (falls vorhanden)
    if user_profile:
        default_years = user_profile.get("years_until_retirement", 30)
        default_tax_rate = int(user_profile.get("tax_rate", 0.42) * 100)
        st.sidebar.info(f"✅ Werte aus Ihrem Profil vorbelegt")
    else:
        default_years = 30
        default_tax_rate = 42

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
        value=default_years,
        help=HELP_TEXTS["years"]
    )

    tax_rate = st.sidebar.slider(
        "Persönlicher Steuersatz (%)",
        min_value=0,
        max_value=50,
        value=default_tax_rate,
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
    st.sidebar.header("📈 Dynamiken & Inflation")

    st.sidebar.markdown("""
    **Beitragsdynamik** erhöht Ihren Sparbeitrag jährlich.
    **Inflation** berücksichtigt die Kaufkraft im Alter.
    """)

    # Beitragsdynamik Ansparphase
    contribution_dynamics = st.sidebar.slider(
        "Beitragsdynamik Ansparphase (%/Jahr)",
        min_value=0.0,
        max_value=5.0,
        value=2.0,
        step=0.5,
        help="""**Jährliche Steigerung Ihres Sparbeitrags**

Typische Werte:
- **0%**: Konstanter Beitrag (einfach, planbar)
- **1-2%**: Inflationsausgleich (empfohlen)
- **2-3%**: Gehaltsanpassung mitwachsen
- **3-5%**: Karriereentwicklung / Sparquote erhöhen

**Beispiel:**
- Start: 500 €/Monat
- Nach 10 Jahren (2% Dynamik): 610 €/Monat
- Nach 30 Jahren (2% Dynamik): 906 €/Monat

**Vorteil:** Höheres Endkapital ohne Verzicht heute!
**Nachteil:** Langfristige Bindung höherer Beträge
        """
    ) / 100

    # Rentendynamik Auszahlungsphase
    pension_dynamics = st.sidebar.slider(
        "Rentendynamik Auszahlungsphase (%/Jahr)",
        min_value=0.0,
        max_value=3.0,
        value=1.0,
        step=0.5,
        help="""**Jährliche Steigerung Ihrer Rente**

Typische Werte:
- **0%**: Konstante Rente (einfach)
- **1%**: Teilweiser Inflationsausgleich
- **2%**: Vollständiger Inflationsausgleich (meist)
- **3%**: Überinflationäre Steigerung

**Beispiel:**
- Start: 2.000 €/Monat
- Nach 10 Jahren (1% Dynamik): 2.209 €/Monat
- Nach 25 Jahren (1% Dynamik): 2.565 €/Monat

**Vorteil:** Kaufkraft bleibt erhalten
**Nachteil:** Anfangsrente ist niedriger (mehr Kapital nötig)
        """
    ) / 100

    # Inflationsrate
    inflation_rate = st.sidebar.slider(
        "Erwartete Inflation (%/Jahr)",
        min_value=0.0,
        max_value=5.0,
        value=2.0,
        step=0.5,
        help="""**Durchschnittliche Inflation über Anlagedauer**

Historische Werte (Deutschland):
- **1991-2020**: ca. 1,8% p.a.
- **2000-2020**: ca. 1,4% p.a.
- **2010-2020**: ca. 1,2% p.a.
- **2021-2024**: ca. 5-8% p.a. (Ausnahme!)
- **EZB-Ziel**: 2% p.a. (langfristig)

**Empfehlung:** 2% für langfristige Planung

**Bedeutung:**
- 100.000 € heute = 74.000 € Kaufkraft in 15 Jahren (bei 2% Inflation)
- 2.000 € Rente heute = 1.480 € Kaufkraft in 15 Jahren

**Wichtig für Altersvorsorge:** Immer real (inflationsbereinigt) rechnen!
        """
    ) / 100

    # Inflationsanpassung anzeigen
    show_real_values = st.sidebar.checkbox(
        "Inflationsbereinigte Werte anzeigen",
        value=True,
        help="Zeigt Kaufkraft (real) statt nominaler Beträge"
    )

    st.sidebar.markdown("---")
    st.sidebar.header("📊 Produkte auswählen")

    # Checkboxen für Produktauswahl
    include_etf = st.sidebar.checkbox("ETF-Sparplan", value=True)
    include_basisrente = st.sidebar.checkbox("Basisrente (Rürup)", value=True)
    include_riester = st.sidebar.checkbox("Riester-Rente", value=True)
    include_privatrente = st.sidebar.checkbox("Privatrente", value=True)

    return {
        "monthly_contribution": monthly_contribution,
        "years": years,
        "tax_rate": tax_rate,
        "initial_investment": initial_investment,
        "state_pension": state_pension,
        "company_pension": company_pension,
        "yearly_pension_income": yearly_pension_income,
        "tax_rate_retirement": tax_rate_retirement,
        "contribution_dynamics": contribution_dynamics,
        "pension_dynamics": pension_dynamics,
        "inflation_rate": inflation_rate,
        "show_real_values": show_real_values,
        "include_etf": include_etf,
        "include_basisrente": include_basisrente,
        "include_riester": include_riester,
        "include_privatrente": include_privatrente,
    }
