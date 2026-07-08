# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Телескопічний конструктор проти будівельника ────────────────────────────
def fig_telescoping_vs_builder():
    W, H = 1200, 660
    frags = []

    # роздільник посередині
    frags.append(line(W / 2, 88, W / 2, H - 30, color="#d0d5db", sw=1.2, dash="6,6"))

    # ═══════════ ЛІВОРУЧ: ТЕЛЕСКОП ═══════════
    lcx = W / 4
    frags.append(text(lcx, 50, "Телескопічний конструктор", size=16, bold=True, color=POS))
    frags.append(text(lcx, 72, "щоразу довший список у дужках", size=12, color=MUTED))

    # стос перевантажень, що росте
    overloads = [
        "Pizza(size)",
        "Pizza(size, cheese)",
        "Pizza(size, cheese, olives)",
        "Pizza(size, cheese, olives, bacon)",
    ]
    oy = 116
    for i, s in enumerate(overloads):
        y = oy + i * 52
        w = 190 + i * 66
        frags.append(rect(lcx - w / 2, y, w, 38, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
        frags.append(text(lcx, y + 24, s, size=12.5, color=INK))

    # проблемний виклик з голими аргументами
    call_y = oy + 4 * 52 + 14
    frags.append(fitbox(lcx - 250, call_y, 500, 62,
                        'new Pizza(30, true, false, true)\n'
                        'що true? що false? — на око не скажеш',
                        size=13, fill=FILL, stroke=LINE, sw=1.4, pad=12))
    frags.append(text(lcx, call_y + 92,
                     "порядок і зміст аргументів — у голові", size=12, bold=True, color=POS))

    # ═══════════ ПРАВОРУЧ: БУДІВЕЛЬНИК ═══════════
    rcx = 3 * W / 4
    frags.append(text(rcx, 50, "Будівельник", size=16, bold=True, color=FIELD))
    frags.append(text(rcx, 72, "названі кроки, тоді один build()", size=12, color=MUTED))

    steps = [
        ".size(30)",
        ".cheese()",
        ".bacon()",
    ]
    sy = 132
    for i, s in enumerate(steps):
        y = sy + i * 60
        frags.append(rect(rcx - 130, y, 260, 40, fill="#eef8f2", stroke=FIELD, sw=1.5, rx=6))
        frags.append(text(rcx, y + 26, s, size=13, bold=True, color=INK))
        if i < len(steps) - 1:
            frags.append(arrow(rcx, y + 40, rcx, y + 60, color=FIELD, sw=1.5))

    # build() віддає готовий продукт
    build_y = sy + 3 * 60 + 6
    frags.append(arrow(rcx, build_y - 6, rcx, build_y + 14, color=FIELD, sw=1.6))
    b, _, _ = textbox(rcx, build_y + 40, ".build()  →  Pizza", size=13, bold=True,
                      fill="#e8f6ee", stroke=FIELD, sw=1.8, min_w=260)
    frags.append(b)
    frags.append(text(rcx, build_y + 96,
                     "кожен крок сам себе називає", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, 'telescoping-vs-builder.svg'), W, H, *frags)


# ── Ролі GoF: Директор жене абстрактного Будівельника, два продукти ─────────
def fig_builder_roles():
    W, H = 1180, 640
    frags = []

    frags.append(text(W / 2, 40, "Той самий процес — різні представлення",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 62, "Директор диктує кроки; хто їх виконує — підставляють",
                      size=12.5, color=MUTED))

    # Директор ліворуч
    dir_cx = W * 0.16
    dir_cy = 200
    d, dw, dh = textbox(dir_cx, dir_cy,
                        ["Директор", "construct():", "  addWalls()", "  addRoof()", "  addDoor()"],
                        size=12.5, bold=True, fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=190)
    frags.append(d)
    frags.append(text(dir_cx, dir_cy + dh / 2 + 26,
                     "знає ПОРЯДОК кроків,", size=11.5, color=INK))
    frags.append(text(dir_cx, dir_cy + dh / 2 + 44,
                     "не знає матеріалу", size=11.5, color=INK))

    # Абстрактний будівельник посередині
    ab_cx = W * 0.46
    ab_cy = 200
    ab, aw, ah = textbox(ab_cx, ab_cy,
                         ["«Будівельник»", "addWalls()", "addRoof()", "addDoor()", "getResult()"],
                         size=12.5, bold=True, fill=FILL, stroke=LINE, sw=1.7, min_w=190)
    frags.append(ab)
    frags.append(text(ab_cx, ab_cy - ah / 2 - 14, "інтерфейс кроків", size=11.5, color=MUTED))

    # стрілка Директор → інтерфейс (жене кроки), повз написи
    frags.append(arrow(dir_cx + dw / 2, dir_cy, ab_cx - aw / 2, ab_cy, color=NEG, sw=1.7))
    frags.append(text((dir_cx + dw / 2 + ab_cx - aw / 2) / 2, dir_cy - 16,
                     "жене кроки", size=11, color=NEG))

    # Два конкретні будівельники праворуч, кожен → свій продукт
    concretes = [
        ("Будівельник дому", "готовий Дім", W * 0.80, 128, FIELD, "#eef8f2", "#e8f6ee"),
        ("Будівельник макета", "картонний Макет", W * 0.80, 340, POS, "#fdecea", "#fbe0dc"),
    ]
    for nm, prod, cx, cy, col, fillsoft, fillhard in concretes:
        b, bw, bh = textbox(cx, cy, nm, size=12.5, bold=True,
                            fill=fillsoft, stroke=col, sw=1.6, min_w=210)
        frags.append(b)
        # реалізує інтерфейс (пунктир від інтерфейсу до конкретного)
        frags.append(line(ab_cx + aw / 2, ab_cy, cx - bw / 2, cy,
                         color=col, sw=1.4, dash="5,5"))
        # продукт під будівельником
        p, pw, ph = textbox(cx, cy + 96, prod, size=12, bold=True,
                            fill=fillhard, stroke=col, sw=1.6, min_w=200)
        frags.append(p)
        frags.append(arrow(cx, cy + bh / 2, cx, cy + 96 - ph / 2, color=col, sw=1.5))

    frags.append(text(W * 0.80, 470, "однакові виклики Директора —", size=11.5, color=INK))
    frags.append(text(W * 0.80, 488, "різний матеріал на виході", size=11.5, bold=True, color=INK))

    # нижній підсумок
    frags.append(line(60, H - 74, W - 60, H - 74, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 48,
                     "Директор задає ЩО й у якому порядку · Будівельник вирішує З ЧОГО",
                     size=13, bold=True, color=INK))
    frags.append(text(W / 2, H - 26,
                     "підстав інший конкретний будівельник — той самий процес дасть інший продукт",
                     size=11.5, color=MUTED))

    render(os.path.join(IMG, 'builder-roles.svg'), W, H, *frags)


# ── Витік напівзібраного стану: сетери проти будівельника ───────────────────
def fig_half_built_leak():
    W, H = 1220, 620
    frags = []

    frags.append(text(W / 2, 40, "Напівзібраний стан: де його можна взяти",
                      size=17, bold=True, color=INK))
    frags.append(line(W / 2, 74, W / 2, H - 30, color="#d0d5db", sw=1.2, dash="6,6"))

    # ═══════════ ЛІВОРУЧ: СЕТЕРИ (витік) ═══════════
    lcx = W / 4
    frags.append(text(lcx, 70, "Сетери: об'єкт існує з першого кроку", size=13.5,
                      bold=True, color=POS))

    st = [
        ("new MutableHttpRequest()", "HttpRequest є — але БИТИЙ", True),
        (".setMethod(\"POST\")", "метод є, url нема — БИТИЙ", True),
        (".setUrl(\"https://…\")", "аж тепер цілий", False),
    ]
    y0 = 110
    for i, (call, note, broken) in enumerate(st):
        y = y0 + i * 118
        col = POS if broken else FIELD
        fillc = "#fdecea" if broken else "#eef8f2"
        b, bw, bh = textbox(lcx, y, call, size=12.5, bold=True,
                            fill=fillc, stroke=col, sw=1.6, min_w=300)
        frags.append(b)
        frags.append(text(lcx, y + bh / 2 + 20, note, size=11.5, bold=broken, color=col))
        if i < len(st) - 1:
            frags.append(arrow(lcx, y + bh / 2 + 30, lcx, y + 118 - bh / 2 - 2,
                               color=MUTED, sw=1.4))

    # «хтось бере його тут» — до битого другого стану
    grab_y = y0 + 1 * 118
    frags.append(text(lcx - 250, grab_y - 8, "хтось", size=12, bold=True, color=POS,
                      anchor="middle"))
    frags.append(text(lcx - 250, grab_y + 10, "бере", size=12, bold=True, color=POS,
                      anchor="middle"))
    frags.append(text(lcx - 250, grab_y + 28, "його ТУТ", size=12, bold=True, color=POS,
                      anchor="middle"))
    frags.append(arrow(lcx - 200, grab_y + 8, lcx - 155, grab_y + 8, color=POS, sw=1.7))
    frags.append(text(lcx, H - 40, "витік напівзібраного об'єкта", size=12.5,
                      bold=True, color=POS))

    # ═══════════ ПРАВОРУЧ: БУДІВЕЛЬНИК (нема чим узяти) ═══════════
    rcx = 3 * W / 4
    frags.append(text(rcx, 70, "Будівельник: продукт з'явиться лише в кінці",
                      size=13.5, bold=True, color=FIELD))

    bs = [
        ".header(…)",
        ".body(…)",
        ".timeout(…)",
    ]
    yb = 110
    for i, s in enumerate(bs):
        y = yb + i * 84
        b, bw, bh = textbox(rcx, y, s, size=12.5, bold=True,
                            fill=FILL, stroke=LINE, sw=1.5, min_w=220)
        frags.append(b)
        frags.append(text(rcx + 210, y, "це Builder,", size=11, color=MUTED))
        frags.append(text(rcx + 210, y + 16, "не запит", size=11, color=MUTED))
        frags.append(arrow(rcx, y + bh / 2, rcx, y + 84 - bh / 2 - 2, color=FIELD, sw=1.4))

    # мітка «взяти нічим» збоку від стосу кроків
    mid_y = yb + 84
    frags.append(text(rcx - 210, mid_y - 8, "запиту ще", size=11.5, bold=True, color=FIELD))
    frags.append(text(rcx - 210, mid_y + 9, "НЕМА —", size=11.5, bold=True, color=FIELD))
    frags.append(text(rcx - 210, mid_y + 26, "взяти нічим", size=11.5, bold=True, color=FIELD))

    # build() народжує цілий продукт
    build_y = yb + 3 * 84 + 4
    bb, bbw, bbh = textbox(rcx, build_y, ".build()", size=13, bold=True,
                           fill="#e8f6ee", stroke=FIELD, sw=1.9, min_w=200)
    frags.append(bb)
    frags.append(arrow(rcx, build_y + bbh / 2, rcx, build_y + 70 - 16, color=FIELD, sw=1.7))
    p, pw, ph = textbox(rcx, build_y + 78, "HttpRequest — цілий,\nперевірений, незмінний",
                        size=12, bold=True, fill="#eef8f2", stroke=FIELD, sw=1.7, min_w=260)
    frags.append(p)
    frags.append(text(rcx, H - 40, "проміжного об'єкта нема чого брати", size=12.5,
                      bold=True, color=FIELD))

    render(os.path.join(IMG, 'half-built-leak.svg'), W, H, *frags)


# ── Staged-будівельник: стадії-типи, build() лише у фінальній ────────────────
def fig_staged_builder_types():
    W, H = 1240, 480
    frags = []

    frags.append(text(W / 2, 40, "Стадії-типи: build() досяжний лише в кінці",
                      size=17, bold=True, color=INK))
    frags.append(text(W / 2, 63, "кожна стадія — окремий тип рівно з дозволеними методами",
                      size=12.5, color=MUTED))

    cy = 210
    # три стадії
    s1x = W * 0.17
    s2x = W * 0.50
    s3x = W * 0.83

    # Стадія 1: NeedMethod
    s1, w1, h1 = textbox(s1x, cy, ["NeedMethod", "method()"], size=13, bold=True,
                         fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=200)
    frags.append(s1)
    frags.append(text(s1x, cy - h1 / 2 - 14, "старт", size=11.5, color=MUTED))

    # Стадія 2: NeedUrl
    s2, w2, h2 = textbox(s2x, cy, ["NeedUrl", "url()"], size=13, bold=True,
                         fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=200)
    frags.append(s2)

    # Стадія 3: Ready (фінальна) — з build()
    s3, w3, h3 = textbox(s3x, cy,
                         ["Ready", "header()", "body()", "timeout()", "build()"],
                         size=12.5, bold=True, fill="#eef8f2", stroke=FIELD, sw=1.9,
                         min_w=200)
    frags.append(s3)
    frags.append(text(s3x, cy - h3 / 2 - 14, "фінальна", size=11.5, color=FIELD))

    # переходи обов'язкових кроків
    frags.append(arrow(s1x + w1 / 2, cy, s2x - w2 / 2, cy, color=NEG, sw=1.8))
    frags.append(text((s1x + w1 / 2 + s2x - w2 / 2) / 2, cy - 12, "method()",
                      size=11.5, bold=True, color=NEG))
    frags.append(arrow(s2x + w2 / 2, cy, s3x - w3 / 2, cy, color=NEG, sw=1.8))
    frags.append(text((s2x + w2 / 2 + s3x - w3 / 2) / 2, cy - 12, "url()",
                      size=11.5, bold=True, color=NEG))

    # петля «необов'язкові — назад у себе» на фінальній стадії
    loop_y = cy + h3 / 2 + 6
    frags.append(line(s3x - 40, loop_y, s3x - 40, loop_y + 26, color=FIELD, sw=1.5))
    frags.append(line(s3x - 40, loop_y + 26, s3x + 40, loop_y + 26, color=FIELD, sw=1.5))
    frags.append(arrow(s3x + 40, loop_y + 26, s3x + 40, loop_y, color=FIELD, sw=1.5))
    frags.append(text(s3x, loop_y + 46, "необов'язкові — у будь-якому порядку",
                      size=11, color=FIELD))

    # заборонений build() біля стадії 2 — «нема в цьому типі» (рамка, БЕЗ лінії крізь текст)
    bx, by = s2x, cy + h2 / 2 + 54
    fb, fbw, fbh = textbox(bx, by, "build() тут НЕ існує", size=12, bold=True,
                           fill="#fdecea", stroke=POS, sw=1.8, min_w=210)
    frags.append(fb)
    frags.append(text(bx, by + fbh / 2 + 18, "нема в стадії NeedUrl —", size=11,
                      bold=True, color=POS))
    frags.append(text(bx, by + fbh / 2 + 35, "виклик не скомпілюється", size=11,
                      bold=True, color=POS))

    frags.append(line(60, H - 62, W - 60, H - 62, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 38,
                      "Обов'язковий крок повертає ТИП наступної стадії · build() оголошено лише у фінальній",
                      size=12.5, bold=True, color=INK))
    frags.append(text(W / 2, H - 18,
                      "тому build() до проходження обов'язкових кроків не існує як код",
                      size=11.5, color=MUTED))

    render(os.path.join(IMG, 'staged-builder-types.svg'), W, H, *frags)


# ── Дві лінії одного «Будівельника»: GoF 1994 ↔ Блох 2008 ───────────────────
def fig_two_lineages():
    W, H = 1180, 720
    frags = []

    # спільний корінь — назва
    root_cx, root_cy = W / 2, 96
    rb, rbw, rbh = textbox(root_cx, root_cy, 'одне ім\'я: «Builder»', size=17,
                           bold=True, fill="#eef2f7", stroke=INK, sw=2, min_w=280)
    frags.append(rb)
    frags.append(text(root_cx, root_cy - rbh / 2 - 12,
                      "спільна кістка: збери рішення в помічнику → забери зібране",
                      size=12.5, color=MUTED))

    # ── розгалуження на дві лінії ──
    lcx = W / 4 + 10          # ЛІВА: GoF
    rcx = 3 * W / 4 - 10      # ПРАВА: Блох
    split_y = root_cy + rbh / 2

    # заголовки ліній
    l_head_y = 210
    r_head_y = 210
    lh, lhw, lhh = textbox(lcx, l_head_y, "GoF · 1994", size=16, bold=True,
                           fill="#fdecea", stroke=POS, sw=2, min_w=220)
    rh, rhw, rhh = textbox(rcx, r_head_y, "Блох · 2008", size=16, bold=True,
                           fill="#eaf0fd", stroke=NEG, sw=2, min_w=220)
    frags.append(lh)
    frags.append(rh)

    # стрілки від кореня до заголовків (повз написи)
    frags.append(arrow(root_cx - rbw / 2 + 30, split_y, lcx, l_head_y - lhh / 2, color=POS, sw=1.8))
    frags.append(arrow(root_cx + rbw / 2 - 30, split_y, rcx, r_head_y - rhh / 2, color=NEG, sw=1.8))

    # підзаголовки книг
    frags.append(text(lcx, l_head_y + lhh / 2 + 18, "Design Patterns", size=12, bold=True, color=INK))
    frags.append(text(lcx, l_head_y + lhh / 2 + 34, "Gamma·Helm·Johnson·Vlissides", size=10.5, color=MUTED))
    frags.append(text(rcx, r_head_y + rhh / 2 + 18, "Effective Java, Пункт 2", size=12, bold=True, color=INK))
    frags.append(text(rcx, r_head_y + rhh / 2 + 34, "Joshua Bloch", size=10.5, color=MUTED))

    # ── картки-«герої» кожної лінії ──
    hero_y = 320
    lhero = fitbox(lcx - 165, hero_y, 330, 58,
                   "герой — ДИРЕКТОР\n(знає порядок кроків)",
                   size=13, bold=True, fill=FILL, stroke=POS, sw=1.6, color=INK)
    rhero = fitbox(rcx - 165, hero_y, 330, 58,
                   "герой — ПЛИННИЙ ЛАНЦЮЖОК\n(порядок задає сам клієнт)",
                   size=13, bold=True, fill=FILL, stroke=NEG, sw=1.6, color=INK)
    frags.append(lhero)
    frags.append(rhero)

    # ── «навіщо» ──
    why_y = 402
    lwhy = fitbox(lcx - 165, why_y, 330, 58,
                  "навіщо: один процес →\nрізні представлення",
                  size=13, fill=FILL, stroke=LINE, sw=1.3, color=INK)
    rwhy = fitbox(rcx - 165, why_y, 330, 58,
                  "навіщо: багато параметрів →\nчитний і безпечний виклик",
                  size=13, fill=FILL, stroke=LINE, sw=1.3, color=INK)
    frags.append(lwhy)
    frags.append(rwhy)

    # ── приклад / вихід ──
    ex_y = 484
    lex = fitbox(lcx - 165, ex_y, 330, 58,
                 "RTF → ASCII · TeX · віджет\n(кілька представлень)",
                 size=12.5, fill="#fdf0ee", stroke=POS, sw=1.3, color=INK)
    rex = fitbox(rcx - 165, ex_y, 330, 58,
                 "один незмінний об'єкт\n(одне представлення)",
                 size=12.5, fill="#eef2fd", stroke=NEG, sw=1.3, color=INK)
    frags.append(lex)
    frags.append(rex)

    # директор: є / нема
    dir_y = 566
    ldir = fitbox(lcx - 165, dir_y, 330, 44, "директор — Є, центральний",
                  size=12.5, bold=True, fill=FILL, stroke=POS, sw=1.4, color=POS)
    rdir = fitbox(rcx - 165, dir_y, 330, 44, "директор — НЕМА (роль грає клієнт)",
                  size=12.5, bold=True, fill=FILL, stroke=NEG, sw=1.4, color=NEG)
    frags.append(ldir)
    frags.append(rdir)

    # вертикальні тонкі напрямні між картками кожної лінії (повз написи, з боків)
    for cx, col in ((lcx, POS), (rcx, NEG)):
        frags.append(line(cx - 165, hero_y + 58, cx - 165, dir_y, color="#e2e6ea", sw=1))
        frags.append(line(cx + 165, hero_y + 58, cx + 165, dir_y, color="#e2e6ea", sw=1))

    # роздільник між лініями
    frags.append(line(W / 2, l_head_y - lhh / 2 - 6, W / 2, dir_y + 44, color="#d0d5db", sw=1.2, dash="6,6"))

    # підсумок унизу
    frags.append(line(60, H - 58, W - 60, H - 58, color="#d0d5db", sw=1.1))
    frags.append(text(W / 2, H - 34,
                      "Два акценти однієї ідеї «відділи складання від об'єкта»: повторне вживання ПРОЦЕСУ ↔ безпека складання ОДНОГО",
                      size=12.5, bold=True, color=INK))
    frags.append(text(W / 2, H - 15,
                      "плинний інтерфейс (Fowler·Evans, 2005) — окремий, ширший прийом; не плутати з жодною з двох ліній",
                      size=11, color=MUTED))

    render(os.path.join(IMG, 'two-lineages.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_telescoping_vs_builder()
    fig_builder_roles()
    fig_half_built_leak()
    fig_staged_builder_types()
    fig_two_lineages()
    print("figs done")
