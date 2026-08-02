# -*- coding: utf-8 -*-
"""Фігури до теми «noexcept: обіцянка й наслідки»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Пошук обробника впирається в межу noexcept ───────────────────────────
def fig_handler_search():
    W, H = 1000, 480
    f = []

    CX, CW = 300, 340

    f.append(fitbox(CX, 40, CW, 56, "main()\ntry { … } catch (...)", size=12))
    f.append(line(645, 68, 686, 68, color=MUTED, sw=1, dash="5 4"))
    f.append(fitbox(690, 40, 280, 56, "цей обробник не отримає нічого",
                    size=11, fill="#fdecea", stroke=POS, color=POS))

    f.append(fitbox(CX, 124, CW, 56, "process()", size=12))

    f.append(line(280, 190, 660, 190, color=POS, sw=1.5, dash="7 5"))
    f.append(text(470, 214, "далі пошук не йде", size=11, color=POS, bold=True))

    f.append(fitbox(CX, 224, CW, 56, "commit() noexcept", size=13,
                    fill="#fdecea", stroke=POS, bold=True))
    f.append(arrow(646, 252, 686, 252, color=POS))
    f.append(fitbox(690, 224, 280, 56, "std::terminate()", size=13,
                    fill="#fdecea", stroke=POS, bold=True))
    f.append(fitbox(690, 292, 280, 68,
                    "чи розкрутиться стек до цієї миті —\nвирішує реалізація",
                    size=11, color=MUTED))

    f.append(fitbox(CX, 308, CW, 56, "write_record()", size=12))
    f.append(fitbox(CX, 392, CW, 56, "throw std::runtime_error{…}",
                    size=12, fill="#fff7e6", stroke=POS))

    f.append(arrow(285, 400, 285, 254))
    f.append(mtext(140, 320, ["пошук обробника", "йде вгору стеком"],
                   size=12, color=MUTED))

    render(os.path.join(OUT, 'handler-search.svg'), W, H, *f,
           title="Межа noexcept зупиняє пошук обробника")


# ── 2. Чому переміщення без noexcept ламає точку відкату ────────────────────
def fig_rollback():
    W, H = 860, 545
    XS = [200, 300, 400, 500, 600]
    CWID, CHT = 90, 46

    def rowlabel(y, s):
        return text(112, y, s, size=12, color=MUTED)

    def cells(y, items):
        out = []
        for x, (txt, kind) in zip(XS, items):
            style = {
                "ok":   dict(fill="#e8f6ee", stroke=FIELD),
                "gone": dict(fill="#ffffff", stroke=MUTED, color=MUTED),
                "bad":  dict(fill="#fdecea", stroke=POS, color=POS),
                "none": dict(fill="#ffffff", stroke=MUTED, color=MUTED),
            }[kind]
            out.append(fitbox(x, y, CWID, CHT, txt, size=11, **style))
        return out

    f = []

    # Панель «переміщення»
    f.append(text(50, 42, "Переміщення, яке може кинути", size=14,
                  color=INK, anchor="start", bold=True))
    f.append(rowlabel(97, "старий буфер"))
    f += cells(70, [("порожньо", "gone"), ("порожньо", "gone"),
                    ("порожньо", "gone"), ("дані", "ok"), ("дані", "ok")])
    for x in XS[:3]:
        f.append(arrow(x + 45, 122, x + 45, 164))
    f.append(text(545, 150, "виняток", size=11, color=POS, bold=True))
    f.append(rowlabel(197, "новий буфер"))
    f += cells(170, [("дані", "ok"), ("дані", "ok"), ("дані", "ok"),
                     ("не збудовано", "bad"), ("порожньо", "none")])
    f.append(text(430, 248,
                  "джерела 0–2 вже випотрошені: повертати назад нема з чого,"
                  " а зворотне переміщення теж може кинути",
                  size=11, color=MUTED))

    f.append(line(40, 276, 820, 276, color=MUTED, sw=1, dash="6 5"))

    # Панель «копіювання»
    f.append(text(50, 318, "Копіювання", size=14, color=INK,
                  anchor="start", bold=True))
    f.append(rowlabel(373, "старий буфер"))
    f += cells(346, [("дані", "ok"), ("дані", "ok"), ("дані", "ok"),
                     ("дані", "ok"), ("дані", "ok")])
    for x in XS[:3]:
        f.append(arrow(x + 45, 398, x + 45, 440))
    f.append(text(545, 426, "виняток", size=11, color=POS, bold=True))
    f.append(rowlabel(473, "новий буфер"))
    f += cells(446, [("копія", "ok"), ("копія", "ok"), ("копія", "ok"),
                     ("не збудовано", "bad"), ("порожньо", "none")])
    f.append(text(430, 524,
                  "старий буфер цілий: досить знищити недобудований новий —"
                  " і контейнер такий самий, як був",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'rollback.svg'), W, H, *f,
           title="Чому переміщення, яке може кинути, позбавляє контейнер точки відкату")


# ── 3. Де noexcept з'являється без вашого слова ─────────────────────────────
def fig_implicit():
    W, H = 1000, 495
    C1, W1 = 40, 268
    C2, W2 = 320, 214
    C3, W3 = 546, 414

    f = []
    hdr = dict(size=12, fill="#eceff3", color=MUTED)
    f.append(fitbox(C1, 46, W1, 42, "функція", **hdr))
    f.append(fitbox(C2, 46, W2, 42, "обіцянка за умовчанням", **hdr))
    f.append(fitbox(C3, 46, W3, 42, "що її скасовує", **hdr))

    rows = [
        ("деструктор — і власноруч написаний,\nі згенерований",
         "noexcept(true)", "ok",
         "база або поле, чий деструктор оголошено noexcept(false)"),
        ("operator delete,\noperator delete[]",
         "noexcept(true)", "ok",
         "нічого: обіцянка безумовна"),
        ("згенеровані переміщення —\nконструктор і присвоєння",
         "виводиться з полів", "calc",
         "поле, чиє переміщення саме не має обіцянки"),
        ("згенеровані копіювання —\nконструктор і присвоєння",
         "виводиться з полів", "calc",
         "поле, що виділяє пам'ять при копіюванні (майже завжди)"),
        ("будь-яка інша функція",
         "noexcept(false)", "no",
         "нічого: тільки ви, написавши noexcept власноруч"),
    ]
    style = {
        "ok":   dict(fill="#e8f6ee", stroke=FIELD, bold=True),
        "calc": dict(fill="#fff7e6", stroke=MUTED),
        "no":   dict(fill="#fdecea", stroke=POS, color=POS, bold=True),
    }

    y = 100
    for name, promise, kind, breaker in rows:
        f.append(fitbox(C1, y, W1, 68, name, size=11, fill="#fbfcfd"))
        f.append(fitbox(C2, y, W2, 68, promise, size=12, **style[kind]))
        f.append(fitbox(C3, y, W3, 68, breaker, size=11))
        y += 76

    f.append(text(500, 478,
                  "жовте — обіцянка не задана наперед, а обчислена компілятором"
                  " з операцій усіх полів і баз",
                  size=11, color=MUTED))

    render(os.path.join(OUT, 'implicit.svg'), W, H, *f,
           title="Де noexcept з'являється без вашого слова")


# ── 4. Що робила динамічна специфікація throw(A, B) в час виконання ─────────
def fig_unexpected():
    W, H = 1040, 530
    f = []

    f.append(fitbox(330, 62, 380, 54,
                    "функція з throw(A, B) кидає виняток типу C",
                    size=13, fill="#fbfcfd"))
    f.append(arrow(520, 116, 520, 148))

    f.append(fitbox(330, 151, 380, 54, "C — це A або B?", size=13))

    f.append(text(258, 168, "так", size=12, color=FIELD, bold=True))
    f.append(arrow(330, 178, 200, 178))
    f.append(fitbox(20, 151, 180, 54, "летить далі", size=12,
                    fill="#e8f6ee", stroke=FIELD, color=FIELD, bold=True))

    f.append(text(534, 228, "ні", size=12, color=POS, bold=True))
    f.append(arrow(520, 205, 520, 239))
    f.append(fitbox(330, 242, 380, 54, "std::unexpected()", size=14,
                    fill="#fdecea", stroke=POS, color=POS, bold=True))
    f.append(arrow(520, 296, 520, 326))
    f.append(fitbox(310, 329, 420, 50,
                    "поточний unexpected_handler", size=13))

    f.append(line(520, 379, 520, 398))
    f.append(line(136, 398, 904, 398))

    outs = [
        (15,  "типовий handler:\nstd::terminate()", "bad"),
        (271, "handler кинув A або B:\nвиняток летить далі", "ok"),
        (527, "handler кинув інше,\nале в списку є bad_exception:\nдалі летить bad_exception", "mid"),
        (783, "handler кинув інше,\nа bad_exception у списку немає:\nstd::terminate()", "bad"),
    ]
    style = {
        "ok":  dict(fill="#e8f6ee", stroke=FIELD),
        "bad": dict(fill="#fdecea", stroke=POS),
        "mid": dict(fill="#fff7e6", stroke=MUTED),
    }
    for x, s, kind in outs:
        f.append(arrow(x + 121, 398, x + 121, 418))
        f.append(fitbox(x, 421, 242, 92, s, size=11, **style[kind]))

    render(os.path.join(OUT, 'unexpected.svg'), W, H, *f,
           title="Порушення throw(A, B) ловилося аж у час виконання")


# ── 5. Бюджет переїздів: скільки роботи додає перерозподіл ──────────────────
def _seq_double(n):
    """Послідовність (скільки переїхало, нова місткість) при подвоєнні."""
    out, cap = [], 0
    while cap < n:
        new = 1 if cap == 0 else 2 * cap
        out.append((cap, new))
        cap = new
    return out


def _seq_msvc(n):
    """Те саме за правилом MSVC STL: cap + cap/2, але не менше за потрібне."""
    out, cap = [], 0
    while cap < n:
        new = max(cap + cap // 2, cap + 1)
        out.append((cap, new))
        cap = new
    return out


def fig_relocation_budget():
    N = 8000
    dbl, msv = _seq_double(N), _seq_msvc(N)
    tot_d = sum(r for r, _ in dbl)
    tot_m = sum(r for r, _ in msv)

    W, H = 1000, 470
    X0, SPAN = 60, 880.0
    S = SPAN / float(max(tot_d, tot_m))
    BH, GAP = 36, 2
    TONE = ("#e3ebf9", "#eef2fb")

    f = []

    def title(y, s):
        return text(X0, y, s, size=13, color=INK, anchor="start", bold=True)

    def note(y, s):
        return text(X0, y, s, size=11, color=MUTED, anchor="start")

    def bar(y, sizes, top=2):
        """Смуга з блоків: top найбільших окремо, решта — одним блоком."""
        out, x = [], X0
        big = sorted(sizes, reverse=True)[:top]
        rest = sum(sizes) - sum(big)
        for i, s in enumerate(big):
            w = s * S
            out.append(fitbox(x, y, w - GAP, BH, str(s), size=12, pad=6,
                              fill=TONE[i % 2], stroke=MUTED, sw=1, rx=3))
            x += w
        if rest > 0:
            w = rest * S
            out.append(fitbox(x, y, w - GAP, BH, "решта %d" % rest, size=11,
                              pad=6, fill="#f3f4f6", stroke=MUTED, sw=1,
                              rx=3, color=MUTED))
        return out

    f.append(title(40, "базова робота: побудувати %d елементів "
                       "— однаково в обох варіантах" % N))
    f.append(fitbox(X0, 52, N * S - GAP, BH,
                    "%d побудов" % N, size=12, pad=6,
                    fill="#e8f6ee", stroke=FIELD, sw=1, rx=3))

    f.append(title(136, "переїзди при коефіцієнті 2 — libstdc++, libc++"))
    f += bar(148, [r for r, _ in dbl])
    f.append(note(206, "усього переїздів: %d, буферів: %d — приблизно ще один "
                       "такий самий обсяг роботи" % (tot_d, len(dbl))))

    f.append(title(254, "переїзди при коефіцієнті 1.5 — MSVC STL"))
    f += bar(266, [r for r, _ in msv])
    f.append(note(324, "усього переїздів: %d, буферів: %d — удвічі більше, "
                       "ніж при подвоєнні" % (tot_m, len(msv))))

    f.append(fitbox(X0, 352, SPAN, 92,
                    "переїздів ≈ N / (r − 1):   r = 2 → ≈ N,   r = 1.5 → ≈ 2·N\n"
                    "копіювання коштує стільки ж, скільки перша побудова, "
                    "тож увесь цикл довшає приблизно в 1 + 1/(r − 1) разів:\n"
                    "удвічі при подвоєнні, утричі при коефіцієнті 1.5",
                    size=13, pad=14, fill="#fbfcfd", stroke=MUTED, sw=1))

    render(os.path.join(OUT, 'relocation-budget.svg'), W, H, *f,
           title="Бюджет переїздів при послідовних push_back")


if __name__ == '__main__':
    fig_handler_search()
    fig_rollback()
    fig_implicit()
    fig_unexpected()
    fig_relocation_budget()
    print("ok")
