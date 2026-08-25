# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Палітра теми
ENC   = "#c0392b"     # небезпека / зловмисник
ENCF  = "#fdecea"
MAC   = "#2457d6"     # автентифікація / тег / MAC
MACF  = "#eaf0fd"
OK    = "#27ae60"     # безпечно / валідно
OKF   = "#eafaf0"
WARN  = "#d97706"     # попередження / вразливість
WARNF = "#fef3c7"
CLR   = "#4b5563"     # відкриті дані / повідомлення
CLRF  = "#f3f4f6"
ACC   = "#6b21a8"     # математичні операції / перетворення
ACCF  = "#f5f3ff"


# ── 1. length-extension-attack: анатомія атаки подовженням повідомлення ──
def fig_length_extension():
    W, H = 940, 460
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 28, "Атака подовженням повідомлення на Merkle-Damgard H(Key || Message)", size=16, color=INK, bold=True))

    # Секція 1: Легітимне обчислення
    p.append(rect(30, 55, 880, 165, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(50, 80, "1. Легітимне обчислення клієнтом: H(K || M)", size=13, color=INK, bold=True, anchor="start"))

    p.append(fitbox(50, 100, 110, 50, "Секрет Key\n(невідомий)", size=12, fill=ENCF, stroke=ENC, bold=True))
    p.append(fitbox(165, 100, 140, 50, "Дані M\n(api_key=...&perms=read)", size=12, fill=CLRF, stroke=CLR))
    p.append(fitbox(310, 100, 120, 50, "MD-Padding\n(\\x80\\x00...|| len)", size=12, fill=WARNF, stroke=WARN))

    p.append(arrow(435, 125, 485, 125, color=LINE, sw=1.8))

    p.append(fitbox(490, 95, 170, 60, "Компресія f(IV, ·)\n(SHA-256 / MD5)", size=12, fill=ACCF, stroke=ACC, bold=True))

    p.append(arrow(665, 125, 715, 125, color=LINE, sw=1.8))

    p.append(fitbox(720, 95, 170, 60, "Вихідний геш Tag T\n= внутрішній стан H_n", size=12, fill=MACF, stroke=MAC, bold=True))
    p.append(text(490, 185, "Кінцевий геш повідомлення є повним внутрішнім вектором стану регістрів", size=11, color=MUTED, italic=True))

    # Секція 2: Фальсифікація зловмисником
    p.append(rect(30, 245, 880, 195, fill="#ffffff", stroke=ENC, sw=1.5, rx=8))
    p.append(text(50, 270, "2. Фальсифікація активним перехоплювачем без знання ключа K", size=13, color=ENC, bold=True, anchor="start"))

    p.append(fitbox(50, 290, 190, 60, "Перехоплений Tag T\n(завантажується як IV')", size=12, fill=MACF, stroke=MAC, bold=True))
    p.append(arrow(245, 320, 295, 320, color=ENC, sw=1.8))

    p.append(fitbox(300, 290, 180, 60, "Додаткові дані M_ext\n(&perms=admin)", size=12, fill=ENCF, stroke=ENC, bold=True))
    p.append(arrow(485, 320, 535, 320, color=ENC, sw=1.8))

    p.append(fitbox(540, 290, 170, 60, "Компресія f(IV', ·)\nновий блок + pad'", size=12, fill=ACCF, stroke=ACC, bold=True))
    p.append(arrow(715, 320, 765, 320, color=ENC, sw=1.8))

    p.append(fitbox(770, 290, 125, 60, "Новий Tag T'\n(валідний!)", size=12, fill=OKF, stroke=OK, bold=True))

    p.append(text(490, 390, "Сконструйоване повідомлення M' = M || MD-Padding || M_ext успішно проходить перевірку сервером", size=12, color=ENC, bold=True))
    p.append(text(490, 415, "Сервер обчислює H(Key || M') і отримує точний збіг із T', не помічаючи підробки прав", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "length-extension-attack.svg"), W, H, *p)


# ── 2. hmac-pipeline: внутрішній та зовнішній контури HMAC ──
def fig_hmac_pipeline():
    W, H = 960, 460
    p = []

    p.append(text(W / 2, 28, "Двопрохідна криптографічна архітектура HMAC (RFC 2104)", size=16, color=INK, bold=True))

    # Секція вхідного ключа
    p.append(fitbox(40, 60, 220, 55, "Секретний ключ K\n(нормалізація до B байтів)", size=12, fill=MACF, stroke=MAC, bold=True))

    p.append(arrow(150, 115, 150, 155, color=LINE, sw=1.8))

    # Розгалуження на внутрішній і зовнішній ключі
    p.append(circle(150, 165, 8, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(arrow(150, 173, 150, 215, color=LINE, sw=1.8)) # вниз до ipad
    p.append(line(158, 165, 590, 165, color=LINE, sw=1.8))
    p.append(arrow(590, 165, 590, 215, color=LINE, sw=1.8)) # вправо і вниз до opad

    # Внутрішній контур (Inner Hash)
    p.append(rect(40, 210, 420, 230, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(250, 235, "Внутрішній контур (Inner Pass)", size=13, color=INK, bold=True))

    p.append(fitbox(60, 255, 180, 50, "K' ⊕ ipad\n(маска 0x36 repeated)", size=12, fill=WARNF, stroke=WARN, bold=True))
    p.append(fitbox(260, 255, 180, 50, "Повідомлення M\n(довільної довжини)", size=12, fill=CLRF, stroke=CLR))

    p.append(arrow(150, 305, 250, 345, color=LINE, sw=1.8))
    p.append(arrow(350, 305, 250, 345, color=LINE, sw=1.8))

    p.append(fitbox(150, 350, 200, 50, "Хеш-функція H(·)\n(SHA-256 / SHA-512)", size=12, fill=ACCF, stroke=ACC, bold=True))

    p.append(arrow(350, 375, 480, 375, color=LINE, sw=1.8))
    p.append(text(415, 365, "Дайджест inner", size=10, color=MUTED, bold=True))

    # Зовнішній контур (Outer Hash)
    p.append(rect(480, 210, 440, 230, fill="#ffffff", stroke=OK, sw=1.5, rx=8))
    p.append(text(700, 235, "Зовнішній контур (Outer Pass)", size=13, color=OK, bold=True))

    p.append(fitbox(500, 255, 180, 50, "K' ⊕ opad\n(маска 0x5c repeated)", size=12, fill=WARNF, stroke=WARN, bold=True))
    p.append(fitbox(700, 255, 200, 50, "Inner Digest (L байтів)\nH((K' ⊕ ipad) || M)", size=11, fill=MACF, stroke=MAC, bold=True))

    p.append(arrow(590, 305, 690, 345, color=LINE, sw=1.8))
    p.append(arrow(800, 305, 690, 345, color=LINE, sw=1.8))

    p.append(fitbox(590, 350, 200, 50, "Хеш-функція H(·)\n(фінальне маскування)", size=12, fill=ACCF, stroke=ACC, bold=True))

    p.append(arrow(790, 375, 830, 375, color=OK, sw=2.0))

    # Результат
    p.append(fitbox(835, 345, 75, 60, "HMAC\nTag", size=12, fill=OKF, stroke=OK, bold=True))

    # Пояснення захисту
    p.append(fitbox(340, 60, 580, 55, "Захист від Length Extension: вихід внутрішнього гешу загорнуто у зовнішній контур під іншим ключем (K' ⊕ opad). Зловмисник не знає виходу зовнішнього гешу для додавання блоків.", size=11, fill=OKF, stroke=OK))

    render(os.path.join(OUT, "hmac-pipeline.svg"), W, H, *p)


# ── 3. cmac-subkeys-pipeline: структура CMAC (NIST SP 800-38B) ──
def fig_cmac_pipeline():
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 28, "Блоковий код автентичності CMAC (OMAC1) на базі AES", size=16, color=INK, bold=True))

    # Верхня частина: генерація підключів K1 та K2
    p.append(rect(30, 55, 900, 115, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    p.append(text(50, 78, "Генерація підключів K1 та K2 у полі GF(2¹²⁸)", size=12, color=INK, bold=True, anchor="start"))

    p.append(fitbox(50, 95, 110, 45, "AES_K(0¹²⁸)", size=11, fill=CLRF, stroke=CLR, bold=True))
    p.append(arrow(160, 117, 200, 117, color=LINE, sw=1.5))

    p.append(fitbox(205, 95, 110, 45, "Базовий L\n(16 байтів)", size=11, fill=ACCF, stroke=ACC, bold=True))
    p.append(arrow(315, 117, 355, 117, color=LINE, sw=1.5))

    p.append(fitbox(360, 90, 250, 55, "K1 = (L << 1) ⊕ (msb ? 0x87 : 0)\n(для повного фінального блока)", size=11, fill=MACF, stroke=MAC, bold=True))
    p.append(arrow(610, 117, 650, 117, color=LINE, sw=1.5))

    p.append(fitbox(655, 90, 260, 55, "K2 = (K1 << 1) ⊕ (msb ? 0x87 : 0)\n(для неповного блока з pad 10...0)", size=11, fill=WARNF, stroke=WARN, bold=True))

    # Нижня частина: конвеєр обробки блоків
    p.append(rect(30, 185, 900, 275, fill="#ffffff", stroke=OK, sw=1.5, rx=8))
    p.append(text(50, 210, "Конвеєр обчислення MAC: поблокове зчеплення та диференціація фіналу", size=12, color=OK, bold=True, anchor="start"))

    # Блок 1
    p.append(fitbox(50, 230, 110, 40, "Блок M₁", size=11, fill=CLRF, stroke=CLR, bold=True))
    p.append(arrow(105, 270, 105, 300, color=LINE, sw=1.5))

    p.append(circle(105, 310, 10, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(105, 314, "⊕", size=14, bold=True))
    p.append(text(50, 314, "IV = 0", size=11, color=MUTED))
    p.append(arrow(75, 310, 95, 310, color=MUTED, sw=1.2))

    p.append(arrow(105, 320, 105, 350, color=LINE, sw=1.5))
    p.append(fitbox(55, 350, 100, 40, "AES_K", size=11, fill=ACCF, stroke=ACC, bold=True))
    p.append(arrow(155, 370, 240, 310, color=LINE, sw=1.5))

    # Блок 2
    p.append(fitbox(200, 230, 110, 40, "Блок M₂", size=11, fill=CLRF, stroke=CLR, bold=True))
    p.append(arrow(255, 270, 255, 300, color=LINE, sw=1.5))

    p.append(circle(255, 310, 10, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(255, 314, "⊕", size=14, bold=True))

    p.append(arrow(255, 320, 255, 350, color=LINE, sw=1.5))
    p.append(fitbox(205, 350, 100, 40, "AES_K", size=11, fill=ACCF, stroke=ACC, bold=True))

    # Пунктир до кінця
    p.append(line(310, 370, 430, 370, color=MUTED, sw=1.5, dash="4,4"))
    p.append(arrow(430, 370, 480, 310, color=LINE, sw=1.5))

    # Фінальний блок (розгалуження)
    p.append(fitbox(440, 230, 110, 40, "Блок M_n", size=11, fill=CLRF, stroke=CLR, bold=True))
    p.append(arrow(495, 270, 495, 300, color=LINE, sw=1.5))

    p.append(circle(495, 310, 10, fill="#ffffff", stroke=LINE, sw=1.5))
    p.append(text(495, 314, "⊕", size=14, bold=True))

    p.append(arrow(495, 320, 495, 350, color=LINE, sw=1.5))

    # Додатковий XOR з K1 або K2
    p.append(fitbox(560, 275, 200, 60, "Якщо блок повний: ⊕ K1\nЯкщо неповний: ⊕ K2 (pad 10*0)", size=11, fill=WARNF, stroke=WARN, bold=True))
    p.append(arrow(560, 305, 505, 310, color=WARN, sw=1.5))

    p.append(fitbox(445, 350, 100, 40, "AES_K", size=11, fill=ACCF, stroke=ACC, bold=True))
    p.append(arrow(545, 370, 620, 370, color=OK, sw=2.0))

    p.append(fitbox(625, 345, 140, 50, "CMAC Tag T\n(Tlen ≤ 128 біт)", size=12, fill=OKF, stroke=OK, bold=True))

    p.append(text(500, 435, "Захист від атак варіювання довжини: підключі K1 та K2 діють як розділювачі доменів", size=11, color=OK, bold=True))

    render(os.path.join(OUT, "cmac-subkeys-pipeline.svg"), W, H, *p)


# ── 4. timing-attack-early-exit: побайтове memcmp проти constant-time ──
def fig_timing_attack():
    W, H = 940, 460
    p = []

    p.append(text(W / 2, 28, "Атака за часом (Timing Attack) на побайтове порівняння токенів", size=16, color=INK, bold=True))

    # Ліва колонка: вразливий memcmp / ==
    p.append(rect(30, 55, 425, 380, fill="#ffffff", stroke=ENC, sw=1.5, rx=8))
    p.append(text(242, 80, "ВРАЗЛИВО: memcmp() / == (ранній вихід)", size=13, color=ENC, bold=True))

    p.append(fitbox(50, 105, 385, 60, "Еталонний MAC: [ 0x7F, 0xA2, 0x3C, 0xD4, ... ]\nПідібраний MAC: [ 0x10, 0x00, 0x00, 0x00, ... ]", size=11, fill=CLRF, stroke=CLR))

    p.append(fitbox(50, 175, 385, 45, "Спроба 1: Байт 0 не збігся (0x10 != 0x7F)\n-> Ранній вихід: час відповіді ~ 5 нс", size=11, fill=ENCF, stroke=ENC))

    p.append(fitbox(50, 230, 385, 45, "Спроба 128: Байт 0 збігся (0x7F == 0x7F), байт 1 ні\n-> Ранній вихід на байті 1: час ~ 10 нс", size=11, fill=WARNF, stroke=WARN))

    p.append(fitbox(50, 285, 385, 45, "Спроба N: Перші k байтів збіглися\n-> Час відповіді зростає лінійно: ~ (k+1) · 5 нс", size=11, fill=ENCF, stroke=ENC))

    p.append(fitbox(50, 345, 385, 75, "Результат атаки:\nЗловмисник вгадує таємний MAC байт за байтом!\nСкладність: 32 × 256 = 8 192 запитів\nзамість повного перебору 2²⁵⁶.", size=11, fill=ENCF, stroke=ENC, bold=True))

    # Права колонка: безпечний constant-time compare
    p.append(rect(485, 55, 425, 380, fill="#ffffff", stroke=OK, sw=1.5, rx=8))
    p.append(text(697, 80, "БЕЗПЕЧНО: Constant-Time Comparison", size=13, color=OK, bold=True))

    p.append(fitbox(505, 105, 385, 60, "volatile uint8_t diff = 0;\nfor (size_t i = 0; i < len; ++i)\n    diff |= a[i] ^ b[i];\nreturn diff == 0;", size=11, fill=CLRF, stroke=CLR, bold=True))

    p.append(fitbox(505, 175, 385, 45, "Спроба 1: Байт 0 не збігся\n-> Перевіряються всі 32 байти: час ~ 60 нс", size=11, fill=OKF, stroke=OK))

    p.append(fitbox(505, 230, 385, 45, "Спроба 128: Байт 0 збігся, байт 1 ні\n-> Перевіряються всі 32 байти: час ~ 60 нс", size=11, fill=OKF, stroke=OK))

    p.append(fitbox(505, 285, 385, 45, "Спроба N: Перші 31 байтів збіглися\n-> Перевіряються всі 32 байти: час ~ 60 нс", size=11, fill=OKF, stroke=OK))

    p.append(fitbox(505, 345, 385, 75, "Результат захисту:\nЧас виконання повністю незалежний від даних.\nЖодного витоку через часовий канал (side-channel).\nСкладність злому залишається 2²⁵⁶.", size=11, fill=OKF, stroke=OK, bold=True))

    render(os.path.join(OUT, "timing-attack-early-exit.svg"), W, H, *p)


if __name__ == "__main__":
    fig_length_extension()
    fig_hmac_pipeline()
    fig_cmac_pipeline()
    fig_timing_attack()
    print("All figures generated successfully.")
