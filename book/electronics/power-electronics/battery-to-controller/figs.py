# -*- coding: utf-8 -*-
"""Фігури до теми «Батарея до контролера».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── 1. Ланцюг живлення: комірка → захист → регулятор → контролер ──────────────
def fig_chain():
    W, H = 720, 300
    f = [text(W / 2, 28, "Дорога від комірки до контролера: чотири ланки",
              size=16, bold=True)]

    y = 92
    h = 66
    # координати центрів чотирьох блоків
    blocks = [
        (95,  "Комірка\n3.0–4.2 В", "#fdecea", POS),
        (270, "Захист\n(відсікач)", FILL, LINE),
        (445, "Регулятор\n→ 3.3 В", "#e9f7ef", FIELD),
        (620, "Контролер\n3.3 В ±5%", "#eaf0fd", NEG),
    ]
    for cx, label, fill, stroke in blocks:
        f.append(fitbox(cx - 72, y, 144, h, label, size=14,
                        fill=fill, stroke=stroke, sw=1.8, bold=True))

    # стрілки між блоками — напис зверху показує, що «тече»
    def flow(x1, x2, cap):
        f.append(arrow(x1, y + h / 2, x2, y + h / 2, sw=2.2))
        f.append(text((x1 + x2) / 2, y - 8, cap, size=11, color=MUTED))
    flow(167, 198, "енергія")
    flow(342, 373, "той самий струм")
    flow(517, 548, "рівні 3.3 В")

    # підписи-ролі під кожним блоком
    roles = [
        (95,  "джерело: напруга\nповзе з розрядом"),
        (270, "рве коло за межами\nбезпечного вікна"),
        (445, "тримає вихід сталим,\nкуди б не пішов вхід"),
        (620, "живиться тим, що\nдав регулятор"),
    ]
    for cx, r in roles:
        f.append(mtext(cx, y + h + 26, r, size=11, color=MUTED))

    # знизу: спад напруги вздовж дороги
    yb = 250
    f.append(text(W / 2, yb - 14, "напруга вздовж дороги", size=12, color=INK, bold=True))
    f.append(text(95,  yb + 6, "3.0…4.2 В (плаває)", size=11, color=POS))
    f.append(text(270, yb + 6, "≈ вхід", size=11, color=MUTED))
    f.append(text(445, yb + 6, "3.3 В", size=11, color=FIELD))
    f.append(text(620, yb + 6, "3.3 В (тверді)", size=11, color=NEG))

    render(os.path.join(IMG, "chain.svg"), W, H, *f)


# ── 2. Лінійний vs імпульсний: куди дівається зайва напруга ───────────────────
def fig_linear_vs_switch():
    W, H = 720, 320
    f = [text(W / 2, 28, "Скинути 4.0 В до 3.3 В: два шляхи",
              size=16, bold=True)]

    # --- ліва половина: лінійний (спалює різницю в тепло) ---
    lx = 180
    f.append(text(lx, 62, "Лінійний (LDO)", size=14, bold=True, color=POS))
    # труба вхід
    f.append(rect(lx - 130, 96, 60, 34, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(lx - 100, 118, "4.0 В", size=12, color=POS))
    # «кран», що душить надлишок
    f.append(circle(lx, 113, 20, fill=FILL, stroke=LINE, sw=1.8))
    f.append(text(lx, 118, "кран", size=11))
    f.append(arrow(lx - 70, 113, lx - 20, 113, sw=2))
    f.append(arrow(lx + 20, 113, lx + 70, 113, sw=2))
    # вихід
    f.append(rect(lx + 70, 96, 60, 34, fill="#e9f7ef", stroke=FIELD, sw=1.6))
    f.append(text(lx + 100, 118, "3.3 В", size=12, color=FIELD))
    # тепло вгору
    f.append(arrow(lx, 93, lx, 60, color=POS, sw=2))
    f.append(text(lx, 50, "0.7 В × I → тепло", size=11, color=POS))
    # струм однаковий
    f.append(text(lx, 158, "струм на вході = струм на виході", size=11, color=MUTED))
    f.append(fitbox(lx - 140, 180, 280, 96,
                    "ККД ≈ 3.3 / 4.0 ≈ 82%.\nПросто й тихо, але вся різниця\nнапруг згоряє в теплі.\nЧим більший розрив вхід–вихід,\nтим гірше.",
                    size=13, fill="#fff5f4", stroke=POS, sw=1.4))

    # --- права половина: імпульсний (перекачує заряд) ---
    rx = 540
    f.append(text(rx, 62, "Імпульсний (buck)", size=14, bold=True, color=FIELD))
    f.append(rect(rx - 130, 96, 60, 34, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(rx - 100, 118, "4.0 В", size=12, color=POS))
    # ключ + котушка (символічно)
    f.append(text(rx - 28, 118, "⇄", size=22, color=INK))
    f.append(text(rx - 28, 138, "ключ", size=10, color=MUTED))
    f.append(text(rx + 18, 105, "котушка", size=10, color=MUTED))
    f.append(arrow(rx - 70, 113, rx - 44, 113, sw=2))
    f.append(arrow(rx - 8, 113, rx + 70, 113, sw=2))
    f.append(rect(rx + 70, 96, 60, 34, fill="#e9f7ef", stroke=FIELD, sw=1.6))
    f.append(text(rx + 100, 118, "3.3 В", size=12, color=FIELD))
    f.append(text(rx, 158, "менший струм на вході, більший на виході", size=11, color=MUTED))
    f.append(fitbox(rx - 140, 180, 280, 96,
                    "ККД 90–96%.\nНе палить різницю, а перекачує\nенергію порціями: менше з батареї,\nбільше в навантаження.\nЦіна — шум і складність.",
                    size=13, fill="#eefcf3", stroke=FIELD, sw=1.4))

    # роздільник
    f.append(line(360, 44, 360, 288, color=MUTED, sw=1, dash="4,4"))

    render(os.path.join(IMG, "linear-vs-switch.svg"), W, H, *f)


# ── 3. Вікно напруг: батарея плаває, контролер вимагає сталого ────────────────
def fig_window():
    W, H = 720, 330
    f = [text(W / 2, 28, "Батарея плаває — контролер цього не терпить",
              size=16, bold=True)]

    # вісь напруги зліва
    ax = 90
    top, bot = 70, 270          # 4.4 В угорі, 2.8 В унизу
    vmax, vmin = 4.4, 2.8
    def yv(v):
        return bot - (v - vmin) / (vmax - vmin) * (bot - top)
    f.append(line(ax, top - 6, ax, bot + 6, color=INK, sw=1.6))
    for v in (4.2, 3.7, 3.3, 3.0):
        yy = yv(v)
        f.append(line(ax - 5, yy, ax + 5, yy, color=INK, sw=1.4))
        f.append(text(ax - 12, yy + 4, "%.1f" % v, size=11, color=INK, anchor="end"))
    f.append(text(ax - 44, (top + bot) / 2, "В", size=12, color=MUTED))

    # смуга «батарея» — від 3.0 (пусто) до 4.2 (повно)
    bx = 200
    bw = 120
    f.append(rect(bx, yv(4.2), bw, yv(3.0) - yv(4.2), fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(bx + bw / 2, yv(4.2) - 10, "БАТАРЕЯ", size=12, bold=True, color=POS))
    f.append(text(bx + bw / 2, yv(4.2) + 20, "повна 4.2", size=11, color=POS))
    f.append(text(bx + bw / 2, yv(3.0) - 8, "пуста 3.0", size=11, color=POS))
    f.append(text(bx + bw / 2, (yv(4.2) + yv(3.0)) / 2, "1.2 В\nгуляє", size=12, color=POS, anchor="middle"))
    # стрілка розряду вниз
    f.append(arrow(bx - 14, yv(4.1), bx - 14, yv(3.1), color=MUTED, sw=1.8))
    f.append(text(bx - 26, (top + bot) / 2, "розряд", size=10, color=MUTED, anchor="end"))

    # смуга «контролер» — вузьке вікно 3.3 ±5%
    cx = 470
    cw = 120
    v_hi, v_lo = 3.465, 3.135
    f.append(rect(cx, yv(v_hi), cw, yv(v_lo) - yv(v_hi), fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(cx + cw / 2, yv(v_hi) - 26, "КОНТРОЛЕР", size=12, bold=True, color=NEG))
    f.append(text(cx + cw / 2, yv(v_hi) - 10, "хоче 3.3 ±5%", size=11, color=NEG))
    f.append(text(cx + cw / 2, (yv(v_hi) + yv(v_lo)) / 2 + 4, "≈ 0.33 В", size=11, color=NEG))
    # пунктир рівня 3.3 через усю картинку
    f.append(line(bx, yv(3.3), cx + cw, yv(3.3), color=FIELD, sw=1.4, dash="5,4"))

    # регулятор-міст між ними
    f.append(arrow(bx + bw + 6, yv(3.6), cx - 6, yv(3.3), color=FIELD, sw=2.4))
    f.append(fitbox((bx + bw + cx) / 2 - 60, yv(4.0) - 6, 120, 40, "регулятор", size=13,
                    fill="#e9f7ef", stroke=FIELD, sw=1.6, bold=True))

    f.append(text(W / 2, bot + 42,
                  "Широку хитку смугу батареї регулятор мусить утиснути у вузьке вікно живлення.",
                  size=12, color=INK))

    render(os.path.join(IMG, "window.svg"), W, H, *f)


# ── 3b. Наївний vs перевернутий вимір власного живлення через АЦП ────────────
def fig_adc_flip():
    W, H = 720, 300
    f = [text(W / 2, 26, "Як АЦП виміряти власне живлення: наївно vs перевернуто",
              size=16, bold=True)]

    # роздільник
    f.append(line(360, 46, 360, 280, color=MUTED, sw=1, dash="4,4"))

    # --- ліворуч: наївно (сліпо) ---
    lx = 180
    f.append(text(lx, 62, "Наївно: вхід = живлення", size=13, bold=True, color=POS))
    f.append(fitbox(lx - 120, 92, 110, 48, "вхід АЦП:\nживлення",
                    size=12, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(fitbox(lx + 10, 92, 110, 48, "опорна АЦП:\nживлення",
                    size=12, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(lx, 162, "вхід / опорна = 1", size=12, color=INK))
    f.append(fitbox(lx - 130, 182, 260, 74,
                    "→ АЦП завжди дає 1023.\nШкала пливе разом із входом,\n"
                    "тож просідання НЕ ВИДНО. Сліпо.",
                    size=12, fill="#fff5f4", stroke=POS, sw=1.4))

    # --- праворуч: перевернуто (бачить) ---
    rx = 540
    f.append(text(rx, 62, "Перевернуто: вхід = еталон", size=13, bold=True, color=FIELD))
    f.append(fitbox(rx - 120, 92, 110, 48, "вхід АЦП:\nеталон 1.1 В",
                    size=12, fill="#e9f7ef", stroke=FIELD, sw=1.5, bold=True))
    f.append(fitbox(rx + 10, 92, 110, 48, "опорна АЦП:\nживлення",
                    size=12, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(rx, 162, "1.1 / живлення → змінюється", size=12, color=INK))
    f.append(fitbox(rx - 130, 182, 260, 74,
                    "→ еталон нерухомий, живлення\nрухається — кожен мілівольт\n"
                    "просідання ВИДНО в цифрі.",
                    size=12, fill="#eefcf3", stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, "adc-flip.svg"), W, H, *f)


# ── 4. Brown-out із гістерезисом: два пороги, фільтр, скінченний автомат ──────
def fig_brownout():
    W, H = 720, 360
    f = [text(W / 2, 26, "Гістерезис brown-out: коли зберігатись, а коли ще ні",
              size=16, bold=True)]

    # осі
    ax, ay = 70, 250          # початок координат
    aw = 560                  # ширина осі часу
    top = 70                  # верх (висока напруга)
    vmax, vmin = 4.3, 2.9
    def yv(v):
        return ay - (v - vmin) / (vmax - vmin) * (ay - top)
    def xt(t):                # t: 0..1 вздовж осі
        return ax + t * aw
    f.append(line(ax, top - 6, ax, ay + 6, color=INK, sw=1.6))
    f.append(line(ax, ay, ax + aw + 8, ay, color=INK, sw=1.6))
    f.append(text(ax + aw + 6, ay + 18, "час", size=11, color=MUTED, anchor="end"))
    f.append(text(ax - 46, (top + ay) / 2, "напруга\nживлення", size=10, color=MUTED))

    for v in (4.2, 3.7, 3.3, 3.0):
        yy = yv(v)
        f.append(line(ax - 5, yy, ax + 4, yy, color=INK, sw=1.2))
        f.append(text(ax - 10, yy + 4, "%.1f" % v, size=10, color=INK, anchor="end"))

    # два пороги + гістерезис
    y_warn = yv(3.40)
    y_crit = yv(3.15)
    y_back = yv(3.55)         # поріг повернення в RUN (вище за warn)
    f.append(line(ax, y_warn, ax + aw, y_warn, color=POS, sw=1.3, dash="6,4"))
    f.append(text(ax + aw + 6, y_warn + 4, "поріг тривоги 3.40", size=10, color=POS, anchor="start"))
    f.append(line(ax, y_crit, ax + aw, y_crit, color="#8e44ad", sw=1.5, dash="3,3"))
    f.append(text(ax + aw + 6, y_crit + 4, "критичний 3.15", size=10, color="#8e44ad", anchor="start"))
    f.append(line(ax, y_back, ax + aw, y_back, color=FIELD, sw=1.1, dash="2,4"))
    f.append(text(ax + aw + 6, y_back + 3, "повернення 3.55", size=10, color=FIELD, anchor="start"))

    # крива напруги: повільний спад + гострі просадки-сплески
    import math
    pts = []
    N = 120
    for i in range(N + 1):
        t = i / N
        base = 4.15 - 1.05 * t                     # повільний розряд
        spike = 0.0
        # три короткі просадки від сплесків струму
        for c, d, a in ((0.30, 0.018, 0.55), (0.55, 0.02, 0.62), (0.78, 0.02, 0.30)):
            spike -= a * math.exp(-((t - c) ** 2) / (2 * d * d))
        noise = 0.02 * math.sin(t * 90)            # дрібний шум АЦП
        v = base + spike + noise
        v = max(vmin + 0.02, min(vmax - 0.02, v))
        pts.append((xt(t), yv(v)))
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (path, NEG))

    # позначки подій
    f.append(mtext(xt(0.30), yv(3.40) - 34, ["сплеск струму:", "провал < фільтра", "→ ігноруємо"],
                   size=9, color=MUTED))
    f.append(mtext(xt(0.62), yv(3.05), ["сталий спад нижче 3.40", "довше за фільтр →", "стан SAVING"],
                   size=9, color=POS))
    f.append(mtext(xt(0.82), yv(2.98) + 6, ["нижче 3.15 →", "останній флаш,", "сон"], size=9, color="#8e44ad"))

    # смужка стану знизу
    yb = 300
    f.append(text(ax, yb - 6, "стан прошивки:", size=11, bold=True, anchor="start"))
    segs = [(0.0, 0.40, "RUN", FIELD, "#eafaf1"),
            (0.40, 0.72, "SAVING", POS, "#fdecea"),
            (0.72, 1.0, "SLEEP", "#8e44ad", "#f3e9f7")]
    for a, b, lab, col, fill in segs:
        x1, x2 = xt(a), xt(b)
        f.append(rect(x1, yb, x2 - x1, 26, fill=fill, stroke=col, sw=1.4, rx=4))
        f.append(text((x1 + x2) / 2, yb + 17, lab, size=11, bold=True, color=col))

    f.append(text(W / 2, yb + 52,
                  "Короткий сплеск нижче порога — ще не привід зберігатись; фільтр і гістерезис "
                  "чекають на СТАЛЕ падіння.", size=11, color=INK))
    render(os.path.join(IMG, "brownout.svg"), W, H, *f)


# ── 5. Клеми батареї ≠ вхід MCU: де ховається падіння напруги ─────────────────
def fig_terminal_vs_pin():
    W, H = 720, 300
    f = [text(W / 2, 26, "Напруга на клемах ≠ напруга на виводі MCU",
              size=16, bold=True)]

    yline = 120
    # блоки вздовж кола струму
    f.append(fitbox(40, yline - 34, 120, 68, "Комірка\n(ЕРС +\nвнутр. опір)",
                    size=12, fill="#fdecea", stroke=POS, sw=1.6, bold=True))
    f.append(fitbox(230, yline - 30, 110, 60, "Захист +\nдроти\n(опір R)",
                    size=12, fill=FILL, stroke=LINE, sw=1.5))
    f.append(fitbox(420, yline - 30, 110, 60, "Конденсатор\nрозв'язки",
                    size=12, fill="#e9f7ef", stroke=FIELD, sw=1.5, bold=True))
    f.append(fitbox(600, yline - 30, 90, 60, "Вивід\nMCU / АЦП",
                    size=12, fill="#eaf0fd", stroke=NEG, sw=1.6, bold=True))

    # струм тече праворуч
    f.append(arrow(160, yline, 230, yline, sw=2.2))
    f.append(arrow(340, yline, 420, yline, sw=2.2))
    f.append(arrow(530, yline, 600, yline, sw=2.2))
    f.append(text(300, yline - 40, "струм сплеску I", size=10, color=MUTED))

    # де що падає
    f.append(text(100, yline + 52, "тут ЕРС\nповна", size=10, color=POS, anchor="middle"))
    f.append(mtext(285, yline + 50, ["падіння", "I·R_внутр"], size=10, color=POS))
    f.append(mtext(475, yline + 50, ["падіння", "I·R_дротів"], size=10, color=INK))
    f.append(mtext(645, yline + 50, ["те, що", "БАЧИТЬ MCU"], size=10, color=NEG))

    # виноски-рамки
    f.append(fitbox(40, 210, 300, 66,
                    "Клеми батареї просідають на I·R_внутр.\n"
                    "Ще більше губиться на опорі дротів\nі відкритих ключах захисту.",
                    size=11, fill="#fff5f4", stroke=POS, sw=1.3))
    f.append(fitbox(360, 210, 330, 66,
                    "Конденсатор розв'язки на мить тримає вивід\n"
                    "MCU вище, ніж клеми, — заряд віддає він.\n"
                    "Тому АЦП і клеми показують РІЗНЕ.",
                    size=11, fill="#eefcf3", stroke=FIELD, sw=1.3))
    render(os.path.join(IMG, "terminal-vs-pin.svg"), W, H, *f)


if __name__ == "__main__":
    fig_chain()
    fig_linear_vs_switch()
    fig_window()
    fig_adc_flip()
    fig_brownout()
    fig_terminal_vs_pin()
    print("OK: chain, linear-vs-switch, window, adc-flip, brownout, terminal-vs-pin")
