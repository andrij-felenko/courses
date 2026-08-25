# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def zigzag(x1, y1, x2, y2, color=INK, sw=2.2, n=6, amp=8):
    """Резистор-зиґзаґ між двома точками (по горизонталі)."""
    import math
    pts = []
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L      # уздовж
    px, py = -uy, ux                           # поперек
    for i in range(n + 1):
        t = i / n
        bx = x1 + (x2 - x1) * t
        by = y1 + (y2 - y1) * t
        off = 0 if (i == 0 or i == n) else (amp if i % 2 else -amp)
        pts.append('%.1f,%.1f' % (bx + px * off, by + py * off))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (' '.join(pts), color, sw))


def wave(x0, y0, w, amp, periods=2.0, phase=0.0, color=INK, sw=2.4, n=90):
    import math
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + t * w
        y = y0 - amp * math.sin(2 * math.pi * periods * t + phase)
        pts.append('%.1f,%.1f' % (x, y))
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (' '.join(pts), color, sw))


# ── Фігура 1: як народжується петля ─────────────────────────────────────────
def fig_loop_born():
    """Дві коробки з'єднані ДВІЧІ: сигнальним проводом і захисним заземленням —
    разом вони замикають кільце. Підсвічуємо саме замкнений контур."""
    W, H = 780, 430
    f = []
    f.append(text(W / 2, 30, "Два з'єднання замість одного — і коло замикається в кільце",
                  size=16, bold=True))

    yA, yB = 150, 150
    # дві коробки
    a, aw, ah = textbox(150, yA, "ПРИЛАД A", size=13, min_w=150, stroke=INK)
    b, bw, bh = textbox(630, yB, "ПРИЛАД B", size=13, min_w=150, stroke=INK)
    f.append(a); f.append(b)
    ax = 150 + aw / 2
    bx = 630 - bw / 2

    # верхній провід — сигнал
    f.append(line(ax, yA - 18, bx, yB - 18, color=POS, sw=2.6))
    f.append(text((ax + bx) / 2, yA - 28, "сигнальний провід (екран кабелю)",
                  size=12, color=POS, bold=True))

    # нижній шлях — обидва прилади заземлені в мережу
    gy = 320
    f.append(line(ax, yA + 18, ax, gy, color=NEG, sw=2.6))
    f.append(line(bx, yB + 18, bx, gy, color=NEG, sw=2.6))
    f.append(line(ax, gy, bx, gy, color=NEG, sw=2.6))
    f.append(text((ax + bx) / 2, gy + 22,
                  "захисне заземлення обох (через розетки мережі)",
                  size=12, color=NEG, bold=True))

    # символ землі під кожним
    for xx in (ax, bx):
        f.append(line(xx - 14, gy, xx + 14, gy, color=NEG, sw=2.4))
        f.append(line(xx - 9, gy + 6, xx + 9, gy + 6, color=NEG, sw=2.0))
        f.append(line(xx - 4, gy + 12, xx + 4, gy + 12, color=NEG, sw=1.8))

    # підсвітити замкнений контур — кругова стрілка струму
    import math
    cx, cy = (ax + bx) / 2, (yA - 18 + gy) / 2
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="48" ry="34" fill="none" '
             'stroke="%s" stroke-width="2.2" stroke-dasharray="6 5"/>'
             % (cx, cy, FIELD))
    f.append(arrow(cx + 30, cy - 24, cx + 46, cy - 6, color=FIELD, sw=2.4))
    f.append(text(cx, cy + 4, "струм\nкружляє".split("\n")[0], size=12, color=FIELD, bold=True))
    f.append(text(cx, cy + 18, "кружляє", size=12, color=FIELD, bold=True))

    return render(os.path.join(IMG, 'loop-born.svg'), W, H, *f)


