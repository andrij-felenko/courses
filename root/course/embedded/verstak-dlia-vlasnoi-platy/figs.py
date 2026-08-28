# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. workbench-layout: Зонування та обладнання робочого місця ───────────────
def fig_workbench_layout():
    W, H = 900, 500
    p = []

    p.append(rect(15, 15, 870, 470, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(450, 42, "Архітектура та зонування робочого місця інженера (EPA)", size=15.5, color=INK, bold=True))

    # Ліва зона: Термічний блок
    p.append(rect(30, 65, 260, 400, fill="#ffffff", stroke="#dc2626", sw=1.2, rx=8))
    p.append(text(160, 90, "Термічний блок", size=13, color=POS, bold=True))
    
    p.append(fitbox(45, 105, 230, 75, "Картриджна станція\n(T12 / JBC C245 / C210)\nШвидкий нагрів (<3 с)\nПряма термопара у жалі", size=10.5, fill="#fef2f2", stroke=POS, sw=1.2))
    p.append(fitbox(45, 190, 230, 75, "Термоповітряний фен\nТурбіна або компресор\nКерування потоком і T°\nНасадки 4–10 мм + кутові", size=10.5, fill="#fff7ed", stroke="#ea580c", sw=1.2))
    p.append(fitbox(45, 275, 230, 75, "Нижній підігрів\nHot plate / ІЧ-плита\nПідтримка 100–140 °C\nЗняття градієнта плати", size=10.5, fill="#fefce8", stroke="#ca8a04", sw=1.2))
    p.append(fitbox(45, 360, 230, 90, "Витяжка диму\nФільтрація HEPA + вугілля\nВловлювання каніфольних\nаерозолів та активаторів", size=10, fill="#f1f5f9", stroke="#64748b", sw=1.0))

    # Центральна зона: Оптика та робоче поле
    p.append(rect(305, 65, 290, 400, fill="#ffffff", stroke="#2563eb", sw=1.5, rx=8))
    p.append(text(450, 90, "Зона монтажу та контролю", size=13, color=NEG, bold=True))

    p.append(fitbox(320, 105, 260, 105, "Бінокулярний мікроскоп\n(Greenough 7x–45x Zoom)\nЛінза Барроу 0.5x (WD 165 мм)\nLED-кільце з поляризатором\nЗахисне скло від диму", size=10.5, fill="#eff6ff", stroke=NEG, sw=1.2))
    p.append(fitbox(320, 220, 260, 115, "Робочий килимок та тримач\nТермостійкий силікон / гума\nФіксація багатошарових плат\nЗручний кут доступу\nТермопари зворотного зв'язку", size=10.5, fill="#f0fdf4", stroke=FIELD, sw=1.2))
    p.append(fitbox(320, 345, 260, 105, "Трафаретний вузол\nМеталевий трафарет (stencil)\nТовщина фольги 100–120 мкм\nРакель 45–60° + паяльна паста\nСуміщення по реперах", size=10, fill="#f8fafc", stroke="#64748b", sw=1.0))

    # Права зона: Інструменти та хімія
    p.append(rect(610, 65, 260, 400, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=8))
    p.append(text(740, 90, "Матеріали та інструмент", size=13, color=FIELD, bold=True))

    p.append(fitbox(625, 105, 230, 75, "Прецизійні пінцети\nФорми 5-SA, 7-SA (ESD-safe)\nТонкі немагнітні кінчики\nВакуумний маніпулятор", size=10.5, fill="#f8fafc", stroke="#64748b", sw=1.0))
    p.append(fitbox(625, 190, 230, 75, "Хімія монтажу\nФлюс ROL0 (no-clean) / RMA\nІзопропіловий спирт 99.8%\nБезворсові серветки", size=10.5, fill="#f8fafc", stroke="#64748b", sw=1.0))
    p.append(fitbox(625, 275, 230, 75, "Витратні матеріали\nМідне обплетення (wick)\nКаптоновий термоскотч\nАлюмінієва фольга-екран", size=10.5, fill="#f8fafc", stroke="#64748b", sw=1.0))
    p.append(fitbox(625, 360, 230, 90, "ESD-заземлення верстака\nШина з резистором 1 МОм\nАнтистатичний браслет\nЗахист чутливих польовиків", size=10, fill="#fef2f2", stroke=POS, sw=1.2))

    render(os.path.join(OUT, "workbench-layout.svg"), W, H, *p)


# ── 2. cartridge-vs-passive: Пасивне жало vs Інтегрований картридж ────────────
def fig_cartridge_vs_passive():
    W, H = 880, 440
    p = []

    p.append(rect(15, 15, 850, 410, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(440, 44, "Тепловий тракт: пасивне жало (Hakko 900M) vs картридж (T12 / JBC)", size=15.5, color=INK, bold=True))

    # Ліва колонка: Пасивна система
    p.append(rect(35, 65, 390, 345, fill="#ffffff", stroke="#dc2626", sw=1.3, rx=8))
    p.append(text(230, 92, "Пасивне жало (роздільна гільза)", size=13, color=POS, bold=True))

    p.append(rect(55, 110, 115, 34, fill="#fee2e2", stroke=POS, sw=1.2, rx=4))
    p.append(text(112, 131, "Нагрівач + сенсор", size=10, color=POS, bold=True))
    
    p.append(rect(180, 110, 80, 34, fill="#f1f5f9", stroke="#64748b", sw=1.0, rx=4))
    p.append(text(220, 131, "Зазор R_th", size=10, color="#64748b", bold=True))

    p.append(rect(270, 110, 135, 34, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=4))
    p.append(text(337, 131, "Знімне мідне жало", size=10, color="#ea580c", bold=True))

    p.append(arrow(170, 127, 180, 127, color=POS, sw=1.5))
    p.append(arrow(260, 127, 270, 127, color=POS, sw=1.5))

    p.append(fitbox(55, 155, 350, 110, "Тепловий бар'єр конструкції:\n• Термопара всередині керамічного стрижня\n• Сенсор «не бачить» падіння T° на кінчику\n• Повітряний прошарок додає термічний опір\n• Час реакції на відбір тепла: 5–15 секунд", size=10.5, fill="#fef2f2", stroke=POS, sw=1.0))

    p.append(fitbox(55, 275, 350, 120, "Наслідки на платі з полігонами:\n• Температурна яма (droop): просідання на 40–70 °C\n• Монтажник вимушено піднімає T° до 380–420 °C\n• Підсумок: швидке вигорання флюсу, окиснення,\n  перегрів клею та відшарування доріжок", size=10.5, fill="#fff1f2", stroke="#be123c", sw=1.2))

    # Права колонка: Картриджна система
    p.append(rect(455, 65, 390, 345, fill="#ffffff", stroke="#16a34a", sw=1.3, rx=8))
    p.append(text(650, 92, "Інтегрований картридж (T12 / JBC C245)", size=13, color=FIELD, bold=True))

    p.append(rect(475, 110, 350, 34, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(650, 131, "Монолітний блок: нагрівач + термопара + робочий кінчик", size=10, color=FIELD, bold=True))

    p.append(fitbox(475, 155, 350, 110, "Пряма передача енергії:\n• Термопара вмонтована безпосередньо у вістря\n• Відсутній повітряний прошарок (нульовий зазор)\n• Мікроконтролер станції опитує термопару сотні\n  разів на секунду; відгук < 20 мілісекунд", size=10.5, fill="#f0fdf4", stroke=FIELD, sw=1.0))

    p.append(fitbox(475, 275, 350, 120, "Поведінка на масивних полігонах:\n• Миттєва подача імпульсу потужності до 130–150 Вт\n• Стабільна температура: просідання не більше 10–15 °C\n• Паяння відбувається за комфортних 290–320 °C\n• Відсутній тепловий стрес для компонентів і плати", size=10.5, fill="#f0fdf4", stroke="#15803d", sw=1.2))

    render(os.path.join(OUT, "cartridge-vs-passive.svg"), W, H, *p)


# ── 3. tip-geometries: Геометрія жал та їхнє призначення ─────────────────────
def fig_tip_geometries():
    W, H = 920, 480
    p = []

    p.append(rect(15, 15, 890, 450, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(460, 44, "Профілі паяльних жал: фізика теплопередачі та призначення", size=15.5, color=INK, bold=True))

    col_w = 205
    xs = [30, 250, 470, 690]

    # 1. Мікрохвиля (Mini-wave / Spoon)
    p.append(rect(xs[0], 65, col_w, 385, fill="#ffffff", stroke="#2563eb", sw=1.2, rx=8))
    p.append(text(xs[0] + col_w/2, 90, "Мікрохвиля (GW/BCM)", size=12, color=NEG, bold=True))
    p.append(text(xs[0] + col_w/2, 107, "Зріз із лункою", size=10, color=MUTED))
    p.append(circle(xs[0] + col_w/2, 140, 20, fill="#dbeafe", stroke=NEG, sw=1.3))
    p.append(circle(xs[0] + col_w/2, 140, 9, fill="#93c5fd", stroke=NEG, sw=1.0))
    p.append(text(xs[0] + col_w/2, 144, "Лунка", size=9.5, color=NEG, bold=True))
    p.append(fitbox(xs[0] + 10, 172, col_w - 20, 265, "Застосування:\nDrag soldering для корпусів\nQFP, SOIC, TSSOP.\n\nФізичний принцип:\nУвігнута лунка утримує\nзапас рідкого припою силою\nповерхневого натягу.\n\nПри веденні жала вздовж ряду\nвиводів припій змочує мідні\nмайданчики, а надлишок сам\nвтягується назад у лунку\nбез утворення перемичок.", size=10, fill="#eff6ff", stroke=NEG, sw=1.0))

    # 2. Клин (Chisel / D)
    p.append(rect(xs[1], 65, col_w, 385, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=8))
    p.append(text(xs[1] + col_w/2, 90, "Клин (Chisel D)", size=12, color=FIELD, bold=True))
    p.append(text(xs[1] + col_w/2, 107, "Викрутка 1.6–3.2 мм", size=10, color=MUTED))
    p.append(rect(xs[1] + col_w/2 - 24, 126, 48, 28, fill="#dcfce7", stroke=FIELD, sw=1.3, rx=3))
    p.append(text(xs[1] + col_w/2, 144, "Площина", size=9.5, color=FIELD, bold=True))
    p.append(fitbox(xs[1] + 10, 172, col_w - 20, 265, "Застосування:\nМасивні полігони землі (GND),\nсилові роз'єми, дроселі.\n\nФізичний принцип:\nШирокий плаский торець дає\nмаксимальну площу контакту\nз металом плати.\n\nЗабезпечує колосальний\nтепловий потік, необхідний\nдля прогріву 4–6 шарів міді\nбез підняття температури\nстанції до небезпечних меж.", size=10, fill="#f0fdf4", stroke=FIELD, sw=1.0))

    # 3. Скошене копитце (Bevel / C)
    p.append(rect(xs[2], 65, col_w, 385, fill="#ffffff", stroke="#ea580c", sw=1.2, rx=8))
    p.append(text(xs[2] + col_w/2, 90, "Копитце (Bevel C)", size=12, color="#ea580c", bold=True))
    p.append(text(xs[2] + col_w/2, 107, "Зріз під кутом 45°", size=10, color=MUTED))
    p.append(rect(xs[2] + col_w/2 - 20, 126, 40, 28, fill="#ffedd5", stroke="#ea580c", sw=1.3, rx=3))
    p.append(text(xs[2] + col_w/2, 144, "Фаска 45°", size=9.5, color="#ea580c", bold=True))
    p.append(fitbox(xs[2] + 10, 172, col_w - 20, 265, "Застосування:\nSMD пасиви 0603/0805, діоди,\nтранзистори SOT-23.\n\nФізичний принцип:\nУніверсальна комбінована\nгеометрія.\n\nПлаский еліптичний зріз\nутворює тепловий місток\nчерез краплю припою,\nа тонкий край дозволяє\nпозиціонувати деталі та\nакуратно формувати галтель.", size=10, fill="#fff7ed", stroke="#ea580c", sw=1.0))

    # 4. Тонка голка (Conical / I)
    p.append(rect(xs[3], 65, col_w, 385, fill="#ffffff", stroke="#dc2626", sw=1.2, rx=8))
    p.append(text(xs[3] + col_w/2, 90, "Голка (Conical I)", size=12, color=POS, bold=True))
    p.append(text(xs[3] + col_w/2, 107, "Гострий конус (пастка)", size=10, color=MUTED))
    p.append(circle(xs[3] + col_w/2, 140, 7, fill="#fee2e2", stroke=POS, sw=1.3))
    p.append(text(xs[3] + col_w/2, 124, "Точка", size=9.5, color=POS, bold=True))
    p.append(fitbox(xs[3] + 10, 172, col_w - 20, 265, "Типова помилка:\nУявна точність для дрібного\nмонтажу 0402 / 0201.\n\nЧому це не працює:\nТочковий контакт має мізерну\nплощу теплопередачі.\n\nТонкий стрижень має високий\nвнутрішній опір: тепло не\nвстигає доходити до кінчика.\nМонтажник гріє задовго,\nруйнуючи плату перегрівом.", size=10, fill="#fef2f2", stroke=POS, sw=1.0))

    render(os.path.join(OUT, "tip-geometries.svg"), W, H, *p)


# ── 4. preheater-thermal-gradient: Механіка нижнього підігріву ────────────────
def fig_preheater_thermal_gradient():
    W, H = 880, 440
    p = []

    p.append(rect(15, 15, 850, 410, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=10))
    p.append(text(440, 44, "Розподіл тепла при монтажі QFN / Thermal Pad: без підігріву vs з підігрівом", size=15, color=INK, bold=True))

    # Ліва частина: Лише фен зверху
    p.append(rect(35, 65, 390, 345, fill="#ffffff", stroke="#dc2626", sw=1.3, rx=8))
    p.append(text(230, 92, "Без нижнього підігріву (лише фен)", size=13, color=POS, bold=True))

    p.append(fitbox(55, 110, 350, 50, "Фен згори: T_air = 380–420 °C\nЛокальний перегрів корпусу мікросхеми", size=10, fill="#fee2e2", stroke=POS, sw=1.2))

    p.append(rect(75, 175, 310, 30, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=4))
    p.append(text(230, 195, "Холодна багатошарова плата (T_pcb = 25 °C)", size=9.5, color="#ea580c", bold=True))

    p.append(fitbox(55, 220, 350, 175, "Фізика процесу та дефекти:\n• Мідні полігони та земляні перехідні отвори (vias)\n  миттєво відводять тепло у площину плати\n• Центральний майданчик (Thermal Pad) не прогрівається\n• Колосальний локальний градієнт ΔT > 350 °C\n• Наслідки:\n  - Короблення склотекстоліту FR-4\n  - Розшарування структури плати (delamination)\n  - Вигорання флюсу ще до розплавлення припою", size=10, fill="#fff1f2", stroke=POS, sw=1.0))

    # Права частина: З нижнім підігрівом
    p.append(rect(455, 65, 390, 345, fill="#ffffff", stroke="#16a34a", sw=1.3, rx=8))
    p.append(text(650, 92, "З нижнім підігрівом (Preheater / Hot Plate)", size=13, color=FIELD, bold=True))

    p.append(fitbox(475, 110, 350, 50, "Фен згори: T_air = 230–250 °C\nДелікатний локальний догрів зони оплавлення", size=10, fill="#fefce8", stroke="#ca8a04", sw=1.2))

    p.append(rect(495, 175, 310, 30, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(650, 195, "Плата рівномірно прогріта знизу: T_pcb = 120–140 °C", size=9.5, color=FIELD, bold=True))

    p.append(fitbox(475, 220, 350, 175, "Фізика процесу та результат:\n• Полігони плати вже насичені теплом і не крадуть енергію\n• Фену треба додати лише ΔT = 80–100 °C для оплавлення\n• Одночасне розплавлення припою на ніжках і Thermal Pad\n• Переваги:\n  - Швидке якісне самоцентрування мікросхеми\n  - Збереження цілісності маски й текстоліту\n  - Активний флюс без термічного розкладання", size=10, fill="#f0fdf4", stroke=FIELD, sw=1.0))

    render(os.path.join(OUT, "preheater-thermal-gradient.svg"), W, H, *p)


if __name__ == "__main__":
    fig_workbench_layout()
    fig_cartridge_vs_passive()
    fig_tip_geometries()
    fig_preheater_thermal_gradient()
    print("Всі фігури згенеровано успішно.")
