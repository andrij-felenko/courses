# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

WARN = "#d97706"

def path(cmds, fill="none", stroke=LINE, sw=1.5, dash=None):
    if isinstance(cmds, list):
        parts = []
        for item in cmds:
            if isinstance(item, tuple):
                cmd_type = item[0]
                coords = " ".join(f"{v:.1f}" for v in item[1:])
                parts.append(f"{cmd_type} {coords}")
            elif isinstance(item, (int, float)):
                parts.append(f"{item:.1f}")
            else:
                parts.append(str(item))
        d_str = " ".join(parts)
    else:
        d_str = str(cmds)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{dash_attr}/>'

def ellipse(cx, cy, rx, ry, fill=FILL, stroke=LINE, sw=1.5, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{dash_attr}/>'


# ── Фігура 1: Режими течії у відкритому каналі за числом Фруда ────────────────
def fig_froude_wave_regimes():
    W, H = 840, 500
    body = []

    panels = [
        ("Докритичний потік (Fr < 1)", "спокійний режим (v < c)", 0.5, 140, 140),
        ("Критичний потік (Fr = 1)", "граничний режим (v = c)", 1.0, 420, 140),
        ("Надкритичний потік (Fr > 1)", "бурхливий режим (v > c)", 2.0, 700, 140)
    ]

    for title_str, sub_str, Fr, cx, cy in panels:
        # Фон панелі
        body.append(rect(cx - 125, cy - 100, 250, 240, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
        body.append(text(cx, cy - 78, title_str, size=12.5, color=INK, bold=True))
        body.append(text(cx, cy - 60, sub_str, size=11, color=MUTED))

        # Дно каналу
        body.append(line(cx - 105, cy + 50, cx + 105, cy + 50, color="#475569", sw=2.5))
        for x_hatch in range(int(cx - 100), int(cx + 105), 15):
            body.append(line(x_hatch, cy + 50, x_hatch - 6, cy + 60, color="#94a3b8", sw=1.0))

        # Поверхня води та хвилі
        if Fr == 0.5:
            body.append(path([
                ("M", cx - 105, cy + 10),
                ("Q", cx - 50, cy + 5, cx, cy + 10),
                ("Q", cx + 50, cy + 15, cx + 105, cy + 10)
            ], fill="none", stroke="#0284c7", sw=2.0))
            body.append(circle(cx, cy + 10, 4, fill=POS, stroke=POS))
            body.append(ellipse(cx - 15, cy + 10, 35, 18, fill="none", stroke="#0284c7", sw=1.2, dash="3 3"))
            body.append(ellipse(cx - 35, cy + 10, 60, 32, fill="none", stroke="#0284c7", sw=1.0, dash="3 3"))
            body.append(arrow(cx - 10, cy - 18, cx - 60, cy - 18, color=POS, sw=1.5))
            body.append(arrow(cx + 10, cy - 18, cx + 60, cy - 18, color=POS, sw=1.5))
            body.append(text(cx, cy + 85, "хвилі біжать уперед", size=11, color=POS, bold=True))
            body.append(text(cx, cy + 102, "проти течії (c > v)", size=11, color=MUTED))

        elif Fr == 1.0:
            body.append(path([
                ("M", cx - 105, cy + 10),
                ("L", cx - 20, cy + 10),
                ("Q", cx, cy - 20, cx + 20, cy + 10),
                ("L", cx + 105, cy + 10)
            ], fill="none", stroke="#0284c7", sw=2.0))
            body.append(circle(cx, cy + 10, 4, fill=WARN, stroke=WARN))
            body.append(line(cx, cy - 35, cx, cy + 45, color=WARN, sw=1.8, dash="4 3"))
            body.append(arrow(cx - 40, cy + 10, cx + 40, cy + 10, color=INK, sw=1.5))
            body.append(text(cx, cy + 85, "стояча фронтальна хвиля", size=11, color=WARN, bold=True))
            body.append(text(cx, cy + 102, "швидкість течії v = c", size=11, color=MUTED))

        elif Fr == 2.0:
            body.append(path([
                ("M", cx - 105, cy + 25),
                ("L", cx - 10, cy + 25),
                ("L", cx + 55, cy - 15),
                ("L", cx + 105, cy - 15)
            ], fill="none", stroke="#0284c7", sw=2.0))
            body.append(circle(cx - 10, cy + 25, 4, fill=NEG, stroke=NEG))
            body.append(line(cx - 10, cy + 25, cx + 75, cy - 25, color=NEG, sw=1.8))
            body.append(line(cx - 10, cy + 25, cx + 75, cy + 45, color=NEG, sw=1.8))
            body.append(text(cx + 42, cy + 5, "α = arcsin(1/Fr)", size=10, color=NEG, bold=True))
            body.append(text(cx, cy + 85, "збурення зносяться вниз", size=11, color=NEG, bold=True))
            body.append(text(cx, cy + 102, "хвилі не йдуть вгору (v > c)", size=11, color=MUTED))

    # Нижній пояснювальний блок
    summary_box = fitbox(W / 2 - 370, 310, 740, 165,
                         "Фізичне значення числа Фруда (Fr = v / √(g·h)) у відкритих каналах:\n"
                         "• Fr < 1 (докритичний): швидкість поширення хвилі c перевищує швидкість потоку v; збурення поширюються вгору проти течії.\n"
                         "• Fr = 1 (критичний): швидкість потоку дорівнює швидкості гравітаційних хвиль; утворюється стоячий фронт.\n"
                         "• Fr > 1 (надкритичний): потік швидший за хвилі; збурення утворюють клиноподібний фронт і зносяться виключно вниз за течією.",
                         size=12.5, fill="#f1f5f9", stroke="#64748b", pad=12)
    body.append(summary_box)

    render(os.path.join(OUT, "froude-wave-regimes.svg"), W, H, *body,
           title="Режими хвильового поширення за числом Фруда у відкритому каналі")


# ── Фігура 2: Хвильовий опір судна та хвильова картина Кельвіна ───────────────
def fig_kelvin_wake_drag():
    W, H = 840, 520
    body = []

    # Ліва панель: Хвильова картина Кельвіна (вид зверху)
    cx1, cy1 = 220, 170
    body.append(rect(cx1 - 190, cy1 - 130, 380, 270, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
    body.append(text(cx1, cy1 - 108, "Хвильова картина Кельвіна (вид зверху)", size=12.5, color=INK, bold=True))

    body.append(path([
        ("M", cx1 - 120, cy1),
        ("Q", cx1 - 60, cy1 - 16, cx1 + 30, cy1),
        ("Q", cx1 - 60, cy1 + 16, cx1 - 120, cy1)
    ], fill="#94a3b8", stroke="#334155", sw=1.5))
    body.append(circle(cx1 + 30, cy1, 3, fill=POS, stroke=POS))

    ang_rad = math.radians(19.47)
    len_wake = 140
    dx = len_wake * math.cos(ang_rad)
    dy = len_wake * math.sin(ang_rad)

    body.append(line(cx1 + 30, cy1, cx1 - 130, cy1 - dy * 1.1, color=NEG, sw=1.8, dash="5 3"))
    body.append(line(cx1 + 30, cy1, cx1 - 130, cy1 + dy * 1.1, color=NEG, sw=1.8, dash="5 3"))

    for i in range(1, 5):
        x_w = cx1 + 30 - i * 32
        body.append(path([
            ("M", x_w, cy1 - i * 10),
            ("Q", x_w - 12, cy1, x_w, cy1 + i * 10)
        ], fill="none", stroke="#0284c7", sw=1.3))
        body.append(line(x_w, cy1 - i * 10, x_w - 18, cy1 - i * 10 - 9, color="#0369a1", sw=1.2))
        body.append(line(x_w, cy1 + i * 10, x_w - 18, cy1 + i * 10 + 9, color="#0369a1", sw=1.2))

    body.append(text(cx1 - 45, cy1 - 48, "θ = 19.47° (універсальний кут)", size=10.5, color=NEG, bold=True))
    body.append(text(cx1, cy1 + 115, "поперечні та розбіжні хвилі", size=11, color=MUTED))

    # Права панель: Крива хвильового опору C_w від числа Фруда Fr
    cx2, cy2 = 620, 170
    body.append(rect(cx2 - 180, cy2 - 130, 360, 270, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
    body.append(text(cx2, cy2 - 108, "Коефіцієнт хвильового опору C_w(Fr)", size=12.5, color=INK, bold=True))

    ox, oy = cx2 - 140, cy2 + 80
    body.append(line(ox, oy, ox + 290, oy, color="#475569", sw=1.5))
    body.append(line(ox, oy, ox, oy - 170, color="#475569", sw=1.5))
    body.append(text(ox + 270, oy + 20, "Fr", size=12, color=INK, bold=True))
    body.append(text(ox - 25, oy - 155, "C_w", size=12, color=INK, bold=True))

    fr_ticks = [(0.2, "0.2"), (0.4, "0.4"), (0.6, "0.6"), (0.8, "0.8")]
    for fr_val, fr_lbl in fr_ticks:
        tx = ox + fr_val * 300
        body.append(line(tx, oy, tx, oy + 4, color="#475569", sw=1.0))
        body.append(text(tx, oy + 18, fr_lbl, size=10, color=MUTED))

    tx_crit = ox + 0.4 * 300
    body.append(line(tx_crit, oy, tx_crit, oy - 160, color=WARN, sw=1.5, dash="4 3"))
    body.append(text(tx_crit, oy - 165, "Fr ≈ 0.4 (хвильовий бар'єр)", size=10.5, color=WARN, bold=True))

    curve_pts = [
        (ox, oy - 5),
        (ox + 0.1 * 300, oy - 8),
        (ox + 0.2 * 300, oy - 18),
        (ox + 0.3 * 300, oy - 35),
        (ox + 0.4 * 300, oy - 105),
        (ox + 0.5 * 300, oy - 145),
        (ox + 0.65 * 300, oy - 155)
    ]
    path_d = ["M", curve_pts[0][0], curve_pts[0][1]]
    for px, py in curve_pts[1:]:
        path_d.extend(["L", px, py])
    body.append(path(path_d, fill="none", stroke=POS, sw=2.5))

    body.append(text(ox + 45, oy - 45, "водотоннажний", size=10, color=MUTED))
    body.append(text(ox + 160, oy - 125, "глісування / ПК", size=10, color=POS, bold=True))

    summary_box = fitbox(W / 2 - 370, 320, 740, 160,
                         "Хвильовий опір суден та межа швидкості корпусу:\n"
                         "• Хвильова картина Кельвіна утворює універсальний кут клина 2θ ≈ 38.94° (θ ≈ 19.47°), незалежно від швидкості.\n"
                         "• При Fr ≈ 0.4 довжина згенерованої поверхневої хвилі дорівнює довжині корпусу судна (λ ≈ L_w).\n"
                         "• Подолання числа Фруда Fr > 0.4 вимагає виходу з водотоннажного режиму на гідродінамічне підтримання (глісування, підводні крила).",
                         size=12.5, fill="#f1f5f9", stroke="#64748b", pad=12)
    body.append(summary_box)

    render(os.path.join(OUT, "kelvin-wake-drag.svg"), W, H, *body,
           title="Хвильова картина Кельвіна та коефіцієнт хвильового опору")


# ── Фігура 3: Гідравлічний стрибок та дисипація енергії ───────────────────────
def fig_hydraulic_jump():
    W, H = 820, 480
    body = []

    cx, cy = 410, 180
    body.append(rect(cx - 370, cy - 130, 740, 260, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
    body.append(text(cx, cy - 108, "Схема гідравлічного стрибка у відкритому каналі", size=13.5, color=INK, bold=True))

    body.append(line(cx - 340, cy + 80, cx + 340, cy + 80, color="#475569", sw=2.5))
    for x_hatch in range(int(cx - 335), int(cx + 340), 18):
        body.append(line(x_hatch, cy + 80, x_hatch - 8, cy + 92, color="#94a3b8", sw=1.0))

    x0 = cx - 340
    x1 = cx - 120
    x2 = cx + 80
    x3 = cx + 340

    y_bot = cy + 80
    h1_px = 35
    h2_px = 125

    y_surf1 = y_bot - h1_px
    y_surf2 = y_bot - h2_px

    water_path = [
        ("M", x0, y_surf1),
        ("L", x1, y_surf1),
        ("C", x1 + 60, y_surf1 - 15, x2 - 40, y_surf2 - 20, x2, y_surf2),
        ("L", x3, y_surf2),
        ("L", x3, y_bot),
        ("L", x0, y_bot)
    ]
    body.append(path(water_path, fill="#e0f2fe", stroke="none"))
    body.append(path([
        ("M", x0, y_surf1),
        ("L", x1, y_surf1),
        ("C", x1 + 60, y_surf1 - 15, x2 - 40, y_surf2 - 20, x2, y_surf2),
        ("L", x3, y_surf2)
    ], fill="none", stroke="#0284c7", sw=2.5))

    body.append(ellipse(cx - 20, cy - 5, 45, 22, fill="#bae6fd", stroke="#0284c7", sw=1.2, dash="3 2"))
    body.append(text(cx - 20, cy - 5, "турбулентне вихроутворення (ролик)", size=10.5, color="#0369a1", bold=True))

    body.append(arrow(cx - 240, y_bot, cx - 240, y_surf1, color=NEG, sw=1.5))
    body.append(arrow(cx - 240, y_surf1, cx - 240, y_bot, color=NEG, sw=1.5))
    body.append(text(cx - 275, cy + 60, "h₁ (бурхлива)", size=11, color=NEG, bold=True))
    body.append(text(cx - 275, cy + 42, "Fr₁ > 1", size=11, color=NEG, bold=True))

    body.append(arrow(cx + 220, y_bot, cx + 220, y_surf2, color=POS, sw=1.5))
    body.append(arrow(cx + 220, y_surf2, cx + 220, y_bot, color=POS, sw=1.5))
    body.append(text(cx + 255, cy + 10, "h₂ (спокійна)", size=11, color=POS, bold=True))
    body.append(text(cx + 255, cy - 8, "Fr₂ < 1", size=11, color=POS, bold=True))

    body.append(arrow(cx - 300, y_surf1 - 15, cx - 220, y_surf1 - 15, color=INK, sw=2.0))
    body.append(text(cx - 260, y_surf1 - 25, "v₁ (велика)", size=11, color=INK, bold=True))

    body.append(arrow(cx + 140, y_surf2 - 15, cx + 200, y_surf2 - 15, color=INK, sw=1.5))
    body.append(text(cx + 170, y_surf2 - 25, "v₂ (мала)", size=11, color=INK, bold=True))

    body.append(rect(cx - 190, cy + 92, 380, 30, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=4))
    body.append(text(cx, cy + 112, "Співвідношення Беланже: h₂/h₁ = 0.5 · (√(1 + 8·Fr₁²) - 1)", size=11, color=INK, bold=True))

    summary_box = fitbox(W / 2 - 370, 305, 740, 150,
                         "Механіка гідравлічного стрибка у відкритому каналі:\n"
                         "• Гідравлічний стрибок — це нелінійний перехід від надкритичного потоку (Fr₁ > 1) до докритичного (Fr₂ < 1).\n"
                         "• Кільцевий вихровий вал інтенсивно дисипує кінетичну енергію потоку у тепло та турбулентний шум.\n"
                         "• Спряжені глибини h₁ та h₂ однозначно визначаються вхідним числом Фруда Fr₁ згідно з рівнянням збереження імпульсу.",
                         size=12.5, fill="#f1f5f9", stroke="#64748b", pad=12)
    body.append(summary_box)

    render(os.path.join(OUT, "hydraulic-jump.svg"), W, H, *body,
           title="Структура гідравлічного стрибка та спряжені глибини")


# ── Фігура 4: Біомеханічне число Фруда та модель інвертованого маятника ────────
def fig_biomechanics_froude():
    W, H = 820, 500
    body = []

    cx1, cy1 = 220, 175
    body.append(rect(cx1 - 190, cy1 - 135, 380, 270, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
    body.append(text(cx1, cy1 - 110, "Інвертований маятник ходьби", size=13, color=INK, bold=True))

    body.append(line(cx1 - 150, cy1 + 90, cx1 + 150, cy1 + 90, color="#475569", sw=2.0))
    body.append(circle(cx1, cy1 + 90, 5, fill="#334155", stroke="#334155"))
    body.append(text(cx1, cy1 + 108, "стопа (опора)", size=10, color=MUTED))

    leg_len = 140
    ang = math.radians(18)
    hip_x = cx1 + leg_len * math.sin(ang)
    hip_y = (cy1 + 90) - leg_len * math.cos(ang)

    body.append(line(cx1, cy1 + 90, hip_x, hip_y, color=POS, sw=3.0))
    body.append(circle(hip_x, hip_y, 16, fill="#3b82f6", stroke="#1d4ed8", sw=1.5))
    body.append(text(hip_x, hip_y + 4, "ЦМ", size=11, color="#ffffff", bold=True))

    body.append(path([
        ("M", cx1 - 60, cy1 - 20),
        ("Q", cx1, cy1 - 55, cx1 + 60, cy1 - 20)
    ], fill="none", stroke="#0284c7", sw=1.8, dash="4 3"))

    body.append(arrow(hip_x, hip_y + 16, hip_x, hip_y + 65, color=NEG, sw=2.0))
    body.append(text(hip_x + 12, hip_y + 45, "F_g = m·g", size=11, color=NEG, bold=True))

    body.append(arrow(hip_x, hip_y - 16, hip_x + 25, hip_y - 50, color=WARN, sw=2.0))
    body.append(text(hip_x + 30, hip_y - 35, "a_c = v²/L", size=11, color=WARN, bold=True))

    body.append(text(cx1 - 75, cy1 + 15, "L (довжина ноги)", size=11, color=POS, bold=True))

    cx2, cy2 = 620, 175
    body.append(rect(cx2 - 180, cy2 - 135, 360, 270, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=8))
    body.append(text(cx2, cy2 - 110, "Перехід ходьба → біг за Fr", size=13, color=INK, bold=True))

    ox, oy = cx2 - 130, cy2 + 70
    body.append(line(ox, oy, ox + 260, oy, color="#475569", sw=2.0))

    val_points = [(0.0, "0.0 (статика)"), (0.25, "0.25 (повільна)"), (0.5, "0.5 (критична)"), (1.0, "1.0 (теоретична)")]
    for val, lbl in val_points:
        px = ox + val * 240
        body.append(line(px, oy - 6, px, oy + 6, color="#475569", sw=1.5))
        body.append(text(px, oy + 22, lbl, size=9.5, color=MUTED))

    body.append(rect(ox, oy - 45, 120, 35, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=4))
    body.append(text(ox + 60, oy - 23, "Зона ходьби (Fr < 0.5)", size=10.5, color="#15803d", bold=True))

    body.append(rect(ox + 120, oy - 45, 120, 35, fill="#fee2e2", stroke="#ef4444", sw=1.2, rx=4))
    body.append(text(ox + 180, oy - 23, "Зона бігу (Fr > 0.5)", size=10.5, color="#b91c1c", bold=True))

    body.append(line(ox + 120, oy - 80, ox + 120, oy + 10, color=WARN, sw=2.0, dash="4 3"))
    body.append(text(ox + 120, oy - 90, "Перехід Александра: Fr ≈ 0.5", size=11, color=WARN, bold=True))

    body.append(text(cx2, cy2 - 50, "При Fr > 0.5 доцентрове", size=10.5, color=INK))
    body.append(text(cx2, cy2 - 35, "прискорення змушує відривати", size=10.5, color=INK))
    body.append(text(cx2, cy2 - 20, "стопу від поверхні", size=10.5, color=INK))

    summary_box = fitbox(W / 2 - 370, 325, 740, 155,
                         "Біомеханіка локомоції тварин та людини (закономерність Александра):\n"
                         "• Біомеханічне число Фруда визначається як Fr = v / √(g·L), де L — довжина кінцівки.\n"
                         "• При ходьбі центр мас рухається по дузі кола: відрив стопи настає, коли доцентрове прискорення v²/L дорівнює g.\n"
                         "• Емпіричний перехід від ходьби до бігу у ссавців, птахів та людини відбувається при досягненні Fr ≈ 0.5 (Fr² ≈ 0.25).",
                         size=12, fill="#f1f5f9", stroke="#64748b", pad=12)
    body.append(summary_box)

    render(os.path.join(OUT, "biomechanics-froude.svg"), W, H, *body,
           title="Біомеханічне число Фруда та перехід від ходьби до бігу")


if __name__ == "__main__":
    fig_froude_wave_regimes()
    fig_kelvin_wake_drag()
    fig_hydraulic_jump()
    fig_biomechanics_froude()
    print("Всі 4 фігури успішно згенеровані у теці img/")
