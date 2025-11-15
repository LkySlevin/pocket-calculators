"""
ETF-Sparplan Rechner für private Altersvorsorge
"""
from .base_calculator import BaseCalculator, InvestmentResult
from .dynamics import calculate_with_contribution_dynamics, adjust_for_inflation


class ETFCalculator(BaseCalculator):
    """
    Rechner für ETF-Sparpläne (private Altersvorsorge)

    Berücksichtigt:
    - Keine Steuervorteile während Ansparphase
    - Abgeltungssteuer (25% + Soli) auf Gewinne bei Entnahme
    - Sparerpauschbetrag (1000€ für Singles, 2000€ für Paare)
    - TER (Total Expense Ratio) der ETFs
    """

    def __init__(
        self,
        monthly_contribution: float,
        years: int,
        annual_return: float = 0.07,
        tax_rate: float = 0.42,
        ter: float = 0.002,  # 0.2% TER typisch für ETFs
        capital_gains_tax: float = 0.26375,  # 25% Abgeltungssteuer + 5.5% Soli
        tax_allowance: float = 1000,  # Sparerpauschbetrag
        order_fee: float = 1.0,  # Ordergebühr pro Ausführung
        depot_fee_yearly: float = 0.0,  # Jährliche Depotgebühr
        spread: float = 0.002,  # Spread (Geld-Brief-Spanne) als Prozent
        initial_investment: float = 0.0,  # Einmaleinzahlung zu Beginn
        rebalancing_count: int = 0,  # Anzahl der Umschichtungen während Laufzeit
        contribution_dynamics: float = 0.0,  # NEU: Jährliche Beitragssteigerung
        inflation_rate: float = 0.02  # NEU: Inflationsrate für reale Werte
    ):
        """
        Args:
            monthly_contribution: Monatlicher Sparbeitrag
            years: Anlagedauer in Jahren
            annual_return: Erwartete Bruttorendite (vor Kosten)
            tax_rate: Persönlicher Steuersatz (für Vergleichszwecke)
            ter: Total Expense Ratio (Gesamtkostenquote)
            capital_gains_tax: Abgeltungssteuer + Solidaritätszuschlag
            tax_allowance: Sparerpauschbetrag pro Jahr
            order_fee: Ordergebühr pro Sparplan-Ausführung
            depot_fee_yearly: Jährliche Depotgebühr
            spread: Spread (Geld-Brief-Spanne) beim Kauf
            initial_investment: Einmaleinzahlung zu Beginn
            rebalancing_count: Anzahl der Umschichtungen (Auflösung + Neuanlage)
            contribution_dynamics: Jährliche Beitragssteigerung (0.02 = 2%)
            inflation_rate: Inflationsrate für Kaufkraft-Berechnung (0.02 = 2%)
        """
        super().__init__(monthly_contribution, years, annual_return, tax_rate)
        self.ter = ter
        self.capital_gains_tax = capital_gains_tax
        self.tax_allowance = tax_allowance
        self.order_fee = order_fee
        self.depot_fee_yearly = depot_fee_yearly
        self.spread = spread
        self.initial_investment = initial_investment
        self.rebalancing_count = rebalancing_count
        self.contribution_dynamics = contribution_dynamics
        self.inflation_rate = inflation_rate

    def calculate(self) -> InvestmentResult:
        """Berechnet den Endwert eines ETF-Sparplans nach Steuern (mit optionalen Umschichtungen und Dynamik)"""

        # Nettorendite nach TER und Spread
        net_annual_return = self.annual_return - self.ter - self.spread

        # --- MIT BEITRAGSDYNAMIK ---
        if self.contribution_dynamics > 0:
            # Berechnung mit dynamischen Beiträgen
            final_value, yearly_values, total_paid = calculate_with_contribution_dynamics(
                initial_monthly_contribution=self.monthly_contribution,
                annual_dynamics_rate=self.contribution_dynamics,
                years=self.years,
                annual_return=net_annual_return,
                initial_investment=self.initial_investment
            )
        else:
            # Gesamte Einzahlungen (inkl. Einmaleinzahlung)
            total_paid = self.monthly_contribution * 12 * self.years + self.initial_investment

            # --- MIT UMSCHICHTUNGEN ---
            if self.rebalancing_count > 0:
                return self._calculate_with_rebalancing(net_annual_return, total_paid)

            # --- OHNE UMSCHICHTUNGEN & OHNE DYNAMIK (Original-Logik) ---
            # Berechne Endwert mit Zinseszins für monatliche Sparraten
            final_value, yearly_values = self._compound_interest(
                self.monthly_contribution,
                net_annual_return,
                self.years
            )

            # Einmaleinzahlung mit Zinseszins (nur wenn keine Dynamik)
            if self.initial_investment > 0:
                # Spread-Kosten bei Einmalkauf
                initial_after_spread = self.initial_investment * (1 - self.spread)
                # Wachstum der Einmaleinzahlung
                initial_growth = initial_after_spread * ((1 + net_annual_return) ** self.years)
                final_value += initial_growth

        # Ordergebühren (monatlich) + einmalig für Initial Investment
        total_order_fees = self.order_fee * 12 * self.years
        if self.initial_investment > 0:
            total_order_fees += self.order_fee  # Eine Ordergebühr für Einmaleinzahlung

        # Depotgebühren
        total_depot_fees = self.depot_fee_yearly * self.years

        # Ziehe Gebühren ab
        final_value = final_value - total_order_fees - total_depot_fees

        # Kursgewinn
        capital_gain = final_value - total_paid

        # Steuer auf Kursgewinn (nach Sparerpauschbetrag)
        # WICHTIG: Bei ETF gilt IMMER die Abgeltungssteuer (26,375%), unabhängig vom persönlichen Steuersatz!
        # Bei Einmalverkauf am Ende steht nur der Freibetrag des Verkaufsjahres zur Verfügung.
        # Freibeträge der Vorjahre können nicht "angespart" werden - sie verfallen jährlich!
        total_tax_allowance = self.tax_allowance  # Nur 1x für das Verkaufsjahr
        taxable_gain = max(0, capital_gain - total_tax_allowance)
        tax_on_gains = taxable_gain * self.capital_gains_tax  # Abgeltungssteuer: 26,375%

        # Endwert nach Steuern
        final_value_after_tax = final_value - tax_on_gains

        # Gesamtkosten über Laufzeit (für Anzeigezwecke)
        # TER und Spread sind bereits in der Rendite berücksichtigt!
        # Berechne hypothetisches Endvermögen OHNE TER/Spread
        gross_return_no_costs = self.annual_return  # Ohne TER/Spread
        final_without_costs, _ = self._compound_interest(
            self.monthly_contribution,
            gross_return_no_costs,
            self.years
        )

        # Einmaleinzahlung ohne Kosten
        if self.initial_investment > 0:
            initial_growth_no_costs = self.initial_investment * ((1 + gross_return_no_costs) ** self.years)
            final_without_costs += initial_growth_no_costs

        # Der Unterschied ist was TER/Spread gekostet haben (inkl. direkter Gebühren)
        total_costs = final_without_costs - final_value

        return InvestmentResult(
            name="ETF-Sparplan (privat)",
            total_paid=total_paid,
            total_value=final_value_after_tax,
            net_return=net_annual_return,
            tax_benefit=0,  # Keine Steuervorteile während Ansparphase
            yearly_values=yearly_values,
            gross_paid=total_paid,  # Bei ETF sind Brutto = Netto (keine Förderung)
            state_allowances=0.0,  # Keine staatlichen Zulagen
            tax_savings=0.0,  # Keine Steuerersparnis während Ansparphase
            total_costs=total_costs,
            gross_return=self.annual_return,  # Bruttorendite vor Kosten
            gross_value=final_value  # Endwert VOR Steuern
        )

    def _calculate_with_rebalancing(self, net_annual_return: float, total_paid: float) -> InvestmentResult:
        """
        Berechnet ETF-Sparplan mit Umschichtungen.

        Bei jeder Umschichtung:
        - Auflösung: Steuern auf Gewinne (mit Freibetrag), Verkaufs-Spread
        - Neuanlage: Ordergebühr, Kauf-Spread
        """

        # Zeitpunkte der Umschichtungen gleichmäßig verteilen
        if self.rebalancing_count >= self.years:
            raise ValueError("Anzahl Umschichtungen darf nicht >= Laufzeit in Jahren sein")

        rebalancing_years = []
        if self.rebalancing_count > 0:
            interval = self.years / (self.rebalancing_count + 1)
            for i in range(1, self.rebalancing_count + 1):
                rebalancing_years.append(int(interval * i))

        # Simulation Jahr für Jahr
        balance = 0.0
        invested_capital = 0.0  # Einzahlungen bis jetzt
        yearly_values = []

        # Initiale Einzahlung
        if self.initial_investment > 0:
            invested_capital += self.initial_investment
            balance = self.initial_investment * (1 - self.spread)  # Spread beim Kauf

        total_order_fees = 0.0
        total_depot_fees = 0.0
        total_rebalancing_taxes = 0.0
        total_rebalancing_costs = 0.0
        remaining_tax_allowance = 0.0  # Wird jedes Jahr neu gesetzt

        for year in range(1, self.years + 1):
            # Jahresanfang: Freibetrag neu setzen
            remaining_tax_allowance = self.tax_allowance

            # Monatliche Einzahlungen mit Wachstum über das Jahr
            for month in range(12):
                monthly_rate = net_annual_return / 12
                balance = balance * (1 + monthly_rate)
                balance += self.monthly_contribution
                invested_capital += self.monthly_contribution
                total_order_fees += self.order_fee

            # Depotgebühr
            total_depot_fees += self.depot_fee_yearly

            # Umschichtung am Jahresende?
            if year in rebalancing_years:
                # 1. Auflösung: Steuern auf Gewinn berechnen
                current_gain = balance - invested_capital

                # Freibetrag anrechnen (vom aktuellen Jahr)
                taxable_gain = max(0, current_gain - remaining_tax_allowance)
                taxes = taxable_gain * self.capital_gains_tax  # Abgeltungssteuer: 26,375%
                total_rebalancing_taxes += taxes

                # Verbrauchter Freibetrag
                used_allowance = min(current_gain, remaining_tax_allowance)
                remaining_tax_allowance -= used_allowance

                # Verkaufs-Spread
                sell_spread_cost = balance * self.spread
                total_rebalancing_costs += sell_spread_cost

                # 2. Neuanlage: Nach Steuern und Kosten
                balance = balance - taxes - sell_spread_cost

                # Kauf-Spread
                buy_spread_cost = balance * self.spread
                total_rebalancing_costs += buy_spread_cost
                balance = balance - buy_spread_cost

                # Ordergebühr für Neuanlage
                total_order_fees += self.order_fee
                total_rebalancing_costs += self.order_fee

                # invested_capital bleibt gleich (nur Umschichtung, keine neue Einzahlung)

            yearly_values.append((year, balance))

        # Finale Kosten
        final_value = balance - total_depot_fees - total_order_fees

        # Finale Steuer (nur auf noch nicht besteuerte Gewinne)
        final_capital_gain = final_value - invested_capital

        # Freibetrag für letztes Jahr (falls nicht durch Umschichtung verbraucht)
        if self.years not in rebalancing_years:
            remaining_tax_allowance = self.tax_allowance

        final_taxable_gain = max(0, final_capital_gain - remaining_tax_allowance)
        final_tax = final_taxable_gain * self.capital_gains_tax  # Abgeltungssteuer: 26,375%

        final_value_after_tax = final_value - final_tax

        # Gesamtkosten berechnen (was hätte man ohne Kosten?)
        gross_return_no_costs = self.annual_return
        final_without_costs, _ = self._compound_interest(
            self.monthly_contribution,
            gross_return_no_costs,
            self.years
        )
        if self.initial_investment > 0:
            initial_growth_no_costs = self.initial_investment * ((1 + gross_return_no_costs) ** self.years)
            final_without_costs += initial_growth_no_costs

        total_costs = (final_without_costs - final_value_after_tax) - final_tax

        return InvestmentResult(
            name="ETF-Sparplan (privat)",
            total_paid=total_paid,
            total_value=final_value_after_tax,
            net_return=net_annual_return,
            tax_benefit=0,
            yearly_values=yearly_values,
            gross_paid=total_paid,
            state_allowances=0.0,
            tax_savings=0.0,
            total_costs=total_costs,
            gross_return=self.annual_return,  # Bruttorendite vor Kosten
            gross_value=final_value  # Endwert VOR Steuern
        )
