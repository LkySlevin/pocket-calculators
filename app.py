#!/usr/bin/env python3
"""
Streamlit Web-App für Altersvorsorge-Vergleich
Mit Mode-Selection und verschiedenen Betriebsmodi

Workflow:
1. Mode Selection (User wählt Modus)
2. User Profiling (Profil laden oder erstellen, VERPFLICHTEND gemäß IDD-Richtlinie)
3. Berechnungen
"""
import streamlit as st
from ui.config import setup_page
from ui.mode_selection import render_mode_selection, render_mode_header
from ui.user_profiling import render_user_profile_form
from modes.intelligent_mode import render_intelligent_mode
from modes.learning_mode import render_learning_mode
from modes.quick_check_mode import render_quick_check_mode


# Seitenkonfiguration
setup_page()

# Session State initialisieren
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = None
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "profiling_step" not in st.session_state:
    st.session_state.profiling_step = 1


# SCHRITT 1: Modus-Auswahl (IMMER ZUERST)
if st.session_state.selected_mode is None:
    # Zeige Mode Selection Screen
    selected_mode = render_mode_selection()

    # Wenn ein Modus ausgewählt wurde, speichere ihn im Session State
    if selected_mode:
        st.session_state.selected_mode = selected_mode
        st.rerun()

# SCHRITT 2: User Profiling (nach Modus-Auswahl, VERPFLICHTEND)
elif st.session_state.user_profile is None:
    # Zeige Profil-Optionen: Laden oder Neu erstellen
    st.title(f"🎯 {st.session_state.selected_mode.replace('_', ' ').title()} Mode")

    st.markdown("---")
    st.header("👤 Nutzerprofil")

    st.info("""
    📋 **Nutzerprofil erforderlich**

    Gemäß IDD-Richtlinie benötigen wir Informationen über Ihre Situation und Risikobereitschaft,
    um Ihnen geeignete Empfehlungen geben zu können.

    Wählen Sie eine Option:
    """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ Neues Profil erstellen", type="primary", use_container_width=True):
            st.session_state.create_new_profile = True
            st.rerun()

    with col2:
        if st.button("📂 Profil laden (Demo)", use_container_width=True):
            # TODO: Später echtes Profil-Laden implementieren
            # Für jetzt: Demo-Profil erstellen
            st.session_state.user_profile = {
                "age": 35,
                "gross_salary": 50000,
                "children": 0,
                "retirement_age": 67,
                "church_tax": False,
                "married": False,
                "partner_salary": 0,
                "tax_rate": 0.35,
                "years_until_retirement": 32,
                "risk_profile": {
                    "risk_class": 3,
                    "risk_label": "Ausgewogen-chancenorientiert",
                    "description": "Ausgewogenes Verhältnis zwischen Sicherheit und Renditechance",
                    "knowledge_level": 2,
                    "experience_level": 2,
                    "loss_tolerance": 3,
                    "investment_horizon": 32
                },
                "kpis": {
                    "return_vs_security": 0.5,  # 0 = Sicherheit, 1 = Rendite
                    "liquidity": 0.3,  # 0 = unwichtig, 1 = sehr wichtig
                    "flexibility": 0.5  # 0 = unwichtig, 1 = sehr wichtig
                }
            }
            st.success("✅ Demo-Profil geladen!")
            st.rerun()

    # Zurück-Button
    if st.button("⬅️ Zurück zur Modus-Auswahl"):
        st.session_state.selected_mode = None
        st.rerun()

    # Wenn "Neues Profil erstellen" geklickt wurde
    if st.session_state.get('create_new_profile', False):
        st.markdown("---")
        profile = render_user_profile_form()

        if profile:
            # Profil speichern
            st.session_state.user_profile = profile
            st.session_state.create_new_profile = False
            st.balloons()
            st.success("✅ Profil erfolgreich erstellt!")

            # Kleine Verzögerung, damit Nutzer die Bestätigung sieht
            import time
            time.sleep(1)
            st.rerun()

# SCHRITT 3: Berechnungen (nur wenn Modus + Profil vorhanden)
else:
    # Zeige den gewählten Modus
    mode = st.session_state.selected_mode

    # Render Mode Header mit Zurück-Button
    render_mode_header(mode)

    # Render den entsprechenden Modus
    if mode == "intelligent":
        render_intelligent_mode()
    elif mode == "learning":
        render_learning_mode()
    elif mode == "quick_check":
        render_quick_check_mode()
    else:
        st.error(f"❌ Unbekannter Modus: {mode}")
        if st.button("Zurück zur Auswahl"):
            st.session_state.selected_mode = None
            st.rerun()
