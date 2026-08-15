# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: Асиметрія напіврозв'язності (RE) ───────────────────────────────────
def fig_re_asymmetry():
    W, H = 840, 340
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=BG, stroke=MUTED, sw=1.0, rx=8))
    p.append(text(W / 2, 38, "Асиметрія напіврозв'язності (Semi-decidability)", size=15, color=INK, bold=True))

    # Ліва частина: Вхід x належить S (x ∈ S)
    p.append(rect(40, 75, 360, 230, fill="#f4faf5", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(220, 102, "Випадок 1: x ∈ S (належить)", size=13, color=FIELD, bold=True))

    b1, bw1, bh1 = textbox(220, 155, "Напіввирішувач M(x)\nВиконує обчислення...", size=11.5, fill=FILL, stroke=INK)
    p.append(b1)
    p.append(arrow(220, 185, 220, 225, color=FIELD, sw=1.8))
    b2, bw2, bh2 = textbox(220, 255, "ЗУПИНКА: Вихід 1 («ТАК»)\nВідповідь отримана за скінченний час", size=11.5, bold=True, fill="#e7f6e9", stroke=FIELD, color=FIELD)
    p.append(b2)

    # Права частина: Вхід x не належить S (x ∉ S)
    p.append(rect(440, 75, 360, 230, fill="#faf4f4", stroke=POS, sw=1.5, rx=6))
    p.append(text(620, 102, "Випадок 2: x ∉ S (не належить)", size=13, color=POS, bold=True))

    b3, bw3, bh3 = textbox(620, 155, "Напіввирішувач M(x)\nВиконує обчислення...", size=11.5, fill=FILL, stroke=INK)
    p.append(b3)
    p.append(arrow(620, 185, 620, 225, color=POS, sw=1.8))
    b4, bw4, bh4 = textbox(620, 255, "НЕСКІНЧЕННИЙ ЦИКЛ (∞)\nАбо відмова (Ні) / Зависання без відповіді", size=11.5, bold=True, fill="#fdeaea", stroke=POS, color=POS)
    p.append(b4)

    render(os.path.join(OUT, "re-asymmetry.svg"), W, H, *p,
           title="Асиметрія напіврозв'язності: зупинка гарантована лише для належних елементів")


# ── Фіг. 2: Схема паралельного перебирання (Dovetailing) ──────────────────────
def fig_dovetailing_grid():
    W, H = 840, 420
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=BG, stroke=MUTED, sw=1.0, rx=8))
    p.append(text(W / 2, 38, "Механізм Dovetailing (Діагональне обходити 2D-сітку кроків)", size=15, color=INK, bold=True))

    # Сітка n x k (n - номер елемента/завдання, k - кількість кроків)
    ox, oy = 180, 100
    cw, ch = 85, 45
    cols, rows = 5, 5

    # Вісі
    p.append(text(ox - 60, oy - 25, "Завдання i ↓ / Кроки k →", size=11.5, color=MUTED, bold=True))
    for c in range(cols):
        p.append(text(ox + c * cw + cw / 2, oy - 12, f"k = {c + 1}", size=11, color=INK, bold=True))
    for r in range(rows):
        p.append(text(ox - 30, oy + r * ch + ch / 2 + 4, f"i = {r}", size=11, color=INK, bold=True))

    # Обхід діагоналями: s = i + c
    diag_order = {}
    idx = 1
    for s in range(cols + rows - 1):
        for r in range(s + 1):
            c = s - r
            if r < rows and c < cols:
                diag_order[(r, c)] = idx
                idx += 1

    for r in range(rows):
        for c in range(cols):
            x = ox + c * cw
            y = oy + r * ch
            order = diag_order.get((r, c), 0)
            fill_color = "#e8f4fc" if order > 0 and order <= 12 else FILL
            stroke_color = FIELD if order > 0 and order <= 12 else MUTED

            p.append(rect(x, y, cw - 4, ch - 4, fill=fill_color, stroke=stroke_color, sw=1.2, rx=4))
            p.append(text(x + cw / 2 - 2, y + ch / 2 + 4, f"#{order}" if order > 0 else "…", size=11, color=INK, bold=True))

    # Пояснювальний текст праворуч від сітки
    p.append(rect(620, 100, 190, 220, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(715, 125, "Порядок обходу:", size=12, color=FIELD, bold=True))
    p.append(text(715, 155, "1. (i=0, k=1)", size=10.5, color=INK))
    p.append(text(715, 180, "2. (i=0, k=2)", size=10.5, color=INK))
    p.append(text(715, 205, "3. (i=1, k=1)", size=10.5, color=INK))
    p.append(text(715, 230, "4. (i=0, k=3)", size=10.5, color=INK))
    p.append(text(715, 255, "5. (i=1, k=2)", size=10.5, color=INK))
    p.append(text(715, 280, "6. (i=2, k=1)", size=10.5, color=INK))
    p.append(text(715, 305, "… діагональ s = i+k", size=10, color=MUTED, bold=True))

    p.append(text(W / 2, 385, "Гарантія: якщо обчислення (i) зупиниться за k кроків, воно буде знайдене за скінченний час!", size=11.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "dovetailing-grid.svg"), W, H, *p,
           title="Механізм Dovetailing для уникнення нескінченного зациклення на одному вході")


# ── Фіг. 3: Теорема Поста (R = RE ∩ coRE) ─────────────────────────────────────
def fig_posts_theorem():
    W, H = 840, 360
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=BG, stroke=MUTED, sw=1.0, rx=8))
    p.append(text(W / 2, 38, "Теорема Поста: Конструкція повного вирішувача", size=15, color=INK, bold=True))

    bx = 60
    p.append(rect(bx, 80, 720, 240, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))

    # Вхід x
    p.append(text(bx + 40, 200, "Вхід x", size=13, color=INK, bold=True))
    p.append(arrow(bx + 75, 200, bx + 140, 140, color=INK, sw=1.6))
    p.append(arrow(bx + 75, 200, bx + 140, 260, color=INK, sw=1.6))

    # Верхній блок M_S
    b_s, bw_s, bh_s = textbox(bx + 260, 140, "Напіввирішувач M_S(x)\n(Перевіряє x ∈ S)", size=11.5, fill="#eaf7ed", stroke=FIELD)
    p.append(b_s)
    p.append(arrow(bx + 380, 140, bx + 480, 140, color=FIELD, sw=1.6))
    p.append(text(bx + 430, 125, "якщо зупинився", size=10, color=FIELD))

    # Нижній блок M_barS
    b_bs, bw_bs, bh_bs = textbox(bx + 260, 260, "Напіввирішувач M_S̄(x)\n(Перевіряє x ∉ S)", size=11.5, fill="#fdeaea", stroke=POS)
    p.append(b_bs)
    p.append(arrow(bx + 380, 260, bx + 480, 260, color=POS, sw=1.6))
    p.append(text(bx + 430, 245, "якщо зупинився", size=10, color=POS))

    # Блок арбітра / об'єднувача
    b_arb, bw_arb, bh_arb = textbox(bx + 580, 200, "Арбітр паралельного запуску\n(Паралельний кроковий обхід)", size=11.5, fill=FILL, stroke=INK)
    p.append(b_arb)
    p.append(arrow(bx + 660, 200, bx + 700, 200, color=INK, sw=1.8))
    p.append(text(bx + 710, 190, "Вихід: ТАК / НІ", size=12, color=FIELD, bold=True, anchor="start"))
    p.append(text(bx + 710, 215, "(Гарантована зупинка)", size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "posts-theorem.svg"), W, H, *p,
           title="Побудова двостороннього вирішувача за теоремою Поста")


