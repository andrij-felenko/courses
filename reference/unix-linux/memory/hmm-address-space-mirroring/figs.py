# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

SOFT = "#fbfcff"
WARM = "#fdecea"
COOL = "#eaf0fd"
GREENF = "#eafaf0"
PALE = "#f4f6f8"


# ── 1. hmm_range_fault: що подають і що дістають ─────────────────────────────
def fig_range_fault():
    W, H = 1420, 720
    p = []

    # ── вхід ──
    p.append(fitbox(40, 60, 330, 46, "що подає драйвер", size=14,
                    fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))
    inp = [
        "діапазон віртуальних адрес\nпростору процесу",
        "політика на весь діапазон:\nчи будувати сторінку,\nчи потрібен запис",
        "маска, якою окремій сторінці\nдозволено мати свою вимогу",
    ]
    y = 122
    for s in inp:
        h = 78 if s.count("\n") == 1 else 96
        p.append(fitbox(40, y, 330, h, s, size=12.5,
                        fill=SOFT, stroke=NEG, sw=1.3, color=INK))
        y += h + 16

    # ── ядро ──
    p.append(arrow(382, 300, 442, 300, MUTED, sw=2))
    p.append(fitbox(456, 60, 430, 46, "ядро йде шляхом звичайного збою",
                    size=14, fill=GREENF, stroke=FIELD, sw=1.8, color=FIELD, bold=True))
    mid = [
        "анонімна сторінка, якої ще немає —\nвиділити кадр і занулити",
        "сторінка файлу — прочитати\nз носія й покласти в кеш",
        "потрібен запис у спільну сторінку —\nрозщепити копіюванням при записі",
        "адреси немає в жодній ділянці —\nпомилка, а не сигнал програмі",
    ]
    y = 122
    for i, s in enumerate(mid):
        col = POS if i == 3 else FIELD
        p.append(fitbox(456, y, 430, 78, s, size=12.5,
                        fill="#fff", stroke=col, sw=1.3, color=INK))
        y += 94

    # ── вихід ──
    p.append(arrow(898, 300, 958, 300, MUTED, sw=2))
    p.append(fitbox(972, 60, 408, 46, "масив відповідей, по одній на сторінку",
                    size=13.5, fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))
    out = [
        "кадр 0x1a2b · чинний · можна писати",
        "кадр 0x1a2c · чинний · лише читання",
        "кадр 0x4f10 · чинний · пам'ять пристрою",
        "помилка: за цією адресою нічого немає",
    ]
    y = 122
    for i, s in enumerate(out):
        col = POS if i == 3 else MUTED
        p.append(fitbox(972, y, 408, 78, s, size=12.5,
                        fill=PALE if i != 3 else WARM, stroke=col, sw=1.3, color=INK))
        y += 94

    p.append(fitbox(40, 512, 1340, 84,
                    "жодного посилання на кадр узято не було: відповідь — не власність,\n"
                    "а лише твердження про стан таблиць у мить читання",
                    size=13.5, fill="#fff", stroke=FIELD, sw=1.8, color=INK))
    p.append(fitbox(40, 612, 1340, 68,
                    "тому чинність цієї відповіді тримає не лічильник посилань,\n"
                    "а послідовне число сповіщувача — і будь-яке скасування її знецінює",
                    size=13, fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))

    return render(os.path.join(OUT, "range-fault.svg"), W, H, *p,
                  title="Виклик не шукає готове відображення, а будує його — як зробив би збій процесора")


