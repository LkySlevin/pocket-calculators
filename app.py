#!/usr/bin/env python3
"""
Streamlit Web-App für Altersvorsorge-Vergleich
Mit Mode-Selection und verschiedenen Betriebsmodi
"""
import streamlit as st
from ui.config import setup_page
from ui.mode_selection import render_mode_selection, render_mode_header
from modes.intelligent_mode import render_intelligent_mode
from modes.learning_mode import render_learning_mode
from modes.quick_check_mode import render_quick_check_mode


# Seitenkonfiguration
setup_page()

# Session State initialisieren
if "selected_mode" not in st.session_state:
    st.session_state.selected_mode = None

# Modus-Auswahl oder gewählten Modus anzeigen
if st.session_state.selected_mode is None:
    # Zeige Mode Selection Screen
    selected_mode = render_mode_selection()

    # Wenn ein Modus ausgewählt wurde, speichere ihn im Session State
    if selected_mode:
        st.session_state.selected_mode = selected_mode
        st.rerun()

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
