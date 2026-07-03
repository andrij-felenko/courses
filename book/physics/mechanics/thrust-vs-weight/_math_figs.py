# -*- coding: utf-8 -*-
"""Фігури до вставки «Теорія ідеального диска» (math-actuator-disk.md).
Окремий файл, щоб не чіпати основний figs.py теми.
Запуск:  python _math_figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── Фігура 1: профілі швидкості й тиску вздовж струмної трубки ────────────────
# Крутий момент: швидкість зростає плавно (0 → v_i на диску → 2·v_i далеко вниз),
# а тиск СТРИБАЄ на диску. Половина розгону — над диском (тиск падає нижче
# атмосферного), половина — під диском (тиск падає від піку до атмосферного).
def fig_profiles():
    W, H = 780, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Уздовж трубки: швидкість росте плавно, тиск стрибає на диску",
                  size=15, bold=True))

    xd = W / 2                       # x диска (спільний для обох графіків)
    xL, xR = 90, W - 40

    # ── верхня панель: швидкість ──
    vy0, vy1 = 70, 190               # верх/низ поля швидкості
    vbase = vy1                      # рівень v=0
    f.append(line(xL, vbase, xR, vbase, color=MUTED, sw=1.2))
    f.append(text(xL - 8, vy0 + 6, "швидкість", size=12, color=INK, anchor="end"))
    # крива швидкості: 0 далеко вгорі → v_i на диску → 2·v_i далеко вниз (плавно)
    v_far = 8                        # px відповідник v≈0 (майже нуль)
    v_i   = 46                       # px на диску
    v_dn  = 92                       # px далеко вниз = 2·v_i
    pts = []
    for i in range(0, 121):
        x = xL + (xR - xL) * i / 120.0
        # логістична форма розгону вздовж осі, центр на диску
        t = (x - xd) / 150.0
        s = 1.0 / (1.0 + math.exp(-t * 2.2))      # 0..1
        vpx = v_far + (v_dn - v_far) * s
        pts.append((x, vbase - vpx))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, NEG))
    # відмітки v_i на диску та 2·v_i праворуч
    f.append(line(xd, vbase, xd, vbase - v_i, color=NEG, sw=1, dash="3,4"))
    f.append(text(xd - 8, vbase - v_i - 4, "v_i", size=13, bold=True, color=NEG, anchor="end"))
    f.append(text(xR - 4, vbase - v_dn - 6, "2·v_i", size=13, bold=True, color=NEG, anchor="end"))
    f.append(text(xL + 40, vbase - v_far - 6, "≈0", size=12, color=MUTED))

    # ── нижня панель: тиск ──
    py_atm = 320                     # рівень атмосферного тиску p₀
    f.append(line(xL, py_atm, xR, py_atm, color=MUTED, sw=1.2, dash="4,5"))
    f.append(text(xR - 2, py_atm - 6, "p₀ (атмосферний)", size=11, color=MUTED, anchor="end"))
    f.append(text(xL - 8, py_atm - 66, "тиск", size=12, color=INK, anchor="end"))
    dp = 40                          # напівамплітуда стрибка
    # над диском: тиск росте від p₀ до піку (p₀+... ) при підході — насправді
    # над диском тиск ВИЩЕ атмосферного зверху трубки? Ні: у трубці над диском
    # повітря розганяється, тиск падає нижче p₀, тоді на диску СТРИБАЄ вгору,
    # а під диском знову падає до p₀. Малюємо канонічний профіль:
    #   вгорі: p₀ → плавно падає до (p₀−a) біля диска зверху
    #   стрибок ↑ до (p₀+b) під диском
    #   під диском: (p₀+b) → плавно спадає до p₀ далеко вниз
    up = []
    for i in range(0, 61):
        x = xL + (xd - xL) * i / 60.0
        t = (x - xd) / 130.0
        s = 1.0 / (1.0 + math.exp(-t * 2.4))       # →1 біля диска
        up.append((x, py_atm + dp * 0.7 * s))       # опускається (нижче лінії = вниз на екрані = менший тиск? )
    # на екрані «вниз» = більше y; менший тиск малюємо ВИЩЕ (менший y), тож інвертуємо
    up = [(x, py_atm - (y - py_atm)) for (x, y) in up]  # дзеркалимо, щоб падіння тиску йшло вгору
    # простіше: намалюємо явно двома гладкими сегментами
    up = []
    for i in range(0, 61):
        x = xL + (xd - xL) * i / 60.0
        frac = (x - xL) / (xd - xL)                 # 0..1
        drop = dp * 0.75 * frac                      # падіння тиску до диска
        up.append((x, py_atm + drop))                # більший y = нижче лінії = менший тиск
    dn = []
    for i in range(0, 61):
        x = xd + (xR - xd) * i / 60.0
        frac = (x - xd) / (xR - xd)                  # 0..1
        # під диском тиск від піку (p₀+dp) спадає до p₀
        val = py_atm - dp * (1.0 - frac)             # менший y = вище = більший тиск
        dn.append((x, val))
    du = "M %.1f %.1f " % up[0] + " ".join("L %.1f %.1f" % p for p in up[1:])
    dd = "M %.1f %.1f " % dn[0] + " ".join("L %.1f %.1f" % p for p in dn[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (du, POS))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (dd, POS))
    # стрибок тиску на диску (вертикаль між кінцем up і початком dn)
    y_top = up[-1][1]                # нижня точка (менший тиск) зверху диска
    y_bot = dn[0][1]                 # верхня точка (більший тиск) під диском
    f.append(arrow(xd, y_top, xd, y_bot, color=POS, sw=3))
    f.append(text(xd + 10, (y_top + y_bot) / 2 + 4, "Δp — стрибок тиску", size=12,
                  bold=True, color=POS, anchor="start"))

    # диск: спільна вертикаль через обидві панелі
    f.append(line(xd, vy0 - 4, xd, 360, color=FIELD, sw=4))
    f.append(text(xd, 384, "диск A", size=13, bold=True, color=FIELD))

    # підпис-висновок
    b, bw, bh = textbox(W / 2, H - 30,
                        "розгін порівну: половина (0→v_i) — НАД диском, половина (v_i→2·v_i) — ПІД ним",
                        size=12, pad=8, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "disk-profiles.svg"), W, H, *f)


# ── Фігура 2: драбина навантаження на диск для реальних апаратів ──────────────
# Що більше T/A, то швидший відкид v_i=√(T/A / 2ρ) і дорожче зависання.
def fig_disk_loading_ladder():
    W, H = 780, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Навантаження на диск і швидкість відкиду в зависі",
                  size=15, bold=True))

    rho = 1.225
    # (назва, T/A [Н/м²]) — з паспортних disk loading (kg/m² × 9.81)
    rows = [
        ("маленький дрон (24 см гвинти)", 65),
        ("Robinson R22 (легкий вертоліт)", 14 * 9.81),
        ("Chinook CH-47 (важкий вертоліт)", 43 * 9.81),
        ("V-22 Osprey (тилтротор)", 130 * 9.81),
        ("реактивний підйом (Harrier-подібний)", 3000),
    ]
    x0 = 60
    y0 = 74
    dy = 60
    maxDL = max(dl for _, dl in rows)
    bar_x = 340
    bar_max = W - 70 - bar_x
    for i, (name, dl) in enumerate(rows):
        y = y0 + i * dy
        vi = math.sqrt(dl / (2 * rho))          # м/с
        f.append(text(x0, y + 4, name, size=12, color=INK, anchor="start"))
        # смуга — довжина ∝ √(dl) (щоб малий дрон було видно поряд із джетом)
        w = bar_max * math.sqrt(dl) / math.sqrt(maxDL)
        col = FIELD if dl < 200 else (POS if dl > 1500 else "#e08e0b")
        f.append(rect(bar_x, y - 12, max(w, 4), 22, fill=col, stroke='none', sw=0, rx=4))
        f.append(text(bar_x + max(w, 4) + 8, y + 4,
                      "T/A ≈ %d Н/м²   v_i ≈ %.0f м/с" % (round(dl), vi),
                      size=11, color=INK, anchor="start"))

    # вісь-підпис
    f.append(text(bar_x, y0 - 16, "довжина смуги ∝ √(T/A)  (∝ швидкості відкиду v_i)",
                  size=11, color=MUTED, anchor="start"))
    # підсумкова плашка
    b, bw, bh = textbox(W / 2, H - 34,
                        "v_i = √( (T/A) / (2·ρ) )  →  дешевий завис вимагає МАЛОГО T/A (широкий диск)",
                        size=12, pad=8, fill="#eafaf1", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "disk-loading-ladder.svg"), W, H, *f)


if __name__ == "__main__":
    p1 = fig_profiles()
    p2 = fig_disk_loading_ladder()
    print("written:")
    for p in (p1, p2):
        print("  ", p)
