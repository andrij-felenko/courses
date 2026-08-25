# -*- coding: utf-8 -*-
import sys
import os

# scripts/ directory is 4 levels up: book/programming/security/secrets-management -> ../../../..
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. secret-zero-problem: Парадокс початкового секрету та машинна ідентичність ──
def fig_secret_zero_problem():
    W, H = 840, 330
    p = []

    # Контейнер / Вузол середовища виконання
    p.append(rect(20, 45, 230, 255, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    p.append(text(135, 75, "Середовище виконання", size=13, color=INK, bold=True))
    p.append(text(135, 95, "Kubernetes Pod / AWS EC2", size=11, color=MUTED))

    # Застосунок
    p.append(rect(40, 115, 190, 80, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(135, 145, "Застосунок", size=13, color=NEG, bold=True))
    p.append(text(135, 168, "не має вшитих паролів", size=10, color=INK))

    # Платформний маркер (ServiceAccount JWT / STS Header)
    p.append(rect(40, 210, 190, 70, fill="#ffffff", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(135, 235, "Платформний маркер", size=11, color=INK, bold=True))
    p.append(text(135, 255, "SA JWT / Instance Identity", size=10, color=MUTED))

    # Платформа / Провайдер ідентичності
    p.append(rect(310, 45, 220, 115, fill="#fdf6e2", stroke="#b58900", sw=1.8, rx=8))
    p.append(text(420, 75, "Провайдер довіри", size=13, color="#b58900", bold=True))
    p.append(text(420, 95, "K8s API / AWS STS / TPM", size=11, color=MUTED))
    p.append(text(420, 125, "криптографічно підписує маркер", size=10, color=INK))
    p.append(text(420, 143, "і підтверджує його чинність", size=10, color=MUTED))

    # Сховище секретів (Vault)
    p.append(rect(590, 45, 230, 255, fill="#eaf6ec", stroke=FIELD, sw=2, rx=8))
    p.append(text(705, 75, "Сховище секретів (Vault)", size=13, color=FIELD, bold=True))
    p.append(text(705, 95, "Автентифікація та авторизація", size=11, color=MUTED))

    p.append(rect(610, 120, 190, 65, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(705, 145, "Перевірка підпису", size=11, color=INK, bold=True))
    p.append(text(705, 167, "Зіставлення з політикою (ACL)", size=10, color=MUTED))

    p.append(rect(610, 205, 190, 75, fill="#ffffff", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(705, 230, "Динамічний токен", size=11, color=FIELD, bold=True))
    p.append(text(705, 250, "Обмежений TTL (напр. 1 год)", size=10, color=INK))
    p.append(text(705, 268, "з прив'язкою до ідентичності", size=9, color=MUTED))

    # Стрілки взаємодії
    # 1. Застосунок читає платформний маркер
    p.append(arrow(135, 195, 135, 210, color=NEG, sw=1.5))

    # 2. Передача маркера до Vault
    p.append(arrow(230, 245, 590, 245, color=NEG, sw=2))
    p.append(text(410, 235, "1. Запит автентифікації з JWT", size=11, color=NEG, bold=True))

    # 3. Vault перевіряє маркер у провайдера довіри
    p.append(arrow(610, 130, 530, 100, color=INK, sw=1.5))
    p.append(text(585, 105, "2. TokenReview", size=10, color=INK))

    # 4. Повернення короткоживучого клієнтського токена
    p.append(arrow(590, 160, 230, 160, color=FIELD, sw=2))
    p.append(text(410, 150, "3. Короткоживучий токен доступу", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "secret-zero-problem.svg"), W, H, *p,
           title="Розв'язання парадоксу початкового секрету через машинну ідентичність")


# ── 2. vault-storage-barrier: Бар'єр безпеки, Envelope Encryption та Шамір ────
def fig_vault_storage_barrier():
    W, H = 840, 340
    p = []

    # Ліва колонка: Ключі розпечатування (Shamir Shards)
    p.append(rect(20, 40, 200, 270, fill="#fdf6e2", stroke="#b58900", sw=1.8, rx=8))
    p.append(text(120, 68, "Розподіл секрету Шаміра", size=12, color="#b58900", bold=True))
    p.append(text(120, 88, "Поріг 3 з 5 часток (k з n)", size=10, color=MUTED))

    p.append(rect(35, 110, 170, 36, fill="#ffffff", stroke="#b58900", sw=1.2, rx=5))
    p.append(text(120, 133, "Частка 1 (Оператор A)", size=10, color=INK))

    p.append(rect(35, 155, 170, 36, fill="#ffffff", stroke="#b58900", sw=1.2, rx=5))
    p.append(text(120, 178, "Частка 2 (Оператор B)", size=10, color=INK))

    p.append(rect(35, 200, 170, 36, fill="#ffffff", stroke="#b58900", sw=1.2, rx=5))
    p.append(text(120, 223, "Частка 3 (Оператор C)", size=10, color=INK))

    p.append(rect(35, 245, 170, 50, fill="#f4f6f8", stroke="#94a3b8", sw=1.0, rx=5))
    p.append(text(120, 266, "Частки 4 та 5 (резерв)", size=10, color=MUTED))
    p.append(text(120, 284, "не потрібні для кворуму", size=9, color=MUTED))

    # Центральна колонка: Бар'єр безпеки у пам'яті (Vault In-Memory Barrier)
    p.append(rect(260, 40, 290, 270, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    p.append(text(405, 68, "Бар'єр безпеки (RAM)", size=13, color=NEG, bold=True))
    p.append(text(405, 88, "Пам'ять заблокована через mlock", size=10, color=MUTED))

    # Головний ключ (Master Key / KEK)
    p.append(rect(280, 110, 250, 65, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(405, 135, "Головний ключ (Master Key)", size=11, color=NEG, bold=True))
    p.append(text(405, 155, "відновлюється з 3 часток у RAM", size=10, color=INK))

    # Ключ шифрування даних (DEK)
    p.append(rect(280, 210, 250, 80, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(405, 235, "Ключ шифрування даних (DEK)", size=11, color=FIELD, bold=True))
    p.append(text(405, 255, "розшифровується Master Key", size=10, color=INK))
    p.append(text(405, 275, "шифрує всі записи сховища", size=9, color=MUTED))

    # Стрілка між Master Key та DEK
    p.append(arrow(405, 175, 405, 210, color=NEG, sw=1.5))
    p.append(text(465, 193, "розшифрування", size=9, color=NEG))

    # Права колонка: Недовірене постійне сховище (Untrusted Storage)
    p.append(rect(590, 40, 230, 270, fill="#fdf2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(705, 68, "Недовірене сховище", size=13, color=POS, bold=True))
    p.append(text(705, 88, "Raft / Consul / Диск / S3", size=10, color=MUTED))

    p.append(rect(610, 110, 190, 75, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(705, 135, "Зашифрований DEK", size=11, color=INK, bold=True))
    p.append(text(705, 155, "зашифрований на KEK", size=10, color=MUTED))
    p.append(text(705, 173, "безпечний для збереження", size=9, color=MUTED))

    p.append(rect(610, 210, 190, 80, fill="#ffffff", stroke=POS, sw=1.2, rx=6))
    p.append(text(705, 235, "Шифротексти секретів", size=11, color=INK, bold=True))
    p.append(text(705, 255, "AES-GCM-256 + HMAC", size=10, color=MUTED))
    p.append(text(705, 275, "повна автентифікованість", size=9, color=MUTED))

    # Стрілки розпечатування (Unseal)
    p.append(arrow(205, 142, 280, 142, color="#b58900", sw=2))
    p.append(text(242, 132, "Кворум", size=9, color="#b58900", bold=True))

    # Стрілки взаємодії сховища
    p.append(arrow(530, 250, 610, 250, color=FIELD, sw=2))
    p.append(text(570, 240, "I/O", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "vault-storage-barrier.svg"), W, H, *p,
           title="Бар'єр безпеки: конвертне шифрування та розподіл секрету Шаміра")


# ── 3. dynamic-secret-lease: Життєвий цикл динамічних секретів та ліз ─────────
def fig_dynamic_secret_lease():
    W, H = 840, 310
    p = []

    # Горизонтальна часова шкала
    p.append(line(40, 160, 800, 160, color=LINE, sw=2))

    # Точки життєвого циклу
    # T0: Запит і створення
    p.append(circle(80, 160, 8, fill=NEG, stroke=NEG, sw=2))
    p.append(rect(30, 45, 140, 85, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    p.append(text(100, 70, "t = 0: Створення", size=11, color=NEG, bold=True))
    p.append(text(100, 90, "CREATE ROLE", size=10, color=INK))
    p.append(text(100, 108, "унікальний логін/пароль", size=9, color=MUTED))
    p.append(text(100, 123, "TTL = 30 хв", size=9, color=NEG, bold=True))
    p.append(line(80, 130, 80, 152, color=NEG, sw=1.5, dash="3,3"))

    # T1: Перше продовження (Heartbeat Renewal 1)
    p.append(circle(270, 160, 8, fill=FIELD, stroke=FIELD, sw=2))
    p.append(rect(200, 195, 140, 80, fill="#eaf6ec", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(270, 220, "t = 20 хв: Продовження", size=11, color=FIELD, bold=True))
    p.append(text(270, 240, "renew-lease (клієнт)", size=10, color=INK))
    p.append(text(270, 258, "перевірка чинності", size=9, color=MUTED))
    p.append(line(270, 168, 270, 195, color=FIELD, sw=1.5, dash="3,3"))

    # T2: Друге продовження (Heartbeat Renewal 2)
    p.append(circle(460, 160, 8, fill=FIELD, stroke=FIELD, sw=2))
    p.append(rect(390, 45, 140, 80, fill="#eaf6ec", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(460, 70, "t = 40 хв: Продовження", size=11, color=FIELD, bold=True))
    p.append(text(460, 90, "renew-lease", size=10, color=INK))
    p.append(text(460, 108, "новий термін очікування", size=9, color=MUTED))
    p.append(line(460, 125, 460, 152, color=FIELD, sw=1.5, dash="3,3"))

    # T3: Досягнення Max TTL або відкликання
    p.append(circle(650, 160, 8, fill="#b58900", stroke="#b58900", sw=2))
    p.append(rect(580, 195, 140, 80, fill="#fdf6e2", stroke="#b58900", sw=1.5, rx=6))
    p.append(text(650, 220, "t = 60 хв: Max TTL", size=11, color="#b58900", bold=True))
    p.append(text(650, 240, "Граничний ліміт лізи", size=10, color=INK))
    p.append(text(650, 258, "заборона продовження", size=9, color=MUTED))
    p.append(line(650, 168, 650, 195, color="#b58900", sw=1.5, dash="3,3"))

    # T4: Анулювання / Знищення (Revocation)
    p.append(circle(770, 160, 8, fill=POS, stroke=POS, sw=2))
    p.append(rect(700, 45, 130, 85, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(765, 70, "t = 60+ хв: Відкликання", size=11, color=POS, bold=True))
    p.append(text(765, 90, "DROP ROLE", size=10, color=POS, bold=True))
    p.append(text(765, 108, "розрив з'єднань БД", size=9, color=INK))
    p.append(text(765, 123, "секрет стає сміттям", size=9, color=MUTED))
    p.append(line(770, 130, 770, 152, color=POS, sw=1.5, dash="3,3"))

    render(os.path.join(OUT, "dynamic-secret-lease.svg"), W, H, *p,
           title="Життєвий цикл динамічного секрету: видача, пульсове продовження та знищення")


# ── 4. dual-key-rotation: Безперервна ротація ключів без простою ──────────────
def fig_dual_key_rotation():
    W, H = 840, 320
    p = []

    # Фаза 1: Одиночний ключ N (активний)
    p.append(rect(30, 50, 230, 230, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(145, 80, "Фаза 1: Робочий стан", size=12, color=INK, bold=True))
    p.append(text(145, 100, "Один активний ключ", size=10, color=MUTED))

    p.append(rect(45, 120, 200, 60, fill="#eaf6ec", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(145, 145, "Ключ v1 (Primary)", size=11, color=FIELD, bold=True))
    p.append(text(145, 165, "Шифрування + Розшифрування", size=9, color=INK))

    p.append(rect(45, 195, 200, 65, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=6))
    p.append(text(145, 220, "База даних / Записи", size=10, color=MUTED))
    p.append(text(145, 240, "усі записи зашифровані v1", size=9, color=MUTED))

    # Стрілка переходу 1 -> 2
    p.append(arrow(260, 160, 300, 160, color=LINE, sw=1.8))

    # Фаза 2: Подвійний ключ під час ротації (Overlapping Window)
    p.append(rect(300, 50, 250, 230, fill="#fdf6e2", stroke="#b58900", sw=2, rx=8))
    p.append(text(425, 80, "Фаза 2: Вікно ротації", size=12, color="#b58900", bold=True))
    p.append(text(425, 100, "Плавна зміна версій", size=10, color=MUTED))

    p.append(rect(315, 115, 220, 55, fill="#eaf6ec", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(425, 137, "Ключ v2 (Primary / New)", size=11, color=FIELD, bold=True))
    p.append(text(425, 155, "Шифрування нових записів", size=9, color=FIELD))

    p.append(rect(315, 175, 220, 55, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    p.append(text(425, 197, "Ключ v1 (Secondary / Old)", size=11, color=NEG, bold=True))
    p.append(text(425, 215, "Тільки розшифрування старих", size=9, color=NEG))

    p.append(text(425, 255, "Фоновий ре-енкрипт (Rewrap)", size=10, color=INK, italic=True))

    # Стрілка переходу 2 -> 3
    p.append(arrow(550, 160, 590, 160, color=LINE, sw=1.8))

    # Фаза 3: Завершення ротації та відкликання старого ключа
    p.append(rect(590, 50, 230, 230, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(705, 80, "Фаза 3: Ротація завершена", size=12, color=INK, bold=True))
    p.append(text(705, 100, "Старий ключ відкликано", size=10, color=MUTED))

    p.append(rect(605, 120, 200, 60, fill="#eaf6ec", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(705, 145, "Ключ v2 (Primary)", size=11, color=FIELD, bold=True))
    p.append(text(705, 165, "Шифрування + Розшифрування", size=9, color=INK))

    p.append(rect(605, 195, 200, 65, fill="#fdf2f2", stroke=POS, sw=1.2, rx=6))
    p.append(text(705, 220, "Ключ v1 (Retired / Revoked)", size=10, color=POS, bold=True))
    p.append(text(705, 240, "видалено з активної пам'яті", size=9, color=MUTED))

    render(os.path.join(OUT, "dual-key-rotation.svg"), W, H, *p,
           title="Автоматична безперервна ротація ключів: вікно перекриття версій")


if __name__ == "__main__":
    fig_secret_zero_problem()
    fig_vault_storage_barrier()
    fig_dynamic_secret_lease()
    fig_dual_key_rotation()
    print("Figures generated successfully.")
