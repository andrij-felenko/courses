# -*- coding: utf-8 -*-
"""Фігури для вставки comp-ssr.md (твердотільне реле і dv/dt).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_ssr_inside():
    """Внутрішня будова AC-SSR: вхід-LED → зеро-крос опто-драйвер → силовий
    симістор → внутрішній RC-снабер. Показує, де саме живе чутливість до dv/dt
    і куди ставлять снабер усередині корпусу."""
    W, H = 880, 430
    f = []

    # бар'єр ізоляції — вертикальна штрихова смуга по центру
    bx = 360
    f.append(line(bx, 70, bx, H - 50, color=MUTED, sw=2, dash="7 6"))
    f.append(text(bx, H - 32, "бар'єр ізоляції (оптичний)", size=12, color=MUTED))

    # підписи двох боків
    f.append(text(180, 60, "бік керування (DC, 3–32 В)", size=13, color=NEG, bold=True))
    f.append(text(625, 60, "силовий бік (мережа AC)", size=13, color=POS, bold=True))

    # ── вхід керування ──
    b1, w1, h1 = textbox(150, 150, "вхідний\nсвітлодіод", size=13,
                         fill="#eaf0fd", stroke=NEG, sw=2)
    f.append(b1)
    f.append(plus(70, 135))
    f.append(minus(70, 170))
    f.append(line(82, 135, 150 - w1 / 2, 150, color=NEG))
    f.append(line(82, 170, 150 - w1 / 2, 150, color=NEG))

    # промінь світла через бар'єр
    f.append(arrow(150 + w1 / 2, 150, 470, 150, color=FIELD, sw=2.2))
    f.append(text(330, 138, "світло", size=11, color=FIELD, italic=True))

    # ── опто-драйвер із зеро-кросом (силовий бік, але мала потужність) ──
    b2 = fitbox(470, 110, 200, 84,
                "опто-симістор\n+ детектор нуля\n(MOC304x-клас)",
                size=13, fill="#fdecea", stroke=POS, sw=2)
    f.append(b2)

    # ── силовий симістор ──
    tcx, tcy = 540, 310
    b3, w3, h3 = textbox(tcx, tcy, "силовий\nсимістор", size=14,
                         fill="#fdecea", stroke=POS, sw=2.4)

    # від драйвера — в затвор силового симістора (заходить ЗЛІВА, не плутаючись
    # із силовими клемами зверху/знизу)
    f.append(line(570, 194, 570, 224, color=POS, sw=2))
    f.append(line(570, 224, tcx - w3 / 2 - 36, 224, color=POS, sw=2))
    f.append(arrow(tcx - w3 / 2 - 36, 224, tcx - w3 / 2 - 36, tcy, color=POS, sw=2))
    f.append(line(tcx - w3 / 2 - 36, tcy, tcx - w3 / 2, tcy, color=POS, sw=2))
    f.append(text(tcx - w3 / 2 - 36, 214, "у затвор", size=11, color=POS, italic=True))

    f.append(b3)

    # силові клеми (до мережі й навантаження)
    f.append(line(tcx, tcy - h3 / 2, tcx, tcy - h3 / 2 - 26, color=POS, sw=2.4))
    f.append(text(tcx, tcy - h3 / 2 - 32, "до мережі", size=11, color=POS))
    f.append(line(tcx, tcy + h3 / 2, tcx, 392, color=POS, sw=2.4))
    f.append(text(tcx, 408, "до навантаження", size=11, color=POS))

    # ── внутрішній RC-снабер паралельно силовому симістору ──
    sx = 740
    # вузли підключення зверху/знизу симістора
    ytop, ybot = tcy - h3 / 2 - 16, tcy + h3 / 2 + 16
    f.append(line(tcx, ytop, sx, ytop, color=LINE, sw=1.6))
    f.append(line(tcx, ybot, sx, ybot, color=LINE, sw=1.6))
    f.append(line(sx, ytop, sx, tcy - 30, color=LINE, sw=1.6))
    f.append(line(sx, tcy + 30, sx, ybot, color=LINE, sw=1.6))
    bs = fitbox(sx - 52, tcy - 30, 104, 60, "R + C\nснабер", size=12,
                fill=FILL, stroke=LINE, sw=1.6)
    f.append(bs)

    cap = ("Внутрішня будова AC-SSR. Логічний бік (синій) — лише світлодіод; "
           "силовий бік (червоний) — опто-симістор із детектором нуля, що керує "
           "силовим симістором. Саме силовий симістор латчиться, тож саме він "
           "чутливий до dv/dt; кращі SSR містять внутрішній RC-снабер просто "
           "паралельно йому.")
    render(os.path.join(IMG, "ssr-inside.svg"), W, H, *f,
           title="Що всередині твердотільного реле")
    return cap


if __name__ == "__main__":
    print(fig_ssr_inside())
    print("Готово:", IMG)
