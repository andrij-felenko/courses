# -*- coding: utf-8 -*-
"""Фігури для теми flyback-isolated (зворотноходовий перетворювач) та її вставки.
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5). Вивід у ./img/.

    python figs.py
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *  # noqa: E402,F403

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

GOLD = "#b8860b"   # осердя / магнітне
HOT = "#fdecea"    # тло гарячої сторони
COLD = "#e9f7ef"   # тло холодної сторони


def _coil(x, y_top, y_bot, n=5, r=9, left=True):
    """Обмотка як ланцюжок півдуг уздовж вертикалі (декоративна котушка)."""
    step = (y_bot - y_top) / n
    d = "M %.1f %.1f " % (x, y_top)
    sweep = 0 if left else 1
    yy = y_top
    for _ in range(n):
        d += "A %.1f %.1f 0 0 %d %.1f %.1f " % (r, step / 2, sweep, x, yy + step)
        yy += step
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, GOLD)


def fig_isolation():
    """Дві НЕ з'єднані «землі» й бар'єр ізоляції між сторонами; крізь бар'єр —
    лише магнітне поле трансформатора, жоден дріт сторони не перетинає."""
    W, H = 880, 430
    bx = W / 2
    f = []

    # тло двох зон
    f.append(rect(30, 80, bx - 30 - 16, 300, fill=HOT, stroke=POS, sw=1.8))
    f.append(rect(bx + 16, 80, W - 30 - (bx + 16), 300, fill=COLD, stroke=FIELD, sw=1.8))

    # лінія бар'єра
    f.append(line(bx, 70, bx, 392, color=POS, sw=2, dash="8 6"))
    f.append(text(bx, 60, "бар'єр ізоляції", size=13, color=POS, bold=True))

    # заголовки зон
    f.append(text((30 + bx - 16) / 2, 102, "ПЕРВИННА — небезпечна", size=14, color=POS, bold=True))
    f.append(text((bx + 16 + W - 30) / 2, 102, "ВТОРИННА — безпечна", size=14, color=FIELD, bold=True))

    cxL = (30 + bx - 16) / 2
    cxR = (bx + 16 + W - 30) / 2

    b, w, h = textbox(cxL, 150, "мережа 230 В", size=13, fill="#ffffff", stroke=POS, sw=1.8)
    f.append(b)
    b, w, h = textbox(cxR, 150, "5 В до рук", size=13, fill="#ffffff", stroke=FIELD, sw=1.8)
    f.append(b)

    # дві окремі «землі» (різні символи)
    def gnd(cx, cy, color):
        out = line(cx, cy - 16, cx, cy, color=color, sw=2)
        out += line(cx - 22, cy, cx + 22, cy, color=color, sw=2)
        out += line(cx - 14, cy + 7, cx + 14, cy + 7, color=color, sw=2)
        out += line(cx - 7, cy + 14, cx + 7, cy + 14, color=color, sw=2)
        return out
    f.append(gnd(cxL, 330, POS))
    f.append(gnd(cxR, 330, FIELD))
    f.append(text(cxL, 365, "своя земля", size=12, color=MUTED))
    f.append(text(cxR, 365, "інша земля", size=12, color=MUTED))

    # трансформатор на бар'єрі: дві обмотки + осердя, лише магнітний зв'язок
    f.append(_coil(bx - 14, 175, 285, n=5, r=10, left=True))
    f.append(_coil(bx + 14, 175, 285, n=5, r=10, left=False))
    f.append(line(bx - 3, 170, bx - 3, 290, color=GOLD, sw=2))
    f.append(line(bx + 3, 170, bx + 3, 290, color=GOLD, sw=2))
    f.append(text(bx, 312, "лише магнітне поле", size=12, color=GOLD, bold=True))

    return render(os.path.join(IMG, "isolation.svg"), W, H, *f)


def fig_phases():
    """Дві фази flyback: ВКЛ — осердя НАБИРАЄ енергію (діод вторинної закритий),
    ВИКЛ — енергія «відлітає» у вторинну (діод відкритий)."""
    W, H = 900, 430
    f = []
    midx = W / 2

    for col, (x0, title, sub) in enumerate([
        (40, "Фаза ВКЛ — запасання", "ключ замкнено"),
        (midx + 20, "Фаза ВИКЛ — віддача", "ключ розімкнено"),
    ]):
        x1 = x0 + (midx - 60)
        f.append(rect(x0, 70, x1 - x0, 320, fill="#fafafa", stroke=MUTED, sw=1.5))
        f.append(text((x0 + x1) / 2, 96, title, size=14, color=INK, bold=True))
        f.append(text((x0 + x1) / 2, 116, sub, size=12, color=MUTED))

        cxp = x0 + (x1 - x0) * 0.30   # первинна
        cxs = x0 + (x1 - x0) * 0.70   # вторинна
        ytop, ybot = 150, 250

        # осердя між обмотками
        f.append(line((cxp + cxs) / 2 - 3, ytop - 6, (cxp + cxs) / 2 - 3, ybot + 6, color=GOLD, sw=2))
        f.append(line((cxp + cxs) / 2 + 3, ytop - 6, (cxp + cxs) / 2 + 3, ybot + 6, color=GOLD, sw=2))
        f.append(_coil(cxp, ytop, ybot, n=4, r=9, left=True))
        f.append(_coil(cxs, ytop, ybot, n=4, r=9, left=False))

        # точки конвенції (первинна вгорі, вторинна внизу — протилежні)
        f.append(circle(cxp - 12, ytop - 2, 3, fill=INK, stroke=INK))
        f.append(circle(cxs + 12, ybot + 2, 3, fill=INK, stroke=INK))

        if col == 0:
            # вхід + ключ замкнено, стрілка струму в первинну
            f.append(text(cxp, 138, "Vвх", size=12, color=POS, bold=True))
            f.append(arrow(cxp, 268, cxp, 300, color=POS, sw=2.2))
            f.append(text(cxp, 318, "струм ↑", size=12, color=POS, bold=True))
            f.append(text((cxp + cxs) / 2, ybot + 56, "осердя НАБИРАЄ", size=12, color=GOLD, bold=True))
            f.append(text((cxp + cxs) / 2, ybot + 74, "енергію", size=12, color=GOLD, bold=True))
            # діод вторинної закритий
            f.append(text(cxs, 300, "діод ✕", size=12, color=MUTED, bold=True))
            f.append(text(cxs, 318, "(закритий)", size=11, color=MUTED))
        else:
            # ключ розімкнено, енергія летить у вторинну
            f.append(text(cxp, 300, "ключ ✕", size=12, color=MUTED, bold=True))
            f.append(text(cxp, 318, "(розімкнено)", size=11, color=MUTED))
            f.append(arrow(cxs, 300, cxs, 268, color=FIELD, sw=2.2))
            f.append(text(cxs, 318, "струм →вихід", size=12, color=FIELD, bold=True))
            f.append(text((cxp + cxs) / 2, ybot + 56, "енергія", size=12, color=FIELD, bold=True))
            f.append(text((cxp + cxs) / 2, ybot + 74, "ВІДЛІТАЄ", size=12, color=FIELD, bold=True))

    return render(os.path.join(IMG, "phases.svg"), W, H, *f)


def fig_turns():
    """Два важелі напруги: коефіцієнт витків Ns/Np (груба шкала, конструкція)
    і шпаруватість D (тонке підстроювання від контролера)."""
    W, H = 860, 380
    f = []

    f.append(text(W / 2, 40, "Vвих = Vвх · (Ns/Np) · D/(1−D)", size=17, color=INK, bold=True))

    # лівий важіль: витки
    b, w, h = textbox(W * 0.27, 110, "коефіцієнт витків\nNs / Np", size=14,
                      fill="#fff7e6", stroke=GOLD, sw=1.8, bold=True)
    f.append(b)
    f.append(text(W * 0.27, 165, "груба шкала", size=13, color=GOLD, bold=True))
    f.append(text(W * 0.27, 188, "задана трансформатором", size=12, color=MUTED))
    f.append(text(W * 0.27, 220, "мало витків вторинної", size=12, color=INK))
    f.append(text(W * 0.27, 240, "→ велике зниження", size=12, color=INK))
    f.append(text(W * 0.27, 270, "325 В → 5 В одним", size=13, color=POS, bold=True))
    f.append(text(W * 0.27, 290, "трансформатором", size=13, color=POS, bold=True))

    # правий важіль: D
    b, w, h = textbox(W * 0.73, 110, "шпаруватість\nD", size=14,
                      fill="#eaf0fd", stroke=NEG, sw=1.8, bold=True)
    f.append(b)
    f.append(text(W * 0.73, 165, "тонке підстроювання", size=13, color=NEG, bold=True))
    f.append(text(W * 0.73, 188, "крутить контролер", size=12, color=MUTED))
    f.append(text(W * 0.73, 220, "тримає вихід сталим", size=12, color=INK))
    f.append(text(W * 0.73, 240, "за зміни входу", size=12, color=INK))
    f.append(text(W * 0.73, 270, "і навантаження", size=12, color=INK))

    # знак множення між ними
    f.append(text(W / 2, 150, "×", size=30, color=INK, bold=True))
    f.append(text(W / 2, 270, "разом — майже", size=12, color=FIELD, bold=True))
    f.append(text(W / 2, 290, "будь-яке відношення", size=12, color=FIELD, bold=True))

    return render(os.path.join(IMG, "turns.svg"), W, H, *f)


def fig_feedback():
    """Зворотний зв'язок крізь бар'єр оптопарою: світлодіод вторинної світить
    на фототранзистор первинної — крізь бар'єр летить світло, а не струм."""
    W, H = 880, 380
    bx = W / 2
    f = []

    f.append(rect(30, 70, bx - 30 - 16, 250, fill=HOT, stroke=POS, sw=1.6))
    f.append(rect(bx + 16, 70, W - 30 - (bx + 16), 250, fill=COLD, stroke=FIELD, sw=1.6))
    f.append(line(bx, 60, bx, 330, color=POS, sw=2, dash="8 6"))
    f.append(text(bx, 50, "бар'єр ізоляції", size=13, color=POS, bold=True))

    cxL = (30 + bx - 16) / 2
    cxR = (bx + 16 + W - 30) / 2
    f.append(text(cxL, 96, "ПЕРВИННА", size=13, color=POS, bold=True))
    f.append(text(cxR, 96, "ВТОРИННА", size=13, color=FIELD, bold=True))

    b, w, h = textbox(cxL, 140, "контролер\n(крутить D)", size=13, fill="#ffffff", stroke=POS, sw=1.8)
    f.append(b)
    b, w, h = textbox(cxR, 140, "вихід Vвих", size=13, fill="#ffffff", stroke=FIELD, sw=1.8)
    f.append(b)

    # оптопара: фототранзистор (ліворуч) ← світло ← світлодіод (праворуч)
    yb = 220
    f.append(circle(cxL + 40, yb, 13, fill="#eaf0fd", stroke=NEG, sw=1.8))   # фототранзистор
    f.append(text(cxL + 40, yb + 34, "фото-\nтранзистор".split("\n")[0], size=11, color=NEG))
    f.append(text(cxL + 40, yb + 48, "транзистор", size=11, color=NEG))
    f.append(circle(cxR - 40, yb, 13, fill="#fff7e6", stroke=GOLD, sw=1.8))   # світлодіод
    f.append(text(cxR - 40, yb + 34, "світлодіод", size=11, color=GOLD))

    # промінь світла крізь бар'єр (хвилясті стрілки = світло)
    f.append(arrow(cxR - 40, yb, cxL + 40, yb, color=GOLD, sw=2.4))
    f.append(text(bx, yb - 18, "світло, не струм", size=13, color=GOLD, bold=True))

    # підпис унизу
    f.append(text(W / 2, 358, "регулювання перетинає ізоляцію, не порушуючи її",
                  size=12, color=MUTED))

    return render(os.path.join(IMG, "feedback.svg"), W, H, *f)


