# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 19 — «Пам'ять, адресація, стек і купа» (Модуль 3).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; стрілки через marker.
Підписи — посекційно (Рис. C.S.N); історія до розділу — секція 0 (Рис. 19.0.N).
Допоміжні функції — спільні з рештою розділів (копія), щоб вигляд був єдиний.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
AMBER = "#caa24a"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def polyline(points, color=INK, w=2.4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{w}"{d}/>\n'


def path(d, fill="none", stroke=INK, w=2):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>\n'


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


def _wrap(s, n):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= n:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ── феритове осердя: кільце + стрілка намагніченості (вліво=1, вправо=0) ─────
def _core(cx, cy, r, one, lab=True):
    col = RED if one else BLUE
    out = circle(cx, cy, r, "none", col, 3.4)
    y = cy - r
    if one:  # проти годинникової
        out += arrow(cx + r * 0.55, y, cx - r * 0.55, y, col, 2)
    else:    # за годинниковою
        out += arrow(cx - r * 0.55, y, cx + r * 0.55, y, col, 2)
    if lab:
        out += text(cx, cy + 5, "1" if one else "0", 14, col, "middle", "bold")
    return out


# ═══════════ §0 — історія: магнітна пам'ять на осердях ══════════════════════
# ── Рис. 19.0.1 — таймлайн технологій пам'яті ──────────────────────────────
def fig_timeline():
    W, H = 900, 648
    s = header(W, H)
    s += text(W / 2, 38, "Як машини вчилися ПАМ'ЯТАТИ: довга дорога до надійної пам'яті", 20.5, INK, "middle", "bold")
    s += text(W / 2, 60, "ранні пам'яті були повільні, примхливі або крихкі — аж поки магнітні осердя не дали швидку й надійну",
              12, GREY, "middle", style="italic")
    spine = 260
    top, bot = 100, H - 26
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("~1947", "лінії затримки (ртутні)", "Біт «біжить» трубкою зі ртуттю по колу — ПОСЛІДОВНО, повільно, примхливо до температури", False),
        ("~1947", "трубки Вільямса (CRT)", "Біти як плямки на екрані — швидше, та ненадійно й крихко (гасли, плутались)", False),
        ("ті ж роки", "магнітні барабани", "Місткі й нелеткі, але МЕХАНІЧНІ: чекай, поки потрібне місце доїде під голівку", False),
        ("1953", "пам'ять на осердях (Форрестер)", "Феритові кільця: ШВИДКО, НАДІЙНО, ВИПАДКОВИЙ доступ і НЕЛЕТКО. Прорив для Whirlwind", True),
        ("1955–75", "двадцять років панування", "Осердя стали стандартною оперативною пам'яттю всіх комп'ютерів епохи", False),
        ("1970-ті", "напівпровідникова RAM", "Кремнієва DRAM витіснила осердя — дешевша й дрібніша, та з осердь зросла ціла індустрія пам'яті", False),
    ]
    n = len(nodes)
    for i, (yr, who, q, hl) in enumerate(nodes):
        y = top + 28 + (bot - top - 56) * i / (n - 1)
        if hl:
            s += circle(spine, y, 11, "#fff", RED, 0)
            s += circle(spine, y, 10, "none", RED, 3.2)
            s += circle(spine, y, 4.5, RED, RED, 1)
        else:
            s += circle(spine, y, 7, "#fff", INK, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 26, y - 4, who, 15, (RED if hl else INK), "start", "bold")
        for j, ln in enumerate(_wrap(q, 62)):
            s += text(spine + 26, y + 16 + j * 17, ln, 12, INK, "start", style="italic")
    save("fig-19-0-1-timeline.svg", s)


# ── Рис. 19.0.2 — один біт у феритовому кільці ─────────────────────────────
def fig_core_bit():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Один біт — у крихітному феритовому кільці", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "напрямок намагніченості кільця кодує 0 чи 1; завдяки гістерезису він тримається й БЕЗ живлення (нелетко)",
              11.5, GREY, "middle", style="italic")
    s += _core(220, 150, 46, False)
    s += text(220, 232, "за годинниковою = 0", 12, BLUE, "middle", "bold")
    s += _core(420, 150, 46, True)
    s += text(420, 232, "проти годинникової = 1", 12, RED, "middle", "bold")
    s += text(320, 110, "той самий", 10.5, GREY, "middle", style="italic")
    s += text(320, 126, "магнітик —", 10.5, GREY, "middle", style="italic")
    s += text(320, 142, "два напрямки", 10.5, GREY, "middle", style="italic")
    # петля гістерезису
    s += text(650, 100, "гістерезис: «магнітна пам'ять»", 12, INK, "middle", "bold")
    ox, oy = 650, 175
    s += arrow(ox - 90, oy, ox + 90, oy, GREY, 1.4)
    s += arrow(ox, oy + 55, ox, oy - 55, GREY, 1.4)
    s += text(ox + 96, oy + 4, "струм", 9.5, GREY, "start")
    s += text(ox + 4, oy - 58, "намагніч.", 9.5, GREY, "start")
    loop = [(ox - 80, oy + 38), (ox - 20, oy + 38), (ox - 20, oy - 38),
            (ox + 80, oy - 38), (ox + 20, oy - 38), (ox + 20, oy + 38), (ox - 80, oy + 38)]
    s += polyline(loop, INK, 2.2)
    s += text(ox - 50, oy + 52, "0", 12, BLUE, "middle", "bold")
    s += text(ox + 50, oy - 46, "1", 12, RED, "middle", "bold")
    s += text(650, 252, "прямокутна петля: стан «застрягає» в одному з двох —", 10, GREY, "middle", style="italic")
    s += text(650, 268, "і лишається там навіть коли струм зник", 10, GREY, "middle", style="italic")
    s += rect(60, 300, W - 120, 96, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 324, "На відміну від тригера (Розділ 16), що тримає біт, лише поки є живлення, осердя пам'ятає й знеструмлене —", 11.5, INK, "middle", "bold")
    s += text(W / 2, 346, "бо магнітний матеріал «застрягає» в одному з двох напрямків (гістерезис). Вимкнув машину — пам'ять ціла.", 11.5, INK, "middle", "bold")
    s += text(W / 2, 372, "Кільця були крихітні (спершу ~1 мм, далі ще менші) — мільйони їх на машину, нанизані вручну на сітку дротів.", 10.5, GREY, "middle", style="italic")
    save("fig-19-0-2-core-bit.svg", s)


# ── Рис. 19.0.3 — збіг струмів: адресація X–Y ──────────────────────────────
def fig_coincident():
    W, H = 900, 482
    s = header(W, H)
    s += text(W / 2, 34, "Геній Форрестера: вибір одного осердя «збігом струмів» по сітці X–Y", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "пів-струму по дроту X + пів-струму по дроту Y → лише осердя на ПЕРЕТИНІ дістає повний струм і перемикається",
              11.5, GREY, "middle", style="italic")
    gx, gy, step = 300, 120, 80
    selc, selr = 2, 1
    # дроти Y (вертикальні)
    for c in range(4):
        x = gx + c * step
        half = (c == selc)
        s += line(x, gy - 30, x, gy + 4 * step - 30, RED if half else FAINT, 2.4 if half else 1.6)
        s += text(x, gy - 40, f"Y{c}", 10.5, RED if half else GREY, "middle", "bold")
    # дроти X (горизонтальні)
    for r in range(4):
        y = gy + r * step
        half = (r == selr)
        s += line(gx - 30, y, gx + 3 * step + 30, y, BLUE if half else FAINT, 2.4 if half else 1.6)
        s += text(gx - 40, y + 4, f"X{r}", 10.5, BLUE if half else GREY, "end", "bold")
    # осердя
    for r in range(4):
        for c in range(4):
            x, y = gx + c * step, gy + r * step
            sel = (r == selr and c == selc)
            col = GREEN if sel else GREY
            s += circle(x, y, 17, "none", col, 3.2 if sel else 2)
            if sel:
                s += circle(x, y, 25, "none", GREEN, 1.4)
    sx, sy = gx + selc * step, gy + selr * step
    s += text(sx + 34, sy - 18, "обране!", 11, GREEN, "start", "bold")
    s += text(sx + 34, sy - 3, "X1+Y2", 10, GREEN, "start", "bold")
    s += text(sx + 34, sy + 13, "повний струм", 9.5, GREY, "start")
    # пояснення збоку
    s += rect(615, 120, 250, 130, "#f6f8f6", GREY, 1.4, 10)
    s += text(740, 144, "Половинки додаються", 12, INK, "middle", "bold")
    s += text(630, 168, "• на обраному X: пів-струму", 10.5, BLUE, "start")
    s += text(630, 188, "• на обраному Y: пів-струму", 10.5, RED, "start")
    s += text(630, 210, "• на перетині: пів+пів = повний", 10.5, GREEN, "start", "bold")
    s += text(630, 230, "→ перемикається ЛИШЕ воно", 10.5, GREEN, "start", "bold")
    s += rect(60, 410, W - 120, 60, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 432, "Уся хитрість: решта осердь на тих лініях дістають лише ПОЛОВИНУ струму — замало, щоб перемкнутись. Спрацьовує тільки перетин.",
              11, INK, "middle", "bold")
    s += text(W / 2, 454, "Тому одне осердя з тисяч адресують лише двома дротами (X та Y) — не дротом до кожного. Це й зробило пам'ять практичною.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-0-3-coincident.svg", s)


# ── Рис. 19.0.4 — руйнівне читання й відновлення ───────────────────────────
def fig_destructive():
    W, H = 900, 432
    s = header(W, H)
    s += text(W / 2, 34, "Підступ: читання РУЙНУЄ біт — тож його одразу відновлюють", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "щоб прочитати, осердя силоміць перемикають у 0 — і дивляться, чи був «клац»; якщо був, то там була 1",
              11.5, GREY, "middle", style="italic")
    # крок 1
    s += text(155, 96, "1. пробуємо записати 0", 11.5, INK, "start", "bold")
    s += _core(180, 150, 40, True)
    s += arrow(228, 150, 300, 150, INK, 2.2)
    s += text(264, 138, "струм", 9, GREY, "middle")
    s += _core(345, 150, 40, False)
    s += text(180, 210, "було 1", 10.5, RED, "middle", "bold")
    s += text(345, 210, "стало 0", 10.5, BLUE, "middle", "bold")
    s += text(262, 178, "ПЕРЕМКНУЛОСЬ", 9, GREEN, "middle", "bold")
    # сенс-дріт
    s += text(560, 110, "перемикання наводить", 10.5, GREEN, "start")
    s += text(560, 126, "імпульс у СЕНС-дроті:", 10.5, GREEN, "start", "bold")
    s += polyline([(560, 165), (610, 165), (615, 140), (625, 140), (630, 165), (760, 165)], GREEN, 2.2)
    s += text(620, 132, "клац!", 9.5, GREEN, "middle", "bold")
    s += text(660, 185, "→ отже, там була 1", 11, GREEN, "start", "bold")
    s += text(560, 210, "(якби була 0 — нічого не перемкнулось би, імпульсу нема → там 0)", 9.5, GREY, "start", style="italic")
    # крок 2 — відновлення
    s += rect(60, 250, W - 120, 70, "#fff8e8", AMBER, 1.8, 10)
    s += text(W / 2, 274, "АЛЕ: читання знищило значення (осердя тепер 0). Тож одразу після читання його ЗАПИСУЮТЬ НАЗАД —",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 296, "цикл «прочитати-відновити» (read-restore). Кожне читання непомітно перезаписує біт.",
              11, INK, "middle", "bold")
    s += text(W / 2, 310, "", 9, GREY, "middle")
    s += text(W / 2, 350, "Це «руйнівне читання» — характерна риса осердь (і, до речі, сучасної DRAM теж: вона так само відновлює біти).",
              11, INK, "middle", "bold")
    s += text(W / 2, 376, "Через дроти X, Y, сенс і заборони (inhibit) крізь кожне кільце треба було протягти по 3–4 дротини — мільйони разів.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 400, "Тому пам'ять на осердях… ткали вручну — здебільшого жінки з голкою, кільце за кільцем. Праця, гідна окремої згадки.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-0-4-destructive.svg", s)


# ── Рис. 19.0.5 — чому це важило + місток до розділу ───────────────────────
def fig_significance():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Чому осердя змінили все — і чому це вступ саме до цього розділу", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "перша швидка, надійна пам'ять із ВИПАДКОВИМ доступом зробила збережену програму (Розділ 18) практичною",
              11.5, GREY, "middle", style="italic")
    feats = [
        ("Випадковий доступ", "будь-яка комірка — миттєво, не чекаючи (на відміну від ліній і барабанів)", GREEN),
        ("Надійність і швидкість", "не гасне, не плутає — на осердя нарешті можна було покластися", GREEN),
        ("Нелеткість", "тримала дані без живлення; звідси й термін «core dump» — досі живий", BLUE),
        ("Сітка адрес X–Y", "пам'ять = РЕШІТКА комірок, кожна за своєю адресою", AMBER),
    ]
    for i, (k, v, col) in enumerate(feats):
        y = 88 + i * 56
        s += rect(70, y, 760, 46, "#fafafa", col, 1.6, 8)
        s += text(90, y + 28, k, 12.5, col, "start", "bold")
        s += text(330, y + 28, v, 11, INK, "start")
    s += rect(60, 322, W - 120, 102, "#f4f7f4", GREEN, 1.8, 10)
    s += text(W / 2, 346, "Останній пункт — наш місток. Пам'ять на осердях була буквально РЕШІТКОЮ комірок, кожна за адресою (X,Y) —", 11.5, INK, "middle", "bold")
    s += text(W / 2, 368, "точнісінько та модель, що ми вивчатимемо в §19.1: пам'ять як масив комірок із адресами.", 11.5, INK, "middle", "bold")
    s += text(W / 2, 392, "Технологія змінилася (тепер кремній, не ферит), а сама ІДЕЯ адресованої решітки лишилась незмінною від Форрестера донині.", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, 414, "Заслуга — Джея Форрестера (практична схема збігу струмів), хоч над осердями працювали й інші (Ван,Ві) — як завжди, праця багатьох.", 10.5, GREY, "middle", style="italic")
    save("fig-19-0-5-significance.svg", s)


