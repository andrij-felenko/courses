# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Відкритий дріт: три загрози й три гарантії TLS ─────────────────────────
# Ідея: між пристроєм і сервером — чужа дорога (Wi-Fi ефір, чужі роутери). На ній
# сусід уміє РОБИТИ три речі: підслухати, підмінити байти, вдати з себе сервер.
# TLS дає рівно три відповіді: таємність, цілісність, автентичність.
def fig_open_wire():
    W, H = 780, 340
    p = []
    p.append(text(W / 2, 28, "Дріт між вами чужий: три загрози — три відповіді TLS", size=15, bold=True))

    # пристрій ── дорога ── сервер
    dy = 90
    p.append(fitbox(40, dy, 150, 60, "Пристрій\n(ваш МК)", size=12, fill="#eafaf0",
                    stroke=FIELD, sw=1.8, bold=True))
    p.append(fitbox(W - 190, dy, 150, 60, "Сервер\n(ваш у хмарі)", size=12, fill="#eafaf0",
                    stroke=FIELD, sw=1.8, bold=True))
    # чужа дорога посередині
    rx1, rx2 = 190, W - 190
    p.append(line(rx1 + 4, dy + 30, rx2 - 4, dy + 30, color=MUTED, sw=2.2, dash="7 5"))
    p.append(text(W / 2, dy + 16, "чужа дорога: ефір Wi-Fi, чужі роутери, інтернет", size=10.5, color=MUTED))
    # зловмисник сидить на дорозі
    p.append(fitbox(W / 2 - 70, dy + 44, 140, 34, "сусід на дорозі", size=11,
                    fill="#fdecea", stroke=POS, sw=1.8, bold=True))

    # три рядки: загроза → відповідь
    rows = [
        ("підслухати вміст", "ТАЄМНІСТЬ: усе шифроване — видно лише кашу"),
        ("підмінити байти", "ЦІЛІСНІСТЬ: печатка на пакеті; підправив — відкинуто"),
        ("вдати з себе сервер", "АВТЕНТИЧНІСТЬ: сервер доводить, хто він (сертифікат)"),
    ]
    y = dy + 110
    for i, (thr, ans) in enumerate(rows):
        yy = y + i * 44
        p.append(fitbox(40, yy, 250, 36, thr, size=11.5, fill="#fdecea", stroke=POS, sw=1.6, bold=True))
        p.append(arrow(295, yy + 18, 330, yy + 18, color=NEG, sw=2.0))
        p.append(fitbox(335, yy, W - 375, 36, ans, size=11, fill="#eafaf0", stroke=FIELD, sw=1.6))
    return render(os.path.join(OUT, "open-wire.svg"), W, H, *p)


# ── 2. Спільна таємниця з незнайомцем: ECDHE на очах у підслуховувача ─────────
# Ідея: обоє кидають у канал ВІДКРИТУ частку (public share). Підслуховувач бачить
# обидві частки — і все одно не може відтворити спільний секрет, бо для цього
# треба ПРИВАТНА частка, яка нікуди не виходила. Секрет народжується в обох
# головах однаково, але в дроті його немає ніколи.
def fig_shared_secret():
    W, H = 780, 330
    p = []
    p.append(text(W / 2, 28, "Спільний секрет народжується, але дротом не летить (ECDHE)", size=15, bold=True))

    lx, rx = 120, W - 120
    ty = 78
    # приватні частки (лишаються вдома)
    p.append(text(lx, ty, "приватна частка a", size=11, color=POS, bold=True))
    p.append(text(lx, ty + 16, "(нікуди не йде)", size=9.5, color=MUTED))
    p.append(text(rx, ty, "приватна частка b", size=11, color=POS, bold=True))
    p.append(text(rx, ty + 16, "(нікуди не йде)", size=9.5, color=MUTED))
    # пристрій / сервер
    p.append(fitbox(lx - 80, ty + 30, 160, 44, "Пристрій", size=12, fill="#eafaf0",
                    stroke=FIELD, sw=1.8, bold=True))
    p.append(fitbox(rx - 80, ty + 30, 160, 44, "Сервер", size=12, fill="#eafaf0",
                    stroke=FIELD, sw=1.8, bold=True))

    # обмін відкритими частками
    my = ty + 110
    p.append(arrow(lx + 84, my, rx - 84, my, color=NEG, sw=2.0))
    p.append(text(W / 2, my - 10, "відкрита частка A →", size=10.5, color=NEG))
    p.append(arrow(rx - 84, my + 26, lx + 84, my + 26, color=NEG, sw=2.0))
    p.append(text(W / 2, my + 44, "← відкрита частка B", size=10.5, color=NEG))
    # підслуховувач бачить обидві
    p.append(text(W / 2, my + 66, "сусід бачить A і B — і все одно безсилий", size=10, color=POS, bold=True))

    # спільний секрет унизу в обох
    sy = my + 84
    p.append(fitbox(lx - 90, sy, 180, 34, "секрет = f(a, B)", size=11, fill=FILL, stroke=LINE, sw=1.6, bold=True))
    p.append(fitbox(rx - 90, sy, 180, 34, "секрет = f(b, A)", size=11, fill=FILL, stroke=LINE, sw=1.6, bold=True))
    p.append(text(W / 2, sy + 22, "=", size=22, color=FIELD, bold=True))
    p.append(text(W / 2, sy - 6, "однакове число в обох головах", size=10, color=FIELD))
    return render(os.path.join(OUT, "shared-secret.svg"), W, H, *p)


