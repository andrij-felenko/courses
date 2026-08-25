# -*- coding: utf-8 -*-
"""Фігури до теми «Угода про виклик (ABI)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

RED_BG   = "#fdecea"
AMBER    = "#b8860b"
AMBER_BG = "#fdf6e3"
GREEN_BG = "#eaf6ee"
BLUE_BG  = "#eaf0fd"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


# ── 1. Що саме мусять узгодити два боки ───────────────────────────────────────
def fig_contract():
    W, H = 820, 400
    f = []
    # дві сторони
    cw, ch = 210, 90
    caller, _, _ = textbox(130, 90, "ТОЙ, ХТО КЛИЧЕ\n(caller)\nпрошивка, що викликає",
                           size=13, fill=BLUE_BG, stroke=NEG, sw=2.2, min_w=cw)
    f.append(caller)
    callee, _, _ = textbox(W - 130, 90, "ТОЙ, КОГО КЛИЧУТЬ\n(callee)\nфункція-бібліотека",
                           size=13, fill=GREEN_BG, stroke=FIELD, sw=2.2, min_w=cw)
    f.append(callee)
    # двобічна стрілка згори
    f.append(arrow(245, 90, W - 245, 90, color=INK, sw=2.4))
    f.append(arrow(W - 245, 78, 245, 78, color=INK, sw=2.4))
    # рамка-контракт посередині
    terms = ("СПІЛЬНА ДОМОВЛЕНІСТЬ (ABI)\n"
             "• куди класти аргументи (які регістри, тоді стек)\n"
             "• звідки брати результат (регістр RAX / R0)\n"
             "• хто зберігає які регістри (caller- / callee-saved)\n"
             "• як лягає кадр стека і де адреса повернення\n"
             "• хто прибирає стек після виклику")
    box, bw, bh = textbox(W / 2, 250, terms, size=13, fill=AMBER_BG, stroke=AMBER, sw=2.4, min_w=560)
    f.append(box)
    f.append(arrow(130, 135, 200, 250 - bh / 2, color=NEG, sw=2))
    f.append(arrow(W - 130, 135, W - 200, 250 - bh / 2, color=FIELD, sw=2))
    f.append(text(W / 2, 250 + bh / 2 + 30,
                  "збігаються ці пункти — код склеюється; не збігаються — тихо ламається",
                  size=12, color=INK, bold=True))
    out("contract.svg", W, H, *f,
        title="Угода про виклик: що саме мусять узгодити обидва боки")


# ── 2. Перші аргументи в регістрах, решта — на стек ───────────────────────────
def fig_args():
    W, H = 860, 430
    f = []
    f.append(text(W / 2, 42, "виклик  f(a, b, c, d, e, f, g)  — сім аргументів",
                  size=14, color=INK, bold=True))
    # регістри (перші 6)
    regs = [("RDI", "a"), ("RSI", "b"), ("RDX", "c"),
            ("RCX", "d"), ("R8", "e"), ("R9", "f")]
    x0 = 60
    rw, rh = 118, 46
    f.append(text(x0, 92, "перші 6 — у регістрах (швидко):", size=12, color=NEG, anchor="start", bold=True))
    for i, (r, a) in enumerate(regs):
        x = x0 + (i % 3) * (rw + 16)
        y = 108 + (i // 3) * (rh + 14)
        f.append(rect(x, y, rw, rh, fill=BLUE_BG, stroke=NEG, sw=1.8))
        f.append(text(x + 12, y + 20, r, size=13, color=NEG, anchor="start", bold=True))
        f.append(text(x + rw - 12, y + 30, "= " + a, size=13, color=INK, anchor="end", bold=True))
    # стек (решта)
    sx = 560
    f.append(text(sx + 90, 92, "решта — на стек (по черзі):", size=12, color=POS, anchor="start", bold=True))
    stack = [("g", POS), ("(адреса повернення)", MUTED)]
    sy = 110
    sw_ = 230
    for val, col in stack:
        f.append(rect(sx, sy, sw_, 40, fill=(RED_BG if col == POS else "#f3f3f3"), stroke=col, sw=1.8))
        f.append(text(sx + sw_ / 2, sy + 26, val, size=12, color=col, bold=True))
        sy += 46
    f.append(text(sx + sw_ / 2, sy + 20, "↓ стек росте вниз", size=11, color=MUTED, italic=True))
    # результат
    res, _, _ = textbox(W / 2, 340, "результат функції повертається в  RAX",
                        size=14, fill=GREEN_BG, stroke=FIELD, sw=2.2, min_w=360)
    f.append(res)
    f.append(text(W / 2, 392, "6 регістрів — це стеля System V AMD64; на ARM таких регістрів чотири (R0–R3)",
                  size=11, color=MUTED, italic=True))
    out("args.svg", W, H, *f,
        title="Аргументи: перші — в регістрах, надлишок — на стек, результат у RAX")


# ── 3. Caller-saved ↔ callee-saved ────────────────────────────────────────────
def fig_saved_split():
    W, H = 860, 440
    f = []
    f.append(text(W / 2, 40, "хто відповідає за збереження регістра?", size=14, color=INK, bold=True))
    # ліва колонка — caller-saved
    lx, ly, cw = 40, 70, 370
    f.append(rect(lx, ly, cw, 320, fill="#fafafa", stroke=NEG, sw=2))
    f.append(rect(lx, ly, cw, 40, fill=NEG, stroke=NEG, sw=0))
    f.append(text(lx + cw / 2, ly + 26, "CALLER-SAVED (леткі)", size=13, color=BG, bold=True))
    left = [
        "RAX RCX RDX RSI RDI R8 R9 R10 R11",
        "",
        "callee вільно їх псує.",
        "Треба значення після виклику —",
        "той, хто кличе, сам його зберіг",
        "перед викликом і відновив після.",
        "Сюди ж падають перші аргументи.",
    ]
    ty = ly + 70
    for i, ln in enumerate(left):
        f.append(text(lx + 20, ty, ln, size=(13 if i == 0 else 12),
                      color=(NEG if i == 0 else INK), anchor="start", bold=(i == 0)))
        ty += 32 if i == 0 else 30
    # права колонка — callee-saved
    rx = 450
    f.append(rect(rx, ly, cw, 320, fill="#fafafa", stroke=FIELD, sw=2))
    f.append(rect(rx, ly, cw, 40, fill=FIELD, stroke=FIELD, sw=0))
    f.append(text(rx + cw / 2, ly + 26, "CALLEE-SAVED (стійкі)", size=13, color=BG, bold=True))
    right = [
        "RBX RBP R12 R13 R14 R15",
        "",
        "callee, якщо хоче ними скористатись,",
        "мусить спершу зберегти їх на стек",
        "і повернути назад перед виходом.",
        "Для того, хто кличе, вони «як були» —",
        "переживають виклик недоторканими.",
    ]
    ty = ly + 70
    for i, ln in enumerate(right):
        f.append(text(rx + 20, ty, ln, size=(13 if i == 0 else 12),
                      color=(FIELD if i == 0 else INK), anchor="start", bold=(i == 0)))
        ty += 32 if i == 0 else 30
    f.append(text(W / 2, 424,
                  "поділ — компроміс: зберігати кожен регістр при кожному виклику було б надто дорого",
                  size=11, color=MUTED, italic=True))
    out("saved-split.svg", W, H, *f,
        title="Регістри поділені: одні береже той, хто кличе, інші — той, кого кличуть")


# ── 4. Кадр стека й адреса повернення ─────────────────────────────────────────
def fig_frame():
    W, H = 820, 470
    f = []
    f.append(text(W / 2, 40, "кадр стека під час виклику  g()  з  f()", size=14, color=INK, bold=True))
    # стос кадрів
    x0, w = 250, 320
    rows = [
        ("кадр f() — локальні змінні f", BLUE_BG, NEG, 60),
        ("надлишкові аргументи для g", RED_BG, POS, 34),
        ("адреса повернення (куди вертатись у f)", AMBER_BG, AMBER, 34),
        ("збережений RBP  (ланцюг кадрів)", "#eef2f7", INK, 34),
        ("callee-saved регістри, що g псує", GREEN_BG, FIELD, 34),
        ("локальні змінні g()", GREEN_BG, FIELD, 60),
    ]
    y = 70
    for i, (label, fill, col, h) in enumerate(rows):
        f.append(rect(x0, y, w, h, fill=fill, stroke=col, sw=1.8))
        f.append(text(x0 + w / 2, y + h / 2 + 5, label, size=12, color=col, bold=True))
        y += h + 4
    total_h = y - 74
    # покажчики
    f.append(text(x0 - 16, 70 + 30, "верх (старі кадри)", size=11, color=MUTED, anchor="end"))
    # RSP знизу
    f.append(arrow(x0 + w + 90, y - 30, x0 + w + 6, y - 30, color=NEG, sw=2.4))
    f.append(text(x0 + w + 96, y - 26, "RSP — вершина стека", size=12, color=NEG, anchor="start", bold=True))
    # стрілка адреси повернення
    ret_y = 70 + rows[0][3] + 4 + rows[1][3] + 4 + rows[2][3] / 2
    f.append(arrow(x0 - 90, ret_y, x0 - 6, ret_y, color=AMBER, sw=2.4))
    f.append(text(x0 - 96, ret_y - 4, "call поклав сюди", size=11, color=AMBER, anchor="end", bold=True))
    f.append(text(x0 - 96, ret_y + 12, "адресу повернення", size=11, color=AMBER, anchor="end", bold=True))
    # напрям росту
    f.append(text(x0 + w / 2, y + 28, "↓ стек росте вниз (до менших адрес) ↓", size=12, color=MUTED, bold=True))
    f.append(text(x0 + w / 2, y + 52, "ret знімає адресу повернення й стрибає нею назад у f",
                  size=11, color=INK, italic=True))
    out("frame.svg", W, H, *f,
        title="Кадр стека: локальні змінні, збережені регістри й адреса повернення")


# ── 5. cdecl проти stdcall (вставка hist-abi-wars) ────────────────────────────
def fig_wars():
    W, H = 880, 470
    f = []
    f.append(text(W / 2, 40, "хто прибирає стек після виклику?", size=15, color=INK, bold=True))
    colw, y0, h = 380, 70, 350
    # ── ліва колонка: cdecl ──
    lx = 40
    f.append(rect(lx, y0, colw, h, fill="#fafafa", stroke=NEG, sw=2))
    f.append(rect(lx, y0, colw, 44, fill=NEG, stroke=NEG, sw=0))
    f.append(text(lx + colw / 2, y0 + 28, "cdecl", size=15, color=BG, bold=True))
    left = [
        ("прибирає ТОЙ, ХТО КЛИЧЕ", NEG, True),
        ("", INK, False),
        ("код прибирання — у КОЖНОМУ", INK, False),
        ("місці виклику (більше байтів)", INK, False),
        ("", INK, False),
        ("✓ змінне число аргументів:", FIELD, True),
        ("   printf, scanf працюють —", INK, False),
        ("   хто кличе, знає їхню", INK, False),
        ("   кількість завжди", INK, False),
    ]
    ty = y0 + 74
    for ln, col, bold in left:
        f.append(text(lx + 22, ty, ln, size=13, color=col, anchor="start", bold=bold))
        ty += 30
    # ── права колонка: stdcall ──
    rx = W - 40 - colw
    f.append(rect(rx, y0, colw, h, fill="#fafafa", stroke=POS, sw=2))
    f.append(rect(rx, y0, colw, 44, fill=POS, stroke=POS, sw=0))
    f.append(text(rx + colw / 2, y0 + 28, "stdcall", size=15, color=BG, bold=True))
    right = [
        ("прибирає ТА, КОГО КЛИЧУТЬ", POS, True),
        ("", INK, False),
        ("код прибирання — в ОДНОМУ", INK, False),
        ("місці (компактніше); стандарт", INK, False),
        ("Win32 API, спадок Паскаля", INK, False),
        ("✗ змінне число аргументів", POS, True),
        ("   неможливе — callee наперед", INK, False),
        ("   не знає, скільки аргументів", INK, False),
        ("   прибирати", INK, False),
    ]
    ty = y0 + 74
    for ln, col, bold in right:
        f.append(text(rx + 22, ty, ln, size=13, color=col, anchor="start", bold=bold))
        ty += 30
    f.append(text(W / 2, y0 + h + 34,
                  "одне дрібне рішення — два протилежні набори наслідків",
                  size=12, color=MUTED, italic=True))
    out("wars.svg", W, H, *f,
        title="Війна угод x86: cdecl проти stdcall")


# ── 6. Пекло DLL (вставка hist-abi-wars) ──────────────────────────────────────
def fig_dll_hell():
    W, H = 860, 470
    f = []
    f.append(text(W / 2, 40, "спільна системна тека Windows", size=15, color=INK, bold=True))
    # три програми зверху
    apps = [("Програма A", "чекає OLE2NLS v2.01"),
            ("Програма B", "ставить OLE2NLS v2.02"),
            ("Програма C", "чекає OLE2NLS v2.01")]
    aw, ay = 220, 70
    xs = [40, (W - aw) / 2, W - 40 - aw]
    for (name, want), x in zip(apps, xs):
        col = POS if "2.02" in want else NEG
        f.append(rect(x, ay, aw, 60, fill=(RED_BG if col == POS else BLUE_BG), stroke=col, sw=2))
        f.append(text(x + aw / 2, ay + 26, name, size=13, color=col, bold=True))
        f.append(text(x + aw / 2, ay + 46, want, size=11, color=INK))
    # спільний файл посередині
    box, bw, bh = textbox(W / 2, 250,
                          "СПІЛЬНА ТЕКА:  \\Windows\\System\\\n"
                          "OLE2NLS.DLL  —  одне ім'я, одна копія",
                          size=13, fill=AMBER_BG, stroke=AMBER, sw=2.4, min_w=460)
    f.append(box)
    # стрілки: A і C читають, B перезаписує
    f.append(arrow(xs[0] + aw / 2, ay + 60, W / 2 - 120, 250 - bh / 2, color=NEG, sw=1.8))
    f.append(arrow(xs[2] + aw / 2, ay + 60, W / 2 + 120, 250 - bh / 2, color=NEG, sw=1.8))
    f.append(arrow(xs[1] + aw / 2, ay + 60, W / 2, 250 - bh / 2, color=POS, sw=2.6))
    f.append(text(W / 2 + 130, 175, "перезапис!", size=12, color=POS, anchor="start", bold=True))
    # наслідок
    res, rw, rh = textbox(W / 2, 360,
                          "B перезаписала спільний файл своєю версією —\n"
                          "A і C ламаються, хоч їх ніхто не чіпав",
                          size=13, fill=RED_BG, stroke=POS, sw=2.2, min_w=520)
    f.append(res)
    f.append(text(W / 2, 360 + rh / 2 + 30,
                  "+ якщо DLL і той, хто кличе, розійшлись в угоді виклику — стек тихо повзе",
                  size=11, color=MUTED, italic=True))
    out("dll-hell.svg", W, H, *f,
        title="«Пекло DLL»: одне ім'я, багато несумісних версій")


# ── 7. System V ABI: gABI + psABI → Linux/BSD/macOS (вставка hist-abi-wars) ────
def fig_sysv_tree():
    W, H = 860, 500
    f = []
    # корінь
    root, rw, rh = textbox(W / 2, 70,
                           "System V ABI\n(AT&T UNIX System V, з 1983)",
                           size=14, fill=AMBER_BG, stroke=AMBER, sw=2.4, min_w=340)
    f.append(root)
    # два поділи
    gy = 200
    g_box, gw, gh = textbox(230, gy,
                            "gABI — загальна частина\n"
                            "формати файлів (ELF),\n"
                            "правила зв'язування\n(однакові скрізь)",
                            size=12, fill=GREEN_BG, stroke=FIELD, sw=2.2, min_w=280)
    f.append(g_box)
    p_box, pw, ph = textbox(W - 230, gy,
                            "psABI — процесорний додаток\n"
                            "які регістри під аргументи,\n"
                            "розміри типів, порядок байтів\n(під кожну архітектуру свій)",
                            size=12, fill=BLUE_BG, stroke=NEG, sw=2.2, min_w=280)
    f.append(p_box)
    f.append(arrow(W / 2 - 40, 70 + rh / 2, 230 + 40, gy - gh / 2, color=INK, sw=2))
    f.append(arrow(W / 2 + 40, 70 + rh / 2, W - 230 - 40, gy - gh / 2, color=INK, sw=2))
    # приклад psABI
    f.append(text(W - 230, gy + ph / 2 + 26,
                  "напр. AMD64: RDI, RSI, RDX, RCX, R8, R9",
                  size=11, color=NEG, italic=True))
    # спільний стовбур униз
    ty = 330
    trunk, tw, th = textbox(W / 2, ty,
                            "один письмовий стандарт двійкової сумісності",
                            size=13, fill="#eef2f7", stroke=INK, sw=2, min_w=480)
    f.append(trunk)
    f.append(arrow(230, gy + gh / 2, W / 2 - 80, ty - th / 2, color=FIELD, sw=1.8))
    f.append(arrow(W - 230, gy + ph / 2, W / 2 + 80, ty - th / 2, color=NEG, sw=1.8))
    # три листки
    leaves = ["Linux", "BSD", "macOS (x86-64)"]
    lw, lyy = 220, 420
    xs = [40, (W - lw) / 2, W - 40 - lw]
    for name, x in zip(leaves, xs):
        f.append(rect(x, lyy, lw, 50, fill=GREEN_BG, stroke=FIELD, sw=2))
        f.append(text(x + lw / 2, lyy + 30, name, size=14, color=FIELD, bold=True))
        f.append(arrow(W / 2, ty + th / 2, x + lw / 2, lyy - 4, color=MUTED, sw=1.5))
    out("sysv-tree.svg", W, H, *f,
        title="System V ABI: один корінь → Linux, BSD, macOS")


if __name__ == "__main__":
    fig_contract()
    fig_args()
    fig_saved_split()
    fig_frame()
    fig_wars()
    fig_dll_hell()
    fig_sysv_tree()
    print("OK: 7 фігур у", IMG)
