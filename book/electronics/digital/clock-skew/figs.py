# -*- coding: utf-8 -*-
"""Фігури до теми «Перекіс тактового сигналу (clock skew)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).
Підпис фігури несе .md, тож великого заголовка всередині малюнка немає (§5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

CLK  = "#8e44ad"   # тактова мережа — фіолетовий
DATA = FIELD       # дані — зелений
LATE = POS         # «пізно» / небезпека — червоний
EARLY = NEG        # «рано» — синій


def ff(x, y, label, w=54, h=64, accent=INK):
    """Прямокутник тригера з підписом і клиноподібним входом такту знизу."""
    out = [rect(x, y, w, h, fill=BG, stroke=accent, sw=2, rx=6)]
    out.append(text(x + w / 2, y + h / 2 + 5, label, size=15, color=accent, bold=True))
    # трикутник-вхід такту на нижній грані
    cx = x + w / 2
    out.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="none" stroke="%s" stroke-width="1.6"/>'
               % (cx - 8, y + h, cx, y + h - 11, cx + 8, y + h, accent))
    return "".join(out), cx, y + h


def buf(cx, cy, r=13, color=CLK):
    """Трикутник-буфер такту вершиною вправо."""
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.5" '
            'opacity="0.9"/>' % (cx - r, cy - r, cx + r, cy, cx - r, cy + r, "#ede0f5", color))


# ── Фігура 1: одне джерело такту, нерівні гілки → різний час приходу ──────────
def fig_tree():
    W, H = 760, 360
    parts = []
    # корінь-осцилятор
    root_x, root_y = 70, H / 2
    parts.append(circle(root_x, root_y, 22, fill="#ede0f5", stroke=CLK, sw=2))
    parts.append(text(root_x, root_y + 5, "CLK", size=12, color=CLK, bold=True))
    parts.append(text(root_x, root_y + 42, "джерело", size=11, color=MUTED))

    # вузол розгалуження
    fork_x = 180
    parts.append(line(root_x + 22, root_y, fork_x, root_y, color=CLK, sw=2.4))
    parts.append(circle(fork_x, root_y, 5, fill=CLK, stroke=CLK, sw=1))

    # верхня гілка — коротка, один буфер: приходить РАНО
    top_y = 96
    parts.append(line(fork_x, root_y, fork_x, top_y, color=CLK, sw=2.4))
    parts.append(line(fork_x, top_y, 300, top_y, color=CLK, sw=2.4))
    parts.append(buf(320, top_y))
    ff_a, cax, cay = ff(474, top_y - 32, "FF A", accent=INK)
    # провід від буфера спускається до рівня нижньої грані й заходить у трикутник-вхід знизу
    parts.append(line(333, top_y, 440, top_y, color=CLK, sw=2.4))
    parts.append(line(440, top_y, 440, cay + 14, color=CLK, sw=2.4))
    parts.append(line(440, cay + 14, cax, cay + 14, color=CLK, sw=2.4))
    parts.append(line(cax, cay + 14, cax, cay, color=CLK, sw=2.4))
    parts.append(ff_a)
    box, _, _ = textbox(600, top_y, "приходить РАНО\n(коротка гілка)", size=12,
                        color=EARLY, stroke=EARLY, fill="#eaf0fd")
    parts.append(box)

    # нижня гілка — довга, звивиста, два буфери, велике віяло: приходить ПІЗНО
    bot_y = 264
    parts.append(line(fork_x, root_y, fork_x, bot_y, color=CLK, sw=2.4))
    # звивистий довгий провід
    parts.append('<path d="M%d %d L240 %d L240 %d L300 %d" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (fork_x, bot_y, bot_y, bot_y + 26, bot_y + 26, CLK))
    parts.append(buf(320, bot_y + 26))
    parts.append(line(333, bot_y + 26, 360, bot_y + 26, color=CLK, sw=2.4))
    parts.append(buf(380, bot_y + 26))
    ff_b, cbx, cby = ff(474, bot_y - 6, "FF B", accent=INK)
    # зайве віяло-навантаження на цій гілці (гілка тягне зайву ємність — ще пізніше)
    parts.append(line(410, bot_y + 26, 410, bot_y + 6, color=CLK, sw=1.8))
    parts.append(circle(410, bot_y + 26, 4, fill=CLK, stroke=CLK, sw=1))
    parts.append(circle(410, bot_y + 6, 4, fill=BG, stroke=CLK, sw=1.4))
    # провід заходить у трикутник-вхід FF B знизу
    parts.append(line(393, bot_y + 26, 440, bot_y + 26, color=CLK, sw=2.4))
    parts.append(line(440, bot_y + 26, 440, cby + 14, color=CLK, sw=2.4))
    parts.append(line(440, cby + 14, cbx, cby + 14, color=CLK, sw=2.4))
    parts.append(line(cbx, cby + 14, cbx, cby, color=CLK, sw=2.4))
    parts.append(ff_b)
    box2, _, _ = textbox(600, bot_y + 20, "приходить ПІЗНО\n(довша гілка,\nбільше буферів)", size=12,
                         color=LATE, stroke=LATE, fill="#fdecea")
    parts.append(box2)

    render(os.path.join(IMG, "clock-tree.svg"), W, H, *parts)


# ── Фігура 2: один фронт джерела, зсунутий фронт приймача → знак перекосу ─────
def fig_sign():
    W, H = 720, 300
    parts = []
    x0, x1 = 90, 660
    # два ряди: launch (джерело) і capture (приймач)
    yL, yC = 92, 214
    per = 150      # умовний період для орієнтиру
    edgeL = 250    # фронт запуску
    skew = 70      # перекіс
    edgeC = edgeL + skew

    def clkrow(y, edge, color, label, sub):
        seg = []
        # ідеалізований меандр із одним активним фронтом на edge
        lo, hi = y + 26, y - 20
        seg.append(text(x0 - 8, y - 26, label, size=13, color=color, bold=True, anchor="start"))
        seg.append(text(x0 - 8, y - 10, sub, size=11, color=MUTED, anchor="start"))
        pts = [(x0, lo), (edge - 60, lo), (edge - 60, hi), (edge, hi),
               (edge, lo), (edge + 90, lo), (edge + 90, hi), (x1, hi)]
        d = "M%.1f %.1f " % pts[0] + " ".join("L%.1f %.1f" % p for p in pts[1:])
        seg.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, color))
        # позначка активного фронту
        seg.append(line(edge, hi - 6, edge, lo + 18, color=color, sw=1.4, dash="4 4"))
        seg.append(circle(edge, hi, 4, fill=color, stroke=color, sw=1))
        return "".join(seg)

    parts.append(clkrow(yL, edgeL, EARLY, "такт у джерелі (launch)", "фронт приходить першим"))
    parts.append(clkrow(yC, edgeC, LATE, "такт у приймачі (capture)", "той самий фронт — пізніше"))

    # виміряти перекіс між двома фронтами
    ymid = (yL + yC) / 2
    parts.append(line(edgeL, yL - 20, edgeL, yC + 26, color=EARLY, sw=1.2, dash="3 4"))
    parts.append(line(edgeC, yL - 20, edgeC, yC + 26, color=LATE, sw=1.2, dash="3 4"))
    parts.append(arrow(edgeL, ymid, edgeC, ymid, color=INK, sw=1.8))
    parts.append(arrow(edgeC, ymid, edgeL, ymid, color=INK, sw=1.8))
    b, _, _ = textbox((edgeL + edgeC) / 2, ymid - 24,
                      "перекіс  t_skew = t_capture − t_launch  > 0", size=12, bold=True)
    parts.append(b)

    render(os.path.join(IMG, "skew-sign.svg"), W, H, *parts)


# ── Фігура 3: двобічність — перекіс двигає бюджет setup і hold у протилежні боки
def fig_two_sided():
    W, H = 720, 340
    parts = []
    x0, x1 = 60, 660
    # вісь часу з двома фронтами приймача (setup) і одним (hold)
    axis_y = 150
    T = 300
    e0 = 150            # поточний фронт
    e1 = e0 + T         # наступний фронт
    parts.append(line(x0, axis_y, x1, axis_y, color=MUTED, sw=1.4))
    for e, lab in [(e0, "фронт n"), (e1, "фронт n+1")]:
        parts.append(line(e, axis_y - 46, e, axis_y + 46, color=INK, sw=2))
        parts.append(text(e, axis_y - 54, lab, size=12, color=INK, bold=True))

    # HOLD-вікно одразу після поточного фронту — перекіс його РОЗШИРЮЄ
    hw = 40
    sk = 34
    parts.append(rect(e0, axis_y + 6, hw, 22, fill="#fdecea", stroke=LATE, sw=1.4))
    parts.append(text(e0 + hw / 2, axis_y + 21, "hold", size=11, color=LATE))
    parts.append(rect(e0 + hw, axis_y + 6, sk, 22, fill="#fdecea", stroke=LATE, sw=1.4, rx=3))
    parts.append(text(e0 + hw + sk / 2, axis_y + 21, "+skew", size=10, color=LATE))
    b1, _, _ = textbox(e0 + 150, axis_y + 78,
                       "приймач тактується ПІЗНІШЕ → нове значення\nдістає фору → вимога hold ЗРОСТАЄ на t_skew",
                       size=11, color=LATE, stroke=LATE, fill="#fdecea")
    parts.append(b1)

    # SETUP-дедлайн перед наступним фронтом — перекіс приймача його ВІДСУВАЄ (дає час)
    sw_win = 46
    parts.append(rect(e1 - sw_win, axis_y - 28, sw_win, 22, fill="#eaf0fd", stroke=EARLY, sw=1.4))
    parts.append(text(e1 - sw_win / 2, axis_y - 13, "setup", size=11, color=EARLY))
    parts.append(rect(e1, axis_y - 28, sk, 22, fill="#e8f6ee", stroke=DATA, sw=1.4, rx=3))
    parts.append(text(e1 + sk / 2, axis_y - 13, "+skew", size=10, color=FIELD))
    parts.append(arrow(e1, axis_y - 40, e1 + sk, axis_y - 40, color=FIELD, sw=1.8))
    b2, _, _ = textbox(e1 - 20, axis_y - 92,
                       "той самий пізній фронт зсуває й дедлайн setup\nправоруч → на довгий шлях є +t_skew часу",
                       size=11, color=FIELD, stroke=FIELD, fill="#e8f6ee")
    parts.append(b2)

    render(os.path.join(IMG, "skew-two-sided.svg"), W, H, *parts)


# ── Фігура 4 (вставка hist): доля перекосу в періоді росла з масштабом ────────
def fig_skew_budget():
    """Стовпчики: період такту падає, а перекіс лишається/росте абсолютно —
    тож його ДОЛЯ в періоді підскакує, поки він з дріб'язку не стає першорядним."""
    W, H = 720, 360
    parts = []
    base_y = 286          # спільна основа стовпчиків
    x0 = 96
    gap = 196
    barw = 96
    # (підпис, повний період px, частка перекосу 0..1)
    eras = [
        ("рання епоха\nвеликий період", 210, 0.04, MUTED),
        ("масштабування\nперіод падає", 130, 0.18, "#b7791f"),
        ("високі частоти\nперекіс тисне", 74, 0.34, LATE),
    ]
    for i, (lab, ph, frac, col) in enumerate(eras):
        x = x0 + i * gap
        # повний період (світлий стовпчик — «дозволений» час перегону)
        parts.append(rect(x, base_y - ph, barw, ph, fill="#eef1f6", stroke=MUTED, sw=1.4, rx=4))
        # частка, з'їдена перекосом (згори, червоняста)
        sh = ph * frac
        parts.append(rect(x, base_y - ph, barw, sh, fill="#fdecea", stroke=col, sw=1.6, rx=4))
        parts.append(text(x + barw / 2, base_y - ph + sh / 2 + 4,
                          "%d%%" % round(frac * 100), size=13, color=col, bold=True))
        # підпис періоду знизу
        parts.append(mtext(x + barw / 2, base_y + 22, lab, size=11, color=col, bold=(i == 2)))
    # спільна основа й вісь
    parts.append(line(x0 - 20, base_y, x0 + 2 * gap + barw + 20, base_y, color=INK, sw=1.6))
    parts.append(text(x0 - 30, base_y - 150, "період такту", size=12, color=MUTED,
                      anchor="middle"))
    # стрілка тренду згори
    parts.append(arrow(x0 + barw / 2, 46, x0 + 2 * gap + barw / 2, 46, color=LATE, sw=2))
    b, _, _ = textbox((x0 + x0 + 2 * gap) / 2 + barw / 2, 30,
                      "той самий перекіс з'їдає дедалі більшу частку періоду", size=12,
                      color=LATE, stroke=LATE, fill="#fdecea", bold=True)
    parts.append(b)
    render(os.path.join(IMG, "skew-budget-growth.svg"), W, H, *parts)


