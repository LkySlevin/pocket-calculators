"""
Unit Tests für die Calculator-Module
"""
import unittest
import sys
import os

# Füge das Parent-Verzeichnis zum Python-Path hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculators.etf_calculator import ETFCalculator
from calculators.basisrente_calculator import BasisrenteCalculator
from calculators.riester_calculator import RiesterCalculator
from calculators.privatrente_calculator import PrivatrenteCalculator
from calculators.dynamics import (
    calculate_with_contribution_dynamics,
    adjust_for_inflation,
    calculate_real_return
)
from calculators.withdrawal_strategy import (
    four_percent_rule,
    dynamic_percentage_withdrawal,
    fixed_monthly_pension
)


class TestETFCalculator(unittest.TestCase):
    """Tests für ETF-Sparplan Calculator"""

    def test_basic_calculation(self):
        """Test grundlegende Berechnung"""
        calc = ETFCalculator(
            monthly_contribution=100,
            years=10,
            annual_return=0.07,
            tax_rate=0.42
        )
        result = calc.calculate()

        self.assertEqual(result.name, "ETF-Sparplan (privat)")
        self.assertEqual(result.total_paid, 12000)  # 100 * 12 * 10
        self.assertGreater(result.total_value, result.total_paid)
        self.assertGreater(result.profit, 0)

    def test_zero_contribution(self):
        """Test mit 0 Euro Beitrag"""
        calc = ETFCalculator(
            monthly_contribution=0,
            years=10,
            annual_return=0.07,
            tax_rate=0.42
        )
        result = calc.calculate()

        self.assertEqual(result.total_paid, 0)
        # Bei 0 Beitrag können Gebühren zu negativem Wert führen
        self.assertLessEqual(result.total_value, 0)


class TestBasisrenteCalculator(unittest.TestCase):
    """Tests für Basisrente Calculator"""

    def test_tax_benefit(self):
        """Test Steuervorteile"""
        calc = BasisrenteCalculator(
            monthly_contribution=100,
            years=10,
            annual_return=0.04,
            tax_rate=0.42,
            deductible_percentage=1.0
        )
        result = calc.calculate()

        # Steuerersparnis sollte vorhanden sein
        self.assertGreater(result.tax_benefit, 0)
        # Effektive Kosten sollten niedriger sein als Einzahlungen
        expected_total = 100 * 12 * 10
        self.assertLess(result.total_paid, expected_total)


class TestRiesterCalculator(unittest.TestCase):
    """Tests für Riester-Rente Calculator"""

    def test_basic_allowance(self):
        """Test Grundzulage"""
        calc = RiesterCalculator(
            monthly_contribution=100,
            years=10,
            annual_return=0.03,
            tax_rate=0.42,
            basic_allowance=175
        )
        result = calc.calculate()

        # Steuervorteile sollten mindestens die Grundzulage * Jahre sein
        expected_min_benefit = 175 * 10
        self.assertGreaterEqual(result.tax_benefit, expected_min_benefit)

    def test_children_allowance(self):
        """Test Kinderzulage"""
        calc_no_children = RiesterCalculator(
            monthly_contribution=100,
            years=10,
            children_allowance=0
        )
        result_no_children = calc_no_children.calculate()

        calc_with_children = RiesterCalculator(
            monthly_contribution=100,
            years=10,
            children_allowance=600  # 2 Kinder
        )
        result_with_children = calc_with_children.calculate()

        # Mit Kindern sollten die Vorteile höher sein
        self.assertGreater(
            result_with_children.tax_benefit,
            result_no_children.tax_benefit
        )


class TestComparison(unittest.TestCase):
    """Tests für Vergleichsfunktionen"""

    def test_comparison_sorting(self):
        """Test ob Ergebnisse korrekt sortiert werden"""
        from calculators.comparison import Comparison

        etf = ETFCalculator(100, 10, 0.07, 0.42).calculate()
        basis = BasisrenteCalculator(100, 10, 0.04, 0.42).calculate()
        riester = RiesterCalculator(100, 10, 0.03, 0.42).calculate()

        comp = Comparison([riester, etf, basis])

        # Sollte nach total_value sortiert sein (absteigend)
        for i in range(len(comp.results) - 1):
            self.assertGreaterEqual(
                comp.results[i].total_value,
                comp.results[i + 1].total_value
            )


class TestPrivatrenteCalculator(unittest.TestCase):
    """Tests für Privatrente Calculator"""

    def test_basic_calculation(self):
        """Test grundlegende Berechnung"""
        calc = PrivatrenteCalculator(
            monthly_contribution=100,
            years=10,
            annual_return=0.05,
            tax_rate=0.42,
            retirement_age=67
        )
        result = calc.calculate()

        # Name kann "Privatrente (Verrentung)" oder "Privatrente (Einmalauszahlung)" sein
        self.assertIn("Privatrente", result.name)
        self.assertGreater(result.total_value, 0)
        self.assertGreater(result.total_paid, 0)


