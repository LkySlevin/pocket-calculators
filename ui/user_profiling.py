"""
User Profiling - Erfassung der Nutzerdaten für personalisierte Berechnungen
"""
import streamlit as st
from utils.tax_calculator import calculate_tax_rate
from ui.risk_profiling import (
    render_risk_profiling,
    render_kpi_definition,
    calculate_risk_class,
    RiskProfile,
    RISK_CLASSES,
    show_risk_profile_complete
)


def render_user_profile_form():
    """
    Rendert das User-Profile Formular zur Erfassung der persönlichen Daten.

    Jetzt erweitert mit:
    - IDD-Risikoprofil (Risikoklassen 1-5 nach GDV/DIN 77223)
    - Nutzer-KPIs (Renditeziel, Kostentoleranz, Prioritäten)
    - Multi-Step Wizard mit Fortschrittsanzeige

    Returns:
        dict: User-Profil mit allen relevanten Daten oder None wenn nicht komplett
    """
    st.title("👤 Ihr persönliches Profil")

    st.markdown("""
    Um Ihnen die besten Empfehlungen geben zu können, benötigen wir einige Informationen
    über Ihre persönliche Situation. Dieser Prozess ist **verpflichtend** gemäß IDD-Richtlinie.

    **Alle Daten werden nur lokal verarbeitet und nicht gespeichert.**
    """)

    # Multi-Step Wizard: Fortschritt anzeigen
    if 'profiling_step' not in st.session_state:
        st.session_state.profiling_step = 1

    # Fortschrittsbalken
    total_steps = 3
    progress = st.session_state.profiling_step / total_steps
    st.progress(progress)
    st.caption(f"Schritt {st.session_state.profiling_step} von {total_steps}")

    st.markdown("---")

    # Persönliche Daten
    st.subheader("📋 Persönliche Angaben")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "Ihr aktuelles Alter",
            min_value=18,
            max_value=67,
            value=35,
            step=1,
            help="Ihr aktuelles Lebensalter"
        )

        gross_salary = st.number_input(
            "Ihr Brutto-Jahresgehalt (€)",
            min_value=0,
            max_value=500000,
            value=50000,
            step=1000,
            help="Ihr jährliches Bruttogehalt vor Steuern"
        )

        children = st.number_input(
            "Anzahl Kinder",
            min_value=0,
            max_value=10,
            value=0,
            step=1,
            help="Anzahl kindergeldberechtigter Kinder"
        )

    with col2:
        retirement_age = st.number_input(
            "Gewünschtes Renteneintrittsalter",
            min_value=60,
            max_value=70,
            value=67,
            step=1,
            help="In welchem Alter möchten Sie in Rente gehen?"
        )

        church_tax = st.checkbox(
            "Kirchensteuerpflichtig",
            value=False,
            help="Zahlen Sie Kirchensteuer? (8-9% je nach Bundesland)"
        )

        married = st.checkbox(
            "Verheiratet / Gemeinsam veranlagt",
            value=False,
            help="Sind Sie verheiratet oder in einer eingetragenen Lebenspartnerschaft?"
        )

    # Partner-Daten (nur wenn verheiratet)
    partner_salary = 0
    if married:
        st.markdown("---")
        st.subheader("💑 Partner-Angaben")

        partner_salary = st.number_input(
            "Brutto-Jahresgehalt Partner (€)",
            min_value=0,
            max_value=500000,
            value=40000,
            step=1000,
            help="Jahresgehalt Ihres Partners/Ihrer Partnerin"
        )

    # Berechnete Werte
    st.markdown("---")
    st.subheader("📊 Berechnete Werte")

    # Steuersatz berechnen
    if married:
        # Ehegattensplitting: Steuersatz für halbes Einkommen berechnen
        # (die Verdopplung der STEUERLAST erfolgt automatisch durch das gemeinsame Einkommen)
        combined_income = gross_salary + partner_salary
        tax_rate = calculate_tax_rate(combined_income / 2)
    else:
        tax_rate = calculate_tax_rate(gross_salary)

    # Kirchensteuer berücksichtigen (9% auf die ESt, vereinfacht)
    if church_tax:
        effective_tax_rate = tax_rate * 1.09
    else:
        effective_tax_rate = tax_rate

    # Anlagedauer
    years_until_retirement = max(1, retirement_age - age)

    # Anzeige
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Steuersatz", f"{effective_tax_rate * 100:.1f}%")
    with col2:
        st.metric("Anlagedauer", f"{years_until_retirement} Jahre")
    with col3:
        if married:
            st.metric("Haushaltseinkommen", f"{(gross_salary + partner_salary):,.0f} €")
        else:
            st.metric("Jahreseinkommen", f"{gross_salary:,.0f} €")
    with col4:
        st.metric("Kinder", f"{children}")

    st.markdown("---")

    # Multi-Step Navigation
    if st.session_state.profiling_step == 1:
        # Schritt 1: Persönliche Daten
        col1, col2 = st.columns([3, 1])

        with col1:
            st.info("💡 Diese Daten werden für personalisierte Empfehlungen und Voreinstellungen verwendet.")

        with col2:
            if st.button("Weiter ➡️", type="primary", use_container_width=True):
                # Temporär speichern
                st.session_state.profiling_data = {
                    "age": age,
                    "gross_salary": gross_salary,
                    "children": children,
                    "retirement_age": retirement_age,
                    "church_tax": church_tax,
                    "married": married,
                    "partner_salary": partner_salary,
                    "tax_rate": effective_tax_rate,
                    "years_until_retirement": years_until_retirement,
                }
                st.session_state.profiling_step = 2
                st.rerun()

    elif st.session_state.profiling_step == 2:
        # Schritt 2: IDD-Risikoprofil
        st.markdown("---")

        knowledge_level, experience_level, loss_tolerance, investment_horizon = render_risk_profiling()

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("⬅️ Zurück", use_container_width=True):
                st.session_state.profiling_step = 1
                st.rerun()

        with col3:
            if st.button("Weiter ➡️", type="primary", use_container_width=True):
                # Risikoprofil berechnen
                profile_data = st.session_state.profiling_data
                risk_class, explanation = calculate_risk_class(
                    knowledge_level=knowledge_level,
                    experience_level=experience_level,
                    loss_tolerance=loss_tolerance,
                    investment_horizon=investment_horizon,
                    age=profile_data['age']
                )

                # Risikoprofil erstellen und speichern
                risk_profile = RiskProfile(
                    risk_class=risk_class,
                    risk_label=RISK_CLASSES[risk_class]['label'],
                    description=RISK_CLASSES[risk_class]['description'],
                    knowledge_level=knowledge_level,
                    experience_level=experience_level,
                    loss_tolerance=loss_tolerance,
                    investment_horizon=investment_horizon
                )

                st.session_state.profiling_data['risk_profile'] = risk_profile.to_dict()
                st.session_state.profiling_data['risk_explanation'] = explanation
                st.session_state.profiling_step = 3
                st.rerun()

    elif st.session_state.profiling_step == 3:
        # Schritt 3: KPI-Definition
        st.markdown("---")

        kpis = render_kpi_definition()

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("⬅️ Zurück", use_container_width=True):
                st.session_state.profiling_step = 2
                st.rerun()

        with col3:
            if st.button("✅ Profil abschließen", type="primary", use_container_width=True):
                # KPIs hinzufügen
                st.session_state.profiling_data['kpis'] = kpis

                # Profil vollständig
                profile = st.session_state.profiling_data

                # Zusammenfassung anzeigen
                st.success("✅ Profil erfolgreich erstellt!")

                # Risikoprofil anzeigen
                risk_profile = RiskProfile(**profile['risk_profile'])
                show_risk_profile_complete(risk_profile, kpis)

                return profile

    return None


