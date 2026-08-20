# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Чотирикомпонентний родовід та анатомія модельного артефакту ─────
def fig_model_artifact_lineage_and_anatomy():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 28, "Анатомія модельного артефакту: від чотирикомпонентного родоводу до реєстру",
                      size=15, bold=True, color=INK))

    # Ліва колонка: 4 джерела (Lineage Sources)
    frags.append(text(160, 68, "Чотири опори відтворюваності (Lineage)", size=12, bold=True, color=MUTED))

    sources = [
        ("Код трансформацій (Code)", "Git Commit SHA: a9f84b2c\nПайплайн, фічі, токенізація, пре/постпроцесинг", "#eef4ff", "#2563eb"),
        ("Знімок даних (Data)", "Dataset Hash: dvc:7e10c59a\nНавчальна й валідаційна вибірки, спліти, зрізи", "#f6faf7", FIELD),
        ("Середовище (Environment)", "Env Hash: sha256:4d81f0bc\nPython 3.11, CUDA 12.4, драйвери, random seed", "#fff9e6", "#d97706"),
        ("Навчені ваги (Weights)", "Tensor Hash: sha256:91ca730e\nВаги шарів, ONNX / Safetensors, квантування INT8", "#fee2e2", POS),
    ]

    box_w = 260
    y_start = 90
    y_step = 95
    left_cx = 160

    for i, (title, desc, bg_col, border_col) in enumerate(sources):
        cy = y_start + i * y_step
        sbox, bw, bh = textbox(left_cx, cy, f"{title}\n{desc}", size=11, bold=True,
                               fill=bg_col, stroke=border_col, sw=1.5, pad=8, min_w=box_w)
        frags.append(sbox)
        # Стрілка праворуч до артефакту
        frags.append(arrow(left_cx + box_w / 2 + 5, cy, 375, 250, color=MUTED, sw=1.3))

    # Центральний блок: Запечатаний незмінний пакет (Sealed Immutable Artifact Package)
    frags.append(rect(380, 80, 270, 390, fill="none", stroke=INK, sw=2, rx=8))
    frags.append(text(515, 108, "Незмінний пакет артефакту", size=13, bold=True, color=INK))
    frags.append(text(515, 126, "v2.4.1 [digest: sha256:d8a2...]", size=10, bold=False, color=MUTED))
    frags.append(line(395, 138, 635, 138, color=LINE, sw=1))

    art_sections = [
        ("manifest.json (Родовід і залежності)", "Коміт, датасет, конфіг, автор, час складання", "#ffffff", LINE),
        ("signature.json (Контракт тензорів)", "Вхідні/вихідні типи, форми, валідація діапазонів", "#ffffff", LINE),
        ("metrics.json (Базовий рівень якості)", "ROC-AUC: 0.942, p99: 12ms, похибка за зрізами", "#ffffff", LINE),
        ("model.safetensors / model.onnx", "Бінарні тензори ваг із прямим доступом через mmap", "#ffffff", LINE),
    ]

    cur_ay = 170
    for atitle, adesc, abg, astr in art_sections:
        abox, abw, abh = textbox(515, cur_ay, f"{atitle}\n{adesc}", size=10, bold=True,
                                 fill=abg, stroke=astr, sw=1.2, pad=6, min_w=245)
        frags.append(abox)
        cur_ay += 74

    # Стрілка праворуч до реєстру моделей
    frags.append(arrow(655, 275, 725, 275, color=INK, sw=2))
    frags.append(text(690, 260, "Пуш у реєстр", size=11, bold=True, color=INK))

    # Права колонка: Реєстр моделей та життєвий цикл (Model Registry & Stages)
    frags.append(rect(735, 80, 235, 390, fill="none", stroke="#2563eb", sw=1.8, rx=8))
    frags.append(text(852, 108, "Реєстр моделей (Registry)", size=13, bold=True, color="#2563eb"))
    frags.append(text(852, 126, "CAS + Керування станами", size=10, bold=False, color=MUTED))
    frags.append(line(750, 138, 955, 138, color="#2563eb", sw=1))

    stages = [
        ("1. Draft / Experimental", "Складання артефакту в CI/CD\nАвтоматичні юніт-тести тензорів", "#f3f4f6", MUTED),
        ("2. Staging / Shadow Run", "Тіньовий запуск на реальному трафіку\nЗвірка затримок і пам'яті з baseline", "#fff9e6", "#d97706"),
        ("3. Production (Active)", "Канарковий випуск або Blue/Green\nАтомарне перемикання вказівника", "#f6faf7", FIELD),
        ("4. Archived (Rollback Ready)", "Незмінне збереження попередніх версій\nМиттєвий відкіт за O(1)", "#fee2e2", "#b91c1c"),
    ]

    cur_sy = 170
    for stitle, sdesc, sbg, sstr in stages:
        sbox, sbw, sbh = textbox(852, cur_sy, f"{stitle}\n{sdesc}", size=10, bold=True,
                                 fill=sbg, stroke=sstr, sw=1.2, pad=6, min_w=215)
        frags.append(sbox)
        cur_sy += 74

    render(os.path.join(IMG, 'model-artifact-lineage-and-anatomy.svg'), W, H, *frags,
           title="Анатомія модельного артефакту: родовід, пакет, маніфест і стадії реєстру")