# ── 3. Рукостискання TLS 1.3 за один оберт (1-RTT), і що воно коштує на МК ─────
# Ідея: показати послідовність повідомлень і де саме на мікроконтролері дорого —
# один оберт, але всередині нього — перевірка підпису й ЕС-математика (CPU),
# сертифікат сервера (кілька КБ RAM), запуск AEAD. Далі — дешевий обмін даними.
def fig_handshake_13():
    W, H = 800, 360
    p = []
    p.append(text(W / 2, 26, "Рукостискання TLS 1.3: один оберт, тоді дешевий потік", size=15, bold=True))

    lx, rx = 70, W - 70
    # колони
    p.append(fitbox(lx - 46, 50, 150, 34, "Пристрій", size=12, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True))
    p.append(fitbox(rx - 104, 50, 150, 34, "Сервер", size=12, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True))
    # вертикальні лінії життя
    p.append(line(lx, 90, lx, 320, color=MUTED, sw=1.2, dash="3 5"))
    p.append(line(rx, 90, rx, 320, color=MUTED, sw=1.2, dash="3 5"))

    def msg(y, x1, x2, label, sub=None, color=NEG):
        p.append(arrow(x1, y, x2, y, color=color, sw=2.0))
        mid = (x1 + x2) / 2
        p.append(text(mid, y - 8, label, size=11, color=color, bold=True))
        if sub:
            p.append(text(mid, y + 14, sub, size=9.5, color=MUTED))

    msg(120, lx, rx, "ClientHello + відкрита частка", "«ось моя частка ECDHE, наперед»")
    msg(175, rx, lx, "ServerHello + частка + СЕРТИФІКАТ + підпис", "тут дорого на МК: RAM + CPU", color=POS)
    # позначка вартості праворуч
    p.append(text(rx + 6, 195, "← сертифікат: кілька КБ RAM;", size=9.5, color=POS, anchor="start"))
    p.append(text(rx + 6, 209, "   перевірка підпису: CPU", size=9.5, color=POS, anchor="start"))
    msg(240, lx, rx, "Finished (з цього місця все шифроване)", "дані вже можна слати", color=FIELD)

    # смуга «оберт лише один»
    p.append(line(lx - 30, 120, lx - 30, 240, color=NEG, sw=2.2))
    p.append(text(lx - 44, 180, "один\nоберт", size=10, color=NEG, bold=True, anchor="middle"))

    p.append(fitbox(60, 290, W - 120, 44,
                    "Після рукостискання — симетричний AEAD: шифрувати й перевіряти кожен пакет дешево. "
                    "Дорога лише ПЕРША зустріч; тому її потім пропускають (відновлення сесії).",
                    size=11, fill=FILL, stroke=LINE, sw=1.5))
    return render(os.path.join(OUT, "handshake-13.svg"), W, H, *p)


