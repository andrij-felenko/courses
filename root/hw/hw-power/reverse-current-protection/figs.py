# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def diode_h(cx, cy, forward='left', color=INK, s=13, sw=2.6):
    """Горизонтальний символ діода з центром (cx,cy).
    forward='left'  -> проводить справа наліво (вістря/катод ліворуч);
    forward='right' -> проводить зліва направо (вістря/катод праворуч)."""
    if forward == 'right':
        tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" '
               'stroke="%s" stroke-width="%.1f"/>'
               % (cx - s, cy - s, cx - s, cy + s, cx + s, cy, color, sw))
        bar = line(cx + s, cy - s, cx + s, cy + s, color=color, sw=sw)
    else:
        tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="none" '
               'stroke="%s" stroke-width="%.1f"/>'
               % (cx + s, cy - s, cx + s, cy + s, cx - s, cy, color, sw))
        bar = line(cx - s, cy - s, cx - s, cy + s, color=color, sw=sw)
    return tri + bar


def xmark(cx, cy, r=12, color=POS, sw=3.4):
    return (line(cx - r, cy - r, cx + r, cy + r, color=color, sw=sw) +
            line(cx - r, cy + r, cx + r, cy - r, color=color, sw=sw))


def zigzag(x, ytop, ybot, n=7, amp=9, color=MUTED, sw=2.4):
    """Вертикальна пружина-зигзаг від (x,ytop) до (x,ybot)."""
    pts = [(x, ytop)]
    span = ybot - ytop
    for i in range(1, n):
        dx = amp if i % 2 else -amp
        pts.append((x + dx, ytop + span * i / n))
    pts.append((x, ybot))
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (d, color, sw))


# ── 1. Звідки береться зворотний струм: три різні причини, один корінь ───────
def fig_where():
    W, H = 1160, 470
    parts = []
    parts.append(line(W / 3, 52, W / 3, H - 92, color=MUTED, sw=1, dash="6 6"))
    parts.append(line(2 * W / 3, 52, 2 * W / 3, H - 92, color=MUTED, sw=1, dash="6 6"))

    cxs = [W / 6, W / 2, 5 * W / 6]
    heads = ["Резервоване живлення", "Вимкнена рейка", "Панель уночі"]
    hcol = [FIELD, NEG, MUTED]
    tops = ["Джерело A\nживий  12 В", "USB  5 В\nживий", "Батарея\n12.6 В"]
    tcol = [FIELD, FIELD, POS]
    tfill = ["#eafaf0", "#eafaf0", "#fdecea"]
    bots = ["Джерело B\nвідмовив ≈ 0 В", "Головні  5 В\nВИМКНЕНО", "Панель\nтемно ≈ 0 В"]
    caps = ["живий блок ллє струм\nу мертвий, як у КЗ",
            "живий USB жене струм\nназад — рейка не гасне",
            "заряд тече назад\nкрізь панель, марно"]
    arrlbl = ["зворотний струм", "крізь body-діод", "розряд назад"]

    ty, by = 150, 300
    for cx, hd, hc, tp, tc, tf, bt, cp, al in zip(cxs, heads, hcol, tops, tcol, tfill, bots, caps, arrlbl):
        parts.append(text(cx, 74, hd, size=16, bold=True, color=hc))
        b1, w1, h1 = textbox(cx, ty, tp, size=13, pad=11, bold=True,
                             fill=tf, stroke=tc, color=tc)
        b2, w2, h2 = textbox(cx, by, bt, size=13, pad=11, bold=True,
                             fill="#f4f6f8", stroke=MUTED, color=INK)
        parts += [b1, b2]
        # зворотна стрілка згори вниз (небезпечний напрям)
        parts.append(arrow(cx - 78, ty + h1 / 2 + 6, cx - 78, by - h2 / 2 - 6, color=POS, sw=4))
        parts.append(text(cx + 96, (ty + by) / 2 - 6, al, size=11.5, color=POS, bold=True))
        # маленька плашка-пояснення праворуч від стрілки
        parts.append(fitbox(cx - 62, (ty + by) / 2 - 26, 150, 52, cp,
                            size=11, fill="#fff7f6", stroke=POS, color=POS))

    parts.append(fitbox(W / 2 - 430, H - 66, 860, 40,
                        "Спільний корінь усіх трьох: щойно нижча сторона порту стає ВИЩОЮ за джерело — струм повертає назад, у бік, на який порт не розрахований.",
                        size=13, fill="#f4f6f8", stroke=LINE, color=INK, bold=True))
    return render(os.path.join(OUT, 'where-reverse.svg'), W, H, *parts,
                  title="Три різні причини зворотного струму — один спільний механізм")


