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
        self.assertEqual(result.total_value, 0)


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


if __name__ == '__main__':
    unittest.main()
