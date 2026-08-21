# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репо (чотири рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE_BG = "#0f1b14"
CODE_FG = "#eaf6ee"
BLOCK_BG = "#f4f7f9"
BLOCK_BORDER = "#2c3e50"


def codeblock(x, y, w, lines, fg=CODE_FG, bg=CODE_BG, size=12, title=None, tcol="#9fb4a6"):
    """Рамка з моноширинним кодом."""
    lh = size * 1.45
    top_pad = 16 if title else 10
    h = top_pad + len(lines) * lh + 10
    out = rect(x, y, w, h, fill=bg, stroke="#0a120d", sw=1.4, rx=6)
    ty = y + top_pad
    if title:
        out += ('<text x="%.1f" y="%.1f" font-family="%s" font-size="10" fill="%s" '
                'text-anchor="start" font-weight="700">%s</text>' % (x + 10, ty, FONT, tcol, esc(title)))
        ty += lh
    for ln in lines:
        out += ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
                'font-size="%d" fill="%s" text-anchor="start">%s</text>'
                % (x + 10, ty + size * 0.35, size, fg, esc(ln)))
        ty += lh
    return out, h


# ── 1. Анатомія базового блоку та передавальна функція ────────────────────────
def fig_cfg_transfer():
    W, H = 840, 400
    p = []
    p.append(text(W / 2, 28, "Анатомія базового блоку: вхідні факти, трансформація та вихід", size=16, bold=True))

    # Попередники (Pred 1, Pred 2)
    b_p1, _, _ = textbox(160, 80, "Попередник P₁\nOUT[P₁]", size=12, pad=8, fill="#eaf2f8", stroke="#2980b9", bold=True)
    b_p2, _, _ = textbox(360, 80, "Попередник P₂\nOUT[P₂]", size=12, pad=8, fill="#eaf2f8", stroke="#2980b9", bold=True)
    p.append(b_p1)
    p.append(b_p2)

    # Вузол злиття (Meet / Join)
    p.append(circle(260, 150, 22, fill="#fef9e7", stroke="#d4ac0d", sw=1.8))
    p.append(text(260, 155, "⊓ / ∪", size=13, color="#7d6608", bold=True))
    p.append(text(340, 153, "Оператор злиття (Meet)", size=11, color=MUTED, anchor="start"))

    p.append(arrow(160, 105, 245, 138, color="#2980b9", sw=1.6))
    p.append(arrow(360, 105, 275, 138, color="#2980b9", sw=1.6))

    # Стрілка від Join до IN[B]
    p.append(arrow(260, 172, 260, 205, color=LINE, sw=1.8))
    p.append(text(275, 195, "IN[B] = OUT[P₁] ⊓ OUT[P₂]", size=11, color=INK, anchor="start", bold=True))

    # Базовий блок B
    bx, by, bw, bh = 140, 210, 240, 115
    p.append(rect(bx, by, bw, bh, fill=BLOCK_BG, stroke=BLOCK_BORDER, sw=1.8, rx=8))
    p.append(text(bx + bw / 2, by + 18, "Базовий блок B", size=13, bold=True))

    # Інструкції всередині блоку
    c_blk, _ = codeblock(bx + 15, by + 28, bw - 30, ["a = b + c", "d = a * 2"], size=11, fg="#d1f2eb", bg="#1b2631")
    p.append(c_blk)

    # Вихідний стан OUT[B]
    p.append(arrow(260, by + bh, 260, by + bh + 35, color=LINE, sw=1.8))
    p.append(text(260, by + bh + 48, "OUT[B] = f_B(IN[B])", size=12, color=INK, bold=True))

    # Панель пояснення передавальної функції праворуч
    px, py, pw, ph = 500, 70, 310, 280
    p.append(rect(px, py, pw, ph, fill="#fafafa", stroke="#bdc3c7", sw=1.2, rx=8))
    p.append(text(px + pw / 2, py + 22, "Передавальна функція (Transfer)", size=13, bold=True, color="#2c3e50"))

    expl = [
        "Стан програми перетворюється",
        "інструкціями блоку B за формулою:",
        "",
        "f_B(x) = GEN[B] ∪ (x \\ KILL[B])",
        "",
        "• GEN[B] — факти, породжені блоком",
        "  (нові визначення або доступні вирази)",
        "• KILL[B] — факти, знищені блоком",
        "  (старі визначення або перезаписані змінні)",
        "• x \\ KILL[B] — збережені вхідні факти"
    ]
    p.append(mtext(px + 16, py + 48, expl, size=11, color=INK, anchor="start", lh=1.35))

    render(os.path.join(OUT, "cfg-transfer.svg"), W, H, *p, title=None)


