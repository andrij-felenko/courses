# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. return-current-frequency: Шлях зворотного струму (DC vs High-Freq AC) ──
def fig_return_current_frequency():
    W, H = 900, 430
    p = []

    # Заголовок блоку DC (ліворуч)
    p.append(rect(30, 45, 400, 310, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(230, 75, "Низька частота (DC та f < 1 кГц)", size=14, color=INK, bold=True))
    p.append(text(230, 95, "Струм тече шляхом найменшого опору R", size=11.5, color=MUTED))

    # Джерело -> Навантаження
    p.append(circle(75, 150, 6, fill=POS, stroke=INK, sw=1.5))
    p.append(text(75, 133, "Джерело", size=11, color=POS, bold=True))

    p.append(circle(375, 230, 6, fill=NEG, stroke=INK, sw=1.5))
    p.append(text(375, 213, "Навантаження", size=11, color=NEG, bold=True))

    # Сигнальна доріжка
    p.append(line(75, 150, 205, 150, color=POS, sw=2.5))
    p.append(line(205, 150, 205, 230, color=POS, sw=2.5))
    p.append(arrow(205, 230, 369, 230, color=POS, sw=2.5))
    p.append(text(140, 140, "Сигнал (I_sig)", size=10.5, color=POS, bold=True))

    # Зворотний струм DC — пряма лінія по діагоналі
    p.append(line(375, 230, 75, 150, color=FIELD, sw=2.2, dash="5 4"))
    p.append(arrow(195, 182, 81, 152, color=FIELD, sw=2.2))
    p.append(text(245, 180, "Зворотний струм (шлях min R)", size=11, color=FIELD, bold=True))
    p.append(text(245, 198, "Розтікається по всій площині", size=10, color=MUTED))

    b1, _, _ = textbox(230, 310, "Опір R домінує над індуктивністю ωL.\nСтрум обирає найкоротшу геометричну пряму.",
                       size=11, fill="#ffffff", stroke=MUTED)
    p.append(b1)

    # Заголовок блоку High-Freq (праворуч)
    p.append(rect(470, 45, 400, 310, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(670, 75, "Висока частота (f > 100 кГц)", size=14, color=INK, bold=True))
    p.append(text(670, 95, "Струм тече шляхом найменшої індуктивності L", size=11.5, color=MUTED))

    p.append(circle(515, 150, 6, fill=POS, stroke=INK, sw=1.5))
    p.append(text(515, 133, "Джерело", size=11, color=POS, bold=True))

    p.append(circle(815, 230, 6, fill=NEG, stroke=INK, sw=1.5))
    p.append(text(815, 213, "Навантаження", size=11, color=NEG, bold=True))

    # Сигнальна доріжка
    p.append(line(515, 150, 645, 150, color=POS, sw=2.5))
    p.append(line(645, 150, 645, 230, color=POS, sw=2.5))
    p.append(arrow(645, 230, 809, 230, color=POS, sw=2.5))
    p.append(text(580, 140, "Сигнал (I_sig)", size=10.5, color=POS, bold=True))

    # Зворотний струм HF — строго дзеркально під доріжкою
    p.append(line(815, 230, 645, 230, color=FIELD, sw=2.5, dash="4 3"))
    p.append(line(645, 230, 645, 150, color=FIELD, sw=2.5, dash="4 3"))
    p.append(arrow(645, 150, 521, 150, color=FIELD, sw=2.5))
    p.append(text(730, 248, "Зворотний струм (min L)", size=11, color=FIELD, bold=True))
    p.append(text(575, 168, "Струм іде строго під трасою", size=10, color=FIELD))

    b2, _, _ = textbox(670, 310, "Індуктивність ωL >> R. Контур прагне\nмінімізувати площу петлі зворотного зв'язку.",
                       size=11, fill="#ffffff", stroke=MUTED)
    p.append(b2)

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, 390,
                          "На високих частотах (фронти перемикання цифри) зворотний струм локалізований безпосередньо під трасою.\n"
                          "Якщо не вести цифрову трасу над аналоговою зоною, цифровий зворотний струм туди ніколи не затече.",
                          size=11.5, stroke=FIELD, fill="#eefaf1")
    p.append(b_bot)

    render(os.path.join(OUT, "return-current-frequency.svg"), W, H, *p,
           title="Розподіл зворотного струму: залежність шляху від частоти")


# ── 2. split-plane-disaster: Катастрофа перетину розрізу землі ────────────────
def fig_split_plane_disaster():
    W, H = 900, 420
    p = []

    # Ліва половина (Аналог)
    p.append(rect(40, 55, 380, 280, fill="#f0f7ff", stroke=NEG, sw=2, rx=6))
    p.append(text(130, 85, "Аналогова земля (AGND)", size=13, color=NEG, bold=True))

    # Права половина (Цифра)
    p.append(rect(480, 55, 380, 280, fill="#fdf2f2", stroke=POS, sw=2, rx=6))
    p.append(text(770, 85, "Цифрова земля (DGND)", size=13, color=POS, bold=True))

    # Розріз (повітряний зазор між полігонами)
    p.append(rect(420, 55, 60, 220, fill="#ffffff", stroke=MUTED, sw=1))
    p.append(text(450, 160, "РОЗРІЗ", size=11, color=MUTED, bold=True))
    p.append(text(450, 178, "(SPLIT)", size=10, color=MUTED))

    # Місток/перемичка внизу
    p.append(rect(420, 275, 60, 60, fill="#e5e7eb", stroke=LINE, sw=1.5))
    p.append(text(450, 305, "Місток", size=10.5, color=INK, bold=True))
    p.append(text(450, 320, "(Star GND)", size=9.5, color=MUTED))

    # Цифровий передавач праворуч -> Аналоговий/змішаний приймач ліворуч
    p.append(circle(760, 130, 6, fill=POS, stroke=INK, sw=1.5))
    p.append(text(760, 115, "Цифровий вихід (МК)", size=11, color=POS, bold=True))

    p.append(circle(140, 130, 6, fill=NEG, stroke=INK, sw=1.5))
    p.append(text(140, 115, "АЦП (CS / CLK)", size=11, color=NEG, bold=True))

    # Сигнальна траса ПЕРЕТИНАЄ РОЗРІЗ напряму
    p.append(line(760, 130, 146, 130, color=POS, sw=3))
    p.append(arrow(210, 130, 146, 130, color=POS, sw=3))
    p.append(text(450, 118, "Цифрова траса перетинає розріз!", size=11, color=POS, bold=True))

    # Шлях зворотного струму — змушений оббігати весь розріз униз через місток!
    p.append(line(140, 130, 140, 300, color=FIELD, sw=2.5, dash="5 4"))
    p.append(line(140, 300, 760, 300, color=FIELD, sw=2.5, dash="5 4"))
    p.append(line(760, 300, 760, 130, color=FIELD, sw=2.5, dash="5 4"))
    p.append(arrow(440, 300, 470, 300, color=FIELD, sw=2.5))

    # Контур петлі
    p.append(line(150, 145, 750, 145, color=POS, sw=1.5, dash="4 4"))
    p.append(line(750, 145, 750, 285, color=POS, sw=1.5, dash="4 4"))
    p.append(line(750, 285, 150, 285, color=POS, sw=1.5, dash="4 4"))
    p.append(line(150, 285, 150, 145, color=POS, sw=1.5, dash="4 4"))
    p.append(text(450, 220, "ВЕЛИЧЕЗНА ПЕТЛЯ ЗВОРОТНОГО СТРУМУ", size=13, color=POS, bold=True))
    p.append(text(450, 240, "Працює як рамкова антена: випромінює шум (EMI)", size=11, color=POS))
    p.append(text(450, 258, "й наводить завади на аналогові кола в зоні AGND", size=11, color=POS))

    # Пояснювальний висновок унизу
    b_bot, _, _ = textbox(W / 2, 380,
                          "Шпарина в землі блокує зворотний струм високої частоти. Замість короткого шляху струм робить гігантську петлю,\n"
                          "створюючи паразитну індуктивність, електромагнітне випромінювання та отруюючи обидва домени.",
                          size=11.5, stroke=POS, fill="#fff5f5")
    p.append(b_bot)

    render(os.path.join(OUT, "split-plane-disaster.svg"), W, H, *p,
           title="Чому розрізи землі небезпечні: поява антеної петлі зворотного струму")


# ── 3. zoned-solid-plane: Суцільний полігон землі та правильне зонування ──────
def fig_zoned_solid_plane():
    W, H = 900, 430
    p = []

    # Єдиний суцільний полігон землі (Solid Ground Plane) на всю плату
    p.append(rect(30, 45, 840, 310, fill="#f8fafc", stroke=FIELD, sw=2.5, rx=8))
    p.append(text(200, 70, "ЄДИНИЙ СУЦІЛЬНИЙ ЗЕМЛЯНИЙ ПОЛІГОН (SOLID GROUND PLANE)", size=12, color=FIELD, bold=True))

    # Віртуальна межа зон (пунктир)
    p.append(line(310, 45, 310, 355, color=MUTED, sw=1.5, dash="6 4"))
    p.append(line(590, 45, 590, 355, color=MUTED, sw=1.5, dash="6 4"))

    # Зона 1: Чутливий аналог (ліворуч)
    p.append(text(170, 100, "Аналогова зона", size=14, color=NEG, bold=True))
    p.append(text(170, 120, "Давачі, ОП, ІП, чисті Vref", size=10.5, color=MUTED))
    p.append(rect(60, 140, 220, 140, fill="#edf5ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(170, 180, "Слабкі аналогові сигнали", size=11.5, color=NEG, bold=True))
    p.append(text(170, 205, "Тільки аналогові траси", size=10.5, color=INK))
    p.append(text(170, 225, "Зворотні струми низькі й чисті", size=10.5, color=FIELD))

    # Зона 2: Змішаний сигнал / АЦП (посередині)
    p.append(text(450, 100, "Змішана зона (АЦП / ЦАП)", size=14, color=INK, bold=True))
    p.append(text(450, 120, "Мікросхема АЦП на межі", size=10.5, color=MUTED))

    # Корпус АЦП на межі
    p.append(rect(365, 150, 170, 120, fill="#fdf6b2", stroke=LINE, sw=2, rx=6))
    p.append(text(450, 185, "АЦП / ЦАП", size=13, color=INK, bold=True))
    p.append(text(400, 215, "AGND", size=10.5, color=NEG, bold=True))
    p.append(text(500, 215, "DGND", size=10.5, color=POS, bold=True))
    p.append(text(450, 245, "Обидва виводи впаяні в", size=9.5, color=INK))
    p.append(text(450, 258, "єдину суцільну землю!", size=9.5, color=FIELD, bold=True))

    # Зона 3: Цифрова зона (праворуч)
    p.append(text(730, 100, "Цифрова зона", size=14, color=POS, bold=True))
    p.append(text(730, 120, "МК, DSP, Flash, DC-DC", size=10.5, color=MUTED))
    p.append(rect(620, 140, 220, 140, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(730, 180, "Мікроконтролер / ШИМ", size=11.5, color=POS, bold=True))
    p.append(text(730, 205, "Швидкі цифрові фронти di/dt", size=10.5, color=POS))
    p.append(text(730, 225, "Зворотний струм замкнений тут", size=10.5, color=FIELD))

    # Зв'язки трас
    p.append(arrow(280, 210, 360, 210, color=NEG, sw=2))
    p.append(text(320, 200, "Ain", size=10, color=NEG, bold=True))

    p.append(arrow(540, 210, 615, 210, color=POS, sw=2))
    p.append(text(575, 200, "SPI/I2C", size=10, color=POS, bold=True))

    # Висновок
    b_bot, _, _ = textbox(W / 2, 390,
                          "Суцільний шар міді дає найменший імпеданс. Просторове зонування гарантує:\n"
                          "цифрові зворотні струми залишаються у своїй третині плати й не перетинають чутливий аналог.",
                          size=11.5, stroke=FIELD, fill="#eefaf1")
    p.append(b_bot)

    render(os.path.join(OUT, "zoned-solid-plane.svg"), W, H, *p,
           title="Золотий стандарт mixed-signal: суцільний полігон землі та просторове зонування")


# ── 4. decoupling-loop-layout: Трасування блокувального конденсатора ───────────
def fig_decoupling_loop_layout():
    W, H = 900, 430
    p = []

    # Лівий блок: ПОГАНО
    p.append(rect(30, 45, 400, 310, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(230, 75, "ПОГАНО: Довгі відводи й велика індуктивність", size=13, color=POS, bold=True))

    # Нога мікросхеми (IC Pin)
    p.append(rect(60, 140, 80, 80, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(100, 175, "IC Pin", size=11.5, color=INK, bold=True))
    p.append(text(100, 192, "(VDD)", size=10, color=MUTED))

    # Конденсатор десь збоку (далеко)
    p.append(rect(280, 140, 80, 80, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(320, 175, "0.1 µF", size=11.5, color=INK, bold=True))
    p.append(text(320, 192, "MLCC", size=10, color=MUTED))

    # Довгі доріжки
    p.append(line(140, 180, 280, 180, color=POS, sw=2.5))
    p.append(text(210, 168, "довга доріжка", size=10, color=POS))

    # Перехідні отвори
    p.append(circle(320, 265, 10, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(320, 269, "GND", size=9.5, color=LINE))
    p.append(line(320, 220, 320, 255, color=LINE, sw=2))

    p.append(circle(100, 265, 10, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(100, 269, "GND", size=9.5, color=LINE))
    p.append(line(100, 220, 100, 255, color=LINE, sw=2))

    # Велика петля струму
    p.append(line(50, 130, 370, 130, color=POS, sw=1.2, dash="4 3"))
    p.append(line(370, 130, 370, 285, color=POS, sw=1.2, dash="4 3"))
    p.append(line(370, 285, 50, 285, color=POS, sw=1.2, dash="4 3"))
    p.append(line(50, 285, 50, 130, color=POS, sw=1.2, dash="4 3"))
    p.append(text(210, 222, "Велика паразитна петля ESL!", size=11, color=POS, bold=True))
    p.append(text(210, 240, "L_loop ≈ 5–10 нГн → шум проникає в чип", size=10, color=POS))

    b1, _, _ = textbox(230, 315, "Конденсатор не встигає віддати струм на ВЧ:\nіндуктивність відводів душить компенсацію di/dt.",
                       size=10.5, fill="#ffffff", stroke=MUTED)
    p.append(b1)

    # Правий блок: ДОБРЕ
    p.append(rect(470, 45, 400, 310, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(670, 75, "ДОБРЕ: Конденсатор впритул, via на майданчику", size=13, color=FIELD, bold=True))

    # Нога мікросхеми
    p.append(rect(500, 140, 80, 80, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(540, 175, "IC Pin", size=11.5, color=INK, bold=True))
    p.append(text(540, 192, "(VDD)", size=10, color=MUTED))

    # Конденсатор впритул до ноги
    p.append(rect(620, 140, 80, 80, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(660, 175, "0.1 µF", size=11.5, color=INK, bold=True))
    p.append(text(660, 192, "MLCC", size=10, color=MUTED))

    # Коротке з'єднання Pin -> C
    p.append(line(580, 180, 620, 180, color=FIELD, sw=4))
    p.append(text(600, 165, "впритул", size=9.5, color=FIELD, bold=True))

    # Перехідні отвори
    p.append(circle(660, 260, 10, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(660, 264, "GND", size=9.5, color=LINE))
    p.append(line(660, 220, 660, 250, color=FIELD, sw=3))

    p.append(circle(740, 180, 10, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(740, 184, "PWR", size=9.5, color=LINE))
    p.append(line(700, 180, 730, 180, color=FIELD, sw=3))

    # Мікроскопічна петля
    p.append(line(490, 130, 710, 130, color=FIELD, sw=1.2, dash="3 3"))
    p.append(line(710, 130, 710, 280, color=FIELD, sw=1.2, dash="3 3"))
    p.append(line(710, 280, 490, 280, color=FIELD, sw=1.2, dash="3 3"))
    p.append(line(490, 280, 490, 130, color=FIELD, sw=1.2, dash="3 3"))
    p.append(text(600, 235, "Мінімальна петля: L_loop < 1 нГн", size=10.5, color=FIELD, bold=True))

    b2, _, _ = textbox(670, 315, "Струм від VDD-шини йде СПЕРШУ крізь конденсатор,\nі лише потім потрапляє на вивід мікросхеми.",
                       size=10.5, fill="#ffffff", stroke=MUTED)
    p.append(b2)

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2, 390,
                          "Правило трасування розв'язки: «Живлення → Конденсатор → Ніжка чипа → Земляний перехідний отвір».\n"
                          "Кожен міліметр доріжки додає ~1 нГн індуктивності, що знецінює високочастотний керамічний конденсатор.",
                          size=11.5, stroke=FIELD, fill="#eefaf1")
    p.append(b_bot)

    render(os.path.join(OUT, "decoupling-loop-layout.svg"), W, H, *p,
           title="Трасування блокувальних конденсаторів: мінімізація індуктивності контуру")


# ── 5. guard-ring-shield: Охоронне кільце навколо високоімпедансного вузла ────
def fig_guard_ring_shield():
    W, H = 940, 430
    p = []

    # Плата текстоліту FR4 (фон)
    p.append(rect(30, 45, 880, 320, fill="#fdfcf7", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(text(140, 70, "Поверхня друкованої плати (FR4)", size=11, color=MUTED, italic=True))

    # Високоомний вхідний вузол по центру (High-Z node)
    p.append(circle(250, 200, 18, fill="#fee2e2", stroke=POS, sw=2))
    p.append(text(250, 205, "Vin", size=13, color=POS, bold=True))
    p.append(text(250, 160, "Високоімпедансний вхід (High-Z)", size=11, color=POS, bold=True))
    p.append(text(250, 240, "R_in > 10¹⁰ Ом (pH/фотодіод)", size=10, color=MUTED))

    # Охоронне кільце навколо (Guard Ring)
    p.append(circle(250, 200, 58, fill="none", stroke=FIELD, sw=6))
    p.append(text(250, 125, "Охоронне кільце (Guard Ring)", size=11.5, color=FIELD, bold=True))

    # Буферний підсилювач (повторювач)
    p.append('<polygon points="430,140 430,260 530,200" fill="#eef3fb" stroke="#333333" stroke-width="2"/>')
    p.append(text(455, 175, "+", size=16, color=POS, bold=True))
    p.append(text(455, 225, "−", size=16, color=NEG, bold=True))
    p.append(text(480, 205, "ОП", size=12, color=INK, bold=True))

    # З'єднання Vin з неінвертуючим входом (+)
    p.append(line(268, 200, 430, 170, color=POS, sw=2))

    # Вихід ОП (530, 200) -> зворотний зв'язок на (-) і на Guard Ring
    p.append(line(530, 200, 570, 200, color=FIELD, sw=2.5))
    p.append(line(570, 200, 570, 275, color=FIELD, sw=2))
    p.append(line(570, 275, 410, 275, color=FIELD, sw=2))
    p.append(line(410, 275, 410, 230, color=FIELD, sw=2))
    p.append(arrow(410, 230, 430, 230, color=FIELD, sw=2))

    # Відвід від виходу ОП на Guard Ring
    p.append(line(570, 200, 570, 95, color=FIELD, sw=2.5))
    p.append(line(570, 95, 308, 95, color=FIELD, sw=2.5))
    p.append(arrow(308, 95, 308, 145, color=FIELD, sw=2.5))
    p.append(text(440, 85, "Екрануючий потенціал V_guard = V_in", size=11, color=FIELD, bold=True))

    # Зовнішній брудний потенціал
    p.append(rect(60, 120, 70, 160, fill="#f3f4f6", stroke=MUTED, sw=1.5, rx=4))
    p.append(text(95, 175, "Сусідні\nшини\nVDD/GND", size=10.5, color=INK))

    # Струм витоку
    p.append(arrow(130, 180, 192, 180, color=POS, sw=1.8))
    p.append(text(160, 170, "I_витоку", size=10, color=POS))
    p.append(text(160, 200, "(перехоплено)", size=9, color=FIELD))

    # Блок формули праворуч
    b_formula, _, _ = textbox(740, 200,
                              "Різниця потенціалів:\n"
                              "ΔV = V_in − V_guard ≈ 0 В\n\n"
                              "Струм витоку на вхід:\n"
                              "I_leak = ΔV / R_поверхні = 0 А!",
                              size=11.5, fill="#ffffff", stroke=FIELD)
    p.append(b_formula)

    # Нижній загальний висновок
    b_bot, _, _ = textbox(W / 2, 390,
                          "Охоронне кільце знаходиться під тим самим потенціалом, що й вимірювальна лінія. Немає різниці напруг —\n"
                          "немає струму витоку крізь вологу, флюс та мікротріщини текстоліту у вхідний підсилювач.",
                          size=11.5, stroke=FIELD, fill="#eefaf1")
    p.append(b_bot)

    render(os.path.join(OUT, "guard-ring-shield.svg"), W, H, *p,
           title="Охоронне кільце з активним потенціалом: захист високоімпедансних входів")


if __name__ == "__main__":
    fig_return_current_frequency()
    fig_split_plane_disaster()
    fig_zoned_solid_plane()
    fig_decoupling_loop_layout()
    fig_guard_ring_shield()
    print("All figures generated successfully.")
