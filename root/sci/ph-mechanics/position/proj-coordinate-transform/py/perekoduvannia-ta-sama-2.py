def rect_to_cyl(x, y, z):
    """Прямокутні → циліндричні (ρ, φ, z)."""
    return math.hypot(x, y), math.atan2(y, x), z

def cyl_to_rect(rho, phi, z):
    return rho * math.cos(phi), rho * math.sin(phi), z

def rect_to_sph(x, y, z):
    """Прямокутні → сферичні (r, θ, φ):
       θ — полярний кут від осі z, φ — азимут у площині xy (домовленість фізиків)."""
    r     = math.sqrt(x*x + y*y + z*z)
    theta = math.atan2(math.hypot(x, y), z)   # кут від осі z, у [0, π]
    phi   = math.atan2(y, x)                    # азимут, у (−π, π]
    return r, theta, phi

def sph_to_rect(r, theta, phi):
    s = r * math.sin(theta)                     # довжина проєкції на площину xy
    return s * math.cos(phi), s * math.sin(phi), r * math.cos(theta)
