# -*- coding: utf-8 -*-
"""Фігури ДЕТАЛЬНОЇ статті «Обхід перешкод» (obstacle-avoidance-d).
Чистий Python + svgkit. Вивід у ./img/ поряд із фігурами базової статті —
імена нові, щоб не перекривати наявні."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
def out(name): return os.path.join(IMG, name)


def vec(x1, y1, x2, y2, color, sw=2.4, hl=10.0, hw=5.0):
    """Кольорова стрілка (лінія + власна голівка того ж кольору)."""
    ang = math.atan2(y2 - y1, x2 - x1)
    L = math.hypot(x2 - x1, y2 - y1)
    if L < hl:
        hl = max(3.0, L * 0.6)
    bx = x2 - hl * math.cos(ang)
    by = y2 - hl * math.sin(ang)
    px, py = -math.sin(ang), math.cos(ang)
    p1 = (bx + hw * px, by + hw * py)
    p2 = (bx - hw * px, by - hw * py)
    s = line(x1, y1, bx, by, color=color, sw=sw)
    s += ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
          % (x2, y2, p1[0], p1[1], p2[0], p2[1], color))
    return s


def dot(cx, cy, r, fill, stroke=None, sw=1.2):
    return circle(cx, cy, r, fill=fill, stroke=(stroke or fill), sw=sw)


# ── 1) obstacle-enlargement.svg — розширення перешкоди на радіус апарата ─────
def fig_enlargement():
    W, H = 780, 430
    frags = [text(W / 2, 28, "Габарит апарата: перешкоду роздувають, апарата стискають у точку",
                  size=15, bold=True)]

    # Ліва панель: наївно — апарат-точка тре стіну
    lx = 40
    frags.append(text(lx + 150, 58, "Наївно: апарат — точка", size=12.5, color=POS, bold=True))
    frags.append(rect(lx, 70, 300, 320, fill="#fff7f6", stroke="#e5b7b0", sw=1.2, rx=8))
    # дві перешкоди з вузькою щілиною
    o1x, o1y, o1w, o1h = lx + 60, 150, 40, 150
    o2x, o2y, o2w, o2h = lx + 175, 150, 40, 150
    frags.append(rect(o1x, o1y, o1w, o1h, fill="#3a3f45", stroke="#3a3f45", sw=1, rx=3))
    frags.append(rect(o2x, o2y, o2w, o2h, fill="#3a3f45", stroke="#3a3f45", sw=1, rx=3))
    gap_c = (o1x + o1w + o2x) / 2
    # апарат-точка «протискується» в щілину, але тілом задіває
    rcx, rcy = gap_c, 340
    R = 26  # справжній радіус апарата
    frags.append(circle(rcx, rcy, R, fill="none", stroke=POS, sw=1.4))
    frags.append(dot(rcx, rcy, 3.0, POS))
    frags.append(vec(rcx, rcy, gap_c, 130, NEG, sw=2.0))
    # позначка щілини
    frags.append(line(o1x + o1w, 138, o2x, 138, color=MUTED, sw=1.0, dash="3 3"))
    frags.append(text(gap_c, 128, "щілина < 2R", size=10.5, color=POS))
    frags.append(text(gap_c, 372, "тіло радіуса R\nне влазить, а точка йде", size=10, color=INK))
    frags.append(text(lx + 150, 405, "гістограма каже «вільно» — апарат тараном у край",
                      size=10.5, color=POS, italic=True))

    # Права панель: розширення на R — щілина сама «затягується»
    rx0 = 440
    frags.append(text(rx0 + 150, 58, "Правильно: перешкода + R", size=12.5, color=FIELD, bold=True))
    frags.append(rect(rx0, 70, 300, 320, fill="#f2fbf5", stroke="#a9dcbb", sw=1.2, rx=8))
    p1x, p1y, p1w, p1h = rx0 + 60, 150, 40, 150
    p2x, p2y, p2w, p2h = rx0 + 175, 150, 40, 150
    grow = R  # розширення на радіус
    # «ореол» розширення (світліший) навколо кожної перешкоди
    frags.append(rect(p1x - grow, p1y - grow, p1w + 2 * grow, p1h + 2 * grow,
                      fill="#cdecd8", stroke="#8fcea6", sw=1.0, rx=8))
    frags.append(rect(p2x - grow, p2y - grow, p2w + 2 * grow, p2h + 2 * grow,
                      fill="#cdecd8", stroke="#8fcea6", sw=1.0, rx=8))
    frags.append(rect(p1x, p1y, p1w, p1h, fill="#3a3f45", stroke="#3a3f45", sw=1, rx=3))
    frags.append(rect(p2x, p2y, p2w, p2h, fill="#3a3f45", stroke="#3a3f45", sw=1, rx=3))
    # тепер розширені перешкоди перекрилися — прохід зник
    gp_c = (p1x + p1w + p2x) / 2
    frags.append(text(gp_c, 225, "×", size=30, color=POS, bold=True))
    frags.append(dot(gp_c, 340, 3.0, FIELD))
    frags.append(text(gp_c, 372, "апарат — точка,\nпрохід закрився сам", size=10, color=INK))
    frags.append(text(rx0 + 150, 405, "щілина < 2R «затяглася» — точка туди не піде",
                      size=10.5, color=FIELD, italic=True))

    render(out("obstacle-enlargement.svg"), W, H, *frags)


# ── 2) braking-distance.svg — гальмівний шлях і безпечна швидкість ───────────
def fig_braking():
    W, H = 780, 360
    frags = [text(W / 2, 28, "Гальмівний шлях: чому «встигну повернути» — це про кінематику",
                  size=15, bold=True)]

    baseY = 250
    x0 = 60
    xw = 660
    frags.append(line(x0, baseY, x0 + xw, baseY, color=INK, sw=2))
    # апарат на старті
    rcx = x0 + 40
    frags.append(circle(rcx, baseY - 16, 15, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(rcx, baseY - 40, "v", size=13, color=NEG, italic=True, bold=True))
    frags.append(vec(rcx + 16, baseY - 16, rcx + 70, baseY - 16, NEG, sw=2.2))

    # ділянка реакції (лаг)
    xr = rcx + 90
    frags.append(rect(xr, baseY - 8, 90, 16, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    frags.append(text(xr + 45, baseY + 28, "лаг реакції", size=10.5, color=POS))
    frags.append(text(xr + 45, baseY + 44, "v·t_lag", size=11, color=POS, italic=True))

    # ділянка гальмування (крива-клин)
    xb = xr + 90
    xbw = 250
    frags.append(('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f L %.1f %.1f Z" '
                  'fill="#fff3d6" stroke="#d79a1e" stroke-width="1.2"/>'
                  % (xb, baseY - 8, xb + xbw * 0.55, baseY - 22, xb + xbw, baseY - 2,
                     xb + xbw, baseY + 8)) )
    frags.append(rect(xb, baseY - 8, xbw, 16, fill="none", stroke="#d79a1e", sw=0.0, rx=0))
    frags.append(text(xb + xbw / 2, baseY + 28, "гальмівний шлях", size=10.5, color="#b5800f"))
    frags.append(text(xb + xbw / 2, baseY + 44, "v² / (2a)", size=12, color="#b5800f", italic=True, bold=True))

    # перешкода в кінці
    obx = xb + xbw + 30
    frags.append(rect(obx, baseY - 60, 26, 68, fill="#3a3f45", stroke="#3a3f45", sw=1, rx=3))
    frags.append(text(obx + 13, baseY - 70, "перешкода", size=10.5, color=INK))
    # мірна лінія «повний шлях зупинки» (нижче, щоб не перетинати підпис-рамку)
    measY = baseY - 92
    frags.append(line(rcx, measY, obx, measY, color=MUTED, sw=1.0, dash="4 3"))
    frags.append(vec(obx - 4, measY, obx, measY, MUTED, sw=1.0))
    frags.append(vec(rcx + 4, measY, rcx, measY, MUTED, sw=1.0))
    # рамка-підпис — над мірною лінією, з білою заливкою (лінія її не перетинає)
    b, bw, bh = textbox((rcx + obx) / 2, baseY - 128, "повний шлях зупинки d_stop = v·t_lag + v²/(2a)",
                        size=11.5, color=INK, bold=True, fill="#ffffff", stroke=MUTED, sw=1.2)
    frags.append(b)

    # нижній висновок-нерівність
    b2, b2w, b2h = textbox(W / 2, H - 34,
                           "безпечно, поки d_stop ≤ (відстань до перешкоди):  v·t_lag + v²/(2a) ≤ d",
                           size=12.5, color=FIELD, bold=True, fill="#f2fbf5", stroke=FIELD, sw=1.4)
    frags.append(b2)

    render(out("braking-distance.svg"), W, H, *frags)


# ── 3) dwa-velocity-space.svg — три множини у просторі швидкостей ────────────
def fig_dwa_space():
    W, H = 780, 470
    frags = [text(W / 2, 28, "Динамічне вікно: рішення живе у просторі швидкостей (v, ω)",
                  size=15, bold=True)]

    # осі: v вертикально (вгору = швидше вперед), ω горизонтально
    ox, oy = 290, 400          # початок координат (v=0, ω=0)
    axw, axh = 440, 320
    frags.append(vec(ox, oy, ox, oy - axh, INK, sw=1.8))
    frags.append(text(ox - 14, oy - axh - 4, "v", size=14, color=INK, italic=True, bold=True))
    frags.append(text(ox - 30, oy - axh + 12, "вперед", size=10, color=MUTED, anchor="start"))
    frags.append(vec(ox - axw / 2, oy, ox + axw / 2, oy, INK, sw=1.8))
    frags.append(text(ox + axw / 2 + 6, oy + 4, "ω", size=14, color=INK, italic=True, bold=True, anchor="start"))
    frags.append(text(ox - axw / 2 - 4, oy + 20, "◀ ліворуч", size=10, color=MUTED, anchor="start"))
    frags.append(text(ox + axw / 2 - 60, oy + 20, "праворуч ▶", size=10, color=MUTED, anchor="start"))

    # Vs — усі можливі швидкості машини (велика світла рамка)
    vs_w, vs_h = axw - 40, axh - 40
    frags.append(rect(ox - vs_w / 2, oy - vs_h, vs_w, vs_h, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(ox + vs_w / 2 - 6, oy - vs_h + 16, "Vs: усе, що вміє машина", size=10.5,
                      color=MUTED, anchor="end"))

    # поточний стан (v0, ω0)
    v0x, v0y = ox + 60, oy - 150
    # Vd — динамічне вікно: маленький прямокутник навколо стану (розгін за 1 такт)
    dw, dh = 150, 120
    frags.append(rect(v0x - dw / 2, v0y - dh / 2, dw, dh, fill="#eef3fe", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(v0x, v0y - dh / 2 - 8, "Vd: досяжне за 1 такт", size=10.5, color=NEG))
    frags.append(dot(v0x, v0y, 4.5, NEG))
    frags.append(text(v0x + 10, v0y + 4, "поточний (v₀, ω₀)", size=10, color=NEG, anchor="start"))

    # Va — допустимі (з яких устигнути загальмувати): відсікаємо верх (зашвидко)
    # покажемо як зелену «стелю» — крива нижче якої безпечно
    cutY = oy - 205
    frags.append(('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" stroke="%s" '
                  'stroke-width="2.2"/>' % (ox - vs_w / 2, cutY + 30, ox, cutY - 20,
                                            ox + vs_w / 2, cutY + 40, FIELD)))
    frags.append(text(ox - vs_w / 2 + 8, cutY + 18, "межа Va", size=10.5, color=FIELD, anchor="start", bold=True))
    frags.append(text(ox, cutY - 30, "вище — не встигнеш загальмувати перед перешкодою",
                      size=10, color=FIELD))

    # перетин: заштрихована зона (Vd нижче межі Va) = з чого вибираємо
    # тут просто підсвітимо нижню частину Vd
    sel_y = max(v0y - dh / 2, cutY + 30)
    sel_h = (v0y + dh / 2) - sel_y
    if sel_h > 4:
        frags.append(rect(v0x - dw / 2 + 2, sel_y, dw - 4, sel_h,
                          fill="#d6f2df", stroke="none", sw=0))
    frags.append(dot(v0x - 30, v0y + 20, 3.2, INK))
    frags.append(dot(v0x + 10, v0y + 30, 3.2, INK))
    frags.append(dot(v0x + 35, v0y + 12, 3.2, INK))
    frags.append(text(v0x, v0y + dh / 2 + 42, "перебираємо пари тут:\nVs ∩ Va ∩ Vd",
                      size=10.5, color=INK, bold=True))

    render(out("dwa-velocity-space.svg"), W, H, *frags)


# ── 4) dwa-arc-scoring.svg — оцінка дуг трьома доданками ─────────────────────
def fig_dwa_arcs():
    W, H = 780, 430
    frags = [text(W / 2, 28, "Кожна пара (v, ω) — це дуга; оцінюємо три доданки й беремо найкращу",
                  size=15, bold=True)]

    rcx, rcy = 140, 300
    frags.append(circle(rcx, rcy, 14, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(rcx, rcy + 34, "апарат", size=10.5, color=INK))

    # ціль угорі-праворуч
    gx, gy = 700, 90
    frags.append(circle(gx, gy, 9, fill="#ffffff", stroke=FIELD, sw=2.4))
    frags.append(dot(gx, gy, 3.5, FIELD))
    frags.append(text(gx, gy - 16, "ціль", size=11, color=FIELD, bold=True))
    frags.append(line(rcx, rcy, gx, gy, color=FIELD, sw=1.0, dash="5 4"))

    # перешкода посередині
    obx, oby = 430, 205
    frags.append(circle(obx, oby, 30, fill="#3a3f45", stroke="#3a3f45", sw=1))
    frags.append(text(obx, oby + 3, "×", size=20, color="#ffffff", bold=True))
    frags.append(text(obx, oby - 40, "перешкода", size=10.5, color=INK))

    def arc(cx, cy, r, a0, a1, color, sw, dash=None):
        # дуга кола (cx,cy) радіуса r від кута a0 до a1 (рад), проти год.
        large = 1 if abs(a1 - a0) > math.pi else 0
        sweep = 1 if a1 > a0 else 0
        x1 = cx + r * math.cos(a0); y1 = cy + r * math.sin(a0)
        x2 = cx + r * math.cos(a1); y2 = cy + r * math.sin(a1)
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" fill="none" '
                'stroke="%s" stroke-width="%.1f"%s/>' % (x1, y1, r, r, large, sweep,
                                                          x2, y2, color, sw, d))

    # три дуги від апарата (центри поворотів праворуч від апарата по горизонталі)
    # дуга A — крута ліворуч (безпечна, але геть від цілі): відкинемо як «повільна/далеко»
    frags.append(arc(rcx, rcy - 120, 120, math.radians(90), math.radians(20), MUTED, 2.4))
    frags.append(text(rcx + 70, rcy - 150, "A: чисто, але\nвід цілі", size=10, color=MUTED, anchor="start"))

    # дуга B — прямо на ціль, але вганяється в перешкоду: ВІДКИНУТИ
    frags.append(arc(rcx, rcy - 300, 300, math.radians(90), math.radians(46), POS, 2.6, dash="6 4"))
    frags.append(text(rcx + 190, rcy - 70, "B: до цілі, але в перешкоду ✗", size=10.5, color=POS, anchor="start"))

    # дуга C — обхід перешкоди з боку цілі: ОБРАНА
    frags.append(arc(rcx, rcy - 210, 210, math.radians(90), math.radians(30), FIELD, 3.4))
    frags.append(text(rcx + 250, rcy - 200, "C: безпечно + до цілі + швидко ✓",
                      size=11, color=FIELD, anchor="start", bold=True))

    # табличка-формула ціни
    b, bw, bh = textbox(W / 2, H - 42,
                        "оцінка дуги  G = α·(до цілі) + β·(зазор до перешкоди) + γ·(швидкість);  дуги в перешкоду відкинуто",
                        size=11.5, color=INK, bold=True, fill="#f7f9fc", stroke=MUTED, sw=1.2)
    frags.append(b)

    render(out("dwa-arc-scoring.svg"), W, H, *frags)


# ── 5) collision-cone.svg — конус зіткнення у просторі швидкостей ────────────
def fig_collision_cone():
    W, H = 800, 440
    frags = [text(W / 2, 28, "Рухома перешкода: небезпечні не напрямки, а швидкості (конус зіткнення)",
                  size=15, bold=True)]

    # Ліва панель — сцена: апарат A, перешкода B рухається
    lx, ly = 60, 70
    frags.append(text(lx + 150, 58 + 6, "Сцена", size=12.5, color=INK, bold=True))
    frags.append(rect(lx, 78, 300, 320, fill="#f7f9fc", stroke=MUTED, sw=1.2, rx=8))
    Ax, Ay = lx + 60, 330
    frags.append(circle(Ax, Ay, 13, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(Ax, Ay + 28, "A (ми)", size=10.5, color=NEG))
    Bx, By = lx + 210, 150
    frags.append(circle(Bx, By, 22, fill="#f2d7d3", stroke=POS, sw=1.8))
    frags.append(text(Bx, By - 30, "B", size=11, color=POS, bold=True))
    # швидкість B
    frags.append(vec(Bx, By, Bx - 44, By + 30, POS, sw=2.2))
    frags.append(text(Bx - 60, By + 30, "v_B", size=11, color=POS, italic=True, anchor="end"))
    # лінія погляду A→B і дотичні (сектор зіткнення в геом. просторі)
    frags.append(line(Ax, Ay, Bx, By, color=MUTED, sw=0.9, dash="3 3"))

    # Права панель — простір швидкостей A: конус зіткнення
    rx0, ry0 = 440, 78
    frags.append(text(rx0 + 165, 58 + 6, "Простір швидкостей A", size=12.5, color=INK, bold=True))
    frags.append(rect(rx0, 78, 330, 320, fill="#ffffff", stroke=MUTED, sw=1.2, rx=8))
    cx, cy = rx0 + 60, 340   # v_A = 0
    frags.append(vec(cx, cy, cx, ry0 + 24, INK, sw=1.5))
    frags.append(vec(cx, cy, rx0 + 300, cy, INK, sw=1.5))
    frags.append(text(cx - 12, ry0 + 20, "v_y", size=11, color=INK, italic=True))
    frags.append(text(rx0 + 300, cy + 16, "v_x", size=11, color=INK, italic=True, anchor="end"))

    # конус, зсунутий на v_B (апекс у кінці вектора v_B)
    apx, apy = cx + 40, cy - 30   # апекс = v_B
    frags.append(dot(apx, apy, 4, POS))
    frags.append(text(apx + 6, apy + 14, "апекс = v_B", size=9.5, color=POS, anchor="start"))
    # дві ноги конуса
    leg1 = (apx + 200, apy - 150)
    leg2 = (apx + 230, apy - 20)
    frags.append(('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#fdecea" '
                  'stroke="%s" stroke-width="1.8" opacity="0.85"/>'
                  % (apx, apy, leg1[0], leg1[1], leg2[0], leg2[1], POS)))
    frags.append(text((apx + leg1[0] + leg2[0]) / 3 + 20, (apy + leg1[1] + leg2[1]) / 3,
                      "VO — швидкості,\nщо ведуть у зіткнення", size=10, color=POS))

    # безпечна швидкість — поза конусом
    safe = (apx + 40, apy - 130)
    frags.append(vec(cx, cy, safe[0], safe[1], FIELD, sw=2.6))
    frags.append(text(safe[0] + 6, safe[1] - 6, "обрана v_A\n(поза конусом)", size=10,
                      color=FIELD, anchor="start", bold=True))

    render(out("collision-cone.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_enlargement()
    fig_braking()
    fig_dwa_space()
    fig_dwa_arcs()
    fig_collision_cone()
    print("OK: obstacle-enlargement, braking-distance, dwa-velocity-space, dwa-arc-scoring, collision-cone")