# ── Фігура 2: спільний зворотний провід — серце механізму ───────────────────
def fig_common_impedance():
    """Два кола ділять один зворотний провід з опором R. Струм гучного кола
    тече крізь R і піднімає 'землю' тихого кола на I·R — той бачить домішку."""
    W, H = 800, 470
    f = []
    f.append(text(W / 2, 30, "Спільний зворотний провід: чужий струм піднімає твою «землю»",
                  size=16, bold=True))

    xL = 120          # ліва (вузли)
    xMid = 470        # права (точка з'єднання з реальною землею)
    yTop = 95         # гучне коло
    yBot = 175        # тихе коло (наш сигнал)
    yRet = 300        # спільний зворотний провід

    # джерела/навантаження двох кіл (символічно — прямокутники зліва)
    s1, w1, h1 = textbox(xL, yTop, "гучне коло\n(великий струм)", size=11, min_w=150, stroke=POS)
    s2, w2, h2 = textbox(xL, yBot, "наш сигнал\n(слабкий)", size=11, min_w=150, stroke=FIELD)
    f.append(s1); f.append(s2)
    x1 = xL + w1 / 2
    x2 = xL + w2 / 2

    # прямі (верхні) проводи кожного кола до правого вузла
    f.append(line(x1, yTop, xMid, yTop, color=POS, sw=2.2))
    f.append(line(x2, yBot, xMid, yBot, color=FIELD, sw=2.2))

    # з правого боку обидва спускаються у спільний вузол N
    f.append(line(xMid, yTop, xMid, yRet, color=INK, sw=2.2))
    f.append(line(xMid, yBot, xMid, yRet, color=INK, sw=2.2))
    f.append(circle(xMid, yRet, 5, fill=INK, stroke=INK))
    f.append(text(xMid + 10, yRet - 8, "вузол N", size=12, anchor="start", bold=True))

    # СПІЛЬНИЙ зворотний провід N → реальна земля, з опором R (зиґзаґ)
    xGnd = 700
    f.append(zigzag(xMid, yRet, xGnd, yRet, color=NEG, sw=2.6))
    f.append(text((xMid + xGnd) / 2, yRet - 14, "спільний зворотний — опір R",
                  size=12, color=NEG, bold=True))
    # символ землі праворуч
    f.append(line(xGnd, yRet, xGnd, yRet + 8, color=NEG, sw=2.2))
    f.append(line(xGnd - 14, yRet + 8, xGnd + 14, yRet + 8, color=NEG, sw=2.4))
    f.append(line(xGnd - 9, yRet + 14, xGnd + 9, yRet + 14, color=NEG, sw=2.0))
    f.append(line(xGnd - 4, yRet + 20, xGnd + 4, yRet + 20, color=NEG, sw=1.8))

    # стрілка великого струму вниз і крізь R
    f.append(arrow(xMid - 18, yTop + 8, xMid - 18, yRet - 8, color=POS, sw=2.4))
    f.append(text(xMid - 24, (yTop + yRet) / 2, "I", size=14, color=POS, bold=True, anchor="end"))
    f.append(arrow(xMid + 30, yRet, xGnd - 30, yRet, color=POS, sw=2.0))

    # піднята «земля» вузла N — підпис
    nb, nbw, nbh = textbox(xMid, yRet + 70, "потенціал N = I·R\n(а не 0!)", size=11,
                           min_w=150, stroke=POS)
    f.append(line(xMid, yRet + 5, xMid, yRet + 70 - nbh / 2, color=POS, sw=1.3, dash="3 3"))
    f.append(nb)

    # що бачить тихий приймач
    f.append(fitbox(120, 392, 560, 40,
                    "Тихий приймач міряє свій сигнал ВІД вузла N → дістає сигнал + I·R. "
                    "Чужий струм підмішався в наш — хоча проводи нібито нарізно.",
                    size=12, fill="#eafaf1", stroke=FIELD))

    return render(os.path.join(IMG, 'common-impedance.svg'), W, H, *f)


