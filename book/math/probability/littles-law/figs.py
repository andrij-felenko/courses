# -*- coding: utf-8 -*-
"""Фігури для теми «Закон Літтла та аналіз черг у комп'ютерних системах» (book/math/probability/littles-law)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_littles_law_intuition():
    """fig1-littles-law-intuition.svg: Геометричне виведення закону Літтла через подвійний підрахунок площі під графіком зайнятості."""
    W, H = 880, 460
    frags = []

    # Фон і заголовок
    frags.append(rect(10, 10, 860, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Геометрична інтуїція закону Літтла: площа під траєкторією системи", size=15, bold=True, color="#1e293b"))

    # Графік: Осі координат
    # OX: Час t (від 0 до T), OY: Кількість заявок N(t)
    ox, oy = 80, 290
    gw, gh = 460, 220

    # Осі
    frags.append(arrow(ox, oy, ox + gw + 20, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.8))
    frags.append(text(ox + gw + 35, oy + 4, "Час t", size=12, bold=True, color=INK, anchor="start"))
    frags.append(text(ox, oy - gh - 28, "Кількість N(t)", size=12, bold=True, color=INK))

    # Позначки на осі X: 0, t1, t2, t3, ..., T
    frags.append(text(ox, oy + 18, "0", size=11, color=MUTED))
    frags.append(line(ox + 440, oy - 3, ox + 440, oy + 3, color=LINE, sw=1.5))
    frags.append(text(ox + 440, oy + 18, "T", size=12, bold=True, color=INK))

    # Сходинковий графік зайнятості N(t)
    # Траєкторія заявок:
    # Заявка 1: [30..190], Заявка 2: [80..280], Заявка 3: [150..340], Заявка 4: [220..410], Заявка 5: [300..430]
    # Зафарбовані горизонтальні смуги (індивідуальний час Wi)
    # Заявка 1 (y=oy-30)
    frags.append(rect(ox + 30, oy - 35, 160, 30, fill="#dbeafe", stroke=BLUE_S, sw=1.2, rx=3))
    frags.append(text(ox + 110, oy - 18, "Заявка 1: W₁", size=11, bold=True, color=BLUE_S))

    # Заявка 2 (y=oy-70)
    frags.append(rect(ox + 80, oy - 70, 200, 30, fill="#e0e7ff", stroke="#4f46e5", sw=1.2, rx=3))
    frags.append(text(ox + 180, oy - 53, "Заявка 2: W₂", size=11, bold=True, color="#4f46e5"))

    # Заявка 3 (y=oy-105)
    frags.append(rect(ox + 150, oy - 105, 190, 30, fill="#f3e8ff", stroke=PURPLE_S, sw=1.2, rx=3))
    frags.append(text(ox + 245, oy - 88, "Заявка 3: W₃", size=11, bold=True, color=PURPLE_S))

    # Заявка 4 (y=oy-140)
    frags.append(rect(ox + 220, oy - 140, 190, 30, fill="#fef3c7", stroke=AMBER_S, sw=1.2, rx=3))
    frags.append(text(ox + 315, oy - 123, "Заявка 4: W₄", size=11, bold=True, color=AMBER_S))

    # Заявка 5 (y=oy-175)
    frags.append(rect(ox + 300, oy - 175, 130, 30, fill="#dcfce7", stroke=GREEN_S, sw=1.2, rx=3))
    frags.append(text(ox + 365, oy - 158, "Заявка 5: W₅", size=11, bold=True, color=GREEN_S))

    # Загальна сходинкова лінія контуру
    # frags.append(...)
    steps_path = f"M {ox} {oy} L {ox+30} {oy} L {ox+30} {oy-35} L {ox+80} {oy-35} L {ox+80} {oy-70} L {ox+150} {oy-70} L {ox+150} {oy-105} L {ox+190} {oy-105} L {ox+190} {oy-70} L {ox+220} {oy-70} L {ox+220} {oy-105} L {ox+280} {oy-105} L {ox+280} {oy-70} L {ox+300} {oy-70} L {ox+300} {oy-105} L {ox+340} {oy-105} L {ox+340} {oy-70} L {ox+410} {oy-70} L {ox+410} {oy-35} L {ox+430} {oy-35} L {ox+430} {oy} L {ox+440} {oy}"
    frags.append(f'<path d="{steps_path}" fill="none" stroke="#1e293b" stroke-width="2.2"/>')

    # Пояснення під графіком
    frags.append(text(300, 335, "Площа під графіком = Інтеграл ∫₀ᵀ N(t) dt = Сума смуг ∑ Wᵢ", size=12, bold=True, color="#0f172a"))

    # Дві перспективи інтегрування (Вертикальна vs Горизонтальна)
    b_vert, _, _ = textbox(190, 395, "Вертикальний розріз (миттєвий стан):\nСередня кількість заявок:\nL = (1 / T) · ∫₀ᵀ N(t) dt", size=11, fill=BLUE_F, stroke=BLUE_S)
    b_horiz, _, _ = textbox(430, 395, "Горизонтальний розріз (час заявок):\nСередній час перебування однієї заявки:\nW = (1 / A(T)) · ∑ᵢ Wᵢ", size=11, fill=PURPLE_F, stroke=PURPLE_S)
    frags += [b_vert, b_horiz]

    # Правий блок: Алгебраїчне зведення до L = λ · W
    frags.append(rect(590, 55, 265, 380, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(722, 80, "Алгебраїчна тотожність", size=13, bold=True, color="#0f172a"))

    txt_proof = (
        "Загальна площа S(T):\n"
        "S(T) = ∫₀ᵀ N(t) dt ≈ ∑ᵢ₌₁ᴬ⁽ᵀ⁾ Wᵢ\n\n"
        "Поділимо обидві частини на T:\n"
        "S(T) / T = (1 / T) · ∑ᵢ₌₁ᴬ⁽ᵀ⁾ Wᵢ\n\n"
        "Помножимо й поділимо на A(T):\n"
        "= [ A(T) / T ] · [ (1 / A(T)) ∑ᵢ Wᵢ ]\n\n"
        "При T → ∞ за ергодичності:\n"
        "• S(T) / T → L  (середня черга)\n"
        "• A(T) / T → λ  (інтенсивність)\n"
        "• (1/A(T)) ∑ Wᵢ → W (сер. час)\n\n"
        "Отримуємо фундаментальний зв'язок:\n"
        "            L = λ · W"
    )
    b_alg, _, _ = textbox(722, 255, txt_proof, size=11, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_alg)

    render(os.path.join(IMG, "fig1-littles-law-intuition.svg"), W, H, *frags)


def fig_system_vs_queue():
    """fig2-system-vs-queue.svg: Декомпозиція системи: закон Літтла для всієї системи, черги очікування та обслуговуючого вузла."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 32, "Декомпозиція системи: застосування закону Літтла до підсистем", size=15, bold=True, color="#1e293b"))

    # Зовнішня рамка "Загальна система"
    frags.append(rect(100, 60, 680, 240, fill="#f8fafc", stroke=BLUE_S, sw=2, rx=8))
    frags.append(text(440, 85, "Загальна система: L = λ · W", size=14, bold=True, color=BLUE_S))

    # Вхідний потік (зліва від зовнішньої рамки)
    frags.append(arrow(15, 180, 95, 180, color=BLUE_S, sw=2.2))
    frags.append(text(55, 145, "Вхід λ", size=12, bold=True, color=BLUE_S))

    # Підсистема 1: Буфер очікування (Черга)
    frags.append(rect(130, 110, 260, 140, fill=AMBER_F, stroke=AMBER_S, sw=1.8, rx=6))
    frags.append(text(260, 135, "Буфер очікування (Черга)", size=13, bold=True, color=AMBER_S))
    txt_q = "• Середня довжина: L_q\n• Середній час очікування: W_q\n\nЗакон Літтла для черги:\nL_q = λ · W_q"
    b_q, _, _ = textbox(260, 195, txt_q, size=11, fill="#ffffff", stroke=AMBER_S)
    frags.append(b_q)

    # Перехід від черги до сервера
    frags.append(arrow(395, 180, 485, 180, color=LINE, sw=2))

    # Підсистема 2: Обслуговуючий вузол (Сервер)
    frags.append(rect(490, 110, 260, 140, fill=GREEN_F, stroke=GREEN_S, sw=1.8, rx=6))
    frags.append(text(620, 135, "Обслуговуючий вузол (Сервер)", size=13, bold=True, color=GREEN_S))
    txt_s = "• Середня зайнятість: L_s = ρ\n• Час обслуговування: W_s = 1/μ\n\nЗакон Літтла для сервера:\nL_s = λ · W_s = λ / μ = ρ"
    b_s, _, _ = textbox(620, 195, txt_s, size=11, fill="#ffffff", stroke=GREEN_S)
    frags.append(b_s)

    # Вихідний потік (справа від зовнішньої рамки)
    frags.append(arrow(785, 180, 865, 180, color=GREEN_S, sw=2.2))
    frags.append(text(825, 145, "Вихід λ", size=12, bold=True, color=GREEN_S))

    # Нижній блок: Адитивність величин
    txt_add = (
        "Адитивність часу та заявок:  Час перебування W = W_q + W_s  |  Кількість у системі L = L_q + L_s\n"
        "L = L_q + L_s = λ · W_q + λ · W_s = λ · (W_q + W_s) = λ · W  (справджується для довільної кількості каскадів)"
    )
    b_add, _, _ = textbox(440, 355, txt_add, size=11, bold=True, fill="#f1f5f9", stroke="#475569")
    frags.append(b_add)

    render(os.path.join(IMG, "fig2-system-vs-queue.svg"), W, H, *frags)


