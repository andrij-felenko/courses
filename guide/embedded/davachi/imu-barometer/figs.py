# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── specific-force: три стани акселерометра ───────────────────────────────────
# Ідея: акселерометр читає питому силу (реакцію опори), а не рух. У спокої — +1g
# угору, у вільному падінні — нуль, нахилений у спокої — проєкції g на свої осі.

def _sensor(cx, cy, s=34):
    """Кубик-давач: квадрат із ніжками й пробною масою всередині."""
    h = s / 2.0
    out = rect(cx - h, cy - h, s, s, fill=BG, stroke=INK, sw=1.6, rx=7)
    out += line(cx, cy - h, cx, cy - h * 0.35, color=MUTED, sw=1.2)
    out += line(cx, cy + h * 0.35, cx, cy + h, color=MUTED, sw=1.2)
    out += circle(cx, cy, s * 0.16, fill="#f1f2f4", stroke=INK, sw=1.3)
    return out


def fig_specific_force():
    W, H = 760, 340
    cols = [150, 380, 610]
    cy = 175
    p = []
    p.append(text(W / 2, 48, "У спокої бачить g (звідси нахил), у падінні — нуль",
                  size=13, color=MUTED))

    # 1) у спокої на столі: опора штовхає вгору → +1g угору
    cx = cols[0]
    p.append(text(cx, 92, "У спокої на столі", size=13, color=INK, bold=True))
    p.append(_sensor(cx, cy))
    p.append(arrow(cx, cy - 6, cx, cy - 70, color=POS, sw=2.6))
    p.append(line(cx - 52, cy + 38, cx + 52, cy + 38, color=INK, sw=2.4))   # стіл
    p.append(text(cx, cy + 70, "читає +1g угору", size=12, color=POS, bold=True))
    p.append(text(cx, cy + 90, "опора штовхає вгору", size=11, color=MUTED))

    # 2) у вільному падінні: нічого не тисне → нуль
    cx = cols[1]
    p.append(text(cx, 92, "У вільному падінні", size=13, color=INK, bold=True))
    p.append(_sensor(cx, cy))
    p.append(circle(cx, cy - 56, 5, fill=POS, stroke="none", sw=1))
    p.append(arrow(cx + 70, cy - 30, cx + 70, cy + 30, color=MUTED, sw=2.0))
    p.append(text(cx + 84, cy, "падає", size=11, color=MUTED, anchor="start"))
    p.append(text(cx, cy + 70, "читає нуль", size=12, color=POS, bold=True))
    p.append(text(cx, cy + 90, "нічого не тисне", size=11, color=MUTED))

    # 3) нахилений у спокої: проєкції g на осі
    cx = cols[2]
    p.append(text(cx, 92, "Нахилений (спокій)", size=13, color=INK, bold=True))
    ang = 24 * math.pi / 180.0
    s = 34; h = s / 2.0
    # повернений квадрат
    def rot(dx, dy):
        return (cx + dx * math.cos(ang) - dy * math.sin(ang),
                cy + dx * math.sin(ang) + dy * math.cos(ang))
    pts = [rot(-h, -h), rot(h, -h), rot(h, h), rot(-h, h)]
    poly = '<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (
        " ".join("%.1f,%.1f" % pt for pt in pts), BG, INK)
    p.append(poly)
    p.append(circle(cx, cy, s * 0.16, fill="#f1f2f4", stroke=INK, sw=1.3))
    p.append(line(cx, cy - 56, cx, cy + 56, color=FIELD, sw=1.4, dash="3,3"))  # вертикаль g
    p.append(text(cx + 10, cy + 54, "g", size=12, color=FIELD, anchor="start", bold=True))
    gx, gy = rot(28, 28)                                                       # проєкція на осі
    p.append(arrow(cx, cy, gx, gy, color=POS, sw=2.4))
    p.append(text(cx, cy + 70, "читає проєкції g", size=12, color=POS, bold=True))
    p.append(text(cx, cy + 90, "звідси крен і тангаж", size=11, color=MUTED))

    render(os.path.join(OUT, "specific-force.svg"), W, H, *p,
           title="Акселерометр міряє питому силу, а не рух")


# ── yaw-blind-spot: гравітація не бачить курсу ───────────────────────────────
# Ідея: нахил (крен/тангаж) змінює проєкцію g — акселерометр це бачить; поворот
# навколо вертикалі (yaw) лишає g незмінним → курс дає магнітометр.

