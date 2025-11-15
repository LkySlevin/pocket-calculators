"""
Advanced Visualization - Inflationsanpassung und Entnahmestrategien

Dieses Modul erweitert die Standard-Visualisierung um:
1. Inflationsbereinigte (reale) vs. nominale Werte
2. Entnahmestrategien-Visualisierung
3. Kapitalverzehr-Charts
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from typing import List
from calculators.comparison import Comparison
from calculators.dynamics import adjust_for_inflation
from calculators.withdrawal_strategy import (
    four_percent_rule,
    dynamic_percentage_withdrawal,
    fixed_monthly_pension,
    hybrid_withdrawal,
    WithdrawalResult
)


def display_inflation_adjusted_chart(
    comparison: Comparison,
    inflation_rate: float,
    show_real_values: bool = True
):
    """
    Zeigt inflationsbereinigte Kapitalentwicklung an.

    Args:
        comparison: Comparison-Objekt mit allen Ergebnissen
        inflation_rate: Inflationsrate (0.02 = 2%)
        show_real_values: True = reale Werte, False = nominale Werte
    """

    st.markdown("---")
    st.header("📈 Kapitalentwicklung über Zeit" + (" (inflationsbereinigt)" if show_real_values else " (nominal)"))

    if inflation_rate > 0 and show_real_values:
        st.info(f"""
        💡 **Inflationsbereinigte Darstellung (Kaufkraft)**

        Die Werte sind um {inflation_rate*100:.1f}% Inflation pro Jahr bereinigt.
        Das zeigt die tatsächliche Kaufkraft Ihres Kapitals im Laufe der Zeit.

        **Beispiel:** {100000:,.0f}€ in 30 Jahren haben bei {inflation_rate*100:.1f}% Inflation eine Kaufkraft von ca. {100000 / ((1 + inflation_rate) ** 30):,.0f}€ (in heutiger Währung).
        """)

    fig = go.Figure()

    for result in comparison.results:
        if result.yearly_values:
            years = list(range(len(result.yearly_values)))
            values = result.yearly_values

            # Inflationsanpassung wenn gewünscht
            if show_real_values and inflation_rate > 0:
                values = adjust_for_inflation(values, inflation_rate)

            fig.add_trace(go.Scatter(
                x=years,
                y=values,
                mode='lines+markers',
                name=result.name,
                line=dict(width=3),
                marker=dict(size=6),
                hovertemplate=(
                    '<b>%{fullData.name}</b><br>' +
                    'Jahr %{x}<br>' +
                    'Wert: %{y:,.0f}€' +
                    ('<br>(Kaufkraft)' if show_real_values else '<br>(Nominal)') +
                    '<extra></extra>'
                )
            ))

    fig.update_layout(
        title=f"Vermögensentwicklung {'(real)' if show_real_values else '(nominal)'}",
        xaxis_title="Jahre",
        yaxis_title=f"Kapital (€) {'- Kaufkraft' if show_real_values else '- Nominal'}",
        hovermode='x unified',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def display_withdrawal_strategies(
    final_capital: float,
    product_name: str,
    withdrawal_years: int = 30,
    annual_return: float = 0.04,
    annual_inflation: float = 0.02,
    desired_monthly_pension: float = 2000
):
    """
    Zeigt Vergleich verschiedener Entnahmestrategien.

    Args:
        final_capital: Verfügbares Kapital zu Rentenbeginn
        product_name: Name des Produkts (für Überschrift)
        withdrawal_years: Geplante Entnahmedauer (Default: 30 Jahre)
        annual_return: Erwartete Rendite des Restkapitals (Default: 4%)
        annual_inflation: Inflationsrate (Default: 2%)
        desired_monthly_pension: Gewünschte monatliche Rente (Default: 2000€)
    """

    st.markdown("---")
    st.header(f"💰 Entnahmestrategien für {product_name}")

    st.markdown(f"""
    **Verfügbares Kapital zu Rentenbeginn:** {final_capital:,.0f}€

    Vergleich verschiedener Strategien zur Kapitalentnahme über {withdrawal_years} Jahre:
    """)

    # Berechne alle Strategien
    strategy_4_percent = four_percent_rule(
        initial_capital=final_capital,
        withdrawal_years=withdrawal_years,
        annual_return=annual_return,
        annual_inflation=annual_inflation,
        with_inflation_adjustment=True
    )

    strategy_dynamic = dynamic_percentage_withdrawal(
        initial_capital=final_capital,
        withdrawal_percentage=0.04,
        withdrawal_years=withdrawal_years,
        annual_return=annual_return
    )

    strategy_fixed = fixed_monthly_pension(
        initial_capital=final_capital,
        monthly_pension=desired_monthly_pension,
        withdrawal_years=withdrawal_years,
        annual_return=annual_return
    )

    strategy_hybrid = hybrid_withdrawal(
        initial_capital=final_capital,
        fixed_monthly_pension=desired_monthly_pension * 0.8,  # 80% als Rente
        capital_reserve_percentage=0.2,  # 20% als Reserve
        withdrawal_years=withdrawal_years,
        annual_return=annual_return
    )

    # Übersichtstabelle
    st.markdown("### 📊 Strategien-Vergleich")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🎯 4%-Regel",
            f"{strategy_4_percent.avg_monthly_withdrawal:,.0f}€/Monat",
            delta=f"Restkapital: {strategy_4_percent.remaining_capital:,.0f}€",
            help="Trinity Study: 4% Entnahme mit Inflationsanpassung"
        )
        if strategy_4_percent.capital_depleted_year > 0:
            st.warning(f"⚠️ Aufgebraucht: Jahr {strategy_4_percent.capital_depleted_year}")
        else:
            st.success(f"✅ Sicher für {withdrawal_years} Jahre")

    with col2:
        st.metric(
            "📊 Dynamisch 4%",
            f"{strategy_dynamic.avg_monthly_withdrawal:,.0f}€/Monat",
            delta=f"Restkapital: {strategy_dynamic.remaining_capital:,.0f}€",
            help="4% vom jeweils aktuellen Kapital"
        )
        st.success("✅ Nie aufgebraucht")

    with col3:
        st.metric(
            "💵 Feste Rente",
            f"{strategy_fixed.avg_monthly_withdrawal:,.0f}€/Monat",
            delta=f"Restkapital: {strategy_fixed.remaining_capital:,.0f}€",
            help=f"Feste {desired_monthly_pension:,.0f}€/Monat"
        )
        if strategy_fixed.capital_depleted_year > 0:
            st.error(f"❌ Aufgebraucht: Jahr {strategy_fixed.capital_depleted_year}")
        else:
            st.success(f"✅ Reicht für {withdrawal_years} Jahre")

    with col4:
        st.metric(
            "🔀 Hybrid (80/20)",
            f"{strategy_hybrid.avg_monthly_withdrawal:,.0f}€/Monat",
            delta=f"Restkapital: {strategy_hybrid.remaining_capital:,.0f}€",
            help="80% Rente + 20% Reserve"
        )
        st.info(f"🏦 {final_capital * 0.2:,.0f}€ Reserve")

    # Kapitalverzehr-Chart
    st.markdown("### 📉 Kapitalverzehr über Zeit")

    _display_capital_depletion_chart([
        strategy_4_percent,
        strategy_dynamic,
        strategy_fixed,
        strategy_hybrid
    ])

    # Entnahmen-Chart
    st.markdown("### 💶 Monatliche Entnahmen über Zeit")

    _display_withdrawal_amounts_chart([
        strategy_4_percent,
        strategy_dynamic,
        strategy_fixed,
        strategy_hybrid
    ])

    # Empfehlung basierend auf Situation
    st.markdown("### 💡 Empfehlung")

    _display_strategy_recommendation(
        strategy_4_percent,
        strategy_dynamic,
        strategy_fixed,
        strategy_hybrid,
        final_capital,
        desired_monthly_pension
    )


def _display_capital_depletion_chart(strategies: List[WithdrawalResult]):
    """Zeigt Kapitalverzehr über Zeit für verschiedene Strategien."""

    fig = go.Figure()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for idx, strategy in enumerate(strategies):
        years = [y[0] for y in strategy.yearly_withdrawals]
        capital = [y[2] for y in strategy.yearly_withdrawals]

        fig.add_trace(go.Scatter(
            x=years,
            y=capital,
            mode='lines',
            name=strategy.strategy_name,
            line=dict(width=3, color=colors[idx]),
            fill='tozeroy',
            hovertemplate=(
                '<b>%{fullData.name}</b><br>' +
                'Jahr %{x}<br>' +
                'Restkapital: %{y:,.0f}€' +
                '<extra></extra>'
            )
        ))

    fig.update_layout(
        title="Restkapital über Zeit",
        xaxis_title="Jahre ab Rentenbeginn",
        yaxis_title="Verbleibendes Kapital (€)",
        hovermode='x unified',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def _display_withdrawal_amounts_chart(strategies: List[WithdrawalResult]):
    """Zeigt monatliche Entnahmen über Zeit."""

    fig = go.Figure()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for idx, strategy in enumerate(strategies):
        years = [y[0] for y in strategy.yearly_withdrawals]
        # Jahreswerte in Monatswerte umrechnen
        monthly_withdrawals = [y[1] / 12 for y in strategy.yearly_withdrawals]

        fig.add_trace(go.Scatter(
            x=years,
            y=monthly_withdrawals,
            mode='lines+markers',
            name=strategy.strategy_name,
            line=dict(width=2, color=colors[idx]),
            marker=dict(size=4),
            hovertemplate=(
                '<b>%{fullData.name}</b><br>' +
                'Jahr %{x}<br>' +
                'Monatl. Entnahme: %{y:,.0f}€' +
                '<extra></extra>'
            )
        ))

    fig.update_layout(
        title="Monatliche Rentenhöhe über Zeit",
        xaxis_title="Jahre ab Rentenbeginn",
        yaxis_title="Monatliche Rente (€)",
        hovermode='x unified',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def _display_strategy_recommendation(
    strategy_4p: WithdrawalResult,
    strategy_dyn: WithdrawalResult,
    strategy_fixed: WithdrawalResult,
    strategy_hybrid: WithdrawalResult,
    final_capital: float,
    desired_monthly_pension: float
):
    """Zeigt personalisierte Empfehlung basierend auf den Strategien."""

    # Prüfe welche Strategie am besten passt
    if strategy_fixed.success_rate >= 1.0:
        # Gewünschte Rente ist sicher machbar
        st.success(f"""
        ✅ **Empfehlung: Feste monatliche Rente ({desired_monthly_pension:,.0f}€/Monat)**

        Ihr Kapital reicht aus, um die gewünschte Rente sicher für {strategy_fixed.yearly_withdrawals[-1][0]} Jahre zu zahlen!

        **Vorteile:**
        - Planbare, konstante monatliche Rente
        - Keine Schwankungen
        - Einfach zu verstehen

        **Restkapital nach 30 Jahren:** {strategy_fixed.remaining_capital:,.0f}€
        """)

    elif strategy_4p.success_rate >= 1.0:
        # 4%-Regel ist sicher
        st.info(f"""
        💡 **Empfehlung: 4%-Regel mit Inflationsanpassung**

        Die klassische 4%-Regel ist für Ihre Situation optimal.

        **Vorteile:**
        - Wissenschaftlich fundiert (Trinity Study)
        - Inflationsangepasst (Kaufkraft bleibt erhalten)
        - Sehr sicher für 30 Jahre

        **Anfangsrente:** {strategy_4p.yearly_withdrawals[0][1] / 12:,.0f}€/Monat
        **Rente nach 30 Jahren:** {strategy_4p.yearly_withdrawals[-1][1] / 12:,.0f}€/Monat (inflationsangepasst)
        **Restkapital:** {strategy_4p.remaining_capital:,.0f}€
        """)

    elif strategy_hybrid.success_rate >= 0.8:
        # Hybrid ist eine gute Wahl
        st.warning(f"""
        ⚠️ **Empfehlung: Hybrid-Strategie (Rente + Reserve)**

        Ihre gewünschte Rente ist zu hoch für das verfügbare Kapital.
        Eine Kombination aus reduzierter Rente und Kapitalreserve ist sinnvoll.

        **Vorschlag:**
        - 80% des Kapitals für Rente: {desired_monthly_pension * 0.8:,.0f}€/Monat
        - 20% als Reserve: {final_capital * 0.2:,.0f}€ (für Notfälle/Erbe)

        **Restkapital nach 30 Jahren:** {strategy_hybrid.remaining_capital:,.0f}€
        """)

    else:
        # Dynamische Entnahme ist die sicherste Option
        st.error(f"""
        🔴 **Warnung: Gewünschte Rente nicht nachhaltig**

        Ihre gewünschte Rente von {desired_monthly_pension:,.0f}€/Monat ist zu hoch.

        **Empfehlung: Dynamische Entnahme (4% vom Restkapital)**

        **Vorteile:**
        - Kapital wird NIE aufgebraucht
        - Flexibilität bei Marktentwicklung
        - Restkapital kann vererbt werden

        **Durchschnittliche Rente:** {strategy_dyn.avg_monthly_withdrawal:,.0f}€/Monat
        **Restkapital nach 30 Jahren:** {strategy_dyn.remaining_capital:,.0f}€

        **Alternative:** Reduzieren Sie Ihre Rentenerwartung auf ca. {strategy_4p.avg_monthly_withdrawal:,.0f}€/Monat für eine sichere 4%-Regel.
        """)


def display_contribution_dynamics_explanation(
    initial_monthly: float,
    dynamics_rate: float,
    years: int
):
    """
    Zeigt Erklärung und Visualisierung der Beitragsdynamik.

    Args:
        initial_monthly: Anfänglicher monatlicher Beitrag
        dynamics_rate: Jährliche Steigerungsrate (0.02 = 2%)
        years: Anlagedauer
    """

    if dynamics_rate <= 0:
        return

    st.markdown("---")
    st.header(f"📈 Beitragsdynamik ({dynamics_rate*100:.1f}% p.a.)")

    # Berechne Entwicklung
    from calculators.dynamics import calculate_contributions_with_dynamics

    contributions = calculate_contributions_with_dynamics(
        initial_monthly_contribution=initial_monthly,
        annual_dynamics_rate=dynamics_rate,
        years=years
    )

    # Beispielhafte Werte anzeigen
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Jahr 1", f"{contributions[0][1]:,.0f}€/Monat")
    with col2:
        year_10 = contributions[9] if len(contributions) > 9 else contributions[-1]
        st.metric("Jahr 10", f"{year_10[1]:,.0f}€/Monat")
    with col3:
        year_20 = contributions[19] if len(contributions) > 19 else contributions[-1]
        st.metric("Jahr 20", f"{year_20[1]:,.0f}€/Monat")
    with col4:
        st.metric(f"Jahr {years}", f"{contributions[-1][1]:,.0f}€/Monat")

    st.info(f"""
    💡 **Vorteil der Dynamik:**

    Ihr Beitrag steigt von **{initial_monthly:,.0f}€** auf **{contributions[-1][1]:,.0f}€** pro Monat.
    Das entspricht einer Steigerung um **{((contributions[-1][1] / initial_monthly) - 1) * 100:.1f}%** über {years} Jahre.

    **Warum sinnvoll?**
    - Gleicht Inflation aus
    - Passt sich Gehaltserhöhungen an
    - Deutlich höheres Endkapital ohne große Belastung am Anfang
    """)