# ── Фіг. 4: Ієрархія обчислюваності (R ⊂ RE ⊂ 2^N) ─────────────────────────────
def fig_re_hierarchy():
    W, H = 840, 400
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill=BG, stroke=MUTED, sw=1.0, rx=8))
    p.append(text(W / 2, 35, "Ієрархія множин за обчислюваністю", size=15, color=INK, bold=True))

    # Зовнішній прямокутник - Всі множини 2^N
    p.append(rect(50, 60, 740, 310, fill="#f4f5f7", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(80, 85, "Усі підмножини ℕ (Нерахованно багато, 2^ℵ₀)", size=12, color=MUTED, bold=True, anchor="start"))

    # Секція RE \ R (Рекурсивно перелічні нерозв'язні)
    p.append(rect(80, 120, 210, 220, fill="#eaf3ec", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(185, 145, "RE \\ R", size=13, color=FIELD, bold=True))
    p.append(text(185, 168, "(Тільки Напіврозв'язні)", size=10.5, color=MUTED))

    # Секція R = RE ∩ coRE (Розв'язні)
    p.append(rect(315, 120, 210, 220, fill="#e8f0fe", stroke="#1a73e8", sw=2.0, rx=8))
    p.append(text(420, 145, "R = RE ∩ coRE", size=13, color="#1a73e8", bold=True))
    p.append(text(420, 168, "(Повністю Розв'язні)", size=10.5, color="#1a73e8"))

    # Секція coRE \ R (Доповнення RE нерозв'язні)
    p.append(rect(550, 120, 210, 220, fill="#faecec", stroke=POS, sw=1.8, rx=8))
    p.append(text(655, 145, "coRE \\ R", size=13, color=POS, bold=True))
    p.append(text(655, 168, "(Тільки Ко-напіврозв'язні)", size=10.5, color=MUTED))

    # Приклади множин
    # K в RE \ R
    p.append(circle(185, 230, 5, fill=FIELD))
    p.append(text(185, 255, "K (Проблема зупинки)", size=11, color=FIELD, bold=True))

    # Множина в R
    p.append(circle(420, 230, 5, fill="#1a73e8"))
    p.append(text(420, 255, "Парні числа / A* (Розв'язні)", size=11, color="#1a73e8", bold=True))

    # K_bar в coRE \ R
    p.append(circle(655, 230, 5, fill=POS))
    p.append(text(655, 255, "K̄ (Неперелічна)", size=11, color=POS, bold=True))

    render(os.path.join(OUT, "re-hierarchy.svg"), W, H, *p,
           title="Ієрархія класів R, RE, coRE та всіх підмножин натуральних чисел")


if __name__ == "__main__":
    fig_re_asymmetry()
    fig_dovetailing_grid()
    fig_posts_theorem()
    fig_re_hierarchy()
    print("All figures generated successfully.")
