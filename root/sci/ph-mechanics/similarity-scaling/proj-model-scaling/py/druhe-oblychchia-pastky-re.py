def air_state(p_atm, T):
    """Повітря за тиском p_atm (атмосфери) і температурою T (кельвіни)."""
    R   = 287.05
    rho = p_atm * 101_325.0 / (R * T)
    mu  = 1.716e-5 * (T/273.15)**1.5 * (273.15+110.4)/(T+110.4)  # формула Сазерленда
    a   = math.sqrt(1.4 * R * T)
    return Gas(rho, mu, a)

def reynolds_capacity(gas):
    """κ = ρ·a/μ.  При сталому Маху  Re = Ma·κ·L."""
    return gas.rho * gas.a / gas.mu

def dynamic_pressure(gas, mach):
    """Швидкісний напір q = ½·ρ·v² — механічне навантаження на модель."""
    return 0.5 * gas.rho * (mach * gas.a)**2