# ── Фігура 3: дві опори — спільна (погано) vs роздільна/зіркою (добре) ───────
def fig_star_vs_daisy():
    """Ліворуч: ланцюжком (струм гучного тече крізь ділянку, спільну з тихим).
    Праворуч: зіркою — кожне коло окремим проводом до однієї точки; спільної
    ділянки немає, чужий струм не падає на чужий провід."""
    W, H = 800, 380
    f = []
    f.append(text(W / 2, 28, "Спільна ділянка vs одна точка («зірка»)", size=16, bold=True))

    # ── ліва половина: ланцюжком (daisy-chain) ──
    f.append(text(200, 60, "ланцюжком — є спільна ділянка", size=13, bold=True, color=POS))
    gy = 250
    f.append(line(70, gy, 330, gy, color=NEG, sw=3))      # спільна шина землі
    # блоки A, B висять на шину в РІЗНИХ точках, але між ними — спільний шмат
    for (xx, lab, col) in ((130, "A", POS), (270, "B", FIELD)):
        bb, bw, bh = textbox(xx, 150, lab, size=12, min_w=70, stroke=col)
        f.append(bb)
        f.append(line(xx, 150 + bh / 2, xx, gy, color=col, sw=2.4))
    # спільна ділянка між точками A і B + точкою заземлення зліва
    f.append(zigzag(70, gy, 130, gy, color=INK, sw=2.6, n=4, amp=7))
    f.append(text(100, gy + 20, "Rспільн", size=11, color=POS, bold=True))
    f.append(arrow(140, gy + 8, 80, gy + 8, color=POS, sw=2.0))
    f.append(text(165, gy + 34, "струм B тече крізь Rспільн → шум у A",
                  size=10.5, color=POS, anchor="start"))
    # земля зліва
    f.append(line(70, gy, 70, gy + 6, color=NEG, sw=2))
    f.append(line(62, gy + 6, 78, gy + 6, color=NEG, sw=2.2))

    # роздільник
    f.append(line(W / 2, 50, W / 2, 330, color="#dddddd", sw=1.2))

    # ── права половина: зіркою (star) ──
    f.append(text(600, 60, "зіркою — спільна лише точка", size=13, bold=True, color=FIELD))
    star = (600, 250)
    f.append(circle(star[0], star[1], 6, fill=NEG, stroke=NEG))
    f.append(text(star[0], star[1] + 22, "одна точка землі", size=11, color=NEG, bold=True))
    for (xx, lab, col) in ((520, "A", POS), (680, "B", FIELD)):
        bb, bw, bh = textbox(xx, 150, lab, size=12, min_w=70, stroke=col)
        f.append(bb)
        # ОКРЕМИЙ провід кожного просто до точки-зірки
        f.append(line(xx, 150 + bh / 2, star[0], star[1], color=col, sw=2.4))
    f.append(text(600, 300, "жодної спільної ділянки → струми не змішуються",
                  size=10.5, color=FIELD))

    return render(os.path.join(IMG, 'star-vs-daisy.svg'), W, H, *f)


# ── Фігура 4: петля як виток трансформатора (Фарадей) ───────────────────────
def fig_loop_antenna():
    """Замкнена петля охоплює площу; мережевий дріт поряд гонить змінний потік
    крізь цю площу → у петлі наводиться ЕРС 50 Гц, як у короткозамкненому витку."""
    W, H = 780, 380
    f = []
    f.append(text(W / 2, 28, "Петля охоплює площу — змінний потік мережі наводить у ній ЕРС",
                  size=15.5, bold=True))

    # прямокутна петля
    x1, y1, x2, y2 = 150, 110, 560, 290
    f.append(rect(x1, y1, x2 - x1, y2 - y1, fill="none", stroke=FIELD, sw=2.6, rx=10))
    f.append(text((x1 + x2) / 2, (y1 + y2) / 2 + 5, "площа петлі  S", size=14,
                  color=FIELD, bold=True))

    # вузли A, B на петлі
    ab, aw, ah = textbox(x1, (y1 + y2) / 2, "A", size=12, min_w=56, stroke=INK)
    bb, bw, bh = textbox(x2, (y1 + y2) / 2, "B", size=12, min_w=56, stroke=INK)
    f.append(ab); f.append(bb)

    # мережевий провід поряд — джерело змінного потоку
    f.append(line(120, 60, 600, 60, color=POS, sw=3))
    f.append(text(360, 50, "поряд — мережевий кабель 50 Гц (змінний струм)",
                  size=12, color=POS, bold=True))
    # «потік» крізь площу — кілька хрестиків/крапок
    import math
    for i in range(5):
        xx = x1 + 60 + i * 80
        yy = (y1 + y2) / 2 - 10
        f.append(circle(xx, yy, 9, fill="none", stroke=NEG, sw=1.8))
        f.append(line(xx - 6, yy - 6, xx + 6, yy + 6, color=NEG, sw=1.6))
        f.append(line(xx - 6, yy + 6, xx + 6, yy - 6, color=NEG, sw=1.6))
    f.append(text((x1 + x2) / 2, y1 - 8, "змінний магнітний потік Φ(t) крізь площу",
                  size=11, color=NEG))

    # наведена ЕРС
    f.append(fitbox(150, 312, 460, 38,
                    "ЕРС = − dΦ/dt  →  струм 50 Гц у петлі. Чим БІЛЬША площа S, тим гірше.",
                    size=12.5, fill="#eafaf1", stroke=FIELD))
    # стрілка струму по петлі
    f.append(arrow(x2, y1 + 40, x2, y1 + 14, color=FIELD, sw=2.2))

    return render(os.path.join(IMG, 'loop-antenna.svg'), W, H, *f)