# ── 2. Напівґратка станів (Semilattice) ────────────────────────────────────────
def fig_semilattice_meet():
    W, H = 820, 380
    p = []
    p.append(text(W / 2, 26, "Напівґратка станів (Semilattice) для поширення констант", size=16, bold=True))

    # Top element ⊤
    t_box, _, _ = textbox(W / 2, 75, "Вершина ⊤ (Top)\n«Ще не ініціалізовано / будь-яка константа»",
                          size=12, pad=8, fill="#e8f8f5", stroke=FIELD, bold=True)
    p.append(t_box)

    # Проміжний рівень: конкретні константи
    c_nodes = [
        (160, 180, "c = 1"),
        (290, 180, "c = 2"),
        (410, 180, "c = 3"),
        (540, 180, "c = 42"),
        (660, 180, "c = k …")
    ]
    for cx, cy, lbl in c_nodes:
        bx, _, _ = textbox(cx, cy, lbl, size=12, pad=6, fill="#fef9e7", stroke="#f39c12", bold=True)
        p.append(bx)
        p.append(line(W / 2, 100, cx, cy - 16, color=MUTED, sw=1.2))

    # Bottom element ⊥
    b_box, _, _ = textbox(W / 2, 295, "Основа ⊥ (Bottom)\n«Невідомо / не є константою (Overdefined / NAC)»",
                          size=12, pad=8, fill="#fdecea", stroke=POS, bold=True)
    p.append(b_box)

    for cx, cy, _ in c_nodes:
        p.append(line(cx, cy + 16, W / 2, 270, color=MUTED, sw=1.2))

    # Правила злиття
    p.append(text(120, 355, "Правила злиття (Meet ⊓):", size=11, bold=True, anchor="start"))
    p.append(text(270, 355, "⊤ ⊓ x = x", size=11, color=FIELD, anchor="start", bold=True))
    p.append(text(380, 355, "c₁ ⊓ c₁ = c₁", size=11, color="#d35400", anchor="start", bold=True))
    p.append(text(490, 355, "c₁ ⊓ c₂ = ⊥  (якщо c₁ ≠ c₂)", size=11, color=POS, anchor="start", bold=True))
    p.append(text(680, 355, "⊥ ⊓ x = ⊥", size=11, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "semilattice-meet.svg"), W, H, *p, title=None)


