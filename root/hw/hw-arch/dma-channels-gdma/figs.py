# -*- coding: utf-8 -*-
"""Фігури до теми «GDMA: загальний пул каналів».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Імена файлів — slug-only, без номерів; підписи фігур дає Markdown.
Стаття: bundled-vs-pool, channel-mux.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AUD  = "#8e44ad"   # фіолетовий акцент
WARM = "#c0a020"   # жовтий акцент (комутатор/арбітр)
GONE = "#b0b0b0"   # «спить/недоступне»


# ── Фіг.1: припаяний DMA проти спільного пулу ───────────────────────────────
def fig_bundled_vs_pool():
    W, H = 860, 470
    f = [text(W / 2, 26, "Дві архітектури власності DMA: припаяно до периферії проти спільного пулу",
              size=15, bold=True)]

    # Розділювач посередині
    f.append(line(W / 2, 46, W / 2, H - 44, color=MUTED, sw=1.2, dash="5,5"))

    # ── Ліва половина: вбудований DMA у кожній периферії ──
    f.append(text(215, 62, "Вбудований DMA: рушій у кожній периферії", size=13, bold=True, color=POS))

    # Три периферії, кожна з власним рушієм; дві «сплять» (сірі)
    peri = [
        (90,  "SPI",  "рушій", False),   # активний
        (90,  None,   None,    None),    # (заповнимо нижче окремо)
    ]
    rows = [
        (86,  "SPI",  "власний\nрушій", INK,  False),
        (176, "I2S",  "рушій\n(спить)", GONE, True),
        (266, "АЦП",  "рушій\n(спить)", GONE, True),
    ]
    for (y, name, sub, col, sleeping) in rows:
        # блок периферії
        f.append(rect(60, y, 140, 64, fill="#f9fafb", stroke=col, sw=1.8, rx=8))
        f.append(text(76, y + 20, name, size=13, bold=True,
                      color=(GONE if sleeping else INK), anchor="start"))
        # вбудований рушій усередині
        rf = "#fdecea" if not sleeping else "#f0f0f0"
        rc = POS if not sleeping else GONE
        f.append(rect(120, y + 12, 68, 40, fill=rf, stroke=rc, sw=1.4))
        f.append(mtext(154, y + 28, sub, size=9, color=rc))

    # активний рушій → дані
    f.append(arrow(200, 118, 250, 118, color=POS, sw=2))
    f.append(text(225, 108, "дані", size=9, color=POS))

    # «дисплею мало» — червона підказка внизу лівої половини
    f.append(rect(60, 350, 340, 74, fill="#fdecea", stroke=POS, sw=1.4, rx=8))
    f.append(fitbox(60, 350, 340, 38,
                    "Дисплею мало смуги — поруч сплять рушії.",
                    size=11, fill="#fdecea", stroke="none", color=INK, bold=True))
    f.append(fitbox(60, 388, 340, 34,
                    "Сплячий рушій перекласти НЕМОЖЛИВО.",
                    size=11, fill="#fdecea", stroke="none", color=POS))

    # ── Права половина: GDMA — спільний пул ──
    ox = 440
    f.append(text(ox + 200, 62, "GDMA: спільний пул, розв'язаний з периферіями",
                  size=13, bold=True, color=FIELD))

    # периферії праворуч — лише піднімають запит, без рушіїв усередині
    pr = [(86, "SPI", NEG), (176, "I2S", AUD), (266, "АЦП", FIELD)]
    for (y, name, col) in pr:
        f.append(rect(ox + 20, y, 96, 44, fill="#f9fafb", stroke=col, sw=1.6, rx=8))
        f.append(text(ox + 68, y + 27, name, size=12, bold=True, color=col))

    # спільний блок-пул із трьома однаковими каналами
    px, py, pw, ph = ox + 190, 78, 130, 210
    f.append(rect(px, py, pw, ph, fill="#fff6e0", stroke=WARM, sw=1.9, rx=10))
    f.append(text(px + pw / 2, py + 20, "Пул GDMA", size=12, bold=True, color=INK))
    chy = [py + 40, py + 100, py + 160]
    chan_col = [NEG, AUD, FIELD]
    for i, cy in enumerate(chy):
        f.append(rect(px + 16, cy, pw - 32, 42, fill=BG, stroke=chan_col[i], sw=1.5))
        f.append(text(px + pw / 2, cy + 18, "канал %d" % i, size=11, bold=True, color=chan_col[i]))
        f.append(text(px + pw / 2, cy + 33, "src/dst/len", size=8, color=MUTED))

    # програмні стрілки периферія → канал (будь-який до будь-кого)
    for i, (y, name, col) in enumerate(pr):
        f.append(arrow(ox + 116, y + 22, px + 16, chy[i] + 21, color=col, sw=1.6))
    f.append(text(px - 8, 60, "прив'язка кодом", size=9, color=MUTED, anchor="middle", italic=True))

    # шина в пам'ять праворуч
    f.append(arrow(px + pw, py + ph / 2, px + pw + 40, py + ph / 2, sw=2.2))
    f.append(rect(px + pw + 40, py + 30, 66, ph - 60, fill="#f4f6f8", stroke=LINE, sw=1.6, rx=8))
    f.append(fitbox(px + pw + 40, py + 30, 66, ph - 60, "спільна\nшина\nй RAM",
                    size=10, fill="#f4f6f8", stroke="none", color=INK, bold=True))

    # виграш — зелена підказка внизу правої половини
    f.append(rect(ox + 20, 350, 400, 74, fill="#e8f8ee", stroke=FIELD, sw=1.4, rx=8))
    f.append(fitbox(ox + 20, 350, 400, 38,
                    "Вільний канал іде тій периферії, якій зараз потрібно.",
                    size=11, fill="#e8f8ee", stroke="none", color=INK, bold=True))
    f.append(fitbox(ox + 20, 388, 400, 34,
                    "Перепризначення — один запис у регістр-селектор.",
                    size=11, fill="#e8f8ee", stroke="none", color=FIELD))

    f.append(text(W / 2, H - 16,
                  "Припаяний рушій сплячого сусіда не позичиш; спільний пул тече туди, де потреба.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "bundled-vs-pool.svg"), W, H, *f)


# ── Фіг.2: комутатор канал↔периферія, поділ TX/RX ───────────────────────────
def fig_channel_mux():
    W, H = 860, 460
    f = [text(W / 2, 26, "Комутатор канал ↔ периферія: селектор задає прив'язку, напрямок задає канал",
              size=14, bold=True)]

    # ── Ліворуч: периферії з лініями запиту ──
    f.append(text(120, 62, "Периферії (запит DMA)", size=12, bold=True, color=MUTED))
    peri = [(84, "SPI2", NEG), (154, "I2S0", AUD), (224, "LCD/CAM", FIELD), (294, "АЦП", "#7a5000")]
    for (y, name, col) in peri:
        f.append(rect(40, y, 130, 46, fill="#f9fafb", stroke=col, sw=1.6, rx=8))
        f.append(text(105, y + 27, name, size=12, bold=True, color=col))

    # ── Комутатор посередині ──
    mx, my, mw, mh = 250, 74, 110, 250
    f.append(rect(mx, my, mw, mh, fill="#fff6e0", stroke=WARM, sw=1.9, rx=10))
    f.append(fitbox(mx, my + 6, mw, 54, "Комутатор\n(peri_sel)", size=12,
                    fill="none", stroke="none", color=INK, bold=True))
    f.append(mtext(mx + mw / 2, my + mh - 22, "номер\nпериферії", size=9, color=MUTED))
    # лінії периферія → комутатор
    for (y, name, col) in peri:
        f.append(line(170, y + 23, mx, y + 23, color=col, sw=1.5))

    # ── Праворуч: пул, дві колонки TX / RX ──
    # RX-колонка (периферія → пам'ять, in-link)
    rx_x = 430
    f.append(text(rx_x + 70, 62, "RX-канали", size=12, bold=True, color=NEG))
    f.append(text(rx_x + 70, 76, "периферія → пам'ять · in-link", size=9, color=MUTED))
    rx_rows = [(88, "RX0", "sel = LCD/CAM (5)", FIELD), (150, "RX1", "sel = I2S0", AUD)]
    for (y, name, sub, col) in rx_rows:
        f.append(rect(rx_x, y, 140, 46, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
        f.append(text(rx_x + 12, y + 20, name, size=12, bold=True, color=NEG, anchor="start"))
        f.append(text(rx_x + 12, y + 36, sub, size=9, color=col, anchor="start"))

    # TX-колонка (пам'ять → периферія, out-link)
    f.append(text(rx_x + 70, 224, "TX-канали", size=12, bold=True, color=POS))
    f.append(text(rx_x + 70, 238, "пам'ять → периферія · out-link", size=9, color=MUTED))
    tx_rows = [(250, "TX0", "sel = LCD/CAM (5)", FIELD), (312, "TX1", "sel = SPI2", NEG)]
    for (y, name, sub, col) in tx_rows:
        f.append(rect(rx_x, y, 140, 46, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
        f.append(text(rx_x + 12, y + 20, name, size=12, bold=True, color=POS, anchor="start"))
        f.append(text(rx_x + 12, y + 36, sub, size=9, color=col, anchor="start"))

    # стрілки комутатор → канали (прив'язки за селектором)
    f.append(arrow(mx + mw, 96, rx_x, 108, color=FIELD, sw=1.5))   # LCD/CAM → RX0
    f.append(arrow(mx + mw, 168, rx_x, 168, color=AUD, sw=1.5))    # I2S0 → RX1
    f.append(arrow(mx + mw, 244, rx_x, 268, color=FIELD, sw=1.5))  # LCD/CAM → TX0
    f.append(arrow(mx + mw, 108, rx_x, 330, color=NEG, sw=1.3))    # SPI2 → TX1

    # шина в пам'ять
    bus_x = rx_x + 160
    f.append(rect(bus_x, 88, 60, 270, fill="#f4f6f8", stroke=LINE, sw=1.6, rx=8))
    f.append(fitbox(bus_x, 88, 60, 270, "спільна\nшина\n↓\nRAM", size=10,
                    fill="none", stroke="none", color=INK, bold=True))
    for y in [111, 173, 273, 335]:
        f.append(arrow(rx_x + 140, y, bus_x, y, color=MUTED, sw=1.4))

    # висновок: двобічна периферія бере пару (LCD/CAM = RX0 + TX0)
    f.append(rect(40, 372, 780, 56, fill="#f9fafb", stroke=WARM, sw=1.4, rx=8))
    f.append(mtext(430, 393,
                   ["LCD/CAM тут задіяна двічі — RX0 (кадр з камери в пам'ять) і TX0 (кадр на екран):",
                    "двобічна периферія бере ДВА канали з пулу."],
                   size=11, color=INK, bold=True))

    f.append(text(W / 2, H - 12,
                  "Селектор каналу тримає номер периферії — це вся прив'язка; напрямок — властивість каналу, не периферії.",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "channel-mux.svg"), W, H, *f)


if __name__ == "__main__":
    fig_bundled_vs_pool()
    fig_channel_mux()
    print("OK: 2 фігури у", IMG)
