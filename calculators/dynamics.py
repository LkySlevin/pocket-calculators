"""
Dynamics Calculator - Berechnung von Beitragsdynamiken und Inflation

Dieses Modul implementiert:
1. Beitragsdynamik in der Ansparphase (1-5% jährliche Steigerung)
2. Rentendynamik in der Auszahlungsphase (1-3% jährliche Steigerung)
3. Inflationsanpassung (nominal vs. real)
"""

from typing import List, Tuple


def calculate_contributions_with_dynamics(
    initial_monthly_contribution: float,
    annual_dynamics_rate: float,
    years: int
) -> List[Tuple[int, float]]:
    """
    Berechnet die Beiträge mit jährlicher Dynamik.

    Args:
        initial_monthly_contribution: Anfänglicher monatlicher Beitrag
        annual_dynamics_rate: Jährliche Steigerungsrate (0.02 = 2%)
        years: Anzahl Jahre

    Returns:
        List von (Jahr, monatlicher_Beitrag) Tupeln
    """
    contributions = []

    for year in range(years):
        # Beitrag erhöht sich jedes Jahr
        yearly_contribution = initial_monthly_contribution * ((1 + annual_dynamics_rate) ** year)
        contributions.append((year + 1, yearly_contribution))

    return contributions


def calculate_with_contribution_dynamics(
    initial_monthly_contribution: float,
    annual_dynamics_rate: float,
    years: int,
    annual_return: float,
    initial_investment: float = 0
) -> Tuple[float, List[float], float]:
    """
    Berechnet Endkapital mit dynamischen Beiträgen.

    Args:
        initial_monthly_contribution: Anfänglicher monatlicher Beitrag
        annual_dynamics_rate: Jährliche Beitragssteigerung (0.02 = 2%)
        years: Anlagedauer in Jahren
        annual_return: Jährliche Rendite (0.05 = 5%)
        initial_investment: Einmalzahlung zu Beginn

    Returns:
        Tuple (Endkapital, yearly_values, total_contributions)
    """
    monthly_rate = annual_return / 12
    total_capital = initial_investment
    yearly_values = [initial_investment]
    total_contributions = initial_investment

    current_monthly_contribution = initial_monthly_contribution

    for year in range(1, years + 1):
        # Beiträge für dieses Jahr
        for month in range(12):
            total_capital = total_capital * (1 + monthly_rate) + current_monthly_contribution
            total_contributions += current_monthly_contribution

        yearly_values.append(total_capital)

        # Dynamik: Beitrag erhöhen für nächstes Jahr
        current_monthly_contribution *= (1 + annual_dynamics_rate)

    return total_capital, yearly_values, total_contributions


def adjust_for_inflation(
    nominal_values: List[float],
    annual_inflation_rate: float
) -> List[float]:
    """
    Passt nominale Werte an Inflation an (Kaufkraft).

    Args:
        nominal_values: Nominale Werte (Liste)
        annual_inflation_rate: Jährliche Inflationsrate (0.02 = 2%)

    Returns:
        Liste der inflationsbereinigten (realen) Werte
    """
    real_values = []

    for year, nominal_value in enumerate(nominal_values):
        # Kaufkraft sinkt jedes Jahr
        real_value = nominal_value / ((1 + annual_inflation_rate) ** year)
        real_values.append(real_value)

    return real_values


def calculate_real_return(
    nominal_return: float,
    inflation_rate: float
) -> float:
    """
    Berechnet reale Rendite aus nominaler Rendite und Inflation (Fisher-Gleichung).

    real_return ≈ nominal_return - inflation_rate (vereinfacht)
    Exakt: (1 + real) = (1 + nominal) / (1 + inflation)

    Args:
        nominal_return: Nominale Rendite (0.07 = 7%)
        inflation_rate: Inflationsrate (0.02 = 2%)

    Returns:
        Reale Rendite
    """
    real_return = ((1 + nominal_return) / (1 + inflation_rate)) - 1
    return real_return


def calculate_pension_with_dynamics(
    initial_monthly_pension: float,
    annual_dynamics_rate: float,
    years: int,
    annual_inflation_rate: float = 0.02
) -> Tuple[List[Tuple[int, float, float]], float]:
    """
    Berechnet Rentenzahlungen mit Dynamik und Inflation.

    Args:
        initial_monthly_pension: Anfängliche monatliche Rente
        annual_dynamics_rate: Jährliche Rentensteigerung (0.01 = 1%)
        years: Anzahl Jahre der Rentenzahlung
        annual_inflation_rate: Inflationsrate (0.02 = 2%)

    Returns:
        Tuple (List[(Jahr, nominale_Rente, reale_Rente)], durchschnittliche_reale_Rente)
    """
    pension_values = []
    current_monthly_pension = initial_monthly_pension
    total_real_pension = 0

    for year in range(1, years + 1):
        # Nominale Rente (mit Dynamik)
        nominal_pension = current_monthly_pension

        # Reale Rente (Kaufkraft)
        real_pension = nominal_pension / ((1 + annual_inflation_rate) ** year)

        pension_values.append((year, nominal_pension, real_pension))
        total_real_pension += real_pension * 12  # Jahreswert

        # Dynamik: Rente erhöhen für nächstes Jahr
        current_monthly_pension *= (1 + annual_dynamics_rate)

    # Durchschnittliche reale Rente
    avg_real_pension = total_real_pension / (years * 12)

    return pension_values, avg_real_pension


