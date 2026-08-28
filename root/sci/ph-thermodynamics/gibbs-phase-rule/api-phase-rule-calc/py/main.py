import ctypes

class PhaseSystemSpecC(ctypes.Structure):
    _fields_ = [
        ("num_species", ctypes.c_size_t),
        ("num_reactions", ctypes.c_size_t),
        ("num_constraints", ctypes.c_size_t),
        ("num_phases", ctypes.c_size_t),
        ("is_condensed", ctypes.c_bool),
        ("stoich_matrix_flat", ctypes.POINTER(ctypes.c_double))
    ]

class PhaseResultSpecC(ctypes.Structure):
    _fields_ = [
        ("rank_reactions", ctypes.c_size_t),
        ("gibbs_components", ctypes.c_size_t),
        ("degrees_of_freedom", ctypes.c_int),
        ("status_code", ctypes.c_int),
        ("status_message", ctypes.c_char_p)
    ]

# Завантаження динамічної бібліотеки
lib = ctypes.CDLL("./libthermo_phase.so")
lib.thermo_analyze_phase_system.argtypes = [
    ctypes.POINTER(PhaseSystemSpecC), 
    ctypes.POINTER(PhaseResultSpecC)
]
lib.thermo_analyze_phase_system.restype = ctypes.c_int
