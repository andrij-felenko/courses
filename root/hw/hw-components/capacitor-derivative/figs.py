# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: чому i = C·dV/dt — заряд як висота, струм як нахил ───────────────
# Дві синхронні криві в одному часі: угорі V(t) (скільки заряду накопичено,
# бо Q = C·V), унизу i(t) (як швидко заряд тече). Там, де V крута — i велике;
# там, де V полога (плато) — i ≈ 0. Один вертикальний зріз показує: значення
# струму = НАХИЛ напруги в ту саму мить. Це робить видимим «струм = похідна V».

def fig_current_is_slope():
    W, H = 680, 500
    ox = 90                       # ліва вісь (спільна для обох графіків)
    # верхня панель V(t)
    vtop, vbot = 70, 200
    # нижня панель i(t)
    itop, ibot = 290, 410
    xr = 540                      # права межа осі часу
    t0 = ox + 10

    # три фази часу: швидкий ріст, плато, повільний ріст
    tA = t0 + 150                 # кінець крутого підйому
    tB = tA + 150                 # кінець плато
    tC = xr - 10                  # кінець пологого підйому

    parts = []

    # ── панель напруги (накопичений заряд) ───────────────────────────────────
    parts.append(arrow(ox, vbot, xr + 24, vbot, color=MUTED, sw=1.3))     # вісь t
    parts.append(arrow(ox, vbot, ox, vtop - 14, color=MUTED, sw=1.3))     # вісь V
    parts.append(text(xr + 30, vbot + 4, 't', 13, MUTED, 'start', italic=True))
    parts.append(text(ox - 10, vtop - 18, 'V', 13, MUTED, 'end', italic=True))
    parts.append(text(ox - 10, vtop - 4, '(заряд Q=CV)', 10, MUTED, 'end'))

    # крива V: крутий підйом → плато → пологий підйом
    vlo = vbot - 8
    vhi = vtop + 14
    vmid = vbot - (vbot - vtop) * 0.62   # рівень плато
    pV = [(t0, vlo), (tA, vmid), (tB, vmid), (tC, vhi)]
    poly = ' '.join('%.1f,%.1f' % p for p in pV)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                 % (poly, POS))

    # підписи фаз під/над кривою напруги
    parts.append(text((t0 + tA) / 2, vmid + 26, 'крута', 11, POS))
    parts.append(text((t0 + tA) / 2, vmid + 40, '(швидко)', 10, POS))
    parts.append(text((tA + tB) / 2, vmid - 12, 'плато', 11, MUTED))
    parts.append(text((tA + tB) / 2, vmid - 26, '(не міняється)', 10, MUTED))
    parts.append(text((tB + tC) / 2, (vmid + vhi) / 2 - 18, 'полога', 11, FIELD))
    parts.append(text((tB + tC) / 2, (vmid + vhi) / 2 - 4, '(повільно)', 10, FIELD))

    # ── панель струму (швидкість зміни заряду) ───────────────────────────────
    parts.append(arrow(ox, ibot, xr + 24, ibot, color=MUTED, sw=1.3))     # вісь t
    parts.append(arrow(ox, ibot, ox, itop - 14, color=MUTED, sw=1.3))     # вісь i
    parts.append(text(xr + 30, ibot + 4, 't', 13, MUTED, 'start', italic=True))
    parts.append(text(ox - 10, itop - 18, 'i', 13, MUTED, 'end', italic=True))
    parts.append(text(ox - 10, itop - 4, '(= C·dV/dt)', 10, MUTED, 'end'))

    # струм = нахил кривої V: висока сходинка, нуль, низька сходинка
    ihi = itop + 14
    imid = ibot - (ibot - itop) * 0.34   # рівень малого струму
    izero = ibot - 6
    # три горизонтальні рівні зі стрибками (нахил V кусково-сталий)
    pI = [(t0, ihi), (tA, ihi), (tA, izero), (tB, izero),
          (tB, imid), (tC, imid)]
    polyI = ' '.join('%.1f,%.1f' % p for p in pI)
    parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
                 % (polyI, NEG))

    parts.append(text((t0 + tA) / 2, ihi - 10, 'велике i', 11, NEG))
    parts.append(text((tA + tB) / 2, izero - 10, 'i ≈ 0', 11, MUTED))
    parts.append(text((tB + tC) / 2, imid - 10, 'мале i', 11, NEG))

    # ── вертикальні зрізи: те саме t у двох панелях ──────────────────────────
    for tx in (tA - 75, tB + 75):
        parts.append(line(tx, vtop - 6, tx, ibot, color=MUTED, sw=1.0, dash="3 4"))

    # стрілка-зв'язок «нахил угорі = висота внизу»
    parts.append(text(W / 2, 248, 'той самий час → струм унизу = НАХИЛ напруги вгорі',
                      11, INK, 'middle', bold=True))

    # ── рамка-висновок (нижче осей, на всю ширину) ───────────────────────────
    box = fitbox(ox, ibot + 28, W - ox - 24, 44,
                 'Конденсатор не «опирається» напрузі — він реагує на її швидкість зміни dV/dt.',
                 size=12, fill=FILL, stroke=MUTED, sw=1.2, color=INK)
    parts.append(box)

    render(os.path.join(IMG, 'current-is-slope.svg'), W, H, *parts,
           title='Струм конденсатора = швидкість зміни напруги')


