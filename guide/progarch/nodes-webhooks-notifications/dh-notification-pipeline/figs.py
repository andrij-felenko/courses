# -*- coding: utf-8 -*-
"""Фігури до кроку «Конвеєр сповіщень DH».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREENBG = "#eafaf0"
REDBG   = "#fdecea"
BLUEBG  = "#eaf0fd"
GREY    = "#e5e7eb"
YELLOWBG = "#fef9e7"


# ───────── Фіг. 1: П'ятиетапний конвеєр сповіщень ─────────
def fig_pipeline_architecture():
    W, H = 1180, 520
    f = []

    # Верхня пріоритетна смуга для критичного класу
    f.append(fitbox(50, 40, 1080, 44,
                    "Критичний клас (пожежа · злом · вода) — оминає злиття та throttling, виходить на пріоритетний розгорт",
                    size=13, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=2))

    # Вхідні події
    f.append(fitbox(50, 140, 170, 240,
                    "Вхідні події\n\n• Камери (рух)\n• Замки (стан)\n• Датчики диму\n• Системні поновлення\n\n[home_id partition]",
                    size=12, fill=FILL, stroke=INK, color=INK, sw=1.6))

    # 5 етапів
    f.append(arrow(220, 260, 255, 260, color=MUTED, sw=1.8))
    f.append(fitbox(260, 140, 165, 240,
                    "① INGEST\n& QUEUE\n\n- Черга задач\n- Гарантія порядку\n- Outbox pattern\n- Persisted log",
                    size=12, fill=FILL, stroke=FIELD, color=FIELD, bold=True, sw=1.6))

    f.append(arrow(425, 260, 460, 260, color=MUTED, sw=1.8))
    f.append(fitbox(465, 140, 165, 240,
                    "② DEDUP &\nTHROTTLE\n\n- Hash ключа\n- Deduplication TTL\n- Coalesce window\n- Token bucket",
                    size=12, fill=FILL, stroke=POS, color=POS, bold=True, sw=1.6))

    f.append(arrow(630, 260, 665, 260, color=MUTED, sw=1.8))
    f.append(fitbox(670, 140, 165, 240,
                    "③ POLICY &\nPREFERENCES\n\n- Матриця прав\n- Home / Away\n- Quiet hours\n- User opt-out",
                    size=12, fill=FILL, stroke=NEG, color=NEG, bold=True, sw=1.6))

    f.append(arrow(835, 260, 870, 260, color=MUTED, sw=1.8))
    f.append(fitbox(875, 140, 165, 240,
                    "④ ROUTER &\nFAN-OUT\n\n- Multi-device\n- Critical push\n- Silent push\n- SMS / Voice",
                    size=12, fill=FILL, stroke=FIELD, color=FIELD, bold=True, sw=1.6))

    f.append(arrow(1040, 260, 1075, 260, color=MUTED, sw=1.8))

    # Вихід
    f.append(fitbox(50, 410, 1080, 75,
                    "⑤ DELIVERY TRACKING & FALLBACK: Відстеження ACK від APNs/FCM → 15с таймаут → Ескалація в SMS/Voice → DLQ при збоях",
                    size=13, fill=BLUEBG, stroke=INK, color=INK, bold=True, sw=1.8))

    render(os.path.join(IMG, "pipeline-architecture.svg"), W, H, *f,
           title="П'ятиетапний конвеєр сповіщень Digital Homes")


# ───────── Фіг. 2: Двоточковий імпульс (Silent Push + Critical Push) ─────────
def fig_dual_payload_sequence():
    W, H = 1080, 500
    f = []

    # Осі систем
    f.append(text(120, 45, "Камера / Хаб", size=13, bold=True, color=INK))
    f.append(line(120, 65, 120, 420, color=MUTED, sw=1.4, dash="4,4"))

    f.append(text(380, 45, "Конвеєр DH", size=13, bold=True, color=FIELD))
    f.append(line(380, 65, 380, 420, color=FIELD, sw=1.4, dash="4,4"))

    f.append(text(640, 45, "APNs / FCM (Push Cloud)", size=13, bold=True, color=POS))
    f.append(line(640, 65, 640, 420, color=POS, sw=1.4, dash="4,4"))

    f.append(text(920, 45, "Мобільний застосунок", size=13, bold=True, color=NEG))
    f.append(line(920, 65, 920, 420, color=NEG, sw=1.4, dash="4,4"))

    # Покрокові стрілки
    # 1. Подія
    f.append(arrow(120, 100, 380, 100, color=INK, sw=1.6))
    f.append(text(250, 90, "1. motion_detected (event_id)", size=11, color=INK))

    # 2. Silent Push
    f.append(arrow(380, 140, 640, 140, color=FIELD, sw=1.6))
    f.append(text(510, 130, "2a. Silent / Data Push (content-available=1)", size=11, color=FIELD))

    f.append(arrow(640, 170, 920, 170, color=FIELD, sw=1.6))
    f.append(text(780, 160, "Фонове пробудження OS", size=11, color=FIELD))

    # 3. Фоновий синк
    f.append(arrow(920, 210, 120, 210, color=NEG, sw=1.6))
    f.append(text(520, 200, "3. Фоновий синк кадру камери (200 мс кеш у RAM)", size=11, color=NEG, bold=True))

    # 4. Critical Alert Push
    f.append(arrow(380, 260, 640, 260, color=POS, sw=1.6))
    f.append(text(510, 250, "2b. Critical Alert Push (sound, rich_id)", size=11, color=POS))

    f.append(arrow(640, 290, 920, 290, color=POS, sw=1.6))
    f.append(text(780, 280, "4. Гучний звук + Багатий екран", size=11, color=POS))

    # 5. Клік у Live
    f.append(arrow(920, 350, 120, 350, color=INK, sw=1.8))
    f.append(text(520, 340, "5. Deep Link dh://live — миттєвий показу з кешу (0 мс лаг)", size=12, color=FIELD, bold=True))

    # Нижній банер
    f.append(fitbox(60, 440, 960, 44,
                    "Silent Push будить застосунок і завантажує відеозріз ДО того, як користувач торкнеться сповіщення",
                    size=13, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=1.8))

    render(os.path.join(IMG, "dual-payload-sequence.svg"), W, H, *f,
           title="Двоточковий імпульс пробудження: Silent Push + Critical Alert")


# ───────── Фіг. 3: Канальний каскад та аварійний fallback ─────────
def fig_channel_fallback_ladder():
    W, H = 1080, 440
    f = []

    # Сходинки
    f.append(fitbox(60, 50, 280, 110,
                    "РІВЕНЬ 1: Primary Push\n\n• APNs Critical Alert\n• FCM High Priority\n• SLA < 1с | Вартість $0",
                    size=12, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=1.8))

    f.append(arrow(340, 105, 410, 105, color=MUTED, sw=1.8))
    f.append(fitbox(410, 75, 140, 60, "Відстеження ACK\n(таймаут 15 с)",
                    size=11, fill=YELLOWBG, stroke=POS, color=POS, bold=True, sw=1.4))
    f.append(arrow(550, 105, 620, 105, color=POS, sw=1.8))
    f.append(text(585, 95, "Немає ACK", size=11, color=POS, bold=True))

    f.append(fitbox(620, 50, 280, 110,
                    "РІВЕНЬ 2: SMS Fallback\n\n• Twilio / SMS Gateway\n• Прямий номер мешканця\n• SLA < 5с | Вартість $0.03",
                    size=12, fill=YELLOWBG, stroke=POS, color=POS, bold=True, sw=1.8))

    f.append(arrow(760, 160, 760, 210, color=MUTED, sw=1.8))
    f.append(text(840, 185, "Сплачено / Помилка", size=11, color=NEG))

    f.append(fitbox(620, 210, 280, 110,
                    "РІВЕНЬ 3: Automated Voice Call\n\n• Автоматичний виклик\n• Синтез TTS («Тривога в домі!»)\n• SLA < 10с | Вартість $0.10",
                    size=12, fill=REDBG, stroke=NEG, color=NEG, bold=True, sw=1.8))

    # Локальний паралельний шлях
    f.append(line(200, 160, 200, 265, color=FIELD, sw=1.8))
    f.append(arrow(200, 265, 260, 265, color=FIELD, sw=1.8))
    f.append(fitbox(260, 210, 280, 110,
                    "ПАРАЛЕЛЬНО: In-Home Siren\n\n• Локальний хаб / Сирена\n• Zigbee / Matter локально\n• Незалежно від інтернет-каналу",
                    size=12, fill=BLUEBG, stroke=INK, color=INK, bold=True, sw=1.8))

    # Банер
    f.append(fitbox(60, 360, 960, 50,
                    "Автоматичне ескалювання гарантує доставку тривоги навіть при повній відсутності інтернету на мобільному мешканця",
                    size=13, fill=FILL, stroke=INK, color=INK, bold=True, sw=1.6))

    render(os.path.join(IMG, "channel-fallback-ladder.svg"), W, H, *f,
           title="Канальний каскад та аварійне ескалювання")


# ───────── Фіг. 4: Дерево прийняття рішень Policy Engine ─────────
def fig_policy_decision_matrix():
    W, H = 1080, 480
    f = []

    f.append(fitbox(50, 180, 180, 120,
                    "Вхідна подія:\n• Клас критичності\n• home_id\n• user_id",
                    size=12, fill=FILL, stroke=INK, color=INK, sw=1.6))

    f.append(arrow(230, 240, 280, 240, color=MUTED, sw=1.8))

    # Питання 1
    f.append(fitbox(280, 180, 190, 120,
                    "Критична тривога?\n(Critical Alert)",
                    size=12, fill=BLUEBG, stroke=INK, color=INK, bold=True, sw=1.6))

    # Гілка ТАК (Критична)
    f.append(arrow(375, 180, 375, 90, color=FIELD, sw=1.8))
    f.append(text(390, 130, "ТАК", size=11, color=FIELD, bold=True))
    f.append(fitbox(280, 40, 520, 50,
                    "НЕГАЙНА ДОСТАВКА в обхід Quiet Hours, DND та Opt-Out",
                    size=13, fill=GREENBG, stroke=FIELD, color=FIELD, bold=True, sw=2))

    # Гілка НІ
    f.append(arrow(470, 240, 520, 240, color=MUTED, sw=1.8))
    f.append(text(495, 225, "НІ", size=11, color=MUTED, bold=True))

    # Питання 2
    f.append(fitbox(520, 180, 190, 120,
                    "Явний Opt-Out\nкористувача?",
                    size=12, fill=YELLOWBG, stroke=POS, color=POS, bold=True, sw=1.6))

    # Гілка ТАК (Opt-Out)
    f.append(arrow(615, 180, 615, 90, color=POS, sw=1.8))
    f.append(text(630, 130, "ТАК", size=11, color=POS, bold=True))
    f.append(fitbox(820, 40, 210, 50,
                    "ВІДКИДАННЯ (Drop)\nПреференс мешканця",
                    size=12, fill=REDBG, stroke=POS, color=POS, bold=True, sw=1.8))

    # Гілка НІ
    f.append(arrow(710, 240, 760, 240, color=MUTED, sw=1.8))
    f.append(text(735, 225, "НІ", size=11, color=MUTED, bold=True))

    # Питання 3
    f.append(fitbox(760, 180, 270, 120,
                    "Quiet Hours зараз?\n(23:00-07:00)",
                    size=12, fill=FILL, stroke=INK, color=INK, bold=True, sw=1.6))

    # Результати від Питання 3
    f.append(arrow(895, 300, 895, 370, color=POS, sw=1.8))
    f.append(text(910, 335, "ТАК (вдома)", size=11, color=POS, bold=True))
    f.append(fitbox(760, 370, 270, 60,
                    "Злиття в ранковий дайджест\n(Притримати до 07:00)",
                    size=12, fill=YELLOWBG, stroke=POS, color=POS, bold=True, sw=1.6))

    f.append(arrow(895, 180, 895, 130, color=FIELD, sw=1.8))
    f.append(text(910, 155, "НІ / Стан Away", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, "policy-decision-matrix.svg"), W, H, *f,
           title="Дерево прийняття рішень Policy Engine")


if __name__ == "__main__":
    fig_pipeline_architecture()
    fig_dual_payload_sequence()
    fig_channel_fallback_ladder()
    fig_policy_decision_matrix()
    print("SVG figures generated successfully.")
