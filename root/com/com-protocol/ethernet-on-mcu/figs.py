# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори-акценти поверх палітри svgkit
WIRE = "#0e6b8a"   # дріт / фізика — холодний бірюзовий
WIREBG = "#e6f4f8"
WIREST = "#2a93b5"
COPPER = "#b9560f"  # мідь / живлення PoE — теплий
COPBG = "#fff1e6"
COPST = "#d2772a"


def rj45(p, x, y, label="RJ45 + магнітика"):
    """Спрощений роз'єм RJ45 із защіпкою, центр верхнього краю в (x, y)."""
    w, h = 64, 50
    p.append(rect(x - w / 2, y, w, h, fill="#eceff4", stroke=INK, sw=1.8, rx=4))
    # защіпка
    p.append(rect(x - 8, y - 8, 16, 10, fill="#dfe3ea", stroke=INK, sw=1.4, rx=2))
    # контакти
    for i in range(8):
        cx = x - 28 + i * 8
        p.append(line(cx, y + 6, cx, y + 20, color="#caa24a", sw=1.6))
    p.append(text(x, y + h + 16, label, size=10, color=INK, bold=True))


# ── wired-anatomy: МК + MAC + PHY + RJ45 → кабель ─────────────────────────────
def fig_wired_anatomy():
    W, H = 900, 380
    p = []
    # рамка МК
    p.append(rect(50, 80, 430, 220, fill="#fbfcff", stroke=INK, sw=2.2, rx=12))
    p.append(text(70, 102, "Мікроконтролер", size=11, color=MUTED, anchor="start", bold=True))

    p.append(fitbox(80, 130, 150, 70, "Ядро + lwIP\n(сокети, TCP/IP)", size=12, fill="#fbecec", stroke=POS, sw=1.8, bold=True, color=POS))
    p.append(fitbox(280, 130, 160, 70, "MAC\n(контролер кадрів)", size=12, fill=WIREBG, stroke=WIREST, sw=1.8, bold=True, color=WIRE))
    p.append(arrow(230, 165, 278, 165, color=INK, sw=2))

    # зовнішній PHY
    p.append(rect(540, 110, 170, 110, fill=WIREBG, stroke=WIREST, sw=2.2, rx=10))
    p.append(text(625, 138, "PHY", size=14, color=WIRE, bold=True))
    p.append(text(625, 158, "(приймач-передавач", size=10, color=INK))
    p.append(text(625, 173, "сигналу в мідь)", size=10, color=INK))
    p.append(text(625, 198, "окремий чип", size=10, color=MUTED, italic=True))
    p.append(arrow(480, 165, 538, 165, color=INK, sw=2.2))
    p.append(text(509, 155, "RMII", size=10, color=MUTED, bold=True))
    p.append(text(509, 186, "(9 ліній)", size=9, color=MUTED))

    # RJ45 + кабель
    rj45(p, 800, 130)
    p.append(arrow(710, 165, 768, 165, color=INK, sw=2))
    p.append(line(800, 240, 800, 320, color=WIRE, sw=3))
    p.append(line(800, 320, 700, 350, color=WIRE, sw=3))
    p.append(text(760, 345, "вита пара → мережа", size=10, color=WIRE, anchor="end", bold=True))

    p.append(text(W / 2, 370, "ланцюг дроту: програма → MAC → PHY → роз'єм → кабель — кожна ланка робить свою справу",
                  size=11.5, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "wired-anatomy.svg"), W, H, *p,
           title="Дротовий Ethernet на МК: ланцюг від програми до кабелю")


