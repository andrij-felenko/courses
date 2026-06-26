# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE = FIELD   # зелений — шлях/пам'ять коду
DATA = NEG     # синій  — шлях/пам'ять даних
CPU  = POS     # червоний — процесор
WARM = "#caa24a"  # бурштин — Flash/повільне


# ── one-vs-two-roads: фон Нейман (одна шина) поруч із Гарвардом (дві шини) ─────
# Ідея: уся різниця між архітектурами — кількість доріг між процесором і пам'яттю.
def fig_one_vs_two_roads():
    W, H = 760, 300
    p = []
    p.append(line(W/2, 70, W/2, 250, color="#dcdcdc", sw=1.4, dash="5 5"))

    # ── ліворуч: фон Нейман ──
    p.append(text(190, 64, "Фон Нейман", size=15, color=DATA, bold=True))
    p.append(text(190, 84, "одна пам'ять, одна шина на все", size=11, color=MUTED, italic=True))
    b, w, h = textbox(120, 160, "ПАМ'ЯТЬ\nкод + дані", size=12, color=DATA,
                      stroke=DATA, fill="#eef2fb", bold=True, min_w=130)
    p.append(b)
    b, w, h = textbox(290, 160, "процесор", size=12, color=CPU, stroke=CPU,
                      fill="#fdecea", bold=True, min_w=92)
    p.append(b)
    p.append(line(187, 160, 244, 160, color=INK, sw=3))
    p.append(text(215, 150, "одна шина", size=10, color=INK, bold=True))
    p.append(text(190, 210, "просто й гнучко —", size=10.5, color=DATA, bold=True))
    p.append(text(190, 226, "та шина одна (вузьке місце)", size=10.5, color=DATA, bold=True))

    # ── праворуч: Гарвард ──
    p.append(text(570, 64, "Гарвард", size=15, color=CODE, bold=True))
    p.append(text(570, 84, "окремі пам'яті й шини для коду й даних", size=11, color=MUTED, italic=True))
    b, w, h = textbox(500, 128, "пам'ять коду", size=11.5, color=CODE, stroke=CODE,
                      fill="#eaf6ee", bold=True, min_w=132)
    p.append(b)
    b, w, h = textbox(500, 192, "пам'ять даних", size=11.5, color=DATA, stroke=DATA,
                      fill="#eef2fb", bold=True, min_w=132)
    p.append(b)
    b, w, h = textbox(660, 160, "процесор", size=12, color=CPU, stroke=CPU,
                      fill="#fdecea", bold=True, min_w=92)
    p.append(b)
    p.append(line(566, 132, 626, 152, color=CODE, sw=2.6))
    p.append(line(566, 188, 626, 168, color=DATA, sw=2.6))
    p.append(text(596, 122, "шина коду", size=9, color=CODE, bold=True))
    p.append(text(596, 206, "шина даних", size=9, color=DATA, bold=True))
    p.append(text(570, 232, "дві шини — код і дані водночас", size=10.5, color=CODE, bold=True))

    render(os.path.join(OUT, "one-vs-two-roads.svg"), W, H, *p,
           title="Уся різниця — кількість доріг між процесором і пам'яттю")


# ── parallel-access: одна шина = по черзі; дві шини = за один такт ─────────────
# Ідея: друга шина прибирає конкуренцію вибірки команди й доступу до даних.
def fig_parallel_access():
    W, H = 760, 300
    p = []
    # фон Нейман: по черзі
    p.append(rect(40, 70, 330, 180, fill="#f7f9fc", stroke=DATA, sw=1.6))
    p.append(text(205, 96, "Фон Нейман: по черзі", size=13, color=DATA, bold=True))
    p.append(text(205, 116, "одна шина → дві потреби конфліктують", size=10, color=MUTED))
    p.append(fitbox(80, 134, 250, 32, "такт 1: вибрати команду", size=10.5,
                    color=CPU, stroke=CPU, fill="#fdecea", bold=True))
    p.append(fitbox(80, 176, 250, 32, "такт 2: читати дані", size=10.5,
                    color=DATA, stroke=DATA, fill="#eef2fb", bold=True))
    p.append(text(205, 232, "доступ до даних чекає на вибірку", size=10, color=CPU, bold=True))

    # Гарвард: водночас
    p.append(rect(390, 70, 330, 180, fill="#eef7f1", stroke=CODE, sw=1.6))
    p.append(text(555, 96, "Гарвард: водночас", size=13, color=CODE, bold=True))
    p.append(text(555, 116, "дві шини → обидві потреби разом", size=10, color=MUTED))
    p.append(fitbox(410, 150, 140, 32, "вибрати команду", size=10,
                    color=CPU, stroke=CPU, fill="#fdecea", bold=True))
    p.append(fitbox(560, 150, 140, 32, "читати дані", size=10,
                    color=DATA, stroke=DATA, fill="#eef2fb", bold=True))
    p.append(text(555, 206, "обидва — за один такт", size=11, color=CODE, bold=True))
    p.append(text(555, 232, "ніхто нікого не чекає", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "parallel-access.svg"), W, H, *p,
           title="Що дають дві шини: вибірку команди й доступ до даних — водночас")


