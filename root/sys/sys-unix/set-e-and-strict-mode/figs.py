# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL  = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL   = "#fdecea"
WARM_FILL  = "#fff6e5"
WARM       = "#b8860b"


# ── 1. Обробка статусу конвеєра: default vs pipefail ──────────────────────────
def fig_pipeline_exit_status_and_pipefail():
    W, H = 1200, 800
    p = []

    p.append(fitbox(50, 30, 1100, 56,
                    "Обробка кодів завершення у конвеєрі: поведінка за замовчуванням проти set -o pipefail",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    # Три процеси у конвеєрі
    # 1. mysqldump (exit 1)
    # 2. gzip (exit 0)
    # 3. s3_upload (exit 0)

    p.append(fitbox(60, 115, 320, 105,
                    "Процес 1: mysqldump\n"
                    "Помилка авторизації / збій СУБД\n"
                    "Потік даних: порожній (0 байтів)\n"
                    "Код виходу: exit 1",
                    size=13, fill=RED_FILL, stroke=POS, bold=True))

    p.append(arrow(383, 167, 437, 167, color=MUTED))
    p.append(fitbox(385, 138, 52, 22, "0 B", size=10, fill=BG, stroke=MUTED))

    p.append(fitbox(440, 115, 320, 105,
                    "Процес 2: gzip -c\n"
                    "Стискає вхідний потік 0 байтів\n"
                    "Генерує заголовок gzip (20 B)\n"
                    "Код виходу: exit 0",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    p.append(arrow(763, 167, 817, 167, color=MUTED))
    p.append(fitbox(765, 138, 52, 22, "20 B", size=10, fill=BG, stroke=MUTED))

    p.append(fitbox(820, 115, 320, 105,
                    "Процес 3: s3_upload\n"
                    "Завантажує 20 байтів у сховище\n"
                    "Мережевий запит успішний\n"
                    "Код виходу: exit 0",
                    size=13, fill=GREEN_FILL, stroke=FIELD, bold=True))

    # Стан масиву PIPESTATUS
    p.append(fitbox(60, 245, 1080, 52,
                    "Внутрішній масив оболонки: PIPESTATUS=( [0]=1  [1]=0  [2]=0 )",
                    size=14, fill=WARM_FILL, stroke=WARM, bold=True))

    # Порівняння режимів: дві великі колонки
    # Ліва колонка: За замовчуванням (Default POSIX)
    p.append(fitbox(60, 320, 525, 340,
                    "Поведінка за замовчуванням (без pipefail)\n\n"
                    "• Оболонка перевіряє код повернення виключно\n"
                    "  з останнього процесу (s3_upload).\n"
                    "• Останній процес завершився успішно: $? = 0.\n"
                    "• Збій першої команди mysqldump повністю ігнорується.\n\n"
                    "НАСЛІДОК:\n"
                    "Пошкоджений бекап (20 байтів) завантажено у хмару,\n"
                    "скрипт вважає операцію успішною і продовжує роботу,\n"
                    "створюючи ілюзію надійного збереження даних.",
                    size=12, fill=RED_FILL, stroke=POS))

    # Права колонка: Режим set -o pipefail
    p.append(fitbox(615, 320, 525, 340,
                    "Режим із прапорцем set -o pipefail\n\n"
                    "• Оболонка сканує масив PIPESTATUS справа наліво.\n"
                    "• Повертає код найправішої команди зі збоєм (exit != 0).\n"
                    "• Підсумковий статус конвеєра: $? = 1.\n\n"
                    "НАСЛІДОК:\n"
                    "Оболонка фіксує аварійний статус конвеєра,\n"
                    "запобігає пошкодженню резервних копій та негайно\n"
                    "передає керування системному обробнику помилок.",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    p.append(fitbox(50, 685, 1100, 75,
                    "Підсумок: без pipefail будь-який конвеєр із фільтром (grep, gzip, tee, awk) у хвості "
                    "приховує аварійне падіння\n"
                    "основного джерела даних, маскуючи фатальні системні збої під успішний результат виконання.",
                    size=13, fill=FILL, stroke=LINE))

    render(os.path.join(IMG, 'pipeline-exit-status-and-pipefail.svg'), W, H, *p,
           title="Обробка статусів конвеєра та прапорець pipefail")


# ── 2. Дерево рішень errexit (set -e) та придушення ──────────────────────────
def fig_errexit_decision_flow_and_bypass():
    W, H = 1200, 840
    p = []

    p.append(fitbox(50, 30, 1100, 56,
                    "Механіка спрацювання set -e (errexit): перевірка статусу та правила придушення",
                    size=15, fill=FILL, stroke=LINE, bold=True))

    # 1. Завершення команди
    p.append(fitbox(400, 110, 400, 50,
                    "Команда або конвеєр завершується зі статусом $?",
                    size=14, fill=FILL, stroke=LINE, bold=True))

    p.append(arrow(600, 160, 600, 195, color=MUTED))

    # 2. Ромб / блок перевірки $? == 0
    p.append(fitbox(430, 195, 340, 50,
                    "Чи статус $? дорівнює 0?",
                    size=13, fill=BLUE_FILL, stroke=NEG, bold=True))

    # Гілка ТАК -> успіх
    p.append(arrow(770, 220, 930, 220, color=FIELD))
    p.append(fitbox(800, 205, 100, 26, "Так ($? = 0)", size=11, fill=BG, stroke=FIELD))
    p.append(fitbox(930, 195, 220, 50,
                    "Продовжити виконання\nнаступного рядка коду",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    # Гілка НІ -> перевірка errexit
    p.append(arrow(600, 245, 600, 285, color=POS))
    p.append(fitbox(610, 252, 90, 24, "Ні ($? != 0)", size=11, fill=BG, stroke=POS))

    p.append(fitbox(430, 285, 340, 50,
                    "Чи активовано set -e (errexit)?",
                    size=13, fill=WARM_FILL, stroke=WARM, bold=True))

    # Гілка НІ (set -e не активовано)
    p.append(arrow(430, 310, 270, 310, color=MUTED))
    p.append(fitbox(300, 298, 90, 24, "Ні (вимкнено)", size=11, fill=BG, stroke=MUTED))
    p.append(fitbox(60, 285, 210, 50,
                    "Продовжити виконання\n(режим за замовчуванням)",
                    size=12, fill=FILL, stroke=MUTED))

    # Гілка ТАК (set -e активовано) -> Перевірка контексту придушення
    p.append(arrow(600, 335, 600, 375, color=POS))
    p.append(fitbox(610, 345, 90, 24, "Так (активно)", size=11, fill=BG, stroke=POS))

    p.append(fitbox(330, 375, 540, 60,
                    "Чи перебуває виклик у контексті перевірки умов?\n"
                    "(POSIX Suppression Rules)",
                    size=14, fill=BLUE_FILL, stroke=NEG, bold=True))

    # Дві гілки від контексту придушення
    # Ліва: ТАК (придушено)
    p.append(arrow(330, 405, 180, 470, color=FIELD))
    p.append(fitbox(180, 425, 130, 26, "Так (придушено)", size=11, fill=BG, stroke=FIELD))

    p.append(fitbox(60, 475, 480, 185,
                    "Контексти придушення errexit:\n\n"
                    "1. Умова перевірки: if cmd; then, while cmd; do, until cmd\n"
                    "2. Ліва частина логічного ланцюжка: cmd1 || cmd2, cmd1 && cmd2\n"
                    "3. Заперечення результату: ! cmd\n\n"
                    "ДІЯ: Оболонка НЕ зупиняє скрипт і НЕ викликає trap ERR.\n"
                    "Код виходу передається керуючій конструкції.",
                    size=12, fill=GREEN_FILL, stroke=FIELD))

    # Права: НІ (НЕ придушено -> аварійна зупинка)
    p.append(arrow(870, 405, 1020, 470, color=POS))
    p.append(fitbox(890, 425, 130, 26, "Ні (діє errexit)", size=11, fill=BG, stroke=POS))

    p.append(fitbox(660, 475, 480, 185,
                    "Аварійна зупинка (Fatal Abort):\n\n"
                    "1. Спрацьовує пастка trap '...' ERR (якщо задано)\n"
                    "2. Спрацьовує фінальна пастка trap '...' EXIT\n"
                    "3. Процес негайно завершується з ненульовим кодом $?\n\n"
                    "НАСЛІДОК: Помилка блокує виконання наступних рядків,\n"
                    "запобігаючи лавиноподібній деструкції системи.",
                    size=12, fill=RED_FILL, stroke=POS))

    p.append(fitbox(50, 690, 1100, 115,
                    "Критична пастка функцій: якщо функція містить команди без захисту, але сама викликається\n"
                    "в умові if func; then або func || fallback, режим set -e ВІДМИКАЄТЬСЯ для ВСІХ внутрішніх команд функції.\n"
                    "Усі вкладені збої будуть мовчки проігноровані до повного виходу з функції.",
                    size=13, fill=WARM_FILL, stroke=WARM))

    render(os.path.join(IMG, 'errexit-decision-flow-and-bypass.svg'), W, H, *p,
           title="Дерево рішень та правила придушення set -e")


if __name__ == '__main__':
    fig_pipeline_exit_status_and_pipefail()
    fig_errexit_decision_flow_and_bypass()
