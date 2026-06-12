# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 26 — «Аналого-цифрове перетворення (АЦП)» (Модуль 4).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; '+' червоний, '−' синій; поле зелене;
стрілки через marker; шрифт sans-serif. Підписи нумеруються посекційно
(Рис. C.S.N) у тексті розділу; історія до розділу — C.0.N.

Скрипт нарощується по ітераціях: кожна тема додає свої функції-фігури.
"""
import os
import math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра ─────────────────────────────────────────────────────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
INK   = "#1b1b1b"
GREY  = "#8a8a8a"
FAINT = "#e4e4e4"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fff6e0"
METAL = "#9a9aa0"
GOLD  = "#caa24a"
PURP  = "#7a4fb0"
LPURP = "#efe9f7"
FONT  = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aBlue" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{BLUE}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", RED: "aRed", BLUE: "aBlue", GREEN: "aGreen", GREY: "aGrey"}


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
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def circle(cx, cy, r, fill="none", stroke=INK, w=2):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{w}"/>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def poly(points, color=INK, w=2, fill="none", dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (f'<polyline points="{pts}" fill="{fill}" stroke="{color}" '
            f'stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ═════════════════════════════════════════════════════════════════════════════
# 📜 Історія до розділу — теорема дискретизації — fig-26-0-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 26.0.1 — головне питання: скільки відліків треба ─────────────────────
def figh1_the_question():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Питання, з якого все почалося: скільки вимірів треба?", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "сигнал змінюється неперервно, а ми бачимо лише окремі виміри — відліки; чи можна по них відновити все?", 10.3, GREY, "middle", style="italic")
    ox, mid, A = 80, 200, 78
    s += line(ox, mid, 905, mid, FAINT, 1.4)
    # неперервний сигнал (складена хвиля)
    sig = []
    N = 300
    for i in range(N + 1):
        x = ox + 820 * i / N
        ph = 2 * math.pi * i / N
        y = mid - A * (0.7 * math.sin(2 * ph) + 0.3 * math.sin(5 * ph + 0.7))
        sig.append((x, y))
    s += poly(sig, GREY, 2.0)
    s += text(ox + 6, 96, "неперервний сигнал (реальний світ)", 10, GREY, "start")
    # відліки
    M = 18
    for j in range(M + 1):
        x = ox + 820 * j / M
        ph = 2 * math.pi * j / M
        y = mid - A * (0.7 * math.sin(2 * ph) + 0.3 * math.sin(5 * ph + 0.7))
        s += line(x, mid, x, y, BLUE, 1.2, dash="3,3")
        s += circle(x, y, 3.4, BLUE, BLUE, 0)
    s += text(ox + 6, mid + 26, "сині точки — відліки (що «бачить» машина)", 10, BLUE, "start", "bold")
    s += rect(150, 312, 660, 64, LAMB, GOLD, 1.4, 10)
    s += text(480, 336, "Скільки відліків за секунду треба, щоб НІЧОГО не втратити —", 11, INK, "middle", "bold")
    s += text(480, 356, "і потім точно відновити неперервний сигнал з самих точок?", 11, INK, "middle", "bold")
    s += text(480, 372, "Відповідь дала теорема дискретизації — про неї ця історія.", 9.3, GREY, "middle")
    save("fig-26-0-1-the-question.svg", s)


# ── Рис. 26.0.2 — стрічка часу: хто і коли ───────────────────────────────────
def figh2_timeline():
    W, H = 980, 430
    s = header(W, H)
    s += text(W / 2, 32, "Теорему відкривали НЕЗАЛЕЖНО — у різних країнах, понад 30 років", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "від чистої математики до телеграфу й теорії інформації — звідси й безліч назв", 10.3, GREY, "middle", style="italic")
    ax = 240
    x0, x1 = 70, 910
    s += line(x0, ax, x1, ax, INK, 2.4)
    for yr in range(1910, 1956, 5):
        x = x0 + (x1 - x0) * (yr - 1908) / (1955 - 1908)
        s += line(x, ax - 5, x, ax + 5, GREY, 1.4)
        s += text(x, ax + 22, str(yr), 9.5, GREY, "middle")

    def xof(yr):
        return x0 + (x1 - x0) * (yr - 1908) / (1955 - 1908)

    miles = [
        (1915, "Е. Уіттекер", "Британія · ряд інтерполяції", GREEN, True, 0),
        (1928, "Г. Найквіст", "Швеція/США · гранична швидкість", BLUE, False, 0),
        (1928, "К. Кюпфмюллер", "Німеччина · дискретизація в телеграфії", GOLD, True, 1),
        (1933, "В. Котельников", "СРСР · ПЕРША строга теорема", RED, False, 1),
        (1939, "Г. Раабе", "Німеччина · доведення (умова Раабе)", GOLD, True, 0),
        (1948, "К. Шеннон", "США · теорія інформації → слава", PURP, False, 0),
    ]
    for yr, nm, sub, col, above, lvl in miles:
        x = xof(yr)
        s += circle(x, ax, 6, col, col, 0)
        if above:
            ytop = ax - 40 - lvl * 70
            s += line(x, ax - 6, x, ytop + 30, col, 1.6)
            box_y = ytop
        else:
            ybot = ax + 44 + lvl * 70
            s += line(x, ax + 6, x, ybot, col, 1.6)
            box_y = ybot
        bw, bh = 188, 52
        bx = min(max(x - bw / 2, 6), W - bw - 6)
        s += rect(bx, box_y, bw, bh, "#ffffff", col, 1.8, 8)
        star = " ★" if yr == 1933 else ""
        s += text(bx + bw / 2, box_y + 21, f"{yr}{star}  {nm}", 11, col, "middle", "bold")
        s += text(bx + bw / 2, box_y + 39, sub, 8.6, INK, "middle")
    s += text(W / 2, 416, "★ 1933, Котельников — перша строга теорема в інженерному контексті; на Заході її не знали понад десятиліття.", 9.6, RED, "middle", "bold")
    save("fig-26-0-2-timeline.svg", s)


# ── Рис. 26.0.3 — телеграф ставить питання (внесок Найквіста) ─────────────────
def figh3_telegraph():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Звідки взялася межа: телеграф і «частота Найквіста»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "1920-ті: скільки імпульсів за секунду можна впхнути в лінію, щоб вони не злилися?", 10.3, GREY, "middle", style="italic")
    # верх: рідкі імпульси — чітко
    ox = 90
    y0, y1 = 110, 165
    s += text(ox, 100, "повільно — імпульси чіткі:", 10.5, GREEN, "start", "bold")
    px = ox
    pts = [(px, y1)]
    for i in range(5):
        pts += [(px, y1), (px + 18, y1), (px + 18, y0), (px + 50, y0), (px + 50, y1), (px + 68, y1)]
        px += 86
    s += poly(pts, GREEN, 2.2)
    # низ: надто часті — зливаються
    yy0, yy1 = 230, 285
    s += text(ox, 218, "надто швидко — імпульси зливаються, годі розрізнити:", 10.5, RED, "start", "bold")
    blur = []
    for i in range(120):
        x = ox + i * 6.3
        y = yy1 - (yy1 - yy0) * (0.5 + 0.42 * math.sin(i * 1.15) * math.exp(-((i % 12) - 6) ** 2 / 40))
        blur.append((x, y))
    s += poly(blur, RED, 1.8)
    s += rect(150, 312, 660, 64, LBLUE, BLUE, 1.5, 10)
    s += text(480, 336, "Найквіст (1928): через лінію зі смугою B можна провести", 11, INK, "middle", "bold")
    s += text(480, 356, "не більше ніж 2·B незалежних імпульсів за секунду.", 11.5, BLUE, "middle", "bold")
    s += text(480, 372, "Це «частота Найквіста» — перший натяк на майбутню теорему дискретизації.", 9.2, GREY, "middle")
    save("fig-26-0-3-telegraph.svg", s)


# ── Рис. 26.0.4 — хто відкрив теорему (мапа авторства) ────────────────────────
def figh4_attribution():
    W, H = 980, 440
    s = header(W, H)
    s += text(W / 2, 32, "Хто насправді відкрив теорему дискретизації", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "не один геній, а ланцюг незалежних людей у різних країнах — кожен додав свою частину", 10.3, GREY, "middle", style="italic")
    # шапка
    cols = [(70, "Ім'я"), (300, "Хто і звідки"), (640, "Рік"), (720, "Внесок")]
    s += rect(40, 74, 900, 30, "#eef1f7", GREY, 1.2, 5)
    for cx, lab in cols:
        s += text(cx, 94, lab, 10.5, INK, "start", "bold")
    rows = [
        ("Е. Уіттекер", "британський математик", "1915", "ряд інтерполяції — математична основа", GREEN, False),
        ("Г. Найквіст", "швед у США (Bell Labs)", "1928", "гранична швидкість, «частота Найквіста»", BLUE, False),
        ("К. Кюпфмюллер", "німецький інженер", "1928", "дискретизація в телеграфії, фільтр", GOLD, False),
        ("В. Котельников", "радянський інженер (Казань)", "1933", "ПЕРША строга теорема; на Заході замовчана", RED, True),
        ("Г. Раабе", "німецький інженер", "1939", "доведення, «умова Раабе»", GOLD, False),
        ("К. Шеннон", "американський математик", "1948–49", "теорія інформації → світова слава", PURP, False),
    ]
    y = 110
    for nm, who, yr, contrib, col, hot in rows:
        bg = LRED if hot else ("#ffffff" if (y // 44) % 2 == 0 else "#f7f8fb")
        s += rect(40, y, 900, 44, bg, (RED if hot else FAINT), (1.8 if hot else 1), 5)
        s += text(70, y + 27, nm + (" ★" if hot else ""), 11, col, "start", "bold")
        s += text(300, y + 27, who, 9.6, INK, "start")
        s += text(640, y + 27, yr, 10, INK, "start", "bold")
        s += text(720, y + 27, contrib, 9.4, GREY, "start")
        y += 48
    s += rect(40, y + 4, 900, 48, LGRN, GREEN, 1.4, 8)
    s += text(W / 2, y + 24, "Теорему відкривали НЕЗАЛЕЖНО — тому в неї стільки імен:", 10.6, INK, "middle", "bold")
    s += text(W / 2, y + 42, "Найквіст–Шеннон, Уіттекер–Шеннон, Котельников… Це КОЛЕКТИВНИЙ здобуток, а не одна нація.", 9.8, GREEN, "middle", "bold")
    save("fig-26-0-4-attribution.svg", s)


# ── Рис. 26.0.5 — спадок: від теореми до твого АЦП ───────────────────────────
def figh5_legacy():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Спадок: одне правило — під усім цифровим світом", 18.5, INK, "middle", "bold")
    s += text(W / 2, 54, "щойно сигнал треба «оцифрувати», працює теорема дискретизації — від музики до твого давача", 10.3, GREY, "middle", style="italic")
    # центральний вузол
    cx, cy = 480, 150
    s += circle(cx, cy, 52, LAMB, GOLD, 2.4)
    s += text(cx, cy - 4, "теорема", 12, INK, "middle", "bold")
    s += text(cx, cy + 14, "дискретизації", 11, INK, "middle", "bold")
    apps = [
        (150, 120, "Цифрове аудіо", "CD, MP3, телефон", BLUE),
        (150, 250, "Цифрове фото/відео", "сенсори, камери", GREEN),
        (810, 120, "Цифрова телефонія", "PCM, T1 (§25.6)", PURP),
        (810, 250, "Кожен АЦП", "давачі, ESP32", RED),
    ]
    for x, y, t, sub, col in apps:
        left = x < cx
        s += rect(x - 75, y - 30, 150, 60, "#ffffff", col, 1.8, 10)
        s += text(x, y - 6, t, 10.6, col, "middle", "bold")
        s += text(x, y + 14, sub, 9, GREY, "middle")
        # стрілка до/від центру
        if left:
            s += arrow(x + 75, y, cx - 50, cy, col, 1.8)
        else:
            s += arrow(x - 75, y, cx + 50, cy, col, 1.8)
    s += rect(150, 312, 660, 50, LGRN, GREEN, 1.4, 10)
    s += text(480, 334, "Скромний АЦП у твоєму ESP32 — прямий нащадок цієї ідеї:", 10.5, INK, "middle", "bold")
    s += text(480, 352, "виміряти світ рівно стільки разів, скільки треба, — і не втратити нічого.", 9.6, GREY, "middle")
    save("fig-26-0-5-legacy.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §26.1 АЦП: перетворити напругу в число — fig-26-1-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 26.1.1 — АЦП — дзеркало ЦАП ──────────────────────────────────────────
def fig11_adc_mirror_dac():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 32, "АЦП — дзеркало ЦАП: той самий міст, протилежні напрями", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "ЦАП перетворює число на напругу (§25.6); АЦП — навпаки, напругу на число", 10.5, GREY, "middle", style="italic")
    s += rect(110, 150, 200, 92, LBLUE, BLUE, 2, 12)
    s += text(210, 186, "ЦИФРА", 14, BLUE, "middle", "bold")
    s += text(210, 210, "число 0 … 2ᴺ−1", 11, INK, "middle")
    s += rect(630, 150, 200, 92, LGRN, GREEN, 2, 12)
    s += text(730, 186, "АНАЛОГ", 14, GREEN, "middle", "bold")
    s += text(730, 210, "напруга 0 … Vref", 11, INK, "middle")
    s += arrow(310, 174, 630, 174, BLUE, 2.6)
    s += text(470, 162, "ЦАП: dacWrite  (число → напруга)", 11, BLUE, "middle", "bold")
    s += arrow(630, 218, 310, 218, RED, 2.6)
    s += text(470, 240, "АЦП: analogRead  (напруга → число)", 11, RED, "middle", "bold")
    s += rect(150, 292, 640, 50, LAMB, GOLD, 1.4, 10)
    s += text(470, 316, "Це одна й та сама відповідність «код ↔ напруга», прочитана у два боки.", 10.3, INK, "middle", "bold")
    s += text(470, 334, "Знаєш ЦАП — уже наполовину знаєш АЦП: він робить зворотне.", 9.4, GREY, "middle")
    save("fig-26-1-1-adc-mirror-dac.svg", s)


# ── Рис. 26.1.2 — вхідний міст: світ → давач → напруга → АЦП → число ──────────
def fig12_bridge():
    W, H = 980, 330
    s = header(W, H)
    s += text(W / 2, 32, "АЦП — вхідний міст: усе, що процесор «відчуває», проходить крізь нього", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "аналоговий світ перетворюється на числа саме тут", 10.5, GREY, "middle", style="italic")
    boxes = [
        (95, "Аналоговий світ", "темп.·світло·звук", GREEN, False),
        (290, "Давач", "(sensor)", INK, False),
        (470, "Напруга", "0 … ~3.3 В", BLUE, False),
        (655, "АЦП", "(ADC)", RED, True),
        (855, "Число → код", "процесор", PURP, False),
    ]
    yb, hb, half = 130, 76, 66
    for x, t1, t2, col, hot in boxes:
        fill = LRED if hot else "#ffffff"
        s += rect(x - half, yb, 2 * half, hb, fill, col, (2.6 if hot else 1.8), 10)
        s += text(x, yb + 32, t1, 11.5, col, "middle", "bold")
        s += text(x, yb + 53, t2, 9.2, GREY, "middle")
    for i in range(len(boxes) - 1):
        x1 = boxes[i][0] + half
        x2 = boxes[i + 1][0] - half
        s += arrow(x1, yb + hb / 2, x2, yb + hb / 2, INK, 2.2)
    s += text(655, yb - 12, "тут — перетворення", 9, RED, "middle", "bold")
    s += rect(150, 250, 680, 52, LBLUE, BLUE, 1.4, 10)
    s += text(490, 273, "Майже кожен давач урешті впирається в АЦП:", 10.5, INK, "middle", "bold")
    s += text(490, 291, "без нього процесор «сліпий» до аналогового світу.", 9.5, GREY, "middle")
    save("fig-26-1-2-bridge.svg", s)


# ── Рис. 26.1.3 — передавальна характеристика: напруга → код ──────────────────
def fig13_transfer():
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 32, "АЦП: вхідна напруга перетворюється на код (дзеркало рис. 25.6.2)", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "тепер навпаки: на вході — напруга (вісь X), на виході — код (вісь Y)", 10.3, GREY, "middle", style="italic")
    ox, oy = 120, 360
    topx, topy = 800, 95
    s += arrow(ox, oy, ox, topy - 12, INK, 2)
    s += arrow(ox, oy, topx + 14, oy, INK, 2)
    s += text(ox - 12, topy - 2, "код", 11, INK, "end", "bold")
    s += text(ox - 12, topy + 14, "2ᴺ−1", 9.5, RED, "end")
    s += text(topx + 6, oy + 26, "вхідна напруга Vin (0 … Vref)", 11, INK, "middle", "bold")
    steps = 16
    x_lo, x_hi = ox, topx
    y_lo, y_hi = oy, topy + 18
    pts = []
    for k in range(steps):
        xa = x_lo + (x_hi - x_lo) * k / steps
        xb = x_lo + (x_hi - x_lo) * (k + 1) / steps
        yk = y_lo + (y_hi - y_lo) * k / steps
        pts.append((xa, yk))
        pts.append((xb, yk))
    pts.append((x_hi, y_hi))
    s += poly(pts, RED, 2.6)
    xmid = (x_lo + x_hi) / 2
    ymid = (y_lo + y_hi) / 2
    s += line(xmid, oy, xmid, ymid, GREEN, 1.3, dash="5,4")
    s += line(ox, ymid, xmid, ymid, GREEN, 1.3, dash="5,4")
    s += circle(xmid, ymid, 4, GREEN, GREEN, 0)
    s += text(xmid + 8, ymid - 8, "Vref/2 → середній код", 9.5, GREEN, "start", "bold")
    s += text(ox + 8, oy - 8, "0 В → код 0", 9.5, BLUE, "start", "bold")
    s += text(x_hi - 4, y_hi - 8, "Vref → код 2ᴺ−1", 9.5, RED, "end", "bold")
    s += rect(150, 372, 640, 44, LAMB, GOLD, 1.4, 8)
    s += text(470, 390, "Кожна вхідна напруга → найближчий код. ESP32: 12 біт = 4096 рівнів.", 10.3, INK, "middle", "bold")
    s += text(470, 408, "Скільки рівнів і який крок — деталі теми §26.3; проти чого Vref — §26.4.", 9.3, GREY, "middle")
    save("fig-26-1-3-transfer.svg", s)


# ── Рис. 26.1.4 — analogRead: пін → число → напруга ──────────────────────────
def fig14_analogread():
    W, H = 960, 350
    s = header(W, H)
    s += text(W / 2, 32, "У коді це один рядок: analogRead дає число", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "ніжка → АЦП → ціле 0…4095; назад у вольти — множенням на крок", 10.3, GREY, "middle", style="italic")
    s += rect(70, 120, 150, 70, LGRN, GREEN, 1.8, 10)
    s += text(145, 150, "ніжка", 12, GREEN, "middle", "bold")
    s += text(145, 170, "GPIO34", 10, INK, "middle")
    s += arrow(220, 155, 300, 155, INK, 2.2)
    s += text(260, 144, "Vin", 9.5, BLUE, "middle", "bold")
    s += rect(300, 120, 150, 70, LRED, RED, 1.8, 10)
    s += text(375, 150, "АЦП", 12, RED, "middle", "bold")
    s += text(375, 170, "12 біт", 10, INK, "middle")
    s += arrow(450, 155, 540, 155, INK, 2.2)
    s += rect(540, 120, 160, 70, LBLUE, BLUE, 1.8, 10)
    s += text(620, 150, "число", 12, BLUE, "middle", "bold")
    s += text(620, 170, "0 … 4095", 10, INK, "middle")
    s += rect(80, 230, 800, 96, "#fbfcff", GREY, 1.4, 10)
    s += text(100, 258, "int  n = analogRead(34);      // напр., n = 2048", 12.5, INK, "start", "bold")
    s += text(100, 284, "float v = n * 3.3 / 4095;     // → v ≈ 1.65 В", 12.5, INK, "start", "bold")
    s += text(100, 310, "n — «який це щабель», v — назад у вольти (крок ≈ 3.3/4095 ≈ 0.8 мВ)", 10, GREY, "start")
    save("fig-26-1-4-analogread.svg", s)


# ── Рис. 26.1.5 — карта застосувань АЦП ──────────────────────────────────────
def fig15_applications():
    W, H = 960, 420
    s = header(W, H)
    s += text(W / 2, 32, "Де працює АЦП: майже кожен давач читають саме ним", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "усе, що дає змінну напругу, стає числом через АЦП", 10.5, GREY, "middle", style="italic")
    rows = [
        ("Потенціометр / ручка", "поворот → напруга подільника", GREEN),
        ("Давач температури", "тепло → напруга (термістор, LM35)", RED),
        ("Фоторезистор (LDR)", "світло → опір → напруга", GOLD),
        ("Мікрофон", "звук → коливання напруги", PURP),
        ("Напруга батареї", "подільник → виміряти заряд", BLUE),
        ("Джойстик", "дві осі → дві напруги (два канали)", "#2aa198"),
    ]
    y = 90
    for t, how, col in rows:
        s += rect(60, y, 840, 46, "#fbfcff", col, 1.6, 9)
        s += text(82, y + 29, t, 12, col, "start", "bold")
        s += text(430, y + 29, how, 10.3, INK, "start")
        y += 52
    s += text(W / 2, 408, "Спільне одне: фізична величина → напруга → АЦП → число, з яким працює код.", 10, GREY, "middle", "bold")
    save("fig-26-1-5-applications.svg", s)


# ── Рис. 26.1.6 — АЦП як лінійка: знайти найближчий щабель ────────────────────
def fig16_levelfinder():
    W, H = 900, 420
    s = header(W, H)
    s += text(W / 2, 32, "Що робить АЦП по суті: знаходить найближчий «щабель»", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "діапазон 0…Vref поділено на рівні; АЦП каже, до якого з них напруга найближча", 10.3, GREY, "middle", style="italic")
    sx = 360
    y0, y1 = 360, 100
    nlev = 8
    s += line(sx, y0, sx, y1, INK, 2.4)
    for k in range(nlev + 1):
        yy = y0 + (y1 - y0) * k / nlev
        s += line(sx - 8, yy, sx + 8, yy, GREY, 1.4)
        s += text(sx - 16, yy + 4, f"код {k}", 9, GREY, "end")
        volt = 3.3 * k / nlev
        s += text(sx + 16, yy + 4, f"{volt:.2f} В", 9, BLUE, "start")
    # вхідна напруга між щаблями
    vin = 3.3 * 4.65 / nlev
    yv = y0 + (y1 - y0) * (4.65 / nlev)
    s += arrow(150, yv, sx - 9, yv, RED, 2.6)
    s += text(150, yv - 10, "Vin (будь-яка)", 10.5, RED, "start", "bold")
    # найближчий щабель = код 5
    yk = y0 + (y1 - y0) * (5 / nlev)
    s += circle(sx, yk, 6, RED, RED, 0)
    s += arrow(sx + 90, yk - 30, sx + 12, yk - 2, RED, 2)
    s += text(sx + 95, yk - 34, "найближчий → код 5", 10.5, RED, "start", "bold")
    s += rect(150, 372, 600, 42, LAMB, GOLD, 1.4, 9)
    s += text(450, 390, "Округлення до найближчого щабля — звідси й похибка квантування.", 10, INK, "middle", "bold")
    s += text(450, 407, "ЯК саме АЦП шукає щабель (SAR, дельта-сигма) — тема §26.8.", 9, GREY, "middle")
    save("fig-26-1-6-level-finder.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §26.2 Дискретизація й квантування — fig-26-2-k
# ═════════════════════════════════════════════════════════════════════════════

def _minisine(ox, cx, cy, w, amp, n, col, dots=False, M=8):
    """Маленька синусоїда для оглядових схем; dots — позначити відліки."""
    pts = []
    for i in range(n + 1):
        x = cx + w * (i / n - 0.5)
        y = cy - amp * math.sin(2 * math.pi * 1.5 * i / n)
        pts.append((x, y))
    s = poly(pts, col, 2.0)
    if dots:
        for j in range(M + 1):
            x = cx + w * (j / M - 0.5)
            y = cy - amp * math.sin(2 * math.pi * 1.5 * j / M)
            s += circle(x, y, 2.6, col, col, 0)
    return s


# ── Рис. 26.2.1 — «напруга → число» — це два кроки ───────────────────────────
def fig21_two_steps():
    W, H = 980, 320
    s = header(W, H)
    s += text(W / 2, 32, "«Напруга → число» — це насправді ДВА окремі кроки", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "спершу дискретизація (розбити час на миті), потім квантування (округлити рівень)", 10.3, GREY, "middle", style="italic")
    yc = 150
    s += text(110, 96, "неперервний сигнал", 10, GREY, "middle")
    s += _minisine(0, 110, yc, 130, 34, 60, GREY)
    s += arrow(180, yc, 250, yc, INK, 2.2)
    s += rect(250, 118, 150, 64, LBLUE, BLUE, 1.8, 10)
    s += text(325, 144, "Крок 1", 11, BLUE, "middle", "bold")
    s += text(325, 163, "Дискретизація", 10, INK, "middle")
    s += text(325, 178, "(у часі)", 8.6, GREY, "middle")
    s += arrow(400, yc, 470, yc, INK, 2.2)
    s += text(540, 96, "відліки (у часі)", 10, BLUE, "middle")
    s += _minisine(0, 540, yc, 130, 34, 60, GREY, dots=True, M=8)
    s += arrow(610, yc, 680, yc, INK, 2.2)
    s += rect(680, 118, 150, 64, LGRN, GREEN, 1.8, 10)
    s += text(755, 144, "Крок 2", 11, GREEN, "middle", "bold")
    s += text(755, 163, "Квантування", 10, INK, "middle")
    s += text(755, 178, "(за рівнем)", 8.6, GREY, "middle")
    s += arrow(830, yc, 895, yc, INK, 2.2)
    s += text(940, 132, "2048", 11, INK, "middle", "bold")
    s += text(940, 150, "2103", 11, INK, "middle", "bold")
    s += text(940, 168, "1990", 11, INK, "middle", "bold")
    s += rect(150, 232, 680, 64, LAMB, GOLD, 1.4, 10)
    s += text(490, 256, "Час і значення — дві РІЗНІ неперервності; кожну дискретизують окремо.", 10.5, INK, "middle", "bold")
    s += text(490, 276, "Дискретизація робить дискретним ЧАС, квантування — ЗНАЧЕННЯ. Разом — число за миттю.", 9.4, GREY, "middle")
    save("fig-26-2-1-two-steps.svg", s)


# ── Рис. 26.2.2 — крок 1: дискретизація (знімки в часі) ───────────────────────
def fig22_sampling():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Крок 1 — дискретизація: знімки сигналу в рівні миті", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "значення беруть лише в моменти 0, T, 2T, …; між ними АЦП «не дивиться»", 10.3, GREY, "middle", style="italic")
    ox, mid, A = 80, 200, 80
    s += line(ox, mid, 905, mid, FAINT, 1.4)
    sig = []
    N = 300
    for i in range(N + 1):
        x = ox + 820 * i / N
        y = mid - A * (0.8 * math.sin(2 * math.pi * 2 * i / N) + 0.2 * math.sin(2 * math.pi * 5 * i / N))
        sig.append((x, y))
    s += poly(sig, GREY, 1.8)
    M = 16
    for j in range(M + 1):
        x = ox + 820 * j / M
        yv = mid - A * (0.8 * math.sin(2 * math.pi * 2 * j / M) + 0.2 * math.sin(2 * math.pi * 5 * j / M))
        s += line(x, 90, x, 330, FAINT, 1)
        s += line(x, mid, x, yv, BLUE, 1.3, dash="3,3")
        s += circle(x, yv, 3.4, BLUE, BLUE, 0)
    # позначка періоду
    x0 = ox + 820 * 5 / M
    x1 = ox + 820 * 6 / M
    s += line(x0, 320, x1, 320, RED, 2)
    s += text((x0 + x1) / 2, 338, "T", 11, RED, "middle", "bold")
    s += text((x0 + x1) / 2, 352, "період", 8.5, GREY, "middle")
    s += rect(150, 96, 360, 40, LBLUE, BLUE, 1.3, 8)
    s += text(330, 120, "fs = 1/T — частота дискретизації", 10, INK, "middle", "bold")
    s += text(W / 2, 372, "Після цього кроку час уже дискретний, але кожен відлік — ще ТОЧНЕ значення. (Як часто брати — §26.5.)", 9.6, GREY, "middle", "bold")
    save("fig-26-2-2-sampling.svg", s)


# ── Рис. 26.2.3 — крок 2: квантування (округлення за рівнем) ──────────────────
def fig23_quantization():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 32, "Крок 2 — квантування: округлити значення до найближчого рівня", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "доступні лише рівні-щаблі; точне значення «приклеюють» до найближчого", 10.3, GREY, "middle", style="italic")
    sx, y0, y1 = 360, 330, 90
    nlev = 8
    levs = []
    for k in range(nlev + 1):
        yy = y0 + (y1 - y0) * k / nlev
        levs.append(yy)
        s += line(220, yy, 620, yy, FAINT, 1.2)
        s += text(210, yy + 4, f"рівень {k}", 8.6, GREY, "end")
    # точне значення між рівнями 5 і 6, ближче до 5
    frac = 5.32
    yv = y0 + (y1 - y0) * frac / nlev
    s += line(250, yv, 590, yv, BLUE, 1.6, dash="5,3")
    s += circle(420, yv, 4.5, BLUE, BLUE, 0)
    s += text(250, yv - 8, "точне значення відліку", 9.5, BLUE, "start", "bold")
    # округлення до рівня 5
    yk = y0 + (y1 - y0) * 5 / nlev
    s += circle(540, yk, 6, GREEN, GREEN, 0)
    s += arrow(440, yv, 528, yk, GREEN, 2)
    s += text(560, yk + 4, "→ рівень 5 (код)", 10, GREEN, "start", "bold")
    # дужка похибки
    s += line(650, yv, 650, yk, RED, 2)
    s += line(645, yv, 655, yv, RED, 2)
    s += line(645, yk, 655, yk, RED, 2)
    s += text(660, (yv + yk) / 2 + 4, "похибка ≤ ½ кроку", 9.5, RED, "start", "bold")
    s += rect(150, 348, 640, 24, LAMB, GOLD, 1.2, 6)
    s += text(470, 365, "Крок між рівнями = LSB. Скільки рівнів (біт) і який крок у мВ — §26.3.", 9.6, INK, "middle", "bold")
    save("fig-26-2-3-quantization.svg", s)


# ── Рис. 26.2.4 — сітка час × рівень ─────────────────────────────────────────
def fig24_grid():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Разом — сітка: час (стовпці) × рівень (рядки)", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "АЦП «приклеює» сигнал до найближчого вузла сітки; кожен вимір = (мить, рівень) = число", 10.3, GREY, "middle", style="italic")
    ox, oy = 90, 340
    rx, ty = 880, 90
    ncol, nrow = 16, 8
    for c in range(ncol + 1):
        x = ox + (rx - ox) * c / ncol
        s += line(x, ty, x, oy, FAINT, 1)
    for r in range(nrow + 1):
        y = oy + (ty - oy) * r / nrow
        s += line(ox, y, rx, y, FAINT, 1)
    s += text(ox - 6, oy + 22, "час →", 10, INK, "start", "bold")
    s += text(ox - 12, ty + 2, "рівень", 10, INK, "end", "bold")
    # сигнал
    sig = []
    A = (oy - ty) * 0.42
    mid = (oy + ty) / 2
    for i in range(241):
        x = ox + (rx - ox) * i / 240
        y = mid - A * (0.8 * math.sin(2 * math.pi * 2 * i / 240) + 0.2 * math.sin(2 * math.pi * 4 * i / 240 + 0.6))
        sig.append((x, y))
    s += poly(sig, GREY, 1.8)
    # приклеєні відліки до вузлів
    for c in range(ncol + 1):
        x = ox + (rx - ox) * c / ncol
        yv = mid - A * (0.8 * math.sin(2 * math.pi * 2 * c / ncol) + 0.2 * math.sin(2 * math.pi * 4 * c / ncol + 0.6))
        # найближчий рядок
        rr = round((yv - oy) / ((ty - oy) / nrow))
        ys = oy + (ty - oy) * rr / nrow
        s += circle(x, ys, 3.6, RED, RED, 0)
    s += rect(180, 360, 600, 30, LRED, RED, 1.3, 8)
    s += text(480, 380, "Червоні точки — те, що реально запам'ятає АЦП: вузли сітки, а не сам сигнал.", 9.8, INK, "middle", "bold")
    save("fig-26-2-4-grid.svg", s)


# ── Рис. 26.2.5 — семпл-холд: «заморозити» напругу на час виміру ──────────────
def fig25_sample_hold():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Семпл-холд: напругу «заморожують», поки АЦП її міряє", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "перетворення триває час; якби напруга під час виміру «їхала», результат був би хибним", 10.3, GREY, "middle", style="italic")
    # схема
    s += text(140, 110, "вхід Vin", 10, BLUE, "middle", "bold")
    s += line(90, 130, 175, 130, INK, 2)
    # ключ
    s += circle(178, 130, 3, INK, INK, 0)
    s += line(178, 130, 214, 116, INK, 2)
    s += circle(220, 130, 3, INK, INK, 0)
    s += text(200, 104, "ключ", 8.6, GREY, "middle")
    s += line(220, 130, 290, 130, INK, 2)
    # вузол + конденсатор до землі
    s += circle(290, 130, 3, INK, INK, 0)
    s += line(290, 130, 290, 160, INK, 2)
    s += line(270, 160, 310, 160, INK, 3)
    s += line(275, 168, 305, 168, INK, 3)
    s += line(290, 168, 290, 182, INK, 2)
    s += line(280, 182, 300, 182, INK, 2)
    s += line(284, 187, 296, 187, INK, 2)
    s += line(287, 191, 293, 191, INK, 2)
    s += text(322, 150, "C (тримає)", 9, GREEN, "start", "bold")
    s += line(290, 130, 380, 130, INK, 2)
    s += poly([(380, 112), (380, 148), (420, 130), (380, 112)], INK, 2, fill=LRED)
    s += text(400, 134, "АЦП", 8.5, RED, "middle", "bold")
    s += line(420, 130, 470, 130, INK, 2)
    s += text(500, 134, "→ код", 10, RED, "start", "bold")
    # часова діаграма праворуч: сигнал + утримані сходинки
    ox2, mid2, A2 = 560, 210, 56
    s += line(ox2, mid2, 920, mid2, FAINT, 1.2)
    sig = []
    for i in range(181):
        x = ox2 + 350 * i / 180
        y = mid2 - A2 * math.sin(2 * math.pi * 2 * i / 180)
        sig.append((x, y))
    s += poly(sig, GREY, 1.6)
    Mh = 9
    stair = []
    for j in range(Mh):
        x0 = ox2 + 350 * j / Mh
        x1 = ox2 + 350 * (j + 1) / Mh
        y = mid2 - A2 * math.sin(2 * math.pi * 2 * j / Mh)
        stair.append((x0, y))
        stair.append((x1, y))
        s += circle(x0, y, 2.6, GREEN, GREEN, 0)
    s += poly(stair, GREEN, 2.2)
    s += text(740, 96, "сіре — сигнал; зелене — «заморожені» рівні", 9, INK, "middle")
    s += rect(150, 330, 660, 40, LGRN, GREEN, 1.3, 8)
    s += text(480, 354, "Ключ на мить замкнувся — конденсатор узяв значення — і тримає його, поки АЦП квантує.", 9.7, INK, "middle", "bold")
    save("fig-26-2-5-sample-hold.svg", s)


# ── Рис. 26.2.6 — похибка квантування ────────────────────────────────────────
def fig26_quant_error():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Похибка квантування: ціна округлення за рівнем", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "різниця між сигналом і його сходинкою — невеликий «шум», завжди не більший за ½ кроку", 10.3, GREY, "middle", style="italic")
    ox, mid, A = 80, 150, 64
    s += line(ox, mid, 905, mid, FAINT, 1.2)
    N = 240
    sig = [(ox + 820 * i / N, mid - A * math.sin(2 * math.pi * 1.5 * i / N)) for i in range(N + 1)]
    s += poly(sig, GREY, 1.7)
    step = A / 3.0
    stair = []
    err_curve = []
    for i in range(N + 1):
        x = ox + 820 * i / N
        yv = mid - A * math.sin(2 * math.pi * 1.5 * i / N)
        q = round((mid - yv) / step) * step
        ys = mid - q
        stair.append((x, ys))
        err_curve.append((x, 300 + (ys - yv) * 1.7))
    s += poly(stair, BLUE, 2.0)
    s += text(ox + 6, 92, "сірим — сигнал, синім — квантований (сходинки)", 9.5, INK, "start")
    # графік похибки внизу
    s += line(ox, 300, 905, 300, FAINT, 1.2)
    s += line(ox, 300 - step * 0.85, 905, 300 - step * 0.85, RED, 1, dash="5,4")
    s += line(ox, 300 + step * 0.85, 905, 300 + step * 0.85, RED, 1, dash="5,4")
    s += text(910, 300 - step * 0.85 + 4, "+½ кроку", 8.6, RED, "start", "bold")
    s += text(910, 300 + step * 0.85 + 4, "−½ кроку", 8.6, RED, "start", "bold")
    s += poly(err_curve, GREEN, 1.8)
    s += text(ox + 6, 360, "похибка = сигнал − сходинка (живе у смузі ±½ кроку)", 9.5, GREEN, "start", "bold")
    s += rect(560, 86, 350, 40, LAMB, GOLD, 1.2, 8)
    s += text(735, 104, "дрібніші рівні (більше біт)", 9.4, INK, "middle", "bold")
    s += text(735, 119, "→ менша похибка (§26.3)", 9, GREY, "middle")
    save("fig-26-2-6-quant-error.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §26.3 Біти й роздільність (LSB) — fig-26-3-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 26.3.1 — біти → рівні (степінь двійки) ──────────────────────────────
def fig31_bits_levels():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Біти → рівні: кожен біт ПОДВОЮЄ кількість рівнів", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "роздільність росте за степенем двійки — рівнів = 2 в степені N", 10.5, GREY, "middle", style="italic")
    x0, y = 150, 92
    for i, n in enumerate(range(4, 10)):
        lv = 2 ** n
        w = lv * 1.35
        yy = y + i * 46
        s += rect(x0, yy, w, 28, LBLUE, BLUE, 1.4, 4)
        s += text(x0 - 10, yy + 19, f"{n} біт", 10.5, INK, "end", "bold")
        s += text(x0 + w + 8, yy + 19, f"= {lv} рівнів", 10.5, BLUE, "start", "bold")
    s += rect(150, 372, 640, 36, LAMB, GOLD, 1.4, 8)
    s += text(470, 388, "12 біт = 4096, 16 біт = 65536 — уже й не влазять у рисунок:", 10, INK, "middle", "bold")
    s += text(470, 403, "подвоєння «вибухає». Тому кілька зайвих біт дають дуже дрібну шкалу.", 9.3, GREY, "middle")
    save("fig-26-3-1-bits-levels.svg", s)


# ── Рис. 26.3.2 — крок (LSB): Vref, поділений на рівні ───────────────────────
def fig32_lsb():
    W, H = 900, 440
    s = header(W, H)
    s += text(W / 2, 32, "Крок (LSB): на скільки вольтів один щабель", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "LSB = Vref / (2ᴺ − 1); та сама шкала, але більше біт — дрібніший крок", 10.5, GREY, "middle", style="italic")
    bary0, bary1, barw = 380, 110, 80
    # ліворуч: 4 біти
    bx1 = 250
    s += rect(bx1, bary1, barw, bary0 - bary1, "#ffffff", INK, 1.6)
    for k in range(17):
        yy = bary0 + (bary1 - bary0) * k / 16
        s += line(bx1, yy, bx1 + barw, yy, GREY, 1)
    s += text(bx1 + barw / 2, bary1 - 12, "4 біти", 11, INK, "middle", "bold")
    s += text(bx1 + barw / 2, bary0 + 20, "16 рівнів", 9.5, GREY, "middle")
    s += text(bx1 + barw / 2, bary0 + 36, "крок ≈ 0.22 В", 10, RED, "middle", "bold")
    # праворуч: 8 біт
    bx2 = 560
    s += rect(bx2, bary1, barw, bary0 - bary1, "#ffffff", INK, 1.6)
    for k in range(257):
        yy = bary0 + (bary1 - bary0) * k / 256
        s += line(bx2, yy, bx2 + barw, yy, GREY, 0.4)
    s += text(bx2 + barw / 2, bary1 - 12, "8 біт", 11, INK, "middle", "bold")
    s += text(bx2 + barw / 2, bary0 + 20, "256 рівнів", 9.5, GREY, "middle")
    s += text(bx2 + barw / 2, bary0 + 36, "крок ≈ 12.9 мВ", 10, GREEN, "middle", "bold")
    # позначки Vref
    s += text(bx1 - 14, bary1 + 4, "Vref", 9, BLUE, "end", "bold")
    s += text(bx1 - 14, bary0 + 4, "0", 9, BLUE, "end")
    s += text(bx2 - 14, bary1 + 4, "Vref", 9, BLUE, "end", "bold")
    s += text(bx2 - 14, bary0 + 4, "0", 9, BLUE, "end")
    s += arrow(bx1 + barw + 30, 245, bx2 - 30, 245, INK, 2)
    s += text((bx1 + bx2) / 2 + 40, 236, "+4 біти", 9.5, INK, "middle", "bold")
    s += rect(150, 405, 600, 28, LBLUE, BLUE, 1.3, 7)
    s += text(450, 423, "ESP32 — 12 біт: 4096 рівнів, крок ≈ 0.81 мВ (ще набагато дрібніше).", 10, INK, "middle", "bold")
    save("fig-26-3-2-lsb.svg", s)


# ── Рис. 26.3.3 — зайвий біт: крок ÷2 ────────────────────────────────────────
def fig33_add_bit():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 32, "Що дає один зайвий біт: крок ÷2, рівнів ×2, похибка ÷2", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "додали біт — кожен щабель розділився навпіл", 10.5, GREY, "middle", style="italic")
    # ліворуч: один крок N біт
    x1, yt, yb = 230, 110, 290
    s += line(x1, yt, x1 + 90, yt, INK, 2)
    s += line(x1, yb, x1 + 90, yb, INK, 2)
    s += line(x1 + 45, yt, x1 + 45, yb, BLUE, 2.6)
    s += line(x1 + 38, (yt + yb) / 2, x1 + 52, (yt + yb) / 2, BLUE, 0)
    s += text(x1 + 60, (yt + yb) / 2 + 4, "1 крок", 10.5, BLUE, "start", "bold")
    s += text(x1 + 45, yt - 10, "N біт", 11, INK, "middle", "bold")
    # стрілка
    s += arrow(x1 + 130, (yt + yb) / 2, x1 + 230, (yt + yb) / 2, INK, 2.4)
    s += text(x1 + 180, (yt + yb) / 2 - 12, "+1 біт", 10.5, GREEN, "middle", "bold")
    # праворуч: розділений навпіл
    x2 = x1 + 320
    ymid = (yt + yb) / 2
    s += line(x2, yt, x2 + 90, yt, INK, 2)
    s += line(x2, yb, x2 + 90, yb, INK, 2)
    s += line(x2, ymid, x2 + 90, ymid, GREEN, 2, dash="5,3")
    s += line(x2 + 45, yt, x2 + 45, ymid, GREEN, 2.6)
    s += line(x2 + 45, ymid, x2 + 45, yb, GREEN, 2.6)
    s += text(x2 + 60, (yt + ymid) / 2 + 4, "½ кроку", 10, GREEN, "start", "bold")
    s += text(x2 + 60, (ymid + yb) / 2 + 4, "½ кроку", 10, GREEN, "start", "bold")
    s += text(x2 + 45, yt - 10, "N+1 біт", 11, INK, "middle", "bold")
    s += rect(150, 312, 600, 38, LAMB, GOLD, 1.4, 8)
    s += text(450, 330, "Кожен біт удвічі дрібнить шкалу. Тому 12 біт замість 10 — це крок учетверо менший", 9.6, INK, "middle", "bold")
    s += text(450, 345, "(і похибка квантування теж учетверо менша).", 9, GREY, "middle")
    save("fig-26-3-3-add-bit.svg", s)


# ── Рис. 26.3.4 — роздільність ≠ діапазон ────────────────────────────────────
def fig34_res_vs_range():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 32, "Роздільність ≠ діапазон: крок залежить від ОБОХ", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "крок = діапазон / рівні; змінюй біти АБО Vref — крок поміняється", 10.5, GREY, "middle", style="italic")
    cfgs = [
        (170, "Vref = 3.3 В", "8 біт", 8, 3.3, BLUE),
        (470, "Vref = 3.3 В", "10 біт", 10, 3.3, GREEN),
        (770, "Vref = 1.1 В", "8 біт", 8, 1.1, PURP),
    ]
    bary0, bary1, barw = 330, 110, 64
    for cx, vlab, nlab, n, vref, col in cfgs:
        bx = cx - barw / 2
        s += rect(bx, bary1, barw, bary0 - bary1, "#ffffff", col, 1.6)
        nd = min(2 ** n, 64)
        for k in range(nd + 1):
            yy = bary0 + (bary1 - bary0) * k / nd
            s += line(bx, yy, bx + barw, yy, FAINT, 0.7)
        step = vref / (2 ** n - 1) * 1000
        s += text(cx, bary1 - 28, nlab, 11, col, "middle", "bold")
        s += text(cx, bary1 - 12, vlab, 9.5, INK, "middle")
        s += text(cx, bary0 + 20, f"крок ≈ {step:.2f} мВ", 10, RED, "middle", "bold")
    s += rect(120, 352, 700, 40, LBLUE, BLUE, 1.3, 8)
    s += text(470, 370, "Більше біт при тій самій Vref → дрібніший крок. Менша Vref при тих самих бітах → теж дрібніший!", 9.3, INK, "middle", "bold")
    s += text(470, 386, "(Звідки береться Vref і як її обрати — тема §26.4.)", 9, GREY, "middle")
    save("fig-26-3-4-res-vs-range.svg", s)


# ── Рис. 26.3.5 — поширені роздільності ──────────────────────────────────────
def fig35_table():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Поширені роздільності та їхній крок (при Vref ≈ 3.3 В)", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "від грубих 8 біт до прецизійних 24 — кожні +2 біти дрібнять крок учетверо", 10.3, GREY, "middle", style="italic")
    s += rect(50, 74, 860, 30, "#eef1f7", GREY, 1.2, 5)
    for cx, lab in [(70, "Роздільність"), (260, "Рівнів"), (470, "Крок @3.3 В"), (650, "Де трапляється")]:
        s += text(cx, 94, lab, 10.5, INK, "start", "bold")
    rows = [
        ("8 біт", "256", "≈ 12.9 мВ", "прості МК, іграшки", GREY, False),
        ("10 біт", "1024", "≈ 3.2 мВ", "Arduino Uno (AVR)", BLUE, False),
        ("12 біт", "4096", "≈ 0.81 мВ", "ESP32, STM32", RED, True),
        ("16 біт", "65 536", "≈ 50 мкВ", "точні вимірювання", GREEN, False),
        ("24 біти", "16.7 млн", "≈ 0.2 мкВ", "аудіо, ваги, тензо", PURP, False),
    ]
    y = 110
    for res, lv, step, where, col, hot in rows:
        bg = LRED if hot else ("#ffffff" if (y // 52) % 2 == 0 else "#f7f8fb")
        s += rect(50, y, 860, 46, bg, (RED if hot else FAINT), (1.8 if hot else 1), 5)
        s += text(70, y + 29, res + (" ★ ESP32" if hot else ""), 11, col, "start", "bold")
        s += text(260, y + 29, lv, 10.5, INK, "start")
        s += text(470, y + 29, step, 10.5, INK, "start", "bold")
        s += text(650, y + 29, where, 10, GREY, "start")
        y += 52
    s += text(W / 2, 388, "Більше біт — дрібніший крок, але повільніше, дорожче й чутливіше до шуму.", 9.6, GREY, "middle", "bold")
    save("fig-26-3-5-table.svg", s)


# ── Рис. 26.3.6 — корисні біти й шум ─────────────────────────────────────────
def fig36_useful_bits():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 32, "Скільки біт насправді корисні: шум підмиває молодші", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "нижні біти «миготять» від шуму; реально корисних (ENOB) — менше за номінальні", 10.3, GREY, "middle", style="italic")
    nbits = 12
    cx, cw, ch = 360, 300, 24
    y0 = 90
    noise = 3
    for i in range(nbits):
        bitidx = nbits - 1 - i
        yy = y0 + i * 26
        useful = i < (nbits - noise)
        fill = LBLUE if useful else FAINT
        col = BLUE if useful else GREY
        s += rect(cx, yy, cw, ch, fill, col, 1.4, 3)
        tag = "MSB" if bitidx == nbits - 1 else ("LSB" if bitidx == 0 else "")
        s += text(cx - 12, yy + 17, f"біт {bitidx} {tag}", 9.5, col, "end", "bold")
        if not useful:
            s += text(cx + cw / 2, yy + 17, "≈ тоне в шумі", 9.5, RED, "middle", "bold")
        else:
            s += text(cx + cw / 2, yy + 17, "корисний", 9, BLUE, "middle")
    s += line(cx, y0 + (nbits - noise) * 26 + 2, cx + cw, y0 + (nbits - noise) * 26 + 2, RED, 2, dash="6,3")
    s += text(cx + cw + 16, y0 + (nbits - noise) * 26 + 6, "поріг шуму", 9.5, RED, "start", "bold")
    s += rect(120, 372, 700, 40, LGRN, GREEN, 1.3, 8)
    s += text(470, 390, "Динамічний діапазон ≈ 6 дБ на біт (12 біт ≈ 72 дБ). Та реально корисних біт (ENOB)", 9.4, INK, "middle", "bold")
    s += text(470, 405, "завжди менше за номінал — бо є шум. Як його приборкати — §26.6 та §26.7.", 9, GREY, "middle")
    save("fig-26-3-6-useful-bits.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §26.4 Опорна напруга (reference) — fig-26-4-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 26.4.1 — АЦП міряє відношення до Vref ───────────────────────────────
def fig41_ratio():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 32, "АЦП міряє ВІДНОШЕННЯ до Vref, а не самі вольти", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "код = (Vin / Vref) × максимум; Vref — це «що вважати повною шкалою»", 10.5, GREY, "middle", style="italic")
    bx, by0, by1, bw = 290, 330, 100, 90
    s += rect(bx, by1, bw, by0 - by1, "#ffffff", INK, 1.8)
    s += text(bx - 12, by1 + 4, "Vref", 10.5, BLUE, "end", "bold")
    s += text(bx - 12, by0 + 4, "0", 10.5, BLUE, "end")
    s += text(bx - 12, by1 - 10, "(повна шкала)", 8.5, GREY, "end")
    frac = 0.62
    vy = by0 + (by1 - by0) * frac
    s += rect(bx, vy, bw, by0 - vy, LGRN, GREEN, 1.4)
    s += text(bx + bw / 2, (vy + by0) / 2 + 4, "Vin", 13, GREEN, "middle", "bold")
    s += line(bx + bw + 18, vy, bx + bw + 18, by0, RED, 1.6)
    s += line(bx + bw + 13, vy, bx + bw + 23, vy, RED, 1.6)
    s += line(bx + bw + 13, by0, bx + bw + 23, by0, RED, 1.6)
    s += text(bx + bw + 28, (vy + by0) / 2 + 4, "62 % від Vref", 10.5, RED, "start", "bold")
    s += arrow(bx + bw + 200, 215, bx + bw + 290, 215, INK, 2.4)
    s += rect(bx + bw + 290, 188, 150, 56, LBLUE, BLUE, 1.6, 10)
    s += text(bx + bw + 365, 212, "код", 12, BLUE, "middle", "bold")
    s += text(bx + bw + 365, 232, "= 62 % × макс", 9.5, INK, "middle")
    s += rect(150, 348, 620, 26, LAMB, GOLD, 1.2, 6)
    s += text(460, 366, "АЦП питає не «скільки вольтів?», а «яка ти частка від Vref?».", 10, INK, "middle", "bold")
    save("fig-26-4-1-ratio.svg", s)


# ── Рис. 26.4.2 — та сама напруга, різний Vref → різний код ──────────────────
def fig42_same_vin():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 32, "Та сама напруга, різний Vref → РІЗНИЙ код", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "без знання Vref код нічого не каже про вольти", 10.5, GREY, "middle", style="italic")
    vin = 0.55
    cfgs = [(250, 3.3, BLUE), (650, 1.1, PURP)]
    by0, by1, bw = 330, 110, 80
    for cx, vref, col in cfgs:
        bx = cx - bw / 2
        s += rect(bx, by1, bw, by0 - by1, "#ffffff", col, 1.8)
        s += text(cx, by1 - 12, f"Vref = {vref} В", 11, col, "middle", "bold")
        s += text(bx - 10, by0 + 4, "0", 9, INK, "end")
        # Vin line
        vy = by0 + (by1 - by0) * (vin / vref)
        s += line(bx - 6, vy, bx + bw + 6, vy, GREEN, 2.4)
        s += text(bx + bw + 10, vy + 4, "Vin = 0.55 В", 9.5, GREEN, "start", "bold")
        frac = vin / vref
        code = round(frac * 4095)
        s += text(cx, by0 + 24, f"{frac*100:.0f} % → код {code}", 10.5, RED, "middle", "bold")
    s += rect(150, 356, 620, 36, LBLUE, BLUE, 1.3, 8)
    s += text(460, 374, "0.55 В — це 17 % від 3.3 В, але аж 50 % від 1.1 В.", 10, INK, "middle", "bold")
    s += text(460, 388, "Той самий вхід дає код 683 або 2048 — усе залежить від Vref.", 9, GREY, "middle")
    save("fig-26-4-2-same-vin.svg", s)


# ── Рис. 26.4.3 — дрейф Vref зсуває ВСІ виміри ───────────────────────────────
def fig43_drift():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 32, "Vref — це лінійка: попливе вона, попливуть УСІ виміри", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "АЦП довіряє Vref беззастережно; похибка опорної на 1 % = похибка кожного виміру на 1 %", 10, GREY, "middle", style="italic")
    # дві лінійки: правильна й «попливла»
    y = 150
    s += text(140, y - 34, "правильна Vref = 3.300 В", 10, GREEN, "middle", "bold")
    s += line(60, y, 460, y, GREEN, 2.4)
    for k in range(11):
        x = 60 + 400 * k / 10
        s += line(x, y - 5, x, y + 5, GREEN, 1.4)
    s += text(260, y + 26, "вимір збігається з істиною", 9, GREY, "middle")
    yy = 250
    s += text(150, yy - 34, "«попливла» Vref = 3.40 В (нагрів/просід)", 10, RED, "middle", "bold")
    s += line(60, yy, 472, yy, RED, 2.4)
    for k in range(11):
        x = 60 + 412 * k / 10
        s += line(x, yy - 5, x, yy + 5, RED, 1.4)
    s += text(266, yy + 26, "ті самі вольти → інший код (помилка ≈ 3 %)", 9, RED, "middle", "bold")
    s += rect(560, 110, 320, 200, LAMB, GOLD, 1.5, 12)
    s += text(720, 138, "Тому Vref має бути:", 11, INK, "middle", "bold")
    s += text(580, 168, "• стабільною (не плисти від тепла)", 10, INK, "start")
    s += text(580, 196, "• без шуму (тихою)", 10, INK, "start")
    s += text(580, 224, "• точно відомою (інакше вольти", 10, INK, "start")
    s += text(595, 242, "не порахуєш)", 10, INK, "start")
    s += text(720, 284, "точність Vref = стеля точності", 9.4, RED, "middle", "bold")
    save("fig-26-4-3-drift.svg", s)


# ── Рис. 26.4.4 — три джерела Vref ───────────────────────────────────────────
def fig44_sources():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 32, "Звідки беруть опорну напругу: три джерела", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "від дешевого й грубого до точного й дорожчого", 10.5, GREY, "middle", style="italic")
    cards = [
        (60, "Живлення (VDD)", "просто беруть напругу живлення", "+ дешево, нічого не треба", "− шумить і пливе", RED),
        (340, "Внутрішнє джерело", "вбудований bandgap ≈ 1.1 В", "+ стабільніше, на чипі", "− точність помірна", GOLD),
        (620, "Зовнішнє прецизійне", "окрема ІС (TL431, REFxx)", "+ найточніше й стабільне", "− дорожче, ще деталь", GREEN),
    ]
    for x, t, d, plus, minus, col in cards:
        s += rect(x, 92, 280, 200, "#fbfcff", col, 1.8, 12)
        s += text(x + 140, 122, t, 12.5, col, "middle", "bold")
        s += line(x + 20, 134, x + 260, 134, FAINT, 1.2)
        s += text(x + 140, 158, d, 9.6, INK, "middle")
        s += text(x + 22, 196, plus, 9.8, GREEN, "start", "bold")
        s += text(x + 22, 224, minus, 9.8, RED, "start", "bold")
        s += text(x + 140, 268, ("грубо" if col == RED else ("середньо" if col == GOLD else "точно")), 10, col, "middle", "bold")
    s += arrow(70, 330, 890, 330, GREY, 2)
    s += text(80, 352, "дешево / грубо", 9.5, GREY, "start")
    s += text(890, 352, "дорого / точно", 9.5, GREY, "end")
    save("fig-26-4-4-sources.svg", s)


# ── Рис. 26.4.5 — раціометричне вимірювання ──────────────────────────────────
def fig45_ratiometric():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Раціометрія: коли коливання Vref самознищуються", 18, INK, "middle", "bold")
    s += text(W / 2, 54, "якщо давач і Vref живляться від ОДНОГО джерела, його дрейф скорочується у відношенні", 10, GREY, "middle", style="italic")
    # VDD шина
    s += line(120, 110, 840, 110, RED, 2.6)
    s += text(120, 102, "VDD (живлення)", 10, RED, "start", "bold")
    # подільник/потенціометр
    s += line(250, 110, 250, 150, INK, 2)
    s += rect(232, 150, 36, 120, "#ffffff", INK, 1.8, 3)
    s += text(250, 215, "R", 10, INK, "middle", "bold")
    s += circle(268, 210, 4, GREEN, GREEN, 0)
    s += arrow(268, 210, 320, 210, GREEN, 2)
    s += line(250, 270, 250, 300, INK, 2)
    s += line(228, 300, 272, 300, INK, 2)
    s += line(234, 306, 266, 306, INK, 2)
    s += line(242, 312, 258, 312, INK, 2)
    s += text(250, 290, "до землі", 8.5, GREY, "middle")
    # АЦП
    s += rect(330, 185, 130, 60, LBLUE, BLUE, 1.8, 10)
    s += text(395, 210, "АЦП", 12, BLUE, "middle", "bold")
    s += text(395, 228, "ref = VDD", 9.5, RED, "middle", "bold")
    # ref шина від VDD у АЦП
    s += line(560, 110, 560, 185, RED, 1.8, dash="5,3")
    s += line(460, 130, 560, 130, RED, 1.8, dash="5,3")
    s += text(620, 126, "та сама VDD — як опорна", 9.5, RED, "start")
    s += rect(150, 300, 700, 84, LGRN, GREEN, 1.5, 12)
    s += text(500, 326, "VDD підскочила на 10 %? І сигнал давача, і Vref зросли на ті самі 10 %.", 10.3, INK, "middle", "bold")
    s += text(500, 348, "Код = відношення сигналу до Vref — а воно НЕ змінилося. Дрейф живлення скоротився.", 9.6, INK, "middle")
    s += text(500, 370, "Тому потенціометри й резистивні давачі часто й не потребують точної опорної.", 9.2, GREY, "middle")
    save("fig-26-4-5-ratiometric.svg", s)


# ── Рис. 26.4.6 — Vref в ESP32: внутрішні ~1.1 В + ослаблення ─────────────────
def fig46_esp32_atten():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 32, "Vref в ESP32: внутрішні ≈ 1.1 В + ослаблення входу", 17.5, INK, "middle", "bold")
    s += text(W / 2, 54, "вхід ділять перед АЦП, щоб ≈1.1-вольтова опорна «накрила» більший діапазон", 10, GREY, "middle", style="italic")
    atts = [
        ("0 dB", 1.1, BLUE),
        ("2.5 dB", 1.5, GREEN),
        ("6 dB", 2.2, GOLD),
        ("11 dB", 3.3, RED),
    ]
    x0 = 150
    scale = 200.0  # px per volt
    for i, (lab, fs, col) in enumerate(atts):
        y = 100 + i * 56
        s += text(x0 - 16, y + 16, lab, 11, col, "end", "bold")
        s += rect(x0, y, fs * scale, 30, "#ffffff", col, 1.6, 4)
        s += text(x0 + fs * scale + 10, y + 20, f"0 … ~{fs} В", 10, col, "start", "bold")
    s += text(x0 + 3.3 * scale + 90, 128, "← типове", 9.5, RED, "start", "bold")
    s += text(x0 + 3.3 * scale + 90, 142, "(0..~3.3 В)", 8.6, GREY, "start")
    s += rect(150, 332, 700, 52, LAMB, GOLD, 1.4, 10)
    s += text(500, 354, "Менше ослаблення — вужчий діапазон, зате той самий 12-бітний крок лягає дрібніше.", 9.8, INK, "middle", "bold")
    s += text(500, 374, "Опорна різниться від чипа до чипа (1.0…1.2 В), тому АЦП ESP32 треба калібрувати — §26.6.", 9.2, GREY, "middle")
    save("fig-26-4-6-esp32-atten.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §26.5 Частота дискретизації, Найквіст, аліасинг — fig-26-5-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 26.5.1 — частота Найквіста: треба понад 2 відліки на період ──────────
def fig51_nyquist():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 30, "Правило Найквіста: понад 2 відліки на період", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "fs — частота дискретизації; частота Найквіста fs/2 — найвища, яку ще можна передати", 10.3, GREY, "middle", style="italic")
    # рядок 1: густо
    ox = 90
    for row, (cyc, M, lab, col, ok) in enumerate([
        (1.5, 24, "густо: багато відліків на період — хвиля відновлюється", GREEN, True),
        (1.5, 5, "на межі: трохи більше за 2 відліки на період — ще годиться", GOLD, True),
    ]):
        mid = 120 + row * 130
        A = 44
        s += line(ox, mid, 905, mid, FAINT, 1.2)
        sig = [(ox + 820 * i / 300, mid - A * math.sin(2 * math.pi * cyc * i / 300)) for i in range(301)]
        s += poly(sig, GREY, 1.6)
        for j in range(M + 1):
            x = ox + 820 * j / M
            y = mid - A * math.sin(2 * math.pi * cyc * j / M)
            s += circle(x, y, 3.2, col, col, 0)
        s += text(ox, mid - A - 14, lab, 10, col, "start", "bold")
    s += rect(150, 332, 660, 52, LBLUE, BLUE, 1.4, 10)
    s += text(480, 356, "Правило: fs  >  2 × (найвища частота сигналу).", 12, BLUE, "middle", "bold")
    s += text(480, 376, "Інакше — біда, що зветься аліасингом (наступний рисунок).", 9.5, GREY, "middle")
    save("fig-26-5-1-nyquist.svg", s)


# ── Рис. 26.5.2 — аліасинг: швидка хвиля прикидається повільною ───────────────
def fig52_aliasing():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 30, "Замало знімків — і швидка хвиля прикидається повільною", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "той самий ефект, що «колесо крутиться назад» у кіно: рідкі відліки брешуть про швидкий рух", 10, GREY, "middle", style="italic")
    ox, mid, A = 80, 200, 82
    s += line(ox, mid, 905, mid, FAINT, 1.2)
    fast = [(ox + 820 * i / 400, mid - A * math.sin(2 * math.pi * 7 * i / 400)) for i in range(401)]
    s += poly(fast, GREY, 1.6)
    M = 8
    for j in range(M + 1):
        x = ox + 820 * j / M
        y = mid - A * math.sin(2 * math.pi * 7 * j / M)
        s += line(x, 92, x, 320, FAINT, 1)
        s += circle(x, y, 3.8, BLUE, BLUE, 0)
    ghost = [(ox + 820 * i / 400, mid + A * math.sin(2 * math.pi * 1 * i / 400)) for i in range(401)]
    s += poly(ghost, RED, 2.6)
    s += text(ox + 6, 96, "реальна хвиля (7 коливань) — сіра", 9.5, GREY, "start", "bold")
    s += text(620, 300, "удавана повільна (1 коливання) — аліас", 9.5, RED, "start", "bold")
    s += text(ox + 6, mid + A + 30, "сині точки — рідкі відліки; вони лягають і на сіру, і на червону", 9.3, BLUE, "start", "bold")
    s += rect(560, 86, 350, 26, LAMB, GOLD, 1.2, 6)
    s += text(735, 104, "7 коливань, лише 8 відліків → привид", 9.4, INK, "middle", "bold")
    save("fig-26-5-2-aliasing.svg", s)


# ── Рис. 26.5.3 — складання частот: дзеркало на fs/2 ─────────────────────────
def fig53_folding():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 30, "Як це працює: частоти вище fs/2 «складаються» дзеркалом", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "усе, що вище за Найквіста (fs/2), відбивається назад у чутний діапазон", 10.3, GREY, "middle", style="italic")
    ox, axy = 70, 250
    fs = 1000.0
    x_for = lambda f: ox + 820 * f / fs
    s += arrow(ox, axy, 910, axy, INK, 2)
    s += text(900, axy + 24, "частота, Гц", 10, INK, "middle")
    for f in [0, 250, 500, 750, 1000]:
        x = x_for(f)
        s += line(x, axy - 5, x, axy + 5, GREY, 1.4)
        s += text(x, axy + 22, str(f), 9, GREY, "middle")
    # лінія Найквіста
    xN = x_for(500)
    s += line(xN, 90, xN, axy, RED, 2, dash="6,4")
    s += text(xN, 82, "Найквіст fs/2 = 500", 10, RED, "middle", "bold")
    # справжня частота 300 (лишається)
    s += circle(x_for(300), axy, 5, GREEN, GREEN, 0)
    s += text(x_for(300), axy - 12, "300 — нижче, лишається", 9, GREEN, "middle", "bold")
    # 700 -> складається до 300
    s += circle(x_for(700), axy, 5, BLUE, BLUE, 0)
    s += text(x_for(700), axy - 12, "700", 9.5, BLUE, "middle", "bold")
    s += f'<path d="M {x_for(700):.1f} {axy-6} Q {xN:.1f} {axy-90} {x_for(300):.1f} {axy-6}" fill="none" stroke="{BLUE}" stroke-width="2" stroke-dasharray="5,4"/>\n'
    s += text(xN, 150, "700 → дзеркало → 300", 9.5, BLUE, "middle", "bold")
    s += rect(150, 300, 660, 44, LBLUE, BLUE, 1.3, 9)
    s += text(480, 320, "Аліас(f) = |f − k·fs|. При fs = 1000: сигнал 700 Гц з'явиться як хибні 300 Гц", 9.6, INK, "middle", "bold")
    s += text(480, 337, "— нерозрізнянно від справжніх 300 Гц.", 9, GREY, "middle")
    save("fig-26-5-3-folding.svg", s)


# ── Рис. 26.5.4 — аліас не виправити: дані не скажуть, котра хвиля ─────────────
def fig54_trap():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 30, "Класична пастка: аліас НЕ виправити після оцифрування", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "з самих відліків не скажеш, котра хвиля була насправді — інформацію втрачено назавжди", 10, GREY, "middle", style="italic")
    ox, mid, A = 80, 190, 70
    # ліворуч-вгорі: що зберіг АЦП (тільки точки)
    s += text(ox + 6, 92, "Що зберіг АЦП — лише точки:", 10, INK, "start", "bold")
    M = 8
    dots = []
    for j in range(M + 1):
        x = ox + 820 * j / M
        y = mid - A * math.sin(2 * math.pi * 7 * j / M)
        dots.append((x, y))
    s += line(ox, mid, 905, mid, FAINT, 1.2)
    for (x, y) in dots:
        s += circle(x, y, 4, INK, INK, 0)
    # дві хвилі через ті самі точки
    fast = [(ox + 820 * i / 400, mid - A * math.sin(2 * math.pi * 7 * i / 400)) for i in range(401)]
    ghost = [(ox + 820 * i / 400, mid + A * math.sin(2 * math.pi * 1 * i / 400)) for i in range(401)]
    s += poly(fast, GREY, 1.5, dash="6,4")
    s += poly(ghost, RED, 2.2, dash="6,4")
    s += text(ox + 6, mid + A + 34, "ті самі точки годяться і для швидкої (сіра), і для повільної (червона)", 9.3, INK, "start", "bold")
    s += rect(150, 322, 660, 50, LRED, RED, 1.4, 10)
    s += text(480, 344, "Після дискретизації аліас уже невідрізнянний від справжнього сигналу.", 10, INK, "middle", "bold")
    s += text(480, 362, "Виправити не можна — лише ЗАПОБІГТИ (фільтром і достатньою fs).", 9.5, RED, "middle", "bold")
    save("fig-26-5-4-trap.svg", s)


# ── Рис. 26.5.5 — антиаліасинговий фільтр ────────────────────────────────────
def fig55_antialias():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 30, "Лік: антиаліасинговий фільтр ПЕРЕД АЦП", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "аналоговий ФНЧ зрізає все вище за fs/2, поки воно ще не потрапило в пастку (пор. §25.4)", 10, GREY, "middle", style="italic")
    # ланцюг
    s += text(110, 120, "сигнал + шум", 10, INK, "middle", "bold")
    s += rect(60, 130, 100, 50, LRED, RED, 1.4, 8)
    s += text(110, 160, "є ВЧ-шум", 9, RED, "middle")
    s += arrow(160, 155, 250, 155, INK, 2.2)
    s += rect(250, 125, 150, 60, LGRN, GREEN, 1.8, 10)
    s += text(325, 150, "ФНЧ", 12, GREEN, "middle", "bold")
    s += text(325, 170, "анти-аліас", 9, GREEN, "middle")
    s += arrow(400, 155, 490, 155, INK, 2.2)
    s += rect(490, 130, 110, 50, "#ffffff", INK, 1.4, 8)
    s += text(545, 152, "лише НЧ", 9.5, INK, "middle", "bold")
    s += text(545, 170, "(< fs/2)", 8.6, GREY, "middle")
    s += arrow(600, 155, 690, 155, INK, 2.2)
    s += rect(690, 130, 110, 50, LBLUE, BLUE, 1.6, 8)
    s += text(745, 160, "АЦП", 12, BLUE, "middle", "bold")
    # спектри до/після
    for (sx, lab, hasnoise) in [(180, "до фільтра", True), (560, "після фільтра", False)]:
        ay = 320
        s += line(sx - 70, ay, sx + 110, ay, INK, 1.6)
        xN = sx + 40
        s += line(xN, ay, xN, ay - 90, RED, 1.4, dash="4,3")
        s += text(xN, ay + 16, "fs/2", 8.5, RED, "middle", "bold")
        # НЧ сигнал
        s += line(sx - 40, ay, sx - 40, ay - 70, GREEN, 5)
        s += text(sx - 70, ay - 76, "сигнал", 8.2, GREEN, "start")
        if hasnoise:
            s += line(sx + 75, ay, sx + 75, ay - 50, RED, 5)
            s += text(sx + 60, ay - 56, "ВЧ-шум", 8.2, RED, "start", "bold")
        s += text(sx + 10, ay + 34, lab, 9.5, INK, "middle", "bold")
    s += text(740, 250, "ВЧ-шум зрізано —", 9.3, GREEN, "middle", "bold")
    s += text(740, 266, "складатися нема чому", 9.3, GREY, "middle")
    save("fig-26-5-5-antialias.svg", s)


# ── Рис. 26.5.6 — передискретизація (oversampling) ───────────────────────────
def fig56_oversampling():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 30, "Із запасом: передискретизація (oversampling)", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "беруть fs помітно більшою за 2·fmax — щоб реальний фільтр устиг зрізати й щоб усереднити", 10, GREY, "middle", style="italic")
    # випадок а: впритул
    for row, (lab, fmax_x, fsh_x, col, note) in enumerate([
        ("Впритул (fs = 2·fmax):", 380, 400, RED, "фільтру нема де спадати — потрібна «стіна» (нездійсненно)"),
        ("Із запасом (fs ≫ 2·fmax):", 220, 540, GREEN, "є проміжок — пологий фільтр устигає зрізати ВЧ"),
    ]):
        ay = 150 + row * 110
        ox = 120
        s += text(ox, ay - 42, lab, 11, col, "start", "bold")
        s += line(ox, ay, 860, ay, INK, 1.6)
        # сигнал до fmax
        s += rect(ox, ay - 46, fmax_x - ox, 46, LGRN, GREEN, 1.2)
        s += text((ox + fmax_x) / 2, ay - 22, "сигнал", 9, GREEN, "middle", "bold")
        # лінія fs/2
        s += line(fsh_x, ay - 70, fsh_x, ay, RED, 1.6, dash="5,3")
        s += text(fsh_x, ay - 76, "fs/2", 8.6, RED, "middle", "bold")
        # проміжок
        if fsh_x - fmax_x > 30:
            s += line(fmax_x, ay - 10, fsh_x, ay - 10, GOLD, 2)
            s += text((fmax_x + fsh_x) / 2, ay - 16, "запас", 8.4, GOLD, "middle", "bold")
        s += text(880, ay - 20, "", 8, GREY, "start")
        s += text(ox, ay + 18, note, 9, GREY, "start")
    s += rect(150, 332, 660, 40, LBLUE, BLUE, 1.3, 8)
    s += text(480, 350, "Бонус: удвічі-вчетверо більше відліків можна усереднити —", 9.6, INK, "middle", "bold")
    s += text(480, 366, "менше шуму й трохи «чесніших» біт (пор. §26.3, §26.7).", 9, GREY, "middle")
    save("fig-26-5-6-oversampling.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §26.6 Похибки реального АЦП і калібрування — fig-26-6-k
# ═════════════════════════════════════════════════════════════════════════════

def _axes(s, ox, oy, px, py, xlab="Vin", ylab="код"):
    s += arrow(ox, oy, ox, py - 12, INK, 2)
    s += arrow(ox, oy, px + 14, oy, INK, 2)
    s += text(ox - 10, py - 2, ylab, 10.5, INK, "end", "bold")
    s += text(px + 6, oy + 24, xlab, 10.5, INK, "middle", "bold")
    return s


# ── Рис. 26.6.1 — ідеал проти реальності ─────────────────────────────────────
def fig61_ideal_vs_real():
    W, H = 920, 420
    s = header(W, H)
    s += text(W / 2, 30, "Реальний АЦП відхиляється від ідеальної прямої", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "ідеал — рівна лінія «напруга → код»; справжній має зсув, нахил і вигин", 10.3, GREY, "middle", style="italic")
    ox, oy, px, py = 120, 360, 780, 100
    s = _axes(s, ox, oy, px, py)
    P = lambda xf, yf: (ox + (px - ox) * xf, oy + (py - oy) * max(0, min(1, yf)))
    s += poly([P(0, 0), P(1, 1)], GREY, 2, dash="7,4")
    ax, ay = P(0.82, 0.9)
    s += text(ax, ay, "ідеал", 10.5, GREY, "start", "bold")
    real = []
    for i in range(101):
        xf = i / 100
        yf = 0.08 + 0.84 * xf + 0.06 * math.sin(math.pi * xf)
        real.append(P(xf, yf))
    s += poly(real, RED, 2.8)
    rx, ry = P(0.6, 0.08 + 0.84 * 0.6 + 0.06 * math.sin(math.pi * 0.6))
    s += text(rx + 10, ry + 26, "реальний", 10.5, RED, "start", "bold")
    ox0x, ox0y = P(0, 0.08)
    s += circle(ox0x, ox0y, 4, RED, RED, 0)
    s += text(ox0x + 8, ox0y - 6, "зсув нуля (offset)", 9.4, RED, "start", "bold")
    s += text(px - 6, P(1, 0.92)[1] - 8, "нахил ≠ 1 (gain)", 9.4, RED, "end", "bold")
    bx, by = P(0.5, 0.08 + 0.84 * 0.5 + 0.06)
    s += text(bx + 8, by - 8, "вигин (INL)", 9.4, RED, "start", "bold")
    s += rect(150, 374, 620, 26, LAMB, GOLD, 1.2, 6)
    s += text(460, 392, "Ці відхилення СИСТЕМНІ (повторювані) — отже, їх можна виміряти й виправити.", 9.6, INK, "middle", "bold")
    save("fig-26-6-1-ideal-vs-real.svg", s)


# ── Рис. 26.6.2 — зсув нуля й похибка масштабу ───────────────────────────────
def fig62_offset_gain():
    W, H = 940, 380
    s = header(W, H)
    s += text(W / 2, 30, "Дві «лінійні» похибки: зсув нуля та похибка масштабу", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "обидві лишають криву прямою — тому їх виправляє двоточкове калібрування", 10.3, GREY, "middle", style="italic")
    for col_i, (cx0, title, kind) in enumerate([(70, "Зсув нуля (offset)", "off"), (510, "Похибка масштабу (gain)", "gain")]):
        ox, oy, px, py = cx0 + 50, 320, cx0 + 360, 110
        s = _axes(s, ox, oy, px, py)
        P = lambda xf, yf: (ox + (px - ox) * xf, oy + (py - oy) * max(0, min(1.05, yf)))
        s += poly([P(0, 0), P(1, 1)], GREY, 1.8, dash="6,4")
        if kind == "off":
            s += poly([P(0, 0.18), P(0.82, 1.0)], RED, 2.6)
            xx, yy = P(0, 0.18)
            s += circle(xx, yy, 4, RED, RED, 0)
            s += text(xx + 8, yy - 6, "код ≠ 0 при 0 В", 9, RED, "start", "bold")
            s += text((ox + px) / 2, py - 6, "вся пряма зсунена вгору", 9, INK, "middle")
        else:
            s += poly([P(0, 0), P(1.0, 0.74)], RED, 2.6)
            s += text((ox + px) / 2, py + 2, "нахил не той — повну", 9, INK, "middle")
            s += text((ox + px) / 2, py + 16, "шкалу досягнуто не там", 9, INK, "middle")
        s += text(cx0 + 205, 92, title, 11.5, RED if kind == "off" else GOLD, "middle", "bold")
    s += rect(160, 340, 620, 30, LGRN, GREEN, 1.3, 8)
    s += text(470, 359, "Зсув — додати/відняти константу; масштаб — домножити. Дві точки задають і те, й те.", 9.5, INK, "middle", "bold")
    save("fig-26-6-2-offset-gain.svg", s)


# ── Рис. 26.6.3 — DNL: нерівні щаблі й пропущений код ────────────────────────
def fig63_dnl():
    W, H = 920, 380
    s = header(W, H)
    s += text(W / 2, 30, "DNL: щаблі різної ширини, аж до пропущеного коду", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "диференціальна нелінійність — відхилення ширини кожного щабля від рівного 1 LSB", 10, GREY, "middle", style="italic")
    ox, oy, px, py = 120, 330, 800, 110
    s = _axes(s, ox, oy, px, py)
    # нерівні щаблі
    widths = [1.0, 1.6, 0.6, 1.2, 0.0, 1.4, 0.9, 1.3]  # 0.0 → пропущений код
    total = sum(widths)
    xacc = 0
    yk = 0
    nseg = len(widths)
    pts = []
    for i, w in enumerate(widths):
        x0 = ox + (px - ox) * xacc / total
        xacc += w
        x1 = ox + (px - ox) * xacc / total
        yy = oy + (py - oy) * (i / nseg)
        pts.append((x0, yy))
        pts.append((x1, yy))
        if abs(w) < 0.01:
            mx = x0
            s += text(mx, yy - 8, "пропущений код!", 9, RED, "middle", "bold")
            s += circle(mx, yy, 3.5, RED, RED, 0)
    pts.append((px, py))
    s += poly(pts, BLUE, 2.4)
    # ідеальна для порівняння
    s += poly([(ox, oy), (px, py)], GREY, 1.4, dash="5,4")
    s += text(ox + 12, oy - 8, "вузький щабель", 8.6, GREEN, "start")
    s += text(ox + 150, oy - 70, "широкий щабель", 8.6, GOLD, "start")
    s += rect(160, 346, 600, 26, LAMB, GOLD, 1.2, 6)
    s += text(460, 364, "Якщо щабель «зник» (DNL < −1 LSB), такий код не з'явиться НІКОЛИ.", 9.5, INK, "middle", "bold")
    save("fig-26-6-3-dnl.svg", s)


# ── Рис. 26.6.4 — INL: крива вигинається від прямої ──────────────────────────
def fig64_inl():
    W, H = 900, 380
    s = header(W, H)
    s += text(W / 2, 30, "INL: крива «вигинається» від ідеальної прямої", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "інтегральна нелінійність — накопичене відхилення від прямої лінії", 10.3, GREY, "middle", style="italic")
    ox, oy, px, py = 120, 330, 770, 100
    s = _axes(s, ox, oy, px, py)
    P = lambda xf, yf: (ox + (px - ox) * xf, oy + (py - oy) * max(0, min(1, yf)))
    s += poly([P(0, 0), P(1, 1)], GREY, 1.8, dash="6,4")
    s += text(P(0.8, 0.86)[0], P(0.8, 0.86)[1], "ідеал", 10, GREY, "start", "bold")
    real = [P(i / 100, i / 100 + 0.12 * math.sin(math.pi * i / 100)) for i in range(101)]
    s += poly(real, RED, 2.6)
    # дужка максимального відхилення на x=0.5
    xa, ya = P(0.5, 0.5)
    xb, yb = P(0.5, 0.5 + 0.12)
    s += line(xa, ya, xb, yb, GREEN, 2)
    s += line(xa - 5, ya, xa + 5, ya, GREEN, 2)
    s += line(xb - 5, yb, xb + 5, yb, GREEN, 2)
    s += text(xb + 8, (ya + yb) / 2, "макс. INL", 9.5, GREEN, "start", "bold")
    s += rect(150, 346, 600, 26, LBLUE, BLUE, 1.2, 6)
    s += text(450, 364, "INL не виправити прямою — потрібна крива поправки (багатоточкове калібрування).", 9.4, INK, "middle", "bold")
    save("fig-26-6-4-inl.svg", s)


# ── Рис. 26.6.5 — реальна крива АЦП ESP32 ────────────────────────────────────
def fig65_esp32_curve():
    W, H = 920, 400
    s = header(W, H)
    s += text(W / 2, 30, "АЦП ESP32: помітно нелінійний, особливо по краях", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "біля 0 і біля максимуму крива «завалюється»; надійна — лише середина діапазону", 10, GREY, "middle", style="italic")
    ox, oy, px, py = 110, 340, 800, 110
    s = _axes(s, ox, oy, px, py)
    P = lambda xf, yf: (ox + (px - ox) * xf, oy + (py - oy) * max(0, min(1, yf)))
    s += poly([P(0, 0), P(1, 1)], GREY, 1.6, dash="6,4")
    # реальна: плоско знизу, лінійно в середині, плоско згори
    real = []
    for i in range(101):
        xf = i / 100
        if xf < 0.12:
            yf = 0.5 * xf
        elif xf > 0.9:
            yf = 0.9 + 0.4 * (xf - 0.9)
        else:
            yf = (0.06) + (xf - 0.12) * (0.9 - 0.06) / (0.9 - 0.12)
        real.append(P(xf, yf))
    s += poly(real, RED, 2.8)
    # зони
    gx0 = P(0.12, 0)[0]
    gx1 = P(0.9, 0)[0]
    s += rect(gx0, py, gx1 - gx0, oy - py, LGRN, "none", 0)
    s += rect(ox, py, gx0 - ox, oy - py, LRED, "none", 0)
    s += rect(gx1, py, px - gx1, oy - py, LRED, "none", 0)
    s += text((gx0 + gx1) / 2, py + 18, "надійна середина", 10, GREEN, "middle", "bold")
    s += text((ox + gx0) / 2, oy - 14, "глухо", 8.6, RED, "middle", "bold")
    s += text((gx1 + px) / 2, py + 30, "насич.", 8.6, RED, "middle", "bold")
    s += rect(160, 356, 600, 28, LAMB, GOLD, 1.3, 7)
    s += text(460, 374, "Тримай сигнал у середині шкали; крайні ~0.1 В і верхівку не довіряй. + розкид між чипами.", 9.2, INK, "middle", "bold")
    save("fig-26-6-5-esp32-curve.svg", s)


# ── Рис. 26.6.6 — калібрування: одно-, дво-, багатоточкове ────────────────────
def fig66_calibration():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 30, "Калібрування: підігнати виміряну криву під істину", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "що більше відомих точок, то складніші похибки можна виправити", 10.3, GREY, "middle", style="italic")
    panels = [
        (60, "1 точка", "лише зсув", [0.5], RED),
        (350, "2 точки", "зсув + масштаб", [0.25, 0.85], GOLD),
        (640, "багато точок", "+ нелінійність", [0.15, 0.38, 0.6, 0.82], GREEN),
    ]
    for x0, title, what, pts, col in panels:
        ox, oy, px, py = x0 + 40, 310, x0 + 250, 120
        s = _axes(s, ox, oy, px, py, xlab="Vin", ylab="")
        P = lambda xf, yf: (ox + (px - ox) * xf, oy + (py - oy) * max(0, min(1, yf)))
        s += poly([P(0, 0), P(1, 1)], GREY, 1.5, dash="5,4")
        for p in pts:
            xx, yy = P(p, p)
            s += circle(xx, yy, 4.5, col, col, 0)
        s += text(x0 + 145, 104, title, 11, col, "middle", "bold")
        s += text(x0 + 145, 330, what, 9.2, INK, "middle")
    s += rect(150, 348, 660, 26, LBLUE, BLUE, 1.2, 6)
    s += text(480, 366, "Виміряли відомі напруги → знаєте поправку → виправляєте всі майбутні читання.", 9.5, INK, "middle", "bold")
    save("fig-26-6-6-calibration.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §26.7 Як правильно зчитати сигнал — fig-26-7-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 26.7.1 — усереднення гасить випадковий шум ──────────────────────────
def fig71_averaging():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 30, "Усереднення: приборкати випадковий шум", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "багато читань коливаються довкола істини; їхнє середнє лягає набагато ближче до неї", 10.3, GREY, "middle", style="italic")
    ox, mid, A = 80, 200, 70
    s += line(ox, mid, 905, mid, GREEN, 2)
    s += text(ox - 6, mid + 4, "істина", 9.5, GREEN, "end", "bold")
    # шумні читання
    noise = [0.6, -0.9, 0.3, 1.1, -0.5, 0.8, -1.2, 0.4, -0.3, 1.0, -0.7, 0.5, -0.4, 0.9, -1.0, 0.2]
    acc = 0
    avg_pts = []
    for j, n in enumerate(noise):
        x = ox + 820 * j / (len(noise) - 1)
        y = mid - A * n
        s += circle(x, y, 3.4, BLUE, BLUE, 0)
        acc += n
        avg_pts.append((x, mid - A * (acc / (j + 1))))
    s += poly(avg_pts, RED, 2.6)
    s += text(ox + 6, 96, "сині точки — окремі (шумні) читання", 9.5, BLUE, "start", "bold")
    s += text(560, 300, "червона — біжуче середнє: швидко сходиться до істини", 9.5, RED, "start", "bold")
    s += rect(150, 332, 660, 40, LAMB, GOLD, 1.3, 9)
    s += text(480, 350, "Випадковий шум спадає приблизно як √N: 16 читань → шум ÷4 (≈ +2 «чесні» біти).", 9.7, INK, "middle", "bold")
    s += text(480, 366, "Калібрування лікувало системне; усереднення — випадкове. Це різні ліки.", 9, GREY, "middle")
    save("fig-26-7-1-averaging.svg", s)


# ── Рис. 26.7.2 — імпеданс джерела й заряд конденсатора S/H ───────────────────
def fig72_source_impedance():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 30, "Імпеданс джерела: АЦП мусить устигнути зарядити конденсатор", 17, INK, "middle", "bold")
    s += text(W / 2, 52, "семпл-холд бере заряд крізь опір джерела; завеликий опір — і за вікно виміру не встигає", 10, GREY, "middle", style="italic")
    # схема зліва
    s += text(110, 110, "джерело", 10, INK, "middle", "bold")
    s += circle(110, 150, 16, "#ffffff", GREEN, 2)
    s += text(110, 155, "V", 11, GREEN, "middle", "bold")
    s += line(126, 150, 175, 150, INK, 2)
    s += rect(175, 138, 56, 24, "#ffffff", RED, 1.8, 3)
    s += text(203, 155, "Rджер", 8.5, RED, "middle", "bold")
    s += line(231, 150, 300, 150, INK, 2)
    s += circle(303, 150, 3, INK, INK, 0)
    s += line(303, 150, 303, 130, INK, 2)
    s += text(330, 128, "ключ S/H", 8.5, GREY, "start")
    s += line(303, 150, 303, 185, INK, 2)
    s += line(286, 185, 320, 185, INK, 3)
    s += line(290, 192, 316, 192, INK, 3)
    s += text(336, 188, "Cтрим", 8.5, GREEN, "start", "bold")
    s += line(303, 192, 303, 206, INK, 2)
    s += line(290, 206, 316, 206, INK, 2)
    s += line(294, 211, 312, 211, INK, 2)
    s += line(298, 216, 308, 216, INK, 2)
    # криві заряду праворуч
    ox, oy = 470, 320
    topx, topy = 900, 110
    s += arrow(ox, oy, ox, topy - 8, INK, 1.8)
    s += arrow(ox, oy, topx + 10, oy, INK, 1.8)
    s += text(ox - 8, topy, "U на C", 9, INK, "end", "bold")
    s += text(topx, oy + 22, "час", 9.5, INK, "middle")
    s += line(ox, topy + 6, topx, topy + 6, GREEN, 1.6, dash="5,3")
    s += text(topx, topy, "Vістина", 9, GREEN, "end", "bold")
    # вікно виміру
    winx = ox + (topx - ox) * 0.45
    s += line(winx, topy, winx, oy, GREY, 1.4, dash="3,3")
    s += text(winx, oy + 22, "кінець вікна", 8.4, GREY, "middle")
    full = oy - (topy + 6)
    low = [(ox + (topx - ox) * i / 100, oy - full * (1 - math.exp(-5 * i / 100))) for i in range(101)]
    s += poly(low, BLUE, 2.4)
    s += text(ox + 150, topy + 26, "малий опір — встиг", 9, BLUE, "start", "bold")
    high = [(ox + (topx - ox) * i / 100, oy - full * (1 - math.exp(-1.2 * i / 100))) for i in range(101)]
    s += poly(high, RED, 2.4)
    hx = ox + (topx - ox) * 0.45
    hy = oy - full * (1 - math.exp(-1.2 * 45 / 100))
    s += circle(hx, hy, 4, RED, RED, 0)
    s += text(ox + 120, oy - 30, "великий опір — НЕ встиг → занижено", 9, RED, "start", "bold")
    s += rect(150, 356, 660, 30, LBLUE, BLUE, 1.3, 7)
    s += text(480, 375, "На ESP32 опір джерела тримають малим (< ~10 кОм). Більший — потрібен буфер.", 9.6, INK, "middle", "bold")
    save("fig-26-7-2-source-impedance.svg", s)


# ── Рис. 26.7.3 — буфер (повторювач) для «кволого» джерела ────────────────────
def fig73_buffer():
    W, H = 940, 360
    s = header(W, H)
    s += text(W / 2, 30, "Буфер: посередник між «кволим» джерелом і АЦП", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "операційний підсилювач-повторювач: джерелу показує високий опір, а АЦП — низький", 10, GREY, "middle", style="italic")
    # джерело
    s += text(95, 130, "високоомне", 9.5, RED, "middle", "bold")
    s += text(95, 145, "джерело", 9.5, RED, "middle")
    s += circle(95, 185, 18, "#ffffff", RED, 2)
    s += text(95, 190, "V", 11, RED, "middle", "bold")
    s += line(113, 185, 210, 185, INK, 2)
    s += text(165, 175, "майже без струму", 8, GREY, "middle")
    # ОП трикутник
    s += poly([(210, 150), (210, 220), (290, 185), (210, 150)], INK, 2, fill=LGRN)
    s += text(238, 190, "+", 14, GREEN, "middle", "bold")
    s += text(252, 178, "ОП", 9, INK, "middle", "bold")
    # зворотний зв'язок
    s += line(290, 185, 330, 185, INK, 2)
    s += line(330, 185, 330, 240, INK, 2)
    s += line(330, 240, 225, 240, INK, 2)
    s += line(225, 240, 225, 205, INK, 2)
    s += text(300, 258, "повний зворотний зв'язок (підсилення = 1)", 8.5, GREY, "middle")
    # до АЦП
    s += line(330, 185, 420, 185, INK, 2)
    s += text(375, 175, "міцний вихід", 8, GREEN, "middle")
    s += rect(420, 160, 110, 50, LBLUE, BLUE, 1.8, 10)
    s += text(475, 190, "АЦП", 12, BLUE, "middle", "bold")
    s += rect(580, 120, 320, 150, "#fbfcff", GREY, 1.4, 12)
    s += text(740, 148, "Повторювач:", 11, INK, "middle", "bold")
    s += text(600, 176, "• вхід — майже нескінченний опір", 9.6, INK, "start")
    s += text(615, 196, "(джерело не вантажиться)", 8.8, GREY, "start")
    s += text(600, 222, "• вихід — малий опір", 9.6, INK, "start")
    s += text(615, 242, "(швидко заряджає Cтрим АЦП)", 8.8, GREY, "start")
    save("fig-26-7-3-buffer.svg", s)


# ── Рис. 26.7.4 — усталення: відкинь перше читання після перемикання ─────────
def fig74_settling():
    W, H = 960, 360
    s = header(W, H)
    s += text(W / 2, 30, "Дай йому час: усталення й «перше читання — геть»", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "після перемикання каналу конденсатор ще тримає стару напругу — першому виміру не вір", 10, GREY, "middle", style="italic")
    ox, oy = 80, 250
    s += line(ox, oy, 905, oy, FAINT, 1.2)
    # стара напруга, потім перемикання, перехід, усталення
    swx = ox + 200
    s += line(ox, oy - 30, swx, oy - 30, GREY, 2.2)
    s += text(ox + 90, oy - 38, "старий канал", 8.6, GREY, "middle")
    s += line(swx, oy - 200, swx, oy, RED, 1.6, dash="5,3")
    s += text(swx, oy - 208, "перемкнули канал", 9, RED, "middle", "bold")
    trans = [(swx + (320) * i / 100, (oy - 30) - 110 * (1 - math.exp(-4 * i / 100))) for i in range(101)]
    s += poly(trans, BLUE, 2.4)
    setx = swx + 320
    s += line(setx, oy - 140, 880, oy - 140, GREEN, 2.4)
    s += text(740, oy - 148, "усталилося — добрі читання", 9, GREEN, "middle", "bold")
    # маркери читань
    s += circle(swx + 30, (oy - 30) - 110 * (1 - math.exp(-4 * 9 / 100)), 4, RED, RED, 0)
    s += text(swx + 70, oy - 80, "1-ше читання — хибне (відкинь!)", 8.8, RED, "start", "bold")
    s += circle(setx + 120, oy - 140, 4, GREEN, GREEN, 0)
    s += rect(160, 300, 640, 40, LGRN, GREEN, 1.3, 9)
    s += text(480, 318, "Після зміни каналу (чи на старті) дай АЦП усталитися — або просто відкинь перший відлік.", 9.5, INK, "middle", "bold")
    s += text(480, 334, "Це той самий час захоплення семпл-холду (§26.2), лише з боку практики.", 9, GREY, "middle")
    save("fig-26-7-4-settling.svg", s)


# ── Рис. 26.7.5 — медіана проти середнього (викиди) ──────────────────────────
def fig75_median():
    W, H = 920, 360
    s = header(W, H)
    s += text(W / 2, 30, "Викиди: медіана стійкіша за середнє", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "одна імпульсна завада тягне середнє, а медіану — ні", 10.3, GREY, "middle", style="italic")
    ox, mid = 90, 190
    s += line(ox, mid, 850, mid, FAINT, 1.2)
    vals = [0.1, -0.1, 0.05, 0.0, 0.08, -0.05, 2.6, 0.02, -0.08, 0.06]  # один викид 2.6
    A = 50
    for j, v in enumerate(vals):
        x = ox + 760 * j / (len(vals) - 1)
        y = mid - A * v
        col = RED if v > 1 else BLUE
        s += circle(x, y, 4, col, col, 0)
        if v > 1:
            s += text(x, y - 12, "викид (завада)", 9, RED, "middle", "bold")
    mean = sum(vals) / len(vals)
    sv = sorted(vals)
    median = (sv[len(sv) // 2 - 1] + sv[len(sv) // 2]) / 2
    s += line(ox, mid - A * mean, 850, mid - A * mean, GOLD, 2.2, dash="6,3")
    s += text(858, mid - A * mean + 4, "середнє (зсунене!)", 9.3, GOLD, "start", "bold")
    s += line(ox, mid - A * median, 850, mid - A * median, GREEN, 2.2)
    s += text(858, mid - A * median + 4, "медіана", 9.3, GREEN, "start", "bold")
    s += rect(150, 312, 620, 38, LBLUE, BLUE, 1.3, 8)
    s += text(460, 330, "Для імпульсних завад (іскри, перемикання) бери медіану чи відкидай крайні значення;", 9.3, INK, "middle", "bold")
    s += text(460, 346, "для рівномірного шуму — звичайне середнє.", 9, GREY, "middle")
    save("fig-26-7-5-median.svg", s)


# ── Рис. 26.7.6 — повний рецепт чистого виміру ───────────────────────────────
def fig76_recipe():
    W, H = 980, 320
    s = header(W, H)
    s += text(W / 2, 30, "Повний рецепт чистого виміру", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "кожна ланка прибирає свою біду — разом дають чесне число", 10.3, GREY, "middle", style="italic")
    steps = [
        ("Джерело\nмалого опору\n(чи буфер)", GREEN, "не «просідає»"),
        ("RC анти-\nаліас (§26.5)", GOLD, "зрізає ВЧ-шум"),
        ("АЦП за\nтаймером (fs)", BLUE, "рівний крок"),
        ("Усереднення\n/ медіана", PURP, "−випадковий шум"),
        ("Калібрування\n(мВ, §26.6)", RED, "−системна похибка"),
    ]
    n = len(steps)
    bw = 150
    gap = (980 - n * bw) / (n + 1)
    y = 120
    for i, (lab, col, note) in enumerate(steps):
        x = gap + i * (bw + gap)
        s += rect(x, y, bw, 80, "#fbfcff", col, 1.8, 10)
        lines = lab.split("\n")
        for k, ln in enumerate(lines):
            s += text(x + bw / 2, y + 26 + k * 17, ln, 10, col, "middle", "bold")
        s += text(x + bw / 2, y + 100, note, 8.6, GREY, "middle")
        if i < n - 1:
            s += arrow(x + bw + 3, y + 40, x + bw + gap - 3, y + 40, INK, 2)
    s += rect(150, 250, 680, 40, LGRN, GREEN, 1.3, 9)
    s += text(490, 268, "Чисте джерело → фільтр → рівні відліки → усереднення → калібрування = надійне число.", 9.6, INK, "middle", "bold")
    s += text(490, 284, "Пропустиш ланку — повернеться саме її біда.", 9, GREY, "middle")
    save("fig-26-7-6-recipe.svg", s)


# ═════════════════════════════════════════════════════════════════════════════
# §26.8 Типи АЦП: SAR, дельта-сигма — fig-26-8-k
# ═════════════════════════════════════════════════════════════════════════════

# ── Рис. 26.8.1 — трикутник компромісів ──────────────────────────────────────
def fig81_tradeoff():
    W, H = 940, 420
    s = header(W, H)
    s += text(W / 2, 30, "Немає «найкращого» АЦП: компроміс швидкість ↔ роздільність", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "кожна архітектура — свій кут; обирають під задачу, а не «найкращий взагалі»", 10.3, GREY, "middle", style="italic")
    ox, oy = 130, 350
    px, py = 820, 100
    s += arrow(ox, oy, ox, py - 10, INK, 2)
    s += arrow(ox, oy, px + 12, oy, INK, 2)
    s += text(ox - 10, py - 2, "роздільність", 10.5, INK, "end", "bold")
    s += text(px, oy + 26, "швидкість", 10.5, INK, "middle", "bold")
    s += text(ox - 10, oy + 14, "низька", 8.5, GREY, "end")
    s += text(px + 6, oy - 8, "", 8, GREY, "start")
    arch = [
        (0.18, 0.86, "Дельта-сигма", PURP, "16–24 біт, повільний"),
        (0.5, 0.55, "SAR", RED, "8–16 біт, швидкий"),
        (0.82, 0.62, "Конвеєрний", GREEN, "10–14 біт, дуже швидкий"),
        (0.9, 0.2, "Flash", BLUE, "6–8 біт, найшвидший"),
    ]
    for xf, yf, lab, col, note in arch:
        x = ox + (px - ox) * xf
        y = oy + (py - oy) * yf
        s += circle(x, y, 11, col, col, 0)
        s += text(x, y - 18, lab, 11, col, "middle", "bold")
        s += text(x, y + 26, note, 8.5, GREY, "middle")
    s += rect(150, 372, 640, 30, LAMB, GOLD, 1.2, 7)
    s += text(470, 391, "Швидкість і роздільність тягнуть у різні боки; додайте ще ціну й складність — і вибір ясний.", 9.3, INK, "middle", "bold")
    save("fig-26-8-1-tradeoff.svg", s)


# ── Рис. 26.8.2 — SAR як зважування (двійковий пошук) ────────────────────────
def fig82_sar_weighing():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 30, "SAR: зважування половинками Vref (двійковий пошук)", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "та сама ідея «гир-часток Vref» (§26.4): більша гиря — лишити чи зняти, далі менша", 10, GREY, "middle", style="italic")
    weights = [("½ Vref", 0.5, True), ("¼ Vref", 0.25, False), ("⅛ Vref", 0.125, True), ("1/16 Vref", 0.0625, True)]
    x = 110
    acc = 0
    for lab, w, keep in weights:
        col = GREEN if keep else GREY
        s += rect(x, 130, 150, 70, LGRN if keep else "#f0f0f0", col, 1.8, 10)
        s += text(x + 75, 158, lab, 12, col, "middle", "bold")
        s += text(x + 75, 182, "лишити ✓" if keep else "зняти ✗", 10, col, "middle", "bold")
        if keep:
            acc += w
        if x < 700:
            s += arrow(x + 150, 165, x + 195, 165, INK, 2)
        x += 195
    s += text(W / 2, 245, "питання за питанням «Vin більше за пробу?» — по одному біту за крок", 10.5, INK, "middle", "bold")
    s += rect(150, 280, 640, 90, LBLUE, BLUE, 1.4, 12)
    s += text(470, 306, "N біт — рівно N кроків порівняння. Усередині — ЦАП (дає пробну напругу)", 10, INK, "middle", "bold")
    s += text(470, 328, "і компаратор (порівнює з Vin). Це «терези» з гирями-частками Vref.", 10, INK, "middle", "bold")
    s += text(470, 352, "Швидко, дешево, по одному виміру — тому SAR і стоїть у мікроконтролерах.", 9.3, GREY, "middle")
    save("fig-26-8-2-sar-weighing.svg", s)


# ── Рис. 26.8.3 — SAR крок за кроком (збіжність) ──────────────────────────────
def fig83_sar_trace():
    W, H = 940, 400
    s = header(W, H)
    s += text(W / 2, 30, "SAR крок за кроком: проба сходиться до Vin", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "кожен крок удвічі звужує невизначеність — як гра «вгадай число»", 10.3, GREY, "middle", style="italic")
    ox, oy = 110, 330
    px, py = 850, 110
    s += arrow(ox, oy, ox, py - 8, INK, 1.8)
    s += arrow(ox, oy, px + 10, oy, INK, 1.8)
    s += text(ox - 8, py, "проба", 9.5, INK, "end", "bold")
    s += text(px, oy + 22, "крок", 9.5, INK, "middle", "bold")
    target = 0.62
    ty = oy + (py - oy) * target
    s += line(ox, ty, px, ty, GREEN, 2, dash="6,3")
    s += text(px, ty - 8, "Vin (ціль)", 9.5, GREEN, "end", "bold")
    N = 8
    trial = 0.0
    w = 0.5
    prev = (ox, oy)
    for i in range(N):
        x = ox + (px - ox) * (i + 1) / N
        test = trial + w
        py_test = oy + (py - oy) * test
        s += circle(x, py_test, 4, RED, RED, 0)
        keep = test <= target
        if keep:
            trial = test
        ky = oy + (py - oy) * trial
        s += line(prev[0], prev[1], x, ky, BLUE, 2)
        prev = (x, ky)
        w /= 2
    s += text(ox + 30, py + 6, "проби (червоні) то вище, то нижче цілі; синя — що лишили", 9, INK, "start")
    s += rect(150, 350, 640, 24, LAMB, GOLD, 1.2, 6)
    s += text(470, 367, "Vin мусить стояти НЕРУХОМО всі N кроків — ось навіщо семпл-холд (§26.2).", 9.5, INK, "middle", "bold")
    save("fig-26-8-3-sar-trace.svg", s)


# ── Рис. 26.8.4 — дельта-сигма: 1 біт швидко → фільтр → багато біт ─────────────
def fig84_deltasigma():
    W, H = 960, 400
    s = header(W, H)
    s += text(W / 2, 30, "Дельта-сигма: передискретизація до краю + цифровий фільтр", 17, INK, "middle", "bold")
    s += text(W / 2, 52, "грубий 1-бітний компаратор міряє ДУЖЕ часто, а фільтр усереднює це в багато біт", 10, GREY, "middle", style="italic")
    # ланцюг
    s += text(95, 120, "Vin", 11, GREEN, "middle", "bold")
    s += arrow(115, 150, 175, 150, INK, 2.2)
    s += rect(175, 122, 150, 56, LGRN, GREEN, 1.8, 10)
    s += text(250, 146, "1-біт модулятор", 9.6, INK, "middle", "bold")
    s += text(250, 164, "(дуже швидко)", 8.6, GREY, "middle")
    s += arrow(325, 150, 400, 150, INK, 2.2)
    # бітовий потік
    bx = 405
    pts = [(bx, 165)]
    bits = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1]
    for i, b in enumerate(bits):
        x0 = bx + i * 9
        y = 135 if b else 165
        pts += [(x0, y), (x0 + 9, y)]
    s += poly(pts, PURP, 1.8)
    s += text(bx + 72, 188, "густий потік 0/1", 8.6, PURP, "middle", "bold")
    s += arrow(bx + 150, 150, bx + 215, 150, INK, 2.2)
    s += rect(bx + 215, 122, 150, 56, LBLUE, BLUE, 1.8, 10)
    s += text(bx + 290, 146, "цифровий фільтр", 9.4, INK, "middle", "bold")
    s += text(bx + 290, 164, "(дециматор)", 8.6, GREY, "middle")
    s += arrow(bx + 365, 150, bx + 420, 150, INK, 2.2)
    s += text(bx + 455, 146, "16–24 біт", 11, BLUE, "middle", "bold")
    s += text(bx + 455, 164, "повільно, точно", 8.4, GREY, "middle")
    s += rect(120, 240, 720, 130, "#fbfcff", GREY, 1.4, 12)
    s += text(480, 266, "Хитрість: «формування шуму» виштовхує похибку квантування у ВИСОКІ частоти,", 9.8, INK, "middle", "bold")
    s += text(480, 286, "а фільтр їх зрізає — лишаючи дуже чистий низькочастотний сигнал.", 9.8, INK, "middle", "bold")
    s += text(480, 312, "+ Передискретизація сама собою захищає від аліасингу (§26.5).", 9.4, GREEN, "middle", "bold")
    s += text(480, 334, "− Повільний: задешево високу роздільність дають лише для неквапних сигналів", 9.4, RED, "middle")
    s += text(480, 352, "(аудіо, ваги, термопари). Це і є «зовнішній точний АЦП» із §26.6–26.7.", 9.2, GREY, "middle")
    save("fig-26-8-4-deltasigma.svg", s)


# ── Рис. 26.8.5 — flash: усі рівні порівнюються одразу ───────────────────────
def fig85_flash():
    W, H = 900, 400
    s = header(W, H)
    s += text(W / 2, 30, "Flash: усі рівні порівнюються ОДРАЗУ — найшвидше", 17.5, INK, "middle", "bold")
    s += text(W / 2, 52, "драбина рівнів + по компаратору на кожен; одним «спалахом» дають код, та коштує дорого", 10, GREY, "middle", style="italic")
    # Vin шина
    s += text(70, 110, "Vin", 11, GREEN, "middle", "bold")
    s += line(90, 130, 90, 350, GREEN, 2.4)
    # драбина рівнів + компаратори
    ladx = 250
    s += text(ladx, 92, "драбина Vref", 9.5, BLUE, "middle", "bold")
    n = 7
    for i in range(n):
        y = 120 + i * 32
        s += rect(ladx - 18, y - 10, 36, 20, "#ffffff", BLUE, 1.4, 2)
        s += text(ladx, y + 4, "R", 8.5, BLUE, "middle", "bold")
        # компаратор
        cyy = y + 16
        s += poly([(ladx + 60, cyy - 14), (ladx + 60, cyy + 14), (ladx + 100, cyy), (ladx + 60, cyy - 14)], INK, 1.6, fill=LGRN)
        s += line(90, cyy, ladx + 60, cyy, GREY, 1) if i == 0 else ""
        s += line(ladx + 18, y, ladx + 60, cyy - 6, GREY, 1)
        s += line(ladx + 100, cyy, ladx + 150, cyy, INK, 1.4)
    s += line(90, 136, ladx + 60, 136, GREY, 1)
    s += text(ladx + 80, 100, str(n) + " компараторів", 8.6, INK, "middle")
    # енкодер
    s += rect(ladx + 150, 150, 90, 150, LBLUE, BLUE, 1.8, 10)
    s += text(ladx + 195, 220, "енкодер", 10, BLUE, "middle", "bold")
    s += arrow(ladx + 240, 225, ladx + 300, 225, INK, 2.2)
    s += text(ladx + 330, 230, "код", 11, INK, "middle", "bold")
    s += rect(120, 360, 660, 30, LRED, RED, 1.3, 7)
    s += text(450, 379, "Для N біт треба 2ᴺ−1 компараторів — звідси мало біт (6–8) і висока ціна й споживання.", 9.2, INK, "middle", "bold")
    save("fig-26-8-5-flash.svg", s)


# ── Рис. 26.8.6 — який АЦП де ────────────────────────────────────────────────
def fig86_table():
    W, H = 960, 380
    s = header(W, H)
    s += text(W / 2, 30, "Який АЦП де: коротка мапа", 18, INK, "middle", "bold")
    s += text(W / 2, 52, "чотири головні архітектури та їхні ніші", 10.3, GREY, "middle", style="italic")
    s += rect(40, 74, 880, 30, "#eef1f7", GREY, 1.2, 5)
    for cx, lab in [(60, "Тип"), (250, "Швидкість"), (420, "Роздільність"), (610, "Де")]:
        s += text(cx, 94, lab, 10.5, INK, "start", "bold")
    rows = [
        ("SAR", "середня–висока", "8–16 біт", "МК загального призначення (★ ESP32)", RED, True),
        ("Дельта-сигма", "низька", "16–24 біт", "аудіо, ваги, термопари (ADS1115 тощо)", PURP, False),
        ("Flash", "найвища", "6–8 біт", "осцилографи, відео", BLUE, False),
        ("Конвеєрний", "висока", "10–14 біт", "відео, швидкий зв'язок", GREEN, False),
    ]
    y = 110
    for typ, spd, res, where, col, hot in rows:
        bg = LRED if hot else ("#ffffff" if (y // 56) % 2 == 0 else "#f7f8fb")
        s += rect(40, y, 880, 50, bg, (RED if hot else FAINT), (1.8 if hot else 1), 5)
        s += text(60, y + 30, typ, 11, col, "start", "bold")
        s += text(250, y + 30, spd, 10, INK, "start")
        s += text(420, y + 30, res, 10, INK, "start", "bold")
        s += text(610, y + 30, where, 9.6, GREY, "start")
        y += 56
    s += text(W / 2, y + 18, "Вбудований АЦП ESP32 — SAR; коли треба більше біт, докуповують зовнішній дельта-сигма.", 9.6, INK, "middle", "bold")
    save("fig-26-8-6-table.svg", s)


if __name__ == "__main__":
    # 📜 Історія до розділу — теорема дискретизації
    figh1_the_question()
    figh2_timeline()
    figh3_telegraph()
    figh4_attribution()
    figh5_legacy()
    # §26.1 АЦП: перетворити напругу в число
    fig11_adc_mirror_dac()
    fig12_bridge()
    fig13_transfer()
    fig14_analogread()
    fig15_applications()
    fig16_levelfinder()
    # §26.2 Дискретизація й квантування
    fig21_two_steps()
    fig22_sampling()
    fig23_quantization()
    fig24_grid()
    fig25_sample_hold()
    fig26_quant_error()
    # §26.3 Біти й роздільність (LSB)
    fig31_bits_levels()
    fig32_lsb()
    fig33_add_bit()
    fig34_res_vs_range()
    fig35_table()
    fig36_useful_bits()
    # §26.4 Опорна напруга (reference)
    fig41_ratio()
    fig42_same_vin()
    fig43_drift()
    fig44_sources()
    fig45_ratiometric()
    fig46_esp32_atten()
    # §26.5 Частота дискретизації, Найквіст, аліасинг
    fig51_nyquist()
    fig52_aliasing()
    fig53_folding()
    fig54_trap()
    fig55_antialias()
    fig56_oversampling()
    # §26.6 Похибки реального АЦП і калібрування
    fig61_ideal_vs_real()
    fig62_offset_gain()
    fig63_dnl()
    fig64_inl()
    fig65_esp32_curve()
    fig66_calibration()
    # §26.7 Як правильно зчитати сигнал
    fig71_averaging()
    fig72_source_impedance()
    fig73_buffer()
    fig74_settling()
    fig75_median()
    fig76_recipe()
    # §26.8 Типи АЦП: SAR, дельта-сигма
    fig81_tradeoff()
    fig82_sar_weighing()
    fig83_sar_trace()
    fig84_deltasigma()
    fig85_flash()
    fig86_table()
    print("OK - figures for Section 26 (26.0.x..26.8.x) generated in", OUT)
