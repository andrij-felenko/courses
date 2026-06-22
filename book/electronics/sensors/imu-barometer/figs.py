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


if __name__ == "__main__":
    fig_specific_force()
    fig_yaw_blind_spot()
    fig_pressure_altitude()
    fig_baro_drift()
    fig_vibration()
    print("ok: figs generated")