# ═══════════ §19.1 — Пам'ять як масив комірок з адресами ════════════════════
def _cell(x, y, addr, val, w=120, h=30, col=INK, bg="#ffffff", hl=False):
    out = rect(x, y, w, h, "#fdf4f4" if hl else bg, RED if hl else col, 2 if hl else 1.4, 4)
    out += text(x - 10, y + h * 0.66, addr, 11, GREY, "end", "bold")
    out += text(x + w / 2, y + h * 0.66, val, 12.5, INK, "middle", "bold")
    return out


# ── Рис. 19.1.1 — пам'ять як масив пронумерованих комірок ──────────────────
def fig191_array():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Пам'ять — це довгий масив пронумерованих комірок", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожна комірка тримає один байт (§17.1) і має свій унікальний НОМЕР — адресу; як вулиця будинків із номерами",
              11.5, GREY, "middle", style="italic")
    s += text(360, 92, "адреса", 11, GREY, "end", "bold")
    s += text(440, 92, "вміст (байт)", 11, INK, "middle", "bold")
    vals = ["0x2A", "0xFF", "0x00", "0x41", "0x7C", "0x10", "0x9B", "0x03"]
    for i, v in enumerate(vals):
        s += _cell(380, 104 + i * 38, f"0x{i:02X}", v, w=120, hl=(i == 3))
    s += text(513, 104 + 3 * 38 + 20, "← комірка за адресою 0x03 містить байт 0x41", 11, RED, "start", "bold")
    # аналогія вулиці
    s += rect(70, 150, 250, 200, "#f4f7f4", GREEN, 1.6, 10)
    s += text(195, 176, "Аналогія: вулиця", 12.5, GREEN, "middle", "bold")
    for i in range(4):
        y = 196 + i * 36
        s += rect(110, y, 36, 28, "#eef7ee", GREEN, 1.4, 4)
        s += text(128, y + 19, "🏠", 13, INK, "middle")
        s += text(95, y + 19, f"№{i}", 10, GREY, "end", "bold")
        s += text(160, y + 19, "← мешканець (дані)", 9.5, INK, "start")
    s += text(195, 340, "номер будинку = адреса", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, 388, "Дві окремі речі: АДРЕСА каже, ДЕ комірка (її номер), а ВМІСТ — ЩО в ній лежить (байт-значення).", 11.5, INK, "middle", "bold")
    s += text(W / 2, 412, "Це та сама модель, що дали осердя (історія розділу): решітка комірок, до кожної — за її координатою/номером.", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, 438, "Зазвичай адреси записують шістнадцятково (§17.2): 0x00, 0x01, 0x02… — компактно й звично для пам'яті.", 10.5, GREY, "middle", style="italic")
    save("fig-19-1-1-array.svg", s)


# ── Рис. 19.1.2 — адреса vs дані (і шина §18.2) ────────────────────────────
def fig191_addr_data():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Адреса vs дані: «де» і «що» — це РІЗНІ речі (й різні шини)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "процесор називає АДРЕСУ (куди), а пам'ять віддає чи приймає ДАНІ (що) — кожне своєю шиною (§18.2)",
              11.5, GREY, "middle", style="italic")
    s += rect(80, 150, 180, 110, "#fdf4f4", RED, 2, 12)
    s += text(170, 200, "ПРОЦЕСОР", 13, RED, "middle", "bold")
    s += text(170, 222, "«дай байт за 0x20»", 10, GREY, "middle", style="italic")
    # адресна шина
    s += arrow(262, 178, 600, 178, BLUE, 2.6)
    s += text(430, 168, "АДРЕСНА шина: 0x20  (ДЕ — номер комірки)", 11, BLUE, "middle", "bold")
    # шина даних
    s += arrow(600, 232, 262, 232, GREEN, 2.6)
    s += text(430, 252, "шина ДАНИХ: 0x41  (ЩО — сам байт)", 11, GREEN, "middle", "bold")
    s += rect(600, 130, 220, 150, "#f4f7f4", GREEN, 2, 12)
    s += text(710, 152, "ПАМ'ЯТЬ", 13, GREEN, "middle", "bold")
    s += _cell(660, 168, "0x1F", "0x10", w=110, h=26)
    s += _cell(660, 198, "0x20", "0x41", w=110, h=26, hl=True)
    s += _cell(660, 228, "0x21", "0x9B", w=110, h=26)
    s += rect(60, 300, W - 120, 100, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 324, "Не плутайте: 0x20 — це АДРЕСА (яка комірка), а 0x41 — це ДАНІ (що в ній). Обидва — числа, та сенс цілком різний.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 346, "Пам'ятаєте шини з §18.2? Адресна несе «де», шина даних — «що». Тут вони оживають: ось навіщо їх дві.",
              11, INK, "middle", "bold")
    s += text(W / 2, 372, "Плутанина «адреса проти значення» — джерело багатьох багів; тримайте їх чітко нарізно (а далі будуть ще й покажчики, §19.4).",
              10.5, GREY, "middle", style="italic")
    save("fig-19-1-2-addr-data.svg", s)


# ── Рис. 19.1.3 — побайтова адресація; багатобайтові значення ──────────────
def fig191_byte_addr():
    W, H = 900, 416
    s = header(W, H)
    s += text(W / 2, 34, "Побайтова адресація: одна адреса = один байт", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожна адреса вказує на ОДИН байт; багатобайтове число займає кілька ПОСЛІДОВНИХ адрес (§17.7)",
              11.5, GREY, "middle", style="italic")
    # стовпчик байтів
    addrs = ["0x10", "0x11", "0x12", "0x13", "0x14"]
    vals = ["0x78", "0x56", "0x34", "0x12", "0x00"]
    for i, (a, v) in enumerate(zip(addrs, vals)):
        hl = i < 4
        s += _cell(360, 100 + i * 40, a, v, w=130, hl=hl)
    # дужка для 4 байтів
    s += line(505, 100, 505, 260, RED, 2)
    s += line(505, 100, 515, 100, RED, 2)
    s += line(505, 260, 515, 260, RED, 2)
    s += text(525, 165, "одне 32-бітне число", 12, RED, "start", "bold")
    s += text(525, 185, "0x12345678", 13, INK, "start", "bold")
    s += text(525, 207, "= 4 байти за адресами", 10.5, GREY, "start")
    s += text(525, 223, "0x10, 0x11, 0x12, 0x13", 10.5, GREY, "start")
    s += text(525, 248, "(порядок байтів — endianness, §17.7)", 10, GREY, "start", style="italic")
    s += text(280, 280, "адреса", 10.5, GREY, "middle", "bold")
    s += rect(60, 308, W - 120, 92, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 332, "Байт — найдрібніша адресована порція (§17.1). Хочеш 16-, 32- чи 64-бітне число — воно лягає в 2, 4 чи 8 сусідніх комірок.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 354, "А в якому ПОРЯДКУ ті байти розкладені (молодший першим чи старший) — це вже endianness із §17.7; тут — лише що вони сусідні.",
              11, INK, "middle", "bold")
    s += text(W / 2, 380, "Тому, до речі, адреси багатобайтових значень зазвичай кратні їхньому розміру (вирівнювання) — так залізу зручніше читати.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-1-3-byte-addr.svg", s)