# ── three-ways: три способи зробити Ethernet ──────────────────────────────────
def fig_three_ways():
    W, H = 940, 430
    p = []
    cols = [
        (60,  "Внутрішній MAC + зовнішній PHY", WIRE, WIREBG, WIREST,
         ["MAC у самому МК", "PHY окремим чипом", "шина MII / RMII",
          "стек — lwIP у МК", "10/100, висока швидкість", "більше ніжок, складніше"]),
        (350, "SPI-Ethernet: W5500", FIELD, "#eef6ef", FIELD,
         ["MAC + PHY + стек у чипі", "TCP/IP усередині (hardwired)", "до МК — лише по SPI",
          "lwIP НЕ потрібен", "кілька сокетів у залізі", "проста плата, мало ніжок"]),
        (640, "SPI-Ethernet: ENC28J60", COPPER, COPBG, COPST,
         ["лише MAC + PHY", "стека всередині немає", "до МК — по SPI",
          "стек — lwIP у МК", "лише 10 Мбіт/с", "найпростіше, найповільніше"]),
    ]
    cw = 250
    for x, head, col, fill, st, items in cols:
        p.append(rect(x, 80, cw, 300, fill=fill, stroke=st, sw=2, rx=12))
        p.append(fitbox(x + 14, 92, cw - 28, 44, head, size=12.5, fill=BG, stroke=st, sw=1.6, bold=True, color=col))
        for i, ln in enumerate(items):
            p.append(text(x + 18, 168 + i * 32, "• " + ln, size=11, color=INK, anchor="start"))

    p.append(text(W / 2, 410, "три двері до мережі: різний поділ праці між МК і чипом, але назовні — той самий Ethernet",
                  size=11.5, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "three-ways.svg"), W, H, *p,
           title="Три способи дати МК дротову мережу")


