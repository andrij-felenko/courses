# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL  = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL  = "#fff6e5"
RED_FILL   = "#fdecea"
GREY_FILL  = "#eceff1"


# ── 1. Концепція Memory Overcommit та семантичний розрив балона ──────────────
def fig_balloon_concept():
    W, H = 1400, 860
    p = []
    cx = 700
    lx = 360
    rx = 1040

    p.append(text(cx, 40, "МЕХАНІЗМ РОЗДУВАННЯ ТА ЗДУВАННЯ VIRTIO-BALLOON", size=16, bold=True))
    p.append(text(cx, 68, "Подолання семантичного розриву: виділення сторінок у гості та повернення фізичної RAM господарю",
                  size=12.5, color=MUTED))

    # Ліва колонка: INFLATE
    p.append(text(lx, 115, "1. НАДУВАННЯ (INFLATE: ГОСПОДАР ЗАБИРАЄ RAM)", size=14, bold=True, color=POS))

    box1, _, _ = textbox(lx, 180, [
        "1. Запит гіпервізора на надування:",
        "QEMU оновлює num_pages у конфігурації virtio",
        "і надсилає переривання гостю"
    ], size=12, pad=12, fill=WARM_FILL, stroke=LINE, min_w=580)
    p.append(box1)
    p.append(arrow(lx, 215, lx, 255))

    box2, _, _ = textbox(lx, 310, [
        "2. Захоплення сторінок у ядрі гостя:",
        "Драйвер virtio_balloon кличе alloc_pages()",
        "і вилучає кадри з пулу buddy allocator"
    ], size=12, pad=12, fill=BLUE_FILL, stroke=LINE, min_w=580)
    p.append(box2)
    p.append(arrow(lx, 345, lx, 385))

    box3, _, _ = textbox(lx, 440, [
        "3. Передача номерів PFN через virtqueue:",
        "Масив номерів 4 КБ сторінок записується в inflateq;",
        "драйвер сповіщає гіпервізор (kick)"
    ], size=12, pad=12, fill=BLUE_FILL, stroke=LINE, min_w=580)
    p.append(box3)
    p.append(arrow(lx, 475, lx, 515))

    box4, _, _ = textbox(lx, 580, [
        "4. Вивільнення фізичної пам'яті хоста:",
        "QEMU транслює GPA → HVA та викликає",
        "madvise(hva, len, MADV_DONTNEED);",
        "ядро хоста скидає EPT-мапінг і звільняє RAM!"
    ], size=12, pad=14, fill=GREEN_FILL, stroke=FIELD, sw=1.5, min_w=580)
    p.append(box4)

    # Права колонка: DEFLATE
    p.append(text(rx, 115, "2. ЗДУВАННЯ (DEFLATE: ПОВЕРНЕННЯ RAM ГОСТЮ)", size=14, bold=True, color=NEG))

    box5, _, _ = textbox(rx, 180, [
        "1. Зменшення цільового розміру балона:",
        "Гіпервізор зменшує ціль num_pages або",
        "гість відчуває брак RAM (тиск пам'яті)"
    ], size=12, pad=12, fill=WARM_FILL, stroke=LINE, min_w=580)
    p.append(box5)
    p.append(arrow(rx, 215, rx, 255))

    box6, _, _ = textbox(rx, 310, [
        "2. Вилучення сторінок зі списку балона:",
        "Драйвер бере збережені кадри зі списку pages",
        "та формує пакет номерів PFN для повернення"
    ], size=12, pad=12, fill=BLUE_FILL, stroke=LINE, min_w=580)
    p.append(box6)
    p.append(arrow(rx, 345, rx, 385))

    box7, _, _ = textbox(rx, 440, [
        "3. Сповіщення хоста через deflateq:",
        "Драйвер надсилає PFN у чергу deflateq;",
        "хост підтверджує можливість повторного звернення"
    ], size=12, pad=12, fill=BLUE_FILL, stroke=LINE, min_w=580)
    p.append(box7)
    p.append(arrow(rx, 475, rx, 515))

    box8, _, _ = textbox(rx, 580, [
        "4. Повернення сторінок гостьовому алокатору:",
        "Драйвер гостя кличе free_pages(); кадри знову",
        "доступні процесам гостя (хост виділить фізичну",
        "пам'ять на льоту при першому EPT page fault)"
    ], size=12, pad=14, fill=GREEN_FILL, stroke=FIELD, sw=1.5, min_w=580)
    p.append(box8)

    # Підсумковий блок унизу
    bottom_box, _, _ = textbox(cx, 755, [
        "СЕМАНТИЧНИЙ РОЗРИВ РОЗВ'ЯЗАНО:",
        "Гіпервізор не знає внутрішньої структури процесів гостя, але драйвер усередині ядра гостя",
        "діє як легальний споживач пам'яті, блокуючи сторінки від імені хоста."
    ], size=12.5, pad=14, fill=BLUE_FILL, stroke=MUTED, sw=1.2, min_w=1260)
    p.append(bottom_box)

    render(os.path.join(IMG, 'virtio-balloon-concept.svg'), W, H, *p,
           title="Концепція та цикл надування/здування virtio-balloon")


