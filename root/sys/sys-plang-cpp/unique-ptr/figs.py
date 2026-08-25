# -*- coding: utf-8 -*-
"""Фігури до теми «unique_ptr: одноосібне володіння»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HEAD = "#eceff3"
OK   = "#e8f6ee"
WARN = "#fff7e6"
HOT  = "#fdecea"


# ── 1. Форма параметра ↔ що вона каже про володіння ─────────────────────────
def fig_ownership_signature():
    W, H = 1000, 470
    f = []

    cols = [(50, 300, "форма в сигнатурі"),
            (370, 340, "що це означає"),
            (730, 220, "хто звільнить")]
    for x, w, name in cols:
        f.append(fitbox(x, 56, w, 44, name, size=13, fill=HEAD, color=MUTED, bold=True))

    rows = [
        (118, "unique_ptr<T> p", "забираю володіння собі;\nвикликач мусить написати std::move",
         "ця функція", OK),
        (196, "unique_ptr<T>& p", "можу підмінити те,\nчим володіє викликач",
         "викликач", WARN),
        (274, "T* p   або   T& p", "лише дивлюся, поки триває виклик;\nзвідки об'єкт — байдуже",
         "викликач", FILL),
        (352, "unique_ptr<T>  ← повернення", "віддаю готове володіння;\nзабути про нього не вийде",
         "викликач", OK),
    ]
    for y, sig, meaning, who, tint in rows:
        f.append(fitbox(50, y, 300, 66, sig, size=13, fill=BG, bold=True))
        f.append(fitbox(370, y, 340, 66, meaning, size=12, fill=tint))
        f.append(fitbox(730, y, 220, 66, who, size=13, fill=FILL, color=MUTED))

    f.append(text(500, 446,
                  "тип параметра відповідає на питання про володіння без жодного коментаря",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'ownership-signature.svg'), W, H, *f,
           title="Що форма параметра каже про володіння")


# ── 2. get / release / reset: поле всередині ↔ об'єкт у купі ────────────────
def fig_handle_operations():
    W, H = 1000, 580
    f = []

    cols = [(50, 260, "операція"),
            (330, 330, "поле-вказівник усередині"),
            (690, 260, "об'єкт у купі")]
    for x, w, name in cols:
        f.append(fitbox(x, 56, w, 44, name, size=13, fill=HEAD, color=MUTED, bold=True))

    rows = [
        (118, "get()", "лишається без змін", "живий, власник той самий", FILL),
        (186, "release()", "стає нульовим", "живий, але без власника", WARN),
        (254, "reset(p)", "спершу дістає p", "старий гине ПІСЛЯ заміни поля", OK),
        (322, "reset()", "стає нульовим", "гине негайно", OK),
        (390, "переміщення", "у джерела — нуль,\nу приймача — стара адреса", "живий, власник новий", OK),
        (458, "~unique_ptr()", "об'єкт власника зникає", "гине, якщо поле не нульове", OK),
    ]
    for y, op, field, obj, tint in rows:
        f.append(fitbox(50, y, 260, 60, op, size=13, fill=BG, bold=True))
        f.append(fitbox(330, y, 330, 60, field, size=12, fill=FILL))
        f.append(fitbox(690, y, 260, 60, obj, size=12, fill=tint))

    f.append(text(500, 552,
                  "лише release розриває зв'язок між адресою і відповідальністю за неї",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'handle-operations.svg'), W, H, *f,
           title="Що роблять get, release і reset")


# ── 3. Як параметр іде через межу функції: регістр проти комірки стека ──────
def fig_abi_passing():
    W, H = 960, 420
    f = []

    f.append(text(60, 44, "T*  —  тривіальний тип, іде в регістрі",
                  size=14, color=INK, anchor="start", bold=True))
    f.append(fitbox(60, 62, 220, 66, "викликач\nмає адресу", size=13))
    f.append(text(454, 90, "один регістр", size=11, color=MUTED))
    f.append(arrow(288, 103, 620, 103, color=FIELD))
    f.append(fitbox(630, 62, 250, 66, "викликана функція\nбере значення", size=13,
                    fill=OK, stroke=FIELD))

    f.append(line(50, 176, 910, 176, color=MUTED, sw=1, dash="6 5"))

    f.append(text(60, 226, "unique_ptr<T>  —  нетривіальний, іде через пам'ять",
                  size=14, color=INK, anchor="start", bold=True))
    f.append(fitbox(60, 244, 210, 66, "викликач\nбудує тимчасовий", size=13))
    f.append(arrow(278, 285, 340, 285, color=POS))
    f.append(fitbox(348, 244, 210, 66, "комірка в кадрі\nстека викликача", size=13,
                    fill=HOT, stroke=POS))
    f.append(arrow(566, 285, 628, 285, color=POS))
    f.append(fitbox(636, 244, 244, 66, "викликана функція\nдістає адресу комірки", size=13,
                    fill=HOT, stroke=POS))

    f.append(text(470, 348, "зайвий запис у пам'ять і зайве читання на кожне передавання",
                  size=11, color=MUTED))
    f.append(text(470, 372, "знищити параметр зобов'язана викликана функція",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'abi-passing.svg'), W, H, *f,
           title="Чому unique_ptr не передається в регістрі")


# ── 4. Дозорне значення C-API проти нуля власника ──────────────────────────
def fig_sentinel_mapping():
    W, H = 1020, 420
    f = []

    cols = [(50, 280, "що повернув open()"),
            (350, 320, "наївне: дескриптор у void*"),
            (690, 280, "власний тип FdHandle")]
    for x, w, name in cols:
        f.append(fitbox(x, 56, w, 44, name, size=13, fill=HEAD, color=MUTED, bold=True))

    rows = [
        (118, "-1  —  відкрити не вдалося",
         "не нульова адреса:\nвласник вважає, що володіє", HOT,
         "дорівнює nullptr:\nвласник порожній", OK),
        (196, "0  —  робочий дескриптор\n(коли stdin закрито)",
         "нульова адреса:\nвидалювача не покличуть", HOT,
         "не nullptr:\nвласник володіє, close(0)", OK),
        (274, "3  —  робочий дескриптор",
         "не нульова адреса:\nclose(3) на виході", OK,
         "не nullptr:\nclose(3) на виході", OK),
    ]
    for y, val, naive, ntint, own, otint in rows:
        f.append(fitbox(50, y, 280, 66, val, size=13, fill=BG, bold=True))
        f.append(fitbox(350, y, 320, 66, naive, size=12, fill=ntint))
        f.append(fitbox(690, y, 280, 66, own, size=12, fill=otint))

    f.append(text(510, 372,
                  "порожній стан власника мусить збігатися з дозорним значенням API, "
                  "а не з нулем машини",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'sentinel-mapping.svg'), W, H, *f,
           title="Дозорне значення C-API проти порожнього стану власника")


if __name__ == '__main__':
    fig_ownership_signature()
    fig_handle_operations()
    fig_abi_passing()
    fig_sentinel_mapping()
    print("ok")
