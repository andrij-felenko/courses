# -*- coding: utf-8 -*-
"""Фігури до теми «Методи множинного доступу» (multiple-access-methods).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Колізія: два сигнали в одному середовищі дають нечитану суму ────────────
def fig_collision():
    W, H = 720, 360
    f = [text(W / 2, 28, "Колізія: двоє говорять одночасно — обидва втрачені", 16, INK, "middle", bold=True)]

    # два передавачі зліва
    ax, ay = 95, 130
    bx, by = 95, 250
    f.append(rect(ax - 60, ay - 26, 120, 52, fill="#eef6ef", stroke=FIELD, sw=1.7))
    f.append(text(ax, ay - 2, "передавач A", 12, INK, "middle", bold=True))
    f.append(text(ax, ay + 15, "пакет A", 10.5, MUTED, "middle"))
    f.append(rect(bx - 60, by - 26, 120, 52, fill="#eaf0fd", stroke=NEG, sw=1.7))
    f.append(text(bx, by - 2, "передавач B", 12, INK, "middle", bold=True))
    f.append(text(bx, by + 15, "пакет B", 10.5, MUTED, "middle"))

    # спільне середовище — труба посередині
    f.append(text(W / 2, 70, "спільне середовище (ефір / дріт)", 11.5, MUTED, "middle"))

    # дві хвилі, що сходяться
    rx, ry = 610, 190
    f.append(arrow(ax + 64, ay, rx - 78, ry - 18, color=FIELD, sw=2.4))
    f.append(arrow(bx + 64, by, rx - 78, ry + 18, color=NEG, sw=2.4))

    # приймач справа
    f.append(rect(rx - 14, ry - 34, 96, 68, fill="#fbfcfd", stroke=LINE, sw=1.7))
    f.append(text(rx + 34, ry - 8, "приймач", 12, INK, "middle", bold=True))
    f.append(text(rx + 34, ry + 12, "бачить лише", 10, MUTED, "middle"))
    f.append(text(rx + 34, ry + 26, "суму ✗", 11, POS, "middle", bold=True))

    # вибух-колізія у точці зустрічі
    cxp, cyp = 500, 190
    f.append('<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="2"/>'
             % (_star(cxp, cyp, 26, 13, 10), POS))
    f.append(text(cxp, cyp + 5, "✗", 18, POS, "middle", bold=True))

    f.append(fitbox(W / 2 - 150, 300, 300, 34,
                    "сума двох сигналів нечитана — губляться ОБИДВА",
                    size=12, fill="#fdecea", stroke=POS, color=INK))

    render(os.path.join(IMG, "collision.svg"), W, H, *f)


def _star(cx, cy, ro, ri, n):
    pts = []
    for i in range(2 * n):
        r = ro if i % 2 == 0 else ri
        a = math.pi / n * i - math.pi / 2
        pts.append("%.1f,%.1f" % (cx + r * math.cos(a), cy + r * math.sin(a)))
    return " ".join(pts)


# ── 2. Чотири осі поділу ресурсу ──────────────────────────────────────────────
def fig_four_axes():
    W, H = 760, 470
    f = [text(W / 2, 28, "Чотири осі поділу спільного ресурсу", 16, INK, "middle", bold=True)]

    cols = ["#c0392b", "#2457d6", "#27ae60", "#b8860b"]  # A B C D
    names = ["A", "B", "C", "D"]

    def panel(px, py, title, sub):
        f.append(rect(px, py, 320, 168, fill="#fbfcfd", stroke="#dde3ea", sw=1.4, rx=8))
        f.append(text(px + 160, py + 24, title, 13.5, INK, "middle", bold=True))
        f.append(text(px + 160, py + 42, sub, 10.5, MUTED, "middle"))
        # рамка осей: x=час, y=частота
        gx, gy = px + 44, py + 150
        gw, gh = 250, 86
        f.append(line(gx, gy, gx + gw, gy, color=MUTED, sw=1.1))
        f.append(line(gx, gy, gx, gy - gh, color=MUTED, sw=1.1))
        f.append(text(gx + gw / 2, gy + 14, "час →", 9.5, MUTED, "middle"))
        f.append(text(gx - 6, gy - gh - 2, "частота", 9.5, MUTED, "end"))
        return gx, gy, gw, gh

    # FDMA: горизонтальні смуги (кожному — своя частота на весь час)
    gx, gy, gw, gh = panel(40, 58, "За частотою (FDMA)", "кожному своя смуга назавжди")
    for i in range(4):
        bh = gh / 4
        y = gy - (i + 1) * bh
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s" stroke="%s" stroke-width="1"/>'
                 % (gx + 2, y + 1, gw - 4, bh - 2, _tint(cols[i]), cols[i]))
        f.append(text(gx + gw / 2, y + bh / 2 + 3.5, names[i], 10, cols[i], "middle", bold=True))

    # TDMA: вертикальні смуги (кожному — своя мить на всю смугу)
    gx, gy, gw, gh = panel(400, 58, "За часом (TDMA)", "кожному своя мить")
    for i in range(4):
        bw = gw / 4
        x = gx + i * bw
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s" stroke="%s" stroke-width="1"/>'
                 % (x + 1, gy - gh + 1, bw - 2, gh - 2, _tint(cols[i]), cols[i]))
        f.append(text(x + bw / 2, gy - gh / 2 + 3.5, names[i], 10, cols[i], "middle", bold=True))

    # CDMA: усі заповнюють усе поле, накладені коди (штрихування різним кольором)
    gx, gy, gw, gh = panel(40, 246, "За кодом (CDMA)", "усі разом, кожен своїм кодом")
    for i in range(4):
        # діагональні штрихи свого кольору по всьому полю, зі зсувом фази
        off = i * 5
        seg = []
        x = gx + 4 + off
        while x < gx + gw - 2:
            seg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.4" opacity="0.65"/>'
                       % (x, gy - 2, x - gh + 6, gy - gh + 2, cols[i]))
            x += 20
        f.extend(seg)
    f.append(text(gx + gw / 2, gy - gh / 2 + 4, "A+B+C+D разом", 10, INK, "middle", bold=True))

    # SDMA: те саме поле перевикористане у двох рознесених «комірках»
    gx, gy, gw, gh = panel(400, 246, "За простором (SDMA)", "рознесені — той самий ресурс")
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s" stroke="%s" stroke-width="1"/>'
             % (gx + 2, gy - gh + 1, gw / 2 - 6, gh - 2, _tint(cols[0]), cols[0]))
    f.append(text(gx + gw / 4, gy - gh / 2 + 4, "A (тут)", 10, cols[0], "middle", bold=True))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s" stroke="%s" stroke-width="1"/>'
             % (gx + gw / 2 + 4, gy - gh + 1, gw / 2 - 6, gh - 2, _tint(cols[0]), cols[0]))
    f.append(text(gx + 3 * gw / 4, gy - gh / 2 + 4, "A (там)", 10, cols[0], "middle", bold=True))
    f.append(line(gx + gw / 2, gy - gh, gx + gw / 2, gy, color=MUTED, sw=1.2, dash="3 3"))

    render(os.path.join(IMG, "four-axes.svg"), W, H, *f)


def _tint(hexcol):
    """Дуже світлий відтінок кольору для заливки."""
    m = {"#c0392b": "#fbe7e4", "#2457d6": "#e6ecfb",
         "#27ae60": "#e4f4ea", "#b8860b": "#f6efdb"}
    return m.get(hexcol, "#f0f0f0")


# ── 3. Кадр TDMA: вікна, повна смуга, захисний зазор ──────────────────────────
def fig_tdma_frame():
    W, H = 740, 340
    f = [text(W / 2, 28, "Кадр TDMA: кожному — своє вікно на всю смугу", 16, INK, "middle", bold=True)]

    ox, oy = 60, 250
    aw, ah = 620, 150
    f.append(line(ox, oy, ox + aw + 12, oy, color=MUTED, sw=1.2))
    f.append(text(ox + aw + 16, oy + 4, "час", 11, MUTED, "start"))
    f.append(line(ox, oy + 4, ox, oy - ah - 6, color=MUTED, sw=1.2))
    f.append(text(ox - 8, oy - ah - 2, "повна смуга", 11, MUTED, "end"))

    slots = ["A", "B", "C", "D", "A", "B"]
    cols = {"A": "#c0392b", "B": "#2457d6", "C": "#27ae60", "D": "#b8860b"}
    n = len(slots)
    gap = 8
    sw = (aw - (n - 1) * gap) / n
    for i, s in enumerate(slots):
        x = ox + i * (sw + gap)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (x, oy - ah, sw, ah, _tint(cols[s]), cols[s]))
        f.append(text(x + sw / 2, oy - ah / 2 + 5, s, 16, cols[s], "middle", bold=True))
        f.append(text(x + sw / 2, oy + 16, "вікно %d" % (i + 1), 9.5, MUTED, "middle"))

    # позначити захисний зазор
    gxp = ox + sw + gap / 2
    f.append(arrow(gxp, oy - ah - 28, gxp, oy - ah - 6, color=MUTED, sw=1.3))
    f.append(text(gxp + 64, oy - ah - 32, "захисний зазор у часі", 10, MUTED, "middle"))

    # дужка кадру
    f.append(line(ox, oy + 36, ox + 4 * (sw + gap) - gap, oy + 36, color=INK, sw=1.4))
    f.append(text(ox + (4 * (sw + gap) - gap) / 2, oy + 50, "один кадр (повторюється)", 10.5, INK, "middle", bold=True))

    render(os.path.join(IMG, "tdma-frame.svg"), W, H, *f)


# ── 4. CDMA: усі разом → множення на код збирає одного ─────────────────────────
def fig_cdma():
    W, H = 760, 340
    f = [text(W / 2, 26, "CDMA: код абонента збирає свій сигнал, чужі лишає тлом", 15.5, INK, "middle", bold=True)]

    def panel(x0, title):
        f.append(rect(x0, 52, 330, 258, fill="#fbfcfd", stroke="#dde3ea", sw=1.4, rx=8))
        f.append(text(x0 + 165, 74, title, 13, INK, "middle", bold=True))
        ax, ay, aw, ah = x0 + 38, 278, 256, 168
        f.append(line(ax, ay, ax + aw, ay, color=MUTED, sw=1.1))
        f.append(line(ax, ay, ax, ay - ah, color=MUTED, sw=1.1))
        f.append(text(ax + aw / 2, ay + 16, "частота", 10, MUTED, "middle"))
        return ax, ay, aw, ah

    nf = 0.16
    cols = ["#c0392b", "#27ae60", "#b8860b"]  # A B C
    # ── ліва панель: у каналі всі разом ──
    ax, ay, aw, ah = panel(30, "У каналі: A+B+C, суцільна суміш")
    f.append(line(ax, ay - nf * ah, ax + aw, ay - nf * ah, color=MUTED, sw=1, dash="4 4"))
    # три розмазані шари різного кольору, накладені
    for i, c in enumerate(cols):
        h = (0.30 + 0.05 * i)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s" stroke-width="1.2" opacity="0.55"/>'
                 % (ax + 8 + i * 4, ay - h * ah, aw - 16 - i * 8, h * ah, _tint(c), c))
    f.append(text(ax + aw / 2, ay - 0.46 * ah, "A + B + C", 11, INK, "middle", bold=True))

    # стрілка-перехід
    f.append(arrow(372, 175, 412, 175, color=INK, sw=2.2))
    f.append(text(392, 162, "× код B", 10.5, NEG, "middle", bold=True))

    # ── права панель: після множення на код B ──
    ax, ay, aw, ah = panel(400, "Після × коду B: збирається лише B")
    f.append(line(ax, ay - nf * ah, ax + aw, ay - nf * ah, color=MUTED, sw=1, dash="4 4"))
    # B — вузька висока купка (зелена)
    f.append('<rect x="%.1f" y="%.1f" width="22" height="%.1f" rx="3" fill="%s" stroke="%s" stroke-width="2.2"/>'
             % (ax + 0.42 * aw, ay - 0.86 * ah, 0.86 * ah, _tint("#27ae60"), "#27ae60"))
    f.append(text(ax + 0.42 * aw + 11, ay - 0.86 * ah - 8, "B ↑", 11, "#27ae60", "middle", bold=True))
    # A,C — розмазане низьке тло
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f3e7ea" stroke="%s" stroke-width="1.1" opacity="0.7"/>'
             % (ax + 10, ay - 0.11 * ah, aw - 20, 0.11 * ah, POS))
    f.append(text(ax + aw / 2, ay - 0.11 * ah - 7, "A, C ↓ розмазані", 10, MUTED, "middle"))

    render(os.path.join(IMG, "cdma.svg"), W, H, *f)


# ── 5. Розклад проти навперебій ───────────────────────────────────────────────
def fig_scheduled_vs_random():
    W, H = 740, 330
    f = [text(W / 2, 28, "Дві філософії доступу: розклад чи навперебій", 16, INK, "middle", bold=True)]

    # ── ліва: розклад ──
    f.append(rect(36, 56, 326, 250, fill="#eef6ef", stroke=FIELD, sw=1.7, rx=8))
    f.append(text(199, 80, "Розклад (scheduled)", 13.5, INK, "middle", bold=True))
    f.append(text(199, 98, "ресурс поділено наперед", 10.5, MUTED, "middle"))
    pros = ["+ колізій немає", "+ доставка вчасно, гарантовано"]
    cons = ["− треба координатор і синхронізація", "− частка простоює без діла"]
    y = 124
    for p in pros:
        f.append(text(58, y, p, 11.5, FIELD, "start", bold=True)); y += 24
    for c in cons:
        f.append(text(58, y, c, 11.5, MUTED, "start")); y += 24
    f.append(text(199, y + 8, "FDMA · TDMA · CDMA", 11, INK, "middle", bold=True))

    # ── права: навперебій ──
    f.append(rect(378, 56, 326, 250, fill="#fdecea", stroke=POS, sw=1.7, rx=8))
    f.append(text(541, 80, "Навперебій (random)", 13.5, INK, "middle", bold=True))
    f.append(text(541, 98, "говори коли маєш що", 10.5, MUTED, "middle"))
    pros = ["+ жодної координації", "+ апаратура проста, гнучка"]
    cons = ["− можливі колізії", "− треба виявляти й перевідправляти"]
    y = 124
    for p in pros:
        f.append(text(400, y, p, 11.5, POS, "start", bold=True)); y += 24
    for c in cons:
        f.append(text(400, y, c, 11.5, MUTED, "start")); y += 24
    f.append(text(541, y + 8, "ALOHA · CSMA (Wi-Fi, Ethernet)", 10.5, INK, "middle", bold=True))

    render(os.path.join(IMG, "scheduled-vs-random.svg"), W, H, *f)


# ── 6. Як обрати вісь ─────────────────────────────────────────────────────────
def fig_choosing():
    W, H = 740, 360
    f = [text(W / 2, 28, "Орієнтир вибору методу доступу", 16, INK, "middle", bold=True)]

    rows = [
        ("Мало абонентів, трафік рівний,\nпотрібні гарантії доставки", "РОЗКЛАД (TDMA/FDMA)", "#eef6ef", FIELD),
        ("Багато змінних абонентів,\nтрафік рідкий і непередбачуваний", "НАВПЕРЕБІЙ (CSMA)", "#fdecea", POS),
        ("Потрібна скритність\nі стійкість до глушіння", "КОД (розширення спектра)", "#eaf0fd", NEG),
        ("Абоненти рознесені\nв просторі", "ПРОСТІР (промені, соти)", "#f6efdb", "#b8860b"),
    ]
    y = 62
    for cond, pick, fill, stroke in rows:
        f.append(rect(40, y, 380, 62, fill="#fbfcfd", stroke="#dde3ea", sw=1.3, rx=6))
        l1, l2 = cond.split("\n")
        f.append(text(58, y + 26, l1, 11.5, INK, "start"))
        f.append(text(58, y + 44, l2, 11.5, MUTED, "start"))
        # стрілка
        f.append(arrow(424, y + 31, 452, y + 31, color=INK, sw=2))
        # вибір
        f.append(rect(458, y + 10, 244, 42, fill=fill, stroke=stroke, sw=1.7, rx=6))
        f.append(text(580, y + 36, pick, 11.5, INK, "middle", bold=True))
        y += 72

    render(os.path.join(IMG, "choosing.svg"), W, H, *f)


# ── 7. Синхронізація кадру за спільною позначкою (beacon/PPS) ─────────────────
def fig_frame_sync():
    W, H = 760, 360
    f = [text(W / 2, 26, "Кадр прив'язано до спільної позначки часу", 16, INK, "middle", bold=True)]

    ox, oy = 60, 250
    aw = 640
    # вісь часу
    f.append(line(ox, oy, ox + aw + 14, oy, color=MUTED, sw=1.2))
    f.append(text(ox + aw + 18, oy + 4, "час", 11, MUTED, "start"))

    # позначка-маяк: вертикальний імпульс на початку кадру
    f.append(line(ox, oy + 6, ox, oy - 150, color=POS, sw=2.6))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (ox - 6, oy - 150, ox + 6, oy - 150, ox, oy - 138, POS))
    f.append(text(ox, oy - 158, "позначка (PPS / маяк)", 11, POS, "middle", bold=True))
    f.append(text(ox + 2, oy + 22, "T₀ — початок кадру", 10.5, POS, "middle"))

    # вікна кадру
    slots = ["A", "B", "C", "D", "E", "F"]
    cols = {"A": "#c0392b", "B": "#2457d6", "C": "#27ae60", "D": "#b8860b",
            "E": "#7d3c98", "F": "#117a8b"}
    n = len(slots)
    ah = 96
    gap = 12
    sw = (aw - (n - 1) * gap) / n
    my = 2  # вікно C — наше
    for i, s in enumerate(slots):
        x = ox + i * (sw + gap)
        hot = (i == my)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" stroke="%s" stroke-width="%.1f"/>'
                 % (x, oy - ah, sw, ah, _tint(cols[s]), cols[s], 2.6 if hot else 1.6))
        f.append(text(x + sw / 2, oy - ah / 2 + 5, s, 15, cols[s], "middle", bold=True))
        # зсув вікна = offset[i]
        f.append(text(x + sw / 2, oy + 16, "+%d" % i + "·Tв", 9, MUTED, "middle"))
    # підпис нашого вікна
    mx = ox + my * (sw + gap)
    f.append(text(mx + sw / 2, oy - ah - 10, "наше вікно", 10.5, cols["C"], "middle", bold=True))

    # захисний зазор між двома вікнами (показати один)
    g0 = ox + (sw + gap) - gap
    f.append(rect(g0, oy - ah, gap, ah, fill="#f0f0f0", stroke="#cfcfcf", sw=0.8, rx=1))
    f.append(arrow(g0 + gap / 2, oy - ah - 30, g0 + gap / 2, oy - ah - 6, color=MUTED, sw=1.2))
    f.append(text(g0 + gap / 2 + 52, oy - ah - 34, "захисний зазор", 9.5, MUTED, "middle"))

    # пояснення внизу
    f.append(fitbox(ox, oy + 36, aw, 28,
                    "момент вікна = T₀ + номер·Tв ;  усі вузли рахують від тієї самої позначки T₀",
                    size=11.5, fill="#eef6ef", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "frame-sync.svg"), W, H, *f)


# ── 8. Дрейф годинників: чуже вікно наповзає ──────────────────────────────────
def fig_drift():
    W, H = 760, 380
    f = [text(W / 2, 26, "Дрейф годинників: без поправки вузол сповзає з вікна", 15.5, INK, "middle", bold=True)]

    ox = 70
    aw = 620
    lane_h = 58

    def lane(y, label, color):
        f.append(line(ox, y, ox + aw + 10, y, color=MUTED, sw=1.0))
        f.append(text(ox - 10, y - lane_h / 2 + 4, label, 10.5, color, "end", bold=True))

    # верхня доріжка — істинні межі вікон (від маяка)
    yt = 110
    lane(yt, "істинне\nвікно", INK)
    nsl = 5
    sw = aw / nsl
    for i in range(nsl):
        x = ox + i * sw
        hot = (i == 2)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s" stroke="%s" stroke-width="%.1f"/>'
                 % (x + 2, yt - lane_h, sw - 4, lane_h, _tint("#27ae60") if hot else "#f4f6f8",
                    "#27ae60" if hot else MUTED, 2.4 if hot else 1.0))
        if hot:
            f.append(text(x + sw / 2, yt - lane_h / 2 + 4, "наше", 11, "#27ae60", "middle", bold=True))

    # нижня доріжка — те, як їх БАЧИТЬ вузол із швидшим годинником (усе зсунуте вперед)
    yb = 250
    lane(yb, "вузол\nбачить", POS)
    shift = 46  # накопичений зсув
    for i in range(nsl):
        x = ox + i * sw + shift * (i / (nsl - 1.0))  # зсув росте до кінця кадру
        hot = (i == 2)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" fill="%s" stroke="%s" stroke-width="%.1f" opacity="0.92"/>'
                 % (x + 2, yb - lane_h, sw - 4, lane_h, _tint("#c0392b") if hot else "#fbfcfd",
                    "#c0392b" if hot else MUTED, 2.4 if hot else 1.0))
        if hot:
            f.append(text(x + sw / 2, yb - lane_h / 2 + 4, "наше?", 11, "#c0392b", "middle", bold=True))

    # стрілки зсуву між істинною і зміщеною межею нашого вікна
    xt = ox + 2 * sw
    xb = ox + 2 * sw + shift * (2 / (nsl - 1.0))
    f.append(arrow(xt, yt + 6, xb, yb - lane_h - 6, color=POS, sw=1.6))
    f.append(text((xt + xb) / 2 + 70, (yt + yb) / 2 - 8, "накопичений зсув за кадр", 10, POS, "middle"))

    # підсумок
    f.append(fitbox(ox, yb + 40, aw, 56,
                    "20 ppm = 20 мкс зсуву на кожну секунду між двома вільними годинниками.\n"
                    "За кадр зсув росте; «хвіст» нашого пакета наповзає на сусіднє вікно → колізія.",
                    size=11.5, fill="#fdecea", stroke=POS, color=INK))

    render(os.path.join(IMG, "drift.svg"), W, H, *f)


# ── 9. Машина станів повторного захоплення синхронізації ──────────────────────
def fig_reacquire():
    W, H = 760, 330
    f = [text(W / 2, 26, "Втрата й повторний захоп синхронізації", 16, INK, "middle", bold=True)]

    # три стани по горизонталі
    states = [
        (160, "ПОШУК", "слухаю весь час,\nчекаю позначку", "#eaf0fd", NEG),
        (400, "СИНХРОН", "рахую вікна,\nпередаю у своєму", "#eef6ef", FIELD),
        (620, "УТРИМАННЯ", "позначки нема —\nйду за лічильником", "#f6efdb", "#b8860b"),
    ]
    cy = 150
    R = 64
    for cx, name, sub, fill, stroke in states:
        f.append(circle(cx, cy, R, fill=fill, stroke=stroke, sw=2.4))
        f.append(text(cx, cy - 6, name, 13, INK, "middle", bold=True))
        for j, ln in enumerate(sub.split("\n")):
            f.append(text(cx, cy + 12 + j * 13, ln, 9, MUTED, "middle"))

    # переходи
    # ПОШУК → СИНХРОН (зловив позначку)
    f.append(arrow(160 + R, cy - 14, 400 - R, cy - 14, color=INK, sw=1.8))
    f.append(text(280, cy - 24, "зловив позначку", 9.5, FIELD, "middle", bold=True))
    # СИНХРОН → УТРИМАННЯ (позначку пропустив)
    f.append(arrow(400 + R, cy - 14, 620 - R, cy - 14, color=INK, sw=1.8))
    f.append(text(510, cy - 24, "пропустив маяк", 9.5, "#b8860b", "middle", bold=True))
    # УТРИМАННЯ → СИНХРОН (маяк повернувся)
    f.append(arrow(620 - R, cy + 16, 400 + R, cy + 16, color=INK, sw=1.6))
    f.append(text(510, cy + 30, "маяк повернувся", 9.5, FIELD, "middle"))
    # УТРИМАННЯ → ПОШУК (надто довго без маяка) — велика дуга низом
    f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (620, cy + R, 390, cy + R + 110, 160, cy + R, POS))
    f.append(text(390, cy + R + 96, "тиша надто довго → скидаю лічильник, шукаю заново", 10, POS, "middle", bold=True))

    render(os.path.join(IMG, "reacquire.svg"), W, H, *f)


# ── 10. Родовід випадкового доступу: ALOHA → Ethernet → Wi-Fi (для hist-вставки) ─
def fig_aloha_lineage():
    W, H = 760, 340
    f = [text(W / 2, 28, "Один корінь: від ALOHAnet до всього випадкового доступу", 15.5, INK, "middle", bold=True)]

    # горизонтальна вісь часу
    ax, ay = 56, 150
    f.append(line(ax, ay, ax + 650, ay, color=MUTED, sw=1.4))
    f.append(text(ax + 656, ay + 4, "час", 11, MUTED, "start"))

    # вузли: (рік, підпис, опис, x, колір)
    nodes = [
        ("1971", "ALOHAnet", "радіо: говори\nколи маєш що", 120, POS),
        ("1973", "Ethernet", "та сама ідея\nна дроті + CSMA/CD", 320, NEG),
        ("1985", "IEEE 802.3", "стандарт LAN\nна базі Ethernet", 480, "#b8860b"),
        ("1997", "Wi-Fi", "ефір знову:\nCSMA/CA, 802.11", 640, FIELD),
    ]
    prev = None
    for yr, name, desc, x, col in nodes:
        if prev is not None:
            f.append(arrow(prev + 16, ay, x - 60, ay, color=INK, sw=2.0))
        f.append(circle(x, ay, 7, fill=_tint(col), stroke=col, sw=2.4))
        f.append(text(x, ay - 66, yr, 12, col, "middle", bold=True))
        tb = textbox(x, ay - 44, name, size=12.5, pad=7, fill=_tint(col), stroke=col, color=INK, bold=True)
        f.append(tb[0])
        f.append(mtext(x, ay + 30, desc, size=9.5, color=MUTED))
        prev = x

    # підпис-висновок унизу
    f.append(fitbox(W / 2 - 305, 286, 610, 40,
                    "Одна ідея — «не координуй наперед, розрулюй колізії постфактум» — "
                    "проросла з гавайського радіо в дріт, у стандарти й назад в ефір.",
                    size=11, fill="#fbfcfd", stroke="#dde3ea", color=INK))

    render(os.path.join(IMG, "aloha-lineage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_collision()
    fig_four_axes()
    fig_tdma_frame()
    fig_cdma()
    fig_scheduled_vs_random()
    fig_choosing()
    fig_frame_sync()
    fig_drift()
    fig_reacquire()
    fig_aloha_lineage()
    print("OK: figures written to", IMG)
