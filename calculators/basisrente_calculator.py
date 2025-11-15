"""
Basisrente (Rürup-Rente) Rechner
"""
from .base_calculator import BaseCalculator, InvestmentResult
from .dynamics import calculate_with_contribution_dynamics


class BasisrenteCalculator(BaseCalculator):
    """
    Rechner für Basisrente (Rürup-Rente)

    Berücksichtigt:
    - Steuerliche Absetzbarkeit während Ansparphase (stufenweise bis 2025: 100%)
    - Volle nachgelagerte Besteuerung der Rente (stufenweise bis 2040: 100%)
    - Keine Kapitalentnahme möglich (nur Verrentung)
    - Kosten der Versicherung
    """

    def __init__(
        self,
        monthly_contribution: float,
        years: int,
        annual_return: float = 0.07,  # Gleiche Startrendite wie ETF (kann ETF-basiert sein)
        tax_rate: float = 0.42,
        deductible_percentage: float = 1.0,  # 100% ab 2025
        tax_rate_retirement: float = 0.30,  # Oft niedriger im Alter
        effective_costs: float = 0.015,  # 1.5% Effektivkosten pro Jahr (inkl. aller Kosten)
        honorar_fee: float = 0.0,  # Einmalige Honorargebühr (bei Nettopolicen)
        initial_investment: float = 0.0,  # Einmaleinzahlung zu Beginn
        contribution_dynamics: float = 0.0,  # NEU: Jährliche Beitragssteigerung
        inflation_rate: float = 0.02  # NEU: Inflationsrate
    ):
        """
        Args:
            monthly_contribution: Monatlicher Sparbeitrag
            years: Anlagedauer in Jahren
            annual_return: Erwartete Bruttorendite
            tax_rate: Persönlicher Steuersatz während Ansparphase
            deductible_percentage: Absetzbarkeit (1.0 = 100% ab 2025)
            tax_rate_retirement: Steuersatz im Rentenalter
            effective_costs: Effektivkosten pro Jahr (beinhaltet Abschluss-, Verwaltungs- und laufende Kosten)
            honorar_fee: Einmalige Honorargebühr (typisch bei Nettopolicen: 1.500€ - 5.000€)
            initial_investment: Einmaleinzahlung zu Beginn
            contribution_dynamics: Jährliche Beitragssteigerung (0.02 = 2%)
            inflation_rate: Inflationsrate (0.02 = 2%)
        """
        super().__init__(monthly_contribution, years, annual_return, tax_rate)
        self.deductible_percentage = deductible_percentage
        self.tax_rate_retirement = tax_rate_retirement
        self.effective_costs = effective_costs
        self.honorar_fee = honorar_fee
        self.initial_investment = initial_investment
        self.contribution_dynamics = contribution_dynamics
        self.inflation_rate = inflation_rate

    def calculate(self) -> InvestmentResult:
        """Berechnet den Endwert einer Basisrente nach Steuern (mit optionaler Dynamik)"""

        # Nettorendite nach Effektivkosten
        net_annual_return = self.annual_return - self.effective_costs

        # --- MIT BEITRAGSDYNAMIK ---
        if self.contribution_dynamics > 0:
            # Berechnung mit dynamischen Beiträgen
            final_value_gross, yearly_values, contract_contributions = calculate_with_contribution_dynamics(
                initial_monthly_contribution=self.monthly_contribution,
                annual_dynamics_rate=self.contribution_dynamics,
                years=self.years,
                annual_return=net_annual_return,
                initial_investment=self.initial_investment
            )
        else:
            # --- OHNE DYNAMIK (Original-Logik) ---
            # Berechne Endwert mit Zinseszins für monatliche Beiträge
            final_value_gross, yearly_values = self._compound_interest(
                self.monthly_contribution,
                net_annual_return,
                self.years
            )

            # Einmaleinzahlung mit Zinseszins
            if self.initial_investment > 0:
                # Wachstum der Einmaleinzahlung (nach Effektivkosten)
                initial_growth = self.initial_investment * ((1 + net_annual_return) ** self.years)
                final_value_gross += initial_growth

            # Vertragsbezogene Einzahlungen (Beiträge + ggf. Einmalbetrag)
            contract_contributions = self.monthly_contribution * 12 * self.years + self.initial_investment

        # Steuerersparnis während Ansparphase (nur auf Vertragsbeiträge)
        tax_savings = contract_contributions * self.deductible_percentage * self.tax_rate

        # Brutto-Einzahlungen (nur Vertragsbeiträge, OHNE separate Honorargebühr)
        gross_paid = contract_contributions

        # Gesamtkosten über Laufzeit (für Anzeigezwecke)
        # Die Effektivkosten sind bereits in der Rendite berücksichtigt!
        # Berechne hypothetisches Endvermögen OHNE Kosten
        final_without_costs, _ = self._compound_interest(
            self.monthly_contribution,
            self.annual_return,  # OHNE Abzug der Kosten
            self.years
        )

        # Einmaleinzahlung ohne Kosten
        if self.initial_investment > 0:
            initial_growth_no_costs = self.initial_investment * ((1 + self.annual_return) ** self.years)
            final_without_costs += initial_growth_no_costs

        # Der Unterschied ist ca. was die Kosten "gekostet" haben
        total_costs = final_without_costs - final_value_gross + self.honorar_fee

        # Bei Auszahlung: Nachgelagerte Besteuerung
        # Vereinfachung: Wir nehmen an, dass der gesamte Wert versteuert wird
        # In Realität würde nur die Rente besteuert
        tax_on_payout = final_value_gross * self.tax_rate_retirement

        # Endwert nach Steuern + Steuerersparnis während Ansparphase
        # Die Steuerersparnis ist Geld, das man zurückbekommt und zur Verfügung hat
        final_value_after_tax = final_value_gross - tax_on_payout + tax_savings

        # Netto-Eigeninvestition: Was wirklich aus der Tasche kam
        # Eingezahlte Beiträge - Steuererstattung
        net_investment_amount = contract_contributions - tax_savings

        return InvestmentResult(
            name="Basisrente (Rürup)",
            total_paid=net_investment_amount,  # Nach Steuerersparnis (was wirklich aus Tasche kam)
            total_value=final_value_after_tax,
            net_return=net_annual_return,
            tax_benefit=tax_savings,  # Gesamt (hier nur Steuern, keine Zulagen)
            yearly_values=yearly_values,
            gross_paid=gross_paid,
            state_allowances=0.0,  # Basisrente hat keine Zulagen
            tax_savings=tax_savings,
            total_costs=total_costs,
            gross_return=self.annual_return,  # Bruttorendite vor Kosten
            gross_value=final_value_gross  # Endwert VOR Steuern
        )
