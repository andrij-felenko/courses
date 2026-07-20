# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

PITCH = "#eaf2fb"   # ділильне коло / допоміжне


def arc(cx, cy, r, a0, a1, color, sw=2.0, arrowhead=False, dash=None):
    """Дуга від кута a0 до a1 (радіани, екранні координати), опц. зі стрілкою."""
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if abs(a1 - a0) > math.pi else 0
    sweep = 1 if a1 > a0 else 0
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    m = ' marker-end="url(#arrow)"' if arrowhead else ''
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f"%s%s/>' % (x0, y0, r, r, large, sweep,
                                                       x1, y1, color, sw, d, m))


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 1 — основний закон зачеплення: спільна нормаль у точці контакту завжди
# проходить через полюс P на лінії центрів. Передавальне відношення = O2P/O1P,
# тож воно стале рівно тоді, коли P нерухомий. Серце всієї теорії спряження.
# ═══════════════════════════════════════════════════════════════════════════
def fig_conjugate():
    W, H = 760, 500
    f = [text(W / 2, 28, 'Основний закон зачеплення: спільна нормаль крізь полюс',
              16, INK, 'middle', bold=True)]

    O1 = (250, 250); O2 = (535, 250)
    r1, r2 = 120, 165
    P = (O1[0] + r1, O1[1])                      # полюс — дотик ділильних кіл

    # лінія центрів
    f.append(line(120, O1[1], 665, O1[1], color=MUTED, sw=1.2, dash='6,5'))
    f.append(text(126, O1[1] - 10, 'лінія центрів', 11, MUTED, 'start'))

    # ділильні кола
    f.append(circle(O1[0], O1[1], r1, fill='none', stroke=NEG, sw=1.4))
    f.append(circle(O2[0], O2[1], r2, fill='none', stroke=NEG, sw=1.4))
    f.append(text(O1[0], O1[1] + r1 + 20, 'ділильне коло 1', 11, NEG, 'middle'))
    f.append(text(O2[0], O2[1] + r2 + 20, 'ділильне коло 2', 11, NEG, 'middle'))

    # напрями обертання
    f.append(arc(O1[0], O1[1], 40, math.radians(-135), math.radians(-45),
                 NEG, sw=2.2, arrowhead=True))
    f.append(text(O1[0], O1[1] - 52, 'ω₁', 14, NEG, 'middle', bold=True))
    f.append(arc(O2[0], O2[1], 40, math.radians(-45), math.radians(-135),
                 POS, sw=2.2, arrowhead=True))
    f.append(text(O2[0], O2[1] - 52, 'ω₂', 14, POS, 'middle', bold=True))

    # осі
    for O, nm, ax in ((O1, 'O₁', 'end'), (O2, 'O₂', 'start')):
        f.append(circle(O[0], O[1], 4, fill=INK, stroke=INK, sw=1))
        dx = -10 if ax == 'end' else 10
        f.append(text(O[0] + dx, O[1] + 20, nm, 13, INK, ax, bold=True))

    # точка контакту C на нормалі, вище полюса (профілі дотикаються тут)
    ang = math.radians(20)                       # нахил нормалі від вертикалі
    up = (-math.sin(ang), -math.cos(ang))
    dn = (math.sin(ang), math.cos(ang))
    C = (P[0] + 108 * up[0], P[1] + 108 * up[1])

    # спільна нормаль — від нижче полюса до вище точки C
    n0 = (P[0] + 78 * dn[0], P[1] + 78 * dn[1])
    n1 = (C[0] + 34 * up[0], C[1] + 34 * up[1])
    f.append(line(n0[0], n0[1], n1[0], n1[1], color=FIELD, sw=2.6))
    f.append(text(n1[0] - 8, n1[1] - 6, 'спільна нормаль', 12, FIELD, 'end', bold=True))

    # спільна дотична профілів у C (перпендикуляр до нормалі), пунктир
    perp = (math.cos(ang), -math.sin(ang))
    t0 = (C[0] - 58 * perp[0], C[1] - 58 * perp[1])
    t1 = (C[0] + 58 * perp[0], C[1] + 58 * perp[1])
    f.append(line(t0[0], t0[1], t1[0], t1[1], color=MUTED, sw=1.6, dash='5,4'))
    f.append(text(t1[0] + 6, t1[1] + 4, 'профілі зубів', 11, MUTED, 'start'))

    # точка контакту C
    f.append(circle(C[0], C[1], 4.5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(C[0] - 10, C[1] - 6, 'C', 13, INK, 'end', bold=True))

    # полюс P
    f.append(circle(P[0], P[1], 5, fill=POS, stroke=POS, sw=1))
    f.append(text(P[0] + 10, P[1] + 20, 'полюс P', 13, POS, 'start', bold=True))

    f.append(mtext(W / 2, H - 34,
                   ['передавальне відношення  ω₁ / ω₂ = O₂P / O₁P  —  стале рівно тоді,',
                    'коли нормаль щоразу влучає в той самий нерухомий полюс P'],
                   12, INK, 'middle'))
    render(os.path.join(IMG, 'conjugate.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 2 — евольвента як слід кінця нитки, що змотується з основного кола.
# Натягнута нитка щомиті — нормаль до кривої й водночас дотична до кола. Саме
# ця властивість (нормаль = дотична до основного кола) робить евольвенту
# ідеальним профілем зуба.
# ═══════════════════════════════════════════════════════════════════════════
def fig_involute():
    W, H = 720, 470
    f = [text(W / 2, 28, 'Евольвента: слід кінця нитки, змотаної з основного кола',
              16, INK, 'middle', bold=True)]

    O = (250, 300); rb = 95

    def inv(t):                                  # точка евольвенти (екранні коорд.)
        x = rb * (math.cos(t) + t * math.sin(t))
        y = rb * (math.sin(t) - t * math.cos(t))
        return (O[0] + x, O[1] - y)

    def touch(t):                                # точка сходу нитки на колі
        return (O[0] + rb * math.cos(t), O[1] - rb * math.sin(t))

    # основне коло
    f.append(circle(O[0], O[1], rb, fill=PITCH, stroke=INK, sw=1.6))
    f.append(circle(O[0], O[1], 4, fill=INK, stroke=INK, sw=1))
    f.append(text(O[0], O[1] + 6, 'O', 12, INK, 'middle', bold=True))
    f.append(text(O[0] - rb - 8, O[1] + 40, 'основне коло', 12, INK, 'end'))

    # сама евольвента
    pts = [inv(i / 60 * 2.4) for i in range(61)]
    d = 'M ' + ' L '.join('%.1f %.1f' % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, POS))
    f.append(text(pts[-1][0] + 10, pts[-1][1] - 2, 'евольвента', 13, POS, 'start', bold=True))
    f.append(circle(pts[0][0], pts[0][1], 3.5, fill=POS, stroke=POS, sw=1))

    # одне положення нитки при t = 2.0
    t = 2.0
    Tp = touch(t); Q = inv(t)
    f.append(line(Tp[0], Tp[1], Q[0], Q[1], color=FIELD, sw=2.6))
    f.append(circle(Q[0], Q[1], 4.5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(circle(Tp[0], Tp[1], 4, fill=INK, stroke=INK, sw=1))
    # радіус до точки сходу — показати дотичність (нитка ⟂ радіус)
    f.append(line(O[0], O[1], Tp[0], Tp[1], color=MUTED, sw=1.2, dash='4,4'))
    # прямий кут між радіусом і ниткою біля Tp
    ur = ((Tp[0] - O[0]) / rb, (Tp[1] - O[1]) / rb)          # уздовж радіуса, від центру
    un = ((Q[0] - Tp[0]), (Q[1] - Tp[1]))
    ln = math.hypot(*un); un = (un[0] / ln, un[1] / ln)
    s = 12
    a = (Tp[0] - ur[0] * s, Tp[1] - ur[1] * s)
    b = (a[0] + un[0] * s, a[1] + un[1] * s)
    c = (Tp[0] + un[0] * s, Tp[1] + un[1] * s)
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.2"/>' % (a[0], a[1], b[0], b[1], c[0], c[1], MUTED))

    f.append(text(290, 150, 'нитка = нормаль', 12, FIELD, 'end', bold=True))
    f.append(text(Tp[0] - 6, Tp[1] + 18, 'точка сходу нитки', 11, INK, 'end'))
    f.append(text(Q[0] + 10, Q[1] - 6, 'олівець', 11, FIELD, 'start'))

    f.append(mtext(W / 2, H - 30,
                   ['натягнута нитка завжди перпендикулярна до кривої (нормаль)',
                    'і водночас дотична до основного кола — у цьому вся суть'],
                   12, MUTED, 'middle'))
    render(os.path.join(IMG, 'involute.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 3 — лінія зачеплення: спільна дотична до двох основних кіл. Вона
# нерухома, перетинає лінію центрів у полюсі P під кутом зачеплення φ, і точка
# контакту весь час біжить уздовж неї. Основне коло менше за ділильне в cos φ.
# ═══════════════════════════════════════════════════════════════════════════
def fig_line_of_action():
    W, H = 800, 480
    f = [text(W / 2, 28, 'Лінія зачеплення: спільна дотична до основних кіл',
              16, INK, 'middle', bold=True)]

    O1 = (255, 258); O2 = (535, 258)
    r1, r2 = 105, 175
    phi = math.radians(20)
    P = (O1[0] + r1, O1[1])
    rb1, rb2 = r1 * math.cos(phi), r2 * math.cos(phi)

    # лінія центрів
    f.append(line(120, O1[1], 730, O1[1], color=MUTED, sw=1.2, dash='6,5'))

    # ділильні кола (пунктир) і основні (суцільні)
    f.append(circle(O1[0], O1[1], r1, fill='none', stroke=MUTED, sw=1.2, ))
    f.append(circle(O2[0], O2[1], r2, fill='none', stroke=MUTED, sw=1.2))
    f.append(circle(O1[0], O1[1], rb1, fill='none', stroke=INK, sw=1.8))
    f.append(circle(O2[0], O2[1], rb2, fill='none', stroke=INK, sw=1.8))

    for O in (O1, O2):
        f.append(circle(O[0], O[1], 4, fill=INK, stroke=INK, sw=1))
    f.append(text(O1[0], O1[1] + 20, 'O₁', 13, INK, 'middle', bold=True))
    f.append(text(O2[0], O2[1] + 20, 'O₂', 13, INK, 'middle', bold=True))

    # лінія зачеплення — через P під кутом φ до вертикалі
    u = (math.sin(phi), math.cos(phi))           # напрям (вниз-праворуч)
    A = (P[0] - 175 * u[0], P[1] - 175 * u[1])
    B = (P[0] + 155 * u[0], P[1] + 155 * u[1])
    f.append(line(A[0], A[1], B[0], B[1], color=FIELD, sw=2.8))
    f.append(text(A[0] - 6, A[1] - 6, 'лінія зачеплення', 12, FIELD, 'end', bold=True))

    # точки дотику лінії з основними колами (перпендикуляр з осі)
    def foot(O):
        s = (O[0] - P[0]) * u[0] + (O[1] - P[1]) * u[1]
        return (P[0] + s * u[0], P[1] + s * u[1])
    T1, T2 = foot(O1), foot(O2)
    for O, T in ((O1, T1), (O2, T2)):
        f.append(line(O[0], O[1], T[0], T[1], color=NEG, sw=1.2, dash='4,4'))
        f.append(circle(T[0], T[1], 3.5, fill=NEG, stroke=NEG, sw=1))

    # вертикаль у полюсі — спільна дотична ділильних кіл (від неї міряють φ)
    f.append(line(P[0], P[1] - 66, P[0], P[1] + 46, color=MUTED, sw=1.2, dash='4,4'))
    # дуга кута φ між вертикаллю (угору) і лінією зачеплення (угору-ліворуч)
    a_vert = math.radians(-90)
    a_line = math.atan2(-u[1], -u[0])
    f.append(arc(P[0], P[1], 46, a_line, a_vert, POS, sw=1.8))
    mid = (a_vert + a_line) / 2
    f.append(text(P[0] + 62 * math.cos(mid), P[1] + 62 * math.sin(mid),
                  'φ', 15, POS, 'middle', bold=True))

    # полюс
    f.append(circle(P[0], P[1], 5, fill=POS, stroke=POS, sw=1))
    f.append(text(P[0] + 12, P[1] - 8, 'полюс P', 13, POS, 'start', bold=True))

    # рухома точка контакту вздовж лінії
    Cc = (P[0] - 40 * u[0], P[1] - 40 * u[1])
    f.append(circle(Cc[0], Cc[1], 4, fill=INK, stroke=INK, sw=1))

    # підписи кіл (з відступом, щоб не лягти на лінії)
    f.append(text(O1[0] - r1 - 6, O1[1] - 30, 'ділильне коло', 11, MUTED, 'end'))
    f.append(text(O2[0] + rb2 + 8, O2[1] - 8, 'основне коло', 11, INK, 'start'))
    f.append(text(W / 2, H - 52, 'd_осн = d · cos φ    (кут зачеплення φ)',
                  13, INK, 'middle', bold=True))
    f.append(mtext(W / 2, H - 28,
                   ['лінія нерухома, тож полюс P не рухається, а кут φ сталий —',
                    'точка контакту весь час біжить уздовж цієї прямої'],
                   11, MUTED, 'middle'))
    render(os.path.join(IMG, 'line-of-action.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 4 — коефіцієнт перекриття: шлях контакту AB довший за основний крок
# p_осн, тому в ньому завжди вміщається принаймні одна пара, а часто — дві.
# Пари перекриваються → зачеплення не переривається. ε = AB / p_осн.
# ═══════════════════════════════════════════════════════════════════════════
def fig_contact_ratio():
    W, H = 760, 320
    f = [text(W / 2, 28, 'Коефіцієнт перекриття: пари зубів перекривають одна одну',
              16, INK, 'middle', bold=True)]

    y = 185
    xL, xR = 90, 670
    xA, xB = 210, 540                            # шлях контакту AB
    pb = 205.0                                   # основний крок (px)
    c1 = 250.0; c2 = c1 + pb                     # дві пари в контакті

    # лінія зачеплення
    f.append(line(xL, y, xR, y, color=MUTED, sw=1.4))
    f.append(text(xR + 4, y + 4, 'лінія зачеплення', 11, MUTED, 'start'))

    # шлях контакту AB (активна ділянка)
    f.append(line(xA, y, xB, y, color=FIELD, sw=5))
    for x, nm, sub in ((xA, 'A', 'зуби входять'), (xB, 'B', 'зуби виходять')):
        f.append(line(x, y - 20, x, y + 20, color=INK, sw=1.6))
        f.append(text(x, y - 28, nm, 13, INK, 'middle', bold=True))
        f.append(text(x, y + 40, sub, 11, MUTED, 'middle'))
    f.append(text((xA + xB) / 2, y - 52, 'шлях контакту  AB', 12, FIELD, 'middle', bold=True))

    # дві пари в контакті, рознесені на основний крок
    for cx, nm in ((c1, 'пара 1'), (c2, 'пара 2')):
        f.append(circle(cx, y, 6, fill=POS, stroke=POS, sw=1))
        f.append(text(cx, y + 62, nm, 11, POS, 'middle', bold=True))
    # дужка основного кроку між парами
    yb = y - 74
    f.append(line(c1, y - 10, c1, yb, color=NEG, sw=1, dash='3,3'))
    f.append(line(c2, y - 10, c2, yb, color=NEG, sw=1, dash='3,3'))
    f.append(line(c1, yb, c2, yb, color=NEG, sw=1.6))
    f.append(text((c1 + c2) / 2, yb - 8, 'основний крок  p_осн', 12, NEG, 'middle', bold=True))

    f.append(mtext(W / 2, H - 26,
                   ['AB довший за p_осн (тут ≈ 1.6 · p_осн), тож поки пара 1 не вийшла в B,',
                    'пара 2 вже ввійшла в A — контакт не переривається.  ε = AB / p_осн > 1'],
                   11, INK, 'middle'))
    render(os.path.join(IMG, 'contact-ratio.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 5 (для історичної вставки) — часова смуга «від циклоїди до евольвенти».
# Хто що зробив і НА ЯКОМУ РІВНІ: ідея/опис кривої (синє), теорія-закон-
# математика (зелене), практичний стандарт (червоне). Данець, троє французів,
# швейцарець і двоє британців за ~170 років. Наочно видно розрив між теорією
# Ойлера (~1760) і стандартом Вілліса (~1840): крива чекала на свою причину.
# ═══════════════════════════════════════════════════════════════════════════
def fig_history_timeline():
    W, H = 900, 450
    f = [text(W / 2, 30, 'Від циклоїди до евольвенти: хто що зробив',
              17, INK, 'middle', bold=True)]
    f.append(text(W / 2, 52,
                  'данець, троє французів, швейцарець і двоє британців — за ~170 років',
                  12, MUTED, 'middle'))

    y = 235
    x0, x1 = 80, 820
    yr0, yr1 = 1665, 1900

    def X(yr):
        return x0 + (yr - yr0) / (yr1 - yr0) * (x1 - x0)

    # вісь часу зі стрілкою праворуч
    f.append(line(x0, y, x1 + 6, y, color=MUTED, sw=1.6))
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>' % (
        x1 + 16, y, x1 + 6, y - 4, x1 + 6, y + 4, MUTED))
    f.append(text(x1 + 2, y - 10, 'час', 11, MUTED, 'end'))

    def event(xc, head, contrib, color, above):
        size = 12
        w = max(text_width(head, size, True), text_width(contrib, size)) + 22
        h = 2 * size * 1.3 + 16
        cy = 150 if above else 322
        edge = cy + h / 2 if above else cy - h / 2
        f.append(line(xc, y, xc, edge, color=color, sw=1.4))
        f.append(circle(xc, y, 5, fill=color, stroke=color, sw=1))
        f.append(rect(xc - w / 2, cy - h / 2, w, h, fill=FILL, stroke=color, sw=1.7, rx=7))
        f.append(text(xc, cy - 4, head, size, INK, 'middle', bold=True))
        f.append(text(xc, cy + size * 1.15, contrib, size, color, 'middle'))

    event(X(1674), 'Ремер · 1674', 'епіциклоїда: ідея', NEG, True)
    event(X(1694), 'Ла Ір · 1694', 'епіциклоїда: теорія', NEG, False)
    event(X(1733), 'Камю · 1733', 'закон зачеплення', FIELD, True)
    event(X(1760), 'Ойлер · ~1760', 'евольвента: теорія', FIELD, False)
    event(X(1841), 'Вілліс · 1838–41', 'евольвента: стандарт', POS, True)
    event(X(1900), 'XX століття', 'стандарт 20°', POS, False)

    # легенда трьох рівнів
    ly = 415
    leg = [(NEG, 'ідея / опис кривої', 128),
           (FIELD, 'теорія: закон і математика', 348),
           (POS, 'практичний стандарт', 648)]
    for color, lbl, lx in leg:
        f.append(circle(lx, ly - 4, 6, fill=color, stroke=color, sw=1))
        f.append(text(lx + 12, ly, lbl, 12, INK, 'start'))

    render(os.path.join(IMG, 'history-timeline.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 6 (math) — геометрія евольвенти в одному прямокутному трикутнику
# O–T–P: катет OT = r_осн, катет TP = r_осн·t (= довжина розмотаної нитки =
# дуга P₀T), гіпотенуза OP = r. Звідси одразу tan α = t, cos α = r_осн/r, а
# полярний кут точки від початку евольвенти — це inv α = tan α − α.
# ═══════════════════════════════════════════════════════════════════════════
def fig_involute_triangle():
    W, H = 780, 560
    f = [text(W / 2, 30, 'Один трикутник евольвенти: кут тиску α, радіус r, функція inv α',
              16, INK, 'middle', bold=True)]

    O = (250, 330); rb = 165
    t = 1.0                                       # катети рівні → α = 45°, усе легко читати

    def touch(a): return (O[0] + rb * math.cos(a), O[1] - rb * math.sin(a))

    def invp(a):
        x = rb * (math.cos(a) + a * math.sin(a))
        y = rb * (math.sin(a) - a * math.cos(a))
        return (O[0] + x, O[1] - y)

    P0 = invp(0.0)                                # старт евольвенти на колі
    T = touch(t)                                  # точка сходу нитки
    P = invp(t)                                   # поточна точка евольвенти

    # основне коло
    f.append(circle(O[0], O[1], rb, fill=PITCH, stroke=INK, sw=1.6))
    f.append(circle(O[0], O[1], 4, fill=INK, stroke=INK, sw=1))
    f.append(text(O[0] - 14, O[1] + 6, 'O', 13, INK, 'end', bold=True))
    f.append(text(O[0] - rb - 10, O[1] + 52, 'основне коло', 12, INK, 'end'))

    # виділена дуга P₀→T (її довжина = r_осн·t = довжині нитки)
    f.append(arc(O[0], O[1], rb, 0.0, -t, POS, sw=4.2))
    amid = -t / 2
    f.append(text(O[0] + (rb + 26) * math.cos(amid), O[1] + (rb + 26) * math.sin(amid),
                  'дуга P₀T = r_осн·t', 12, POS, 'start', bold=True))

    # сама евольвента P₀→P (суцільна) + бліда неперервність далі
    pts = ['%.1f %.1f' % invp(i / 40 * t) for i in range(41)]
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (' L '.join(pts), FIELD))
    ptl = ['%.1f %.1f' % invp(t + i / 30 * 0.9) for i in range(31)]
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="1.4" '
             'stroke-dasharray="4,4"/>' % (' L '.join(ptl), FIELD))
    f.append(text(P0[0] + 6, P0[1] + 20, 'P₀', 12, FIELD, 'start', bold=True))

    # трикутник O–T–P
    f.append(line(O[0], O[1], T[0], T[1], color=NEG, sw=2.4))     # OT = радіус основного кола
    f.append(line(T[0], T[1], P[0], P[1], color=FIELD, sw=2.8))   # TP = нитка = нормаль
    f.append(line(O[0], O[1], P[0], P[1], color=INK, sw=1.8, dash='6,4'))  # OP = r

    # прямий кут при T (нитка ⟂ радіус)
    ur = ((O[0] - T[0]) / rb, (O[1] - T[1]) / rb)
    up = ((P[0] - T[0]), (P[1] - T[1])); lp = math.hypot(*up); up = (up[0] / lp, up[1] / lp)
    s = 13
    q1 = (T[0] + ur[0] * s, T[1] + ur[1] * s)
    q2 = (q1[0] + up[0] * s, q1[1] + up[1] * s)
    q3 = (T[0] + up[0] * s, T[1] + up[1] * s)
    f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="1.3"/>' % (q1[0], q1[1], q2[0], q2[1],
                                                    q3[0], q3[1], MUTED))

    # точки
    f.append(circle(T[0], T[1], 4.5, fill=NEG, stroke=NEG, sw=1))
    f.append(circle(P[0], P[1], 5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(T[0] + 8, T[1] - 6, 'T', 13, NEG, 'start', bold=True))
    f.append(text(P[0] + 10, P[1] + 4, 'P', 13, FIELD, 'start', bold=True))

    # підписи сторін
    f.append(text((O[0] + T[0]) / 2 - 16, (O[1] + T[1]) / 2 - 4, 'r_осн', 13, NEG, 'end', bold=True))
    f.append(text((T[0] + P[0]) / 2 + 12, (T[1] + P[1]) / 2 - 6, 'r_осн·t', 13, FIELD, 'start', bold=True))
    f.append(text((O[0] + P[0]) / 2 + 4, (O[1] + P[1]) / 2 + 20, 'r', 13, INK, 'middle', bold=True))

    # кути при O: inv α (P0→P) і α (P→T)
    bP = math.atan2(P[1] - O[1], P[0] - O[0])
    bT = math.atan2(T[1] - O[1], T[0] - O[0])
    f.append(arc(O[0], O[1], 34, 0.0, bP, INK, sw=1.6))
    f.append(arc(O[0], O[1], 46, bP, bT, POS, sw=1.8))
    ma = (bP + bT) / 2
    f.append(text(O[0] + 66 * math.cos(ma), O[1] + 66 * math.sin(ma), 'α', 15, POS, 'middle', bold=True))
    f.append(text(O[0] + 120, O[1] + 44, 'inv α', 12, INK, 'start', bold=True))
    f.append(line(O[0] + 118, O[1] + 40, O[0] + 40, O[1] + 8, color=INK, sw=0.9))

    f.append(mtext(W / 2, H - 52,
                   ['r = r_осн·√(1 + t²)     cos α = r_осн / r     tan α = t',
                    'inv α = tan α − α  —  полярний кут точки від початку евольвенти'],
                   13, INK, 'middle', lh=1.5))
    render(os.path.join(IMG, 'involute-triangle.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 7 (math) — довжина активної ділянки AB як розклад по трьох відрізках
# лінії зачеплення: T₁B = √(r_a1²−r_осн1²), AT₂ = √(r_a2²−r_осн2²) і повний
# T₁T₂ = a·sin φ. Активна ділянка AB = T₁B + AT₂ − T₁T₂; ε = AB / p_осн.
# ═══════════════════════════════════════════════════════════════════════════
def fig_path_of_contact():
    W, H = 820, 560
    f = [text(W / 2, 30, 'Активна ділянка AB: тіп-кола крають лінію зачеплення',
              16, INK, 'middle', bold=True)]

    phi = math.radians(20)
    O1 = (235, 300); r1 = 115
    a = 250
    r2 = a - r1                                   # 135
    O2 = (O1[0] + a, O1[1])
    P = (O1[0] + r1, O1[1])
    rb1, rb2 = r1 * math.cos(phi), r2 * math.cos(phi)
    ra1, ra2 = r1 + 15, r2 + 15
    u = (math.sin(phi), math.cos(phi))            # напрям лінії зачеплення (вниз-праворуч)
    n = (math.cos(phi), -math.sin(phi))           # нормаль до неї (для винесення дужок)

    def foot(O):
        sp = (O[0] - P[0]) * u[0] + (O[1] - P[1]) * u[1]
        return (P[0] + sp * u[0], P[1] + sp * u[1])
    T1, T2 = foot(O1), foot(O2)
    lB = math.sqrt(ra1 ** 2 - rb1 ** 2)           # T1→B
    lA = math.sqrt(ra2 ** 2 - rb2 ** 2)           # T2→A
    B = (T1[0] + lB * u[0], T1[1] + lB * u[1])
    A = (T2[0] - lA * u[0], T2[1] - lA * u[1])

    # основні кола (суцільні) й ділильні (бліді)
    f.append(circle(O1[0], O1[1], r1, fill='none', stroke=MUTED, sw=1.0))
    f.append(circle(O2[0], O2[1], r2, fill='none', stroke=MUTED, sw=1.0))
    f.append(circle(O1[0], O1[1], rb1, fill='none', stroke=INK, sw=1.7))
    f.append(circle(O2[0], O2[1], rb2, fill='none', stroke=INK, sw=1.7))
    # кола вершин (тіп-кола) — тонкий контур
    f.append(circle(O1[0], O1[1], ra1, fill='none', stroke=POS, sw=1.0))
    f.append(circle(O2[0], O2[1], ra2, fill='none', stroke=POS, sw=1.0))

    for O, nm in ((O1, 'O₁'), (O2, 'O₂')):
        f.append(circle(O[0], O[1], 4, fill=INK, stroke=INK, sw=1))
        f.append(text(O[0], O[1] + 20, nm, 13, INK, 'middle', bold=True))

    # перпендикуляри осі→точки дотику (= основні радіуси)
    for O, T in ((O1, T1), (O2, T2)):
        f.append(line(O[0], O[1], T[0], T[1], color=NEG, sw=1.1, dash='4,3'))

    # лінія зачеплення (уся) і активна ділянка AB (жирна)
    L0 = (T1[0] - 26 * u[0], T1[1] - 26 * u[1])
    L1 = (T2[0] + 26 * u[0], T2[1] + 26 * u[1])
    f.append(line(L0[0], L0[1], L1[0], L1[1], color=MUTED, sw=1.4))
    f.append(line(A[0], A[1], B[0], B[1], color=FIELD, sw=5))

    for pt, col in ((T1, NEG), (A, INK), (B, INK), (T2, NEG), (P, POS)):
        f.append(circle(pt[0], pt[1], 4, fill=col, stroke=col, sw=1))
    f.append(text(T1[0] - 12, T1[1] + 2, 'T₁', 12, NEG, 'end', bold=True))
    f.append(text(T2[0] + 12, T2[1] + 6, 'T₂', 12, NEG, 'start', bold=True))
    f.append(text(A[0] - 12, A[1] - 2, 'A', 13, INK, 'end', bold=True))
    f.append(text(B[0] + 12, B[1] + 2, 'B', 13, INK, 'start', bold=True))
    f.append(text(P[0] + 12, P[1] - 8, 'полюс P', 12, POS, 'start', bold=True))
    f.append(text((A[0] + B[0]) / 2 - 40, (A[1] + B[1]) / 2 + 6,
                  'активна AB', 12, FIELD, 'end', bold=True))

    # дужка T₁→B (винесена по +n) і дужка A→T₂ (винесена по −n), плюс повний T₁T₂
    def bracket(P1, P2, off, col, lab):
        a1 = (P1[0] + n[0] * off, P1[1] + n[1] * off)
        a2 = (P2[0] + n[0] * off, P2[1] + n[1] * off)
        f.append(line(P1[0], P1[1], a1[0], a1[1], color=col, sw=0.9, dash='3,3'))
        f.append(line(P2[0], P2[1], a2[0], a2[1], color=col, sw=0.9, dash='3,3'))
        f.append(line(a1[0], a1[1], a2[0], a2[1], color=col, sw=1.5))
        mx, my = (a1[0] + a2[0]) / 2, (a1[1] + a2[1]) / 2
        sgn = 1 if off >= 0 else -1                 # тримати підпис ДАЛІ від AB, з того ж боку, що й дужка
        f.append(text(mx + n[0] * 30 * sgn, my + n[1] * 30 * sgn, lab, 12, col, 'middle', bold=True))
    bracket(T1, B, 52, NEG, '√(r_a1²−r_осн1²)')
    bracket(A, T2, -52, POS, '√(r_a2²−r_осн2²)')
    bracket(T1, T2, -110, INK, 'a·sin φ')

    f.append(mtext(W / 2, H - 44,
                   ['AB = √(r_a1²−r_осн1²) + √(r_a2²−r_осн2²) − a·sin φ',
                    'коефіцієнт перекриття  ε = AB / p_осн = AB / (π·m·cos φ)'],
                   13, INK, 'middle', lh=1.5))
    render(os.path.join(IMG, 'path-of-contact.svg'), W, H, *f)


# ═══════════════════════════════════════════════════════════════════════════
# Фігура 8 (math) — межа підрізу. Рейка-гребінка, обкочуючись, підрізає зуб,
# якщо її лінія вершин перетинає лінію зачеплення ЗА точкою інтерференції T
# (дотик лінії зачеплення до основного кола). Умова: h_a ≤ r·sin²φ → N ≥ 2/sin²φ.
# ═══════════════════════════════════════════════════════════════════════════
def fig_undercut():
    W, H = 840, 580
    f = [text(W / 2, 30, 'Межа підрізу: лінія вершин рейки і точка інтерференції T',
              16, INK, 'middle', bold=True)]

    phi = math.radians(20)
    O = (410, 96); r = 210
    rb = r * math.cos(phi)
    P = (O[0], O[1] + r)                          # полюс — низ ділильного кола
    u = (math.cos(phi), -math.sin(phi))           # лінія зачеплення: угору-праворуч від P

    # точка інтерференції T = проекція O на лінію зачеплення (дотик до основного кола)
    sT = (O[0] - P[0]) * u[0] + (O[1] - P[1]) * u[1]
    T = (P[0] + sT * u[0], P[1] + sT * u[1])       # PT = r·sin φ

    # часткові дуги ділильного й основного кіл біля полюса
    base = math.atan2(P[1] - O[1], P[0] - O[0])    # напрям на P (вниз)
    f.append(arc(O[0], O[1], r, base - 0.66, base + 0.44, MUTED, sw=1.3))
    f.append(arc(O[0], O[1], rb, base - 0.66, base + 0.44, INK, sw=1.7))
    f.append(circle(O[0], O[1], 4, fill=INK, stroke=INK, sw=1))
    f.append(text(O[0] + 8, O[1] - 2, 'O', 12, INK, 'start', bold=True))
    f.append(line(O[0], O[1], P[0], P[1], color=MUTED, sw=1.0, dash='5,4'))
    f.append(text(O[0] - r + 6, O[1] + r - 52, 'ділильне коло', 11, MUTED, 'start'))
    f.append(text(T[0] + 40, T[1] - 30, 'основне коло', 11, INK, 'start'))

    # перпендикуляр O→T (= r_осн), точка інтерференції
    f.append(line(O[0], O[1], T[0], T[1], color=NEG, sw=1.1, dash='4,3'))
    f.append(circle(T[0], T[1], 5, fill=NEG, stroke=NEG, sw=1))
    f.append(text(T[0] - 10, T[1] - 8, 'T', 13, NEG, 'end', bold=True))

    # лінія зачеплення через P і T, з обох боків
    LA = (P[0] - 70 * u[0], P[1] - 70 * u[1])
    LB = (T[0] + 150 * u[0], T[1] + 150 * u[1])
    f.append(line(LA[0], LA[1], LB[0], LB[1], color=FIELD, sw=2.4))
    f.append(text(LB[0] + 4, LB[1] - 4, 'лінія зачеплення', 11, FIELD, 'start', bold=True))

    # полюс
    f.append(circle(P[0], P[1], 5, fill=POS, stroke=POS, sw=1))
    f.append(text(P[0] - 10, P[1] + 6, 'P', 13, POS, 'end', bold=True))

    # PT = r·sin φ  (винесений підпис)
    nn = (math.sin(phi), math.cos(phi))
    mid = ((P[0] + T[0]) / 2, (P[1] + T[1]) / 2)
    f.append(text(mid[0] + nn[0] * 20 + 6, mid[1] + nn[1] * 20, 'PT = r·sin φ', 12, NEG, 'start', bold=True))

    # рейка: ділильна пряма (горизонталь через P) і лінія вершин на висоті h_a
    ha = 66
    yv = P[1]                                     # ділильна пряма рейки
    ya = P[1] - ha                                # лінія вершин (до колеса, вгору)
    f.append(line(150, yv, 700, yv, color=MUTED, sw=1.2, dash='6,4'))
    f.append(text(158, yv + 16, 'ділильна пряма рейки', 11, MUTED, 'start'))
    f.append(line(150, ya, 700, ya, color=POS, sw=1.6))
    f.append(text(158, ya - 8, 'лінія вершин рейки', 11, POS, 'start', bold=True))

    # висота головки h_a (вертикальна дужка ліворуч)
    xg = 205
    f.append(line(xg, yv, xg, ya, color=INK, sw=1.2))
    f.append(line(xg - 5, yv, xg + 5, yv, color=INK, sw=1.2))
    f.append(line(xg - 5, ya, xg + 5, ya, color=INK, sw=1.2))
    f.append(text(xg - 10, (yv + ya) / 2 + 4, 'h_a', 12, INK, 'end', bold=True))

    # кілька зубів рейки (трапеції) з боками під кутом φ
    def rack_tooth(xc):
        half = 24; slope = math.tan(phi) * ha
        pts = [(xc - half - slope, yv), (xc - half, ya),
               (xc + half, ya), (xc + half + slope, yv)]
        d = 'M ' + ' L '.join('%.1f %.1f' % p for p in pts)
        return '<path d="%s" fill="none" stroke="%s" stroke-width="1.3"/>' % (d, MUTED)
    for xc in (300, 400, 500):
        f.append(rack_tooth(xc))

    # точка X — перетин лінії вершин з лінією зачеплення (на відстані h_a/sin φ від P)
    sX = ha / math.sin(phi)
    X = (P[0] + sX * u[0], P[1] + sX * u[1])
    f.append(circle(X[0], X[1], 5, fill=POS, stroke=POS, sw=1))
    f.append(text(X[0] + 8, X[1] + 2, 'X', 13, POS, 'start', bold=True))
    f.append(text(X[0] + 8, X[1] + 20, 'PX = h_a / sin φ', 12, POS, 'start', bold=True))

    # висновок: X за T (далі від P) → підріз
    f.append(textbox(W / 2, H - 92,
                     'X далі від P, ніж T  ⇒  h_a > r·sin²φ  ⇒  зуб підрізаний',
                     12, pad=8, fill=FILL, stroke=POS, sw=1.4)[0])
    f.append(mtext(W / 2, H - 44,
                   ['без підрізу:  h_a ≤ r·sin²φ   ⇒   N ≥ 2·a* / sin²φ',
                    'a*=1:   φ = 14.5° → 32 зуба     φ = 20° → 18 (межа 17)     φ = 25° → 12'],
                   12, INK, 'middle', lh=1.5))
    render(os.path.join(IMG, 'undercut.svg'), W, H, *f)


fig_conjugate()
fig_involute()
fig_line_of_action()
fig_contact_ratio()
fig_history_timeline()
fig_involute_triangle()
fig_path_of_contact()
fig_undercut()
print('Done.')
