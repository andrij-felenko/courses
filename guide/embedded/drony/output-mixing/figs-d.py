# -*- coding: utf-8 -*-
"""Фігури до ДЕТАЛЬНОЇ теми «Узгодження сигналів керування».
Запуск:  python figs-d.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Окремо від figs.py (той — для базової версії)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Мікшер як матриця: вектор команд × матриця → вектор виходів ─────────────
def fig_mixer_matrix():
    """Бажаний рух (roll/pitch/yaw/throttle) множиться на матрицю коефіцієнтів
    і дає вектор виходів. Рядок — один вихід, стовпець — одна вісь керування.
    Уся геометрія апарата стиснута в числа матриці."""
    W, H = 820, 380
    f = [text(W / 2, 30, "Мікшер — це множення вектора команд на матрицю", size=17, bold=True)]

    # вектор команд (ліворуч)
    cmds = ["roll", "pitch", "yaw", "thr"]
    cx0, cy0 = 90, 110
    f.append(text(cx0, cy0 - 16, "бажаний рух", size=12, bold=True, color=FIELD))
    for i, c in enumerate(cmds):
        yy = cy0 + i * 46
        f.append(rect(cx0 - 44, yy, 88, 38, fill="#eef6ef", stroke=FIELD, sw=1.3))
        f.append(text(cx0, yy + 24, c, size=13, bold=True, color=FIELD))
    f.append(text(cx0, cy0 + 4 * 46 + 26, "(вектор)", size=10, color=MUTED))

    f.append(text(cx0 + 70, cy0 + 2 * 46 + 2, "×", size=22, bold=True, color=INK))

    # матриця коефіцієнтів (центр) — приклад квадрокоптера-X
    mx0, my0 = 250, 110
    f.append(text(mx0 + 150, my0 - 16, "матриця коефіцієнтів (геометрія апарата)",
                  size=12, bold=True, color=POS, anchor="middle"))
    rows = [("-1", "+1", "+1", "+1"),
            ("-1", "-1", "-1", "+1"),
            ("+1", "+1", "-1", "+1"),
            ("+1", "-1", "+1", "+1")]
    cw, rh = 66, 46
    f.append(rect(mx0 - 6, my0 - 6, cw * 4 + 12, rh * 4 + 12, fill="#fbeee6", stroke=POS, sw=1.6))
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            xx = mx0 + c * cw + cw / 2
            yy = my0 + r * rh + rh / 2 + 5
            col = POS if val.startswith("+") else NEG
            f.append(text(xx, yy, val, size=14, bold=True, color=col))
    # підписи стовпців знизу
    for c, lab in enumerate(cmds):
        f.append(text(mx0 + c * cw + cw / 2, my0 + rh * 4 + 22, lab, size=10, color=MUTED))

    f.append(text(mx0 + cw * 4 + 26, my0 + 2 * rh + 2, "=", size=22, bold=True, color=INK))

    # вектор виходів (праворуч)
    ox0 = mx0 + cw * 4 + 60
    f.append(text(ox0 + 44, my0 - 16, "виходи", size=12, bold=True, color=INK))
    for i in range(4):
        yy = my0 + i * rh
        f.append(rect(ox0, yy, 128, 38, fill=BG, stroke=LINE, sw=1.3))
        f.append(text(ox0 + 64, yy + 24, "мотор %d" % (i + 1), size=12, bold=True))

    f.append(text(W / 2, H - 18,
                  "рядок = один вихід · стовпець = одна вісь · kᵢⱼ = наскільки вихід i слухає вісь j",
                  size=12, color=INK))
    return render(os.path.join(IMG, "mixer-matrix.svg"), W, H, *f)


# ── 2. Насичення: наївне обрізання vs зсув спільного рівня ─────────────────────
def fig_saturation():
    """Два способи впоратися з насиченням виходу. Наївне обрізання зменшує
    різницю між моторами й краде крен. Зсув усіх виходів на спільний надлишок
    зберігає різницю, жертвуючи лише загальною тягою."""
    W, H = 840, 420
    f = [text(W / 2, 30, "Насичення: обрізати покомпонентно чи зсунути всіх?", size=17, bold=True)]

    def bars(ox, title, vals, clipped_idx, note, note_col):
        # шкала 0..1.4, стеля на 1.0
        base_y, top_y = 300, 90
        scale = (base_y - top_y) / 1.4
        f.append(text(ox + 130, 66, title, size=13, bold=True))
        # вісь і стеля
        f.append(line(ox, base_y, ox + 300, base_y, color=LINE, sw=1.4))
        ceil_y = base_y - 1.0 * scale
        f.append(line(ox, ceil_y, ox + 300, ceil_y, color=POS, sw=1.4, dash="6 4"))
        f.append(text(ox + 300, ceil_y - 6, "стеля 1.0", size=10, color=POS, anchor="end"))
        labs = ["прав", "прав", "лів", "лів"]
        for i, v in enumerate(vals):
            bx = ox + 24 + i * 68
            vis = min(v, 1.0) if i in clipped_idx else v
            col = NEG if i < 2 else FIELD
            # реальна (обрізана) частина
            f.append(rect(bx, base_y - vis * scale, 44, vis * scale,
                          fill=("#eaf0fd" if i < 2 else "#eafaf0"), stroke=col, sw=1.4, rx=3))
            # «загублена» частина (якщо обрізали) — пунктиром
            if i in clipped_idx and v > 1.0:
                f.append(rect(bx, base_y - v * scale, 44, (v - 1.0) * scale,
                              fill="none", stroke=MUTED, sw=1.2, rx=3))
                f.append(line(bx, base_y - v * scale, bx + 44, base_y - v * scale,
                              color=MUTED, sw=1.0, dash="3 3"))
            f.append(text(bx + 22, base_y + 16, labs[i], size=10, color=MUTED))
            f.append(text(bx + 22, base_y - vis * scale - 6, "%.2f" % vis, size=10, bold=True, color=col))
        f.append(fitbox(ox + 10, 330, 300, 40, note, size=11, bold=True,
                        fill=FILL, stroke=note_col))

    bars(40, "наївне обрізання (clip)",
         [0.20, 0.20, 1.40, 1.40], [2, 3],
         "лівий уперся в 1.0 → різниця 1.20→0.80 → крен вкрадено", POS)
    bars(470, "зсув спільного рівня (desat)",
         [-0.20, -0.20, 1.00, 1.00], [],
         "усі зсунуто на −0.40 → різниця 1.20 збережена, впала лише тяга", FIELD)

    f.append(text(W / 2, H - 14,
                  "різниця між моторами = крен; зберегти різницю важливіше, ніж рівень тяги",
                  size=12, color=INK))
    return render(os.path.join(IMG, "saturation.svg"), W, H, *f)


# ── 3. Автомат перекосу H3-120: три серво, кожне = сума трьох команд ───────────
def fig_swashplate():
    """Три серво під 60/180/300° тримають тарілку. Хід кожного =
    C + P·cosθ + R·sinθ: загальний крок піднімає всі однаково, поздовжній
    гойдає заднє проти передніх, поперечний розводить бічні."""
    W, H = 820, 440
    f = [text(W / 2, 30, "Автомат перекосу H3-120: кожне серво = сума трьох команд", size=17, bold=True)]

    # кругла тарілка з трьома серво під 60/180/300°
    cx, cy, R = 230, 250, 120
    f.append(text(cx, 74, "розкладка серво (вид згори)", size=12, bold=True))
    f.append(text(cx, cy - R - 24, "↑ вперед (0°)", size=11, color=MUTED))
    f.append(circle(cx, cy, R, fill="#f4f6f8", stroke=LINE, sw=1.6))
    f.append(circle(cx, cy, 5, fill=INK, stroke=INK, sw=1))
    # осі
    f.append(line(cx, cy - R, cx, cy + R, color=MUTED, sw=1.0, dash="4 4"))
    f.append(line(cx - R, cy, cx + R, cy, color=MUTED, sw=1.0, dash="4 4"))
    servos = [(60, "A", POS), (180, "B", NEG), (300, "C", FIELD)]
    for ang, name, col in servos:
        # 0° угору, за годинниковою; екранний кут
        rad = math.radians(ang)
        sx = cx + R * math.sin(rad)
        sy = cy - R * math.cos(rad)
        f.append(circle(sx, sy, 15, fill="#fff", stroke=col, sw=2.4))
        f.append(text(sx, sy + 5, name, size=14, bold=True, color=col))
        f.append(text(sx + 18 * math.sin(rad), sy - 18 * math.cos(rad) + 4,
                      "%d°" % ang, size=10, color=MUTED,
                      anchor=("start" if math.sin(rad) > 0.1 else ("end" if math.sin(rad) < -0.1 else "middle"))))

    # формули праворуч
    fx = 470
    f.append(text(fx + 165, 74, "хід серво = C + P·cos θ + R·sin θ", size=13, bold=True, color=INK))
    lines = [
        ("серво A (60°)", "= C + 0.5·P + 0.866·R", POS),
        ("серво B (180°)", "= C − 1.0·P + 0.0·R", NEG),
        ("серво C (300°)", "= C + 0.5·P − 0.866·R", FIELD),
    ]
    for i, (lab, formula, col) in enumerate(lines):
        yy = 120 + i * 52
        f.append(rect(fx, yy, 330, 42, fill=BG, stroke=col, sw=1.4))
        f.append(text(fx + 12, yy + 26, lab, size=12, bold=True, color=col, anchor="start"))
        f.append(text(fx + 128, yy + 26, formula, size=12, anchor="start"))
    # легенда осей
    leg = ["C — загальний крок (усі три вгору однаково)",
           "P — поздовжній нахил (заднє проти передніх)",
           "R — поперечний нахил (бічні в різні боки)"]
    for i, s in enumerate(leg):
        f.append(text(fx, 300 + i * 22, s, size=11, color=MUTED, anchor="start"))

    f.append(text(W / 2, H - 16,
                  "коефіцієнти суми — це косинуси й синуси азимутів серво, а не магічні числа",
                  size=12, color=INK))
    return render(os.path.join(IMG, "swashplate.svg"), W, H, *f)


if __name__ == "__main__":
    fig_mixer_matrix()
    fig_saturation()
    fig_swashplate()
    print("OK: 3 фігури у", IMG)
