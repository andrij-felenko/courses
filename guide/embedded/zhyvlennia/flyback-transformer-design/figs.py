# -*- coding: utf-8 -*-
"""Фігури до кроку «Проектування трансформатора flyback».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: карта проєктування — ТЗ на вході, чотири числа трансформатора ──
def fig_design_map():
    W, H = 760, 330
    inb, w1, h1 = textbox(150, 165,
                          ["ТЗ вузла:", "Vвх, Vвих, Iвих", "потужність P", "частота f"],
                          size=14, pad=12, fill="#eef2f7", stroke=NEG, sw=2)
    # коробка-«серце» між входом і виходом
    core = rect(330, 120, 100, 90, fill="#fff6e6", stroke=POS, sw=2.2, rx=8)
    corelbl = mtext(380, 158, ["трансфор-", "матор"], size=13, bold=True)
    outs = [
        ("індуктивність Lпр", 70),
        ("відношення Np/Ns", 120),
        ("витки Np + зазор", 170),
        ("провід (RMS-струм)", 220),
    ]
    g = inb + core + corelbl
    for s, yy in outs:
        g += line(430, 165, 560, yy + 12, color=MUTED, sw=1.4)
        g += fitbox(560, yy, 175, 30, s, size=12, fill=FILL, stroke=FIELD, sw=1.6)
    g += arrow(258, 165, 326, 165, color=INK, sw=2)
    g += text(W/2, 300, "Спроєктувати flyback = порахувати ці чотири числа його трансформатора",
              size=13, color=MUTED)
    render(os.path.join(OUT, 'design-map.svg'), W, H, g,
           title="Від ТЗ — до серця перетворювача")


# ── Фігура 2: DCM — трикутник струму, пакет енергії ½·L·Iпік² щоцикл ─────────
def fig_dcm_energy():
    W, H = 720, 350
    x0, y0 = 80, 285
    xr, yt = 660, 70
    ip = y0 - 175                       # рівень піку струму
    # три цикли: наростання (ВКЛ) → спад (ВИКЛ) → пауза (DCM), повтор
    period = (xr - x0 - 20) / 3.0
    g = (rect(x0, yt, xr - x0, y0 - yt, fill="#fbfcfd", stroke="#dfe3e8", sw=1.2, rx=8)
         + line(x0, y0, xr, y0, color=INK, sw=2)
         + line(x0, y0, x0, yt, color=INK, sw=2))
    for k in range(3):
        bx = x0 + 10 + k * period
        ton = period * 0.40
        toff = period * 0.32
        # наростання первинного струму (ВКЛ) — запасаємо
        g += line(bx, y0, bx + ton, ip, color=POS, sw=2.6)
        # спад (ВИКЛ) — віддаємо у вторинну
        g += line(bx + ton, ip, bx + ton + toff, y0, color=NEG, sw=2.4, dash="5 4")
        # пауза до нуля (ознака DCM)
        g += line(bx + ton + toff, y0, bx + period, y0, color=MUTED, sw=2)
        if k == 0:
            g += text(bx + ton/2, ip - 12, "ВКЛ", size=12, color=POS, bold=True)
            g += text(bx + ton + toff/2 + 6, y0 - 60, "ВИКЛ", size=12, color=NEG, bold=True)
            g += text(bx + period - period*0.12, y0 - 14, "пауза", size=11, color=MUTED)
    g += text(x0 - 8, ip + 4, "Iпік", size=12, color=POS, anchor="end", bold=True)
    g += line(x0, ip, x0 + 10, ip, color=POS, sw=2)
    g += text(xr - 6, y0 + 20, "час", size=12, color=MUTED, anchor="end")
    g += text(x0 - 8, yt + 30, "струм", size=12, color=INK, anchor="end")
    # підпис-формула пакета енергії
    box = fitbox(380, 92, 270, 46,
                 "пакет ½·L·Iпік² × f = потужність",
                 size=13, fill="#fff6e6", stroke=POS, sw=1.6, bold=True)
    g += box
    render(os.path.join(OUT, 'dcm-energy.svg'), W, H, g,
           title="DCM: щоцикл осердя набирає й повністю віддає пакет енергії")


# ── Фігура 3: навіщо зазор — B-H зрізаний зазором, той самий струм під Bsat ──
def fig_gap():
    W, H = 720, 360
    x0, y0 = 90, 300                     # початок осей (H=0, B=0)
    xr, yt = 660, 70
    bsat = yt + 40                       # рівень насичення
    g = (rect(x0, yt, xr - x0, y0 - yt, fill="#fbfcfd", stroke="#dfe3e8", sw=1.2, rx=8)
         + line(x0, y0, xr, y0, color=INK, sw=2)            # вісь H (струм·витки)
         + line(x0, y0, x0, yt, color=INK, sw=2)            # вісь B
         + line(x0, bsat, xr, bsat, color=POS, sw=1.6, dash="6 5"))
    g += text(xr - 6, bsat - 8, "Bнас — межа насичення", size=12, color=POS, anchor="end")
    g += text(x0 - 8, yt + 26, "B", size=13, color=INK, anchor="end", bold=True)
    g += text(xr - 6, y0 + 20, "струм · витки  (H)", size=12, color=MUTED, anchor="end")
    # «без зазору»: крута пряма, що швидко впирається в Bsat за малого струму
    xn = x0 + (xr - x0) * 0.30
    g += line(x0, y0, xn, bsat, color=NEG, sw=2.6)
    g += line(xn, bsat, xn, y0, color=NEG, sw=1.2, dash="3 4")
    g += text(xn, y0 + 20, "Iмало", size=11, color=NEG, anchor="middle")
    g += fitbox(x0 + 20, yt + 8, 150, 26, "без зазору: круто", size=11,
                fill="#eaf0fd", stroke=NEG, sw=1.4)
    # «із зазором»: пологіша пряма — той самий Bsat аж при великому струмі
    xg = x0 + (xr - x0) * 0.86
    g += line(x0, y0, xg, bsat, color=FIELD, sw=2.8)
    g += line(xg, bsat, xg, y0, color=FIELD, sw=1.2, dash="3 4")
    g += text(xg, y0 + 20, "Iпік", size=11, color=FIELD, anchor="middle", bold=True)
    g += fitbox(xg - 215, bsat + 14, 200, 26, "із зазором: полого", size=11,
                fill="#e9f7ef", stroke=FIELD, sw=1.4)
    render(os.path.join(OUT, 'gap-shears-bh.svg'), W, H, g,
           title="Навіщо зазор: він «нахиляє» лінію — той самий Iпік влізає під Bнас")


# ── Фігура 4: де гріє струм — трикутні імпульси й їхнє RMS ───────────────────
def fig_rms():
    W, H = 720, 320
    g = ""
    # дві панелі: первинна (ВКЛ) і вторинна (ВИКЛ)
    panels = [("Первинна обмотка", 60, POS, "Iпік", 0.42),
              ("Вторинна обмотка", 390, NEG, "Iпік·Np/Ns", 0.34)]
    for title_s, px, col, peaklbl, frac in panels:
        bx, by = px + 20, 250
        bw, bh = 250, 150
        g += rect(bx, by - bh, bw, bh, fill="#fbfcfd", stroke="#dfe3e8", sw=1.2, rx=8)
        g += line(bx, by, bx + bw, by, color=INK, sw=1.8)
        g += line(bx, by, bx, by - bh, color=INK, sw=1.8)
        top = by - bh + 30
        tw = bw * frac
        # трикутний імпульс провідності + пауза
        g += line(bx, by, bx + tw, top, color=col, sw=2.6)
        g += line(bx + tw, top, bx + tw, by, color=col, sw=2.6)
        g += line(bx + tw, by, bx + bw - 6, by, color=MUTED, sw=2, dash="4 4")
        g += text(bx + tw/2, top - 8, peaklbl, size=11, color=col, bold=True, anchor="middle")
        g += text(bx + bw/2, by - bh - 10, title_s, size=13, bold=True)
        g += text(bx + bw - 6, by + 18, "час", size=11, color=MUTED, anchor="end")
    g += text(W/2, 300,
              "Гріє провід не пік, а діюче (RMS) трикутних імпульсів — за ним і добирають переріз",
              size=12.5, color=MUTED)
    render(os.path.join(OUT, 'rms-heating.svg'), W, H, g,
           title="Де струм гріє: трикутні імпульси у двох обмотках")


# ════════════════════════════════════════════════════════════════════════════
# Фігури до вставки «Математика осердя: добуток площ і зазор»
# ════════════════════════════════════════════════════════════════════════════

# ── Вставка 1: добуток площ Ap = Wa·Ae — два множники, дві задачі ────────────
def fig_ap_box():
    W, H = 740, 360
    # Розріз осердя: вікно (Wa) ліворуч, переріз заліза (Ae) праворуч
    cx, cy = 215, 200
    # П-подібне осердя в розрізі — два стовпи й перемичка, всередині — вікно
    g = ""
    # зовнішній контур заліза
    g += rect(cx - 95, cy - 105, 190, 210, fill="#e8e2d8", stroke=INK, sw=2, rx=4)
    # внутрішнє вікно (повітря під обмотки)
    win = rect(cx - 55, cy - 70, 70, 140, fill="#eef2f7", stroke=NEG, sw=2, rx=3)
    g += win
    g += text(cx - 20, cy, "Wa", size=15, color=NEG, bold=True)
    g += text(cx - 20, cy + 20, "вікно", size=10, color=NEG)
    # переріз заліза (правий стовп) — заштрихуємо як «потік тут»
    g += rect(cx + 35, cy - 70, 50, 140, fill="#fde6e6", stroke=POS, sw=2, rx=3)
    g += text(cx + 60, cy - 2, "Ae", size=14, color=POS, bold=True)
    g += text(cx + 60, cy + 18, "потік", size=10, color=POS)
    g += text(cx, cy - 125, "розріз осердя", size=12, color=MUTED, bold=True)

    # Права частина: формула-добуток і дві задачі
    g += text(500, 95, "Ap = Wa · Ae", size=22, bold=True)
    b1, w1, h1 = textbox(500, 165,
                         ["Ae (переріз заліза):", "тримає ПОТІК", "→ не насититись"],
                         size=13, pad=12, fill="#fde6e6", stroke=POS, sw=1.8)
    b2, w2, h2 = textbox(500, 270,
                         ["Wa (площа вікна):", "тримає МІДЬ", "→ обмотки влізуть"],
                         size=13, pad=12, fill="#eef2f7", stroke=NEG, sw=1.8)
    g += b1 + b2
    g += line(cx + 95, 165, 500 - w1/2, 165, color=POS, sw=1.4, dash="4 4")
    g += line(cx + 95, 200, 500 - w2/2, 270, color=NEG, sw=1.4, dash="4 4")
    g += text(W/2, 335,
              "Один множник бореться з насиченням, другий — з тіснотою; добуток ловить обидва",
              size=12.5, color=MUTED)
    render(os.path.join(OUT, 'ap-box.svg'), W, H, g,
           title="Добуток площ: дві площі — дві різні задачі в одному числі")


# ── Вставка 2: магнітне коло — реактанс зазору тримає майже всю енергію ──────
def fig_gap_reluctance():
    W, H = 740, 340
    # Магнітне коло як петля: довгий шлях заліза (малий опір) + крихітний зазор (величезний опір)
    g = ""
    # прямокутна петля магнітопроводу
    L, T, R, B = 110, 80, 560, 250
    g += line(L, T, R - 70, T, color=INK, sw=14)          # верх
    g += line(L, T, L, B, color=INK, sw=14)               # ліво
    g += line(L, B, R, B, color=INK, sw=14)               # низ
    g += line(R, T + 22, R, B, color=INK, sw=14)          # право (до зазору)
    # зазор — тонкий розрив угорі праворуч
    g += rect(R - 70, T - 7, 70, 14, fill="#e9f7ef", stroke=FIELD, sw=2.4, rx=2)
    g += line(R - 70, T, R - 70, T, color=FIELD, sw=2)
    g += text(R - 35, T - 16, "зазор lg", size=12, color=FIELD, bold=True, anchor="middle")
    # «магнітний рушій» — котушка зліва (струм·витки)
    for i in range(4):
        yy = T + 40 + i * 38
        g += circle(L, yy, 11, fill="#fff6e6", stroke=POS, sw=2)
    g += text(L - 24, (T + B) / 2, "N·I", size=13, color=POS, bold=True, anchor="end")

    # підписи опорів
    g += fitbox(170, B + 14, 230, 30, "залізо: Rfe ≈ lfe/(µr·µ0·Ae) — мале",
                size=11.5, fill="#f2efe9", stroke=INK, sw=1.4)
    g += fitbox(R - 215, T + 30, 200, 30, "зазор: Rg = lg/(µ0·Ae) — ВЕЛИКЕ",
                size=11.5, fill="#e9f7ef", stroke=FIELD, sw=1.6)

    # права колонка — стовпчики «де живе енергія»
    bx = 600
    g += text(bx + 25, 70, "де енергія", size=12, bold=True, anchor="middle")
    # залізо — крихітний стовпчик
    g += rect(bx, 230, 22, 18, fill="#cfd8e3", stroke=INK, sw=1.4)
    g += text(bx + 11, 264, "Fe", size=11, color=MUTED, anchor="middle")
    # зазор — майже весь
    g += rect(bx + 40, 95, 22, 153, fill=FIELD, stroke=INK, sw=1.4)
    g += text(bx + 51, 264, "зазор", size=11, color=FIELD, anchor="middle", bold=True)
    g += text(bx + 30, 88, "≈ вся", size=10, color=FIELD, anchor="middle")

    g += text(W/2, 322,
              "Зазор додає величезний опір потокові — у ньому й накопичується майже вся енергія пакета",
              size=12.5, color=MUTED)
    render(os.path.join(OUT, 'gap-reluctance.svg'), W, H, g,
           title="Зазор у магнітному колі: малий розмір, величезний опір, уся енергія")


# ── Вставка 3: чи влізе мідь у вікно — заповнення Ku ─────────────────────────
def fig_window_fit():
    W, H = 740, 330
    # Велике вікно (Wa) і всередині — пакет дротів + порожнечі (ізоляція, каркас)
    wx, wy, ww, wh = 90, 70, 230, 200
    g = rect(wx, wy, ww, wh, fill="#eef2f7", stroke=NEG, sw=2.2, rx=4)
    g += text(wx + ww/2, wy - 12, "площа вікна Wa", size=12, color=NEG, bold=True, anchor="middle")
    # первинна — стовпчик мідних кружечків зліва
    import random
    random.seed(7)
    r = 11
    # первинна (теплі) — два ряди
    for row in range(2):
        for col in range(7):
            cxp = wx + 24 + col * 26
            cyp = wy + 30 + row * 26
            g += circle(cxp, cyp, r, fill="#f6c9a0", stroke=POS, sw=1.4)
    g += text(wx + 24 + 3*26, wy + 30 + 26 + 40, "первинна Np", size=11, color=POS, anchor="middle")
    # вторинна (холодні) — два ряди нижче, трохи товщі
    for row in range(2):
        for col in range(6):
            cxs = wx + 28 + col * 30
            cys = wy + 122 + row * 30
            g += circle(cxs, cys, 13, fill="#aacbe8", stroke=NEG, sw=1.4)
    g += text(wx + ww/2, wy + wh + 22, "вторинна Ns", size=11, color=NEG, anchor="middle")
    # «порожнеча» — заштрихована верхня смужка (каркас + ізоляція + зазори)
    g += rect(wx + 6, wy + wh - 26, ww - 12, 20, fill="#f0ede7", stroke=MUTED, sw=1.2, rx=3)
    g += text(wx + ww/2, wy + wh - 11, "каркас, ізоляція, повітря", size=10, color=MUTED, anchor="middle")

    # права частина — формула заповнення
    g += text(530, 95, "Ku ≈ 0.4", size=22, bold=True)
    g += text(530, 122, "(ізольований flyback)", size=11, color=MUTED, anchor="middle")
    b, bw2, bh2 = textbox(530, 200,
                          ["мідь, що влізе =", "Ku · Wa", "", "має вмістити", "Np·Aпр + Ns·Aвт"],
                          size=13, pad=14, fill=FILL, stroke=FIELD, sw=1.8)
    g += b
    g += text(W/2, 308,
              "Лише ~40 % вікна — це мідь; решта на каркас, ізоляцію й повітря між витками",
              size=12.5, color=MUTED)
    render(os.path.join(OUT, 'window-fit.svg'), W, H, g,
           title="Чи влізе мідь: вікно заповнене лише на коефіцієнт Ku")


if __name__ == '__main__':
    fig_design_map()
    fig_dcm_energy()
    fig_gap()
    fig_rms()
    fig_ap_box()
    fig_gap_reluctance()
    fig_window_fit()
    print("OK: figures written to", OUT)
