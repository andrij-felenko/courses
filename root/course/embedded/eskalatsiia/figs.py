# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Чотири апаратні тригери ескалації ─────────────────────────────────────
def fig_triggers():
    W, H = 940, 480
    frags = []

    cards = [
        ("1. Неоднозначність сцени",
         "Softmax-ентропія вище норми;\nдві близькі гіпотези:\n• P(людина) = 0.48\n• P(тінь/мішок) = 0.52\nЦіна помилки неприйнятна.",
         NEG, "#eef4ff"),
        ("2. Глухий кут планувальника",
         "Усі кандидатні траєкторії в\nсітці вартостей (costmap)\nзаблоковані або мають вартість\nвище допустимої стелі безпеки.",
         POS, "#fff0f0"),
        ("3. Сіра зона детекції",
         "Критичний об'єкт у діапазоні\nграничної впевненості [0.4..0.7]:\nігнорувати небезпечно,\nаварійне гальмування — зрив місії.",
         "#d97706", "#fffbeb"),
        ("4. Вихід за межі ODD",
         "Порушення робочого домену:\n• засліплення камери сонцем\n• знос вітром > 12 м/с\n• розходження EKF (іновації > 3σ)\n• OOD-аномалія на вході.",
         "#7c3aed", "#f5f3ff")
    ]

    bw, bh = 210, 200
    gap = (W - 40 - 4 * bw) / 3
    x0 = 20
    y0 = 60

    for i, (title_text, desc, col, bg_col) in enumerate(cards):
        x = x0 + i * (bw + gap)
        frags.append(rect(x, y0, bw, bh, fill=bg_col, stroke=col, sw=2, rx=8))
        frags.append(text(x + bw / 2, y0 + 26, title_text, size=13, color=col, bold=True))
        frags.append(line(x + 10, y0 + 38, x + bw - 10, y0 + 38, color=col, sw=1.2))
        frags.append(mtext(x + bw / 2, y0 + 62, desc, size=11, color=INK, lh=1.35))
        
        # Стрілка вниз до спільного вузла ескалації
        frags.append(arrow(x + bw / 2, y0 + bh, x + bw / 2, y0 + bh + 45, color=col, sw=1.8))

    # Спільний блок: Генератор запиту ескалації
    yb = y0 + bh + 50
    w_hub, h_hub = 780, 110
    x_hub = (W - w_hub) / 2
    frags.append(rect(x_hub, yb, w_hub, h_hub, fill="#1e293b", stroke="#0f172a", sw=2, rx=10))
    frags.append(text(W / 2, yb + 28, "БОРТОВИЙ МОДУЛЬ ЕСКАЛАЦІЇ (Escalation Supervisor)", size=14, color="#ffffff", bold=True))
    frags.append(mtext(W / 2, yb + 56, "1. Фіксація поточного безпечного стану та увімкнення динамічного таймера\n2. Пакування контексту: стиснутий ROI 256x256 + локальна сітка + вектор стану\n3. Генерація структурованих варіантів дій A / B / C і надсилання оператору",
                       size=12, color="#94a3b8", lh=1.35))

    render(os.path.join(OUT, "eskalatsiia-triggers.svg"), W, H, *frags)


