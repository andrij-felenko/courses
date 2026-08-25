# -*- coding: utf-8 -*-
"""Фігури теми «Годинник машини: RTC, часові пояси, tzdata, timedatectl»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Апаратний RTC проти програмних годинників ядра ────────────────────────
def fig_rtc_vs_system_clocks():
    W, H = 1000, 560
    f = []

    # Верхній заголовок діаграми
    f.append(fitbox(40, 20, 920, 44,
                    "Апаратний годинник реального часу (RTC) та програмні шкали ядра Linux",
                    size=16, bold=True, fill="#eaf0fd", stroke="#2457d6"))

    # Ліва колонка: Апаратний рівень (RTC)
    f.append(fitbox(40, 80, 260, 440,
                    "Апаратний рівень (RTC / CMOS)\n\n"
                    "• Кварцовий резонатор 32.768 кГц\n"
                    "• Живлення від батарейки CR2032\n"
                    "• Рахує секунди, хвилини, години\n"
                    "• Роздільність 1 Гц (цілі секунди)\n"
                    "• Температурний дрейф ~20 ppm\n"
                    "  (±1.7 с на добу без корекції)\n\n"
                    "Драйвер ядра: /dev/rtc0\n"
                    "Інтерфейс ioctl(RTC_RD_TIME)",
                    size=13, fill="#fdf6e3", stroke="#b58900"))

    # Центральна колонка: Ініціалізація та синхронізація
    f.append(fitbox(340, 80, 280, 440,
                    "Міст синхронізації та лічильники\n\n"
                    "[Старт системи: hctosys]\n"
                    "Ядро одноразово зчитує RTC\n"
                    "та ініціалізує час xtime\n\n"
                    "[Швидкі лічильники (clocksource)]\n"
                    "• TSC (CPU Time Stamp Counter)\n"
                    "• HPET / ARM Generic Timer\n"
                    "Мільярди тактів на секунду\n\n"
                    "[Зворотний запис утилітою або ядром]\n"
                    "• hwclock --systohc\n"
                    "• Режим 11-хвилинного оновлення\n"
                    "  ядра при активному NTP (RTC_SYNC)",
                    size=13, fill="#f4f6f8", stroke="#4b5563"))

    # Права колонка: Програмні годинники ядра
    f.append(fitbox(660, 80, 300, 440,
                    "Шкали часу ядра Linux (POSIX Clocks)\n\n"
                    "CLOCK_REALTIME\n"
                    "Настінний час від 1970-01-01 UTC.\n"
                    "Може стрибати (NTP step, clock_settime).\n\n"
                    "CLOCK_MONOTONIC\n"
                    "Суворо неперервний від старту машини.\n"
                    "Не йде назад; зупиняється в сні (suspend).\n\n"
                    "CLOCK_BOOTTIME\n"
                    "Монотонний + час сну машини.\n\n"
                    "CLOCK_TAI\n"
                    "Атомний час без високосних стрибків.",
                    size=13, fill="#eef7ee", stroke="#27ae60"))

    # Стрілки між колонками
    f.append(arrow(300, 160, 340, 160, color="#2457d6", sw=2))
    f.append(arrow(340, 420, 300, 420, color="#c0392b", sw=2))
    f.append(arrow(620, 200, 660, 200, color="#27ae60", sw=2))

    render(os.path.join(OUT, 'rtc-vs-system-clocks.svg'), W, H, *f)


# ── 2. UTC проти Local Time в RTC під час переходу DST ───────────────────────
def fig_utc_vs_local_rtc_dst():
    W, H = 1000, 520
    f = []

    f.append(fitbox(40, 20, 920, 44,
                    "Поведінка RTC під час осіннього переведення годинника (03:00 -> 02:00)",
                    size=16, bold=True, fill="#eaf0fd", stroke="#2457d6"))

    # Верхня смуга: RTC у форматі UTC
    f.append(fitbox(40, 80, 920, 180,
                    "Золотий стандарт Unix: RTC зберігає UTC (безперервна лінійна вісь)\n\n"
                    "00:00 UTC ───────────> 00:30 UTC ───────────> 01:00 UTC ───────────> 01:30 UTC ───────────> 02:00 UTC\n"
                    "(03:00 EEST)          (03:30 EEST)          (03:00 EET)           (03:30 EET)           (04:00 EET)\n\n"
                    "✓ Час на апаратному лічильнику зростає суворо монотонно, без стрибків і петель.\n"
                    "✓ Зміна зміщення поясу обчислюється в просторі користувача бібліотекою за базою tzdata.",
                    size=13, fill="#eef7ee", stroke="#27ae60"))

    # Нижня смуга: RTC у форматі Local Time
    f.append(fitbox(40, 280, 920, 210,
                    "Спадщина Windows: RTC зберігає місцевий час (Local Time)\n\n"
                    "02:00 (літо) ───> 02:59 (літо) ───[СТРИБОК НАЗАД]───> 02:00 (зима) ───> 03:00 (зима)\n\n"
                    "✗ Петля часу: інтервал [02:00 .. 03:00] повторюється двічі з тими самими апаратними показниками.\n"
                    "✗ Пастка подвійного завантаження (Dual-boot): Linux і Windows можуть перевести RTC двічі (-2 год).\n"
                    "✗ fsck та раннє монтування: якщо пояс ще невідомий, ядро вважає час у RTC за UTC і ламає позначки.",
                    size=13, fill="#fdecea", stroke="#c0392b"))

    render(os.path.join(OUT, 'utc-vs-local-rtc-dst.svg'), W, H, *f)


# ── 3. Структура бінарного файлу часового поясу tzfile(5) ─────────────────────
def fig_tzfile_structure():
    W, H = 1000, 540
    f = []

    f.append(fitbox(40, 20, 920, 44,
                    "Внутрішня структура бінарного файлу часового поясу /usr/share/zoneinfo/ (tzfile)",
                    size=16, bold=True, fill="#eaf0fd", stroke="#2457d6"))

    # Блок 1: Заголовок
    f.append(fitbox(40, 80, 210, 420,
                    "1. Заголовок (44 байти)\n\n"
                    "Магічні байти: \"TZif2\"\n"
                    "Версія формату (1, 2 або 3)\n\n"
                    "Лічильники структури:\n"
                    "• tzh_timecnt (кількість переходів)\n"
                    "• tzh_typecnt (кількість типів ttinfo)\n"
                    "• tzh_charcnt (байти назв зон)\n"
                    "• tzh_leapcnt (високосні секунди)\n"
                    "• tzh_ttisstdcnt\n"
                    "• tzh_ttisgmtcnt",
                    size=12, fill="#fdf6e3", stroke="#b58900"))

    # Блок 2: Таблиці переходів
    f.append(fitbox(270, 80, 210, 420,
                    "2. Таблиці переходів\n\n"
                    "[Масив transition times]\n"
                    "timecnt значень 64-бітних цілих\n"
                    "(миті time_t за UTC, коли\n"
                    "змінювалося правило чи зміщення)\n\n"
                    "[Масив transition types]\n"
                    "timecnt байтів-індексів:\n"
                    "кожен перехід вказує на\n"
                    "відповідний запис ttinfo",
                    size=12, fill="#eaf0fd", stroke="#2457d6"))

    # Блок 3: Описи типів локального часу
    f.append(fitbox(500, 80, 220, 420,
                    "3. Записи типів (ttinfo)\n\n"
                    "typecnt структур ttinfo:\n"
                    "• tt_utoff (зміщення від UTC у с,\n"
                    "  наприклад, +7200 або +10800)\n"
                    "• tt_isdst (0 — зимовий час,\n"
                    "  1 — літній час DST)\n"
                    "• tt_desigidx (індекс абревіатури\n"
                    "  в таблиці символів)\n\n"
                    "Таблиця назв: \"EET\\0EEST\\0\"",
                    size=12, fill="#eef7ee", stroke="#27ae60"))

    # Блок 4: POSIX TZ правило наприкінці
    f.append(fitbox(740, 80, 220, 420,
                    "4. Хвіст: POSIX TZ рядок\n\n"
                    "Текстове правило між '\\n':\n\n"
                    "\"EET-2EEST,M3.5.0/3,\n"
                    "M10.5.0/4\"\n\n"
                    "Дозволяє бібліотеці\n"
                    "обчислювати всі майбутні\n"
                    "переходи без нескінченного\n"
                    "розширення масиву\n"
                    "історичних переходів.",
                    size=12, fill="#f4f6f8", stroke="#4b5563"))

    # Стрілки між блоками
    f.append(arrow(250, 240, 270, 240, color="#4b5563", sw=1.8))
    f.append(arrow(480, 240, 500, 240, color="#4b5563", sw=1.8))
    f.append(arrow(720, 240, 740, 240, color="#4b5563", sw=1.8))

    render(os.path.join(OUT, 'tzfile-structure.svg'), W, H, *f)


# ── 4. Архітектура керування часом у systemd ─────────────────────────────────
def fig_systemd_time_architecture():
    W, H = 1000, 540
    f = []

    f.append(fitbox(40, 20, 920, 44,
                    "Архітектура керування часом, часовими поясами та синхронізацією в systemd",
                    size=16, bold=True, fill="#eaf0fd", stroke="#2457d6"))

    # Верхній шар: Користувацький простір
    f.append(fitbox(40, 80, 440, 110,
                    "Утиліта timedatectl (CLI)\n"
                    "Запити стану, зміна часового поясу, налаштування NTP та RTC.\n"
                    "Спілкується через системну шину D-Bus.",
                    size=13, fill="#eaf0fd", stroke="#2457d6"))

    f.append(fitbox(520, 80, 440, 110,
                    "Програми користувача (Applications)\n"
                    "Читають змінну $TZ або /etc/localtime через libc (localtime_r).\n"
                    "Викликають clock_gettime() для отримання шкал часу.",
                    size=13, fill="#eef7ee", stroke="#27ae60"))

    # Середній шар: Демони та файли конфігурації
    f.append(fitbox(40, 230, 440, 140,
                    "systemd-timedated.service (D-Bus демон)\n"
                    "• Обслуговує інтерфейс org.freedesktop.timedate1\n"
                    "• Атомарно перезаписує лінк /etc/localtime -> /usr/share/zoneinfo/...\n"
                    "• Керує режимом RTC (UTC проти Local) та вмикає службу NTP",
                    size=12, fill="#fdf6e3", stroke="#b58900"))

    f.append(fitbox(520, 230, 440, 140,
                    "systemd-timesyncd.service (SNTP клієнт)\n"
                    "• Конфігурація: /etc/systemd/timesyncd.conf\n"
                    "• Синхронізує системний годинник з мережевими серверами NTP\n"
                    "• Стан: /var/lib/systemd/timesync/clock (фіксація монотонного часу\n"
                    "  для плат без RTC, захист від стрибка в 1970 рік)",
                    size=12, fill="#f4f6f8", stroke="#4b5563"))

    # Нижній шар: Ядро та Залізо
    f.append(fitbox(40, 410, 920, 100,
                    "Ядро Linux та Апаратний рівень\n"
                    "Системний час (CLOCK_REALTIME, CLOCK_MONOTONIC) ⇄ Системні виклики adjtimex / clock_settime\n"
                    "Апаратний годинник /dev/rtc0 ⇄ 11-хвилинний автозапис ядра (RTC_SYNC) та hwclock",
                    size=13, fill="#f9fafb", stroke="#333333"))

    # Стрілки
    f.append(arrow(260, 190, 260, 230, color="#2457d6", sw=1.8))
    f.append(arrow(740, 190, 740, 230, color="#27ae60", sw=1.8))
    f.append(arrow(260, 370, 260, 410, color="#b58900", sw=1.8))
    f.append(arrow(740, 370, 740, 410, color="#4b5563", sw=1.8))

    render(os.path.join(OUT, 'systemd-time-architecture.svg'), W, H, *f)


if __name__ == '__main__':
    fig_rtc_vs_system_clocks()
    fig_utc_vs_local_rtc_dst()
    fig_tzfile_structure()
    fig_systemd_time_architecture()
    print("Всі фігури згенеровано успішно.")
