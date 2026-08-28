import ctypes

class PoyntingVec3(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double), ("z", ctypes.c_double)]

class PoyntingSummary(ctypes.Structure):
    _fields_ = [
        ("active_power_watts", ctypes.c_double),
        ("reactive_power_vars", ctypes.c_double),
        ("max_flux_density_w_m2", ctypes.c_double),
        ("status_ok", ctypes.c_bool)
    ]