# ── 2. Пастка body-діода: один ключ пропускає реверс, back-to-back — ні ──────
def fig_body_diode_trap():
    W, H = 1000, 470
    parts = []
    parts.append(line(W / 2, 52, W / 2, H - 74, color=MUTED, sw=1, dash="6 6"))
    ymid = 232

    # ── ЛІВА панель: один MOSFET-ключ, вимкнений ────────────────────────────
    parts.append(text(W * 0.25, 74, "Один MOSFET-ключ (ВИМКНЕНО)", size=16, bold=True, color=POS))
    lx, rx = 70, 430          # межі кола
    swx = 250                 # ключ (канал)
    dy = 88                   # гілка body-діода нижче
    # верхня гілка — канал (ключ), розірваний
    parts.append(line(lx, ymid, swx - 34, ymid, color=LINE, sw=2.4))
    parts.append(line(swx + 34, ymid, rx, ymid, color=LINE, sw=2.4))
    kb, kw, kh = textbox(swx, ymid, "канал\nрозірвано", size=12, pad=9, bold=True,
                        fill="#f4f6f8", stroke=MUTED, color=MUTED)
    parts.append(kb)
    parts.append(xmark(swx, ymid - 2, r=10, color=POS, sw=3))
    # нижня гілка — body-діод (проводить у зворотний бік: справа наліво)
    parts.append(line(lx, ymid, lx, ymid + dy, color=LINE, sw=2.4))
    parts.append(line(rx, ymid, rx, ymid + dy, color=LINE, sw=2.4))
    parts.append(line(lx, ymid + dy, swx - 20, ymid + dy, color=LINE, sw=2.4))
    parts.append(line(swx + 20, ymid + dy, rx, ymid + dy, color=LINE, sw=2.4))
    parts.append(diode_h(swx, ymid + dy, forward='left', color=INK))
    parts.append(text(swx, ymid + dy + 34, "body-діод", size=12, color=INK, bold=True))
    # позначки кінців
    parts.append(text(lx, ymid - 20, "джерело", size=12, color=MUTED, anchor="middle"))
    parts.append(text(rx, ymid - 20, "вихід", size=12, color=MUTED, anchor="middle"))
    # зворотний струм: з виходу (справа) назад у джерело крізь body-діод
    parts.append(arrow(rx - 30, ymid + dy + 20, lx + 30, ymid + dy + 20, color=POS, sw=4))
    parts.append(fitbox(W * 0.25 - 185, ymid + dy + 42, 370, 52,
                        "зворотний струм проходить крізь\nbody-діод — попри вимкнений канал",
                        size=12, fill="#fff7f6", stroke=POS, color=POS, bold=True))

    # ── ПРАВА панель: два MOSFET спина-до-спини ─────────────────────────────
    off = W / 2
    parts.append(text(W * 0.75, 74, "Два MOSFET спина-до-спини", size=16, bold=True, color=FIELD))
    lx2, rx2 = off + 70, off + 430
    mid = (lx2 + rx2) / 2
    d1, d2 = mid - 96, mid + 96
    parts.append(line(lx2, ymid, d1 - 20, ymid, color=LINE, sw=2.4))
    parts.append(diode_h(d1, ymid, forward='left', color=INK))     # катод ліворуч
    parts.append(line(d1 + 20, ymid, d2 - 20, ymid, color=LINE, sw=2.4))
    parts.append(diode_h(d2, ymid, forward='right', color=INK))    # катод праворуч
    parts.append(line(d2 + 20, ymid, rx2, ymid, color=LINE, sw=2.4))
    parts.append(circle(mid, ymid, 4, fill=INK, stroke=INK))
    parts.append(text(mid, ymid - 20, "аноди разом", size=11.5, color=MUTED))
    parts.append(text(d1, ymid + 34, "body 1", size=11.5, color=INK, bold=True))
    parts.append(text(d2, ymid + 34, "body 2", size=11.5, color=INK, bold=True))
    parts.append(text(lx2, ymid - 20, "джерело", size=12, color=MUTED))
    parts.append(text(rx2, ymid - 20, "вихід", size=12, color=MUTED))
    # спроба зворотного струму справа — впирається в катод діода 2
    parts.append(arrow(rx2 - 20, ymid + 70, d2 + 24, ymid + 70, color=POS, sw=4))
    parts.append(xmark(d2, ymid + 70, r=11, color=POS, sw=3.2))
    parts.append(fitbox(W * 0.75 - 185, ymid + 96, 370, 52,
                        "будь-який напрям упирається у зворотно\nзміщений діод — глухо в обидва боки",
                        size=12, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))

    return render(os.path.join(OUT, 'body-diode-trap.svg'), W, H, *parts,
                  title="Чому один ключ не блокує реверс, а два — блокують")


