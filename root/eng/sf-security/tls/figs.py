# -*- coding: utf-8 -*-
"""Фігури для теми «TLS» (book/communications/cryptographic-comm/tls)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

COLOR_BG = "#ffffff"
COLOR_HEADER = "#e2e8f0"
COLOR_CLIENT = "#dbeafe"       # синій для клієнта
COLOR_CLIENT_BORDER = "#2563eb"
COLOR_SERVER = "#fef3c7"       # жовтий для сервера
COLOR_SERVER_BORDER = "#d97706"
COLOR_CRYPTO = "#f3e8ff"       # фіолетовий для криптографії / ключів
COLOR_CRYPTO_BORDER = "#7e22ce"
COLOR_CIPHER = "#d1fae5"       # зелений для зашифрованих даних
COLOR_CIPHER_BORDER = "#059669"
COLOR_WARN = "#fee2e2"         # рожевий для незахищеного / вразливого
COLOR_WARN_BORDER = "#dc2626"
COLOR_MUTED = "#64748b"
COLOR_LINE = "#333333"

def fig1_handshake_comparison():
    """Фігура 1: Порівняння фаз рукостискання TLS 1.2 (2-RTT), TLS 1.3 (1-RTT) та TLS 1.3 (0-RTT)."""
    W, H = 1040, 560
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(520, 28, "Еволюція рукостискання: затримка встановлення з'єднання та захист метаданих",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # ── Панель 1: TLS 1.2 (2-RTT) ──
    frags.append(rect(20, 60, 315, 480, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(177, 85, "TLS 1.2 (2-RTT Handshake)", size=13, bold=True, color="#1e3a8a"))
    frags.append(text(177, 102, "Сертифікат і параметри у відкритому вигляді", size=10, italic=True, color=COLOR_MUTED))

    # Стовпчики Client / Server
    frags.append(rect(45, 120, 70, 24, fill=COLOR_CLIENT, stroke=COLOR_CLIENT_BORDER, sw=1.2, rx=4))
    frags.append(text(80, 136, "Client", size=11, bold=True, color="#1e3a8a"))
    frags.append(rect(235, 120, 70, 24, fill=COLOR_SERVER, stroke=COLOR_SERVER_BORDER, sw=1.2, rx=4))
    frags.append(text(270, 136, "Server", size=11, bold=True, color="#92400e"))

    frags.append(line(80, 144, 80, 500, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(line(270, 144, 270, 500, color="#94a3b8", sw=1.2, dash="4,4"))

    # RTT 1 у TLS 1.2
    frags.append(arrow(85, 175, 265, 205, color=COLOR_LINE, sw=1.5))
    frags.append(text(177, 180, "ClientHello (CipherSuites)", size=9.5, bold=True))

    frags.append(arrow(265, 220, 85, 260, color=COLOR_WARN_BORDER, sw=1.5))
    frags.append(text(177, 230, "ServerHello, Certificate (Plain)", size=9.5, bold=True, color=COLOR_WARN_BORDER))
    frags.append(text(177, 245, "ServerKeyExchange, ServerHelloDone", size=9, color=COLOR_MUTED))

    frags.append(text(30, 220, "1 RTT", size=9.5, bold=True, color=COLOR_MUTED))

    # RTT 2 у TLS 1.2
    frags.append(arrow(85, 280, 265, 320, color=COLOR_LINE, sw=1.5))
    frags.append(text(177, 290, "ClientKeyExchange", size=9.5, bold=True))
    frags.append(text(177, 305, "ChangeCipherSpec, Finished", size=9, color=COLOR_MUTED))

    frags.append(arrow(265, 335, 85, 370, color=COLOR_LINE, sw=1.5))
    frags.append(text(177, 345, "ChangeCipherSpec, Finished", size=9.5, bold=True))

    frags.append(text(30, 330, "2 RTT", size=9.5, bold=True, color=COLOR_MUTED))

    # Дані додатку у TLS 1.2
    frags.append(arrow(85, 410, 265, 440, color=COLOR_CIPHER_BORDER, sw=2.0))
    frags.append(text(177, 415, "[Шифровані дані додатку]", size=10, bold=True, color=COLOR_CIPHER_BORDER))

    frags.append(rect(35, 470, 285, 55, fill=COLOR_WARN, stroke=COLOR_WARN_BORDER, sw=1.0, rx=4))
    frags.append(text(177, 488, "Недоліки TLS 1.2:", size=9.5, bold=True, color=COLOR_WARN_BORDER))
    frags.append(text(177, 504, "• Затримка 2 RTT до першого байта даних", size=9, color="#7f1d1d"))
    frags.append(text(177, 518, "• Відкритий сертифікат розкриває ідентичність", size=9, color="#7f1d1d"))

    # ── Панель 2: TLS 1.3 (1-RTT) ──
    frags.append(rect(355, 60, 325, 480, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(517, 85, "TLS 1.3 (1-RTT Full Handshake)", size=13, bold=True, color="#047857"))
    frags.append(text(517, 102, "Захищений обмін з першої відповіді", size=10, italic=True, color=COLOR_MUTED))

    # Стовпчики Client / Server
    frags.append(rect(380, 120, 70, 24, fill=COLOR_CLIENT, stroke=COLOR_CLIENT_BORDER, sw=1.2, rx=4))
    frags.append(text(415, 136, "Client", size=11, bold=True, color="#1e3a8a"))
    frags.append(rect(585, 120, 70, 24, fill=COLOR_SERVER, stroke=COLOR_SERVER_BORDER, sw=1.2, rx=4))
    frags.append(text(620, 136, "Server", size=11, bold=True, color="#92400e"))

    frags.append(line(415, 144, 415, 500, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(line(620, 144, 620, 500, color="#94a3b8", sw=1.2, dash="4,4"))

    # Запит ClientHello + key_share
    frags.append(arrow(420, 180, 615, 215, color=COLOR_CLIENT_BORDER, sw=1.8))
    frags.append(text(517, 185, "ClientHello", size=10, bold=True, color=COLOR_CLIENT_BORDER))
    frags.append(text(517, 200, "+ key_share (ECDH публічний ключ)", size=9, color="#1e40af"))

    # Відповідь ServerHello + EncryptedExtensions + Certificate + Finished
    frags.append(arrow(615, 240, 420, 285, color=COLOR_SERVER_BORDER, sw=1.8))
    frags.append(text(517, 245, "ServerHello + key_share", size=10, bold=True, color=COLOR_SERVER_BORDER))
    frags.append(rect(435, 260, 165, 42, fill=COLOR_CIPHER, stroke=COLOR_CIPHER_BORDER, sw=1.0, rx=4))
    frags.append(text(517, 274, "{EncryptedExtensions, Cert,", size=9, bold=True, color=COLOR_CIPHER_BORDER))
    frags.append(text(517, 289, " CertVerify, Finished}", size=9, bold=True, color=COLOR_CIPHER_BORDER))

    frags.append(text(368, 245, "1 RTT", size=9.5, bold=True, color="#047857"))

    # Завершення клієнта і передача даних
    frags.append(arrow(420, 335, 615, 365, color=COLOR_CIPHER_BORDER, sw=2.0))
    frags.append(text(517, 340, "{Finished} + [Шифровані дані додатку]", size=9.5, bold=True, color=COLOR_CIPHER_BORDER))

    frags.append(arrow(615, 395, 420, 425, color=COLOR_CIPHER_BORDER, sw=2.0))
    frags.append(text(517, 400, "[Шифрована відповідь сервера]", size=9.5, bold=True, color=COLOR_CIPHER_BORDER))

    frags.append(rect(370, 470, 295, 55, fill=COLOR_CIPHER, stroke=COLOR_CIPHER_BORDER, sw=1.0, rx=4))
    frags.append(text(517, 488, "Переваги TLS 1.3 (1-RTT):", size=9.5, bold=True, color="#065f46"))
    frags.append(text(517, 504, "• Дані надсилаються рівно за 1 RTT", size=9, color="#065f46"))
    frags.append(text(517, 518, "• Сертифікат сервера зашифровано ключем handshake", size=9, color="#065f46"))

    # ── Панель 3: TLS 1.3 (0-RTT Early Data) ──
    frags.append(rect(700, 60, 320, 480, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(860, 85, "TLS 1.3 (0-RTT Resumption)", size=13, bold=True, color="#5b21b6"))
    frags.append(text(860, 102, "Відновлення сесії за допомогою PSK", size=10, italic=True, color=COLOR_MUTED))

    # Стовпчики Client / Server
    frags.append(rect(725, 120, 70, 24, fill=COLOR_CLIENT, stroke=COLOR_CLIENT_BORDER, sw=1.2, rx=4))
    frags.append(text(760, 136, "Client", size=11, bold=True, color="#1e3a8a"))
    frags.append(rect(925, 120, 70, 24, fill=COLOR_SERVER, stroke=COLOR_SERVER_BORDER, sw=1.2, rx=4))
    frags.append(text(960, 136, "Server", size=11, bold=True, color="#92400e"))

    frags.append(line(760, 144, 760, 500, color="#94a3b8", sw=1.2, dash="4,4"))
    frags.append(line(960, 144, 960, 500, color="#94a3b8", sw=1.2, dash="4,4"))

    # Перший політ: ClientHello + PSK + Early Data
    frags.append(arrow(765, 180, 955, 215, color=COLOR_CRYPTO_BORDER, sw=2.0))
    frags.append(text(860, 185, "ClientHello + early_data_ext", size=9.5, bold=True, color=COLOR_CRYPTO_BORDER))
    frags.append(text(860, 200, "+ [0-RTT Early Data (GET /index)]", size=9.5, bold=True, color="#6b21a8"))

    frags.append(text(715, 195, "0 RTT", size=10, bold=True, color="#6b21a8"))

    # Відповідь сервера
    frags.append(arrow(955, 250, 765, 290, color=COLOR_SERVER_BORDER, sw=1.8))
    frags.append(text(860, 255, "ServerHello (PSK selected)", size=9.5, bold=True, color=COLOR_SERVER_BORDER))
    frags.append(text(860, 270, "{EncryptedExtensions, Finished}", size=9, color=COLOR_CIPHER_BORDER))
    frags.append(text(860, 285, "[Шифрована відповідь 200 OK]", size=9, color=COLOR_CIPHER_BORDER))

    # Звичайний потік даних після оновлення ключів
    frags.append(arrow(765, 335, 955, 365, color=COLOR_CIPHER_BORDER, sw=1.8))
    frags.append(text(860, 345, "{Finished} (1-RTT Traffic Key)", size=9, color=COLOR_CIPHER_BORDER))

    frags.append(rect(715, 470, 290, 55, fill=COLOR_WARN, stroke=COLOR_WARN_BORDER, sw=1.0, rx=4))
    frags.append(text(860, 488, "Застереження щодо 0-RTT:", size=9.5, bold=True, color=COLOR_WARN_BORDER))
    frags.append(text(860, 504, "• Немає прямої секретності (PFS) для 0-RTT", size=9, color="#7f1d1d"))
    frags.append(text(860, 518, "• Вразливість до атак повтору (Replay Attacks)", size=9, color="#7f1d1d"))

    render(os.path.join(IMG, "fig1-handshake-comparison.svg"), W, H, *frags)


def fig2_record_layer_aead():
    """Фігура 2: Структура протоколу записів TLS 1.3 та обробка автентифікованого шифрування AEAD."""
    W, H = 980, 480
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(490, 28, "Архітектура кадру протоколу записів TLS 1.3 та механізм AEAD",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # Верхня панель: Структура бінарного кадру
    frags.append(rect(30, 65, 920, 160, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(490, 88, "Формат захищеного запису TLS 1.3 на канальному рівні (Wire Layout)", size=13, bold=True, color="#1e3a8a"))

    # Блоки кадру
    # 1. Заголовок (5 байт)
    frags.append(rect(50, 115, 230, 80, fill=COLOR_CLIENT, stroke=COLOR_CLIENT_BORDER, sw=1.5, rx=6))
    frags.append(text(165, 138, "Зовнішній заголовок (5 байтів)", size=11, bold=True, color="#1e3a8a"))
    frags.append(text(165, 156, "Type: 0x17 (opaque_type)", size=9.5, color=COLOR_LINE))
    frags.append(text(165, 172, "Legacy Version: 0x0303 (TLS 1.2)", size=9.5, color=COLOR_LINE))
    frags.append(text(165, 186, "Length: N байтів (зашифроване тіло)", size=9, color=COLOR_MUTED))

    # 2. Зашифроване тіло (N - 16 байт)
    frags.append(rect(290, 115, 410, 80, fill=COLOR_CIPHER, stroke=COLOR_CIPHER_BORDER, sw=1.5, rx=6))
    frags.append(text(495, 138, "Зашифрований корисний вантаж (Encrypted Payload)", size=11, bold=True, color="#065f46"))
    frags.append(text(495, 156, "Відкритий текст (Application Data / Handshake) + Padding", size=9.5, color=COLOR_LINE))
    frags.append(text(495, 174, "+ Справжній тип вмісту (Inner ContentType: 1 байт у кінці)", size=9.5, bold=True, color="#047857"))
    frags.append(text(495, 188, "Маскування типу та вирівнювання довжини від аналізу трафіку", size=9.5, italic=True, color=COLOR_MUTED))

    # 3. Аутентифікаційний тег (16 байт)
    frags.append(rect(710, 115, 220, 80, fill=COLOR_CRYPTO, stroke=COLOR_CRYPTO_BORDER, sw=1.5, rx=6))
    frags.append(text(820, 138, "Тег автентичності (16 байтів)", size=11, bold=True, color="#6b21a8"))
    frags.append(text(820, 156, "AEAD Authentication Tag", size=9.5, color=COLOR_LINE))
    frags.append(text(820, 174, "GCM / Poly1305 / CCM", size=9.5, bold=True, color="#5b21b6"))
    frags.append(text(820, 188, "Захист цілісності та заголовка", size=9.5, color=COLOR_MUTED))

    # Нижня панель: Конвеєр AEAD автентифікації та синтез Nonce
    frags.append(rect(30, 240, 920, 215, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(490, 265, "Математика формування Nonce та AEAD-перевірки", size=13, bold=True, color="#5b21b6"))

    # Лівий блок: Формування Nonce (IV XOR SeqNum)
    frags.append(rect(50, 290, 420, 145, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(260, 312, "Синтез унікального одноразового числа (Nonce)", size=11, bold=True, color="#1e3a8a"))
    frags.append(textbox(260, 360, "Write IV (96 біт) = iv₀ iv₁ ... iv₁₁\n⊕ 64-бітний SeqNum (доповнений нулями зліва)\n= Унікальний Nonce для кожного запису",
                         size=10, fill=COLOR_CRYPTO, stroke=COLOR_CRYPTO_BORDER)[0])
    frags.append(text(260, 418, "Захист від атак повтору без передачі Nonce через мережу", size=9.5, italic=True, color=COLOR_MUTED))

    # Правий блок: AEAD Encrypt / Decrypt
    frags.append(rect(490, 290, 440, 145, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    frags.append(text(710, 312, "Автентифіковане шифрування з асоційованими даними", size=11, bold=True, color="#047857"))
    frags.append(textbox(710, 360, "Входи AEAD: Key, Nonce, Plaintext (Data || InnerType || Pad)\nАсоційовані дані (AAD) = 5-байтний зовнішній заголовок\nВихід: Ciphertext || 16-байтний Auth Tag",
                         size=10, fill=COLOR_CIPHER, stroke=COLOR_CIPHER_BORDER)[0])
    frags.append(text(710, 418, "Цілісність заголовка захищена без його шифрування", size=9.5, italic=True, color=COLOR_MUTED))

    render(os.path.join(IMG, "fig2-record-layer-aead.svg"), W, H, *frags)


def fig3_tls13_key_schedule():
    """Фігура 3: Дерево виведення ключів TLS 1.3 на базі функцій HKDF-Extract та HKDF-Expand."""
    W, H = 1000, 580
    frags = []

    # Заголовок
    tb_title, _, _ = textbox(500, 28, "Дерево ключів TLS 1.3 (Key Schedule на базі HKDF)",
                             size=15, bold=True, fill=COLOR_HEADER, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(tb_title)

    # ── Етап 1: Ранній секрет (Early Secret) ──
    frags.append(rect(30, 65, 290, 490, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(175, 90, "1. Рання фаза (Early Secret)", size=12.5, bold=True, color="#6b21a8"))
    frags.append(text(175, 107, "Використання PSK (якщо наявний)", size=9.5, italic=True, color=COLOR_MUTED))

    frags.append(textbox(175, 145, "Вхідний матеріал (IKM):\nPSK (або 0-вектор)", size=10, fill=COLOR_CLIENT, stroke=COLOR_CLIENT_BORDER)[0])
    frags.append(arrow(175, 175, 175, 205, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(175, 225, "HKDF-Extract(0, IKM)\n= Early Secret", size=10.5, bold=True, fill=COLOR_CRYPTO, stroke=COLOR_CRYPTO_BORDER)[0])
    frags.append(arrow(175, 255, 175, 295, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(175, 335, "HKDF-Expand-Label\n↓\n• Client Early Traffic Secret\n• Early Exporter Master Secret", size=9.5, fill="#ffffff", stroke="#94a3b8")[0])
    frags.append(arrow(175, 385, 175, 415, color=COLOR_CIPHER_BORDER, sw=1.5))
    frags.append(textbox(175, 445, "Ключі для 0-RTT\nClient Early Write Key & IV", size=10, bold=True, fill=COLOR_CIPHER, stroke=COLOR_CIPHER_BORDER)[0])

    # ── Етап 2: Секрет рукостискання (Handshake Secret) ──
    frags.append(rect(345, 65, 310, 490, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(500, 90, "2. Фаза рукостискання (Handshake)", size=12.5, bold=True, color="#1e3a8a"))
    frags.append(text(500, 107, "Асиметричний обмін ECDHE", size=9.5, italic=True, color=COLOR_MUTED))

    # Стрілка переходу від Early Secret
    frags.append(arrow(245, 225, 360, 225, color=COLOR_CRYPTO_BORDER, sw=1.8))
    frags.append(text(302, 215, "Derive-Secret", size=9.5, bold=True, color="#6b21a8"))

    frags.append(textbox(500, 145, "Спільний секрет ECDHE (Z)\nZ = x_A · Y_B (X25519 / P-256)", size=10, fill=COLOR_CLIENT, stroke=COLOR_CLIENT_BORDER)[0])
    frags.append(arrow(500, 175, 500, 205, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(500, 225, "HKDF-Extract(EarlyDerived, Z)\n= Handshake Secret", size=10.5, bold=True, fill=COLOR_CRYPTO, stroke=COLOR_CRYPTO_BORDER)[0])
    frags.append(arrow(500, 255, 500, 295, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(500, 335, "HKDF-Expand-Label(Transcript)\n↓\n• Client Handshake Traffic Secret\n• Server Handshake Traffic Secret", size=9.5, fill="#ffffff", stroke="#94a3b8")[0])
    frags.append(arrow(500, 385, 500, 415, color=COLOR_CIPHER_BORDER, sw=1.5))
    frags.append(textbox(500, 455, "Захист повідомлень рукостискання:\nClient/Server Handshake Keys & IVs\n+ Finished Verification Keys", size=9.5, bold=True, fill=COLOR_CIPHER, stroke=COLOR_CIPHER_BORDER)[0])

    # ── Етап 3: Головний секрет додатку (Master Secret) ──
    frags.append(rect(680, 65, 290, 490, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(825, 90, "3. Фаза додатку (Master Secret)", size=12.5, bold=True, color="#047857"))
    frags.append(text(825, 107, "Безпечна передача даних і оновлення", size=9.5, italic=True, color=COLOR_MUTED))

    # Стрілка переходу від Handshake Secret
    frags.append(arrow(585, 225, 700, 225, color=COLOR_CRYPTO_BORDER, sw=1.8))
    frags.append(text(642, 215, "Derive-Secret", size=9.5, bold=True, color="#6b21a8"))

    frags.append(textbox(825, 145, "Вхідний матеріал: 0-вектор\n(Консолідація ентропії)", size=10, fill=COLOR_SERVER, stroke=COLOR_SERVER_BORDER)[0])
    frags.append(arrow(825, 175, 825, 205, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(825, 225, "HKDF-Extract(HandshakeDerived, 0)\n= Master Secret", size=10.5, bold=True, fill=COLOR_CRYPTO, stroke=COLOR_CRYPTO_BORDER)[0])
    frags.append(arrow(825, 255, 825, 295, color=COLOR_LINE, sw=1.5))

    frags.append(textbox(825, 335, "HKDF-Expand-Label(Transcript)\n↓\n• Client/Server App Traffic Secret 0\n• Resumption Master Secret\n• Exporter Master Secret", size=9.5, fill="#ffffff", stroke="#94a3b8")[0])
    frags.append(arrow(825, 385, 825, 415, color=COLOR_CIPHER_BORDER, sw=1.5))
    frags.append(textbox(825, 455, "Захист трафіку додатку (1-RTT)\nClient/Server Application Keys & IVs\n+ KeyUpdate (Оновлення ключів)", size=9.5, bold=True, fill=COLOR_CIPHER, stroke=COLOR_CIPHER_BORDER)[0])

    render(os.path.join(IMG, "fig3-tls13-key-schedule.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_handshake_comparison()
    fig2_record_layer_aead()
    fig3_tls13_key_schedule()
    print("Усі 3 фігури успішно згенеровано у ./img/")
