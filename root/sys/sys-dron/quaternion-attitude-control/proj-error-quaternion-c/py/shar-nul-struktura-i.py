from dataclasses import dataclass

@dataclass
class Quat:
    w: float
    x: float
    y: float
    z: float

# тотожність — «нічого не роблю», нульовий поворот
QUAT_IDENTITY = Quat(1.0, 0.0, 0.0, 0.0)