# ── Фігура 5 (math): суперпозиція — внесок кожного кола окремо через спільний Z
def fig_superposition_split():
    """Дві гілки зі струмами I1, I2 ллються в один вузол і йдуть крізь спільний Z.
    Похибкова напруга на Z = (I1+I2)·Z; за суперпозицією — сума двох внесків.
    Показуємо, що тіло читача — це КЗН по контуру тихого кола."""
    W, H = 820, 430
    f = []
    f.append(text(W / 2, 30, "Суперпозиція: спад на спільному Z — сума внесків кожного кола",
                  size=15.5, bold=True))

    # дві гілки-джерела струму зліва
    yA, yB = 95, 185
    s1, w1, h1 = textbox(120, yA, "коло 1\nструм I₁", size=11, min_w=140, stroke=POS)
    s2, w2, h2 = textbox(120, yB, "коло 2\nструм I₂", size=11, min_w=140, stroke=FIELD)
    f.append(s1); f.append(s2)
    x1 = 120 + w1 / 2
    x2 = 120 + w2 / 2

    xN = 430
    yN = 250
    # обидві гілки сходяться у вузол N
    f.append(line(x1, yA, xN, yA, color=POS, sw=2.2))
    f.append(line(x2, yB, xN, yB, color=FIELD, sw=2.2))
    f.append(line(xN, yA, xN, yN, color=INK, sw=2.2))
    f.append(line(xN, yB, xN, yN, color=INK, sw=2.2))
    f.append(circle(xN, yN, 5, fill=INK, stroke=INK))
    f.append(text(xN - 12, yN - 6, "N", size=13, anchor="end", bold=True))

    # стрілки струмів у вузол
    f.append(arrow(x1 + 60, yA, x1 + 92, yA, color=POS, sw=2.0))
    f.append(text(x1 + 76, yA - 8, "I₁", size=12, color=POS, bold=True))
    f.append(arrow(x2 + 60, yB, x2 + 92, yB, color=FIELD, sw=2.0))
    f.append(text(x2 + 76, yB - 8, "I₂", size=12, color=FIELD, bold=True))

    # спільний Z праворуч від N до землі
    xG = 700
    f.append(zigzag(xN, yN, xG, yN, color=NEG, sw=2.6))
    f.append(text((xN + xG) / 2, yN - 14, "спільний зворот  Z(ω)", size=12, color=NEG, bold=True))
    f.append(arrow(xN + 28, yN, xG - 28, yN, color=POS, sw=2.0))
    f.append(text((xN + xG) / 2, yN + 22, "I₁ + I₂", size=12, color=POS, bold=True))
    # земля
    f.append(line(xG, yN, xG, yN + 7, color=NEG, sw=2.2))
    f.append(line(xG - 13, yN + 7, xG + 13, yN + 7, color=NEG, sw=2.4))
    f.append(line(xG - 8, yN + 13, xG + 8, yN + 13, color=NEG, sw=2.0))
    f.append(line(xG - 3, yN + 19, xG + 3, yN + 19, color=NEG, sw=1.8))

    # формула-внесок
    f.append(fitbox(120, 320, 580, 80,
                    "V_N = (I₁ + I₂)·Z   →   у твій сигнал лізе чужий внесок I₁·Z.\n"
                    "Окремо: вимкни I₂ — лишиться I₁·Z; вимкни I₁ — лишиться I₂·Z; "
                    "разом сума.\nТихе коло «бачить» Z як спільний член — звідси transfer impedance.",
                    size=12, fill="#f4f6f8", stroke=INK))
    return render(os.path.join(IMG, 'superposition-split.svg'), W, H, *f)


