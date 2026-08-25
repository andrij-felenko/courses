# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Машина Тюринга».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)

RED   = "#c0392b"   # позначка Y / голівка / гаряче
BLUE  = "#2457d6"   # позначка X / холодне
GREEN = "#27ae60"   # обчислюване / прийом
AMBER = "#b9770e"   # скінченний автомат
CTRL  = "#eef2fb"   # заливка коробки керування
HEAD  = "#fff2c4"   # підсвітка клітинки під голівкою


def cell(cx, top, s, w=44, h=46, fill=BG, stroke=INK, tcol=INK, size=17):
    """Клітинка стрічки з центром по x = cx, верхом top."""
    x = cx - w / 2
    out = rect(x, top, w, h, fill=fill, stroke=stroke, sw=1.6, rx=3)
    out += text(cx, top + h / 2 + size * 0.35, s, size=size, color=tcol, bold=True)
    return out


def head_tri(cx, cell_top, color=RED):
    """Трикутник-голівка вістрям донизу над клітинкою (верх клітинки = cell_top)."""
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (cx - 9, cell_top - 22, cx + 9, cell_top - 22, cx, cell_top - 4, color))


# ── Фігура 1: анатомія — скінченний автомат проти машини Тюринга ──────────────
# Ліворуч FA: керування + однобічний вхід, без пам'яті поза станом.
# Праворуч TM: те саме керування, але голівка над необмеженою стрічкою (читає+пише,
# рухається в обидва боки). Показуємо РІВНО те, що додає машина Тюринга.
def fig_anatomy():
    W, H = 940, 450
    P = [line(470, 44, 470, 410, color="#dfe3e8", sw=1.6, dash="7,7")]

    # ── ліворуч: скінченний автомат ──
    Lc = 190
    P.append(text(Lc, 40, "Скінченний автомат", size=15, color=INK, bold=True))
    P.append(text(Lc, 61, "пам'ять — лише поточний стан", size=11, color=MUTED))
    box, w_, h_ = textbox(Lc, 112, "керування\n(скінченні стани Q)", size=11.5,
                          fill=CTRL, stroke=NEG, color=INK)
    P.append(box)
    # стрічка входу: 5 клітинок
    cy = 214
    Lsym = ["1", "0", "1", "1", "0"]
    Lx = [80 + 44 * i for i in range(5)]           # ліві краї
    Lc_cells = [x + 22 for x in Lx]                # центри
    for cx, s in zip(Lc_cells, Lsym):
        P.append(cell(cx, cy, s))
    # голівка над 3-ю клітинкою (лише читання)
    hcx = Lc_cells[2]
    P.append(head_tri(hcx, cy, RED))
    P.append(text(hcx + 16, cy - 8, "лише читає", size=10.5, color=RED, anchor="start", bold=True))
    # рух — тільки вперед
    P.append(arrow(Lc_cells[0] - 8, cy + 78, Lc_cells[4] + 8, cy + 78))
    P.append(text(Lc, cy + 100, "тільки вперед, один прохід", size=11, color=MUTED))
    P.append(text(Lc, cy + 132, "поза станом пам'яті немає", size=12, color=INK, bold=True))

    # ── праворуч: машина Тюринга ──
    Rc = 610
    P.append(text(600, 40, "Машина Тюринга", size=15, color=INK, bold=True))
    P.append(text(600, 61, "пам'ять — необмежена стрічка", size=11, color=MUTED))
    box2, w2, h2 = textbox(Rc, 112, "те саме керування\n(скінченні стани Q)", size=11.5,
                           fill=CTRL, stroke=GREEN, color=INK)
    P.append(box2)
    # стрічка: «…» ліворуч, 4 клітинки, «…» праворуч
    Rx = [500 + 44 * i for i in range(4)]
    Rc_cells = [x + 22 for x in Rx]
    P.append(text(Rc_cells[0] - 40, cy + 30, "…", size=22, color=MUTED))
    Rsym = ["0", "0", "1", "1"]
    for cx, s in zip(Rc_cells, Rsym):
        P.append(cell(cx, cy, s, fill=HEAD if cx == Rc_cells[2] else BG,
                      stroke=RED if cx == Rc_cells[2] else INK))
    P.append(text(Rc_cells[3] + 40, cy + 30, "…", size=22, color=MUTED))
    hcx2 = Rc_cells[2]
    P.append(head_tri(hcx2, cy, RED))
    P.append(text(hcx2 + 16, cy - 8, "читає і пише", size=10.5, color=RED, anchor="start", bold=True))
    # рух — в обидва боки
    P.append(arrow(Rc - 40, cy + 78, Rc - 108, cy + 78))
    P.append(arrow(Rc + 40, cy + 78, Rc + 108, cy + 78))
    P.append(text(Rc, cy + 100, "ходить в обидва боки, переписує", size=11, color=MUTED))
    P.append(text(Rc, cy + 132, "пам'ять переїхала на стрічку", size=12, color=INK, bold=True))
    render("img/anatomy.svg", W, H, *P)


