"""
Produktspezifische Parameter-Tabs (ETF, Basisrente, Riester)
"""
import streamlit as st
from .config import HELP_TEXTS


def render_etf_tab():
    """
    Rendert Tab für ETF-Parameter

    Returns:
        dict: Dictionary mit ETF-Parametern
    """
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Rendite & Grundkosten")

        etf_return = st.number_input(
            "Erwartete jährliche Rendite (%)",
            min_value=0.0,
            max_value=20.0,
            value=7.0,
            step=0.1,
            key="etf_return",
            help=HELP_TEXTS["etf_return"]
        ) / 100

        etf_ter = st.number_input(
            "TER - Gesamtkostenquote (%)",
            min_value=0.0,
            max_value=3.0,
            value=0.2,
            step=0.05,
            key="etf_ter",
            help=HELP_TEXTS["etf_ter"]
        ) / 100

    with col2:
        st.subheader("Steuerparameter")

        etf_tax_allowance = st.number_input(
            "Sparerpauschbetrag pro Jahr (€)",
            min_value=0,
            max_value=2000,
            value=1000,
            step=100,
            key="etf_allowance",
            help="1.000€ für Singles, 2.000€ für Paare (ab 2023)"
        )

    # Erweiterte Optionen
    with st.expander("🔍 Erweiterte Kostenoptionen"):
        col1, col2 = st.columns(2)

        with col1:
            etf_order_fee = st.number_input(
                "Ordergebühr pro Ausführung (€)",
                min_value=0.0,
                max_value=10.0,
                value=1.0,
                step=0.25,
                key="etf_order",
                help=HELP_TEXTS["etf_order_fee"]
            )

            etf_spread = st.number_input(
                "Spread / Geld-Brief-Spanne (%)",
                min_value=0.0,
                max_value=5.0,
                value=0.2,
                step=0.05,
                key="etf_spread",
                help=HELP_TEXTS["etf_spread"]
            ) / 100

        with col2:
            etf_depot_fee = st.number_input(
                "Depotgebühr pro Jahr (€)",
                min_value=0.0,
                max_value=200.0,
                value=0.0,
                step=10.0,
                key="etf_depot",
                help=HELP_TEXTS["etf_depot_fee"]
            )

    # Umschichtungen
    with st.expander("🔄 Umschichtungen"):
        st.markdown("""
        **Umschichtung** bedeutet: Auflösung des Sparplans und Neuanlage in einen anderen ETF.

        Bei jeder Umschichtung fallen an:
        - 📊 **Kapitalertragssteuer** auf realisierte Gewinne (mit Freibetrag)
        - 💰 **Ordergebühren** für Verkauf und Neukauf
        - 📉 **Spread-Kosten** (Verkaufs- und Kaufs-Spread)
        """)

        etf_rebalancing = st.number_input(
            "Anzahl Umschichtungen während Laufzeit",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            key="etf_rebalancing",
            help=HELP_TEXTS["etf_rebalancing"]
        )

        if etf_rebalancing > 0:
            st.info(f"💡 Der Freibetrag ({etf_tax_allowance:,.0f}€/Jahr) wird bei jeder Umschichtung anteilig angerechnet.")

    # Auszahlungsoptionen
    with st.expander("💰 Auszahlung im Rentenalter"):
        st.markdown("""
        **Wie möchten Sie Ihr ETF-Vermögen im Rentenalter nutzen?**

        Im Gegensatz zu Riester/Basisrente haben Sie bei ETFs freie Wahl:
        - 💵 **Einmalauszahlung**: Gesamtes Kapital auf einmal (z.B. für große Anschaffungen)
        - 📊 **Verrentung**: Monatliche Entnahmen über viele Jahre (Kapitalerhalt möglich)
        - 🔀 **Kombination**: Teil als Einmalzahlung, Rest als Rente
        """)

        etf_payout_strategy = st.radio(
            "Auszahlungsstrategie",
            options=["Einmalauszahlung (100%)", "Verrentung (4% Entnahme p.a.)", "Kombination"],
            index=0,
            key="etf_payout_strategy",
            help="Wählen Sie, wie Sie Ihr ETF-Vermögen im Rentenalter nutzen möchten."
        )

        etf_lump_sum_percentage = 0.0
        if etf_payout_strategy == "Einmalauszahlung (100%)":
            etf_lump_sum_percentage = 100.0
            st.info("💡 Bei Einmalauszahlung wird das gesamte Kapital sofort entnommen und versteuert.")
        elif etf_payout_strategy == "Kombination":
            etf_lump_sum_percentage = st.slider(
                "Anteil Einmalauszahlung (%)",
                min_value=0.0,
                max_value=100.0,
                value=30.0,
                step=5.0,
                key="etf_lump_sum_percentage",
                help="Der Rest wird als monatliche Rente (4% p.a.) ausgezahlt."
            )
            st.info(f"💡 {etf_lump_sum_percentage:.0f}% sofort, {100-etf_lump_sum_percentage:.0f}% als monatliche Rente (4% p.a.)")

    return {
        "return": etf_return,
        "ter": etf_ter,
        "tax_allowance": etf_tax_allowance,
        "order_fee": etf_order_fee,
        "spread": etf_spread,
        "depot_fee": etf_depot_fee,
        "rebalancing_count": etf_rebalancing,
        "lump_sum_percentage": etf_lump_sum_percentage,
    }


