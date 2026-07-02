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


# ════════════════════ Фігури ДЕТАЛЬНОЇ статті (von-neumann-harvard-d) ═════════

# ── bottleneck-bandwidth: спільна шина ділить одну пропускну здатність ─────────
# Ідея: у фон Неймана трафік коду й даних ділять ОДНУ смугу; сума не може її пробити.
def fig_bottleneck_bandwidth():
    W, H = 820, 340
    p = []
    # труба пропускної здатності — одна на все
    pipe_x, pipe_y, pipe_w, pipe_h = 300, 110, 360, 60
    p.append(rect(pipe_x, pipe_y, pipe_w, pipe_h, fill="#f2f4f8", stroke=INK, sw=2))
    p.append(text(pipe_x + pipe_w/2, pipe_y - 14,
                  "одна шина — одна смуга: B = ширина × частота", size=12, color=INK, bold=True))
    # дві частки трафіку в одній трубі
    p.append(rect(pipe_x + 6, pipe_y + 8, 210, pipe_h - 16, fill="#fdecea", stroke=CPU, sw=1.4))
    p.append(text(pipe_x + 111, pipe_y + pipe_h/2 + 4, "трафік коду", size=11, color=CPU, bold=True))
    p.append(rect(pipe_x + 222, pipe_y + 8, 130, pipe_h - 16, fill="#eef2fb", stroke=DATA, sw=1.4))
    p.append(text(pipe_x + 287, pipe_y + pipe_h/2 + 4, "дані", size=11, color=DATA, bold=True))
    # джерела трафіку — процесор ліворуч, пам'ять праворуч
    b, w, h = textbox(150, 140, "процесор", size=13, color=CPU, stroke=CPU,
                      fill="#fdecea", bold=True, min_w=120)
    p.append(b)
    b, w, h = textbox(730, 140, "пам'ять\nкод + дані", size=12, color=DATA, stroke=DATA,
                      fill="#eef2fb", bold=True, min_w=120)
    p.append(b)
    p.append(line(210, 140, pipe_x, 140, color=INK, sw=2.4))
    p.append(line(pipe_x + pipe_w, 140, 672, 140, color=INK, sw=2.4))
    # висновок унизу — формула-стеля
    p.append(fitbox(160, 220, 500, 34,
                    "код і дані ділять ту саму B: B_код + B_дані ≤ B",
                    size=13, color=INK, fill="#fff8e6", stroke=WARM, bold=True))
    p.append(text(W/2, 290,
                  "Хоч би який швидкий процесор — сумарний потік до пам'яті "
                  "впирається в одну смугу. Це і є вузьке місце.",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "bottleneck-bandwidth.svg"), W, H, *p,
           title="Вузьке місце: один канал ділить пропускну здатність на код і дані")


