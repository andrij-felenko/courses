# -*- coding: utf-8 -*-
"""Фігури до теми «Коди виправлення помилок (FEC)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b9770e"
PURPLE = "#7d3c98"
TEAL = "#117a65"


# ── 1. Конвеєр передачі з FEC та переміжником ────────────────────────────────
def fig_fec_pipeline():
    W, H = 840, 250
    p = [text(W / 2, 24, "Конвеєр прямої корекції помилок (FEC) із переміжненням", size=15, bold=True)]

    # Блоки передавача
    tx_y = 75
    b_src = textbox(70, tx_y, "Джерело\nінформації\nk біт", size=10.5, pad=6, fill="#ffffff", stroke=LINE)
    b_enc = textbox(215, tx_y, "Кодер FEC\nнадлишковість\nn = k/R біт", size=10.5, pad=6, fill="#eaf0fd", stroke=NEG)
    b_intl = textbox(365, tx_y, "Переміжник (π)\nперетасування бітів\nпроти пакетів", size=10.5, pad=6, fill="#fef9e7", stroke=AMBER)
    b_mod = textbox(505, tx_y, "Модулятор\nBPSK / QAM\ns(t)", size=10.5, pad=6, fill="#ffffff", stroke=LINE)

    p.extend([b_src[0], b_enc[0], b_intl[0], b_mod[0]])
    p.append(arrow(115, tx_y, 155, tx_y, sw=1.5))
    p.append(arrow(275, tx_y, 305, tx_y, sw=1.5))
    p.append(arrow(425, tx_y, 465, tx_y, sw=1.5))

    # Канал
    b_ch = textbox(685, 125, "Зашумлений канал\nAWGN + завади\nпакети помилок", size=10.5, pad=8, fill="#fdecea", stroke=POS)
    p.append(b_ch[0])
    p.append(arrow(545, tx_y, 615, 115, sw=1.5))

    # Блоки приймача (нижній ряд, справа наліво)
    rx_y = 185
    b_demod = textbox(505, rx_y, "Демодулятор\nжорсткі біти або\nм'які LLR", size=10.5, pad=6, fill="#ffffff", stroke=LINE)
    b_deintl = textbox(365, rx_y, "Депереміжник (π⁻¹)\nвідновлення черги\nрозсіювання", size=10.5, pad=6, fill="#fef9e7", stroke=AMBER)
    b_dec = textbox(215, rx_y, "Декодер FEC\nвиправлення бітів\nоцінка k біт", size=10.5, pad=6, fill="#e8f8f5", stroke=FIELD)
    b_sink = textbox(70, rx_y, "Одержувач\nвідновлені дані\nk біт", size=10.5, pad=6, fill="#ffffff", stroke=LINE)

    p.extend([b_demod[0], b_deintl[0], b_dec[0], b_sink[0]])
    p.append(arrow(615, 135, 545, rx_y, sw=1.5))
    p.append(arrow(465, rx_y, 425, rx_y, sw=1.5))
    p.append(arrow(305, rx_y, 275, rx_y, sw=1.5))
    p.append(arrow(155, rx_y, 115, rx_y, sw=1.5))

    render(os.path.join(IMG, "fec-pipeline.svg"), W, H, *p)


# ── 2. Криві BER vs Eb/N0: Енергетичний виграш ──────────────────────────────
def fig_coding_gain_curve():
    W, H = 780, 430
    ox, oy = 90, 350
    aw, ah = 610, 280
    p = [text(W / 2, 26, "Криві ймовірності помилки (BER) та енергетичний виграш", size=15, bold=True)]

    # Сітка та осі
    p.append(arrow(ox, oy, ox + aw + 20, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - ah - 20, color=INK, sw=1.6))
    p.append(text(ox + aw + 20, oy + 25, "Eb/N0 (дБ) →", size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy - ah - 15, "BER", size=11, color=MUTED, anchor="end"))

    # Позначки осі Y (логарифмічні рівні)
    levels = [("10⁰", 0), ("10⁻¹", 0.17), ("10⁻²", 0.34), ("10⁻³", 0.51), ("10⁻⁴", 0.68), ("10⁻⁵", 0.85), ("10⁻⁶", 1.0)]
    for lbl, frac in levels:
        y = oy - ah * frac
        p.append(line(ox - 4, y, ox, y, color=MUTED, sw=1))
        p.append(line(ox, y, ox + aw, y, color="#e5e7eb", sw=0.8, dash="3,3"))
        p.append(text(ox - 8, y + 4, lbl, size=10, color=MUTED, anchor="end"))

    # Позначки осі X
    db_ticks = [("-2", 0.05), ("0", 0.18), ("2", 0.31), ("4", 0.44), ("6", 0.57), ("8", 0.70), ("10", 0.83), ("12", 0.96)]
    for lbl, frac in db_ticks:
        x = ox + aw * frac
        p.append(line(x, oy, x, oy + 4, color=MUTED, sw=1))
        p.append(text(x, oy + 18, lbl, size=10, color=MUTED, anchor="middle"))

    # 1. Некодований BPSK
    pts_uncoded = "95,75 140,110 200,160 280,220 370,270 470,310 590,345"
    p.append(f'<polyline points="{pts_uncoded}" fill="none" stroke="{LINE}" stroke-width="2.2" stroke-dasharray="5,3"/>')
    p.append(text(600, 335, "Некодований BPSK", size=10, color=INK, anchor="start"))

    # 2. Жорстке декодування (блоковий код БЧХ / РС)
    pts_hard = "105,72 170,120 250,190 330,265 420,325 470,348"
    p.append(f'<polyline points="{pts_hard}" fill="none" stroke="{NEG}" stroke-width="2.2"/>')
    p.append(text(475, 330, "Жорстке декодування (Hard)", size=10, color=NEG, anchor="start", bold=True))

    # 3. М'яке декодування (згортковий код Viterbi)
    pts_soft = "100,72 150,115 220,180 290,260 360,330 390,348"
    p.append(f'<polyline points="{pts_soft}" fill="none" stroke="{AMBER}" stroke-width="2.2"/>')
    p.append(text(395, 305, "М'яке декодування (Soft)", size=10, color=AMBER, anchor="start", bold=True))

    # 4. Сучасний турбо / LDPC код (крутий водоспад)
    pts_ldpc = "100,72 135,105 170,145 200,210 215,310 225,348"
    p.append(f'<polyline points="{pts_ldpc}" fill="none" stroke="{FIELD}" stroke-width="2.8"/>')
    tb_ldpc = textbox(280, 160, "LDPC / Turbo\n(водоспад)", size=9.5, pad=4, fill="#ffffff", stroke=FIELD, sw=1)
    p.append(tb_ldpc[0])
    p.append(line(240, 160, 185, 175, color=FIELD, sw=1, dash="2,2"))

    # 5. Межа Шеннона (вертикальна асимптота)
    shannon_x = ox + aw * 0.12
    p.append(line(shannon_x, oy, shannon_x, oy - ah, color=POS, sw=2, dash="4,2"))
    p.append(text(shannon_x + 6, oy - ah + 15, "Межа Шеннона", size=10.5, color=POS, bold=True))

    # Показ енергетичного виграшу (Coding Gain) на рівні BER = 10^-5
    y_target = oy - ah * 0.85
    p.append(line(ox, y_target, ox + aw * 0.85, y_target, color=POS, sw=1.2, dash="2,2"))

    x_uncoded_target = 580
    x_ldpc_target = 220
    p.append(circle(x_uncoded_target, y_target, 4, fill=LINE, stroke=LINE))
    p.append(circle(x_ldpc_target, y_target, 4, fill=FIELD, stroke=FIELD))

    # Двостороння стрілка виграшу
    p.append(line(x_ldpc_target, y_target, x_uncoded_target, y_target, color=POS, sw=2))
    p.append(arrow(x_ldpc_target + 35, y_target, x_ldpc_target, y_target, color=POS, sw=2))
    p.append(arrow(x_uncoded_target - 35, y_target, x_uncoded_target, y_target, color=POS, sw=2))

    p.append(text((x_ldpc_target + x_uncoded_target) / 2, y_target - 10, "Енергетичний виграш G_c ≈ 7–9 дБ", size=11, color=POS, bold=True))

    render(os.path.join(IMG, "coding-gain-curve.svg"), W, H, *p)


# ── 3. Блокові коди проти Згорткових (структурне порівняння) ─────────────────
def fig_block_vs_convolutional():
    W, H = 840, 340
    p = [text(W / 2, 24, "Структурні парадигми: блокові та неперервні (згорткові) коди", size=15, bold=True)]

    # Ліва половина: Блокові коди
    p.append(rect(30, 48, 370, 270, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    p.append(text(215, 72, "Блокові коди (n, k): Хеммінг, БЧХ, Рід–Соломон", size=11.5, color=NEG, bold=True))

    p.append(textbox(215, 115, "Інформаційний вектор m = [m₁, m₂, ..., mk]\nфіксована довжина k біт", size=10, pad=6, fill="#ffffff", stroke=LINE)[0])
    p.append(arrow(215, 138, 215, 160, sw=1.5))
    p.append(textbox(215, 185, "Множення на матрицю c = m · G\nабо синдромний поліном s(x)\nКодове слово c = [m | p] довжиною n біт", size=10, pad=6, fill="#eaf0fd", stroke=NEG)[0])
    p.append(textbox(215, 260, "• Автономні ізольовані блоки даних\n• Пам'ять між сусідніми блоками відсутня\n• Синдромна перевірка: H · cᵀ = 0", size=10, pad=6, fill="#ffffff", stroke=LINE)[0])

    # Права половина: Згорткові коди
    p.append(rect(440, 48, 370, 270, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(625, 72, "Неперервні коди: Згорткові (Trellis / Вітербі)", size=11.5, color=FIELD, bold=True))

    p.append(textbox(625, 115, "Неперервний потік бітів ... u_t, u_{t-1}, ...\nзсувні регістри з пам'яттю m тактів", size=10, pad=6, fill="#ffffff", stroke=LINE)[0])
    p.append(arrow(625, 138, 625, 160, sw=1.5))
    p.append(textbox(625, 185, "Згортка з поліномами g₁(D), g₂(D)\nвихідні біти (v₁ᵗ, v₂ᵗ) залежать від пам'яті\nДекодування за графом станів (Trellis)", size=10, pad=6, fill="#e8f8f5", stroke=FIELD)[0])
    p.append(textbox(625, 260, "• Потокова обробка без штучних меж\n• Довжина кодового обмеження K\n• Оптимальний пошук шляху за Вітербі", size=10, pad=6, fill="#ffffff", stroke=LINE)[0])

    render(os.path.join(IMG, "block-vs-convolutional.svg"), W, H, *p)


# ── 4. Переміжнення: Розсіювання пакетів помилок ────────────────────────────
def fig_interleaving():
    W, H = 840, 320
    p = [text(W / 2, 24, "Механізм переміжнення (Interleaving): розсіювання пакету помилок", size=15, bold=True)]

    # 1. Запис у матрицю по рядках
    p.append(text(140, 56, "1. Запис кодових слів по рядках", size=11, bold=True))
    mx, my = 50, 70
    cw, ch = 36, 26
    for r_idx in range(4):
        for c_idx in range(5):
            x = mx + c_idx * cw
            y = my + r_idx * ch
            p.append(rect(x, y, cw, ch, fill="#f4f6f8", stroke=LINE, sw=1, rx=2))
            p.append(text(x + cw/2, y + ch/2 + 4, f"b{r_idx}{c_idx}", size=9, color=INK))

    p.append(mtext(140, 195, ["Кожен рядок — слово коду,", "здатне виправити 1 помилку"], size=9.5, color=MUTED, anchor="middle"))

    # Стрілка зчитування по стовпчиках
    p.append(arrow(245, 115, 300, 115, color=AMBER, sw=2))
    p.append(mtext(272, 100, ["Передача", "по стовпцях"], size=9.5, color=AMBER, anchor="middle"))

    # 2. Канал з пакетом помилок
    p.append(text(415, 56, "2. Пакет помилок у каналі (4 біти підряд)", size=11, color=POS, bold=True))
    stream_x = 325
    stream_y = 95
    p.append(rect(stream_x, stream_y, 180, 50, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(mtext(stream_x + 90, stream_y + 20, ["Пакет завади вражає біти:", "[ b01, b11, b21, b31 ]"], size=10, color=POS, bold=True, anchor="middle"))

    # Стрілка депереміжнення
    p.append(arrow(520, 115, 575, 115, color=FIELD, sw=2))
    p.append(mtext(547, 100, ["Депереміжник", "(по рядках)"], size=9.5, color=FIELD, anchor="middle"))

    # 3. Відновлена матриця на приймачі
    p.append(text(690, 56, "3. Розсіяні поодинокі помилки", size=11, color=FIELD, bold=True))
    rx, ry = 600, 70
    for r_idx in range(4):
        for c_idx in range(5):
            x = rx + c_idx * cw
            y = ry + r_idx * ch
            is_err = (c_idx == 1)
            fill_c = "#fdecea" if is_err else "#e8f8f5"
            stroke_c = POS if is_err else FIELD
            p.append(rect(x, y, cw, ch, fill=fill_c, stroke=stroke_c, sw=1.5 if is_err else 1, rx=2))
            p.append(text(x + cw/2, y + ch/2 + 4, f"b{r_idx}{c_idx}", size=9, color=POS if is_err else INK, bold=is_err))

    p.append(mtext(690, 195, ["У кожному рядку — лише 1 помилка!", "Кодер легко виправляє всі 4 біти."], size=9.5, color=FIELD, anchor="middle", bold=True))

    p.append(line(50, 240, 790, 240, color="#d1d5db", sw=1, dash="4,4"))
    p.append(text(W / 2, 265, "Без переміжнення пакет із 4 помилок знищив би одне кодове слово (перевищивши ліміт t = 1).", size=10.5, color=INK, anchor="middle"))
    p.append(text(W / 2, 285, "Завдяки переміжненню концентрована пачка перетворюється на безпечні некорельовані бітові інверсії.", size=10, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, "interleaving.svg"), W, H, *p)


# ── 5. Еволюція наближення до межі Шеннона ──────────────────────────────────
def fig_shannon_gap_evolution():
    W, H = 860, 370
    p = [text(W / 2, 24, "Історичне наближення кодів корекції до границі Шеннона", size=15, bold=True)]

    # 6 рівномірно розташованих етапів у хронологічному порядку
    ox = 50
    step_w = 126
    oy = 270

    p.append(arrow(ox - 10, oy, ox + 6 * step_w + 20, oy, color=INK, sw=1.8))
    p.append(text(ox + 6 * step_w + 20, oy + 25, "Хронологія епох →", size=10.5, color=MUTED, anchor="end"))

    # Межа Шеннона в кінці осі
    sh_x = ox + 6 * step_w
    p.append(line(sh_x, oy - 220, sh_x, oy + 8, color=POS, sw=2, dash="3,3"))
    p.append(text(sh_x, oy + 20, "Границя Шеннона\n(0 дБ відриву)", size=9.5, color=POS, bold=True, anchor="middle"))

    codes = [
        ("1950", "Хеммінг", "5.5 дБ", NEG, 100, "Найпростіші лінійні\nблокові коди"),
        ("1967", "Вітербі", "3.8 дБ", NEG, 170, "Згорткові коди\nкосмос Mariner"),
        ("1977", "RS + Viterbi", "2.2 дБ", AMBER, 100, "Каскадні схеми\nVoyager, DVB-S"),
        ("1993", "Турбо-коди", "0.7 дБ", FIELD, 170, "Ітеративні коди\n3G / 4G LTE"),
        ("1996", "LDPC", "0.25 дБ", FIELD, 100, "Графи Таннера\n5G, Wi-Fi 6, 10GbE"),
        ("2009", "Полярні", "0.08 дБ", TEAL, 170, "Поляризація каналу\n5G Control")
    ]

    for i, (year, name, gap, col, h_box, desc) in enumerate(codes):
        x = ox + i * step_w + step_w / 2
        y_box = oy - h_box

        # Точка на часовій осі
        p.append(circle(x, oy, 4, fill=col, stroke=INK, sw=1.2))
        p.append(text(x, oy + 16, year, size=10, color=INK, bold=True, anchor="middle"))

        # Зв'язкова лінія від осі до боксу
        p.append(line(x, oy - 6, x, y_box + 30, color=col, sw=1.2, dash="2,2"))

        # Картка опису коду
        card_txt = f"{name}\nВідрив: {gap}\n{desc}"
        tb = textbox(x, y_box, card_txt, size=9, pad=5, fill="#ffffff", stroke=col, sw=1.5)
        p.append(tb[0])

    p.append(text(W / 2, 335, "За 60 років розрив між теоретичною ємністю каналу та реальними алгоритмами скоротився з 5.5 дБ до < 0.1 дБ", size=11, color=INK, anchor="middle", bold=True))

    render(os.path.join(IMG, "shannon-gap-evolution.svg"), W, H, *p)


def main():
    fig_fec_pipeline()
    fig_coding_gain_curve()
    fig_block_vs_convolutional()
    fig_interleaving()
    fig_shannon_gap_evolution()
    print("All figures generated successfully.")


if __name__ == "__main__":
    main()