# ── Рис. 19.1.4 — розмір адресного простору: 2^N ──────────────────────────
def fig191_space():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Скільки комірок можна адресувати: N бітів адреси → 2ᴺ комірок", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "ширина адреси (адресної шини, §18.2) задає розмір пам'яті, яку машина взагалі здатна позначити — знову 2ᴺ (§17.1)",
              11.5, GREY, "middle", style="italic")
    rows = [
        ("8 бітів", "2⁸ = 256", "256 байтів", BLUE),
        ("16 бітів", "2¹⁶ = 65 536", "64 КБ", GREEN),
        ("24 біти", "2²⁴", "16 МБ", AMBER),
        ("32 біти", "2³² ≈ 4.3 млрд", "4 ГБ", RED),
    ]
    y0 = 96
    for i, (bits, cnt, human, col) in enumerate(rows):
        y = y0 + i * 64
        s += rect(120, y, 200, 50, "#fafafa", col, 1.8, 8)
        s += text(220, y + 31, f"{bits} адреси", 13, col, "middle", "bold")
        s += arrow(326, y + 25, 386, y + 25, INK, 2)
        s += rect(390, y, 220, 50, "#ffffff", col, 1.4, 8)
        s += text(500, y + 31, cnt, 12.5, INK, "middle", "bold")
        s += text(660, y + 31, f"≈ {human}", 13, col, "middle", "bold")
    s += text(W / 2, 372, "Ось чому «розрядність» процесора стосується й пам'яті: 16-бітна адреса бачить лише 64 КБ, 32-бітна — аж 4 ГБ.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 398, "Це та сама вибухова формула 2ᴺ із §17.1 — тут вона міряє МІСТКІСТЬ адресного простору. Кожен біт адреси подвоює пам'ять.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-1-4-space.svg", s)


# ── Рис. 19.1.5 — дві операції: читання й запис ────────────────────────────
def fig191_rw():
    W, H = 900, 416
    s = header(W, H)
    s += text(W / 2, 34, "Дві операції над пам'яттю: читання й запис", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "ЧИТАТИ: дай адресу — отримай байт. ПИСАТИ: дай адресу + байт — він збережеться. Що саме — каже шина керування (§18.2)",
              11.5, GREY, "middle", style="italic")
    # читання
    s += rect(70, 92, 360, 130, "#eef7ee", GREEN, 1.8, 12)
    s += text(250, 116, "ЧИТАННЯ (read)", 13, GREEN, "middle", "bold")
    s += text(160, 150, "процесор:", 10, GREY, "middle")
    s += text(160, 168, "«адреса 0x20»", 11, BLUE, "middle", "bold")
    s += arrow(232, 163, 320, 163, BLUE, 2.2)
    s += text(360, 150, "пам'ять:", 10, GREY, "middle")
    s += text(360, 168, "«ось 0x41»", 11, GREEN, "middle", "bold")
    s += arrow(320, 196, 232, 196, GREEN, 2.2)
    s += text(250, 212, "дані повертаються процесору", 9.5, GREY, "middle", style="italic")
    # запис
    s += rect(470, 92, 360, 130, "#f3f5fd", BLUE, 1.8, 12)
    s += text(650, 116, "ЗАПИС (write)", 13, BLUE, "middle", "bold")
    s += text(560, 150, "процесор:", 10, GREY, "middle")
    s += text(560, 168, "«за 0x20 поклади 0x99»", 10.5, BLUE, "middle", "bold")
    s += arrow(632, 182, 740, 182, BLUE, 2.4)
    s += text(770, 168, "пам'ять", 10, GREY, "middle")
    s += text(770, 186, "зберігає", 10.5, GREEN, "middle", "bold")
    s += text(650, 212, "комірка 0x20 тепер містить 0x99", 9.5, GREY, "middle", style="italic")
    s += rect(60, 240, W - 120, 96, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 264, "Усе, що робить процесор із пам'яттю, зводиться до цих двох дій: прочитати комірку або записати в неї.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 286, "Згадайте «вибірку» з §18.3: це і є ЧИТАННЯ команди за адресою з PC. А збереження результату (§18.2) — це ЗАПИС.",
              11, INK, "middle", "bold")
    s += text(W / 2, 312, "Шина керування (§18.2) щоразу каже пам'яті, що робити — читати чи писати; адреса каже куди, шина даних несе байт.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 366, "Випадковий доступ (RAM): будь-яку комірку — напряму й миттєво, не чекаючи (дарунок осердь, історія розділу).",
              11, INK, "middle", "bold")
    save("fig-19-1-5-rw.svg", s)


# ── Рис. 19.1.6 — комірка тримає ЧИСЛО; сенс — за домовленістю ─────────────
def fig191_meaning():
    W, H = 900, 408
    s = header(W, H)
    s += text(W / 2, 34, "Комірка тримає просто ЧИСЛО — а що воно означає, вирішує програма", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "адреса каже лише ДЕ; самі біти сенсу не мають (§17.1) — той самий байт може бути числом, буквою, командою…",
              11.5, GREY, "middle", style="italic")
    s += _cell(400, 92, "0x20", "0x41", w=120, h=44, hl=True)
    s += text(460, 154, "той самий байт 0x41 (= 0100 0001)", 11, GREY, "middle", style="italic")
    means = [("ціле число", "65", BLUE), ("символ", "'A' (код)", GREEN),
             ("частина команди", "opcode/операнд", RED), ("частина дробу", "біти float", AMBER)]
    for i, (k, v, col) in enumerate(means):
        x = 90 + i * 195
        s += arrow(460, 168, x + 90, 196, GREY, 1.4, "3 3")
        s += rect(x, 200, 180, 70, "#fafafa", col, 1.6, 10)
        s += text(x + 90, 226, k, 12, col, "middle", "bold")
        s += text(x + 90, 250, v, 12, INK, "middle", "bold")
    s += rect(60, 292, W - 120, 100, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 316, "Це наскрізна думка Розділу 17, тепер у пам'яті: байт у комірці — просто число; ЯК його прочитати, вирішує програма.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 338, "Адреса — це лише МІСЦЕ. Чи лежить там код, чи дані, чи число, чи буква — залежить від того, як цю комірку ВЖИВАЮТЬ.",
              11, INK, "middle", "bold")
    s += text(W / 2, 364, "Звідси й сила фон-нейманівської машини (Розділ 18): код і дані — однакові числа в однаковій пам'яті, різні лише вживанням.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 384, "І звідси ж клас багів: прочитати комірку «не за тією домовленістю» (дані як код, ціле як дріб) — і все ламається.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-1-6-meaning.svg", s)


# ═══════════ §19.2 — Карта пам'яті: регіони ═════════════════════════════════
# ── Рис. 19.2.1 — класична карта пам'яті ───────────────────────────────────
def fig192_map():
    W, H = 900, 528
    s = header(W, H)
    s += text(W / 2, 34, "Карта пам'яті: адресний простір поділено на регіони", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "не вся пам'ять однакова — різні діапазони адрес відведені під різне: код, сталі, змінні, купа, стек",
              11.5, GREY, "middle", style="italic")
    barx, barw = 350, 250
    segs = [
        ("стек (stack)", "виклики функцій, локальні · §19.5", RED, "#fdf4f4", 56, "↓ росте ВНИЗ"),
        ("вільний простір", "сюди ростуть стек і купа", GREY, "#f6f8f6", 64, ""),
        ("купа (heap)", "динамічна пам'ять · §19.6", AMBER, "#fff8e8", 50, "↑ росте ВГОРУ"),
        (".bss", "глобальні, нульові на старті", BLUE, "#f3f5fd", 46, ""),
        (".data", "глобальні з початковим значенням", BLUE, "#f3f5fd", 46, ""),
        (".rodata", "сталі: рядки, таблиці (RO)", GREEN, "#eef7ee", 46, ""),
        (".text — КОД", "машинні інструкції (RO)", GREEN, "#eef7ee", 58, ""),
    ]
    y = 100
    for name, sub, col, bg, h, note in segs:
        s += rect(barx, y, barw, h, bg, col, 1.8, 0)
        s += text(barx + barw / 2, y + h / 2, name, 12.5, col, "middle", "bold")
        s += text(barx + barw / 2, y + h / 2 + 16, sub, 9.5, GREY, "middle")
        if note:
            s += text(barx + barw + 14, y + h / 2 + 4, note, 11, col, "start", "bold")
        y += h
    s += text(barx - 14, 110, "висока адреса", 10.5, GREY, "end", "bold")
    s += text(barx - 14, y - 4, "0x0000 (низька)", 10.5, GREY, "end", "bold")
    s += arrow(barx - 60, 120, barx - 60, y - 16, GREY, 1.6)
    s += text(barx - 76, (110 + y) / 2, "адреси", 10, GREY, "middle", "bold")
    # стрілки росту
    s += arrow(barx + barw + 90, 116, barx + barw + 90, 150, RED, 2)
    s += arrow(barx + barw + 90, 250, barx + barw + 90, 216, AMBER, 2)
    s += text(W / 2, 500, "Кожне має своє місце: код — де процесор його вибирає; змінні — де можна міняти; купа й стек ростуть назустріч у вільний простір.",
              10.5, INK, "middle", "bold")
    save("fig-19-2-1-map.svg", s)


# ── Рис. 19.2.2 — що тримає кожен регіон ───────────────────────────────────
def fig192_regions():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Що тримає кожен регіон — і які в нього властивості", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "шість типових ділянок; знати, де що живе, — половина розуміння будь-якого бага з пам'яттю",
              11.5, GREY, "middle", style="italic")
    s += rect(70, 84, 200, 28, "#eef0f4", INK, 1.3, 6)
    s += text(90, 103, "регіон", 11.5, INK, "start", "bold")
    s += text(440, 103, "що тримає", 11.5, INK, "middle", "bold")
    s += text(770, 103, "властивість", 11.5, INK, "middle", "bold")
    rows = [
        (".text (код)", "машинні інструкції програми", "тільки читання", GREEN),
        (".rodata", "сталі: рядки-літерали, таблиці", "тільки читання", GREEN),
        (".data", "глобальні/статичні з початковим значенням", "читання-запис", BLUE),
        (".bss", "глобальні/статичні, нульові на старті", "читання-запис", BLUE),
        ("купа (heap)", "динамічні дані на запит (§19.6)", "RW · росте ↑", AMBER),
        ("стек (stack)", "виклики функцій, локальні (§19.5)", "RW · росте ↓", RED),
    ]
    for i, (r, what, prop, col) in enumerate(rows):
        y = 120 + i * 46
        s += rect(70, y, 200, 40, "#fafafa", col, 1.5, 6)
        s += text(90, y + 25, r, 12, col, "start", "bold")
        s += rect(280, y, 320, 40, "#ffffff", GREY, 1, 6)
        s += text(290, y + 25, what, 10.5, INK, "start")
        s += rect(610, y, 220, 40, "#ffffff", col, 1.2, 6)
        s += text(720, y + 25, prop, 11, col, "middle", "bold")
    s += text(W / 2, 414, "Код і сталі — незмінні (RO), тож їх часто кладуть у постійну пам'ять (Flash, §19.3); змінні — у RW-пам'ять (RAM).",
              11, INK, "middle", "bold")
    save("fig-19-2-2-regions.svg", s)


# ── Рис. 19.2.3 — стек і купа ростуть назустріч ────────────────────────────
def fig192_grow():
    W, H = 880, 424
    s = header(W, H)
    s += text(W / 2, 34, "Стек і купа ростуть НАЗУСТРІЧ — щоб ділити один вільний простір", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "обидва міняються в розмірі по ходу програми, тож їх ставлять з протилежних кінців вільної пам'яті",
              11.5, GREY, "middle", style="italic")
    bx, bw = 320, 240
    s += rect(bx, 90, bw, 56, "#fdf4f4", RED, 1.8, 0)
    s += text(bx + bw / 2, 114, "СТЕК", 13, RED, "middle", "bold")
    s += text(bx + bw / 2, 132, "виклики, локальні", 9.5, GREY, "middle")
    s += arrow(bx + bw / 2, 150, bx + bw / 2, 200, RED, 2.4)
    s += text(bx + bw / 2 + 14, 178, "росте вниз", 10, RED, "start", "bold")
    s += rect(bx, 210, bw, 70, "#f6f8f6", GREY, 1.5, 0)
    s += text(bx + bw / 2, 250, "вільний простір", 12, GREY, "middle", "bold")
    s += arrow(bx + bw / 2, 340, bx + bw / 2, 290, AMBER, 2.4)
    s += text(bx + bw / 2 + 14, 318, "росте вгору", 10, "#9a7322", "start", "bold")
    s += rect(bx, 344, bw, 56, "#fff8e8", AMBER, 1.8, 0)
    s += text(bx + bw / 2, 368, "КУПА", 13, "#9a7322", "middle", "bold")
    s += text(bx + bw / 2, 386, "динамічні дані", 9.5, GREY, "middle")
    # пояснення
    s += rect(600, 120, 260, 240, "#f4f7f4", GREEN, 1.6, 10)
    s += text(730, 146, "Чому назустріч?", 12.5, GREEN, "middle", "bold")
    for i, t in enumerate(["• обидва міняють розмір на льоту", "• наперед не знати, кому скільки треба",
                           "• з протилежних кінців кожен бере", "   стільки, скільки треба, з ОДНОГО",
                           "   спільного запасу — гнучко", "", "• небезпека: якщо вони ЗІЙДУТЬСЯ —",
                           "   зіткнення (переповнення, §19.7)"]):
        col = RED if i >= 6 else INK
        s += text(620, 172 + i * 23, t, 10.3, col, "start", "bold" if i >= 6 else "normal")
    s += text(W / 2, 416, "Поки між ними є вільне місце — усе гаразд. Біда, коли стек дороста до купи (або навпаки): про це §19.7.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-2-3-grow.svg", s)


# ── Рис. 19.2.4 — карта пам'яті мікроконтролера ────────────────────────────
def fig192_mcu():
    W, H = 900, 452
    s = header(W, H)
    s += text(W / 2, 34, "На мікроконтролері: окремі діапазони — Flash, RAM, периферія", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у МК різні види пам'яті лежать у РІЗНИХ діапазонах адрес — і навіть периферія виглядає як «пам'ять»",
              11.5, GREY, "middle", style="italic")
    blocks = [
        ("0x4000_0000", "ПЕРИФЕРІЯ (регістри)", "не пам'ять, а керування залізом:\nGPIO, таймери, UART… (§20.3)", AMBER, "#fff8e8"),
        ("0x2000_0000", "RAM (SRAM)", ".data · .bss · купа · стек\nтимчасова, летка (§19.3)", BLUE, "#f3f5fd"),
        ("0x0000_0000", "FLASH", ".text (код) · .rodata (сталі)\nпостійна, нелетка (§19.3)", GREEN, "#eef7ee"),
    ]
    for i, (addr, name, desc, col, bg) in enumerate(blocks):
        y = 92 + i * 104
        s += rect(250, y, 400, 88, bg, col, 2, 10)
        s += text(450, y + 28, name, 14, col, "middle", "bold")
        for j, ln in enumerate(desc.split("\n")):
            s += text(450, y + 50 + j * 18, ln, 10.5, INK, "middle")
        s += text(238, y + 44, addr, 10.5, GREY, "end", "bold")
    s += text(155, 110, "висока", 10, GREY, "middle")
    s += text(155, 400, "0x0", 10, GREY, "middle")
    s += text(700, 136, "← залізо, не RAM", 10, "#9a7322", "start", "bold")
    s += text(700, 240, "← змінні", 10, BLUE, "start", "bold")
    s += text(700, 344, "← програма", 10, GREEN, "start", "bold")
    s += text(W / 2, 432, "Це і є Гарвардський поділ (§18.7), видимий у карті: код у Flash, дані в RAM, а периферія — окремий діапазон адрес.",
              11, INK, "middle", "bold")
    save("fig-19-2-4-mcu.svg", s)


# ── Рис. 19.2.5 — пам'ять-відображений ввід-вивід ──────────────────────────
def fig192_mmio():
    W, H = 900, 432
    s = header(W, H)
    s += text(W / 2, 34, "Пам'ять-відображений ввід-вивід: керувати залізом — як писати в пам'ять", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "деякі адреси — це не комірки RAM, а РЕГІСТРИ периферії; запис у них керує залізом тими самими LD/ST (§18.8)",
              11.5, GREY, "middle", style="italic")
    s += rect(70, 130, 170, 90, "#fdf4f4", RED, 2, 12)
    s += text(155, 170, "ПРОЦЕСОР", 12.5, RED, "middle", "bold")
    s += text(155, 192, "ST 1 → 0x4001_0004", 9.5, INK, "middle", "bold")
    s += arrow(242, 175, 360, 175, BLUE, 2.4)
    s += text(301, 165, "та сама команда", 9, GREY, "middle")
    s += text(301, 192, "ЗАПИСУ, що й у RAM", 9, GREY, "middle")
    s += rect(360, 130, 220, 90, "#fff8e8", AMBER, 2, 12)
    s += text(470, 156, "регістр GPIO", 12, "#9a7322", "middle", "bold")
    s += text(470, 178, "за адресою 0x4001_0004", 9.5, GREY, "middle")
    s += text(470, 200, "(це не пам'ять — це залізо!)", 9.5, GREY, "middle", style="italic")
    s += arrow(582, 175, 680, 175, AMBER, 2.4)
    s += circle(740, 175, 26, "#fff6c0", AMBER, 2)
    s += text(740, 180, "💡", 20, INK, "middle")
    s += text(740, 222, "світлодіод засвітився", 10, "#9a7322", "middle", "bold")
    s += rect(60, 252, W - 120, 100, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 276, "Геніальна простота: периферію «підвісили» на адреси, тож процесору не треба ОКРЕМИХ команд вводу-виводу —", 11.5, INK, "middle", "bold")
    s += text(W / 2, 298, "він керує залізом тими самими читанням і записом (§18.8), що й пам'яттю. Записав у потрібну адресу — увімкнув пристрій.", 11.5, INK, "middle", "bold")
    s += text(W / 2, 324, "Ось чому в коді для МК ви «пишете в регістр», щоб засвітити ніжку чи запустити таймер. Детально — у Розділі 20 (§20.3).", 11, INK, "middle", "bold")
    s += text(W / 2, 350, "Тому й карта пам'яті МК містить діапазон периферії: ті адреси ведуть не до RAM, а до органів керування чипом.", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, 392, "Обережно: помилкова адреса може випадково «торкнутися» периферії — ще одна причина тримати карту пам'яті в голові.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 414, "(і причина, чому деякі змінні позначають volatile — щоб компілятор не «оптимізував» доступ до залізних регістрів; це Розділ 23)",
              9.5, GREY, "middle", style="italic")
    save("fig-19-2-5-mmio.svg", s)


# ═══════════ §19.3 — Flash vs RAM ═══════════════════════════════════════════
# ── Рис. 19.3.1 — летка vs нелетка ─────────────────────────────────────────
def fig193_volatile():
    W, H = 900, 416
    s = header(W, H)
    s += text(W / 2, 34, "Головний поділ пам'яті: летка (RAM) vs нелетка (Flash)", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "чи пам'ятає вона дані БЕЗ живлення? RAM забуває все при вимкненні; Flash зберігає",
              11.5, GREY, "middle", style="italic")
    # RAM
    s += rect(70, 92, 380, 230, "#f3f5fd", BLUE, 2, 12)
    s += text(260, 116, "RAM — ЛЕТКА (volatile)", 13, BLUE, "middle", "bold")
    s += rect(100, 134, 150, 70, "#ffffff", GREEN, 1.6, 8)
    s += text(175, 158, "живлення ON", 10.5, GREEN, "middle", "bold")
    s += text(175, 180, "дані: 0x41 ✓", 11, INK, "middle", "bold")
    s += arrow(258, 169, 308, 169, INK, 2)
    s += rect(316, 134, 120, 70, "#fdf6f6", RED, 1.6, 8)
    s += text(376, 158, "OFF", 10.5, RED, "middle", "bold")
    s += text(376, 180, "пусто ✗", 11, RED, "middle", "bold")
    s += text(260, 232, "як дошка, що стирається, щойно згасне світло", 10, GREY, "middle", style="italic")
    s += text(260, 256, "тримає біт, лише поки тече струм — як тригер (§16)", 10, INK, "middle", "bold")
    s += text(260, 280, "робоча пам'ять: змінні, стек, купа", 10.5, BLUE, "middle", "bold")
    s += text(260, 302, "(дешевша на біт, дуже швидка)", 9.5, GREY, "middle", style="italic")
    # Flash
    s += rect(450, 92, 380, 230, "#eef7ee", GREEN, 2, 12)
    s += text(640, 116, "Flash — НЕЛЕТКА (non-volatile)", 12.5, GREEN, "middle", "bold")
    s += rect(480, 134, 150, 70, "#ffffff", GREEN, 1.6, 8)
    s += text(555, 158, "живлення ON", 10.5, GREEN, "middle", "bold")
    s += text(555, 180, "дані: код ✓", 11, INK, "middle", "bold")
    s += arrow(638, 169, 688, 169, INK, 2)
    s += rect(696, 134, 120, 70, "#eef7ee", GREEN, 1.6, 8)
    s += text(756, 158, "OFF", 10.5, GREEN, "middle", "bold")
    s += text(756, 180, "код ✓ ціле!", 10.5, GREEN, "middle", "bold")
    s += text(640, 232, "як чорнило на папері — лишається без живлення", 10, GREY, "middle", style="italic")
    s += text(640, 256, "пам'ятає фізично (заряд у плавучому затворі)", 10, INK, "middle", "bold")
    s += text(640, 280, "постійна пам'ять: програма, сталі", 10.5, GREEN, "middle", "bold")
    s += text(640, 302, "(тому ваш скетч лишається після вимкнення)", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, 356, "Ось чому програма «не зникає», коли ви від'єднуєте плату, а змінні обнуляються при кожному перезапуску:",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 380, "програма живе в нелеткій Flash, а змінні — в леткій RAM. Це найпрактичніший поділ у всій пам'яті.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 404, "(термін «летка»/«volatile» ще зустрінеться як ключове слово мови — Розділ 23 — та поки йдеться про фізику пам'яті)",
              9.5, GREY, "middle", style="italic")
    save("fig-19-3-1-volatile.svg", s)


# ── Рис. 19.3.2 — що куди: код у Flash, змінні в RAM ───────────────────────
def fig193_split():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Що куди: незмінне — у Flash, мінливе — в RAM", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "це фізичне пояснення поділу RO/RW із §19.2: властивості даних диктують, у якій пам'яті їм жити",
              11.5, GREY, "middle", style="italic")
    s += rect(70, 90, 380, 230, "#eef7ee", GREEN, 2, 12)
    s += text(260, 116, "FLASH (нелетка, повільніший запис)", 11.5, GREEN, "middle", "bold")
    for i, (t, d) in enumerate([(".text — КОД", "інструкції програми"), (".rodata — СТАЛІ", "рядки, таблиці")]):
        y = 134 + i * 56
        s += rect(96, y, 328, 46, "#ffffff", GREEN, 1.5, 8)
        s += text(116, y + 21, t, 12, GREEN, "start", "bold")
        s += text(116, y + 39, d, 10, GREY, "start")
    s += text(260, 268, "чому сюди:", 10.5, INK, "middle", "bold")
    s += text(260, 288, "• не міняються під час роботи", 10, INK, "middle")
    s += text(260, 306, "• мусять пережити вимкнення", 10, INK, "middle")
    s += rect(450, 90, 380, 230, "#f3f5fd", BLUE, 2, 12)
    s += text(640, 116, "RAM (летка, швидка, побайтна)", 11.5, BLUE, "middle", "bold")
    for i, (t, d) in enumerate([(".data / .bss — ГЛОБАЛЬНІ", "змінні стану програми"),
                                ("стек і купа", "локальні, динамічні (§19.5–6)")]):
        y = 134 + i * 56
        s += rect(476, y, 328, 46, "#ffffff", BLUE, 1.5, 8)
        s += text(496, y + 21, t, 12, BLUE, "start", "bold")
        s += text(496, y + 39, d, 10, GREY, "start")
    s += text(640, 268, "чому сюди:", 10.5, INK, "middle", "bold")
    s += text(640, 288, "• міняються постійно (потрібен швидкий запис)", 10, INK, "middle")
    s += text(640, 306, "• тимчасові — не шкода, що зникнуть", 10, INK, "middle")
    s += text(W / 2, 352, "Правило просте: незмінне й цінне (код, сталі) — у нелетку Flash; мінливе й тимчасове (змінні) — у швидку RAM.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 378, "Це й була причина групування RO/RW у карті §19.2 — фізика двох пам'ятей диктує, де чому місце.",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 402, "На МК RAM зазвичай МІЗЕРНА (кілобайти), а Flash більша — тож великі сталі таблиці тримають у Flash, щоб берегти RAM.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-3-2-split.svg", s)


# ── Рис. 19.3.3 — примхи Flash: блоки, знос, повільний запис ───────────────
def fig193_quirks():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Чому Flash не годиться для частих змін: примхи запису", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "читати з Flash легко й швидко, але ПИСАТИ — складно: лише цілими блоками, повільно й обмежену кількість разів",
              11.5, GREY, "middle", style="italic")
    # RAM
    s += rect(70, 88, 360, 150, "#f3f5fd", BLUE, 1.8, 12)
    s += text(250, 112, "RAM — пише легко", 13, BLUE, "middle", "bold")
    for i, t in enumerate(["• будь-який ОКРЕМИЙ байт — одразу", "• швидко (за такти)",
                           "• скільки завгодно разів", "• ідеально для змінних, що весь час міняються"]):
        s += text(92, 138 + i * 24, t, 11, INK, "start")
    # Flash
    s += rect(470, 88, 360, 150, "#fff8e8", AMBER, 1.8, 12)
    s += text(650, 112, "Flash — пише важко", 13, "#9a7322", "middle", "bold")
    for i, t in enumerate(["• лише цілими БЛОКАМИ (не байтом)", "• спершу СТЕРТИ блок (усе → 1), тоді писати (1 → 0)",
                           "• повільно (мікро-мілісекунди)", "• ЗНОС: ~10 000–100 000 циклів на блок"]):
        s += text(492, 138 + i * 24, t, 10.3, INK, "start")
    # блок стирання
    s += text(160, 268, "запис у Flash:", 11, "#9a7322", "start", "bold")
    s += text(300, 300, "стерти весь блок", 10, RED, "middle", "bold")
    s += rect(220, 310, 160, 26, "#fdecec", RED, 1.4, 4)
    s += text(300, 328, "1 1 1 1 1 1 1 1", 11, RED, "middle", "bold")
    s += arrow(390, 323, 450, 323, INK, 2)
    s += text(560, 300, "тоді записати потрібні 0", 10, GREEN, "middle", "bold")
    s += rect(480, 310, 160, 26, "#eef7ee", GREEN, 1.4, 4)
    s += text(560, 328, "1 0 1 1 0 0 1 0", 11, INK, "middle", "bold")
    s += rect(60, 354, W - 120, 76, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 378, "Тому Flash чудова для коду (записав раз при прошивці — читай мільйони разів), та погана для даних, що весь час міняються:",
              11, INK, "middle", "bold")
    s += text(W / 2, 400, "лічильник, що пише у Flash щосекунди, «зносить» блок за лічені дні. Часті зміни — робота для RAM (а збереження налаштувань — обережно).",
              11, INK, "middle", "bold")
    s += text(W / 2, 422, "(До речі, так само влаштовані SSD й флешки — звідси їхній «знос» і потреба в рівномірному розподілі записів.)",
              9.5, GREY, "middle", style="italic")
    save("fig-19-3-3-quirks.svg", s)


# ── Рис. 19.3.4 — старт: копія .data з Flash у RAM ─────────────────────────
def fig193_startup():
    W, H = 900, 432
    s = header(W, H)
    s += text(W / 2, 34, "Тонкість запуску: як глобальні змінні дістають початкові значення", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "початкові значення мусять пережити вимкнення (отже, у Flash) — та змінні мінливі (отже, в RAM). Розв'язок: копія при старті",
              11.5, GREY, "middle", style="italic")
    # Flash
    s += rect(90, 100, 300, 200, "#eef7ee", GREEN, 2, 12)
    s += text(240, 124, "FLASH (нелетка)", 12.5, GREEN, "middle", "bold")
    s += rect(112, 140, 256, 36, "#ffffff", GREEN, 1.4, 6)
    s += text(124, 163, ".text — код (виконується тут)", 10.5, INK, "start", "bold")
    s += rect(112, 184, 256, 36, "#ffffff", GREEN, 1.4, 6)
    s += text(124, 207, ".rodata — сталі (читаються тут)", 10.5, INK, "start", "bold")
    s += rect(112, 228, 256, 36, "#fff8e8", AMBER, 1.4, 6)
    s += text(124, 251, "початкові значення .data", 10.5, "#9a7322", "start", "bold")
    s += text(240, 286, "усе це пережило вимкнення", 9.5, GREY, "middle", style="italic")
    # RAM
    s += rect(510, 100, 300, 200, "#f3f5fd", BLUE, 2, 12)
    s += text(660, 124, "RAM (летка)", 12.5, BLUE, "middle", "bold")
    s += rect(532, 184, 256, 36, "#fff8e8", AMBER, 1.4, 6)
    s += text(660, 207, ".data (вже з копією значень)", 10.5, "#9a7322", "middle", "bold")
    s += rect(532, 228, 256, 36, "#f3f5fd", BLUE, 1.4, 6)
    s += text(660, 251, ".bss → обнулено", 10.5, BLUE, "middle", "bold")
    # стрілки
    s += arrow(372, 246, 528, 202, AMBER, 2.4)
    s += text(450, 214, "КОПІЯ при старті", 10, "#9a7322", "middle", "bold")
    s += arrow(660, 300, 660, 268, BLUE, 2, "3 3")
    s += text(660, 318, "обнуляється на старті", 9, BLUE, "middle")
    s += rect(60, 332, W - 120, 92, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 356, "Перед запуском main() крихітний стартовий код КОПІЮЄ початкові значення .data з Flash у RAM і ОБНУЛЯЄ .bss.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 378, "Тому глобальна змінна щоразу стартує зі свого початкового значення — воно зберігалося у Flash і скопіювалося в RAM.",
              11, INK, "middle", "bold")
    s += text(W / 2, 402, "Як саме це робить тулчейн (стартовий код, секції) — Розділ 21; тут досить розуміти ЧОМУ потрібна ця копія.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-3-4-startup.svg", s)


# ── Рис. 19.3.5 — родина пам'ятей ──────────────────────────────────────────
def fig193_zoo():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Родина пам'ятей: хто летка, хто ні, і де яку вживають", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "видів пам'яті багато, та для мікроконтролера головні дві — Flash (програма) і SRAM (змінні)",
              11.5, GREY, "middle", style="italic")
    s += rect(60, 82, 110, 28, "#eef0f4", INK, 1.2, 6)
    s += text(115, 101, "тип", 11.5, INK, "middle", "bold")
    s += text(280, 101, "летка?", 11, INK, "middle", "bold")
    s += text(470, 101, "особливості", 11, INK, "middle", "bold")
    s += text(740, 101, "де вживають", 11, INK, "middle", "bold")
    rows = [
        ("SRAM", "летка", "дуже швидка; комірка ≈ тригер (§16)", "робоча RAM МК, кеші", BLUE),
        ("DRAM", "летка", "щільна, потребує освіження (заряд стікає)", "головна пам'ять ПК", BLUE),
        ("Flash", "НЕлетка", "читання швидке; запис блоками, знос", "програма МК, SSD, флешки", GREEN),
        ("EEPROM", "НЕлетка", "повільна, зате побайтна", "малі налаштування на МК", GREEN),
        ("ROM", "НЕлетка", "тільки читання, вшите назавжди", "незмінні дані, заводський код", AMBER),
    ]
    for i, (t, vol, feat, use, col) in enumerate(rows):
        y = 116 + i * 50
        s += rect(60, y, 110, 44, "#fafafa", col, 1.5, 6)
        s += text(115, y + 27, t, 12.5, col, "middle", "bold")
        s += rect(180, y, 150, 44, "#fdf6f6" if vol == "летка" else "#eef7ee", RED if vol == "летка" else GREEN, 1.3, 6)
        s += text(255, y + 27, vol, 11, RED if vol == "летка" else GREEN, "middle", "bold")
        s += rect(340, y, 300, 44, "#ffffff", GREY, 1, 6)
        s += text(350, y + 27, feat, 10, INK, "start")
        s += rect(650, y, 190, 44, "#ffffff", col, 1.2, 6)
        s += text(745, y + 27, use, 9.5, INK, "middle")
    s += text(W / 2, 404, "Для нас практично: на МК — Flash тримає прошиту програму, SRAM тримає змінні під час роботи. Решта — за потреби.",
              11, INK, "middle", "bold")
    save("fig-19-3-5-zoo.svg", s)


