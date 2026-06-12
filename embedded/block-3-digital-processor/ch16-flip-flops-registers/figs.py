# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для Розділу 16 — «Тригери, регістри й тактування» (Модуль 3).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; «1» червоний, «0» синій; «дійсне/висновок» зелене;
стрілки через marker; шрифт sans-serif. Підписи — посекційно (Рис. C.S.N);
історія до розділу — секція 0 (Рис. 16.0.N). Скрипт нарощується по темах.
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


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# ── гліфи вентилів (нарощуємо в темах) ──────────────────────────────────────
def gate_not(x, y, w=40, h=42, fill="#fafafa", stroke=INK, sw=2, bubble=True):
    out = f'<path d="M {x},{y-h/2} L {x},{y+h/2} L {x+w},{y} Z" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n'
    if bubble:
        out += circle(x + w + 6, y, 6, "#fff", stroke, sw)
    return out


def gate_nor(x, y, w=54, h=46, fill="#fafafa", stroke=INK, sw=2):
    r = h / 2
    out = (f'<path d="M {x},{y-r} Q {x+w*0.55},{y-r} {x+w},{y} Q {x+w*0.55},{y+r} {x},{y+r} '
           f'Q {x+w*0.28},{y} {x},{y-r} Z" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')
    return out + circle(x + w + 6, y, 6, "#fff", stroke, sw)


def gate_and(x, y, w=48, h=46, fill="#fafafa", stroke=INK, sw=2):
    r = h / 2
    bx = x + w - r
    return (f'<path d="M {x},{y-r} L {bx},{y-r} A {r},{r} 0 0 1 {bx},{y+r} '
            f'L {x},{y+r} Z" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def gate_nand(x, y, w=48, h=46, fill="#fafafa", stroke=INK, sw=2):
    return gate_and(x, y, w, h, fill, stroke, sw) + circle(x + w + 6, y, 6, "#fff", stroke, sw)


def ttable(x, y, headers, rows, cw=40, ch=24, out_cols=(-1,)):
    out = ""
    n = len(headers)
    oc = set((i if i >= 0 else n + i) for i in out_cols)
    for c, hh in enumerate(headers):
        out += rect(x + c * cw, y, cw, ch, "#eceef0", GREY, 1.2)
        out += text(x + c * cw + cw / 2, y + ch * 0.68, hh, 12, INK, "middle", "bold")
    for r, row in enumerate(rows):
        yy = y + ch * (r + 1)
        for c, v in enumerate(row):
            is_out = c in oc
            if isinstance(v, str):
                out += rect(x + c * cw, yy, cw, ch, "#fafafa", GREY, 1.1)
                out += text(x + c * cw + cw / 2, yy + ch * 0.68, v, 10.5, INK, "middle", "bold")
                continue
            col = RED if v == 1 else BLUE
            bg = ("#eafaef" if v == 1 else "#f3f5fd") if is_out else ("#fdf4f4" if v == 1 else "#f3f5fd")
            tc = (GREEN if v == 1 else BLUE) if is_out else col
            out += rect(x + c * cw, yy, cw, ch, bg, GREY, 1.1)
            out += text(x + c * cw + cw / 2, yy + ch * 0.68, str(v), 12, tc, "middle", "bold")
    return out


def _pin(x1, y1, x2, y2):
    return line(x1, y1, x2, y2, INK, 1.8)


def _box(x, y, w, h, label, sub=None, fill="#eef4ff"):
    out = rect(x, y, w, h, fill, INK, 2, 8)
    out += text(x + w / 2, y + h / 2 + 4, label, 13, INK, "middle", "bold")
    if sub:
        out += text(x + w / 2, y + h / 2 + 20, sub, 10, GREY, "middle")
    return out


def triode(cx, cy, r=26):
    out = circle(cx, cy, r, "#fafafa", INK, 2)
    out += line(cx - 11, cy - 10, cx + 11, cy - 10, INK, 2.4)      # анод (пластина)
    out += line(cx, cy - 10, cx, cy - r - 12, INK, 1.6)            # вивід анода
    out += line(cx - 13, cy + 1, cx + 13, cy + 1, INK, 1.4, "3 3")  # сітка
    out += line(cx - 13, cy + 1, cx - r - 12, cy + 1, INK, 1.6)    # вивід сітки
    out += line(cx - 8, cy + 9, cx, cy + 15, INK, 2.2)             # катод (V)
    out += line(cx, cy + 15, cx + 8, cy + 9, INK, 2.2)
    out += line(cx, cy + 15, cx, cy + r + 12, INK, 1.6)           # вивід катода
    return out


def _inv_pair(ox, oy, q, qbar):
    """Два перехресно-зв'язані інвертори (ядро пам'яті) зі станом q / qbar."""
    out = ""
    g1y, g2y = oy - 26, oy + 26
    # G1 (верхній)
    out += gate_not(ox, g1y, 40, 30)
    # G2 (нижній)
    out += gate_not(ox, g2y, 40, 30)
    # вузли Q (праворуч від G1) і Q̄ (праворуч від G2)
    out += line(ox + 46, g1y, ox + 80, g1y, INK, 1.8)
    out += line(ox + 46, g2y, ox + 80, g2y, INK, 1.8)
    qc = RED if q else BLUE
    qbc = RED if qbar else BLUE
    out += circle(ox + 80, g1y, 3, INK, INK, 1)
    out += circle(ox + 80, g2y, 3, INK, INK, 1)
    out += text(ox + 86, g1y + 4, f"Q={q}", 12, qc, "start", "bold")
    out += text(ox + 86, g2y + 4, f"Q̄={qbar}", 12, qbc, "start", "bold")
    # перехресні зв'язки: Q → вхід G2, Q̄ → вхід G1
    out += line(ox + 80, g1y, ox + 80, oy - 60, INK, 1.4)
    out += line(ox + 80, oy - 60, ox - 22, oy - 60, INK, 1.4)
    out += line(ox - 22, oy - 60, ox - 22, g2y, INK, 1.4)
    out += line(ox - 22, g2y, ox, g2y, INK, 1.4)
    out += line(ox + 80, g2y, ox + 80, oy + 60, INK, 1.4)
    out += line(ox + 80, oy + 60, ox - 36, oy + 60, INK, 1.4)
    out += line(ox - 36, oy + 60, ox - 36, g1y, INK, 1.4)
    out += line(ox - 36, g1y, ox, g1y, INK, 1.4)
    return out


# ── Рис. 16.0.1 — таймлайн: як схема навчилася пам'ятати ───────────────────
def fig_timeline():
    W, H = 880, 760
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг питань: як змусити схему ПАМ'ЯТАТИ", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "більшість фізики «забуває», скочуючись у рівновагу; пам'ять — це навмисна, стійка непокора цьому",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 100, H - 30
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("прадавнє", "питання", "Як зробити, щоб схема ТРИМАЛА обраний стан, а не «розслаблялась»?", False),
        ("1900-ті", "реле-засувка / relay latch", "Телефонні станції: реле тримає себе власним контактом — механічна пам'ять", False),
        ("1918", "Екклз і Джордан / Eccles & Jordan", "Дві перехресно-зв'язані лампи → ДВА стійкі стани: перша електронна комірка пам'яті", False),
        ("1930-ті", "назва «flip-flop»", "За клацанням, з яким схема перекидається між станами", False),
        ("1940-ві", "ENIAC", "Тисячі лампових тригерів = регістри й лічильники першого комп'ютера", False),
        ("1947 →", "транзистор → кремній", "Та сама перехресна петля, але крихітна: SRAM, регістри (→ цей розділ)", False),
        ("тепер", "кожен біт пам'яті", "Регістр, кеш, комірка SRAM — прямий нащадок схеми 1918 року", False),
    ]
    n = len(nodes)
    for i, (yr, who, q, faint) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        col = INK
        if i == 2:
            s += circle(spine, y, 11, "#fff", RED, 0)
            s += circle(spine, y, 10, "none", RED, 3.2)
            s += circle(spine, y, 4.5, RED, RED, 1)
        else:
            s += circle(spine, y, 7, "#fff", col, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 15, (RED if i == 2 else col), "start", "bold")
        s += text(spine + 26, y + 17, q, 12, col, "start", style="italic")
    save("fig-16-0-1-timeline.svg", s)


# ── Рис. 16.0.2 — перехресний зв'язок = пам'ять ────────────────────────────
def fig_crosscoupled():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Серце ідеї: перехресний зв'язок робить два стійкі стани", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "вихід кожного елемента живить вхід іншого — петля сама себе підтримує (як у §14.6)",
              12, GREY, "middle", style="italic")
    s += _inv_pair(330, 200, 1, 0)
    s += text(330, 300, "два інвертори, з'єднані «навхрест»", 12, INK, "middle", "bold")
    # таблиця станів
    s += rect(560, 110, 270, 180, "#f4f7f4", GREEN, 1.6, 10)
    s += text(695, 136, "Два стійкі стани:", 13, INK, "middle", "bold")
    s += text(610, 168, "стан «1»:", 12.5, INK, "start", "bold")
    s += text(700, 168, "Q=1, Q̄=0", 12.5, RED, "start", "bold")
    s += text(610, 196, "стан «0»:", 12.5, INK, "start", "bold")
    s += text(700, 196, "Q=0, Q̄=1", 12.5, BLUE, "start", "bold")
    s += text(610, 230, "кожен сам себе тримає:", 11.5, GREY, "start", style="italic")
    s += text(610, 248, "Q=1 змушує Q̄=0,", 11.5, GREY, "start")
    s += text(610, 264, "а Q̄=0 змушує Q=1 →", 11.5, GREY, "start")
    s += text(610, 280, "замкнене коло, що «застрягло».", 11.5, GREY, "start", "bold")
    s += text(W / 2, 360, "Це й є 1 біт пам'яті: схема НЕ скочується в одну рівновагу — вона має дві й тримає обрану.",
              12, INK, "middle", "bold")
    s += text(W / 2, 382, "Перекинути її з одного стану в інший — окремий «поштовх» (set/reset, далі §16.2).",
              11.5, GREY, "middle", style="italic")
    save("fig-16-0-2-crosscoupled.svg", s)


# ── Рис. 16.0.3 — бістабільність: кулька у двох ямах ───────────────────────
def fig_bistable():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "Інтуїція: кулька у двох ямах (бістабільність)", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "стійких станів два, між ними — горбок; кулька лишається у своїй ямі, доки її не «штовхнути» через горб",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 120, 740
    mid, half = (gx0 + gx1) / 2, (gx1 - gx0) / 2
    base = 290

    def yof(x):  # подвійна яма V(t) = (t²−1)²: дві ями (t=±1), горб (t=0), стіни по краях
        t = (x - mid) / half * 1.6
        return base - 56 * (t * t - 1) ** 2

    pts = [(x, yof(x)) for x in range(gx0, gx1 + 1, 5)]
    s += polyline(pts, INK, 2.6)
    lx = mid - half / 1.6   # ліва яма (t=-1)
    rx = mid + half / 1.6   # права яма (t=+1)
    s += circle(lx, base - 12, 12, "#f3f5fd", BLUE, 2.4)
    s += text(lx, base - 8, "0", 13, BLUE, "middle", "bold")
    s += text(lx, base + 28, "стан «0»", 12, BLUE, "middle", "bold")
    s += circle(rx, base - 12, 12, "#fdf4f4", RED, 1.4)
    s += text(rx, base - 8, "1", 13, RED, "middle", "bold")
    s += text(rx, base + 28, "стан «1»", 12, RED, "middle", "bold")
    # горбок
    s += text(mid, yof(mid) - 12, "бар'єр", 11.5, GREY, "middle", style="italic")
    s += arrow(lx + 26, 150, rx - 26, 150, GREEN, 2)
    s += text(mid, 142, "«поштовх» (тригер) перекидає через горб", 11.5, GREEN, "middle", "bold")
    s += rect(70, 340, W - 140, 46, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 362, "Комбінаційна схема має ОДНУ рівновагу (скотилася — і все). Тригер навмисно має ДВІ —", 12, INK, "middle", "bold")
    s += text(W / 2, 380, "тому й уміє пам'ятати, у якій із них його лишили.", 12, GREY, "middle", style="italic")
    save("fig-16-0-3-bistable.svg", s)


# ── Рис. 16.0.4 — Екклз–Джордан (лампи) → сучасні вентилі ──────────────────
def fig_tubes_to_gates():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Та сама ідея крізь технології: лампи 1918 → кремній сьогодні", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "перехресний зв'язок незмінний; змінюється лише, ЧИМ його роблять — лампою, транзистором, вентилем",
              12, GREY, "middle", style="italic")
    # ліворуч — дві лампи навхрест
    s += rect(50, 90, 380, 250, "none", FAINT, 1.5, 10)
    s += text(240, 114, "Екклз–Джордан, 1918", 13.5, INK, "middle", "bold")
    s += line(150, 140, 330, 140, RED, 2)
    s += text(140, 144, "+V", 10.5, RED, "end", "bold")
    s += triode(160, 220)
    s += triode(320, 220)
    s += line(160, 182, 160, 140, INK, 1.6)
    s += line(320, 182, 320, 140, INK, 1.6)
    # перехресні зв'язки (анод однієї → сітка іншої)
    s += line(187, 221, 293, 250, INK, 1.4, "4 3")   # анод A → сітка B
    s += line(293, 221, 187, 250, INK, 1.4, "4 3")   # анод B → сітка A
    s += text(160, 280, "лампа A", 10.5, INK, "middle")
    s += text(320, 280, "лампа B", 10.5, INK, "middle")
    s += text(240, 320, "дві тріоди навхрест → два стани", 11, GREY, "middle", style="italic")
    # праворуч — два вентилі навхрест
    s += rect(450, 90, 380, 250, "none", FAINT, 1.5, 10)
    s += text(640, 114, "Сьогодні: пара вентилів / транзисторів", 12.5, INK, "middle", "bold")
    s += _inv_pair(620, 215, 1, 0)
    s += text(640, 320, "та сама перехресна петля — у кремнії", 11, GREY, "middle", style="italic")
    # стрілка наступності
    s += text(W / 2, 372, "Лампа згоріла в історії, ідея — ні: кожна комірка SRAM у вашому чипі — це Екклз–Джордан у мініатюрі.",
              12, INK, "middle", "bold")
    save("fig-16-0-4-tubes-to-gates.svg", s)


