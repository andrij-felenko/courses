# -*- coding: utf-8 -*-
"""Фігури теми «Решта поведінкових оглядово» (Інтерпретатор, Знімок). Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

GOLD = "#8a6d00"
GOLDFILL = "#fff9e6"
GOLDSTROKE = "#e0a800"


def tbox(cx, cy, s, **kw):
    frag, _w, _h = textbox(cx, cy, s, **kw)
    return frag


# ── Інтерпретатор: дерево виразу x + 3 * 2 ──────────────────────────────────
def fig_interpreter_ast():
    W, H = 900, 460
    f = []

    # координати вузлів
    ADD = (450, 110)
    VARX = (270, 240)
    MUL = (630, 240)
    NUM3 = (540, 370)
    NUM2 = (720, 370)

    # лінії виклику вниз (батько -> дитина): суцільні, ведуть ПОВЗ підписи вузлів
    f.append(line(ADD[0] - 14, ADD[1] + 22, VARX[0] + 18, VARX[1] - 26, color=NEG, sw=2.0))
    f.append(line(ADD[0] + 14, ADD[1] + 22, MUL[0] - 18, MUL[1] - 26, color=NEG, sw=2.0))
    f.append(line(MUL[0] - 14, MUL[1] + 22, NUM3[0] + 14, NUM3[1] - 26, color=NEG, sw=2.0))
    f.append(line(MUL[0] + 14, MUL[1] + 22, NUM2[0] - 14, NUM2[1] - 26, color=NEG, sw=2.0))

    # вузли дерева
    f.append(tbox(*ADD, "Add", size=15, bold=True, fill="#eef2ff", stroke=NEG, min_w=90))
    f.append(tbox(*VARX, "Var(x)", size=14, fill=FILL, stroke=LINE, min_w=90))
    f.append(tbox(*MUL, "Mul", size=15, bold=True, fill="#eef2ff", stroke=NEG, min_w=90))
    f.append(tbox(*NUM3, "Num(3)", size=14, fill=FILL, stroke=LINE, min_w=90))
    f.append(tbox(*NUM2, "Num(2)", size=14, fill=FILL, stroke=LINE, min_w=90))

    # підписи результатів interpret — під кожним вузлом, окремо від ліній
    f.append(text(VARX[0], VARX[1] + 40, "interpret → 5", size=12, color=FIELD, bold=True))
    f.append(text(NUM3[0], NUM3[1] + 40, "interpret → 3", size=12, color=FIELD, bold=True))
    f.append(text(NUM2[0], NUM2[1] + 40, "interpret → 2", size=12, color=FIELD, bold=True))
    f.append(text(MUL[0] + 90, MUL[1] - 8, "interpret → 6", size=12, color=FIELD, bold=True, anchor="start"))
    f.append(text(ADD[0] + 90, ADD[1] - 8, "interpret → 11", size=13, color=FIELD, bold=True, anchor="start"))

    # значення спливають угору — пунктирні зелені лінії поряд із суцільними викличними
    f.append(line(VARX[0] + 26, VARX[1] - 30, ADD[0] - 22, ADD[1] + 18, color=FIELD, sw=1.4, dash="5,4"))
    f.append(line(MUL[0] - 26, MUL[1] - 30, ADD[0] + 22, ADD[1] + 18, color=FIELD, sw=1.4, dash="5,4"))
    f.append(line(NUM3[0] + 22, NUM3[1] - 30, MUL[0] - 22, MUL[1] + 18, color=FIELD, sw=1.4, dash="5,4"))
    f.append(line(NUM2[0] - 22, NUM2[1] - 30, MUL[0] + 22, MUL[1] + 18, color=FIELD, sw=1.4, dash="5,4"))

    f.append(text(150, 60, "суцільна синя — виклик interpret() вниз", size=12, color=NEG, anchor="start"))
    f.append(text(150, 82, "пунктирна зелена — значення спливає вгору", size=12, color=FIELD, anchor="start"))

    f.append(text(W / 2, 430, "Корінь Add не знає, гілка під ним чи лист — кожен вузол відповідає лише за свій interpret().",
                  size=12, color=MUTED))
    render(out("interpreter-ast.svg"), W, H, *f,
           title="Дерево виразу «x + 3 * 2» з об'єктів-вузлів")


# ── Знімок: три ролі ─────────────────────────────────────────────────────────
def fig_memento_roles():
    W, H = 980, 420
    f = []

    # Джерело — ліворуч
    SX, SY, SW_, SH = 60, 110, 260, 190
    f.append(rect(SX, SY, SW_, SH, fill="#eef2ff", stroke=NEG, sw=2.0, rx=10))
    f.append(text(SX + SW_ / 2, SY + 30, "Джерело", size=15, color=NEG, bold=True))
    f.append(text(SX + SW_ / 2, SY + 54, "(Originator)", size=12, color=NEG))
    f.append(rect(SX + 30, SY + 78, SW_ - 60, 84, fill="#ffffff", stroke=NEG, sw=1.2, rx=6, ))
    f.append(text(SX + SW_ / 2, SY + 100, "прихований стан", size=12, color=INK))
    f.append(text(SX + SW_ / 2, SY + 124, "text, cursor", size=13, color=INK, bold=True))
    f.append(text(SX + SW_ / 2, SY + 150, "редактор", size=11, color=MUTED))

    # Знімок — центр, коробка з замком
    MX, MY, MW, MH = 400, 110, 220, 190
    f.append(rect(MX, MY, MW, MH, fill="#fff9e6", stroke=GOLDSTROKE, sw=2.2, rx=10))
    f.append(text(MX + MW / 2, MY + 30, "Знімок", size=15, color=GOLD, bold=True))
    f.append(text(MX + MW / 2, MY + 54, "(Memento)", size=12, color=GOLD))
    # замок: коло + дужка
    lockcx, lockcy = MX + MW / 2, MY + 108
    f.append(circle(lockcx, lockcy, 22, fill="#fffdf5", stroke=GOLDSTROKE, sw=2))
    f.append(text(lockcx, lockcy + 6, "🔒", size=20, color=GOLD, anchor="middle"))
    f.append(text(MX + MW / 2, MY + 158, "читає лише", size=12, color=MUTED))
    f.append(text(MX + MW / 2, MY + 176, "Джерело", size=12, color=MUTED, bold=True))

    # Доглядач — праворуч, стос коробок
    CX, CY, CW, CH = 700, 110, 220, 190
    f.append(rect(CX, CY, CW, CH, fill="#eaf7ef", stroke=FIELD, sw=2.0, rx=10))
    f.append(text(CX + CW / 2, CY + 30, "Доглядач", size=15, color=FIELD, bold=True))
    f.append(text(CX + CW / 2, CY + 54, "(Caretaker)", size=12, color=FIELD))
    for i, dy in enumerate((70, 92, 114)):
        stw = 130 - i * 10
        f.append(rect(CX + CW / 2 - stw / 2, CY + dy, stw, 18, fill="#ffffff", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(CX + CW / 2, CY + 152, "стос коробок", size=12, color=INK))
    f.append(text(CX + CW / 2, CY + 168, "(історія скасувань)", size=11, color=MUTED))
    f.append(text(CX + CW / 2, CY + 184, "тримає, але не відкриває", size=11, color=MUTED, bold=True))

    # стрілки save()/restore() між Джерелом і Знімком
    f.append(arrow(SX + SW_ + 4, SY + 60, MX - 4, MY + 60, color=NEG, sw=2.0))
    f.append(text((SX + SW_ + MX) / 2, SY + 44, "save()", size=13, color=NEG, bold=True))
    f.append(arrow(MX - 4, SY + 90, SX + SW_ + 4, SY + 90, color=FIELD, sw=2.0))
    f.append(text((SX + SW_ + MX) / 2, SY + 108, "restore()", size=13, color=FIELD, bold=True))

    # стрілка "у стос" від Знімка до Доглядача
    f.append(arrow(MX + MW + 4, MY + 96, CX - 4, CY + 96, color=GOLD, sw=2.0))
    f.append(text((MX + MW + CX) / 2, MY + 78, "у стос", size=13, color=GOLD, bold=True))

    f.append(text(W / 2, 350, "Джерело пакує й розпаковує стан; Доглядач лише впорядковує коробки в часі й ніколи не заглядає всередину.",
                  size=12, color=MUTED))
    render(out("memento-roles.svg"), W, H, *f,
           title="Три ролі Знімка")


# ── Знімок проти журналу змін ─────────────────────────────────────────────────
def fig_memento_vs_eventlog():
    W, H = 980, 430
    f = []

    # верхній ряд — Знімок: чотири повні коробки
    TOP_Y = 100
    xs = [190, 390, 590, 790]
    labels = ["S₀", "S₁", "S₂", "S₃"]
    f.append(text(40, TOP_Y + 5, "Знімок", size=14, color=NEG, bold=True, anchor="start"))
    for x, lab in zip(xs, labels):
        active = (lab == "S₃")
        f.append(rect(x - 55, TOP_Y - 32, 110, 64,
                      fill="#eef2ff" if not active else "#fdecea",
                      stroke=NEG if not active else POS, sw=2.2 if active else 1.6, rx=8))
        f.append(text(x, TOP_Y + 7, lab, size=16, color=INK, bold=True))
    for x1, x2 in zip(xs, xs[1:]):
        f.append(line(x1 + 55, TOP_Y, x2 - 55, TOP_Y, color=MUTED, sw=1.3))
    f.append(text(xs[3], TOP_Y - 52, "відновити крок 3 = взяти S₃ готовим", size=12, color=POS, bold=True))
    f.append(text(xs[3], TOP_Y + 60, "миттєво, але кожна коробка —", size=11, color=MUTED))
    f.append(text(xs[3], TOP_Y + 78, "повний обсяг пам'яті", size=11, color=MUTED))

    # нижній ряд — журнал змін: одна база + три дельти
    BOT_Y = 300
    f.append(text(40, BOT_Y + 5, "Журнал змін", size=14, color=FIELD, bold=True, anchor="start"))
    f.append(rect(xs[0] - 55, BOT_Y - 32, 110, 64, fill="#eaf7ef", stroke=FIELD, sw=2.2, rx=8))
    f.append(text(xs[0], BOT_Y + 7, "S₀", size=16, color=INK, bold=True))
    deltas = ["Δ₁", "Δ₂", "Δ₃"]
    for x, lab in zip(xs[1:], deltas):
        f.append(rect(x - 34, BOT_Y - 20, 68, 40, fill="#fffdf5", stroke=GOLDSTROKE, sw=1.6, rx=6))
        f.append(text(x, BOT_Y + 6, lab, size=14, color=GOLD, bold=True))
    f.append(line(xs[0] + 55, BOT_Y, xs[1] - 34, BOT_Y, color=MUTED, sw=1.3))
    f.append(line(xs[1] + 34, BOT_Y, xs[2] - 34, BOT_Y, color=MUTED, sw=1.3))
    f.append(line(xs[2] + 34, BOT_Y, xs[3] - 34, BOT_Y, color=MUTED, sw=1.3))

    f.append(text(xs[3], BOT_Y - 52, "відновити крок 3 = S₀ ⊕ Δ₁ ⊕ Δ₂ ⊕ Δ₃", size=12, color=FIELD, bold=True))
    f.append(text(xs[3], BOT_Y + 60, "компактно в пам'яті, але", size=11, color=MUTED))
    f.append(text(xs[3], BOT_Y + 78, "відновлення коштує відтворення", size=11, color=MUTED))

    f.append(text(W / 2, 400, "Класичний обмін «пам'ять проти обчислення»: Знімок платить місцем за миттєвість, журнал — часом за компактність.",
                  size=12, color=MUTED))
    render(out("memento-vs-eventlog.svg"), W, H, *f,
           title="Порівняння двох способів повернути минуле")


if __name__ == "__main__":
    fig_interpreter_ast()
    fig_memento_roles()
    fig_memento_vs_eventlog()
    print("готово:", ", ".join(sorted(os.listdir(IMG))))