# ── tradeoff: таблиця-порівняння гнучкість проти швидкості ────────────────────
# Ідея: жодна архітектура не «краща» — кожна щось виграє й щось програє.
def fig_tradeoff():
    W, H = 820, 360
    p = []
    rows = [
        ("шини до пам'яті",   "одна на все",                 "дві окремі"),
        ("швидкість доступу", "впирається у вузьке місце",   "паралельно — швидше"),
        ("гнучкість пам'яті", "код і дані ділять простір",   "роздільні простори"),
        ("«код як дані»",     "легко (вантажити програму)",  "важко (треба спецзасоби)"),
        ("складність",        "простіша",                    "складніша (всього вдвічі)"),
    ]
    x0, xv, xh = 40, 300, 580   # колонки: ознака / фон Нейман / Гарвард
    cw1, cw2 = 250, 220
    # шапка колонок
    p.append(fitbox(x0,  60, cw1, 30, "ознака", size=12, color=INK, fill="#fafafa",
                    stroke=MUTED, bold=True))
    p.append(fitbox(xv,  60, cw2, 30, "Фон Нейман", size=12, color=DATA,
                    fill="#eef2fb", stroke=DATA, bold=True))
    p.append(fitbox(xh,  60, cw2, 30, "Гарвард", size=12, color=CODE,
                    fill="#eaf6ee", stroke=CODE, bold=True))
    y = 96
    for name, vn, hv in rows:
        p.append(fitbox(x0, y, cw1, 38, name, size=11, color=INK, fill="#fafafa",
                        stroke=MUTED, bold=True))
        p.append(fitbox(xv, y, cw2, 38, vn, size=10, color=INK, fill="#f7f9fc", stroke=DATA))
        p.append(fitbox(xh, y, cw2, 38, hv, size=10, color=INK, fill="#eef7f1", stroke=CODE))
        y += 46
    p.append(text(W/2, y + 16, "Фон Нейман міняє швидкість на простоту й гнучкість; "
                  "Гарвард — навпаки.", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "tradeoff.svg"), W, H, *p,
           title="Компроміс: гнучкість проти швидкості")


# ── where-used: де яку архітектуру обирають і чому ────────────────────────────
# Ідея: вибір архітектури випливає з того, що машині важливіше.
def fig_where_used():
    W, H = 820, 320
    p = []
    p.append(rect(40, 64, 360, 200, fill="#f7f9fc", stroke=DATA, sw=1.6))
    p.append(text(220, 90, "Фон Нейман", size=14, color=DATA, bold=True))
    p.append(text(220, 110, "ПК · ноутбуки · сервери · телефони", size=10.5, color=INK, bold=True))
    for i, ln in enumerate(["треба запускати будь-які програми,",
                            "завантажені в пам'ять на льоту;",
                            "гнучкість єдиної пам'яті важливіша",
                            "за останній відсоток швидкодії."]):
        p.append(text(64, 138 + i*24, "• " + ln if i in (0, 2) else "   " + ln,
                      size=10.5, color=INK, anchor="start"))

    p.append(rect(420, 64, 360, 200, fill="#eef7f1", stroke=CODE, sw=1.6))
    p.append(text(600, 90, "Гарвард", size=14, color=CODE, bold=True))
    p.append(text(600, 110, "мікроконтролери · DSP", size=10.5, color=INK, bold=True))
    for i, ln in enumerate(["цінніші швидкість і передбачуваність;",
                            "AVR в Arduino Uno — Гарвардська:",
                            "програма у Flash, дані в SRAM — окремо;",
                            "DSP тягне дані й коефіцієнти за такт."]):
        bold = (i == 1)
        col = CODE if bold else INK
        p.append(text(444, 138 + i*24, "• " + ln if i in (0, 1, 3) else "   " + ln,
                      size=10.5, color=col, anchor="start", bold=bold))

    p.append(text(W/2, 294, "Різні цілі — різний вибір: ПК має запускати що завгодно, "
                  "МК зазвичай виконує одну прошиту програму.", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "where-used.svg"), W, H, *p,
           title="Де яку вживають: ПК — фон Нейман, мікроконтролери — часто Гарвард")


