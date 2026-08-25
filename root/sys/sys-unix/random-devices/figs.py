# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

PURPLE = "#7a4fb0"
SOFT = "#fbfcff"
WARM = "#b8860b"


# ── 1. Що ядро вважає непередбачним і за що дає залік ───────────────────────
def fig_sources():
    W, H = 1300, 830
    p = []

    p.append(fitbox(40, 50, 300, 48, "подія, яку бачить ядро", size=13,
                    fill="#eaf0fd", stroke=NEG, sw=1.8, color=NEG, bold=True))
    p.append(fitbox(360, 50, 580, 48, "що саме в ній не може відтворити стороння людина",
                    size=13, fill="#eafaf0", stroke=FIELD, sw=1.8, color=FIELD, bold=True))
    p.append(fitbox(960, 50, 300, 48, "чи додає до лічильника ентропії", size=13,
                    fill="#f6efff", stroke=PURPLE, sw=1.8, color=PURPLE, bold=True))

    rows = [
        ("апаратне переривання", NEG,
         "молодші розряди лічильника тактів у мить приходу\nразом з номером лінії та адресою повернення",
         "так, дрібними порціями", FIELD),
        ("натиск клавіші, рух миші", NEG,
         "код клавіші плюс момент, коли людина її натиснула,\nз точністю до наносекунд",
         "так", FIELD),
        ("звіт диска про завершення", NEG,
         "коли саме контролер сказав «готово» —\nмеханіка й черга дають розкид",
         "так", FIELD),
        ("інструкція RDSEED / RDRAND", WARM,
         "шум фізичного джерела всередині самого кристала —\nготові біти, а не сировина",
         "лише якщо ввімкнено\nrandom.trust_cpu", WARM),
        ("прошивка й завантажувач", WARM,
         "число, яке передали через протокол UEFI RNG\nабо запис rng-seed у дереві пристроїв",
         "лише якщо ввімкнено\nrandom.trust_bootloader", WARM),
        ("насіння з минулого запуску", MUTED,
         "стан генератора, збережений у файл перед вимкненням\n— але образ диска можна скопіювати",
         "ні, лише домішують", POS),
        ("серійні номери, MAC-адреси", MUTED,
         "унікальні для примірника заліза,\nпроте кожен охочий може їх прочитати",
         "ні, лише домішують", POS),
        ("власне тремтіння лічильника", PURPLE,
         "скільки тактів набігло на однаковому циклі —\nядро крутить його навмисне, коли бракує решти",
         "так, під час завантаження", FIELD),
    ]

    y = 116
    RH = 76
    for what, accent, why, credit, ccol in rows:
        p.append(fitbox(40, y, 300, RH, what, size=12, fill=SOFT,
                        stroke=accent, sw=1.8, color=accent, bold=True))
        p.append(arrow(348, y + RH / 2, 352, y + RH / 2, color=accent, sw=1.6))
        p.append(fitbox(360, y, 580, RH, why, size=12, fill="#ffffff",
                        stroke=MUTED, sw=1.3, color=INK))
        p.append(fitbox(960, y, 300, RH, credit, size=12, fill="#ffffff",
                        stroke=ccol, sw=1.5, color=ccol, bold=True))
        y += RH + 12

    p.append(fitbox(40, y + 14, 1220, 58,
                    "жодна подія сама по собі не дає «випадкового байта» — "
                    "кожна приносить кілька бітів невідомості, і лише сума має вагу",
                    size=13, fill="#eceff2", stroke=INK, sw=1.8, color=INK, bold=True))

    render(os.path.join(OUT, "sources.svg"), W, H, *p,
           title="Джерела непередбачності та залік ентропії")


