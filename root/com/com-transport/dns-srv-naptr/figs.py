# -*- coding: utf-8 -*-
"""Фігури до теми «Записи DNS SRV і NAPTR»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"
COOL = "#eef8f1"


def box(cx, cy, s, size=12, fill=FILL, bold=False):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, bold=bold)
    return body, w / 2.0, h / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# 1. Ланцюг пошуку: NAPTR → SRV → A/AAAA. Кожен крок додає рівно одну
#    відсутню річ, і лише після трьох клієнт має чим відкрити з'єднання.
# ─────────────────────────────────────────────────────────────────────────────
def fig_lookup_chain():
    W, H = 1040, 660
    f = []

    f.append(text(40, 40, "Клієнт тримає лише ім'я: sip:olena@example.com",
                  size=14, color=INK, anchor="start", bold=True))

    steps = [
        (60, SOFT, "Крок 1 — який транспорт пропонує домен",
         "запит NAPTR\nexample.com",
         "«є SIPS поверх TCP,\nпитай далі ім'я\n_sips._tcp.example.com»",
         "з'явився транспорт"),
        (250, WARM, "Крок 2 — який вузол і на якому порту",
         "запит SRV\n_sips._tcp.example.com",
         "«пріоритет 10, вага 60,\nпорт 5061,\nвузол sip1.example.com»",
         "з'явилися вузол і порт"),
        (440, COOL, "Крок 3 — яка в цього вузла адреса",
         "запит A / AAAA\nsip1.example.com",
         "«198.51.100.9»\n«2001:db8::9»",
         "з'явилася адреса"),
    ]

    for py, tone, head, q, a, gain in steps:
        f.append(rect(30, py, 980, 170, fill=tone, stroke="#cbd5e1", sw=1.2, rx=10))
        f.append(text(52, py + 28, head, size=13, color=MUTED, anchor="start", bold=True))
        qb, qw, qh = box(230, py + 105, q, size=12, fill="#ffffff")
        ab, aw, ah = box(730, py + 105, a, size=12, fill="#ffffff")
        f += [qb, ab]
        f.append(arrow(230 + qw + 10, py + 105, 730 - aw - 10, py + 105))
        f.append(text(480, py + 88, gain, size=11, color=MUTED))

    f.append(rect(30, 630 - 0, 0, 0, fill="none", stroke="none", sw=0))
    band = "Аж тепер є з чим стукати: TCP на 198.51.100.9:5061, TLS — і сертифікат мусить називати example.com"
    f.append(fitbox(30, 626, 980, 56, band, size=13, bold=True,
                    fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(OUT, 'lookup-chain.svg'), W, H + 30, *f,
           title="Три запити DNS перед першим пакетом протоколу")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Пріоритет упорядковує, вага розігрує: наростальна сума на числовій осі.
# ─────────────────────────────────────────────────────────────────────────────
def fig_weight_draw():
    W, H = 1040, 560
    f = []

    f.append(text(40, 40, "Пріоритет задає порядок спроб; вага ділить навантаження всередині одного пріоритету",
                  size=13, color=INK, anchor="start", bold=True))

    f.append(rect(30, 60, 980, 130, fill=SOFT, stroke="#c8d6ea", sw=1.2, rx=10))
    f.append(text(52, 88, "пріоритет 10 — з нього починають завжди",
                  size=12, color=MUTED, anchor="start", bold=True))
    for cx, s in ((250, "sip1.example.com\nвага 60"),
                  (520, "sip2.example.com\nвага 30"),
                  (790, "sip3.example.com\nвага 10")):
        b, _, _ = box(cx, 145, s, size=12, fill="#ffffff")
        f.append(b)

    f.append(rect(30, 206, 980, 104, fill=WARM, stroke="#e6d3b3", sw=1.2, rx=10))
    f.append(text(52, 234, "пріоритет 20 — тільки якщо жоден із верхніх не відповів",
                  size=12, color=MUTED, anchor="start", bold=True))
    b, _, _ = box(250, 278, "backup.example.net\nвага 100", size=12, fill="#ffffff")
    f.append(b)

    f.append(text(40, 356, "Жереб: рівномірне ціле r з проміжку [0 … 100], сума ваг = 100",
                  size=13, color=INK, anchor="start", bold=True))

    x0, unit = 130, 7.8
    segs = ((0, 60, "sip1", "0 … 60", "#dbeafe"),
            (60, 90, "sip2", "61 … 90", "#fde8d7"),
            (90, 100, "sip3", "91 … 100", "#e2f4e8"))
    for lo, hi, name, rng, tone in segs:
        f.append(fitbox(x0 + lo * unit, 430, (hi - lo) * unit, 52,
                        name + "\n" + rng, size=12, fill=tone, stroke="#94a3b8"))

    for r, lbl in ((47, "r = 47"), (88, "r = 88"), (96, "r = 96")):
        mx = x0 + r * unit
        f.append(text(mx, 396, lbl, size=12, color=POS, bold=True))
        f.append(arrow(mx, 404, mx, 426, color=POS, sw=1.6))

    f.append(text(40, 516, "Частка кожного вузла = його вага ÷ сума ваг: 60 %, 30 %, 10 %",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'weight-draw.svg'), W, H, *f,
           title="Вибір цілі SRV за наростальною сумою ваг")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Одна й та сама ідея, зроблена тричі: MX → SRV → HTTPS/SVCB.
# ─────────────────────────────────────────────────────────────────────────────
def fig_record_arc():
    W, H = 1060, 470
    f = []

    f.append(text(40, 40, "Одне питання «хто робить це для домену» — три покоління відповіді",
                  size=14, color=INK, anchor="start", bold=True))

    lx, lw = 30, 170
    cols = ((215, "MX · 1986", SOFT),
            (500, "SRV · 2000", WARM),
            (785, "HTTPS і SVCB · 2023", COOL))
    cw = 260

    for cx, head, tone in cols:
        f.append(fitbox(cx, 62, cw, 46, head, size=13, bold=True, fill=tone, stroke="#94a3b8"))

    rows = (
        (124, 78, "що питаємо",
         "ім'я домену,\nтип MX",
         "_служба._транспорт.домен,\nтип SRV",
         "ім'я домену,\nтип HTTPS"),
        (214, 108, "що приходить",
         "пріоритет\nта ім'я поштового вузла",
         "пріоритет, вага,\nпорт,\nім'я вузла",
         "пріоритет, ім'я вузла,\nпорт, список ALPN,\nпідказки адрес, ключ ECH"),
        (334, 92, "чим обмежене",
         "працює для однієї\nєдиної служби",
         "транспорт треба знати\nнаперед або питати NAPTR:\nдо трьох запитів поспіль",
         "потрібна підтримка\nв клієнті та резолвері"),
    )

    for ry, rh, label, c1, c2, c3 in rows:
        f.append(fitbox(lx, ry, lw, rh, label, size=12, bold=True,
                        fill="#ffffff", stroke="#cbd5e1"))
        for (cx, _, _), cell in zip(cols, (c1, c2, c3)):
            f.append(fitbox(cx, ry, cw, rh, cell, size=11, fill="#ffffff", stroke="#cbd5e1"))

    render(os.path.join(OUT, 'record-arc.svg'), W, H, *f,
           title="MX, SRV і SVCB: що саме повертає кожне покоління записів")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Жеребкування повторюють, доки група не спорожніє: на виході не одна ціль,
#    а весь порядок обходу. Суми щоразу рахують наново.
# ─────────────────────────────────────────────────────────────────────────────
def fig_two_draws():
    W, H = 1040, 660
    f = []

    f.append(text(40, 38,
                  "Жереб не вибирає одну ціль — він розкладає всю групу пріоритету в порядок обходу",
                  size=14, color=INK, anchor="start", bold=True))

    rounds = [
        (60, SOFT, "Тур 1 — у грі всі три записи",
         [("sip1\nвага 60\nсума 60", "#dbeafe"),
          ("sip2\nвага 30\nсума 90", "#fde8d7"),
          ("sip3\nвага 10\nсума 100", "#e2f4e8")],
         "r = 88 з [0 … 100]\nперша сума ≥ 88 — це 90\nвибрано sip2"),
        (230, WARM, "Тур 2 — sip2 викинуто, суми пораховані наново",
         [("sip1\nвага 60\nсума 60", "#dbeafe"),
          ("sip3\nвага 10\nсума 70", "#e2f4e8")],
         "r = 64 з [0 … 70]\nперша сума ≥ 64 — це 70\nвибрано sip3"),
        (400, COOL, "Тур 3 — лишився один запис",
         [("sip1\nвага 60\nсума 60", "#dbeafe")],
         "жеребкувати нема з чого\nвибрано sip1"),
    ]

    for py, tone, head, cells, verdict in rounds:
        f.append(rect(30, py, 980, 150, fill=tone, stroke="#cbd5e1", sw=1.2, rx=10))
        f.append(text(52, py + 26, head, size=12, color=MUTED, anchor="start", bold=True))
        cx = 60
        for s, cell_tone in cells:
            f.append(fitbox(cx, py + 44, 180, 92, s, size=12, fill=cell_tone, stroke="#94a3b8"))
            cx += 200
        f.append(fitbox(660, py + 44, 320, 92, verdict, size=12, fill="#ffffff", stroke="#94a3b8"))

    f.append(fitbox(30, 580, 980, 56,
                    "Порядок обходу: sip2 → sip3 → sip1 — найважчий вузол цього разу останній",
                    size=13, bold=True, fill="#ffffff", stroke="#94a3b8"))

    render(os.path.join(OUT, 'two-draws.svg'), W, H, *f,
           title="Тури жеребкування RFC 2782 дають весь порядок обходу")


# ─────────────────────────────────────────────────────────────────────────────
# Розкладка RDATA обох записів: де фіксовані 16-бітні числа, де рядки
# з байтом довжини, а де ім'я домену. Для довідки api-srv-naptr-records.
# ─────────────────────────────────────────────────────────────────────────────
def fig_rdata_layout():
    W, H = 1060, 440
    f = []

    f.append(text(50, 40, "RDATA на дроті: з чого складається кожен запис",
                  size=15, color=INK, anchor="start", bold=True))

    x0, hh = 50, 76

    def ribbon(y, cells):
        x = x0
        for name, sub, w, fill in cells:
            f.append(rect(x, y, w, hh, fill=fill, stroke="#94a3b8", sw=1.5))
            f.append(text(x + w / 2, y + 27, name, size=13, color=INK, bold=True))
            f.append(mtext(x + w / 2, y + 47, sub.split("\n"), size=11, color=MUTED))
            x += w

    # SRV ---------------------------------------------------------------------
    f.append(text(50, 90, "SRV — тип 33", size=13, color=INK, anchor="start", bold=True))
    ribbon(106, (
        ("PRIORITY", "2 байти\n0–65535", 150, SOFT),
        ("WEIGHT",   "2 байти\n0–65535", 150, SOFT),
        ("PORT",     "2 байти\n0–65535", 150, SOFT),
        ("TARGET",   "ім'я домену, без компресії\nканонічне ім'я або «.»", 510, COOL),
    ))
    f.append(text(50, 212, "Три числа фіксованої довжини, далі — ім'я вузла, а не адреса.",
                  size=11, color=MUTED, anchor="start"))

    # NAPTR -------------------------------------------------------------------
    f.append(text(50, 264, "NAPTR — тип 35", size=13, color=INK, anchor="start", bold=True))
    ribbon(280, (
        ("ORDER",       "2 байти\n0–65535",    115, SOFT),
        ("PREFERENCE",  "2 байти\n0–65535",    130, SOFT),
        ("FLAGS",       "рядок\n1 + ≤255 Б",   130, WARM),
        ("SERVICES",    "рядок\n1 + ≤255 Б",   140, WARM),
        ("REGEXP",      "рядок\n1 + ≤255 Б",   130, WARM),
        ("REPLACEMENT", "ім'я домену\nабо «.»", 315, COOL),
    ))
    f.append(text(50, 386, "Три поля посередині — рядки: перший байт задає довжину, звідси межа 255.",
                  size=11, color=MUTED, anchor="start"))
    f.append(text(50, 410, "Останні два взаємовиключні: заповнене або REGEXP, або REPLACEMENT.",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'rdata-layout.svg'), W, H, *f,
           title="Розкладка RDATA записів SRV і NAPTR")


if __name__ == '__main__':
    fig_lookup_chain()
    fig_weight_draw()
    fig_record_arc()
    fig_two_draws()
    fig_rdata_layout()
    print("ok")
