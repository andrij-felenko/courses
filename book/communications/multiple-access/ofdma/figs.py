# -*- coding: utf-8 -*-
"""Фігури до теми «OFDMA: множинний доступ на ортогональних піднесних».
Запуск:  py -3 figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Порівняння виділення ресурсу: OFDM (Wi-Fi 5) vs OFDMA (Wi-Fi 6 / 5G) ───
def fig_ofdm_vs_ofdma_allocation():
    W, H = 960, 480
    f = []

    # Заголовок лівої та правої частин
    f.append(text(240, 36, "OFDM (один користувач у часовий слот)", 15, INK, "middle", bold=True))
    f.append(text(720, 36, "OFDMA (множинний доступ у часі та частоті)", 15, FIELD, "middle", bold=True))

    # Кольори для 4 користувачів
    u_colors = [
        ("#2457d6", "#eaf0fb"),  # Користувач 1 (синій)
        ("#27ae60", "#eaf6ee"),  # Користувач 2 (зелений)
        ("#d35400", "#fbeee6"),  # Користувач 3 (помаранчевий)
        ("#8e44ad", "#f4ecf7"),  # Користувач 4 (фіолетовий)
    ]

    # ── Ліва діаграма: OFDM ──
    ox_l, oy_l = 80, 80
    grid_w, grid_h = 320, 260

    # Осі
    f.append(line(ox_l, oy_l + grid_h, ox_l + grid_w + 30, oy_l + grid_h, color=LINE, sw=1.8))
    f.append(arrow(ox_l + grid_w + 20, oy_l + grid_h, ox_l + grid_w + 35, oy_l + grid_h, color=LINE, sw=1.8))
    f.append(text(ox_l + grid_w + 35, oy_l + grid_h + 20, "Час (t)", 11, MUTED, "end"))

    f.append(line(ox_l, oy_l + grid_h, ox_l, oy_l - 20, color=LINE, sw=1.8))
    f.append(arrow(ox_l, oy_l - 10, ox_l, oy_l - 25, color=LINE, sw=1.8))
    f.append(text(ox_l - 12, oy_l - 12, "Частота (f)", 11, MUTED, "end"))

    # Блоки часу в OFDM (кожен користувач займає ВСЮ смугу послідовно)
    slot_w = grid_w / 4
    for i in range(4):
        bx = ox_l + i * slot_w
        by = oy_l
        bw = slot_w - 4
        bh = grid_h
        stroke_c, fill_c = u_colors[i]
        f.append(rect(bx, by, bw, bh, fill=fill_c, stroke=stroke_c, sw=1.6, rx=4))
        f.append(text(bx + bw / 2, by + bh / 2 - 10, f"Слот {i+1}", 12, stroke_c, "middle", bold=True))
        f.append(text(bx + bw / 2, by + bh / 2 + 10, f"Абонент {chr(65+i)}", 11, INK, "middle"))

    # Пояснення під OFDM
    f.append(text(ox_l + grid_w / 2, oy_l + grid_h + 46, "Монопольний доступ до каналу:", 12, INK, "middle", bold=True))
    f.append(text(ox_l + grid_w / 2, oy_l + grid_h + 66, "Короткий пакет VoIP блокує всю смугу 20/80 МГц;", 11, MUTED, "middle"))
    f.append(text(ox_l + grid_w / 2, oy_l + grid_h + 84, "висока затримка очікування в черзі", 11, POS, "middle"))

    # ── Права діаграма: OFDMA ──
    ox_r, oy_r = 560, 80

    # Осі
    f.append(line(ox_r, oy_r + grid_h, ox_r + grid_w + 30, oy_r + grid_h, color=LINE, sw=1.8))
    f.append(arrow(ox_r + grid_w + 20, oy_r + grid_h, ox_r + grid_w + 35, oy_r + grid_h, color=LINE, sw=1.8))
    f.append(text(ox_r + grid_w + 35, oy_r + grid_h + 20, "Час (t)", 11, MUTED, "end"))

    f.append(line(ox_r, oy_r + grid_h, ox_r, oy_r - 20, color=LINE, sw=1.8))
    f.append(arrow(ox_r, oy_r - 10, ox_r, oy_r - 25, color=LINE, sw=1.8))
    f.append(text(ox_r - 12, oy_r - 12, "Частота (f)", 11, MUTED, "end"))

    # Сітка OFDMA: 4 користувачі ділять спектр паралельно в кожному слоті
    t_step = grid_w / 3
    # Слот 1
    # U1 (A) верхня частина
    f.append(rect(ox_r, oy_r, t_step - 4, grid_h * 0.45, fill=u_colors[0][1], stroke=u_colors[0][0], sw=1.6, rx=4))
    f.append(text(ox_r + t_step / 2 - 2, oy_r + grid_h * 0.22, "Абонент A", 11, u_colors[0][0], "middle", bold=True))

    # U2 (B) середня частина
    f.append(rect(ox_r, oy_r + grid_h * 0.47, t_step - 4, grid_h * 0.25, fill=u_colors[1][1], stroke=u_colors[1][0], sw=1.6, rx=4))
    f.append(text(ox_r + t_step / 2 - 2, oy_r + grid_h * 0.59, "Абонент B", 11, u_colors[1][0], "middle", bold=True))

    # U3 (C) нижня частина
    f.append(rect(ox_r, oy_r + grid_h * 0.74, t_step - 4, grid_h * 0.25, fill=u_colors[2][1], stroke=u_colors[2][0], sw=1.6, rx=4))
    f.append(text(ox_r + t_step / 2 - 2, oy_r + grid_h * 0.86, "Абонент C", 11, u_colors[2][0], "middle", bold=True))

    # Слот 2
    # U4 (D) верхня четвертина
    f.append(rect(ox_r + t_step, oy_r, t_step - 4, grid_h * 0.25, fill=u_colors[3][1], stroke=u_colors[3][0], sw=1.6, rx=4))
    f.append(text(ox_r + t_step * 1.5 - 2, oy_r + grid_h * 0.12, "Абонент D", 11, u_colors[3][0], "middle", bold=True))

    # U1 (A) решта
    f.append(rect(ox_r + t_step, oy_r + grid_h * 0.27, t_step - 4, grid_h * 0.72, fill=u_colors[0][1], stroke=u_colors[0][0], sw=1.6, rx=4))
    f.append(text(ox_r + t_step * 1.5 - 2, oy_r + grid_h * 0.63, "Абонент A (Відео)", 11, u_colors[0][0], "middle", bold=True))

    # Слот 3: 4 клієнти
    for k in range(4):
        kh = (grid_h - 12) / 4
        ky = oy_r + k * (kh + 4)
        f.append(rect(ox_r + 2 * t_step, ky, t_step - 4, kh, fill=u_colors[k][1], stroke=u_colors[k][0], sw=1.6, rx=4))
        f.append(text(ox_r + 2.5 * t_step - 2, ky + kh / 2 + 4, f"Абонент {chr(65+k)}", 10.5, u_colors[k][0], "middle", bold=True))

    # Пояснення під OFDMA
    f.append(text(ox_r + grid_w / 2, oy_l + grid_h + 46, "Паралельний доступ у 2D-сітці:", 12, FIELD, "middle", bold=True))
    f.append(text(ox_r + grid_w / 2, oy_l + grid_h + 66, "Спектр ділиться на дрібні субканали (RU / RB);", 11, MUTED, "middle"))
    f.append(text(ox_r + grid_w / 2, oy_l + grid_h + 84, "одночасне обслуговування багатьох клієнтів", 11, FIELD, "middle"))

    render(os.path.join(IMG, "ofdm-vs-ofdma-allocation.svg"), W, H, *f,
           title="Порівняння виділення ресурсів у часі та частоті між OFDM та OFDMA")


# ── 2. Двовимірна часово-частотна сітка та ресурсні блоки (RB/RU) ─────────────
def fig_time_frequency_grid():
    W, H = 940, 520
    f = []

    ox, oy = 90, 60
    gw, gh = 640, 360

    f.append(text(W / 2, 28, "Двовимірна сітка ресурсу (Time-Frequency Resource Grid)", 15, INK, "middle", bold=True))

    # Осі
    f.append(line(ox, oy + gh, ox + gw + 40, oy + gh, color=LINE, sw=2))
    f.append(arrow(ox + gw + 30, oy + gh, ox + gw + 50, oy + gh, color=LINE, sw=2))
    f.append(text(ox + gw + 50, oy + gh + 22, "Час (OFDM-символи / слоти)", 11.5, INK, "end", bold=True))

    f.append(line(ox, oy + gh, ox, oy - 25, color=LINE, sw=2))
    f.append(arrow(ox, oy - 15, ox, oy - 35, color=LINE, sw=2))
    f.append(text(ox - 14, oy - 16, "Частота (піднесні Δf)", 11.5, INK, "end", bold=True))

    # Клітинки сітки (14 символів у часі × 12 піднесних у частоті для 1 PRB)
    num_cols = 14
    num_rows = 12
    cw = gw / num_cols
    ch = gh / num_rows

    for r in range(num_rows):
        for c in range(num_cols):
            x = ox + c * cw
            y = oy + r * ch

            is_pilot = (r in [1, 7] and c in [0, 4, 7, 11]) or (r in [4, 10] and c in [2, 6, 9, 13])
            is_sample_re = (r == 3 and c == 8)

            if is_sample_re:
                fill = "#fde8e8"
                stroke = POS
                sw = 2.0
            elif is_pilot:
                fill = "#fef9e7"
                stroke = "#f39c12"
                sw = 1.2
            else:
                fill = "#f4f8fb"
                stroke = "#bcd4ec"
                sw = 0.8

            f.append(rect(x, y, cw, ch, fill=fill, stroke=stroke, sw=sw, rx=1))

    # Виділення всього Ресурсного Блоку (PRB)
    f.append(rect(ox - 2, oy - 2, gw + 4, gh + 4, fill="none", stroke=NEG, sw=2.5, rx=6))

    # Розмітка частоти
    f.append(line(ox - 10, oy, ox - 2, oy, color=NEG, sw=1.5))
    f.append(line(ox - 10, oy + gh, ox - 2, oy + gh, color=NEG, sw=1.5))
    f.append(line(ox - 10, oy, ox - 10, oy + gh, color=NEG, sw=1.5))
    f.append(text(ox - 20, oy + gh / 2 - 8, "12 піднесних", 11, NEG, "end", bold=True))
    f.append(text(ox - 20, oy + gh / 2 + 10, "(180 кГц при Δf = 15 кГц)", 10, MUTED, "end"))

    # Розмітка часу
    f.append(line(ox, oy + gh + 8, ox, oy + gh + 16, color=NEG, sw=1.5))
    f.append(line(ox + gw, oy + gh + 8, ox + gw, oy + gh + 16, color=NEG, sw=1.5))
    f.append(line(ox, oy + gh + 16, ox + gw, oy + gh + 16, color=NEG, sw=1.5))
    f.append(text(ox + gw / 2, oy + gh + 34, "1 слот = 14 OFDM-символів (1.0 мс або 0.5 мс)", 11, NEG, "middle", bold=True))

    # Виноски праворуч
    leg_x = ox + gw + 35
    # Ресурсний блок
    f.append(rect(leg_x, oy + 20, 160, 64, fill="#edf3fc", stroke=NEG, sw=1.5, rx=4))
    f.append(text(leg_x + 80, oy + 42, "Ресурсний блок (RB)", 11.5, NEG, "middle", bold=True))
    f.append(text(leg_x + 80, oy + 62, "12 піднесних × 1 слот", 10.5, INK, "middle"))

    # Ресурсний елемент (RE)
    f.append(rect(leg_x, oy + 110, 160, 64, fill="#fde8e8", stroke=POS, sw=1.5, rx=4))
    f.append(text(leg_x + 80, oy + 132, "Ресурсний елемент (RE)", 11.5, POS, "middle", bold=True))
    f.append(text(leg_x + 80, oy + 152, "1 піднесна × 1 символ", 10.5, INK, "middle"))

    # Пілотні / опорні сигнали (RS)
    f.append(rect(leg_x, oy + 200, 160, 64, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=4))
    f.append(text(leg_x + 80, oy + 222, "Опорний пілот (RS)", 11.5, "#d35400", "middle", bold=True))
    f.append(text(leg_x + 80, oy + 242, "Для оцінки каналу H(f)", 10.5, INK, "middle"))

    # Стрілка на RE
    re_cx = ox + 8 * cw + cw / 2
    re_cy = oy + 3 * ch + ch / 2
    f.append(line(re_cx, re_cy, leg_x - 10, oy + 142, color=POS, sw=1.4, dash="3 3"))
    f.append(circle(re_cx, re_cy, 4, fill=POS, stroke=POS))

    render(os.path.join(IMG, "time-frequency-grid-rb.svg"), W, H, *f,
           title="Двовимірна сітка ресурсу: ресурсний елемент (RE), ресурсний блок (RB) та опорні пілоти")


# ── 3. Багатокористувацька різноманітність (Multiuser Diversity) ───────────────
def fig_multiuser_diversity():
    W, H = 920, 460
    f = []

    ox, oy = 70, 70
    gw, gh = 780, 240

    f.append(text(W / 2, 32, "Багатокористувацька різноманітність (Multiuser Diversity Gain)", 15, INK, "middle", bold=True))

    # Осі
    f.append(line(ox, oy + gh, ox + gw + 30, oy + gh, color=LINE, sw=1.8))
    f.append(arrow(ox + gw + 20, oy + gh, ox + gw + 35, oy + gh, color=LINE, sw=1.8))
    f.append(text(ox + gw + 35, oy + gh + 20, "Частота / Піднесні (f)", 11.5, MUTED, "end"))

    f.append(line(ox, oy + gh, ox, oy - 20, color=LINE, sw=1.8))
    f.append(arrow(ox, oy - 10, ox, oy - 25, color=LINE, sw=1.8))
    f.append(text(ox - 12, oy - 12, "Якість каналу (SINR / |H(f)|²)", 11.5, MUTED, "end"))

    # Генеруємо 3 різні криві частотно-селективного завмирання для трьох користувачів
    def h_user(k, shift, freq_scale):
        val = math.sin(k * freq_scale + shift) * 0.35 + math.cos(k * freq_scale * 2.1 + shift * 1.5) * 0.2 + 0.5
        return max(0.08, min(0.95, val))

    pts_a, pts_b, pts_c = [], [], []
    num_pts = 120
    for i in range(num_pts):
        x = ox + (i / (num_pts - 1)) * gw
        norm_i = i / num_pts
        ya = oy + gh * (1.0 - h_user(norm_i, 0.2, 7.5))
        yb = oy + gh * (1.0 - h_user(norm_i, 2.4, 6.2))
        yc = oy + gh * (1.0 - h_user(norm_i, 4.6, 8.8))
        pts_a.append((x, ya))
        pts_b.append((x, yb))
        pts_c.append((x, yc))

    def make_path(pts):
        return "M " + " L ".join(f"{px:.1f},{py:.1f}" for px, py in pts)

    # Криві
    f.append(f'<path d="{make_path(pts_a)}" fill="none" stroke="#2457d6" stroke-width="1.8" stroke-dasharray="4 2"/>')
    f.append(f'<path d="{make_path(pts_b)}" fill="none" stroke="#27ae60" stroke-width="1.8" stroke-dasharray="4 2"/>')
    f.append(f'<path d="{make_path(pts_c)}" fill="none" stroke="#e67e22" stroke-width="1.8" stroke-dasharray="4 2"/>')

    # Огинаюча максимуму
    pts_max = []
    for i in range(num_pts):
        x = pts_a[i][0]
        best_y = min(pts_a[i][1], pts_b[i][1], pts_c[i][1])
        pts_max.append((x, best_y))

    # Заливка виграшу шедулера
    poly_fill = f"M {ox},{oy+gh} " + " ".join(f"L {px:.1f},{py:.1f}" for px, py in pts_max) + f" L {ox+gw},{oy+gh} Z"
    f.append(f'<path d="{poly_fill}" fill="#eafaf1" opacity="0.6"/>')
    f.append(f'<path d="{make_path(pts_max)}" fill="none" stroke="#117a37" stroke-width="3.2"/>')

    # Легенда
    leg_y = oy + gh + 44
    f.append(line(ox + 40, leg_y, ox + 75, leg_y, color="#2457d6", sw=2, dash="4 2"))
    f.append(text(ox + 82, leg_y + 4, "Користувач A", 11, "#2457d6", "start", bold=True))

    f.append(line(ox + 200, leg_y, ox + 235, leg_y, color="#27ae60", sw=2, dash="4 2"))
    f.append(text(ox + 242, leg_y + 4, "Користувач B", 11, "#27ae60", "start", bold=True))

    f.append(line(ox + 360, leg_y, ox + 395, leg_y, color="#e67e22", sw=2, dash="4 2"))
    f.append(text(ox + 402, leg_y + 4, "Користувач C", 11, "#e67e22", "start", bold=True))

    f.append(line(ox + 520, leg_y, ox + 560, leg_y, color="#117a37", sw=3.2))
    f.append(text(ox + 568, leg_y + 4, "Опортуністичний вибір max(SINR) — сумарна ємність зростає", 11.5, "#117a37", "start", bold=True))

    render(os.path.join(IMG, "multiuser-diversity-gain.svg"), W, H, *f,
           title="Багатокористувацька різноманітність: планувальник віддає кожну піднесу тому абоненту, у якого там пік SINR")


# ── 4. Синхронізація у висхідному каналі (Uplink OFDMA: TA, CFO, Power) ────────
def fig_ul_ofdma_sync():
    W, H = 940, 470
    f = []

    f.append(text(W / 2, 30, "Висхідний канал (Uplink OFDMA): три виміри синхронізації", 15, INK, "middle", bold=True))

    # Станція (AP / Base Station) праворуч
    ap_x, ap_y = 780, 200
    f.append(rect(ap_x - 50, ap_y - 60, 110, 180, fill="#2c3e50", stroke="#1a252f", sw=2, rx=8))
    f.append(text(ap_x + 5, ap_y - 30, "Базова станція", 12, "#ffffff", "middle", bold=True))
    f.append(text(ap_x + 5, ap_y - 12, "/ Точка доступу", 11, "#ecf0f1", "middle"))
    f.append(text(ap_x + 5, ap_y + 25, "Спільний FFT", 11, "#1abc9c", "middle", bold=True))
    f.append(text(ap_x + 5, ap_y + 45, "Один часовий", 10, "#bdc3c7", "middle"))
    f.append(text(ap_x + 5, ap_y + 62, "інтервал демодуляції", 10, "#bdc3c7", "middle"))

    # Абоненти ліворуч на різній відстані
    # UE 1 (близький)
    u1_x, u1_y = 120, 100
    f.append(rect(u1_x - 50, u1_y - 35, 100, 70, fill="#edf3fc", stroke=NEG, sw=1.6, rx=6))
    f.append(text(u1_x, u1_y - 12, "Абонент 1 (Близько)", 11, NEG, "middle", bold=True))
    f.append(text(u1_x, u1_y + 8, "RU #1 (f₁..f₂₆)", 10, INK, "middle"))
    f.append(text(u1_x, u1_y + 24, "d = 15 м", 9.5, MUTED, "middle"))

    # UE 2 (далекий)
    u2_x, u2_y = 120, 290
    f.append(rect(u2_x - 50, u2_y - 35, 100, 70, fill="#fbeee6", stroke="#d35400", sw=1.6, rx=6))
    f.append(text(u2_x, u2_y - 12, "Абонент 2 (Далеко)", 11, "#d35400", "middle", bold=True))
    f.append(text(u2_x, u2_y + 8, "RU #2 (f₂₇..f₅₂)", 10, INK, "middle"))
    f.append(text(u2_x, u2_y + 24, "d = 350 м", 9.5, MUTED, "middle"))

    # Лінії передачі
    f.append(line(u1_x + 50, u1_y, ap_x - 50, ap_y - 20, color=NEG, sw=2))
    f.append(arrow(ap_x - 65, ap_y - 23, ap_x - 50, ap_y - 20, color=NEG, sw=2))

    f.append(line(u2_x + 50, u2_y, ap_x - 50, ap_y + 20, color="#d35400", sw=2))
    f.append(arrow(ap_x - 65, ap_y + 17, ap_x - 50, ap_y + 20, color="#d35400", sw=2))

    # 3 блоки вимог синхронізації посередині
    # 1. Часова синхронізація (Timing Advance)
    f.append(rect(280, 80, 380, 66, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    f.append(text(470, 102, "1. Час: Випередження передачі (Timing Advance, TA)", 11.5, NEG, "middle", bold=True))
    f.append(text(470, 122, "Далекий абонент стартує раніше, щоб обидва сигнали потрапили в CP", 10, INK, "middle"))
    f.append(text(470, 136, "Помилка |Δt| < 0.1 · T_cp (інакше втрата ортогональності)", 9.5, MUTED, "middle"))

    # 2. Частотна синхронізація (CFO)
    f.append(rect(280, 170, 380, 66, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    f.append(text(470, 192, "2. Частота: Компенсація зсуву несучої (CFO Correction)", 11.5, POS, "middle", bold=True))
    f.append(text(470, 212, "Різниця гетеродинів спричиняє міжканальну заваду (ICI) між RU", 10, INK, "middle"))
    f.append(text(470, 226, "Точність |Δf_cfo| < 1–2% від кроку Δf", 9.5, MUTED, "middle"))

    # 3. Керування потужністю (UL Power Control)
    f.append(rect(280, 260, 380, 66, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    f.append(text(470, 282, "3. Потужність: Контроль рівнів (UL Power Control)", 11.5, FIELD, "middle", bold=True))
    f.append(text(470, 302, "Близький сигнал не повинен засліпити АЦП і заглушити далекого", 10, INK, "middle"))
    f.append(text(470, 316, "Вирівнювання потужності на вході базової станції (усунення Near-Far)", 9.5, MUTED, "middle"))

    # Керуючий кадр Trigger Frame / DCI
    f.append(rect(280, 350, 480, 50, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=6))
    f.append(text(520, 370, "Керування через Downlink Trigger Frame (Wi-Fi 6) або DCI (LTE/5G):", 11, "#d35400", "middle", bold=True))
    f.append(text(520, 388, "Базова станція диктує кожному: номер RU/RB, точний час старту, схему MCS та цільову потужність", 9.5, INK, "middle"))

    render(os.path.join(IMG, "ul-ofdma-synchronization.svg"), W, H, *f,
           title="Синхронізація у висхідному каналі UL-OFDMA: узгодження за часом (TA), частотою (CFO) та потужністю")


# ── 5. OFDMA проти SC-FDMA (DFT-s-OFDM): архітектура та PAPR ───────────────────
def fig_sc_fdma_vs_ofdma():
    W, H = 940, 500
    f = []

    f.append(text(W / 2, 28, "OFDMA проти SC-FDMA (DFT-Spread OFDM): чому висхідний канал потребує меншого PAPR", 14.5, INK, "middle", bold=True))

    # ── Верхня схема: Класичний OFDMA передавач ──
    oy1 = 60
    f.append(text(60, oy1 + 18, "OFDMA (Downlink LTE/5G, Wi-Fi 6):", 12.5, NEG, "start", bold=True))

    blocks_ofdm = [
        ("Біти даних", 100, "#f4f6f8", LINE),
        ("QAM\nМодулятор", 110, "#edf3fc", NEG),
        ("Розподіл по\nпіднесних M", 125, "#edf3fc", NEG),
        ("N-точковий\nIFFT", 110, "#eaf6ee", FIELD),
        ("Додавання\nCP", 100, "#fef9e7", "#d35400"),
        ("Вихідний сигнал:\nВисокий PAPR (~10-12 дБ)", 160, "#fde8e8", POS),
    ]

    bx = 60
    for i, (name, bw, bg_c, str_c) in enumerate(blocks_ofdm):
        f.append(rect(bx, oy1 + 35, bw, 52, fill=bg_c, stroke=str_c, sw=1.5, rx=5))
        f.append(mtext(bx + bw / 2, oy1 + 55, name, size=10.5, color=str_c, bold=True))
        if i < len(blocks_ofdm) - 1:
            f.append(line(bx + bw, oy1 + 61, bx + bw + 18, oy1 + 61, color=LINE, sw=1.5))
            f.append(arrow(bx + bw + 10, oy1 + 61, bx + bw + 20, oy1 + 61, color=LINE, sw=1.5))
            bx += bw + 20

    # ── Нижня схема: SC-FDMA передавач ──
    oy2 = 200
    f.append(text(60, oy2 + 18, "SC-FDMA / DFT-s-OFDM (Uplink LTE / опція 5G NR):", 12.5, FIELD, "start", bold=True))

    blocks_sc = [
        ("Біти даних", 90, "#f4f6f8", LINE),
        ("QAM\nМодулятор", 95, "#edf3fc", NEG),
        ("M-точковий\nDFT (прекодування)", 135, "#e8f8f5", "#16a085"),
        ("Розподіл по\nпіднесних M із N", 125, "#edf3fc", NEG),
        ("N-точковий\nIDFT", 100, "#eaf6ee", FIELD),
        ("Додавання\nCP", 85, "#fef9e7", "#d35400"),
        ("Низький PAPR\n(~6-8 дБ, −3 дБ)", 140, "#eaf6ee", FIELD),
    ]

    bx = 60
    for i, (name, bw, bg_c, str_c) in enumerate(blocks_sc):
        f.append(rect(bx, oy2 + 35, bw, 52, fill=bg_c, stroke=str_c, sw=1.5, rx=5))
        f.append(mtext(bx + bw / 2, oy2 + 55, name, size=10, color=str_c, bold=True))
        if i < len(blocks_sc) - 1:
            f.append(line(bx + bw, oy2 + 61, bx + bw + 16, oy2 + 61, color=LINE, sw=1.5))
            f.append(arrow(bx + bw + 8, oy2 + 61, bx + bw + 18, oy2 + 61, color=LINE, sw=1.5))
            bx += bw + 18

    # Пояснювальна панель унизу
    py = 310
    f.append(rect(60, py, 820, 160, fill="#fbfcfd", stroke="#d5dbdb", sw=1.5, rx=8))
    f.append(text(470, py + 26, "Чому попереднє перетворення Фур'є (DFT-прекодування) рятує батарею смартфона:", 12, INK, "middle", bold=True))

    f.append(text(80, py + 56, "• В OFDMA кожен символ QAM модулює окрему гармоніку в частоті; IFFT складає їхні фази, створюючи випадкові гострі сплески потужності.", 10.5, MUTED, "start"))
    f.append(text(80, py + 78, "• Підсилювач потужності (PA) змушений працювати з великим запасом (Back-off ~8-10 дБ) у нелінійній зоні, марнуючи енергію батареї.", 10.5, POS, "start"))
    f.append(text(80, py + 102, "• В SC-FDMA додатковий M-точковий DFT «розмазує» кожен символ QAM по всіх піднесених: сигнал у часовій області поводиться як одна несуча.", 10.5, MUTED, "start"))
    f.append(text(80, py + 124, "• Пік-фактор (PAPR) падає на 2–3 дБ, ККД підсилювача зростає, радіус дії телефону збільшується без перегріву передавача.", 10.5, FIELD, "start", bold=True))

    render(os.path.join(IMG, "sc-fdma-vs-ofdma-papr.svg"), W, H, *f,
           title="Порівняння ланцюгів формування сигналу OFDMA та SC-FDMA: механізм зменшення пік-фактора PAPR через DFT-прекодування")


# ── 6. Циклічний префікс (CP) у багатокористувацькому просторі ────────────────
def fig_multiuser_cyclic_prefix():
    W, H = 940, 480
    f = []

    f.append(text(W / 2, 28, "Циклічний префікс (CP) у багатокористувацькому висхідному каналі", 14.5, INK, "middle", bold=True))

    ox, oy = 80, 70
    t_scale = 1.6
    # Розміри: CP = 60 px, Symbol T_s = 320 px
    cp_w = 70
    ts_w = 340
    sh = 40

    # 1. Сигнал близького користувача UE 1 (мінімальна затримка)
    y1 = oy + 30
    f.append(text(ox - 10, y1 + sh / 2 + 4, "Близький абонент (UE 1):", 11.5, NEG, "end", bold=True))
    # CP
    f.append(rect(ox + 20, y1, cp_w, sh, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=3))
    f.append(text(ox + 20 + cp_w / 2, y1 + sh / 2 + 4, "CP", 10.5, "#d35400", "middle", bold=True))
    # Символ Ts
    f.append(rect(ox + 20 + cp_w, y1, ts_w, sh, fill="#edf3fc", stroke=NEG, sw=1.6, rx=3))
    f.append(text(ox + 20 + cp_w + ts_w / 2, y1 + sh / 2 + 4, "Корисний символ T_s (UE 1)", 11, NEG, "middle", bold=True))

    # 2. Сигнал далекого користувача UE 2 (зсув затримки розповсюдження Δt)
    delta_t = 40
    y2 = y1 + sh + 35
    f.append(text(ox - 10, y2 + sh / 2 + 4, "Далекий абонент (UE 2):", 11.5, "#d35400", "end", bold=True))
    # CP далекого
    f.append(rect(ox + 20 + delta_t, y2, cp_w, sh, fill="#fef9e7", stroke="#f39c12", sw=1.5, rx=3))
    f.append(text(ox + 20 + delta_t + cp_w / 2, y2 + sh / 2 + 4, "CP", 10.5, "#d35400", "middle", bold=True))
    # Символ Ts далекого
    f.append(rect(ox + 20 + delta_t + cp_w, y2, ts_w, sh, fill="#fbeee6", stroke="#d35400", sw=1.6, rx=3))
    f.append(text(ox + 20 + delta_t + cp_w + ts_w / 2, y2 + sh / 2 + 4, "Корисний символ T_s (UE 2)", 11, "#d35400", "middle", bold=True))

    # Дужка затримки Δt
    f.append(line(ox + 20, y2 - 10, ox + 20 + delta_t, y2 - 10, color=POS, sw=1.6))
    f.append(line(ox + 20, y2 - 14, ox + 20, y2 - 6, color=POS, sw=1.4))
    f.append(line(ox + 20 + delta_t, y2 - 14, ox + 20 + delta_t, y2 - 6, color=POS, sw=1.4))
    f.append(text(ox + 20 + delta_t / 2, y2 - 16, "Δt (розкид ходу хвиль)", 10, POS, "middle", bold=True))

    # 3. Вікно FFT-інтегрування базової станції
    y3 = y2 + sh + 45
    fft_start = ox + 20 + delta_t
    f.append(text(ox - 10, y3 + sh / 2 + 4, "Вікно FFT базової станції:", 11.5, FIELD, "end", bold=True))
    f.append(rect(fft_start, y3, ts_w, sh, fill="#eaf6ee", stroke=FIELD, sw=2.2, rx=4))
    f.append(text(fft_start + ts_w / 2, y3 + sh / 2 + 4, "Інтервал демодуляції FFT (тривалість T_s = 1/Δf)", 11.5, FIELD, "middle", bold=True))

    # Пунктирні лінії меж вікна FFT вгору крізь обидва сигнали
    f.append(line(fft_start, y1 - 10, fft_start, y3 + sh + 10, color=FIELD, sw=1.5, dash="4 3"))
    f.append(line(fft_start + ts_w, y1 - 10, fft_start + ts_w, y3 + sh + 10, color=FIELD, sw=1.5, dash="4 3"))

    # Пояснювальний висновок
    py = y3 + sh + 30
    f.append(rect(60, py, 820, 110, fill="#f4f8fb", stroke="#bcd4ec", sw=1.5, rx=6))
    f.append(text(470, py + 24, "Умова збереження ортогональності в OFDMA:  Δt_prop + τ_max < T_cp", 12, NEG, "middle", bold=True))
    f.append(text(80, py + 52, "• Вікно інтегрування FFT потрапляє на корисні відліки обох сигналів без захоплення сусідніх символів (немає ISI).", 10.5, MUTED, "start"))
    f.append(text(80, py + 72, "• Циклічний префікс поглинає як різницю відстаней до абонентів (Δt), так і багатопроменеву луну каналу (τ_max).", 10.5, MUTED, "start"))
    f.append(text(80, py + 92, "• Якщо затримка перевищить T_cp, виникає руйнування ортогональності та міжканальна інтерференція (ICI) між блоками RU.", 10.5, POS, "start"))

    render(os.path.join(IMG, "multiuser-cyclic-prefix.svg"), W, H, *f,
           title="Циклічний префікс (CP) у багатокористувацькому просторі: поглинання просторового розкиду затримок")


if __name__ == "__main__":
    fig_ofdm_vs_ofdma_allocation()
    fig_time_frequency_grid()
    fig_multiuser_diversity()
    fig_ul_ofdma_sync()
    fig_sc_fdma_vs_ofdma()
    fig_multiuser_cyclic_prefix()
    print("Усі фігури для OFDMA успішно згенеровано.")
