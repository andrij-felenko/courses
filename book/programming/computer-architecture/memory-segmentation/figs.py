# -*- coding: utf-8 -*-
"""Фігури для теми «Сегментація пам'яті»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def _box(cx, cy, s, **kw):
    """textbox із центром (cx,cy); повертає (frag, (left,right,top,bottom))."""
    frag, w, h = textbox(cx, cy, s, **kw)
    return frag, (cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2)


def fig_real_mode():
    """1. Формування 20-бітної фізичної адреси в реальному режимі 8086."""
    W, H = 940, 520
    F = []

    # Заголовок блоків
    F.append(text(W / 2, 40, "Формування фізичної адреси в реальному режимі 8086", size=18, bold=True))

    # Сегментний регістр (ліворуч)
    b_seg, e_seg = _box(240, 120, "Сегментний регістр (16 біт)\nнаприклад: 0x2000", size=14, bold=True, fill="#eaf0fd", stroke=NEG)
    F.append(b_seg)

    # Зсув на 4 біти
    b_shift, e_shift = _box(240, 220, "Зсув ліворуч на 4 біти (×16)\n0x20000 (20 біт)", size=13, fill="#fff2df", stroke="#d97706")
    F.append(b_shift)
    F.append(arrow(240, e_seg[3], 240, e_shift[2], color=NEG, sw=2))

    # Зсув (Offset) (праворуч)
    b_off, e_off = _box(700, 120, "Ефективна адреса / Зсув (16 біт)\nнаприклад: 0x015A", size=14, bold=True, fill="#eafaf0", stroke=FIELD)
    F.append(b_off)

    # Суматор 20 біт по центру
    b_add, e_add = _box(470, 320, ["20-бітний апаратний суматор", "0x20000 + 0x0015A"], size=14, bold=True, fill="#f4f6f8", stroke=LINE)
    F.append(b_add)

    # Стрілки від зсунутого сегмента і від оффсету до суматора
    F.append(arrow(240, e_shift[3], 410, e_add[2], color="#d97706", sw=2))
    F.append(arrow(700, e_off[3], 530, e_add[2], color=FIELD, sw=2))

    # Результат: Фізична адреса
    b_phys, e_phys = _box(470, 440, ["Фізична адреса на шині A0..A19 (20 біт)", "0x2015A  (діапазон 0x00000 .. 0xFFFFF, 1 МБ RAM)"],
                          size=14, bold=True, fill="#fdecea", stroke=POS, color=POS)
    F.append(b_phys)
    F.append(arrow(470, e_add[3], 470, e_phys[2], color=POS, sw=2.4))

    render(os.path.join(IMG, 'real-mode-addressing.svg'), W, H, *F,
           title="Формування 20-бітної фізичної адреси в реальному режимі")


def fig_descriptor_selector():
    """2. Селектор сегмента та структура 8-байтового дескриптора GDT."""
    W, H = 1000, 580
    F = []

    F.append(text(W / 2, 36, "Селектор сегмента (16 біт) та дескриптор сегмента (64 біти)", size=18, bold=True))

    # --- Верхня частина: Селектор сегмента ---
    y_sel = 100
    F.append(text(60, y_sel + 20, "Селектор:", size=15, bold=True, anchor="start"))
    
    # 13 біт Index [15:3]
    F.append(fitbox(180, y_sel, 440, 44, "Index [15:3] — 13 бітів (індекс у таблиці GDT/LDT, до 8192 записів)", size=12, fill="#eaf0fd", stroke=NEG))
    # 1 біт TI [2]
    F.append(fitbox(630, y_sel, 150, 44, "TI [2]: 0=GDT, 1=LDT", size=12, fill="#fff2df", stroke="#d97706"))
    # 2 біти RPL [1:0]
    F.append(fitbox(790, y_sel, 160, 44, "RPL [1:0]: 0..3 (привілей)", size=12, fill="#fdecea", stroke=POS))

    # Стрілка вниз до таблиці GDT
    F.append(arrow(400, y_sel + 44, 400, 190, color=NEG, sw=2))
    F.append(text(410, 172, "Вибірка запису за індексом", size=12, color=NEG, anchor="start"))

    # --- Середня частина: GDTR та Таблиця GDT ---
    b_gdtr, e_gdtr = _box(150, 240, ["Регістр GDTR (48 біт):", "Limit (16 біт) | Base (32 біти)"], size=12, fill="#f4f6f8", stroke=LINE)
    F.append(b_gdtr)
    F.append(arrow(e_gdtr[1], 240, 310, 240, color=LINE, sw=1.8))

    # Таблиця GDT (спрощена схема масиву)
    F.append(rect(310, 190, 200, 100, fill="#ffffff", stroke=LINE, sw=1.5, rx=4))
    F.append(text(410, 212, "GDT[0]: Нульовий дескриптор", size=11, color=MUTED))
    F.append(rect(314, 222, 192, 28, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=2))
    F.append(text(410, 240, "GDT[Index]: Цільовий дескриптор", size=11, bold=True, color=NEG))
    F.append(text(410, 272, "GDT[Index+1]: Наступний...", size=11, color=MUTED))

    # Стрілка від знайденого дескриптора до розгортки структури
    F.append(arrow(506, 236, 590, 236, color=NEG, sw=2))
    F.append(text(548, 224, "8 байтів", size=11, color=NEG))

    # --- Нижня частина: 64-бітний Дескриптор (Детальна структура) ---
    F.append(text(W / 2, 325, "Анатомія 8-байтового дескриптора сегмента (IA-32):", size=14, bold=True))

    y_d1 = 350
    # Байт 7..4 (старші 32 біти)
    F.append(fitbox(50, y_d1, 180, 46, "Base [31:24]\n(8 бітів)", size=12, fill="#eafaf0", stroke=FIELD))
    F.append(fitbox(235, y_d1, 200, 46, "Прапорці (G, D/B, L, AVL)\nLimit [19:16] (4 біти)", size=11, fill="#fff2df", stroke="#d97706"))
    F.append(fitbox(440, y_d1, 220, 46, "Атрибути доступу (P, DPL, S)\nType (4 біти: r/w/x/c/a)", size=11, fill="#fdecea", stroke=POS))
    F.append(fitbox(665, y_d1, 285, 46, "Base [23:16]\n(8 бітів)", size=12, fill="#eafaf0", stroke=FIELD))

    y_d2 = 410
    # Байт 3..0 (молодші 32 біти)
    F.append(fitbox(50, y_d2, 450, 46, "Base Address [15:0] — Базова адреса сегмента (16 бітів)", size=12, fill="#eafaf0", stroke=FIELD))
    F.append(fitbox(510, y_d2, 440, 46, "Segment Limit [15:0] — Межа сегмента (16 бітів)", size=12, fill="#fff2df", stroke="#d97706"))

    # Пояснення відновлення
    F.append(text(W / 2, 490, "Процесор апаратно склеює розбиті поля: Base = [31:24] | [23:16] | [15:0] (32 біти)", size=12, bold=True, color=FIELD))
    F.append(text(W / 2, 514, "Limit = [19:16] | [15:0] (20 бітів). Якщо Granularity (G)=1, межа множиться на 4 КБ (до 4 ГБ)", size=12, color=MUTED))

    render(os.path.join(IMG, 'descriptor-and-selector.svg'), W, H, *F,
           title="Селектор і дескриптор сегмента GDT")


def fig_shadow_cache():
    """3. Видимий селектор і прихований тіньовий регістр дескриптора."""
    W, H = 960, 540
    F = []

    F.append(text(W / 2, 38, "Тіньовий кеш дескрипторів (Shadow Descriptor Cache)", size=18, bold=True))

    # Блок CPU сегментного регістра
    F.append(rect(40, 80, 530, 420, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))
    F.append(text(305, 110, "Внутрішня структура сегментного регістра CPU (CS, DS, SS...)", size=14, bold=True))

    # Видима частина
    b_vis, e_vis = _box(160, 180, ["Видима частина (16 біт):", "Селектор (Selector)", "(доступний для mov ds, ax)"],
                        size=12, bold=True, fill="#eaf0fd", stroke=NEG)
    F.append(b_vis)

    # Невидима частина (Тіньовий кеш)
    F.append(rect(60, 250, 490, 225, fill="#fff8f0", stroke="#d97706", sw=1.5, rx=6))
    F.append(text(305, 275, "Прихована частина — Тіньовий кеш (Shadow Cache):", size=13, bold=True, color="#d97706"))

    F.append(fitbox(80, 295, 450, 40, "Базова адреса (Base Address): 32/64 біти", size=12, fill="#eafaf0", stroke=FIELD))
    F.append(fitbox(80, 345, 450, 40, "Межа сегмента (Segment Limit): 32 біти (у байтах)", size=12, fill="#fff2df", stroke="#d97706"))
    F.append(fitbox(80, 395, 450, 60, "Атрибути захисту: DPL (0..3), Тип (Read/Write/Exec),\nРозрядність (D/B), Присутність (P), Гранулярність (G)", size=11, fill="#fdecea", stroke=POS))

    # Зовнішня оперативна пам'ять (GDT)
    F.append(rect(640, 80, 280, 210, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))
    F.append(text(780, 110, "Оперативна пам'ять (RAM)", size=14, bold=True))
    b_gdt, e_gdt = _box(780, 180, ["Таблиця GDT в пам'яті", "8-байтовий дескриптор", "(Base, Limit, Rights)"], size=12, fill="#eaf0fd", stroke=NEG)
    F.append(b_gdt)

    # Крок 1: Завантаження селектора
    F.append(arrow(e_vis[1], 180, e_gdt[0], 180, color=NEG, sw=2.2))
    F.append(text((e_vis[1] + e_gdt[0]) / 2, 165, "1. Одноразове читання GDT", size=12, bold=True, color=NEG))

    # Крок 2: Заповнення тіньового кешу
    F.append(arrow(780, e_gdt[3], 550, 360, color="#d97706", sw=2.2))
    F.append(text(720, 330, "2. Апаратне декодування\nу тіньовий регістр", size=12, bold=True, color="#d97706"))

    # Крок 3: Виконання звичайних інструкцій
    b_exec, e_exec = _box(780, 420, ["Кожна інструкція [ebx]:", "Читає Base/Limit миттєво", "з тіньового кешу без RAM!"],
                          size=12, bold=True, fill="#eafaf0", stroke=FIELD)
    F.append(b_exec)
    F.append(arrow(550, 420, e_exec[0], 420, color=FIELD, sw=2.4))
    F.append(text((550 + e_exec[0]) / 2, 405, "3. 0 тактів затримки", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, 'shadow-descriptor-cache.svg'), W, H, *F,
           title="Видимий селектор і тіньовий регістр дескриптора")


def fig_privilege_rings():
    """4. Перевірка привілеїв (CPL, RPL, DPL) та шлюзи виклику."""
    W, H = 960, 540
    F = []

    F.append(text(W / 2, 36, "Ієрархія кілець захисту та перевірка привілеїв DPL / CPL / RPL", size=18, bold=True))

    # Кільця ліворуч (вкладені прямокутники/овали)
    cx, cy = 240, 280
    F.append(circle(cx, cy, 200, fill="#eaf0fd", stroke=LINE, sw=1.5))
    F.append(circle(cx, cy, 140, fill="#fff2df", stroke=LINE, sw=1.5))
    F.append(circle(cx, cy, 80, fill="#fdecea", stroke=LINE, sw=1.5))

    F.append(text(cx, cy - 165, "Ring 3: Застосунки (User Mode)", size=13, bold=True, color=NEG))
    F.append(text(cx, cy - 105, "Ring 1..2: Драйвери / Служби", size=12, color="#d97706"))
    F.append(text(cx, cy, "Ring 0:\nЯдро (Kernel)", size=13, bold=True, color=POS))

    # Правила перевірки праворуч
    F.append(rect(480, 75, 450, 410, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    F.append(text(705, 105, "Апаратні правила доступу IA-32:", size=14, bold=True))

    # Правило 1: Дані
    b_d, _ = _box(705, 170, ["1. Доступ до сегмента даних (DS, ES, SS):",
                             "Діє правило: max(CPL, RPL) <= DPL",
                             "CPL (поточний код) і RPL (селектор) мають бути",
                             "не менш привілейованими, ніж дескриптор даних.",
                             "Порушення -> Генеральний збій захисту (#GP)."],
                  size=11, fill="#eafaf0", stroke=FIELD)
    F.append(b_d)

    # Правило 2: Прямий перехід коду
    b_c, _ = _box(705, 275, ["2. Прямий перехід на код (JMP / CALL):",
                             "Для звичайного сегмента: CPL == DPL (той самий рівень).",
                             "Для підпорядкованого (Conforming): CPL >= DPL",
                             "(код виконується без зміни CPL викликача)."],
                  size=11, fill="#fff2df", stroke="#d97706")
    F.append(b_c)

    # Правило 3: Шлюз виклику (Call Gate)
    b_g, _ = _box(705, 395, ["3. Міжрівневий виклик через Call Gate:",
                             "Ring 3 викликає шлюз з Gate.DPL = 3.",
                             "Шлюз вказує на цільовий сегмент Ring 0.",
                             "CPU автоматично перемикає стек на стек ядра з TSS,",
                             "копіює параметри і підвищує CPL 3 -> 0."],
                  size=11, fill="#fdecea", stroke=POS)
    F.append(b_g)

    render(os.path.join(IMG, 'privilege-check-rings.svg'), W, H, *F,
           title="Правила перевірки привілеїв і кільця захисту")


def fig_flat_model():
    """5. Плоска модель пам'яті (Flat Model) та передача ролі сторінковому MMU."""
    W, H = 960, 500
    F = []

    F.append(text(W / 2, 36, "Плоска модель (Flat Model) та витіснення сегментації пейджингом", size=18, bold=True))

    # Блок 1: Логічна адреса
    b1, e1 = _box(160, 140, ["Логічна адреса:", "Селектор : Зсув (Offset)", "CS : EIP  або  DS : EAX"],
                  size=13, bold=True, fill="#eaf0fd", stroke=NEG)
    F.append(b1)

    # Блок 2: Плоский сегментний дескриптор
    b2, e2 = _box(480, 140, ["Плоский дескриптор (Flat Segment):", "Base Address = 0x00000000", "Limit = 4 ГБ (0xFFFFF, G=1)"],
                  size=13, bold=True, fill="#fff2df", stroke="#d97706")
    F.append(b2)
    F.append(arrow(e1[1], 140, e2[0], 140, color=NEG, sw=2))

    # Блок 3: Лінійна адреса
    b3, e3 = _box(800, 140, ["Лінійна адреса:", "Base + Offset = Offset", "(тотожне відображення)"],
                  size=13, bold=True, fill="#eafaf0", stroke=FIELD)
    F.append(b3)
    F.append(arrow(e2[1], 140, e3[0], 140, color="#d97706", sw=2))

    # Стрілка вниз до Сторінкового апарату MMU
    F.append(arrow(800, e3[3], 800, 260, color=FIELD, sw=2.4))
    F.append(text(810, 230, "Лінійна адреса йде на вхід MMU", size=12, color=FIELD, anchor="start"))

    # Блок 4: Сторінковий переклад (MMU Paging)
    F.append(rect(100, 270, 760, 190, fill="#ffffff", stroke=POS, sw=1.8, rx=8))
    F.append(text(480, 300, "Вся реальна ізоляція та захист перейшли до пейджингу (Сторінковий MMU):", size=14, bold=True, color=POS))

    b_p1, _ = _box(240, 370, ["Таблиці сторінок (CR3)", "Ізоляція процесів:", "Кожен процес має свій CR3"], size=12, fill="#f4f6f8", stroke=LINE)
    b_p2, _ = _box(480, 370, ["Прапорці захисту сторінок", "R/W (запис) | U/S (рівень)", "NX / XD (заборона виконання)"], size=12, fill="#fdecea", stroke=POS)
    b_p3, _ = _box(720, 370, ["Фізичні кадри RAM (4 КБ)", "Динамічне виділення", "та віртуальна пам'ять"], size=12, fill="#eafaf0", stroke=FIELD)
    F += [b_p1, b_p2, b_p3]

    F.append(arrow(340, 370, 370, 370, color=LINE, sw=1.5))
    F.append(arrow(590, 370, 620, 370, color=LINE, sw=1.5))

    render(os.path.join(IMG, 'flat-model-vs-paging.svg'), W, H, *F,
           title="Плоска модель і сторінковий переклад MMU")


