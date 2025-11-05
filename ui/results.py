"""
Ergebnisanzeige und Visualisierungen
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from calculators.comparison import Comparison
from utils.tax_calculator import calculate_retirement_tax_rate


def display_overview(comparison: Comparison):
    """
    Zeigt Übersicht der Ergebnisse als Metrics

    Args:
        comparison: Comparison-Objekt mit allen Ergebnissen
    """
    st.header("📊 Ergebnisübersicht")

    cols = st.columns(len(comparison.results))
    for idx, (col, result) in enumerate(zip(cols, comparison.results)):
        with col:
            rank_emoji = ["🥇", "🥈", "🥉"][idx] if idx < 3 else f"#{idx + 1}"
            st.subheader(f"{rank_emoji} {result.name}")

            # Endwert VOR Steuern (brutto)
            st.metric(
                "Endwert",
                f"{result.gross_value:,.0f} €",
                help="Endwert VOR Steuern (brutto)"
            )

            st.metric("Brutto-Einzahlungen", f"{result.gross_paid:,.0f} €")

            # Staatliche Zulagen (bei allen anzeigen, auch wenn 0€)
            st.metric("💰 Staatliche Zulagen", f"{result.state_allowances:,.0f} €")

            # Eingesparte Steuern (bei allen anzeigen, auch wenn 0€)
            st.metric("💵 Eingesparte Steuern", f"{result.tax_savings:,.0f} €")

            # Netto-Eigeninvestition (immer anzeigen)
            st.metric("🔹 Netto-Eigeninvestition", f"{result.net_investment:,.0f} €")

            # Bruttorendite und Nettorendite getrennt anzeigen
            st.metric("📊 Bruttorendite (p.a.)", f"{result.gross_return * 100:.2f}%")
            st.metric("📉 Nettorendite (p.a.)", f"{result.net_return * 100:.2f}%")
            st.metric("💹 Gesamtrendite (ROI)", f"{result.return_percentage:.2f}%",
                     help="Return on Investment: Gewinn geteilt durch Netto-Eigeninvestition über gesamte Laufzeit")


def display_detailed_table(comparison: Comparison, yearly_pension_income: float, etf_tax_allowance: float = 1000,
                          etf_lump_sum_percentage: float = 0.0):
    """
    Zeigt detaillierte Vergleichstabelle

    Args:
        comparison: Comparison-Objekt mit allen Ergebnissen
        yearly_pension_income: Jährliches Renteneinkommen für Steuerberechnung
        etf_tax_allowance: Sparerpauschbetrag für ETF (default: 1000€)
        etf_lump_sum_percentage: Anteil Einmalauszahlung bei ETF (0-100%)
    """
    st.markdown("---")
    st.header("📋 Detaillierter Vergleich")

    # Info-Box bei ETF-Einmalauszahlung
    if etf_lump_sum_percentage > 0:
        if etf_lump_sum_percentage == 100:
            st.info(f"""
💵 **ETF-Auszahlungsstrategie: Einmalauszahlung (100%)**

Bei vollständiger Einmalauszahlung wird das gesamte Kapital auf einmal entnommen und versteuert:
- Nur der **Gewinnanteil** wird mit Abgeltungssteuer (26,375%) besteuert
- Freibetrag ({etf_tax_allowance:,.0f}€) wird einmalig angerechnet
- **Vorteil**: Volle Kontrolle über das gesamte Kapital
- **Nachteil**: Hohe Steuerlast auf einmal, kein Kapitalerhalt
            """)
        else:
            st.info(f"""
🔀 **ETF-Auszahlungsstrategie: Kombination ({etf_lump_sum_percentage:.0f}% Einmal / {100-etf_lump_sum_percentage:.0f}% Rente)**

Ihr Kapital wird aufgeteilt:
- **{etf_lump_sum_percentage:.0f}% Einmalauszahlung**: Sofort verfügbar (Gewinnanteil wird versteuert)
- **{100-etf_lump_sum_percentage:.0f}% Verrentung**: Monatliche Entnahme (4% p.a.) mit Kapitalerhalt
- Freibetrag ({etf_tax_allowance:,.0f}€) wird bei Einmalauszahlung verbraucht

**Hinweis**: Bei Kombination fällt der Freibetrag nur für die Einmalauszahlung an (kann nicht doppelt genutzt werden).
            """)
    else:
        # Nur Verrentung
        has_etf = any("ETF" in result.name for result in comparison.results)
        if has_etf:
            st.info("""
