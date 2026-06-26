# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── axes: п'ять осей, за якими міряємо будь-який канал виводу ─────────────────
# Ідея: жоден канал не виграє за всіма; вибір каналу = вибір, чим пожертвувати.
def fig_axes():
    W, H = 700, 340
    p = []
    p.append(text(W / 2, 30, "За чим міряти канал виводу — п'ять осей", size=17, bold=True))

    rows = [
        ("Час програми", "як сильно друк краде такти й зрушує тайминг", POS),
        ("Пропускна спроможність", "скільки даних канал пропускає за секунду", "#2457d6"),
        ("Живучість", "чи працює до main() і в мить аварії", FIELD),
        ("Ціна в залізі", "піни, міст, окремий зонд", MUTED),
        ("Двобічність", "лише слухати чи й слати чипу команди", "#2457d6"),
    ]
    y0, rh = 64, 50
    for i, (name, sub, col) in enumerate(rows):
        y = y0 + i * rh
        p.append(rect(50, y, 600, rh - 10, fill=FILL, stroke=col, sw=1.6))
        p.append(circle(78, y + (rh - 10) / 2, 9, fill=BG, stroke=col, sw=2))
        p.append(text(78, y + (rh - 10) / 2 + 4, str(i + 1), size=12, bold=True, color=col))
        p.append(text(104, y + 22, name, size=14, bold=True, color=INK, anchor="start"))
        p.append(text(104, y + 36, sub, size=11.5, color=MUTED, anchor="start"))

    p.append(text(W / 2, 326, "жоден канал не виграє за всіма — вибрати канал = вибрати, чим пожертвувати",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "axes.svg"), W, H, *p)


# ── uart-vs-usb: зовнішній міст-UART проти вбудованого USB CDC ────────────────
# Ідея: USB ширший і без моста, але живе лише поки тримається USB-стек; UART
# вузький, зате живий з перших тактів і навіть у аварії.
def fig_uart_vs_usb():
    W, H = 700, 350
    p = []
    p.append(text(W / 2, 30, "UART через міст проти вбудованого USB CDC", size=17, bold=True))

    # ── UART (зверху) ──
    p.append(text(60, 64, "UART: окремий міст, вузько — зате живе завжди", size=13, bold=True,
                  color=FIELD, anchor="start"))
    p.append(rect(60, 76, 130, 58, fill="#1f1f1f", stroke=FIELD, sw=1.5))
    p.append(text(125, 100, "чіп", size=12.5, color="#cccccc"))
    p.append(text(125, 120, "2 піни TX/RX", size=11, color="#7fd49a"))
    p.append(arrow(190, 105, 236, 105, color=FIELD, sw=1.8))
    p.append(rect(236, 76, 110, 58, fill=FILL, stroke=FIELD, sw=1.5))
    p.append(text(291, 100, "USB↔UART", size=12, bold=True))
    p.append(text(291, 120, "міст", size=11, color=MUTED))
    p.append(arrow(346, 105, 392, 105, color=FIELD, sw=1.8))
    p.append(rect(392, 84, 92, 42, fill="#0c1c34", stroke=FIELD, sw=1.5))
    p.append(text(438, 110, "ПК", size=12.5, bold=True, color="#9db8f0"))
    p.append(text(560, 96, "~11 КБ/с", size=12, color=INK))
    p.append(text(560, 116, "живий у аварії", size=11, color=FIELD, italic=True))

    # ── USB CDC (знизу) ──
    p.append(text(60, 188, "USB CDC: ширше й без моста — та вмирає зі стеком", size=13, bold=True,
                  color=POS, anchor="start"))
    p.append(rect(60, 200, 180, 64, fill="#1f1f1f", stroke=POS, sw=1.5))
    p.append(text(150, 222, "чіп з вбудованим USB", size=11.5, color="#cccccc"))
    p.append(rect(76, 232, 148, 24, fill="#2a1414", stroke=POS, sw=1.1))
    p.append(text(150, 249, "USB-стек має піднятися", size=10.5, color="#e6a6a0"))
    p.append(arrow(240, 232, 392, 232, color=POS, sw=2.2))
    p.append(text(316, 220, "один USB-кабель", size=11, color=POS, italic=True))
    p.append(rect(392, 210, 92, 44, fill="#0c1c34", stroke=POS, sw=1.5))
    p.append(text(438, 237, "ПК", size=12.5, bold=True, color="#9db8f0"))
    p.append(text(560, 222, "МБ/с", size=12, color=INK))
    p.append(text(560, 242, "впав чіп — порт зник", size=10.5, color=POS, italic=True))

    p.append(text(W / 2, 326, "будні — USB (швидко, без моста); аварія й старт — лиши собі UART",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "uart-vs-usb.svg"), W, H, *p)


