# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

DARK   = "#13202a"
GREENT = "#7fe0a0"
MONO   = "#eef6ef"
PAPER  = "#f6f4ec"
GOLD   = "#a98a2a"
GOLDT  = "#7a6312"


# ── eval-two-steps: як «puts [expr {$a + 2}]» стає викликом ────────────────────
def fig_eval_two_steps():
    W, H = 780, 380
    p = []

    # рядок вихідного тексту згори
    src = 'set b [expr {$a + 2}]'
    p.append(rect(40, 56, W - 80, 44, fill=DARK, stroke=INK, sw=1.6, rx=8))
    p.append(text(W / 2, 84, src, size=16, color=MONO, bold=True))
    p.append(text(W / 2, 118, "один рядок — одна команда", size=11, color=MUTED, italic=True))

    # КРОК 1 — поділ на слова + підстановки
    y1 = 150
    p.append(text(60, y1, "Крок 1 — поділ на слова, тоді підстановки [ ] і $", size=12,
                  color=FIELD, bold=True, anchor="start"))
    # три слова: set / b / [...]
    wx = 60
    labels = [("set", FILL, INK), ("b", FILL, INK), ("[expr {$a + 2}]", PAPER, GOLDT)]
    boxes_mid = []
    for txt, fill, col in labels:
        bw = text_width(txt, 14, True) + 24
        p.append(rect(wx, y1 + 14, bw, 34, fill=fill, stroke=(GOLD if fill == PAPER else LINE),
                      sw=(2.0 if fill == PAPER else 1.4), rx=6))
        p.append(text(wx + bw / 2, y1 + 36, txt, size=14, color=col, bold=True))
        boxes_mid.append((wx + bw / 2, bw))
        wx += bw + 16

    # дужкове підставлення: [...] виконується й дає "5" (при a=3)
    bx = boxes_mid[2][0]
    p.append(text(bx, y1 + 70, "виконати вкладену команду →", size=10, color=MUTED, italic=True))
    p.append(arrow(bx, y1 + 76, bx, y1 + 96, color=GOLD, sw=2.2))
    p.append(rect(bx - 34, y1 + 100, 68, 30, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=6))
    p.append(text(bx, y1 + 120, "5", size=15, color=FIELD, bold=True))
    p.append(text(bx + 60, y1 + 120, "(при a = 3)", size=10, color=MUTED, anchor="start"))

    # КРОК 2 — виклик: перше слово = ім'я команди, решта = аргументи
    y2 = 300
    p.append(text(60, y2, "Крок 2 — перше слово — ім'я команди, решта — аргументи",
                  size=12, color=FIELD, bold=True, anchor="start"))
    call = 'set  b  5'
    p.append(rect(60, y2 + 14, 250, 40, fill=DARK, stroke=INK, sw=1.6, rx=8))
    p.append(text(76, y2 + 40, "set", size=15, color="#8fd0ff", bold=True, anchor="start"))
    p.append(text(150, y2 + 40, "b", size=15, color=MONO, bold=True, anchor="start"))
    p.append(text(190, y2 + 40, "5", size=15, color=GREENT, bold=True, anchor="start"))
    p.append(text(330, y2 + 40, "→  b дістає значення «5»", size=12, color=INK,
                  bold=True, anchor="start"))
    p.append(text(76, y2 + 70, "команда", size=9, color="#8fd0ff", anchor="start"))
    p.append(text(150, y2 + 70, "два аргументи-рядки", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "eval-two-steps.svg"), W, H, *p,
           title="Дві дії Tcl над кожним рядком: підстановка, тоді виклик")


