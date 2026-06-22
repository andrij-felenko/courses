# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN = "#c07000"   # бурштин — assert / баг
WFILL = "#fff3cd"


# ── three-levels: одне питання «звідки збій?» → три різні відповіді ────────────
# Ідея: походження збою (а не його тяжкість) диктує силу відповіді. Очікувано →
# код повернення; порушено припущення → assert; стан невідновний → паніка.

def fig_three_levels():
    W, H = 760, 360
    cx = W / 2
    p = []

    # корінь — питання
    root, rw, rh = textbox(cx, 64, "Звідки збій?", size=14, bold=True,
                           fill=FILL, stroke=INK, sw=2.2, pad=12)

    cols = [
        (150, NEG, "#eaf0fd", "очікувано",
         "ЗОВНІШНІЙ СВІТ\nдавач мовчить,\nфайл відсутній,\nшина зайнята",
         "КОД ПОВЕРНЕННЯ\nхай вирішує\nвикликач"),
        (cx, WARN, WFILL, "баг",
         "ПОРУШЕНО\nПРИПУЩЕННЯ\nNULL там, де не\nможе бути; індекс\nза межами",
         "ASSERT\nстоп у debug,\nфайл і рядок"),
        (W - 150, POS, "#fdecea", "невідновно",
         "СТАН ЗЛАМАНО\nпсування стеку,\nбита критична\nструктура в RAM",
         "ПАНІКА / RESET\nдалі будь-яка\nдія робить гірше"),
    ]

    for gx, col, fill, edge, cause, answer in cols:
        # ярлик гілки
        p.append(text(gx, 116, edge, size=11, color=col, italic=True, bold=True))
        # причина
        cb, cw, ch = textbox(gx, 188, cause, size=11, fill=FILL, stroke=MUTED, sw=1.4)
        # відповідь
        ab, aw, ah = textbox(gx, 296, answer, size=12, bold=True, color=INK,
                             fill=fill, stroke=col, sw=2.2)
        # ребро корінь → причина
        p.append(line(cx, 64 + rh / 2, gx, 188 - ch / 2, color=MUTED, sw=1.5))
        # ребро причина → відповідь
        p.append(arrow(gx, 188 + ch / 2, gx, 296 - ah / 2, color=col, sw=1.8))
        p.append(cb)
        p.append(ab)

    p.append(root)
    p.append(text(cx, H - 12, "силу відповіді диктує ПОХОДЖЕННЯ збою, не його гучність",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "three-levels.svg"), W, H, *p,
           title="Три рівні реакції: одне питання, три відповіді")


# ── ndebug-pitfall: робота всередині assert зникає в релізі ───────────────────
# Ідея: одна лінія часу для DEBUG, друга — для RELEASE(NDEBUG). У релізі весь
# рядок assert вирізає препроцесор, і якщо в нього сховали init() — її не буде.

def fig_ndebug_pitfall():
    W, H = 700, 360
    p = []
    midx = 350
    lx, rxc = 235, 575           # центри колонок
    bw = 250

    p.append(text(lx, 60, "DEBUG", size=14, color=FIELD, bold=True))
    p.append(text(rxc, 60, "RELEASE (NDEBUG)", size=14, color=POS, bold=True))
    p.append(line(midx, 50, midx, 318, color=MUTED, sw=1.2, dash="5 4"))

    rows = [
        ("assert( init() == OK )", FILL, INK, INK, "рядок ВИРІЗАНО\nпрепроцесором ✗", "#fdecea", POS),
        ("init() ВИКЛИКАНО ✓", "#e8f5e9", FIELD, INK, "init() НЕ ВИКЛИКАНО ✗", "#fdecea", POS),
        ("перевірка є ✓", "#e8f5e9", FIELD, INK, "старт без\nініціалізації ✗", "#fdecea", POS),
    ]
    y = 86
    bh = 50
    prev = None
    for ltext, lfill, lstroke, lcol, rtext, rfill, rstroke in rows:
        p.append(fitbox(lx - bw / 2, y, bw, bh, ltext, size=12, fill=lfill,
                        stroke=lstroke, sw=1.8, color=lcol))
        p.append(fitbox(rxc - bw / 2, y, bw, bh, rtext, size=12, fill=rfill,
                        stroke=rstroke, sw=1.8, color=INK))
        if prev is not None:
            p.append(arrow(lx, prev + bh, lx, y, color=FIELD, sw=1.5))
            p.append(arrow(rxc, prev + bh, rxc, y, color=POS, sw=1.5))
        prev = y
        y += 74

    # хрест поверх правої гілки «вирізано»
    p.append(line(rxc - 22, 80, rxc + 22, 122, color=POS, sw=3.5))
    p.append(line(rxc + 22, 80, rxc - 22, 122, color=POS, sw=3.5))

    note, nw, nh = textbox(midx, H - 26, "Правило: в assert — лише чиста перевірка, жодної роботи",
                           size=12, bold=True, fill="#fdecea", stroke=POS, sw=2)
    p.append(note)

    render(os.path.join(OUT, "ndebug-pitfall.svg"), W, H, *p,
           title="Пастка assert: робота всередині зникає в релізі")