# ── modified-harvard: спектр — роздільні шляхи вгорі, спільна пам'ять унизу ────
# Ідея: реальний чип бере швидкість Гарварда й гнучкість фон Неймана воднораз.
def fig_modified_harvard():
    W, H = 760, 360
    p = []
    b, w, h = textbox(380, 80, "процесор", size=13, color=CPU, stroke=CPU,
                      fill="#fdecea", bold=True, min_w=150)
    p.append(b)
    # дві швидкі роздільні шини (Гарвард-стиль)
    b, w, h = textbox(250, 175, "кеш коду", size=12, color=CODE, stroke=CODE,
                      fill="#eaf6ee", bold=True, min_w=170)
    p.append(b)
    b, w, h = textbox(510, 175, "кеш даних", size=12, color=DATA, stroke=DATA,
                      fill="#eef2fb", bold=True, min_w=170)
    p.append(b)
    p.append(line(345, 96, 270, 156, color=CODE, sw=2.4))
    p.append(line(415, 96, 490, 156, color=DATA, sw=2.4))
    p.append(text(120, 170, "Гарвард-стиль:", size=10.5, color=INK, anchor="start", bold=True))
    p.append(text(120, 188, "дві швидкі шини", size=9.5, color=MUTED, anchor="start"))
    # спільна головна пам'ять (фон-нейман-стиль)
    b, w, h = textbox(380, 270, "спільна головна пам'ять\n(код і дані разом)",
                      size=11.5, color="#8a6a1e", stroke=WARM, fill="#fbf3e0", bold=True, min_w=300)
    p.append(b)
    p.append(line(270, 195, 330, 246, color=INK, sw=1.8))
    p.append(line(490, 195, 430, 246, color=INK, sw=1.8))
    p.append(text(636, 264, "фон-нейман-стиль:", size=10.5, color=INK, anchor="middle", bold=True))
    p.append(text(636, 282, "одна гнучка пам'ять", size=9.5, color=MUTED, anchor="middle"))
    p.append(text(W/2, 330, "Близько до ядра — швидкість Гарварда; глибше — "
                  "гнучкість фон Неймана. ESP32 — саме такий гібрид.",
                  size=11, color=INK, bold=True))
    render(os.path.join(OUT, "modified-harvard.svg"), W, H, *p,
           title="Реальність — спектр: модифікована Гарвардська бере від обох")


# ════════════════════ Фігури вставки comp-esp32-buses ════════════════════════

# ── esp32-buses-map: карта шин і пам'ятей ESP32 ───────────────────────────────
def fig_esp32_buses_map():
    W, H = 880, 470
    p = []
    cx, cy = 440, 250
    b, w, h = textbox(cx, cy, "ядро CPU", size=15, color=INK, stroke=INK,
                      fill="#f3f6ff", bold=True, min_w=150)
    p.append(b)
    # шина команд (зелена) ліворуч-угору → IRAM; праворуч-угору → кеш → Flash
    b, w, h = textbox(150, 150, "IRAM\nкод (швидко)", size=12, color=CODE, stroke=CODE,
                      fill="#eaf6ee", bold=True, min_w=160)
    p.append(b)
    b, w, h = textbox(660, 150, "кеш + MMU", size=12, color=CODE, stroke=CODE,
                      fill="#eaf6ee", bold=True, min_w=120)
    p.append(b)
    b, w, h = textbox(800, 150, "Flash\n(зовні)", size=12, color="#8a6a1e", stroke=WARM,
                      fill="#fbf3e0", bold=True, min_w=110)
    p.append(b)
    p.append(line(370, 232, 215, 172, color=CODE, sw=3))
    p.append(line(510, 232, 615, 172, color=CODE, sw=3))
    p.append(line(728, 150, 745, 150, color=WARM, sw=3))
    p.append(text(300, 196, "шина команд", size=11, color=CODE, bold=True))
    p.append(text(737, 132, "SPI", size=10, color="#8a6a1e", bold=True))
    # шина даних (синя) ліворуч-униз → периферія; праворуч-униз → DRAM
    b, w, h = textbox(150, 360, "периферія\nрегістри GPIO/UART", size=11.5, color=DATA, stroke=DATA,
                      fill="#eef2fb", bold=True, min_w=180)
    p.append(b)
    b, w, h = textbox(700, 360, "DRAM\nдані (стек, купа)", size=12, color=DATA, stroke=DATA,
                      fill="#eef2fb", bold=True, min_w=180)
    p.append(b)
    p.append(line(370, 268, 220, 338, color=DATA, sw=3))
    p.append(line(510, 268, 620, 338, color=DATA, sw=3))
    p.append(text(560, 312, "шина даних", size=11, color=DATA, bold=True))
    p.append(text(W/2, 440, "Вибірка команди (зелена) і доступ до даних (синя) — "
                  "різними шинами, тож можуть статися за один такт.",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "esp32-buses-map.svg"), W, H, *p,
           title="Шини й пам'яті ESP32: Гарвард, видимий неозброєним оком")