# ── eias: один рядок «1 2 3» — число? список? команда? ──────────────────────────
def fig_eias():
    W, H = 760, 340
    p = []

    # центр — сам рядок
    cx = W / 2
    p.append(rect(cx - 110, 70, 220, 56, fill=DARK, stroke=INK, sw=1.8, rx=10))
    p.append(text(cx, 94, 'рядок:', size=11, color=MUTED))
    p.append(text(cx, 116, '"1 2 3"', size=18, color=MONO, bold=True))
    p.append(text(cx, 142, "самих байтів досить — тип домальовує контекст", size=10,
                  color=MUTED, italic=True))

    # три прочитання
    y = 224
    fan_y = 160          # спільна точка розгалуження — НИЖЧЕ підпису, щоб стрілки його не чіпали
    cols = [
        ("як ЧИСЛО", "expr {\"5\"+1} → 6", "коли команда чекає число", "#eef2fb", NEG),
        ("як СПИСОК", "llength {1 2 3} → 3", "коли команда чекає список", "#eef6ef", FIELD),
        ("як КОД", 'eval "set x 5"', "коли команда чекає скрипт", PAPER, GOLDT),
    ]
    cw = 224
    gap = (W - 3 * cw) / 4
    for i, (head, ex, note, fill, col) in enumerate(cols):
        x = gap + i * (cw + gap)
        p.append(arrow(cx, fan_y, x + cw / 2, y - 6, color=MUTED, sw=1.6))
        p.append(rect(x, y, cw, 92, fill=fill, stroke=col, sw=2.0, rx=8))
        p.append(text(x + cw / 2, y + 26, head, size=13, color=col, bold=True))
        p.append(text(x + cw / 2, y + 52, ex, size=12, color=INK, bold=True))
        p.append(text(x + cw / 2, y + 76, note, size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "eias.svg"), W, H, *p,
           title="Один рядок — три прочитання: усе є рядок")


