# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. radio-transaction-phases: Енергетична анатомія радіотранзакції ───────────
def fig_radio_transaction_phases():
    W, H = 980, 420
    p = []

    p.append(text(W / 2, 26, 'Енергетична анатомія радіотранзакції: фази, струми та заряд кулонів', size=16, color=INK, bold=True))

    # Grid / axes
    x0, y0 = 80, 340
    w_ax = 840
    p.append(line(x0, y0, x0 + w_ax, y0, color=LINE, sw=1.5))
    p.append(line(x0, y0, x0, 70, color=LINE, sw=1.5))
    p.append(text(x0 - 10, 75, 'Струм I', size=11, color=INK, anchor='end', bold=True))
    p.append(text(x0 + w_ax + 10, y0 + 4, 'Час t', size=11, color=INK, anchor='start', bold=True))

    # Current scale lines
    levels = [
        (340, '0 мА / 1.5 мкА (Сон)', MUTED),
        (280, '10 мА (Прийом / PLL)', NEG),
        (180, '45 мА (+14 дБм)', FIELD),
        (100, '120 мА (+22 дБм)', POS)
    ]
    for y_lvl, label, col in levels:
        p.append(line(x0, y_lvl, x0 + w_ax, y_lvl, color='#e5e7eb', sw=1, dash='3,3'))
        p.append(text(x0 - 8, y_lvl + 4, label, size=10, color=col, anchor='end'))

    # Phase blocks on the timeline
    p.append(rect(90, 280, 40, 60, fill='#fef3c7', stroke='#d97706', sw=1.5, rx=3))
    p.append(rect(130, 180, 120, 160, fill='#fee2e2', stroke=POS, sw=1.8, rx=3))
    p.append('<rect x="130" y="100" width="120" height="80" rx="3" fill="#fca5a5" stroke="' + POS + '" stroke-width="1.2" stroke-dasharray="4,3"/>')
    p.append(rect(250, 338, 200, 2, fill='#e5e7eb', stroke=MUTED, sw=1.2, rx=1))
    p.append(rect(450, 280, 50, 60, fill='#e0e7ff', stroke=NEG, sw=1.5, rx=3))
    p.append(rect(500, 338, 200, 2, fill='#e5e7eb', stroke=MUTED, sw=1.2, rx=1))
    p.append(rect(700, 280, 50, 60, fill='#e0e7ff', stroke=NEG, sw=1.5, rx=3))
    p.append(rect(750, 338, 160, 2, fill='#e5e7eb', stroke=MUTED, sw=1.2, rx=1))

    # Phase Labels & Callouts
    b1, w1, h1 = textbox(110, 235, 'Старт PLL\n1–2 мс\n~5 мА', size=10, pad=4, fill='#fffbeb', stroke='#d97706', sw=1.2)
    p.append(b1)

    b2, w2, h2 = textbox(190, 140, 'Передача (Tx)\nToA: 50–1500 мс\n45–120 мА\nQ_tx = ∫ I_tx dt', size=10, pad=5, fill='#ffffff', stroke=POS, sw=1.5, bold=True)
    p.append(b2)

    b3, w3, h3 = textbox(350, 305, 'Очікування RX1 (сон 1.5 мкА)', size=10, pad=4, fill=FILL, stroke=MUTED, sw=1)
    p.append(b3)

    b4, w4, h4 = textbox(475, 235, 'Вікно RX1\n15–20 мс\n10 мА', size=10, pad=4, fill='#eef2ff', stroke=NEG, sw=1.2)
    p.append(b4)

    b5, w5, h5 = textbox(600, 305, 'Очікування RX2 (сон 1.5 мкА)', size=10, pad=4, fill=FILL, stroke=MUTED, sw=1)
    p.append(b5)

    b6, w6, h6 = textbox(725, 235, 'Вікно RX2\n15–20 мс\n10 мА', size=10, pad=4, fill='#eef2ff', stroke=NEG, sw=1.2)
    p.append(b6)

    b7, w7, h7 = textbox(835, 305, 'Глибокий сон до\nнаступної пачки', size=10, pad=4, fill=FILL, stroke=MUTED, sw=1)
    p.append(b7)

    # Time markers on x-axis
    p.append(text(90, y0 + 16, '0', size=10, color=MUTED))
    p.append(text(130, y0 + 16, 't_pll', size=10, color=MUTED))
    p.append(text(250, y0 + 16, 'ToA', size=10, color=MUTED))
    p.append(text(475, y0 + 16, 't = +1.0 с', size=10, color=MUTED))
    p.append(text(725, y0 + 16, 't = +2.0 с', size=10, color=MUTED))

    # Summary box at bottom
    b_sum, ws, hs = textbox(W / 2, 388, 'Сумарний заряд транзакції:  Q_транзакції = Q_pll + Q_tx + Q_rx1 + Q_rx2 + Q_сон  (Tx та Rx визначають 99.8% заряду)', size=11, pad=6, fill='#f8fafc', stroke=LINE, sw=1.3, bold=True)
    p.append(b_sum)

    render(os.path.join(OUT, 'radio-transaction-phases.svg'), W, H, *p)


