# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CLR_MEDIA = "#c0392b"
CLR_DATA  = "#2457d6"
CLR_SEC   = "#27ae60"
CLR_NET   = "#6b7280"
CLR_WARN  = "#b08900"

def fig_webrtc_stack():
    W, H = 880, 480
    p = []
    p.append(text(W / 2, 28, "Архітектура стеку протоколів WebRTC", size=16, bold=True))

    # Application Layer
    p.append(rect(40, 50, 800, 45, fill="#fdf3e0", stroke=LINE))
    p.append(text(440, 78, "Прикладний шар (JavaScript API / Нативний додаток: MediaStream, RTCDataChannel)", size=13, bold=True))

    # Media Path column
    mw = 380
    mx = 40
    p.append(rect(mx, 105, mw, 230, fill="#fef5f5", stroke=CLR_MEDIA, sw=1.5))
    p.append(text(mx + mw/2, 125, "Медіа-тракт (Аудіо / Відео)", size=13, bold=True, color=CLR_MEDIA))
    p.append(fitbox(mx + 20, 140, mw - 40, 36, "Кодеки: Opus (аудіо), H.264 / VP8 / VP9 / AV1 (відео)", size=11, fill="#ffffff", stroke=CLR_MEDIA))
    p.append(fitbox(mx + 20, 185, mw - 40, 36, "RTP (корисний вантаж) / RTCP (зворотний зв'язок)", size=11, fill="#ffffff", stroke=CLR_MEDIA))
    p.append(fitbox(mx + 20, 230, mw - 40, 36, "SRTP / SRTCP (шифрування AES-GCM / HMAC-SHA1)", size=11, fill="#fdecea", stroke=CLR_MEDIA, bold=True))
    p.append(fitbox(mx + 20, 275, mw - 40, 45, "DTLS (узгодження ключів для SRTP через RFC 5764)", size=11, fill="#eaf6ee", stroke=CLR_SEC, bold=True))

    # Data Path column
    dx = 460
    dw = 380
    p.append(rect(dx, 105, dw, 230, fill="#f0f4fe", stroke=CLR_DATA, sw=1.5))
    p.append(text(dx + dw/2, 125, "Тракт довільних даних (DataChannel)", size=13, bold=True, color=CLR_DATA))
    p.append(fitbox(dx + 20, 140, dw - 40, 36, "Бінарні повідомлення / Текстові кадри (UTF-8)", size=11, fill="#ffffff", stroke=CLR_DATA))
    p.append(fitbox(dx + 20, 185, dw - 40, 36, "SCTP (потоковий контроль, надійний / ненадійний режим)", size=11, fill="#ffffff", stroke=CLR_DATA))
    p.append(fitbox(dx + 20, 230, dw - 40, 90, "DTLS (інкапсуляція та захист усього SCTP-трафіку)\nШифрування TLS 1.2 / 1.3 на транспортному рівні", size=11, fill="#eaf6ee", stroke=CLR_SEC, bold=True))

    # Common Lower Layers
    p.append(fitbox(40, 345, 800, 38, "UDP (User Datagram Protocol) — мультиплексування потоків через BUNDLE на єдиному сокеті", size=12, fill="#eaf0fd", stroke=NEG, bold=True))
    p.append(fitbox(40, 390, 800, 38, "ICE (Interactive Connectivity Establishment) + STUN / TURN (NAT Traversal)", size=12, fill="#f4f6f8", stroke=LINE, bold=True))
    p.append(fitbox(40, 435, 800, 32, "IP (IPv4 / IPv6) — мережевий шар", size=11, fill="#ffffff", stroke=LINE))

    render(os.path.join(OUT, "webrtc-stack.svg"), W, H, *p)


