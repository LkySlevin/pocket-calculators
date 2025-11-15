"""
IDD Risk Profiling Module (nach GDV/DIN 77223)

Implementiert die Risikoklassifizierung nach Insurance Distribution Directive (IDD).
"""

import streamlit as st
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class RiskProfile:
    """Risikoprofil nach IDD/GDV-Richtlinien"""
    risk_class: int  # 1-5
    risk_label: str
    description: str
    knowledge_level: int  # 1-4
    experience_level: int  # 1-4
    loss_tolerance: int  # 1-5
    investment_horizon: int  # Jahre

    def to_dict(self) -> Dict:
        """Konvertiert Profil in Dictionary für Session State"""
        return {
            'risk_class': self.risk_class,
            'risk_label': self.risk_label,
            'description': self.description,
            'knowledge_level': self.knowledge_level,
            'experience_level': self.experience_level,
            'loss_tolerance': self.loss_tolerance,
            'investment_horizon': self.investment_horizon
        }


# Risikoklassen nach GDV/DIN 77223
RISK_CLASSES = {
    1: {
        'label': 'Sehr sicherheitsorientiert',
        'description': 'Kapitalerhalt steht im Vordergrund. Wertschwankungen werden nicht toleriert.',
        'max_loss': '0-5%',
        'typical_products': ['Garantieprodukte', 'Festgeld', 'Basisrente (klassisch)']
    },
    2: {
        'label': 'Sicherheitsorientiert',
        'description': 'Überwiegend sichere Anlagen mit geringen Wertschwankungen.',
        'max_loss': '5-10%',
        'typical_products': ['Mischfonds (konservativ)', 'Basisrente (Hybrid)', 'Riester (klassisch)']
    },
    3: {
        'label': 'Ausgewogen-chancenorientiert',
        'description': 'Ausgewogenes Verhältnis zwischen Sicherheit und Renditechance.',
        'max_loss': '10-20%',
        'typical_products': ['Mischfonds (ausgewogen)', 'ETF-Portfolio (60/40)', 'Fondsgebundene Rente']
    },
    4: {
        'label': 'Renditeorientiert',
        'description': 'Höhere Renditechancen bei akzeptierten Wertschwankungen.',
        'max_loss': '20-30%',
        'typical_products': ['Aktienfonds', 'ETF-Portfolio (80/20)', 'Fondsgebundene Rente (100% Aktien)']
    },
    5: {
        'label': 'Spekulativ',
        'description': 'Maximale Renditechance bei hohen Risiken und starken Schwankungen.',
        'max_loss': '>30%',
        'typical_products': ['Einzelaktien', 'Emerging Markets ETFs', 'Kryptowährungen']
    }
}


def calculate_risk_class(
    knowledge_level: int,
    experience_level: int,
    loss_tolerance: int,
    investment_horizon: int,
    age: int
) -> Tuple[int, str]:
    """
    Berechnet die Risikoklasse basierend auf den Antworten.

    Args:
        knowledge_level: Wissensstufe 1-4
        experience_level: Erfahrungsstufe 1-4
        loss_tolerance: Verlusttoleranz 1-5
        investment_horizon: Anlagehorizont in Jahren
        age: Alter des Nutzers

    Returns:
        Tuple (risk_class, explanation)
    """

    # Basis-Score aus Wissen und Erfahrung
    knowledge_score = (knowledge_level + experience_level) / 2

    # Verlusttoleranz ist der wichtigste Faktor
    loss_score = loss_tolerance

    # Zeithorizont beeinflusst Risikofähigkeit
    if investment_horizon < 5:
        horizon_modifier = -1
    elif investment_horizon < 10:
        horizon_modifier = 0
    elif investment_horizon < 20:
        horizon_modifier = 0.5
    else:
        horizon_modifier = 1

    # Alter beeinflusst Risikofähigkeit (jünger = mehr Zeit)
    if age < 30:
        age_modifier = 0.5
    elif age < 40:
        age_modifier = 0.25
    elif age < 50:
        age_modifier = 0
    elif age < 60:
        age_modifier = -0.25
    else:
        age_modifier = -0.5

    # Gesamtscore (Verlusttoleranz 60%, Wissen 30%, Horizont 10%)
    total_score = (
        loss_score * 0.6 +
        knowledge_score * 0.3 +
        min(5, max(1, loss_score + horizon_modifier + age_modifier)) * 0.1
    )

    # Risikoklasse ermitteln
    if total_score <= 1.5:
        risk_class = 1
    elif total_score <= 2.5:
        risk_class = 2
    elif total_score <= 3.5:
        risk_class = 3
    elif total_score <= 4.5:
        risk_class = 4
    else:
        risk_class = 5

    # Erklärung generieren
    explanation = f"""
    **Ihre Risikoklasse: {risk_class} - {RISK_CLASSES[risk_class]['label']}**

    {RISK_CLASSES[risk_class]['description']}

    **Berechnungsgrundlage:**
    - Wissen & Erfahrung: {knowledge_score:.1f}/4
    - Verlusttoleranz: {loss_tolerance}/5
    - Anlagehorizont: {investment_horizon} Jahre
    - Ihr Alter: {age} Jahre

    **Maximaler akzeptierter Verlust:** {RISK_CLASSES[risk_class]['max_loss']}

    **Geeignete Produkte:**
    {', '.join(RISK_CLASSES[risk_class]['typical_products'])}
    """

    return risk_class, explanation


