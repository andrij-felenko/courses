# -*- coding: utf-8 -*-
import sys, os

# Шлях до scripts/ у корені репозиторію (4 рівні вгору від теки теми)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Палітра кольорів ────────────────────────────────────────────────
CLR_ALERT   = "#c0392b"     # Атака, вторгнення, критичне занулення
CLR_ALERT_F = "#fdecea"
CLR_SECURE  = "#27ae60"     # Захищений домен, цілісність
CLR_SECURE_F= "#eafaf0"
CLR_WARN    = "#d97706"     # Сенсор, поріг спрацювання
CLR_WARN_F  = "#fef3c7"
CLR_SIGNAL  = "#2457d6"     # Сигнали, шини, LFSR
CLR_SIGNAL_F= "#eaf0fd"
CLR_HARD    = "#4b5563"     # Механіка, корпус, плата
CLR_HARD_F  = "#f3f4f6"
CLR_BAT     = "#8b5cf6"     # Батарейний резервний домен
CLR_BAT_F   = "#f5f3ff"


# ── 1. Вектори фізичних атак на пристрій ─────────────────────────────
def fig_tamper_threat_vectors():
    W, H = 1040, 520
    p = []

    p.append(text(W / 2, 28, "Вектори фізичних атак та точки вторгнення в захищений пристрій", size=16, color=INK, bold=True))

    # Корпус / Зовнішній контур
    p.append(rect(40, 55, 960, 440, fill="#ffffff", stroke=LINE, sw=2, rx=10))
    p.append(text(160, 80, "Зовнішній корпус пристрою", size=13, color=MUTED, bold=True))

    # 4 блоки загроз
    attacks = [
        (80, 110, 200, 165, "Механічне розкриття", "Зняття кришки корпусу,\nвідкручування гвинтів.\nСвітло потрапляє всередину,\nрозмикаються контакти.", CLR_ALERT_F, CLR_ALERT),
        (310, 110, 200, 165, "Мікросвердління", "Просвердлювання отвору\nдіаметром 0.5–1 мм для\nвведення мікрозондів до\nвнутрішніх шин Flash/RAM.", CLR_ALERT_F, CLR_ALERT),
        (540, 110, 200, 165, "Cold Boot (Заморозка)", "Охолодження чипа спреєм\nчи рідким азотом (< -30°C).\nЗаряд у SRAM зберігається\nсекундами без живлення.", CLR_SIGNAL_F, CLR_SIGNAL),
        (770, 110, 200, 165, "Глітчинг живлення", "Маніпуляція напругою VDD\nта тактовою частотою.\nСпроба пропустити команду\nперевірки пароля/підпису.", CLR_WARN_F, CLR_WARN),
    ]

    for x, y, w, h, title, desc, bg_c, strk_c in attacks:
        p.append(rect(x, y, w, h, fill=bg_c, stroke=strk_c, sw=1.5, rx=8))
        p.append(text(x + w / 2, y + 26, title, size=13, color=strk_c, bold=True))
        p.append(fitbox(x + 10, y + 42, w - 20, h - 52, desc, size=11, fill=bg_c, stroke=bg_c))

    # Захисний периметр всередині
    p.append(rect(80, 310, 890, 160, fill=CLR_SECURE_F, stroke=CLR_SECURE, sw=1.8, rx=8))
    p.append(text(525, 335, "Захисний бар'єр: Сенсори + Активна сітка + Резервний домен MCU", size=14, color=CLR_SECURE, bold=True))

    sensors = [
        (100, 360, 190, 90, "Оптичні фотодіоди та\nмікроперемикачі NC/NO"),
        (325, 360, 190, 90, "Активна сітка (Mesh)\nз динамічним кодом LFSR"),
        (550, 360, 190, 90, "Температурний монітор\n(поріг < -25°C і > +105°C)"),
        (775, 360, 190, 90, "Brownout-детектор та\nапаратна зероїзація"),
    ]

    for x, y, w, h, txt in sensors:
        p.append(fitbox(x, y, w, h, txt, size=11, fill="#ffffff", stroke=CLR_SECURE, sw=1.2))

    return render(os.path.join(OUT, "physical-tamper-threat-vectors.svg"), W, H, *p)


