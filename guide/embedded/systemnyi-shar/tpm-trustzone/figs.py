# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Ланцюг довіри: незмінний корінь у кремнії перевіряє наступну ланку ──────
# Ідея: довіра не з повітря — вона спирається на ROM, який фізично не можна
# переписати. Кожна ланка ПЕРЕВІРЯЄ підпис наступної перш ніж віддати їй владу;
# не зійшовся підпис — стоп, далі не йдемо.
def fig_chain_of_trust():
    W, H = 760, 300
    p = []
    p.append(text(W / 2, 30, "Ланцюг довіри: кожна ланка перевіряє наступну", size=16, bold=True))

    stages = [
        ("ROM\n(корінь у кремнії)", "#eafaf0", FIELD, "незмінний"),
        ("Завантажувач", FILL, LINE, "перевірено"),
        ("Прошивка", FILL, LINE, "перевірено"),
    ]
    bx, by, bw, bh, gap = 60, 90, 180, 70, 70
    cx = []
    for i, (lab, fill, stroke, tag) in enumerate(stages):
        x = bx + i * (bw + gap)
        p.append(fitbox(x, by, bw, bh, lab, size=13, fill=fill, stroke=stroke, sw=2.0, bold=True))
        p.append(text(x + bw / 2, by - 12, tag, size=11, color=(FIELD if i == 0 else MUTED)))
        cx.append(x + bw / 2)
        if i < len(stages) - 1:
            ax1 = x + bw
            ax2 = x + bw + gap
            p.append(arrow(ax1 + 4, by + bh / 2, ax2 - 4, by + bh / 2, color=NEG, sw=2.0))
            p.append(text((ax1 + ax2) / 2, by + bh / 2 - 12, "перевір\nпідпис", size=10, color=NEG))

    # зрив ланцюга — якщо підпис не зійшовся
    p.append(text(cx[1], by + bh + 46, "✗ не зійшовся підпис → стоп, далі не йдемо",
                  size=12, color=POS, bold=True))
    # підкреслення кореня
    p.append(text(cx[0], by + bh + 28, "довіряємо «за визначенням»", size=10, color=FIELD))
    return render(os.path.join(OUT, "chain-of-trust.svg"), W, H, *p)


# ── 2. Дві стратегії ізоляції: TrustZone (один кристал, біт NS) vs TPM (окремий чип)
# Ідея: захистити секрет можна двома різними способами. TrustZone ділить ОДИН
# процесор на два світи бітом на шині. TPM — це ОКРЕМА мікросхема на шині, в яку
# секрет узагалі ніколи не виходить.
def fig_two_isolations():
    W, H = 780, 380
    p = []
    p.append(text(W / 2, 30, "Дві стратегії: розділити кристал чи винести в окремий чип", size=15, bold=True))

    # ── ЛІВОРУЧ: TrustZone — один SoC, дві зони ──
    lx, ly, lw, lh = 40, 70, 320, 250
    p.append(rect(lx, ly, lw, lh, fill="#fcfcfd", stroke=LINE, sw=1.5))
    p.append(text(lx + lw / 2, ly + 24, "TrustZone — один процесор", size=13, color=NEG, bold=True))
    # нормальний світ
    p.append(fitbox(lx + 20, ly + 44, lw - 40, 78,
                    "НОРМАЛЬНИЙ світ\nдодаток, мережа, UI\n(тут весь складний код)",
                    size=11, fill="#eef2fb", stroke=NEG, sw=1.6))
    # межа з бітом NS
    midy = ly + 44 + 78 + 12
    p.append(line(lx + 20, midy, lx + lw - 20, midy, color=POS, sw=2.4, dash="6 4"))
    p.append(text(lx + lw / 2, midy - 6, "межа стереже біт NS на кожній транзакції", size=9, color=POS))
    # безпечний світ
    p.append(fitbox(lx + 20, midy + 10, lw - 40, 70,
                    "БЕЗПЕЧНИЙ світ\nключі, крипто\n(малий, перевірений код)",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True))
    p.append(text(lx + lw / 2, ly + lh - 10, "секрет не покидає кристал", size=10, color=MUTED))

    # ── ПРАВОРУЧ: TPM — головний процесор + окремий чип ──
    rx, ry, rw, rh = 420, 70, 320, 250
    p.append(rect(rx, ry, rw, rh, fill="#fcfcfd", stroke=LINE, sw=1.5))
    p.append(text(rx + rw / 2, ry + 24, "TPM — окрема мікросхема", size=13, color=FIELD, bold=True))
    # головний процесор
    p.append(fitbox(rx + 20, ry + 44, rw - 40, 70,
                    "Головний процесор\nуся система, будь-який код\n(може бути зламаний)",
                    size=11, fill="#eef2fb", stroke=NEG, sw=1.6))
    # шина
    busx1, busx2 = rx + rw / 2, rx + rw / 2
    p.append(arrow(rx + rw / 2, ry + 44 + 70 + 2, rx + rw / 2, ry + 44 + 70 + 34, color=LINE, sw=2.0))
    p.append(arrow(rx + rw / 2, ry + 44 + 70 + 36, rx + rw / 2, ry + 44 + 70 + 4, color=LINE, sw=2.0))
    p.append(text(rx + rw / 2 + 64, ry + 44 + 70 + 22, "команди по шині", size=9, color=MUTED))
    # TPM-чип
    p.append(fitbox(rx + 40, ry + 44 + 70 + 44, rw - 80, 70,
                    "TPM\nключі всередині назавжди\nрахує крипто за нас",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True))
    p.append(text(rx + rw / 2, ry + rh - 10, "секрет фізично в іншому корпусі", size=10, color=MUTED))

    return render(os.path.join(OUT, "two-isolations.svg"), W, H, *p)


