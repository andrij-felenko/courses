# -*- coding: utf-8 -*-
"""figs.py — генератор ілюстрацій для теми cmaf (Common Media Application Format).
Створює SVG-фігури за стандартом репозиторію через svgkit.
"""

import sys
import os

# scripts/ лежить на 4 рівні вище: book/communications/protocols/cmaf -> scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")


def fig_cmaf_hierarchy():
    """Ієрархія сутностей моделі CMAF (ISO/IEC 23000-19)."""
    W, H = 880, 480
    p = []

    # Тло
    p.append(rect(0, 0, W, H, fill=BG, stroke=BG))

    # Рівень 1: CMAF Presentation
    p.append(rect(30, 20, 820, 70, fill="#f8fafc", stroke="#64748b", sw=2, rx=8))
    p.append(text(440, 45, "CMAF Presentation (Повний медіапоказ)", size=16, color=INK, bold=True))
    p.append(text(440, 70, "Описує весь сеанс: узгоджена часова шкала, вибір мов, якісні драбини, субтитри", size=12, color=MUTED))

    # Стрілки від Presentation до Selection Sets
    p.append(arrow(220, 90, 220, 120, color="#64748b", sw=1.5))
    p.append(arrow(440, 90, 440, 120, color="#64748b", sw=1.5))
    p.append(arrow(660, 90, 660, 120, color="#64748b", sw=1.5))

    # Рівень 2: Selection Sets
    p.append(rect(30, 120, 360, 75, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(210, 145, "Video Selection Set", size=14, color=NEG, bold=True))
    p.append(text(210, 168, "Альтернативні відеопотоки (ракурси, кодеки)", size=11, color=MUTED))

    p.append(rect(410, 120, 230, 75, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(525, 145, "Audio Selection Set", size=14, color=FIELD, bold=True))
    p.append(text(525, 168, "Мовні доріжки (UKR, ENG, 5.1)", size=11, color=MUTED))

    p.append(rect(660, 120, 190, 75, fill="#fefce8", stroke="#ca8a04", sw=1.8, rx=6))
    p.append(text(755, 145, "Subtitle Set", size=14, color="#a16207", bold=True))
    p.append(text(755, 168, "Субтитри (WebVTT / TTML)", size=11, color=MUTED))

    # Стрілка від Video Selection Set до Switching Set
    p.append(arrow(210, 195, 210, 225, color=NEG, sw=1.5))

    # Рівень 3: CMAF Switching Set
    p.append(rect(30, 225, 500, 80, fill="#f5f3ff", stroke="#7c3aed", sw=1.8, rx=6))
    p.append(text(280, 250, "CMAF Switching Set (Адаптивна драбина бітрейтів)", size=14, color="#6d28d9", bold=True))
    p.append(text(280, 272, "Доріжки з ідентичним часовим вирівнюванням точок розрізу (GOP/SAP)", size=11, color=MUTED))
    p.append(text(280, 292, "Клієнт перемикає якість на межі будь-якого фрагмента без артефактів", size=11, color=MUTED))

    # Стрілки до доріжок Tracks
    p.append(arrow(110, 305, 110, 335, color="#7c3aed", sw=1.5))
    p.append(arrow(280, 305, 280, 335, color="#7c3aed", sw=1.5))
    p.append(arrow(450, 305, 450, 335, color="#7c3aed", sw=1.5))

    # Рівень 4: CMAF Tracks
    p.append(rect(30, 335, 160, 55, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(110, 357, "Track 1: 1080p", size=13, color=INK, bold=True))
    p.append(text(110, 377, "AVC/H.264 5.0 Mbps", size=10, color=MUTED))

    p.append(rect(200, 335, 160, 55, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(280, 357, "Track 2: 720p", size=13, color=INK, bold=True))
    p.append(text(280, 377, "AVC/H.264 2.5 Mbps", size=10, color=MUTED))

    p.append(rect(370, 335, 160, 55, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(450, 357, "Track 3: 480p", size=13, color=INK, bold=True))
    p.append(text(450, 377, "AVC/H.264 1.1 Mbps", size=10, color=MUTED))

    # Рівень 5: Адресовні сутності окремого Track (Track 1)
    p.append(line(110, 390, 110, 415, color=LINE, sw=1.5))
    p.append(arrow(110, 415, 140, 435, color=LINE, sw=1.5))

    p.append(rect(140, 410, 150, 50, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=5))
    p.append(text(215, 430, "CMAF Header", size=12, color="#3730a3", bold=True))
    p.append(text(215, 448, "init.mp4 (ftyp + moov)", size=10, color=MUTED))

    p.append(arrow(290, 435, 320, 435, color=LINE, sw=1.5))

    p.append(rect(320, 410, 165, 50, fill="#fce7f3", stroke="#db2777", sw=1.5, rx=5))
    p.append(text(402, 430, "CMAF Segment 1", size=12, color="#9d174d", bold=True))
    p.append(text(402, 448, "seg-1.m4s (styp + moof + mdat)", size=9, color=MUTED))

    p.append(arrow(485, 435, 515, 435, color=LINE, sw=1.5))

    p.append(rect(515, 410, 165, 50, fill="#fce7f3", stroke="#db2777", sw=1.5, rx=5))
    p.append(text(597, 430, "CMAF Segment 2", size=12, color="#9d174d", bold=True))
    p.append(text(597, 448, "seg-2.m4s (styp + moof + mdat)", size=9, color=MUTED))

    p.append(text(720, 438, "… і далі у часі", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, "cmaf-hierarchy.svg"), W, H, *p)


def fig_cmaf_fmp4_chunk():
    """Анатомія сегмента fMP4 та розбиття на CMAF Chunks для Chunked Transfer Encoding."""
    W, H = 920, 460
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke=BG))

    # Секція 1: CMAF Header (Ініціалізаційний сегмент)
    p.append(rect(20, 20, 880, 95, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=6))
    p.append(text(460, 42, "CMAF Header (Ініціалізаційний сегмент: init.mp4)", size=14, color=INK, bold=True))

    p.append(rect(40, 55, 120, 45, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=4))
    p.append(text(100, 75, "ftyp", size=12, color=INK, bold=True))
    p.append(text(100, 90, "brand: cmfc", size=9, color=MUTED))

    p.append(rect(170, 55, 710, 45, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=4))
    p.append(text(525, 74, "moov (Метадані треку та кодека: mvhd, trak, mdia, minf, stbl [stsd], mvex [trex])", size=12, color="#0369a1", bold=True))
    p.append(text(525, 90, "Не містить жодного медіасемплу; завантажується клієнтом один раз на початку сеансу", size=10, color=MUTED))

    # Секція 2: CMAF Media Segment (Повний 2- або 6-секундний сегмент seg-001.m4s)
    p.append(rect(20, 135, 880, 160, fill="#faf5ff", stroke="#9333ea", sw=1.8, rx=6))
    p.append(text(460, 158, "CMAF Media Segment (seg-001.m4s) — поділений на 3 CMAF Chunks по 660 мс", size=14, color="#7e22ce", bold=True))

    # styp box
    p.append(rect(35, 175, 75, 105, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=4))
    p.append(text(72, 225, "styp", size=12, color=INK, bold=True))
    p.append(text(72, 245, "cmfs", size=10, color=MUTED))

    # Chunk 1 (IDR)
    p.append(rect(120, 175, 240, 105, fill="#fef2f2", stroke=POS, sw=1.5, rx=5))
    p.append(text(240, 195, "CMAF Chunk 1 (Ключовий)", size=12, color=POS, bold=True))
    p.append(rect(130, 205, 105, 65, fill="#fee2e2", stroke=POS, sw=1, rx=3))
    p.append(text(182, 225, "moof", size=11, color=POS, bold=True))
    p.append(text(182, 242, "mfhd, traf", size=9, color=MUTED))
    p.append(text(182, 258, "tfdt, trun", size=9, color=MUTED))
    p.append(rect(245, 205, 105, 65, fill="#fee2e2", stroke=POS, sw=1, rx=3))
    p.append(text(297, 225, "mdat", size=11, color=POS, bold=True))
    p.append(text(297, 243, "IDR NAL-кадр", size=9, color=INK))
    p.append(text(297, 258, "+ P-кадри", size=9, color=MUTED))

    # Chunk 2
    p.append(rect(370, 175, 240, 105, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(490, 195, "CMAF Chunk 2", size=12, color=FIELD, bold=True))
    p.append(rect(380, 205, 105, 65, fill="#dcfce7", stroke=FIELD, sw=1, rx=3))
    p.append(text(432, 225, "moof", size=11, color=FIELD, bold=True))
    p.append(text(432, 242, "mfhd, traf", size=9, color=MUTED))
    p.append(text(432, 258, "tfdt, trun", size=9, color=MUTED))
    p.append(rect(495, 205, 105, 65, fill="#dcfce7", stroke=FIELD, sw=1, rx=3))
    p.append(text(547, 225, "mdat", size=11, color=FIELD, bold=True))
    p.append(text(547, 245, "P / B кадри", size=10, color=INK))

    # Chunk 3
    p.append(rect(620, 175, 240, 105, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(740, 195, "CMAF Chunk 3", size=12, color=FIELD, bold=True))
    p.append(rect(630, 205, 105, 65, fill="#dcfce7", stroke=FIELD, sw=1, rx=3))
    p.append(text(682, 225, "moof", size=11, color=FIELD, bold=True))
    p.append(text(682, 242, "mfhd, traf", size=9, color=MUTED))
    p.append(text(682, 258, "tfdt, trun", size=9, color=MUTED))
    p.append(rect(745, 205, 105, 65, fill="#dcfce7", stroke=FIELD, sw=1, rx=3))
    p.append(text(797, 225, "mdat", size=11, color=FIELD, bold=True))
    p.append(text(797, 245, "P / B кадри", size=10, color=INK))

    # Секція 3: Потокова передача через HTTP Chunked Transfer Encoding (CTE)
    p.append(rect(20, 315, 880, 125, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(460, 338, "HTTP Chunked Transfer Encoding (LL-DASH / LL-HLS) — прогресивна видача без очікування кінця сегмента", size=13, color=NEG, bold=True))

    p.append(arrow(240, 280, 240, 355, color=POS, sw=1.8))
    p.append(rect(140, 358, 200, 65, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(240, 380, "HTTP Chunk 1 (0.66s)", size=11, color=POS, bold=True))
    p.append(text(240, 398, "Негайно летить у CDN і плеєр", size=9, color=MUTED))
    p.append(text(240, 412, "Плеєр уже декодує кадри", size=9, color=POS))

    p.append(arrow(490, 280, 490, 355, color=FIELD, sw=1.8))
    p.append(rect(390, 358, 200, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(490, 380, "HTTP Chunk 2 (1.33s)", size=11, color=FIELD, bold=True))
    p.append(text(490, 398, "Доливається тим самим з'єднанням", size=9, color=MUTED))
    p.append(text(490, 412, "Затримка: 1–2 секунди від камери", size=9, color=FIELD))

    p.append(arrow(740, 280, 740, 355, color=FIELD, sw=1.8))
    p.append(rect(640, 358, 200, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(740, 380, "HTTP Chunk 3 (2.00s)", size=11, color=FIELD, bold=True))
    p.append(text(740, 398, "Завершує сегмент (0-chunk trailer)", size=9, color=MUTED))
    p.append(text(740, 412, "Кеш CDN фіксує повний .m4s", size=9, color=INK))

    render(os.path.join(IMG, "cmaf-fmp4-chunk.svg"), W, H, *p)


def fig_unified_cdn_architecture():
    """Єдина архітектура сховища та CDN для одночасної роздачі на HLS і DASH."""
    W, H = 900, 450
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke=BG))

    # Ліва частина: Кодувальник / Пакувальник
    p.append(rect(20, 30, 230, 390, fill="#f8fafc", stroke="#475569", sw=1.8, rx=6))
    p.append(text(135, 60, "CMAF Пакувальник", size=15, color=INK, bold=True))
    p.append(text(135, 82, "Одне кодування відео", size=11, color=MUTED))

    p.append(rect(35, 110, 200, 110, fill="#eff6ff", stroke=NEG, sw=1.5, rx=5))
    p.append(text(135, 135, "Один набір медіафайлів", size=12, color=NEG, bold=True))
    p.append(text(135, 158, "init.mp4 (CMAF Header)", size=11, color=INK))
    p.append(text(135, 180, "seg-1.m4s, seg-2.m4s …", size=11, color=INK))
    p.append(text(135, 202, "(Спільні fMP4 байти)", size=10, color=MUTED))

    p.append(rect(35, 240, 200, 75, fill="#fefce8", stroke="#ca8a04", sw=1.5, rx=5))
    p.append(text(135, 265, "Маніфест HLS", size=12, color="#a16207", bold=True))
    p.append(text(135, 285, "master.m3u8 / index.m3u8", size=10, color=MUTED))
    p.append(text(135, 300, "#EXT-X-MAP:URI=\"init.mp4\"", size=9, color="#a16207"))

    p.append(rect(35, 325, 200, 75, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=5))
    p.append(text(135, 350, "Маніфест DASH", size=12, color=FIELD, bold=True))
    p.append(text(135, 370, "manifest.mpd (XML)", size=10, color=MUTED))
    p.append(text(135, 385, "<Initialization sourceURL=\"init.mp4\"/>", size=9, color=FIELD))

    # Стрілки в CDN
    p.append(arrow(250, 165, 310, 165, color=NEG, sw=2))
    p.append(arrow(250, 275, 310, 275, color="#ca8a04", sw=1.5))
    p.append(arrow(250, 360, 310, 360, color=FIELD, sw=1.5))

    # Середня частина: Сховище Origin та Вузол роздачі (CDN Edge Cache)
    p.append(rect(310, 30, 280, 390, fill="#fdf4ff", stroke="#a21caf", sw=2, rx=8))
    p.append(text(450, 60, "CDN Кеш та Сховище", size=15, color="#86198f", bold=True))
    p.append(text(450, 82, "100% спільне використання кешу", size=11, color=MUTED))

    p.append(rect(325, 110, 250, 120, fill="#ffffff", stroke="#a21caf", sw=1.5, rx=6))
    p.append(text(450, 135, "Кеш медіасегментів (99% трафіку)", size=12, color="#86198f", bold=True))
    p.append(text(450, 160, "GET /video/1080p/init.mp4", size=10, color=INK))
    p.append(text(450, 182, "GET /video/1080p/seg-100.m4s", size=10, color=INK))
    p.append(text(450, 205, "Один кеш-хіт для обох екосистем!", size=10, color=FIELD, bold=True))

    p.append(rect(325, 245, 250, 155, fill="#ffffff", stroke="#64748b", sw=1.2, rx=6))
    p.append(text(450, 270, "Легковагі текстові маніфести", size=11, color=INK, bold=True))
    p.append(text(450, 292, "master.m3u8 (кілька КБ)", size=10, color="#a16207"))
    p.append(text(450, 312, "manifest.mpd (кілька КБ)", size=10, color=FIELD))
    p.append(text(450, 335, "Обидва посилаються на ті самі", size=10, color=MUTED))
    p.append(text(450, 355, "відносні URL-адреси .m4s", size=10, color=MUTED))
    p.append(text(450, 375, "Економія сховища: 50%", size=11, color=POS, bold=True))

    # Стрілки з CDN до клієнтів
    p.append(arrow(590, 180, 660, 140, color=NEG, sw=2))
    p.append(arrow(590, 290, 660, 165, color="#ca8a04", sw=1.5))

    p.append(arrow(590, 210, 660, 310, color=NEG, sw=2))
    p.append(arrow(590, 330, 660, 335, color=FIELD, sw=1.5))

    # Права частина: Клієнтські платформи
    # Apple HLS
    p.append(rect(660, 70, 220, 150, fill="#fefce8", stroke="#ca8a04", sw=1.8, rx=6))
    p.append(text(770, 95, "Apple Екосистема (HLS)", size=14, color="#a16207", bold=True))
    p.append(text(770, 118, "iOS, iPadOS, macOS, Safari, tvOS", size=10, color=MUTED))
    p.append(text(770, 145, "1. Читає master.m3u8", size=11, color=INK))
    p.append(text(770, 168, "2. Завантажує init.mp4", size=11, color=INK))
    p.append(text(770, 190, "3. Качає seg-1.m4s (fMP4)", size=11, color=NEG, bold=True))

    # DASH Ecosystem
    p.append(rect(660, 250, 220, 150, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(770, 275, "DASH / Інші плеєри", size=14, color=FIELD, bold=True))
    p.append(text(770, 298, "Android, Chrome, Smart TV, Web", size=10, color=MUTED))
    p.append(text(770, 325, "1. Читає manifest.mpd", size=11, color=INK))
    p.append(text(770, 348, "2. Завантажує init.mp4", size=11, color=INK))
    p.append(text(770, 370, "3. Качає той самий seg-1.m4s!", size=11, color=NEG, bold=True))

    render(os.path.join(IMG, "unified-cdn-architecture.svg"), W, H, *p)


def fig_cenc_encryption_schemes():
    """Спільне шифрування CENC: повноблочний cenc (AES-CTR) проти cbcs (AES-CBC 1:9 pattern)."""
    W, H = 880, 420
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke=BG))

    p.append(text(440, 30, "Схеми шифрування Common Encryption (CENC / ISO/IEC 23001-7) у CMAF", size=15, color=INK, bold=True))

    # Верхня частина: Схема 'cenc' (AES-CTR 100%)
    p.append(rect(30, 55, 820, 155, fill="#f8fafc", stroke=NEG, sw=1.8, rx=6))
    p.append(text(180, 80, "Схема 'cenc' — AES-128 CTR", size=14, color=NEG, bold=True))
    p.append(text(540, 80, "(Історично: Microsoft PlayReady, Widevine Modular)", size=11, color=MUTED))
    p.append(text(440, 100, "100% корисного навантаження NAL-юніта шифрується лічильниковим режимом (Counter Mode)", size=11, color=INK))

    # Блоки cenc
    p.append(rect(50, 120, 100, 45, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=3))
    p.append(text(100, 138, "NAL Header", size=11, color=INK, bold=True))
    p.append(text(100, 153, "Відкритий (Clear)", size=9, color=MUTED))

    for i in range(6):
        bx = 160 + i * 110
        p.append(rect(bx, 120, 100, 45, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
        p.append(text(bx + 50, 138, f"Block {i+1} (16B)", size=10, color=POS, bold=True))
        p.append(text(bx + 50, 153, "AES-CTR", size=9, color=POS))

    p.append(text(440, 192, "Шифрується кожен 16-байтний блок без пропусків. Не підтримується апаратними рушіями Apple.", size=11, color=POS))

    # Нижня частина: Схема 'cbcs' (AES-CBC 10% pattern)
    p.append(rect(30, 230, 820, 165, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(210, 255, "Схема 'cbcs' — AES-128 CBC (1:9 Pattern Protection)", size=14, color=FIELD, bold=True))
    p.append(text(600, 255, "(Універсальний стандарт: Apple FairPlay, Widevine, PlayReady)", size=11, color=MUTED))
    p.append(text(440, 275, "Патерн 1:9 — шифрується лише 1 блок з 10 (16 байтів шифровано : 144 байти відкрито)", size=11, color=INK))

    # Блоки cbcs
    p.append(rect(50, 295, 100, 45, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=3))
    p.append(text(100, 313, "NAL Header", size=11, color=INK, bold=True))
    p.append(text(100, 328, "Відкритий (Clear)", size=9, color=MUTED))

    # Патерн 1 encrypted, потім кілька skip
    p.append(rect(160, 295, 120, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(text(220, 313, "Crypt Block 1", size=10, color=POS, bold=True))
    p.append(text(220, 328, "16B AES-CBC", size=9, color=POS))

    p.append(rect(290, 295, 380, 45, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(480, 313, "Skip Blocks 1..9 (144 байти відкритого відеопотоку)", size=11, color=FIELD, bold=True))
    p.append(text(480, 328, "Пропускаються без криптографічних операцій (збереження енергії ЦП/GPU)", size=9, color=MUTED))

    p.append(rect(680, 295, 120, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(text(740, 313, "Crypt Block 2", size=10, color=POS, bold=True))
    p.append(text(740, 328, "16B AES-CBC", size=9, color=POS))

    p.append(text(440, 372, "Ентропія відео повністю зламана (картинка не декодується), але навантаження на крипточип менше на 90%!", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "cenc-encryption-schemes.svg"), W, H, *p)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    fig_cmaf_hierarchy()
    fig_cmaf_fmp4_chunk()
    fig_unified_cdn_architecture()
    fig_cenc_encryption_schemes()
