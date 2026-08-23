# -*- coding: utf-8 -*-
# Фігури для вставки math-contact-mechanics.md.
# ОКРЕМИЙ файл, щоб не чіпати figs.py статті-власника. Вивід — у ./img/.
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

COPPER = "#c9782f"
GOLD = "#c9a227"
FILMCOL = "#8e7cc3"


# ── Фігура 1: звідки береться R = ρ/(2a) — струм тисне крізь одну плямку ──────
def fig_spreading():
    W, H = 820, 430
    f = []
    f.append(text(W / 2, 30, "Опір звуження: струм протискається крізь одну плямку", size=15, bold=True))

    # ── ЛІВА ПОЛОВИНА: два бруски металу, що торкаються в одній точці ──
    cx = 250                          # центр діаграми металу
    halfw = 175                       # піврозмір брусків
    topy, boty = 70, 360
    conty = 215                       # площина контакту
    f.append(rect(cx - halfw, topy, 2 * halfw, conty - topy, fill="#eef1f5", stroke=INK, sw=1.6, rx=4))
    f.append(rect(cx - halfw, conty, 2 * halfw, boty - conty, fill="#eef1f5", stroke=INK, sw=1.6, rx=4))

    aR = 26                           # радіус плямки контакту
    # лінії струму, що сходяться до плямки згори і розходяться донизу (малюємо ПЕРШИМИ, під написами)
    for k in range(-4, 5):
        sx = cx + k * 34
        cxk = cx + (aR - 5) * (k / 4.0)
        f.append(line(sx, topy + 14, cxk, conty - 2, color=NEG, sw=1.4))
        f.append(line(cxk, conty + 2, sx, boty - 14, color=NEG, sw=1.4))

    # плямка контакту (a-spot) — поверх ліній
    f.append(circle(cx, conty, aR, fill=GOLD, stroke=INK, sw=1.6))
    # виноска «плямка 2a» — вбік, у чистий проміжок праворуч від брусків
    lead_x = cx + halfw + 6
    f.append(line(cx + aR, conty, lead_x, conty, color=INK, sw=1.2))
    f.append(text(lead_x + 4, conty - 6, "плямка", size=11, bold=True, anchor="start"))
    f.append(text(lead_x + 4, conty + 12, "радіус a", size=11, bold=True, anchor="start"))

    # ярлики «струм» — поза лівим краєм брусків, де ліній струму нема
    f.append(text(cx - halfw - 32, topy + 40, "струм", size=11, color=NEG, anchor="middle", bold=True))
    f.append(text(cx - halfw - 32, boty - 26, "струм", size=11, color=NEG, anchor="middle", bold=True))
    # ярлики металів — біля контактної площини (по центру бруска), де лінії вже зійшлися до плямки
    f.append(text(cx - halfw + 34, conty - 12, "метал А", size=11, color=MUTED, anchor="middle"))
    f.append(text(cx - halfw + 34, conty + 20, "метал Б", size=11, color=MUTED, anchor="middle"))

    # ── ПРАВА КОЛОНКА: суть (чиста зона, x від ~560) ──
    bx = 685
    body, w, h = textbox(bx, 150,
                         "Уся видима площа\nне важить — струм\nбачить лише плямку\nрадіусом a.",
                         size=12, pad=11, fill="#f4f0fb", stroke=FILMCOL, min_w=210)
    f.append(body)
    body2, w2, h2 = textbox(bx, 305,
                            "R = ρ / (2a)\n\nвдвічі ширша\nплямка → вдвічі\nменший опір",
                            size=12, pad=11, fill="#eaf5ee", stroke=FIELD, min_w=210)
    f.append(body2)

    render(os.path.join(OUT, "constriction-spreading.svg"), W, H, *f)


