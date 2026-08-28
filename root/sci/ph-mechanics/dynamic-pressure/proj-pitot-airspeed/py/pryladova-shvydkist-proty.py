from math import sqrt

R_AIR, RHO_SSL, P_SSL, GAMMA = 287.05, 1.225, 101325.0, 1.4

def air_density(p_static, T_kelvin):
    return p_static / (R_AIR * T_kelvin)          # ρ = p/(R·T)

def eas_from_dp(dp):                              # приладова
    return 0.0 if dp <= 0 else sqrt(2.0 * dp / RHO_SSL)

def tas_from_dp(dp, rho):                         # справжня
    return 0.0 if dp <= 0 else sqrt(2.0 * dp / rho)
