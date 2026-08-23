# -*- coding: utf-8 -*-
"""Фігури до ДЕТАЛЬНОЇ теми «Лінк під глушінням» (jamming-fhss-d).
Запуск:  python figs-d.py   → пише SVG у ./img/ з префіксом d-
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Таксономія глушилок: як розподілена потужність по смузі ────────────────
# Ідея: одна й та сама повна потужність J розкладається по осі частот по-різному —
# і саме форма розкладу вирішує, скільки шкоди вона завдає розширеному сигналу.
def fig_jammer_types():
    W, H = 760, 470
    f = [text(W / 2, 26, "Одна потужність — чотири форми: як глушилка розкладає J по смузі",
              15.5, INK, "middle", bold=True)]

    # смуга сигналу — світло-зелена підкладка на кожній панелі
    def panel(x0, y0, title):
        pw, ph = 330, 150
        f.append(rect(x0, y0, pw, ph, fill="#fbfcfd", stroke="#dde3ea", sw=1.3, rx=8))
        f.append(text(x0 + pw / 2, y0 + 20, title, 12.5, INK, "middle", bold=True))
        ax, ay = x0 + 24, y0 + ph - 26
        aw, ah = pw - 48, ph - 58
        # смуга розширеного сигналу (зелена підкладка на всю ширину)
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eef6ef" stroke="none"/>'
                 % (ax, ay - 0.16 * ah, aw, 0.16 * ah))
        f.append(line(ax, ay, ax + aw, ay, color=MUTED, sw=1.1))
        f.append(text(x0 + pw / 2, y0 + ph - 6, "частота", 9.5, MUTED, "middle"))
        return ax, ay, aw, ah

    # A. Загороджувальна (barrage): рівна низька заливка на всю смугу
    ax, ay, aw, ah = panel(30, 44, "Загороджувальна: тонко на всю смугу")
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" stroke="%s" stroke-width="1.4"/>'
             % (ax, ay - 0.30 * ah, aw, 0.30 * ah, POS))
    f.append(text(ax + aw / 2, ay - 0.30 * ah - 7, "рівна, слабка скрізь", 9.5, POS, "middle"))

    # B. Точкова (spot/tone): одна висока вузька лінія
    ax, ay, aw, ah = panel(400, 44, "Точкова: уся сила в одну лінію")
    f.append('<rect x="%.1f" y="%.1f" width="14" height="%.1f" rx="2" fill="#fdecea" stroke="%s" stroke-width="2"/>'
             % (ax + 0.46 * aw, ay - 0.92 * ah, 0.92 * ah, POS))
    f.append(text(ax + 0.46 * aw + 7, ay - 0.92 * ah - 7, "гучна, вузька", 9.5, POS, "middle"))

    # C. Часткова смуга (partial-band): середня заливка на частину
    ax, ay, aw, ah = panel(30, 210, "Часткова смуга: сильно на частку ρ")
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" stroke="%s" stroke-width="1.6"/>'
             % (ax + 0.10 * aw, ay - 0.62 * ah, 0.34 * aw, 0.62 * ah, POS))
    f.append(text(ax + 0.10 * aw + 0.17 * aw, ay - 0.62 * ah - 7, "частка ρ, помірно", 9.5, POS, "middle"))

    # D. Слідкувальна (follower): вузька лінія + стрілка «женеться»
    ax, ay, aw, ah = panel(400, 210, "Слідкувальна: женеться за стрибком")
    f.append('<rect x="%.1f" y="%.1f" width="13" height="%.1f" rx="2" fill="#eef6ef" stroke="%s" stroke-width="2"/>'
             % (ax + 0.24 * aw, ay - 0.80 * ah, 0.80 * ah, FIELD))
    f.append(text(ax + 0.24 * aw + 6, ay - 0.80 * ah - 7, "сигнал", 9, FIELD, "middle"))
    f.append('<rect x="%.1f" y="%.1f" width="13" height="%.1f" rx="2" fill="#fdecea" stroke="%s" stroke-width="2"/>'
             % (ax + 0.60 * aw, ay - 0.62 * ah, 0.62 * ah, POS))
    f.append(text(ax + 0.60 * aw + 6, ay - 0.62 * ah - 7, "завада", 9, POS, "middle"))
    f.append(arrow(ax + 0.34 * aw, ay - 0.40 * ah, ax + 0.58 * aw, ay - 0.40 * ah, color=INK, sw=1.6))
    f.append(text(ax + 0.47 * aw, ay - 0.40 * ah - 6, "навздогін", 9, INK, "middle"))

    f.append(fitbox(W / 2 - 250, 420, 500, 34,
                    "Повна потужність J однакова скрізь — розширений сигнал найлегше топить та форма, "
                    "що збирає J у вузьку частку смуги (точкова, часткова, слідкувальна)",
                    size=11, fill="#f4f6f8", stroke=MUTED, color=INK))

    render(os.path.join(IMG, "d-jammer-types.svg"), W, H, *f)


# ── 2. Виведення виграшу обробки з осей часу й частоти ────────────────────────
# Ідея: чип у N разів коротший за біт → його спектр у N разів ширший; той самий
# множник N — це і виграш обробки. Показуємо це в парі час↔частота.
def fig_pg_derive():
    W, H = 760, 430
    f = [text(W / 2, 26, "Звідки береться виграш: короткий чип = широкий спектр",
              15.5, INK, "middle", bold=True)]

    # ── верх: вісь часу ──
    tx, ty = 70, 130
    tw = 620
    f.append(text(tx - 6, ty - 30, "у часі", 12, INK, "end", bold=True))
    # один біт
    f.append(line(tx, ty, tx + tw, ty, color=MUTED, sw=1.1))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="26" rx="3" fill="#eef6ef" stroke="%s" stroke-width="1.8"/>'
             % (tx, ty - 40, tw, FIELD))
    f.append(text(tx + tw / 2, ty - 24, "один біт даних — тривалість T_b", 11, FIELD, "middle", bold=True))
    # чипи всередині
    nchip = 10
    cw = tw / nchip
    for i in range(nchip):
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="16" fill="%s" stroke="#ffffff" stroke-width="1"/>'
                 % (tx + i * cw, ty + 8, cw, POS if i % 2 else NEG))
    f.append(text(tx + tw / 2, ty + 44, "той самий біт, подрібнений на N чипів — кожен коротший у N разів (T_c = T_b / N)",
                  10.5, MUTED, "middle"))

    # стрілка перетворення
    f.append(arrow(W / 2, ty + 60, W / 2, ty + 92, color=INK, sw=2))
    f.append(text(W / 2 + 90, ty + 80, "коротше в часі → ширше в спектрі", 10.5, INK, "middle"))

    # ── низ: вісь частоти ──
    fx, fy = 70, 350
    fw = 620
    f.append(text(fx - 6, fy - 60, "у спектрі", 12, INK, "end", bold=True))
    f.append(line(fx, fy, fx + fw, fy, color=MUTED, sw=1.1))
    f.append(text(fx + fw / 2, fy + 20, "частота", 10, MUTED, "middle"))
    # вузький спектр біта — висока купка в центрі
    f.append('<rect x="%.1f" y="%.1f" width="46" height="90" rx="3" fill="#eef6ef" stroke="%s" stroke-width="2"/>'
             % (fx + fw / 2 - 23, fy - 90, FIELD))
    f.append(text(fx + fw / 2, fy - 98, "спектр біта: вузький, W_дані", 10.5, FIELD, "middle", bold=True))
    # широкий спектр чипів — низька заливка на всю ширину
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="24" rx="3" fill="#fbeeee" stroke="%s" stroke-width="1.6"/>'
             % (fx + 30, fy - 24, fw - 60, POS))
    f.append(text(fx + fw / 2, fy - 30, "спектр чипів: у N разів ширший, W_розш = N · W_дані", 10.5, POS, "middle"))
    # двобічні стрілки-розміри
    f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1" marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
             % (fx + 30, fy + 6, fx + fw - 30, fy + 6, MUTED))

    f.append(fitbox(fx + 120, fy - 70, 380, 30,
                    "виграш = W_розш / W_дані = T_b / T_c = N (число чипів на біт)",
                    size=12, fill="#ffffff", stroke=NEG, color=INK))

    render(os.path.join(IMG, "d-pg-derive.svg"), W, H, *f)


# ── 3. Кореляція розгортання: свій код → +1, чужий/завада → біля нуля ─────────
# Ідея: приймач множить прийняте на локальний код і СУМУЄ по біту. Для «свого»
# коду добуток скрізь +1 (сума = N). Для завади добуток стрибає ±1 (сума ≈ 0).
def fig_correlation():
    W, H = 760, 420
    f = [text(W / 2, 26, "Розгортання = кореляція: свій код підсумовується, чуже гаситься",
              15, INK, "middle", bold=True)]
    N = 12
    ox = 80
    cw = (W - 2 * ox) / N

    def row(y, seq, label, color):
        f.append(text(ox - 10, y + 4, label, 11, INK, "end", bold=True))
        for i, v in enumerate(seq):
            fill = "#eef6ef" if v > 0 else "#eaf0fd"
            st = FIELD if v > 0 else NEG
            f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="22" rx="2" fill="%s" stroke="%s" stroke-width="1.4"/>'
                     % (ox + i * cw + 1, y - 11, cw - 2, fill, st))
            f.append(text(ox + i * cw + cw / 2, y + 4, "+1" if v > 0 else "−1", 9.5, st, "middle"))

    code = [1, -1, 1, 1, -1, -1, 1, -1, -1, 1, -1, 1]

    # A. свій сигнал (== код) × код = скрізь +1
    f.append(text(ox - 10, 70, "СВІЙ сигнал", 11.5, FIELD, "end", bold=True))
    row(96, code, "прийнято (=код)", FIELD)
    row(126, code, "× локальний код", FIELD)
    prod = [a * b for a, b in zip(code, code)]
    row(156, prod, "= добуток", FIELD)
    f.append(fitbox(ox, 176, W - 2 * ox, 26,
                    "сума добутку = +%d  →  біт зібрався у високу купку (× N)" % sum(prod),
                    size=11.5, fill="#eef6ef", stroke=FIELD, color=INK, bold=True))

    # B. завада (стороння послідовність) × код ≈ 0
    jam = [1, 1, -1, 1, -1, 1, 1, -1, 1, -1, -1, -1]
    f.append(text(ox - 10, 236, "ЗАВАДА", 11.5, POS, "end", bold=True))
    row(262, jam, "прийнято (чуже)", POS)
    row(292, code, "× локальний код", FIELD)
    prodj = [a * b for a, b in zip(jam, code)]
    row(322, prodj, "= добуток", POS)
    f.append(fitbox(ox, 342, W - 2 * ox, 26,
                    "сума добутку = %d  →  завада розпорошилася в низьке тло (≈ 0)" % sum(prodj),
                    size=11.5, fill="#fdecea", stroke=POS, color=INK, bold=True))

    f.append(text(W / 2, 402, "Той самий локальний код: «свій» він згортає в пік, «чуже» лишає біля нуля — у цьому вся сила.",
                  11, MUTED, "middle"))
    render(os.path.join(IMG, "d-correlation.svg"), W, H, *f)


# ── 4. Слідкувальна глушилка: перегони зі швидкістю світла ────────────────────
# Ідея: щоб зіпсувати стрибок, завада має ДІЙТИ до кінця перебування на частоті.
# Її бюджет часу = (сигнал→глушилка) + обробка + (глушилка→приймач). Якщо це
# більше за час стрибка мінус (сигнал→приймач напряму) — вона спізнюється.
def fig_follower_race():
    W, H = 760, 400
    f = [text(W / 2, 26, "Слідкувальна глушилка: перегони проти часу стрибка",
              15.5, INK, "middle", bold=True)]

    # три вузли: передавач (T), глушилка (J), приймач (R)
    T = (130, 130)
    J = (620, 110)
    R = (400, 320)
    for (x, y), lab, sub, col in [(T, "передавач", "стрибає щоT_h", INK),
                                  (J, "глушилка", "слухає+б'є", POS),
                                  (R, "приймач", "чекає біт", FIELD)]:
        f.append(rect(x - 66, y - 26, 132, 52, fill="#eef3f9", stroke=col, sw=1.8, rx=8))
        f.append(text(x, y - 4, lab, 12, INK, "middle", bold=True))
        f.append(text(x, y + 14, sub, 10, MUTED, "middle"))

    # прямий шлях сигналу T→R (зелений, короткий)
    f.append(arrow(T[0] + 40, T[1] + 24, R[0] - 40, R[1] - 26, color=FIELD, sw=2.4))
    f.append(text((T[0] + R[0]) / 2 - 70, (T[1] + R[1]) / 2, "1) сигнал напряму", 10.5, FIELD, "middle", bold=True))
    f.append(text((T[0] + R[0]) / 2 - 70, (T[1] + R[1]) / 2 + 15, "час d_TR/c", 9.5, FIELD, "middle"))

    # шлях до глушилки T→J
    f.append(arrow(T[0] + 60, T[1] - 4, J[0] - 66, J[1], color=POS, sw=2))
    f.append(text((T[0] + J[0]) / 2, T[1] - 30, "2) сигнал до глушилки: d_TJ/c", 10, POS, "middle"))

    # обробка в глушилці (петля)
    f.append(text(J[0], J[1] - 40, "+ обробка τ_j", 10, POS, "middle", bold=True))

    # удар глушилки J→R
    f.append(arrow(J[0] - 40, J[1] + 26, R[0] + 50, R[1] - 20, color=POS, sw=2))
    f.append(text((J[0] + R[0]) / 2 + 30, (J[1] + R[1]) / 2, "3) удар: d_JR/c", 10, POS, "middle"))

    # часова умова
    f.append(fitbox(40, 344, W - 80, 46,
                    "Завада встигне зіпсувати хоп лише якщо  d_TJ/c + τ_j + d_JR/c  <  T_h + d_TR/c.\n"
                    "Коротший час перебування T_h (швидші стрибки) → умову виконати важче → глушилка спізнюється.",
                    size=11.5, fill="#fdecea", stroke=POS, color=INK))

    render(os.path.join(IMG, "d-follower-race.svg"), W, H, *f)


# ── 5. Часткова смуга: найгірший випадок для FHSS ─────────────────────────────
# Ідея: якщо завада «розумно» стискається в частку смуги ρ, крива втрат
# перегинається — з крутого (експонента) спаду в пологий (обернено-лінійний).
def fig_partial_band():
    W, H = 700, 430
    ox, oy = 90, 350
    aw, ah = 540, 270
    f = [text(W / 2, 26, "Часткова смуга ламає FHSS: пологий «хвіст» замість крутого спаду",
              14.5, INK, "middle", bold=True)]

    # осі: x — Eb/NJ (дБ), y — ймовірність помилки (лог, схематично зверху вниз)
    f.append(line(ox, oy, ox + aw + 12, oy, color=MUTED, sw=1.3))
    f.append(arrow(ox + aw, oy, ox + aw + 16, oy, color=MUTED, sw=1.3))
    f.append(text(ox + aw / 2, oy + 40, "запас проти завади  E_b/N_J  (більше →)", 12, MUTED, "middle"))
    f.append(line(ox, oy + 4, ox, oy - ah - 4, color=MUTED, sw=1.3))
    f.append(text(ox - 12, oy - ah / 2, "частка збитих\nбітів (гірше ↑)", 11.5, MUTED, "end"))

    def X(u):  return ox + u * aw           # u ∈ [0..1]
    def Y(v):  return oy - v * ah           # v ∈ [0..1]

    # крива 1: повношумова завада — круто вниз (експонента)
    pts1 = []
    for i in range(101):
        u = i / 100
        v = math.exp(-4.2 * u)              # круто спадає
        pts1.append("%.1f,%.1f" % (X(u), Y(v)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts1), FIELD))
    f.append(text(X(0.34), Y(math.exp(-4.2 * 0.34)) - 12, "рівномірна завада:", 11, FIELD, "start", bold=True))
    f.append(text(X(0.34), Y(math.exp(-4.2 * 0.34)) + 4, "круто вниз (експонента)", 10.5, FIELD, "start"))

    # крива 2: найгірша часткова смуга — пологий обернено-лінійний хвіст
    pts2 = []
    for i in range(101):
        u = i / 100
        v = 0.42 / (1 + 7.5 * u)            # обернено-лінійний, пологий
        pts2.append("%.1f,%.1f" % (X(u), Y(v)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts2), POS))
    f.append(text(X(0.52), Y(0.42 / (1 + 7.5 * 0.52)) - 10, "розумна часткова смуга:", 11, POS, "start", bold=True))
    f.append(text(X(0.52), Y(0.42 / (1 + 7.5 * 0.52)) + 6, "пологий хвіст (∝ 1/(E_b/N_J))", 10.5, POS, "start"))

    # стрілка «розрив»
    f.append(fitbox(X(0.60), Y(0.30), 200, 40,
                    "той самий запас — а помилок у рази більше: код+перемішування закривають цю дірку",
                    size=10, fill="#f4f6f8", stroke=MUTED, color=INK))

    render(os.path.join(IMG, "d-partial-band.svg"), W, H, *f)


# ── 6. Синхронізація: захоплення (пошук фази) + стеження ──────────────────────
# Ідея: перш ніж розгортати, приймач має ЗНАЙТИ фазу коду/стрибків (захоплення),
# а потім УТРИМУВАТИ її (стеження). Схибив на пів-чипа — виграшу немає.
def fig_sync():
    W, H = 720, 400
    f = [text(W / 2, 26, "Синхронізація — вузьке місце: спершу знайти фазу, тоді втримати",
              14.5, INK, "middle", bold=True)]

    # фаза 1: захоплення — грубий пошук зсуву
    f.append(rect(40, 56, 300, 300, fill="#fbfcfd", stroke="#dde3ea", sw=1.3, rx=8))
    f.append(text(190, 78, "1. Захоплення (acquisition)", 12.5, INK, "middle", bold=True))
    f.append(text(190, 96, "ковзний корелятор пробує зсуви", 10, MUTED, "middle"))
    # пік кореляції на правильному зсуві
    bx, by = 70, 300
    bw, bh = 240, 150
    f.append(line(bx, by, bx + bw, by, color=MUTED, sw=1.1))
    f.append(text(bx + bw / 2, by + 18, "зсув коду (чипи)", 10, MUTED, "middle"))
    peak = 0.62
    for i in range(25):
        u = i / 24
        v = 0.12 if abs(u - peak) > 0.05 else 1.0
        f.append('<rect x="%.1f" y="%.1f" width="7" height="%.1f" fill="%s"/>'
                 % (bx + u * bw - 3, by - v * bh, v * bh, FIELD if v > 0.5 else "#cfd8dc"))
    f.append(text(bx + peak * bw, by - bh - 6, "пік = знайшли фазу", 10, FIELD, "middle", bold=True))
    f.append(text(bx + 0.2 * bw, by - 0.16 * bh - 8, "тло: код «не в такт»", 9.5, MUTED, "middle"))

    # стрілка
    f.append(arrow(348, 200, 388, 200, color=INK, sw=2.2))
    f.append(text(368, 188, "зловили", 9.5, INK, "middle"))

    # фаза 2: стеження — тримаємо пік у вершині
    f.append(rect(396, 56, 300, 300, fill="#fbfcfd", stroke="#dde3ea", sw=1.3, rx=8))
    f.append(text(546, 78, "2. Стеження (tracking)", 12.5, INK, "middle", bold=True))
    f.append(text(546, 96, "петля тримає фазу на вершині", 10, MUTED, "middle"))
    # трикутник кореляції з ранньою/пізньою точками
    tx, ty = 546, 300
    f.append(line(tx - 120, ty, tx + 120, ty, color=MUTED, sw=1.1))
    f.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (tx - 110, ty, tx, ty - 150, tx + 110, ty, FIELD))
    # рання / пізня
    for dx, lab, col in [(-42, "рання", NEG), (42, "пізня", POS)]:
        yv = ty - (150 - abs(dx) * 150 / 110)
        f.append(circle(tx + dx, yv, 4.5, fill=col, stroke=col, sw=1))
        f.append(text(tx + dx, yv - 10 if dx < 0 else yv + 18, lab, 9.5, col, "middle", bold=True))
    f.append(text(tx, ty - 160, "вершина = точна фаза", 10, FIELD, "middle", bold=True))
    f.append(text(tx, ty + 20, "рання=пізня → тримаємось у центрі", 9.5, MUTED, "middle"))

    f.append(fitbox(W / 2 - 250, 366, 500, 26,
                    "Схибив фазою більш ніж на пів-чипа — «свій» код уже не збирає сигнал, і виграш обробки зникає.",
                    size=11, fill="#fdecea", stroke=POS, color=INK))
    render(os.path.join(IMG, "d-sync.svg"), W, H, *f)


if __name__ == "__main__":
    fig_jammer_types()
    fig_pg_derive()
    fig_correlation()
    fig_follower_race()
    fig_partial_band()
    fig_sync()
    print("OK: detailed figures written to", IMG)