# ── Фігура 2: Порівняння трьох архітектур розміщення інференсу ─────────────────
def fig_model_serving_architectures():
    W, H = 980, 480
    frags = []

    frags.append(text(490, 26, "Архітектури розміщення інференсу: Хмара, Периферійний хаб і Вбудований пристрій",
                      size=14, bold=True, color=INK))

    paradigms = [
        ("Хмарний сервіс (Cloud API)", "gRPC / REST / Triton / TorchServe", [
            ("Обчислення", "Потужні кластери GPU / TPU, dynamic batching"),
            ("Мережа", "Транспорт WAN, затримка p99: 30–120 мс"),
            ("Приватність", "Сирі клієнтські дані передаються в хмару"),
            ("Оновлення", "Миттєве централізоване (Blue/Green, Canary)"),
            ("Вартість", "Висока серверна плата за GPU-години"),
        ], "#eef4ff", "#2563eb"),

        ("Периферійний хаб (Edge Hub)", "Локальний шлюз / Сервер підприємства", [
            ("Обчислення", "Локальні CPU/NPU, помірний паралелізм"),
            ("Мережа", "Локальна мережа LAN, затримка p99: 5–15 мс"),
            ("Приватність", "Дані не залишають контур локальної мережі"),
            ("Оновлення", "Оркестрація через K3s / агенти доставки"),
            ("Вартість", "Баланс між апаратними витратами й трафіком"),
        ], "#fff9e6", "#d97706"),

        ("Вбудований рушій (On-Device)", "Вбудований процес C++/ONNX Runtime / NPU", [
            ("Обчислення", "MCU / мобільний SoC / квантування INT8/FP16"),
            ("Мережа", "Повна автономність (Zero Network), p99 < 1 мс"),
            ("Приватність", "Абсолютна: сирі дані залишаються на чипі"),
            ("Оновлення", "OTA-прошивки або завантаження артефактів"),
            ("Вартість", "Нульові витрати на трафік, жорсткий ліміт RAM"),
        ], "#f6faf7", FIELD),
    ]

    col_w = 295
    col_gap = 20
    left_m = 25
    top_m = 55

    for idx, (title, sub, rows_info, bg_col, border_col) in enumerate(paradigms):
        cx = left_m + idx * (col_w + col_gap) + col_w / 2
        cy = top_m

        hdr_box, hw, hh = textbox(cx, cy + 22, f"{title}\n({sub})", size=12, bold=True,
                                  fill=bg_col, stroke=border_col, sw=1.8, pad=8, min_w=col_w)
        frags.append(hdr_box)

        cur_y = cy + 70
        for r_name, r_val in rows_info:
            rbox, rw, rh = textbox(cx, cur_y + 24, f"{r_name}:\n{r_val}", size=10, bold=False,
                                   fill="#ffffff", stroke=MUTED, sw=1.1, pad=6, min_w=col_w)
            frags.append(rbox)
            cur_y += 56

        # Підсумок внизу картки
        summary_text = (
            "Оптимально для: надвеликих LLM,\nскладного мультимодального пошуку" if idx == 0 else
            "Оптимально для: відеоаналітики заводів,\nлокальних медичних систем" if idx == 1 else
            "Оптимально для: автопілотів, дронів,\nрозумних камер, мобільних застосунків"
        )
        sum_box, sum_w, sum_h = textbox(cx, cur_y + 30, summary_text, size=10, bold=True,
                                        fill=bg_col, stroke=border_col, sw=1.2, pad=6, min_w=col_w)
        frags.append(sum_box)

    render(os.path.join(IMG, 'model-serving-architectures.svg'), W, H, *frags,
           title="Порівняння трьох парадигм розміщення модельного інференсу")