# ── 2. Два стани однієї віртуальної сторінки ────────────────────────────────
def fig_page_states():
    W, H = 1400, 760
    p = []

    p.append(fitbox(40, 58, 600, 50, "сторінка живе в системній пам'яті",
                    size=14.5, fill=COOL, stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(fitbox(760, 58, 600, 50, "сторінка живе в пам'яті пристрою",
                    size=14.5, fill=WARM, stroke=POS, sw=1.8, color=POS, bold=True))

    left = [
        ("запис у таблиці процесу", "звичайний, наявний:\nномер системного кадру"),
        ("таблиця пристрою", "той самий кадр,\nвписаний драйвером"),
        ("читає процесор", "напряму, з пам'яті"),
        ("читає прискорювач", "через шину, на кожне звертання"),
    ]
    right = [
        ("запис у таблиці процесу", "особливий, відсутній:\n«сторінка в пристрої»"),
        ("таблиця пристрою", "кадр власної пам'яті\nприскорювача"),
        ("читає процесор", "не може: дотик дає збій"),
        ("читає прискорювач", "з локальної пам'яті, на повній швидкості"),
    ]

    y = 132
    for i in range(4):
        k, v = left[i]
        p.append(fitbox(40, y, 250, 82, k, size=12.5,
                        fill=PALE, stroke=MUTED, sw=1.2, color=MUTED))
        p.append(fitbox(304, y, 336, 82, v, size=12.5,
                        fill=SOFT, stroke=NEG, sw=1.3, color=INK))
        k, v = right[i]
        p.append(fitbox(760, y, 250, 82, k, size=12.5,
                        fill=PALE, stroke=MUTED, sw=1.2, color=MUTED))
        p.append(fitbox(1024, y, 336, 82, v, size=12.5,
                        fill="#fff", stroke=POS, sw=1.3, color=INK))
        y += 98

    # переходи
    p.append(arrow(660, 210, 742, 210, FIELD, sw=2.4))
    p.append(fitbox(500, 552, 400, 74,
                    "переселення: драйвер копіює вміст\nсвоїм рушієм прямого доступу",
                    size=12.5, fill=GREENF, stroke=FIELD, sw=1.4, color=INK))
    p.append(arrow(742, 330, 660, 330, POS, sw=2.4))
    p.append(fitbox(940, 552, 420, 74,
                    "дотик процесора: збій кличе драйвера,\nі той повертає сторінку назад",
                    size=12.5, fill=WARM, stroke=POS, sw=1.4, color=INK))

    p.append(fitbox(40, 552, 420, 74,
                    "вказівник у програмі — той самий\nв обох станах, програма не бачить різниці",
                    size=12.5, fill=SOFT, stroke=NEG, sw=1.4, color=INK))

    p.append(fitbox(40, 654, 1320, 72,
                    "описувач кадру існує й для пам'яті пристрою — інакше зворотне відображення,\n"
                    "лічильники посилань і переселення не мали б за що взятися",
                    size=13, fill="#fff", stroke=FIELD, sw=1.7, color=INK))

    return render(os.path.join(OUT, "page-states.svg"), W, H, *p,
                  title="Одна віртуальна адреса, два місця, де можуть лежати її байти")


# ── 3. Три такти переселення ────────────────────────────────────────────────
def fig_migrate_phases():
    W, H = 1420, 700
    p = []

    p.append(fitbox(40, 58, 190, 48, "ядро", size=13.5,
                    fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))
    p.append(fitbox(40, 268, 190, 48, "драйвер", size=13.5,
                    fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))

    cols = [270, 560, 850, 1140]
    CW = 250

    kern = [
        "зібрати сторінки діапазону,\nзамкнути їх і вписати\nв таблицю запис «переселяється»",
        "",
        "поставити нові кадри\nв таблиці процесу\nзамість записів переселення",
        "розімкнути сторінки,\nвіддати посилання\nна старі кадри",
    ]
    drv = [
        "",
        "виділити кадри у своїй пам'яті\nй скопіювати вміст —\nце довго й асинхронно",
        "",
        "",
    ]
    names = ["такт перший", "робота драйвера", "такт другий", "такт третій"]

    for i in range(4):
        p.append(fitbox(cols[i], 58, CW, 48, names[i], size=13,
                        fill=COOL if i != 1 else GREENF,
                        stroke=NEG if i != 1 else FIELD, sw=1.5,
                        color=NEG if i != 1 else FIELD, bold=True))
        if kern[i]:
            p.append(fitbox(cols[i], 126, CW, 118, kern[i], size=12.5,
                            fill=SOFT, stroke=NEG, sw=1.3, color=INK))
        if drv[i]:
            p.append(fitbox(cols[i], 268, CW, 118, drv[i], size=12.5,
                            fill="#fff", stroke=FIELD, sw=1.3, color=INK))
        if i < 3:
            p.append(arrow(cols[i] + CW + 6, 186, cols[i + 1] - 6, 186, MUTED, sw=1.8))

    p.append(arrow(cols[0] + CW / 2, 250, cols[1] + CW / 2, 262, MUTED, sw=1.6))
    p.append(arrow(cols[1] + CW / 2, 392, cols[2] + CW / 2, 250, MUTED, sw=1.6))

    p.append(fitbox(270, 430, 1120, 82,
                    "поки триває копіювання, звертання до цих адрес натикається на запис переселення\n"
                    "й чекає — саме тому таких тактів три, а не один",
                    size=13, fill=GREENF, stroke=FIELD, sw=1.7, color=INK))
    p.append(fitbox(270, 530, 1120, 82,
                    "частина сторінок випадає з переселення ще на першому такті: закріплені,\n"
                    "прибиті до пам'яті, спільні з іншими — ядро гасить їм позначку, драйвер мусить це прийняти",
                    size=13, fill=WARM, stroke=POS, sw=1.7, color=INK))
    p.append(fitbox(270, 630, 1120, 52,
                    "такі сторінки лишаються віддзеркаленими, а не переселеними",
                    size=12.5, fill=PALE, stroke=MUTED, sw=1.3, color=MUTED))

    return render(os.path.join(OUT, "migrate-phases.svg"), W, H, *p,
                  title="Переселення розбите на такти, бо копіювання довше за будь-який замок")


# ── 4. Життя описувача кадру плати (для вставки proj-migrate-to-device) ─────
def fig_devpage_life():
    W, H = 1580, 680
    p = []

    cols = [40, 350, 660, 970, 1280]
    CW = 260

    names = [
        "у вільному пулі",
        "zone_device_page_init()",
        "у таблиці процесу",
        "migrate_to_ram()",
        "page_free()",
    ]
    bodies = [
        "описувач існує від самої реєстрації\nдіапазону, але не належить нікому;\nнаступний вільний драйвер\nзнаходить через zone_device_data",
        "драйвер бере кадр під переселення:\nлічильник стає одиницею,\nсторінка замикається,\nа pagemap дістає посилання",
        "такт другий вписав відсутній запис,\nщо вказує на цей описувач;\nтакт третій розімкнув сторінку\nй лишив її жити в таблиці",
        "процесор торкнувся адреси:\nдрайвер копіює вміст\nу системний кадр, а ядро знімає\nвідсутній запис із таблиці",
        "посилань не лишилося —\nядро само кличе зворотний виклик\nдрайвера; це і є free()\nрозподільника пам'яті плати",
    ]
    counts = [
        "лічильник: 0",
        "лічильник: 1 · сторінка замкнена",
        "лічильник: 1 · тримає запис таблиці",
        "лічильник: 1 → 0",
        "кадр знову в пулі, лічильник: 0",
    ]
    heads = [PALE, COOL, SOFT, WARM, GREENF]
    edges = [MUTED, NEG, NEG, POS, FIELD]

    for i in range(5):
        p.append(fitbox(cols[i], 58, CW, 46, names[i], size=13,
                        fill=heads[i], stroke=edges[i], sw=1.7,
                        color=edges[i], bold=True))
        p.append(fitbox(cols[i], 122, CW, 150, bodies[i], size=12,
                        fill="#fff", stroke=edges[i], sw=1.3, color=INK))
        p.append(fitbox(cols[i], 292, CW, 68, counts[i], size=12,
                        fill=PALE, stroke=MUTED, sw=1.2, color=MUTED))
        if i < 4:
            p.append(arrow(cols[i] + CW + 6, 197, cols[i + 1] - 6, 197,
                           MUTED, sw=2))

    # цикл замикається: з page_free назад у вільний пул
    p.append(line(cols[4] + CW / 2, 372, cols[4] + CW / 2, 412, MUTED, sw=1.8))
    p.append(line(cols[4] + CW / 2, 412, cols[0] + CW / 2, 412, MUTED, sw=1.8))
    p.append(arrow(cols[0] + CW / 2, 412, cols[0] + CW / 2, 374, MUTED, sw=1.8))

    p.append(fitbox(40, 444, 1500, 76,
                    "лічильник кадру ZONE_DEVICE не рахує, скільки пам'яті виділено — він означає рівно одне:\n"
                    "чи належить цей кадр комусь просто зараз",
                    size=13, fill="#fff", stroke=FIELD, sw=1.7, color=INK))
    p.append(fitbox(40, 544, 1500, 96,
                    "звідси обидві типові біди: __free_page() для кадру плати не існує взагалі,\n"
                    "а зайвий put_page() віддає в пул кадр, який ще стоїть у таблиці процесу —\n"
                    "наступне переселення видасть його вдруге, і два адресні простори поділять одні байти",
                    size=13, fill=WARM, stroke=POS, sw=1.7, color=INK))

    return render(os.path.join(OUT, "devpage-life.svg"), W, H, *p,
                  title="Кадр пам'яті пристрою живе за тими самими лічильниками, що й звичайний")


if __name__ == "__main__":
    print(fig_range_fault())
    print(fig_page_states())
    print(fig_migrate_phases())
    print(fig_devpage_life())