# ── Фігура 2: обчислення 0011 як «фільм» на стрічці ──────────────────────────
# Шість знімків стрічки: машина викреслює пари (0→X синім, 1→Y червоним),
# підсвічена клітинка — під голівкою. Видно, що лічильник живе на стрічці.
def fig_run():
    W, H = 780, 520
    P = [text(390, 32, "Обчислення 0011: пам'ять лягає на стрічку", size=14, color=INK, bold=True)]
    frames = [
        ("q0", "викреслити перший 0", ["0", "0", "1", "1"], 0),
        ("q1", "дійшли до 1 — ось пара", ["X", "0", "1", "1"], 2),
        ("q2", "вертаємось ліворуч до X", ["X", "0", "Y", "1"], 0),
        ("q1", "новий раунд: наступна 1", ["X", "X", "Y", "1"], 3),
        ("q0", "нулів більше немає", ["X", "X", "Y", "Y"], 2),
        ("q3", "самі Y — баланс, ПРИЙОМ", ["X", "X", "Y", "Y", "␣"], 4),
    ]

    def sym_color(s):
        return BLUE if s == "X" else RED if s == "Y" else MUTED if s == "␣" else INK

    y0, dy, ch = 66, 70, 44
    for i, (st, note, cells, hidx) in enumerate(frames):
        top = y0 + i * dy
        P.append(text(28, top + 18, st, size=14, color=INK, anchor="start", bold=True))
        P.append(text(28, top + 36, note, size=10.5, color=MUTED, anchor="start"))
        xs = [312 + 52 * j for j in range(len(cells))]   # центри клітинок
        for j, (cx, s) in enumerate(zip(xs, cells)):
            hit = (j == hidx)
            P.append(cell(cx, top, s, w=52, h=ch,
                          fill=HEAD if hit else BG,
                          stroke=RED if hit else "#c9ced4",
                          tcol=sym_color(s)))
        # маленька голівка над активною клітинкою
        P.append(head_tri(xs[hidx], top, RED))
    # легенда
    ly = y0 + 6 * dy + 12
    P.append(text(60, ly, "X — викреслений 0", size=11, color=BLUE, anchor="start", bold=True))
    P.append(text(300, ly, "Y — викреслена 1", size=11, color=RED, anchor="start", bold=True))
    P.append(text(520, ly, "жовта клітинка — голівка", size=11, color=MUTED, anchor="start"))
    render("img/machine-run.svg", W, H, *P)


