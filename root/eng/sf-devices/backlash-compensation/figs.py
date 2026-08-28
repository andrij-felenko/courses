# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. gear-backlash-gap: фізичний зазор і втрата контакту при реверсі ─────────
def fig_gear_backlash_gap():
    W, H = 760, 360
    p = []

    p.append(text(W / 2, 28, "Фази передачі руху крізь зазор зубчастого зачеплення", size=13, bold=True))

    cards = [
        ("1. Прямий рух (+)", "Контакт на правій грані", "Ведучий зуб штовхає ведений,\nнавантаження рухається синхронно.", "#eafaf0", FIELD),
        ("2. Реверс: мертвий хід", "Втрата контакту (зазор Δx)", "Мотор крутиться назад у повітрі,\nнавантаження стоїть нерухомо.", "#fff3cd", "#c07000"),
        ("3. Зворотний контакт (-)", "Контакт на лівій грані", "Зазор вибрано, ведучий зуб штовхає\nпротилежну грань, рух відновився.", "#eef4ff", NEG),
    ]

    cw, ch = 220, 260
    xs = [35, 270, 505]
    top_y = 55

    for i, (title, subtitle, desc, bg_col, border_col) in enumerate(cards):
        x = xs[i]
        p.append(rect(x, top_y, cw, ch, fill=bg_col, stroke=border_col, sw=1.8, rx=6))
        p.append(text(x + cw / 2, top_y + 24, title, size=12, bold=True, color=INK))
        p.append(text(x + cw / 2, top_y + 44, subtitle, size=10, bold=True, color=border_col))

        cy = top_y + 125
        p.append(rect(x + 20, cy - 35, 60, 70, fill="#dcdfe6", stroke="#909399", sw=1.5, rx=3))
        p.append(rect(x + 140, cy - 35, 60, 70, fill="#dcdfe6", stroke="#909399", sw=1.5, rx=3))
        p.append(text(x + 50, cy + 50, "Ведений зуб", size=9, color=MUTED))

        if i == 0:
            p.append(rect(x + 90, cy - 30, 50, 60, fill="#a8e6cf", stroke=FIELD, sw=2, rx=3))
            p.append(arrow(x + 100, cy - 45, x + 135, cy - 45, color=FIELD, sw=2))
            p.append(text(x + 115, cy - 52, "F рушійна", size=9, color=FIELD, bold=True))
            p.append(line(x + 140, cy - 30, x + 140, cy + 30, color=POS, sw=2.5))
            p.append(text(x + 115, cy + 2, "Контакт", size=9, color=INK, bold=True))
        elif i == 1:
            p.append(rect(x + 85, cy - 30, 50, 60, fill="#ffd3b6", stroke="#c07000", sw=2, rx=3))
            p.append(arrow(x + 120, cy - 45, x + 85, cy - 45, color=POS, sw=2))
            p.append(text(x + 110, cy - 52, "Реверс мотора", size=9, color=POS, bold=True))
            p.append(line(x + 80, cy + 15, x + 85, cy + 15, color=POS, sw=1.5))
            p.append(line(x + 135, cy + 15, x + 140, cy + 15, color=POS, sw=1.5))
            p.append(text(x + 110, cy + 2, "Мертвий хід Δx", size=9, color=POS, bold=True))
        else:
            p.append(rect(x + 80, cy - 30, 50, 60, fill="#d0e1fd", stroke=NEG, sw=2, rx=3))
            p.append(arrow(x + 125, cy - 45, x + 90, cy - 45, color=NEG, sw=2))
            p.append(text(x + 110, cy - 52, "F реверсна", size=9, color=NEG, bold=True))
            p.append(line(x + 80, cy - 30, x + 80, cy + 30, color=POS, sw=2.5))
            p.append(text(x + 105, cy + 2, "Контакт", size=9, color=INK, bold=True))

        p.append(mtext(x + cw / 2, top_y + 205, desc, size=10, color=INK, lh=1.3))

    p.append(text(W / 2, 345, "Під час зміни напрямку стіл стоїть нерухомо, поки вал двигуна долає зазор Δx",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "gear-backlash-gap.svg"), W, H, *p,
           title="Механічний зазор у зачепленні зубчастих коліс при реверсі")


