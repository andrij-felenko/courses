# -*- coding: utf-8 -*-
"""Фігури до теми «Прямий доступ до пам'яті (DMA)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F = "#eaf0fd"   # ядро (холодне)
GREEN_F = "#e7f6ee"  # DMA / добре
RED_F = "#fdecea"    # проблема / застаріле


# ── 1. Ядро-вантажник проти DMA: хто стоїть на шляху даних ────────────────────
def fig_copyloop_vs_dma():
    W, H = 880, 470
    f = []
    # роздільник
    f.append(line(440, 70, 440, 442, color="#dddddd", sw=1.5, dash="5,6"))

    # ── ЛІВО: ядро в потоці даних ──
    f.append(text(220, 52, "Ядро як вантажник", size=15, bold=True, color=POS))
    f.append(fitbox(140, 92, 160, 56, "буфер\nу ОЗП", size=13))
    f.append(fitbox(140, 200, 160, 60, "ЯДРО", size=16, fill=BLUE_F, stroke=NEG, sw=2, bold=True))
    f.append(fitbox(140, 322, 160, 60, "регістр даних\nпериферії", size=12.5))
    # потік знизу вгору крізь ядро
    f.append(arrow(220, 320, 220, 262, color=INK, sw=2))
    f.append(arrow(220, 198, 220, 150, color=INK, sw=2))
    # підписи кроків праворуч від ланцюга
    f.append(text(312, 300, "① читай регістр", size=11, anchor="start", color=INK))
    f.append(text(312, 178, "② пиши в ОЗП", size=11, anchor="start", color=INK))
    f.append(text(312, 232, "③ лічи, повтори", size=11, anchor="start", color=MUTED))
    f.append(text(220, 420, "ядро зайняте на кожен байт —", size=11.5, color=POS))
    f.append(text(220, 437, "справжні обчислення стоять", size=11.5, color=POS))

    # ── ПРАВО: DMA у потоці, ядро осторонь ──
    f.append(text(680, 52, "Той самий потік із DMA", size=15, bold=True, color=FIELD))
    f.append(fitbox(610, 92, 150, 56, "буфер\nу ОЗП", size=13))
    f.append(fitbox(610, 210, 150, 58, "DMA", size=16, fill=GREEN_F, stroke=FIELD, sw=2, bold=True))
    f.append(fitbox(610, 322, 150, 58, "регістр\nпериферії", size=12.5))
    # прямий потік периферія → DMA → ОЗП
    f.append(arrow(685, 320, 685, 270, color=FIELD, sw=2.2))
    f.append(arrow(685, 208, 685, 150, color=FIELD, sw=2.2))
    # ядро осторонь, поза шляхом даних
    f.append(fitbox(468, 96, 104, 56, "ядро\nрахує", size=12.5, fill=BLUE_F, stroke=NEG, sw=1.8, bold=True))
    # тонкий пунктир «готово» від DMA до ядра
    f.append(line(608, 232, 566, 150, color=NEG, sw=1.4, dash="4,4"))
    f.append(text(556, 214, "1 IRQ", size=10, anchor="start", color=NEG, bold=True))
    f.append(text(556, 228, "на блок", size=10, anchor="start", color=NEG))
    f.append(text(680, 420, "ядро не торкається даних —", size=11.5, color=FIELD))
    f.append(text(680, 437, "рахує або спить, поки DMA возить", size=11.5, color=FIELD))

    render(os.path.join(IMG, "copyloop-vs-dma.svg"), W, H, *f)


# ── 2. Рукостискання запит–підтвердження й лічильник ──────────────────────────
def fig_handshake():
    W, H = 880, 430
    f = []
    f.append(text(W / 2, 32, "Один елемент за «запитом»: рукостискання й лічильник",
                  size=16, bold=True))

    # ядро зверху
    f.append(fitbox(365, 52, 150, 46, "ЯДРО", size=14, fill=BLUE_F, stroke=NEG, sw=2, bold=True))
    # периферія ліворуч
    f.append(fitbox(40, 150, 150, 96, "Периферія\n(напр. АЦП)\nрегістр даних", size=12, stroke=MUTED))
    # ОЗП праворуч
    f.append(fitbox(690, 150, 150, 96, "ОЗП\nбуфер", size=13))
    # контролер DMA у центрі з трьома регістрами
    f.append(rect(330, 130, 220, 150, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(text(440, 150, "Контролер DMA", size=13, bold=True, color=FIELD))
    f.append(fitbox(345, 162, 190, 30, "src → адреса джерела", size=11, fill=BG, stroke=MUTED, sw=1.2))
    f.append(fitbox(345, 197, 190, 30, "dst → адреса приймача", size=11, fill=BG, stroke=MUTED, sw=1.2))
    f.append(fitbox(345, 232, 190, 30, "count → скільки лишилось", size=11, fill=BG, stroke=MUTED, sw=1.2))

    # ① запит: периферія → DMA (угорі)
    f.append(arrow(192, 178, 328, 178, color=POS, sw=2))
    f.append(text(260, 170, "① запит: новий байт", size=11, color=POS))
    # ② DMA читає регістр периферії (нижче, назад)
    f.append(arrow(328, 214, 194, 214, color=INK, sw=1.8))
    f.append(text(262, 232, "② DMA читає регістр", size=11, color=INK))
    # ③ DMA пише в ОЗП
    f.append(arrow(552, 195, 688, 195, color=INK, sw=1.8))
    f.append(text(620, 187, "③ пише в ОЗП", size=11, color=INK))
    # ④ лічильник
    f.append(text(440, 300, "④ dst += ширина, count −= 1, запит знято", size=10.5, color=MUTED))
    # ⑤ IRQ до ядра, коли count = 0
    f.append(arrow(440, 128, 440, 100, color=NEG, sw=2))
    f.append(text(452, 118, "⑤ count = 0 → IRQ «готово»", size=11, anchor="start", color=NEG))

    # підсумкова смуга
    f.append(rect(80, 330, 720, 74, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    f.append(text(W / 2, 356, "Поки count > 0, DMA чекає наступного запиту й возить рівно один елемент — ядро не бере участі.",
                  size=12, color=INK))
    f.append(text(W / 2, 380, "Переривання приходить раз на весь блок, а не на кожен байт.",
                  size=12, color=INK, bold=True))

    render(os.path.join(IMG, "handshake.svg"), W, H, *f)


# ── 3. Спільна шина (крадіжка циклів) vs матриця шин (паралельні шляхи) ────────
def fig_arbitration():
    W, H = 900, 410
    f = []
    f.append(line(452, 70, 452, 372, color="#dddddd", sw=1.5, dash="5,6"))

    # ── ЛІВО: одна шина, крадіжка циклів ──
    f.append(text(230, 56, "Одна шина: по черзі", size=14, bold=True, color=POS))
    f.append(text(230, 128, "цикли шини в часі →", size=11, color=MUTED))
    x0, y0, sw_, sh, gap = 44, 150, 26, 36, 4
    owners = ["C", "C", "C", "D", "C", "C", "C", "C", "D", "C", "C", "C"]
    for i, o in enumerate(owners):
        x = x0 + i * (sw_ + gap)
        if o == "D":
            f.append(rect(x, y0, sw_, sh, fill=RED_F, stroke=POS, sw=1.6))
            f.append(text(x + sw_ / 2, y0 + sh + 16, "DMA", size=9, color=POS, bold=True))
        else:
            f.append(rect(x, y0, sw_, sh, fill=BLUE_F, stroke=NEG, sw=1.2))
    # легенда
    f.append(rect(60, 236, 16, 16, fill=BLUE_F, stroke=NEG, sw=1.2))
    f.append(text(84, 249, "ядро", size=11, anchor="start", color=INK))
    f.append(rect(150, 236, 16, 16, fill=RED_F, stroke=POS, sw=1.4))
    f.append(text(174, 249, "DMA вкрав цикл", size=11, anchor="start", color=INK))
    f.append(text(230, 300, "DMA бере цикл лише коли має що возити;", size=11, color=INK))
    f.append(text(230, 318, "ядро гальмує тільки в разі збігу тієї ж миті.", size=11, color=INK))

    # ── ПРАВО: матриця шин ──
    f.append(text(676, 56, "Матриця шин: паралельні шляхи", size=14, bold=True, color=FIELD))
    f.append(fitbox(490, 108, 108, 50, "ядро", size=13, fill=BLUE_F, stroke=NEG, sw=1.8, bold=True))
    f.append(fitbox(490, 250, 108, 50, "DMA", size=13, fill=GREEN_F, stroke=FIELD, sw=1.8, bold=True))
    f.append(rect(650, 120, 66, 190, fill="#f4f6f8", stroke=LINE, sw=1.5))
    f.append(text(683, 114, "матриця", size=10, color=MUTED))
    f.append(fitbox(760, 108, 116, 50, "Flash\n(код)", size=12))
    f.append(fitbox(760, 250, 116, 50, "SRAM +\nпериферія", size=12))
    # непересічні шляхи
    f.append(line(598, 133, 650, 133, color=NEG, sw=2.4))
    f.append(line(716, 133, 760, 133, color=NEG, sw=2.4))
    f.append(line(598, 275, 650, 275, color=FIELD, sw=2.4))
    f.append(line(716, 275, 760, 275, color=FIELD, sw=2.4))
    f.append(text(676, 340, "ядро читає код із Flash, а DMA возить SRAM↔периферія —", size=10.5, color=INK))
    f.append(text(676, 357, "водночас, різними шляхами, без черги.", size=10.5, color=INK))

    render(os.path.join(IMG, "arbitration.svg"), W, H, *f)


# ── 4. Кільцевий режим і пінг-понг для безперервного потоку ───────────────────
def fig_circular_pingpong():
    W, H = 900, 430
    f = []
    f.append(line(450, 70, 450, 392, color="#dddddd", sw=1.5, dash="5,6"))

    # ── ЛІВО: кільцевий буфер ──
    f.append(text(220, 54, "Кільцевий режим: буфер без кінця", size=13.5, bold=True, color=FIELD))
    cx, cy, r = 220, 232, 92
    f.append(circle(cx, cy, r, fill=BG, stroke=LINE, sw=2))
    f.append(line(cx - r, cy, cx + r, cy, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(cx, cy - 40, "половина A", size=12, color=INK))
    f.append(text(cx, cy + 48, "половина B", size=12, color=INK))
    # позначки переривань
    f.append(circle(cx, cy - r, 4.5, fill=NEG, stroke=NEG))
    f.append(text(cx, cy - r - 12, "повний → IRQ + обгортка", size=10, color=NEG))
    f.append(circle(cx, cy + r, 4.5, fill=NEG, stroke=NEG))
    f.append(text(cx, cy + r + 22, "половина → IRQ", size=10, color=NEG))
    # покажчик DMA
    f.append(circle(cx + r, cy, 5, fill=FIELD, stroke=FIELD))
    f.append(text(cx + r + 12, cy + 4, "DMA пише", size=10, anchor="start", color=FIELD, bold=True))
    f.append(text(220, 360, "дійшовши кінця — DMA сам вертається на початок", size=10.5, color=MUTED))

    # ── ПРАВО: пінг-понг ──
    f.append(text(680, 54, "Пінг-понг: возять і читають нарізно", size=13.5, bold=True, color=NEG))
    f.append(fitbox(580, 120, 200, 64, "половина A\nядро читає (готова)", size=12, fill=BLUE_F, stroke=NEG, sw=1.8))
    f.append(text(680, 210, "⇅  міняються ролями", size=11, color=MUTED))
    f.append(fitbox(580, 232, 200, 64, "половина B\nDMA наповнює", size=12, fill=GREEN_F, stroke=FIELD, sw=1.8))
    f.append(text(680, 340, "поки DMA наповнює одну половину,", size=10.5, color=INK))
    f.append(text(680, 357, "ядро спокійно читає іншу — потік без розривів.", size=10.5, color=INK))

    render(os.path.join(IMG, "circular-pingpong.svg"), W, H, *f)


# ── 5. Пастка когерентності кешу: дві версії однієї пам'яті ───────────────────
def fig_cache_trap():
    W, H = 900, 450
    f = []
    f.append(line(452, 70, 452, 388, color="#dddddd", sw=1.5, dash="5,6"))

    # ── ЛІВО: приймання (DMA пише в ОЗП) ──
    f.append(text(228, 54, "Приймання: DMA пише в ОЗП", size=13, bold=True, color=POS))
    f.append(fitbox(60, 108, 150, 48, "ядро", size=13, fill=BLUE_F, stroke=NEG, sw=1.8, bold=True))
    f.append(fitbox(60, 198, 150, 56, "кеш даних\n[старе]", size=12, fill=RED_F, stroke=POS, sw=2))
    f.append(fitbox(300, 198, 140, 56, "ОЗП\n[нове]", size=12, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(line(135, 156, 135, 198, color=NEG, sw=1.6))
    f.append(text(145, 182, "читає", size=9, anchor="start", color=NEG))
    # DMA пише свіже в ОЗП
    f.append(arrow(370, 300, 370, 256, color=FIELD, sw=2))
    f.append(text(370, 316, "DMA пише свіже", size=10, color=FIELD))
    # неузгодженість
    f.append(line(212, 226, 298, 226, color=POS, sw=1.4, dash="5,4"))
    f.append(text(255, 218, "≠", size=17, color=POS, bold=True))
    f.append(text(228, 356, "ядро читає старе → лік: інвалідувати кеш", size=11, color=FIELD, bold=True))

    # ── ПРАВО: передавання (DMA читає з ОЗП) ──
    f.append(text(676, 54, "Передавання: DMA читає з ОЗП", size=13, bold=True, color=POS))
    f.append(fitbox(510, 108, 150, 48, "ядро пише", size=13, fill=BLUE_F, stroke=NEG, sw=1.8, bold=True))
    f.append(fitbox(510, 198, 150, 56, "кеш даних\n[нове, брудне]", size=11.5, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(fitbox(752, 198, 138, 56, "ОЗП\n[старе]", size=12, fill=RED_F, stroke=POS, sw=2))
    f.append(line(585, 156, 585, 198, color=NEG, sw=1.6))
    f.append(text(595, 182, "пише", size=9, anchor="start", color=NEG))
    # DMA читає старе з ОЗП
    f.append(arrow(821, 300, 821, 256, color=POS, sw=2))
    f.append(text(821, 316, "DMA шле старе", size=10, color=POS))
    f.append(line(662, 226, 750, 226, color=POS, sw=1.4, dash="5,4"))
    f.append(text(706, 218, "≠", size=17, color=POS, bold=True))
    f.append(text(676, 356, "DMA бере старе → лік: очистити (flush) кеш", size=11, color=FIELD, bold=True))

    f.append(text(W / 2, 420,
                  "На ядрах із кешем даних (напр. Cortex-M7) ОЗП і кеш — дві версії однієї пам'яті; DMA бачить лише ОЗП.",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "cache-trap.svg"), W, H, *f)


# ── 6. (вставка proj-setup) Порядок налаштування каналу й два замки ───────────
def fig_setup_order():
    W, H = 940, 600
    f = []
    f.append(text(W / 2, 32, "Налаштування каналу: анкета ліворуч, два замки на трубі праворуч",
                  size=16, bold=True))
    f.append(line(501, 58, 501, 515, color="#dddddd", sw=1.5, dash="5,6"))

    # ── ЛІВО: впорядкована анкета ──
    f.append(text(253, 76, "Бік DMA: заповнити й звести", size=13, bold=True, color=NEG))
    steps = [
        ("① такт: RCC->AHBENR |= RCC_AHBENR_DMA1EN", False),
        ("② погасити канал: CCR.EN = 0", False),
        ("③ стерти прапорці: DMA1->IFCR = CGIF1", False),
        ("④ CPAR = (uint32_t)&ADC1->DR — АДРЕСА регістра", False),
        ("⑤ CMAR = (uint32_t)adc_buf — адреса буфера", False),
        ("⑥ CNDTR = 1024 — елементів, не байтів", False),
        ("⑦ CCR = напрямок · інкременти · ширини · кільце", False),
        ("⑧ CCR.EN = 1 — ЗАМОК 1 відкрито", True),
    ]
    y = 92
    for s, hot in steps:
        f.append(fitbox(44, y, 418, 38, s, size=12,
                        fill=GREEN_F if hot else FILL,
                        stroke=FIELD if hot else LINE, sw=2 if hot else 1.4))
        y += 46
    f.append(fitbox(44, 468, 418, 46,
                    "поки EN = 1, записи в CPAR / CMAR / CNDTR\nконтролер просто ігнорує",
                    size=11, fill=BG, stroke=MUTED, sw=1.2))

    # ── ПРАВО: шлях даних із двома кранами ──
    f.append(text(710, 76, "Шлях даних і два замки на ньому", size=13, bold=True, color=FIELD))
    chain = [
        (110, 44, "АЦП: новий відлік у ADC1->DR", False),
        (172, 52, "ЗАМОК 2 · ADC1->CR2 |= ADC_CR2_DMA\nдозвіл піднімати запит", True),
        (242, 52, "канал DMA1_Channel1\nCPAR · CMAR · CNDTR · CCR", False),
        (312, 52, "ЗАМОК 1 · CCR.EN = 1\nканал зведено", True),
        (382, 44, "буфер adc_buf[1024] у ОЗП", False),
    ]
    for yy, hh, s, hot in chain:
        f.append(fitbox(540, yy, 340, hh, s, size=12,
                        fill=GREEN_F if hot else FILL,
                        stroke=FIELD if hot else LINE, sw=2 if hot else 1.4))
    for y1, y2 in ((154, 170), (224, 240), (294, 310), (364, 380)):
        f.append(arrow(710, y1, 710, y2, color=FIELD, sw=2))
    f.append(fitbox(540, 468, 340, 46,
                    "номер каналу задає кремній:\nADC1 просить лише DMA1_Channel1",
                    size=11, fill=BG, stroke=MUTED, sw=1.2))

    f.append(fitbox(40, 530, 860, 52,
                    "Закритий будь-який із двох замків — і в буфері назавжди лишиться нуль: канал мовчить і ні на що не скаржиться.",
                    size=13, fill="#fbfcfd", stroke=MUTED, sw=1.2))
    render(os.path.join(IMG, "setup-order.svg"), W, H, *f)


# ── 7. (вставка proj-setup) CNDTR як діагностика каналу ───────────────────────
def fig_debug_cndtr():
    W, H = 980, 520
    f = []
    f.append(text(W / 2, 30, "Канал мовчить? CNDTR показує, де саме обрив", size=16, bold=True))
    f.append(fitbox(340, 52, 300, 44, "прочитай CNDTR двічі з паузою", size=13,
                    fill=BLUE_F, stroke=NEG, sw=2))
    f.append(line(490, 96, 490, 128, color=LINE, sw=1.6))
    f.append(line(165, 128, 815, 128, color=LINE, sw=1.6))

    cols = [
        (20, "не змінюється зовсім", POS, "запит не доходить до каналу",
         ["• не той канал: запит живе",
          "   лише на своєму номері",
          "• не піднято дозвіл DMA",
          "   у самій периферії",
          "• периферію не запущено",
          "• нема такту DMA у RCC"]),
        (345, "зменшився раз і став", MUTED, "лічильник дійшов нуля",
         ["• звичайний режим без CIRC —",
          "   так і має бути: вимкни канал,",
          "   перезаряди CNDTR, увімкни",
          "• або злетів TEIF: адреса поза",
          "   мапою чи буфер у пам'яті,",
          "   недосяжній для контролера"]),
        (670, "біжить, а дані не ті", NEG, "возить не те й не туди",
         ["• PSIZE / MSIZE не збігаються",
          "   з реальною шириною даних",
          "• MINC / PINC переплутано",
          "• кеш або брак volatile",
          "• ядро не встигло за півбуфером",
          "   і читає вже перезаписане"]),
    ]
    for x, sym, col, mean, items in cols:
        cx = x + 145
        f.append(arrow(cx, 128, cx, 148, color=LINE, sw=1.6))
        f.append(fitbox(x, 150, 290, 42, sym, size=13, bold=True, color=col,
                        fill=BG, stroke=col, sw=2))
        f.append(arrow(cx, 192, cx, 212, color=LINE, sw=1.6))
        f.append(fitbox(x, 214, 290, 40, mean, size=12, fill=FILL, stroke=MUTED, sw=1.3))
        f.append(arrow(cx, 254, cx, 274, color=LINE, sw=1.6))
        f.append(rect(x, 276, 290, 172, fill=BG, stroke=MUTED, sw=1.3))
        f.append(mtext(x + 14, 300, items, size=11, color=INK, anchor="start", lh=1.35))

    f.append(fitbox(40, 462, 900, 46,
                    "CNDTR читається на ходу й рахує, скільки елементів ЛИШИЛОСЬ — це найдешевший осцилограф каналу.",
                    size=13, fill="#fbfcfd", stroke=MUTED, sw=1.2))
    render(os.path.join(IMG, "debug-cndtr.svg"), W, H, *f)


# ── (вставка hist-birth) Хронологія ідеї прямого доступу ──────────────────────
def fig_hist_timeline():
    W, H = 960, 552
    f = []
    f.append(text(W / 2, 36, "Як визрівала думка «хай пристрій сам іде в пам'ять»",
                  size=16, bold=True))
    f.append(text(W / 2, 58, "роки — за першою поставкою або оголошенням машини", size=10.5, color=MUTED))
    f.append(line(150, 76, 150, 524, color="#cccccc", sw=1.6, dash="5,6"))

    rows = [
        ("1951", "UNIVAC I — буфер вводу-виводу",
         "стрічка говорить із буфером, але блок у пам'ять усе одно переносить обчислювач", False),
        ("1954", "DYSEAC (NBS) і SAGE (IBM) — прямий доступ",
         "пристрій уперше йде в пам'ять сам; чия першість — сперечаються досі", True),
        ("1957", "IBM 709 — «синхронізатор даних» 766",
         "канал стає окремим виконавцем власної програми вводу-виводу", False),
        ("1964", "IBM System/360 і CDC 6600",
         "канали з програмами команд; у Крея — десять повноцінних периферійних процесорів", False),
        ("1965", "DEC PDP-8 «data break», IBM 1130 «cycle steal»",
         "прямий доступ приходить у дешеві міні-машини — і дістає власну назву від кожного виробника", False),
        ("1979", "Intel 8237 і Intel 8089",
         "дві філософії поруч: тупий лічильник-возій і канал-співпроцесор із власними командами", False),
        ("1981", "IBM PC — один 8237A-5 на платі",
         "канал 0 витрачено не на дані, а на оновлення динамічної пам'яті", False),
        ("1982", "Intel 80186 — DMA переїжджає на кристал",
         "контролер, таймери й переривання в одному корпусі: форма сучасного мікроконтролера", False),
    ]
    y = 100
    for year, name, desc, big in rows:
        f.append(text(132, y + 4, year, size=13, anchor="end", bold=True, color=POS if big else NEG))
        f.append(circle(150, y, 7 if big else 5,
                        fill=RED_F if big else GREEN_F,
                        stroke=POS if big else FIELD, sw=2 if big else 1.6))
        f.append(text(176, y, name, size=12.5, anchor="start", bold=True, color=INK))
        f.append(text(176, y + 19, desc, size=11, anchor="start", color=MUTED))
        y += 58

    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


# ── (вставка hist-birth) Три відповіді: де живуть адреса й лічильник ──────────
def fig_hist_three_owners():
    W, H = 960, 432
    f = []
    f.append(text(W / 2, 36, "Де живе розум возія: три відповіді, і всі три дожили до нас",
                  size=16, bold=True))
    f.append(line(320, 60, 320, 378, color="#dddddd", sw=1.5, dash="5,6"))
    f.append(line(640, 60, 640, 378, color="#dddddd", sw=1.5, dash="5,6"))

    # ── ЛІВО: адреса й лічильник веде сам процесор ──
    f.append(text(160, 78, "У процесорі", size=13.5, bold=True, color=NEG))
    f.append(text(160, 96, "DEC PDP-8, трициклова «data break», 1965", size=10.5, color=MUTED))
    f.append(fitbox(35, 110, 250, 44, "пристрій\nлише піднімає запит", size=11.5))
    f.append(arrow(160, 154, 160, 182, color=INK, sw=1.8))
    f.append(fitbox(35, 184, 250, 52, "ПРОЦЕСОР\nадреса й лічильник — у комірках пам'яті",
                    size=11, fill=BLUE_F, stroke=NEG, sw=2))
    f.append(arrow(160, 236, 160, 264, color=INK, sw=1.8))
    f.append(fitbox(35, 266, 250, 40, "пам'ять", size=12.5))
    f.append(text(160, 336, "три такти пам'яті на одне слово", size=10.5, color=INK))
    f.append(text(160, 354, "пристрій дешевий, смуга шини дорога", size=10.5, color=MUTED))

    # ── ЦЕНТР: окремий спільний контролер ──
    f.append(text(480, 78, "В окремому контролері", size=13.5, bold=True, color=FIELD))
    f.append(text(480, 96, "Intel 8237 (1979) і DMA сучасного МК", size=10.5, color=MUTED))
    f.append(fitbox(355, 110, 250, 44, "пристрій\nпіднімає запит", size=11.5))
    f.append(arrow(480, 154, 480, 182, color=INK, sw=1.8))
    f.append(fitbox(355, 184, 250, 52, "КОНТРОЛЕР DMA\nканали: src · dst · count",
                    size=11, fill=GREEN_F, stroke=FIELD, sw=2))
    f.append(arrow(480, 236, 480, 264, color=INK, sw=1.8))
    f.append(fitbox(355, 266, 250, 40, "пам'ять", size=12.5))
    f.append(text(480, 336, "один такт пам'яті на слово", size=10.5, color=INK))
    f.append(text(480, 354, "один блок обслуговує всі пристрої", size=10.5, color=MUTED))

    # ── ПРАВО: сам пристрій — ведучий на шині ──
    f.append(text(800, 78, "У самому пристрої", size=13.5, bold=True, color=POS))
    f.append(text(800, 96, "SAGE, а згодом PCI та PCIe: bus mastering", size=10.5, color=MUTED))
    f.append(fitbox(675, 110, 250, 52, "ПРИСТРІЙ — сам ведучий\nсвої адреса й лічильник",
                    size=11, fill=RED_F, stroke=POS, sw=2))
    f.append(arrow(800, 162, 800, 264, color=POS, sw=2))
    f.append(text(788, 212, "без посередника", size=10.5, anchor="end", color=MUTED))
    f.append(fitbox(675, 266, 250, 40, "пам'ять", size=12.5))
    f.append(text(800, 336, "пристрій сам ходить шиною", size=10.5, color=INK))
    f.append(text(800, 354, "найшвидше — і найнебезпечніше", size=10.5, color=MUTED))

    f.append(text(W / 2, 404,
                  "У сучасному довіднику ці три відповіді звуться «DMA request», «DMA controller» і «bus master».",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "hist-three-owners.svg"), W, H, *f)


# ══ (вставка math-budget) Бюджет циклів шини ══════════════════════════════════

def _poly(pts, color=INK, sw=2.2):
    """Ламана з окремих відрізків (у svgkit є лише line)."""
    return "".join(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                        color=color, sw=sw) for i in range(len(pts) - 1))


# ── 10. Ціна одного елемента: два доступи, і вони нерівні ─────────────────────
def fig_budget_cost():
    W, H = 900, 400
    f = []
    f.append(text(W / 2, 36, "Ціна одного елемента: два доступи, і вони нерівні",
                  size=16, bold=True))

    CW, CH = 32, 34          # клітинка = один такт шини
    BX = 330                 # ліва межа смуг
    LX = 664                 # спільна колонка правих підписів
    rows = [
        (112, "периферія за мостом (APB = f/4)", 8, 9),
        (182, "периферія за мостом (APB = f/2)", 4, 5),
        (252, "периферія просто на швидкій шині", 1, 2),
    ]
    for y, name, npr, total in rows:
        f.append(text(30, y + CH / 2 + 5, name, size=12.5, anchor="start", color=INK))
        for i in range(npr):                      # доступи до регістра периферії
            f.append(rect(BX + i * CW, y, CW - 3, CH, fill=RED_F, stroke=POS, sw=1.5, rx=4))
        f.append(rect(BX + npr * CW, y, CW - 3, CH, fill=BLUE_F, stroke=NEG, sw=1.5, rx=4))
        endx = BX + (npr + 1) * CW - 3
        f.append(line(endx + 12, y + CH / 2, LX - 12, y + CH / 2,
                      color="#cfcfcf", sw=1, dash="3,4"))
        word = "такти" if total in (2, 3, 4) else "тактів"
        f.append(text(LX, y + 12, "Cₑ = %d %s" % (total, word), size=12.5,
                      anchor="start", color=INK, bold=True))
        f.append(text(LX, y + 31, "ρ = %d %%" % total, size=12, anchor="start", color=MUTED))

    # легенда
    f.append(rect(330, 310, 20, 20, fill=RED_F, stroke=POS, sw=1.5, rx=4))
    f.append(text(360, 325, "доступ до регістра периферії", size=11.5, anchor="start", color=INK))
    f.append(rect(330, 344, 20, 20, fill=BLUE_F, stroke=NEG, sw=1.5, rx=4))
    f.append(text(360, 359, "доступ до SRAM — один такт", size=11.5, anchor="start", color=INK))

    f.append(text(30, 325, "той самий обсяг даних —", size=11.5, anchor="start", color=MUTED))
    f.append(text(30, 345, "ціна від 2 до 9 тактів", size=11.5, anchor="start", color=MUTED))
    f.append(text(664, 325, "ρ — за темпу 1 МГц", size=11, anchor="start", color=MUTED))
    f.append(text(664, 345, "і шини 100 МГц", size=11, anchor="start", color=MUTED))

    render(os.path.join(IMG, "budget-cost.svg"), W, H, *f)


# ── 11. Сповільнення ядра  T/N = 1 + α·ρ/(1−ρ) ────────────────────────────────
def fig_budget_slowdown():
    W, H = 880, 470
    X0, X1 = 118, 672
    YB, YT = 372, 84
    RMAX, VMAX = 0.7, 3.5

    def px(r):
        return X0 + r / RMAX * (X1 - X0)

    def py(v):
        return YB - (v - 1.0) / (VMAX - 1.0) * (YB - YT)

    f = []
    f.append(text(W / 2, 36, "Скільки коштує ядру крадіжка циклів", size=16, bold=True))
    f.append(text(X0 - 6, YT - 22, "сповільнення ядра  T / N", size=12,
                  anchor="start", color=MUTED))

    # позначки по осі T/N (без сітки — щоб лінії не лізли на підписи)
    for v in (1.5, 2.0, 2.5, 3.0, 3.5):
        f.append(line(X0 - 6, py(v), X0, py(v), color=MUTED, sw=1.2))
        f.append(text(X0 - 12, py(v) + 4, "%.1f" % v, size=11, anchor="end", color=MUTED))
    f.append(text(X0 - 12, py(1.0) + 4, "1.0", size=11, anchor="end", color=MUTED))

    # осі
    f.append(line(X0, YT, X0, YB, color=INK, sw=1.6))
    f.append(line(X0, YB, X1, YB, color=INK, sw=1.6))
    for k in range(0, 8):
        f.append(text(px(k / 10.0), YB + 21, "%.1f" % (k / 10.0), size=11, color=MUTED))
    f.append(text((X0 + X1) / 2, YB + 46, "зайнятість шини  ρ", size=12.5, color=INK))

    # криві
    for a, col, lab in [(1.00, POS, "α = 1"), (0.50, INK, "α = 0.5"), (0.25, NEG, "α = 0.25")]:
        pts, r = [], 0.0
        while r <= RMAX + 1e-9:
            pts.append((px(r), py(min(1.0 + a * r / (1.0 - r), VMAX))))
            r += 0.01
        f.append(_poly(pts, color=col, sw=2.4))
        f.append(text(X1 + 14, py(min(1.0 + a * RMAX / (1 - RMAX), VMAX)) + 4,
                      lab, size=12, anchor="start", color=col, bold=True))
    f.append(line(X0, py(1.0), X1, py(1.0), color=FIELD, sw=2.4))
    f.append(text(X1 + 14, py(1.0) - 10, "α = 0", size=12, anchor="start", color=FIELD, bold=True))
    f.append(text(X1 + 14, py(1.0) + 10, "різні порти матриці", size=10, anchor="start", color=FIELD))

    # позначка з прикладу — у порожньому верхньому лівому куті поля
    mx, my = px(0.05), py(1.0 + 0.25 * 0.05 / 0.95)
    f.append(circle(mx, my, 4.5, fill=NEG, stroke=NEG))
    f.append(line(mx + 6, my - 6, 202, 190, color=MUTED, sw=1.1))
    f.append(text(150, 150, "АЦП: ρ = 5 %, α = 0.25", size=11.5, anchor="start",
                  color=NEG, bold=True))
    f.append(text(150, 170, "ядро втратило 1.3 % — учетверо менше за саму зайнятість",
                  size=11, anchor="start", color=MUTED))

    f.append(text(W / 2, YB + 78,
                  "α — частка тактів ядра, у яких воно просить ту саму магістраль",
                  size=11.5, color=MUTED))

    render(os.path.join(IMG, "budget-slowdown.svg"), W, H, *f)


# ── 12. Дедлайн: той самий час відгуку, два присуди ───────────────────────────
def fig_budget_deadline():
    W, H = 920, 440
    X0, SCALE = 112, 6.6      # x(такт) = X0 + такт·SCALE, шкала 0…110 тактів

    def x(c):
        return X0 + c * SCALE

    f = []
    f.append(text(W / 2, 36, "Переповнення — питання затримки, а не смуги", size=16, bold=True))

    def row(ytitle, ybar, title, tcol, dline, dcol, verdict, vcol):
        g = [text(X0, ytitle, title, size=13, anchor="start", color=tcol, bold=True)]
        # блокування чужим неподільним пакетом
        g.append(rect(x(0), ybar, x(23) - x(0), 32, fill=RED_F, stroke=POS, sw=1.6))
        g.append(text((x(0) + x(23)) / 2, ybar + 21, "чужий пакет — 23 такти", size=11, color=POS))
        # власне перенесення
        g.append(rect(x(23), ybar, x(28) - x(23), 32, fill=GREEN_F, stroke=FIELD, sw=1.6))
        g.append(line(x(25.5), ybar + 34, x(25.5), ybar + 48, color=FIELD, sw=1.2))
        g.append(text(x(25.5), ybar + 62, "своє: 5", size=10.5, color=FIELD, bold=True))
        # дедлайн
        g.append(line(x(dline), ybar - 24, x(dline), ybar + 44, color=dcol, sw=2, dash="6,4"))
        g.append(text(x(dline), ytitle + 24, "дедлайн %d" % dline, size=11.5, color=dcol, bold=True))
        # присуд
        g.append(text(x(28) + 52, ybar + 62, verdict, size=12, anchor="start", color=vcol, bold=True))
        return g

    f += row(94, 136, "АЦП 1 МГц: наступний відлік аж через 100 тактів", NEG,
             100, NEG, "устигає — до дедлайну ще 72 такти", FIELD)
    f += row(254, 296, "АЦП 5 МГц: наступний відлік уже через 20 тактів", POS,
             20, POS, "дедлайн минув посеред чужого пакета — відлік затерто", POS)

    f.append(line(60, 210, 860, 210, color="#e4e4e4", sw=1.2))

    f.append(text(W / 2, 396,
                  "Час відгуку той самий — 28 тактів; шина при цьому зайнята лише на третину.",
                  size=11.5, color=INK))
    f.append(text(W / 2, 418,
                  "Блокування B = 23 такти — це неподільний пакет на 16 слів у зовнішню SDRAM.",
                  size=11, color=MUTED))

    render(os.path.join(IMG, "budget-deadline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_copyloop_vs_dma()
    fig_handshake()
    fig_arbitration()
    fig_circular_pingpong()
    fig_cache_trap()
    fig_setup_order()
    fig_debug_cndtr()
    fig_hist_timeline()
    fig_hist_three_owners()
    fig_budget_cost()
    fig_budget_slowdown()
    fig_budget_deadline()
    print("OK: figures written to", IMG)
