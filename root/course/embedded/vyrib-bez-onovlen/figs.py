# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. ota-vs-immutable-stack: Архітектурний стек ─────────────────────────────
def fig_ota_vs_immutable_stack():
    W, H = 940, 470
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 32, "Порівняння архітектурного стеку та ресурсних витрат", size=16, color=INK, bold=True))

    # Ліва колонка: OTA-пристрій
    x1, y1, w_col, h_col = 40, 60, 410, 320
    p.append(rect(x1, y1, w_col, h_col, fill="#fdf3f2", stroke=POS, sw=1.8, rx=10))
    p.append(text(x1 + w_col / 2, y1 + 30, "Пристрій з підтримкою OTA", size=15, color=POS, bold=True))

    layers_ota = [
        ("Сховище: Dual-bank A/B Flash (2× обсяг)", "Резервний слот, мапа розділів, scratch-сектор"),
        ("Завантажувач: криптографія й відкат", "ECDSA/RSA підпис, хешування, лічильники версій"),
        ("Мережевий стек і транспорт OTA", "TLS, MQTT/HTTPS-клієнт, протокол поблочного завантаження"),
        ("Менеджер збоїв і відновлення", "Контроль живлення під час запису, watchdog оновлення"),
        ("Прикладний код виробу", "Основна функціональність із залежністю від стану OTA"),
    ]

    by = y1 + 55
    for title, desc in layers_ota:
        p.append(rect(x1 + 16, by, w_col - 32, 44, fill="#ffffff", stroke="#e0b4b0", sw=1.2, rx=6))
        p.append(text(x1 + w_col / 2, by + 18, title, size=11.5, color=INK, bold=True))
        p.append(text(x1 + w_col / 2, by + 34, desc, size=9.5, color=MUTED))
        by += 50

    # Права колонка: Незмінний моноліт
    x2 = 490
    p.append(rect(x2, y1, w_col, h_col, fill="#edf7ee", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(x2 + w_col / 2, y1 + 30, "Незмінний монолітний виріб", size=15, color=FIELD, bold=True))

    layers_imm = [
        ("Сховище: Одинарний Flash / OTP / ROM", "Мінімальний обсяг під монолітний образ"),
        ("Завантажувач: Прямий апаратний старт", "Старт із нульового вектора, відсутність гілок OTA"),
        ("Апаратний захист: eFuse / WP# / RDP Level 2", "Апаратна заборона модифікації та зневадження"),
        ("Апаратний сторож (Watchdog)", "Суворий апаратний таймер без стану оновлення"),
        ("Прикладний код виробу", "Детермінована логіка без зовнішніх мережевих хуків"),
    ]

    by = y1 + 55
    for title, desc in layers_imm:
        p.append(rect(x2 + 16, by, w_col - 32, 44, fill="#ffffff", stroke="#b9deb9", sw=1.2, rx=6))
        p.append(text(x2 + w_col / 2, by + 18, title, size=11.5, color=INK, bold=True))
        p.append(text(x2 + w_col / 2, by + 34, desc, size=9.5, color=MUTED))
        by += 50

    # Підсумкова плашка порівняння параметрів унизу
    p.append(rect(40, 395, 860, 58, fill=FILL, stroke=LINE, sw=1.4, rx=8))
    
    col_w = 860 / 4
    metrics = [
        ("Flash-пам'ять", "256–1024 КБ (OTA)", "16–64 КБ (Monolith)"),
        ("Час запуску", "100–500 мс (валідація)", "< 1 мс (прямий XIP)"),
        ("Поверхня атаки", "Велика (радіо/стек/ключі)", "Нульова (немає порту оновлення)"),
        ("Автономність", "3–5 років (радіо-вікна)", "10–15 років (Li-SOCl2)"),
    ]
    
    for i, (m_name, m_ota, m_imm) in enumerate(metrics):
        cx = 40 + col_w * i + col_w / 2
        p.append(text(cx, 414, m_name, size=11, color=INK, bold=True))
        p.append(text(cx, 430, m_ota, size=9.5, color=POS))
        p.append(text(cx, 444, m_imm, size=9.5, color=FIELD, bold=True))
        if i < 3:
            p.append(line(40 + col_w * (i + 1), 402, 40 + col_w * (i + 1), 446, color="#d0d5dd", sw=1))

    render(os.path.join(OUT, "ota-vs-immutable-stack.svg"), W, H, *p,
           title="Архітектурний стек: OTA-пристрій проти незмінного виробу")


# ── 2. attack-surface-comparison: Порівняння векторів атаки ──────────────────
def fig_attack_surface_comparison():
    W, H = 940, 440
    p = []

    p.append(text(W / 2, 30, "Вектори компрометації: динамічне оновлення проти фізичної фіксації", size=15, color=INK, bold=True))

    # Верхній блок: OTA-ланцюг уразливостей
    y_ota = 55
    p.append(rect(40, y_ota, 860, 165, fill="#fdf3f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(60, y_ota + 24, "Вектори проникнення в систему з оновленням (OTA)", size=13, color=POS, bold=True, anchor="start"))

    steps_ota = [
        ("Сервер оновлень", "Витік приватного\nключа підпису"),
        ("Канал зв'язку", "Підміна маніфесту,\nMITM, спуфінг"),
        ("Мережевий стек", "Переповнення буфера\nв парсері пакетів"),
        ("Завантажувач", "Атака відкату на\nстару версію (CVE)"),
        ("Flash-пам'ять", "Стійка модифікація\nпрошивки (руткіт)"),
    ]

    bx = 55
    bw = 148
    for i, (head, sub) in enumerate(steps_ota):
        p.append(rect(bx, y_ota + 45, bw, 95, fill="#ffffff", stroke="#e0b4b0", sw=1.2, rx=6))
        p.append(text(bx + bw / 2, y_ota + 72, head, size=11, color=POS, bold=True))
        p.append(mtext(bx + bw / 2, y_ota + 96, sub, size=9.5, color=INK, lh=1.25))
        if i < 4:
            p.append(line(bx + bw + 2, y_ota + 92, bx + bw + 20, y_ota + 92, color=POS, sw=1.8))
            p.append(text(bx + bw + 14, y_ota + 88, "→", size=14, color=POS, bold=True))
        bx += bw + 26

    # Нижній блок: Незмінна система
    y_imm = 240
    p.append(rect(40, y_imm, 860, 175, fill="#edf7ee", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(60, y_imm + 24, "Бар'єри безпеки в системі з апаратною фіксацією", size=13, color=FIELD, bold=True, anchor="start"))

    steps_imm = [
        ("Мережева поверхня", "Відсутній сервіс оновлення,\nзакриті порти"),
        ("Апаратний захист (WP#)", "Сектори Flash замкнено\nна рівні кристала"),
        ("Перепалені eFuse", "Інтерфейси SWD/JTAG\nвідключено назавжди"),
        ("Спроба атаки", "Виконання в RAM\nскидається ребутом"),
        ("Результат", "Неможливість закріплення\nчужого коду в Flash"),
    ]

    bx = 55
    for i, (head, sub) in enumerate(steps_imm):
        p.append(rect(bx, y_imm + 45, bw, 105, fill="#ffffff", stroke="#b9deb9", sw=1.2, rx=6))
        p.append(text(bx + bw / 2, y_imm + 72, head, size=11, color=FIELD, bold=True))
        p.append(mtext(bx + bw / 2, y_imm + 96, sub, size=9.5, color=INK, lh=1.25))
        if i < 4:
            p.append(line(bx + bw + 2, y_imm + 95, bx + bw + 20, y_imm + 95, color=FIELD, sw=1.8))
            p.append(text(bx + bw + 14, y_imm + 91, "→", size=14, color=FIELD, bold=True))
        bx += bw + 26

    render(os.path.join(OUT, "attack-surface-comparison.svg"), W, H, *p,
           title="Порівняння векторів атаки та точок відмови")


# ── 3. decision-matrix: Матриця рішень ────────────────────────────────────────
def fig_decision_matrix():
    W, H = 940, 480
    p = []

    p.append(text(W / 2, 30, "Матриця вибору: коли незмінність є чесною інженерною відповіддю", size=15, color=INK, bold=True))

    cards = [
        (
            "1. Незмінність — критична вимога",
            "• Системи безпеки SIL-3 / SIL-4\n• Авіоніка (DO-178C Level A)\n• Медичні імпланти (FDA Class III)\n• Оновлення анулює сертифікацію",
            "#edf7ee", FIELD, 40, 60
        ),
        (
            "2. Незмінність — оптимізація вартості",
            "• Автономні давачі (10+ років)\n• Фіксовані мости (USB-UART, BMS)\n• Одноразові логери температури\n• Мінімізація Flash, RAM і струму",
            "#eef4fa", NEG, 490, 60
        ),
        (
            "3. Локальне сервісне оновлення",
            "• Промислові контролери без мережі\n• Доступ через техніка з ноутбуком\n• Фізичний перемикач запису на платі\n• Суворий регламент техогляду",
            "#fdf8e8", "#b8860b", 40, 260
        ),
        (
            "4. Динамічне OTA обов'язкове",
            "• Споживчі IoT-шлюзи та хаби\n• Пристрої з мінливими протоколами\n• Системи зі стрічками вразливостей\n• Продукти з новими платними фічами",
            "#fdf3f2", POS, 490, 260
        ),
    ]

    bw, bh = 410, 185
    for title, content, fill, stroke, x, y in cards:
        p.append(rect(x, y, bw, bh, fill=fill, stroke=stroke, sw=1.8, rx=10))
        p.append(text(x + 20, y + 28, title, size=13.5, color=stroke, bold=True, anchor="start"))
        p.append(line(x + 20, y + 40, x + bw - 20, y + 40, color=stroke, sw=1, dash="4,3"))
        p.append(mtext(x + 24, y + 68, content, size=11, color=INK, lh=1.4, anchor="start"))

    # Центральна зв'язка або підпис унізу
    p.append(rect(40, 452, 860, 22, fill=FILL, stroke=LINE, sw=1, rx=4))
    p.append(text(W / 2, 467, "Критерій вибору: складність оточення, вимоги регуляторів, бюджет енергії та ціна помилки в полі", size=10, color=MUTED))

    render(os.path.join(OUT, "decision-matrix.svg"), W, H, *p,
           title="Матриця рішень: незмінний виріб проти оновлюваного")


# ── 4. lockdown-sequence: Послідовність апаратного замикання ──────────────────
def fig_lockdown_sequence():
    W, H = 940, 390
    p = []

    p.append(text(W / 2, 30, "Етапи остаточної апаратної фіксації виробу на заводському стенді", size=15, color=INK, bold=True))

    steps = [
        ("Етап 1: Прошивання", "Запис образу в Flash\nчерез SWD/JTAG;\nверифікація CRC32/SHA", "#ffffff", LINE),
        ("Етап 2: Калібрування", "Запис коефіцієнтів у\nвиділений OTP-сектор;\nконтрольний самотест", "#ffffff", LINE),
        ("Етап 3: Захист Flash", "Активація Write-Protect\nдля всіх секторів коду\n(Option Bytes)", "#ffffff", LINE),
        ("Етап 4: Перепалювання", "Пропалювання eFuse / RDP Level 2;\nнезворотне відключення\nінтерфейсу зневадження", "#fdf0ed", POS),
        ("Етап 5: Автономний старт", "Холодний ребут;\nперевірка роботи без\nпідключеного джига", "#edf7ee", FIELD),
    ]

    bx = 40
    bw = 158
    bh = 175
    y = 65

    for i, (st_title, st_desc, fill, stroke) in enumerate(steps):
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=stroke, sw=1.6, rx=8))
        
        # Бейдж номера етапу
        p.append(circle(bx + 24, y + 24, 12, fill=stroke, stroke=stroke, sw=1))
        p.append(text(bx + 24, y + 29, str(i + 1), size=11, color="#ffffff", bold=True))
        
        # Назва
        p.append(text(bx + bw / 2 + 8, y + 28, st_title.split(":")[1].strip(), size=11.5, color=stroke if stroke != LINE else INK, bold=True))
        p.append(line(bx + 12, y + 48, bx + bw - 12, y + 48, color="#e0e0e0", sw=1))
        
        # Опис
        p.append(mtext(bx + bw / 2, y + 80, st_desc, size=10, color=INK, lh=1.35))

        if i < 4:
            # Стрілка між кроками
            p.append(line(bx + bw + 2, y + bh / 2, bx + bw + 18, y + bh / 2, color=LINE, sw=1.8))
            p.append(text(bx + bw + 12, y + bh / 2 - 4, "→", size=15, color=LINE, bold=True))

        bx += bw + 22

    # Попереджувальна плашка внизу
    p.append(rect(40, 260, 860, 105, fill="#fff8e7", stroke="#d48800", sw=1.5, rx=8))
    p.append(text(60, 285, "⚠️ Точка неповернення: перехід у стан RDP Level 2 (eFuse)", size=13, color="#b36b00", bold=True, anchor="start"))
    p.append(mtext(60, 310, 
                   "Після перепалювання апаратних фьюзів або переведення Option Bytes у стан Level 2 кристал переходить у стан остаточного замкнення.\n"
                   "Шина зневадження SWD/JTAG фізично відключається логікою кристала. Повернення в режим розробки або повторне зчитування прошивки\n"
                   "неможливе навіть за наявності фізичного доступу до виводів мікроконтролера.",
                   size=10.5, color=INK, lh=1.35, anchor="start"))

    render(os.path.join(OUT, "lockdown-sequence.svg"), W, H, *p,
           title="Послідовність апаратного замикання виробу на заводі")


if __name__ == "__main__":
    fig_ota_vs_immutable_stack()
    fig_attack_surface_comparison()
    fig_decision_matrix()
    fig_lockdown_sequence()
    print("All figures generated successfully.")
