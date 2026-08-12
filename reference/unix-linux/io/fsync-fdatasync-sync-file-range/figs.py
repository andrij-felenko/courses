# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT   = "#fbfcff"
WARM   = "#fdf3e7"
COOL   = "#eaf0fd"
GREEN  = "#eafaf0"
GREY   = "#f1f2f4"
DANGER = "#fdecea"


# ── 1. Стек скидання кешу та межі досяжності ─────────────────────────────────
def fig_flushing_stack():
    W, H = 1200, 720
    p = []

    p.append(text(W / 2, 44, "Стек зберігання Linux та межі гарантій fsync, fdatasync і sync_file_range",
                  size=16, bold=True, color=INK))

    layers = [
        (90,  "Пам'ять процесу (App RAM)", "буфери прикладної програми", SOFT, INK),
        (170, "Сторінковий кеш ядра (Page Cache)", "брудні сторінки RAM, кеш файлової системи", COOL, NEG),
        (250, "Метадані та журнал файлової системи", "inode table, journal / intent log (ext4/xfs)", WARM, FIELD),
        (330, "Черга блокового рівня (Block Layer / bio)", "I/O scheduler, request queue", GREY, INK),
        (410, "Волатильний кеш накопичувача (Drive DRAM)", "DRAM-буфер контролера SSD / HDD", DANGER, POS),
        (490, "Енергонезалежна пам'ять (Flash / Platter)", "NAND flash, магнітні пластини (durable state)", GREEN, INK),
    ]

    BX, BW, BH = 250, 680, 54
    for y, title_txt, sub_txt, bg, border in layers:
        p.append(rect(BX, y, BW, BH, fill=bg, stroke=border, sw=1.8, rx=6))
        p.append(text(BX + BW / 2, y + 24, title_txt, size=13, bold=True, color=INK))
        p.append(text(BX + BW / 2, y + 43, sub_txt, size=11, color=MUTED))

    # Стрілки гарантій праворуч і ліворуч
    # 1. sync_file_range (ліворуч)
    SX = 220
    p.append(line(SX, 117, SX, 357, color=NEG, sw=2.5))
    p.append(arrow(SX, 350, SX, 357, color=NEG, sw=2.5))
    p.append(fitbox(15, 210, 195, 80,
                    "sync_file_range\nініціює виштовхування,\nАЛЕ НЕ шле FLUSH на диск!\nне захищає при збої",
                    size=10, fill=COOL, stroke=NEG))

    # 2. fdatasync (праворуч)
    FX1 = 960
    p.append(line(FX1, 117, FX1, 517, color=POS, sw=2.5))
    p.append(arrow(FX1, 510, FX1, 517, color=POS, sw=2.5))
    p.append(fitbox(980, 220, 205, 80,
                    "fdatasync\nвиштовхує сторінки даних,\nлише необхідні метадані (i_size)\n+ шле REQ_PREFLUSH/FLUSH",
                    size=10, fill=GREEN, stroke=POS))

    # 3. fsync (праворуч далі)
    FX2 = 1170
    p.append(line(FX2, 117, FX2, 517, color=FIELD, sw=2.5))
    p.append(arrow(FX2, 510, FX2, 517, color=FIELD, sw=2.5))

    p.append(fitbox(BX, 570, BW, 100,
                    "Ключова відмінність:\n"
                    "• sync_file_range зупиняється на блоковому шарі (не гарантує збереження у Flash/Platter при знеструмленні).\n"
                    "• fdatasync та fsync примусово видають команди FLUSH / FUA накопичувачу, очищаючи Drive DRAM.\n"
                    "• fsync додатково скидає неістотні метадані (st_mtime/st_ctime) та робить транзакцію в журналі ФС.",
                    size=11.5, fill=SOFT, stroke=LINE))

    render(os.path.join(OUT, "fig-flushing-stack.svg"), W, H, *p,
           title="Стек зберігання та глибина скидання кешу для fsync, fdatasync і sync_file_range")