# ── Фігура 3: драбина машин як вкладені множини ──────────────────────────────
# Скінченний автомат ⊂ магазинний ⊂ машина Тюринга (= усе обчислюване);
# а поза зеленим — область, куди не дістає жодна машина (проблема зупинки).
def fig_ladder():
    W, H = 840, 540
    P = []
    # зовнішня коробка — усі задачі
    P.append(rect(40, 55, 760, 450, fill="#f6f7f9", stroke=MUTED, sw=1.6, rx=12))
    P.append(text(58, 80, "Простір усіх задач", size=12, color=MUTED, anchor="start"))
    # верхнє кільце — необчислюване
    P.append(circle(250, 98, 6, fill=RED, stroke=RED, sw=1))
    P.append(text(420, 96, "НЕобчислюване — не бере жодна машина", size=12.5, color=RED, bold=True))
    P.append(text(420, 116, "напр. проблема зупинки", size=11, color=RED))
    # машина Тюринга — усе обчислюване (зелене)
    P.append(rect(80, 145, 680, 350, fill="#eafaf0", stroke=GREEN, sw=2, rx=11))
    P.append(text(112, 172, "Машина Тюринга — усе обчислюване", size=13.5, color=GREEN, anchor="start", bold=True))
    P.append(text(112, 191, "пам'ять: необмежена стрічка з довільним доступом", size=10.5, color=MUTED, anchor="start"))
    # магазинний автомат
    P.append(rect(140, 212, 560, 226, fill="#eef4ff", stroke=NEG, sw=1.8, rx=10))
    P.append(text(170, 238, "Магазинний автомат", size=12.5, color=NEG, anchor="start", bold=True))
    P.append(text(170, 257, "пам'ять: стек · напр. 0ⁿ1ⁿ, дужки, синтаксис", size=10.5, color=MUTED, anchor="start"))
    # скінченний автомат
    P.append(rect(200, 285, 440, 116, fill="#fdf3e3", stroke=AMBER, sw=1.8, rx=9))
    P.append(text(230, 313, "Скінченний автомат", size=12.5, color=AMBER, anchor="start", bold=True))
    P.append(text(230, 333, "пам'ять: лише стан · напр. розпізнає 101", size=10.5, color=MUTED, anchor="start"))
    P.append(text(230, 353, "не вміє порахувати 0ⁿ1ⁿ", size=10.5, color=AMBER, anchor="start"))
    # підпис у зеленому кільці (поза магазинним)
    P.append(text(420, 470, "усе, що взагалі можна обчислити, — усередині зеленого", size=11, color=GREEN))
    render("img/ladder.svg", W, H, *P)


