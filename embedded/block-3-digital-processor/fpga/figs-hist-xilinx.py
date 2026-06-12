# -*- coding: utf-8 -*-
"""
Генератор SVG-фігур для історичної вставки до Розділу 3.7 — «Програмована
логіка: ПЛІС/FPGA» (Модуль 3): Фріман, Вондершмітт і Барнетт засновують Xilinx.

ОКРЕМИЙ скрипт лише цієї вставки (головний figs.py розділу не чіпаємо).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.

Стиль (AUTHORING §9): білий фон; стрілки через marker; шрифт sans-serif.
Підписи історії до розділу — секція 0 (Рис. 3.7.0.k → файли fig-r07-0-k-*).
Допоміжні функції — копія спільних із рештою розділів, щоб вигляд був єдиний.
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


# ── проста «постать» (голова + плечі) для портретних карток ─────────────────
def _person(cx, cy, col):
    out = circle(cx, cy, 12, "#ffffff", col, 2.4)
    out += path(f"M{cx-18},{cy+30} Q{cx},{cy+10} {cx+18},{cy+30}", "none", col, 2.4)
    return out


# ═══════════ Рис. 3.7.0.1 — таймлайн: від ідеї до чипа-«чистої касети» ══════
def fig_timeline():
    W, H = 900, 712
    s = header(W, H)
    s += text(W / 2, 38, "Ланцюг до FPGA: чип, якому СХЕМУ завантажують, як програму", 21, INK, "middle", "bold")
    s += text(W / 2, 60, "від ідеї в Zilog, яку там не схотіли, до заснування Xilinx і першого «масиву логічних клітинок»",
              12.5, GREY, "middle", style="italic")
    spine = 250
    top, bot = 100, H - 26
    s += line(spine, top, spine, bot, GREY, 3)
    nodes = [
        ("до 1984", "ASIC — місяці чекання",
         "Замовну мікросхему проєктують і виготовляють МІСЯЦЯМИ; помилка в кремнії = нова дорога ітерація", False),
        ("поч. 1980-х", "ідея Фрімана в Zilog",
         "А якщо зробити чип, як ЧИСТУ КАСЕТУ — логіку в нього не «запікають», а ЗАВАНТАЖУЮТЬ за пів дня?", False),
        ("Zilog каже «ні»", "ринок надто малий",
         "Керівництво не схотіло вкладатися в новий клас чипів — і Фріман із колегами пішли робити це самі", False),
        ("лютий 1984", "засновано Xilinx",
         "Фріман + Вондершмітт + Барнетт; ~$4 млн венчурних грошей; ані власної фабрики, ані готового ринку", True),
        ("1 лист. 1985", "XC2064 — перша FPGA",
         "Світ побачив перший «Logic Cell Array»: ~64 логічні блоки, схему задають БІТСТРІМОМ при ввімкненні", False),
        ("1990", "вихід на біржу",
         "Xilinx на Nasdaq; «фаблес»-модель (чип без власного заводу) із дивацтва стає нормою галузі", False),
        ("донині", "FPGA усюди",
         "Осцилографи, SDR, відеотехніка, ретро-консолі, прискорювачі — і хобі-плати на вашому столі", False),
    ]
    n = len(nodes)
    for i, (yr, who, q, hl) in enumerate(nodes):
        y = top + 30 + (bot - top - 60) * i / (n - 1)
        if hl:
            s += circle(spine, y, 11, "#fff", RED, 0)
            s += circle(spine, y, 10, "none", RED, 3.2)
            s += circle(spine, y, 4.5, RED, RED, 1)
        else:
            s += circle(spine, y, 7, "#fff", INK, 2.6)
        s += text(spine - 22, y + 5, yr, 12.5, GREY, "end", "bold")
        s += text(spine + 26, y - 3, who, 15.5, (RED if hl else INK), "start", "bold")
        for j, ln in enumerate(_wrap(q, 60)):
            s += text(spine + 26, y + 18 + j * 17, ln, 12, INK, "start", style="italic")
    save("fig-r07-0-1-timeline.svg", s)


# ═══════════ Рис. 3.7.0.2 — троє засновників: різні ролі ════════════════════
def fig_founders():
    W, H = 900, 452
    s = header(W, H)
    s += text(W / 2, 34, "Троє засновників — три РІЗНІ ролі (а не «один геній»)", 21, INK, "middle", "bold")
    s += text(W / 2, 56, "винахід, гроші-управління й виробнича модель — окремі внески; компанію зробила саме їхня СПІЛКА",
              11.5, GREY, "middle", style="italic")
    cards = [
        ("Росс Фріман", "Ross Freeman", "ВИНАХІД",
         "Придумав саму FPGA: чип, у який схему ЗАВАНТАЖУЮТЬ. Фізик, мрійник; ставив на дешевшання транзисторів", RED),
        ("Джеймс Барнетт", "James V. Barnett II", "УПРАВЛІННЯ",
         "Інженер-управлінець; підняв компанію з нуля — перший очільник, гроші, команда, продукт (перевірити)", BLUE),
        ("Берні Вондершмітт", "Bernard Vonderschmitt", "МОДЕЛЬ",
         "34 роки в RCA; збудував «фаблес»-модель — чип без власного заводу — і знайшов фабрику-партнера", GREEN),
    ]
    cw, gap = 270, 22
    x0 = (W - (3 * cw + 2 * gap)) / 2
    for i, (name, eng, role, desc, col) in enumerate(cards):
        x = x0 + i * (cw + gap)
        hl = (col == RED)
        s += rect(x, 84, cw, 286, "#fdf4f4" if hl else "#fafafa", col, 2.2 if hl else 1.6, 12)
        s += _person(x + cw / 2, 124, col)
        s += text(x + cw / 2, 192, name, 15, INK, "middle", "bold")
        s += text(x + cw / 2, 211, eng, 11.5, GREY, "middle", style="italic")
        # роль-пігулка
        s += rect(x + cw / 2 - 62, 226, 124, 26, col, col, 0, 13)
        s += text(x + cw / 2, 244, role, 13, "#ffffff", "middle", "bold")
        for j, ln in enumerate(_wrap(desc, 32)):
            s += text(x + 18, 280 + j * 19, ln, 11.3, INK, "start")
    s += text(W / 2, 408, "«Придумати» ≠ «підняти компанію» ≠ «зробити так, щоб це взагалі можна було випускати». Усі три ролі — потрібні.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 432, "Усі троє прийшли з Zilog; FPGA винайшов Фріман, але БЕЗ решти двох винахід так і лишився б ідеєю в шухляді.",
              10.5, GREY, "middle", style="italic")
    save("fig-r07-0-2-founders.svg", s)


# ═══════════ Рис. 3.7.0.3 — головна ідея: «чиста касета» проти ASIC ═════════
def fig_blank_tape():
    W, H = 900, 470
    s = header(W, H)
    s += text(W / 2, 34, "Головна ідея Фрімана: чип — як ЧИСТА КАСЕТА, а не запечений у кремній", 18.5, INK, "middle", "bold")
    s += text(W / 2, 56, "замовний чип «запікають» місяцями; FPGA-«болванку» можна налаштувати під свою схему за пів дня — і переналаштувати знову",
              11.5, GREY, "middle", style="italic")
    # ── ліворуч: ASIC — запечена схема ──
    s += rect(60, 88, 360, 300, "#fdf6f6", RED, 1.8, 10)
    s += text(240, 114, "ASIC: схему ЗАПІКАЮТЬ у кремній", 13, RED, "middle", "bold")
    # чіп із намертво розведеними доріжками
    s += rect(110, 134, 260, 150, "#ffffff", INK, 1.6, 6)
    fixed = [(140, 164), (200, 164), (260, 164), (320, 164),
             (140, 224), (200, 224), (260, 224), (320, 224)]
    for (gx, gy) in fixed:
        s += rect(gx - 14, gy - 12, 28, 24, "#f1f1f1", GREY, 1.3, 3)
    # жорсткі (намертво) з'єднання
    wires = [((140, 164), (200, 224)), ((200, 164), (260, 164)),
             ((260, 164), (320, 224)), ((140, 224), (200, 224)),
             ((260, 224), (320, 224)), ((200, 224), (260, 164))]
    for (a, b) in wires:
        s += line(a[0], a[1], b[0], b[1], INK, 2)
    s += text(240, 306, "розведення НАМЕРТВО — назавжди", 10.5, INK, "middle", "bold")
    s += text(240, 334, "проєкт + виготовлення = МІСЯЦІ", 12, RED, "middle", "bold")
    s += text(240, 356, "помилка → нова маска, нова партія, нові гроші", 10.5, GREY, "middle", style="italic")
    # ── праворуч: FPGA — болванка + бітстрім ──
    s += rect(480, 88, 360, 300, "#f4f7f4", GREEN, 1.8, 10)
    s += text(660, 114, "FPGA: ту саму «болванку» НАЛАШТОВУЮТЬ", 12, GREEN, "middle", "bold")
    s += rect(530, 134, 260, 150, "#ffffff", INK, 1.6, 6)
    # масив однакових порожніх клітинок + перемикачі на перетинах
    for r in range(3):
        for c in range(4):
            cx = 560 + c * 60
            cy = 162 + r * 44
            s += rect(cx - 16, cy - 13, 32, 26, "#eef7ee", GREEN, 1.3, 3)
            s += text(cx, cy + 4, "?", 12, GREEN, "middle", "bold")
    # «програмовані» перемикачі (зелені точки) між клітинками
    for r in range(2):
        for c in range(3):
            sx = 590 + c * 60
            sy = 184 + r * 44
            s += circle(sx, sy, 3.6, GREEN, GREEN, 0)
    s += text(660, 306, "однакові клітинки + програмовані перемикачі", 10, GREY, "middle", style="italic")
    # бітстрім, що «вливається»
    s += text(660, 332, "завантаж БІТСТРІМ → схема готова за ПІВ ДНЯ", 11, GREEN, "middle", "bold")
    s += text(660, 356, "інша задача → інший бітстрім; та сама мікросхема", 10.5, GREY, "middle", style="italic")
    # стрілка-міст із підписом-аналогією
    s += text(W / 2, 410, "Це ТА САМА думка, що зробила комп'ютер універсальним (§3.5): не перепаювати залізо, а ЗАВАНТАЖИТИ опис.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 432, "Лише тут завантажують не послідовну програму для процесора, а ПАРАЛЕЛЬНУ СХЕМУ — конфігурацію самого заліза.",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 456, "Фріман називав це «чистою стрічкою»: чистий носій, на який інженер сам наносить потрібну логіку.",
              10.5, GREY, "middle", style="italic")
    save("fig-r07-0-3-blank-tape.svg", s)


# ═══════════ Рис. 3.7.0.4 — «фаблес»: компанія без власного заводу ══════════
def fig_fabless():
    W, H = 900, 446
    s = header(W, H)
    s += text(W / 2, 34, "Друге дітище Xilinx: «фаблес» — фірма, що проєктує чипи, але НЕ має заводу", 17.5, INK, "middle", "bold")
    s += text(W / 2, 56, "у Вондершмітта не було грошей на фабрику — тож він винайшов модель, за якою кремній ллє ЧУЖИЙ завод на замовлення",
              11.5, GREY, "middle", style="italic")
    # ── Xilinx: лише проєктування ──
    s += rect(60, 96, 250, 250, "#fdf4f4", RED, 2, 12)
    s += text(185, 122, "Xilinx (fabless)", 14.5, RED, "middle", "bold")
    s += text(185, 142, "тільки ПРОЄКТУЄ", 11, GREY, "middle", style="italic")
    for i, t in enumerate(["• архітектура FPGA", "• схема й логіка", "• ПЗ-компілятор схем", "• продаж і підтримка"]):
        s += text(82, 174 + i * 26, t, 11.5, INK, "start")
    s += text(185, 296, "ані чистих кімнат,", 10.5, INK, "middle")
    s += text(185, 314, "ані печей, ані $$$ на завод", 10.5, INK, "middle")
    # ── обмін: креслення → пластини ──
    s += arrow(312, 178, 588, 178, INK, 2.6)
    s += text(450, 166, "креслення кристала (GDSII)", 10.5, INK, "middle", "bold")
    s += arrow(588, 250, 312, 250, INK, 2.6)
    s += text(450, 270, "готові пластини з чипами", 10.5, INK, "middle", "bold")
    s += text(450, 220, "↔", 18, GREY, "middle", "bold")
    # ── фабрика-партнер ──
    s += rect(590, 96, 250, 250, "#f4f7f4", GREEN, 2, 12)
    s += text(715, 122, "Чужа фабрика", 14.5, GREEN, "middle", "bold")
    s += text(715, 142, "(партнер — напр. Seiko)", 11, GREY, "middle", style="italic")
    # стилізована «піч»/завод
    s += rect(645, 168, 140, 80, "#ffffff", GREEN, 1.6, 6)
    for k in range(4):
        s += rect(660 + k * 30, 184, 18, 48, "#eef7ee", GREEN, 1.2, 3)
    s += text(715, 270, "ллє КРЕМНІЙ на замовлення,", 10.5, INK, "middle")
    s += text(715, 288, "дозавантажує свій дорогий завод", 10.5, INK, "middle")
    s += text(715, 312, "(вигідно ОБОМ сторонам)", 10.5, GREEN, "middle", "bold")
    s += rect(60, 366, W - 120, 64, "#f6f8f6", GREY, 1.4, 10)
    s += text(W / 2, 390, "«Я не мав грошей побудувати фабрику» — Вондершмітт. Він домовився з давнім знайомим у Seiko, бо ЧУЖА фабрика так",
              11, INK, "middle", "bold")
    s += text(W / 2, 412, "лише виграє: завод не простоює. Цю модель «проєктуємо тут — виробляють там» сьогодні наслідує пів галузі (деталі — §3.10.8).",
              11, GREY, "middle", style="italic")
    save("fig-r07-0-4-fabless.svg", s)


# ═══════════ Рис. 3.7.0.5 — ставка Фрімана на закон Мура ════════════════════
def fig_moore_bet():
    W, H = 880, 470
    s = header(W, H)
    s += text(W / 2, 34, "Сміливий заклад Фрімана: «транзисторів буде так багато, що їх можна МАРНУВАТИ»", 17, INK, "middle", "bold")
    s += text(W / 2, 56, "FPGA свідомо «розкидається» транзисторами заради гнучкості; ставка була на те, що закон Мура зробить їх майже безплатними",
              11.5, GREY, "middle", style="italic")
    # осі
    ox, oy = 110, 300
    ax, ay = 470, 70
    s += arrow(ox, oy, ax + 10, oy, INK, 2)         # вісь часу
    s += arrow(ox, oy, ox, ay, INK, 2)              # вісь «ціна за транзистор»
    s += text(ax + 12, oy + 4, "роки →", 11.5, INK, "start", "bold")
    s += text(ox - 16, ay - 6, "ціна 1 транзистора", 11.5, INK, "start", "bold")
    s += text(ox - 16, ay + 12, "(логарифм)", 10, GREY, "start", style="italic")
    # спадна крива «дешевшання»
    pts = [(ox, ay + 18), (ox + 70, ay + 70), (ox + 150, ay + 130),
           (ox + 240, ay + 178), (ox + 320, ay + 206), (ax, ay + 222)]
    s += polyline(pts, BLUE, 3)
    s += text(ox + 250, ay + 160, "закон Мура:", 12, BLUE, "start", "bold")
    s += text(ox + 250, ay + 178, "транзистор дешевшає", 11, BLUE, "start")
    s += text(ox + 250, ay + 194, "удвічі що 2 роки", 11, BLUE, "start")
    # маркер «тут була ставка»
    s += circle(ox + 70, ay + 70, 5, RED, RED, 0)
    s += text(ox + 78, ay + 58, "1984: ставка зроблена тут", 10.5, RED, "start", "bold")
    # права колонка — суть угоди
    bx = 520
    s += rect(bx, 84, 300, 230, "#fafafa", INK, 1.6, 10)
    s += text(bx + 150, 110, "Чим «платить» FPGA за гнучкість", 12.5, INK, "middle", "bold")
    s += text(bx + 16, 140, "• більша площа кристала", 11.5, RED, "start", "bold")
    s += text(bx + 16, 160, "• повільніша за «запечений» ASIC", 11.5, RED, "start", "bold")
    s += text(bx + 16, 180, "• дорожча за штуку", 11.5, RED, "start", "bold")
    s += line(bx + 16, 196, bx + 284, 196, FAINT, 1.4)
    s += text(bx + 150, 220, "…але натомість:", 11.5, GREY, "middle", style="italic")
    s += text(bx + 16, 244, "• схема готова за ГОДИНИ, не місяці", 11.5, GREEN, "start", "bold")
    s += text(bx + 16, 264, "• помилку правлять новим бітстрімом", 11.5, GREEN, "start", "bold")
    s += text(bx + 16, 284, "• нуль витрат на маски й партію", 11.5, GREEN, "start", "bold")
    s += rect(60, 336, W - 120, 100, "#f4f7f4", GREEN, 1.6, 10)
    s += text(W / 2, 362, "У 1984-му «марнувати» транзистори звучало майже єретично — кремній був дорогий. Та Фріман угадав напрям:",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 384, "що дешевшими ставали транзистори, то вигіднішим робився обмін «трохи зайвого кремнію → миттєва гнучкість».",
              11.5, INK, "middle", "bold")
    s += text(W / 2, 410, "Це той самий компроміс «площа й швидкість проти гнучкості», що визначає вибір FPGA проти ASIC донині (§3.7.8).",
              11, GREY, "middle", style="italic")
    s += text(W / 2, 428, "Заклад на майбутнє дешевшання — рідкісний приклад, коли інженер виграв ставку на ціле десятиліття вперед.",
              10.5, GREY, "middle", style="italic")
    save("fig-r07-0-5-moore-bet.svg", s)


if __name__ == "__main__":
    fig_timeline()
    fig_founders()
    fig_blank_tape()
    fig_fabless()
    fig_moore_bet()
    print("done:", OUT)