# ── trace-channel: слід через зонд — ITM/SWO або буфер у RAM ─────────────────
# Ідея: байти йдуть не дротом даних, а лінією відлагодження; ядро майже не платить.
def fig_trace_channel():
    W, H = 700, 340
    p = []
    p.append(text(W / 2, 30, "Слід через зонд: вивід майже задарма для ядра", size=17, bold=True))

    # чіп
    p.append(rect(40, 70, 300, 210, fill="#0c1c34", stroke="#2457d6", sw=2))
    p.append(text(190, 94, "живий чіп", size=13, bold=True, color="#9db8f0"))

    # шлях 1: ITM → SWO
    p.append(rect(60, 112, 260, 64, fill="#10243f", stroke=FIELD, sw=1.4))
    p.append(text(190, 132, "1) запис у регістр ITM", size=12, color="#a8e6c0"))
    p.append(text(190, 152, "ядро поклало число й пішло далі", size=10.5, color="#7fd49a"))
    p.append(text(190, 170, "(Cortex-M3/M4/M7; вивід — SWO)", size=10, color=MUTED))

    # шлях 2: буфер у RAM
    p.append(rect(60, 188, 260, 76, fill="#10243f", stroke=POS, sw=1.4))
    p.append(text(190, 208, "2) склав байти в буфер у RAM", size=12, color="#e6a6a0"))
    cells = ["b0", "b1", "b2", "…"]
    for i, c in enumerate(cells):
        x = 92 + i * 50
        p.append(rect(x, 220, 42, 24, fill="#1f1f1f", stroke=POS, sw=1))
        p.append(text(x + 21, 237, c, size=11, color="#cccccc"))
    p.append(text(190, 258, "RTT (ARM) · apptrace/TRAX (ESP32)", size=10, color=MUTED))

    # лінія відлагодження → зонд → ПК
    p.append(arrow(340, 175, 400, 175, color="#2457d6", sw=2.2))
    p.append(text(370, 163, "JTAG/SWD", size=10, color="#2457d6", italic=True))
    p.append(rect(400, 145, 110, 60, fill=FILL, stroke=INK, sw=1.8))
    p.append(text(455, 172, "зонд", size=14, bold=True))
    p.append(text(455, 192, "читає наживо", size=10.5, color=MUTED))
    p.append(arrow(510, 175, 566, 175, color=INK, sw=1.8))
    p.append(rect(566, 145, 90, 60, fill="#f1fbf4", stroke=FIELD, sw=1.8))
    p.append(text(611, 178, "ПК", size=13, bold=True, color=FIELD))

    p.append(text(W / 2, 320, "ядро не чекає на байти → тайминг не зрушено, гейзенбаг не сполоханий",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "trace-channel.svg"), W, H, *p)


# ── channel-map: канали від легкого UART до важкої мережі ────────────────────
# Ідея: кожен канал — точка компромісу; підписаний козир і вада.
def fig_channel_map():
    W, H = 700, 360
    p = []
    p.append(text(W / 2, 30, "Канали виводу: козир і вада кожного", size=17, bold=True))

    cards = [
        ("UART", FIELD, "завжди напохваті,\nживе в аварії", "вузько (~11 КБ/с),\nгальмує ядро"),
        ("USB CDC", "#2457d6", "ширше (МБ/с),\nбез моста", "вмирає зі стеком,\nне до main()"),
        ("Слід / зонд", POS, "майже без ціни,\nне лякає гейзенбаг", "потрібен зонд\nабо вбуд. блок"),
        ("Семіхостинг", MUTED, "printf без коду\nпід нього", "дуже повільно,\nбез зонда не їде"),
        ("Мережа", "#2457d6", "вікно в далекий\nпристрій", "найкрихкіше,\nважкий стек"),
    ]
    cw, gap = 124, 12
    x0 = (W - (cw * len(cards) + gap * (len(cards) - 1))) / 2
    for i, (title, col, good, bad) in enumerate(cards):
        x = x0 + i * (cw + gap)
        # «вага» каналу росте зліва направо — підказка висотою смужки зверху
        p.append(rect(x, 64, cw, 12 + i * 5, fill=col, stroke="none", sw=0))
        p.append(rect(x, 86, cw, 232, fill=FILL, stroke=col, sw=1.8))
        p.append(text(x + cw / 2, 110, title, size=13.5, bold=True, color=col))
        # козир
        p.append(circle(x + 20, 134, 8, fill="#eaf6ee", stroke=FIELD, sw=1.6))
        p.append(text(x + 20, 138, "+", size=13, bold=True, color=FIELD))
        p.append(mtext(x + cw / 2 + 8, 130, good, size=10, color=INK, lh=1.2))
        # вада
        p.append(circle(x + 20, 214, 8, fill="#fdecea", stroke=POS, sw=1.6))
        p.append(text(x + 20, 218, "−", size=14, bold=True, color=POS))
        p.append(mtext(x + cw / 2 + 8, 210, bad, size=10, color=INK, lh=1.2))
        # порядкова вага
        p.append(text(x + cw / 2, 300, "легше" if i == 0 else ("важче" if i == len(cards) - 1 else ""),
                      size=10, color=MUTED, italic=True))

    p.append(text(W / 2, 344, "зліва направо — від найлегшого до найважчого; бери найлегший, що покриває випадок",
                  size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "channel-map.svg"), W, H, *p)


if __name__ == "__main__":
    fig_axes()
    fig_uart_vs_usb()
    fig_trace_channel()
    fig_channel_map()
    print("ok: 4 figures ->", OUT)
