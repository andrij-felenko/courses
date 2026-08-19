# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to reach scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def box_at(cx, cy, s, **kw):
    """textbox по центру, повертає (svg, півширина, піввисота)."""
    body, w, h = textbox(cx, cy, s, **kw)
    return body, w / 2, h / 2


# ── Фігура 1: Чотири вектори атак на незахищений вебхук ───────────────────────
def fig_attack_vectors():
    W, H = 1000, 560
    p = []
    p.append(text(W / 2, 32, "Вектори атак на відкритий вебхук-ендпоінт", size=18, bold=True))

    # Центральний вузол: Сервер-споживач
    cx, cy = 680, 290
    server_box, sw, sh = box_at(cx, cy, "Сервер споживача\nPOST /api/webhooks\n(Публічна URL-адреса)",
                                size=13, bold=True, fill="#f8fafc", stroke=INK, min_w=200, pad=12)
    p.append(server_box)

    # 1. Спуфінг джерела
    y1 = 100
    b1, w1, h1 = box_at(220, y1, "1. Спуфінг джерела (Source Spoofing)\nЗловмисник шле вигадану подію\n«payment.succeeded» на публічний URL",
                        size=12, fill="#fdecea", stroke=POS, min_w=360)
    p.append(b1)
    p.append(arrow(220 + w1, y1, cx - sw, cy - 60, color=POS, sw=1.8))
    p.append(text(460, y1 + 35, "Фальшиве тіло без секрету", size=11, color=POS, bold=True))

    # 2. Підробка тіла запиту
    y2 = 220
    b2, w2, h2 = box_at(220, y2, "2. Підробка тіла (Payload Tampering)\nПерехоплення та зміна суми\nабо account_id під час передачі",
                        size=12, fill="#fdecea", stroke=POS, min_w=360)
    p.append(b2)
    p.append(arrow(220 + w2, y2, cx - sw, cy - 15, color=POS, sw=1.8))
    p.append(text(460, y2 + 10, "Модифікований JSON", size=11, color=POS, bold=True))

    # 3. Атака повторного відтворення
    y3 = 350
    b3, w3, h3 = box_at(220, y3, "3. Атака повторення (Replay Attack)\nПерехоплення справжнього запиту\nі повторне надсилання десятки разів",
                        size=12, fill="#fdecea", stroke=POS, min_w=360)
    p.append(b3)
    p.append(arrow(220 + w3, y3, cx - sw, cy + 25, color=POS, sw=1.8))
    p.append(text(460, y3 + 5, "Повтор старого виклику", size=11, color=POS, bold=True))

    # 4. Таймінг-атака
    y4 = 480
    b4, w4, h4 = box_at(220, y4, "4. Таймінг-атака (Timing Attack)\nПобайтовий підбір підпису через різницю\nв часі обриву небезпечного strcmp",
                        size=12, fill="#fdecea", stroke=POS, min_w=360)
    p.append(b4)
    p.append(arrow(220 + w4, y4, cx - sw, cy + 70, color=POS, sw=1.8))
    p.append(text(460, y4 - 15, "Вимірювання затримки відповіді", size=11, color=POS, bold=True))

    # Наслідок на сервері
    rx = 900
    res_box, _, _ = box_at(rx, cy, "Наслідки без захисту:\n• Відвантаження без оплати\n• Подвійне нарахування\n• Злам автентифікації",
                           size=11, fill="#fff5f5", stroke=POS, min_w=170, pad=10)
    p.append(res_box)
    p.append(arrow(cx + sw, cy, rx - 85, cy, color=POS, sw=1.8))

    render(os.path.join(IMG, "attack-vectors.svg"), W, H, *p)


