# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

HOT  = "#fdecea"
COLD = "#eef4ff"
GRN  = "#eafaf1"
WARN = "#fff8e1"
PURP = "#f3e8ff"


# ── Фігура 1: Спостережницький ефект та часові шкали (Probe Effect) ──────────
def fig_observer_effect_timing():
    W, H = 1080, 520
    frags = []

    frags.append(text(W / 2, 35, "Спостережницький ефект (Probe Effect) у багатопотоковому середовищі", size=17, bold=True))

    PW, PH = 490, 430
    PY = 65

    # Панель 1: Нативне виконання
    p1_x = 35
    frags.append(rect(p1_x, PY, PW, PH, fill=BG, stroke=POS, sw=2, rx=8))
    frags.append(text(p1_x + PW / 2, PY + 28, "Нативне виконання (без діагностики)", size=15, bold=True, color=POS))
    frags.append(line(p1_x + 20, PY + 42, p1_x + PW - 20, PY + 42, color=MUTED, sw=1))

    # Потік 1
    frags.append(text(p1_x + 75, PY + 75, "Потік 1:", size=13, bold=True, anchor="start"))
    frags.append(line(p1_x + 75, PY + 105, p1_x + PW - 30, PY + 105, color=LINE, sw=2))
    b1_1, _, _ = textbox(p1_x + 155, PY + 105, "Зчитування ptr", size=11, fill=COLD, stroke=NEG, pad=6)
    b1_2, _, _ = textbox(p1_x + 295, PY + 105, "Виклик ptr->func()", size=11, fill=HOT, stroke=POS, pad=6)
    frags.extend([b1_1, b1_2])

    # Потік 2
    frags.append(text(p1_x + 75, PY + 165, "Потік 2:", size=13, bold=True, anchor="start"))
    frags.append(line(p1_x + 75, PY + 195, p1_x + PW - 30, PY + 195, color=LINE, sw=2))
    b2_1, _, _ = textbox(p1_x + 225, PY + 195, "free(ptr) + обнулення", size=11, fill=HOT, stroke=POS, pad=6)
    frags.append(b2_1)

    # Зона колізії / гонки
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="none" stroke="%s" stroke-width="1.5" stroke-dasharray="5 4"/>' % (p1_x + 195, PY + 65, 125, 175, POS))
    frags.append(text(p1_x + 257, PY + 265, "Вікно гонки (Use-After-Free)", size=12, bold=True, color=POS))
    frags.append(text(p1_x + 257, PY + 285, "Потік 2 звільняє пам'ять до виклику в Потоці 1", size=10, color=POS))

    # Вердикт 1
    res1, _, _ = textbox(p1_x + PW / 2, PY + 360, "Результат: СТАБІЛЬНИЙ ЗБІЙ (SIGSEGV)\nПам'ять пошкоджено через неспівпадання таймінгів", size=12, fill=HOT, stroke=POS, bold=True, pad=8)
    frags.append(res1)

    # Панель 2: З додаванням printf / спостереженням
    p2_x = 555
    frags.append(rect(p2_x, PY, PW, PH, fill=BG, stroke=FIELD, sw=2, rx=8))
    frags.append(text(p2_x + PW / 2, PY + 28, "З додаванням printf(...) або відладчика", size=15, bold=True, color=FIELD))
    frags.append(line(p2_x + 20, PY + 42, p2_x + PW - 20, PY + 42, color=MUTED, sw=1))

    # Потік 1 з затримкою
    frags.append(text(p2_x + 45, PY + 75, "Потік 1:", size=13, bold=True, anchor="start"))
    frags.append(line(p2_x + 45, PY + 105, p2_x + PW - 20, PY + 105, color=LINE, sw=2))
    bp1_1, _, _ = textbox(p2_x + 110, PY + 105, "printf(\"trace\")", size=11, fill=WARN, stroke="#d97706", pad=6)
    bp1_2, _, _ = textbox(p2_x + 230, PY + 105, "Зчитування ptr", size=11, fill=COLD, stroke=NEG, pad=6)
    bp1_3, _, _ = textbox(p2_x + 365, PY + 105, "Виклик ptr->func()", size=11, fill=GRN, stroke=FIELD, pad=6)
    frags.extend([bp1_1, bp1_2, bp1_3])

    # Потік 2
    frags.append(text(p2_x + 45, PY + 165, "Потік 2:", size=13, bold=True, anchor="start"))
    frags.append(line(p2_x + 45, PY + 195, p2_x + PW - 20, PY + 195, color=LINE, sw=2))
    bp2_1, _, _ = textbox(p2_x + 420, PY + 195, "free(ptr)", size=11, fill=COLD, stroke=NEG, pad=6)
    frags.append(bp2_1)

    # Пояснення розриву
    frags.append(arrow(p2_x + 110, PY + 130, p2_x + 110, PY + 180, color="#d97706", sw=1.5))
    frags.append(text(p2_x + 230, PY + 250, "printf затримує Потік 1 на ~30-50 мкс", size=12, bold=True, color=FIELD))
    frags.append(text(p2_x + 230, PY + 270, "I/O syscall + блокування stdout розводять потоки в часі", size=10, color=MUTED))

    # Вердикт 2
    res2, _, _ = textbox(p2_x + PW / 2, PY + 360, "Результат: ПОМИЛКА ЗНИКАЄ (Гейзенбаг)\nКод успішно виконується, дефект маскується вимірюванням", size=12, fill=GRN, stroke=FIELD, bold=True, pad=8)
    frags.extend([res2])

    render(os.path.join(IMG, "observer-effect-timing.svg"), W, H, *frags)