# ── 3. PCR-розширення: одностороння драбина хешів ─────────────────────────────
# Ідея: значення регістра НЕ можна записати напряму — лише «розширити»:
# нове = Hash(старе ‖ вимір). Це драбина в один бік: підкинеш чужий вимір — і
# далі котиться зовсім інше число, підмінити «заднім числом» уже годі.
def fig_pcr_extend():
    W, H = 780, 330
    p = []
    p.append(text(W / 2, 30, "PCR-розширення: драбина хешів в один бік", size=16, bold=True))
    p.append(text(W / 2, 54, "нове значення = Hash( старе значення ‖ новий вимір )", size=12, color=MUTED))

    y = 150
    boxes = ["0…0", "H₁", "H₂", "H₃"]
    meas = ["вимір A", "вимір B", "вимір C"]
    bx, bw, gap = 50, 120, 80
    for i, val in enumerate(boxes):
        x = bx + i * (bw + gap)
        fill = "#eafaf0" if i == 0 else FILL
        p.append(rect(x, y, bw, 56, fill=fill, stroke=(FIELD if i == 0 else LINE), sw=2.0))
        p.append(text(x + bw / 2, y + 34, val, size=16, bold=True))
        p.append(text(x + bw / 2, y - 14, ("старт = нулі" if i == 0 else "PCR"), size=10, color=MUTED))
        if i < len(boxes) - 1:
            ax1, ax2 = x + bw, x + bw + gap
            p.append(arrow(ax1 + 4, y + 28, ax2 - 4, y + 28, color=NEG, sw=2.0))
            p.append(text((ax1 + ax2) / 2, y - 4, "Hash", size=11, color=NEG, bold=True))
            p.append(text((ax1 + ax2) / 2, y + 56, meas[i], size=10, color=INK))

    p.append(fitbox(50, y + 96, W - 100, 56,
                    "Підкинеш чужий вимір замість виміру B — далі покотиться зовсім інше число. "
                    "Назад драбину не відмотати: «правильний» хеш заднім числом уже не підставиш.",
                    size=12, fill="#fdecea", stroke=POS, sw=1.6))
    return render(os.path.join(OUT, "pcr-extend.svg"), W, H, *p)