# ── tcl-obj: подвійне подання Tcl_Obj — рядок + кешований внутрішній тип ─────────
def fig_tcl_obj():
    W, H = 760, 360
    p = []

    # структура Tcl_Obj — дві половини
    ox, oy, ow, oh = 220, 70, 320, 150
    p.append(rect(ox, oy, ow, oh, fill=FILL, stroke=INK, sw=2.0, rx=10))
    p.append(text(ox + ow / 2, oy - 12, "один об'єкт-значення (Tcl_Obj)", size=12,
                  color=INK, bold=True))
    # верхня половина — рядкове подання
    p.append(rect(ox + 14, oy + 16, ow - 28, 52, fill=DARK, stroke=INK, sw=1.4, rx=6))
    p.append(text(ox + ow / 2, oy + 36, "рядкове подання", size=10, color="#8fcf9f"))
    p.append(text(ox + ow / 2, oy + 58, '"1 2 3"', size=15, color=MONO, bold=True))
    # нижня половина — внутрішнє подання (кеш)
    p.append(rect(ox + 14, oy + 80, ow - 28, 56, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(ox + ow / 2, oy + 100, "внутрішнє подання (кеш типу)", size=10, color=FIELD))
    p.append(text(ox + ow / 2, oy + 122, "список [1][2][3]", size=14, color="#256b38", bold=True))

    # зліва — «попросили як список»
    p.append(text(70, oy + 44, "перший доступ", size=11, color=MUTED, bold=True, anchor="start"))
    p.append(text(70, oy + 62, "як список:", size=11, color=INK, anchor="start"))
    p.append(text(70, oy + 80, "розібрати РАЗ,", size=10, color=MUTED, anchor="start"))
    p.append(text(70, oy + 96, "запам'ятати", size=10, color=MUTED, anchor="start"))
    p.append(arrow(190, oy + 90, ox - 4, oy + 100, color=FIELD, sw=2.0))

    # справа — «повторний доступ безкоштовний»
    p.append(text(W - 70, oy + 70, "далі — той самий", size=11, color=MUTED, bold=True, anchor="end"))
    p.append(text(W - 70, oy + 88, "тип майже безкоштовно:", size=10, color=MUTED, anchor="end"))
    p.append(text(W - 70, oy + 106, "кеш уже готовий", size=10, color=FIELD, anchor="end"))
    p.append(arrow(W - 60, oy + 116, ox + ow + 4, oy + 108, color=FIELD, sw=2.0))

    # знизу — shimmering (мерехтіння): чергування типів скидає кеш
    sy = 258
    p.append(text(W / 2, sy, "Мерехтіння (shimmering): просиш то як число, то як список —",
                  size=11, color=POS, bold=True))
    p.append(text(W / 2, sy + 20,
                  "кеш щоразу викидається й будується наново → втрата, якщо в гарячому циклі",
                  size=11, color=INK))
    p.append(rect(W / 2 - 250, sy + 34, 500, 44, fill="#fdf0ee", stroke=POS, sw=1.6, rx=8))
    p.append(text(W / 2, sy + 52, 'число → список → число → список …', size=12, color=POS, bold=True))
    p.append(text(W / 2, sy + 70, "кожна стрілка = розбір заново", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "tcl-obj.svg"), W, H, *p,
           title="Tcl_Obj: рядок назовні, кеш типу всередині")


# ── refcount: життя Tcl_Obj і лічильник посилань ────────────────────────────────
def fig_refcount():
    W, H = 820, 470
    p = []

    p.append(text(W / 2, 34, "Життя одного значення: лічильник посилань керує звільненням",
                  size=13, color=INK, bold=True))

    # три стани об'єкта в ряд, стрілки-переходи між ними
    box_w, box_h = 190, 96
    ys = 78
    xs = [40, 315, 590]
    heads = [
        ("щойно створений", "refCount = 0", "Tcl_NewIntObj(42)", MUTED, DARK),
        ("покладений у змінну", "refCount = 1", "змінна тримає посилання", FIELD, DARK),
        ("звільнений", "refCount = 0", "пам'ять повертається", POS, DARK),
    ]
    cx = []
    for x, (h1, h2, h3, col, bg) in zip(xs, heads):
        p.append(rect(x, ys, box_w, box_h, fill=bg, stroke=INK, sw=1.8, rx=9))
        p.append(text(x + box_w / 2, ys + 24, h1, size=11, color=MONO, bold=True))
        p.append(text(x + box_w / 2, ys + 50, h2, size=15, color="#8fd0ff", bold=True))
        p.append(text(x + box_w / 2, ys + 76, h3, size=9.5, color=MUTED, italic=True))
        cx.append(x + box_w / 2)

    ay = ys + box_h / 2
    p.append(arrow(xs[0] + box_w + 4, ay, xs[1] - 4, ay, color=FIELD, sw=2.2))
    p.append(text((xs[0] + box_w + xs[1]) / 2, ay - 12, "IncrRefCount", size=10, color=FIELD, bold=True))
    p.append(text((xs[0] + box_w + xs[1]) / 2, ay + 16, "0 → 1", size=10, color=MUTED))

    p.append(arrow(xs[1] + box_w + 4, ay, xs[2] - 4, ay, color=POS, sw=2.2))
    p.append(text((xs[1] + box_w + xs[2]) / 2, ay - 12, "DecrRefCount", size=10, color=POS, bold=True))
    p.append(text((xs[1] + box_w + xs[2]) / 2, ay + 16, "1 → 0", size=10, color=MUTED))

    # правило зверху коротко
    p.append(rect(40, 208, W - 80, 44, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(W / 2, 226, "Правило: 0 посилань → значення живе «нічиє» й може зникнути будь-коли.",
                  size=11.5, color="#256b38", bold=True))
    p.append(text(W / 2, 244, "Хочеш утримати вказівник — спершу підніми лічильник; відпустив — опусти.",
                  size=11, color=INK))

    # НЕБЕЗПЕКА: висіння вказівника через eval
    dy = 286
    p.append(text(40, dy, "Пастка — вказівник переживає eval без утримання:", size=12,
                  color=POS, bold=True, anchor="start"))

    # ліворуч: неправильно
    lx, lw = 40, 360
    p.append(rect(lx, dy + 14, lw, 150, fill="#fdf0ee", stroke=POS, sw=1.8, rx=8))
    p.append(text(lx + lw / 2, dy + 36, "НЕБЕЗПЕЧНО", size=11, color=POS, bold=True))
    bad = [
        "Tcl_Obj *o = objv[1];      // тримаю сирий",
        "Tcl_EvalObjEx(interp, body, 0);  // тут body",
        "                           // міг звільнити o",
        "Tcl_GetString(o);          // ← читаю мертве",
    ]
    for i, ln in enumerate(bad):
        p.append(text(lx + 14, dy + 60 + i * 24, ln, size=10.5, color="#7a1f14",
                      anchor="start", bold=(i == 3)))

    # праворуч: правильно
    rx0, rw = 430, 350
    p.append(rect(rx0, dy + 14, rw, 150, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(rx0 + rw / 2, dy + 36, "БЕЗПЕЧНО", size=11, color="#256b38", bold=True))
    good = [
        "Tcl_Obj *o = objv[1];",
        "Tcl_IncrRefCount(o);       // утримав",
        "Tcl_EvalObjEx(interp, body, 0);",
        "Tcl_GetString(o);          // живе — я тримаю",
        "Tcl_DecrRefCount(o);       // відпустив",
    ]
    for i, ln in enumerate(good):
        p.append(text(rx0 + 14, dy + 58 + i * 21, ln, size=10, color="#215c33",
                      anchor="start", bold=(i in (1, 4))))

    render(os.path.join(OUT, "refcount.svg"), W, H, *p,
           title="Лічильник посилань Tcl_Obj: 0 → 1 → 0 і пастка висіння вказівника")


# ── own-control: власна керівна конструкція repeat N {body} ─────────────────────
def fig_own_control():
    W, H = 800, 430
    p = []

    p.append(text(W / 2, 32, "Власна керівна конструкція: тіло — рядок, виконаний відкладено",
                  size=13, color=INK, bold=True))

    # виклик згори (звужений, щоб праворуч лишити місце для пояснення поза стрілкою)
    p.append(rect(250, 52, 300, 58, fill=DARK, stroke=INK, sw=1.8, rx=9))
    p.append(text(400, 74, "repeat 3 {", size=15, color=MONO, bold=True))
    p.append(text(400, 96, 'puts "крок $i" }', size=15, color=MONO, bold=True))
    # пояснення — ПРАВОРУЧ від виклику, не на осі стрілки
    p.append(text(566, 74, "число 3 і тіло-рядок —", size=10, color=MUTED, italic=True, anchor="start"))
    p.append(text(566, 90, "обидва просто аргументи", size=10, color=MUTED, italic=True, anchor="start"))

    # C-команда посередині — «не виконує тіло сама, а відкладає»
    cxb, cyb, cwb, chb = 250, 150, 300, 66
    p.append(rect(cxb, cyb, cwb, chb, fill="#eef2fb", stroke=NEG, sw=2.0, rx=8))
    p.append(text(cxb + cwb / 2, cyb + 24, "C-команда RepeatCmd", size=12, color=NEG, bold=True))
    p.append(text(cxb + cwb / 2, cyb + 46, "тіло НЕ чіпає — лише зберігає й крутить цикл",
                  size=10, color=INK))
    p.append(arrow(400, 112, 400, cyb - 2, color=NEG, sw=2.0))

    # цикл: тіло виконується N разів у кадрі викликача (uplevel 1)
    ly = 248
    # одна вертикальна стрілка вниз від C-команди до смуги-підпису
    p.append(arrow(400, cyb + chb + 2, 400, ly - 12, color=FIELD, sw=2.0))
    p.append(text(W / 2, ly, "N разів: виконати тіло-рядок у кадрі того, хто покликав (uplevel 1)",
                  size=11.5, color=FIELD, bold=True))

    step_w = 150
    xs = [80, 325, 570]
    for k, x in enumerate(xs, 1):
        # короткі стрілки СТАРТУЮТЬ ПІД підписом, тож його не перетинають
        p.append(arrow(x + step_w / 2, ly + 8, x + step_w / 2, ly + 16, color=FIELD, sw=1.6))
        p.append(rect(x, ly + 18, step_w, 74, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
        p.append(text(x + step_w / 2, ly + 40, f"оберт {k}", size=11, color="#256b38", bold=True))
        p.append(text(x + step_w / 2, ly + 62, "Tcl_EvalObjEx", size=10.5, color=INK, bold=True))
        p.append(text(x + step_w / 2, ly + 80, "(interp, body, 0)", size=9.5, color=MUTED))

    # висновок: те саме роблять вбудовані if / while
    p.append(rect(120, ly + 108, W - 240, 44, fill=PAPER, stroke=GOLD, sw=1.6, rx=8))
    p.append(text(W / 2, ly + 126, "Точнісінько так само влаштовані вбудовані if і while:", size=11,
                  color=GOLDT, bold=True))
    p.append(text(W / 2, ly + 144, "беруть тіло-рядок і самі вирішують, коли й скільки разів його виконати.",
                  size=10.5, color=INK))

    render(os.path.join(OUT, "own-control.svg"), W, H, *p,
           title="repeat N {body}: власна керівна конструкція через відкладене виконання тіла")


# ── hist-shell-lineage: труба → зворотні лапки Борна → дужки Tcl ─────────────────
def fig_hist_shell_lineage():
    W, H = 880, 476
    p = []

    LX = 44                 # ліва межа панелей
    PW = W - 2 * LX         # ширина панелі
    rows = [
        (56,  "Труба «|» — потік між двома процесами",
              "#eef2fb", NEG,
              "процес A", "процес B",
              "потік даних", "вихід A стає входом B; обидва живуть паралельно, дані течуть потоком"),
        (198, "Оболонка Борна (1979): зворотні лапки — вихід у рядок",
              "#f6f4ec", GOLDT,
              "`date`", 'echo "сьогодні …"',
              "текст у рядок", "команду виконати, її ВИХІД вставити в рядок як звичайні слова"),
        (340, "Tcl (1988): квадратні дужки — те саме, але в повній мові",
              "#eef6ef", FIELD,
              "[clock format …]", "set d …",
              "текст у рядок", "один із дванадцяти базових приписів мови, а не трюк терміналу"),
    ]

    for (ry, head, fill, col, left, right, edge, note) in rows:
        p.append(text(LX, ry, head, size=13, color=col, bold=True, anchor="start"))
        py = ry + 12
        p.append(rect(LX, py, PW, 92, fill=fill, stroke=col, sw=1.8, rx=10))

        bw = 250            # широкі коробки з великим проміжком → написи не чіпляються
        lx = LX + 42
        rxb = LX + PW - 42 - bw
        by = py + 20
        bh = 40
        p.append(rect(lx, by, bw, bh, fill=DARK, stroke=INK, sw=1.4, rx=6))
        p.append(text(lx + bw / 2, by + 26, left, size=14, color=MONO, bold=True))
        p.append(rect(rxb, by, bw, bh, fill=DARK, stroke=INK, sw=1.4, rx=6))
        p.append(text(rxb + bw / 2, by + 26, right, size=14, color=MONO, bold=True))

        # стрілка між коробками; підпис НАД лінією (не на ній)
        ax1 = lx + bw + 12
        ax2 = rxb - 12
        amid = (ax1 + ax2) / 2
        p.append(text(amid, by + 10, edge, size=11, color=col, bold=True))
        p.append(arrow(ax1, by + 26, ax2, by + 26, color=col, sw=2.2))

        # пояснення шару — окремим рядком під коробками, на всю ширину панелі
        p.append(text(LX + PW / 2, py + 80, note, size=11, color=MUTED, italic=True))

    p.append(text(W / 2, 460,
                  "Спільне трьох шарів: вихід команди повертається як текст. Різне: глибина того, у що рядок розгортається.",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "hist-shell-lineage.svg"), W, H, *p,
           title="Родовід підстановки: труба → зворотні лапки Борна → дужки Tcl")


if __name__ == "__main__":
    fig_eval_two_steps()
    fig_eias()
    fig_tcl_obj()
    fig_refcount()
    fig_own_control()
    fig_hist_shell_lineage()
    print("figures written to", OUT)