def fig_ice_connectivity():
    W, H = 880, 440
    p = []
    p.append(text(W / 2, 28, "Зв'язність ICE: виявлення адрес через STUN та ретрансляція TURN", size=16, bold=True))

    # Columns: Peer A, NAT A, STUN/TURN, NAT B, Peer B
    col_x = [70, 230, 440, 650, 810]
    labels = [
        "Peer A\n(192.168.1.50)",
        "NAT A\n(Маршрутизатор)",
        "STUN / TURN\nСервер",
        "NAT B\n(Маршрутизатор)",
        "Peer B\n(10.0.0.12)"
    ]

    for cx, lbl in zip(col_x, labels):
        p.append(rect(cx - 55, 50, 110, 42, fill="#f4f6f8", stroke=LINE))
        p.append(mtext(cx, 63, lbl, size=11, bold=True))
        p.append(line(cx, 95, cx, 385, color="#cccccc", sw=1, dash="4,4"))

    # Steps
    # 1. Host Candidates
    p.append(text(col_x[0], 115, "1. Збір локальних адрес (Host)", size=11, color=INK, anchor="start"))
    p.append(rect(col_x[0] - 10, 122, 160, 22, fill="#fdf3e0", stroke=CLR_WARN, rx=4))
    p.append(text(col_x[0] + 70, 137, "cand: host (192.168.1.50)", size=10, bold=True))

    # 2. STUN Binding
    p.append(arrow(col_x[0], 155, col_x[2], 155, color=NEG))
    p.append(text(280, 150, "STUN Binding Request", size=10, color=NEG))
    p.append(arrow(col_x[2], 180, col_x[0], 180, color=NEG))
    p.append(text(280, 175, "Binding Success (XOR-MAPPED: 203.0.113.4:54320)", size=10, color=NEG))
    p.append(rect(col_x[0] - 10, 188, 160, 22, fill="#eaf0fd", stroke=NEG, rx=4))
    p.append(text(col_x[0] + 70, 203, "cand: srflx (203.0.113.4)", size=10, bold=True))

    # 3. TURN Allocate
    p.append(arrow(col_x[0], 220, col_x[2], 220, color=POS))
    p.append(text(280, 215, "TURN Allocate Request", size=10, color=POS))
    p.append(arrow(col_x[2], 245, col_x[0], 245, color=POS))
    p.append(text(280, 240, "Allocate Response (Relayed: 198.51.100.1:34780)", size=10, color=POS))
    p.append(rect(col_x[0] - 10, 252, 160, 22, fill="#fdecea", stroke=POS, rx=4))
    p.append(text(col_x[0] + 70, 267, "cand: relay (198.51.100.1)", size=10, bold=True))

    # 4. Direct P2P Check vs Relay
    p.append(line(col_x[0], 295, col_x[4], 295, color=CLR_SEC, sw=2))
    p.append(arrow(col_x[0], 295, col_x[4] - 5, 295, color=CLR_SEC, sw=2))
    p.append(text(440, 290, "Прямий P2P-канал (STUN Connectivity Check: srflx ↔ srflx)", size=11, bold=True, color=CLR_SEC))

    # 5. Relay fallback path
    p.append(line(col_x[0], 335, col_x[2], 335, color=POS, sw=1.5, dash="3,3"))
    p.append(line(col_x[2], 335, col_x[4], 335, color=POS, sw=1.5, dash="3,3"))
    p.append(arrow(col_x[2], 335, col_x[4] - 5, 335, color=POS, sw=1.5))
    p.append(text(440, 330, "Резервний шлях через TURN Relay (якщо пряме пробиття NAT заблоковане)", size=10, italic=True, color=POS))

    # Summary box
    p.append(rect(50, 370, 780, 55, fill="#f4f6f8", stroke=LINE))
    p.append(text(440, 390, "Пріоритет перевірки пар кандидатів: Host (найвищий) → Server Reflexive (STUN) → Relayed (TURN fallback).", size=11, bold=True))
    p.append(text(440, 410, "Переможна пара фіксується атрибутом USE-CANDIDATE і використовується для всього трафіку сесії.", size=10, color=MUTED))

    render(os.path.join(OUT, "ice-connectivity-check.svg"), W, H, *p)