# ── 3. Час реакції активного клапана: скільки реверсу встигає просочитися ────
def fig_response():
    W, H = 900, 470
    parts = []
    ox, aw = 118, 690
    zy = 244                  # лінія нуля струму (I = 0)
    up, dn = 150, 150         # висота вгору (прямий) / вниз (реверс)

    # осі
    parts.append(line(ox, zy - up - 18, ox, zy + dn + 18, color=INK, sw=2))   # Y
    parts.append(arrow(ox, zy, ox + aw, zy, color=INK, sw=2))                  # X (нуль струму)
    parts.append(text(ox + aw - 4, zy - 10, "час →", size=13, color=INK, anchor="end"))
    parts.append(text(ox - 12, zy - up - 6, "струм", size=13, color=INK, anchor="end"))
    parts.append(text(ox - 12, zy - up + 12, "+ вперед", size=11, color=FIELD, anchor="end"))
    parts.append(text(ox - 12, zy + dn + 4, "− назад", size=11, color=POS, anchor="end"))

    def xt(f):
        return ox + aw * f

    t0 = 0.40                 # струм повернув
    tr = 0.60                 # контролер відкрив ключ
    yfwd = zy - up * 0.72     # рівень прямого струму
    yrev = zy + dn * 0.80     # пік зворотного крізь body-діод

    # прямий струм (зелений) до t0
    parts.append(line(ox, yfwd, xt(t0), yfwd, color=FIELD, sw=3.4))
    parts.append(text(xt(t0 / 2), yfwd - 12, "прямий струм", size=12.5, color=FIELD, bold=True))

    # зона реверсу (заштрихована) t0..tr — заряд, що просочився
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
                 'stroke="none"/>' % (xt(t0), zy, xt(tr) - xt(t0), yrev - zy))
    # крива струму: вниз через нуль до піка, тримається, тоді стрибок у нуль
    path = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="3.4"/>'
            % (xt(t0), yfwd, xt(t0), yrev, xt(tr), yrev, xt(tr), zy, xt(0.98), zy, POS))
    parts.append(path)

    # вертикальні пунктири на t0 і tr
    for f, lbl, col in [(t0, "струм повернув", POS), (tr, "контролер відкрив ключ", FIELD)]:
        parts.append(line(xt(f), zy - up - 14, xt(f), zy + dn + 14, color=col, sw=1.3, dash="5 5"))
    parts.append(text(xt(t0), zy - up - 22, "струм повернув", size=12, color=POS, bold=True))
    parts.append(text(xt(tr) + 8, zy - up - 22, "ключ відкрито", size=12, color=FIELD, bold=True, anchor="start"))

    # смуга часу реакції
    parts.append(arrow(xt(t0), zy + dn + 30, xt(tr), zy + dn + 30, color=INK, sw=2))
    parts.append(arrow(xt(tr), zy + dn + 30, xt(t0), zy + dn + 30, color=INK, sw=2))
    parts.append(text((xt(t0) + xt(tr)) / 2, zy + dn + 48, "t реакції", size=13, color=INK, bold=True))

    # підпис піку та хвоста
    parts.append(text(xt((t0 + tr) / 2), yrev + 22, "реверс крізь body-діод", size=12.5, color=POS, bold=True))
    parts.append(text(xt(0.80), zy - 12, "ключ відкрито, струм = 0", size=12, color=FIELD, bold=True))

    # плашка-висновок (верхній правий кут — там порожньо)
    parts.append(fitbox(xt(0.62) + 12, zy - up - 6, 300, 80,
                        "Заштрихована площа —\nзаряд, що проскочив назад\nза час реакції. Швидший\nконтролер — менша площа.",
                        size=12, fill="#f4f6f8", stroke=LINE, color=INK))

    return render(os.path.join(OUT, 'response-time.svg'), W, H, *parts,
                  title="Активний клапан не миттєвий: реверс тече, поки контролер спрацьовує")


