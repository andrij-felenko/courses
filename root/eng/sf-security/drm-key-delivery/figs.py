# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ENC  = "#c0392b"      # зашифроване / ключ
ENCF = "#fdecea"
CLR  = "#6b7280"      # службове / звичайне
CLRF = "#eef1f4"
OK   = "#27ae60"      # успіх / захищений контур
OKF  = "#eafaf0"
BLU  = "#2457d6"      # мережевий / логічний обмін
BLUF = "#eaf0fd"
PUR  = "#7e22ce"      # TEE / апаратний захист
PURF = "#f5f3ff"


# ── 1. eme-license-flow: повний шлях запиту та видачі ліцензії ───────────────
def fig_license_flow():
    W, H = 1080, 560
    p = []

    # 4 вертикальні колони компонентів
    # X1: 150 (Медіа / Demuxer)
    # X2: 390 (JavaScript / Додаток)
    # X3: 670 (CDM / TEE Анклав)
    # X4: 930 (DRM Проксі + Сервер Ліцензій)

    col_w = 200
    p.append(fitbox(50, 24, col_w, 48, "Медіаплеєр (Браузер)\nDemuxer / HTML5 Video", size=13, fill=CLRF, stroke=CLR, sw=1.6))
    p.append(fitbox(290, 24, col_w, 48, "Клієнтський код (JS)\nEME API / Мережа", size=13, fill=BLUF, stroke=BLU, sw=1.6))
    p.append(fitbox(570, 24, col_w, 48, "CDM / TEE\nАпаратний анклав", size=13, fill=PURF, stroke=PUR, sw=1.6))
    p.append(fitbox(830, 24, col_w, 48, "Сервер ліцензій\nDRM Proxy + KMS", size=13, fill=OKF, stroke=OK, sw=1.6))

    # Вертикальні пунктирні лінії життя
    for cx in (150, 390, 670, 930):
        p.append(line(cx, 80, cx, 520, color="#d1d5db", sw=1.4, dash="6 4"))

    # Крок 1: fMP4 містить pssh -> подія encrypted
    y1 = 115
    p.append(arrow(150, y1, 386, y1, color=CLR, sw=1.8))
    b, _, _ = textbox(270, y1 - 22, "1. Подія 'encrypted' (initData = PSSH)", size=12, fill="#ffffff", stroke=CLR, sw=1.2)
    p.append(b)

    # Крок 2: JS створює сесію -> generateRequest() -> CDM
    y2 = 180
    p.append(arrow(390, y2, 666, y2, color=BLU, sw=1.8))
    b, _, _ = textbox(530, y2 - 22, "2. generateRequest('cenc', initData)", size=12, fill="#ffffff", stroke=BLU, sw=1.2)
    p.append(b)

    # Внутрішня дія CDM: атестація, ephemeral key, підпис челенджу
    y3 = 238
    b, _, _ = textbox(670, y3, "Генерація Nonce + Ключа сесії\nПідпис сертифікатом пристрою (HW Root)", size=11, fill=PURF, stroke=PUR, sw=1.2)
    p.append(b)

    # Крок 3: CDM повертає License Challenge -> подія 'message' у JS
    y4 = 295
    p.append(arrow(670, y4, 394, y4, color=PUR, sw=1.8))
    b, _, _ = textbox(530, y4 - 22, "3. Подія 'message' (License Challenge blob)", size=12, fill="#ffffff", stroke=PUR, sw=1.2)
    p.append(b)

    # Крок 4: JS надсилає HTTPS POST із токеном авторизації
    y5 = 355
    p.append(arrow(390, y5, 926, y5, color=BLU, sw=1.8))
    b, _, _ = textbox(660, y5 - 22, "4. HTTPS POST /license (Challenge + JWT токен)", size=12, fill="#ffffff", stroke=BLU, sw=1.2)
    p.append(b)

    # Дія сервера: перевірка сертифіката, вилучення KID, запечатування ключа K
    y6 = 410
    b, _, _ = textbox(930, y6, "Перевірка прав + Політики (HDCP)\nЗагортання K_content під ключем сесії", size=11, fill=OKF, stroke=OK, sw=1.2)
    p.append(b)

    # Крок 5: Сервер повертає License Response -> JS
    y7 = 460
    p.append(arrow(930, y7, 394, y7, color=OK, sw=1.8))
    b, _, _ = textbox(660, y7 - 22, "5. License Response (зашифрований контейнер)", size=12, fill="#ffffff", stroke=OK, sw=1.2)
    p.append(b)

    # Крок 6: JS передає сесії update(license) -> CDM розгортає ключ у Secure Path
    y8 = 505
    p.append(arrow(390, y8, 666, y8, color=ENC, sw=2.0))
    b, _, _ = textbox(530, y8 - 22, "6. session.update(license) -> розгортання в TEE", size=12, fill="#ffffff", stroke=ENC, sw=1.4)
    p.append(b)

    render(os.path.join(OUT, "eme-license-flow.svg"), W, H, *p)


