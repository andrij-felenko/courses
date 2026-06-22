# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── alias: один код у різних фірм означає різні прилади ───────────────────────
# Ідея: код на корпусі — псевдонім приладу в межах системи одного виробника,
# а не глобальне ім'я. Той самий A7 розходиться в кількох фірм у різні прилади,
# тож першими фільтрами стають корпус і виробник, а не сам код.

def fig_alias():
    W, H = 720, 360
    p = []

    # лівий блок: крихітний SOT-23 з кодом
    lx, ly, lw, lh = 30, 56, 300, 270
    p.append(rect(lx, ly, lw, lh, fill=BG, stroke="#c9d3dc", sw=1.4))
    p.append(text(lx + lw / 2, ly + 26, "SOT-23 (вид зверху), ~3 × 1.3 мм",
                  size=13, color=INK, bold=True))
    # корпус
    bx, by, bw, bh = lx + lw / 2 - 75, ly + 64, 150, 96
    p.append(rect(bx, by, bw, bh, fill="#2a2a2a", stroke="#000000", sw=2, rx=6))
    p.append('<text x="%.1f" y="%.1f" font-family="Consolas, monospace" font-size="34" '
             'fill="#f2f2f2" text-anchor="middle" font-weight="700">A7</text>'
             % (lx + lw / 2, by + bh / 2 + 12))
    # три ніжки
    for dx in (-46, 46):
        p.append(rect(bx + bw / 2 + dx - 11, by + bh, 22, 15, fill="#c9a24a", stroke="#7a6020", sw=1.3, rx=2))
    p.append(rect(bx + bw / 2 - 11, by - 15, 22, 15, fill="#c9a24a", stroke="#7a6020", sw=1.3, rx=2))
    # мітка піна 1
    p.append(circle(bx + 14, by + 14, 4.5, fill="#f2f2f2", stroke="#f2f2f2", sw=1))
    p.append(text(lx + lw / 2, ly + 200, "повна назва — десяток символів,",
                  size=12.5, color=MUTED))
    p.append(text(lx + lw / 2, ly + 218, "а на корпус влазить 2–3", size=12.5, color=MUTED))
    note = fitbox(lx + 22, ly + 232, lw - 44, 24, "код — псевдонім, а не part number",
                  size=12, fill="#fbf3df", stroke="#e3d09a", sw=1.2, bold=True)
    p.append(note)

    # правий блок: той самий код розходиться в різні прилади
    rx, ry, rw, rh = 360, 56, 330, 270
    p.append(rect(rx, ry, rw, rh, fill=BG, stroke="#c9d3dc", sw=1.4))
    p.append(text(rx + rw / 2, ry + 26, "той самий код — чому неоднозначний",
                  size=13, color=INK, bold=True))
    src = rx + 56
    p.append(rect(src - 34, ry + 44, 68, 34, fill="#2a2a2a", stroke="#000000", sw=2, rx=5))
    p.append('<text x="%.1f" y="%.1f" font-family="Consolas, monospace" font-size="20" '
             'fill="#f2f2f2" text-anchor="middle" font-weight="700">A7</text>' % (src, ry + 67))
    rows = [
        ("виробник + корпус → BAV99", "здвоєний діод (SOT-23)", NEG),
        ("інша фірма / корпус", "інший прилад", POS),
        ("ще одна система позначень", "ще інше", MUTED),
    ]
    yy = ry + 96
    for head, tail, col in rows:
        p.append(line(src, ry + 78, rx + 28, yy + 14, color=col, sw=1.7))
        p.append(rect(rx + 28, yy, rw - 48, 40, fill="#f3f3f3", stroke="#d6d6d6", sw=1.1, rx=5))
        p.append(text(rx + 40, yy + 17, head, size=11.5, color=col, anchor="start", bold=True))
        p.append(text(rx + 40, yy + 33, tail, size=11.5, color=INK, anchor="start"))
        yy += 52

    render(os.path.join(OUT, "alias.svg"), W, H, *p,
           title="Маркування — псевдонім приладу всередину однієї фірми")


# ── parts: з яких ролей зібраний код ─────────────────────────────────────────
# Ідея: у коді майже завжди ховаються три ролі — сімейство приладу, суфікс
# варіанта й (інколи) дата/партія, яку при декодуванні відкидають; окремо
# стоїть мітка піна 1, що не є символом коду.

