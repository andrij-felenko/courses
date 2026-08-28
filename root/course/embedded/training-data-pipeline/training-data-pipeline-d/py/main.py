from dataclasses import dataclass

# Розмітка одного об'єкта: клас + рамка у частках кадру [0..1]
@dataclass
class Label:
    cls: int          # номер класу: 0 = людина, 1 = машина, ...
    cx: float         # центр X рамки, частка ширини
    cy: float         # центр Y рамки, частка висоти
    w: float          # ширина рамки, частка кадру
    h: float          # висота рамки, частка кадру

# Перевести рамку в пікселях у нормований запис
def box_to_label(cls, x0, y0, x1, y1, img_w, img_h):
    return Label(
        cls=cls,
        cx=(x0 + x1) / 2 / img_w,   # центр X у частках
        cy=(y0 + y1) / 2 / img_h,   # центр Y у частках
        w=(x1 - x0) / img_w,        # ширина у частках
        h=(y1 - y0) / img_h,        # висота у частках
    )
