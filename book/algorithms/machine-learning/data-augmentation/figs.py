# -*- coding: utf-8 -*-
"""Фігури до теми «Аугментація даних». Чистий Python, svgkit зі scripts/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def drone(cx, cy, s=1.0, ink=INK, flip=False, rot=0.0, dim=False):
    """Спрощений силует квадрокоптера в групі з поворотом/дзеркалом/затемненням."""
    col = MUTED if dim else ink
    sw = 2.0
    body = []
    # рама-хрест
    body.append(line(cx - 26*s, cy - 26*s, cx + 26*s, cy + 26*s, color=col, sw=sw))
    body.append(line(cx + 26*s, cy - 26*s, cx - 26*s, cy + 26*s, color=col, sw=sw))
    # центр
    body.append(rect(cx - 9*s, cy - 9*s, 18*s, 18*s, fill=BG, stroke=col, sw=sw, rx=3))
    # ротори
    for dx, dy in [(-26, -26), (26, -26), (-26, 26), (26, 26)]:
        body.append(circle(cx + dx*s, cy + dy*s, 9*s, fill=BG, stroke=col, sw=sw))
    # маркер «ніс» (щоб було видно дзеркало/поворот) — стрілка вгору
    body.append(line(cx, cy, cx, cy - 30*s, color=POS, sw=sw + 0.5))
    body.append(text(cx + (7 if not flip else -7)*s, cy - 22*s, "N", size=int(11*s), color=POS, bold=True))
    inner = "".join(body)
    tf = []
    if flip:
        tf.append("translate(%.1f,0) scale(-1,1) translate(%.1f,0)" % (2*cx, -2*cx))
    if rot:
        tf.append("rotate(%.1f %.1f %.1f)" % (rot, cx, cy))
    if tf:
        return '<g transform="%s">%s</g>' % (" ".join(tf), inner)
    return inner


def fig_one_to_many():
    """Один кадр → багато варіантів, усі з тим самим ярликом «ціль»."""
    W, H = 760, 430
    frags = [text(W/2, 26, "Один кадр → багато прикладів (ярлик той самий)", size=17, bold=True)]
    # оригінал ліворуч, у зеленій рамці
    ox, oy = 120, 200
    frags.append(rect(ox - 70, oy - 70, 140, 140, fill="#eafaf1", stroke=FIELD, sw=2.5, rx=10))
    frags.append(drone(ox, oy, 1.0))
    frags.append(text(ox, oy + 96, "оригінал (1 фото)", size=13, bold=True))
    frags.append(text(ox, oy + 116, "ярлик: «ціль»", size=12, color=FIELD, bold=True))
    # стрілка «×N»
    frags.append(arrow(ox + 78, oy, ox + 150, oy, color=INK, sw=2.2))
    box, _, _ = textbox(ox + 190, oy - 92, "× багато", size=13, bold=True, fill="#fdf6e3", stroke=POS)
    frags.append(box)
    # чотири похідні праворуч (сітка 2×2)
    gx, gy, dx, dy = 430, 130, 155, 150
    cells = [
        ("віддзеркалення", dict(flip=True)),
        ("поворот", dict(rot=-14)),
        ("обрізка + масштаб", dict(s=1.28)),
        ("затемнення", dict(dim=True)),
    ]
    for i, (name, kw) in enumerate(cells):
        r, c = divmod(i, 2)
        px, py = gx + c*dx, gy + r*dy
        frags.append(rect(px - 62, py - 58, 124, 116, fill=BG, stroke=LINE, sw=1.5, rx=8))
        frags.append(drone(px, py, kw.get('s', 0.82), flip=kw.get('flip', False),
                            rot=kw.get('rot', 0.0), dim=kw.get('dim', False)))
        frags.append(text(px, py + 50, name, size=11, bold=True, color=MUTED))
        frags.append(text(px, py + 67, "«ціль»", size=10, color=FIELD, bold=True))
    render(os.path.join(OUT, 'one-to-many.svg'), W, H, *frags)


def fig_label_boundary():
    """Межа: що зберігає ярлик, а що його руйнує."""
    W, H = 720, 360
    frags = [text(W/2, 26, "Межа аугментації: ярлик мусить лишитися правдою", size=17, bold=True)]
    # ліва колонка — зберігає (зелена)
    lx = 200
    frags.append(rect(30, 52, 320, 280, fill="#f2fbf6", stroke=FIELD, sw=2, rx=10))
    frags.append(text(lx, 78, "✓ ярлик зберігається", size=14, bold=True, color=FIELD))
    ok_rows = [
        ("«6», нахилена на 10°", "= «6»"),
        ("знак STOP, віддзеркалений", "= STOP"),
        ("кіт удень / у сутінках", "= кіт"),
    ]
    for i, (a, b) in enumerate(ok_rows):
        yy = 118 + i*66
        frags.append(fitbox(60, yy, 190, 44, a, size=12, fill=BG, stroke=FIELD))
        frags.append(arrow(255, yy + 22, 285, yy + 22, color=FIELD, sw=2))
        frags.append(text(320, yy + 27, b, size=13, bold=True, color=FIELD))
    # права колонка — руйнує (червона)
    rx = 530
    frags.append(rect(370, 52, 320, 280, fill="#fdf2f0", stroke=POS, sw=2, rx=10))
    frags.append(text(rx, 78, "✗ ярлик стає брехнею", size=14, bold=True, color=POS))
    bad_rows = [
        ("«6», перевернута", "→ «9»"),
        ("літера «b», дзеркало", "→ «d»"),
        ("родимка, розтягнута", "→ інша форма"),
    ]
    for i, (a, b) in enumerate(bad_rows):
        yy = 118 + i*66
        frags.append(fitbox(400, yy, 190, 44, a, size=12, fill=BG, stroke=POS))
        frags.append(arrow(595, yy + 22, 625, yy + 22, color=POS, sw=2))
        frags.append(text(660, yy + 27, b, size=12, bold=True, color=POS))
    render(os.path.join(OUT, 'label-boundary.svg'), W, H, *frags)


def fig_pipeline():
    """Де живе аугментація: на льоту, лише над train, щоепохи інша."""
    W, H = 740, 340
    frags = [text(W/2, 26, "Аугментація живе між даними й моделлю — тільки над train", size=16, bold=True)]
    # train гілка
    y1 = 120
    b1, _, _ = textbox(90, y1, ["train", "(N фото)"], size=13, bold=True, fill="#eafaf1", stroke=FIELD)
    frags.append(b1)
    frags.append(arrow(150, y1, 215, y1, sw=2))
    aug, _, _ = textbox(300, y1, ["аугментатор", "щоепохи — новий"], size=12, bold=True,
                        fill="#fdf6e3", stroke=POS)
    frags.append(aug)
    frags.append(arrow(392, y1, 470, y1, sw=2))
    m, _, _ = textbox(560, y1, ["модель", "(навчання)"], size=13, bold=True, fill=FILL, stroke=INK)
    frags.append(m)
    # цикл-стрілка «щоепохи»
    frags.append(line(300, y1 + 34, 300, y1 + 60, color=POS, sw=1.6, dash="4,3"))
    frags.append(text(300, y1 + 78, "епоха 1: ліва-віддзеркалена…", size=10, color=MUTED))
    frags.append(text(300, y1 + 94, "епоха 2: обрізана, темніша…", size=10, color=MUTED))
    # val/test гілка — БЕЗ аугментації
    y2 = 260
    b2, _, _ = textbox(90, y2, ["val / test"], size=13, bold=True, fill="#eef2ff", stroke=NEG)
    frags.append(b2)
    frags.append(arrow(150, y2, 470, y2, sw=2, color=NEG))
    frags.append(text(300, y2 - 14, "БЕЗ аугментації — оригінали", size=12, bold=True, color=NEG))
    m2, _, _ = textbox(560, y2, ["модель", "(оцінка)"], size=13, bold=True, fill=FILL, stroke=INK)
    frags.append(m2)
    render(os.path.join(OUT, 'aug-pipeline.svg'), W, H, *frags)


def fig_crop_2048():
    """Звідки 2048: вікно 224 ковзає по кадру 256 → 33×33 позицій, ×2 дзеркала."""
    W, H = 760, 470
    frags = [text(W/2, 26, "Звідки множник 2048: ковзне вікно 224 по кадру 256", size=17, bold=True)]

    # ── великий кадр 256 з вікном 224 ліворуч ──
    ox, oy = 60, 70            # лівий-верхній кут кадру-256
    S = 250                    # намальований бік кадру (px на екрані)
    frags.append(rect(ox, oy, S, S, fill="#f4f6f8", stroke=LINE, sw=2, rx=4))
    frags.append(text(ox + S/2, oy - 12, "кадр 256×256", size=13, bold=True))
    # вікно 224 у певній позиції (зсув 20 з 32 можливих)
    win = S * 224.0 / 256.0    # бік вікна на екрані
    off = (S - win) * 20.0 / 32.0
    wx, wy = ox + off, oy + off
    frags.append(rect(wx, wy, win, win, fill="#eafaf1", stroke=FIELD, sw=2.5, rx=3))
    frags.append(text(wx + win/2, wy + win/2 + 5, "вікно 224×224", size=12, bold=True, color=FIELD))
    # діапазон зсуву по горизонталі: 0…32 (короткий відрізок + винесений підпис)
    ay = oy + S + 24
    frags.append(line(ox, ay, ox + (S - win), ay, color=POS, sw=2))
    frags.append(line(ox, ay - 5, ox, ay + 5, color=POS, sw=2))
    frags.append(line(ox + (S - win), ay - 5, ox + (S - win), ay + 5, color=POS, sw=2))
    frags.append(text(ox, ay + 20, "зсув x: 0…32  →  33 позиції", size=12, bold=True, color=POS, anchor="start"))
    # діапазон зсуву по вертикалі
    axx = ox + S + 16
    frags.append(line(axx, oy, axx, oy + (S - win), color=NEG, sw=2))
    frags.append(line(axx - 5, oy, axx + 5, oy, color=NEG, sw=2))
    frags.append(line(axx - 5, oy + (S - win), axx + 5, oy + (S - win), color=NEG, sw=2))
    frags.append(text(axx + 8, oy + (S - win)/2, "зсув y: 0…32", size=12, bold=True, color=NEG, anchor="start"))

    # ── арифметика праворуч ──
    rx = 500
    frags.append(text(rx, 96, "Рахунок", size=15, bold=True, anchor="start"))
    rows = [
        "по горизонталі:  256 − 224 = 32",
        "позицій по осі:  32 + 1 = 33",
        "усіх обрізків:   33 × 33 = 1089",
        "+ дзеркало:      × 2",
        "разом варіантів: ≈ 2048",
    ]
    for i, r in enumerate(rows):
        yy = 130 + i*34
        col = FIELD if i == len(rows) - 1 else INK
        bold = i == len(rows) - 1
        frags.append(text(rx, yy, r, size=13, bold=bold, color=col, anchor="start"))
    # рамка-підсумок
    b, _, _ = textbox(rx + 118, 330, ["з 1 кадру —", "≈ 2048 прикладів"], size=14, bold=True,
                      fill="#eafaf1", stroke=FIELD)
    frags.append(b)
    frags.append(text(rx, 392, "(автори рахують 32²·2 = 2048;", size=11, color=MUTED, anchor="start"))
    frags.append(text(rx, 408, "різниця з 33² — дрібниця для оцінки)", size=11, color=MUTED, anchor="start"))
    render(os.path.join(OUT, 'crop-2048.svg'), W, H, *frags)


def fig_ilsvrc_gap():
    """Розрив ILSVRC-2012: 15.3% top-5 у AlexNet проти 26.2% у другого місця."""
    W, H = 640, 380
    frags = [text(W/2, 26, "ImageNet 2012: обрив у таблиці помилок (top-5)", size=17, bold=True)]

    base_y = 320            # нульова лінія стовпчиків
    scale = 9.0            # px на 1% помилки
    def bar(cx, err, label, sub, color, fillc):
        h = err * scale
        x = cx - 62
        out = rect(x, base_y - h, 124, h, fill=fillc, stroke=color, sw=2, rx=4)
        out += text(cx, base_y - h - 12, "%.1f%%" % err, size=18, bold=True, color=color)
        out += text(cx, base_y + 20, label, size=14, bold=True)
        out += text(cx, base_y + 38, sub, size=11, color=MUTED)
        return out

    # вісь
    frags.append(line(70, base_y, 590, base_y, color=INK, sw=1.6))
    for pct in (0, 10, 20, 30):
        yy = base_y - pct*scale
        frags.append(line(66, yy, 70, yy, color=MUTED, sw=1.2))
        frags.append(text(56, yy + 4, "%d%%" % pct, size=10, color=MUTED, anchor="end"))

    frags.append(bar(210, 15.3, "AlexNet (1-ше)", "глибока згорткова", FIELD, "#eafaf1"))
    frags.append(bar(450, 26.2, "2-ге місце", "класичні ручні ознаки", POS, "#fdf2f0"))

    # дужка розриву між 15.3 і 26.2
    y15 = base_y - 15.3*scale
    y26 = base_y - 26.2*scale
    frags.append(line(285, y15, 322, y15, color=INK, sw=1.4, dash="4,3"))
    frags.append(line(322, y15, 322, y26, color=INK, sw=1.6))
    frags.append(line(318, y26, 375, y26, color=INK, sw=1.4, dash="4,3"))
    frags.append(text(330, (y15 + y26)/2 + 4, "розрив ≈ 10.9 в.п.", size=13, bold=True, color=INK, anchor="start"))
    render(os.path.join(OUT, 'ilsvrc-gap.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_one_to_many()
    fig_label_boundary()
    fig_pipeline()
    fig_crop_2048()
    fig_ilsvrc_gap()
    print("figs done")