def fig_offer_answer():
    W, H = 880, 420
    p = []
    p.append(text(W / 2, 28, "Сигнальний обмін Offer / Answer та збір Trickle ICE", size=16, bold=True))

    ax, sx, bx = 120, 440, 760
    # Lifelines
    p.append(rect(ax - 60, 50, 120, 40, fill="#eaf0fd", stroke=NEG))
    p.append(text(ax, 75, "Peer A (Ініціатор)", size=12, bold=True))
    p.append(line(ax, 90, ax, 360, color="#cccccc", sw=1, dash="4,4"))

    p.append(rect(sx - 75, 50, 150, 40, fill="#fdf3e0", stroke=CLR_WARN))
    p.append(text(sx, 75, "Сигнальний сервер", size=11, bold=True))
    p.append(line(sx, 90, sx, 360, color="#cccccc", sw=1, dash="4,4"))

    p.append(rect(bx - 60, 50, 120, 40, fill="#eaf6ee", stroke=CLR_SEC))
    p.append(text(bx, 75, "Peer B (Відповідач)", size=12, bold=True))
    p.append(line(bx, 90, bx, 360, color="#cccccc", sw=1, dash="4,4"))

    # Offer
    p.append(arrow(ax, 115, sx, 115, color=NEG, sw=1.5))
    p.append(text(280, 110, "1. SDP Offer (кодеки, ufrag, DTLS fingerprint)", size=10, bold=True, color=NEG))
    p.append(arrow(sx, 130, bx, 130, color=NEG, sw=1.5))
    p.append(text(600, 125, "1. SDP Offer ретранслюється до Peer B", size=10, color=NEG))

    # Answer
    p.append(arrow(bx, 165, sx, 165, color=CLR_SEC, sw=1.5))
    p.append(text(600, 160, "2. SDP Answer (обрані кодеки, DTLS fingerprint)", size=10, bold=True, color=CLR_SEC))
    p.append(arrow(sx, 180, ax, 180, color=CLR_SEC, sw=1.5))
    p.append(text(280, 175, "2. SDP Answer повертається до Peer A", size=10, color=CLR_SEC))

    # Trickle ICE
    p.append(arrow(ax, 215, sx, 215, color=CLR_WARN, sw=1.2))
    p.append(arrow(sx, 225, bx, 225, color=CLR_WARN, sw=1.2))
    p.append(text(440, 210, "3. Trickle ICE: асинхронна відправка ICE Candidate A", size=10, color=CLR_WARN))

    p.append(arrow(bx, 250, sx, 250, color=CLR_WARN, sw=1.2))
    p.append(arrow(sx, 260, ax, 260, color=CLR_WARN, sw=1.2))
    p.append(text(440, 245, "3. Trickle ICE: асинхронна відправка ICE Candidate B", size=10, color=CLR_WARN))

    # Direct P2P Media
    p.append(rect(ax + 20, 290, bx - ax - 40, 45, fill="#ffffff", stroke=CLR_MEDIA, sw=1.5, rx=6))
    p.append(line(ax + 25, 312, bx - 25, 312, color=CLR_MEDIA, sw=2))
    p.append(arrow(ax + 25, 312, bx - 25, 312, color=CLR_MEDIA, sw=2))
    p.append(arrow(bx - 25, 312, ax + 25, 312, color=CLR_MEDIA, sw=2))
    p.append(text(440, 305, "4. Прямий двонаправлений медіа-трафік SRTP / DataChannel", size=11, bold=True, color=CLR_MEDIA))

    # Footnote
    p.append(text(W/2, 390, "Сигнальний сервер потрібен виключно для початкового узгодження метаданих і не бере участі в передачі медіа.", size=11, italic=True, color=MUTED))

    render(os.path.join(OUT, "offer-answer-sdp.svg"), W, H, *p)


def fig_dtls_srtp():
    W, H = 880, 430
    p = []
    p.append(text(W / 2, 28, "Шифрування DTLS-SRTP та виведення сесійних ключів", size=16, bold=True))

    # Left: DTLS Handshake over UDP
    p.append(rect(40, 55, 360, 310, fill="#eaf6ee", stroke=CLR_SEC, sw=1.5))
    p.append(text(220, 80, "1. DTLS Handshake (поверх UDP)", size=13, bold=True, color=CLR_SEC))
    p.append(fitbox(60, 100, 320, 35, "Клієнтський ClientHello (випадкові числа + розширення)", size=11, fill="#ffffff", stroke=CLR_SEC))
    p.append(fitbox(60, 145, 320, 35, "ServerHello + Сертифікат + ServerKeyExchange", size=11, fill="#ffffff", stroke=CLR_SEC))
    p.append(fitbox(60, 190, 320, 35, "ClientKeyExchange + CertificateVerify (якщо взаємна)", size=11, fill="#ffffff", stroke=CLR_SEC))
    p.append(fitbox(60, 235, 320, 45, "Звірка хешу сертифіката з SDP a=fingerprint\n(Захист від Man-in-the-Middle атаки)", size=10, fill="#fdf3e0", stroke=CLR_WARN, bold=True))
    p.append(fitbox(60, 290, 320, 60, "DTLS Finished\n(Спільний секрет Master Secret сформовано)", size=11, fill="#eaf6ee", stroke=CLR_SEC, bold=True))

    # Center arrow: Key Derivation
    p.append(arrow(405, 210, 475, 210, color=INK, sw=2))
    p.append(text(440, 195, "RFC 5764", size=11, bold=True))
    p.append(text(440, 230, "Keying Material", size=10, italic=True))

    # Right: SRTP Keys & Encryption
    p.append(rect(480, 55, 360, 310, fill="#fef5f5", stroke=CLR_MEDIA, sw=1.5))
    p.append(text(660, 80, "2. Виведення ключів SRTP / SRTCP", size=13, bold=True, color=CLR_MEDIA))

    keys = [
        "SRTP Master Client Encryption Key (128/256 біт)",
        "SRTP Master Server Encryption Key (128/256 біт)",
        "SRTP Master Client Salt Key (112 біт)",
        "SRTP Master Server Salt Key (112 біт)",
        "SRTCP Master Authentication Keys (якщо HMAC-SHA1)"
    ]
    ky = 100
    for k in keys:
        p.append(fitbox(500, ky, 320, 30, k, size=10, fill="#ffffff", stroke=CLR_MEDIA))
        ky += 36

    p.append(fitbox(500, 285, 320, 65, "Прямий захист RTP-пакетів:\nЗаголовки у відкритому вигляді (SSRC, Seq, Timestamp)\nКорисний вантаж зашифровано AES-GCM / AES-CTR", size=10, fill="#fdecea", stroke=CLR_MEDIA, bold=True))

    p.append(text(W / 2, 395, "DTLS не шифрує медіа безпосередньо: він узгоджує ключі для надшвидкого апаратного шифрування SRTP у потоці.", size=11, bold=True, color=INK))

    render(os.path.join(OUT, "dtls-srtp-key-exchange.svg"), W, H, *p)