# ── pipeline-structural-hazard: конвеєр, зіткнення IF і MEM на одній шині ──────
# Ідея: на одній шині стадії «вибірка» і «пам'ять» хочуть її водночас → бульбашка.
def fig_pipeline_hazard():
    W, H = 860, 420
    p = []
    stages = ["IF", "ID", "EX", "MEM", "WB"]
    cyc_x0, cyc_w = 210, 78
    row_h = 34
    # ── верхній блок: одна шина → структурна загроза ──
    ytop = 74
    p.append(text(W/2, ytop - 12, "Одна шина (фон Нейман): вибірка (IF) і доступ до пам'яті (MEM) б'ються за неї",
                  size=12, color=DATA, bold=True))
    # шапка тактів
    ncyc = 8
    for c in range(ncyc):
        p.append(text(cyc_x0 + cyc_w*c + cyc_w/2, ytop + 12, "т%d" % (c+1),
                      size=9.5, color=MUTED, bold=True))
    # три команди зі зсувом; у такті, де накладаються IF та MEM — бульбашка
    rows_top = [
        ("I1", 0, ["IF","ID","EX","MEM","WB"]),
        ("I2", 1, ["IF","ID","EX","MEM","WB"]),
        ("I3", 2, ["IF","--","ID","EX","MEM","WB"]),  # застопорена: -- = бульбашка
    ]
    def cell(x, y, s, kind):
        if s == "--":
            return fitbox(x+2, y, cyc_w-4, row_h-6, "◦ стоп", size=9,
                          color=CPU, fill="#fff0ef", stroke=CPU, bold=True)
        col = CPU if s == "IF" else (DATA if s == "MEM" else INK)
        fil = "#fdecea" if s == "IF" else ("#eef2fb" if s == "MEM" else "#f6f7f9")
        return fitbox(x+2, y, cyc_w-4, row_h-6, s, size=10, color=col,
                      fill=fil, stroke=col if s in ("IF","MEM") else MUTED, bold=True)
    y = ytop + 22
    for name, off, seq in rows_top:
        p.append(text(cyc_x0 - 20, y + row_h/2 + 2, name, size=11, color=INK, bold=True, anchor="end"))
        for i, s in enumerate(seq):
            p.append(cell(cyc_x0 + cyc_w*(off+i), y, s, s))
        y += row_h
    # маркер конфлікту: у такті 4 I1.MEM і I3.IF хотіли б шину
    p.append(text(cyc_x0 + cyc_w*3 + cyc_w/2, y + 6, "↑ IF та MEM разом → стоп", size=9.5, color=CPU, bold=True))

    # ── нижній блок: дві шини → без загрози ──
    ybot = 250
    p.append(text(W/2, ybot - 6, "Дві шини (Гарвард): IF по шині коду, MEM по шині даних — водночас, без стопу",
                  size=12, color=CODE, bold=True))
    for c in range(ncyc):
        p.append(text(cyc_x0 + cyc_w*c + cyc_w/2, ybot + 12, "т%d" % (c+1),
                      size=9.5, color=MUTED, bold=True))
    rows_bot = [
        ("I1", 0, ["IF","ID","EX","MEM","WB"]),
        ("I2", 1, ["IF","ID","EX","MEM","WB"]),
        ("I3", 2, ["IF","ID","EX","MEM","WB"]),
    ]
    y = ybot + 22
    for name, off, seq in rows_bot:
        p.append(text(cyc_x0 - 20, y + row_h/2 + 2, name, size=11, color=INK, bold=True, anchor="end"))
        for i, s in enumerate(seq):
            p.append(cell(cyc_x0 + cyc_w*(off+i), y, s, s))
        y += row_h
    p.append(text(W/2, y + 20, "Розділивши шини, Гарвард прибирає саму причину бульбашки "
                  "в такті, де сходяться вибірка й доступ до даних.", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "pipeline-structural-hazard.svg"), W, H, *p,
           title="Структурна загроза конвеєра: одна шина спотикається, дві — ні")


# ── dsp-fir-tap: один крок FIR = три читання водночас → потрібні кілька шин ────
# Ідея: MAC за такт вимагає команду + відлік + коефіцієнт РАЗОМ — три доступи.
def fig_dsp_fir_tap():
    W, H = 840, 380
    p = []
    b, w, h = textbox(W/2, 90, "ядро DSP: один такт MAC\nacc += x[k] · h[k]",
                      size=13, color=INK, stroke=INK, fill="#f3f6ff", bold=True, min_w=280)
    p.append(b)
    # три джерела, кожне своєю шиною, усі за один такт
    srcs = [
        (150, "команда MAC", "пам'ять коду", CODE, "#eaf6ee", "шина програми"),
        (420, "відлік x[k]",  "пам'ять даних A", DATA, "#eef2fb", "шина даних 1"),
        (690, "коеф. h[k]",   "пам'ять даних B", DATA, "#eef2fb", "шина даних 2"),
    ]
    for cx, what, where, col, fil, busn in srcs:
        b, w, h = textbox(cx, 300, where, size=11.5, color=col, stroke=col,
                          fill=fil, bold=True, min_w=180)
        p.append(b)
        p.append(arrow(cx, 282, cx if cx == 420 else (cx*0.55+W/2*0.45), 116,
                       color=col, sw=2.6))
        p.append(text(cx, 250, what, size=11, color=col, bold=True))
        p.append(text(cx, 330, busn, size=9.5, color=MUTED, italic=True))
    p.append(text(W/2, 360, "Три доступи В ОДНОМУ такті: одна шина їх не вмістить, "
                  "а модифікований Гарвард із кількома шинами — так.",
                  size=11.5, color=INK, bold=True))
    render(os.path.join(OUT, "dsp-fir-tap.svg"), W, H, *p,
           title="Крок фільтра DSP: команда + відлік + коефіцієнт — усі за один такт")


