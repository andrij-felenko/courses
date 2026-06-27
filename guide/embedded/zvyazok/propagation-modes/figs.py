# -*- coding: utf-8 -*-
"""Фігури до кроку курсу «Режими поширення радіохвиль».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

SKY = "#2457d6"    # небесна хвиля / іоносфера — холодне
GND = "#b9770e"    # поверхнева хвиля — тепле, земляне
LOS = "#27ae60"    # пряма видимість — зелене (наш робочий режим)


# ── 1. Чотири дороги однієї хвилі ────────────────────────────────────────────
def fig_modes():
    W, H = 940, 500
    f = [text(W / 2, 30, "Чотири дороги, якими хвиля доходить від A до B", size=18, bold=True),
         text(W / 2, 52, "режим обирає не радіо, а частота: та сама антена на різних частотах «ходить» по-різному",
              size=11.5, color=MUTED, italic=True)]

    # земля — дуга (виразна кривина), плюс пагорб посередині
    ground_y = 400
    r_e = 1600
    f.append('<path d="M 40,%.1f A %d,%d 0 0 1 900,%.1f L 900,476 L 40,476 Z" '
             'fill="#f1efe9" stroke="%s" stroke-width="2.4"/>'
             % (ground_y, r_e, r_e, ground_y, INK))
    f.append(text(W / 2, 468, "поверхня Землі з кривиною — горб посередині затуляє пряму лінію", size=9.5, color=MUTED))

    # іоносфера — пунктирна стеля
    iono_y = 92
    f.append(line(60, iono_y, 880, iono_y, color=SKY, sw=2, dash="8,7"))
    f.append(text(W / 2, iono_y - 8, "іоносфера — заряджений шар високо вгорі", size=10.5, color=SKY, bold=True))

    # вершина пагорба (де земля найвища)
    crest_x, crest_y = W / 2, ground_y - 30

    ax, ay = 150, ground_y - 26     # A — на схилі ліворуч
    bx, by = 790, ground_y - 26     # B — на схилі праворуч
    f.append(line(ax, ay, ax, ay - 44, color=INK, sw=2.6))
    f.append(text(ax, ay + 26, "A", size=14, color=INK, bold=True))
    f.append(line(bx, by, bx, by - 44, color=INK, sw=2.6))
    f.append(text(bx, by + 26, "B", size=14, color=INK, bold=True))

    topA = (ax, ay - 44)
    topB = (bx, by - 44)
    midx = (topA[0] + topB[0]) / 2

    # 1) небесна хвиля — вгору до іоносфери і вниз
    f.append('<path d="M %d,%d Q %d,%d %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (topA[0], topA[1], (topA[0] + midx) / 2 - 40, iono_y + 16, midx, iono_y + 6,
                (midx + topB[0]) / 2 + 40, iono_y + 16, topB[0], topB[1], SKY))
    f.append(text(midx, iono_y + 38, "небесна хвиля — відбивається від іоносфери (тисячі км)", size=10.5, color=SKY, bold=True))

    # 2) тропосферне розсіяння — вузький конус у тропосферу, дрібка вниз
    sct_x, sct_y = midx, 168
    f.append(line(topA[0], topA[1], sct_x, sct_y, color=MUTED, sw=1.6))
    f.append('<circle cx="%d" cy="%d" r="8" fill="#e8e8ec" stroke="%s" stroke-width="1.5"/>' % (sct_x, sct_y, MUTED))
    f.append(line(sct_x, sct_y, topB[0], topB[1], color=MUTED, sw=1.4, dash="4,4"))
    f.append(text(midx, sct_y - 12, "тропосферне розсіяння — дрібка від завихрень повітря", size=9.5, color=MUTED))

    # 3) пряма видимість — рівна лінія, що впирається в горб
    f.append(line(topA[0], topA[1], topB[0], topB[1], color=LOS, sw=2.6))
    # хрестик у точці, де лінія перетинає горб
    f.append(text(crest_x + 12, crest_y - 14, "✕", size=15, color=POS, bold=True))
    f.append(text(midx, ground_y - 56, "пряма видимість — найкоротша, та горб її ріже", size=10, color=LOS, bold=True))

    # 4) поверхнева хвиля — тулиться до землі, огинає горб
    f.append('<path d="M %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ax + 4, ay - 8, midx, ground_y - 18, bx - 4, by - 8, GND))
    f.append(text(midx, ground_y - 2, "поверхнева хвиля — тулиться до землі, огинає горб", size=10, color=GND, bold=True))

    return render(os.path.join(IMG, 'modes.svg'), W, H, *f)


# ── 2. Частота вибирає режим ─────────────────────────────────────────────────
def fig_freq_picks():
    W, H = 940, 360
    f = [text(W / 2, 30, "Частота сама вибирає режим поширення", size=18, bold=True),
         text(W / 2, 52, "низько — хвиля огинає й відбивається; високо — летить тільки прямо, як промінь світла",
              size=11.5, color=MUTED, italic=True)]

    # вісь частоти
    x0, x1, axy = 80, 860, 300
    f.append(line(x0, axy, x1, axy, color=INK, sw=2.2))
    f.append('<polygon points="%d,%d %d,%d %d,%d" fill="%s"/>' % (x1, axy, x1 - 12, axy - 6, x1 - 12, axy + 6, INK))
    f.append(text(x1 - 4, axy + 26, "частота →", size=11, color=INK, bold=True))

    ticks = [(x0 + 30, "100 кГц"), (x0 + 210, "1 МГц"), (x0 + 390, "30 МГц"),
             (x0 + 560, "300 МГц"), (x0 + 740, "2.4 ГГц")]
    for tx, lbl in ticks:
        f.append(line(tx, axy - 6, tx, axy + 6, color=INK, sw=1.8))
        f.append(text(tx, axy + 22, lbl, size=10, color=MUTED))

    # три смуги-режими над віссю
    def band(x, w, color, title, sub):
        f.append(rect(x, 96, w, 150, fill="#fcfcfc", stroke=color, sw=2, rx=10))
        f.append(text(x + w / 2, 122, title, size=13, color=color, bold=True))
        for i, ln in enumerate(sub):
            f.append(text(x + w / 2, 146 + i * 18, ln, size=10, color=INK))

    band(x0 + 4, 250, GND, "Поверхнева хвиля",
         ["тулиться до землі,", "огинає обрій", "сотні км · AM, LF/MF"])
    band(x0 + 262, 175, SKY, "Небесна хвиля",
         ["стрибки від", "іоносфери", "тисячі км · KX/HF"])
    band(x0 + 442, 330, LOS, "Пряма видимість",
         ["летить прямо, як промінь;", "за обрій не заходить", "VHF/UHF · Wi-Fi, дрони, GPS"])

    return render(os.path.join(IMG, 'freq-picks.svg'), W, H, *f)


# ── 3. Зона Френеля: «тунель», а не лінія ────────────────────────────────────
def fig_fresnel():
    W, H = 940, 360
    f = [text(W / 2, 30, "Лінія є — а зв'язку нема: зона Френеля", size=18, bold=True),
         text(W / 2, 52, "хвилі потрібна не сама пряма лінія, а вільний еліпсоїд-«тунель» довкола неї",
              size=11.5, color=MUTED, italic=True)]

    ax, ay = 110, 210
    bx, by = 830, 210
    # антени
    f.append(line(ax, ay, ax, ay - 36, color=INK, sw=2.6))
    f.append(circle(ax, ay - 36, 3, fill=INK, stroke=INK, sw=0))
    f.append(text(ax, ay + 22, "A", size=13, color=INK, bold=True))
    f.append(line(bx, by, bx, by - 36, color=INK, sw=2.6))
    f.append(circle(bx, by - 36, 3, fill=INK, stroke=INK, sw=0))
    f.append(text(bx, by + 22, "B", size=13, color=INK, bold=True))

    topA = (ax, ay - 36)
    topB = (bx, by - 36)
    cx = (topA[0] + topB[0]) / 2
    cy = (topA[1] + topB[1]) / 2
    rx = (topB[0] - topA[0]) / 2
    ry = 78

    # еліпс зони Френеля
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="#eef6ef" stroke="%s" stroke-width="2" />'
             % (cx, cy, rx, ry, LOS))
    # пряма лінія всередині
    f.append(line(topA[0], topA[1], topB[0], topB[1], color=INK, sw=2, dash="6,5"))
    f.append(text(cx, cy - ry - 8, "перша зона Френеля — її треба тримати вільною (≥60 %)", size=10.5, color=LOS, bold=True))
    f.append(text(cx, cy + 4, "пряма лінія видимості", size=9.5, color=MUTED))

    # перешкода, що НЕ перетинає лінію, але лізе в зону
    obx = cx + 40
    f.append(rect(obx - 26, cy + 18, 52, 120, fill="#d9d9de", stroke=MUTED, sw=1.6, rx=2))
    f.append(text(obx, cy + 150, "дах / дерево", size=9.5, color=INK))
    f.append(text(obx + 96, cy + 30, "лінію не чіпає,", size=10, color=POS))
    f.append(text(obx + 96, cy + 46, "але ріже зону —", size=10, color=POS))
    f.append(text(obx + 96, cy + 62, "сигнал просідає", size=10, color=POS, bold=True))

    return render(os.path.join(IMG, 'fresnel.svg'), W, H, *f)


# ── 4. Радіообрій: чому вище — далі ──────────────────────────────────────────
def fig_horizon():
    W, H = 940, 380
    f = [text(W / 2, 30, "Радіообрій: чому що вище антена, то далі видно", size=18, bold=True),
         text(W / 2, 52, "пряма хвиля впирається в кривину Землі; підняв антену — відсунув обрій",
              size=11.5, color=MUTED, italic=True)]

    # земля — велике коло, видно шматок дуги
    ground_y = 300
    r_e = 1700
    f.append('<path d="M 40,%.1f A %d,%d 0 0 1 900,%.1f L 900,370 L 40,370 Z" '
             'fill="#f1efe9" stroke="%s" stroke-width="2.4"/>'
             % (ground_y, r_e, r_e, ground_y, INK))
    f.append(text(W / 2, 360, "опукла поверхня Землі", size=9.5, color=MUTED))

    # низька антена
    lx = 250
    f.append(line(lx, ground_y - 4, lx, ground_y - 44, color=GND, sw=3))
    f.append(text(lx, ground_y + 22, "низька антена", size=10.5, color=GND, bold=True))
    f.append('<path d="M %d,%d L %d,%d" stroke="%s" stroke-width="2" stroke-dasharray="5,4"/>'
             % (lx, ground_y - 44, lx + 150, ground_y - 4, GND))
    f.append(circle(lx + 150, ground_y - 4, 4, fill=GND, stroke=GND, sw=0))
    f.append(text(lx + 95, ground_y - 52, "обрій близько", size=9.5, color=GND))

    # висока антена
    hx = 250
    f.append(line(hx + 6, ground_y - 4, hx + 6, ground_y - 150, color=SKY, sw=3))
    f.append(text(hx + 6, ground_y - 165, "висока антена", size=10.5, color=SKY, bold=True))
    f.append('<path d="M %d,%d L %d,%d" stroke="%s" stroke-width="2" stroke-dasharray="5,4"/>'
             % (hx + 6, ground_y - 150, hx + 360, ground_y - 6, SKY))
    f.append(circle(hx + 360, ground_y - 6, 4, fill=SKY, stroke=SKY, sw=0))
    f.append(text(hx + 250, ground_y - 100, "обрій далеко", size=10, color=SKY, bold=True))

    # формула-підказка збоку
    box, bw, bh = textbox(760, 150, "d ≈ 3.57·√h\nh у метрах → d у км", size=11,
                          fill="#f3f7ff", stroke=SKY, color=INK, bold=False)
    f.append(box)

    return render(os.path.join(IMG, 'horizon.svg'), W, H, *f)


# ── 5. Загадка 1901: стрибок, якого не мало бути (вставка-історія) ────────────
def fig_leap_1901():
    W, H = 940, 470
    f = [text(W / 2, 30, "Загадка 1901 року: сигнал, якого не мало долетіти", size=18, bold=True),
         text(W / 2, 52, "за прямою видимістю горб океану ховає Ньюфаундленд від Корнуолу — а «S» нібито прийшло",
              size=11.5, color=MUTED, italic=True)]

    # земля — виразна дуга океану між двома берегами
    ground_y = 392
    r_e = 1150
    f.append('<path d="M 40,%.1f A %d,%d 0 0 1 900,%.1f L 900,446 L 40,446 Z" '
             'fill="#eaf1f6" stroke="%s" stroke-width="2.4"/>'
             % (ground_y, r_e, r_e, ground_y, INK))
    f.append(text(W / 2, 438, "опуклість Землі — ~3400 км океану між Поудю і Сент-Джонсом", size=9.5, color=MUTED))

    # вершина опуклості (горб океану)
    crest_x = W / 2
    crest_y = ground_y - 86

    # дві станції на берегах (на дузі)
    ax, ay = 150, ground_y - 26
    bx, by = 790, ground_y - 26
    f.append(line(ax, ay, ax, ay - 40, color=GND, sw=3))
    f.append(text(ax, ay + 22, "Поудю (Корнуол)", size=10.5, color=GND, bold=True))
    f.append(text(ax, ay + 38, "передавач ~13 кВт", size=9, color=MUTED))
    f.append(line(bx, by, bx, by - 40, color=SKY, sw=3))
    f.append(text(bx, by + 22, "Сент-Джонс", size=10.5, color=SKY, bold=True))
    f.append(text(bx, by + 38, "Марконі слухає «S»", size=9, color=MUTED))

    topA = (ax, ay - 40)
    topB = (bx, by - 40)

    # пряма видимість — впирається в горб океану (✕)
    f.append(line(topA[0], topA[1], crest_x - 70, crest_y + 14, color=POS, sw=2, dash="6,5"))
    f.append(line(topB[0], topB[1], crest_x + 70, crest_y + 14, color=POS, sw=2, dash="6,5"))
    f.append(text(crest_x, crest_y + 4, "✕", size=20, color=POS, bold=True))
    f.append(text(crest_x, crest_y - 14, "пряма дорога впирається в горб океану", size=10, color=POS, bold=True))

    # «невидиме дзеркало» — пунктир угорі (питання, а не факт)
    sky_y = 96
    f.append(line(120, sky_y, 820, sky_y, color=SKY, sw=1.8, dash="3,7"))
    f.append(text(W / 2, sky_y - 8, "якесь дзеркало вгорі? — 1901-го його ще ніхто не припускав", size=10.5, color=SKY, italic=True))

    # гіпотетичний небесний стрибок (тонкий, як здогад)
    midx = (topA[0] + topB[0]) / 2
    f.append('<path d="M %d,%d Q %d,%d %d,%d Q %d,%d %d,%d" fill="none" stroke="%s" '
             'stroke-width="2" stroke-dasharray="7,5"/>'
             % (topA[0], topA[1], (topA[0] + midx) / 2, sky_y + 18, midx, sky_y + 8,
                (midx + topB[0]) / 2, sky_y + 18, topB[0], topB[1], SKY))

    return render(os.path.join(IMG, 'leap-1901.svg'), W, H, *f)


# ── 6. 1924: як Епплтон і Барнетт зміряли висоту дзеркала ────────────────────
def fig_appleton():
    W, H = 940, 470
    f = [text(W / 2, 30, "1924: дві дороги однієї передачі видають висоту дзеркала", size=18, bold=True),
         text(W / 2, 52, "пряма хвиля вздовж землі + хвиля, що стрибнула від іоносфери — їхня різниця ходу й дає висоту",
              size=11.5, color=MUTED, italic=True)]

    ground_y = 392
    f.append(rect(40, ground_y, 860, 54, fill="#eef3ec", stroke=INK, sw=2, rx=0))
    f.append(text(W / 2, ground_y + 34, "поверхня Землі  ·  Борнмут → Оксфорд, ~120 км", size=9.5, color=MUTED))

    # іоносфера — стеля-дзеркало
    iono_y = 110
    f.append(line(120, iono_y, 820, iono_y, color=SKY, sw=2.4, dash="9,7"))
    f.append(text(W / 2, iono_y - 10, "відбивний шар (~100 км угору)", size=11, color=SKY, bold=True))

    tx, txy = 170, ground_y - 4
    rxx, rxy = 770, ground_y - 4
    f.append(line(tx, txy, tx, txy - 42, color=GND, sw=3))
    f.append(text(tx, ground_y + 22, "передавач Бі-Бі-Сі", size=10.5, color=GND, bold=True))
    f.append(text(tx, ground_y + 38, "Борнмут, ~770 кГц", size=9, color=MUTED))
    f.append(line(rxx, rxy, rxx, rxy - 42, color=LOS, sw=3))
    f.append(text(rxx, ground_y + 22, "приймач", size=10.5, color=LOS, bold=True))
    f.append(text(rxx, ground_y + 38, "Оксфорд", size=9, color=MUTED))

    T = (tx, txy - 42)
    R = (rxx, rxy - 42)
    midx = (T[0] + R[0]) / 2

    # пряма (поверхнева) — коротка дорога вздовж землі
    f.append(line(T[0], T[1], R[0], R[1], color=GND, sw=2.6))
    f.append(text(midx, T[1] - 8, "пряма дорога — вздовж землі (коротша)", size=10, color=GND, bold=True))

    # небесна — нагору до дзеркала і вниз (довша дорога)
    f.append('<path d="M %d,%d L %d,%d L %d,%d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (T[0], T[1], midx, iono_y + 6, R[0], R[1], SKY))
    f.append(text(midx, iono_y + 30, "небесна дорога — стрибок угору й вниз (довша на Δ)", size=10, color=SKY, bold=True))

    # підсвітити різницю ходу Δ біля приймача
    f.append(circle(R[0], R[1], 7, fill="#fff", stroke=POS, sw=2))
    f.append(text(R[0] + 4, R[1] - 16, "тут дві хвилі складаються", size=9.5, color=POS))
    f.append(text(R[0] + 4, R[1] - 2, "то в лад, то в протифазу", size=9.5, color=POS, bold=True))

    # пояснення-рамка: міняємо частоту → лічимо завмирання → висота
    box, bw, bh = textbox(180, 200,
                          "повільно міняємо частоту →\nрізниця ходу Δ «протягує»\nфазу → сигнал то гасне,\nто оживає → з ритму\nзавмирань рахуємо Δ → висоту",
                          size=10.5, fill="#f3f7ff", stroke=SKY, color=INK)
    f.append(box)

    return render(os.path.join(IMG, 'appleton-1924.svg'), W, H, *f)


if __name__ == '__main__':
    fig_modes()
    fig_freq_picks()
    fig_fresnel()
    fig_horizon()
    fig_leap_1901()
    fig_appleton()
    print('OK: modes.svg, freq-picks.svg, fresnel.svg, horizon.svg, leap-1901.svg, appleton-1924.svg')
