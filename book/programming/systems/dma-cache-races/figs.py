# -*- coding: utf-8 -*-
"""Фігури до теми «Пастки DMA» (cache coherency, alignment, races)
та її ⚙️-вставки proj-cache-dma.
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Імена файлів — slug-only, без номерів. Заголовки/підписи — без «Рис.» і номерів
(підпис дає сам Markdown).
Стаття: cache-coherency, buffer-alignment, dma-checklist.
Вставка ⚙️: coherency-detail, alignment-detail.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

MONO    = "Consolas, 'DejaVu Sans Mono', monospace"
STALE   = "#fdecea"   # стале / небезпека (червоний фон)
FRESH   = "#eaf6ee"   # свіже / коректне (зелений фон)
WARN    = "#fdf6e3"   # увага / нейтральне (теплий фон)
WARN_S  = "#b8860b"


def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)


def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


# ════════════════ СТАТТЯ ═════════════════════════════════════════════════════

# ── 1. Дві симетричні пастки когерентності (RX invalidate / TX write-back) ───
def fig_cache_coherency():
    W, H = 760, 470
    f = [text(W / 2, 30, "Дві симетричні пастки: ядро й DMA бачать ту саму RAM",
              size=16, bold=True)]

    # колонки: ЯДРО | КЕШ | RAM | DMA
    cx = {"core": 110, "cache": 300, "ram": 500, "dma": 680}
    colw = 130

    def column_label(x, s, color=INK):
        return text(x, 60, s, size=13, bold=True, color=color)

    f.append(column_label(cx["core"], "Ядро"))
    f.append(column_label(cx["cache"], "Кеш"))
    f.append(column_label(cx["ram"], "RAM"))
    f.append(column_label(cx["dma"], "DMA"))

    # ── Верх: RX — DMA поклав свіже в RAM, кеш тримає старе ──
    yr = 78
    f.append(text(40, yr + 2, "Приймання (RX): DMA → RAM, потім читає ядро",
                  size=12, color=MUTED, anchor="start", bold=True))
    yb = yr + 18
    # ядро читає (стрілка від кешу до ядра)
    f.append(rect(cx["core"] - colw/2, yb, colw, 48, fill=STALE, stroke=POS))
    f.append(fitbox(cx["core"] - colw/2, yb, colw, 48, "читає\nстале", size=12,
                    fill=STALE, stroke=POS, color=POS, bold=True))
    f.append(rect(cx["cache"] - colw/2, yb, colw, 48, fill=STALE, stroke=POS))
    f.append(fitbox(cx["cache"] - colw/2, yb, colw, 48, "стара копія", size=12,
                    fill=STALE, stroke=POS, color=POS))
    f.append(rect(cx["ram"] - colw/2, yb, colw, 48, fill=FRESH, stroke=FIELD))
    f.append(fitbox(cx["ram"] - colw/2, yb, colw, 48, "свіжі дані", size=12,
                    fill=FRESH, stroke=FIELD, color=FIELD))
    f.append(rect(cx["dma"] - colw/2, yb, colw, 48, fill=FRESH, stroke=FIELD))
    f.append(fitbox(cx["dma"] - colw/2, yb, colw, 48, "щойно\nзаписав", size=12,
                    fill=FRESH, stroke=FIELD, color=FIELD))
    # потік DMA → RAM
    f.append(arrow(cx["dma"] - colw/2, yb + 24, cx["ram"] + colw/2, yb + 24, color=FIELD))
    # читання кеш → ядро
    f.append(arrow(cx["cache"] - colw/2, yb + 24, cx["core"] + colw/2, yb + 24, color=POS))
    # ліки
    f.append(text(40, yb + 76, "Ліки: invalidate — оголосити рядки кешу недійсними перед читанням",
                  size=11.5, color=NEG, anchor="start"))

    # роздільник
    f.append(line(40, 248, W - 40, 248, color=MUTED, sw=1, dash="4,4"))

    # ── Низ: TX — ядро написало в кеш, RAM стара, DMA везе старе ──
    yt = 268
    f.append(text(40, yt + 2, "Передавання (TX): ядро → RAM, потім читає DMA",
                  size=12, color=MUTED, anchor="start", bold=True))
    yb2 = yt + 18
    f.append(rect(cx["core"] - colw/2, yb2, colw, 48, fill=FRESH, stroke=FIELD))
    f.append(fitbox(cx["core"] - colw/2, yb2, colw, 48, "написало\nнове", size=12,
                    fill=FRESH, stroke=FIELD, color=FIELD))
    f.append(rect(cx["cache"] - colw/2, yb2, colw, 48, fill=FRESH, stroke=FIELD))
    f.append(fitbox(cx["cache"] - colw/2, yb2, colw, 48, "нове\n(не скинуте)", size=12,
                    fill=FRESH, stroke=FIELD, color=FIELD))
    f.append(rect(cx["ram"] - colw/2, yb2, colw, 48, fill=STALE, stroke=POS))
    f.append(fitbox(cx["ram"] - colw/2, yb2, colw, 48, "стара RAM", size=12,
                    fill=STALE, stroke=POS, color=POS))
    f.append(rect(cx["dma"] - colw/2, yb2, colw, 48, fill=STALE, stroke=POS))
    f.append(fitbox(cx["dma"] - colw/2, yb2, colw, 48, "везе\nстале", size=12,
                    fill=STALE, stroke=POS, color=POS, bold=True))
    # ядро → кеш
    f.append(arrow(cx["core"] + colw/2, yb2 + 24, cx["cache"] - colw/2, yb2 + 24, color=FIELD))
    # RAM → DMA
    f.append(arrow(cx["ram"] + colw/2, yb2 + 24, cx["dma"] - colw/2, yb2 + 24, color=POS))
    f.append(text(40, yb2 + 76, "Ліки: write-back (clean) — примусово скинути кеш у RAM перед стартом DMA",
                  size=11.5, color=NEG, anchor="start"))

    out("cache-coherency.svg", W, H, *f)


# ── 2. Вирівнювання й доповнення буфера на межу кешлінії ─────────────────────
def fig_buffer_alignment():
    W, H = 760, 430
    f = [text(W / 2, 30, "Вирівняний буфер не ділить кешлінії з чужими даними",
              size=16, bold=True)]

    cell = 40
    n = 12                      # 12 байтових клітинок = трохи більше за 1 лінію
    x0 = 90
    line_b = 4                  # 4 клітинки на «лінію» в малюнку (умовно)

    def grid(y, owners, title, good):
        # owners: список ('buf'|'other'|'pad') по клітинках
        parts = [text(x0, y - 10, title, size=12.5, bold=True,
                      color=(FIELD if good else POS), anchor="start")]
        for i, ow in enumerate(owners):
            xx = x0 + i * cell
            if ow == 'buf':
                fill, st = FRESH, FIELD
            elif ow == 'pad':
                fill, st = WARN, WARN_S
            else:
                fill, st = STALE, POS
            parts.append(rect(xx, y, cell, cell, fill=fill, stroke=st, sw=1.2, rx=0))
        # межі ліній (товсті вертикалі кожні line_b клітинок)
        for k in range(0, n + 1, line_b):
            xx = x0 + k * cell
            parts.append(line(xx, y - 4, xx, y + cell + 4, color=INK, sw=2.4))
        return parts

    # Погано: буфер зміщений на 2 клітинки, ділить крайні лінії з чужими даними
    y1 = 92
    bad = (['other', 'other'] + ['buf'] * 7 + ['other', 'other', 'other'])
    f += grid(y1, bad, "Невирівняний: початок усередині лінії", good=False)
    # дужка під буфером
    f.append(text(x0 + 2*cell + 3.5*cell, y1 + cell + 26,
                  "крайні лінії спільні з чужими даними → invalidate знищить сусіда",
                  size=11, color=POS))

    # Добре: буфер на межі лінії + доповнення до кратного
    y2 = 240
    good = (['buf'] * 7 + ['pad'] + ['other'] * 4)
    f += grid(y2, good, "Вирівняний на межу + доповнений (pad) до кратного лінії", good=True)
    f.append(text(x0 + 4*cell, y2 + cell + 26,
                  "буфер займає лише цілі «свої» лінії — операції кешу не чіпають зайвого",
                  size=11, color=FIELD))

    # легенда
    ly = 372
    items = [(FRESH, FIELD, "буфер DMA"), (WARN, WARN_S, "доповнення (pad)"),
             (STALE, POS, "чужі дані")]
    lx = x0
    for fill, st, lab in items:
        f.append(rect(lx, ly - 12, 16, 14, fill=fill, stroke=st, sw=1.2, rx=2))
        f.append(text(lx + 22, ly, lab, size=11, anchor="start"))
        lx += text_width(lab, 11) + 70
    f.append(text(x0, ly + 24, "Товста вертикаль — межа кешлінії (тут 4 клітинки = одна лінія).",
                  size=10.5, color=MUTED, anchor="start"))

    out("buffer-alignment.svg", W, H, *f)


# ── 3. Чек-лист буфера: чотири ворота, кожне «ні» → свій клас помилки ────────
def fig_dma_checklist():
    W, H = 860, 560
    f = [text(W / 2, 30, "Чотири ворота перед кожним DMA-буфером",
              size=16, bold=True)]

    gates = [
        ("Вирівняний на\nмежу кешлінії?", "невирівняно → invalidate\nпсує сусідні дані"),
        ("У DMA-придатній\nпам'яті (SRAM/static)?", "ні → DMA відмовляє,\nHardFault, глюк PSRAM"),
        ("Invalidate / write-back\nна місці й у потрібний бік?", "ні → стале читання\nабо DMA везе старе"),
        ("Власник зараз один —\nядро АБО DMA?", "обидва → гонка,\nпошкоджений буфер"),
    ]

    cx_gate = 560
    gate_w, gate_h = 230, 64
    fail_w, fail_h = 230, 56
    y = 70
    step = 110

    for i, (q, fail) in enumerate(gates):
        yc = y + i * step + gate_h / 2
        # ворота (ромб через polygon, текст через fitbox усередині)
        gx, gy = cx_gate - gate_w/2, y + i * step
        # рамка-ворота
        f.append(rect(gx, gy, gate_w, gate_h, fill=WARN, stroke=WARN_S, sw=1.8))
        f.append(fitbox(gx, gy, gate_w, gate_h, q, size=12, fill=WARN,
                        stroke=WARN_S, color=INK, bold=True))
        # «ні» → ліворуч до коробки помилки
        f.append(arrow(gx, yc, gx - 40, yc, color=POS))
        fx = gx - 40 - fail_w
        f.append(rect(fx, yc - fail_h/2, fail_w, fail_h, fill=STALE, stroke=POS, sw=1.4))
        f.append(fitbox(fx, yc - fail_h/2, fail_w, fail_h, fail, size=11,
                        fill=STALE, stroke=POS, color=POS))
        f.append(text(gx - 20, yc - 6, "ні", size=11, color=POS))
        # «так» → вниз до наступних воріт
        if i < len(gates) - 1:
            f.append(arrow(cx_gate, gy + gate_h, cx_gate, gy + step, color=FIELD))
            f.append(text(cx_gate + 16, gy + gate_h + 22, "так", size=11, color=FIELD))

    # фінал
    yc_last = y + (len(gates) - 1) * step + gate_h
    f.append(arrow(cx_gate, yc_last, cx_gate, yc_last + 28, color=FIELD))
    f.append(text(cx_gate + 16, yc_last + 20, "так", size=11, color=FIELD))
    fb, w, h = textbox(cx_gate, yc_last + 28 + 26,
                       "Буфер безпечний — можна запускати передачу", size=13,
                       fill=FRESH, stroke=FIELD, sw=2.4, bold=True, pad=14)
    f.append(fb)

    out("dma-checklist.svg", W, H, *f)


# ════════════════ ВСТАВКА ⚙️ proj-cache-dma ═════════════════════════════════

# ── 1. Деталь когерентності: write-back-кеш, відкладений запис, кешлінія ─────
def fig_coherency_detail():
    W, H = 780, 440
    f = [text(W / 2, 30, "Чому write-back-кеш розходиться з RAM у часі",
              size=16, bold=True)]

    # горизонтальна вісь часу
    ox, oy = 70, 360
    aw = 640
    f.append(arrow(ox, oy, ox + aw, oy, sw=1.8))
    f.append(text(ox + aw, oy + 22, "час", size=12, anchor="end"))

    # три моменти
    moments = [
        (0.10, "ядро пише\nв буфер", FRESH, FIELD, "кеш: НОВЕ\nRAM: старе"),
        (0.45, "write-back\nще не стався", WARN, WARN_S, "кеш: НОВЕ\nRAM: СТАРЕ"),
        (0.80, "після clean\n→ старт DMA", FRESH, FIELD, "кеш: НОВЕ\nRAM: НОВЕ"),
    ]
    for frac, lab, fill, st, state in moments:
        xx = ox + frac * aw
        f.append(line(xx, oy - 6, xx, oy + 6, sw=1.4))
        # подія зверху
        f.append(rect(xx - 70, 70, 140, 46, fill=fill, stroke=st, sw=1.4))
        f.append(fitbox(xx - 70, 70, 140, 46, lab, size=12, fill=fill, stroke=st,
                        color=st, bold=True))
        f.append(arrow(xx, 116, xx, oy - 8, color=MUTED, sw=1.2))
        # стан кеш/RAM знизу події
        bad = "СТАРЕ" in state
        sf, ss = (STALE, POS) if bad else (FRESH, FIELD)
        f.append(rect(xx - 70, 150, 140, 52, fill=sf, stroke=ss, sw=1.4))
        f.append(fitbox(xx - 70, 150, 140, 52, state, size=11.5, fill=sf, stroke=ss,
                        color=ss, bold=True))

    # пояснення в середині
    f.append(text(W / 2, 250,
                  "Запис ядра осідає в кеші й до RAM доходить «колись» (write-back).",
                  size=12, color=INK))
    f.append(text(W / 2, 272,
                  "Поки clean не виконано, DMA на шині бачить у RAM лише стару копію.",
                  size=12, color=INK))
    f.append(text(W / 2, 300,
                  "Кеш зберігає копії блоками-кешлініями (на ESP32-S3 — 32 байти).",
                  size=11.5, color=MUTED))

    out("coherency-detail.svg", W, H, *f)


# ── 2. Деталь вирівнювання: half-line, false line sharing з RAM ─────────────
def fig_alignment_detail():
    W, H = 780, 430
    f = [text(W / 2, 30, "Невирівняний буфер: invalidate крайньої лінії губить запис сусіда",
              size=15.5, bold=True)]

    cell = 44
    x0 = 70
    n = 14
    line_b = 4

    # один ряд: показуємо одну спільну крайню лінію детально
    y = 110
    f.append(text(x0, y - 14, "Крок 1. Невирівняний буфер ділить крайню лінію із сусідом",
                  size=12.5, bold=True, anchor="start", color=POS))
    owners = ['nb', 'nb'] + ['buf'] * 9 + ['nb', 'nb', 'nb']
    labels = {2: "↦ buf[0]", 0: "сусід"}
    for i, ow in enumerate(owners):
        xx = x0 + i * cell
        if ow == 'buf':
            fill, st = FRESH, FIELD
        else:
            fill, st = STALE, POS
        f.append(rect(xx, y, cell, cell, fill=fill, stroke=st, sw=1.2, rx=0))
    for k in range(0, n + 1, line_b):
        xx = x0 + k * cell
        f.append(line(xx, y - 4, xx, y + cell + 4, color=INK, sw=2.4))
    # позначити першу лінію як спільну
    f.append(text(x0 + 2*cell, y + cell + 22,
                  "перша лінія: 2 байти сусіда + початок буфера", size=11, color=POS,
                  anchor="middle"))

    # крок 2: invalidate цієї лінії
    y2 = 250
    f.append(text(x0, y2 - 14,
                  "Крок 2. invalidate цієї лінії викидає і свіжий запис сусіда в ній",
                  size=12.5, bold=True, anchor="start", color=POS))
    for i in range(line_b):
        xx = x0 + i * cell
        fill, st = STALE, POS
        f.append(rect(xx, y2, cell, cell, fill=fill, stroke=st, sw=1.2, rx=0))
        f.append(text(xx + cell/2, y2 + cell/2 + 5, "✗", size=18, color=POS, bold=True))
    f.append(line(x0, y2 - 4, x0, y2 + cell + 4, color=INK, sw=2.4))
    f.append(line(x0 + line_b*cell, y2 - 4, x0 + line_b*cell, y2 + cell + 4, color=INK, sw=2.4))
    f.append(text(x0 + line_b*cell + 16, y2 + cell/2 + 5,
                  "наступне читання сусіда → стара RAM-копія: тихе пошкодження",
                  size=11.5, color=POS, anchor="start"))

    # рішення
    y3 = 350
    fb, w, h = textbox(W/2, y3,
                       ["Рішення: початок буфера — на межі 32 Б, довжина — кратна 32 Б",
                        "(вирівняти + доповнити): буфер займає лише цілі власні лінії"],
                       size=12, fill=FRESH, stroke=FIELD, sw=2, bold=True, pad=12)
    f.append(fb)

    out("alignment-detail.svg", W, H, *f)


if __name__ == "__main__":
    fig_cache_coherency()
    fig_buffer_alignment()
    fig_dma_checklist()
    fig_coherency_detail()
    fig_alignment_detail()
    print("OK: 5 figures ->", IMG)