# ── Фігура 4 (вставка hist): чотири незалежні дороги до одного означення ─────
# Ербран→Гедель, Черч, Тюринг, Пост — різні мотиви, різні конструкції, один клас.
# Головна теза внизу: збіг переконує, але ПОЯСНЮЄ лише Тюринґів аналіз людини.
def fig_hist_roads():
    W, H = 1020, 600
    P = [text(510, 34, "Чотири дороги до одного означення обчислення", size=16, color=INK, bold=True)]

    # питання згори
    box, bw, bh = textbox(510, 82,
                          "«Чи є механічна процедура, що про будь-яке твердження\n"
                          "скаже, доказовне воно чи ні?» — Гільберт, 1928",
                          size=12.5, fill=FILL, stroke=INK, color=INK)
    P.append(box)

    # роздача: вертикаль → горизонтальна рейка → чотири відгалуження
    P.append(line(510, 108, 510, 150, color=MUTED, sw=1.6))
    P.append(line(145, 150, 880, 150, color=MUTED, sw=1.6))

    cols = [
        (145, AMBER, "Ербран → Гедель", "1931 · 1934",
         ["Лист Ербрана до Геделя", "(7 квітня 1931), а далі —", "лекції Геделя в Прінстоні.",
          "Мотив: врятувати доведення", "несуперечливості"],
         "загальнорекурсивні\nфункції"),
        (390, BLUE, "Алонзо Черч", "1932–1936",
         ["Числення підстановок як", "підвалина логіки; Кліні й", "Россер довели: вона",
          "суперечлива. Уцілів", "обчислювальний осередок"],
         "λ-числення"),
        (635, RED, "Алан Тюринг", "1936",
         ["Аналіз того, що робить", "ЛЮДИНА, коли рахує:", "папір у клітинку, символи,",
          "скінченні «стани розуму»,", "погляд на одну клітинку"],
         "машина зі стрічкою"),
        (880, GREEN, "Еміль Пост", "1936",
         ["Робітник ходить рядом", "коробок і ставить/стирає", "позначки за списком",
          "інструкцій. Подав це як", "гіпотезу для перевірки"],
         "«робітник у коробках»"),
    ]
    for cx, col, head, years, body, res in cols:
        P.append(arrow(cx, 150, cx, 176, color=MUTED, sw=1.6))
        P.append(rect(cx - 110, 178, 220, 222, fill=BG, stroke=col, sw=1.8, rx=9))
        P.append(text(cx - 95, 204, head, size=13, color=col, anchor="start", bold=True))
        P.append(text(cx - 95, 223, years, size=11, color=MUTED, anchor="start"))
        for i, ln in enumerate(body):
            P.append(text(cx - 95, 249 + i * 18, ln, size=11, color=INK, anchor="start"))
        P.append(line(cx - 95, 348, cx + 95, 348, color="#dfe3e8", sw=1.2))
        P.append(mtext(cx, 368, res, size=12, color=col, anchor="middle", bold=True))
        # збірка донизу
        P.append(line(cx, 402, cx, 430, color=MUTED, sw=1.6))

    P.append(line(145, 430, 880, 430, color=MUTED, sw=1.6))
    P.append(arrow(510, 430, 510, 443, color=MUTED, sw=1.6))
    box2, _, _ = textbox(510, 470,
                         "ОДИН І ТОЙ САМИЙ клас обчислюваних функцій\n"
                         "(Кліні, 1936; Тюринг, додаток від 28 серпня 1936)",
                         size=13, fill="#eafaf0", stroke=GREEN, color=INK, bold=True)
    P.append(box2)

    P.append(text(510, 528, "Збіг чотирьох доріг — сильний доказ. Але збіг не ПОЯСНЮЄ, чому це саме «механічна процедура»:",
                  size=11.5, color=MUTED))
    P.append(text(510, 550, "пояснив лише Тюрингів аналіз людини-обчислювача — тому Гедель прийняв його, а λ-числення відкинув.",
                  size=11.5, color=INK, bold=True))
    render("img/hist-roads.svg", W, H, *P)