# ── 4. Реле зворотного струму: дві котушки на одному якорі ───────────────────
def fig_cutout_mechanism():
    W, H = 1180, 660
    BLUE, AMBER = NEG, "#b8791f"
    parts = [line(W / 2, 54, W / 2, H - 92, color=MUTED, sw=1, dash="6 6")]

    def panel(pcx, closed):
        p = []
        tcol = FIELD if closed else POS
        p.append(text(pcx, 80,
                      "ЗАРЯД  →  контакти ЗАМКНЕНІ" if closed
                      else "РЕВЕРС  →  контакти РОЗІМКНЕНІ",
                      size=17, bold=True, color=tcol))
        # контекст: динамо ліворуч, батарея праворуч
        dyn = "Динамо\n13.5 В (крутиться)" if closed else "Динамо  ≈6 В\n(двигун заглух)"
        b, _, _ = textbox(pcx - 178, 140, dyn, size=12.5, pad=10, bold=True,
                          fill="#eafaf0" if closed else "#f4f6f8",
                          stroke=FIELD if closed else MUTED, color=INK)
        p.append(b)
        b, _, _ = textbox(pcx + 178, 140, "Батарея\n12.6 В", size=12.5, pad=10,
                          bold=True, fill="#fdf6ec", stroke=AMBER, color=INK)
        p.append(b)
        # електромагніт: осердя + дві котушки
        p.append(rect(pcx - 32, 388, 64, 150, fill="#eceff1", stroke=MUTED, sw=2, rx=4))
        p.append(text(pcx, 562, "осердя", size=11.5, color=MUTED))
        p.append(rect(pcx - 98, 402, 196, 30, fill="#eaf0fd", stroke=BLUE, sw=2.2, rx=9))
        p.append(text(pcx, 422, "котушка НАПРУГИ", size=12.5, bold=True, color=BLUE))
        p.append(rect(pcx - 98, 480, 196, 36, fill="#fdf1e0", stroke=AMBER, sw=2.2, rx=9))
        p.append(text(pcx, 494, "котушка СТРУМУ", size=12.5, bold=True, color=AMBER))
        # живлення (тонкі дроти): динамо → обидві котушки
        p.append(line(pcx - 178, 166, pcx - 178, 501, color=MUTED, sw=2))
        p.append(line(pcx - 178, 501, pcx - 98, 501, color=MUTED, sw=2))
        p.append(line(pcx - 178, 417, pcx - 98, 417, color=MUTED, sw=2))
        # СТРІЛКА струму крізь котушку струму — суть фігури
        if closed:
            p.append(arrow(pcx - 70, 501, pcx + 116, 501, color=FIELD, sw=4))
            p.append(text(pcx + 150, 505, "+I  заряд", size=12.5, bold=True,
                          color=FIELD, anchor="start"))
        else:
            p.append(arrow(pcx + 78, 501, pcx - 116, 501, color=POS, sw=4))
            p.append(text(pcx + 150, 505, "−I  реверс", size=12.5, bold=True,
                          color=POS, anchor="start"))
        # якір, вісь, контакти
        piv = (pcx - 150, 320)
        fe_y = 352 if closed else 300
        fe = (pcx + 150, fe_y)
        p.append(line(piv[0], piv[1], fe[0], fe[1], color=INK, sw=6))
        p.append(circle(piv[0], piv[1], 6, fill="#d9dde1", stroke=INK, sw=2))
        p.append(text(piv[0] - 12, piv[1] - 12, "вісь", size=11, color=MUTED, anchor="end"))
        p.append(text(pcx - 10, (piv[1] + fe_y) / 2 - 18, "якір", size=12.5,
                      bold=True, color=INK))
        mcx = pcx + 118
        t = (mcx - piv[0]) / (fe[0] - piv[0])
        mc_y = piv[1] + t * (fe[1] - piv[1])
        fc_y = 366
        p.append(line(mcx, fc_y + 4, mcx, 480, color=INK, sw=3))          # стійка нижнього контакту
        p.append(line(pcx + 178, 166, pcx + 178, 366, color=MUTED, sw=2))  # батарея вниз
        p.append(line(pcx + 178, 366, mcx, 366, color=MUTED, sw=2))
        p.append(circle(mcx, mc_y + 7, 5, fill=INK, stroke=INK))          # рухомий контакт
        p.append(circle(mcx, fc_y, 5, fill=INK, stroke=INK))              # нерухомий контакт
        if closed:
            p.append(line(mcx, mc_y + 7, mcx, fc_y, color=FIELD, sw=4))
            p.append(text(mcx + 14, (mc_y + fc_y) / 2 + 4, "замкнено",
                          size=12, bold=True, color=FIELD, anchor="start"))
        else:
            p.append(xmark(mcx, (mc_y + 7 + fc_y) / 2, r=11, color=POS, sw=3.2))
            p.append(text(mcx + 16, (mc_y + 7 + fc_y) / 2 + 4, "розрив",
                          size=12, bold=True, color=POS, anchor="start"))
        # пружина тягне якір угору
        p.append(zigzag(fe[0], 250, fe_y, n=7, amp=9,
                        color=FIELD if not closed else MUTED, sw=2.6))
        p.append(line(fe[0] - 12, 250, fe[0] + 12, 250, color=MUTED, sw=3))
        p.append(text(fe[0] + 16, 250, "пружина", size=12, bold=True,
                      color=FIELD if not closed else MUTED, anchor="start"))
        # підпис-висновок
        cap = ("Напруга динамо вища за батарею — котушка напруги притягує якір.\n"
               "Зарядний струм у котушці струму ДОДАЄ притягання: контакти держаться міцно."
               if closed else
               "Струм обернувся — у котушці струму він тепер ВІДНІМАЄ притягання.\n"
               "Утримання гасне, і пружина рвучко розмикає контакти: батарею від'єднано.")
        p.append(fitbox(pcx - 262, 586, 524, 58, cap, size=12.5,
                        fill="#eafaf0" if closed else "#fdecea",
                        stroke=FIELD if closed else POS, color=INK))
        return p

    parts += panel(300, True)
    parts += panel(880, False)
    return render(os.path.join(OUT, 'cutout-mechanism.svg'), W, H, *parts,
                  title="Реле зворотного струму: дві котушки на одному якорі вирішують за напрямом")


# ── 5. Естафета однобічного клапана: реле → діод → вбудований міст ───────────
def fig_lineage():
    W, H = 1360, 470
    parts = []
    parts.append(fitbox(W / 2 - 470, 34, 940, 54,
                        "Естафета однобічного клапана: та сама робота —\n"
                        "«пускати вперед, тримати назад» — переходить від пружини до кремнію.",
                        size=14, fill="#f4f6f8", stroke=LINE, color=INK, bold=True))
    ly = 252
    parts.append(arrow(80, ly, W - 60, ly, color=INK, sw=2.5))
    parts.append(text(W - 60, ly - 12, "час →", size=13, color=INK, anchor="end"))

    nodes = [
        (170, "1880-і–1910-і", "DC-станції",
         "Батарея «плаває» на шині поряд\nіз динамо. Реле зворотного\nструму від'єднує її, коли\nдинамо слабшає — щоб вона\nне крутила його мотором.", False),
        (430, "1912+", "Автомобіль",
         "Самопуск Кеттерінга → у\nкожному авто батарея й динамо.\nТе саме реле зворотного\nструму, тепер серійне.", False),
        (690, "1930-і+", "Три-блоковий регулятор",
         "Регулятор напруги, обмежувач\nструму й реле зворотного\nструму в одній коробці:\nLucas, Delco-Remy, Bosch.", False),
        (950, "~1960-і", "Кремнієвий діод",
         "Один блокувальний діод у\nрозрив дроту — та сама\nоднобічність, але без\nконтактів, що підгоряли\nй розладнувалися.", True),
        (1210, "1960+", "Генератор змінного струму",
         "Діодний міст-випрямляч\nпотрібен усе одно — і він\nблокує реверс вбудовано.\nОкреме реле зникає само.", True),
    ]
    for x, yr, name, desc, solid in nodes:
        col = FIELD if solid else NEG
        parts.append(circle(x, ly, 8, fill=col, stroke=INK, sw=2))
        parts.append(text(x, ly - 46, yr, size=14, bold=True, color=INK))
        parts.append(text(x, ly - 26, name, size=12.5, bold=True, color=col))
        parts.append(line(x, ly + 8, x, ly + 40, color=MUTED, sw=1.4, dash="4 4"))
        parts.append(fitbox(x - 116, ly + 44, 232, 116, desc, size=12,
                            fill="#eafaf0" if solid else "#eef1f6",
                            stroke=col if solid else MUTED, color=INK))
    return render(os.path.join(OUT, 'cutout-lineage.svg'), W, H, *parts,
                  title="Від електромеханічного реле до вбудованого діодного випрямляча")


