'''Denitrification function that should match the default in Daisy'''
import math as m
import numpy as np

def default_denitrification(*, Theta, NO3, rho_b, CO2_C, CO2_C_fast, Theta_sat, h, **_kwargs):
    # pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals
    # pylint: disable=invalid-name
    """
    Compute denitrification following the original Daisy implementation, including potential and
    actual denitrification, partitioning between N2 and N2O, and moisture/NO3/CO2 response
    functions.

    Parameters
    ----------
    h : float
        Soil water pressure head (cm).
    Theta : float
        Volumetric water content.
    Theta_sat : float
        Saturated water content.
    NO3 : float
        Soil nitrate concentration.
    rho_b : float
        Soil dry bulk density. [g/cm^3]
    CO2_C : float
        Total soil CO2-C.
    CO2_C_fast : float
        Fast pool of CO2-C.

    Returns
    -------
    dict
        {
            "N2O-Denit": float,
            "N2-Denit": float,
            "NO3": float (negative = loss),
            "Actual-Denit": float,
            "Potential-Denit": float,
        }
    """

    # ------------------------
    # Water-filled pore space
    # ------------------------
    wfps = Theta / Theta_sat

    # ------------------------
    # Response curves
    # ------------------------

    # WFPS moisture response (from Daisy)
    waterPLF_x = [0.0, 0.4,  0.5,  0.57, 0.64, 0.71, 0.76, 0.81, 0.85, 0.9, 1.0]
    waterPLF_y = [0.0, 0.01, 0.07, 0.17, 0.32, 0.51, 0.66, 0.79, 0.9,  1.0, 1.0]
    f_w = plf(waterPLF_x, waterPLF_y, wfps)

    # Should CO2_C_mass really be calculayed before correcting CO2_C
    activeDepth = 30.0
    CO2_C_mass = CO2_C * 0.001 * activeDepth * 1e8 * 24.0

    # Pressure response correction
    h_corr = float(pressure_response(h))
    if h_corr != 0:
        # Daisy rescales CO2 pools
        CO2_C_fast = (CO2_C_fast / h_corr) * 0.6
        CO2_C      = (CO2_C      / h_corr) * 0.6

    # ------------------------
    # Parameters
    # ------------------------
    alpha = 0.0001      # slow pool factor (kg Gas-N/kg CO2-C)
    alpha_fast = 0.05302701196829458
    Kd = 0.020833       # 1/h
    Kd_fast = Kd
    f_T = 1.0           # temperature modifier (placeholder)

    # ------------------------
    # Potential denitrification
    # ------------------------
    potDenitFast = f_T * alpha_fast * CO2_C_fast
    potDenitSlow = f_T * alpha * (CO2_C - CO2_C_fast)
    potDenit = potDenitFast + potDenitSlow

    # ------------------------
    # Actual denitrification (limited by nitrate)
    # ------------------------
    rate_fast = f_w * potDenitFast
    rate_slow = f_w * potDenitSlow

    actDenit = min(rate_slow, Kd * NO3) + min(rate_fast, Kd_fast * NO3)
    NO3_loss = -actDenit  # negative = nitrate consumed


    # ------------------------
    # Partitioning between N2O and N2
    # ------------------------
    NO3_mass = (NO3 / rho_b) * 1e6
    # activeDepth = 30.0
    # CO2_C_mass = CO2_C * 0.001 * activeDepth * 1e8 * 24.0

    # Daisy regulatory functions
    fr_NO3 = (1.0 - (0.5 + m.atan(m.pi * 0.01 * (NO3_mass - 190.0)) / m.pi)) * 25.0
    fr_CO2 = 13.0 + 30.78 * m.atan(m.pi * 0.07 * (CO2_C_mass - 13.0)) / m.pi
    fr_WFPS = 1.4 / pow(13.0, 17.0 / pow(13.0, 2.2 * wfps))

    fr = min(fr_NO3, fr_CO2) * fr_WFPS

    N2_denit = actDenit / (1.0 + 1.0 / fr)
    N2O_denit = actDenit / (1.0 + fr)

    return {
        "N2O-Denit": N2O_denit,
        "N2-Denit": N2_denit,
        "NO3": NO3_loss,
        "Actual-Denit": actDenit,
        "Potential-Denit": potDenit,
    }


def plf(x, y, x0):
    """
    Piecewise-linear interpolation function.

    Parameters
    ----------
    x, y : list of float
        Coordinates and values of a tabulated function.
    x0 : float
        Point at which to compute an interpolated value.

    Returns
    -------
    float
        Interpolated function value.
    """
    i_min, i_max = 0, len(x) - 1

    if x0 < x[i_min]:
        return y[i_min]
    if x0 > x[i_max]:
        return y[i_max]

    while True:
        if i_max - i_min == 1:
            slope = (y[i_max] - y[i_min]) / (x[i_max] - x[i_min])
            return y[i_min] + slope * (x0 - x[i_min])

        mid = (i_max + i_min) // 2
        if x[mid] < x0:
            i_min = mid
        elif x0 == x[mid]:
            return y[mid]
        else:
            i_max = mid


def pressure_response(h):
    # pylint: disable=invalid-name
    """
    Pressure response as a function of soil water pressure head.

    Uses a pF-based moisture response curve typical of Daisy.

    Returns
    -------
    float in [0, 1]
    """
    if h >= 0:
        return 0.6  # saturated / ponded

    pF = np.log10(-h)

    if pF <= 0:
        return 0.6
    if pF <= 1.5:
        return 0.6 + (1.0 - 0.6) * (pF / 1.5)
    if pF <= 2.5:
        return 1.0
    if pF <= 6.5:
        return 1.0 - (pF - 2.5) / (6.5 - 2.5)

    return 0.0