# ── Фігура 5 (вставка hist): діагональ по обчислюваних числах ────────────────
# Список машин → їхні цифрові рядки → перевернута діагональ β. Здається,
# суперечність; насправді вона вказує на єдине слабке місце — «задовільність».
def fig_hist_diagonal():
    W, H = 900, 620
    P = [text(450, 32, "Чому стаття зветься «Про обчислювані числа»", size=15, color=INK, bold=True),
         text(450, 54, "Машина друкує нескінченний рядок цифр — цей рядок і є обчислюване число",
              size=11, color=MUTED)]

    rows = [
        ("M₁ → 0.", ["0", "1", "0", "0", "1", "1"]),
        ("M₂ → 0.", ["1", "1", "0", "1", "0", "0"]),
        ("M₃ → 0.", ["0", "0", "1", "1", "1", "0"]),
        ("M₄ → 0.", ["1", "0", "1", "0", "0", "1"]),
        ("M₅ → 0.", ["0", "1", "1", "0", "1", "1"]),
    ]
    xs = [130 + 60 * j for j in range(6)]
    y0, dy = 100, 52
    for i, (lab, digs) in enumerate(rows):
        top = y0 + i * dy
        P.append(text(95, top + 28, lab, size=12, color=INK, anchor="end", bold=True))
        for j, (cx, d) in enumerate(zip(xs, digs)):
            hit = (i == j)
            P.append(cell(cx, top, d, w=54, h=44,
                          fill=HEAD if hit else BG,
                          stroke=RED if hit else "#c9ced4",
                          tcol=RED if hit else INK))
        P.append(text(478, top + 28, "…", size=18, color=MUTED))

    # пояснення праворуч від таблиці
    notes = [
        (195, "Червоні клітинки — діагональ:", RED, True),
        (214, "n-та цифра n-го рядка.", MUTED, False),
        (248, "Кожен опис машини — скінченний", INK, False),
        (267, "текст, отже машини можна", INK, False),
        (286, "пронумерувати: список ІСНУЄ.", INK, False),
    ]
    for ny, s, col, bd in notes:
        P.append(text(512, ny, s, size=11, color=col, anchor="start", bold=bd))

    # рядок β — перевернута діагональ
    btop = 380
    P.append(text(95, btop + 28, "β  = 0.", size=12, color=BLUE, anchor="end", bold=True))
    for cx, d in zip(xs, ["1", "0", "0", "1", "0", "…"]):
        P.append(cell(cx, btop, d, w=54, h=44, fill="#eef4ff", stroke=BLUE, tcol=BLUE))
    P.append(text(512, btop + 22, "β: беремо діагональ і кожну", size=11, color=BLUE, anchor="start", bold=True))
    P.append(text(512, btop + 41, "цифру міняємо на протилежну.", size=11, color=BLUE, anchor="start"))

    box, _, _ = textbox(450, 480,
                        "β відрізняється від КОЖНОГО рядка — отже, β у списку немає.\n"
                        "Але ж β будується цілком механічно. То чому β не обчислюване?",
                        size=12, fill="#fdecea", stroke=RED, color=INK)
    P.append(box)

    box2, _, _ = textbox(450, 565,
                         "Бо щоб СКЛАСТИ список, треба вміти відсіяти описи, які зациклюються, —\n"
                         "а це нерозв'язно. Діагональ не спростовує список — вона вказує на винного.",
                         size=11.5, fill="#eafaf0", stroke=GREEN, color=INK)
    P.append(box2)
    render("img/hist-diagonal.svg", W, H, *P)


# ══ фігури до вставки proj-turing-simulator ═══════════════════════════════════
GHOST = "#fbfbfc"   # клітинка, якої ще немає в словнику


def brack(x1, x2, y, label, color=MUTED, size=11, up=False, gap=17):
    """Дужка під (або над) ділянкою + підпис із запасом, щоб не чіпати клітинки."""
    d = -7 if up else 7
    return [line(x1, y, x2, y, color=color, sw=1.4),
            line(x1, y, x1, y + d, color=color, sw=1.4),
            line(x2, y, x2, y + d, color=color, sw=1.4),
            text((x1 + x2) / 2, y - gap if up else y + gap + 4, label, size=size, color=color)]


