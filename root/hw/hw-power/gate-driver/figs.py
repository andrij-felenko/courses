# -*- coding: utf-8 -*-
"""Фігури до статті «Драйвер затвора» (book/electronics/power-electronics/gate-driver):
  - push-pull.svg  — тотемний (двотактний) вихід драйвера
  - bootstrap.svg  — плаваюче живлення верхнього затвора (бутстреп)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── фіг. 1. Тотемний (двотактний) вихід ──────────────────────────────────────
def fig_push_pull():
    W, H = 720, 360
    f = [text(W / 2, 28, "Двотактний вихід драйвера: влити й відсмоктати заряд", size=16, bold=True)]

    # логічний вхід (мА) ліворуч
    f.append(rect(30, 150, 110, 60, fill="#eef2f7", stroke=LINE, sw=1.6))
    f.append(text(85, 176, "лог. вхід", size=12, bold=True))
    f.append(text(85, 196, "(мА)", size=11, color=MUTED))
    f.append(arrow(140, 180, 214, 180, color=INK, sw=2))

    # корпус драйвера
    dx, dy, dw, dh = 214, 70, 250, 220
    f.append(rect(dx, dy, dw, dh, fill=BG, stroke="#c9d3dc", sw=1.6))
    f.append(text(dx + dw / 2, dy - 8, "драйвер", size=13, bold=True))

    midx = dx + dw / 2
    # шина живлення затвора Vdrive (зверху, червона) і земля (знизу)
    f.append(line(dx + 40, 96, dx + dw - 40, 96, color=POS, sw=2.4))
    f.append(text(midx, 88, "Vdrive (10–12 В)", size=11, color=POS, bold=True))
    f.append(line(dx + 40, 264, dx + dw - 40, 264, color=INK, sw=1.8))
    f.append(line(midx - 24, 264, midx + 24, 264, color=INK, sw=1.8))
    f.append(text(midx, 282, "GND", size=10, bold=True))

    # верхній ключ (наповнює)
    f.append(rect(midx - 34, 116, 68, 34, fill="#eafaf0", stroke=FIELD, sw=2))
    f.append(text(midx, 138, "верх", size=11, bold=True))
    # нижній ключ (спорожняє)
    f.append(rect(midx - 34, 196, 68, 34, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(midx, 218, "низ", size=11, bold=True))

    # стовпчик: Vdrive → верх → вузол → низ → GND
    f.append(line(midx, 96, midx, 116, color=INK, sw=2))
    f.append(line(midx, 150, midx, 173, color=INK, sw=2))   # верх → вузол
    f.append(line(midx, 173, midx, 196, color=INK, sw=2))   # вузол → низ
    f.append(line(midx, 230, midx, 264, color=INK, sw=2))
    f.append(circle(midx, 173, 3.2, fill=INK, stroke=INK, sw=1))

    # вихід → Rg → затвор
    f.append(line(midx, 173, dx + dw, 173, color=INK, sw=2))
    f.append(rect(dx + dw + 18, 161, 40, 24, fill=BG, stroke=INK, sw=1.6, rx=0))
    f.append(text(dx + dw + 38, 178, "Rg", size=11, bold=True))
    f.append(line(dx + dw + 58, 173, dx + dw + 100, 173, color=INK, sw=2))
    f.append(rect(dx + dw + 100, 150, 86, 48, fill="#fff5e8", stroke="#b5732e", sw=1.6))
    f.append(text(dx + dw + 143, 170, "затвор", size=10, bold=True))
    f.append(text(dx + dw + 143, 187, "MOSFET", size=9.5, color=MUTED))

    # напрями струму
    f.append(text(midx + 44, 134, "наповнює ↑", size=10, color=FIELD, anchor="start", bold=True))
    f.append(text(midx + 44, 216, "спорожняє ↓", size=10, color=NEG, anchor="start", bold=True))

    f.append(text(W / 2, 338,
                  "Вхід вмикає або верхній ключ (ллє ампери з Vdrive у затвор), або нижній (стягує заряд у землю).",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "push-pull.svg"), W, H, *f)


# ── фіг. 2. Бутстреп: плаваюче живлення верхнього затвора ─────────────────────
def fig_bootstrap():
    W, H = 720, 392
    f = [text(W / 2, 26, "Бутстреп: плаваюче живлення верхнього N-ключа", size=15, bold=True)]

    # силова шина (червона) і земля
    f.append(line(360, 64, 680, 64, color=POS, sw=2.4))
    f.append(text(520, 56, "+Vbus (висока шина)", size=11, color=POS, bold=True))
    f.append(line(220, 350, 680, 350, color=INK, sw=1.8))
    f.append(text(656, 366, "GND", size=10, bold=True))

    # верхній і нижній ключі півмоста
    f.append(rect(526, 92, 70, 48, fill="#eef2f7", stroke="#7f93a8", sw=1.8))
    f.append(text(561, 112, "Q_верх", size=10, bold=True))
    f.append(text(561, 128, "(N)", size=9.5, color=MUTED))
    f.append(rect(526, 240, 70, 48, fill="#eef2f7", stroke="#7f93a8", sw=1.8))
    f.append(text(561, 260, "Q_низ", size=10, bold=True))
    f.append(text(561, 276, "(N)", size=9.5, color=MUTED))

    f.append(line(561, 64, 561, 92, color=INK, sw=2))
    f.append(line(561, 140, 561, 206, color=INK, sw=2))   # витік верхнього → SW
    f.append(line(561, 206, 561, 240, color=INK, sw=2))   # SW → стік нижнього
    f.append(line(561, 288, 561, 350, color=INK, sw=2))
    f.append(circle(561, 206, 3.2, fill=INK, stroke=INK, sw=1))
    f.append(text(575, 201, "SW", size=10, anchor="start", bold=True))

    # навантаження праворуч від SW
    f.append(line(561, 206, 622, 206, color=INK, sw=2))
    f.append(rect(622, 182, 58, 48, fill=BG, stroke=INK, sw=1.6, rx=0))
    f.append(text(651, 202, "наван-", size=9.5))
    f.append(text(651, 216, "таження", size=9.5))
    f.append(line(651, 230, 651, 350, color=INK, sw=2))

    # Vdrive (низьковольтне живлення драйвера) ліворуч
    f.append(line(150, 150, 286, 150, color=POS, sw=2))
    f.append(text(150, 142, "Vdrive 12 В", size=10, color=POS, anchor="start", bold=True))

    # діод Dbs (трикутник + риска), вістрям праворуч (від Vdrive до VB)
    f.append('<path d="M 290,138 L 290,162 L 312,150 Z" fill="#dfe7f0" stroke="%s" stroke-width="1.6"/>' % INK)
    f.append(line(312, 138, 312, 162, color=INK, sw=2.5))
    f.append(text(301, 132, "Dbs", size=9.5, bold=True))
    f.append(line(312, 150, 430, 150, color=INK, sw=2))
    f.append(circle(430, 150, 3.2, fill=INK, stroke=INK, sw=1))
    f.append(text(430, 138, "VB", size=10, bold=True))

    # конденсатор Cbs (дві риски) між VB і SW
    f.append(line(430, 150, 430, 180, color=INK, sw=2))
    f.append(line(414, 184, 446, 184, color=INK, sw=2.6))
    f.append(line(414, 192, 446, 192, color=INK, sw=2.6))
    f.append(text(458, 191, "Cbs", size=9.5, anchor="start", bold=True))
    f.append(line(430, 196, 430, 206, color=INK, sw=2))
    f.append(line(430, 206, 561, 206, color=INK, sw=2))

    # верхній вихід HO (від VB) на затвор Q_верх
    f.append(line(430, 150, 430, 116, color=INK, sw=1.8))
    f.append(line(430, 116, 526, 116, color=INK, sw=1.8))
    f.append(text(478, 108, "HO (від VB)", size=9.5, color=FIELD, bold=True))
    # нижній вихід LO (від Vdrive) на затвор Q_низ
    f.append(text(522, 264, "← LO (від Vdrive)", size=9.5, color=NEG, anchor="end"))

    # пояснення двох фаз — у рамку, що сама вміщає текст
    body, bw, bh = textbox(195, 322, ["Q_низ ON: SW≈0, Cbs набирає заряд",
                                      "від Vdrive крізь Dbs.",
                                      "Q_верх ON: SW↑ до Vbus, Cbs їде",
                                      "вгору й піднімає VB над шиною."],
                           size=10, fill="#f6f8fb", stroke="#c9d3dc", sw=1.2, pad=9)
    f.append(body)

    render(os.path.join(IMG, "bootstrap.svg"), W, H, *f)


if __name__ == "__main__":
    fig_push_pull()
    fig_bootstrap()
    print("Готово: 2 фігури статті у", IMG)