# ── avr-word-vs-byte: Flash 16-біт словами, Z байтовий, LPM бере один байт ─────
# Ідея: покажчик у Гарварда дивиться в дані; читати код треба окремою командою.
def fig_avr_word_byte():
    W, H = 840, 380
    p = []
    # Flash — рядок слів, кожне 16 біт = 2 байти
    p.append(text(W/2, 70, "Flash програми — слова по 16 біт; кожне слово = два байти",
                  size=12.5, color=INK, bold=True))
    wx0, wy, ww = 120, 96, 150
    words = [("слово 0", "b0 | b1"), ("слово 1", "b2 | b3"), ("слово 2", "b4 | b5")]
    for i, (wl, bl) in enumerate(words):
        x = wx0 + i*(ww+20)
        p.append(rect(x, wy, ww, 56, fill="#eaf6ee", stroke=CODE, sw=1.6))
        p.append(text(x + ww/2, wy + 22, wl, size=11, color=CODE, bold=True))
        p.append(line(x + ww/2, wy + 30, x + ww/2, wy + 56, color=MUTED, sw=1))
        p.append(text(x + ww/4, wy + 47, "байт %d" % (2*i), size=9, color=MUTED))
        p.append(text(x + 3*ww/4, wy + 47, "байт %d" % (2*i+1), size=9, color=MUTED))

    # Z-покажчик — байтовий; молодший біт вибирає половину слова
    b, w, h = textbox(160, 220, "Z-покажчик\n(байтова адреса)", size=11.5, color=DATA,
                      stroke=DATA, fill="#eef2fb", bold=True, min_w=190)
    p.append(b)
    p.append(text(160, 262, "старші біти → слово · молодший біт → який байт",
                  size=9.5, color=MUTED, italic=True))
    # LPM тягне ОДИН байт із Flash у регістр
    b, w, h = textbox(560, 220, "LPM Rd, Z", size=13, color=CODE, stroke=CODE,
                      fill="#eaf6ee", bold=True, min_w=150)
    p.append(b)
    p.append(arrow(258, 214, 484, 214, color=CODE, sw=2.4))
    p.append(text(370, 200, "окрема команда в простір КОДУ", size=10, color=CODE, bold=True))
    b, w, h = textbox(560, 300, "регістр даних\n(один байт)", size=11.5, color=INK,
                      stroke=INK, fill="#f6f7f9", bold=True, min_w=150)
    p.append(b)
    p.append(arrow(560, 244, 560, 276, color=INK, sw=2.2))
    p.append(text(W/2, 356, "Звичайний покажчик читав би простір ДАНИХ за тим самим числом — "
                  "там інше. Код дістаємо лише LPM.", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "avr-word-vs-byte.svg"), W, H, *p,
           title="AVR: Flash словами, Z байтовий, LPM бере байт коду в дані")


# ── wx-permission: модиф. Гарвард на рівні дозволів — сторінка або W, або X ────
# Ідея: спільна пам'ять, але кожна сторінка АБО запис, АБО виконання, не разом.
def fig_wx_permission():
    W, H = 820, 360
    p = []
    p.append(text(W/2, 70, "Спільна пам'ять (фон Нейман), але дозволи розділені (як Гарвард)",
                  size=12.5, color=INK, bold=True))
    # смуга сторінок пам'яті
    px0, py, pw, ph = 90, 110, 640, 70
    pages = [
        ("код", "X", CODE, "#eaf6ee"),
        ("код", "X", CODE, "#eaf6ee"),
        ("дані", "W", DATA, "#eef2fb"),
        ("стек", "W", DATA, "#eef2fb"),
        ("код", "X", CODE, "#eaf6ee"),
    ]
    cw = pw / len(pages)
    for i, (nm, perm, col, fil) in enumerate(pages):
        x = px0 + i*cw
        p.append(rect(x, py, cw-6, ph, fill=fil, stroke=col, sw=1.6))
        p.append(text(x + (cw-6)/2, py + 26, nm, size=11.5, color=col, bold=True))
        tag = "виконувати (X),\nне писати" if perm == "X" else "писати (W),\nне виконувати"
        p.append(mtext(x + (cw-6)/2, py + 44, tag, size=8.5, color=MUTED))
    p.append(text(W/2, py - 8, "кожна сторінка — АБО W, АБО X; ніколи обидва (W ⊕ X)",
                  size=11, color=INK, bold=True))
    # спроба атаки: виконати дані → апаратна заборона
    b, w, h = textbox(230, 250, "зловмисник кладе код\nу буфер даних", size=11, color=CPU,
                      stroke=CPU, fill="#fff0ef", bold=True, min_w=210)
    p.append(b)
    b, w, h = textbox(590, 250, "процесор відмовляє:\nсторінка не X", size=11, color=CODE,
                      stroke=CODE, fill="#eaf6ee", bold=True, min_w=210)
    p.append(b)
    p.append(arrow(340, 250, 480, 250, color=INK, sw=2.4))
    p.append(text(W/2, 320, "Одна пам'ять дає гнучкість; заборона «писати й виконувати заразом» "
                  "повертає захист роздільних просторів.", size=11, color=INK, bold=True))
    render(os.path.join(OUT, "wx-permission.svg"), W, H, *p,
           title="W ⊕ X: Гарвардський захист без Гарвардських двох пам'ятей")