def fig_yaw_blind_spot():
    W, H = 780, 360
    p = []
    p.append(text(W / 2, 48, "Нахил міняє проєкцію g; поворот навколо вертикалі — ні",
                  size=13, color=MUTED))
    bw, by, bh = 224, 74, 248
    xs = [28, 278, 528]

    # панель 1: крен/тангаж — видно
    x = xs[0]
    p.append(rect(x, by, bw, bh, fill=BG, stroke=INK, sw=1.3))
    p.append(text(x + bw / 2, by + 26, "Крен / тангаж — видно", size=12.5, color=FIELD, bold=True))
    cx, cy = x + bw / 2, by + 150
    ang = 20 * math.pi / 180
    def rot1(dx, dy):
        return (cx + dx * math.cos(ang) - dy * math.sin(ang),
                cy + dx * math.sin(ang) + dy * math.cos(ang))
    pts = [rot1(-70, -12), rot1(70, -12), rot1(70, 12), rot1(-70, 12)]
    p.append('<polygon points="%s" fill="#eef2ff" stroke="%s" stroke-width="1.6"/>' % (
        " ".join("%.1f,%.1f" % q for q in pts), NEG))
    p.append(line(cx, cy - 64, cx, cy + 70, color=FIELD, sw=1.6, dash="4,3"))
    p.append(arrow(cx, cy, cx, cy + 70, color=FIELD, sw=1.6))
    p.append(text(cx + 12, cy + 70, "g", size=12, color=FIELD, anchor="start", bold=True))
    p.append(text(x + bw / 2, by + bh - 14, "проєкція g змінилась", size=10.5, color=INK))

    # панель 2: yaw — не видно
    x = xs[1]
    p.append(rect(x, by, bw, bh, fill=BG, stroke=INK, sw=1.3))
    p.append(text(x + bw / 2, by + 26, "Курс (yaw) — не видно", size=12.5, color=POS, bold=True))
    cx, cy = x + bw / 2, by + 150
    ang = 35 * math.pi / 180
    def rot2(dx, dy):
        return (cx + dx * math.cos(ang) - dy * math.sin(ang),
                cy + dx * math.sin(ang) + dy * math.cos(ang))
    pts = [rot2(-60, -22), rot2(48, -22), rot2(48, 22), rot2(-60, 22)]
    p.append('<polygon points="%s" fill="#eef2ff" stroke="%s" stroke-width="1.6"/>' % (
        " ".join("%.1f,%.1f" % q for q in pts), NEG))
    nose = [rot2(48, -10), rot2(66, 0), rot2(48, 10)]
    p.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.4"/>' % (
        " ".join("%.1f,%.1f" % q for q in nose), NEG, NEG))
    p.append(circle(cx, cy, 13, fill=BG, stroke=FIELD, sw=1.8))               # g ⊙ у площину
    p.append(circle(cx, cy, 3, fill=FIELD, stroke="none", sw=1))
    p.append(text(cx, cy + 50, "g ⊙ — не змінюється", size=10.5, color=FIELD))
    p.append(text(x + bw / 2, by + bh - 14, "для g нічого не сталось", size=10.5, color=INK))

    # панель 3: курс дає магнітометр
    x = xs[2]
    p.append(rect(x, by, bw, bh, fill=BG, stroke=INK, sw=1.3))
    p.append(text(x + bw / 2, by + 26, "Курс дає магнітометр", size=12.5, color=POS, bold=True))
    cx, cy = x + bw / 2, by + 150
    p.append(circle(cx, cy, 58, fill="#fffdf5", stroke=POS, sw=1.6))
    p.append(text(cx, cy - 40, "Пн", size=11, color=POS, bold=True))
    p.append(arrow(cx, cy + 36, cx, cy - 36, color=POS, sw=2.4))
    p.append(text(x + bw / 2, by + bh - 14, "по горизонтальному полю Землі", size=10.5, color=INK))

    render(os.path.join(OUT, "yaw-blind-spot.svg"), W, H, *p,
           title="Гравітація фіксує два кути з трьох — курс сліпий")


# ── pressure-altitude: тиск падає з висотою ──────────────────────────────────
# Ідея: барометр міряє тиск, а висоту з нього рахують; біля землі ~1 гПа на 8 м,
# а MEMS-сенсор розрізняє лічені паскалі → бачить кроки в сантиметри.

def fig_pressure_altitude():
    W, H = 760, 360
    ox, oy = 90, 300          # початок осей
    ah, aw = 220, 380         # висота осі / ширина осі
    p = []
    p.append(text(W / 2, 48, "≈ 1 гПа на 8 м біля землі; MEMS ловить кроки в сантиметри",
                  size=13, color=MUTED))
    # осі
    p.append(arrow(ox, oy, ox, oy - ah - 10, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw + 10, oy, color=INK, sw=1.6))
    p.append(text(ox - 8, oy - ah - 2, "висота", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox + aw + 6, oy + 18, "тиск", size=11, color=INK, anchor="end", bold=True))

    # крива тиск(висота): тиск спадає, що вище (експонента), малюємо точками
    pts = []
    for i in range(61):
        t = i / 60.0
        hh = t * ah                                   # висота вгору
        # тиск падає з висотою: беремо праву координату як спадну від висоти
        pr = (1 - math.exp(-1.7 * t))                 # 0..~0.8
        x = ox + 18 + pr * (aw - 30)
        y = oy - hh
        pts.append((x, y))
    poly = '<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in pts), NEG)
    p.append(poly)
    p.append(circle(ox + 18, oy, 5, fill=FIELD, stroke=INK, sw=1.2))
    p.append(text(ox + 30, oy - 6, "рівень моря ≈ 1013 гПа", size=11, color=FIELD, anchor="start", bold=True))
    # крок 1 гПа / 8 м
    p.append(line(ox, oy - 44, ox + 70, oy - 44, color=POS, sw=1.4))
    p.append(text(ox + 78, oy - 40, "≈ 1 гПа / 8 м  (≈ 12 Па/м)", size=11, color=POS, anchor="start", bold=True))

    # бічна рамка — здатність MEMS
    bx, bw2 = ox + aw - 150, 200
    box, w, h = textbox(W - 122, 150,
                        ["MEMS-барометр:", "роздільність — лічені Па", "→ кроки висоти ~10 см"],
                        size=11, pad=12, fill="#f4f6f8")
    p.append(box)

    render(os.path.join(OUT, "pressure-altitude.svg"), W, H, *p,
           title="Барометр міряє тиск, а висоту з нього рахують")


