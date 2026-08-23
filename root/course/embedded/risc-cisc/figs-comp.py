# -*- coding: utf-8 -*-
# Фігури ДЛЯ ВСТАВКИ comp-decode-frontend.md (клас «фронтенд декодування»).
# Вивід — у ту саму теку ./img/, окремі імена (…-fe.svg), інших фігур не чіпає.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE   = "#1f47b5"   # CISC-бік
GREEN  = "#1f8a3b"   # RISC-бік
F_BLUE = "#f3f5fd"
F_GRN  = "#eef7ee"
F_GREY = "#f4f5f7"
F_HOT  = "#fdeaea"
HOT    = "#c0392b"


# ── 1. Блок-схема класу: спільний конвеєр фронтенду ────────────────────────────
# Клас «фронтенд декодування» як послідовність вузлів: буфер вибірки → визначення
# довжини → декодери → черга/кеш µops → у виконавче ядро. Однаковий каркас для
# обох філософій; наповнення вузлів різне (нижні дві фігури).

def fig_blockdiagram():
    W, H = 820, 400
    p = [text(W / 2, 40, "Клас «фронтенд декодування»: спільний ланцюг вузлів",
              size=15, bold=True)]

    # горизонтальний конвеєр із п'яти вузлів
    y = 150
    bh = 72
    nodes = [
        ("Буфер\nвибірки", "сирі байти\nз кеша команд", F_GREY, INK),
        ("Визначення\nдовжини", "де межі\nкоманд", F_GREY, INK),
        ("Декодери", "команда →\nµops", F_GREY, INK),
        ("Черга / кеш\nµops", "згладити потік,\nне декодувати двічі", F_GREY, INK),
    ]
    x0 = 40
    gap = 26
    bw = (W - 2 * x0 - (len(nodes) - 1) * gap - 150) / len(nodes)
    xs = []
    bx = x0
    for name, sub, fill, col in nodes:
        xs.append(bx)
        p.append(rect(bx, y, bw, bh, fill=fill, stroke=INK, sw=1.8, rx=7))
        p.append(mtext(bx + bw / 2, y + 24, name, size=11.5, bold=True, color=col))
        p.append(mtext(bx + bw / 2, y + bh + 16, sub, size=8.5, color=MUTED))
        bx += bw + gap
    # вхід зліва
    p.append(text(x0 + bw / 2, y - 40, "потік команд\nу пам'яті", size=9.5, color=MUTED))
    p.append(arrow(x0 + bw / 2, y - 22, x0 + bw / 2, y - 2, color=INK, sw=1.6))
    # стрілки між вузлами
    for i in range(len(nodes) - 1):
        a = xs[i] + bw
        p.append(arrow(a, y + bh / 2, a + gap, y + bh / 2, color=INK, sw=1.8))
    # вихід у бекенд
    lastx = xs[-1] + bw
    p.append(arrow(lastx, y + bh / 2, lastx + gap, y + bh / 2, color=GREEN, sw=2))
    b, wv, hv = textbox(lastx + gap + 78, y + bh / 2, "виконавче\nядро (бекенд)",
                        size=10.5, bold=True, color=GREEN, fill=F_GRN, stroke=GREEN, sw=1.8, pad=10)
    p.append(b)

    # підпис-суть під конвеєром
    p.append(text(W / 2, y + bh + 66,
                  "Фронтенд перетворює сирі байти на готові до виконання внутрішні кроки (µops) — і подає їх бекенду.",
                  size=11, bold=True))
    p.append(text(W / 2, y + bh + 92,
                  "Каркас той самий для будь-якого процесора; уся різниця RISC ↔ CISC — у тому, ЩО коштує кожен вузол.",
                  size=10.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "frontend-block.svg"), W, H, *p)


# ── 2. Контраст: чим наповнені ті самі вузли в RISC і в CISC ───────────────────
# Дві колонки під той самий каркас. RISC: паралельний зріз полів, тверда логіка,
# крихітний фронтенд (~ ядро Cortex-M0 12k вентилів цілком). CISC: спекулятивний
# пошук меж, розбір ModR/M/SIB, мікрокод-ROM на складне, кеш µops.

