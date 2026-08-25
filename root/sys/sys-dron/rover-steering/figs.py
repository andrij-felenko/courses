# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Ровер».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: дві родини керма — диференційна проти Аккермана ─────────────────
# Наземний ровер повертає не тягою, як дрон, а самими колесами. Два способи:
# диференційна (по-різному крутити ліві й праві колеса — борт відстає, машина
# розвертається) та Аккерман (керовані передні колеса вивертають під різними
# кутами до спільного центра дуги). Показуємо обидва «згори».
def fig_two_families():
    W, H = 960, 500
    parts = []

    # ── ЛІВОРУЧ: диференційна (skid/differential) ──
    lx = 245
    ly = 235
    bw, bh = 120, 170
    # корпус
    parts.append(rect(lx - bw / 2, ly - bh / 2, bw, bh, fill="#eef2f7", stroke=INK, sw=2, rx=10))
    parts.append(text(lx, ly - bh / 2 - 46, "Диференційна", size=17, bold=True))
    parts.append(text(lx, ly - bh / 2 - 24, "(різна швидкість бортів)", size=12, color=MUTED))
    # чотири колеса (усі паралельні корпусу)
    for sx in (-1, 1):
        for sy in (-1, 1):
            wx = lx + sx * (bw / 2 + 14)
            wy = ly + sy * 48
            parts.append(rect(wx - 9, wy - 20, 18, 40, fill="#3a3f45", stroke=INK, sw=1.5, rx=4))
    # праві колеса швидше (довша стрілка), ліві повільніше
    parts.append(arrow(lx + bw / 2 + 14, ly - 60, lx + bw / 2 + 14, ly - 118, color=POS, sw=3))
    parts.append(text(lx + bw / 2 + 26, ly - 96, "праві\nшвидше", size=11, color=POS, anchor="start", bold=True))
    parts.append(arrow(lx - bw / 2 - 14, ly - 60, lx - bw / 2 - 14, ly - 90, color=NEG, sw=3))
    parts.append(text(lx - bw / 2 - 26, ly - 78, "ліві\nповільніше", size=11, color=NEG, anchor="end", bold=True))
    # результат: розворот на місці навколо центра
    parts.append('<path d="M %.1f %.1f A 40 40 0 1 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2.6" marker-end="url(#arrow)"/>'
                 % (lx + 40, ly - 6, lx - 6, ly + 40, FIELD))
    parts.append(text(lx, ly + 4, "розворот\nна місці", size=11, color=FIELD, bold=True))
    parts.append(text(lx, ly + bh / 2 + 40, "колеса завжди прямо;\nповертає РІЗНИЦЯ швидкостей",
                      size=11.5, color=INK))

    # ── ПРАВОРУЧ: Аккерман (car-like) ──
    rx = W - 250
    ry = 235
    parts.append(rect(rx - bw / 2, ry - bh / 2, bw, bh, fill="#eef2f7", stroke=INK, sw=2, rx=10))
    parts.append(text(rx, ry - bh / 2 - 46, "Аккерман", size=17, bold=True))
    parts.append(text(rx, ry - bh / 2 - 24, "(керовані передні колеса)", size=12, color=MUTED))
    # задні колеса — прямо
    for sx in (-1, 1):
        wx = rx + sx * (bw / 2 + 14)
        wy = ry + 48
        parts.append(rect(wx - 9, wy - 20, 18, 40, fill="#3a3f45", stroke=INK, sw=1.5, rx=4))
    # передні колеса — вивернуті (внутрішнє крутіше), around a common center to the right
    def wheel_rot(wx, wy, deg):
        a = math.radians(deg)
        # намалюємо повернутий прямокутник як 4 кути
        pts = []
        for dx, dy in [(-9, -20), (9, -20), (9, 20), (-9, 20)]:
            X = wx + dx * math.cos(a) - dy * math.sin(a)
            Y = wy + dx * math.sin(a) + dy * math.cos(a)
            pts.append("%.1f,%.1f" % (X, Y))
        return ('<polygon points="%s" fill="#3a3f45" stroke="%s" stroke-width="1.5"/>'
                % (" ".join(pts), INK))
    # праворуч поворот: внутрішнє (праве) колесо вивернуте крутіше
    parts.append(wheel_rot(rx + bw / 2 + 14, ry - 48, 33))   # праве переднє, крутіше
    parts.append(wheel_rot(rx - bw / 2 - 14, ry - 48, 20))   # ліве переднє, м'якше
    parts.append(text(rx + bw / 2 + 22, ry - 96, "внутрішнє\nкрутіше", size=10.5, color=POS, anchor="start", bold=True))
    parts.append(text(rx - bw / 2 - 22, ry - 96, "зовнішнє\nм'якше", size=10.5, color=NEG, anchor="end", bold=True))
    # спільний центр дуги праворуч, лінії-радіуси (тримаємо в межах полотна)
    ccx, ccy = rx + 190, ry + 48
    for wy in (ry + 48, ry - 48):
        parts.append(line(rx, wy, ccx, ccy, color="#c9cfd6", sw=1.4, dash="4,4"))
    parts.append(circle(ccx, ccy, 5, fill=FIELD, stroke=FIELD, sw=1))
    parts.append(text(ccx - 6, ccy + 20, "спільний\nцентр дуги", size=10.5, color=FIELD, anchor="end", bold=True))
    parts.append(text(rx, ry + bh / 2 + 40, "колеса вивертаються;\nповертає КУТ передніх коліс",
                      size=11.5, color=INK))

    box, bw2, bh2 = textbox(W / 2, H - 28,
                            "Наземний ровер повертає САМИМИ колесами: або різницею швидкостей бортів,\n"
                            "або кутом керованих коліс — тягою корпус не розвернути",
                            size=12.5, pad=11, fill=FILL, bold=True)
    parts.append(box)

    render("img/two-families.svg", W, H, *parts,
           title="Дві родини керма ровера: диференційна проти Аккермана")