# ── Фігура 2: водяна аналогія — заряд як вода, струм як потік ─────────────────
# Конденсатор = бак. Напруга V — рівень води (бо Q=CV: більший рівень = більше
# заряду). Струм i — потік крізь трубу (швидкість, з якою рівень міняється).
# Ємність C — площа дна бака: широкий бак (велике C) при тому самому потоці
# наповнюється повільніше. Показує, ЧОМУ i = C·dV/dt: потік = площа × швидкість
# підйому рівня. І де аналогія ламається — підпис унизу.

def fig_tank():
    W, H = 680, 380
    parts = []

    # ── бак (конденсатор) ────────────────────────────────────────────────────
    bx, by, bw, bh = 120, 80, 200, 230
    parts.append(rect(bx, by, bw, bh, fill="#eef6ff", stroke=INK, sw=2.2, rx=4))
    # рівень води
    wl = by + bh * 0.42
    parts.append(rect(bx + 3, wl, bw - 6, by + bh - wl - 3, fill="#bfe0ff",
                      stroke="none", sw=0))
    parts.append(line(bx, wl, bx + bw, wl, color=NEG, sw=2.0))

    # підпис рівня = напруга
    parts.append(arrow(bx + bw + 16, by + bh, bx + bw + 16, wl, color=POS, sw=1.6))
    parts.append(text(bx + bw + 24, (wl + by + bh) / 2, 'V', 14, POS, 'start',
                      bold=True, italic=True))
    parts.append(text(bx + bw + 24, (wl + by + bh) / 2 + 16, '(рівень', 10, POS, 'start'))
    parts.append(text(bx + bw + 24, (wl + by + bh) / 2 + 28, '= заряд Q)', 10, POS, 'start'))

    # підпис площі дна = ємність C
    parts.append(line(bx, by + bh + 14, bx + bw, by + bh + 14, color=FIELD, sw=1.6))
    parts.append(text(bx + bw / 2, by + bh + 30, 'C — площа дна (ємність)', 11, FIELD))
    parts.append(text(bx + bw / 2, by + bh + 44, 'ширший бак → той самий потік підіймає рівень повільніше',
                      10, MUTED))

    # ── труба з потоком (струм) ──────────────────────────────────────────────
    py = wl - 30
    parts.append(rect(bx - 90, py, 92, 22, fill="#dff5e6", stroke=INK, sw=1.6, rx=3))
    parts.append(arrow(bx - 86, py + 11, bx - 6, py + 11, color=NEG, sw=2.4))
    parts.append(text(bx - 44, py - 8, 'i — потік', 12, NEG, 'middle', bold=True))
    parts.append(text(bx - 44, py + 40, '(струм)', 10, NEG))

    # ── формула-зв'язок ──────────────────────────────────────────────────────
    fb, fw, fh = textbox(500, 150, ['потік = площа × швидкість', 'підйому рівня',
                                     '', 'i = C · dV/dt'],
                         size=13, color=INK, fill="#fff8e1",
                         stroke="#f0b429", sw=1.4)
    parts.append(fb)

    # стрілка від формули до бака
    parts.append(arrow(498 - fw / 2, 150, bx + bw + 70, 150, color=MUTED, sw=1.3))

    # ── де аналогія ламається ────────────────────────────────────────────────
    parts.append(text(W / 2, H - 16,
                      'Межа аналогії: вода не «всмоктується назад» при спаді рівня, а реальний конденсатор '
                      'при dV/dt<0 віддає струм назад (i<0).',
                      10, MUTED, 'middle'))

    render(os.path.join(IMG, 'water-tank.svg'), W, H, *parts,
           title='Водяна аналогія: рівень = напруга, потік = струм, дно = ємність')