def fig_adapter():
    """Повний ланцюг мережевого адаптера: 230 В → міст → 325 В → flyback крізь
    трансформатор → ізольовані 5 В; оптопара тримає рівень; бар'єр посередині."""
    W, H = 940, 360
    f = []
    bx = W * 0.60   # бар'єр ближче до виходу

    # тло двох зон
    f.append(rect(20, 90, bx - 20 - 14, 200, fill=HOT, stroke=POS, sw=1.5))
    f.append(rect(bx + 14, 90, W - 20 - (bx + 14), 200, fill=COLD, stroke=FIELD, sw=1.5))
    f.append(line(bx, 80, bx, 300, color=POS, sw=2, dash="8 6"))
    f.append(text(bx, 70, "бар'єр", size=12, color=POS, bold=True))

    y = 150
    boxes = [
        (95, "мережа\n230 В~", POS),
        (215, "міст +\nконденсатор", POS),
        (335, "ключ\n(MOSFET)", POS),
    ]
    for cx, label, col in boxes:
        b, w, h = textbox(cx, y, label, size=12, fill="#ffffff", stroke=col, sw=1.6)
        f.append(b)
    # підпис 325 В під рядком вузлів (щоб не налазив на заголовок зони)
    f.append(text(275, y + 42, "≈325 В пост.", size=12, color=POS, bold=True))

    # трансформатор на бар'єрі
    f.append(_coil(bx - 14, y - 35, y + 35, n=4, r=9, left=True))
    f.append(_coil(bx + 14, y - 35, y + 35, n=4, r=9, left=False))
    f.append(line(bx - 3, y - 40, bx - 3, y + 40, color=GOLD, sw=2))
    f.append(line(bx + 3, y - 40, bx + 3, y + 40, color=GOLD, sw=2))
    f.append(text(bx, y + 60, "трансформатор", size=11, color=GOLD, bold=True))

    # вторинна сторона
    for cx, label in [(bx + 110, "діод +\nконденсатор"), (W - 80, "5 В\nпост.")]:
        b, w, h = textbox(cx, y, label, size=12, fill="#ffffff", stroke=FIELD, sw=1.6)
        f.append(b)

    # стрілки потоку енергії
    f.append(arrow(150, y, 178, y, color=INK, sw=1.8))
    f.append(arrow(258, y, 298, y, color=INK, sw=1.8))
    f.append(arrow(372, y, bx - 26, y, color=INK, sw=1.8))
    f.append(arrow(bx + 26, y, bx + 70, y, color=INK, sw=1.8))

    # оптопара зворотного зв'язку (під трансформатором, через бар'єр)
    yb = y + 95
    f.append(arrow(bx + 110, yb, 335, yb, color=GOLD, sw=2))
    f.append(text((335 + bx + 110) / 2, yb - 10, "оптопара: вихід → контролер (світло)",
                  size=11, color=GOLD, bold=True))

    f.append(text((20 + bx) / 2, 110, "небезпечна сторона", size=12, color=POS, bold=True))
    f.append(text((bx + W) / 2, 110, "безпечна сторона", size=12, color=FIELD, bold=True))

    return render(os.path.join(IMG, "adapter.svg"), W, H, *f)


