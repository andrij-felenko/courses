# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── stack-layering: Пошаровий стек RFCOMM ────────────────────────────────────
def fig_stack_layering():
    W, H = 760, 390
    p = []

    layers = [
        ("Застосунки / Служби", "Термінал (SPP), PPP/Модем (DUN), Телефонна книга (PBAP), AT-команди (HFP)", "#f8fafc", "#475569"),
        ("Віртуальний COM-порт ОС", "Драйвер TTY / POSIX пристрій (/dev/rfcomm0), емуляція 9-контактного RS-232", "#eff6ff", NEG),
        ("Протокол RFCOMM", "Мультиплексування DLCI 0..30, емуляція ліній V.24 (MSC/RPN), кредитний контроль CBFC", "#f0fdf4", FIELD),
        ("Рівень L2CAP", "Канал PSM 0x0003, фіксований/динамічний CID, сегментація та складання (SAR), MTU", "#fdf4ff", "#a855f7"),
        ("Інтерфейс HCI", "Пакетна передача кадрів ACL (HCI_ACLDATA_PKT) через фізичний інтерфейс UART/USB", "#fffbeb", "#d97706"),
        ("Контролер Bluetooth (PHY / Baseband)", "Радіоканал 2.4 ГГц, стрибки частоти FHSS, апаратний CRC, повтори ARQ", "#fef2f2", POS)
    ]

    y_start = 58
    row_h = 44
    gap = 8
    box_w = 680
    cx = W / 2

    for i, (title_text, sub_text, fill_col, stroke_col) in enumerate(layers):
        cy = y_start + i * (row_h + gap) + row_h / 2
        
        # Background box
        p.append(rect(cx - box_w / 2, cy - row_h / 2, box_w, row_h, fill=fill_col, stroke=stroke_col, sw=1.6, rx=6))
        
        # Texts
        p.append(text(cx, cy - 7, title_text, size=13, color=stroke_col, bold=True))
        p.append(text(cx, cy + 11, sub_text, size=11, color=INK))

        # Down arrow between boxes
        if i < len(layers) - 1:
            arrow_y1 = cy + row_h / 2 + 1
            arrow_y2 = arrow_y1 + gap - 2
            p.append(line(cx - 310, arrow_y1, cx - 310, arrow_y2, color=MUTED, sw=1.5))
            p.append(line(cx + 310, arrow_y1, cx + 310, arrow_y2, color=MUTED, sw=1.5))

    render(os.path.join(OUT, "stack-layering.svg"), W, H, *p,
           title="Місце RFCOMM у стеку протоколів Bluetooth Classic")