# ── 2. Метадані: fsync проти fdatasync ───────────────────────────────────────
def fig_metadata_split():
    W, H = 1200, 640
    p = []

    p.append(text(W / 2, 44, "Порівняння fsync та fdatasync: перезапис блока проти розширення файла",
                  size=16, bold=True, color=INK))

    BW, BH = 480, 210

    # Сценарій 1: Перезапис наявного блока
    X1 = 80
    Y1 = 90
    p.append(rect(X1, Y1, BW, BH, fill=SOFT, stroke=COOL, sw=1.8, rx=8))
    p.append(text(X1 + BW / 2, Y1 + 30, "Сценарій А: Перезапис в межах наявного блока", size=13, bold=True, color=INK))
    p.append(text(X1 + BW / 2, Y1 + 50, "Розмір файла не змінився, нові блоки не виділялися", size=11, color=MUTED))

    p.append(fitbox(X1 + 20, Y1 + 75, 440, 55,
                    "fdatasync(fd)\n• 1 операція В/В: сторінка даних -> диск + FLUSH\n• st_mtime оновлюється лише в ОЗП (dirty inode)",
                    size=11, fill=GREEN, stroke=POS))
    p.append(fitbox(X1 + 20, Y1 + 140, 440, 55,
                    "fsync(fd)\n• 2+ операції В/В: сторінка даних + транзакція журналу ФС\n• запис метаданих inode на диск обов'язковий",
                    size=11, fill=DANGER, stroke=NEG))

    # Сценарій 2: Розширення файла (додавання блоків)
    X2 = 640
    p.append(rect(X2, Y1, BW, BH, fill=SOFT, stroke=COOL, sw=1.8, rx=8))
    p.append(text(X2 + BW / 2, Y1 + 30, "Сценарій Б: Запис із розширенням файла (append)", size=13, bold=True, color=INK))
    p.append(text(X2 + BW / 2, Y1 + 50, "Змінився i_size або виділено нові екстенти", size=11, color=MUTED))

    p.append(fitbox(X2 + 20, Y1 + 75, 440, 55,
                    "fdatasync(fd)\n• 2 операції В/В: сторінка даних + новий i_size / екстент\n• i_size істотний для зчитування нових байтів!",
                    size=11, fill=WARM, stroke=FIELD))
    p.append(fitbox(X2 + 20, Y1 + 140, 440, 55,
                    "fsync(fd)\n• 2+ операції В/В: сторінка даних + повні метадані inode + журнал\n• повністю ідентична поведінка щодо збереження i_size",
                    size=11, fill=DANGER, stroke=NEG))

    # Підсумкове порівняльне роз'яснення
    p.append(fitbox(80, 330, 1040, 260,
                    "Чому fdatasync швидший при перезаписі вільних блоків (In-place Overwrite):\n\n"
                    "1. Журнальні файлові системи (ext4, xfs) при кожній зміні файлу змінюють метку часу st_mtime в inode.\n"
                    "2. Для fsync(fd) зміна st_mtime вважається зміною метаданих, яка ВИМАГАЄ транзакції в журналі (journal commit).\n"
                    "3. Для fdatasync(fd) зміна st_mtime НЕ є істотною для читання даних, тому запис у журнал пропускається.\n"
                    "4. Результат: fdatasync заощаджує цілу дискову транзакцію та затримку позиціонування голівки/блокування транзакції!",
                    size=12, fill=COOL, stroke=LINE))

    render(os.path.join(OUT, "fig-metadata-split.svg"), W, H, *p,
           title="Різниця між fsync та fdatasync при перезаписі та розширенні файла")


# ── 3. Пайплайн sync_file_range ──────────────────────────────────────────────
def fig_sync_file_range_pipeline():
    W, H = 1200, 600
    p = []

    p.append(text(W / 2, 44, "Комбінації прапорців sync_file_range та конвеєризація скидання",
                  size=16, bold=True, color=INK))

    # Прапорці
    BX, BW, BH = 340, 140, 60
    p.append(rect(80, 90, BX, BH, fill=SOFT, stroke=COOL, sw=1.6, rx=6))
    p.append(text(80 + BX / 2, 115, "SYNC_FILE_RANGE_WAIT_BEFORE", size=12, bold=True, color=INK))
    p.append(text(80 + BX / 2, 135, "чекає завершення попереднього В/В", size=10.5, color=MUTED))

    p.append(rect(430, 90, BX, BH, fill=SOFT, stroke=COOL, sw=1.6, rx=6))
    p.append(text(430 + BX / 2, 115, "SYNC_FILE_RANGE_WRITE", size=12, bold=True, color=INK))
    p.append(text(430 + BX / 2, 135, "запускає асинхронний запис брудних сторінок", size=10.5, color=MUTED))

    p.append(rect(780, 90, BX, BH, fill=SOFT, stroke=COOL, sw=1.6, rx=6))
    p.append(text(780 + BX / 2, 115, "SYNC_FILE_RANGE_WAIT_AFTER", size=12, bold=True, color=INK))
    p.append(text(780 + BX / 2, 135, "чекає виштовхування відправлених сторінок", size=10.5, color=MUTED))

    # Типовий патерн фонового запису
    p.append(fitbox(80, 180, 1040, 380,
                    "Практичний патерн конвеєризації в базах даних (Asynchronous Page Flushing Pipeline):\n\n"
                    "Крок 1: Фоновий потік генерує брудні сторінки та викликає sync_file_range(fd, off, len, SYNC_FILE_RANGE_WRITE).\n"
                    "        -> Запит на запис відправляється до блокового шару НЕ БЛОКУЮЧИ потік виконання.\n\n"
                    "Крок 2: Потік продовжує виконувати інші обчислення, поки контролер диска виконує DMA-передачу.\n\n"
                    "Крок 3: Перед фіксацією транзакції потік викликає sync_file_range(fd, off, len, SYNC_FILE_RANGE_WAIT_BEFORE | WRITE | WAIT_AFTER).\n"
                    "        -> Очікування триває мінімальний час, бо сторінки ВЖЕ виштовхувалися під час Кроку 1 та 2!\n\n"
                    "Крок 4 (ОБОВ'ЯЗКОВИЙ): fdatasync(fd) або fsync(fd) для видачі FLUSH на носій.\n"
                    "        -> Скидає волатильний DRAM-кеш накопичувача й гарантує долговічність при аварійному вимкненні!",
                    size=12, fill=WARM, stroke=FIELD))

    render(os.path.join(OUT, "fig-sync-file-range-pipeline.svg"), W, H, *p,
           title="Асинхронний конвеєр sync_file_range та фінальне очищення кешу накопичувача")


fig_flushing_stack()
fig_metadata_split()
fig_sync_file_range_pipeline()
print("фігури згенеровано успішно")