# ═══════════════════════ §16.1 — Пам'ять стану ══════════════════════════════
# ── Рис. 16.1.1 — комбінаційна логіка не вміє пам'ятати ─────────────────────
def fig161_no_memory():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Комбінаційна логіка не вміє пам'ятати", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "її вихід — це функція лише входів ЗАРАЗ; минулого вона не зберігає (з §15.7)",
              12, GREY, "middle", style="italic")
    s += rect(120, 110, 250, 130, "#eef4ff", INK, 2, 12)
    s += text(245, 168, "комбінаційна", 14, INK, "middle", "bold")
    s += text(245, 190, "логіка", 14, INK, "middle", "bold")
    for i, lab in enumerate(["вхід"]):
        s += _pin(70, 175, 120, 175)
        s += text(64, 179, "вхід", 11.5, INK, "end", "bold")
    s += _pin(370, 175, 420, 175)
    s += text(426, 179, "вихід = f(вхід зараз)", 12, GREEN, "start", "bold")
    s += text(245, 262, "немає шляху від «що було раніше»", 11.5, GREY, "middle", style="italic")
    s += rect(540, 110, 290, 130, "#fdf6f6", RED, 1.6, 10)
    s += text(685, 136, "Чого вона НЕ може:", 12.5, RED, "middle", "bold")
    for i, t in enumerate(["• «чи натискали кнопку?»", "• «це вже третій імпульс»",
                           "• утримати рівень після", "  зникнення сигналу"]):
        s += text(556, 164 + i * 22, t, 11.5, INK, "start")
    s += text(W / 2, 330, "Щоб пам'ятати, схемі потрібен СТАН — і спосіб його зберігати між подіями.", 12, INK, "middle", "bold")
    save("fig-16-1-1-no-memory.svg", s)


# ── Рис. 16.1.2 — зворотний зв'язок = стан (модель послідовнісної схеми) ────
def fig161_seq_model():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "Загальна модель: комбінаційна логіка + зворотний зв'язок = СТАН", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "частину виходу заводять назад як «стан» — і тепер вихід залежить і від входів, і від минулого",
              12, GREY, "middle", style="italic")
    # комбінаційна логіка
    s += rect(300, 110, 260, 120, "#eef4ff", INK, 2, 12)
    s += text(430, 158, "комбінаційна логіка", 13, INK, "middle", "bold")
    s += text(430, 178, "(вентилі без петель)", 10.5, GREY, "middle")
    # входи
    s += _pin(150, 140, 300, 140)
    s += text(144, 144, "входи", 12, INK, "end", "bold")
    # виходи
    s += _pin(560, 140, 700, 140)
    s += text(706, 144, "виходи", 12, GREEN, "start", "bold")
    # петля стану
    s += _pin(560, 200, 640, 200)
    s += text(600, 192, "наступний стан", 10, GREY, "middle")
    s += line(640, 200, 640, 300, INK, 1.8)
    s += rect(360, 280, 140, 44, "#eef7ee", GREEN, 2, 8)
    s += text(430, 307, "пам'ять стану", 12, GREEN, "middle", "bold")
    s += line(640, 300, 500, 300, INK, 1.8)
    s += line(360, 300, 200, 300, INK, 1.8)
    s += line(200, 300, 200, 200, INK, 1.8)
    s += line(200, 200, 300, 200, INK, 1.8)
    s += arrow(260, 200, 300, 200, INK, 1.8)
    s += text(230, 192, "поточний стан", 10, GREY, "middle")
    s += rect(70, 350, W - 140, 40, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 375, "вихід = f(входи, стан) · наступний стан = g(входи, стан) — це кістяк УСІХ схем з пам'яттю",
              12, INK, "middle", "bold")
    save("fig-16-1-2-seq-model.svg", s)


# ── Рис. 16.1.3 — непарна vs парна інверсія в петлі ────────────────────────
def fig161_odd_even():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Ключ: петля з ПАРНОЇ кількості інверсій тримає стан, з непарної — коливається", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "один інвертор у кільці суперечить сам собі (стійкого стану нема); два — узгоджуються у два стійкі стани",
              12, GREY, "middle", style="italic")
    # ЛІВО: один інвертор → осциляція
    s += rect(50, 84, 380, 290, "none", FAINT, 1.5, 10)
    s += text(240, 108, "1 інвертор (непарна) → КОЛИВАННЯ", 12.5, RED, "middle", "bold")
    s += gate_not(190, 170, 44, 34)
    s += line(150, 170, 190, 170, INK, 1.8)
    s += line(246, 170, 280, 170, INK, 1.8)
    # петля назад
    s += line(280, 170, 280, 130, INK, 1.6)
    s += line(280, 130, 130, 130, INK, 1.6)
    s += line(130, 130, 130, 170, INK, 1.6)
    s += arrow(130, 170, 150, 170, INK, 1.6)
    s += text(205, 130, "вихід → вхід", 10, GREY, "middle")
    s += text(240, 215, "«0→1→0→1…» — ніколи не вщухає", 11, INK, "middle", style="italic")
    # коливання
    osc = []
    for i in range(120):
        t = i / 12.0
        v = 1 if int(t) % 2 == 0 else 0
        osc.append((70 + i * 2.9, 320 - v * 36))
    s += polyline(osc, RED, 2)
    s += text(240, 360, "автоколивання (кільцевий генератор)", 11, RED, "middle", "bold")
    # ПРАВО: два інвертори → бістабільність
    s += rect(450, 84, 380, 290, "none", FAINT, 1.5, 10)
    s += text(640, 108, "2 інвертори (парна) → ДВА СТАНИ", 12.5, GREEN, "middle", "bold")
    s += _inv_pair(610, 210, 1, 0)
    s += text(640, 300, "«Q=1 тримає Q̄=0 тримає Q=1» — застрягло", 10.5, INK, "middle", style="italic")
    s += text(640, 352, "стабільно: пам'ятає 1 біт", 11.5, GREEN, "middle", "bold")
    save("fig-16-1-3-odd-even.svg", s)


# ── Рис. 16.1.4 — тримає стан у часі ───────────────────────────────────────
def fig161_holds():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "«Пам'ятає» означає: тримає рівень у часі, доки не перекинуть", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "без зовнішнього сигналу вихід Q лежить незмінно; короткий «поштовх» перекидає його — і він знову лежить",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 110, 800
    hi, lo = 120, 220
    s += text(70, hi + 5, "Q", 13, INK, "end", "bold")
    s += line(gx0, hi, gx1, hi, FAINT, 1)
    s += line(gx0, lo, gx1, lo, FAINT, 1)
    s += text(gx0 - 6, hi + 4, "1", 10, RED, "end")
    s += text(gx0 - 6, lo + 4, "0", 10, BLUE, "end")
    # Q: 0 довго, поштовх→1 довго, поштовх→0
    seg = [(gx0, lo), (300, lo), (300, hi), (560, hi), (560, lo), (gx1, lo)]
    s += polyline(seg, GREEN, 2.6)
    # поштовхи
    for x, lab in ((300, "set →1"), (560, "reset →0")):
        s += arrow(x, 290, x, 250, RED, 2)
        s += text(x, 305, lab, 11, RED, "middle", "bold")
    s += text(205, lo - 10, "тримає 0", 11, GREY, "middle", style="italic")
    s += text(430, hi - 10, "тримає 1 (хоч поштовх давно зник)", 11, GREY, "middle", style="italic")
    s += text(680, lo - 10, "знову тримає 0", 11, GREY, "middle", style="italic")
    s += rect(70, 322, W - 140, 30, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 342, "Між поштовхами Q не змінюється сам — оце «лежить, де поклали» і є збережений біт.", 12, INK, "middle", "bold")
    save("fig-16-1-4-holds.svg", s)


# ── Рис. 16.1.5 — енергозалежність: вимкнули — забула ──────────────────────
def fig161_volatile():
    W, H = 820, 320
    s = header(W, H)
    s += text(W / 2, 34, "Тонкість: така пам'ять тримається ЖИВЛЕННЯМ", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "петля самопідтримки працює, лише поки є струм; зникло живлення — біт забуто (енергозалежність)",
              12, GREY, "middle", style="italic")
    s += rect(110, 100, 250, 120, "#eef7ee", GREEN, 2, 10)
    s += text(235, 150, "живлення Є", 13, GREEN, "middle", "bold")
    s += text(235, 174, "Q = 1 (тримається)", 12, RED, "middle", "bold")
    s += text(235, 200, "петля підкріплює себе", 10.5, GREY, "middle", style="italic")
    s += arrow(370, 160, 450, 160, INK, 2.4)
    s += text(410, 150, "вимк.", 11, RED, "middle", "bold")
    s += rect(460, 100, 250, 120, "#f1f1f1", GREY, 2, 10)
    s += text(585, 150, "живлення НЕМА", 13, GREY, "middle", "bold")
    s += text(585, 174, "Q = ?  (забуто)", 12, GREY, "middle", "bold")
    s += text(585, 200, "петля розірвана", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, 270, "Тому пам'ять на тригерах (регістри, SRAM) — «енергозалежна»: губить дані без живлення.", 12, INK, "middle", "bold")
    s += text(W / 2, 292, "Постійне зберігання (Flash) — інша річ, до якої дійдемо в Розділі 19.", 11.5, GREY, "middle", style="italic")
    save("fig-16-1-5-volatile.svg", s)


# ═══════════════════════ §16.2 — SR-засувка ═════════════════════════════════
# ── Рис. 16.2.1 — SR-засувка з двох NOR ────────────────────────────────────
def fig162_sr_nor():
    W, H = 820, 400
    s = header(W, H)
    s += text(W / 2, 34, "SR-засувка: два NOR навхрест із керувальними входами S і R", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "S (set) ставить Q=1, R (reset) ставить Q=0, а S=R=0 — «тримати» (це і є пам'ять)",
              12, GREY, "middle", style="italic")
    # NOR_top: Q = NOR(R, Q̄);  NOR_bot: Q̄ = NOR(S, Q)
    s += gate_nor(220, 150, 54, 44)
    s += gate_nor(220, 260, 54, 44)
    s += text(247, 132, "NOR", 10, GREY, "middle")
    s += text(247, 296, "NOR", 10, GREY, "middle")
    # входи R, S
    s += _pin(120, 138, 220, 138)
    s += text(112, 142, "R", 13, BLUE, "end", "bold")
    s += _pin(120, 272, 220, 272)
    s += text(112, 276, "S", 13, RED, "end", "bold")
    # виходи
    s += line(286, 150, 380, 150, INK, 1.8)
    s += text(386, 154, "Q", 14, GREEN, "start", "bold")
    s += line(286, 260, 380, 260, INK, 1.8)
    s += text(386, 264, "Q̄", 14, GREEN, "start", "bold")
    # ЗЗ: Q → нижній вхід1 (220,248); Q̄ → верхній вхід2 (220,162)
    s += circle(340, 150, 3, INK, INK, 1)
    s += line(340, 150, 340, 212, INK, 1.5)
    s += line(340, 212, 180, 212, INK, 1.5)
    s += line(180, 212, 180, 248, INK, 1.5)
    s += line(180, 248, 220, 248, INK, 1.5)
    s += circle(320, 260, 3, INK, INK, 1)
    s += line(320, 260, 320, 198, INK, 1.5)
    s += line(320, 198, 160, 198, INK, 1.5)
    s += line(160, 198, 160, 162, INK, 1.5)
    s += line(160, 162, 220, 162, INK, 1.5)
    # таблиця
    s += text(560, 110, "S  R  → Q (наступний)", 13, INK, "middle", "bold")
    rows = [("0", "0", "Q  тримати"), ("1", "0", "1  set"), ("0", "1", "0  reset"), ("1", "1", "— заборона")]
    for i, (sv, rv, q) in enumerate(rows):
        yy = 140 + i * 40
        cs = RED if sv == "1" else BLUE
        cr = RED if rv == "1" else BLUE
        s += text(480, yy, "S=" + sv, 13, cs, "start", "bold")
        s += text(540, yy, "R=" + rv, 13, cr, "start", "bold")
        col = GREY if q.startswith("—") else (GREEN if "тримати" in q else INK)
        s += text(600, yy, "→ " + q, 12.5, col, "start", "bold")
    s += text(560, 312, "S=R=0 → пам'ять: Q лишається таким, як був", 11.5, GREEN, "middle", "bold")
    save("fig-16-2-1-sr-nor.svg", s)


# ── Рис. 16.2.2 — чотири випадки роботи ────────────────────────────────────
def fig162_cases():
    W, H = 880, 410
    s = header(W, H)
    s += text(W / 2, 34, "Чотири випадки SR-засувки: тримати / set / reset / заборона", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "входи S, R керують двома NOR; стежмо, який стан вони дають на виході Q",
              12, GREY, "middle", style="italic")

    def cell(ox, title, sv, rv, qtxt, col):
        nonlocal s
        s += rect(ox, 88, 195, 270, "none", col, 1.8, 10)
        s += text(ox + 97, 112, title, 13.5, col, "middle", "bold")
        s += text(ox + 97, 140, f"S={sv}, R={rv}", 13, INK, "middle", "bold")
        # маленька засувка-блок
        s += rect(ox + 47, 160, 100, 70, "#fafafa", INK, 1.6, 8)
        s += text(ox + 97, 190, "SR", 12, INK, "middle", "bold")
        s += text(ox + 97, 208, "засувка", 10, GREY, "middle")
        s += text(ox + 97, 262, qtxt, 12.5, col, "middle", "bold")
        return

    cell(40, "ТРИМАТИ", 0, 0, "Q = старе", GREEN)
    s += text(137, 292, "Q = попереднє", 11, GREEN, "middle", "bold")
    s += text(137, 310, "значення (пам'ять)", 11, GREEN, "middle", "bold")
    cell(255, "SET", 1, 0, "Q → 1", RED)
    s += text(352, 290, "ставимо одиницю", 11, INK, "middle")
    cell(470, "RESET", 0, 1, "Q → 0", BLUE)
    s += text(567, 290, "ставимо нуль", 11, INK, "middle")
    cell(685, "ЗАБОРОНА", 1, 1, "Q=Q̄=0 (!)", GREY)
    s += text(782, 290, "не комплементарні", 11, GREY, "middle")
    s += text(782, 308, "→ так не роблять", 11, RED, "middle", "bold")
    s += text(W / 2, 388, "Уся пам'ять — у випадку «тримати»: прибрали S і R — і засувка зберігає, що в ній було.",
              12, INK, "middle", "bold")
    save("fig-16-2-2-cases.svg", s)