def calculate_required_capital_with_dynamics(
    initial_monthly_pension: float,
    annual_pension_dynamics: float,
    withdrawal_years: int,
    annual_return: float,
    annual_inflation_rate: float = 0.02
) -> float:
    """
    Berechnet benötigtes Kapital für dynamische Rente.

    Dies ist komplexer als die einfache 4%-Regel, da:
    1. Die Rente jährlich steigt (Dynamik)
    2. Das verbleibende Kapital weiter Rendite erwirtschaftet
    3. Inflation berücksichtigt werden muss

    Args:
        initial_monthly_pension: Anfängliche monatliche Rente
        annual_pension_dynamics: Jährliche Rentensteigerung (0.01 = 1%)
        withdrawal_years: Erwartete Jahre der Rentenzahlung (z.B. 25 Jahre)
        annual_return: Erwartete Rendite des Restkapitals (0.04 = 4%)
        annual_inflation_rate: Inflationsrate (0.02 = 2%)

    Returns:
        Benötigtes Kapital zu Rentenbeginn
    """
    # Barwert aller zukünftigen Rentenzahlungen
    present_value = 0
    current_monthly_pension = initial_monthly_pension
    monthly_return = annual_return / 12

    for year in range(1, withdrawal_years + 1):
        # Jahressumme der Rente
        yearly_pension = current_monthly_pension * 12

        # Barwert dieser Zahlung (abgezinst)
        discount_factor = (1 + annual_return) ** year
        present_value += yearly_pension / discount_factor

        # Dynamik: Rente erhöhen für nächstes Jahr
        current_monthly_pension *= (1 + annual_pension_dynamics)

    return present_value


# Beispiel-Nutzung und Tests
if __name__ == "__main__":
    print("=== Test: Beitragsdynamik ===")
    contributions = calculate_contributions_with_dynamics(
        initial_monthly_contribution=500,
        annual_dynamics_rate=0.02,  # 2% Steigerung
        years=10
    )
    for year, contrib in contributions:
        print(f"Jahr {year}: {contrib:.2f} €/Monat")

    print("\n=== Test: Kapital mit Dynamik ===")
    final_capital, yearly_values, total_contrib = calculate_with_contribution_dynamics(
        initial_monthly_contribution=500,
        annual_dynamics_rate=0.02,
        years=30,
        annual_return=0.05,
        initial_investment=10000
    )
    print(f"Endkapital: {final_capital:,.2f} €")
    print(f"Eingezahlt gesamt: {total_contrib:,.2f} €")
    print(f"Gewinn: {final_capital - total_contrib:,.2f} €")

    print("\n=== Test: Inflation ===")
    nominal_values = [100000, 105000, 110250, 115763]
    real_values = adjust_for_inflation(nominal_values, 0.02)
    for i, (nom, real) in enumerate(zip(nominal_values, real_values)):
        print(f"Jahr {i}: Nominal {nom:,.0f} € → Real {real:,.0f} € (Kaufkraft)")

    print("\n=== Test: Reale Rendite ===")
    real_return = calculate_real_return(0.07, 0.02)
    print(f"Nominale Rendite 7%, Inflation 2% → Reale Rendite: {real_return*100:.2f}%")

    print("\n=== Test: Rentendynamik ===")
    pension_values, avg_real = calculate_pension_with_dynamics(
        initial_monthly_pension=2000,
        annual_dynamics_rate=0.01,  # 1% Steigerung
        years=25,
        annual_inflation_rate=0.02
    )
    print(f"Anfangsrente: 2.000 €/Monat")
    print(f"Jahr 1: Nominal {pension_values[0][1]:.2f} €, Real {pension_values[0][2]:.2f} €")
    print(f"Jahr 10: Nominal {pension_values[9][1]:.2f} €, Real {pension_values[9][2]:.2f} €")
    print(f"Jahr 25: Nominal {pension_values[24][1]:.2f} €, Real {pension_values[24][2]:.2f} €")
    print(f"Durchschnittliche reale Rente: {avg_real:.2f} €/Monat")

    print("\n=== Test: Benötigtes Kapital für dynamische Rente ===")
    required_capital = calculate_required_capital_with_dynamics(
        initial_monthly_pension=2000,
        annual_pension_dynamics=0.01,
        withdrawal_years=25,
        annual_return=0.04
    )
    print(f"Benötigtes Kapital: {required_capital:,.2f} €")
    print(f"Vergleich 4%-Regel (statisch): {2000 * 12 * 25:,.2f} €")