def fig_snubber():
    """Викид індуктивності витоку при вимиканні ключа й снабер, що підрізає пік:
    енергії витоку нема куди дітися (вторинна її не приймає) — гострий сплеск на
    стоку, здатний пробити ключ; снабер (RCD/TVS) поглинає й обрізає пік."""
    W, H = 860, 420
    f = []
    # графік напруги на стоку в часі
    L, R = 90, 560
    T, B = 90, 320
    f.append(line(L, T - 10, L, B, color=INK, sw=2))
    f.append(line(L, B, R, B, color=INK, sw=2))
    f.append(text(L - 12, T - 16, "U стоку", size=12, color=INK, anchor="end"))
    f.append(text(R, B + 22, "час", size=12, color=INK))

    # рівні
    y_vin = B - 70        # Vвх
    y_refl = B - 130      # Vвх + відбита
    y_spike = T + 6       # пік витоку
    y_clamp = B - 175     # рівень, до якого ріже снабер
    f.append(line(L, y_vin, R, y_vin, color=MUTED, sw=1, dash="4 4"))
    f.append(text(R + 4, y_vin + 4, "Vвх", size=11, color=MUTED, anchor="start"))
    f.append(line(L, y_refl, R, y_refl, color=MUTED, sw=1, dash="4 4"))
    f.append(text(R + 4, y_refl + 4, "+відбита", size=11, color=MUTED, anchor="start"))
    f.append(line(L, y_clamp, R, y_clamp, color=FIELD, sw=1.4, dash="6 4"))
    f.append(text(R + 4, y_clamp + 4, "снабер ріже", size=11, color=FIELD, anchor="start", bold=True))

    # БЕЗ снабера (червона крива): гострий пік до самого верху
    x_sw = L + 150        # момент вимикання
    no = ["%.1f,%.1f" % (L, y_vin), "%.1f,%.1f" % (x_sw, y_vin),
          "%.1f,%.1f" % (x_sw + 18, y_spike),                # гострий викид угору
          "%.1f,%.1f" % (x_sw + 42, y_refl),                 # спад до відбитої
          "%.1f,%.1f" % (R, y_refl)]
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(no), POS))
    f.append(text(x_sw + 20, y_spike - 8, "пробій!", size=12, color=POS, bold=True, anchor="start"))

    # стрілка вимикання
    f.append(line(x_sw, T - 6, x_sw, B, color=MUTED, sw=1, dash="3 4"))
    f.append(text(x_sw, B + 22, "ключ вимкнено", size=11, color=MUTED))

    # підписи кривих
    f.append(text(L + 20, y_vin - 8, "Vвх (ключ відкритий)", size=11, color=MUTED, anchor="start"))

    # пояснювальна рамка
    box, bw, bh = textbox((L + R) / 2, B + 70,
                          "енергії витоку нема куди дітися: вторинна її не приймає →\n"
                          "гострий сплеск на стоку. Снабер (RCD або TVS) його поглинає.",
                          size=12, fill="#eef7f0", stroke=FIELD, sw=1.5)
    f.append(box)

    return render(os.path.join(IMG, "snubber.svg"), W, H, *f)