# ── 2. pssh-container-binding: бокс pssh та прив'язка до кількох DRM ──────────
def fig_pssh():
    W, H = 1060, 480
    p = []

    # Контейнерний рівень: fMP4 init segment (moov)
    p.append(fitbox(40, 30, 980, 70,
                    "Ініціалізаційний сегмент fMP4 (moov / trak / mdia / minf / stbl)\n"
                    "Один спільний ідентифікатор ключа: KID = 16 байтів у заголовку tenc",
                    size=14, fill=CLRF, stroke=CLR, sw=1.8))

    # Стрілки до трьох блоків PSSH
    p.append(arrow(200, 106, 200, 160, color=BLU, sw=1.8))
    p.append(arrow(530, 106, 530, 160, color=PUR, sw=1.8))
    p.append(arrow(860, 106, 860, 160, color=ENC, sw=1.8))

    # Блок 1: Widevine PSSH
    p.append(fitbox(40, 166, 310, 180,
                    "PSSH: Widevine\n"
                    "SystemID: edef8ba9-79d6-4ace...\n"
                    "KID: 0123...cdef\n"
                    "Data: Protocol Buffers\n"
                    "(provider, content_id, policy)",
                    size=12, fill=BLUF, stroke=BLU, sw=1.6))

    # Блок 2: PlayReady PSSH
    p.append(fitbox(375, 166, 310, 180,
                    "PSSH: PlayReady\n"
                    "SystemID: 9a04f079-9840-4286...\n"
                    "KID: 0123...cdef\n"
                    "Data: XML WRMHEADER\n"
                    "(LA_URL, DS_ID, checksum)",
                    size=12, fill=PURF, stroke=PUR, sw=1.6))

    # Блок 3: FairPlay PSSH / URI
    p.append(fitbox(710, 166, 310, 180,
                    "PSSH: FairPlay (або HLS URI)\n"
                    "SystemID: 94ce86fb-07ff-4f43...\n"
                    "KID: 0123...cdef\n"
                    "Data: SKD URI\n"
                    "(skd://fps.key.service/id)",
                    size=12, fill=ENCF, stroke=ENC, sw=1.6))

    # Загальний висновок унизу: єдиний зашифрований потік
    p.append(fitbox(40, 385, 980, 68,
                    "Результат: різні CDM вилучають свій PSSH-блок і роблять власний запит,\n"
                    "але отримують один і той самий 128-бітний ключ K_content для однакових кадрів",
                    size=13, fill=OKF, stroke=OK, sw=1.8))

    render(os.path.join(OUT, "pssh-container-binding.svg"), W, H, *p)


