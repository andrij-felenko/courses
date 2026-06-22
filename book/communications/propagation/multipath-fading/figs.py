# -*- coding: utf-8 -*-
"""Фігури до теми «Багатопроменевість і завмирання».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def _wave(x0, y0, x1, amp, period, phase=0.0, color=INK, sw=1.8, step=2.0):
    """Синусоїда як <path> від x0 до x1 навколо рівня y0."""
    pts = []
    x = x0
    while x <= x1 + 0.01:
        y = y0 - amp * math.sin(2 * math.pi * (x - x0) / period + phase)
        pts.append("%.1f,%.1f" % (x, y))
        x += step
    return ('<path d="M %s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (" L ".join(pts), color, sw))


# ── 1. Хвиля приходить багатьма шляхами ─────────────────────────────────────
def fig_multipath():
    """Кілька копій однієї хвилі від TX до RX: пряма (найкоротша) і відбиті від
    стелі, підлоги, стіни. Думка — маршрути різної довжини, тож різні затримки."""
    W, H = 760, 420
    f = []

    # стіни кімнати
    f.append(rect(40, 60, 680, 300, fill="#fbfcfd", stroke=MUTED, sw=1.4))
    f.append(text(W / 2, 80, "кімната: хвиля відбивається від усього", size=12,
                  italic=True, color=MUTED))

    txx, txy = 110, 210
    rxx, rxy = 650, 210
    # передавач / приймач
    f.append(circle(txx, txy, 24, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(txx, txy + 5, "TX", size=13, bold=True, color=POS))
    f.append(circle(rxx, rxy, 24, fill="#eef3ff", stroke=NEG, sw=2))
    f.append(text(rxx, rxy + 5, "RX", size=13, bold=True, color=NEG))

    # пряма копія (найкоротша)
    f.append(line(txx + 24, txy, rxx - 24, rxy, color=FIELD, sw=2.4))
    f.append(text(W / 2, 200, "пряма (найкоротша)", size=11, bold=True, color=FIELD))

    # відбита від стелі
    f.append(line(txx + 18, txy - 14, 360, 96, color=NEG, sw=1.6, dash="6 4"))
    f.append(line(360, 96, rxx - 18, rxy - 14, color=NEG, sw=1.6, dash="6 4"))
    f.append(text(360, 88, "від стелі", size=10, color=NEG))

    # відбита від підлоги
    f.append(line(txx + 18, txy + 14, 380, 332, color=NEG, sw=1.6, dash="6 4"))
    f.append(line(380, 332, rxx - 18, rxy + 14, color=NEG, sw=1.6, dash="6 4"))
    f.append(text(380, 350, "від підлоги", size=10, color=NEG))

    # відбита від дальньої стіни (петля праворуч)
    f.append(line(txx + 22, txy + 8, 560, 300, color=MUTED, sw=1.4, dash="3 4"))
    f.append(line(560, 300, rxx - 8, rxy + 22, color=MUTED, sw=1.4, dash="3 4"))
    f.append(text(560, 290, "від меблів", size=10, color=MUTED))

    f.append(text(W / 2, 392,
                  "Кожна копія долає різну відстань — тож приходить із різною затримкою і фазою.",
                  size=12, italic=True, color=INK))
    render(os.path.join(IMG, "multipath.svg"), W, H, *f,
           title="Хвиля доходить не одним шляхом, а жменею копій")


# ── 2. Копії складаються — вирішує фаза ─────────────────────────────────────
def fig_addition():
    """Дві копії у фазі дають подвоєну амплітуду (+6 дБ); у протифазі — майже
    нуль. Те саме, що інтерференція хвиль на воді."""
    W, H = 780, 400
    f = []
    period, amp = 70, 26

    # ── у фазі ──
    yA = 120
    f.append(text(50, yA - 60, "У ФАЗІ:", size=12, bold=True, color=FIELD, anchor="start"))
    f.append(_wave(150, yA, 430, amp, period, 0.0, color=NEG, sw=1.6))
    f.append(_wave(150, yA, 430, amp, period, 0.0, color=POS, sw=1.6))
    f.append(text(460, yA + 4, "=", size=18, bold=True))
    f.append(_wave(500, yA, 760, 2 * amp, period, 0.0, color=FIELD, sw=2.6))
    f.append(text(630, yA - 56, "сильний сигнал (×2 = +6 дБ)", size=11, bold=True, color=FIELD))

    # ── у протифазі ──
    yB = 280
    f.append(text(50, yB - 60, "У ПРОТИФАЗІ:", size=12, bold=True, color=POS, anchor="start"))
    f.append(_wave(150, yB, 430, amp, period, 0.0, color=NEG, sw=1.6))
    f.append(_wave(150, yB, 430, amp, period, math.pi, color=POS, sw=1.6))
    f.append(text(460, yB + 4, "=", size=18, bold=True))
    f.append(line(500, yB, 760, yB, color=FIELD, sw=2.6))
    f.append(text(630, yB - 56, "майже нуль — «мертва зона»", size=11, bold=True, color=POS))

    f.append(text(W / 2, 380,
                  "Зсув лише на пів хвилі обертає підсилення на знищення — як інтерференція хвиль на воді.",
                  size=12, italic=True, color=INK))
    render(os.path.join(IMG, "addition.svg"), W, H, *f,
           title="Копії додаються — і все вирішує фаза")


# ── 3. Завмирання у просторі: піки й мертві зони ────────────────────────────
def fig_fading_map():
    """Уздовж лінії руху сила сигналу мерехтить: піки чергуються з провалами що
    кілька сантиметрів (між сусіднім піком і нулем ~λ/2)."""
    W, H = 780, 380
    f = []
    x0, x1 = 80, 720
    base = 250          # рівень осі
    # вісь
    f.append(line(x0, base, x1, base, color=MUTED, sw=1.4))
    f.append(text(x1, base + 20, "положення приймача →", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 8, 110, "сила", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 8, 124, "сигналу", size=11, color=MUTED, anchor="end"))

    # «мерехтлива» крива: добуток двох близьких частот дає биття піків і провалів
    pts = []
    x = x0
    while x <= x1:
        t = (x - x0) / 36.0
        env = abs(math.cos(t * 0.55)) * (0.55 + 0.45 * abs(math.sin(t * 1.9)))
        y = base - 8 - env * 150
        pts.append("%.1f,%.1f" % (x, y))
        x += 2
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" L ".join(pts), NEG))

    # позначки піка й мертвої зони
    f.append(circle(150, base - 8 - 150, 5, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(150, base - 175, "пік", size=11, bold=True, color=FIELD))
    f.append(text(150, base - 160, "зв'язок є", size=9, color=FIELD))
    f.append(circle(263, base - 12, 5, fill=POS, stroke=POS, sw=1))
    f.append(text(263, base + 38, "мертва зона", size=11, bold=True, color=POS))
    f.append(text(263, base + 53, "зв'язку нема", size=9, color=POS))

    # відстань пік→нуль ≈ λ/2
    f.append(line(150, 100, 263, 100, color=MUTED, sw=1.2, dash="4 3"))
    f.append(text(206, 92, "≈ λ/2  (на 2.4 ГГц ~6 см)", size=10, italic=True, color=MUTED))

    f.append(text(W / 2, 350,
                  "Простір — не рівне поле, а строката карта піків і ям, розкиданих що кілька сантиметрів.",
                  size=12, italic=True, color=INK))
    render(os.path.join(IMG, "fading-map.svg"), W, H, *f,
           title="Завмирання у просторі: піки й мертві зони поруч")


# ── 4. Завмирання в часі: сигнал дихає ──────────────────────────────────────
def fig_fading_time():
    """Коли щось рухається, рівень сигналу стрибає в часі; інколи провал кидає
    його під поріг чутливості — пакет губиться. Ось навіщо запас бюджету."""
    W, H = 780, 380
    f = []
    x0, x1 = 80, 720
    top, bottom = 90, 300
    thr = 250           # поріг чутливості

    # осі
    f.append(line(x0, bottom, x1, bottom, color=MUTED, sw=1.4))
    f.append(text(x1, bottom + 20, "час →", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 8, top + 10, "рівень", size=11, color=MUTED, anchor="end"))

    # поріг чутливості
    f.append(line(x0, thr, x1, thr, color=POS, sw=1.6, dash="7 4"))
    f.append(text(x1, thr - 8, "поріг чутливості", size=11, bold=True, color=POS, anchor="end"))

    # «дихання» рівня в часі (сума кількох синусів)
    pts = []
    x = x0
    while x <= x1:
        t = (x - x0) / 40.0
        v = (math.sin(t) + 0.6 * math.sin(t * 2.3 + 1) + 0.4 * math.sin(t * 4.1)) / 2.0
        y = thr - 50 - v * 70
        pts.append((x, y))
        x += 2
    path = " L ".join("%.1f,%.1f" % p for p in pts)
    f.append('<path d="M %s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path, NEG))

    # підсвітити провали нижче порога
    for (x, y) in pts:
        if y > thr:
            f.append(circle(x, y, 1.6, fill=POS, stroke=POS, sw=0))
    # підпис до одного провалу
    f.append(text(W / 2, 330,
                  "Глибокий провал на мить кидає сигнал під поріг — пакет губиться; запас бюджету це переживає.",
                  size=12, italic=True, color=INK))
    render(os.path.join(IMG, "fading-time.svg"), W, H, *f,
           title="Завмирання в часі: сигнал «дихає»")


# ── 5. Луна розмиває символи (ISI) ──────────────────────────────────────────
def fig_isi():
    """Затримані копії наповзають на наступні символи. На повільному потоці
    дрібниця; на швидкому луна попереднього символу спотворює наступний."""
    W, H = 780, 400
    f = []

    def pulses(x0, y0, n, sw_w, color, label):
        out = [text(x0, y0 - 44, label, size=12, bold=True, color=color, anchor="start")]
        for i in range(n):
            x = x0 + i * sw_w
            out.append(rect(x, y0 - 24, sw_w * 0.6, 48, fill="#eef3ff" if color == NEG else "#fff7e6",
                            stroke=color, sw=1.4))
        return out

    # ── повільні символи: луна встигає згаснути ──
    yS = 130
    f.append(text(50, yS - 70, "ПОВІЛЬНІ символи — луна встигає згаснути:", size=12,
                  bold=True, color=FIELD, anchor="start"))
    for i in range(4):
        x = 90 + i * 150
        f.append(rect(x, yS - 22, 70, 44, fill="#eafaf0", stroke=FIELD, sw=1.5))
        f.append(text(x + 35, yS + 5, "симв %d" % (i + 1), size=11, color=INK))
        # запізніла луна — окремо, не дотягується до наступного
        f.append(rect(x + 40, yS + 30, 50, 14, fill=BG, stroke=MUTED, sw=1, rx=3))
    f.append(text(720, yS + 41, "луна", size=10, italic=True, color=MUTED, anchor="end"))

    # ── швидкі символи: луна наповзає ──
    yF = 290
    f.append(text(50, yF - 70, "ШВИДКІ символи — луна наповзає на наступний:", size=12,
                  bold=True, color=POS, anchor="start"))
    for i in range(7):
        x = 90 + i * 88
        f.append(rect(x, yF - 22, 44, 44, fill="#eef3ff", stroke=NEG, sw=1.4))
    # луна попереднього символу, зсунута вправо — лягає на наступний
    for i in range(7):
        x = 90 + i * 88 + 34
        f.append(rect(x, yF - 16, 44, 32, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    f.append(text(720, yF + 36, "луна спотворює наступний біт", size=10, italic=True,
                  color=POS, anchor="end"))

    f.append(text(W / 2, 384,
                  "Розкид затримок між копіями ставить стелю швидкості: швидше — мусиш упоратися з луною.",
                  size=12, italic=True, color=INK))
    render(os.path.join(IMG, "isi.svg"), W, H, *f,
           title="Луна розмиває символи: міжсимвольна інтерференція")


# ── 6. Арсенал проти завмирань ──────────────────────────────────────────────
def fig_remedies():
    """Чотири взаємодоповняльні прийоми: рознесені антени, OFDM, розширений
    спектр, завадостійке кодування з повтором."""
    W, H = 780, 360
    f = []
    cards = [
        ("Рознесені антени", "одна в провалі —\nдруга майже напевно ні\n(провали — що ~6 см)", NEG, "#eef3ff"),
        ("OFDM", "багато вузьких піднесучих:\nкожна завмирає рівно\nй легко вирівнюється", POS, "#fdecea"),
        ("Розширений спектр", "сигнал розкидано:\nне всі частоти\nпровалюються разом", FIELD, "#eafaf0"),
        ("Кодування з повтором", "надлишковий код латає\nпоодинокі втрати або\nпросить надіслати ще раз", MUTED, "#f4f6f8"),
    ]
    bw, bh, gap = 168, 150, 20
    x0 = (W - (4 * bw + 3 * gap)) / 2
    cy = 180
    for i, (ttl, body, col, fill) in enumerate(cards):
        x = x0 + i * (bw + gap)
        f.append(rect(x, cy - bh / 2, bw, bh, fill=fill, stroke=col, sw=1.7))
        f.append(text(x + bw / 2, cy - bh / 2 + 26, ttl, size=13, bold=True, color=col))
        f.append(mtext(x + bw / 2, cy - 6, body.split("\n"), size=11, color=INK, lh=1.45))

    f.append(text(W / 2, 332,
                  "Кожен прийом б'є по слабкому місці завмирань; разом вони роблять радіолінк надійним.",
                  size=12, italic=True, color=INK))
    render(os.path.join(IMG, "remedies.svg"), W, H, *f,
           title="Арсенал проти завмирань")


# ── 7. Ворог стає другом: MIMO ──────────────────────────────────────────────
def fig_mimo():
    """Кілька антен на обох кінцях; різні відбиті шляхи дають незалежні канали,
    по них женуть кілька різних потоків. Колишній ворог множить ємність."""
    W, H = 760, 400
    f = []

    txx = 170
    rxx = 590
    ys = [150, 250]
    # TX-антени
    for i, y in enumerate(ys):
        f.append(circle(txx, y, 26, fill="#fdecea", stroke=POS, sw=2))
        f.append(text(txx, y + 5, "TX%d" % (i + 1), size=12, bold=True, color=POS))
    # RX-антени
    for i, y in enumerate(ys):
        f.append(circle(rxx, y, 26, fill="#eef3ff", stroke=NEG, sw=2))
        f.append(text(rxx, y + 5, "RX%d" % (i + 1), size=12, bold=True, color=NEG))

    # усі чотири шляхи TX→RX (кожен трохи інший через відбиття)
    for ty in ys:
        for ry in ys:
            same = (ty == ry)
            f.append(line(txx + 26, ty, rxx - 26, ry,
                          color=FIELD if same else MUTED,
                          sw=2.2 if same else 1.2,
                          dash=None if same else "4 4"))
    f.append(text(W / 2, 130, "різні відбиті шляхи = незалежні канали", size=11,
                  italic=True, color=MUTED))

    # два різні потоки
    f.append(text(txx, 100, "потік A", size=11, bold=True, color=POS))
    f.append(text(txx, 305, "потік B", size=11, bold=True, color=POS))
    f.append(text(rxx, 100, "потік A", size=11, bold=True, color=NEG))
    f.append(text(rxx, 305, "потік B", size=11, bold=True, color=NEG))

    f.append(fitbox(300, 330, 160, 40, "одна частота,\nкілька потоків одразу", size=11,
                    fill="#eafaf0", stroke=FIELD, sw=1.3, bold=True))

    f.append(text(W / 2, 388,
                  "Чим багатша багатопроменевість, тим краще MIMO розділяє потоки — ворог став другом.",
                  size=12, italic=True, color=INK))
    render(os.path.join(IMG, "mimo.svg"), W, H, *f,
           title="MIMO робить багатопроменевість другом")


if __name__ == "__main__":
    fig_multipath()
    fig_addition()
    fig_fading_map()
    fig_fading_time()
    fig_isi()
    fig_remedies()
    fig_mimo()
    print("OK: 7 figures ->", IMG)
