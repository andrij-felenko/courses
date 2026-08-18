# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
RED_B   = "#e74c3c"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
GREEN_B = "#27ae60"
BLUE_T  = "#eaf0fd"
BLUE_B  = "#2980b9"
NEUT    = "#eef2f6"


def fig_tombstone_index_bloat():
    """Порівняння звичайного B-tree індексу з м'яким видаленням та часткового індексу (WHERE deleted_at IS NULL)."""
    W, H = 1040, 430
    f = []

    # Title / Headers
    f.append(fitbox(40, 30, 460, 36, "Звичайний B-tree індекс (з м'яким видаленням)", size=14, bold=True, fill=RED_T, stroke=RED_B, color="#922b21"))
    f.append(fitbox(540, 30, 460, 36, "Частковий індекс (WHERE deleted_at IS NULL)", size=14, bold=True, fill=GREEN_T, stroke=GREEN_B, color="#1e8449"))

    # Left box: Full index with dead tombstones
    f.append(rect(40, 80, 460, 320, fill=BG, stroke="#c8ced6", rx=6))
    
    # B-Tree root/nodes left
    f.append(fitbox(170, 95, 200, 34, "Корінь індексу (idx_orders)", size=12, fill=NEUT))
    f.append(arrow(220, 129, 130, 160))
    f.append(arrow(320, 129, 390, 160))

    # Pages with tombstones
    f.append(fitbox(60, 160, 160, 44, "Сторінка A: 4 записи\n(3 з яких deleted_at!)", size=11, fill=RED_T, stroke=RED_B))
    f.append(fitbox(320, 160, 160, 44, "Сторінка B: 4 записи\n(2 з яких deleted_at!)", size=11, fill=RED_T, stroke=RED_B))

    # Leaf nodes array
    f.append(fitbox(60, 225, 420, 38, "[ID:1 Live]  [ID:2 Dead]  [ID:3 Dead]  [ID:4 Dead]", size=11, fill="#fadbd8", stroke=RED_B))
    f.append(fitbox(60, 275, 420, 38, "[ID:5 Live]  [ID:6 Dead]  [ID:7 Live]  [ID:8 Dead]", size=11, fill="#fadbd8", stroke=RED_B))

    f.append(fitbox(60, 330, 420, 50, "Сканування залучає змертвілі сторінки!\nВисока латентність, розбухання індексу (Bloat).", size=12, fill=RED_T, stroke=RED_B, color=RED_B, bold=True))

    # Right box: Partial Index
    f.append(rect(540, 80, 460, 320, fill=BG, stroke="#c8ced6", rx=6))

    # B-Tree root right
    f.append(fitbox(670, 95, 200, 34, "Корінь індексу (idx_active)", size=12, fill=NEUT))
    f.append(arrow(770, 129, 770, 160))

    f.append(fitbox(670, 160, 200, 44, "Компактні сторінки\nТільки живі записи!", size=11, fill=GREEN_T, stroke=GREEN_B))

    # Leaf nodes array right
    f.append(fitbox(640, 225, 260, 38, "[ID:1 Live]  [ID:5 Live]  [ID:7 Live]", size=11, fill="#d4efdf", stroke=GREEN_B))
    
    # Separated Heap for tombstones
    f.append(fitbox(570, 275, 400, 38, "Таблиця (Heap): мертві записи зберігаються без індексації", size=11, fill=NEUT, stroke=MUTED))

    f.append(fitbox(560, 330, 420, 50, "Індекс компактний і гарячий у кеші RAM!\n0% змертвілих сторінок у пошуку активних даних.", size=12, fill=GREEN_T, stroke=GREEN_B, color=GREEN_B, bold=True))

    render(os.path.join(OUT, 'tombstone-index-bloat.svg'), W, H, *f,
           title="Порівняння розбухання B-tree індексу та часткового індексу")


