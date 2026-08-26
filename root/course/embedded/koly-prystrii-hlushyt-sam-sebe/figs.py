# -*- coding: utf-8 -*-
"""Фігури для теми koly-prystrii-hlushyt-sam-sebe.
(Коли пристрій глушить сам себе: гармоніки DC-DC, тактові генератори шин, десенсибілізація).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. desense-noise-floor: підйом шумової полиці та втрата SNR ─────────────
def fig_desense_noise_floor():
    W, H = 760, 340
    p = []

    # Тло блоків порівняння: Чистий ефір (ліворуч) та Внутрішнє глушіння (праворуч)
    p.append(rect(20, 20, 350, 300, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(rect(390, 20, 350, 300, fill="#fef2f2", stroke="#fca5a5", sw=1.2, rx=8))

    # Заголовки блоків
    t1, _, _ = textbox(195, 45, "Чистий ефір (без внутрішніх завад)", size=12, bold=True,
                       color=FIELD, fill="#eafaf0", stroke=FIELD, sw=1.2, min_w=280)
    p.append(t1)

    t2, _, _ = textbox(565, 45, "Внутрішнє глушіння (Self-Desense)", size=12, bold=True,
                       color=POS, fill="#fee2e2", stroke=POS, sw=1.2, min_w=280)
    p.append(t2)

    # --- Лівий графік (Чистий) ---
    ox1, oy1 = 55, 270
    p.append(arrow(ox1, oy1, ox1 + 290, oy1, color=INK, sw=1.4))  # вісь f
    p.append(arrow(ox1, oy1, ox1, 75, color=INK, sw=1.4))        # вісь P
    p.append(text(ox1 + 285, oy1 + 18, "f", size=11, italic=True, color=INK))
    p.append(text(ox1 - 10, 80, "P", size=11, italic=True, color=INK, anchor="end"))

    # Чиста шумова полиця (kTB + NF)
    ny1 = oy1 - 45
    p.append(line(ox1, ny1, ox1 + 270, ny1, color=MUTED, sw=1.4, dash="4 3"))
    p.append(text(ox1 + 10, ny1 + 14, "Шумова полиця: −115 дБм", size=9, color=MUTED, anchor="start"))

    # Слабкий корисний сигнал
    sx1 = ox1 + 140
    sig_h1 = 110
    p.append(line(sx1, oy1, sx1, oy1 - sig_h1, color=FIELD, sw=3.0))
    p.append(circle(sx1, oy1 - sig_h1, 3, fill=FIELD, stroke=FIELD))
    p.append(text(sx1, oy1 - sig_h1 - 8, "Сигнал (−95 дБм)", size=10, bold=True, color=FIELD))

    # Стрілка SNR
    p.append(line(sx1 + 45, ny1, sx1 + 45, oy1 - sig_h1, color=FIELD, sw=1.2))
    p.append(text(sx1 + 52, (ny1 + oy1 - sig_h1) / 2 + 3, "SNR = +20 дБ", size=9, bold=True, color=FIELD, anchor="start"))
    p.append(text(195, 298, "Прийом успішний (SNR > SNR_min)", size=10, bold=True, color=FIELD))

    # --- Правий графік (Глушіння) ---
    ox2, oy2 = 425, 270
    p.append(arrow(ox2, oy2, ox2 + 290, oy2, color=INK, sw=1.4))  # вісь f
    p.append(arrow(ox2, oy2, ox2, 75, color=INK, sw=1.4))        # вісь P
    p.append(text(ox2 + 285, oy2 + 18, "f", size=11, italic=True, color=INK))
    p.append(text(ox2 - 10, 80, "P", size=11, italic=True, color=INK, anchor="end"))

    # Базова та піднята шумова полиця
    p.append(line(ox2, ny1, ox2 + 270, ny1, color=MUTED, sw=1.0, dash="2 3"))
    ny2 = oy1 - 95  # підйом на 50px (~15 дБ)
    p.append(line(ox2, ny2, ox2 + 270, ny2, color=POS, sw=1.8, dash="5 3"))
    p.append(text(ox2 + 10, ny2 - 6, "Піднята полиця: −100 дБм (+15 дБ)", size=9, bold=True, color=POS, anchor="start"))

    # Гармоніка цифрової шини
    hx2 = ox2 + 90
    p.append(line(hx2, oy2, hx2, oy2 - 140, color=POS, sw=2.2))
    p.append(text(hx2, oy2 - 145, "Гармоніка SPI", size=9, bold=True, color=POS))

    # Той самий корисний сигнал
    sx2 = ox2 + 140
    p.append(line(sx2, oy2, sx2, oy2 - sig_h1, color="#94a3b8", sw=2.5))
    p.append(circle(sx2, oy2 - sig_h1, 3, fill="#94a3b8", stroke="#94a3b8"))
    p.append(text(sx2, oy2 - sig_h1 - 8, "Сигнал (−95 дБм)", size=10, color="#64748b"))

    # Зона втрати SNR
    p.append(line(sx2 + 45, ny2, sx2 + 45, oy2 - sig_h1, color=POS, sw=1.2))
    p.append(text(sx2 + 52, (ny2 + oy2 - sig_h1) / 2 + 3, "SNR = +5 дБ (< поріг)", size=9, bold=True, color=POS, anchor="start"))
    p.append(text(565, 298, "Втрата пакетів: сигнал потонув у шумі", size=10, bold=True, color=POS))

    render(os.path.join(OUT, "desense-noise-floor.svg"), W, H, *p,
           title="Десенсибілізація: підйом шумової полиці від внутрішніх завад")


# ── 2. clock-harmonics-spectrum: гармоніки цифрових шин і радіосмуги ───────
def fig_clock_harmonics_spectrum():
    W, H = 760, 320
    p = []

    # Вісь частот та амплітуди
    ox, oy = 60, 250
    aw = 640
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, 40, color=INK, sw=1.6))
    p.append(text(ox + aw - 10, oy + 22, "Частота f (МГц / ГГц)", size=11, bold=True, color=INK))
    p.append(text(ox - 12, 45, "Рівень (дБм)", size=11, bold=True, color=INK, anchor="end"))

    # Радіосмуги (кольорові вертикальні зони)
    # 433 МГц zone (x ≈ 165)
    p.append(rect(155, 60, 30, 190, fill="#e0f2fe", stroke="#7dd3fc", sw=1.0, rx=3))
    p.append(text(170, 75, "433M", size=9, bold=True, color=NEG))

    # 868 МГц zone (x ≈ 280)
    p.append(rect(265, 60, 35, 190, fill="#e0f2fe", stroke="#7dd3fc", sw=1.0, rx=3))
    p.append(text(282, 75, "868M", size=9, bold=True, color=NEG))

    # 2.4 ГГц zone (x ≈ 540..630)
    p.append(rect(520, 60, 110, 190, fill="#fef3c7", stroke="#fcd34d", sw=1.0, rx=3))
    p.append(text(575, 75, "2.4 ГГц ISM (Wi-Fi / BLE)", size=9, bold=True, color="#b45309"))

    # Гармоніки тактової частоти 40 МГц (меандр)
    harmonics = [
        (80, 180, "40M (1-ша)", False),
        (105, 150, "80M", False),
        (130, 135, "120M", False),
        (170, 115, "11-та (440M)", True),   # біля 433 МГц
        (205, 100, "200M", False),
        (240, 90, "240M", False),
        (280, 80, "22-га (880M)", True),   # біля 868 МГц
        (330, 70, "1.0G", False),
        (400, 58, "1.4G", False),
        (470, 48, "1.8G", False),
        (545, 42, "60-та (2.40G)", True),  # точне влучання в BLE Ch 37 / Wi-Fi Ch 1
        (580, 38, "61-ша (2.44G)", True),  # Wi-Fi Ch 7
        (615, 34, "62-га (2.48G)", True),  # BLE Ch 39
    ]

    # Спектральна обвідна
    env_pts = ["%d,%d" % (ox, oy - 195)]
    for x, h, _, _ in harmonics:
        env_pts.append("%d,%d" % (x, oy - h - 5))
    p.append('<polyline points="%s" fill="none" stroke="#94a3b8" stroke-width="1.2" stroke-dasharray="3 3"/>' % " ".join(env_pts))
    p.append(text(380, 130, "Спектральна обвідна гармонік меандру", size=9, italic=True, color="#64748b"))

    for x, h, lbl, is_target in harmonics:
        col = POS if is_target else MUTED
        sw = 2.0 if is_target else 1.2
        p.append(line(x, oy, x, oy - h, color=col, sw=sw))
        p.append(circle(x, oy - h, 2.5 if is_target else 1.5, fill=col, stroke=col))
        if is_target:
            p.append(text(x, oy - h - 7, lbl, size=9, bold=True, color=POS))

    # Пояснювальний блок знизу
    b1, _, _ = textbox(380, 288, "Гострі фронти (dV/dt > 1 В/нс) створюють сотні гармонік, що прямо б'ють у чутливі канали радіо",
                       size=11, bold=False, color=INK, fill="#f8fafc", stroke="#94a3b8", sw=1.0, min_w=620)
    p.append(b1)

    render(os.path.join(OUT, "clock-harmonics-spectrum.svg"), W, H, *p,
           title="Гармоніки тактових сигналів цифрових шин у радіочастотних діапазонах")


# ── 3. pcb-isolation-shielding: топологія плати та зони екранування ────────
def fig_pcb_isolation_shielding():
    W, H = 760, 380
    p = []

    # Контур друкованої плати (PCB)
    p.append(rect(30, 25, 700, 330, fill="#f1f5f9", stroke="#334155", sw=2.0, rx=10))
    p.append(text(50, 48, "Друкована плата (PCB) — Суцільний внутрішній шар GND", size=11, bold=True, color="#334155", anchor="start"))

    # 1. Зона Антени (лівий верхній кут)
    p.append(rect(50, 70, 160, 150, fill="#fef2f2", stroke=POS, sw=1.4, rx=6))
    p.append(text(130, 92, "РЧ-зона та Антена", size=11, bold=True, color=POS))
    p.append(rect(65, 110, 50, 90, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(90, 155, "Антена\n(Keepout)", size=9, bold=True, color=POS))
    # РЧ тракт і LNA
    p.append(rect(130, 130, 65, 50, fill="#ffffff", stroke="#dc2626", sw=1.2, rx=4))
    p.append(text(162, 158, "LNA / РЧ\nФільтр", size=9, bold=True, color=POS))
    p.append(line(115, 155, 130, 155, color=POS, sw=2.0))

    # 2. Зона Екрану (Shield Can) над МК і пам'яттю (центр)
    p.append('<rect x="250" y="70" width="260" height="200" rx="6" fill="#f8fafc" stroke="#2563eb" stroke-width="2.0" stroke-dasharray="6 4"/>')
    p.append(text(380, 92, "Металевий екран (Shield Can)", size=11, bold=True, color=NEG))

    # Зшивальні перехідні отвори (Via Stitching) по периметру екрану
    for vx in range(255, 510, 20):
        p.append(circle(vx, 72, 2.5, fill=NEG, stroke=NEG))
        p.append(circle(vx, 268, 2.5, fill=NEG, stroke=NEG))
    for vy in range(80, 265, 20):
        p.append(circle(252, vy, 2.5, fill=NEG, stroke=NEG))
        p.append(circle(508, vy, 2.5, fill=NEG, stroke=NEG))

    # Чипи всередині екрану
    p.append(rect(275, 115, 100, 80, fill="#ffffff", stroke="#475569", sw=1.4, rx=4))
    p.append(text(325, 155, "Мікро-\nконтролер\n(MCU / SoC)", size=10, bold=True, color=INK))

    p.append(rect(395, 115, 95, 80, fill="#ffffff", stroke="#475569", sw=1.4, rx=4))
    p.append(text(442, 155, "Швидкісна\nпам'ять\n(QSPI Flash)", size=10, bold=True, color=INK))

    p.append(line(375, 155, 395, 155, color=MUTED, sw=1.6))
    p.append(text(385, 145, "SPI", size=9, color=MUTED))

    # 3. Зона DC-DC живлення (правий бік)
    p.append(rect(540, 70, 170, 200, fill="#fefce8", stroke="#ca8a04", sw=1.4, rx=6))
    p.append(text(625, 92, "Імпульсне живлення", size=11, bold=True, color="#854d0e"))

    p.append(rect(555, 115, 65, 55, fill="#ffffff", stroke="#ca8a04", sw=1.2, rx=4))
    p.append(text(587, 145, "DC-DC\nBuck", size=9, bold=True, color="#854d0e"))

    p.append(rect(635, 115, 60, 55, fill="#ffffff", stroke="#ca8a04", sw=1.2, rx=4))
    p.append(text(665, 145, "Дросель\nSW", size=9, bold=True, color="#854d0e"))
    p.append(line(620, 142, 635, 142, color="#ca8a04", sw=2.0))

    # Феритова намистина (Ferrite Bead) на виході живлення
    p.append(rect(565, 200, 120, 45, fill="#dcfce7", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(625, 226, "Ферит (FB) + LDO\nдля РЧ-тракту", size=9, bold=True, color=FIELD))
    p.append(line(587, 170, 587, 200, color="#ca8a04", sw=1.6))

    # Лінія чистого живлення до РЧ
    p.append(arrow(565, 222, 210, 222, color=FIELD, sw=1.6))
    p.append(arrow(210, 222, 170, 180, color=FIELD, sw=1.6))
    p.append(text(380, 212, "Чиста лінія 3.3 В (RF_VDD)", size=9, bold=True, color=FIELD))

    # Нижній пояс правил
    t_bot, _, _ = textbox(380, 315, "Правила: рознесення в кути плати + екранна бляшанка + зшивка GND (via stitching) + феритова розв'язка",
                          size=11, bold=True, color=INK, fill="#ffffff", stroke="#64748b", sw=1.2, min_w=660)
    p.append(t_bot)

    render(os.path.join(OUT, "pcb-isolation-shielding.svg"), W, H, *p,
           title="Топологічні зони плати та апаратне екранування")


# ── 4. rx-quiet-window-timing: координація шин і вікна прийому ─────────────
def fig_rx_quiet_window_timing():
    W, H = 760, 320
    p = []

    # Часова вісь знизу
    ox, oy = 180, 275
    aw = 540
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.4))
    p.append(text(ox + aw - 10, oy + 20, "Час t", size=11, italic=True, color=INK))

    # Рівні каналів (Y-координати)
    y_rf = 60      # Радіотрансивер
    y_irq = 115    # Сигнал тригера RX_ACTIVE
    y_bus = 175    # Активність цифрових шин (SPI / Flash)
    y_noise = 235  # Шумова полиця вхідного тракту

    # Підписи каналів ліворуч
    p.append(text(165, y_rf + 10, "Стан Радіо (RX)", size=10, bold=True, color=INK, anchor="end"))
    p.append(text(165, y_irq + 10, "Сигнал RX_ACTIVE (IRQ)", size=10, bold=True, color=NEG, anchor="end"))
    p.append(text(165, y_bus + 10, "Шина SPI / DMA", size=10, bold=True, color=POS, anchor="end"))
    p.append(text(165, y_noise + 10, "Шум на вході LNA", size=10, bold=True, color="#b45309", anchor="end"))

    # Часові межі:
    t1 = 320
    t2 = 560

    # Вертикальні маркерні лінії та підсвічування Quiet Window
    p.append(f'<rect x="{t1}" y="35" width="{t2 - t1}" height="230" rx="4" fill="#f0fdf4" stroke="{FIELD}" stroke-width="1.2" stroke-dasharray="4 4"/>')
    p.append(text((t1 + t2) / 2, 48, "Захищене вікно: Rx Quiet Window", size=10, bold=True, color=FIELD))

    # 1. Радіотрансивер
    p.append(rect(180, y_rf - 10, t1 - 180, 30, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=3))
    p.append(text((180 + t1) / 2, y_rf + 9, "Очікування / Сканування", size=9, color=MUTED))

    p.append(rect(t1, y_rf - 10, t2 - t1, 30, fill="#dcfce7", stroke=FIELD, sw=1.4, rx=3))
    p.append(text((t1 + t2) / 2, y_rf + 9, "Прийом пакета (Preamble + Payload)", size=9, bold=True, color=FIELD))

    p.append(rect(t2, y_rf - 10, 140, 30, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=3))
    p.append(text((t2 + 700) / 2, y_rf + 9, "Обробка пакета", size=9, color=MUTED))

    # 2. Сигнал RX_ACTIVE (IRQ)
    p.append(line(180, y_irq + 15, t1, y_irq + 15, color=NEG, sw=2.0))
    p.append(line(t1, y_irq + 15, t1, y_irq - 5, color=NEG, sw=2.0))
    p.append(line(t1, y_irq - 5, t2, y_irq - 5, color=NEG, sw=2.5))
    p.append(line(t2, y_irq - 5, t2, y_irq + 15, color=NEG, sw=2.0))
    p.append(line(t2, y_irq + 15, 700, y_irq + 15, color=NEG, sw=2.0))

    # 3. Активність SPI / DMA
    p.append(rect(190, y_bus - 10, 115, 30, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    p.append(text(247, y_bus + 9, "DMA Flash / LCD", size=9, bold=True, color=POS))

    p.append(line(t1, y_bus + 5, t2, y_bus + 5, color=FIELD, sw=1.8, dash="4 2"))
    p.append(text((t1 + t2) / 2, y_bus + 9, "Шина призупинена (Тиша)", size=9, bold=True, color=FIELD))

    p.append(rect(t2 + 15, y_bus - 10, 115, 30, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    p.append(text(t2 + 72, y_bus + 9, "DMA відновлено", size=9, bold=True, color=POS))

    # 4. Рівень шуму LNA
    p.append(line(180, y_noise - 10, t1, y_noise - 10, color=POS, sw=2.0))
    p.append(text(250, y_noise - 16, "Шум: −98 дБм", size=9, bold=True, color=POS))

    p.append(line(t1, y_noise - 10, t1, y_noise + 12, color=MUTED, sw=1.0, dash="2 2"))
    p.append(line(t1, y_noise + 12, t2, y_noise + 12, color=FIELD, sw=2.2))
    p.append(line(t2, y_noise + 12, t2, y_noise - 10, color=MUTED, sw=1.0, dash="2 2"))
    p.append(text((t1 + t2) / 2, y_noise + 26, "Чистий ефір: −115 дБм", size=9, bold=True, color=FIELD))

    p.append(line(t2, y_noise - 10, 700, y_noise - 10, color=POS, sw=2.0))
    p.append(text(630, y_noise - 16, "Шум: −98 дБм", size=9, bold=True, color=POS))

    render(os.path.join(OUT, "rx-quiet-window-timing.svg"), W, H, *p,
           title="Часова діаграма координації шин і захищеного вікна прийому пакета")


def main():
    fig_desense_noise_floor()
    fig_clock_harmonics_spectrum()
    fig_pcb_isolation_shielding()
    fig_rx_quiet_window_timing()


if __name__ == "__main__":
    main()
