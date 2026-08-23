# -*- coding: utf-8 -*-
"""Фігури до базової статті «Аналіз логів польоту/поїздки»
(root/course/embedded/flight-log-analysis).
Чистий Python, без залежностей; svgkit — зі scripts/ (не переписувати)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Дві родини логів: бортовий .bin (на SD/флеші, швидко, повно) проти
#    телеметрійного .tlog (на землі, через радіо, урізано смугою каналу).
# ─────────────────────────────────────────────────────────────────────────────
def fig_two_logs():
    W, H = 940, 470
    frags = [text(W / 2, 52, "Один політ — два різні записи", size=13, color=MUTED)]

    # Апарат посередині зверху
    b, w, h = textbox(W / 2, 96, "Автопілот у польоті", size=13, bold=True, pad=12,
                      stroke=INK, fill="#f4f6f8")
    frags.append(b)

    # Ліворуч: бортовий лог
    lx = 240
    frags.append(arrow(W / 2 - 60, 110, lx + 40, 168))
    b1, w1, h1 = textbox(lx, 200, "Бортовий лог  .bin", size=13, bold=True, pad=12,
                         min_w=230, stroke=FIELD, fill="#eafaf0")
    frags.append(b1)
    for i, ln in enumerate([
        "пишеться на SD/флеш борту",
        "повна, «сира» частота (кГц)",
        "нічого не губиться",
        "читаємо ПІСЛЯ посадки",
    ]):
        frags.append(text(lx, 244 + i * 24, "• " + ln, size=12, color=INK, anchor="middle"))

    # Праворуч: телеметрійний лог
    rx = 700
    frags.append(arrow(W / 2 + 60, 110, rx - 40, 168))
    # підпис ребра — вище й правіше самої стрілки, щоб лінія його не різала
    frags.append(text(rx + 20, 118, "по радіо, ~поки летимо", size=10, color=MUTED,
                      italic=True, anchor="end"))
    b2, w2, h2 = textbox(rx, 200, "Телеметрійний лог  .tlog", size=13, bold=True, pad=12,
                         min_w=230, stroke=NEG, fill="#eaf0fd")
    frags.append(b2)
    for i, ln in enumerate([
        "пишеться на землі (станція)",
        "лише те, що влізло в канал",
        "рідше, дещо губиться",
        "бачимо наживо в польоті",
    ]):
        frags.append(text(rx, 244 + i * 24, "• " + ln, size=12, color=INK, anchor="middle"))

    frags.append(text(W / 2, H - 44,
                      "Розслідування падіння — це майже завжди бортовий .bin: у ньому є все й на повній частоті.",
                      size=12, color=INK, bold=True))
    frags.append(text(W / 2, H - 20,
                      "Телеметрійний .tlog зручний, коли борт не пережив падіння, а на землі щось таки записалося.",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, 'two-logs.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Самоописовий потік записів: спершу FMT (креслення рядка), тоді DATA за ним.
#    Пояснює, ЧОМУ бінарний лог читається без окремого довідника полів.
# ─────────────────────────────────────────────────────────────────────────────
def fig_self_describing():
    W, H = 940, 430
    frags = [text(W / 2, 52, "Лог сам собі словник: креслення йде попереду даних", size=13, color=MUTED)]

    y = 110
    # FMT-запис (креслення)
    fb = fitbox(70, y, 360, 96,
                "FMT  ATT\nполя: TimeUS, Roll, Pitch, Yaw\nтипи:  Q      f     f     f",
                size=13, pad=12, stroke=POS, fill="#fdecea")
    frags.append(fb)
    frags.append(text(250, y - 8, "КРЕСЛЕННЯ (один раз)", size=11, color=POS, bold=True))

    # стрілка «за цим кресленням читай»
    frags.append(arrow(430, y + 48, 510, y + 48))
    frags.append(text(470, y + 34, "за ним", size=10, color=MUTED, italic=True))

    # DATA-записи (за кресленням)
    for i in range(3):
        dy = y + i * 40
        db = fitbox(510, dy, 360, 30,
                    "ATT  %d  -1.2  0.7  38.4" % (17240 + i * 25),
                    size=12, pad=8, stroke=FIELD, fill="#eafaf0")
        frags.append(db)
    frags.append(text(690, y - 8, "ДАНІ (потік, тисячі рядків)", size=11, color=FIELD, bold=True))

    # Пояснення знизу
    frags.append(line(70, 250, 870, 250, color=MUTED, dash="4 4"))
    b, w, h = textbox(W / 2, 300,
                      "Прочитав FMT ATT — знаєш, що кожен рядок ATT це час, крен, тангаж, курс.\n"
                      "Тому програма розбирає незнайомий лог сама, не питаючи, які там поля.",
                      size=12, pad=12, stroke=INK, fill="#f4f6f8")
    frags.append(b)
    frags.append(text(W / 2, 372,
                      "Telemetry .tlog натомість — це потік MAVLink-повідомлень; його «словник» — спільний опис протоколу.",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, 'self-describing.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Вібрація очима спектра: та сама тряска, що ховається в часовому графіку,
#    вилазить піком на певній частоті — і тільки в певному вікні газу.
# ─────────────────────────────────────────────────────────────────────────────
def fig_vibe_spectrum():
    W, H = 940, 470
    frags = [text(W / 2, 52, "Резонанс видно не в часі, а в спектрі", size=13, color=MUTED)]

    # Осі
    ox, oy = 110, 380          # початок координат
    aw, ah = 720, 250          # ширина/висота поля
    frags.append(line(ox, oy, ox + aw, oy, color=INK, sw=1.6))          # X
    frags.append(line(ox, oy, ox, oy - ah, color=INK, sw=1.6))          # Y
    frags.append(text(ox + aw / 2, oy + 40, "частота тряски, Гц →", size=12, color=INK))
    frags.append(text(ox - 70, oy - ah / 2, "сила", size=12, color=INK))
    frags.append(text(ox - 70, oy - ah / 2 + 16, "тряски", size=12, color=INK))

    # Мітки частот
    for hz, xf in [(0, 0.0), (100, 0.28), (200, 0.55), (300, 0.82)]:
        x = ox + aw * xf
        frags.append(line(x, oy, x, oy + 6, color=INK))
        frags.append(text(x, oy + 22, str(hz), size=11, color=MUTED))

    # Крива спектра: рівний «шумовий пол» + гострий пік ~135 Гц
    peak_x = ox + aw * 0.37
    pts = []
    for i in range(0, 121):
        xf = i / 120.0
        x = ox + aw * xf
        floor = 22 + 8 * math.sin(xf * 12)           # легкий шумовий пол
        # гострий резонансний пік
        d = (x - peak_x) / 26.0
        peak = 150 * math.exp(-d * d)
        val = floor + peak
        pts.append((x, oy - val))
    path = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (path, NEG))

    # Позначити пік
    frags.append(line(peak_x, oy - 172, peak_x, oy - 200, color=POS, dash="3 3"))
    b, bw, bh = textbox(peak_x + 6, oy - 220, "пік ≈ 135 Гц", size=12, bold=True, pad=8,
                        stroke=POS, fill="#fdecea")
    frags.append(b)

    # Підпис-діагноз
    frags.append(text(peak_x + 150, oy - 96,
                      "вилазить лише на 40–60 % газу", size=11, color=MUTED, italic=True))
    frags.append(text(peak_x + 150, oy - 78,
                      "→ резонанс рами / дисбаланс гвинта", size=11, color=INK, bold=True))

    frags.append(text(W / 2, H - 18,
                      "Часовий графік показав би просто «шум». Розклад на частоти (ШПФ) показує ДЕ саме він і від чого.",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, 'vibe-spectrum.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 4. (для вставки proj-log-parser) Байтова розкладка сирого запису ATT і як
#    рядок формату "Qffffff" ріже його на поля: різні розміри, little-endian.
#    Показує три пастки одразу — розмір поля, порядок байтів, зсув курсора.
# ─────────────────────────────────────────────────────────────────────────────
def fig_record_slicing():
    W, H = 940, 500
    frags = [text(W / 2, 46, "Один сирий запис ATT, порізаний рядком формату «Qffffff»",
                  size=13, color=MUTED)]

    # ── Ряд байтів: 3 байти шапки + 8 (Q) + 6×4 (f) = 35 байтів ──────────────
    ox, oy = 40, 100          # лівий верх стрічки байтів
    bw, bh = 24, 28           # клітинка байта
    def cell(i, fill, stroke, lab=None):
        x = ox + i * bw
        out = rect(x, oy, bw, bh, fill=fill, stroke=stroke, sw=1.2, rx=2)
        if lab is not None:
            out += text(x + bw / 2, oy + bh / 2 + 4, lab, size=10, color=INK)
        return out

    i = 0
    # шапка: 0xA3 0x95 msgid
    for lab, fl in [("A3", "#f4e0dd"), ("95", "#f4e0dd"), ("id", "#f4e0dd")]:
        frags.append(cell(i, fl, POS, lab)); i += 1
    hdr_end = i
    # поле Q — TimeUS, 8 байтів
    q_start = i
    for _ in range(8):
        frags.append(cell(i, "#eafaf0", FIELD)); i += 1
    # шість полів f — по 4 байти
    f_bounds = []
    for _ in range(6):
        f_bounds.append(i)
        for _ in range(4):
            frags.append(cell(i, "#eaf0fd", NEG)); i += 1
    total = i        # 35

    # верхні дужки-підписи полів
    def brace(i0, i1, label, color, up=True):
        x0 = ox + i0 * bw; x1 = ox + i1 * bw
        yb = oy - 12
        s = line(x0 + 2, yb, x1 - 2, yb, color=color, sw=1.4)
        s += line(x0 + 2, yb, x0 + 2, yb + 6, color=color, sw=1.4)
        s += line(x1 - 2, yb, x1 - 2, yb + 6, color=color, sw=1.4)
        s += text((x0 + x1) / 2, yb - 5, label, size=10, color=color, bold=True)
        return s

    frags.append(brace(0, hdr_end, "шапка 3 Б", POS))
    frags.append(brace(q_start, q_start + 8, "Q  TimeUS  (8 Б)", FIELD))
    fnames = ["DesRoll", "Roll", "DesPitch", "Pitch", "DesYaw", "Yaw"]
    # підписуємо лише перші три f, щоб не громадити
    for k in range(3):
        frags.append(brace(f_bounds[k], f_bounds[k] + 4,
                           "f %s" % fnames[k], NEG))
    mid_rest = ox + (f_bounds[3] + total) / 2.0 * bw
    frags.append(text(mid_rest, oy - 17,
                      "f  Pitch · DesYaw · Yaw  (по 4 Б)", size=10, color=NEG, bold=True))

    # зсув курсора під стрічкою
    frags.append(line(ox, oy + bh + 10, ox + total * bw, oy + bh + 10,
                      color=MUTED, sw=1.0, dash="3 3"))
    for off, i0 in [(0, 0), (3, hdr_end), (11, f_bounds[0]), (35, total)]:
        x = ox + i0 * bw
        frags.append(line(x, oy + bh + 6, x, oy + bh + 14, color=MUTED, sw=1.0))
        frags.append(text(x, oy + bh + 28, "+%d" % off, size=10, color=MUTED))
    frags.append(text(ox + total * bw / 2, oy + bh + 46,
                      "курсор іде по стрічці; крок = розмір поля з рядка формату, а не однаковий",
                      size=11, color=INK))

    # ── Little-endian: як 4 байти float складаються назад ────────────────────
    ly = 250
    frags.append(line(ox, ly, ox + total * bw, ly, color="#e3e6ea", sw=1.0))
    b, bw2, bh2 = textbox(230, ly + 60,
                          "Порядок байтів: little-endian.\n"
                          "float Roll у файлі:  DB 0F C9 BF  (молодший байт першим)\n"
                          "у пам'яті МК треба:  BF C9 0F DB  →  memcpy лягає як є",
                          size=12, pad=12, stroke=INK, fill="#f4f6f8")
    frags.append(b)

    # маленька стрічка 4 байтів і розворот
    sx = 560; sy = ly + 28
    raw = ["DB", "0F", "C9", "BF"]
    for j, val in enumerate(raw):
        frags.append(rect(sx + j * 34, sy, 32, 26, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
        frags.append(text(sx + j * 34 + 16, sy + 18, val, size=11, color=INK))
    frags.append(text(sx + 2 * 34, sy - 8, "як лежить у .bin (LE)", size=10, color=MUTED))
    frags.append(arrow(sx + 2 * 34, sy + 40, sx + 2 * 34, sy + 66, color=FIELD))
    for j, val in enumerate(reversed(raw)):
        frags.append(rect(sx + j * 34, sy + 70, 32, 26, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=3))
        frags.append(text(sx + j * 34 + 16, sy + 88, val, size=11, color=INK))
    frags.append(text(sx + 2 * 34, sy + 116, "число −1.5708  (float32, рад)", size=10, color=MUTED))

    frags.append(text(W / 2, H - 20,
                      "Три пастки одразу: розмір поля різний (Q=8, f=4), порядок байтів little-endian, "
                      "а курсор мусить крокувати рівно на розмір поля.",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, 'record-slicing.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# 5. [hist-blackbox] Пряма нитка ідеї бортового запису крізь ~70 років:
#    порожнеча без свідка (Miss Hobart) → ідея Воррена → сталевий дріт →
#    серійне «яйце» → флеш-лог дрона. Носій змінюється, задум той самий.
# ─────────────────────────────────────────────────────────────────────────────
def fig_blackbox_thread():
    W, H = 940, 500
    frags = [text(W / 2, 30, "Одна ідея крізь сімдесят років: змінюється носій, не задум",
                  size=13, color=MUTED)]

    # Горизонтальна вісь часу (нижче, щоб верхні картки не налазили на підзаголовок)
    ax0, ax1, ay = 60, 862, 190
    frags.append(line(ax0, ay, ax1, ay, color=INK, sw=2))
    frags.append(arrow(ax1 - 2, ay, ax1 + 10, ay))
    frags.append(text(ax1 + 6, ay - 12, "час", size=11, color=MUTED, italic=True))

    # П'ять віх: (частка по осі, рік, заголовок, суть-носій, колір).
    # up=True → картка над віссю, інакше під нею (щоб сусідні не налазили).
    steps = [
        (0.02, "1934",       "Miss Hobart зникла", "порожнеча:\nнема свідка",       POS),
        (0.27, "1954",       "записка Воррена",     "ідея: хай апарат\nсам пише",    NEG),
        (0.52, "кін. 1950-х", "Flight Memory",      "сталевий дріт\n0.05 мм, петля", FIELD),
        (0.73, "1958 →",     "«Red Egg»",           "серійний\nсамописець",          POS),
        (0.96, "нині",       "лог дрона",           "флеш-пам'ять\nATT · GPS · BAT", NEG),
    ]
    for i, (xf, yr, head, body, col) in enumerate(steps):
        x = ax0 + (ax1 - ax0 - 16) * xf
        up = (i % 2 == 0)
        frags.append(circle(x, ay, 6, fill=col, stroke=INK, sw=1.4))
        frags.append(text(x, ay + (24 if up else -14), yr, size=12, color=INK, bold=True))
        # картка з назвою й суттю
        cy = ay - 96 if up else ay + 96
        b, bw, bh = textbox(x, cy, head + "\n" + body, size=11, pad=9,
                            stroke=col, fill=FILL)
        frags.append(b)
        # тонка пунктирна ніжка від картки до точки на осі
        edge = cy + bh / 2 if up else cy - bh / 2
        near = ay - 9 if up else ay + 9
        frags.append(line(x, edge, x, near, color=MUTED, sw=1.0, dash="3 3"))

    # Підсумок
    frags.append(text(W / 2, H - 42,
                      "Носій міняється: сталевий дріт → магнітна стрічка → напівпровідникова пам'ять.",
                      size=12, color=INK, bold=True))
    frags.append(text(W / 2, H - 20,
                      "Задум незмінний: пиши безперервно, тримай останнє, переживи катастрофу.",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, 'blackbox-thread.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_two_logs()
    fig_self_describing()
    fig_vibe_spectrum()
    fig_record_slicing()
    fig_blackbox_thread()
    print("OK figs written to", IMG)