# ── Фігура 2: неголономність — боком не поїдеш ───────────────────────────────
# Головна відмінність ровера від дрона й від вільної точки: колесо не ковзає
# вбік. Тому машина НЕ може миттю зсунутися боком — щоб дістатися точки збоку,
# мусить виписати дугу. Показуємо: заборонений прямий бічний хід (перекреслено)
# і дозволений об'їзд дугою.
def fig_nonholonomic():
    W, H = 940, 440
    parts = []

    # машинка (вид згори), дивиться вгору
    def car(cx, cy, col=INK, fill="#eef2f7"):
        parts.append(rect(cx - 26, cy - 40, 52, 80, fill=fill, stroke=col, sw=2, rx=9))
        parts.append(arrow(cx, cy - 40, cx, cy - 66, color=FIELD, sw=2.2))  # ніс
        for sx in (-1, 1):
            for sy in (-1, 1):
                parts.append(rect(cx + sx * 30 - 6, cy + sy * 26 - 14, 12, 28,
                                  fill="#3a3f45", stroke=col, sw=1.2, rx=3))

    # старт ліворуч, ціль — точка збоку (праворуч на тому ж рівні)
    sx0, sy0 = 210, 220
    tx, ty = 560, 220
    car(sx0, sy0)
    parts.append(circle(tx, ty, 9, fill=FIELD, stroke=FIELD, sw=1.5))
    parts.append(text(tx, ty - 20, "ціль", size=13, color=FIELD, bold=True, anchor="middle"))

    # ЗАБОРОНЕНО: прямий бічний хід
    parts.append(line(sx0 + 30, sy0, tx - 12, ty, color=POS, sw=3, dash="7,6"))
    # велике перекреслення
    mxx = (sx0 + tx) / 2
    parts.append(line(mxx - 26, sy0 - 26, mxx + 26, sy0 + 26, color=POS, sw=4))
    parts.append(line(mxx - 26, sy0 + 26, mxx + 26, sy0 - 26, color=POS, sw=4))
    parts.append(text(mxx, sy0 - 46, "боком — НЕ можна", size=14, color=POS, bold=True))
    parts.append(text(mxx, sy0 + 52, "колесо не ковзає вбік", size=11.5, color=POS))

    # ДОЗВОЛЕНО: об'їзд дугою (виїхати вперед, розвернутись, під'їхати)
    # проста S-дуга під ціль
    parts.append('<path d="M %.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="3" marker-end="url(#arrow)"/>'
                 % (sx0, sy0 - 40, sx0 + 30, sy0 - 150,
                    tx - 30, ty - 150, tx, ty - 12, NEG))
    parts.append(text((sx0 + tx) / 2, sy0 - 150, "дугою — можна",
                      size=14, color=NEG, bold=True))
    parts.append(text((sx0 + tx) / 2, sy0 - 128, "виїхати вперед, повернути, під'їхати",
                      size=11.5, color=NEG))

    box = fitbox(70, H - 78, W - 140, 52,
                 "Неголономна в'язь: ровер миттєво рухається лише вздовж свого носа й повертає.\n"
                 "Дістатися точки збоку можна тільки об'їздом-дугою — це формує всю навігацію ровера.",
                 size=13, fill="#eef6ff", stroke=NEG, sw=2)
    parts.append(box)

    render("img/nonholonomic.svg", W, H, *parts,
           title="Боком не поїдеш: неголономна в'язь ровера")