def render_basisrente_tab(monthly_contribution: float, years: int):
    """
    Rendert Tab für Basisrente-Parameter

    Args:
        monthly_contribution: Monatlicher Sparbeitrag
        years: Anlagedauer

    Returns:
        dict: Dictionary mit Basisrente-Parametern
    """
    st.subheader("Vertragstyp")

    tarif_typ = st.radio(
        "Welchen Tariftyp möchten Sie vergleichen?",
        options=["Bruttopolice", "Nettopolice / Honorartarif"],
        index=0,
        key="basis_tarif_typ",
        help="""
**Bruttopolice:**
- Standardtarif mit Abschluss- und Verwaltungskosten eingepreist
- Höhere laufende Kosten (1,5% - 2,5% p.a.)
- Provision für Vermittler eingerechnet

**Nettopolice / Honorartarif:**
- Transparente Kostenstruktur
- Niedrigere Effektivkosten (0,5% - 1,0% p.a.)
- Separate Honorar- oder Beratungsgebühren
- Oft bessere Rendite durch niedrigere Kosten
        """
    )

    is_netto = (tarif_typ == "Nettopolice / Honorartarif")

    st.subheader("Rendite")

    basis_return = st.number_input(
        "Erwartete jährliche Rendite (%)",
        min_value=0.0,
        max_value=15.0,
        value=7.0,
        step=0.1,
        key="basis_return",
        help=HELP_TEXTS["basis_return"]
    ) / 100

    st.subheader("Kosten")

    if is_netto:
        # Nettopolice: Niedrigere Effektivkosten + einmalige Honorargebühr
        basis_effective_costs = st.number_input(
            "Effektivkosten (% p.a.)",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            key="basis_effective_costs_netto",
            help="Bei Nettotarifen deutlich niedriger: 0,5% - 1,0% p.a."
        ) / 100

        basis_honorar = st.number_input(
            "Einmalige Honorargebühr (€)",
            min_value=0.0,
            max_value=10000.0,
            value=2000.0,
            step=500.0,
            key="basis_honorar",
            help="Typisch: 1.500€ - 5.000€ einmalig für Beratung und Vermittlung"
        )

        st.info(f"""
💡 **Nettopolice gewählt:**
- Niedrige laufende Kosten: {basis_effective_costs * 100:.1f}% p.a.
- Einmalige Honorargebühr: {basis_honorar:,.0f} €
- Transparente Kostenstruktur
        """)
    else:
        # Bruttopolice: Höhere Effektivkosten, dafür keine Honorargebühr
        basis_effective_costs = st.number_input(
            "Effektivkosten (% p.a.)",
            min_value=0.0,
            max_value=5.0,
            value=1.5,
            step=0.1,
            key="basis_effective_costs_brutto",
            help=HELP_TEXTS["basis_effective_costs"]
        ) / 100

        basis_honorar = 0.0  # Bei Bruttopolice keine separate Honorargebühr

    # Effektivkosten-Rechner (nur bei Bruttopolice relevant)
    if not is_netto:
        with st.expander("🧮 Effektivkostenrechner"):
            st.markdown("""
            **Berechnen Sie die Effektivkosten basierend auf den Vertragskosten:**

            Die Effektivkosten setzen sich aus verschiedenen Kostenarten zusammen.
            """)

            total_contributions = monthly_contribution * 12 * years

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Einmalige Kosten**")

                # Abschlusskosten
                abschluss_prozent = st.slider(
                    "Abschlusskosten (% der Beitragssumme)",
                    0.0, 6.0, 2.5, 0.25,
                    key="basis_abschluss"
                )
                abschluss_euro = total_contributions * (abschluss_prozent / 100)
                st.caption(f"= {abschluss_euro:,.0f} €")

            with col2:
                st.markdown("**Laufende Kosten (jährlich)**")

                # Verwaltungskosten
                verwaltung_prozent = st.slider(
                    "Verwaltungskosten (% p.a.)",
                    0.0, 2.0, 0.5, 0.1,
                    key="basis_verwaltung"
                )


                # Fondskosten
                fonds_prozent = st.slider(
                    "Fondskosten / TER (% p.a.)",
                    0.0, 2.0, 0.2, 0.1,
                    key="basis_fonds"
                )

            # Berechnung der Effektivkosten
            # Einmalige Kosten werden auf die Laufzeit verteilt
            abschluss_pro_jahr = (abschluss_euro / total_contributions) / years * 100

            # Gesamte jährliche Kosten
            effektiv_gesamt = abschluss_pro_jahr + verwaltung_prozent + fonds_prozent

            st.markdown("---")
            st.markdown("**💡 Berechnete Effektivkosten:**")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Abschluss (verteilt)", f"{abschluss_pro_jahr:.2f}% p.a.")
            with col2:
                st.metric("Laufende Kosten", f"{verwaltung_prozent + fonds_prozent:.2f}% p.a.")
            with col3:
                st.metric("🎯 Gesamt", f"{effektiv_gesamt:.2f}% p.a.")

            st.info(f"💡 **Tipp:** Übernehmen Sie die berechneten {effektiv_gesamt:.2f}% in das Feld 'Effektivkosten' oben.")

    return {
        "return": basis_return,
        "effective_costs": basis_effective_costs,
        "honorar_fee": basis_honorar,
    }


