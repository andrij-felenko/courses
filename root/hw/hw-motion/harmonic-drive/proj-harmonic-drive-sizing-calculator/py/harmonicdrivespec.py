from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass(frozen=True)
class HarmonicDriveSpec:
    size_name: str
    ratio: float
    rated_torque: float           # Номінальний тривалий крутний момент [Н·м]
    limit_accel_torque: float     # Граничний момент розгону/гальмування [Н·м]
    ratchet_torque: float         # Момент перескоку зубів [Н·м]
    max_input_speed: float        # Максимальна вхідна швидкість [об/хв]
    t1_torque: float              # Границя першої зони жорсткості T_1 [Н·м]
    t2_torque: float              # Границя другої зони жорсткості T_2 [Н·м]
    k1_stiffness: float           # Жорсткість зони 1 [Н·м / рад]
    k2_stiffness: float           # Жорсткість зони 2 [Н·м / рад]
    k3_stiffness: float           # Жорсткість зони 3 [Н·м / рад]
    lost_motion_arcmin: float     # Втрачений рух [кутові мінути]
    c_dyn_bearing: float          # Динамічна вантажопідйомність підшипника C [Н]
    bearing_load_factor: float    # Фактор переведення моменту в радіальне навантаження [Н / (Н·м)]

@dataclass(frozen=True)
class MotionSegment:
    duration_s: float             # Тривалість ділянки t_i [с]
    output_speed_rpm: float       # Частота обертання вихідного вала n_i [об/хв]
    output_torque_nm: float       # Вихідний крутний момент T_i [Н·м]

@dataclass
class SizingResult:
    spec: HarmonicDriveSpec
    n_eq: float
    t_eq: float
    max_torque: float
    max_speed_in: float
    angular_deflection_arcmin: float
    bearing_l10h: float
    passed_rated: bool
    passed_accel: bool
    passed_ratchet: bool
    passed_speed: bool
    passed_bearing: bool

    @property
    def is_valid(self) -> bool:
        return all([
            self.passed_rated,
            self.passed_accel,
            self.passed_ratchet,
            self.passed_speed,
            self.passed_bearing
        ])

