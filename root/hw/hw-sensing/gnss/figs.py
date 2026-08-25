# -*- coding: utf-8 -*-
# Фігури до статті «Супутникова навігація (GNSS)» (book/communications/synchronization/gnss).
# svgkit імпортуємо зі scripts/ (НЕ копіюємо). Вивід — у ./img/.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: трилатерація — три відстані пришпилюють точку ───────────────────
# Ідея, яку важко передати словами: одна відстань → ціле коло можливих місць;
# дві відстані → дві точки перетину; три → одна. Звідси й «потрібно багато».
def fig_trilateration():
    W, H = 640, 470
    parts = []

    # три «маяки» (супутники, спроєктовані на площину) і шукана точка
    P = (330, 250)                      # справжнє положення приймача
    sats = [(150, 130), (520, 150), (360, 410)]
    rs = [math.hypot(P[0] - sx, P[1] - sy) for sx, sy in sats]
    cols = [NEG, FIELD, POS]

    # кола рівної відстані від кожного маяка (геометричне місце точок)
    for (sx, sy), r, c in zip(sats, rs, cols):
        parts.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" '
                     'stroke="%s" stroke-width="2" opacity="0.85"/>' % (sx, sy, r, c))

    # радіус-відрізок від одного маяка до точки (підписана відстань)
    sx, sy = sats[0]
    parts.append(line(sx, sy, P[0], P[1], color=NEG, sw=1.5, dash="4 4"))
    mx, my = (sx + P[0]) / 2, (sy + P[1]) / 2
    parts.append(text(mx - 6, my - 8, 'd₁', size=14, color=NEG, anchor='end', italic=True))

    # маяки
    for i, (sx, sy) in enumerate(sats):
        parts.append(circle(sx, sy, 8, fill=cols[i], stroke=INK, sw=1.5))
        parts.append(text(sx, sy - 16, 'супутник %d' % (i + 1), size=12, color=INK))

    # шукана точка — перетин усіх трьох кіл
    parts.append(circle(P[0], P[1], 6, fill="#fff", stroke=INK, sw=2.5))
    b, bw, bh = textbox(P[0] + 78, P[1] + 8, "ти —\nтут", size=13, bold=True,
                        fill="#fffbe6", stroke=INK)
    parts.append(b)
    parts.append(line(P[0] + 7, P[1], P[0] + 78 - bw / 2, P[1] + 4, color=MUTED, sw=1.2))

    cap = ("Кожна виміряна відстань — це ціле коло (у просторі — сфера) можливих місць; "
           "перетин трьох пришпилює точку.")
    parts.append(fitbox(20, H - 46, W - 40, 34, cap, size=13, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'trilateration.svg'), W, H,
                  *parts, title='Трилатерація: відстані задають положення')


# ── Фігура 2: чому САМЕ чотири — годинник приймача як зайва невідома ──────────
# Похибка дешевого годинника приймача додає ОДНАКОВЕ c·Δt до КОЖНОЇ дальності.
# Тож невідомих не три (x,y,z), а чотири (+Δt) — і рівнянь треба чотири.
def fig_why_four():
    W, H = 660, 430
    parts = []

    # ліворуч: ідеальний годинник → 3 супутники, 3 невідомі
    parts.append(text(165, 70, 'якби годинник був ідеальний', size=14, bold=True))
    parts.append(fitbox(40, 88, 250, 96,
                        "3 невідомі:\n x, y, z\n\n3 рівняння → 3 супутники",
                        size=14, fill="#eaf7ef", stroke=FIELD))

    # стрілка-перехід
    parts.append(arrow(305, 150, 360, 150, color=INK, sw=2))
    parts.append(text(332, 138, 'але він', size=11, color=MUTED))
    parts.append(text(332, 174, 'дешевий', size=11, color=MUTED))

    # праворуч: реальний годинник → +Δt → 4 супутники
    parts.append(text(500, 70, 'насправді: годинник бреше на Δt', size=14, bold=True))
    parts.append(fitbox(375, 88, 250, 96,
                        "4 невідомі:\n x, y, z і Δt\n\n4 рівняння → 4 супутники",
                        size=14, fill="#fdeeee", stroke=POS))

    # суть: одна й та сама добавка c·Δt у кожній псевдодальності
    parts.append(line(40, 210, W - 40, 210, color="#dddddd", sw=1))
    parts.append(text(W / 2, 238, 'кожна виміряна дальність зміщена на ОДНЕ й те саме c·Δt:',
                      size=14, bold=True))
    eqs = ["ρ₁ = (справжня d₁) + c·Δt",
           "ρ₂ = (справжня d₂) + c·Δt",
           "ρ₃ = (справжня d₃) + c·Δt",
           "ρ₄ = (справжня d₄) + c·Δt   ← цей «оплачує» Δt"]
    for i, e in enumerate(eqs):
        parts.append(text(W / 2, 268 + i * 26, e, size=14,
                          color=(POS if i == 3 else INK)))

    cap = ("Спільне зміщення — четверта невідома; додавши один супутник, приймач "
           "обчислює і місце, і власну похибку часу.")
    parts.append(fitbox(20, H - 40, W - 40, 30, cap, size=12, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'why-four.svg'), W, H,
                  *parts, title='Чому потрібні щонайменше чотири супутники')