# ── Фігура 2: Структура та обчислення HMAC-SHA256 ──────────────────────────────
def fig_hmac_construction():
    W, H = 1000, 520
    p = []
    p.append(text(W / 2, 30, "Будова HMAC-SHA256 (RFC 2104)", size=18, bold=True))

    # Ключ K
    b_key, kw, kh = box_at(120, 110, "Спільний секрет K\n(байти ключа)", size=12, bold=True,
                           fill="#eaf0fd", stroke=NEG, min_w=150)
    p.append(b_key)

    # Нормалізація ключа K'
    b_kprime, kpw, kph = box_at(320, 110, "K' (64 байти)\n(padding нулями\nабо SHA256 якщо > 64)",
                                size=11, fill="#f4f6f8", stroke=LINE, min_w=160)
    p.append(b_kprime)
    p.append(arrow(120 + kw, 110, 320 - kpw, 110, sw=1.5))

    # Розгалуження на внутрішній і зовнішній XOR
    p.append(arrow(320, 110 + kph, 320, 200, sw=1.5))
    p.append(arrow(320, 200, 180, 240, sw=1.5))
    p.append(arrow(320, 200, 680, 240, sw=1.5))

    # Внутрішня гілка (Inner Hash)
    b_ipad, iw, ih = box_at(180, 270, "K' ⊕ ipad\n(ipad = 0x36...)", size=12, bold=True,
                            fill="#eaf7ef", stroke=FIELD, min_w=140)
    p.append(b_ipad)

    b_msg, mw, mh = box_at(380, 270, "Сире тіло запиту (M)\n(Raw Bytes)", size=12, bold=True,
                           fill="#fef3c7", stroke="#d97706", min_w=160)
    p.append(b_msg)

    # Конкатенація і внутрішній хеш
    b_inner_hash, inw, inh = box_at(280, 380, "Внутрішній SHA-256\nHASH( (K' ⊕ ipad) || M )\n→ 32 байти внутрішнього дайджесту",
                                    size=12, bold=True, fill="#eaf0fd", stroke=NEG, min_w=300)
    p.append(b_inner_hash)
    p.append(arrow(180, 270 + ih, 240, 380 - inh, sw=1.5))
    p.append(arrow(380, 270 + mh, 320, 380 - inh, sw=1.5))

    # Зовнішня гілка (Outer Hash)
    b_opad, ow, oh = box_at(680, 270, "K' ⊕ opad\n(opad = 0x5C...)", size=12, bold=True,
                            fill="#eaf7ef", stroke=FIELD, min_w=140)
    p.append(b_opad)

    # Зовнішній SHA-256
    b_outer_hash, outw, outh = box_at(680, 380, "Зовнішній SHA-256\nHASH( (K' ⊕ opad) || Inner_Hash )\n→ 32 байти HMAC",
                                     size=12, bold=True, fill="#eaf0fd", stroke=NEG, min_w=300)
    p.append(b_outer_hash)
    p.append(arrow(680, 270 + oh, 680, 380 - outh, sw=1.5))
    p.append(arrow(280 + inw, 380, 680 - outw, 380, color=FIELD, sw=2))

    # Результат: Підпис
    b_sig, sigw, sigh = box_at(680, 475, "HMAC-SHA256 Підпис (HEX або Base64)\nПередається у заголовку X-Hub-Signature-256 або Stripe-Signature",
                               size=12, bold=True, fill="#eaf7ef", stroke=FIELD, min_w=480)
    p.append(b_sig)
    p.append(arrow(680, 380 + outh, 680, 475 - sigh, color=FIELD, sw=2))

    render(os.path.join(IMG, "hmac-construction.svg"), W, H, *p)