# ── Фігура 6 (math): чому зв'язок гіршає з частотою — Z(ω)=R+jωL ─────────────
def fig_transfer_impedance_freq():
    """Модуль спільного опору |Z| = √(R²+(ωL)²): на низьких частотах плато R,
    далі злам на ω=R/L і зростання +20 дБ/дек через ωL. Лог-лог ескіз."""
    import math
    W, H = 760, 420
    f = []
    f.append(text(W / 2, 28, "Спільний опір росте з частотою: |Z| = √(R² + (ωL)²)",
                  size=15.5, bold=True))

    # осі
    x0, y0 = 110, 330      # початок (лівий-нижній)
    xw, yh = 560, 250      # довжина осей
    f.append(line(x0, y0, x0 + xw, y0, color=INK, sw=1.8))   # вісь частоти
    f.append(line(x0, y0, x0, y0 - yh, color=INK, sw=1.8))   # вісь |Z|
    f.append(text(x0 + xw, y0 + 24, "частота (лог)", size=12, anchor="end"))
    f.append(text(x0 - 8, y0 - yh + 4, "|Z|", size=13, anchor="end", bold=True))

    # крива |Z|: плато R, тоді +20 дБ/дек. Беремо лог-лог: y росте лінійно після зламу.
    # параметри ескізу
    f_break_frac = 0.42                # частка по осі X, де злам ω=R/L
    yR = y0 - 60                       # рівень плато R
    pts = []
    n = 80
    for i in range(n + 1):
        t = i / n                      # 0..1 уздовж осі X (лог-частота)
        x = x0 + t * xw
        if t <= f_break_frac:
            y = yR
        else:
            # після зламу зростання вгору (на лог-лог — пряма), нахил ~ +1 декада/декада
            y = yR - (t - f_break_frac) / (1 - f_break_frac) * (yh - 70)
        pts.append('%.1f,%.1f' % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linejoin="round"/>' % (' '.join(pts), POS))

    # позначки R та злам
    xb = x0 + f_break_frac * xw
    f.append(line(x0, yR, xb, yR, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(x0 - 8, yR + 4, "R", size=12, anchor="end", color=NEG, bold=True))
    f.append(line(xb, y0, xb, yR, color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(xb, y0 + 20, "ω = R/L", size=11.5, color=INK, bold=True))

    # підписи двох режимів
    f.append(text((x0 + xb) / 2, yR - 12, "опір тримає R", size=11.5, color=NEG))
    f.append(text(xb + (x0 + xw - xb) / 2, yR - 70,
                  "панує ωL  (+20 дБ/дек)", size=11.5, color=POS, bold=True))

    # висновок-рамка
    f.append(fitbox(110, 358, 540, 50,
                    "Та сама петля, що дає 10 мВ на 50 Гц, на фронтах цифри (МГц)\n"
                    "сполучає в рази гірше — провід стає котушкою. Бий по ПЛОЩІ, не лише R.",
                    size=12, fill="#fdecea", stroke=POS))
    return render(os.path.join(IMG, 'transfer-impedance-freq.svg'), W, H, *f)


# ── Фігура 7 (hist): дефект контакту 1 — куди заведено екран ────────────────
def fig_pin1_defect():
    """Той самий прилад, два варіанти. Ліворуч (дефект): екран із контакту 1
    заведено на сигнальну землю плати → струм екрана тече доріжкою з опором R
    і лишає на ній I·R прямо в сигналі. Праворуч (добре): контакт 1 одразу на
    корпус → струм екрана йде корпусом повз плату, сигнальна земля чиста."""
    W, H = 820, 430
    f = []
    f.append(text(W / 2, 28, "Куди заведено контакт 1: на плату (дефект) чи на корпус",
                  size=15.5, bold=True))

    def panel(ox, title, tcol, to_chassis):
        # корпус приладу — велика рамка
        cx0, cy0, cw, ch = ox + 55, 70, 300, 300
        f.append(rect(cx0, cy0, cw, ch, fill="none", stroke=INK, sw=2.2, rx=10))
        f.append(text(cx0 + cw / 2, cy0 - 8, title, size=13, bold=True, color=tcol))
        # символ корпусу-металу (штрихована смужка зверху)
        f.append(text(cx0 + 8, cy0 + 18, "металевий корпус", size=10.5,
                      anchor="start", color=MUTED))

        # плата всередині
        bx0, by0, bw, bh = cx0 + 40, cy0 + 70, cw - 80, 120
        f.append(rect(bx0, by0, bw, bh, fill="#f4f6f8", stroke=MUTED, sw=1.6, rx=6))
        f.append(text(bx0 + bw / 2, by0 + 16, "друкована плата", size=10.5, color=MUTED))
        f.append(text(bx0 + bw / 2, by0 + bh - 10, "сигнальна земля", size=10.5,
                      color=FIELD, bold=True))

        # роз'єм XLR зліва на корпусі — контакт 1 (екран)
        px, py = cx0, cy0 + ch / 2
        f.append(circle(px, py, 7, fill="none", stroke=NEG, sw=2.2))
        f.append(text(px - 12, py - 10, "контакт 1\n(екран)".split("\n")[0],
                      size=10.5, anchor="end", color=NEG, bold=True))
        f.append(text(px - 12, py + 4, "(екран)", size=10.5, anchor="end", color=NEG))
        # вхідний струм екрана зовні
        f.append(arrow(px - 42, py, px - 11, py, color=NEG, sw=2.4))
        f.append(text(px - 44, py - 10, "струм екрана", size=10.5, anchor="start", color=NEG))

        # точка з'єднання плата↔корпус (праворуч унизу плати)
        jx, jy = bx0 + bw, by0 + bh
        f.append(circle(jx, jy, 4, fill=INK, stroke=INK))

        if not to_chassis:
            # ДЕФЕКТ: контакт 1 → на сигнальну землю плати (заходить у плату зліва)
            ent_x, ent_y = bx0, by0 + bh - 18
            f.append(line(px + 7, py, ent_x, ent_y, color=POS, sw=2.6))
            # струм біжить уздовж землі плати до точки з'єднання → крізь опір R
            f.append(zigzag(ent_x + 6, ent_y, jx - 6, ent_y, color=POS, sw=2.4, n=4, amp=6))
            f.append(text((ent_x + jx) / 2, ent_y + 16, "R землі", size=10.5,
                          color=POS, bold=True))
            f.append(arrow(ent_x + 40, ent_y - 12, jx - 20, ent_y - 12, color=POS, sw=1.8))
            # від точки з'єднання — на корпус і вниз на землю
            f.append(line(jx, jy, jx, cy0 + ch, color=INK, sw=2.2))
            # підпис-біда
            f.append(fitbox(cx0, cy0 + ch + 14, cw, 40,
                            "Струм екрана тече сигнальною землею → I·R лізе в сигнал. ГУЛ.",
                            size=11, fill="#fdecea", stroke=POS))
        else:
            # ДОБРЕ: контакт 1 одразу на корпус, повз плату
            f.append(line(px + 7, py, cx0 + 6, py, color=FIELD, sw=2.6))
            f.append(line(cx0 + 6, py, cx0 + 6, cy0 + ch, color=FIELD, sw=2.6))
            f.append(text(cx0 + 6, py - 12, "→ одразу на корпус", size=10.5,
                          anchor="start", color=FIELD, bold=True))
            f.append(arrow(cx0 + 6, py + 30, cx0 + 6, py + 70, color=FIELD, sw=1.8))
            f.append(fitbox(cx0, cy0 + ch + 14, cw, 40,
                            "Струм екрана йде корпусом повз плату → сигнальна земля чиста.",
                            size=11, fill="#eafaf1", stroke=FIELD))

        # вихід приладу на корпус — символ землі знизу
        gx = cx0 + cw / 2
        gy = cy0 + ch
        f.append(line(gx, gy, gx, gy + 8, color=NEG, sw=2.0))
        f.append(line(gx - 12, gy + 8, gx + 12, gy + 8, color=NEG, sw=2.2))
        f.append(line(gx - 7, gy + 13, gx + 7, gy + 13, color=NEG, sw=1.9))
        f.append(line(gx - 3, gy + 18, gx + 3, gy + 18, color=NEG, sw=1.7))

    panel(0, "ДЕФЕКТ: контакт 1 → плата", POS, to_chassis=False)
    # роздільник
    f.append(line(W / 2, 50, W / 2, 380, color="#dddddd", sw=1.2))
    panel(410, "ПРАВИЛЬНО: контакт 1 → корпус", FIELD, to_chassis=True)

    return render(os.path.join(IMG, 'pin1-defect.svg'), W, H, *f)


if __name__ == '__main__':
    outs = [fig_loop_born(), fig_common_impedance(), fig_star_vs_daisy(), fig_loop_antenna(),
            fig_superposition_split(), fig_transfer_impedance_freq(), fig_pin1_defect()]
    for p in outs:
        print("wrote", p)