# ── Фігура 3: час → відстань. Чому годинник мусить бути аж такий точний ───────
# Світло долає ~30 см за наносекунду; тому 1 нс промаху = 30 см помилки дальності.
def fig_time_to_distance():
    W, H = 640, 380
    parts = []

    parts.append(text(W / 2, 64, 'дальність = час польоту × швидкість світла',
                      size=15, bold=True))
    parts.append(text(W / 2, 90, 'c ≈ 300 000 км/с  =  30 см за наносекунду',
                      size=13, color=MUTED))

    # драбина: похибка часу → похибка відстані
    rows = [("1 нс", "30 см"),
            ("1 мкс", "300 м"),
            ("1 мс", "300 км")]
    x0, y0, rh = 150, 130, 56
    parts.append(text(x0 + 60, y0 - 12, 'промах годинника', size=12, bold=True))
    parts.append(text(x0 + 330, y0 - 12, 'бреше дальність на', size=12, bold=True))
    for i, (t, d) in enumerate(rows):
        y = y0 + i * rh
        parts.append(fitbox(x0, y, 120, 40, t, size=16, bold=True,
                            fill="#eaf0fd", stroke=NEG))
        parts.append(arrow(x0 + 132, y + 20, x0 + 268, y + 20, color=INK, sw=1.8))
        parts.append(fitbox(x0 + 272, y, 150, 40, d, size=16, bold=True,
                            fill="#fdeeee", stroke=POS))

    cap = ("Щоб дальність була точна до метрів, час треба знати до наносекунд — "
           "тому на супутниках атомні годинники.")
    parts.append(fitbox(20, H - 48, W - 40, 36, cap, size=13, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'time-to-distance.svg'), W, H,
                  *parts, title='Чому час вимірюють до наносекунд')


# ── Фігура 4: похибки й драбина точності (звичайний → SBAS → RTK) ─────────────
# Звідки беруться метри помилки і як їх збивають аж до сантиметрів.
def fig_errors_rtk():
    W, H = 660, 420
    parts = []

    # ліворуч: джерела похибки, що домішуються до кожної дальності
    parts.append(text(180, 64, 'що псує дальність', size=14, bold=True))
    errs = ["атмосфера: затримка сигналу",
            "багатопроменевість: відбиття",
            "орбіта й годинник супутника",
            "шум приймача"]
    for i, e in enumerate(errs):
        parts.append(fitbox(24, 82 + i * 46, 312, 38, e, size=12,
                            fill="#fdeeee", stroke=POS))

    # праворуч: драбина точності
    parts.append(text(500, 64, 'драбина точності', size=14, bold=True))
    ladder = [("звичайний GNSS", "~3–5 м", "#fdeeee", POS),
              ("+ SBAS (WAAS/EGNOS)", "~1–2 м", "#fff7e6", "#d98c00"),
              ("+ RTK (фаза несучої, база поряд)", "~1–3 см", "#eaf7ef", FIELD)]
    for i, (name, val, fill, stroke) in enumerate(ladder):
        y = 82 + i * 64
        parts.append(fitbox(360, y, 210, 48, name, size=12, fill=fill, stroke=stroke))
        parts.append(fitbox(580, y, 60, 48, val, size=13, bold=True,
                            fill="#ffffff", stroke=stroke))
        if i < 2:
            parts.append(arrow(465, y + 50, 465, y + 62, color=INK, sw=1.6))

    cap = ("SBAS шле поправки на атмосферу й орбіти; RTK міряє фазу несучої "
           "з близькою базою — звідси сантиметри.")
    parts.append(fitbox(20, H - 48, W - 40, 36, cap, size=13, fill="#f4f6f8", stroke=MUTED))

    return render(os.path.join(OUT, 'errors-rtk.svg'), W, H,
                  *parts, title='Похибки й способи дійти до сантиметрів')


if __name__ == '__main__':
    fig_trilateration()
    fig_why_four()
    fig_time_to_distance()
    fig_errors_rtk()
    print('OK figs:', os.listdir(OUT))