# ── 4. Куди на МК тиснуть вимоги TLS: RAM, ROM, CPU, довіра ───────────────────
# Ідея: на великому комп'ютері TLS «безкоштовний», на МК — ні. Чотири окремі
# тиски, кожен зі своєю ціною й своїм важелем послаблення. Це головна карта теми.
def fig_mcu_costs():
    W, H = 780, 340
    p = []
    p.append(text(W / 2, 28, "На мікроконтролері TLS тисне у чотири боки", size=15, bold=True))

    cards = [
        ("RAM", "буфер запису до 16 КБ +\n~7–8 КБ на рукостискання",
         "важіль: зменшити max fragment", NEG),
        ("ROM (Flash)", "код крипто, крива, розбір\nсертифіката — десятки КБ",
         "важіль: лишити один набір шифрів", NEG),
        ("CPU / час", "ЕС-математика й перевірка\nпідпису — сотні мс",
         "важіль: апаратне крипто, менша крива", POS),
        ("Довіра / ключі", "де тримати сертифікати CA\nі власний приватний ключ",
         "важіль: eFuse, захищений елемент", FIELD),
    ]
    cw, chh, gx, gy = 350, 120, 20, 16
    x0, y0 = 40, 60
    for i, (title, body, lever, col) in enumerate(cards):
        cx = x0 + (i % 2) * (cw + gx)
        cy = y0 + (i // 2) * (chh + gy)
        p.append(rect(cx, cy, cw, chh, fill="#fcfcfd", stroke=col, sw=1.8))
        p.append(text(cx + 14, cy + 24, title, size=14, color=col, bold=True, anchor="start"))
        p.append(fitbox(cx + 12, cy + 34, cw - 24, 46, body, size=11, fill=FILL, stroke=LINE, sw=1.2))
        p.append(text(cx + 14, cy + chh - 12, lever, size=10, color=MUTED, anchor="start"))
    return render(os.path.join(OUT, "mcu-costs.svg"), W, H, *p)


# ══════════════════════════════════════════════════════════════════════════
#  ДЕТАЛЬНА (-d): глибші фігури — механіка, якої нема в базовій
# ══════════════════════════════════════════════════════════════════════════

# ── 5. Дерево ключів TLS 1.3: як з одного секрету ECDHE виростає ціла родина ──
# Ідея: спільний секрет ECDHE не вживається напряму. Він проходить крізь
# HKDF-сходи (Extract → Derive-Secret), і на кожному щаблі народжується окремий
# ключ для окремої ролі. Це головна причина, чому TLS 1.3 стійкіший: кожен ключ
# ізольований, витік одного не оголює інших. Показуємо ДЕРЕВО виведення.
def fig_key_schedule():
    W, H = 820, 470
    p = []
    p.append(text(W / 2, 26, "Дерево ключів TLS 1.3: один секрет ECDHE → ціла родина", size=15, bold=True))

    cx = W / 2
    # три вузли-секрети на центральній осі
    p.append(fitbox(cx - 110, 48, 220, 34, "Early Secret", size=12,
                    fill=FILL, stroke=MUTED, sw=1.6, bold=True))
    p.append(text(cx + 150, 65, "= HKDF-Extract(0, PSK|0)", size=9.5, color=MUTED, anchor="start"))

    # вливання секрету ECDHE збоку
    p.append(fitbox(40, 108, 150, 40, "секрет ECDHE\n(з рукостискання)", size=10,
                    fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True))
    p.append(arrow(192, 128, cx - 112, 128, color=FIELD, sw=2.0))

    p.append(fitbox(cx - 110, 112, 220, 34, "Handshake Secret", size=12,
                    fill="#eef4ff", stroke=NEG, sw=1.8, bold=True))
    p.append(text(cx + 150, 129, "= HKDF-Extract(dHS, ECDHE)", size=9.5, color=MUTED, anchor="start"))

    p.append(fitbox(cx - 110, 176, 220, 34, "Master Secret", size=12,
                    fill=FILL, stroke=MUTED, sw=1.6, bold=True))
    p.append(text(cx + 150, 193, "= HKDF-Extract(dMS, 0)", size=9.5, color=MUTED, anchor="start"))

    # вертикальні зв'язки між секретами
    p.append(arrow(cx, 82, cx, 112, color=LINE, sw=1.8))
    p.append(arrow(cx, 146, cx, 176, color=LINE, sw=1.8))

    # відгалуження від Handshake Secret — два traffic secret рукостискання
    hy = 129
    p.append(arrow(cx - 110, hy, cx - 230, 250, color=NEG, sw=1.6))
    p.append(arrow(cx + 110, hy, cx + 230, 250, color=NEG, sw=1.6))
    p.append(fitbox(cx - 340, 250, 210, 40, "client_hs_traffic\nшифр рукостискання →", size=9.5,
                    fill="#eef4ff", stroke=NEG, sw=1.4))
    p.append(fitbox(cx + 130, 250, 210, 40, "server_hs_traffic\n← шифр рукостискання", size=9.5,
                    fill="#eef4ff", stroke=NEG, sw=1.4))

    # відгалуження від Master Secret — два application traffic secret
    my = 193
    p.append(arrow(cx - 110, my, cx - 230, 330, color=FIELD, sw=1.6))
    p.append(arrow(cx + 110, my, cx + 230, 330, color=FIELD, sw=1.6))
    p.append(fitbox(cx - 330, 330, 200, 40, "client_app_traffic\n(ваші дані →)", size=9.5,
                    fill="#eafaf0", stroke=FIELD, sw=1.4))
    p.append(fitbox(cx + 130, 330, 200, 40, "server_app_traffic\n(← ваші дані)", size=9.5,
                    fill="#eafaf0", stroke=FIELD, sw=1.4))
    # і resumption secret — на квиток
    p.append(arrow(cx, my + 17, cx, 330, color=MUTED, sw=1.6))
    p.append(fitbox(cx - 95, 330, 190, 40, "resumption_secret\n(майбутній квиток)", size=9.5,
                    fill=FILL, stroke=MUTED, sw=1.4))

    p.append(fitbox(50, 398, W - 100, 56,
                    "Кожен щабель — HKDF-Extract (втягнути ентропію) + Derive-Secret (виростити ключ ролі).\n"
                    "Ключі РІЗНІ для рукостискання й даних, для клієнта й сервера, для квитка.\n"
                    "Витік одного не оголює інших — саме ця ізоляція й робить 1.3 міцнішим за 1.2.",
                    size=10.5, fill=FILL, stroke=LINE, sw=1.4))
    return render(os.path.join(OUT, "key-schedule.svg"), W, H, *p)


# ── 6. Як запечатано ОДИН запис: AEAD, nonce = лічильник XOR IV ───────────────
# Ідея: після рукостискання кожен запис іде через AEAD. Ключова тонкість 1.3 —
# nonce не передається, а РАХУЄТЬСЯ з лічильника записів XOR фіксований IV. Тому
# кожен запис має унікальний nonce без жодного зайвого байта в дроті, а лічильник
# ще й ловить викидання/перестановку записів. Показуємо анатомію одного запису.
def fig_aead_record():
    W, H = 800, 380
    p = []
    p.append(text(W / 2, 26, "Один захищений запис: AEAD і nonce з лічильника", size=15, bold=True))

    # ── зліва: побудова nonce ──
    p.append(text(150, 62, "1. Побудова nonce (не передається!)", size=11.5, color=NEG, bold=True))
    p.append(fitbox(40, 78, 100, 34, "seq = 7", size=11, fill=FILL, stroke=MUTED, sw=1.5, bold=True))
    p.append(text(150, 100, "XOR", size=13, color=POS, bold=True))
    p.append(fitbox(180, 78, 120, 34, "write_iv\n(фікс., 12 Б)", size=9.5, fill="#eef4ff", stroke=NEG, sw=1.5))
    p.append(arrow(150, 116, 150, 140, color=LINE, sw=1.8))
    p.append(fitbox(70, 140, 200, 32, "nonce запису №7 (унікальний)", size=10,
                    fill="#eef4ff", stroke=NEG, sw=1.6, bold=True))

    # ── центр: AEAD-функція ──
    p.append(rect(330, 70, 180, 200, fill="#fcfcfd", stroke=FIELD, sw=2.0))
    p.append(text(420, 92, "AEAD-seal", size=13, color=FIELD, bold=True))
    p.append(fitbox(345, 104, 150, 30, "ключ app_traffic", size=10, fill="#eafaf0", stroke=FIELD, sw=1.3))
    p.append(fitbox(345, 140, 150, 30, "nonce №7", size=10, fill="#eef4ff", stroke=NEG, sw=1.3))
    p.append(fitbox(345, 176, 150, 30, "дані (plaintext)", size=10, fill=FILL, stroke=LINE, sw=1.3))
    p.append(fitbox(345, 212, 150, 30, "заголовок (AAD)", size=10, fill=FILL, stroke=MUTED, sw=1.3))

    # ── справа: результат — шифротекст + тег ──
    p.append(arrow(514, 170, 560, 170, color=LINE, sw=2.0))
    p.append(fitbox(566, 120, 200, 44, "шифротекст\n(нечитабельний)", size=10.5,
                    fill=FILL, stroke=LINE, sw=1.6))
    p.append(fitbox(566, 176, 200, 44, "тег цілісності (16 Б)\nпідправив — не сходиться", size=9.5,
                    fill="#fdecea", stroke=POS, sw=1.6, bold=True))

    p.append(fitbox(50, 296, W - 100, 68,
                    "Лічильник seq зростає на кожен запис і НІКОЛИ не повторюється в межах ключа —\n"
                    "тому nonce унікальний без жодного зайвого байта в дроті (на відміну від TLS 1.2).\n"
                    "seq входить і в тег через AAD: викинули чи переставили запис — тег не збігся, запис відкинуто.\n"
                    "Один ключ, один IV на з'єднання; уся унікальність — з лічильника.",
                    size=10.5, fill=FILL, stroke=LINE, sw=1.4))
    return render(os.path.join(OUT, "aead-record.svg"), W, H, *p)


# ── 7. Бюджет RAM на одне з'єднання й важіль max_fragment_length ──────────────
# Ідея: кількісно показати, з чого складається пам'ять на з'єднання й наскільки
# її ЗБИВАЄ домовленість про менший запис. Це поглиблює якісний mcu-costs базової
# конкретними числами: два буфери по 16 КБ + купа → ~39 КБ; MFL=4 КБ → ~15 КБ.
def fig_ram_budget():
    W, H = 800, 380
    p = []
    p.append(text(W / 2, 26, "Пам'ять на одне з'єднання: важіль меншого запису", size=15, bold=True))

    # дві стовпчикові діаграми: без важеля / з важелем
    base_y = 300           # нижня лінія стовпців
    scale = 5.4            # px на КБ
    def bar(x, label, parts):
        # parts: список (кб, підпис, колір)
        y = base_y
        for kb, sub, col in parts:
            h = kb * scale
            p.append(rect(x, y - h, 150, h, fill=col, stroke=LINE, sw=1.4))
            if h > 22:
                p.append(text(x + 75, y - h / 2 + 4, "%d КБ" % kb, size=11, color="#ffffff", bold=True))
            y -= h
        total = sum(k for k, _, _ in parts)
        p.append(line(x - 8, y, x - 8, base_y, color=MUTED, sw=1.2))
        p.append(text(x + 75, base_y + 20, label, size=11, bold=True))
        p.append(text(x + 75, base_y + 36, "разом ≈ %d КБ" % total, size=11, color=POS, bold=True))

    bar(120, "стандарт (запис 16 КБ)", [
        (16, "буфер вх.", "#c0392b"),
        (16, "буфер вих.", "#2457d6"),
        (8,  "купа handshake", "#27ae60"),
    ])
    bar(530, "MFL 4 КБ + економія", [
        (4, "буфер вх.", "#c0392b"),
        (4, "буфер вих.", "#2457d6"),
        (7, "купа handshake", "#27ae60"),
    ])
    # стрілка «важіль»
    p.append(arrow(290, 150, 520, 150, color=FIELD, sw=2.4))
    p.append(text(405, 138, "max_fragment_length", size=11, color=FIELD, bold=True))
    p.append(text(405, 168, "−24 КБ RAM", size=12, color=FIELD, bold=True))

    p.append(fitbox(50, 333, W - 100, 42,
                    "Два буфери запису домінують. Домовились про запис 4 КБ замість 16 КБ —\n"
                    "і найбільший з'їдач падає вчетверо. На чипі з 300 КБ це різниця між «влізло» і «ні».",
                    size=10.5, fill=FILL, stroke=LINE, sw=1.4))
    return render(os.path.join(OUT, "ram-budget.svg"), W, H, *p)


# ── 8. Дві площини підганяння: компіляція (config.h) vs код (conf) ────────────
# Ідея практикуму: п'ять важелів живуть на ДВОХ рівнях. Один рівень — статичний,
# у mbedtls_config.h, вирішується під час компіляції (розмір запису, які шифри й
# криві взагалі є в збірці, апаратне крипто). Другий — динамічний, у коді через
# ssl_config, вирішується під час старту (корінь довіри, режим перевірки, свій
# сертифікат). Показати, куди кожен важіль лягає і на що тисне.
def fig_tuning_planes():
    W, H = 800, 430
    p = []
    p.append(text(W / 2, 28, "П'ять важелів на двох рівнях: компіляція та код", size=15, bold=True))

    # ── рівень 1: mbedtls_config.h (компіляція) ──
    cy1 = 58
    p.append(fitbox(30, cy1, W - 60, 34, "РІВЕНЬ 1 — mbedtls_config.h  (вирішено під час компіляції: що взагалі є у прошивці)",
                    size=11.5, fill="#eef2ff", stroke=NEG, sw=1.8, bold=True))
    row1 = cy1 + 44
    cfg = [
        ("MBEDTLS_SSL_*_CONTENT_LEN\n= 4096", "RAM: буфери\nвчетверо менші", NEG),
        ("список MBEDTLS_*_C:\nлише X25519 + один AEAD", "Flash: викинуто\nзайвий код", FIELD),
        ("MBEDTLS_..._ALT\n(апаратне крипто)", "CPU: AES/ECC\nна залізо чипа", POS),
    ]
    cw = (W - 60 - 2 * 20) / 3
    for i, (k, eff, col) in enumerate(cfg):
        x = 30 + i * (cw + 20)
        p.append(fitbox(x, row1, cw, 46, k, size=10.5, fill="#f4f6f8", stroke=LINE, sw=1.5, bold=True))
        p.append(arrow(x + cw / 2, row1 + 50, x + cw / 2, row1 + 66, color=col, sw=2.0))
        p.append(fitbox(x, row1 + 68, cw, 34, eff, size=10, fill="#fff", stroke=col, sw=1.5, color=col, bold=True))

    # ── стрілка «збірка готова» ──
    midY = row1 + 118
    p.append(line(30, midY, W - 30, midY, color=MUTED, sw=1.2, dash="4 4"))
    p.append(text(W / 2, midY - 6, "↑ статично, у файлі-конфізі   ·   ↓ динамічно, у коді старту ↓", size=10, color=MUTED))

    # ── рівень 2: mbedtls_ssl_config (код) ──
    cy2 = midY + 14
    p.append(fitbox(30, cy2, W - 60, 34, "РІВЕНЬ 2 — mbedtls_ssl_config  (вирішено в коді на старті: як саме довіряти)",
                    size=11.5, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True))
    row2 = cy2 + 44
    api = [
        ("conf_ca_chain(&cacert)", "корінь довіри\nв ланцюг", FIELD),
        ("conf_authmode(\nVERIFY_REQUIRED)", "перевіряти\nсервер — обов'язково", POS),
        ("conf_own_cert(\nopaque-ключ)", "свій ключ —\nіз захищеного\nелемента", NEG),
    ]
    for i, (k, eff, col) in enumerate(api):
        x = 30 + i * (cw + 20)
        p.append(fitbox(x, row2, cw, 46, k, size=10.5, fill="#f4f6f8", stroke=LINE, sw=1.5, bold=True))
        p.append(arrow(x + cw / 2, row2 + 50, x + cw / 2, row2 + 66, color=col, sw=2.0))
        p.append(fitbox(x, row2 + 68, cw, 40, eff, size=10, fill="#fff", stroke=col, sw=1.5, color=col, bold=True))
    return render(os.path.join(OUT, "tuning-planes.svg"), W, H, *p)


# ── 9. Приватний ключ не покидає захищений елемент ───────────────────────────
# Ідея: ключ народжується й живе всередині secure element. PK-контекст лише
# ОБГОРТАЄ ручку на цей ключ. Коли TLS треба підписати транскрипт, прошивка не
# бере ключ — вона ПРОСИТЬ елемент підписати, і назад приходить лише підпис.
# Ключ фізично не має шляху назовні; дамп Flash його не містить.
def fig_opaque_key():
    W, H = 780, 320
    p = []
    p.append(text(W / 2, 28, "Приватний ключ не виходить: підписує сам захищений елемент", size=15, bold=True))

    # прошивка (ліворуч) ── secure element (праворуч)
    fx, fw = 40, 300
    sx, sw_ = W - 300 - 40, 300
    fy = 70
    p.append(fitbox(fx, fy, fw, 200, "", size=10, fill="#f8fafc", stroke=LINE, sw=1.6))
    p.append(text(fx + fw / 2, fy + 20, "прошивка (mbedTLS)", size=12, bold=True))
    p.append(fitbox(fx + 20, fy + 40, fw - 40, 40, "TLS-рукостискання\nдійшло до CertificateVerify", size=10.5,
                    fill="#eafaf0", stroke=FIELD, sw=1.5))
    p.append(fitbox(fx + 20, fy + 100, fw - 40, 40, "PK-контекст\n(лише ОБГОРТКА на ручку ключа)", size=10.5,
                    fill="#eef2ff", stroke=NEG, sw=1.5, bold=True))

    p.append(fitbox(sx, fy, sw_, 200, "", size=10, fill="#fdf2f2", stroke=POS, sw=1.8))
    p.append(text(sx + sw_ / 2, fy + 20, "захищений елемент", size=12, bold=True, color=POS))
    p.append(fitbox(sx + 20, fy + 44, sw_ - 40, 44, "приватний ключ\nнароджений і замкнений тут\n(назовні шляху немає)", size=10,
                    fill="#fff", stroke=POS, sw=1.6, color=POS, bold=True))
    p.append(fitbox(sx + 20, fy + 110, sw_ - 40, 40, "робить операцію підпису\nвсередині, ключем зі свого нутра", size=10,
                    fill="#fff", stroke=POS, sw=1.5))

    # стрілки: запит підпису → , ← лише підпис
    midx1, midx2 = fx + fw, sx
    p.append(arrow(midx1 + 4, fy + 118, midx2 - 4, fy + 118, color=INK, sw=2.2))
    p.append(text((midx1 + midx2) / 2, fy + 108, "«підпиши оце»", size=10.5, bold=True))
    p.append(arrow(midx2 - 4, fy + 150, midx1 + 4, fy + 150, color=FIELD, sw=2.2))
    p.append(text((midx1 + midx2) / 2, fy + 168, "лише підпис", size=10.5, color=FIELD, bold=True))

    p.append(fitbox(40, H - 34, W - 80, 24,
                    "Дамп Flash ключа не містить: він у елементі. Прошивка бачить лише результат підпису, не сам ключ.",
                    size=10.5, fill=FILL, stroke=LINE, sw=1.4))
    return render(os.path.join(OUT, "opaque-key.svg"), W, H, *p)


# ── 10. Сходи key schedule: три Extract, входи зліва, транскрипт-зрізи справа ──
# Ідея (для math-вставки): показати ланцюг ЧИСЛО-ЗА-ЧИСЛОМ, чого НЕ дає загальне
# дерево. Центральна вісь — три щаблі Extract; ЗЛІВА видно, що ВЛИВАЄТЬСЯ в кожен
# (PSK/0 → ECDHE → 0); між щаблями — ланка derived (сіль наступного Extract);
# СПРАВА кожна гілка Derive-Secret тягне свій ЗРІЗ транскрипту (CH..SH, CH..SF,
# CH..CF). Наголос: ECDHE входить РАЗ, довгостроковий ключ сервера — НІКОЛИ.
def fig_key_schedule_ladder():
    W, H = 860, 560
    p = []
    p.append(text(W / 2, 26, "Сходи key schedule: що вливається (зліва) і який транскрипт вплетено (справа)", size=14, bold=True))

    cx = 300                         # вісь щаблів зсунута вліво: справа місце під гілки
    nw = 224                         # ширина вузла-щабля
    nh = 52                          # висота вузла: три рядки (назва · hex · формула)
    # три щаблі Extract на осі — назва + hex-значення + HMAC-форма трьома рядками всередині рамки
    y1, y2, y3 = 74, 230, 386
    p.append(fitbox(cx - nw / 2, y1, nw, nh, "Early Secret · 33ad0a1c…\n= HMAC(0, PSK|0)", size=10.5,
                    fill=FILL, stroke=MUTED, sw=1.7, bold=True))
    p.append(fitbox(cx - nw / 2, y2, nw, nh, "Handshake Secret · 1dc826e9…\n= HMAC(dHS, ECDHE)", size=10.5,
                    fill="#eef4ff", stroke=NEG, sw=1.9, bold=True))
    p.append(fitbox(cx - nw / 2, y3, nw, nh, "Master Secret · 9e5c11b4…\n= HMAC(dMS, 0)", size=10.5,
                    fill=FILL, stroke=MUTED, sw=1.7, bold=True))

    ncx = cx - nw / 2                 # лівий край вузлів
    nrx = cx + nw / 2                 # правий край вузлів
    def ymid(y):                      # вертикальний центр вузла
        return y + nh / 2

    # входи ЗЛІВА: що є IKM кожного Extract (стрілка-стуб у лівий край вузла)
    ix, iw, ih = 30, 132, 40
    def inbox(y, s, stroke, sw, bold=False):
        yc = ymid(y)
        p.append(fitbox(ix, yc - ih / 2, iw, ih, s, size=10, fill="#f4f6f8" if stroke == MUTED else "#eafaf0",
                        stroke=stroke, sw=sw, bold=bold))
        p.append(arrow(ix + iw + 2, yc, ncx - 3, yc, color=stroke, sw=sw))
    inbox(y1, "PSK  або  0…0\n(IKM)", MUTED, 1.6)
    inbox(y2, "секрет ECDHE\n(жива випадковість)", FIELD, 2.1, bold=True)
    inbox(y3, "0…0\n(нового матеріалу нема)", MUTED, 1.6)

    # містки derived між щаблями (на осі, як salt наступного Extract).
    # Спинну стрілку РОЗРИВАЄМО навколо напису derived, щоб лінія не різала текст (svgcheck v6).
    m1c = (y1 + nh + y2) / 2
    m2c = (y2 + nh + y3) / 2
    gap = 14                               # пів-висота напису derived + запас
    p.append(line(cx, y1 + nh, cx, m1c - gap, color=LINE, sw=1.8))
    p.append(arrow(cx, m1c + gap, cx, y2, color=LINE, sw=1.8))
    p.append(line(cx, y2 + nh, cx, m2c - gap, color=LINE, sw=1.8))
    p.append(arrow(cx, m2c + gap, cx, y3, color=LINE, sw=1.8))
    p.append(textbox(cx, m1c, "derived → dHS", size=9.5,
                     fill="#fff", stroke=MUTED, sw=1.3, color=MUTED, pad=5)[0])
    p.append(textbox(cx, m2c, "derived → dMS", size=9.5,
                     fill="#fff", stroke=MUTED, sw=1.3, color=MUTED, pad=5)[0])

    # гілки СПРАВА: Derive-Secret зі своїм зрізом транскрипту.
    # Стрілки — короткі стуби від правого краю вузла до лівого краю рамки-гілки (не перетинають написи).
    bx = nrx + 44                    # ліва межа стовпця гілок
    bw = W - bx - 40
    def branch(y_box, bh, s, stroke, sw, from_y, bold=False):
        p.append(fitbox(bx, y_box, bw, bh, s, size=9.5,
                        fill="#eef4ff" if stroke == NEG else ("#eafaf0" if stroke == FIELD else FILL),
                        stroke=stroke, sw=sw, bold=bold))
        p.append(arrow(nrx + 2, from_y, bx - 3, y_box + bh / 2, color=stroke, sw=max(1.4, sw - 0.3)))

    # від Handshake Secret — hs traffic (транскрипт CH..SH)
    branch(y2 - 34, 44, "c/s hs traffic  b8b2f4a0… / 4e1f9c73…\nDerive-Secret(HS, «c|s hs traffic», CH..SH)",
           NEG, 1.6, ymid(y2))
    # від Master Secret — ap traffic (транскрипт CH..SF)
    branch(y3 - 70, 44, "c/s ap traffic  2af8e015… / 77b3c0d9…\nDerive-Secret(MS, «c|s ap traffic», CH..SF)",
           FIELD, 1.7, y3 + 6, bold=True)
    # exp master (той самий транскрипт CH..SF)
    branch(y3 - 18, 30, "exp master  0c9a4f6e…   (CH..SF)", MUTED, 1.4, ymid(y3))
    # res master (повний транскрипт CH..CF)
    branch(y3 + 20, 30, "res master  5d0e88a3…   (CH..CF — повний)", MUTED, 1.4, y3 + nh - 6)

    # фінальний крок: traffic → write_key/write_iv
    fy = y3 + 70
    p.append(arrow(bx + bw / 2, y3 + 50, bx + bw / 2, fy, color=INK, sw=1.6))
    p.append(fitbox(bx, fy, bw, 32, "Expand-Label(«key»/«iv») → write_key + write_iv", size=9.5,
                    fill="#fff", stroke=INK, sw=1.5, bold=True))

    p.append(fitbox(40, H - 58, W - 80, 44,
                    "ECDHE входить РІВНО РАЗ (щабель 2). Довгостроковий ключ сервера в дерево НЕ вливається — він лише підписав транскрипт.\n"
                    "Що пізніший щабель — то повніший вплетений транскрипт (CH..SH → CH..SF → CH..CF). Тому старий запис не відмикається навіть викраденим ключем сервера.",
                    size=10, fill=FILL, stroke=LINE, sw=1.4))
    return render(os.path.join(OUT, "key-schedule-ladder.svg"), W, H, *p)


if __name__ == "__main__":
    fig_key_schedule_ladder()
    fig_open_wire()
    fig_shared_secret()
    fig_handshake_13()
    fig_mcu_costs()
    fig_key_schedule()
    fig_aead_record()
    fig_ram_budget()
    fig_tuning_planes()
    fig_opaque_key()
    print("figures written to", OUT)
