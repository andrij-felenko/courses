# -*- coding: utf-8 -*-
import sys
import os

# scripts/ directory is 4 levels up: book/programming/security/least-privilege -> ../../../..
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. least-privilege-vs-ambient-authority ──────────────────────────────────
def fig_least_privilege_vs_ambient_authority():
    W, H = 840, 340
    p = []

    # Фон лівої панелі — Ambient Authority / Monolithic Root (Небезпечно)
    p.append(rect(20, 20, 385, 300, fill="#fdf2f2", stroke=POS, sw=1.8, rx=10))
    p.append(text(212, 48, "Надлишкова довіра (Ambient Authority)", size=13, color=POS, bold=True))
    p.append(text(212, 68, "Монолітний процес із правами root / SYSTEM", size=10, color=MUTED))

    # Блок монолітного процесу
    p.append(rect(40, 85, 345, 105, fill="#ffffff", stroke=POS, sw=1.4, rx=8))
    p.append(text(212, 108, "Вебсервер / Демон обробки (root)", size=12, color=INK, bold=True))
    p.append(text(212, 128, "Парсер HTTP/PNG + Запис конфігу + Raw-сокети", size=10, color=MUTED))
    p.append(rect(55, 142, 315, 36, fill="#fee2e2", stroke=POS, sw=1.0, rx=5))
    p.append(text(212, 164, "Уразливість парсера = повне захоплення системи", size=10, color=POS, bold=True))

    # Стрілки доступу від моноліту
    p.append(arrow(110, 190, 110, 225, color=POS, sw=1.8))
    p.append(arrow(212, 190, 212, 225, color=POS, sw=1.8))
    p.append(arrow(315, 190, 315, 225, color=POS, sw=1.8))

    # Ресурси ОС під загрозою
    p.append(rect(40, 230, 100, 70, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(90, 255, "/etc/shadow", size=10, color=INK, bold=True))
    p.append(text(90, 275, "паролі ОС", size=9, color=POS))

    p.append(rect(162, 230, 100, 70, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(212, 255, "Пам'ять ядра", size=10, color=INK, bold=True))
    p.append(text(212, 275, "RAW / eBPF", size=9, color=POS))

    p.append(rect(285, 230, 100, 70, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(335, 255, "Файли користувача", size=10, color=INK, bold=True))
    p.append(text(335, 275, "видалення / шифр", size=9, color=POS))


    # Фон правої панелі — Least Privilege (Безпечно)
    p.append(rect(435, 20, 385, 300, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(627, 48, "Принцип найменших привілеїв (PoLP)", size=13, color=FIELD, bold=True))
    p.append(text(627, 68, "Ізольовані воркери з мінімальним контекстом", size=10, color=MUTED))

    # Блок ізольованого воркера
    p.append(rect(455, 85, 345, 105, fill="#ffffff", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(627, 108, "Парсер клієнтських даних (nobody)", size=12, color=INK, bold=True))
    p.append(text(627, 128, "seccomp-bpf + chroot + 0 capabilities", size=10, color=MUTED))
    p.append(rect(470, 142, 315, 36, fill="#dcfce7", stroke=FIELD, sw=1.0, rx=5))
    p.append(text(627, 164, "Уразливість замкнена в пісочниці без прав", size=10, color=FIELD, bold=True))

    # Стрілки доступу від воркера
    p.append(arrow(525, 190, 525, 225, color=POS, sw=1.8))
    p.append(arrow(627, 190, 627, 225, color=FIELD, sw=1.8))
    p.append(arrow(730, 190, 730, 225, color=POS, sw=1.8))

    # Блоковані та дозволені ресурси
    p.append(rect(455, 230, 100, 70, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(505, 255, "/etc/shadow", size=10, color="#94a3b8", bold=True))
    p.append(text(505, 275, "EACCES (заборонено)", size=9, color=POS, bold=True))

    p.append(rect(577, 230, 100, 70, fill="#ffffff", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(627, 255, "IPC сокет", size=10, color=INK, bold=True))
    p.append(text(627, 275, "тільки валідні DTO", size=9, color=FIELD))

    p.append(rect(700, 230, 100, 70, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(750, 255, "Диск і мережа", size=10, color="#94a3b8", bold=True))
    p.append(text(750, 275, "EPERM (немає прав)", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "least-privilege-vs-ambient-authority.svg"), W, H, *p,
           title="Порівняння моделі надлишкової довіри та принципу найменших привілеїв")


# ── 2. deny-by-default-evaluation-flow ───────────────────────────────────────
def fig_deny_by_default_evaluation_flow():
    W, H = 840, 310
    p = []

    # Запит ліворуч
    p.append(rect(30, 105, 140, 90, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(100, 135, "Вхідний запит", size=12, color=INK, bold=True))
    p.append(text(100, 155, "Суб'єкт S", size=10, color=MUTED))
    p.append(text(100, 173, "Об'єкт O, дія R", size=10, color=MUTED))

    # Стрілка до оцінювача
    p.append(arrow(170, 150, 240, 150, color=LINE, sw=2))
    p.append(text(205, 140, "Перевірка", size=10, color=MUTED))

    # Блок алгоритму Deny-by-Default
    p.append(rect(240, 40, 340, 220, fill="#f0f4f8", stroke=NEG, sw=1.8, rx=10))
    p.append(text(410, 68, "Оцінювач політики (PDP)", size=13, color=NEG, bold=True))
    p.append(text(410, 88, "Базовий стан: verdict = DENY", size=11, color=POS, bold=True))

    # Внутрішня умова перевірки
    p.append(rect(260, 105, 300, 60, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(410, 128, "Чи існує ЯВНЕ правило дозволу?", size=11, color=INK, bold=True))
    p.append(text(410, 148, "(Explicit Allow Rule Match)", size=10, color=MUTED))

    p.append(rect(260, 180, 300, 65, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(410, 202, "Чи відсутні правила явного блокування?", size=10, color=INK))
    p.append(text(410, 220, "Deny rules override / Guards", size=9, color=MUTED))

    # Стрілка Так -> Дозвіл (Вгору праворуч)
    p.append(arrow(580, 120, 660, 90, color=FIELD, sw=2))
    p.append(text(615, 95, "ТАК", size=10, color=FIELD, bold=True))

    p.append(rect(660, 50, 150, 80, fill="#eaf6ec", stroke=FIELD, sw=2, rx=8))
    p.append(text(735, 82, "ALLOW", size=14, color=FIELD, bold=True))
    p.append(text(735, 104, "Доступ надано", size=11, color=INK))

    # Стрілка Ні / Невідомо -> Відмова (Вниз праворуч)
    p.append(arrow(580, 180, 660, 210, color=POS, sw=2))
    p.append(text(615, 205, "НІ / Немає правила", size=10, color=POS, bold=True))

    p.append(rect(660, 170, 150, 80, fill="#fdecea", stroke=POS, sw=2, rx=8))
    p.append(text(735, 202, "DENY (За замовчуванням)", size=12, color=POS, bold=True))
    p.append(text(735, 224, "Блокування запиту", size=11, color=INK))

    render(os.path.join(OUT, "deny-by-default-evaluation-flow.svg"), W, H, *p,
           title="Алгоритм обчислення дозволу за моделлю Deny-by-Default")


# ── 3. privilege-separation-architecture ─────────────────────────────────────
def fig_privilege_separation_architecture():
    W, H = 840, 330
    p = []

    # Мережеві пакети ззовні
    p.append(rect(20, 115, 120, 85, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(80, 145, "Недовірена", size=11, color=INK, bold=True))
    p.append(text(80, 163, "мережа", size=11, color=INK, bold=True))
    p.append(text(80, 182, "сирі байти", size=9, color=MUTED))

    # Стрілка входу до недоваженого воркера
    p.append(arrow(140, 155, 210, 155, color=POS, sw=2))
    p.append(text(175, 145, "TCP", size=10, color=POS, bold=True))

    # Непривілейований процес (Worker / Sandbox)
    p.append(rect(210, 45, 260, 240, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=10))
    p.append(text(340, 75, "Непривілейований воркер", size=12, color=NEG, bold=True))
    p.append(text(340, 95, "UID=65534 (nobody), GID=65534", size=10, color=MUTED))

    p.append(rect(225, 115, 230, 50, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(340, 135, "Парсер протоколу / Декодер", size=10, color=INK, bold=True))
    p.append(text(340, 152, "Обробка вхідних даних", size=9, color=MUTED))

    p.append(rect(225, 175, 230, 95, fill="#ffffff", stroke=NEG, sw=1.2, rx=6))
    p.append(text(340, 195, "Обмеження середовища:", size=10, color=NEG, bold=True))
    p.append(text(340, 215, "• seccomp: read, write, exit", size=9, color=INK))
    p.append(text(340, 233, "• chroot: порожня тека (/var/empty)", size=9, color=INK))
    p.append(text(340, 251, "• caps: 0 (повна відсутність)", size=9, color=INK))

    # Канал IPC (socketpair / UNIX Domain Socket)
    p.append(rect(485, 120, 95, 80, fill="#ffffff", stroke="#475569", sw=1.5, rx=6))
    p.append(text(532, 145, "IPC", size=11, color="#475569", bold=True))
    p.append(text(532, 163, "socketpair", size=9, color=MUTED))
    p.append(text(532, 181, "SCM_RIGHTS", size=9, color=MUTED))

    # Стрілки зв'язку воркер <-> брокер
    p.append(arrow(470, 148, 490, 148, color=NEG, sw=1.6))
    p.append(arrow(490, 172, 470, 172, color=FIELD, sw=1.6))
    p.append(arrow(575, 148, 595, 148, color=NEG, sw=1.6))
    p.append(arrow(595, 172, 575, 172, color=FIELD, sw=1.6))

    # Привілейований монітор (Broker / Master)
    p.append(rect(595, 45, 225, 240, fill="#fdf6e2", stroke="#b58900", sw=1.8, rx=10))
    p.append(text(707, 75, "Привілейований монітор", size=12, color="#b58900", bold=True))
    p.append(text(707, 95, "UID=0 (root) або виділений сервіс", size=10, color=MUTED))

    p.append(rect(610, 115, 195, 48, fill="#ffffff", stroke="#b58900", sw=1.2, rx=6))
    p.append(text(707, 134, "Валідація запитів IPC", size=10, color=INK, bold=True))
    p.append(text(707, 150, "Сувора схема повідомлень", size=9, color=MUTED))

    p.append(rect(610, 175, 195, 95, fill="#ffffff", stroke="#b58900", sw=1.2, rx=6))
    p.append(text(707, 195, "Привілейовані операції:", size=10, color="#b58900", bold=True))
    p.append(text(707, 215, "• Автентифікація PAM / Shadow", size=9, color=INK))
    p.append(text(707, 233, "• Відкриття файлів / ключів", size=9, color=INK))
    p.append(text(707, 251, "• Запис у захищений аудит-лог", size=9, color=INK))

    render(os.path.join(OUT, "privilege-separation-architecture.svg"), W, H, *p,
           title="Архітектура розділення привілеїв: ізольований воркер і контролюючий монітор")


if __name__ == "__main__":
    fig_least_privilege_vs_ambient_authority()
    fig_deny_by_default_evaluation_flow()
    fig_privilege_separation_architecture()
    print("All figures generated successfully.")
