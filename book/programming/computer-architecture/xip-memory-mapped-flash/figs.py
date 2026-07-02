# -*- coding: utf-8 -*-
# Фігури теми «XIP: виконання коду з флеші на місці».
# svgkit імпортуємо (не копіюємо) — §5 AUTHORING.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

RED_F, RED = "#fdf4f4", POS      # ядро (CPU)
BLU_F, BLU = "#eef3ff", NEG      # Flash (код)
GRN_F, GRN = "#eef6ef", FIELD    # SRAM (дані)
CTL_F, CTL = "#fff7e8", "#b8791f"  # контролер-вікно


# ── shadow-vs-xip: дві дороги виконання коду із зовнішньої Flash ──────────────
def fig_shadow_vs_xip():
    W, H = 780, 430
    p = []
    midx = W / 2
    p.append(line(midx, 60, midx, H - 24, color="#d9dee5", sw=1.6, dash="5,5"))

    # ── ЛІВОРУЧ: тіньове копіювання ──
    p.append(text(W * 0.25, 40, "Тіньове копіювання", size=15, bold=True, color=INK))
    p.append(text(W * 0.25, 60, "весь код → у RAM на старті", size=11, color=MUTED))

    # зовнішня Flash (джерело коду)
    fL, fw, fh = textbox(W * 0.13, 150, "Зовнішня\nFlash\n(код)", size=12, bold=True,
                         color=BLU, fill=BLU_F, stroke=BLU, sw=1.8)
    p.append(fL)
    # SRAM (копія коду + дані)
    sL, sw_, sh = textbox(W * 0.38, 150, "SRAM\nкопія коду\n+ дані", size=12, bold=True,
                          color=GRN, fill=GRN_F, stroke=GRN, sw=1.8)
    p.append(sL)
    # товста стрілка копіювання на старті
    p.append(arrow(W * 0.13 + fw / 2, 150, W * 0.38 - sw_ / 2, 150, color=INK, sw=5))
    p.append(text(W * 0.255, 128, "весь код, старт", size=10, color=MUTED))

    # ядро читає з SRAM
    cL, cw, chh = textbox(W * 0.255, 300, "Ядро", size=13, bold=True,
                          color=RED, fill=RED_F, stroke=RED, sw=1.8)
    p.append(cL)
    p.append(arrow(W * 0.38, 150 + sh / 2, W * 0.30, 300 - chh / 2, color=RED, sw=2.2))
    p.append(text(W * 0.36, 245, "виконує", size=10, color=RED, anchor="start"))

    p.append(fitbox(W * 0.055, 340, W * 0.39, 56,
                    "− повільний старт (перелив коду)\n− RAM тримає ще й копію коду",
                    size=11, color=NEG, fill="#f7f9ff", stroke="#cdd8f5"))

    # ── ПРАВОРУЧ: XIP ──
    p.append(text(W * 0.75, 40, "XIP — на місці", size=15, bold=True, color=INK))
    p.append(text(W * 0.75, 60, "ядро виконує прямо з Flash", size=11, color=MUTED))

    # зовнішня Flash (код лишається тут)
    fR, fw2, fh2 = textbox(W * 0.62, 150, "Зовнішня\nFlash\n(код)", size=12, bold=True,
                           color=BLU, fill=BLU_F, stroke=BLU, sw=1.8)
    p.append(fR)
    # контролер-вікно
    kR, kw, kh = textbox(W * 0.80, 150, "Контролер\n(вікно)", size=11, bold=True,
                         color=CTL, fill=CTL_F, stroke=CTL, sw=1.8)
    p.append(kR)
    p.append(arrow(W * 0.62 + fw2 / 2, 150, W * 0.80 - kw / 2, 150, color=INK, sw=2))

    # SRAM лише під дані
    sR, sw2, sh2 = textbox(W * 0.92, 150, "SRAM\nлише дані", size=11, bold=True,
                           color=GRN, fill=GRN_F, stroke=GRN, sw=1.8)
    p.append(sR)

    # ядро читає код через вікно + дані з SRAM
    cR, cw2, ch2 = textbox(W * 0.80, 300, "Ядро", size=13, bold=True,
                           color=RED, fill=RED_F, stroke=RED, sw=1.8)
    p.append(cR)
    p.append(arrow(W * 0.80, 150 + kh / 2, W * 0.80, 300 - ch2 / 2, color=RED, sw=2.2))
    p.append(text(W * 0.815, 235, "код", size=10, color=RED, anchor="start"))
    p.append(arrow(W * 0.92, 150 + sh2 / 2, W * 0.85, 300 - ch2 / 2, color=GRN, sw=2))
    p.append(text(W * 0.905, 245, "дані", size=10, color=GRN, anchor="start"))

    p.append(fitbox(W * 0.555, 340, W * 0.39, 56,
                    "+ миттєвий старт (нема переливу)\n+ RAM уся вільна під дані",
                    size=11, color=FIELD, fill="#f2fbf5", stroke="#c7ebd4"))

    render(os.path.join(OUT, "shadow-vs-xip.svg"), W, H, *p)