# ── 3. Класифікація 4 класичних задач потоку даних ───────────────────────────
def fig_dataflow_directions():
    W, H = 840, 370
    p = []
    p.append(text(W / 2, 26, "Класифікація задач потоку даних: напрямок × квантор шляхів", size=16, bold=True))

    # Колонки (Forward, Backward) та Рядки (May, Must)
    p.append(text(310, 60, "Прямий аналіз (Forward, →)", size=14, bold=True, color="#1b4f72"))
    p.append(text(630, 60, "Зворотний аналіз (Backward, ←)", size=14, bold=True, color="#1b4f72"))

    p.append(text(60, 135, "May (Чи можливо?)\nОб'єднання ∪\n«Існує шлях»", size=11, bold=True, color="#784212"))
    p.append(text(60, 255, "Must (Чи гарантовано?)\nПеретин ∩\n«На всіх шляхах»", size=11, bold=True, color="#145a32"))

    # Сітка квадрантів
    quads = [
        # (x, y, title, task_name, formula, init_info, color_bg, color_stroke)
        (180, 80, 260, 115, "Reaching Definitions",
         "Які визначення змінних доходять сюди?",
         "OUT[B] = GEN[B] ∪ (IN[B] \\ KILL[B])",
         "IN[B] = ∪ OUT[P],  ініціалізація: ∅",
         "#ebf5fb", "#2980b9"),

        (500, 80, 260, 115, "Live Variables",
         "Чи буде значення змінної прочитане далі?",
         "IN[B] = USE[B] ∪ (OUT[B] \\ DEF[B])",
         "OUT[B] = ∪ IN[S],  ініціалізація: ∅",
         "#fef5e7", "#d35400"),

        (180, 205, 260, 115, "Available Expressions",
         "Які вирази вже гарантовано обчислені?",
         "OUT[B] = GEN[B] ∪ (IN[B] \\ KILL[B])",
         "IN[B] = ∩ OUT[P],  ініціалізація: ALL",
         "#eafaf1", "#27ae60"),

        (500, 205, 260, 115, "Very Busy Expressions",
         "Які вирази обов'язково виконаються далі?",
         "IN[B] = USE[B] ∪ (OUT[B] \\ KILL[B])",
         "OUT[B] = ∩ IN[S],  ініціалізація: ALL",
         "#f4ecf7", "#8e44ad"),
    ]

    for qx, qy, qw, qh, title, desc, f_trans, f_meet, bg, stroke in quads:
        p.append(rect(qx, qy, qw, qh, fill=bg, stroke=stroke, sw=1.5, rx=6))
        p.append(text(qx + qw / 2, qy + 18, title, size=12, bold=True, color=stroke))
        p.append(text(qx + qw / 2, qy + 36, desc, size=10, color=INK, italic=True))
        p.append(text(qx + qw / 2, qy + 64, f_trans, size=10, color=INK, bold=True))
        p.append(text(qx + qw / 2, qy + 88, f_meet, size=10, color=MUTED))

    p.append(text(W / 2, 345, "Квантор May стартує з ∅ (песимістично), квантор Must стартує з ALL (оптимістично)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "dataflow-directions.svg"), W, H, *p, title=None)


# ── 4. Use-Def ланцюжки у загальному CFG проти SSA ────────────────────────────
def fig_ssa_du_chains():
    W, H = 840, 360
    p = []
    p.append(text(W / 2, 26, "Потік даних: щільний аналіз у традиційному CFG проти розрідженого в SSA", size=16, bold=True))

    # Ліва половина: Звичайний CFG
    lx = 30
    p.append(rect(lx, 55, 370, 280, fill="#fcfcfc", stroke="#bdc3c7", sw=1.2, rx=8))
    p.append(text(lx + 185, 78, "Традиційний CFG (Щільний аналіз)", size=13, bold=True, color="#2c3e50"))

    # Блоки традиційного CFG
    b1, _ = codeblock(lx + 120, 95, 130, ["x = 10", "if (cond)"], size=10, title="Блок B1")
    b2, _ = codeblock(lx + 30, 175, 130, ["x = 20"], size=10, title="Блок B2")
    b3, _ = codeblock(lx + 210, 175, 130, ["y = 5"], size=10, title="Блок B3")
    b4, _ = codeblock(lx + 120, 250, 130, ["z = x + 1"], size=10, title="Блок B4")

    p.append(b1)
    p.append(b2)
    p.append(b3)
    p.append(b4)

    p.append(arrow(lx + 150, 145, lx + 95, 175, color=LINE, sw=1.3))
    p.append(arrow(lx + 220, 145, lx + 275, 175, color=LINE, sw=1.3))
    p.append(arrow(lx + 95, 220, lx + 150, 250, color=LINE, sw=1.3))
    p.append(arrow(lx + 275, 220, lx + 220, 250, color=LINE, sw=1.3))

    p.append(text(lx + 185, 318, "IN/OUT бітові вектори на кожному кроці\nРозмір стану: O(кількість блоків × змінні)",
                  size=10, color=MUTED))

    # Права половина: SSA форма
    rx = 440
    p.append(rect(rx, 55, 370, 280, fill="#fcfcfc", stroke="#bdc3c7", sw=1.2, rx=8))
    p.append(text(rx + 185, 78, "Форма SSA (Розріджений аналіз)", size=13, bold=True, color="#27ae60"))

    sb1, _ = codeblock(rx + 120, 95, 130, ["x₁ = 10", "if (cond)"], size=10, title="Блок B1")
    sb2, _ = codeblock(rx + 30, 175, 130, ["x₂ = 20"], size=10, title="Блок B2")
    sb3, _ = codeblock(rx + 210, 175, 130, ["y₁ = 5"], size=10, title="Блок B3")
    sb4, _ = codeblock(rx + 105, 250, 160, ["x₃ = ϕ(x₂, x₁)", "z₁ = x₃ + 1"], size=10, title="Блок B4")

    p.append(sb1)
    p.append(sb2)
    p.append(sb3)
    p.append(sb4)

    p.append(arrow(rx + 150, 145, rx + 95, 175, color=LINE, sw=1.3))
    p.append(arrow(rx + 220, 145, rx + 275, 175, color=LINE, sw=1.3))
    p.append(arrow(rx + 95, 220, rx + 150, 250, color=LINE, sw=1.3))
    p.append(arrow(rx + 275, 220, rx + 220, 250, color=LINE, sw=1.3))

    # Пряме ребро SSA Use-Def (зелене пунктирне)
    p.append(arrow(rx + 160, 130, rx + 240, 250, color="#27ae60", sw=1.8))
    p.append(text(rx + 185, 318, "Значення течуть прямо через ребра Use-Def та ϕ\nНемає потреби перераховувати B3!",
                  size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "ssa-du-chains.svg"), W, H, *p, title=None)


if __name__ == "__main__":
    fig_cfg_transfer()
    fig_semilattice_meet()
    fig_dataflow_directions()
    fig_ssa_du_chains()
    print("All figures generated successfully.")