# ── Стрічка як словник: нескінченне у скінченній пам'яті ──────────────────────
# Клітинка існує в пам'яті, лише коли в неї писали; решта стрічки — обіцянка,
# яку виконує значення за замовчуванням ␣ при читанні.
def fig_tape_dict():
    W, H = 1000, 470
    P = []
    cw, top = 58, 122
    syms = ["␣", "␣", "␣", "0", "0", "1", "1", "␣", "␣", "␣", "␣"]
    idx = list(range(-3, 8))
    real = lambda i: 3 <= i <= 6                      # ці клітинки є у словнику
    x0 = (W - cw * len(syms)) / 2
    for i, n in enumerate(idx):                       # номери клітинок — над смугою
        P.append(text(x0 + cw * i + cw / 2, top - 12, str(n), size=11,
                      color=INK if real(i) else MUTED))
    for i, s in enumerate(syms):                      # справжні клітинки й примарні
        cx = x0 + cw * i + cw / 2
        if real(i):
            P.append(cell(cx, top, s, w=cw, h=46, size=17))
        else:
            P.append('<rect x="%.1f" y="%.1f" width="%.1f" height="46" rx="3" fill="%s" '
                     'stroke="#c9ced4" stroke-width="1.3" stroke-dasharray="4,4"/>'
                     % (cx - cw / 2, top, cw, GHOST))
            P.append(text(cx, top + 30, s, size=16, color=MUTED))
    P.append(text(x0 - 28, top + 32, "…", size=22, color=MUTED))
    P.append(text(x0 + cw * len(syms) + 28, top + 32, "…", size=22, color=MUTED))
    hcx = x0 + cw * 5 + cw / 2                        # голівка над клітинкою 2
    P.append(head_tri(hcx, top, RED))
    P.append(text(hcx, top - 36, "head = 2", size=12, color=RED, bold=True))
    P.extend(brack(x0 + cw * 3, x0 + cw * 7, top + 62,
                   "ці чотири клітинки справді лежать у словнику", color=INK, size=12))
    P.extend(brack(x0, x0 + cw * 3, top + 104, "ключа немає", color=MUTED))
    P.extend(brack(x0 + cw * 7, x0 + cw * 11, top + 104, "ключа немає", color=MUTED))
    b, _w, _h = textbox(W / 2, 306, "tape = {3: '0', 4: '0', 5: '1', 6: '1'}\nhead = 2      q = 'q1'",
                        size=14, fill=CTRL, stroke=NEG, color=INK, pad=14)
    P.append(b)
    P.append(text(W / 2, 362, "tape.get(head, '␣')  —  клітинки, якої немає, ще не існує: читаємо ␣",
                  size=13, color=INK, bold=True))
    P.append(text(W / 2, 398, "Нескінченна стрічка — це обіцянка, а не масив: клітинка народжується",
                  size=12, color=MUTED))
    P.append(text(W / 2, 420, "тоді, коли в неї вперше пишуть. Пам'яті треба рівно стільки,",
                  size=12, color=MUTED))
    P.append(text(W / 2, 442, "скільки клітинок машина насправді зачепила.", size=12, color=MUTED))
    render("img/sim-data.svg", W, H,
           text(W / 2, 44, "Нескінченна стрічка у скінченній пам'яті", size=17, bold=True), *P)


