"""
Vergleichsmodul für verschiedene Altersvorsorge-Produkte
"""
from typing import List
from .base_calculator import InvestmentResult


class Comparison:
    """Vergleicht mehrere Altersvorsorge-Produkte"""

    def __init__(self, results: List[InvestmentResult]):
        """
        Args:
            results: Liste von InvestmentResult Objekten
        """
        self.results = sorted(results, key=lambda x: x.total_value, reverse=True)

    def print_summary(self):
        """Gibt eine formatierte Zusammenfassung aus"""
        print("\n" + "=" * 80)
        print("VERGLEICH ALTERSVORSORGE-PRODUKTE")
        print("=" * 80 + "\n")

        for i, result in enumerate(self.results, 1):
            print(f"{i}. {result.name}")
            print("-" * 80)
            print(f"   Eigene Einzahlungen:     {result.total_paid:>15,.2f} €")

            if result.tax_benefit > 0:
                print(f"   Steuervorteile/Zulagen:  {result.tax_benefit:>15,.2f} €")
                print(f"   Effektive Kosten:        {result.total_paid - result.tax_benefit:>15,.2f} €")

            print(f"   Endwert (nach Steuern):  {result.total_value:>15,.2f} €")
            print(f"   Gewinn:                  {result.profit:>15,.2f} €")
            print(f"   Rendite:                 {result.return_percentage:>15,.2f} %")
            print(f"   Jährliche Nettorendite:  {result.net_return * 100:>15,.2f} %")
            print()

        # Vergleich zum Besten
        best = self.results[0]
        print("\n" + "=" * 80)
        print("VERGLEICH ZUM BESTEN PRODUKT")
        print("=" * 80 + "\n")

        for result in self.results[1:]:
            difference = best.total_value - result.total_value
            percentage = (difference / best.total_value) * 100
            print(f"{result.name}:")
            print(f"   Differenz zu {best.name}: -{difference:,.2f} € ({percentage:.2f}%)")
            print()

    def print_yearly_comparison(self):
        """Gibt einen jahresweisen Vergleich aus"""
        print("\n" + "=" * 80)
        print("ENTWICKLUNG ÜBER DIE JAHRE")
        print("=" * 80 + "\n")

        # Header
        print(f"{'Jahr':<6}", end="")
        for result in self.results:
            print(f"{result.name[:20]:>22}", end="")
        print("\n" + "-" * 80)

        # Finde maximale Anzahl Jahre
        max_years = max(len(r.yearly_values) for r in self.results)

        # Ausgabe für jedes Jahr
        for year_idx in range(max_years):
            print(f"{year_idx + 1:<6}", end="")
            for result in self.results:
                if year_idx < len(result.yearly_values):
                    _, value = result.yearly_values[year_idx]
                    print(f"{value:>20,.2f} €", end="  ")
                else:
                    print(f"{'':>22}", end="")
            print()

    def get_recommendation(self) -> str:
        """Gibt eine Empfehlung basierend auf den Ergebnissen"""
        best = self.results[0]

        recommendation = f"\n{'=' * 80}\n"
        recommendation += "EMPFEHLUNG\n"
        recommendation += f"{'=' * 80}\n\n"

        recommendation += f"Basierend auf den berechneten Werten bietet {best.name} den höchsten "
        recommendation += f"Endwert von {best.total_value:,.2f} €.\n\n"

        # Zusätzliche Hinweise
        recommendation += "WICHTIGE HINWEISE:\n"
        recommendation += "- Diese Berechnung ist eine Vereinfachung und ersetzt keine Beratung\n"
        recommendation += "- Flexibilität: ETFs können jederzeit verkauft werden, Riester/Rürup nicht\n"
        recommendation += "- Garantien: Riester garantiert Kapitalerhalt, ETFs unterliegen Schwankungen\n"
        recommendation += "- Persönliche Situation: Steuervorteile variieren je nach Einkommen\n"
        recommendation += "- Inflation wurde nicht berücksichtigt\n"

        return recommendation
