# -*- coding: utf-8 -*-
"""figs.py — фігури до вставки «Помпи ICL7660-класу» (comp-charge-pumps.md).
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── comp-hookup: пінаут 7660 + дві обв'язки (інвертор / подвоювач) ───────────
# Несе вагу: показує ОДНУ й ту саму 8-вивідну деталь у двох увімкненнях.
# Інвертор — живлення на V+, вихід −Vвх на VOUT. Подвоювач — вхід на VOUT,
# а 2·Vвх знімають уже з V+. Видно, що змінюється лише роль виводів.
def fig_hookup():
    W, H = 960, 540
    parts = []

    # ── один корпус DIP-8, намальований у заданому центрі, з обома обв'язками
    def chip(cx, cy, title, left_in, right_out, vin_label, vout_label,
             vin_pin, vout_pin):
        out = []
        bw, bh = 150, 200
        x, y = cx - bw / 2, cy - bh / 2
        # корпус
        out.append(rect(x, y, bw, bh, fill=FILL, stroke=INK, sw=2, rx=8))
        # ключ (півколо-виїмка згори)
        out.append('<path d="M%.1f %.1f a 10 10 0 0 0 20 0" fill="none" '
                   'stroke="%s" stroke-width="2"/>' % (cx - 10, y, INK))
        out.append(text(cx, cy - 4, "7660", size=15, color=MUTED, bold=True))
        out.append(text(cx, cy + 14, "клас", size=11, color=MUTED))

        # назви виводів: ліворуч 1..4 згори вниз, праворуч 8..5 згори вниз
        left_names  = ["NC/BOOST", "CAP+", "GND", "CAP−"]
        right_names = ["V+", "OSC", "LV", "VOUT"]
        left_nums   = [1, 2, 3, 4]
        right_nums  = [8, 7, 6, 5]
        ys = [y + bh * (i + 0.5) / 4 for i in range(4)]

        for i, yy in enumerate(ys):
            # ліві ніжки
            out.append(line(x - 16, yy, x, yy, color=INK, sw=2))
            out.append(text(x - 6, yy - 5, str(left_nums[i]), size=10,
                            color=MUTED, anchor="end"))
            out.append(text(x + 6, yy + 4, left_names[i], size=11, color=INK,
                            anchor="start"))
            # праві ніжки
            out.append(line(x + bw, yy, x + bw + 16, yy, color=INK, sw=2))
            out.append(text(x + bw + 6, yy - 5, str(right_nums[i]), size=10,
                            color=MUTED, anchor="start"))
            out.append(text(x + bw - 6, yy + 4, right_names[i], size=11,
                            color=INK, anchor="end"))

        # летючий конденсатор Cf між CAP+ (лів.2, ys[1]) і CAP− (лів.4, ys[3])
        cfx = x - 52
        out.append(line(x - 16, ys[1], cfx, ys[1], color=INK, sw=2))
        out.append(line(x - 16, ys[3], cfx, ys[3], color=INK, sw=2))
        out.append(line(cfx, ys[1], cfx, ys[1] + 14, color=INK, sw=2))
        out.append(line(cfx, ys[3], cfx, ys[3] - 14, color=INK, sw=2))
        # дві пластини Cf
        out.append(line(cfx - 13, ys[1] + 14, cfx + 13, ys[1] + 14, color=INK, sw=2.5))
        out.append(line(cfx - 13, ys[3] - 14, cfx + 13, ys[3] - 14, color=INK, sw=2.5))
        out.append(text(cfx - 20, (ys[1] + ys[3]) / 2 + 4, "Cf", size=12,
                        color=NEG, anchor="end", italic=True))

        # GND символ на лів.3 (ys[2])
        gx = x - 40
        out.append(line(x - 16, ys[2], gx, ys[2], color=INK, sw=2))
        out.append(line(gx, ys[2], gx, ys[2] + 12, color=INK, sw=2))
        out.append(line(gx - 9, ys[2] + 12, gx + 9, ys[2] + 12, color=INK, sw=2))
        out.append(line(gx - 5, ys[2] + 16, gx + 5, ys[2] + 16, color=INK, sw=2))

        # ── вхід і вихід — на потрібних виводах (різні для двох схем)
        pin_y = {8: ys[0], 7: ys[1], 6: ys[2], 5: ys[3]}  # праві
        # вхід Vвх
        iy = pin_y[vin_pin]
        out.append(line(x + bw + 16, iy, x + bw + 60, iy, color=POS, sw=2.5))
        out.append(plus(x + bw + 70, iy, r=8))
        out.append(text(x + bw + 70, iy - 16, vin_label, size=12, color=POS,
                        anchor="middle", bold=True))
        # вихід Vвих + резервуарний конденсатор Cout на землю
        oy = pin_y[vout_pin]
        out.append(line(x + bw + 16, oy, x + bw + 60, oy, color=INK, sw=2.5))
        # Cout
        coutx = x + bw + 60
        out.append(line(coutx, oy, coutx, oy + 22, color=INK, sw=2))
        out.append(line(coutx - 12, oy + 22, coutx + 12, oy + 22, color=INK, sw=2.5))
        out.append(line(coutx - 12, oy + 28, coutx + 12, oy + 28, color=INK, sw=2.5))
        # земля під Cout
        out.append(line(coutx, oy + 28, coutx, oy + 38, color=INK, sw=2))
        out.append(line(coutx - 8, oy + 38, coutx + 8, oy + 38, color=INK, sw=2))
        out.append(line(coutx - 4, oy + 42, coutx + 4, oy + 42, color=INK, sw=2))
        out.append(text(coutx + 18, oy + 6, "Cout", size=11, color=MUTED,
                        anchor="start", italic=True))
        # підпис виходу
        col = NEG if vout_label.startswith("−") else POS
        out.append(text(coutx, oy - 12, vout_label, size=13, color=col,
                        anchor="middle", bold=True))

        # заголовок схеми
        out.append(text(cx, y - 22, title, size=15, color=INK, bold=True))
        return out

    # ліва схема — ІНВЕРТОР: Vвх→V+(8), Vвих=−Vвх на VOUT(5)
    parts += chip(255, 300, "Інвертор:  −Vвх",
                  None, None, "Vвх", "−Vвх", vin_pin=8, vout_pin=5)
    # права схема — ПОДВОЮВАЧ: Vвх→VOUT(5), Vвих=+2·Vвх на V+(8)
    parts += chip(705, 300, "Подвоювач:  2·Vвх",
                  None, None, "Vвх", "2·Vвх", vin_pin=5, vout_pin=8)

    # роздільна штрихова лінія між схемами
    parts.append(line(W / 2, 70, W / 2, H - 30, color=MUTED, sw=1.2, dash="6,6"))

    render("img/comp-hookup.svg", W, H, *parts,
           title="Помпа 7660-класу: одна деталь — дві обв'язки")


if __name__ == "__main__":
    fig_hookup()
    print("comp-hookup.svg generated")
