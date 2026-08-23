# -*- coding: utf-8 -*-
"""Фігури до теми «Thread, Zigbee і Matter: стек розумного дому на 802.15.4».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

ZIG = "#b8860b"   # Zigbee — теплий
THR = "#2457d6"   # Thread — синій
MAT = "#27ae60"   # Matter — зелений (дах)
BASE = "#6b7280"  # підвал — нейтральний


# ── 1. Будівля поверхів: один підвал, різні надбудови ─────────────────────────
def fig_stack_layers():
    W, H = 760, 470
    f = [text(W / 2, 28, "Один підвал — різні поверхи над ним", 16, INK, "middle", bold=True)]

    # Спільний підвал 802.15.4 на всю ширину
    bx, bw = 70, 620
    by, bh = 392, 46
    f.append(rect(bx, by, bw, bh, fill="#eef0f2", stroke=BASE, sw=2))
    f.append(text(bx + bw / 2, by + 20, "Радіо 802.15.4  —  PHY + MAC  (спільний фундамент)", 12.5, INK, "middle", bold=True))
    f.append(text(bx + bw / 2, by + 37, "2.4 ГГц · 250 кбіт/с · ощадливе · CSMA/CA", 10, MUTED, "middle"))

    # ── Лівий під'їзд: Zigbee (вся будівля від одного) ──
    zx, zw = 70, 200
    # мережа Zigbee
    f.append(rect(zx, 300, zw, 80, fill="#f6efdb", stroke=ZIG, sw=1.8))
    f.append(text(zx + zw / 2, 326, "Мережа Zigbee", 12, INK, "middle", bold=True))
    f.append(text(zx + zw / 2, 344, "власна, НЕ на IP", 9.5, MUTED, "middle"))
    f.append(text(zx + zw / 2, 360, "сітка: ZC · ZR · ZED", 9.5, MUTED, "middle"))
    # прикладна мова Zigbee
    f.append(rect(zx, 232, zw, 56, fill="#f6efdb", stroke=ZIG, sw=1.8))
    f.append(text(zx + zw / 2, 256, "Прикладна мова", 11.5, INK, "middle", bold=True))
    f.append(text(zx + zw / 2, 273, "Cluster Library / Dotdot", 9.5, MUTED, "middle"))
    # дужка «вся будівля Zigbee»
    f.append(line(zx - 14, 232, zx - 14, 380, color=ZIG, sw=2.2))
    f.append(mtext(zx - 30, 300, "Zigbee:\nуся будівля\nвід одного", size=9.5, color=ZIG, anchor="end", bold=True))

    # ── Правий під'їзд: Thread (нижні поверхи) + Matter (дах) ──
    tx, tw = 360, 330
    # 6LoWPAN перехідник
    f.append(rect(tx, 348, tw, 32, fill="#e6ecfb", stroke=THR, sw=1.6))
    f.append(text(tx + tw / 2, 369, "6LoWPAN — стиск IPv6-заголовків у тісний кадр", 10, INK, "middle"))
    # мережа Thread (IPv6)
    f.append(rect(tx, 284, tw, 60, fill="#e6ecfb", stroke=THR, sw=1.8))
    f.append(text(tx + tw / 2, 308, "Мережа Thread  —  IPv6-сітка", 12, INK, "middle", bold=True))
    f.append(text(tx + tw / 2, 326, "кожен вузол = справжня IP-адреса · без єдиної точки відмови", 9.3, MUTED, "middle"))
    # дужка Thread
    f.append(line(tx - 12, 284, tx - 12, 380, color=THR, sw=2.2))
    f.append(mtext(tx - 26, 332, "Thread:\nнижні\nповерхи", size=9.5, color=THR, anchor="end", bold=True))

    # дах Matter — ширший за Thread, бо лягає й на Wi-Fi/Ethernet
    mx, mw = 360, 330
    f.append(rect(mx, 196, mw, 76, fill="#e4f4ea", stroke=MAT, sw=2.2))
    f.append(text(mx + mw / 2, 222, "Matter  —  спільна прикладна МОВА (дах)", 12.5, INK, "middle", bold=True))
    f.append(text(mx + mw / 2, 241, "єдині типи пристроїв і дії для ВСІХ виробників", 9.6, MUTED, "middle"))
    f.append(text(mx + mw / 2, 258, "їде поверх Thread · Wi-Fi · Ethernet  (BLE — для знайомства)", 9.3, MUTED, "middle"))

    # стрілки: Matter сідає на Thread
    f.append(arrow(mx + 80, 272, mx + 80, 282, color=MAT, sw=2))
    f.append(arrow(mx + mw - 80, 272, mx + mw - 80, 282, color=MAT, sw=2))

    # підпис-висновок
    f.append(fitbox(70, 70, 620, 50,
                    "Не три суперники, а різні ПОВЕРХИ. Zigbee надбудовує все сам (острів, не на IP).\n"
                    "Thread будує IP-мережу без даху; Matter — спільний дах-мова, що лягає на Thread (і на Wi-Fi).",
                    size=11, fill="#fbfcfd", stroke="#dde3ea", color=INK))

    render(os.path.join(IMG, "stack-layers.svg"), W, H, *f)


# ── 2. Зірка проти сітки: дальність і самозлікування ──────────────────────────
def fig_star_vs_mesh():
    W, H = 760, 380
    f = [text(W / 2, 26, "Зірка (Wi-Fi) проти сітки (802.15.4): дальність і обхід відмови", 15, INK, "middle", bold=True)]

    # ── ліва панель: зірка ──
    f.append(rect(34, 50, 330, 300, fill="#fbfcfd", stroke="#dde3ea", sw=1.4, rx=8))
    f.append(text(199, 72, "Зірка: усі напряму до центру", 12.5, INK, "middle", bold=True))
    hub = (150, 175)
    f.append(circle(hub[0], hub[1], 22, fill="#e6ecfb", stroke=THR, sw=2))
    f.append(text(hub[0], hub[1] + 4, "хаб", 10, THR, "middle", bold=True))
    near = [(150, 100), (90, 215), (215, 130), (110, 130)]
    for nx, ny in near:
        f.append(line(hub[0], hub[1], nx, ny, color=MUTED, sw=1.3))
        f.append(circle(nx, ny, 11, fill="#eef0f2", stroke=BASE, sw=1.5))
    # далекий вузол поза радіусом — не добиває
    far = (300, 300)
    f.append('<circle cx="%d" cy="%d" r="80" fill="none" stroke="%s" stroke-width="1.1" stroke-dasharray="4 5"/>'
             % (hub[0], hub[1], MUTED))
    f.append(text(hub[0] + 60, hub[1] - 60, "радіус", 9, MUTED, "middle"))
    f.append(line(hub[0], hub[1], far[0], far[1], color=POS, sw=1.3, dash="3 4"))
    f.append(circle(far[0], far[1], 11, fill="#fdecea", stroke=POS, sw=1.7))
    f.append(text(far[0], far[1] + 26, "далека лампа", 9.5, POS, "middle", bold=True))
    f.append(text(far[0] - 6, far[1] - 16, "✗ не добиває", 9.5, POS, "end", bold=True))

    # ── права панель: сітка ──
    f.append(rect(396, 50, 330, 300, fill="#fbfcfd", stroke="#dde3ea", sw=1.4, rx=8))
    f.append(text(561, 72, "Сітка: естафета через сусідів", 12.5, INK, "middle", bold=True))
    # вузли сітки
    G = {
        "hub": (450, 110),
        "a":   (560, 130),
        "b":   (520, 210),
        "x":   (620, 215),   # цей зникне
        "c":   (600, 300),
        "lamp":(680, 300),
    }
    # ребра сітки
    edges = [("hub", "a"), ("hub", "b"), ("a", "x"), ("b", "x"),
             ("x", "c"), ("x", "lamp"), ("b", "c"), ("c", "lamp")]
    for u, v in edges:
        col = MUTED
        sw = 1.2
        if "x" in (u, v):
            col = "#cfcfcf"; sw = 1.0
        f.append(line(G[u][0], G[u][1], G[v][0], G[v][1], color=col, sw=sw))
    # вузли
    for k, (nx, ny) in G.items():
        if k == "hub":
            f.append(circle(nx, ny, 18, fill="#e6ecfb", stroke=THR, sw=2))
            f.append(text(nx, ny + 4, "хаб", 9, THR, "middle", bold=True))
        elif k == "lamp":
            f.append(circle(nx, ny, 12, fill="#e4f4ea", stroke=MAT, sw=1.8))
            f.append(text(nx, ny + 26, "лампа", 9.5, MAT, "middle", bold=True))
        elif k == "x":
            f.append(circle(nx, ny, 11, fill="#f7f7f7", stroke="#bbbbbb", sw=1.4))
            f.append(text(nx, ny + 3, "✗", 12, POS, "middle", bold=True))
            f.append(text(nx, ny - 17, "зник", 9, POS, "middle", bold=True))
        else:
            f.append(circle(nx, ny, 11, fill="#eef0f2", stroke=BASE, sw=1.5))
    # підсвітити обхідний маршрут hub→b→c→lamp
    route = ["hub", "b", "c", "lamp"]
    for i in range(len(route) - 1):
        u, v = route[i], route[i + 1]
        f.append(line(G[u][0], G[u][1], G[v][0], G[v][1], color=MAT, sw=2.6))
    f.append(text(561, 338, "вузол зник → пакет іде в обхід (самозлікування)", 9.8, MAT, "middle", bold=True))

    render(os.path.join(IMG, "star-vs-mesh.svg"), W, H, *f)


# ── 3. Хронологія: від острова Zigbee до спільного даху Matter ────────────────
def fig_thread_matter_timeline():
    # Свідомо РІВНОМІРНІ слоти (не лінійна шкала років): тут важить ПОРЯДОК віх
    # і дуга «острів → фундамент → дах», а не точні проміжки між датами.
    miles = [
        ("2002",       "Zigbee Alliance",    ZIG, ["острівний стек:", "своя мережа + мова"]),
        ("січ. 2014",  "Google купує Nest",  THR, ["$3.2 млрд — за Thread", "стане Google"]),
        ("лип. 2014",  "Thread Group",       THR, ["IP-мережа на 802.15.4;", "дах лишено порожнім"]),
        ("2016",       "OpenThread",         THR, ["відкритий код —", "Thread іде в чіпи"]),
        ("серп. 2018", "Apple → Thread",     THR, ["навіть Apple згодна:", "дім має бути на IP"]),
        ("груд. 2019", "CHIP",               MAT, ["Amazon + Apple + Google", "за одним столом"]),
        ("трав. 2021", "CHIP → Matter",      MAT, ["і Zigbee Alliance →", "CSA (ширша роль)"]),
        ("жовт. 2022", "Matter 1.0",         MAT, ["готовий стандарт:", "текст + код + знак"]),
    ]
    n = len(miles)
    bw, bh = 168, 62          # картка
    gap = 14                  # проміжок між картками
    margin = 18
    W = margin * 2 + n * bw + (n - 1) * gap
    H = 320
    axy = H / 2 + 6           # вісь по центру

    f = [text(W / 2, 28, "Від острова Zigbee до спільного даху Matter (порядок віх)", 15, INK, "middle", bold=True)]
    # вісь часу
    ax0, ax1 = margin, W - margin
    f.append(line(ax0, axy, ax1 - 6, axy, color=BASE, sw=2.2))
    f.append(arrow(ax1 - 8, axy, ax1, axy, color=BASE, sw=2.2))

    for i, (ylab, head, col, lines) in enumerate(miles):
        cx = margin + bw / 2 + i * (bw + gap)
        side_up = (i % 2 == 0)
        f.append(circle(cx, axy, 6.0, fill=col, stroke=col, sw=1.5))
        f.append(text(cx, axy + (-13 if side_up else 20), ylab, 9.5, MUTED, "middle", bold=True))
        by = axy - 26 - bh if side_up else axy + 26
        f.append(line(cx, axy, cx, by + (bh if side_up else 0), color=col, sw=1.1, dash="2 3"))
        f.append(rect(cx - bw / 2, by, bw, bh, fill="#fbfcfd", stroke=col, sw=1.6))
        f.append(text(cx, by + 19, head, 11, INK, "middle", bold=True))
        f.append(mtext(cx, by + 35, lines, size=9, color=MUTED))

    # легенда трьох ролей під віссю
    ly = H - 16
    f.append(circle(margin + 6, ly, 6, fill=ZIG, stroke=ZIG))
    f.append(text(margin + 18, ly + 4, "Zigbee — острів", 10.5, INK, "start"))
    f.append(circle(margin + 200, ly, 6, fill=THR, stroke=THR))
    f.append(text(margin + 212, ly + 4, "Thread — IP-мережа (фундамент)", 10.5, INK, "start"))
    f.append(circle(margin + 470, ly, 6, fill=MAT, stroke=MAT))
    f.append(text(margin + 482, ly + 4, "Matter — спільна мова (дах)", 10.5, INK, "start"))

    render(os.path.join(IMG, "thread-matter-timeline.svg"), W, H, *f)


# ── 4. Вилястий танок бджоли: звідки «зигзаг» у назві Zigbee ──────────────────
def fig_waggle_dance():
    import math
    W, H = 760, 430
    f = [text(W / 2, 26, "Вилястий танок бджоли: кут = напрям, тривалість = відстань", 15, INK, "middle", bold=True)]

    # центр вісімки
    cx, cy = 250, 240
    # пряма «вилянка» під кутом ang праворуч від вертикалі
    ang = 32.0
    L = 92                          # довжина прямої вилянки
    a = math.radians(ang)
    dx, dy = math.sin(a) * L, -math.cos(a) * L   # вгору-праворуч
    sx, sy = cx - dx / 2, cy - dy / 2            # низ вилянки
    ex, ey = cx + dx / 2, cy + dy / 2            # верх вилянки (до Сонця)

    # вертикаль = напрям на Сонце
    f.append(line(cx, cy + 60, cx, cy - 120, color=MUTED, sw=1.3, dash="4 5"))
    f.append(text(cx + 4, cy - 124, "вертикаль ↑ = на Сонце", 9.5, MUTED, "start"))
    # маленьке сонце вгорі
    f.append(circle(cx, cy - 118, 9, fill="#fff4d6", stroke=ZIG, sw=1.6))
    for k in range(8):
        t = math.radians(k * 45)
        f.append(line(cx + math.cos(t) * 12, cy - 118 + math.sin(t) * 12,
                      cx + math.cos(t) * 16, cy - 118 + math.sin(t) * 16, color=ZIG, sw=1.2))

    # дуги повернення (вісімка): права петля й ліва петля
    r = 46
    # права дуга: від верху вилянки навколо праворуч до низу
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 1 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (ex, ey, r, r, sx, sy, MUTED))
    # ліва дуга: від верху навколо ліворуч до низу
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 1 0 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (ex, ey, r, r, sx, sy, MUTED))
    # стрілки напрямку обходу на дугах
    f.append(text(ex + r + 6, cy - 6, "зворот", 8.5, MUTED, "start"))
    f.append(text(sx - r - 6, cy + 10, "зворот", 8.5, MUTED, "end"))

    # сама вилянка — жирна кольорова з «хитанням» (зигзаг уздовж лінії)
    # перпендикуляр до вилянки
    px, py = math.cos(a), math.sin(a)        # одиничний перпендикуляр (вправо від напряму вгору)
    zig = []
    steps = 7
    amp = 7
    for i in range(steps + 1):
        t = i / steps
        bxp = sx + (ex - sx) * t
        byp = sy + (ey - sy) * t
        s = amp if (i % 2 == 0) else -amp
        zig.append((bxp + px * s, byp + py * s))
    path = "M %.1f %.1f " % zig[0] + " ".join("L %.1f %.1f" % p for p in zig[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, ZIG))
    # стрілка-напрям уздовж вилянки (на Сонце)
    f.append(arrow(cx, cy, ex, ey, color=ZIG, sw=2.4))
    f.append(circle(sx, sy, 4, fill=ZIG, stroke=ZIG))
    f.append(text(sx - 6, sy + 16, "старт", 9, ZIG, "end", bold=True))

    # позначка кута між вертикаллю та вилянкою
    f.append('<path d="M %.1f %.1f A 34 34 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.3"/>'
             % (cx, cy - 34, cx + math.sin(a) * 34, cy - math.cos(a) * 34, INK))
    f.append(text(cx + 16, cy - 40, "кут θ", 10, INK, "start", bold=True))

    # підпис до вилянки
    f.append(mtext(ex + 30, ey + 6, ["пряма «вилянка»:", "біжить і ШВИДКО", "махає черевцем", "— тут уся звістка"],
                   size=9.5, color=INK, anchor="start", bold=False))

    # ── права колонка: що кодують кут і час ──
    bx = 500
    f.append(fitbox(bx, 70, 232, 70,
                    "КУТ θ вилянки до вертикалі\n=\nнапрям на квітку відносно Сонця",
                    size=10.5, fill="#f6efdb", stroke=ZIG, color=INK, bold=True))
    f.append(fitbox(bx, 158, 232, 78,
                    "ТРИВАЛІСТЬ вилянки\n=\nвідстань до квітки\n(довша → далі)",
                    size=10.5, fill="#f6efdb", stroke=ZIG, color=INK, bold=True))
    # стрічка тривалості
    f.append(text(bx + 116, 262, "тривалість вилянки → відстань", 9.5, MUTED, "middle"))
    for i, w in enumerate([18, 40, 70]):
        yb = 280 + i * 26
        f.append(rect(bx + 4, yb, w, 14, fill=ZIG, stroke=ZIG, sw=1, rx=3))
        lab = ["близько", "далі", "ще далі"][i]
        f.append(text(bx + 4 + w + 8, yb + 11, lab, 9, MUTED, "start"))

    # висновок-стрічка внизу
    f.append(fitbox(34, 372, W - 68, 44,
                    "Біг туди-сюди прямою вилянкою, обрамлений почерговими дугами вліво-вправо, виглядає збоку як ЗИГЗАГ —\n"
                    "звідси й ім'я Zigbee: звістка йде далеко не криком, а ПЕРЕКАЗОМ, точнісінько як пакет сіткою сусід-сусідові.",
                    size=10.5, fill="#fbfcfd", stroke="#dde3ea", color=INK))

    render(os.path.join(IMG, "waggle-dance.svg"), W, H, *f)


if __name__ == "__main__":
    fig_stack_layers()
    fig_star_vs_mesh()
    fig_thread_matter_timeline()
    fig_waggle_dance()
    print("OK: figures written to", IMG)
