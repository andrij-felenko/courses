# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

RED_T   = "#fdecea"
GREEN_T = "#f2faf5"
BLUE_T  = "#eaf0fd"
GREY_T  = "#f4f6f8"
YELLOW_T = "#fef9e7"
AMBER   = "#d35400"


# ── 1. Три фази паралельної зміни (Expand, Transition, Contract) ────────────────
def fig_expand_contract_phases():
    W, H = 1180, 520
    frags = []
    frags.append(text(W / 2, 36, "Життєвий цикл паралельної зміни: розширення, міграція та звуження",
                      size=17, bold=True))

    phases = [
        (40, 350, POS, RED_T, "ФАЗА 1: РОЗШИРЕННЯ (EXPAND)",
         [
             "Постачальник публікує новий контракт v2 поряд із v1.",
             "Сервер підтримує ОБИДВА інтерфейси одночасно.",
             "Жоден існуючий клієнт не ламається (100% сумісність).",
             "Клієнти v1 продовжують працювати без змін.",
         ],
         "Стан: Контракт розширено (v1 + v2)"),
        (415, 350, FIELD, GREEN_T, "ФАЗА 2: МІГРАЦІЯ (TRANSITION)",
         [
             "Клієнти поступово переходять з v1 на v2 за власним графіком.",
             "Телеметрія вимірює частку трафіку на старому інтерфейсі.",
             "Надсилаються попередження про застарівання (Deprecation).",
             "Виконується бекфіл історичних даних та подвійний запис.",
         ],
         "Стан: Трафік мігрує (v1 → v2)"),
        (790, 350, NEG, BLUE_T, "ФАЗА 3: ЗВУЖЕННЯ (CONTRACT)",
         [
             "Телеметрія підтверджує: трафік v1 впав до нуля.",
             "Старий інтерфейс v1, адаптери та шими видаляються.",
             "Видаляються застарілі колонки в базі даних.",
             "Кодова база повертається до чистого стану без легасі.",
         ],
         "Стан: Тільки v2 (чистий контракт)"),
    ]

    for x, w, col, tint, title, points, status in phases:
        frags.append(fitbox(x, 75, w, 44, title, size=13.5, bold=True, fill=tint, stroke=col, sw=2.0))
        box_text = "\n\n".join(points)
        frags.append(fitbox(x, 130, w, 240, box_text, size=12, fill=BG, stroke=col, sw=1.4))
        frags.append(fitbox(x, 385, w, 40, status, size=12, bold=True, fill=tint, stroke=col, sw=1.6))

    frags.append(arrow(393, 250, 412, 250, color=LINE, sw=2.2))
    frags.append(arrow(768, 250, 787, 250, color=LINE, sw=2.2))

    frags.append(fitbox(50, 445, 1080, 50,
                        "Ключовий інваріант: кожен крок є сумісним у часі, розгортання клієнта і сервера розчеплені,\n"
                        "а система ніколи не вимагає одночасної зупинки всіх компонентів (Zero-Downtime).",
                        size=12.5, bold=True, fill=GREY_T, stroke=LINE, sw=1.5))

    render(os.path.join(IMG, 'expand-contract-phases.svg'), W, H, *frags)


