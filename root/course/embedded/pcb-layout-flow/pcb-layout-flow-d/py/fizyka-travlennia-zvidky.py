from dataclasses import dataclass

# Компенсація травлення: наскільки розширити малюнок доріжки,
# щоб ПІСЛЯ ізотропного підтраву вона вийшла цільової ширини.
# Усі величини — у мікрометрах.
@dataclass
class EtchComp:
    target_um: float    # цільова ширина готової доріжки
    draw_um: float      # ширина, яку слід намалювати (з компенсацією)
    undercut_um: float  # підтрав з одного боку

def etch_compensate(target_um,
                    copper_thickness_um,  # 35 = 1oz, 70 = 2oz
                    etch_factor):         # типово 2..4
    undercut_um = copper_thickness_um / etch_factor       # u = t / EF
    # готова = намальована − 2u  ⇒  намальована = цільова + 2u
    draw_um = target_um + 2.0 * undercut_um
    return EtchComp(target_um, draw_um, undercut_um)

# Приклад: хочемо готову доріжку 150 мкм на міді 1oz, EF=3
#   u        = 35 / 3      ≈ 11.7 мкм
#   малювати = 150 + 23.4  ≈ 173.4 мкм
# Тобто щоб отримати рівні 150 мкм, малюнок має бути ~173 мкм —
# цю поправку завод вносить сам, але тепер зрозуміло ЧОМУ вона є.
