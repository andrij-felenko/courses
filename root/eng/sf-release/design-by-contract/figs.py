# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN = "#c07000"   # бурштин — інваріант
WFILL = "#fff3cd"


# ── contract: три частини контракту й хто винен ───────────────────────────────
# Ідея: функція — це угода. Передумова на вході (борг ВИКЛИКАЧА), постумова на
# виході (борг ФУНКЦІЇ), інваріант тримається до і після. Хто винен при хибі
# кожної — різний, і саме це показує, чий код шукати.

def fig_contract():
    W, H = 760, 380
    p = []
    fx, fy, fw, fh = 270, 92, 220, 196          # «тіло функції»
    p.append(rect(fx, fy, fw, fh, fill="#f6f7f9", stroke=INK, sw=1.8))
    p.append(text(fx + fw / 2, fy - 14, "тіло функції", size=12, color=INK, bold=True))

    pre, pw, ph = textbox(fx + fw / 2, fy + 34,
                          "ПЕРЕДУМОВА\nвимога на вході", size=11, bold=True,
                          color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=190)
    inv, iw, ih = textbox(fx + fw / 2, fy + fh / 2 + 4,
                          "ІНВАРІАНТ\nтримається наскрізь", size=11, bold=True,
                          color=WARN, fill=WFILL, stroke=WARN, sw=1.8, min_w=190)
    post, pow_, poh = textbox(fx + fw / 2, fy + fh - 32,
                              "ПОСТУМОВА\nгарантія на виході", size=11, bold=True,
                              color=FIELD, fill="#e8f5e9", stroke=FIELD, sw=1.8, min_w=190)

    # вхід / вихід
    p.append(arrow(120, fy + 34, fx, fy + 34, color=NEG, sw=1.8))
    p.append(text(120, fy + 20, "виклик", size=10, color=NEG, anchor="start"))
    p.append(arrow(fx + fw, fy + fh - 32, W - 120, fy + fh - 32, color=FIELD, sw=1.8))
    p.append(text(W - 150, fy + fh - 44, "return", size=10, color=FIELD, anchor="start"))

    p.append(pre); p.append(inv); p.append(post)

    blame = [
        (NEG, "хиба ПЕРЕДумови → винен ВИКЛИКАЧ: дав погані аргументи"),
        (FIELD, "хиба ПОСТумови → винна ФУНКЦІЯ: не виконала обіцянку"),
        (WARN, "хиба ІНВАРІАНТА → щось затерло стан модуля"),
    ]
    by = H - 64
    for col, txt in blame:
        p.append(circle(70, by, 5, fill=col, stroke=col, sw=1))
        p.append(text(86, by + 4, txt, size=11, color=INK, anchor="start"))
        by += 22

    render(os.path.join(OUT, "contract.svg"), W, H, *p,
           title="Контракт функції: передумова, постумова, інваріант")


# ── blame: контракт чітко призначає провину, а оборона — ні ───────────────────
# Ідея: дві колонки. Без контракту падіння — посеред чужого коду, і незрозуміло,
# хто винен. З контрактом перевірка на самій межі одразу називає винного.

def fig_blame():
    W, H = 720, 330
    p = []
    midx = 360
    lx, rxc = 185, 535
    bw = 270

    p.append(text(lx, 58, "БЕЗ контракту", size=14, color=POS, bold=True))
    p.append(text(rxc, 58, "З контрактом", size=14, color=FIELD, bold=True))
    p.append(line(midx, 48, midx, 268, color=MUTED, sw=1.2, dash="5 4"))

    left = [
        ("погані аргументи проходять\nу тіло функції", "#fdecea", POS),
        ("крах за 50 рядків углиб,\nу чужому коді", "#fdecea", POS),
        ("хто винен? викликач\nчи функція? — невідомо", "#fdecea", POS),
    ]
    right = [
        ("передумова на самій межі\nловить аргумент одразу", "#e8f5e9", FIELD),
        ("стоп тут же, де помилка\nвперше ввійшла", "#e8f5e9", FIELD),
        ("винен ВИКЛИКАЧ — однозначно,\nбез гадань", "#e8f5e9", FIELD),
    ]
    y = 84
    bh = 46
    pl = pr = None
    for (lt, lf, ls), (rt, rf, rs) in zip(left, right):
        p.append(fitbox(lx - bw / 2, y, bw, bh, lt, size=11, fill=lf, stroke=ls, sw=1.7))
        p.append(fitbox(rxc - bw / 2, y, bw, bh, rt, size=11, fill=rf, stroke=rs, sw=1.7))
        if pl is not None:
            p.append(arrow(lx, pl + bh, lx, y, color=POS, sw=1.5))
            p.append(arrow(rxc, pr + bh, rxc, y, color=FIELD, sw=1.5))
        pl = pr = y
        y += 64

    p.append(text(W / 2, H - 14,
                  "контракт перетворює «десь зламалось» на «винен той, хто порушив свій бік»",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "blame.svg"), W, H, *p,
           title="Призначення провини: межа контракту називає винного")


