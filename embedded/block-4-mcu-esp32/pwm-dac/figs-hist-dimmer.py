# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для 📜 Історії до Розділу 4.7 «PWM і ЦАП»:
«Як приборкали яскравість: від реостата до тиристорного диммера й до ШІМ»

Фігури:
  fig-25-0-1-rheostat-heat   — схема реостат+лампа, потоки потужності
  fig-25-0-2-phase-control   — фазове керування: синусоїда з відрізаним початком

Вивід → ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Реостат у послідовнику з лампою — куди тече потужність
# ─────────────────────────────────────────────────────────────────────────────
def fig_rheostat_heat():
    W, H = 700, 360
    parts = []

    # Фон
    parts.append(rect(0, 0, W, H, fill=BG, stroke="none", sw=0, rx=0))

    # Заголовок
    parts.append(text(W/2, 30, "Реостат у послідовнику з лампою: куди тече потужність",
                      size=15, bold=True))

    # ── Блоки схеми ─────────────────────────────────────────────────────────
    # Розетка (джерело)
    src_cx, src_cy = 80, 160
    parts.append(circle(src_cx, src_cy, 36, fill="#e8f0fe", stroke=NEG, sw=2.0))
    parts.append(text(src_cx, src_cy - 6, "~", size=22, color=NEG, bold=True))
    parts.append(text(src_cx, src_cy + 14, "230 В", size=11, color=MUTED))

    # Реостат (змінний резистор) — прямокутник зі стрілкою
    rh_cx, rh_cy = 280, 160
    rh_w, rh_h = 110, 50
    parts.append(rect(rh_cx - rh_w/2, rh_cy - rh_h/2, rh_w, rh_h,
                      fill="#fff3cd", stroke="#e0a000", sw=2.0))
    parts.append(text(rh_cx, rh_cy - 6, "Реостат", size=13, bold=True))
    parts.append(text(rh_cx, rh_cy + 10, "(змінний R)", size=11, color=MUTED))
    # Стрілка-покажчик (символ регулювання)
    parts.append(line(rh_cx - 18, rh_cy - rh_h/2 - 12,
                      rh_cx + 18, rh_cy - rh_h/2 - 12, color="#e0a000", sw=1.5))
    parts.append(arrow(rh_cx - 18, rh_cy - rh_h/2 - 12,
                       rh_cx + 14, rh_cy - rh_h/2 - 12, color="#e0a000", sw=1.5))

    # Лампа (кола + хрест)
    lamp_cx, lamp_cy = 520, 160
    lamp_r = 34
    parts.append(circle(lamp_cx, lamp_cy, lamp_r, fill="#fffde7", stroke="#f9a825", sw=2.2))
    # Хрестик нитки
    d = 14
    parts.append(line(lamp_cx - d, lamp_cy - d, lamp_cx + d, lamp_cy + d,
                      color="#f9a825", sw=2.2))
    parts.append(line(lamp_cx - d, lamp_cy + d, lamp_cx + d, lamp_cy - d,
                      color="#f9a825", sw=2.2))
    parts.append(text(lamp_cx, lamp_cy + lamp_r + 16, "Лампа", size=13, bold=True))

    # ── Дроти (горизонталь) ───────────────────────────────────────────────
    # зверху: розетка → реостат → лампа
    y_top = 160 - 4
    parts.append(line(src_cx + 36, y_top, rh_cx - rh_w/2, y_top, color=LINE, sw=2.0))
    parts.append(line(rh_cx + rh_w/2, y_top, lamp_cx - lamp_r, y_top, color=LINE, sw=2.0))
    # знизу: замикальний провід
    y_bot = 260
    parts.append(line(src_cx, src_cy + 36, src_cx, y_bot, color=LINE, sw=2.0))
    parts.append(line(src_cx, y_bot, lamp_cx, y_bot, color=LINE, sw=2.0))
    parts.append(line(lamp_cx, lamp_cy + lamp_r, lamp_cx, y_bot, color=LINE, sw=2.0))

    # ── Стрілки потужності ────────────────────────────────────────────────
    # З розетки → стрілка вправо (загальна потужність)
    parts.append(arrow(src_cx + 36, y_top, src_cx + 80, y_top, color=LINE, sw=2.0))

    # Від реостата вгору: тепло
    heat_x = rh_cx
    parts.append(arrow(heat_x, rh_cy - rh_h/2,
                       heat_x, rh_cy - rh_h/2 - 55, color=POS, sw=2.0))
    tb, _, _ = textbox(heat_x, rh_cy - rh_h/2 - 75,
                       "≈50 % → ТЕПЛО\n(марна втрата)",
                       size=12, fill="#fde8e8", stroke=POS, sw=1.5)
    parts.append(tb)

    # До лампи → стрілка вправо і вниз (світло)
    parts.append(arrow(rh_cx + rh_w/2, y_top, lamp_cx - lamp_r - 5, y_top,
                       color=FIELD, sw=2.0))
    tb2, _, _ = textbox(lamp_cx, lamp_cy - lamp_r - 40,
                        "≈50 % → СВІТЛО",
                        size=12, fill="#e8f6ec", stroke=FIELD, sw=1.5)
    parts.append(tb2)

    # Підпис «від розетки»
    parts.append(text(src_cx + 100, y_top - 14, "100 % від розетки", size=11, color=MUTED))

    # ── Висновок внизу ───────────────────────────────────────────────────
    concl = fitbox(20, 298, W - 40, 46,
                   "Щоб удвічі притлумити лампу, реостат сам розсіює ≈ стільки ж тепла — він стає нагрівачем.",
                   size=12, fill="#f4f6f8", stroke=MUTED, sw=1.2)
    parts.append(concl)

    render(os.path.join(OUT, "fig-25-0-1-rheostat-heat.svg"), W, H, *parts)
    print("  fig-25-0-1-rheostat-heat.svg  OK")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Фазове керування — три сценарії відкриття тиристора
