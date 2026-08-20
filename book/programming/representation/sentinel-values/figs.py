# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. in-band-vs-out-of-band: порівняння сигналізації ─────────────────────────
def fig_in_band_vs_out_of_band():
    W, H = 760, 360
    p = []
    midx = W / 2

    # Розділювач
    p.append(line(midx, 40, midx, H - 30, color=MUTED, sw=1.2, dash="5 5"))

    # ЛІВА КОЛОНКА: In-band
    lx = midx / 2
    p.append(text(lx, 42, "In-band (внутрішньосмугова)", size=15, bold=True, color=POS))
    p.append(text(lx, 62, "Одне спільне поле: дані + сигнал відсутності", size=12, color=MUTED))

    # Блок даних з вартовим всередині
    bx = lx - 140
    p.append(rect(bx, 85, 280, 48, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(rect(bx, 85, 200, 48, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    p.append(rect(bx + 200, 85, 80, 48, fill="#fdecea", stroke=POS, sw=1.8, rx=6))
    p.append(text(bx + 100, 114, "Дійсні значення (0..254)", size=12, color=NEG, bold=True))
    p.append(text(bx + 240, 114, "−1 / 0xFF", size=12, color=POS, bold=True))
    p.append(text(bx + 240, 148, "вартовий краде 1 стан", size=10, color=POS, italic=True))

    p.append(fitbox(bx, 170, 280, 140,
                    "Плюси:\n"
                    "• 0 байтів оверхеду пам'яті\n"
                    "• Працює у примітивних типах\n\n"
                    "Мінуси:\n"
                    "• Втрата валідного значення\n"
                    "• Можна забути перевірити (баг)\n"
                    "• Плутанина між даними й помилкою",
                    size=12, pad=10, fill="#fffaf9", stroke=POS, sw=1.4))

    # ПРАВА КОЛОНКА: Out-of-band
    rx = midx + midx / 2
    p.append(text(rx, 42, "Out-of-band (позасмугова)", size=15, bold=True, color=FIELD))
    p.append(text(rx, 62, "Окремий канал: статус існує окремо від даних", size=12, color=MUTED))

    # Два окремих блоки
    rbx = rx - 140
    p.append(rect(rbx, 85, 90, 48, fill="#ebfbee", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(rbx + 45, 108, "Тег статусу", size=11, color=FIELD, bold=True))
    p.append(text(rbx + 45, 124, "Some / None", size=10, color=FIELD))

    p.append(rect(rbx + 100, 85, 180, 48, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    p.append(text(rbx + 190, 114, "Повний діапазон типу T", size=12, color=NEG, bold=True))
    p.append(text(rbx + 190, 148, "усі 256/4G станів доступні", size=10, color=FIELD, italic=True))

    p.append(fitbox(rbx, 170, 280, 140,
                    "Плюси:\n"
                    "• Безпека на рівні типів\n"
                    "• Жодне число не втрачається\n"
                    "• Компілятор змушує перевіряти\n\n"
                    "Мінуси:\n"
                    "• Додаткова пам'ять (+паддінг)\n"
                    "• Потрібна підтримка мови / Option",
                    size=12, pad=10, fill="#f6fcf8", stroke=FIELD, sw=1.4))

    render(os.path.join(OUT, "in-band-vs-out-of-band.svg"), W, H, *p,
           title="In-band проти Out-of-band сигналізації відсутності значення")


# ── 2. getchar-eof-widening: чому getchar повертає int замість char ───────────
def fig_getchar_eof_widening():
    W, H = 760, 340
    p = []

    p.append(text(W / 2, 42, "Чому getchar() повертає 32-бітний int, а не 8-бітний char", size=14, bold=True))

    # Верхній блок: Байт 0xFF з файлу
    p.append(text(160, 80, "Байт 0xFF (255) з файлу:", size=12, bold=True, anchor="start"))
    p.append(rect(340, 64, 100, 30, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    p.append(text(390, 84, "11111111", size=13, bold=True, color=NEG))
    p.append(text(460, 84, "= 255 у беззнаковому байті", size=11, color=MUTED, anchor="start"))

    # Стрілка розширення до int
    p.append(arrow(390, 98, 390, 130, color=LINE, sw=1.5))
    p.append(text(405, 118, "розширення до 32 бітів (int)", size=10, color=MUTED, anchor="start"))

    # Два випадки в 32-бітному int
    # Випадок А: Валідний прочитаний байт 0xFF
    y_a = 145
    p.append(rect(60, y_a, 640, 60, fill="#f4fbf6", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(80, y_a + 25, "Валідний байт 255 як int:", size=12, bold=True, anchor="start", color=FIELD))
    p.append(text(80, y_a + 46, "0x000000FF  (старші 24 біти = 0, молодші 8 бітів = 11111111)", size=12, anchor="start", color=INK))
    p.append(text(580, y_a + 35, "= +255", size=14, bold=True, color=FIELD))

    # Випадок Б: Вартове значення EOF
    y_b = 220
    p.append(rect(60, y_b, 640, 60, fill="#fdf4f4", stroke=POS, sw=1.5, rx=6))
    p.append(text(80, y_b + 25, "Вартове значення EOF (-1) як int:", size=12, bold=True, anchor="start", color=POS))
    p.append(text(80, y_b + 46, "0xFFFFFFFF  (усі 32 біти встановлені в 1 у доповняльному коді)", size=12, anchor="start", color=INK))
    p.append(text(580, y_b + 35, "= −1 (EOF)", size=14, bold=True, color=POS))

    # Висновок внизу
    p.append(text(W / 2, 312, "У 32-бітному int значення 0x000000FF (255) та 0xFFFFFFFF (-1) ніколи не перетинаються!",
                  size=12, color=INK, italic=True, bold=True))

    render(os.path.join(OUT, "getchar-eof-widening.svg"), W, H, *p,
           title="Розширення типу: розділення валідного байта 0xFF та EOF (-1)")


# ── 3. sentinel-linked-list: звичайний список проти списку з вартовим ─────────
def fig_sentinel_linked_list():
    W, H = 760, 360
    p = []
    midy = 175

    # Розділювач
    p.append(line(30, midy, W - 30, midy, color=MUTED, sw=1, dash="4 4"))

    # ВЕРХ: Звичайний список з NULL
    p.append(text(40, 30, "А. Звичайний двозв'язний список (краї впираються в NULL):", size=13, bold=True, anchor="start"))

    # Head ptr
    p.append(rect(40, 55, 60, 32, fill="#f0f0f0", stroke=LINE, sw=1.2, rx=4))
    p.append(text(70, 75, "head", size=11, bold=True))
    p.append(arrow(100, 71, 135, 71, color=LINE, sw=1.5))

    # Node 1
    p.append(rect(140, 48, 100, 46, fill=FILL, stroke=LINE, sw=1.4, rx=4))
    p.append(text(190, 74, "Вузол A", size=12, bold=True))
    p.append(text(152, 60, "NULL", size=9, color=POS))
    p.append(line(140, 48, 165, 94, color=POS, sw=1)) # X for null prev

    # Node 2
    p.append(rect(300, 48, 100, 46, fill=FILL, stroke=LINE, sw=1.4, rx=4))
    p.append(text(350, 74, "Вузол B", size=12, bold=True))

    # Node 3
    p.append(rect(460, 48, 100, 46, fill=FILL, stroke=LINE, sw=1.4, rx=4))
    p.append(text(510, 74, "Вузол C", size=12, bold=True))
    p.append(text(538, 88, "NULL", size=9, color=POS))

    # Tail ptr
    p.append(rect(620, 55, 60, 32, fill="#f0f0f0", stroke=LINE, sw=1.2, rx=4))
    p.append(text(650, 75, "tail", size=11, bold=True))
    p.append(arrow(620, 71, 565, 71, color=LINE, sw=1.5))

    # Стрілки між вузлами
    p.append(arrow(240, 60, 300, 60, color=NEG, sw=1.4))
    p.append(arrow(300, 80, 240, 80, color=NEG, sw=1.4))
    p.append(arrow(400, 60, 460, 60, color=NEG, sw=1.4))
    p.append(arrow(460, 80, 400, 80, color=NEG, sw=1.4))

    p.append(text(W / 2, 120, "Крайові умови: вставка/видалення першого або останнього вузла вимагає окремих 'if (head == NULL)'",
                  size=11, color=POS, italic=True))

    # НИЗ: Круговий список з Dummy Sentinel Node
    p.append(text(40, 195, "Б. Круговий список із фіктивним вартовим вузлом (Sentinel):", size=13, bold=True, anchor="start", color=FIELD))

    # Sentinel Node
    p.append(rect(60, 225, 120, 54, fill="#fdf0ed", stroke=POS, sw=2, rx=6))
    p.append(text(120, 248, "SENTINEL", size=12, bold=True, color=POS))
    p.append(text(120, 266, "(dummy head)", size=10, color=POS))

    # Data Nodes
    p.append(rect(240, 225, 100, 54, fill=FILL, stroke=LINE, sw=1.4, rx=4))
    p.append(text(290, 255, "Вузол A", size=12, bold=True))

    p.append(rect(400, 225, 100, 54, fill=FILL, stroke=LINE, sw=1.4, rx=4))
    p.append(text(450, 255, "Вузол B", size=12, bold=True))

    p.append(rect(560, 225, 100, 54, fill=FILL, stroke=LINE, sw=1.4, rx=4))
    p.append(text(610, 255, "Вузол C", size=12, bold=True))

    # Внутрішні стрілки
    p.append(arrow(180, 240, 240, 240, color=FIELD, sw=1.5))
    p.append(arrow(240, 260, 180, 260, color=FIELD, sw=1.5))
    p.append(arrow(340, 240, 400, 240, color=FIELD, sw=1.5))
    p.append(arrow(400, 260, 340, 260, color=FIELD, sw=1.5))
    p.append(arrow(500, 240, 560, 240, color=FIELD, sw=1.5))
    p.append(arrow(560, 260, 500, 260, color=FIELD, sw=1.5))

    # Замикаючі кругові стрілки
    p.append(line(660, 240, 710, 240, color=FIELD, sw=1.5))
    p.append(line(710, 240, 710, 310, color=FIELD, sw=1.5))
    p.append(line(710, 310, 120, 310, color=FIELD, sw=1.5))
    p.append(arrow(120, 310, 120, 280, color=FIELD, sw=1.5))

    p.append(text(W / 2, 342, "Єдине універсальне правило: 0 перевірок на NULL, список ніколи не буває порожнім на рівні покажчиків!",
                  size=11, color=FIELD, bold=True, italic=True))

    render(os.path.join(OUT, "sentinel-linked-list.svg"), W, H, *p,
           title="Усунення крайових випадків у списку за допомогою вартового вузла")


# ── 4. niche-filling-layout: оптимізація порожнеч (Niche Filling) ─────────────
def fig_niche_filling_layout():
    W, H = 760, 340
    p = []
    midx = W / 2

    p.append(line(midx, 40, midx, H - 30, color=MUTED, sw=1.2, dash="5 5"))

    # ЛІВО: Звичайний Option<u32> (без ніші)
    lx = midx / 2
    p.append(text(lx, 42, "Option<u32> (без оптимізації)", size=14, bold=True, color=POS))
    p.append(text(lx, 62, "Розмір: 8 байтів (через вирівнювання)", size=12, color=MUTED))

    # Пам'ять: 1 байт тег, 3 байти паддінг, 4 байти число
    bx = lx - 140
    y0 = 85
    p.append(rect(bx, y0, 60, 50, fill="#ebfbee", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(bx + 30, y0 + 24, "Тег", size=11, bold=True, color=FIELD))
    p.append(text(bx + 30, y0 + 40, "1 байт", size=9, color=MUTED))

    p.append(rect(bx + 60, y0, 80, 50, fill="#fdf0ed", stroke=POS, sw=1.5, rx=4))
    p.append(text(bx + 100, y0 + 24, "Паддінг", size=11, bold=True, color=POS))
    p.append(text(bx + 100, y0 + 40, "3 байти (дарма)", size=9, color=POS))

    p.append(rect(bx + 140, y0, 140, 50, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    p.append(text(bx + 210, y0 + 24, "Значення u32", size=11, bold=True, color=NEG))
    p.append(text(bx + 210, y0 + 40, "4 байти (0..4 294 967 295)", size=9, color=MUTED))

    p.append(fitbox(bx, 160, 280, 130,
                    "Чому розмір 8 байтів:\n"
                    "Тип u32 вимагає вирівнювання за 4 байти.\n"
                    "Тег займає 1 байт, тому компілятор\n"
                    "додає 3 байти порожнечі.\n"
                    "Оверхед пам'яті = 100%!",
                    size=12, pad=10, fill="#fffaf9", stroke=POS, sw=1.4))

    # ПРАВО: Option<NonZeroU32> або Option<&T> (Niche Filling)
    rx = midx + midx / 2
    p.append(text(rx, 42, "Option<NonZeroU32> / Option<&T>", size=14, bold=True, color=FIELD))
    p.append(text(rx, 62, "Розмір: 4 байти (Niche filling, 0 байтів оверхеду)", size=12, color=FIELD, bold=True))

    # Пам'ять: рівно 4 байти
    rbx = rx - 140
    p.append(rect(rbx, y0, 280, 50, fill="#eaf0fd", stroke=FIELD, sw=2, rx=4))
    p.append(text(rbx + 140, y0 + 24, "Рівно 4 байти (NonZeroU32)", size=12, bold=True, color=INK))
    p.append(text(rbx + 140, y0 + 40, "Значення 1..4 294 967 295 = Some(x)  |  0x00000000 = None", size=10, color=FIELD, bold=True))

    p.append(fitbox(rbx, 160, 280, 130,
                    "Як працює оптимізація ніші:\n"
                    "Тип NonZeroU32 гарантує, що 0 заборонено.\n"
                    "Компілятор використовує бітовий патерн 0\n"
                    "як вартове значення для стану None.\n"
                    "Типова безпека + нульовий оверхед!",
                    size=12, pad=10, fill="#f6fcf8", stroke=FIELD, sw=1.4))

    p.append(text(W / 2, 315, "Non-Zero Optimization поєднує строгість типів Option із нульовими витратами пам'яті вартових значень!",
                  size=11, color=FIELD, bold=True, italic=True))

    render(os.path.join(OUT, "niche-filling-layout.svg"), W, H, *p,
           title="Non-Zero Optimization: заповнення невикористаної бітової ніші")


if __name__ == "__main__":
    fig_in_band_vs_out_of_band()
    fig_getchar_eof_widening()
    fig_sentinel_linked_list()
    fig_niche_filling_layout()
    print("All figures generated successfully.")
