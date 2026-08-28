from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional

class BoundaryType(Enum):
    DIRICHLET = "dirichlet"
    NEUMANN = "neumann"

@dataclass
class GridConfig:
    nx: int = 100
    ny: int = 100
    nz: int = 1
    step_size_meters: float = 1e-3
    relative_permittivity: float = 1.0

@dataclass
class ElectrodeSpec:
    electrode_id: int
    potential_volts: float
    boundary_type: BoundaryType
    nodes: List[Tuple[int, int, int]] = field(default_factory=list)

@dataclass
class EnergyResult:
    total_energy_joules: float
    max_energy_density_j_m3: float
    mean_energy_density_j_m3: float
    iterations_count: int
    is_converged: bool

class ElectrostaticEnergyCalculator:
    def __init__(self, config: GridConfig) -> None:
        ...

    def add_electrode(self, electrode: ElectrodeSpec) -> None:
        """Додає поверхню або об'єм електрода з заданим потенціалом."""
        ...

    def set_charge_density(self, x: int, y: int, z: int, rho_c_m3: float) -> None:
        """Встановлює об'ємну густину заряду ρ у вказаному вузлі сітки."""
        ...

    def solve_field(self, max_iterations: int = 10000, tolerance: float = 1e-7) -> None:
        """Розв'язує рівняння Пуассона ітераційним методом."""
        ...

    def calculate_total_energy(self) -> EnergyResult:
        """Обчислює інтегральну енергію поля по всіх комірках сітки."""
        ...

    @staticmethod
    def analytical_flat_capacitor_energy(
        area_sq_m: float, 
        distance_m: float, 
        voltage_volts: float, 
        relative_permittivity: float = 1.0
    ) -> float:
        """Аналітичний розрахунок W = 0.5 * C * V^2 для плоского конденсатора."""
        eps0 = 8.854187817e-12
        capacitance = (eps0 * relative_permittivity * area_sq_m) / distance_m
        return 0.5 * capacitance * (voltage_volts ** 2)