# ── 2. Принцип роботи активної сітки (Active Mesh Shield) ─────────────
def fig_active_mesh_shield():
    W, H = 1040, 540
    p = []

    p.append(text(W / 2, 28, "Принцип роботи динамічної активної захисної сітки (Active Mesh Shield)", size=16, color=INK, bold=True))

    # Ліва колонка: Контролер тампера
    p.append(rect(40, 60, 240, 440, fill=CLR_SECURE_F, stroke=CLR_SECURE, sw=1.8, rx=8))
    p.append(text(160, 90, "Контролер тампера", size=14, color=CLR_SECURE, bold=True))
    p.append(text(160, 110, "(Апаратний домен VBAT)", size=11, color=MUTED, italic=True))

    p.append(fitbox(60, 135, 200, 75, "Генератор LFSR\nПсевдовипадковий бітовий\nпотік із регулярною зміною", size=11, fill="#ffffff", stroke=CLR_SIGNAL, bold=True))
    p.append(fitbox(60, 230, 200, 70, "Виходи TAMP_OUT1/2\nДва взаємно інверсні або\nзсунуті в часі сигнали", size=11, fill=CLR_SIGNAL_F, stroke=CLR_SIGNAL))

    p.append(fitbox(60, 320, 200, 70, "Входи TAMP_IN1/2\nПорівняння отриманого біта\nз очікуваним у поточному такті", size=11, fill=CLR_WARN_F, stroke=CLR_WARN))
    p.append(fitbox(60, 410, 200, 70, "Модуль рішень\nМиттєвий тригер зероїзації\nпри будь-якому незбігу", size=11, fill=CLR_ALERT_F, stroke=CLR_ALERT, bold=True))

    # Центральна частина: Фізична сітка на платі / гнучкому шлейфі
    p.append(rect(320, 60, 400, 440, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(520, 90, "Захисна сітка (PCB / Flex Mesh)", size=14, color=INK, bold=True))
    p.append(text(520, 110, "Переплетені мікродоріжки 50–100 мкм у шарах плати", size=11, color=MUTED, italic=True))

    # Доріжки сітки (імітація змійки)
    p.append(line(350, 160, 690, 160, color=CLR_SIGNAL, sw=3))
    p.append(line(690, 160, 690, 200, color=CLR_SIGNAL, sw=3))
    p.append(line(690, 200, 350, 200, color=CLR_SIGNAL, sw=3))
    p.append(line(350, 200, 350, 240, color=CLR_SIGNAL, sw=3))
    p.append(line(350, 240, 690, 240, color=CLR_SIGNAL, sw=3))

    p.append(line(350, 270, 690, 270, color=CLR_WARN, sw=3, dash="4,4"))
    p.append(line(690, 270, 690, 310, color=CLR_WARN, sw=3, dash="4,4"))
    p.append(line(690, 310, 350, 310, color=CLR_WARN, sw=3, dash="4,4"))
    p.append(line(350, 310, 350, 350, color=CLR_WARN, sw=3, dash="4,4"))
    p.append(line(350, 350, 690, 350, color=CLR_WARN, sw=3, dash="4,4"))

    p.append(fitbox(340, 380, 360, 105, "Непроникний кокон:\nСвердло перерізає лінію → Обрив\nГолка перемикає сусідні лінії → Замикання A на B\nЗонд заземлює доріжку → Замикання на GND\nШунтування неможливе: сигнал динамічний!", size=11, fill="#ffffff", stroke=CLR_SECURE))

    # Права колонка: Чотири зафіксовані типи втручання
    p.append(rect(760, 60, 240, 440, fill="#ffffff", stroke=CLR_ALERT, sw=1.5, rx=8))
    p.append(text(880, 90, "Стани вторгнення", size=14, color=CLR_ALERT, bold=True))

    violations = [
        (780, 125, 200, 70, "1. Обрив лінії (Open)\nПерерізано доріжку свердлом;\nсигнал не доходить до IN", CLR_ALERT_F, CLR_ALERT),
        (780, 215, 200, 70, "2. Замикання на GND/VDD\nЗонд або інструмент торкнувся\nшини живлення чи землі", CLR_ALERT_F, CLR_ALERT),
        (780, 305, 200, 70, "3. Міжлінійний міст\nСпроба замкнути сусідні доріжки\nструмопровідним клеєм", CLR_ALERT_F, CLR_ALERT),
        (780, 395, 200, 85, "4. Незбіг шаблону (Mismatch)\nСтатичний потенціал замість\nдинамічного коду LFSR", CLR_ALERT_F, CLR_ALERT),
    ]

    for x, y, w, h, txt, bg_c, strk_c in violations:
        p.append(fitbox(x, y, w, h, txt, size=11, fill=bg_c, stroke=strk_c, sw=1.2))

    # Стрілки зв'язку
    p.append(arrow(260, 260, 320, 200, color=CLR_SIGNAL, sw=2))
    p.append(arrow(320, 340, 260, 350, color=CLR_WARN, sw=2))
    p.append(arrow(720, 250, 760, 250, color=CLR_ALERT, sw=2))

    return render(os.path.join(OUT, "active-mesh-shield-principle.svg"), W, H, *p)


# ── 3. Архітектура апаратного домену тампера в MCU ────────────────────
def fig_mcu_tamper_domain():
    W, H = 1060, 540
    p = []

    p.append(text(W / 2, 28, "Архітектура ізольованого апаратного домену тампера та зероїзації в MCU", size=16, color=INK, bold=True))

    # Ліва частина: Основний домен VDD (вимикається)
    p.append(rect(40, 60, 360, 440, fill=CLR_HARD_F, stroke=CLR_HARD, sw=1.5, rx=8))
    p.append(text(220, 90, "Основний системний домен (VDD)", size=14, color=INK, bold=True))
    p.append(text(220, 110, "Знеструмлюється при вимкненні пристрою", size=11, color=MUTED, italic=True))

    p.append(fitbox(60, 135, 320, 65, "Головне ядро CPU (ARM Cortex-M)\nВиконує прикладну прошивку,\nстек протоколів та бізнес-логіку", size=11, fill="#ffffff", stroke=CLR_HARD))
    p.append(fitbox(60, 220, 320, 65, "Системна пам'ять (SRAM / Flash)\nМістить оперативні дані,\nбуфери ключів та стек", size=11, fill="#ffffff", stroke=CLR_HARD))
    p.append(fitbox(60, 305, 320, 65, "Криптоприскорювач (AES / PKA)\nАпаратні регістри ключів шифрування\nта модуль розрахунку підписів", size=11, fill="#ffffff", stroke=CLR_HARD))
    p.append(fitbox(60, 390, 320, 90, "Шина керування та переривань\nПри тривозі отримує сигнал Tamper NMI\nдля екстреного очищення CPU RAM", size=11, fill=CLR_ALERT_F, stroke=CLR_ALERT))

    # Права частина: Ізольований домен резервного живлення VBAT
    p.append(rect(440, 60, 580, 440, fill=CLR_BAT_F, stroke=CLR_BAT, sw=2, rx=8))
    p.append(text(730, 90, "Резервний домен безпеки (VBAT — Батарейка RTC)", size=14, color=CLR_BAT, bold=True))
    p.append(text(730, 110, "Активний 24/7/365, споживання < 500 нА навіть без основного живлення", size=11, color=CLR_BAT, italic=True))

    # Внутрішні модулі VBAT
    p.append(fitbox(465, 135, 250, 75, "Контролер тампера (TAMP)\n• Активна сітка LFSR\n• Пасивні входи (NC/NO)\n• Цифровий фільтр брязкоту", size=11, fill="#ffffff", stroke=CLR_SECURE, bold=True))
    p.append(fitbox(745, 135, 250, 75, "Сенсори середовища\n• Монітор темряви (Light)\n• Датчик холоду (< -25°C)\n• Brownout-детектор VBAT", size=11, fill="#ffffff", stroke=CLR_WARN, bold=True))

    p.append(fitbox(465, 235, 530, 90, "Шина миттєвої апаратної зероїзації (Hardware Zeroization Bus)\nАсинхронний комбінаційний сигнал скидання: діє за наносекунди\nбез участі CPU, тактового генератора ядра та Flash-пам'яті!", size=12, fill=CLR_ALERT_F, stroke=CLR_ALERT, bold=True))

    p.append(fitbox(465, 350, 250, 130, "Резервні регістри BKP SRAM\nЗберігають майстер-ключі (Root Keys),\nвектори ініціалізації та лічильники.\nПри тривозі: апаратний розряд\nкомірок у нуль за лічені наносекунди", size=11, fill="#ffffff", stroke=CLR_ALERT))
    p.append(fitbox(745, 350, 250, 130, "Модуль фіксації вторгнення\n• Запис незмивного прапорця TAMPF\n• Фіксація штампа часу RTC\n• Вічне блокування криптомодуля\n(Tamper Lockout / Bricking)", size=11, fill="#ffffff", stroke=CLR_ALERT))

    # Червона стрілка апаратного знищення
    p.append(arrow(465, 280, 380, 280, color=CLR_ALERT, sw=3))
    p.append(arrow(465, 280, 380, 340, color=CLR_ALERT, sw=3))

    return render(os.path.join(OUT, "mcu-tamper-domain-architecture.svg"), W, H, *p)


# ── 4. Таймлайн апаратної та програмної зероїзації ───────────────────
def fig_zeroization_timeline():
    W, H = 1040, 500
    p = []

    p.append(text(W / 2, 28, "Хронологія захисної реакції: від фізичного дотику до повного занулення", size=16, color=INK, bold=True))

    # Головна вісь часу
    p.append(line(80, 230, 960, 230, color=LINE, sw=2))
    p.append(arrow(960, 230, 1000, 230, color=LINE, sw=2))
    p.append(text(990, 255, "Час", size=12, color=MUTED, bold=True))

    steps = [
        (120, "T = 0", "Фізичне розкриття", "Розрив сітки Mesh,\nвідкриття мікроперемикача\nчи сплеск фотоструму", CLR_ALERT_F, CLR_ALERT, 70),
        (330, "T + 10..50 нс", "Апаратна зероїзація", "Асинхронний імпульс;\nрозряд BKP SRAM,\nскидання ключів AES/PKA", CLR_ALERT_F, CLR_ALERT, 300),
        (560, "T + 1..5 мкс", "Tamper NMI / Прокидання", "Процесор переходить у\nнайвище переривання;\nочищення CPU RAM і регістрів", CLR_WARN_F, CLR_WARN, 70),
        (790, "T + 10..50 мкс", "Фіксація та блокування", "Запис чорної скриньки RTC,\nблокування JTAG/SWD,\nперехід у незворотний Lock", CLR_SECURE_F, CLR_SECURE, 300),
    ]

    for cx, t_lbl, title, desc, bg_c, strk_c, y_box in steps:
        # Мітка на осі
        p.append(circle(cx, 230, 7, fill=strk_c, stroke="#ffffff", sw=2))
        p.append(text(cx, 215 if y_box > 200 else 255, t_lbl, size=12, color=strk_c, bold=True))

        # Лінія до плашки
        p.append(line(cx, 230, cx, y_box + (75 if y_box < 200 else 0), color=strk_c, sw=1.5, dash="2,2"))

        # Плашка опису
        p.append(rect(cx - 95, y_box, 190, 85, fill=bg_c, stroke=strk_c, sw=1.5, rx=6))
        p.append(text(cx, y_box + 22, title, size=12, color=strk_c, bold=True))
        p.append(fitbox(cx - 90, y_box + 32, 180, 48, desc, size=10, fill=bg_c, stroke=bg_c))

    return render(os.path.join(OUT, "hardware-zeroization-timeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_tamper_threat_vectors()
    fig_active_mesh_shield()
    fig_mcu_tamper_domain()
    fig_zeroization_timeline()
    print("Всі 4 фігури успішно згенеровано у teci img/")
