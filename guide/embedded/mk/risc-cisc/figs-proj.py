# -*- coding: utf-8 -*-
# Фігури для вставки proj-disasm-walkthrough.md.
# Окремий файл, щоб не чіпати figs.py / figs-d.py цієї теми.
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Ті самі відтінки, що в темі: AVR-бік теплий, ARM-бік холодний, спільне — сіре.
AVRC  = "#b5641f"   # AVR (8-бітний) — теплий
ARMC  = "#1f47b5"   # ARM Thumb-2 — холодний
GREEN = "#1f8a3b"
F_AVR = "#fbf3ec"
F_ARM = "#f3f5fd"
F_GRN = "#eef7ee"
F_GREY = "#f4f5f7"


# ── loadstore: той самий цикл, дві мови, візерунок LD → op → ST ────────────────
# Ідея: одна C-функція sum += a[i] у двох дизасемблерах поруч; кольором
# виділено спільний кістяк load/store, щоб читач побачив ОДИН візерунок.

def fig_loadstore():
    W, H = 860, 470
    p = []
    p.append(text(W / 2, 40, "Один цикл  sum += a[i]  —  той самий візерунок у двох залізах",
                  size=15, bold=True))

    # спільна легенда-кістяк
    p.append(rect(W / 2 - 250, 56, 500, 30, fill=F_GREY, stroke=INK, sw=1.4, rx=8))
    p.append(text(W / 2 - 150, 76, "завантаж (LD/LDR)", size=11, bold=True, color=GREEN))
    p.append(text(W / 2 + 6, 76, "→ порахуй у регістрах →", size=11, color=MUTED))
    p.append(text(W / 2 + 168, 76, "збережи (ST/STR)", size=11, bold=True, color=GREEN))

    # ── AVR колонка ──
    lx, lw = 40, 380
    p.append(rect(lx, 104, lw, 330, fill=F_AVR, stroke=AVRC, sw=2, rx=10))
    p.append(text(lx + lw / 2, 128, "AVR (8-біт) — тіло циклу", size=12.5, bold=True, color=AVRC))
    avr = [
        ("ld   r24, Z+",   "; a[i] молодший байт → r24", True),
        ("ld   r25, Z+",   "; a[i] старший байт → r25", True),
        ("add  r18, r24",  "; sum += a[i], молодший", False),
        ("adc  r19, r25",  "; +перенос, старший байт", False),
        ("sbiw r26, ...",  "; лічильник -= 1", False),
        ("brne .-...",     "; ще не 0 → назад у цикл", False),
    ]
    for i, (op, cm, ls) in enumerate(avr):
        ry = 146 + i * 40
        stroke = GREEN if ls else AVRC
        fill = F_GRN if ls else BG
        p.append(rect(lx + 18, ry, lw - 36, 32, fill=fill, stroke=stroke, sw=1.6 if ls else 1.3, rx=6))
        p.append(text(lx + 32, ry + 21, op, size=11.5, bold=True, anchor="start"))
        p.append(text(lx + 150, ry + 21, cm, size=9.5, color=MUTED, anchor="start"))
    p.append(text(lx + lw / 2, 424, "16-біт = ПАРА регістрів; додавання у два кроки (add+adc)",
                  size=10, color=AVRC, italic=True))

    # ── ARM колонка ──
    rx, rw = 440, 380
    p.append(rect(rx, 104, rw, 330, fill=F_ARM, stroke=ARMC, sw=2, rx=10))
    p.append(text(rx + rw / 2, 128, "ARM Thumb-2 — тіло циклу", size=12.5, bold=True, color=ARMC))
    arm = [
        ("ldrh r3, [r1], #2", "; a[i] у r3 (16-біт одразу)", True),
        ("add  r2, r2, r3",   "; sum += a[i], один крок", False),
        ("cmp  r1, r4",       "; дійшли кінця масиву?", False),
        ("bne  .-...",        "; ні → назад у цикл", False),
    ]
    for i, (op, cm, ls) in enumerate(arm):
        ry = 146 + i * 40
        stroke = GREEN if ls else ARMC
        fill = F_GRN if ls else BG
        p.append(rect(rx + 18, ry, rw - 36, 32, fill=fill, stroke=stroke, sw=1.6 if ls else 1.3, rx=6))
        p.append(text(rx + 32, ry + 21, op, size=11.5, bold=True, anchor="start"))
        p.append(text(rx + 178, ry + 21, cm, size=9.5, color=MUTED, anchor="start"))
    p.append(text(rx + rw / 2, 344, "16-біт влазить у ОДИН 32-бітний регістр:", size=10, color=ARMC, italic=True))
    p.append(text(rx + rw / 2, 360, "одне ldrh, одне add — коротший цикл", size=10, color=ARMC, italic=True))

    p.append(text(W / 2, 458,
                  "Кістяк один (зелене): пам'ять чіпають лише LD/ST. Різна лише ширина регістра — звідси й різна к-сть команд.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "loadstore-both.svg"), W, H, *p)


# ── spill: чому регістрів не вистачає і що робить компілятор ───────────────────
# Ідея: скінченний банк регістрів; коли живих змінних більше — зайві «виливаються»
# у стек парою ST/LD. Показати саме МЕХАНІЗМ spilling.

def fig_spill():
    W, H = 820, 400
    p = []
    p.append(text(W / 2, 40, "Виливання регістрів: коли живих змінних більше, ніж регістрів",
                  size=14.5, bold=True))

    # банк регістрів
    bx, by = 60, 90
    p.append(text(bx, by - 12, "банк регістрів (скінченний)", size=11, bold=True, anchor="start", color=INK))
    regs = ["a", "b", "c", "d", "e", "f"]
    full = 5  # перші 5 зайняті живими змінними
    for i, r in enumerate(regs):
        cx = bx + i * 62
        occupied = i < full
        fill = F_GRN if occupied else BG
        stroke = GREEN if occupied else MUTED
        p.append(rect(cx, by, 52, 46, fill=fill, stroke=stroke, sw=1.8, rx=6))
        p.append(text(cx + 26, by + 22, "r%d" % (i + 2), size=11, bold=True))
        lab = r if occupied else "—"
        p.append(text(cx + 26, by + 38, lab, size=9.5, color=MUTED))
    p.append(text(bx + 3 * 62, by + 70, "усі зайняті живими значеннями", size=10, color=GREEN))

    # шоста змінна не має місця
    gx = bx + 6 * 62 + 6
    p.append(rect(gx, by, 70, 46, fill="#fdecea", stroke=POS, sw=2, rx=6))
    p.append(text(gx + 35, by + 21, "g?", size=12, bold=True, color=POS))
    p.append(text(gx + 35, by + 38, "нема місця", size=8.5, color=POS))
    p.append(arrow(gx + 35, by + 50, gx + 35, by + 96, color=POS, sw=2))

    # стек — куди виливаємо
    sx, sy = gx - 30, by + 100
    p.append(rect(sx, sy, 130, 62, fill=F_GREY, stroke=INK, sw=1.8, rx=8))
    p.append(text(sx + 65, sy - 8, "стек у RAM", size=10.5, bold=True))
    p.append(text(sx + 65, sy + 24, "spill: ST r, [SP]", size=10.5, bold=True, color=POS))
    p.append(text(sx + 65, sy + 44, "потім: LD r, [SP]", size=10.5, color=POS))

    # висновок-ланцюг
    concl, cw, ch = textbox(W / 2, 300,
                            "Кожне виливання = зайва пара ST+LD у пам'ять.\n"
                            "Через це довга функція з десятками змінних\n"
                            "часто повільніша за кілька коротких.",
                            size=11.5, bold=True, fill=F_GREY, stroke=INK, sw=1.8, pad=14)
    p.append(concl)
    p.append(text(W / 2, 300 + ch / 2 + 24,
                  "Практика: тримай робочий набір гарячого циклу малим — і виливань не буде.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "register-spill.svg"), W, H, *p)


if __name__ == "__main__":
    fig_loadstore()
    fig_spill()
    print("OK: proj figures written to", OUT)