# ═══════════ §19.4 — Адреси й покажчики ═════════════════════════════════════
# ── Рис. 19.4.1 — що таке покажчик ─────────────────────────────────────────
def fig194_pointer():
    W, H = 900, 412
    s = header(W, H)
    s += text(W / 2, 34, "Покажчик — це змінна, значення якої є АДРЕСОЮ іншої змінної", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "він не містить самих даних — він «вказує» на них, тримаючи їхню адресу (пряме продовження §19.1)",
              11.5, GREY, "middle", style="italic")
    # покажчик p
    s += text(225, 110, "покажчик p", 12, RED, "middle", "bold")
    s += _cell(170, 124, "0x10", "0x20", w=140, h=40, hl=True)
    s += text(240, 184, "значення p = 0x20 (адреса!)", 10, GREY, "middle", style="italic")
    # змінна x
    s += text(670, 110, "змінна x", 12, GREEN, "middle", "bold")
    s += rect(600, 124, 140, 40, "#eef7ee", GREEN, 2, 4)
    s += text(590, 148, "0x20", 11, GREY, "end", "bold")
    s += text(670, 150, "42", 14, INK, "middle", "bold")
    s += text(670, 184, "значення x = 42 (самі дані)", 10, GREY, "middle", style="italic")
    # стрілка p -> x
    s += path("M312,144 C 420,144 480,144 598,144", "none", RED, 2.4)
    s += text(455, 132, "p вказує на x", 11, RED, "middle", "bold")
    s += circle(598, 144, 3, RED, RED, 1)
    s += rect(60, 224, W - 120, 100, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 248, "Дві різні комірки: у x лежать ДАНІ (42), у p лежить АДРЕСА, де ті дані (0x20). p «знає, де» x, не тримаючи його значення.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 270, "Це і є непрямість (indirection): замість самого значення тримаємо ВКАЗІВКУ, де його знайти. Просте, та страшенно потужне.",
              11, INK, "middle", "bold")
    s += text(W / 2, 296, "Пам'ятаєте §19.1 — «адреса проти даних»? Покажчик робить саму адресу повноцінною даниною: її можна зберігати, копіювати, передавати.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 360, "Записують так: p — це «адреса x», а сам x дістають, «пішовши за покажчиком». Дві операції — нижче.",
              11, INK, "middle", "bold")
    save("fig-19-4-1-pointer.svg", s)


