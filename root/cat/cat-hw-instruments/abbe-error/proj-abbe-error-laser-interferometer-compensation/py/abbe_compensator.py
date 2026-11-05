"""
abbe_compensator.py
Реалізація математичної моделі похибки Аббе першого порядку для малих кутів.

Містить структури геометричного плеча AbbeArm, дискретних замірів кутів
InterferometerSample та клас AbbeCompensator, що виконує конвертацію кутових
одиниць у радіани, векторний розрахунок паразитного поздовжнього зміщення
позиціонування вздовж осі X та розрахунок компенсуючих поправок для ЧПУ.
"""
from dataclasses import dataclass
import math
from typing import List, Optional, Sequence


@dataclass(frozen=True)
class AbbeArm:
    """
    Геометричне плече Аббе — вектор просторового зміщення робочої точки
    (наприклад, вершини різального інструмента або вимірювального щупа)
    відносно лінії вимірювання (лазерного променя або оптичної шкали).

    Атрибути:
        dy: Поперечний зсув уздовж осі Y (мм). Створює похибку при рисканні (yaw).
        dz: Вертикальний зсув уздовж осі Z (мм). Створює похибку при тангажі (pitch).
        dx: Поздовжній зсув уздовж осі X (мм). Входить у просторовий вектор плеча.
    """
    dy: float
    dz: float
    dx: float = 0.0

    def __post_init__(self) -> None:
        for name, val in (("dy", self.dy), ("dz", self.dz), ("dx", self.dx)):
            if not isinstance(val, (int, float)) or not math.isfinite(val):
                raise ValueError(f"Компонент плеча Аббе '{name}' повинен бути скінченним числом, отримано: {val}")


@dataclass(frozen=True)
class InterferometerSample:
    """
    Дискретний замір кутових відхилень каретки за допомогою лазерного інтерферометра.

    Атрибути:
        position: Координата положення каретки вздовж осі переміщення X (мм).
        pitch: Кутове відхилення тангажу навколо осі Y у вхідних одиницях.
        yaw: Кутове відхилення рискання навколо осі Z у вхідних одиницях.
    """
    position: float
    pitch: float
    yaw: float

    def __post_init__(self) -> None:
        for name, val in (("position", self.position), ("pitch", self.pitch), ("yaw", self.yaw)):
            if not isinstance(val, (int, float)) or not math.isfinite(val):
                raise ValueError(f"Параметр заміру '{name}' повинен бути скінченним числом, отримано: {val}")


@dataclass(frozen=True)
class AbbeCorrection:
    """
    Результат розрахунку лінійної похибки Аббе та компенсуючої поправки для ЧПУ.

    Атрибути:
        position: Координата вузла сітки вздовж осі переміщення X (мм).
        pitch_rad: Кут тангажу, нормалізований у радіани (рад).
        yaw_rad: Кут рискання, нормалізований у радіани (рад).
        abbe_error: Розраховане лінійне зміщення робочої точки вздовж осі X (мм).
        correction: Коригувальна поправка для системи ЧПУ (мм), correction = -abbe_error.
    """
    position: float
    pitch_rad: float
    yaw_rad: float
    abbe_error: float
    correction: float