📊 **ETF-Auszahlungsstrategie: Verrentung (4% p.a.)**

Bei der Verrentung bleibt Ihr Kapital erhalten:
- Jährliche Entnahme: 4% des Gesamtkapitals
- Nur der **Gewinnanteil** der Entnahme wird versteuert
- Kapital bleibt investiert und wächst weiter
- **Vorteil**: Nachhaltigkeit, Kapital bleibt als Notreserve/Erbe
            """)

    df_data = []
    for result in comparison.results:
        # ETF: Berücksichtige Auszahlungsstrategie
        is_etf = "ETF" in result.name

        if is_etf and etf_lump_sum_percentage > 0:
            # ETF mit Einmalauszahlung oder Kombination (verwende gross_value)
            lump_sum_amount = result.gross_value * (etf_lump_sum_percentage / 100)
            remaining_amount = result.gross_value - lump_sum_amount

            # Steuer auf Einmalauszahlung (sofort fällig)
            gross_profit = result.gross_value - result.total_paid
            lump_sum_gain = gross_profit * (etf_lump_sum_percentage / 100)
            lump_sum_taxable = max(0, lump_sum_gain - etf_tax_allowance)
            lump_sum_tax = lump_sum_taxable * 0.26375
            lump_sum_net = lump_sum_amount - lump_sum_tax

            # Rest als Rente (4% p.a.)
            monthly_payout = remaining_amount * 0.04 / 12
            yearly_payout = monthly_payout * 12
        else:
            # Normale Verrentung (4% p.a.) für alle oder nur ETF ohne Einmalauszahlung (verwende gross_value)
            lump_sum_amount = 0
            lump_sum_net = 0
            remaining_amount = result.gross_value
            monthly_payout = result.gross_value * 0.04 / 12
            yearly_payout = monthly_payout * 12

        # Steuerbelastung auf die laufende Rente
        # WICHTIG: ETF wird IMMER mit Abgeltungssteuer besteuert, unabhängig vom Einkommen!
        if is_etf:
            # ETF: Abgeltungssteuer (26,375%) - fix, unabhängig vom Einkommen
            tax_rate_on_payout = 0.26375

            if etf_lump_sum_percentage < 100:
                # Nur wenn es noch eine laufende Rente gibt
                # Bei ETF: Nur der Gewinnanteil der Entnahme wird besteuert!
                gross_profit = result.gross_value - result.total_paid
                remaining_gain = gross_profit * ((100 - etf_lump_sum_percentage) / 100)
                gain_ratio = remaining_gain / remaining_amount if remaining_amount > 0 else 0
                taxable_portion = yearly_payout * gain_ratio

                # Freibetrag wurde bereits bei Einmalauszahlung verbraucht, daher 0
                # (Vereinfachung: Freibetrag nur 1x pro Jahr nutzbar)
                freibetrag_remaining = 0 if lump_sum_amount > 0 else etf_tax_allowance
                taxable_portion_after_allowance = max(0, taxable_portion - freibetrag_remaining)
                tax_on_payout = taxable_portion_after_allowance * tax_rate_on_payout
            else:
                # 100% Einmalauszahlung - keine laufende Rente
                tax_on_payout = 0
        else:
            # Basisrente/Riester: Nachgelagerte Besteuerung mit persönlichem Steuersatz
            # Hier wird die GESAMTE Auszahlung besteuert (nachgelagerte Besteuerung)
            total_retirement_income = yearly_pension_income + yearly_payout
            tax_rate_on_payout = calculate_retirement_tax_rate(total_retirement_income)
            tax_on_payout = yearly_payout * tax_rate_on_payout

        net_payout = yearly_payout - tax_on_payout

        # Tabellendaten zusammenstellen
        row_data = {
            "Produkt": result.name,
            "Brutto-Einzahlungen": f"{result.gross_paid:,.2f} €",
            "Staatliche Zulagen": f"{result.state_allowances:,.2f} €",
            "Eingesparte Steuern": f"{result.tax_savings:,.2f} €",
            "Netto-Eigeninvestition": f"{result.net_investment:,.2f} €",
            "Gesamtkosten": f"{result.total_costs:,.2f} €",
            "Endwert (vor Steuern)": f"{result.gross_value:,.2f} €",
            "Endwert (nach Steuern)": f"{result.total_value:,.2f} €",
            "Gewinn": f"{result.profit:,.2f} €",
            "Gesamtrendite (ROI)": f"{result.return_percentage:.2f}%",
            "Bruttorendite (p.a.)": f"{result.gross_return * 100:.2f}%",
            "Nettorendite (p.a.)": f"{result.net_return * 100:.2f}%",
        }

        # ETF-spezifische Spalten bei Einmalauszahlung
        if is_etf and etf_lump_sum_percentage > 0:
            row_data["Einmalauszahlung (brutto)"] = f"{lump_sum_amount:,.2f} €"
            row_data["Steuer auf Einmalauszahlung"] = f"{lump_sum_tax:,.2f} €"
            row_data["Einmalauszahlung (netto)"] = f"{lump_sum_net:,.2f} €"

        if etf_lump_sum_percentage < 100 or not is_etf:
            # Nur wenn es eine laufende Rente gibt
            row_data["Monatl. Rente (brutto, 4%)"] = f"{monthly_payout:,.2f} €"
            row_data["Steuersatz bei Auszahlung"] = f"{tax_rate_on_payout * 100:.1f}%"
            row_data["Monatl. Rente (netto)"] = f"{net_payout / 12:,.2f} €"

        df_data.append(row_data)

    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def display_wealth_development_chart(comparison: Comparison, monthly_contribution: float, years: int):
    """
    Zeigt Vermögensentwicklung als Liniendiagramm

    Args:
        comparison: Comparison-Objekt mit allen Ergebnissen
        monthly_contribution: Monatlicher Sparbeitrag
        years: Anlagedauer
    """
    st.markdown("---")
    st.header("📈 Vermögensentwicklung über die Jahre")

    fig = go.Figure()

    for result in comparison.results:
        years_list = [year for year, _ in result.yearly_values]
        values_list = [value for _, value in result.yearly_values]

        fig.add_trace(go.Scatter(
            x=years_list,
            y=values_list,
            mode='lines+markers',
            name=result.name,
            line=dict(width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Jahr: %{x}<br>' +
                         'Wert: %{y:,.2f} €<br>' +
                         '<extra></extra>'
        ))

    # Einzahlungslinie hinzufügen
    total_contributions = [monthly_contribution * 12 * year for year in range(1, years + 1)]
    fig.add_trace(go.Scatter(
        x=list(range(1, years + 1)),
        y=total_contributions,
        mode='lines',
        name='Eigene Einzahlungen',
        line=dict(width=2, dash='dash', color='gray'),
        hovertemplate='Jahr: %{x}<br>' +
                     'Einzahlungen: %{y:,.2f} €<br>' +
                     '<extra></extra>'
    ))

    fig.update_layout(
        title="Vermögensentwicklung im Vergleich",
        xaxis_title="Jahre",
        yaxis_title="Vermögen (€)",
        hovermode='x unified',
        template="plotly_white",
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def display_cost_breakdown_chart(comparison: Comparison):
    """
    Zeigt Kostenaufschlüsselung als Stacked Bar Chart

    Args:
        comparison: Comparison-Objekt mit allen Ergebnissen
    """
    st.markdown("---")
    st.header("💶 Kostenaufschlüsselung & Förderung")

    fig_cost = go.Figure()

    product_names = [r.name for r in comparison.results]
    net_investments = [r.net_investment for r in comparison.results]
    state_allowances = [r.state_allowances for r in comparison.results]
    tax_savings = [r.tax_savings for r in comparison.results]

    # Netto-Eigeninvestition (was wirklich aus der Tasche kam)
    fig_cost.add_trace(go.Bar(
        x=product_names,
        y=net_investments,
        name='Netto-Eigeninvestition',
        marker_color='#FF6B6B',
        text=[f"{v:,.0f} €" for v in net_investments],
        textposition='inside',
        hovertemplate='<b>Netto-Eigeninvestition</b><br>%{y:,.0f} €<extra></extra>'
    ))

    # Staatliche Zulagen
    fig_cost.add_trace(go.Bar(
        x=product_names,
        y=state_allowances,
        name='Staatliche Zulagen',
        marker_color='#4ECDC4',
        text=[f"+{v:,.0f} €" if v > 0 else "" for v in state_allowances],
        textposition='inside',
        hovertemplate='<b>Staatliche Zulagen</b><br>%{y:,.0f} €<extra></extra>'
    ))

    # Eingesparte Steuern
    fig_cost.add_trace(go.Bar(
        x=product_names,
        y=tax_savings,
        name='Eingesparte Steuern',
        marker_color='#95E1D3',
        text=[f"+{v:,.0f} €" if v > 0 else "" for v in tax_savings],
        textposition='inside',
        hovertemplate='<b>Eingesparte Steuern</b><br>%{y:,.0f} €<extra></extra>'
    ))

    fig_cost.update_layout(
        title="Was zahlen Sie wirklich? (Brutto-Einzahlungen aufgeteilt)",
        xaxis_title="Produkt",
        yaxis_title="Betrag (€)",
        barmode='stack',
        template="plotly_white",
        height=500,
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )

    st.plotly_chart(fig_cost, use_container_width=True)

    # Erklärung
    st.info("""
    **📊 So lesen Sie diese Grafik:**

    - **Rot (Netto-Eigeninvestition)**: Das Geld, das wirklich aus Ihrer Tasche kommt
    - **Türkis (Staatliche Zulagen)**: Geschenktes Geld vom Staat (nur Riester)
    - **Hellgrün (Eingesparte Steuern)**: Steuerersparnis während der Ansparphase (Riester + Basisrente)

    **Zusammen ergeben diese die Brutto-Einzahlungen** (= monatlicher Beitrag × Monate + Einmaleinzahlung)
    """)


def display_endvalue_comparison_chart(comparison: Comparison):
    """
    Zeigt Endwert-Vergleich als Balkendiagramm

    Args:
        comparison: Comparison-Objekt mit allen Ergebnissen
    """
    st.markdown("---")
    st.header("📊 Endwert-Vergleich (vor Steuern)")

    fig_bar = go.Figure()

    product_names = [r.name for r in comparison.results]
    gross_values = [r.gross_value for r in comparison.results]
    contributions = [r.total_paid for r in comparison.results]
    profits = [r.gross_value - r.total_paid for r in comparison.results]

    fig_bar.add_trace(go.Bar(
        x=product_names,
        y=contributions,
        name='Eigene Einzahlungen',
        marker_color='lightblue',
        text=[f"{v:,.0f} €" for v in contributions],
        textposition='inside'
    ))

    fig_bar.add_trace(go.Bar(
        x=product_names,
        y=profits,
        name='Gewinn',
        marker_color='lightgreen',
        text=[f"{v:,.0f} €" for v in profits],
        textposition='inside'
    ))

    fig_bar.update_layout(
        title="Zusammensetzung des Endwerts (vor Steuern)",
        xaxis_title="Produkt",
        yaxis_title="Betrag (€)",
        barmode='stack',
        template="plotly_white",
        height=500,
        hovermode='x unified'
    )

    st.plotly_chart(fig_bar, use_container_width=True)


def display_riester_payout_details(comparison: Comparison, riester_lump_sum: int, yearly_pension_income: float):
    """
    Zeigt Details zur Riester-Auszahlung

    Args:
        comparison: Comparison-Objekt mit allen Ergebnissen
        riester_lump_sum: Prozentsatz der Einmalauszahlung
        yearly_pension_income: Jährliches Renteneinkommen
    """
    if riester_lump_sum == 0:
        return

    st.markdown("---")
    st.header("💶 Riester-Auszahlungsdetails")

    # Finde Riester-Ergebnis
    riester_result = next((r for r in comparison.results if "Riester" in r.name), None)
    if riester_result:
        lump_sum_amount = riester_result.gross_value * (riester_lump_sum / 100)
        remaining_for_pension = riester_result.gross_value - lump_sum_amount

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                f"Einmalauszahlung ({riester_lump_sum}%)",
                f"{lump_sum_amount:,.2f} €"
            )
        with col2:
            st.metric(
                "Verbleibend für Rente",
                f"{remaining_for_pension:,.2f} €"
            )
        with col3:
            monthly_pension = remaining_for_pension * 0.04 / 12
            st.metric(
                "Monatliche Rente (4%, brutto)",
                f"{monthly_pension:,.2f} €"
            )

        st.warning(f"""