# ── Рис. 16.2.3 — заборонений стан і гонка ─────────────────────────────────
def fig162_forbidden():
    W, H = 840, 380
    s = header(W, H)
    s += text(W / 2, 34, "Чому S=R=1 заборонено: і не комплементарно, і гонка на виході", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "при S=R=1 обидва виходи стають 0 (Q має бути протилежним Q̄!); а зняти обидва воднораз — гонка",
              12, GREY, "middle", style="italic")
    # стан S=R=1
    s += rect(70, 96, 330, 230, "#fdf6f6", RED, 1.7, 10)
    s += text(235, 122, "Поки S=1 і R=1:", 13, RED, "middle", "bold")
    s += text(235, 156, "Q = 0   і   Q̄ = 0", 16, INK, "middle", "bold")
    s += text(235, 184, "але ж вони мусять бути", 11.5, GREY, "middle", style="italic")
    s += text(235, 200, "ПРОТИЛЕЖНІ — це збій", 11.5, RED, "middle", "bold")
    s += text(235, 240, "Q і Q̄ більше не «дзеркало»,", 11, INK, "middle")
    s += text(235, 258, "тож подальша логіка плутається", 11, INK, "middle")
    s += text(235, 296, "(сам стан ще «тихий», біда — далі)", 10.5, GREY, "middle", style="italic")
    # гонка при знятті
    s += rect(440, 96, 330, 230, "#fbf6ec", AMBER, 1.7, 10)
    s += text(605, 122, "Коли S і R падають у 0 воднораз:", 12, "#9a7322", "middle", "bold")
    s += text(605, 154, "хто «вистрелить» першим —", 12, INK, "middle", "bold")
    s += text(605, 172, "той і виграє", 12, INK, "middle", "bold")
    s += arrow(540, 205, 540, 235, GREEN, 2)
    s += text(540, 250, "Q=1?", 12, GREEN, "middle", "bold")
    s += arrow(670, 205, 670, 235, GREEN, 2)
    s += text(670, 250, "Q=0?", 12, GREEN, "middle", "bold")
    s += text(605, 285, "результат НЕПЕРЕДБАЧУВАНИЙ", 11.5, RED, "middle", "bold")
    s += text(605, 305, "(метастабільність — §16.8)", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, 358, "Висновок: одночасно set і reset — не можна. Правильні засувки потім захищають від цього.",
              12, INK, "middle", "bold")
    save("fig-16-2-3-forbidden.svg", s)


# ── Рис. 16.2.4 — часова діаграма S, R, Q ──────────────────────────────────
def fig162_waveform():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Часова діаграма: як S і R керують виходом Q", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "між імпульсами засувка ТРИМАЄ останнє значення — оце утримання і є збережений біт",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 130, 820

    def waveform(label, ylo, pulses, color):
        nonlocal s
        hi, lo = ylo - 18, ylo + 18
        s += text(95, ylo + 4, label, 13, color, "end", "bold")
        s += line(gx0, lo, gx1, lo, FAINT, 1)
        pts = [(gx0, lo)]
        for (a, b) in pulses:
            pts += [(a, lo), (a, hi), (b, hi), (b, lo)]
        pts.append((gx1, lo))
        s += polyline(pts, color, 2.4)

    waveform("S", 110, [(220, 270)], RED)
    waveform("R", 200, [(470, 520)], BLUE)
    # Q: 0 до 220, 1 від 220 до 470, 0 від 470
    hi, lo = 272, 308
    s += text(95, 294, "Q", 13, GREEN, "end", "bold")
    s += line(gx0, lo, gx1, lo, FAINT, 1)
    qs = [(gx0, lo), (220, lo), (220, hi), (470, hi), (470, lo), (gx1, lo)]
    s += polyline(qs, GREEN, 2.6)
    # анотації
    s += line(220, 90, 220, 308, GREY, 1, "3 3")
    s += line(470, 180, 470, 308, GREY, 1, "3 3")
    s += text(345, hi - 8, "Q тримає 1 (хоч S давно зник)", 11, GREY, "middle", style="italic")
    s += text(180, lo - 8, "0", 10.5, GREY, "middle")
    s += text(650, lo - 8, "Q тримає 0", 11, GREY, "middle", style="italic")
    s += text(245, 100, "set", 10.5, RED, "middle", "bold")
    s += text(495, 190, "reset", 10.5, BLUE, "middle", "bold")
    s += rect(70, 348, W - 140, 30, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 368, "Короткий S підняв Q і пішов — Q лишився 1. Короткий R його скинув. Між ними — утримання.",
              12, INK, "middle", "bold")
    save("fig-16-2-4-waveform.svg", s)


# ── Рис. 16.2.5 — застосування: придушення дребезгу кнопки ─────────────────
def fig162_debounce():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо: SR-засувка прибирає «дребезг» перемикача", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "перший дотик контакту перекидає засувку — і подальше «торохтіння» вже нічого не змінює",
              12, GREY, "middle", style="italic")
    # перемикач SPDT
    s += line(120, 150, 120, 250, INK, 2)
    s += text(120, 140, "спільний", 10, INK, "middle")
    s += circle(120, 150, 4, INK, INK, 1)
    s += circle(120, 250, 4, INK, INK, 1)
    s += line(110, 130, 110, 270, INK, 2)
    s += line(96, 130, 124, 130, INK, 2)
    s += line(96, 270, 124, 270, INK, 2)
    s += text(120, 122, "GND", 9.5, BLUE, "middle")
    s += text(70, 200, "SPDT", 11, INK, "middle", "bold")
    s += line(120, 150, 200, 165, INK, 2)   # рухомий контакт до верхнього
    s += line(200, 150, 280, 150, INK, 1.8)
    s += circle(200, 165, 4, "#fff", INK, 1.5)
    s += circle(200, 250, 4, "#fff", INK, 1.5)
    s += text(255, 142, "→ S̄", 11, RED, "middle", "bold")
    s += line(200, 250, 280, 250, INK, 1.8)
    s += text(255, 268, "→ R̄", 11, BLUE, "middle", "bold")
    # підтяжки
    s += line(200, 165, 200, 110, INK, 1.4)
    s += rect(192, 86, 16, 20, "none", INK, 1.4)
    s += line(200, 70, 200, 86, RED, 1.6)
    s += text(216, 80, "Vdd", 9, RED, "start")
    s += line(200, 250, 200, 305, INK, 1.4)
    s += rect(192, 305, 16, 20, "none", INK, 1.4)
    s += line(200, 325, 200, 340, RED, 1.6)
    # NAND-засувка (активно-низькі входи)
    s += rect(300, 130, 120, 140, "#eef7ee", GREEN, 2, 10)
    s += text(360, 190, "SR-засувка", 12, INK, "middle", "bold")
    s += text(360, 210, "(на NAND,", 10, GREY, "middle")
    s += text(360, 224, "входи S̄,R̄)", 10, GREY, "middle")
    s += line(420, 200, 470, 200, INK, 1.8)
    s += text(476, 204, "чистий Q", 12, GREEN, "start", "bold")
    # дребезг vs чисто
    s += text(620, 110, "вхід (дребезг):", 11, INK, "start", "bold")
    bnc = [(540, 150), (560, 150), (560, 130), (568, 130), (568, 150), (576, 150), (576, 132), (584, 132), (584, 150), (760, 150)]
    s += polyline(bnc, AMBER, 2)
    s += text(620, 240, "вихід засувки:", 11, GREEN, "start", "bold")
    s += polyline([(540, 280), (562, 280), (562, 258), (760, 258)], GREEN, 2.4)
    s += text(660, 300, "одне чисте перемикання", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, 372, "Перший контакт «защолкнув» стан; торохтіння не дістає іншого входу, тож засувка не реагує (деталі — §22.5).",
              11.5, INK, "middle", "bold")
    save("fig-16-2-5-debounce.svg", s)


# ═══════════════════════ §16.3 — Тактований D-тригер ════════════════════════
def _clk(x, y):  # символ тактового входу (трикутник «фронт»)
    return f'<path d="M {x},{y-7} L {x+12},{y} L {x},{y+7}" fill="none" stroke="{INK}" stroke-width="1.8"/>\n'


def _dff_symbol(x, y, w=90, h=110):
    out = rect(x, y, w, h, "#fafafa", INK, 2, 6)
    out += text(x + 16, y + 32, "D", 14, INK, "start", "bold")
    out += text(x + w - 16, y + 32, "Q", 14, GREEN, "end", "bold")
    out += text(x + w - 16, y + h - 22, "Q̄", 13, GREEN, "end", "bold")
    out += _clk(x, y + h - 30)
    out += text(x + 18, y + h - 26, "clk", 11, INK, "start")
    return out


# ── Рис. 16.3.1 — тактований (gated) латч ──────────────────────────────────
def fig163_gated():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 34, "Перший крок: дозволити запис лише за сигналом такту", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "два AND «пропускають» S і R, лише коли такт=1; такт=0 → на засувку йдуть нулі → вона тримає",
              12, GREY, "middle", style="italic")
    s += text(110, 150, "S", 13, RED, "end", "bold")
    s += _pin(116, 150, 180, 150)
    s += text(110, 250, "R", 13, BLUE, "end", "bold")
    s += _pin(116, 250, 180, 250)
    s += text(110, 200, "такт", 12, INK, "end", "bold")
    s += _pin(116, 200, 150, 200)
    s += circle(150, 200, 3, INK, INK, 1)
    s += line(150, 200, 150, 165, INK, 1.6)
    s += line(150, 165, 180, 165, INK, 1.6)
    s += line(150, 200, 150, 235, INK, 1.6)
    s += line(150, 235, 180, 235, INK, 1.6)
    s += gate_and(180, 158, 40, 32)
    s += text(200, 138, "S·такт", 9.5, GREY, "middle")
    s += gate_and(180, 242, 40, 32)
    s += text(200, 280, "R·такт", 9.5, GREY, "middle")
    s += _pin(226, 158, 300, 158)
    s += _pin(226, 242, 300, 242)
    s += _box(300, 160, 120, 80, "SR-засувка", None, "#eef7ee")
    s += _pin(420, 200, 480, 200)
    s += text(486, 204, "Q", 14, GREEN, "start", "bold")
    s += rect(560, 120, 270, 170, "#f4f7f4", GREEN, 1.6, 10)
    s += text(695, 146, "Поведінка:", 12.5, INK, "middle", "bold")
    s += text(580, 176, "такт = 1:", 12, RED, "start", "bold")
    s += text(680, 176, "«відкрито» — Q стежить за S/R", 11, INK, "start")
    s += text(580, 206, "такт = 0:", 12, BLUE, "start", "bold")
    s += text(680, 206, "«зачинено» — Q тримає", 11, INK, "start")
    s += text(580, 244, "тепер запис відбувається", 11, GREY, "start", style="italic")
    s += text(580, 260, "не «будь-коли», а за тактом —", 11, GREY, "start", style="italic")
    s += text(580, 276, "та все ще цілий час, поки такт=1", 11, "#9a7322", "start", "bold")
    save("fig-16-3-1-gated.svg", s)


# ── Рис. 16.3.2 — D-латч: один вхід, без заборони ──────────────────────────
def fig163_dlatch():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "D-латч: один вхід даних D — і заборонений стан зникає", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "беремо S=D, R=D̄ (через інвертор): S і R завжди протилежні, тож S=R=1 неможливе",
              12, GREY, "middle", style="italic")
    s += text(110, 160, "D", 13, INK, "end", "bold")
    s += circle(140, 160, 3, INK, INK, 1)
    s += _pin(116, 160, 230, 160)
    s += text(180, 152, "S = D", 10, GREY, "middle")
    s += line(140, 160, 140, 230, INK, 1.6)
    s += gate_not(150, 230, 30, 26)
    s += _pin(192, 230, 230, 230)
    s += text(205, 222, "R = D̄", 10, GREY, "middle")
    s += text(110, 280, "такт", 12, INK, "end", "bold")
    s += _pin(116, 280, 230, 280)
    s += _box(230, 150, 130, 150, "тактований", "латч (gated)", "#eef7ee")
    s += _pin(360, 200, 430, 200)
    s += text(436, 204, "Q", 14, GREEN, "start", "bold")
    s += rect(540, 120, 290, 170, "#f4f7f4", GREEN, 1.6, 10)
    s += text(685, 146, "Тепер:", 12.5, INK, "middle", "bold")
    s += text(560, 176, "• такт=1 → Q стежить за D (Q=D)", 11.5, INK, "start")
    s += text(560, 200, "• такт=0 → Q тримає (пам'ять)", 11.5, INK, "start")
    s += text(560, 224, "• заборонений стан НЕМОЖЛИВИЙ", 11.5, GREEN, "start", "bold")
    s += text(560, 252, "Та поки такт=1, латч «прозорий»:", 11, "#9a7322", "start", "bold")
    s += text(560, 268, "будь-яка зміна D одразу йде на Q.", 11, "#9a7322", "start")
    save("fig-16-3-2-dlatch.svg", s)


# ── Рис. 16.3.3 — майстер-слейв → захоплення по фронту ─────────────────────
def fig163_master_slave():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "D-тригер: два латчі (майстер + слейв) ловлять D рівно по ФРОНТУ", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "латчі тактовані ПРОТИЛЕЖНО, тож «прозорі» по черзі — і пара пропускає D лише на мить переходу",
              12, GREY, "middle", style="italic")
    s += text(95, 175, "D", 13, INK, "end", "bold")
    s += _pin(100, 175, 170, 175)
    s += _box(170, 140, 130, 80, "МАЙСТЕР", "латч", "#eef4ff")
    s += _pin(300, 175, 370, 175)
    s += text(335, 167, "внутр.", 9.5, GREY, "middle")
    s += _box(370, 140, 130, 80, "СЛЕЙВ", "латч", "#eef7ee")
    s += _pin(500, 175, 580, 175)
    s += text(586, 179, "Q", 14, GREEN, "start", "bold")
    # такт
    s += text(95, 300, "такт", 12, INK, "end", "bold")
    s += _pin(100, 300, 235, 300)
    s += circle(235, 300, 3, INK, INK, 1)
    s += line(235, 300, 235, 220, INK, 1.6)
    s += _clk(229, 220)
    s += line(235, 300, 320, 300, INK, 1.6)
    s += gate_not(320, 300, 26, 22)
    s += line(352, 300, 435, 300, INK, 1.6)
    s += line(435, 300, 435, 220, INK, 1.6)
    s += _clk(429, 220)
    s += text(300, 318, "майстер — по такту", 10, GREY, "middle")
    s += text(470, 318, "слейв — по інверсії такту", 10, GREY, "middle")
    s += rect(620, 110, 230, 200, "#f4f7f4", GREEN, 1.6, 10)
    s += text(735, 136, "Як виходить «фронт»:", 12, INK, "middle", "bold")
    for i, t in enumerate(["• такт=0: майстер «дивиться»", "  на D, слейв тримає вихід",
                           "• такт 0→1 (ФРОНТ): майстер", "  замикається на тому D,",
                           "  слейв пропускає його на Q", "• між фронтами Q НЕ реагує",
                           "  на D зовсім"]):
        s += text(636, 162 + i * 21, t, 10.8, INK, "start")
    save("fig-16-3-3-master-slave.svg", s)


