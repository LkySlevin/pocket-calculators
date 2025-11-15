"""
Withdrawal Strategy Calculator - Entnahmestrategien für die Rentenphase

Implementiert verschiedene Strategien zur Kapitalentnahme im Ruhestand:
1. 4%-Regel (Trinity Study) - Konstante Entnahmerate
2. Dynamische Entnahme - Prozentual vom Restkapital
3. Feste monatliche Rente - Garantierte Zahlung
4. Hybrid - Rente + Kapitalreserve
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class WithdrawalResult:
    """Ergebnis einer Entnahmestrategie"""
    strategy_name: str
    initial_capital: float
    total_withdrawals: float  # Summe aller Entnahmen
    remaining_capital: float  # Verbleibendes Kapital am Ende
    yearly_withdrawals: List[Tuple[int, float, float]]  # (Jahr, Entnahme, Restkapital)
    avg_monthly_withdrawal: float
    capital_depleted_year: int  # Jahr in dem Kapital aufgebraucht (0 = nie)
    success_rate: float  # 1.0 = Kapital reicht, <1.0 = vorzeitig aufgebraucht


def four_percent_rule(
    initial_capital: float,
    withdrawal_years: int,
    annual_return: float = 0.04,
    annual_inflation: float = 0.02,
    with_inflation_adjustment: bool = True
) -> WithdrawalResult:
    """
    4%-Regel (Trinity Study)

    Entnahme 4% des Anfangskapitals, inflationsangepasst.
    Gilt als sicher für 30 Jahre bei 60/40 Aktien/Anleihen Portfolio.

    Args:
        initial_capital: Startkapital
        withdrawal_years: Entnahmedauer in Jahren
        annual_return: Erwartete jährliche Rendite
        annual_inflation: Inflationsrate
        with_inflation_adjustment: Entnahmen an Inflation anpassen

    Returns:
        WithdrawalResult
    """
    yearly_withdrawals = []
    current_capital = initial_capital
    annual_withdrawal = initial_capital * 0.04
    total_withdrawals = 0
    capital_depleted_year = 0

    for year in range(1, withdrawal_years + 1):
        # Inflationsanpassung der Entnahme
        if with_inflation_adjustment and year > 1:
            annual_withdrawal *= (1 + annual_inflation)

        # Prüfen ob genug Kapital vorhanden
        if current_capital <= 0:
            if capital_depleted_year == 0:
                capital_depleted_year = year - 1
            yearly_withdrawals.append((year, 0, 0))
            continue

        # Entnahme (max. verfügbares Kapital)
        actual_withdrawal = min(annual_withdrawal, current_capital)
        current_capital -= actual_withdrawal
        total_withdrawals += actual_withdrawal

        # Rendite auf Restkapital
        current_capital *= (1 + annual_return)

        yearly_withdrawals.append((year, actual_withdrawal, current_capital))

    # Success Rate berechnen
    if capital_depleted_year == 0:
        success_rate = 1.0
    else:
        success_rate = capital_depleted_year / withdrawal_years

    return WithdrawalResult(
        strategy_name="4%-Regel (Trinity Study)",
        initial_capital=initial_capital,
        total_withdrawals=total_withdrawals,
        remaining_capital=max(0, current_capital),
        yearly_withdrawals=yearly_withdrawals,
        avg_monthly_withdrawal=(total_withdrawals / withdrawal_years) / 12,
        capital_depleted_year=capital_depleted_year,
        success_rate=success_rate
    )


def dynamic_percentage_withdrawal(
    initial_capital: float,
    withdrawal_percentage: float,
    withdrawal_years: int,
    annual_return: float = 0.04
) -> WithdrawalResult:
    """
    Dynamische Entnahme - Prozentsatz vom aktuellen Kapital

    Entnahme X% des jeweils aktuellen Kapitals.
    - Vorteil: Kapital wird nie aufgebraucht
    - Nachteil: Entnahmen schwanken stark

    Args:
        initial_capital: Startkapital
        withdrawal_percentage: Jährliche Entnahmerate (0.04 = 4%)
        withdrawal_years: Entnahmedauer in Jahren
        annual_return: Erwartete jährliche Rendite

    Returns:
        WithdrawalResult
    """
    yearly_withdrawals = []
    current_capital = initial_capital
    total_withdrawals = 0

    for year in range(1, withdrawal_years + 1):
        # Entnahme X% vom aktuellen Kapital
        annual_withdrawal = current_capital * withdrawal_percentage
        current_capital -= annual_withdrawal
        total_withdrawals += annual_withdrawal

        # Rendite auf Restkapital
        current_capital *= (1 + annual_return)

        yearly_withdrawals.append((year, annual_withdrawal, current_capital))

    return WithdrawalResult(
        strategy_name=f"Dynamische Entnahme ({withdrawal_percentage*100:.1f}%)",
        initial_capital=initial_capital,
        total_withdrawals=total_withdrawals,
        remaining_capital=current_capital,
        yearly_withdrawals=yearly_withdrawals,
        avg_monthly_withdrawal=(total_withdrawals / withdrawal_years) / 12,
        capital_depleted_year=0,  # Wird nie aufgebraucht
        success_rate=1.0
    )


def fixed_monthly_pension(
    initial_capital: float,
    monthly_pension: float,
    withdrawal_years: int,
    annual_return: float = 0.04
) -> WithdrawalResult:
    """
    Feste monatliche Rente

    Entnahme eines festen monatlichen Betrags bis Kapital aufgebraucht.

    Args:
        initial_capital: Startkapital
        monthly_pension: Gewünschte monatliche Rente
        withdrawal_years: Geplante Entnahmedauer in Jahren
        annual_return: Erwartete jährliche Rendite

    Returns:
        WithdrawalResult
    """
    yearly_withdrawals = []
    current_capital = initial_capital
    annual_withdrawal = monthly_pension * 12
    total_withdrawals = 0
    capital_depleted_year = 0

    for year in range(1, withdrawal_years + 1):
        # Monatliche Entnahmen simulieren
        year_withdrawal = 0
        for month in range(12):
            if current_capital <= 0:
                if capital_depleted_year == 0:
                    capital_depleted_year = year
                break

            # Entnahme
            actual_monthly_withdrawal = min(monthly_pension, current_capital)
            current_capital -= actual_monthly_withdrawal
            year_withdrawal += actual_monthly_withdrawal

            # Monatliche Rendite
            current_capital *= (1 + annual_return / 12)

        total_withdrawals += year_withdrawal
        yearly_withdrawals.append((year, year_withdrawal, current_capital))

        if current_capital <= 0:
            break

    # Success Rate berechnen
    if capital_depleted_year == 0:
        success_rate = 1.0
    else:
        success_rate = capital_depleted_year / withdrawal_years

    return WithdrawalResult(
        strategy_name=f"Feste Rente ({monthly_pension:,.0f}€/Monat)",
        initial_capital=initial_capital,
        total_withdrawals=total_withdrawals,
        remaining_capital=max(0, current_capital),
        yearly_withdrawals=yearly_withdrawals,
        avg_monthly_withdrawal=monthly_pension,
        capital_depleted_year=capital_depleted_year,
        success_rate=success_rate
    )


def hybrid_withdrawal(
    initial_capital: float,
    fixed_monthly_pension: float,
    capital_reserve_percentage: float,
    withdrawal_years: int,
    annual_return: float = 0.04
) -> WithdrawalResult:
    """
    Hybrid-Strategie: Feste Rente + Kapitalreserve

    - X% des Kapitals wird als Reserve behalten (Erbe, Notfälle)
    - Rest wird für feste Rente verwendet

    Args:
        initial_capital: Startkapital
        fixed_monthly_pension: Gewünschte monatliche Rente
        capital_reserve_percentage: Prozent als Reserve (0.2 = 20%)
        withdrawal_years: Geplante Entnahmedauer in Jahren
        annual_return: Erwartete jährliche Rendite

    Returns:
        WithdrawalResult
    """
    # Kapital aufteilen
    reserve_capital = initial_capital * capital_reserve_percentage
    withdrawal_capital = initial_capital - reserve_capital

    # Feste Rente aus Entnahmekapital
    result = fixed_monthly_pension(
        initial_capital=withdrawal_capital,
        monthly_pension=fixed_monthly_pension,
        withdrawal_years=withdrawal_years,
        annual_return=annual_return
    )

    # Reserve wird verzinst (nicht entnommen)
    final_reserve = reserve_capital * ((1 + annual_return) ** withdrawal_years)

    # Ergebnis anpassen
    result.strategy_name = f"Hybrid ({capital_reserve_percentage*100:.0f}% Reserve)"
    result.initial_capital = initial_capital
    result.remaining_capital += final_reserve

    # Reserve zu yearly_withdrawals hinzufügen
    updated_withdrawals = []
    for year, withdrawal, capital in result.yearly_withdrawals:
        reserve_at_year = reserve_capital * ((1 + annual_return) ** year)
        total_capital = capital + reserve_at_year
        updated_withdrawals.append((year, withdrawal, total_capital))

    result.yearly_withdrawals = updated_withdrawals

    return result


def calculate_safe_withdrawal_rate(
    initial_capital: float,
    desired_monthly_pension: float,
    withdrawal_years: int,
    annual_return: float = 0.04,
    annual_inflation: float = 0.02
) -> Dict[str, float]:
    """
    Berechnet sichere Entnahmerate für gewünschte Rente.

    Args:
        initial_capital: Verfügbares Kapital
        desired_monthly_pension: Gewünschte monatliche Rente
        withdrawal_years: Geplante Entnahmedauer
        annual_return: Erwartete Rendite
        annual_inflation: Inflationsrate

    Returns:
        Dictionary mit verschiedenen Szenarien
    """
    desired_annual = desired_monthly_pension * 12

    # Szenario 1: Ohne Inflationsanpassung
    result_no_inflation = fixed_monthly_pension(
        initial_capital=initial_capital,
        monthly_pension=desired_monthly_pension,
        withdrawal_years=withdrawal_years,
        annual_return=annual_return
    )

    # Szenario 2: 4%-Regel mit Inflation
    result_4_percent = four_percent_rule(
        initial_capital=initial_capital,
        withdrawal_years=withdrawal_years,
        annual_return=annual_return,
        annual_inflation=annual_inflation,
        with_inflation_adjustment=True
    )

    # Szenario 3: Dynamische Entnahme 4%
    result_dynamic = dynamic_percentage_withdrawal(
        initial_capital=initial_capital,
        withdrawal_percentage=0.04,
        withdrawal_years=withdrawal_years,
        annual_return=annual_return
    )

    return {
        "desired_monthly_pension": desired_monthly_pension,
        "desired_withdrawal_rate": (desired_annual / initial_capital) * 100,
        "safe_4_percent_monthly": result_4_percent.avg_monthly_withdrawal,
        "dynamic_4_percent_monthly": result_dynamic.avg_monthly_withdrawal,
        "no_inflation_depleted_year": result_no_inflation.capital_depleted_year,
        "inflation_adjusted_depleted_year": result_4_percent.capital_depleted_year,
        "dynamic_remaining_capital": result_dynamic.remaining_capital,
    }


# Beispiel-Nutzung und Tests
if __name__ == "__main__":
    print("=== Test: 4%-Regel ===")
    result_4p = four_percent_rule(
        initial_capital=500000,
        withdrawal_years=30,
        annual_return=0.05,
        annual_inflation=0.02
    )
    print(f"Strategie: {result_4p.strategy_name}")
    print(f"Startkapital: {result_4p.initial_capital:,.0f} €")
    print(f"Durchschnittliche Entnahme: {result_4p.avg_monthly_withdrawal:,.0f} €/Monat")
    print(f"Gesamtentnahmen: {result_4p.total_withdrawals:,.0f} €")
    print(f"Restkapital: {result_4p.remaining_capital:,.0f} €")
    print(f"Success Rate: {result_4p.success_rate*100:.1f}%")
    print(f"Jahr 1: {result_4p.yearly_withdrawals[0][1]:,.0f} €")
    print(f"Jahr 30: {result_4p.yearly_withdrawals[29][1]:,.0f} €")

    print("\n=== Test: Dynamische Entnahme ===")
    result_dyn = dynamic_percentage_withdrawal(
        initial_capital=500000,
        withdrawal_percentage=0.04,
        withdrawal_years=30,
        annual_return=0.05
    )
    print(f"Strategie: {result_dyn.strategy_name}")
    print(f"Durchschnittliche Entnahme: {result_dyn.avg_monthly_withdrawal:,.0f} €/Monat")
    print(f"Restkapital: {result_dyn.remaining_capital:,.0f} €")
    print(f"Jahr 1: {result_dyn.yearly_withdrawals[0][1]:,.0f} €")
    print(f"Jahr 30: {result_dyn.yearly_withdrawals[29][1]:,.0f} €")

    print("\n=== Test: Feste Rente ===")
    result_fixed = fixed_monthly_pension(
        initial_capital=500000,
        monthly_pension=2000,
        withdrawal_years=30,
        annual_return=0.05
    )
    print(f"Strategie: {result_fixed.strategy_name}")
    print(f"Monatliche Rente: {result_fixed.avg_monthly_withdrawal:,.0f} €")
    print(f"Restkapital: {result_fixed.remaining_capital:,.0f} €")
    print(f"Kapital aufgebraucht in Jahr: {result_fixed.capital_depleted_year}")
    print(f"Success Rate: {result_fixed.success_rate*100:.1f}%")

    print("\n=== Test: Hybrid ===")
    result_hybrid = hybrid_withdrawal(
        initial_capital=500000,
        fixed_monthly_pension=1800,
        capital_reserve_percentage=0.2,  # 20% Reserve
        withdrawal_years=30,
        annual_return=0.05
    )
    print(f"Strategie: {result_hybrid.strategy_name}")
    print(f"Monatliche Rente: {result_hybrid.avg_monthly_withdrawal:,.0f} €")
    print(f"Restkapital (inkl. Reserve): {result_hybrid.remaining_capital:,.0f} €")
    print(f"Success Rate: {result_hybrid.success_rate*100:.1f}%")

    print("\n=== Test: Sichere Entnahmerate ===")
    safe_rate = calculate_safe_withdrawal_rate(
        initial_capital=500000,
        desired_monthly_pension=2500,
        withdrawal_years=30,
        annual_return=0.05,
        annual_inflation=0.02
    )
    print(f"Gewünschte Rente: {safe_rate['desired_monthly_pension']:,.0f} €/Monat")
    print(f"Entnahmerate: {safe_rate['desired_withdrawal_rate']:.2f}%")
    print(f"4%-Regel (sicher): {safe_rate['safe_4_percent_monthly']:,.0f} €/Monat")
    print(f"Dynamisch 4%: {safe_rate['dynamic_4_percent_monthly']:,.0f} €/Monat")
    print(f"Ohne Inflation aufgebraucht in Jahr: {safe_rate['no_inflation_depleted_year']}")