# ── 6. Сенсор знаку струму: V_ds = I·R_ds(on), від'ємний поріг, затемнення ────
def fig_sense_threshold():
    W, H = 960, 560
    parts = []
    ox, oy = 430, 300
    sx, sy = 42, 9.5

    def X(i):
        return ox + i * sx

    def Y(v):
        return oy - v * sy

    parts.append(arrow(X(-6) - 18, oy, X(6) + 40, oy, color=INK, sw=2))
    parts.append(text(X(6) + 36, oy + 24, "струм I →", size=13, color=INK, anchor="end"))
    parts.append(arrow(ox, Y(-15) + 16, ox, Y(15) - 14, color=INK, sw=2))
    parts.append(text(ox + 10, Y(15) - 18, "V_ds", size=13, color=INK, anchor="start", bold=True))
    parts.append(text(X(3.6), oy + 24, "+ прямий (норма)", size=11.5, color=FIELD))
    parts.append(text(X(-3.7), oy + 24, "− реверс", size=11.5, color=POS))

    ip = -2.5
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
                 'stroke="none"/>' % (X(ip), Y(14), X(0) - X(ip), Y(-14) - Y(14)))
    parts.append(mtext(X(-1.25), Y(11.5), ["терпимий", "реверс", "(ключ ON)"],
                       size=11.5, color=POS, bold=True))

    parts.append(line(X(-6), Y(2 * -6), X(6), Y(2 * 6), color=NEG, sw=3.6))
    parts.append(text(X(-3.3), Y(2 * -3.3) + 20, "V_ds = I · R_ds(on)", size=13, color=NEG, bold=True))

    parts.append(line(X(-4.6), Y(-5), X(0.3), Y(-5), color=POS, sw=1.6, dash="6 5"))
    parts.append(text(X(-4.8), Y(-5) + 4, "поріг V_th = −5 мВ", size=11.5, color=POS, anchor="end"))
    parts.append(line(X(ip), Y(-5), X(ip), oy, color=POS, sw=1.6, dash="6 5"))
    parts.append(circle(X(ip), Y(-5), 4.6, fill=POS, stroke=POS))
    parts.append(text(X(ip), oy + 65, "I_поріг = −2.5 А", size=12, color=POS, bold=True))

    parts.append(arrow(X(5.2), Y(10.4), X(6.1), Y(12.2), color=FIELD, sw=3))
    parts.append(fitbox(X(2.9), Y(15) - 6, 250, 60,
                        "далі — прямий струм:\n+20 А → +40 мВ\n(за межами кадру)",
                        size=11.5, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))
    parts.append(fitbox(694, oy - 26, 250, 68,
                        "V_ds перетнув поріг ↓\n⇒ контролер\nрозмикає ключ",
                        size=12, fill="#fff7f6", stroke=POS, color=POS, bold=True))
    parts.append(fitbox(100, H - 80, W - 200, 56,
                        "Затемнення (blanking): рішення компаратора ігнорують t_затемн після кожного фронту напруги —\n"
                        "щоб дзвін V_ds не вимкнув живу рейку хибним «реверсом».",
                        size=12, fill="#f4f6f8", stroke=LINE, color=INK, bold=True))

    return render(os.path.join(OUT, 'sense-threshold.svg'), W, H, *parts,
                  title="Як контролер читає знак струму: V_ds на відкритому ключі й від'ємний поріг")