# ── Рис. 16.3.4 — поведінка: Q ловить D лише по фронту ─────────────────────
def fig163_waveform():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Поведінка D-тригера: Q бере значення D лише в МИТЬ фронту такту", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "між фронтами D може смикатися як завгодно — Q байдуже; він оновлюється тільки на наростанні такту",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 130, 830
    edges = [220, 400, 580, 760]

    def sq(label, yc, levels, color):
        # levels: список (x_start, value) сегментів
        nonlocal s
        hi, lo = yc - 16, yc + 16
        s += text(95, yc + 4, label, 13, color, "end", "bold")
        s += line(gx0, lo, gx1, lo, FAINT, 1)
        pts = []
        prevy = lo  # усі хвилі починаються з 0
        pts.append((gx0, prevy))
        for (x, v) in levels:
            ny = hi if v else lo
            pts.append((x, prevy))
            pts.append((x, ny))
            prevy = ny
        pts.append((gx1, prevy))
        s += polyline(pts, color, 2.4)

    # такт: меандр
    clk_levels = []
    x = gx0
    v = 0
    for e in edges:
        clk_levels.append((e - 40, 0))
        clk_levels.append((e, 1))
        clk_levels.append((e + 60, 0))
    sq("такт", 110, clk_levels, INK)
    for e in edges:
        s += line(e, 90, e, 330, GREY, 1, "3 3")
        s += text(e, 86, "▲", 10, RED, "middle", "bold")
    # D: змінюється, зокрема МІЖ фронтами (ті зміни Q проігнорує)
    # значення D у миті фронтів: 220→1, 400→0, 580→1, 760→1
    d_levels = [(150, 1), (270, 0), (340, 1), (370, 0), (520, 1), (640, 0), (700, 1)]
    sq("D", 200, d_levels, BLUE)
    # Q: семплює D на кожному фронті
    sampled = [1, 0, 1, 1]
    q_levels = []
    for i, e in enumerate(edges):
        q_levels.append((e, sampled[i]))
    sq("Q", 290, q_levels, GREEN)
    s += text(330, 178, "D смикнувся між фронтами — Q це проігнорує", 10.5, GREY, "middle", style="italic")
    s += text(W / 2, 372, "На кожному ▲ (наростання такту) Q ← (значення D у цю мить); далі тримає до наступного ▲.",
              12, INK, "middle", "bold")
    save("fig-16-3-4-waveform.svg", s)


# ── Рис. 16.3.5 — символ і роль робочого коня ──────────────────────────────
def fig163_symbol():
    W, H = 820, 350
    s = header(W, H)
    s += text(W / 2, 34, "Умовний символ D-тригера — і чому він «робочий кінь»", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "трикутник на тактовому вході = «спрацьовує по ФРОНТУ»; один вхід D, виходи Q і Q̄",
              12, GREY, "middle", style="italic")
    s += _dff_symbol(180, 110, 110, 130)
    s += _pin(120, 142, 180, 142)
    s += text(114, 146, "D", 14, INK, "end", "bold")
    s += _pin(120, 210, 180, 210)
    s += text(114, 214, "clk", 13, INK, "end", "bold")
    s += _pin(290, 142, 350, 142)
    s += text(356, 146, "Q", 14, GREEN, "start", "bold")
    s += _pin(290, 200, 350, 200)
    s += text(356, 204, "Q̄", 13, GREEN, "start", "bold")
    s += text(235, 100, "D-тригер", 13, INK, "middle", "bold")
    s += text(235, 260, "Q ← D по фронту clk", 11.5, GREY, "middle", style="italic")
    s += rect(470, 110, 320, 150, "#f4f7f4", GREEN, 1.6, 10)
    s += text(630, 136, "Чому він усюди:", 12.5, INK, "middle", "bold")
    for i, t in enumerate(["• один вхід, без заборонених станів",
                           "• запис лише в чітку мить (фронт) →",
                           "  уся машина крокує синхронно",
                           "• 8 поряд = РЕГІСТР на байт (§16.5)",
                           "• ланцюжок = ЛІЧИЛЬНИК (§16.7)"]):
        s += text(486, 164 + i * 22, t, 11.5, INK, "start")
    s += text(W / 2, 312, "D-тригер — основний елемент пам'яті всієї синхронної цифрової техніки.", 12.5, INK, "middle", "bold")
    save("fig-16-3-5-symbol.svg", s)


# ═══════════════════════ §16.4 — Фронт vs рівень ════════════════════════════
def wave(gx0, gx1, yc, transitions, color, label=None, start=0, amp=15):
    """Прямокутна хвиля. transitions = [(x, value0/1), ...]. start — рівень на початку."""
    hi, lo = yc - amp, yc + amp
    out = ""
    if label:
        out += text(gx0 - 12, yc + 4, label, 12.5, color, "end", "bold")
    out += line(gx0, lo, gx1, lo, FAINT, 1)
    prevy = lo if start == 0 else hi
    pts = [(gx0, prevy)]
    for (x, v) in transitions:
        ny = hi if v else lo
        pts.append((x, prevy))
        pts.append((x, ny))
        prevy = ny
    pts.append((gx1, prevy))
    out += polyline(pts, color, 2.3)
    return out


def _clk_pulses(edges, width=80):
    tr = []
    for e in edges:
        tr.append((e, 1))
        tr.append((e + width, 0))
    return tr


# ── Рис. 16.4.1 — рівень vs фронт на одній діаграмі ────────────────────────
def fig164_level_vs_edge():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Рівнева засувка проти тригера по фронту: та сама D, різний Q", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "латч «прозорий» цілий високий такт і ловить зміни D будь-коли; тригер бере D лише в мить фронту",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 130, 840
    edges = [200, 440, 680]
    s += wave(gx0, gx1, 110, _clk_pulses(edges), INK, "такт")
    for e in edges:
        s += line(e, 95, e, 360, GREY, 1, "3 3")
        s += text(e, 90, "▲", 9, RED, "middle", "bold")
    # позначити «прозоре вікно» латча
    s += rect(200, 95, 80, 14, "#fff3e0", "none", 0)
    s += text(240, 88, "вікно «прозоро»", 9, AMBER, "middle")
    s += wave(gx0, gx1, 190, [(240, 1)], BLUE, "D")
    s += text(300, 178, "D піднявся ПОСЕРЕДИНІ вікна", 10, GREY, "middle", style="italic")
    s += wave(gx0, gx1, 270, [(240, 1)], AMBER, "Q латч")
    s += text(330, 258, "латч одразу пішов за D (ще у вікні)", 10, AMBER, "middle", "bold")
    s += wave(gx0, gx1, 345, [(440, 1)], GREEN, "Q тригер")
    s += text(330, 333, "тригер чекав до НАСТУПНОГО фронту", 10, GREEN, "middle", "bold")
    s += text(W / 2, 398, "Між 1-м і 2-м фронтом виходи різні: латч уже 1, тригер ще 0 — бо латч прозорий, а тригер ні.",
              11.5, INK, "middle", "bold")
    save("fig-16-4-1-level-vs-edge.svg", s)


# ── Рис. 16.4.2 — проблема прозорості: гонка крізь латч ────────────────────
def fig164_racethrough():
    W, H = 860, 400
    s = header(W, H)
    s += text(W / 2, 34, "Чому рівневий латч небезпечний: гонка крізь прозоре вікно", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "якщо вихід латча вертається на вхід, то поки такт=1 нове значення «оббігає» петлю знов і знов",
              12, GREY, "middle", style="italic")
    # схема: латч із ЗЗ через інвертор
    s += _box(150, 130, 120, 70, "D-латч", None, "#eef4ff")
    s += _pin(90, 150, 150, 150)
    s += text(84, 154, "D", 12, INK, "end", "bold")
    s += _pin(110, 200, 150, 200)
    s += _clk(104, 200)
    s += text(118, 204, "такт", 10, INK, "start")
    s += _pin(270, 150, 330, 150)
    s += text(336, 154, "Q", 13, GREEN, "start", "bold")
    s += gate_not(330, 230, 28, 24)
    s += line(300, 150, 300, 230, INK, 1.5)
    s += line(300, 230, 330, 230, INK, 1.5)
    s += line(372, 230, 400, 230, INK, 1.5)
    s += line(400, 230, 400, 280, INK, 1.5)
    s += line(400, 280, 120, 280, INK, 1.5)
    s += line(120, 280, 120, 150, INK, 1.5)
    s += line(120, 150, 150, 150, INK, 1.5)
    s += text(260, 270, "ЗЗ: Q → D (через інвертор)", 10, GREY, "middle", style="italic")
    # хвиля: за один високий такт — кілька змін
    gx0, gx1 = 470, 840
    s += wave(gx0, gx1, 150, [(540, 1), (700, 0)], INK, "такт", amp=14)
    s += rect(540, 138, 160, 12, "#fff3e0", "none", 0)
    glitch = [(560, 1), (590, 0), (620, 1), (650, 0), (680, 1)]
    s += wave(gx0, gx1, 250, glitch, RED, "Q", amp=14)
    s += text(655, 218, "смикається кілька разів", 10, RED, "middle", "bold")
    s += text(655, 300, "за ОДИН такт!", 11, RED, "middle", "bold")
    s += text(655, 320, "результат залежить від затримок", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, 380, "Кілька оновлень за такт — непередбачувано. Саме тому прозорий латч не годиться для петель.",
              11.5, INK, "middle", "bold")
    save("fig-16-4-2-racethrough.svg", s)


# ── Рис. 16.4.3 — фронт усе лагодить: одне оновлення за такт ────────────────
def fig164_edge_solves():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 34, "Фронт усе лагодить: рівно ОДНЕ оновлення за такт", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "тригер захоплює вхід лише на мить; нове значення встигне вплинути аж на НАСТУПНОМУ фронті",
              12, GREY, "middle", style="italic")
    s += _dff_symbol(160, 120, 100, 110)
    s += _pin(100, 152, 160, 152)
    s += text(94, 156, "D", 12, INK, "end", "bold")
    s += _pin(110, 200, 160, 200)
    s += text(118, 204, "такт", 10, INK, "start")
    s += _pin(260, 152, 320, 152)
    s += text(326, 156, "Q", 13, GREEN, "start", "bold")
    s += gate_not(320, 250, 26, 22)
    s += line(300, 152, 300, 250, INK, 1.5)
    s += line(300, 250, 320, 250, INK, 1.5)
    s += line(358, 250, 380, 250, INK, 1.5)
    s += line(380, 250, 380, 300, INK, 1.5)
    s += line(380, 300, 130, 300, INK, 1.5)
    s += line(130, 300, 130, 152, INK, 1.5)
    s += line(130, 152, 160, 152, INK, 1.5)
    s += text(255, 290, "ЗЗ Q → D, але…", 10, GREY, "middle", style="italic")
    # хвиля: чітке перемикання щотакту (ділення на 2)
    gx0, gx1 = 470, 840
    edges = [510, 600, 690, 780]
    s += wave(gx0, gx1, 140, _clk_pulses(edges, 35), INK, "такт", amp=13)
    for e in edges:
        s += line(e, 128, e, 240, GREY, 1, "3 3")
    s += wave(gx0, gx1, 220, [(510, 1), (600, 0), (690, 1), (780, 0)], GREEN, "Q", amp=13)
    s += text(655, 270, "по 1 чіткій зміні на фронт", 10, GREEN, "middle", "bold")
    s += text(655, 288, "(тут Q ділить такт навпіл)", 9.5, GREY, "middle", style="italic")
    s += text(W / 2, 350, "Захоплене значення стає входом для НАСТУПНОГО фронту — стани чітко розділені в часі.",
              11.5, INK, "middle", "bold")
    save("fig-16-4-3-edge-solves.svg", s)


# ── Рис. 16.4.4 — зсувний регістр: 1 крок за такт ──────────────────────────
def fig164_shift():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо це: у ланцюзі тригерів біт рухається рівно на 1 щабель за такт", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "на фронтах усі тригери оновлюються РАЗОМ, тож біт акуратно «крокує»; рівневі латчі прогнали б його наскрізь",
              11.5, GREY, "middle", style="italic")
    # ланцюг із 3 тригерів
    for i in range(3):
        x = 150 + i * 200
        s += rect(x, 96, 90, 70, "#fafafa", INK, 2, 6)
        s += text(x + 45, 126, f"D-тр {i+1}", 12, INK, "middle", "bold")
        s += _clk(x, 150)
        if i == 0:
            s += _pin(90, 116, 150, 116)
            s += text(84, 120, "вхід", 11, INK, "end", "bold")
        s += _pin(x + 90, 116, x + (110 if i < 2 else 110), 116)
        s += text(x + 100, 110, f"Q{i+1}", 10, GREEN, "middle", "bold")
    # таблиця руху біта
    s += text(150, 210, "вхід=1 один такт, далі 0:", 12, INK, "start", "bold")
    rows = [("такт 1", 1, 0, 0), ("такт 2", 0, 1, 0), ("такт 3", 0, 0, 1)]
    s += text(250, 240, "Q1", 11, GREEN, "middle", "bold")
    s += text(330, 240, "Q2", 11, GREEN, "middle", "bold")
    s += text(410, 240, "Q3", 11, GREEN, "middle", "bold")
    for r, (lab, q1, q2, q3) in enumerate(rows):
        yy = 264 + r * 30
        s += text(180, yy, lab, 11.5, INK, "start", "bold")
        for c, q in enumerate((q1, q2, q3)):
            x = 250 + c * 80
            col = RED if q else GREY
            s += circle(x, yy - 4, 11, "#fdf4f4" if q else "#f4f4f4", col, 1.8)
            s += text(x, yy, str(q), 12, col, "middle", "bold")
    s += rect(540, 220, 300, 120, "#f4f7f4", GREEN, 1.6, 10)
    s += text(690, 246, "Один біт «1» крокує:", 12, INK, "middle", "bold")
    s += text(690, 270, "Q1 → Q2 → Q3,", 12.5, GREEN, "middle", "bold")
    s += text(690, 290, "по одному щаблю за фронт.", 11, INK, "middle")
    s += text(690, 316, "Це працює ЛИШЕ тому, що тригери", 10, GREY, "middle", style="italic")
    s += text(690, 330, "по фронту, а не прозорі латчі.", 10, GREY, "middle", style="italic")
    save("fig-16-4-4-shift.svg", s)


# ── Рис. 16.4.5 — наростання vs спад + чистий фронт ────────────────────────
def fig164_rise_fall():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "По якому фронту — і чому фронт мусить бути ЧИСТИМ", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "буває спрацювання по наростанню (❯) і по спаду (❯ з кружком); а кволий фронт (§14.5) збиває тригер",
              12, GREY, "middle", style="italic")
    # по наростанню
    s += _dff_symbol(110, 100, 90, 90)
    s += text(155, 90, "по наростанню", 11, INK, "middle", "bold")
    s += wave(250, 380, 130, [(300, 1), (340, 0)], INK, None, amp=12)
    s += text(300, 110, "▲ тут", 9.5, RED, "middle", "bold")
    s += arrow(300, 118, 300, 124, RED, 1.6)
    # по спаду
    s += rect(470, 100, 90, 90, "#fafafa", INK, 2, 6)
    s += text(485, 145, "D", 13, INK, "start", "bold")
    s += text(545, 145, "Q", 13, GREEN, "end", "bold")
    s += _clk(470, 165)
    s += circle(464, 165, 5, "#fff", INK, 1.8)   # кружок = по спаду
    s += text(515, 90, "по спаду", 11, INK, "middle", "bold")
    s += wave(580, 720, 130, [(620, 1), (680, 0)], INK, None, amp=12)
    s += text(680, 110, "▼ тут", 9.5, BLUE, "middle", "bold")
    s += arrow(680, 118, 680, 124, BLUE, 1.6)
    # чистий фронт
    s += rect(120, 220, 620, 100, "#fbf6ec", AMBER, 1.6, 10)
    s += text(430, 246, "Фронт має бути КРУТИЙ (§14.5):", 12.5, "#9a7322", "middle", "bold")
    s += text(290, 280, "крутий → чітка мить спрацювання", 11, GREEN, "middle", "bold")
    s += text(290, 300, "(тригер знає, коли саме ловити)", 10, GREY, "middle", style="italic")
    s += text(600, 280, "кволий/брудний → тремтить, подвоюється", 11, RED, "middle", "bold")
    s += text(600, 300, "(тут і стає в пригоді тригер Шмітта §14.6)", 10, GREY, "middle", style="italic")
    save("fig-16-4-5-rise-fall.svg", s)


