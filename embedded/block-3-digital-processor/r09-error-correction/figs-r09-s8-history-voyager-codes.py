# -*- coding: utf-8 -*-
"""
SVG-фігури для історичної вставки §3.9.8i — «Вояджери дзвонять додому».
Окремий генератор (головний figs.py не чіпаємо). Чистий Python, без залежностей.
Вивід → ./img/.  Імена: fig-r09-s8i-k-<slug>.svg.  Підписи у тексті: Рис. 3.9.8i.k.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif;
єдиний вигляд із рештою розділів (допоміжні функції — копія з figs-...-history-hdl.py).
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
        f'  <marker id="aGrey" markerWidth="11" markerHeight="11" refX="8" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREY}"/></marker>\n'
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


def _wrap(txt, width=26):
    words = txt.split()
    lines, cur = [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if len(t) > width:
            lines.append(cur); cur = wd
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


# ═══════════ Рис. 3.9.8i.1 — чому в космосі немає права на помилку ══════════
def fig_link_budget():
    """Сигнал від Вояджера приходить мізерно слабким, перепитати неможливо —
    тож виправляти помилки треба самому приймачу. Це і є мотивація каскаду."""
    W, H = 920, 470
    s = header(W, H)
    s += text(W / 2, 34, "Чому в далекому космосі немає права на «перепитай»", 21, INK, "middle", "bold")
    s += text(W / 2, 55, "сигнал приходить мізерним, а луна-запит ішов би роками — отже, приймач мусить лагодити дані сам",
              12, GREY, "middle", style="italic")

    # Сонце-Земля ліворуч, апарат праворуч; промінь, що блякне
    earth_x, earth_y = 110, 230
    probe_x = 800
    s += circle(earth_x, earth_y, 26, "#eef3fb", BLUE, 2.6)
    s += text(earth_x, earth_y + 5, "Земля", 12, BLUE, "middle", "bold")
    s += text(earth_x, earth_y + 50, "велика антена", 10.5, GREY, "middle")
    s += text(earth_x, earth_y + 64, "Deep Space Network", 10.5, GREY, "middle")

    # апарат
    s += rect(probe_x - 14, earth_y - 10, 28, 20, "#fff", INK, 2, 3)
    s += line(probe_x, earth_y - 10, probe_x, earth_y - 34, INK, 2)
    s += path(f"M{probe_x-22},{earth_y-34} Q{probe_x},{earth_y-54} {probe_x+22},{earth_y-34}", "none", INK, 2.4)
    s += text(probe_x, earth_y + 34, "апарат", 12, INK, "middle", "bold")
    s += text(probe_x, earth_y + 50, "передавач ~20 Вт", 10.5, GREY, "middle")
    s += text(probe_x, earth_y + 64, "(як лампочка в холодильнику)", 10, GREY, "middle")

    # промінь, що згасає: серія дуг дедалі блідіших
    for i in range(7):
        xx = earth_x + 40 + i * 95
        op = 1.0 - i * 0.13
        col = BLUE
        s += f'<path d="M{xx},{earth_y-46} A 46 46 0 0 1 {xx},{earth_y+46}" fill="none" stroke="{col}" stroke-width="2.4" opacity="{op:.2f}"/>\n'
    s += arrow(earth_x + 44, earth_y, probe_x - 60, earth_y, GREY, 1.6, dash="2 6")
    s += text(W / 2, earth_y - 70, "відстань — мільярди кілометрів", 12, GREY, "middle", style="italic")

    # три рамки внизу: три суворі факти
    facts = [
        ("Сигнал — слабший за подих", "До антени долітають крихти потужності: енергії в них менше, ніж у батарейці наручного годинника. На межі чутності кожен зайвий перевернутий біт коштує дорого.", RED),
        ("Перепитати — не варіант", "Радіохвиля долає шлях лише в один бік годинами. Запит «повтори пакет» вертався б туди-назад день і довше — жоден діалог із підтвердженням тут не працює.", AMBER),
        ("Тож лагодимо на місці", "Раз перепитати не можна, приймач мусить ВИПРАВИТИ помилку сам, із того, що прийшло. Саме для цього в потік навмисне домішують надлишок — корекційний код.", GREEN),
    ]
    bw, bx0, by = 286, 18, 312
    for i, (h, body, col) in enumerate(facts):
        x = bx0 + i * (bw + 6)
        s += rect(x, by, bw, 134, "#fff", col, 2.2, 10)
        s += rect(x, by, bw, 8, col, col, 0, 0)
        s += text(x + bw / 2, by + 30, h, 13.5, col, "middle", "bold")
        yy = by + 52
        for ln in _wrap(body, 40):
            s += text(x + 14, yy, ln, 11, INK, "start")
            yy += 15.5
    return save("fig-r09-s8i-1-link-budget.svg", s)


# ═══════════ Рис. 3.9.8i.2 — каскад: RS зовні, згортковий код усередині ═════
def fig_concatenation():
    """Серце теми: два коди в каскаді. Внутрішній згортковий + Вітербі гасить
    рідкий шум, але зриваючись — лишає БУРСТ. Зовнішній Рід–Соломон, що рахує
    символами, цей бурст замітає. Один код одного прикриває."""
    W, H = 940, 560
    s = header(W, H)
    s += text(W / 2, 32, "Каскад двох кодів: один прикриває слабке місце іншого", 21, INK, "middle", "bold")
    s += text(W / 2, 53, "так збудовано зв'язок Вояджерів — зовнішній Рід–Соломон + внутрішній згортковий код із декодером Вітербі",
              11.5, GREY, "middle", style="italic")

    # ── верхній ряд: КОДУВАННЯ на борту (зліва направо) ────────────────────
    y1 = 96
    s += text(30, y1 - 12, "НА БОРТУ — закутуємо дані у два шари захисту:", 12.5, INK, "start", "bold")
    s += rect(30, y1, 150, 52, "#fff", INK, 2, 8)
    s += text(105, y1 + 23, "дані знімків", 12.5, INK, "middle")
    s += text(105, y1 + 39, "і вимірів", 11, GREY, "middle")
    s += arrow(182, y1 + 26, 236, y1 + 26, INK, 2)

    s += rect(238, y1, 168, 52, "#fbeeec", RED, 2.4, 8)
    s += text(322, y1 + 21, "зовнішній код", 12.5, RED, "middle", "bold")
    s += text(322, y1 + 38, "Рід–Соломон RS(255,223)", 11, INK, "middle")
    s += arrow(408, y1 + 26, 462, y1 + 26, INK, 2)

    s += rect(464, y1, 168, 52, "#eef3fb", BLUE, 2.4, 8)
    s += text(548, y1 + 21, "внутрішній код", 12.5, BLUE, "middle", "bold")
    s += text(548, y1 + 38, "згортковий, R=1/2", 11, INK, "middle")
    s += arrow(634, y1 + 26, 688, y1 + 26, INK, 2)

    s += rect(690, y1, 96, 52, "#fff", INK, 2, 8)
    s += text(738, y1 + 23, "передавач", 11.5, INK, "middle")
    s += text(738, y1 + 39, "→ антена", 11, GREY, "middle")
    # хвилька в космос
    s += path(f"M788,{y1+26} q14,-16 28,0 q14,16 28,0 q14,-16 28,0", "none", GREY, 2)
    s += text(872, y1 + 30, "у", 11, GREY, "middle")
    s += text(872, y1 + 44, "космос", 10.5, GREY, "middle")

    # ── середина: КАНАЛ із шумом ───────────────────────────────────────────
    ymid = 196
    s += rect(30, ymid, W - 60, 60, "#fbf7ee", AMBER, 2, 10)
    s += text(48, ymid + 24, "КАНАЛ (мільярди км шуму):", 12.5, AMBER, "start", "bold")
    s += text(48, ymid + 44, "до сигналу домішуються поодинокі похибки — і зрідка цілі сплески перешкод",
              11.5, INK, "start")
    # символьна стрічка з рідким шумом + один бурст
    sx = 470
    for i in range(30):
        bad = i in (7, 18, 19, 20, 21)  # один поодинокий + один сплеск
        col = RED if bad else GREEN
        s += rect(sx + i * 14, ymid + 18, 11, 24, col, col, 0, 2)
    s += text(sx + 7 * 14 + 5, ymid + 14, "↑", 12, RED, "middle", "bold")
    s += text(sx + 19 * 14, ymid + 14, "сплеск", 10.5, RED, "middle", "bold")

    # ── нижній ряд: ДЕКОДУВАННЯ на Землі (справа наліво за змістом, але малюємо зліва) ─
    y3 = 300
    s += text(30, y3 - 12, "НА ЗЕМЛІ — знімаємо шари у зворотному порядку:", 12.5, INK, "start", "bold")
    s += rect(30, y3, 96, 52, "#fff", INK, 2, 8)
    s += text(78, y3 + 23, "приймач", 11.5, INK, "middle")
    s += text(78, y3 + 39, "DSN", 11, GREY, "middle")
    s += arrow(128, y3 + 26, 182, y3 + 26, INK, 2)

    s += rect(184, y3, 196, 52, "#eef3fb", BLUE, 2.4, 8)
    s += text(282, y3 + 20, "декодер Вітербі", 12.5, BLUE, "middle", "bold")
    s += text(282, y3 + 37, "гасить рідкий шум", 11, INK, "middle")
    s += arrow(382, y3 + 26, 436, y3 + 26, INK, 2)

    s += rect(438, y3, 210, 52, "#fbeeec", RED, 2.4, 8)
    s += text(543, y3 + 20, "декодер Рід–Соломона", 12, RED, "middle", "bold")
    s += text(543, y3 + 37, "замітає СПЛЕСКИ символів", 11, INK, "middle")
    s += arrow(650, y3 + 26, 704, y3 + 26, GREEN, 2.2)

    s += rect(706, y3, 150, 52, "#eafaee", GREEN, 2.6, 8)
    s += text(781, y3 + 22, "чисті дані", 12.5, GREEN, "middle", "bold")
    s += text(781, y3 + 38, "знімок без діри", 11, INK, "middle")

    # ── пояснювальний блок: чому саме так, а не один код ───────────────────
    yk = 384
    s += rect(30, yk, W - 60, 150, "#fff", INK, 1.6, 10)
    s += text(50, yk + 26, "У чому хитрість каскаду (concatenated code):", 13.5, INK, "start", "bold")
    s += text(50, yk + 50, "• Вітербі чудово витирає поодинокі похибки — але коли він таки помиляється, то зривається СЕРІЄЮ: лишає",
              11.5, INK, "start")
    s += text(64, yk + 68, "не один зіпсований біт, а щільний сплеск підряд. Для побітових кодів така злита діра — найгірший випадок.",
              11.5, INK, "start")
    s += text(50, yk + 92, "• Рід–Соломон рахує не біти, а СИМВОЛИ (байти). Цілий сплеск підряд псує лише кілька сусідніх символів —",
              11.5, RED, "start")
    s += text(64, yk + 110, "а виправити десяток зіпсованих символів йому однаково, лежать вони купкою чи врозсип. Сплеск його не лякає.",
              11.5, RED, "start")
    s += text(50, yk + 134, "Підсумок: внутрішній код прибирає дрібний шум, зовнішній — підчищає рідкі сплески за ним. Разом — глибокий захист.",
              12, GREEN, "start", "bold")
    return save("fig-r09-s8i-2-concatenation.svg", s)


# ═══════════ Рис. 3.9.8i.3 — чому символьний код тримає сплеск, а бітовий ні ═
def fig_burst():
    """Той самий сплеск помилок очима двох кодів. Зверху — код, що рахує
    бітами (як Геммінг, §3.9.6): сплеск перевищує його межу й валить блок.
    Знизу — Рід–Соломон: той самий сплеск займає лише кілька символів,
    і код спокійно їх відновлює. Це і є відповідь «чому CD/QR виживають»."""
    W, H = 920, 500
    s = header(W, H)
    s += text(W / 2, 32, "Один і той самий сплеск — очима двох кодів", 21, INK, "middle", "bold")
    s += text(W / 2, 53, "ось чому подряпаний диск ще грає, а заляпаний QR ще читається: сплеск псує мало СИМВОЛІВ, хай і багато бітів",
              11.5, GREY, "middle", style="italic")

    # спільна «подряпина» — діапазон зіпсованих бітів
    scratch_a, scratch_b = 8, 18  # індекси зіпсованих елементів

    # ── верхня панель: код, що рахує БІТАМИ ────────────────────────────────
    yT = 96
    s += text(40, yT - 8, "Код, що рахує БІТАМИ (як Геммінг (7,4), §3.9.6): сплеск перевищує його стелю",
              12.5, BLUE, "start", "bold")
    n = 32
    bx, bw = 70, 22
    for i in range(n):
        bad = scratch_a <= i <= scratch_b
        col = RED if bad else "#eef3fb"
        st = RED if bad else BLUE
        s += rect(bx + i * bw, yT + 14, bw - 4, 26, col, st, 1.6, 2)
    # дужка подряпини
    s += line(bx + scratch_a * bw, yT + 8, bx + (scratch_b + 1) * bw - 4, yT + 8, RED, 2)
    s += text(bx + (scratch_a + scratch_b) / 2 * bw + 8, yT + 2, "сплеск помилок", 11, RED, "middle", "bold")
    s += text(bx, yT + 64, "Цей код виправляє лише 1 перевернутий біт на блок. Сплеск перевертає їх", 11.5, INK, "start")
    s += text(bx, yT + 82, "купу поспіль — стеля давно пройдена.", 11.5, INK, "start")
    s += rect(bx + 540, yT + 50, 250, 40, "#fbeeec", RED, 2.2, 8)
    s += text(bx + 665, yT + 75, "БЛОК ВТРАЧЕНО — діра в даних", 12, RED, "middle", "bold")

    # ── нижня панель: Рід–Соломон, що рахує СИМВОЛАМИ ──────────────────────
    yB = 268
    s += text(40, yB - 8, "Рід–Соломон, що рахує СИМВОЛАМИ (байтами): той самий сплеск — лише кілька символів",
              12.5, RED, "start", "bold")
    # та сама стрічка, але згрупована по символах (по 4 біти на клітину для наочності)
    sym = 8           # символів
    per = 4           # «бітів» у символі (умовно, для картинки)
    sbx, sbw = 70, 96
    bad_syms = set()
    for i in range(scratch_a, scratch_b + 1):
        bad_syms.add(i // per)
    for k in range(sym):
        bad = k in bad_syms
        col = "#fbeeec" if bad else "#eafaee"
        st = RED if bad else GREEN
        s += rect(sbx + k * sbw, yB + 14, sbw - 8, 40, col, st, 2.2, 4)
        s += text(sbx + k * sbw + (sbw - 8) / 2, yB + 39, f"символ {k}", 11, st, "middle", "bold")
        # внутрішні біти
        for j in range(per):
            gi = k * per + j
            bb = scratch_a <= gi <= scratch_b
            cc = RED if bb else GREEN
            s += rect(sbx + k * sbw + 6 + j * ((sbw - 20) / per), yB + 58, (sbw - 24) / per, 7, cc, cc, 0, 1)
    s += text(sbx, yB + 92, "Сплеск ліг лише в кілька СУСІДНІХ символів. А Рід–Соломону байдуже, де саме лежать", 11.5, INK, "start")
    s += text(sbx, yB + 110, "зіпсовані символи: він виправляє їх до своєї межі (для RS(255,223) — аж 16 символів на блок),",
              11.5, INK, "start")
    s += text(sbx, yB + 128, "однаково — чи розкидані вони, чи злиплися в одну подряпину.", 11.5, INK, "start")
    s += rect(sbx + 540, yB + 96, 250, 40, "#eafaee", GREEN, 2.4, 8)
    s += text(sbx + 665, yB + 121, "СИМВОЛИ ВІДНОВЛЕНО — даних ціле", 11.5, GREEN, "middle", "bold")

    # підсумковий рядок-міст до CD/QR
    s += rect(40, 440, W - 80, 44, "#fff", INK, 1.6, 10)
    s += text(W / 2, 458, "Ось і вся таємниця: подряпина на CD чи пляма на QR — це сплеск, що псує БАГАТО бітів, але МАЛО символів.",
              12, INK, "middle")
    s += text(W / 2, 476, "Символьний код Рід–Соломона саме на сплески й розрахований — тому носій терпить ушкодження й читається далі.",
              12, GREEN, "middle", "bold")
    return save("fig-r09-s8i-3-burst.svg", s)


# ═══════════ Рис. 3.9.8i.4 — колективна атрибуція: код, декодер, каскад, політ
def fig_credit():
    """Чесна атрибуція без міфу про одинокого генія: математики дали КОД,
    інші — придатний ДЕКОДЕР (без нього код був мертвий), ще інші — ідею
    КАСКАДУ, і лише разом це полетіло на Вояджерах."""
    W, H = 940, 430
    s = header(W, H)
    s += text(W / 2, 32, "Чия заслуга: код, декодер, каскад і політ — чотири ланки, жодного одинокого генія", 18.5, INK, "middle", "bold")
    s += text(W / 2, 53, "сам код був безсилий без придатного декодера, а в космос його вивів ще й каскад — це праця кількох рук",
              11.5, GREY, "middle", style="italic")

    cols = [
        ("Рід і Соломон, 1960", "математики, Lincoln Lab",
         "5-сторінкова стаття «Polynomial Codes over Certain Finite Fields» дала сам КОД: лічити символами, а не бітами",
         RED),
        ("Берлекамп і Мессі, ~1969", "+ Пітерсон та інші",
         "придумали швидкий ДЕКОДЕР. Без нього код був гарною теорією, та надто важкою, щоб рахувати її на практиці",
         BLUE),
        ("Форні та теорія каскадів", "ідея concatenated code",
         "показали, як скласти два коди шарами, щоб зовнішній замітав сплески за внутрішнім — основа схеми Вояджера",
         AMBER),
        ("JPL і команди NASA", "інженери далекого космосу",
         "звели код, декодер і каскад у реальний радіозв'язок Вояджерів — і він працює досі, за межами Сонячної системи",
         GREEN),
    ]
    cw = 214
    gap = (W - 40 - cw * 4) / 3
    y = 86
    for i, (name, role, did, col) in enumerate(cols):
        x = 20 + i * (cw + gap)
        s += rect(x, y, cw, 268, "#fff", col, 2.4, 10)
        s += rect(x, y, cw, 8, col, col, 0, 0)
        hcx, hcy = x + cw / 2, y + 54
        if i in (0, 1):   # люди — портрет
            s += circle(hcx, hcy, 15, "#fff", col, 2.6)
            s += path(f"M{hcx-24},{hcy+40} Q{hcx},{hcy+12} {hcx+24},{hcy+40}", "none", col, 2.6)
        elif i == 2:      # ідея — схема двох прямокутників (каскад)
            s += rect(hcx - 26, hcy - 6, 22, 18, "#fff", col, 2.2, 2)
            s += rect(hcx + 4, hcy - 6, 22, 18, "#fff", col, 2.2, 2)
            s += arrow(hcx - 4, hcy + 3, hcx + 2, hcy + 3, col, 2)
        else:             # організація — антена
            s += line(hcx, hcy + 16, hcx, hcy - 8, col, 2.6)
            s += path(f"M{hcx-20},{hcy+16} Q{hcx},{hcy-22} {hcx+20},{hcy+16}", "none", col, 2.6)
        s += text(hcx, y + 116, name, 13, INK, "middle", "bold")
        yy = y + 138
        for ln in _wrap(role, 28):
            s += text(hcx, yy, ln, 10.5, GREY, "middle", style="italic")
            yy += 15
        yy += 4
        for ln in _wrap(did, 30):
            s += text(hcx, yy, ln, 10.5, col, "middle")
            yy += 15
        if i < 3:
            ax = x + cw + gap / 2
            s += arrow(ax - 11, y + 130, ax + 11, y + 130, INK, 2)
    s += text(W / 2, H - 10, "Код, декодер, каскад, політ — велике в техніці майже завжди збирається з внеску багатьох, а не одного імені",
              11.5, GREY, "middle", style="italic")
    return save("fig-r09-s8i-4-credit.svg", s)


if __name__ == "__main__":
    fig_link_budget()
    fig_concatenation()
    fig_burst()
    fig_credit()
    print("r09-s8 history (Voyager codes) figures done.")
