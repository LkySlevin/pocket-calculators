"""
Steuerberechnungs-Funktionen für Altersvorsorge
"""


def calculate_tax_rate(yearly_income: float) -> float:
    """
    Berechnet ungefähren Steuersatz basierend auf Jahreseinkommen (2025)
    Allgemeine Funktion für Einkommensteuer-Berechnung.

    Args:
        yearly_income: Jahreseinkommen in Euro

    Returns:
        Steuersatz als Dezimalzahl (z.B. 0.42 für 42%)
    """
    if yearly_income <= 11_604:  # Grundfreibetrag
        return 0.0
    elif yearly_income <= 17_005:
        return 0.14  # Eingangssteuersatz
    elif yearly_income <= 66_760:
        # Progressionszone 1
        return 0.14 + (yearly_income - 17_005) / (66_760 - 17_005) * (0.42 - 0.14)
    elif yearly_income <= 277_825:
        return 0.42  # Spitzensteuersatz
    else:
        return 0.45  # Reichensteuer


def calculate_retirement_tax_rate(yearly_income: float) -> float:
    """
    Berechnet ungefähren Steuersatz basierend auf Jahreseinkommen (2025)

    Args:
        yearly_income: Jahreseinkommen in Euro

    Returns:
        Steuersatz als Dezimalzahl (z.B. 0.42 für 42%)
    """
    if yearly_income <= 11_604:  # Grundfreibetrag
        return 0.0
    elif yearly_income <= 17_005:
        return 0.14  # Eingangssteuersatz
    elif yearly_income <= 66_760:
        # Progressionszone 1
        return 0.14 + (yearly_income - 17_005) / (66_760 - 17_005) * (0.42 - 0.14)
    elif yearly_income <= 277_825:
        return 0.42  # Spitzensteuersatz
    else:
        return 0.45  # Reichensteuer
