# -*- coding: utf-8 -*-
"""Фігури до теми «Модель плагінів і реєстр елементів»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'img')
os.makedirs(OUT, exist_ok=True)


# ── 1. Будова плагіна: файл → дескриптор → фічі ────────────────────────────
def fig_anatomy():
    W, H = 960, 580
    f = []

    # лівий блок — файл на диску
    f.append(rect(40, 62, 350, 300, fill="#ffffff"))
    f.append(text(215, 88, "libgstexample.so — файл на диску", size=14, bold=True))
    f.append(fitbox(62, 104, 306, 56,
                    "gst_plugin_desc\n(єдиний обов'язковий символ)", size=14))
    f.append(fitbox(62, 174, 306, 56,
                    "plugin_init() — код реєстрації", size=14))
    f.append(fitbox(62, 244, 306, 96,
                    "класи елементів:\nGType, метадані, шаблони падів", size=14))

    # перехід
    f.append(text(475, 178, "core завантажує файл", size=12, color=MUTED))
    f.append(text(475, 196, "і кличе plugin_init", size=12, color=MUTED))
    f.append(arrow(396, 216, 554, 216))

    # правий блок — записи в реєстрі
    f.append(rect(560, 62, 360, 300, fill="#ffffff"))
    f.append(text(740, 88, "записи в реєстрі (features)", size=14, bold=True))
    f.append(fitbox(582, 104, 316, 68,
                    "GstElementFactory\n«videoconvert»", size=14, fill="#eef6ee"))
    f.append(fitbox(582, 184, 316, 68,
                    "GstTypeFindFactory\n«video/quicktime»", size=14, fill="#eef6ee"))
    f.append(fitbox(582, 264, 316, 76,
                    "GstDeviceProviderFactory\n«v4l2deviceprovider»", size=14, fill="#eef6ee"))

    # нижній підсумок
    f.append(fitbox(40, 412, 880, 112,
                    "що реєстр знає про фабрику, не відкриваючи файл:\n"
                    "ім'я · klass · опис · автор · rank\n"
                    "шаблони падів разом із їхніми caps · тип для створення",
                    size=15, fill="#f7f4ee"))

    render(os.path.join(OUT, 'plugin-anatomy.svg'), W, H, *f,
           title="Плагін: один файл, один символ, кілька записів у реєстрі")


# ── 2. Холодний і звичайний старт ──────────────────────────────────────────
def fig_registry_start():
    W, H = 1000, 640
    f = []
    lx, rx = 55, 535
    bw = 410
    cxl, cxr = lx + bw / 2, rx + bw / 2

    f.append(text(cxl, 58, "перший старт: кеш порожній або застарів", size=14, bold=True))
    f.append(text(cxr, 58, "звичайний старт: кеш свіжий", size=14, bold=True))

    rows = [(74, 58), (162, 58), (250, 76), (356, 58), (444, 76)]

    left = [
        "gst_init(): звірка кешу з файлами",
        "обхід GST_PLUGIN_PATH і системних тек",
        "fork → gst-plugin-scanner\nвідкриває КОЖЕН файл плагіна",
        "описи вертаються в батька каналом",
        "registry.x86_64.bin переписано\nсотні мілісекунд",
    ]
    right = [
        "gst_init(): часи й розміри збіглися",
        "прочитано registry.x86_64.bin",
        "усі фабрики в пам'яті:\nімена, caps, rank — жодного dlopen",
        "конвеєр збирається за описами",
        "dlopen лише тих файлів,\nчиї елементи справді створено",
    ]
    fills_l = ["#f4f6f8", "#f4f6f8", "#fdecea", "#f4f6f8", "#fdecea"]
    fills_r = ["#f4f6f8", "#f4f6f8", "#eef6ee", "#f4f6f8", "#eef6ee"]

    for i, (y, h) in enumerate(rows):
        f.append(fitbox(lx, y, bw, h, left[i], size=14, fill=fills_l[i]))
        f.append(fitbox(rx, y, bw, h, right[i], size=14, fill=fills_r[i]))
        if i < len(rows) - 1:
            ny = rows[i + 1][0]
            f.append(arrow(cxl, y + h + 3, cxl, ny - 4))
            f.append(arrow(cxr, y + h + 3, cxr, ny - 4))

    f.append(fitbox(55, 548, 890, 66,
                    "кеш — не істина: істина у файлах плагінів.\n"
                    "Змінився час або розмір файла — саме цей плагін перескановують заново.",
                    size=15, fill="#f7f4ee"))

    render(os.path.join(OUT, 'registry-start.svg'), W, H, *f,
           title="Два шляхи старту: перескановування проти читання кешу")


# ── 3. Вибір декодера за rank ──────────────────────────────────────────────
def fig_rank_autoplug():
    W, H = 960, 600
    f = []
    cx = 480

    f.append(fitbox(280, 58, 400, 56, "caps потоку: video/x-h264", size=15, fill="#eef6ee"))
    f.append(arrow(cx, 118, cx, 146))

    f.append(fitbox(180, 150, 600, 68,
                    "з реєстру: усі фабрики класу Decoder,\n"
                    "чий sink-шаблон приймає ці caps", size=15))
    f.append(arrow(cx, 222, cx, 250))

    rows = [
        ("апаратний декодер · rank 300", "#fdecea"),
        ("другий апаратний · rank 260", "#f4f6f8"),
        ("програмний декодер · rank 256", "#f4f6f8"),
        ("запасний декодер · rank 64", "#f4f6f8"),
    ]
    y = 254
    for label, fill in rows:
        f.append(fitbox(200, y, 560, 46, label, size=15, fill=fill))
        y += 54

    f.append(text(150, 300, "вище", size=12, color=MUTED, anchor="end"))
    f.append(text(150, 430, "нижче", size=12, color=MUTED, anchor="end"))
    f.append(arrow(120, 316, 120, 412))

    f.append(arrow(cx, 474, cx, 502))
    f.append(fitbox(150, 506, 660, 62,
                    "згори вниз: створити → злінкувати → якщо не вдалося,\n"
                    "спробувати наступну фабрику", size=15, fill="#f7f4ee"))

    render(os.path.join(OUT, 'rank-autoplug.svg'), W, H, *f,
           title="Rank вирішує порядок спроб, а не саму можливість")


# ── 4. Історія реєстру: від XML до бінарного кешу з окремим сканером ───────
def fig_registry_history():
    W, H = 1000, 700
    f = []

    spine_x = 252
    rows = [
        (96, "січень 2001 · 0.1.0",
         "XML-реєстр «на кшталт ld.so.cache»:\n"
         "кеш самоописів заведено відразу, сканування — у процесі застосунку"),
        (224, "грудень 2005 · 0.10.0",
         "перебудова ядра заради потоків і планування;\n"
         "формат реєстру лишається XML"),
        (352, "2008 · 0.10.20",
         "бінарний реєстр стає типовим:\n"
         "розбір XML коштував помітну частку часу старту"),
        (480, "2009 · гілка 0.10",
         "сканування виноситься в окремий процес-помічник\n"
         "(з листопада 2009 він зветься gst-plugin-scanner)"),
        (608, "вересень 2012 · 1.0",
         "XML-реєстру більше немає:\n"
         "лишається бінарний кеш плюс помічник — те, що бачимо нині"),
    ]

    f.append(line(spine_x, 74, spine_x, 630, color=MUTED, sw=2))

    for cy, when, what in rows:
        f.append(text(232, cy + 5, when, size=13, bold=True, anchor="end"))
        f.append(circle(spine_x, cy, 8, fill="#ffffff", stroke=LINE, sw=2))
        f.append(fitbox(276, cy - 40, 684, 80, what, size=14))

    f.append(text(W / 2, 668,
                  "усі п'ять кроків розв'язують ту саму задачу: дізнатися, що вміють файли, "
                  "і не платити за це щоразу",
                  size=13, color=MUTED))

    render(os.path.join(OUT, 'registry-history.svg'), W, H, *f,
           title="Реєстр GStreamer: що змінювалося й заради чого")


# ── 5. Маска типу проти рядка klass (до довідки інтерфейсу) ────────────────
def fig_factory_type_match():
    W, H = 1000, 620
    f = []

    f.append(fitbox(60, 66, 380, 100,
                    "маска запиту\nGST_ELEMENT_FACTORY_TYPE_DECODER\n"
                    "| GST_ELEMENT_FACTORY_TYPE_MEDIA_VIDEO",
                    size=13, fill="#eaf0fd"))
    f.append(fitbox(560, 66, 380, 100,
                    "фабрика avdec_h264\nметадані klass:\n«Codec/Decoder/Video»",
                    size=13, fill="#eef6ee"))

    f.append(arrow(250, 170, 410, 210))
    f.append(arrow(750, 170, 590, 210))

    f.append(fitbox(160, 214, 680, 76,
                    "крок 1 — вид елемента: у масці стоїть біт DECODER,\n"
                    "тож у klass шукають підрядок «Decoder» → знайдено",
                    size=15))
    f.append(arrow(500, 294, 500, 320))

    f.append(fitbox(160, 324, 680, 76,
                    "крок 2 — медіа: у масці є біт MEDIA_VIDEO,\n"
                    "тож у klass має бути ще й «Video» → знайдено",
                    size=15))
    f.append(arrow(500, 404, 500, 430))

    f.append(fitbox(280, 434, 440, 52,
                    "фабрика лишається в списку", size=15, fill="#eef6ee"))

    f.append(fitbox(60, 506, 880, 86,
                    "порівнюють не числа, а текст: біт PARSER вимагає ОБОХ підрядків —\n"
                    "«Parser» і «Codec». Елемент із klass «Filter/Parser» під маску не підпаде.",
                    size=15, fill="#f7f4ee"))

    render(os.path.join(OUT, 'factory-type-match.svg'), W, H, *f,
           title="Маска типу перевіряється підрядком у рядку klass")


# ── Шість воріт між файлом .c і працездатним елементом ─────────────────────
def fig_plugin_gates():
    W, H = 1060, 842
    f = []
    lx, bw = 46, 510
    rx, rw = 606, 410
    cxl = lx + bw / 2

    f.append(text(cxl, 50, "що мусить збігтися", size=15, bold=True))
    f.append(text(rx + rw / 2, 50, "як воно мовчить, коли не збіглося",
                  size=15, bold=True))

    gates = [
        ("збірка: libgstmyfilter.so\nтри бібліотеки, PACKAGE визначено",
         "'PACKAGE' undeclared —\nєдина гучна помилка з шести"),
        ("ім'я файла ↔ ім'я в GST_PLUGIN_DEFINE\nсимвол gst_plugin_myfilter_get_desc",
         "«is not a GStreamer plugin»:\nточки входу не знайдено"),
        ("файл лежить у GST_PLUGIN_PATH,\nчас або розмір змінилися",
         "gst-inspect не бачить нічого\nабо показує стару копію"),
        ("версія: major точно, minor ≤ ядра",
         "«has incompatible version,\nnot loading» рівнем WARNING"),
        ("plugin_init → фабрика «myfilter»,\nметадані й шаблони падів із класу",
         "No such element or plugin"),
        ("klass дав категорію,\ncaps шаблону перетнулися з потоком",
         "елемент є й працює на ім'я,\nале автопідбір його не бере"),
    ]

    y0, gh, gap = 74, 94, 22
    for i, (leftt, rightt) in enumerate(gates):
        y = y0 + i * (gh + gap)
        f.append(fitbox(lx, y, bw, gh, leftt, size=14, fill="#eef6ee"))
        f.append(fitbox(rx, y, rw, gh, rightt, size=14, fill="#fdecea"))
        if i < len(gates) - 1:
            f.append(arrow(cxl, y + gh + 3, cxl, y + gh + gap - 4))

    f.append(fitbox(46, 774, 970, 48,
                    "П'ять перевірок із шести не зупиняють запуск — "
                    "вони просто не додають вашого елемента в реєстр.",
                    size=15, fill="#f7f4ee"))

    render(os.path.join(OUT, 'plugin-gates.svg'), W, H, *f,
           title="Шлях від файла .c до елемента: шість перевірок і шість мовчань")


if __name__ == '__main__':
    fig_anatomy()
    fig_registry_start()
    fig_rank_autoplug()
    fig_registry_history()
    fig_factory_type_match()
    fig_plugin_gates()
    print("ok")