# ── 2. Віртчерги та потоки обміну ─────────────────────────────────────────────
def fig_balloon_queues_flow():
    W, H = 1420, 880
    p = []
    cx = 710

    p.append(text(cx, 40, "АРХІТЕКТУРА ВІРТЧЕРГ VIRTIO-BALLOON", size=16, bold=True))
    p.append(text(cx, 68, "Чотири спеціалізовані черги virtqueue між драйвером гостя та бекендом QEMU/KVM",
                  size=12.5, color=MUTED))

    # Верхній шар: Ядро гостя
    p.append(text(cx, 115, "ГОСТЬОВА СИСТЕМА (LINUX GUEST KERNEL)", size=14, bold=True, color=NEG))
    guest_box, _, _ = textbox(cx, 175, [
        "ДРАЙВЕР virtio_balloon.c",
        "Підсистеми: Buddy Allocator (alloc_pages) · Page Lists (vb->pages) · Memory Shrinker · Statistics Worker"
    ], size=13, pad=14, fill=BLUE_FILL, stroke=LINE, min_w=1260)
    p.append(guest_box)

    # Середній шар: 4 віртчерги
    q_x = [230, 550, 870, 1190]
    queues = [
        ("0: inflateq", "Надування балона", "Масив 32-біт/64-біт PFN\nГість → Хост (alloc_pages)\nЗвільнення RAM хоста", POS),
        ("1: deflateq", "Здування балона", "Масив PFN для повернення\nГість → Хост (free_pages)\nПовернення пам'яті гостю", NEG),
        ("2: statsq", "Статистика пам'яті", "Масив virtio_balloon_stat\nХост запитує телеметрію:\nMemFree, Available, MajorFaults", FIELD),
        ("3: free_page_vq", "Free Page Reporting/Hinting", "Підказки вільних сторінок\nОптимізація міграції ВМ\nReporting блоків MAX_ORDER", INK)
    ]

    for qx, (q_name, q_role, q_desc, color) in zip(q_x, queues):
        # Стрілка з гостя
        p.append(arrow(qx, 215, qx, 265, color=color))
        box, _, _ = textbox(qx, 380, [
            q_name,
            q_role,
            "───────────────"
        ] + q_desc.split('\n'), size=11.5, pad=12, fill=WARM_FILL, stroke=color, sw=1.6, min_w=290)
        p.append(box)
        # Стрілка до хоста
        p.append(arrow(qx, 495, qx, 545, color=color))

    # Нижній шар: Гіпервізор QEMU / KVM
    p.append(text(cx, 580, "ГОСПОДАР ТА ГІПЕРВІЗОР (HOST QEMU / KVM / LIBVIRT)", size=14, bold=True, color=POS))
    host_box, _, _ = textbox(cx, 660, [
        "БЕКЕНД hw/virtio/virtio-balloon.c (QEMU)",
        "Трансляція GPA → HVA · madvise(MADV_DONTNEED) · punch hole у memfd · QMP API (balloon / query-balloon)",
        "Демони автобалонінгу: libvirt / MOM / Proxmox Dynamic Memory Management"
    ], size=12.5, pad=14, fill=GREEN_FILL, stroke=LINE, min_w=1260)
    p.append(host_box)

    # Інформаційна плашка
    info_box, _, _ = textbox(cx, 790, [
        "Синхронізація лічильників:",
        "Конфігураційний простір пристрою містить num_pages (ціль хоста) та actual (підтверджений стан гостя).",
        "Драйвер гостя поступово підганяє actual під num_pages через пакети у віртчергах."
    ], size=12, pad=12, fill=GREY_FILL, stroke=MUTED, sw=1.1, min_w=1260)
    p.append(info_box)

    render(os.path.join(IMG, 'virtio-balloon-queues-flow.svg'), W, H, *p,
           title="Структура віртчерг та потоків керування virtio-balloon")


