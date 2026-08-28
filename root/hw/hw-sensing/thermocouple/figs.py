# -*- coding: utf-8 -*-
"""Фігури до теми «Термопара».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

ALLOY_A = "#d9534f"   # Позитивний провідник (Хромель / Мідь / Залізо)
ALLOY_B = "#337ab7"   # Негативний провідник (Алюмель / Константан)
SHEATH  = "#78909c"   # Металева гільза
MGO_INS = "#fff9c4"   # Оксид магнію MgO


# ── 1. Фізика термопари: розподіл градієнта вздовж провідників ─────────────
def fig_seebeck_circuit():
    W, H = 760, 380
    f = [text(W / 2, 26, "Генерація термо-ЕРС вздовж температурного градієнта", size=16, bold=True)]

    # Гаряча зона (ліворуч)
    f.append(rect(30, 60, 160, 260, fill="#fbe9e7", stroke=POS, sw=1.5, rx=8))
    f.append(text(110, 85, "Гаряча зона", size=14, bold=True, color=POS))
    f.append(text(110, 105, "T_hot (робочий спай)", size=12, color=INK))

    # Холодна зона / ізотермічний блок (праворуч)
    f.append(rect(540, 60, 190, 260, fill="#e3f2fd", stroke=NEG, sw=1.5, rx=8))
    f.append(text(635, 85, "Холодна зона (CJC)", size=14, bold=True, color=NEG))
    f.append(text(635, 105, "T_cold (ізотермічна планка)", size=12, color=INK))

    # Спай гарячий (з'єднання двох металів)
    f.append(circle(110, 190, 8, fill="#ff7043", stroke=POS, sw=2))
    f.append(text(110, 218, "Робочий спай", size=11, bold=True, color=POS))

    # Провідник А (верхній)
    f.append(line(110, 190, 160, 150, color=ALLOY_A, sw=3.5))
    f.append(line(160, 150, 560, 150, color=ALLOY_A, sw=3.5))
    b_a, _, _ = textbox(350, 130, "Провідник A (наприклад, Хромель: S_A > 0)", size=11.5, fill=BG, stroke=ALLOY_A)
    f.append(b_a)

    # Провідник В (нижній)
    f.append(line(110, 190, 160, 230, color=ALLOY_B, sw=3.5))
    f.append(line(160, 230, 560, 230, color=ALLOY_B, sw=3.5))
    b_b, _, _ = textbox(350, 252, "Провідник B (наприклад, Алюмель: S_B < 0)", size=11.5, fill=BG, stroke=ALLOY_B)
    f.append(b_b)

    # Холодні спаї на клемах
    f.append(circle(560, 150, 6, fill=BG, stroke=INK, sw=2))
    f.append(circle(560, 230, 6, fill=BG, stroke=INK, sw=2))
    f.append(text(585, 145, "Клема (+)", size=11, bold=True, color=INK, anchor="start"))
    f.append(text(585, 225, "Клема (−)", size=11, bold=True, color=INK, anchor="start"))

    # Мідні доріжки та вольтметр
    f.append(line(560, 150, 650, 150, color="#d35400", sw=2, dash="4,3"))
    f.append(line(560, 230, 650, 230, color="#d35400", sw=2, dash="4,3"))
    f.append(line(650, 150, 650, 170, color="#d35400", sw=2))
    f.append(line(650, 230, 650, 210, color="#d35400", sw=2))

    # Блок АЦП / Вольтметр
    f.append(rect(620, 170, 60, 40, fill=BG, stroke=INK, sw=1.5, rx=4))
    f.append(text(650, 195, "АЦП", size=13, bold=True, color=INK))

    # Локальний давач температури холодного спаю
    f.append(rect(565, 270, 140, 36, fill="#ffffff", stroke=FIELD, sw=1.4, rx=5))
    f.append(text(635, 292, "Давач T_cold (NTC/RTD)", size=11, bold=True, color=FIELD))

    # Стрілка температурного градієнта
    f.append(arrow(210, 345, 510, 345, color=LINE, sw=2))
    f.append(text(360, 365, "Температурний градієнт dT/dx генерує напругу вздовж дротів", size=12, color=MUTED))

    render(os.path.join(IMG, "seebeck-circuit-gradient.svg"), W, H, *f)


# ── 2. Конструктивні типи спаїв ───────────────────────────────────────────
def fig_junction_types():
    W, H = 760, 390
    f = [text(W / 2, 26, "Конструктивні типи спаїв термопар у захисних гільзах", size=16, bold=True)]

    types = [
        ("1. Відкритий спай (Exposed)", 30, "#fff3e0",
         "Швидкість: τ < 0.1 с\nЗахист: відсутній\nІзоляція: немає\nЗастосування: чисті гази"),
        ("2. Заземлений спай (Grounded)", 270, "#e8f5e9",
         "Швидкість: τ ≈ 0.5–1 с\nЗахист: високий тиск\nІзоляція: з'єднаний з гільзою\nЗастосування: рідини, тиск"),
        ("3. Ізольований спай (Ungrounded)", 510, "#e1f5fe",
         "Швидкість: τ ≈ 2–5 с\nЗахист: максимальний\nІзоляція: > 500 В (MgO)\nЗастосування: EMI, багатоканальні")
    ]

    for title, x0, bg_col, desc in types:
        f.append(rect(x0, 60, 220, 305, fill=bg_col, stroke=MUTED, sw=1.3, rx=8))
        f.append(text(x0 + 110, 84, title, size=12.5, bold=True, color=INK))

        # Графіка гільзи / спаю
        gy = 140
        gw = 170
        gh = 56
        gx = x0 + 25

        if "Відкритий" in title:
            f.append(rect(gx + 30, gy, gw - 30, gh, fill="#eceff1", stroke=MUTED, sw=1.2))
            f.append(line(gx + 30, gy + 18, gx + gw, gy + 18, color=ALLOY_A, sw=3))
            f.append(line(gx + 30, gy + 38, gx + gw, gy + 38, color=ALLOY_B, sw=3))
            f.append(line(gx + 30, gy + 18, gx + 10, gy + 28, color=ALLOY_A, sw=3))
            f.append(line(gx + 30, gy + 38, gx + 10, gy + 28, color=ALLOY_B, sw=3))
            f.append(circle(gx + 10, gy + 28, 6, fill="#e65100", stroke=POS, sw=1.5))
        elif "Заземлений" in title:
            f.append(rect(gx + 20, gy, gw - 20, gh, fill=MGO_INS, stroke=SHEATH, sw=2))
            f.append(line(gx + 20, gy + 18, gx + gw, gy + 18, color=ALLOY_A, sw=3))
            f.append(line(gx + 20, gy + 38, gx + gw, gy + 38, color=ALLOY_B, sw=3))
            f.append(line(gx + 20, gy + 18, gx + 20, gy + 28, color=ALLOY_A, sw=3))
            f.append(line(gx + 20, gy + 38, gx + 20, gy + 28, color=ALLOY_B, sw=3))
            f.append(circle(gx + 20, gy + 28, 7, fill=SHEATH, stroke=INK, sw=2))
        else:
            f.append(rect(gx + 10, gy, gw - 10, gh, fill=MGO_INS, stroke=SHEATH, sw=2))
            f.append(line(gx + 35, gy + 18, gx + gw, gy + 18, color=ALLOY_A, sw=3))
            f.append(line(gx + 35, gy + 38, gx + gw, gy + 38, color=ALLOY_B, sw=3))
            f.append(line(gx + 35, gy + 18, gx + 25, gy + 28, color=ALLOY_A, sw=3))
            f.append(line(gx + 35, gy + 38, gx + 25, gy + 28, color=ALLOY_B, sw=3))
            f.append(circle(gx + 25, gy + 28, 5.5, fill="#ffb74d", stroke=POS, sw=1.5))

        b, _, _ = textbox(x0 + 110, 275, desc, size=11, pad=8, fill=BG, stroke=MUTED)
        f.append(b)

    render(os.path.join(IMG, "thermocouple-junction-types.svg"), W, H, *f)


# ── 3. Тракт вимірювання та алгоритм компенсації холодного спаю (CJC) ───────
def fig_cjc_pipeline():
    W, H = 760, 390
    f = [text(W / 2, 24, "Тракт збору даних і послідовність компенсації холодного спаю", size=16, bold=True)]

    # Крок 1: Клеми та вимірювання напруги
    f.append(rect(20, 55, 215, 145, fill="#fff8e1", stroke="#ffa000", sw=1.4, rx=6))
    f.append(text(127, 76, "1. Апаратний фронтенд", size=12.5, bold=True, color=INK))
    f.append(mtext(127, 102, ["Вхідна термо-ЕРС V_raw", "Фільтр НЧ + PGA (In-Amp)", "24-біт ΔΣ АЦП (зчитує мкВ)"], size=11, color=INK))
    f.append(text(127, 180, "→ Вихід: V_raw (мВ)", size=11.5, bold=True, color=POS))

    # Крок 2: Вимірювання температури холодного спаю
    f.append(rect(20, 220, 215, 145, fill="#e8f5e9", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(127, 241, "2. Сенсор холодного спаю", size=12.5, bold=True, color=INK))
    f.append(mtext(127, 267, ["NTC / RTD PT100 на клемах", "Зчитування температури", "планки клем T_cj"], size=11, color=INK))
    f.append(text(127, 345, "→ Вихід: T_cj (°C)", size=11.5, bold=True, color=FIELD))

    # Стрілки зведення в алгоритм
    f.append(arrow(235, 127, 275, 175, color=LINE, sw=2))
    f.append(arrow(235, 292, 275, 245, color=LINE, sw=2))

    # Крок 3: Обчислювальне ядро MCU
    f.append(rect(280, 55, 460, 310, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    f.append(text(510, 80, "3. Обчислювальний алгоритм у прошивці мікроконтролера", size=13, bold=True, color=INK))

    b_a, _, _ = textbox(510, 125, "Етап A: Перетворення T_cj у напругу еквівалентного спаю\nV_cj = NIST_Direct_Poly(T_cj)",
                        size=11.5, fill="#ffffff", stroke=FIELD, bold=True)
    f.append(b_a)

    f.append(arrow(510, 150, 510, 180, color=LINE, sw=1.8))

    b_b, _, _ = textbox(510, 205, "Етап B: Лінійне додавання термоелектрорушійних сил\nV_total = V_raw + V_cj   (в мілівольтах)",
                        size=12, fill="#ffffff", stroke=POS, bold=True)
    f.append(b_b)

    f.append(arrow(510, 230, 510, 260, color=LINE, sw=1.8))

    b_c, _, _ = textbox(510, 295, "Етап C: Обернений поліном NIST для сумарної напруги\nT_hot = NIST_Inverse_Poly(V_total)   (вихідна температура, °C)",
                        size=11.5, fill="#e3f2fd", stroke=NEG, bold=True)
    f.append(b_c)

    f.append(text(510, 348, "ПОМИЛКА: Не можна додавати температури напряму T_hot ≠ T_raw + T_cj!", size=10.5, color="#c0392b", bold=True))

    render(os.path.join(IMG, "cjc-compensation-pipeline.svg"), W, H, *f)


# ── 4. Криві чутливості та коефіцієнта Зеєбека S(T) ─────────────────────────
def fig_seebeck_curves():
    W, H = 760, 420
    f = [text(W / 2, 26, "Коефіцієнт Зеєбека S(T) стандартних термопар (нелінійність)", size=16, bold=True)]

    ox, oy = 80, 345
    ax_w, ax_h = 620, 270

    f.append(line(ox, oy, ox + ax_w, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - ax_h, color=INK, sw=1.8))

    f.append(text(ox + ax_w / 2, oy + 42, "Температура гарячого спаю,  °C", size=12, color=INK))
    f.append(mtext(ox - 52, oy - ax_h / 2, ["Диференційний", "коефіцієнт", "Зеєбека S", "(мкВ/°C)"], size=10.5, color=INK))

    t_min, t_max = -200, 1200
    s_min, s_max = 0, 70

    def X(t): return ox + (t - t_min) / (t_max - t_min) * ax_w
    def Y(s): return oy - (s - s_min) / (s_max - s_min) * ax_h

    for t in (-200, 0, 200, 400, 600, 800, 1000, 1200):
        f.append(line(X(t), oy, X(t), oy + 5, color=INK, sw=1.2))
        f.append(text(X(t), oy + 20, str(t), size=10.5, color=MUTED))
        if t != -200:
            f.append(line(X(t), oy, X(t), oy - ax_h, color="#eceff1", sw=1, dash="3,3"))

    for s_val in (10, 20, 30, 40, 50, 60, 70):
        f.append(line(ox - 5, Y(s_val), ox, Y(s_val), color=INK, sw=1.2))
        f.append(text(ox - 12, Y(s_val) + 4, str(s_val), size=10.5, color=MUTED, anchor="end"))
        f.append(line(ox, Y(s_val), ox + ax_w, Y(s_val), color="#eceff1", sw=1, dash="3,3"))

    def s_k(t):
        if t < 0: return 40.0 + 0.1 * t + 0.0002 * t * t
        dip = 2.5 * math.exp(-((t - 160) / 70) ** 2)
        return 39.5 + 0.004 * t - dip

    def s_j(t):
        if t < -40 or t > 800: return None
        return 50.0 + 0.015 * t - 0.00001 * t * t

    def s_t(t):
        if t < -200 or t > 400: return None
        return 38.7 + 0.08 * (t) - 0.00008 * (t ** 2)

    def s_n(t):
        if t < -200 or t > 1200: return None
        return 26.0 + 0.018 * t - 0.000006 * (t ** 2)

    def draw_curve(fn, t_start, t_end, col, name, label_t):
        step = 10
        pts = []
        cur_t = t_start
        while cur_t <= t_end:
            v = fn(cur_t)
            if v is not None and s_min <= v <= s_max:
                pts.append((X(cur_t), Y(v)))
            cur_t += step
        if pts:
            pts_str = " ".join("%.1f,%.1f" % p for p in pts)
            f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pts_str, col))
            ly = fn(label_t)
            if ly is not None:
                f.append(rect(X(label_t) - 24, Y(ly) - 20, 48, 18, fill=BG, stroke=col, sw=1.2, rx=3))
                f.append(text(X(label_t), Y(ly) - 7, name, size=11, bold=True, color=col))

    draw_curve(s_j, -40, 750, "#8e44ad", "Тип J", 450)
    draw_curve(s_k, -200, 1200, "#d35400", "Тип K", 900)
    draw_curve(s_t, -200, 400, "#2980b9", "Тип T", 150)
    draw_curve(s_n, -200, 1200, "#27ae60", "Тип N", 1050)

    f.append(circle(X(160), Y(s_k(160)), 5, fill="#ffccbc", stroke="#d35400", sw=1.5))
    f.append(text(X(160) + 12, Y(s_k(160)) + 18, "Провал Кюрі (~160 °C)", size=10, color="#d35400", anchor="start"))

    render(os.path.join(IMG, "seebeck-nonlinearity-curves.svg"), W, H, *f)


def main():
    fig_seebeck_circuit()
    fig_junction_types()
    fig_cjc_pipeline()
    fig_seebeck_curves()
    print("All figures generated successfully.")


if __name__ == '__main__':
    main()
