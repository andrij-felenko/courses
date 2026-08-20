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


# ── Фігура 1: Деплой ≠ Реліз ───────────────────────────────────────────────
def fig_deployment_vs_release():
    W, H = 960, 460
    frags = []

    # Верхня колонка: Деплой (фізичне розгортання)
    y_top = 110
    frags.append(box(200, y_top, "1. Деплой на сервери\n(код потрапляє в прод)",
                     size=13, bold=True, fill="#e8f0ff", stroke=NEG, min_w=240))
    frags.append(box(540, y_top, "Стан у системі:\nновий код спить за прапорцем",
                     size=12, fill="#f4f6f8", stroke=MUTED, min_w=280))
    frags.append(box(830, y_top, "Трафік:\n100% на старому коді",
                     size=12, bold=True, fill="#eafaf0", stroke=FIELD, min_w=170))

    frags.append(arrow(325, y_top, 395, y_top, color=NEG, sw=2))
    frags.append(arrow(685, y_top, 740, y_top, color=FIELD, sw=2))

    # Розділювальна лінія між деплоєм і релізом
    y_mid = 225
    frags.append(line(70, y_mid, 890, y_mid, color=MUTED, sw=1.5, dash="6 4"))
    frags.append(box(W / 2 + 50, y_mid, "Рішення в рантаймі: прапорець перемикає поведінку без повторного розгортання",
                     size=11, bold=True, fill="#fff", stroke=MUTED, pad=6))

    # Нижня колонка: Реліз (відкриття користувачам)
    y_bot = 340
    frags.append(box(200, y_bot, "2. Реліз для користувачів\n(керування видимістю)",
                     size=13, bold=True, fill="#fff3e0", stroke=POS, min_w=240))
    frags.append(box(540, y_bot, "Поступова розкатка:\n1% → 10% → 50% → 100% за хешем",
                     size=12, fill="#fdf6e3", stroke=POS, min_w=280))
    frags.append(box(830, y_bot, "Відкат при збої:\nмиттєве 0% без перезбірки",
                     size=12, bold=True, fill="#fdecea", stroke=POS, min_w=170))

    frags.append(arrow(325, y_bot, 395, y_bot, color=POS, sw=2))
    frags.append(arrow(685, y_bot, 740, y_bot, color=POS, sw=2))

    # Зв'язок між етапами зліва: стрілка від верхнього блоку до проміжного і далі вниз
    y_label = 225
    frags.append(box(100, y_label, "деплой готовий →\nпочаток релізу",
                     size=10, fill="#fff", stroke=INK, pad=5))
    frags.append(arrow(150, y_top + 34, 100, y_label - 22, color=INK, sw=1.8))
    frags.append(arrow(100, y_label + 22, 150, y_bot - 34, color=INK, sw=1.8))

    frags.append(text(W / 2, H - 20,
                      "Деплой — це технічна доставка байтів на машини; реліз — це надання можливості користувачам.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'deployment-vs-release.svg'), W, H, *frags,
           title="Розділення деплою та релізу: керування видимістю коду через прапорці")


# ── Фігура 2: Таксономія прапорців за Годжсоном і Фаулером ──────────────────
def fig_taxonomy():
    W, H = 960, 520
    frags = []

    # Координатна сітка 2x2
    ox, oy = 480, 270
    x_min, x_max = 120, 840
    y_min, y_max = 70, 470

    # Осі
    frags.append(line(x_min, oy, x_max, oy, color=INK, sw=2))
    frags.append(arrow(x_max - 2, oy, x_max + 2, oy, color=INK, sw=2))
    frags.append(text(x_max - 10, oy - 14, "Тривалість життя →", size=12, bold=True, anchor="end"))
    frags.append(text(x_min + 30, oy + 20, "короткоживучі (дні/тижні)", size=11, color=MUTED, anchor="start"))
    frags.append(text(x_max - 30, oy + 20, "довгоживучі (місяці/роки)", size=11, color=MUTED, anchor="end"))

    frags.append(line(ox, y_max, ox, y_min, color=INK, sw=2))
    frags.append(arrow(ox, y_min + 2, ox, y_min - 2, color=INK, sw=2))
    frags.append(text(ox + 16, y_min + 16, "↑ Динамічність рішень", size=12, bold=True, anchor="start"))
    frags.append(text(ox + 16, y_max - 14, "статичні / конфігурація", size=11, color=MUTED, anchor="start"))
    frags.append(text(ox + 16, y_min + 36, "динамічні на кожен запит", size=11, color=MUTED, anchor="start"))

    # Чотири квадранти
    # 1. Верхній лівий: Прапорці експериментів (A/B)
    frags.append(box(290, 160,
                     "Прапорці експериментів (A/B)\n• Життя: тижні або місяці\n• Розрахунок: динамічний за користувачем\n• Мета: перевірка гіпотез і метрик",
                     size=11, fill="#eaf0fd", stroke=NEG, pad=8, min_w=290))

    # 2. Верхній правий: Прапорці прав і доступу (Entitlements)
    frags.append(box(670, 160,
                     "Прапорці доступу / прав\n• Життя: роки (постійні)\n• Розрахунок: динамічний за тарифом/роллю\n• Мета: монетизація та преміум-функції",
                     size=11, fill="#fdf6e3", stroke=POS, pad=8, min_w=290))

    # 3. Нижній лівий: Прапорці випуску (Release Toggles)
    frags.append(box(290, 380,
                     "Прапорці випуску (Release)\n• Життя: дні або тижні\n• Розрахунок: когорти або статичний відсоток\n• Мета: безпечний Trunk-Based деплой",
                     size=11, fill="#eafaf0", stroke=FIELD, pad=8, min_w=290))

    # 4. Нижній правий: Експлуатаційні (Ops / Kill Switches)
    frags.append(box(670, 380,
                     "Аварійні рубильники (Ops / Kill Switch)\n• Життя: місяці або роки (постійні)\n• Розрахунок: глобальний або регіональний\n• Мета: деградація під піковим навантаженням",
                     size=11, fill="#fdecea", stroke=POS, pad=8, min_w=290))

    render(os.path.join(IMG, 'flag-quadrant-taxonomy.svg'), W, H, *frags,
           title="Таксономія прапорців: тривалість життя проти динамічності обчислення")


# ── Фігура 3: Внутрішній конвеєр обчислення прапорця ─────────────────────────
def fig_evaluation_pipeline():
    W, H = 960, 480
    frags = []

    # Вхідний контекст ліворуч
    xC = 120
    yMid = 240
    frags.append(box(xC, yMid,
                     "Контекст запиту:\n• user_id: \"usr_8492\"\n• country: \"UA\"\n• plan: \"premium\"\n• app_version: \"3.2.0\"",
                     size=11, fill="#e8f0ff", stroke=NEG, pad=8, min_w=170))

    # Конвеєр SDK у центрі
    steps = [
        (310, "1. Примусове\nперевизначення\n(Override / URL / Debug)"),
        (480, "2. Правила\nтаргетингу\n(Країна / План / Роль)"),
        (650, "3. Хеш-бакет\nрозважування\n(hash(flag:user) % 100)"),
        (820, "4. Значення за\nзамовчуванням\n(Default fallback)")
    ]

    for i, (sx, label) in enumerate(steps):
        frags.append(box(sx, yMid - 40, label, size=11, bold=True, fill="#fff3e0", stroke=POS, pad=8, min_w=140))
        if i > 0:
            prev_x = steps[i - 1][0]
            frags.append(arrow(prev_x + 72, yMid - 40, sx - 72, yMid - 40, color=MUTED, sw=1.5))
            frags.append(text((prev_x + sx) / 2, yMid - 56, "ні", size=10, color=MUTED))

    # Вхідна стрілка від контексту
    frags.append(arrow(xC + 88, yMid - 40, steps[0][0] - 72, yMid - 40, color=NEG, sw=2))

    # Виходи з кожного кроку вниз до результату
    yOut = 390
    frags.append(box(480, yOut,
                     "Результат обчислення: { value: true, variant: \"treatment\", reason: \"RULE_MATCH\" }\n(виконується локально в пам'яті за <0.1 мс)",
                     size=12, bold=True, fill="#eafaf0", stroke=FIELD, pad=8, min_w=680))

    for sx, _ in steps:
        frags.append(arrow(sx, yMid + 15, sx, yOut - 30, color=FIELD, sw=1.8))
        frags.append(text(sx + 14, yMid + 50, "так", size=10, color=FIELD, bold=True))

    frags.append(text(W / 2, H - 16,
                      "SDK послідовно перевіряє правила і повертає значення миттєво без виклику мережі на гарячому шляху.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'evaluation-pipeline.svg'), W, H, *frags,
           title="Конвеєр обчислення прапорця всередині SDK")


# ── Фігура 4: Архітектура дистрибуції: площина керування → SDK ──────────────
def fig_distribution():
    W, H = 960, 480
    frags = []

    # Ліворуч: Панель керування та репозиторій правил
    frags.append(box(160, 150,
                     "Площина керування (Control Plane)\n• UI інженера / менеджера\n• Конфіг у Git (GitOps)\n• Валідація правил і схем",
                     size=11, bold=True, fill="#fdf6e3", stroke=POS, pad=8, min_w=240))

    frags.append(box(160, 320,
                     "Сервер розповсюдження\n(Flag Service / Edge Proxy)\n• Генерація правил конфігурації\n• Кешування та версіонування (ETag)",
                     size=11, fill="#f6f8fb", stroke=INK, pad=8, min_w=240))

    frags.append(arrow(160, 205, 160, 270, color=INK, sw=2))

    # Центр: Канали передачі (Push / Pull)
    frags.append(box(500, 200,
                     "Потоковий Push (SSE / gRPC stream)\nМиттєве оновлення правил (< 1 сек)",
                     size=11, bold=True, fill="#eaf0fd", stroke=NEG, pad=7, min_w=270))
    frags.append(box(500, 320,
                     "Фоновий Pull (полінг з ETag / 304)\nСтійкість при обриві з'єднання",
                     size=11, fill="#f4f6f8", stroke=MUTED, pad=7, min_w=270))

    frags.append(arrow(285, 305, 360, 215, color=NEG, sw=1.8))
    frags.append(arrow(285, 335, 360, 330, color=MUTED, sw=1.8))

    # Праворуч: Застосунок і локальний SDK
    xApp = 800
    frags.append(box(xApp, 260,
                     "Застосунок (Application Node)\n\n"
                     "┌───────────────────────────────┐\n"
                     "│ In-Memory сховище правил      │\n"
                     "│ (атомарний swap копії правил) │\n"
                     "└──────────────┬────────────────┘\n"
                     "               │ 0 мережевих викликів\n"
                     "               ▼\n"
                     "┌───────────────────────────────┐\n"
                     "│ Рушій обчислення (SDK Engine) │\n"
                     "│ hash() + правила (< 0.1 мс)   │\n"
                     "└───────────────────────────────┘",
                     size=10, fill="#eafaf0", stroke=FIELD, pad=10, min_w=260))

    frags.append(arrow(640, 210, 665, 235, color=NEG, sw=1.8))
    frags.append(arrow(640, 320, 665, 285, color=MUTED, sw=1.8))

    frags.append(text(W / 2, H - 16,
                      "Правила доставляються у фоні; саме обчислення виконується повністю в локальній пам'яті вузла.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'distribution-architecture.svg'), W, H, *frags,
           title="Архітектура дистрибуції правил: відділення доставки від обчислення")


# ── Фігура 5: Життєвий цикл прапорця та прибирання боргу ───────────────────
def fig_lifecycle():
    W, H = 960, 460
    frags = []

    stages = [
        (110, "1. Створення", "Код за швом\nСтан: OFF (0%)", "#e8f0ff", NEG),
        (295, "2. Канарка", "Внутрішні юзери\nта 1% трафіку", "#fdf6e3", POS),
        (480, "3. Розкатка", "10% → 50% → 100%\nМоніторинг метрик", "#eaf0fd", NEG),
        (665, "4. Стабілізація", "100% увімкнено\nTTL таймер спливає", "#fff3e0", POS),
        (850, "5. Очищення", "Видалення if/else\nВидалення з конфігу", "#eafaf0", FIELD),
    ]

    yNode = 220
    for i, (sx, title, desc, fill_c, stroke_c) in enumerate(stages):
        frags.append(box(sx, yNode - 40, title, size=12, bold=True, fill=fill_c, stroke=stroke_c, pad=6, min_w=140))
        frags.append(box(sx, yNode + 35, desc, size=11, fill="#fff", stroke=stroke_c, pad=6, min_w=140))
        frags.append(line(sx, yNode - 18, sx, yNode + 10, color=stroke_c, sw=1.5))

        if i < len(stages) - 1:
            next_x = stages[i + 1][0]
            frags.append(arrow(sx + 72, yNode - 40, next_x - 72, yNode - 40, color=INK, sw=1.8))

    # Нижня стрілка відкату з будь-якого етапу розкатки
    yBack = 370
    frags.append(box(480, yBack,
                     "Аварійний відкат (Kill Switch / Rollback): повернення на 0% за секунди без повторного деплою",
                     size=11, bold=True, fill="#fdecea", stroke=POS, pad=8, min_w=680))
    frags.append(arrow(295, yNode + 62, 295, yBack - 22, color=POS, sw=1.5))
    frags.append(arrow(480, yNode + 62, 480, yBack - 22, color=POS, sw=1.5))
    frags.append(arrow(665, yNode + 62, 665, yBack - 22, color=POS, sw=1.5))

    frags.append(text(W / 2, H - 18,
                      "Прапорець є тимчасовим кредитом: життєвий цикл завершується лише повним видаленням мертвої гілки з коду.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, 'flag-lifecycle.svg'), W, H, *frags,
           title="Повний життєвий цикл прапорця функції: від створення до видалення боргу")


if __name__ == '__main__':
    fig_deployment_vs_release()
    fig_taxonomy()
    fig_evaluation_pipeline()
    fig_distribution()
    fig_lifecycle()
    print("ok")