# ── baro-drift: погода зсуває барометричну висоту ────────────────────────────
# Ідея: апарат стоїть (справжня висота стала), але тиск повзе з фронтом — і
# барометрична висота дрейфує на десятки метрів. Прив'язку дає GNSS/далекомір.

def fig_baro_drift():
    W, H = 760, 340
    ox, oy = 80, 270
    aw, ah = 600, 190
    p = []
    p.append(text(W / 2, 48, "Апарат стоїть, а тиск повзе з фронтом — висота «дихає»",
                  size=13, color=MUTED))
    p.append(arrow(ox, oy, ox + aw + 10, oy, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox, oy - ah - 10, color=INK, sw=1.4))
    p.append(text(ox + aw + 6, oy + 18, "час (години)", size=11, color=INK, anchor="end"))
    p.append(text(ox - 8, oy - ah - 2, "висота", size=11, color=INK, anchor="end", bold=True))

    mid = oy - ah * 0.5
    # справжня висота — стала
    p.append(line(ox, mid, ox + aw, mid, color=FIELD, sw=2.2, dash="7,4"))
    p.append(text(ox + 20, mid - 8, "справжня висота (апарат рівно)", size=11, color=FIELD, anchor="start", bold=True))
    # барометрична — повзе (повільна хвиля)
    pts = []
    for i in range(81):
        t = i / 80.0
        y = mid - ah * 0.30 * math.sin(2 * math.pi * (t * 1.15 - 0.05))
        x = ox + t * aw
        pts.append((x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in pts), POS))
    p.append(text(ox + aw * 0.62, mid - ah * 0.42, "висота за барометром", size=11, color=POS, anchor="start", bold=True))
    # позначка «фронт зсунув тиск»
    fx = ox + aw * 0.46
    p.append(line(fx, mid, fx, mid - ah * 0.30, color=MUTED, sw=1.2, dash="3,3"))
    p.append(text(fx + 8, mid - ah * 0.18, "фронт зсунув тиск", size=10, color=MUTED, anchor="start"))
    p.append(text(fx + 8, mid - ah * 0.18 + 14, "→ десятки метрів хибно", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "baro-drift.svg"), W, H, *p,
           title="Барометр «дихає» разом із погодою")


# ── vibration: жорсткий монтаж тоне в шумі, демпфер+фільтр рятують ────────────
# Ідея: тряска моторів забиває акселерометр; високі частоти ще й аліасять у смугу
# корисного. Рятують м'який монтаж (фізично) + цифровий фільтр (рештки).

def _noisy(ox, oy, w, amp, n, seed, color, sw=1.8):
    """Псевдовипадкова тремтлива лінія навколо oy."""
    s = seed
    pts = []
    for i in range(n):
        s = (1103515245 * s + 12345) & 0x7fffffff
        r = (s / 0x7fffffff) * 2 - 1
        x = ox + w * i / (n - 1)
        pts.append((x, oy + r * amp))
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in pts), color, sw)


def _clean(ox, oy, w, amp, n, color, sw=1.8):
    """Гладка хвиля (відфільтрований сигнал)."""
    pts = []
    for i in range(n):
        t = i / (n - 1)
        x = ox + w * t
        pts.append((x, oy + amp * math.sin(2 * math.pi * 1.5 * t)))
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in pts), color, sw)


def fig_vibration():
    W, H = 760, 360
    p = []
    p.append(text(W / 2, 48, "Тряска моторів забиває акселерометр; рятують монтаж і фільтр",
                  size=13, color=MUTED))
    bw, by, bh = 330, 72, 232
    xL, xR = 30, 400

    # ліва панель — жорстко прикручений
    p.append(rect(xL, by, bw, bh, fill=BG, stroke=POS, sw=1.6))
    p.append(text(xL + bw / 2, by + 26, "Жорстко прикручений — шум", size=12.5, color=POS, bold=True))
    p.append(circle(xL + 56, by + 96, 20, fill="#f1f2f4", stroke=INK, sw=1.5))
    p.append(text(xL + 56, by + 100, "мотор", size=9, color=INK))
    p.append(rect(xL + bw - 110, by + 78, 80, 34, fill="#eef2ff", stroke=NEG, sw=1.5))
    p.append(text(xL + bw - 70, by + 100, "IMU", size=11, color=NEG, bold=True))
    p.append(_noisy(xL + 24, by + 168, bw - 48, 26, 70, 7, POS, 1.8))
    p.append(text(xL + bw / 2, by + bh - 26, "тряска забиває сигнал; високі частоти", size=10, color=INK))
    p.append(text(xL + bw / 2, by + bh - 12, "ще й аліасять у смугу корисного", size=10, color=INK))

    # права панель — демпфери + ФНЧ
    p.append(rect(xR, by, bw, bh, fill=BG, stroke=FIELD, sw=1.6))
    p.append(text(xR + bw / 2, by + 26, "На демпферах + фільтр — чисто", size=12.5, color=FIELD, bold=True))
    p.append(circle(xR + 56, by + 96, 20, fill="#f1f2f4", stroke=INK, sw=1.5))
    p.append(text(xR + 56, by + 100, "мотор", size=9, color=INK))
    p.append(rect(xR + bw - 110, by + 78, 80, 34, fill="#eef2ff", stroke=NEG, sw=1.5))
    p.append(text(xR + bw - 70, by + 100, "IMU", size=11, color=NEG, bold=True))
    p.append(_clean(xR + 24, by + 168, bw - 48, 16, 90, FIELD, 2.0))
    p.append(text(xR + bw / 2, by + bh - 26, "м'який монтаж гасить тряску,", size=10, color=INK))
    p.append(text(xR + bw / 2, by + bh - 12, "фільтр прибирає рештки", size=10, color=INK))

    render(os.path.join(OUT, "vibration.svg"), W, H, *p,
           title="IMU ніколи не прикручують намертво")