class HarmonicDriveCalculator:
    RAD_TO_ARCMIN = (180.0 * 60.0) / math.pi

    @staticmethod
    def calculate_equivalent_load(cycle: List[MotionSegment]) -> tuple[float, float, float, float]:
        if not cycle:
            raise ValueError("Цикл руху не містить сегментів")
        
        sum_t = sum(seg.duration_s for seg in cycle)
        if sum_t <= 0:
            raise ValueError("Сумарний час циклу повинен бути додатним")
        
        sum_n_t = sum(abs(seg.output_speed_rpm) * seg.duration_s for seg in cycle)
        n_eq = sum_n_t / sum_t
        
        # Кубічне зважування моменту за втомним критерієм підшипника та flexspline
        if sum_n_t > 0:
            sum_cubic = sum(abs(seg.output_speed_rpm) * seg.duration_s * (abs(seg.output_torque_nm) ** 3) for seg in cycle)
            t_eq = (sum_cubic / sum_n_t) ** (1.0 / 3.0)
        else:
            # Якщо редуктор лише тримає статичний момент
            t_eq = max(abs(seg.output_torque_nm) for seg in cycle)
        
        max_torque = max(abs(seg.output_torque_nm) for seg in cycle)
        max_speed_out = max(abs(seg.output_speed_rpm) for seg in cycle)
        
        return n_eq, t_eq, max_torque, max_speed_out

    @classmethod
    def calculate_torsional_deflection(cls, spec: HarmonicDriveSpec, torque: float) -> float:
        t_abs = abs(torque)
        t1 = spec.t1_torque
        t2 = spec.t2_torque
        
        if t_abs <= t1:
            theta_rad = t_abs / spec.k1_stiffness
        elif t_abs <= t2:
            theta_rad = (t1 / spec.k1_stiffness) + ((t_abs - t1) / spec.k2_stiffness)
        else:
            theta_rad = (
                (t1 / spec.k1_stiffness)
                + ((t2 - t1) / spec.k2_stiffness)
                + ((t_abs - t2) / spec.k3_stiffness)
            )
        
        return theta_rad * cls.RAD_TO_ARCMIN

    @staticmethod
    def calculate_bearing_life(spec: HarmonicDriveSpec, n_in_eq: float, t_eq: float) -> float:
        if n_in_eq <= 0:
            return float('inf')
        
        # Еквівалентне радіальне навантаження на кулачковий підшипник генератора
        p_eq = t_eq * spec.bearing_load_factor
        if p_eq <= 0:
            return float('inf')
        
        # Ресурс за стандартом ISO 281 для шарикопідшипників (показник степеня 3)
        l_10 = (spec.c_dyn_bearing / p_eq) ** 3
        l_10h = (1_000_000.0 / (60.0 * n_in_eq)) * l_10
        return l_10h

    @classmethod
    def evaluate_catalog(
        cls,
        catalog: List[HarmonicDriveSpec],
        cycle: List[MotionSegment],
        target_life_hours: float = 15000.0
    ) -> List[SizingResult]:
        n_eq, t_eq, max_t, max_n = cls.calculate_equivalent_load(cycle)
        results = []
        
        for spec in catalog:
            n_in_eq = n_eq * spec.ratio
            max_n_in = max_n * spec.ratio
            
            passed_rated = t_eq <= spec.rated_torque
            passed_accel = max_t <= spec.limit_accel_torque
            passed_ratchet = max_t <= (0.8 * spec.ratchet_torque)
            passed_speed = max_n_in <= spec.max_input_speed
            
            l_10h = cls.calculate_bearing_life(spec, n_in_eq, t_eq)
            passed_bearing = l_10h >= target_life_hours
            
            deflection = cls.calculate_torsional_deflection(spec, max_t)
            
            res = SizingResult(
                spec=spec,
                n_eq=n_eq,
                t_eq=t_eq,
                max_torque=max_t,
                max_speed_in=max_n_in,
                angular_deflection_arcmin=deflection,
                bearing_l10h=l_10h,
                passed_rated=passed_rated,
                passed_accel=passed_accel,
                passed_ratchet=passed_ratchet,
                passed_speed=passed_speed,
                passed_bearing=passed_bearing
            )
            results.append(res)
            
        return results

def format_sizing_report(results: List[SizingResult]) -> str:
    lines = [
        "ЗВІТ ІНЖЕНЕРНОГО ПІДБОРУ ХВИЛЬОВОГО РЕДУКТОРА",
        "=" * 60,
    ]
    for r in results:
        status = "ПІДХОДИТЬ" if r.is_valid else "ВІДХИЛЕНО"
        lines.append(f"Модель: {r.spec.size_name:<10} | Статус: {status}")
        lines.append(f"  T_eq = {r.t_eq:.2f} Н·м (Номінал: {r.spec.rated_torque} Н·м) -> {'OK' if r.passed_rated else 'ПЕРЕВАНТАЖЕННЯ'}")
        lines.append(f"  T_max = {r.max_torque:.2f} Н·м (Пік розгону: {r.spec.limit_accel_torque} Н·м) -> {'OK' if r.passed_accel else 'ПЕРЕВИЩЕННЯ'}")
        lines.append(f"  Запас до перескоку зубів: {r.spec.ratchet_torque / r.max_torque:.2f} (Мін: 1.25) -> {'OK' if r.passed_ratchet else 'НЕБЕЗПЕКА РЕЧЕТИНГУ'}")
        lines.append(f"  Ресурс підшипника L_10h = {r.bearing_l10h:.0f} год -> {'OK' if r.passed_bearing else 'МАЛИЙ РЕСУРС'}")
        lines.append(f"  Пружне скручування θ = {r.angular_deflection_arcmin:.2f} кут. мін")
        lines.append("-" * 60)
    return "\n".join(lines)
