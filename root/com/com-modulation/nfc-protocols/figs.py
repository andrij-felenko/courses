# -*- coding: utf-8 -*-
"""
Фігури теми «Протоколи NFC: ISO 14443, NDEF і режими роботи».
Запуск: python figs.py → ./img/*.svg
Імпортуємо svgkit зі scripts/.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Модуляція радіочастотного сигналу NFC ─────────────────────────
def fig_rf_modulation():
    W, H = 720, 420
    parts = []

    # Панель 1: Зв'язок PCD -> PICC (Запит)
    py1 = 40
    parts.append(rect(30, py1, 660, 160, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(45, py1 + 24, "Передача PCD → PICC (Канал зчитувача до мітки, несуча 13.56 МГц)", 12, INK, "start", bold=True))

    # Type A: Modified Miller + ASK 100%
    parts.append(text(45, py1 + 60, "ISO 14443 Type A (106 кбіт/с): Modified Miller, ASK 100%", 11, FIELD, "start", bold=True))
    pts_a = []
    for x in range(45, 330):
        if 160 <= x <= 190:
            amp = 0
        else:
            amp = 20
        y = (py1 + 105) + amp * math.sin((x - 45) * 0.4)
        pts_a.append(f"{x},{y:.1f}")
    parts.append(f'<polyline points="{" ".join(pts_a)}" fill="none" stroke="{FIELD}" stroke-width="1.8"/>')
    parts.append(line(160, py1 + 80, 160, py1 + 130, color=NEG, sw=1, dash="2 2"))
    parts.append(line(190, py1 + 80, 190, py1 + 130, color=NEG, sw=1, dash="2 2"))
    parts.append(text(175, py1 + 143, "Пауза 100% (2.3-3.0 мкс)", 10, NEG, "middle"))

    # Type B: NRZ-L + ASK 10%
    parts.append(text(370, py1 + 60, "ISO 14443 Type B (106 кбіт/с): NRZ-L, ASK 10-14%", 11, POS, "start", bold=True))
    pts_b = []
    for x in range(370, 660):
        if 480 <= x <= 550:
            amp = 14
        else:
            amp = 22
        y = (py1 + 105) + amp * math.sin((x - 370) * 0.4)
        pts_b.append(f"{x},{y:.1f}")
    parts.append(f'<polyline points="{" ".join(pts_b)}" fill="none" stroke="{POS}" stroke-width="1.8"/>')
    parts.append(line(480, py1 + 80, 480, py1 + 130, color=POS, sw=1, dash="2 2"))
    parts.append(line(550, py1 + 80, 550, py1 + 130, color=POS, sw=1, dash="2 2"))
    parts.append(text(515, py1 + 143, "Модуляція 10% (неперервне поле)", 10, POS, "middle"))

    # Панель 2: Зв'язок PICC -> PCD (Модуляція навантаженням)
    py2 = 220
    parts.append(rect(30, py2, 660, 170, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(45, py2 + 24, "Відповідь PICC → PCD (Модуляція навантаженням на піднесучій fs = 848 кГц)", 12, INK, "start", bold=True))

    sx0, sy0, sw_len = 60, py2 + 130, 260
    parts.append(arrow(sx0 - 10, sy0, sx0 + sw_len + 20, sy0, color=MUTED, sw=1.2))
    parts.append(arrow(sx0 + sw_len/2, sy0 + 5, sx0 + sw_len/2, sy0 - 75, color=MUTED, sw=1.2))
    parts.append(text(sx0 + sw_len + 15, sy0 + 16, "f (МГц)", 10, MUTED, "end"))
    parts.append(text(sx0 + sw_len/2 - 5, sy0 - 80, "Амплітуда", 10, MUTED, "end"))

    fc_x = sx0 + sw_len/2
    parts.append(line(fc_x, sy0, fc_x, sy0 - 65, color=NEG, sw=2.5))
    parts.append(text(fc_x, sy0 + 16, "fc = 13.56", 10, NEG, "middle", bold=True))

    fs_left = fc_x - 70
    fs_right = fc_x + 70
    parts.append(line(fs_left, sy0, fs_left, sy0 - 35, color=POS, sw=2))
    parts.append(line(fs_right, sy0, fs_right, sy0 - 35, color=POS, sw=2))
    parts.append(text(fs_left, sy0 + 16, "12.71 МГц", 9, POS, "middle"))
    parts.append(text(fs_right, sy0 + 16, "14.41 МГц", 9, POS, "middle"))
    parts.append(text(fs_left, sy0 - 42, "fc - fs", 9, POS, "middle"))
    parts.append(text(fs_right, sy0 - 42, "fc + fs", 9, POS, "middle"))

    tx_box = fitbox(360, py2 + 45, 310, 100,
                    "Type A: Манчестерське кодування на піднесучій 848 кГц\n"
                    "Type B: BPSK модуляція піднесучої (зсув фази на 180°)\n"
                    "Зміна імпедансу мітки ΔZ створює бічні смуги fc ± 848 кГц,\n"
                    "які зчитувач детектує у витку антени PCD.",
                    size=10, fill="#ffffff", stroke="#cbd5e1", sw=1, color=INK)
    parts.append(tx_box)

    render(os.path.join(IMG, "nfc-rf-modulation.svg"), W, H, *parts,
           title="Фізичний рівень NFC: тип А/B модуляції та модуляція навантаженням")


# ── Фігура 2: Алгоритм антиколізії ISO 14443-3 (Cascade Levels) ──────────────
def fig_iso14443_anticollision():
    W, H = 720, 360
    parts = []

    bw, bh = 145, 170
    y_top = 80

    steps = [
        ("Крок 1: Ініціалізація", "REQA (0x26) /\nWUPA (0x52)\n\nВідповідь ATQA:\nВказує розмір UID\n(4, 7 або 10 байт)", "#e0f2fe", FIELD),
        ("Cascade Level 1", "SEL = 0x93\nANTICOLLISION\n\nОтримання:\nUID0..UID3 + BCC\n(Якщо UID0=0x88 → CT)", "#fef3c7", INK),
        ("Cascade Level 2", "SEL = 0x95\n(якщо UID > 4B)\n\nОтримання:\nUID3..UID6 + BCC\n\nSELECT → SAK", "#ecfdf5", POS),
        ("Cascade Level 3", "SEL = 0x97\n(якщо UID = 10B)\n\nОтримання:\nUID6..UID9 + BCC\n\nПерехід у ACTIVE", "#f3e8ff", INK)
    ]

    for i, (title_str, text_str, bg_col, border_col) in enumerate(steps):
        bx = 35 + i * 165
        parts.append(rect(bx, y_top, bw, bh, fill=bg_col, stroke=border_col, sw=1.5, rx=6))
        parts.append(text(bx + bw/2, y_top + 22, title_str, 11, border_col, "middle", bold=True))
        parts.append(line(bx + 10, y_top + 34, bx + bw - 10, y_top + 34, color=border_col, sw=1))

        box = fitbox(bx + 8, y_top + 40, bw - 16, bh - 48, text_str, size=10, fill="none", stroke="none", color=INK)
        parts.append(box)

        if i < 3:
            parts.append(arrow(bx + bw + 2, y_top + bh/2, bx + 163, y_top + bh/2, color=MUTED, sw=2))

    res_box = fitbox(160, 275, 400, 50,
                     "SAK (Select Acknowledge) завершує вибір мітки:\n"
                     "SAK bit 3 = 0 (Сумісна з ISO 14443-4) → Надсилається RATS\n"
                     "SAK bit 3 = 1 (MIFARE Classic / Proprietary)",
                     size=10, fill="#ffffff", stroke=MUTED, sw=1.2, color=INK)
    parts.append(res_box)

    render(os.path.join(IMG, "iso14443-anticollision.svg"), W, H, *parts,
           title="Ієрархія антиколізії та каскадного вибору UID в ISO 14443-3")


# ── Фігура 3: Режими роботи NFC (Reader/Writer, P2P, Card Emulation) ─────────
def fig_nfc_operating_modes():
    W, H = 720, 360
    parts = []

    modes = [
        ("Reader/Writer Mode", "Активний пристрій (PCD)\nживить пасивну мітку (PICC).\n\nЗастосування:\n- Зчитування NDEF тегів\n- Смарт-плакати\n- Валідація квитків", "#eff6ff", FIELD),
        ("Peer-to-Peer Mode", "Два активних/пасивних\nпристрої (P2P).\n\nПротоколи:\n- ISO/IEC 18092 (NFCIP-1)\n- LLCP (Logical Link)\n- SNEP (NDEF Exchange)", "#f0fdf4", POS),
        ("Card Emulation Mode", "Смартфон імітує\nпасивну смарт-карту.\n\nАрхітектура:\n- HCE (Host Card Emulation)\n- Secure Element (SE / SIM)\n- SWP (Single Wire Protocol)", "#fdf2f8", NEG)
    ]

    for i, (m_title, m_desc, bg_c, border_c) in enumerate(modes):
        bx = 35 + i * 225
        bw = 205
        bh = 240
        y0 = 50
        parts.append(rect(bx, y0, bw, bh, fill=bg_c, stroke=border_c, sw=1.8, rx=8))
        parts.append(text(bx + bw/2, y0 + 26, m_title, 13, border_c, "middle", bold=True))
        parts.append(line(bx + 12, y0 + 40, bx + bw - 12, y0 + 40, color=border_c, sw=1.2))

        tb = fitbox(bx + 10, y0 + 50, bw - 20, bh - 60, m_desc, size=11, fill="none", stroke="none", color=INK)
        parts.append(tb)

    parts.append(fitbox(100, 305, 520, 35,
                        "Всі 3 режими спираються на єдиний фізичний шар 13.56 МГц (ISO 14443 / FeliCa)",
                        size=11, fill="#ffffff", stroke=MUTED, sw=1, color=INK))

    render(os.path.join(IMG, "nfc-operating-modes.svg"), W, H, *parts,
           title="Три основні режими роботи технології NFC")


# ── Фігура 4: Структура NDEF запису та байта заголовка ──────────────────────
def fig_ndef_record_structure():
    W, H = 720, 380
    parts = []

    py1 = 40
    parts.append(rect(30, py1, 660, 110, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(45, py1 + 22, "Байт заголовка NDEF Record (Record Header Byte)", 12, INK, "start", bold=True))

    bits = [
        ("MB", "Message Begin"),
        ("ME", "Message End"),
        ("CF", "Chunk Flag"),
        ("SR", "Short Record"),
        ("IL", "ID Length"),
        ("TNF2", "Type Name"),
        ("TNF1", "Format (3b)"),
        ("TNF0", "")
    ]

    for i, (bname, bdesc) in enumerate(bits):
        bx = 45 + i * 78
        bw = 74
        bh = 32
        by = py1 + 32
        parts.append(rect(bx, by, bw, bh, fill="#e2e8f0" if i < 5 else "#dbeafe", stroke=FIELD if i >= 5 else INK, sw=1, rx=3))
        parts.append(text(bx + bw/2, by + 20, bname, 11, FIELD if i >= 5 else INK, "middle", bold=True))
        if bdesc:
            parts.append(text(bx + bw/2, by + 46, bdesc, 9, MUTED, "middle"))

    py2 = 180
    parts.append(rect(30, py2, 660, 160, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=6))
    parts.append(text(45, py2 + 22, "Послідовність полів NDEF Запису (NDEF Record Layout)", 12, INK, "start", bold=True))

    fields = [
        ("Header", "1 байт\nMB..TNF", "#dbeafe", FIELD, 75),
        ("Type Len", "1 байт\nuint8_t", "#fef3c7", INK, 85),
        ("Payload Len", "1 або 4 байти\n(SR=1:1B, SR=0:4B)", "#fee2e2", NEG, 140),
        ("ID Len", "0 або 1B\n(якщо IL=1)", "#f3e8ff", INK, 90),
        ("Record Type", "N байт\n('U', 'T')", "#ecfdf5", POS, 95),
        ("Payload", "M байт\nДані", "#eff6ff", FIELD, 105)
    ]

    curr_x = 45
    for f_name, f_desc, f_bg, f_border, f_w in fields:
        parts.append(rect(curr_x, py2 + 35, f_w, 85, fill=f_bg, stroke=f_border, sw=1.5, rx=4))
        parts.append(text(curr_x + f_w/2, py2 + 55, f_name, 11, f_border, "middle", bold=True))
        parts.append(line(curr_x + 6, py2 + 65, curr_x + f_w - 6, py2 + 65, color=f_border, sw=0.8))

        tb = fitbox(curr_x + 4, py2 + 70, f_w - 8, 45, f_desc, size=9, fill="none", stroke="none", color=INK)
        parts.append(tb)
        curr_x += f_w + 10

    render(os.path.join(IMG, "ndef-record-structure.svg"), W, H, *parts,
           title="Бітова структура заголовка та бінарне компонування запису NDEF")


fig_rf_modulation()
fig_iso14443_anticollision()
fig_nfc_operating_modes()
fig_ndef_record_structure()
print("Done generating SVG figures for NFC protocols.")
