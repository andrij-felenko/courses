# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# ── 1. Робота лабораторного джерела у режимах CV/CC та пастка вихідної ємності ─
def fig_bench_power_supply_current_limiting():
    W, H = 940, 490
    f = []

    # ── Ліва панель: ВАХ (Вольт-амперна характеристика джерела) ───────────────
    lx, ly, lw, lh = 30, 48, 420, 422
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(lx + lw / 2, ly + 22, "ВАХ джерела: перехід CV (Voltage) → CC (Current)", size=12, bold=True, color=INK))

    # Осі координат
    ax_x0, ax_y0 = lx + 60, ly + 345
    ax_x1, ax_y1 = lx + 380, ly + 55

    # Стрілки осей
    f.append(line(ax_x0, ax_y0, ax_x1 + 15, ax_y0, color="#64748b", sw=1.5))
    f.append(line(ax_x0, ax_y0, ax_x0, ax_y1 - 10, color="#64748b", sw=1.5))
    f.append(text(ax_x1 + 18, ax_y0 + 4, "I (Струм)", size=10, color="#475569", bold=True, anchor="start"))
    f.append(text(ax_x0, ax_y1 - 18, "V (Напруга)", size=10, color="#475569", bold=True, anchor="middle"))

    # Позначки на осях
    f.append(line(ax_x0 - 4, ly + 110, ax_x0, ly + 110, color="#64748b", sw=1.5))
    f.append(text(ax_x0 - 8, ly + 114, "V_set (5.0 В)", size=9.5, color="#334155", anchor="end", bold=True))

    f.append(line(lx + 270, ax_y0, lx + 270, ax_y0 + 4, color="#64748b", sw=1.5))
    f.append(text(lx + 270, ax_y0 + 16, "I_limit (200 мА)", size=9.5, color="#334155", anchor="middle", bold=True))

    # Зони роботи CV / CC
    f.append(rect(ax_x0 + 1, ly + 110, 209, ax_y0 - (ly + 110), fill="#f0fdf4", stroke="none"))
    f.append(text(ax_x0 + 104, ly + 220, "Зона стабілізації напруги (CV)", size=10, color=FIELD, bold=True))
    f.append(text(ax_x0 + 104, ly + 238, "V = V_set (константа)", size=9.5, color="#15803d"))
    f.append(text(ax_x0 + 104, ly + 252, "I < I_limit", size=9.5, color="#15803d"))

    f.append(rect(lx + 270, ly + 110, 110, ax_y0 - (ly + 110), fill="#fef2f2", stroke="none"))
    f.append(text(lx + 325, ly + 220, "Зона захисту (CC)", size=10, color=POS, bold=True))
    f.append(text(lx + 325, ly + 238, "I = I_limit (константа)", size=9.5, color="#991b1b"))
    f.append(text(lx + 325, ly + 252, "V_out спадає до нуля", size=9.5, color="#991b1b"))

    # Лінія характеристики
    f.append(line(ax_x0, ly + 110, lx + 270, ly + 110, color=FIELD, sw=3))
    f.append(line(lx + 270, ly + 110, lx + 270, ax_y0, color=POS, sw=3))

    # Точки режиму
    # Точка А (штатна)
    pax, pay = ax_x0 + 90, ly + 110
    f.append(circle(pax, pay, 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    f.append(text(pax, pay - 10, "Точка А: Норма (100 мА / 5.0 В)", size=9.5, color=FIELD, bold=True))

    # Точка B (КЗ)
    pbx, pby = lx + 270, ax_y0 - 25
    f.append(circle(pbx, pby, 5, fill=POS, stroke="#ffffff", sw=1.5))
    f.append(text(pbx - 10, pby - 8, "Точка Б: КЗ (200 мА / 0.2 В)", size=9.5, color=POS, bold=True, anchor="end"))

    # Підпис знизу
    f.append(rect(lx + 15, ly + 372, lw - 30, 36, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    f.append(text(lx + lw / 2, ly + 386, "При короткому замиканні напруга падає: V_out = I_limit · R_short", size=9.5, color=INK, bold=True))
    f.append(text(lx + lw / 2, ly + 400, "Потужність на платі обмежена величиною P = V_out · I_limit ≈ 0.04 Вт", size=9, color=MUTED))

    # ── Права панель: Структура джерела та пастка вихідного конденсатора ───────
    rx, ry, rw, rh = 470, 48, 440, 422
    f.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(rx + rw / 2, ry + 22, "Внутрішній контур джерела та розряд C_out", size=12, bold=True, color=INK))

    # Блок лабораторного БЖ
    bx, by, bw, bh = rx + 15, ry + 42, 240, 230
    f.append(rect(bx, by, bw, bh, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=4))
    f.append(text(bx + bw / 2, by + 18, "Лабораторний блок живлення", size=11, bold=True, color="#1e293b"))

    # Внутрішні елементи БЖ
    f.append(rect(bx + 15, by + 35, 80, 40, fill="#e2e8f0", stroke="#475569", sw=1, rx=3))
    f.append(text(bx + 55, by + 52, "Регулятор", size=9.5, bold=True, color="#0f172a"))
    f.append(text(bx + 55, by + 65, "MOSFET/BJT", size=9, color=MUTED))

    # Струмовий шунт
    f.append(rect(bx + 130, by + 45, 50, 22, fill="#fef3c7", stroke="#d97706", sw=1, rx=2))
    f.append(text(bx + 155, by + 60, "R_shunt", size=9, bold=True, color="#92400e"))

    # Лінія виходу +
    f.append(line(bx + 95, by + 55, bx + 130, by + 55, color=POS, sw=2))
    f.append(line(bx + 180, by + 55, bx + bw, by + 55, color=POS, sw=2))

    # Лінія виходу -
    f.append(line(bx + 15, by + 195, bx + bw, by + 195, color=NEG, sw=2))

    # Конденсатор C_out всередині БЖ
    f.append(line(bx + 205, by + 55, bx + 205, by + 105, color=POS, sw=1.5))
    f.append(rect(bx + 190, by + 105, 30, 35, fill="#fee2e2", stroke=POS, sw=1.2, rx=2))
    f.append(text(bx + 205, by + 120, "C_out", size=9.5, bold=True, color=POS))
    f.append(text(bx + 205, by + 133, "470 мкФ", size=9, color=POS))
    f.append(line(bx + 205, by + 140, bx + 205, by + 195, color=NEG, sw=1.5))

    # Компаратор CC зворотного зв'язку
    f.append(rect(bx + 20, by + 115, 120, 50, fill="#f1f5f9", stroke="#94a3b8", sw=1, rx=3))
    f.append(text(bx + 80, by + 133, "Петля CC-захисту", size=9.5, bold=True, color="#334155"))
    f.append(text(bx + 80, by + 148, "Час реакції: 50–200 мкс", size=9, color="#64748b"))

    # Плата навантаження справа
    px, py, pw, ph = rx + 285, ry + 42, 140, 230
    f.append(rect(px, py, pw, ph, fill="#f0fdf4", stroke="#16a34a", sw=1.2, rx=4))
    f.append(text(px + pw / 2, py + 18, "Нова плата (DUT)", size=11, bold=True, color="#15803d"))

    # КЗ на платі
    f.append(rect(px + 20, py + 95, 100, 50, fill="#fef2f2", stroke=POS, sw=1.2, rx=3))
    f.append(text(px + 70, py + 115, "Дефект: КЗ", size=10, bold=True, color=POS))
    f.append(text(px + 70, py + 132, "R_short = 0.1 Ом", size=9, color="#991b1b"))

    # З'єднання між БЖ і платою
    f.append(line(bx + bw, by + 55, px + 20, by + 55, color=POS, sw=2))
    f.append(line(px + 20, by + 55, px + 70, py + 95, color=POS, sw=1.5))

    f.append(line(bx + bw, by + 195, px + 20, by + 195, color=NEG, sw=2))
    f.append(line(px + 20, by + 195, px + 70, py + 145, color=NEG, sw=1.5))

    # Стрілка небезпечного струму розряду
    f.append(line(bx + 205, by + 38, px + 70, by + 38, color=POS, sw=2, dash="4,3"))
    f.append(text(rx + 265, by + 30, "Піковий розряд C_out: до 30–50 А за < 5 мкс!", size=9.5, bold=True, color=POS))

    # Нижній блок пояснення небезпеки C_out
    by_bot = ry + 285
    f.append(rect(rx + 15, by_bot, rw - 30, 122, fill="#fef2f2", stroke="#f87171", sw=1, rx=4))
    f.append(text(rx + 25, by_bot + 18, "Пастка вихідної ємності джерела живлення (C_out):", size=10.5, bold=True, color="#991b1b", anchor="start"))
    f.append(text(rx + 25, by_bot + 38, "1. Навіть при встановленому ліміті струму 50 мА вихідний конденсатор БЖ заряджений до 5 В.", size=9.5, color="#7f1d1d", anchor="start"))
    f.append(text(rx + 25, by_bot + 56, "2. При підключенні плати вся енергія E = 0.5 · C · V² миттєво скидається в місце дефекту.", size=9.5, color="#7f1d1d", anchor="start"))
    f.append(text(rx + 25, by_bot + 74, "3. Петля зворотного зв'язку за струмом CC має затримку 50–200 мкс і не захищає від розряду C_out.", size=9.5, color="#7f1d1d", anchor="start"))
    f.append(text(rx + 25, by_bot + 96, "Правило: вмикати вихід БЖ кнопкою Output ON після підключення або плавно крутити напругу від 0 В.", size=9.5, bold=True, color="#991b1b", anchor="start"))

    return "".join(f)

# ── 2. Тепловізійний моніторинг гарячих точок та алгоритм діагностики ─────────
def fig_thermal_hotspot_triaging():
    W, H = 940, 510
    f = []

    # ── Ліва частина: Зразки теплових сигнатур на платі ───────────────────────
    lx, ly, lw, lh = 30, 48, 430, 442
    f.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(lx + lw / 2, ly + 22, "Типові теплові сигнатури несправностей (IR)", size=12, bold=True, color=INK))

    # Секція 1: Нормальний LDO
    s1_y = ly + 40
    f.append(rect(lx + 15, s1_y, lw - 30, 114, fill="#f8fafc", stroke="#cbd5e1", sw=1, rx=4))
    f.append(text(lx + 25, s1_y + 18, "1. Штатний нагрів лінійного стабілізатора (LDO)", size=10.5, bold=True, color="#1e293b", anchor="start"))

    # Міні-макет чіпа LDO
    f.append(rect(lx + 35, s1_y + 34, 50, 40, fill="#334155", stroke="#1e293b", sw=1, rx=2))
    f.append(text(lx + 60, s1_y + 58, "LDO", size=9.5, bold=True, color="#ffffff"))
    # Тепловий ореол навколо (градієнт)
    f.append(circle(lx + 60, s1_y + 54, 32, fill="none", stroke="#fb923c", sw=2))
    f.append(circle(lx + 60, s1_y + 54, 42, fill="none", stroke="#fdba74", sw=1.5))

    f.append(text(lx + 130, s1_y + 44, "• Температура: 35–45 °C (рівномірна)", size=9.5, color="#334155", anchor="start"))
    f.append(text(lx + 130, s1_y + 62, "• Тепло розсіюється через мідний полігон GND", size=9.5, color="#334155", anchor="start"))
    f.append(text(lx + 130, s1_y + 80, "• Градієнт плавний, немає локального перегріву виводів", size=9.5, color="#15803d", bold=True, anchor="start"))

    # Секція 2: Пробитий керамічний конденсатор MLCC
    s2_y = ly + 164
    f.append(rect(lx + 15, s2_y, lw - 30, 122, fill="#fef2f2", stroke="#fca5a5", sw=1, rx=4))
    f.append(text(lx + 25, s2_y + 18, "2. Пробитий MLCC (тріщина діелектрика / КЗ)", size=10.5, bold=True, color="#991b1b", anchor="start"))

    # Міні-макет MLCC
    f.append(rect(lx + 40, s2_y + 35, 40, 20, fill="#92400e", stroke="#78350f", sw=1, rx=1))
    f.append(rect(lx + 38, s2_y + 35, 8, 20, fill="#94a3b8", stroke="#64748b", sw=0.8))
    f.append(rect(lx + 74, s2_y + 35, 8, 20, fill="#94a3b8", stroke="#64748b", sw=0.8))
    # Точкова гаряча точка (hotspot)
    f.append(circle(lx + 60, s2_y + 45, 14, fill=POS, stroke="#fef08a", sw=2))
    f.append(text(lx + 60, s2_y + 49, ">90°", size=9, bold=True, color="#ffffff"))

    f.append(text(lx + 130, s2_y + 42, "• Температура: 80–120 °C (точковий спалах)", size=9.5, color="#991b1b", bold=True, anchor="start"))
    f.append(text(lx + 130, s2_y + 60, "• Локалізація: один корпус 0402/0603/0805", size=9.5, color="#334155", anchor="start"))
    f.append(text(lx + 130, s2_y + 78, "• Причина: мікротріщина від термоудару пайки або згину", size=9.5, color="#334155", anchor="start"))
    f.append(text(lx + 130, s2_y + 96, "• Дія: зняти паяльником та перевірити опір шини", size=9.5, color="#991b1b", bold=True, anchor="start"))

    # Секція 3: Неправильна орієнтація ІС / Latch-up
    s3_y = ly + 296
    f.append(rect(lx + 15, s3_y, lw - 30, 128, fill="#fffbeb", stroke="#fde68a", sw=1, rx=4))
    f.append(text(lx + 25, s3_y + 18, "3. Перевернутий чіп (зсув на 90°/180° / Latch-up)", size=10.5, bold=True, color="#92400e", anchor="start"))

    # Чіп QFN з гарячими кутовими діодами
    f.append(rect(lx + 35, s3_y + 36, 50, 50, fill="#1e293b", stroke="#0f172a", sw=1, rx=2))
    f.append(circle(lx + 43, s3_y + 44, 3, fill="#ffffff")) # Точка ключа Pin 1
    # Гарячий кут
    f.append(circle(lx + 75, s3_y + 76, 12, fill=POS, stroke="#f59e0b", sw=1.8))
    f.append(text(lx + 75, s3_y + 80, "ESD", size=9, bold=True, color="#ffffff"))

    f.append(text(lx + 130, s3_y + 42, "• Температура: 70–110 °C біля кута чіпа", size=9.5, color="#92400e", bold=True, anchor="start"))
    f.append(text(lx + 130, s3_y + 60, "• Прямий струм тече крізь вбудовані ESD-діоди на GND", size=9.5, color="#334155", anchor="start"))
    f.append(text(lx + 130, s3_y + 78, "• Небезпека: деградація кремнію та пропікання корпусу", size=9.5, color="#334155", anchor="start"))
    f.append(text(lx + 130, s3_y + 96, "• Демонтаж обов'язковий: компонент часто пошкоджений", size=9.5, color="#b45309", bold=True, anchor="start"))

    # ── Права частина: Алгоритм тріажу гарячих точок (Flowchart) ──────────────
    rx, ry, rw, rh = 480, 48, 430, 442
    f.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke="#d0d5dd", sw=1.2, rx=6))
    f.append(text(rx + rw / 2, ry + 22, "Алгоритм покрокової локалізації КЗ (Тріаж)", size=12, bold=True, color=INK))

    # Крок 1: Подача живлення
    k1_y = ry + 40
    f.append(fitbox(rx + 25, k1_y, rw - 50, 44, "1. Подати номінальну V_in з I_limit = 50–100 мА\nБЖ переходить у CC-режим (напруга просіла)", size=10, fill="#f1f5f9", stroke="#94a3b8", bold=True))

    f.append(arrow(rx + rw / 2, k1_y + 44, rx + rw / 2, k1_y + 60, color="#64748b"))

    # Крок 2: Тепловізійний огляд
    k2_y = k1_y + 60
    f.append(fitbox(rx + 25, k2_y, rw - 50, 44, "2. Огляд плати тепловізором (або спиртовий тест)\nШукаємо компонент з ΔT > +15 °C відносно плати", size=10, fill="#fef3c7", stroke="#d97706", bold=True))

    f.append(arrow(rx + rw / 2, k2_y + 44, rx + rw / 2, k2_y + 60, color="#64748b"))

    # Крок 3: Розгалуження — тип нагріву
    k3_y = k2_y + 60
    f.append(rect(rx + 25, k3_y, rw - 50, 72, fill="#ffffff", stroke="#475569", sw=1.2, rx=4))
    f.append(text(rx + rw / 2, k3_y + 18, "3. Ідентифікація типу нагрітого вузла:", size=10.5, bold=True, color=INK))
    f.append(text(rx + 40, k3_y + 38, "A. Пасивний елемент (MLCC, TVS, діод)", size=9.5, color="#334155", anchor="start"))
    f.append(text(rx + 40, k3_y + 56, "Б. Активна мікросхема (MCU, DC-DC, LDO)", size=9.5, color="#334155", anchor="start"))

    f.append(arrow(rx + 115, k3_y + 72, rx + 115, k3_y + 92, color="#64748b"))
    f.append(arrow(rx + rw - 115, k3_y + 72, rx + rw - 115, k3_y + 92, color="#64748b"))

    # Крок 4А (Зняття MLCC)
    k4a_y = k3_y + 92
    f.append(fitbox(rx + 15, k4a_y, 195, 74, "Гілка А: Зняти MLCC / TVS\n• Випаяти елемент\n• Перевірити опір шини\n• Якщо КЗ зникло — заміна", size=9.5, fill="#f0fdf4", stroke="#16a34a", color="#14532d", bold=True))

    # Крок 4Б (Секціонування)
    f.append(fitbox(rx + 220, k4a_y, 195, 74, "Гілка Б: Секціонування\n• Розімкнути 0R перемичку\n• Визначити: КЗ до чи після\n• Перевірити ключ Pin 1 чипа", size=9.5, fill="#fef2f2", stroke="#dc2626", color="#7f1d1d", bold=True))

    # Крок 5 (Фінальна перевірка)
    k5_y = k4a_y + 88
    f.append(arrow(rx + 110, k4a_y + 74, rx + rw / 2, k5_y, color="#16a34a"))
    f.append(arrow(rx + 310, k4a_y + 74, rx + rw / 2, k5_y, color="#dc2626"))

    f.append(fitbox(rx + 25, k5_y, rw - 50, 50, "5. Контрольний замір: R_rail > 1 кОм (для 3.3 В / 5 В)\nПовторне вмикання з підняттям I_limit до робочого струму", size=9.5, fill="#eff6ff", stroke="#2563eb", color="#1e40af", bold=True))

    return "".join(f)

if __name__ == "__main__":
    render(os.path.join(IMG, "bench-power-supply-current-limiting.svg"), 940, 490,
           fig_bench_power_supply_current_limiting(),
           title="Режими CV/CC лабораторного джерела живлення та динаміка пускового струму")
    render(os.path.join(IMG, "thermal-hotspot-triaging.svg"), 940, 510,
           fig_thermal_hotspot_triaging(),
           title="Тепловізійний аналіз друкованої плати та локалізація критичних дефектів")
    print("Figures generated successfully in img/")