# ── 7. Зворотне відновлення діода: трикутник струму й заряд Q_rr ──────────────
def fig_qrr():
    W, H = 940, 520
    parts = []
    ox, aw = 150, 640
    zy = 250

    def XT(f):
        return ox + aw * f

    yF = zy - 66
    yPk = zy + 120
    y25 = zy + 30
    fFlat, fZero, fPk, f25, fEnd = 0.16, 0.288, 0.52, 0.66, 0.82

    parts.append(arrow(ox - 10, zy, ox + aw + 30, zy, color=INK, sw=2))
    parts.append(text(ox + aw + 26, zy - 10, "час →", size=13, color=INK, anchor="end"))
    parts.append(arrow(ox, zy + 150, ox, zy - 122, color=INK, sw=2))
    parts.append(text(ox + 8, zy - 118, "струм", size=13, color=INK, anchor="start", bold=True))
    parts.append(text(ox - 12, yF + 4, "+ прямий", size=11, color=FIELD, anchor="end"))
    parts.append(text(ox - 12, yPk + 4, "− реверс", size=11, color=POS, anchor="end"))
    parts.append(text(ox - 12, zy - 4, "0", size=12, color=MUTED, anchor="end"))

    parts.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f z" '
                 'fill="#fdecea" stroke="none"/>'
                 % (XT(fZero), zy, XT(fPk), yPk, XT(f25), y25, XT(fEnd), zy))
    parts.append(text(XT(0.47), zy + 66, "Q_rr", size=18, color=POS, bold=True))
    parts.append(text(XT(0.47), zy + 86, "винесений заряд", size=11, color=POS))

    parts.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Q%.1f %.1f %.1f %.1f '
                 'Q%.1f %.1f %.1f %.1f L%.1f %.1f" fill="none" stroke="%s" stroke-width="3.6"/>'
                 % (XT(0.04), yF, XT(fFlat), yF,
                    XT(fPk), yPk,
                    XT(0.58), yPk + 4, XT(f25), y25,
                    XT(0.74), zy + 4, XT(fEnd), zy,
                    XT(0.95), zy, POS))

    parts.append(text(XT(0.085), yF - 12, "I_F  (прямий струм)", size=12, color=FIELD, bold=True, anchor="start"))
    parts.append(text(XT(0.20), zy - 46, "нахил = di/dt", size=12, color=MUTED, bold=True))
    parts.append(mtext(XT(fPk), zy - 40, ["−I_RRM", "(пік реверсу)"], size=12, color=POS, bold=True))

    for f in (fZero, fPk, f25, fEnd):
        parts.append(line(XT(f), zy, XT(f), zy + 140, color=MUTED, sw=1, dash="4 5"))

    yb = zy + 142
    parts.append(arrow(XT(fZero), yb, XT(fPk), yb, color=INK, sw=1.8))
    parts.append(arrow(XT(fPk), yb, XT(fZero), yb, color=INK, sw=1.8))
    parts.append(text((XT(fZero) + XT(fPk)) / 2, yb - 6, "ta", size=12, color=INK, bold=True))
    parts.append(arrow(XT(fPk), yb, XT(f25), yb, color=INK, sw=1.8))
    parts.append(arrow(XT(f25), yb, XT(fPk), yb, color=INK, sw=1.8))
    parts.append(text((XT(fPk) + XT(f25)) / 2, yb - 6, "tb", size=12, color=INK, bold=True))
    yb2 = zy + 170
    parts.append(arrow(XT(fZero), yb2, XT(fEnd), yb2, color=MUTED, sw=1.6))
    parts.append(arrow(XT(fEnd), yb2, XT(fZero), yb2, color=MUTED, sw=1.6))
    parts.append(text((XT(fZero) + XT(fEnd)) / 2, yb2 - 6, "t_rr = ta + tb", size=12, color=MUTED, bold=True))

    parts.append(fitbox(XT(0.615), zy - 120, 300, 76,
                        "I_RRM = √(2 · Q_rr · di/dt)\nкрутіший di/dt ⇒ вищий пік\nШотткі: Q_rr ≈ 0",
                        size=12.5, fill="#f4f6f8", stroke=LINE, color=INK, bold=True))

    return render(os.path.join(OUT, 'qrr-recovery.svg'), W, H, *parts,
                  title="Зворотне відновлення: власний імпульс реверсу діода при перемиканні")


# ── 8. Що проскакує ↔ час реакції: заряд крізь діод у подвійному логарифмі ────
def fig_through_vs_time():
    import math
    W, H = 940, 540
    parts = []
    L, Rr = 180, 772
    T, B = 95, 402
    xlo, xhi = -7, -3
    ylo, yhi = -6, -1

    def PX(lt):
        return L + (lt - xlo) / (xhi - xlo) * (Rr - L)

    def PY(lq):
        return B - (lq - ylo) / (yhi - ylo) * (B - T)

    def logQ(lt, ipk):
        return math.log10(ipk) + lt

    xlabels = {-7: "100 нс", -6: "1 мкс", -5: "10 мкс", -4: "100 мкс", -3: "1 мс"}
    for d in range(xlo, xhi + 1):
        parts.append(line(PX(d), T, PX(d), B, color="#e5e7eb", sw=1))
        parts.append(text(PX(d), B + 22, xlabels[d], size=11.5, color=MUTED))
    ylabels = {-6: "1 мкКл", -5: "10 мкКл", -4: "100 мкКл", -3: "1 мКл", -2: "10 мКл", -1: "100 мКл"}
    for d in range(ylo, yhi + 1):
        parts.append(line(L, PY(d), Rr, PY(d), color="#e5e7eb", sw=1))
        parts.append(text(L - 12, PY(d) + 4, ylabels[d], size=11.5, color=MUTED, anchor="end"))

    parts.append(rect(L, T, Rr - L, B - T, fill="none", stroke=INK, sw=1.6))
    parts.append(text((L + Rr) / 2, B + 46, "час реакції  t_реакції", size=13, color=INK, bold=True))
    parts.append(mtext(52, (T + B) / 2 - 18, ["заряд", "крізь", "діод"], size=12.5, color=INK, bold=True))

    parts.append(line(L, PY(-2), Rr, PY(-2), color=FIELD, sw=2, dash="7 5"))
    parts.append(text(Rr - 6, PY(-2) - 8, "орієнтовна межа body-діода", size=11, color=FIELD, anchor="end", bold=True))

    parts.append(line(PX(xlo), PY(logQ(xlo, 20)), PX(xhi), PY(logQ(xhi, 20)), color=POS, sw=3.6))
    parts.append(mtext(560, 170, ["Q = I_пік · t", "(I_пік = 20 А)"], size=12.5, color=POS, bold=True))

    lt_a = math.log10(0.5e-6)
    xa, ya = PX(lt_a), PY(logQ(lt_a, 20))
    lt_f = math.log10(1e-4)
    xf, yf = PX(lt_f), PY(logQ(lt_f, 20))

    parts.append(arrow(xa + 8, ya + 8, xf - 8, yf - 8, color=MUTED, sw=1.6))
    parts.append(text((xa + xf) / 2 + 44, (ya + yf) / 2 + 6, "× 200", size=14, color=MUTED, bold=True))

    parts.append(circle(xa, ya, 6, fill=POS, stroke=INK, sw=1.6))
    parts.append(fitbox(185, 215, 140, 62,
                        "аналоговий контролер\nt ≈ 0.5 мкс\n→ Q = 10 мкКл\nE = 5 мкДж",
                        size=11, fill="#fff7f6", stroke=POS, color=POS, bold=True))
    parts.append(circle(xf, yf, 6, fill=POS, stroke=INK, sw=1.6))
    parts.append(fitbox(xf - 42, yf + 16, 214, 58,
                        "прошивковий наглядач\nt ≈ 100 мкс → Q = 2 мКл\nE = 1 мДж",
                        size=11, fill="#f4f6f8", stroke=LINE, color=INK, bold=True))

    return render(os.path.join(OUT, 'through-vs-time.svg'), W, H, *parts,
                  title="Швидший клапан — менше заряду й енергії крізь діод")