def render_riester_tab(monthly_contribution: float, years: int):
    """
    Rendert Tab für Riester-Parameter

    Args:
        monthly_contribution: Monatlicher Sparbeitrag
        years: Anlagedauer

    Returns:
        dict: Dictionary mit Riester-Parametern
    """
    st.subheader("Produktvariante")

    riester_variante = st.selectbox(
        "Welche Riester-Variante möchten Sie vergleichen?",
        options=["Fondsgebunden", "Klassisch (Versicherung)"],
        index=0,
        key="riester_variante",
        help="""
**Fondsgebunden:**
- Höheres Renditepotenzial (2% - 4%)
- Beitragsgarantie durch Sicherungskapital
- Zusätzliche Fondskosten (TER)
- Schwankungen möglich

**Klassisch (Versicherung):**
- Garantierte Verzinsung + Überschüsse
- Sehr niedrige Rendite (0,5% - 2%)
- Höhere Garantiekosten durch Beitragsgarantie
- Keine Fondskosten
        """
    )

    is_fondsgebunden = (riester_variante == "Fondsgebunden")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Rendite")

        # Unterschiedliche Defaultwerte je nach Variante
        default_rendite = 3.0 if is_fondsgebunden else 1.5

        riester_return = st.number_input(
            "Erwartete jährliche Rendite (%)",
            min_value=0.0,
            max_value=10.0,
            value=default_rendite,
            step=0.1,
            key="riester_return",
            help=HELP_TEXTS["riester_return"]
        ) / 100

    with col2:
        st.subheader("Zulagen")

        riester_children = st.number_input(
            "Anzahl Kinder",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            key="riester_children",
            help=HELP_TEXTS["riester_children"]
        )

    # Zulagen-Info
    with st.expander("🎁 Ihre Riester-Zulagen"):
        grundzulage = 175
        kinderzulage_total = riester_children * 300
        total_allowances = (grundzulage + kinderzulage_total) * years

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Grundzulage/Jahr", f"{grundzulage} €")
        with col2:
            st.metric("Kinderzulage/Jahr", f"{kinderzulage_total} €")
        with col3:
            st.metric(f"Gesamt ({years} Jahre)", f"{total_allowances:,.0f} €")

    # Kosten-Eingabe
    st.subheader("Kosten")

    total_contributions = monthly_contribution * 12 * years

    # Abschluss-/Vertriebskosten
    col1, col2 = st.columns(2)
    with col1:
        abschluss_typ = st.radio(
            "Abschlusskosten eingeben als:",
            options=["Prozent der Beitragssumme", "Absoluter Betrag (€)"],
            index=0,
            key="riester_abschluss_typ"
        )

    with col2:
        if abschluss_typ == "Prozent der Beitragssumme":
            abschluss_prozent = st.number_input(
                "Abschlusskosten (% der Beitragssumme)",
                min_value=0.0,
                max_value=10.0,
                value=3.5 if is_fondsgebunden else 4.0,
                step=0.25,
                key="riester_abschluss_proz"
            )
            abschluss_euro = total_contributions * (abschluss_prozent / 100)
            st.caption(f"= {abschluss_euro:,.0f} €")
        else:
            abschluss_euro = st.number_input(
                "Abschlusskosten (€)",
                min_value=0.0,
                max_value=20000.0,
                value=2000.0,
                step=100.0,
                key="riester_abschluss_euro"
            )

    # Laufende Verwaltungs-/Vertriebskosten
    verwaltung_kosten = st.number_input(
        "Laufende Verwaltungs-/Vertriebskosten (% p.a.)",
        min_value=0.0,
        max_value=3.0,
        value=0.7 if is_fondsgebunden else 1.0,
        step=0.1,
        key="riester_verwaltung",
        help="Jährliche Kosten für Verwaltung und Vertrieb"
    )

    # Fondskosten (nur bei fondsgebunden)
    if is_fondsgebunden:
        fonds_kosten = st.number_input(
            "Fondskosten / TER (% p.a.)",
            min_value=0.0,
            max_value=3.0,
            value=0.8,
            step=0.1,
            key="riester_fonds",
            help="Total Expense Ratio der zugrunde liegenden Fonds"
        )
    else:
        fonds_kosten = 0.0

    # Wechsel-/Übertragungskosten (optional)
    with st.expander("➕ Weitere Kosten (optional)"):
        wechsel_kosten = st.number_input(
            "Wechsel-/Übertragungskosten (€ einmalig)",
            min_value=0.0,
            max_value=1000.0,
            value=0.0,
            step=50.0,
            key="riester_wechsel",
            help="Falls Sie später den Anbieter wechseln möchten"
        )

    # Berechnung der Effektivkosten
    st.markdown("---")
    st.markdown("**📊 Berechnete Effektivkosten:**")

    # Abschlusskosten auf Laufzeit verteilen
    abschluss_pro_jahr = (abschluss_euro / total_contributions) / years * 100 if total_contributions > 0 else 0

    # Wechselkosten auf Laufzeit verteilen (falls vorhanden)
    wechsel_pro_jahr = (wechsel_kosten / total_contributions) / years * 100 if wechsel_kosten > 0 else 0

    # Gesamte Effektivkosten
    riester_effective_costs = (abschluss_pro_jahr + verwaltung_kosten + fonds_kosten + wechsel_pro_jahr) / 100

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Abschluss (verteilt)", f"{abschluss_pro_jahr:.2f}% p.a.")
    with col2:
        st.metric("Verwaltung", f"{verwaltung_kosten:.2f}% p.a.")
    with col3:
        if is_fondsgebunden:
            st.metric("Fonds (TER)", f"{fonds_kosten:.2f}% p.a.")
        else:
            st.metric("Fonds (TER)", "0.00% p.a.")
    with col4:
        st.metric("🎯 Gesamt", f"{riester_effective_costs * 100:.2f}% p.a.")

    if is_fondsgebunden:
        st.info(f"""
💡 **Fondsgebundene Riester:** Effektivkosten = {riester_effective_costs * 100:.2f}% p.a.
- Höheres Renditepotenzial durch Fonds
- Zusätzliche Fondskosten werden berücksichtigt
        """)
    else:
        st.info(f"""
💡 **Klassische Riester:** Effektivkosten = {riester_effective_costs * 100:.2f}% p.a.
- Garantierte Verzinsung (sehr niedrig)
- Keine Fondskosten
        """)

    # Auszahlungsoptionen
    with st.expander("💶 Auszahlungsoptionen bei Rentenbeginn"):
        st.markdown("**30%-Regelung** für Riester-Rente")

        riester_lump_sum = st.slider(
            "Einmalauszahlung bei Rentenbeginn (%)",
            min_value=0,
            max_value=30,
            value=0,
            step=5,
            key="riester_lump",
            help="""**30%-Regelung** bei Verträgen ab 2005 (20% bei älteren Verträgen).

⚠️ **WICHTIG - Steuerliche Folgen:**

Die Einmalauszahlung ist **voll steuerpflichtig** und wird zu Ihrem Einkommen
im Auszahlungsjahr addiert! Dies kann Ihren Steuersatz erheblich erhöhen.

**Beispiel:**
- Riester-Kapital: 50.000€
- Einmalauszahlung (30%): 15.000€
- Ihr sonstiges Einkommen: 40.000€
- **Gesamteinkommen: 55.000€**

Ohne Riester: Steuersatz ~32%
Mit Riester: Steuersatz ~37%

→ Steuer auf 15.000€: ~5.600€
→ Netto bleiben nur: ~9.400€

**Strategien:**
1. In Jahr mit niedrigem Einkommen auszahlen (z.B. Teilzeit)
2. Komplett auf Einmalauszahlung verzichten → höhere monatliche Rente
3. Nach Renteneintritt warten (niedrigeres Einkommen)
            """
        )

        if riester_lump_sum > 0:
            st.warning(f"""
⚠️ **Sie haben {riester_lump_sum}% Einmalauszahlung gewählt.**

Die verbleibenden {100 - riester_lump_sum}% werden monatlich verentet.

**Beachten Sie:**
- Einmalauszahlung voll steuerpflichtig im Auszahlungsjahr
- Kann Ihren Steuersatz deutlich erhöhen
- Prüfen Sie die steuerlichen Auswirkungen genau!
            """)

    return {
        "return": riester_return,
        "effective_costs": riester_effective_costs,
        "children": riester_children,
        "lump_sum": riester_lump_sum,
    }


def render_product_tabs(monthly_contribution: float, years: int):
    """
    Rendert alle Produkt-Tabs

    Args:
        monthly_contribution: Monatlicher Sparbeitrag
        years: Anlagedauer

    Returns:
        dict: Dictionary mit allen Produkt-Parametern
    """
    st.header("🔧 Produktspezifische Parameter")
    tab1, tab2, tab3 = st.tabs(["📈 ETF-Sparplan", "🏛️ Basisrente (Rürup)", "🎁 Riester-Rente"])

    with tab1:
        etf_params = render_etf_tab()

    with tab2:
        basis_params = render_basisrente_tab(monthly_contribution, years)

    with tab3:
        riester_params = render_riester_tab(monthly_contribution, years)

    return {
        "etf": etf_params,
        "basisrente": basis_params,
        "riester": riester_params,
    }
