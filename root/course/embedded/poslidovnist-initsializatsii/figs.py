#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор векторних діаграм для теми «Послідовність ініціалізації: порядок, затримки, перевірка»."""

import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def create_bringup_timeline():
    """Діаграма 1: Часова шкала етапів bring-up від подачі напруги до перших валідних даних."""
    w, h = 880, 360
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">')
    svg.append('  <defs>')
    svg.append('    <style>')
    svg.append('      .bg { fill: #f8fafc; }')
    svg.append('      .title { font-family: system-ui, sans-serif; font-size: 15px; font-weight: 700; fill: #0f172a; }')
    svg.append('      .label { font-family: system-ui, sans-serif; font-size: 12px; font-weight: 600; fill: #334155; }')
    svg.append('      .sublabel { font-family: system-ui, sans-serif; font-size: 11px; fill: #64748b; }')
    svg.append('      .code { font-family: ui-monospace, monospace; font-size: 11px; fill: #1e293b; }')
    svg.append('      .axis { stroke: #cbd5e1; stroke-width: 1.2; stroke-dasharray: 4,4; }')
    svg.append('      .line-main { stroke: #0284c7; stroke-width: 2.5; fill: none; }')
    svg.append('      .line-por { stroke: #e11d48; stroke-width: 1.5; stroke-dasharray: 3,3; fill: none; }')
    svg.append('      .box-phase { rx: 6px; ry: 6px; stroke-width: 1.5; }')
    svg.append('    </style>')
    svg.append('    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append('      <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" />')
    svg.append('    </marker>')
    svg.append('  </defs>')

    # Тло
    svg.append(f'  <rect class="bg" x="0" y="0" width="{w}" height="{h}" rx="8"/>')

    # Заголовок
    svg.append('  <text class="title" x="24" y="32">Часова діаграма послідовності запуску (Bring-Up Timeline)</text>')

    # Ліва колонка сигналів / рівнів (x=24..130)
    svg.append('  <text class="label" x="24" y="65">1. Напруга VDD</text>')
    svg.append('  <text class="sublabel" x="24" y="80">Живлення чипа</text>')
    svg.append('  <text class="code" x="24" y="100" fill="#e11d48">V_POR=1.65 В</text>')
    svg.append('  <text class="code" x="24" y="118" fill="#0284c7">V_NOM=3.3 В</text>')

    svg.append('  <text class="label" x="24" y="170">2. Стан чипа</text>')
    svg.append('  <text class="sublabel" x="24" y="186">Внутрішнє ядро</text>')

    svg.append('  <text class="label" x="24" y="260">3. Шина I2C/SPI</text>')
    svg.append('  <text class="sublabel" x="24" y="276">Транзакції МК</text>')

    # Часова вісь знизу
    svg.append('  <line x1="150" y1="320" x2="840" y2="320" stroke="#64748b" stroke-width="1.5" marker-end="url(#arrow)"/>')
    svg.append('  <text class="sublabel" x="845" y="324">Час t</text>')

    # Вертикальні розділові фази
    x_t0 = 160
    x_t1 = 265
    x_t2 = 390
    x_t3 = 525
    x_t4 = 680
    x_t5 = 820

    for x_pos in [x_t0, x_t1, x_t2, x_t3, x_t4, x_t5]:
        svg.append(f'  <line class="axis" x1="{x_pos}" y1="50" x2="{x_pos}" y2="315"/>')

    # 1. Сигнал VDD
    svg.append(f'  <path class="line-main" d="M 150 115 L {x_t0} 115 L {x_t1} 65 L 830 65"/>')
    # Лінія порогу POR
    svg.append(f'  <line class="line-por" x1="{x_t0}" y1="90" x2="830" y2="90"/>')

    # 2. Фази стану чипа
    # Фаза 0: Вимкнено
    svg.append(f'  <rect class="box-phase" x="{x_t0}" y="150" width="{x_t1 - x_t0}" height="45" fill="#fee2e2" stroke="#f87171"/>')
    svg.append(f'  <text class="code" x="{(x_t0 + x_t1)/2}" y="177" text-anchor="middle" font-weight="700">Ramp Up</text>')

    # Фаза 1: POR / Boot Time
    svg.append(f'  <rect class="box-phase" x="{x_t1}" y="150" width="{x_t2 - x_t1}" height="45" fill="#ffedd5" stroke="#fb923c"/>')
    svg.append(f'  <text class="code" x="{(x_t1 + x_t2)/2}" y="168" text-anchor="middle" font-weight="700">POR / Booting</text>')
    svg.append(f'  <text class="sublabel" x="{(x_t1 + x_t2)/2}" y="184" text-anchor="middle">LDO &amp; NVM Load</text>')

    # Фаза 2: SW Reset & ID Check
    svg.append(f'  <rect class="box-phase" x="{x_t2}" y="150" width="{x_t3 - x_t2}" height="45" fill="#fef08a" stroke="#eab308"/>')
    svg.append(f'  <text class="code" x="{(x_t2 + x_t3)/2}" y="168" text-anchor="middle" font-weight="700">Soft Reset</text>')
    svg.append(f'  <text class="sublabel" x="{(x_t2 + x_t3)/2}" y="184" text-anchor="middle">Poll Ready bit</text>')

    # Фаза 3: Configuration & Read-Back
    svg.append(f'  <rect class="box-phase" x="{x_t3}" y="150" width="{x_t4 - x_t3}" height="45" fill="#e0e7ff" stroke="#818cf8"/>')
    svg.append(f'  <text class="code" x="{(x_t3 + x_t4)/2}" y="168" text-anchor="middle" font-weight="700">Configuring</text>')
    svg.append(f'  <text class="sublabel" x="{(x_t3 + x_t4)/2}" y="184" text-anchor="middle">Range, ODR, Readback</text>')

    # Фаза 4: Active Mode
    svg.append(f'  <rect class="box-phase" x="{x_t4}" y="150" width="{x_t5 - x_t4}" height="45" fill="#dcfce7" stroke="#4ade80"/>')
    svg.append(f'  <text class="code" x="{(x_t4 + x_t5)/2}" y="168" text-anchor="middle" font-weight="700">Active Mode</text>')
    svg.append(f'  <text class="sublabel" x="{(x_t4 + x_t5)/2}" y="184" text-anchor="middle">Valid Data DRDY</text>')

    # 3. Активність шини
    # Тиша (Заборона транзакцій)
    svg.append(f'  <rect class="box-phase" x="{x_t0}" y="245" width="{x_t2 - x_t0}" height="45" fill="#f1f5f9" stroke="#cbd5e1"/>')
    svg.append(f'  <text class="code" x="{(x_t0 + x_t2)/2}" y="264" text-anchor="middle" fill="#dc2626" font-weight="700">Тиша на шині (Hi-Z / NACK)</text>')
    svg.append(f'  <text class="sublabel" x="{(x_t0 + x_t2)/2}" y="280" text-anchor="middle">Звернення ЗАБОРОНЕНІ</text>')

    # Скидання та перевірка ID
    svg.append(f'  <rect class="box-phase" x="{x_t2}" y="245" width="{x_t3 - x_t2}" height="45" fill="#ffffff" stroke="#94a3b8"/>')
    svg.append(f'  <text class="code" x="{(x_t2 + x_t3)/2}" y="264" text-anchor="middle">CMD: SW_RESET</text>')
    svg.append(f'  <text class="code" x="{(x_t2 + x_t3)/2}" y="280" text-anchor="middle" fill="#0284c7">RD: WHO_AM_I</text>')

    # Запис та Read-Back
    svg.append(f'  <rect class="box-phase" x="{x_t3}" y="245" width="{x_t4 - x_t3}" height="45" fill="#ffffff" stroke="#94a3b8"/>')
    svg.append(f'  <text class="code" x="{(x_t3 + x_t4)/2}" y="264" text-anchor="middle">WR &amp; Read-Back</text>')
    svg.append(f'  <text class="sublabel" x="{(x_t3 + x_t4)/2}" y="280" text-anchor="middle">Верифікація полів</text>')

    # Періодичне читання
    svg.append(f'  <rect class="box-phase" x="{x_t4}" y="245" width="{x_t5 - x_t4}" height="45" fill="#ffffff" stroke="#94a3b8"/>')
    svg.append(f'  <text class="code" x="{(x_t4 + x_t5)/2}" y="264" text-anchor="middle">Burst Read Out</text>')
    svg.append(f'  <text class="sublabel" x="{(x_t4 + x_t5)/2}" y="280" text-anchor="middle">Збір вибірок</text>')

    # Часові інтервали
    svg.append(f'  <line x1="{x_t1}" y1="138" x2="{x_t2}" y2="138" stroke="#ea580c" stroke-width="1.2"/>')
    svg.append(f'  <text class="code" x="{(x_t1 + x_t2)/2}" y="132" text-anchor="middle" fill="#ea580c">t_POR: 1..100 мс</text>')

    svg.append(f'  <line x1="{x_t2}" y1="138" x2="{x_t3}" y2="138" stroke="#ca8a04" stroke-width="1.2"/>')
    svg.append(f'  <text class="code" x="{(x_t2 + x_t3)/2}" y="132" text-anchor="middle" fill="#ca8a04">t_RESET: 2..15 мс</text>')

    svg.append(f'  <line x1="{x_t3}" y1="138" x2="{x_t4}" y2="138" stroke="#4f46e5" stroke-width="1.2"/>')
    svg.append(f'  <text class="code" x="{(x_t3 + x_t4)/2}" y="132" text-anchor="middle" fill="#4f46e5">t_CONFIG</text>')

    svg.append(f'  <line x1="{x_t4}" y1="138" x2="{x_t5}" y2="138" stroke="#16a34a" stroke-width="1.2"/>')
    svg.append(f'  <text class="code" x="{(x_t4 + x_t5)/2}" y="132" text-anchor="middle" fill="#16a34a">t_SETTLE: 5..50 мс</text>')

    svg.append('</svg>')

    out_file = os.path.join(OUT_DIR, "bringup-timeline.svg")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated {out_file}")


def create_init_pipeline():
    """Діаграма 2: Архітектурний конвеєр 5-етапної ініціалізації з обробкою помилок."""
    w, h = 900, 420
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">')
    svg.append('  <defs>')
    svg.append('    <style>')
    svg.append('      .bg { fill: #f8fafc; }')
    svg.append('      .title { font-family: system-ui, sans-serif; font-size: 15px; font-weight: 700; fill: #0f172a; }')
    svg.append('      .step-hdr { font-family: system-ui, sans-serif; font-size: 12.5px; font-weight: 700; fill: #0f172a; }')
    svg.append('      .desc { font-family: system-ui, sans-serif; font-size: 10.5px; fill: #475569; }')
    svg.append('      .code { font-family: ui-monospace, monospace; font-size: 10px; fill: #1e293b; }')
    svg.append('      .step-box { rx: 8px; ry: 8px; stroke-width: 1.5; }')
    svg.append('      .flow-arrow { stroke: #0284c7; stroke-width: 2; fill: none; marker-end: url(#arrow-blue); }')
    svg.append('      .err-arrow { stroke: #ef4444; stroke-width: 1.5; stroke-dasharray: 4,3; fill: none; marker-end: url(#arrow-red); }')
    svg.append('    </style>')
    svg.append('    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append('      <path d="M 0 1 L 10 5 L 0 9 z" fill="#0284c7" />')
    svg.append('    </marker>')
    svg.append('    <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append('      <path d="M 0 1 L 10 5 L 0 9 z" fill="#ef4444" />')
    svg.append('    </marker>')
    svg.append('  </defs>')

    svg.append(f'  <rect class="bg" x="0" y="0" width="{w}" height="{h}" rx="8"/>')
    svg.append('  <text class="title" x="24" y="30">Архітектурний конвеєр надійної ініціалізації (Device Init Pipeline)</text>')

    # 5 блоків по горизонталі
    box_w = 150
    box_h = 180
    y_top = 58
    xs = [24 + i * (box_w + 24) for i in range(5)]

    # Етап 1: POR & Delay
    svg.append(f'  <rect class="step-box" x="{xs[0]}" y="{y_top}" width="{box_w}" height="{box_h}" fill="#f0fdf4" stroke="#86efac"/>')
    svg.append(f'  <text class="step-hdr" x="{xs[0] + 10}" y="{y_top + 22}">1. POR &amp; Затримка</text>')
    svg.append(f'  <text class="desc" x="{xs[0] + 10}" y="{y_top + 44}">• Подача VDD</text>')
    svg.append(f'  <text class="desc" x="{xs[0] + 10}" y="{y_top + 62}">• Стабілізація LDO</text>')
    svg.append(f'  <text class="desc" x="{xs[0] + 10}" y="{y_top + 80}">• Витримка t_boot</text>')
    svg.append(f'  <text class="code" x="{xs[0] + 10}" y="{y_top + 106}" fill="#16a34a">delay_ms(10..50)</text>')
    svg.append(f'  <text class="desc" x="{xs[0] + 10}" y="{y_top + 130}">Шина в Hi-Z стані</text>')
    svg.append(f'  <text class="desc" x="{xs[0] + 10}" y="{y_top + 148}">Захист від NACK</text>')

    # Етап 2: Soft Reset & ID
    svg.append(f'  <rect class="step-box" x="{xs[1]}" y="{y_top}" width="{box_w}" height="{box_h}" fill="#eff6ff" stroke="#93c5fd"/>')
    svg.append(f'  <text class="step-hdr" x="{xs[1] + 10}" y="{y_top + 22}">2. Скидання та ID</text>')
    svg.append(f'  <text class="desc" x="{xs[1] + 10}" y="{y_top + 44}">• Запис SW_RESET</text>')
    svg.append(f'  <text class="desc" x="{xs[1] + 10}" y="{y_top + 62}">• Poll Ready біта</text>')
    svg.append(f'  <text class="desc" x="{xs[1] + 10}" y="{y_top + 80}">• Читання CHIP_ID</text>')
    svg.append(f'  <text class="code" x="{xs[1] + 10}" y="{y_top + 106}" fill="#2563eb">id == EXPECT_ID</text>')
    svg.append(f'  <text class="desc" x="{xs[1] + 10}" y="{y_top + 130}">Таймаут опитування</text>')
    svg.append(f'  <text class="desc" x="{xs[1] + 10}" y="{y_top + 148}">Перевірка зв\'язку</text>')

    # Етап 3: Конфігурація
    svg.append(f'  <rect class="step-box" x="{xs[2]}" y="{y_top}" width="{box_w}" height="{box_h}" fill="#fdf4ff" stroke="#f0abfc"/>')
    svg.append(f'  <text class="step-hdr" x="{xs[2] + 10}" y="{y_top + 22}">3. Конфігурація</text>')
    svg.append(f'  <text class="desc" x="{xs[2] + 10}" y="{y_top + 44}">1) Електрика (IO)</text>')
    svg.append(f'  <text class="desc" x="{xs[2] + 10}" y="{y_top + 62}">2) Діапазон шкали</text>')
    svg.append(f'  <text class="desc" x="{xs[2] + 10}" y="{y_top + 80}">3) Фільтр (DLPF)</text>')
    svg.append(f'  <text class="desc" x="{xs[2] + 10}" y="{y_top + 98}">4) Частота ODR</text>')
    svg.append(f'  <text class="desc" x="{xs[2] + 10}" y="{y_top + 116}">5) Переривання INT</text>')
    svg.append(f'  <text class="code" x="{xs[2] + 10}" y="{y_top + 142}" fill="#9333ea">wr(REG, val)</text>')

    # Етап 4: Read-Back
    svg.append(f'  <rect class="step-box" x="{xs[3]}" y="{y_top}" width="{box_w}" height="{box_h}" fill="#fefce8" stroke="#fde047"/>')
    svg.append(f'  <text class="step-hdr" x="{xs[3] + 10}" y="{y_top + 22}">4. Read-Back</text>')
    svg.append(f'  <text class="desc" x="{xs[3] + 10}" y="{y_top + 44}">• Зчитування назад</text>')
    svg.append(f'  <text class="desc" x="{xs[3] + 10}" y="{y_top + 62}">• Бітова маска</text>')
    svg.append(f'  <text class="desc" x="{xs[3] + 10}" y="{y_top + 80}">• Порівняння полів</text>')
    svg.append(f'  <text class="code" x="{xs[3] + 10}" y="{y_top + 106}" fill="#ca8a04">(rd&amp;m) == (wr&amp;m)</text>')
    svg.append(f'  <text class="desc" x="{xs[3] + 10}" y="{y_top + 130}">Ігнорування RO-біт</text>')
    svg.append(f'  <text class="desc" x="{xs[3] + 10}" y="{y_top + 148}">Захист від збоїв</text>')

    # Етап 5: Активація / Робота
    svg.append(f'  <rect class="step-box" x="{xs[4]}" y="{y_top}" width="{box_w}" height="{box_h}" fill="#ecfdf5" stroke="#6ee7b7"/>')
    svg.append(f'  <text class="step-hdr" x="{xs[4] + 10}" y="{y_top + 22}">5. Активація</text>')
    svg.append(f'  <text class="desc" x="{xs[4] + 10}" y="{y_top + 44}">• Режим Normal</text>')
    svg.append(f'  <text class="desc" x="{xs[4] + 10}" y="{y_top + 62}">• Час прогріву</text>')
    svg.append(f'  <text class="desc" x="{xs[4] + 10}" y="{y_top + 80}">• Очищення FIFO</text>')
    svg.append(f'  <text class="code" x="{xs[4] + 10}" y="{y_top + 106}" fill="#059669">STATE_READY</text>')
    svg.append(f'  <text class="desc" x="{xs[4] + 10}" y="{y_top + 130}">Старт вимірювань</text>')
    svg.append(f'  <text class="desc" x="{xs[4] + 10}" y="{y_top + 148}">Передача в app</text>')

    # Стрілки прямого потоку між етапами
    for i in range(4):
        x_from = xs[i] + box_w
        x_to = xs[i+1]
        y_mid = y_top + 75
        svg.append(f'  <line class="flow-arrow" x1="{x_from}" y1="{y_mid}" x2="{x_to}" y2="{y_mid}"/>')

    # Нижня частина: Обробка збоїв (Retry & Fallback)
    y_err = 285
    box_err_w = 480
    box_err_h = 105

    svg.append(f'  <rect class="step-box" x="24" y="{y_err}" width="{box_err_w}" height="{box_err_h}" fill="#fff1f2" stroke="#fca5a5"/>')
    svg.append(f'  <text class="step-hdr" x="36" y="{y_err + 22}" fill="#e11d48">Обробка помилок та Retry Logic</text>')
    svg.append(f'  <text class="desc" x="36" y="{y_err + 44}">1. Збій зв\'язку / NACK / Розбіжність Read-Back / Таймаут</text>')
    svg.append(f'  <text class="desc" x="36" y="{y_err + 64}">2. Лічильник спроб (retries &lt; MAX): експоненційний backoff</text>')
    svg.append(f'  <text class="desc" x="36" y="{y_err + 84}">3. Відновлення шини (Bus Recovery) та повтор з Кроку 1</text>')

    # Блок Safe State
    box_safe_w = 330
    x_safe = 540
    svg.append(f'  <rect class="step-box" x="{x_safe}" y="{y_err}" width="{box_safe_w}" height="{box_err_h}" fill="#fef2f2" stroke="#ef4444"/>')
    svg.append(f'  <text class="step-hdr" x="{x_safe + 12}" y="{y_err + 22}" fill="#b91c1c">Аварійний Safe State</text>')
    svg.append(f'  <text class="desc" x="{x_safe + 12}" y="{y_err + 44}">• Вичерпано ліміт спроб (retries &gt;= MAX)</text>')
    svg.append(f'  <text class="desc" x="{x_safe + 12}" y="{y_err + 64}">• Відкат стану драйвера (Driver Rollback)</text>')
    svg.append(f'  <text class="desc" x="{x_safe + 12}" y="{y_err + 84}">• Перехід у безпечний режим системи</text>')

    # Стрілки помилок від етапів 2, 3, 4 вниз
    for i in [1, 2, 3]:
        x_err_src = xs[i] + box_w / 2
        svg.append(f'  <line class="err-arrow" x1="{x_err_src}" y1="{y_top + box_h}" x2="{x_err_src}" y2="{y_err}"/>')

    # Стрілка з Retry до Safe State
    svg.append(f'  <line class="err-arrow" x1="{24 + box_err_w}" y1="{y_err + 52}" x2="{x_safe}" y2="{y_err + 52}"/>')

    svg.append('</svg>')

    out_file = os.path.join(OUT_DIR, "init-pipeline.svg")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated {out_file}")


def create_readback_verification():
    """Діаграма 3: Детальна механіка Read-Back верифікації регістрів з маскуванням."""
    w, h = 800, 380
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">')
    svg.append('  <defs>')
    svg.append('    <style>')
    svg.append('      .bg { fill: #f8fafc; }')
    svg.append('      .title { font-family: system-ui, sans-serif; font-size: 15px; font-weight: 700; fill: #0f172a; }')
    svg.append('      .hdr { font-family: system-ui, sans-serif; font-size: 13px; font-weight: 700; fill: #0f172a; }')
    svg.append('      .label { font-family: system-ui, sans-serif; font-size: 11.5px; fill: #334155; }')
    svg.append('      .code { font-family: ui-monospace, monospace; font-size: 11px; fill: #0f172a; }')
    svg.append('      .box-pane { rx: 6px; ry: 6px; stroke-width: 1.5; }')
    svg.append('      .flow-arrow { stroke: #0284c7; stroke-width: 1.8; fill: none; marker-end: url(#arrow-blue); }')
    svg.append('    </style>')
    svg.append('    <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append('      <path d="M 0 1 L 10 5 L 0 9 z" fill="#0284c7" />')
    svg.append('    </marker>')
    svg.append('    <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append('      <path d="M 0 1 L 10 5 L 0 9 z" fill="#16a34a" />')
    svg.append('    </marker>')
    svg.append('    <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">')
    svg.append('      <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626" />')
    svg.append('    </marker>')
    svg.append('  </defs>')

    svg.append(f'  <rect class="bg" x="0" y="0" width="{w}" height="{h}" rx="8"/>')
    svg.append('  <text class="title" x="24" y="30">Анатомія зворотної верифікації (Read-Back Verification)</text>')

    # 1. Запис цільового значення
    y_step1 = 65
    svg.append(f'  <rect class="box-pane" x="24" y="{y_step1}" width="220" height="95" fill="#eff6ff" stroke="#93c5fd"/>')
    svg.append(f'  <text class="hdr" x="36" y="{y_step1 + 22}">1. Цільовий запис</text>')
    svg.append(f'  <text class="code" x="36" y="{y_step1 + 45}">Target = 0x34</text>')
    svg.append(f'  <text class="label" x="36" y="{y_step1 + 65}">[0b00110100] (Range+ODR)</text>')
    svg.append(f'  <text class="label" x="36" y="{y_step1 + 83}">wr_reg(CTRL_REG, 0x34)</text>')

    # 2. Фізичне зчитування з чипа
    svg.append(f'  <rect class="box-pane" x="280" y="{y_step1}" width="220" height="95" fill="#fefce8" stroke="#fde047"/>')
    svg.append(f'  <text class="hdr" x="292" y="{y_step1 + 22}">2. Читання з шини</text>')
    svg.append(f'  <text class="code" x="292" y="{y_step1 + 45}">ReadBack = 0xB4</text>')
    svg.append(f'  <text class="label" x="292" y="{y_step1 + 65}">[0b10110100] (Біт 7=DRDY)</text>')
    svg.append(f'  <text class="label" x="292" y="{y_step1 + 83}">rd_reg(CTRL_REG, &amp;val)</text>')

    # 3. Застосування маски Care-Bits
    y_step2 = 195
    svg.append(f'  <rect class="box-pane" x="280" y="{y_step2}" width="220" height="85" fill="#fdf4ff" stroke="#f0abfc"/>')
    svg.append(f'  <text class="hdr" x="292" y="{y_step2 + 22}">3. Маскування (Care Bits)</text>')
    svg.append(f'  <text class="code" x="292" y="{y_step2 + 45}">MASK = 0x7F (біти 0..6 R/W)</text>')
    svg.append(f'  <text class="label" x="292" y="{y_step2 + 65}">Біт 7 (RO Status) ігнорується</text>')

    # 4. Компаратор
    svg.append(f'  <rect class="box-pane" x="540" y="115" width="235" height="110" fill="#f0fdf4" stroke="#86efac"/>')
    svg.append(f'  <text class="hdr" x="552" y="137">4. Цифровий компаратор</text>')
    svg.append(f'  <text class="code" x="552" y="160">(Target &amp; MASK) == (Read &amp; MASK)</text>')
    svg.append(f'  <text class="code" x="552" y="180">(0x34 &amp; 0x7F) == (0xB4 &amp; 0x7F)</text>')
    svg.append(f'  <text class="code" x="552" y="202" fill="#16a34a" font-weight="700">0x34 == 0x34  [MATCH!]</text>')

    # Стрілки
    svg.append(f'  <line class="flow-arrow" x1="244" y1="{y_step1 + 45}" x2="280" y2="{y_step1 + 45}"/>')
    svg.append(f'  <line class="flow-arrow" x1="390" y1="{y_step1 + 95}" x2="390" y2="{y_step2}"/>')
    svg.append(f'  <line class="flow-arrow" x1="500" y1="160" x2="540" y2="160"/>')

    # Розгалуження результату
    y_res = 295
    # Success branch
    svg.append(f'  <rect class="box-pane" x="540" y="{y_res}" width="110" height="60" fill="#dcfce7" stroke="#4ade80"/>')
    svg.append(f'  <text class="hdr" x="550" y="{y_res + 24}" fill="#15803d">УСПІХ (OK)</text>')
    svg.append(f'  <text class="label" x="550" y="{y_res + 44}">Наступний регістр</text>')

    # Mismatch branch
    svg.append(f'  <rect class="box-pane" x="665" y="{y_res}" width="110" height="60" fill="#fee2e2" stroke="#f87171"/>')
    svg.append(f'  <text class="hdr" x="675" y="{y_res + 24}" fill="#b91c1c">РОЗБІЖНІСТЬ</text>')
    svg.append(f'  <text class="label" x="675" y="{y_res + 44}">Retry / Bus Reset</text>')

    svg.append(f'  <line x1="595" y1="225" x2="595" y2="{y_res}" stroke="#16a34a" stroke-width="1.8" marker-end="url(#arrow-green)"/>')
    svg.append(f'  <line x1="720" y1="225" x2="720" y2="{y_res}" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arrow-red)"/>')

    # Текстова примітка знизу зліва
    svg.append('  <text class="label" x="24" y="320">Перевага: виявляє апаратні збої, коли лінія I2C/SPI відповіла ACK,</text>')
    svg.append('  <text class="label" x="24" y="340">але значення не збереглося у регістрі через просідання VDD чи захист.</text>')

    svg.append('</svg>')

    out_file = os.path.join(OUT_DIR, "readback-verification.svg")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Generated {out_file}")


if __name__ == "__main__":
    create_bringup_timeline()
    create_init_pipeline()
    create_readback_verification()