def fig_parts():
    W, H = 720, 300
    p = []
    cx = W / 2

    # збільшений код по центру
    p.append(text(cx, 60, "A7W", size=46, color=INK, bold=True))
    # підкреслення ролей під символами
    p.append(line(cx - 46, 74, cx - 8, 74, color=NEG, sw=3))      # A7
    p.append(line(cx + 4, 74, cx + 30, 74, color=FIELD, sw=3))    # W

    boxes = [
        (cx - 230, 120, NEG, "#eef4ff", "сімейство приладу",
         "головна частина: який це\nтранзистор, діод чи мікросхема"),
        (cx + 10, 120, FIELD, "#eafaf0", "суфікс варіанта",
         "уточнює різновид: підтип,\nпідсилення, клас напруги"),
    ]
    for bx, by, col, fill, head, body in boxes:
        p.append(rect(bx, by, 220, 78, fill=fill, stroke=col, sw=1.6))
        p.append(text(bx + 110, by + 22, head, size=13, color=col, bold=True))
        p.append(mtext(bx + 110, by + 42, body, size=11.5, color=INK))

    # дата/партія — окрема, відкидається
    p.append(rect(cx - 230, 218, 220, 56, fill="#f3f3f3", stroke=MUTED, sw=1.4))
    p.append(text(cx - 120, 240, "дата / партія", size=13, color=MUTED, bold=True))
    p.append(text(cx - 120, 260, "до типу приладу не стосується —", size=11, color=INK))
    p.append(text(cx - 120, 274, "при декодуванні відкидають", size=11, color=INK))

    # мітка піна 1 — не символ коду
    p.append(rect(cx + 10, 218, 220, 56, fill="#fdf6e3", stroke="#e0a32e", sw=1.4))
    p.append(circle(cx + 32, 240, 6, fill="#e0a32e", stroke="#e0a32e", sw=1))
    p.append(text(cx + 130, 240, "мітка піна 1", size=13, color="#b07d10", bold=True))
    p.append(text(cx + 120, 260, "крапка / скіс / смужка — ключ", size=11, color=INK))
    p.append(text(cx + 120, 274, "до розпіновки, а не літера коду", size=11, color=INK))

    render(os.path.join(OUT, "parts.svg"), W, H, *p,
           title="Три ролі всередині коду (плюс мітка піна 1 окремо)")


# ── decode: процедура від коду до компонента ─────────────────────────────────
# Ідея: декодування — упорядкована процедура з п'яти кроків, а не вгадування;
# пропуск кроку «чий це код» дає хибну відповідь.

def fig_decode():
    W, H = 720, 470
    p = []
    steps = [
        (NEG,  "1", "Зчитай код точно",
         "A7 (велике A, цифра 7). Знайди мітку піна 1 —", "вона задає орієнтацію корпусу."),
        (FIELD, "2", "Зафіксуй корпус",
         "Порахуй ніжки → SOT-23, 3 ніжки.", "Код чинний лише в парі зі своїм корпусом."),
        ("#e0a32e", "3", "Знайди виробника",
         "Логотип, закупівля чи контекст плати.", "Один код у різних фірм означає різне."),
        (INK,  "4", "Шукай у таблиці кодів",
         "Marking-розділ даташита або зведений", "довідник кодів: рядок A7 → ім'я приладу."),
        (POS,  "5", "Звір по даташиту",
         "Звір корпус, ніжки й функцію знайденого", "приладу — це відсіює випадкові збіги."),
    ]
    bx, bw, bh = 40, 640, 66
    y = 56
    for col, num, head, l1, l2 in steps:
        p.append(rect(bx, y, bw, bh, fill=BG, stroke=col, sw=1.8))
        p.append(circle(bx + 30, y + bh / 2, 18, fill=col, stroke=col, sw=1))
        p.append(text(bx + 30, y + bh / 2 + 6, num, size=18, color=BG, bold=True))
        p.append(text(bx + 62, y + 24, head, size=15, color=col, anchor="start", bold=True))
        p.append(text(bx + 62, y + 43, l1, size=12.5, color=INK, anchor="start"))
        p.append(text(bx + 62, y + 59, l2, size=12.5, color=INK, anchor="start"))
        if num != "5":
            p.append(arrow(bx + bw / 2, y + bh, bx + bw / 2, y + bh + 14, color=MUTED, sw=2))
        y += bh + 16

    render(os.path.join(OUT, "decode.svg"), W, H, *p,
           title="Від коду до компонента: п'ять кроків, не вгадування")


# ── codes: код-метод на пасивних деталях (значущі цифри + множник) ────────────
# Ідея: на резисторах і конденсаторах місця теж немає, тож номінал стискають
# тим самим прийомом «значущі цифри + множник»; показано три його форми.

def fig_codes():
    W, H = 720, 360
    p = []
    cards = [
        (30, "тризначний", "103", "10 × 10³", "= 10 000 Ω = 10 кΩ",
         "перші дві — значущі,\nтретя — скільки нулів"),
        (250, "літера R = кома", "4R7", "4.7", "= 4.7 (Ом або пФ)",
         "R сидить на місці коми;\nне губиться, як крапка"),
        (470, "EIA-96 (точні 1%)", "01C", "100 × 100", "= 10 000 Ω = 10 кΩ",
         "дві цифри → код у ряді E96,\nлітера → множник"),
    ]
    cw, ch = 220, 250
    for x, kind, code, mid, res, note in cards:
        p.append(rect(x, 60, cw, ch, fill=BG, stroke="#c9d3dc", sw=1.4))
        p.append(text(x + cw / 2, 86, kind, size=13, color=INK, bold=True))
        p.append(rect(x + cw / 2 - 52, 100, 104, 46, fill="#f1f1f1", stroke="#c9c9c9", sw=1.3, rx=6))
        p.append('<text x="%.1f" y="%.1f" font-family="Consolas, monospace" font-size="30" '
                 'fill="%s" text-anchor="middle" font-weight="700">%s</text>'
                 % (x + cw / 2, 134, INK, code))
        p.append(text(x + cw / 2, 174, mid, size=15, color=NEG, bold=True))
        p.append(text(x + cw / 2, 200, res, size=13, color=FIELD, bold=True))
        p.append(mtext(x + cw / 2, 232, note, size=11.5, color=MUTED))

    render(os.path.join(OUT, "codes.svg"), W, H, *p,
           title="Код-метод пасивних деталей: значущі цифри + множник")


if __name__ == "__main__":
    fig_alias()
    fig_parts()
    fig_decode()
    fig_codes()
    print("OK: figures written to", OUT)