# ── 3. tee-secure-video-path: звичайний світ проти безпечного світу ───────────
def fig_secure_path():
    W, H = 1060, 520
    p = []

    # Ліва половина: Normal World (Rich OS / Браузер) (30..480)
    p.append(rect(30, 30, 450, 450, fill="#f8fafc", stroke=CLR, sw=1.8, rx=8))
    p.append(text(255, 62, "Звичайний світ (Normal World / Rich OS)", size=14, bold=True, color=CLR))

    # Компоненти у звичайному світі
    p.append(fitbox(50, 90, 410, 56, "Браузер / Додаток (JS Heap)\nМає лише зашифрований fMP4 та Challenge", size=12, fill=CLRF, stroke=CLR))
    p.append(fitbox(50, 170, 410, 56, "Ядро ОС (Linux / Windows / Android)\nНе має доступу до захищених регістрів", size=12, fill=CLRF, stroke=CLR))
    p.append(fitbox(50, 250, 410, 80, "Звичайна оперативна пам'ять (Host RAM)\nТут лежать лише зашифровані пакети NAL.\nКлючі у відкритому вигляді сюди не потрапляють.", size=12, fill=ENCF, stroke=ENC, sw=1.4))

    # Межа апаратної ізоляції (TrustZone / MMU Firewall)
    p.append(line(530, 30, 530, 200, color=PUR, sw=2.2, dash="8 6"))
    b, _, _ = textbox(530, 255, "Апаратна\nмежа TZASC\nFirewall", size=11, fill="#ffffff", stroke=PUR, sw=1.4, color=PUR)
    p.append(b)
    p.append(line(530, 310, 530, 480, color=PUR, sw=2.2, dash="8 6"))

    # Права половина: Secure World (TEE / SVP) (580..1030)
    p.append(rect(580, 30, 450, 450, fill=PURF, stroke=PUR, sw=1.8, rx=8))
    p.append(text(805, 62, "Безпечний світ (Secure World / TEE)", size=14, bold=True, color=PUR))

    p.append(fitbox(600, 90, 410, 56, "Crypto Engine + OTP eFuses\nАпаратний корінь довіри (Root Key)", size=12, fill="#ffffff", stroke=PUR))
    p.append(fitbox(600, 170, 410, 60, "Дешифратор AES-128 (вбудовані регістри)\nКлюч K_content завантажується лише в регістри кремнію", size=12, fill=OKF, stroke=OK))
    p.append(fitbox(600, 250, 410, 60, "Захищена відеопам'ять (Protected RAM)\nДекодовані кадри YUV доступні лише VPU", size=12, fill=OKF, stroke=OK))
    p.append(fitbox(600, 330, 410, 60, "Контролер дисплея + HDCP 2.2 передавач\nШифрування сигналу перед виходом на HDMI", size=12, fill=BLUF, stroke=BLU))

    # Стрілка передачі захищеного сигналу
    p.append(arrow(805, 148, 805, 168, color=PUR, sw=1.8))
    p.append(arrow(805, 232, 805, 248, color=OK, sw=1.8))
    p.append(arrow(805, 312, 805, 328, color=BLU, sw=1.8))

    # Стрілка подачі зашифрованих даних через межу
    p.append(arrow(462, 380, 598, 200, color=ENC, sw=2.0))

    render(os.path.join(OUT, "tee-secure-video-path.svg"), W, H, *p)


# ── 4. key-envelope-hierarchy: ієрархія криптографічного загортання ───────────
def fig_key_hierarchy():
    W, H = 1060, 450
    p = []

    # Рівень 1: Апаратний корінь (eFuse)
    p.append(fitbox(40, 40, 220, 110,
                    "Рівень 0: Кремній\n"
                    "Root Key (eFuse)\n"
                    "Зашитий на заводі,\n"
                    "недоступний ПЗ",
                    size=12, fill=PURF, stroke=PUR, sw=1.8))

    p.append(arrow(264, 95, 306, 95, color=PUR, sw=2))

    # Рівень 2: Приватний ключ пристрою / сертифікат
    p.append(fitbox(310, 40, 220, 110,
                    "Рівень 1: Пристрій\n"
                    "Device Private Key\n"
                    "Підписаний вендором,\n"
                    "доводить рівень захисту",
                    size=12, fill=BLUF, stroke=BLU, sw=1.8))

    p.append(arrow(534, 95, 576, 95, color=BLU, sw=2))

    # Рівень 3: Тимчасовий сесійний ключ (Key Wrapping)
    p.append(fitbox(580, 40, 210, 110,
                    "Рівень 2: Сесія\n"
                    "Session Key (K_sess)\n"
                    "Узгоджується на\n"
                    "один запит ліцензії",
                    size=12, fill=OKF, stroke=OK, sw=1.8))

    p.append(arrow(794, 95, 836, 95, color=OK, sw=2))

    # Рівень 4: Ключ контенту (AES-128)
    p.append(fitbox(840, 40, 180, 110,
                    "Рівень 3: Медіа\n"
                    "Content Key (K_c)\n"
                    "Розшифровує кадри\n"
                    "в Secure Path",
                    size=12, fill=ENCF, stroke=ENC, sw=2))

    # Пояснювальний блок унизу
    p.append(fitbox(40, 200, 980, 200,
                    "Криптографічний конверт ліцензії:\n"
                    "1. Клієнт генерує ефемерну пару ключів і підписує запит ключем Device Private Key.\n"
                    "2. Сервер перевіряє сертифікат пристрою та узгоджує ключ сесії K_sess.\n"
                    "3. Сервер загортає симетричний ключ контенту K_c алгоритмом AES-KW під ключем K_sess.\n"
                    "4. Анклав TEE розгортає K_sess за допомогою свого приватного ключа, а потім видобуває K_c.\n"
                    "Жоден ключ ні на мить не з'являється у відкритому вигляді в оперативній пам'яті хоста.",
                    size=13, fill="#ffffff", stroke=CLR, sw=1.6))

    render(os.path.join(OUT, "key-envelope-hierarchy.svg"), W, H, *p)


if __name__ == "__main__":
    fig_license_flow()
    fig_pssh()
    fig_secure_path()
    fig_key_hierarchy()
    print("All figures generated successfully.")