# ══════════════════════════════════════════════════════════════════════════════
# ДЕТАЛЬНА ЧАСТИНА (imu-barometer-d.md) — глибші фігури з виведеннями
# ══════════════════════════════════════════════════════════════════════════════

# ── specific-force-vector: f = a − g як векторна різниця ──────────────────────
# Ідея: акселерометр видає f = a − g. Показуємо чотири стани як векторну
# конструкцію, з наголосом на розгін (де до −g додається реакція й вектор
# нахиляється — звідси удаваний нахил).

def _accel_box(cx, cy, s=30, ang=0.0):
    h = s / 2.0
    def rot(dx, dy):
        return (cx + dx * math.cos(ang) - dy * math.sin(ang),
                cy + dx * math.sin(ang) + dy * math.cos(ang))
    pts = [rot(-h, -h), rot(h, -h), rot(h, h), rot(-h, h)]
    poly = '<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.6"/>' % (
        " ".join("%.1f,%.1f" % q for q in pts), BG, INK)
    poly += circle(cx, cy, s * 0.15, fill="#f1f2f4", stroke=INK, sw=1.2)
    return poly


def fig_specific_force_vector():
    W, H = 780, 320
    p = []
    p.append(text(W / 2, 50, "f = a − g  — акселерометр звітує про відхилення руху від вільного падіння",
                  size=13, color=MUTED))
    cols = [120, 330, 545, 700]
    cy = 180
    L = 56   # довжина 1g

    # 1) спокій: a=0 → f = −g (угору, 1g)
    cx = cols[0]
    p.append(text(cx, 92, "Спокій", size=12.5, color=INK, bold=True))
    p.append(text(cx, 108, "a = 0", size=11, color=MUTED))
    p.append(_accel_box(cx, cy))
    p.append(arrow(cx, cy, cx, cy - L, color=POS, sw=2.6))
    p.append(text(cx, cy - L - 8, "f = −g", size=11.5, color=POS, bold=True))
    p.append(text(cx, cy + 46, "+1g угору", size=10.5, color=MUTED))

    # 2) вільне падіння: a=g → f=0
    cx = cols[1]
    p.append(text(cx, 92, "Вільне падіння", size=12.5, color=INK, bold=True))
    p.append(text(cx, 108, "a = g", size=11, color=MUTED))
    p.append(_accel_box(cx, cy))
    p.append(circle(cx, cy, 6, fill=BG, stroke=POS, sw=2.2))
    p.append(text(cx, cy - L - 8, "f = 0", size=11.5, color=POS, bold=True))
    p.append(text(cx, cy + 46, "невагомість", size=10.5, color=MUTED))

    # 3) бічний розгін: f = a − g нахилений
    cx = cols[2]
    p.append(text(cx, 92, "Бічний розгін", size=12.5, color=INK, bold=True))
    p.append(text(cx, 108, "a ≠ 0 (убік)", size=11, color=MUTED))
    p.append(_accel_box(cx, cy))
    # −g угору (пунктир), −a (реакція, ліворуч), сума f нахилена
    p.append(line(cx, cy, cx, cy - L, color=MUTED, sw=1.4, dash="4,3"))
    p.append(text(cx + 4, cy - L + 6, "−g", size=10, color=MUTED, anchor="start"))
    ax = 34
    p.append(line(cx, cy - L, cx - ax, cy - L, color=MUTED, sw=1.4, dash="4,3"))
    p.append(text(cx - ax, cy - L - 6, "−a", size=10, color=MUTED, anchor="middle"))
    p.append(arrow(cx, cy, cx - ax, cy - L, color=POS, sw=2.6))
    p.append(text(cx - ax - 6, cy - L - 6, "f", size=12, color=POS, bold=True, anchor="end"))
    p.append(text(cx, cy + 46, "вектор нахилився →", size=10.5, color=MUTED))
    p.append(text(cx, cy + 60, "удаваний нахил", size=10.5, color=POS, bold=True))

    render(os.path.join(OUT, "specific-force-vector.svg"), W, H, *p,
           title="Рівняння акселерометра: f = a − g")


