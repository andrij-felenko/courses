# -*- coding: utf-8 -*-
"""Фігури до теми «MAC, IP і ARP».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Два рівні адрес: вшита MAC і призначена IP ───────────────────────────
def fig_two_levels():
    """Дві адреси на одному пристрої: MAC випалена в чіп на заводі (незмінна,
    плоска), IP видана мережею (тимчасова, з номером підмережі). Видно, що
    одна каже ХТО апаратно, друга — ДЕ в мережі."""
    W, H = 760, 380
    f = [text(W / 2, 30, "Дві адреси на одному пристрої — і навіщо обидві", size=17, bold=True)]

    # пристрій посередині
    dev, dw, dh = textbox(W / 2, 200, "Пристрій\n(Wi-Fi/Ethernet)", size=13, bold=True,
                          fill="#eef3ff", stroke=NEG, min_w=170)
    f.append(dev)

    # ліворуч: MAC — вшита, заводська
    b1 = rect(40, 95, 250, 210, fill="#fdecea", stroke=POS, sw=1.6)
    f.append(b1)
    f.append(text(165, 122, "MAC — апаратна", size=14, bold=True, color=POS))
    f.append(text(165, 144, "канальний рівень", size=11, color=MUTED))
    f.append(fitbox(60, 158, 210, 30, "DE:AD:BE:EF:12:34", size=14, fill=BG, stroke=POS, sw=1.2))
    f.append(mtext(165, 212, ["• випалена в чіп на заводі",
                              "• незмінна, своя в кожного",
                              "• плоска: лише «хто», не «де»"],
                   size=11, anchor="middle", color=INK, lh=1.55))
    # стрілка від MAC до пристрою
    f.append(arrow(290, 200, W / 2 - dw / 2, 200, color=POS))

    # праворуч: IP — призначена мережею
    b2 = rect(470, 95, 250, 210, fill="#eafaf0", stroke=FIELD, sw=1.6)
    f.append(b2)
    f.append(text(595, 122, "IP — логічна", size=14, bold=True, color=FIELD))
    f.append(text(595, 144, "мережевий рівень", size=11, color=MUTED))
    f.append(fitbox(490, 158, 210, 30, "192.168.1.42", size=14, fill=BG, stroke=FIELD, sw=1.2))
    f.append(mtext(595, 212, ["• видана мережею (DHCP)",
                              "• змінюється з місцем",
                              "• ієрархічна: підмережа + вузол"],
                   size=11, anchor="middle", color=INK, lh=1.55))
    # стрілка від IP до пристрою
    f.append(arrow(470, 200, W / 2 + dw / 2, 200, color=FIELD))

    f.append(text(W / 2, 350, "MAC каже, ХТО на дроті; IP каже, ДЕ він у топології мереж.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "two-levels.svg"), W, H, *f)


# ── 2. Кадр vs пакет: конверт у конверті ────────────────────────────────────
def fig_frame_vs_packet():
    """Вкладеність: байти даних кладуть у IP-пакет (адреси IP), а той цілком —
    у кадр Ethernet/Wi-Fi (адреси MAC). Видно, що пакет їде через усю мережу
    незмінним, а кадр живе один крок і на кожній ланці новий."""
    W, H = 760, 400
    f = [text(W / 2, 30, "Кадр і пакет: лист у конверті для одного кроку", size=17, bold=True)]

    # зовнішній: кадр (канальний)
    f.append(rect(50, 70, 660, 230, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(80, 96, "КАДР  (Ethernet / Wi-Fi)  — адреси MAC", size=13, bold=True, color=POS))
    f.append(fitbox(70, 112, 150, 46, "MAC отримувача\n(наступний крок)", size=10,
                    fill=BG, stroke=POS, sw=1.1))
    f.append(fitbox(228, 112, 150, 46, "MAC відправника\n(цей пристрій)", size=10,
                    fill=BG, stroke=POS, sw=1.1))
    f.append(fitbox(640, 112, 56, 46, "CRC", size=10, fill=BG, stroke=POS, sw=1.1))

    # внутрішній: пакет (мережевий)
    f.append(rect(95, 170, 540, 110, fill="#eafaf0", stroke=FIELD, sw=1.6))
    f.append(text(120, 194, "ПАКЕТ  (IP)  — адреси IP", size=13, bold=True, color=FIELD))
    f.append(fitbox(112, 210, 140, 44, "IP отримувача\n(кінцевий вузол)", size=10,
                    fill=BG, stroke=FIELD, sw=1.1))
    f.append(fitbox(264, 210, 140, 44, "IP відправника\n(джерело)", size=10,
                    fill=BG, stroke=FIELD, sw=1.1))
    # корисні дані всередині пакета
    f.append(fitbox(420, 210, 200, 44, "ДАНІ\n(TCP/UDP → застосунок)", size=10,
                    fill="#fff7e6", stroke=MUTED, sw=1.1))

    f.append(text(W / 2, 332, "Пакет (зелений) їде через усю мережу НЕЗМІННИМ — кінцеві IP сталі.",
                  size=12, italic=True, color=MUTED))
    f.append(text(W / 2, 352, "Кадр (червоний) живе ОДИН крок: на кожній ланці його зривають і пакують наново з новими MAC.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "frame-vs-packet.svg"), W, H, *f)


# ── 3. Обмін ARP: широкомовний запит → адресна відповідь ────────────────────
def fig_arp_exchange():
    """Серце теми. A знає IP цілі, але не знає її MAC. Кричить УСІМ
    (broadcast) «у кого 192.168.1.42?»; усі чують, відповідає лише власник —
    особисто (unicast) «це я, ось мій MAC»."""
    W, H = 760, 440
    f = [text(W / 2, 30, "ARP: як знайти MAC за відомим IP у своїй мережі", size=17, bold=True)]

    # відправник A ліворуч
    ax, ay = 110, 230
    f.append(circle(ax, ay, 40, fill="#eef3ff", stroke=NEG, sw=2))
    f.append(text(ax, ay - 4, "A", size=20, bold=True, color=NEG))
    f.append(text(ax, ay + 16, "я", size=10, color=MUTED))
    f.append(fitbox(40, ay + 48, 140, 40, "знаю IP цілі\nMAC — ні", size=10,
                    fill=BG, stroke=NEG, sw=1.1))

    # три отримувачі праворуч (B, C — власник, D)
    rx = 600
    ys = [110, 230, 350]
    names = ["B", "C", "D"]
    owner = 1  # C — власник IP
    for i, (yy, nm) in enumerate(zip(ys, names)):
        is_owner = (i == owner)
        col = FIELD if is_owner else MUTED
        fillc = "#eafaf0" if is_owner else "#f4f6f8"
        f.append(circle(rx, yy, 34, fill=fillc, stroke=col, sw=2))
        f.append(text(rx, yy + 6, nm, size=18, bold=True, color=col))
        if is_owner:
            f.append(fitbox(rx + 44, yy - 18, 120, 36, "це мій IP\n.42", size=10,
                            fill="#eafaf0", stroke=FIELD, sw=1.1))

    # КРОК 1: широкомовний запит до всіх (червоні стрілки)
    for yy in ys:
        f.append(arrow(ax + 42, ay - 18, rx - 38, yy, color=POS, sw=1.6))
    f.append(fitbox(255, 150, 250, 56,
                    "1. ЗАПИТ — усім (broadcast)\nMAC-ціль: FF:FF:FF:FF:FF:FF\n«у кого 192.168.1.42?»",
                    size=11, fill="#fdecea", stroke=POS, sw=1.3, bold=False))

    # КРОК 2: адресна відповідь лише від власника (зелена стрілка назад)
    f.append(arrow(rx - 38, ys[owner] + 14, ax + 40, ay + 14, color=FIELD, sw=2))
    f.append(fitbox(250, 300, 260, 56,
                    "2. ВІДПОВІДЬ — особисто A (unicast)\n«.42 → це мій MAC C0:FF:EE:...»\nтепер A знає MAC цілі",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.3))

    f.append(text(W / 2, 422, "Питають усіх; відповідає тільки власник адреси — і теж особисто.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "arp-exchange.svg"), W, H, *f)


# ── 4. Своя підмережа vs через шлюз: кого питати ARP ────────────────────────
def fig_local_vs_gateway():
    """Рішення перед відправкою: маска показує, чи ціль у моїй підмережі.
    Так → ARP-имо саму ціль і шлемо прямо. Ні → ARP-имо ШЛЮЗ і віддаємо кадр
    йому (а IP-пакет усе одно адресований кінцевому вузлу)."""
    W, H = 770, 440
    f = [text(W / 2, 28, "Кого питати ARP: ціль у моїй мережі — чи маршрутизатор?", size=16, bold=True)]

    # вузол-джерело вгорі
    f.append(textbox(W / 2, 78, "Хочу надіслати на IP цілі", size=13, bold=True,
                     fill="#eef3ff", stroke=NEG, min_w=260)[0])

    # ромб-рішення
    cx, cy = W / 2, 158
    f.append('<polygon points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" fill="#fff7e6" stroke="%s" stroke-width="1.6"/>'
             % (cx, cy - 38, cx + 150, cy, cx, cy + 38, cx - 150, cy, MUTED))
    f.append(mtext(cx, cy - 4, ["ціль у МОЇЙ підмережі?", "(IP & маска збігаються)"],
                   size=11, anchor="middle"))
    f.append(arrow(W / 2, 96, W / 2, cy - 40, color=NEG))

    # ТАК — ліворуч
    f.append(text(cx - 160, cy - 6, "ТАК", size=12, bold=True, color=FIELD, anchor="end"))
    f.append(arrow(cx - 150, cy, 200, cy, color=FIELD))
    f.append(fitbox(50, cy + 24, 300, 86,
                    "ARP саму ЦІЛЬ:\n«у кого цей IP?» → її MAC\n\nкадр шлю ПРЯМО на MAC цілі\nодин крок — і на місці",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.3))

    # НІ — праворуч
    f.append(text(cx + 160, cy - 6, "НІ (інша мережа)", size=12, bold=True, color=POS, anchor="start"))
    f.append(arrow(cx + 150, cy, 570, cy, color=POS))
    f.append(fitbox(420, cy + 24, 300, 86,
                    "ARP ШЛЮЗ (маршрутизатор):\nберу його MAC\n\nкадр — на MAC шлюзу,\nале IP-пакет — на кінцевий вузол",
                    size=11, fill="#fdecea", stroke=POS, sw=1.3))

    f.append(text(W / 2, 398, "ARP працює лише в МЕЖАХ однієї підмережі — широкомовний крик не виходить за маршрутизатор.",
                  size=12, italic=True, color=MUTED))
    f.append(text(W / 2, 418, "За межі веде маршрутизація: кадр віддаєш шлюзу, а він передає пакет далі.",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "local-vs-gateway.svg"), W, H, *f)


# ── 5. ARP-таблиця: кеш відповідностей IP→MAC ───────────────────────────────
def fig_arp_table():
    """Чому не питати щоразу: відповіді IP→MAC осідають у таблиці-кеші на
    кілька хвилин. Перед відправкою — погляд у кеш: є запис → шлю одразу;
    нема → один ARP-запит, далі знову з кеша."""
    W, H = 760, 390
    f = [text(W / 2, 30, "ARP-таблиця: кеш, щоб не питати щоразу", size=17, bold=True)]

    # таблиця ліворуч
    tx, ty, tw = 50, 80, 360
    rows = [("IP", "MAC", "вік"),
            ("192.168.1.1", "A4:B1:..:01", "12 c"),
            ("192.168.1.42", "C0:FF:..:EE", "47 c"),
            ("192.168.1.50", "DE:AD:..:34", "3 c")]
    rh = 42
    f.append(rect(tx, ty, tw, rh * len(rows), fill=BG, stroke=LINE, sw=1.4))
    for i, (a, b, c) in enumerate(rows):
        yy = ty + i * rh
        if i == 0:
            f.append(rect(tx, yy, tw, rh, fill="#eef3ff", stroke=LINE, sw=1.2))
            bold = True
            col = INK
        else:
            f.append(line(tx, yy, tx + tw, yy, color="#dddddd", sw=1))
            bold = False
            col = INK
        f.append(text(tx + 95, yy + 27, a, size=12, bold=bold, color=col))
        f.append(text(tx + 245, yy + 27, b, size=12, bold=bold, color=col))
        f.append(text(tx + 330, yy + 27, c, size=12, bold=bold, color=MUTED if not bold else INK))
    # вертикальні розділювачі стовпців
    f.append(line(tx + 175, ty, tx + 175, ty + rh * len(rows), color="#dddddd", sw=1))
    f.append(line(tx + 295, ty, tx + 295, ty + rh * len(rows), color="#dddddd", sw=1))
    f.append(text(tx + tw / 2, ty + rh * len(rows) + 24,
                  "записи живуть кілька хвилин, потім стираються", size=11, italic=True, color=MUTED))

    # логіка праворуч
    f.append(fitbox(450, 90, 270, 52, "Треба надіслати на IP.\nЗаглянь у таблицю:",
                    size=12, fill="#fff7e6", stroke=MUTED, sw=1.3, bold=True))
    f.append(arrow(585, 142, 585, 168, color=LINE))
    f.append(fitbox(450, 170, 270, 46, "Є запис? → шлю кадр ОДРАЗУ\n(нуль затримки)",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.3))
    f.append(arrow(585, 216, 585, 240, color=LINE))
    f.append(fitbox(450, 242, 270, 60, "Нема? → один ARP-запит,\nвідповідь лягає в таблицю,\nдалі знову з кеша",
                    size=11, fill="#fdecea", stroke=POS, sw=1.3))

    render(os.path.join(IMG, "arp-table.svg"), W, H, *f)


if __name__ == "__main__":
    fig_two_levels()
    fig_frame_vs_packet()
    fig_arp_exchange()
    fig_local_vs_gateway()
    fig_arp_table()
    print("OK: 5 figures ->", IMG)
