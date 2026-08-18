# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

BLUE_T  = "#eaf0fd"
GREEN_T = "#e7f6ec"
AMBER_T = "#fdf0dd"
RED_T   = "#fdecea"
PURP_T  = "#f3e8ff"
NEUT    = "#eef2f6"

AMBER   = "#e08a1e"
GREEN   = "#2e7d32"
BLUE    = "#1565c0"
RED     = "#c62828"
PURPLE  = "#7b1fa2"


def fig_resilience_tactics_flow():
    """Ланцюжок тактик стійкості під навантаженням: Ingress → Adaptive Limiter → Brownout → Bulkhead → Worker / DLQ."""
    W, H = 1000, 420
    f = []

    # 1. Вхідний трафік (Пік 50k RPS)
    f.append(fitbox(40, 40, 200, 70, "Вхідний потік трафіку\n(Пікове навантаження\n50,000 RPS)",
                    size=12, bold=True, fill=RED_T, stroke=RED, color=RED))
    f.append(arrow(240, 75, 290, 75, color=RED, sw=2))

    # 2. Адаптивний контролер паралелізму (CoDel / Vegas)
    f.append(fitbox(290, 30, 210, 90, "Адаптивний лимитер\n(Little's Law & CoDel)\n\nДинамічний ліміт inflight\nЗатримка черги < 20 мс",
                    size=11, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # Гілка скидання надлишку (Shedding)
    f.append(arrow(395, 120, 395, 160, color=RED, sw=2))
    f.append(fitbox(310, 160, 170, 50, "429 Too Many Requests\n(Shedding Tier 2)",
                    size=11, fill=RED_T, stroke=RED, color=RED))

    f.append(arrow(500, 75, 550, 75, color=AMBER, sw=2))

    # 3. Деградація Brownout (Tiering)
    f.append(fitbox(550, 30, 210, 90, "Селектор пріоритетів\n(Brownout Mode)\n\nTier 0: Замки / Платежі ✓\nTier 1: Статус UI ✓\nTier 2: Аналітика (Shed)",
                    size=11, bold=True, fill=BLUE_T, stroke=BLUE, color=BLUE))

    f.append(arrow(760, 75, 810, 75, color=BLUE, sw=2))

    # 4. Bulkhead та ізольовані воркери
    f.append(fitbox(810, 30, 150, 90, "Ізольований Bulkhead\n\nВоркери Tier 0\n(Окремий пуп сокетів)",
                    size=11, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Нижній шар: Черга повідомлень та DLQ для отруйних пакетів
    f.append(fitbox(40, 260, 920, 120, "Шар асинхронної обробки подій та захисту від отруйних пакетів (Poison Messages)",
                    size=12, bold=True, fill=NEUT, stroke=INK, color=INK))

    f.append(fitbox(70, 300, 240, 60, "Асинхронний Event Log\n(Kafka / NATS JetStream)",
                    size=11, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(arrow(310, 330, 360, 330, color=BLUE, sw=2))

    f.append(fitbox(360, 300, 250, 60, "Ретрай з експоненційним\nзсувом та джиттером (Jitter)",
                    size=11, fill=AMBER_T, stroke=AMBER, color=AMBER))
    f.append(arrow(610, 330, 660, 330, color=AMBER, sw=2))

    f.append(fitbox(660, 300, 260, 60, "Dead Letter Queue (DLQ)\n(Ізоляція збійних пакетів\nпісля 3 спроб)",
                    size=11, bold=True, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    render(os.path.join(OUT, 'resilience-tactics-flow.svg'), W, H, *f,
           title="Ланцюжок тактик стійкості під навантаженням")


def fig_cell_based_architecture():
    """Багаторегіональна осередкова архітектура (Cell-Based Architecture) з ізоляцією радіуса ураження."""
    W, H = 1000, 460
    f = []

    # 1. Глобальний DNS / Anycast / Edge CDN
    f.append(fitbox(200, 30, 600, 60, "Глобальний маршрутизатор: GeoDNS / Anycast BGP / Edge CDN (TLS Termination)",
                    size=13, bold=True, fill=BLUE_T, stroke=BLUE, color=BLUE))

    f.append(arrow(350, 90, 220, 150, color=BLUE, sw=2))
    f.append(arrow(500, 90, 500, 150, color=BLUE, sw=2))
    f.append(arrow(650, 90, 780, 150, color=BLUE, sw=2))

    # 2. Осередки (Cells)
    # Cell 1 (EU West)
    f.append(fitbox(50, 150, 280, 200, "Осередок 1 (Cell 1 - EU West)\n\n• Tenants: 1 .. 50,000\n• Ingress & Service Mesh\n• БД: Isolated PostgreSQL\n• Специфіка: GDPR Compliance\n(Дані не залишають ЄС)",
                    size=11, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Cell 2 (US East)
    f.append(fitbox(360, 150, 280, 200, "Осередок 2 (Cell 2 - US East)\n\n• Tenants: 50,001 .. 100,000\n• Ingress & Service Mesh\n• БД: Isolated PostgreSQL\n• Автономне виконання\n(Радіус ураження = 5%)",
                    size=11, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Cell N (APAC)
    f.append(fitbox(670, 150, 280, 200, "Осередок N (Cell N - APAC)\n\n• Tenants: 950,000 .. 1M\n• Ingress & Service Mesh\n• БД: Isolated PostgreSQL\n• Ізольований стан\n(Локальні деплої)",
                    size=11, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    # 3. Нижній шар: Глобальний глобальний реєстр топології (Global Cell Router Registry)
    f.append(fitbox(50, 380, 900, 50, "Глобальний контролер осередків: Cell Registry & Routing Metadata (Read-Only Replicas)",
                    size=12, bold=True, fill=NEUT, stroke=INK, color=INK))

    render(os.path.join(OUT, 'cell-based-architecture.svg'), W, H, *f,
           title="Багаторегіональна осередкова архітектура (Cell-Based Architecture)")


def fig_zero_trust_stride_boundary():
    """Модель загроз STRIDE та периметр Zero-Trust з mTLS, SPIFFE та конвертним шифруванням."""
    W, H = 1000, 440
    f = []

    # Зовнішня межа (Ненадійна зона)
    f.append(fitbox(40, 40, 220, 360, "Зовнішній периметр\n(Ненадійна мережа)\n\n• Публічний Інтернет\n• IoT Давачі\n• Мобільні клієнти\n\nЗагрози STRIDE:\n- Spoofing (Підробка)\n- DoS (Атака на відмову)\n- Tampering (Перехоплення)",
                    size=11, fill=RED_T, stroke=RED, color=RED))

    f.append(arrow(260, 220, 330, 220, color=RED, sw=2))

    # Внутрішня зона Zero-Trust (Межа mTLS)
    f.append(fitbox(330, 40, 630, 360, "Периметр Zero-Trust (Внутрішній Service Mesh)\n\nІдентичність: SPIFFE/SPIRE X.509 SVID | mTLS (TLS 1.3)",
                    size=12, bold=True, fill=NEUT, stroke=INK, color=INK))

    # Внутрішні сервіси
    f.append(fitbox(360, 110, 260, 80, "API Gateway / Proxy\n\n- Перевірка OAuth2 / JWT\n- Token Bucket Rate Limit",
                    size=11, fill=BLUE_T, stroke=BLUE, color=BLUE))

    f.append(arrow(620, 150, 670, 150, color=BLUE, sw=2))

    f.append(fitbox(670, 110, 260, 80, "Ledger & Core Services\n\n- OPA Rego AuthZ (RBAC)\n- Envelope Encryption (DEK)",
                    size=11, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Сховище та шифрування
    f.append(fitbox(360, 240, 260, 120, "KMS & Secrets Manager\n(Vault / AWS KMS)\n\n• Ротація KEK ключа\n• Генерація тимчасових DEK\n• Zero-Trust автентифікація",
                    size=11, fill=AMBER_T, stroke=AMBER, color=AMBER))

    f.append(fitbox(670, 240, 260, 120, "Захищене Сховище (БД)\n\n• Append-Only Audit Log\n• Шифрування колонок (DEK)\n• Криптографічні хеш-ланцюги",
                    size=11, fill=PURP_T, stroke=PURPLE, color=PURPLE))

    render(os.path.join(OUT, 'zero-trust-stride-boundary.svg'), W, H, *f,
           title="Модель загроз STRIDE та периметр Zero-Trust")


def fig_canary_burnrate_evaluation():
    """Життєвий цикл автоматизованого канареєчного деплою з оцінкою вигорання бюджету помилок."""
    W, H = 1000, 420
    f = []

    # Етапи деплою
    f.append(fitbox(40, 40, 180, 70, "1. Старт Canary (1%)\n\nМаршрутизація 1%\nтрафіку на версію v2.4",
                    size=11, bold=True, fill=BLUE_T, stroke=BLUE, color=BLUE))
    f.append(arrow(220, 75, 270, 75, color=BLUE, sw=2))

    f.append(fitbox(270, 40, 200, 70, "2. Аналіз метрик (5 хв)\n\nПорівняння з Baseline:\n• Error Rate (5xx)\n• Latency p99",
                    size=11, bold=True, fill=AMBER_T, stroke=AMBER, color=AMBER))

    # Дві гілки рішення
    # Гілка А: Сплеск Burn Rate → Відкочування
    f.append(arrow(370, 110, 370, 170, color=RED, sw=2))
    f.append(fitbox(260, 170, 220, 80, "КРИТИЧНИЙ СПЛЕСК (Burn > 14.4x)\n\nАвтоматичне відкочування (Rollback)\nЧас реакції < 30 секунд!",
                    size=11, bold=True, fill=RED_T, stroke=RED, color=RED))

    # Гілка Б: Норма → Ескалація
    f.append(arrow(470, 75, 520, 75, color=GREEN, sw=2))
    f.append(fitbox(520, 40, 200, 70, "3. Прогресія (25% → 50%)\n\nБюджет помилок в нормі\n(Burn Rate < 1.0x)",
                    size=11, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    f.append(arrow(720, 75, 770, 75, color=GREEN, sw=2))

    f.append(fitbox(770, 40, 190, 70, "4. Повний реліз (100%)\n\nПереключення 100%\nЗавершення канарейки",
                    size=11, bold=True, fill=GREEN_T, stroke=GREEN, color=GREEN))

    # Нижній шар: Моніторинг вигорання бюджету помилок
    f.append(fitbox(40, 290, 920, 100, "Вікно оцінки метрик: Multi-Window Multi-Burn-Rate Alerting (1h / 14.4x та 6h / 6x)\n\n• Автоматичний регулятор порівнює метрики Canary та Baseline у реальному часі\n• При перевищенні порогу відхилення — автоматичний терміновий rollback без участі людини",
                    size=11, fill=NEUT, stroke=INK, color=INK))

    render(os.path.join(OUT, 'canary-burnrate-evaluation.svg'), W, H, *f,
           title="Життєвий цикл автоматизованого канареєчного деплою")


if __name__ == '__main__':
    fig_resilience_tactics_flow()
    fig_cell_based_architecture()
    fig_zero_trust_stride_boundary()
    fig_canary_burnrate_evaluation()
    print("Figures generated successfully.")
