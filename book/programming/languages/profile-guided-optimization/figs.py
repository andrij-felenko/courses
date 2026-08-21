# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE_BG = "#0f1b14"
CODE_FG = "#eaf6ee"
IR_BG   = "#151d2b"
IR_FG   = "#bcd0ff"


# ── 1. overview-pipeline: Трифазний конвеєр PGO ─────────────────────────────
def fig_overview_pipeline():
    W, H = 860, 390
    p = []

    # Три фази у вигляді вертикальних колонок
    col_w = 240
    xs = [150, 430, 710]

    # Фоноcontainers для трьох фаз
    p.append(rect(30, 50, col_w, 310, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(rect(310, 50, col_w, 310, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(rect(590, 50, col_w, 310, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))

    # Заголовки фаз
    p.append(text(150, 75, "1. Інструментація", size=13, color=INK, bold=True))
    p.append(text(430, 75, "2. Прогін і профілювання", size=13, color=INK, bold=True))
    p.append(text(710, 75, "3. Оптимізована збірка", size=13, color=INK, bold=True))

    # Фаза 1: Блоки
    b1, _, _ = textbox(150, 120, "Вихідний код\n(.c / .cpp / .rs)", size=10.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.4, min_w=160)
    p.append(b1)
    p.append(arrow(150, 145, 150, 175, color=INK, sw=1.5))
    p.append(text(150, 162, "-fprofile-generate", size=9.5, color=MUTED, italic=True))

    b2, _, _ = textbox(150, 205, "Компілятор\n(вставка лічильників CFG)", size=10, bold=True, fill="#eef4ff", stroke=NEG, sw=1.4, min_w=170)
    p.append(b2)
    p.append(arrow(150, 235, 150, 265, color=INK, sw=1.5))

    b3, _, _ = textbox(150, 300, "Інструментований\nбінарник + runtime", size=10, bold=True, fill="#fdecea", stroke=POS, sw=1.5, min_w=170)
    p.append(b3)

    # Стрілка переходу від фази 1 до фази 2
    p.append(arrow(240, 300, 320, 120, color=POS, sw=1.8))
    p.append(text(285, 200, "запуск", size=9.5, color=POS, bold=True))

    # Фаза 2: Блоки
    b4, _, _ = textbox(430, 120, "Типове навантаження\n(репрезентативні дані)", size=10, bold=True, fill="#ffffff", stroke=LINE, sw=1.4, min_w=170)
    p.append(b4)
    p.append(arrow(430, 145, 430, 175, color=INK, sw=1.5))
    p.append(text(430, 162, "виконання", size=9.5, color=MUTED, italic=True))

    b5, _, _ = textbox(430, 205, "Сирий профіль\n(.profraw / .gcda)", size=10, bold=True, fill="#fff9db", stroke="#f59f00", sw=1.4, min_w=160)
    p.append(b5)
    p.append(arrow(430, 235, 430, 265, color=INK, sw=1.5))
    p.append(text(430, 252, "llvm-profdata merge", size=9.5, color=MUTED, italic=True))

    b6, _, _ = textbox(430, 300, "Індексований профіль\n(code.profdata)", size=10, bold=True, fill="#e6fcf5", stroke=FIELD, sw=1.5, min_w=170)
    p.append(b6)

    # Стрілка переходу від фази 2 до фази 3
    p.append(arrow(520, 300, 600, 120, color=FIELD, sw=1.8))
    p.append(text(565, 200, "профіль", size=9.5, color=FIELD, bold=True))

    # Фаза 3: Блоки
    b7, _, _ = textbox(710, 120, "Вихідний код +\nдані профілю", size=10.5, bold=True, fill="#ffffff", stroke=LINE, sw=1.4, min_w=160)
    p.append(b7)
    p.append(arrow(710, 145, 710, 175, color=INK, sw=1.5))
    p.append(text(710, 162, "-fprofile-use", size=9.5, color=MUTED, italic=True))

    b8, _, _ = textbox(710, 205, "PGO-оптимізатор\n(layout, inlining, ICP)", size=10, bold=True, fill="#eef4ff", stroke=NEG, sw=1.4, min_w=170)
    p.append(b8)
    p.append(arrow(710, 235, 710, 265, color=INK, sw=1.5))

    b9, _, _ = textbox(710, 300, "Оптимізований\nвиконуваний файл", size=10, bold=True, fill="#ebfbee", stroke=FIELD, sw=1.8, min_w=170)
    p.append(b9)

    render(os.path.join(OUT, "overview-pipeline.svg"), W, H, *p, title="Трифазний конвеєр Profile-Guided Optimization (PGO)")


# ── 2. basic-block-layout: Розміщення базових блоків ────────────────────────
def fig_basic_block_layout():
    W, H = 860, 420
    p = []

    p.append(line(W / 2, 45, W / 2, 395, color=MUTED, sw=1.2, dash="4 4"))

    # Ліва частина: Без PGO
    p.append(text(215, 35, "Без PGO (статичне розміщення)", size=12.5, color=POS, bold=True))

    b_a1, _, _ = textbox(215, 80, "Блок A: перевірка if (cond)", size=10, bold=True, fill="#ffffff", stroke=LINE, sw=1.4, min_w=190)
    p.append(b_a1)

    # Дві гілки
    p.append(arrow(160, 102, 120, 150, color=POS, sw=1.6))
    p.append(text(105, 125, "99% (гаряча)", size=9.5, color=POS, bold=True))

    p.append(arrow(270, 102, 310, 150, color=MUTED, sw=1.4))
    p.append(text(325, 125, "1% (холодна)", size=9.5, color=MUTED))

    b_c1, _, _ = textbox(120, 175, "Блок C (гарячий)\nосновна обробка", size=10, bold=True, fill="#fdecea", stroke=POS, sw=1.5, min_w=130)
    b_b1, _, _ = textbox(310, 175, "Блок B (холодний)\nобробка помилки", size=10, bold=True, fill="#f4f6f8", stroke=LINE, sw=1.3, min_w=130)
    p.extend([b_c1, b_b1])

    # Пам'ять без PGO
    p.append(text(215, 235, "Послідовність у пам'яті (L1i cache):", size=10, color=INK, bold=True))
    p.append(rect(40, 255, 350, 42, fill="#ffffff", stroke=LINE, sw=1.4, rx=4))
    p.append(rect(40, 255, 110, 42, fill="#f1f3f5", stroke=LINE, sw=1.2, rx=0))
    p.append(rect(150, 255, 120, 42, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=0))
    p.append(rect(270, 255, 120, 42, fill="#fdecea", stroke=POS, sw=1.5, rx=0))

    p.append(text(95, 280, "Блок A", size=10, bold=True))
    p.append(text(210, 280, "Блок B (холодний)", size=9.5, color=MUTED))
    p.append(text(330, 280, "Блок C (гарячий)", size=9.5, color=POS, bold=True))

    # Стрибок у пам'яті
    p.append(arrow(95, 305, 330, 305, color=POS, sw=1.6))
    p.append(text(215, 325, "стрибок (branch taken) + промах L1i", size=9.5, color=POS, italic=True))

    b_res1, _, _ = textbox(215, 365, "Постійний стрибок через холодний код:\nкеш-лінія L1i засмічується блоком B", size=9.5, fill="#fff5f5", stroke=POS, sw=1.2, min_w=340)
    p.append(b_res1)

    # Права частина: З PGO (Pettis-Hansen layout)
    p.append(text(645, 35, "З PGO (алгоритм Pettis-Hansen)", size=12.5, color=FIELD, bold=True))

    b_a2, _, _ = textbox(645, 80, "Блок A: перевірка if (cond)", size=10, bold=True, fill="#ffffff", stroke=LINE, sw=1.4, min_w=190)
    p.append(b_a2)

    # Прямий потік
    p.append(arrow(645, 102, 645, 150, color=FIELD, sw=2.0))
    p.append(text(695, 125, "99% fall-through", size=9.5, color=FIELD, bold=True))

    p.append(arrow(725, 95, 780, 150, color=MUTED, sw=1.2))
    p.append(text(800, 125, "1% jump", size=9.5, color=MUTED))

    b_c2, _, _ = textbox(645, 175, "Блок C (гарячий)\nосновна обробка", size=10, bold=True, fill="#ebfbee", stroke=FIELD, sw=1.8, min_w=140)
    b_b2, _, _ = textbox(790, 175, "Блок B\n(холодний)", size=9.5, bold=False, fill="#f4f6f8", stroke=LINE, sw=1.1, min_w=85)
    p.extend([b_c2, b_b2])

    # Пам'ять з PGO
    p.append(text(645, 235, "Послідовність у пам'яті (L1i cache):", size=10, color=INK, bold=True))
    p.append(rect(470, 255, 350, 42, fill="#ffffff", stroke=LINE, sw=1.4, rx=4))
    p.append(rect(470, 255, 130, 42, fill="#f1f3f5", stroke=LINE, sw=1.2, rx=0))
    p.append(rect(600, 255, 130, 42, fill="#ebfbee", stroke=FIELD, sw=1.8, rx=0))
    p.append(rect(730, 255, 90, 42, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=0))

    p.append(text(535, 280, "Блок A", size=10, bold=True))
    p.append(text(665, 280, "Блок C (гарячий)", size=9.5, color=FIELD, bold=True))
    p.append(text(775, 280, "Блок B", size=9.5, color=MUTED))

    # Прямий потік у пам'яті
    p.append(arrow(535, 305, 665, 305, color=FIELD, sw=1.8))
    p.append(text(600, 325, "послідовне виконання (fall-through)", size=9.5, color=FIELD, italic=True))

    b_res2, _, _ = textbox(645, 365, "Ідеальна щільність кешу інструкцій L1i:\nнемає зайвих стрибків, нуль хибних передбачень", size=9.5, fill="#f4fbf6", stroke=FIELD, sw=1.2, min_w=340)
    p.append(b_res2)

    render(os.path.join(OUT, "basic-block-layout.svg"), W, H, *p, title="Оптимізація розміщення базових блоків (Basic Block Layout)")


# ── 3. hot-cold-splitting: Розділення функцій на гарячі та холодні частини ──
def fig_hot_cold_splitting():
    W, H = 860, 400
    p = []

    # До розділення
    p.append(text(210, 40, "До розділення: монолітна функція", size=12.5, color=POS, bold=True))

    p.append(rect(60, 70, 300, 230, fill="#ffffff", stroke=LINE, sw=1.5, rx=6))
    p.append(text(210, 95, "Функція process_request()", size=11, bold=True))

    p.append(rect(80, 115, 260, 50, fill="#ebfbee", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(210, 142, "Гаряче ядро (парсинг + розрахунок, 99%)", size=9.5, color=FIELD, bold=True))

    p.append(rect(80, 175, 260, 110, fill="#f4f6f8", stroke=MUTED, sw=1.3, rx=4))
    p.append(text(210, 200, "Холодний код (1% викликів):", size=9.5, color=MUTED, bold=True))
    p.append(text(210, 222, "• Детальне логування та трасування помилок", size=9.5, color=MUTED))
    p.append(text(210, 242, "• Форматування стектрейсу і дамп пам'яті", size=9.5, color=MUTED))
    p.append(text(210, 262, "• Складне відновлення після збоїв мережі", size=9.5, color=MUTED))

    b_warn, _, _ = textbox(210, 345, "Проблема: 70% обсягу функції — холодний код.\nВін витісняє корисні інструкції з L1i та iTLB.", size=9.5, fill="#fff5f5", stroke=POS, sw=1.3, min_w=320)
    p.append(b_warn)

    # Стрілка трансформації
    p.append(arrow(380, 185, 450, 185, color=INK, sw=2.0))
    p.append(text(415, 170, "PGO Splitting", size=9.5, color=INK, bold=True))

    # Після розділення
    p.append(text(650, 40, "Після Hot/Cold Splitting (секції ELF)", size=12.5, color=FIELD, bold=True))

    # Секція .text.hot
    p.append(rect(480, 70, 340, 130, fill="#f4fbf6", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(650, 92, "Секція .text.hot (компактний робочий набір)", size=10.5, color=FIELD, bold=True))

    p.append(rect(500, 110, 300, 70, fill="#ebfbee", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(650, 132, "process_request.hot:", size=10, bold=True))
    p.append(text(650, 150, "Парсинг та швидкий шлях (fast-path)", size=9.5, color=FIELD))
    p.append(text(650, 168, "jnz process_request.cold  ; рідкісний стрибок", size=9.5, color=POS, italic=True))

    # Секція .text.cold
    p.append(rect(480, 220, 340, 95, fill="#f8f9fa", stroke=MUTED, sw=1.3, rx=6))
    p.append(text(650, 240, "Секція .text.cold (винесено на край пам'яті)", size=10.5, color=MUTED, bold=True))

    p.append(rect(500, 255, 300, 48, fill="#ffffff", stroke=MUTED, sw=1.1, rx=4))
    p.append(text(650, 272, "process_request.cold:", size=9.5, color=MUTED, bold=True))
    p.append(text(650, 290, "Логування, дамп, відновлення", size=9.5, color=MUTED))

    # Стрілка між секціями
    p.append(arrow(750, 185, 750, 220, color=POS, sw=1.3))

    b_good, _, _ = textbox(650, 355, "Результат: гарячий код спаковано в мінімум кеш-ліній.\nХолодний код завантажується лише при реальних збоях.", size=9.5, fill="#f4fbf6", stroke=FIELD, sw=1.3, min_w=340)
    p.append(b_good)

    render(os.path.join(OUT, "hot-cold-splitting.svg"), W, H, *p, title="Розділення функцій на гарячі та холодні частини (Hot/Cold Function Splitting)")


# ── 4. indirect-call-promotion: Спекулятивна девіртуалізація ────────────────
def fig_indirect_call_promotion():
    W, H = 860, 410
    p = []

    p.append(line(W / 2, 45, W / 2, 385, color=MUTED, sw=1.2, dash="4 4"))

    # Ліва частина: Непрямий виклик
    p.append(text(215, 35, "Звичайний поліморфний виклик", size=12.5, color=POS, bold=True))

    b_call1, _, _ = textbox(215, 80, "obj->process(data)\n(виклик через vtable або покажчик)", size=10, bold=True, fill="#ffffff", stroke=LINE, sw=1.4, min_w=240)
    p.append(b_call1)

    p.append(arrow(215, 110, 215, 145, color=INK, sw=1.5))

    b_vt, _, _ = textbox(215, 175, "1. Завантаження vptr з об'єкта\n2. Читання адреси методу з vtable\n3. Непрямий перехід: call *%rax", size=9.5, fill="#f4f6f8", stroke=LINE, sw=1.3, min_w=240)
    p.append(b_vt)

    p.append(arrow(215, 215, 215, 250, color=POS, sw=1.5))

    b_tgt, _, _ = textbox(215, 280, "Цільова функція\n(компілятор не знає яка)", size=10, bold=True, fill="#fdecea", stroke=POS, sw=1.4, min_w=200)
    p.append(b_tgt)

    b_lim, _, _ = textbox(215, 345, "Обмеження:\n• Неможливо заінлайнити\n• Помилки апаратного передбачення переходів (BTB)\n• Блокування конвеєра", size=9.5, fill="#fff5f5", stroke=POS, sw=1.2, min_w=330)
    p.append(b_lim)

    # Права частина: Indirect Call Promotion
    p.append(text(645, 35, "З PGO: Indirect Call Promotion (ICP)", size=12.5, color=FIELD, bold=True))

    b_prof, _, _ = textbox(645, 75, "Профіль значень (Value Profile):\nobj->process вказує на FastHandler у 99.4% випадків", size=9.5, bold=True, fill="#fff9db", stroke="#f59f00", sw=1.4, min_w=310)
    p.append(b_prof)

    p.append(arrow(645, 105, 645, 135, color=FIELD, sw=1.6))

    b_guard, _, _ = textbox(645, 170, "Спекулятивна перевірка типу:\nif (obj->vptr == FastHandler::vtable)", size=10, bold=True, fill="#ffffff", stroke=LINE, sw=1.4, min_w=280)
    p.append(b_guard)

    # Дві гілки
    p.append(arrow(580, 198, 540, 240, color=FIELD, sw=1.8))
    p.append(text(525, 218, "99.4%", size=9.5, color=FIELD, bold=True))

    p.append(arrow(710, 198, 750, 240, color=MUTED, sw=1.2))
    p.append(text(765, 218, "0.6%", size=9.5, color=MUTED))

    b_inl, _, _ = textbox(530, 275, "Прямий виклик +\nАГРЕСИВНИЙ ІНЛАЙНІНГ\n(FastHandler::process)", size=9.5, bold=True, fill="#ebfbee", stroke=FIELD, sw=1.8, min_w=170)
    b_slw, _, _ = textbox(760, 275, "call *%rax\n(резервний непрямий)", size=9.5, bold=False, fill="#f4f6f8", stroke=LINE, sw=1.1, min_w=140)
    p.extend([b_inl, b_slw])

    b_adv, _, _ = textbox(645, 345, "Переваги:\n• Інлайнінг розкриває автовекторизацію (SIMD)\n• Згортання констант та усунення підвиразів\n• Прямий перехід без промахів BTB", size=9.5, fill="#f4fbf6", stroke=FIELD, sw=1.2, min_w=340)
    p.append(b_adv)

    render(os.path.join(OUT, "indirect-call-promotion.svg"), W, H, *p, title="Спекулятивна девіртуалізація та Indirect Call Promotion")


# ── 5. autofdo-bolt-stack: Сучасний виробничий стек ─────────────────────────
def fig_autofdo_bolt_stack():
    W, H = 860, 420
    p = []

    # Чотири рівні стеку
    levels = [
        ("1. Базова компіляція + ThinLTO", "Міжмодульний аналіз графу викликів, глобальне поширення констант та імпорт функцій між файлами", "#f8fafc", LINE),
        ("2. Profile-Guided Optimization (PGO / AutoFDO)", "Точні ваги переходів, Pettis-Hansen block layout, hot/cold splitting та спекулятивна девіртуалізація", "#eef4ff", NEG),
        ("3. Профілювання у продакшені (Linux perf / LBR)", "Апаратні лічильники PMU зчитують Last Branch Record без сповільнення реального трафіку (<1-2% накладних витрат)", "#fff9db", "#f59f00"),
        ("4. Пост-лінкерна оптимізація бінарника (BOLT)", "Перевпорядкування машинних інструкцій на межах кеш-ліній (64B), розгортання переходів, усунення i-cache misses", "#ebfbee", FIELD),
    ]

    y_start = 75
    h_box = 62
    gap = 22

    for i, (title_text, desc_text, fill_c, strk_c) in enumerate(levels):
        cy = y_start + i * (h_box + gap)
        p.append(rect(100, cy, 660, h_box, fill=fill_c, stroke=strk_c, sw=1.6, rx=6))
        p.append(text(430, cy + 22, title_text, size=11, color=INK, bold=True))
        p.append(text(430, cy + 44, desc_text, size=9.5, color=MUTED))

        if i < 3:
            p.append(arrow(430, cy + h_box, 430, cy + h_box + gap, color=INK, sw=1.5))

    # Бокова шкала накопичення виграшу
    p.append(rect(780, 75, 55, 314, fill="#f1f3f5", stroke=LINE, sw=1.2, rx=4))
    p.append(text(807, 105, "+5-10%", size=9.5, color=INK, bold=True))
    p.append(text(807, 189, "+10-15%", size=9.5, color=NEG, bold=True))
    p.append(text(807, 273, "Sample", size=9.5, color=MUTED, bold=True))
    p.append(text(807, 357, "+7-15%", size=9.5, color=FIELD, bold=True))
    p.append(text(807, 372, "BOLT", size=9.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "autofdo-bolt-stack.svg"), W, H, *p, title="Сучасний виробничий стек оптимізації: ThinLTO + AutoFDO + BOLT")


if __name__ == "__main__":
    fig_overview_pipeline()
    fig_basic_block_layout()
    fig_hot_cold_splitting()
    fig_indirect_call_promotion()
    fig_autofdo_bolt_stack()
    print("All figures generated successfully.")
