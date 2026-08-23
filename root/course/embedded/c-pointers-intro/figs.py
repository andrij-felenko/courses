# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

VAL  = NEG      # синій — значення/дані
ADDR = FIELD    # зелений — адреса/покажчик
WARN = POS      # червоний — проблема/копія


def cell(x, y, w, name, val, vcolor=VAL, addr=None, h=46):
    """Комірка пам'яті: назва зверху, значення всередині, адреса під низом (опц.)."""
    p = [rect(x, y, w, h, fill="#fbfcfd", stroke=INK, sw=1.6)]
    p.append(text(x + w/2, y - 8, name, size=13, color=INK, bold=True))
    p.append(text(x + w/2, y + h/2 + 6, val, size=14, color=vcolor, bold=True))
    if addr is not None:
        p.append(text(x + w/2, y + h + 15, addr, size=10.5, color=MUTED))
    return "".join(p)


# ── swap-by-value: чому обмін через звичайні параметри не спрацьовує ───────────
# Ідея: функція дістає КОПІЇ, міняє копії, оригінали лишаються цілі.
def fig_swap_by_value():
    W, H = 780, 330
    p = []
    p.append(text(W/2, 26, "Функція дістає КОПІЇ — оригінали не міняються", size=15, bold=True))

    # ── ліворуч: оригінали в main ──
    p.append(text(150, 66, "у main", size=12.5, color=INK, bold=True))
    p.append(cell(90, 84, 120, "a", "3", VAL))
    p.append(cell(90, 168, 120, "b", "7", VAL))

    # стрілки копіювання праворуч
    p.append(arrow(215, 107, 300, 107, color=MUTED, sw=1.6))
    p.append(arrow(215, 191, 300, 191, color=MUTED, sw=1.6))
    p.append(text(258, 98, "копія", size=10, color=MUTED, italic=True))
    p.append(text(258, 182, "копія", size=10, color=MUTED, italic=True))

    # ── усередині swap(x, y): копії, які помінялися місцями ──
    p.append(text(400, 66, "усередині swap(x, y)", size=12.5, color=WARN, bold=True))
    p.append(cell(305, 84, 120, "x", "7", WARN))
    p.append(cell(305, 168, 120, "y", "3", WARN))
    p.append(text(365, 250, "тут обмін стався…", size=11, color=WARN, italic=True))

    # ── праворуч: після повернення — нічого не змінилось ──
    p.append(line(470, 70, 470, 260, color="#dcdcdc", sw=1.4, dash="5 5"))
    p.append(text(620, 66, "у main ПІСЛЯ виклику", size=12.5, color=INK, bold=True))
    p.append(cell(560, 84, 120, "a", "3", VAL))
    p.append(cell(560, 168, 120, "b", "7", VAL))
    p.append(text(620, 250, "…а тут — усе, як було", size=11, color=INK, italic=True))

    p.append(text(W/2, 306, "Копії зникли разом із функцією — оригінали a і b недосяжні.",
                  size=12, color=WARN, bold=True))
    return render(os.path.join(OUT, "swap-by-value.svg"), W, H, *p)


# ── ptr-cells: int *p = &x; дві комірки, і запис *p = 99 крізь покажчик ────────
def fig_ptr_cells():
    W, H = 760, 340
    p = []
    p.append(text(W/2, 26, "int *p = &x;  — покажчик тримає адресу x", size=15, bold=True))

    # x — дані
    p.append(cell(120, 92, 150, "x  (дані)", "42", VAL, addr="адреса 0x20"))
    # p — адреса
    p.append(cell(430, 92, 200, "p  (покажчик)", "0x20", ADDR, addr="адреса 0x10"))

    # стрілка p -> x («вказує на»)
    p.append(arrow(430, 115, 272, 115, color=ADDR, sw=2.2))
    p.append(text(360, 82, "вказує на", size=11, color=ADDR, bold=True, italic=True))

    # нижня частина: *p = 99 пише в x
    p.append(text(W/2, 210, "*p = 99;  — «піди за адресою в p і запиши туди»", size=13.5, color=WARN, bold=True))
    p.append(cell(120, 236, 150, "x  ТЕПЕР", "99", WARN, addr="адреса 0x20"))
    p.append(cell(430, 236, 200, "p  (без змін)", "0x20", ADDR, addr="адреса 0x10"))
    p.append(arrow(430, 259, 272, 259, color=WARN, sw=2.2))
    p.append(text(345, 226, "запис крізь p", size=11, color=WARN, bold=True, italic=True))

    p.append(text(W/2, 322, "p не змінився — змінилося те, НА ЩО він вказує.", size=12, color=MUTED, italic=True))
    return render(os.path.join(OUT, "ptr-cells.svg"), W, H, *p)