# ── who-checks: контракт — одна сторона; оборона — кожен вхід ──────────────────
# Ідея: межу між викликачем і функцією перевіряє РІВНО одна сторона за домовле-
# ністю (інакше дубль). Оборона з недовірою перевіряє КОЖЕН вхід, бо світ бреше.

def fig_who_checks():
    W, H = 760, 410
    p = []
    midx = 380
    p.append(line(midx, 70, midx, 332, color=MUTED, sw=1.2, dash="5 4"))
    p.append(text(195, 56, "КОНТРАКТ", size=14, color=FIELD, bold=True))
    p.append(text(575, 56, "ОБОРОНА", size=14, color=POS, bold=True))
    p.append(text(195, 74, "довірений код", size=10, color=MUTED, italic=True))
    p.append(text(575, 74, "недовірений світ", size=10, color=MUTED, italic=True))

    # ── ліворуч: викликач → [одна перевірка на межі] → функція ──
    lcx = 195
    cl, clw, clh = textbox(lcx, 116, "викликач", size=11, fill=FILL, stroke=MUTED, sw=1.4, min_w=130)
    chk, ckw, ckh = textbox(lcx, 196, "ПЕРЕВІРКА\nрівно ОДНА сторона\n(домовились наперед)",
                            size=11, bold=True, color=FIELD, fill="#e8f5e9", stroke=FIELD, sw=2, min_w=210)
    fn, fnw, fnh = textbox(lcx, 282, "функція\n(довіряє входу)", size=11,
                           fill=FILL, stroke=MUTED, sw=1.4, min_w=160)
    p.append(arrow(lcx, 116 + clh / 2, lcx, 196 - ckh / 2, color=FIELD, sw=1.7))
    p.append(arrow(lcx, 196 + ckh / 2, lcx, 282 - fnh / 2, color=FIELD, sw=1.7))
    p.append(cl); p.append(chk); p.append(fn)

    # ── праворуч: кожен вхід окремо перевіряється ──
    rcx = 575
    src, sw_, sh = textbox(rcx, 110, "недовірені дані", size=11, color=POS,
                           fill="#fdecea", stroke=POS, sw=1.6, min_w=180)
    p.append(src)
    ins = ["UART", "радіо", "давач", "NVS"]
    gx0, gstep = 470, 70
    gy = 196
    for i, lab in enumerate(ins):
        gx = gx0 + i * gstep
        b, bw, bh = textbox(gx, gy, lab, size=10, fill=FILL, stroke=POS, sw=1.4, min_w=58)
        p.append(b)
        p.append(arrow(rcx, 110 + sh / 2, gx, gy - bh / 2, color=POS, sw=1.3))
        # кожен вхід — своя застава
        p.append(text(gx, gy + 26, "✓", size=13, color=POS, bold=True))
    p.append(text(rcx, 282, "перевіряємо КОЖЕН вхід", size=11, color=POS, bold=True))

    p.append(text(W / 2, H - 14,
                  "одна межа — одна сторона; периметр зі світом — недовіра до кожного",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "who-checks.svg"), W, H, *p,
           title="Хто перевіряє межу: контракт (одна сторона) vs оборона (кожен вхід)")


# ── lsp: правило підтипів Лісков — послабити перед, посилити пост ──────────────
# Ідея: нащадок мусить лишитись придатним усюди, де чекають батька. Звідси перед-
# умову можна лише ПОСЛАБИТИ (звузити вимогу), постумову — лише ПОСИЛИТИ.

