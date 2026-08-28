# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Хвилі розгортання парку, вікна витримки та ліміти ─────────────
def fig_fleet_rollout_waves():
    W, H = 960, 480
    frags = []

    # Тло часової осі
    frags.append(rect(40, 60, 880, 390, fill="#fafbfc", stroke="#e5e7eb", sw=1.5, rx=8))

    # Заголовки колонок етапів
    col_x = [140, 320, 520, 760]
    waves = [
        ("Хвиля 0: Доґфуд / Канарка", "0.5% парку (500 пристроїв)", "#eff6ff", "#2563eb"),
        ("Хвиля 1: Рання когорта", "5% парку (5 000 пристроїв)", "#f0fdf4", "#16a34a"),
        ("Хвиля 2: Широка когорта", "25% парку (25 000 пристроїв)", "#fefce8", "#ca8a04"),
        ("Хвиля 3: Глобальний реліз", "100% парку (100 000 пристроїв)", "#faf5ff", "#9333ea"),
    ]

    for i, (title, sub, f_col, s_col) in enumerate(waves):
        cx = col_x[i]
        b, w, h = textbox(cx, 100, f"{title}\n{sub}", size=11, bold=True,
                          fill=f_col, stroke=s_col, sw=1.8, pad=8)
        frags.append(b)

    # Вікна активності та витримки (Soak Time)
    # Хвиля 0: Розгортання (1 год) -> Витримка (12 год)
    frags.append(rect(60, 160, 160, 80, fill="#dbeafe", stroke="#2563eb", sw=1.5, rx=6))
    frags.append(text(140, 190, "Викочування: 500 од.", size=11, color="#1e40af", bold=True))
    frags.append(text(140, 215, "Ліміт: 50 паралельно", size=10, color=MUTED))

    frags.append(rect(60, 260, 160, 70, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=6))
    frags.append(text(140, 290, "Soak Time: 12 годин", size=11, color="#991b1b", bold=True))
    frags.append(text(140, 312, "SLI: відмови, відкоти, мовчання", size=9, color=MUTED))

    # Стрілка переходу 0 -> 1
    frags.append(arrow(220, 200, 240, 200, color=LINE, sw=1.8))
    frags.append(text(230, 190, "OK", size=10, color=FIELD, bold=True))

    # Хвиля 1: Розгортання (3 год) -> Витримка (24 год)
    frags.append(rect(240, 160, 160, 80, fill="#dcfce7", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(320, 190, "Викочування: 5 000 од.", size=11, color="#15803d", bold=True))
    frags.append(text(320, 215, "Ліміт: 200 паралельно", size=10, color=MUTED))

    frags.append(rect(240, 260, 160, 70, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=6))
    frags.append(text(320, 290, "Soak Time: 24 години", size=11, color="#991b1b", bold=True))
    frags.append(text(320, 312, "Добовий цикл навантаження", size=9, color=MUTED))

    # Стрілка переходу 1 -> 2
    frags.append(arrow(400, 200, 440, 200, color=LINE, sw=1.8))
    frags.append(text(420, 190, "OK", size=10, color=FIELD, bold=True))

    # Хвиля 2: Розгортання (8 год) -> Витримка (48 год)
    frags.append(rect(440, 160, 160, 80, fill="#fef9c3", stroke="#ca8a04", sw=1.5, rx=6))
    frags.append(text(520, 190, "Викочування: 25 000 од.", size=11, color="#854d0e", bold=True))
    frags.append(text(520, 215, "Ліміт: 1 000 паралельно", size=10, color=MUTED))

    frags.append(rect(440, 260, 160, 70, fill="#fef2f2", stroke="#dc2626", sw=1.5, rx=6))
    frags.append(text(520, 290, "Soak Time: 48 годин", size=11, color="#991b1b", bold=True))
    frags.append(text(520, 312, "Різні апаратні ревізії", size=9, color=MUTED))

    # Стрілка переходу 2 -> 3
    frags.append(arrow(600, 200, 680, 200, color=LINE, sw=1.8))
    frags.append(text(640, 190, "OK", size=10, color=FIELD, bold=True))

    # Хвиля 3: Фінальне розгортання
    frags.append(rect(680, 160, 160, 80, fill="#f3e8ff", stroke="#9333ea", sw=1.5, rx=6))
    frags.append(text(760, 190, "Решта: 70 000 од.", size=11, color="#6b21a8", bold=True))
    frags.append(text(760, 215, "Ліміт: 2 500 паралельно", size=10, color=MUTED))

    frags.append(rect(680, 260, 160, 70, fill="#f0fdf4", stroke="#16a34a", sw=1.5, rx=6))
    frags.append(text(760, 290, "100% Парку оновлено", size=11, color="#15803d", bold=True))
    frags.append(text(760, 312, "Кампанія завершена", size=9, color=MUTED))

    # Нижня плашка: Автоматичний Stop-the-Line
    bar, bw, bh = textbox(480, 390,
                          "Автоматичний моніторинг Stop-the-Line:\n"
                          "Якщо на будь-якому етапі (Помилки > 1.0% АБО Відкоти > 0.5% АБО Замовклі > 0.2%) "
                          "-> Негайне блокування кампанії",
                          size=11, bold=True, fill="#fff1f2", stroke="#be123c", sw=2, pad=10)
    frags.append(bar)

    render(os.path.join(IMG, 'fleet-rollout-waves.svg'), W, H, *frags,
           title="Поетапні хвилі розгортання парку, вікна витримки та ліміти одночасності")


# ── Фігура 2: Воронка тріажу метрик кампанії ────────────────────────────────
def fig_campaign_triage_metrics():
    W, H = 960, 520
    frags = []

    # 1. Цільовий пул
    b1, w1, h1 = textbox(130, 260, "Цільовий пул парку\n(Target Population)\n100 000 пристроїв",
                         size=12, bold=True, fill="#f3f4f6", stroke=INK, sw=1.8, pad=10)
    frags.append(b1)

    # Стрілка 1 -> 2
    frags.append(arrow(215, 260, 275, 260, color=LINE, sw=1.8))

    # 2. Призначені на хвилю
    b2, w2, h2 = textbox(365, 260, "Призначені на хвилю\n(Assigned to Wave)\nКритерії сумісності",
                         size=12, bold=True, fill="#eef4ff", stroke=NEG, sw=1.8, pad=10)
    frags.append(b2)

    # Стрілка 2 -> 3
    frags.append(arrow(455, 260, 515, 260, color=LINE, sw=1.8))

    # 3. В процесі (In-Flight)
    b3, w3, h3 = textbox(605, 260, "В процесі виконання\n(In-Flight / Downloading)\nОбмежено лімітом",
                         size=12, bold=True, fill="#fffbeb", stroke="#d97706", sw=2, pad=10)
    frags.append(b3)

    # Розгалуження результатів на 4 термінальні стани
    # 4a. Успіх (Succeeded)
    frags.append(arrow(695, 230, 770, 110, color=FIELD, sw=2))
    b_succ, _, _ = textbox(850, 100, "Успішно (Succeeded)\nНова версія підтверджена\nЗв'язок і телеметрія в нормі",
                           size=11, bold=True, fill="#f0fdf4", stroke=FIELD, sw=1.8, pad=8)
    frags.append(b_succ)

    # 4b. Явна відмова (Failed)
    frags.append(arrow(695, 245, 770, 205, color="#d97706", sw=2))
    b_fail, _, _ = textbox(850, 205, "Явна відмова (Failed)\nПомилка завантаження / SHA256\nПристрій працює на старій версії",
                           size=11, bold=True, fill="#fffbeb", stroke="#d97706", sw=1.8, pad=8)
    frags.append(b_fail)

    # 4c. Апаратний відкіт (Rolled Back)
    frags.append(arrow(695, 275, 770, 315, color="#ea580c", sw=2))
    b_rb, _, _ = textbox(850, 315, "Апаратний відкіт (Rolled Back)\nWatchdog / провал self-test\nАвтоповернення у слот A/B",
                         size=11, bold=True, fill="#fff7ed", stroke="#ea580c", sw=1.8, pad=8)
    frags.append(b_rb)

    # 4d. Замовклі пристрої (Silenced / Bricked)
    frags.append(arrow(695, 290, 770, 425, color=POS, sw=2.2))
    b_sil, _, _ = textbox(850, 425, "Замовклі пристрої (Silenced)\nТаймаут серцебиття (Heartbeat)\nКритична аварія: окрипічення",
                          size=11, bold=True, fill="#fef2f2", stroke=POS, sw=2.2, pad=8)
    frags.append(b_sil)

    # Пояснювальний бейдж для Silenced
    badge, _, _ = textbox(365, 430,
                          "Найнебезпечніший показник: пристрій взяв оновлення, пішов на перезавантаження,\n"
                          "але не надіслав жодного статусу через збій мережевого драйвера або паніку ядра",
                          size=10, bold=True, fill="#fff1f2", stroke=POS, sw=1.2, pad=6)
    frags.append(badge)
    frags.append(line(575, 430, 725, 430, color=POS, sw=1.5, dash="3,3"))

    render(os.path.join(IMG, 'campaign-triage-metrics.svg'), W, H, *frags,
           title="Воронка метрик кампанії оновлення та виявлення замовклих пристроїв")


# ── Фігура 3: Скінченний автомат станів контролера кампанії ─────────────────
def fig_campaign_state_machine():
    W, H = 960, 480
    frags = []

    # 1. Стан ЧЕРНЕТКА / ЗАПЛАНОВАНО
    b_draft, _, _ = textbox(120, 150, "ЗАПЛАНОВАНО\n(Scheduled)\nПеревірка маніфесту",
                            size=11, bold=True, fill="#f3f4f6", stroke=MUTED, sw=1.5, pad=8)
    frags.append(b_draft)

    # 2. Стан АКТИВНА ХВИЛЯ (In-Progress)
    b_active, _, _ = textbox(340, 150, "АКТИВНА ХВИЛЯ\n(In-Progress)\nРоздача квот пристроям",
                             size=11, bold=True, fill="#eef4ff", stroke=NEG, sw=2, pad=10)
    frags.append(b_active)

    # Стрілка Заплановано -> Активна хвиля
    frags.append(arrow(190, 150, 265, 150, color=LINE, sw=1.8))
    frags.append(text(227, 138, "Старт", size=10, color=INK))

    # 3. Стан ВИРОБЛЕННЯ ВИМОГ / ВИПРОБУВАННЯ (Soaking & Evaluating)
    b_soak, _, _ = textbox(600, 150, "ВИСТОЮВАННЯ\n(Soaking & Evaluating)\nЗбір телеметрії когорти",
                           size=11, bold=True, fill="#fefce8", stroke="#ca8a04", sw=2, pad=10)
    frags.append(b_soak)

    # Стрілка Активна хвиля -> Вистоювання
    frags.append(arrow(415, 150, 500, 150, color=LINE, sw=1.8))
    frags.append(text(457, 138, "Квоту видано", size=10, color=INK))

    # 4. Стан ЗАВЕРШЕНО
    b_done, _, _ = textbox(850, 150, "ЗАВЕРШЕНО\n(Completed)\n100% парку оновлено",
                           size=11, bold=True, fill="#f0fdf4", stroke=FIELD, sw=2, pad=10)
    frags.append(b_done)

    # Стрілка Вистоювання -> Завершено (якщо остання хвиля)
    frags.append(arrow(700, 150, 770, 150, color=FIELD, sw=2))
    frags.append(text(735, 138, "SLI OK (фінал)", size=10, color=FIELD, bold=True))

    # Петля: Вистоювання -> Наступна хвиля (якщо не остання)
    frags.append(line(600, 205, 600, 250, color=FIELD, sw=1.8))
    frags.append(line(600, 250, 340, 250, color=FIELD, sw=1.8))
    frags.append(arrow(340, 250, 340, 205, color=FIELD, sw=1.8))
    frags.append(text(470, 240, "SLI в нормі -> Наступна хвиля (Ring N+1)", size=10, color=FIELD, bold=True))

    # 5. Аварійний стан: ЗУПИНЕНО / STOP-THE-LINE
    b_pause, _, _ = textbox(470, 380,
                            "АВАРІЙНО ЗУПИНЕНО (Stop-the-Line / Paused)\n"
                            "Перевищено поріг: Відмови > Max || Відкоти > Max || Замовклі > Max\n"
                            "Зупинка роздачі нових пакетів, розслідування інциденту",
                            size=11, bold=True, fill="#fef2f2", stroke=POS, sw=2.2, pad=10)
    frags.append(b_pause)

    # Стрілки збоїв з Активної хвилі та Вистоювання у Stop-the-Line
    frags.append(line(340, 205, 340, 330, color=POS, sw=2, dash="4,3"))
    frags.append(arrow(340, 330, 420, 345, color=POS, sw=2))

    frags.append(line(600, 205, 600, 330, color=POS, sw=2, dash="4,3"))
    frags.append(arrow(600, 330, 520, 345, color=POS, sw=2))

    frags.append(text(260, 290, "Аномалія метрик", size=10, color=POS, bold=True))
    frags.append(text(680, 290, "Зрив порогу SLI", size=10, color=POS, bold=True))

    render(os.path.join(IMG, 'campaign-state-machine.svg'), W, H, *frags,
           title="Скінченний автомат станів контролера кампанії оновлення")


if __name__ == '__main__':
    fig_fleet_rollout_waves()
    fig_campaign_triage_metrics()
    fig_campaign_state_machine()
    print("Всі фігури успішно згенеровано.")
