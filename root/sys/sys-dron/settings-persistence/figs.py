# -*- coding: utf-8 -*-
"""Фігури до теми «Налаштування й що переживає перезапуск»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


# ── 1. Три роди стану за власником ──────────────────────────────────────────
def state_owners():
    W, H = 1180, 690
    f = []
    cols = [
        (40, "СТАН СТАНЦІЇ", "власник — сама станція", FIELD,
         ["одиниці й мова", "тека збереження", "ключі до карт",
          "перелік каналів", "гучність попереджень"],
         "ФАЙЛ НАЛАШТУВАНЬ",
         ["читається як істина", "іншого джерела немає",
          "втрата = кілька хвилин", "перенастроювання"]),
        (415, "КОПІЯ СТАНУ АПАРАТА", "власник — апарат", NEG,
         ["параметри автопілота", "місія на борту", "геозона",
          "опис компонентів", "набір режимів"],
         "КЕШ ІЗ ПЕРЕВІРКОЮ",
         ["перед ужитком звіряємо", "контрольну суму з апаратом",
          "не збіглося — тягнемо заново", "втрата = зайвий час"]),
        (790, "СТАН СЕАНСУ", "власника після вимкнення немає", POS,
         ["координати й висота", "режим польоту", "заряд батареї",
          "факт під'єднаності", "швидкість каналу"],
         "НЕ ЗБЕРІГАЄТЬСЯ НІДЕ",
         ["описує подію, якої вже немає", "збережене було б хибним",
          "із першої ж секунди", "будується з нуля щоразу"]),
    ]
    CW = 350
    for x, title, who, color, items, verdict, notes in cols:
        f.append(rect(x, 60, CW, 560, fill="#ffffff", stroke=color, sw=2.2))
        f.append(fitbox(x + 16, 76, CW - 32, 44, title, size=16, bold=True,
                        fill="#ffffff", stroke="none", color=color))
        f.append(fitbox(x + 16, 122, CW - 32, 30, who, size=13,
                        fill="#ffffff", stroke="none", color=MUTED))
        f.append(line(x + 20, 162, x + CW - 20, 162, color=color, sw=1.2))
        y = 186
        for it in items:
            f.append(fitbox(x + 26, y, CW - 52, 36, it, size=13))
            y += 44
        f.append(line(x + 20, y + 6, x + CW - 20, y + 6, color=color, sw=1.2, dash="5 4"))
        f.append(fitbox(x + 26, y + 22, CW - 52, 40, verdict, size=14, bold=True,
                        fill="#f4f6f8", stroke=color, color=color))
        yy = y + 76
        for n in notes:
            f.append(text(x + 26, yy, n, size=12, color=MUTED, anchor="start"))
            yy += 22

    f.append(text(W / 2, 660,
                  "критерій поділу: чия копія вважається правдою, коли дві копії розійшлися",
                  size=14, color=INK, bold=True))
    render(os.path.join(OUT, 'state-owners.svg'), W, H, *f,
           title="Три роди стану застосунку — і три способи (не) зберігати")


# ── 2. Шлях одного налаштування ─────────────────────────────────────────────
def setting_path():
    W, H = 1180, 620
    f = []

    # джерела
    b, w1, h1 = textbox(210, 130,
                        ["JSON-МЕТАДАНІ (ресурс у застосунку)",
                         "тип · межі · одиниці · підпис · опис",
                         "ТИПОВЕ ЗНАЧЕННЯ"],
                        size=14, pad=16, stroke=FIELD, sw=2)
    f.append(b)
    f.append(text(210, 78, "незмінне, однакове в усіх копіях застосунку",
                 size=12, color=MUTED))

    b2, w2, h2 = textbox(210, 400,
                         ["ФАЙЛ НАЛАШТУВАНЬ НА ДИСКУ",
                          "лише ключі, яких хтось торкався",
                          "ПЕРЕКРИТТЯ ЗНАЧЕННЯ"],
                         size=14, pad=16, stroke=NEG, sw=2)
    f.append(b2)
    f.append(text(210, 470, "немає ключа — діє типове значення",
                 size=12, color=MUTED))

    # ядрове розширення
    b3, w3, h3 = textbox(600, 130,
                         ["ЯДРОВЕ РОЗШИРЕННЯ",
                          "править метадані до народження факту:",
                          "інше типове · сховати налаштування"],
                         size=13, pad=14, stroke=POS, sw=2, fill="#fdecea")
    f.append(b3)

    # факт
    b4, w4, h4 = textbox(600, 400,
                         ["SettingsFact",
                          "значення + метадані",
                          "читає при народженні",
                          "пише при кожній зміні"],
                         size=14, pad=16, stroke=INK, sw=2.4)
    f.append(b4)

    # споживачі
    b5, w5, h5 = textbox(985, 340, ["ІНТЕРФЕЙС", "редактор із підписом,", "межами й одиницями"],
                         size=13, pad=14)
    f.append(b5)
    b6, w6, h6 = textbox(985, 470, ["КОД ПІДСИСТЕМ", "читає значення", "як звичайний факт"],
                         size=13, pad=14)
    f.append(b6)

    # стрілки
    f.append(arrow(210, 130 + h1 / 2, 210, 400 - h2 / 2 - 4, color=MUTED))
    f.append(arrow(210 + w1 / 2, 130, 600 - w3 / 2 - 4, 130, color=FIELD))
    f.append(arrow(600, 130 + h3 / 2, 600, 400 - h4 / 2 - 4, color=POS))
    f.append(arrow(210 + w2 / 2, 400, 600 - w4 / 2 - 4, 400, color=NEG))
    f.append(arrow(600 + w4 / 2, 385, 985 - w5 / 2 - 4, 350, color=INK))
    f.append(arrow(600 + w4 / 2, 415, 985 - w6 / 2 - 4, 460, color=INK))

    f.append(text(310, 265, "тільки для ключів,", size=12, color=MUTED, anchor="start"))
    f.append(text(310, 285, "що є у файлі", size=12, color=MUTED, anchor="start"))
    f.append(text(405, 118, "метадані", size=12, color=FIELD))
    f.append(text(405, 388, "значення", size=12, color=NEG))
    f.append(text(628, 265, "сховане налаштування", size=12, color=POS, anchor="start"))
    f.append(text(628, 285, "бере типове, диск не читає", size=12, color=POS, anchor="start"))

    # зворотний запис
    f.append(arrow(600 - w4 / 2 - 4, 435, 210 + w2 / 2, 435, color=NEG))
    f.append(text(405, 458, "запис на кожну зміну", size=12, color=NEG))

    f.append(text(W / 2, 575,
                  "окремої дії «зберегти» немає: зміна значення одразу лягає на диск",
                  size=14, bold=True))
    render(os.path.join(OUT, 'setting-path.svg'), W, H, *f,
           title="Звідки факт налаштування бере значення і куди його віддає")


# ── 3. Карта диска ──────────────────────────────────────────────────────────
def disk_map():
    W, H = 1180, 640
    f = []
    areas = [
        (40, "ФАЙЛ НАЛАШТУВАНЬ", FIELD,
         ["QGroundControl.ini", "текстовий, кілька кілобайтів"],
         ["версія формату", "одиниці, мова, ключі карт", "конфігурації каналів",
          "шлях до теки збереження", "прапорці одноразових вікон"],
         ["видаляє: користувач або сам", "застосунок при зміні формату",
          "наслідок: типові значення,", "перенастроювання на кілька хвилин"]),
        (415, "ТЕКИ КЕША", NEG,
         ["ParamCache/<sysid>_<compid>.v2", "qgcMapCache.db"],
         ["копії параметрів апаратів", "тайли карт", "завантажені описи метаданих",
          "усе — з перевіркою свіжості", "або з можливістю добути знову"],
         ["видаляє: застосунок, користувач", "і сама операційна система",
          "наслідок: довше під'єднання,", "повторне завантаження тайлів"]),
        (790, "ТЕКА ДОКУМЕНТІВ", POS,
         ["Documents/QGroundControl/…", "звичайні файли з розширеннями"],
         ["місії та плани (.plan)", "телеметрія (.tlog)", "журнали польоту (.ulg)",
          "набори параметрів (.params)", "знімки й відео"],
         ["видаляє: тільки користувач", "застосунок сюди лише пише",
          "наслідок: незворотна втрата", "результатів роботи"]),
    ]
    CW = 350
    for x, title, color, head, items, who in areas:
        f.append(rect(x, 60, CW, 520, fill="#ffffff", stroke=color, sw=2.2))
        f.append(fitbox(x + 16, 76, CW - 32, 40, title, size=16, bold=True,
                        fill="#ffffff", stroke="none", color=color))
        yy = 138
        for hline in head:
            f.append(text(x + CW / 2, yy, hline, size=12, color=MUTED))
            yy += 20
        f.append(line(x + 20, yy + 4, x + CW - 20, yy + 4, color=color, sw=1.2))
        y = yy + 26
        for it in items:
            f.append(fitbox(x + 26, y, CW - 52, 34, it, size=13))
            y += 40
        f.append(line(x + 20, y + 8, x + CW - 20, y + 8, color=color, sw=1.2, dash="5 4"))
        yy = y + 32
        for n in who:
            f.append(text(x + 26, yy, n, size=12, color=MUTED, anchor="start"))
            yy += 21

    f.append(text(W / 2, 614,
                  "право на видалення росте зліва направо разом із ціною втрати",
                  size=14, bold=True))
    render(os.path.join(OUT, 'disk-map.svg'), W, H, *f,
           title="Що станція лишає на диску — і хто має право це прибрати")


# ── 4. Анатомія власної групи налаштувань (вставка proj) ────────────────────
def settings_group_anatomy():
    W, H = 1240, 720
    f = []

    # два джерела двох імен
    bj, wj, hj = textbox(300, 130,
                         ["РЕСУРС ІЗ МЕТАДАНИМИ",
                          ":/json/Payload.SettingsGroup.json",
                          "тип · межі · одиниці · підпис · типове"],
                         size=13, pad=16, stroke=FIELD, sw=2)
    bi, wi, hi = textbox(940, 130,
                         ["СХОВИЩЕ НА ДИСКУ",
                          "QGroundControl.ini → [PayloadPlanner]",
                          "лише ключі, яких хтось торкався"],
                         size=13, pad=16, stroke=NEG, sw=2)
    f += [bj, bi]

    # клас групи
    bc, wc, hc = textbox(620, 360,
                         ["class PayloadSettings : public SettingsGroup",
                          'DECLARE_SETTINGGROUP(Payload, "PayloadPlanner")',
                          "DEFINE_SETTINGFACT(triggerInterval)",
                          "у SettingsManager::init(): new PayloadSettings(this)"],
                         size=13, pad=18, stroke=INK, sw=2.4)
    f.append(bc)

    # споживачі
    bp, wp, hp = textbox(300, 600,
                         ["З КОДУ C++",
                          "SettingsManager::instance()",
                          "->payloadSettings()->triggerInterval()"],
                         size=13, pad=14)
    bq, wq, hq = textbox(940, 600,
                         ["З QML",
                          "QGroundControl.settingsManager",
                          ".payloadSettings.triggerInterval"],
                         size=13, pad=14)
    f += [bp, bq]

    # зв'язки
    f.append(arrow(420, 169, 540, 300, color=FIELD))
    f.append(arrow(700, 310, 930, 178, color=NEG))
    f.append(arrow(520, 414, 320, 559, color=INK))
    f.append(arrow(720, 414, 920, 559, color=INK))

    f.append(text(430, 200, "немає ключа → exit(-1) при першому доступі",
                  size=12, color=POS, anchor="end"))
    f.append(text(468, 245, "ім'я «Payload» → який JSON", size=12, color=FIELD, anchor="end"))
    f.append(text(468, 263, "читати при створенні групи", size=12, color=FIELD, anchor="end"))
    f.append(text(838, 245, "значення: читає при народженні,", size=12, color=NEG, anchor="start"))
    f.append(text(838, 263, "пише при кожній зміні", size=12, color=NEG, anchor="start"))

    f.append(text(620, 470, "факт народжується при першому доступі —", size=12, color=MUTED))
    f.append(text(620, 490, "і тут-таки читає своє значення з диска", size=12, color=MUTED))

    f.append(text(W / 2, 690,
                  "два імені в одному рядку оголошення ведуть у два різні світи: "
                  "ліве — у ресурс збірки, праве — у файл на диску",
                  size=14, bold=True))
    render(os.path.join(OUT, 'settings-group-anatomy.svg'), W, H, *f,
           title="Що з чим пов'язують два імені власної групи налаштувань")


state_owners()
setting_path()
disk_map()
settings_group_anatomy()
print("ok")
