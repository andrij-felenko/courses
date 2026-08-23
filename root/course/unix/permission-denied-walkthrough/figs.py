# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT   = "#fbfcff"
WARM   = "#fdecea"
COOL   = "#eaf0fd"
GREENF = "#eafaf0"
PALE   = "#f4f6f8"


# ── 1. Повне дерево рішень DAC ядра (generic_permission + capabilities) ────────
def fig_dac_decision_tree():
    W, H = 1000, 680
    p = []

    # Заголовок / Початковий стан
    p.append(fitbox(260, 20, 480, 46, "Запит процесу на доступ до Inode\n(Виклик generic_permission / inode_permission)",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    # Стрілка вниз до першого рішення
    p.append(line(500, 66, 500, 100, color=LINE, sw=1.8))

    # Блок 1: Перевірка fsuid == inode->i_uid
    p.append(fitbox(300, 100, 400, 52, "1. Чи fsuid процесу == inode->i_uid?\n(Перевірка класу власника файлу)",
                    size=12, fill=COOL, stroke=NEG, sw=1.6, color=INK, bold=True))

    # Гілка ТАК (Власник) -> Ліворуч
    p.append(line(300, 126, 170, 126, color=FIELD, sw=1.6))
    p.append(line(170, 126, 170, 180, color=FIELD, sw=1.6))
    p.append(fitbox(50, 180, 240, 60, "Клас ВЛАСНИК (Owner)\n\nАналізуються ТІЛЬКИ біти:\nS_IRUSR, S_IWUSR, S_IXUSR",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.4, color=INK))

    # Гілка НІ -> Вниз до перевірки групи
    p.append(line(500, 152, 500, 190, color=LINE, sw=1.6))
    p.append(fitbox(300, 190, 400, 52, "2. Чи fsgid або supplementary GID == inode->i_gid?\n(Перевірка класу групи файлу)",
                    size=12, fill=COOL, stroke=NEG, sw=1.6, color=INK, bold=True))

    # Гілка ТАК (Група) -> Праворуч
    p.append(line(700, 216, 830, 216, color=FIELD, sw=1.6))
    p.append(line(830, 216, 830, 270, color=FIELD, sw=1.6))
    p.append(fitbox(710, 270, 240, 60, "Клас ГРУПА (Group)\n\nАналізуються ТІЛЬКИ біти:\nS_IRGRP, S_IWGRP, S_IXGRP",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.4, color=INK))

    # Гілка НІ -> Вниз до перевірки Інші
    p.append(line(500, 242, 500, 280, color=LINE, sw=1.6))
    p.append(fitbox(350, 280, 300, 50, "3. Клас РЕШТА (Others)\n\nАналізуються ТІЛЬКИ біти:\nS_IROTH, S_IWOTH, S_IXOTH",
                    size=11, fill=GREENF, stroke=FIELD, sw=1.4, color=INK))

    # Збіг до перевірки бітів
    p.append(line(170, 240, 170, 370, color=LINE, sw=1.4))
    p.append(line(170, 370, 320, 370, color=LINE, sw=1.4))

    p.append(line(830, 330, 830, 370, color=LINE, sw=1.4))
    p.append(line(830, 370, 680, 370, color=LINE, sw=1.4))

    p.append(line(500, 330, 500, 370, color=LINE, sw=1.4))

    # Центральний ромб/блок: Чи дозволяє обрана трійка бітів потрібну дію?
    p.append(fitbox(320, 370, 360, 50, "Чи містить обрана трійка\nвсі запитувані права (r/w/x)?",
                    size=12, fill=PALE, stroke=INK, sw=1.8, color=INK, bold=True))

    # Якщо ТАК -> Доступ надано
    p.append(line(320, 395, 120, 395, color=FIELD, sw=1.8))
    p.append(line(120, 395, 120, 460, color=FIELD, sw=1.8))
    p.append(fitbox(40, 460, 180, 60, "ДОСТУП ДОЗВОЛЕНО\n\n(Успішне повернення 0,\nвиклик VFS триває)",
                    size=12, fill=GREENF, stroke=FIELD, sw=2.0, color=INK, bold=True))

    # Якщо НІ -> Перевірка Capabilities
    p.append(line(500, 420, 500, 460, color=POS, sw=1.8))
    p.append(fitbox(320, 460, 360, 54, "Перевірка Capabilities процесу:\nCAP_DAC_OVERRIDE / CAP_DAC_READ_SEARCH",
                    size=12, fill=WARM, stroke=POS, sw=1.6, color=INK, bold=True))

    # Capabilities: ТАК
    p.append(line(500, 514, 500, 550, color=LINE, sw=1.4))
    p.append(fitbox(240, 550, 520, 56, "Для запиту x: чи є хоч один біт x у будь-якому класі?\nДля читання/запису: CAP_DAC_OVERRIDE дозволяє безумовно",
                    size=11, fill=COOL, stroke=NEG, sw=1.4, color=INK))

    p.append(line(240, 578, 120, 578, color=FIELD, sw=1.6))
    p.append(line(120, 578, 120, 520, color=FIELD, sw=1.6))

    # Capabilities: НІ -> EACCES
    p.append(line(760, 578, 860, 578, color=POS, sw=1.8))
    p.append(line(860, 578, 860, 460, color=POS, sw=1.8))
    p.append(fitbox(770, 460, 180, 60, "ВІДМОВА: EACCES\n\n(Permission denied,\nerrno 13)",
                    size=12, fill=WARM, stroke=POS, sw=2.0, color=INK, bold=True))

    # Підсумкова примітка внизу
    p.append(fitbox(40, 624, 920, 44, "ПРАВИЛО ВЗАЄМНОГО ВИКЛЮЧЕННЯ: класи перевіряються строго по черзі. Якщо процес є власником файлу,\nйого права визначаються ТІЛЬКИ трійкою власника — дозволи групи та others повністю ігноруються.",
                    size=11, fill=PALE, stroke=LINE, sw=1.2, color=INK))

    render(os.path.join(OUT, "dac-decision-tree.svg"), W, H, *p,
           title="Алгоритм перевірки прав доступу ядра (DAC)")


# ── 2. Покомпонентний розбір шляху (Path Resolution Walk) ──────────────────────
def fig_path_traversal_resolution():
    W, H = 1000, 520
    p = []

    # Заголовок
    p.append(fitbox(250, 20, 500, 44, "Шлях запиту: /var/log/app/service.log\n(Покомпонентний обхід VFS link_path_walk)",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    # Компоненти шляху зліва направо
    # Компонент 1: /
    p.append(fitbox(40, 90, 160, 120, "1. Каталог '/'\n(root inode)\n\nВласник: root:root\nПрава: drwxr-xr-x (0755)\n\nПотрібно: +x (пошук)\nРезультат: OK",
                    size=10, fill=GREENF, stroke=FIELD, sw=1.4, color=INK))

    p.append(line(200, 150, 240, 150, color=FIELD, sw=2.0))

    # Компонент 2: var
    p.append(fitbox(240, 90, 160, 120, "2. Каталог 'var'\n(inode /var)\n\nВласник: root:root\nПрава: drwxr-xr-x (0755)\n\nПотрібно: +x (пошук)\nРезультат: OK",
                    size=10, fill=GREENF, stroke=FIELD, sw=1.4, color=INK))

    p.append(line(400, 150, 440, 150, color=FIELD, sw=2.0))

    # Компонент 3: log (Пастка: бракує +x для не-власника!)
    p.append(fitbox(440, 90, 220, 140, "3. Каталог 'log'\n(inode /var/log/app)\n\nВласник: app-admin:adm\nПрава: drwxr-x--- (0750)\n\nПроцес: uid=1001 (www-data)\nПотрібно: +x (пошук)\nРезультат: ВІДМОВА!",
                    size=10, fill=WARM, stroke=POS, sw=2.0, color=INK, bold=True))

    # Червона стрілка відмови вниз
    p.append(line(550, 230, 550, 280, color=POS, sw=2.0))
    p.append(fitbox(410, 280, 280, 64, "ЯДРО ПЕРЕРИВАЄ ОБХІД: EACCES\n\nБрак біта виконання (+x) на проміжному\nкаталозі блокує будь-який вхід у піддерево",
                    size=11, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    # Компонент 4: цільовий файл (до якого ядро навіть не дійшло)
    p.append(line(660, 150, 740, 150, color=MUTED, sw=1.4))
    p.append(fitbox(740, 90, 220, 120, "4. Файл 'service.log'\n(inode service.log)\n\nВласник: www-data:www-data\nПрава: -rwxrwxrwx (0777)\n\nСТАН: НЕ ДОСЯГНУТО!\n(0777 не рятує від збою вище)",
                    size=10, fill=PALE, stroke=MUTED, sw=1.4, color=MUTED))

    # Пояснення внизу
    p.append(fitbox(40, 370, 920, 130, "ПРИНЦИП ПРОХОДЖЕННЯ ШЛЯХУ В КАТАЛОГАХ:\n\n"
                                      "• Біт читання (+r) на каталозі дозволяє лише читати список імен (getdents64, вивід ls без атрибутів).\n"
                                      "• Біт виконання (+x) на каталозі дозволяє пошук (lookup), перетин каталогу та доступ до inode об'єктів усередині.\n"
                                      "• Якщо на будь-якому каталозі шляху бракує +x, ядро повертає EACCES незалежно від прав на сам цільовий файл.\n"
                                      "• Для читання чи відкриття файлу за точним шляхом біт +r на каталогах НЕ потрібен — достатньо лише +x.",
                    size=11, fill=COOL, stroke=NEG, sw=1.4, color=INK))

    render(os.path.join(OUT, "path-traversal-resolution.svg"), W, H, *p,
           title="Покомпонентний розбір шляху та перевірка біта x на каталогах")


# ── 3. EACCES проти EPERM ──────────────────────────────────────────────────────
def fig_eacces_vs_eperm():
    W, H = 1000, 560
    p = []

    # Заголовок
    p.append(fitbox(280, 20, 440, 44, "Анатомія відмов: EACCES проти EPERM\n(Два принципово різні рівні безпеки ядра)",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    # Ліва колонка: EACCES
    p.append(fitbox(40, 80, 430, 46, "EACCES (errno 13, Permission denied)\nПорушення дискреційних прав доступу (DAC)",
                    size=12, fill=COOL, stroke=NEG, sw=1.8, color=INK, bold=True))

    p.append(fitbox(40, 136, 430, 250,
                    "КОЛИ ВИНИКАЄ EACCES:\n\n"
                    "• Брак бітів r/w/x на цільовому файлі за класом fsuid/fsgid.\n"
                    "• Брак біта +x (пошук) на будь-якому каталозі шляху.\n"
                    "• Брак біта +w на батьківському каталозі при створенні/видаленні.\n"
                    "• Порушення Sticky Bit (+t) при спробі видалити чужий файл у /tmp.\n"
                    "• Спроба запису на файлову систему, змонтовану в режимі ro.\n"
                    "• Запуск бінарника без біта +x або з ФС, змонтованої з noexec.\n"
                    "• Блокування модулем безпеки LSM (AppArmor, SELinux DAC hook).",
                    size=11, fill="#fff", stroke=NEG, sw=1.4, color=INK))

    # Права колонка: EPERM
    p.append(fitbox(530, 80, 430, 46, "EPERM (errno 1, Operation not permitted)\nБрак привілеїв суб'єкта або порушення системного інваріанта",
                    size=12, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    p.append(fitbox(530, 136, 430, 250,
                    "КОЛИ ВИНИКАЄ EPERM:\n\n"
                    "• Спроба chown() файлу звичайним користувачем (потрібен CAP_CHOWN).\n"
                    "• Спроба chmod() не-власником файлу (потрібен fsuid==owner чи CAP_FOWNER).\n"
                    "• Спроба змінити файл з атрибутом 'immutable' (chattr +i, FS_IMMUTABLE_FL).\n"
                    "• Відправка сигналу kill() процесу іншого користувача (без CAP_KILL).\n"
                    "• Спроба встановити системний час, мережеві маршрути або завантажити модуль ядра.\n"
                    "• Порушення обмежень безпеки Seccomp або Landlock sandbox.",
                    size=11, fill="#fff", stroke=POS, sw=1.4, color=INK))

    # Нижній синтез: критерій розрізнення
    p.append(fitbox(40, 404, 920, 136,
                    "ГОЛОВНЕ ПРАВИЛО РОЗРІЗНЕННЯ EACCES ТА EPERM:\n\n"
                    "1. EACCES стосується прав доступу до ДАНИХ (читання, запис, пошук, виконання вмісту) за матрицею rwx.\n"
                    "2. EPERM стосується ПРИВІЛЕЇВ ВЛАСНОСТІ ТА АДМІНІСТРУВАННЯ (зміна метаданих, власника, системних ресурсів, сигналів).\n"
                    "3. Якщо вам бракує rwx на об'єкті — це EACCES. Якщо ви намагаєтеся адмініструвати чужий об'єкт чи змінити ядровий стан — це EPERM.",
                    size=11, fill=PALE, stroke=LINE, sw=1.4, color=INK))

    render(os.path.join(OUT, "eacces-vs-eperm.svg"), W, H, *p,
           title="Розмежування помилок EACCES та EPERM")


# ── 4. Операції над файлом проти операцій над каталогом (Sticky bit) ───────────
def fig_directory_vs_file_ops():
    W, H = 1000, 560
    p = []

    # Заголовок
    p.append(fitbox(250, 20, 500, 44, "Операції над файлом проти операцій над каталогом\n(Парадокс видалення та Sticky Bit)",
                    size=13, fill=PALE, stroke=INK, sw=2.0, color=INK, bold=True))

    # Лівий блок: Модифікація вмісту файлу
    p.append(fitbox(40, 80, 430, 46, "Зміна ВМІСТУ файлу (write, truncate)\nОб'єкт дії — Inode файлу",
                    size=12, fill=COOL, stroke=NEG, sw=1.8, color=INK, bold=True))

    p.append(fitbox(40, 136, 430, 200,
                    "ЩО ПЕРЕВІРЯЄ ЯДРО:\n\n"
                    "1. +x на всіх проміжних каталогах шляху.\n"
                    "2. +w на самому цільовому файлі (за fsuid/fsgid/other).\n"
                    "3. Відсутність прапорця read-only на змонтованій ФС.\n"
                    "4. Відсутність атрибутів append-only (+a) або immutable (+i).\n\n"
                    "Права батьківського каталогу на зміну вмісту НЕ впливають!",
                    size=11, fill="#fff", stroke=NEG, sw=1.4, color=INK))

    # Правий блок: Створення / Видалення / Перейменування
    p.append(fitbox(530, 80, 430, 46, "Створення / Видалення / Перейменування\n(unlink, rmdir, rename, creat) — дія над КАТАЛОГОМ",
                    size=12, fill=WARM, stroke=POS, sw=1.8, color=INK, bold=True))

    p.append(fitbox(530, 136, 430, 200,
                    "ЩО ПЕРЕВІРЯЄ ЯДРО:\n\n"
                    "1. +x та +w на БАТЬКІВСЬКОМУ каталозі (запис нового запису в каталог).\n"
                    "2. Права на сам видалюваний файл взагалі НЕ перевіряються!\n"
                    "   (Можна видалити файл 0000, якщо є +w на каталозі).\n"
                    "3. Якщо на каталозі стоїть Sticky Bit (S_ISVTX, +t, 01000):\n"
                    "   Видалення дозволено ТІЛЬКИ якщо fsuid == власник файлу,\n"
                    "   АБО fsuid == власник каталогу, АБО є CAP_FOWNER.",
                    size=11, fill="#fff", stroke=POS, sw=1.4, color=INK))

    # Нижній синтез
    p.append(fitbox(40, 356, 920, 180,
                    "ПРАКТИЧНІ НАСЛІДКИ ДЛЯ БЕЗПЕКИ:\n\n"
                    "• Каталог /tmp має права drwxrwxrwt (1777): кожен користувач може створювати свої файли (+w для всіх),\n"
                    "  але завдяки Sticky Bit (+t) ніхто не може видалити або перейменувати чужий файл у /tmp.\n"
                    "• Команда rm -f file спочатку перевіряє права на запис у файл лише для того, щоб спитати підтвердження в інтерактивному режимі,\n"
                    "  але системний виклик unlink() звертається виключно до inode батьківського каталогу.\n"
                    "• Безпечне створення тимчасових файлів вимагає або використання mkstemp() у /tmp, або створення приватного каталогу з правами 0700.",
                    size=11, fill=PALE, stroke=LINE, sw=1.4, color=INK))

    render(os.path.join(OUT, "directory-vs-file-ops.svg"), W, H, *p,
           title="Різниця між операціями над файлом і операціями над каталогом")


if __name__ == "__main__":
    fig_dac_decision_tree()
    fig_path_traversal_resolution()
    fig_eacces_vs_eperm()
    fig_directory_vs_file_ops()
    print("Всі фігури успішно скомпільовано.")