# ── flash-cache: влучення віддає команду вмить, промах змушує чекати ──────────
def fig_flash_cache():
    W, H = 880, 360
    p = []
    b, w, h = textbox(110, 200, "ядро CPU\nпотрібна команда", size=12, color=INK, stroke=INK,
                      fill="#f3f6ff", bold=True, min_w=160)
    p.append(b)
    b, w, h = textbox(440, 200, "кеш + MMU\nкопії гарячого коду", size=13, color=CODE, stroke=CODE,
                      fill="#eaf6ee", bold=True, min_w=210)
    p.append(b)
    b, w, h = textbox(770, 200, "Flash\nувесь код, зовні", size=12, color="#8a6a1e", stroke=WARM,
                      fill="#fbf3e0", bold=True, min_w=170)
    p.append(b)
    # ядро ↔ кеш
    p.append(arrow(192, 192, 332, 192, color=INK, sw=2.4))
    p.append(text(262, 180, "адреса", size=11, color=INK, bold=True))
    p.append(arrow(332, 212, 192, 212, color=CODE, sw=2.6))
    p.append(text(262, 232, "влучення → вмить", size=11, color=CODE, bold=True))
    # кеш ↔ Flash
    p.append(arrow(548, 200, 686, 200, color=WARM, sw=2.6))
    p.append(text(615, 188, "промах:", size=11, color="#8a6a1e", bold=True))
    p.append(text(615, 234, "ядро чекає сотні тактів", size=11, color=CPU, bold=True))
    p.append(text(W/2, 312, "Поки код «гарячий» — летить; перший дотик до «холодного» "
                  "шматка коштує паузи на читання з Flash.", size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "flash-cache.svg"), W, H, *p,
           title="Кеш Flash: як повільна пам'ять вдає швидку шину команд")


# ── iram-attr: код у Flash зникає, коли кеш вимкнено; код в IRAM лишається ─────
def fig_iram_attr():
    W, H = 820, 400
    p = []
    p.append(line(W/2, 70, W/2, 330, color="#dcdcdc", sw=1.6, dash="4 5"))
    # ліворуч: звичайна функція з Flash
    p.append(text(210, 70, "Звичайна функція (у Flash)", size=13, color=INK, bold=True))
    b, w, h = textbox(210, 110, "loop(), обробка…", size=12, color="#8a6a1e", stroke=WARM,
                      fill="#fbf3e0", bold=True, min_w=190)
    p.append(b)
    b, w, h = textbox(210, 185, "запис у Flash →\nкеш вимкнено", size=11.5, color=CPU, stroke=CPU,
                      fill="#fff4f3", bold=True, min_w=190)
    p.append(b)
    p.append(arrow(210, 128, 210, 162, color=INK, sw=2))
    b, w, h = textbox(210, 260, "код недосяжний —\nпереривання впаде", size=12, color=CPU, stroke=CPU,
                      fill="#ffffff", bold=True, min_w=200)
    p.append(b)
    p.append(arrow(210, 208, 210, 236, color=CPU, sw=2))
    # праворуч: функція з IRAM_ATTR
    p.append(text(610, 70, "Функція з IRAM_ATTR", size=13, color=INK, bold=True))
    b, w, h = textbox(610, 110, "IRAM_ATTR isr()", size=12, color=CODE, stroke=CODE,
                      fill="#eaf6ee", bold=True, min_w=190)
    p.append(b)
    b, w, h = textbox(610, 185, "запис у Flash →\nкеш вимкнено", size=11.5, color="#8a6a1e", stroke=WARM,
                      fill="#fbf3e0", bold=True, min_w=190)
    p.append(b)
    p.append(arrow(610, 128, 610, 162, color=INK, sw=2))
    b, w, h = textbox(610, 260, "код усе одно поруч —\nпереривання спрацює", size=12, color=CODE, stroke=CODE,
                      fill="#ffffff", bold=True, min_w=220)
    p.append(b)
    p.append(arrow(610, 208, 610, 236, color=CODE, sw=2))
    p.append(text(W/2, 360, "Те, що мусить працювати завжди — обробники переривань, "
                  "код керування Flash — кладуть в IRAM (IRAM_ATTR).", size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "iram-attr.svg"), W, H, *p,
           title="Навіщо IRAM_ATTR: код, що працює, коли кеш мовчить")


if __name__ == "__main__":
    fig_one_vs_two_roads()
    fig_parallel_access()
    fig_tradeoff()
    fig_where_used()
    fig_modified_harvard()
    fig_esp32_buses_map()
    fig_flash_cache()
    fig_iram_attr()
    print("OK: figs written to", OUT)