def fig_safety_zones():
    """Дві зони адаптера й бар'єр між ними: гаряча первинна (325 В) ліворуч,
    холодна вторинна (5 В) праворуч; фізична щілина в платі по центру;
    бар'єр перетинають лише оптопара (світло) і Y-конденсатор (шум).
    (Фігура вставки comp-wall-adapter.md — статус done, не змінюється.)"""
    W, H = 900, 500
    f = []

    bx = W / 2  # лінія бар'єра
    zone_bottom = 442  # низ кольорових зон

    # ── фон двох зон ──
    f.append(rect(20, 70, bx - 20 - 14, zone_bottom - 70, fill="#fdecea", stroke=POS, sw=2))
    f.append(rect(bx + 14, 70, W - 20 - (bx + 14), zone_bottom - 70, fill="#e9f7ef", stroke=FIELD, sw=2))

    # ── фізична щілина в платі (наскрізний проріз) ──
    f.append(rect(bx - 13, 70, 26, zone_bottom - 70, fill="#ffffff", stroke=MUTED, sw=2, rx=4))
    f.append(line(bx, 78, bx, zone_bottom - 8, color=MUTED, sw=2, dash="6 6"))
    f.append(text(bx, zone_bottom + 28, "проріз у платі + трансформатор = бар'єр", size=12, color=MUTED))

    # ── заголовки зон ──
    f.append(text((20 + bx - 14) / 2, 56, "ПЕРВИННА — небезпечна", size=15, color=POS, bold=True))
    f.append(text((bx + 14 + W - 20) / 2, 56, "ВТОРИННА — безпечна", size=15, color=FIELD, bold=True))

    # ── вузли первинної (гарячої) ──
    cxL = (20 + bx - 14) / 2
    b, w, h = textbox(cxL, 120, "мережа 110–230 В\n→ міст → 325 В", size=13,
                      fill="#ffffff", stroke=POS, sw=1.8)
    f.append(b)
    f.append(plus(cxL, 168, r=11))
    f.append(text(cxL, 196, "325 В пост.", size=13, color=POS, bold=True))
    b, w, h = textbox(cxL, 250, "контролер + ключ\n(MOSFET)", size=13,
                      fill="#ffffff", stroke=POS, sw=1.8)
    f.append(b)
    f.append(text(cxL, 320, "дотик = смерть", size=14, color=POS, bold=True))

    # ── вузли вторинної (холодної) ──
    cxR = (bx + 14 + W - 20) / 2
    b, w, h = textbox(cxR, 120, "випрямляч\n+ конденсатор", size=13,
                      fill="#ffffff", stroke=FIELD, sw=1.8)
    f.append(b)
    f.append(minus(cxR - 30, 168, r=11))
    f.append(plus(cxR + 30, 168, r=11))
    f.append(text(cxR, 196, "5 В пост.", size=13, color=FIELD, bold=True))
    b, w, h = textbox(cxR, 250, "роз'єм USB\n(пальці, кабель)", size=13,
                      fill="#ffffff", stroke=FIELD, sw=1.8)
    f.append(b)
    f.append(text(cxR, 320, "безпечно для рук", size=14, color=FIELD, bold=True))

    # ── два містки через бар'єр ──
    yb1, yb2 = 364, 410
    # оптопара
    f.append(line(cxL, yb1, cxR, yb1, color=NEG, sw=2.4))
    bb, ww, hh = textbox(bx, yb1, "оптопара\n(світло)", size=12,
                         fill="#eaf0fd", stroke=NEG, sw=1.8)
    f.append(bb)
    # Y-конденсатор
    f.append(line(cxL, yb2, cxR, yb2, color=INK, sw=2.4, dash="4 4"))
    bb, ww, hh = textbox(bx, yb2, "Y-конд.\n(тільки шум)", size=12,
                         fill="#fff7e6", stroke="#b8860b", sw=1.8)
    f.append(bb)

    return render(os.path.join(IMG, "safety-zones.svg"), W, H, *f)


if __name__ == "__main__":
    outs = [
        fig_isolation(), fig_phases(), fig_turns(),
        fig_feedback(), fig_adapter(), fig_snubber(),
        fig_safety_zones(),
    ]
    for o in outs:
        print("written:", o)