def render_risk_profiling() -> RiskProfile:
    """
    Rendert den IDD-Risikoprofil-Fragebogen.

    Returns:
        RiskProfile mit berechneter Risikoklasse
    """

    st.markdown("### 📊 IDD-Risikoprofil (nach GDV/DIN 77223)")
    st.markdown("""
    Um Ihnen geeignete Anlageempfehlungen zu geben, müssen wir Ihre Risikobereitschaft
    und Erfahrung ermitteln. Dies ist gesetzlich vorgeschrieben (IDD-Richtlinie).
    """)

    # Wissensstufe
    st.markdown("#### 1. Kenntnisse über Finanzanlagen")
    knowledge_level = st.radio(
        "Wie schätzen Sie Ihre Kenntnisse über Finanzanlagen ein?",
        options=[1, 2, 3, 4],
        format_func=lambda x: {
            1: "Keine Kenntnisse - Ich habe mich noch nie mit Finanzanlagen beschäftigt",
            2: "Grundkenntnisse - Ich kenne die Grundbegriffe (Aktie, Fonds, ETF)",
            3: "Fortgeschrittene Kenntnisse - Ich verstehe Rendite, Risiko, Diversifikation",
            4: "Expertenkenntnisse - Ich habe fundiertes Wissen über Kapitalmärkte"
        }[x],
        key="knowledge_level"
    )

    # Erfahrungsstufe
    st.markdown("#### 2. Erfahrung mit Finanzanlagen")
    experience_level = st.radio(
        "Welche Erfahrung haben Sie mit Finanzanlagen?",
        options=[1, 2, 3, 4],
        format_func=lambda x: {
            1: "Keine Erfahrung - Ich habe noch nie in Wertpapiere investiert",
            2: "Geringe Erfahrung - Ich habe vereinzelt in Fonds oder ETFs investiert",
            3: "Mittlere Erfahrung - Ich habe regelmäßig in verschiedene Anlageklassen investiert",
            4: "Umfangreiche Erfahrung - Ich manage aktiv ein diversifiziertes Portfolio"
        }[x],
        key="experience_level"
    )

    # Verlusttoleranz (wichtigster Faktor!)
    st.markdown("#### 3. Verlusttoleranz")
    st.markdown("""
    Angenommen, Sie investieren 10.000 € für Ihre Altersvorsorge.
    Wie viel Wertverlust würden Sie in einem schlechten Jahr akzeptieren?
    """)

    loss_tolerance = st.radio(
        "Maximaler akzeptierter Verlust:",
        options=[1, 2, 3, 4, 5],
        format_func=lambda x: {
            1: "0-500 € (0-5%) - Ich möchte keine Verluste",
            2: "500-1.000 € (5-10%) - Geringe Verluste sind okay",
            3: "1.000-2.000 € (10-20%) - Moderate Verluste für höhere Chancen",
            4: "2.000-3.000 € (20-30%) - Höhere Verluste für deutlich bessere Renditechancen",
            5: "über 3.000 € (>30%) - Ich akzeptiere hohe Risiken für maximale Rendite"
        }[x],
        key="loss_tolerance"
    )

    # Anlagehorizont
    st.markdown("#### 4. Anlagehorizont")
    investment_horizon = st.slider(
        "Wie viele Jahre bis zum Renteneintritt?",
        min_value=5,
        max_value=50,
        value=st.session_state.get('profiling_data', {}).get('years_to_retirement', 30),
        step=1,
        key="risk_investment_horizon"
    )

    # Zusätzliche Informationen
    with st.expander("ℹ️ Warum diese Fragen?"):
        st.markdown("""
        **Gesetzliche Grundlage:**
        - Die Insurance Distribution Directive (IDD) verpflichtet Versicherungsvermittler,
          die Geeignetheit von Produkten zu prüfen.
        - Die GDV-Risikoklassen (1-5) sind der deutsche Standard für Risikobewertung.

        **Ihre Vorteile:**
        - Sie erhalten nur Produkte, die zu Ihrem Profil passen
        - Schutz vor ungeeigneten Hochrisikoprodukten
        - Transparente Dokumentation Ihrer Risikobereitschaft

        **Hinweis:**
        Sie können jederzeit höhere Sicherheit wählen (niedrigere Risikoklasse),
        aber nicht beliebig höhere Risiken ohne entsprechende Kenntnisse/Erfahrung.
        """)

    return knowledge_level, experience_level, loss_tolerance, investment_horizon


