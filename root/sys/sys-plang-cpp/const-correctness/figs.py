# -*- coding: utf-8 -*-
"""Фігури до теми «Коректність за const» (reference/cpp-standards/language)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

FREEZE_FILL = "#fdecea"
OPEN_FILL = "#eaf7ee"


# ── 1. const — властивість шляху, а не об'єкта ─────────────────────────────
def fig_const_view():
    W, H = 880, 330
    f = []

    obj, ow, oh = textbox(440, 180, ["x = 1", "звичайний об'єкт"], size=15,
                          pad=14, fill=FILL, min_w=180)
    left, lw, lh = textbox(150, 180, ["int&", "двері з правом писати"], size=14,
                           pad=12, fill=OPEN_FILL, stroke=FIELD)
    right, rw, rh = textbox(730, 180, ["const int&", "двері лише для читання"], size=14,
                            pad=12, fill=FREEZE_FILL, stroke=POS)
    f += [obj, left, right]

    # стрілки від дверей до об'єкта
    f.append(arrow(150 + lw / 2 + 10, 180, 440 - ow / 2 - 10, 180, color=FIELD))
    f.append(arrow(730 - rw / 2 - 10, 180, 440 + ow / 2 + 10, 180, color=POS))

    f.append(text(150 + lw / 2 + 10 + (440 - ow / 2 - 10 - 150 - lw / 2 - 10) / 2,
                  160, "писати можна", size=13, color=FIELD, bold=True))
    f.append(text(730 - rw / 2 - 10 - (730 - rw / 2 - 10 - 440 - ow / 2 - 10) / 2,
                  160, "писати не можна", size=13, color=POS, bold=True))

    f.append(text(440, 262, "комірка одна — прав доступу два", size=14, color=MUTED))
    f.append(text(440, 292, "const_cast повертає перші двері; сам об'єкт від цього не змінюється",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "const-view.svg"), W, H, *f,
           title="const описує двері, а не кімнату")


# ── 2. дві сторони вказівника ──────────────────────────────────────────────
def fig_pointer_sides():
    W, H = 900, 440
    f = [text(W / 2, 54, "червоним обведено те, що заморожене", size=13, color=MUTED)]

    rows = [
        ("const char* p", False, True, ["p = other;  ✓", "*p = 'X';   ✗"]),
        ("char* const q", True, False, ["q = other;  ✗", "*q = 'X';   ✓"]),
        ("const char* const s", True, True, ["s = other;  ✗", "*s = 'X';   ✗"]),
    ]

    for i, (decl, ptr_frozen, data_frozen, verdict) in enumerate(rows):
        y = 120 + i * 115
        f.append(text(24, y + 5, decl, size=15, anchor="start", bold=True))

        pb, pw, ph = textbox(300, y, "вказівник", size=13, pad=11,
                             fill=FREEZE_FILL if ptr_frozen else FILL,
                             stroke=POS if ptr_frozen else LINE,
                             sw=2 if ptr_frozen else 1.5)
        db, dw, dh = textbox(500, y, "дані", size=13, pad=11,
                             fill=FREEZE_FILL if data_frozen else FILL,
                             stroke=POS if data_frozen else LINE,
                             sw=2 if data_frozen else 1.5)
        f += [pb, db]
        f.append(arrow(300 + pw / 2 + 8, y, 500 - dw / 2 - 8, y))

        vb, vw, vh = textbox(740, y, verdict, size=14, pad=12, fill=BG, stroke=MUTED)
        f.append(vb)

    render(os.path.join(IMG, "pointer-const-sides.svg"), W, H, *f,
           title="У вказівнику дві незалежні речі: стрілка й мішень")


# ── 3. де зупиняється const у const-методі ─────────────────────────────────
def fig_method_depth():
    W, H = 900, 390
    f = []

    f.append(rect(60, 70, 460, 232, fill="#fbfcfd", stroke=LINE, sw=2))
    f.append(text(290, 102, "усередині const-методу: this → const Widget*",
                  size=13, color=MUTED))

    b1, w1, h1 = textbox(290, 162, ["v_ : std::vector<int>", "застигло разом із вмістом"],
                         size=13, pad=11, fill=FREEZE_FILL, stroke=POS, sw=2)
    b2, w2, h2 = textbox(290, 244, ["impl_ : Impl*", "застигла лише стрілка"],
                         size=13, pad=11, fill=FREEZE_FILL, stroke=POS, sw=2)
    f += [b1, b2]

    out, ow, oh = textbox(742, 244, ["Impl", "мінливий:", "const сюди не дістає"],
                          size=13, pad=12, fill=OPEN_FILL, stroke=FIELD)
    f.append(out)
    f.append(arrow(527, 244, 742 - ow / 2 - 10, 244, color=FIELD, sw=2))
    f.append(text(600, 224, "межа const", size=13, color=FIELD, bold=True))

    f.append(text(290, 340, "виняток — поле mutable: його можна міняти й у const-методі",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "const-method-depth.svg"), W, H, *f,
           title="Константність не проходить крізь вказівник")


# ── 4. хроніка появи const (вставка hist-const-origin) ─────────────────────
def fig_const_timeline():
    W = 1080
    rows = [
        ("січень 1981", ["меморандум Bell Labs «Extensions of the C Language Type Concept»:",
                         "кваліфікатори readonly і writeonly — про права доступу, не про сталі"]),
        ("1981", ["розмова з Деннісом Рітчі: кваліфікувати можна й сам вказівник",
                  "→ друга позиція, праворуч від зірочки: char* const"]),
        ("початок 1980-х", ["комітет зі стандартів C у Bell Labs (голова Ларрі Рослер) голосує:",
                            "«беремо в C — але перейменуйте на const». Компілятори не змінилися"]),
        ("1983", ["створено комітет ANSI X3J11; пропозиція const відроджується там"]),
        ("20 березня 1988", ["Рітчі публічно заперечує проти noalias і сумнівається,",
                             "що const і volatile «виправдовують свою вагу»"]),
        ("1989", ["ANSI X3.159-1989: const і volatile у стандарті C як «кваліфікатори типу»"]),
        ("і далі", ["C не бере правила «глобальний const локальний до файлу»",
                    "→ у C++ const придатний як константний вираз, у C — ні"]),
    ]
    step = 84
    y0 = 118
    H = y0 + (len(rows) - 1) * step + 90
    f = [line(238, y0 - 42, 238, y0 + (len(rows) - 1) * step + 42, color=MUTED, sw=2)]

    for i, (when, lines) in enumerate(rows):
        y = y0 + i * step
        box, bw, bh = textbox(660, y, lines, size=14, pad=13,
                              fill=FILL if i != 6 else OPEN_FILL,
                              stroke=LINE if i != 6 else FIELD, min_w=800)
        f.append(box)
        f.append(circle(238, y, 7, fill=BG, stroke=POS, sw=2.5))
        f.append(text(214, y + 5, when, size=13, anchor="end", bold=True))

    f.append(text(W / 2, H - 34,
                  "перейменування на етапі 3 змістило наголос: readonly називав право доступу, const називає сталість",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "const-timeline.svg"), W, H, *f,
           title="Від двох бітів захисту пам'яті до кваліфікатора типу")


# ── 5. конверсії константності (вставка api-const-toolbox) ─────────────────
def fig_qual_conversions():
    W, H = 1140, 510
    f = [text(W / 2, 44, "мовчазна конверсія: що компілятор зробить сам, без жодного касту",
              size=14, color=MUTED)]

    # панель А — один рівень углиб
    src1, sw1, _ = textbox(180, 112, "char*", size=16, pad=14, fill=FILL, min_w=180)
    dst1, dw1, _ = textbox(620, 112, "const char*", size=16, pad=14,
                           fill=OPEN_FILL, stroke=FIELD, sw=2, min_w=250)
    ver1, _, _ = textbox(940, 112, ["✓ можна", "один рівень —", "просто звузили права"],
                         size=13, pad=12, fill=BG, stroke=FIELD)
    f += [src1, dst1, ver1]
    f.append(arrow(180 + sw1 / 2 + 12, 112, 620 - dw1 / 2 - 12, 112, color=FIELD, sw=2.2))

    f.append(line(56, 176, W - 56, 176, color=MUTED, sw=1, dash="6 5"))

    # панель Б — два рівні углиб
    src2, sw2, _ = textbox(180, 342, "char**", size=16, pad=14, fill=FILL, min_w=180)
    f.append(src2)

    rows = [
        (250, "char* const*", True,
         ["✓ можна", "const став на рівні 1 —", "нижче нічого не змінилось"]),
        (342, "const char**", False,
         ["✗ не можна", "крізь неї відкрився б", "шлях запису в const-об'єкт"]),
        (434, "const char* const*", True,
         ["✓ можна", "const додано й на", "проміжному рівні"]),
    ]
    for y, decl, allowed, verdict in rows:
        col = FIELD if allowed else POS
        box, bw, _ = textbox(620, y, decl, size=16, pad=14, min_w=250, sw=2,
                             fill=OPEN_FILL if allowed else FREEZE_FILL, stroke=col)
        ver, _, _ = textbox(940, y, verdict, size=13, pad=12, fill=BG, stroke=col)
        f += [box, ver]
        f.append(arrow(180 + sw2 / 2 + 12, 342, 620 - bw / 2 - 12, y, color=col, sw=2.2))

    f.append(text(W / 2, 490,
                  "правило: додаєш const на глибині — постав його й на всіх проміжних рівнях",
                  size=14, color=MUTED))

    render(os.path.join(IMG, "qual-conversions.svg"), W, H, *f,
           title="Куди константність додається мовчки, а куди — ніяк")


# ── чому mutable без замка ламається на двох потоках (вставка proj-…-cache) ─
def fig_lazy_cache_race():
    W, H = 940, 500
    f = []

    f.append(text(250, 72, "Потік A — рахує й записує", size=14, bold=True))
    f.append(text(690, 72, "Потік B — читає готове", size=14, bold=True))

    f.append(text(44, 100, "час", size=12, color=MUTED))
    f.append(arrow(44, 114, 44, 412, color=MUTED, sw=1.4))

    a1, aw1, _ = textbox(250, 136, ["бачить ready_ == false",
                                    "рахує compute_summary()"], size=13, pad=12)
    a2, aw2, _ = textbox(250, 228, "запис 1: cache_ ← результат", size=13, pad=12,
                         fill=OPEN_FILL, stroke=FIELD)
    a3, aw3, _ = textbox(250, 306, "запис 2: ready_ ← true", size=13, pad=12,
                         fill=OPEN_FILL, stroke=FIELD)
    f += [a1, a2, a3]

    b1, bw1, _ = textbox(690, 260, "читає ready_ → true", size=13, pad=12)
    b2, bw2, _ = textbox(690, 338, "читає cache_ → ще порожній", size=13, pad=12,
                         fill=FREEZE_FILL, stroke=POS)
    b3, bw3, _ = textbox(690, 410, "віддає сміття", size=13, pad=12,
                         fill=FREEZE_FILL, stroke=POS, sw=2)
    f += [b1, b2, b3]

    f.append(arrow(250 + aw3 / 2 + 12, 306, 690 - bw1 / 2 - 12, 262, color=POS, sw=2))

    f.append(mtext(W / 2, 458,
                   ["Обидва записи потоку A — звичайні, незахищені. Ні компілятор, ні процесор",
                    "не зобов'язані лишати їх у написаному порядку: ready_ може лягти першим."],
                   size=13, color=MUTED))

    render(os.path.join(IMG, "lazy-cache-race.svg"), W, H, *f,
           title="Чому mutable без замка ламається на двох потоках")


# ── чотири варіанти кеша і ціна гарячого шляху (вставка proj-…-cache) ──────
def fig_lazy_cache_cost():
    W, H = 980, 400
    f = []

    cols = [(28, 286), (322, 268), (598, 176), (782, 170)]
    heads = ["варіант кеша", "що на гарячому шляху", "один потік", "кілька потоків"]
    for (x, w), h in zip(cols, heads):
        f.append(fitbox(x, 52, w, 40, h, size=13, bold=True,
                        fill="#eef1f5", stroke=MUTED))

    rows = [
        (["mutable-поле", "без синхронізації"], "читання поля",
         "~2 нс", "гонка = UB", False),
        (["mutable mutex", "на кожному виклику"], "lock + unlock",
         "~20 нс", "~125 нс і росте", True),
        (["atomic-прапорець", "+ mutex на повільному"], "acquire-читання",
         "~2 нс", "~2 нс, не росте", True),
        (["once_flag", "+ call_once"], "виклик у бібліотеку",
         "між ними", "між ними", True),
    ]

    y = 104
    for c1, c2, c3, c4, ok in rows:
        f.append(fitbox(cols[0][0], y, cols[0][1], 62, c1, size=13,
                        fill=FILL if ok else FREEZE_FILL,
                        stroke=LINE if ok else POS))
        f.append(fitbox(cols[1][0], y, cols[1][1], 62, c2, size=13,
                        fill=BG, stroke=MUTED))
        f.append(fitbox(cols[2][0], y, cols[2][1], 62, c3, size=13,
                        fill=BG, stroke=MUTED))
        f.append(fitbox(cols[3][0], y, cols[3][1], 62, c4, size=13, fill=BG,
                        stroke=MUTED if ok else POS,
                        color=INK if ok else POS))
        y += 68

    f.append(text(W / 2, 386,
                  "порядки величини для x86-64: на іншій машині зміняться числа, не сходинки",
                  size=12, color=MUTED))

    render(os.path.join(IMG, "lazy-cache-cost.svg"), W, H, *f,
           title="Ціна одного виклику word_count() на прогрітому кеші")


if __name__ == "__main__":
    fig_const_view()
    fig_pointer_sides()
    fig_method_depth()
    fig_const_timeline()
    fig_qual_conversions()
    fig_lazy_cache_race()
    fig_lazy_cache_cost()
    print("ok:", os.listdir(IMG))
