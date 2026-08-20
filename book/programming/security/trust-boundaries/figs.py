# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. boundary-levels: Ієрархія контурів безпеки та межі довіри ─────────────
def fig_boundary_levels():
    W, H = 760, 340
    p = []

    # Контур 4: Зовнішня мережа (Недовірений)
    p.append(rect(30, 40, 700, 270, fill="#fdf2f2", stroke=POS, sw=1.5, rx=10))
    p.append(text(50, 65, "Контур 0: Відкрита мережа / Інтернет (Повна відсутність довіри)", size=12, color=POS, bold=True, anchor="start"))

    # Контур 3: Периметр застосунку / DMZ / WAF
    p.append(rect(60, 85, 640, 210, fill="#fffaf0", stroke="#d97706", sw=1.5, rx=8))
    p.append(text(80, 110, "Контур 1: Периметр і проксі (WAF, Ingress, TLS-термінація)", size=11, color="#b45309", bold=True, anchor="start"))

    # Контур 2: Простір користувача / Пісочниця
    p.append(rect(90, 130, 580, 150, fill="#f0f9ff", stroke=NEG, sw=1.5, rx=8))
    p.append(text(110, 155, "Контур 2: Безпривілейований процес / Sandbox (Ring 3, Seccomp, Unshare)", size=11, color=NEG, bold=True, anchor="start"))

    # Контур 1: Ядро операційної системи
    p.append(rect(120, 175, 520, 90, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(140, 200, "Контур 3: Ядро ОС та гіпервізор (Ring 0 / VMX root, захищена пам'ять)", size=11, color=FIELD, bold=True, anchor="start"))

    # Контур 0: Апаратний корінь довіри (TEE/TPM)
    p.append(rect(150, 215, 460, 40, fill="#ffffff", stroke=INK, sw=1.8, rx=6))
    p.append(text(380, 240, "Контур 4: Апаратний анклав і TEE (TrustZone, Intel SGX, TPM)", size=11, color=INK, bold=True))

    # Стрілка перетину межі зліва направо або ззовні всередину
    # Лінія демаркації
    p.append(line(735, 50, 735, 305, color=POS, sw=2, dash="4,3"))
    p.append(text(745, 180, "Межа", size=10, color=POS, bold=True, anchor="start"))

    render(os.path.join(OUT, "boundary-levels.svg"), W, H, *p,
           title="Ієрархія контурів безпеки та межі довіри")


# ── 2. confused-deputy-boundary: Атака «заплутаний заступник» ─────────────────
def fig_confused_deputy():
    W, H = 760, 300
    p = []

    # Непривілейований клієнт
    p.append(rect(30, 50, 190, 110, fill="#fdf2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(125, 78, "Недовірений клієнт", size=12, color=POS, bold=True))
    p.append(text(125, 102, "UID: 1000 (User)", size=10, color=MUTED))
    p.append(text(125, 124, "Не має доступу до /etc/shadow", size=9, color=POS))
    p.append(text(125, 142, "Запит: «Запиши в /etc/shadow»", size=9, color=INK, bold=True))

    # Межа довіри
    p.append(line(250, 30, 250, 275, color=POS, sw=2, dash="4,3"))
    p.append(text(250, 25, "Межа довіри", size=10, color=POS, bold=True))

    # Привілейований заступник (Сервіс)
    p.append(rect(280, 50, 200, 110, fill="#fffaf0", stroke="#d97706", sw=1.8, rx=8))
    p.append(text(380, 78, "Привілейований демон", size=12, color="#b45309", bold=True))
    p.append(text(380, 102, "UID: 0 (root)", size=10, color=MUTED))
    p.append(text(380, 124, "Виконує запис від СВОГО імені", size=9, color=POS, bold=True))
    p.append(text(380, 142, "Втрата контексту клієнта!", size=9, color=POS))

    # Захищений ресурс
    p.append(rect(530, 50, 190, 110, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(625, 78, "Системний файл", size=12, color=FIELD, bold=True))
    p.append(text(625, 102, "Шлях: /etc/shadow", size=10, color=MUTED))
    p.append(text(625, 124, "Дозвіл: тільки root (rw-)", size=9, color=INK))
    p.append(text(625, 142, "Перезаписано нелегітимно!", size=9, color=POS, bold=True))

    # Стрілки
    p.append(arrow(220, 105, 275, 105, color=POS, sw=2))
    p.append(arrow(480, 105, 525, 105, color=POS, sw=2))

    # Панель захисту
    p.append(rect(50, 190, 660, 85, fill="#f8fafc", stroke=INK, sw=1.5, rx=8))
    p.append(text(380, 215, "Контрзаходи проти заплутаного заступника на межі:", size=11, color=INK, bold=True))
    p.append(text(380, 238, "1. Передача дескриптора (Capability) замість шляху: клієнт відкриває сам і передає fd через SCM_RIGHTS", size=10, color=FIELD))
    p.append(text(380, 258, "2. Зниження привілеїв під час відкриття (seteuid/faccessat2) або перевірка SO_PEERCRED", size=10, color=FIELD))

    render(os.path.join(OUT, "confused-deputy-boundary.svg"), W, H, *p,
           title="Атака «заплутаний заступник» на межі привілеїв")


# ── 3. privilege-separated-architecture: Розділення привілеїв ────────────────
def fig_privilege_separated():
    W, H = 760, 310
    p = []

    # Недовірена зона (Мережа)
    p.append(rect(30, 45, 140, 120, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(100, 75, "Мережевий трафік", size=11, color=POS, bold=True))
    p.append(text(100, 100, "Сирі байти від", size=10, color=MUTED))
    p.append(text(100, 120, "віддаленого клієнта", size=10, color=MUTED))
    p.append(text(100, 142, "(Потенційний експлойт)", size=9, color=POS))

    # Стрілка мережі
    p.append(arrow(170, 105, 215, 105, color=POS, sw=2))

    # Непривілейований процес (Пісочниця / Воркер)
    p.append(rect(220, 45, 230, 120, fill="#f0f9ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(335, 72, "Ізольований парсер (Worker)", size=11, color=NEG, bold=True))
    p.append(text(335, 95, "UID: nobody, chroot(/var/empty)", size=9, color=INK))
    p.append(text(335, 115, "Seccomp: read, write, exit_group", size=9, color=NEG, bold=True))
    p.append(text(335, 135, "Заборонено: open, exec, socket", size=9, color=POS))
    p.append(text(335, 153, "Злам тут НЕ дає доступу до ОС!", size=9, color=FIELD, bold=True))

    # Межа між воркером та майстром (IPC)
    p.append(line(470, 30, 470, 185, color=POS, sw=2, dash="4,3"))
    p.append(text(470, 22, "Межа IPC", size=9, color=POS, bold=True))

    # Суворий IPC канал
    p.append(arrow(450, 105, 485, 105, color=LINE, sw=2))
    p.append(text(470, 95, "IPC", size=9, color=LINE, bold=True))

    # Привілейований монітор (Master / Broker)
    p.append(rect(490, 45, 240, 120, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(610, 72, "Привілейований брокер (Master)", size=11, color=FIELD, bold=True))
    p.append(text(610, 95, "UID: root (керує ключами)", size=9, color=INK))
    p.append(text(610, 115, "Валідує десеріалізований DTO", size=9, color=FIELD, bold=True))
    p.append(text(610, 135, "Відкриває ресурси на замовлення", size=9, color=INK))
    p.append(text(610, 153, "НЕ парсить сирий мережевий потік", size=9, color=FIELD))

    # Нижня пояснювальна таблиця
    p.append(rect(30, 195, 700, 95, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(380, 220, "Принцип двоконтурного розділення привілеїв (OpenSSH / Chromium Model):", size=11, color=INK, bold=True))
    p.append(text(380, 243, "• Складний парсинг і обробка вхідних даних замкнені у безпривілейованому Seccomp-фільтрі.", size=10, color=INK))
    p.append(text(380, 263, "• Привілейований процес виконує лише тривіальну перевірку суворо типізованих повідомлень через сокет.", size=10, color=INK))
    p.append(text(380, 281, "• Компрометація воркера через переповнення буфера стримується ядром і не виходить за межі пісочниці.", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "privilege-separated-architecture.svg"), W, H, *p,
           title="Архітектура розділення привілеїв (Privilege Separation)")


# ── 4. double-fetch-toctou: Подвійна вибірка через межу пам'яті ──────────────
def fig_double_fetch():
    W, H = 760, 310
    p = []

    # Простір користувача (Недовірена пам'ять)
    p.append(rect(30, 45, 310, 235, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(185, 70, "Простір користувача (Ring 3)", size=12, color=POS, bold=True))
    p.append(text(185, 92, "Спільна пам'ять або буфер виклику", size=10, color=MUTED))

    # Буфер у юзерспейсі
    p.append(rect(50, 110, 270, 70, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(text(185, 133, "struct Request { uint32_t size; void* ptr; }", size=10, color=INK, bold=True))
    p.append(text(185, 155, "Початково: size = 64  (Перевірка пройшла)", size=9, color=FIELD))
    p.append(text(185, 170, "Атака: потік мутує size = 0xFFFFFFFF!", size=9, color=POS, bold=True))

    p.append(text(185, 210, "Паралельний ворожий потік", size=10, color=POS, bold=True))
    p.append(text(185, 230, "Мутує пам'ять у шпарині між", size=9, color=INK))
    p.append(text(185, 248, "перевіркою та використанням", size=9, color=INK))

    # Межа між User та Kernel
    p.append(line(370, 30, 370, 290, color=POS, sw=2, dash="4,3"))
    p.append(text(370, 20, "Межа User / Kernel", size=10, color=POS, bold=True))

    # Простір ядра (Привілейований)
    p.append(rect(400, 45, 330, 235, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(565, 70, "Простір ядра (Ring 0)", size=12, color=FIELD, bold=True))

    # Крок 1: Перевірка
    p.append(rect(420, 95, 290, 45, fill="#ffffff", stroke=INK, sw=1.2, rx=6))
    p.append(text(565, 115, "1. Перша вибірка (Check):", size=10, color=INK, bold=True))
    p.append(text(565, 130, "Зчитує size (64). Перевірка: 64 <= MAX_BUF (OK)", size=9, color=FIELD))

    # Шпарина часу
    p.append(text(565, 158, "⏱ Шпарина гонки TOCTOU (Race Window)", size=10, color=POS, bold=True))

    # Крок 2: Використання
    p.append(rect(420, 175, 290, 45, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    p.append(text(565, 195, "2. Друга вибірка (Use):", size=10, color=POS, bold=True))
    p.append(text(565, 210, "Зчитує size вдруге (0xFFFFFFFF) → переповнення!", size=9, color=POS, bold=True))

    # Правильне рішення
    p.append(rect(420, 230, 290, 40, fill="#e8f8f0", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(565, 248, "Захист: копіювання в локальний стек якраз 1 раз", size=9, color=FIELD, bold=True))
    p.append(text(565, 262, "copy_from_user() перед будь-якою валідацією!", size=9, color=FIELD))

    # Стрілки зчитування
    p.append(arrow(320, 130, 415, 115, color=FIELD, sw=1.8))
    p.append(arrow(320, 155, 415, 195, color=POS, sw=1.8))

    render(os.path.join(OUT, "double-fetch-toctou.svg"), W, H, *p,
           title="Атака подвійної вибірки (Double-Fetch) через межу спільної пам'яті")


if __name__ == "__main__":
    fig_boundary_levels()
    fig_confused_deputy()
    fig_privilege_separated()
    fig_double_fetch()
    print("Figures generated successfully.")