# ── panic-flow: що ESP-IDF робить при паніці ──────────────────────────────────
# Ідея: тригери збоку зливаються в panic handler; той друкує трасування й далі
# розгалужується на три налаштовані стратегії. На МК без MMU це б'є все.

def fig_panic_flow():
    W, H = 720, 340
    p = []

    triggers = ["HardFault", "stack overflow", "abort()\nassert", "watchdog"]
    tx = 90
    ty0, tstep = 70, 62
    handler_cx, handler_cy = 340, 150
    hb, hw, hh = textbox(handler_cx, handler_cy, "panic handler\n(друк трасування\nі причини)",
                         size=12, bold=True, fill=WFILL, stroke=WARN, sw=2.2)

    tcs = []
    for i, t in enumerate(triggers):
        ty = ty0 + i * tstep
        tb, tw, th = textbox(tx, ty, t, size=11, fill=FILL, stroke=MUTED, sw=1.4, min_w=120)
        p.append(tb)
        tcs.append((tx + tw / 2, ty))

    for (ex, ey) in tcs:
        p.append(line(ex, ey, handler_cx - hw / 2, handler_cy, color=MUTED, sw=1.4))
    p.append(hb)

    outs = [
        (70, "RESET\n(штатний шлях)", POS, "#fdecea"),
        (170, "ЗАВИСНУТИ\nдля JTAG", NEG, "#eaf0fd"),
        (270, "CORE DUMP\nу Flash", FIELD, "#e8f5e9"),
    ]
    oxc = 600
    for oy, lab, col, fill in outs:
        ob, ow, oh = textbox(oxc, oy, lab, size=11, bold=True, color=INK,
                             fill=fill, stroke=col, sw=2)
        p.append(arrow(handler_cx + hw / 2, handler_cy, oxc - ow / 2, oy, color=col, sw=1.6))
        p.append(ob)

    p.append(text(W / 2, H - 14,
                  "МК без MMU: падіння будь-якого коду = падіння всього → майже завжди reset",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "panic-flow.svg"), W, H, *p,
           title="Паніка на ESP32: тригери → handler → налаштована реакція")


# ── contract: де стоять перед-/постумова та інваріант (детальна) ──────────────
# Ідея: функція як «контракт». Передумова — на вході (борг викликача), постумова
# — на виході (борг функції), інваріант — тримається наскрізь. Хто винен при
# хибі кожної — різний, і це визначає, чий код шукати.