# ── lwip-flow: кадр знизу вгору до сокета ─────────────────────────────────────
def fig_lwip_flow():
    W, H = 760, 520
    p = []
    layers = [
        ("Ваш код: сокети", "send() / recv() — байтовий потік", "#fbecec", POS),
        ("lwIP: TCP / UDP", "порти, надійність, черги", "#eef6ef", FIELD),
        ("lwIP: IP", "адреси, маршрут пакета", "#e9eefb", NEG),
        ("MAC", "збирає й перевіряє кадр (Ethernet frame)", WIREBG, WIRE),
        ("PHY", "біти ⇄ напруга у міді", COPBG, COPPER),
    ]
    x, w = 150, 460
    y = 80
    bh, gap = 64, 14
    cys = []
    for i, (head, sub, fill, col) in enumerate(layers):
        yy = y + i * (bh + gap)
        p.append(rect(x, yy, w, bh, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(x + 16, yy + 26, head, size=13, color=col, anchor="start", bold=True))
        p.append(text(x + 16, yy + 47, sub, size=10.5, color=INK, anchor="start"))
        cys.append((yy, yy + bh))

    # стрілки вниз (передача) і вгору (прийом)
    for i in range(len(layers) - 1):
        y1 = cys[i][1]
        y2 = cys[i + 1][0]
        p.append(arrow(x - 28, y1 + 2, x - 28, y2 - 2, color=POS, sw=2))      # вниз: передаємо
        p.append(arrow(x + w + 28, y2 - 2, x + w + 28, y1 + 2, color=NEG, sw=2))  # вгору: приймаємо
    p.append(text(x - 28, y - 12, "передача ↓", size=10, color=POS, bold=True))
    p.append(text(x + w + 28, y - 12, "↑ прийом", size=10, color=NEG, bold=True))

    # кабель унизу
    p.append(line(x + w / 2, cys[-1][1], x + w / 2, cys[-1][1] + 24, color=COPPER, sw=3))
    p.append(text(x + w / 2, cys[-1][1] + 40, "кабель", size=10, color=COPPER, bold=True))

    p.append(text(W / 2, 505, "той самий стек, що й по Wi-Fi: міняється лише найнижча ланка — як біти йдуть у середовище",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "lwip-flow.svg"), W, H, *p,
           title="Шлях даних крізь lwIP: від сокета до міді")


# ── wire-vs-radio: коли дріт кращий за радіо ──────────────────────────────────
def fig_wire_vs_radio():
    W, H = 860, 360
    p = []
    # радіо
    p.append(rect(60, 90, 360, 210, fill="#f3f3f3", stroke="#bdbdbd", sw=1.8, rx=12))
    p.append(text(240, 116, "Радіо (Wi-Fi)", size=13, color=MUTED, bold=True))
    for i, ln in enumerate(["зручно: без кабелю", "затримка «плаває»", "ділить ефір із сусідами",
                            "перешкоди, завмирання", "живлення — окремо"]):
        p.append(text(82, 148 + i * 28, "• " + ln, size=11.5, color=INK, anchor="start"))

    # дріт
    p.append(rect(440, 90, 360, 210, fill=WIREBG, stroke=WIREST, sw=2.2, rx=12))
    p.append(text(620, 116, "Дріт (Ethernet)", size=13, color=WIRE, bold=True))
    for i, ln in enumerate(["надійний, без завад", "затримка передбачувана", "детермінізм (час гарантовано)",
                            "живлення в тому ж кабелі (PoE)", "робоча конячка промисловості"]):
        p.append(text(462, 148 + i * 28, "• " + ln, size=11.5, color=INK, anchor="start", bold=(i in (2, 3))))

    p.append(arrow(420, 195, 438, 195, color=INK, sw=2.6))
    p.append(text(W / 2, 330, "де ціна збою висока або час критичний — дріт виграє саме передбачуваністю, не швидкістю",
                  size=11, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "wire-vs-radio.svg"), W, H, *p,
           title="Коли дріт кращий за радіо")


# ── poe: живлення по кабелю, класи ────────────────────────────────────────────
def fig_poe():
    W, H = 880, 380
    p = []
    # джерело (світч) → кабель → пристрій
    p.append(fitbox(60, 150, 150, 80, "Світч-джерело\n(PSE)", size=12, fill="#eef6ef", stroke=FIELD, sw=2, bold=True, color=FIELD))
    p.append(fitbox(670, 150, 150, 80, "МК-пристрій\n(PD)", size=12, fill="#fbecec", stroke=POS, sw=2, bold=True, color=POS))

    # кабель: дані + живлення
    p.append(line(210, 178, 670, 178, color=WIRE, sw=4))
    p.append(text(440, 168, "дані (вита пара)", size=11, color=WIRE, bold=True))
    p.append(line(210, 204, 670, 204, color=COPPER, sw=4))
    p.append(text(440, 224, "живлення по тих самих парах (центр-відводи магнітики)", size=10.5, color=COPPER, bold=True))

    # таблиця класів
    p.append(rect(220, 250, 440, 110, fill=COPBG, stroke=COPST, sw=1.6, rx=10))
    p.append(text(440, 272, "Стандарти й стеля живлення (на пристрої)", size=11.5, color=COPPER, bold=True))
    rows = [
        ("802.3af (PoE, Type 1)", "до ~13 Вт"),
        ("802.3at (PoE+, Type 2)", "до ~25 Вт"),
        ("802.3bt (Type 3/4)", "до ~70 Вт"),
    ]
    for i, (a, b) in enumerate(rows):
        yy = 296 + i * 20
        p.append(text(240, yy, a, size=10.5, color=INK, anchor="start"))
        p.append(text(640, yy, b, size=10.5, color=INK, anchor="end", bold=True))

    p.append(text(W / 2, 120, "один кабель несе і мережу, і живлення — пристрою не треба окремого блока",
                  size=11.5, color=INK, italic=True, bold=True))
    render(os.path.join(OUT, "poe.svg"), W, H, *p,
           title="PoE: живлення тим самим кабелем, що й дані")


if __name__ == "__main__":
    fig_wired_anatomy()
    fig_three_ways()
    fig_lwip_flow()
    fig_wire_vs_radio()
    fig_poe()
    print("OK: figures written to", OUT)