def fig_twcc_loop():
    W, H = 880, 420
    p = []
    p.append(text(W / 2, 28, "Контур адаптивного керування бітрейтом TWCC (RFC 8888)", size=16, bold=True))

    # Sender on Left, Receiver on Right
    sx = 180
    rx = 700

    p.append(rect(sx - 140, 55, 280, 310, fill="#eaf0fd", stroke=NEG, sw=1.5))
    p.append(text(sx, 80, "Відправник (Sender)", size=13, bold=True, color=NEG))
    p.append(fitbox(sx - 120, 100, 240, 38, "Відеокодер (динамічний бітрейт R)", size=11, fill="#ffffff", stroke=NEG))
    p.append(fitbox(sx - 120, 148, 240, 38, "Pacer: згладжування сплесків кадрів", size=11, fill="#ffffff", stroke=NEG))
    p.append(fitbox(sx - 120, 196, 240, 48, "RTP Packetizer:\nдодає Transport-Wide Sequence #", size=10, fill="#ffffff", stroke=NEG))
    p.append(fitbox(sx - 120, 254, 240, 95, "Оцінювач перевантаження (GCC):\n- Градієнт затримки (Trendline)\n- Фільтрація джиттера\n- Детектор перевантаження\n-> Новий ліміт бітрейту", size=10, fill="#fdf3e0", stroke=CLR_WARN, bold=True))

    p.append(rect(rx - 140, 55, 280, 310, fill="#eaf6ee", stroke=CLR_SEC, sw=1.5))
    p.append(text(rx, 80, "Приймач (Receiver)", size=13, bold=True, color=CLR_SEC))
    p.append(fitbox(rx - 120, 105, 240, 45, "Фіксація точного часу прибуття:\nпакет i -> t_arr[i] (мкс)", size=11, fill="#ffffff", stroke=CLR_SEC))
    p.append(fitbox(rx - 120, 160, 240, 45, "Jitter Buffer & Відеодекодер", size=11, fill="#ffffff", stroke=CLR_SEC))
    p.append(fitbox(rx - 120, 215, 240, 50, "Генератор RTCP TWCC Feedback:\n(Sequence # + дельти часу d_t)", size=11, fill="#ffffff", stroke=CLR_SEC))
    p.append(fitbox(rx - 120, 275, 240, 75, "Відправка RTCP кожні 25–100 мс:\nМінімальне обчислювальне навантаження\n(вся аналітика на відправнику)", size=10, fill="#eaf6ee", stroke=CLR_SEC, bold=True))

    # Flows between Sender and Receiver
    # Top arrow: RTP Packets
    p.append(line(sx + 140, 130, rx - 140, 130, color=CLR_MEDIA, sw=2))
    p.append(arrow(sx + 140, 130, rx - 140, 130, color=CLR_MEDIA, sw=2))
    p.append(text(440, 120, "RTP медіа-пакети з заголовком Transport-CC (номери 1, 2, 3...)", size=10, bold=True, color=CLR_MEDIA))

    # Bottom arrow: RTCP Feedback
    p.append(line(rx - 140, 245, sx + 140, 245, color=CLR_SEC, sw=2))
    p.append(arrow(rx - 140, 245, sx + 140, 245, color=CLR_SEC, sw=2))
    p.append(text(440, 235, "Зворотний зв'язок RTCP TWCC: час надходження кожного пакета", size=10, bold=True, color=CLR_SEC))

    p.append(text(W / 2, 395, "Завдяки TWCC відправник виявляє зростання черг у проміжних маршрутизаторах задовго до реальної втрати пакетів.", size=11, italic=True, color=MUTED))

    render(os.path.join(OUT, "twcc-feedback-loop.svg"), W, H, *p)