# ─────────────────────────────────────────────────────────────────────────────
def fig_phase_control():
    W, H = 720, 420
    parts = []
    parts.append(rect(0, 0, W, H, fill=BG, stroke="none", sw=0, rx=0))

    parts.append(text(W/2, 28, "Фазове керування: тиристор відрізає частину кожної хвилі",
                      size=15, bold=True))

    # ── Три ряди: рано / посередині / пізно ──────────────────────────────
    scenarios = [
        ("Рано  (кут ≈30°)",  0.15,  "≈90 % потужності", FIELD,   "#e8f6ec"),
        ("Посеред (кут ≈90°)", 0.50, "≈50 % потужності", "#e8a000","#fff3cd"),
        ("Пізно  (кут≈145°)", 0.82,  "≈10 % потужності", POS,     "#fde8e8"),
    ]

    row_y  = [80, 200, 320]
    y_mid  = 50   # відносний центр хвилі всередині рядка
    row_h  = 80   # висота хвилі (±40)

    xs_start = 130  # X початку синусоїди
    xs_end   = 660  # X кінця синусоїди
    period   = (xs_end - xs_start)  # один повний період

    for i, (label, fire_frac, pwr_label, line_color, fill_color) in enumerate(scenarios):
        y0 = row_y[i]
        cy = y0 + y_mid

        # Підпис сценарію зліва
        parts.append(text(xs_start - 10, cy + 5, label, size=11, anchor="end", color=INK))

    # Ось часу
        parts.append(line(xs_start, cy, xs_end, cy, color=MUTED, sw=1.0, dash="4,3"))

        # Синусоїда за один повний цикл — будуємо через path
        # x: xs_start..xs_end, y: cy - row_h/2 * sin(...)
        n_pts = 200
        fire_x = xs_start + fire_frac * period  # X точки підпалу

        # 1) «Відрізана» ліва частина (ключ закритий) — штрихова лінія + сіре заповнення
        path_cut = []
        for k in range(n_pts + 1):
            x = xs_start + k / n_pts * period
            if x > fire_x:
                break
            angle = (k / n_pts) * 2 * math.pi
            y = cy - (row_h / 2) * math.sin(angle)
            if k == 0:
                path_cut.append(f"M {x:.1f} {y:.1f}")
            else:
                path_cut.append(f"L {x:.1f} {y:.1f}")
        if path_cut:
            # закрити вниз до осі й назад
            path_cut.append(f"L {fire_x:.1f} {cy:.1f}")
            path_cut.append(f"L {xs_start:.1f} {cy:.1f} Z")
            parts.append(f'<path d="{" ".join(path_cut)}" fill="#eeeeee" stroke="none" opacity="0.7"/>')

        # Штрихова крива «закритої» частини
        path_dashed = []
        for k in range(n_pts + 1):
            x = xs_start + k / n_pts * period
            if x > fire_x + 2:
                break
            angle = (k / n_pts) * 2 * math.pi
            y = cy - (row_h / 2) * math.sin(angle)
            if k == 0:
                path_dashed.append(f"M {x:.1f} {y:.1f}")
            else:
                path_dashed.append(f"L {x:.1f} {y:.1f}")
        if path_dashed:
            parts.append(f'<path d="{" ".join(path_dashed)}" fill="none" '
                         f'stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="5,4"/>')

        # 2) «Провідна» частина (ключ відкритий) — яскрава заповнена крива
        path_cond = []
        for k in range(n_pts + 1):
            x = xs_start + k / n_pts * period
            if x < fire_x:
                continue
            angle = (k / n_pts) * 2 * math.pi
            y = cy - (row_h / 2) * math.sin(angle)
            if not path_cond:
                path_cond.append(f"M {x:.1f} {cy:.1f} L {x:.1f} {y:.1f}")
            else:
                path_cond.append(f"L {x:.1f} {y:.1f}")
        path_cond.append(f"L {xs_end:.1f} {cy:.1f} Z")
        if path_cond:
            parts.append(f'<path d="{" ".join(path_cond)}" fill="{fill_color}" '
                         f'stroke="none" opacity="0.85"/>')

        # Жирна крива провідної частини
        path_cond2 = []
        for k in range(n_pts + 1):
            x = xs_start + k / n_pts * period
            if x < fire_x:
                continue
            angle = (k / n_pts) * 2 * math.pi
            y = cy - (row_h / 2) * math.sin(angle)
            if not path_cond2:
                path_cond2.append(f"M {x:.1f} {y:.1f}")
            else:
                path_cond2.append(f"L {x:.1f} {y:.1f}")
        if path_cond2:
            parts.append(f'<path d="{" ".join(path_cond2)}" fill="none" '
                         f'stroke="{line_color}" stroke-width="2.5"/>')

        # Вертикальна позначка «підпалу» (червона пунктирна)
        parts.append(line(fire_x, cy - row_h/2 - 8, fire_x, cy + 10,
                          color=POS, sw=1.8, dash="4,3"))
        # Мітка «підпал» або «відкриття»
        parts.append(text(fire_x + 3, cy - row_h/2 - 12, "↑ підпал", size=9,
                          color=POS, anchor="start"))

        # Підпис потужності справа
        tb, _, _ = textbox(xs_end + 28, cy, pwr_label, size=11,
                           fill=fill_color, stroke=line_color, sw=1.5, min_w=90)
        parts.append(tb)

    # ── Вісь X та підписи ────────────────────────────────────────────────
    parts.append(arrow(xs_start - 5, 380, xs_end + 20, 380, color=MUTED, sw=1.5))
    parts.append(text(xs_end + 22, 380 + 5, "час", size=11, color=MUTED, anchor="start"))

    # ── Підпис-зв'язка внизу ────────────────────────────────────────────
    concl = fitbox(20, 390, W - 40, 22,
                   "Лампа отримує повну напругу лише частку часу — це і є ШІМ на частоті мережі (пор. §4.7.1).",
                   size=10, fill="#f0f4ff", stroke="#8090c0", sw=1.0, rx=4)
    parts.append(concl)

    render(os.path.join(OUT, "fig-25-0-2-phase-control.svg"), W, H, *parts)
    print("  fig-25-0-2-phase-control.svg  OK")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Генерую фігури для ch25-history-dimmer …")
    fig_rheostat_heat()
    fig_phase_control()
    print("Готово.")