# ── Рис. 19.4.2 — дві операції: «адреса від» і «розіменування» ─────────────
def fig194_ops():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Дві операції з покажчиками: взяти адресу й піти за нею", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "«&x» дає адресу змінної x; «*p» іде за адресою в p і дістає (чи міняє) значення там — вони зворотні",
              11.5, GREY, "middle", style="italic")
    # &x
    s += rect(70, 92, 360, 130, "#f3f5fd", BLUE, 1.8, 12)
    s += text(250, 116, "& — «адреса від» (address-of)", 12, BLUE, "middle", "bold")
    s += text(250, 144, "&x  →  0x20", 15, INK, "middle", "bold")
    s += text(250, 170, "«дай мені, ДЕ лежить x»", 10.5, GREY, "middle")
    s += text(250, 196, "так покажчик і дістає адресу: p = &x", 10.5, BLUE, "middle", "bold")
    # *p
    s += rect(470, 92, 360, 130, "#eef7ee", GREEN, 1.8, 12)
    s += text(650, 116, "* — «розіменування» (dereference)", 11.5, GREEN, "middle", "bold")
    s += text(650, 144, "*p  →  42", 15, INK, "middle", "bold")
    s += text(650, 170, "«піди за p і візьми значення там»", 10.5, GREY, "middle")
    s += text(650, 196, "*p = 99  ←  так МІНЯЮТЬ x через p", 10.5, GREEN, "middle", "bold")
    # зворотність
    s += arrow(300, 250, 560, 250, INK, 2)
    s += text(430, 240, "&  (взяти адресу)", 10.5, BLUE, "middle", "bold")
    s += arrow(560, 280, 300, 280, INK, 2)
    s += text(430, 300, "*  (піти за адресою)", 10.5, GREEN, "middle", "bold")
    s += text(150, 250, "x", 14, INK, "middle", "bold")
    s += text(150, 280, "значення", 9.5, GREY, "middle")
    s += text(710, 250, "p", 14, RED, "middle", "bold")
    s += text(710, 280, "адреса", 9.5, GREY, "middle")
    s += rect(60, 330, W - 120, 76, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 354, "& і * — зворотні: & веде від значення до його адреси, * — від адреси назад до значення. *(&x) — це знову x.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 376, "Через *p можна не лише ЧИТАТИ чуже значення, а й ПИСАТИ його — ось чому функція, маючи адресу, здатна змінити вашу змінну.",
              11, INK, "middle", "bold")
    s += text(W / 2, 398, "(синтаксис & і * — з мови C; тут важлива сама ідея «взяти адресу» / «піти за адресою», а не значки)",
              9.5, GREY, "middle", style="italic")
    save("fig-19-4-2-ops.svg", s)


# ── Рис. 19.4.3 — покажчик — це просто число ───────────────────────────────
def fig194_number():
    W, H = 880, 396
    s = header(W, H)
    s += text(W / 2, 34, "Покажчик — це просто ЧИСЛО (адреса); тип каже, на ЩО він вказує", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "сам покажчик — лише адреса-число (§17.1, §19.1); його «тип» потрібен компілятору, щоб знати розмір і крок",
              11.5, GREY, "middle", style="italic")
    s += _cell(360, 96, "0x10", "0x00002004", w=200, h=44, hl=True)
    s += text(460, 158, "вміст покажчика — просто 32-бітне число (адреса)", 10.5, GREY, "middle", style="italic")
    s += text(460, 178, "на 32-бітній машині покажчик займає 4 байти", 10.5, INK, "middle", "bold")
    s += rect(120, 210, 300, 96, "#f3f5fd", BLUE, 1.6, 10)
    s += text(270, 234, "«тип» покажчика", 12, BLUE, "middle", "bold")
    s += text(270, 258, "int*  — вказує на 4-байтне ціле", 10.5, INK, "middle")
    s += text(270, 278, "char* — вказує на 1 байт", 10.5, INK, "middle")
    s += text(270, 298, "(каже, скільки читати й який крок)", 9.5, GREY, "middle", style="italic")
    rect_note = "#fff8e8"
    s += rect(460, 210, 300, 96, rect_note, AMBER, 1.6, 10)
    s += text(610, 234, "крок під час обходу", 12, "#9a7322", "middle", "bold")
    s += text(610, 258, "p+1 для int* зсуває на 4 байти", 10.5, INK, "middle")
    s += text(610, 278, "p+1 для char* — на 1 байт", 10.5, INK, "middle")
    s += text(610, 298, "(бо «крок» = розмір того, на що вказує)", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, 340, "Тож покажчик — це адреса-число плюс ЗНАННЯ про те, на що вона показує. Саме число — як будь-яке інше (§17.1).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 366, "Через це покажчики й бувають 16-, 32- чи 64-бітні — рівно стільки, скільки треба, щоб умістити адресу (§19.1).",
              10.5, GREY, "middle", style="italic")
    save("fig-19-4-3-number.svg", s)


# ── Рис. 19.4.4 — аналогія: адреса на папірці ──────────────────────────────
def fig194_analogy():
    W, H = 900, 438
    s = header(W, H)
    s += text(W / 2, 34, "Точна аналогія: покажчик — це адреса будинку на папірці", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "папірець з адресою — це не сам будинок; він лише каже, ДЕ будинок (згадайте «вулицю» з §19.1)",
              11.5, GREY, "middle", style="italic")
    # папірець
    s += rect(90, 100, 150, 90, "#fffdf5", AMBER, 2, 8)
    s += text(165, 128, "папірець", 11, "#9a7322", "middle", "bold")
    s += text(165, 152, "вул. Пам'яті,", 10.5, INK, "middle")
    s += text(165, 170, "буд. 0x20", 11, INK, "middle", "bold")
    s += text(165, 206, "= покажчик", 10, RED, "middle", "bold")
    s += arrow(244, 145, 320, 145, INK, 2.2)
    # будинок
    s += rect(330, 105, 130, 80, "#eef7ee", GREEN, 2, 8)
    s += text(395, 140, "🏠 будинок", 12, INK, "middle", "bold")
    s += text(395, 162, "(самі дані: 42)", 9.5, GREY, "middle")
    s += text(395, 200, "= змінна x", 10, GREEN, "middle", "bold")
    # три дії
    actions = [("копіювати папірець", "два папірці → той самий будинок (два покажчики на ті самі дані)", GREEN),
               ("дати другові", "він піде за адресою й навіть перефарбує будинок (функція змінить ваші дані)", BLUE),
               ("піти за адресою", "дістатися будинку = розіменування (*p)", AMBER)]
    for i, (a, d, col) in enumerate(actions):
        y = 240 + i * 40
        s += rect(70, y, 250, 34, "#fafafa", col, 1.5, 6)
        s += text(195, y + 22, a, 11, col, "middle", "bold")
        s += text(335, y + 22, d, 10, INK, "start")
    s += rect(540, 100, 300, 86, "#fdf6f6", RED, 1.6, 10)
    s += text(690, 124, "Де аналогія ламається", 12, RED, "middle", "bold")
    s += text(560, 146, "папірець зі СТАРОЮ чи хибною адресою", 10, INK, "start")
    s += text(560, 164, "веде до знесеного чи чужого будинку —", 10, INK, "start")
    s += text(560, 180, "це «висячий»/«дикий» покажчик (далі)", 10, RED, "start", "bold")
    s += text(W / 2, 414, "Папірець (адреса) — повноцінна річ: його можна копіювати, передавати, загубити. Але користь з нього лише тоді, коли адреса ПРАВИЛЬНА.",
              10.5, INK, "middle", "bold")
    save("fig-19-4-4-analogy.svg", s)


# ── Рис. 19.4.5 — навіщо покажчики ─────────────────────────────────────────
def fig194_uses():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо покажчики: чотири головні застосування", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "непрямість дає те, чого інакше не зробити: дешево ділитися даними, міняти чуже, обходити пам'ять, будувати структури",
              11.5, GREY, "middle", style="italic")
    uses = [
        ("Передати без копіювання", "велику таблицю чи структуру передають за АДРЕСОЮ (4 байти),", "а не копіюють цілком — швидко й економно", BLUE),
        ("Змінити чужу змінну", "функція, діставши адресу вашої змінної, може ЗАПИСАТИ в неї", "(через *p) — так повертають результат «назовні»", GREEN),
        ("Пройти масив/пам'ять", "покажчик, що збільшується (p+1, p+2…), КРОКУЄ по сусідніх", "комірках (§19.1) — природний спосіб обходу", AMBER),
        ("Зв'язані структури", "комірка тримає адресу наступної → списки, дерева, графи;", "вузли «вказують» один на одного — гнучкі форми", RED),
    ]
    for i, (t, d1, d2, col) in enumerate(uses):
        y = 90 + i * 80
        s += rect(70, y, 760, 68, "#fafafa", col, 1.7, 10)
        s += text(92, y + 28, t, 13, col, "start", "bold")
        s += text(360, y + 24, d1, 10.5, INK, "start")
        s += text(360, y + 46, d2, 10.5, GREY, "start")
    s += text(W / 2, 424, "Усе це — наслідки однієї ідеї: тримати не саме значення, а ВКАЗІВКУ на нього. Тому покажчики всюди в системному коді.",
              11, INK, "middle", "bold")
    save("fig-19-4-5-uses.svg", s)


# ── Рис. 19.4.6 — небезпеки покажчиків ─────────────────────────────────────
def fig194_dangers():
    W, H = 900, 452
    s = header(W, H)
    s += text(W / 2, 34, "Інший бік: покажчики — джерело найгрізніших багів", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "сила непрямості має ціну: покажчик, що вказує «не туди», тихо псує пам'ять або валить програму",
              11.5, GREY, "middle", style="italic")
    dangers = [
        ("Нульовий (null)", "вказує «в нікуди» (адреса 0)", "піти за ним → аварія (crash)", RED),
        ("Висячий (dangling)", "вказує на пам'ять, що вже НЕдійсна", "(звільнена/вийшла з області) → сміття", AMBER),
        ("Дикий (wild)", "неініціалізований — містить ВИПАДКОВУ адресу", "піти за ним → псує випадкову пам'ять", RED),
    ]
    for i, (t, d1, d2, col) in enumerate(dangers):
        y = 88 + i * 64
        s += rect(70, y, 760, 54, "#fdf6f6" if col == RED else "#fff8e8", col, 1.7, 10)
        s += text(92, y + 23, t, 12.5, col, "start", "bold")
        s += text(300, y + 22, d1, 10.5, INK, "start")
        s += text(300, y + 41, d2, 10.5, GREY, "start")
    s += rect(60, 290, W - 120, 110, "#fdf6f6", RED, 1.7, 10)
    s += text(W / 2, 314, "Особливо небезпечно на МК: там зазвичай НЕМАЄ захисту пам'яті, тож хибний покажчик може «надряпати»", 11.5, INK, "middle", "bold")
    s += text(W / 2, 336, "поверх коду, чужих даних або навіть РЕГІСТРІВ ПЕРИФЕРІЇ (§19.2 — вони ж на адресах!) — і чип поведеться загадково.", 11.5, INK, "middle", "bold")
    s += text(W / 2, 362, "Корінь біди завжди той самий: плутанина «адреса проти значення» (§19.1) або покажчик, що показує кудись не туди.", 11, INK, "middle", "bold")
    s += text(W / 2, 384, "Тому з покажчиками потрібна дисципліна: ініціалізуй, перевіряй на null, не тримай після звільнення (типові біди — §19.7).", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, 424, "Висновок: покажчик — гострий інструмент. Дає величезну силу непрямості, та вимагає акуратності, якої не пробачає.",
              11, INK, "middle", "bold")
    save("fig-19-4-6-dangers.svg", s)


# ═══════════ §19.5 — Стек: виклик функції ═══════════════════════════════════
def _frame(x, y, w, name, col, bg, rows=None, hl=False):
    h = 26 + (len(rows) * 18 if rows else 0)
    out = rect(x, y, w, h, bg, col, 2.2 if hl else 1.6, 6)
    out += text(x + w / 2, y + 17, name, 11.5, col, "middle", "bold")
    if rows:
        for i, r in enumerate(rows):
            out += text(x + 10, y + 34 + i * 18, r, 9, INK, "start")
    return out, h


# ── Рис. 19.5.1 — проблема вкладених викликів ──────────────────────────────
def fig195_problem():
    W, H = 900, 408
    s = header(W, H)
    s += text(W / 2, 34, "Проблема: функція викликає функцію — і так у глибину", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "при кожному виклику треба пам'ятати, КУДИ повертатися, і дати функції місце під її локальні змінні",
              11.5, GREY, "middle", style="italic")
    boxes = [("main()", "викликає f()", GREEN, 90),
             ("f()", "викликає g()", BLUE, 330),
             ("g()", "викликає h()…", AMBER, 570)]
    for name, act, col, x in boxes:
        s += rect(x, 110, 200, 80, "#fafafa", col, 1.8, 10)
        s += text(x + 100, 140, name, 14, col, "middle", "bold")
        s += text(x + 100, 164, act, 10.5, GREY, "middle")
        s += text(x + 100, 182, "+ свої локальні", 9.5, INK, "middle")
    s += arrow(292, 150, 328, 150, INK, 2.2)
    s += arrow(532, 150, 568, 150, INK, 2.2)
    s += text(790, 150, "… і глибше", 11, GREY, "start", style="italic")
    s += rect(60, 222, W - 120, 110, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 246, "Кожна функція мусить: 1) запам'ятати АДРЕСУ ПОВЕРНЕННЯ — куди продовжити того, хто її викликав;",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 268, "2) мати власне місце під параметри й ЛОКАЛЬНІ змінні. І так на будь-яку глибину вкладеності.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 294, "Ключове спостереження: хто викликаний ОСТАННІМ — повертається ПЕРШИМ (g завершиться раніше за f, f — раніше за main).",
              11, INK, "middle", "bold")
    s += text(W / 2, 316, "Така поведінка «останній прийшов — перший пішов» має ідеальну структуру даних. Її звуть стеком.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 366, "Без такого механізму неможливі ні вкладені виклики, ні рекурсія, ні навіть звичайне повернення з функції.",
              11, INK, "middle", "bold")
    save("fig-19-5-1-problem.svg", s)


