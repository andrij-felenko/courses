# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODEBG = "#f4f6f8"
CODEFONT = "'Consolas', 'DejaVu Sans Mono', monospace"


def codeblock(x, y, w, lines, size=12, lh=1.45, title=None, accent=INK):
    """Рамка з моноширинним кодом (рядки — список). Повертає (svg, висота)."""
    pad = 12
    head = (size + 8) if title else 0
    h = head + len(lines) * size * lh + 2 * pad
    out = [rect(x, y, w, h, fill=CODEBG, stroke=accent, sw=1.6, rx=8)]
    if title:
        out.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" '
                   'fill="%s" font-weight="700">%s</text>'
                   % (x + pad, y + pad + size - 2, FONT, size, accent, esc(title)))
    ty = y + pad + head + size - 2
    for i, ln in enumerate(lines):
        out.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" '
                   'fill="%s" xml:space="preserve">%s</text>'
                   % (x + pad, ty + i * size * lh, CODEFONT, size, INK, esc(ln)))
    return "".join(out), h


# ── purpose: народжена ДОКУМЕНТУВАТИ, а не будувати ───────────────────────────
# Ідея: спершу VHDL — точний паспорт чужого чипа для Пентагону; симуляція й
# синтез приросли пізніше з ТОГО САМОГО тексту.

