# -*- coding: utf-8 -*-
"""Фігури теми «Вісім оман розподілених обчислень». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GREEN_F = "#d4edda"
RED_F   = "#fdecea"
BLUE_F  = "#e8f0fe"
WARN_F  = "#fff3cd"

# ── 1. direct-vs-remote-call: локальний виклик проти віддаленого ────────────
def fig_direct_vs_remote():
    W, H = 1000, 440
    f = []

    f.append(rect(10, 10, 980, 420, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 38, "Локальний виклик функції проти віддаленого виклику (RPC)", size=15, bold=True, color=INK))

    # Ліва колонка: Локальний виклик (In-Process)
    f.append(rect(30, 60, 450, 350, fill="#fafbfc", stroke=MUTED, sw=1, rx=6))
    f.append(text(255, 88, "Локальний виклик (In-Process Memory)", size=13, bold=True, color=FIELD))

    # Блоки локального виклику
    b1, _, _ = textbox(130, 150, "Функція-ініціатор\n(Caller Stack)", size=11, bold=True, min_w=140, pad=8, fill=BLUE_F, stroke=FIELD)
    f.append(b1)

    b2, _, _ = textbox(380, 150, "Виконувана функція\n(Callee Body)", size=11, bold=True, min_w=140, pad=8, fill=GREEN_F, stroke=FIELD)
    f.append(b2)

    # Стрілки туди й назад
    f.append(arrow(205, 135, 305, 135, color=FIELD, sw=1.5))
    f.append(text(255, 125, "вказівник / регістри", size=10, color=MUTED))

    f.append(arrow(305, 165, 205, 165, color=FIELD, sw=1.5))
    f.append(text(255, 182, "значення у стеку", size=10, color=MUTED))

    # Характеристики локального
    props_local = [
        "• Адресний простір: спільна оперативна пам'ять (RAM)",
        "• Затримка: детермінована (~1–10 наносекунд)",
        "• Передача аргументів: за посиланням (нуль копіювань)",
        "• Доля процесу: спільна (або працюють обидва, або падіння OS)",
        "• Видимість результату: успіх або перехоплений виняток"
    ]
    f.append(rect(45, 215, 420, 180, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(text(255, 238, "Властивості виконання в пам'яті:", size=11, bold=True, color=FIELD))
    f.append(mtext(60, 268, props_local, size=10.5, color=INK, anchor="start", lh=1.45))

    # Права колонка: Віддалений виклик (Remote Procedure Call)
    f.append(rect(520, 60, 450, 350, fill="#fafbfc", stroke=MUTED, sw=1, rx=6))
    f.append(text(745, 88, "Віддалений виклик (RPC через мережу)", size=13, bold=True, color=POS))

    # Блоки віддаленого виклику
    b3, _, _ = textbox(595, 150, "Клієнтський вузол\n(Process A)", size=11, bold=True, min_w=120, pad=8, fill=BLUE_F, stroke=POS)
    f.append(b3)

    b4, _, _ = textbox(745, 150, "Мережа / Канал\n(Ненадійний)", size=10, bold=True, min_w=120, pad=6, fill=WARN_F, stroke=POS)
    f.append(b4)

    b5, _, _ = textbox(895, 150, "Серверний вузол\n(Process B)", size=11, bold=True, min_w=120, pad=8, fill=RED_F, stroke=POS)
    f.append(b5)

    # Стрілки через мережу
    f.append(arrow(660, 135, 680, 135, color=POS, sw=1.2))
    f.append(arrow(810, 135, 830, 135, color=POS, sw=1.2))
    f.append(arrow(830, 165, 810, 165, color=POS, sw=1.2))
    f.append(arrow(680, 165, 660, 165, color=POS, sw=1.2))

    # Характеристики віддаленого
    props_remote = [
        "• Адресний простір: ізольовані вузли, серіалізація байтів",
        "• Затримка: недетермінована (~0.5–100+ мілісекунд)",
        "• Передача аргументів: глибоке копіювання через сокет",
        "• Доля процесу: незалежна (клієнт живий, сервер завис)",
        "• Видимість результату: три стани (Успіх / Збій / Невідомо)"
    ]
    f.append(rect(535, 215, 420, 180, fill="#ffffff", stroke=LINE, sw=1, rx=4))
    f.append(text(745, 238, "Властивості виконання через мережу:", size=11, bold=True, color=POS))
    f.append(mtext(550, 268, props_remote, size=10.5, color=INK, anchor="start", lh=1.45))

    render(out("direct-vs-remote-call.svg"), W, H, *f,
           title="Локальний виклик у пам'яті проти віддаленого виклику через мережу")


# ── 2. rpc-three-state-ambiguity: три стани невизначеності ──────────────────
def fig_rpc_three_state():
    W, H = 1000, 380
    f = []

    f.append(rect(10, 10, 980, 360, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 36, "Три стани невизначеності при мережевому таймауті", size=15, bold=True, color=INK))

    cases = [
        ("Сценарій А: Запит втрачено", "Мережа скинула пакет до сервера",
         ["1. Запит відправлено клієнтом",
          "2. Пакет дропнуто в комутаторі",
          "3. Сервер НЕ отримав запит",
          "4. Стан сервера: НЕ змінено",
          "5. Клієнт фіксує: Timeout Error"],
         180, RED_F, POS),
        ("Сценарій Б: Збій під час обробки", "Сервер упав під час виконання",
         ["1. Запит успішно доставлено",
          "2. Сервер почав транзакцію",
          "3. Сервер упав / OOM / паніка",
          "4. Стан сервера: частково змінено",
          "5. Клієнт фіксує: Timeout Error"],
         500, WARN_F, FIELD),
        ("Сценарій В: Відповідь втрачено", "Мережа скинула ACK/Response",
         ["1. Запит успішно виконано",
          "2. Сервер закомітив стан",
          "3. Відповідь втрачено на звороті",
          "4. Стан сервера: ПОВНІСТЮ змінено",
          "5. Клієнт фіксує: Timeout Error"],
         820, GREEN_F, POS)
    ]

    for title, subtitle, details, cx, fill_c, stroke_c in cases:
        f.append(rect(cx - 145, 60, 290, 255, fill="#fafbfc", stroke=MUTED, sw=1, rx=6))
        f.append(rect(cx - 135, 72, 270, 48, fill=fill_c, stroke=stroke_c, sw=1.2, rx=4))
        f.append(text(cx, 90, title, size=11.5, bold=True, color=stroke_c))
        f.append(text(cx, 107, subtitle, size=10, italic=True, color=INK))

        # Опис кроків
        f.append(mtext(cx - 125, 145, details, size=10.5, color=INK, anchor="start", lh=1.5))

    f.append(rect(30, 328, 940, 32, fill="#f8d7da", stroke=POS, sw=1, rx=4))
    f.append(text(500, 348, "Висновок клієнта однаковий («Timeout»), але стан бази даних діаметрально протилежний!", size=11, bold=True, color=POS))

    render(out("rpc-three-state-ambiguity.svg"), W, H, *f,
           title="Три стани невизначеності мережевого виклику")


# ── 3. eight-fallacies-map: карта 8 оман розподілених обчислень ─────────────
def fig_eight_fallacies():
    W, H = 1000, 530
    f = []

    f.append(rect(10, 10, 980, 510, fill="#ffffff", stroke=MUTED, sw=1, rx=8))
    f.append(text(500, 36, "Вісім оман розподілених обчислень: фізична реальність та інженерний захист", size=15, bold=True, color=INK))

    fallacies = [
        ("1. Мережа надійна", "Втрати пакетів, розриви, ресети", "Таймаути, ретраї, ідемпотентність", 180, 105),
        ("2. Затримка нульова", "Швидкість світла, черги пакетів", "Батчинг, асинхронність, кеш", 500, 105),
        ("3. Смуга нескінченна", "Насичення NIC, ліміти MTU", "Стислі бінарні формати (Protobuf)", 820, 105),

        ("4. Мережа безпечна", "Перехоплення, MITM-атаки", "Zero Trust, mTLS, підписані JWT", 180, 240),
        ("5. Топологія незмінна", "Динамічні IP, автоскейлінг", "Service Discovery, Health Check", 500, 240),
        ("6. Один адміністратор", "Різні команди, несумісні конфіги", "Семантичне версіювання, Tracing", 820, 240),

        ("7. Вартість передачі = 0", "Маршалінг у CPU, тарифи хмари", "Zero-copy, пули з'єднань, AZ-роутинг", 340, 375),
        ("8. Мережа однорідна", "Різні ОС, процесори (endianness)", "Канонічні IDL-схеми, узгодження типів", 660, 375),
    ]

    for name, reality, defense, cx, cy in fallacies:
        f.append(rect(cx - 150, cy - 40, 300, 115, fill="#fafbfc", stroke=LINE, sw=1.2, rx=6))
        f.append(rect(cx - 150, cy - 40, 300, 28, fill=BLUE_F, stroke=FIELD, sw=1, rx=6))
        f.append(text(cx, cy - 22, name, size=11.5, bold=True, color=FIELD))

        f.append(text(cx - 140, cy + 5, "Реальність:", size=9.5, bold=True, color=POS, anchor="start"))
        f.append(text(cx - 70, cy + 5, reality, size=9.5, color=INK, anchor="start"))

        f.append(text(cx - 140, cy + 32, "Захист:", size=9.5, bold=True, color=FIELD, anchor="start"))
        f.append(text(cx - 70, cy + 32, defense, size=9.5, color=INK, anchor="start"))

    render(out("eight-fallacies-map.svg"), W, H, *f,
           title="Матриця восьми оман розподілених систем")


if __name__ == "__main__":
    fig_direct_vs_remote()
    fig_rpc_three_state()
    fig_eight_fallacies()
    print("Figures generated successfully in", IMG)