# -- 6. Signal chain of the software supervisor (proj insert) -----------------
def fig_supervisor_chain():
    W, H = 1240, 615
    P = []
    yP, yS, yC = 150, 355, 515

    src, ws, hs = textbox(110, yP, "Джерело", size=14, pad=12, bold=True,
                          fill="#eafaf0", stroke=FIELD, color=FIELD)
    rs, wr, hr = textbox(340, yP, "шунт Rs\n10 мОм", size=13, pad=11, bold=True,
                         fill=FILL, stroke=MUTED, color=INK)
    swb, ww, hw = textbox(700, yP, "MOSFET-ключ\n+ body-діод", size=14, pad=12, bold=True,
                          fill="#eaf0fd", stroke=NEG, color=NEG)
    ld, wl, hl = textbox(1030, yP, "Навантаження", size=14, pad=12, bold=True,
                         fill=FILL, stroke=MUTED, color=INK)
    P.append(line(110 + ws / 2, yP, 340 - wr / 2, yP, color=LINE, sw=2.6))
    P.append(line(340 + wr / 2, yP, 700 - ww / 2, yP, color=LINE, sw=2.6))
    P.append(line(700 + ww / 2, yP, 1030 - wl / 2, yP, color=LINE, sw=2.6))
    P += [src, rs, swb, ld]

    P.append(line(1030, yP - hl / 2, 1030, 78, color=POS, sw=1.4, dash="5 5"))
    P.append(arrow(1030, 78, 150, 78, color=POS, sw=4))
    P.append(line(150, 78, 110, yP - hs / 2, color=POS, sw=1.4, dash="5 5"))
    P.append(text(590, 58,
                  "зворотний струм тече крізь ще замкнений канал, поки прошивка вирішує",
                  size=13, color=POS, bold=True))

    ina, wi, hi = textbox(340, yS, "двобічний підсилювач\nзсув нуля 1.65 В",
                          size=13, pad=11, bold=True, fill="#fff7f6", stroke=POS, color=INK)
    adc, wa, ha = textbox(600, yS, "АЦП\n12-біт", size=13, pad=12, bold=True,
                          fill=FILL, stroke=MUTED, color=INK)
    P.append(arrow(340, yP + hr / 2, 340, yS - hi / 2, color=LINE, sw=2.4))
    P.append(text(360, (yP + yS) / 2 - 6, "напруга", size=11, color=MUTED, anchor="start"))
    P.append(text(360, (yP + yS) / 2 + 10, "на шунті", size=11, color=MUTED, anchor="start"))
    P.append(arrow(340 + wi / 2, yS, 600 - wa / 2, yS, color=LINE, sw=2.4))
    P += [ina, adc]

    mcu, wm, hm = textbox(470, yC, "МК-наглядач\nмА → антидрижання → автомат",
                          size=13, pad=12, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG)
    drv, wd, hd = textbox(770, yC, "драйвер\nзатвора", size=13, pad=12, bold=True,
                          fill=FILL, stroke=MUTED, color=INK)
    flt, wf, hf = textbox(150, yC, "прапорець\n→ система", size=13, pad=12, bold=True,
                          fill="#eafaf0", stroke=FIELD, color=FIELD)
    P.append(arrow(600, yS + ha / 2, 470 + wm / 4, yC - hm / 2, color=LINE, sw=2.4))
    P.append(arrow(470 + wm / 2, yC, 770 - wd / 2, yC, color=LINE, sw=2.4))
    P.append(arrow(770, yC - hd / 2, 735, yP + hw / 2 + 4, color=NEG, sw=2.4))
    P.append(text(800, (yP + yC) / 2 - 6, "керування", size=11, color=NEG, anchor="start"))
    P.append(text(800, (yP + yC) / 2 + 10, "затвором", size=11, color=NEG, anchor="start"))
    P.append(arrow(470 - wm / 2, yC, 150 + wf / 2, yC, color=FIELD, sw=2.4))
    P += [mcu, drv, flt]

    return render(os.path.join(OUT, 'supervisor-chain.svg'), W, H, *P,
                  title="Сигнальний ланцюг програмного наглядача зворотного струму")


