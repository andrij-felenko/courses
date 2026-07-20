# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── Фігура 1: той самий загублений відгук — два кінці повтору ────────────────
def fig_retry_ambiguity():
    W, H = 860, 470
    frags = []
    frags.append(text(W / 2, 32, "Той самий загублений відгук — два різні кінці", size=16, bold=True))
    frags.append(text(W / 2, 54, "клієнт не знає, чи пройшло, тож повторює — а далі все залежить від сервера",
                      size=12, color=MUTED, italic=True))

    # спільна зав'язка
    frags.append(fitbox(150, 78, 560, 40,
                        "POST /charges 100 грн  →  сервер списав  →  відгук зник  →  клієнт повторює",
                        size=12, fill=FILL, stroke=INK, sw=1.6))

    # два панелі
    panels = [
        (40, POS, "Повтор без захисту", "#fdecea",
         ["① POST 100 грн  →  списано, відгук зник",
          "② повтор POST 100 грн  →  списано ЗНОВУ"],
         "разом −200 грн   ✗  подвійне списання"),
        (440, FIELD, "Повтор із ключем ідемпотентності", "#eafaf1",
         ["① POST 100 грн [key K]  →  списано, відгук зник",
          "② повтор [key K]  →  віддано збережене"],
         "разом −100 грн   ✓  рівно раз"),
    ]
    for px, col, header, resfill, rows, result in panels:
        frags.append(rect(px, 142, 380, 292, fill=BG, stroke=col, sw=1.9))
        frags.append(text(px + 190, 172, header, size=13, bold=True, color=col))
        ry = 194
        for r in rows:
            frags.append(fitbox(px + 22, ry, 336, 44, r, size=12, fill=FILL, stroke=MUTED, sw=1.4))
            ry += 54
        frags.append(fitbox(px + 22, 324, 336, 58, result, size=13, fill=resfill,
                            stroke=col, sw=2.0, bold=True, color=col))

    render(os.path.join(IMG, "retry-ambiguity.svg"), W, H, *frags)


# ── Фігура 2: вкладені класи — безпечні ⊂ ідемпотентні ⊂ усі методи ──────────
def fig_method_classes():
    W, H = 760, 480
    frags = []
    frags.append(text(W / 2, 32, "Три вкладені обіцянки методів HTTP", size=16, bold=True))

    # зовнішнє кільце — усі методи
    frags.append(rect(40, 60, 680, 388, fill=BG, stroke=MUTED, sw=1.7))
    frags.append(text(W / 2, 88, "усі методи", size=13, bold=True, color=MUTED))
    # POST / PATCH — у зовнішньому кільці (не ідемпотентні)
    frags.append(text(150, 424, "POST", size=14, bold=True, color=POS))
    frags.append(text(150, 442, "повтор → інший стан", size=10, color=MUTED))
    frags.append(text(610, 424, "PATCH", size=14, bold=True, color=POS))
    frags.append(text(610, 442, "як пощастить", size=10, color=MUTED))

    # середнє кільце — ідемпотентні
    frags.append(rect(130, 130, 500, 248, fill="#eaf0fd", stroke=NEG, sw=1.9))
    frags.append(text(W / 2, 158, "ідемпотентні", size=13, bold=True, color=NEG))
    # PUT / DELETE — у середньому кільці (міняють стан, повтор безпечний)
    frags.append(text(175, 256, "PUT", size=14, bold=True, color=NEG))
    frags.append(text(585, 256, "DELETE", size=14, bold=True, color=NEG))

    # внутрішнє кільце — безпечні
    frags.append(rect(228, 198, 304, 116, fill="#eafaf1", stroke=FIELD, sw=2.1))
    frags.append(text(W / 2, 232, "безпечні", size=13, bold=True, color=FIELD))
    frags.append(text(W / 2, 262, "GET · HEAD · OPTIONS · TRACE", size=12, color=INK))
    frags.append(text(W / 2, 288, "лише читають — стан не рухають", size=10, color=MUTED, italic=True))

    frags.append(text(W / 2, H - 14, "чим глибше кільце — тим суворіша обіцянка серверу",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "method-classes.svg"), W, H, *frags)