⚠️ **Steuerliche Auswirkung der Einmalauszahlung:**

Die Einmalauszahlung von {lump_sum_amount:,.2f} € wird in dem Jahr, in dem Sie in Rente gehen,
zu Ihrem sonstigen Einkommen addiert und **voll versteuert**.

**Beispiel bei Rentenbeginn:**
- Sonstiges Einkommen (z.B. aus Arbeit): {yearly_pension_income:,.0f} €/Jahr
- + Riester-Einmalauszahlung: {lump_sum_amount:,.0f} €
- = Gesamteinkommen: {yearly_pension_income + lump_sum_amount:,.0f} €

Dies kann Ihren Steuersatz deutlich erhöhen! Erwägen Sie:
1. Auszahlung in ein Jahr mit niedrigem Einkommen verschieben
2. Nach Renteneintritt auszahlen lassen (niedrigeres Einkommen)
3. Oder ganz auf Einmalauszahlung verzichten → {remaining_for_pension * 0.04 / 12 + lump_sum_amount * 0.04 / 12:,.2f} € monatlich statt {monthly_pension:,.2f} €
        """)


def display_recommendation(comparison: Comparison, initial_investment: float, years: int):
    """
    Zeigt Empfehlung basierend auf den Ergebnissen

    Args:
        comparison: Comparison-Objekt mit allen Ergebnissen
        initial_investment: Einmalinvestition
        years: Anlagedauer
    """
    st.markdown("---")
    st.header("💡 Empfehlung")

    best = comparison.results[0]
    best_monthly_pension = best.gross_value * 0.04 / 12

    # Wenn Einmaleinzahlung genutzt wurde, zeige das an
    if initial_investment > 0:
        st.info(f"""
