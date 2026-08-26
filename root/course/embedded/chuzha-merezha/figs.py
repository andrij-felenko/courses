# -*- coding: utf-8 -*-
"""Фігури до статті «Чужа мережа: що ти купуєш і що втрачаєш».
Запуск: python figs.py  → генерує SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

def _tint(c):
    m = {POS: "#fbe7e4", NEG: "#e6ecfb", FIELD: "#e4f4ea", "#b8860b": "#f6efdb",
         "#7d3c98": "#efe6f4", "#d35400": "#fbeee6"}
    return m.get(c, "#f4f6f8")

# ── 1. Пастка NAT-таймаутів та Keepalive проти сну модема ─────────────────────
def fig_nat_keepalive_trap():
    W, H = 840, 500
    f = [
        text(W / 2, 28, "Пастка операторського CGNAT: Keepalive проти батареї", 16, INK, "middle", bold=True)
    ]

    # Секція А: Частий Keepalive (батарея вмирає)
    y_a = 65
    f.append(rect(20, y_a, 800, 190, fill="#ffffff", stroke="#dcdcdc", sw=1, rx=8))
    f.append(text(35, y_a + 24, "Варіант А: Утримання NAT-сесії живими пінгами (Keepalive = 90 с)", 13, POS, "start", bold=True))
    f.append(text(35, y_a + 44, "NAT-запис не зникає, але радіотракт постійно прокидається і спустошує батарею", 11, MUTED, "start"))

    # Часова шкала А
    tx_start, tx_end = 50, 770
    t_line_y = y_a + 130
    f.append(line(tx_start, t_line_y, tx_end, t_line_y, color=MUTED, sw=1.5))
    f.append(text(tx_end - 10, t_line_y + 22, "Час (хвилини) →", 10.5, MUTED, "end"))

    # Події для А: 0с, 90с, 180с, 270с
    events_a = [
        (80, "TX: Keepalive (150 мА)", POS),
        (230, "TX: Keepalive (150 мА)", POS),
        (380, "TX: Keepalive (150 мА)", POS),
        (530, "TX: Keepalive (150 мА)", POS),
        (680, "TX: Keepalive (150 мА)", POS),
    ]

    for x_pos, lbl, col in events_a:
        # Імпульс струму
        f.append(rect(x_pos - 15, t_line_y - 45, 30, 45, fill=_tint(POS), stroke=POS, sw=1.5, rx=3))
        # RRC Inactivity tail
        f.append(rect(x_pos + 15, t_line_y - 24, 60, 24, fill="#fef5e7", stroke="#d35400", sw=1.2, rx=3))
        f.append(line(x_pos, t_line_y, x_pos, t_line_y + 12, color=col, sw=1.5))
        f.append(text(x_pos, t_line_y - 52, "Пінг", 10.5, POS, "middle", bold=True))
        f.append(text(x_pos + 45, t_line_y - 30, "Хвіст 15 с", 9.5, "#d35400", "middle"))

    f.append(text(35, y_a + 172, "Результат: 35% часу модем не спить. Батарея 2000 мАг сідає за 2-3 тижні замість 5 років.", 11, POS, "start", bold=True))

    # Секція Б: Рідкісна передача без пінгу (Тихий розрив)
    y_b = 275
    f.append(rect(20, y_b, 800, 205, fill="#ffffff", stroke="#dcdcdc", sw=1, rx=8))
    f.append(text(35, y_b + 24, "Варіант Б: Глибокий сон (PSM / eDRX) без Keepalive-пінгів", 13, FIELD, "start", bold=True))
    f.append(text(35, y_b + 44, "Батарея збережена, але операторський CGNAT стирає запис через 120 с неактивності", 11, MUTED, "start"))

    t_line_yb = y_b + 125
    f.append(line(tx_start, t_line_yb, tx_start + 720, t_line_yb, color=MUTED, sw=1.5))

    # Подія 1: Відправка телеметрії на 0 хв
    f.append(rect(65, t_line_yb - 45, 30, 45, fill=_tint(FIELD), stroke=FIELD, sw=1.5, rx=3))
    f.append(text(80, t_line_yb - 52, "Дані", 10.5, FIELD, "middle", bold=True))
    f.append(text(80, t_line_yb + 20, "0 хв", 10.5, MUTED, "middle"))

    # Зона живого NAT: 0 .. 120с
    f.append(rect(100, t_line_yb - 18, 140, 18, fill=_tint(FIELD), stroke=FIELD, sw=1, rx=2))
    f.append(text(170, t_line_yb - 5, "NAT-запис активний", 10, FIELD, "middle"))

    # Скидання NAT
    f.append(line(240, t_line_yb - 40, 240, t_line_yb + 30, color=POS, sw=2, dash="4,3"))
    f.append(text(240, t_line_yb - 46, "Таймаут NAT (120 с)", 10.5, POS, "middle", bold=True))
    f.append(text(240, t_line_yb + 20, "Запис стерто", 10, POS, "middle", bold=True))

    # Зона "Чорної діри"
    f.append(rect(242, t_line_yb - 18, 470, 18, fill=_tint(POS), stroke=POS, sw=1, rx=2))
    f.append(text(477, t_line_yb - 5, "ЧОРНА ДІРА: сокет розірвано оператором, вхідні пакети відкидаються", 10, POS, "middle"))

    # Спроба сервера відправити команду на 10-й хвилині
    f.append(line(460, t_line_yb - 65, 460, t_line_yb - 22, color=POS, sw=2))
    f.append(circle(460, t_line_yb - 22, 4, fill=POS, stroke=POS))
    f.append(text(460, t_line_yb - 72, "Сервер: Push-команда (DROP без сповіщення)", 10.5, POS, "middle", bold=True))

    f.append(text(35, y_b + 185, "Висновок: Сервер не може викликати пристрій. Архітектура мусить бути суто Device-Initiated.", 11, INK, "start", bold=True))

    render(os.path.join(IMG, "nat-keepalive-trap.svg"), W, H, *f)


# ── 2. Економіка трафіку: Округлення сесій та оверхед протоколів ───────────────
def fig_session_rounding():
    W, H = 840, 470
    f = [
        text(W / 2, 28, "Анатомія витрат трафіку: корисні байти проти білінгу", 16, INK, "middle", bold=True)
    ]

    # Стовпчик 1: Чисті корисні дані
    x1 = 120
    f.append(rect(x1 - 65, 75, 130, 330, fill="#ffffff", stroke="#dcdcdc", sw=1.5, rx=6))
    f.append(text(x1, 100, "1. Давач", 13, INK, "middle", bold=True))
    f.append(text(x1, 120, "Корисне навантаження", 10, MUTED, "middle"))

    f.append(rect(x1 - 45, 300, 90, 45, fill=_tint(FIELD), stroke=FIELD, sw=1.5, rx=4))
    f.append(text(x1, 326, "50 байтів", 11.5, FIELD, "middle", bold=True))
    f.append(text(x1, 365, "Температура, тиск,", 10, MUTED, "middle"))
    f.append(text(x1, 382, "заряд батареї", 10, MUTED, "middle"))

    # Стрілка 1 -> 2
    f.append(arrow(x1 + 75, 235, x1 + 125, 235, color=MUTED, sw=1.5))

    # Стовпчик 2: Оверхед мережевих протоколів (IP, TCP, TLS)
    x2 = 335
    f.append(rect(x2 - 85, 75, 170, 330, fill="#ffffff", stroke="#dcdcdc", sw=1.5, rx=6))
    f.append(text(x2, 100, "2. Протоколи", 13, INK, "middle", bold=True))
    f.append(text(x2, 120, "Реальний ефірний трафік", 10, MUTED, "middle"))

    # Блоки оверхеду
    f.append(rect(x2 - 70, 145, 140, 80, fill=_tint("#7d3c98"), stroke="#7d3c98", sw=1.2, rx=3))
    f.append(text(x2, 175, "TLS Handshake", 11, "#7d3c98", "middle", bold=True))
    f.append(text(x2, 198, "Сертифікати X.509 (~2.5 КБ)", 9.5, "#7d3c98", "middle"))

    f.append(rect(x2 - 70, 230, 140, 40, fill=_tint(NEG), stroke=NEG, sw=1.2, rx=3))
    f.append(text(x2, 250, "TCP 3-Way Handshake", 10.5, NEG, "middle", bold=True))
    f.append(text(x2, 264, "SYN, SYN-ACK, ACK (180 Б)", 9.5, NEG, "middle"))

    f.append(rect(x2 - 70, 275, 140, 35, fill=_tint("#d35400"), stroke="#d35400", sw=1.2, rx=3))
    f.append(text(x2, 292, "IP + TCP + TLS Headers", 10, "#d35400", "middle", bold=True))
    f.append(text(x2, 305, "Заголовки пакетів (85 Б)", 9.5, "#d35400", "middle"))

    f.append(rect(x2 - 70, 315, 140, 28, fill=_tint(FIELD), stroke=FIELD, sw=1.5, rx=3))
    f.append(text(x2, 333, "Дані: 50 байтів", 10.5, FIELD, "middle", bold=True))

    f.append(text(x2, 365, "Разом у ефірі:", 10.5, INK, "middle", bold=True))
    f.append(text(x2, 385, "≈ 2.8 КБайт", 12.5, POS, "middle", bold=True))

    # Стрілка 2 -> 3
    f.append(arrow(x2 + 95, 235, x2 + 145, 235, color=MUTED, sw=1.5))

    # Стовпчик 3: Округлення оператора (CDR Billing Rounding)
    x3 = 635
    f.append(rect(x3 - 135, 75, 270, 330, fill="#ffffff", stroke=POS, sw=1.8, rx=6))
    f.append(text(x3, 100, "3. Білінг оператора", 13, POS, "middle", bold=True))
    f.append(text(x3, 120, "Округлення PDP-сесії (Session Rounding)", 10, MUTED, "middle"))

    f.append(rect(x3 - 115, 145, 230, 205, fill=_tint(POS), stroke=POS, sw=1.5, rx=4))
    f.append(text(x3, 172, "Округлення сесії до 100 КБ", 12, POS, "middle", bold=True))
    f.append(text(x3, 196, "Якщо модем розриває PDP-контекст", 10.5, INK, "middle"))
    f.append(text(x3, 214, "після кожної передачі телеметрії,", 10.5, INK, "middle"))
    f.append(text(x3, 232, "оператор списує 100 КБ за 50 байт!", 10.5, POS, "middle", bold=True))

    f.append(line(x3 - 95, 252, x3 + 95, 252, color=POS, sw=1, dash="3,3"))
    f.append(text(x3, 272, "24 відправки/добу = 2.4 МБ/добу", 11, POS, "middle", bold=True))
    f.append(text(x3, 292, "За місяць: 72 МБ замість 2.1 МБ", 11, POS, "middle", bold=True))
    f.append(text(x3, 318, "Перевищення ліміту ×34 рази", 11, POS, "middle", bold=True))

    # Висновок унизу
    f.append(text(W / 2, 435, "Правило: Утримувати відкриту IP-сесію, використовувати TLS Session Resumption або CoAP/UDP.", 12, INK, "middle", bold=True))

    render(os.path.join(IMG, "session-rounding.svg"), W, H, *f)


# ── 3. Стан модема та джитер затримок RTT ─────────────────────────────────────
def fig_cellular_state_jitter():
    W, H = 840, 480
    f = [
        text(W / 2, 28, "Автомат станів RRC та природа гігантського джитеру RTT", 16, INK, "middle", bold=True)
    ]

    # Зліва: Граф станів RRC (Idle -> Random Access -> Connected -> Tail)
    # Блок RRC IDLE
    bx, by = 45, 85
    f.append(rect(bx, by, 220, 85, fill=_tint(FIELD), stroke=FIELD, sw=1.5, rx=6))
    f.append(text(bx + 110, by + 28, "RRC IDLE / PSM / eDRX", 12, FIELD, "middle", bold=True))
    f.append(text(bx + 110, by + 50, "Модем спить (струм < 10 мкА)", 10, MUTED, "middle"))
    f.append(text(bx + 110, by + 68, "Радіоканал відсутній", 10, MUTED, "middle"))

    # Стрілка активації
    f.append(arrow(bx + 110, by + 85, bx + 110, by + 145, color=POS, sw=1.8))
    f.append(text(bx + 118, by + 118, "Виникли дані (TX)", 10, POS, "start", bold=True))

    # Блок Random Access / PRACH
    by2 = 230
    f.append(rect(bx, by2, 220, 85, fill=_tint("#d35400"), stroke="#d35400", sw=1.5, rx=6))
    f.append(text(bx + 110, by2 + 28, "PRACH Random Access", 12, "#d35400", "middle", bold=True))
    f.append(text(bx + 110, by2 + 48, "Синхронізація з базовою станцією,", 9.5, MUTED, "middle"))
    f.append(text(bx + 110, by2 + 66, "виділення слотів (1.5 - 6 с)", 10, "#d35400", "middle", bold=True))

    # Стрілка до Connected
    f.append(arrow(bx + 110, by2 + 85, bx + 110, by2 + 135, color=FIELD, sw=1.8))

    # Блок RRC CONNECTED
    by3 = 365
    f.append(rect(bx, by3, 220, 85, fill=_tint(NEG), stroke=NEG, sw=1.5, rx=6))
    f.append(text(bx + 110, by3 + 28, "RRC CONNECTED", 12.5, NEG, "middle", bold=True))
    f.append(text(bx + 110, by3 + 50, "Передача даних (100-250 мА)", 10, MUTED, "middle"))
    f.append(text(bx + 110, by3 + 68, "RTT відгуку: 40 - 80 мс", 10.5, NEG, "middle", bold=True))

    # Стрілка повернення по таймеру неактивності
    f.append(arrow(bx + 220, by3 + 42, bx + 220, by + 42, color=MUTED, sw=1.5))
    f.append(text(bx + 228, 260, "Inactivity Timer (10-20 с)", 10, MUTED, "start"))

    # Справа: Розподіл реального RTT затримок
    rx = 345
    f.append(rect(rx, 75, 460, 385, fill="#ffffff", stroke="#dcdcdc", sw=1.5, rx=8))
    f.append(text(rx + 230, 105, "Діапазон RTT в стільникових мережах (LTE-M / NB-IoT)", 12.5, INK, "middle", bold=True))

    # Рядки затримок
    scenarios = [
        ("1. Гарячий канал (RRC Connected)", "40 – 90 мс", FIELD, "Модем уже синхронізований, дані йдуть миттєво"),
        ("2. Пробудження з eDRX (DRX = 5.12 с)", "800 – 2500 мс", "#7d3c98", "Очікування вікна пейджингу + PRACH"),
        ("3. Холодний старт із PSM / глибокого сну", "3.0 – 8.0 с", "#d35400", "Повний цикл встановлення RRC з'єднання"),
        ("4. Слабкий сигнал (HARQ / RLC повтори)", "1.5 – 5.0 с", POS, "Радіоканал втрачає блоки; прозорі ретрансмісії"),
        ("5. Перевантаження стільника (QCI 9)", "5.0 – 15+ с", POS, "IoT-трафік витісняється голосовим і відео"),
    ]

    sy = 135
    for title, val, col, desc in scenarios:
        f.append(rect(rx + 15, sy, 430, 52, fill=_tint(col), stroke=col, sw=1, rx=4))
        f.append(text(rx + 25, sy + 22, title, 11, INK, "start", bold=True))
        f.append(text(rx + 415, sy + 22, val, 11.5, col, "end", bold=True))
        f.append(text(rx + 25, sy + 40, desc, 9.5, MUTED, "start"))
        sy += 58

    f.append(text(rx + 230, 435, "Наслідок: Синхронні RPC-протоколи з короткими таймаутами непридатні!", 11, POS, "middle", bold=True))

    render(os.path.join(IMG, "cellular-state-jitter.svg"), W, H, *f)


# ── 4. Архітектура стійкості SIM: Multi-IMSI / eSIM та захист від блокувань ────
def fig_resilient_sim_architecture():
    W, H = 840, 490
    f = [
        text(W / 2, 28, "Архітектура надійності: Multi-IMSI / eUICC та авто-відновлення", 16, INK, "middle", bold=True)
    ]

    # Ліва половина: Будова eUICC / Multi-IMSI картки
    f.append(rect(20, 65, 380, 405, fill="#ffffff", stroke="#dcdcdc", sw=1.5, rx=8))
    f.append(text(210, 95, "Апаратна частина: SIM / eUICC", 13, INK, "middle", bold=True))
    f.append(text(210, 115, "Сховище незалежних профілів операторів", 10.5, MUTED, "middle"))

    # Блок Bootstrap
    f.append(rect(40, 135, 340, 75, fill=_tint("#7d3c98"), stroke="#7d3c98", sw=1.5, rx=4))
    f.append(text(55, 160, "Bootstrap Profile (Аварійний профіль)", 11.5, "#7d3c98", "start", bold=True))
    f.append(text(55, 180, "Глобальний роумінг (100+ країн). Служить лише для", 9.5, MUTED, "start"))
    f.append(text(55, 196, "відновлення зв'язку та завантаження RSP профілів", 9.5, MUTED, "start"))

    # Блок Operational 1
    f.append(rect(40, 220, 340, 70, fill=_tint(FIELD), stroke=FIELD, sw=1.5, rx=4))
    f.append(text(55, 244, "Operational Profile #1 (Основний оператор)", 11.5, FIELD, "start", bold=True))
    f.append(text(55, 263, "Локальний контракт, низький тариф, пріоритетна смуга", 9.5, MUTED, "start"))
    f.append(text(55, 278, "АКТИВНИЙ СТАН (Активний IMSI)", 10, FIELD, "start", bold=True))

    # Блок Operational 2
    f.append(rect(40, 300, 340, 70, fill=_tint(NEG), stroke=NEG, sw=1.2, rx=4))
    f.append(text(55, 324, "Operational Profile #2 (Резервний оператор)", 11.5, NEG, "start", bold=True))
    f.append(text(55, 343, "Альтернативна національна мережа", 9.5, MUTED, "start"))
    f.append(text(55, 358, "РЕЗЕРВ (Standby)", 10, MUTED, "start"))

    # Блок SIM Applet / Switcher
    f.append(rect(40, 380, 340, 75, fill=_tint("#d35400"), stroke="#d35400", sw=1.2, rx=4))
    f.append(text(55, 404, "Multi-IMSI Applet / eUICC OS (SGP.32)", 11.5, "#d35400", "start", bold=True))
    f.append(text(55, 423, "Автоматичне перемикання при втраті мережі > 3 год", 9.5, MUTED, "start"))
    f.append(text(55, 439, "або за спеціальною AT-командою мікроконтролера", 9.5, MUTED, "start"))

    # Права половина: Алгоритм виходу з пастки блокування (Permanent Reject / Cause #11/#15)
    rx = 420
    f.append(rect(rx, 65, 400, 405, fill="#ffffff", stroke="#dcdcdc", sw=1.5, rx=8))
    f.append(text(rx + 200, 95, "Алгоритм захисту від Blacklist-блокувань", 13, POS, "middle", bold=True))
    f.append(text(rx + 200, 115, "Як прошивка рятує модем від вічного офлайну", 10.5, MUTED, "middle"))

    steps = [
        ("1. Помилка реєстрації", "CREG / CEREG повертає 3 (Denied) або Cause #11/#15", POS),
        ("2. Експоненційний відступ", "Сон 1 хв → 5 хв → 30 хв (захист батареї від скану)", "#d35400"),
        ("3. Скидання чорного списку", "AT+CFUN=0 → AT+CFUN=1 (очищення кешу PLMN у модемі)", NEG),
        ("4. Примусовий вибір PLMN", "AT+COPS=1,2,... (спроба зв'язку з іншою базовою станцією)", "#7d3c98"),
        ("5. Аварійне перемикання SIM", "Команда аплету перемкнути IMSI на резервний профіль", FIELD),
    ]

    sy = 135
    for title, desc, col in steps:
        f.append(rect(rx + 15, sy, 370, 54, fill=_tint(col), stroke=col, sw=1.2, rx=4))
        f.append(text(rx + 25, sy + 22, title, 11, col, "start", bold=True))
        f.append(text(rx + 25, sy + 42, desc, 9.5, INK, "start"))
        if sy < 360:
            f.append(arrow(rx + 200, sy + 54, rx + 200, sy + 62, color=MUTED, sw=1.2))
        sy += 61

    render(os.path.join(IMG, "resilient-sim-architecture.svg"), W, H, *f)


if __name__ == "__main__":
    fig_nat_keepalive_trap()
    fig_session_rounding()
    fig_cellular_state_jitter()
    fig_resilient_sim_architecture()
    print("Всі 4 фігури успішно згенеровано у ./img/")