# ── Фігура 5 (вставка hist): H-дерево — симетрія дає рівні шляхи ──────────────
def fig_htree():
    """Рекурсивна «H»: від кореня до кожного листка — однакова довжина дроту,
    тож (за лінійною моделлю) однаковий час приходу. Геометрія проти перекосу."""
    W, H = 560, 340
    parts = []
    cx, cy = W / 2, 158       # центр трохи вище, щоб лишити місце під підпис
    def H_shape(cx, cy, arm, depth):
        seg = []
        half = arm / 2
        # вертикальні стійки «H»
        seg.append(line(cx - half, cy - half, cx - half, cy + half, color=CLK, sw=2.2))
        seg.append(line(cx + half, cy - half, cx + half, cy + half, color=CLK, sw=2.2))
        # горизонтальна перекладина
        seg.append(line(cx - half, cy, cx + half, cy, color=CLK, sw=2.2))
        corners = [(cx - half, cy - half), (cx - half, cy + half),
                   (cx + half, cy - half), (cx + half, cy + half)]
        if depth > 0:
            for (x, y) in corners:
                seg.extend(H_shape(x, y, arm / 2, depth - 1))
        else:
            for (x, y) in corners:
                seg.append(circle(x, y, 4.5, fill="#ede0f5", stroke=CLK, sw=1.6))
        return seg
    parts.extend(H_shape(cx, cy, 128, 2))
    # корінь у центрі
    parts.append(circle(cx, cy, 9, fill=CLK, stroke=CLK, sw=1))
    parts.append(text(cx + 46, cy - 4, "корінь", size=11, color=CLK, bold=True, anchor="start"))
    b, _, _ = textbox(cx, H - 24,
                      "від кореня до кожного листка — рівна довжина → рівний час приходу",
                      size=11, color=CLK, stroke=CLK, fill="#ede0f5")
    parts.append(b)
    render(os.path.join(IMG, "h-tree.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_tree()
    fig_sign()
    fig_two_sided()
    fig_skew_budget()
    fig_htree()
    print("OK: clock-tree.svg, skew-sign.svg, skew-two-sided.svg, "
          "skew-budget-growth.svg, h-tree.svg")
