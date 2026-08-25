# -*- coding: utf-8 -*-
"""Фігури до теми «Коефіцієнт придушення синфазного сигналу (CMRR)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

WIRE = "#cf8b5e"   # тепла мідь для дротів


# ── 1. Розклад входу: спільне + різниця → два підсилення ────────────────────
def fig_decompose():
    W, H = 760, 430
    f = [text(W / 2, 30, "Будь-який вхід = спільне + різниця", size=17, bold=True),
         text(W / 2, 52, "підсилювач множить кожну складову на свій коефіцієнт; CMRR = Aд / Aс",
              size=12, color=MUTED, italic=True)]

    # дві осі входів зліва: V+ і V−, що сидять на спільному рівні
    bx = 70
    base_y = 200            # рівень нуля для осей
    amp = 26                # розмах
    # вісь
    f.append(line(bx, base_y - 90, bx, base_y + 90, color=INK, sw=1.6))
    f.append(text(bx - 8, base_y - 96, "V", size=12, color=INK, anchor="end", bold=True))
    # спільний п'єдестал (синфазне) — пунктир
    cm = 40
    f.append(line(bx, base_y - cm, bx + 150, base_y - cm, color=MUTED, sw=1.4, dash="5 4"))
    f.append(text(bx + 156, base_y - cm + 4, "Vс (спільне)", size=11, color=MUTED, anchor="start"))
    # дві точки входів навколо п'єдесталу
    vp = base_y - cm - amp / 2
    vm = base_y - cm + amp / 2
    f.append(circle(bx, vp, 5, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(bx - 8, vp - 6, "V₊", size=12, color=POS, anchor="end", bold=True))
    f.append(circle(bx, vm, 5, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(text(bx - 8, vm + 14, "V₋", size=12, color=NEG, anchor="end", bold=True))
    # дужка різниці
    f.append(line(bx + 18, vp, bx + 18, vm, color=FIELD, sw=2.2))
    f.append(text(bx + 24, base_y - cm + 4, "Vд", size=11, color=FIELD, anchor="start", bold=True))

    # стрілка вправо до блоку-підсилювача
    amp_x = 300
    f.append(arrow(bx + 110, base_y, amp_x - 6, base_y, color=LINE, sw=1.8))

    # блок «диференційний підсилювач»
    bw, bh = 150, 120
    f.append(rect(amp_x, base_y - bh / 2, bw, bh, fill="#eaf6ee", stroke=FIELD, sw=2))
    f.append(mtext(amp_x + bw / 2, base_y - 22,
                   ["диференційний", "підсилювач"], size=13, color=INK, bold=True, lh=1.3))
    f.append(text(amp_x + bw / 2, base_y + 14, "Aд  · Vд", size=12, color=FIELD, bold=True))
    f.append(text(amp_x + bw / 2, base_y + 36, "Aс  · Vс", size=12, color=POS, bold=True))

    # дві стрілки на виході: велика від різниці, тонесенька-просочена від спільного
    ox = amp_x + bw
    f.append(arrow(ox, base_y - 22, ox + 120, base_y - 22, color=FIELD, sw=3.2))
    f.append(text(ox + 126, base_y - 18, "корисне", size=12, color=FIELD, anchor="start", bold=True))
    f.append(arrow(ox, base_y + 22, ox + 120, base_y + 22, color=POS, sw=1.0))
    f.append(text(ox + 126, base_y + 26, "просочена завада", size=11, color=POS, anchor="start"))

    # формула внизу у рамці
    f.append(fitbox(W / 2 - 250, 360, 500, 50,
                    "вихід = Aд·Vд + Aс·Vс      — мрія: Aс → 0, тобто CMRR → ∞",
                    size=14, fill=FILL, bold=True))
    render(os.path.join(IMG, "decompose.svg"), W, H, *f)


# ── 2. Що CMRR робить із завадою: зведення до входу + драбина дБ ─────────────
def fig_ladder():
    W, H = 800, 430
    f = [text(W / 2, 30, "Як читати число: завада, зведена до входу", size=17, bold=True),
         text(W / 2, 52, "синфазна завада ділиться на CMRR — і стає крихітною похибкою на вході",
              size=12, color=MUTED, italic=True)]

    # ліворуч — ланцюжок «1 В завади ÷ CMRR = помилка»
    cx = 210
    f.append(fitbox(cx - 150, 95, 300, 46, "синфазна завада  Vс = 1 В", size=13,
                    fill="#fdecea", stroke=POS, bold=True))
    f.append(arrow(cx, 145, cx, 178, color=LINE, sw=1.8))
    f.append(text(cx + 10, 168, "÷ CMRR", size=12, color=INK, anchor="start", bold=True))
    f.append(fitbox(cx - 150, 180, 300, 46,
                    "видно на вході як  Vс / CMRR", size=13, fill="#eaf6ee", stroke=FIELD, bold=True))
    # три приклади-результати
    rows = [("CMRR = 60 дБ (×1 000)", "= 1 мВ  — псує сигнал", POS),
            ("CMRR = 100 дБ (×100 000)", "= 10 мкВ  — майже невидно", FIELD),
            ("CMRR = 120 дБ (×1 000 000)", "= 1 мкВ  — чисто", FIELD)]
    ry = 252
    for lab, val, col in rows:
        f.append(text(cx - 150, ry, lab, size=12, color=MUTED, anchor="start"))
        f.append(text(cx - 150, ry + 18, val, size=12, color=col, anchor="start", bold=True))
        ry += 50

    # праворуч — драбина дБ ↔ разів
    L = 470
    f.append(line(L, 100, L, 400, color=INK, sw=1.8))
    f.append(text(L, 90, "дБ ↔ у скільки разів", size=12, bold=True, anchor="start"))
    ladder = [(60, "1 000"), (80, "10 000"), (100, "100 000"), (120, "1 000 000")]
    y0, y1 = 380, 130
    db0, db1 = 60, 120
    for db, mult in ladder:
        y = y0 + (db - db0) / (db1 - db0) * (y1 - y0)
        f.append(line(L - 6, y, L + 6, y, color=INK, sw=1.6))
        f.append(text(L - 12, y + 4, "%d дБ" % db, size=12, color=INK, anchor="end", bold=True))
        f.append(text(L + 14, y + 4, "× %s" % mult, size=12, color=FIELD, anchor="start", bold=True))
    # стрілочка «+20 дБ = ×10»
    ya = y0 + (60 - db0) / (db1 - db0) * (y1 - y0)
    yb = y0 + (80 - db0) / (db1 - db0) * (y1 - y0)
    f.append(line(L + 200, ya, L + 200, yb, color=NEG, sw=1.6))
    f.append(line(L + 195, ya, L + 205, ya, color=NEG, sw=1.6))
    f.append(line(L + 195, yb, L + 205, yb, color=NEG, sw=1.6))
    f.append(mtext(L + 212, (ya + yb) / 2 - 6, ["+20 дБ", "= ×10"], size=11,
                   color=NEG, anchor="start", bold=True, lh=1.25))
    render(os.path.join(IMG, "ladder.svg"), W, H, *f)


# ── 3. CMRR не сталий: спадає з частотою ────────────────────────────────────
def fig_vs_freq():
    W, H = 780, 430
    f = [text(W / 2, 30, "CMRR не одне число, а крива від частоти", size=17, bold=True),
         text(W / 2, 52, "найвищий на постійному струмі, спадає з частотою завади — дивись на потрібній частоті",
              size=12, color=MUTED, italic=True)]

    L, R, T, B = 90, 700, 100, 360
    # осі
    f.append(line(L, T, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text(L - 8, T - 10, "CMRR, дБ", size=12, bold=True, anchor="middle"))
    f.append(text(R, B + 26, "частота (лог)", size=12, bold=True, anchor="end"))

    # рівні дБ по вертикалі: 120..40
    db_top, db_bot = 130.0, 30.0
    def yv(db):
        return T + (db_top - db) / (db_top - db_bot) * (B - T)
    for db in (120, 100, 80, 60, 40):
        y = yv(db)
        f.append(line(L - 5, y, L, y, color=INK, sw=1.4))
        f.append(text(L - 10, y + 4, "%d" % db, size=11, color=MUTED, anchor="end"))
        f.append(line(L, y, R, y, color="#e7e9ec", sw=1.0))

    # декади по горизонталі: DC, 10, 100, 1k, 10k, 100k
    decs = ["DC", "10", "100", "1k", "10k", "100k"]
    n = len(decs)
    def xv(i):
        return L + i / (n - 1) * (R - L)
    for i, lab in enumerate(decs):
        x = xv(i)
        f.append(line(x, B, x, B + 5, color=INK, sw=1.4))
        f.append(text(x, B + 22, lab, size=11, color=MUTED))

    # крива CMRR: полиця ~120 дБ до ~10 Гц, далі спад ~−20 дБ/декаду
    pts = []
    for i in range(0, 5 * (n - 1) + 1):
        ii = i / 5.0                      # позиція в декадах 0..(n-1)
        # рівна полиця до декади 1 (10 Гц), далі лінійний спад у дБ
        db = 120.0 if ii <= 1.0 else 120.0 - 20.0 * (ii - 1.0)
        pts.append((xv(ii), yv(db)))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, FIELD))

    # вертикаль мережевих 50 Гц і значення на кривій там
    # 50 Гц ≈ між декадами 1 (10) і 2 (100): log10(50)=1.699 → позиція 1.699
    x50 = xv(1.699)
    db50 = 120.0 - 20.0 * (1.699 - 1.0)   # ≈ 106 дБ
    f.append(line(x50, T, x50, B, color=POS, sw=1.6, dash="6 4"))
    f.append(circle(x50, yv(db50), 5, fill=POS, stroke=POS))
    f.append(text(x50 + 8, T + 16, "мережа 50 Гц", size=11, color=POS, anchor="start", bold=True))
    f.append(text(x50 + 8, yv(db50) - 8, "≈ %d дБ тут" % round(db50), size=11,
                  color=POS, anchor="start", bold=True))

    # підпис «полиця на DC»
    f.append(text(xv(0.4), yv(120) - 10, "120 дБ на DC", size=11, color=FIELD, anchor="middle", bold=True))
    # підпис нахилу
    f.append(text(xv(3.4), yv(120 - 20 * 2.4) - 12, "− 20 дБ / декаду", size=11,
                  color=FIELD, anchor="middle", bold=True))

    render(os.path.join(IMG, "vs-freq.svg"), W, H, *f)


# ── 4. Чому «довгий хвіст»: короткий резистор vs джерело струму ──────────────
def _valve(f, cx, cy):
    """Спрощений символ лампи-тріода: коло, всередині анод/сітка/катод-риски."""
    f.append(circle(cx, cy, 24, fill="#ffffff", stroke=INK, sw=1.8))
    # анод (пластинка вгорі)
    f.append(line(cx - 10, cy - 11, cx + 10, cy - 11, color=INK, sw=2.4))
    # сітка (пунктир посередині)
    f.append(line(cx - 11, cy, cx + 11, cy, color=MUTED, sw=1.6, dash="3 3"))
    # катод (галочка внизу)
    f.append(line(cx - 8, cy + 12, cx, cy + 6, color=POS, sw=2.2))
    f.append(line(cx, cy + 6, cx + 8, cy + 12, color=POS, sw=2.2))


def _ltp(f, ox, oy, long_tail):
    """Малює одну пару з двома лампами зі спільним катодним хвостом у точці (ox,oy=верх)."""
    lx, rx = ox + 40, ox + 150      # центри двох ламп по X
    vy = oy + 70                    # центр ламп по Y
    rail_top = oy + 6               # верхня шина (анодне живлення)
    knot = oy + 150                 # вузол з'єднання катодів
    tail_bot = oy + 250             # низ хвоста (−)

    # верхня шина живлення й анодні резистори
    f.append(line(lx - 30, rail_top, rx + 30, rail_top, color=INK, sw=2))
    f.append(text(rx + 36, rail_top + 4, "+V", size=11, color=INK, anchor="start", bold=True))
    for x in (lx, rx):
        f.append(line(x, rail_top, x, vy - 24, color=LINE, sw=1.6))
        f.append(rect(x - 6, rail_top + 14, 12, 26, fill="#fff7ec", stroke=WIRE, sw=1.4, rx=3))

    # лампи
    _valve(f, lx, vy)
    _valve(f, rx, vy)
    # виходи від анодів убік
    f.append(text(lx - 30, vy - 26, "вих", size=10, color=FIELD, anchor="middle", bold=True))
    f.append(text(rx + 30, vy - 26, "вих", size=10, color=FIELD, anchor="middle", bold=True))

    # входи (сітки) ліворуч/праворуч зі стрілками «спільний підйом»
    f.append(line(lx - 24, vy, lx - 50, vy, color=NEG, sw=1.6))
    f.append(line(rx + 24, vy, rx + 50, vy, color=NEG, sw=1.6))
    f.append(text(lx - 54, vy + 4, "вх", size=10, color=NEG, anchor="end", bold=True))
    f.append(text(rx + 54, vy + 4, "вх", size=10, color=NEG, anchor="start", bold=True))

    # катоди вниз до спільного вузла
    f.append(line(lx, vy + 12, lx, knot, color=POS, sw=1.8))
    f.append(line(rx, vy + 12, rx, knot, color=POS, sw=1.8))
    f.append(line(lx, knot, rx, knot, color=POS, sw=1.8))
    midx = (lx + rx) / 2
    f.append(circle(midx, knot, 3.2, fill=POS, stroke=POS))

    # хвіст донизу
    f.append(line(midx, knot, midx, tail_bot - (40 if long_tail else 0), color=POS, sw=1.8))

    if long_tail:
        # джерело струму: коло з двома стрілками (символ)
        scy = tail_bot - 22
        f.append(circle(midx, scy, 18, fill="#eaf6ee", stroke=FIELD, sw=2))
        f.append(arrow(midx, scy + 9, midx, scy - 9, color=FIELD, sw=2))
        f.append(line(midx, tail_bot - 4, midx, tail_bot + 14, color=POS, sw=1.8))
        f.append(text(midx + 24, scy + 4, "джерело", size=10, color=FIELD, anchor="start", bold=True))
        f.append(text(midx + 24, scy + 17, "струму", size=10, color=FIELD, anchor="start", bold=True))
        f.append(text(midx, tail_bot + 30, "Iхв = const", size=11, color=FIELD, bold=True))
    else:
        # звичайний резистор
        f.append(rect(midx - 7, tail_bot - 60, 14, 40, fill="#fff7ec", stroke=WIRE, sw=1.5, rx=3))
        f.append(text(midx + 22, tail_bot - 40, "Rмал", size=11, color=WIRE, anchor="start", bold=True))
        f.append(line(midx, tail_bot - 20, midx, tail_bot + 14, color=POS, sw=1.8))

    # шина «−» внизу
    f.append(line(midx - 26, tail_bot + 14, midx + 26, tail_bot + 14, color=INK, sw=2))
    f.append(text(midx + 32, tail_bot + 18, "−", size=12, color=INK, anchor="start", bold=True))

    # стрілки спільного підйому входів (обидва вгору однаково)
    for x in (lx - 50, rx + 50):
        f.append(arrow(x, vy + 26, x, vy + 6, color=NEG, sw=1.6))
    f.append(text(midx, vy + 40, "обидва входи ↑ разом (спільне)", size=10,
                  color=NEG, anchor="middle"))

    return midx, knot


def fig_ltp_tail():
    W, H = 820, 470
    f = [text(W / 2, 28, "Чому хвіст хочуть «довгим»", size=17, bold=True),
         text(W / 2, 50, "той самий спільний підйом обох входів: короткий хвіст пропускає заваду, довгий — застигає",
              size=12, color=MUTED, italic=True)]

    # ліва пара — короткий резистор
    mxL, _ = _ltp(f, 60, 80, long_tail=False)
    f.append(fitbox(40, 360, 320, 84,
                    "короткий хвіст: спільний струм ВІЛЬНО росте →\nвихід сіпається → спільне просочилось",
                    size=13, fill="#fdecea", stroke=POS, bold=True))

    # права пара — джерело струму
    mxR, _ = _ltp(f, 460, 80, long_tail=True)
    f.append(fitbox(460, 360, 320, 84,
                    "довгий хвіст (джерело струму): Iхв сталий →\nспільному нікуди дітися → скоротилось",
                    size=13, fill="#eaf6ee", stroke=FIELD, bold=True))

    # роздільник по центру
    f.append(line(W / 2, 90, W / 2, 345, color="#dfe2e6", sw=1.4, dash="4 5"))
    render(os.path.join(IMG, "ltp-tail.svg"), W, H, *f)


if __name__ == "__main__":
    fig_decompose()
    fig_ladder()
    fig_vs_freq()
    fig_ltp_tail()
    print("OK: figures written to", IMG)