# ── 2. hysteresis-loop: гістерезисна петля положення ───────────────────────────
def fig_hysteresis_loop():
    W, H = 760, 360
    p = []

    p.append(text(W / 2, 26, "Гістерезисна петля переміщення: координата навантаження від кута мотора", size=13, bold=True))

    ox, oy = 260, 190
    dx = 40

    p.append(line(ox - 180, oy, ox + 180, oy, color=MUTED, sw=1.2))
    p.append(line(ox, oy + 120, ox, oy - 120, color=MUTED, sw=1.2))
    p.append(text(ox + 195, oy + 4, "x_motor (вал)", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(ox, oy - 130, "x_load (виконавчий орган)", size=11, color=INK, bold=True))

    p.append(line(ox - 140 + dx, oy + 100, ox + 100 + dx, oy - 100, color=FIELD, sw=2.5))
    p.append(line(ox + 100 - dx, oy - 100, ox - 140 - dx, oy + 100, color=NEG, sw=2.5))

    p.append(line(ox + 100 + dx, oy - 100, ox + 100 - dx, oy - 100, color=POS, sw=2.5, dash="4 3"))
    p.append(line(ox - 140 - dx, oy + 100, ox - 140 + dx, oy + 100, color=POS, sw=2.5, dash="4 3"))

    p.append(arrow(ox + 20 + dx, oy - 30, ox + 60 + dx, oy - 65, color=FIELD, sw=2))
    p.append(arrow(ox + 140, oy - 100, ox + 90, oy - 100, color=POS, sw=2))
    p.append(arrow(ox - 20 - dx, oy + 30, ox - 60 - dx, oy + 65, color=NEG, sw=2))
    p.append(arrow(ox - 180, oy + 100, ox - 130, oy + 100, color=POS, sw=2))

    p.append(line(ox - dx, oy + 130, ox + dx, oy + 130, color=POS, sw=1.5))
    p.append(line(ox - dx, oy + 125, ox - dx, oy + 135, color=POS, sw=1.5))
    p.append(line(ox + dx, oy + 125, ox + dx, oy + 135, color=POS, sw=1.5))
    p.append(text(ox, oy + 148, "Люфт зазору Δx", size=11, color=POS, bold=True))

    bx, by, bw, bh = 500, 60, 235, 255
    p.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(bx + bw / 2, by + 24, "Рівняння гістерезису", size=12, bold=True, color=INK))

    p.append(text(bx + 15, by + 56, "1. Рух уперед (v > 0):", size=10, bold=True, color=FIELD, anchor="start"))
    p.append(text(bx + 25, by + 74, "x_load = x_motor - Δx/2", size=10, color=INK, anchor="start"))

    p.append(text(bx + 15, by + 104, "2. Рух назад (v < 0):", size=10, bold=True, color=NEG, anchor="start"))
    p.append(text(bx + 25, by + 122, "x_load = x_motor + Δx/2", size=10, color=INK, anchor="start"))

    p.append(text(bx + 15, by + 152, "3. Реверс (перетин зазору):", size=10, bold=True, color=POS, anchor="start"))
    p.append(text(bx + 25, by + 170, "dx_load / dt = 0", size=10, color=INK, anchor="start"))
    p.append(text(bx + 25, by + 188, "(виконавчий орган стоїть)", size=9, color=MUTED, italic=True, anchor="start"))

    p.append(line(bx + 15, by + 205, bx + bw - 15, by + 205, color="#e2e8f0", sw=1))
    p.append(mtext(bx + bw / 2, by + 224, "Помилка позиції є нелінійною\nі залежить від передісторії руху", size=9, color=INK, lh=1.3))

    p.append(text(W / 2, 345, "Петля гістерезису розділяє рух уперед і назад на величину повного мертвого ходу Δx",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "hysteresis-loop.svg"), W, H, *p,
           title="Гістерезисна петля передачі положення з люфтом")


