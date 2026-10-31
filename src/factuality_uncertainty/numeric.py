"""Decimal quantities, dimensions and bounded arithmetic; no expression eval."""

from decimal import Decimal, InvalidOperation

UNITS = {"Wh": ("energy", "1"), "kWh": ("energy", "1000"),
         "W": ("power", "1"), "kW": ("power", "1000"),
         "h": ("time", "1"), "min": ("time", "0.01666666666666666666666666667"),
         "kg": ("mass", "1"), "g": ("mass", "0.001"),
         "1": ("ratio", "1"), "%": ("ratio", "0.01")}


def number(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("invalid_quantity")
    try:
        parsed = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("invalid_quantity") from exc
    if not parsed.is_finite() or abs(parsed) > Decimal("1e30"):
        raise ValueError("invalid_quantity")
    return parsed


def quantity(value, unit):
    if unit not in UNITS:
        raise ValueError("unknown_unit")
    dimension, factor = UNITS[unit]
    return number(value) * Decimal(factor), dimension


def check(claim, fact):
    """Assumptions, units, bounds and arithmetic are separate from text support."""
    failures = []
    if set(claim.get("assumption_refs", [])) != set(fact.get("assumption_refs", [])):
        failures.append("assumptions_mismatch")
    try:
        actual, dimension = quantity(claim["value"], claim["unit"])
        expected, expected_dimension = quantity(fact["value"], fact["unit"])
        tolerance = number(claim.get("tolerance", "0"))
        maximum = number(fact.get("tolerance", "0"))
        if tolerance < 0 or maximum < 0 or tolerance > maximum:
            failures.append("unauthorized_tolerance")
        if dimension != expected_dimension:
            failures.append("unit_mismatch")
        elif abs(actual - expected) > max(Decimal(0), min(tolerance, maximum)):
            failures.append("quantity_mismatch")
        bounds = fact.get("bounds")
        if bounds is not None:
            low, high = map(number, bounds)
            if low > high:
                raise ValueError("invalid_bounds")
            if not low <= actual <= high:
                failures.append("outside_bounds")
        expression = claim.get("arithmetic")
        if expression:
            left, ld = quantity(expression["left"]["value"], expression["left"]["unit"])
            right, rd = quantity(expression["right"]["value"], expression["right"]["unit"])
            operation = expression["op"]
            if operation == "add" and ld == rd == dimension:
                computed = left + right
            elif operation == "subtract" and ld == rd == dimension:
                computed = left - right
            elif operation == "divide" and right != 0 and (
                    ld == rd and dimension == "ratio" or
                    ld == "energy" and rd == "time" and dimension == "power"):
                computed = left / right
            elif operation == "multiply" and {ld, rd} == {"power", "time"} and dimension == "energy":
                computed = left * right
            else:
                raise ValueError("unsupported_arithmetic")
            if abs(computed - actual) > max(Decimal(0), min(tolerance, maximum)):
                failures.append("arithmetic_mismatch")
    except (ValueError, KeyError, TypeError, InvalidOperation) as exc:
        failures.append(str(exc) if isinstance(exc, ValueError) else "invalid_numeric_structure")
    return {"status": "fail" if failures else "pass", "failures": sorted(set(failures))}