# ── 2. Дві машини: накопичувач і генератор ─────────────────────────────────
def fig_pipeline():
    W, H = 1300, 700
    p = []

    cols = [
        ("події заліза", NEG,
         "переривання, введення,\nдиски, інструкція\nпроцесора, прошивка",
         "надходять коли завгодно,\nдрібними й нерівними\nпорціями"),
        ("накопичувач", FIELD,
         "стан геш-функції\nBLAKE2s, 256 бітів\n(mix_pool_bytes)",
         "усе вмішується всередину;\nдістати назад окремий\nвнесок неможливо"),
        ("ключ генератора", PURPLE,
         "base_crng: ключ ChaCha20\nна 256 бітів\n+ номер покоління",
         "перезаряджається з\nнакопичувача раз на 60 с\nі при появі ентропії"),
        ("потоки на ядрах", WARM,
         "на кожному ядрі свій\nпримірник ChaCha20,\nбез спільного замка",
         "перший блок шифру стирає\nвласний ключ, решта йде\nна вихід"),
    ]

    x = 40
    BW, GAP = 268, 44
    for name, accent, what, note in cols:
        p.append(fitbox(x, 56, BW, 50, name, size=15, fill=SOFT,
                        stroke=accent, sw=2, color=accent, bold=True))
        p.append(fitbox(x, 124, BW, 96, what, size=12, fill="#ffffff",
                        stroke=accent, sw=1.5, color=INK))
        p.append(fitbox(x, 238, BW, 96, note, size=12, fill="#ffffff",
                        stroke=MUTED, sw=1.2, color=MUTED))
        if x + BW + GAP < 40 + 4 * (BW + GAP):
            p.append(arrow(x + BW + 6, 81, x + BW + GAP - 6, 81, color=accent, sw=2))
        x += BW + GAP

    RIGHT = 40 + 4 * BW + 3 * GAP

    p.append(fitbox(40, 372, RIGHT - 40, 52,
                    "усе, що ліворуч, працює на дві потреби: набрати перші 256 бітів невідомості "
                    "й далі не дати ключу застаріти",
                    size=13, fill="#eceff2", stroke=INK, sw=1.8, color=INK, bold=True))

    outs = [
        ("getrandom()", "виклик без файлів\nі без дескрипторів"),
        ("/dev/urandom, /dev/random", "той самий потік,\nвиданий через read()"),
        ("сама система", "адреси ASLR, куки стека,\nномери портів, ключі"),
    ]
    ox = 40
    OW = (RIGHT - 40 - 2 * 40) / 3
    for name, note in outs:
        p.append(arrow(ox + OW / 2, 436, ox + OW / 2, 470, color=WARM, sw=2))
        p.append(fitbox(ox, 478, OW, 46, name, size=13, fill="#fff8e8",
                        stroke=WARM, sw=1.8, color=WARM, bold=True))
        p.append(fitbox(ox, 534, OW, 62, note, size=12, fill="#ffffff",
                        stroke=MUTED, sw=1.2, color=MUTED))
        ox += OW + 40

    p.append(text(W / 2, 638,
                  "накопичувач збирає невідомість, генератор роздає її без обмежень",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "pipeline.svg"), W, H, *p,
           title="Накопичувач на BLAKE2s і генератор на ChaCha20")


# ── 3. Три стани генератора під час завантаження ───────────────────────────
def fig_boot_states():
    W, H = 1300, 640
    p = []

    p.append(fitbox(40, 50, 330, 62, "як просять випадкові байти", size=13,
                    fill="#eceff2", stroke=INK, sw=1.8, color=INK, bold=True))
    heads = [
        ("ключа ще немає\n(зібрано < 128 бітів)", POS),
        ("ранній ключ\n(зібрано 128 бітів)", WARM),
        ("готовий ключ\n(зібрано 256 бітів)", FIELD),
    ]
    hx = 390
    CW = 288
    for htxt, hcol in heads:
        p.append(fitbox(hx, 50, CW, 62, htxt, size=12, fill=SOFT,
                        stroke=hcol, sw=2, color=hcol, bold=True))
        hx += CW + 6

    rows = [
        ("getrandom() без прапорців", ("чекає", POS), ("чекає", WARM), ("віддає одразу", FIELD)),
        ("getrandom(GRND_NONBLOCK)", ("помилка EAGAIN", POS), ("помилка EAGAIN", WARM), ("віддає одразу", FIELD)),
        ("getrandom(GRND_INSECURE)", ("віддає передбачне", POS), ("віддає", WARM), ("віддає одразу", FIELD)),
        ("читання з /dev/random", ("чекає", POS), ("чекає", WARM), ("віддає одразу", FIELD)),
        ("читання з /dev/urandom", ("віддає + запис у журнал", POS), ("віддає", WARM), ("віддає одразу", FIELD)),
        ("get_random_bytes() у ядрі", ("віддає передбачне", POS), ("віддає", WARM), ("віддає одразу", FIELD)),
    ]

    y = 128
    RH = 62
    for name, c1, c2, c3 in rows:
        p.append(fitbox(40, y, 330, RH, name, size=12, fill="#ffffff",
                        stroke=INK, sw=1.3, color=INK, bold=True))
        cx = 390
        for txt, col in (c1, c2, c3):
            p.append(fitbox(cx, y, CW, RH, txt, size=12, fill="#ffffff",
                            stroke=col, sw=1.5, color=col))
            cx += CW + 6
        y += RH + 10

    p.append(fitbox(40, y + 12, 1222, 58,
                    "після переходу в правий стовпчик різниці між усіма рядками більше немає — "
                    "увесь клопіт випадковості вміщається в перші секунди роботи системи",
                    size=13, fill="#eceff2", stroke=INK, sw=1.8, color=INK, bold=True))

    render(os.path.join(OUT, "boot-states.svg"), W, H, *p,
           title="Поведінка інтерфейсів у трьох станах генератора")