# ── 3. quadrant-glitch: спотворення кругової інтерполяції ───────────────────────
def fig_quadrant_glitch():
    W, H = 760, 340
    p = []

    p.append(text(W / 2, 26, "Вплив люфту на кругову інтерполяцію при зміні знака швидкості осей", size=13, bold=True))

    lx = 190
    ly = 175
    r = 75

    p.append(rect(30, 50, 325, 250, fill="#fdf7f7", stroke=POS, sw=1.5, rx=6))
    p.append(text(lx, 74, "Без компенсації люфту", size=12, bold=True, color=POS))
    p.append(text(lx, 92, "Сходинки на полюсах квадрантів", size=10, color=MUTED))

    p.append(circle(lx, ly, r, fill="none", stroke="#cbd5e1", sw=1.5))

    d = 10
    path_glitch = f"M {lx+r} {ly-d} L {lx+r} {ly+d} A {r} {r} 0 0 1 {lx+d} {ly+r} L {lx-d} {ly+r} A {r} {r} 0 0 1 {lx-r} {ly+d} L {lx-r} {ly-d} A {r} {r} 0 0 1 {lx-d} {ly-r} L {lx+d} {ly-r} A {r} {r} 0 0 1 {lx+r} {ly-d} Z"
    p.append(f'<path d="{path_glitch}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    p.append(circle(lx + r, ly, 4, fill=POS, stroke=BG, sw=1))
    p.append(circle(lx - r, ly, 4, fill=POS, stroke=BG, sw=1))
    p.append(circle(lx, ly + r, 4, fill=POS, stroke=BG, sw=1))
    p.append(circle(lx, ly - r, 4, fill=POS, stroke=BG, sw=1))

    p.append(text(lx + r + 20, ly, "Реверс X", size=9, color=POS, bold=True, anchor="start"))
    p.append(text(lx, ly - r - 10, "Реверс Y", size=9, color=POS, bold=True))
    p.append(mtext(lx, 275, "«Пласкі зуби» через затримку осей:\nколо деформується на 0°, 90°, 180°, 270°", size=9, color=POS, lh=1.3))

    rx_c = 570
    p.append(rect(405, 50, 325, 250, fill="#f2fbf5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(rx_c, 74, "З програмною компенсацією", size=12, bold=True, color=FIELD))
    p.append(text(rx_c, 92, "Миттєва вибірка мертвого ходу Δx", size=10, color=MUTED))

    p.append(circle(rx_c, ly, r, fill="none", stroke=FIELD, sw=2.5))
    p.append(circle(rx_c + r, ly, 4, fill=FIELD, stroke=BG, sw=1))
    p.append(circle(rx_c - r, ly, 4, fill=FIELD, stroke=BG, sw=1))
    p.append(circle(rx_c, ly + r, 4, fill=FIELD, stroke=BG, sw=1))
    p.append(circle(rx_c, ly - r, 4, fill=FIELD, stroke=BG, sw=1))

    p.append(text(rx_c + r + 15, ly, "+Δx влито", size=9, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx_c, ly - r - 10, "+Δy влито", size=9, color=FIELD, bold=True))
    p.append(mtext(rx_c, 275, "Планувальник додає зміщення при реверсі:\nідеальний круглий контур без сходинок", size=9, color=FIELD, lh=1.3))

    p.append(text(W / 2, 325, "Реверс швидкості на полюсах квадрантів вимагає точного впорскування імпульсів компенсації",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "quadrant-glitch.svg"), W, H, *p,
           title="Деформація контуру на полюсах квадрантів без компенсації люфту")


# ── 4. pulse-burst-vs-profile: небезпечний стрибок проти плавного профілю ───────
def fig_pulse_burst_vs_profile():
    W, H = 760, 320
    p = []

    p.append(text(W / 2, 24, "Способи впорскування кроків компенсації: миттєвий сплеск vs плавний профіль", size=13, bold=True))

    bx = 35
    by = 48
    bw = 330
    bh = 235
    p.append(rect(bx, by, bw, bh, fill="#fdf7f7", stroke=POS, sw=1.5, rx=6))
    p.append(text(bx + bw / 2, by + 22, "Миттєвий сплеск (Step Burst) — Помилка", size=11, bold=True, color=POS))

    gx, gy = bx + 40, by + 125
    p.append(line(gx, gy + 40, gx + 250, gy + 40, color=MUTED, sw=1))
    p.append(line(gx, gy + 45, gx, gy - 40, color=MUTED, sw=1))
    p.append(text(gx + 250, gy + 52, "t", size=9, color=MUTED, anchor="start"))
    p.append(text(gx - 8, gy - 35, "v", size=9, color=MUTED))

    p.append(line(gx, gy + 10, gx + 80, gy + 40, color=INK, sw=1.8))
    p.append(line(gx + 80, gy + 40, gx + 80, gy - 35, color=POS, sw=3))
    p.append(line(gx + 80, gy - 35, gx + 95, gy - 35, color=POS, sw=3))
    p.append(line(gx + 95, gy - 35, gx + 95, gy + 40, color=POS, sw=3))
    p.append(line(gx + 95, gy + 40, gx + 230, gy - 10, color=INK, sw=1.8))

    p.append(text(gx + 120, gy - 25, "a → ∞ (удар)", size=9, color=POS, bold=True, anchor="start"))
    p.append(mtext(bx + bw / 2, by + 195, "Миттєвий викид усіх кроків за один такт:\nзрив синхронізації крокового мотора,\nпропуск кроків, удар по зубах шестерень", size=9, color=POS, lh=1.3))

    rx = 395
    p.append(rect(rx, by, bw, bh, fill="#f2fbf5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(rx + bw / 2, by + 22, "Профіль з обмеженням a_max — Норма", size=11, bold=True, color=FIELD))

    rgx, rgy = rx + 40, by + 125
    p.append(line(rgx, rgy + 40, rgx + 250, rgy + 40, color=MUTED, sw=1))
    p.append(line(rgx, rgy + 45, rgx, rgy - 40, color=MUTED, sw=1))
    p.append(text(rgx + 250, rgy + 52, "t", size=9, color=MUTED, anchor="start"))
    p.append(text(rgx - 8, rgy - 35, "v", size=9, color=MUTED))

    p.append(line(rgx, rgy + 10, rgx + 60, rgy + 40, color=INK, sw=1.8))
    p.append(line(rgx + 60, rgy + 40, rgx + 90, rgy - 25, color=FIELD, sw=2.5))
    p.append(line(rgx + 90, rgy - 25, rgx + 125, rgy - 25, color=FIELD, sw=2.5))
    p.append(line(rgx + 125, rgy - 25, rgx + 155, rgy + 40, color=FIELD, sw=2.5))
    p.append(line(rgx + 155, rgy + 40, rgx + 230, rgy - 15, color=INK, sw=1.8))

    p.append(text(rgx + 105, rgy - 32, "a_comp ≤ a_max", size=9, color=FIELD, bold=True))
    p.append(mtext(rx + bw / 2, by + 195, "Кроки люфту видаються трапецеїдальним\nабо S-подібним профілем зі швидкістю v_comp:\nмотор тримає момент, зачеплення плавне", size=9, color=FIELD, lh=1.3))

    p.append(text(W / 2, 305, "Компенсація мусить поважати фізичні ліміти прискорення і моменту приводу",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "pulse-burst-vs-profile.svg"), W, H, *p,
           title="Порівняння миттєвого впорскування кроків з обмеженим профілем")


# ── 5. dual-loop-architecture: архітектура подвійного зворотного зв'язку ──────
def fig_dual_loop_architecture():
    W, H = 780, 350
    p = []

    p.append(text(W / 2, 24, "Структура подвійного контуру (Dual-Loop) з енкодером мотора та лінійною шкалою", size=13, bold=True))

    p.append(arrow(30, 95, 75, 95, color=INK, sw=1.8))
    p.append(text(50, 83, "x_target", size=10, bold=True))

    p.append(circle(90, 95, 14, fill=BG, stroke=INK, sw=1.5))
    p.append(text(90, 99, "+", size=12, bold=True))

    p.append(rect(130, 65, 115, 60, fill="#eef4ff", stroke=NEG, sw=1.8, rx=5))
    p.append(mtext(187, 88, "Position Loop\n(1–2 кГц)", size=10, bold=True, color=NEG))
    p.append(arrow(104, 95, 130, 95, color=INK, sw=1.5))

    p.append(arrow(245, 95, 275, 95, color=INK, sw=1.5))
    p.append(text(260, 83, "v_cmd", size=9, bold=True))
    p.append(circle(290, 95, 14, fill=BG, stroke=INK, sw=1.5))
    p.append(text(290, 99, "+", size=12, bold=True))

    p.append(rect(330, 65, 120, 60, fill="#f2fbf5", stroke=FIELD, sw=1.8, rx=5))
    p.append(mtext(390, 88, "Velocity Loop\n(10–20 кГц)", size=10, bold=True, color=FIELD))
    p.append(arrow(304, 95, 330, 95, color=INK, sw=1.5))

    p.append(rect(480, 65, 80, 60, fill="#f8fafc", stroke=LINE, sw=1.5, rx=5))
    p.append(mtext(520, 88, "Мотор\n(BLDC/Крок)", size=10, bold=True))
    p.append(arrow(450, 95, 480, 95, color=INK, sw=1.5))

    p.append(rect(590, 65, 85, 60, fill="#fff3cd", stroke="#c07000", sw=2, rx=5))
    p.append(mtext(632, 88, "Редуктор / ШВП\n(Люфт Δx)", size=9, bold=True, color="#c07000"))
    p.append(arrow(560, 95, 590, 95, color=INK, sw=1.5))

    p.append(rect(705, 65, 60, 60, fill="#e2e8f0", stroke=LINE, sw=1.8, rx=5))
    p.append(mtext(735, 88, "Стіл\n(Load)", size=10, bold=True))
    p.append(arrow(675, 95, 705, 95, color=INK, sw=1.5))

    p.append(line(520, 125, 520, 180, color=FIELD, sw=1.8))
    p.append(rect(460, 180, 120, 40, fill="#f2fbf5", stroke=FIELD, sw=1.5, rx=4))
    p.append(mtext(520, 198, "Енкодер вала\n(Motor Encoder)", size=9, bold=True, color=FIELD))
    p.append(line(460, 200, 290, 200, color=FIELD, sw=1.8))
    p.append(arrow(290, 200, 290, 109, color=FIELD, sw=1.8))
    p.append(text(302, 160, "v_motor (-)", size=9, color=FIELD, bold=True, anchor="start"))

    p.append(line(735, 125, 735, 270, color=NEG, sw=1.8))
    p.append(rect(590, 250, 140, 40, fill="#eef4ff", stroke=NEG, sw=1.5, rx=4))
    p.append(mtext(660, 268, "Лінійна оптична шкала\n(Linear Optical Scale)", size=9, bold=True, color=NEG))

    p.append(rect(340, 250, 170, 40, fill="#fdf7f7", stroke=POS, sw=1.5, rx=4))
    p.append(mtext(425, 268, "Anti-Hunting Filter\n(Зона нечутливості в зазорі)", size=9, bold=True, color=POS))
    p.append(arrow(590, 270, 510, 270, color=NEG, sw=1.8))
    p.append(line(340, 270, 90, 270, color=NEG, sw=1.8))
    p.append(arrow(90, 270, 90, 109, color=NEG, sw=1.8))
    p.append(text(102, 230, "x_table (-)", size=9, color=NEG, bold=True, anchor="start"))

    p.append(text(W / 2, 335, "Внутрішній контур забезпечує швидкість і демпфування, зовнішній — абсолютну точність столу",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "dual-loop-architecture.svg"), W, H, *p,
           title="Архітектура подвійного зворотного зв'язку для компенсації люфту")


if __name__ == "__main__":
    fig_gear_backlash_gap()
    fig_hysteresis_loop()
    fig_quadrant_glitch()
    fig_pulse_burst_vs_profile()
    fig_dual_loop_architecture()
    print("OK: 5 figures generated successfully.")