# ── Фігура 3: Часове вікно та захист від Replay ────────────────────────────────
def fig_replay_window():
    W, H = 1000, 480
    p = []
    p.append(text(W / 2, 32, "Часове вікно (Time-Window) та дедуплікація Replay", size=18, bold=True))

    # Часова вісь
    y_axis = 220
    p.append(line(80, y_axis, 920, y_axis, color=INK, sw=2.5))
    p.append(arrow(915, y_axis, 940, y_axis, color=INK, sw=2.5))
    p.append(text(935, y_axis + 25, "Час (t)", size=12, bold=True))

    # Поточний час сервера T_now
    x_now = 500
    p.append(line(x_now, 90, x_now, 350, color=NEG, sw=2, dash="4 4"))
    b_now, nw, nh = box_at(x_now, 75, "Поточний час сервера (T_now)", size=12, bold=True,
                           fill="#eaf0fd", stroke=NEG, min_w=200)
    p.append(b_now)

    # Межі вікна валідності [T_now - Δt, T_now + Δt]
    x_min = 280
    x_max = 720
    p.append(line(x_min, 120, x_min, 330, color=FIELD, sw=1.8, dash="5 5"))
    p.append(line(x_max, 120, x_max, 330, color=FIELD, sw=1.8, dash="5 5"))

    # Позначення меж
    p.append(text(x_min, y_axis + 22, "T_now − Δt\n(напр. −300 с)", size=11, color=FIELD, bold=True))
    p.append(text(x_max, y_axis + 22, "T_now + Δt\n(напр. +300 с)", size=11, color=FIELD, bold=True))

    # Зона 1: Застарілий запит (Expired)
    p.append(rect(80, 140, x_min - 80, 140, fill="#fff5f5", stroke=POS, sw=1, rx=4))
    p.append(text((80 + x_min) / 2, 180, "Застарілий запит", size=13, bold=True, color=POS))
    p.append(text((80 + x_min) / 2, 205, "t < T_now − 300s", size=11, color=POS))
    p.append(text((80 + x_min) / 2, 255, "ВІДХИЛЕНО (401/400)", size=11, bold=True, color=POS))

    # Зона 2: Валідне вікно (Valid Window)
    p.append(rect(x_min, 140, x_max - x_min, 140, fill="#eaf7ef", stroke=FIELD, sw=1.5, rx=4))
    p.append(text((x_min + x_max) / 2, 165, "Допустиме вікно валідності", size=13, bold=True, color=FIELD))
    p.append(text((x_min + x_max) / 2, 188, "|T_now − t| ≤ 300s", size=11, color=FIELD))

    # Подія всередині вікна + дедуплікація
    p.append(text((x_min + x_max) / 2, 215, "1-й прихід: перевірка HMAC → OK → запис Nonce", size=11, color=INK))
    p.append(text((x_min + x_max) / 2, 235, "Replay повтор: Nonce вже в базі → 200 (без дії)", size=11, color=FIELD, bold=True))

    # Зона 3: Майбутній запит (Clock Skew / Future)
    p.append(rect(x_max, 140, 920 - x_max, 140, fill="#fff5f5", stroke=POS, sw=1, rx=4))
    p.append(text((x_max + 920) / 2, 180, "Запит із майбутнього", size=13, bold=True, color=POS))
    p.append(text((x_max + 920) / 2, 205, "t > T_now + 300s", size=11, color=POS))
    p.append(text((x_max + 920) / 2, 255, "ВІДХИЛЕНО (400)", size=11, bold=True, color=POS))

    # Підсумок знизу
    b_summary, _, _ = box_at(W / 2, 410, "Дворівневий захист: Часове вікно обмежує життя запиту до 5 хвилин,\nа сховище Nonce / Event ID захищає від тисяч повторів усередині цього вікна.",
                             size=12, fill="#f8fafc", stroke=LINE, min_w=650, pad=10)
    p.append(b_summary)

    render(os.path.join(IMG, "timestamp-replay-window.svg"), W, H, *p)


