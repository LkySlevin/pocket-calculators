"""
Intelligent Mode - Automatische Optimierung und Suche nach besten Angeboten
"""
import streamlit as st
from ui.user_profiling import render_user_profile_form, display_pension_gap_analysis


def render_intelligent_mode():
    """
    Rendert den Intelligent Mode mit automatischer Optimierung.
    """
    # Prüfen ob Profil bereits erstellt wurde
    if "user_profile" not in st.session_state or st.session_state.user_profile is None:
        # Profil-Formular anzeigen
        profile = render_user_profile_form()

        if profile:
            # Profil speichern
            st.session_state.user_profile = profile
            st.session_state.optimization_params = None  # Reset
            st.rerun()
        return

    # Profil existiert - prüfe ob Optimierungsparameter gesetzt sind
    profile = st.session_state.user_profile

    if st.session_state.get("optimization_params") is None:
        # Zeige Optimierungsparameter-Formular
        render_optimization_params_form(profile)
        return

    # Optimierungsparameter existieren - zeige Ergebnisse
    optimization_params = st.session_state.optimization_params
    render_optimization_results(profile, optimization_params)


def render_optimization_params_form(profile: dict):
    """
    Rendert das Formular für Optimierungsparameter.

    Args:
        profile: User-Profil Dictionary
    """
    st.title("🤖 Intelligent Mode - Optimierungsparameter")

    st.markdown("""
    Der Intelligent Mode findet die optimale Altersvorsorge-Strategie für Ihre Situation.

    Geben Sie zunächst Ihre Präferenzen und Rahmenbedingungen ein.
    """)

    # Rentenlücken-Analyse zuerst anzeigen
    display_pension_gap_analysis(profile)

    st.markdown("---")
    st.subheader("🎯 Ihre Optimierungsziele")

    st.markdown("""
    Gewichten Sie die verschiedenen Ziele nach Ihrer persönlichen Präferenz:
    """)

    col1, col2 = st.columns(2)

    with col1:
        goal_return = st.slider(
            "📈 Maximale Rendite",
            min_value=0,
            max_value=10,
            value=8,
            help="Wie wichtig ist Ihnen eine hohe Rendite?"
        )

        goal_flexibility = st.slider(
            "🔄 Flexibilität",
            min_value=0,
            max_value=10,
            value=6,
            help="Wie wichtig ist es Ihnen, jederzeit auf Ihr Geld zugreifen zu können?"
        )

        goal_simplicity = st.slider(
            "🎯 Einfachheit",
            min_value=0,
            max_value=10,
            value=5,
            help="Möchten Sie möglichst wenig Aufwand haben?"
        )

    with col2:
        goal_security = st.slider(
            "🛡️ Sicherheit",
            min_value=0,
            max_value=10,
            value=7,
            help="Wie wichtig ist Ihnen Kapitalsicherheit?"
        )

        goal_tax_benefits = st.slider(
            "💰 Steuervorteile",
            min_value=0,
            max_value=10,
            value=7,
            help="Wie wichtig sind Ihnen Steuervorteile?"
        )

        goal_legacy = st.slider(
            "👨‍👩‍👧‍👦 Vererbbarkeit",
            min_value=0,
            max_value=10,
            value=5,
            help="Wie wichtig ist es, dass Ihr Vermögen vererbbar ist?"
        )

    st.markdown("---")
    st.subheader("💸 Sparbudget & Restriktionen")

    col1, col2 = st.columns(2)

    with col1:
        min_monthly = st.number_input(
            "Minimale monatliche Sparrate (€)",
            min_value=0.0,
            max_value=5000.0,
            value=100.0,
            step=50.0,
            help="Mindestbetrag, den Sie monatlich sparen möchten"
        )

        max_monthly = st.number_input(
            "Maximale monatliche Sparrate (€)",
            min_value=min_monthly,
            max_value=10000.0,
            value=500.0,
            step=50.0,
            help="Maximalbetrag, den Sie monatlich sparen können"
        )

    with col2:
        existing_savings = st.number_input(
            "Vorhandenes Kapital für Einmalanlage (€)",
            min_value=0.0,
            max_value=1000000.0,
            value=0.0,
            step=5000.0,
            help="Falls Sie einen Einmalbetrag anlegen möchten"
        )

        allow_riester = st.checkbox(
            "Riester-Rente einbeziehen",
            value=True if profile.get("children", 0) > 0 else True,
            help="Riester ist besonders attraktiv bei Kindern"
        )

    st.markdown("---")
    st.subheader("⚙️ Zusätzliche Präferenzen")

    col1, col2 = st.columns(2)

    with col1:
        prefer_etf = st.checkbox(
            "Präferenz für ETF-Sparpläne",
            value=True,
            help="ETFs sind kostengünstig und flexibel"
        )

        avoid_insurance = st.checkbox(
            "Versicherungsprodukte vermeiden",
            value=False,
            help="Nur Riester/Rürup/Privatrente sind Versicherungsprodukte"
        )

    with col2:
        max_complexity = st.select_slider(
            "Maximale Komplexität",
            options=["Sehr einfach", "Einfach", "Mittel", "Komplex"],
            value="Mittel",
            help="Wie komplex darf Ihre Vorsorge-Strategie sein?"
        )

        rebalancing_frequency = st.selectbox(
            "Umschichtungsbereitschaft",
            options=["Keine Umschichtung", "Jährlich", "Alle 5 Jahre", "Alle 10 Jahre"],
            index=0,
            help="Sind Sie bereit, Ihr Portfolio gelegentlich umzuschichten?"
        )

    st.markdown("---")

    # Optimierung starten
    if st.button("🚀 Optimierung starten", type="primary", use_container_width=True):
        # Speichere Optimierungsparameter
        st.session_state.optimization_params = {
            "goals": {
                "return": goal_return,
                "flexibility": goal_flexibility,
                "simplicity": goal_simplicity,
                "security": goal_security,
                "tax_benefits": goal_tax_benefits,
                "legacy": goal_legacy,
            },
            "budget": {
                "min_monthly": min_monthly,
                "max_monthly": max_monthly,
                "existing_savings": existing_savings,
            },
            "preferences": {
                "allow_riester": allow_riester,
                "prefer_etf": prefer_etf,
                "avoid_insurance": avoid_insurance,
                "max_complexity": max_complexity,
                "rebalancing_frequency": rebalancing_frequency,
            }
        }
        st.rerun()