# ═══════════════════════ §16.5 — Регістр ════════════════════════════════════
def _ff_small(x, y, w=64, h=70, dlab="D", qlab="Q", top_pin=True):
    out = rect(x, y, w, h, "#fafafa", INK, 1.8, 5)
    out += _clk(x, y + h - 16)
    if dlab:
        out += text(x + 10, y + 22, dlab, 11, INK, "start", "bold")
    if qlab:
        out += text(x + w - 10, y + 22, qlab, 11, GREEN, "end", "bold")
    return out


# ── Рис. 16.5.1 — паралельний регістр: 8 тригерів = байт ───────────────────
def fig165_parallel():
    W, H = 900, 360
    s = header(W, H)
    s += text(W / 2, 34, "Регістр: 8 D-тригерів зі спільним тактом = пам'ять на байт", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "усі біти захоплюються ОДНОЧАСНО на одному фронті — так зберігають ціле слово (число)",
              12, GREY, "middle", style="italic")
    x0 = 70
    for i in range(8):
        x = x0 + i * 100
        s += rect(x, 130, 70, 80, "#fafafa", INK, 1.8, 5)
        s += text(x + 35, 175, "тр", 11, INK, "middle", "bold")
        s += _clk(x, 194)
        # вхід D зверху
        s += _pin(x + 35, 100, x + 35, 130)
        s += text(x + 35, 92, f"D{i}", 10, INK, "middle", "bold")
        # вихід Q знизу
        s += _pin(x + 35, 210, x + 35, 245)
        s += text(x + 35, 260, f"Q{i}", 10, GREEN, "middle", "bold")
    # спільний такт
    s += line(40, 300, 810, 300, INK, 2)
    for i in range(8):
        x = x0 + i * 100
        s += line(x, 194, x, 300, INK, 1.4)
        s += circle(x, 300, 3, INK, INK, 1)
    s += text(34, 304, "такт", 12, RED, "end", "bold")
    s += text(W / 2, 336, "Один фронт такту — і всі 8 бітів записалися разом. Вісім тригерів тримають один байт.",
              12, INK, "middle", "bold")
    save("fig-16-5-1-parallel.svg", s)


# ── Рис. 16.5.2 — дозвіл запису (load enable) ──────────────────────────────
def fig165_load_enable():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Дозвіл запису: регістр тримає, поки не накажуть «завантажити»", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "перед тригером — MUX: load=0 повертає старе значення (тримати), load=1 пропускає нові дані",
              12, GREY, "middle", style="italic")
    # MUX
    s += text(95, 150, "нові дані", 11, INK, "end", "bold")
    s += _pin(100, 150, 180, 150)
    s += text(95, 200, "(старе Q)", 10.5, GREY, "end")
    s += _pin(100, 200, 180, 200)
    s += f'<path d="M 180,135 L 215,150 L 215,200 L 180,215 Z" fill="#fbf6ec" stroke="{INK}" stroke-width="2"/>\n'
    s += text(197, 179, "MUX", 10, INK, "middle", "bold")
    s += _pin(215, 175, 280, 175)
    s += _ff_small(280, 140, 90, 70)
    s += text(325, 130, "D-тригер", 11, INK, "middle", "bold")
    s += _pin(370, 162, 470, 162)
    s += text(476, 166, "Q", 13, GREEN, "start", "bold")
    # зворотний зв'язок Q → нижній вхід MUX
    s += circle(430, 162, 3, INK, INK, 1)
    s += line(430, 162, 430, 290, INK, 1.4)
    s += line(430, 290, 130, 290, INK, 1.4)
    s += line(130, 290, 130, 200, INK, 1.4)
    s += line(130, 200, 100, 200, INK, 1.4)
    # керування load
    s += _pin(197, 250, 197, 215)
    s += text(197, 268, "load", 11, RED, "middle", "bold")
    s += rect(560, 120, 280, 150, "#f4f7f4", GREEN, 1.6, 10)
    s += text(700, 146, "Поведінка:", 12.5, INK, "middle", "bold")
    s += text(580, 176, "load=1 → запис нових даних", 12, INK, "start")
    s += text(580, 202, "load=0 → MUX вертає Q на вхід:", 12, INK, "start")
    s += text(596, 222, "тригер перезаписує себе ж →", 11, GREY, "start")
    s += text(596, 240, "значення не змінюється (тримає)", 11, GREEN, "start", "bold")
    s += text(W / 2, 332, "Так роблять кожен біт. Регістр зберігає число, поки не подадуть load — тоді бере нове.",
              12, INK, "middle", "bold")
    save("fig-16-5-2-load-enable.svg", s)


# ── Рис. 16.5.3 — зсувний регістр і його типи ──────────────────────────────
def fig165_shift():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Зсувний регістр: тригери ланцюжком — дані «їдуть» уздовж", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "вихід кожного → вхід наступного; за фронт уся низка зсувається на один щабель",
              12, GREY, "middle", style="italic")
    for i in range(4):
        x = 130 + i * 160
        s += rect(x, 110, 90, 70, "#fafafa", INK, 1.8, 5)
        s += text(x + 45, 150, f"тр {i+1}", 11, INK, "middle", "bold")
        s += _clk(x, 164)
        if i < 3:
            s += arrow(x + 90, 145, x + 160, 145, INK, 1.8)
        s += _pin(x + 45, 180, x + 45, 205)
        s += text(x + 45, 218, f"Q{i+1}", 9.5, GREEN, "middle", "bold")
    s += _pin(60, 145, 130, 145)
    s += text(54, 149, "вхід", 11, INK, "end", "bold")
    s += _pin(670, 145, 740, 145)
    s += text(746, 149, "вихід", 11, GREEN, "start", "bold")
    # типи
    s += rect(70, 250, W - 140, 100, "none", GREY, 1.2, 10)
    s += text(W / 2, 274, "Три способи вмикати — звідси три типи:", 12.5, INK, "middle", "bold")
    types = [("SIPO", "вхід послідовно (1 дріт) → вихід паралельно (всі Q)"),
             ("PISO", "вхід паралельно (завантажили все) → вихід послідовно (1 дріт)"),
             ("SISO", "і вхід, і вихід послідовні — лінія затримки")]
    for i, (t, d) in enumerate(types):
        yy = 300 + i * 18
        s += text(110, yy, t + ":", 11.5, RED, "start", "bold")
        s += text(175, yy, d, 11, INK, "start")
    save("fig-16-5-3-shift.svg", s)


# ── Рис. 16.5.4 — серійно↔паралельно (серце UART/SPI) ──────────────────────
def fig165_serial_parallel():
    W, H = 880, 370
    s = header(W, H)
    s += text(W / 2, 34, "Головне застосування: перетворення серійне ↔ паралельне", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "по одному дроту біти йдуть ПО ЧЕРЗІ; зсувний регістр збирає їх у байт (і навпаки) — основа UART, SPI",
              11.5, GREY, "middle", style="italic")
    # серійний потік
    s += text(75, 130, "1 дріт,", 11, INK, "start", "bold")
    s += text(75, 146, "біти по черзі:", 11, INK, "start")
    s += wave(80, 280, 185, [(110, 1), (135, 0), (160, 1), (185, 1), (210, 0), (235, 1)], BLUE, None, amp=12)
    s += text(180, 215, "час →", 9.5, GREY, "middle", style="italic")
    s += arrow(290, 185, 340, 185, INK, 2)
    # зсувний регістр
    s += _box(340, 150, 150, 70, "зсувний", "регістр (SIPO)", "#eef7ee")
    s += _clk(340, 200)
    # паралельний вихід
    for i in range(6):
        s += _pin(490, 160 + i * 10, 520, 160 + i * 10)
    s += text(540, 175, "8 бітів", 12, GREEN, "start", "bold")
    s += text(540, 193, "одразу (байт)", 11, GREEN, "start")
    s += rect(70, 250, W - 140, 100, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 276, "Так приймач послідовної лінії «складає» байт із бітів, а передавач — «розкладає» байт у біти.",
              12, INK, "middle", "bold")
    s += text(W / 2, 300, "Це буквально серце UART (Розділ 35) і SPI (Розділ 37): зсувний регістр на кожному кінці.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 324, "Один дріт + такт несе ціле число — зсувний регістр перекладає між «по черзі» і «все разом».",
              11, GREY, "middle", style="italic")
    save("fig-16-5-4-serial-parallel.svg", s)


# ── Рис. 16.5.5 — регістри в процесорі ─────────────────────────────────────
def fig165_processor():
    W, H = 860, 380
    s = header(W, H)
    s += text(W / 2, 34, "Навіщо: регістри — це «руки» процесора, де лежать числа", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "АЛП (§15.7) рахує, а регістри тримають його операнди й результат — разом це обчислювальне ядро",
              12, GREY, "middle", style="italic")
    # регістри
    for i, lab in enumerate(["R0", "R1", "R2", "R3"]):
        y = 110 + i * 45
        s += rect(120, y, 110, 36, "#eef7ee", GREEN, 1.8, 6)
        s += text(175, y + 23, f"регістр {lab}", 11.5, INK, "middle", "bold")
    s += text(175, 308, "регістровий файл", 11, GREY, "middle", style="italic")
    # АЛП
    s += f'<path d="M 380,130 L 470,150 L 470,250 L 380,270 L 380,210 L 395,200 L 380,190 Z" fill="#eef4ff" stroke="{INK}" stroke-width="2"/>\n'
    s += text(425, 205, "АЛП", 14, INK, "middle", "bold")
    s += arrow(230, 160, 380, 165, INK, 1.8)
    s += arrow(230, 250, 380, 235, INK, 1.8)
    s += text(305, 150, "операнди", 10, GREY, "middle")
    s += arrow(470, 200, 540, 200, GREEN, 2)
    s += text(505, 192, "результат", 10, GREEN, "middle", "bold")
    s += line(540, 200, 540, 330, INK, 1.5)
    s += line(540, 330, 175, 330, INK, 1.5)
    s += arrow(175, 330, 175, 304, INK, 1.5)
    s += text(360, 350, "результат вертається в регістр", 10, GREY, "middle", style="italic")
    # інші регістри
    s += rect(600, 120, 230, 150, "#f4f7f4", GREEN, 1.6, 10)
    s += text(715, 146, "Спеціальні регістри:", 12, INK, "middle", "bold")
    for i, t in enumerate(["• лічильник команд (PC) — де ми", "  в програмі (§18.2)",
                           "• регістр інструкції — що робимо", "• регістр адреси/даних пам'яті",
                           "• прапорці (нуль, перенос…)"]):
        s += text(616, 172 + i * 20, t, 10.8, INK, "start")
    s += text(W / 2, 360, "Регістр + АЛП = датапас. Додамо керування (Розділ 18) — і це вже процесор.", 12, INK, "middle", "bold")
    save("fig-16-5-5-processor.svg", s)


# ═══════════════════════ §16.6 — Тактовий сигнал ════════════════════════════
def _crystal(cx, cy):
    out = line(cx - 22, cy - 14, cx - 22, cy + 14, INK, 2)
    out += rect(cx - 14, cy - 16, 28, 32, "#eef4ff", INK, 2, 2)
    out += line(cx + 22, cy - 14, cx + 22, cy + 14, INK, 2)
    out += line(cx - 30, cy, cx - 22, cy, INK, 1.8)
    out += line(cx + 22, cy, cx + 30, cy, INK, 1.8)
    return out


# ── Рис. 16.6.1 — тактовий сигнал: період, частота ─────────────────────────
def fig166_clock():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 34, "Тактовий сигнал: рівномірний «пульс», за яким крокує машина", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "період T між фронтами, частота f = 1/T; зазвичай половину часу 1, половину 0 (шпаруватість 50%)",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 110, 800
    edges = [180, 320, 460, 600, 740]
    s += wave(gx0, gx1, 150, _clk_pulses(edges, 70), INK, "такт", amp=22)
    # період
    s += line(180, 200, 320, 200, RED, 1.6)
    s += line(180, 194, 180, 206, RED, 1.6)
    s += line(320, 194, 320, 206, RED, 1.6)
    s += text(250, 220, "період T", 12, RED, "middle", "bold")
    for e in edges:
        s += text(e, 118, "▲", 9, RED, "middle", "bold")
    # частоти
    s += rect(110, 250, W - 220, 90, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 274, "f = 1/T — скільки тактів за секунду:", 12.5, INK, "middle", "bold")
    fr = [("1 Гц", "1 такт/с"), ("16 МГц", "Arduino Uno"), ("240 МГц", "ядро ESP32"), ("3 ГГц", "ПК")]
    for i, (a, b) in enumerate(fr):
        x = 200 + i * 165
        s += text(x, 304, a, 13, RED, "middle", "bold")
        s += text(x, 324, b, 10.5, GREY, "middle")
    save("fig-16-6-1-clock.svg", s)


# ── Рис. 16.6.2 — синхронність: один такт — усі крокують разом ──────────────
def fig166_synchronous():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Синхронність: один такт на всіх — машина крокує в ногу", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "такт — це диригент: на кожному його фронті ВСІ тригери оновлюються одночасно, крок за кроком",
              12, GREY, "middle", style="italic")
    # джерело такту
    s += rect(70, 150, 90, 50, "#fdf4f4", RED, 2, 8)
    s += text(115, 180, "ТАКТ", 12, RED, "middle", "bold")
    s += line(160, 175, 230, 175, RED, 2)
    s += circle(230, 175, 3, RED, RED, 1)
    s += line(230, 110, 230, 280, RED, 2)
    # тригери
    for i in range(4):
        y = 110 + i * 50
        s += rect(280, y - 15, 90, 34, "#fafafa", INK, 1.8, 5)
        s += text(325, y + 7, f"тригер {i+1}", 10.5, INK, "middle", "bold")
        s += line(230, y, 280, y, RED, 1.4)
        s += circle(230, y, 2.5, RED, RED, 1)
        s += _clk(280, y + 2)
    s += text(325, 320, "усі тактовані РАЗОМ", 11, RED, "middle", "bold")
    s += rect(450, 110, 380, 180, "#f4f7f4", GREEN, 1.6, 10)
    s += text(640, 136, "Що дає спільний такт:", 12.5, INK, "middle", "bold")
    for i, t in enumerate(["• у машині є єдиний «момент істини» —", "  фронт такту, коли стан змінюється",
                           "• між фронтами все «застигло» й", "  логіка спокійно встигає порахувати",
                           "• уся система передбачувана:", "  крок — порахувати — крок — порахувати",
                           "• це і є СИНХРОННИЙ дизайн"]):
        s += text(466, 162 + i * 19, t, 10.8, INK, "start")
    save("fig-16-6-2-synchronous.svg", s)