# ── complementary-crossover: частотний поділ гіро/акселерометра ───────────────
# Ідея: гіроскопова гілка — ФВЧ (веде на високих частотах), акселерометрова —
# ФНЧ (веде на низьких). На частоті розділу 1/(2πτ) довіра переходить; сума = 1.

def fig_complementary_crossover():
    W, H = 780, 360
    ox, oy = 90, 290
    aw, ah = 610, 210
    p = []
    p.append(text(W / 2, 50, "Гіроскоп веде на високих частотах, акселерометр — на низьких; сума = 1",
                  size=13, color=MUTED))
    # осі
    p.append(arrow(ox, oy, ox + aw + 10, oy, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=INK, sw=1.4))
    p.append(text(ox + aw + 4, oy + 18, "частота (log)", size=11, color=INK, anchor="end"))
    p.append(text(ox - 8, oy - ah - 2, "вага", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox - 10, oy - ah + 6, "1", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy - 2, "0", size=10, color=MUTED, anchor="end"))

    top = oy - ah + 8
    xc = ox + aw * 0.5          # частота розділу
    # акселерометр — ФНЧ: 1 на низьких, спадає до 0 після xc (сигмоїда)
    accf = []
    for i in range(121):
        t = i / 120.0
        x = ox + t * aw
        val = 1.0 / (1.0 + math.exp(12 * (t - 0.5)))   # спад біля центру
        y = oy - (oy - top) * val
        accf.append((x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in accf), NEG))
    # гіроскоп — ФВЧ: 0 на низьких, росте до 1 після xc
    gyf = []
    for i in range(121):
        t = i / 120.0
        x = ox + t * aw
        val = 1.0 / (1.0 + math.exp(-12 * (t - 0.5)))
        y = oy - (oy - top) * val
        gyf.append((x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in gyf), POS))
    # сума = 1 (пласка)
    p.append(line(ox, top, ox + aw, top, color=FIELD, sw=2.0, dash="6,4"))
    p.append(text(ox + aw - 6, top - 8, "сума = 1", size=11, color=FIELD, anchor="end", bold=True))

    # частота розділу
    p.append(line(xc, oy, xc, top - 4, color=MUTED, sw=1.2, dash="3,3"))
    p.append(text(xc, oy + 18, "f = 1/(2πτ)", size=11, color=MUTED, bold=True))

    # підписи гілок
    p.append(text(ox + aw * 0.16, oy - (oy - top) * 0.86, "акселерометр (ФНЧ)", size=11.5, color=NEG, bold=True, anchor="start"))
    p.append(text(ox + aw * 0.60, oy - (oy - top) * 0.86, "гіроскоп (ФВЧ)", size=11.5, color=POS, bold=True, anchor="start"))
    p.append(text(ox + aw * 0.12, oy - 18, "абсолютний,", size=10, color=MUTED))
    p.append(text(ox + aw * 0.12, oy - 6, "недрейфний", size=10, color=MUTED))
    p.append(text(ox + aw * 0.86, oy - 18, "швидкий,", size=10, color=MUTED))
    p.append(text(ox + aw * 0.86, oy - 6, "без тряски", size=10, color=MUTED))

    render(os.path.join(OUT, "complementary-crossover.svg"), W, H, *p,
           title="Комплементарний фільтр як частотний поділ")


# ── baro-derivation: три рівні опису тиск↔висота ─────────────────────────────
# Ідея: гідростатичний стовп → експонента (T const) → степенева ISA (T падає);
# лінійне «8.3 м/гПа» — дотична біля землі, що занижує висоту вгорі.

