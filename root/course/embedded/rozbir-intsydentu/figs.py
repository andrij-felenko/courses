# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Тріада джерел даних та синхронізація часу ──────────────────────────────
def fig_data_triad():
    W, H = 940, 450
    p = []
    p.append(text(W / 2, 28, "Тріада джерел даних розслідування: три горизонти спостереження на спільній осі часу",
                  size=14, color=INK, bold=True))

    lanes = [
        ("Польотний контролер (FC)", "ULog / DataFlash (50–400 Гц)",
         ["IMU: прискорення, кутові швидкості, кліпінг",
          "EKF: нев'язки (innovations), дисперсії, прапорці",
          "Керування: DesRoll/Pitch vs Roll/Pitch, PWM/DShot",
          "Живлення: напруга шини, струм, просадки"],
         "#eaf3ff", NEG),
        ("Бортовий комп'ютер (SBC)", "systemd / ROS 2 bag (1–50 Гц)",
         ["Система: journalctl, dmesg, падіння 5V, OOM",
          "Навігація: топіки /cmd_vel, /scan лідара, хмара точок",
          "Планувальник: стан місії, черги подій, затримка IPC",
          "Ресурси: завантаження ядер CPU, сплески пам'яті"],
         "#f7faf7", FIELD),
        ("Наземна станція (GCS)", "MAVLink tlog / Radio (1–10 Гц)",
         ["Радіолінк: RSSI, remrssi, втрата пакетів, шум ефіру",
          "Команди: MISSION_ITEM, підтвердження (ACK/NACK)",
          "Дії оператора: зміна режимів, ручне втручання",
          "Повний запис телеметрії з погляду оператора"],
         "#fef9e7", "#d4ac0d"),
    ]

    y_start = 65
    lane_h = 105
    lane_w = 610
    x_lane = 25

    for i, (title_text, subtitle_text, items, bg_col, border_col) in enumerate(lanes):
        y = y_start + i * (lane_h + 15)
        p.append(rect(x_lane, y, lane_w, lane_h, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        p.append(text(x_lane + 16, y + 24, title_text, size=13, color=INK, anchor="start", bold=True))
        p.append(text(x_lane + 220, y + 24, "—  " + subtitle_text, size=11.5, color=MUTED, anchor="start"))

        # Дві колонки пунктів
        col1_items = items[:2]
        col2_items = items[2:]
        for j, it in enumerate(col1_items):
            p.append(text(x_lane + 16, y + 52 + j * 24, "• " + it, size=11, color=INK, anchor="start"))
        for j, it in enumerate(col2_items):
            p.append(text(x_lane + 310, y + 52 + j * 24, "• " + it, size=11, color=INK, anchor="start"))

    # Права панель: Синхронізація часу та часова прив'язка
    x_sync = 660
    w_sync = 255
    h_sync = 345
    p.append(rect(x_sync, y_start, w_sync, h_sync, fill=FILL, stroke=LINE, sw=1.6, rx=8))
    p.append(text(x_sync + w_sync / 2, y_start + 26, "Синхронізація шкали", size=13, color=INK, bold=True))
    p.append(text(x_sync + w_sync / 2, y_start + 46, "Прив'язка до єдиного T₀", size=11.5, color=MUTED))

    steps = [
        ("1. GPS Time", "Супутниковий UTC-час\nяк абсолютний якір"),
        ("2. TIMESYNC", "MAVLink RTT-компенсація\nзсуву годинника FC ↔ SBC"),
        ("3. Boot TimeUS", "Монотонний мікросекундний\nтаймер контролера"),
        ("4. Вікно аварії", "Точний збіг мілісекунд\nна всіх трьох потоках"),
    ]

    for k, (st_t, st_d) in enumerate(steps):
        sy = y_start + 70 + k * 65
        p.append(rect(x_sync + 12, sy, w_sync - 24, 54, fill="#ffffff", stroke=MUTED, sw=1.0, rx=5))
        p.append(text(x_sync + 22, sy + 20, st_t, size=11.5, color=NEG if k == 3 else INK, anchor="start", bold=True))
        p.append(mtext(x_sync + 22, sy + 36, st_d, size=10, color=MUTED, anchor="start", lh=1.2))

    # Нижній висновок
    y_bot = 422
    p.append(text(W / 2, y_bot, "Жоден журнал окремо не дає повної картини: FC бачить фізику, SBC — рішення, GCS — наміри оператора",
                  size=11.5, color=MUTED, italic=True))

    return render(os.path.join(OUT, "incident-data-triad.svg"), W, H, *p)


# ── 2. Дерево діагностичних рішень пошуку першопричини ────────────────────────
def fig_decision_tree():
    W, H = 960, 480
    p = []
    p.append(text(W / 2, 26, "Дерево діагностичних рішень: розпізнавання відмов за сигнатурами в логах",
                  size=14, color=INK, bold=True))

    # Корінь: Симптом аварії
    root_x = W / 2
    root_y = 60
    b_root, _, _ = textbox(root_x, root_y, "СИМПТОМ: втрата керування, зрив орієнтації або зіткнення",
                           size=12.5, pad=10, fill="#fdecea", stroke=POS, sw=1.8, bold=True)
    p.append(b_root)

    # 3 основні гілки
    col_w = 285
    gap_x = 28
    y_branch = 145

    branches = [
        ("1. ВІДМОВА ЗАЛІЗА (Hardware)",
         [("Асиметрія моторів", "Один мотор = 100%, протилежний = 0%,\nа кутова швидкість наростає\n→ Відмова мотора / ESC / гвинта"),
          ("Зависання давача", "Acc/Gyr = const або тайм-аут I2C,\nнулі в ULog, помилки шини\n→ Апаратний відвал сенсора"),
          ("Провал живлення", "Напруга падає нижче порогу відсічки\nпід час різкого набору газу\n→ Просадка батареї / Brownout")],
         "#fdedec", POS),

        ("2. ЗБІЙ ОЦІНКИ СТАНУ (EKF)",
         [("Магнітна завада", "Mag innovation стрибає зі струмом,\nкурс Yaw розходиться\n→ Наведення від силових кабелів"),
          ("Зрив GNSS / Супутників", "Стрибок HDOP, різке зростання\nvelocity innovation в EKF\n→ Глушіння / супутниковий мультипас"),
          ("Вібраційний шум", "Кліпінг акселерометра > 0,\nрозмах вібрацій > 30 м/с²\n→ Відрив демпфера / резонанс")],
         "#eaf2f8", NEG),

        ("3. АЛГОРИТМІЧНИЙ ЗБІЙ (Logic)",
         [("Зациклення місії", "Апарат кружляє навколо точки,\nрадіус досягнення < зносу вітром\n→ Помилка планування місії"),
          ("Насичення інтегратора", "Integrator windup на обмеженні кута,\nповільне скидання накопиченої сили\n→ Перерегулювання та удар"),
          ("Голодування потоків SBC", "Сплеск затримки /cmd_vel > 500 мс,\nCPU 100%, OOM killer вбив процес\n→ Зрив offboard-контуру")],
         "#f4f6f7", LINE),
    ]

    for idx, (b_title, leaves, b_fill, b_stroke) in enumerate(branches):
        bx = 35 + idx * (col_w + gap_x)
        # Заголовок гілки
        p.append(rect(bx, y_branch, col_w, 36, fill=b_fill, stroke=b_stroke, sw=1.6, rx=6))
        p.append(text(bx + col_w / 2, y_branch + 22, b_title, size=11.5, color=INK, bold=True))

        # Стрілка від кореня до гілки
        p.append(arrow(root_x, root_y + 20, bx + col_w / 2, y_branch - 4, color=MUTED, sw=1.4))

        # Листя (3 діагнози в стовпчик)
        y_leaf = y_branch + 50
        for l_title, l_desc in leaves:
            lh = 76
            p.append(rect(bx, y_leaf, col_w, lh, fill="#ffffff", stroke=MUTED, sw=1.0, rx=5))
            p.append(text(bx + 10, y_leaf + 18, l_title, size=11, color=b_stroke, anchor="start", bold=True))
            p.append(mtext(bx + 10, y_leaf + 36, l_desc, size=9.5, color=INK, anchor="start", lh=1.25))
            y_leaf += lh + 10

    # Нижній висновок
    p.append(text(W / 2, 465, "Діагностика полягає у звірці бажаного з дійсним: чи віддав регулятор команду, і чи був фізичний відгук",
                  size=11, color=MUTED, italic=True))

    return render(os.path.join(OUT, "root-cause-decision-tree.svg"), W, H, *p)


# ── 3. Замкнений цикл усунення відмов: 5 Чому -> SITL -> CI ───────────────────
def fig_five_whys_loop():
    W, H = 940, 420
    p = []
    p.append(text(W / 2, 26, "Замкнений інженерний цикл: перетворення аварійного логу на гарантію ненападу",
                  size=14, color=INK, bold=True))

    blocks = [
        ("1. Інцидент", "Фізична аварія,\nзбір уламків,\nвилучення карток пам'яті", "#fdecea", POS),
        ("2. Синхронізація", "Зведення ULog, ROS bag\nта MAVLink tlog\nна спільну шкалу часу", "#eaf3ff", NEG),
        ("3. Аналіз 5 Чому", "Пошук першопричини:\nвід симптому до прогалини\nв чеклісті чи коді", "#fef9e7", "#d4ac0d"),
        ("4. Log Replay / EKF", "Прогін сирих IMU/GPS\nданих через виправлені\nалгоритми оцінки", "#f7faf7", FIELD),
        ("5. SITL/HIL Тест", "Відтворення аварійного\nсценарію в симуляторі\nз інжекцією відмов", "#f4f6f8", LINE),
        ("6. CI Регресія", "Автоматичний гейт у CI:\nблокування збірки при\nповторенні помилки", "#eafaf1", FIELD),
    ]

    n = len(blocks)
    bw = 135
    bh = 110
    gap = (W - 50 - n * bw) / (n - 1)
    x0 = 25
    y_row = 80

    for i, (title_text, desc_text, fill_col, stroke_col) in enumerate(blocks):
        x = x0 + i * (bw + gap)
        p.append(rect(x, y_row, bw, bh, fill=fill_col, stroke=stroke_col, sw=1.6, rx=8))
        p.append(text(x + bw / 2, y_row + 24, title_text, size=11.5, color=INK, bold=True))
        p.append(mtext(x + bw / 2, y_row + 46, desc_text, size=10, color=MUTED, lh=1.3))

        # Стрілка вперед
        if i < n - 1:
            ax1 = x + bw
            ax2 = x + bw + gap
            p.append(arrow(ax1 + 2, y_row + bh / 2, ax2 - 2, y_row + bh / 2, color=LINE, sw=1.6))

    # Зворотна петля: від CI Регресії назад до системи
    y_loop = 245
    p.append(rect(60, y_loop, W - 120, 135, fill="#fcfcfc", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(W / 2, y_loop + 25, "Чому розбір вважається завершеним лише після створення тесту", size=12.5, color=FIELD, bold=True))

    reasons = [
        ("• Справжнє виправлення", "Зафіксовано не лише заміну деталі, а зміну в коді чи передполітному регламенті."),
        ("• Недопущення рецидиву", "Автоматичний симуляційний тест проганяє точно такий самий збій на кожному коміті."),
        ("• Культура без винних", "Шукаємо системну слабкість у процесі перевірки, а не «хто винен у поломці»."),
    ]

    for k, (head_r, body_r) in enumerate(reasons):
        ry = y_loop + 52 + k * 26
        p.append(text(85, ry, head_r, size=11, color=INK, anchor="start", bold=True))
        p.append(text(275, ry, body_r, size=11, color=MUTED, anchor="start"))

    return render(os.path.join(OUT, "five-whys-regression-loop.svg"), W, H, *p)


if __name__ == "__main__":
    fig_data_triad()
    fig_decision_tree()
    fig_five_whys_loop()
    print("All figures generated successfully.")