# ── Рис. 16.6.3 — як роблять такт: кільце vs кварц ─────────────────────────
def fig166_generate():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Звідки береться такт: кільцевий генератор і кварц", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "непарне кільце інверторів осцилює (§16.1), та неточно; кварц дає стабільну, точну частоту",
              12, GREY, "middle", style="italic")
    # кільцевий
    s += rect(50, 90, 380, 250, "none", FAINT, 1.5, 10)
    s += text(240, 114, "Кільцевий генератор (3 інвертори)", 12, INK, "middle", "bold")
    for i in range(3):
        x = 120 + i * 90
        s += gate_not(x, 175, 34, 28)
        if i < 2:
            s += line(x + 46, 175, x + 90, 175, INK, 1.6)
    s += line(286, 175, 320, 175, INK, 1.6)
    s += line(320, 175, 320, 130, INK, 1.6)
    s += line(320, 130, 90, 130, INK, 1.6)
    s += line(90, 130, 90, 175, INK, 1.6)
    s += arrow(90, 175, 120, 175, INK, 1.6)
    s += wave(90, 400, 245, [(120, 1), (160, 0), (200, 1), (240, 0), (280, 1), (320, 0), (360, 1)], RED, None, amp=14)
    s += text(240, 290, "просто, та частота «гуляє»", 11, RED, "middle", "bold")
    s += text(240, 308, "(залежить від затримок, температури)", 10, GREY, "middle", style="italic")
    s += text(240, 326, "годиться для приблизного такту", 10, GREY, "middle", style="italic")
    # кварц
    s += rect(450, 90, 380, 250, "none", FAINT, 1.5, 10)
    s += text(640, 114, "Кварцовий генератор", 12, INK, "middle", "bold")
    s += gate_not(560, 175, 40, 32, bubble=False)
    s += text(580, 150, "підсилювач", 9.5, GREY, "middle")
    s += line(606, 175, 650, 175, INK, 1.6)
    s += line(540, 175, 540, 230, INK, 1.6)
    s += line(540, 230, 700, 230, INK, 1.6)
    s += line(700, 230, 700, 175, INK, 1.6)
    s += line(650, 175, 700, 175, INK, 1.6)
    s += _crystal(620, 230)
    s += text(620, 258, "кварц", 10, INK, "middle", "bold")
    s += line(650, 175, 730, 175, INK, 1.6)
    s += text(736, 179, "такт", 11, GREEN, "start", "bold")
    s += text(640, 290, "точна, стабільна частота", 11, GREEN, "middle", "bold")
    s += text(640, 308, "(механічний резонанс кристала)", 10, GREY, "middle", style="italic")
    s += text(640, 326, "так роблять головний такт (історія — §24)", 10, GREY, "middle", style="italic")
    save("fig-16-6-3-generate.svg", s)


# ── Рис. 16.6.4 — бюджет періоду: логіка мусить устигнути ──────────────────
def fig166_period_budget():
    W, H = 880, 400
    s = header(W, H)
    s += text(W / 2, 34, "Такт — це «ручка швидкості»: період мусить вмістити роботу логіки", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "між двома фронтами комбінаційна логіка має ВСТИГНУТИ порахувати (критичний шлях) + запас",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 120, 820
    # такт
    s += wave(gx0, gx1, 110, [(250, 1), (290, 0), (620, 1), (660, 0)], INK, "такт", amp=14)
    s += line(250, 90, 250, 350, GREY, 1, "3 3")
    s += line(620, 90, 620, 350, GREY, 1, "3 3")
    s += text(250, 86, "▲", 9, RED, "middle", "bold")
    s += text(620, 86, "▲", 9, RED, "middle", "bold")
    s += line(250, 150, 620, 150, RED, 1.6)
    s += text(435, 144, "період T", 11.5, RED, "middle", "bold")
    # логіка встигла (добре)
    s += text(95, 200, "логіка", 11, INK, "end", "bold")
    s += polyline([(250, 215), (270, 215), (340, 185), (520, 185), (620, 185)], GREEN, 2.4)
    s += text(390, 178, "порахувала й «устоялась»", 10, GREEN, "middle", "bold")
    s += line(520, 170, 520, 200, GREEN, 1.2, "3 3")
    s += line(520, 200, 620, 200, GREEN, 1.6)
    s += text(570, 213, "запас", 9.5, GREEN, "middle", "bold")
    s += text(310, 232, "✔ встигла до наступного фронту", 11, GREEN, "start", "bold")
    # якщо такт надто швидкий (погано)
    s += text(95, 290, "надто", 10.5, RED, "end", "bold")
    s += text(95, 303, "швидко", 10.5, RED, "end", "bold")
    s += line(450, 320, 450, 270, RED, 1.4, "4 3")
    s += text(450, 262, "наступний фронт ТУТ", 10, RED, "middle", "bold")
    s += polyline([(250, 320), (270, 320), (430, 285), (470, 285)], AMBER, 2.4)
    s += text(360, 340, "✘ логіка ще рахує — фронт ловить «сире» → помилка", 10.5, RED, "middle", "bold")
    s += text(W / 2, 378, "Тому є МАКСИМАЛЬНА частота: T ≥ найдовший шлях логіки + запас. Швидше — лише спростивши логіку (§18).",
              11, INK, "middle", "bold")
    save("fig-16-6-4-period-budget.svg", s)


# ── Рис. 16.6.5 — розведення такту й перекіс (skew) ────────────────────────
def fig166_skew():
    W, H = 860, 340
    s = header(W, H)
    s += text(W / 2, 34, "Розведення такту: фронт мусить дійти до всіх майже водночас", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "якщо до різних тригерів такт приходить у різний час (перекіс, skew) — синхронність ламається",
              12, GREY, "middle", style="italic")
    # дерево такту
    s += rect(60, 150, 80, 44, "#fdf4f4", RED, 2, 8)
    s += text(100, 177, "ТАКТ", 11, RED, "middle", "bold")
    s += line(140, 172, 200, 172, RED, 2)
    s += circle(200, 172, 3, RED, RED, 1)
    s += line(200, 110, 200, 250, RED, 2)
    for i, dy in enumerate((110, 172, 250)):
        s += line(200, dy, 280, dy, RED, 1.6)
        s += rect(280, dy - 16, 80, 32, "#fafafa", INK, 1.6, 5)
        s += text(320, dy + 4, f"тригер", 10, INK, "middle", "bold")
        s += _clk(280, dy + 2)
    s += text(420, 172, "«дерево такту»", 11, GREY, "start", style="italic")
    s += text(420, 192, "(балансують довжини,", 10, GREY, "start")
    s += text(420, 208, "щоб фронт приходив рівно)", 10, GREY, "start")
    s += rect(560, 110, 280, 160, "#fbf6ec", AMBER, 1.6, 10)
    s += text(700, 136, "Перекіс (skew):", 12.5, "#9a7322", "middle", "bold")
    s += text(580, 164, "якщо один тригер бачить фронт", 11, INK, "start")
    s += text(580, 182, "пізніше за сусіда, дані можуть", 11, INK, "start")
    s += text(580, 200, "«прослизнути» на зайвий щабель", 11, INK, "start")
    s += text(580, 226, "тому такт розводять акуратно,", 10.5, GREY, "start", style="italic")
    s += text(580, 242, "як гілки дерева однакової довжини", 10.5, GREY, "start", style="italic")
    s += text(580, 260, "(строгі межі часу — далі §16.8)", 10.5, GREY, "start", style="italic")
    save("fig-16-6-5-skew.svg", s)


# ═══════════════════════ §16.7 — Лічильники ═════════════════════════════════
# ── Рис. 16.7.1 — toggle-тригер: ділить частоту навпіл ─────────────────────
def fig167_toggle():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Toggle-тригер (T): перемикається щотакту й ділить частоту на 2", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "D-тригер, у якого вхід D з'єднано з власним Q̄: щофронту Q стає протилежним → 0,1,0,1…",
              12, GREY, "middle", style="italic")
    s += _dff_symbol(120, 110, 100, 100)
    s += _pin(70, 200, 120, 200)
    s += text(64, 204, "такт", 11, INK, "end", "bold")
    s += text(165, 100, "T-тригер", 12, INK, "middle", "bold")
    s += _pin(220, 142, 280, 142)
    s += text(286, 146, "Q", 13, GREEN, "start", "bold")
    # ЗЗ Q̄ → D
    s += line(220, 188, 250, 188, INK, 1.4)
    s += text(232, 182, "Q̄", 9, GREY, "middle")
    s += line(250, 188, 250, 240, INK, 1.4)
    s += line(250, 240, 100, 240, INK, 1.4)
    s += line(100, 240, 100, 142, INK, 1.4)
    s += arrow(100, 142, 120, 142, INK, 1.4)
    s += text(170, 256, "Q̄ назад на D", 9.5, GREY, "middle", style="italic")
    # хвиля: такт удвічі частіший за Q
    gx0, gx1 = 360, 820
    edges = [400, 460, 520, 580, 640, 700, 760]
    s += wave(gx0, gx1, 130, _clk_pulses(edges, 30), INK, "такт", amp=14)
    for e in edges:
        s += line(e, 118, e, 230, GREY, 1, "3 3")
    qt = [(400, 1), (460, 0), (520, 1), (580, 0), (640, 1), (700, 0), (760, 1)]
    s += wave(gx0, gx1, 210, qt, GREEN, "Q", amp=14)
    s += text(590, 256, "Q удвічі повільніший за такт (÷2)", 11, GREEN, "middle", "bold")
    s += text(W / 2, 330, "Один toggle-тригер = поділ частоти на 2. З цього й будують лічильники.", 12, INK, "middle", "bold")
    save("fig-16-7-1-toggle.svg", s)


# ── Рис. 16.7.2 — ланцюговий (ripple) лічильник: рахує у двійковій ──────────
def fig167_ripple():
    W, H = 880, 440
    s = header(W, H)
    s += text(W / 2, 34, "Лічильник: ланцюг toggle-тригерів рахує імпульси у двійковій", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "кожен наступний тригер ділить ще навпіл, тож разом вони лічать 000, 001, 010, … як двійкове число",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 150, 840
    edges = [180, 270, 360, 450, 540, 630, 720, 810]
    s += wave(gx0, gx1, 100, _clk_pulses(edges, 35), INK, "такт", amp=12)
    for e in edges:
        s += line(e, 90, e, 350, GREY, 0.8, "3 3")
    q0 = [(180, 1), (270, 0), (360, 1), (450, 0), (540, 1), (630, 0), (720, 1), (810, 0)]
    q1 = [(270, 1), (450, 0), (630, 1), (810, 0)]
    q2 = [(450, 1), (810, 0)]
    s += wave(gx0, gx1, 165, q0, GREEN, "Q0 (÷2)", amp=11)
    s += wave(gx0, gx1, 225, q1, GREEN, "Q1 (÷4)", amp=11)
    s += wave(gx0, gx1, 285, q2, GREEN, "Q2 (÷8)", amp=11)
    # двійковий рахунок під фронтами
    counts = ["001", "010", "011", "100", "101", "110", "111", "000"]
    for i, e in enumerate(edges):
        s += text(e, 340, counts[i], 10, RED, "middle", "bold")
    s += text(150, 340, "→", 11, GREY, "start")
    s += rect(70, 360, W - 140, 60, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 384, "Q2 Q1 Q0 разом — це двійкове число, що зростає на 1 щотакту: 0→1→2→…→7→0.", 12, INK, "middle", "bold")
    s += text(W / 2, 406, "Молодший біт Q0 ділить такт на 2, Q1 — на 4, Q2 — на 8: біт n = такт / 2ⁿ⁺¹.", 11.5, GREY, "middle", style="italic")
    save("fig-16-7-2-ripple.svg", s)


# ── Рис. 16.7.3 — ділення частоти: швидкий такт → повільний ────────────────
def fig167_divide():
    W, H = 860, 360
    s = header(W, H)
    s += text(W / 2, 34, "Ділення частоти: з одного швидкого такту — будь-який повільніший", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "N-бітний лічильник на старшому біті дає такт / 2ᴺ — так роблять повільні ритми з кварцового такту",
              12, GREY, "middle", style="italic")
    # драбинка ділень
    rows = [("Q0", "такт / 2"), ("Q1", "такт / 4"), ("Q2", "такт / 8"),
            ("Q9", "такт / 1024"), ("Q23", "такт / ≈16 млн")]
    for i, (b, d) in enumerate(rows):
        y = 110 + i * 36
        s += text(150, y, b, 12, GREEN, "end", "bold")
        s += text(175, y, "=", 12, GREY, "start")
        s += text(200, y, d, 12, INK, "start", "bold")
    s += text(150, 110 + 5 * 36, "(що старший біт — то повільніший)", 10.5, GREY, "end", style="italic")
    s += rect(470, 100, 360, 200, "#f4f7f4", GREEN, 1.6, 10)
    s += text(650, 126, "Приклад: блимати світлодіодом 1 раз/с", 11.5, INK, "middle", "bold")
    s += text(490, 156, "кварц 16 МГц = 16 000 000 тактів/с", 11, INK, "start")
    s += text(490, 180, "ділимо на 2²⁴ ≈ 16.8 млн →", 11, INK, "start")
    s += text(490, 204, "≈ 1 Гц на старшому біті лічильника", 11, GREEN, "start", "bold")
    s += text(490, 234, "Так само роблять секунди годинника,", 10.5, GREY, "start", style="italic")
    s += text(490, 250, "періоди таймерів, частоти звуку.", 10.5, GREY, "start", style="italic")
    s += text(490, 276, "Серце апаратних таймерів (Розділ 24).", 10.5, "#9a7322", "start", "bold")
    s += text(W / 2, 334, "Лічильник — це і годинник, і подільник частоти: рахуючи такти, він відмірює час.", 12, INK, "middle", "bold")
    save("fig-16-7-3-divide.svg", s)


# ── Рис. 16.7.4 — ланцюговий vs синхронний ─────────────────────────────────
def fig167_ripple_vs_sync():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Ланцюговий проти синхронного: де перенос «біжить», а де ні", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "у ланцюговому кожен тригер чекає попередній (затримка накопичується); у синхронному всі по одному такту",
              12, GREY, "middle", style="italic")
    # ланцюговий
    s += rect(50, 90, 390, 250, "none", AMBER, 1.6, 10)
    s += text(245, 114, "Ланцюговий (ripple)", 12.5, "#9a7322", "middle", "bold")
    for i in range(3):
        x = 90 + i * 110
        s += rect(x, 150, 70, 50, "#fafafa", INK, 1.6, 5)
        s += text(x + 35, 180, f"T{i}", 11, INK, "middle", "bold")
        s += _clk(x, 192)
        if i < 2:
            s += arrow(x + 70, 175, x + 110, 192, INK, 1.6)
    s += _pin(50, 175, 90, 175)
    s += text(46, 179, "такт", 9.5, INK, "end")
    s += text(245, 240, "такт → T0 → T1 → T2", 10.5, INK, "middle", "bold")
    s += text(245, 262, "перенос «біжить» (як суматор §15.6)", 10, GREY, "middle", style="italic")
    s += text(245, 282, "просто, та старший біт відстає", 10.5, RED, "middle", "bold")
    s += text(245, 300, "на суму затримок → можливі глітчі", 10, GREY, "middle", style="italic")
    # синхронний
    s += rect(460, 90, 380, 250, "none", GREEN, 1.6, 10)
    s += text(650, 114, "Синхронний", 12.5, GREEN, "middle", "bold")
    for i in range(3):
        x = 500 + i * 100
        s += rect(x, 150, 64, 50, "#fafafa", INK, 1.6, 5)
        s += text(x + 32, 180, f"T{i}", 11, INK, "middle", "bold")
        s += _clk(x, 192)
    s += line(480, 225, 800, 225, RED, 1.8)
    for i in range(3):
        x = 500 + i * 100
        s += line(x + 5, 200, x + 5, 225, RED, 1.2)
        s += circle(x + 5, 225, 2.5, RED, RED, 1)
    s += text(470, 229, "такт", 9.5, RED, "end", "bold")
    s += text(650, 252, "усі тригери — по СПІЛЬНОМУ такту", 10.5, INK, "middle", "bold")
    s += text(650, 272, "логіка вирішує, кому перемкнутись", 10, GREY, "middle", style="italic")
    s += text(650, 292, "складніше, зате швидко й без глітчів", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, 364, "Ланцюговий — для невибагливого; синхронний — там, де треба швидкість і чистота (як у процесорі).",
              11.5, INK, "middle", "bold")
    save("fig-16-7-4-ripple-vs-sync.svg", s)