# ── mmap-window: як контролер перетворює читання з пам'яті на розмову з Flash ──
def fig_mmap_window():
    W, H = 820, 360
    p = []
    yc = 150

    # 1) ядро виставляє адресу
    core, cw, ch = textbox(90, yc, "Ядро\nчитає адресу\n0x9000_0100", size=12, bold=True,
                           color=RED, fill=RED_F, stroke=RED, sw=1.8)
    p.append(core)
    p.append(text(90, yc + ch / 2 + 22, "«звичайна пам'ять»", size=10, color=MUTED))

    # внутрішня шина (зелена)
    p.append(line(90 + cw / 2, yc, 300, yc, color=GRN, sw=5))
    p.append(text((90 + cw / 2 + 300) / 2, yc - 12, "внутрішня шина", size=10,
                  color=GRN, bold=True))
    p.append(arrow(280, yc, 305, yc, color=INK, sw=2))

    # 2) контролер-вікно
    ctl, ctlw, ctlh = textbox(400, yc, "QSPI-контролер\nвікно 0x9000…\nу пам'яті",
                              size=12, bold=True, color=CTL, fill=CTL_F, stroke=CTL, sw=2)
    p.append(ctl)
    p.append(text(400, yc + ctlh / 2 + 22, "перекладає у послідовну мову", size=10, color=MUTED))

    # 3) послідовна транзакція (список фаз) між контролером і Flash
    phases = ["cmd READ (1 лінія)", "адреса (4 лінії)", "пауза-очікування", "дані ← 4 лінії"]
    bx, by, bw, bh = 520, 74, 150, 152
    p.append(rect(bx, by, bw, bh, fill="#fffaf0", stroke=CTL, sw=1.6, rx=8))
    p.append(text(bx + bw / 2, by + 18, "послідовно:", size=10, color=CTL, bold=True))
    for i, ph in enumerate(phases):
        col = FIELD if i == 3 else INK
        p.append(text(bx + 10, by + 42 + i * 26, "• " + ph, size=10, color=col, anchor="start"))
    p.append(arrow(400 + ctlw / 2, yc, bx - 4, yc, color=INK, sw=2))

    # 4) зовнішня Flash
    fl, flw, flh = textbox(750, yc, "Зовнішня\nFlash\n(NOR)", size=12, bold=True,
                           color=BLU, fill=BLU_F, stroke=BLU, sw=1.8)
    p.append(fl)
    p.append(arrow(bx + bw, yc, 750 - flw / 2, yc, color=INK, sw=2))
    # відповідь-дані назад
    p.append(line(750 - flw / 2, yc + 42, bx + bw, yc + 42, color=FIELD, sw=2))
    p.append(arrow(bx + bw + 30, yc + 42, bx + bw - 2, yc + 42, color=FIELD, sw=2))
    p.append(text((bx + bw + 750 - flw / 2) / 2, yc + 58, "слово даних", size=10,
                  color=FIELD, bold=True))

    # підсумковий рядок унизу
    p.append(text(W / 2, H - 20,
                  "ядро бачить просто пам'ять — уся послідовна кухня схована в контролері",
                  size=12, color=INK, bold=True))

    render(os.path.join(OUT, "mmap-window.svg"), W, H, *p)


if __name__ == "__main__":
    fig_shadow_vs_xip()
    fig_mmap_window()
    print("OK: figures written to", OUT)
