# -*- coding: utf-8 -*-
"""Фігури до теми «Фізика лінка Ethernet».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Порівняння лінійного кодування: Manchester, MLT-3, PAM-5 ──────────────
def fig_line_coding_comparison():
    W, H = 940, 560
    f = [text(W / 2, 26, "Еволюція кодування Ethernet: спектр і швидкість", size=16, bold=True)]
    f.append(text(W / 2, 46, "Від перемикання щотакту до багаторівневих амплітуд: як умістити гігабіт у смугу 100 МГц",
                  size=11.5, color=MUTED, italic=True))

    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    n_bits = len(bits)
    x0, bit_w = 180, 85
    x_end = x0 + n_bits * bit_w

    # Верхня шкала бітів
    for i, b in enumerate(bits):
        bx = x0 + i * bit_w
        f.append(rect(bx, 64, bit_w, 24, fill="#f8fafc", stroke="#cbd5e1", sw=1.0, rx=3))
        f.append(text(bx + bit_w / 2, 80, str(b), size=13, bold=True, color=INK))
        f.append(line(bx, 88, bx, 500, color="#f1f5f9", sw=1.0, dash="3,3"))
    f.append(line(x_end, 88, x_end, 500, color="#f1f5f9", sw=1.0, dash="3,3"))
    f.append(text(x0 - 15, 80, "Бітовий потік:", size=12, bold=True, color=MUTED, anchor="end"))

    # 1. 10BASE-T: Manchester
    y_m = 145
    f.append(textbox(90, y_m, "10BASE-T\nМанчестер\n10 Мбіт/с\n(20 Мбод)", size=11, bold=True, fill="#fef2f2", stroke=POS)[0])
    f.append(line(x0, y_m, x_end, y_m, color="#e2e8f0", sw=1.0, dash="4,4"))
    m_pts = []
    # 1: High (+V) -> Low (-V); 0: Low (-V) -> High (+V)
    cur_y = y_m - 20 if bits[0] == 1 else y_m + 20
    m_pts.append("M%.1f,%.1f" % (x0, cur_y))
    for i, b in enumerate(bits):
        bx = x0 + i * bit_w
        mid_x = bx + bit_w / 2
        next_x = bx + bit_w
        if b == 1:
            # start High, transition to Low at mid
            m_pts.append("L%.1f,%.1f" % (mid_x, y_m - 20))
            m_pts.append("L%.1f,%.1f" % (mid_x, y_m + 20))
            m_pts.append("L%.1f,%.1f" % (next_x, y_m + 20))
            if i + 1 < n_bits and bits[i + 1] == 1:
                m_pts.append("L%.1f,%.1f" % (next_x, y_m - 20))
        else:
            # start Low, transition to High at mid
            m_pts.append("L%.1f,%.1f" % (mid_x, y_m + 20))
            m_pts.append("L%.1f,%.1f" % (mid_x, y_m - 20))
            m_pts.append("L%.1f,%.1f" % (next_x, y_m - 20))
            if i + 1 < n_bits and bits[i + 1] == 0:
                m_pts.append("L%.1f,%.1f" % (next_x, y_m + 20))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(m_pts), POS))
    f.append(text(x_end + 10, y_m - 5, "+2.5 V", size=9.5, color=MUTED, anchor="start"))
    f.append(text(x_end + 10, y_m + 15, "−2.5 V", size=9.5, color=MUTED, anchor="start"))
    f.append(text(x_end + 10, y_m + 32, "max 10 МГц", size=10, color=POS, bold=True, anchor="start"))

    # 2. 100BASE-TX: MLT-3
    y_mlt = 280
    f.append(textbox(90, y_mlt, "100BASE-TX\nMLT-3 (4B5B)\n100 Мбіт/с\n(125 Мбод)", size=11, bold=True, fill="#eff6ff", stroke=NEG)[0])
    f.append(line(x0, y_mlt, x_end, y_mlt, color="#cbd5e1", sw=1.0, dash="4,4"))
    f.append(line(x0, y_mlt - 22, x_end, y_mlt - 22, color="#f1f5f9", sw=1.0))
    f.append(line(x0, y_mlt + 22, x_end, y_mlt + 22, color="#f1f5f9", sw=1.0))
    mlt_seq = [0, 1, 0, -1]
    mlt_idx = 0
    cur_lvl = 0
    mlt_pts = ["M%.1f,%.1f" % (x0, y_mlt)]
    for i, b in enumerate(bits):
        bx = x0 + i * bit_w
        next_x = bx + bit_w
        if b == 1:
            mlt_idx = (mlt_idx + 1) % 4
            cur_lvl = mlt_seq[mlt_idx]
        y_val = y_mlt - cur_lvl * 22
        mlt_pts.append("L%.1f,%.1f" % (bx, y_val))
        mlt_pts.append("L%.1f,%.1f" % (next_x, y_val))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(mlt_pts), NEG))
    f.append(text(x_end + 10, y_mlt - 20, "+1.0 V", size=9.5, color=MUTED, anchor="start"))
    f.append(text(x_end + 10, y_mlt + 3, "0 V", size=9.5, color=MUTED, anchor="start"))
    f.append(text(x_end + 10, y_mlt + 24, "−1.0 V", size=9.5, color=MUTED, anchor="start"))
    f.append(text(x_end + 10, y_mlt + 40, "max 31.25 МГц", size=10, color=NEG, bold=True, anchor="start"))

    # 3. 1000BASE-T: PAM-5
    y_pam = 430
    f.append(textbox(90, y_pam, "1000BASE-T\nPAM-5 (4 пари)\n1 Гбіт/с\n(125 Мбод/пара)", size=11, bold=True, fill="#f0fdf4", stroke=FIELD)[0])
    for l_idx, l_val in enumerate([2, 1, 0, -1, -2]):
        yy = y_pam - l_val * 14
        f.append(line(x0, yy, x_end, yy, color="#e2e8f0" if l_val != 0 else "#94a3b8", sw=1.0, dash="4,4" if l_val != 0 else None))
    # 2 біти на символ: пари [1,0], [1,1], [0,0], [1,0] -> рівні +1, +2, 0, -1
    pam_symbols = [+1, +2, -1, +1]
    pam_pts = []
    sym_w = bit_w * 2
    for s_idx, sym in enumerate(pam_symbols):
        sx = x0 + s_idx * sym_w
        next_sx = sx + sym_w
        sy = y_pam - sym * 14
        if s_idx == 0:
            pam_pts.append("M%.1f,%.1f" % (sx, sy))
        else:
            pam_pts.append("L%.1f,%.1f" % (sx, sy))
        pam_pts.append("L%.1f,%.1f" % (next_sx, sy))
        # позначка 2 бітів
        f.append(textbox(sx + sym_w / 2, y_pam + 48, "%d%d → рівень %+d" % (bits[s_idx*2], bits[s_idx*2+1], sym),
                         size=10, fill="#f8fafc", stroke="#cbd5e1", pad=4)[0])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pam_pts), FIELD))
    f.append(text(x_end + 10, y_pam - 26, "+2 (+1.0V)", size=9, color=MUTED, anchor="start"))
    f.append(text(x_end + 10, y_pam - 12, "+1 (+0.5V)", size=9, color=MUTED, anchor="start"))
    f.append(text(x_end + 10, y_pam + 3, "0 (0V)", size=9, color=MUTED, anchor="start"))
    f.append(text(x_end + 10, y_pam + 16, "−1 (−0.5V)", size=9, color=MUTED, anchor="start"))
    f.append(text(x_end + 10, y_pam + 29, "−2 (−1.0V)", size=9, color=MUTED, anchor="start"))
    f.append(text(x_end + 10, y_pam + 45, "max 62.5 МГц", size=10, color=FIELD, bold=True, anchor="start"))

    # Підсумок знизу
    f.append(line(50, 515, W - 50, 515, color="#cbd5e1", sw=1.0))
    f.append(text(W / 2, 538, "Ключ: перехід від 2 рівнів напруги до 3 і 5 знижує граничну частоту в кабелі при зростанні бітрейту",
                  size=11.5, bold=True, color=INK))

    render(os.path.join(IMG, "line-coding-comparison.svg"), W, H, *f)


# ── 2. Одночасний двосторонній дуплекс 1000BASE-T: Гібрид і DSP ──────────────
def fig_gigabit_hybrid_dsp():
    W, H = 960, 530
    f = [text(W / 2, 26, "Одночасний двосторонній дуплекс 1000BASE-T (1 з 4 пар)", size=16, bold=True)]
    f.append(text(W / 2, 46, "Гібридний міст розділяє зустрічні сигнали, а цифровий процесор (DSP) віднімає відлуння й наводки",
                  size=11.5, color=MUTED, italic=True))

    # Лівий бік: Локальний PHY
    f.append(rect(40, 70, 480, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(60, 95, "Локальний PHY-трансивер (канал A)", size=13, bold=True, color=INK, anchor="start"))

    # Блок передавача TX
    f.append(rect(65, 120, 160, 65, fill="#eff6ff", stroke=NEG, sw=1.5))
    f.append(text(145, 145, "Передавач (TX)", size=12, bold=True, color=NEG))
    f.append(text(145, 165, "Trellis-кодер + ЦАП", size=10.5, color=MUTED))

    # Стрілка передачі на гібрид
    f.append(arrow(225, 152, 330, 152, color=NEG, sw=2.0))
    f.append(text(278, 142, "PAM-5 TX", size=10, bold=True, color=NEG))

    # Гібридний міст / трансформатор
    f.append(rect(330, 120, 150, 190, fill="#fef3c7", stroke="#d97706", sw=1.8))
    f.append(text(405, 145, "Гібридний міст", size=12, bold=True, color="#b45309"))
    f.append(text(405, 165, "(диференційний", size=10.5, color="#92400e"))
    f.append(text(405, 180, "трансформатор)", size=10.5, color="#92400e"))
    f.append(line(350, 205, 460, 205, color="#d97706", sw=1.0, dash="3,3"))
    f.append(text(405, 230, "Віднімає локальний TX", size=10, bold=True, color=INK))
    f.append(text(405, 250, "з сумарного сигналу", size=9.5, color=MUTED))
    f.append(text(405, 285, "Придушення: ~20 дБ", size=9.5, color=POS, bold=True))

    # Кабель (вита пара) праворуч
    f.append(rect(570, 185, 200, 70, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=6))
    f.append(text(670, 212, "Вита пара Cat5e (100 м)", size=12, bold=True, color=INK))
    f.append(text(670, 232, "Двосторонній потік (250 Мбіт/с)", size=10.5, color=MUTED))

    # Лінії між гібридом і кабелем (диференційна пара)
    f.append(line(480, 205, 570, 205, color=INK, sw=2.0))
    f.append(line(480, 235, 570, 235, color=INK, sw=2.0))
    f.append(arrow(495, 195, 555, 195, color=NEG, sw=1.5))
    f.append(arrow(555, 245, 495, 245, color=FIELD, sw=1.5))
    f.append(text(525, 185, "TX →", size=10, bold=True, color=NEG))
    f.append(text(525, 260, "← RX", size=10, bold=True, color=FIELD))

    # Віддалений вузол праворуч
    f.append(rect(810, 170, 110, 100, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=6))
    f.append(text(865, 210, "Дистанційний", size=11, bold=True, color=INK))
    f.append(text(865, 230, "вузол (PHY)", size=11, bold=True, color=INK))
    f.append(line(770, 205, 810, 205, color=INK, sw=2.0))
    f.append(line(770, 235, 810, 235, color=INK, sw=2.0))

    # Вихід гібрида на RX
    f.append(arrow(405, 310, 405, 360, color=FIELD, sw=2.0))
    f.append(text(415, 335, "Залишок RX + відлуння", size=9.5, color=MUTED, anchor="start"))

    # Блок DSP і компенсаторів
    f.append(rect(65, 360, 415, 115, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    f.append(text(272, 382, "DSP-процесор обробки сигналу (Receiver DSP)", size=12, bold=True, color=FIELD))

    # Компоненти DSP
    f.append(fitbox(75, 400, 115, 60, "Ехокомпенсатор\n(AEC FIR)\nвіднімає відлуння TX", size=9.5, fill="#ffffff", stroke="#86efac"))
    f.append(fitbox(198, 400, 125, 60, "NEXT/FEXT гасник\nвіднімає наводки\nз пар B, C, D", size=9.5, fill="#ffffff", stroke="#86efac"))
    f.append(fitbox(331, 400, 140, 60, "Еквалайзер (DFE) +\nДекодер Вітербі\nвідновлює 2 біти", size=9.5, fill="#ffffff", stroke="#86efac"))

    # Зв'язок TX -> Echo Canceller
    f.append(line(145, 185, 145, 340, color=NEG, sw=1.5, dash="3,3"))
    f.append(arrow(145, 340, 145, 400, color=NEG, sw=1.5))
    f.append(text(152, 270, "Опорний TX", size=9.5, color=NEG, anchor="start"))

    # Вхід від інших пар
    f.append(arrow(260, 485, 260, 460, color=POS, sw=1.5))
    f.append(text(260, 502, "Сигнали пар B, C, D (NEXT)", size=9.5, color=POS, bold=True))

    render(os.path.join(IMG, "gigabit-hybrid-dsp.svg"), W, H, *f)


# ── 3. Імпульси автопогодження FLP і структура базової сторінки ──────────────
def fig_flp_burst_structure():
    W, H = 960, 520
    f = [text(W / 2, 26, "Автопогодження лінка (Auto-Negotiation): пачка імпульсів FLP", size=16, bold=True)]
    f.append(text(W / 2, 46, "Сумісність із 10BASE-T: замість одного імпульсу NLP передається пачка з 33 імпульсів кодового слова",
                  size=11.5, color=MUTED, italic=True))

    # Верх: 10BASE-T NLP
    f.append(rect(40, 70, 880, 80, fill="#fef2f2", stroke=POS, sw=1.2, rx=6))
    f.append(text(55, 95, "10BASE-T: Звичайні імпульси лінка (NLP — Normal Link Pulses)", size=12.5, bold=True, color=POS, anchor="start"))
    f.append(line(200, 125, 880, 125, color="#cbd5e1", sw=1.0))
    # pulses at 250, 550, 850
    for px in [250, 550, 850]:
        f.append(rect(px - 4, 105, 8, 20, fill=POS, stroke=POS, sw=1.0))
        f.append(text(px, 100, "100 нс", size=9, color=POS))
    f.append(line(250, 135, 550, 135, color=INK, sw=1.2))
    f.append(line(250, 130, 250, 140, color=INK, sw=1.2))
    f.append(line(550, 130, 550, 140, color=INK, sw=1.2))
    f.append(text(400, 147, "Інтервал тиші: 16 ± 8 мс (перевірка наявності кабелю)", size=10, bold=True, color=INK))

    # Середина: FLP Burst
    f.append(rect(40, 165, 880, 155, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    f.append(text(55, 190, "Auto-Negotiation: Пачка швидких імпульсів (FLP Burst — 33 імпульси за 2 мс)", size=12.5, bold=True, color=NEG, anchor="start"))
    f.append(text(55, 208, "Для приймача 10BASE-T уся 2-мс пачка зливається в один NLP; приймач з автопогодженням читає 16 біт", size=10.5, color=MUTED, anchor="start"))

    # Збільшена пачка FLP
    bx0, bw = 80, 780
    f.append(line(bx0, 260, bx0 + bw, 260, color="#94a3b8", sw=1.0))
    n_clocks = 9  # покажемо частину імпульсів схематично
    dx = bw / (n_clocks * 2)
    for k in range(n_clocks):
        cx = bx0 + k * 2 * dx + 15
        # Тактовий імпульс (Clock)
        f.append(rect(cx - 3, 235, 6, 25, fill=NEG, stroke=NEG, sw=1.0))
        f.append(text(cx, 228, "C%d" % (k + 1), size=9, color=NEG, bold=True))
        # Дані (Data) — між тактами
        if k < n_clocks - 1:
            data_val = 1 if k in [0, 1, 3, 4, 6] else 0
            dx_pos = cx + dx
            if data_val == 1:
                f.append(rect(dx_pos - 3, 243, 6, 17, fill=FIELD, stroke=FIELD, sw=1.0))
                f.append(text(dx_pos, 275, "«1»", size=9, color=FIELD, bold=True))
            else:
                f.append(circle(dx_pos, 260, 2.5, fill="#cbd5e1", stroke="#94a3b8", sw=1.0))
                f.append(text(dx_pos, 275, "«0»", size=9, color=MUTED))

    f.append(text(bx0 + 70, 305, "17 тактових (125 мкс) + 16 бітів даних у проміжках (62.5 мкс) = 16-бітове слово Base Page", size=10.5, bold=True, color=INK, anchor="start"))

    # Низ: Поля 16-бітової базової сторінки (Base Page)
    f.append(rect(40, 335, 880, 160, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=6))
    f.append(text(55, 355, "Структура 16-бітового кодового слова базової сторінки (Base Page, Clause 28)", size=12, bold=True, color=INK, anchor="start"))

    fields = [
        ("D0..D4", "Селектор\n(00001 = 802.3)", "#dbeafe", "#1e40af", 100),
        ("D5..D9", "Технології\n10/100, HD/FD", "#fef3c7", "#92400e", 150),
        ("D10..D11", "Пауза\n(Flow Control)", "#f3e8ff", "#6b21a8", 110),
        ("D12", "Remote\nFault (RF)", "#fee2e2", "#991b1b", 90),
        ("D13", "Підтвердж.\nACK (3 копії)", "#dcfce7", "#166534", 110),
        ("D14", "Next Page\n(1000BASE-T)", "#ffedd5", "#9a3412", 110),
        ("D15", "Зарезерв.\n(0)", "#f1f5f9", "#475569", 90),
    ]
    cur_fx = 60
    for name, desc, bg_c, txt_c, w_col in fields:
        f.append(rect(cur_fx, 375, w_col, 24, fill=bg_c, stroke=txt_c, sw=1.2, rx=3))
        f.append(text(cur_fx + w_col / 2, 391, name, size=10, bold=True, color=txt_c))
        f.append(fitbox(cur_fx, 404, w_col, 50, desc, size=9.5, fill="#ffffff", stroke="#cbd5e1"))
        cur_fx += w_col + 15

    f.append(text(W / 2, 480, "Пріоритет: 10GBASE-T FD > 1000BASE-T FD > 1000BASE-T HD > 100BASE-TX FD > 100BASE-TX HD > 10BASE-T",
                  size=11, bold=True, color=POS))

    render(os.path.join(IMG, "flp-burst-structure.svg"), W, H, *f)


# ── 4. Архітектура MAC-PHY: Інтерфейси MII / RGMII / SGMII та MDIO ───────────
def fig_mac_phy_interfaces():
    W, H = 960, 540
    f = [text(W / 2, 26, "Апаратна межа MAC ↔ PHY та інтерфейси з'єднання", size=16, bold=True)]
    f.append(text(W / 2, 46, "Цифровий контролер MAC у SoC підключається до трансивера PHY через шину даних та шину керування MDIO",
                  size=11.5, color=MUTED, italic=True))

    # Лівий блок: SoC / МАК
    f.append(rect(40, 70, 240, 440, fill="#f8fafc", stroke="#475569", sw=1.8, rx=8))
    f.append(text(160, 100, "SoC / Мережевий MAC", size=13, bold=True, color=INK))
    f.append(text(160, 120, "(цифрова логіка, кадри, DMA)", size=10.5, color=MUTED))

    # Центральний блок: PHY-трансивер
    f.append(rect(390, 70, 260, 440, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(520, 100, "PHY-трансивер", size=13, bold=True, color=FIELD))
    f.append(text(520, 120, "(кодери, ЦАП/АЦП, DSP, AFE)", size=10.5, color=MUTED))

    # Правий блок: Трансформатор + RJ-45
    f.append(rect(730, 70, 190, 440, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=8))
    f.append(text(825, 100, "Гальванорозв'язка", size=12.5, bold=True, color="#b45309"))
    f.append(text(825, 120, "Трансформатори + RJ-45", size=10.5, color=MUTED))

    # Варіанти шин даних MAC <-> PHY
    f.append(rect(60, 145, 200, 230, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=5))
    f.append(text(160, 165, "Інтерфейси даних:", size=11, bold=True, color=INK))

    bus_y = 190
    buses = [
        ("MII (100M)", "4 біти @ 25 МГц, 16 ліній", NEG),
        ("RMII (100M)", "2 біти @ 50 МГц, 7 ліній", POS),
        ("RGMII (1G)", "4 біти DDR @ 125 МГц, 12 ліній", FIELD),
        ("SGMII (1G)", "1 пара SerDes 1.25 Гбод, 4-6 ліній", "#7c3aed"),
    ]
    for bname, bdesc, bcol in buses:
        f.append(textbox(160, bus_y, "%s\n%s" % (bname, bdesc), size=9.5, stroke=bcol, fill="#f8fafc", pad=4)[0])
        bus_y += 45

    # Стрілка шини даних
    f.append(arrow(280, 240, 390, 240, color=INK, sw=2.5))
    f.append(arrow(390, 260, 280, 260, color=INK, sw=2.5))
    f.append(text(335, 230, "TX Data / Clock", size=10, bold=True, color=INK))
    f.append(text(335, 275, "RX Data / Clock", size=10, bold=True, color=INK))

    # Шина керування MDIO/MDC
    f.append(rect(60, 395, 200, 95, fill="#eff6ff", stroke=NEG, sw=1.2, rx=5))
    f.append(text(160, 415, "Шина керування (SMI):", size=11, bold=True, color=NEG))
    f.append(text(160, 435, "MDC (тактування до 2.5 МГц)", size=10, color=INK))
    f.append(text(160, 455, "MDIO (двонаправлені дані)", size=10, color=INK))
    f.append(text(160, 475, "Регістри 0..31 (Clause 22/45)", size=9.5, color=MUTED))

    # Стрілки MDIO/MDC
    f.append(arrow(280, 430, 390, 430, color=NEG, sw=1.8))
    f.append(line(280, 455, 390, 455, color=NEG, sw=1.8))
    f.append(arrow(380, 455, 390, 455, color=NEG, sw=1.8))
    f.append(arrow(290, 455, 280, 455, color=NEG, sw=1.8))
    f.append(text(335, 423, "MDC →", size=9.5, bold=True, color=NEG))
    f.append(text(335, 470, "← MDIO →", size=9.5, bold=True, color=NEG))

    # Вміст PHY
    f.append(fitbox(410, 145, 220, 95, "Блок узгодження (PCS/PMA):\n- 4B5B / 8B10B / PAM кодери\n- Скремблер і дескремблер\n- Синхронізація бітів і слів", size=9.5, fill="#ffffff", stroke="#86efac"))
    f.append(fitbox(410, 255, 220, 115, "Аналогова частина (PMD/AFE):\n- ЦАП передавача (драйвер лінії)\n- АЦП високої швидкості\n- Ехо- та NEXT-компенсатори\n- Автовизначення Auto-MDIX", size=9.5, fill="#ffffff", stroke="#86efac"))
    f.append(fitbox(410, 395, 220, 95, "Регістровий файл MDIO:\n- 0x00 BMCR (керування режимом)\n- 0x01 BMSR (статус лінка)\n- 0x04 ANAR (здатності автопогодж.)\n- 0x09/0x0A (1000BASE-T Ctrl/Stat)", size=9.5, fill="#ffffff", stroke="#93c5fd"))

    # Зв'язок PHY -> Трансформатори
    for py, pname in [(190, "Пара A (TX+/TX-)"), (260, "Пара B (RX+/RX-)"), (330, "Пара C (TRD2+/TRD2-)"), (400, "Пара D (TRD3+/TRD3-)")]:
        f.append(line(650, py, 730, py, color="#b45309", sw=1.8))
        f.append(text(690, py - 6, pname, size=9.5, color="#92400e"))

    # Вміст трансформаторного вузла
    f.append(fitbox(745, 145, 160, 120, "Трансформатори (Magnetics):\n- Гальванічна ізоляція 1.5 кВ\n- Common-Mode Choke (CMC)\n- Захист від напруг і ESD\n- Термінація Боба Сміта", size=9.5, fill="#ffffff", stroke="#fcd34d"))
    f.append(fitbox(745, 290, 160, 100, "Конектор 8P8C (RJ-45):\n- 4 кручені пари UTP\n- Категорії Cat5e / Cat6\n- До 100 метрів лінії", size=9.5, fill="#ffffff", stroke="#fcd34d"))

    # Вихід на кабель праворуч
    f.append(arrow(825, 410, 825, 470, color=INK, sw=2.0))
    f.append(text(825, 490, "До 100 м кабелю UTP", size=11, bold=True, color=INK))

    render(os.path.join(IMG, "mac-phy-interfaces.svg"), W, H, *f)


if __name__ == "__main__":
    fig_line_coding_comparison()
    fig_gigabit_hybrid_dsp()
    fig_flp_burst_structure()
    fig_mac_phy_interfaces()
    print("Всі фігури згенеровано успішно.")