class AbbeCompensator:
    """
    Математичний обчислювач похибки Аббе першого порядку для малих кутів.

    Принцип Аббе стверджує: якщо лінія вимірювання не збігається з лінією переміщення
    робочого органа, будь-який кутовий перекіс напрямних призводить до лінійної похибки.
    Для правої декартової системи координат і малих кутів (sin(theta) ≈ theta):
        Delta_x = dz * theta_pitch - dy * theta_yaw
    де:
        theta_pitch — тангаж (обертання навколо осі Y у радіанах);
        theta_yaw   — рискання (обертання навколо осі Z у радіанах);
        dz          — вертикальне плече Аббе (мм);
        dy          — поперечне плече Аббе (мм).

    Для компенсації паразитного зміщення система керування ЧПУ повинна додати
    поправку протилежного знака:
        Correction = -Delta_x
    """

    # Константи переведення кутових одиниць у радіани
    _ARCSEC_TO_RAD: float = math.pi / (180.0 * 3600.0)  # 1 кутова секунда ≈ 4.848136811e-6 рад
    _URAD_TO_RAD: float = 1e-6                          # 1 мікрорадіан = 10^-6 рад

    def __init__(self, arm: AbbeArm, default_unit: str = "arcsec") -> None:
        """
        Ініціалізація компенсатора геометричним плечем та базовими одиницями кута.

        Аргументи:
            arm: Об'єкт AbbeArm із просторовими зсувами (dy, dz, dx).
            default_unit: Одиниця вимірювання кутів ('arcsec', 'urad', 'µrad', 'rad').
        """
        self.arm = arm
        self.default_unit = default_unit.lower()
        self._validate_unit(self.default_unit)

    @classmethod
    def _validate_unit(cls, unit: str) -> None:
        """Перевірка валідності вказаної кутової одиниці."""
        valid_units = {"arcsec", "urad", "µrad", "rad"}
        if unit not in valid_units:
            raise ValueError(
                f"Невідома кутова одиниця '{unit}'. Підтримуються: {', '.join(sorted(valid_units))}"
            )

    def to_radians(self, angle: float, unit: Optional[str] = None) -> float:
        """
        Нормалізація числового значення кута в радіани.

        Аргументи:
            angle: Кутове значення.
            unit: Одиниця виміру (якщо не вказано, використовується default_unit).

        Повертає:
            Кут у радіанах.
        """
        u = unit.lower() if unit is not None else self.default_unit
        self._validate_unit(u)

        if u == "arcsec":
            return angle * self._ARCSEC_TO_RAD
        if u in ("urad", "µrad"):
            return angle * self._URAD_TO_RAD
        return float(angle)

    def calculate_displacement(self, pitch_rad: float, yaw_rad: float) -> float:
        """
        Векторний розрахунок паразитного поздовжнього лінійного зміщення першого порядку.

        Аргументи:
            pitch_rad: Тангаж навколо осі Y (рад).
            yaw_rad: Рискання навколо осі Z (рад).

        Повертає:
            Паразитне лінійне зміщення Delta_x уздовж осі X (мм).
        """
        return (self.arm.dz * pitch_rad) - (self.arm.dy * yaw_rad)

    def calculate_sample(
        self,
        sample: InterferometerSample,
        unit: Optional[str] = None
    ) -> AbbeCorrection:
        """
        Розрахунок похибки Аббе та протилежної поправки для одного вимірювального заміру.

        Аргументи:
            sample: Об'єкт заміру InterferometerSample.
            unit: Одиниця кута заміру (опціонально).

        Повертає:
            Об'єкт AbbeCorrection із розрахованою похибкою та поправкою.
        """
        pitch_rad = self.to_radians(sample.pitch, unit)
        yaw_rad = self.to_radians(sample.yaw, unit)
        abbe_error = self.calculate_displacement(pitch_rad, yaw_rad)
        correction = -abbe_error

        return AbbeCorrection(
            position=sample.position,
            pitch_rad=pitch_rad,
            yaw_rad=yaw_rad,
            abbe_error=abbe_error,
            correction=correction,
        )

    def compute_corrections(
        self,
        samples: Sequence[InterferometerSample],
        unit: Optional[str] = None
    ) -> List[AbbeCorrection]:
        """
        Пакетний розрахунок масиву поправок для послідовності замірів інтерферометра.

        Аргументи:
            samples: Послідовність вимірювань InterferometerSample.
            unit: Одиниця кута для всіх замірів (опціонально).

        Повертає:
            Список розрахованих вузлів корекції AbbeCorrection.
        """
        return [self.calculate_sample(s, unit) for s in samples]
