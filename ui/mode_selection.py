"""
Mode Selection Screen - Startbildschirm mit Modusauswahl
"""
import json

import streamlit as st

MODE_CARDS = [
    {
        "id": "intelligent",
        "icon": "🤖",
        "title": "Intelligent Mode",
        "description": "Automatische Optimierung für die theoretisch perfekte Lösung inkl. Suche nach den besten verfügbaren Angeboten am Markt.",
        "gradient": "linear-gradient(135deg, #2d3561 0%, #1f2544 100%)",
        "hover_gradient": "linear-gradient(135deg, #3d4571 0%, #2f3554 100%)",
        "border": "rgba(102, 126, 234, 0.3)",
        "hover_border": "rgba(102, 126, 234, 1)",
        "shadow": "rgba(102, 126, 234, 0.3)",
        "hover_shadow": "rgba(102, 126, 234, 0.6)",
    },
    {
        "id": "learning",
        "icon": "📚",
        "title": "Learning Mode",
        "description": "Zugriff auf alle Parameter mit manueller Anpassung kombiniert mit leicht verständlichen Erklärungen der verschiedenen Konzepte, Vor- und Nachteile.",
        "gradient": "linear-gradient(135deg, #3d2f5b 0%, #2a1f3d 100%)",
        "hover_gradient": "linear-gradient(135deg, #4d3f6b 0%, #3a2f4d 100%)",
        "border": "rgba(118, 75, 162, 0.3)",
        "hover_border": "rgba(118, 75, 162, 1)",
        "shadow": "rgba(118, 75, 162, 0.3)",
        "hover_shadow": "rgba(118, 75, 162, 0.6)",
    },
    {
        "id": "quick_check",
        "icon": "⚡",
        "title": "Quick Check Mode",
        "description": "Laden Sie einen bestehenden Vertrag hoch und prüfen Sie schnell, ob dieser geeignet ist oder nicht.",
        "gradient": "linear-gradient(135deg, #4a2d5e 0%, #331f42 100%)",
        "hover_gradient": "linear-gradient(135deg, #5a3d6e 0%, #433152 100%)",
        "border": "rgba(240, 147, 251, 0.3)",
        "hover_border": "rgba(240, 147, 251, 1)",
        "shadow": "rgba(240, 147, 251, 0.3)",
        "hover_shadow": "rgba(240, 147, 251, 0.6)",
    }
]


def render_mode_selection():
    """
    Rendert den Mode-Selection Screen mit drei verschiedenen Modi.

    Returns:
        str: Gewählter Modus ('intelligent', 'learning', 'quick_check') oder None
    """

    # CSS für die gesamte Seite plus Hilfsskript
    st.markdown(
        """
        <style>
            .stApp {
                background: #1a1a2e;
            }

            .main-title {
                text-align: center;
                color: #ffffff;
                font-size: 2.8rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
            }

            .main-subtitle {
                text-align: center;
                color: rgba(255,255,255,0.7);
                font-size: 1.1rem;
                margin-bottom: 3rem;
            }

            /* Buttons unsichtbar machen, aber für JS klickbar lassen */
            div[data-testid="column"] button[kind="primary"] {
                position: absolute !important;
                opacity: 0 !important;
                pointer-events: none !important;
                width: 0 !important;
                height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
            }
        </style>
        <script>
            window.selectModeCard = function(label) {
                const buttons = Array.from(window.parent.document.querySelectorAll('button'));
                const target = buttons.find((btn) => btn.innerText.trim() === label.trim());
                if (target) {
                    target.click();
                }
            };
        </script>
        """,
        unsafe_allow_html=True,
    )

    # Haupttitel
    st.markdown('<h1 class="main-title">💰 Altersvorsorge-Rechner</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="main-subtitle">Wählen Sie Ihren Modus durch Klick auf eine Karte</p>',
        unsafe_allow_html=True,
    )

    # Buttons als Columns mit HTML
    cols = st.columns(len(MODE_CARDS), gap="medium")
    selected_mode = None

    for col, card in zip(cols, MODE_CARDS):
        with col:
            # HTML Card mit Inline-Styles und Click-Handler
            safe_title = json.dumps(card["title"])
            card_html = f"""
            <style>
                .mode-card-{card['id']} {{
                    width: 100%;
                    min-height: 550px;
                    background: {card['gradient']};
                    border: 2px solid {card['border']};
                    border-radius: 16px;
                    padding: 3rem 2rem;
                    cursor: pointer;
                    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 8px 24px {card['shadow']};
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    color: white;
                    margin-bottom: 1rem;
                }}

                .mode-card-{card['id']}:hover {{
                    background: {card['hover_gradient']};
                    border-color: {card['hover_border']};
                    box-shadow: 0 20px 48px {card['hover_shadow']};
                    transform: translateY(-12px) scale(1.02);
                }}

                .mode-card-{card['id']} .icon {{
                    font-size: 8rem;
                    margin-bottom: 1.5rem;
                    line-height: 1;
                }}

                .mode-card-{card['id']} .title {{
                    font-size: 2rem;
                    font-weight: bold;
                    margin-bottom: 1rem;
                    line-height: 1.2;
                }}

                .mode-card-{card['id']} .description {{
                    font-size: 1.1rem;
                    line-height: 1.6;
                    opacity: 0.9;
                }}
            </style>
            <div class="mode-card-{card['id']}" onclick="window.selectModeCard({safe_title})">
                <div class="icon">{card['icon']}</div>
                <div class="title">{card['title']}</div>
                <div class="description">{card['description']}</div>
            </div>
            """

            st.markdown(card_html, unsafe_allow_html=True)

            # Unsichtbarer Button pro Karte für Streamlit-Interaktion
            if st.button(
                card['title'],
                key=f"btn_{card['id']}",
                use_container_width=True,
                type="primary",
            ):
                selected_mode = card['id']

    # Footer
    st.markdown(
        """
        <div style='text-align: center; color: rgba(255,255,255,0.7); margin-top: 3rem; font-size: 0.9rem;'>
            <p>Pocket Calculator - Altersvorsorge-Vergleichsrechner</p>
            <p style='font-size: 0.8em;'>Keine Anlageberatung. Alle Berechnungen ohne Gewähr.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return selected_mode


def render_mode_header(mode: str):
    """
    Rendert einen Header mit dem aktuellen Modus und einem Zurück-Button.

    Args:
        mode: Aktueller Modus ('intelligent', 'learning', 'quick_check')
    """
    mode_info = {
        "intelligent": {"icon": "🤖", "name": "Intelligent Mode", "color": "#667eea"},
        "learning": {"icon": "📚", "name": "Learning Mode", "color": "#764ba2"},
        "quick_check": {"icon": "⚡", "name": "Quick Check Mode", "color": "#f093fb"},
    }

    info = mode_info.get(mode, {"icon": "💰", "name": "Unknown Mode", "color": "#333"})

    col1, col2 = st.columns([6, 1])

    with col1:
        st.markdown(
            f"""
            <div style="background: {info['color']}; color: white; padding: 1rem 2rem;
                        border-radius: 10px; margin-bottom: 2rem; display: flex; align-items: center;">
                <span style="font-size: 2rem; margin-right: 1rem;">{info['icon']}</span>
                <span style="font-size: 1.5rem; font-weight: bold;">{info['name']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if st.button("🏠 Zurück", key="back_to_selection", use_container_width=True):
            st.session_state.selected_mode = None
            st.rerun()
