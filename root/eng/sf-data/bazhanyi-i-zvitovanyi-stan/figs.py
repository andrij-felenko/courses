# -*- coding: utf-8 -*-
import sys
import os

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── Фігура 1: Порівняння імперативного та декларативного керування ─────────────
def fig_imperative_vs_declarative_control():
    W, H = 1000, 520
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Імперативні команди проти декларативного узгодження стану", size=15, color=INK, bold=True, anchor="start"))

    # Ліва панель: Імперативні RPC-виклики (Крах при збоях зв'язку)
    left_x = 40
    p.append(rect(left_x, 60, 435, 430, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    p.append(text(left_x + 217, 85, "1. Імперативний підхід (RPC / Direct Commands)", size=12.5, color="#b91c1c", bold=True))
    
    # Кроки імперативного виклику
    p.append(rect(left_x + 20, 105, 395, 45, fill="#fee2e2", stroke="#fca5a5", sw=1.2, rx=4))
    p.append(text(left_x + 217, 125, "Керівний сервіс (Cloud / API)", size=11, color=INK, bold=True))
    p.append(text(left_x + 217, 140, "POST /device/setSpeed(120)", size=10, color="#b91c1c", bold=True))

    p.append(arrow(left_x + 217, 150, left_x + 217, 195, color="#b91c1c", sw=2.0))
    p.append(text(left_x + 225, 175, "Прямий мережевий виклик", size=10, color="#b91c1c", anchor="start"))

    # Мережевий розрив
    p.append(rect(left_x + 20, 195, 395, 55, fill="#ffffff", stroke="#f87171", sw=1.2, rx=4))
    p.append(text(left_x + 217, 215, "Мережева нестабільність / Офлайн", size=11, color="#991b1b", bold=True))
    p.append(text(left_x + 217, 235, "Таймаут клієнта -> Повторна відправка -> Завислий пакет", size=10, color="#7f1d1d"))

    p.append(arrow(left_x + 217, 250, left_x + 217, 290, color="#b91c1c", sw=2.0))

    # Локальний пристрій
    p.append(rect(left_x + 20, 290, 395, 75, fill="#fee2e2", stroke="#fca5a5", sw=1.2, rx=4))
    p.append(text(left_x + 217, 310, "Кінцевий вузол / IoT пристрій", size=11, color=INK, bold=True))
    p.append(text(left_x + 217, 330, "1. Отримав локальну команду оператора: setSpeed(0)", size=10, color="#15803d", bold=True))
    p.append(text(left_x + 217, 348, "2. Згодом долетів запізнілий пакет з хмари: setSpeed(120)", size=10, color="#b91c1c", bold=True))

    # Висновок зліва
    p.append(rect(left_x + 20, 380, 395, 95, fill="#ffffff", stroke="#dc2626", sw=1.5, rx=4))
    p.append(text(left_x + 217, 402, "Наслідки імперативної моделі:", size=10.5, color="#b91c1c", bold=True))
    p.append(text(left_x + 35, 422, "• Перезапис свіжих дій старими пакетами (Out-of-order)", size=10, color=INK, anchor="start"))
    p.append(text(left_x + 35, 442, "• Блокування клієнта під час відсутності зв'язку", size=10, color=INK, anchor="start"))
    p.append(text(left_x + 35, 462, "• Невизначений стан при падінні посеред ланцюжка", size=10, color=INK, anchor="start"))

    # Права панель: Декларативне узгодження (Desired vs Reported State)
    right_x = 525
    p.append(rect(right_x, 60, 435, 430, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    p.append(text(right_x + 217, 85, "2. Декларативний підхід (Desired vs Reported)", size=12.5, color="#15803d", bold=True))

    # Хмарний стан
    p.append(rect(right_x + 20, 105, 395, 65, fill="#dcfce7", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(right_x + 217, 125, "Сховище стану (Device Shadow / etcd)", size=11, color=INK, bold=True))
    p.append(text(right_x + 35, 145, "Desired:  { \"speed\": 120, \"v\": 42 }", size=10, color="#1d4ed8", bold=True, anchor="start"))
    p.append(text(right_x + 35, 160, "Reported: { \"speed\": 0,   \"v\": 41 }", size=10, color="#047857", bold=True, anchor="start"))

    # Двонаправлений потік
    p.append(arrow(right_x + 120, 170, right_x + 120, 230, color="#1d4ed8", sw=2.0))
    p.append(text(right_x + 110, 200, "Delta / Pull Desired", size=10, color="#1d4ed8", anchor="end", bold=True))

    p.append(arrow(right_x + 310, 230, right_x + 310, 170, color="#047857", sw=2.0))
    p.append(text(right_x + 320, 200, "Publish Reported", size=10, color="#047857", anchor="start", bold=True))

    # Автономний контролер / вузол
    p.append(rect(right_x + 20, 230, 395, 115, fill="#ffffff", stroke="#86efac", sw=1.2, rx=4))
    p.append(text(right_x + 217, 250, "Автономний Reconciler / Контролер вузла", size=11, color=INK, bold=True))
    p.append(text(right_x + 35, 270, "1. Обчислення дельти: Delta = Desired - Reported (+120)", size=10, color=INK, anchor="start"))
    p.append(text(right_x + 35, 290, "2. Ідемпотентна дія: Плавне розігнати двигун до 120", size=10, color=INK, anchor="start"))
    p.append(text(right_x + 35, 310, "3. Фіксація факту: Підтвердити новий Reported: 120", size=10, color=INK, anchor="start"))
    p.append(text(right_x + 35, 330, "4. Дрейф зникає: Delta = 0 (Стан узгоджено)", size=10, color="#15803d", bold=True, anchor="start"))

    # Висновок справа
    p.append(rect(right_x + 20, 360, 395, 115, fill="#dcfce7", stroke="#22c55e", sw=1.5, rx=4))
    p.append(text(right_x + 217, 380, "Переваги декларативної моделі:", size=10.5, color="#15803d", bold=True))
    p.append(text(right_x + 35, 400, "• Асинхронність: запис бажаного стану не чекає на пристрій", size=10, color=INK, anchor="start"))
    p.append(text(right_x + 35, 420, "• Стійкість до розривів: зв'язок відновився -> дельта застосувалась", size=10, color=INK, anchor="start"))
    p.append(text(right_x + 35, 440, "• Самозцілення: локальний збій чи дрейф виправляється циклом", size=10, color=INK, anchor="start"))
    p.append(text(right_x + 35, 460, "• Ідемпотентність: повторний запуск не змінює результат", size=10, color="#15803d", bold=True, anchor="start"))

    render(os.path.join(OUT, "imperative-vs-declarative-control.svg"), W, H, *p)

# ── Фігура 2: Структура документа Digital Twin / Shadow Document ─────────────
def fig_device_shadow_three_way_split():
    W, H = 1000, 500
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Анатомія документа цифрового двійника (Device Shadow Document)", size=15, color=INK, bold=True, anchor="start"))

    # Три головні блоки
    col_w = 285
    col_h = 320
    y_top = 70

    # Блок 1: Desired State (Специфікація)
    x1 = 40
    p.append(rect(x1, y_top, col_w, col_h, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    p.append(text(x1 + col_w/2, y_top + 25, "state.desired (Бажаний)", size=12, color="#1e40af", bold=True))
    p.append(text(x1 + col_w/2, y_top + 45, "Джерело правди: Клієнт / Хмара", size=10, color="#64748b"))

    p.append(rect(x1 + 15, y_top + 60, col_w - 30, 170, fill="#ffffff", stroke="#93c5fd", sw=1.0, rx=4))
    p.append(text(x1 + 25, y_top + 80, "{", size=10, color=INK, anchor="start"))
    p.append(text(x1 + 35, y_top + 100, "\"power\": \"ON\",", size=10, color="#1e40af", bold=True, anchor="start"))
    p.append(text(x1 + 35, y_top + 120, "\"target_temp\": 22.5,", size=10, color="#1e40af", bold=True, anchor="start"))
    p.append(text(x1 + 35, y_top + 140, "\"fan_mode\": \"AUTO\",", size=10, color="#1e40af", bold=True, anchor="start"))
    p.append(text(x1 + 35, y_top + 160, "\"led_brightness\": 80,", size=10, color="#1e40af", bold=True, anchor="start"))
    p.append(text(x1 + 35, y_top + 180, "\"filter_alert\": null", size=10, color="#dc2626", bold=True, anchor="start"))
    p.append(text(x1 + 25, y_top + 200, "}", size=10, color=INK, anchor="start"))
    p.append(text(x1 + col_w/2, y_top + 220, "(null = видалення властивості)", size=9.5, color="#dc2626"))

    p.append(rect(x1 + 15, y_top + 245, col_w - 30, 60, fill="#dbeafe", stroke="#bfdbfe", sw=1.0, rx=4))
    p.append(text(x1 + col_w/2, y_top + 265, "Встановлюється додатком,", size=10, color="#1e40af"))
    p.append(text(x1 + col_w/2, y_top + 285, "оператором або розкладом", size=10, color="#1e40af"))

    # Блок 2: Reported State (Телеметрія)
    x2 = 355
    p.append(rect(x2, y_top, col_w, col_h, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    p.append(text(x2 + col_w/2, y_top + 25, "state.reported (Звітований)", size=12, color="#15803d", bold=True))
    p.append(text(x2 + col_w/2, y_top + 45, "Джерело правди: Фізичний вузол", size=10, color="#64748b"))

    p.append(rect(x2 + 15, y_top + 60, col_w - 30, 170, fill="#ffffff", stroke="#86efac", sw=1.0, rx=4))
    p.append(text(x2 + 25, y_top + 80, "{", size=10, color=INK, anchor="start"))
    p.append(text(x2 + 35, y_top + 100, "\"power\": \"ON\",", size=10, color="#15803d", bold=True, anchor="start"))
    p.append(text(x2 + 35, y_top + 120, "\"target_temp\": 20.0,", size=10, color="#dc2626", bold=True, anchor="start"))
    p.append(text(x2 + 35, y_top + 140, "\"fan_mode\": \"AUTO\",", size=10, color="#15803d", bold=True, anchor="start"))
    p.append(text(x2 + 35, y_top + 160, "\"led_brightness\": 50,", size=10, color="#dc2626", bold=True, anchor="start"))
    p.append(text(x2 + 35, y_top + 180, "\"firmware_v\": \"2.4.1\"", size=10, color="#15803d", bold=True, anchor="start"))
    p.append(text(x2 + 25, y_top + 200, "}", size=10, color=INK, anchor="start"))
    p.append(text(x2 + col_w/2, y_top + 220, "(лише реальний стан сенсорів)", size=9.5, color="#15803d"))

    p.append(rect(x2 + 15, y_top + 245, col_w - 30, 60, fill="#dcfce7", stroke="#bbf7d0", sw=1.0, rx=4))
    p.append(text(x2 + col_w/2, y_top + 265, "Публікується пристроєм", size=10, color="#15803d"))
    p.append(text(x2 + col_w/2, y_top + 285, "після зміни чи опитування", size=10, color="#15803d"))

    # Блок 3: Computed Delta (Обчислена різниця)
    x3 = 675
    p.append(rect(x3, y_top, col_w, col_h, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(x3 + col_w/2, y_top + 25, "state.delta (Різниця / Дрейф)", size=12, color="#b45309", bold=True))
    p.append(text(x3 + col_w/2, y_top + 45, "Обчислюється сервером автоматично", size=10, color="#64748b"))

    p.append(rect(x3 + 15, y_top + 60, col_w - 30, 170, fill="#ffffff", stroke="#fde68a", sw=1.0, rx=4))
    p.append(text(x3 + 25, y_top + 80, "{", size=10, color=INK, anchor="start"))
    p.append(text(x3 + 35, y_top + 100, "// power та fan_mode збігаються", size=9.5, color="#94a3b8", anchor="start"))
    p.append(text(x3 + 35, y_top + 120, "\"target_temp\": 22.5,", size=10, color="#b45309", bold=True, anchor="start"))
    p.append(text(x3 + 35, y_top + 140, "\"led_brightness\": 80", size=10, color="#b45309", bold=True, anchor="start"))
    p.append(text(x3 + 35, y_top + 160, "// filter_alert видалено", size=9.5, color="#94a3b8", anchor="start"))
    p.append(text(x3 + 25, y_top + 180, "}", size=10, color=INK, anchor="start"))
    p.append(text(x3 + col_w/2, y_top + 215, "Delta = Desired \\ Reported", size=10.5, color="#b45309", bold=True))

    p.append(rect(x3 + 15, y_top + 245, col_w - 30, 60, fill="#fef3c7", stroke="#fde68a", sw=1.0, rx=4))
    p.append(text(x3 + col_w/2, y_top + 265, "Надсилається пристрою у топік:", size=9.5, color="#b45309"))
    p.append(text(x3 + col_w/2, y_top + 285, ".../shadow/update/delta", size=9.5, color="#b45309", bold=True))

    # Нижня плашка: Метадані та Оптимістичне блокування
    p.append(rect(40, 410, 920, 70, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(60, 432, "Службові метадані документа (Metadata & Concurrency Control):", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(60, 452, "• version: 1042 (монотонно зростаючий цілочисельний лічильник для детекції колізій та Optimistic Locking)", size=10, color="#334155", anchor="start"))
    p.append(text(60, 468, "• timestamp: 1714567890 (час останньої модифікації кожної окремої гілки та поля в епосі UNIX)", size=10, color="#334155", anchor="start"))

    render(os.path.join(OUT, "device-shadow-three-way-split.svg"), W, H, *p)

# ── Фігура 3: Життєвий цикл циклу узгодження (Reconciliation Loop) ─────────────
def fig_reconciliation_state_machine():
    W, H = 1000, 500
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Життєвий цикл циклу узгодження (The Reconciliation / Controller Loop)", size=15, color=INK, bold=True, anchor="start"))

    # 4 етапи циклу узгодження по колу / прямокутнику
    box_w, box_h = 200, 130
    
    # 1. Observe (Спостереження)
    b1_x, b1_y = 60, 80
    p.append(rect(b1_x, b1_y, box_w, box_h, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    p.append(text(b1_x + box_w/2, b1_y + 25, "1. OBSERVE (Опитування)", size=11.5, color="#1e40af", bold=True))
    p.append(text(b1_x + 15, b1_y + 50, "• Читання Desired (etcd/API)", size=9.5, color=INK, anchor="start"))
    p.append(text(b1_x + 15, b1_y + 70, "• Збір телеметрії Reported", size=9.5, color=INK, anchor="start"))
    p.append(text(b1_x + 15, b1_y + 90, "• Перевірка версій ревізій", size=9.5, color=INK, anchor="start"))
    p.append(text(b1_x + 15, b1_y + 110, "• Watch-подія або таймер", size=9.5, color="#1e40af", anchor="start"))

    # Стрілка 1 -> 2
    p.append(arrow(b1_x + box_w, b1_y + box_h/2, 290, b1_y + box_h/2, color="#2563eb", sw=2.0))
    p.append(text(275, b1_y + box_h/2 - 10, "Стан отримано", size=9.5, color="#2563eb", bold=True))

    # 2. Analyze & Diff (Аналіз і Дельта)
    b2_x, b2_y = 300, 80
    p.append(rect(b2_x, b2_y, box_w, box_h, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(b2_x + box_w/2, b2_y + 25, "2. DIFF (Виявлення дрейфу)", size=11.5, color="#b45309", bold=True))
    p.append(text(b2_x + 15, b2_y + 50, "• Δ = Desired - Reported", size=9.5, color=INK, anchor="start"))
    p.append(text(b2_x + 15, b2_y + 70, "• Фільтр шуму та гістерезис", size=9.5, color=INK, anchor="start"))
    p.append(text(b2_x + 15, b2_y + 90, "• Перевірка: чи Δ == 0?", size=9.5, color=INK, anchor="start"))
    p.append(text(b2_x + 15, b2_y + 110, "• Визначення невідповідностей", size=9.5, color="#b45309", anchor="start"))

    # Стрілка 2 -> 3
    p.append(arrow(b2_x + box_w, b2_y + box_h/2, 530, b2_y + box_h/2, color="#d97706", sw=2.0))
    p.append(text(515, b2_y + box_h/2 - 10, "Є дрейф (Δ ≠ 0)", size=9.5, color="#d97706", bold=True))

    # 3. Plan & Actuate (Дія)
    b3_x, b3_y = 540, 80
    p.append(rect(b3_x, b3_y, box_w, box_h, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=6))
    p.append(text(b3_x + box_w/2, b3_y + 25, "3. ACTUATE (Виконання дії)", size=11.5, color="#b91c1c", bold=True))
    p.append(text(b3_x + 15, b3_y + 50, "• Генерація плану переходів", size=9.5, color=INK, anchor="start"))
    p.append(text(b3_x + 15, b3_y + 70, "• Ідемпотентна мутація", size=9.5, color=INK, anchor="start"))
    p.append(text(b3_x + 15, b3_y + 90, "• Керування актуатором / API", size=9.5, color=INK, anchor="start"))
    p.append(text(b3_x + 15, b3_y + 110, "• Обробка таймаутів і помилок", size=9.5, color="#b91c1c", anchor="start"))

    # Стрілка 3 -> 4
    p.append(arrow(b3_x + box_w, b3_y + box_h/2, 770, b3_y + box_h/2, color="#ef4444", sw=2.0))
    p.append(text(755, b3_y + box_h/2 - 10, "Дію виконано", size=9.5, color="#ef4444", bold=True))

    # 4. Report & Ingest (Звіт та Оновлення)
    b4_x, b4_y = 780, 80
    p.append(rect(b4_x, b4_y, box_w, box_h, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    p.append(text(b4_x + box_w/2, b4_y + 25, "4. REPORT (Фіксація звіту)", size=11.5, color="#15803d", bold=True))
    p.append(text(b4_x + 15, b4_y + 50, "• Зчитування нового стану", size=9.5, color=INK, anchor="start"))
    p.append(text(b4_x + 15, b4_y + 70, "• Оновлення Reported в базі", size=9.5, color=INK, anchor="start"))
    p.append(text(b4_x + 15, b4_y + 90, "• Інкремент version++", size=9.5, color=INK, anchor="start"))
    p.append(text(b4_x + 15, b4_y + 110, "• Зменшення дрейфу до нуля", size=9.5, color="#15803d", anchor="start"))

    # Зворотні зв'язки (Feedback Loops)
    # З 4 повертається в 1 (Завершення циклу)
    p.append('<path d="M 880 210 L 880 270 L 160 270 L 160 210" stroke="#16a34a" stroke-width="2.0" stroke-dasharray="6,4" fill="none"/>')
    p.append(circle(880, 210, 3, fill="#16a34a"))
    p.append(arrow(160, 230, 160, 215, color="#16a34a", sw=2.0))
    p.append(text(500, 260, "Наступна ітерація: перевірка рівноваги (Level-Triggered)", size=10, color="#15803d", bold=True))

    # Якщо дельта нульова (зі стану 2 повертаємось в стан очікування)
    p.append('<path d="M 400 210 L 400 240 L 190 240 L 190 210" stroke="#d97706" stroke-width="1.5" fill="none"/>')
    p.append(circle(400, 210, 3, fill="#d97706"))
    p.append(arrow(190, 230, 190, 215, color="#d97706", sw=1.5))
    p.append(text(295, 235, "Δ = 0 (Дрейфу немає)", size=9.5, color="#d97706"))

    # Нижній блок: Помилки та Експоненційний Backoff
    p.append(rect(60, 310, 880, 160, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(80, 335, "Обробка крайових випадків та відмовостійкість циклу узгодження:", size=11, color=INK, bold=True, anchor="start"))
    
    p.append(rect(80, 350, 260, 100, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=4))
    p.append(text(210, 370, "1. Рівневий тригер (Level-Triggered)", size=10, color="#1e40af", bold=True))
    p.append(text(95, 392, "Цикл реагує не на перепади", size=9.5, color=INK, anchor="start"))
    p.append(text(95, 408, "подій (Edge), а на поточний", size=9.5, color=INK, anchor="start"))
    p.append(text(95, 424, "наявний рівень різниці (Δ).", size=9.5, color=INK, anchor="start"))
    p.append(text(95, 440, "Втрата події не ламає систему.", size=9.5, color="#1e40af", bold=True, anchor="start"))

    p.append(rect(370, 350, 260, 100, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=4))
    p.append(text(500, 370, "2. Exponential Backoff & Jitter", size=10, color="#b45309", bold=True))
    p.append(text(385, 392, "При збої зв'язку або актуатора", size=9.5, color=INK, anchor="start"))
    p.append(text(385, 408, "затримка зростає: 2^k * t + r.", size=9.5, color=INK, anchor="start"))
    p.append(text(385, 424, "Випадковий джитер запобігає", size=9.5, color=INK, anchor="start"))
    p.append(text(385, 440, "хвилям узгодження (Thundering Herd).", size=9.5, color="#b45309", bold=True, anchor="start"))

    p.append(rect(660, 350, 260, 100, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=4))
    p.append(text(790, 370, "3. Детекція флапінгу (Anti-Flap)", size=10, color="#b91c1c", bold=True))
    p.append(text(675, 392, "Якщо бажаний стан швидко скаче", size=9.5, color=INK, anchor="start"))
    p.append(text(675, 408, "туди-сюди (осциляція), вмикається", size=9.5, color=INK, anchor="start"))
    p.append(text(675, 424, "Rate Limiting та deadband-зона,", size=9.5, color=INK, anchor="start"))
    p.append(text(675, 440, "щоб зберегти ресурс заліза.", size=9.5, color="#b91c1c", bold=True, anchor="start"))

    render(os.path.join(OUT, "reconciliation-state-machine.svg"), W, H, *p)

# ── Фігура 4: Оптимістичне блокування та запобігання гонкам ───────────────────
def fig_optimistic_versioning_race():
    W, H = 1000, 500
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d0d7de", sw=1.2, rx=8))
    p.append(text(40, 38, "Запобігання гонкам та дрейфу: Optimistic Concurrency Control (OCC)", size=15, color=INK, bold=True, anchor="start"))

    # Часова шкала трьох акторів
    y_axis = 80
    
    # Актор 1: Мобільний додаток (Клієнт А)
    p.append(rect(60, y_axis, 240, 40, fill="#eff6ff", stroke="#3b82f6", sw=1.2, rx=4))
    p.append(text(180, y_axis + 25, "Клієнт A (Мобільний додаток)", size=11, color="#1e40af", bold=True))

    # Актор 2: Сховище Shadow (Центральний брокер)
    p.append(rect(380, y_axis, 240, 40, fill="#f8fafc", stroke="#64748b", sw=1.2, rx=4))
    p.append(text(500, y_axis + 25, "Центральний Shadow (Брокер)", size=11, color=INK, bold=True))

    # Актор 3: Хмарний автоматизатор (Клієнт B)
    p.append(rect(700, y_axis, 240, 40, fill="#fffbeb", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(820, y_axis + 25, "Клієнт B (Хмарний планувальник)", size=11, color="#b45309", bold=True))

    # Вертикальні лінії життя (Lifelines)
    p.append(line(180, y_axis + 40, 180, 460, color="#94a3b8", sw=1.2, dash="4,4"))
    p.append(line(500, y_axis + 40, 500, 460, color="#64748b", sw=1.5))
    p.append(line(820, y_axis + 40, 820, 460, color="#94a3b8", sw=1.2, dash="4,4"))

    # Крок 1: Початковий стан у базі
    p.append(rect(430, 140, 140, 30, fill="#e2e8f0", stroke="#cbd5e1", sw=1.0, rx=3))
    p.append(text(500, 160, "version: 10, temp: 20", size=9.5, color=INK, bold=True))

    # Крок 2: Обидва читають стан v:10
    p.append(arrow(500, 175, 180, 190, color="#2563eb", sw=1.5))
    p.append(text(340, 180, "Read (v: 10)", size=9.5, color="#2563eb"))

    p.append(arrow(500, 175, 820, 190, color="#d97706", sw=1.5))
    p.append(text(660, 180, "Read (v: 10)", size=9.5, color="#d97706"))

    # Крок 3: Клієнт А відправляє оновлення першим
    p.append(arrow(180, 220, 500, 240, color="#2563eb", sw=2.0))
    p.append(text(340, 225, "UPDATE desired.temp=22 (if v==10)", size=9.5, color="#2563eb", bold=True))

    # Центральний вузол приймає оновлення А
    p.append(rect(410, 245, 180, 40, fill="#dcfce7", stroke="#22c55e", sw=1.2, rx=4))
    p.append(text(500, 262, "Успіх: v=10 збігається!", size=9.5, color="#15803d", bold=True))
    p.append(text(500, 277, "Записано temp=22, version -> 11", size=9.5, color="#15803d"))

    p.append(arrow(500, 290, 180, 305, color="#16a34a", sw=1.5))
    p.append(text(340, 295, "200 OK (new v: 11)", size=9.5, color="#16a34a", bold=True))

    # Крок 4: Клієнт B надсилає запізніле оновлення з v:10
    p.append(arrow(820, 310, 500, 335, color="#ef4444", sw=2.0))
    p.append(text(660, 320, "UPDATE desired.temp=25 (if v==10)", size=9.5, color="#ef4444", bold=True))

    # Центральний вузол відхиляє оновлення B (Конфлікт версій)
    p.append(rect(410, 340, 180, 40, fill="#fee2e2", stroke="#ef4444", sw=1.5, rx=4))
    p.append(text(500, 357, "ВІДХИЛЕНО: Conflict!", size=9.5, color="#b91c1c", bold=True))
    p.append(text(500, 372, "Поточна v=11 != очікувана v=10", size=9.5, color="#b91c1c"))

    p.append(arrow(500, 385, 820, 405, color="#dc2626", sw=1.8))
    p.append(text(660, 395, "409 Conflict (stale version)", size=9.5, color="#dc2626", bold=True))

    # Крок 5: Клієнт B повторно читає і зливає зміни
    p.append(rect(710, 415, 220, 40, fill="#fffbeb", stroke="#fde68a", sw=1.0, rx=3))
    p.append(text(820, 432, "Клієнт B читає v:11,", size=9.5, color="#b45309"))
    p.append(text(820, 447, "перераховує бізнес-правило", size=9.5, color="#b45309", bold=True))

    render(os.path.join(OUT, "optimistic-versioning-race.svg"), W, H, *p)

def main():
    fig_imperative_vs_declarative_control()
    fig_device_shadow_three_way_split()
    fig_reconciliation_state_machine()
    fig_optimistic_versioning_race()
    print("All figures generated successfully.")

if __name__ == "__main__":
    main()