# ── Стрічка універсальної машини: програма і дані поруч ───────────────────────
# Опис M (програма), стан M і робоча стрічка M — усе на одній стрічці U.
# Правило — запис сталої ширини на 7 клітинок; U звіряє перші три.
def fig_u_tape():
    W, H = 1060, 580
    P = []
    cw, top = 32, 140
    syms = ["^"] + list("q00XRq1") + list("q0YYRq3") + ["#", "q", "0", "|", "*", "0", "0", "1", "1"]
    x0 = (W - cw * (len(syms) + 2)) / 2
    cx_of = lambda i: x0 + cw * (i + (2 if i >= 15 else 0)) + cw / 2   # «…» між описом і #
    FILL_F = {0: "#eef4ff", 1: "#eef4ff", 2: "#fdecea", 3: "#eafaf0", 4: "#f2f3f5",
              5: "#eef4ff", 6: "#eef4ff"}
    STRK_F = {0: NEG, 1: NEG, 2: RED, 3: GREEN, 4: MUTED, 5: NEG, 6: NEG}
    for i, s in enumerate(syms):
        cx = cx_of(i)
        if 1 <= i <= 14:                              # дві правила-картки
            k = (i - 1) % 7
            P.append(cell(cx, top, s, w=cw, h=44, size=15, fill=FILL_F[k], stroke=STRK_F[k]))
        elif i in (15, 18):                           # межі '#' та '|'
            P.append(cell(cx, top, s, w=cw, h=44, size=15, fill="#f2f3f5", stroke=INK))
        elif i in (16, 17):                           # стан M
            P.append(cell(cx, top, s, w=cw, h=44, size=15, fill=CTRL, stroke=NEG))
        elif i == 19:                                 # позначка голівки M
            P.append(cell(cx, top, s, w=cw, h=44, size=15, fill=HEAD, stroke=RED, tcol=RED))
        else:
            P.append(cell(cx, top, s, w=cw, h=44, size=15))
    P.append(text(cx_of(14) + cw, top + 30, "…", size=22, color=MUTED))
    P.append(text(cx_of(23) + cw, top + 30, "…", size=22, color=MUTED))
    P.extend(brack(cx_of(1) - cw / 2, cx_of(14) + cw * 1.6, top - 14,
                   "опис M — програма, по 7 клітинок на правило", color=NEG, size=12, up=True))
    P.extend(brack(cx_of(16) - cw / 2, cx_of(17) + cw / 2, top - 14, "стан M", color=NEG,
                   size=12, up=True))
    P.extend(brack(cx_of(19) - cw / 2, cx_of(23) + cw / 2, top - 14,
                   "робоча стрічка M — дані", color=RED, size=12, up=True))
    P.append(text(cx_of(0), top - 20, "край", size=10, color=MUTED))
    # поля правила — у два яруси, щоб підписи не сходились
    y1, y2 = top + 58, top + 104
    P.extend(brack(cx_of(1) - cw / 2, cx_of(2) + cw / 2, y1, "стан", color=NEG, size=11))
    P.extend(brack(cx_of(4) - cw / 2, cx_of(4) + cw / 2, y1, "пише", color=GREEN, size=11))
    P.extend(brack(cx_of(6) - cw / 2, cx_of(7) + cw / 2, y1, "новий стан", color=NEG, size=11))
    P.append(line(cx_of(3), top + 24, cx_of(3), y2, color=RED, sw=1, dash="3,3"))
    P.append(line(cx_of(5), top + 24, cx_of(5), y2, color=MUTED, sw=1, dash="3,3"))
    P.extend(brack(cx_of(3) - cw / 2, cx_of(3) + cw / 2, y2, "бачить", color=RED, size=11))
    P.extend(brack(cx_of(5) - cw / 2, cx_of(5) + cw / 2, y2, "зсув", color=MUTED, size=11))
    # цикл U: питання ← зі стрічки, відповідь → у правило
    qcx, qcy = W / 2 + 196, 322
    qb, qw, qh = textbox(qcx, qcy, "хто я і що бачу:  (q0, 0)", size=13,
                         fill=HEAD, stroke=RED, color=INK, pad=11)
    P.append(qb)
    P.append(arrow(cx_of(17), top + 48, qcx - 20, qcy - qh / 2 - 6, color=NEG))
    P.append(arrow(cx_of(20), top + 48, qcx + 40, qcy - qh / 2 - 6, color=RED))
    P.append(arrow(qcx - qw / 2 - 8, qcy, cx_of(2) + 16, y1 + 40, color=INK))
    P.append(text(W / 2 - 96, qcy - 12, "збіг у перших трьох клітинках", size=12, color=INK, bold=True))
    P.append(text(W / 2 - 96, qcy + 10, "правила — і U знає, що робити", size=12, color=MUTED))
    P.append(text(W / 2, 416, "U не знає про M нічого: усе, що вона робить, — читає клітинки.",
                  size=13.5, color=INK, bold=True))
    P.append(text(W / 2, 450, "Опис ліворуч від «#» — це програма. Стрічка праворуч від «|» — це дані.",
                  size=12, color=MUTED))
    P.append(text(W / 2, 472, "Обоє — просто символи в клітинках, і U ходить від одних до других.",
                  size=12, color=MUTED))
    P.append(text(W / 2, 514, "Змініть символи ліворуч від «#» — і та сама U стане іншою машиною.",
                  size=13, color=GREEN, bold=True))
    render("img/u-tape.svg", W, H,
           text(W / 2, 44, "Стрічка універсальної машини: програма і дані поруч", size=17, bold=True),
           *P)