# ── Фігура 3: мікс бажання → колеса (диференційна) ───────────────────────────
# Пряме дзеркало «мікшера моторів», але для землі. Два бажання — ЛІНІЙНА
# швидкість v (уперед) і КУТОВА швидкість ω (розворот) — розкладаються на дві
# швидкості коліс: спільне v на обидва, а ω додає одному й віднімає в іншого.
def fig_diff_mix():
    W, H = 940, 470
    parts = []

    # ── зліва: два бажання ──
    bx = 150
    parts.append(text(bx, 70, "БАЖАННЯ", size=14, bold=True))
    # v — уперед
    parts.append(arrow(bx, 150, bx, 100, color=FIELD, sw=3.2))
    parts.append(text(bx + 16, 118, "v — уперед\n(лінійна швидкість)", size=12, color=FIELD, anchor="start", bold=True))
    # ω — розворот
    parts.append('<path d="M %.1f %.1f A 34 34 0 1 1 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="3" marker-end="url(#arrow)"/>'
                 % (bx + 34, 236, bx - 6, 280, POS))
    parts.append(text(bx + 16, 250, "ω — розворот\n(кутова швидкість)", size=12, color=POS, anchor="start", bold=True))

    # ── стрілка «розклад» ──
    parts.append(arrow(bx + 150, 200, bx + 250, 200, color=INK, sw=2.6))
    parts.append(text(bx + 200, 186, "розклад", size=12, color=MUTED, bold=True))

    # ── праворуч: два колеса ──
    wx = W - 300
    # корпус
    parts.append(rect(wx - 40, 120, 80, 160, fill="#eef2f7", stroke=INK, sw=2, rx=10))
    parts.append(arrow(wx, 120, wx, 92, color=FIELD, sw=2))
    parts.append(text(wx, 84, "ніс", size=11, color=FIELD, bold=True))
    # ліве / праве колесо
    parts.append(rect(wx - 40 - 20, 170, 20, 60, fill="#3a3f45", stroke=INK, sw=1.5, rx=4))
    parts.append(rect(wx + 40, 170, 20, 60, fill="#3a3f45", stroke=INK, sw=1.5, rx=4))
    parts.append(text(wx - 70, 250, "ліве", size=12, bold=True, anchor="middle"))
    parts.append(text(wx + 70, 250, "праве", size=12, bold=True, anchor="middle"))
    # знаки: v однаково обом; ω додає правому, віднімає лівому (розворот вліво)
    parts.append(text(wx - 70, 150, "v − ω·b", size=12.5, color=NEG, bold=True, anchor="middle"))
    parts.append(text(wx + 70, 150, "v + ω·b", size=12.5, color=POS, bold=True, anchor="middle"))

    # формули знизу
    box = fitbox(70, H - 150, W - 140, 66,
                 "v_лів = v − ω·b        v_прав = v + ω·b        (b — піввідстань між колесами)\n"
                 "спільне v — обом порівну (їдьмо вперед); ω — «+» одному колесу, «−» іншому (розворот).\n"
                 "Це той самий мікшер, що й у дрона, лише вихід — швидкості коліс, а не оберти гвинтів.",
                 size=13, fill="#e9f7ef", stroke=FIELD, sw=2)
    parts.append(box)

    render("img/diff-mix.svg", W, H, *parts,
           title="Мікс бажання → колеса: v і ω розкладаються на два борти")