def calculate_pension_gap(profile: dict) -> dict:
    """
    Berechnet die Rentenlücke basierend auf dem Nutzerprofil.

    Args:
        profile: User-Profil Dictionary

    Returns:
        dict: Rentenlücken-Analyse mit Empfehlungen
    """
    gross_salary = profile["gross_salary"]
    partner_salary = profile.get("partner_salary", 0)
    married = profile.get("married", False)
    years_until_retirement = profile["years_until_retirement"]

    # Vereinfachte Berechnung der gesetzlichen Rente
    # Annahme: ~48% des Durchschnittseinkommens bei 45 Beitragsjahren
    # (stark vereinfacht, in Realität deutlich komplexer)

    if married:
        total_salary = gross_salary + partner_salary
        # Beide Partner arbeiten, beide bekommen Rente
        expected_state_pension_user = gross_salary * 0.48 * (years_until_retirement / 45)
        expected_state_pension_partner = partner_salary * 0.48 * (years_until_retirement / 45)
        expected_state_pension = expected_state_pension_user + expected_state_pension_partner
    else:
        total_salary = gross_salary
        expected_state_pension = gross_salary * 0.48 * (years_until_retirement / 45)

    # Monatliche Werte
    expected_state_pension_monthly = expected_state_pension / 12

    # Angestrebte Rente (70% des letzten Nettogehalts als Faustregel)
    # Vereinfachte Netto-Berechnung (60% vom Brutto)
    net_salary = total_salary * 0.6
    target_pension = net_salary * 0.7

    # Monatliche Werte
    target_pension_monthly = target_pension / 12

    # Rentenlücke
    pension_gap = target_pension - expected_state_pension
    pension_gap_monthly = pension_gap / 12

    # Benötigtes Kapital (4% Entnahmeregel)
    required_capital = pension_gap * 25  # 1/0.04 = 25

    # Wie viel muss monatlich gespart werden?
    # Annahme: 5% Rendite nach Kosten
    net_return = 0.05
    n_months = years_until_retirement * 12

    # Sparrate-Berechnung (aufgezinst)
    if n_months > 0 and net_return > 0:
        monthly_rate = (net_return / 12)
        required_monthly_savings = required_capital * monthly_rate / (((1 + monthly_rate) ** n_months) - 1)
    else:
        required_monthly_savings = 0

    return {
        "gross_salary": total_salary,
        "net_salary": net_salary,
        "target_pension": target_pension,
        "target_pension_monthly": target_pension_monthly,
        "expected_state_pension": expected_state_pension,
        "expected_state_pension_monthly": expected_state_pension_monthly,
        "pension_gap": pension_gap,
        "pension_gap_monthly": pension_gap_monthly,
        "required_capital": required_capital,
        "required_monthly_savings": required_monthly_savings,
    }