# ── Фігура 3: дві грані одного зв'язку — похідна та інтеграл ──────────────────
# Зліва: дано напругу → струм є її ПОХІДНОЮ (i = C·dV/dt). Справа: дано струм →
# напруга є його ІНТЕГРАЛОМ (V = (1/C)∫i dt). Це той самий зв'язок, прочитаний
# у два боки: диференціювання й накопичення обернені. Унизу — де кожен бік
# працює (диференціатор, інтегратор, RC-затримка).

def fig_two_faces():
    W, H = 700, 360
    parts = []

    cy = 120
    lx = 175          # центр лівого блоку
    rx = 525          # центр правого блоку

    # ── лівий бік: V → i (похідна) ───────────────────────────────────────────
    b1, w1, h1 = textbox(lx, cy, ['ДАНО: напруга V(t)', '', 'струм = похідна V',
                                   'i = C · dV/dt'],
                         size=13, color=INK, fill=FILL, stroke=POS, sw=1.8)
    parts.append(b1)
    parts.append(text(lx, cy - h1 / 2 - 12, 'диференціювання', 12, POS, 'middle', bold=True))

    # ── правий бік: i → V (інтеграл) ─────────────────────────────────────────
    b2, w2, h2 = textbox(rx, cy, ['ДАНО: струм i(t)', '', 'напруга = інтеграл i',
                                   'V = (1/C) ∫ i dt'],
                         size=13, color=INK, fill=FILL, stroke=NEG, sw=1.8)
    parts.append(b2)
    parts.append(text(rx, cy - h2 / 2 - 12, 'накопичення', 12, NEG, 'middle', bold=True))

    # ── стрілки «обернені дії» між блоками ───────────────────────────────────
    gap_l = lx + w1 / 2
    gap_r = rx - w2 / 2
    parts.append(arrow(gap_l + 6, cy - 12, gap_r - 6, cy - 12, color=POS, sw=1.8))
    parts.append(text((gap_l + gap_r) / 2, cy - 20, 'd/dt', 11, POS, 'middle', italic=True))
    parts.append(arrow(gap_r - 6, cy + 14, gap_l + 6, cy + 14, color=NEG, sw=1.8))
    parts.append(text((gap_l + gap_r) / 2, cy + 30, '∫ dt', 11, NEG, 'middle', italic=True))
    parts.append(text((gap_l + gap_r) / 2, cy + 48, 'обернені', 10, MUTED, 'middle'))

    # ── де працює кожен бік ──────────────────────────────────────────────────
    yb = 250
    uses = [
        (130, 'Диференціатор', 'реагує на стрибок,', 'передній фронт', POS),
        (350, 'Інтегратор', 'накопичує струм,', 'плавний сигнал', NEG),
        (570, 'RC-затримка', 'фільтр, антидребезг,', 'витримка часу', FIELD),
    ]
    for cx, title, l1, l2, col in uses:
        bb = fitbox(cx - 95, yb, 190, 74,
                    '%s\n%s\n%s' % (title, l1, l2),
                    size=11, fill=FILL, stroke=col, sw=1.4, color=INK)
        parts.append(bb)

    parts.append(text(W / 2, yb - 14, 'Де це працює', 12, INK, 'middle', bold=True))

    render(os.path.join(IMG, 'two-faces.svg'), W, H, *parts,
           title=u'Один зв’язок у два боки: похідна (i) та інтеграл (V)')


fig_current_is_slope()
fig_tank()
fig_two_faces()
print('Done. SVG in', IMG)