# ── 2. Структура пакету запиту до оператора ──────────────────────────────────
def fig_packet():
    W, H = 940, 440
    frags = []

    # Заголовок зверху
    frags.append(rect(20, 30, W - 40, 50, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=6))
    frags.append(text(40, 60, "ПАКЕТ ЗАПИТУ ЕСКАЛАЦІЇ: ESCALATION_QUERY (Розмір <= 480 байтів)", size=13, color="#ffffff", anchor="start", bold=True))
    frags.append(text(W - 40, 60, "Канал: Телеметрія / MAVLink payload", size=12, color="#94a3b8", anchor="end"))

    # Чотири секції пакету
    sections = [
        ("Секція 1: Заголовок і тригер",
         "• ID запиту: 0x8A4F\n• Код причини: PATH_BLOCKED\n• Рівень тривоги: WARNING\n• Часова мітка: 142.850 с\n• Динамічний дедлайн: 3.2 с",
         "#2563eb", "#eff6ff", 190),
        ("Секція 2: Візуальний ROI",
         "• Кроп камери: 256x256 px\n• Формат: JPEG Q=45 (280 B)\n• Bounding Box детекції\n• Вектор руху цілі (Vx, Vy)\n• Клас: UNKNOWN_OBSTACLE",
         "#059669", "#ecfdf5", 220),
        ("Секція 3: Геопростір",
         "• Координати: (X, Y, Z)\n• Поточна швидкість: 4.8 м/с\n• Зріз сітки вартостей 10x10 м\n• Поточний вейпойнт: #14\n• Запас батареї: 64% (18 хв)",
         "#7c3aed", "#f5f3ff", 220),
        ("Секція 4: Варіанти дій",
         "• A: Об'їзд ліворуч (+15 м)\n• B: Об'їзд праворуч (+60 м)\n• C: Скасувати сегмент\n• D: Аварійне зависання\n(Оператор обирає 1 байт!)",
         "#c0392b", "#fef2f2", 230)
    ]

    y_sec = 100
    h_sec = 210
    x_cur = 20
    for title_text, body_text, stroke_c, fill_c, w_b in sections:
        frags.append(rect(x_cur, y_sec, w_b, h_sec, fill=fill_c, stroke=stroke_c, sw=1.8, rx=6))
        frags.append(text(x_cur + w_b / 2, y_sec + 24, title_text, size=12, color=stroke_c, bold=True))
        frags.append(line(x_cur + 8, y_sec + 34, x_cur + w_b - 8, y_sec + 34, color=stroke_c, sw=1))
        frags.append(mtext(x_cur + 12, y_sec + 58, body_text, size=11, color=INK, anchor="start", lh=1.35))
        x_cur += w_b + 13

    # Нижня плашка: Як відповідає оператор
    y_resp = 330
    frags.append(rect(20, y_resp, W - 40, 85, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(40, y_resp + 28, "ВІДПОВІДЬ ОПЕРАТОРА (ESCALATION_RESPONSE):", size=13, color=INK, anchor="start", bold=True))
    frags.append(mtext(40, y_resp + 52, "• query_id (2 байти) + selected_option (1 байт) + auth_token (4 байти) = 7 байтів корисного навантаження.\n• Оператор не формує складну траєкторію вручну — він обирає одне з прорахованих безпечних рішень одним кліком.",
                       size=11.5, color=MUTED, anchor="start", lh=1.3))

    render(os.path.join(OUT, "operator-query-packet.svg"), W, H, *frags)


# ── 3. Фізика динамічного таймауту ──────────────────────────────────────────
def fig_timeout():
    W, H = 940, 420
    frags = []

    # Верхня шкала дистанції
    y_track = 120
    frags.append(line(60, y_track, W - 60, y_track, color=LINE, sw=3))
    
    # Апарат ліворуч
    frags.append(rect(60, y_track - 25, 60, 50, fill="#2563eb", stroke="#1e40af", sw=2, rx=6))
    frags.append(text(90, y_track + 5, "Борт", size=12, color="#ffffff", bold=True))
    frags.append(text(90, y_track - 35, "V = 8.0 м/с", size=12, color=INK, bold=True))
    frags.append(arrow(125, y_track, 175, y_track, color="#2563eb", sw=2.5))

    # Перешкода праворуч
    frags.append(rect(W - 130, y_track - 35, 70, 70, fill="#dc2626", stroke="#991b1b", sw=2, rx=8))
    frags.append(text(W - 95, y_track + 5, "Бар'єр", size=12, color="#ffffff", bold=True))
    frags.append(text(W - 95, y_track - 45, "Перешкода", size=12, color=POS, bold=True))

    # Відрізки дистанції
    # Загальна відстань D_obs = 40 м
    frags.append(line(120, y_track + 40, W - 130, y_track + 40, color=MUTED, sw=1.5))
    frags.append(line(120, y_track + 33, 120, y_track + 47, color=MUTED, sw=1.5))
    frags.append(line(W - 130, y_track + 33, W - 130, y_track + 47, color=MUTED, sw=1.5))
    frags.append(text((120 + W - 130) / 2, y_track + 58, "Дистанція виявлення: D_obs = 40.0 м", size=12, color=INK, bold=True))

    # Розбивка на 3 зони під шкалою
    y_zones = 220
    # Зона 1: Час на реакцію (T_react * V)
    w_react = 280
    x_react = 120
    frags.append(rect(x_react, y_zones, w_react, 60, fill="#eff6ff", stroke="#2563eb", sw=1.5, rx=4))
    frags.append(text(x_react + w_react / 2, y_zones + 24, "ВІКНО РЕАКЦІЇ (D_react = 18 м)", size=11.5, color="#1e40af", bold=True))
    frags.append(text(x_react + w_react / 2, y_zones + 46, "T_deadline = D_react / V = 2.25 с", size=11, color="#2563eb"))

    # Зона 2: Гальмівний шлях (D_brake = V^2 / 2a)
    w_brake = 260
    x_brake = x_react + w_react + 10
    frags.append(rect(x_brake, y_zones, w_brake, 60, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=4))
    frags.append(text(x_brake + w_brake / 2, y_zones + 24, "ГАЛЬМІВНИЙ ШЛЯХ (D_brake = 16 м)", size=11.5, color="#92400e", bold=True))
    frags.append(text(x_brake + w_brake / 2, y_zones + 46, "a_max = 2.0 м/с² (фізична межа гальм)", size=11, color="#d97706"))

    # Зона 3: Запас безпеки (D_margin)
    w_margin = 130
    x_margin = x_brake + w_brake + 10
    frags.append(rect(x_margin, y_zones, w_margin, 60, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=4))
    frags.append(text(x_margin + w_margin / 2, y_zones + 24, "ЗАПАС (6 м)", size=11.5, color="#991b1b", bold=True))
    frags.append(text(x_margin + w_margin / 2, y_zones + 46, "Буфер D_margin", size=11, color="#dc2626"))

    # Підсумок формули внизу
    y_bot = 315
    frags.append(rect(60, y_bot, W - 120, 75, fill="#f8fafc", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(W / 2, y_bot + 24, "Формула розрахунку жорсткого дедлайну ескалації:", size=12, color=INK, bold=True))
    frags.append(text(W / 2, y_bot + 50, "T_deadline = (D_obs - D_brake - D_margin) / V_curr - t_sensor_lag", size=12.5, color=POS, bold=True))

    render(os.path.join(OUT, "dynamic-timeout-braking.svg"), W, H, *frags)


# ── 4. Скінченний автомат ескалації та каскад fail-safe ─────────────────────
def fig_fsm():
    W, H = 940, 520
    frags = []

    # 1. Стан AUTONOMOUS
    frags.append(rect(40, 50, 190, 80, fill="#f0fdf4", stroke="#16a34a", sw=2, rx=8))
    frags.append(text(135, 85, "AUTONOMOUS", size=13, color="#15803d", bold=True))
    frags.append(text(135, 108, "Штатне виконання місії", size=11, color=MUTED))

    # Стрілка до ESCALATION_REQUESTED
    frags.append(arrow(230, 90, 310, 90, color=LINE, sw=1.8))
    frags.append(text(270, 78, "Тригер", size=11, color=POS, bold=True))

    # 2. Стан ESCALATION_REQUESTED
    frags.append(rect(315, 50, 230, 80, fill="#eff6ff", stroke="#2563eb", sw=2, rx=8))
    frags.append(text(430, 80, "ESCALATION_REQUESTED", size=12.5, color="#1e40af", bold=True))
    frags.append(mtext(430, 102, "Розрахунок дедлайну\nВідправка пакету на GCS", size=11, color=MUTED))

    # Стрілка до AWAITING_OPERATOR
    frags.append(arrow(545, 90, 630, 90, color=LINE, sw=1.8))

    # 3. Стан AWAITING_OPERATOR
    frags.append(rect(635, 50, 260, 80, fill="#fffbeb", stroke="#d97706", sw=2, rx=8))
    frags.append(text(765, 80, "AWAITING_OPERATOR", size=12.5, color="#92400e", bold=True))
    frags.append(mtext(765, 102, "Зворотний відлік T_deadline\nПрийом дискретної опції", size=11, color=MUTED))

    # Гілка успіху: оператор відповів
    frags.append(arrow(765, 130, 765, 215, color="#16a34a", sw=2))
    frags.append(text(775, 175, "Опція A / B / C", size=11, color="#16a34a", anchor="start", bold=True))

    frags.append(rect(660, 220, 210, 70, fill="#f0fdf4", stroke="#16a34a", sw=1.8, rx=6))
    frags.append(text(765, 250, "APPLY_OVERRIDE", size=12, color="#15803d", bold=True))
    frags.append(text(765, 270, "Виконання обраної дії", size=11, color=MUTED))

    # Повернення в AUTONOMOUS
    frags.append(line(660, 255, 135, 255, color="#16a34a", sw=1.8, dash="4,3"))
    frags.append(arrow(135, 255, 135, 135, color="#16a34a", sw=1.8))
    frags.append(text(380, 245, "Дію завершено -> повернення до автономної місії", size=11, color="#16a34a", bold=True))

    # Гілка вичерпання дедлайну -> Каскад FAILSAFE (прямокутна траєкторія стрілки)
    frags.append(line(765, 50, 765, 25, color=POS, sw=1.8))
    frags.append(line(765, 25, 480, 25, color=POS, sw=1.8))
    frags.append(arrow(480, 25, 480, 340, color=POS, sw=2))
    frags.append(text(620, 18, "Таймаут вичерпано / обрив радіолінка", size=11, color=POS, bold=True))

    # Каскадний блок аварійної логіки
    y_fail = 350
    frags.append(rect(40, y_fail, W - 80, 135, fill="#fef2f2", stroke="#dc2626", sw=2, rx=8))
    frags.append(text(60, y_fail + 26, "КАСКАД FAIL-SAFE ЗА ВІДСУТНОСТІ ВІДПОВІДІ ТА ЗВ'ЯЗКУ:", size=13, color="#991b1b", anchor="start", bold=True))

    fails = [
        ("Рівень 1: FAILSAFE_HOLD", "Миттєве гальмування;\nзависання/зупинка на місці;\nконтроль бюджету батареї.", "#dc2626"),
        ("Рівень 2: FAILSAFE_BACKTRACK", "Реверс руху за буфером точок\n(Breadcrumb trail) назад до зони\nперевіреного зв'язку й безпеки.", "#b91c1c"),
        ("Рівень 3: SAFE_TERMINATION", "Керована аварійна посадка / стоп;\nзнеструмлення силових приводів;\nмаяк + запис у чорну скриньку.", "#7f1d1d")
    ]

    w_fb = 260
    gap_fb = (W - 120 - 3 * w_fb) / 2
    for j, (ftitle, fdesc, fcol) in enumerate(fails):
        xf = 60 + j * (w_fb + gap_fb)
        frags.append(rect(xf, y_fail + 45, w_fb, 75, fill="#ffffff", stroke=fcol, sw=1.5, rx=5))
        frags.append(text(xf + w_fb / 2, y_fail + 68, ftitle, size=11.5, color=fcol, bold=True))
        frags.append(mtext(xf + w_fb / 2, y_fail + 90, fdesc, size=10.5, color=INK, lh=1.3))
        if j < 2:
            frags.append(arrow(xf + w_fb, y_fail + 82, xf + w_fb + gap_fb - 2, y_fail + 82, color=fcol, sw=1.5))

    render(os.path.join(OUT, "escalation-state-machine.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_triggers()
    fig_packet()
    fig_timeout()
    fig_fsm()
    print("Figures generated successfully.")
