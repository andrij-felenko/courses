import numpy as np
from dataclasses import dataclass, field

@dataclass
class AccelCal:
    accel_bias: np.ndarray = field(default_factory=lambda: np.zeros(3))  # зсув у системі ТІЛА (м/с²)
    calibrated: bool = False                                            # True, коли зсув визначено

# Калібрування зсуву на НЕРУХОМОМУ апараті: усереднити N відліків.
# Горизонтальні осі мають дати ~0, вертикальна — ~g; зсув беремо з горизонталі,
# а по вертикалі лишаємо тяжіння (віднімемо його пізніше у світовій системі).
# Повертає True, якщо апарат був досить нерухомий (розкид малий), інакше False.
def accel_calibrate(cal: AccelCal, samples: np.ndarray) -> bool:
    mean = samples.mean(axis=0)                    # samples має форму (N, 3)

    # перевірка нерухомості: середньоквадратичний розкид навколо середнього
    var = ((samples - mean) ** 2).sum(axis=1).mean()
    if var > 0.25:                                 # (0.5 м/с²)² — апарат ворушився, не калібруємо
        return False

    # зсув по горизонталі — прямо середнє; по вертикалі зсув поки не чіпаємо
    cal.accel_bias = np.array([mean[0], mean[1], 0.0])  # вертикаль тримає g; зсув Z — у нуль висоти
    cal.calibrated = True
    return True