# ── 2. toa-energy-comparison: Порівняння ToA та енергії за різної модуляції ────
def fig_toa_energy_comparison():
    W, H = 980, 420
    p = []

    p.append(text(W / 2, 26, 'Час в ефірі (ToA) та енергетична вартість 20 байтів корисного навантаження', size=16, color=INK, bold=True))

    rows = [
        ('FSK (50 kbps)', 5.6, 0.55, '5.6 мс', '0.55 мДж', '1× (база)', FIELD),
        ('LoRa SF7 / 125k', 61.7, 6.1, '61.7 мс', '6.1 мДж', '11×', FIELD),
        ('LoRa SF8 / 125k', 113.2, 11.2, '113 мс', '11.2 мДж', '20×', '#3b82f6'),
        ('LoRa SF9 / 125k', 205.8, 20.4, '206 мс', '20.4 мДж', '37×', '#6366f1'),
        ('LoRa SF10 / 125k', 370.7, 36.7, '371 мс', '36.7 мДж', '67×', '#d97706'),
        ('LoRa SF11 / 125k', 741.4, 73.4, '741 мс', '73.4 мДж', '133×', '#ea580c'),
        ('LoRa SF12 / 125k', 1482.8, 146.8, '1483 мс', '146.8 мДж', '267×', POS)
    ]

    y_start = 75
    row_h = 38
    bar_x = 180
    max_bar_w = 460
    max_toa = 1500.0

    p.append(text(90, y_start - 12, 'Конфігурація', size=11, color=MUTED, bold=True))
    p.append(text(bar_x + max_bar_w / 2, y_start - 12, 'Шкала часу в ефірі (ToA, мс)', size=11, color=MUTED, bold=True))
    p.append(text(720, y_start - 12, 'Тривалість', size=11, color=MUTED, bold=True))
    p.append(text(810, y_start - 12, 'Енергія (3.3В)', size=11, color=MUTED, bold=True))
    p.append(text(900, y_start - 12, 'Витрата', size=11, color=MUTED, bold=True))

    for i, (name, toa, mj, str_toa, str_mj, str_ratio, col) in enumerate(rows):
        yy = y_start + i * row_h
        if i % 2 == 1:
            p.append(rect(30, yy - 6, 920, row_h, fill='#f9fafb', stroke='none', rx=0))
        
        p.append(text(35, yy + 16, name, size=11, color=INK, anchor='start', bold=True))
        
        bw = max(4.0, (toa / max_toa) * max_bar_w)
        p.append(rect(bar_x, yy + 4, bw, 18, fill=col, stroke='none', rx=3))

        p.append(text(720, yy + 16, str_toa, size=11, color=INK, bold=True))
        p.append(text(810, yy + 16, str_mj, size=11, color=INK, bold=True))
        p.append(text(900, yy + 16, str_ratio, size=11, color=col, bold=True))

    b_bot, wb, hb = textbox(W / 2, 375, 'Перехід від SF7 до SF12 збільшує час в ефірі та витрату енергії у 24 рази!\nЗменшення розміру корисного навантаження та вибір максимального бітрейту — головні важелі автономності.', size=11, pad=6, fill='#fef2f2', stroke=POS, sw=1.2)
    p.append(b_bot)

    render(os.path.join(OUT, 'toa-energy-comparison.svg'), W, H, *p)


