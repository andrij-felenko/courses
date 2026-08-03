# -*- coding: utf-8 -*-
"""Фігури до детальної статті «NFC/RFID».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"


# ── 1. Поле на осі котушки: чому дальність — це «край» H(z) ───────────────────
def fig_field_falloff():
    W, H = 940, 470
    f = [text(W / 2, 30, "Поле на осі котушки спадає як 1/z³ — звідси і сантиметри дальності", size=17.5, bold=True),
         text(W / 2, 52, "H(z) тримається майже сталим у межах радіуса a, а далі різко валиться — картка живиться лише поблизу",
              size=11.5, color=MUTED, italic=True)]

    # осі графіка
    ox, oy = 120, 400          # початок координат
    gw, gh = 700, 300          # розміри поля графіка
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=2))          # X
    f.append(line(ox, oy, ox, oy - gh, color=INK, sw=2))          # Y
    f.append(text(ox + gw + 6, oy + 4, "z / a", size=12, color=INK, anchor="start"))
    f.append(text(ox - 10, oy - gh - 6, "H(z)/H(0)", size=12, color=INK, anchor="end"))

    # крива H(z)/H(0) = a³/(a²+z²)^{3/2}, у координатах x = z/a
    a = 1.0
    pts = []
    for i in range(0, 361):
        zr = i / 60.0                      # z/a від 0 до 6
        val = a ** 3 / (a * a + (zr * a) ** 2) ** 1.5
        px = ox + (zr / 6.0) * gw
        py = oy - val * gh
        pts.append((px, py))
    d = "M %.1f,%.1f " % pts[0] + " ".join("L %.1f,%.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, FIELD))

    # позначка z = a (радіус) — злам
    zr = 1.0
    px = ox + (zr / 6.0) * gw
    val = 1.0 / (2 ** 1.5)
    py = oy - val * gh
    f.append(line(px, oy, px, py, color=MUTED, sw=1.4, dash="5,5"))
    f.append(line(ox, py, px, py, color=MUTED, sw=1.4, dash="5,5"))
    f.append(circle(px, py, 4, fill=POS, stroke=POS, sw=0))
    f.append(text(px, oy + 20, "z = a", size=11, color=INK))
    f.append(text(ox - 8, py + 4, "0.35", size=10, color=MUTED, anchor="end"))

    # горизонталь 1.0
    f.append(text(ox - 8, oy - gh + 4, "1.0", size=10, color=MUTED, anchor="end"))

    # асимптота ~ (a/z)³
    f.append(text(ox + gw * 0.62, oy - gh * 0.16, "далеко:  H ∝ (a/z)³", size=11.5, color=POS, italic=True, anchor="start"))
    f.append(text(ox + gw * 0.05, oy - gh * 0.86, "близько:  H ≈ стала", size=11.5, color=FIELD, italic=True, anchor="start"))

    # висновок-рамка
    box, bw, bh = textbox(W / 2, 452, "Робоча зона — z ≲ a: збільшив котушку → відсунув «обрив»", size=11.5, pad=9,
                          fill="#eef6ef", stroke=FIELD)
    f.append(box)

    return render(os.path.join(IMG, 'field-falloff.svg'), W, H, *f)


# ── 2. Дві бічні смуги: піднесена частота породжує пару супутників ────────────
def fig_sidebands():
    W, H = 940, 420
    f = [text(W / 2, 30, "Модуляція навантаження на 847.5 кГц народжує дві бічні смуги", size=17.5, bold=True),
         text(W / 2, 52, "картка перемикає резистор із частотою fₛ = fc/16 — у спектрі зчитувача з'являються супутники fc ± fₛ",
              size=11.5, color=MUTED, italic=True)]

    ox, oy = 90, 350
    gw = 760
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=2))
    f.append(text(ox + gw + 6, oy + 4, "f", size=13, color=INK, anchor="start"))

    # несуча в центрі
    cx = ox + gw * 0.5
    f.append(line(cx, oy, cx, oy - 230, color=INK, sw=3.2))
    f.append(text(cx, oy - 244, "несуча 13.56 МГц", size=11.5, color=INK, bold=True))
    f.append(text(cx, oy + 20, "fc", size=11, color=INK))

    # бічні смуги
    for sign, lab in ((-1, "fc − 847.5 кГц"), (1, "fc + 847.5 кГц")):
        sx = cx + sign * gw * 0.20
        f.append(line(sx, oy, sx, oy - 95, color=FIELD, sw=3.2))
        f.append(text(sx, oy - 106, lab, size=10.5, color=FIELD, bold=True))
        # дужка від несучої до супутника
        my = oy - 150
        f.append('<path d="M %.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
                 % (cx, my, cx + sign * 30, my - 34, sx - sign * 30, my - 34, sx, my, MUTED))
        f.append(text((cx + sx) / 2, my - 40, "847.5 кГц", size=9.5, color=MUTED))

    # підпис-висновок
    f.append(text(cx, oy - 200, "приймач зчитувача фільтрує саме ці супутники — не всю несучу",
                  size=11, color=POS, italic=True))

    box, bw, bh = textbox(W / 2, 400, "Корисний сигнал винесений на 847.5 кГц убік від могутньої несучої — його легко відділити",
                          size=11, pad=9, fill="#fbf7e3", stroke=GOLD)
    f.append(box)

    return render(os.path.join(IMG, 'sidebands.svg'), W, H, *f)


# ── 3. Manchester + OOK: як біт стає пачкою супутника ────────────────────────
def fig_manchester():
    W, H = 940, 430
    f = [text(W / 2, 30, "Один біт картки = півперіоду тиші, півперіоду «дрижання» субнесучої", size=17.0, bold=True),
         text(W / 2, 52, "Manchester кодує біт переходом усередині вікна; OOK вмикає/вимикає субнесучу 847.5 кГц",
              size=11.5, color=MUTED, italic=True)]

    bits = [1, 0, 0, 1]
    ox = 90
    bw = 190                       # ширина одного біта
    top = 120
    lvl_hi = top
    lvl_lo = top + 60

    # рядок 1: логічні біти й межі вікон
    for i, b in enumerate(bits):
        x0 = ox + i * bw
        f.append(line(x0, 96, x0, 360, color="#dddddd", sw=1))
        f.append(text(x0 + bw / 2, 90, "біт %d" % b, size=11, color=INK, bold=True))
    f.append(line(ox + len(bits) * bw, 96, ox + len(bits) * bw, 360, color="#dddddd", sw=1))

    # рядок Manchester (логічний рівень з переходом усередині)
    f.append(text(ox - 12, top + 30, "Manchester", size=10.5, color=NEG, anchor="end", bold=True))
    path = []
    for i, b in enumerate(bits):
        x0 = ox + i * bw
        xm = x0 + bw / 2
        x1 = x0 + bw
        # логіка 1: low→high у середині; логіка 0: high→low (умовність ISO 14443A)
        if b == 1:
            path += [(x0, lvl_lo), (xm, lvl_lo), (xm, lvl_hi), (x1, lvl_hi)]
        else:
            path += [(x0, lvl_hi), (xm, lvl_hi), (xm, lvl_lo), (x1, lvl_lo)]
    d = "M %.1f,%.1f " % path[0] + " ".join("L %.1f,%.1f" % p for p in path[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, NEG))
    for i in range(len(bits)):
        xm = ox + i * bw + bw / 2
        f.append(circle(xm, (lvl_hi + lvl_lo) / 2, 3, fill=POS, stroke=POS, sw=0))
    f.append(text(ox + len(bits) * bw + 12, (lvl_hi + lvl_lo) / 2 + 4,
                  "перехід = біт", size=9.5, color=POS, anchor="start"))

    # рядок субнесучої (OOK): пачки 847.5 кГц там, де рівень «high»
    sc_mid = 300
    amp = 26
    f.append(text(ox - 12, sc_mid + 4, "субнесуча", size=10.5, color=FIELD, anchor="end", bold=True))
    f.append(text(ox - 12, sc_mid + 18, "847.5 кГц", size=9, color=MUTED, anchor="end"))
    # проходимо кожну половинку вікна; де рівень high — малюємо синус, де low — рівна лінія
    seg = []
    for i, b in enumerate(bits):
        x0 = ox + i * bw
        xm = x0 + bw / 2
        halves = [(x0, xm, 1 if b == 1 else 0), (xm, x0 + bw, 0 if b == 1 else 1)]
        for (hx0, hx1, on) in halves:
            if on:
                n = 24
                for k in range(n + 1):
                    xx = hx0 + (hx1 - hx0) * k / n
                    yy = sc_mid - amp * math.sin(2 * math.pi * 6 * (k / n))
                    seg.append((xx, yy))
            else:
                seg.append((hx0, sc_mid))
                seg.append((hx1, sc_mid))
    d2 = "M %.1f,%.1f " % seg[0] + " ".join("L %.1f,%.1f" % p for p in seg[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (d2, FIELD))

    box, bw2, bh2 = textbox(W / 2, 404,
                            "Зчитувач ловить пачки субнесучої, відновлює переходи Manchester → біти. Один біт триває 9.4 мкс (106 кбіт/с)",
                            size=10.8, pad=9, fill="#eef6ef", stroke=FIELD)
    f.append(box)

    return render(os.path.join(IMG, 'manchester.svg'), W, H, *f)


# ── 4. Антиколізія: двійкове дерево по UID ───────────────────────────────────
def fig_anticollision():
    W, H = 940, 470
    f = [text(W / 2, 30, "Антиколізія — двійкове дерево: зчитувач домовляється з кожною карткою по біту UID", size=16.0, bold=True),
         text(W / 2, 52, "на колізії (дві картки шлють протилежні біти) зчитувач фіксує «0», картки з «1» замовкають — і навпаки",
              size=11.5, color=MUTED, italic=True)]

    def node(cx, cy, label, accent=INK, fill="#f4f6f8"):
        r = 22
        return (circle(cx, cy, r, fill=fill, stroke=accent, sw=2) +
                text(cx, cy + 4, label, size=11, color=accent, bold=True))

    # рівні дерева
    y0, y1, y2, y3 = 100, 200, 300, 400
    # корінь
    f.append(node(470, y0, "?"))
    f.append(text(470, y0 - 30, "колізія на біті b3", size=10, color=POS))

    # гілки 0/1
    f.append(line(470, y0 + 22, 300, y1 - 22, color=INK, sw=1.8))
    f.append(line(470, y0 + 22, 640, y1 - 22, color=INK, sw=1.8))
    f.append(text(376, y0 + 62, "0", size=12, color=NEG, bold=True))
    f.append(text(566, y0 + 62, "1", size=12, color=POS, bold=True))

    f.append(node(300, y1, "?"))
    f.append(node(640, y1, "?"))
    f.append(text(300, y1 - 30, "колізія на b1", size=9.5, color=POS))
    f.append(text(640, y1 - 30, "колізія на b0", size=9.5, color=POS))

    # рівень 2
    f.append(line(300, y1 + 22, 210, y2 - 22, color=INK, sw=1.8))
    f.append(line(300, y1 + 22, 390, y2 - 22, color=INK, sw=1.8))
    f.append(line(640, y1 + 22, 560, y2 - 22, color=INK, sw=1.8))
    f.append(line(640, y1 + 22, 720, y2 - 22, color=INK, sw=1.8))
    f.append(text(246, y1 + 62, "0", size=11, color=NEG, bold=True))
    f.append(text(354, y1 + 62, "1", size=11, color=POS, bold=True))
    f.append(text(590, y1 + 62, "0", size=11, color=NEG, bold=True))
    f.append(text(694, y1 + 62, "1", size=11, color=POS, bold=True))

    # листки — конкретні картки (повний UID)
    leaves = [(210, "UID A"), (390, "UID B"), (560, "UID C"), (720, "UID D")]
    for lx, lab in leaves:
        f.append(circle(lx, y2, 22, fill="#eef6ef", stroke=FIELD, sw=2.2))
        f.append(text(lx, y2 + 4, "✓", size=15, color=FIELD, bold=True))
        f.append(text(lx, y2 + 44, lab, size=10, color=INK, bold=True))
        f.append(text(lx, y2 + 60, "SELECT", size=9, color=FIELD))

    # легенда
    f.append(rect(60, y3 + 20, 820, 44, fill="#fbfdfb", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(W / 2, y3 + 40, "Кожен спуск ліворуч/праворуч відсікає половину карток; за log₂N раундів лишається рівно одна — її SELECT-имо, далі HALT і наступна гілка",
                  size=10.5, color=INK))
    f.append(text(W / 2, y3 + 56, "40-бітний UID → щонайбільше 40 раундів на один каскад (для 7- і 10-байтових UID каскадів більше)",
                  size=9.5, color=MUTED))

    return render(os.path.join(IMG, 'anticollision.svg'), W, H, *f)


# ── 5. Коефіцієнт зв'язку k на осі: k і k² (живлення vs відповідь) ────────────
def fig_coupling_falloff():
    W, H = 940, 470
    f = [text(W / 2, 30, "Зв'язок k на осі: плато, тоді кубічний обрив — і подвійна кара k² для відповіді", size=15.5, bold=True),
         text(W / 2, 52, "живлення картки йде за k, а видимість її відповіді — за k² (∝ M²): межа читання ближча за межу живлення",
              size=11.5, color=MUTED, italic=True)]

    ox, oy = 120, 400
    gw, gh = 700, 300
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=2))          # X
    f.append(line(ox, oy, ox, oy - gh, color=INK, sw=2))          # Y
    f.append(text(ox + gw + 6, oy + 4, "z / a", size=12, color=INK, anchor="start"))
    f.append(text(ox - 10, oy - gh - 6, "частка від значення впритул", size=11, color=INK, anchor="end"))

    # крива k(z) ∝ 1/(1+(z/a)²)^{3/2}, нормована на 1 при z=0
    def kf(zr):
        return 1.0 / (1.0 + zr * zr) ** 1.5

    pts_k, pts_k2 = [], []
    for i in range(0, 361):
        zr = i / 60.0                      # z/a від 0 до 6
        vk = kf(zr)
        px = ox + (zr / 6.0) * gw
        pts_k.append((px, oy - vk * gh))
        pts_k2.append((px, oy - vk * vk * gh))
    dk = "M %.1f,%.1f " % pts_k[0] + " ".join("L %.1f,%.1f" % p for p in pts_k[1:])
    dk2 = "M %.1f,%.1f " % pts_k2[0] + " ".join("L %.1f,%.1f" % p for p in pts_k2[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (dk, FIELD))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="7,5"/>' % (dk2, POS))

    # підписи кривих
    f.append(text(ox + gw * 0.30, oy - kf(1.8) * gh - 12, "k  (живлення V_ind)", size=11.5, color=FIELD, italic=True, anchor="start"))
    f.append(text(ox + gw * 0.16, oy - kf(1.0) ** 2 * gh - 10, "k²  (відповідь картки)", size=11.5, color=POS, italic=True, anchor="start"))

    # межа плато z = a
    px = ox + (1.0 / 6.0) * gw
    f.append(line(px, oy, px, oy - gh, color=MUTED, sw=1.4, dash="5,5"))
    f.append(text(px, oy + 20, "z = a", size=11, color=INK))
    f.append(text(px + 6, oy - gh + 14, "край плато", size=10, color=MUTED, anchor="start"))

    # умовний поріг читання/живлення
    thr = 0.12
    f.append(line(ox, oy - thr * gh, ox + gw, oy - thr * gh, color=MUTED, sw=1.2, dash="3,4"))
    f.append(text(ox + gw - 4, oy - thr * gh - 6, "поріг", size=10, color=MUTED, anchor="end"))

    box, bw, bh = textbox(W / 2, 452, "Збільшив котушку → відсунув край плато; але k² не обдуриш — відповідь гасне швидше за живлення",
                          size=11.5, pad=9, fill="#fbf7e3", stroke=GOLD)
    f.append(box)

    return render(os.path.join(IMG, 'coupling-falloff.svg'), W, H, *f)


# ── 6. Розщеплення резонансу зв'язаної пари контурів ──────────────────────────
def fig_coupling_splitting():
    W, H = 940, 470
    f = [text(W / 2, 30, "Сильний зв'язок розщеплює один резонанс на два: f₀/√(1±k)", size=16.5, bold=True),
         text(W / 2, 52, "з ростом k єдиний пік на f₀ роздвоюється; за критичним зв'язком рівно на f₀ утворюється провал",
              size=11.5, color=MUTED, italic=True)]

    ox, oy = 110, 400
    gw, gh = 720, 300
    f.append(line(ox, oy, ox + gw, oy, color=INK, sw=2))          # X (частота)
    f.append(line(ox, oy, ox, oy - gh, color=INK, sw=2))          # Y (відгук)
    f.append(text(ox + gw + 6, oy + 4, "f", size=13, color=INK, anchor="start"))
    f.append(text(ox - 10, oy - gh - 6, "відгук", size=11, color=INK, anchor="end"))

    fc = ox + gw * 0.5           # позиція f₀ на осі
    f.append(line(fc, oy, fc, oy - gh, color=MUTED, sw=1.2, dash="4,5"))
    f.append(text(fc, oy + 20, "f₀ = 13.56 МГц", size=11, color=INK))

    # лоренцівський пік: L(x; x0, w) = 1/(1+((x-x0)/w)²)
    def lor(x, x0, w):
        return 1.0 / (1.0 + ((x - x0) / w) ** 2)

    span = gw * 0.34             # піврозмах осі частот навколо f₀ (умовні одиниці)
    wpk = span * 0.10            # ширина піка

    def draw_curve(kval, color, amp, dash=None, label=None, ly=0):
        pts = []
        N = 300
        for i in range(N + 1):
            x = fc - span + 2 * span * i / N
            if kval == 0:
                v = lor(x, fc, wpk)
            else:
                # два піки на f₀/√(1±k) → зсув по осі пропорційний до частотного зсуву
                dmin = span * (1.0 / (1.0 + kval) ** 0.5 - 1.0)   # нижня мода (ліворуч)
                dplus = span * (1.0 / (1.0 - kval) ** 0.5 - 1.0)  # верхня мода (праворуч)
                v = max(lor(x, fc + dmin, wpk), lor(x, fc + dplus, wpk))
            pts.append((x, oy - v * amp))
        d = "M %.1f,%.1f " % pts[0] + " ".join("L %.1f,%.1f" % p for p in pts[1:])
        style = 'stroke-dasharray="%s"' % dash if dash else ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="2.6" %s/>' % (d, color, style)

    # слабкий зв'язок — один пік
    f.append(draw_curve(0.0, FIELD, gh * 0.95))
    f.append(text(fc, oy - gh * 0.95 - 10, "слабкий k: один пік", size=11, color=FIELD, bold=True))

    # надмірний зв'язок — два піки (провал на f₀)
    f.append(draw_curve(0.28, POS, gh * 0.62, dash="7,5"))
    # позначки нових мод
    dmin = span * (1.0 / (1.0 + 0.28) ** 0.5 - 1.0)
    dplus = span * (1.0 / (1.0 - 0.28) ** 0.5 - 1.0)
    f.append(text(fc + dmin, oy - gh * 0.62 - 10, "f₋ = f₀/√(1+k)", size=10.5, color=POS, anchor="middle"))
    f.append(text(fc + dplus, oy - gh * 0.62 - 10, "f₊ = f₀/√(1−k)", size=10.5, color=POS, anchor="middle"))
    # стрілка на провал
    dipx = fc
    dipy = oy - lor(fc, fc + dmin, wpk) * gh * 0.62 * 1.0
    dipv = max(lor(fc, fc + dmin, wpk), lor(fc, fc + dplus, wpk))
    dipy = oy - dipv * gh * 0.62
    f.append(circle(fc, dipy, 4, fill=POS, stroke=POS, sw=0))
    f.append(text(fc + 8, dipy - 8, "провал на f₀", size=10.5, color=POS, anchor="start"))

    box, bw, bh = textbox(W / 2, 452,
                          "Критичний зв'язок: k ≈ 1/√(Q₁·Q₂). Впритул k переростає його → замість піка провал: «занадто близько теж погано»",
                          size=11.0, pad=9, fill="#fbf7e3", stroke=GOLD)
    f.append(box)

    return render(os.path.join(IMG, 'coupling-splitting.svg'), W, H, *f)


# ── 7. Три лінії стандартів 13.56 МГц сходяться в NFC (для hist-вставки) ──────
def fig_nfc_lineages():
    W, H = 980, 560
    f = [text(W / 2, 30, "Три несумісні світи 13.56 МГц сходяться під дахом NFC", size=17.5, bold=True),
         text(W / 2, 52, "кожна родина зі своїм роком і батьком → спільний стандарт NFCIP-1 (2004) → типи міток NFC Forum",
              size=11.5, color=MUTED, italic=True)]

    # три родини-джерела (ліва колонка)
    srcX = 30
    srcW = 260
    src = [
        (100, "ISO 14443 Type A", "Philips / MIFARE · 1994 (Mikron, Ґраткорн)", "#fdecea", POS),
        (190, "ISO 14443 Type B", "Innovatron + транспорт · «розумна» картка", "#eef2fb", NEG),
        (280, "Sony FeliCa", "Sony · 1988 → Octopus, Гонконг · 1997", "#eef6ef", FIELD),
    ]
    for cy, title_s, sub_s, fill, col in src:
        f.append(fitbox(srcX, cy - 34, srcW, 68, title_s + "\n" + sub_s,
                        size=13, fill=fill, stroke=col, sw=2.2))

    # відхилений «Type C»
    f.append(fitbox(srcX, 350, srcW, 40,
                    "FeliCa → «Type C»?  ВІДХИЛЕНО (WG8)",
                    size=11, fill="#fbfbfb", stroke=MUTED, sw=1.4))
    f.append(text(srcX + srcW / 2, 408, "→ окремо: JIS X 6319-4", size=10, color=MUTED, italic=True))

    # центральний вузол NFCIP-1
    hubX, hubY, hubW, hubH = 385, 150, 210, 120
    f.append(rect(hubX, hubY, hubW, hubH, fill="#fff8e6", stroke=GOLD, sw=3, rx=12))
    f.append(text(hubX + hubW / 2, hubY + 30, "NFCIP-1", size=20, color=GOLD, bold=True))
    f.append(text(hubX + hubW / 2, hubY + 52, "ISO/IEC 18092", size=12, color=INK))
    f.append(text(hubX + hubW / 2, hubY + 70, "= ECMA-340", size=12, color=INK))
    f.append(text(hubX + hubW / 2, hubY + 92, "ISO 08.12.2003", size=10.5, color=MUTED))
    f.append(text(hubX + hubW / 2, hubY + 108, "ECMA грудень 2004", size=10.5, color=MUTED))

    # стрілки джерела → вузол
    for cy, *_rest, col in src:
        f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.4" marker-end="url(#arrow)"/>'
                 % (srcX + srcW, cy, hubX, hubY + hubH / 2, col))

    # успадкування нижніх шарів (підпис під вузлом)
    f.append(fitbox(hubX - 5, hubY + hubH + 16, hubW + 10, 48,
                    "успадкував нижні шари:\n106 кбіт/с = Type A · 212/424 = FeliCa",
                    size=10.5, fill="#fbfdfb", stroke=MUTED, sw=1.2))

    # NFC Forum (над вузлом, праворуч)
    f.append(fitbox(hubX + hubW + 35, 58, 300, 56,
                    "NFC Forum · 18.03.2004\nNXP (Philips) + Sony + Nokia",
                    size=12, fill="#fff8e6", stroke=GOLD, sw=1.8))
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.6" stroke-dasharray="4,4"/>'
             % (hubX + hubW, hubY + 8, hubX + hubW + 35, 100, GOLD))

    # типи міток (права колонка)
    tagX = hubX + hubW + 35
    tagW = 300
    tags = [
        (155, "Type 1 / Type 2", "Topaz · MIFARE Ultralight / NTAG (14443A)", POS),
        (220, "Type 4", "MIFARE DESFire (14443 A/B)", NEG),
        (285, "Type 3", "Sony FeliCa (JIS X 6319-4)", FIELD),
        (350, "Type 5", "ISO 15693 (сусід, «дальше поле»)", MUTED),
    ]
    for cy, title_s, sub_s, col in tags:
        f.append(fitbox(tagX, cy - 26, tagW, 52, title_s + "\n" + sub_s,
                        size=11.5, fill="#ffffff", stroke=col, sw=1.8))
        f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
                 % (hubX + hubW, hubY + hubH / 2, tagX, cy, col))

    # висновок-стрічка внизу
    f.append(rect(30, 470, W - 60, 62, fill="#fbfdfb", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(W / 2, 494, "Три народи не злилися — над ними став перекладач: NFC-читач упізнає тип і говорить кожному його мовою",
                  size=12, color=INK, bold=True))
    f.append(text(W / 2, 514, "колись відхилена FeliCa повертається рівноправним Type 3; 6 базових патентів — Ф. Амтманн (австрієць) і Ф. Можар (француз), 2015",
                  size=10, color=MUTED))

    return render(os.path.join(IMG, 'nfc-lineages.svg'), W, H, *f)


# ── 8. Один прохід колізії: NVB, розрізаний байт, докльований біт ─────────────
#     (до проєктної вставки proj-anticollision-loop.md)
def fig_collision_frame():
    W, H = 940, 500
    f = [text(W / 2, 30, "Один прохід антиколізії: NVB, розрізаний байт і докльований біт", size=17.0, bold=True),
         text(W / 2, 52, "зчитувач шле відомий префікс UID, картка договорює решту — на першій розбіжності колізія",
              size=11.5, color=MUTED, italic=True)]

    cell = 74          # ширина клітинки-байта
    ox = 70
    yq = 122           # рядок «запит зчитувача»

    # ── Рядок 1: кадр-запит зчитувача ──
    f.append(text(ox, yq - 24, "кадр зчитувача (ANTICOLLISION):", size=11.5, color=INK, anchor="start", bold=True))
    labels = [("SEL", "0x93", INK, "#eef2f7"),
              ("NVB", "0x33", POS, "#fbf7e3"),
              ("UID0", "0x9A", FIELD, "#eef6ef"),
              ("UID1*", "3 біти", NEG, "#eaf0ff")]
    for i, (lab, val, col, fill) in enumerate(labels):
        x0 = ox + i * cell
        f.append(rect(x0, yq, cell - 8, 44, fill=fill, stroke=col, sw=1.8))
        f.append(text(x0 + (cell - 8) / 2, yq + 18, lab, size=11, color=col, bold=True))
        f.append(text(x0 + (cell - 8) / 2, yq + 36, val, size=11, color=INK))

    # позначка «розрізаний останній байт»
    xr = ox + 3 * cell + (cell - 8) / 2
    f.append(line(xr, yq + 46, xr, yq + 70, color=NEG, sw=1.4, dash="4,4"))
    f.append(text(xr, yq + 86, "лише старші 3 біти", size=10, color=NEG))
    f.append(text(xr, yq + 100, "tx_last_bits = 3", size=9.5, color=MUTED))

    # NVB розшифровка
    xn = ox + 1 * cell + (cell - 8) / 2
    f.append(text(xn, yq + 86, "0x33 = 3 байти + 3 біти", size=9.5, color=MUTED))
    f.append(text(xn, yq + 100, "(SEL+NVB+UID0 та 3 біти UID1)", size=9, color=MUTED))

    # ── Рядок 2: відповідь карток і колізія ──
    ya = 278
    f.append(text(ox, ya - 24, "картки договорюють біти UID1 (від четвертого біта далі):", size=11.5, color=INK, anchor="start", bold=True))

    bits_a = "011"   # картка A
    bits_b = "010"   # картка B — розходяться на 3-му показаному
    bw = 44
    for i in range(3):
        bx = ox + 150 + i * bw
        f.append(text(bx + (bw - 6) / 2, ya - 6, "b%d" % (4 + i), size=9, color=MUTED))

    def bitrow(y, seq, lab, col):
        f.append(text(ox, y + 20, lab, size=10.5, color=col, anchor="start", bold=True))
        for i, ch in enumerate(seq):
            bx = ox + 150 + i * bw
            fill = "#eef6ef" if ch == "1" else "#ffffff"
            f.append(rect(bx, y, bw - 6, 30, fill=fill, stroke=col, sw=1.6))
            f.append(text(bx + (bw - 6) / 2, y + 21, ch, size=13, color=col, bold=True))

    bitrow(ya, bits_a, "картка A", FIELD)
    bitrow(ya + 44, bits_b, "картка B", GOLD)

    # позначка колізії на 3-й показаній позиції (b6)
    cxpos = ox + 150 + 2 * bw
    f.append(rect(cxpos - 3, ya - 6, bw, 86, fill="none", stroke=POS, sw=2.4, rx=6))
    f.append(text(cxpos + (bw - 6) / 2, ya + 108, "КОЛІЗІЯ", size=12, color=POS, bold=True))
    f.append(text(cxpos + (bw - 6) / 2, ya + 124, "coll_pos тут", size=9.5, color=POS))

    # ── Рядок 3: реакція зчитувача ──
    yb = 442
    box, _, _ = textbox(W / 2, yb,
                        "зчитувач ставить на біті колізії 1, оновлює NVB (префікс +1 біт) і шле знову — картки з 0 тут замовкають",
                        size=11.0, pad=10, fill="#fbf7e3", stroke=GOLD)
    f.append(box)
    f.append(text(W / 2, yb + 40, "кожен прохід подовжує відоме число щонайменше на біт → щонайбільше 32 проходи на каскад",
                  size=10.5, color=MUTED, italic=True))

    return render(os.path.join(IMG, 'collision-frame.svg'), W, H, *f)


if __name__ == '__main__':
    fig_field_falloff()
    fig_sidebands()
    fig_manchester()
    fig_anticollision()
    fig_coupling_falloff()
    fig_coupling_splitting()
    fig_nfc_lineages()
    fig_collision_frame()
    print('OK: field-falloff.svg, sidebands.svg, manchester.svg, anticollision.svg, '
          'coupling-falloff.svg, coupling-splitting.svg, nfc-lineages.svg, collision-frame.svg')
