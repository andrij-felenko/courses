# -*- coding: utf-8 -*-
"""Фігури до теми «Теорема Нетер».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def top_arc(cx, cy, r, a_left=150, a_right=30, color=INK, sw=2.2, arrow=True):
    """Дуга по верху кола від лівого кута a_left до правого a_right (мат. градуси),
    зі стрілкою на кінці — читається як «обертання»."""
    x0 = cx + r * math.cos(math.radians(a_left)); y0 = cy - r * math.sin(math.radians(a_left))
    x1 = cx + r * math.cos(math.radians(a_right)); y1 = cy - r * math.sin(math.radians(a_right))
    mk = ' marker-end="url(#arrow)"' if arrow else ''
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f"%s/>' % (x0, y0, r, r, x1, y1, color, sw, mk))


def dcircle(cx, cy, r, stroke=MUTED, sw=1.6, dash="4,4"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, stroke, sw, dash))


# ── Фігура 1: словник «симетрія → закон збереження» ──────────────────────────
def fig_dictionary():
    W, H = 780, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Симетрія → закон збереження", size=18, bold=True))

    xi = 65                       # центр іконки
    lx, lw = 110, 300             # ліва рамка (симетрія)
    rx, rw = 495, 240             # права рамка (збереження)
    f.append(text(lx + lw / 2, 58, "Неперервна симетрія", size=14, bold=True, color=MUTED))
    f.append(text(rx + rw / 2, 58, "Що зберігається", size=14, bold=True, color=MUTED))

    rows = [
        (120, "clock",  ["Зсув у часі", "той самий дослід сьогодні й завтра"], "Енергія"),
        (215, "shift",  ["Зсув у просторі", "той самий дослід тут і за кілометр"], "Імпульс"),
        (310, "rot",    ["Поворот", "немає виділеного напрямку"], "Момент імпульсу"),
    ]
    bh = 66
    for cy, icon, left, right in rows:
        # іконка
        if icon == "clock":
            f.append(circle(xi, cy, 21, fill=FILL, stroke=INK, sw=2))
            f.append(line(xi, cy, xi, cy - 13, color=INK, sw=2.2))       # хвилинна
            f.append(line(xi, cy, xi + 10, cy + 5, color=INK, sw=2.2))   # годинна
            f.append(circle(xi, cy, 2.2, fill=INK, stroke=INK, sw=1))
        elif icon == "shift":
            f.append(circle(xi - 15, cy, 6, fill=INK, stroke=INK, sw=1))
            f.append(arrow(xi - 6, cy, xi + 14, cy, color=LINE, sw=2))
            f.append(dcircle(xi + 20, cy, 6))
        elif icon == "rot":
            f.append(circle(xi, cy, 20, fill="none", stroke=MUTED, sw=1.4))
            f.append(top_arc(xi, cy, 20, 160, 20, color=INK, sw=2.4))
        # ліва рамка (симетрія)
        f.append(fitbox(lx, cy - bh / 2, lw, bh, left, size=14, pad=9,
                        fill=FILL, stroke=LINE, sw=1.6))
        # стрілка
        f.append(arrow(lx + lw + 6, cy, rx - 8, cy, color=FIELD, sw=2.6))
        # права рамка (збереження)
        f.append(fitbox(rx, cy - bh / 2, rw, bh, right, size=17, pad=10,
                        fill="#eef6ef", stroke=FIELD, sw=1.8, bold=True, color=INK))

    return render(os.path.join(IMG, "symmetry-conservation.svg"), W, H, *f)


# ── Фігура 2: трансляційна симетрія → збереження імпульсу ────────────────────
def fig_translation():
    W, H = 800, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Плаский потенціал уздовж x → сила = 0 → імпульс сталий",
                  size=16, bold=True))

    # роздільник панелей
    f.append(line(W / 2, 74, W / 2, 300, color="#d6dde6", sw=1.4, dash="5,6"))
    f.append(text(210, 60, "Симетрія: U рівний уздовж x", size=13, bold=True, color=FIELD))
    f.append(text(590, 60, "Симетрії нема: U похилий", size=13, bold=True, color=POS))

    # осі-підказки (обидві панелі)
    for ox in (52, 432):
        f.append(arrow(ox, 250, ox, 92, color=MUTED, sw=1.3))          # вісь U вгору
        f.append(text(ox - 8, 96, "U", size=12, color=MUTED, anchor="end"))
    for ox0, ox1 in ((60, 372), (440, 752)):
        f.append(arrow(ox0, 262, ox1, 262, color=MUTED, sw=1.3))       # вісь x праворуч
        f.append(text(ox1, 278, "x", size=12, color=MUTED, anchor="middle"))

    # ── ліва панель: рівна поверхня ──
    ys = 214
    f.append(line(70, ys, 360, ys, color=FIELD, sw=4))                 # рівний профіль U
    f.append(circle(200, ys - 11, 11, fill=FILL, stroke=INK, sw=1.8))  # кулька
    f.append(dcircle(262, ys - 11, 11, stroke=MUTED, sw=1.6))          # зсунута (привид)
    # вільний зсув в обидва боки
    f.append(arrow(210, 176, 150, 176, color=NEG, sw=1.8))
    f.append(arrow(252, 176, 312, 176, color=NEG, sw=1.8))
    f.append(text(231, 170, "зсув по x — те саме", size=11, color=NEG, anchor="middle"))
    f.append(fitbox(70, 300, 290, 40, "нахилу вздовж x нема → Fₓ = 0 → pₓ = const",
                    size=13, pad=7, fill="#eef6ef", stroke=FIELD, sw=1.4))

    # ── права панель: похила поверхня ──
    prof = [(448, 168), (540, 198), (632, 228), (752, 258)]
    for i in range(len(prof) - 1):
        f.append(line(prof[i][0], prof[i][1], prof[i + 1][0], prof[i + 1][1],
                      color=POS, sw=4))
    bx, by = 586, 212                                                  # кулька на схилі
    f.append(circle(bx, by - 12, 11, fill=FILL, stroke=INK, sw=1.8))
    f.append(arrow(bx + 4, by - 4, bx + 44, by + 18, color=POS, sw=2.4))  # сила вниз по схилу
    f.append(text(bx + 52, by + 20, "F", size=14, bold=True, color=POS, anchor="start"))
    f.append(fitbox(452, 300, 300, 40, "є нахил → Fₓ ≠ 0 → pₓ змінюється",
                    size=13, pad=7, fill="#fdecea", stroke=POS, sw=1.4))

    return render(os.path.join(IMG, "translation-momentum.svg"), W, H, *f)


# ── Фігура 3: обертальна симетрія → момент імпульсу ──────────────────────────
def fig_rotation():
    W, H = 560, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Обертальна симетрія центрального поля", size=16, bold=True))

    cx, cy = 280, 250
    # еквіпотенціали U(r): концентричні кола
    for r in (45, 90, 135, 180):
        f.append(circle(cx, cy, r, fill="none", stroke="#dfe4ea", sw=1.4))
    # центр (джерело поля)
    f.append(circle(cx, cy, 8, fill=POS, stroke=POS, sw=1))
    f.append(text(cx, cy + 26, "центр поля", size=11, color=MUTED))

    # частинка на орбіті радіуса r0
    r0 = 135
    ang = 42
    px = cx + r0 * math.cos(math.radians(ang))
    py = cy - r0 * math.sin(math.radians(ang))
    # радіус-вектор
    f.append(line(cx, cy, px, py, color=INK, sw=1.6, dash="5,4"))
    f.append(text((cx + px) / 2 + 10, (cy + py) / 2 - 6, "r", size=14, italic=True, color=INK))
    # сама частинка
    f.append(circle(px, py, 8, fill=NEG, stroke=NEG, sw=1))
    f.append(text(px + 14, py - 8, "маса m", size=11, color=NEG, anchor="start"))
    # вектор швидкості (по дотичній, проти годинникової)
    vx = -math.sin(math.radians(ang)); vy = -math.cos(math.radians(ang))
    f.append(arrow(px, py, px + 52 * vx, py + 52 * vy, color=INK, sw=2.2))
    f.append(text(px + 52 * vx - 6, py + 52 * vy - 8, "v", size=14, italic=True, color=INK, anchor="end"))

    # велика дуга-обертання: «поверни всю картину — нічого не зміниться»
    f.append(top_arc(cx, cy, 210, 158, 22, color=FIELD, sw=2.6))
    f.append(text(cx, 58, "поверни всю картину — нічого не зміниться", size=12, color=FIELD))

    # підсумок
    f.append(fitbox(70, 420, 420, 40,
                    "U залежить лише від r → поворот нічого не міняє → L = m·r²·ω = const",
                    size=13, pad=7, fill="#eef6ef", stroke=FIELD, sw=1.4))

    return render(os.path.join(IMG, "rotation-angular-momentum.svg"), W, H, *f)


# ── Фігура 4: дві варіації траєкторії → чому заряд є межовим членом ───────────
def poly(pts, color=INK, sw=2.4, dash=None):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, color, sw, da))


def fig_variations():
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Дві варіації однієї траєкторії: чому збережений заряд — це межовий член",
                  size=16, bold=True))

    N = 60
    panels = [
        (40,  "Варіація для рівнянь руху", FIELD),
        (470, "Симетрійна варіація",       POS),
    ]
    # роздільник панелей
    f.append(line(455, 74, 455, 410, color="#d6dde6", sw=1.4, dash="5,6"))

    for ox, sub, accent in panels:
        axx = ox + 42          # вертикальна вісь q
        ay_top, ay_bot = 96, 322
        x0, x1 = axx + 28, axx + 300    # межі t
        baseY = 250                     # рівень кінців істинної траєкторії

        f.append(text(ox + 205, 58, sub, size=14, bold=True, color=accent))
        # осі
        f.append(arrow(axx, ay_bot, axx, ay_top - 4, color=MUTED, sw=1.3))
        f.append(text(axx - 10, ay_top + 4, "q", size=13, italic=True, color=MUTED, anchor="end"))
        f.append(arrow(axx, ay_bot, x1 + 22, ay_bot, color=MUTED, sw=1.3))
        f.append(text(x1 + 24, ay_bot + 5, "t", size=13, italic=True, color=MUTED, anchor="start"))

        # істинна траєкторія: кінці на baseY, вигин угору
        def true_pt(k):
            t = k / N
            x = x0 + t * (x1 - x0)
            y = baseY - 62 * math.sin(math.pi * t)
            return x, y
        true = [true_pt(k) for k in range(N + 1)]
        f.append(poly(true, color=INK, sw=2.6))

        # пунктирні орієнтири t1, t2 до осі
        for xe in (x0, x1):
            f.append(line(xe, ay_bot, xe, baseY, color="#cfd6de", sw=1.2, dash="3,4"))
        f.append(text(x0, ay_bot + 18, "t₁", size=12, color=MUTED))
        f.append(text(x1, ay_bot + 18, "t₂", size=12, color=MUTED))
        # точки-кінці істинної
        f.append(circle(x0, baseY, 4.5, fill=INK, stroke=INK, sw=1))
        f.append(circle(x1, baseY, 4.5, fill=INK, stroke=INK, sw=1))
        f.append(text((x0 + x1) / 2, 305, "істинна q(t)", size=12, italic=True, color=INK))

        if accent == FIELD:
            # варіація з ЗАКРІПЛЕНИМИ кінцями: інший вигин, ті самі кінці
            varied = [(x, y - 26 * math.sin(math.pi * ((x - x0) / (x1 - x0))))
                      for (x, y) in true]
            f.append(poly(varied, color=accent, sw=2.2, dash="7,5"))
            f.append(text((x0 + x1) / 2, 140, "q + ε·δq", size=12, italic=True, color=accent))
            # закріплені кінці показані спільними кінцевими точками (δq = 0)
            f.append(fitbox(ox + 20, 360, 380, 48,
                            "кінці закріплені → межовий член зникає → лишається\nумова руху: d/dt(∂L/∂q̇) − ∂L/∂q = 0",
                            size=12, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.4))
        else:
            # симетрійна: рівномірний зсув угору — кінці НЕ закріплені
            dy = 40
            varied = [(x, y - dy) for (x, y) in true]
            f.append(poly(varied, color=accent, sw=2.2, dash="7,5"))
            f.append(text((x0 + x1) / 2, 122, "q + ε·δq", size=12, italic=True, color=accent))
            # подвійні стрілки-щілини на кінцях = ε·δq (підпис праворуч від стрілки, нижче кривої)
            for xe in (x0, x1):
                f.append(arrow(xe, baseY - 3, xe, baseY - dy + 3, color=accent, sw=1.6))
                f.append(arrow(xe, baseY - dy + 3, xe, baseY - 3, color=accent, sw=1.6))
                f.append(circle(xe, baseY - dy, 4.5, fill=accent, stroke=accent, sw=1))
                f.append(text(xe + 30, baseY - dy / 2 + 12, "ε·δq", size=11,
                              color=accent, anchor="middle"))
            f.append(fitbox(ox + 20, 360, 380, 48,
                            "кінці вільні → лишається межовий член\nQ = (∂L/∂q̇)·δq  — саме він і зберігається",
                            size=12, pad=8, fill="#fdecea", stroke=POS, sw=1.4))

    return render(os.path.join(IMG, "variations-boundary.svg"), W, H, *f)


# ── Фігура 5: хронологія життя Нетер і народження теореми (для hist-вставки) ──
def fig_timeline():
    W, H = 1000, 360
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Емілі Нетер: життя і народження теореми (1882–1935)",
                  size=17, bold=True))

    y0 = 192                                   # базова лінія часу
    x0, step = 80, 120
    f.append(line(x0 - 20, y0, x0 + 7 * step + 20, y0, color=MUTED, sw=2))

    events = [
        ("1882", "Народження\nЕрланген",             INK,   FILL),
        ("1907", "Докторат\nінваріанти",             INK,   FILL),
        ("1915", "Ґеттінґен\nзагадка ЗТВ",           NEG,   "#eaf0fd"),
        ("1918", "«Invariante\nVariationsprobleme»", FIELD, "#eef6ef"),
        ("1919", "Габілітація\nнарешті дозволено",   INK,   FILL),
        ("1921", "Теорія ідеалів\nнетерові кільця",  INK,   FILL),
        ("1933", "Звільнення\nнацистами",            POS,   "#fdecea"),
        ("1935", "Смерть\nБрін-Мор (США)",           POS,   "#fdecea"),
    ]
    bw, bh = 150, 66
    for i, (yr, txt, col, fillc) in enumerate(events):
        x = x0 + i * step
        above = (i % 2 == 0)
        by = 60 if above else 258
        cy = by + bh if above else by            # край рамки, до якого йде конектор
        f.append(line(x, y0, x, cy, color=MUTED, sw=1.4))
        f.append(fitbox(x - bw / 2, by, bw, bh, txt, size=13, pad=8,
                        fill=fillc, stroke=col, sw=1.6, color=INK))
        r = 8 if yr == "1918" else 6
        f.append(circle(x, y0, r, fill=col, stroke=col, sw=1))
        yy = y0 + 26 if above else y0 - 16       # рік — з боку, протилежного до рамки
        f.append(text(x, yy, yr, size=15, bold=True, color=col))

    return render(os.path.join(IMG, "noether-timeline.svg"), W, H, *f)


# ── Фігура 6: дві теореми Нетер — збереження проти тотожності ─────────────────
def fig_two_theorems():
    W, H = 940, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Дві теореми Нетер: збереження проти тотожності", size=17, bold=True))

    f.append(line(470, 48, 470, 350, color="#d6dde6", sw=1.4, dash="5,6"))

    # ── ліва колонка: перша теорема ──
    f.append(fitbox(60, 46, 380, 34, "Перша теорема", size=15, pad=6,
                    fill="#eef6ef", stroke=FIELD, sw=1.8, bold=True, color=INK))
    f.append(fitbox(60, 96, 380, 84,
                    "Глобальна (скінченна) симетрія\nодин параметр на всю систему\nнапр. зсув у часі — однаковий усюди",
                    size=13, pad=8, fill=FILL, stroke=LINE, sw=1.4))
    f.append(arrow(250, 188, 250, 226, color=FIELD, sw=2.6))
    f.append(fitbox(60, 232, 380, 84,
                    "Збережена ВЕЛИЧИНА\ndQ/dt = 0\nенергія · імпульс · момент",
                    size=13, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.8, color=INK))

    # ── права колонка: друга теорема ──
    f.append(fitbox(500, 46, 380, 34, "Друга теорема", size=15, pad=6,
                    fill="#eaf0fd", stroke=NEG, sw=1.8, bold=True, color=INK))
    f.append(fitbox(500, 96, 380, 84,
                    "Локальна (калібрувальна) симетрія\nдовільна функція в кожній точці\nнапр. свобода координат у ЗТВ",
                    size=13, pad=8, fill="#eaf0fd", stroke=NEG, sw=1.4))
    f.append(arrow(690, 188, 690, 226, color=POS, sw=2.6))
    f.append(fitbox(500, 232, 380, 84,
                    "ТОТОЖНІСТЬ між рівняннями\n0 = 0\nне нова величина, а залежність",
                    size=13, pad=8, fill="#fdecea", stroke=POS, sw=1.8, color=INK))

    f.append(fitbox(60, 352, 820, 66,
                    "Саме друга теорема пояснила загадку ЗТВ: там збереження енергії «вироджується»\n"
                    "в тотожність 0 = 0 — це підпис локальної симетрії простору-часу, а не зникнення енергії.",
                    size=13, pad=9, fill=FILL, stroke=MUTED, sw=1.4))

    return render(os.path.join(IMG, "noether-two-theorems.svg"), W, H, *f)


SUN = "#e8a33d"   # колір Сонця у фокусі (не плутати з червоною орбітою Ейлера)


# ── Фігури для proj-вставки: чисельне збереження на кеплерівській орбіті ──────
def _kepler_step(method, x, y, vx, vy, dt, mu=1.0):
    """Один крок інтегратора кеплерівської орбіти. Повертає (x,y,vx,vy).
    Чистий Python — без numpy (canon §5)."""
    r3 = (x*x + y*y) ** 1.5
    ax, ay = -mu*x/r3, -mu*y/r3
    if method == "euler":                    # явний (наївний) Ейлер
        xn, yn = x + dt*vx, y + dt*vy
        vx, vy = vx + dt*ax, vy + dt*ay
        x, y = xn, yn
    elif method == "symp":                   # симплектичний Ейлер
        vx, vy = vx + dt*ax, vy + dt*ay
        x, y = x + dt*vx, y + dt*vy
    else:                                    # velocity Verlet (leapfrog)
        vhx, vhy = vx + 0.5*dt*ax, vy + 0.5*dt*ay
        x, y = x + dt*vhx, y + dt*vhy
        r3n = (x*x + y*y) ** 1.5
        vx, vy = vhx - 0.5*dt*mu*x/r3n, vhy - 0.5*dt*mu*y/r3n
    return x, y, vx, vy


def _kepler_run(method, dt, nsteps, sample=1):
    """Проінтегрувати орбіту; повернути (точки [(x,y)], енергії, часи-в-обертах)."""
    x, y, vx, vy = 0.4, 0.0, 0.0, 2.0        # a=1, e=0.6 → E=-0.5, L=0.8, T=2π
    T = 2*math.pi
    def en(): return 0.5*(vx*vx+vy*vy) - 1.0/math.hypot(x, y)
    pts = [(x, y)]; Es = [en()]; ts = [0.0]
    for i in range(nsteps):
        x, y, vx, vy = _kepler_step(method, x, y, vx, vy, dt)
        if (i+1) % sample == 0:
            pts.append((x, y)); Es.append(en()); ts.append((i+1)*dt/T)
    return pts, Es, ts


def fig_kepler_orbits():
    """Явний Ейлер (спіраль назовні) проти симплектичного Верле (замкнена орбіта)."""
    W, H = 880, 512
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W/2, 26, "Та сама орбіта, два інтегратори: хто береже структуру",
                  size=16, bold=True))

    T = 2*math.pi
    dt, n = 0.01, int(5*T/0.01)
    eul, _, _ = _kepler_run("euler",  dt, n)
    ver, _, _ = _kepler_run("verlet", dt, n)

    # спільне квадратне вікно з центром у Сонці (0,0): масштаб чесний і однаковий,
    # Сонце по центру, опорне коло не вилазить за панель
    rmax = max(math.hypot(px, py) for (px, py) in eul)
    cx0, cy0 = 0.0, 0.0
    span = 2*(rmax + 0.35)

    def panel(px0, title, traj, col):
        pw = ph = 358
        py0 = 78
        s = pw/span
        ox, oy = px0 + pw/2, py0 + ph/2
        def mp(x, y): return ox + (x-cx0)*s, oy - (y-cy0)*s
        out = [rect(px0, py0, pw, ph, fill="#fbfcfd", stroke="#e3e8ee", sw=1.4)]
        out.append(text(px0+pw/2, py0-10, title, size=14, bold=True, color=col))
        sx0, sy0 = mp(0.0, 0.0)
        # опорне коло істинного афелію r=1.6 (масштаб однаковий по осях → коло)
        out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="#cbd3dc" '
                   'stroke-width="1.2" stroke-dasharray="5,4"/>' % (sx0, sy0, 1.6*s))
        # Сонце у фокусі
        out.append(circle(sx0, sy0, 6.5, fill=SUN, stroke=SUN, sw=1))
        # траєкторія
        out.append(poly([mp(x, y) for (x, y) in traj], color=col, sw=1.5))
        # старт (перигелій)
        sx, sy = mp(0.4, 0.0)
        out.append(circle(sx, sy, 4, fill=INK, stroke=INK, sw=1))
        return out

    f += panel(60,  "Явний Ейлер",                    eul, POS)
    f += panel(462, "Симплектичний Верле (leapfrog)", ver, FIELD)

    # маленька легенда під заголовком
    f.append(circle(360, 52, 5.5, fill=SUN, stroke=SUN, sw=1))
    f.append(text(372, 56, "Сонце (фокус)", size=11, color=MUTED, anchor="start"))
    f.append(line(505, 52, 533, 52, color="#cbd3dc", sw=1.4, dash="5,4"))
    f.append(text(539, 56, "істинний афелій r = 1.6", size=11, color=MUTED, anchor="start"))

    f.append(fitbox(60,  464, 358, 34, "енергія росте → орбіта розкручується назовні",
                    size=12, pad=6, fill="#fdecea", stroke=POS, sw=1.3))
    f.append(fitbox(462, 464, 358, 34, "енергія обмежена → орбіта замкнена, стабільна",
                    size=12, pad=6, fill="#eef6ef", stroke=FIELD, sw=1.3))
    return render(os.path.join(IMG, "kepler-orbits.svg"), W, H, *f)


def fig_energy_drift():
    """Енергія вздовж 20 обертів: дрейф Ейлера проти обмежених смуг симплектиків."""
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W/2, 26, "Повна енергія вздовж 20 обертів: дрейф проти обмеженості",
                  size=16, bold=True))

    T = 2*math.pi
    dt, n = 0.02, int(20*T/0.02)
    _, Ee, te = _kepler_run("euler", dt, n, sample=8)
    _, Es, ts = _kepler_run("symp",  dt, n, sample=8)
    _, Ev, tv = _kepler_run("verlet", dt, n, sample=8)

    PX0, PW = 96, 700
    xlo, xhi = 0.0, 20.0

    def xmap(t): return PX0 + (t-xlo)/(xhi-xlo)*PW

    def panel(py0, ph, ylo, yhi, title):
        def ymap(e): return py0 + ph - (e-ylo)/(yhi-ylo)*ph
        out = [rect(PX0, py0, PW, ph, fill="#fbfcfd", stroke="#e3e8ee", sw=1.3)]
        out.append(text(PX0-8, py0-6, title, size=12, bold=True, color=MUTED, anchor="start"))
        # вісь X — позначки обертів
        for xt in (0, 5, 10, 15, 20):
            sx = xmap(xt)
            out.append(line(sx, py0+ph, sx, py0+ph+4, color=MUTED, sw=1))
            out.append(text(sx, py0+ph+17, str(xt), size=11, color=MUTED))
        return out, ymap

    # ── верхня панель: повна шкала, Ейлер проходить крізь E=0 ──
    top, ym1 = panel(58, 168, -0.62, 0.30, "повна шкала")
    f += top
    # лінія втечі E=0 і опорна E=-0.5
    f.append(line(PX0, ym1(0.0), PX0+PW, ym1(0.0), color=POS, sw=1.2, dash="6,5"))
    f.append(text(PX0+PW-6, ym1(0.0)-6, "E = 0 — межа втечі (орбіта стає незамкненою)",
                  size=11, color=POS, anchor="end"))
    f.append(line(PX0, ym1(-0.5), PX0+PW, ym1(-0.5), color="#cbd3dc", sw=1.1, dash="4,4"))
    f.append(text(PX0-10, ym1(-0.5)+4, "−0.5", size=11, color=MUTED, anchor="end"))
    f.append(text(PX0-10, ym1(0.0)+4, "0", size=11, color=MUTED, anchor="end"))
    f.append(poly([(xmap(t), ym1(e)) for t, e in zip(te, Ee)], color=POS,   sw=2.0))
    f.append(poly([(xmap(t), ym1(e)) for t, e in zip(ts, Es)], color=NEG,   sw=1.6))
    f.append(poly([(xmap(t), ym1(e)) for t, e in zip(tv, Ev)], color=FIELD, sw=1.6))

    # ── нижня панель: збільшено, видно обмежені смуги симплектиків ──
    ylo2, yhi2 = -0.545, -0.455
    bot, ym2 = panel(288, 140, ylo2, yhi2, "збільшено біля −0.5 (Ейлер — поза шкалою, весь угорі)")
    f += bot
    f.append(line(PX0, ym2(-0.5), PX0+PW, ym2(-0.5), color="#cbd3dc", sw=1.1, dash="4,4"))
    f.append(text(PX0-10, ym2(-0.5)+4, "−0.5", size=11, color=MUTED, anchor="end"))
    # тільки симплектичні (Ейлер вилетів за верх)
    def clip(seq):
        return [(xmap(t), ym2(e)) for t, e in seq if ylo2 <= e <= yhi2]
    f.append(poly(clip(zip(ts, Es)), color=NEG,   sw=1.6))
    f.append(poly(clip(zip(tv, Ev)), color=FIELD, sw=1.8))
    f.append(text(PX0+PW-6, ym2(-0.5)-24, "симплектичний Ейлер — смуга ±0.03, БЕЗ дрейфу",
                  size=11, color=NEG, anchor="end"))
    f.append(text(PX0+PW-6, ym2(-0.5)+30, "Верле — смуга у ~40× вужча, теж без дрейфу",
                  size=11, color=FIELD, anchor="end"))

    # спільна вісь-підпис
    f.append(text(PX0+PW/2, 452, "час, обертів", size=12, color=MUTED))
    # легенда кольорів (угорі праворуч верхньої панелі)
    lx, ly = PX0+16, 74
    for i, (c, lab) in enumerate([(POS, "явний Ейлер"), (NEG, "симплектичний Ейлер"),
                                  (FIELD, "Верле (leapfrog)")]):
        yy = ly + i*16
        f.append(line(lx, yy, lx+22, yy, color=c, sw=2.4))
        f.append(text(lx+28, yy+4, lab, size=11, color=INK, anchor="start"))

    return render(os.path.join(IMG, "energy-drift.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_dictionary(), fig_translation(), fig_rotation(), fig_variations(),
          fig_timeline(), fig_two_theorems(),
          fig_kepler_orbits(), fig_energy_drift()]
    print("written:")
    for p in ps:
        print("  ", p)