class TestDynamics(unittest.TestCase):
    """Tests für Dynamik-Berechnungen"""

    def test_contribution_dynamics(self):
        """Test Beitragsdynamik-Berechnung"""
        final_capital, yearly_values, total_paid = calculate_with_contribution_dynamics(
            initial_monthly_contribution=100,
            annual_dynamics_rate=0.02,  # 2% Steigerung
            years=10,
            annual_return=0.05,
            initial_investment=0
        )

        # Mit Dynamik sollte mehr eingezahlt werden als ohne
        static_total = 100 * 12 * 10
        self.assertGreater(total_paid, static_total)

        # Endkapital sollte positiv sein
        self.assertGreater(final_capital, 0)

        # Sollte 11 Werte haben (Jahr 0 bis Jahr 10)
        self.assertEqual(len(yearly_values), 11)

    def test_inflation_adjustment(self):
        """Test Inflationsanpassung"""
        nominal_values = [100000, 105000, 110250]
        inflation_rate = 0.02

        real_values = adjust_for_inflation(nominal_values, inflation_rate)

        # Reale Werte sollten kleiner oder gleich nominalen Werten sein
        for real, nominal in zip(real_values, nominal_values):
            self.assertLessEqual(real, nominal)

        # Erster Wert sollte gleich sein (Jahr 0)
        self.assertAlmostEqual(real_values[0], nominal_values[0], places=2)

    def test_real_return_calculation(self):
        """Test reale Rendite-Berechnung (Fisher-Gleichung)"""
        nominal_return = 0.07  # 7%
        inflation_rate = 0.02  # 2%

        real_return = calculate_real_return(nominal_return, inflation_rate)

        # Reale Rendite sollte ca. 4.9% sein
        self.assertAlmostEqual(real_return, 0.049, places=3)

        # Reale Rendite sollte kleiner als nominale sein
        self.assertLess(real_return, nominal_return)


class TestWithdrawalStrategies(unittest.TestCase):
    """Tests für Entnahmestrategien"""

    def test_four_percent_rule(self):
        """Test 4%-Regel"""
        result = four_percent_rule(
            initial_capital=500000,
            withdrawal_years=30,
            annual_return=0.05,
            annual_inflation=0.02,
            with_inflation_adjustment=True
        )

        # Sollte für 30 Jahre reichen
        self.assertEqual(result.capital_depleted_year, 0)
        self.assertEqual(result.success_rate, 1.0)

        # Durchschnittliche Entnahme sollte sinnvoll sein
        self.assertGreater(result.avg_monthly_withdrawal, 0)
        self.assertLess(result.avg_monthly_withdrawal, 5000)

    def test_dynamic_withdrawal(self):
        """Test dynamische Entnahme"""
        result = dynamic_percentage_withdrawal(
            initial_capital=500000,
            withdrawal_percentage=0.04,
            withdrawal_years=30,
            annual_return=0.05
        )

        # Kapital sollte nie aufgebraucht werden
        self.assertEqual(result.capital_depleted_year, 0)
        self.assertEqual(result.success_rate, 1.0)

        # Restkapital sollte positiv sein
        self.assertGreater(result.remaining_capital, 0)

    def test_fixed_pension(self):
        """Test feste monatliche Rente"""
        result = fixed_monthly_pension(
            initial_capital=500000,
            monthly_pension=2000,
            withdrawal_years=30,
            annual_return=0.04
        )

        # Durchschnittliche Entnahme sollte ca. 2000€ sein
        self.assertAlmostEqual(result.avg_monthly_withdrawal, 2000, places=0)

        # Sollte entweder reichen oder vorher aufgebraucht sein
        if result.capital_depleted_year > 0:
            self.assertLess(result.capital_depleted_year, 30)
        else:
            self.assertGreaterEqual(result.remaining_capital, 0)


class TestCalculatorsWithDynamics(unittest.TestCase):
    """Tests für Calculator mit Dynamik-Support"""

    def test_etf_with_dynamics(self):
        """Test ETF Calculator mit Beitragsdynamik"""
        calc_static = ETFCalculator(
            monthly_contribution=100,
            years=10,
            annual_return=0.07,
            tax_rate=0.42,
            contribution_dynamics=0.0
        )
        result_static = calc_static.calculate()

        calc_dynamic = ETFCalculator(
            monthly_contribution=100,
            years=10,
            annual_return=0.07,
            tax_rate=0.42,
            contribution_dynamics=0.02  # 2% Dynamik
        )
        result_dynamic = calc_dynamic.calculate()

        # Mit Dynamik sollte mehr eingezahlt werden
        self.assertGreater(result_dynamic.total_paid, result_static.total_paid)

        # Endwert sollte auch höher sein
        self.assertGreater(result_dynamic.total_value, result_static.total_value)

    def test_basisrente_with_dynamics(self):
        """Test Basisrente Calculator mit Dynamik"""
        calc_dynamic = BasisrenteCalculator(
            monthly_contribution=100,
            years=10,
            annual_return=0.05,
            tax_rate=0.42,
            contribution_dynamics=0.02
        )
        result = calc_dynamic.calculate()

        # Berechnung sollte funktionieren
        self.assertGreater(result.total_value, 0)
        self.assertGreater(result.tax_benefit, 0)


if __name__ == '__main__':
    unittest.main()