# ── 3. Взаємодія зі Shrinker та запобігання OOM гостя ────────────────────────
def fig_balloon_shrinker_oom():
    W, H = 1400, 840
    p = []
    cx = 700

    p.append(text(cx, 40, "ЗАХИСТ ВІД OOM: ВЗАЄМОДІЯ VIRTIO-BALLOON ІЗ ПІДСИСТЕМОЮ MM ГОСТЯ", size=16, bold=True))
    p.append(text(cx, 68, "Реєстрація драйвера в системі shrinker дозволяє автоматично здувати балон під час дефіциту пам'яті",
                  size=12.5, color=MUTED))

    # Стовпчик 1: Звичайний стан
    col1_x = 260
    p.append(text(col1_x, 120, "1. ШТАТНИЙ СТАН", size=13.5, bold=True))
    b1, _, _ = textbox(col1_x, 210, [
        "Балон роздуто на 8 ГБ",
        "Сторінки у списку vb->pages",
        "Buddy allocator має запас RAM",
        "Застосунки працюють стабільно"
    ], size=12, pad=12, fill=GREEN_FILL, stroke=LINE, min_w=360)
    p.append(b1)

    # Стовпчик 2: Сплеск навантаження
    col2_x = 700
    p.append(text(col2_x, 120, "2. ДЕФІЦИТ RAM У ГОСТІ", size=13.5, bold=True, color=POS))
    b2, _, _ = textbox(col2_x, 210, [
        "Сплеск пам'яті застосунків",
        "Рівень вільної RAM падає нижче",
        "водяного знака wmark_low",
        "kswapd починає пряме вивільнення"
    ], size=12, pad=12, fill=WARM_FILL, stroke=POS, sw=1.5, min_w=380)
    p.append(b2)

    # Стовпчик 3: Дія Shrinker
    col3_x = 1140
    p.append(text(col3_x, 120, "3. ПОРЯТУНОК ЧЕРЕЗ SHRINKER", size=13.5, bold=True, color=FIELD))
    b3, _, _ = textbox(col3_x, 210, [
        "Ядро викликає shrinker_scan()",
        "virtio_balloon_shrinker_scan()",
        "здуває балон на вимогу ядра MM,",
        "повертаючи сторінки алокатору"
    ], size=12, pad=12, fill=BLUE_FILL, stroke=FIELD, sw=1.5, min_w=360)
    p.append(b3)

    p.append(arrow(450, 210, 500, 210))
    p.append(arrow(895, 210, 955, 210))

    # Нижня частина: Порівняння сценаріїв
    p.append(text(cx, 340, "НАСЛІДКИ НАЯВНОСТІ / ВІДСУТНОСТІ ПРАПОРЦЯ VIRTIO_BALLOON_F_DEFLATE_ON_OOM", size=14, bold=True))

    # Сценарій без автоздування
    bad_box, _, _ = textbox(360, 480, [
        "БЕЗ АВТОЗДУВАННЯ / БЕЗ SHRINKER:",
        "1. Балон утримує 8 ГБ як звичайний процес.",
        "2. Ядро гостя вичерпує сторінки кешу й анонімної пам'яті.",
        "3. Викликається функція out_of_memory().",
        "4. OOM Killer знищує базу даних або веб-сервер!",
        "5. Результат: аварія сервісу за наявності гігабайтів у балоні."
    ], size=12, pad=14, fill=RED_FILL, stroke=POS, sw=1.6, min_w=620)
    p.append(bad_box)

    # Сценарій зі shrinker
    good_box, _, _ = textbox(1040, 480, [
        "З УВІМКНЕНИМ SHRINKER ТА DEFLATE_ON_OOM:",
        "1. Ядро гостя сприймає балон як резервуар сторінок.",
        "2. При падінні free RAM балон автоматично стискається.",
        "3. Сторінки повертаються до buddy allocator без OOM.",
        "4. Клієнтські процеси отримують пам'ять без затримок.",
        "5. Результат: повна стабільність гостьової операційної системи."
    ], size=12, pad=14, fill=GREEN_FILL, stroke=FIELD, sw=1.6, min_w=620)
    p.append(good_box)

    # Висновок унизу
    bottom_warn, _, _ = textbox(cx, 680, [
        "ПРАВИЛО БАЛАНСУ ПАМ'ЯТІ У ХМАРАХ:",
        "Балонінг ефективний лише тоді, коли гість може віддати пам'ять без шкоди для власної роботи.",
        "Агресивне надування балона без зворотного клапана (shrinker) перетворює overcommit на аварію гостя."
    ], size=12.5, pad=14, fill=WARM_FILL, stroke=MUTED, sw=1.2, min_w=1300)
    p.append(bottom_warn)

    render(os.path.join(IMG, 'balloon-shrinker-oom.svg'), W, H, *p,
           title="Запобігання аварійному вимкненню процесів гостя через механізм shrinker")


