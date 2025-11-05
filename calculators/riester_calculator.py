"""
Riester-Rente Rechner
"""
from .base_calculator import BaseCalculator, InvestmentResult


class RiesterCalculator(BaseCalculator):
    """
    Rechner für Riester-Rente

    Berücksichtigt:
    - Staatliche Zulagen (Grundzulage + Kinderzulagen)
    - Steuerliche Absetzbarkeit (Sonderausgabenabzug bis 2.100€/Jahr)
    - Nachgelagerte Besteuerung bei Auszahlung
    - Garantie des eingezahlten Kapitals (reduziert Rendite)
    - Höhere Kosten durch Versicherungsprodukt
    """

    def __init__(
        self,
        monthly_contribution: float,
        years: int,
        annual_return: float = 0.03,  # Konservativ wegen Garantie
        tax_rate: float = 0.42,
        tax_rate_retirement: float = 0.30,
        basic_allowance: float = 175,  # Grundzulage pro Jahr
        children_allowance: float = 0,  # Kinderzulage pro Jahr
        effective_costs: float = 0.02,  # 2% Effektivkosten pro Jahr (inkl. aller Kosten)
        max_deductible: float = 2100,  # Maximaler Sonderausgabenabzug
        lump_sum_percentage: float = 0.0  # Prozent Einmalauszahlung (max 30%)
    ):
        """
        Args:
            monthly_contribution: Monatlicher Sparbeitrag
            years: Anlagedauer in Jahren
            annual_return: Erwartete Bruttorendite
            tax_rate: Persönlicher Steuersatz während Ansparphase
            tax_rate_retirement: Steuersatz im Rentenalter
            basic_allowance: Grundzulage pro Jahr (175€)
            children_allowance: Kinderzulage pro Jahr (300€ pro Kind ab 2008)
            effective_costs: Effektivkosten pro Jahr (beinhaltet Abschluss-, Verwaltungs- und laufende Kosten)
            max_deductible: Maximaler Sonderausgabenabzug
            lump_sum_percentage: Prozent Einmalauszahlung bei Rentenbeginn (max 30%)
        """
        super().__init__(monthly_contribution, years, annual_return, tax_rate)
        self.tax_rate_retirement = tax_rate_retirement
        self.basic_allowance = basic_allowance
        self.children_allowance = children_allowance
        self.effective_costs = effective_costs
        self.max_deductible = max_deductible
        self.lump_sum_percentage = min(lump_sum_percentage, 30.0) / 100  # Max 30%

    def calculate(self) -> InvestmentResult:
        """Berechnet den Endwert einer Riester-Rente nach Steuern"""

        # Nettorendite nach Effektivkosten
        net_annual_return = self.annual_return - self.effective_costs

        # WICHTIG: Rendite darf nicht negativ sein
        if net_annual_return < 0:
            net_annual_return = 0.001  # Minimal positive Rendite

        # Jährliche Einzahlung
        yearly_contribution = self.monthly_contribution * 12

        # Staatliche Zulagen pro Jahr
        yearly_allowance = self.basic_allowance + self.children_allowance

        # Steuerersparnis durch Sonderausgabenabzug (Günstigerprüfung)
        deductible_amount = min(yearly_contribution, self.max_deductible)
        yearly_tax_benefit = deductible_amount * self.tax_rate

        # Günstigerprüfung: Das Finanzamt gewährt das Bessere
        # (entweder Zulage oder Steuerersparnis minus Zulage)
        additional_tax_benefit = max(0, yearly_tax_benefit - yearly_allowance)

        # Gesamte staatliche Förderung pro Jahr
        total_yearly_benefit = yearly_allowance + additional_tax_benefit

        # --- Berechnung des Endwerts ---
        # Wir berechnen das Wachstum nur auf die eigenen Einzahlungen + Zulagen
        # Die Steuerersparnis fließt sofort zurück (wird nicht angelegt)

        # Monatlicher Beitrag inkl. Zulagen (für Zinseszins)
        monthly_contribution_with_allowance = (yearly_contribution + yearly_allowance) / 12

        # Berechne Endwert mit Zinseszins
        final_value_gross, yearly_values = self._compound_interest(
            monthly_contribution_with_allowance,
            net_annual_return,
            self.years
        )

        # Eigene Einzahlungen
        gross_paid = yearly_contribution * self.years

        # Staatliche Zulagen gesamt
        total_allowances = yearly_allowance * self.years

        # Steuerersparnis gesamt (zusätzlich zu Zulagen)
        total_additional_tax = additional_tax_benefit * self.years

        # Gesamtkosten über Laufzeit (für Anzeigezwecke)
        # Die Effektivkosten sind bereits in der Rendite berücksichtigt!
        # Hier berechnen wir nur einen Schätzwert, was die Kosten "gekostet haben"
        # Wir müssen dazu berechnen, wie viel MEHR Vermögen ohne Kosten da wäre

        # Berechne hypothetisches Endvermögen OHNE Kosten
        final_without_costs, _ = self._compound_interest(
            monthly_contribution_with_allowance,
            self.annual_return,  # OHNE Abzug der Kosten
            self.years
        )

        # Der Unterschied ist ca. was die Kosten "gekostet" haben
        total_costs = final_without_costs - final_value_gross

        # Bei Auszahlung: Nachgelagerte Besteuerung des gesamten Kapitals
        tax_on_payout = final_value_gross * self.tax_rate_retirement

        # Endwert nach Steuern + zusätzliche Steuerersparnis während Ansparphase
        # Die zusätzliche Steuerersparnis ist Geld, das man zurückbekommt und zur Verfügung hat
        # Zulagen sind bereits im final_value_gross enthalten (wurden mitangelegt)
        final_value_after_tax = final_value_gross - tax_on_payout + total_additional_tax

        # Gesamte steuerliche Vorteile (Zulagen + Steuerersparnis)
        total_tax_benefit = total_allowances + total_additional_tax

        # Netto-Eigeninvestition: Was wirklich aus der Tasche kam
        # Eingezahlte Beiträge - Steuererstattung (Zulagen haben damit nichts zu tun!)
        net_investment_amount = gross_paid - total_additional_tax

        return InvestmentResult(
            name="Riester-Rente",
            total_paid=net_investment_amount,  # Was wirklich aus der Tasche kam
            total_value=final_value_after_tax,
            net_return=net_annual_return,
            tax_benefit=total_tax_benefit,  # Zulagen + Steuervorteile
            yearly_values=yearly_values,
            gross_paid=gross_paid,
            state_allowances=total_allowances,
            tax_savings=total_additional_tax,
            total_costs=total_costs,
            gross_return=self.annual_return,  # Bruttorendite vor Kosten
            gross_value=final_value_gross  # Endwert VOR Steuern
        )
