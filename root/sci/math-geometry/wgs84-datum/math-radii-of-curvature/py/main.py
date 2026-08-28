import math

WGS84_A  = 6_378_137.0
WGS84_E2 = 6.69437999014e-3            # 2f − f², f = 1/298.257223563

def meridian_arc(phi: float) -> float:
    """Довжина дуги меридіана від екватора до широти phi (радіани), метри."""
    e2 = WGS84_E2
    e4, e6, e8 = e2*e2, e2**3, e2**4
    A = 1 + 3*e2/4 + 45*e4/64 + 175*e6/256 + 11025*e8/16384
    B =     3*e2/8 + 15*e4/32 + 525*e6/1024 + 2205*e8/4096
    C =              15*e4/256 + 105*e6/1024 + 2205*e8/16384
    D =                            35*e6/3072 + 315*e8/12288
    k = WGS84_A * (1 - e2)
    return k * (A*phi - B*math.sin(2*phi) + C*math.sin(4*phi) - D*math.sin(6*phi))

# meridian_arc(math.pi/2) -> 10001965.729...