def fig_fpv_robotics():
    W, H = 880, 440
    p = []
    p.append(text(W / 2, 28, "WebRTC у робототехніці: FPV-відео та телеметрія через браузер", size=16, bold=True))

    # Left: Robot/Drone Hardware
    p.append(rect(40, 55, 360, 315, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(220, 80, "Бортовий комп'ютер дрона / робота", size=13, bold=True))

    p.append(fitbox(60, 95, 320, 42, "CSI/USB Камера (1080p60 / 720p120)\nHardware Capture (V4L2 / DMA-BUF)", size=11, fill="#ffffff", stroke=LINE))
    p.append(fitbox(60, 145, 320, 48, "Апаратний H.264/AV1 енкодер (NVENC / V4L2-M2M):\nНизька затримка (Intra-Refresh, zero B-frames)", size=10, fill="#fdecea", stroke=CLR_MEDIA, bold=True))
    p.append(fitbox(60, 202, 320, 42, "WebRTC C++ Agent (libdatachannel / GStreamer):\nSRTP відеострімінг + RTCDataChannel", size=11, fill="#ffffff", stroke=CLR_MEDIA))
    p.append(fitbox(60, 252, 320, 48, "Політний контролер (UART / CAN / MAVLink):\nПрийом команд керування та відправка телеметрії", size=10, fill="#eaf0fd", stroke=CLR_DATA, bold=True))
    p.append(fitbox(60, 310, 320, 45, "RTCDataChannel (ordered=false, maxRetransmits=0)\nТелеметрія польоту 50 Гц без затримок буферизації", size=10, fill="#fdf3e0", stroke=CLR_WARN))

    # Right: Browser GCS Station
    p.append(rect(480, 55, 360, 315, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(660, 80, "Станція керування в браузері (GCS)", size=13, bold=True))

    p.append(fitbox(500, 95, 320, 42, "HTML5 Canvas / WebCodecs API:\nАпаратний декодер низької затримки", size=11, fill="#ffffff", stroke=LINE))
    p.append(fitbox(500, 145, 320, 45, "Відображення FPV-відео (Glass-to-Glass < 60 мс)\nБез плагінів у будь-якому сучасному браузері", size=10, fill="#fdecea", stroke=CLR_MEDIA, bold=True))
    p.append(fitbox(500, 198, 320, 45, "Gamepad API / Клавіатура:\nОпитування стіків джойстика з частотою 100 Гц", size=11, fill="#ffffff", stroke=CLR_DATA))
    p.append(fitbox(500, 252, 320, 48, "Відправка команд керування по DataChannel:\nБінарний формат (MAVLink / Protobuf / FlatBuffers)", size=10, fill="#eaf0fd", stroke=CLR_DATA, bold=True))
    p.append(fitbox(500, 310, 320, 45, "HUD Телеметрії (Штучний горизонт, GPS, батарея)\nРендеринг через WebGL / SVG", size=10, fill="#eaf6ee", stroke=CLR_SEC))

    # Central Bi-directional Links
    p.append(line(400, 130, 480, 130, color=CLR_MEDIA, sw=2))
    p.append(arrow(400, 130, 480, 130, color=CLR_MEDIA, sw=2))
    p.append(text(440, 120, "SRTP Відео", size=10, bold=True, color=CLR_MEDIA))

    p.append(line(400, 240, 480, 240, color=CLR_DATA, sw=2))
    p.append(arrow(480, 240, 400, 240, color=CLR_DATA, sw=2))
    p.append(text(440, 230, "Команди", size=10, bold=True, color=CLR_DATA))

    p.append(line(400, 290, 480, 290, color=CLR_WARN, sw=2))
    p.append(arrow(400, 290, 480, 290, color=CLR_WARN, sw=2))
    p.append(text(440, 280, "Телеметрія", size=10, bold=True, color=CLR_WARN))

    p.append(text(W / 2, 400, "Повна відсутність додаткових шлюзів: браузер безпосередньо з'єднується з бортовим комп'ютером через WebRTC.", size=11, bold=True, color=INK))

    render(os.path.join(OUT, "fpv-robotics-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_webrtc_stack()
    fig_ice_connectivity()
    fig_offer_answer()
    fig_dtls_srtp()
    fig_twcc_loop()
    fig_fpv_robotics()
    print("All figures generated successfully.")