# ── Фігура 2: опір падає як 1/√F — крива сили проти опору ─────────────────────
def fig_force_resistance():
    W, H = 760, 430
    f = []
    f.append(text(W / 2, 30, "Тисни сильніше — опір падає, але щораз повільніше", size=15, bold=True))

    # осі
    ox, oy = 110, 350           # початок координат
    axw, axh = 560, 270
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.8))            # X
    f.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.8))            # Y
    f.append(text(ox + axw, oy + 26, "сила притиску F, грам-сила", size=12, anchor="end"))
    f.append(text(ox - 18, oy - axh - 6, "перехідний опір R", size=12, anchor="start"))

    # крива R ∝ 1/√F, нормована
    Fmin, Fmax = 5.0, 200.0
    def Rof(F):
        return 1.0 / math.sqrt(F)
    Rmax = Rof(Fmin)
    pts = []
    N = 80
    for i in range(N + 1):
        F = Fmin + (Fmax - Fmin) * i / N
        x = ox + axw * (F - Fmin) / (Fmax - Fmin)
        y = oy - (axh - 24) * (Rof(F) / Rmax)
        pts.append((x, y))
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, COPPER))

    # позначки робочих точок: 20 г, 50 г, 100 г
    for F, lab, col in [(20, "20 г\nмало", POS), (50, "50 г", MUTED), (100, "100 г\nробоча", FIELD)]:
        x = ox + axw * (F - Fmin) / (Fmax - Fmin)
        y = oy - (axh - 24) * (Rof(F) / Rmax)
        f.append(line(x, oy, x, y, color=col, sw=1.2, dash="3,3"))
        f.append(line(ox, y, x, y, color=col, sw=1.2, dash="3,3"))
        f.append(circle(x, y, 5, fill=col, stroke=INK, sw=1.4))
        f.append(mtext(x + 8, y - 10, lab, size=11, color=col, anchor="start"))

    # підпис-суть
    body, w, h = textbox(ox + axw - 150, oy - axh + 44,
                         "R ∝ 1 / √F\n\nвід 100 до 200 г —\nвиграш крихітний:\nтиснути далі марно",
                         size=11, pad=9, fill="#fff7ec", stroke=COPPER, min_w=150)
    f.append(body)

    render(os.path.join(OUT, "force-resistance-curve.svg"), W, H, *f)


# ── Фігура 3: тупий циліндрик проти коронки — тиск = F / площа ────────────────
def fig_crown_pressure():
    W, H = 760, 400
    f = []
    f.append(text(W / 2, 30, "Та сама сила, різна площа: коронка продавлює плівку", size=15, bold=True))

    filmY = 300                # рівень плівки/міді
    coppTop = filmY + 8
    # мідь + плівка — спільні для обох половин
    for x0 in (40, 410):
        f.append(rect(x0, coppTop, 310, 70, fill="#f6d9b8", stroke=COPPER, sw=1.5, rx=3))
        # плівка окислу — тонка кольорова смужка згори
        f.append(rect(x0, filmY, 310, 8, fill=FILMCOL, stroke="none", sw=0))
    f.append(text(52, coppTop + 44, "мідь", size=11, color=MUTED, anchor="start"))
    f.append(text(422, coppTop + 44, "мідь", size=11, color=MUTED, anchor="start"))
    f.append(text(300, filmY - 4, "плівка окислу/флюсу", size=10, color=FILMCOL, anchor="middle"))

    # ── ЛІВОРУЧ: тупий плоский плунжер ──
    lx = 190
    f.append(text(lx, 66, "тупе вістря", size=13, bold=True))
    f.append(rect(lx - 34, 90, 68, 150, fill="#cfd6de", stroke=INK, sw=1.5, rx=3))
    # плоский торець лягає на плівку широко
    f.append(line(lx - 34, filmY, lx + 34, filmY, color=INK, sw=3))
    f.append(arrow(lx, 100, lx, 88, color=POS, sw=2))
    f.append(text(lx, 84, "F", size=13, color=POS, bold=True))
    # плівка ціла — плунжер її не пробив
    body, w, h = textbox(lx, 355,
                         "велика площа →\nмалий тиск →\nплівка ЦІЛА",
                         size=11, pad=8, fill="#fdecea", stroke=POS, min_w=150)
    f.append(body)

    # ── ПРАВОРУЧ: коронка з зубцями ──
    rx = 560
    f.append(text(rx, 66, "коронка (зубці)", size=13, bold=True))
    f.append(rect(rx - 34, 90, 68, 130, fill="#cfd6de", stroke=INK, sw=1.5, rx=3))
    # зубці — трикутнички, що впираються вістрями
    for dx in (-22, -7, 8, 23):
        tx = rx + dx
        f.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="#cfd6de" stroke="%s" stroke-width="1.4"/>'
                 % (tx - 8, 220, tx + 8, 220, tx, filmY, INK))
        # плівка пробита під кожним вістрям — розрив
        f.append(line(tx - 4, filmY + 4, tx + 4, filmY + 4, color=FIELD, sw=3))
    f.append(arrow(rx, 100, rx, 88, color=POS, sw=2))
    f.append(text(rx, 84, "F", size=13, color=POS, bold=True))
    body2, w2, h2 = textbox(rx, 355,
                            "мала площа вістер →\nвеличезний тиск →\nплівку ПРОБИТО",
                            size=11, pad=8, fill="#eaf5ee", stroke=FIELD, min_w=150)
    f.append(body2)

    render(os.path.join(OUT, "crown-pressure.svg"), W, H, *f)


if __name__ == "__main__":
    fig_spreading()
    fig_force_resistance()
    fig_crown_pressure()
    print("done: constriction-spreading, force-resistance-curve, crown-pressure")
