# -*- coding: utf-8 -*-
"""Фігури до вставки «comp-hotair-station» (паяльний фен і станція гарячого повітря).
Запуск:  python comp-figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

SOLDER = "#9aa3ad"   # припій
PAD    = "#c98a2b"   # мідний майданчик
BODY   = "#3a4150"   # тіло компонента
HEAT   = POS         # тепло / гаряче
AIR    = "#2457d6"   # холодне повітря на вході


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.1 — Блок-схема станції: повітря → турбіна → нагрівник → сопло, з петлею керування
# ─────────────────────────────────────────────────────────────────────────────
def fig_block():
    W, H = 760, 320
    f = []
    f.append(text(W / 2, 26, "Що всередині станції гарячого повітря", size=17, bold=True))

    # ─ Тракт повітря: чотири блоки в ряд ─
    y = 90
    bh = 56
    boxes = [
        (40,  "Забір\nповітря",        FILL,  AIR),
        (210, "Турбіна\n(нагнітач)",   FILL,  INK),
        (390, "Нагрівник\n(спіраль)",  "#fdecea", HEAT),
        (570, "Сопло\n→ ціль",          FILL,  INK),
    ]
    bw = 130
    for x, label, fill, col in boxes:
        f.append(fitbox(x, y, bw, bh, label, size=13, fill=fill, color=col, bold=True))

    # стрілки потоку між блоками (холодне → гаряче за кольором)
    f.append(arrow(40 + bw, y + bh / 2, 210, y + bh / 2, color=AIR, sw=2.2))
    f.append(arrow(210 + bw, y + bh / 2, 390, y + bh / 2, color=INK, sw=2.2))
    f.append(arrow(390 + bw, y + bh / 2, 570, y + bh / 2, color=HEAT, sw=2.6))
    f.append(text(125, y - 8, "холодне", size=10, color=AIR))
    f.append(text(485, y - 8, "гаряче", size=10, color=HEAT))

    # термопара в потоці біля нагрівника
    tc_x, tc_y = 455, y + bh + 26
    f.append(circle(tc_x, tc_y, 7, fill="#fff7e6", stroke=HEAT, sw=1.6))
    f.append(text(tc_x, tc_y + 3, "T", size=11, bold=True, color=HEAT))
    f.append(line(455, y + bh, tc_x, tc_y - 7, color=HEAT, sw=1.2, dash="3,3"))
    f.append(text(tc_x + 70, tc_y + 4, "термопара в потоці", size=10, color=MUTED))

    # ─ Блок керування з двома незалежними петлями ─
    cy = 250
    f.append(rect(150, cy - 22, 300, 50, fill="#eef7f0", stroke=FIELD, sw=1.6, rx=8))
    f.append(text(300, cy - 4, "Керування", size=13, bold=True, color=FIELD))
    f.append(text(300, cy + 16, "уставка T  ·  уставка потоку", size=11, color=INK))

    # петля температури: термопара → керування → нагрівник
    f.append(arrow(tc_x, tc_y + 7, 360, cy - 22, color=FIELD, sw=1.6))
    f.append(arrow(420, cy - 22, 430, y + bh, color=HEAT, sw=1.6))
    f.append(text(530, cy - 30, "тримає T (зворотний зв'язок)", size=10, color=FIELD))

    # керування потоком → турбіна
    f.append(arrow(230, cy - 22, 245, y + bh, color=INK, sw=1.6))
    f.append(text(150, cy - 30, "задає потік", size=10, color=MUTED))

    render(os.path.join(IMG, "hotair-block.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.2 — Профіль нагрівання: чотири зони (прогрів · витримка · оплавлення · спад)
# ─────────────────────────────────────────────────────────────────────────────
def fig_profile():
    W, H = 760, 380
    f = []
    f.append(text(W / 2, 26, "Профіль температури: вести зонами, не бити одразу", size=17, bold=True))

    # осі
    ox, oy = 70, 300            # початок координат
    ax, ay = 700, 60           # кінець осей
    f.append(line(ox, oy, ax, oy, color=LINE, sw=1.6))   # час →
    f.append(line(ox, oy, ox, ay, color=LINE, sw=1.6))   # T ↑
    f.append(text(ax - 8, oy + 22, "час →", size=12, color=INK, anchor="end"))
    f.append(text(ox - 50, ay + 6, "T, °C", size=12, color=INK, anchor="start"))

    # рівні температур (горизонтальні пунктири)
    def ylvl(t):  # 25..260 °C → піксель
        return oy - (t - 25) * (oy - ay) / (260 - 25)

    for t, lab in [(183, "183 — оплавлення (Sn63Pb37)"), (150, "150 — низ витримки")]:
        yy = ylvl(t)
        f.append(line(ox, yy, ax - 120, yy, color="#d0d4d9", sw=1.0, dash="4,4"))
        f.append(text(ax - 116, yy + 4, lab, size=10, color=MUTED, anchor="start"))

    # точки профілю: (час, T)
    pts_t = [0, 90, 90, 180, 180, 235, 235, 300]
    # відповідні температури — прогрів, витримка, стрибок до піка, спад
    pts_T = [25, 150, 150, 175, 175, 215, 215, 70]
    # будуємо плавну ламану по ключових вузлах
    nodes = [(0, 25), (90, 150), (180, 175), (215, 215), (235, 205), (300, 70)]

    def px(tt):
        return ox + tt * (ax - ox) / 300

    d = "M %.1f %.1f" % (px(nodes[0][0]), ylvl(nodes[0][1]))
    for tt, TT in nodes[1:]:
        d += " L %.1f %.1f" % (px(tt), ylvl(TT))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, HEAT))

    # межі зон (вертикальні лінії) і підписи зон
    zones = [
        (0, 90,   "прогрів", "≤ 3 °C/с"),
        (90, 180, "витримка", "150–200 °C, 60–120 с"),
        (180, 235, "оплавлення", "пік +20…30 °C"),
        (235, 300, "спад", "контрольовано"),
    ]
    for a, b, name, note in zones:
        f.append(line(px(b), oy, px(b), ay + 10, color="#c8ccd1", sw=1.0, dash="2,3"))
        midx = px((a + b) / 2)
        f.append(text(midx, ay - 2, name, size=12, bold=True, color=INK))
        f.append(text(midx, ay + 14, note, size=9.5, color=MUTED))

    # позначка піка
    f.append(circle(px(215), ylvl(215), 4, fill=HEAT, stroke=HEAT, sw=1))
    f.append(text(px(215) + 6, ylvl(215) - 8, "пік", size=10, bold=True, color=HEAT, anchor="start"))

    # нижній підпис-висновок
    f.append(text(W / 2, 360,
                  "Плата йде до оплавлення поступово: різкий стрибок дав би тепловий удар і popcorn-ефект.",
                  size=11, color=INK))
    render(os.path.join(IMG, "reflow-profile.svg"), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# Фіг.3 — Чому нижній підігрів: тонкий перепад верх/низ деформує плату
# ─────────────────────────────────────────────────────────────────────────────
def fig_preheat():
    W, H = 760, 340
    f = []
    f.append(text(W / 2, 26, "Нижній підігрів: прибрати перепад верх↔низ", size=17, bold=True))

    def chip_on_board(cx, cy, warp=0.0):
        # плата (можливо вигнута), майданчики, корпус BGA з кульками
        bw, bh = 260, 18
        x0 = cx - bw / 2
        if abs(warp) < 0.5:
            f.append(rect(x0, cy, bw, bh, fill="#e7eaee", stroke=LINE, sw=1.3, rx=3))
            edge_y = cy
        else:
            # вигнута плата — дуга
            d = ('M %.1f %.1f Q %.1f %.1f %.1f %.1f L %.1f %.1f Q %.1f %.1f %.1f %.1f Z'
                 % (x0, cy, cx, cy + warp, x0 + bw, cy,
                    x0 + bw, cy + bh, cx, cy + bh + warp, x0, cy + bh))
            f.append('<path d="%s" fill="#e7eaee" stroke="%s" stroke-width="1.3"/>' % (d, LINE))
            edge_y = cy
        # корпус BGA
        f.append(rect(cx - 55, cy - 34, 110, 30, fill=BODY, stroke=LINE, sw=1.2, rx=3))
        # кульки під корпусом
        for i in range(7):
            bx = cx - 48 + i * 16
            # у вигнутій платі крайні кульки відходять від майданчика
            lift = 0 if abs(warp) < 0.5 else max(0, (abs(bx - cx) - 14)) * 0.10
            f.append(circle(bx, cy - 2 - lift, 4.5, fill=SOLDER, stroke=LINE, sw=0.9))
        return edge_y

    # ── Ліва панель: лише верхній фен, холодний низ ──
    Lx = 200
    f.append(text(Lx, 64, "лише верхній потік", size=13, bold=True, color=POS))
    chip_on_board(Lx, 170, warp=26)
    # гарячий потік згори
    for dx in (-20, 0, 20):
        f.append(arrow(Lx + dx, 92, Lx + dx, 128, color=HEAT, sw=2.0))
    f.append(text(Lx, 84, "≈ 350 °C", size=10, color=HEAT))
    # холодний низ
    f.append(text(Lx, 250, "низ холодний", size=11, color=AIR))
    f.append(text(Lx, 270, "перепад крізь плату", size=11, color=POS))
    f.append(text(Lx, 290, "→ вигин, відрив кульок", size=11, bold=True, color=POS))

    # ── Права панель: верхній фен + нижній підігрів ──
    Rx = 560
    f.append(text(Rx, 64, "верхній + нижній підігрів", size=13, bold=True, color=FIELD))
    chip_on_board(Rx, 170, warp=0)
    for dx in (-20, 0, 20):
        f.append(arrow(Rx + dx, 92, Rx + dx, 128, color=HEAT, sw=2.0))
    f.append(text(Rx, 84, "≈ 350 °C", size=10, color=HEAT))
    # нижній підігрів — широка тепла зона під платою
    f.append(rect(Rx - 150, 200, 300, 16, fill="#fdecea", stroke=HEAT, sw=1.3, rx=4))
    for dx in (-90, -45, 0, 45, 90):
        f.append(arrow(Rx + dx, 200, Rx + dx, 190, color=HEAT, sw=1.6))
    f.append(text(Rx, 234, "низ прогрітий до ≈150 °C", size=11, color=FIELD))
    f.append(text(Rx, 254, "малий перепад", size=11, color=FIELD))
    f.append(text(Rx, 274, "→ плата рівна, кульки на місці", size=11, bold=True, color=FIELD))

    # роздільник
    f.append(line(W / 2 - 20, 56, W / 2 - 20, 300, color="#d0d4d9", sw=1.0, dash="4,4"))
    render(os.path.join(IMG, "bottom-preheat.svg"), W, H, *f)


if __name__ == "__main__":
    fig_block()
    fig_profile()
    fig_preheat()
    print("OK: 3 фігури у", IMG)
