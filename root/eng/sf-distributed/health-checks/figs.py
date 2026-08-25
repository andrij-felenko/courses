# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=11, pad=8, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Життєвий цикл і розмежування проб ─────────────────────────────
def fig_lifecycle_probes():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 28, "Розмежування проб у життєвому циклі контейнера: Startup, Liveness та Readiness", size=15, bold=True))

    # Секція 1: Startup Probe (Фаза ініціалізації)
    frags.append(rect(25, 55, 290, 440, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(170, 82, "1. Проба запуску (Startup Probe)", size=12, bold=True, color=NEG))
    
    frags.append(box(170, 140, "Старт процесу\nЗавантаження конфігів,\nпрогрів JIT, виділення пулів", size=10, fill="#ffffff", stroke=MUTED, min_w=240))
    frags.append(arrow(170, 185, 170, 220, color=MUTED, sw=1.5))

    frags.append(box(170, 255, "Startup Probe: перевірка\nчи завершилася ініціалізація\n(блокує liveness/readiness)", size=10, bold=True, fill="#e8f0ff", stroke=NEG, min_w=250))
    
    frags.append(arrow(170, 295, 170, 335, color=POS, sw=1.5))
    frags.append(box(170, 370, "Збій таймауту старту:\nперевищено failureThreshold\n→ SIGKILL і перезапуск", size=10, fill="#fdecea", stroke=POS, min_w=240))
    
    frags.append(rect(35, 420, 270, 65, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(170, 440, [
        "Призначення: захист повільних застосунків",
        "від передчасного вбивства liveness-пробою",
        "під час холодного старту."
    ], size=9, color=INK))

    # Секція 2: Liveness Probe (Фаза виявлення глухих кутів)
    frags.append(rect(340, 55, 305, 440, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(492, 82, "2. Проба живості (Liveness Probe)", size=12, bold=True, color=POS))

    frags.append(box(492, 140, "Процес працює\nОбробка запитів,\nфонові задачі", size=10, fill="#ffffff", stroke=MUTED, min_w=240))
    frags.append(arrow(492, 185, 492, 220, color=MUTED, sw=1.5))

    frags.append(box(492, 255, "Liveness Probe: перевірка\nчи живий внутрішній цикл\n(deadlock, пам'ять, зависання)", size=10, bold=True, fill="#fff5f5", stroke=POS, min_w=260))

    frags.append(arrow(492, 295, 492, 335, color=POS, sw=1.5))
    frags.append(box(492, 370, "Непоправний збій процесу:\nLiveness повертає 500 / Timeout\n→ Оркестратор рестартує под", size=10, fill="#fdecea", stroke=POS, min_w=250))

    frags.append(rect(350, 420, 285, 65, fill="#fff5f5", stroke=POS, sw=1, rx=4))
    frags.append(mtext(492, 440, [
        "Суворе правило: Liveness ніколи не перевіряє",
        "зовнішні залежності! Рестарт має сенс лише",
        "коли зламано сам внутрішній процес."
    ], size=9, color=POS))

    # Секція 3: Readiness Probe (Фаза маршрутизації трафіку)
    frags.append(rect(670, 55, 305, 440, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(822, 82, "3. Проба готовності (Readiness Probe)", size=12, bold=True, color=FIELD))

    frags.append(box(822, 140, "Готовий до трафіку\nЕкземпляр включено в ротацію\nбалансувальника (Endpoints)", size=10, fill="#eafaf0", stroke=FIELD, min_w=250))
    frags.append(arrow(822, 185, 822, 220, color=FIELD, sw=1.5))

    frags.append(box(822, 255, "Readiness Probe: перевірка\nздатності приймати запити\n(пул з'єднань, черга, drain)", size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=260))

    frags.append(arrow(822, 295, 822, 335, color="#e67e22", sw=1.5))
    frags.append(box(822, 370, "Тимчасова неготовність:\nReadiness повертає 503\n→ Вилучення з балансувальника (без рестарту!)", size=10, fill="#fff8e1", stroke="#e67e22", min_w=275))

    frags.append(rect(680, 420, 285, 65, fill="#f0fff4", stroke=FIELD, sw=1, rx=4))
    frags.append(mtext(822, 440, [
        "Суворе правило: збій готовності НЕ вбиває",
        "процес. Він дає час відновитися (очистити чергу,",
        "дочекатися БД, завершити прогрів кешу)."
    ], size=9, color=FIELD))

    return render(os.path.join(IMG, 'liveness-vs-readiness-lifecycle.svg'), W, H, *frags)


# ── Фігура 2: Каскадний колапс від глибоких перевірок ────────────────────────
def fig_deep_health_check_cascade():
    W, H = 980, 480
    frags = []

    frags.append(text(490, 28, "Каскадний колапс кластера через «глибоку» перевірку живості (Deep Health Check)", size=15, bold=True))

    # Крок 1: Нормальний стан і спільна залежність
    frags.append(rect(30, 55, 435, 400, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(247, 82, "1. Помилкова архітектура (Deep Probe)", size=13, bold=True, color=POS))

    frags.append(box(130, 150, "Pod 1 (Web)\n/healthz -> DB ping", size=10, fill="#ffffff", stroke=MUTED, min_w=140))
    frags.append(box(130, 230, "Pod 2 (Web)\n/healthz -> DB ping", size=10, fill="#ffffff", stroke=MUTED, min_w=140))
    frags.append(box(130, 310, "Pod 3 (Web)\n/healthz -> DB ping", size=10, fill="#ffffff", stroke=MUTED, min_w=140))

    frags.append(box(370, 230, "Спільна СУБД\n(PostgreSQL / Redis)\nСплеск затримки (CPU 99%)", size=11, bold=True, fill="#fff5f5", stroke=POS, min_w=160))

    frags.append(arrow(205, 150, 285, 210, color=POS, sw=1.5))
    frags.append(arrow(205, 230, 285, 230, color=POS, sw=1.5))
    frags.append(arrow(205, 310, 285, 250, color=POS, sw=1.5))

    frags.append(rect(45, 365, 405, 75, fill="#fff5f5", stroke=POS, sw=1, rx=4))
    frags.append(mtext(247, 385, [
        "Помилка: /healthz перевіряє спільну базу даних.",
        "Коли база тимчасово сповільнюється, проби на ВСІХ подах",
        "одночасно перевищують таймаут (1 секунда)."
    ], size=9.5, color=POS))

    # Крок 2: Каскад рестартів і колапс
    frags.append(rect(495, 55, 455, 400, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(722, 82, "2. Каскадний колапс і петля CrashLoopBackOff", size=13, bold=True, color=POS))

    frags.append(box(595, 140, "Оркестратор (K8s)\nLiveness failed\nОдночасний SIGKILL", size=10, bold=True, fill="#fdecea", stroke=POS, min_w=160))
    frags.append(box(845, 140, "Усі 100 подів убито!\n0 подів у ротації\n100% 503 для клієнтів", size=10, bold=True, fill="#fdecea", stroke=POS, min_w=150))

    frags.append(arrow(680, 140, 765, 140, color=POS, sw=2))

    frags.append(box(722, 250, "Рестарт 100 подів одночасно:\nШквал відкриття TCP-з'єднань на СУБД\n(Thundering Herd на пулі конектів)", size=10.5, bold=True, fill="#fff5f5", stroke=POS, min_w=380))

    frags.append(arrow(722, 185, 722, 215, color=POS, sw=1.5))
    frags.append(arrow(722, 285, 722, 320, color=POS, sw=1.5))

    frags.append(box(722, 355, "Метастабільна відмова:\nСУБД остаточно лягає під шквалом підключень.\nКластер назавжди застрягає в CrashLoopBackOff.", size=10, bold=True, fill="#fdecea", stroke=POS, min_w=400))

    frags.append(rect(510, 398, 425, 45, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    frags.append(text(722, 422, "Висновок: перевірка має залежати лише від локального стану процесу.", size=9.5, bold=True, color=INK))

    return render(os.path.join(IMG, 'deep-health-check-cascade.svg'), W, H, *frags)


# ── Фігура 3: Активне зондування проти пасивного спостереження ───────────────
def fig_active_vs_passive():
    W, H = 980, 480
    frags = []

    frags.append(text(490, 28, "Активне зондування (Active Probing) проти Пасивного спостереження (Outlier Detection)", size=15, bold=True))

    # Секція 1: Активне зондування (Active Synthetic Probing)
    frags.append(rect(30, 55, 440, 400, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(250, 82, "1. Активне зондування (Active Probes / Polling)", size=12, bold=True, color=NEG))

    frags.append(box(120, 170, "Балансувальник /\nОркестратор\n(Таймер кожні 5 с)", size=10, bold=True, fill="#ffffff", stroke=MUTED, min_w=130))
    frags.append(box(370, 130, "Бекенд A\n/healthz -> 200 OK", size=10, fill="#eafaf0", stroke=FIELD, min_w=120))
    frags.append(box(370, 220, "Бекенд B\n/healthz -> Timeout", size=10, fill="#fdecea", stroke=POS, min_w=120))

    frags.append(arrow(190, 155, 305, 135, color=FIELD, sw=1.5))
    frags.append(text(245, 135, "GET /healthz", size=9, color=FIELD))

    frags.append(arrow(190, 185, 305, 215, color=POS, sw=1.5))
    frags.append(text(245, 215, "Синтетичний запит", size=9, color=POS))

    frags.append(rect(45, 280, 410, 160, fill="#f4f6f8", stroke=MUTED, sw=1, rx=4))
    frags.append(mtext(250, 305, [
        "Характеристики активного зондування:",
        "• Штучний трафік: N балансувальників × M серверів",
        "  породжують постійне фонове навантаження.",
        "• Ризик фальшивого позитиву: /healthz повертає 200,",
        "  але реальні бізнес-маршрути падають через deadlock.",
        "• Періодичність: виявляє аварію лише після чергового",
        "  інтервалу таймера (затримка виявлення = periodSeconds)."
    ], size=9.5, color=INK))

    # Секція 2: Пасивне виявлення аномалій (Outlier Detection)
    frags.append(rect(490, 55, 460, 400, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(720, 82, "2. Пасивне спостереження (Outlier Detection / Envoy)", size=12, bold=True, color=FIELD))

    frags.append(box(575, 170, "Зворотний проксі /\nEnvoy Sidecar\n(Аналіз реальних RPC)", size=10, bold=True, fill="#ffffff", stroke=MUTED, min_w=140))
    frags.append(box(835, 130, "Бекенд A\nРеальні виклики -> 200 OK", size=10, fill="#eafaf0", stroke=FIELD, min_w=150))
    frags.append(box(835, 220, "Бекенд B (Outlier)\n5 помилок 5xx поспіль\n[Тимчасова евікція на 30 с]", size=10, fill="#fdecea", stroke=POS, min_w=160))

    frags.append(arrow(650, 155, 755, 135, color=FIELD, sw=2))
    frags.append(text(700, 135, "Користувацький RPC", size=9, color=FIELD))

    frags.append(arrow(650, 185, 750, 215, color=POS, sw=2))
    frags.append(text(700, 215, "5xx / Connection Reset", size=9, color=POS))

    frags.append(rect(505, 280, 430, 160, fill="#f0fff4", stroke=FIELD, sw=1, rx=4))
    frags.append(mtext(720, 305, [
        "Характеристики пасивного спостереження:",
        "• Нуль додаткового трафіку: аналізує реальні запити.",
        "• Миттєва реакція: вузол вилучається одразу після k помилок",
        "  (наприклад consecutive_5xx = 5) без очікування таймера.",
        "• Outlier Ejection: ізолює вузол з високим лагом або помилками,",
        "  повертаючи його в пул після періоду охолодження.",
        "• Найвища точність для виявлення «сірих відмов» (gray failures)."
    ], size=9.5, color=FIELD))

    return render(os.path.join(IMG, 'active-vs-passive-probing.svg'), W, H, *frags)


# ── Фігура 4: Режим паніки балансувальника (Panic Threshold / Fail-Open) ──────
def fig_panic_threshold():
    W, H = 980, 480
    frags = []

    frags.append(text(490, 28, "Режим паніки балансувальника (Panic Threshold): захист від тотального блекауту", size=15, bold=True))

    # Ліва частина: Звичайний режим (Строга ізоляція)
    frags.append(rect(30, 55, 435, 400, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(247, 82, "1. Звичайний режим (Healthy > 50%)", size=12, bold=True, color=FIELD))

    frags.append(box(120, 180, "Вхідний трафік\n10 000 RPS", size=10, bold=True, fill="#ffffff", stroke=MUTED, min_w=120))

    frags.append(box(350, 120, "Вузол 1: Healthy [50%]", size=10, fill="#eafaf0", stroke=FIELD, min_w=140))
    frags.append(box(350, 180, "Вузол 2: Healthy [50%]", size=10, fill="#eafaf0", stroke=FIELD, min_w=140))
    frags.append(box(350, 240, "Вузол 3: Unhealthy [0%]", size=10, fill="#fdecea", stroke=POS, min_w=140))
    frags.append(box(350, 300, "Вузол 4: Unhealthy [0%]", size=10, fill="#fdecea", stroke=POS, min_w=140))

    frags.append(arrow(185, 160, 275, 130, color=FIELD, sw=2))
    frags.append(arrow(185, 180, 275, 180, color=FIELD, sw=2))
    frags.append(line(185, 200, 275, 240, color=POS, sw=1.5, dash="4,4"))

    frags.append(rect(45, 350, 405, 90, fill="#f0fff4", stroke=FIELD, sw=1, rx=4))
    frags.append(mtext(247, 372, [
        "50% вузлів здорові (вище порогу паніки).",
        "Балансувальник строго ізолює хворі вузли 3 і 4,",
        "спрямовуючи 100% трафіку виключно на здорові вузли 1 і 2.",
        "Користувачі отримують успішні відповіді (200 OK)."
    ], size=9.5, color=FIELD))

    # Права частина: Режим паніки (Fail-Open)
    frags.append(rect(495, 55, 455, 400, fill="#fcfdfe", stroke=MUTED, sw=1.2, rx=6))
    frags.append(text(722, 82, "2. Режим паніки (Healthy < Panic Threshold, напр. 0%)", size=12, bold=True, color=POS))

    frags.append(box(585, 180, "Вхідний трафік\n10 000 RPS", size=10, bold=True, fill="#ffffff", stroke=MUTED, min_w=120))

    frags.append(box(815, 120, "Вузол 1: Unhealthy [25%]", size=10, fill="#fff3e0", stroke="#e67e22", min_w=150))
    frags.append(box(815, 180, "Вузол 2: Unhealthy [25%]", size=10, fill="#fff3e0", stroke="#e67e22", min_w=150))
    frags.append(box(815, 240, "Вузол 3: Unhealthy [25%]", size=10, fill="#fff3e0", stroke="#e67e22", min_w=150))
    frags.append(box(815, 300, "Вузол 4: Unhealthy [25%]", size=10, fill="#fff3e0", stroke="#e67e22", min_w=150))

    frags.append(arrow(650, 160, 735, 130, color="#e67e22", sw=1.8))
    frags.append(arrow(650, 175, 735, 175, color="#e67e22", sw=1.8))
    frags.append(arrow(650, 185, 735, 235, color="#e67e22", sw=1.8))
    frags.append(arrow(650, 200, 735, 290, color="#e67e22", sw=1.8))

    frags.append(rect(510, 350, 425, 90, fill="#fff8e1", stroke="#e67e22", sw=1, rx=4))
    frags.append(mtext(722, 372, [
        "Усі вузли провалили health check через мережевий сплеск!",
        "Замість 100% відмов (503 Service Unavailable) вмикається Fail-Open:",
        "балансувальник ігнорує статус здоров'я і ділить трафік порівну.",
        "Частина запитів проходить успішно, рятуючи систему від колапсу."
    ], size=9.5, color="#d35400"))

    return render(os.path.join(IMG, 'panic-threshold-failopen.svg'), W, H, *frags)


def main():
    fig_lifecycle_probes()
    fig_deep_health_check_cascade()
    fig_active_vs_passive()
    fig_panic_threshold()
    print("All figures generated successfully.")


if __name__ == '__main__':
    main()
