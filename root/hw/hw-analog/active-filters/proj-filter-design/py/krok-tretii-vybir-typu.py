from typing import NamedTuple

# Один «рецепт» ланки: множник частоти (f_ланки = fmul · fc) і добротність.
class SKRecipe(NamedTuple):
    fmul: float
    Q: float

# Тип фільтра = впорядкований набір ланок (нижчий Q першим — економить запас).
class SKFilterType(NamedTuple):
    name: str
    stage: tuple[SKRecipe, ...]   # ланки
    order: int                    # порядок (2 на кожну ланку 2-го порядку)

# ── Другий порядок: одна ланка ───────────────────────────────────────────
BW2   = (SKRecipe(1.000, 0.7071),)                        # Баттерворт
BE2   = (SKRecipe(1.274, 0.5774),)                        # Бессель
CH2_1 = (SKRecipe(0.863, 0.9565),)                        # Чебишев 1 дБ

# ── Четвертий порядок: дві ланки, нижчий Q першим ────────────────────────
BW4    = (SKRecipe(1.000, 0.5412), SKRecipe(1.000, 1.3066))
BE4    = (SKRecipe(1.432, 0.5219), SKRecipe(1.606, 0.8055))
CH4_05 = (SKRecipe(0.597, 0.7051), SKRecipe(1.031, 2.9406))  # 0.5 дБ
CH4_1  = (SKRecipe(0.529, 0.7846), SKRecipe(0.993, 3.5600))  # 1 дБ

FT_BW4   = SKFilterType("Баттерворт-4", BW4, 4)
FT_BE4   = SKFilterType("Бессель-4", BE4, 4)
FT_CH4_1 = SKFilterType("Чебишев-4 (1 дБ)", CH4_1, 4)
