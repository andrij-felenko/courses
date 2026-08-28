import math
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class TransitionType(Enum):
    SECOND_ORDER = 1
    FIRST_ORDER = 2
    TRICRITICAL = 3


class ErrorCode(Enum):
    SUCCESS = 0
    CONVERGENCE_FAILED = 1
    INVALID_PARAMETERS = 2


@dataclass
class LandauParams:
    a0: float = 1.0
    b: float = 1.0
    c: float = 0.0
    Tc: float = 300.0
    g: float = 1.0e-18
    C0: float = 25.0
    type: TransitionType = TransitionType.SECOND_ORDER

    def validate(self) -> bool:
        if self.Tc <= 0.0 or self.a0 <= 0.0:
            return False
        if self.type == TransitionType.SECOND_ORDER and self.b <= 0.0:
            return False
        if self.type == TransitionType.FIRST_ORDER and (
            self.b >= 0.0 or self.c <= 0.0
        ):
            return False
        return True


@dataclass
class StateResult:
    T: float
    H: float
    eta: float
    free_energy: float
    heat_capacity: float
    susceptibility: float
    correlation_length: float
    error: ErrorCode = ErrorCode.SUCCESS


class LandauSolver:
    """Python API клас розв'язувача термодинамічних переходів Ландау."""

    def __init__(self, params: LandauParams):
        if not params.validate():
            raise ValueError("Некоректні параметри потенціалу Ландау")
        self.params = params

    def compute_potential(
        self, T: float, eta: float, H: float = 0.0
    ) -> float:
        a = self.params.a0 * (T - self.Tc)
        energy = (
            a * eta**2 + 0.5 * self.params.b * eta**4 - eta * H
        )
        if self.params.c > 0.0:
            energy += (1.0 / 3.0) * self.params.c * eta**6
        return energy

    def compute_order_parameter(
        self, T: float, H: float = 0.0, eta_guess: float = 0.0
    ) -> float:
        if (
            self.params.type == TransitionType.SECOND_ORDER
            and T >= self.Tc
            and abs(H) < 1e-12
        ):
            return 0.0

        a = self.params.a0 * (T - self.Tc)
        eta = eta_guess
        if (
            eta == 0.0
            and T < self.Tc
            and self.params.type == TransitionType.SECOND_ORDER
        ):
            eta = math.sqrt(self.params.a0 * (self.Tc - T) / self.params.b)

        for _ in range(200):
            grad = (
                2.0 * a * eta + 2.0 * self.params.b * eta**3 - H
            )
            hessian = 2.0 * a + 6.0 * self.params.b * eta**2
            if self.params.c > 0.0:
                grad += 2.0 * self.params.c * eta**5
                hessian += 10.0 * self.params.c * eta**4

            if abs(hessian) < 1e-14:
                break
            step = grad / hessian
            eta -= step
            if abs(step) < 1e-9:
                return eta
        return eta

    def compute_heat_capacity(self, T: float) -> float:
        if self.params.type == TransitionType.SECOND_ORDER:
            return (
                self.params.C0
                if T >= self.Tc
                else self.params.C0
                + (self.params.a0**2 * T) / self.params.b
            )
        return self.params.C0

    def compute_susceptibility(self, T: float, H: float = 0.0) -> float:
        eta = self.compute_order_parameter(T, H)
        a = self.params.a0 * (T - self.Tc)
        denom = 2.0 * a + 6.0 * self.params.b * eta**2
        if self.params.c > 0.0:
            denom += 10.0 * self.params.c * eta**4
        return 1.0 / denom if abs(denom) >= 1e-12 else 1.0e12

    def compute_correlation_length(
        self, T: float, H: float = 0.0
    ) -> float:
        chi = self.compute_susceptibility(T, H)
        return math.sqrt(self.params.g * chi) if chi > 0 else 0.0

    def solve_state(self, T: float, H: float = 0.0) -> StateResult:
        eta = self.compute_order_parameter(T, H)
        return StateResult(
            T=T,
            H=H,
            eta=eta,
            free_energy=self.compute_potential(T, eta, H),
            heat_capacity=self.compute_heat_capacity(T),
            susceptibility=self.compute_susceptibility(T, H),
            correlation_length=self.compute_correlation_length(T, H),
        )
