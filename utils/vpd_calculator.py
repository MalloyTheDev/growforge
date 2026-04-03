# FILE: growforge/utils/vpd_calculator.py
"""
GrowForge — VPD (Vapor Pressure Deficit) calculator and charting utility.
"""

import math


def calculate_vpd(temp_c: float, humidity_rh: float, leaf_offset: float = 2.0) -> float:
    """
    Calculate VPD in kPa.

    Args:
        temp_c: Air temperature in Celsius
        humidity_rh: Relative humidity (0-100)
        leaf_offset: Leaf temp offset below air temp (default 2°C)

    Returns:
        VPD in kPa
    """
    leaf_temp = temp_c - leaf_offset

    # Saturation vapor pressure (Tetens formula)
    svp_air = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    svp_leaf = 0.6108 * math.exp((17.27 * leaf_temp) / (leaf_temp + 237.3))

    # Actual vapor pressure
    avp = svp_air * (humidity_rh / 100.0)

    # VPD = SVP at leaf - AVP
    vpd = svp_leaf - avp
    return round(max(0, vpd), 2)


def vpd_zone(vpd_value: float) -> str:
    """Return the VPD zone description."""
    if vpd_value < 0.4:
        return "⚠️ Danger (too low) — risk of mold, slow transpiration"
    elif vpd_value < 0.8:
        return "🌱 Seedling / Early Veg zone — good for clones and seedlings"
    elif vpd_value < 1.0:
        return "🌿 Late Veg zone — ideal for vegetative growth"
    elif vpd_value < 1.2:
        return "🌸 Early Flower zone — good transition period"
    elif vpd_value < 1.4:
        return "🌺 Mid Flower zone — peak flowering conditions"
    elif vpd_value < 1.6:
        return "🍂 Late Flower zone — ripening, lower mold risk"
    else:
        return "⚠️ Danger (too high) — plant stress, close stomata"


def vpd_color(vpd_value: float) -> str:
    """Return a color hex for the VPD value."""
    if vpd_value < 0.4:
        return "#29b6f6"  # Blue - too low
    elif vpd_value < 0.8:
        return "#66bb6a"  # Light green - seedling
    elif vpd_value < 1.0:
        return "#4caf50"  # Green - veg
    elif vpd_value < 1.2:
        return "#8bc34a"  # Lime - early flower
    elif vpd_value < 1.4:
        return "#ffc107"  # Amber - mid flower
    elif vpd_value < 1.6:
        return "#ff9800"  # Orange - late flower
    else:
        return "#f44336"  # Red - danger


def generate_vpd_table(leaf_offset: float = 2.0):
    """
    Generate a VPD lookup table.
    Returns list of dicts with temp, rh, vpd, zone, color.
    """
    table = []
    for temp in range(15, 36):  # 15-35°C
        for rh in range(30, 91, 5):  # 30-90% RH
            vpd = calculate_vpd(temp, rh, leaf_offset)
            table.append({
                "temp_c": temp,
                "rh": rh,
                "vpd": vpd,
                "zone": vpd_zone(vpd),
                "color": vpd_color(vpd),
            })
    return table


def c_to_f(c: float) -> float:
    return round(c * 9 / 5 + 32, 1)


def f_to_c(f: float) -> float:
    return round((f - 32) * 5 / 9, 1)
