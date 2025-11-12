"""
Privatrente (Private Rentenversicherung) Rechner
"""
from .base_calculator import BaseCalculator, InvestmentResult


class PrivatrenteCalculator(BaseCalculator):
    """
    Rechner für Privatrente (Private Rentenversicherung ohne staatliche Förderung)

    Berücksichtigt:
    - Keine steuerliche Absetzbarkeit während Ansparphase
    - Günstige Besteuerung bei Auszahlung (nur Ertragsanteil bzw. Halbeinkünfteverfahren)
    - Kapitalwahlrecht: Einmalauszahlung oder Verrentung
    - Kosten der Versicherung
    - Flexibilität ohne Förderung
    """

    # Ertragsanteil-Tabelle nach § 22 EStG (Alter bei Rentenbeginn -> Ertragsanteil in %)
    ERTRAGSANTEIL_TABLE = {
        50: 30, 51: 29, 52: 28, 53: 27, 54: 27,
        55: 26, 56: 25, 57: 25, 58: 24, 59: 23,
        60: 22, 61: 22, 62: 21, 63: 20, 64: 19,
        65: 18, 66: 18, 67: 17, 68: 16, 69: 16,
        70: 15
    }

    def __init__(
        self,
        monthly_contribution: float,
        years: int,
        annual_return: float = 0.05,  # Konservative Rendite (zwischen Riester und ETF)
        tax_rate: float = 0.42,
        tax_rate_retirement: float = 0.30,  # Persönlicher Steuersatz im Alter
        effective_costs: float = 0.018,  # 1.8% Effektivkosten pro Jahr
        honorar_fee: float = 0.0,  # Einmalige Honorargebühr (bei Nettopolicen)
        initial_investment: float = 0.0,  # Einmaleinzahlung zu Beginn
        payout_option: str = "annuity",  # "annuity" oder "lump_sum"
        retirement_age: int = 67  # Alter bei Rentenbeginn
    ):
        """
        Args:
            monthly_contribution: Monatlicher Sparbeitrag
            years: Anlagedauer in Jahren
            annual_return: Erwartete Bruttorendite (vor Kosten)
            tax_rate: Persönlicher Steuersatz während Ansparphase (für Vergleichszwecke)
            tax_rate_retirement: Persönlicher Steuersatz im Rentenalter
            effective_costs: Effektivkosten pro Jahr (beinhaltet Abschluss-, Verwaltungs- und laufende Kosten)
            honorar_fee: Einmalige Honorargebühr (typisch bei Nettopolicen: 1.500€ - 5.000€)
            initial_investment: Einmaleinzahlung zu Beginn
            payout_option: "annuity" (Verrentung) oder "lump_sum" (Einmalauszahlung)
            retirement_age: Alter bei Rentenbeginn (relevant für Ertragsanteil)
        """
        super().__init__(monthly_contribution, years, annual_return, tax_rate)
        self.tax_rate_retirement = tax_rate_retirement
        self.effective_costs = effective_costs
        self.honorar_fee = honorar_fee
        self.initial_investment = initial_investment
        self.payout_option = payout_option
        self.retirement_age = retirement_age

    def calculate(self) -> InvestmentResult:
        """Berechnet den Endwert einer Privatrente nach Steuern"""

        # Nettorendite nach Effektivkosten
        net_annual_return = self.annual_return - self.effective_costs

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

        # --- BESTEUERUNG BEI AUSZAHLUNG ---

        # Erträge (Gewinn)
        capital_gain = final_value_gross - contract_contributions

        if self.payout_option == "lump_sum":
            # Einmalauszahlung: Halbeinkünfteverfahren (nur 50% der Erträge steuerpflichtig)
            # Voraussetzung: 12 Jahre Laufzeit + Auszahlung ab 62 Jahren
            # Vereinfachung: Wir gehen davon aus, dass die Voraussetzungen erfüllt sind
            taxable_gain = capital_gain * 0.5  # Nur 50% der Erträge
            tax_on_payout = taxable_gain * self.tax_rate_retirement
        else:
            # Verrentung: Nur Ertragsanteil wird besteuert
            # Ertragsanteil hängt vom Alter bei Rentenbeginn ab
            ertragsanteil_percentage = self._get_ertragsanteil(self.retirement_age)

            # Der Ertragsanteil bezieht sich auf die gesamte Jahresrente
            # Vereinfachung: Wir besteuern den Ertragsanteil des Gesamtkapitals
            # (In Realität würde nur die jährliche Rente besteuert, aber für Vergleichszwecke
            # rechnen wir mit dem Barwert der Besteuerung)
            tax_on_payout = final_value_gross * (ertragsanteil_percentage / 100) * self.tax_rate_retirement

        # Endwert nach Steuern
        # Bei Privatrente gibt es KEINE Steuerersparnis während der Ansparphase
        final_value_after_tax = final_value_gross - tax_on_payout

        # Netto-Eigeninvestition: Was wirklich aus der Tasche kam
        # Bei Privatrente: Brutto = Netto (keine Förderung, keine Steuerersparnis)
        net_investment_amount = contract_contributions

        return InvestmentResult(
            name=f"Privatrente ({self._get_payout_name()})",
            total_paid=net_investment_amount,  # Keine Steuerersparnis (= Bruttobeiträge)
            total_value=final_value_after_tax,
            net_return=net_annual_return,
            tax_benefit=0,  # Keine Förderung während Ansparphase
            yearly_values=yearly_values,
            gross_paid=gross_paid,
            state_allowances=0.0,  # Keine Zulagen
            tax_savings=0.0,  # Keine Steuerersparnis während Ansparphase
            total_costs=total_costs,
            gross_return=self.annual_return,  # Bruttorendite vor Kosten
            gross_value=final_value_gross  # Endwert VOR Steuern
        )

    def _get_ertragsanteil(self, age: int) -> int:
        """
        Gibt den Ertragsanteil in % für ein bestimmtes Alter zurück.

        Args:
            age: Alter bei Rentenbeginn

        Returns:
            Ertragsanteil in Prozent
        """
        # Begrenze Alter auf Tabellenwerte
        if age < 50:
            return 30  # Höchster Wert
        elif age > 70:
            return 15  # Niedrigster Wert
        else:
            return self.ERTRAGSANTEIL_TABLE.get(age, 18)  # Default: 18% (Alter 65)

    def _get_payout_name(self) -> str:
        """Gibt einen lesbaren Namen für die Auszahlungsoption zurück."""
        if self.payout_option == "lump_sum":
            return "Einmalauszahlung"
        else:
            return "Verrentung"