def display_pension_gap_analysis(profile: dict):
    """
    Zeigt die Rentenlücken-Analyse an.

    Args:
        profile: User-Profil Dictionary
    """
    st.subheader("📉 Ihre Rentenlücke")

    gap_data = calculate_pension_gap(profile)

    st.markdown("""
    **Die Rentenlücke** ist die Differenz zwischen Ihrer erwarteten gesetzlichen Rente
    und dem Betrag, den Sie benötigen, um Ihren Lebensstandard im Alter zu halten.
    """)

    # Visualisierung
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Zielrente (70% vom Netto)",
            f"{gap_data['target_pension_monthly']:,.0f} €/Monat",
            help="Empfohlene Rente um Lebensstandard zu halten"
        )

    with col2:
        st.metric(
            "Erwartete gesetzliche Rente",
            f"{gap_data['expected_state_pension_monthly']:,.0f} €/Monat",
            help="Geschätzte gesetzliche Rente (stark vereinfacht)"
        )

    with col3:
        delta_value = f"-{gap_data['pension_gap_monthly']:,.0f} €"
        st.metric(
            "Ihre Rentenlücke",
            f"{gap_data['pension_gap_monthly']:,.0f} €/Monat",
            delta=delta_value,
            delta_color="inverse",
            help="Diese Lücke sollten Sie durch private Vorsorge schließen"
        )

    st.markdown("---")

    # Empfehlungen
    st.subheader("💡 Spar-Empfehlungen")

    st.info(f"""
    **Um Ihre Rentenlücke zu schließen, benötigen Sie:**

    - **Gesamtkapital bei Rentenbeginn**: {gap_data['required_capital']:,.0f} €
    - **Monatliche Sparrate** (bei 5% Rendite): {gap_data['required_monthly_savings']:,.0f} €/Monat
    - **Anlagedauer**: {profile['years_until_retirement']} Jahre
    """)

    # Empfehlungen pro Produkt
    st.markdown("### 🎯 Optimale Aufteilung nach Produkten")

    children = profile.get("children", 0)
    gross_salary = profile["gross_salary"]

    # Riester-Optimum berechnen
    riester_optimal = calculate_riester_optimal(gross_salary, children)

    # ETF/Privatrente/Basisrente: Rest aufteilen
    remaining_savings = max(0, gap_data['required_monthly_savings'] - riester_optimal)

    st.markdown(f"""
    **Empfohlene monatliche Sparraten:**

    1. **🎁 Riester-Rente**: {riester_optimal:,.0f} €/Monat
       - Optimale Förderung durch Zulagen
       - {children} Kinder = {children * 300:,.0f} €/Jahr Zulagen
       - Grundzulage: 175 €/Jahr

    2. **📈 ETF-Sparplan**: {remaining_savings * 0.5:,.0f} €/Monat
       - Flexibel und kostengünstig
       - Hohe erwartete Rendite

    3. **🏛️ Basisrente (Rürup)**: {remaining_savings * 0.3:,.0f} €/Monat
       - Steuerliche Vorteile bei hohem Einkommen
       - Bei Ihrem Steuersatz: {profile['tax_rate'] * 100:.0f}%

    4. **🏦 Privatrente**: {remaining_savings * 0.2:,.0f} €/Monat
       - Günstige Besteuerung im Alter
       - Flexibilität bei Auszahlung

    **Gesamt**: {gap_data['required_monthly_savings']:,.0f} €/Monat
    """)

    st.warning("""
    ⚠️ **Hinweis**: Dies sind vereinfachte Berechnungen zur Orientierung.
    Die tatsächlichen Werte hängen von vielen individuellen Faktoren ab.

    Verwenden Sie den **Learning Mode** für detaillierte Berechnungen mit
    allen Parametern und Kostenstrukturen!
    """)