# ── Коли даним тісно: програма посувається ───────────────────────────────────
# M просить крок ліворуч, а там межа опису. U посуває ВЕСЬ опис на клітинку
# ліворуч і віддає M звільнену клітинку — порожню, як і належить стрічці.
def fig_u_shift():
    W, H = 1000, 480
    P = []
    cw = 34
    tail = list("qa#c0|")                 # хвіст опису, межа, стан M, межа
    workx = 300 + cw * len(tail)          # робоча зона — на місці й не рухається

    def rowdraw(top, dx, mark_new=False):
        out = []
        x0 = 300 + dx
        for i, s in enumerate(tail):
            cx = x0 + cw * i + cw / 2
            out.append(cell(cx, top, s, w=cw, h=44, size=15,
                            fill=CTRL if i in (3, 4) else "#f2f3f5",
                            stroke=INK if s in "#|" else "#c9ced4"))
        bar_cx = x0 + cw * (len(tail) - 1) + cw / 2
        if mark_new:                      # звільнена клітинка — нова, порожня
            out.append(cell(workx + cw / 2, top, "␣", w=cw, h=44, size=15,
                            fill="#eafaf0", stroke=GREEN, tcol=GREEN))
        for i, s in enumerate("*00"):
            # після зсуву позначка «*» переїжджає у звільнену клітинку — ЛІВОРУЧ
            # від нової порожньої; самі дані «00» лишаються на місці.
            off = (-1 if i == 0 else i) if mark_new else i
            cx = workx + cw * off + cw / 2
            out.append(cell(cx, top, s, w=cw, h=44, size=15,
                            fill=HEAD if s == "*" else BG,
                            stroke=RED if s == "*" else "#c9ced4",
                            tcol=RED if s == "*" else INK))
        out.append(text(x0 - 26, top + 30, "…", size=22, color=MUTED))
        return out, bar_cx

    top1 = 128
    f1, bar1 = rowdraw(top1, 0)
    P.extend(f1)
    P.append(text(150, top1 + 30, "було", size=14, color=INK, bold=True))
    P.append(arrow(workx + 20, top1 - 18, bar1 + 6, top1 - 18, color=RED))
    P.append(text(workx + 178, top1 - 44, "M просить крок ліворуч —", size=12.5, color=RED, bold=True))
    P.append(text(workx + 178, top1 - 24, "а там межа «|», далі чужа земля: опис", size=11.5, color=RED))
    P.append(text(560, top1 + 78, "ще крок — і M затерла б власну програму", size=12, color=RED))

    top2 = 292
    f2, bar2 = rowdraw(top2, -cw, mark_new=True)
    P.extend(f2)
    P.append(text(150, top2 + 30, "стало", size=14, color=INK, bold=True))
    P.append(arrow(bar1, top1 + 50, bar2, top2 - 12, color=NEG))
    P.append(text(300, top2 - 40, "увесь опис поїхав на клітинку ліворуч", size=12, color=NEG, bold=True))
    P.append(text(workx + cw / 2, top2 + 78, "звільнена клітинка", size=11, color=GREEN, bold=True))
    P.append(text(workx + cw / 2, top2 + 96, "порожня — і вона тепер", size=11, color=GREEN))
    P.append(text(workx + cw / 2, top2 + 114, "клітинка стрічки M", size=11, color=GREEN))

    P.append(text(W / 2, 420, "Одна стрічка на двох: коли даним тісно — посувають програму.",
                  size=13.5, color=INK, bold=True))
    P.append(text(W / 2, 448, "Ціна — пробігти весь опис. Тому справжні машини тримають програму "
                              "й дані за адресами, а не пліч-о-пліч.", size=11.5, color=MUTED))
    render("img/u-shift.svg", W, H,
           text(W / 2, 44, "Коли даним тісно: програма посувається", size=17, bold=True), *P)


if __name__ == "__main__":
    fig_anatomy()
    fig_run()
    fig_ladder()
    fig_hist_roads()
    fig_hist_diagonal()
    fig_tape_dict()
    fig_u_tape()
    fig_u_shift()
    print("OK: anatomy.svg, machine-run.svg, ladder.svg, hist-roads.svg, hist-diagonal.svg, "
          "sim-data.svg, u-tape.svg, u-shift.svg")