# ── Рис. 19.5.2 — стек = LIFO (стос тарілок) ───────────────────────────────
def fig195_lifo():
    W, H = 900, 416
    s = header(W, H)
    s += text(W / 2, 34, "Стек — структура «останній прийшов, перший пішов» (LIFO)", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "як стос тарілок: кладеш зверху (push) і береш зверху (pop); останнє покладене знімається першим",
              11.5, GREY, "middle", style="italic")
    # стос тарілок
    plates = ["g", "f", "main"]
    for i, p in enumerate(plates):
        y = 220 - i * 34
        col = [AMBER, BLUE, GREEN][i]
        s += rect(150, y, 200, 28, "#fafafa", col, 1.8, 14)
        s += text(250, y + 19, f"кадр {p}()", 11, col, "middle", "bold")
    s += text(250, 250, "стос (стек)", 10.5, GREY, "middle", style="italic")
    s += arrow(370, 130, 410, 130, GREEN, 2.4)
    s += text(450, 126, "push: покласти зверху", 10.5, GREEN, "start", "bold")
    s += arrow(410, 170, 370, 170, RED, 2.4)
    s += text(450, 166, "pop: зняти зверху", 10.5, RED, "start", "bold")
    s += rect(430, 196, 410, 130, "#f4f7f4", INK, 1.5, 10)
    s += text(635, 220, "Чому саме стек для викликів?", 12, INK, "middle", "bold")
    for i, t in enumerate(["• останній викликаний (g) — перший", "   повертається → знімаємо його кадр",
                           "• тоді f, тоді main — точно LIFO!", "• вкладені виклики й рекурсія", "   лягають на стек ідеально"]):
        s += text(450, 246 + i * 16, t, 10, INK, "start")
    s += text(W / 2, 356, "Порядок завершення викликів — рівно зворотний до порядку входу. Це і є LIFO, і саме тому виклики тримають у СТЕКУ.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 382, "Дві дії й усе: PUSH (увійшли у функцію — додали кадр) і POP (вийшли — зняли кадр). Просто й блискавично.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-5-2-lifo.svg", s)


# ── Рис. 19.5.3 — стековий кадр ────────────────────────────────────────────
def fig195_frame():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Стековий кадр: що саме кладе на стек один виклик", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен виклик додає «кадр» (frame) — пакет усього, що потрібно функції та для повернення з неї",
              11.5, GREY, "middle", style="italic")
    parts = [
        ("адреса повернення", "куди продовжити того, хто викликав (→ у PC при return)", RED),
        ("збережені регістри", "значення регістрів, які треба відновити після виклику", AMBER),
        ("параметри", "аргументи, передані функції", BLUE),
        ("локальні змінні", "власні змінні функції (живуть, поки вона працює)", GREEN),
    ]
    y0 = 100
    for i, (k, d, col) in enumerate(parts):
        y = y0 + i * 56
        s += rect(180, y, 260, 46, "#fafafa", col, 1.8, 8)
        s += text(310, y + 28, k, 12.5, col, "middle", "bold")
        s += text(460, y + 28, d, 10.5, INK, "start")
    s += line(150, y0, 150, y0 + 4 * 56 - 10, GREY, 1.6)
    s += text(120, y0 + 2 * 56, "один", 10.5, GREY, "middle", "bold")
    s += text(120, y0 + 2 * 56 + 16, "кадр", 10.5, GREY, "middle", "bold")
    s += text(W / 2, 348, "Увійшли у функцію — цей кадр ляг на стек (push); вийшли — кадр знявся (pop), і вся його пам'ять умить звільнилась.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 372, "Тому локальні змінні ще звуть «автоматичними»: вони самі з'являються при вході й самі зникають при виході — без турбот.",
              11, INK, "middle", "bold")
    s += text(W / 2, 398, "(точний склад кадру залежить від процесора й домовленості викликів — тут показано типову суть)",
              9.5, GREY, "middle", style="italic")
    save("fig-19-5-3-frame.svg", s)


# ── Рис. 19.5.4 — адреса повернення: push на виклику, pop у PC ──────────────
def fig195_returnaddr():
    W, H = 900, 424
    s = header(W, H)
    s += text(W / 2, 34, "Серце механізму: адреса повернення (як процесор «знає, куди назад»)", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "виклик КЛАДЕ адресу повернення на стек; «return» ЗНІМАЄ її назад у PC — і виконання продовжується там, де перервалось",
              11.5, GREY, "middle", style="italic")
    # виклик
    s += rect(70, 92, 360, 150, "#eef7ee", GREEN, 1.8, 12)
    s += text(250, 116, "ВИКЛИК  f()", 13, GREEN, "middle", "bold")
    s += text(90, 142, "main на адресі 0x44 викликає f", 10.5, INK, "start")
    s += text(90, 162, "процесор кладе на стек 0x45", 10.5, RED, "start", "bold")
    s += text(90, 178, "(адресу НАСТУПНОЇ команди main)", 9.5, GREY, "start")
    s += text(90, 204, "PC ← початок f  (стрибок, §18.2)", 10.5, INK, "start", "bold")
    s += text(90, 224, "→ виконуємо f", 10.5, GREEN, "start", "bold")
    # повернення
    s += rect(470, 92, 360, 150, "#f3f5fd", BLUE, 1.8, 12)
    s += text(650, 116, "RETURN з f", 13, BLUE, "middle", "bold")
    s += text(490, 142, "f завершилась, команда «return»", 10.5, INK, "start")
    s += text(490, 162, "процесор знімає зі стека 0x45", 10.5, RED, "start", "bold")
    s += text(490, 182, "PC ← 0x45", 11.5, INK, "start", "bold")
    s += text(490, 208, "→ main продовжується рівно там,", 10.5, BLUE, "start", "bold")
    s += text(490, 224, "де перервався", 10.5, BLUE, "start", "bold")
    s += arrow(432, 167, 468, 167, INK, 2.2)
    # стек у центрі
    s += rect(380, 260, 140, 40, "#fdf4f4", RED, 1.8, 6)
    s += text(450, 278, "стек:", 9.5, GREY, "middle")
    s += text(450, 294, "0x45 ↩", 12, RED, "middle", "bold")
    s += text(W / 2, 340, "Ось як виклик «пам'ятає дорогу назад»: адреса повернення лежить на стеку, доки функція працює, і повертається в PC при виході.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 364, "Це прямо спирається на PC (§18.2) і стрибки (§18.1): виклик — стрибок із запам'ятовуванням, повернення — стрибок за збереженою адресою.",
              11, INK, "middle", "bold")
    s += text(W / 2, 392, "І тут же причаїлася найгрізніша біда: зіпсуєш цю адресу на стеку (переповненням, §19.7) — і повернення піде «не туди».",
              10.5, GREY, "middle", style="italic")
    save("fig-19-5-4-returnaddr.svg", s)


# ── Рис. 19.5.5 — наскрізний прохід: main → f → g ──────────────────────────
def fig195_trace():
    W, H = 900, 432
    s = header(W, H)
    s += text(W / 2, 34, "Наскрізний прохід: стек росте при викликах і спадає при поверненнях", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "main викликає f, f викликає g; потім розкручується назад — кадри знімаються у зворотному порядку (LIFO)",
              11.5, GREY, "middle", style="italic")
    stages = [
        ("main працює", [("main", GREEN)]),
        ("main → f", [("main", GREEN), ("f", BLUE)]),
        ("f → g", [("main", GREEN), ("f", BLUE), ("g", AMBER)]),
        ("g повернулась", [("main", GREEN), ("f", BLUE)]),
        ("f повернулась", [("main", GREEN)]),
    ]
    sw = 168
    for i, (title, frames) in enumerate(stages):
        x = 40 + i * sw
        s += text(x + sw / 2 - 10, 92, title, 10.5, INK, "middle", "bold")
        baseY = 320
        for j, (nm, col) in enumerate(frames):
            fy = baseY - j * 36
            top = (j == len(frames) - 1)
            s += rect(x + 18, fy, 130, 30, "#fafafa", col, 2.2 if top else 1.4, 5)
            s += text(x + 83, fy + 20, f"{nm}()", 11, col, "middle", "bold")
            if top:
                s += text(x + 158, fy + 19, "←SP", 8.5, RED, "start", "bold")
        if i < 4:
            ico = "push ↑" if i < 2 else "pop ↓"
            icol = GREEN if i < 2 else RED
            s += text(x + sw - 6, 200, ico, 9, icol, "middle", "bold")
    s += text(W / 2, 360, "g (останній доданий) знімається ПЕРШИМ, тоді f. Вершину стека стежить покажчик стека SP (§18.2): push рухає його, pop вертає.",
              11, INK, "middle", "bold")
    s += text(W / 2, 384, "Зверніть увагу: пам'ять виділяється й звільняється САМА — просто рухом SP. Жодного ручного керування локальними.",
              11, INK, "middle", "bold")
    s += text(W / 2, 410, "(у пам'яті стек росте до НИЖЧИХ адрес — §19.2; тут «вершину» намальовано вгорі для наочності)",
              9.5, GREY, "middle", style="italic")
    save("fig-19-5-5-trace.svg", s)


# ── Рис. 19.5.6 — властивості стека ────────────────────────────────────────
def fig195_props():
    W, H = 900, 412
    s = header(W, H)
    s += text(W / 2, 34, "Властивості стека: швидко й само — але обмежено й недовговічно", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "стек ідеальний для викликів і локальних, та має дві важливі межі, про які мусить пам'ятати програміст",
              11.5, GREY, "middle", style="italic")
    s += rect(70, 88, 360, 150, "#eef7ee", GREEN, 1.8, 12)
    s += text(250, 112, "Переваги", 13, GREEN, "middle", "bold")
    for i, t in enumerate(["• ШВИДКО: виділення = рух SP на крок", "• САМО: вхід у функцію виділяє,",
                           "   вихід звільняє (нічого не питають)", "• локальні — «автоматичні»",
                           "• ідеально лягає на вкладені виклики"]):
        s += text(92, 138 + i * 21, t, 10.5, INK, "start")
    s += rect(470, 88, 360, 150, "#fdf6f6", RED, 1.8, 12)
    s += text(650, 112, "Межі (обережно!)", 13, RED, "middle", "bold")
    for i, t in enumerate(["• ОБМЕЖЕНИЙ розмір (регіон §19.2);", "   надто глибоко → переповнення (§19.7)",
                           "• локальні ЗНИКАЮТЬ при поверненні:", "   не повертай покажчик на локальну!",
                           "   (це висячий покажчик, §19.4)"]):
        col = RED if i in (2, 3) else INK
        s += text(492, 138 + i * 21, t, 10.3, col, "start", "bold" if i in (2, 3) else "normal")
    s += rect(60, 256, W - 120, 92, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 280, "Стек — для тимчасового: те, що живе рівно стільки, скільки виклик. Швидко й безтурботно, поки не вийдеш за межі.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 302, "А для даних, які мусять ПЕРЕЖИТИ функцію (чи розмір яких заздалегідь невідомий), стек не годиться — потрібна КУПА (§19.6).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 328, "Глибока рекурсія — класична пастка стека: кожен виклик додає кадр, і без виходу стек швидко переповнюється.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 380, "Стек також рятує переривання (Розділ 23): на час обробника контекст теж кладуть на стек — той самий механізм.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-5-6-props.svg", s)


# ═══════════ §19.6 — Купа й динамічна пам'ять ═══════════════════════════════
# ── Рис. 19.6.1 — навіщо купа: чого не може стек ───────────────────────────
def fig196_why():
    W, H = 900, 416
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо купа: два випадки, з якими стек не впорається", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "локальні зникають при поверненні (§19.5), а їхній розмір відомий наперед — та інколи треба не так",
              11.5, GREY, "middle", style="italic")
    s += rect(70, 88, 360, 150, "#fdf6f6", RED, 1.8, 12)
    s += text(250, 112, "1. Дані мусять ПЕРЕЖИТИ функцію", 11.5, RED, "middle", "bold")
    s += text(90, 138, "функція створила результат і завершилась —", 10, INK, "start")
    s += text(90, 156, "та результат потрібен далі, після неї", 10, INK, "start")
    s += text(90, 180, "стек: кадр знято → дані ЗНИКЛИ (§19.5)", 10, RED, "start", "bold")
    s += text(90, 204, "потрібна пам'ять, що живе ДОВШЕ за виклик", 10.5, GREEN, "start", "bold")
    s += rect(470, 88, 360, 150, "#fff8e8", AMBER, 1.8, 12)
    s += text(650, 112, "2. Розмір невідомий НАПЕРЕД", 11.5, "#9a7322", "middle", "bold")
    s += text(490, 138, "скільки даних — вирішується під час роботи", 10, INK, "start")
    s += text(490, 156, "(напр. прочитати N вимірів, N — на льоту)", 10, INK, "start")
    s += text(490, 180, "стек: локальний масив має фіксований розмір", 10, RED, "start", "bold")
    s += text(490, 204, "потрібна пам'ять, що береться на ПОТРІБНИЙ розмір", 10.5, GREEN, "start", "bold")
    s += rect(60, 256, W - 120, 90, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 280, "Для обох випадків є КУПА (heap): велика область, з якої можна ВЗЯТИ блок будь-якого розміру під час роботи,",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 302, "тримати його скільки треба (він переживає функції) і ПОВЕРНУТИ, коли більше не потрібен. Це й є динамічна пам'ять.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 328, "«Динамічна» — бо розмір і час життя вирішуються на льоту (runtime), а не наперед (як у стека й глобальних).",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 384, "Ціна гнучкості — ручне керування й нові класи проблем (фрагментація, витоки), яких у стека не було.",
              11, INK, "middle", "bold")
    save("fig-19-6-1-why.svg", s)