def fig_lsp():
    W, H = 760, 400
    p = []
    cx = W / 2

    base, bw, bh = textbox(cx, 70, "БАТЬКІВСЬКИЙ контракт", size=13, bold=True,
                           color=INK, fill=FILL, stroke=INK, sw=2, min_w=300)
    p.append(base)

    # ліва колона — передумова; права — постумова
    lx, rx = 200, 560
    p.append(text(lx, 132, "ПЕРЕДУМОВА (вхід)", size=12, color=NEG, bold=True))
    p.append(text(rx, 132, "ПОСТУМОВА (вихід)", size=12, color=FIELD, bold=True))

    pre_b, w1, h1 = textbox(lx, 178, "батько: x > 0", size=11, fill="#eaf0fd", stroke=NEG, sw=1.6, min_w=200)
    post_b, w2, h2 = textbox(rx, 178, "батько: список\nвідсортовано", size=11,
                             fill="#e8f5e9", stroke=FIELD, sw=1.6, min_w=200)
    p.append(pre_b); p.append(post_b)

    # дозволено
    ok_pre, _, hop = textbox(lx, 250, "нащадку МОЖНА: x ≥ 0\n(послабити — ширше)",
                             size=11, bold=True, color=FIELD, fill="#e8f5e9", stroke=FIELD, sw=2, min_w=230)
    ok_post, _, hoq = textbox(rx, 250, "нащадку МОЖНА: ще й\nбез дублів (посилити)",
                              size=11, bold=True, color=FIELD, fill="#e8f5e9", stroke=FIELD, sw=2, min_w=230)
    p.append(arrow(lx, 178 + h1 / 2, lx, 250 - hop / 2, color=FIELD, sw=1.6))
    p.append(arrow(rx, 178 + h2 / 2, rx, 250 - hoq / 2, color=FIELD, sw=1.6))
    p.append(ok_pre); p.append(ok_post)

    # заборонено
    no_pre, _, hnp = textbox(lx, 322, "НЕ МОЖНА: x > 100\n(посилити — вужче)",
                             size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=2, min_w=230)
    no_post, _, hnq = textbox(rx, 322, "НЕ МОЖНА: інколи\nне відсортовано",
                              size=11, bold=True, color=POS, fill="#fdecea", stroke=POS, sw=2, min_w=230)
    p.append(no_pre); p.append(no_post)

    p.append(text(W / 2, H - 12,
                  "передумову лише послаблювати · постумову лише посилювати · інваріант зберігати",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "lsp.svg"), W, H, *p,
           title="Правило Лісков: куди вільно зсувати контракт нащадка")


# ── invariant-lifecycle: інваріант ламається всередині, відновлюється до return ─
# Ідея: лінія «істинності» інваріанта в часі однієї операції. Цілий на вході,
# на мить хибний посеред кроків, знову цілий перед поверненням. Хиба НА МЕЖАХ —
# чужа провина; хиба ВСЕРЕДИНІ — нормальна, якщо відновлено до виходу.

def fig_invariant_lifecycle():
    W, H = 760, 360
    p = []
    # вісь часу
    ax0, ax1, ay = 90, 670, 210
    p.append(line(ax0, ay, ax1, ay, color=MUTED, sw=1.4))
    p.append(text(ax1 + 6, ay + 4, "час", size=10, color=MUTED, anchor="start"))

    # три точки: вхід, середина, вихід
    xin, xmid, xout = 170, 380, 600
    ytrue, yfalse = 150, 270

    # «істинність» інваріанта: true на вході → false посередині → true на виході
    seg = lambda x1, y1, x2, y2, c: line(x1, y1, x2, y2, color=c, sw=3)
    p.append(seg(xin, ytrue, xmid - 60, ytrue, FIELD))       # тримається
    p.append(seg(xmid - 60, ytrue, xmid, yfalse, WARN))      # падає
    p.append(seg(xmid, yfalse, xmid + 60, yfalse, WARN))     # «в дорозі»
    p.append(seg(xmid + 60, yfalse, xout, ytrue, FIELD))     # відновлено
    p.append(seg(xout, ytrue, ax1 - 20, ytrue, FIELD))

    # рівні
    p.append(text(ax0 - 4, ytrue + 4, "ціл.", size=10, color=FIELD, anchor="end", bold=True))
    p.append(text(ax0 - 4, yfalse + 4, "хиб.", size=10, color=WARN, anchor="end", bold=True))
    p.append(line(ax0, ytrue, ax1 - 20, ytrue, color="#d8dde3", sw=0.8, dash="3 4"))
    p.append(line(ax0, yfalse, ax1 - 20, yfalse, color="#d8dde3", sw=0.8, dash="3 4"))

    # маркери-точки
    for x in (xin, xout):
        p.append(circle(x, ytrue, 5, fill=FIELD, stroke=FIELD, sw=1))
    p.append(circle(xmid, yfalse, 5, fill=WARN, stroke=WARN, sw=1))

    # підписи зверху
    inb, iw, ih = textbox(xin, 96, "ВХІД\nassert: ціл.", size=10, bold=True,
                          color=FIELD, fill="#e8f5e9", stroke=FIELD, sw=1.6, min_w=110)
    midb, mw, mh = textbox(xmid, 320, "посеред кроків —\nна мить хибний (норма)",
                           size=10, bold=True, color=WARN, fill=WFILL, stroke=WARN, sw=1.6, min_w=180)
    outb, ow, oh = textbox(xout, 96, "ВИХІД\nassert: ціл.", size=10, bold=True,
                           color=FIELD, fill="#e8f5e9", stroke=FIELD, sw=1.6, min_w=110)
    p.append(inb); p.append(midb); p.append(outb)

    p.append(text(W / 2, H - 14,
                  "хиба НА МЕЖАХ → чужа провина; хиба всередині дозволена, якщо відновлено до return",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "invariant-lifecycle.svg"), W, H, *p,
           title="Життя інваріанта в межах однієї операції")


if __name__ == "__main__":
    fig_contract()
    fig_blame()
    fig_who_checks()
    fig_lsp()
    fig_invariant_lifecycle()
    print("OK: figures written to", OUT)
