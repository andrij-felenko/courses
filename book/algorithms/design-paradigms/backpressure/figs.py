# -*- coding: utf-8 -*-
"""Фігури до теми «Протитиск (backpressure)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── дрібні помічники ────────────────────────────────────────────────────────
def polyline(pts, color=INK, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, color, sw, d))


def head_at(x, y, dx, dy, color=INK, size=10):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=11, dash=None):
    return line(x1, y1, x2, y2, color=color, sw=sw, dash=dash) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


def poly(pts, fill=FILL, stroke='none', sw=0, opacity=None):
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    op = ' fill-opacity="%.2f"' % opacity if opacity is not None else ''
    return ('<polygon points="%s" fill="%s"%s stroke="%s" stroke-width="%.1f"/>'
            % (p, fill, op, stroke, sw))


# ── Фігура 1: корінь задачі й три відповіді ──────────────────────────────────
def fig_dilemma():
    W, H = 940, 566
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Швидший виробник живить повільнішого споживача", size=18, bold=True))

    # верхня стрічка: виробник → буфер → споживач
    py = 66
    # виробник
    f.append(rect(52, py, 176, 74, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(text(140, py + 30, "Виробник", size=15, bold=True))
    f.append(text(140, py + 52, "λ = 1000/с", size=13, color=POS, bold=True))
    # товста (швидка) стрілка виробник → буфер
    f.append(varrow(230, py + 24, 320, py + 24, color=POS, sw=5.0, head=14))
    # зелена стрілка протитиску: буфер → виробник (проти течії)
    f.append(varrow(316, py + 54, 232, py + 54, color=FIELD, sw=2.4, head=11, dash="5 4"))
    f.append(text(274, py + 72, "протитиск", size=10, color=FIELD, bold=True))
    # буфер: ряд комірок, частина заповнена
    bx, by, cw = 330, py + 14, 26
    f.append(text(330 + 5 * cw / 2, py - 4, "буфер (черга)", size=12, color=MUTED))
    for i in range(5):
        filled = i < 3
        f.append(rect(bx + i * cw, by, cw - 4, 46,
                      fill=("#dfe6f7" if filled else BG), stroke=NEG, sw=1.4, rx=3))
    # тонка (повільна) стрілка
    f.append(varrow(470, py + 37, 560, py + 37, color=NEG, sw=2.0, head=10))
    # споживач
    f.append(rect(566, py, 176, 74, fill="#eafaf1", stroke=FIELD, sw=1.6))
    f.append(text(654, py + 30, "Споживач", size=15, bold=True))
    f.append(text(654, py + 52, "μ = 100/с", size=13, color=FIELD, bold=True))

    # підсумок над картами
    b, w, h = textbox(W / 2, 186,
                      "λ > μ:  надлишок 900/с накопичується — і система може зробити рівно три речі",
                      size=14, pad=11, fill="#f4f6f8", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)

    # три карти-відповіді
    cards = [
        (40,  "1. Нескінченний буфер", POS,     "#fdecea",
         ["черга росте без меж", "пам'ять вичерпується", "затримка → ∞"], "крах під навантаженням"),
        (350, "2. Відкидати надлишок", "#b5651d", "#fdf0e4",
         ["зайве викидаємо", "темп збережено", "але дані втрачено"], "живо, ціною втрат"),
        (660, "3. Протитиск", FIELD,   "#eafaf1",
         ["виробник чекає", "черга обмежена", "нічого не втрачено"], "стабільно, без втрат"),
    ]
    cw2, ctop, chh = 240, 232, 250
    for (cx0, title, col, tint, lines, verdict) in cards:
        # рамка карти
        f.append(rect(cx0, ctop, cw2, chh, fill=BG, stroke=col, sw=1.7))
        # шапка
        f.append(rect(cx0, ctop, cw2, 42, fill=tint, stroke=col, sw=1.7))
        f.append(text(cx0 + cw2 / 2, ctop + 27, title, size=14, bold=True, color=col))
        # тіло
        f.append(mtext(cx0 + cw2 / 2, ctop + 84, lines, size=14, lh=1.55))
        # вердикт
        f.append(line(cx0 + 18, ctop + chh - 56, cx0 + cw2 - 18, ctop + chh - 56, color="#e3e6ea", sw=1.2))
        f.append(mtext(cx0 + cw2 / 2, ctop + chh - 30, verdict, size=13, bold=True, color=col))
    return render(os.path.join(IMG, "producer-consumer-dilemma.svg"), W, H, *f)


# ── Фігура 2: затримка проти завантаження ρ = λ/μ ────────────────────────────
def fig_latency_utilization():
    W, H = 880, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Затримка в черзі злітає, коли завантаження ρ → 1", size=18, bold=True))

    L, R, T, Bt = 118, 812, 84, 430
    r0, r1 = 0.0, 1.2
    wmax = 12.0                                     # стеля осі затримки (W = 1/(1−ρ))

    def px(r): return L + (r - r0) / (r1 - r0) * (R - L)
    def py(w): return Bt - min(w, wmax) / wmax * (Bt - T)

    # зони: стабільна (ρ<1, зелена) і нестабільна (ρ≥1, червона)
    f.append(rect(px(0), T, px(1.0) - px(0), Bt - T, fill="#eafaf1", stroke='none', sw=0, rx=0))
    f.append(rect(px(1.0), T, px(r1) - px(1.0), Bt - T, fill="#fbe4e0", stroke='none', sw=0, rx=0))

    # сітка по X
    xr = 0.0
    while xr <= r1 + 1e-9:
        x = px(xr)
        f.append(line(x, T, x, Bt, color="#eceef1", sw=1.0))
        f.append(text(x, Bt + 22, ("%.1f" % xr), size=11, color=MUTED))
        xr += 0.2
    f.append(rect(L, T, R - L, Bt - T, fill="none", stroke=INK, sw=1.6))
    f.append(text((L + R) / 2, Bt + 46, "завантаження  ρ = λ / μ", size=13, color=INK))
    f.append(text(L - 8, T - 20, "затримка / довжина черги", size=12, color=INK, anchor="start"))

    # крива W = 1/(1−ρ)
    pts, r = [], 0.0
    while r <= 0.92:
        pts.append((px(r), py(1.0 / (1.0 - r))))
        r += 0.01
    f.append(polyline(pts, color=INK, sw=3.0))

    # вертикальна асимптота на ρ=1
    f.append(line(px(1.0), T, px(1.0), Bt, color=POS, sw=2.0, dash="6 5"))
    f.append(text(px(1.0), T - 6, "ρ = 1  (λ = μ)", size=12, color=POS, bold=True))

    # позначки-точки
    for r, lab, col, dy in ((0.5, "ρ=0.5: низька затримка", FIELD, 26),
                            (0.9, "ρ=0.9: затримка вдесятеро", "#b5651d", -14)):
        x, y = px(r), py(1.0 / (1.0 - r))
        f.append(circle(x, y, 6, fill=col, stroke=BG, sw=1.6))
        f.append(text(x + (10 if r < 0.7 else -6), y + dy, lab, size=11, color=col,
                      anchor=("start" if r < 0.7 else "end"), bold=True))

    # підписи зон
    f.append(text(px(0.42), T + 24, "стабільно: протитиск тримає ρ < 1", size=12.5,
                  color=FIELD, bold=True))
    f.append(text(px(1.1), T + 24, "черга → ∞", size=12.5, color=POS, bold=True))
    return render(os.path.join(IMG, "latency-utilization.svg"), W, H, *f)


# ── Фігура 3: штовхати проти тягти ───────────────────────────────────────────
def fig_push_vs_pull():
    W, H = 920, 476
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Штовхати (push) проти тягти (pull, за попитом)", size=18, bold=True))

    def actor(x, y, w, h, label, col, tint):
        return (rect(x, y, w, h, fill=tint, stroke=col, sw=1.6) +
                text(x + w / 2, y + h / 2 + 5, label, size=14, bold=True))

    prod_x, cons_x, aw, ah = 70, 700, 150, 66

    # ── Рядок 1: PUSH ──
    y1 = 88
    f.append(rect(28, y1 - 34, 92, 28, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(74, y1 - 15, "PUSH", size=14, bold=True, color=POS))
    f.append(actor(prod_x, y1, aw, ah, "Виробник", POS, "#fdecea"))
    f.append(actor(cons_x, y1, aw, ah, "Споживач", POS, "#fdecea"))
    # «повінь» стрілок
    cy = y1 + ah / 2
    for k in range(4):
        yy = y1 + 12 + k * 14
        f.append(varrow(prod_x + aw + 6, yy, cons_x - 66, yy, color=POS, sw=2.4, head=9))
    # переповнений буфер біля споживача
    for i in range(4):
        over = i >= 2
        f.append(rect(cons_x - 58, y1 - 2 + i * 17, 40, 14,
                      fill=("#fdecea" if over else "#dfe6f7"),
                      stroke=(POS if over else NEG), sw=1.3, rx=2))
    f.append(text(cons_x - 38, y1 + ah + 20, "буфер переповнено", size=10, color=POS))
    f.append(text(W / 2, y1 + ah + 46, "виробник шле власним темпом → без сигналу «стоп» споживач захлинається",
                  size=13, color=MUTED))

    # ── Рядок 2: PULL / попит ──
    y2 = 300
    f.append(rect(28, y2 - 34, 92, 28, fill="#eafaf1", stroke=FIELD, sw=1.5))
    f.append(text(74, y2 - 15, "PULL", size=14, bold=True, color=FIELD))
    f.append(actor(prod_x, y2, aw, ah, "Виробник", FIELD, "#eafaf1"))
    f.append(actor(cons_x, y2, aw, ah, "Споживач", FIELD, "#eafaf1"))
    # попит угору (проти течії): від споживача до виробника
    f.append(varrow(cons_x - 6, y2 + 16, prod_x + aw + 6, y2 + 16, color=NEG, sw=2.4, head=11, dash="6 5"))
    f.append(text(W / 2, y2 + 2, "попит  request(n)  ↑ проти течії", size=12, color=NEG, bold=True))
    # дані вниз, обмежено
    f.append(varrow(prod_x + aw + 6, y2 + 46, cons_x - 6, y2 + 46, color=FIELD, sw=2.8, head=11))
    f.append(text(W / 2, y2 + 66, "дані  ≤ n елементів  ↓ за течією", size=12, color=FIELD, bold=True))
    f.append(text(W / 2, y2 + ah + 40, "тече не більше, ніж замовлено → протитиск вбудовано в саму механіку",
                  size=13, color=MUTED))
    return render(os.path.join(IMG, "push-vs-pull.svg"), W, H, *f)


# ── Фігура 4: вікно приймача TCP як протитиск ────────────────────────────────
def fig_tcp_window():
    W, H = 940, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Вікно приймача TCP: повний буфер зупиняє відправника", size=18, bold=True))

    # відправник
    f.append(rect(56, 96, 168, 88, fill="#eef1fb", stroke=NEG, sw=1.6))
    f.append(text(140, 132, "Відправник", size=15, bold=True))
    f.append(text(140, 156, "шле ≤ вікно", size=12, color=MUTED))

    # приймальний буфер — вертикальна шкала
    bx, bw, btop, bh = 740, 96, 84, 176
    f.append(text(bx + bw / 2, btop - 12, "буфер приймача", size=12, color=MUTED))
    # заповнене (отримане, ще не прочитане) — знизу; вільне (= вікно) — зверху
    fill_h = 116
    f.append(rect(bx, btop, bw, bh - fill_h, fill=BG, stroke=NEG, sw=1.4))          # вільне
    f.append(rect(bx, btop + bh - fill_h, bw, fill_h, fill="#dfe6f7", stroke=NEG, sw=1.4))  # заповнене
    f.append(text(bx + bw / 2, btop + (bh - fill_h) / 2 + 4, "вікно", size=12, color=NEG, bold=True))
    f.append(text(bx + bw / 2, btop + bh - fill_h / 2 + 4, "дані", size=12, color=MUTED))
    # дужка «вікно = вільне місце»
    f.append(varrow(bx + bw + 14, btop + bh - fill_h, bx + bw + 14, btop, color=NEG, sw=1.6, head=9))
    f.append(text(bx + bw + 22, btop + (bh - fill_h) / 2, "вільне", size=11, color=NEG, anchor="start"))
    f.append(text(bx + bw + 22, btop + (bh - fill_h) / 2 + 15, "місце", size=11, color=NEG, anchor="start"))

    # застосунок читає (виток знизу буфера)
    f.append(varrow(bx + bw / 2, btop + bh + 6, bx + bw / 2, btop + bh + 44, color=FIELD, sw=2.0, head=10))
    f.append(rect(bx - 42, btop + bh + 44, bw + 84, 34, fill="#eafaf1", stroke=FIELD, sw=1.5))
    f.append(text(bx + bw / 2, btop + bh + 65, "застосунок читає повільно", size=11, bold=True, color=FIELD))

    # дані →
    f.append(varrow(226, 120, bx - 6, 120, color=NEG, sw=2.6, head=12))
    f.append(text((226 + bx) / 2, 108, "сегменти даних →", size=12, color=INK))
    # ← ACK + вікно
    f.append(varrow(bx - 6, 160, 226, 160, color=POS, sw=2.2, head=11, dash="6 5"))
    f.append(text((226 + bx) / 2, 178, "← ACK + оголошене вікно (rwnd)", size=12, color=POS, bold=True))

    # послідовність станів вікна внизу
    seq_y = 352
    f.append(text(346, seq_y - 18, "як живе вікно, коли застосунок відстає:", size=13, color=MUTED, bold=True))
    steps = [("4 КБ", "потік іде", FIELD, "#eafaf1"),
             ("2 КБ", "буфер повниться", "#b5651d", "#fdf0e4"),
             ("0", "СТОП + зонд", POS, "#fdecea"),
             ("3 КБ", "вичитав → оживає", FIELD, "#eafaf1")]
    sx = 96
    box_w, gap = 168, 44
    for i, (val, note, col, tint) in enumerate(steps):
        x = sx + i * (box_w + gap)
        f.append(rect(x, seq_y, box_w, 60, fill=tint, stroke=col, sw=1.6))
        f.append(text(x + box_w / 2, seq_y + 26, "вікно = " + val, size=13, bold=True, color=col))
        f.append(text(x + box_w / 2, seq_y + 48, note, size=11, color=INK))
        if i < len(steps) - 1:
            f.append(varrow(x + box_w + 4, seq_y + 30, x + box_w + gap - 4, seq_y + 30,
                            color=INK, sw=1.8, head=9))
    return render(os.path.join(IMG, "tcp-window.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# Фігури до вставки «Математика стабільності черги» (math-queue-stability.md)
# ════════════════════════════════════════════════════════════════════════════

# ── Фігура 5: черга — ціна випадковості ─────────────────────────────────────
def fig_randomness_queue():
    W, H = 1000, 610
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Черга — ціна випадковості, а не завантаження", size=18, bold=True))

    XL, XR = 92, 902
    TMAX = 14.0
    def px(t): return XL + t / TMAX * (XR - XL)

    # ── верх: рівномірно (D/D/1) — ніхто ніколи не чекає
    f.append(text(XL, 74, "Рівномірно: прихід рівно кожні 2 с, обслуговування рівно 1 с",
                  size=13.5, color=INK, anchor="start", bold=True))
    y_lane = 150
    f.append(line(XL, y_lane + 34, XR, y_lane + 34, color=INK, sw=1.6))
    for tt in range(0, 15, 2):
        f.append(line(px(tt), y_lane + 34, px(tt), y_lane + 40, color=INK, sw=1.2))
        f.append(text(px(tt), y_lane + 56, str(tt), size=10.5, color=MUTED))
    f.append(text(XR + 42, y_lane + 38, "час, с", size=11.5, color=MUTED))
    for i, a in enumerate([2, 4, 6, 8, 10, 12]):
        f.append(varrow(px(a), 96, px(a), y_lane - 5, color=NEG, sw=1.7, head=8))
        f.append(text(px(a), 90, str(i + 1), size=10.5, color=NEG, bold=True))
        f.append(rect(px(a), y_lane, px(a + 1) - px(a), 30, fill="#eafaf1",
                      stroke=FIELD, sw=1.5, rx=3))
        f.append(text((px(a) + px(a + 1)) / 2, y_lane + 20, str(i + 1), size=11,
                      color=FIELD, bold=True))
    f.append(text(XL, 240, "жоден не чекав ані секунди · середнє очікування = 0",
                  size=13, color=FIELD, anchor="start", bold=True))

    # ── низ: випадково (M/M/1) — той самий ρ, але черга є
    f.append(text(XL, 300, "Випадково: той самий середній темп, той самий середній час обслуговування",
                  size=13.5, color=INK, anchor="start", bold=True))
    y_lane = 400
    jobs = [(1.2, 1.2, 0.6), (1.8, 1.8, 1.5), (2.3, 3.3, 0.4),
            (7.0, 7.0, 2.0), (7.4, 9.0, 0.5), (12.0, 12.0, 1.0)]
    f.append(line(XL, y_lane + 34, XR, y_lane + 34, color=INK, sw=1.6))
    for tt in range(0, 15, 2):
        f.append(line(px(tt), y_lane + 34, px(tt), y_lane + 40, color=INK, sw=1.2))
        f.append(text(px(tt), y_lane + 56, str(tt), size=10.5, color=MUTED))
    f.append(text(XR + 42, y_lane + 38, "час, с", size=11.5, color=MUTED))
    f.append(text(XL - 6, y_lane - 16, "чекає", size=10.5, color=POS, anchor="end"))
    f.append(text(XL - 6, y_lane + 20, "на сервері", size=10.5, color=FIELD, anchor="end"))
    for i, (a, st, sl) in enumerate(jobs):
        f.append(varrow(px(a), 322, px(a), y_lane - 28, color=NEG, sw=1.7, head=8))
        f.append(text(px(a), 316, str(i + 1), size=10.5, color=NEG, bold=True))
        if st > a + 1e-9:
            f.append(rect(px(a), y_lane - 24, px(st) - px(a), 14,
                          fill="#fbe4e0", stroke=POS, sw=1.4, rx=3))
        f.append(rect(px(st), y_lane, px(st + sl) - px(st), 30, fill="#eafaf1",
                      stroke=FIELD, sw=1.5, rx=3))
        f.append(text((px(st) + px(st + sl)) / 2, y_lane + 20, str(i + 1), size=11,
                      color=FIELD, bold=True))
    f.append(text(XL, 490, "№3 і №5 чекали (червоне) — хоч сервер простоював половину часу",
                  size=13, color=POS, anchor="start", bold=True))

    # ── підсумок
    b, bw, bh = textbox(W / 2, 550,
                        ["Однакове ρ = 0.5, однакове середнє обслуговування — а черга різна:",
                          "рівномірно → очікування 0 · випадково → очікування ≈ цілий час обслуговування"],
                        size=13, fill="#f2f6fc", stroke=NEG, sw=1.6, pad=14)
    f.append(b)
    return render(os.path.join(IMG, "randomness-makes-queue.svg"), W, H, *f)


# ── Фігура 6: ланцюг станів і переріз балансу ───────────────────────────────
def fig_birth_death_cut():
    W, H = 1000, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Ланцюг станів: скільки одиниць у системі", size=18, bold=True))

    ys = 168
    r = 30
    nodes = [(112, "0"), (250, "1"), (388, "2"), (610, "n"), (790, "n+1")]
    f.append(text(499, ys + 8, "…", size=26, color=MUTED))
    f.append(text(908, ys + 8, "…", size=26, color=MUTED))

    def edge(x1, x2, up, lab, col):
        """Дуга-стрілка між станами: up=True — λ згори, False — μ знизу."""
        off = -(r + 6) if up else (r + 6)
        y = ys + off
        a, b_ = (x1 + r + 4, x2 - r - 4) if x2 > x1 else (x1 - r - 4, x2 + r + 4)
        out = [varrow(a, y, b_, y, color=col, sw=2.0, head=9)]
        out.append(text((x1 + x2) / 2, y + (-10 if up else 20), lab, size=14,
                        color=col, bold=True))
        return out

    # стани
    for x, lab in nodes:
        f.append(circle(x, ys, r, fill="#f2f6fc", stroke=NEG, sw=2.0))
        f.append(text(x, ys + 6, lab, size=15, color=INK, bold=True))

    # переходи вгору (λ) і вниз (μ)
    for (x1, _), (x2, _) in ((nodes[0], nodes[1]), (nodes[1], nodes[2]), (nodes[3], nodes[4])):
        f.extend(edge(x1, x2, True, "λ", POS))
        f.extend(edge(x2, x1, False, "μ", FIELD))
    # обірвані переходи біля «…»
    f.append(varrow(388 + r + 4, ys - r - 6, 470, ys - r - 6, color=POS, sw=2.0, head=9))
    f.append(varrow(470, ys + r + 6, 388 + r + 4, ys + r + 6, color=FIELD, sw=2.0, head=9))
    f.append(varrow(528, ys - r - 6, 610 - r - 4, ys - r - 6, color=POS, sw=2.0, head=9))
    f.append(varrow(610 - r - 4, ys + r + 6, 528, ys + r + 6, color=FIELD, sw=2.0, head=9))
    f.append(varrow(790 + r + 4, ys - r - 6, 880, ys - r - 6, color=POS, sw=2.0, head=9))
    f.append(varrow(880, ys + r + 6, 790 + r + 4, ys + r + 6, color=FIELD, sw=2.0, head=9))

    # переріз між n і n+1
    xc = 700
    f.append(line(xc, ys - 118, xc, ys + 96, color=INK, sw=2.2, dash="7 5"))
    f.append(text(xc, ys - 128, "переріз", size=13, color=INK, bold=True))

    # рівняння балансу
    b, bw, bh = textbox(300, 340,
                        ["Крізь будь-який переріз потік угору = потік униз:",
                         "λ · pₙ  =  μ · pₙ₊₁     →     pₙ₊₁ = ρ · pₙ"],
                        size=13.5, fill="#f7f7f9", stroke=INK, sw=1.6, pad=13)
    f.append(b)
    b, bw, bh = textbox(740, 340,
                        ["Отже pₙ = ρⁿ · p₀, а сума ймовірностей = 1:",
                         "p₀ · (1 + ρ + ρ² + …) = 1  —  збігається ЛИШЕ за ρ < 1"],
                        size=13.5, fill="#eafaf1", stroke=FIELD, sw=1.7, pad=13)
    f.append(b)

    f.append(text(W / 2, 430, "Стабільність — не додаткове припущення, а умова, за якої розв'язок узагалі існує",
                  size=13.5, color=NEG, bold=True))
    return render(os.path.join(IMG, "birth-death-cut.svg"), W, H, *f)


# ── Фігура 7: три режими N(t) ───────────────────────────────────────────────
def fig_three_regimes():
    import random as _rnd

    def traj(lam, mu, T, step, seed, K=None):
        """Проста подієва симуляція M/M/1 (або M/M/1/K); повертає N на сітці."""
        rg = _rnd.Random(seed)
        t = 0.0; n = 0
        na = rg.expovariate(lam); nd = float('inf')
        out = []; grid = 0.0
        while grid <= T:
            nxt = min(na, nd)
            if nxt > grid:
                out.append((grid, n)); grid += step; continue
            t = nxt
            if na <= nd:
                if K is None or n < K:
                    n += 1
                    if n == 1: nd = t + rg.expovariate(mu)
                na = t + rg.expovariate(lam)
            else:
                n -= 1
                nd = t + rg.expovariate(mu) if n > 0 else float('inf')
        return out

    W, H = 1000, 700
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Три режими: що робить довжина черги з часом", size=18, bold=True))

    L, R, T, Bt = 108, 800, 100, 500
    TMAX, NMAX = 600.0, 100.0
    def px(t): return L + t / TMAX * (R - L)
    def py(n): return Bt - min(n, NMAX) / NMAX * (Bt - T)

    # сітка
    for nn in range(0, 101, 20):
        f.append(line(L, py(nn), R, py(nn), color="#eceef1", sw=1.0))
        f.append(text(L - 12, py(nn) + 4, str(nn), size=11, color=MUTED, anchor="end"))
    for tt in range(0, 601, 100):
        f.append(line(px(tt), T, px(tt), Bt, color="#eceef1", sw=1.0))
        f.append(text(px(tt), Bt + 22, str(tt), size=11, color=MUTED))
    f.append(rect(L, T, R - L, Bt - T, fill="none", stroke=INK, sw=1.6))
    f.append(text((L + R) / 2, Bt + 48, "час, с   (μ = 1 обслуговування за секунду)", size=13, color=INK))
    f.append(text(L - 12, T - 22, "N(t) — одиниць у системі", size=12.5, color=INK, anchor="start"))

    # теоретична пряма (λ−μ)·t для ρ=1.15
    f.append(polyline([(px(0), py(0)), (px(600), py(0.15 * 600))], color=INK, sw=1.8, dash="7 5"))
    f.append(text(300, 214, "нахил λ − μ", size=12.5, color=INK, bold=True, anchor="end"))
    f.append(varrow(306, 210, 372, 246, color=INK, sw=1.4, head=8))

    # траєкторії
    curves = [(1.15, POS, "ρ = 1.15  →  росте лінійно, темпом λ − μ"),
              (1.00, "#b5651d", "ρ = 1  →  не осідає, блукає вгору ∝ √t"),
              (0.80, FIELD, "ρ = 0.8  →  коливається біля ρ/(1−ρ) = 4")]
    ends = {}
    for lam, col, lab in curves:
        pts = [(px(t), py(n)) for (t, n) in traj(lam, 1.0, TMAX, 2.0, seed=int(lam * 1000) + 7)]
        f.append(polyline(pts, color=col, sw=2.4))
        ends[lam] = pts[-1][1]

    # крива √t-орієнтир для ρ=1
    sq = [(px(t), py(1.13 * math.sqrt(t))) for t in range(0, 601, 10)]
    f.append(polyline(sq, color="#b5651d", sw=1.6, dash="5 4"))
    f.append(text(690, 452, "≈ 1.13·√t", size=12, color="#b5651d", bold=True))
    f.append(varrow(690, 444, 668, 410, color="#b5651d", sw=1.3, head=7))

    # підписи праворуч, рознесені по вертикалі
    slots = [(1.15, 150), (1.00, 372), (0.80, 470)]
    for (lam, ylab), (_, col, lab) in zip(slots, curves):
        f.append(line(R + 4, ends[lam], R + 22, ylab, color=col, sw=1.2, dash="3 3"))
        f.append(circle(R, ends[lam], 4.5, fill=col, stroke=BG, sw=1.2))
        f.append(text(R + 28, ylab + 4, lab.split("→")[0].strip(), size=12.5, color=col,
                      anchor="start", bold=True))

    # легенда-пояснення знизу
    rows = [("ρ = 0.8", FIELD, "стабільно: N коливається біля скінченного середнього ρ/(1−ρ) = 4"),
            ("ρ = 1", "#b5651d", "критично: усталеного стану НЕМА — N блукає вгору порядку √t"),
            ("ρ = 1.15", POS, "нестабільно: N росте лінійно, темпом λ − μ = 0.15 за секунду")]
    y0 = 604
    for i, (tag, col, txt) in enumerate(rows):
        y = y0 + i * 28
        f.append(rect(L, y - 10, 16, 12, fill=col, stroke=col, sw=1.0, rx=2))
        f.append(text(L + 26, y, tag, size=12.5, color=col, anchor="start", bold=True))
        f.append(text(L + 104, y, "— " + txt, size=12.5, color=INK, anchor="start"))
    return render(os.path.join(IMG, "three-regimes.svg"), W, H, *f)


# ── Фігура 8: обрізаний ланцюг — стеля K ────────────────────────────────────
def fig_bounded_chain():
    W, H = 1000, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Обрізаний ланцюг: стеля K робить нормування можливим завжди",
                  size=18, bold=True))

    ys = 158
    r = 30
    nodes = [(112, "0"), (248, "1"), (384, "2"), (606, "K−1"), (742, "K")]
    f.append(text(495, ys + 8, "…", size=26, color=MUTED))

    def edge(x1, x2, up, lab, col):
        off = -(r + 6) if up else (r + 6)
        y = ys + off
        a, b_ = (x1 + r + 4, x2 - r - 4) if x2 > x1 else (x1 - r - 4, x2 + r + 4)
        return [varrow(a, y, b_, y, color=col, sw=2.0, head=9),
                text((x1 + x2) / 2, y + (-10 if up else 20), lab, size=14, color=col, bold=True)]

    for x, lab in nodes:
        f.append(circle(x, ys, r, fill="#f2f6fc", stroke=NEG, sw=2.0))
        f.append(text(x, ys + 6, lab, size=14, color=INK, bold=True))
    for (x1, _), (x2, _) in ((nodes[0], nodes[1]), (nodes[1], nodes[2]), (nodes[3], nodes[4])):
        f.extend(edge(x1, x2, True, "λ", POS))
        f.extend(edge(x2, x1, False, "μ", FIELD))
    f.append(varrow(384 + r + 4, ys - r - 6, 466, ys - r - 6, color=POS, sw=2.0, head=9))
    f.append(varrow(466, ys + r + 6, 384 + r + 4, ys + r + 6, color=FIELD, sw=2.0, head=9))
    f.append(varrow(524, ys - r - 6, 606 - r - 4, ys - r - 6, color=POS, sw=2.0, head=9))
    f.append(varrow(606 - r - 4, ys + r + 6, 524, ys + r + 6, color=FIELD, sw=2.0, head=9))

    # стіна за K
    xw = 828
    f.append(line(xw, ys - 62, xw, ys + 62, color=POS, sw=5.0))
    f.append(line(742 + r + 4, ys, xw - 6, ys, color=POS, sw=2.0, dash="6 4"))
    f.append(text(xw - 42, ys - 44, "✗", size=22, color=POS, bold=True))
    f.append(text(xw + 12, ys - 12, "далі ходу нема:", size=12.5, color=POS,
                  anchor="start", bold=True))
    f.append(text(xw + 12, ys + 8, "виробник блокується", size=12.5, color=POS, anchor="start"))
    f.append(text(xw + 12, ys + 28, "або надлишок відкидають", size=12.5, color=POS, anchor="start"))

    # формули
    b, bw, bh = textbox(268, 310,
                        ["Сума СКІНЧЕННА — нормується за будь-якого ρ,",
                         "навіть за ρ > 1:",
                         "pₙ = ρⁿ · (1 − ρ) / (1 − ρ^(K+1))"],
                        size=13.5, fill="#eafaf1", stroke=FIELD, sw=1.7, pad=13)
    f.append(b)
    b, bw, bh = textbox(716, 310,
                        ["Фактичний темп сам падає під μ:",
                         "λ_еф = λ · (1 − p_K) = μ · (1 − p₀)  ≤  μ",
                         "Стеля затримки:  W ≤ K / μ"],
                        size=13.5, fill="#f2f6fc", stroke=NEG, sw=1.7, pad=13)
    f.append(b)

    # приклад зі статті
    b, bw, bh = textbox(W / 2, 442,
                        ["λ = 1000/с,  μ = 100/с  (ρ = 10 — безнадійно нестабільно),  K = 10:",
                         "p_K = 0.90  →  λ_еф = 1000 · 0.10 = 100 = μ   ·   W ≤ 10/100 = 0.1 с",
                         "Місткість буфера K — це і є бюджет затримки"],
                        size=13.5, fill="#f7f7f9", stroke=INK, sw=1.8, pad=14)
    f.append(b)
    return render(os.path.join(IMG, "bounded-chain.svg"), W, H, *f)


# ── Фігура 9 (hist): індикаторна діаграма — протитиск як вкрадена площа ─────
def fig_indicator():
    W, H = 940, 580
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Індикаторна діаграма: у машинній залі протитиск — це вкрадена площа",
                  size=18, bold=True))

    L, R, T, Bt = 118, 762, 96, 442
    PMAX, PSCALE = 100.0, 112.0          # тиск у котлі та стеля осі
    VCUT, VMAX = 0.30, 1.00              # відсічка та повний хід
    V0 = 0.08                            # шкідливий простір
    PBACK = 22.0                         # тиск на випуску (протитиск)

    def px(v): return L + v / 1.06 * (R - L)
    def py(p): return Bt - p / PSCALE * (Bt - T)

    # ── смуга втрат: між ідеальним випуском (p=0) і справжнім (p=PBACK)
    f.append(poly([(px(V0), py(0)), (px(VMAX), py(0)),
                   (px(VMAX), py(PBACK)), (px(V0), py(PBACK))],
                  fill=POS, opacity=0.20))

    # ── корисна площа циклу (замкнена петля)
    loop = [(px(V0), py(PMAX)), (px(VCUT), py(PMAX))]
    v = VCUT
    while v <= VMAX + 1e-9:
        loop.append((px(v), py(PMAX * VCUT / v)))
        v += 0.01
    loop += [(px(VMAX), py(PBACK)), (px(V0), py(PBACK))]
    f.append(poly(loop, fill=FIELD, opacity=0.16))
    f.append(polyline(loop + [loop[0]], color=INK, sw=2.6))

    # ── осі та сітка
    f.append(line(px(0), py(0), px(1.06), py(0), color=INK, sw=1.6))
    f.append(line(px(0), py(0), px(0), T - 6, color=INK, sw=1.6))
    f.append(text(px(0) - 10, T + 4, "тиск", size=12, color=INK, anchor="end"))
    f.append(text(px(0) - 10, T + 20, "у циліндрі", size=12, color=INK, anchor="end"))
    f.append(text((px(0) + px(VMAX)) / 2, py(0) + 34, "хід поршня  (об'єм)", size=13, color=INK))

    # нульова лінія тиску — ідеальний випуск
    f.append(line(px(V0), py(0), px(VMAX), py(0), color=NEG, sw=2.0, dash="7 5"))
    f.append(text(px(VMAX) + 8, py(0) + 5, "ідеал: 0", size=11, color=NEG, anchor="start", bold=True))
    # лінія протитиску
    f.append(text(px(VMAX) + 8, py(PBACK) + 5, "насправді", size=11, color=POS, anchor="start", bold=True))

    # ── підписи ділянок циклу (ведемо повз лінії)
    f.append(text(px((V0 + VCUT) / 2) + 46, py(PMAX) - 12, "впуск: пара штовхає поршень",
                  size=12.5, color=INK, bold=True, anchor="start"))
    f.append(text(px(0.60), py(52) - 4, "розширення", size=12.5, color=INK, bold=True))
    f.append(text(px(0.55), py(PMAX * VCUT / 0.55) + 44, "корисна робота", size=15,
                  color=FIELD, bold=True))
    f.append(text(px(0.55), py(PBACK / 2) + 5, "робота, з'їдена протитиском", size=13.5,
                  color=POS, bold=True))

    # стрілка «протитиск» до лінії випуску
    f.append(varrow(px(0.16), py(64), px(0.16), py(PBACK) - 4, color=POS, sw=2.2, head=10))
    f.append(text(px(0.16), py(70), "ПРОТИТИСК", size=12.5, color=POS, bold=True))
    f.append(text(px(0.16), py(84), "тиск на випуску", size=11, color=POS))

    # ── висновок
    b, w, h = textbox(W / 2, 512,
                      ["Що вищий тиск на випуску — то товща червона смуга й то менша зелена площа.",
                       "Півтора століття протитиск означав РІВНО ЦЕ: роботу, яку в тебе вкрали."],
                      size=14, pad=13, fill="#f7f7f9", stroke=INK, sw=1.8, bold=False)
    f.append(b)
    return render(os.path.join(IMG, "indicator-backpressure.svg"), W, H, *f)


# ── Фігура 10 (hist): механізм і назва — дві доріжки ────────────────────────
def fig_name_vs_mechanism():
    W, H = 1000, 726
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Механізм працював піввіку — під іншою назвою", size=18, bold=True))

    LX, RX = 470.0, 530.0                # рейки двох доріжок
    LW, RW = 400.0, 400.0
    LBX, RBX = 40.0, 560.0               # ліві/праві рамки

    # шапки доріжок
    f.append(fitbox(LBX, 62, LW, 34, "МЕХАНІЗМ — річ уже працює",
                    size=14, bold=True, fill="#eef1fb", stroke=NEG, sw=1.7, color=NEG))
    f.append(fitbox(RBX, 62, RW, 34, "НАЗВА «back pressure» — слово живе деінде",
                    size=14, bold=True, fill="#fdecea", stroke=POS, sw=1.7, color=POS))

    # рейки
    f.append(line(LX, 106, LX, 606, color=NEG, sw=3.0))
    f.append(line(RX, 106, RX, 606, color=POS, sw=3.0))

    def ev(side, y, h, lines):
        col, tint = (NEG, "#eef1fb") if side == 'L' else (POS, "#fdecea")
        x = LBX if side == 'L' else RBX
        out = [fitbox(x, y, LW if side == 'L' else RW, h, lines,
                      size=13, bold=True, fill=tint, stroke=col, sw=1.6, color=INK)]
        cy = y + h / 2
        if side == 'L':
            out.append(line(x + LW, cy, LX, cy, color=col, sw=1.8))
            out.append(circle(LX, cy, 6, fill=col, stroke=BG, sw=1.8))
        else:
            out.append(line(RX, cy, x, cy, color=col, sw=1.8))
            out.append(circle(RX, cy, 6, fill=col, stroke=BG, sw=1.8))
        return out

    f += ev('R', 116, 76, ["1848 · парова машина",
                           "тиск на випуску, проти якого штовхає поршень:",
                           "втрата, яку інженер мусить мінімізувати"])
    f += ev('L', 206, 58, ["1963 · телетайп ASR-33",
                           "Ctrl-S спиняє зчитувач перфострічки — це XOFF"])
    f += ev('L', 278, 58, ["1973 · конвеєр Unix",
                           "на повному буфері (4 КБ) письменник засинає"])
    f += ev('L', 350, 58, ["1974 · RFC 675 (TCP)",
                           "«вікно = 0» спиняє відправника"])
    f += ev('L', 422, 76, ["1997 · Ethernet 802.3x",
                           "кадр PAUSE спиняє порт — і зветься",
                           "«керуванням потоком»"])
    f += ev('R', 422, 76, ["1990-ті · комутатори Ethernet",
                           "«backpressure» = навмисна колізія,",
                           "щоб заткнути відправника"])
    f += ev('R', 512, 76, ["2003 · теорія мереж",
                           "Нілі називає «backpressure» алгоритм",
                           "Тассіуласа й Ефремідеса (1992)"])

    # доріжки сходяться
    f.append(line(LX, 606, 500, 622, color=NEG, sw=3.0))
    f.append(line(RX, 606, 500, 622, color=POS, sw=3.0))
    f.append(varrow(500, 622, 500, 636, color=FIELD, sw=3.0, head=11))
    f.append(fitbox(60, 640, 880, 64,
                    ["2013–2015 · Reactive Streams — тут назва нарешті прикріплюється до механізму",
                     "1.0.0 — 30 квітня 2015 · JDK 9 (вересень 2017) — java.util.concurrent.Flow"],
                    size=14, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.8, color=INK))
    return render(os.path.join(IMG, "name-vs-mechanism.svg"), W, H, *f)


# ── Фігура (proj): два прогони в часі — черга й затримка ─────────────────────
def fig_two_runs():
    W, H = 980, 520
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Один конвеєр, два прогони: різниця — один рядок", size=18, bold=True))

    # легенда — над панелями, де жодної лінії немає
    f.append(line(268, 52, 306, 52, color=POS, sw=3.4))
    f.append(text(314, 56, "черга без стелі", size=12.5, color=POS, anchor="start", bold=True))
    f.append(line(520, 52, 558, 52, color=FIELD, sw=3.4))
    f.append(text(566, 56, "черга зі стелею 32", size=12.5, color=FIELD, anchor="start", bold=True))

    T, Bt, tmax = 92, 388, 20.0

    def panel(L, R, ymax, ticks, head, redlab, greenlab, gval):
        """Одна панель. Усередині рамки ліній НЕМА — тільки дві криві,
        тож написам просторо: позначки осей винесені назовні."""
        g = []

        def px(t): return L + t / tmax * (R - L)

        def py(v): return Bt - v / ymax * (Bt - T)

        g.append(text((L + R) / 2, 74, head, size=14, bold=True))
        g.append(rect(L, T, R - L, Bt - T, fill="none", stroke=INK, sw=1.6))
        for v, lab in ticks:                       # позначки осі Y — ліворуч від рамки
            y = py(v)
            g.append(line(L - 6, y, L, y, color=INK, sw=1.4))
            g.append(text(L - 11, y + 4, lab, size=11, color=MUTED, anchor="end"))
        for t in (0, 5, 10, 15, 20):               # позначки осі X — під рамкою
            x = px(t)
            g.append(line(x, Bt, x, Bt + 6, color=INK, sw=1.4))
            g.append(text(x, Bt + 22, "%d" % t, size=11, color=MUTED))
        g.append(text((L + R) / 2, Bt + 44, "час від старту, с", size=12, color=MUTED))
        # без стелі — з кута в кут; зі стелею — при самій осі
        g.append(polyline([(px(0), py(0)), (px(tmax), py(ymax))], color=POS, sw=3.2))
        g.append(polyline([(px(0), py(gval)), (px(tmax), py(gval))], color=FIELD, sw=3.2))
        g.append(mtext(px(1.2), py(ymax * 0.90), redlab, size=12.5, color=POS,
                       anchor="start", lh=1.35, bold=True))
        g.append(text(px(9.5), Bt - 16, greenlab, size=12, color=FIELD, anchor="start", bold=True))
        return g

    f += panel(96, 470, 9000.0,
               [(0, "0"), (2250, "2 250"), (4500, "4 500"), (6750, "6 750"), (9000, "9 000")],
               "довжина черги, елементів",
               ["без стелі:", "+450 елементів", "щосекунди"],
               "зі стелею: 32", 32.0)
    f += panel(566, 940, 18.0,
               [(0, "0"), (4.5, "4.5"), (9, "9.0"), (13.5, "13.5"), (18, "18.0")],
               "затримка елемента, с",
               ["без стелі:", "+0.9 секунди", "щосекунди"],
               "зі стелею: 0.68 с", 0.68)

    b, bw, bh = textbox(W / 2, 474,
                        ["Пропускна здатність обох прогонів — 50 елементів/с.",
                         "Необмежена черга не додала жодного."],
                        size=14, pad=13, fill="#f7f7f9", stroke=INK, sw=1.8, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "two-runs.svg"), W, H, *f)


# ── Фігура (proj): кільце протитиску й розірване кільце ──────────────────────
def fig_cycle_deadlock():
    W, H = 980, 462
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Напрям тиску має бути ациклічним", size=18, bold=True))
    f.append(line(490, 50, 490, 340, color="#e3e6ea", sw=1.4))

    def cells(x, y, n, filled, col, tint):
        g = []
        for i in range(n):
            g.append(rect(x + i * 28, y, 24, 40,
                          fill=(tint if i < filled else BG), stroke=col, sw=1.4, rx=3))
        return g

    def stage(x, y, label):
        return (rect(x, y, 120, 60, fill="#f4f6f8", stroke=INK, sw=1.7) +
                text(x + 60, y + 36, label, size=15, bold=True))

    def ring(x0, sub, sub_col, lab_a, col_a, lab_b, col_b,
             back_col, back_dash, back_full, back_lab, note, note_col, drop):
        g = [text(x0 + 220, 62, sub, size=14, bold=True, color=sub_col)]
        # верхній ряд (дані): A → forward → B
        g.append(text(x0 + 90, 88, lab_a, size=11, color=col_a, bold=True))
        g.append(text(x0 + 350, 88, lab_b, size=11, color=col_b, bold=True))
        g.append(stage(x0 + 30, 100, "етап A"))
        g.append(stage(x0 + 290, 100, "етап B"))
        g.append(text(x0 + 224, 100, "forward (4) — повна", size=11.5, color=POS))
        g += cells(x0 + 170, 110, 4, 4, POS, "#fdecea")
        g.append(varrow(x0 + 152, 130, x0 + 166, 130, color=INK, sw=2.2, head=9))
        g.append(varrow(x0 + 282, 130, x0 + 288, 130, color=INK, sw=2.2, head=9))
        # нижній ряд (зворотний шлях): B → back → A
        g.append(line(x0 + 350, 160, x0 + 350, 262, color=back_col, sw=2.2, dash=back_dash))
        g.append(varrow(x0 + 350, 262, x0 + 284, 262, color=back_col, sw=2.2, head=10, dash=back_dash))
        g += cells(x0 + 170, 242, 4, back_full, back_col, ("#fdecea" if back_full == 4 else "#eafaf1"))
        g.append(text(x0 + 224, 300, back_lab, size=11.5, color=back_col))
        g.append(line(x0 + 168, 262, x0 + 90, 262, color=back_col, sw=2.2, dash=back_dash))
        g.append(varrow(x0 + 90, 262, x0 + 90, 166, color=back_col, sw=2.2, head=10, dash=back_dash))
        # напис усередині кільця — там, де жодна лінія не проходить
        b, bw, bh = textbox(x0 + 220, 211, note, size=12, pad=11,
                            fill=BG, stroke=note_col, sw=1.7, color=INK, bold=True)
        g.append(b)
        if drop:  # відгалуження «не влізло — викидаємо»
            g.append(varrow(x0 + 350, 216, x0 + 392, 286, color=POS, sw=2.0, head=10, dash="4 3"))
            g.append(mtext(x0 + 392, 308, ["не влізло —", "викидаємо"], size=11, color=POS, bold=True))
        return g

    f += ring(30, "кільце: тиск замикається сам на себе", POS,
              "спить у forward <-", POS, "спить у back <-", POS,
              POS, None, 4, "back (4) — повна",
              ["forward 4 + back 4 = 8 місць", "у чергах 8 + по 1 у руках = 10",
               "10 елементів на 8 місць —", "рухатися нікому"], POS, False)
    f += ring(510, "розірване кільце: зворотна дуга не блокує", FIELD,
              "чекає — і дочекається", FIELD, "не спить у send", FIELD,
              FIELD, "6 5", 2, "back (4) — з відкиданням",
              ["B ніколи не спить у send,", "тож forward спорожняється,", "тож A прокидається:",
               "тиск доходить до джерела"], FIELD, True)

    b, bw, bh = textbox(W / 2, 406,
                        ["У кільці звільнити місце може лише той, хто сам уже спить у send.",
                         "Розірвати кільце — окремим етапом, неблокувальною дугою або кредитами."],
                        size=13, pad=13, fill="#f7f7f9", stroke=INK, sw=1.8, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "cycle-deadlock.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_dilemma(), fig_latency_utilization(), fig_push_vs_pull(), fig_tcp_window(),
          fig_randomness_queue(), fig_birth_death_cut(), fig_three_regimes(),
          fig_bounded_chain(), fig_indicator(), fig_name_vs_mechanism(),
          fig_two_runs(), fig_cycle_deadlock()]
    print("written:")
    for p in ps:
        print("  ", p)