def calculate_riester_optimal(gross_salary: float, children: int) -> float:
    """
    Berechnet die optimale monatliche Riester-Sparrate.

    Bei höheren Gehältern liegt das Optimum bei ca. 160 €/Monat
    (4% vom Vorjahreseinkommen, max. 2.100 € - Zulagen = ~160€)

    Args:
        gross_salary: Brutto-Jahresgehalt
        children: Anzahl Kinder

    Returns:
        float: Optimale monatliche Riester-Sparrate
    """
    # Maximaler Sonderausgabenabzug: 2.100 €/Jahr
    max_deductible = 2100

    # Zulagen
    basic_allowance = 175
    children_allowance = children * 300
    total_allowances = basic_allowance + children_allowance

    # 4% vom Vorjahreseinkommen abzgl. Zulagen
    four_percent = gross_salary * 0.04

    # Mindesteigenbeitrag: 4% vom Vorjahreseinkommen abzgl. Zulagen
    min_contribution = max(60, four_percent - total_allowances)  # Mindestens 60€/Jahr

    # Optimaler Beitrag: Maximum aus Mindesteigenbeitrag und (max_deductible - Zulagen)
    optimal_yearly = min(
        max_deductible - total_allowances,
        four_percent - total_allowances
    )

    # Bei höheren Gehältern: ca. 160€/Monat
    if gross_salary > 50000:
        optimal_yearly = max_deductible - total_allowances

    # Monatlicher Wert
    optimal_monthly = optimal_yearly / 12

    return max(0, optimal_monthly)
