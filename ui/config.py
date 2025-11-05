"""
Streamlit Konfiguration und Hilfstexte für den Altersvorsorge-Rechner
"""
import streamlit as st


def setup_page():
    """Seitenkonfiguration für Streamlit"""
    st.set_page_config(
        page_title="Altersvorsorge Vergleichsrechner",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )


# Hilfstexte mit realen Beispielen
HELP_TEXTS = {
    "monthly_contribution": "Wie viel möchten Sie monatlich investieren?",
    "years": "Wie lange möchten Sie sparen? Je länger, desto stärker der Zinseszinseffekt.",
    "tax_rate": "Ihr aktueller Grenzsteuersatz. Bei 60.000€ Jahreseinkommen ca. 42%.",
    "tax_rate_retirement": "Erwarteter Steuersatz im Rentenalter (meist niedriger). Wird basierend auf Ihrer Gesamtrente berechnet.",

    # ETF
    "etf_return": "Historische Rendite MSCI World: ~7-8% p.a. (vor Kosten). Konservativ: 5-6%, Optimistisch: 8-9%",
    "etf_ter": """**TER (Total Expense Ratio)** - Gesamtkostenquote des ETFs.

**Beispiele:**
- MSCI World ETFs: 0,12% - 0,25% p.a.
- iShares Core MSCI World: 0,20% p.a.
- Vanguard FTSE All-World: 0,22% p.a.
- Aktiv gemanagte Fonds: oft 1,5% - 2,5% p.a.
    """,
    "etf_order_fee": """**Ordergebühr** pro Sparplan-Ausführung.

**Beispiele:**
- Trade Republic: 0,00€ (kostenlos)
- Scalable Capital: 0,00€ (kostenlos)
- ING: 1,75% (mind. 1,50€)
- Comdirect: 1,5% (ab 25€ Sparrate)
- DKB: 1,50€ pro Ausführung
    """,
    "etf_depot_fee": """**Depotführungsgebühr** pro Jahr.

**Beispiele:**
- Trade Republic: 0,00€
- Scalable Capital: 0,00€
- flatex: 0,00€
- Comdirect: 0,00€ (bei Sparplan aktiv)
- Traditionelle Banken: oft 20-60€ p.a.
    """,
    "etf_spread": """**Spread** = Geld-Brief-Spanne beim Kauf.

**Beispiele:**
- Große ETFs (MSCI World): 0,01% - 0,05%
- Kleinere ETFs: 0,1% - 0,3%
- Exotische ETFs: bis 1%

Bei monatlichen Käufen über viele Jahre summiert sich dieser Kostenfaktor!
    """,
    "etf_rebalancing": """**Umschichtungen** = Komplette Auflösung des Sparplans und Neuanlage in anderen ETF.

**Was passiert bei einer Umschichtung:**
1. 📊 **Kapitalertragssteuer** auf realisierte Gewinne (Freibetrag wird angerechnet)
2. 💰 **Ordergebühren** für Verkauf und Neukauf
3. 📉 **Spread-Kosten** (zweimal: Verkauf + Kauf)

**Beispiel:** 4 Umschichtungen über 30 Jahre können mehrere zehntausend Euro kosten!

**Typische Szenarien:**
- 0: Buy & Hold (optimal für langfristige Anleger)
- 1-2: Gelegentlicher ETF-Wechsel (z.B. wegen besserer Konditionen)
- 3-5: Häufigere Strategiewechsel (teuer!)

**💡 Tipp:** Vermeiden Sie unnötige Umschichtungen - sie kosten Rendite!
    """,

    # Basisrente
    "basis_return": """**Erwartete Rendite** der Basisrente.

**Typische Werte:**
- Klassische Versicherung: 1% - 2,5% p.a. (garantiert + Überschuss)
- Fondsgebundene Tarife: 3% - 5% p.a. (historisch, nicht garantiert)
- ETF-Basisrente: 4% - 6% p.a. (nach Kosten)

**Vorsicht:** Garantien reduzieren die Rendite erheblich!
    """,
    "basis_effective_costs": """**Effektivkosten** - Alle laufenden Kosten zusammengefasst.

**Typische Werte:**
- Nettotarife/Honorartarife: 0,5% - 1,0% p.a.
- Bruttotarife: 1,5% - 2,5% p.a.
- Klassische Tarife: oft höher durch Garantien

**Was ist enthalten:**
- Verwaltungskosten
- Garantiekosten
- Fondskosten (TER)
- Verteilte Abschlusskosten

**Tipp:** Nutzen Sie den Effektivkostenrechner zur Berechnung!
    """,

    # Riester
    "riester_return": """**Erwartete Rendite** der Riester-Rente.

**Typische Werte:**
- Klassische Versicherung: 0,5% - 2% p.a. (wegen Garantiepflicht)
- Fondssparpläne: 2% - 4% p.a. (nach Kosten)
- Banksparplan: 1% - 2% p.a.

**Problem:** Beitragsgarantie ist Pflicht → reduziert Rendite erheblich!
    """,
    "riester_effective_costs": """**Effektivkosten** - Alle laufenden Kosten zusammengefasst.

**Typische Werte:**
- Banksparplan: 0,5% - 1,5% p.a.
- Fondssparplan: 1,5% - 2,5% p.a.
- Versicherung: 2,0% - 3,0% p.a.

**Was ist enthalten:**
- Verwaltungskosten
- Garantiekosten (Pflicht bei Riester!)
- Fondskosten (TER)
- Verteilte Abschlusskosten

**Hinweis:** Bei Riester oft höher wegen Beitragsgarantie!

**Tipp:** Nutzen Sie den Effektivkostenrechner zur Berechnung!
    """,
    "riester_children": """**Anzahl Kinder** für Kinderzulage.

**Zulagen:**
- Grundzulage: 175€ pro Jahr
- Kinderzulage: 300€ pro Jahr pro Kind (ab 2008 geboren)
- Kinderzulage: 185€ pro Jahr (vor 2008 geboren)

**Wichtig:** Zulagen müssen jährlich beantragt werden!
    """,
    "riester_acquisition": """**Abschlusskosten** (über 5 Jahre verteilt).

**Typische Werte:**
- Honorartarife: 0€ oder 150-300€ fix
- Standard-Tarife: 3% - 6% der Beitragssumme

**Beispiel:** Bei 2.100€/Jahr über 30 Jahre (63.000€):
- 3%: 1.890€
- 6%: 3.780€

**Vorsicht:** Oft sehr hohe Kosten bei klassischen Tarifen!
    """,
    "riester_admin": """**Verwaltungsgebühr** pro Jahr.

**Typische Werte:**
- Günstige Tarife: 15-40€ p.a.
- Mittlere Tarife: 40-80€ p.a.
- Teure Tarife: 80-120€ p.a.

Verbraucherschützer raten zu Tarifen unter 50€ p.a.!
    """,

    # Rente
    "state_pension": """**Erwartete gesetzliche Rente** (brutto).

**Richtwerte:**
- Durchschnittsverdiener (45 Jahre): ca. 1.500€
- Gutverdiener: 2.000€ - 2.500€
- Geringverdiener: 800€ - 1.200€

Ihre voraussichtliche Rente finden Sie in Ihrer jährlichen Renteninformation!
    """,
    "company_pension": """**Betriebsrente** (brutto).

**Typische Werte:**
- Kleine Betriebsrente: 200€ - 500€
- Mittlere Betriebsrente: 500€ - 1.000€
- Große Betriebsrente: 1.000€ - 2.000€

Prüfen Sie Ihre betriebliche Altersversorgung!
    """,
}
