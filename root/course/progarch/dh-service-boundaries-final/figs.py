# -*- coding: utf-8 -*-
"""Фігури до кроку «Фінал розкрою DH» — парадні двері, стилі швів, повна мапа."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER = "#c77d0a"


def db_cyl(frags, cx, cy, rx=18, ry=6, h=20, fill="#dfe6f6", stroke=NEG, label="своє"):
    """Маленький циліндр «власна БД» під сервісом."""
    frags.append('<path d="M%.1f %.1f v%.1f a%.1f %.1f 0 0 0 %.1f 0 v-%.1f" '
                 'fill="%s" stroke="%s" stroke-width="1.4"/>'
                 % (cx - rx, cy, h, rx, ry, 2 * rx, h, fill, stroke))
    frags.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" '
                 'stroke="%s" stroke-width="1.4"/>' % (cx, cy, rx, ry, "#eef2fb", stroke))
    frags.append(text(cx, cy + 4, label, size=9.5, color=stroke))


# ─────────────────────────────────────────────────────────────────────────────
def fig_front_door():
    """Клієнти → шлюз → BFF → ядро + телеметрія (з fan-out і деградацією)."""
    W, H = 1200, 560
    frags = []

    # ── клієнти (ліворуч) ──
    frags.append(text(120, 74, "Клієнти", size=14, bold=True, color=MUTED))
    b, _, _ = textbox(120, 150, "Застосунок\nна телефоні", size=12.5,
                      fill="#f2f3f5", stroke=MUTED, min_w=150)
    frags.append(b)
    b, _, _ = textbox(120, 300, "Веб-\nдашборд", size=12.5,
                      fill="#f2f3f5", stroke=MUTED, min_w=150)
    frags.append(b)

    # ── шлюз (єдині двері) ──
    gx = 360
    frags.append(rect(gx - 78, 96, 156, 300, fill="#fbf1e0", stroke=AMBER, sw=2.4))
    frags.append(text(gx, 122, "API-шлюз", size=14, bold=True, color=AMBER))
    for i, s in enumerate(["TLS", "перевірка", "токена", "ліміт", "маршрут"]):
        frags.append(text(gx, 158 + i * 44, s, size=12.5, color=INK))

    # клієнти → шлюз (синхронно, суцільна)
    frags.append(arrow(197, 150, gx - 82, 176, color=FIELD, sw=2.2))
    frags.append(arrow(197, 300, gx - 82, 320, color=FIELD, sw=2.2))
    frags.append(text(268, 130, "чекає", size=11, color=FIELD, bold=True))
    frags.append(text(268, 145, "відповіді", size=11, color=FIELD))

    # ── BFF на кожен клієнт ──
    bx = 620
    b, _, _ = textbox(bx, 176, "BFF\nзастосунку", size=12.5,
                      fill="#eaf0fd", stroke=NEG, min_w=150)
    frags.append(b)
    b, _, _ = textbox(bx, 320, "BFF\nдашборда", size=12.5,
                      fill="#eaf0fd", stroke=NEG, min_w=150)
    frags.append(b)
    frags.append(arrow(gx + 82, 176, bx - 82, 176, color=FIELD, sw=2.2))
    frags.append(arrow(gx + 82, 320, bx - 82, 320, color=FIELD, sw=2.2))

    # ── ядро та сервіс телеметрії (праворуч) ──
    cx = 960
    b, _, _ = textbox(cx, 150, "ЯДРО-моноліт\n(керування, твін…)", size=12.5,
                      fill="#eafaf0", stroke=FIELD, sw=2.4, min_w=210)
    frags.append(b)
    b, bw, bh = textbox(cx, 350, "Телеметрія\n— сервіс", size=12.5,
                        fill="#eef2fb", stroke=NEG, sw=2.4, min_w=180)
    frags.append(b)
    db_cyl(frags, cx, 350 + bh / 2 + 12)

    # BFF застосунку → ядро (синхронно) і → телеметрія (з деградацією, пунктир)
    frags.append(arrow(bx + 82, 168, cx - 108, 150, color=FIELD, sw=2.2))
    frags.append(text(bx + 205, 132, "склад екрана", size=11, color=MUTED))
    frags.append(arrow(bx + 82, 195, cx - 92, 330, color=NEG, sw=2.0))
    # підпис читання — унизу, ПОЗА діагоналлю стрілки
    frags.append(mtext(795, 452, "читання з телеметрії —\nтаймаут + запас (через виявлення)",
                       size=11.5, color=NEG, lh=1.3))

    frags.append(text(W / 2, H - 20,
                      "Одні двері й одна перевірка токена на межі; кожен BFF збирає рівно свій екран, "
                      "а читання з телеметрії тепер іде мережею — з таймаутом і запасом.",
                      size=12.5, color=MUTED))

    render(os.path.join(IMG, "front-door.svg"), W, H, *frags,
           title="Парадні двері: шлюз, BFF і склад екрана через межу")


# ─────────────────────────────────────────────────────────────────────────────
def fig_seam_styles():
    """Кожен шов DH: синхронний чи асинхронний, чому, і прихована ціна."""
    W, H = 1200, 560
    frags = []

    cols = [26, 470, 720, 1000, W - 20]     # межі 4 колонок
    heads = ["Шов", "Стиль", "Чому саме так", "Прихована ціна"]
    cc = [(cols[i] + cols[i + 1]) / 2 for i in range(4)]

    head_bot = 92
    for i, h in enumerate(heads):
        frags.append(text(cc[i], 68, h, size=13.5, color=INK, bold=True))
    frags.append(line(cols[0], head_bot, cols[4], head_bot, color=MUTED, sw=1.4))
    for x in cols[1:4]:
        frags.append(line(x, 52, x, H - 40, color="#e2e5ea", sw=1))

    rows = [
        ("Клієнт → шлюз → ядро", "синхронно", FIELD,
         "людина натиснула й дивиться на екран", "ланцюг доступності"),
        ("Ядро → телеметрія", "асинхронно · подія", NEG,
         "факт летить сам, ядро не чекає запису", "зрештою узгоджене"),
        ("BFF → телеметрія (читання)", "синхронно, але терпить", AMBER,
         "екран хоче зараз — та проживе без виміру", "таймаут + запас"),
        ("Ядро ⇄ хаб у домі", "команда вниз · подія вгору", NEG,
         "у домі буває поганий Wi-Fi", "ретрай + ідемпотентність"),
        ("Білінг → платіжний провайдер", "синхронно за ACL", FIELD,
         "треба тверде «так / ні» від чужого", "чужа мова за стіною"),
        ("Сповіщення → пуш", "асинхронно · вистрелив-забув", NEG,
         "доставку листа не блокуємо командою", "ACL на вихід"),
    ]
    row_h = 68
    for i, (seam, style, sc, why, cost) in enumerate(rows):
        cy = head_bot + row_h / 2 + i * row_h
        if i:
            frags.append(line(cols[0], head_bot + i * row_h, cols[4],
                              head_bot + i * row_h, color="#eef0f3", sw=1))
        frags.append(mtext(cols[0] + 12, cy + 5, seam, size=12.5, color=INK,
                           anchor="start", bold=True))
        # чип стилю
        solid = sc is FIELD
        b, _, _ = textbox(cc[1], cy, style, size=11.5,
                          fill="#eafaf0" if solid else "#eef2fb",
                          stroke=sc, sw=1.8, min_w=190)
        frags.append(b)
        frags.append(mtext(cols[2] + 12, cy + 5, why, size=12, color=MUTED,
                           anchor="start"))
        frags.append(mtext(cols[3] + 12, cy + 5, cost, size=12, color=INK,
                           anchor="start"))

    frags.append(text(W / 2, H - 16,
                      "Стиль обирають на КОЖЕН шов окремо — тому DH виходить мішаний: "
                      "синхронний там, де людина чекає, асинхронний там, де факт може летіти сам.",
                      size=12.5, color=MUTED))

    render(os.path.join(IMG, "seam-styles.svg"), W, H, *frags,
           title="Кожен шов дістає свій стиль інтеграції")


# ─────────────────────────────────────────────────────────────────────────────
def fig_final_topology():
    """Уся фінальна мапа DH: край, двері, ядро+супутники, зовнішнє, шви."""
    W, H = 1280, 780
    frags = []

    def chip(cx, cy, label, fillc, strokec, w=132, size=12):
        b, bw, bh = textbox(cx, cy, label, size=size, fill=fillc, stroke=strokec,
                            sw=1.4, min_w=w)
        frags.append(b)
        return bw, bh

    # ── смуги-заголовки ──
    bands = [(90, "Край і клієнти"), (330, "Парадні двері"),
             (640, "Ядро-моноліт"), (940, "Супутники-сервіси"), (1160, "Зовнішнє")]
    for x, name in bands:
        frags.append(text(x, 62, name, size=12.5, bold=True, color=MUTED))

    # ── КРАЙ: клієнти + хаб ──
    chip(90, 130, "Застосунок\n· дашборд", "#f2f3f5", MUTED, w=140)
    chip(90, 300, "ДІМ · Хаб", "#fff8e1", INK, w=140)
    frags.append(line(150, 230, 150, 360, color=MUTED, sw=1.3, dash="5,6"))
    frags.append(text(90, 250, "межа машини", size=10, color=MUTED))

    # ── ДВЕРІ: шлюз + BFF ──
    frags.append(rect(268, 96, 130, 150, fill="#fbf1e0", stroke=AMBER, sw=2.2))
    frags.append(text(333, 120, "API-шлюз", size=12.5, bold=True, color=AMBER))
    frags.append(text(333, 150, "токен · ліміт", size=11, color=INK))
    frags.append(text(333, 172, "маршрут", size=11, color=INK))
    chip(333, 300, "BFF-и\nна клієнт", "#eaf0fd", NEG, w=132)

    # ── ЯДРО: 6 модулів ──
    frags.append(rect(500, 90, 300, 470, fill="#f4fbf6", stroke=FIELD, sw=3))
    frags.append(text(650, 116, "ЯДРО — один процес, одна база", size=12, bold=True, color=FIELD))
    mods = ["Керування", "Твін", "Автоматизації", "Сповіщення", "Білінг", "Ідентичність"]
    mxs = [575, 725]
    mys = [175, 265, 355]
    for i, m in enumerate(mods):
        chip(mxs[i % 2], mys[i // 2], m, "#eafaf0", FIELD, w=132, size=11.5)
    frags.append(text(650, 470, "спільне ядро: DeviceId, HomeId", size=10.5, color=MUTED))
    frags.append(text(650, 520, "виявлення сервісів — реєстр,", size=10.5, color=MUTED))
    frags.append(text(650, 537, "де живі супутники", size=10.5, color=MUTED))

    # ── нова межа машини перед супутниками ──
    frags.append(line(860, 90, 860, 620, color=POS, sw=1.5, dash="6,6"))
    frags.append(text(862, 82, "нова межа машини", size=10.5, color=POS, bold=True))

    # ── СУПУТНИКИ: телеметрія, відео ──
    _, bh1 = chip(960, 200, "Телеметрія\n— сервіс", "#eef2fb", NEG, w=150)
    db_cyl(frags, 960, 200 + bh1 / 2 + 12)
    _, bh2 = chip(960, 420, "Відео\n— сервіс", "#eef2fb", NEG, w=150)
    db_cyl(frags, 960, 420 + bh2 / 2 + 12)

    # ── ЗОВНІШНЄ: платіжний (верхня смуга), пуш (нижня смуга) — щоб лінії йшли повз супутники ──
    chip(1170, 120, "Платіжний\nпровайдер", "#f2f3f5", MUTED, w=150)
    frags.append(text(1170, 165, "за ACL", size=10, color=MUTED))
    chip(1170, 520, "Пуш\nApple / Google", "#f2f3f5", MUTED, w=150)
    frags.append(text(1170, 565, "ACL на вихід", size=10, color=MUTED))

    # ── ШВИ (суцільна = синхронно, пунктир = асинхронно) ──
    # клієнти → шлюз (синх)
    frags.append(arrow(162, 130, 264, 150, color=FIELD, sw=2.0))
    # шлюз → BFF (синх)
    frags.append(arrow(333, 248, 333, 268, color=FIELD, sw=2.0))
    # BFF → ядро (синх)
    frags.append(arrow(400, 300, 496, 282, color=FIELD, sw=2.0))
    # ядро ⇢ телеметрія (подія, асинх) — коротка стрілка праворуч від ядра
    frags.append(line(802, 205, 884, 200, color=NEG, sw=1.9, dash="7,6"))
    frags.append(text(843, 182, "потік подій", size=10.5, color=NEG, bold=True))
    frags.append('<polygon points="884,200 872,197 875,208" fill="%s"/>' % NEG)
    # ядро ⇢ відео (окремі шляхи, тонкий пунктир)
    frags.append(line(802, 405, 884, 415, color=MUTED, sw=1.4, dash="4,7"))
    # хаб ⇄ ядро — вниз від хаба, попід BFF, у ядро (щоб не різати чип BFF)
    frags.append(line(150, 320, 150, 470, color=NEG, sw=1.7, dash="7,6"))
    frags.append(line(150, 470, 496, 470, color=NEG, sw=1.7, dash="7,6"))
    frags.append(text(300, 458, "команда · подія", size=10, color=NEG))
    # ядро → платіжний (синх за ACL) — верхньою смугою, повз телеметрію
    frags.append(arrow(802, 140, 1092, 122, color=FIELD, sw=1.8))
    # ядро ⇢ пуш (асинх) — нижньою смугою, попід відео
    frags.append(line(802, 430, 1092, 516, color=NEG, sw=1.6, dash="7,6"))
    frags.append('<polygon points="1092,516 1080,510 1080,522" fill="%s"/>' % NEG)

    # ── легенда ──
    ly = H - 34
    frags.append(line(40, ly, 84, ly, color=FIELD, sw=2.4))
    frags.append(text(92, ly + 4, "синхронно — чекає відповіді", size=11.5,
                      color=FIELD, anchor="start", bold=True))
    frags.append(line(420, ly, 464, ly, color=NEG, sw=2.0, dash="7,6"))
    frags.append(text(472, ly + 4, "асинхронно — факт летить сам", size=11.5,
                      color=NEG, anchor="start", bold=True))
    frags.append(text(820, ly + 4,
                      "ні «мікросервіси», ні «моноліт» — ядро з двома супутниками й одними дверима",
                      size=11.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "final-topology.svg"), W, H, *frags,
           title="Уся фінальна мапа Digital Homes")


# ─────────────────────────────────────────────────────────────────────────────
def fig_topo_one_source():
    """Одне джерело топології — двоє читачів: сторож і картинка (стиль живе в даних)."""
    W, H = 1200, 560
    frags = []

    # ── джерело (ліворуч) ──
    sx, sy = 250, 300
    frags.append(rect(sx - 150, sy - 120, 300, 240, fill="#fbf1e0", stroke=AMBER, sw=2.6))
    frags.append(text(sx, sy - 92, "topology", size=15, bold=True, color=AMBER))
    frags.append(text(sx, sy - 70, "одне джерело правди", size=11, color=MUTED))
    for i, s in enumerate(["9 розгортань + свої бази",
                           "кожен шов + СТИЛЬ",
                           "async-шви + топіки"]):
        frags.append(text(sx, sy - 28 + i * 34, s, size=12.5, color=INK))
    frags.append(text(sx, sy + 98, "(стиль — поле в даних)", size=11, color=AMBER, italic=True))

    # ── читач 1: сторож (праворуч угорі) ──
    gx, gy = 905, 168
    frags.append(rect(gx - 178, gy - 80, 356, 160, fill="#fdecea", stroke=POS, sw=2.4))
    frags.append(text(gx, gy - 54, "СТОРОЖ — валить збірку", size=13.5, bold=True, color=POS))
    for i, s in enumerate(["ребро поза мапою",
                           "чужа база (не своя)",
                           "async-шов + синхронний виклик"]):
        frags.append(text(gx, gy - 24 + i * 27, "✗  " + s, size=12, color=INK))
    frags.append(text(gx, gy + 66, "exit 1 → merge заблоковано", size=11.5, color=POS))

    # ── читач 2: картинка (праворуч унизу) ──
    px, py = 905, 438
    frags.append(rect(px - 178, py - 80, 356, 160, fill="#eafaf0", stroke=FIELD, sw=2.4))
    frags.append(text(px, py - 54, "SVG-топологія", size=13.5, bold=True, color=FIELD))
    frags.append(line(px - 152, py - 22, px - 104, py - 22, color=INK, sw=2.4))
    frags.append(text(px - 92, py - 18, "суцільна = синхронно", size=12, color=INK, anchor="start"))
    frags.append(line(px - 152, py + 12, px - 104, py + 12, color=INK, sw=2.0, dash="7,6"))
    frags.append(text(px - 92, py + 16, "пунктир = асинхронно", size=12, color=INK, anchor="start"))
    frags.append(text(px, py + 60, "дах стрілки — зі СТИЛЮ в даних", size=11.5, color=FIELD))

    # ── стрілки-читачі ──
    frags.append(arrow(sx + 152, sy - 46, gx - 182, gy + 26, color=POS, sw=2.4))
    frags.append(text(566, 200, "стереже", size=13, bold=True, color=POS))
    frags.append(arrow(sx + 152, sy + 46, px - 182, py - 26, color=FIELD, sw=2.4))
    frags.append(text(566, 398, "малює", size=13, bold=True, color=FIELD))

    frags.append(mtext(W / 2, H - 30,
                       ["Зміниш стиль шва в даних — зрушаться обоє: і пунктир на картинці, і вимога сторожа.",
                        "Розійтися нема куди ні наявності стрілки, ні її стилю."],
                       size=12.5, color=MUTED, lh=1.3))

    render(os.path.join(IMG, "topo-one-source.svg"), W, H, *frags,
           title="Одне джерело топології — сторож і картинка з тих самих даних")


# ─────────────────────────────────────────────────────────────────────────────
def fig_service_gate():
    """Три сервісні перевірки: будь-яка червона → збірка червона, exit 1."""
    W, H = 1240, 560
    frags = []

    # ── джерело ──
    frags.append(rect(40, 208, 250, 134, fill="#fbf1e0", stroke=AMBER, sw=2.4))
    frags.append(mtext(165, 250, "topology\n(розгортання + шви)\n+ сканер коду сервісів",
                       size=12.5, color=INK, lh=1.45, bold=True))

    # ── три гейти ──
    gates = [
        ("1 · ребро поза мапою", "video → core", 122),
        ("2 · чужа база", "gateway → telemetry_db", 285),
        ("3 · async-шов + синхронний виклик", "core → telemetry", 448),
    ]
    for title_g, ex, gy in gates:
        frags.append(rect(470, gy - 50, 384, 100, fill="#fdecea", stroke=POS, sw=2.2))
        frags.append(text(672, gy - 20, title_g, size=12.5, bold=True, color=INK))
        frags.append(text(672, gy + 6, ex, size=13, color=POS))
        frags.append(text(506, gy + 8, "✗", size=23, bold=True, color=POS))
        frags.append(arrow(292, 275, 466, gy, color=MUTED, sw=1.8))
        frags.append(arrow(856, gy, 1000, 275, color=POS, sw=2.0))

    # ── червоний вузол ──
    frags.append(rect(1002, 203, 212, 144, fill="#c0392b", stroke=POS, sw=2))
    frags.append(mtext(1108, 248, "ЗБІРКА ЧЕРВОНА\nexit 1\nmerge заблоковано",
                       size=13, color="#ffffff", lh=1.5, bold=True))

    # ── зелена лінія: усе чисто ──
    frags.append(line(470, H - 28, 856, H - 28, color=FIELD, sw=2.2))
    frags.append(text(663, H - 34, "жодного ✗  →  топологія DH тримається", size=12.5,
                      color=FIELD, bold=True))

    render(os.path.join(IMG, "service-gate.svg"), W, H, *frags,
           title="Сервісний сторож: три перевірки, будь-яка валить збірку")


if __name__ == "__main__":
    fig_front_door()
    fig_seam_styles()
    fig_final_topology()
    fig_topo_one_source()
    fig_service_gate()
    print("OK: front-door.svg, seam-styles.svg, final-topology.svg, "
          "topo-one-source.svg, service-gate.svg")
