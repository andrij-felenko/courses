# -*- coding: utf-8 -*-
"""
Фігури для вставки r11-history-arm.md
  Рис. 4.11.0.1 — Тупик, що породив ARM (три стовпці: глухий кут → WDC → рішення)
  Рис. 4.11.0.2 — RISC проти CISC (дві картки-колонки)
  Рис. 4.11.0.3 — Бізнес-модель ARM: ліцензування ядра (ARM у центрі → ліцензіати)

Чистий Python, без сторонніх залежностей. Вивід → ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.11.0.1 — Тупик, що породив ARM
# Три стовпці: (1) глухий кут, (2) поворот (WDC), (3) рішення
# ══════════════════════════════════════════════════════════════════════════════
def fig1_why_own_cpu():
    W, H = 820, 340
    frags = []

    # Заголовок
    frags.append(text(W / 2, 28, "Чому Acorn вирішила зробити власний процесор", size=15, bold=True))

    # Три зони
    col_w = 220
    col_gap = 40
    c1x = 60 + col_w / 2
    c2x = c1x + col_w + col_gap
    c3x = c2x + col_w + col_gap
    box_top = 55
    box_h = 240

    # --- Стовпець 1: Глухий кут ---
    frags.append(rect(c1x - col_w / 2, box_top, col_w, box_h,
                      fill="#fef2f2", stroke=POS, sw=2, rx=10))
    frags.append(text(c1x, box_top + 22, "Глухий кут", size=13, bold=True, color=POS))

    items1 = [
        ("6502 (8-біт)", "BBC Micro", "→ стеля продуктивності"),
        ("Motorola 68000", "16-біт CISC", "✗ повільна реакція"),
        ("National 32016", "16-біт CISC", "✗ висока латентність"),
    ]
    y_start = box_top + 52
    for name, sub, note in items1:
        tb, bw, bh = textbox(c1x, y_start, f"{name}\n{sub}", size=11,
                             fill="#fff0f0", stroke=POS, sw=1, pad=7)
        frags.append(tb)
        frags.append(text(c1x, y_start + bh / 2 + 14, note, size=10, color=MUTED))
        y_start += bh + 26

    # --- Стрілка 1→2 ---
    arr_y = box_top + box_h / 2
    frags.append(arrow(c1x + col_w / 2 + 4, arr_y, c2x - col_w / 2 - 4, arr_y,
                       color=LINE, sw=2))

    # --- Стовпець 2: Поворот — WDC ---
    frags.append(rect(c2x - col_w / 2, box_top, col_w, box_h,
                      fill="#fffbea", stroke="#d97706", sw=2, rx=10))
    frags.append(text(c2x, box_top + 22, "Поворот", size=13, bold=True, color="#d97706"))

    wdc_lines = [
        "Візит у Western",
        "Design Center,",
        "Фенікс (1983)",
        "",
        "Очікували:",
        "корпорацію-гіганта",
        "",
        "Побачили:",
        "кімнату + жменю",
        "інженерів зі",
        "студентами",
        "",
        "→ «якщо ВОНИ",
        "можуть — і ми»",
    ]
    frags.append(mtext(c2x, box_top + 52, wdc_lines, size=11, color=INK, lh=1.28))

    # --- Стрілка 2→3 ---
    frags.append(arrow(c2x + col_w / 2 + 4, arr_y, c3x - col_w / 2 - 4, arr_y,
                       color=LINE, sw=2))

    # --- Стовпець 3: Рішення ---
    frags.append(rect(c3x - col_w / 2, box_top, col_w, box_h,
                      fill="#f0fdf4", stroke=FIELD, sw=2, rx=10))
    frags.append(text(c3x, box_top + 22, "Рішення", size=13, bold=True, color=FIELD))

    res_lines = [
        "Спроєктувати",
        "ВЛАСНЕ RISC-ядро",
        "",
        "Ключові ролі:",
        "Sophie Wilson",
        "→ система команд",
        "(ISA)",
        "",
        "Steve Furber",
        "→ мікроархітек-",
        "тура й логіка",
        "",
        "Команда Acorn",
        "→ кремній і тести",
    ]
    frags.append(mtext(c3x, box_top + 52, res_lines, size=11, color=INK, lh=1.28))

    # Підпис внизу
    frags.append(text(W / 2, H - 12,
                      "Технічний тупик + знятий психологічний бар'єр = народження ARM",
                      size=10, color=MUTED))

    render(os.path.join(OUT, "fig-11-0-1-why-own-cpu.svg"), W, H, *frags,
           title=None)
    print("fig-11-0-1-why-own-cpu.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.11.0.2 — RISC проти CISC
# Дві картки-колонки з контрастними рядками
# ══════════════════════════════════════════════════════════════════════════════
def fig2_risc_vs_cisc():
    W, H = 720, 360
    frags = []

    frags.append(text(W / 2, 28, "Дві філософії системи команд", size=15, bold=True))

    card_w = 280
    card_h = 270
    gap = 60
    left_x = W / 2 - gap / 2 - card_w
    right_x = W / 2 + gap / 2

    top_y = 48

    # --- CISC карта ---
    frags.append(rect(left_x, top_y, card_w, card_h,
                      fill="#fef2f2", stroke=POS, sw=2.5, rx=12))
    frags.append(text(left_x + card_w / 2, top_y + 26, "CISC", size=16, bold=True, color=POS))
    frags.append(text(left_x + card_w / 2, top_y + 42,
                      "(x86, 68000, VAX)", size=10, color=MUTED))

    cisc_rows = [
        ("Регістрів:", "мало (8–16)"),
        ("Команд:", "багато (сотні)"),
        ("Довжина команди:", "різна (1–15 байт)"),
        ("Декодер:", "складний"),
        ("Конвеєр:", "важко заповнити"),
    ]
    ry = top_y + 68
    for label, val in cisc_rows:
        frags.append(text(left_x + 14, ry, label, size=11, color=MUTED, anchor="start"))
        frags.append(text(left_x + card_w - 14, ry, val, size=11, color=INK, anchor="end", bold=True))
        frags.append(line(left_x + 10, ry + 8, left_x + card_w - 10, ry + 8,
                          color="#e5e7eb", sw=1))
        ry += 36

    # --- RISC (ARM) карта ---
    frags.append(rect(right_x, top_y, card_w, card_h,
                      fill="#f0fdf4", stroke=FIELD, sw=2.5, rx=12))
    frags.append(text(right_x + card_w / 2, top_y + 26, "RISC (ARM)", size=16, bold=True, color=FIELD))
    frags.append(text(right_x + card_w / 2, top_y + 42,
                      "(Acorn RISC Machine)", size=10, color=MUTED))

    risc_rows = [
        ("Регістрів:", "багато (16–32)"),
        ("Команд:", "мало (~70)"),
        ("Довжина команди:", "фіксована (4 байт)"),
        ("Декодер:", "простий"),
        ("Конвеєр:", "рівний, швидкий"),
    ]
    ry = top_y + 68
    for label, val in risc_rows:
        frags.append(text(right_x + 14, ry, label, size=11, color=MUTED, anchor="start"))
        frags.append(text(right_x + card_w - 14, ry, val, size=11, color=FIELD, anchor="end", bold=True))
        frags.append(line(right_x + 10, ry + 8, right_x + card_w - 10, ry + 8,
                          color="#d1fae5", sw=1))
        ry += 36

    # --- VS між картками ---
    vs_cx = W / 2
    vs_cy = top_y + card_h / 2
    frags.append(circle(vs_cx, vs_cy, 20, fill="#f4f6f8", stroke=LINE, sw=1.5))
    frags.append(text(vs_cx, vs_cy + 5, "VS", size=12, bold=True, color=INK))

    # Підпис
    frags.append(text(W / 2, H - 14,
                      "Проста архітектура RISC — і та, що під силу крихітній команді Acorn",
                      size=10, color=MUTED))

    render(os.path.join(OUT, "fig-11-0-2-risc-vs-cisc.svg"), W, H, *frags,
           title=None)
    print("fig-11-0-2-risc-vs-cisc.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
# Рис. 4.11.0.3 — Бізнес-модель ARM: ліцензування ядра
# ARM у центрі; стрілки-ліцензії до 4 виробників; зворотні стрілки — роялті
# ══════════════════════════════════════════════════════════════════════════════
def fig3_licensing():
    W, H = 820, 400
    frags = []

    frags.append(text(W / 2, 28, "Бізнес-модель ARM: продавати дизайн ядра, а не чипи", size=15, bold=True))

    # --- ARM у центрі ---
    cx, cy = W / 2, H / 2 + 10
    arm_w, arm_h = 180, 90

    frags.append(rect(cx - arm_w / 2, cy - arm_h / 2, arm_w, arm_h,
                      fill="#eff6ff", stroke=NEG, sw=2.5, rx=12))
    frags.append(mtext(cx, cy - 8, ["ARM Ltd", "дизайн ядра Cortex-M", "(без власних фабрик)"],
                       size=12, bold=False, lh=1.3))
    frags.append(text(cx, cy + 32, "", size=11, color=MUTED))

    # --- Чотири ліцензіати ---
    vendors = [
        ("STMicroelectronics", "STM32\n(Cortex-M + СВОЯ\nпериферія)", -280, -120),
        ("Raspberry Pi", "RP2040\n(Cortex-M + СВОЯ\nпериферія)", 280, -120),
        ("Nordic Semiconductor", "nRF-серія\n(Cortex-M + СВОЯ\nпериферія)", -280, 140),
        ("NXP Semiconductors", "LPC / Kinetis\n(Cortex-M + СВОЯ\nпериферія)", 280, 140),
    ]

    vbox_w, vbox_h = 190, 80

    for name, chip, dx, dy in vendors:
        vx = cx + dx
        vy = cy + dy

        frags.append(rect(vx - vbox_w / 2, vy - vbox_h / 2, vbox_w, vbox_h,
                          fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=9))
        frags.append(text(vx, vy - vbox_h / 2 + 16, name, size=10, bold=True, color=FIELD))
        chip_lines = chip.split("\n")
        frags.append(mtext(vx, vy + 4, chip_lines, size=10, color=INK, lh=1.3))

        # Стрілка: ARM → ліцензіат (ліцензія)
        # Визначаємо кінцеву точку на межі ARM-рамки і початкову на межі vendor-рамки
        # Напрямок: від ARM до vendor
        sign_dx = 1 if dx > 0 else -1
        sign_dy = 1 if dy > 0 else -1

        # Точки на межах ARM-рамки (вихідна) та vendor-рамки (вхідна)
        if abs(dx) > abs(dy):
            arm_px = cx + sign_dx * arm_w / 2
            arm_py = cy + dy * (arm_h / 2) / abs(dy) if dy != 0 else cy
            arm_py = min(max(arm_py, cy - arm_h / 2 + 10), cy + arm_h / 2 - 10)
            ven_px = vx - sign_dx * vbox_w / 2
            ven_py = vy
        else:
            arm_px = cx + dx * (arm_w / 2) / abs(dx) if dx != 0 else cx
            arm_px = min(max(arm_px, cx - arm_w / 2 + 10), cx + arm_w / 2 - 10)
            arm_py = cy + sign_dy * arm_h / 2
            ven_px = vx
            ven_py = vy - sign_dy * vbox_h / 2

        # Зсув для паралельних стрілок (ліцензія і роялті поряд)
        perp_x = -sign_dy * 5 if abs(dx) > abs(dy) else sign_dx * 5
        perp_y = sign_dx * 5 if abs(dx) > abs(dy) else -sign_dy * 5

        # Ліцензія ARM → vendor (синя)
        frags.append(arrow(arm_px + perp_x, arm_py + perp_y,
                           ven_px + perp_x, ven_py + perp_y,
                           color=NEG, sw=1.8))

        # Роялті vendor → ARM (зелена, зворотна)
        frags.append(arrow(ven_px - perp_x, ven_py - perp_y,
                           arm_px - perp_x, arm_py - perp_y,
                           color=FIELD, sw=1.5))

    # Легенда
    leg_x = 20
    leg_y = H - 36
    frags.append(line(leg_x, leg_y, leg_x + 30, leg_y, color=NEG, sw=2))
    frags.append(arrow(leg_x, leg_y, leg_x + 30, leg_y, color=NEG, sw=1.8))
    frags.append(text(leg_x + 38, leg_y + 4, "ліцензія (ARM → виробник)", size=10,
                      color=INK, anchor="start"))

    leg_y2 = H - 16
    frags.append(line(leg_x, leg_y2, leg_x + 30, leg_y2, color=FIELD, sw=1.5))
    frags.append(arrow(leg_x, leg_y2, leg_x + 30, leg_y2, color=FIELD, sw=1.5))
    frags.append(text(leg_x + 38, leg_y2 + 4, "роялті з кожного чипа (виробник → ARM)",
                      size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "fig-11-0-3-licensing.svg"), W, H, *frags,
           title=None)
    print("fig-11-0-3-licensing.svg — OK")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    fig1_why_own_cpu()
    fig2_risc_vs_cisc()
    fig3_licensing()
    print("Усі фігури збережено в", OUT)