# ── Фігура 4: тримати курс на лінію — погляд наперед ─────────────────────────
# Як ровер їде за заданою лінією. Він не кермує «прямо на найближчу точку»
# (це смикає й зрізає кути), а цілиться в точку НАПЕРЕД на відстані огляду L.
# Різниця між напрямом носа й напрямом на цю точку задає кут керма.
def fig_lookahead():
    W, H = 940, 430
    parts = []

    # задана лінія (шлях) — плавна крива зліва направо
    parts.append('<path d="M 80 320 C 300 200, 560 200, 880 130" fill="none" '
                 'stroke="%s" stroke-width="3" stroke-dasharray="2,0"/>' % FIELD)
    parts.append(text(150, 300, "заданий шлях", size=12.5, color=FIELD, bold=True))

    # ровер трохи збоку від лінії
    cx, cy = 300, 280
    ang = -18  # ніс дивиться вправо-вгору
    def car(cx, cy, deg):
        a = math.radians(deg)
        def R(dx, dy):
            return (cx + dx * math.cos(a) - dy * math.sin(a),
                    cy + dx * math.sin(a) + dy * math.cos(a))
        p = [R(-30, -18), R(30, -18), R(30, 18), R(-30, 18)]
        pts = " ".join("%.1f,%.1f" % (x, y) for x, y in p)
        parts.append('<polygon points="%s" fill="#eef2f7" stroke="%s" stroke-width="2"/>' % (pts, INK))
        nx, ny = R(46, 0)
        bx, by = R(30, 0)
        parts.append(arrow(bx, by, nx, ny, color=INK, sw=2.4))  # напрям носа
        return R(0, 0)
    car(cx, cy, ang)

    # точка огляду наперед на шляху
    lx, ly = 640, 188
    parts.append(circle(lx, ly, 8, fill=POS, stroke=POS, sw=1.5))
    parts.append(text(lx, ly - 16, "точка огляду\n(наперед на L)", size=11.5, color=POS, bold=True, anchor="middle"))
    # коло огляду радіуса L
    Ld = math.hypot(lx - cx, ly - cy)
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.4" stroke-dasharray="5,5"/>' % (cx, cy, Ld, MUTED))
    parts.append(text(cx - 10, cy + 40, "L — відстань огляду", size=11, color=MUTED, anchor="middle"))

    # промінь на точку огляду
    parts.append(line(cx, cy, lx, ly, color=NEG, sw=2))
    # напрям носа (продовжити)
    na = math.radians(ang)
    parts.append(line(cx, cy, cx + 150 * math.cos(na), cy + 150 * math.sin(na),
                      color=INK, sw=1.4, dash="4,4"))
    # кут між ними — дуга
    parts.append('<path d="M %.1f %.1f A 46 46 0 0 0 %.1f %.1f" fill="none" '
                 'stroke="%s" stroke-width="2"/>'
                 % (cx + 46 * math.cos(na), cy + 46 * math.sin(na),
                    cx + 46 * (lx - cx) / Ld, cy + 46 * (ly - cy) / Ld, POS))
    parts.append(text(cx + 92, cy - 8, "кут α → кут керма", size=12, color=POS, bold=True, anchor="start"))

    box = fitbox(70, H - 74, W - 140, 50,
                 "Курс тримають, цілячись у точку НАПЕРЕД на шляху (на відстані огляду L), а не в найближчу.\n"
                 "Кут між носом і напрямом на цю точку задає поворот; більший L — плавніше, менший — точніше.",
                 size=13, fill="#eef6ff", stroke=NEG, sw=2)
    parts.append(box)

    render("img/lookahead.svg", W, H, *parts,
           title="Тримати курс на лінію: цілитися в точку наперед")


