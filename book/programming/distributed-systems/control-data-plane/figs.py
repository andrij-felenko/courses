# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=13, pad=9, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Фундаментальний поділ на площину управління і даних ────────────
def fig_control_data_planes_architecture():
    W, H = 1000, 580
    frags = []

    # Заголовок
    frags.append(text(500, 30, "Фундаментальний поділ: Площина управління та Площина даних", size=16, bold=True))

    # Зона Площини управління (зверху)
    frags.append(rect(40, 55, 920, 165, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(65, 80, "ПЛОЩИНА УПРАВЛІННЯ (Control Plane) — Повільний контур оркестрації та консенсусу", size=12, bold=True, color=NEG, anchor="start"))

    frags.append(box(150, 140, "Декларативний стан\n(K8s API, YAML, Raft)\nЦільова топологія", size=11, bold=True, fill="#ffffff", stroke=MUTED, min_w=150))
    frags.append(box(380, 140, "Обчислення топології (RIB)\nАлгоритми маршрутизації\nГенерація правил (FIB)", size=11, bold=True, fill="#eaf0fd", stroke=NEG, min_w=180))
    frags.append(box(620, 140, "Безпека та ідентичність\nЦентр сертифікації (CA)\nРотація mTLS-ключів", size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=180))
    frags.append(box(835, 140, "Моніторинг стану\nВиявлення вузлів\nHealth Checkers", size=11, bold=True, fill="#fff8e7", stroke="#e67e22", min_w=140))

    frags.append(arrow(235, 140, 280, 140, color=NEG, sw=1.5))
    frags.append(arrow(480, 140, 520, 140, color=FIELD, sw=1.5))
    frags.append(arrow(720, 140, 755, 140, color="#e67e22", sw=1.5))

    # Канал між площинами (посередині)
    frags.append(rect(40, 240, 920, 50, fill="#fdfefe", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(500, 260, "Асинхронний канал конфігурації: xDS (gRPC) / Netlink / OpenFlow / BGP (push або pull)", size=11, bold=True, color=INK))
    frags.append(text(500, 278, "Низький пріоритет обробки, дебаунсинг змін, дельта-оновлення, відсутність блокування трафіку", size=10, color=MUTED))

    # Стрілки передачі між зонами
    frags.append(arrow(500, 220, 500, 240, color=NEG, sw=2.0))
    frags.append(arrow(500, 290, 500, 310, color=NEG, sw=2.0))

    # Зона Площини даних (знизу)
    frags.append(rect(40, 310, 920, 235, fill="#fcfdfe", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(65, 335, "ПЛОЩИНА ДАНИХ (Data Plane / Forwarding Plane) — Швидкий шлях обробки кожного запиту/пакета", size=12, bold=True, color=FIELD, anchor="start"))

    # Конвеєр площини даних
    frags.append(box(120, 430, "Вхідний пакет /\nHTTP-запит\n(Мережева черга)", size=10, bold=True, fill="#e8f0fe", stroke=NEG, min_w=110))
    frags.append(box(295, 430, "L4/L7 Парсер заголовків\nНуль алокацій пам'яті\nZero-copy буфери", size=10, bold=True, fill="#ffffff", stroke=MUTED, min_w=150))
    frags.append(box(490, 430, "Локальна таблиця (FIB)\nАтомарний зліпок (RCU)\nПошук без блокувань (O(1))", size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=165))
    frags.append(box(685, 430, "Виконання дій (Actions)\nБалансування, mTLS,\nРейт-ліміти, метрики", size=10, bold=True, fill="#ffffff", stroke=MUTED, min_w=150))
    frags.append(box(870, 430, "Вихідний інтерфейс\nФорвардинг пакета\nLine-rate швидкість", size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=130))

    frags.append(arrow(185, 430, 210, 430, color=LINE, sw=1.8))
    frags.append(arrow(380, 430, 398, 430, color=FIELD, sw=2.0))
    frags.append(arrow(582, 430, 600, 430, color=FIELD, sw=2.0))
    frags.append(arrow(770, 430, 795, 430, color=LINE, sw=1.8))

    # Підписи затримок знизу
    frags.append(text(500, 520, "Характеристики: мікросекундна затримка (μs/ns), лінійна пропускна здатність, повна ізоляція від відмов контролера", size=10, italic=True, color=MUTED))

    return render(os.path.join(IMG, 'control-data-planes-architecture.svg'), W, H, *frags)


# ── Фігура 2: Атомарна неблокуюча підміна зліпка (RCU / Atomic Swap) ─────────
def fig_atomic_snapshot_swap_rcu():
    W, H = 1000, 530
    frags = []

    frags.append(text(500, 30, "Неблокуюча підміна таблиці маршрутизації в Площині даних (Atomic Pointer Swap / RCU)", size=16, bold=True))

    # Контур Control Plane Thread (зліва)
    frags.append(rect(40, 60, 270, 430, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(175, 85, "Потік управління (Control Thread)", size=12, bold=True, color=NEG))

    frags.append(box(175, 145, "1. Отримання оновлення\n(xDS gRPC подія / зміна)", size=11, bold=True, fill="#ffffff", stroke=MUTED, min_w=230))
    frags.append(box(175, 230, "2. Створення нового зліпка\n(Candidate Snapshot B)\nу фоновій пам'яті", size=11, bold=True, fill="#eaf0fd", stroke=NEG, min_w=230))
    frags.append(box(175, 330, "3. Атомарний swap покажчика\nstd::atomic_store_explicit(\n  &active_config, new_snap,\n  std::memory_order_release)", size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=230))
    frags.append(box(175, 440, "4. Очікування епохи читачів\nта безпечне звільнення\nстарого Snapshot A (RCU)", size=10, bold=True, fill="#fff8e7", stroke="#e67e22", min_w=230))

    frags.append(arrow(175, 175, 175, 195, color=NEG, sw=1.5))
    frags.append(arrow(175, 265, 175, 290, color=NEG, sw=1.5))
    frags.append(arrow(175, 375, 175, 405, color="#e67e22", sw=1.5))

    # Центральна область: Атомарний покажчик та зліпки пам'яті
    frags.append(rect(340, 60, 310, 430, fill="#fcfdfe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(495, 85, "Пам'ять конфігурації (Heap / Shared)", size=12, bold=True, color=INK))

    frags.append(box(495, 140, "Атомарний покажчик:\nstd::atomic<ConfigSnapshot*>", size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=250))

    frags.append(box(495, 240, "Активний Snapshot A (v1)\n• Таблиця маршрутів: 10.0.0.0/8\n• Бекенди: [srv1, srv2]\n(Читають старі потоки)", size=10, fill="#ffffff", stroke=MUTED, min_w=250))
    frags.append(box(495, 380, "Новий Snapshot B (v2)\n• Таблиця маршрутів: 10.0.0.0/8\n• Бекенди: [srv1, srv2, srv3]\n(Читають нові потоки)", size=10, fill="#eafaf0", stroke=FIELD, min_w=250))

    frags.append(arrow(495, 170, 495, 200, color=FIELD, sw=2.0))
    frags.append(line(295, 330, 365, 140, color=FIELD, sw=2.0, dash="4 4"))

    # Контур Data Plane Workers (справа)
    frags.append(rect(680, 60, 280, 430, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(820, 85, "Робочі потоки (Data Plane Workers)", size=12, bold=True, color=FIELD))

    frags.append(box(820, 160, "Data Worker 1 (Core 1)\nrcu_read_lock()\nЧитає Snapshot A\nОбробка пакета #1042\nrcu_read_unlock()", size=10, fill="#ffffff", stroke=MUTED, min_w=240))
    frags.append(box(820, 310, "Data Worker 2 (Core 2)\nrcu_read_lock()\nЧитає новий Snapshot B\nОбробка пакета #1043\nrcu_read_unlock()", size=10, fill="#eafaf0", stroke=FIELD, min_w=240))
    frags.append(box(820, 430, "Нуль блокувань (Lock-Free)\nЖоден потік не чекає на м'ютекс!\nЗатримка обробки: < 100 нс", size=10, bold=True, fill="#e8f0fe", stroke=NEG, min_w=240))

    frags.append(arrow(695, 160, 625, 240, color=MUTED, sw=1.5))
    frags.append(arrow(695, 310, 625, 380, color=FIELD, sw=1.8))

    return render(os.path.join(IMG, 'atomic-snapshot-swap-rcu.svg'), W, H, *frags)


# ── Фігура 3: Статична стабільність та ізоляція відмов ────────────────────────
def fig_static_stability_failure_isolation():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 30, "Принцип статичної стабільності: поведінка при відмові Площини управління", size=16, bold=True))

    # Ліва колонка: Антипатерн (Синхронний запит у Control Plane)
    frags.append(rect(40, 60, 440, 430, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(text(260, 85, "АНТИПАТЕРН: Синхронна залежність на шлях трафіку", size=11, bold=True, color=POS))

    frags.append(box(260, 140, "Вхідний запит клієнта\n(100 000 запитів/сек)", size=10, fill="#ffffff", stroke=MUTED, min_w=340))
    frags.append(box(260, 225, "Data Plane зупиняє запит і робить\nСИНХРОННИЙ виклик у Control Plane:\n«Куди маршрутизувати цей пакет?»", size=10, bold=True, fill="#fdecea", stroke=POS, min_w=360))
    frags.append(box(260, 320, "Control Plane падає або зависає\n(OOM / сплеск навантаження / таймаут)", size=10, bold=True, fill="#fdecea", stroke=POS, min_w=360))
    frags.append(box(260, 425, "КАТАСТРОФА СИСТЕМИ:\n• Черги сокетів переповнені (100% Drop)\n• Каскадні таймаути клієнтів\n• Повна недоступність усієї мережі", size=10, bold=True, fill="#f8d7da", stroke=POS, min_w=360))

    frags.append(arrow(260, 165, 260, 195, color=LINE, sw=1.5))
    frags.append(arrow(260, 260, 260, 295, color=POS, sw=2.0))
    frags.append(arrow(260, 350, 260, 385, color=POS, sw=2.0))

    # Права колонка: Патерн (Статична стабільність / Асинхронне кешування)
    frags.append(rect(520, 60, 440, 430, fill="#f6fcf8", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(740, 85, "ЕТАЛОН: Статична стабільність (Static Stability)", size=11, bold=True, color=FIELD))

    frags.append(box(740, 140, "Вхідний запит клієнта\n(100 000 запитів/сек)", size=10, fill="#ffffff", stroke=MUTED, min_w=340))
    frags.append(box(740, 225, "Data Plane обробляє запит ЛОКАЛЬНО:\nПошук у локальній таблиці (FIB / Snapshot)\nНуль мережевих блокувань (Затримка: 15 мкс)", size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=360))
    frags.append(box(740, 320, "Control Plane впав / недоступний 2 години\n(Асинхронний канал gRPC xDS обірвано)", size=10, bold=True, fill="#fff8e7", stroke="#e67e22", min_w=360))
    frags.append(box(740, 425, "СИСТЕМА ПОВНІСТЮ ПРАЦЮЄ (100% Up):\n• Трафік іде за останнім валідним зліпком\n• Клієнти не помічають падіння оркестратора\n• Відновлення без черг смерті (Thundering Herd)", size=10, bold=True, fill="#d1e7dd", stroke=FIELD, min_w=360))

    frags.append(arrow(740, 165, 740, 195, color=LINE, sw=1.5))
    frags.append(arrow(740, 260, 740, 295, color=FIELD, sw=2.0))
    frags.append(arrow(740, 350, 740, 385, color=FIELD, sw=2.0))

    return render(os.path.join(IMG, 'static-stability-failure-isolation.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_control_data_planes_architecture()
    fig_atomic_snapshot_swap_rcu()
    fig_static_stability_failure_isolation()
    print("Figures generated successfully.")