# ── Рис. 16.7.5 — лічильник за модулем і застосування ──────────────────────
def fig167_uses():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Лічильник за модулем і навіщо лічильники взагалі", 20.5, INK, "middle", "bold")
    s += text(W / 2, 56, "змусивши лічильник скидатись на числі N, дістаємо рахунок 0…N−1; а лічити — це те, чого логіка без пам'яті не вміла",
              11.5, GREY, "middle", style="italic")
    # mod-N
    s += rect(60, 90, 360, 130, "none", INK, 1.6, 10)
    s += text(240, 114, "Лічильник за модулем N", 12.5, INK, "middle", "bold")
    s += text(80, 142, "рахує 0, 1, 2, …, N−1, тоді знову 0", 11, INK, "start")
    s += text(80, 166, "(детектор «дійшли до N» скидає його)", 10.5, GREY, "start", style="italic")
    s += text(80, 194, "напр. mod-10 → десяткова цифра 0…9", 11, RED, "start", "bold")
    # кругова стрілка
    s += text(240, 244, "0→1→2→…→9→0→…", 12, GREEN, "middle", "bold")
    # застосування
    s += rect(460, 90, 380, 220, "#f4f7f4", GREEN, 1.6, 10)
    s += text(650, 116, "Де лічильники працюють:", 12.5, INK, "middle", "bold")
    for i, t in enumerate([
        "• ПОДІЛ ЧАСТОТИ й відлік ЧАСУ",
        "  (таймери, годинник — §24)",
        "• ЛІЧБА ПОДІЙ: «скільки імпульсів",
        "  прийшло» — те, чого комбінаційна",
        "  логіка не вміла (§15.7, §16.1)!",
        "• ЛІЧИЛЬНИК КОМАНД (PC): крокує",
        "  адресами програми (§18.2)"]):
        s += text(476, 144 + i * 22, t, 11, INK, "start")
    s += text(W / 2, 350, "Ось і відповідь на питання з §16.1: «скільки разів натиснули?» — рахує лічильник.", 12, INK, "middle", "bold")
    save("fig-16-7-5-uses.svg", s)


# ═══════════════════ §16.8 — Метастабільність і таймінг ═════════════════════
# ── Рис. 16.8.1 — вікно setup/hold ─────────────────────────────────────────
def fig168_setup_hold():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 34, "Setup / hold: дані мусять «застигнути» довкола фронту такту", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "трохи ПЕРЕД фронтом (setup) і трохи ПІСЛЯ (hold) вхід D має не змінюватися — інакше тригер не «вловить» чисто",
              11.5, GREY, "middle", style="italic")
    gx0, gx1 = 110, 820
    edge = 440
    # такт
    s += wave(gx0, gx1, 120, [(edge, 1), (edge + 120, 0)], INK, "такт", amp=16)
    s += line(edge, 100, edge, 300, RED, 1.4, "3 3")
    s += text(edge, 94, "▲ фронт", 10, RED, "middle", "bold")
    # вікно
    tsu, th = 70, 35
    s += rect(edge - tsu, 180, tsu + th, 90, "#fff3e0", AMBER, 1.4)
    s += line(edge - tsu, 175, edge - tsu, 280, AMBER, 1, "2 3")
    s += line(edge + th, 175, edge + th, 280, AMBER, 1, "2 3")
    s += text(edge - tsu / 2, 300, "setup", 10.5, "#9a7322", "middle", "bold")
    s += text(edge + th / 2, 300, "hold", 10.5, "#9a7322", "middle", "bold")
    s += text(edge - 5, 172, "← D має бути стабільним →", 10, "#9a7322", "middle", "bold")
    # D — змінюється завчасно, у вікні стабільний
    s += wave(gx0, gx1, 225, [(300, 1)], GREEN, "D", amp=16)
    s += text(250, 250, "D змінився ЗАВЧАСНО", 10, GREEN, "middle", "bold")
    s += text(620, 218, "у вікні D стабільний → захоплено чисто ✓", 11, GREEN, "start", "bold")
    s += text(W / 2, 336, "Якщо ж D зміниться САМЕ у вікні (на фронті) — тригер може «зависнути»: це метастабільність (Рис. 16.8.2).",
              11.5, INK, "middle", "bold")
    save("fig-16-8-1-setup-hold.svg", s)


# ── Рис. 16.8.2 — метастабільність ─────────────────────────────────────────
def fig168_metastable():
    W, H = 880, 380
    s = header(W, H)
    s += text(W / 2, 34, "Метастабільність: тригер «завис» між 0 і 1", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "коли D змінюється рівно на фронті, вихід може зупинитися посередині й розв'язатися через НЕПЕРЕДБАЧУВАНИЙ час",
              11.5, GREY, "middle", style="italic")
    gx0, gx1 = 110, 640
    edge = 240
    s += wave(gx0, gx1, 110, [(edge, 1), (edge + 80, 0)], INK, "такт", amp=13)
    s += line(edge, 98, edge, 300, RED, 1.2, "3 3")
    s += text(edge, 92, "▲ (D змінився саме тут)", 9.5, RED, "middle", "bold")
    # Q: зависає на середині, тоді розв'язується
    hi, lo, mid = 175, 245, 210
    s += text(95, 214, "Q", 13, GREEN, "end", "bold")
    s += line(gx0, lo, gx1, lo, FAINT, 1)
    s += line(gx0, hi, gx1, hi, FAINT, 1)
    meta = [(gx0, lo), (edge, lo), (edge + 15, mid + 3), (edge + 60, mid - 2), (edge + 110, mid + 4),
            (edge + 160, mid - 3), (edge + 210, mid), (edge + 250, mid - 6), (edge + 290, lo + 6), (gx1, lo)]
    s += polyline(meta, AMBER, 2.6)
    s += text(edge + 130, mid - 14, "«завис» — ні 0, ні 1", 10.5, RED, "middle", "bold")
    s += text(edge + 300, lo - 8, "нарешті впав", 10, GREY, "start", style="italic")
    s += text(edge + 150, 280, "час розв'язання — ВИПАДКОВИЙ", 11, RED, "middle", "bold")
    # метафора: кулька на горбі
    s += rect(680, 90, 170, 210, "none", FAINT, 1.5, 10)
    s += text(765, 114, "Як кулька на горбі", 11, INK, "middle", "bold")
    s += f'<path d="M 700,250 Q 765,150 830,250" fill="none" stroke="{INK}" stroke-width="2"/>\n'
    s += circle(765, 145, 9, "#fbf3e0", AMBER, 2)
    s += text(765, 180, "?", 12, RED, "middle", "bold")
    s += text(765, 272, "балансує, тоді падає", 10, GREY, "middle")
    s += text(765, 288, "ліворуч чи праворуч —", 9.5, GREY, "middle")
    s += text(W / 2, 360, "Це той самий «горб» бістабільності з §16.0: рівновага хитка, і коли саме та куди впаде — наперед не знати.",
              11, INK, "middle", "bold")
    save("fig-16-8-2-metastable.svg", s)


# ── Рис. 16.8.3 — усередині синхронного домену безпечно ────────────────────
def fig168_sync_safe():
    W, H = 860, 340
    s = header(W, H)
    s += text(W / 2, 34, "Чому всередині синхронної схеми метастабільності НЕ буває", 19.5, INK, "middle", "bold")
    s += text(W / 2, 56, "таймінг-дисципліна (§16.6) гарантує: логіка встигає порахувати й D «застигає» задовго до фронту",
              12, GREY, "middle", style="italic")
    gx0, gx1 = 120, 820
    e1, e2 = 200, 700
    s += wave(gx0, gx1, 110, [(e1, 1), (e1 + 60, 0), (e2, 1), (e2 + 60, 0)], INK, "такт", amp=13)
    s += line(e1, 98, e1, 250, RED, 1, "3 3")
    s += line(e2, 98, e2, 250, RED, 1, "3 3")
    s += text(e1, 92, "▲", 9, RED, "middle")
    s += text(e2, 92, "▲", 9, RED, "middle")
    s += line(e1, 150, e2, 150, RED, 1.4)
    s += text((e1 + e2) / 2, 144, "період", 10.5, RED, "middle", "bold")
    # D: рахується після e1, застигає задовго до e2
    s += text(95, 214, "D", 13, INK, "end", "bold")
    s += polyline([(gx0, 230), (e1, 230), (e1 + 30, 230), (e1 + 120, 185), (e2 - 120, 185), (e2, 185), (gx1, 185)], GREEN, 2.4)
    s += rect(e2 - 70, 165, 105, 90, "#eafaef", GREEN, 1.2)
    s += text(e2 - 17, 270, "стабільно (setup ок)", 10, GREEN, "middle", "bold")
    s += text(e1 + 120, 178, "логіка порахувала…", 10, GREY, "start", style="italic")
    s += text(W / 2, 314, "Період підібрано так, що D устоюється раніше за вікно наступного фронту → захоплення завжди чисте.",
              11.5, INK, "middle", "bold")
    save("fig-16-8-3-sync-safe.svg", s)


# ── Рис. 16.8.4 — небезпека на межі: асинхронний вхід ──────────────────────
def fig168_boundary():
    W, H = 860, 350
    s = header(W, H)
    s += text(W / 2, 34, "Небезпека на МЕЖІ: асинхронний сигнал може змінитись будь-коли", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "кнопка чи сигнал з іншого такту не знають про наш фронт — і можуть змінитись саме у вікні setup/hold",
              11.5, GREY, "middle", style="italic")
    gx0, gx1 = 120, 820
    edges = [240, 440, 640]
    s += wave(gx0, gx1, 110, _clk_pulses(edges, 60), INK, "наш такт", amp=13)
    for e in edges:
        s += rect(e - 25, 98, 50, 14, "#fff3e0", "none", 0)
        s += text(e, 92, "▲", 9, RED, "middle")
    # асинхронний вхід — змінюється де завгодно, зокрема просто на фронті
    s += wave(gx0, gx1, 210, [(300, 1), (438, 0), (600, 1)], BLUE, "кнопка (асинхр.)", amp=13)
    s += line(438, 195, 438, 130, RED, 1.4, "3 3")
    s += text(438, 250, "змінилась МАЙЖЕ на фронті!", 10.5, RED, "middle", "bold")
    s += text(438, 268, "→ ризик метастабільності", 10, RED, "middle", "bold")
    s += text(W / 2, 326, "Зовнішні, незалежні сигнали — головне джерело метастабільності. Заводити їх «напряму» в логіку не можна.",
              11.5, INK, "middle", "bold")
    save("fig-16-8-4-boundary.svg", s)


# ── Рис. 16.8.5 — синхронізатор із двох тригерів ───────────────────────────
def fig168_synchronizer():
    W, H = 880, 360
    s = header(W, H)
    s += text(W / 2, 34, "Ліки — синхронізатор: два тригери поспіль", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "перший може «зависнути», та має цілий період, щоб розв'язатися, перш ніж другий його зчитає — і той бере чисте",
              11.5, GREY, "middle", style="italic")
    s += text(85, 165, "асинхр.", 11, BLUE, "end", "bold")
    s += text(85, 181, "вхід", 11, BLUE, "end", "bold")
    s += _pin(90, 175, 150, 175)
    s += _dff_symbol(150, 130, 95, 100)
    s += text(197, 120, "тригер 1", 10.5, INK, "middle", "bold")
    s += _pin(245, 162, 320, 162)
    s += text(282, 154, "може «дзвеніти»", 9, AMBER, "middle")
    s += _dff_symbol(320, 130, 95, 100)
    s += text(367, 120, "тригер 2", 10.5, INK, "middle", "bold")
    s += _pin(415, 162, 490, 162)
    s += text(496, 166, "чистий 0/1", 12, GREEN, "start", "bold")
    # спільний такт
    s += line(120, 300, 480, 300, RED, 2)
    s += text(114, 304, "такт", 11, RED, "end", "bold")
    for x in (160, 330):
        s += line(x, 218, x, 300, RED, 1.4)
        s += circle(x, 300, 2.5, RED, RED, 1)
    s += rect(560, 100, 290, 200, "#f4f7f4", GREEN, 1.6, 10)
    s += text(705, 126, "Як це працює:", 12.5, INK, "middle", "bold")
    for i, t in enumerate([
        "• тригер 1 ловить асинхронний вхід",
        "  і ІНКОЛИ зависає (метастабільно)",
        "• та за цілий період він майже",
        "  напевно розв'язується в 0 чи 1",
        "• тригер 2 зчитує його вже чистим",
        "• метастабільність не зникає зовсім —",
        "  лише стає НЕЙМОВІРНО рідкісною (MTBF)"]):
        s += text(576, 152 + i * 21, t, 10.6, INK, "start")
    save("fig-16-8-5-synchronizer.svg", s)


# ═══════════════════════ §16.9 — Скінченні автомати (Мур / Мілі) ════════════
def _state(cx, cy, r, label, sub=None, fill="#eef4ff", stroke=INK, accent=False):
    """Стан-кружок діаграми станів. accent — подвійне кільце (поточний/початковий)."""
    out = circle(cx, cy, r, fill, stroke, 2.4 if not accent else 2.8)
    if accent:
        out += circle(cx, cy, r - 5, "none", stroke, 1.6)
    out += text(cx, cy + (4 if not sub else -3), label, 13, INK, "middle", "bold")
    if sub:
        out += text(cx, cy + 14, sub, 10, GREY, "middle")
    return out