# ── Рис. 19.6.2 — взяти й повернути (allocate / free) ──────────────────────
def fig196_allocfree():
    W, H = 900, 424
    s = header(W, H)
    s += text(W / 2, 34, "Дві дії з купою: взяти блок (allocate) і повернути (free)", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "просиш блок потрібного розміру — дістаєш ПОКАЖЧИК на нього (§19.4); попрацював — повертаєш блок у спільний запас",
              11.5, GREY, "middle", style="italic")
    # allocate
    s += rect(70, 90, 360, 130, "#eef7ee", GREEN, 1.8, 12)
    s += text(250, 114, "ВЗЯТИ (allocate)", 13, GREEN, "middle", "bold")
    s += text(90, 140, "«дай мені блок на 100 байтів»", 10.5, INK, "start", "bold")
    s += arrow(250, 150, 250, 168, GREEN, 2)
    s += text(90, 184, "купа знаходить вільний блок і повертає", 10, INK, "start")
    s += text(90, 202, "ПОКАЖЧИК на нього: p = allocate(100)", 10.5, RED, "start", "bold")
    # free
    s += rect(470, 90, 360, 130, "#f3f5fd", BLUE, 1.8, 12)
    s += text(650, 114, "ПОВЕРНУТИ (free)", 13, BLUE, "middle", "bold")
    s += text(490, 140, "«я закінчив із цим блоком»", 10.5, INK, "start", "bold")
    s += arrow(650, 150, 650, 168, BLUE, 2)
    s += text(490, 184, "free(p): блок вертається в запас", 10.5, INK, "start", "bold")
    s += text(490, 202, "і може бути виданий комусь іншому", 10, GREY, "start")
    s += rect(60, 240, W - 120, 110, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 264, "На відміну від стека, купа — РУЧНА: ти сам береш і сам мусиш повернути; і в БУДЬ-ЯКОМУ порядку (не LIFO).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 286, "Покажчик — твоя ЄДИНА ниточка до блоку: у купи дані не мають імені, лише адресу. Загубив покажчик — загубив блок (витік).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 312, "(у мові C це функції malloc/free; у C++ — new/delete; суть — «взяти» і «повернути» пам'ять на льоту)",
              10, GREY, "middle", style="italic")
    s += text(W / 2, 334, "Хто стежить за вільними й зайнятими блоками — «розпорядник купи» (allocator): службова бухгалтерія над областю купи.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 384, "Свобода брати будь-що будь-коли — могутня, та саме вона й породжує фрагментацію (нижче) і вимагає дисципліни.",
              11, INK, "middle", "bold")
    save("fig-19-6-2-allocfree.svg", s)


# ── Рис. 19.6.3 — стек vs купа ─────────────────────────────────────────────
def fig196_vs():
    W, H = 900, 430
    s = header(W, H)
    s += text(W / 2, 34, "Стек vs купа: дві області — два характери", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "стек — швидкий, автоматичний, але жорсткий; купа — гнучка, але ручна й примхлива",
              11.5, GREY, "middle", style="italic")
    s += rect(330, 82, 250, 30, "#fdf4f4", RED, 1.4, 6)
    s += text(455, 102, "СТЕК (§19.5)", 12.5, RED, "middle", "bold")
    s += rect(610, 82, 250, 30, "#fff8e8", AMBER, 1.4, 6)
    s += text(735, 102, "КУПА (heap)", 12.5, "#9a7322", "middle", "bold")
    rows = [
        ("керування", "автоматичне (вхід/вихід)", "РУЧНЕ (взяв — поверни)"),
        ("порядок", "суворий LIFO", "будь-який"),
        ("швидкість", "дуже швидко (рух SP)", "повільніше (пошук блоку)"),
        ("розмір", "відомий наперед, малий", "гнучкий, до межі купи"),
        ("час життя", "поки триває функція", "поки сам не звільниш"),
        ("головна біда", "переповнення (§19.7)", "фрагментація, витоки"),
    ]
    for i, (k, st, hp) in enumerate(rows):
        y = 120 + i * 48
        s += rect(70, y, 250, 42, "#fafafa", GREY, 1.2, 6)
        s += text(82, y + 26, k, 12, INK, "start", "bold")
        s += rect(330, y, 250, 42, "#fdf4f4", RED, 1.2, 6)
        s += text(455, y + 26, st, 10.5, INK, "middle")
        s += rect(610, y, 250, 42, "#fff8e8", AMBER, 1.2, 6)
        s += text(735, y + 26, hp, 10.5, INK, "middle")
    s += text(W / 2, 422, "Коротко: стек — для тимчасового, що живе з викликом (швидко й безтурботно); купа — для довговічного чи невідомого розміру (гнучко, та обережно).",
              10.5, INK, "middle", "bold")
    save("fig-19-6-3-vs.svg", s)


# ── Рис. 19.6.4 — фрагментація ─────────────────────────────────────────────
def fig196_frag():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 34, "Головна біда купи: фрагментація", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "після багатьох «взяти-повернути» вільне місце дробиться на дрібні розкидані шматки — і великий блок уже нікуди покласти",
              11.5, GREY, "middle", style="italic")
    bx, bw = 90, 720
    # початок: усе вільно
    s += text(bx, 96, "спочатку — суцільний вільний простір:", 10.5, INK, "start", "bold")
    s += rect(bx, 104, bw, 28, "#eef7ee", GREEN, 1.4, 4)
    s += text(bx + bw / 2, 122, "вільно", 10, GREEN, "middle", "bold")
    # після взять/повернень: дірки
    s += text(bx, 168, "після багатьох allocate/free — «дірки» між зайнятими блоками:", 10.5, INK, "start", "bold")
    segs = [("зайнято", 120, BLUE), ("вільно", 70, GREEN), ("зайнято", 90, BLUE),
            ("вільно", 60, GREEN), ("зайнято", 110, BLUE), ("вільно", 80, GREEN),
            ("зайнято", 100, BLUE), ("вільно", 90, GREEN)]
    x = bx
    for name, w, col in segs:
        bg = "#f3f5fd" if col == BLUE else "#eef7ee"
        s += rect(x, 176, w, 28, bg, col, 1.4, 0)
        s += text(x + w / 2, 194, "■" if col == BLUE else "·", 11, col, "middle", "bold")
        x += w
    s += text(bx + bw + 6, 194, "", 9, GREY, "start")
    # запит великого блоку
    s += rect(bx, 240, 300, 30, "#fff8e8", AMBER, 1.8, 6)
    s += text(bx + 150, 260, "запит: блок на 200 байтів", 11, "#9a7322", "middle", "bold")
    s += text(bx + 320, 260, "✘ НЕ влазить!", 13, RED, "start", "bold")
    s += text(bx, 296, "вільного загалом ВИСТАЧАЄ (70+60+80+90 = 300), та немає суцільного шматка на 200 поспіль.", 10.5, INK, "start", "bold")
    s += rect(60, 320, W - 120, 110, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 344, "Це «зовнішня фрагментація»: пам'ять є, але роздроблена. Як паркінг із проміжками, у який не влазить автобус,",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 366, "хоч вільних місць сумарно й багато. Виділення може зазнати невдачі попри «достатню» вільну пам'ять.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 392, "Що довше працює програма з безладними alloc/free різних розмірів, то гірша фрагментація — поступово, непомітно.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 414, "На великих системах із цим борються (ущільнення, пули блоків); на крихітному МК це особливо небезпечно (нижче).",
              10.5, GREY, "middle", style="italic")
    save("fig-19-6-4-frag.svg", s)


# ── Рис. 19.6.5 — біди купи ────────────────────────────────────────────────
def fig196_bugs():
    W, H = 900, 432
    s = header(W, H)
    s += text(W / 2, 34, "Біди купи: витік, використання після звільнення, подвійне звільнення", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "ручне керування означає ручні помилки — і всі вони підступні, бо проявляються не одразу",
              11.5, GREY, "middle", style="italic")
    bugs = [
        ("Витік пам'яті (leak)", "узяв блок і не повернув (чи загубив покажчик);", "пам'ять помалу заповнюється → з часом вичерпується", RED),
        ("Використання після звільнення", "звільнив блок, та далі ним користуєшся через покажчик —", "це висячий покажчик (§19.4): сміття або аварія", AMBER),
        ("Подвійне звільнення (double free)", "звільнив той самий блок ДВІЧІ —", "псує бухгалтерію розпорядника купи", RED),
    ]
    for i, (t, d1, d2, col) in enumerate(bugs):
        y = 86 + i * 76
        s += rect(70, y, 760, 64, "#fdf6f6" if col == RED else "#fff8e8", col, 1.7, 10)
        s += text(92, y + 26, t, 12.5, col, "start", "bold")
        s += text(92, y + 46, d1, 10.5, INK, "start")
        s += text(470, y + 46, d2, 10.5, GREY, "start")
    s += rect(60, 322, W - 120, 100, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 346, "Найпідступніший — ВИТІК: програма працює, але помалу «з'їдає» пам'ять; на сервері це тижні, на МК — інколи години до краху.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 368, "Усі три ростуть із того самого кореня, що й біди покажчиків (§19.4): пам'яттю керуєш ти, і ти ж за неї відповідаєш.",
              11, INK, "middle", "bold")
    s += text(W / 2, 394, "Повний звід типових бід пам'яті — і стека, і купи — зберемо в наступному підрозділі (§19.7).",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 414, "Золоте правило: кожному allocate — рівно один free, не раніше й не пізніше; і не чіпай блок після звільнення.",
              10.5, INK, "middle", "bold")
    save("fig-19-6-5-bugs.svg", s)


# ── Рис. 19.6.6 — купа на мікроконтролері: обережно ────────────────────────
def fig196_mcu():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 34, "Купа на мікроконтролері: потужно, та небезпечно", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "на крихітному МК динамічна пам'ять особливо ризикована — тому вбудована практика часто її уникає або суворо обмежує",
              11.5, GREY, "middle", style="italic")
    risks = [
        ("Мізерна RAM", "лічені кілобайти — фрагментація вичерпує її швидко й фатально", RED),
        ("Витоки = крах", "пристрій працює тижнями без перезапуску; навіть крихітний витік зрештою вб'є його", RED),
        ("Недетермінований час", "allocate триває то довше, то коротше — погано для реального часу (керування)", AMBER),
    ]
    for i, (t, d, col) in enumerate(risks):
        y = 88 + i * 56
        s += rect(70, y, 760, 46, "#fdf6f6" if col == RED else "#fff8e8", col, 1.7, 10)
        s += text(92, y + 28, t, 12, col, "start", "bold")
        s += text(330, y + 28, d, 10.5, INK, "start")
    s += rect(60, 268, W - 120, 110, "#eef7ee", GREEN, 1.7, 10)
    s += text(W / 2, 292, "Тому у вбудованих системах часто: уникають динамічної пам'яті зовсім, або виділяють ОДИН раз на старті,",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 314, "або беруть фіксовані «пули» блоків однакового розміру (без фрагментації), або обходяться стеком і глобальними.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 340, "Правило для МК: динамічна пам'ять — за потреби й обережно; для постійних чи критичних до часу даних — статика й стек.",
              11, GREEN, "middle", "bold")
    s += text(W / 2, 362, "Це не значить «купа погана» — на великих системах вона незамінна; та на крихітному залізі реального часу до неї підходять сторожко.",
              10, GREY, "middle", style="italic")
    s += text(W / 2, 402, "Коли в Модулях 4–5 ви писатимете прошивки, віддавайте перевагу передбачуваній статичній пам'яті там, де можна.",
              10.5, INK, "middle", "bold")
    save("fig-19-6-6-mcu.svg", s)


# ═══════════ §19.7 — Переповнення стека й типові біди пам'яті ════════════════
# ── Рис. 19.7.1 — переповнення стека ───────────────────────────────────────
def fig197_stackoverflow():
    W, H = 900, 444
    s = header(W, H)
    s += text(W / 2, 34, "Переповнення стека: стек доростає до купи", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "стек росте вниз (глибокі виклики, рекурсія, великі локальні) — і якщо дороста до купи, починається лихо (§19.2)",
              11.5, GREY, "middle", style="italic")
    bx, bw = 330, 240
    s += rect(bx, 92, bw, 50, "#fdf4f4", RED, 1.8, 0)
    s += text(bx + bw / 2, 114, "СТЕК", 12.5, RED, "middle", "bold")
    s += text(bx + bw / 2, 132, "виклики, локальні", 9, GREY, "middle")
    s += arrow(bx + bw / 2, 150, bx + bw / 2, 235, RED, 2.6)
    s += text(bx + bw / 2 + 14, 195, "росте вниз", 10, RED, "start", "bold")
    s += text(bx + bw / 2 + 14, 211, "(глибше й глибше)", 9, GREY, "start")
    s += rect(bx, 200, bw, 44, "#fdecec", RED, 1.6, 0, )
    s += text(bx + bw / 2, 226, "💥 ЗІТКНЕННЯ", 12, RED, "middle", "bold")
    s += rect(bx, 250, bw, 44, "#fff8e8", AMBER, 1.8, 0)
    s += text(bx + bw / 2, 272, "КУПА", 12.5, "#9a7322", "middle", "bold")
    s += arrow(bx + bw / 2, 244, bx + bw / 2, 250, AMBER, 2)
    # причини
    s += rect(70, 100, 230, 150, "#f6f8f6", GREY, 1.4, 10)
    s += text(185, 124, "Звідки переповнення", 11.5, INK, "middle", "bold")
    for i, t in enumerate(["• рекурсія без кінця", "• надто глибокі вкладені", "   виклики",
                           "• величезні локальні", "   масиви на стеку"]):
        s += text(86, 150 + i * 22, t, 10.5, INK, "start")
    # наслідок
    s += rect(600, 100, 230, 150, "#fdf6f6", RED, 1.4, 10)
    s += text(715, 124, "Що буде", 11.5, RED, "middle", "bold")
    for i, t in enumerate(["ПК: ОС спіймає й", "   зупинить (segfault)", "",
                           "МК: ТИХО псує сусіднє", "   → загадковий крах"]):
        col = RED if i >= 3 else INK
        s += text(616, 150 + i * 22, t, 10.5, col, "start", "bold" if i >= 3 else "normal")
    s += text(W / 2, 330, "Стек і купа ростуть назустріч в один простір (§19.2). Якщо стек дороста до купи — вони псують дані одне одного.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 356, "На МК це особливо підступно: немає захисту пам'яті, тож ніхто не попередить — програма просто почне поводитись дивно.",
              11, INK, "middle", "bold")
    s += text(W / 2, 386, "Запобігання: уникай нескінченної рекурсії, не клади величезні масиви на стек, лишай стеку запас.",
              10.5, GREEN, "middle", "bold")
    s += text(W / 2, 414, "Глибока рекурсія — найчастіша причина: кожен виклик додає кадр (§19.5), і без виходу стек швидко вичерпується.",
              10, GREY, "middle", style="italic")
    save("fig-19-7-1-stackoverflow.svg", s)


