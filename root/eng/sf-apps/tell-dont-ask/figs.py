# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: «спитай-тоді-дій» проти «скажи» ───────────────────────────────
# Ліворуч: рішення (ромб) живе ЗЗОВНІ, поза об'єктом; три стрілки крізь стіну.
# Праворуч: одна стрілка-наказ; рішення сховане ВСЕРЕДИНІ об'єкта.
W, H = 900, 470
p = []

p.append(text(225, 40, "Спитай-тоді-дій", size=16, bold=True, color=POS))
p.append(text(675, 40, "Скажи", size=16, bold=True, color=FIELD))
p.append(line(450, 58, 450, H - 22, color=MUTED, sw=1.2, dash="5 6"))

# --- ЛІВА панель ---
# викликач
cl = textbox(120, 250, "викликач", size=14, bold=True, min_w=150,
             fill="#fdecea", stroke=POS)
p.append(cl[0])

# ромб-рішення поряд із викликачем (рішення ЗЗОВНІ)
dx, dy, dr = 120, 355, 42
p.append('<polygon points="%g,%g %g,%g %g,%g %g,%g" fill="#fff3f2" stroke="%s" stroke-width="1.8"/>' % (
    dx, dy - dr, dx + dr, dy, dx, dy + dr, dx - dr, dy, POS))
p.append(text(dx, dy - 4, "баланс", size=11, color=POS, bold=True))
p.append(text(dx, dy + 12, "< сума?", size=11, color=POS, bold=True))

# об'єкт-рахунок зі скляною стіною (видно нутрощі)
ox, oy, ow, oh = 250, 150, 180, 210
p.append(rect(ox, oy, ow, oh, fill="#f4f6f8", stroke=POS, sw=2))
p.append(text(ox + ow / 2, oy + 26, "Рахунок", size=15, bold=True, color=POS))
p.append(fitbox(ox + 22, oy + 46, ow - 44, 92,
                "getBalance()\nsetBalance()\n(дані назовні)", size=12,
                color=MUTED, fill="#eceff1", stroke=MUTED, sw=1))
p.append(text(ox + ow / 2, oy + oh - 16, "нутрощі відкриті", size=10,
             color=MUTED, italic=True))

# стрілка 1: викликач ПИТАЄ баланс (об'єкт -> викликач/ромб)
p.append(arrow(ox - 6, 250, cl[1] / 2 + 120 + 6, 250, color=POS))
p.append(text((ox + cl[1] / 2 + 120) / 2, 238, "1. дай баланс", size=10, color=POS))
# стрілка 2: рішення (обчислення поза об'єктом)
p.append(text(120, 300, "2. вирішує САМ", size=10, color=POS, italic=True))
# стрілка 3: викликач НАКАЗУЄ новий баланс (ромб -> об'єкт)
p.append(arrow(dx + dr + 4, 355, ox + ow / 2, oy + oh + 6, color=POS))
p.append(text(300, 400, "3. постав баланс", size=10, color=POS))

p.append(text(225, H - 10, "рішення живе ЗЗОВНІ об'єкта", size=11, color=POS))

# --- ПРАВА панель ---
cr = textbox(560, 250, "викликач", size=14, bold=True, min_w=150,
             fill="#eafaf1", stroke=FIELD)
p.append(cr[0])

# об'єкт-рахунок як чорна скринька: рішення сховане всередині
bx, by, bw, bh = 700, 150, 180, 210
p.append(rect(bx, by, bw, bh, fill="#eef7f0", stroke=FIELD, sw=2))
p.append(text(bx + bw / 2, by + 26, "Рахунок", size=15, bold=True, color=FIELD))
# ромб-рішення ВСЕРЕДИНІ
idx, idy, idr = bx + bw / 2, by + 108, 40
p.append('<polygon points="%g,%g %g,%g %g,%g %g,%g" fill="#ffffff" stroke="%s" stroke-width="1.6"/>' % (
    idx, idy - idr, idx + idr, idy, idx, idy + idr, idx - idr, idy, FIELD))