# ── Фігура 5 (вставка proj): знайти точку огляду — коло ∩ відрізок ────────────
# Робочий крок алгоритму: шлях — це ламана; коло огляду радіуса L рідко влучає
# у вершину, воно перетинає ВІДРІЗОК у двох точках. Беремо той корінь, що
# ПОПЕРЕДУ за рухом (більший параметр t уздовж відрізка). Показуємо коло, два
# перетини, обраний (зелений) і відкинутий (сірий) та напрям руху вздовж шляху.
def fig_pp_goalpoint():
    W, H = 940, 480
    parts = []

    # Прямий відрізок шляху проходить майже горизонтально; ровер трохи нижче за
    # нього, так що коло огляду перетинає ЦЕЙ відрізок у двох точках — обидві в
    # межах намальованого відрізка й полотна.
    ax, ay = 150.0, 205.0
    bx, by = 830.0, 165.0
    parts.append(line(ax, ay, bx, by, color=FIELD, sw=3))
    parts.append(circle(ax, ay, 4.5, fill=FIELD, stroke=FIELD, sw=1))
    parts.append(circle(bx, by, 4.5, fill=FIELD, stroke=FIELD, sw=1))
    parts.append(text(ax + 8, ay - 12, "заданий шлях (відрізок ламаної)",
                      size=12.5, color=FIELD, bold=True, anchor="start"))

    # ровер під шляхом, дивиться вправо (уздовж руху)
    cx, cy = 380.0, 320.0
    ang = -4
    a = math.radians(ang)

    def R(dx, dy):
        return (cx + dx * math.cos(a) - dy * math.sin(a),
                cy + dx * math.sin(a) + dy * math.cos(a))

    # два перетини кола з відрізком — підбираємо L так, щоб обидва були на відрізку
    dxs, dys = bx - ax, by - ay
    fx, fy = ax - cx, ay - cy
    Aq = dxs * dxs + dys * dys
    L = 175.0
    Bq = 2 * (fx * dxs + fy * dys)
    Cq = fx * fx + fy * fy - L * L
    disc = Bq * Bq - 4 * Aq * Cq
    sq = math.sqrt(disc)
    t1 = (-Bq - sq) / (2 * Aq)   # менший t — позаду за рухом
    t2 = (-Bq + sq) / (2 * Aq)   # більший t — попереду
    P_back = (ax + t1 * dxs, ay + t1 * dys)
    P_fwd = (ax + t2 * dxs, ay + t2 * dys)

    # коло огляду радіуса L
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.6" stroke-dasharray="6,5"/>' % (cx, cy, L, MUTED))
    # позначка радіуса L — до переднього кореня
    parts.append(line(cx, cy, P_fwd[0], P_fwd[1], color=MUTED, sw=1.3, dash="3,3"))
    parts.append(text((cx + P_fwd[0]) / 2 + 8, (cy + P_fwd[1]) / 2 + 4,
                      "L", size=15, color=MUTED, bold=True, italic=True, anchor="start"))
    # і до заднього кореня — тонкий радіус
    parts.append(line(cx, cy, P_back[0], P_back[1], color=MUTED, sw=1.0, dash="2,3"))

    # відкинутий корінь (позаду) — сірий
    parts.append(circle(P_back[0], P_back[1], 8, fill="#e5e7eb", stroke=MUTED, sw=2))
    parts.append(text(P_back[0], P_back[1] - 16, "корінь позаду\n(відкинути)",
                      size=11, color=MUTED, anchor="middle"))

    # обраний корінь (попереду) — зелений/червоний акцент
    parts.append(circle(P_fwd[0], P_fwd[1], 9, fill=POS, stroke=POS, sw=1.5))
    parts.append(text(P_fwd[0] + 14, P_fwd[1] - 8, "точка огляду\n(корінь ПОПЕРЕДУ за рухом)",
                      size=12, color=POS, bold=True, anchor="start"))

    # стрілка «напрям руху вздовж шляху» на відрізку
    axm, aym = ax + dxs * 0.10, ay + dys * 0.10
    bxm, bym = ax + dxs * 0.30, ay + dys * 0.30
    parts.append(arrow(axm, aym, bxm, bym, color=INK, sw=2.2))
    parts.append(text((axm + bxm) / 2, (aym + bym) / 2 - 12, "напрям руху вздовж шляху",
                      size=11.5, color=INK, anchor="middle"))

    # корпус ровера (вид згори)
    p = [R(-30, -18), R(30, -18), R(30, 18), R(-30, 18)]
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in p)
    parts.append('<polygon points="%s" fill="#eef2f7" stroke="%s" stroke-width="2"/>' % (pts, INK))
    nx, ny = R(48, 0)
    bxx, byy = R(30, 0)
    parts.append(arrow(bxx, byy, nx, ny, color=INK, sw=2.4))
    parts.append(text(cx, cy + 42, "ровер", size=12, color=INK, bold=True))

    box = fitbox(60, H - 66, W - 120, 46,
                 "Точку огляду шукають як перетин кола радіуса L із відрізком ламаної (квадратне рівняння),\n"
                 "а з двох коренів беруть той, що ПОПЕРЕДУ за напрямом руху — інакше ровер поїхав би назад по шляху.",
                 size=12.5, fill="#eef6ff", stroke=NEG, sw=2)
    parts.append(box)

    render("img/pp-goalpoint.svg", W, H, *parts,
           title="Знайти точку огляду: перетин кола огляду з відрізком шляху")