def fig_data_lifecycle_pipeline():
    """Багатошаровий конвеєр життєвого циклу даних: Hot OLTP -> Detach Partition -> Cold Archive -> Crypto-Shredding."""
    W, H = 1080, 440
    f = []

    # 4 Tiers
    # Tier 1: Hot
    f.append(fitbox(40, 50, 220, 150, "Hot Tier (0-90 днів)\n\n• PostgreSQL / Partitioned\n• Оптимізовано під OLTP\n• Часткові індекси\n• Швидкі NVMe SSD", size=12, fill=BLUE_T, stroke=BLUE_B))
    
    # Arrow 1
    f.append(arrow(260, 125, 300, 125, sw=2, color=BLUE_B))
    f.append(fitbox(262, 95, 36, 22, "DETACH", size=9, bold=True, fill=BG, stroke=BLUE_B, color=BLUE_B))

    # Tier 2: Detached Warm
    f.append(fitbox(300, 50, 220, 150, "Warm Tier (90-365 днів)\n\n• Від'єднані партиції\n• Read-Only доступ\n• 0 впливу на гарячі індекси\n• Дешевше сховище", size=12, fill=AMBER_T, stroke=AMBER))

    # Arrow 2
    f.append(arrow(520, 125, 560, 125, sw=2, color=AMBER))
    f.append(fitbox(522, 95, 36, 22, "EXPORT", size=9, bold=True, fill=BG, stroke=AMBER, color=AMBER))

    # Tier 3: Cold Archive
    f.append(fitbox(560, 50, 220, 150, "Cold Tier (1-7 років)\n\n• S3 / Apache Parquet\n• Колонкове стиснення (ZSTD)\n• Запити через DuckDB/Athena\n• Відповідність регуляторам", size=12, fill=GREEN_T, stroke=GREEN_B))

    # Arrow 3
    f.append(arrow(780, 125, 820, 125, sw=2, color=RED_B))
    f.append(fitbox(782, 95, 36, 22, "PURGE", size=9, bold=True, fill=BG, stroke=RED_B, color=RED_B))

    # Tier 4: Purged / Shredded
    f.append(fitbox(820, 50, 220, 150, "Erasure / Shredded\n\n• Вилучення ключів KMS\n• Знищення фізичних файлів\n• Очищення знімків\n• GDPR Compliance", size=12, fill=RED_T, stroke=RED_B))

    # Bottom Pipeline Details (Execution control)
    f.append(rect(40, 240, 1000, 150, fill=NEUT, stroke="#c8ced6", rx=6))
    f.append(fitbox(240, 252, 600, 30, "Вузол керування політикам retention (Data Lifecycle Node Worker)", size=13, bold=True, fill=BG, stroke=MUTED))
    
    f.append(fitbox(70, 295, 280, 75, "Асинхронний оркестратор:\nОцінка TTL та регламентів", size=11, fill=BG, stroke=INK))
    f.append(fitbox(390, 295, 300, 75, "Опитування Outbox / WAL:\nСинхронізація Search & Cache", size=11, fill=BG, stroke=INK))
    f.append(fitbox(720, 295, 280, 75, "Аудит операцій знищення:\nПідпис логів вилучення", size=11, fill=BG, stroke=INK))

    render(os.path.join(OUT, 'data-lifecycle-pipeline.svg'), W, H, *f,
           title="Багатошаровий конвеєр життєвого циклу даних")


def fig_crypto_shredding():
    """Схема криптографічного знищення (Crypto-Shredding): знищення ключа орендаря у KMS робить дані недоступними у всіх шарах."""
    W, H = 1040, 440
    f = []

    # KMS Box (top center)
    f.append(fitbox(370, 30, 300, 65, "KMS (Key Management System)\nКлюч орендаря / користувача K_user", size=13, bold=True, fill=AMBER_T, stroke=AMBER))

    # Erasure action on KMS
    f.append(fitbox(720, 30, 280, 65, "Запит GDPR Article 17:\nВидалення ключа K_user!", size=12, bold=True, fill=RED_T, stroke=RED_B))
    f.append(arrow(720, 62, 670, 62, color=RED_B, sw=2))

    # Title label for encrypted targets
    f.append(fitbox(270, 98, 500, 26, "Дані зашифровані за допомогою K_user в усіх шарах системи:", size=12, bold=True, fill=NEUT, stroke=MUTED))

    # Encrypted data targets
    f.append(fitbox(40, 175, 280, 120, "Гаряча база OLTP\n\nЗашифроване поле PII:\n0x8f4a2b9... (Ciphertext)", size=12, fill=BLUE_T, stroke=BLUE_B))
    f.append(fitbox(380, 175, 280, 120, "Архівні бакапи & S3\n\nНезмінні файли Parquet:\nE(PII, K_user)", size=12, fill=GREEN_T, stroke=GREEN_B))
    f.append(fitbox(720, 175, 280, 120, "Журнали й аудит-логи\n\nІсторія транзакцій:\nE(User_Metadata, K_user)", size=12, fill=NEUT, stroke=MUTED))

    # Connection arrows from KMS to storage layers
    f.append(arrow(430, 130, 180, 175, color=MUTED))
    f.append(arrow(520, 130, 520, 175, color=MUTED))
    f.append(arrow(610, 130, 860, 175, color=MUTED))

    # Bottom consequence box
    f.append(fitbox(40, 320, 960, 90, "Після видалення K_user з KMS зашифровані блоки перетворюються на математичний шум.\nБакапи не потрібно перезаписувати — GDPR дотримується миттєво без порушення цілісності ledgers!", size=12, bold=True, fill=RED_T, stroke=RED_B, color=RED_B))

    render(os.path.join(OUT, 'crypto-shredding.svg'), W, H, *f,
           title="Криптографічне знищення даних (Crypto-Shredding)")


if __name__ == "__main__":
    fig_tombstone_index_bloat()
    fig_data_lifecycle_pipeline()
    fig_crypto_shredding()