# ── Фігура 3: ключ ідемпотентності — робота раз, відповідь скільки завгодно ──
def fig_idempotency_key():
    W, H = 880, 400
    frags = []
    frags.append(text(W / 2, 32, "Ключ ідемпотентності: робота — раз, відповідь — скільки завгодно",
                      size=15, bold=True))

    # центральне сховище (спільне для обох доріжок)
    sx, sy, sw_, sh = 335, 96, 210, 226
    frags.append(rect(sx, sy, sw_, sh, fill=FILL, stroke=INK, sw=2.0))
    frags.append(mtext(sx + sw_ / 2, 196, ["Сховище ключів", "K → відповідь R"],
                       size=13, bold=True))

    # доріжка 1 (виконання)
    y1 = 145
    b1, w1, h1 = textbox(130, y1, ["Запит 1", "key = K"], size=12, fill=BG, stroke=INK, sw=1.7)
    frags.append(b1)
    frags.append(arrow(130 + w1 / 2 + 4, y1, sx - 4, y1, color=FIELD, sw=1.8))
    frags.append(fitbox(200, y1 - 44, 118, 30, "нема K", size=11, fill="#ffffff", stroke=FIELD, sw=1.3))
    r1, rw1, rh1 = textbox(760, y1, ["R: списано 1×", "(робота виконана)"], size=12,
                           fill="#eafaf1", stroke=FIELD, sw=1.9)
    frags.append(arrow(sx + sw_ + 4, y1, 760 - rw1 / 2 - 4, y1, color=FIELD, sw=1.8))
    frags.append(fitbox(590, y1 - 44, 150, 30, "виконати + зберегти", size=10,
                        fill="#ffffff", stroke=FIELD, sw=1.3))
    frags.append(r1)

    # доріжка 2 (повтор)
    y2 = 275
    b2, w2, h2 = textbox(130, y2, ["Запит 2 (повтор)", "key = K"], size=12, fill=BG, stroke=NEG, sw=1.7)
    frags.append(b2)
    frags.append(arrow(130 + w2 / 2 + 4, y2, sx - 4, y2, color=NEG, sw=1.8))
    frags.append(fitbox(205, y2 + 16, 108, 30, "є K", size=11, fill="#ffffff", stroke=NEG, sw=1.3))
    r2, rw2, rh2 = textbox(760, y2, ["той самий R", "без списання"], size=12,
                           fill="#eaf0fd", stroke=NEG, sw=1.9)
    frags.append(arrow(sx + sw_ + 4, y2, 760 - rw2 / 2 - 4, y2, color=NEG, sw=1.8))
    frags.append(fitbox(600, y2 + 16, 140, 30, "відтворити R", size=10,
                        fill="#ffffff", stroke=NEG, sw=1.3))
    frags.append(r2)

    render(os.path.join(IMG, "idempotency-key.svg"), W, H, *frags)


# ── Фігура 4 (proj): гонка застовплення сходиться на унікальному обмеженні ────
def fig_claim_race():
    W, H = 980, 470
    frags = []
    frags.append(text(W / 2, 32, "Гонка застовплення вирішується в одній точці", size=16, bold=True))
    frags.append(text(W / 2, 54,
                      "два одночасні INSERT на той самий ключ — унікальне обмеження пропускає рівно один",
                      size=12, color=MUTED, italic=True))

    # дві заявки зліва
    a, aw, ah = textbox(140, 150, ["Запит A", "INSERT key=K"], size=13, fill=BG, stroke=INK, sw=1.8)
    b, bw, bh = textbox(140, 320, ["Запит B", "INSERT key=K"], size=13, fill=BG, stroke=INK, sw=1.8)
    frags.append(a)
    frags.append(b)

    # центральний вузол — унікальне обмеження
    cx, cy, cw, ch = 480, 235, 250, 130
    frags.append(rect(cx - cw / 2, cy - ch / 2, cw, ch, fill=FILL, stroke=INK, sw=2.4))
    frags.append(mtext(cx, cy - 16, ["UNIQUE", "(user_id, path, key)"], size=13, bold=True))
    frags.append(text(cx, cy + 34, "рівно один INSERT проходить", size=11, color=MUTED, italic=True))

    # стрілки заявок у вузол (сходяться)
    frags.append(arrow(140 + aw / 2 + 6, 150, cx - cw / 2 - 6, cy - 34, color=INK, sw=1.9))
    frags.append(arrow(140 + bw / 2 + 6, 320, cx - cw / 2 - 6, cy + 34, color=INK, sw=1.9))

    # два наслідки справа
    win, ww, wh = textbox(810, 150,
                          ["переможець", "рядок створено · in_progress", "→ робить роботу"],
                          size=12, fill="#eafaf1", stroke=FIELD, sw=2.0, color=FIELD, bold=True)
    los, lw, lh = textbox(810, 320,
                          ["програвач", "конфлікт на вставці", "→ читає рядок переможця · діє за станом"],
                          size=12, fill="#eaf0fd", stroke=NEG, sw=2.0, color=NEG, bold=True)
    frags.append(win)
    frags.append(los)

    # стрілки вузол → наслідки
    frags.append(arrow(cx + cw / 2 + 6, cy - 34, 810 - ww / 2 - 6, 150, color=FIELD, sw=2.0))
    frags.append(arrow(cx + cw / 2 + 6, cy + 34, 810 - lw / 2 - 6, 320, color=NEG, sw=2.0))

    render(os.path.join(IMG, "claim-race.svg"), W, H, *frags)


