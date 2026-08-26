# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми 'Не бути поміченим: потужність, спрямованість, шпаруватість'."""

import sys
import os
import math

# Підключаємо спільний svgkit із scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_intercept_geometry():
    """Фігура 1: Геометрія перехоплення та баланс радіолінка."""
    w, h = 820, 420
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        rect(0, 0, w, h, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=0),
    ]

    # Заголовок
    out.append(text(w / 2, 28, "Геометрія перехоплення: радіолінк проти комплексу РЕР", size=16, bold=True, color=INK))

    # Зони виявлення навколо TX (cx=170, cy=230)
    tx_x, tx_y = 170, 230
    r_det_max = 150
    r_det_tpc = 80

    # Велика зона виявлення без TPC
    out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fde8e8" stroke="%s" stroke-width="1.5" stroke-dasharray="4,4"/>' % (tx_x, tx_y, r_det_max, POS))
    # Менша зона виявлення з TPC
    out.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#e8f8f0" stroke="%s" stroke-width="1.8"/>' % (tx_x, tx_y, r_det_tpc, FIELD))

    # Вузол TX
    tb_tx, _, _ = textbox(tx_x, tx_y, "TX: Передавач\n(EIRP = P_tx · G_tx)", size=12, pad=8, fill="#ffffff", stroke=INK, bold=True)
    out.append(tb_tx)

    # Законний приймач RX (праворуч-вгору, всередині зони зв'язку)
    rx_x, rx_y = tx_x + 85, tx_y - 50
    out.append(line(tx_x + 40, tx_y - 25, rx_x - 45, rx_y + 15, color=FIELD, sw=2.0))
    tb_rx, _, _ = textbox(rx_x, rx_y, "RX: Приймач лінка\n(R_comm, поріг SNR)", size=11, pad=6, fill="#f0fff4", stroke=FIELD, bold=True)
    out.append(tb_rx)

    # Пеленгатор РЕР / ESM (праворуч-вниз, далеко за межами TPC кола)
    esm_x, esm_y = tx_x + 220, tx_y + 80
    out.append(line(tx_x + 50, tx_y + 25, esm_x - 65, esm_y - 10, color=POS, sw=1.5, dash="3,3"))
    tb_esm, _, _ = textbox(esm_x, esm_y, "РЕР / Пеленгатор\n(G_esm >> 1, радіометр)", size=11, pad=6, fill="#fff5f5", stroke=POS, bold=True)
    out.append(tb_esm)

    # Підписи зон збоку / зверху
    out.append(text(tx_x, tx_y - r_det_max - 8, "Зона виявлення РЕР на максимальній потужності (P_max)", size=11, color=POS, anchor="middle", bold=True))
    out.append(text(tx_x, tx_y - r_det_tpc - 6, "Зона перехоплення з TPC (P_min)", size=11, color=FIELD, anchor="middle", bold=True))

    # Права інформаційна панель
    panel_x, panel_y, panel_w, panel_h = 490, 55, 305, 340
    out.append(rect(panel_x, panel_y, panel_w, panel_h, fill=FILL, stroke="#c0c8d0", sw=1.2, rx=6))
    out.append(text(panel_x + panel_w / 2, panel_y + 24, "Фізика енергетичного балансу", size=13, bold=True, color=INK))

    info_lines = [
        "1. Чутливість пеленгатора РЕР:",
        "   РЕР накопичує енергію радіометром",
        "   і має велику апертуру (G_esm).",
        "   Тому без контролю потужності R_det >> R_comm.",
        "",
        "2. Вплив потужності (TPC):",
        "   Дальність виявлення: R_det ∝ √(EIRP).",
        "   Зниження потужності на 10 дБ (у 10 разів)",
        "   зменшує радіус виявлення в 3.16 раза,",
        "   а площу перехоплення (S_det) — рівно в 10 разів.",
        "",
        "3. Мета LPI-тракту:",
        "   Тримати EIRP на мінімумі, щоб R_det < R_esm."
    ]
    ty = panel_y + 50
    for l in info_lines:
        if l.startswith("1.") or l.startswith("2.") or l.startswith("3."):
            out.append(text(panel_x + 12, ty, l, size=11, color=INK, anchor="start", bold=True))
        else:
            out.append(text(panel_x + 12, ty, l, size=11, color=MUTED if not l else INK, anchor="start"))
        ty += 21

    out.append("</svg>")
    path = os.path.join(OUT_DIR, "d-intercept-geometry.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("Generated:", path)


def fig_burst_toa_compression():
    """Фігура 2: Шпаруватий режим: стиснення часу передачі (Time on Air) та джитер пауз."""
    w, h = 820, 390
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        rect(0, 0, w, h, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=0),
    ]

    out.append(text(w / 2, 28, "Шпаруватий режим (Burst ToA) та псевдовипадковий джитер", size=16, bold=True, color=INK))

    # Секція 1: Повільна безперервна передача
    out.append(text(50, 65, "А. Традиційна повільна передача (10 кбіт/с, висока шпаруватість)", size=13, bold=True, color=POS, anchor="start"))
    
    # Вісь часу 1
    t1_y = 120
    out.append(line(50, t1_y, 760, t1_y, color=LINE, sw=1.5))
    out.append(text(765, t1_y + 4, "t", size=12, bold=True, color=LINE, anchor="start"))

    # Пакети 1 (довгі, періодичні)
    p1_ranges = [(70, 200), (270, 400), (470, 600), (670, 740)]
    for x1, x2 in p1_ranges:
        pw = x2 - x1
        out.append(rect(x1, t1_y - 35, pw, 35, fill="#fde8e8", stroke=POS, sw=1.5, rx=3))
        out.append(text(x1 + pw / 2, t1_y - 14, "ToA = 100 мс", size=11, bold=True, color=POS))

    # Позначення періоду
    out.append(line(70, t1_y + 12, 270, t1_y + 12, color=MUTED, sw=1.0))
    out.append(text(170, t1_y + 26, "Фіксований період T = 200 мс (Duty Cycle = 50%) — демаскує", size=11, color=MUTED))

    # Секція 2: Шпаруватий режим з ToA-компресією
    out.append(text(50, 205, "Б. LPI-режим: стиснена пачка (1 Мбіт/с) + псевдовипадковий джитер", size=13, bold=True, color=FIELD, anchor="start"))

    # Вісь часу 2
    t2_y = 265
    out.append(line(50, t2_y, 760, t2_y, color=LINE, sw=1.5))
    out.append(text(765, t2_y + 4, "t", size=12, bold=True, color=LINE, anchor="start"))

    # Пакети 2 (ультракороткі, випадкові паузи)
    p2_pos = [80, 260, 520, 710]
    burst_w = 16
    for xp in p2_pos:
        out.append(rect(xp, t2_y - 42, burst_w, 42, fill="#e8f8f0", stroke=FIELD, sw=1.8, rx=2))
        out.append(text(xp + burst_w / 2, t2_y - 48, "2 мс", size=10, bold=True, color=FIELD))

    # Паузи мовчання
    out.append(text(170, t2_y - 12, "Пауза Δt₁ = 850 мс", size=11, color=MUTED))
    out.append(text(390, t2_y - 12, "Пауза Δt₂ = 1320 мс (джитер)", size=11, color=MUTED))
    out.append(text(615, t2_y - 12, "Пауза Δt₃ = 940 мс", size=11, color=MUTED))

    out.append(text(w / 2, t2_y + 28, "Duty Cycle < 0.2%: радіометр РЕР не встигає інтегрувати енергію, а TDoA не будує кореляцію", size=11, bold=True, color=FIELD))

    # Нижній висновок
    out.append(rect(50, 325, 720, 48, fill=FILL, stroke="#c0c8d0", sw=1.0, rx=5))
    out.append(text(w / 2, 345, "Висока швидкість у каналі зменшує час у ефірі (ToA) пропорційно швидкості.", size=11, bold=True, color=INK))
    out.append(text(w / 2, 362, "Псевдовипадкові паузи ламають циклостаціонарний аналіз спектра пеленгаторами.", size=11, color=MUTED))

    out.append("</svg>")
    path = os.path.join(OUT_DIR, "d-burst-toa-compression.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("Generated:", path)


def fig_antenna_radiation_pattern():
    """Фігура 3: Просторова фільтрація: всеспрямована антена проти вузькоспрямованої."""
    w, h = 820, 420
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        rect(0, 0, w, h, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=0),
    ]

    out.append(text(w / 2, 28, "Просторова фільтрація: всеспрямований диполь проти спрямованої антени", size=16, bold=True, color=INK))

    # Ліва частина: Всеспрямована антена
    c1_x, c1_y = 200, 200
    out.append(text(c1_x, 65, "А. Всеспрямована антена (диполь)", size=13, bold=True, color=POS))
    
    # Діаграма - кругова
    out.append('<circle cx="%d" cy="%d" r="80" fill="#fde8e8" stroke="%s" stroke-width="1.8"/>' % (c1_x, c1_y, POS))
    out.append(circle(c1_x, c1_y, 4, fill=POS, stroke=INK, sw=1.0))
    out.append(text(c1_x, c1_y - 92, "Випромінювання на 360° (G ≈ 2.1 dBi)", size=11, color=POS, bold=True))
    out.append(text(c1_x, c1_y + 105, "Помітність для РЕР однакова в усіх напрямках", size=11, color=MUTED))
    out.append(text(c1_x, c1_y + 122, "Небезпечний сектор загрози: 360° (повне коло)", size=11, color=POS, bold=True))

    # Розділювач
    out.append(line(400, 60, 400, 390, color="#d0d7de", sw=1.2, dash="4,4"))

    # Права частина: Спрямована антена
    c2_x, c2_y = 590, 200
    out.append(text(c2_x, 65, "Б. Спрямована антена (Patch / Yagi)", size=13, bold=True, color=FIELD))

    # Головна пелюстка (еліпс витягнутий праворуч)
    lobe_main = "M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d Z" % (
        c2_x, c2_y,
        c2_x + 50, c2_y - 45, c2_x + 140, c2_y - 25, c2_x + 150, c2_y,
        c2_x + 140, c2_y + 25, c2_x + 50, c2_y + 45, c2_x, c2_y
    )
    out.append('<path d="%s" fill="#e8f8f0" stroke="%s" stroke-width="2.0"/>' % (lobe_main, FIELD))

    # Бокові пелюстки (Side Lobes) - малі
    side_top = "M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d Z" % (
        c2_x, c2_y,
        c2_x + 10, c2_y - 40, c2_x - 10, c2_y - 45, c2_x - 5, c2_y - 35,
        c2_x, c2_y - 25, c2_x, c2_y - 10, c2_x, c2_y
    )
    side_bot = "M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d Z" % (
        c2_x, c2_y,
        c2_x + 10, c2_y + 40, c2_x - 10, c2_y + 45, c2_x - 5, c2_y + 35,
        c2_x, c2_y + 25, c2_x, c2_y + 10, c2_x, c2_y
    )
    # Задня пелюстка (Back Lobe)
    back_lobe = "M %d %d C %d %d, %d %d, %d %d C %d %d, %d %d, %d %d Z" % (
        c2_x, c2_y,
        c2_x - 20, c2_y - 15, c2_x - 30, c2_y - 10, c2_x - 32, c2_y,
        c2_x - 30, c2_y + 10, c2_x - 20, c2_y + 15, c2_x, c2_y
    )
    out.append('<path d="%s" fill="#fff5f5" stroke="%s" stroke-width="1.2"/>' % (side_top, POS))
    out.append('<path d="%s" fill="#fff5f5" stroke="%s" stroke-width="1.2"/>' % (side_bot, POS))
    out.append('<path d="%s" fill="#fff5f5" stroke="%s" stroke-width="1.2"/>' % (back_lobe, POS))
    out.append(circle(c2_x, c2_y, 4, fill=FIELD, stroke=INK, sw=1.0))

    # Стрілка на приймач
    out.append(text(c2_x + 100, c2_y - 40, "Головний промінь (G_main = +14 dBi)", size=11, bold=True, color=FIELD))
    out.append(text(c2_x + 100, c2_y - 25, "Кут променя θ_3dB ≈ 30°", size=10, color=MUTED))

    out.append(text(c2_x - 85, c2_y - 45, "Бокові пелюстки (SLR ≤ -15 дБ)", size=10, color=POS))
    out.append(text(c2_x - 105, c2_y + 25, "Задня пелюстка (F/B ≥ 25 дБ)", size=10, color=POS))

    out.append(text(c2_x, c2_y + 105, "Поза головним променем дальність РЕР падає в 4–10 разів", size=11, color=MUTED))
    out.append(text(c2_x, c2_y + 122, "Сектор загрози звужено з 360° до ~30° (у 12 разів)", size=11, color=FIELD, bold=True))

    out.append("</svg>")
    path = os.path.join(OUT_DIR, "d-antenna-radiation-pattern.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("Generated:", path)


def fig_fhss_crypto_hopping():
    """Фігура 4: Архітектура криптографічного генератора стрибків FHSS."""
    w, h = 820, 380
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (w, h, w, h),
        rect(0, 0, w, h, fill="#ffffff", stroke="#d0d7de", sw=1.0, rx=0),
    ]

    out.append(text(w / 2, 28, "Криптографічний генератор стрибків робочої частоти (FHSS Core)", size=16, bold=True, color=INK))

    # Блоки конвеєра:
    # 1. Вхідні дані (Ключ + Епоха/Хоп-лічильник)
    b1_x, b1_y = 110, 110
    tb1, _, _ = textbox(b1_x, b1_y, "Вхідні параметри:\n• Секретний ключ K\n• Номер кроку t_hop\n• Ідентифікатор мережі", size=11, pad=8, fill="#ffffff", stroke=INK, bold=False)
    out.append(tb1)

    # Стрілка 1->2
    out.append(line(205, b1_y, 255, b1_y, color=INK, sw=1.8))
    out.append('<polygon points="255,%d 245,%d 245,%d" fill="%s"/>' % (b1_y, b1_y - 4, b1_y + 4, INK))

    # 2. Криптографічне ядро (ChaCha / PRF)
    b2_x, b2_y = 350, b1_y
    tb2, _, _ = textbox(b2_x, b2_y, "Криптографічний PRF:\nChaCha20 / SipHash Core\n32-бітний псевдовипадковий\nвивід PRNG(K, t_hop)", size=11, pad=8, fill="#f0fff4", stroke=FIELD, bold=False)
    out.append(tb2)

    # Стрілка 2->3
    out.append(line(445, b1_y, 495, b1_y, color=INK, sw=1.8))
    out.append('<polygon points="495,%d 485,%d 485,%d" fill="%s"/>' % (b1_y, b1_y - 4, b1_y + 4, INK))

    # 3. Модуль мапування на канали та чорний список
    b3_x, b3_y = 590, b1_y
    tb3, _, _ = textbox(b3_x, b3_y, "Мапування каналів:\n• Редукція без зміщення (mod M)\n• Фільтр чорного списку (AFH)\n• Індекс каналу: ch_idx", size=11, pad=8, fill="#f0f7ff", stroke=NEG, bold=False)
    out.append(tb3)

    # Стрілка 3->4 (вниз)
    out.append(line(b3_x, b1_y + 45, b3_x, 215, color=INK, sw=1.8))
    out.append('<polygon points="%d,215 %d,205 %d,205" fill="%s"/>' % (b3_x, b3_x - 4, b3_x + 4, INK))

    # 4. Апаратний радіомодуль (PLL Synthesizer)
    b4_x, b4_y = b3_x, 260
    tb4, _, _ = textbox(b4_x, b4_y, "Радіотракт / PLL Синтезатор:\nВстановлення частоти f = F_base + ch_idx · ΔF\nЧас перемикання PLL: τ_lock < 50 мкс", size=11, pad=8, fill="#fff5f5", stroke=POS, bold=False)
    out.append(tb4)

    # Ліва нижня інформаційна панель (чому криптографія, а не LFSR)
    out.append(rect(40, 195, 340, 145, fill=FILL, stroke="#c0c8d0", sw=1.0, rx=5))
    out.append(text(210, 215, "Чому саме криптографічний генератор:", size=12, bold=True, color=INK))
    fhss_notes = [
        "• Звичайний LFSR (m-послідовність) зламується",
        "  алгоритмом Берлекемпа-Мессі за 2N відліків.",
        "• Крипто-PRF робить наступний канал непередбачуваним",
        "  для станції РЕР навіть після перехоплення 10 000 хопів.",
        "• Відсутність відкритого заголовка в ефірі —",
        "  синхронізація тримається на спільному лічильнику часу."
    ]
    ny = 236
    for note in fhss_notes:
        out.append(text(50, ny, note, size=10, color=INK, anchor="start"))
        ny += 17

    out.append("</svg>")
    path = os.path.join(OUT_DIR, "d-fhss-crypto-hopping.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("Generated:", path)


if __name__ == "__main__":
    fig_intercept_geometry()
    fig_burst_toa_compression()
    fig_antenna_radiation_pattern()
    fig_fhss_crypto_hopping()
