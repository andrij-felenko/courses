# -*- coding: utf-8 -*-
# Окрема фігура для вставки hist-sccb.md (щоб не колотися з figs.py у паралельних правках).
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def _wave(pts, color, sw=2.2):
    d = "M " + " L ".join("%.1f %.1f" % (x, yv) for x, yv in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, color, sw)


def fig_ninth_bit():
    """9-й такт: I2C у ньому слухає ACK від відомого, SCCB його ігнорує (Don't-Care)."""
    W, H = 940, 470
    parts = [text(W / 2, 28, "Дев'ятий такт: ось де SCCB розходиться з I2C", size=18, bold=True)]

    x0 = 124
    xe = 900
    slot = (xe - x0) / 9.0          # ширина одного бітового такту
    base_off = 40                    # низ хвилі від верху доріжки
    top_off = 6                      # верх хвилі

    def row(y, sda_label, sda_col, ack_fill, ack_txt, ack_col, note):
        # підписи ліній
        parts.append(text(x0 - 12, y + 24, "SCL", size=12, bold=True, anchor="end", color=MUTED))
        parts.append(text(x0 - 12, y + 24 + 62, sda_label, size=12, bold=True, anchor="end", color=sda_col))
        # SCL: дев'ять однакових імпульсів
        scly = y
        pts = [(x0, scly + base_off)]
        for k in range(9):
            cx = x0 + k * slot
            pts += [(cx + slot * 0.22, scly + base_off), (cx + slot * 0.22, scly + top_off),
                    (cx + slot * 0.78, scly + top_off), (cx + slot * 0.78, scly + base_off)]
        pts += [(xe, scly + base_off)]
        parts.append(_wave(pts, MUTED, sw=1.8))
        # номери тактів
        for k in range(9):
            cx = x0 + k * slot + slot / 2
            parts.append(text(cx, scly - 4, str(k + 1), size=10, color="#9aa5b5"))
        # SDA: 8 біт даних (рівень) + виділений 9-й такт
        sday = y + 62
        parts.append(line(x0, sday + base_off / 2, x0 + 8 * slot, sday + base_off / 2,
                          color=sda_col, sw=2, dash="3,3"))
        for k in range(8):
            cx = x0 + k * slot + slot / 2
            parts.append(text(cx, sday + base_off / 2 + 4, "D%d" % (7 - k), size=9.5, color=sda_col))
        # 9-й такт — кольорова плашка
        bx = x0 + 8 * slot
        parts.append(rect(bx + 3, sday + 6, slot - 6, base_off - 8, fill=ack_fill,
                          stroke=ack_col, sw=1.6, rx=4))
        parts.append(text(bx + slot / 2, sday + base_off / 2 + 4, ack_txt, size=10.5,
                          bold=True, color=ack_col))
        # примітка під 9-м тактом
        parts.append(fitbox(x0, sday + base_off + 8, xe - x0, 30, note,
                            size=10.5, fill="none", stroke="none", sw=0, color="#4b5563"))

    # ── I2C ──
    parts.append(fitbox(x0 - 6, 52, 150, 26, "I2C", size=13, bold=True,
                        fill="#eaf0fd", stroke=NEG, sw=1.5, color=NEG))
    row(90, "SDA", NEG, "#eaf0fd", "ACK", NEG,
        "9-й такт = ACK: відомий сам тягне лінію в 0 — «отримав». Немає нуля → майстер бачить, що зв'язку немає.")

    # ── SCCB ──
    parts.append(fitbox(x0 - 6, 250, 150, 26, "SCCB", size=13, bold=True,
                        fill="#fff3e6", stroke="#c96a1b", sw=1.5, color="#c96a1b"))
    row(288, "SIO_D", "#c96a1b", "#f4f5f7", "X", "#c96a1b",
        "9-й такт = Don't-Care: лінію відпущено у плав, майстер на неї НЕ дивиться й жене наступну фазу.")

    parts.append(fitbox(150, 424, 640, 38,
                        "Ті самі 8 біт даних, той самий 9-й такт — тільки I2C у ньому СЛУХАЄ підтвердження,"
                        " а SCCB його викидає.",
                        size=11.5, fill="#fff8f0", stroke="#c96a1b", sw=1.5))
    render(os.path.join(OUT, "sccb-ninth-bit.svg"), W, H, *parts)


if __name__ == "__main__":
    fig_ninth_bit()
    print("done")