def fig_purpose():
    W, H = 780, 330
    p = []
    # центральний текст-опис
    cb, cbw, cbh = textbox(W / 2, 150, "один текст VHDL\n(точний опис поведінки)",
                           size=13, bold=True, fill=CODEBG, stroke=INK, sw=2, pad=14)
    p.append(cb)

    # ← початкова мета: документ
    db, dbw, dbh = textbox(150, 90, "ПАСПОРТ чипа\nдля військових:\nщо він робить,\nоднаково в усіх",
                           size=11, bold=True, color=NEG, fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(db)
    p.append(arrow(150, 90 + dbh / 2, W / 2 - cbw / 2 - 6, 150 - 18, color=NEG, sw=1.8))
    p.append(text(150, 90 - dbh / 2 - 8, "МЕТА 1980-х", size=10, color=NEG, bold=True))

    # → приросло: симуляція
    sb, sbw, sbh = textbox(630, 90, "СИМУЛЯТОР\nчитає той самий\nтекст — «проганяє»\nповедінку", size=11,
                           bold=True, color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.8)
    p.append(sb)
    p.append(arrow(W / 2 + cbw / 2 + 6, 150 - 18, 630, 90 + sbh / 2, color=FIELD, sw=1.8))
    p.append(text(630, 90 - sbh / 2 - 8, "приросло пізніше", size=10, color=FIELD, bold=True))

    # → приросло: синтез
    yb, ybw, ybh = textbox(630, 250, "СИНТЕЗАТОР\nбудує з тексту\nсправжню схему\nвентилів", size=11,
                           bold=True, color=POS, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(yb)
    p.append(arrow(W / 2 + cbw / 2 + 6, 150 + 18, 630, 250 - ybh / 2, color=POS, sw=1.8))
    p.append(text(630, 250 + ybh / 2 + 14, "приросло ще пізніше", size=10, color=POS, bold=True))

    p.append(text(W / 2, H - 16,
                  "спершу — щоб ЗАПИСАТИ поведінку однозначно; будувати з опису навчилися вже потім",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "purpose.svg"), W, H, *p,
           title="Навіщо постала VHDL: спочатку документ, а не креслення")


# ── entity-architecture: інтерфейс окремо від нутрощів ────────────────────────
# Ідея: entity = розпіновка (що зовні), architecture = схема (що всередині);
# до однієї entity можна написати кілька architecture.

def fig_entity_architecture():
    W, H = 780, 360
    p = []
    # entity — паспорт виводів
    ex, ey, ew, eh = 60, 70, 300, 150
    p.append(rect(ex, ey, ew, eh, fill="#eef4ff", stroke=NEG, sw=2.2, rx=10))
    p.append(text(ex + ew / 2, ey + 26, "entity adder", size=14, bold=True, color=NEG))
    src, sh = codeblock(ex + 20, ey + 40, ew - 40,
                        ["port ( a, b : in  std_logic;", "       s    : out std_logic );"],
                        size=11, accent=NEG)
    p.append(src)
    p.append(text(ex + ew / 2, ey + eh - 10, "лише виводи — «що зовні»", size=10, color=NEG, italic=True))

    # ніжки входів/виходу
    for i, (lab, col) in enumerate([("a", NEG), ("b", NEG)]):
        py = ey + 70 + i * 34
        p.append(line(ex - 34, py, ex, py, color=col, sw=2))
        p.append(circle(ex - 34, py, 3.5, fill=BG, stroke=col, sw=2))
        p.append(text(ex - 40, py + 4, lab, size=11, color=col, anchor="end", italic=True))
    py = ey + 90
    p.append(line(ex + ew, py, ex + ew + 34, py, color=POS, sw=2))
    p.append(circle(ex + ew + 34, py, 3.5, fill=BG, stroke=POS, sw=2))
    p.append(text(ex + ew + 40, py + 4, "s", size=11, color=POS, anchor="start", italic=True))

    # дві architecture під однією entity
    p.append(arrow(ex + ew / 2, ey + eh + 6, ex + ew / 2, ey + eh + 40, color=INK, sw=1.6))
    p.append(text(ex + ew / 2 + 8, ey + eh + 28, "до однієї entity —", size=9, color=MUTED, anchor="start"))

    a1 = fitbox(60, 268, 300, 66,
                "architecture behav:\ns <= a xor b;\n(«ЩО» має вийти)", size=11,
                fill=CODEBG, stroke=FIELD, sw=1.8, bold=True, color=FIELD)
    p.append(a1)
    a2 = fitbox(420, 268, 300, 66,
                "architecture struct:\nвентилі, з'єднані дротами\n(«ЯК саме» побудовано)", size=11,
                fill=CODEBG, stroke="#8a5fb0", sw=1.8, bold=True, color="#8a5fb0")
    p.append(a2)
    p.append(text(390, 250, "…можна кілька різних architecture", size=11, color=INK, bold=True))

    render(os.path.join(OUT, "entity-architecture.svg"), W, H, *p,
           title="entity + architecture: паспорт виводів окремо від нутрощів")


# ── std-logic-nine: один дріт має дев'ять станів, не два ───────────────────────
# Ідея: реальна лінія — не лише 0/1; std_logic ловить «нічого не знаю» (U),
# «конфлікт» (X), «відпущено» (Z) тощо — щоб симулятор бачив біду.

def fig_std_logic_nine():
    W, H = 780, 340
    p = []
    vals = [
        ("'U'", "не задано", "жоден драйвер ще не чіпав", MUTED),
        ("'X'", "конфлікт", "двоє женуть різне — коротке", POS),
        ("'0'", "нуль", "лінію притягнуто донизу", NEG),
        ("'1'", "одиниця", "лінію притягнуто вгору", NEG),
        ("'Z'", "відпущено", "високий опір, ніхто не жене", FIELD),
        ("'W'", "слабкий X", "слабкий конфлікт", POS),
        ("'L'", "слабкий 0", "підтяжка донизу", NEG),
        ("'H'", "слабка 1", "підтяжка догори", NEG),
        ("'-'", "байдуже", "синтезу вільно вибрати", "#8a5fb0"),
    ]
    cols, rows = 3, 3
    cw, ch = 236, 82
    gx, gy = 30, 56
    for i, (sym, name, note, col) in enumerate(vals):
        r, c = divmod(i, cols)
        x = gx + c * (cw + 8)
        y = gy + r * (ch + 8)
        p.append(rect(x, y, cw, ch, fill="#fbfcfe", stroke=col, sw=1.8, rx=8))
        p.append(text(x + 34, y + 42, sym, size=22, bold=True, color=col))
        p.append(line(x + 62, y + 14, x + 62, y + ch - 14, color="#e2e2e2", sw=1.2))
        p.append(text(x + 74, y + 30, name, size=12, bold=True, color=col, anchor="start"))
        p.append(mtext(x + 74, y + 50, wrap(note, 24), size=9.5, color=MUTED, anchor="start", lh=1.2))

    p.append(text(W / 2, H - 14,
                  "двійка 0/1 — лише дві клітинки; решта сім кажуть симулятору «тут щось не так»",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "std-logic-nine.svg"), W, H, *p,
           title="std_logic: у дроті не два стани, а дев'ять")


def wrap(s, width):
    """Простий перенос рядка за словами — повертає список рядків."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


# ── strong-typing: строгий тип ловить помилку на компіляції ────────────────────
# Ідея: змішав різні типи — VHDL СПИНИТЬ ще до симуляції; C/Verilog мовчки
# «домовиться» й глюк випливе вже в кремнії.

def fig_strong_typing():
    W, H = 760, 320
    p = []
    colw = 330
    lx, rx = 40, W - 40 - colw

    # VHDL — суворо
    p.append(text(lx + colw / 2, 56, "VHDL: строгий тип", size=14, bold=True, color=NEG))
    s1, h1 = codeblock(lx, 70, colw,
                       ["signal cnt : integer;",
                        "signal ln  : std_logic;",
                        "cnt <= ln;   -- різні типи!"],
                       size=11, accent=NEG)
    p.append(s1)
    xb, xbw, xbh = textbox(lx + colw / 2, 70 + h1 + 44, "✗ КОМПІЛЯТОР СПИНЯЄ\nще до симуляції",
                           size=12, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=2)
    p.append(xb)
    p.append(text(lx + colw / 2, 70 + h1 + 44 + xbh / 2 + 20,
                  "помилку видно за секунди, у себе на столі", size=10, color=MUTED, italic=True))

    # C/Verilog — вільно
    p.append(text(rx + colw / 2, 56, "Вільний тип (C, Verilog)", size=14, bold=True, color=MUTED))
    s2, h2 = codeblock(rx, 70, colw,
                       ["reg [7:0] cnt;",
                        "wire      ln;",
                        "cnt = ln;   // мовчки зіллє"],
                       size=11, accent=MUTED)
    p.append(s2)
    wb, wbw, wbh = textbox(rx + colw / 2, 70 + h2 + 44, "⚠ ЗБИРАЄТЬСЯ мовчки\nглюк випливе в кремнії",
                           size=12, bold=True, color="#b8860b", fill="#fdf6e3", stroke="#b8860b", sw=2)
    p.append(wb)
    p.append(text(rx + colw / 2, 70 + h2 + 44 + wbh / 2 + 20,
                  "ловиш уже на платі — коштує днів", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "strong-typing.svg"), W, H, *p,
           title="Строга типізація: багатослівність в обмін на ранню ловлю помилок")


# ── vhdl-birth-steps: чотири кроки народження мови ────────────────────────────
# Ідея: не один винахід, а ланцюг — біда документування → програма+контракт →
# взірець Ada → драбина стандартів. Різні люди, різна мета на кожному кроці.

def fig_vhdl_birth_steps():
    W, H = 820, 340
    p = []
    steps = [
        ("1", "БІДА", "тисячі спецчипів,\nкожна фірма\nдокументує по-своєму;\nзнання зникає\nз фірмою", NEG, "#eef4ff"),
        ("2", "ПРОГРАМА + КОНТРАКТ", "VHSIC (1980)\nставить задачу;\nконтракт ВПС 1983:\nIntermetrics · TI · IBM", FIELD, "#eafaf0"),
        ("3", "ВЗІРЕЦЬ Ada", "беруть готову\nсувору мову DoD —\nне винаходити\nнаново перевірене", "#8a5fb0", "#f3edf9"),
        ("4", "ДРАБИНА СТАНДАРТІВ", "7.2 (1985) →\nIEEE 1076-1987 →\n1076-1993 +\nstd_logic_1164", POS, "#fdecea"),
    ]
    n = len(steps)
    cw = 176
    gap = (W - 2 * 24 - n * cw) / (n - 1)
    y = 74
    ch = 176
    cxs = []
    for i, (num, head, body, col, bg) in enumerate(steps):
        x = 24 + i * (cw + gap)
        cx = x + cw / 2
        cxs.append((x, cx))
        p.append(rect(x, y, cw, ch, fill=bg, stroke=col, sw=2.2, rx=10))
        # кружок з номером кроку
        p.append(circle(x + 22, y + 22, 15, fill=BG, stroke=col, sw=2.2))
        p.append(text(x + 22, y + 27, num, size=15, bold=True, color=col))
        p.append(text(cx + 12, y + 27, head, size=11.5, bold=True, color=col, anchor="middle"))
        p.append(mtext(cx, y + 62, body.split("\n"), size=10.5, color=INK, lh=1.32))
    # стрілки між кроками
    for i in range(n - 1):
        x_from = cxs[i][0] + cw
        x_to = cxs[i + 1][0]
        p.append(arrow(x_from + 2, y + ch / 2, x_to - 2, y + ch / 2, color=INK, sw=2))
    # підписи ролей під стрілками/кроками
    roles = ["потреба", "замовник + виконавці", "філософія", "однозначність росте"]
    for (x, cx), r in zip(cxs, roles):
        p.append(text(cx, y + ch + 22, r, size=10, color=MUTED, italic=True))
    p.append(text(W / 2, H - 14,
                  "не один винахід генія, а ланцюг кроків: мета на старті — ДОКУМЕНТ, будувати залізо навчаться пізніше",
                  size=11, color=INK, italic=True))
    render(os.path.join(OUT, "vhdl-birth-steps.svg"), W, H, *p,
           title="Народження VHDL у чотири кроки")


# ── document-to-silicon: три вміння того самого тексту, здобуті по черзі ───────
# Ідея: спершу VHDL лише ДОКУМЕНТУЄ; тоді приростає СИМУЛЯЦІЯ; аж наприкінці —
# СИНТЕЗ, що будує з опису схему. Порядок у часі — стрижень історії.

def fig_document_to_silicon():
    W, H = 800, 360
    p = []
    # спільна вісь часу
    ax = 60
    ay = H - 54
    p.append(arrow(ax - 10, ay, W - 30, ay, color=MUTED, sw=1.8))
    p.append(text(W - 30, ay + 22, "час →", size=11, color=MUTED, anchor="end", italic=True))

    stages = [
        ("ДОКУМЕНТ", "мета 1983:\nточний паспорт\nповедінки чужого\nчипа — обов'язковий\nза MIL-STD-454", NEG, "#eef4ff", "записати"),
        ("СИМУЛЯЦІЯ", "«так очевидно\nприваблива» ідея:\nраз записано\nформально —\nпроганяй на ПК", FIELD, "#eafaf0", "проганяти"),
        ("СИНТЕЗ", "перелом:\nінструмент сам\nбудує з опису\nсхему вентилів\nі тригерів", POS, "#fdecea", "будувати"),
    ]
    n = len(stages)
    cw = 220
    cx0 = 40
    gap = (W - 2 * 40 - n * cw) / (n - 1) if n > 1 else 0
    y = 66
    ch = 168
    centers = []
    for i, (head, body, col, bg, verb) in enumerate(stages):
        x = cx0 + i * (cw + gap)
        cx = x + cw / 2
        centers.append(cx)
        p.append(rect(x, y, cw, ch, fill=bg, stroke=col, sw=2.2, rx=10))
        p.append(text(cx, y + 28, head, size=15, bold=True, color=col))
        p.append(line(x + 20, y + 40, x + cw - 20, y + 40, color=col, sw=1.2))
        p.append(mtext(cx, y + 62, body.split("\n"), size=11, color=INK, lh=1.34))
        # риска на осі часу + що вміє
        p.append(line(cx, y + ch, cx, ay, color=col, sw=1.4, dash="4 4"))
        p.append(circle(cx, ay, 5, fill=bg, stroke=col, sw=2))
        p.append(text(cx, ay - 12, verb, size=11, bold=True, color=col))
    # стрілки «той самий текст росте»
    for i in range(n - 1):
        x_from = cx0 + i * (cw + gap) + cw
        x_to = cx0 + (i + 1) * (cw + gap)
        p.append(arrow(x_from + 2, y + ch / 2, x_to - 2, y + ch / 2, color=INK, sw=2))
        if i == 0:
            p.append(mtext((x_from + x_to) / 2, y + ch / 2 - 20,
                           ["той самий", "текст"], size=9, color=MUTED, lh=1.15))
    p.append(text(W / 2, 48,
                  "той самий текст VHDL здобував уміння по черзі — будувати залізо навчився ОСТАННІМ",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(OUT, "document-to-silicon.svg"), W, H, *p,
           title="Спершу документ, симуляція й синтез — потім")


if __name__ == "__main__":
    fig_purpose()
    fig_entity_architecture()
    fig_std_logic_nine()
    fig_strong_typing()
    fig_vhdl_birth_steps()
    fig_document_to_silicon()
    print("OK: figures written to", OUT)
