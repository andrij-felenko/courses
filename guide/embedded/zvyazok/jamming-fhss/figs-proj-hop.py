# -*- coding: utf-8 -*-
"""Фігури до вставки proj-hop-sequence (LFSR-генератор розкладу стрибків).
Запуск:  python figs-proj-hop.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Як тактує LFSR Галуа: біти зсуваються, а на відводах XOR-иться вихід ──
# Ідея, яку важко сказати словами: у формі Галуа немає довгого ланцюга XOR —
# випав молодший біт, і ЦЕЙ один біт править лише кілька позицій усередині регістра.
def fig_galois_step():
    W, H = 720, 360
    f = []
    f.append(text(W / 2, 30, "Один такт LFSR у формі Галуа", 16, INK, "middle", bold=True))

    # 8 комірок регістра (демо-ширина; у коді 16/32), біт 7 — старший, біт 0 — молодший
    n = 8
    cw, ch = 56, 46
    x0 = (W - n * cw) / 2
    yr = 90
    bits_before = [1, 0, 1, 1, 0, 0, 1, 0]      # довільний стан «до»
    # відводи Галуа для демо: після зсуву XOR-имо на позиціях 6 і 4 (умовно)
    taps = {6, 4}

    def cell(ix, val, y, hot=False, tap=False):
        cx = x0 + ix * cw
        fill = "#fdecea" if hot else ("#eef6ef" if tap else FILL)
        stroke = POS if hot else (FIELD if tap else LINE)
        out = rect(cx, y, cw - 6, ch, fill=fill, stroke=stroke, sw=2)
        out += text(cx + (cw - 6) / 2, y + ch / 2 + 6, str(val), 20, INK, "middle", bold=True)
        # номер біта
        out += text(cx + (cw - 6) / 2, y - 8, "b%d" % (n - 1 - ix), 11, MUTED, "middle")
        return out, cx

    # ── ряд «до» ──
    for i, v in enumerate(bits_before):
        frag, _ = cell(i, v, yr)
        f.append(frag)
    f.append(text(x0 - 14, yr + ch / 2 + 5, "до", 13, MUTED, "end", bold=True))

    # молодший біт випадає праворуч
    out_x = x0 + n * cw + 2
    f.append(arrow(x0 + (n - 1) * cw + (cw - 6), yr + ch / 2, out_x + 20, yr + ch / 2, color=POS, sw=2))
    f.append(text(out_x + 30, yr + ch / 2 - 8, "випав", 12, POS, "start", bold=True))
    f.append(text(out_x + 30, yr + ch / 2 + 8, "біт = 1", 12, POS, "start"))

    # ── ряд «після»: усе зсунулося праворуч, старший = 0, на відводах XOR з випалим ──
    ya = 220
    outbit = bits_before[-1]                       # 1
    shifted = [0] + bits_before[:-1]               # логічний зсув праворуч
    after = shifted[:]
    for t in taps:
        idx = (n - 1) - t                          # позиція в масиві зліва направо
        after[idx] ^= outbit
    for i, v in enumerate(after):
        is_tap = ((n - 1 - i) in taps)
        frag, cx = cell(i, v, ya, tap=is_tap)
        f.append(frag)
    f.append(text(x0 - 14, ya + ch / 2 + 5, "після", 13, MUTED, "end", bold=True))

    # стрілка зсуву між рядами
    f.append(arrow(x0 + n * cw / 2, yr + ch + 8, x0 + n * cw / 2, ya - 12, color=MUTED, sw=1.6))
    f.append(text(x0 + n * cw / 2 + 12, (yr + ch + ya) / 2 + 4, "зсув праворуч", 12, MUTED, "start"))

    # підпис-пояснення на відводах
    tb, tw, th = textbox(W / 2, 312,
                         "випалий біт = 1 → на кожному відводі (зелені) вміст XOR-иться з ним\n"
                         "жоден довгий ланцюг XOR не потрібен: правимо лише кілька комірок",
                         size=12, fill="#eef6ef", stroke=FIELD, color=INK)
    f.append(tb)

    render(os.path.join(IMG, "d-galois-step.svg"), W, H, *f)


# ── 2. Вихід LFSR → номер каналу: сире «за модулем» дає колізії й сусідів ──
# Ідея: не можна брати канал = слово % N наївно — так виходять збіги й сусідні
# частоти поспіль (легка здобич для глушилки). Показуємо проблему і лік — таблицю-тасовку.
def fig_channel_map():
    W, H = 720, 430
    f = []
    f.append(text(W / 2, 30, "Від слова LFSR до номера каналу", 16, INK, "middle", bold=True))

    # злива: колонка сирих слів
    col_x = 70
    y0 = 70
    rows = 6
    rh = 44
    words = ["0x8E31", "0x1A0C", "0x1A0D", "0xC7F2", "0x8E31", "0x55A0"]
    naive = [3, 12, 13, 2, 3, 0]        # word % 16 (демо): є повтор 3, є сусіди 12→13
    f.append(text(col_x + 60, y0 - 14, "сире слово LFSR", 12, MUTED, "middle", bold=True))
    for i, w in enumerate(words):
        y = y0 + i * rh
        f.append(rect(col_x, y, 120, rh - 8, fill=FILL, stroke=LINE, sw=1.5))
        f.append(text(col_x + 60, y + (rh - 8) / 2 + 5, w, 15, INK, "middle", bold=True))

    # середина: наївне «% 16» — з бідами
    mid_x = 300
    f.append(text(mid_x + 40, y0 - 14, "наївно: % 16", 12, POS, "middle", bold=True))
    bad_rows = {0: "повтор", 4: "повтор", 1: "сусід", 2: "сусід"}
    for i, ch in enumerate(naive):
        y = y0 + i * rh
        f.append(arrow(col_x + 122, y + (rh - 8) / 2, mid_x - 4, y + (rh - 8) / 2, color=MUTED, sw=1.4))
        bad = i in bad_rows
        fill = "#fdecea" if bad else FILL
        stroke = POS if bad else LINE
        f.append(rect(mid_x, y, 80, rh - 8, fill=fill, stroke=stroke, sw=2 if bad else 1.5))
        f.append(text(mid_x + 40, y + (rh - 8) / 2 + 5, "к%d" % ch, 15, INK, "middle", bold=True))
        if bad:
            f.append(text(mid_x + 88, y + (rh - 8) / 2 + 4, bad_rows[i], 11, POS, "start"))

    # права: таблиця-тасовка + правило «не сусід/не повтор»
    r_x = 520
    f.append(text(r_x + 70, y0 - 14, "через таблицю + фільтр", 12, FIELD, "middle", bold=True))
    good = [11, 4, 9, 15, 2, 7]     # після відображення й уникнення повторів/сусідів
    for i, ch in enumerate(good):
        y = y0 + i * rh
        f.append(arrow(mid_x + 82, y + (rh - 8) / 2, r_x - 4, y + (rh - 8) / 2, color=FIELD, sw=1.4))
        f.append(rect(r_x, y, 80, rh - 8, fill="#eef6ef", stroke=FIELD, sw=2))
        f.append(text(r_x + 40, y + (rh - 8) / 2 + 5, "к%d" % ch, 15, INK, "middle", bold=True))

    # нижній підпис
    tb, tw, th = textbox(W / 2, 392,
                         "однакові слова → однаковий канал (повтор); близькі слова → сусідні канали.\n"
                         "лік: перестановна таблиця розкидає близькі входи + відкидай повтор сусіда",
                         size=12, fill="#eef6ef", stroke=FIELD, color=INK)
    f.append(tb)

    render(os.path.join(IMG, "d-channel-map.svg"), W, H, *f)


# ── 3. Слідкувальна глушилка: гонка всередині кадру ──────────────────────────
# Ідея: глушилка мусить ВСТИГНУТИ почути стрибок, визначити частоту й ударити,
# поки кадр іще корисний. Секретний розклад лишає їй тільки хвіст кадру;
# простий лічильник вона взагалі рахує наперед і глушить кадр цілком.
def fig_follower_race():
    W, H = 720, 400
    f = []
    f.append(text(W / 2, 30, "Слідкувальна глушилка: гонка всередині кадру", 16, INK, "middle", bold=True))

    bx = 70
    bw = 580
    # шкала кадру
    f.append(text(W / 2, 58, "один кадр (стрибок сидить на одній частоті)", 12, MUTED, "middle"))

    # ── смуга A: секретний розклад ──
    yA = 90
    bh = 58
    listen = 0.28          # частка кадру на «почути й визначити»
    f.append(text(bx, yA - 8, "секретний розклад", 12, FIELD, "start", bold=True))
    # корисна частина
    f.append(rect(bx, yA, bw * listen, bh, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(fitbox(bx, yA, bw * listen, bh, "глушилка\nслухає й шукає", size=11,
                    fill="#fdecea", stroke=POS, color=INK))
    f.append(rect(bx + bw * listen, yA, bw * (1 - listen), bh, fill="#eef6ef", stroke=FIELD, sw=1.8))
    f.append(fitbox(bx + bw * listen, yA, bw * (1 - listen), bh,
                    "кадр проходить чисто (вона встигає накрити лише хвіст)",
                    size=11, fill="#eef6ef", stroke=FIELD, color=INK))
    # хвіст, який вона встигає вдарити
    tail = 0.12
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="#fdecea" stroke="%s" stroke-width="1.6" opacity="0.55"/>'
             % (bx + bw * (1 - tail), yA, bw * tail, bh, POS))

    # ── смуга B: простий лічильник ──
    yB = 200
    f.append(text(bx, yB - 8, "простий лічильник (передбачуваний)", 12, POS, "start", bold=True))
    f.append(rect(bx, yB, bw, bh, fill="#fdecea", stroke=POS, sw=2))
    f.append(fitbox(bx, yB, bw, bh,
                    "глушилці не треба слухати — вона РАХУЄ твій канал наперед і б'є кадр цілком",
                    size=11.5, fill="#fdecea", stroke=POS, color=INK))

    # ── важіль: швидші стрибки коротшають кадр ──
    yC = 300
    f.append(line(bx, yC, bx + bw, yC, color=MUTED, sw=1.2))
    f.append(arrow(bx, yC, bx + bw + 12, yC, color=MUTED, sw=1.4))
    f.append(text(bx + bw + 18, yC + 4, "темп", 11, MUTED, "start"))
    tb, tw, th = textbox(W / 2, 350,
                         "важіль: швидші стрибки → коротший кадр → менше часу глушилці зреагувати;\n"
                         "ширша смуга → більше каналів-кандидатів, важче наздогнати",
                         size=12, fill=FILL, stroke=LINE, color=INK)
    f.append(tb)

    render(os.path.join(IMG, "d-follower-race.svg"), W, H, *f)


if __name__ == "__main__":
    fig_galois_step()
    fig_channel_map()
    fig_follower_race()
    print("OK: d-galois-step.svg, d-channel-map.svg, d-follower-race.svg")
