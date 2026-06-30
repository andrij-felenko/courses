# -*- coding: utf-8 -*-
"""Фігури до теми «Guard ring і захист від витоків» (аналогова електроніка, кутом теорії кіл).
Чотири фігури:
  leakage-divider.svg — витік як паразитний резистор від сусіднього вузла до високоомного входу:
                        дільник напруги з мізерним джерелом топить корисний сигнал
  guard-nulls-v.svg   — кільце на тому самому потенціалі: напруга на опорі витоку ≈ 0 → струм ≈ 0
  guard-ring-layout.svg— кільце оточує доріжку входу; струм витоку тепер тече з кільця, не з входу
  guard-noninv-inv.svg— куди вести кільце: неінвертувальний (від виходу-буфера) та інвертувальний (на землю)
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def leakage_divider():
    """Витік = резистор від «брудного» вузла до високоомного входу. Разом із Rджерела — дільник."""
    W, H = 720, 360
    p = []
    # ── зліва: схема дільника ──
    # високоомне джерело сигналу зверху
    nx = 250          # вузол входу
    ny = 165
    topy = 70
    p.append(text(120, topy - 6, "джерело сигналу", size=12, color=MUTED))
    p.append(line(120, topy + 8, 120, ny, color=INK, sw=2))
    # Rджерела (величезний) — зиґзаґ вертикально
    p.append(rect(108, topy + 18, 24, 70, fill=BG, stroke=INK, sw=1.6, rx=3))
    p.append(text(150, topy + 40, "Rджерела", size=12, bold=True, anchor="start"))
    p.append(text(150, topy + 56, "= 100 ГОм", size=12, color=NEG, anchor="start"))
    p.append(line(120, ny, nx, ny, color=INK, sw=2))
    # вузол входу
    p.append(circle(nx, ny, 4, fill=INK, stroke=INK))
    p.append(text(nx, ny - 12, "вхід (високоомний)", size=12, bold=True))
    # стрілка в підсилювач
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.6"/>'
             % (nx + 18, ny - 22, nx + 18, ny + 22, nx + 66, ny, FILL, LINE))
    p.append(text(nx + 90, ny + 4, "до АЦП", size=11, color=MUTED, anchor="start"))
    # витік: резистор від вузла ВНИЗ до «брудного» вузла (живлення / сусідня доріжка)
    p.append(line(nx, ny, nx, ny + 50, color=POS, sw=2))
    p.append(rect(nx - 12, ny + 50, 24, 60, fill="#fdecea", stroke=POS, sw=1.6, rx=3))
    p.append(text(nx + 16, ny + 74, "Rвитоку", size=12, bold=True, color=POS, anchor="start"))
    p.append(text(nx + 16, ny + 90, "1 ГОм (волого)", size=11, color=POS, anchor="start"))
    p.append(line(nx, ny + 110, nx, ny + 150, color=POS, sw=2))
    p.append(line(nx - 30, ny + 150, nx + 30, ny + 150, color=POS, sw=2))
    p.append(text(nx, ny + 168, "сусідній вузол  5 В", size=12, color=POS))

    b, _, _ = textbox(515, 150,
                      "Корисне джерело МІЦНЕ за напругою, але\n"
                      "слабке за струмом (100 ГОм). Витік 1 ГОм\n"
                      "до 5-вольтового сусіда — це дільник, де\n"
                      "брудний вузол майже жорсткий, а корисний\n"
                      "ні. Вхід підтягується до ≈ 4.95 В — сигнал\n"
                      "розчавлено, ще до підсилювача.",
                      size=12, fill="#fdecea", stroke=POS)
    p.append(b)
    render(os.path.join(OUT, 'leakage-divider.svg'), W, H, *p,
           title="Витік — це паразитний резистор: дільник топить високоомний сигнал")


def guard_nulls_v():
    """Кільце на потенціалі входу: напруга на Rвитоку ≈ 0 → струм витоку ≈ 0 (закон Ома)."""
    W, H = 720, 330
    p = []
    cy = 150
    # дві однакові «коробки» опору витоку: без кільця і з кільцем
    def leak(cx, vleft, vright, col, ilbl, fillc):
        out = []
        # лівий вузол
        out.append(circle(cx - 90, cy, 4, fill=INK, stroke=INK))
        out.append(text(cx - 90, cy - 16, vleft, size=12, bold=True))
        # опір витоку
        out.append(rect(cx - 50, cy - 14, 100, 28, fill=fillc, stroke=col, sw=1.8, rx=4))
        out.append(text(cx, cy + 5, "Rвитоку", size=12, bold=True, color=col))
        # правий вузол
        out.append(circle(cx + 90, cy, 4, fill=INK, stroke=INK))
        out.append(text(cx + 90, cy - 16, vright, size=12, bold=True))
        out.append(line(cx - 90, cy, cx - 50, cy, color=col, sw=2))
        out.append(line(cx + 50, cy, cx + 90, cy, color=col, sw=2))
        out.append(text(cx, cy + 40, ilbl, size=13, bold=True, color=col))
        return out

    p += leak(190, "5 В", "0.1 В", POS, "I = 4.9 В / R  (великий)", "#fdecea")
    p.append(text(190, cy + 70, "БЕЗ кільця: вся різниця на опорі", size=12, color=MUTED))
    p += leak(530, "0.1 В", "0.1 В", FIELD, "I = 0.000 В / R  ≈ 0", "#eafaf0")
    p.append(text(530, cy + 70, "З кільцем на тому ж потенціалі", size=12, color=MUTED))

    # стрілка-перехід
    p.append(arrow(310, cy, 400, cy, color=INK, sw=2))
    p.append(text(355, cy - 12, "кільце", size=12, bold=True, color=FIELD))

    b, _, _ = textbox(W / 2, 300,
                      "Струм витоку = напруга на опорі / опір. Прибери НАПРУГУ на кінцях опору —\n"
                      "тримай обидва кінці на одному потенціалі — і струм зникне, хоч опір той самий.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'guard-nulls-v.svg'), W, H, *p,
           title="Кільце нулює НАПРУГУ на опорі витоку — і струм гасне сам")


def guard_ring_layout():
    """Топологія: кільце оточує доріжку/вивід входу; джерело витоку тепер живить кільце, не вхід."""
    W, H = 720, 360
    p = []
    # «брудне» оточення — сітка-фон
    p.append(rect(60, 70, 600, 230, fill="#fbfbfb", stroke=MUTED, sw=1, rx=8))
    p.append(text(80, 90, "поверхня плати (волога, флюс, бруд → витоки звідусіль)", size=11, color=MUTED, anchor="start"))

    # центральна доріжка входу
    cx, cy = 360, 195
    p.append(circle(cx, cy, 8, fill="#eaf0fd", stroke=NEG, sw=2))
    p.append(text(cx, cy + 4, "•", size=10, color=NEG))
    p.append(text(cx, cy - 22, "вивід / доріжка ВХОДУ", size=12, bold=True, color=NEG))
    p.append(text(cx, cy - 8, "(0.1 В, високоомний)", size=11, color=NEG))

    # охоронне кільце навколо
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="14" fill="none" '
             'stroke="%s" stroke-width="3.5"/>' % (cx - 95, cy - 55, 190, 110, FIELD))
    p.append(text(cx, cy + 44, "ОХОРОННЕ КІЛЬЦЕ  (0.1 В — той самий потенціал)", size=12, bold=True, color=FIELD))

    # стрілки витоку ззовні: впираються в кільце, не доходять до входу
    for sx, sy in [(120, 120), (120, 270), (600, 120), (600, 270)]:
        ex = cx - 105 if sx < cx else cx + 105
        ey = cy - 40 if sy < cy else cy + 40
        p.append(arrow(sx, sy, ex, ey, color=POS, sw=1.8))
    p.append(text(120, 112, "витік", size=11, color=POS, anchor="start"))
    p.append(text(600, 112, "витік", size=11, color=POS, anchor="end"))

    # підпис: кільце ловить увесь струм, вхід чистий
    p.append(text(cx, cy + 70, "увесь струм витоку сідає на кільце — до входу не доходить нічого", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 332,
                      "Кільце фізично ОТОЧУЄ високоомний вузол. Будь-який витік із брудного оточення\n"
                      "впирається спершу в кільце; його бере на себе джерело кільця, а не сам вхід.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'guard-ring-layout.svg'), W, H, *p,
           title="Кільце оточує вхід: перехоплює витік ще до високоомного вузла")


def guard_noninv_inv():
    """Куди гнати потенціал кільця: неінвертувальний — з виходу-повторювача; інвертувальний — на землю."""
    W, H = 720, 360
    p = []

    def opamp(cx, cy, lbl_in_plus, lbl_in_minus):
        out = []
        out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.8"/>'
                   % (cx, cy - 38, cx, cy + 38, cx + 64, cy, FILL, LINE))
        out.append(text(cx + 10, cy - 14, "+", size=15, bold=True, color=POS, anchor="start"))
        out.append(text(cx + 10, cy + 22, "−", size=15, bold=True, color=NEG, anchor="start"))
        return out

    # ── ліворуч: неінвертувальний (повторювач) ──
    cx1, cy1 = 150, 150
    p += opamp(cx1, cy1, "+", "−")
    p.append(text(cx1 + 30, cy1 - 56, "неінвертувальний", size=13, bold=True))
    # вхід на «+»
    p.append(line(cx1 - 70, cy1 - 18, cx1, cy1 - 18, color=NEG, sw=2))
    p.append(circle(cx1 - 70, cy1 - 18, 4, fill=INK, stroke=INK))
    p.append(text(cx1 - 74, cy1 - 30, "Vвх", size=11, color=NEG, anchor="end"))
    # вихід
    p.append(line(cx1 + 64, cy1, cx1 + 110, cy1, color=INK, sw=2))
    p.append(text(cx1 + 114, cy1 + 4, "Vвих ≈ Vвх", size=11, color=MUTED, anchor="start"))
    # зворотний на «−»
    p.append(line(cx1 + 90, cy1, cx1 + 90, cy1 + 50, color=INK, sw=1.6))
    p.append(line(cx1 + 90, cy1 + 50, cx1 - 18, cy1 + 50, color=INK, sw=1.6))
    p.append(line(cx1 - 18, cy1 + 50, cx1 - 18, cy1 + 18, color=INK, sw=1.6))
    p.append(line(cx1 - 18, cy1 + 18, cx1, cy1 + 18, color=INK, sw=1.6))
    # кільце від виходу
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" fill="none" '
             'stroke="%s" stroke-width="3"/>' % (cx1 - 84, cy1 - 34, 30, 32, FIELD))
    p.append(line(cx1 + 90, cy1 + 50, cx1 - 100, cy1 + 50, color=FIELD, sw=2.2, dash="5 4"))
    p.append(line(cx1 - 100, cy1 + 50, cx1 - 100, cy1 - 18, color=FIELD, sw=2.2, dash="5 4"))
    p.append(line(cx1 - 100, cy1 - 18, cx1 - 84, cy1 - 18, color=FIELD, sw=2.2, dash="5 4"))
    p.append(text(cx1 - 10, cy1 + 86, "кільце ← з ВИХОДУ", size=12, bold=True, color=FIELD))
    p.append(text(cx1 - 10, cy1 + 102, "(гониться за Vвх)", size=11, color=MUTED))

    # ── праворуч: інвертувальний / трансімпедансний (віртуальна земля) ──
    cx2, cy2 = 470, 150
    p += opamp(cx2, cy2, "+", "−")
    p.append(text(cx2 + 30, cy2 - 56, "інвертувальний (TIA)", size=13, bold=True))
    # «+» на землю
    p.append(line(cx2 - 40, cy2 + 18, cx2, cy2 + 18, color=INK, sw=2))
    p.append(line(cx2 - 40, cy2 + 10, cx2 - 40, cy2 + 26, color=INK, sw=2))
    p.append(line(cx2 - 46, cy2 + 16, cx2 - 34, cy2 + 16, color=INK, sw=1.5))
    p.append(text(cx2 - 50, cy2 + 22, "0 В", size=11, color=MUTED, anchor="end"))
    # вхід-струм у «−» = віртуальна земля
    p.append(line(cx2 - 70, cy2 - 18, cx2, cy2 - 18, color=NEG, sw=2))
    p.append(circle(cx2 - 70, cy2 - 18, 4, fill=INK, stroke=INK))
    p.append(text(cx2 - 74, cy2 - 30, "Iвх", size=11, color=NEG, anchor="end"))
    p.append(text(cx2 - 30, cy2 - 6, "≈ 0 В", size=10, color=FIELD))
    # вихід + Rзв
    p.append(line(cx2 + 64, cy2, cx2 + 110, cy2, color=INK, sw=2))
    p.append(text(cx2 + 114, cy2 + 4, "Vвих", size=11, color=MUTED, anchor="start"))
    p.append(line(cx2 + 90, cy2, cx2 + 90, cy2 - 50, color=INK, sw=1.6))
    p.append(rect(cx2 + 6, cy2 - 58, 76, 16, fill=BG, stroke=INK, sw=1.4, rx=3))
    p.append(text(cx2 + 44, cy2 - 46, "Rзв", size=11))
    p.append(line(cx2 + 6, cy2 - 50, cx2 - 18, cy2 - 50, color=INK, sw=1.6))
    p.append(line(cx2 - 18, cy2 - 50, cx2 - 18, cy2 - 18, color=INK, sw=1.6))
    p.append(line(cx2 - 18, cy2 - 18, cx2, cy2 - 18, color=INK, sw=1.6))
    # кільце на землю
    p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="10" fill="none" '
             'stroke="%s" stroke-width="3"/>' % (cx2 - 84, cy2 - 34, 30, 32, FIELD))
    p.append(line(cx2 - 84, cy2 + 70, cx2 - 84, cy2 - 2, color=FIELD, sw=2.2, dash="5 4"))
    p.append(line(cx2 - 110, cy2 + 70, cx2 - 50, cy2 + 70, color=FIELD, sw=2.2, dash="5 4"))
    p.append(line(cx2 - 80, cy2 + 66, cx2 - 88, cy2 + 74, color=FIELD, sw=1.5))
    p.append(text(cx2 - 10, cy2 + 86, "кільце ← на ЗЕМЛЮ", size=12, bold=True, color=FIELD))
    p.append(text(cx2 - 10, cy2 + 102, "(вхід уже ≈ 0 В)", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 338,
                      "Кільце завжди жене ТОЙ САМИЙ потенціал, що й захищений вузол. Неінвертувальний:\n"
                      "беремо його з виходу-повторювача. Інвертувальний: вузол — віртуальна земля, тож кільце на 0 В.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'guard-noninv-inv.svg'), W, H, *p,
           title="Куди вести кільце: з виходу-буфера (неінв.) чи на землю (інв.)")


# ── фігури до вставки math-guard-attenuation ────────────────────────────────

def residual_budget():
    """Що лишається на Rвитоку з кільцем: зсув Vos (плаский поверх) + сигнал/Aol
    (пропорційний сигналу). Поряд — гігантська повна різниця без кільця, для масштабу."""
    W, H = 720, 372
    p = []
    base = 250            # нульова лінія стовпчиків
    xL = 175              # «без кільця»
    xR = 510              # «з кільцем»
    bw = 96

    # вісь
    p.append(line(80, base, W - 40, base, color=MUTED, sw=1.4))

    # ── ліворуч: без кільця — повна різниця 4.9 В ──
    fullh = 192
    p.append(rect(xL - bw / 2, base - fullh, bw, fullh, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(xL, base - fullh - 12, "БЕЗ кільця", size=13, bold=True, color=POS))
    p.append(text(xL, base - fullh / 2, "ΔV = 4.9 В", size=14, bold=True, color=POS))
    p.append(text(xL, base - fullh / 2 + 18, "(уся різниця)", size=11, color=POS))
    p.append(text(xL, base + 20, "сигнал тоне", size=11, color=POS))

    # ── праворуч: з кільцем — крихітний залишок із двох доданків, показаний лупою ──
    p.append(text(xR, base - fullh - 12, "З кільцем  (лупа ×1000)", size=13, bold=True, color=FIELD))
    mvh = 168             # 7 мВ → 168 px (окрема шкала в мВ, бо в шкалі вольтів залишок невидимий)
    px_per_mv = mvh / 7.0
    vos = 2.0             # мВ — зсув ОП
    sig = 1.0             # мВ — похибка повторювача Vсигн/Aol (демонстраційно наочна частка)
    h1 = vos * px_per_mv
    h2 = sig * px_per_mv
    p.append(rect(xR - bw / 2, base - h1, bw, h1, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(rect(xR - bw / 2, base - h1 - h2, bw, h2, fill="#cdebd9", stroke=FIELD, sw=1.6))
    p.append(text(xR + bw / 2 + 10, base - h1 / 2 + 4, "Vos ≈ 2 мВ", size=11, color=INK, anchor="start"))
    p.append(text(xR + bw / 2 + 10, base - h1 / 2 + 19, "(не від сигналу)", size=10, color=MUTED, anchor="start"))
    p.append(text(xR + bw / 2 + 10, base - h1 - h2 / 2 + 2, "Vсигн/Aol ≈ 1 мВ", size=11, color=INK, anchor="start"))
    p.append(text(xR + bw / 2 + 10, base - h1 - h2 / 2 + 17, "(росте з сигналом)", size=10, color=MUTED, anchor="start"))
    p.append(text(xR, base - h1 - h2 - 12, "разом ≈ 3 мВ", size=12, bold=True, color=FIELD))
    # шкала лупи
    p.append(line(xR - bw / 2 - 16, base, xR - bw / 2 - 16, base - mvh, color=MUTED, sw=1.2))
    p.append(text(xR - bw / 2 - 20, base - mvh + 4, "7 мВ", size=10, color=MUTED, anchor="end"))
    p.append(text(xR - bw / 2 - 20, base, "0", size=10, color=MUTED, anchor="end"))

    p.append(text(W / 2, base + 22, "напруга, що лишається на опорі витоку Rвитоку → саме вона жене залишковий струм", size=11, color=MUTED))

    b, _, _ = textbox(W / 2, 332,
                      "Кільце знімає з опору майже всю напругу — лишаються ДВА дрібні залишки: зсув ОП Vos\n"
                      "(плаский, від сигналу не залежить) і похибка повторювача Vсигн/Aol (росте із сигналом).\n"
                      "Праву колонку показано лупою ×1000 — у шкалі лівої вона була б тонша за лінію.",
                      size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b)
    render(os.path.join(OUT, 'residual-budget.svg'), W, H, *p,
           title="Що лишається на опорі витоку: зсув Vos + похибка підсилення")


def suppression_ratio():
    """Коефіцієнт пригнічення = відношення напруг (R скорочується), і чому він
    скінченний: залишкова напруга ніколи не нуль, тож пригнічення велике, але не ∞."""
    W, H = 720, 320
    p = []
    cx = 250
    fy = 130              # центр дробу
    # дріб ΔVповна / Vзалишк
    p.append(text(cx, fy - 14, "ΔVповна", size=21, bold=True, color=POS))
    p.append(line(cx - 78, fy + 4, cx + 78, fy + 4, color=INK, sw=2.4))
    p.append(text(cx, fy + 30, "Vзалишк", size=21, bold=True, color=FIELD))
    p.append(text(cx + 112, fy + 8, "=", size=24, bold=True))
    p.append(text(cx + 150, fy + 8, "Gприг", size=21, bold=True, anchor="start", color=INK))
    p.append(text(cx, fy + 70, "опір Rвитоку скоротився — лишилось чисте відношення двох напруг", size=11, color=MUTED))

    # приклад чисел праворуч-знизу від дробу
    nx = cx
    p.append(text(nx, fy + 104, "2 В  /  2 мВ  =  1000×        4.9 В  /  3 мВ  ≈  1600×", size=13, bold=True, color=INK))

    # «ніколи не нуль»
    b2, _, _ = textbox(W / 2, 268,
                       "Vзалишк = Vos + Vсигн/Aol  >  0  ЗАВЖДИ   →   Iзалишк = Vзалишк / Rвитоку  >  0.\n"
                       "Зсув скінченний, підсилення скінченне — пригнічення велике (×1000…×2000), але НЕ нескінченне.",
                       size=12, fill="#eef7f0", stroke=FIELD)
    p.append(b2)
    render(os.path.join(OUT, 'suppression-ratio.svg'), W, H, *p,
           title="Пригнічення — це відношення напруг, і воно скінченне")


if __name__ == '__main__':
    leakage_divider()
    guard_nulls_v()
    guard_ring_layout()
    guard_noninv_inv()
    residual_budget()
    suppression_ratio()
    print("OK: 6 figures ->", OUT)
