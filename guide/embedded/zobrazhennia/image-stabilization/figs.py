# -*- coding: utf-8 -*-
"""Фігури до теми «Стабілізація зображення» (підвіс / OIS / EIS).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Три шари стабілізації на шляху світла ─────────────────────────────────
def fig_three_layers():
    """Шлях сцена→об'єктив→сенсор→кадр→кодек→запис. Три родини стабілізації
    перехоплюють рух у трьох різних точках: підвіс — до об'єктива, OIS —
    усередині, EIS — після кадру."""
    W, H = 880, 360
    f = [text(W / 2, 30, "Три родини стабілізації — три точки на шляху світла", size=17, bold=True)]

    # ланцюг блоків шляху
    stages = ["сцена", "об'єктив", "сенсор", "кадр", "кодек", "запис /\nлінк"]
    bx, by, bw, bh, gap = 40, 150, 118, 56, 22
    centers = []
    for i, s in enumerate(stages):
        x = bx + i * (bw + gap)
        centers.append((x + bw / 2, by))
        f.append(fitbox(x, by, bw, bh, s, size=12, bold=True, fill=FILL, stroke=LINE))
        if i:
            px = bx + (i - 1) * (bw + gap) + bw
            f.append(arrow(px, by + bh / 2, x, by + bh / 2))

    # три виноски-родини під відповідними точками
    # підвіс — перед об'єктивом; OIS — між об'єктивом і сенсором; EIS — після кадру
    def tag(cx, label, sub, col, dy):
        ty = by + bh + dy
        f.append(line(cx, by + bh, cx, ty, color=col, sw=1.6, dash="4 4"))
        f.append(fitbox(cx - 92, ty, 184, 46, label + "\n" + sub,
                        size=11, bold=True, fill=BG, stroke=col, color=col))

    gim_x = (centers[0][0] + centers[1][0]) / 2     # до об'єктива
    ois_x = (centers[1][0] + centers[2][0]) / 2     # усередині (об'єктив↔сенсор)
    eis_x = centers[3][0]                            # після кадру
    tag(gim_x, "ПІДВІС (механічна)", "рухає всю камеру", FIELD, 26)
    tag(ois_x, "OIS (оптична)", "зсуває лінзу / сенсор", NEG, 86)
    tag(eis_x, "EIS (цифрова)", "переставляє пікселі", POS, 26)

    f.append(text(W / 2, H - 16,
                  "що раніше перехоплено рух, то менше шкоди він завдає картинці — але то дорожче залізом",
                  size=12, color=INK))
    return render(os.path.join(IMG, "three-layers.svg"), W, H, *f)


# ── 2. Підвіс: контур тримає камеру, поки рама крутиться ─────────────────────
def fig_gimbal_loop():
    """Рама кренить праворуч — мотор крену докручує камеру ліворуч на той самий
    кут, тож об'єктив лишається рівним. IMU на КАМЕРІ міряє її кут; контролер
    зводить похибку до нуля мотором. Це зворотний зв'язок, де керована величина
    — кут камери, збурення — кидок рами."""
    import math
    W, H = 840, 380
    f = [text(W / 2, 30, "Підвіс: мотор відкручує камеру назустріч кидку рами", size=17, bold=True)]

    # ── зліва: фізична картинка ──
    rx, ry = 175, 210
    # рама, нахилена праворуч
    a = 17 * math.pi / 180.0
    dx, dy = 110 * math.cos(a), 110 * math.sin(a)
    f.append(line(rx - dx, ry - dy, rx + dx, ry + dy, color=MUTED, sw=6))
    f.append(text(rx, ry + 86, "рама нахилилась праворуч", size=11, color=MUTED))
    f.append(text(rx, ry - 98, "мотор крену докрутив камеру ←", size=11, bold=True, color=FIELD))
    # камера — лишається рівною (горизонтальна)
    f.append(rect(rx - 46, ry - 66, 92, 44, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(circle(rx + 30, ry - 44, 11, fill="#fff", stroke=FIELD, sw=2))    # об'єктив
    f.append(text(rx - 16, ry - 40, "камера", size=11, bold=True, color=FIELD))
    f.append(text(rx, ry - 26, "рівна", size=10, color=FIELD))
    # IMU на камері
    f.append(rect(rx - 44, ry - 62, 18, 12, fill=POS, stroke=POS, sw=1))
    f.append(text(rx - 35, ry - 80, "IMU на камері", size=10, bold=True, color=POS))

    # ── справа: контур зворотного зв'язку ──
    ox = 470
    f.append(text(ox + 165, 78, "Контур, що це робить", size=13, bold=True))
    f.append(fitbox(ox, 102, 148, 48, "ціль: камера\nрівна (0°)", size=11, bold=True, fill=FILL, stroke=LINE))
    f.append(minus(ox + 173, 126))
    f.append(arrow(ox + 148, 126, ox + 164, 126))
    f.append(fitbox(ox + 196, 102, 134, 48, "контролер\n(ПІД)", size=11, bold=True, fill="#fbeee6", stroke=POS))
    f.append(arrow(ox + 182, 126, ox + 196, 126))
    f.append(arrow(ox + 263, 150, ox + 263, 190))
    f.append(fitbox(ox + 196, 192, 134, 46, "мотор крену", size=11, bold=True, fill=FILL, stroke=FIELD))
    f.append(arrow(ox + 196, 215, ox + 148, 215))
    f.append(fitbox(ox, 192, 148, 46, "кут камери\n(з її IMU)", size=11, bold=True, fill=FILL, stroke=POS))
    # зворотний зв'язок угору до суматора
    f.append(line(ox + 74, 192, ox + 74, 162, color=LINE, sw=1.5))
    f.append(line(ox + 74, 162, ox + 173, 162, color=LINE, sw=1.5))
    f.append(arrow(ox + 173, 162, ox + 173, 138))
    f.append(text(ox + 165, 268, "збурення — кидок рами; керована величина — кут камери",
                  size=10, color=MUTED))

    f.append(text(W / 2, H - 16,
                  "IMU сидить на КАМЕРІ, не на рамі: контур міряє й виправляє саме той бік, що знімає",
                  size=12, color=INK))
    return render(os.path.join(IMG, "gimbal-loop.svg"), W, H, *f)


# ── 3. EIS: видиме вікно плаває в запасі знятого кадру ───────────────────────
def fig_eis_crop():
    """Сенсор знімає більший кадр, ніж бачить глядач; видиме вікно зсувається
    протилежно руху камери в межах запасу. Поки зсув уміщається — картинка
    нерухома; перевищив запас — край вікна оголює межу й стабілізувати нема чим."""
    W, H = 840, 380
    f = [text(W / 2, 30, "EIS: видиме вікно плаває в запасі знятого кадру", size=17, bold=True)]

    fw, fh = 230, 156
    ww, wh = 150, 100

    def panel(cx, sx, sy, title, sub, ok):
        x0, y0 = cx - fw / 2, 78
        f.append(rect(x0, y0, fw, fh, fill="#f0f2f5", stroke=LINE, sw=1.6))   # знятий кадр
        f.append(text(cx, y0 - 8, title, size=12, bold=True))
        f.append(text(x0 + 6, y0 + 15, "знятий кадр", size=9, color=MUTED, anchor="start"))
        # видиме вікно — затиснуте в межах знятого кадру (за потреби впирається в край)
        wx = cx - ww / 2 + sx
        wy = y0 + (fh - wh) / 2 + sy
        wx = max(x0, min(wx, x0 + fw - ww))
        wy = max(y0, min(wy, y0 + fh - wh))
        col = FIELD if ok else POS
        f.append(rect(wx, wy, ww, wh, fill="#ffffff", stroke=col, sw=3))
        f.append(text(wx + ww / 2, wy + wh / 2 + 4, "видиме вікно", size=11, bold=True, color=col))
        f.append(fitbox(cx - 120, y0 + fh + 12, 240, 34, sub, size=10, bold=False,
                        fill=BG, stroke=col, color=col))

    panel(150, 0, 0, "камера рівна",
          "вікно в центрі запасу", True)
    panel(420, 30, -14, "кидок у межах запасу",
          "вікно поїхало ПРОТИ руху — картинка стоїть", True)
    panel(690, 200, -120, "кидок більший за запас",
          "вікно вперлось у край — гасити нема чим", False)

    f.append(text(W / 2, H - 16,
                  "запас більший → спокійніша картинка, але вужчий кут огляду; сіре поле — те, що EIS «з'їдає» на зсув",
                  size=12, color=INK))
    return render(os.path.join(IMG, "eis-crop.svg"), W, H, *f)


# ── 4. Анатомія Стедікама: маси розведені, центр ваги назовні, кардан у ньому ─
def fig_steadicam_anatomy():
    """Стедікам Брауна: камеру вгорі врівноважують монітор+батареї внизу, маси
    рознесені по вертикалі — і центр ваги «виходить» назовні корпуса, у вільну
    точку. Саме туди ставлять кардан ультранизького тертя: рука крізь
    ізоеластичне плече тримає за нього, а кутові поштовхи руки до камери не
    доходять. Низ трохи важчий за верх — рій стоїть вертикально сам."""
    W, H = 760, 470
    f = [text(W / 2, 30, "Стедікам: рознести маси — і дістати центр ваги назовні", size=17, bold=True)]

    # вертикальна штанга («сани»)
    sx = 300
    top, bot = 96, 392
    f.append(line(sx, top, sx, bot, color=LINE, sw=5))

    # камера вгорі
    f.append(rect(sx - 62, top - 4, 92, 46, fill="#eef6ef", stroke=FIELD, sw=2))
    f.append(circle(sx + 22, top + 19, 11, fill="#fff", stroke=FIELD, sw=2))
    f.append(text(sx - 28, top + 24, "камера", size=11, bold=True, color=FIELD))

    # монітор+батареї внизу (противага, трохи важча)
    f.append(rect(sx - 58, bot - 34, 116, 40, fill=FILL, stroke=LINE, sw=2))
    f.append(text(sx, bot - 18, "монітор + батареї", size=11, bold=True))
    f.append(text(sx, bot - 4, "(противага, низ важчий)", size=9, color=MUTED))

    # центр ваги — назовні корпуса, у середині штанги
    cgy = (top + bot) / 2 + 8
    f.append(circle(sx, cgy, 13, fill="#fdecea", stroke=POS, sw=2.5))
    f.append(circle(sx, cgy, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(sx + 92, cgy - 6, "центр ваги — тут,", size=12, bold=True, color=POS, anchor="middle"))
    f.append(text(sx + 92, cgy + 10, "у вільному просторі", size=12, color=POS, anchor="middle"))

    # кардан у центрі ваги
    f.append(circle(sx, cgy, 26, fill="none", stroke=NEG, sw=2))
    f.append(circle(sx, cgy, 34, fill="none", stroke=NEG, sw=1.4))
    f.append(text(sx - 120, cgy - 6, "кардан низького", size=12, bold=True, color=NEG, anchor="middle"))
    f.append(text(sx - 120, cgy + 10, "тертя — тут", size=12, color=NEG, anchor="middle"))

    # ізоеластичне плече від руки оператора до кардана
    hx = sx - 230
    f.append(rect(hx - 26, cgy - 70, 52, 140, fill="#f0f2f5", stroke=LINE, sw=1.6))
    f.append(text(hx, cgy - 84, "оператор", size=11, bold=True))
    f.append(text(hx, cgy + 88, "(жилет)", size=10, color=MUTED))
    # плече — ламана лінія (пружинне)
    import math
    ax0, ay0 = hx + 26, cgy
    seg = (sx - 34 - ax0) / 4.0
    pts = [(ax0, ay0)]
    for i in range(1, 4):
        pts.append((ax0 + seg * i, ay0 + (10 if i % 2 else -10)))
    pts.append((sx - 34, cgy))
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=FIELD, sw=2.4))
    f.append(text((ax0 + sx) / 2 - 24, cgy + 40, "ізоеластичне плече", size=11, bold=True, color=FIELD))
    f.append(text((ax0 + sx) / 2 - 24, cgy + 56, "(несе вагу, гасить кроки)", size=9, color=MUTED))

    f.append(text(W / 2, H - 18,
                  "рука тримає за кардан у центрі ваги: її кутові поштовхи камери не торкаються — підвіс «розв'язує» картинку від тіла",
                  size=11, color=INK))
    return render(os.path.join(IMG, "steadicam-anatomy.svg"), W, H, *f)


# ── 5. Та сама ідея, дві реалізації: пасивна механіка → активний контур ──────
def fig_passive_to_active():
    """Стедікам тримає камеру масою й пружиною — пасивно, без живлення й
    обчислень: інерція не дає камері крутитися, кардан розв'язує її від руки.
    Безколекторний підвіс викидає масу й пружину й ставить на їхнє місце
    активний контур: IMU міряє кут, мотор прямого приводу відкручує назустріч.
    Одна мета — нерухома камера, — два різні способи її досягти."""
    W, H = 860, 360
    f = [text(W / 2, 30, "Одна ідея — два способи: маса й пружина проти активного контуру", size=16, bold=True)]

    # ── ліва панель: пасивна (Стедікам) ──
    lx = 215
    f.append(rect(40, 70, 350, 230, fill="#f7faf7", stroke=FIELD, sw=1.6))
    f.append(text(lx, 92, "Стедікам (1975): пасивно", size=13, bold=True, color=FIELD))
    f.append(fitbox(lx - 150, 110, 300, 34, "велика рознесена МАСА → інерція не дає камері крутитись",
                    size=11, fill=BG, stroke=FIELD))
    f.append(fitbox(lx - 150, 152, 300, 34, "ПРУЖИНА (плече) → несе вагу, гасить кроки",
                    size=11, fill=BG, stroke=FIELD))
    f.append(fitbox(lx - 150, 194, 300, 34, "КАРДАН → розв'язує камеру від руки",
                    size=11, fill=BG, stroke=FIELD))
    f.append(text(lx, 254, "ні живлення, ні гіроскопа, ні коду", size=11, bold=True, color=INK))
    f.append(text(lx, 276, "ціна: вага й тренована рука оператора", size=10, color=MUTED))

    # ── права панель: активна (безколекторний підвіс) ──
    rx = 645
    f.append(rect(470, 70, 350, 230, fill="#fbeee6", stroke=POS, sw=1.6))
    f.append(text(rx, 92, "Безколекторний підвіс (~2012): активно", size=13, bold=True, color=POS))
    f.append(fitbox(rx - 150, 110, 300, 34, "IMU на камері → міряє кут у реальному часі",
                    size=11, fill=BG, stroke=POS))
    f.append(fitbox(rx - 150, 152, 300, 34, "контролер (ПІД) → рахує, куди й наскільки",
                    size=11, fill=BG, stroke=POS))
    f.append(fitbox(rx - 150, 194, 300, 34, "мотор ПРЯМОГО ПРИВОДУ → відкручує назустріч",
                    size=11, fill=BG, stroke=POS))
    f.append(text(rx, 254, "масу й пружину замінив контур керування", size=11, bold=True, color=INK))
    f.append(text(rx, 276, "ціна: живлення моторів і точне налаштування", size=10, color=MUTED))

    # стрілка-міст між панелями
    f.append(arrow(390, 185, 470, 185, color=NEG, sw=2.4))
    f.append(text(430, 172, "та сама", size=10, bold=True, color=NEG))
    f.append(text(430, 205, "мета", size=10, bold=True, color=NEG))

    f.append(text(W / 2, H - 16,
                  "мета незмінна — камера нерухома, поки тіло рухається; змінився лише спосіб її тримати",
                  size=12, color=INK))
    return render(os.path.join(IMG, "passive-to-active.svg"), W, H, *f)


# ── 6. Прив'язка часу: дві стрічки + автосинхронізація по збігу руху ─────────
def fig_eis_sync():
    """Кадри й відліки гіро — дві стрічки в різних часових світах: між ними
    сталий зсув (offset) і повільний дрейф годинника. Праворуч — як зсув
    знаходять автоматично: криву руху по гіро ковзають уздовж кривої руху по
    відео, доки вони не накладуться (мінімум розбіжності)."""
    import math
    W, H = 880, 410
    f = [text(W / 2, 30, "Прив'язка часу: зсунути гіро під кадри за збігом руху", size=17, bold=True)]

    # ── зліва: дві часові стрічки ──
    x0, xw = 40, 360
    yf, yg = 96, 172
    f.append(text(x0, yf - 16, "відео (свій кварц)", size=11, bold=True, anchor="start", color=FIELD))
    f.append(line(x0, yf, x0 + xw, yf, color=FIELD, sw=2))
    for i in range(7):                                  # кадри — рідко
        cx = x0 + 18 + i * 56
        f.append(line(cx, yf - 7, cx, yf + 7, color=FIELD, sw=2))
    f.append(text(x0, yg + 26, "гіро (інший кварц, густо + дрейф)", size=11, bold=True, anchor="start", color=POS))
    f.append(line(x0, yg, x0 + xw, yg, color=POS, sw=2))
    for i in range(30):                                 # гіро — густо, крок трохи росте (дрейф)
        cx = x0 + 10 + i * 11 + 0.05 * i * i
        if cx > x0 + xw:
            break
        f.append(line(cx, yg - 5, cx, yg + 5, color=POS, sw=1.4))
    # зсув між стартами стрічок
    f.append(line(x0 + 18, yf, x0 + 10, yg, color=MUTED, sw=1.4, dash="3 3"))
    f.append(text(x0 + 2, (yf + yg) / 2, "offset", size=10, color=MUTED, anchor="start"))
    f.append(text(x0 + xw - 4, yg + 26, "крок росте → дрейф", size=10, color=MUTED, anchor="end"))

    # ── справа-внизу: дві криві руху накладаються при правильному зсуві ──
    bx, by, bw, bh = 60, 252, 320, 108
    f.append(rect(bx, by, bw, bh, fill="#f0f2f5", stroke=LINE, sw=1.4))
    f.append(text(bx + bw / 2, by - 8, "коли зсув вірний — криві руху збігаються", size=11, bold=True))
    n = 60
    pts_v, pts_g = [], []
    for i in range(n + 1):
        xx = bx + 8 + i * (bw - 16) / n
        t = i / n * 6.28
        env = math.exp(-0.45 * i / n * 6)
        yv = by + bh / 2 - 32 * math.sin(t) * env
        yg2 = by + bh / 2 - 32 * math.sin(t + 0.13) * env          # ледь зсунута
        pts_v.append("%.1f,%.1f" % (xx, yv))
        pts_g.append("%.1f,%.1f" % (xx, yg2))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts_v), FIELD))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="5 4"/>' % (" ".join(pts_g), POS))
    f.append(text(bx + bw + 14, by + 22, "— рух по відео", size=10, color=FIELD, anchor="start"))
    f.append(text(bx + bw + 14, by + 42, "·· рух по гіро", size=10, color=POS, anchor="start"))
    f.append(mtext(bx + bw + 14, by + 74, ["ковзаємо гіро", "уздовж часу →", "мінімум розбіжності", "= точна прив'язка"],
                   size=10, color=INK, anchor="start", lh=1.35))

    f.append(text(W / 2, H - 14,
                  "помилка зсуву на пів кадру → стабілізація в протифазі, гірше за відсутність EIS",
                  size=12, color=INK))
    return render(os.path.join(IMG, "eis-sync.svg"), W, H, *f)


# ── 7. Рядкова заслінка: кожен рядок знято в свій момент → свій кут ──────────
def fig_eis_rolling():
    """CMOS зчитує кадр згори вниз: верхній рядок схоплено раніше за нижній на
    весь час зчитування. За поворот камери верх і низ виходять під різним кутом
    («желе»). Виправлення — деформація по рядках: кожному рядку свій кут на
    момент ЙОГО зчитування, а не один кут на весь кадр."""
    import math
    W, H = 880, 400
    f = [text(W / 2, 30, "Рядкова заслінка: кожному рядку — свій кут зчитування", size=17, bold=True)]

    # ── зліва: час зчитування зверху вниз ──
    fx, fy, fw, fh = 92, 86, 150, 230
    f.append(rect(fx, fy, fw, fh, fill="#ffffff", stroke=LINE, sw=1.6))
    f.append(text(fx + fw / 2, fy - 10, "знятий кадр", size=11, bold=True))
    for i in range(1, 10):                              # рядки розгортки
        ry = fy + i * fh / 10
        f.append(line(fx, ry, fx + fw, ry, color="#d7dbe0", sw=1))
    f.append(arrow(fx - 26, fy + 6, fx - 26, fy + fh - 6, color=POS))
    f.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="10" fill="%s" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">час зчитування згори вниз</text>'
             % (fx - 42, fy + fh / 2, FONT, POS, fx - 42, fy + fh / 2))
    f.append(text(fx + fw + 10, fy + 12, "верх: t_кадру", size=10, color=INK, anchor="start"))
    f.append(text(fx + fw + 10, fy + fh - 4, "низ: +час зчитування", size=10, color=INK, anchor="start"))

    # ── центр: один кут на всі рядки = «желе» ──
    mx = 410
    f.append(text(mx + 30, 78, "один кут на кадр", size=12, bold=True))
    f.append(text(mx + 30, 96, "→ стовп кривиться («желе»)", size=10, color=POS))
    jx, jy = mx + 30, 124
    pj = []
    for i in range(7):
        yy = jy + i * 24
        xx = jx + 18 * math.sin(i * 0.9)
        pj.append("%.1f,%.1f" % (xx, yy))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="4"/>' % (" ".join(pj), POS))
    f.append(text(jx, jy + 7 * 24 + 12, "крива", size=10, color=POS))

    # ── справа: свій кут на рядок = рівно ──
    rx = 690
    f.append(text(rx + 20, 78, "свій кут на рядок", size=12, bold=True, color=FIELD))
    f.append(text(rx + 20, 96, "→ стовп рівний", size=10, color=FIELD))
    f.append(line(rx + 20, 124, rx + 20, 124 + 6 * 24, color=FIELD, sw=4))
    f.append(text(rx + 20, 124 + 6 * 24 + 12, "рівно", size=10, color=FIELD))
    # стрілка-перетворення
    f.append(arrow(mx + 120, 210, rx - 30, 210, color=NEG))
    f.append(text((mx + 120 + rx - 30) / 2, 200, "деформація по рядках", size=10, bold=True, color=NEG))

    f.append(text(W / 2, H - 14,
                  "t_рядка = t_кадру + (рядок / висота)·час зчитування — кут беремо на цей момент",
                  size=12, color=INK))
    return render(os.path.join(IMG, "eis-rolling.svg"), W, H, *f)


if __name__ == "__main__":
    fig_three_layers()
    fig_gimbal_loop()
    fig_eis_crop()
    fig_steadicam_anatomy()
    fig_passive_to_active()
    fig_eis_sync()
    fig_eis_rolling()
    print("OK: 7 фігур у", IMG)
