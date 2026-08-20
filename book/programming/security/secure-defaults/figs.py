# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми 'Безпечні дефолти та відмова захисту'."""
import sys, os

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від book/programming/security/secure-defaults)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fig_failsafe_state_machine():
    """Фігура 1: Порівняння автоматів станів: Fail-Open проти Fail-Safe (Fail-Closed)."""
    w, h = 900, 470
    frags = []

    # Заголовок
    frags.append(text(450, 26, "Поведінка системи під час збоїв: Fail-Open проти Fail-Safe", size=17, bold=True))

    # Ліва колонка: Небезпечна модель (Fail-Open)
    frags.append(rect(15, 55, 420, 395, fill="#fff5f5", stroke=POS, sw=1.8, rx=8))
    frags.append(text(225, 80, "НЕБЕЗПЕЧНА ПОВЕДІНКА: Fail-Open", size=14, bold=True, color=POS))
    frags.append(text(225, 98, "(Відмова на користь відкритості / доступності)", size=11, color=MUTED))

    fo_init, _, _ = textbox(225, 140, "Початковий стан: Доступ заборонено\n(Очікування верифікації запиту)", size=11, pad=6, fill=BG, stroke=LINE, min_w=360)
    fo_eval, _, _ = textbox(225, 215, "Оцінка правил безпеки\n(WAF / Auth Service / ACL)", size=11, pad=6, fill="#fef3c7", stroke="#d97706", min_w=360)
    
    # Збійний перехід Fail-Open
    fo_err, _, _ = textbox(225, 295, "ЗБІЙ: Таймаут мережі / Невідомий атрибут /\nПомилка парсера / Uncaught Exception", size=10, pad=6, fill="#fee2e2", stroke=POS, bold=True, min_w=360)
    
    fo_res, _, _ = textbox(225, 385, "РЕЗУЛЬТАТ: ДОЗВОЛИТИ (Permit Bypass)\nВразливість захисту, доступ зловмиснику", size=12, pad=8, fill="#fee2e2", stroke=POS, bold=True, min_w=360)
    
    frags.extend([fo_init, fo_eval, fo_err, fo_res])
    frags.append(arrow(225, 162, 225, 192, color=LINE, sw=1.5))
    frags.append(arrow(225, 238, 225, 268, color=POS, sw=1.8))
    frags.append(arrow(225, 322, 225, 355, color=POS, sw=2.0))

    # Права колонка: Безпечна модель (Fail-Safe / Fail-Closed)
    frags.append(rect(465, 55, 420, 395, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(675, 80, "БЕЗПЕЧНА ПОВЕДІНКА: Fail-Safe (Fail-Closed)", size=14, bold=True, color=FIELD))
    frags.append(text(675, 98, "(Відмова на користь безпеки й збереження інваріанту)", size=11, color=MUTED))

    fc_init, _, _ = textbox(675, 140, "Початковий стан: Дефолт ЗАБОРОНА (Deny)\n(Інваріант безпеки зафіксовано)", size=11, pad=6, fill=BG, stroke=LINE, min_w=360)
    fc_eval, _, _ = textbox(675, 215, "Оцінка правил безпеки\n(Явне позитивне підтвердження прав)", size=11, pad=6, fill="#eaf0fd", stroke=NEG, min_w=360)
    
    # Збійний перехід Fail-Safe
    fc_err, _, _ = textbox(675, 295, "ЗБІЙ: Таймаут / Помилка розбору токена /\nАварійна зупинка сервісу авторизації", size=10, pad=6, fill="#f0fdf4", stroke=FIELD, bold=True, min_w=360)
    
    fc_res, _, _ = textbox(675, 385, "РЕЗУЛЬТАТ: ЗАБОРОНЕНО (Safe Default Retained)\nІнваріант збережено + запис до аудит-логу", size=12, pad=8, fill="#dcfce7", stroke=FIELD, bold=True, min_w=360)
    
    frags.extend([fc_init, fc_eval, fc_err, fc_res])
    frags.append(arrow(675, 162, 675, 192, color=LINE, sw=1.5))
    frags.append(arrow(675, 238, 675, 268, color=FIELD, sw=1.8))
    frags.append(arrow(675, 322, 675, 355, color=FIELD, sw=2.0))

    out_path = os.path.join(IMG_DIR, "failsafe-state-machine.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def fig_default_deny_architecture():
    """Фігура 2: Архітектурний конвеєр перевірки доступу на базі Default Deny."""
    w, h = 880, 480
    frags = []

    frags.append(text(440, 26, "Конвеєр авторизації за принципом абсолютної заборони (Default Deny)", size=17, bold=True))

    # Крок 1: Вхідний запит
    b_req, _, _ = textbox(440, 75, "Вхідний запит (Request: Суб'єкт, Дія, Об'єкт, Контекст оточення)", size=12, pad=8, fill="#f8fafc", stroke=LINE, min_w=680)
    frags.append(b_req)

    # Крок 2: Базовий стан - Заборона
    b_init, _, _ = textbox(440, 145, "КРОК 1: Ініціалізація рішення за замовчуванням\nРішення = ЗАБОРОНЕНО (Explicit Deny Baseline, S = ⊥)", size=11, pad=8, fill="#fee2e2", stroke=POS, bold=True, min_w=680)
    frags.append(b_init)

    # Крок 3: Перевірка явних заборон (Explicit Deny)
    b_deny, _, _ = textbox(440, 225, "КРОК 2: Перевірка заборонних правил (Explicit Deny Rules)\nЯкщо знайдено хоча б одну пряму заборону → Негайне блокування", size=11, pad=8, fill="#fef3c7", stroke="#d97706", min_w=680)
    frags.append(b_deny)

    # Крок 4: Перевірка явних дозволів (Explicit Allow)
    b_allow, _, _ = textbox(440, 305, "КРОК 3: Пошук однозначного явного дозволу (Explicit Allow Match)\nПовне співпадіння прав + валідний підпис + успішна перевірка умов", size=11, pad=8, fill="#eaf0fd", stroke=NEG, min_w=680)
    frags.append(b_allow)

    # Крок 5: Розгалуження на фінальне рішення
    # Ліва гілка: Дозвіл (лише за успіхом усіх перевірок)
    b_grant, _, _ = textbox(240, 410, "ДОЗВІЛ (ALLOW)\nЛише якщо є явний дозвіл,\nнемає заборон і збоїв", size=11, pad=8, fill="#dcfce7", stroke=FIELD, bold=True, min_w=340)
    
    # Права гілка: Збереження дефолтної заборони
    b_block, _, _ = textbox(640, 410, "ЗАБОРОНА (DENY)\nНемає дозволу / Помилка / Збій /\nНевідоме правило / Таймаут", size=11, pad=8, fill="#fee2e2", stroke=POS, bold=True, min_w=340)
    
    frags.extend([b_grant, b_block])

    # З'єднувальні стрілки
    frags.append(arrow(440, 96, 440, 122, color=LINE, sw=1.5))
    frags.append(arrow(440, 168, 440, 202, color=POS, sw=1.5))
    frags.append(arrow(440, 248, 440, 282, color="#d97706", sw=1.5))
    
    frags.append(arrow(340, 328, 240, 380, color=FIELD, sw=2.0))
    frags.append(arrow(540, 328, 640, 380, color=POS, sw=2.0))

    out_path = os.path.join(IMG_DIR, "default-deny-architecture.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def fig_system_stack_defaults():
    """Фігура 3: Ієрархія безпечних дефолтів на всіх рівнях програмного стека."""
    w, h = 900, 480
    frags = []

    frags.append(text(450, 26, "Ієрархія безпечних дефолтів на рівнях архітектури системи", size=17, bold=True))

    # Рівень 1: Операційна система та ядро
    l1, _, _ = textbox(450, 80, 
        "Рівень 1: Операційна система та ядро (Kernel & OS)\n"
        "• umask 0077/0027 • Localhost binding (127.0.0.1) • noexec/nosuid для /tmp • Seccomp default ERRNO",
        size=11, pad=8, fill="#f8fafc", stroke=LINE, min_w=840)
    
    # Рівень 2: Мережа та транспорт
    l2, _, _ = textbox(450, 160,
        "Рівень 2: Мережевий стек та файрвол (Network & Transport)\n"
        "• Default DROP для вхідних ланцюжків iptables/nftables • Тільки TLS 1.3 • Сувора автентифікація mTLS",
        size=11, pad=8, fill="#eaf0fd", stroke=NEG, min_w=840)

    # Рівень 3: Мова програмування та середовище виконання
    l3, _, _ = textbox(450, 240,
        "Рівень 3: Мова програмування та компілятор (Language & Compiler)\n"
        "• Незмінність (const/immutable) за дефолтом • Параметризовані SQL-запити • Захист від переповнень буфера",
        size=11, pad=8, fill="#fef3c7", stroke="#d97706", min_w=840)

    # Рівень 4: Веб-протоколи та API
    l4, _, _ = textbox(450, 320,
        "Рівень 4: Веб-інтерфейси та браузерний захист (Web & HTTP API)\n"
        "• Cookie SameSite=Lax/Strict, HttpOnly, Secure • CSP default-src 'none' • Заборона парсингу XXE сутностей",
        size=11, pad=8, fill="#f3e8ff", stroke="#7e22ce", min_w=840)

    # Рівень 5: Авторизація та доступ до даних
    l5, _, _ = textbox(450, 400,
        "Рівень 5: Контроль доступу та політики безпеки (RBAC / ABAC / Data)\n"
        "• Default DENY для всіх суб'єктів • Мінімум привілеїв • Автоматичне шифрування дисків AES-256",
        size=11, pad=8, fill="#dcfce7", stroke=FIELD, bold=True, min_w=840)

    frags.extend([l1, l2, l3, l4, l5])

    # Стрілки ієрархії
    frags.append(arrow(450, 108, 450, 134, color=LINE, sw=1.5))
    frags.append(arrow(450, 188, 450, 214, color=NEG, sw=1.5))
    frags.append(arrow(450, 268, 450, 294, color="#d97706", sw=1.5))
    frags.append(arrow(450, 348, 450, 374, color="#7e22ce", sw=1.5))

    out_path = os.path.join(IMG_DIR, "system-stack-defaults.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

if __name__ == "__main__":
    fig_failsafe_state_machine()
    fig_default_deny_architecture()
    fig_system_stack_defaults()