# ── 4. Free Page Reporting проти класичного балонінгу ─────────────────────────
def fig_free_page_reporting():
    W, H = 1420, 860
    p = []
    cx = 710
    lx = 360
    rx = 1060

    p.append(text(cx, 40, "ЕВОЛЮЦІЯ: ТРАДИЦІЙНИЙ PFN-БАЛОНІНГ ПРОТИ FREE PAGE REPORTING", size=16, bold=True))
    p.append(text(cx, 68, "Перехід від поштучного захоплення 4 КБ сторінок до пакетного репортингу блоків buddy allocator",
                  size=12.5, color=MUTED))

    # Ліва колонка: Класичний підхід
    p.append(text(lx, 115, "КЛАСИЧНИЙ VIRTIO-BALLOON (PFN ARRAY)", size=14, bold=True, color=POS))

    b_old1, _, _ = textbox(lx, 190, [
        "1. Посторінковий цикл alloc_pages(order=0):",
        "Драйвер циклічно виділяє мільйони 4 КБ кадрів,",
        "розбиваючи суцільні великі блоки buddy allocator."
    ], size=12, pad=12, fill=WARM_FILL, stroke=LINE, min_w=580)
    p.append(b_old1)
    p.append(arrow(lx, 230, lx, 270))

    b_old2, _, _ = textbox(lx, 320, [
        "2. Передача масивів 32-біт PFN:",
        "Буфери по 256 PFN (1 МБ) женуться через virtqueue.",
        "Для 32 ГБ потрібно 8 388 608 PFN і тисячі VM-exit!"
    ], size=12, pad=12, fill=RED_FILL, stroke=POS, sw=1.4, min_w=580)
    p.append(b_old2)
    p.append(arrow(lx, 365, lx, 405))

    b_old3, _, _ = textbox(lx, 465, [
        "3. Наслідки класичного підходу:",
        "• Високе навантаження на vCPU під час надування;",
        "• Фрагментація пам'яті гостя (руйнування HugePages);",
        "• Обмеження 32-біт PFN межею 16 ТБ RAM гостя."
    ], size=12, pad=12, fill=GREY_FILL, stroke=MUTED, min_w=580)
    p.append(b_old3)

    # Права колонка: Free Page Reporting
    p.append(text(rx, 115, "FREE PAGE REPORTING (VIRTIO_BALLOON_F_REPORTING)", size=14, bold=True, color=FIELD))

    b_new1, _, _ = textbox(rx, 190, [
        "1. Інтеграція з ядром mm (Linux 5.7+):",
        "page_reporting_register() підключає хук до buddy allocator.",
        "Сторінки НЕ вилучаються з пулу вільних!"
    ], size=12, pad=12, fill=GREEN_FILL, stroke=LINE, min_w=580)
    p.append(b_new1)
    p.append(arrow(rx, 230, rx, 270))

    b_new2, _, _ = textbox(rx, 320, [
        "2. Репортинг великими блоками (MAX_ORDER - 1):",
        "Ядро повідомляє про цілі діапазони (наприклад, 2 МБ/4 МБ)",
        "через список scatter-gather без розбиття на 4 КБ."
    ], size=12, pad=12, fill=GREEN_FILL, stroke=FIELD, sw=1.4, min_w=580)
    p.append(b_new2)
    p.append(arrow(rx, 365, rx, 405))

    b_new3, _, _ = textbox(rx, 465, [
        "3. Переваги Free Page Reporting:",
        "• Нульове навантаження на процесор у стані спокою;",
        "• Збереження прозорих HugePages (THP) у хості;",
        "• Миттєве повернення RAM гостю без запитів deflate."
    ], size=12, pad=12, fill=BLUE_FILL, stroke=MUTED, min_w=580)
    p.append(b_new3)

    # Зведена порівняльна таблиця внизу
    comp_box, _, _ = textbox(cx, 680, [
        "ПОРІВНЯННЯ ПРОДУКТИВНОСТІ ДВОХ ПІДХОДІВ ПРИ ОЧИЩЕННІ 32 ГБ RAM:",
        "Параметр                      Класичний балон (PFN)          Free Page Reporting (5.7+)",
        "Одиниця передачі              4 КБ (32-біт PFN)              Блок 2–4 МБ (scatter-gather)",
        "Кількість дескрипторів        8 388 608 елементів            8 192 діапазони",
        "Час вивільнення 32 ГБ         ~1200–2500 мс (високий CPU)     ~15–40 мс (майже непомітно)",
        "Вплив на HugeTLB хоста        Руйнує 2 МБ сторінки хоста     Зберігає 2 МБ сторінки неушкодженими"
    ], size=12, pad=14, fill=WARM_FILL, stroke=LINE, min_w=1280)
    p.append(comp_box)

    render(os.path.join(IMG, 'free-page-reporting.svg'), W, H, *p,
           title="Архітектурні відмінності між класичним балонінгом та Free Page Reporting")


if __name__ == '__main__':
    fig_balloon_concept()
    fig_balloon_queues_flow()
    fig_balloon_shrinker_oom()
    fig_free_page_reporting()
    print("All figures generated successfully.")