# ── dlci-multiplexing: Мультиплексування до 30 каналів через один L2CAP ────────
def fig_dlci_multiplexing():
    W, H = 760, 350
    p = []

    # Left boxes: virtual serial channels
    y_channels = [65, 125, 185, 245]
    channels = [
        ("DLCI 0: Службовий канал (MCC)", "Керування сесією, кадри PN, MSC, RPN, RLS, TEST", "#eff6ff", NEG),
        ("DLCI 2: Канал даних SPP", "Віртуальний термінал UART (Server Channel 1, потік байтів)", "#f0fdf4", FIELD),
        ("DLCI 4: Канал даних DUN", "Модемні AT-команди та пакетний трафік PPP (Server Channel 2)", "#fffbeb", "#d97706"),
        ("DLCI 6: Канал OBEX / PBAP", "Синхронізація контактів та файлів (Server Channel 3)", "#fdf4ff", "#a855f7")
    ]

    mux_cx, mux_cy = 440, 155
    mux_w, mux_h = 200, 220

    l2cap_cx, l2cap_cy = 645, 155
    l2cap_w, l2cap_h = 150, 100

    # Draw left channels
    for i, (title_text, sub_text, fill_col, stroke_col) in enumerate(channels):
        cy = y_channels[i]
        p.append(rect(40, cy - 22, 280, 44, fill=fill_col, stroke=stroke_col, sw=1.6, rx=6))
        p.append(text(180, cy - 6, title_text, size=12, color=stroke_col, bold=True))
        p.append(text(180, cy + 11, sub_text, size=9.5, color=INK))

        # Connecting lines into MUX
        p.append(arrow(320, cy, mux_cx - mux_w / 2, mux_cy + (i - 1.5) * 45, color=stroke_col, sw=1.5))

    # Multiplexer Box
    p.append(rect(mux_cx - mux_w / 2, mux_cy - mux_h / 2, mux_w, mux_h, fill="#f8fafc", stroke="#334155", sw=2, rx=8))
    p.append(text(mux_cx, mux_cy - 20, "Мульти-", size=13, color=INK, bold=True))
    p.append(text(mux_cx, mux_cy, "плексор", size=13, color=INK, bold=True))
    p.append(text(mux_cx, mux_cy + 20, "RFCOMM", size=13, color=NEG, bold=True))
    p.append(text(mux_cx, mux_cy + 42, "(DLCI 0..30)", size=10, color=MUTED))

    # Single line from MUX to L2CAP
    p.append(arrow(mux_cx + mux_w / 2, mux_cy, l2cap_cx - l2cap_w / 2, l2cap_cy, color=NEG, sw=2.5))
    p.append(text(542, mux_cy - 12, "Єдиний потік кадрів", size=10.5, color=NEG, bold=True))

    # L2CAP Box
    p.append(rect(l2cap_cx - l2cap_w / 2, l2cap_cy - l2cap_h / 2, l2cap_w, l2cap_h, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    p.append(text(l2cap_cx, l2cap_cy - 25, "Канал L2CAP", size=13, color=FIELD, bold=True))
    p.append(text(l2cap_cx, l2cap_cy - 5, "PSM = 0x0003", size=11, color=INK, bold=True))
    p.append(text(l2cap_cx, l2cap_cy + 15, "Фіксований CID", size=10, color=MUTED))
    p.append(text(l2cap_cx, l2cap_cy + 32, "(єдиний канал зв'язку)", size=9.5, color=MUTED, italic=True))

    # Bottom summary
    p.append(text(W / 2, H - 20, "До 30 незалежних послідовних портів обслуговуються одним з'єднанням L2CAP", size=11.5, color=INK, italic=True))

    render(os.path.join(OUT, "dlci-multiplexing.svg"), W, H, *p,
           title="Мультиплексування віртуальних каналів DLCI у протоколі RFCOMM")


# ── frame-structure: Анатомія кадру RFCOMM ──────────────────────────────────
def fig_frame_structure():
    W, H = 760, 360
    p = []

    y_bar = 70
    h_bar = 54

    # Frame header blocks
    x0 = 40
    fields = [
        ("Адреса (Address)", "1 байт", 110, "#eff6ff", NEG, "EA (1) | C/R | D | DLCI (5 біт)"),
        ("Керування (Control)", "1 байт", 110, "#f0fdf4", FIELD, "Тип кадру (UIH/SABM/UA/DISC) + P/F"),
        ("Довжина (Length)", "1 або 2 байти", 120, "#fffbeb", "#d97706", "EA bit + 7 або 15 біт довжини"),
        ("Кредити (Credits)", "1 байт (опція)", 100, "#fdf4ff", "#a855f7", "Кількість кредитів (UIH + P/F=1)"),
        ("Корисні дані (Payload)", "0 .. N байтів", 150, "#f8fafc", "#475569", "Дані порту або команда DLCI 0"),
        ("Контроль (FCS)", "1 байт", 90, "#fef2f2", POS, "8-бітний CRC (поліном 0xE0)")
    ]

    curr_x = x0
    for title_txt, size_txt, w_box, fill_col, stroke_col, desc in fields:
        p.append(rect(curr_x, y_bar, w_box, h_bar, fill=fill_col, stroke=stroke_col, sw=1.8, rx=5))
        p.append(text(curr_x + w_box / 2, y_bar + 20, title_txt.split(" (")[0], size=11.5, color=stroke_col, bold=True))
        p.append(text(curr_x + w_box / 2, y_bar + 38, size_txt, size=10, color=MUTED))
        curr_x += w_box

    # Detailed breakdown boxes below
    y_details = 160
    
    # Detailed breakdown 1: Address field
    p.append(rect(40, y_details, 210, 140, fill="#eff6ff", stroke=NEG, sw=1.4, rx=6))
    p.append(text(145, y_details + 20, "Поле адреси (1 байт)", size=12, color=NEG, bold=True))
    p.append(text(145, y_details + 42, "Біт 0: EA = 1 (кінець адреси)", size=10.5, color=INK))
    p.append(text(145, y_details + 62, "Біт 1: C/R (команда / відповідь)", size=10.5, color=INK))
    p.append(text(145, y_details + 82, "Біт 2: D (напрямок ініціатора)", size=10.5, color=INK))
    p.append(text(145, y_details + 104, "Біти 3..7: Номер Server Channel", size=10.5, color=INK))
    p.append(text(145, y_details + 124, "DLCI = (ServerChannel << 1) | D", size=10, color=NEG, bold=True))

    # Detailed breakdown 2: Control & Length
    p.append(rect(270, y_details, 220, 140, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(380, y_details + 20, "Керування та довжина", size=12, color=FIELD, bold=True))
    p.append(text(380, y_details + 42, "SABM (0x2F / 0x3F) — запуск", size=10.5, color=INK))
    p.append(text(380, y_details + 62, "UA (0x63 / 0x73) — підтвердження", size=10.5, color=INK))
    p.append(text(380, y_details + 82, "UIH (0xEF / 0xFF) — потік даних", size=10.5, color=INK))
    p.append(text(380, y_details + 104, "DISC (0x43 / 0x53) — розрив", size=10.5, color=INK))
    p.append(text(380, y_details + 124, "P/F = 1 в UIH вмикає байт Credits", size=10, color=FIELD, bold=True))

    # Detailed breakdown 3: FCS Check Sequence
    p.append(rect(510, y_details, 210, 140, fill="#fef2f2", stroke=POS, sw=1.4, rx=6))
    p.append(text(615, y_details + 20, "Контрольна сума FCS (CRC-8)", size=12, color=POS, bold=True))
    p.append(text(615, y_details + 45, "Для SABM, UA, DISC, DM:", size=10.5, color=INK, bold=True))
    p.append(text(615, y_details + 65, "Рахується по: Addr + Ctrl + Len", size=10, color=MUTED))
    p.append(text(615, y_details + 90, "Для кадрів UIH (дані):", size=10.5, color=INK, bold=True))
    p.append(text(615, y_details + 110, "Рахується ТІЛЬКИ по: Addr + Ctrl", size=10, color=MUTED))
    p.append(text(615, y_details + 126, "(швидкий пропуск даних)", size=9.5, color=POS, italic=True))

    # Bottom summary
    p.append(text(W / 2, H - 15, "Кадр RFCOMM інкапсулюється в пакет L2CAP без повторного додавання преамбули", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "frame-structure.svg"), W, H, *p,
           title="Структура та поля кадру протоколу RFCOMM")


# ── cbfc-credits: Кредитний контроль потоку (CBFC) ───────────────────────────
def fig_cbfc_credits():
    W, H = 760, 390
    p = []

    # Two lifelines: Dev A (Sender) and Dev B (Receiver)
    x_a = 150
    x_b = 610
    y_top = 70
    y_bot = 355

    # Headers
    p.append(rect(x_a - 90, y_top - 24, 180, 36, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(x_a, y_top - 6, "Передавач (Пристрій A)", size=12, color=NEG, bold=True))

    p.append(rect(x_b - 90, y_top - 24, 180, 36, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(x_b, y_top - 6, "Приймач (Пристрій B)", size=12, color=FIELD, bold=True))

    # Lifelines
    p.append(line(x_a, y_top + 12, x_a, y_bot, color=LINE, sw=1.5, dash="4,4"))
    p.append(line(x_b, y_top + 12, x_b, y_bot, color=LINE, sw=1.5, dash="4,4"))

    # Step 1: Initial credits in PN
    y1 = 110
    p.append(arrow(x_b, y1, x_a, y1 + 15, color=FIELD, sw=1.6))
    p.append(text(380, y1 + 4, "Відповідь PN: початковий баланс = 2 кредити", size=11, color=FIELD, bold=True))
    p.append(text(x_a - 100, y1 + 15, "Баланс: 2", size=10, color=NEG, bold=True))

    # Step 2: Send Frame 1
    y2 = 150
    p.append(arrow(x_a, y2, x_b, y2 + 15, color=NEG, sw=1.6))
    p.append(text(380, y2 + 4, "UIH кадр #1 (P/F=0, витрачено 1 кредит)", size=10.5, color=INK))
    p.append(text(x_a - 100, y2 + 15, "Баланс: 1", size=10, color=NEG, bold=True))

    # Step 3: Send Frame 2 (exhausts credits)
    y3 = 190
    p.append(arrow(x_a, y3, x_b, y3 + 15, color=NEG, sw=1.6))
    p.append(text(380, y3 + 4, "UIH кадр #2 (P/F=0, витрачено 1 кредит)", size=10.5, color=INK))
    p.append(text(x_a - 100, y3 + 15, "Баланс: 0", size=10, color=POS, bold=True))

    # Step 4: Sender PAUSED
    y4 = 230
    p.append(rect(x_a - 80, y4 - 12, 160, 24, fill="#fef2f2", stroke=POS, sw=1.4, rx=4))
    p.append(text(x_a, y4 + 4, "ПАУЗА: кредити вичерпано", size=10, color=POS, bold=True))

    # Step 5: Receiver frees buffer and issues credits
    y5 = 265
    p.append(arrow(x_b, y5, x_a, y5 + 15, color=FIELD, sw=2.0))
    p.append(text(380, y5 + 4, "UIH кадр (P/F=1, Credits = +3 поповнення)", size=11, color=FIELD, bold=True))
    p.append(text(x_a - 100, y5 + 20, "Баланс: 3", size=10, color=FIELD, bold=True))

    # Step 6: Sender resumes
    y6 = 310
    p.append(arrow(x_a, y6, x_b, y6 + 15, color=NEG, sw=1.6))
    p.append(text(380, y6 + 4, "UIH кадр #3 (передача відновлена)", size=10.5, color=INK))
    p.append(text(x_a - 100, y6 + 15, "Баланс: 2", size=10, color=NEG, bold=True))

    # Footer note
    p.append(text(W / 2, H - 15, "Кожен DLCI веде власний незалежний облік кредитів, усуваючи блокування черги", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "cbfc-credits.svg"), W, H, *p,
           title="Кредитний контроль потоку (Credit-Based Flow Control)")


# ── session-lifecycle: Життєвий цикл сесії RFCOMM ────────────────────────────
def fig_session_lifecycle():
    W, H = 760, 390
    p = []

    steps = [
        ("1. Підключення L2CAP", "Відкриття каналу до PSM 0x0003, виділення CID", "#eff6ff", NEG),
        ("2. Запуск MUX (DLCI 0)", "SABM(0) → UA(0): старт мультиплексора керування", "#f0fdf4", FIELD),
        ("3. Узгодження PN", "PN(DLCI k): MTU, пріоритет, кредитний режим CBFC", "#fffbeb", "#d97706"),
        ("4. Відкриття DLCI k", "SABM(k) → UA(k): активація віртуального порту даних", "#fdf4ff", "#a855f7"),
        ("5. Сигнали ліній RS-232", "MSC(k): передача стану ліній RTS, CTS, DTR, DSR, CD", "#f8fafc", "#475569"),
        ("6. Потік даних (UIH)", "Двосторонній обмін корисними байтами під контролем CBFC", "#eff6ff", NEG),
        ("7. Закриття каналу", "DISC(k) → UA(k); DISC(0) → UA(0) для зупинки MUX", "#fef2f2", POS)
    ]

    y_start = 58
    row_h = 37
    gap = 8
    box_w = 680
    cx = W / 2

    for i, (title_text, sub_text, fill_col, stroke_col) in enumerate(steps):
        cy = y_start + i * (row_h + gap) + row_h / 2
        p.append(rect(cx - box_w / 2, cy - row_h / 2, box_w, row_h, fill=fill_col, stroke=stroke_col, sw=1.5, rx=5))
        p.append(text(cx - 180, cy + 4, title_text, size=12, color=stroke_col, bold=True, anchor="start"))
        p.append(text(cx + 40, cy + 4, sub_text, size=11, color=INK, anchor="start"))

        if i < len(steps) - 1:
            ay1 = cy + row_h / 2 + 1
            ay2 = ay1 + gap - 2
            p.append(arrow(cx - 310, ay1, cx - 310, ay2, color=MUTED, sw=1.4))

    render(os.path.join(OUT, "session-lifecycle.svg"), W, H, *p,
           title="Послідовність фаз сесії RFCOMM від запуску до розриву")


if __name__ == "__main__":
    fig_stack_layering()
    fig_dlci_multiplexing()
    fig_frame_structure()
    fig_cbfc_credits()
    fig_session_lifecycle()
    print("Всі фігури згенеровано успішно.")
