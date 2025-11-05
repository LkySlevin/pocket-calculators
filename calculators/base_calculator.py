"""
Basis-Klasse für alle Altersvorsorge-Rechner
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class InvestmentResult:
    """Ergebnis einer Altersvorsorge-Berechnung"""
    name: str
    total_paid: float  # Gesamte Einzahlungen (netto, nach Förderung)
    total_value: float  # Endwert (nach Steuern)
    net_return: float  # Nettorendite nach Kosten (p.a.)
    tax_benefit: float  # Steuervorteile während Ansparphase (Gesamt)
    yearly_values: List[Tuple[int, float]]  # [(Jahr, Wert), ...]

    # Neue detaillierte Felder
    gross_paid: float = 0.0  # Brutto-Einzahlungen (vor Förderung)
    state_allowances: float = 0.0  # Staatliche Zulagen (nur Riester)
    tax_savings: float = 0.0  # Eingesparte Steuern (Riester + Basisrente)
    total_costs: float = 0.0  # Gesamtkosten über Laufzeit
    gross_return: float = 0.0  # Bruttorendite vor Kosten (p.a.)
    gross_value: float = 0.0  # Endwert VOR Steuern (brutto)

    @property
    def profit(self) -> float:
        """Gewinn = Endwert - Einzahlungen"""
        return self.total_value - self.total_paid

    @property
    def return_percentage(self) -> float:
        """Rendite in Prozent"""
        if self.total_paid == 0:
            return 0
        return (self.profit / self.total_paid) * 100

    @property
    def net_investment(self) -> float:
        """Netto-Eigeninvestition = Brutto - Zulagen - Steuerersparnis"""
        return self.gross_paid - self.state_allowances - self.tax_savings


class BaseCalculator(ABC):
    """Abstrakte Basisklasse für Altersvorsorge-Rechner"""

    def __init__(
        self,
        monthly_contribution: float,
        years: int,
        annual_return: float,
        tax_rate: float
    ):
        """
        Args:
            monthly_contribution: Monatlicher Sparbeitrag
            years: Anlagedauer in Jahren
            annual_return: Erwartete jährliche Rendite (als Dezimalzahl, z.B. 0.07 für 7%)
            tax_rate: Persönlicher Steuersatz (als Dezimalzahl, z.B. 0.42 für 42%)
        """
        self.monthly_contribution = monthly_contribution
        self.years = years
        self.annual_return = annual_return
        self.tax_rate = tax_rate

    @abstractmethod
    def calculate(self) -> InvestmentResult:
        """Berechnet das Endergebnis der Altersvorsorge"""
        pass

    def _compound_interest(
        self,
        monthly_payment: float,
        annual_rate: float,
        years: int
    ) -> Tuple[float, List[Tuple[int, float]]]:
        """
        Berechnet den Endwert bei monatlichen Einzahlungen mit Zinseszins

        Returns:
            Tuple aus (Endwert, Liste der jährlichen Werte)
        """
        monthly_rate = annual_rate / 12
        months = years * 12

        balance = 0
        yearly_values = []

        for month in range(1, months + 1):
            balance = balance * (1 + monthly_rate) + monthly_payment

            # Speichere Wert am Jahresende
            if month % 12 == 0:
                year = month // 12
                yearly_values.append((year, balance))

        return balance, yearly_values