# ── array-decay: ім'я масиву = адреса першого елемента; arr[i] == *(arr+i) ─────
def fig_array_decay():
    W, H = 780, 300
    p = []
    p.append(text(W/2, 26, "Ім'я масиву = адреса першого елемента", size=15, bold=True))

    xs = [120, 220, 320, 420, 520]
    vals = ["10", "20", "30", "40", "50"]
    addrs = ["0x40", "0x44", "0x48", "0x4C", "0x50"]
    for i, x in enumerate(xs):
        p.append(rect(x, 96, 96, 48, fill="#fbfcfd", stroke=INK, sw=1.6))
        p.append(text(x + 48, 96 + 30, vals[i], size=14, color=VAL, bold=True))
        p.append(text(x + 48, 82, "arr[%d]" % i, size=11.5, color=INK, bold=True))
        p.append(text(x + 48, 160, addrs[i], size=10, color=MUTED))

    # arr показує на перший елемент
    p.append(arrow(150, 210, 150, 150, color=ADDR, sw=2.2))
    b, w, h = textbox(150, 232, "arr  →  0x40", size=12.5, color=ADDR, stroke=ADDR,
                      fill="#eaf6ee", bold=True, min_w=140)
    p.append(b)

    # тотожність
    b, w, h = textbox(470, 232, "arr[i]  ≡  *(arr + i)", size=13, color=WARN, stroke=WARN,
                      fill="#fdecea", bold=True, min_w=210)
    p.append(b)
    p.append(text(470, 205, "індекс — це прихована арифметика покажчика", size=10.5, color=MUTED, italic=True))
    return render(os.path.join(OUT, "array-decay.svg"), W, H, *p)


# ── null-history: одне рішення 1965 → клас аварій; тип-опція зачиняє двері ──────
# Для вставки hist-billion-dollar-null. Ліворуч — причинний ланцюг від винаходу
# нуля до класу аварій; праворуч — лік (тип-опція повертає безпеку).
def fig_null_history():
    W, H = 820, 470
    p = []
    p.append(text(W/2, 28, "Помилка на мільярд: від рішення 1965 року до класу аварій",
                  size=15, bold=True))

    # ── витік: 1965, нуль у типі ──
    b, w, h = textbox(200, 78, ["1965 · ALGOL W", "нуль вписано в ТИП посилання"],
                      size=12.5, bold=True, stroke=WARN, fill="#fdecea", color=WARN, min_w=300)
    p.append(b)

    # наслідок: тип перестав розрізняти
    p.append(arrow(200, 100, 200, 128, color=WARN, sw=2))
    b, w, h = textbox(200, 150, ["тип більше не розрізняє",
                                 "«веде на об'єкт»  vs  «порожньо»"],
                      size=11.5, stroke=INK, fill=FILL, min_w=320)
    p.append(b)

    # три властивості — три рамки в ряд
    p.append(arrow(200, 172, 200, 200, color=INK, sw=1.8))
    p.append(text(200, 214, "три властивості, що роблять помилку підступною:",
                  size=11, color=MUTED, italic=True))
    props = [
        ("невидима\nв ТИПІ", 78),
        ("рознесена\nв ЧАСІ", 200),
        ("слухняно\nвиконувана", 322),
    ]
    for s, cx in props:
        b, w, h = textbox(cx, 250, s, size=11, stroke=WARN, fill="#fdecea",
                          color=WARN, bold=True, min_w=104)
        p.append(b)

    # клас аварій
    p.append(arrow(200, 274, 200, 302, color=WARN, sw=2))
    b, w, h = textbox(200, 326, ["КЛАС АВАРІЙ:", "розіменування нуля"],
                      size=12.5, bold=True, stroke=WARN, fill="#f9d7d2", color=WARN, min_w=300)
    p.append(b)

    # C успадкував
    p.append(arrow(200, 348, 200, 374, color=MUTED, sw=1.7))
    b, w, h = textbox(200, 394, "C успадкував саму ідею (не винайшов)",
                      size=11, stroke=MUTED, fill=FILL, color=MUTED, min_w=320)
    p.append(b)

    # ── роздільник ──
    p.append(line(430, 62, 430, 420, color="#dcdcdc", sw=1.6, dash="6 6"))

    # ── лік: тип-опція ──
    p.append(text(628, 78, "Лік у новіших мовах", size=12.5, bold=True, color=FIELD))
    b, w, h = textbox(628, 122, ["ТИП-ОПЦІЯ", "Option · Optional · Maybe"],
                      size=12.5, bold=True, stroke=FIELD, fill="#eaf6ee", color=FIELD, min_w=290)
    p.append(b)

    p.append(arrow(628, 144, 628, 172, color=FIELD, sw=2))
    b, w, h = textbox(628, 198, ["знову РОЗДІЛЯЄ два типи:",
                                 "Some(значення)   vs   None"],
                      size=11.5, stroke=INK, fill=FILL, min_w=300)
    p.append(b)

    p.append(arrow(628, 220, 628, 248, color=FIELD, sw=2))
    b, w, h = textbox(628, 276, ["компілятор ПРИМУШУЄ", "розібрати випадок «нема»"],
                      size=11.5, bold=True, stroke=FIELD, fill="#eaf6ee", color=FIELD, min_w=300)
    p.append(b)

    p.append(arrow(628, 298, 628, 326, color=FIELD, sw=2))
    b, w, h = textbox(628, 352, ["клас аварій зникає", "ще до запуску"],
                      size=12, bold=True, stroke=FIELD, fill="#d7efdf", color=FIELD, min_w=290)
    p.append(b)

    p.append(text(628, 400, "саме та безпека, якої Гоар прагнув 1965-го",
                  size=10.5, color=MUTED, italic=True))

    return render(os.path.join(OUT, "null-history.svg"), W, H, *p)


if __name__ == "__main__":
    fig_swap_by_value()
    fig_ptr_cells()
    fig_array_decay()
    fig_null_history()
    print("OK figures written to", OUT)
