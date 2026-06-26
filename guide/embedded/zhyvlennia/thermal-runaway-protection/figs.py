# -*- coding: utf-8 -*-
"""Фігури до кроку «Захист від теплової втечі» (guide/embedded/zhyvlennia).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

HOT  = POS        # гаряче, небезпека — червоне
COOL = NEG        # холодне, безпечне — синє
OK   = FIELD      # зелене виділення
WARN = "#caa24a"  # бурштин — проміжний поріг


# ── 1. Одна петля — три маски ────────────────────────────────────────────────
def fig_one_loop_three_masks():
    """Та сама петля додатного теплового зв'язку (нагрів→струм→потужність→нагрів)
    проступає в трьох місцях силового кола. Вага: показати, що це ОДНЕ явище,
    а не три різні біди — звідси й спільний підхід до захисту."""
    W, H = 820, 492
    f = [text(W / 2, 30, "Одна петля теплової втечі — три маски в силовому колі", size=16, bold=True)]

    # ── петля вгорі: чотири ланки по колу ──
    cx, cy, r = W / 2, 150, 92
    nodes = [
        ("нагрів", -90),
        ("струм ↑", 0),
        ("потужність ↑", 90),
        ("ще нагрів", 180),
    ]
    pos = {}
    import math
    for nm, ang in nodes:
        a = math.radians(ang)
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        pos[nm] = (x, y)
    # дуги-стрілки за годинниковою
    order = ["нагрів", "струм ↑", "потужність ↑", "ще нагрів"]
    for i in range(len(order)):
        a0 = order[i]
        a1 = order[(i + 1) % len(order)]
        x0, y0 = pos[a0]
        x1, y1 = pos[a1]
        # трохи підрізати до країв вузлів
        dx, dy = x1 - x0, y1 - y0
        d = (dx * dx + dy * dy) ** 0.5
        ux, uy = dx / d, dy / d
        f.append(arrow(x0 + ux * 40, y0 + uy * 22, x1 - ux * 40, y1 - uy * 22, color=HOT, sw=2.2))
    for nm in order:
        x, y = pos[nm]
        col = HOT if nm in ("нагрів", "ще нагрій", "ще нагрів") else INK
        b, bw, bh = textbox(x, y, nm, size=11.5, fill="#fdecea", stroke=HOT, sw=1.8, bold=True, color=INK)
        f.append(b)
    f.append(text(cx, cy + 4, "+", size=26, color=HOT, bold=True))
    f.append(text(cx, cy + 26, "знак петлі", size=9, color=MUTED))

    # умова втечі — праворуч від петлі
    f.append(fitbox(cx + r + 30, cy - 34, 196, 64,
                    "Петля втікає, коли\nпідсилення за оберт ≥ 1.\nЗахист = тримати його < 1\nабо розірвати петлю.",
                    size=10, fill="#fff", stroke=INK, sw=1.4))

    # ── три колонки-маски внизу ──
    masks = [
        ("Лінійний транзистор", COOL,
         "LDO, клас A, hot-swap:\nVbeↆ або низький Vgs.\nРозрив: емітерний R,\nтеплова компенсація.",
         "#eaf0fd"),
        ("Паралельні ключі", WARN,
         "Спільна напруга керування:\n«жадібний» загарбує струм.\nРозрив: баластний R\nу кожному емітері/витоку.",
         "#fdf6e3"),
        ("Комірка акумулятора", HOT,
         "Дефект/прокол/перезаряд:\nекзотерм. реакції з ~80–120°.\nПетлю НЕ розірвати —\nлише ловити й стримувати.",
         "#fdecea"),
    ]
    colw = 244
    gap = (W - 40 - 3 * colw) / 2
    x = 20
    top = 290
    bh = 150
    for nm, col, body, fill in masks:
        f.append(rect(x, top, colw, bh, fill=fill, stroke=col, sw=1.9))
        f.append(text(x + colw / 2, top + 24, nm, size=12.5, color=col, bold=True))
        f.append(line(x + 16, top + 34, x + colw - 16, top + 34, color=col, sw=1))
        f.append(mtext(x + colw / 2, top + 58, body.split("\n"), size=10, color=INK, lh=1.32))
        # тонка стрілка від петлі донизу
        f.append(line(x + colw / 2, top - 14, x + colw / 2, top - 2, color=MUTED, sw=1.2, dash="2 3"))
        x += colw + gap

    f.append(fitbox(20, top + bh + 12, W - 40, 28,
                    "Дві маски ліворуч лікують схемотехнікою (розірвати петлю); праву — лише шарами захисту, бо тепло народжується всередині комірки.",
                    size=10, fill="#eafaf0", stroke=OK, sw=1.3))
    render(os.path.join(IMG, "one-loop-three-masks.svg"), W, H, *f)


# ── 2. Захист шарами (defense in depth) ──────────────────────────────────────
def fig_defense_layers():
    """Чотири рубежі захисту, від найшвидшого незалежного заліза до фізичного
    стримування. Вага: показати, що firmware — лише перший рубіж, і що головні
    рубежі мусять спрацювати БЕЗ мікроконтролера."""
    W, H = 820, 460
    f = [text(W / 2, 30, "Захист шарами: кожен наступний рубіж ловить те, що пропустив попередній", size=15, bold=True)]

    layers = [
        ("1", "Прошивка: foldback", "зрізає струм за °C і dT/dt", OK, "швидко, але гине з МК",
         "#eafaf0"),
        ("2", "Залізо: OTP-компаратор", "поріг у залізі рве затвор/драйв", WARN, "працює, коли МК завис",
         "#fdf6e3"),
        ("3", "Незалежний розрив", "запобіжник / eFuse / контактор", HOT, "остання електрична лінія",
         "#fdecea"),
        ("4", "Фізичне стримування", "зазори, бар'єри, відведення газів", HOT, "комірка згоріла — пакет цілий",
         "#fdecea"),
    ]
    n = len(layers)
    bx = 60
    bw = W - 2 * bx
    bh = 62
    gap = 16
    y = 70
    for num, title, sub, col, note, fill in layers:
        f.append(rect(bx, y, bw, bh, fill=fill, stroke=col, sw=2.0))
        # номер-кружок
        f.append(circle(bx + 30, y + bh / 2, 17, fill="#fff", stroke=col, sw=2))
        f.append(text(bx + 30, y + bh / 2 + 6, num, size=16, color=col, bold=True))
        f.append(text(bx + 64, y + 24, title, size=13, color=INK, bold=True, anchor="start"))
        f.append(text(bx + 64, y + 44, sub, size=10.5, color=MUTED, anchor="start"))
        # права колонка-нотатка
        f.append(text(bx + bw - 18, y + bh / 2 + 4, note, size=10.5, color=col, anchor="end", bold=True))
        # стрілка «пропустив → наступний»
        if num != str(n):
            f.append(arrow(bx + bw / 2, y + bh, bx + bw / 2, y + bh + gap - 2, color=MUTED, sw=1.6))
        y += bh + gap

    # вісь незалежності від МК ліворуч
    f.append(arrow(34, 80, 34, y - gap - 6, color=MUTED, sw=1.6))
    f.append('<text x="22" y="%d" font-family="%s" font-size="10" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 22 %d)">що нижче — то незалежніше від прошивки →</text>'
             % (int((80 + y) / 2), FONT, MUTED, int((80 + y) / 2)))

    render(os.path.join(IMG, "defense-layers.svg"), W, H, *f)


# ── 3. Поріг за рівнем І за швидкістю ─────────────────────────────────────────
def fig_threshold_and_rate():
    """Дві осі захисту: абсолютна температура (робота/попередження/аварія) і
    швидкість dT/dt. Вага: показати, ЧОМУ самого порога мало — комірка в утечі
    злітає так круто, що поки чекаєш аварійний рівень, уже пізно; рятує rate-trip."""
    W, H = 820, 440
    f = [text(W / 2, 30, "Ловити втечу за РІВНЕМ і за ШВИДКІСТЮ: чому самого порога мало", size=15, bold=True)]

    ox, oy = 80, 330
    axw, axh = 660, 250
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 6, oy + 26, "час", size=11, color=INK, anchor="end"))
    f.append('<text x="34" y="%d" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 34 %d)">температура комірки</text>'
             % (oy - axh // 2, FONT, INK, oy - axh // 2))

    def ty(frac): return oy - frac * (axh - 16)

    # горизонтальні пороги
    for frac, lab, col in [(0.45, "робоча межа", OK), (0.62, "попередження", WARN), (0.82, "аварія", HOT)]:
        f.append(line(ox, ty(frac), ox + axw, ty(frac), color=col, sw=1.3, dash="5 4"))
        f.append(text(ox + axw + 2, ty(frac) + 4, lab, size=9.5, color=col, anchor="start", bold=True))

    # нормальний нагрів — пологий, виходить на плато під попередженням
    pts = []
    import math
    N = 80
    for i in range(N + 1):
        t = i / N
        x = ox + t * axw * 0.74
        y = ty(0.18 + 0.34 * (1 - math.exp(-3.2 * t)))
        pts.append((x, y))
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (path, OK))
    f.append(text(ox + axw * 0.40, ty(0.30), "нормальна робота", size=10, color=OK, bold=True))

    # втеча — повзе як усі, тоді раптом злітає круто
    bx = ox + axw * 0.40         # точка зриву
    pts2 = [(ox, ty(0.18))]
    for i in range(0, 41):
        t = i / 40.0
        x = ox + t * (bx - ox)
        y = ty(0.18 + 0.30 * (1 - math.exp(-3.0 * t)))
        pts2.append((x, y))
    # крутий злет
    x_s = pts2[-1][0]
    y_s = pts2[-1][1]
    for i in range(1, 26):
        t = i / 25.0
        x = x_s + t * (axw * 0.16)
        y = y_s - (y_s - ty(0.95)) * (t ** 1.6)
        pts2.append((x, y))
    path2 = "M " + " L ".join("%.1f %.1f" % p for p in pts2)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (path2, HOT))
    f.append(text(bx - 6, ty(0.16), "та сама комірка йде в утечу", size=10, color=HOT, bold=True, anchor="end"))

    # де ловить кожен механізм
    # 1) рівень «аварія» — ловить надто пізно
    xcross = x_s + axw * 0.16 * 0.78
    f.append(circle(xcross, ty(0.82), 5, fill="#fff", stroke=HOT, sw=2))
    f.append(mtext(xcross + 10, ty(0.86), ["поріг «аварія»", "ловить уже на злеті"], size=9, color=HOT, anchor="start"))
    # 2) rate-trip — ловить на самому коліні, набагато раніше
    f.append(circle(x_s + axw * 0.02, y_s - 10, 5, fill="#fff", stroke=COOL, sw=2))
    f.append(mtext(x_s + axw * 0.02, y_s - 50, ["rate-trip:", "крутий dT/dt", "рве раніше"], size=9, color=COOL, anchor="middle"))
    f.append(arrow(x_s + axw * 0.02, y_s - 22, x_s + axw * 0.02, y_s - 12, color=COOL, sw=1.6))

    f.append(fitbox(ox, oy + 40, axw, 30,
                    "Комірка в утечі деякий час виглядає нормальною, тоді злітає за секунди — чекати абсолютний поріг пізно; крутизну dT/dt видно раніше.",
                    size=10, fill="#eaf0fd", stroke=COOL, sw=1.3))
    render(os.path.join(IMG, "threshold-and-rate.svg"), W, H, *f)


# ── 4. Пастка лінійного режиму MOSFET (ZTC) ──────────────────────────────────
def fig_mosfet_linear_trap():
    """Передавальна крива Id(Vgs) холодного й гарячого кристала перетинаються в
    точці ZTC. Нижче ZTC (малий Vgs, лінійний режим) гарячий бере БІЛЬШЕ струму
    — додатний зв'язок, можлива втеча; вище ZTC — менше, ключ сам стабілізується.
    Вага: розбити поширений міф «MOSFET не йде в розгін»."""
    W, H = 820, 440
    f = [text(W / 2, 30, "Пастка лінійного режиму MOSFET: міф «не йде в розгін» хибний", size=15, bold=True)]

    ox, oy = 90, 340
    axw, axh = 560, 268
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 6, oy + 26, "напруга на затворі Vgs", size=11, color=INK, anchor="end"))
    f.append('<text x="40" y="%d" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 40 %d)">струм стоку Id</text>'
             % (oy - axh // 2, FONT, INK, oy - axh // 2))

    import math
    # дві експонент-подібні криві, що перетинаються в ZTC
    def curve(vth, scale):
        pts = []
        v = 0.0
        while v <= 1.0:
            id_ = scale * (math.exp(3.4 * (v - vth)) - math.exp(-3.4 * vth))
            if id_ < 0:
                id_ = 0
            x = ox + v * axw
            y = oy - min(id_, 1.05) * (axh - 14)
            pts.append((x, y))
            v += 0.01
        return pts

    # холодна (нижчий поріг провідності, крутіша внизу) і гаряча
    cold = curve(0.42, 0.34)
    hot = curve(0.34, 0.30)
    pc = "M " + " L ".join("%.1f %.1f" % p for p in cold)
    ph = "M " + " L ".join("%.1f %.1f" % p for p in hot)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (pc, COOL))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (ph, HOT))
    f.append(text(ox + axw * 0.30, oy - axh * 0.86, "гарячий", size=10.5, color=HOT, bold=True))
    f.append(text(ox + axw * 0.52, oy - axh * 0.86, "холодний", size=10.5, color=COOL, bold=True))

    # знайти точку перетину чисельно
    vz = None
    for i in range(1, 100):
        v = i / 100.0
        a = 0.34 * (math.exp(3.4 * (v - 0.42)) - math.exp(-3.4 * 0.42))
        b = 0.30 * (math.exp(3.4 * (v - 0.34)) - math.exp(-3.4 * 0.34))
        if a >= b:
            vz = v
            idz = b
            break
    if vz is None:
        vz, idz = 0.72, 0.5
    zx = ox + vz * axw
    zy = oy - min(idz, 1.05) * (axh - 14)
    f.append(line(zx, oy, zx, zy, color=INK, sw=1.1, dash="3 4"))
    f.append(circle(zx, zy, 5, fill="#fff", stroke=INK, sw=2))
    f.append(text(zx, oy + 16, "ZTC", size=10.5, color=INK, bold=True))

    # зони ліворуч і праворуч від ZTC
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10"/>'
             % (ox, oy - axh, zx - ox, axh, HOT))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10"/>'
             % (zx, oy - axh, ox + axw - zx, axh, OK))

    f.append(fitbox(ox + 12, oy - axh + 8, max(120, zx - ox - 24), 70,
                    "Лінійний режим\n(малий Vgs):\nгарячий бере БІЛЬШЕ\n→ петля, можлива втеча",
                    size=9.5, fill="#fff", stroke=HOT, sw=1.4))
    f.append(fitbox(zx + 14, oy - axh + 8, ox + axw - zx - 26, 70,
                    "Відкритий ключ\n(великий Vgs):\nгарячий бере МЕНШЕ\n→ сам стабілізується",
                    size=9.5, fill="#fff", stroke=OK, sw=1.4))

    f.append(fitbox(40, oy + 40, W - 80, 30,
                    "Додатний tempco Rds(on) рятує лише як відкритий ключ; у лінійному режимі (hot-swap, обмежувач) MOSFET так само втікає.",
                    size=10, fill="#fdecea", stroke=HOT, sw=1.3))
    render(os.path.join(IMG, "mosfet-linear-trap.svg"), W, H, *f)


# ══════════════════════════════════════════════════════════════════════════════
#  Фігури до вставки proj-propagation-barrier (стримування поширення втечі)
# ══════════════════════════════════════════════════════════════════════════════

# ── 5. Теплові шляхи сусід-до-сусіда й де працює кожен бар'єр ──────────────────
def fig_heat_paths():
    """Три канали тепла від комірки-в-утечі до сусідки (зазор+бар'єр, шина/виводи,
    гарячий газ/полум'я) і де саме кожен бар'єр перехоплює. Вага: показати, що
    бар'єр між боками комірок НЕ закриває обхід шиною й вентиляцію — три різні
    шляхи треба перекривати трьома різними засобами."""
    W, H = 860, 470
    f = [text(W / 2, 30, "Три шляхи тепла від комірки-в-утечі до сусідки — і де працює кожен бар'єр", size=15, bold=True)]

    # дві комірки збоку: ліворуч — у втечі (гаряча), праворуч — сусідка (поки холодна)
    cw, ch = 150, 230
    y0 = 90
    xL = 150
    xR = 520
    f.append(rect(xL, y0, cw, ch, fill="#fdecea", stroke=HOT, sw=2.4))
    f.append(mtext(xL + cw / 2, y0 + ch / 2 - 6, ["КОМІРКА", "В УТЕЧІ", "≈ 600–900 °C"], size=13, color=HOT, bold=True))
    f.append(rect(xR, y0, cw, ch, fill="#eaf0fd", stroke=COOL, sw=2.2))
    f.append(mtext(xR + cw / 2, y0 + ch / 2 - 6, ["СУСІДКА", "поки ~25 °C", "поріг ≈150 °C"], size=13, color=COOL, bold=True))

    midy = y0 + ch / 2

    # бар'єр у зазорі (вузька смужка між боками)
    bx = xL + cw + 80
    f.append(rect(bx, y0 + 20, 26, ch - 40, fill="#f0e6cf", stroke=WARN, sw=2))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="10" fill="%s" '
             'text-anchor="middle" font-weight="700" transform="rotate(-90 %.1f %.1f)">бар\'єр у зазорі</text>'
             % (bx + 13, midy, FONT, WARN, bx + 13, midy))

    # 1) кондукція бік-до-боку через зазор → перехоплює бар'єр
    f.append(arrow(xL + cw, midy - 40, xR, midy - 40, color=HOT, sw=2.6))
    f.append(text((xL + cw + xR) / 2, midy - 50, "1 · кондукція через зазор", size=10.5, color=HOT, bold=True))
    f.append(text(bx + 13, y0 + 8, "✓ ловить", size=9, color=FIELD, bold=True))

    # 2) обхід виводами/шиною поверху → бар'єр у зазорі НЕ ловить
    busy = y0 - 4
    f.append(line(xL + cw / 2, y0, xL + cw / 2, busy, color=INK, sw=2))
    f.append(line(xR + cw / 2, y0, xR + cw / 2, busy, color=INK, sw=2))
    f.append(rect(xL + cw / 2 - 4, busy - 14, (xR + cw / 2) - (xL + cw / 2) + 8, 14, fill="#d9dde2", stroke=INK, sw=1.6, rx=3))
    f.append(arrow(xL + cw / 2 + 30, busy - 7, xR + cw / 2 - 30, busy - 7, color=HOT, sw=2.4))
    f.append(text((xL + xR) / 2 + cw / 2, busy - 22, "2 · обхід шиною/виводами — бар'єр у зазорі тут безсилий", size=10.5, color=HOT, bold=True))

    # 3) гарячий газ/полум'я з клапана вниз → канал вентиляції
    venty = y0 + ch + 6
    f.append(line(xL + cw / 2, y0 + ch, xL + cw / 2, venty, color=INK, sw=2))
    f.append(text(xL + cw / 2, venty + 14, "клапан", size=9, color=MUTED))
    for i in range(5):
        xx = xL + cw / 2 + 18 + i * 26
        f.append(arrow(xx - 14, venty + 4, xx + 6, venty + 16, color=HOT, sw=2.0))
    f.append(text((xL + cw / 2) + 70, venty + 40, "3 · гарячий газ ≫800 °C і полум'я", size=10.5, color=HOT, bold=True, anchor="start"))
    # канал відведення
    f.append(rect(xL + cw / 2 - 10, venty + 48, xR + cw / 2 - xL - cw / 2 + 80, 22, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=4))
    f.append(text((xL + xR) / 2 + 40, venty + 63, "канал вентиляції відводить гази НАЗОВНІ, повз сусідок ✓", size=10, color=FIELD, bold=True))

    render(os.path.join(IMG, "heat-paths.svg"), W, H, *f)


# ── 6. Час до запалення сусідки: з бар'єром і без ─────────────────────────────
def fig_time_to_ignition():
    """Температура сусідки повзе до порога запалення; тонкий зазор доводить її до
    порога за десятки секунд, товстий бар'єр — або за багато хвилин, або взагалі
    виходить на плато нижче порога. Вага: показати фізичний сенс «5-хвилинного
    вікна» — бар'єр не «не пускає тепло», а РОЗТЯГУЄ час до запалення."""
    W, H = 820, 440
    f = [text(W / 2, 30, "Час до запалення сусідки: тонкий зазор VS товстий бар'єр", size=15, bold=True)]

    ox, oy = 80, 330
    axw, axh = 640, 250
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 6, oy + 26, "час від зриву сусіда", size=11, color=INK, anchor="end"))
    f.append('<text x="34" y="%d" font-family="%s" font-size="11" fill="%s" '
             'text-anchor="middle" transform="rotate(-90 34 %d)">температура сусідки</text>'
             % (oy - axh // 2, FONT, INK, oy - axh // 2))

    def ty(frac): return oy - frac * (axh - 16)
    def tx(frac): return ox + frac * axw

    import math
    # поріг запалення сусідки
    f.append(line(ox, ty(0.80), ox + axw, ty(0.80), color=HOT, sw=1.4, dash="6 4"))
    f.append(text(ox + axw + 2, ty(0.80) + 4, "поріг ≈150 °C", size=9.5, color=HOT, anchor="start", bold=True))
    # позначка «вікно евакуації / норматив 5 хв»
    f.append(line(tx(0.62), oy, tx(0.62), oy - axh, color=FIELD, sw=1.2, dash="3 4"))
    f.append(text(tx(0.62), oy - axh - 4, "ціль: ≥ 5 хв (норматив)", size=9.5, color=FIELD, bold=True))

    base = 0.12   # стартова ~25 °C

    # тонкий зазор: швидко доходить порога (експонента до високого усталеного)
    pts = []
    for i in range(81):
        t = i / 80.0
        frac = base + (1.05 - base) * (1 - math.exp(-3.6 * t))
        pts.append((tx(t * 0.55), ty(min(frac, 1.0))))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % ("M " + " L ".join("%.1f %.1f" % p for p in pts), HOT))
    # точка перетину порога
    f.append(circle(tx(0.205), ty(0.80), 5, fill="#fff", stroke=HOT, sw=2))
    f.append(mtext(tx(0.205) + 8, ty(0.92), ["тонкий зазор:", "поріг за ~десятки с", "→ сусідка зривається"], size=9.5, color=HOT, anchor="start", bold=False))

    # товстий бар'єр: пологий підйом, виходить на плато НИЖЧЕ порога
    pts2 = []
    for i in range(81):
        t = i / 80.0
        frac = base + (0.62 - base) * (1 - math.exp(-0.9 * t))
        pts2.append((tx(t), ty(frac)))
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % ("M " + " L ".join("%.1f %.1f" % p for p in pts2), COOL))
    f.append(mtext(tx(0.74), ty(0.50), ["товстий бар'єр:", "плато НИЖЧЕ порога", "сусідка вціліла"], size=9.5, color=COOL, anchor="middle", bold=False))

    f.append(fitbox(ox, oy + 40, axw, 30,
                    "Бар'єр не «не пускає» тепло, а розтягує час до запалення: досить, щоб сусідка вийшла на плато нижче порога — або щоб вистачило виграного вікна.",
                    size=10, fill="#eaf0fd", stroke=COOL, sw=1.3))
    render(os.path.join(IMG, "time-to-ignition.svg"), W, H, *f)