p.append(text(idx, idy - 4, "баланс", size=10, color=FIELD, bold=True))
p.append(text(idx, idy + 11, "< сума?", size=10, color=FIELD, bold=True))
p.append(text(bx + bw / 2, by + bh - 16, "рішення сховане", size=10,
             color=FIELD, italic=True))

# одна стрілка-наказ
p.append(arrow(cr[1] / 2 + 560 + 6, 250, bx - 6, 250, color=FIELD))
p.append(text((bx + cr[1] / 2 + 560) / 2, 238, "withdraw(сума)", size=11,
             color=FIELD, bold=True))

p.append(text(675, H - 10, "рішення живе ВСЕРЕДИНІ об'єкта", size=11, color=FIELD))

render(os.path.join(OUT, 'ask-then-act-vs-tell.svg'), W, H, *p)
print("wrote ask-then-act-vs-tell.svg")


# ── Фігура 2: заздрість до чужих даних — куди переселяється поведінка ────────
# Показує, що логіка, яка тягне дані одного об'єкта, має жити В ТОМУ об'єкті.
W2, H2 = 880, 400
q = []

q.append(text(W2 / 2, 38, "Куди селиться логіка", size=16, bold=True, color=INK))

# ВЕРХ: логіка в чужому домі (заздрість до даних)
# метод-викликач із трьома зверненнями до полів рахунку
mx, my, mw, mh = 60, 78, 300, 150
q.append(rect(mx, my, mw, mh, fill="#fdecea", stroke=POS, sw=1.8))
q.append(text(mx + mw / 2, my + 24, "метод оплати", size=14, bold=True, color=POS))
q.append(fitbox(mx + 20, my + 40, mw - 40, 92,
                "acc.balance\nacc.limit\nacc.balance -= сума\n(порпає ЧУЖІ поля)",
                size=12, color=INK, fill="#fff3f2", stroke=POS, sw=1))

# рахунок — голий мішок даних
ax, ay, aw, ah = 520, 78, 260, 150
q.append(rect(ax, ay, aw, ah, fill="#f4f6f8", stroke=MUTED, sw=1.5))
q.append(text(ax + aw / 2, ay + 24, "Рахунок (дані)", size=14, bold=True, color=MUTED))
q.append(fitbox(ax + 20, ay + 40, aw - 40, 92,
                "balance\nlimit\n(жодної поведінки)",
                size=12, color=MUTED, fill="#eceff1", stroke=MUTED, sw=1))

# три стрілки заздрості від методу до полів рахунку
for yy in (my + 70, my + 92, my + 114):
    q.append(arrow(mx + mw + 4, yy, ax - 4, ay + ah / 2, color=POS, sw=1.4))
# підпис над пучком стрілок (стрілки — нижче y=my+66, тож напис вище не перетне їх)
q.append(text(W2 / 2, my + 52, "тягне чужі дані", size=11, color=POS, italic=True))

# стрілка «переселення» вниз
q.append(arrow(W2 / 2, my + mh + 8, W2 / 2, my + mh + 44, color=FIELD, sw=2))
q.append(text(W2 / 2 + 12, my + mh + 30, "перенести поведінку до даних",
             size=11, color=FIELD, anchor="start"))

# НИЗ: логіка переїхала ВСЕРЕДИНУ рахунку
ry = my + mh + 60
rx, rw, rh = 300, 280, 118
q.append(rect(rx, ry, rw, rh, fill="#eef7f0", stroke=FIELD, sw=2))
q.append(text(rx + rw / 2, ry + 24, "Рахунок (поведінка)", size=14, bold=True, color=FIELD))
q.append(fitbox(rx + 20, ry + 40, rw - 40, 62,
                "withdraw(сума):\n  дані й правило — тут, разом",
                size=12, color=INK, fill="#ffffff", stroke=FIELD, sw=1))

# викликач тепер лише наказує
cx2, cy2 = 130, ry + rh / 2
cc = textbox(cx2, cy2, "викликач", size=13, bold=True, min_w=140,
             fill="#eafaf1", stroke=FIELD)