def fig_contrast():
    W, H = 840, 470
    p = [text(W / 2, 38, "Ті самі вузли, різна ціна: RISC-фронтенд проти CISC-фронтенду",
              size=14.5, bold=True)]

    colw = 372
    xL = 30
    xR = W - 30 - colw
    top = 66
    rowh = 60
    labels = ["Буфер вибірки", "Визначення довжини", "Декодери", "Мікрокод / кеш µops"]

    # заголовки колонок
    p.append(rect(xL, top, colw, 30, fill=F_GRN, stroke=GREEN, sw=1.8, rx=6))
    p.append(text(xL + colw / 2, top + 20, "RISC-фронтенд (сталої довжини)", size=12, bold=True, color=GREEN))
    p.append(rect(xR, top, colw, 30, fill=F_BLUE, stroke=BLUE, sw=1.8, rx=6))
    p.append(text(xR + colw / 2, top + 20, "CISC-фронтенд (змінної довжини)", size=12, bold=True, color=BLUE))

    risc = [
        "проста черга; наступна команда\nзавжди на сталому кроці (4 чи 2 б)",
        "БЕЗКОШТОВНО: усі команди рівні,\nмежа відома наперед",
        "тверда логіка; поля на сталих бітах,\nрегістри читаються паралельно",
        "здебільшого немає — кожна команда\nіде прямо в бекенд",
    ]
    cisc = [
        "черга ≥ 15 б; треба вікно, бо межа\nкоманди наперед невідома",
        "СПЕКУЛЯТИВНО: пробує довжину в\nбагатьох місцях, START/END-біти",
        "розбір префіксів, ModR/M, SIB;\nкілька декодерів (1 складний + прості)",
        "мікрокод-ROM на складні команди +\nкеш µops, щоб обійти весь фронтенд",
    ]
    y = top + 40
    for i in range(4):
        p.append(text(xL - 4, y - 6, labels[i], size=9.5, color=MUTED, anchor="start"))
        p.append(fitbox(xL, y, colw, rowh, risc[i], size=10, pad=8,
                        fill=F_GRN, stroke=GREEN, sw=1.4))
        p.append(fitbox(xR, y, colw, rowh, cisc[i], size=10, pad=8,
                        fill=F_BLUE, stroke=BLUE, sw=1.4))
        y += rowh + 8

    # нижній підсумок — гейти
    ys = y + 4
    p.append(rect(xL, ys, colw, 44, fill=F_GRN, stroke=GREEN, sw=1.8, rx=6))
    p.append(mtext(xL + colw / 2, ys + 18,
                   "увесь фронтенд — жменька вентилів\n(ціле ядро Cortex-M0 ≈ 12 000 вентилів)",
                   size=10, bold=True, color=GREEN))
    p.append(rect(xR, ys, colw, 44, fill=F_BLUE, stroke=BLUE, sw=1.8, rx=6))
    p.append(mtext(xR + colw / 2, ys + 18,
                   "лише фронтенд — сотні тисяч вентилів;\nпровідний споживач енергії та площі",
                   size=10, bold=True, color=BLUE))

    p.append(text(W / 2, H - 14,
                  "RISC несе цей вузол майже задарма; у CISC той самий вузол — найдорожча частина процесора.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "frontend-contrast.svg"), W, H, *p)


# ── 3. «Перший байт»: що фронтенд робить із першим байтом потоку ───────────────
# Оживити відмінність на одному вхідному байті. RISC: одразу знає розкладку —
# читає поля паралельно. CISC: перший байт може бути префіксом; довжину дізнаєшся
# лише пройшовши префікси + опкод + ModR/M(+SIB) — послідовно.

def fig_firstbyte():
    W, H = 820, 400
    p = [text(W / 2, 38, "«Перший байт» потоку: що фронтенд може зробити відразу",
              size=14.5, bold=True)]

    # ── RISC ──
    yR = 92
    p.append(text(40, yR, "RISC: перший байт — частина сталого 32-бітного слова",
                  size=11.5, bold=True, color=GREEN, anchor="start"))
    # 4 байти слова
    bx, bw = 40, 60
    for i in range(4):
        fill = F_GRN if i == 0 else BG
        p.append(rect(bx + i * (bw + 6), yR + 14, bw, 34, fill=fill, stroke=GREEN, sw=1.6, rx=4))
        p.append(text(bx + i * (bw + 6) + bw / 2, yR + 14 + 22, "байт %d" % i, size=9.5,
                      color=(GREEN if i == 0 else MUTED), bold=(i == 0)))
    p.append(arrow(bx + 4 * (bw + 6) + 4, yR + 31, bx + 4 * (bw + 6) + 34, yR + 31, color=GREEN, sw=1.8))
    p.append(text(bx + 4 * (bw + 6) + 44, yR + 26,
                  "довжина відома одразу (4 б); поля на сталих бітах →",
                  size=10, color=GREEN, anchor="start"))
    p.append(text(bx + 4 * (bw + 6) + 44, yR + 44,
                  "опкод і номери регістрів вихоплюються ПАРАЛЕЛЬНО, за один крок.",
                  size=10, color=INK, anchor="start"))

    # роздільник
    p.append(line(30, 178, W - 30, 178, color=MUTED, sw=1, dash="5 4"))

    # ── CISC ──
    yC = 214
    p.append(text(40, yC, "CISC: перший байт може бути будь-чим — розбір суворо послідовний",
                  size=11.5, bold=True, color=BLUE, anchor="start"))
    steps = [("префікс?", "0..n байтів"), ("опкод", "1..3 б"),
             ("ModR/M", "де операнди"), ("SIB", "склад. адреса"),
             ("зсув / imm", "0..8 б")]
    bx2 = 40
    sw_ = 132
    for i, (nm, sub) in enumerate(steps):
        p.append(rect(bx2, yC + 16, sw_, 40, fill=F_BLUE, stroke=BLUE, sw=1.6, rx=5))
        p.append(text(bx2 + sw_ / 2, yC + 16 + 17, nm, size=10.5, bold=True, color=INK))
        p.append(text(bx2 + sw_ / 2, yC + 16 + 32, sub, size=8.5, color=MUTED))
        if i < len(steps) - 1:
            p.append(arrow(bx2 + sw_, yC + 16 + 20, bx2 + sw_ + 8, yC + 16 + 20, color=BLUE, sw=1.6))
        bx2 += sw_ + 8
    p.append(text(40, yC + 16 + 62,
                  "довжину команди (а отже й де починається наступна) знаєш ЛИШЕ пройшовши весь ланцюг —",
                  size=10, color=BLUE, anchor="start"))
    p.append(text(40, yC + 16 + 80,
                  "тому декодувати кілька команд за такт можна тільки спекулятивно, грубою силою.",
                  size=10, color=INK, anchor="start"))

    p.append(text(W / 2, H - 14,
                  "Той самий «перший байт»: у RISC він одразу все каже, у CISC — майже нічого без решти ланцюга.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "frontend-firstbyte.svg"), W, H, *p)


if __name__ == "__main__":
    fig_blockdiagram()
    fig_contrast()
    fig_firstbyte()
    print("OK: frontend comp figures written to", OUT)
