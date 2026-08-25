# -*- coding: utf-8 -*-
"""Фігури до теми «Переглядач логів: графіки й повідомлення з бортового файлу»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Самоопис: два різні формати зводяться до одного словника
# ─────────────────────────────────────────────────────────────────────────────
def fig_self_describing():
    W, H = 1000, 640
    f = []

    box_w, box_h, gap = 400, 56, 14
    lx, rx = 50, 550          # ліві краї колонок
    lcx, rcx = lx + box_w / 2, rx + box_w / 2

    f.append(text(lcx, 72, "ULog (.ulg) — PX4", size=16, bold=True))
    f.append(text(rcx, 72, "DataFlash (.bin) — ArduPilot", size=16, bold=True))

    left = [
        "магія «ULog», версія, час старту",
        "F — опис структури: назва й поля",
        "A — підписка: номер ↔ назва структури",
        "P, Q — параметри й типові значення",
        "D — дані: номер + байти за описом",
        "L — текст, O — позначка провалу запису",
    ]
    right = [
        "0xA3 0x95 — початок кожного пакета",
        "FMT — тип, довжина, ім'я структури",
        "…і рядок формату: B H h f L M + підписи",
        "PARM — параметри, MSG — текст",
        "пакет даних: 0xA3 0x95, тип, байти",
        "провал запису нічим не позначено",
    ]

    y = 92
    for a, b in zip(left, right):
        f.append(fitbox(lx, y, box_w, box_h, a, size=14))
        f.append(fitbox(rx, y, box_w, box_h, b, size=14))
        y += box_h + gap
    col_bottom = y - gap

    # спільний словник
    sb, sw_, sh = textbox(W / 2, 590,
                          "словник застосунку: «структура.поле» → ряд точок (секунди, значення)",
                          size=15, bold=True, fill="#eaf4ee", stroke=FIELD, sw=2)
    f.append(sb)
    top = 590 - sh / 2
    f.append(arrow(lcx, col_bottom + 6, W / 2 - 120, top - 8))
    f.append(arrow(rcx, col_bottom + 6, W / 2 + 120, top - 8))

    render(os.path.join(IMG, 'self-describing.svg'), W, H, *f,
           title="Два формати, що описують себе самі, і спільний результат розбору")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Прорідження: кожен n-й проти огинаючої «мінімум-максимум»
# ─────────────────────────────────────────────────────────────────────────────
def _series(n=900):
    """Детермінований ряд: повільна хвиля, дрібне тремтіння і один вузький сплеск."""
    pts = []
    seed = 12345
    for i in range(n):
        seed = (1103515245 * seed + 12345) % 2147483648
        jitter = (seed / 2147483648.0 - 0.5) * 0.16
        t = i / (n - 1.0)
        v = math.sin(t * 6.4) * 0.55 + jitter
        if 0.615 < t < 0.632:                 # вузький сплеск на кілька відліків
            v += 1.35
        pts.append((t, v))
    return pts


def _panel(x, y, w, h, pts, cols=None, mark_cols=False):
    """Панель із рядом; повертає SVG-фрагмент."""
    out = rect(x, y, w, h, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4)
    if mark_cols and cols:
        step = w / float(cols)
        for c in range(1, cols):
            out += line(x + c * step, y + 2, x + c * step, y + h - 2,
                        color="#dfe3e8", sw=1.0)
    lo, hi = -0.95, 2.05
    def sx(t): return x + 6 + t * (w - 12)
    def sy(v): return y + h - 6 - (v - lo) / (hi - lo) * (h - 12)
    d = " ".join("%.1f,%.1f" % (sx(t), sy(v)) for t, v in pts)
    out += ('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>'
            % (d, NEG))
    return out


def fig_decimation():
    pts = _series()
    cols = 30
    W, H = 1000, 700
    px, pw, ph = 60, 880, 132
    f = []

    # (a) усі відліки
    y1 = 86
    f.append(text(px, y1 - 12, "усі 900 відліків — так виглядає ряд насправді",
                  size=15, anchor="start", bold=True))
    f.append(_panel(px, y1, pw, ph, pts))

    # (b) кожен n-й
    y2 = y1 + ph + 76
    step = len(pts) // cols
    thin = [pts[i] for i in range(0, len(pts), step)]
    f.append(text(px, y2 - 12, "кожен 30-й відлік — сплеск зник безслідно",
                  size=15, anchor="start", bold=True, color=POS))
    f.append(_panel(px, y2, pw, ph, thin, cols, mark_cols=True))

    # (c) мінімум і максимум у кожній колонці
    y3 = y2 + ph + 76
    env = []
    per = len(pts) / float(cols)
    for c in range(cols):
        chunk = pts[int(c * per):int((c + 1) * per)]
        if not chunk:
            continue
        first, last = chunk[0], chunk[-1]
        mn = min(chunk, key=lambda p: p[1])
        mx = max(chunk, key=lambda p: p[1])
        picked = sorted({first, mn, mx, last}, key=lambda p: p[0])
        env.extend(picked)
    f.append(text(px, y3 - 12,
                  "перший, найменший, найбільший, останній у колонці — сплеск на місці",
                  size=15, anchor="start", bold=True, color=FIELD))
    f.append(_panel(px, y3, pw, ph, env, cols, mark_cols=True))

    f.append(text(px, y3 + ph + 34,
                  "вертикальні лінії — межі піксельних колонок графіка",
                  size=13, anchor="start", color=MUTED))

    render(os.path.join(IMG, 'decimation.svg'), W, H, *f,
           title="Чому проріджування бере не кожен n-й відлік, а огинаючу")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Дві дороги: бортовий файл проти файлу телеметрії
# ─────────────────────────────────────────────────────────────────────────────
def fig_two_roads():
    W, H = 1000, 560
    box_w, box_h, gap = 400, 66, 34
    lx, rx = 50, 550
    lcx, rcx = lx + box_w / 2, rx + box_w / 2
    f = []

    left = [
        ".ulg або .bin — бортовий файл",
        "розбір у робочому потоці",
        "словник полів у пам'яті станції",
        "графік, карта, параметри, повідомлення",
    ]
    right = [
        ".tlog — файл телеметрії станції",
        "канал відтворення замість радіо",
        "звичайний шлях: розбір → Vehicle → факти",
        "інспектор MAVLink малює ті самі поля",
    ]

    y = 78
    for i, (a, b) in enumerate(zip(left, right)):
        f.append(fitbox(lx, y, box_w, box_h, a, size=15,
                        fill="#eef2f9" if i == 0 else FILL))
        f.append(fitbox(rx, y, box_w, box_h, b, size=15,
                        fill="#eef2f9" if i == 0 else FILL))
        if i < 3:
            f.append(arrow(lcx, y + box_h + 4, lcx, y + box_h + gap - 4))
            f.append(arrow(rcx, y + box_h + 4, rcx, y + box_h + gap - 4))
        y += box_h + gap

    nb, nw, nh = textbox(W / 2, 508,
                         "дороги різні, бо .tlog — це кадри протоколу,\n"
                         "які застосунок уже вміє тлумачити без окремого розбирача",
                         size=15, fill="#eaf4ee", stroke=FIELD, sw=2)
    f.append(nb)

    render(os.path.join(IMG, 'two-roads.svg'), W, H, *f,
           title="Два види файлів — дві різні дороги до графіка")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Де записана довжина запису — і що з того випливає (до вставки api-)
# ─────────────────────────────────────────────────────────────────────────────
def fig_record_length():
    W, H = 1060, 560
    f = []
    HL = dict(fill="#eaf7ef", stroke=FIELD, sw=2.0)

    # ── ULog ────────────────────────────────────────────────────────────────
    f.append(text(40, 62, "ULog — .ulg", size=16, bold=True, anchor="start"))

    f.append(fitbox(40, 76, 250, 56, "магія — 7 Б\n55 4C 6F 67 01 12 35", size=13))
    f.append(fitbox(290, 76, 110, 56, "версія\n1 Б", size=13))
    f.append(fitbox(400, 76, 190, 56, "час старту\nuint64 — 8 Б", size=13))
    f.append(mtext(610, 98, ["16 байтів — рівно один раз",
                             "на початку файлу"], size=13, color=MUTED, anchor="start"))

    f.append(fitbox(40, 152, 170, 56, "msg_size\nuint16 — 2 Б", size=13, **HL))
    f.append(fitbox(210, 152, 150, 56, "msg_type\n1 літера", size=13))
    f.append(fitbox(360, 152, 230, 56, "тіло — msg_size Б", size=13))
    f.append(mtext(610, 174, ["довжина попереду тіла:",
                              "незнайомий тип — пропустити"], size=13, color=MUTED, anchor="start"))

    # ── DataFlash ───────────────────────────────────────────────────────────
    f.append(text(40, 254, "DataFlash — .bin / .log", size=16, bold=True, anchor="start"))

    f.append(fitbox(40, 268, 70, 56, "A3", size=13))
    f.append(fitbox(110, 268, 70, 56, "95", size=13))
    f.append(fitbox(180, 268, 150, 56, "msgid = 128\n(FMT)", size=13))
    f.append(fitbox(330, 268, 90, 56, "type\n1 Б", size=13))
    f.append(fitbox(420, 268, 110, 56, "length\n1 Б", size=13, **HL))
    f.append(fitbox(530, 268, 110, 56, "name[4]", size=13))
    f.append(fitbox(640, 268, 130, 56, "format[16]", size=13))
    f.append(fitbox(770, 268, 130, 56, "labels[64]", size=13))
    f.append(text(470, 344, "оголошення: 3 + 1 + 1 + 4 + 16 + 64 = 89 байтів",
                  size=13, color=MUTED))

    f.append(fitbox(40, 366, 70, 56, "A3", size=13))
    f.append(fitbox(110, 366, 70, 56, "95", size=13))
    f.append(fitbox(180, 366, 150, 56, "msgid\n1 Б", size=13))
    f.append(fitbox(330, 366, 340, 56, "поля пакета — розкладку дає FMT", size=13))
    f.append(mtext(690, 388, ["довжини в пакеті немає:",
                              "її знає лише таблиця FMT"], size=13, color=MUTED, anchor="start"))

    nb, nw, nh = textbox(W / 2, 500,
                         "ULog: довжина в кожному записі плюс маркер синхронізації S\n"
                         "DataFlash: лише початок пакета A3 95 — після невідомого типу шукають наступну пару",
                         size=14, fill="#eaf4ee", stroke=FIELD, sw=2)
    f.append(nb)

    render(os.path.join(IMG, 'record-length.svg'), W, H, *f,
           title="Де записана довжина запису — і що з того випливає")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Одне ім'я ATT.Roll — дві різні розкладки у двох версіях прошивки
# ─────────────────────────────────────────────────────────────────────────────
def fig_fmt_offsets():
    W, H = 1000, 560
    PW = 440
    f = []

    panels = [
        (40, "ArduPilot Copter-3.6", "FMT: ATT · довжина 27 · формат QccccCCCC",
         [("TimeUS",   "Q", "uint64",         3),
          ("DesRoll",  "c", "int16 × 0.01",  11),
          ("Roll",     "c", "int16 × 0.01",  13),
          ("DesPitch", "c", "int16 × 0.01",  15),
          ("Pitch",    "c", "int16 × 0.01",  17),
          ("DesYaw",   "C", "uint16 × 0.01", 19),
          ("Yaw",      "C", "uint16 × 0.01", 21),
          ("ErrRP",    "C", "uint16 × 0.01", 23),
          ("ErrYaw",   "C", "uint16 × 0.01", 25)],
         "3 + 8 + 8×2 = 27"),
        (520, "ArduPilot, теперішня гілка", "FMT: ATT · довжина 36 · формат QffffffB",
         [("TimeUS",   "Q", "uint64",  3),
          ("DesRoll",  "f", "float",  11),
          ("Roll",     "f", "float",  15),
          ("DesPitch", "f", "float",  19),
          ("Pitch",    "f", "float",  23),
          ("DesYaw",   "f", "float",  27),
          ("Yaw",      "f", "float",  31),
          ("AEKF",     "B", "uint8",  35)],
         "3 + 8 + 6×4 + 1 = 36"),
    ]

    for px, title, sub, rows, total in panels:
        f.append(rect(px, 40, PW, 400, fill=BG, stroke=MUTED, sw=1.2, rx=6))
        f.append(text(px + PW / 2, 66, title, size=15, bold=True))
        f.append(text(px + PW / 2, 88, sub, size=12, color=MUTED))
        f.append(line(px + 12, 102, px + PW - 12, 102, color="#dfe3e8", sw=1))
        f.append(text(px + 16, 122, "поле", size=12, anchor="start", bold=True, color=MUTED))
        f.append(text(px + 150, 122, "літера", size=12, bold=True, color=MUTED))
        f.append(text(px + 190, 122, "тип у файлі", size=12, anchor="start", bold=True, color=MUTED))
        f.append(text(px + PW - 16, 122, "зміщення", size=12, anchor="end", bold=True, color=MUTED))
        f.append(line(px + 12, 132, px + PW - 12, 132, color="#dfe3e8", sw=1))

        y = 154
        for name, letter, typ, off in rows:
            hot = (name == "Roll")
            if hot:
                f.append(rect(px + 10, y - 16, PW - 20, 26, fill="#eaf4ee",
                              stroke=FIELD, sw=1.4, rx=4))
            col = FIELD if hot else INK
            f.append(text(px + 16, y, name, size=13, anchor="start", color=col, bold=hot))
            f.append(text(px + 150, y, letter, size=13, color=col, bold=True))
            f.append(text(px + 190, y, typ, size=13, anchor="start", color=col))
            f.append(text(px + PW - 16, y, str(off), size=13, anchor="end", color=col, bold=hot))
            y += 30

        f.append(line(px + 12, 410, px + PW - 12, 410, color="#dfe3e8", sw=1))
        f.append(text(px + PW - 16, 429, total, size=13, anchor="end", color=MUTED))

    nb, nw, nh = textbox(W / 2, 500,
                         "те саме ім'я «ATT.Roll» — інша літера, інше зміщення, інший множник;\n"
                         "зашита в програму розкладка мовчки дає тут безглузде число",
                         size=14, fill="#eaf4ee", stroke=FIELD, sw=2)
    f.append(nb)

    render(os.path.join(IMG, 'fmt-offsets.svg'), W, H, *f,
           title="Розкладка ATT у двох версіях прошивки: одне ім'я, різні зміщення")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Хід файлом: стрибок на оголошену довжину проти побайтового пошуку
# ─────────────────────────────────────────────────────────────────────────────
def fig_walk_resync():
    W, H = 1000, 470
    f = []

    f.append(text(W / 2, 48, "Довжину пакета дає оголошення, а не самі дані",
                  size=16, bold=True))

    x0, ytop, sh = 60, 150, 56
    segs = [
        ("FMT · 89 Б", 170, FILL),
        ("ATT · 36 Б", 140, FILL),
        ("ATT · 36 Б", 140, FILL),
        ("тип без оголошення", 220, "#fdecea"),
        ("ATT · 36 Б", 140, FILL),
        ("…", 70, FILL),
    ]

    f.append(text(285, 112, "стрибок на оголошену довжину", size=13, color=NEG))
    f.append(text(620, 112, "зсув на один байт", size=13, color=POS))

    x = x0
    for i, (label, w, fill) in enumerate(segs):
        f.append(fitbox(x, ytop, w, sh, label, size=13, fill=fill))
        if i == 3:
            xx = x + 8
            while xx + 20 <= x + w - 8:
                f.append(arrow(xx, 134, xx + 14, 134, color=POS, sw=1.4))
                xx += 20
        elif label != "…":
            f.append(arrow(x + 8, 134, x + w - 8, 134, color=NEG, sw=1.8))
        x += w

    for i, lbl in enumerate(("0xA3", "0x95", "тип")):
        f.append(fitbox(60 + i * 70, 250, 70, 36, lbl, size=13, fill="#eef2f9"))
    f.append(mtext(300, 262,
                   ["вікно з трьох байтів — усе, що читач тримає в пам'яті:",
                    "не збіглося з 0xA3 0x95 плюс оголошений тип — викидаємо",
                    "перший байт, дочитуємо один новий і пробуємо знову"],
                   size=13, anchor="start"))

    nb, nw, nh = textbox(W / 2, 400,
                         "0xA3 0x95 випадково трапляється й усередині даних — тоді після\n"
                         "несправжнього пакета сигнатура не збіжиться, і читач знову піде побайтово",
                         size=13, fill="#fdecea", stroke=POS, sw=2)
    f.append(nb)

    render(os.path.join(IMG, 'walk-resync.svg'), W, H, *f,
           title="Хід файлом DataFlash: коли можна стрибати, а коли доводиться шукати")


if __name__ == '__main__':
    fig_self_describing()
    fig_decimation()
    fig_two_roads()
    fig_record_length()
    fig_fmt_offsets()
    fig_walk_resync()
    print("ok")