def render_optimization_results(profile: dict, optimization_params: dict):
    """
    Rendert die Optimierungsergebnisse.

    Args:
        profile: User-Profil Dictionary
        optimization_params: Optimierungsparameter Dictionary
    """
    st.title("🤖 Ihre optimale Altersvorsorge-Strategie")

    st.success("✅ Optimierung abgeschlossen!")

    st.markdown("""
    Basierend auf Ihrem Profil und Ihren Präferenzen haben wir die optimale
    Altersvorsorge-Strategie für Sie ermittelt.
    """)

    st.markdown("---")

    # Placeholder für zukünftige KI-Optimierung
    st.info("""
    🚧 **KI-Optimierung in Entwicklung**

    Die vollständige Optimierung mit Marktdaten-Integration wird in einer
    zukünftigen Version verfügbar sein.

    Aktuell zeigen wir Ihnen eine regelbasierte Empfehlung basierend auf Ihren Angaben.
    """)

    # Einfache regelbasierte Empfehlung
    goals = optimization_params["goals"]
    budget = optimization_params["budget"]
    prefs = optimization_params["preferences"]

    st.subheader("💰 Empfohlene Sparraten-Verteilung")

    total_budget = budget["max_monthly"]

    # Einfache regelbasierte Logik
    if prefs["prefer_etf"] and not prefs["avoid_insurance"]:
        etf_ratio = 0.5
        riester_ratio = 0.2 if prefs["allow_riester"] else 0
        ruerup_ratio = 0.2 if profile["tax_rate"] > 0.35 else 0.1
        privat_ratio = 0.1
    elif prefs["avoid_insurance"]:
        etf_ratio = 1.0
        riester_ratio = 0
        ruerup_ratio = 0
        privat_ratio = 0
    else:
        etf_ratio = 0.4
        riester_ratio = 0.3 if prefs["allow_riester"] else 0
        ruerup_ratio = 0.2
        privat_ratio = 0.1

    # Normalisieren
    total_ratio = etf_ratio + riester_ratio + ruerup_ratio + privat_ratio
    etf_ratio /= total_ratio
    riester_ratio /= total_ratio
    ruerup_ratio /= total_ratio
    privat_ratio /= total_ratio

    # Berechne Beträge
    etf_amount = total_budget * etf_ratio
    riester_amount = total_budget * riester_ratio
    ruerup_amount = total_budget * ruerup_ratio
    privat_amount = total_budget * privat_ratio

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📈 ETF-Sparplan", f"{etf_amount:.0f} €/Monat", f"{etf_ratio * 100:.0f}%")

    with col2:
        st.metric("🎁 Riester-Rente", f"{riester_amount:.0f} €/Monat", f"{riester_ratio * 100:.0f}%")

    with col3:
        st.metric("🏛️ Basisrente", f"{ruerup_amount:.0f} €/Monat", f"{ruerup_ratio * 100:.0f}%")

    with col4:
        st.metric("🏦 Privatrente", f"{privat_amount:.0f} €/Monat", f"{privat_ratio * 100:.0f}%")

    st.markdown("---")

    st.subheader("📊 Erwartete Ergebnisse")

    years = profile["years_until_retirement"]

    # Vereinfachte Rendite-Annahmen
    etf_return = 0.07 - 0.003  # 7% - 0.3% Kosten
    riester_return = 0.03 - 0.02  # 3% - 2% Kosten
    ruerup_return = 0.05 - 0.015  # 5% - 1.5% Kosten
    privat_return = 0.05 - 0.018  # 5% - 1.8% Kosten

    # Einfache Endwert-Berechnung (ohne Zinseszins-Details)
    def calculate_future_value(monthly, rate, years):
        months = years * 12
        return monthly * (((1 + rate/12) ** months - 1) / (rate/12))

    etf_value = calculate_future_value(etf_amount, etf_return, years) if etf_amount > 0 else 0
    riester_value = calculate_future_value(riester_amount, riester_return, years) if riester_amount > 0 else 0
    ruerup_value = calculate_future_value(ruerup_amount, ruerup_return, years) if ruerup_amount > 0 else 0
    privat_value = calculate_future_value(privat_amount, privat_return, years) if privat_amount > 0 else 0

    total_value = etf_value + riester_value + ruerup_value + privat_value
    total_invested = total_budget * 12 * years

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Gesamtwert (vor Steuern)", f"{total_value:,.0f} €")

    with col2:
        st.metric("Eingezahlt", f"{total_invested:,.0f} €")

    with col3:
        gain = total_value - total_invested
        st.metric("Gewinn", f"{gain:,.0f} €", f"+{gain/total_invested*100:.1f}%")

    st.markdown("---")

    st.subheader("🎯 Warum diese Empfehlung?")

    reasons = []

    if etf_ratio > 0.4:
        reasons.append("- **Hoher ETF-Anteil**: Sie präferieren Flexibilität und niedrige Kosten")

    if riester_ratio > 0.2:
        reasons.append("- **Riester-Rente**: Optimale Förderung durch staatliche Zulagen")

    if ruerup_ratio > 0.15:
        reasons.append(f"- **Basisrente**: Starke Steuervorteile bei Ihrem Steuersatz ({profile['tax_rate']*100:.0f}%)")

    if goals["security"] > 7:
        reasons.append("- **Sicherheit**: Streuung über verschiedene Produkte reduziert Risiko")

    if goals["flexibility"] > 7 and etf_ratio > 0.3:
        reasons.append("- **Flexibilität**: Hoher ETF-Anteil ermöglicht jederzeit Zugriff")

    for reason in reasons:
        st.markdown(reason)

    st.markdown("---")

    st.subheader("📋 Nächste Schritte")

    st.markdown("""
    **1. ETF-Sparplan einrichten**
    - Empfohlene Broker: Trade Republic, Scalable Capital, ING
    - ETF-Empfehlung: MSCI World oder FTSE All-World
    - Ordergebühren: 0€ - 1€ pro Ausführung

    **2. Riester-Vertrag abschließen** (falls gewählt)
    - Empfohlene Anbieter: Fairr, DWS, Union Investment
    - Auf niedrige Kosten achten (< 1,5% p.a.)

    **3. Basisrente einrichten** (falls gewählt)
    - Bei hohem Einkommen: Nettotarife bevorzugen
    - Honorarberater konsultieren

    **4. Privatrente** (optional)
    - Nur bei Restbudget sinnvoll
    - Auf flexible Auszahlungsoptionen achten
    """)

    st.markdown("---")

    # Link zum Learning Mode
    st.info("""
    💡 **Tipp**: Nutzen Sie den **Learning Mode** für detaillierte Berechnungen
    mit Ihren konkreten Zahlen und allen Kostenstrukturen!
    """)

    if st.button("📚 Zum Learning Mode", use_container_width=True):
        st.session_state.selected_mode = "learning"
        st.rerun()

    # Reset-Button
    st.markdown("---")
    if st.button("🔄 Neue Optimierung starten", use_container_width=True):
        st.session_state.optimization_params = None
        st.rerun()
