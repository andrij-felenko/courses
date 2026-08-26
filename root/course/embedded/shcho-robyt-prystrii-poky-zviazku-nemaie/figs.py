# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Локальні палітри під єдиний стиль svgkit
AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── 1. degradation-ladder: трифазна градація автономної деградації ────────────
def fig_degradation_ladder():
    W, H = 860, 460
    p = []
    p.append(text(W / 2, 34, "трифазна градація автономної поведінки при втраті зв'язку", size=15, color=INK, bold=True))

    # Стовпці рівнів деградації
    bw, bh, by = 190, 240, 70
    xs = [25, 230, 435, 640]
    phases = [
        (GREENBG, FIELD, "0. НОРМА", "канал стабільний",
         "• пряме керування\n• живий потік телеметрії\n• віддалені уставки\n• актуальні дедлайни\n\nстан: ONLINE"),
        (BLUEBG, NEG, "ФАЗА 1 (< 5 с)", "короткий збій",
         "• утримання уставки\n• ігнорування дропів\n• кешовані ліміти\n• фільтрація шуму\n\nстан: CACHE_HOLD"),
        (AMBERBG, AMBER, "ФАЗА 2 (5–60 с)", "тривалий обрив",
         "• локальний регулятор\n• повернення / дрейф\n• автономна модель\n• проріджування логів\n\nстан: AUTONOMOUS"),
        (REDBG, POS, "ФАЗА 3 (> 60 с)", "критичний таймаут",
         "• повне знеструмлення\n• зупинка моторів\n• закриття клапанів\n• аварійний маяк\n\nстан: SAFE_STATE"),
    ]

    for x, (fill, col, head, sub, body) in zip(xs, phases):
        tagcol = AMBERTX if col == AMBER else col
        p.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=2, rx=8))
        p.append(text(x + bw / 2, by + 24, head, size=12.5, color=tagcol, bold=True))
        p.append(text(x + bw / 2, by + 42, sub, size=9.8, color=MUTED, italic=True))
        lines = body.split("\n")
        cur_y = by + 68
        for ln in lines:
            if ln.startswith("стан:"):
                p.append(rect(x + 12, cur_y - 12, bw - 24, 26, fill=BG, stroke=col, sw=1.2, rx=4))
                p.append(text(x + bw / 2, cur_y + 5, ln, size=10, color=tagcol, bold=True))
            elif ln:
                p.append(text(x + 16, cur_y, ln, size=9.8, color=INK, anchor="start"))
                cur_y += 18
            else:
                cur_y += 10

    # Стрілки переходу між фазами
    for i in range(3):
        p.append(arrow(xs[i] + bw + 2, by + bh / 2, xs[i + 1] - 4, by + bh / 2, color=LINE, sw=2.0))

    # Нижня шкала небезпеки та автономності
    p.append(rect(25, 330, 805, 100, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(W / 2, 354, "динаміка безпеки: як зростає ціна помилки з часом мовчання ефіру", size=11.5, color=INK, bold=True))

    p.append(line(50, 385, 805, 385, color=MUTED, sw=1.8))
    p.append(circle(50, 385, 4, fill=FIELD, stroke=FIELD))
    p.append(circle(255, 385, 4, fill=NEG, stroke=NEG))
    p.append(circle(460, 385, 4, fill=AMBER, stroke=AMBER))
    p.append(circle(665, 385, 4, fill=POS, stroke=POS))

    p.append(text(50, 410, "0 с (старт)", size=9.6, color=FIELD, bold=True))
    p.append(text(255, 410, "t = 5 с (межа кешу)", size=9.6, color=NEG, bold=True))
    p.append(text(460, 410, "t = 60 с (межа евристики)", size=9.6, color=AMBERTX, bold=True))
    p.append(text(665, 410, "t > 60 с (аварійний стоп)", size=9.6, color=POS, bold=True))

    render(os.path.join(OUT, "degradation-ladder.svg"), W, H, *p,
           title="Трифазна градація автономної деградації")


# ── 2. deadman-architecture: архітектура таймера мертвої руки ─────────────────
def fig_deadman_architecture():
    W, H = 860, 420
    p = []
    p.append(text(W / 2, 34, "апаратний і програмний захист: таймер мертвої руки (Dead-Man)", size=15, color=INK, bold=True))

    # Лівий блок: Джерело команд і зв'язок
    p.append(rect(30, 75, 180, 200, fill=BLUEBG, stroke=NEG, sw=1.8, rx=8))
    p.append(text(120, 102, "РАДІО / КАНАЛ", size=12, color=NEG, bold=True))
    p.append(text(120, 122, "пакети керування", size=9.8, color=MUTED, italic=True))
    p.append(text(120, 155, "кожні 50 мс:\n• валідна уставка\n• номер кадру\n• підпис / CRC", size=9.8, color=INK))
    p.append(rect(45, 220, 150, 36, fill=BG, stroke=NEG, sw=1.2, rx=4))
    p.append(text(120, 242, "Heartbeat / Ping", size=10.2, color=NEG, bold=True))

    # Центральний блок: МК з двома таймерами
    p.append(rect(260, 60, 310, 230, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    p.append(text(415, 86, "МІКРОКОНТРОЛЕР", size=13, color=INK, bold=True))

    # Софтовий Dead-Man Watchdog
    p.append(rect(280, 106, 270, 70, fill=AMBERBG, stroke=AMBER, sw=1.4, rx=6))
    p.append(text(415, 126, "Софтовий Dead-Man Timer (200 мс)", size=10.5, color=AMBERTX, bold=True))
    p.append(text(415, 144, "скидається кожним ВАЛІДНИМ пакетом;", size=9.6, color=INK))
    p.append(text(415, 160, "при таймауті: обнуляє ШІМ у регістрах", size=9.6, color=AMBERTX, bold=True))

    # Апаратний захист / таймер блокування
    p.append(rect(280, 190, 270, 80, fill=BG, stroke=POS, sw=1.4, rx=6))
    p.append(text(415, 210, "Апаратний Interlock / Monostable", size=10.5, color=POS, bold=True))
    p.append(text(415, 228, "таймер вимагає пульсації (toggle pin);", size=9.6, color=INK))
    p.append(text(415, 246, "якщо CPU завис у HIGH чи LOW —", size=9.6, color=INK))
    p.append(text(415, 260, "апаратна лінія ENABLE падає в 0", size=9.6, color=POS, bold=True))

    # Правий блок: Силовий каскад і навантаження
    p.append(rect(620, 75, 210, 200, fill=REDBG, stroke=POS, sw=1.8, rx=8))
    p.append(text(725, 102, "СИЛОВИЙ ДРАЙВЕР", size=12, color=POS, bold=True))
    p.append(text(725, 122, "мотори, нагрівачі, клапани", size=9.8, color=MUTED, italic=True))

    p.append(rect(635, 140, 180, 42, fill=BG, stroke=POS, sw=1.2, rx=4))
    p.append(text(725, 158, "Вхід ENABLE (Gate Kill)", size=10.2, color=POS, bold=True))
    p.append(text(725, 172, "0 = апаратний стоп", size=9.5, color=MUTED))

    p.append(rect(635, 196, 180, 42, fill=BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(725, 214, "Вхід PWM / Power", size=10.2, color=INK, bold=True))
    p.append(text(725, 228, "керування шпаруватістю", size=9.5, color=MUTED))

    # Зв'язки лініями
    p.append(arrow(210, 140, 280, 140, color=NEG, sw=2.0))
    p.append(arrow(550, 140, 635, 217, color=AMBER, sw=2.0))
    p.append(arrow(550, 230, 635, 161, color=POS, sw=2.2))

    # Пояснювальний блок унизу
    p.append(rect(30, 310, 800, 85, fill=FILL, stroke=MUTED, sw=1.4, rx=8))
    p.append(text(W / 2, 334, "чому системного WDT недостатньо для безпеки:", size=11.5, color=INK, bold=True))
    p.append(text(W / 2, 355, "1. Системний WDT стежить лише за зависанням CPU (цикл крутиться — WDT задоволений).", size=9.8, color=INK))
    p.append(text(W / 2, 375, "2. Dead-Man Timer стежить за надходженням свіжих команд (немає команд — повне знеструмлення).", size=9.8, color=POS, bold=True))

    render(os.path.join(OUT, "deadman-architecture.svg"), W, H, *p,
           title="Архітектура таймера мертвої руки (Dead-Man Watchdog)")


# ── 3. offline-storage: організація кільцевого буфера телеметрії ──────────────
def fig_offline_storage():
    W, H = 860, 430
    p = []
    p.append(text(W / 2, 34, "локальне збереження журналів: кільцевий буфер та проріджування", size=15, color=INK, bold=True))

    # Діаграма пам'яті Flash / FRAM
    p.append(rect(40, 70, 780, 115, fill=FILL, stroke=LINE, sw=1.8, rx=8))
    p.append(text(430, 92, "Кільцеве сховище у Flash / FRAM (сектори по 4 КБ)", size=12, color=INK, bold=True))

    # Сектори
    sec_w = 114
    sec_y = 108
    sec_xs = [56 + i * 126 for i in range(6)]
    labels = [
        ("Сектор 0", "передано ✓\n(вільний)", GREENBG, FIELD),
        ("Сектор 1", "передано ✓\n(вільний)", GREENBG, FIELD),
        ("Сектор 2", "Read Ptr ▶\n(черга на злив)", BLUEBG, NEG),
        ("Сектор 3", "офлайн дані\n(накопичення)", BLUEBG, NEG),
        ("Сектор 4", "Write Ptr ◀\n(запис зараз)", AMBERBG, AMBER),
        ("Сектор 5", "резерв подій\n(Black Box)", REDBG, POS),
    ]

    for sx, (sname, stxt, sfill, scol) in zip(sec_xs, labels):
        tagcol = AMBERTX if scol == AMBER else scol
        p.append(rect(sx, sec_y, sec_w, 62, fill=sfill, stroke=scol, sw=1.6, rx=6))
        p.append(text(sx + sec_w / 2, sec_y + 19, sname, size=10.5, color=tagcol, bold=True))
        for j, l in enumerate(stxt.split("\n")):
            p.append(text(sx + sec_w / 2, sec_y + 36 + j * 14, l, size=9.5, color=INK))

    # Нижній блок: дворівнева фільтрація (Downsampling vs Black Box)
    by2 = 210
    p.append(rect(40, by2, 375, 195, fill=BLUEBG, stroke=NEG, sw=1.6, rx=8))
    p.append(text(227, by2 + 25, "1. Звичайна телеметрія (Downsampling)", size=11.5, color=NEG, bold=True))
    p.append(text(227, by2 + 48, "Поки зв'язок є: пишемо 50 Гц у буфер.", size=9.8, color=INK))
    p.append(text(227, by2 + 68, "Зв'язок зник (> 10 с): проріджуємо до 1 Гц.", size=9.8, color=INK))
    p.append(text(227, by2 + 88, "Буфер заповнено на 90%: зберігаємо", size=9.8, color=INK))
    p.append(text(227, by2 + 106, "тільки усереднені значення (Min/Max/Avg).", size=9.8, color=INK))
    p.append(rect(60, by2 + 130, 335, 48, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(227, by2 + 150, "Економія пам'яті: у 50 разів", size=10.8, color=NEG, bold=True))
    p.append(text(227, by2 + 166, "збільшує час автономного логування", size=9.5, color=MUTED))

    p.append(rect(445, by2, 375, 195, fill=REDBG, stroke=POS, sw=1.6, rx=8))
    p.append(text(632, by2 + 25, "2. Критичні події (Black Box Events)", size=11.5, color=POS, bold=True))
    p.append(text(632, by2 + 48, "Аварії, тривоги, розриви лінка, спрацювання", size=9.8, color=INK))
    p.append(text(632, by2 + 66, "захистів пишуться в НЕПЕРЕЗАПИСУВАНИЙ пул.", size=9.8, color=INK))
    p.append(text(632, by2 + 88, "• фіксований snapshot стану перед аварією", size=9.8, color=INK))
    p.append(text(632, by2 + 106, "• точний таймстемп і код помилки", size=9.8, color=INK))
    p.append(rect(465, by2 + 130, 335, 48, fill=BG, stroke=POS, sw=1.2, rx=6))
    p.append(text(632, by2 + 150, "Пріоритет №1: ніколи не затирається", size=10.8, color=POS, bold=True))
    p.append(text(632, by2 + 166, "гарантія збереження для пост-аналізу", size=9.5, color=MUTED))

    render(os.path.join(OUT, "offline-storage.svg"), W, H, *p,
           title="Організація кільцевого буфера телеметрії та захист від переповнення")


# ── 4. reconnection-flow: послідовність відновлення зв'язку ──────────────────
def fig_reconnection_flow():
    W, H = 860, 440
    p = []
    p.append(text(W / 2, 34, "порядок безпечного відновлення після появи зв'язку", size=15, color=INK, bold=True))

    steps = [
        ("КРОК 1", "Автентифікація та Handshake",
         "• перевірка актуальності сесії\n• захист від replay-атак (скидання старих команд)\n• обмін статусом «я був в офлайні N секунд»",
         BLUEBG, NEG),
        ("КРОК 2", "Підтягування часу RTC (Time Slew)",
         "• плавне усунення часового дрейфу\n• ЗАБОРОНА різкого стрибка назад (монотонність!)\n• збереження коректного порядку логів",
         AMBERBG, AMBER),
        ("КРОК 3", "Плавний перехід (Smooth Takeover)",
         "• звірка поточної фізичної позиції з новою уставкою\n• плавне наростання швидкості (Ramp-up)\n• виключення ударних механічних ривків",
         GREENBG, FIELD),
        ("КРОК 4", "Фоновий злив логів (Rate-limited)",
         "• вивантаження збереженого Flash-буфера\n• низький пріоритет (обмеження смуги 10–20%)\n• не заважає свіжому потоку керування",
         FILL, LINE),
    ]

    sy = 70
    sh = 76
    for i, (num, title, body, fill, col) in enumerate(steps):
        tagcol = AMBERTX if col == AMBER else col
        y = sy + i * (sh + 14)
        p.append(rect(40, y, 780, sh, fill=fill, stroke=col, sw=1.6, rx=8))
        p.append(rect(55, y + 14, 80, 48, fill=BG, stroke=col, sw=1.2, rx=6))
        p.append(text(95, y + 42, num, size=11, color=tagcol, bold=True))

        p.append(text(150, y + 26, title, size=12, color=tagcol, anchor="start", bold=True))
        lines = body.split("\n")
        for j, ln in enumerate(lines):
            p.append(text(150, y + 44 + j * 14, ln, size=9.6, color=INK, anchor="start"))

        if i < 3:
            p.append(arrow(430, y + sh, 430, y + sh + 12, color=col, sw=2.0))

    render(os.path.join(OUT, "reconnection-flow.svg"), W, H, *p,
           title="Послідовність безпечного повернення в режим віддаленого керування")


if __name__ == "__main__":
    fig_degradation_ladder()
    fig_deadman_architecture()
    fig_offline_storage()
    fig_reconnection_flow()
    print("Всі фігури згенеровано успішно.")