# ── 3. rx-strategies-comparison: Порівняння стратегій прослуховування ефіру ────
def fig_rx_strategies_comparison():
    W, H = 980, 420
    p = []

    p.append(text(W / 2, 26, 'Стратегії прийому: чому постійне прослуховування вбиває батарею', size=16, color=INK, bold=True))

    panels = [
        (40, 65, 280, 310, '1. Безперервний Rx (Always-On)', POS, [
            'Режим: Приймач увімкнений 100%',
            'Струм: I_rx = 10–15 мА постійно',
            'Дюті-цикл прийому: 100 %',
            'Затримка низхідного кадру: 0 мс',
            '',
            'Ціна автономності:',
            'Батарея 2400 мА·год помре за',
            '2400 / 12 мА = 200 годин (8.3 дня)',
            'Непридатно для автономних вузлів!'
        ]),
        (350, 65, 280, 310, '2. LoRaWAN Class A (Подійний Rx)', FIELD, [
            'Режим: Rx лише після власного Tx',
            'Струм: Сон 1.5 мкА, вікна RX1/RX2',
            'Дюті-цикл прийому: < 0.01 %',
            'Затримка: до наступного аплінку',
            '',
            'Ціна автономності:',
            'Два вікна по 15 мс щогодини',
            'Середній струм Rx: ~0.08 мкА',
            'Час життя від батареї: 5–10 років!',
            'Ідеально для давачів телеметрії.'
        ]),
        (660, 65, 280, 310, '3. Preamble Sampling / Sniff', NEG, [
            'Режим: Періодичний Sniff каналу',
            'Струм: Імпульс 1 мс кожні 500 мс',
            'Дюті-цикл прийому: ~0.2 %',
            'Затримка: не більше 500 мс',
            '',
            'Ціна автономності:',
            'Передавач шле довгу преамбулу,',
            'приймач споживає ~25 мкА середнього.',
            'Час життя: 3–5 років від батареї.',
            'Для двосторонніх sub-GHz вузлів.'
        ])
    ]

    for px, py, pw, ph, ptitle, pcol, plines in panels:
        p.append(rect(px, py, pw, ph, fill='#ffffff', stroke=pcol, sw=1.8, rx=6))
        p.append(rect(px, py, pw, 32, fill=pcol, stroke=pcol, sw=1.8, rx=0))
        p.append(text(px + pw / 2, py + 21, ptitle, size=11, color='#ffffff', bold=True))
        
        for li, line_text in enumerate(plines):
            is_bold = 'Ціна' in line_text or 'Час життя' in line_text or 'Непридатно' in line_text or 'Ідеально' in line_text or 'Батарея' in line_text
            col = POS if 'Непридатно' in line_text or 'помре' in line_text else (FIELD if '5–10 років' in line_text or 'Ідеально' in line_text else INK)
            p.append(text(px + 14, py + 58 + li * 24, line_text, size=11, color=col, anchor='start', bold=is_bold))

    b_bot, wb, hb = textbox(W / 2, 396, 'Прийом (Rx) забирає 10 мА — стільки ж, скільки передача на 0 дБм. Мінімізація часу слухання — головний закон енергоощадності.', size=11, pad=5, fill='#f8fafc', stroke=LINE, sw=1.2, bold=True)
    p.append(b_bot)

    render(os.path.join(OUT, 'rx-strategies-comparison.svg'), W, H, *p)


