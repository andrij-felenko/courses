from dataclasses import dataclass

# Розібрана шина: префікс, ліва/права межі ЯК НАПИСАНО, і чи це вектор.
# Увага: left/right — це ліве/праве число запису, НЕ «менше/більше».
@dataclass
class BusName:
    prefix: str            # "D" для "D[7..0]"
    left: int = 0          # ліва й права межі: 7 і 0 для "D[7..0]"
    right: int = 0
    is_vector: bool = False  # False для скаляра "CLK"
