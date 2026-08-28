# -*- coding: utf-8 -*-
"""figs.py — генератор ілюстрацій для теми vkhidnyi-kontrol-i-pidrobni-komponenty (sys-notary).
Генерує 2 SVG-схеми в ./img/ за допомогою спільного svgkit.
"""
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(SCRIPT_DIR, "img"), exist_ok=True)


# ── Фігура 1: Послідовність вхідного контролю за AS6081 / IDEA-STD-1010 ─────────
def fig_counterfeit_inspection_workflow():
    W, H = 1000, 580
    P = []
    P.append(text(W / 2, 26, "Багаторівневий протокол вхідного контролю компонентів за стандартами AS6081 та IDEA-STD-1010", size=15, bold=True))

    stages = [
        ("Рівень 1: Пакування та документи", 
         "• Сертифікат відповідності (CoC)\n• Перевірка захисту MSL (J-STD-033)\n• Заводські стрічки, маркування, 2D-код\n• Пакувальний антистатичний ESD-аудит",
         "#eff6ff", "#2563eb"),
        ("Рівень 2: Зовнішній оптичний огляд",
         "• Мікроскопія поверхні компаунду\n• Тест розчинниками (Acetone, NMP)\n• Виявлення Blacktop та перемаркування\n• Стан виводів, копланарність, дефекти",
         "#fefce8", "#ca8a04"),
        ("Рівень 3: Рентгенографія та XRF",
         "• Рентген (X-Ray): кристал і розварка\n• Виявлення пустот і зміщення підкладки\n• Спектрометрія XRF: склад припою\n• Перевірка вмісту свинцю (Pb / RoHS)",
         "#f0fdf4", "#16a34a"),
        ("Рівень 4: Декапсуляція та кристал",
         "• Кислотне травлення (HNO3 / H2SO4)\n• Огляд топології кристала (Die mask)\n• Верифікація логотипу та копірайту\n• Перевірка ревізії кремнієвої топології",
         "#faf5ff", "#9333ea"),
        ("Рівень 5: Електропараметрика",
         "• Зняття сигнатур переходів (Curve Tracer)\n• Струм спокою споживання (IDD_q)\n• Вхідні/вихідні струми витоку та рівні\n• Тестування на температурних межах",
         "#fff1f2", "#e11d48")
    ]

    sw = 172
    gap = 20
    x0 = 25
    y0 = 60
    sh = 190

    for i, (title, desc, fill_c, strk_c) in enumerate(stages):
        sx = x0 + i * (sw + gap)
        P.append(rect(sx, y0, sw, sh, fill=fill_c, stroke=strk_c, sw=1.8, rx=6))
        P.append(text(sx + sw / 2, y0 + 22, title, size=11, bold=True, color=strk_c))
        P.append(mtext(sx + 10, y0 + 48, desc, size=9.5, color=INK, anchor="start", lh=1.35))
        
        # Стрілка переходу між рівнями
        if i < len(stages) - 1:
            P.append(arrow(sx + sw + 2, y0 + sh / 2, sx + sw + gap - 4, y0 + sh / 2, color="#64748b", sw=1.8))

    # Нижня частина: Розгалуження вердиктів
    P.append(rect(25, 275, 950, 275, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    P.append(text(500, 300, "МАТРИЦЯ ПРИЙНЯТТЯ РІШЕНЬ ТА ПРОЦЕДУРА КВАЛІФІКАЦІЇ ПАРТІЇ", size=12.5, bold=True, color="#1e293b"))

    # Блок Успіху
    P.append(rect(45, 325, 425, 205, fill="#f0fdf4", stroke="#16a34a", sw=1.6, rx=6))
    P.append(text(257, 350, "ПРИДАТНО: ДОПУСК У СЕРІЙНЕ ВИРОБНИЦТВО", size=11.5, bold=True, color="#15803d"))
    ok_text = (
        "1. Усі 5 рівнів пройдено без зауважень за вибіркою ANSI/ASQ Z1.4.\n"
        "2. V-I сигнатури ESD-діодів повністю відповідають еталону (UUT ≈ Gold).\n"
        "3. Відсутні сліди шліфування, розчинники не змивають маркування.\n"
        "4. Рентген підтверджує автентичну геометрію підкладки та дротів.\n"
        "5. Формується верифікаційний паспорт партії та вноситься в PLM/ERP."
    )
    P.append(mtext(60, 375, ok_text, size=9.5, color=INK, anchor="start", lh=1.35))

    # Блок Відбракування
    P.append(rect(530, 325, 425, 205, fill="#fef2f2", stroke="#dc2626", sw=1.6, rx=6))
    P.append(text(742, 350, "ВІДХИЛЕНО: ВИЯВЛЕНО ПІДРОБКУ АБО БРАК", size=11.5, bold=True, color="#b91c1c"))
    bad_text = (
        "1. Негайна ізоляція всієї партії у фізичний карантинний ізолятор.\n"
        "2. Блокування лоту в ERP-системі для унеможливлення видачі на склад.\n"
        "3. Оформлення акта невідповідності (Non-Conformance Report, NCR).\n"
        "4. Внесення інциденту до баз даних контрафакту GIDEP та ERAI.\n"
        "5. Юридична претензія постачальнику й утилізація без повернення на ринок."
    )
    P.append(mtext(545, 375, bad_text, size=9.5, color=INK, anchor="start", lh=1.35))

    render(os.path.join(SCRIPT_DIR, "img", "counterfeit-inspection-workflow.svg"), W, H, *P)


# ── Фігура 2: Порівняння рентгеноструктури автентичного та підробленого чіпа ─────
def fig_xray_die_bonding_comparison():
    W, H = 1000, 560
    P = []
    P.append(text(W / 2, 26, "Порівняльний аналіз внутрішньої структури мікросхеми під рентгеном (X-Ray) та мікроскопом", size=15, bold=True))

    # Ліва колонка: Автентичний компонент
    P.append(rect(25, 55, 460, 480, fill="#f8fafc", stroke="#16a34a", sw=1.8, rx=8))
    P.append(text(255, 82, "АВТЕНТИЧНИЙ ОРИГІНАЛЬНИЙ ОЕМ-ЧІП", size=12.5, bold=True, color="#15803d"))

    # Схематичний вигляд чіпа
    P.append(rect(105, 105, 300, 210, fill="#1e293b", stroke="#475569", sw=1.5, rx=4)) # Корпус
    P.append(rect(175, 145, 160, 130, fill="#334155", stroke="#64748b", sw=1.2)) # Підкладка (Paddle)
    P.append(rect(205, 170, 100, 80, fill="#64748b", stroke="#94a3b8", sw=1.2)) # Кристал (Die)
    P.append(text(255, 215, "OEM DIE\n(Повний розмір)", size=10, bold=True, color="#f8fafc"))

    # Виводи з боків
    for y_pin in range(125, 300, 30):
        P.append(rect(75, y_pin, 30, 14, fill="#94a3b8", stroke="#475569", sw=1.0))
        P.append(rect(405, y_pin, 30, 14, fill="#94a3b8", stroke="#475569", sw=1.0))
        # Золоті дроти (Au wire bonds)
        P.append(line(105, y_pin + 7, 205, 185 + (y_pin - 125) * 0.3, color="#fbbf24", sw=1.5))
        P.append(line(405, y_pin + 7, 305, 185 + (y_pin - 125) * 0.3, color="#fbbf24", sw=1.5))

    # Текстовий опис ознак оригіналу
    auth_desc = (
        "✓ Розмір кристала точно відповідає заводській масці виробника.\n"
        "✓ Золоті дроти (Au) однакової довжини з правильним прогином петлі.\n"
        "✓ Суцільний шар припою/компаунду підкладки без пустот (voids < 5%).\n"
        "✓ Симетрична монолітна вивідна рамка з заводським штампом.\n"
        "✓ Відсутні сліди перерозварювання, відриву або подвійних контактів."
    )
    P.append(rect(40, 335, 430, 180, fill="#ffffff", stroke="#86efac", sw=1.4, rx=6))
    P.append(mtext(55, 360, auth_desc, size=10, color=INK, anchor="start", lh=1.4))

    # Права колонка: Контрафактний чіп
    P.append(rect(515, 55, 460, 480, fill="#f8fafc", stroke="#dc2626", sw=1.8, rx=8))
    P.append(text(745, 82, "КОНТРАФАКТНИЙ / ПЕРЕМАРКОВАНИЙ ЧІП", size=12.5, bold=True, color="#b91c1c"))

    # Схематичний вигляд чіпа підробки
    P.append(rect(595, 105, 300, 210, fill="#1e293b", stroke="#475569", sw=1.5, rx=4)) # Корпус
    P.append(rect(675, 145, 140, 130, fill="#334155", stroke="#64748b", sw=1.2)) # Чужа підкладка
    P.append(rect(710, 175, 70, 70, fill="#475569", stroke="#ef4444", sw=1.4)) # Зменшений кристал-клон
    P.append(text(745, 205, "КЛОН", size=10, bold=True, color="#fca5a5"))
    P.append(text(745, 220, "(-60%)", size=9, bold=True, color="#fca5a5"))

    # Виводи з боків та дефектні дроти
    for i, y_pin in enumerate(range(125, 300, 30)):
        P.append(rect(565, y_pin, 30, 14, fill="#cbd5e1", stroke="#991b1b", sw=1.0))
        P.append(rect(895, y_pin, 30, 14, fill="#cbd5e1", stroke="#991b1b", sw=1.0))
        if i == 1:
            # Обірваний дріт
            P.append(line(595, y_pin + 7, 650, y_pin + 20, color="#ef4444", sw=1.5, dash="3,3"))
        elif i == 3:
            # Перехресне розварювання
            P.append(line(895, y_pin + 7, 780, 185, color="#f87171", sw=1.5))
        else:
            P.append(line(595, y_pin + 7, 710, 185 + (y_pin - 125) * 0.25, color="#f87171", sw=1.5))
            P.append(line(895, y_pin + 7, 780, 185 + (y_pin - 125) * 0.25, color="#f87171", sw=1.5))

    # Пустоти / деламінація
    P.append(circle(685, 255, 10, fill="#ef4444", stroke="#b91c1c", sw=1.2))
    P.append(circle(805, 160, 8, fill="#ef4444", stroke="#b91c1c", sw=1.2))

    # Текстовий опис ознак підробки
    fake_desc = (
        "✗ Площа кристала значно менша за оригінал (дешевий кристал-замінник).\n"
        "✗ Дешеві алюмінієві/мідні дроти з обривами та різною кривизною петель.\n"
        "✗ Масивні термічні пустоти й деламінація (> 35%) від кустарного випаювання.\n"
        "✗ Невідповідність підкладки (leadframe paddle) оригінальній прес-формі.\n"
        "✗ Залишкові залишки старих обірваних дротів від попереднього монтажу."
    )
    P.append(rect(530, 335, 430, 180, fill="#ffffff", stroke="#fca5a5", sw=1.4, rx=6))
    P.append(mtext(545, 360, fake_desc, size=10, color=INK, anchor="start", lh=1.4))

    render(os.path.join(SCRIPT_DIR, "img", "xray-die-bonding-comparison.svg"), W, H, *P)


if __name__ == "__main__":
    fig_counterfeit_inspection_workflow()
    fig_xray_die_bonding_comparison()
    print("Done: generated 2 illustrations in ./img/")
