"""Explicit temperature-dependent p-affinity to energy-equivalent conversion.

Kd values yield standard binding free energies under equilibrium assumptions.
For mixed IC50 and censored values the result is only a comparison scale.
"""
import math

R_KCAL_MOL_K = 0.00198720425864083
DEFAULT_TEMPERATURE_K = 298.15


def energy_factor(temperature_k=DEFAULT_TEMPERATURE_K):
    """Return positive kcal/mol per p-affinity unit at the stated temperature."""
    if not math.isfinite(temperature_k) or temperature_k <= 0:
        raise ValueError('Temperature must be finite and positive')
    return R_KCAL_MOL_K * temperature_k * math.log(10)


def p_to_energy_equivalent(p_affinity, temperature_k=DEFAULT_TEMPERATURE_K):
    """Convert p values to the signed energy-equivalent scale (kcal/mol)."""
    return -energy_factor(temperature_k) * p_affinity


def rmse_to_energy_equivalent(rmse_p, temperature_k=DEFAULT_TEMPERATURE_K):
    """Convert a nonnegative p-unit RMSE to kcal/mol on the same scale."""
    if not math.isfinite(rmse_p) or rmse_p < 0:
        raise ValueError('RMSE must be finite and nonnegative')
    return energy_factor(temperature_k) * rmse_p