# ── Фігура 6 (вставка proj): кінець шляху — коло вже нікуди не влучає ──────────
# Головна практична пастка: коли ровер підходить до останньої точки ближче, ніж
# L, коло огляду вже НЕ перетинає жодного відрізка (уся решта шляху всередині
# кола). Тоді ціль-точку беруть як кінцеву вершину, а на підході — гальмують і
# зупиняються, інакше ровер «наздоганяв» би недосяжну точку по колу.
def fig_pp_endpath():
    W, H = 940, 430
    parts = []

    # короткий шлях, що закінчується вершиною-фінішем
    p0 = (130, 300)
    pf = (560, 250)   # фініш
    parts.append(line(p0[0], p0[1], pf[0], pf[1], color=FIELD, sw=3))
    parts.append(circle(p0[0], p0[1], 4.5, fill=FIELD, stroke=FIELD, sw=1))
    parts.append(circle(pf[0], pf[1], 10, fill=FIELD, stroke=INK, sw=2))
    parts.append(text(pf[0] + 16, pf[1] - 6, "кінець шляху\n(остання точка)",
                      size=12, color=FIELD, bold=True, anchor="start"))

    # ровер близько до фінішу — ближче, ніж L
    cx, cy = 430, 268
    ang = -7
    a = math.radians(ang)

    def R(dx, dy):
        return (cx + dx * math.cos(a) - dy * math.sin(a),
                cy + dx * math.sin(a) + dy * math.cos(a))

    L = 200.0
    parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.6" stroke-dasharray="6,5"/>' % (cx, cy, L, MUTED))
    parts.append(text(cx - L + 20, cy - 8, "коло огляду L", size=11.5, color=MUTED, anchor="start"))

    # відстань ровер→фініш менша за L: підкреслюємо, що фініш ВСЕРЕДИНІ кола
    d = math.hypot(pf[0] - cx, pf[1] - cy)
    parts.append(line(cx, cy, pf[0], pf[1], color=NEG, sw=2, dash="4,4"))
    parts.append(text((cx + pf[0]) / 2, (cy + pf[1]) / 2 + 22,
                      "до фінішу %.0f < L: коло вже нікуди не перетинає шлях" % d,
                      size=11.5, color=NEG, bold=True, anchor="middle"))

    # корпус ровера
    p = [R(-30, -18), R(30, -18), R(30, 18), R(-30, 18)]
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in p)
    parts.append('<polygon points="%s" fill="#eef2f7" stroke="%s" stroke-width="2"/>' % (pts, INK))
    nx, ny = R(48, 0)
    bxx, byy = R(30, 0)
    parts.append(arrow(bxx, byy, nx, ny, color=INK, sw=2.4))
    parts.append(text(cx - 4, cy + 44, "ровер", size=12, color=INK, bold=True))

    # рішення: цілитись у фініш і гальмувати
    box = fitbox(60, H - 92, W - 120, 62,
                 "Коли до останньої точки ближче за L, коло огляду вже не перетинає жодного відрізка —\n"
                 "уся решта шляху всередині кола. Тоді ціллю беруть саму кінцеву вершину, а на підході\n"
                 "гасять швидкість і зупиняються; без цього ровер кружляв би довкола недосяжної точки.",
                 size=12.5, fill="#fff4ec", stroke=POS, sw=2)
    parts.append(box)

    render("img/pp-endpath.svg", W, H, *parts,
           title="Кінець шляху: коло огляду більше нічого не перетинає")