q.append(cc[0])
q.append(arrow(cx2 + cc[1] / 2 + 4, cy2, rx - 6, ry + rh / 2, color=FIELD))
q.append(text((cx2 + cc[1] / 2 + rx) / 2, cy2 - 12, "withdraw()", size=11,
             color=FIELD, bold=True))

render(os.path.join(OUT, 'behavior-follows-data.svg'), W2, H2, *q)
print("wrote behavior-follows-data.svg")


# ── Фігура 3: автомат станів замовлення — дозволені переходи як команди ──────
# Чотири стани; стрілки-переходи підписані ІМЕНАМИ КОМАНД (pay/ship/cancel).
# Зелені суцільні — дозволені; червона пунктирна — заборонений (стереже інваріант).
# Мета фігури: показати, що «кажи» = дозволені ребра цього графа живуть
# ВСЕРЕДИНІ об'єкта, а не як розсипані ззовні if-и.
W3, H3 = 900, 430
s = []

s.append(text(W3 / 2, 36, "Автомат станів замовлення", size=16, bold=True, color=INK))
s.append(text(W3 / 2, 58, "переходи — це команди об'єкта, кожна стереже свій інваріант",
              size=11, color=MUTED, italic=True))

# координати центрів станів (з великим запасом між ними)
y_top = 150
xn, xp, xsh = 130, 430, 770   # new, paid, shipped у ряд
xcanc = 430                    # cancelled — нижче, під paid
ycanc = 340

# вузли-стани
n_new = circle(xn, y_top, 46, fill="#eef2f7", stroke=MUTED, sw=2)
s.append(n_new); s.append(text(xn, y_top + 5, "NEW", size=14, bold=True, color=INK))
n_paid = circle(xp, y_top, 46, fill="#eef7f0", stroke=FIELD, sw=2)
s.append(n_paid); s.append(text(xp, y_top + 5, "PAID", size=14, bold=True, color=FIELD))
n_ship = circle(xsh, y_top, 46, fill="#eef7f0", stroke=FIELD, sw=2)
s.append(n_ship); s.append(text(xsh, y_top + 5, "SHIPPED", size=13, bold=True, color=FIELD))
n_canc = circle(xcanc, ycanc, 46, fill="#f4f6f8", stroke=MUTED, sw=2)
s.append(n_canc); s.append(text(xcanc, ycanc + 5, "CANCELLED", size=12, bold=True, color=MUTED))

# дозволені переходи (зелені суцільні), підписи — над стрілкою з запасом
s.append(arrow(xn + 48, y_top, xp - 48, y_top, color=FIELD, sw=2))
s.append(text((xn + xp) / 2, y_top - 16, "pay()", size=13, bold=True, color=FIELD))

s.append(arrow(xp + 48, y_top, xsh - 48, y_top, color=FIELD, sw=2))
s.append(text((xp + xsh) / 2, y_top - 16, "ship()", size=13, bold=True, color=FIELD))

# cancel: з NEW вниз-праворуч і з PAID вниз — обидва дозволені
s.append(arrow(xn + 20, y_top + 42, xcanc - 46, ycanc - 20, color=FIELD, sw=1.8))
s.append(arrow(xp, y_top + 48, xcanc, ycanc - 48, color=FIELD, sw=1.8))
s.append(text(xp + 60, (y_top + ycanc) / 2, "cancel()", size=13, bold=True, color=FIELD, anchor="start"))

# заборонений перехід: SHIPPED --cancel--> (червоний пунктир, перекреслений)
fx1, fy1 = xsh, y_top + 48
fx2, fy2 = xcanc + 60, ycanc - 46
s.append(line(fx1, fy1, fx2, fy2, color=POS, sw=1.8, dash="6 6"))
# косий хрестик поперек забороненого ребра
mxf, myf = (fx1 + fx2) / 2, (fy1 + fy2) / 2
s.append(line(mxf - 11, myf - 11, mxf + 11, myf + 11, color=POS, sw=2.4))
s.append(line(mxf - 11, myf + 11, mxf + 11, myf - 11, color=POS, sw=2.4))
s.append(text(xsh - 6, ycanc - 4, "cancel() → виняток", size=11, bold=True, color=POS, anchor="end"))