# ── 4. Вимірюваний запуск + віддалене засвідчення ─────────────────────────────
# Ідея: кожна стадія МІРЯЄ наступну (хеш→розширення PCR) перш ніж дати їй владу.
# Перевіряч надсилає одноразове число (nonce), пристрій повертає ПІДПИСАНИЙ
# знімок PCR — «ось що в мене реально запустилося». Підпис + nonce = не підробиш.
def fig_measured_attestation():
    W, H = 800, 360
    p = []
    p.append(text(W / 2, 28, "Вимірюваний запуск і віддалене засвідчення", size=16, bold=True))

    # ліворуч — стадії запуску міряють у PCR
    sx = 50
    stages = ["ROM", "завантажувач", "прошивка"]
    sy, sh = 70, 44
    for i, st in enumerate(stages):
        yy = sy + i * (sh + 16)
        p.append(fitbox(sx, yy, 150, sh, st, size=12, fill=("#eafaf0" if i == 0 else FILL),
                        stroke=(FIELD if i == 0 else LINE), sw=1.8, bold=(i == 0)))
        p.append(arrow(sx + 150 + 4, yy + sh / 2, sx + 230, yy + sh / 2, color=NEG, sw=1.8))
        p.append(text(sx + 150 + 44, yy + sh / 2 - 9, "міряє", size=9, color=NEG))

    # сховище PCR
    px = sx + 240
    p.append(rect(px, sy, 130, sh * 3 + 32, fill="#eef2fb", stroke=NEG, sw=2.0))
    p.append(text(px + 65, sy + 22, "PCR", size=14, bold=True, color=NEG))
    p.append(text(px + 65, sy + 44, "знімок того,", size=10, color=INK))
    p.append(text(px + 65, sy + 60, "що запустилось", size=10, color=INK))
    p.append(text(px + 65, sy + 92, "не підмінити", size=10, color=POS))
    p.append(text(px + 65, sy + 108, "заднім числом", size=10, color=POS))

    # праворуч — перевіряч
    vx = px + 200
    p.append(fitbox(vx, sy + 10, 170, 70, "Перевіряч\n(сервер у полі)", size=12,
                    fill=FILL, stroke=LINE, sw=1.8, bold=True))
    # nonce туди
    p.append(arrow(vx - 4, sy + 30, px + 132, sy + 30, color=LINE, sw=1.8))
    p.append(text((px + 132 + vx) / 2, sy + 20, "1) nonce", size=10, color=INK))
    # підписаний quote назад
    p.append(arrow(px + 132, sy + 64, vx - 4, sy + 64, color=FIELD, sw=2.2))
    p.append(text((px + 132 + vx) / 2, sy + 80, "2) підписаний", size=10, color=FIELD, bold=True))
    p.append(text((px + 132 + vx) / 2, sy + 94, "знімок", size=10, color=FIELD, bold=True))

    p.append(fitbox(50, 250, W - 100, 80,
                    "Кожна стадія міряє наступну (хеш → розширення PCR) ПЕРШ ніж дати їй владу. "
                    "Перевіряч шле одноразове число (nonce) — пристрій повертає знімок PCR, підписаний "
                    "ключем зсередини. Підпис доводить «це справді ця залізяка», nonce — «відповідь свіжа, "
                    "не запис старої».", size=12, fill="#eafaf0", stroke=FIELD, sw=1.6))
    return render(os.path.join(OUT, "measured-attestation.svg"), W, H, *p)


# ── 5. eFuse: дорога в один бік (для вставки proj-esp32-secure-boot) ───────────
# Ідея: біт eFuse можна пропалити РІВНО раз. 0→1 — назавжди; назад дороги нема.
# Тому послідовність увімкнення захисту — це сходи вниз без поручнів: кожен крок
# відрізає шлях назад. Помилився з ключем — лишився на чипі назавжди.
def fig_efuse_oneway():
    W, H = 780, 360
    p = []
    p.append(text(W / 2, 30, "eFuse: кожен крок — двері, що замикаються за тобою", size=15, bold=True))

    steps = [
        ("Чистий чип", "ще все можна: прошити, стерти, перепрошити будь-чим", "#eafaf0", FIELD),
        ("Пропалено відбиток ключа\n(BLOCK2)", "тепер чип прийме лише образ, підписаний ТВОЇМ ключем", FILL, LINE),
        ("Увімкнено Secure Boot\n(ABS_DONE_1)", "ROM відтепер перевіряє підпис; чужий код не запуститься", FILL, LINE),
        ("Release-режим шифрування\n(DISABLE_DL_*)", "UART більше не зчитає й не зашифрує Flash; лише OTA", "#fdecea", POS),
    ]
    x = 60
    y0 = 70
    bw, bh, vgap = 300, 56, 18
    for i, (lab, sub, fill, stroke) in enumerate(steps):
        y = y0 + i * (bh + vgap)
        p.append(fitbox(x, y, bw, bh, lab, size=12, fill=fill, stroke=stroke, sw=2.0, bold=True))
        p.append(text(x + bw + 14, y + bh / 2 - 1, sub, size=10.5, color=MUTED, anchor="start"))
        if i < len(steps) - 1:
            ax = x + bw / 2
            p.append(arrow(ax, y + bh + 2, ax, y + bh + vgap - 2, color=NEG, sw=2.0))

    # вертикальна стрілка «назад не можна»
    p.append(line(x - 28, y0 + 6, x - 28, y0 + 3 * (bh + vgap) + bh - 6, color=POS, sw=2.2, dash="2 6"))
    p.append(text(x - 40, (y0 + y0 + 3 * (bh + vgap) + bh) / 2, "назад дороги нема", size=11,
                  color=POS, bold=True, anchor="middle"))
    return render(os.path.join(OUT, "efuse-oneway.svg"), W, H, *p)