# ── 7. Детектор події поширення: рівень + швидкість + ПРОСТОРОВИЙ розкид ───────
def fig_propagation_detector():
    """Чому проти поширення мало порога й dT/dt на одному давачі: треба бачити
    ПРОСТОРОВИЙ розкид — одна зона злетіла, сусідні ще холодні. Вага: показати
    логіку, що відрізняє локальну подію (втеча комірки) від загального нагріву
    всього пакета, і дерево команд (контактор + вентиляція)."""
    W, H = 880, 560
    f = [text(W / 2, 30, "Детектор події поширення: локальний сплеск VS рівний нагрів пакета", size=15, bold=True)]

    # дві мапи зон пакета 4×2
    def pack_map(x0, y0, temps, title, col):
        cell = 52
        out = [text(x0 + 2 * cell, y0 - 10, title, size=11.5, color=col, bold=True, anchor="middle")]
        for r in range(2):
            for c in range(4):
                v = temps[r][c]
                fill = "#fdecea" if v >= 150 else ("#f7efd6" if v >= 60 else "#eaf0fd")
                stk = HOT if v >= 150 else (WARN if v >= 60 else COOL)
                out.append(rect(x0 + c * cell, y0 + r * cell, cell - 4, cell - 4, fill=fill, stroke=stk, sw=1.8, rx=4))
                out.append(text(x0 + c * cell + (cell - 4) / 2, y0 + r * cell + (cell - 4) / 2 + 4,
                                "%d°" % v, size=10.5, color=stk, bold=True))
        return out

    # ліворуч: подія поширення — одна зона гаряча, решта холодні
    evt = [[28, 27, 210, 29], [27, 95, 28, 26]]
    f += pack_map(70, 90, evt, "ПОДІЯ: одна зона злетіла, сусіди холодні", HOT)
    f.append(fitbox(58, 230, 360, 58,
                    "Максимум високий, dT/dt крутий, але РОЗКИД\nвеликий → локальна втеча комірки,\nне загальний перегрів пакета.",
                    size=10.5, fill="#fdecea", stroke=HOT, sw=1.4))

    # праворуч: рівний нагрів — усі теплі майже однаково
    amb = [[64, 66, 67, 65], [66, 68, 65, 67]]
    f += pack_map(540, 90, amb, "НЕ подія: увесь пакет нагрівся рівно", FIELD)
    f.append(fitbox(500, 230, 360, 58,
                    "Максимум помірний, розкид малий → нагрів\nвід навантаження чи спеки. Тут — звичайний\nfoldback, а не аварія поширення.",
                    size=10.5, fill="#eef6ef", stroke=FIELD, sw=1.4))

    # дерево рішення внизу
    ty0 = 320
    f.append(fitbox(W / 2 - 200, ty0, 400, 44, "на кожну зону: рівень І dT/dt І розкид по сусідах", size=12, fill=FILL, stroke=INK, sw=1.8, bold=True))
    f.append(arrow(W / 2, ty0 + 44, W / 2, ty0 + 64, color=INK, sw=1.8))
    f.append(fitbox(W / 2 - 140, ty0 + 64, 280, 38, "локальний сплеск підтверджено?", size=12, fill="#fff", stroke=HOT, sw=1.8, bold=True))

    # дві гілки
    yb = ty0 + 140
    f.append(arrow(W / 2 - 60, ty0 + 102, W / 2 - 170, yb, color=HOT, sw=1.8))
    f.append(text(W / 2 - 145, ty0 + 122, "так", size=10, color=HOT, bold=True))
    f.append(arrow(W / 2 + 60, ty0 + 102, W / 2 + 170, yb, color=FIELD, sw=1.8))
    f.append(text(W / 2 + 140, ty0 + 122, "ні", size=10, color=FIELD, bold=True))

    f.append(fitbox(W / 2 - 320, yb, 300, 78,
                    "ПОДІЯ ПОШИРЕННЯ:\n• розірвати контактор\n• увімкнути вентиляцію\n• засув: без автоскиду",
                    size=11, fill="#fdecea", stroke=HOT, sw=2))
    f.append(fitbox(W / 2 + 20, yb, 300, 78,
                    "штатний тепловий режим:\n• foldback за рівнем\n• стежити далі\n• це не аварія поширення",
                    size=11, fill="#eef6ef", stroke=FIELD, sw=1.8))

    render(os.path.join(IMG, "propagation-detector.svg"), W, H, *f)


if __name__ == "__main__":
    fig_one_loop_three_masks()
    fig_defense_layers()
    fig_threshold_and_rate()
    fig_mosfet_linear_trap()
    fig_heat_paths()
    fig_time_to_ignition()
    fig_propagation_detector()
    print("OK: 4 figures ->", IMG)
