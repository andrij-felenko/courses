# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

# ── Кольори для функціональних блоків та слотів ──────────────────────────────
SLOT_M = "#eaf0fd"   # Memory (синій)
SLOT_I = "#fdecea"   # Integer (червоний)
SLOT_F = "#e8f8f0"   # Floating-point (зелений)
SLOT_B = "#fef5e7"   # Branch (помаранчевий)
SLOT_TMP = "#f0f2f5" # Template (сірий)

BORDER_M = "#2457d6"
BORDER_I = "#c0392b"
BORDER_F = "#27ae60"
BORDER_B = "#d35400"
BORDER_TMP = "#6b7280"

# ── Фігура 1: Формат кортежу (Bundle) IA-64 EPIC та біти зупинки ─────────────
def fig_bundle_layout():
    w, h = 820, 480
    frags = []

    # Заголовок
    frags.append(text(w / 2, 35, "128-бітний кортеж команд IA-64 (Instruction Bundle)", size=16, bold=True))
    frags.append(text(w / 2, 55, "Три 41-бітні інструкції та 5-бітний шаблон розкладання й залежностей", size=12, color=MUTED))

    # Головна лінійка 128 біт
    y_bar = 90
    x_start = 50
    total_w = 720

    # Шаблон (5 біт)
    w_tmp = 85
    w_slot = (total_w - w_tmp) / 3 # ~211 px

    # Рендеримо 4 поля кортежу
    # 1. Template (біти 0..4)
    frags.append(rect(x_start, y_bar, w_tmp, 60, fill=SLOT_TMP, stroke=BORDER_TMP, sw=1.8, rx=6))
    frags.append(text(x_start + w_tmp / 2, y_bar + 26, "Шаблон", size=13, bold=True))
    frags.append(text(x_start + w_tmp / 2, y_bar + 46, "5 бітів", size=11, color=MUTED))
    frags.append(text(x_start + w_tmp / 2, y_bar - 8, "[4:0]", size=11, color=INK))

    # 2. Slot 0 (біти 5..45)
    x_s0 = x_start + w_tmp
    frags.append(rect(x_s0, y_bar, w_slot, 60, fill=SLOT_M, stroke=BORDER_M, sw=1.8, rx=6))
    frags.append(text(x_s0 + w_slot / 2, y_bar + 26, "Слот 0 (Slot 0)", size=13, bold=True))
    frags.append(text(x_s0 + w_slot / 2, y_bar + 46, "41 біт (Слот пам'яті M)", size=11, color=MUTED))
    frags.append(text(x_s0 + w_slot / 2, y_bar - 8, "[45:5]", size=11, color=INK))

    # 3. Slot 1 (біти 46..86)
    x_s1 = x_s0 + w_slot
    frags.append(rect(x_s1, y_bar, w_slot, 60, fill=SLOT_I, stroke=BORDER_I, sw=1.8, rx=6))
    frags.append(text(x_s1 + w_slot / 2, y_bar + 26, "Слот 1 (Slot 1)", size=13, bold=True))
    frags.append(text(x_s1 + w_slot / 2, y_bar + 46, "41 біт (Цілочисловий I)", size=11, color=MUTED))
    frags.append(text(x_s1 + w_slot / 2, y_bar - 8, "[86:46]", size=11, color=INK))

    # 4. Slot 2 (біти 87..127)
    x_s2 = x_s1 + w_slot
    frags.append(rect(x_s2, y_bar, w_slot, 60, fill=SLOT_I, stroke=BORDER_I, sw=1.8, rx=6))
    frags.append(text(x_s2 + w_slot / 2, y_bar + 26, "Слот 2 (Slot 2)", size=13, bold=True))
    frags.append(text(x_s2 + w_slot / 2, y_bar + 46, "41 біт (Цілочисловий I)", size=11, color=MUTED))
    frags.append(text(x_s2 + w_slot / 2, y_bar - 8, "[127:87]", size=11, color=INK))

    # Анатомія 41-бітної інструкції
    y_inst = 200
    frags.append(text(w / 2, y_inst - 10, "Будова кожної 41-бітної інструкції всередині слота:", size=13, bold=True))

    w_qp = 100
    w_op = 140
    w_ops = 480
    x_inst_start = 50

    frags.append(rect(x_inst_start, y_inst, w_qp, 44, fill="#fef9e7", stroke=BORDER_B, sw=1.5, rx=4))
    frags.append(text(x_inst_start + w_qp / 2, y_inst + 20, "qp [5:0]", size=12, bold=True))
    frags.append(text(x_inst_start + w_qp / 2, y_inst + 36, "предикат p0..p63", size=10, color=MUTED))

    frags.append(rect(x_inst_start + w_qp, y_inst, w_op, 44, fill=FILL, stroke=LINE, sw=1.5, rx=4))
    frags.append(text(x_inst_start + w_qp + w_op / 2, y_inst + 20, "Opcode [40:37, ...]", size=12, bold=True))
    frags.append(text(x_inst_start + w_qp + w_op / 2, y_inst + 36, "код операції", size=10, color=MUTED))

    frags.append(rect(x_inst_start + w_qp + w_op, y_inst, w_ops, 44, fill=FILL, stroke=LINE, sw=1.5, rx=4))
    frags.append(text(x_inst_start + w_qp + w_op + w_ops / 2, y_inst + 20, "Операнди (r_dest, r_src1, r_src2 / константи)", size=12, bold=True))
    frags.append(text(x_inst_start + w_qp + w_op + w_ops / 2, y_inst + 36, "по 7 бітів на архітектурний регістр r0..r127", size=10, color=MUTED))

    # Нижній блок: Шаблони, типи блоків і біти зупинки
    y_grp = 280
    frags.append(rect(50, y_grp, 720, 165, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(70, y_grp + 26, "Функції 5-бітного поля шаблону (Template):", size=14, bold=True, anchor="start"))

    frags.append(circle(75, y_grp + 56, 4, fill=BORDER_TMP, stroke=BORDER_TMP))
    frags.append(text(90, y_grp + 60, "1. Призначення блоків: кодує тип виконавчого пристрою для кожного слота (M, I, F, B, L+X).", size=12, anchor="start"))
    frags.append(text(105, y_grp + 78, "Наприклад, шаблон M_MI призначає слот 0 → пам'ять, 1 → пам'ять, 2 → АЛП.", size=11, color=MUTED, anchor="start"))

    frags.append(circle(75, y_grp + 105, 4, fill=BORDER_TMP, stroke=BORDER_TMP))
    frags.append(text(90, y_grp + 109, "2. Явні біти зупинки (Stop Bits, позначка ';;'):", size=12, bold=True, anchor="start"))
    frags.append(text(105, y_grp + 127, "Визначають межі груп інструкцій (Instruction Groups). Інструкції всередині групи незалежні", size=11, anchor="start"))
    frags.append(text(105, y_grp + 145, "і виконуються паралельно. Біт ';;' вказує залізу: наступні інструкції залежать від попередніх.", size=11, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'bundle-layout.svg'), w, h, *frags)


# ── Фігура 2: Повна предикація та усунення розгалужень (Hyperblock) ──────────
def fig_predication():
    w, h = 820, 430
    frags = []

    frags.append(text(w / 2, 35, "Трансформація коду: Розгалуження проти Повної Предикації", size=16, bold=True))
    frags.append(text(w / 2, 55, "Усунення стрибків та штрафів хибного передбачення конвеєра", size=12, color=MUTED))

    # Ліва колонка: Традиційне розгалуження (Control Flow Graph)
    x_left = 220
    frags.append(text(x_left, 90, "Традиційний конвеєр (Розгалуження)", size=14, bold=True, color=POS))
    
    # Блок порівняння
    frags.append(rect(x_left - 130, 110, 260, 42, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(x_left, 136, "CMP r1, r2  (r1 == r2 ?)", size=12, bold=True))

    # Стрілки розгалуження
    frags.append(arrow(x_left - 60, 152, x_left - 90, 185, color=POS, sw=1.5))
    frags.append(text(x_left - 100, 170, "Так", size=11, color=POS, bold=True, anchor="end"))

    frags.append(arrow(x_left + 60, 152, x_left + 90, 185, color=NEG, sw=1.5))
    frags.append(text(x_left + 100, 170, "Ні", size=11, color=NEG, bold=True, anchor="start"))

    # Гілка Then
    frags.append(rect(x_left - 170, 190, 150, 42, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    frags.append(text(x_left - 95, 216, "ADD r3 = r4, r5", size=11, bold=True))

    # Гілка Else
    frags.append(rect(x_left + 20, 190, 150, 42, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(x_left + 95, 216, "SUB r3 = r6, r7", size=11, bold=True))

    # Злиття
    frags.append(arrow(x_left - 95, 232, x_left - 30, 265, color=LINE, sw=1.5))
    frags.append(arrow(x_left + 95, 232, x_left + 30, 265, color=LINE, sw=1.5))

    frags.append(rect(x_left - 130, 270, 260, 38, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(x_left, 294, "Продовження виконання...", size=11, color=MUTED))

    frags.append(rect(x_left - 160, 330, 320, 70, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    frags.append(text(x_left, 352, "Ризик: Хибне передбачення переходу", size=11, bold=True, color=POS))
    frags.append(text(x_left, 372, "Скидання конвеєра: втрата 15–30 тактів.", size=10, color=INK))
    frags.append(text(x_left, 388, "Апаратний предикатор витрачає енергію й площу.", size=10, color=MUTED))

    # Розділювач
    frags.append(line(410, 85, 410, 410, color="#d1d5db", sw=1.5, dash="4,4"))

    # Права колонка: EPIC Повна предикація (Hyperblock)
    x_right = 610
    frags.append(text(x_right, 90, "EPIC Предикація (Лінійний гіперблок)", size=14, bold=True, color=FIELD))

    # Предикатне порівняння
    frags.append(rect(x_right - 160, 110, 320, 50, fill="#e8f8f0", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(x_right, 132, "cmp.eq p1, p2 = r1, r2 ;;", size=12, bold=True))
    frags.append(text(x_right, 149, "Встановлює: p1 = (r1==r2), p2 = (r1!=r2)", size=10, color=MUTED))

    frags.append(arrow(x_right, 160, x_right, 185, color=FIELD, sw=1.8))

    # Паралельне виконання під предикатами
    frags.append(rect(x_right - 160, 190, 320, 95, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(x_right, 212, "Паралельна пачка команд (один такт):", size=11, bold=True))
    
    # Інструкція 1
    frags.append(rect(x_right - 145, 224, 290, 26, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    frags.append(text(x_right, 241, "(p1)  add r3 = r4, r5  [діє якщо p1==1]", size=11))

    # Інструкція 2
    frags.append(rect(x_right - 145, 253, 290, 26, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4))
    frags.append(text(x_right, 270, "(p2)  sub r3 = r6, r7  [діє якщо p2==1]", size=11))

    frags.append(arrow(x_right, 285, x_right, 310, color=FIELD, sw=1.8))

    frags.append(rect(x_right - 160, 315, 320, 85, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(x_right, 335, "Результат: Нуль переходів у коді", size=11, bold=True, color=FIELD))
    frags.append(text(x_right, 355, "Обидві команди летять у конвеєр паралельно.", size=10, color=INK))
    frags.append(text(x_right, 371, "Команда з хибним предикатом перетворюється на NOP.", size=10, color=INK))
    frags.append(text(x_right, 387, "Ніколи не скидає конвеєр, передбачення не потрібне.", size=10, color=MUTED))

    render(os.path.join(IMG, 'predication-hyperblock.svg'), w, h, *frags)


# ── Фігура 3: Спекуляція даних і таблиця ALAT ────────────────────────────────
def fig_speculation_alat():
    w, h = 820, 460
    frags = []

    frags.append(text(w / 2, 30, "Механізми спекуляції EPIC: Керування (NaT) та Дані (ALAT)", size=16, bold=True))
    frags.append(text(w / 2, 50, "Раннє підтягування пам'яті вище небезпечних розгалужень та записів", size=12, color=MUTED))

    # Ліва половина: Спекуляція керування (Control Speculation & NaT)
    x_c = 215
    frags.append(rect(30, 75, 370, 360, fill="#fdfdfd", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x_c, 100, "Спекуляція керування (Control Speculation)", size=13, bold=True, color=BORDER_I))

    frags.append(rect(45, 120, 340, 48, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    frags.append(text(x_c, 140, "ld.s r1 = [r_ptr]  ;;", size=12, bold=True))
    frags.append(text(x_c, 157, "Спекулятивне читання до перевірки покажчика", size=10, color=MUTED))

    frags.append(arrow(x_c, 168, x_c, 190, color=LINE, sw=1.5))

    # Стан регістра з бітом NaT
    frags.append(rect(45, 190, 340, 60, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    frags.append(text(x_c, 210, "Регістр r1: [ 64-бітні дані ] + [ NaT біт ]", size=11, bold=True))
    frags.append(text(x_c, 228, "Якщо помилка пам'яті (Page Fault) → NaT = 1", size=10, color=POS))
    frags.append(text(x_c, 242, "Виняток не викликається, аварії ОС немає", size=10, color=MUTED))

    frags.append(arrow(x_c, 250, x_c, 275, color=LINE, sw=1.5))

    frags.append(rect(45, 275, 340, 42, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    frags.append(text(x_c, 294, "chk.s r1, recovery_code", size=12, bold=True))
    frags.append(text(x_c, 308, "Перевірка в точці, де дані дійсно потрібні", size=10, color=MUTED))

    frags.append(arrow(x_c, 317, x_c, 340, color=POS, sw=1.5))

    frags.append(rect(45, 340, 340, 75, fill="#fff5f5", stroke=POS, sw=1.2, rx=6))
    frags.append(text(x_c, 360, "Відновлення (якщо NaT == 1):", size=11, bold=True, color=POS))
    frags.append(text(x_c, 378, "Перехід у recovery_code: повторний ld r1 = [r_ptr]", size=10, color=INK))
    frags.append(text(x_c, 395, "Якщо помилка справжня — тепер процесор згенерує Trap.", size=10, color=MUTED))

    # Права половина: Спекуляція даних (Data Speculation & ALAT)
    x_d = 605
    frags.append(rect(420, 75, 370, 360, fill="#fdfdfd", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(x_d, 100, "Спекуляція даних (Data Speculation & ALAT)", size=13, bold=True, color=BORDER_M))

    frags.append(rect(435, 120, 340, 48, fill="#eaf0fd", stroke=BORDER_M, sw=1.4, rx=6))
    frags.append(text(x_d, 140, "ld.a r1 = [r_src]  ;;", size=12, bold=True))
    frags.append(text(x_d, 157, "Читання вище підозрілого запису st [r_dst]", size=10, color=MUTED))

    frags.append(arrow(x_d, 168, x_d, 190, color=LINE, sw=1.5))

    # Таблиця ALAT
    frags.append(rect(435, 190, 340, 75, fill="#f4f6f8", stroke=BORDER_M, sw=1.5, rx=6))
    frags.append(text(x_d, 210, "Апаратна таблиця ALAT (Advanced Load Table)", size=11, bold=True, color=BORDER_M))
    frags.append(text(x_d, 230, "Запис: [Регістр: r1 | Адреса: 0x1000 | Валідний: 1]", size=10, color=INK))
    frags.append(text(x_d, 248, "Будь-який st [0x1000] скидає запис у Валідний = 0", size=10, color=POS))

    frags.append(arrow(x_d, 265, x_d, 290, color=LINE, sw=1.5))

    frags.append(rect(435, 290, 340, 44, fill=FILL, stroke=LINE, sw=1.4, rx=6))
    frags.append(text(x_d, 310, "chk.a.clr r1, recovery_code", size=12, bold=True))
    frags.append(text(x_d, 325, "Перевірка валідності запису в ALAT", size=10, color=MUTED))

    frags.append(arrow(x_d, 334, x_d, 355, color=BORDER_M, sw=1.5))

    frags.append(rect(435, 355, 340, 65, fill="#f0f5ff", stroke=BORDER_M, sw=1.2, rx=6))
    frags.append(text(x_d, 375, "Результат ALAT:", size=11, bold=True, color=BORDER_M))
    frags.append(text(x_d, 393, "Якщо адреси перетнулися — повторне читання з пам'яті.", size=10, color=INK))
    frags.append(text(x_d, 408, "Якщо ні (99% випадків) — нуль затримок пам'яті!", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, 'speculation-alat.svg'), w, h, *frags)


# ── Фігура 4: Програмна конвеєризація (Software Pipelining) ─────────────────
def fig_software_pipelining():
    w, h = 820, 480
    frags = []

    frags.append(text(w / 2, 30, "Програмна конвеєризація (Software Pipelining / Modulo Scheduling)", size=16, bold=True))
    frags.append(text(w / 2, 50, "Суміщення фаз різних ітерацій у компактне стабільне ядро (Kernel)", size=12, color=MUTED))

    # Порівняння: Звичайний цикл vs Конвеєризований
    cell_w = 75
    cell_h = 28

    stages = ["Читання (L)", "Обчислення (C)", "Запис (S)"]
    st_colors = ["#eaf0fd", "#fdecea", "#e8f8f0"]
    st_strokes = [BORDER_M, BORDER_I, BORDER_F]

    # Верхня частина: Звичайне виконання (ітерація за ітерацією)
    y_seq = 85
    frags.append(text(50, y_seq + 18, "Звичайний цикл:", size=13, bold=True, anchor="start"))
    frags.append(text(50, y_seq + 36, "3 такти на ітерацію", size=11, color=MUTED, anchor="start"))

    x_seq_start = 220
    for i in range(3):
        for s in range(3):
            cx = x_seq_start + (i * 3 + s) * 55
            frags.append(rect(cx, y_seq, 50, cell_h, fill=st_colors[s], stroke=st_strokes[s], sw=1.2, rx=4))
            frags.append(text(cx + 25, y_seq + 18, "i%d:%s" % (i+1, stages[s][0]), size=10, bold=True))

    # Лінія розділу
    frags.append(line(50, 150, 770, 150, color="#e5e7eb", sw=1.5))

    # Нижня частина: Програмна конвеєризація (II = 1 такт)
    y_pip = 175
    frags.append(text(50, y_pip + 18, "Програмний конвеєр", size=13, bold=True, anchor="start"))
    frags.append(text(50, y_pip + 36, "(Інтервал ініціалізації II = 1):", size=11, color=FIELD, bold=True, anchor="start"))

    x_p_start = 220
    n_cycles = 7

    # Часова шкала тактів
    for c in range(n_cycles):
        frags.append(text(x_p_start + c * cell_w + cell_w / 2, y_pip - 5, "Такт %d" % (c + 1), size=11, color=MUTED, bold=True))

    # Сітка виконання 5 ітерацій зі зсувом в 1 такт
    for it in range(5):
        for st in range(3):
            c_idx = it + st
            if c_idx < n_cycles:
                cx = x_p_start + c_idx * cell_w
                cy = y_pip + 10 + it * (cell_h + 4)
                frags.append(rect(cx + 2, cy, cell_w - 4, cell_h, fill=st_colors[st], stroke=st_strokes[st], sw=1.2, rx=4))
                frags.append(text(cx + cell_w / 2, cy + 18, "i%d: %s" % (it + 1, stages[st][0]), size=11, bold=True))

    # Виділення трьох зон: Пролог, Ядро, Епілог
    y_zone = y_pip + 10 + 5 * (cell_h + 4) + 10

    # Пролог (Такти 1-2)
    w_pro = 2 * cell_w
    frags.append(rect(x_p_start, y_zone, w_pro, 55, fill="#fffaf0", stroke=BORDER_B, sw=1.4, rx=6))
    frags.append(text(x_p_start + w_pro / 2, y_zone + 24, "Пролог (Prologue)", size=12, bold=True, color=BORDER_B))
    frags.append(text(x_p_start + w_pro / 2, y_zone + 42, "Заповнення конвеєра", size=10, color=MUTED))

    # Стабільне ядро (Такти 3-5)
    w_ker = 3 * cell_w
    frags.append(rect(x_p_start + w_pro, y_zone, w_ker, 55, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(x_p_start + w_pro + w_ker / 2, y_zone + 24, "Стабільне ядро (Kernel) — 1 ітерація щотакту!", size=12, bold=True, color=FIELD))
    frags.append(text(x_p_start + w_pro + w_ker / 2, y_zone + 42, "Одночасно: Read(i+2) | Calc(i+1) | Write(i)", size=10, color=INK))

    # Епілог (Такти 6-7)
    w_epi = 2 * cell_w
    frags.append(rect(x_p_start + w_pro + w_ker, y_zone, w_epi, 55, fill="#fffaf0", stroke=BORDER_B, sw=1.4, rx=6))
    frags.append(text(x_p_start + w_pro + w_ker + w_epi / 2, y_zone + 24, "Епілог (Epilogue)", size=12, bold=True, color=BORDER_B))
    frags.append(text(x_p_start + w_pro + w_ker + w_epi / 2, y_zone + 42, "Завершення останніх даних", size=10, color=MUTED))

    # Пояснення про ротаційні регістри
    y_bot = y_zone + 70
    frags.append(rect(50, y_bot, 720, 48, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    frags.append(text(w / 2, y_bot + 20, "Ротаційні регістри IA-64 (r32..r127 та p16..p63):", size=12, bold=True))
    frags.append(text(w / 2, y_bot + 36, "Автоматично зсувають індекси щоітерації за інструкцією br.ctop, усуваючи дублювання коду прологу й епілогу.", size=11, color=MUTED))

    render(os.path.join(IMG, 'software-pipelining.svg'), w, h, *frags)


if __name__ == '__main__':
    fig_bundle_layout()
    fig_predication()
    fig_speculation_alat()
    fig_software_pipelining()
    print("All figures generated successfully.")
