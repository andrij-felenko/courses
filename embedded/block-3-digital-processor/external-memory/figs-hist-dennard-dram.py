# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до Розділу 3.8 — «Зовнішня пам'ять»
(Модуль 3): Роберт Деннард і DRAM з одного транзистора (IBM, 1966–68).

ОКРЕМИЙ скрипт лише цієї вставки (головний figs.py розділу не чіпаємо).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «+» червоний, «−» синій; стрілки через marker;
шрифт sans-serif. Підписи історії до розділу — секція 0 (Рис. 3.8.0.k →
файли fig-r08-0-k-*). Допоміжні функції — копія спільних із рештою розділів,
щоб вигляд був єдиний.
"""
import os

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


# ── символ MOS-транзистора-ключа (спрощений): затвор + канал ────────────────
def _fet(cx, cy, col=INK, on=True):
    """Крихітний ключ: вертикальний канал, затвор ліворуч. on=True → провідний."""
    out = line(cx, cy - 16, cx, cy + 16, col, 3)               # канал (сток-витік)
    out += line(cx - 18, cy, cx - 4, cy, col, 2.4)             # лінія затвора
    out += line(cx - 4, cy - 9, cx - 4, cy + 9, col, 3)        # пластина затвора
    if on:
        out += text(cx - 22, cy + 4, "ON", 10, GREEN, "end", "bold")
    else:
        out += text(cx - 22, cy + 4, "off", 10, GREY, "end", "bold")
    return out


# ── символ конденсатора (дві пластини) із зарядом/без ───────────────────────
def _cap(cx, cy, charged, label=True):
    col = RED if charged else GREY
    out = line(cx - 16, cy, cx - 4, cy, INK, 2.4)          # підвід
    out += line(cx - 4, cy - 12, cx - 4, cy + 12, INK, 3)  # верхня пластина
    out += line(cx + 4, cy - 12, cx + 4, cy + 12, col, 3)  # нижня пластина
    out += line(cx + 4, cy, cx + 16, cy, INK, 2.4)         # до землі
    out += line(cx + 10, cy + 8, cx + 22, cy + 8, INK, 2)  # земля
    out += line(cx + 13, cy + 12, cx + 19, cy + 12, INK, 2)
    out += text(cx, cy - 20, "+ + +" if charged else "—", 11 if charged else 12,
                RED if charged else GREY, "middle", "bold")
    if label:
        if charged:
            out += text(cx, cy + 34, "заряд є = «1»", 10.5, RED, "middle", "bold")
        else:
            out += text(cx, cy + 34, "порожньо = «0»", 10.5, GREY, "middle")
    return out


# ═══════════ Рис. 3.8.0.1 — ланцюг: від осердь до 1T-комірки й тріумфу ══════
def fig_timeline():
    W, H = 900, 690
    s = header(W, H)
    s += text(W / 2, 36, "Ланцюг до DRAM: як один транзистор здешевив пам'ять у рази", 20.5, INK, "middle", "bold")
    s += text(W / 2, 58, "ідея 1966-го дозріла не одразу — спершу ринок узяв складнішу комірку, і лише потім переміг найпростіший варіант",
              12, GREY, "middle", style="italic")
    spine = 250
    top, bot = 96, H - 24
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("до 1968", "осердя: дорого й вручну",
         "Оперативку ткали з феритових кілець руками (§3.6); надійно, але громіздко, дорого й не масштабовано", False),
        ("1966", "епіфанія Деннарда",
         "Почувши доповідь колег про комірку на кількох транзисторах, Деннард того ж вечора питає себе: а що, як ОДИН транзистор?", True),
        ("1967 → 4.VI.1968", "патент US 3,387,286",
         "IBM подає заявку 1967-го; патент видано 1968-го — одна комірка = один транзистор + один конденсатор (1T1C)", False),
        ("жовтень 1970", "Intel 1103 — перша DRAM",
         "Перша масова DRAM бере НЕ 1T-комірку Деннарда, а складнішу 3-транзисторну (від Honeywell) — її простіше було випустити", False),
        ("середина 1970-х", "1T перемагає",
         "Щойно техпроцес дозрів, чипи на 4 Кбіт переходять на комірку Деннарда — найдешевшу й найщільнішу; вона й лишилась", False),
        ("донині", "DRAM усюди",
         "Кожен модуль ОЗП у телефоні, ПК і серверi — мільярди копій тієї самої комірки 1T1C; ідея пережила сам ферит", False),
    ]
    n = len(nodes)
    for i, (yr, who, q, hl) in enumerate(nodes):
        y = top + 26 + (bot - top - 52) * i / (n - 1)
        if hl:
            s += circle(spine, y, 11, "#fff", RED, 0)
            s += circle(spine, y, 10, "none", RED, 3.2)
            s += circle(spine, y, 4.5, RED, RED, 1)
        else:
            s += circle(spine, y, 7, "#fff", INK, 2.6)
        s += text(spine - 22, y + 5, yr, 12, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5, (RED if hl else INK), "start", "bold")
        for j, ln in enumerate(_wrap(q, 62)):
            s += text(spine + 26, y + 18 + j * 17, ln, 12, INK, "start", style="italic")
    save("fig-r08-0-1-timeline.svg", s)


# ═══════════ Рис. 3.8.0.2 — сама комірка 1T1C: транзистор-ключ + конденсатор ═
def fig_cell():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Комірка Деннарда: один транзистор-ключ і один конденсатор-«відерце»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "біт — це наявність чи відсутність заряду у крихітному конденсаторі; транзистор лише ВІДЧИНЯЄ доступ до нього",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВОРУЧ: запис «1» — рядок відчиняє ключ, стовпець заливає заряд ──
    s += rect(60, 84, 360, 300, "#fafafa", INK, 1.6, 10)
    s += text(240, 110, "ЗАПИС «1»: ключ ON → конденсатор заряджається", 11.5, INK, "middle", "bold")
    # лінія рядка (word line) — керує затвором
    s += text(96, 168, "рядок", 11, GREEN, "end", "bold")
    s += text(96, 184, "(word)", 9.5, GREEN, "end")
    s += arrow(100, 176, 196, 176, GREEN, 2.4)
    s += _fet(214, 200, INK, on=True)
    # лінія стовпця (bit line) — несе заряд
    s += text(240, 132, "стовпець (bit line)", 10.5, RED, "middle", "bold")
    s += arrow(240, 140, 240, 182, RED, 2.4)
    s += line(214, 184, 240, 184, INK, 2.4)         # від bit line до стоку
    s += line(214, 216, 300, 216, INK, 2.4)         # від витоку до конденсатора
    s += _cap(326, 230, charged=True)
    s += text(240, 366, "пів-секрету DRAM: дешевизна — бо деталей лише ДВІ", 11, GREEN, "middle", "bold")

    # ── ПРАВОРУЧ: зберігання — ключ off, заряд замкнено в конденсаторі ──
    s += rect(480, 84, 360, 300, "#fafafa", INK, 1.6, 10)
    s += text(660, 110, "ЗБЕРІГАННЯ: ключ off → заряд замкнено", 11.5, INK, "middle", "bold")
    s += text(516, 168, "рядок", 11, GREY, "end", "bold")
    s += text(516, 184, "(0 В)", 9.5, GREY, "end")
    s += line(520, 176, 612, 176, GREY, 2, dash="5 5")
    s += _fet(634, 200, GREY, on=False)
    s += text(660, 132, "стовпець відключено", 10.5, GREY, "middle")
    s += line(634, 184, 660, 184, GREY, 2, dash="4 4")
    s += line(634, 216, 720, 216, INK, 2.4)
    s += _cap(746, 230, charged=True)
    s += text(660, 300, "заряд тримається… але НЕ вічно:", 11, RED, "middle", "bold")
    s += text(660, 320, "конденсатор помалу «тече» крізь неідеальний", 10, INK, "middle")
    s += text(660, 336, "ізолятор — тому біт треба раз у раз ОСВІЖАТИ", 10, INK, "middle")
    s += text(660, 366, "(скільки часу до втрати — кількісно в 🧮 §3.8.2)", 10, GREY, "middle", style="italic")

    s += text(W / 2, 410, "Порівняйте з тригером (§3.3): там біт тримає ПЕТЛЯ з кількох транзисторів, що активно живиться струмом.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 432, "Тут біт — це пасивний заряд у відерці. Дешево до краю (дві деталі), та платня — за течу: безперервна регенерація.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 456, "Звідси й назва: DRAM — Dynamic RAM, «динамічна», бо вміст доводиться постійно поновлювати, інакше він зникне.",
              10.5, GREY, "middle", style="italic")
    save("fig-r08-0-2-cell.svg", s)


# ═══════════ Рис. 3.8.0.3 — 6T / 3T / 1T: чому менше транзисторів = дешевше ══
def fig_compare():
    W, H = 900, 452
    s = header(W, H)
    s += text(W / 2, 34, "Перегони «менше деталей на біт»: 6 → 3 → 1 транзистор", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "що менше транзисторів на один біт, то більше бітів влазить на кристал — і то дешевший кожен біт",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("SRAM (тригер)", "6 транзисторів / біт", "6T",
         ["петля з §3.3: тримає біт сама,", "поки є живлення;", "ШВИДКА, не тече, не треба", "освіжати — але ВЕЛИКА", "й дорога на біт"],
         "сьогодні — кеш у ядрі (§3.5.9)", BLUE, 6),
        ("3T-комірка (Honeywell)", "3 транзистори / біт", "3T",
         ["компроміс: заряд на ємності", "затвора, окремі ключі на", "запис і читання;", "простіша за тригер, та все", "ще три прилади на біт"],
         "саме її взяв Intel 1103 (1970)", AMBER, 3),
        ("DRAM Деннарда", "1 транзистор / біт", "1T1C",
         ["один ключ + один", "конденсатор; найменша", "можлива комірка —", "найщільніша й найдешевша,", "ціною регенерації"],
         "переможець: уся масова ОЗП", RED, 1),
    ]
    cw, gap = 270, 22
    x0 = (W - (3 * cw + 2 * gap)) / 2
    for i, (name, sub, tag, lines, foot, col, ntr) in enumerate(cards):
        x = x0 + i * (cw + gap)
        win = (col == RED)
        s += rect(x, 80, cw, 300, "#fdf4f4" if win else "#fafafa", col, 2.4 if win else 1.6, 12)
        s += text(x + cw / 2, 106, name, 14.5, INK, "middle", "bold")
        s += text(x + cw / 2, 125, sub, 11.5, col, "middle", "bold")
        # піктограма: ntr квадратиків-транзисторів + (для 1T) конденсатор
        bx = x + 22
        for k in range(ntr):
            s += rect(bx + k * 24, 142, 18, 18, "#fff", col, 1.8, 3)
            s += text(bx + k * 24 + 9, 155, "T", 11, col, "middle", "bold")
        if ntr == 1:
            s += text(bx + 30, 155, "+ C", 12, RED, "start", "bold")
            s += rect(bx + 66, 142, 18, 18, "#fff", RED, 1.8, 3)
            s += text(bx + 66 + 9, 155, "C", 11, RED, "middle", "bold")
        # «пігулка» з тегом
        s += rect(x + cw - 70, 138, 54, 24, col, col, 0, 12)
        s += text(x + cw - 43, 155, tag, 12, "#fff", "middle", "bold")
        for j, ln in enumerate(lines):
            s += text(x + 20, 188 + j * 19, ln, 11.2, INK, "start")
        s += line(x + 18, 292, x + cw - 18, 292, FAINT, 1.4)
        for j, ln in enumerate(_wrap(foot, 30)):
            s += text(x + cw / 2, 312 + j * 16, ln, 11, (RED if win else GREY), "middle",
                      "bold" if win else "normal", "normal" if win else "italic")
    s += text(W / 2, 404, "Ось чому 1T-комірка зрештою перемогла: на тій самій площі кремнію вона дає НАЙБІЛЬШЕ бітів — отже, найдешевших.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 428, "Платня за щільність — складніший контролер: руйнівне читання й безперервна регенерація (далі). Воно того варте.",
              11, GREY, "middle", style="italic")
    save("fig-r08-0-3-compare.svg", s)


# ═══════════ Рис. 3.8.0.4 — дві ціни дешевизни: руйнівне читання й течія ════
def fig_two_prices():
    W, H = 900, 446
    s = header(W, H)
    s += text(W / 2, 34, "Дві ціни за дешевизну 1T-комірки (обидві Деннард розв'язав схемою)", 18, INK, "middle", "bold")
    s += text(W / 2, 56, "крихітний заряд складно і прочитати, не стерши, і втримати, не поновивши — звідси два «ритуали» DRAM",
              11.5, GREY, "middle", style="italic")

    # ── ЛІВОРУЧ: руйнівне читання → відновлення ──
    s += rect(60, 84, 360, 300, "#fdf6f6", RED, 1.8, 10)
    s += text(240, 110, "1) Читання РУЙНУЄ біт", 13.5, RED, "middle", "bold")
    # три кадри: заряджено → ключ ON, заряд стікає в лінію → відновити
    s += _cap(150, 162, charged=True, label=False)
    s += text(150, 196, "було «1»", 10, INK, "middle", "bold")
    s += arrow(196, 172, 252, 172, RED, 2.4)
    s += text(224, 158, "ключ ON", 9.5, RED, "middle", "bold")
    s += _cap(300, 162, charged=False, label=False)
    s += text(300, 196, "заряд УТІК у лінію", 9.5, RED, "middle", "bold")
    s += text(300, 210, "(підсилювач устиг", 9, GREY, "middle")
    s += text(300, 222, "почути: «там була 1»)", 9, GREY, "middle")
    s += text(240, 256, "комірка тепер ПОРОЖНЯ — біт стерто читанням", 10.5, INK, "middle", "bold")
    s += arrow(240, 270, 240, 302, GREEN, 2.4)
    s += text(356, 290, "тож одразу", 9.5, GREEN, "end", "bold")
    s += _cap(240, 328, charged=True, label=False)
    s += text(240, 362, "…і схема ВІДНОВЛЮЄ заряд назад", 10.5, GREEN, "middle", "bold")

    # ── ПРАВОРУЧ: течія → регенерація ──
    s += rect(480, 84, 360, 300, "#fdf6f6", RED, 1.8, 10)
    s += text(660, 110, "2) Заряд сам ТЕЧЕ з часом", 13.5, RED, "middle", "bold")
    # графік спаду заряду + поріг + точки оновлення
    ox, oy = 540, 290
    s += arrow(ox, oy, ox + 250, oy, INK, 2)
    s += arrow(ox, oy, ox, 150, INK, 2)
    s += text(ox + 250, oy + 16, "час →", 10.5, INK, "start", "bold")
    s += text(ox - 8, 146, "заряд", 10.5, INK, "end", "bold")
    # лінія порога «нижче — біт втрачено»
    thr = 250
    s += line(ox, thr, ox + 250, thr, GREY, 1.6, dash="6 5")
    s += text(ox + 252, thr + 4, "поріг", 9.5, GREY, "start", style="italic")
    # пилкоподібний спад із поновленнями
    saw = [(ox, 168)]
    x = ox
    top_y, drop = 168, 80
    for k in range(3):
        saw.append((x + 70, top_y + drop))       # стікання
        saw.append((x + 70, top_y))               # стрибок угору = регенерація
        x += 70
    s += polyline(saw, RED, 2.6)
    for k in range(3):
        s += circle(ox + 70 + k * 70, top_y, 4, GREEN, GREEN, 0)
    s += text(660, 330, "зелені точки — РЕГЕНЕРАЦІЯ:", 10.5, GREEN, "middle", "bold")
    s += text(660, 348, "контролер раз у кілька мс перечитує", 9.5, INK, "middle")
    s += text(660, 362, "й дозаряджає КОЖЕН рядок, щоб біт не впав за поріг", 9.5, INK, "middle")

    s += text(W / 2, 410, "Обидва «ритуали» — читати-відновлювати й періодично освіжати — успадковані аж від магнітних осердь (§3.6).",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 432, "Саме вони — причина, чому DRAM не під'єднати до простого GPIO, а потрібен окремий контролер пам'яті (§3.8.4).",
              11, GREY, "middle", style="italic")
    save("fig-r08-0-4-two-prices.svg", s)


# ═══════════ Рис. 3.8.0.5 — чесний родовід: ідея ≠ перший чип ═══════════════
def fig_lineage():
    W, H = 900, 452
    s = header(W, H)
    s += text(W / 2, 34, "Чий це винахід: ідея, перший масовий чип і остаточний переможець — РІЗНІ внески", 16.5, INK, "middle", "bold")
    s += text(W / 2, 56, "«придумати найкращу комірку» ≠ «першим випустити робочу DRAM» ≠ «зробити так, щоб найкраща комірка пішла в серію»",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("ІДЕЯ 1T1C", "Роберт Деннард, IBM", "1966 / 1968",
         ["Епіфанія: біт = заряд на", "конденсаторі, доступ — через", "ОДИН транзистор. Патент", "US 3,387,286. Найдешевша", "можлива комірка — на папері", "й у патенті."], RED),
        ("ПЕРШИЙ ЧИП", "Honeywell → Intel", "1969 / 1970",
         ["Реджіц і Проебстінг (Honeywell)", "роблять 3-транзисторну", "комірку; Intel під орудою", "Карпа випускає 1103 —", "першу МАСОВУ DRAM.", "Не 1T, бо так було простіше."], BLUE),
        ("ПЕРЕМОГА 1T", "галузь, середина 1970-х", "~1973–1976",
         ["Коли техпроцес дозрів,", "чипи на 4 Кбіт переходять", "на комірку Деннарда —", "вона витісняє і 3T, і осердя.", "Відтоді 1T1C — стандарт", "усієї світової ОЗП."], GREEN),
    ]
    cw, gap = 272, 20
    x0 = (W - (3 * cw + 2 * gap)) / 2
    for i, (role, who, when, lines, col) in enumerate(cards):
        x = x0 + i * (cw + gap)
        s += rect(x, 82, cw, 268, "#fafafa", col, 1.8, 12)
        s += rect(x, 82, cw, 30, col, col, 0, 12)
        s += text(x + cw / 2, 103, role, 14, "#fff", "middle", "bold")
        s += text(x + cw / 2, 134, who, 13, INK, "middle", "bold")
        s += text(x + cw / 2, 153, when, 11.5, col, "middle", "bold")
        for j, ln in enumerate(lines):
            s += text(x + 18, 178 + j * 19, ln, 11.2, INK, "start")
        # стрілка-перехід між картками
        if i < 2:
            ax = x + cw + 2
            s += arrow(ax, 216, ax + gap - 4, 216, GREY, 2.4)
    s += rect(60, 366, W - 120, 66, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 392, "Підручник любить одне ім'я — «Деннард винайшов DRAM». Чесніше: він придумав найкращу КОМІРКУ, але першу масову",
              11, INK, "middle", "bold")
    s += text(W / 2, 414, "DRAM випустили інші й на іншій комірці; а перемогла ідея Деннарда лише тоді, коли її дотягнула вся галузь. Велике — гуртом.",
              11, GREY, "middle", style="italic")
    save("fig-r08-0-5-lineage.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_cell()
    fig_compare()
    fig_two_prices()
    fig_lineage()
    print("done:", OUT)
