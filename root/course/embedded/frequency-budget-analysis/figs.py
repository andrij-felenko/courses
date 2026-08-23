# -*- coding: utf-8 -*-
"""Фігури до теми «Частотний бюджет у системах зв'язку» (frequency-budget-analysis).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Смуга як полиця: канали-коробки + захисні проміжки ─────────────────────
def fig_band_as_shelf():
    W, H = 760, 330
    f = [text(W / 2, 28, "Доступна смуга — полиця скінченної ширини", 16, INK, "middle", bold=True)]

    # «полиця» — рамка всієї смуги
    ox, oy = 60, 130
    bw, bh = 640, 70
    f.append(rect(ox, oy, bw, bh, fill="#fbfcfd", stroke=INK, sw=2.0, rx=4))
    # межі смуги
    f.append(text(ox, oy + bh + 22, "f_низ", 11, MUTED, "middle"))
    f.append(text(ox + bw, oy + bh + 22, "f_верх", 11, MUTED, "middle"))
    f.append(line(ox, oy + bh + 6, ox, oy + bh + 14, color=MUTED, sw=1.2))
    f.append(line(ox + bw, oy + bh + 6, ox + bw, oy + bh + 14, color=MUTED, sw=1.2))
    # дужка ширини
    f.append(line(ox, oy - 16, ox + bw, oy - 16, color=MUTED, sw=1.2))
    f.append(text(ox + bw / 2, oy - 22, "уся доступна смуга (Гц) — це й є «гаманець»", 11, MUTED, "middle"))

    # канали-коробки + захисні проміжки
    cols = ["#c0392b", "#2457d6", "#27ae60", "#b8860b", "#7d3c98"]
    n = 5
    guard = 18.0
    cw = (bw - (n + 1) * guard) / n
    for i in range(n):
        x = ox + guard + i * (cw + guard)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (x, oy + 8, cw, bh - 16, _tint(cols[i]), cols[i]))
        f.append(text(x + cw / 2, oy + bh / 2 + 5, "кан. %d" % (i + 1), 11, cols[i], "middle", bold=True))

    # позначити один захисний проміжок
    gx = ox + guard + cw + guard / 2
    f.append(line(gx, oy + 8, gx, oy + bh - 8, color=MUTED, sw=1.0, dash="3 3"))
    f.append(arrow(gx, oy + bh + 38, gx, oy + bh - 6, color=MUTED, sw=1.2))
    f.append(text(gx + 56, oy + bh + 44, "захисний проміжок", 10, MUTED, "middle"))

    f.append(fitbox(ox, oy + bh + 64, bw, 30,
                    "скільки каналів влізе = ширина полиці ÷ (ширина каналу + захисний проміжок)",
                    size=11.5, fill="#eef6ef", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "band-as-shelf.svg"), W, H, *f)


def _tint(hexcol):
    m = {"#c0392b": "#fbe7e4", "#2457d6": "#e6ecfb", "#27ae60": "#e4f4ea",
         "#b8860b": "#f6efdb", "#7d3c98": "#efe6f4", "#117a8b": "#e0f0f2"}
    return m.get(hexcol, "#f0f0f0")


# ── 2. Що з'їдає смугу: рахунок ширини одного слота ───────────────────────────
def fig_slot_ledger():
    W, H = 760, 360
    f = [text(W / 2, 28, "Скільки спектра треба одному каналу: рахунок у герцах", 15.5, INK, "middle", bold=True)]

    # центральна несна
    cx = W / 2
    base = 250
    # вісь частоти
    f.append(line(70, base, 690, base, color=MUTED, sw=1.3))
    f.append(text(694, base + 4, "f", 12, MUTED, "start"))
    f.append(line(cx, base + 6, cx, base - 150, color=MUTED, sw=1.0, dash="4 4"))
    f.append(text(cx, base + 22, "несна f₀", 11, INK, "middle", bold=True))

    # ── корисна смуга сигналу (зелена, у центрі) ──
    sig_w = 150
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="86" rx="3" fill="%s" stroke="%s" stroke-width="2"/>'
             % (cx - sig_w / 2, base - 100, sig_w, _tint("#27ae60"), "#27ae60"))
    f.append(text(cx, base - 54, "корисна смуга", 11.5, "#27ae60", "middle", bold=True))
    f.append(text(cx, base - 38, "сигналу B", 10.5, "#27ae60", "middle"))

    # ── запас на дрейф несної ±Δf (помаранчеві шматки обабіч) ──
    drift = 56
    for sgn in (-1, 1):
        x0 = cx + sgn * sig_w / 2
        x1 = x0 + sgn * drift
        xl, xr = min(x0, x1), max(x0, x1)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="86" fill="#f6efdb" stroke="%s" stroke-width="1.4" opacity="0.85"/>'
                 % (xl, base - 100, xr - xl, "#b8860b"))
    f.append(text(cx - sig_w / 2 - drift / 2, base - 110, "±Δf дрейф", 9.5, "#b8860b", "middle", bold=True))
    f.append(text(cx + sig_w / 2 + drift / 2, base - 110, "±Δf дрейф", 9.5, "#b8860b", "middle", bold=True))

    # ── захисний проміжок до сусідів (сірі краї) ──
    grd = 40
    for sgn in (-1, 1):
        x0 = cx + sgn * (sig_w / 2 + drift)
        x1 = x0 + sgn * grd
        xl, xr = min(x0, x1), max(x0, x1)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="86" fill="#eef0f2" stroke="#b8bec6" stroke-width="1.2"/>'
                 % (xl, base - 100, xr - xl))
    f.append(text(cx - sig_w / 2 - drift - grd / 2, base - 78, "захист", 9, MUTED, "middle"))
    f.append(text(cx + sig_w / 2 + drift + grd / 2, base - 78, "захист", 9, MUTED, "middle"))

    # дужка повної ширини слота
    full = sig_w + 2 * drift + 2 * grd
    f.append(line(cx - full / 2, base + 44, cx + full / 2, base + 44, color=INK, sw=1.5))
    f.append(line(cx - full / 2, base + 38, cx - full / 2, base + 50, color=INK, sw=1.5))
    f.append(line(cx + full / 2, base + 38, cx + full / 2, base + 50, color=INK, sw=1.5))
    f.append(text(cx, base + 62, "повна ширина слота = те, що канал реально «з'їдає»", 11, INK, "middle", bold=True))

    f.append(fitbox(120, base + 78, W - 240, 28,
                    "слот = смуга сигналу B  +  2·(запас на дрейф Δf)  +  2·(пів-захисний проміжок)",
                    size=11.5, fill="#eef6ef", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "slot-ledger.svg"), W, H, *f)


# ── 3. ppm-дрейф: дві вільні несні розходяться ───────────────────────────────
def fig_ppm_drift():
    W, H = 760, 360
    f = [text(W / 2, 26, "Допуск у ppm розсуває несні: канал треба ширший", 15.5, INK, "middle", bold=True)]

    cx = W / 2
    # ── верх: ідеал — обидві несні точно на місці ──
    yt = 110
    f.append(text(120, yt - 40, "Ідеал:", 12, INK, "start", bold=True))
    f.append(text(120, yt - 24, "обидва точно на f₀", 10, MUTED, "start"))
    f.append(line(150, yt, 690, yt, color=MUTED, sw=1.1))
    f.append(line(cx, yt + 4, cx, yt - 30, color="#27ae60", sw=2.4))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (cx - 5, yt - 30, cx + 5, yt - 30, cx, yt - 40, "#27ae60"))
    f.append(text(cx, yt + 18, "f₀ передавача = f₀ приймача", 10, "#27ae60", "middle", bold=True))

    # ── низ: реальність — передавач +Δ, приймач −Δ ──
    yb = 240
    f.append(text(120, yb - 40, "Реальність:", 12, INK, "start", bold=True))
    f.append(text(120, yb - 24, "кожен зі своїм ppm", 10, MUTED, "start"))
    f.append(line(150, yb, 690, yb, color=MUTED, sw=1.1))
    off = 70
    # передавач зсунутий праворуч
    f.append(line(cx + off, yb + 4, cx + off, yb - 30, color=POS, sw=2.4))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (cx + off - 5, yb - 30, cx + off + 5, yb - 30, cx + off, yb - 40, POS))
    f.append(text(cx + off, yb + 18, "передавач +Δ", 10, POS, "middle", bold=True))
    # приймач зсунутий ліворуч
    f.append(line(cx - off, yb + 4, cx - off, yb - 30, color=NEG, sw=2.4))
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (cx - off - 5, yb - 30, cx - off + 5, yb - 30, cx - off, yb - 40, NEG))
    f.append(text(cx - off, yb + 18, "приймач −Δ", 10, NEG, "middle", bold=True))
    # позначка f0 посередині
    f.append(line(cx, yb + 4, cx, yb - 14, color=MUTED, sw=1.0, dash="3 3"))
    f.append(text(cx, yb - 50, "f₀ (номінал)", 9.5, MUTED, "middle"))
    # дужка повного розходження
    f.append(line(cx - off, yb - 64, cx + off, yb - 64, color=INK, sw=1.4))
    f.append(text(cx, yb - 70, "розходження до 2·Δf", 10.5, INK, "middle", bold=True))

    f.append(fitbox(110, yb + 40, W - 220, 56,
                    "Δf = f₀ · ppm·10⁻⁶ на кожен бік.  2.4 ГГц × 40 ppm = 96 кГц зсуву на радіо;\n"
                    "два вільні радіо можуть розійтися вдвічі — ≈ 192 кГц. Цю «дірку» треба вмістити в канал.",
                    size=11.5, fill="#fdecea", stroke=POS, color=INK))

    render(os.path.join(IMG, "ppm-drift.svg"), W, H, *f)


# ── 4. Конкретика 2.4 ГГц: 14 каналів по 5 МГц, ширина 20 МГц → лише 1/6/11 ───
def fig_wifi_overlap():
    W, H = 760, 380
    f = [text(W / 2, 26, "2.4 ГГц Wi-Fi: 14 каналів по 5 МГц, а ширина — 20 МГц", 15.5, INK, "middle", bold=True)]

    # вісь частоти 2400…2483 МГц
    ox, oy = 50, 250
    aw = 660
    f0, f1 = 2400.0, 2484.0
    def fx(mhz):
        return ox + (mhz - f0) / (f1 - f0) * aw
    f.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.4))
    for mhz in (2400, 2420, 2440, 2460, 2484):
        f.append(line(fx(mhz), oy, fx(mhz), oy + 7, color=MUTED, sw=1.1))
        f.append(text(fx(mhz), oy + 22, "%d" % mhz, 9.5, MUTED, "middle"))
    f.append(text(ox + aw / 2, oy + 40, "частота, МГц  (ISM-діапазон 2.400–2.4835 ГГц)", 10.5, MUTED, "middle"))

    # центри каналів 1..13: 2412 + (k-1)*5
    centers = [2412 + (k) * 5 for k in range(13)]
    # бліді контури всіх 13 каналів по 20 МГц (видно перекриття)
    for k, c in enumerate(centers):
        x0, x1 = fx(c - 10), fx(c + 10)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="40" rx="3" fill="none" stroke="#c8ced6" stroke-width="1.0"/>'
                 % (x0, oy - 52, x1 - x0))
        # риска центру + номер
        f.append(line(fx(c), oy - 56, fx(c), oy - 12, color="#c8ced6", sw=0.8))
        f.append(text(fx(c), oy - 60, "%d" % (k + 1), 8, MUTED, "middle"))

    # виділити 1, 6, 11 кольором — три, що НЕ перекриваються
    hot = {1: "#c0392b", 6: "#27ae60", 11: "#2457d6"}
    for ch, col in hot.items():
        c = 2412 + (ch - 1) * 5
        x0, x1 = fx(c - 10), fx(c + 10)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="86" rx="4" fill="%s" stroke="%s" stroke-width="2.2" opacity="0.92"/>'
                 % (x0, oy - 130, x1 - x0, _tint(col), col))
        f.append(text(fx(c), oy - 100, "кан. %d" % ch, 11, col, "middle", bold=True))
        f.append(text(fx(c), oy - 84, "20 МГц", 9, col, "middle"))

    # підпис відстані 25 МГц між 1 і 6
    c1 = 2412; c6 = 2412 + 25
    f.append(line(fx(c1), oy - 144, fx(c6), oy - 144, color=INK, sw=1.3))
    f.append(text((fx(c1) + fx(c6)) / 2, oy - 150, "25 МГц — саме стільки, щоб не перекритися", 9.5, INK, "middle", bold=True))

    f.append(fitbox(ox, oy + 52, aw, 30,
                    "крок між каналами 5 МГц, а ширина 20 МГц → сусіди налазять; вільно «стоять» поряд лише 1, 6, 11",
                    size=11, fill="#eef6ef", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "wifi-overlap.svg"), W, H, *f)


# ── 5. Доплер: діє лише радіальна складова швидкості ──────────────────────────
def fig_doppler_radial():
    W, H = 760, 380
    f = [text(W / 2, 26, "Доплер бере лише радіальну складову швидкості", 15.5, INK, "middle", bold=True)]

    # наземна станція
    sx, sy = W / 2, 320
    f.append(circle(sx, sy, 9, fill=_tint("#27ae60"), stroke="#27ae60", sw=2))
    f.append(text(sx, sy + 26, "наземна станція (приймач)", 10.5, INK, "middle", bold=True))

    # горизонтальна траєкторія апарата
    py = 110
    f.append(line(80, py, 680, py, color=MUTED, sw=1.2, dash="6 5"))
    f.append(text(80, py - 12, "траєкторія апарата (стала висота, стала швидкість v)", 10, MUTED, "start"))

    vlen = 78  # довжина вектора швидкості

    # ── позиція A: наближення (θ малий → радіальна велика) ──
    ax = sx - 210
    f.append(circle(ax, py, 7, fill=_tint("#c0392b"), stroke=POS, sw=2))
    # лінія погляду станція→A
    f.append(line(sx, sy, ax, py, color="#b8bec6", sw=1.1))
    # вектор повної швидкості (горизонтально, праворуч — до точки підльоту)
    f.append(arrow(ax, py, ax + vlen, py, color=INK, sw=2.2))
    f.append(text(ax + vlen / 2, py - 10, "v", 12, INK, "middle", bold=True, italic=True))
    # розклад: радіальна (вздовж променя на станцію) — велика частка
    # напрямок від A до станції:
    import math as _m
    dx, dy = sx - ax, sy - py
    L = _m.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    # проєкція вектора v=(vlen,0) на (ux,uy): scalar = vlen*ux
    proj = vlen * ux
    f.append(arrow(ax, py, ax + proj * ux, py + proj * uy, color=POS, sw=2.2))
    f.append(text(ax + proj * ux * 0.5 + 14, py + proj * uy * 0.5 + 16, "v_рад", 10.5, POS, "middle", bold=True))
    f.append(text(ax, py - 22, "наближення: θ малий", 10, POS, "middle", bold=True))
    f.append(text(ax, py - 36, "cos θ ≈ 1 → повний зсув", 9.5, POS, "middle"))

    # ── позиція B: точка найближчого підльоту (θ=90° → радіальна = 0) ──
    bx = sx
    f.append(circle(bx, py, 7, fill=_tint("#2457d6"), stroke=NEG, sw=2))
    f.append(line(sx, sy, bx, py, color="#b8bec6", sw=1.1))
    # вектор швидкості горизонтальний, лінія погляду вертикальна → перпендикуляр
    f.append(arrow(bx, py, bx + vlen, py, color=INK, sw=2.2))
    f.append(text(bx + vlen / 2, py - 10, "v", 12, INK, "middle", bold=True, italic=True))
    # прямий кут
    f.append('<rect x="%.1f" y="%.1f" width="12" height="12" fill="none" stroke="%s" stroke-width="1.2"/>'
             % (bx + 1, py + 1, NEG))
    f.append(text(bx + 96, py - 24, "точно над головою (θ=90°)", 10, NEG, "middle", bold=True))
    f.append(text(bx + 96, py - 10, "cos θ = 0 → зсуву немає", 9.5, NEG, "middle"))

    f.append(fitbox(90, 244, W - 180, 30,
                    "у формулу входить v·cos θ — складова вздовж променя на приймача; поперечний рух частоти не зсуває",
                    size=11, fill="#eef6ef", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "doppler-radial.svg"), W, H, *f)


# ── 6. Пастка переповнення: f₀·ppm у uint32 «загортається» за модулем 2³² ─────
def fig_int_overflow():
    W, H = 760, 350
    f = [text(W / 2, 26, "Пастка uint32: f₀·ppm не влазить і «загортається»", 15.5, INK, "middle", bold=True)]

    # шкала чисел (умовна — показуємо ПОРЯДКИ, не лінійний масштаб)
    ox, oy = 60, 150
    aw = 640
    f.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.4))
    f.append(text(ox, oy + 50, "0", 10, MUTED, "middle"))

    # позиції трьох чисел (рознесені вручну для наочності порядків)
    x_wrap = ox + 0.16 * aw     # 1.51 млрд — що лишилось після wrap
    x_ceil = ox + 0.30 * aw     # 4.29 млрд — стеля uint32
    x_true = ox + 0.92 * aw     # 96 млрд — справжній добуток

    # зона «за межею uint32» — заштрихована заливка праворуч від стелі
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="20" fill="#fdecea" opacity="0.6"/>'
             % (x_ceil, oy - 10, ox + aw - x_ceil))

    # стеля uint32 — червона пунктирна межа
    f.append(line(x_ceil, oy - 72, x_ceil, oy + 18, color=POS, sw=2.0, dash="5 4"))
    f.append(text(x_ceil, oy + 34, "стеля uint32", 10, POS, "middle", bold=True))
    f.append(text(x_ceil, oy + 48, "4.29 млрд", 9.5, POS, "middle"))

    # справжній добуток 96 млрд — далеко за стелею
    f.append(line(x_true, oy - 6, x_true, oy + 6, color=INK, sw=1.4))
    f.append(text(x_true, oy - 14, "2.4·10⁹ · 40", 10.5, INK, "middle"))
    f.append(text(x_true, oy + 22, "= 96 млрд", 10.5, INK, "middle", bold=True))
    f.append(text(x_true, oy + 36, "(× 22 за стелю)", 9, MUTED, "middle"))

    # стрілка «загортання» від справжнього до залишку
    f.append(arrow(x_true, oy - 42, x_wrap, oy - 42, color=POS, sw=1.6))
    f.append(text((x_true + x_wrap) / 2, oy - 50, "mod 2³² — лишається тільки решта", 10.5, POS, "middle", bold=True))

    # залишок 1.51 млрд
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
             % (x_wrap - 5, oy - 6, x_wrap + 5, oy - 6, x_wrap, oy - 16, POS))
    f.append(text(x_wrap, oy + 48, "лишилось 1.51 млрд", 9.5, POS, "middle"))

    # підсумок-наслідок: дрейф схлопнувся
    f.append(fitbox(110, oy + 76, W - 220, 56,
                    "далі / 1 000 000:   ПРАВИЛЬНО Δf = 96 000 Гц    проти    ХИБНО 1 510 Гц\n"
                    "дрейф вийшов ≈ у 64 рази меншим — канал здається майже без дрейфу, N завищено",
                    size=11.5, fill="#fdecea", stroke=POS, color=INK))

    render(os.path.join(IMG, "int-overflow.svg"), W, H, *f)


if __name__ == "__main__":
    fig_band_as_shelf()
    fig_slot_ledger()
    fig_ppm_drift()
    fig_wifi_overlap()
    fig_doppler_radial()
    fig_int_overflow()
    print("OK: figures written to", IMG)
