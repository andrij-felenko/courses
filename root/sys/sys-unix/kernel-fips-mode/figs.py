# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
WARM_FILL = "#fff6e5"
GREY_FILL = "#eceff1"
RED_FILL = "#fde8e8"


# ── 1. Конвеєр завантаження ядра в режимі FIPS ──────────────────────────────
def fig_fips_boot_pipeline():
    W, H = 1420, 720
    p = []

    # Columns / Stages
    x1 = 180   # Завантажувач
    x2 = 500   # Initramfs
    x3 = 840   # Ядро: testmgr
    x4 = 1200  # Готовність або паніка

    p.append(text(x1, 70, "1. Параметри GRUB", size=14, bold=True))
    p.append(text(x2, 70, "2. Ранній простір (initramfs)", size=14, bold=True))
    p.append(text(x3, 70, "3. Ініціалізація ядра", size=14, bold=True))
    p.append(text(x4, 70, "4. Підсумковий стан", size=14, bold=True))

    # Stage 1
    fr1, w1, h1 = textbox(x1, 190, ["cmdline: «fips=1»", "boot_fips_enabled = 1"],
                          size=13, pad=12, fill=WARM_FILL, stroke=LINE, bold=True)
    p.append(fr1)

    # Stage 2
    fr2_hmac, w2_hmac, h2_hmac = textbox(x2, 190, ["Перевірка цілісності", "vmlinuz + .vmlinuz.hmac", "dracut-fips / fipscheck"],
                                         size=13, pad=13, fill=BLUE_FILL, stroke=LINE)
    p.append(fr2_hmac)
    p.append(arrow(x1 + w1/2, 190, x2 - w2_hmac/2 - 6, 190))

    fr2_fail, w2_fail, h2_fail = textbox(x2, 330, ["Невідповідність HMAC", "образ ядра пошкоджено"],
                                         size=12, pad=10, fill=RED_FILL, stroke=NEG)
    p.append(fr2_fail)
    p.append(arrow(x2, 190 + h2_hmac/2, x2, 330 - h2_fail/2 - 6, color=NEG))

    fr2_halt, w2_halt, h2_halt = textbox(x2, 450, ["Зупинка завантаження", "Emergency Shell / Stop"],
                                         size=12, pad=10, fill=RED_FILL, stroke=NEG, bold=True)
    p.append(fr2_halt)
    p.append(arrow(x2, 330 + h2_fail/2, x2, 450 - h2_halt/2 - 6, color=NEG))

    # Stage 3
    fr3_kat, w3_kat, h3_kat = textbox(x3, 190, ["Самоперевірки алгоритмів", "KAT у crypto/testmgr.c", "AES, SHA, HMAC, RSA, ECC"],
                                      size=13, pad=13, fill=BLUE_FILL, stroke=LINE)
    p.append(fr3_kat)
    p.append(arrow(x2 + w2_hmac/2, 190, x3 - w3_kat/2 - 6, 190))

    fr3_drbg, w3_drbg, h3_drbg = textbox(x3, 330, ["Генератор SP 800-90A", "Ініціалізація DRBG", "Continuous Health Tests"],
                                         size=13, pad=12, fill=BLUE_FILL, stroke=LINE)
    p.append(fr3_drbg)
    p.append(arrow(x3, 190 + h3_kat/2, x3, 330 - h3_drbg/2 - 6))

    # Stage 4
    fr4_ok, w4_ok, h4_ok = textbox(x4, 260, ["/proc/sys/crypto/fips_enabled = 1", "Заборонено: MD5, DES, RC4", "Дозволено: FIPS-approved", "Система готова до роботи"],
                                   size=13, pad=14, fill=GREEN_FILL, stroke=POS, bold=True)
    p.append(fr4_ok)
    p.append(arrow(x3 + w3_drbg/2, 330, x4 - w4_ok/2 - 6, 280, color=POS))
    p.append(arrow(x3 + w3_kat/2, 190, x4 - w4_ok/2 - 6, 240, color=POS))

    fr4_panic, w4_panic, h4_panic = textbox(x4, 450, ["Помилка KAT або DRBG", "fips_fail() -> panic()", "Ядро аварійно зупиняється"],
                                            size=12, pad=12, fill=RED_FILL, stroke=NEG, bold=True)
    p.append(fr4_panic)
    p.append(arrow(x3, 330 + h3_drbg/2, x4 - w4_panic/2 - 6, 450, color=NEG))

    p.append(text(W / 2, 595,
                  "У режимі FIPS будь-який збій цілісності бінарного образу або помилка Known Answer Test є фатальною.",
                  size=13, color=MUTED))
    p.append(text(W / 2, 625,
                  "Ядро гарантує, що жодна криптографічна операція не виконається в невалідному або скомпрометованому стані.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'fips-boot-pipeline.svg'), W, H, *p,
           title="Послідовність завантаження ядра та активація режиму FIPS")


# ── 2. Криптографічна межа ядра (Cryptographic Boundary) ───────────────────
def fig_fips_crypto_boundary():
    W, H = 1420, 720
    p = []

    # Canvas split: User Space vs Kernel Space vs Hardware
    y_user = 160
    y_kern = 390
    y_hw   = 590

    p.append(text(W / 2, 50, "Криптографічна межа FIPS (Kernel Cryptographic Module Boundary)", size=16, bold=True))

    # User space apps
    x_app1, x_app2, x_app3 = 260, 710, 1160

    fr_u1, w_u1, h_u1 = textbox(x_app1, y_user, ["OpenSSL / GnuTLS", "FIPS Provider (fips.so)", "Перевірка /proc/sys/.../fips_enabled"],
                                size=13, pad=12, fill=WARM_FILL, stroke=LINE)
    p.append(fr_u1)

    fr_u2, w_u2, h_u2 = textbox(x_app2, y_user, ["Системні демони / SSHD", "Заборона слабких шифрів", "Криптополітики: FIPS"],
                                size=13, pad=12, fill=WARM_FILL, stroke=LINE)
    p.append(fr_u2)

    fr_u3, w_u3, h_u3 = textbox(x_app3, y_user, ["Сокети AF_ALG / getrandom()", "Прямий виклик криптографії ядра", "з простору користувача"],
                                size=13, pad=12, fill=WARM_FILL, stroke=LINE)
    p.append(fr_u3)

    # Boundary line (Kernel space border)
    p.append(text(180, 265, "Системні виклики та sysfs/procfs межа", size=12, color=MUTED, italic=True))
    p.append(line(50, 280, W - 50, 280, color=LINE, sw=1.5, dash="6,6"))

    # Kernel space components
    x_k1, x_k2, x_k3, x_k4 = 230, 540, 880, 1200

    fr_k1, w_k1, h_k1 = textbox(x_k1, y_kern, ["Диспетчер Crypto API", "crypto_alloc_tfm()", "Блокування: DES, MD5, RC4"],
                                size=13, pad=12, fill=BLUE_FILL, stroke=LINE)
    p.append(fr_k1)

    fr_k2, w_k2, h_k2 = textbox(x_k2, y_kern, ["Схвалені алгоритми", "AES-XTS/GCM, SHA-2/3", "HMAC, RSA, ECDSA"],
                                size=13, pad=12, fill=GREEN_FILL, stroke=LINE, bold=True)
    p.append(fr_k2)

    fr_k3, w_k3, h_k3 = textbox(x_k3, y_kern, ["Генератор SP 800-90A", "CTR_DRBG / HMAC_DRBG", "Continuous Health Tests"],
                                size=13, pad=12, fill=GREEN_FILL, stroke=LINE, bold=True)
    p.append(fr_k3)

    fr_k4, w_k4, h_k4 = textbox(x_k4, y_kern, ["Самотестування (KAT)", "testmgr.c + testmgr.h", "Звірка еталонних векторів"],
                                size=13, pad=12, fill=BLUE_FILL, stroke=LINE)
    p.append(fr_k4)

    # Connecting arrows across boundary
    p.append(arrow(x_app1, y_user + h_u1/2, x_k1, y_kern - h_k1/2 - 6))
    p.append(arrow(x_app2, y_user + h_u2/2, x_k2, y_kern - h_k2/2 - 6))
    p.append(arrow(x_app3, y_user + h_u3/2, x_k3, y_kern - h_k3/2 - 6))

    # Hardware Layer
    p.append(line(50, 500, W - 50, 500, color=LINE, sw=1.5, dash="6,6"))
    p.append(text(180, 485, "Апаратна межа (Hardware / CPU Extensions)", size=12, color=MUTED, italic=True))

    fr_hw1, w_hw1, h_hw1 = textbox(400, y_hw, ["Апаратні інструкції CPU", "AES-NI, ARMv8 CE, SHA-NI", "Апаратні криптоприскорювачі"],
                                   size=13, pad=12, fill=GREY_FILL, stroke=LINE)
    p.append(fr_hw1)

    fr_hw2, w_hw2, h_hw2 = textbox(1020, y_hw, ["Апаратні генератори випадковості", "RDRAND / RDSEED, TPM 2.0, HWRNG", "Джерела ентропії для ядра"],
                                   size=13, pad=12, fill=GREY_FILL, stroke=LINE)
    p.append(fr_hw2)

    p.append(arrow(400, y_hw - h_hw1/2, x_k2, y_kern + h_k2/2 + 6))
    p.append(arrow(1020, y_hw - h_hw2/2, x_k3, y_kern + h_k3/2 + 6))

    render(os.path.join(IMG, 'fips-crypto-boundary.svg'), W, H, *p,
           title="Логічна та криптографічна межа FIPS модуля ядра")


# ── 3. Механізм Known Answer Tests (KAT) у testmgr ──────────────────────────
def fig_kat_execution_flow():
    W, H = 1420, 720
    p = []

    p.append(text(W / 2, 50, "Механізм Known Answer Test (KAT) під час реєстрації алгоритму", size=16, bold=True))

    # Layout nodes
    x_reg   = 180
    x_test  = 520
    x_enc   = 860
    x_eval  = 1220

    # 1. Registration
    fr_reg, w_reg, h_reg = textbox(x_reg, 240, ["crypto_register_alg()", "або завантаження модуля", "наприклад, aes-generic"],
                                   size=13, pad=12, fill=WARM_FILL, stroke=LINE)
    p.append(fr_reg)

    # 2. Test manager lookup
    fr_tm, w_tm, h_tm = textbox(x_test, 240, ["testmgr.c: пошук векторів", "Таблиці crypto/testmgr.h", "Еталони: Key, PT, CT, IV"],
                                size=13, pad=13, fill=BLUE_FILL, stroke=LINE)
    p.append(fr_tm)
    p.append(arrow(x_reg + w_reg/2, 240, x_test - w_tm/2 - 6, 240))

    # 3. Execution steps
    fr_enc, w_enc, h_enc = textbox(x_enc, 180, ["Пряме перетворення", "CT_actual = Encrypt(Key, PT)", "Звірка: CT_actual == CT_expected"],
                                   size=13, pad=12, fill=BLUE_FILL, stroke=LINE)
    p.append(fr_enc)

    fr_dec, w_dec, h_dec = textbox(x_enc, 330, ["Зворотне перетворення", "PT_actual = Decrypt(Key, CT)", "Звірка: PT_actual == PT_expected"],
                                   size=13, pad=12, fill=BLUE_FILL, stroke=LINE)
    p.append(fr_dec)

    p.append(arrow(x_test + w_tm/2, 240, x_enc - w_enc/2 - 6, 180))
    p.append(arrow(x_test + w_tm/2, 240, x_enc - w_dec/2 - 6, 330))

    # 4. Result Evaluation
    fr_ok, w_ok, h_ok = textbox(x_eval, 180, ["Усі вектори зійшлися", "selftest: passed", "Алгоритм доступний у реєстрі"],
                                size=13, pad=12, fill=GREEN_FILL, stroke=POS, bold=True)
    p.append(fr_ok)
    p.append(arrow(x_enc + w_enc/2, 180, x_eval - w_ok/2 - 6, 180, color=POS))

    fr_fail, w_fail, h_fail = textbox(x_eval, 330, ["Розбіжність результату", "fips_fail() активується", "Алгоритм блокується / panic()"],
                                      size=12, pad=12, fill=RED_FILL, stroke=NEG, bold=True)
    p.append(fr_fail)
    p.append(arrow(x_enc + w_dec/2, 330, x_eval - w_fail/2 - 6, 330, color=NEG))

    # Pairwise consistency test box below
    fr_pct, w_pct, h_pct = textbox(W / 2, 510, ["Для асиметричних ключів (RSA, ECDSA): Pairwise Consistency Test (PCT)", "Генерація пари ключів -> Підпис випадкового гешу приватним ключем -> Верифікація відкритим ключем", "У разі розбіжності пара ключів негайно знищується і не повертається застосунку"],
                                   size=13, pad=14, fill=WARM_FILL, stroke=LINE)
    p.append(fr_pct)

    p.append(text(W / 2, 630,
                  "Тестові вектори жорстко скомпільовані в образ ядра (testmgr.h) і не можуть бути модифіковані в рантаймі.",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'kat-execution-flow.svg'), W, H, *p,
           title="Послідовність виконання Known Answer Test для алгоритмів ядра")


if __name__ == '__main__':
    fig_fips_boot_pipeline()
    fig_fips_crypto_boundary()
    fig_kat_execution_flow()
    print("All figures generated successfully.")