def fig_baro_derivation():
    W, H = 780, 380
    p = []
    p.append(text(W / 2, 50, "Гідростатика → експонента → степенева ISA; лінійне — лише дотична біля землі",
                  size=13, color=MUTED))

    # ЛІВОРУЧ: стовп повітря з рівнянням шару
    cx, ctop, cbot, cw = 70, 90, 330, 70
    p.append(rect(cx, ctop, cw, cbot - ctop, fill="#f4f8ff", stroke=NEG, sw=1.4))
    # шари
    for yy in range(ctop + 30, cbot, 34):
        p.append(line(cx, yy, cx + cw, yy, color="#c9d6f5", sw=1.0))
    p.append(arrow(cx + cw + 14, ctop + 20, cx + cw + 14, ctop + 4, color=INK, sw=1.4))
    p.append(text(cx + cw + 20, ctop + 16, "h", size=11, color=INK, anchor="start", bold=True))
    # виділений шар
    ys = ctop + 150
    p.append(rect(cx, ys, cw, 26, fill="#dbe6ff", stroke=NEG, sw=1.4))
    p.append(arrow(cx + cw / 2, ys - 2, cx + cw / 2, ys - 20, color=POS, sw=1.8))
    p.append(text(cx + cw / 2, ys - 24, "p", size=10, color=POS, anchor="middle"))
    p.append(arrow(cx + cw / 2, ys + 28, cx + cw / 2, ys + 46, color=POS, sw=1.8))
    p.append(text(cx + cw / 2, ys + 60, "p+dp", size=10, color=POS, anchor="middle"))
    box, w, h = textbox(cx + cw / 2, cbot + 34, "dp = −ρ·g·dh",
                        size=12, pad=8, fill="#fffdf5", stroke=POS, color=INK, bold=True)
    p.append(box)

    # ПРАВОРУЧ: криві тиск(висота)
    ox, oy = 300, 340
    aw, ah = 250, 250
    p.append(arrow(ox, oy, ox, oy - ah - 10, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox + aw + 10, oy, color=INK, sw=1.4))
    p.append(text(ox - 8, oy - ah - 2, "висота", size=11, color=INK, anchor="end", bold=True))
    p.append(text(ox + aw + 6, oy + 18, "тиск p/p₀", size=11, color=INK, anchor="end"))
    p.append(text(ox - 8, oy + 2, "0", size=10, color=MUTED, anchor="end"))

    # степенева ISA (майже експонента) — тиск спадає з висотою
    pts_isa = []
    for i in range(81):
        t = i / 80.0                 # частка висоти
        hh = t * ah
        pr = (1 - t) ** 5.255        # p/p0 (нормовано за верхню висоту)
        pr = max(pr, 0.02)
        x = ox + 8 + pr * (aw - 16)
        y = oy - hh
        pts_isa.append((x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in pts_isa), NEG))
    # лінійна дотична біля землі (початковий нахил кривої) — короткий відрізок,
    # довжину обмежуємо, щоб не вилітати за полотно (крива вгорі майже вертикальна)
    x0, y0 = pts_isa[0]
    x1, y1 = pts_isa[4]
    dx, dy = (x1 - x0), (y1 - y0)
    seg = (dx * dx + dy * dy) ** 0.5
    Lseg = ah * 0.82
    ux, uy = (dx / seg, dy / seg) if seg else (0.0, -1.0)
    p.append(line(x0, y0, x0 + ux * Lseg, y0 + uy * Lseg, color=POS, sw=1.8, dash="6,4"))

    p.append(circle(ox + 8 + (aw - 16), oy, 4, fill=FIELD, stroke=INK, sw=1.2))
    p.append(text(ox + aw - 6, oy - 8, "рівень моря", size=10, color=FIELD, anchor="end", bold=True))
    p.append(text(ox + 40, oy - ah + 20, "ISA:", size=11, color=NEG, anchor="start", bold=True))
    p.append(text(ox + 40, oy - ah + 34, "p = p₀(1−Lh/T₀)^5.255", size=10.5, color=NEG, anchor="start"))
    p.append(text(ox + 92, oy - ah * 0.42, "лінійна", size=10.5, color=POS, anchor="start", bold=True))
    p.append(text(ox + 92, oy - ah * 0.42 + 13, "≈ 8.3 м/гПа", size=10, color=POS, anchor="start"))
    p.append(text(ox + 92, oy - ah * 0.42 + 26, "(занижує вгорі)", size=9.5, color=MUTED, anchor="start"))

    # рамка «шкала висоти» у вільному місці справа вгорі
    box2, w2, h2 = textbox(W - 120, 120, ["шкала висоти:", "H = RT/(Mg)", "≈ 8.4 км"],
                           size=11, pad=10, fill="#f4f6f8", color=INK)
    p.append(box2)

    render(os.path.join(OUT, "baro-derivation.svg"), W, H, *p,
           title="Тиск ↔ висота: три рівні опису")


# ── gyro-drift-laws: два закони росту помилки кута ────────────────────────────
# Ідея: помилка гіроскопа росте лінійно від зсуву (b·t) і як корінь від шуму
# (ARW·√t). Показуємо обидві криві на одній осі часу.

def fig_gyro_drift_laws():
    W, H = 760, 340
    ox, oy = 80, 280
    aw, ah = 600, 210
    p = []
    p.append(text(W / 2, 50, "Зсув дає лінійний відхід (b·t), шум — блукання кута (ARW·√t)",
                  size=13, color=MUTED))
    p.append(arrow(ox, oy, ox + aw + 10, oy, color=INK, sw=1.4))
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=INK, sw=1.4))
    p.append(text(ox + aw + 4, oy + 18, "час", size=11, color=INK, anchor="end"))
    p.append(text(ox - 8, oy - ah - 2, "помилка кута", size=11, color=INK, anchor="end", bold=True))

    # лінійна від зсуву: b·t
    p.append(line(ox, oy, ox + aw, oy - ah * 0.92, color=POS, sw=2.6))
    p.append(text(ox + aw - 6, oy - ah * 0.92 - 8, "Δθ = b·t  (зсув)", size=11.5, color=POS, anchor="end", bold=True))

    # корінь від шуму: ARW·√t
    pts = []
    for i in range(101):
        t = i / 100.0
        x = ox + t * aw
        y = oy - ah * 0.62 * math.sqrt(t)
        pts.append((x, y))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in pts), NEG))
    p.append(text(ox + aw - 6, oy - ah * 0.62 - 8, "σ = ARW·√t  (шум)", size=11.5, color=NEG, anchor="end", bold=True))

    # приклад-мітка: 0.05°/с → 3° за 60 с
    p.append(circle(ox + aw * 0.5, oy - ah * 0.46, 4, fill=POS, stroke=INK, sw=1.2))
    p.append(text(ox + aw * 0.5 + 8, oy - ah * 0.46 - 4, "напр. 0.05°/с → 3° за 60 с", size=10.5, color=MUTED, anchor="start"))

    # мораль
    p.append(text(ox + 10, oy - ah + 8, "лінійне з часом переганяє корінь → зсув приборкують калібруванням при ввімкненні",
                  size=10.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "gyro-drift-laws.svg"), W, H, *p,
           title="Два закони росту помилки гіроскопа")