# ── dsp-bus-growth: родовід TMS320 — від однієї шини даних до кількох ──────────
# Ідея (для hist-вставки): DSP заганяли модифікований Гарвард дедалі глибше —
# кількість шин пам'яті росла з покоління в покоління заради однотактного MAC.
def fig_dsp_bus_growth():
    W, H = 880, 430
    p = []
    p.append(text(W/2, 52, "Родовід TMS320: заради однотактного MAC додавали шини пам'яті",
                  size=13, color=INK, bold=True))
    # чотири віхи; для кожної — стовпчик «шин» (1 програмна + N даних)
    # (дані звірено: C54x має 1 програмну-читання + 2 даних-читання + 1 даних-запис)
    cols = [
        (150, "TMS32010", "1983", 1, 1, "1 прогр. + 1 даних"),
        (370, "TMS320C25", "1986", 1, 1, "1 прогр. + 1 даних\n(+ переносити код у дані)"),
        (590, "TMS320C5x", "1990-ті", 1, 2, "1 прогр. + 2 даних"),
        (810, "TMS320C54x", "1996", 1, 3, "1 прогр. + 2 чит. + 1 зап.\n(вісім шин з адресними)"),
    ]
    base = 320       # низ стовпчиків
    unit = 34        # висота однієї «шини»
    for cx, name, year, pbus, dbus, note in cols:
        n = pbus + dbus
        # стовпчик знизу вгору: спершу програмні (зелені), потім даних (сині)
        for i in range(n):
            col = CODE if i < pbus else DATA
            fil = "#eaf6ee" if i < pbus else "#eef2fb"
            y = base - (i + 1) * unit
            p.append(rect(cx - 52, y + 3, 104, unit - 6, fill=fil, stroke=col, sw=1.6))
            lbl = "шина коду" if i < pbus else "шина даних"
            p.append(text(cx, y + unit/2 + 4, lbl, size=9.5, color=col, bold=True))
        p.append(text(cx, base + 20, name, size=12, color=INK, bold=True))
        p.append(text(cx, base + 37, year, size=10, color=MUTED, italic=True))
        p.append(mtext(cx, base + 55, note, size=8.5, color=MUTED, lh=1.25))
        # лічильник «шин пам'яті» над стовпчиком
        p.append(text(cx, base - n*unit - 8, "%d шини пам'яті" % n if n < 5 else "%d шин" % n,
                      size=10.5, color=INK, bold=True))
    # стрілка часу під усім
    p.append(arrow(110, base + 92, W - 90, base + 92, color=MUTED, sw=1.8))
    p.append(text(W/2, base + 108, "час →  більше шин = більше даних за такт = ширший MAC-конвеєр",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "dsp-bus-growth.svg"), W, H, *p)


if __name__ == "__main__":
    fig_dsp_bus_growth()
    fig_one_vs_two_roads()
    fig_parallel_access()
    fig_tradeoff()
    fig_where_used()
    fig_modified_harvard()
    fig_esp32_buses_map()
    fig_flash_cache()
    fig_iram_attr()
    # детальна стаття
    fig_bottleneck_bandwidth()
    fig_pipeline_hazard()
    fig_dsp_fir_tap()
    fig_avr_word_byte()
    fig_wx_permission()
    print("OK: figs written to", OUT)