# легенда праворуч унизу, у власній рамці — не перетинає граф
lg = textbox(150, ycanc + 6, "дозволено\nзаборонено (кидає)", size=11,
             min_w=170, fill="#ffffff", stroke=MUTED)
s.append(lg[0])
s.append(circle(150 - 74, ycanc - 6, 6, fill=FIELD, stroke=FIELD, sw=1))
s.append(circle(150 - 74, ycanc + 14, 6, fill=POS, stroke=POS, sw=1))

render(os.path.join(OUT, 'order-state-machine.svg'), W3, H3, *s)
print("wrote order-state-machine.svg")


# ── Фігура 3 (для вставки hist): родовід гасла — три сходинки ────────────────
# Sharp 1997 (спостереження) → Hunt/Thomas 1998 (гасло+популяризація) →
# Fowler 2013 (канон+стриманість). Одна вісь часу, три картки, різні ролі.
W3, H3 = 940, 430
r = []

r.append(text(W3 / 2, 40, "Родовід «Tell, Don't Ask»", size=17, bold=True, color=INK))

# горизонтальна вісь часу
axis_y = 120
r.append(line(70, axis_y, W3 - 70, axis_y, color=MUTED, sw=2))
r.append(arrow(W3 - 74, axis_y, W3 - 60, axis_y, color=MUTED, sw=2))
r.append(text(W3 - 66, axis_y - 12, "час", size=11, color=MUTED, anchor="end", italic=True))

# три вузли на осі
cols = [
    (200, "1997", "Алек Шарп\n(Alec Sharp)", "Smalltalk by Example",
     "спостереження", "«Процедурний код здобуває\nінформацію, тоді ухвалює\nрішення; об'єктний — каже\nоб'єктам щось зробити»", MUTED),
    (470, "1998", "Гант і Томас\n(Hunt & Thomas)", "toolshed.com · IEEE Software",
     "гасло + розголос", "Дали ім'я «Tell, Don't Ask»\nі рознесли принцип;\nдодали думку про\nінваріанти класу", POS),
    (740, "2013", "Мартін Фаулер\n(Martin Fowler)", "martinfowler.com/bliki",
     "канон + стриманість", "«Особисто я tell-dont-ask\nне вживаю»; сходинка до\nспіврозташування, не догма;\nстереже від GetterEradicators", FIELD),
]

for cx, year, who, src, role, quote, col in cols:
    # вузол на осі
    r.append(circle(cx, axis_y, 9, fill="#ffffff", stroke=col, sw=2.5))
    r.append(text(cx, axis_y - 20, year, size=15, bold=True, color=col))
    # стовпчик від осі до картки
    card_top = axis_y + 40
    r.append(line(cx, axis_y + 10, cx, card_top, color=col, sw=1.4, dash="4 5"))
    # картка ролі
    cw, ch = 250, 210
    cxl = cx - cw / 2
    r.append(rect(cxl, card_top, cw, ch, fill="#ffffff", stroke=col, sw=1.8))
    r.append(mtext(cx, card_top + 24, who.split("\n"), size=13, color=INK, bold=True, lh=1.2))
    r.append(text(cx, card_top + 62, src, size=10, color=MUTED, italic=True))
    # плашка ролі
    rw = text_width(role, 11, True) + 20
    r.append(rect(cx - rw / 2, card_top + 74, rw, 22, fill=col, stroke=col, sw=1, rx=11))
    r.append(text(cx, card_top + 89, role, size=11, color="#ffffff", bold=True))
    # цитата/суть
    r.append(mtext(cx, card_top + 122, quote.split("\n"), size=10.5, color=INK, lh=1.3))

# підпис-нитка внизу: ідея → гасло → зважений канон
r.append(text(W3 / 2, H3 - 14,
              "спостереження  →  гасло й розголос  →  зважений канон із застереженнями",
              size=11, color=MUTED, italic=True))

render(os.path.join(OUT, 'tell-dont-ask-lineage.svg'), W3, H3, *r)
print("wrote tell-dont-ask-lineage.svg")