💰 **Sie haben eine Einmaleinzahlung von {initial_investment:,.0f} € eingeplant.**

Diese wächst über {years} Jahre deutlich an und trägt wesentlich zum Endergebnis bei!
        """)

    st.success(f"""
    **Basierend auf Ihren Eingaben bietet {best.name} den höchsten Endwert von {best.gross_value:,.2f} € (vor Steuern).**

    Bei einer 4%-Entnahme entspricht das einer monatlichen Zusatzrente von ca. **{best_monthly_pension:,.2f} € (brutto)**.
    """)

    st.info("""
    **Wichtige Hinweise:**

    - Diese Berechnung ist eine **Vereinfachung** und ersetzt keine professionelle Finanzberatung
    - **Flexibilität**: ETFs können jederzeit verkauft werden, Riester/Rürup sind bis zur Rente gebunden
    - **Garantien**: Riester garantiert Kapitalerhalt, ETFs unterliegen Marktschwankungen
    - **Steuervorteile**: Variieren je nach persönlicher Situation und Einkommen
    - **Inflation**: Wurde in dieser Berechnung nicht berücksichtigt
    - **Kosten**: Können je nach Anbieter erheblich variieren - Vergleichen lohnt sich!
    - **Rentensteuer**: Basierend auf Ihrem Gesamteinkommen im Ruhestand berechnet
    """)


def display_results(comparison: Comparison, params: dict):
    """
    Zeigt alle Ergebnisse und Visualisierungen

    Args:
        comparison: Comparison-Objekt mit allen Ergebnissen
        params: Dictionary mit allen Parametern
    """
    st.success("✅ Berechnung abgeschlossen!")

    # Übersicht
    display_overview(comparison)

    # Detaillierte Tabelle
    etf_tax_allowance = params.get("etf", {}).get("tax_allowance", 1000)
    etf_lump_sum_percentage = params.get("etf", {}).get("lump_sum_percentage", 0.0)
    display_detailed_table(comparison, params["yearly_pension_income"], etf_tax_allowance, etf_lump_sum_percentage)

    # Kostenaufschlüsselung & Förderung
    display_cost_breakdown_chart(comparison)

    # Vermögensentwicklung
    display_wealth_development_chart(
        comparison,
        params["monthly_contribution"],
        params["years"]
    )

    # Endwert-Vergleich
    display_endvalue_comparison_chart(comparison)

    # Riester-Auszahlungsdetails
    if params.get("include_riester") and params.get("riester_lump_sum", 0) > 0:
        display_riester_payout_details(
            comparison,
            params["riester_lump_sum"],
            params["yearly_pension_income"]
        )

    # Empfehlung
    display_recommendation(
        comparison,
        params["initial_investment"],
        params["years"]
    )
