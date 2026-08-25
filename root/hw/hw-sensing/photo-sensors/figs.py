# -*- coding: utf-8 -*-
"""Фігури до теми «Фотодавачі».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Три приймачі світла: що саме світло робить у кожному ──────────────────
def fig_three_devices():
    W, H = 760, 380
    f = [text(W / 2, 28, "Те саме світло — три різні відповіді", size=16, bold=True)]

    cards = [
        ("Фоторезистор (LDR)", "#fbeee6", POS,
         "світло народжує вільні носії\nу всьому об'ємі шару",
         "→ опір ПАДАЄ", "повільний · нелінійний · дешевий"),
        ("Фотодіод", "#eef2f8", NEG,
         "фотон у переході вибиває пару;\nполе зриває її в струм",
         "→ дає СТРУМ", "швидкий · лінійний · слабкий сигнал"),
        ("Фототранзистор", "#eef6ef", FIELD,
         "той самий перехід,\nале база підсилює струм",
         "→ дає БІЛЬШИЙ струм", "чутливий · повільніший за діод"),
    ]
    cw, gap = 230, 18
    x = (W - (3 * cw + 2 * gap)) / 2
    top = 58
    for title, fl, col, how, out, foot in cards:
        f.append(rect(x, top, cw, 268, fill=fl, stroke=col, sw=1.8, rx=10))
        f.append(text(x + cw / 2, top + 26, title, size=13.5, bold=True, color=INK))
        f.append(line(x + 14, top + 38, x + cw - 14, top + 38, color=col, sw=1.2))
        # промінь світла, що падає згори
        for k in range(3):
            sx = x + cw / 2 - 26 + k * 26
            f.append(line(sx, top + 52, sx - 8, top + 86, color="#e0a93c", sw=2.2))
        f.append(text(x + cw / 2, top + 50, "☀ світло", size=10.5, color="#b8801f"))
        f.append(mtext(x + cw / 2, top + 112, how, size=11, color=MUTED, lh=1.25))
        b, _, _ = textbox(x + cw / 2, top + 178, out, size=13, fill=BG, stroke=col, bold=True)
        f.append(b)
        f.append(mtext(x + cw / 2, top + 232, foot, size=10.5, color=INK, lh=1.2))
        x += cw + gap
    f.append(text(W / 2, top + 296,
                  "усі троє ловлять той самий фотон — різняться лише тим, що з ним роблять далі",
                  size=12, color=INK, italic=True))
    render(os.path.join(IMG, "three-devices.svg"), W, H, *f)


# ── 2. Фотодіод: два режими роботи на одній ВАХ ──────────────────────────────
def fig_two_modes():
    W, H = 760, 430
    f = [text(W / 2, 28, "Фотодіод: одна деталь — два способи її ввімкнути", size=16, bold=True)]

    # координати ВАХ: 0 у центрі правої половини
    ox, oy = 470, 215
    L, R = 250, 110            # ліве плече (−U), праве плече (+U)
    UP, DN = 120, 130          # верх (+I), низ (−I)
    f.append(line(ox - L, oy, ox + R, oy, color=INK, sw=1.8))        # вісь U
    f.append(line(ox, oy - UP, ox, oy + DN, color=INK, sw=1.8))      # вісь I
    f.append(text(ox + R + 6, oy + 4, "U", size=13, bold=True, color=INK, anchor="start"))
    f.append(text(ox + 8, oy - UP - 2, "I", size=13, bold=True, color=INK, anchor="start"))
    f.append(text(ox - L / 2, oy - UP - 4, "зворотне зміщення (−U)", size=10, color=MUTED))
    f.append(text(ox + R / 2 + 8, oy - UP - 4, "пряме (+U)", size=10, color=MUTED))

    # ВАХ діода при трьох рівнях світла: темнова крива + зсув УНИЗ на фотострум.
    # форма: ліворуч (−U) — рівна поличка (−I_фото); праворуч росте прямий струм угору.
    def iv(shift, color, sw=2.6):
        pts = []
        for i in range(0, 121):
            u = (ox - L) + i * (L + R) / 120.0
            uu = u - ox
            if uu <= 0:
                cur = shift                       # поличка фотоструму під −U
            else:
                cur = shift + (uu ** 1.9) * 0.02  # прямий струм круто вгору
            y = oy - cur
            if y < oy - UP:                       # обрізати по верху полотна
                # знайти точку перетину з верхом — лишити вертикальний хвіст
                pts.append("%.1f,%.1f" % (u, oy - UP))
                break
            pts.append("%.1f,%.1f" % (u, y))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                 % (" ".join(pts), color, sw))

    iv(0, "#c4ccd6")           # темнова (без світла) — проходить через 0
    iv(-58, "#8aa0e0")         # слабке світло
    iv(-104, NEG)              # яскраве світло
    # стрілка «більше світла» вниз по поличці
    f.append(line(ox - L + 26, oy - 6, ox - L + 26, oy + 98, color=POS, sw=1.6, dash="3,3"))
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="1.6"/>'
             % (ox - L + 26, oy + 98, ox - L + 21, oy + 88, ox - L + 31, oy + 88, POS))
    f.append(mtext(ox - L + 44, oy + 56, ["більше", "світла"], size=10, color=POS, lh=1.2))

    # дві робочі точки на ВАХ
    # фотопровідна: ліворуч на яскравій поличці
    px, py = ox - 150, oy + 104
    f.append(circle(px, py, 5, fill=BG, stroke=NEG, sw=2.2))
    f.append(text(px, py - 12, "робота тут (−U)", size=9.5, color=NEG))
    # фотовольтаїчна: точка U>0, I<0 (IV квадрант) — діод сам віддає
    qx, qy = ox + 30, oy + 104
    f.append(circle(qx, qy, 5, fill=BG, stroke=FIELD, sw=2.2))

    # підписи квадрантів (винесено вниз, щоб не налазити)
    f.append(text(ox - L / 2, oy + DN + 22, "поличка фотоструму: I ∝ освітленість",
                  size=10.5, color=NEG))
    f.append(mtext(ox + R / 2 + 14, oy + DN + 22, ["IV кв.: сам", "віддає енергію"],
                   size=9.5, color=FIELD, lh=1.2))

    # дві мини-картки ліворуч: який режим що дає
    sx, sw_ = 40, 200
    f.append(text(sx + sw_ / 2, 70, "режим −U  (фотопровідний)", size=11, bold=True, color=NEG))
    f.append(rect(sx, 80, sw_, 56, fill="#eef2f8", stroke=NEG, sw=1.4, rx=8))
    f.append(mtext(sx + sw_ / 2, 104, ["зворотна напруга розширює перехід",
                                       "→ швидкий і строго лінійний"], size=10, color=INK, lh=1.3))
    f.append(text(sx + sw_ / 2, 172, "режим 0 В  (фотовольтаїчний)", size=11, bold=True, color=FIELD))
    f.append(rect(sx, 182, sw_, 56, fill="#eef6ef", stroke=FIELD, sw=1.4, rx=8))
    f.append(mtext(sx + sw_ / 2, 206, ["напруги нема, діод сам дає струм",
                                       "→ тихий, але повільніший"], size=10, color=INK, lh=1.3))

    f.append(text(W / 2, H - 14,
                  "світло зсуває всю ВАХ униз; де поставити робочу точку — і є вибір режиму",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "two-modes.svg"), W, H, *f)


# ── 3. Чому фототранзистор повільніший за фотодіод ───────────────────────────
def fig_speed():
    W, H = 740, 360
    f = [text(W / 2, 28, "Підсилення коштує швидкості: діод vs транзистор", size=16, bold=True)]

    # дві осі час→відгук
    def axes(ox, oy, title, col):
        axw, axh = 250, 150
        f.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.6))
        f.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.6))
        f.append(text(ox + axw / 2, oy + 22, "час", size=10.5, color=MUTED))
        f.append(text(ox, oy - axh - 8, title, size=12.5, bold=True, color=col))
        # ідеальний стрибок світла (сіра пунктирна сходинка)
        f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" '
                 'fill="none" stroke="#c4ccd6" stroke-width="1.6" stroke-dasharray="4,4"/>'
                 % (ox + 8, oy, ox + 50, oy, ox + 50, oy - axh + 18, ox + axw - 6, oy - axh + 18))
        return ox, oy, axw, axh

    ox, oy, axw, axh = axes(70, 250, "Фотодіод", NEG)
    # швидкий відгук — майже вертикальний фронт
    pts = []
    for i in range(0, 101):
        x = ox + 50 + i * (axw - 56) / 100.0
        t = i / 100.0
        y = oy - (axh - 18) * (1 - 2.718 ** (-t * 9))
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), NEG))
    f.append(text(ox + axw - 6, oy - axh + 34, "мкс", size=10, color=NEG, anchor="end"))
    f.append(text(ox + 120, oy - 6, "слабкий струм", size=10, color=MUTED, anchor="start"))

    ox, oy, axw, axh = axes(420, 250, "Фототранзистор", FIELD)
    # повільний відгук — пологий фронт, але вища поличка (показано вище)
    pts = []
    for i in range(0, 101):
        x = ox + 50 + i * (axw - 56) / 100.0
        t = i / 100.0
        y = oy - (axh - 8) * (1 - 2.718 ** (-t * 2.4))
        pts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), FIELD))
    f.append(text(ox + axw - 6, oy - axh + 24, "десятки–сотні мкс", size=10, color=FIELD, anchor="end"))
    f.append(text(ox + 120, oy - 6, "великий струм", size=10, color=MUTED, anchor="start"))

    f.append(text(W / 2, H - 16,
                  "та сама ємність переходу заряджається крізь підсилення β → фронт розпливається",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "speed.svg"), W, H, *f)


# ── 4. Трансімпедансний підсилювач: струм → напруга ──────────────────────────
def fig_transimpedance():
    W, H = 720, 360
    f = [text(W / 2, 28, "Трансімпедансна схема: струм фотодіода стає напругою", size=16, bold=True)]

    # фотодіод ліворуч
    dx, dy = 110, 175
    f.append(text(dx, dy - 74, "фотодіод", size=11, bold=True, color=NEG))
    # символ діода (трикутник + риска)
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#eaf0fd" stroke="%s" stroke-width="1.8"/>'
             % (dx - 16, dy - 16, dx - 16, dy + 16, dx + 12, dy, NEG))
    f.append(line(dx + 12, dy - 16, dx + 12, dy + 16, color=NEG, sw=2.4))
    # стрілки світла
    for k in range(2):
        f.append(line(dx - 44 + k * 12, dy - 40, dx - 30 + k * 12, dy - 18, color="#e0a93c", sw=2.2))
    f.append(text(dx - 40, dy - 44, "☀", size=13, color="#b8801f"))
    # провід від діода до інвертувального входу
    f.append(line(dx + 12, dy, 300, dy, color=LINE, sw=1.8))
    f.append(line(dx - 16, dy, dx - 16, 250, color=LINE, sw=1.8))
    f.append(line(dx - 16, 250, 470, 250, color=LINE, sw=1.8))     # земля до виходу/ОП+

    # ОП — трикутник
    ax_, ay = 300, 130
    f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#eef6ef" stroke="%s" stroke-width="1.8"/>'
             % (ax_, ay, ax_, ay + 90, ax_ + 90, ay + 45, FIELD))
    f.append(text(ax_ + 28, ay + 50, "ОП", size=13, bold=True, color=FIELD))
    f.append(text(ax_ - 6, ay + 20, "−", size=16, bold=True, color=NEG, anchor="end"))
    f.append(text(ax_ - 6, ay + 74, "+", size=16, bold=True, color=POS, anchor="end"))
    # + вхід на землю
    f.append(line(ax_ - 30, ay + 70, ax_, ay + 70, color=LINE, sw=1.8))
    f.append(line(ax_ - 30, ay + 70, ax_ - 30, 250, color=LINE, sw=1.8))
    # вихід
    f.append(line(ax_ + 90, ay + 45, 560, ay + 45, color=LINE, sw=1.8))
    f.append(text(590, ay + 49, "Uвих", size=12, bold=True, color=INK, anchor="middle"))

    # резистор зворотного зв'язку Rf поверх ОП
    f.append(line(300, dy, 300, 90, color=LINE, sw=1.8))
    f.append(line(300, 90, 430, 90, color=LINE, sw=1.8))
    f.append(rect(345, 80, 60, 20, fill=BG, stroke=POS, sw=1.6, rx=3))
    f.append(text(375, 94, "Rf", size=11, bold=True, color=POS))
    f.append(line(430, 90, 430, ay + 45, color=LINE, sw=1.8))
    f.append(line(430, ay + 45, 470, ay + 45, color=LINE, sw=1.8))

    # формула й суть
    b, _, _ = textbox(560, 150, "Uвих = I · Rf", size=13, fill="#fbeee6", stroke=POS, bold=True)
    f.append(b)
    f.append(mtext(W / 2, 300,
                   ["вхід «−» тримається на нулі (віртуальна земля) → діод працює при 0 В, увесь струм тече крізь Rf",
                    "Rf задає коефіцієнт: великий Rf — велика напруга з малого струму, але вужча смуга"],
                   size=11, color=INK, lh=1.4))
    render(os.path.join(IMG, "transimpedance.svg"), W, H, *f)


# ── 5. Спектральна чутливість: відгук залежить від довжини хвилі ─────────────
def fig_spectral():
    W, H = 740, 380
    f = [text(W / 2, 28, "Кожен давач «бачить» свій діапазон довжин хвиль", size=16, bold=True)]

    ox, oy = 80, 300
    axw, axh = 600, 220
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw / 2, oy + 42, "довжина хвилі  λ  (нм)", size=12, color=INK))
    f.append(mtext(ox - 52, oy - axh / 2, ["відносний", "відгук"], size=11, color=INK, lh=1.2))

    # шкала довжин хвиль + кольорова смужка видимого діапазону
    band = [("УФ", 300, 400, "#b19cd9"), ("видиме", 400, 700, None),
            ("ближнє ІЧ", 700, 1100, "#d98c8c")]
    lam0, lam1 = 300, 1100
    def X(lam):
        return ox + (lam - lam0) / (lam1 - lam0) * axw
    # смужка видимого спектра
    vis = [(400, "#7a4fd0"), (450, "#3753d9"), (500, "#27ae60"),
           (560, "#c9c021"), (600, "#e08a3c"), (660, "#c0392b"), (700, "#8a2b22")]
    for i in range(len(vis) - 1):
        l0, c0 = vis[i]
        l1, c1 = vis[i + 1]
        f.append(rect(X(l0), oy + 6, X(l1) - X(l0), 12, fill=c0, stroke="none", sw=0, rx=0))
    for lam in (300, 400, 500, 700, 900, 1100):
        f.append(line(X(lam), oy, X(lam), oy + 5, color=INK, sw=1.4))
        f.append(text(X(lam), oy + 22, str(lam), size=10, color=MUTED))

    # криві відгуку (дзвони)
    def bell(center, width, peak, color, sw=2.6, dash=None):
        pts = []
        for lam in range(lam0, lam1 + 1, 8):
            y = oy - axh * peak * 2.718 ** (-((lam - center) / width) ** 2)
            pts.append("%.1f,%.1f" % (X(lam), y))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                 % (" ".join(pts), color, sw, d))

    bell(560, 90, 0.62, FIELD, dash="6,4")     # людське око (видиме)
    bell(900, 230, 0.95, NEG)                   # кремнієвий фотодіод (пік у ближньому ІЧ)
    bell(560, 150, 0.5, POS)                    # типовий LDR (CdS — близько до ока)

    f.append(text(X(900) + 4, oy - axh * 0.95 - 6, "кремнієвий фотодіод", size=11, bold=True, color=NEG, anchor="middle"))
    f.append(text(X(560), oy - axh * 0.62 - 8, "око людини", size=10.5, color=FIELD, anchor="middle"))
    f.append(text(X(470), oy - axh * 0.5 - 6, "LDR (CdS)", size=10.5, bold=True, color=POS, anchor="middle"))

    f.append(text(W / 2, H - 12,
                  "кремній найкраще «бачить» ближнє ІЧ — тому ІЧ-пульт працює, а далеке ІЧ для нього невидиме",
                  size=11, color=INK, italic=True))
    render(os.path.join(IMG, "spectral.svg"), W, H, *f)


if __name__ == "__main__":
    fig_three_devices()
    fig_two_modes()
    fig_speed()
    fig_transimpedance()
    fig_spectral()
    print("OK: 5 figures ->", IMG)
