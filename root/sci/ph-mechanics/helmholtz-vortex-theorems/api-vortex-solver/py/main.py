import ctypes

class VortexSolverConfig(ctypes.Structure):
    _fields_ = [
        ("num_vortices", ctypes.c_int),
        ("core_radius_eps", ctypes.c_double),
        ("core_type", ctypes.c_int),
        ("integrator", ctypes.c_int),
        ("dt", ctypes.c_double),
        ("is_3d", ctypes.c_int)
    ]

lib = ctypes.CDLL("./libvortex_solver.so")
print("Python ctypes integration initialized successfully.")