def fig_contract():
    W, H = 720, 360
    p = []
    fx, fy, fw, fh = 250, 96, 220, 200       # «тіло функції»
    p.append(rect(fx, fy, fw, fh, fill="#f6f7f9", stroke=INK, sw=1.8))
    p.append(text(fx + fw / 2, fy - 14, "тіло функції", size=12, color=INK, bold=True))

    # передумова — зверху на вході
    pre, pw, ph = textbox(fx + fw / 2, fy + 34,
                          "ПЕРЕДУМОВА\nassert на вході", size=11, bold=True,
                          color=NEG, fill="#eaf0fd", stroke=NEG, sw=1.8, min_w=180)
    p.append(pre)
    # інваріант — посередині
    inv, iw, ih = textbox(fx + fw / 2, fy + fh / 2 + 6,
                          "ІНВАРІАНТ\nтримається наскрізь", size=11, bold=True,
                          color=WARN, fill="#fff3cd", stroke=WARN, sw=1.8, min_w=180)
    p.append(inv)
    # постумова — знизу на виході
    post, pow_, poh = textbox(fx + fw / 2, fy + fh - 30,
                              "ПОСТУМОВА\nassert перед return", size=11, bold=True,
                              color=FIELD, fill="#e8f5e9", stroke=FIELD, sw=1.8, min_w=180)
    p.append(post)

    # вхід / вихід
    p.append(arrow(120, fy + 34, fx, fy + 34, color=NEG, sw=1.8))
    p.append(text(120, fy + 20, "виклик", size=10, color=NEG, anchor="start"))
    p.append(arrow(fx + fw, fy + fh - 30, W - 120, fy + fh - 30, color=FIELD, sw=1.8))
    p.append(text(W - 150, fy + fh - 42, "return", size=10, color=FIELD, anchor="start"))

    # хто винен
    blame = [
        (NEG, "хиба ПЕРЕДумови → винен ВИКЛИКАЧ (порушив свій бік угоди)"),
        (FIELD, "хиба ПОСТумови / інваріанта → винна сама ФУНКЦІЯ"),
    ]
    by = H - 46
    for col, txt in blame:
        p.append(circle(70, by, 5, fill=col, stroke=col, sw=1))
        p.append(text(86, by + 4, txt, size=11, color=INK, anchor="start"))
        by += 22

    render(os.path.join(OUT, "contract.svg"), W, H, *p,
           title="Функція як контракт: передумова, постумова, інваріант")


# ── assert-strategy: які перевірки лишати в кожному режимі (детальна) ──────────
# Ідея: не «assert увімкнено/вимкнено», а три класи перевірок із різною долею.
# Зовнішнє завжди перевіряємо; критичний інваріант лишаємо й у релізі; дорогий
# контроль — лише в debug.

def fig_assert_strategy():
    W, H = 720, 320
    p = []
    colx = [250, 470, 640]
    head = [("DEBUG", FIELD), ("RELEASE", WARN), ("дорого?", MUTED)]
    rowx0 = 40
    laby = 78
    for cx, (h, col) in zip(colx, head):
        p.append(text(cx, laby, h, size=12, color=col, bold=True))
    p.append(text(rowx0, laby, "перевірка", size=12, color=INK, anchor="start", bold=True))

    rows = [
        ("вхід зовні (код повернення)", "✓", "✓", "ні", FIELD, FIELD),
        ("критичний інваріант", "✓", "✓ (лишити!)", "ні", FIELD, FIELD),
        ("звичайний assert", "✓", "вимкнено", "ні", FIELD, MUTED),
        ("обхід усього масиву", "✓", "#ifdef DEBUG", "так", FIELD, POS),
    ]
    y = 108
    for lab, d, r, cost, dcol, rcol in rows:
        p.append(line(rowx0, y - 16, W - 40, y - 16, color="#e3e6ea", sw=1.0))
        p.append(text(rowx0, y, lab, size=11, color=INK, anchor="start"))
        p.append(text(colx[0], y, d, size=11, color=dcol, bold=True))
        p.append(text(colx[1], y, r, size=11, color=rcol, bold=True))
        p.append(text(colx[2], y, cost, size=11, color=MUTED))
        y += 40

    note, nw, nh = textbox(W / 2, H - 34,
                           "Правило: зовнішнє — завжди; критичний інваріант — і в релізі; дороге — лише в debug",
                           size=11, bold=True, fill=FILL, stroke=INK, sw=1.6)
    p.append(note)

    render(os.path.join(OUT, "assert-strategy.svg"), W, H, *p,
           title="Стратегія assert: яку перевірку де лишати")


if __name__ == "__main__":
    fig_three_levels()
    fig_ndebug_pitfall()
    fig_panic_flow()
    fig_contract()
    fig_assert_strategy()
    print("OK: figures written to", OUT)