# -- 7. Discrete sampling and trip latency (proj insert) ----------------------
def fig_sampled_timing():
    W, H = 1020, 560
    P = []
    ox, aw = 118, 812
    zy = 250
    up, dn = 150, 175
    n = 14
    step = aw / n

    def xs(i):
        return ox + (i + 0.5) * step

    P.append(line(ox, zy - up - 22, ox, zy + dn + 20, color=INK, sw=2))
    P.append(arrow(ox, zy, ox + aw + 12, zy, color=INK, sw=2))
    P.append(text(ox + aw + 8, zy - 12, "час →", size=13, color=INK, anchor="end"))
    P.append(text(ox - 10, zy - up - 8, "струм", size=13, color=INK, anchor="end"))
    P.append(text(ox - 10, zy - up + 16, "+ вперед", size=11, color=FIELD, anchor="end"))
    P.append(text(ox - 10, zy + dn + 2, "− назад", size=11, color=POS, anchor="end"))

    yFwd = zy - up * 0.55
    yRev = zy + dn * 0.72
    yTrip = zy + dn * 0.38
    i_drop, i_trip = 6, 8
    x_drop = xs(i_drop) - step * 0.45

    P.append(line(ox, yTrip, ox + aw, yTrip, color=POS, sw=1.6, dash="7 5"))
    P.append(text(ox + aw, yTrip - 9, "−I_trip (поріг реверсу)", size=12, color=POS,
                  anchor="end", bold=True))

    for i in range(n):
        P.append(line(xs(i), zy - up, xs(i), zy + dn, color="#e2e6ea", sw=1))

    P.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
             'stroke="none"/>' % (x_drop, zy, xs(i_trip) - x_drop, yRev - zy))

    P.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f L%.1f %.1f" '
             'fill="none" stroke="%s" stroke-width="3.4"/>'
             % (ox, yFwd, x_drop, yFwd, x_drop, yRev, xs(i_trip), yRev,
                xs(i_trip), zy, ox + aw, zy, INK))

    for i in range(n):
        if i < i_drop:
            P.append(circle(xs(i), yFwd, 5, fill=FIELD, stroke=FIELD))
        elif i <= i_trip:
            P.append(circle(xs(i), yRev, 6.5, fill=POS, stroke=POS))
        else:
            P.append(circle(xs(i), zy, 5, fill=MUTED, stroke=MUTED))

    for k, i in enumerate([i_drop, i_drop + 1, i_trip]):
        P.append(text(xs(i), yRev + 28, str(k + 1), size=15, color=POS, bold=True))
    P.append(text(xs(i_trip) + 12, yRev + 50, "→ ключ розімкнено", size=12, color=POS,
                  bold=True, anchor="start"))

    P.append(text(xs(2), yFwd - 16, "прямий струм", size=12.5, color=FIELD, bold=True))
    P.append(text((x_drop + xs(i_trip)) / 2, yRev - 18, "реверс крізь відкритий канал",
                  size=12, color=POS, bold=True))
    P.append(text((x_drop + xs(i_trip)) / 2, zy + 22, "заряд, що проскочив",
                  size=11.5, color=POS))
    P.append(text(xs(11), zy - 12, "ключ відкрито, струм ≈ 0", size=12, color=MUTED, bold=True))

    ybr = zy + dn + 40
    P.append(arrow(x_drop, ybr, xs(i_trip), ybr, color=INK, sw=2))
    P.append(arrow(xs(i_trip), ybr, x_drop, ybr, color=INK, sw=2))
    P.append(text((x_drop + xs(i_trip)) / 2, ybr + 20,
                  "затримка = N вибірок × T + оброблення", size=12.5, color=INK, bold=True))

    yT = yFwd - 42
    P.append(arrow(xs(0), yT, xs(1), yT, color=MUTED, sw=1.6))
    P.append(arrow(xs(1), yT, xs(0), yT, color=MUTED, sw=1.6))
    P.append(text((xs(0) + xs(1)) / 2, yT - 8, "T = 100 мкс", size=11.5, color=MUTED))

    P.append(fitbox(xs(9) - 6, zy - up - 20, 330, 92,
                    "Аналоговий рефлекс\nрозірвав би коло за ~1 мкс —\n"
                    "ще до другої крапки.\nНаглядач чекає три вибірки.",
                    size=12, fill="#f4f6f8", stroke=LINE, color=INK))

    return render(os.path.join(OUT, 'sampled-timing.svg'), W, H, *P,
                  title="Наглядач бачить струм лише у вибірках — і чекає N поспіль")


if __name__ == '__main__':
    fig_where()
    fig_body_diode_trap()
    fig_response()
    fig_cutout_mechanism()
    fig_lineage()
    fig_sense_threshold()
    fig_qrr()
    fig_through_vs_time()
    fig_supervisor_chain()
    fig_sampled_timing()
    print("OK: 10 figures ->", OUT)