def fig_x86_64_tls():
    """6. Сегнаментація в x86-64 Long Mode: FS/GS, TLS та ядро."""
    W, H = 980, 520
    F = []

    F.append(text(W / 2, 36, "Сегментація в x86-64 Long Mode: фіксація нуля та збереження FS/GS", size=18, bold=True))

    # Ліва колонка: CS, DS, ES, SS у 64-бітному режимі
    F.append(rect(40, 75, 420, 410, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    F.append(text(250, 105, "Регістри CS, DS, ES, SS у 64-біт:", size=14, bold=True))

    b_nul, _ = _box(250, 180, ["Апаратне ігнорування бази:", "База примусово = 0x0000000000000000", "Перевірку Limit вимкнено залізом"],
                    size=12, fill="#fdecea", stroke=POS)
    F.append(b_nul)

    b_cs, _ = _box(250, 310, ["Залишкове використання CS:", "• L-біт (Long Mode): 64-біт vs 32-біт сумісність",
                              "• DPL / CPL: Поточне кільце (Ring 0 vs 3)",
                              "DS, ES, SS селектори здебільшого ігноруються"],
                    size=11, fill="#fff2df", stroke="#d97706")
    F.append(b_cs)

    b_flat, _ = _box(250, 420, ["Результат: абсолютно плоский 64-бітний простір", "без сегментного накладного тягаря"],
                     size=11, bold=True, fill="#f4f6f8", stroke=LINE)
    F.append(b_flat)

    # Права колонка: FS та GS
    F.append(rect(500, 75, 440, 410, fill="#ffffff", stroke=FIELD, sw=1.8, rx=8))
    F.append(text(720, 105, "Виняток: регістри FS та GS (MSR-база):", size=14, bold=True, color=FIELD))

    b_fs, _ = _box(720, 190, ["Регістр FS: Простір користувача (TLS)",
                              "MSR IA32_FS_BASE (0xC0000100)",
                              "Вказує на Thread-Local Storage потоку",
                              "fs:0x28 -> Stack Canary (__stack_chk_guard)"],
                   size=11, fill="#eafaf0", stroke=FIELD)
    F.append(b_fs)

    b_gs, _ = _box(720, 315, ["Регістр GS: Простір ядра (Per-CPU Data)",
                              "MSR IA32_GS_BASE (0xC0000101)",
                              "MSR IA32_KERNEL_GS_BASE (0xC0000102)",
                              "Вказує на структуру CPU: current task_struct, стеки"],
                   size=11, fill="#eaf0fd", stroke=NEG)
    F.append(b_gs)

    b_swap, _ = _box(720, 420, ["Інструкція swapgs:", "Миттєвий атомарний обмін бази GS під час syscall / переривання",
                               "Ядро миттєво отримує доступ до своєї структури CPU!"],
                    size=11, bold=True, fill="#fff2df", stroke="#d97706")
    F.append(b_swap)

    render(os.path.join(IMG, 'x86-64-fs-gs-tls.svg'), W, H, *F,
           title="Сегментація в x86-64 Long Mode")


if __name__ == '__main__':
    fig_real_mode()
    fig_descriptor_selector()
    fig_shadow_cache()
    fig_privilege_rings()
    fig_flat_model()
    fig_x86_64_tls()
    print("All figures generated successfully.")