# ── 4. Часова смуга підсистеми випадковості (вставка hist) ─────────────────
def fig_timeline():
    W = 1320
    rows = [
        ("1994 · random.c\n1.3.30 (1995)", NEG,
         "Теодор Тсо пише random.c: накопичувач-LFSR на 4096 бітів, бухгалтерія\n"
         "ентропії, гешування замість шифру через експортні обмеження",
         "два файли: /dev/random блокує, /dev/urandom — ні"),
        ("2014 · 3.17", NEG,
         "скарга LibreSSL: файл потребує дескриптора й може бути відсутнім\n"
         "у chroot — з'являється системний виклик getrandom()",
         "перший інтерфейс, що вміє чекати засівання"),
        ("2016 · 4.8", MUTED,
         "генератор переведено на потоковий шифр ChaCha20",
         "якість байтів більше не залежить від лічильника"),
        ("2019 · 5.4", WARM,
         "оптимізація ext4 у 5.3 зменшила переривання й машини перестали\n"
         "завантажуватися; Торвальдс додає try_to_generate_entropy()",
         "джерелом стає дрейф власного планувальника"),
        ("2020 · 5.6", WARM,
         "Енді Лутомирський прибирає блокувальний накопичувач,\n"
         "Тсо погоджується відмовитися від бухгалтерії",
         "/dev/random зрівняно з /dev/urandom"),
        ("2022 · 5.17–5.18", PURPLE,
         "Джейсон Доненфельд переписує підсистему: SHA-1 → BLAKE2s,\n"
         "стан на 256 бітів замість LFSR, раунд SipHash у перериваннях",
         "поріг готовності піднято зі 128 до 256 бітів"),
        ("2024 · 6.11", FIELD,
         "getrandom() покладено у vDSO — байти породжуються\n"
         "в самому процесі, без переходу в ядро",
         "ключ ядро стирає при fork і при клонуванні ВМ"),
    ]

    X0, XA = 40, 40
    WA = 210
    XB = XA + WA + 14
    WB = 660
    XC = XB + WB + 14
    WC = 360
    RH = 96
    y = 46

    p = []
    p.append(fitbox(XA, y, WA, 40, "рік · версія ядра", size=13,
                    fill="#eceff2", stroke=INK, sw=1.8, color=INK, bold=True))
    p.append(fitbox(XB, y, WB, 40, "що сталося", size=13,
                    fill="#eceff2", stroke=INK, sw=1.8, color=INK, bold=True))
    p.append(fitbox(XC, y, WC, 40, "що це змінило для читача байтів", size=13,
                    fill="#eceff2", stroke=INK, sw=1.8, color=INK, bold=True))
    y += 40 + 16

    for label, col, what, effect in rows:
        p.append(fitbox(XA, y, WA, RH, label, size=14,
                        fill="#ffffff", stroke=col, sw=2.0, color=col, bold=True))
        p.append(fitbox(XB, y, WB, RH, what, size=12.5,
                        fill=SOFT, stroke=col, sw=1.5, color=INK))
        p.append(fitbox(XC, y, WC, RH, effect, size=12.5,
                        fill="#ffffff", stroke=MUTED, sw=1.3, color=MUTED))
        y += RH + 12

    H = y + 20
    render(os.path.join(OUT, "rng-timeline.svg"), W, H, *p,
           title="Часова смуга підсистеми випадковості Linux")


if __name__ == "__main__":
    fig_sources()
    fig_pipeline()
    fig_boot_states()
    fig_timeline()
    print("ok")
