# -*- coding: utf-8 -*-
"""Фігури до теми «Подвійна буферизація» (дисплей: tearing/vsync).
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BACK = "#eef4ff"   # відтінок заднього буфера
SCAN = "#fbe9e7"   # заливка вже відсканованої частини


# ── tearing: запис застав сканування на півдорозі ────────────────────────────
def fig_tearing():
    W, H = 700, 330
    sx, sy, sw, sh = 90, 60, 200, 220          # екран
    p = [rect(sx, sy, sw, sh, fill=BG, stroke=INK, sw=1.8)]

    # лінія розриву посеред екрана
    ty = sy + sh * 0.46
    p.append(rect(sx, sy, sw, ty - sy, fill="#eaf3ff", stroke="none", sw=0))   # новий верх
    p.append(rect(sx, ty, sw, sy + sh - ty, fill="#f4f6f8", stroke="none", sw=0))  # старий низ
    p.append(line(sx, sy, sx, sy + sh, color=INK, sw=1.8))
    p.append(line(sx + sw, sy, sx + sw, sy + sh, color=INK, sw=1.8))
    # рухомий об'єкт, розколотий лінією розриву (коло зі зсувом половин)
    cx = sx + sw * 0.5
    p.append('<path d="M%.1f %.1f a46 46 0 0 1 92 0 z" fill="#cfe0ff" stroke="%s" stroke-width="1.6"/>'
             % (cx - 46 + 16, ty, NEG))           # верхня половина зсунута праворуч
    p.append('<path d="M%.1f %.1f a46 46 0 0 0 92 0 z" fill="#cfe0ff" stroke="%s" stroke-width="1.6"/>'
             % (cx - 46 - 16, ty, NEG))           # нижня половина зсунута ліворуч
    p.append(line(sx, ty, sx + sw, ty, color=POS, sw=2.4))
    p.append(text(sx + sw + 8, ty + 4, "лінія розриву", size=12, color=POS, anchor="start", bold=True))
    p.append(text(sx + sw / 2, sy - 10, "показаний кадр", size=12, color=MUTED))

    # пояснення праворуч: сканування згори вниз через спільний буфер
    bx = 430
    fb, fbw, fbh = (bx, 90), 170, 150
    p.append(rect(bx, 90, fbw, fbh, fill=BACK, stroke=NEG, sw=1.6))
    p.append(text(bx + fbw / 2, 110, "спільний буфер", size=12, bold=True, color=NEG))
    p.append(arrow(bx + fbw / 2, 122, bx + fbw / 2, 232, color=INK, sw=1.6))
    p.append(text(bx + fbw / 2 + 10, 180, "панель читає", size=11, color=INK, anchor="start"))
    p.append(text(bx + fbw / 2 + 10, 196, "згори вниз", size=11, color=INK, anchor="start"))
    box, bw, bh = textbox(bx + fbw / 2, 282, "ми пишемо новий кадр\nу той самий буфер", size=11, color=POS, stroke=POS, fill="#fdecea")
    p.append(box)
    render(os.path.join(OUT, "tearing.svg"), W, H, *p)


# ── подвійна буферизація: малюй у задній, показуй передній, swap ──────────────
def fig_double_buffer():
    W, H = 700, 300
    # передній буфер → панель
    fx, fy, bw, bh = 80, 90, 150, 90
    p = [rect(fx, fy, bw, bh, fill="#eaf3ff", stroke=NEG, sw=1.8)]
    p.append(text(fx + bw / 2, fy - 12, "ПЕРЕДНІЙ (front)", size=12, bold=True, color=NEG))
    p.append(text(fx + bw / 2, fy + bh / 2 + 5, "готовий кадр", size=12, color=INK))
    sc = rect(330, fy - 6, 90, bh + 12, fill=BG, stroke=INK, sw=1.6)
    p.append(sc)
    p.append(text(375, fy + bh / 2 + 5, "скло", size=12, color=MUTED))
    p.append(arrow(fx + bw, fy + bh / 2, 330, fy + bh / 2, color=NEG, sw=1.8))
    p.append(text((fx + bw + 330) / 2, fy + bh / 2 - 10, "показ", size=10, color=NEG))

    # задній буфер ← малювання
    p.append(rect(fx, 200, bw, bh, fill=BACK, stroke=FIELD, sw=1.8))
    p.append(text(fx + bw / 2, 200 - 12, "ЗАДНІЙ (back)", size=12, bold=True, color=FIELD))
    p.append(text(fx + bw / 2, 200 + bh / 2 + 5, "малюємо тут", size=12, color=INK))
    p.append(arrow(fx - 14, 200 + bh / 2, fx, 200 + bh / 2, color=FIELD, sw=1.8))
    p.append(text(fx - 18, 200 + bh / 2 - 10, "код", size=10, color=FIELD, anchor="end"))

    # swap між ними
    p.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (fx + bw + 40, fy + bh, fx + bw + 120, fy + bh + 30, fx + bw + 120, 200 - 10, fx + bw + 40, 200, POS))
    p.append('<path d="M%.1f %.1f C %.1f %.1f, %.1f %.1f, %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (fx + bw + 60, 200, fx + bw + 150, 200 - 10, fx + bw + 150, fy + bh + 30, fx + bw + 60, fy + bh, POS))
    box, _, _ = textbox(530, 150, "SWAP\nготовий ↔ чорновий", size=12, color=POS, stroke=POS, fill="#fdecea", bold=True)
    p.append(box)
    p.append(text(530, 205, "панель ніколи не читає", size=10.5, color=MUTED))
    p.append(text(530, 221, "той буфер, у який пишемо", size=10.5, color=MUTED))
    render(os.path.join(OUT, "double-buffer.svg"), W, H, *p)


# ── swap: перекинути вказівник проти копіювання ──────────────────────────────
def fig_swap():
    W, H = 700, 320
    # ЛІВОРУЧ: вказівник
    p = [text(180, 56, "перекинути вказівник", size=13, bold=True, color=FIELD)]
    p.append(rect(70, 90, 90, 60, fill="#eaf3ff", stroke=NEG, sw=1.6))
    p.append(text(115, 124, "буфер A", size=11, color=NEG))
    p.append(rect(70, 180, 90, 60, fill=BACK, stroke=FIELD, sw=1.6))
    p.append(text(115, 214, "буфер B", size=11, color=FIELD))
    p.append(circle(250, 135, 16, fill=FILL, stroke=INK, sw=1.6))
    p.append(text(250, 139, "ptr", size=10, color=INK))
    p.append(arrow(234, 130, 160, 115, color=INK, sw=1.6))
    p.append('<line x1="234" y1="142" x2="160" y2="208" stroke="%s" stroke-width="1.4" stroke-dasharray="4 3"/>' % MUTED)
    box, _, _ = textbox(180, 282, "зміна адреси · 0 копіювання", size=11, color=FIELD, stroke=FIELD, fill="#eafaf0")
    p.append(box)

    # ПРАВОРУЧ: копія
    p.append(text(520, 56, "скопіювати (blit)", size=13, bold=True, color=POS))
    p.append(rect(420, 90, 90, 60, fill=BACK, stroke=FIELD, sw=1.6))
    p.append(text(465, 124, "задній", size=11, color=FIELD))
    p.append(rect(580, 90, 90, 60, fill="#eaf3ff", stroke=NEG, sw=1.6))
    p.append(text(625, 124, "передній", size=11, color=NEG))
    p.append(arrow(510, 120, 580, 120, color=POS, sw=2.0))
    p.append(text(545, 110, "копія", size=10, color=POS))
    box, _, _ = textbox(545, 220, "повний кадр щоразу\nпрацює завжди", size=11, color=POS, stroke=POS, fill="#fdecea")
    p.append(box)
    box, _, _ = textbox(545, 282, "W×H×bpp байтів на показ", size=10.5, color=MUTED, stroke=MUTED, fill=FILL)
    p.append(box)
    p.append(line(350, 80, 350, 290, color="#d0d4d8", sw=1.2, dash="5 4"))
    render(os.path.join(OUT, "swap.svg"), W, H, *p)


# ── vsync: міняти буфери у щілині vertical blanking ───────────────────────────
def fig_vsync():
    W, H = 700, 280
    ox, oy = 60, 170
    aw = 580
    p = [arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6)]
    p.append(text(ox + aw, oy + 20, "час", size=11, italic=True, color=INK))
    # цикли: сканування — vblank — сканування ...
    span = 150
    gap = 34
    x = ox + 20
    for i in range(3):
        p.append(rect(x, oy - 70, span, 60, fill="#eaf3ff", stroke=NEG, sw=1.4))
        p.append(text(x + span / 2, oy - 36, "сканування кадру", size=10.5, color=NEG))
        # vblank — вузька зелена пауза
        if i < 3:
            gx = x + span
            p.append(rect(gx, oy - 70, gap, 60, fill="#eafaf0", stroke=FIELD, sw=1.4))
            p.append(text(gx + gap / 2, oy - 80, "vblank", size=9.5, color=FIELD, bold=True))
        x += span + gap
    # стрілка-вказівка: безпечний обмін — у паузу
    gx = ox + 20 + span + gap / 2
    p.append(arrow(gx, oy + 64, gx, oy - 4, color=FIELD, sw=1.8))
    box, _, _ = textbox(gx, oy + 86, "swap ТУТ — шва нема", size=11, color=FIELD, stroke=FIELD, fill="#eafaf0", bold=True)
    p.append(box)
    # хибний обмін — посеред сканування
    bx = ox + 20 + span * 0.5
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" stroke-dasharray="5 3" marker-end="url(#arrow)"/>'
             % (bx, oy + 64, bx, oy - 4, POS))
    box, _, _ = textbox(bx, oy + 86, "swap тут — знову розрив", size=11, color=POS, stroke=POS, fill="#fdecea")
    p.append(box)
    render(os.path.join(OUT, "vsync.svg"), W, H, *p)


# ── te-sync: розумна панель по TE проти LTDC сам ─────────────────────────────
def fig_te_sync():
    W, H = 720, 300
    # ЛІВОРУЧ: розумна панель (command mode, GRAM) — МК чекає TE
    p = [text(190, 54, "розумна панель (GRAM)", size=12.5, bold=True, color=INK)]
    p.append(rect(70, 90, 100, 56, fill=FILL, stroke=INK, sw=1.6))
    p.append(text(120, 122, "МК", size=12, bold=True))
    p.append(rect(260, 84, 110, 68, fill="#eaf3ff", stroke=NEG, sw=1.6))
    p.append(text(315, 110, "панель", size=11, color=NEG))
    p.append(text(315, 130, "+ GRAM", size=9.5, color=MUTED))
    p.append(arrow(170, 108, 260, 108, color=INK, sw=1.8))
    p.append(text(215, 100, "кадр", size=9, color=MUTED))
    p.append(arrow(260, 134, 170, 134, color=POS, sw=1.6))
    p.append(text(215, 148, "TE (безпечна мить)", size=9.5, color=POS, bold=True))
    box, _, _ = textbox(215, 210, "МК чекає TE, тоді шле кадр —\nпотрапляє в паузу панелі", size=10.5, color=FIELD, stroke=FIELD, fill="#eafaf0")
    p.append(box)

    p.append(line(400, 76, 400, 250, color="#d0d4d8", sw=1.2, dash="5 4"))

    # ПРАВОРУЧ: RGB-панель + LTDC робить усе сам
    p.append(text(560, 54, "RGB-панель + LTDC", size=12.5, bold=True, color=INK))
    p.append(rect(450, 84, 150, 72, fill=FILL, stroke=INK, sw=1.6))
    p.append(text(525, 108, "LTDC у МК", size=11.5, bold=True))
    p.append(text(525, 128, "перед + задній", size=9.5, color=MUTED))
    p.append(text(525, 146, "гортає на vblank", size=9.5, color=FIELD))
    p.append(arrow(600, 120, 660, 120, color=INK, sw=1.8))
    p.append(rect(660, 96, 48, 48, fill="#eaf3ff", stroke=NEG, sw=1.4))
    p.append(text(684, 124, "скло", size=9.5, color=NEG))
    box, _, _ = textbox(560, 210, "контролер сам тримає два буфери\nй міняє їх — без участи коду", size=10.5, color=FIELD, stroke=FIELD, fill="#eafaf0")
    p.append(box)
    render(os.path.join(OUT, "te-sync.svg"), W, H, *p)


# ── tradeoff: один буфер / два / запис у vblank ──────────────────────────────
def fig_tradeoff():
    W, H = 720, 300
    cols = [
        (60,  "один буфер", "#fdecea", POS,
         ["1× RAM — найдешевше", "може рватися", "найпростіше"]),
        (260, "подвійний буфер", "#eafaf0", FIELD,
         ["2× RAM", "розривів нема", "найплавніше"]),
        (460, "один буфер + vblank", "#eef4ff", NEG,
         ["1× RAM", "розривів нема", "лиш дрібні зміни"]),
    ]
    cw = 180
    p = []
    for x, title, fill, accent, rows in cols:
        p.append(rect(x, 70, cw, 180, fill=BG, stroke=accent, sw=1.8))
        p.append(rect(x, 70, cw, 34, fill=fill, stroke=accent, sw=1.8))
        p.append(text(x + cw / 2, 92, title, size=12, bold=True, color=accent))
        for i, r in enumerate(rows):
            yy = 130 + i * 38
            p.append(circle(x + 18, yy - 4, 3.5, fill=accent, stroke=accent, sw=1))
            p.append(text(x + 32, yy, r, size=11, color=INK, anchor="start"))
    p.append(text(W / 2, 280, "скільки RAM — стільки й плавності можеш дозволити", size=11.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "tradeoff.svg"), W, H, *p)


# ── (detailed) TE: command mode віддає TE-імпульс, video mode — ні ───────────
def fig_te_modes():
    W, H = 720, 320
    # ВЕРХ: command mode — панель з GRAM сама освіжає, TE сигналить паузу
    p = [text(W / 2, 50, "command mode (панель із GRAM)", size=13, bold=True, color=NEG)]
    ox, oy = 60, 110
    span, gap = 150, 40
    x = ox
    for i in range(3):
        p.append(rect(x, oy - 40, span, 34, fill="#eaf3ff", stroke=NEG, sw=1.3))
        p.append(text(x + span / 2, oy - 18, "панель читає GRAM", size=9.5, color=NEG))
        gx = x + span
        p.append(rect(gx, oy - 40, gap, 34, fill="#eafaf0", stroke=FIELD, sw=1.3))
        x += span + gap
    # TE-імпульси на межах
    x = ox + span
    for i in range(3):
        p.append('<path d="M%.1f %.1f v-22 h10 v22" fill="none" stroke="%s" stroke-width="1.8"/>' % (x + gap / 2 - 5, oy + 30, POS))
        x += span + gap
    p.append(arrow(ox - 12, oy + 30, ox + 3 * (span + gap), oy + 30, color=INK, sw=1.4))
    p.append(text(ox + 3 * (span + gap) - 6, oy + 50, "TE-ніжка (GPIO)", size=10, color=POS, anchor="end", bold=True))
    p.append(text(ox, oy + 50, "імпульс = «зараз пауза, писати безпечно»", size=10, color=MUTED, anchor="start"))

    # НИЗ: video mode — МК сам жене пікселі, TE нерелевантна
    p.append(text(W / 2, 210, "video mode (RGB-потік від МК)", size=13, bold=True, color=MUTED))
    oy2 = 260
    p.append(arrow(ox - 12, oy2, ox + 3 * (span + gap), oy2, color=INK, sw=1.4))
    x = ox
    for i in range(3):
        p.append(rect(x, oy2 - 30, span, 26, fill="#f4f6f8", stroke=MUTED, sw=1.3))
        p.append(text(x + span / 2, oy2 - 12, "МК жене рядки", size=9.5, color=MUTED))
        gx = x + span
        p.append(rect(gx, oy2 - 30, gap, 26, fill="#eafaf0", stroke=FIELD, sw=1.2))
        x += span + gap
    p.append(text(ox + 3 * (span + gap) - 6, oy2 + 22, "TE не потрібна — синхронізує сам VSYNC потоку", size=10, color=MUTED, anchor="end"))
    render(os.path.join(OUT, "te-modes.svg"), W, H, *p)


# ── (detailed) bandwidth: flip = 0, copy = весь кадр × 60/с ───────────────────
def fig_bandwidth():
    W, H = 700, 300
    p = [text(W / 2, 46, "ціна обміну на шину пам'яті", size=13, bold=True, color=INK)]
    base = 250
    # flip — нульовий стовпчик
    fx = 180
    p.append(rect(fx - 40, base - 4, 80, 4, fill=FIELD, stroke=FIELD, sw=1))
    p.append(text(fx, base + 24, "перекид вказівника", size=11, color=FIELD, bold=True))
    p.append(text(fx, base + 42, "≈ 0 байтів/с", size=11, color=FIELD))
    # copy — високий стовпчик
    cx = 480
    bh = 150
    p.append(rect(cx - 45, base - bh, 90, bh, fill="#fdecea", stroke=POS, sw=1.6))
    p.append(text(cx, base + 24, "копія щокадру", size=11, color=POS, bold=True))
    p.append(text(cx, base + 42, "750 КБ × 60 ≈ 45 МБ/с", size=11, color=POS))
    p.append(text(cx, base - bh - 10, "увесь кадр, 60 разів на секунду", size=10, color=MUTED))
    p.append(line(90, base, 620, base, color=INK, sw=1.4))
    render(os.path.join(OUT, "bandwidth.svg"), W, H, *p)


# ── (detailed) triple buffer: писар ніколи не чекає ──────────────────────────
def fig_triple():
    W, H = 700, 280
    p = [text(W / 2, 46, "потрійна буферизація: показ · готовий · малюємо", size=13, bold=True, color=INK)]
    labels = [("показується", "#eaf3ff", NEG), ("готовий, чекає", "#eafaf0", FIELD), ("малюємо", BACK, POS)]
    bw, gap = 150, 40
    x0 = (W - (3 * bw + 2 * gap)) / 2
    for i, (lab, fill, acc) in enumerate(labels):
        x = x0 + i * (bw + gap)
        p.append(rect(x, 90, bw, 70, fill=fill, stroke=acc, sw=1.8))
        p.append(text(x + bw / 2, 130, lab, size=11.5, bold=True, color=acc))
        p.append(text(x + bw / 2, 78, "буфер %d" % (i + 1), size=10, color=MUTED))
    # ротація по колу
    p.append(text(W / 2, 200, "ролі обертаються по колу на кожен vblank", size=11, color=MUTED, italic=True))
    p.append(text(W / 2, 224, "писар завжди має вільний буфер → ніколи не стоїть; платня — +1 кадр пам'яті й лагу", size=10.5, color=INK))
    render(os.path.join(OUT, "triple.svg"), W, H, *p)


if __name__ == "__main__":
    fig_tearing()
    fig_double_buffer()
    fig_swap()
    fig_vsync()
    fig_te_sync()
    fig_tradeoff()
    fig_te_modes()
    fig_bandwidth()
    fig_triple()
    print("done")