# ── Фігура 4: Життєвий цикл ротації секретів без простою ──────────────────────
def fig_secret_rotation():
    W, H = 1000, 500
    p = []
    p.append(text(W / 2, 32, "Ротація секретів без простою (Zero-Downtime Secret Rotation)", size=18, bold=True))

    xs = [140, 380, 620, 860]
    y_top = 100

    # Крок 1
    b1, w1, h1 = box_at(xs[0], y_top + 40, "Фаза 1: Генерація\n\nПровайдер створює\nновий секрет Secret_B.\nСпоживач додає Secret_B\nяк вторинний (secondary).",
                        size=11, fill="#f8fafc", stroke=LINE, min_w=200, pad=10)
    p.append(b1)
    p.append(text(xs[0], y_top - 15, "КРОК 1", size=13, bold=True, color=NEG))

    # Крок 2
    b2, w2, h2 = box_at(xs[1], y_top + 40, "Фаза 2: Підпис обома\n\nПровайдер шле підпис\nSecret_B (або обидва: A і B).\nСпоживач валідує:\n1) Secret_A (primary)\n2) Secret_B (secondary).",
                        size=11, fill="#eaf0fd", stroke=NEG, min_w=200, pad=10)
    p.append(b2)
    p.append(text(xs[1], y_top - 15, "КРОК 2", size=13, bold=True, color=NEG))
    p.append(arrow(xs[0] + w1, y_top + 40, xs[1] - w2, y_top + 40, sw=1.7))

    # Крок 3
    b3, w3, h3 = box_at(xs[2], y_top + 40, "Фаза 3: Перемикання\n\nСпоживач підвищує\nSecret_B до primary.\nSecret_A стає secondary.\nЗапити обох типів\nуспішно проходять.",
                        size=11, fill="#eaf7ef", stroke=FIELD, min_w=200, pad=10)
    p.append(b3)
    p.append(text(xs[2], y_top - 15, "КРОК 3", size=13, bold=True, color=FIELD))
    p.append(arrow(xs[1] + w2, y_top + 40, xs[2] - w3, y_top + 40, sw=1.7))

    # Крок 4
    b4, w4, h4 = box_at(xs[3], y_top + 40, "Фаза 4: Очищення\n\nМинув час time-window\n(наприклад, 15 хвилин).\nСтарий Secret_A\nповністю видаляється\nз конфігурації.",
                        size=11, fill="#f8fafc", stroke=LINE, min_w=200, pad=10)
    p.append(b4)
    p.append(text(xs[3], y_top - 15, "КРОК 4", size=13, bold=True, color=FIELD))
    p.append(arrow(xs[2] + w3, y_top + 40, xs[3] - w4, y_top + 40, sw=1.7))

    # Стан конфігурації споживача в часі
    y_cfg = 340
    p.append(text(W / 2, y_cfg - 35, "Стан верифікатора споживача на кожному етапі:", size=13, bold=True))

    s1, _, _ = box_at(xs[0], y_cfg + 20, "Primary: Key_A\nSecondary: Key_B", size=11, fill="#ffffff", stroke=LINE, min_w=190)
    s2, _, _ = box_at(xs[1], y_cfg + 20, "Primary: Key_A\nSecondary: Key_B", size=11, fill="#eaf0fd", stroke=NEG, min_w=190)
    s3, _, _ = box_at(xs[2], y_cfg + 20, "Primary: Key_B\nSecondary: Key_A", size=11, fill="#eaf7ef", stroke=FIELD, min_w=190)
    s4, _, _ = box_at(xs[3], y_cfg + 20, "Primary: Key_B\nSecondary: —", size=11, fill="#ffffff", stroke=LINE, min_w=190)
    for s in (s1, s2, s3, s4):
        p.append(s)

    p.append(arrow(xs[0] + 95, y_cfg + 20, xs[1] - 95, y_cfg + 20, sw=1.3))
    p.append(arrow(xs[1] + 95, y_cfg + 20, xs[2] - 95, y_cfg + 20, sw=1.3))
    p.append(arrow(xs[2] + 95, y_cfg + 20, xs[3] - 95, y_cfg + 20, sw=1.3))

    render(os.path.join(IMG, "secret-rotation-lifecycle.svg"), W, H, *p)


if __name__ == "__main__":
    fig_attack_vectors()
    fig_hmac_construction()
    fig_replay_window()
    fig_secret_rotation()
    print("All figures generated successfully.")