# ── Рис. 19.7.2 — переповнення буфера ──────────────────────────────────────
def fig197_bufferoverflow():
    W, H = 900, 452
    s = header(W, H)
    s += text(W / 2, 34, "Переповнення буфера: запис за межі масиву псує сусіднє", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "масив на 8 байтів, а пишемо 12 — зайве «вилазить» поверх сусідніх даних, аж до АДРЕСИ ПОВЕРНЕННЯ на стеку (§19.5)",
              11.5, GREY, "middle", style="italic")
    # масив 8 комірок + сусіди
    x0 = 150
    for i in range(8):
        s += rect(x0 + i * 50, 110, 48, 36, "#eef7ee", GREEN, 1.5, 4)
        s += text(x0 + i * 50 + 24, 134, "·", 12, GREEN, "middle")
    s += text(x0 + 4 * 50, 96, "буфер на 8 байтів", 10.5, GREEN, "middle", "bold")
    # сусідні (зайві)
    for i in range(4):
        s += rect(x0 + (8 + i) * 50, 110, 48, 36, "#fdecec", RED, 1.8, 4)
        s += text(x0 + (8 + i) * 50 + 24, 134, "✗", 12, RED, "middle", "bold")
    s += text(x0 + 10 * 50, 96, "сусіднє: інші дані / адреса повернення", 10, RED, "middle", "bold")
    s += arrow(x0 + 8 * 50 - 6, 164, x0 + 9 * 50, 152, RED, 2.2)
    s += text(x0 + 9 * 50, 184, "запис 12 байтів «перелився» за край — і затер сусідів", 10.5, RED, "middle", "bold")
    s += rect(70, 210, 380, 110, "#fdf6f6", RED, 1.6, 10)
    s += text(260, 234, "Наслідок 1: крах", 12, RED, "middle", "bold")
    s += text(90, 258, "затерта адреса повернення →", 10.5, INK, "start")
    s += text(90, 276, "функція «повернеться» в сміття →", 10.5, INK, "start")
    s += text(90, 294, "стрибок у нікуди, аварія", 10.5, INK, "start")
    s += text(90, 312, "(пам'ятаєте §19.5 — адреса на стеку?)", 9.5, GREY, "start", style="italic")
    s += rect(470, 210, 380, 110, "#fff8e8", AMBER, 1.6, 10)
    s += text(660, 234, "Наслідок 2: злам (експлойт)", 12, "#9a7322", "middle", "bold")
    s += text(490, 258, "зловмисник навмисне підбирає «зайве»,", 10.5, INK, "start")
    s += text(490, 276, "щоб адреса повернення вказала на ЙОГО код →", 10.5, INK, "start")
    s += text(490, 294, "захоплення керування («smashing the stack»)", 10.5, INK, "start")
    s += text(490, 312, "— класична діра безпеки на десятиліття", 9.5, GREY, "start", style="italic")
    s += text(W / 2, 348, "Корінь — відсутність перевірки меж: код пише, не глянувши, чи влазить. Дуже частий і дуже небезпечний баг.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 374, "Запобігання: завжди перевіряй межі (індекс < розмір), користуйся безпечними функціями, не довіряй довжині вхідних даних.",
              11, GREEN, "middle", "bold")
    s += text(W / 2, 404, "Те саме буває й поза стеком (у купі, у глобальних) — будь-який запис за межу виділеного псує сусіднє.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 430, "«Off-by-one» (на одиницю далі) — найтиповіша форма: цикл до <= замість <, забутий нуль-термінатор рядка тощо.",
              10, GREY, "middle", style="italic")
    save("fig-19-7-2-bufferoverflow.svg", s)


# ── Рис. 19.7.3 — звід типових бід пам'яті ─────────────────────────────────
def fig197_roundup():
    W, H = 900, 466
    s = header(W, H)
    s += text(W / 2, 34, "Звід типових бід пам'яті (зведення розділу)", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "майже всі грізні баги системного коду — про пам'ять; ось вони разом, з посиланнями, де ми їх зустріли",
              11.5, GREY, "middle", style="italic")
    bugs = [
        ("Переповнення стека", "стек доріс до купи (глибока рекурсія, великі локальні)", "§19.5"),
        ("Переповнення буфера", "запис за межі масиву → псує сусіднє (й адресу повернення)", "§19.5"),
        ("Витік пам'яті", "узяв на купі й не повернув → пам'ять вичерпується", "§19.6"),
        ("Висячий покажчик", "на звільнену/зниклу пам'ять (use-after-free)", "§19.4–6"),
        ("Розіменування null", "піти за нульовим покажчиком → аварія", "§19.4"),
        ("Дикий покажчик", "неініціалізований → випадкова адреса → псує пам'ять", "§19.4"),
        ("Подвійне звільнення", "free того самого блоку двічі → псує розпорядника", "§19.6"),
        ("Читання неініціалізованого", "узяв змінну до присвоєння → сміттєве значення", "—"),
    ]
    for i, (t, d, ref) in enumerate(bugs):
        y = 86 + i * 44
        s += rect(70, y, 250, 38, "#fdf6f6", RED, 1.4, 6)
        s += text(82, y + 24, t, 11, RED, "start", "bold")
        s += rect(330, y, 420, 38, "#ffffff", GREY, 1, 6)
        s += text(342, y + 24, d, 10, INK, "start")
        s += rect(760, y, 70, 38, "#eef0f4", INK, 1, 6)
        s += text(795, y + 24, ref, 10, GREY, "middle", "bold")
    s += text(W / 2, 452, "Усі вони небезпечні передусім тому, що ТИХІ — не дають негайної помилки, а псують щось і йдуть далі (чому — нижче).",
              11, INK, "middle", "bold")
    save("fig-19-7-3-roundup.svg", s)


# ── Рис. 19.7.4 — чому такі небезпечні ─────────────────────────────────────
def fig197_whyhard():
    W, H = 900, 432
    s = header(W, H)
    s += text(W / 2, 34, "Чому біди пам'яті — найважчі: тихі, далекі, несталі", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "вони не кричать про себе — псують щось нишком, і симптом виринає геть не там і не тоді, де причина",
              11.5, GREY, "middle", style="italic")
    props = [
        ("ТИХІ", "не дають негайної помилки — псують пам'ять і виконуються далі, ніби все гаразд", RED),
        ("ДАЛЕКІ", "симптом виринає не там, де причина: зіпсував одне — впало зовсім інше, згодом", AMBER),
        ("НЕСТАЛІ", "залежать від таймінгу й даних: то є, то нема — важко відтворити й спіймати", RED),
    ]
    for i, (t, d, col) in enumerate(props):
        y = 90 + i * 56
        s += rect(70, y, 760, 46, "#fdf6f6" if col == RED else "#fff8e8", col, 1.7, 10)
        s += text(92, y + 28, t, 12.5, col, "start", "bold")
        s += text(230, y + 28, d, 10.5, INK, "start")
    s += rect(70, 270, 380, 110, "#fdf6f6", RED, 1.6, 10)
    s += text(260, 294, "На мікроконтролері — гірше", 12, RED, "middle", "bold")
    s += text(90, 318, "немає захисту пам'яті:", 10.5, INK, "start", "bold")
    s += text(90, 336, "ніхто не ловить хибний доступ —", 10.5, INK, "start")
    s += text(90, 354, "програма просто «дуріє»", 10.5, INK, "start")
    s += text(90, 372, "(а перезапустити в полі нема кому)", 9.5, GREY, "start", style="italic")
    s += rect(470, 270, 380, 110, "#eef7ee", GREEN, 1.6, 10)
    s += text(660, 294, "На ПК — трохи легше", 12, GREEN, "middle", "bold")
    s += text(490, 318, "апаратний захист (MMU) + ОС", 10.5, INK, "start", "bold")
    s += text(490, 336, "ловлять багато звернень «не туди»", 10.5, INK, "start")
    s += text(490, 354, "→ програма падає одразу (segfault),", 10.5, INK, "start")
    s += text(490, 372, "ближче до місця помилки", 10.5, INK, "start")
    save("fig-19-7-4-whyhard.svg", s)


# ── Рис. 19.7.5 — спільний корінь ──────────────────────────────────────────
def fig197_root():
    W, H = 880, 392
    s = header(W, H)
    s += text(W / 2, 34, "Спільний корінь: доступ ПОЗА межами або в НЕ ТОЙ ЧАС", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "попри розмаїття, майже всі біди пам'яті зводяться до двох помилок — і обидві з понять цього розділу",
              11.5, GREY, "middle", style="italic")
    s += rect(80, 92, 340, 150, "#fdf6f6", RED, 1.8, 12)
    s += text(250, 118, "Доступ ПОЗА дійсною пам'яттю", 11.5, RED, "middle", "bold")
    for i, t in enumerate(["• за межі масиву (буфер)", "• за нульовою/випадковою адресою", "• стек дороста до купи",
                           "корінь: плутанина «адреса/значення»", "та брак перевірки меж (§19.1)"]):
        col = GREY if i >= 3 else INK
        s += text(100, 144 + i * 20, t, 10.3, col, "start", "italic" if i >= 3 else "normal")
    s += rect(460, 92, 340, 150, "#fff8e8", AMBER, 1.8, 12)
    s += text(630, 118, "Вживання в НЕ ТОЙ ЧАС", 11.5, "#9a7322", "middle", "bold")
    for i, t in enumerate(["• до ініціалізації (сміття)", "• після звільнення (висячий)", "• після виходу функції (локальна)",
                           "корінь: брак дисципліни покажчиків", "та керування часом життя (§19.4)"]):
        col = GREY if i >= 3 else INK
        s += text(480, 144 + i * 20, t, 10.3, col, "start", "italic" if i >= 3 else "normal")
    s += rect(60, 264, W - 120, 114, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 288, "Звідси й уся профілактика: не виходь за межі виділеного й не чіпай пам'ять не у свій час (до ініціалізації / після звільнення).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 312, "Дві наскрізні ідеї розділу тримають усе: чітка різниця «адреса/значення» (§19.1) і дисципліна покажчиків (§19.4).",
              11, INK, "middle", "bold")
    s += text(W / 2, 340, "Тому пам'ять — і найпотужніше, і найнебезпечніше в системному коді: машина робить РІВНО що сказано, навіть коли це сказано хибно.",
              10.5, GREY, "middle", style="italic")
    s += text(W / 2, 362, "(згадайте §18.1: процесор дурний і слухняний — він залюбки перепише адресу повернення, якщо ви йому це звеліли)",
              10, GREY, "middle", style="italic")
    save("fig-19-7-5-root.svg", s)


# ── Рис. 19.7.6 — як захищатися ────────────────────────────────────────────
def fig197_defenses():
    W, H = 900, 432
    s = header(W, H)
    s += text(W / 2, 34, "Як захищатися: дисципліна, передбачуваність, інструменти", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "цілковито уникнути не завжди можна, та правильні звички гасять переважну більшість бід пам'яті",
              11.5, GREY, "middle", style="italic")
    defs = [
        ("Перевіряй межі", "індекс < розмір; не довіряй довжині вхідних даних", GREEN),
        ("Ініціалізуй усе", "змінні й покажчики — нулем чи валідним значенням одразу", GREEN),
        ("Звільняй рівно раз", "кожному allocate — один free; обнуляй покажчик після нього", GREEN),
        ("Бережи стек", "уникай нескінченної рекурсії й величезних локальних; лишай запас", GREEN),
        ("На МК — статика", "віддавай перевагу статичній/стековій пам'яті над купою", BLUE),
        ("Інструменти й мови", "санітайзери, статичний аналіз; мови з безпекою пам'яті (Rust) гасять цілі класи", AMBER),
    ]
    for i, (t, d, col) in enumerate(defs):
        y = 86 + i * 46
        s += rect(70, y, 250, 40, "#fafafa", col, 1.6, 8)
        s += text(90, y + 25, t, 12, col, "start", "bold")
        s += rect(330, y, 500, 40, "#ffffff", GREY, 1, 8)
        s += text(346, y + 25, d, 10.3, INK, "start")
    s += rect(60, 372, W - 120, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 394, "C/C++ на МК ДОВІРЯЄ вам: ніхто не стереже пам'ять, тож дисципліна — на вас. Ці звички відрізняють надійну прошивку від примхливої.",
              11, INK, "middle", "bold")
    s += text(W / 2, 414, "Засвоївши пам'ять зсередини (увесь цей розділ), ви розумієте і ЧОМУ виникають ці біди, і як їх не припуститися.",
              10.5, GREY, "middle", style="italic")
    save("fig-19-7-6-defenses.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_core_bit()
    fig_coincident()
    fig_destructive()
    fig_significance()
    # §19.1
    fig191_array()
    fig191_addr_data()
    fig191_byte_addr()
    fig191_space()
    fig191_rw()
    fig191_meaning()
    # §19.2
    fig192_map()
    fig192_regions()
    fig192_grow()
    fig192_mcu()
    fig192_mmio()
    # §19.3
    fig193_volatile()
    fig193_split()
    fig193_quirks()
    fig193_startup()
    fig193_zoo()
    # §19.4
    fig194_pointer()
    fig194_ops()
    fig194_number()
    fig194_analogy()
    fig194_uses()
    fig194_dangers()
    # §19.5
    fig195_problem()
    fig195_lifo()
    fig195_frame()
    fig195_returnaddr()
    fig195_trace()
    fig195_props()
    # §19.6
    fig196_why()
    fig196_allocfree()
    fig196_vs()
    fig196_frag()
    fig196_bugs()
    fig196_mcu()
    # §19.7
    fig197_stackoverflow()
    fig197_bufferoverflow()
    fig197_roundup()
    fig197_whyhard()
    fig197_root()
    fig197_defenses()
    print("ch19 figures done.")