# ── 6. Робочий конвеєр: ключ → підпис → пропал → ланцюг (для proj-вставки) ─────
# Ідея: показати, ХТО що робить. На хості (раз!) родиться ключ. Образи
# підписуються на хості. На чипі — РАЗ пропалюється відбиток і прапорець. А далі
# щоразу при старті ROM→завантажувач→додаток звіряють підпис тим відбитком.
def fig_secureboot_pipeline():
    W, H = 800, 380
    p = []
    p.append(text(W / 2, 28, "Конвеєр захищеного завантаження на ESP32", size=16, bold=True))

    # ── смуга «на хості» ──
    hx, hy, hw, hh = 40, 56, 720, 120
    p.append(rect(hx, hy, hw, hh, fill="#fcfcfd", stroke=LINE, sw=1.4))
    p.append(text(hx + 14, hy + 20, "На хості (комп'ютер розробника)", size=12, color=NEG, bold=True, anchor="start"))
    p.append(fitbox(hx + 20, hy + 32, 210, 70,
                    "1) генеруємо КЛЮЧ\nRSA-3072 (приватний)\nраз і назавжди → у сейф",
                    size=11, fill="#eafaf0", stroke=FIELD, sw=1.8, bold=True))
    p.append(arrow(hx + 20 + 210 + 6, hy + 67, hx + 20 + 250, hy + 67, color=NEG, sw=1.8))
    p.append(fitbox(hx + 280, hy + 32, 210, 70,
                    "2) ПІДПИСУЄМО образи\nзавантажувач + додаток\nприватним ключем",
                    size=11, fill=FILL, stroke=LINE, sw=1.6))
    p.append(arrow(hx + 280 + 210 + 6, hy + 67, hx + 280 + 250, hy + 67, color=NEG, sw=1.8))
    p.append(fitbox(hx + 540, hy + 32, 160, 70,
                    "3) дістаємо ВІДБИТОК\n(SHA-256 відкритого\nключа)",
                    size=11, fill=FILL, stroke=LINE, sw=1.6))

    # стрілка вниз: відбиток → у чип (раз)
    p.append(arrow(hx + 540 + 80, hy + hh + 2, hx + 540 + 80, hy + hh + 34, color=POS, sw=2.4))
    p.append(text(hx + 540 + 80 + 96, hy + hh + 20, "пропалити РАЗ", size=10.5, color=POS, bold=True))

    # ── смуга «у чипі назавжди» ──
    cx, cy, cw, ch = 40, hy + hh + 40, 720, 70
    p.append(rect(cx, cy, cw, ch, fill="#fff7f5", stroke=POS, sw=1.6))
    p.append(text(cx + 14, cy + 20, "У чипі — НЕЗВОРОТНО (eFuse)", size=12, color=POS, bold=True, anchor="start"))
    p.append(fitbox(cx + 230, cy + 28, 300, 34,
                    "відбиток у BLOCK2  +  біт «Secure Boot увімкнено» (ABS_DONE_1)",
                    size=11, fill="#fdecea", stroke=POS, sw=1.6, bold=True))

    # ── смуга «щоразу при старті» ──
    bx, by, bbw, bbh = 40, cy + ch + 30, 720, 64
    p.append(rect(bx, by, bbw, bbh, fill="#fcfcfd", stroke=LINE, sw=1.4))
    p.append(text(bx + 14, by + 18, "Щоразу при ввімкненні живлення", size=12, color=INK, bold=True, anchor="start"))
    chain = ["ROM", "завантажувач", "додаток"]
    sxx, syy, sbw, sbh, sgap = bx + 40, by + 26, 150, 30, 80
    for i, st in enumerate(chain):
        xx = sxx + i * (sbw + sgap)
        p.append(fitbox(xx, syy, sbw, sbh, st, size=12,
                        fill=("#eafaf0" if i == 0 else FILL),
                        stroke=(FIELD if i == 0 else LINE), sw=1.7, bold=(i == 0)))
        if i < len(chain) - 1:
            p.append(arrow(xx + sbw + 4, syy + sbh / 2, xx + sbw + sgap - 4, syy + sbh / 2, color=NEG, sw=1.8))
            p.append(text(xx + sbw + sgap / 2, syy + sbh / 2 - 7, "звір\nпідпис", size=9, color=NEG))
    return render(os.path.join(OUT, "secureboot-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_chain_of_trust()
    fig_two_isolations()
    fig_pcr_extend()
    fig_measured_attestation()
    fig_efuse_oneway()
    fig_secureboot_pipeline()
    print("figures written to", OUT)