# ── 2. Потік даних під час подвійного запису, бекфілу та читання ────────────────
def fig_dual_write_dual_read():
    W, H = 1180, 560
    frags = []
    frags.append(text(W / 2, 34, "Механіка міграції стану: подвійний запис, фоновий бекфіл і перемикання читань",
                      size=17, bold=True))

    steps = [
        (40, 255, "1. Додавання нової схеми",
         "Створення колонки / таблиці B\n(nullable, без обмежень)\n\n• Старий код пише і читає A\n• Сховище готове приймати B",
         GREY_T, LINE),
        (325, 255, "2. Подвійний запис",
         "Застосунок пише в A і B\n(атомарно або через Outbox)\n\n• Нові мутації йдуть у B\n• Читання все ще з A",
         YELLOW_T, AMBER),
        (610, 255, "3. Фоновий бекфіл",
         "Пакетний воркер копіює\nісторичні записи з A в B\n\n• Умовний запис (без затирання)\n• Досягнення збіжності A ≡ B",
         GREEN_T, FIELD),
        (895, 255, "4. Перемикання й очищення",
         "Читання перемикається на B\nЗупинка запису в A\n\n• Видалення колонки A\n• Чистий стан схеми B",
         BLUE_T, NEG),
    ]

    for x, w, title, desc, tint, col in steps:
        frags.append(fitbox(x, 70, w, 40, title, size=13, bold=True, fill=tint, stroke=col, sw=1.8))
        frags.append(fitbox(x, 118, w, 190, desc, size=12, fill=BG, stroke=col, sw=1.4))

    frags.append(arrow(298, 210, 322, 210, color=LINE, sw=2.0))
    frags.append(arrow(583, 210, 607, 210, color=LINE, sw=2.0))
    frags.append(arrow(868, 210, 892, 210, color=LINE, sw=2.0))

    frags.append(fitbox(40, 330, 1100, 190,
                        "Анатомія захисту від гонки даних під час міграції сховища:\n\n"
                        "1. Подвійний запис обов'язково вмикається ДО запуску фонового бекфілу — щоб не втратити жодної нової мутації.\n"
                        "2. Фоновий бекфіл копіює записи пакетами від старіших до новіших і використовує умовний запис (Conditional Update / Version Check),\n"
                        "   аби фоновий процес випадково не перезаписав старішим значенням свіжішу мутацію, яку вже зафіксував подвійний запис.\n"
                        "3. Перемикання читання здійснюється через динамічний прапорець (Feature Flag) з поступовим зростанням частки 1% → 10% → 100%,\n"
                        "   що дозволяє миттєво відкотити читання назад на A у разі виявлення дефекту в новому форматі B.",
                        size=12, fill=GREY_T, stroke=LINE, sw=1.5))

    render(os.path.join(IMG, 'dual-write-dual-read.svg'), W, H, *frags)


# ── 3. Скінченний автомат життєвого циклу елемента API ──────────────────────────
def fig_state_machine_transition():
    W, H = 1180, 520
    frags = []
    frags.append(text(W / 2, 36, "Скінченний автомат життєвого циклу елемента API: від створення до вилучення",
                      size=17, bold=True))

    nodes = [
        (60, 180, 200, 70, "1. СТАБІЛЬНИЙ (v1)", "Основний контракт,\n100% активного трафіку", BLUE_T, NEG),
        (350, 180, 220, 70, "2. РОЗШИРЕНИЙ (v1 + v2)", "Новий контракт опубліковано,\nактивні обидві версії", GREEN_T, FIELD),
        (660, 180, 220, 70, "3. ЗАСТАРІЛИЙ (DEPRECATED)", "v1 позначено застарілим,\nSunset заголовок, телеметрія", YELLOW_T, AMBER),
        (970, 180, 160, 70, "4. ВИЛУЧЕНИЙ", "v1 стерто з коду,\nтрафік v1 = 0", RED_T, POS),
    ]

    for x, y, w, h, title, desc, tint, col in nodes:
        frags.append(fitbox(x, y, w, h, f"{title}\n{desc}", size=12, bold=True, fill=tint, stroke=col, sw=1.8))

    frags.append(arrow(263, 215, 347, 215, color=LINE, sw=2.0))
    frags.append(text(305, 195, "Expand", size=11, bold=True, color=INK))

    frags.append(arrow(573, 215, 657, 215, color=LINE, sw=2.0))
    frags.append(text(615, 195, "Deprecate", size=11, bold=True, color=INK))

    frags.append(arrow(883, 215, 967, 215, color=LINE, sw=2.0))
    frags.append(text(925, 195, "Contract", size=11, bold=True, color=INK))

    frags.append(arrow(660, 265, 260, 265, color=POS, sw=1.8))
    frags.append(text(460, 285, "Аварійний відкат: виявлено регресію у v2 → повернення трафіку на v1",
                      size=11, bold=True, color=POS))

    frags.append(fitbox(60, 335, 1070, 145,
                        "Критерії та захисні гейти для переходів між станами:\n\n"
                        "• Перехід 1 → 2 (Expand): додавання нових полів/методів як необов'язкових (non-breaking, мінорний реліз SemVer).\n"
                        "• Перехід 2 → 3 (Deprecate): публікація дат застарівання, заголовків Sunset/Deprecation та початок аудиту клієнтів.\n"
                        "• Перехід 3 → 4 (Contract): дозволений ТІЛЬКИ тоді, коли показник metrics_legacy_calls_total == 0 за повний бізнес-цикл.\n"
                        "• Зворотність: доки система перебуває у стані 2 або 3, будь-який збій утилізує v1 як безпечну подушку відкату.",
                        size=12, fill=GREY_T, stroke=LINE, sw=1.5))

    render(os.path.join(IMG, 'state-machine-transition.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_expand_contract_phases()
    fig_dual_write_dual_read()
    fig_state_machine_transition()
    print("Expand-contract figures generated successfully.")