# ── allan-averaging: як з одного запису робимо кластери довжини τ ─────────────
# Ідея вставки math-allan-variance: беремо довгий запис нерухомого гіроскопа,
# ріжемо на кластери тривалості τ, усереднюємо кожен, і дивимося на РІЗНИЦЮ
# сусідніх середніх. Малий τ ловить швидкий шум; великий τ згладжує шум, але
# показує повільний дрейф. Один рядок даних — три розкрої на різні τ.

def fig_allan_averaging():
    W, H = 780, 430
    p = []
    p.append(text(W / 2, 46, "Один запис ділимо на кластери довжини τ і дивимось РІЗНИЦЮ сусідніх середніх",
                  size=12.5, color=MUTED))

    ox, oy, aw = 60, 78, 660          # ліворуч-верх осі часу, ширина
    # спільна «стрічка сигналу»: повільний дрейф + швидкий шум (детермінований,
    # щоб figs був стабільний і не зациклювався).
    import math as _m
    def sig(u):                       # u ∈ [0,1] уздовж запису
        drift = 0.9 * _m.sin(1.7 * u)                 # повільна хвиля (дрейф)
        noise = 0.0
        for k in (11, 17, 23, 31):                     # кілька «швидких» гармонік
            noise += _m.sin(k * 6.283 * u + k)
        return drift + 0.16 * noise

    rows = [
        ("малий τ: кластери короткі — у різниці живе ШВИДКИЙ ШУМ", 12, POS,  0.055),
        ("середній τ", 4, MUTED, 0.11),
        ("великий τ: кластери довгі — шум усереднився, лишився ПОВІЛЬНИЙ ДРЕЙФ", 2, NEG, 0.22),
    ]
    rh = 108
    for ri, (lab, ncl, col, tau) in enumerate(rows):
        y0 = oy + ri * rh
        yc = y0 + 40                  # осьова лінія цього рядка
        # сама стрічка сигналу (однакова для всіх рядків)
        pts = []
        for i in range(0, aw + 1, 3):
            u = i / float(aw)
            pts.append((ox + i, yc - sig(u) * 20))
        p.append('<polyline points="%s" fill="none" stroke="#c8ccd2" stroke-width="1.4"/>' % (
            " ".join("%.1f,%.1f" % q for q in pts)))
        # межі кластерів + середнє кожного кластера
        cw = aw / float(ncl)
        means = []
        for c in range(ncl):
            xa = ox + c * cw
            # середнє сигналу на кластері
            s = 0.0; cnt = 0
            for i in range(int(c * cw), int((c + 1) * cw), 2):
                s += sig(i / float(aw)); cnt += 1
            m = s / max(cnt, 1)
            means.append((xa + cw / 2, yc - m * 20))
            p.append(line(xa, y0 + 6, xa, y0 + 74, color="#dfe3e8", sw=1.0, dash="2,3"))
            p.append(line(xa + 2, yc - m * 20, xa + cw - 2, yc - m * 20, color=col, sw=2.4))
        p.append(line(ox + aw, y0 + 6, ox + aw, y0 + 74, color="#dfe3e8", sw=1.0, dash="2,3"))
        # стрілки різниці між сусідніми середніми
        for a in range(len(means) - 1):
            (x1, yy1), (x2, yy2) = means[a], means[a + 1]
            xm = (x1 + x2) / 2
            p.append(arrow(xm, yy1, xm, yy2, color=col, sw=1.6))
        p.append(text(ox, y0 - 2, lab, size=11, color=col, anchor="start", bold=True))
    render(os.path.join(OUT, "allan-averaging.svg"), W, H, *p,
           title="Дисперсія Аллана: різниця сусідніх середніх на масштабі τ")


# ── allan-deviation-slopes: log-log «ванна» з нахилами −½, 0, +½ ──────────────
# Ідея: девіація Аллана σ_A(τ) на log-log дає впізнавані прямі ділянки, кожна —
# свій шум. −½ ARW (читаємо на τ=1 с), 0 нестабільність зсуву (мінімум ×0.664),
# +½ rate random walk. Плюс тонкі краї −1 (квантування) і +1 (rate ramp).