def render_kpi_definition() -> Dict[str, float]:
    """
    Rendert die KPI-Definition für den Nutzer.

    3 vereinfachte KPIs:
    1. Rendite vs. Sicherheit (Slider)
    2. Liquidität (Slider)
    3. Flexibilität (Slider)

    Returns:
        Dictionary mit Nutzer-KPIs
    """

    st.markdown("### 🎯 Ihre persönlichen Ziele (KPIs)")
    st.markdown("""
    Definieren Sie Ihre 3 wichtigsten Prioritäten für die Altersvorsorge.
    """)

    # KPI 1: Rendite vs. Sicherheit
    st.markdown("#### 1️⃣ Rendite vs. Sicherheit")
    return_vs_security = st.slider(
        "Was ist Ihnen wichtiger?",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        format="%.1f",
        help="""
        **0.0 = Maximale Sicherheit** (Garantien, keine Verluste)
        **0.5 = Ausgewogen** (Balance zwischen Sicherheit und Rendite)
        **1.0 = Maximale Rendite** (Höhere Risiken akzeptabel)
        """,
        key="return_vs_security"
    )

    # Zeige Label basierend auf Wert
    if return_vs_security < 0.3:
        security_label = "🛡️ Sicherheitsorientiert"
        security_description = "Sie bevorzugen sichere Anlagen wie Garantieprodukte, Basisrente (klassisch)"
    elif return_vs_security < 0.7:
        security_label = "⚖️ Ausgewogen"
        security_description = "Sie suchen eine Balance, z.B. Mischfonds, Basisrente (Hybrid), Riester"
    else:
        security_label = "📈 Renditeorientiert"
        security_description = "Sie akzeptieren Risiken für höhere Renditen, z.B. ETF-Portfolio, Aktien"

    st.caption(f"{security_label}: {security_description}")

    st.markdown("---")

    # KPI 2: Liquidität
    st.markdown("#### 2️⃣ Liquidität")
    liquidity = st.slider(
        "Wie wichtig ist Ihnen der Zugriff auf Ihr Kapital?",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        format="%.1f",
        help="""
        **0.0 = Unwichtig** (Kapital kann langfristig gebunden sein)
        **0.5 = Mittel** (Gelegentlicher Zugriff gewünscht)
        **1.0 = Sehr wichtig** (Jederzeit verfügbar)
        """,
        key="liquidity"
    )

    # Zeige Label basierend auf Wert
    if liquidity < 0.3:
        liquidity_label = "🔒 Niedrig"
        liquidity_description = "Langfristige Bindung ist okay (z.B. Basisrente, Riester)"
    elif liquidity < 0.7:
        liquidity_label = "🔓 Mittel"
        liquidity_description = "Teilweiser Zugriff gewünscht (z.B. Privatrente mit Kapitalwahlrecht)"
    else:
        liquidity_label = "💰 Hoch"
        liquidity_description = "Jederzeit verfügbar (z.B. ETF-Depot, Tagesgeld)"

    st.caption(f"{liquidity_label}: {liquidity_description}")

    st.markdown("---")

    # KPI 3: Flexibilität
    st.markdown("#### 3️⃣ Flexibilität")
    flexibility = st.slider(
        "Wie flexibel soll Ihre Vorsorge sein?",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        format="%.1f",
        help="""
        **0.0 = Unwichtig** (Feste Verträge sind okay)
        **0.5 = Mittel** (Gewisse Anpassungsmöglichkeiten gewünscht)
        **1.0 = Sehr wichtig** (Maximale Flexibilität bei Beiträgen und Auszahlungen)
        """,
        key="flexibility"
    )

    # Zeige Label basierend auf Wert
    if flexibility < 0.3:
        flexibility_label = "📋 Niedrig"
        flexibility_description = "Feste Verträge sind okay (z.B. Riester, Basisrente)"
    elif flexibility < 0.7:
        flexibility_label = "🔄 Mittel"
        flexibility_description = "Gewisse Anpassungen gewünscht (z.B. Privatrente mit Dynamik)"
    else:
        flexibility_label = "🎯 Hoch"
        flexibility_description = "Maximale Flexibilität (z.B. ETF-Sparplan, frei anpassbar)"

    st.caption(f"{flexibility_label}: {flexibility_description}")

    # KPIs sammeln
    kpis = {
        'return_vs_security': return_vs_security,
        'liquidity': liquidity,
        'flexibility': flexibility
    }

    # Zusammenfassung anzeigen
    st.markdown("---")
    with st.expander("📋 Ihre KPI-Zusammenfassung"):
        st.markdown(f"""
        **1. Rendite vs. Sicherheit:** {return_vs_security:.1f} ({security_label})
        - {security_description}

        **2. Liquidität:** {liquidity:.1f} ({liquidity_label})
        - {liquidity_description}

        **3. Flexibilität:** {flexibility:.1f} ({flexibility_label})
        - {flexibility_description}

        ---

        **Empfehlung basierend auf Ihren KPIs:**
        """)

        # Intelligente Empfehlung basierend auf allen 3 KPIs
        if return_vs_security < 0.4 and liquidity < 0.5:
            st.success("✅ Ihre KPIs passen gut zu: **Basisrente (klassisch), Riester**")
        elif return_vs_security > 0.6 and liquidity > 0.5 and flexibility > 0.5:
            st.success("✅ Ihre KPIs passen gut zu: **ETF-Sparplan**")
        elif return_vs_security > 0.6 and liquidity < 0.5:
            st.success("✅ Ihre KPIs passen gut zu: **Basisrente (fondsgebunden), ETF**")
        elif flexibility > 0.6:
            st.success("✅ Ihre KPIs passen gut zu: **ETF-Sparplan, Privatrente mit Kapitalwahlrecht**")
        else:
            st.success("✅ Ihre KPIs passen gut zu: **Mischung aus ETF, Basisrente und Privatrente**")

    return kpis


def show_risk_profile_complete(risk_profile: RiskProfile, kpis: Dict) -> None:
    """
    Zeigt das vollständige Risikoprofil und KPIs an.

    Args:
        risk_profile: Berechnetes Risikoprofil
        kpis: Nutzer-KPIs (mit neuen 3 KPIs)
    """

    st.success("✅ Risikoprofil und Ziele erfolgreich definiert!")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Ihr Risikoprofil")
        st.metric(
            label="Risikoklasse",
            value=f"{risk_profile.risk_class} - {risk_profile.risk_label}"
        )
        st.markdown(f"**Max. Verlust:** {RISK_CLASSES[risk_profile.risk_class]['max_loss']}")

    with col2:
        st.markdown("### 🎯 Ihre KPIs")

        # Zeige die 3 vereinfachten KPIs
        return_vs_security = kpis.get('return_vs_security', 0.5)
        liquidity = kpis.get('liquidity', 0.3)
        flexibility = kpis.get('flexibility', 0.5)

        st.metric(label="Rendite vs. Sicherheit", value=f"{return_vs_security:.1f}")
        st.metric(label="Liquidität", value=f"{liquidity:.1f}")
        st.metric(label="Flexibilität", value=f"{flexibility:.1f}")
