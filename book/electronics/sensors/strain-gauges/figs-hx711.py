# -*- coding: utf-8 -*-
"""Фігури до вставки «Тензодавач + HX711».
Запуск:  python figs-hx711.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Підключення: 4 дроти комірки → HX711 → 2 дроти до MCU; вимір ратіометричний ─
def fig_hx711_wiring():
    W, H = 820, 400
    f = [text(W / 2, 26, "Тензодавач → HX711 → MCU: міст живиться й читається тим самим AVDD",
              size=15, bold=True)]

    # --- ліворуч: тензодавач (ваг-комірка) як міст із чотирма виводами ---
    cx, cy, s = 150, 200, 64
    top = (cx, cy - s); bot = (cx, cy + s); lft = (cx - s, cy); rgt = (cx + s, cy)
    f.append(text(cx, 96, "тензодавач (міст)", size=12, bold=True))
    for a, b in [(top, rgt), (rgt, bot), (bot, lft), (lft, top)]:
        f.append(line(a[0], a[1], b[0], b[1], color=LINE, sw=2))
    for a, b in [(top, rgt), (rgt, bot), (bot, lft), (lft, top)]:
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        f.append(rect(mx - 11, my - 8, 22, 16, fill="#eef3f9", stroke=LINE, sw=1.4))
    # чотири кольорові виводи
    f.append(text(top[0], top[1] - 12, "E+ (черв.)", size=10, bold=True, color=POS))
    f.append(text(bot[0], bot[1] + 20, "E− (чорн.)", size=10, bold=True, color=MUTED))
    f.append(text(lft[0] - 26, lft[1] - 6, "A−", size=11, bold=True, color=NEG))
    f.append(text(lft[0] - 22, lft[1] + 10, "(біл.)", size=9, color=MUTED))
    f.append(text(rgt[0] + 26, rgt[1] - 6, "A+", size=11, bold=True, color=FIELD))
    f.append(text(rgt[0] + 24, rgt[1] + 10, "(зел.)", size=9, color=MUTED))

    # --- посередині: HX711 ---
    hx_x, hx_y, hx_w, hx_h = 360, 120, 200, 168
    f.append(rect(hx_x, hx_y, hx_w, hx_h, fill="#fff7ec", stroke="#b8860b", sw=2))
    f.append(text(hx_x + hx_w / 2, hx_y + 24, "HX711", size=15, bold=True))
    f.append(text(hx_x + hx_w / 2, hx_y + 42, "24-біт ΔΣ-АЦП", size=10, color=MUTED))
    # блоки всередині
    f.append(fitbox(hx_x + 16, hx_y + 56, 168, 30, "PGA ×128 / ×64",
                    size=11, bold=True, fill="#fdecea", stroke=POS))
    f.append(fitbox(hx_x + 16, hx_y + 92, 168, 30, "ΔΣ-модулятор + цифра",
                    size=10, bold=True, fill="#eef3f9", stroke=NEG))
    f.append(fitbox(hx_x + 16, hx_y + 128, 168, 28, "регулятор AVDD",
                    size=10, bold=True, fill="#eafaf1", stroke=FIELD))

    # дроти комірка → HX711
    f.append(line(top[0], top[1] - 18, top[0], 108, color=POS, sw=2))
    f.append(line(top[0], 108, hx_x, 108, color=POS, sw=2))
    f.append(line(hx_x, 108, hx_x, hx_y + 138, color=POS, sw=2))  # AVDD назад у міст
    f.append(arrow(hx_x, hx_y + 138, hx_x - 1, hx_y + 138, color=POS))
    f.append(line(bot[0], bot[1] + 26, bot[0], 318, color=MUTED, sw=2))
    f.append(line(bot[0], 318, hx_x, 318, color=MUTED, sw=2))
    f.append(line(hx_x, 318, hx_x, hx_y + hx_h, color=MUTED, sw=2))
    f.append(arrow(rgt[0] + 8, rgt[1], hx_x, hx_y + 80, color=FIELD))
    f.append(arrow(lft[0] - 8, lft[1] + 30, hx_x, hx_y + 96, color=NEG))

    # --- праворуч: MCU, лише два цифрові дроти ---
    mc_x, mc_y, mc_w, mc_h = 640, 150, 150, 110
    f.append(rect(mc_x, mc_y, mc_w, mc_h, fill="#eef3f9", stroke=NEG, sw=2))
    f.append(text(mc_x + mc_w / 2, mc_y + 30, "MCU", size=15, bold=True))
    f.append(text(mc_x + mc_w / 2, mc_y + 54, "2 цифрові", size=11, color=MUTED))
    f.append(text(mc_x + mc_w / 2, mc_y + 70, "лінії GPIO", size=11, color=MUTED))
    # DOUT та PD_SCK
    f.append(arrow(hx_x + hx_w, hx_y + 70, mc_x, mc_y + 30, color=INK))
    f.append(text((hx_x + hx_w + mc_x) / 2, hx_y + 58, "DOUT", size=11, bold=True))
    f.append(arrow(mc_x, mc_y + 80, hx_x + hx_w, hx_y + 110, color=INK))
    f.append(text((hx_x + hx_w + mc_x) / 2, mc_y + 100, "PD_SCK", size=11, bold=True))

    # підпис-висновок про ратіометричність
    f.append(rect(60, 344, 700, 40, fill="#eafaf1", stroke=FIELD, sw=1.5))
    f.append(text(410, 369,
                  "AVDD живить міст І служить опорою АЦП: дрейф живлення скорочується сам — вимір ратіометричний",
                  size=11, bold=True, color=INK))

    render(os.path.join(IMG, 'hx711-wiring.svg'), W, H, *f)


# ── 2. Протокол читання: DOUT↓ = готово; 24 такти MSB-first; зайві такти = режим ──
def fig_hx711_protocol():
    W, H = 820, 420
    f = [text(W / 2, 26, "Один обмін HX711: чекаємо DOUT↓, тактуємо 24 біти, далі 1–3 зайвих такти",
              size=15, bold=True)]

    base = 70
    # вісь часу
    f.append(arrow(40, 360, 790, 360, color=MUTED))
    f.append(text(770, 376, "час", size=10, color=MUTED))

    # --- DOUT ---
    yd = base
    f.append(text(36, yd + 4, "DOUT", size=12, bold=True, anchor="start"))
    # високо (не готово) → падає (готово) → дані → назад високо
    f.append(line(110, yd - 18, 210, yd - 18, color=NEG, sw=2.4))            # high = не готово
    f.append(line(210, yd - 18, 210, yd + 14, color=NEG, sw=2.4))            # фронт вниз
    f.append(text(210, yd - 26, "DOUT↓ = дані готові", size=10, bold=True, color=POS))
    # ділянка даних — пунктир «біти»
    f.append(line(210, yd + 14, 590, yd + 14, color=NEG, sw=2.4, dash="6 4"))
    f.append(text(400, yd + 30, "24 біти даних, старший перший (MSB)", size=10, color=MUTED))
    f.append(line(590, yd + 14, 600, yd - 18, color=NEG, sw=2.4))            # 25-й такт тягне DOUT угору
    f.append(line(600, yd - 18, 700, yd - 18, color=NEG, sw=2.4))
    f.append(text(648, yd - 26, "знову високо", size=9, color=MUTED))

    # --- PD_SCK ---
    yc = base + 150
    f.append(text(36, yc + 4, "PD_SCK", size=12, bold=True, anchor="start"))
    f.append(line(110, yc + 14, 230, yc + 14, color=INK, sw=2))              # тиша до старту
    # 24 робочі імпульси (намалюємо групою прямокутних піків)
    x = 240; pw = 12; gap = 4
    for i in range(13):  # умовні «зубці» = такти (узагальнено)
        f.append(line(x, yc + 14, x, yc - 12, color=INK, sw=1.6))
        f.append(line(x, yc - 12, x + pw, yc - 12, color=INK, sw=1.6))
        f.append(line(x + pw, yc - 12, x + pw, yc + 14, color=INK, sw=1.6))
        f.append(line(x + pw, yc + 14, x + pw + gap, yc + 14, color=INK, sw=1.6))
        x += pw + gap
    f.append(line(110, yc + 14, 240, yc + 14, color=INK, sw=2))
    f.append(text(345, yc + 34, "24 такти зчитують біти", size=10, color=MUTED))
    # зайві такти (інший колір)
    for i in range(3):
        f.append(line(x, yc + 14, x, yc - 12, color=POS, sw=2))
        f.append(line(x, yc - 12, x + pw, yc - 12, color=POS, sw=2))
        f.append(line(x + pw, yc - 12, x + pw, yc + 14, color=POS, sw=2))
        f.append(line(x + pw, yc + 14, x + pw + gap, yc + 14, color=POS, sw=2))
        x += pw + gap
    f.append(text(x + 30, yc - 18, "+1…3 зайвих", size=10, bold=True, color=POS, anchor="start"))

    # --- таблиця: скільки зайвих → який канал/підсилення ---
    tb_x, tb_y, tb_w = 470, base + 6, 320
    rows = [
        ("зайвих тактів", "канал · підсилення", True),
        ("+1  (усього 25)", "A · ×128   (±20 мВ)", False),
        ("+2  (усього 26)", "B · ×32", False),
        ("+3  (усього 27)", "A · ×64   (±40 мВ)", False),
    ]
    rh = 28
    for i, (a, b, hd) in enumerate(rows):
        yy = tb_y + i * rh
        fill = "#fff7ec" if hd else "#ffffff"
        f.append(rect(tb_x, yy, tb_w, rh, fill=fill, stroke=LINE, sw=1.2, rx=3))
        f.append(text(tb_x + 12, yy + 18, a, size=11, bold=hd, anchor="start",
                      color=(INK if hd else POS)))
        f.append(text(tb_x + 150, yy + 18, b, size=11, bold=hd, anchor="start"))

    f.append(text(W / 2, 398,
                  "вибір на наступний вимір задають зайві такти; після зміни перший відлік відкидають",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, 'hx711-protocol.svg'), W, H, *f)


if __name__ == "__main__":
    fig_hx711_wiring()
    fig_hx711_protocol()
    print("OK: 2 фігури у", IMG)
