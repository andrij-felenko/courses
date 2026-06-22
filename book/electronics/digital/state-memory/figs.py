# -*- coding: utf-8 -*-
"""Фігури до теми «Пам'ять стану» та вставки про тригер Екклза–Джордана.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

HOT = POS    # «1», гаряче — червоний
LOW = NEG    # «0», холодне — синій
OK  = FIELD  # зелене виділення / висновок


# ── helper: інвертор (трикутник + кружок інверсії), вістрям праворуч ─────────
def inverter(x, y, w=40, h=30, fill=FILL, stroke=INK, sw=2):
    """(x,y) — лівий-верхній кут трикутника; повертає (svg, x_out, y_mid)."""
    ym = y + h / 2
    tri = ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s" stroke="%s" '
           'stroke-width="%.1f"/>' % (x, y, x, y + h, x + w, ym, fill, stroke, sw))
    bub = circle(x + w + 6, ym, 6, fill=BG, stroke=stroke, sw=sw)
    return tri + bub, x + w + 12, ym


def dot(cx, cy, r=3.2):
    return circle(cx, cy, r, fill=INK, stroke=INK, sw=1)


# ── 1. Комбінаційна логіка не пам'ятає ──────────────────────────────────────
def fig_no_memory():
    W, H = 760, 330
    f = [text(W / 2, 30, "Комбінаційна логіка не вміє пам'ятати", size=18, bold=True),
         text(W / 2, 52, "її вихід — це функція лише входів зараз; сліду минулого в ній не лишається",
              size=12.5, color=MUTED, italic=True)]
    # коробка комбінаційної логіки
    bx, by, bw, bh = 110, 110, 230, 120
    f.append(rect(bx, by, bw, bh, fill="#eef4ff", stroke=INK, sw=2))
    f.append(mtext(bx + bw / 2, by + bh / 2 - 4, ["комбінаційна", "логіка"],
                   size=15, bold=True))
    # вхід / вихід
    f.append(line(bx - 50, by + bh / 2, bx, by + bh / 2, color=INK, sw=1.8))
    f.append(text(bx - 56, by + bh / 2 + 4, "вхід", size=12.5, color=INK, anchor="end", bold=True))
    f.append(line(bx + bw, by + bh / 2, bx + bw + 50, by + bh / 2, color=INK, sw=1.8))
    f.append(text(bx + bw + 56, by + bh / 2 + 4, "вихід = f(вхід зараз)",
                  size=12.5, color=OK, anchor="start", bold=True))
    f.append(text(bx + bw / 2, by + bh + 26, "немає шляху від «що було раніше»",
                  size=11.5, color=MUTED, italic=True))
    # рамка «чого не може»
    nb = fitbox(470, 108, 250, 124,
                "Чого вона не може:\n• «чи натискали кнопку?»\n• «це вже третій імпульс?»\n• утримати рівень після\n   зникнення сигналу",
                size=12, fill="#fdecea", stroke=HOT, sw=1.6)
    f.append(nb)
    f.append(text(W / 2, 312, "Щоб пам'ятати, схемі потрібен стан — і спосіб тримати його між подіями.",
                  size=12.5, bold=True))
    render(os.path.join(IMG, "no-memory.svg"), W, H, *f)


# ── 2. Загальна модель: логіка + зворотний зв'язок = стан ────────────────────
def fig_seq_model():
    W, H = 760, 400
    f = [text(W / 2, 30, "Комбінаційна логіка + зворотний зв'язок = стан", size=18, bold=True),
         text(W / 2, 52, "частину виходу заводять назад як стан — вихід тепер залежить і від входів, і від минулого",
              size=12, color=MUTED, italic=True)]
    bx, by, bw, bh = 270, 100, 220, 110
    f.append(rect(bx, by, bw, bh, fill="#eef4ff", stroke=INK, sw=2))
    f.append(text(bx + bw / 2, by + 46, "комбінаційна логіка", size=13.5, bold=True))
    f.append(text(bx + bw / 2, by + 68, "(вентилі без петель)", size=10.5, color=MUTED))
    # входи
    f.append(line(bx - 110, by + 30, bx, by + 30, color=INK, sw=1.8))
    f.append(text(bx - 116, by + 34, "входи", size=12, color=INK, anchor="end", bold=True))
    # виходи
    f.append(line(bx + bw, by + 30, bx + bw + 90, by + 30, color=INK, sw=1.8))
    f.append(text(bx + bw + 96, by + 34, "виходи", size=12, color=OK, anchor="start", bold=True))
    # наступний стан праворуч → вниз
    f.append(text(bx + bw + 60, by + bh - 6, "наступний стан", size=10, color=MUTED))
    f.append(line(bx + bw, by + bh - 22, bx + bw + 120, by + bh - 22, color=INK, sw=1.8))
    f.append(line(bx + bw + 120, by + bh - 22, bx + bw + 120, 300, color=INK, sw=1.8))
    # коробка пам'яті
    mbx, mby, mbw, mbh = bx + bw / 2 - 70, 280, 140, 44
    f.append(rect(mbx, mby, mbw, mbh, fill="#eef7ee", stroke=OK, sw=2))
    f.append(text(mbx + mbw / 2, mby + 27, "пам'ять стану", size=12.5, color=OK, bold=True))
    # назад до пам'яті й у логіку
    f.append(line(bx + bw + 120, 300, mbx + mbw, 300, color=INK, sw=1.8))
    f.append(line(mbx, 300, bx - 70, 300, color=INK, sw=1.8))
    f.append(line(bx - 70, 300, bx - 70, by + bh - 22, color=INK, sw=1.8))
    f.append(arrow(bx - 70, by + bh - 22, bx, by + bh - 22, color=INK, sw=1.8))
    f.append(text(bx - 70, by + bh - 30, "поточний стан", size=10, color=MUTED))
    # підсумок
    sb = fitbox(60, 350, 640, 38,
                "вихід = f(входи, стан)   ·   наступний стан = g(входи, стан) — кістяк усіх схем з пам'яттю",
                size=12.5, fill="#f4f7f4", stroke=OK, sw=1.6, bold=True)
    f.append(sb)
    render(os.path.join(IMG, "seq-model.svg"), W, H, *f)


# ── 3. Парна vs непарна кількість інверсій у петлі ──────────────────────────
def fig_odd_even():
    W, H = 820, 410
    f = [text(W / 2, 30, "Парність інверсій у петлі вирішує: тримати стан чи коливатися", size=17, bold=True),
         text(W / 2, 52, "один інвертор у петлі осідає біля порога; кільце з 3+ інверторів коливається; два інвертори дають два стійкі стани",
              size=11.5, color=MUTED, italic=True)]
    # ── ліва панель: один інвертор (непарна) ──
    lx, ly, lw, lh = 40, 78, 360, 300
    f.append(rect(lx, ly, lw, lh, fill=BG, stroke="#e2e6ea", sw=1.5))
    f.append(text(lx + lw / 2, ly + 26, "1 інвертор (непарна) → нема стійкого стану",
                  size=12.5, color=HOT, bold=True))
    # інвертор + петля
    isvg, ix_out, iym = inverter(lx + 130, 150, 44, 32)
    f.append(line(lx + 90, 166, lx + 130, 166, color=INK, sw=1.8))
    f.append(isvg)
    f.append(line(ix_out, iym, lx + 250, iym, color=INK, sw=1.6))
    f.append(line(lx + 250, iym, lx + 250, 126, color=INK, sw=1.6))
    f.append(line(lx + 250, 126, lx + 70, 126, color=INK, sw=1.6))
    f.append(line(lx + 70, 126, lx + 70, 166, color=INK, sw=1.6))
    f.append(arrow(lx + 70, 166, lx + 90, 166, color=INK, sw=1.6))
    f.append(text(lx + 160, 120, "вихід → вхід", size=10, color=MUTED))
    f.append(text(lx + lw / 2, 220, "вихід = вхід → застрягає коло порога,",
                  size=11, color=INK, italic=True))
    f.append(text(lx + lw / 2, 238, "поводиться як підсилювач, а не пам'ять",
                  size=11, color=INK, italic=True))
    f.append(text(lx + lw / 2, 300, "чисте коливання дає лише непарне", size=11, color=HOT))
    f.append(text(lx + lw / 2, 318, "кільце з 3 і більше інверторів", size=11, color=HOT, bold=True))
    f.append(text(lx + lw / 2, 350, "(кільцевий генератор)", size=11, color=MUTED, italic=True))
    # ── права панель: два інвертори (парна) ──
    rx, ry, rw, rh = 420, 78, 360, 300
    f.append(rect(rx, ry, rw, rh, fill=BG, stroke="#e2e6ea", sw=1.5))
    f.append(text(rx + rw / 2, ry + 26, "2 інвертори (парна) → два стійкі стани",
                  size=12.5, color=OK, bold=True))
    # два інвертори навхрест
    i1, o1x, o1y = inverter(rx + 110, 150, 44, 30)
    i2, o2x, o2y = inverter(rx + 110, 210, 44, 30)
    f.append(i1); f.append(i2)
    # виходи + вузли
    f.append(line(o1x, o1y, rx + 200, o1y, color=INK, sw=1.8))
    f.append(line(o2x, o2y, rx + 200, o2y, color=INK, sw=1.8))
    f.append(dot(rx + 200, o1y)); f.append(dot(rx + 200, o2y))
    f.append(text(rx + 210, o1y + 4, "Q=1", size=12, color=HOT, anchor="start", bold=True))
    f.append(text(rx + 210, o2y + 4, "Q̄=0", size=12, color=LOW, anchor="start", bold=True))
    # перехресні дроти
    f.append(line(rx + 200, o1y, rx + 200, 126, color=INK, sw=1.4))
    f.append(line(rx + 200, 126, rx + 92, 126, color=INK, sw=1.4))
    f.append(line(rx + 92, 126, rx + 92, o2y, color=INK, sw=1.4))
    f.append(line(rx + 92, o2y, rx + 110, o2y, color=INK, sw=1.4))
    f.append(line(rx + 200, o2y, rx + 200, 264, color=INK, sw=1.4))
    f.append(line(rx + 200, 264, rx + 78, 264, color=INK, sw=1.4))
    f.append(line(rx + 78, 264, rx + 78, o1y, color=INK, sw=1.4))
    f.append(line(rx + 78, o1y, rx + 110, o1y, color=INK, sw=1.4))
    f.append(text(rx + rw / 2, 300, "Q=1 тримає Q̄=0, а Q̄=0 тримає Q=1 — узгоджено",
                  size=11, color=INK, italic=True))
    f.append(text(rx + rw / 2, 322, "(і дзеркальний стан так само стійкий)", size=11, color=MUTED, italic=True))
    f.append(text(rx + rw / 2, 352, "стабільно: тримає 1 біт", size=12, color=OK, bold=True))
    render(os.path.join(IMG, "odd-even.svg"), W, H, *f)


# ── 4. Бістабільна комірка тримає рівень у часі ─────────────────────────────
def fig_holds():
    W, H = 800, 320
    f = [text(W / 2, 30, "Тримає рівень у часі, доки його не перекинуть", size=18, bold=True),
         text(W / 2, 52, "без сигналу вихід Q лежить незмінно; короткий поштовх перекидає його — і він знову лежить",
              size=12, color=MUTED, italic=True)]
    x0, x1 = 110, 760
    yhi, ylo = 110, 210
    f.append(text(x0 - 36, (yhi + ylo) / 2 + 4, "Q", size=14, bold=True, anchor="end"))
    f.append(line(x0, yhi, x1, yhi, color="#e2e6ea", sw=1))
    f.append(line(x0, ylo, x1, ylo, color="#e2e6ea", sw=1))
    f.append(text(x0 - 8, yhi + 4, "1", size=10.5, color=HOT, anchor="end"))
    f.append(text(x0 - 8, ylo + 4, "0", size=10.5, color=LOW, anchor="end"))
    # хвиля Q: 0 до set, 1 до reset, 0 далі
    xs, xr = 300, 560
    f.append('<polyline points="%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" '
             'fill="none" stroke="%s" stroke-width="2.6"/>'
             % (x0, ylo, xs, ylo, xs, yhi, xr, yhi, xr, ylo, x1, ylo, OK))
    # поштовхи
    for x, lab in ((xs, "set →1"), (xr, "reset →0")):
        f.append(line(x, 290, x, 250, color=HOT, sw=2))
        f.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
                 % (x - 5, 252, x + 5, 252, x, 244, HOT))
        f.append(text(x, 305, lab, size=11, color=HOT, bold=True))
    f.append(text((x0 + xs) / 2, ylo - 8, "тримає 0", size=11, color=MUTED, italic=True))
    f.append(text((xs + xr) / 2, yhi - 8, "тримає 1 (хоч поштовх давно зник)", size=11, color=MUTED, italic=True))
    f.append(text((xr + x1) / 2, ylo - 8, "знову тримає 0", size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "holds.svg"), W, H, *f)


# ── 5. Пам'ять на тригерах тримається живленням (енергозалежність) ──────────
def fig_volatile():
    W, H = 760, 300
    f = [text(W / 2, 30, "Така пам'ять тримається живленням", size=18, bold=True),
         text(W / 2, 52, "петля підкріплює себе, лише поки тече струм; зникло живлення — біт забуто",
              size=12, color=MUTED, italic=True)]
    # ліва: живлення є
    lx, ly, lw, lh = 90, 92, 250, 120
    f.append(rect(lx, ly, lw, lh, fill="#eef7ee", stroke=OK, sw=2))
    f.append(text(lx + lw / 2, ly + 42, "живлення є", size=13.5, color=OK, bold=True))
    f.append(text(lx + lw / 2, ly + 68, "Q = 1 (тримається)", size=12.5, color=HOT, bold=True))
    f.append(text(lx + lw / 2, ly + 94, "петля підкріплює себе", size=10.5, color=MUTED, italic=True))
    # стрілка «вимк.»
    f.append(arrow(lx + lw, ly + lh / 2, lx + lw + 70, ly + lh / 2, color=INK, sw=2.4))
    f.append(text(lx + lw + 35, ly + lh / 2 - 10, "вимк.", size=11, color=HOT, bold=True))
    # права: живлення нема
    rx = lx + lw + 70
    f.append(rect(rx, ly, lw, lh, fill="#f1f1f1", stroke=MUTED, sw=2))
    f.append(text(rx + lw / 2, ly + 42, "живлення нема", size=13.5, color=MUTED, bold=True))
    f.append(text(rx + lw / 2, ly + 68, "Q = ?  (забуто)", size=12.5, color=MUTED, bold=True))
    f.append(text(rx + lw / 2, ly + 94, "петля розірвана", size=10.5, color=MUTED, italic=True))
    f.append(text(W / 2, 268, "Тому пам'ять на тригерах (регістри, кеш, SRAM) звуть енергозалежною: без струму губить усе.",
                  size=12, bold=True))
    render(os.path.join(IMG, "volatile.svg"), W, H, *f)


# ════════════════ ВСТАВКА: тригер Екклза–Джордана ═══════════════════════════

# ── 6. Ланцюг питань: як схема навчилася пам'ятати (часова лінія) ────────────
def fig_timeline():
    W, H = 820, 560
    f = [text(W / 2, 32, "Ланцюг питань: як схема навчилася пам'ятати", size=18, bold=True),
         text(W / 2, 54, "майже вся фізика «забуває», скочуючись у рівновагу; пам'ять — навмисна, стійка непокора цьому",
              size=11.5, color=MUTED, italic=True)]
    ax = 220
    f.append(line(ax, 90, ax, 530, color=MUTED, sw=3))
    nodes = [
        ("прадавнє", "питання", "Як зробити, щоб схема тримала обраний стан, а не «розслаблялась»?", False),
        ("1900-ті", "реле-засувка", "Телефонні станції: реле тримає себе власним контактом — механічна пам'ять", False),
        ("1918", "Екклз і Джордан", "Дві перехресно-зв'язані лампи → два стійкі стани: перша електронна комірка пам'яті", True),
        ("1930-ті", "назва «фліп-флоп»", "За клацанням, з яким схема перекидається між станами", False),
        ("1940-ві", "ENIAC", "Тисячі лампових тригерів = регістри й лічильники першого комп'ютера", False),
        ("1947 →", "транзистор → кремній", "Та сама перехресна петля, але крихітна: SRAM, регістри", False),
        ("тепер", "кожен біт пам'яті", "Регістр, кеш, комірка SRAM — прямий нащадок схеми 1918 року", False),
    ]
    y = 120
    dy = 68
    for when, title, desc, hot in nodes:
        col = HOT if hot else INK
        if hot:
            f.append(circle(ax, y, 10, fill=BG, stroke=HOT, sw=3.2))
            f.append(circle(ax, y, 4.5, fill=HOT, stroke=HOT, sw=1))
        else:
            f.append(circle(ax, y, 7, fill=BG, stroke=INK, sw=2.6))
        f.append(text(ax - 22, y + 5, when, size=12, color=MUTED, anchor="end", bold=True))
        f.append(text(ax + 24, y - 4, title, size=14.5, color=col, anchor="start", bold=True))
        f.append(text(ax + 24, y + 15, desc, size=11.5, color=INK, anchor="start", italic=True))
        y += dy
    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


# ── 7. Перехресний зв'язок робить два стійкі стани ──────────────────────────
def fig_crosscoupled():
    W, H = 820, 380
    f = [text(W / 2, 30, "Перехресний зв'язок робить два стійкі стани", size=18, bold=True),
         text(W / 2, 52, "вихід кожного елемента живить вхід іншого — петля сама себе підтримує",
              size=12, color=MUTED, italic=True)]
    # схема навхрест зліва
    bx = 250
    i1, o1x, o1y = inverter(bx, 150, 44, 30)
    i2, o2x, o2y = inverter(bx, 210, 44, 30)
    f.append(i1); f.append(i2)
    f.append(line(o1x, o1y, bx + 90, o1y, color=INK, sw=1.8))
    f.append(line(o2x, o2y, bx + 90, o2y, color=INK, sw=1.8))
    f.append(dot(bx + 90, o1y)); f.append(dot(bx + 90, o2y))
    f.append(text(bx + 100, o1y + 4, "Q=1", size=12, color=HOT, anchor="start", bold=True))
    f.append(text(bx + 100, o2y + 4, "Q̄=0", size=12, color=LOW, anchor="start", bold=True))
    f.append(line(bx + 90, o1y, bx + 90, 126, color=INK, sw=1.4))
    f.append(line(bx + 90, 126, bx - 18, 126, color=INK, sw=1.4))
    f.append(line(bx - 18, 126, bx - 18, o2y, color=INK, sw=1.4))
    f.append(line(bx - 18, o2y, bx, o2y, color=INK, sw=1.4))
    f.append(line(bx + 90, o2y, bx + 90, 264, color=INK, sw=1.4))
    f.append(line(bx + 90, 264, bx - 32, 264, color=INK, sw=1.4))
    f.append(line(bx - 32, 264, bx - 32, o1y, color=INK, sw=1.4))
    f.append(line(bx - 32, o1y, bx, o1y, color=INK, sw=1.4))
    f.append(text(bx + 22, 300, "два інвертори, з'єднані навхрест", size=11.5, bold=True))
    # рамка зі станами
    sb = fitbox(540, 100, 250, 170,
                "Два стійкі стани:\nстан «1»:  Q=1, Q̄=0\nстан «0»:  Q=0, Q̄=1\nкожен сам себе тримає —\nзамкнене коло, що «застрягло»",
                size=12, fill="#f4f7f4", stroke=OK, sw=1.6)
    f.append(sb)
    f.append(text(W / 2, 352, "Це й є 1 біт: схема не скочується в одну рівновагу — вона має дві й тримає обрану.",
                  size=12, bold=True))
    render(os.path.join(IMG, "crosscoupled.svg"), W, H, *f)


# ── 8. Інтуїція: кулька у двох ямах (бістабільність) ────────────────────────
def fig_bistable():
    W, H = 760, 380
    f = [text(W / 2, 30, "Кулька у двох ямах: дві рівноваги замість однієї", size=18, bold=True),
         text(W / 2, 52, "між ямами — горбок; кулька лишається у своїй ямі, доки її не штовхнути через бар'єр",
              size=12, color=MUTED, italic=True)]
    # крива W: дві ями + горб (двоямний профіль)
    import math
    x0, x1 = 110, 650
    ybase, amp = 290, 70
    pts = []
    N = 120
    for k in range(N + 1):
        t = k / N
        xx = x0 + t * (x1 - x0)
        u = (t - 0.5) * 2.0          # u ∈ [-1,1]
        # двоямний профіль: мінімуми біля u=±0.6, локальний максимум при u=0
        val = (u ** 4 - 0.9 * u ** 2)
        yy = ybase - amp * (1.6 - val * 2.4)
        pts.append((xx, yy))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, INK))
    # дно ям ≈ u=±0.6 → t=0.2 та 0.8
    def at(t):
        i = int(round(t * N))
        return pts[i]
    wx0, wy0 = at(0.205); wx1, wy1 = at(0.795)
    f.append(circle(wx0, wy0 - 12, 12, fill="#eaf0fd", stroke=LOW, sw=2.4))
    f.append(text(wx0, wy0 - 8, "0", size=13, color=LOW, bold=True))
    f.append(text(wx0, wy0 + 34, "стан «0»", size=12, color=LOW, bold=True))
    f.append(circle(wx1, wy1 - 12, 12, fill="#fdecea", stroke=HOT, sw=2.4))
    f.append(text(wx1, wy1 - 8, "1", size=13, color=HOT, bold=True))
    f.append(text(wx1, wy1 + 34, "стан «1»", size=12, color=HOT, bold=True))
    # горб + стрілка-поштовх
    hx, hy = at(0.5)
    f.append(text(hx, hy - 14, "бар'єр", size=11, color=MUTED, italic=True))
    f.append(arrow(wx0 + 26, 130, wx1 - 26, 130, color=OK, sw=2))
    f.append(text(W / 2 - 25, 122, "«поштовх» (тригер) перекидає через горб",
                  size=11.5, color=OK, bold=True, anchor="middle"))
    # підсумок
    sb = fitbox(60, 338, 640, 36,
                "Комбінаційна схема має одну рівновагу; тригер навмисно має дві — тому й пам'ятає, у якій його лишили.",
                size=12, fill="#f4f7f4", stroke=OK, sw=1.6, bold=True)
    f.append(sb)
    render(os.path.join(IMG, "bistable.svg"), W, H, *f)


# ── 9. Та сама ідея крізь технології: лампи 1918 → кремній ──────────────────
def fig_tubes_to_gates():
    W, H = 820, 400
    f = [text(W / 2, 30, "Та сама ідея крізь технології: лампи 1918 → кремній сьогодні", size=17, bold=True),
         text(W / 2, 52, "перехресний зв'язок незмінний; змінюється лише, чим його роблять — лампою, транзистором, вентилем",
              size=11.5, color=MUTED, italic=True)]
    # ── ліва панель: дві лампи навхрест (умовно) ──
    lx, ly, lw, lh = 40, 84, 360, 250
    f.append(rect(lx, ly, lw, lh, fill=BG, stroke="#e2e6ea", sw=1.5))
    f.append(text(lx + lw / 2, ly + 26, "Екклз–Джордан, 1918", size=13.5, bold=True))
    # шина живлення
    f.append(line(lx + 60, 138, lx + 300, 138, color=HOT, sw=2))
    f.append(text(lx + 50, 142, "+V", size=10.5, color=HOT, anchor="end", bold=True))
    # дві «лампи» = кружки з анодом/сіткою/катодом
    for cx in (lx + 110, lx + 250):
        f.append(circle(cx, 210, 26, fill=FILL, stroke=INK, sw=2))
        f.append(line(cx - 11, 200, cx + 11, 200, color=INK, sw=2.4))      # анод
        f.append(line(cx, 200, cx, 172, color=INK, sw=1.6))
        f.append(line(cx, 172, cx, 138, color=INK, sw=1.6))                 # до +V
        f.append(line(cx - 13, 211, cx + 13, 211, color=INK, sw=1.4, dash="3 3"))  # сітка
        f.append(line(cx + 13, 211, cx + 24, 211, color=INK, sw=1.6))
        f.append(line(cx - 8, 219, cx, 225, color=INK, sw=2.2))             # катод (V)
        f.append(line(cx, 225, cx + 8, 219, color=INK, sw=2.2))
        f.append(line(cx, 225, cx, 250, color=INK, sw=1.6))
    # перехресні з'єднання анод↔сітка (умовно, пунктир)
    f.append(line(lx + 134, 211, lx + 226, 240, color=INK, sw=1.4, dash="4 3"))
    f.append(line(lx + 226, 211, lx + 134, 240, color=INK, sw=1.4, dash="4 3"))
    f.append(text(lx + 110, 282, "лампа A", size=10.5))
    f.append(text(lx + 250, 282, "лампа B", size=10.5))
    f.append(text(lx + lw / 2, 314, "дві тріоди навхрест → два стани", size=11, color=MUTED, italic=True))
    # ── права панель: пара вентилів навхрест ──
    rx, ry, rw, rh = 420, 84, 360, 250
    f.append(rect(rx, ry, rw, rh, fill=BG, stroke="#e2e6ea", sw=1.5))
    f.append(text(rx + rw / 2, ry + 26, "Сьогодні: пара вентилів у кремнії", size=13, bold=True))
    bx = rx + 130
    i1, o1x, o1y = inverter(bx, 168, 44, 30)
    i2, o2x, o2y = inverter(bx, 228, 44, 30)
    f.append(i1); f.append(i2)
    f.append(line(o1x, o1y, bx + 90, o1y, color=INK, sw=1.8))
    f.append(line(o2x, o2y, bx + 90, o2y, color=INK, sw=1.8))
    f.append(dot(bx + 90, o1y)); f.append(dot(bx + 90, o2y))
    f.append(text(bx + 100, o1y + 4, "Q=1", size=12, color=HOT, anchor="start", bold=True))
    f.append(text(bx + 100, o2y + 4, "Q̄=0", size=12, color=LOW, anchor="start", bold=True))
    f.append(line(bx + 90, o1y, bx + 90, 144, color=INK, sw=1.4))
    f.append(line(bx + 90, 144, bx - 18, 144, color=INK, sw=1.4))
    f.append(line(bx - 18, 144, bx - 18, o2y, color=INK, sw=1.4))
    f.append(line(bx - 18, o2y, bx, o2y, color=INK, sw=1.4))
    f.append(line(bx + 90, o2y, bx + 90, 282, color=INK, sw=1.4))
    f.append(line(bx + 90, 282, bx - 32, 282, color=INK, sw=1.4))
    f.append(line(bx - 32, 282, bx - 32, o1y, color=INK, sw=1.4))
    f.append(line(bx - 32, o1y, bx, o1y, color=INK, sw=1.4))
    f.append(text(rx + rw / 2, 314, "та сама перехресна петля — у кремнії", size=11, color=MUTED, italic=True))
    f.append(text(W / 2, 372, "Лампа згоріла в історії, ідея — ні: кожна комірка SRAM — це Екклз–Джордан у мініатюрі.",
                  size=12, bold=True))
    render(os.path.join(IMG, "tubes-to-gates.svg"), W, H, *f)


if __name__ == "__main__":
    fig_no_memory()
    fig_seq_model()
    fig_odd_even()
    fig_holds()
    fig_volatile()
    fig_timeline()
    fig_crosscoupled()
    fig_bistable()
    fig_tubes_to_gates()
    print("OK figs.py -> img/")