def _arc(x1, y1, x2, y2, bend=0.0, color=INK, w=2.0, dash=None):
    """Дуга-перехід зі стрілкою. bend — кривина (±)."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    cx, cy = mx + nx * bend, my + ny * bend
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<path d="M {x1:.1f},{y1:.1f} Q {cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def _self_loop(cx, cy, r, color=INK, w=1.8, side="top"):
    """Петля «лишитись у стані» над/під кружком."""
    if side == "top":
        x1, y1 = cx - 12, cy - r
        x2, y2 = cx + 12, cy - r
        cpy = cy - r - 40
    else:
        x1, y1 = cx - 12, cy + r
        x2, y2 = cx + 12, cy + r
        cpy = cy + r + 40
    m = _MARK.get(color, "aInk")
    return (f'<path d="M {x1:.1f},{y1:.1f} C {x1-14:.1f},{cpy:.1f} {x2+14:.1f},{cpy:.1f} {x2:.1f},{y2:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" marker-end="url(#{m})"/>\n')


# ── Рис. 16.9.1 — від лічильника до автомата ───────────────────────────────
def fig169_counter_to_fsm():
    W, H = 880, 430
    s = header(W, H)
    s += text(W / 2, 34, "Узагальнення: лічильник — це автомат, у якого наступний стан завжди «+1»", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "відв'яжемо перехід від жорсткого «+1» — і той самий апарат (регістр стану) почне ходити будь-яким маршрутом",
              11.5, GREY, "middle", style="italic")
    # ЛІВО: лічильник — кільце 0→1→2→3→0
    s += rect(40, 84, 380, 300, "none", FAINT, 1.5, 10)
    s += text(230, 110, "Лічильник: маршрут зашитий («+1»)", 12.5, INK, "middle", "bold")
    cyc = [(150, 180, "0"), (310, 180, "1"), (310, 320, "2"), (150, 320, "3")]
    for (cx, cy, lab) in cyc:
        s += _state(cx, cy, 24, lab, fill="#eef4ff")
    s += _arc(174, 180, 286, 180, 0, INK, 1.8)
    s += _arc(310, 204, 310, 296, 0, INK, 1.8)
    s += _arc(286, 320, 174, 320, 0, INK, 1.8)
    s += _arc(150, 296, 150, 204, 0, INK, 1.8)
    s += text(230, 168, "+1", 10.5, GREY, "middle")
    s += text(230, 344, "+1", 10.5, GREY, "middle")
    s += text(230, 372, "стан іде по колу, завжди однаково", 10.5, GREY, "middle", style="italic")
    # ПРАВО: автомат — той самий регістр, але переходи залежать від ВХОДУ
    s += rect(460, 84, 380, 300, "none", FAINT, 1.5, 10)
    s += text(650, 110, "Автомат: наступний стан = f(стан, ВХІД)", 12, INK, "middle", "bold")
    st = [(560, 180, "A"), (740, 180, "B"), (650, 330, "C")]
    for (cx, cy, lab) in st:
        s += _state(cx, cy, 24, lab, fill="#eef7ee", stroke=GREEN)
    s += _arc(584, 180, 716, 180, 0, GREEN, 1.8)
    s += text(650, 168, "вхід=1", 10, INK, "middle", "bold")
    s += _arc(730, 204, 668, 308, 30, GREEN, 1.8)
    s += _arc(632, 308, 572, 204, 30, GREEN, 1.8)
    s += _self_loop(560, 180, 24, GREY, 1.6, "top")
    s += text(560, 128, "вхід=0", 9.5, GREY, "middle")
    s += text(650, 372, "маршрут обирає вхід — це вже КЕРУВАННЯ", 10.5, GREEN, "middle", "bold")
    s += text(W / 2, 410, "Та сама пам'ять стану (§16.7) + інша логіка переходу = з «лічби» виходить машина, що приймає рішення.",
              11.5, INK, "middle", "bold")
    save("fig-16-9-1-counter-to-fsm.svg", s)


# ── Рис. 16.9.2 — діаграма станів контролера протоколу ─────────────────────
def fig169_state_diagram():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Діаграма станів: контролер приймача послідовного байта", 20, INK, "middle", "bold")
    s += text(W / 2, 56, "кружок = стан, стрілка = перехід (підпис «умова входу»); машина «йде» діаграмою такт за тактом",
              12, GREY, "middle", style="italic")
    # стартова стрілка
    s += arrow(70, 150, 110, 150, INK, 2)
    s += text(70, 138, "старт", 10, GREY, "start")
    IDLE = (170, 150); START = (380, 150); DATA = (590, 150); STOP = (760, 300)
    s += _state(*IDLE, 40, "IDLE", "чекає", fill="#eef4ff", accent=True)
    s += _state(*START, 40, "START", "старт-біт", fill="#eef7ee", stroke=GREEN)
    s += _state(*DATA, 40, "DATA", "8 бітів", fill="#eef7ee", stroke=GREEN)
    s += _state(*STOP, 40, "STOP", "стоп-біт", fill="#fbf6ec", stroke=AMBER)
    # переходи
    s += _arc(IDLE[0] + 40, 150, START[0] - 40, 150, 0, INK, 2)
    s += text((IDLE[0] + START[0]) / 2, 138, "лінія впала (0)", 10, INK, "middle", "bold")
    s += _self_loop(IDLE[0], IDLE[1], 40, GREY, 1.6, "top")
    s += text(IDLE[0], 92, "лінія=1 (тиша)", 9.5, GREY, "middle")
    s += _arc(START[0] + 40, 150, DATA[0] - 40, 150, 0, INK, 2)
    s += text((START[0] + DATA[0]) / 2, 138, "пів-біта минуло", 10, INK, "middle", "bold")
    s += _self_loop(DATA[0], DATA[1], 40, GREY, 1.6, "top")
    s += text(DATA[0], 92, "лічу біти < 8", 9.5, GREY, "middle")
    s += _arc(DATA[0] + 20, 188, STOP[0] - 20, STOP[1] - 30, 30, INK, 2)
    s += text(720, 215, "8 бітів зібрано", 10, INK, "middle", "bold")
    s += _arc(STOP[0] - 30, STOP[1] - 20, IDLE[0] + 18, IDLE[1] + 36, -120, BLUE, 2)
    s += text(420, 380, "стоп-біт перевірено → готово, у IDLE", 10.5, BLUE, "middle", "bold")
    # легенда
    s += rect(60, 410, W - 120, 48, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 432, "Кожен такт машина дивиться на вхід (рівень лінії, лічильник бітів) і вирішує: лишитись чи перейти.",
              12, INK, "middle", "bold")
    s += text(W / 2, 450, "Це той самий приймач, що в §16.5 «складав» байт зсувним регістром, — тепер ним КЕРУЄ автомат.",
              11, GREY, "middle", style="italic")
    save("fig-16-9-2-state-diagram.svg", s)


# ── Рис. 16.9.3 — Мур проти Мілі ───────────────────────────────────────────
def fig169_moore_mealy():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Дві школи: вихід на СТАНІ (Мур) проти виходу на ПЕРЕХОДІ (Мілі)", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "Мур: вихід пишемо в кружку (залежить лише від стану). Мілі: вихід пишемо на стрілці (стан + вхід)",
              11.5, GREY, "middle", style="italic")
    # ЛІВО: Мур
    s += rect(40, 84, 410, 250, "none", FAINT, 1.5, 10)
    s += text(245, 110, "Автомат МУРА: вихід = f(стан)", 12.5, INK, "middle", "bold")
    s += _state(150, 200, 42, "S0", "вих=0", fill="#eef4ff", accent=True)
    s += _state(340, 200, 42, "S1", "вих=1", fill="#eef7ee", stroke=GREEN)
    s += _arc(192, 200, 298, 200, 0, INK, 2)
    s += text(245, 188, "вх=1", 10, INK, "middle", "bold")
    s += _arc(298, 222, 192, 222, -34, INK, 2)
    s += text(245, 270, "вх=0", 10, INK, "middle", "bold")
    s += text(245, 320, "вихід «приписаний» стану, тримається весь такт", 10, GREY, "middle", style="italic")
    # ПРАВО: Мілі
    s += rect(460, 84, 400, 250, "none", FAINT, 1.5, 10)
    s += text(660, 110, "Автомат МІЛІ: вихід = f(стан, вхід)", 12.5, INK, "middle", "bold")
    s += _state(560, 200, 42, "T0", fill="#eef4ff", accent=True)
    s += _state(760, 200, 42, "T1", fill="#eef7ee", stroke=GREEN)
    s += _arc(602, 200, 718, 200, 0, GREEN, 2)
    s += text(660, 182, "вх=1 / вих=1", 10, GREEN, "middle", "bold")
    s += _arc(718, 222, 602, 222, -34, INK, 2)
    s += text(660, 270, "вх=0 / вих=0", 10, INK, "middle", "bold")
    s += text(660, 320, "вихід «висить» на переході — реагує того ж такту", 10, GREY, "middle", style="italic")
    # порівняння внизу
    s += rect(60, 350, W - 120, 108, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 374, "Той самий обов'язок — різний почерк:", 12.5, INK, "middle", "bold")
    rows = [
        ("Мур", "вихід залежить лише від стану", "на такт ПІЗНІШЕ, зате стабільний і легше таймити", BLUE),
        ("Мілі", "вихід залежить і від входу", "реагує ОДРАЗУ, та може «мигати» разом із входом", AMBER),
    ]
    for i, (nm, a, b, col) in enumerate(rows):
        yy = 402 + i * 26
        s += text(96, yy, nm + ":", 12, col, "start", "bold")
        s += text(160, yy, a, 11, INK, "start")
        s += text(470, yy, "→ " + b, 11, GREY, "start")
    save("fig-16-9-3-moore-mealy.svg", s)


# ── Рис. 16.9.4 — канонічна реалізація автомата ────────────────────────────
def fig169_implementation():
    W, H = 880, 420
    s = header(W, H)
    s += text(W / 2, 34, "Як його будують: регістр стану + логіка переходу + логіка виходу", 19, INK, "middle", "bold")
    s += text(W / 2, 56, "це знайома модель §16.1 у конкретній формі; повний код-приклад — окремо (⚙️ далі), тут лише кістяк",
              11.5, GREY, "middle", style="italic")
    # входи
    s += _pin(70, 150, 150, 150)
    s += text(64, 154, "входи", 12, INK, "end", "bold")
    # логіка наступного стану
    s += rect(150, 110, 170, 90, "#eef4ff", INK, 2, 10)
    s += text(235, 148, "логіка", 12, INK, "middle", "bold")
    s += text(235, 166, "наступного стану", 11, INK, "middle", "bold")
    s += text(235, 184, "(комбінаційна)", 9.5, GREY, "middle")
    s += arrow(320, 150, 400, 150, INK, 2)
    s += text(360, 140, "наст. стан", 9.5, GREY, "middle")
    # регістр стану
    s += rect(400, 110, 150, 90, "#eef7ee", GREEN, 2.2, 10)
    s += text(475, 144, "РЕГІСТР", 12.5, INK, "middle", "bold")
    s += text(475, 162, "стану", 12.5, INK, "middle", "bold")
    s += _clk(400, 188)
    s += text(414, 192, "такт", 9.5, INK, "start")
    s += arrow(550, 150, 640, 150, GREEN, 2.2)
    s += text(595, 140, "поточ. стан", 9.5, GREEN, "middle")
    # логіка виходу
    s += rect(640, 110, 150, 90, "#fbf6ec", AMBER, 2, 10)
    s += text(715, 148, "логіка", 12, INK, "middle", "bold")
    s += text(715, 166, "виходу", 12, INK, "middle", "bold")
    s += _pin(790, 150, 850, 150)
    s += text(852, 154, "виходи", 12, GREEN, "start", "bold")
    # зворотний зв'язок: поточний стан → логіка наступного стану
    s += circle(600, 150, 3, INK, INK, 1)
    s += line(600, 150, 600, 260, INK, 1.6)
    s += line(600, 260, 235, 260, INK, 1.6)
    s += line(235, 260, 235, 200, INK, 1.6)
    s += arrow(235, 240, 235, 200, INK, 1.6)
    s += text(417, 252, "поточний стан вертається в логіку переходу", 10, GREY, "middle", style="italic")
    # пунктир для Мілі: вхід також у логіку виходу
    s += line(110, 150, 110, 330, BLUE, 1.4, "4 3")
    s += line(110, 330, 715, 330, BLUE, 1.4, "4 3")
    s += line(715, 330, 715, 200, BLUE, 1.4, "4 3")
    s += arrow(715, 300, 715, 200, BLUE, 1.4)
    s += text(420, 322, "лише для МІЛІ: вхід заходить і в логіку виходу", 10, BLUE, "middle", "bold")
    s += rect(70, 356, W - 140, 50, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 380, "Регістр на фронті робить «наступний стан» поточним; уся машина крокує в ногу зі своїм тактом.",
              12, INK, "middle", "bold")
    s += text(W / 2, 398, "Логіка переходу й виходу — звичайні вентилі (Розділ 3.2); пам'ять — тригери (цей розділ).",
              11, GREY, "middle", style="italic")
    save("fig-16-9-4-implementation.svg", s)


if __name__ == "__main__":
    # історія розділу (§16.0)
    fig_timeline()
    fig_crosscoupled()
    fig_bistable()
    fig_tubes_to_gates()
    # §16.1
    fig161_no_memory()
    fig161_seq_model()
    fig161_odd_even()
    fig161_holds()
    fig161_volatile()
    # §16.2
    fig162_sr_nor()
    fig162_cases()
    fig162_forbidden()
    fig162_waveform()
    fig162_debounce()
    # §16.3
    fig163_gated()
    fig163_dlatch()
    fig163_master_slave()
    fig163_waveform()
    fig163_symbol()
    # §16.4
    fig164_level_vs_edge()
    fig164_racethrough()
    fig164_edge_solves()
    fig164_shift()
    fig164_rise_fall()
    # §16.5
    fig165_parallel()
    fig165_load_enable()
    fig165_shift()
    fig165_serial_parallel()
    fig165_processor()
    # §16.6
    fig166_clock()
    fig166_synchronous()
    fig166_generate()
    fig166_period_budget()
    fig166_skew()
    # §16.7
    fig167_toggle()
    fig167_ripple()
    fig167_divide()
    fig167_ripple_vs_sync()
    fig167_uses()
    # §16.8
    fig168_setup_hold()
    fig168_metastable()
    fig168_sync_safe()
    fig168_boundary()
    fig168_synchronizer()
    # §16.9
    fig169_counter_to_fsm()
    fig169_state_diagram()
    fig169_moore_mealy()
    fig169_implementation()
    print("ch16 figures done.")
