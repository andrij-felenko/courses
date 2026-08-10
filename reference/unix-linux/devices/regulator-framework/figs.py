import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

def draw_regulator_tree():
    # Дерево живлення так, як його описує проза: батарея → PMIC → головний DC-DC на 3.3 V →
    # від нього два LDO (1.8 V сенсорам, 1.2 V інтерфейсам). Батьківсько-дочірній звʼязок у ядрі —
    # це поле rdev->supply (drivers/regulator/core.c), у Device Tree — властивість vin-supply
    # (Documentation/devicetree/bindings/regulator/regulator.yaml, patternProperties ".*-supply$").
    w, h = 860, 440

    frags = []

    # Джерело — системна батарея
    bat, bw, bh = textbox(72, 225, "Батарея\n3.7–4.2 V", fill="#fdecea")
    frags.append(bat)

    # Корпус PMIC
    frags.append(rect(150, 60, 400, 340, fill="#f0f0f0", stroke=LINE, rx=10))
    frags.append(text(350, 88, "PMIC — мікросхема керування живленням", size=13, bold=True))

    # Батько: головний імпульсний перетворювач
    buck1, kw1, kh1 = textbox(240, 225, "BUCK1 (DC-DC)\nVSYS = 3.3 V", fill=FILL)
    # Нащадки: два LDO, які живляться від BUCK1
    ldo1, lw1, lh1 = textbox(440, 150, "LDO1 (LDO)\nVCC_SENSOR = 1.8 V", fill=FILL)
    ldo2, lw2, lh2 = textbox(440, 310, "LDO2 (LDO)\nVCC_IO = 1.2 V", fill=FILL)
    frags.extend([buck1, ldo1, ldo2])

    # Споживачі — поза корпусом PMIC
    sensor, sw, sh = textbox(760, 150, "Сенсор\n(споживач)", fill="#e6f7ff")
    emmc, ew, eh = textbox(760, 310, "eMMC I/O\n(споживач)", fill="#e6f7ff")
    frags.extend([sensor, emmc])

    # Батарея живить вхід PMIC
    frags.append(arrow(72 + bw / 2, 225, 240 - kw1 / 2, 225))

    # Внутрішня шина 3.3 V: від BUCK1 до обох LDO — саме це і є батьківське джерело
    frags.append(line(240 + kw1 / 2, 225, 330, 225))
    frags.append(line(330, 150, 330, 310))
    frags.append(arrow(330, 150, 440 - lw1 / 2, 150))
    frags.append(arrow(330, 310, 440 - lw2 / 2, 310))
    frags.append(mtext(250, 300, "батьківське джерело\nдля обох LDO", size=12, color=MUTED))

    # Виходи LDO до своїх споживачів
    frags.append(arrow(440 + lw1 / 2, 150, 760 - sw / 2, 150))
    frags.append(arrow(440 + lw2 / 2, 310, 760 - ew / 2, 310))
    frags.append(text(640, 138, "regulator_enable()", size=12, color=MUTED))
    frags.append(text(640, 298, "regulator_enable()", size=12, color=MUTED))

    frags.append(text(380, 425, "У Device Tree звʼязок задає vin-supply = <&buck1> у вузлах LDO1 і LDO2",
                      size=12, color=MUTED))

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
    os.makedirs(out_dir, exist_ok=True)
    render(os.path.join(out_dir, "regulator-tree.svg"), w, h, *frags,
           title="Дерево живлення: батарея → PMIC → BUCK1 (3.3 V) → LDO1/LDO2")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    draw_regulator_tree()