# ── Фігура 2: Таксономія помилок за Джимом Греєм ─────────────────────────────
def fig_bug_taxonomy_gray():
    W, H = 1080, 560
    frags = []

    frags.append(text(W / 2, 35, "Таксономія програмних помилок за Джимом Греєм та розвитком", size=17, bold=True))

    cards = [
        (40,  70, 480, 215, "Боровські баги (Bohrbugs)",
         ["Детерміновані, легко відтворювані помилки.",
          "Проявляються надійно за однакового набору вхідних даних.",
          "Легко ізолюються модульним тестом і фіксуються відладчиком.",
          "Аналогія: класична детермінована модель атома Бора."],
         COLD, NEG, "Детермінізм: 100% | Стійкі до спостереження"),

        (560, 70, 480, 215, "Гейзенбаги (Heisenbugs)",
         ["Плаваючий дефект, що змінюється або зникає при спробі",
          "його дослідити (додавання логів printf, запуск у gdb, -O0).",
          "Причини: гонки потоків, неініціалізована пам'ять, таймінги I/O.",
          "Аналогія: квантовий принцип невизначеності Гейзенберга."],
         HOT, POS, "Детермінізм: низький | Чутливі до спостереження"),

        (40,  310, 480, 215, "Мандальбаги (Mandelbugs)",
         ["Складні помилки з хаотичною, нелінійною поведінкою.",
          "Причина лежить у далекій, непрямій залежності або затримці:",
          "переповнення буфера кілька хвилин тому, фрагментація купи.",
          "Аналогія: фрактал Мандельброта (прості правила → хаос)."],
         WARN, "#b8860b", "Складність: екстремальна | Довгий ланцюг причини"),

        (560, 310, 480, 215, "Шредінбаги (Schroedinbugs)",
         ["Дефект, який не проявляється взагалі впродовж місяців",
          "або років роботи в продакшені, доки хтось не помітить у коді,",
          "що він теоретично не повинен був працювати взагалі.",
          "Аналогія: кіт Шредінгера (стан колапсує при спостереженні)."],
         PURP, "#7c3aed", "Стан: прихований парадокс | Збій після усвідомлення")
    ]

    for cx, cy, cw, ch, title, lines, bg_col, stroke_col, badge in cards:
        frags.append(rect(cx, cy, cw, ch, fill=BG, stroke=stroke_col, sw=2, rx=8))
        frags.append(rect(cx + 8, cy + 8, cw - 16, 32, fill=bg_col, stroke="none", rx=4))
        frags.append(text(cx + cw / 2, cy + 30, title, size=14, bold=True, color=stroke_col))

        ly = cy + 62
        for ln in lines:
            frags.append(text(cx + 20, ly, "• " + ln, size=11, color=INK, anchor="start"))
            ly += 22

        frags.append(line(cx + 15, cy + ch - 38, cx + cw - 15, cy + ch - 38, color=MUTED, sw=1))
        frags.append(text(cx + cw / 2, cy + ch - 16, badge, size=11, bold=True, color=stroke_col))

    render(os.path.join(IMG, "bug-taxonomy-gray.svg"), W, H, *frags)