def fig_concurrency_latency_knee():
    """fig3-concurrency-latency-knee.svg: Нелінійне зростання затримки та черги при зростанні коефіцієнта завантаження rho -> 1."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 30, "Нелінійний відгук черги при зростанні завантаження ρ = λ / μ", size=15, bold=True, color="#1e293b"))

    # Графік: OX - коефіцієнт завантаження ρ (від 0.0 до 1.0), OY - Середній час W або середня черга L
    ox, oy = 80, 360
    gw, gh = 430, 290

    frags.append(arrow(ox, oy, ox + gw + 25, oy, color=LINE, sw=1.8))
    frags.append(arrow(ox, oy, ox, oy - gh - 20, color=LINE, sw=1.8))
    frags.append(text(ox + gw + 30, oy + 4, "Завантаження ρ", size=12, bold=True, color=INK, anchor="start"))
    frags.append(text(ox, oy - gh - 26, "Час відгуку W / Кількість L", size=12, bold=True, color=INK))

    # Зони: Лінійна (0.0..0.6), Перегин/Коліно (0.6..0.8), Аварійна зона (0.8..1.0)
    frags.append(rect(ox, oy - gh, int(0.6 * gw), gh, fill="#f0fdf4", stroke="none"))
    frags.append(rect(ox + int(0.6 * gw), oy - gh, int(0.2 * gw), gh, fill="#fefce8", stroke="none"))
    frags.append(rect(ox + int(0.8 * gw), oy - gh, int(0.2 * gw), gh, fill="#fef2f2", stroke="none"))

    # Позначки по OX: 0.0, 0.2, 0.4, 0.6, 0.8, 1.0
    for i in range(6):
        rho_val = i * 0.2
        px = ox + int(rho_val * gw)
        frags.append(line(px, oy - 4, px, oy + 4, color=LINE, sw=1.2))
        frags.append(text(px, oy + 18, f"{rho_val:.1f}", size=11, color=INK))

    # Вертикальна асимптота при ρ = 1.0
    frags.append(line(ox + gw, oy, ox + gw, oy - gh - 10, color=RED_S, sw=1.5, dash="4 4"))
    frags.append(text(ox + gw, oy - gh - 18, "ρ = 1.0 (Бар'єр)", size=11, bold=True, color=RED_S))

    # Крива M/M/1: W(rho) = W_s / (1 - rho). Нехай W_s = 20px
    pts = [
        (0.0, 20), (0.1, 22), (0.2, 25), (0.3, 28), (0.4, 33), (0.5, 40),
        (0.6, 50), (0.7, 66), (0.75, 80), (0.8, 100), (0.85, 133), (0.88, 166),
        (0.90, 200), (0.92, 250), (0.935, 290)
    ]
    path_d = ["M"]
    for idx, (r, h_val) in enumerate(pts):
        px = ox + r * gw
        py = oy - h_val
        path_d.append(f"{px:.1f} {py:.1f}" if idx == 0 else f"L {px:.1f} {py:.1f}")
    frags.append(f'<path d="{" ".join(path_d)}" fill="none" stroke="{RED_S}" stroke-width="2.8"/>')

    # Точка коліна (Knee point) при rho ≈ 0.8
    frags.append(circle(ox + 0.8 * gw, oy - 100, 5, fill=AMBER_S, stroke="#ffffff", sw=2))

    # Підписи зон на графіку у вільних місцях
    frags.append(text(ox + 0.3 * gw, oy - 80, "Лінійна зона (ρ < 0.6)\nW ≈ W_s (черга порожня)", size=11, bold=True, color=GREEN_S))
    frags.append(text(ox + 0.55 * gw, oy - 230, "Перегин (коліно ρ ≈ 0.7..0.8)", size=11, bold=True, color=AMBER_S))
    frags.append(text(ox + 0.88 * gw, oy - 270, "Колапс (ρ → 1)\nW → ∞, L → ∞", size=11, bold=True, color=RED_S))

    # Правий блок із поясненням відмінності Літтла від M/M/1
    frags.append(rect(550, 55, 310, 360, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(705, 80, "Лінійність vs Нелінійність", size=13, bold=True, color="#0f172a"))

    txt_knee = (
        "1. Закон Літтла (L = λ · W):\n"
        "• Лінійно пов'язує СЕРЕДНІ значення.\n"
        "• Якщо затримка W виросла в 10 разів,\n"
        "  кількість заявок L виросте рівно в 10 р.\n\n"
        "2. Формула М/М/1 (W = 1 / (μ - λ)):\n"
        "• Пояснює, ЧОМУ саме затримка W росте.\n"
        "• При ρ → 1 знаменник (1 - ρ) прямує до 0.\n"
        "• Стохастичні сплески не встигають\n"
        "  розсмоктуватися між надходженнями.\n\n"
        "Практичне правило архітектури:\n"
        "Сервери розраховують на ρ ≤ 0.7..0.75.\n"
        "Робота при ρ > 0.85 гарантує черговий\n"
        "колапс при найменшому сплеску трафіку."
    )
    b_info, _, _ = textbox(705, 245, txt_knee, size=11, fill="#ffffff", stroke=BLUE_S)
    frags.append(b_info)

    render(os.path.join(IMG, "fig3-concurrency-latency-knee.svg"), W, H, *frags)


def fig_computer_systems_mapping():
    """fig4-computer-systems-mapping.svg: Застосування закону Літтла на всіх рівнях комп'ютерних систем."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 30, "Закон Літтла на всіх рівнях обчислювальної ієрархії", size=15, bold=True, color="#1e293b"))

    # 4 квадранти: Веб-сервери/Пул з'єднань, TCP/BDP, CPU Pipeline/ROB, NVMe/Storage
    cards = [
        (30, 55, 400, 170, BLUE_F, BLUE_S, "1. Веб-сервери та пули потоків", 
         "• Формула: Concurrent_Requests = Throughput · Latency\n"
         "• Приклад: 10 000 req/s при Latency = 50 ms (0.05 s)\n"
         "• Конкурентність: L = 10 000 · 0.05 = 500 in-flight запитів\n"
         "• Висновок: Пул з'єднань та файлові дескриптори\n"
         "  мусять вміщувати щонайменше 500 одночасних слотів."),

        (450, 55, 400, 170, PURPLE_F, PURPLE_S, "2. Мережевий стек: TCP Bandwidth-Delay Product",
         "• Формула: In_Flight_Bytes = Bandwidth · RTT (BDP)\n"
         "• Приклад: 10 Gbit/s канал, RTT = 40 ms (0.04 s)\n"
         "• Буфер у польоті: L = 1.25 GB/s · 0.04 s = 50 MB\n"
         "• Висновок: TCP Window Size мусить бути ≥ 50 MB,\n"
         "  інакше канал простоюватиме в очікуванні ACK."),

        (30, 245, 400, 170, AMBER_F, AMBER_S, "3. Процесори: Буфер перевпорядкування (ROB)",
         "• Формула: In_Flight_Instructions = IPC · Memory_Latency\n"
         "• Приклад: IPC = 4 інструкції/такт, промах L3 = 200 тактів\n"
         "• Вікно виконання: L = 4 · 200 = 800 інструкцій\n"
         "• Висновок: Щоб приховати затримку звернення до RAM,\n"
         "  процесорний Out-of-Order ROB мусить мати сотні слотів."),

        (450, 245, 400, 170, GREEN_F, GREEN_S, "4. Накопичувачі: Глибина черги NVMe (Queue Depth)",
         "• Формула: Queue_Depth = IOPS · Storage_Latency\n"
         "• Приклад: NVMe видає 500 000 IOPS при затримці 0.2 ms\n"
         "• Глибина черги: L = 500 000 · 0.0002 s = 100 команд\n"
         "• Висновок: Щоб утилізувати всі паралельні канали флеш-пам'яті,\n"
         "  драйвер мусить підтримувати глибину черги QD ≥ 100.")
    ]

    for x, y, w, h, fill_c, str_c, title_c, body_c in cards:
        frags.append(rect(x, y, w, h, fill=fill_c, stroke=str_c, sw=1.5, rx=8))
        frags.append(text(x + w/2, y + 24, title_c, size=12, bold=True, color=str_c))
        b_c, _, _ = textbox(x + w/2, y + 98, body_c, size=10, fill="#ffffff", stroke=str_c)
        frags.append(b_c)

    render(os.path.join(IMG, "fig4-computer-systems-mapping.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_littles_law_intuition()
    fig_system_vs_queue()
    fig_concurrency_latency_knee()
    fig_computer_systems_mapping()
    print("All Little's Law figures generated successfully.")