# ── Фігура (вставка hist): Аккерманова геометрія згори ────────────────────────
# Серце винаходу Ланкенсперґера: задня вісь нерухома (обидва задні колеса прямо),
# керовані передні вивернуті на РІЗНІ кути так, щоб продовження осей УСІХ чотирьох
# коліс перетнулося в одній точці — миттєвому центрі повороту (ICR) на продовженні
# задньої осі. До внутрішнього переднього колеса радіус коротший → воно крутіше.
def fig_ackermann_geometry():
    W, H = 960, 560
    parts = []

    # Геометрія (у координатах картинки). Центр повороту ICR — ліворуч на лінії
    # задньої осі. Колеса: ліва пара (внутрішня, ближча до ICR) вивернута крутіше.
    track = 200.0          # колія (між лівими й правими колесами), px
    base = 210.0           # колісна база (між осями), px
    rax_y = 360.0          # задня вісь (y)
    rl_x = 300.0           # заднє ліве (внутрішнє)
    rr_x = rl_x + track    # заднє праве (зовнішнє)
    fax_y = rax_y - base   # передня вісь (y)
    fl_x = rl_x            # переднє ліве (внутрішнє)
    fr_x = rr_x            # переднє праве (зовнішнє)

    # ICR лежить на продовженні задньої осі, ліворуч (центр повороту — зліва).
    icr_x = rl_x - 250.0
    icr_y = rax_y

    def wheel(cx, cy, angle_deg, inner):
        # Колесо як видовжений прямокутник, повернутий на angle (0 = дивиться вгору).
        a = math.radians(angle_deg)
        ww, wl = 16.0, 46.0
        corners = [(-ww / 2, -wl / 2), (ww / 2, -wl / 2), (ww / 2, wl / 2), (-ww / 2, wl / 2)]
        pts = []
        for dx, dy in corners:
            pts.append((cx + dx * math.cos(a) - dy * math.sin(a),
                        cy + dx * math.sin(a) + dy * math.cos(a)))
        col = POS if inner else NEG
        return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="2.4" opacity="0.92"/>' % (
            " ".join("%.1f,%.1f" % p for p in pts),
            "#fdecea" if inner else "#eaf0fd", col)

    # Кути вивороту передніх коліс рахуємо ЧЕСНО з геометрії: лінія кочення колеса
    # (його поздовжня вісь) ⟂ радіусу ICR→колесо; кут беремо від вертикалі (0 = вгору).
    def steer_angle(cx, cy):
        rdx, rdy = cx - icr_x, cy - icr_y
        pdx, pdy = -rdy, rdx          # перпендикуляр до радіуса
        if pdy > 0:                    # колесо має дивитися вгору
            pdx, pdy = -pdx, -pdy
        return math.degrees(math.atan2(pdx, -pdy))

    ang_fl = steer_angle(fl_x, fax_y)   # внутрішнє переднє — крутіше
    ang_fr = steer_angle(fr_x, fax_y)   # зовнішнє переднє — м'якше

    # ── Пунктирні продовження осей усіх коліс до ICR ──
    for (wx, wy) in [(rl_x, rax_y), (rr_x, rax_y), (fl_x, fax_y), (fr_x, fax_y)]:
        parts.append(line(wx, wy, icr_x, icr_y, color=MUTED, sw=1.4, dash="6,6"))

    # ── Радіуси до передніх коліс (внутрішній коротший — POS, зовнішній довший — NEG) ──
    parts.append(line(icr_x, icr_y, fl_x, fax_y, color=POS, sw=2.6))
    parts.append(line(icr_x, icr_y, fr_x, fax_y, color=NEG, sw=2.6))

    # ── Корпус (кузов) як напівпрозорий прямокутник ──
    body_pad = 26
    parts.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="18" '
                 'fill="#f4f6f8" stroke="%s" stroke-width="1.6" opacity="0.5"/>'
                 % (rl_x - body_pad, fax_y - body_pad,
                    track + 2 * body_pad, base + 2 * body_pad, INK))

    # ── Задня вісь (короткий відрізок поперек) ──
    parts.append(line(rl_x, rax_y, rr_x, rax_y, color=INK, sw=2))
    parts.append(text((rl_x + rr_x) / 2, rax_y + 22, "задня вісь — колеса прямо",
                      size=12.5, color=INK, bold=True))

    # ── Колеса ──
    for (wx, wy, ang, inner) in [
        (rl_x, rax_y, 0.0, True), (rr_x, rax_y, 0.0, False),
        (fl_x, fax_y, ang_fl, True), (fr_x, fax_y, ang_fr, False),
    ]:
        parts.append(wheel(wx, wy, ang, inner))

    # ── Підписи кутів передніх коліс ──
    parts.append(text(fl_x - 6, fax_y - 42, "внутрішнє:", size=12.5, color=POS, bold=True))
    parts.append(text(fl_x - 6, fax_y - 26, "крутіше (%.0f°)" % abs(ang_fl), size=12.5, color=POS, bold=True))
    parts.append(text(fr_x + 6, fax_y - 42, "зовнішнє:", size=12.5, color=NEG, bold=True))
    parts.append(text(fr_x + 6, fax_y - 26, "м'якше (%.0f°)" % abs(ang_fr), size=12.5, color=NEG, bold=True))

    # ── ICR — миттєвий центр повороту ──
    parts.append(circle(icr_x, icr_y, 7, fill=INK, stroke=INK, sw=1))
    parts.append(text(icr_x, icr_y + 30, "миттєвий центр повороту", size=13.5, color=INK, bold=True))
    parts.append(text(icr_x, icr_y + 48, "(осі всіх коліс сходяться сюди)", size=12, color=MUTED))

    # ── Підписи радіусів ──
    parts.append(text((icr_x + fl_x) / 2 - 6, (icr_y + fax_y) / 2 - 8,
                      "радіус коротший", size=12, color=POS, bold=True))
    parts.append(text((icr_x + fr_x) / 2 + 30, (icr_y + fax_y) / 2 + 10,
                      "радіус довший", size=12, color=NEG, bold=True))

    # ── Нижня рамка з умовою ──
    box = fitbox(150, H - 64, W - 300, 46,
                 "Умова чистого кочення: продовження осей УСІХ коліс перетинаються в одній точці.\n"
                 "Задні колеса дивляться прямо → центр завжди лежить на продовженні задньої осі.",
                 size=13, fill="#f4f6f8", stroke=INK, sw=1.6)
    parts.append(box)

    render("img/ackermann-geometry.svg", W, H, *parts,
           title="Аккерманова геометрія: спільний центр для всіх коліс")


if __name__ == "__main__":
    fig_two_families()
    fig_nonholonomic()
    fig_diff_mix()
    fig_lookahead()
    fig_pp_goalpoint()
    fig_pp_endpath()
    fig_ackermann_geometry()
    print("OK: two-families, nonholonomic, diff-mix, lookahead, pp-goalpoint, pp-endpath, ackermann-geometry")