# ── 4. adr-loop-dynamics: Адаптивне керування швидкістю (ADR) та потужністю ────
def fig_adr_loop_dynamics():
    W, H = 980, 400
    p = []

    p.append(text(W / 2, 26, 'Замкнений контур адаптивної швидкості (ADR) та оптимізації потужності (TPC)', size=16, color=INK, bold=True))

    # Node Block
    p.append(rect(40, 75, 230, 260, fill='#f0fdf4', stroke=FIELD, sw=1.8, rx=6))
    p.append(text(155, 102, 'Автономний вузол (Node)', size=13, color=FIELD, bold=True))
    p.append(text(155, 130, '• Передає пакет (Tx)', size=11, color=INK))
    p.append(text(155, 155, '• Встановлює біт ADR = 1', size=11, color=INK))
    p.append(text(155, 180, '• Рахує ADR_ACK_CNT', size=11, color=INK))
    p.append(text(155, 215, 'Отримав команду LinkADRReq:', size=11, color=POS, bold=True))
    p.append(text(155, 240, '→ Знижує SF (зменшує ToA)', size=11, color=INK))
    p.append(text(155, 265, '→ Зменшує потужність Tx', size=11, color=INK))
    p.append(text(155, 300, 'Економія енергії: до 90%!', size=11, color=FIELD, bold=True))

    # Gateway / Network Server Block
    p.append(rect(710, 75, 230, 260, fill='#eff6ff', stroke=NEG, sw=1.8, rx=6))
    p.append(text(825, 102, 'Сервер мережі (LNS)', size=13, color=NEG, bold=True))
    p.append(text(825, 130, '• Збирає останні N=20 пакетів', size=11, color=INK))
    p.append(text(825, 155, '• Вимірює max(SNR) шлюзів', size=11, color=INK))
    p.append(text(825, 190, 'Розрахунок запасу лінії:', size=11, color=NEG, bold=True))
    p.append(text(825, 215, 'Margin = SNR_max − SNR_req − Margin_safe', size=10, color=INK))
    p.append(text(825, 250, 'Якщо Margin > 3 дБ:', size=11, color=POS, bold=True))
    p.append(text(825, 275, 'Формує LinkADRReq (DR↑, Power↓)', size=11, color=INK))
    p.append(text(825, 305, 'Шле команду у вікні RX1/RX2', size=11, color=INK))

    # Center Flow Arrows and Decision Box
    p.append(arrow(270, 135, 710, 135, color=FIELD, sw=2.2))
    p.append(text(490, 122, 'Uplink: Data + FCnt + ADR=1', size=11, color=FIELD, bold=True))

    p.append(arrow(710, 280, 270, 280, color=NEG, sw=2.2))
    p.append(text(490, 268, 'Downlink (RX1/RX2): MAC LinkADRReq', size=11, color=NEG, bold=True))

    # Fallback Mechanism Box (center)
    bf, wbf, hbf = textbox(490, 200, 'Захист від втрати зв\'язку (Fallback):\nЯкщо немає відповідей > ADR_ACK_LIMIT (64 кроки):\n1. Збільшити Tx Power до максимуму (+20 дБм)\n2. Якщо немає зв\'язку ще 32 кроки → Збільшити SF (знизити DR)', size=10, pad=6, fill='#fffbeb', stroke='#d97706', sw=1.4)
    p.append(bf)

    # Bottom summary
    b_sum, ws, hs = textbox(W / 2, 368, 'ADR автоматично оптимізує енергію кожного вузла: пристрої поблизу шлюзу переходять на SF7 та малу потужність, заощаджуючи батарею.', size=11, pad=5, fill='#f8fafc', stroke=LINE, sw=1.2, bold=True)
    p.append(b_sum)

    render(os.path.join(OUT, 'adr-loop-dynamics.svg'), W, H, *p)


if __name__ == '__main__':
    fig_radio_transaction_phases()
    fig_toa_energy_comparison()
    fig_rx_strategies_comparison()
    fig_adr_loop_dynamics()
    print('All figures generated successfully.')
