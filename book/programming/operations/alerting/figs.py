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


# ── Фігура 1: Симптомний проти причинного алертингу ──────────────────────────
def fig_symptom_vs_cause():
    W, H = 960, 480
    frags = []

    # Верхня колонка: Причинний підхід (внутрішні технічні метрики)
    y_top = 115
    frags.append(box(190, y_top, "1. Причинний підхід\n(внутрішні технічні метрики)",
                     size=13, bold=True, fill="#fff3e0", stroke=POS, min_w=240))
    frags.append(box(520, y_top, "Алерт на кожен ресурс:\n• CPU > 85% • Disk > 80%\n• MySQL slow queries > 10",
                     size=11, fill="#fdf6e3", stroke=POS, min_w=270))
    frags.append(box(820, y_top, "Наслідок: Шум і сліпота\n• 90% хибних тривог\n• Пропуск тихих падінь бізнесу",
                     size=11, bold=True, fill="#fdecea", stroke=POS, min_w=220))

    frags.append(arrow(315, y_top, 380, y_top, color=POS, sw=2))
    frags.append(arrow(660, y_top, 705, y_top, color=POS, sw=2))

    # Розділювальна лінія
    y_mid = 235
    frags.append(line(60, y_mid, 900, y_mid, color=MUTED, sw=1.5, dash="6 4"))
    frags.append(box(W / 2, y_mid, "Зміна фокусу: алерти лише на страждання користувача, ресурси — на панелі діагностики",
                     size=11, bold=True, fill="#fff", stroke=MUTED, pad=6))

    # Нижня колонка: Симптомний підхід (досвід користувача та SLI)
    y_bot = 355
    frags.append(box(190, y_bot, "2. Симптомний підхід\n(досвід користувача та SLI)",
                     size=13, bold=True, fill="#e8f0ff", stroke=NEG, min_w=240))
    frags.append(box(520, y_bot, "Алерт на золоті сигнали:\n• Частка помилок (5xx) > 1%\n• Затримка p99 > 500 мс",
                     size=11, fill="#eaf0fd", stroke=NEG, min_w=270))
    frags.append(box(820, y_bot, "Наслідок: Точний сигнал\n• Будить людей лише при біді\n• Ловить невідомі збої",
                     size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=220))

    frags.append(arrow(315, y_bot, 380, y_bot, color=NEG, sw=2))
    frags.append(arrow(660, y_bot, 705, y_bot, color=FIELD, sw=2))

    # Зв'язок зліва: перехід до SLI
    y_label = 235
    frags.append(box(85, y_label, "перехід →\nдо SLI", size=10, fill="#fff", stroke=INK, pad=4))
    frags.append(arrow(135, y_top + 36, 85, y_label - 20, color=INK, sw=1.6))
    frags.append(arrow(85, y_label + 20, 135, y_bot - 36, color=INK, sw=1.6))

    frags.append(text(W / 2, H - 18,
                      "Причинні алерти шумлять і пропускають аварії; симптомні алерти захищають користувача.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'symptom-vs-cause-alerting.svg'), W, H, *frags,
           title="Порівняння симптомного та причинного алертингу")


# ── Фігура 2: Скінченний автомат життєвого циклу алерту ──────────────────────
def fig_lifecycle():
    W, H = 960, 420
    frags = []

    y = 160
    frags.append(box(130, y, "1. Inactive\n(неактивний)\nУмова = false",
                     size=12, bold=True, fill="#eafaf0", stroke=FIELD, min_w=150))
    frags.append(box(390, y, "2. Pending\n(очікування)\nТаймер for: 5m",
                     size=12, bold=True, fill="#fdf6e3", stroke=POS, min_w=160))
    frags.append(box(670, y, "3. Firing\n(спрацьовування)\nСповіщення в AM",
                     size=12, bold=True, fill="#fdecea", stroke=POS, min_w=170))
    frags.append(box(880, y, "4. Resolved\n(знято)\nВідновлення норми",
                     size=12, bold=True, fill="#e8f0ff", stroke=NEG, min_w=140))

    # Переходи вперед
    frags.append(arrow(210, y - 10, 305, y - 10, color=POS, sw=2))
    frags.append(text(257, y - 26, "Умова = true", size=10, bold=True, color=POS))

    frags.append(arrow(475, y - 10, 580, y - 10, color=POS, sw=2))
    frags.append(text(527, y - 26, "Час >= 5 хв", size=10, bold=True, color=POS))

    frags.append(arrow(760, y - 10, 805, y - 10, color=NEG, sw=2))
    frags.append(text(782, y - 26, "Умова = false", size=10, bold=True, color=NEG))

    # Зворотний перехід з Pending в Inactive (короткий сплеск зник)
    frags.append(arrow(350, y + 42, 170, y + 42, color=FIELD, sw=1.8))
    frags.append(text(260, y + 62, "Сплеск минув до вичерпання 5 хв (без шуму)", size=10, color=FIELD))

    # Зворотний перехід з Resolved в Inactive
    frags.append(arrow(880, y + 42, 130, y + 130, color=MUTED, sw=1.5))
    frags.append(text(500, y + 135, "Автоматичне повернення до моніторингу за замовчуванням", size=11, color=MUTED))

    frags.append(text(W / 2, H - 20,
                      "Інтервал затримки for захищає чергових від хибних сповіщень на короткочасних сплесках.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'alert-lifecycle-state-machine.svg'), W, H, *frags,
           title="Скінченний автомат станів правила алертингу")


# ── Фігура 3: Топологія та конвеєр Alertmanager ─────────────────────────────
def fig_alertmanager_pipeline():
    W, H = 960, 490
    frags = []

    y1 = 120
    frags.append(box(110, y1, "Prometheus / Mimir\n(потік алертів)", size=11, bold=True, fill="#f4f6f8", stroke=LINE, min_w=150))
    frags.append(box(320, y1, "1. Дедуплікація\n(Fingerprint хеш)", size=11, fill="#e8f0ff", stroke=NEG, min_w=140))
    frags.append(box(520, y1, "2. Замовчування\n(Silences / Вікна робіт)", size=11, fill="#fdf6e3", stroke=POS, min_w=150))
    frags.append(box(740, y1, "3. Інгібування\n(Inhibition / Батько глушить)", size=11, fill="#fdecea", stroke=POS, min_w=170))

    frags.append(arrow(190, y1, 245, y1, color=LINE, sw=1.8))
    frags.append(arrow(395, y1, 440, y1, color=NEG, sw=1.8))
    frags.append(arrow(600, y1, 650, y1, color=POS, sw=1.8))

    y2 = 290
    frags.append(box(210, y2, "4. Згрупування (Grouping)\ngroup_by: [alertname, cluster]\ngroup_wait: 30s",
                     size=11, fill="#eaf0fd", stroke=NEG, min_w=240))
    frags.append(box(540, y2, "5. Дерево маршрутизації (Route Tree)\nЗіставлення міток (labels)\nseverity = critical / warning",
                     size=11, fill="#f4f6f8", stroke=LINE, min_w=260))

    frags.append(arrow(740, y1 + 35, 330, y2 - 40, color=POS, sw=1.8))
    frags.append(arrow(335, y2, 405, y2, color=NEG, sw=1.8))

    y_rec1 = 230
    y_rec2 = 290
    y_rec3 = 350
    frags.append(box(830, y_rec1, "PagerDuty (P1 / Critical)\nДзвінок / SMS черговому",
                     size=10, bold=True, fill="#fdecea", stroke=POS, min_w=200))
    frags.append(box(830, y_rec2, "Slack / Matrix (P2 / Warn)\nРобочий канал команди",
                     size=10, bold=True, fill="#eaf0fd", stroke=NEG, min_w=200))
    frags.append(box(830, y_rec3, "Jira / Bugzilla (P3 / Info)\nАвтоматичний таск",
                     size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=200))

    frags.append(arrow(675, y2 - 20, 725, y_rec1, color=POS, sw=1.8))
    frags.append(arrow(675, y2, 725, y_rec2, color=NEG, sw=1.8))
    frags.append(arrow(675, y2 + 20, 725, y_rec3, color=FIELD, sw=1.8))

    frags.append(text(W / 2, H - 20,
                      "Alertmanager фільтрує шум через замовчування, інгібування та згрупування перед надсиланням.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'alertmanager-pipeline-topology.svg'), W, H, *frags,
           title="Конвеєр обробки та маршрутизації в Alertmanager")


# ── Фігура 4: Багатовіконний моніторинг випалювання бюджету (Burn Rate) ───────
def fig_burn_rate():
    W, H = 960, 480
    frags = []

    y_t1 = 90
    y_t2 = 180
    y_t3 = 270
    y_t4 = 360

    frags.append(box(150, y_t1, "Критичний 1 (Page)\nШвидкість = 14.4x (2% / 1 год)",
                     size=11, bold=True, fill="#fdecea", stroke=POS, min_w=210))
    frags.append(box(150, y_t2, "Критичний 2 (Page)\nШвидкість = 6x (5% / 6 год)",
                     size=11, bold=True, fill="#fff3e0", stroke=POS, min_w=210))
    frags.append(box(150, y_t3, "Тікет 1 (Робочий час)\nШвидкість = 3x (10% / 24 год)",
                     size=11, bold=True, fill="#e8f0ff", stroke=NEG, min_w=210))
    frags.append(box(150, y_t4, "Тікет 2 (Робочий час)\nШвидкість = 1x (10% / 3 дні)",
                     size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=210))

    frags.append(box(490, y_t1, "Коротке: 1 год (14.4x) AND Довге: 5 хв (14.4x)\nМиттєве виявлення повної відмови системи",
                     size=11, fill="#fdecea", stroke=POS, min_w=370))
    frags.append(box(490, y_t2, "Коротке: 6 год (6x) AND Довге: 30 хв (6x)\nВиявлення стійкої деградації середнього темпу",
                     size=11, fill="#fff3e0", stroke=POS, min_w=370))
    frags.append(box(490, y_t3, "Коротке: 24 год (3x) AND Довге: 2 год (3x)\nПовільне танення бюджету помилок",
                     size=11, fill="#eaf0fd", stroke=NEG, min_w=370))
    frags.append(box(490, y_t4, "Коротке: 3 дні (1x) AND Довге: 6 год (1x)\nФоновий витік надійності протягом місяця",
                     size=11, fill="#eafaf0", stroke=FIELD, min_w=370))

    frags.append(arrow(260, y_t1, 300, y_t1, color=POS, sw=1.8))
    frags.append(arrow(260, y_t2, 300, y_t2, color=POS, sw=1.8))
    frags.append(arrow(260, y_t3, 300, y_t3, color=NEG, sw=1.8))
    frags.append(arrow(260, y_t4, 300, y_t4, color=FIELD, sw=1.8))

    frags.append(box(810, y_t1, "Пейджер: терміново\nВичерпання за 2 дні", size=10, bold=True, fill="#fdecea", stroke=POS, min_w=170))
    frags.append(box(810, y_t2, "Пейджер: терміново\nВичерпання за 5 днів", size=10, bold=True, fill="#fff3e0", stroke=POS, min_w=170))
    frags.append(box(810, y_t3, "Тікет: черга розробки\nВичерпання за 10 днів", size=10, bold=True, fill="#eaf0fd", stroke=NEG, min_w=170))
    frags.append(box(810, y_t4, "Тікет: плановий спринт\nВичерпання за 30 днів", size=10, bold=True, fill="#eafaf0", stroke=FIELD, min_w=170))

    frags.append(arrow(680, y_t1, 720, y_t1, color=POS, sw=1.8))
    frags.append(arrow(680, y_t2, 720, y_t2, color=POS, sw=1.8))
    frags.append(arrow(680, y_t3, 720, y_t3, color=NEG, sw=1.8))
    frags.append(arrow(680, y_t4, 720, y_t4, color=FIELD, sw=1.8))

    frags.append(text(W / 2, H - 20,
                      "Багатовіконна перевірка одночасно гарантує швидке реагування та відсутність передчасного зняття.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'multi-window-burn-rate.svg'), W, H, *frags,
           title="Багаторівнева стратегія алертингу за швидкістю випалювання бюджету")


# ── Фігура 5: Флапінг та гістерезис ──────────────────────────────────────────
def fig_flapping():
    W, H = 960, 460
    frags = []

    ox, oy = 100, 360
    gx, gy = 880, 80

    # Пороги гістерезису
    y_fire = 150
    y_clear = 270

    # Зона гістерезису (буфер) - малюємо ДО тексту
    frags.append(rect(ox + 1, y_fire, gx - ox - 2, y_clear - y_fire, fill="#fdfbf7", stroke="none"))
    frags.append(text(gx - 20, (y_fire + y_clear) / 2 + 4, "Зона гістерезису: стан не змінюється", size=11, italic=True, color=MUTED, anchor="end"))

    # Осі
    frags.append(line(ox, oy, gx, oy, color=INK, sw=2))
    frags.append(arrow(gx - 2, oy, gx + 2, oy, color=INK, sw=2))
    frags.append(text(gx - 10, oy + 25, "Час (t) →", size=12, bold=True, anchor="end"))

    frags.append(line(ox, oy, ox, gy, color=INK, sw=2))
    frags.append(arrow(ox, gy + 2, ox, gy - 2, color=INK, sw=2))
    frags.append(text(ox - 10, gy + 15, "Метрика", size=12, bold=True, anchor="end"))

    # Пунктирні лінії порогів
    frags.append(line(ox, y_fire, gx, y_fire, color=POS, sw=1.5, dash="5 4"))
    frags.append(box(210, y_fire - 18, "Порог активації (T_fire = 85%)", size=11, bold=True, color=POS, fill="#fff", stroke="none", pad=2))

    frags.append(line(ox, y_clear, gx, y_clear, color=FIELD, sw=1.5, dash="5 4"))
    frags.append(box(210, y_clear + 18, "Порог деактивації (T_clear = 75%)", size=11, bold=True, color=FIELD, fill="#fff", stroke="none", pad=2))

    # Траєкторія метрики
    pts = [
        (ox, 310), (160, 290), (220, 200), (280, 130), (340, 175),
        (400, 140), (460, 210), (520, 165), (580, 225), (640, 285),
        (700, 295), (760, 320), (820, 310)
    ]
    path_d = "M " + " L ".join(["%.1f %.1f" % p for p in pts])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d, NEG))

    frags.append(circle(280, 130, 5, fill=POS, stroke=INK, sw=1.5))
    frags.append(box(320, 105, "Алерт FIRING\n(перетин T_fire)", size=10, bold=True, fill="#fdecea", stroke=POS, pad=4))

    frags.append(circle(640, 285, 5, fill=FIELD, stroke=INK, sw=1.5))
    frags.append(box(640, 335, "Алерт RESOLVED\n(спад нижче T_clear)", size=10, bold=True, fill="#eafaf0", stroke=FIELD, pad=4))

    frags.append(text(W / 2, H - 20,
                      "Гістерезис вимагає падіння нижче T_clear для зняття алерту, запобігаючи нескінченному спаму.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'alert-flapping-and-hysteresis.svg'), W, H, *frags,
           title="Гістерезис та захист від брязкання (flapping)")


if __name__ == '__main__':
    fig_symptom_vs_cause()
    fig_lifecycle()
    fig_alertmanager_pipeline()
    fig_burn_rate()
    fig_flapping()
    print("All figures generated successfully.")