# ── Фігура 3: Архітектура тіньової пам'яті (Shadow Memory) ───────────────────
def fig_sanitizer_shadow_memory():
    W, H = 1080, 520
    frags = []

    frags.append(text(W / 2, 35, "Архітектура тіньової пам'яті санітайзерів (ASan / TSan)", size=17, bold=True))

    # Ліва частина: Пам'ять застосунку
    frags.append(rect(50, 75, 420, 400, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(260, 105, "Пам'ять застосунку (Application Memory)", size=14, bold=True, color=INK))
    frags.append(line(70, 120, 450, 120, color=MUTED, sw=1))

    # Байти застосунку
    frags.append(text(120, 145, "Адреса", size=11, bold=True, color=MUTED))
    frags.append(text(260, 145, "Дані (8-байтний блок)", size=11, bold=True, color=MUTED))
    frags.append(text(400, 145, "Стан", size=11, bold=True, color=MUTED))

    app_rows = [
        ("0x7ffd0000", "Червона зона стеку (Redzone)", HOT, POS, "Отруєно (8B)"),
        ("0x7ffd0008", "Буфер: char data[6] + 2B pad", GRN, FIELD, "Доступно (6B)"),
        ("0x7ffd0010", "Червона зона стеку (Redzone)", HOT, POS, "Отруєно (8B)"),
        ("0x7ffd0018", "Вказівник повернення стек-фрейму", COLD, NEG, "Доступно (8B)"),
        ("0x7ffd0020", "Звільнений буфер (Quarantine)", WARN, "#b8860b", "Звільнено (UAF)")
    ]

    ry = 165
    for addr, desc, fill_col, stroke_col, st in app_rows:
        frags.append(rect(70, ry, 380, 45, fill=fill_col, stroke=stroke_col, sw=1.2, rx=4))
        frags.append(text(120, ry + 27, addr, size=10, bold=True, color=INK))
        frags.append(text(250, ry + 27, desc, size=10, color=INK))
        frags.append(text(400, ry + 27, st, size=9, bold=True, color=stroke_col))
        ry += 58

    # Центральне відображення (стрілка + формула)
    mid_x = 540
    frags.append(rect(mid_x - 55, 215, 110, 100, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    frags.append(text(mid_x, 240, "Формула ASan:", size=10, bold=True, color=INK))
    frags.append(text(mid_x, 262, "ShadowAddr =", size=10, color=MUTED))
    frags.append(text(mid_x, 280, "(Addr >> 3)", size=10, bold=True, color=POS))
    frags.append(text(mid_x, 298, "+ Offset", size=10, bold=True, color=POS))

    frags.append(arrow(455, 265, 480, 265, color=POS, sw=2))
    frags.append(arrow(600, 265, 625, 265, color=FIELD, sw=2))

    # Права частина: Тіньова пам'ять
    frags.append(rect(630, 75, 400, 400, fill=BG, stroke=LINE, sw=1.5, rx=8))
    frags.append(text(830, 105, "Тіньова пам'ять (Shadow Memory: 1/8)", size=14, bold=True, color=INK))
    frags.append(line(650, 120, 1010, 120, color=MUTED, sw=1))

    frags.append(text(690, 145, "Тіньова адреса", size=11, bold=True, color=MUTED))
    frags.append(text(800, 145, "Байт-значення", size=11, bold=True, color=MUTED))
    frags.append(text(935, 145, "Інтерпретація ASan", size=11, bold=True, color=MUTED))

    sh_rows = [
        ("0x1fffba00", "0xF1", HOT, POS, "Stack Left Redzone"),
        ("0x1fffba01", "0x06", GRN, FIELD, "6 байтів валідні"),
        ("0x1fffba02", "0xF3", HOT, POS, "Stack Right Redzone"),
        ("0x1fffba03", "0x00", COLD, NEG, "Всі 8 байтів валідні"),
        ("0x1fffba04", "0xFD", WARN, "#b8860b", "Freed Heap Memory")
    ]

    sry = 165
    for saddr, val, fill_col, stroke_col, interp in sh_rows:
        frags.append(rect(650, sry, 360, 45, fill=fill_col, stroke=stroke_col, sw=1.2, rx=4))
        frags.append(text(695, sry + 27, saddr, size=10, bold=True, color=INK))
        frags.append(text(800, sry + 27, val, size=11, bold=True, color=stroke_col))
        frags.append(text(935, sry + 27, interp, size=10, color=INK))
        sry += 58

    render(os.path.join(IMG, "sanitizer-shadow-memory.svg"), W, H, *frags)


# ── Фігура 4: Детермінований запис і відтворення (Mozilla rr) ─────────────────
def fig_rr_record_replay_architecture():
    W, H = 1080, 520
    frags = []

    frags.append(text(W / 2, 35, "Архітектура детермінованого запису й відтворення (Mozilla rr)", size=17, bold=True))

    PW, PH = 490, 420
    PY = 65
    p1_x = 35

    frags.append(rect(p1_x, PY, PW, PH, fill=BG, stroke=POS, sw=2, rx=8))
    frags.append(text(p1_x + PW / 2, PY + 28, "Фаза запису: rr record ./app", size=15, bold=True, color=POS))
    frags.append(line(p1_x + 20, PY + 42, p1_x + PW - 20, PY + 42, color=MUTED, sw=1))

    # Блоки запису
    b_cpu, _, _ = textbox(p1_x + 140, PY + 95, "CPU execution\nДетерміновані інструкції", size=10, fill=COLD, stroke=NEG, pad=6)
    b_pmu, _, _ = textbox(p1_x + 360, PY + 95, "PMU Hardware Counter\nЛічильник умовних переходів", size=10, fill=WARN, stroke="#d97706", pad=6)
    frags.extend([b_cpu, b_pmu])

    frags.append(text(p1_x + PW / 2, PY + 165, "Джерела недетермінізму (перехоплюються через ptrace / seccomp):", size=10, bold=True, color=INK))

    b_sys, _, _ = textbox(p1_x + 95, PY + 215, "Системні виклики\n(read, time, epoll)", size=9, fill=HOT, stroke=POS, pad=5)
    b_sig, _, _ = textbox(p1_x + 245, PY + 215, "Асинхронні сигнали\n(SIGINT, SIGALRM)", size=9, fill=HOT, stroke=POS, pad=5)
    b_tsc, _, _ = textbox(p1_x + 395, PY + 215, "Інструкції часу/CPU\n(rdtsc, cpuid)", size=9, fill=HOT, stroke=POS, pad=5)
    frags.extend([b_sys, b_sig, b_tsc])

    frags.append(arrow(p1_x + PW / 2, PY + 260, p1_x + PW / 2, PY + 300, color=POS, sw=2))

    trace_box, _, _ = textbox(p1_x + PW / 2, PY + 345, "Компактний слід виконання (Trace Directory)\n• Повна фіксація всіх входів і результатів syscalls\n• Точні часові мітки переходів PMU", size=11, fill=FILL, stroke=LINE, bold=True, pad=8)
    frags.append(trace_box)

    # Фаза 2: Відтворення (Replay)
    p2_x = 555
    frags.append(rect(p2_x, PY, PW, PH, fill=BG, stroke=FIELD, sw=2, rx=8))
    frags.append(text(p2_x + PW / 2, PY + 28, "Фаза відтворення: rr replay", size=15, bold=True, color=FIELD))
    frags.append(line(p2_x + 20, PY + 42, p2_x + PW - 20, PY + 42, color=MUTED, sw=1))

    # Блоки відтворення
    in_box, _, _ = textbox(p2_x + PW / 2, PY + 95, "Читання збереженого сліду (Trace Log)\nВсі зовнішні дані інжектуються з журналу", size=11, fill=FILL, stroke=LINE, pad=6)
    frags.append(in_box)

    frags.append(arrow(p2_x + PW / 2, PY + 135, p2_x + PW / 2, PY + 170, color=FIELD, sw=2))

    sim_box, _, _ = textbox(p2_x + PW / 2, PY + 215, "100% Детерміноване виконання в 1 потік\n• PMU відраховує точну кількість переходів\n• Стан регістрів і пам'яті біт-у-біт повторюється", size=11, fill=GRN, stroke=FIELD, pad=8)
    frags.append(sim_box)

    frags.append(arrow(p2_x + PW / 2, PY + 265, p2_x + PW / 2, PY + 305, color=FIELD, sw=2))

    gdb_box, _, _ = textbox(p2_x + PW / 2, PY + 355, "Time-Travel Debugging у GDB:\n• reverse-continue  • reverse-stepi\n• reverse-watchpoints (хто змінив змінну!)", size=11, fill=COLD, stroke=NEG, bold=True, pad=8)
    frags.append(gdb_box)

    render(os.path.join(IMG, "rr-record-replay-architecture.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_observer_effect_timing()
    fig_bug_taxonomy_gray()
    fig_sanitizer_shadow_memory()
    fig_rr_record_replay_architecture()
    print("All figures generated successfully.")