# ── Фігура 3: Дрейф розподілів і контур зворотного зв'язку MLOps ──────────────
def fig_model_drift_and_feedback_loop():
    W, H = 1000, 500
    frags = []

    frags.append(text(500, 26, "Дрейф розподілів даних і замкнений контур зворотного зв'язку MLOps",
                      size=14, bold=True, color=INK))

    # Верхній потік: Обслуговування клієнтів (Live Serving Plane)
    frags.append(rect(30, 55, 940, 110, fill="none", stroke=INK, sw=1.5, rx=8))
    frags.append(text(500, 75, "Площина бойового інференсу (Live Serving Plane)", size=12, bold=True, color=INK))

    frags.append(textbox(130, 115, "Клієнтський трафік\nВхідні ознаки X(t)", size=11, bold=True,
                         fill="#eef4ff", stroke="#2563eb", sw=1.4, pad=6)[0])
    frags.append(arrow(210, 115, 290, 115, color=INK, sw=1.8))

    frags.append(textbox(410, 115, "Інференс-сервер v2.4\n(Атомарне виконання моделі)", size=11, bold=True,
                         fill="#f6faf7", stroke=FIELD, sw=1.6, pad=8)[0])
    frags.append(arrow(530, 115, 610, 115, color=INK, sw=1.8))

    frags.append(textbox(720, 115, "Вихідні передбачення Y(t)\n+ Запис у чергу телеметрії", size=11, bold=True,
                         fill="#eef4ff", stroke="#2563eb", sw=1.4, pad=6)[0])
    frags.append(arrow(830, 115, 910, 115, color=INK, sw=1.8))
    frags.append(text(940, 115, "Клієнт", size=11, bold=True, color=INK, anchor="start"))

    # Відгалуження до моніторингу дрейфу
    frags.append(arrow(720, 145, 720, 195, color=MUTED, sw=1.5))
    frags.append(text(780, 175, "Асинхронний лог", size=10, bold=False, color=MUTED))

    # Середній блок: Детекція дрейфу та SLO (Drift Analysis Engine)
    frags.append(rect(30, 200, 940, 130, fill="none", stroke="#d97706", sw=1.6, rx=8))
    frags.append(text(500, 222, "Моніторинг зсуву розподілів та оцінка SLO дрейфу", size=12, bold=True, color="#d97706"))

    # Блок еталона
    frags.append(textbox(160, 270, "Еталонний розподіл P₀(X)\n(Train/Validation baseline)", size=10, bold=True,
                         fill="#ffffff", stroke=MUTED, sw=1.2, pad=6)[0])
    frags.append(arrow(265, 270, 340, 270, color=MUTED, sw=1.4))

    # Блок обчислення метрик
    frags.append(textbox(490, 270, "Статистичний калькулятор зсуву:\n• PSI (Population Stability Index)\n• KS-тест / Відстань Васерштейна", size=10, bold=True,
                         fill="#fff9e6", stroke="#d97706", sw=1.4, pad=6)[0])
    frags.append(arrow(640, 270, 715, 270, color=MUTED, sw=1.4))

    # Блок живого вікна
    frags.append(textbox(820, 270, "Поточний розподіл P_t(X)\n(Ковзне вікно за 24 год)", size=10, bold=True,
                         fill="#ffffff", stroke=MUTED, sw=1.2, pad=6)[0])

    # Нижній блок: Три рівні реакції контуру зворотного зв'язку
    frags.append(text(500, 355, "Контур автоматичного реагування на основі порогів PSI", size=12, bold=True, color=INK))

    actions = [
        ("PSI < 0.10 (Стабільний стан)", "Розподіл у межах норми.\nМодель не потребує втручання.", "#f6faf7", FIELD),
        ("0.10 ≤ PSI < 0.25 (Помірний дрейф)", "Попередження інженерам.\nАвтоматичний запуск тіньового тесту.", "#fff9e6", "#d97706"),
        ("PSI ≥ 0.25 (Критичний зсув)", "Алерт черговому інженеру.\nТригер конвеєра перенавчання v2.5.", "#fee2e2", POS),
    ]

    for i, (atitle, adesc, abg, astr) in enumerate(actions):
        cx = 175 + i * 325
        cy = 415
        abox, abw, abh = textbox(cx, cy, f"{atitle}\n{adesc}", size=10, bold=True,
                                 fill=abg, stroke=astr, sw=1.4, pad=8, min_w=295)
        frags.append(abox)

    # Зворотна петля від критичного дрейфу назад до інференс-сервера
    frags.append(arrow(825, 455, 825, 480, color=POS, sw=1.5))
    frags.append(line(825, 480, 50, 480, color=POS, sw=1.5))
    frags.append(line(50, 480, 50, 115, color=POS, sw=1.5))
    frags.append(arrow(50, 115, 280, 115, color=POS, sw=1.5))
    frags.append(text(400, 472, "Автоматичне складання артефакту v2.5 та канарковий реліз", size=10, bold=True, color=POS))

    render(os.path.join(IMG, 'model-drift-and-feedback-loop.svg'), W, H, *frags,
           title="Дрейф розподілів даних, пороги PSI та замкнений контур зворотного зв'язку MLOps")


if __name__ == '__main__':
    fig_model_artifact_lineage_and_anatomy()
    fig_model_serving_architectures()
    fig_model_drift_and_feedback_loop()
    print("Всі фігури згенеровано успішно.")