def fig_allan_slopes():
    W, H = 760, 470
    p = []
    ox, oy = 96, 96                    # верх-ліво області графіка
    aw, ah = 600, 300                  # ширина/висота області
    bx, by = ox, oy + ah               # нижній-лівий кут (початок осей)

    # осі
    p.append(line(bx, oy, bx, by, color=INK, sw=1.6))          # вертикаль
    p.append(line(bx, by, bx + aw, by, color=INK, sw=1.6))     # горизонталь
    p.append(text(bx - 66, oy + ah / 2, "σ_A(τ)", size=13, color=INK, bold=True))
    p.append(text(bx - 66, oy + ah / 2 + 18, "(log)", size=10.5, color=MUTED))
    p.append(text(bx + aw / 2, by + 52, "інтервал усереднення  τ  (log)", size=13, color=INK, bold=True))
    # мітки декад по x (τ)
    for i, lb in enumerate(["0.01", "0.1", "1", "10", "100", "1000"]):
        x = bx + aw * i / 5.0
        p.append(line(x, by, x, by + 5, color=INK, sw=1.2))
        p.append(text(x, by + 22, lb + " с", size=10.5, color=MUTED))
        if i > 0:
            p.append(line(x, oy, x, by, color="#eef0f3", sw=1.0))

    # крива-«ванна»: задаємо ключові точки (x у частках ширини, y у частках висоти
    # від низу вгору) — три головні ділянки з правильними нахилами.
    # На log-log нахил −½ означає: 10× по τ → падіння в √10 ≈ 3.16× по σ.
    def X(fx): return bx + aw * fx
    def Y(fy): return by - ah * fy     # fy від 0 (низ) до 1 (верх)

    # опорні вузли (fx, fy): квантування(−1) · ARW(−½) · зсув(0) · RRW(+½) · ramp(+1)
    nodes = [(0.00, 0.92), (0.14, 0.66),   # −1 квантування (крутий спад)
             (0.14, 0.66), (0.50, 0.30),   # −½ ARW
             (0.50, 0.30), (0.66, 0.26),   # 0 нестабільність зсуву (полиця з мінімумом)
             (0.66, 0.26), (0.88, 0.52),   # +½ rate random walk
             (0.88, 0.52), (1.00, 0.86)]   # +1 rate ramp
    curve = [(X(fx), Y(fy)) for (fx, fy) in nodes]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3" stroke-linejoin="round"/>' % (
        " ".join("%.1f,%.1f" % q for q in curve), NEG))

    # підписи ділянок із нахилами
    def seg_lab(fx, fy, s, col, dx=0, dy=0):
        p.append(text(X(fx) + dx, Y(fy) + dy, s, size=11.5, color=col, bold=True))

    seg_lab(0.05, 0.86, "−1", POS, dy=-6)
    p.append(text(X(0.055), Y(0.86) + 12, "квантування", size=9.5, color=MUTED, anchor="middle"))
    seg_lab(0.30, 0.52, "нахил −½", POS, dy=-8)
    p.append(text(X(0.30), Y(0.52) + 10, "angle random walk (ARW)", size=9.5, color=MUTED))
    seg_lab(0.58, 0.24, "нахил 0", FIELD, dy=-10)
    p.append(text(X(0.58), Y(0.24) - 24, "нестабільність зсуву", size=9.5, color=MUTED))
    seg_lab(0.78, 0.40, "нахил +½", NEG, dy=-6)
    p.append(text(X(0.785), Y(0.40) + 12, "rate random walk", size=9.5, color=MUTED))
    seg_lab(0.955, 0.72, "+1", NEG, dy=-4)
    p.append(text(X(0.95), Y(0.72) + 12, "rate ramp", size=9.5, color=MUTED, anchor="middle"))

    # read-off ARW на τ=1 с: вертикаль на x=«1 с» до кривої
    x1 = X(0.40)                        # приблизно там, де нахил −½ (τ≈1 с область)
    # знайдемо y на −½ ділянці в точці fx=0.40 інтерполяцією між (0.14,0.66)-(0.50,0.30)
    t = (0.40 - 0.14) / (0.50 - 0.14)
    fy1 = 0.66 + t * (0.30 - 0.66)
    p.append(line(X(0.40), by, X(0.40), Y(fy1), color=POS, sw=1.2, dash="4,3"))
    p.append(line(bx, Y(fy1), X(0.40), Y(fy1), color=POS, sw=1.2, dash="4,3"))
    p.append(circle(X(0.40), Y(fy1), 4, fill=POS, stroke=INK, sw=1.2))
    p.append(text(X(0.40) + 8, Y(fy1) - 8, "ARW тут (τ=1 с)", size=10, color=POS, anchor="start", bold=True))

    # read-off нестабільності зсуву: у найнижчій точці кривої (полиця, fy≈0.26)
    p.append(circle(X(0.66), Y(0.26), 4, fill=FIELD, stroke=INK, sw=1.2))
    p.append(line(bx, Y(0.26), X(0.66), Y(0.26), color=FIELD, sw=1.2, dash="4,3"))
    p.append(text(X(0.66) + 8, Y(0.26) + 16, "мінімум × 0.664 = нестабільність зсуву",
                  size=10, color=FIELD, anchor="start", bold=True))

    render(os.path.join(OUT, "allan-deviation-slopes.svg"), W, H, *p,
           title="Девіація Аллана: нахили читаються як типи шуму")


if __name__ == "__main__":
    fig_specific_force()
    fig_yaw_blind_spot()
    fig_pressure_altitude()
    fig_baro_drift()
    fig_vibration()
    # детальна частина
    fig_specific_force_vector()
    fig_complementary_crossover()
    fig_baro_derivation()
    fig_gyro_drift_laws()
    # вставка math-allan-variance
    fig_allan_averaging()
    fig_allan_slopes()
    print("ok: figs generated")