# ── Фігура 5 (proj): скінченний автомат стану ключа ──────────────────────────
def fig_key_state_machine():
    W, H = 1000, 520
    frags = []
    frags.append(text(W / 2, 30, "Автомат стану ключа ідемпотентності", size=16, bold=True))
    frags.append(text(W / 2, 52,
                      "щаслива доріжка — два переходи; решта — відповідь паралельному повтору за станом і відбитком",
                      size=12, color=MUTED, italic=True))

    yS = 180
    x0, x1, x2 = 160, 500, 840

    # три стани
    s0, w0, h0 = textbox(x0, yS, "немає", size=14, fill=BG, stroke=MUTED, sw=1.9, bold=True, color=MUTED)
    s1, w1, h1 = textbox(x1, yS, "in_progress", size=14, fill="#fff4e6", stroke=POS, sw=2.3, bold=True, color=POS)
    s2, w2, h2 = textbox(x2, yS, "completed", size=14, fill="#eafaf1", stroke=FIELD, sw=2.3, bold=True, color=FIELD)
    frags += [s0, s1, s2]

    # переходи щасливої доріжки
    frags.append(arrow(x0 + w0 / 2 + 6, yS, x1 - w1 / 2 - 6, yS, color=INK, sw=2.1))
    frags.append(fitbox(235, 128, 210, 34, "застовплення (INSERT · claim)", size=11,
                        fill=BG, stroke=INK, sw=1.3))
    frags.append(arrow(x1 + w1 / 2 + 6, yS, x2 - w2 / 2 - 6, yS, color=INK, sw=2.1))
    frags.append(fitbox(575, 128, 210, 34, "робота + UPDATE — 1 транзакція", size=11,
                        fill=BG, stroke=INK, sw=1.3))

    # виходи зі станів (над станами)
    frags.append(arrow(x1, yS - h1 / 2 - 4, x1, 108, color=MUTED, sw=1.6))
    frags.append(fitbox(370, 78, 260, 30, "reclaim: завис > оренди → перехоплення", size=10,
                        fill=BG, stroke=MUTED, sw=1.3))
    frags.append(arrow(x2, yS - h2 / 2 - 4, x2, 108, color=MUTED, sw=1.6))
    frags.append(fitbox(720, 78, 260, 30, "reaper: DELETE коли expires_at < now", size=10,
                        fill=BG, stroke=MUTED, sw=1.3))

    # шина «паралельний повтор» під станами (пунктир) — підпис одразу під станами,
    # з'єднувальні лінії стартують НИЖЧЕ підпису (не перетинають його)
    frags.append(text(W / 2, 210, "паралельний повтор — залежно від стану ключа й відбитка тіла:",
                      size=11, color=MUTED, italic=True))
    frags.append(line(260, 282, 850, 282, color=MUTED, sw=1.5, dash="5 4"))
    frags.append(line(x1, 232, x1, 282, color=MUTED, sw=1.5, dash="5 4"))  # in_progress → шина
    frags.append(line(x2, 232, x2, 282, color=MUTED, sw=1.5, dash="5 4"))  # completed → шина

    # три відповіді (пунктирні спуски із шини)
    frags.append(line(275, 282, 275, 330, color=NEG, sw=1.5, dash="5 4"))
    frags.append(fitbox(150, 330, 250, 64, "in_progress:\n409 + Retry-After", size=12,
                        fill="#eaf0fd", stroke=NEG, sw=1.9, color=NEG, bold=True))
    frags.append(line(560, 282, 560, 330, color=POS, sw=1.5, dash="5 4"))
    frags.append(fitbox(430, 330, 260, 64, "інший відбиток тіла:\n422 (звірка перша)", size=12,
                        fill="#fdecea", stroke=POS, sw=1.9, color=POS, bold=True))
    frags.append(line(845, 282, 845, 330, color=FIELD, sw=1.5, dash="5 4"))
    frags.append(fitbox(720, 330, 250, 64, "completed:\nточне відтворення", size=12,
                        fill="#eafaf1", stroke=FIELD, sw=1.9, color=FIELD, bold=True))

    render(os.path.join(IMG, "key-state-machine.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_retry_ambiguity()
    fig_method_classes()
    fig_idempotency_key()
    fig_claim_race()
    fig_key_state_machine()
    print("figures written")
