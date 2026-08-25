# -*- coding: utf-8 -*-
import sys
import os

# scripts/ directory is 4 levels up: root/eng/sf-security/mandatory-access-control -> ../../../..
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. dac-flaw-vs-mac-enforcement ──────────────────────────────────────────
def fig_dac_flaw_vs_mac_enforcement():
    W, H = 840, 350
    p = []

    # Ліва панель: Дискреційний контроль (DAC) — Вразливість
    p.append(rect(20, 20, 385, 310, fill="#fdf2f2", stroke=POS, sw=1.8, rx=10))
    p.append(text(212, 48, "Дискреційний контроль (DAC)", size=13, color=POS, bold=True))
    p.append(text(212, 68, "Фоновий авторитет користувача (UID 1000)", size=10, color=MUTED))

    # Блок троянського процесу користувача
    p.append(rect(40, 88, 345, 95, fill="#ffffff", stroke=POS, sw=1.4, rx=8))
    p.append(text(212, 110, "Скомпрометована утиліта (UID 1000)", size=12, color=INK, bold=True))
    p.append(text(212, 128, "PDF-парсер / Гра / Сторонній скрипт", size=10, color=MUTED))
    p.append(rect(55, 142, 315, 30, fill="#fee2e2", stroke=POS, sw=1.0, rx=5))
    p.append(text(212, 162, "Успадковує повні права користувача на всі його файли", size=9, color=POS, bold=True))

    # Стрілки доступу від трояна
    p.append(arrow(110, 183, 110, 225, color=POS, sw=1.8))
    p.append(arrow(212, 183, 212, 225, color=POS, sw=1.8))
    p.append(arrow(315, 183, 315, 225, color=POS, sw=1.8))

    # Цільові файли користувача
    p.append(rect(40, 230, 100, 80, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(90, 255, "~/.ssh/id_rsa", size=10, color=INK, bold=True))
    p.append(text(90, 275, "Приватні ключі", size=9, color=MUTED))
    p.append(text(90, 295, "ВИТІК ДАНИХ", size=9, color=POS, bold=True))

    p.append(rect(162, 230, 100, 80, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(212, 255, "~/.bashrc", size=10, color=INK, bold=True))
    p.append(text(212, 275, "Конфігурація", size=9, color=MUTED))
    p.append(text(212, 295, "ПЕРЕХОПЛЕННЯ", size=9, color=POS, bold=True))

    p.append(rect(285, 230, 100, 80, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(335, 255, "~/Documents", size=10, color=INK, bold=True))
    p.append(text(335, 275, "Документи", size=9, color=MUTED))
    p.append(text(335, 295, "ШИФРУВАННЯ", size=9, color=POS, bold=True))


    # Права панель: Обов'язковий контроль (MAC) — Захист
    p.append(rect(435, 20, 385, 310, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(627, 48, "Обов'язковий контроль (MAC)", size=13, color=FIELD, bold=True))
    p.append(text(627, 68, "Центральна політика безпеки ядра (SELinux / AppArmor)", size=10, color=MUTED))

    # Блок ізольованого процесу з міткою
    p.append(rect(455, 88, 345, 95, fill="#ffffff", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(627, 110, "Ізольований процес (pdf_t / UID 1000)", size=12, color=INK, bold=True))
    p.append(text(627, 128, "Права обмежені доменом незалежно від UID", size=10, color=MUTED))
    p.append(rect(470, 142, 315, 30, fill="#dcfce7", stroke=FIELD, sw=1.0, rx=5))
    p.append(text(627, 162, "Ядро блокує доступ до нецільових типів об'єктів", size=9, color=FIELD, bold=True))

    # Стрілки доступу від ізольованого процесу
    p.append(arrow(525, 183, 525, 225, color=POS, sw=1.8))
    p.append(arrow(627, 183, 627, 225, color=FIELD, sw=1.8))
    p.append(arrow(730, 183, 730, 225, color=POS, sw=1.8))

    # Результати доступу за політикою
    p.append(rect(455, 230, 100, 80, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(505, 255, "ssh_home_t", size=10, color="#64748b", bold=True))
    p.append(text(505, 275, "Ключі SSH", size=9, color=MUTED))
    p.append(text(505, 295, "БЛОКОВАНО", size=9, color=POS, bold=True))

    p.append(rect(577, 230, 100, 80, fill="#ffffff", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(627, 255, "user_doc_t", size=10, color=INK, bold=True))
    p.append(text(627, 275, "Тільки PDF", size=9, color=FIELD))
    p.append(text(627, 295, "ДОЗВОЛЕНО", size=9, color=FIELD, bold=True))

    p.append(rect(700, 230, 100, 80, fill="#f8fafc", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(750, 255, "user_home_t", size=10, color="#64748b", bold=True))
    p.append(text(750, 275, "Системні файли", size=9, color=MUTED))
    p.append(text(750, 295, "БЛОКОВАНО", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "dac-flaw-vs-mac-enforcement.svg"), W, H, *p,
           title="Порівняння дискреційного (DAC) та обов'язкового (MAC) контролю доступу")


# ── 2. blp-vs-biba-duality ──────────────────────────────────────────────────
def fig_blp_vs_biba_duality():
    W, H = 840, 360
    p = []

    # Ліва панель: Модель Bell-LaPadula (Конфіденційність)
    p.append(rect(20, 20, 385, 320, fill="#f8fafc", stroke=NEG, sw=1.8, rx=10))
    p.append(text(212, 46, "Модель Bell-LaPadula (1973)", size=13, color=NEG, bold=True))
    p.append(text(212, 64, "Мета: Конфіденційність (захист від витоку)", size=10, color=MUTED))

    # Рівні таємності
    p.append(rect(40, 85, 345, 45, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    p.append(text(212, 105, "Top Secret (Висока таємність)", size=11, color=POS, bold=True))
    p.append(text(212, 122, "Об'єкти високої чутливості", size=9, color=MUTED))

    p.append(rect(40, 148, 345, 55, fill="#ffffff", stroke=NEG, sw=1.4, rx=6))
    p.append(text(212, 170, "Суб'єкт S (Рівень Secret)", size=12, color=INK, bold=True))
    p.append(text(212, 190, "Поточний рівень допуску суб'єкта", size=9, color=MUTED))

    p.append(rect(40, 222, 345, 45, fill="#f1f5f9", stroke="#94a3b8", sw=1.2, rx=6))
    p.append(text(212, 242, "Unclassified (Відкриті дані)", size=11, color="#475569", bold=True))
    p.append(text(212, 259, "Загальнодоступні файли", size=9, color=MUTED))

    # Стрілки правил BLP
    # Вгору: Читання заборонено (no read up), Запис дозволено (write up)
    p.append(arrow(110, 148, 110, 130, color=POS, sw=1.6))
    p.append(text(105, 140, "No Read Up", size=9, color=POS, bold=True, anchor="end"))
    p.append(arrow(310, 148, 310, 130, color=FIELD, sw=1.6))
    p.append(text(315, 140, "Write Up", size=9, color=FIELD, bold=True, anchor="start"))

    # Вниз: Читання дозволено (read down), Запис заборонено (no write down)
    p.append(arrow(110, 203, 110, 222, color=FIELD, sw=1.6))
    p.append(text(105, 214, "Read Down", size=9, color=FIELD, bold=True, anchor="end"))
    p.append(arrow(310, 203, 310, 222, color=POS, sw=1.6))
    p.append(text(315, 214, "No Write Down (*)", size=9, color=POS, bold=True, anchor="start"))

    # Резюме правил внизу
    p.append(rect(40, 280, 345, 45, fill="#ffffff", stroke=LINE, sw=1.0, rx=5))
    p.append(text(212, 298, "Simple Security: L(S) ≥ L(O) для читання", size=9, color=INK, bold=True))
    p.append(text(212, 314, "*-Property: L(S) ≤ L(O) для запису", size=9, color=INK, bold=True))


    # Права панель: Модель Biba (Цілісність)
    p.append(rect(435, 20, 385, 320, fill="#f8fafc", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(627, 46, "Модель Biba (1977)", size=13, color=FIELD, bold=True))
    p.append(text(627, 64, "Мета: Цілісність (захист від спотворення)", size=10, color=MUTED))

    # Рівні цілісності
    p.append(rect(455, 85, 345, 45, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=6))
    p.append(text(627, 105, "Kernel / TCB (Висока цілісність)", size=11, color=FIELD, bold=True))
    p.append(text(627, 122, "Критичний код та системні структури", size=9, color=MUTED))

    p.append(rect(455, 148, 345, 55, fill="#ffffff", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(627, 170, "Суб'єкт S (Рівень System / App)", size=12, color=INK, bold=True))
    p.append(text(627, 190, "Поточний рівень довіри суб'єкта", size=9, color=MUTED))

    p.append(rect(455, 222, 345, 45, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    p.append(text(627, 242, "Untrusted / Net (Низька цілісність)", size=11, color=POS, bold=True))
    p.append(text(627, 259, "Неперевірені зовнішні дані з мережі", size=9, color=MUTED))

    # Стрілки правил Biba
    # Вгору: Читання дозволено (read up), Запис заборонено (no write up)
    p.append(arrow(525, 148, 525, 130, color=FIELD, sw=1.6))
    p.append(text(520, 140, "Read Up", size=9, color=FIELD, bold=True, anchor="end"))
    p.append(arrow(725, 148, 725, 130, color=POS, sw=1.6))
    p.append(text(730, 140, "No Write Up (*)", size=9, color=POS, bold=True, anchor="start"))

    # Вниз: Читання заборонено (no read down), Запис дозволено (write down)
    p.append(arrow(525, 203, 525, 222, color=POS, sw=1.6))
    p.append(text(520, 214, "No Read Down", size=9, color=POS, bold=True, anchor="end"))
    p.append(arrow(725, 203, 725, 222, color=FIELD, sw=1.6))
    p.append(text(730, 214, "Write Down", size=9, color=FIELD, bold=True, anchor="start"))

    # Резюме правил внизу
    p.append(rect(455, 280, 345, 45, fill="#ffffff", stroke=LINE, sw=1.0, rx=5))
    p.append(text(627, 298, "Simple Integrity: I(S) ≤ I(O) для читання", size=9, color=INK, bold=True))
    p.append(text(627, 314, "*-Integrity: I(S) ≥ I(O) для запису", size=9, color=INK, bold=True))

    render(os.path.join(OUT, "blp-vs-biba-duality.svg"), W, H, *p,
           title="Дуальність моделей безпеки: Bell-LaPadula (конфіденційність) проти Biba (цілісність)")


# ── 3. lsm-hook-architecture ────────────────────────────────────────────────
def fig_lsm_hook_architecture():
    W, H = 840, 350
    p = []

    # Тло простору користувача
    p.append(rect(20, 20, 220, 310, fill="#f8fafc", stroke=LINE, sw=1.4, rx=8))
    p.append(text(130, 48, "Простір користувача", size=12, color=INK, bold=True))
    p.append(rect(40, 75, 180, 75, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(130, 100, "Процес (task_struct)", size=11, color=INK, bold=True))
    p.append(text(130, 120, "openat(fd, path, flags)", size=10, color=NEG))
    p.append(text(130, 138, "UID / GID / Caps", size=9, color=MUTED))

    # Стрілка системного виклику
    p.append(arrow(220, 112, 270, 112, color=LINE, sw=2.0))
    p.append(text(245, 102, "syscall", size=9, color=MUTED))

    # Тло ядра Linux
    p.append(rect(270, 20, 550, 310, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(545, 48, "Простір ядра Linux (VFS & LSM Framework)", size=13, color=FIELD, bold=True))

    # 1. Перевірка DAC
    p.append(rect(290, 75, 150, 75, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(365, 98, "1. Перевірка DAC", size=11, color=INK, bold=True))
    p.append(text(365, 118, "POSIX ugo/rwx +", size=9, color=MUTED))
    p.append(text(365, 134, "POSIX Capabilities", size=9, color=MUTED))

    # Відмова DAC
    p.append(arrow(365, 150, 365, 185, color=POS, sw=1.6))
    p.append(rect(300, 185, 130, 35, fill="#fee2e2", stroke=POS, sw=1.0, rx=4))
    p.append(text(365, 206, "EACCES / EPERM", size=9, color=POS, bold=True))

    # Успіх DAC -> Хук LSM
    p.append(arrow(440, 112, 480, 112, color=FIELD, sw=1.8))
    p.append(text(460, 102, "OK", size=9, color=FIELD, bold=True))

    # 2. LSM Hook
    p.append(rect(480, 75, 150, 75, fill="#ffffff", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(555, 98, "2. LSM Hook", size=11, color=FIELD, bold=True))
    p.append(text(555, 118, "security_file_open()", size=9, color=INK))
    p.append(text(555, 134, "security_hook_heads", size=9, color=MUTED))

    # Запит до Security Server / AVC
    p.append(arrow(555, 150, 555, 185, color=NEG, sw=1.6))

    # 3. Security Server (SELinux / AppArmor) + AVC
    p.append(rect(460, 185, 190, 75, fill="#ffffff", stroke=NEG, sw=1.4, rx=6))
    p.append(text(555, 206, "3. Security Server / AVC", size=11, color=NEG, bold=True))
    p.append(text(555, 224, "Access Vector Cache", size=9, color=MUTED))
    p.append(text(555, 242, "Контекст (S) ↔ Контекст (O)", size=9, color=INK))

    # Відмова LSM
    p.append(arrow(460, 222, 410, 260, color=POS, sw=1.6))
    p.append(rect(340, 260, 120, 35, fill="#fee2e2", stroke=POS, sw=1.0, rx=4))
    p.append(text(400, 281, "AVC Denial (EACCES)", size=9, color=POS, bold=True))

    # Дозвіл LSM -> Доступ до Inode/Об'єкта
    p.append(arrow(630, 112, 675, 112, color=FIELD, sw=1.8))
    p.append(text(652, 102, "OK", size=9, color=FIELD, bold=True))

    # 4. Об'єкт ядра (Inode / Socket)
    p.append(rect(675, 75, 130, 140, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(740, 98, "4. Об'єкт ядра", size=11, color=INK, bold=True))
    p.append(text(740, 118, "struct inode", size=9, color=MUTED))
    p.append(text(740, 134, "struct file", size=9, color=MUTED))
    p.append(rect(685, 150, 110, 50, fill="#f1f5f9", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(740, 168, "void *security", size=9, color=FIELD, bold=True))
    p.append(text(740, 186, "Мітка об'єкта", size=9, color=MUTED))

    # Фінальний успішний вихід
    p.append(arrow(740, 215, 740, 255, color=FIELD, sw=1.8))
    p.append(rect(675, 255, 130, 40, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(740, 279, "Операцію виконано", size=9, color=FIELD, bold=True))

    render(os.path.join(OUT, "lsm-hook-architecture.svg"), W, H, *p,
           title="Архітектура підсистеми LSM: послідовність перевірок DAC та MAC у ядрі Linux")


# ── 4. selinux-te-and-mls-labels ────────────────────────────────────────────
def fig_selinux_te_and_mls_labels():
    W, H = 840, 350
    p = []

    # Верхня панель: Анатомія контексту безпеки SELinux
    p.append(rect(20, 20, 800, 130, fill="#f8fafc", stroke=NEG, sw=1.6, rx=10))
    p.append(text(420, 44, "Анатомія контексту безпеки (Security Context Label)", size=13, color=NEG, bold=True))

    # 4 поля мітки
    # 1. user
    p.append(rect(40, 60, 180, 70, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(130, 82, "Користувач (User)", size=10, color=MUTED))
    p.append(text(130, 102, "system_u / unconfined_u", size=11, color=INK, bold=True))
    p.append(text(130, 120, "Ідентичність у політиці", size=9, color=MUTED))

    # 2. role
    p.append(rect(230, 60, 180, 70, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(320, 82, "Роль (Role)", size=10, color=MUTED))
    p.append(text(320, 102, "system_r / object_r", size=11, color=INK, bold=True))
    p.append(text(320, 120, "RBAC-прошарок", size=9, color=MUTED))

    # 3. type / domain
    p.append(rect(420, 60, 190, 70, fill="#ffffff", stroke=POS, sw=1.5, rx=6))
    p.append(text(515, 82, "Тип / Домен (Type/Domain)", size=10, color=POS, bold=True))
    p.append(text(515, 102, "httpd_t / container_file_t", size=11, color=POS, bold=True))
    p.append(text(515, 120, "Type Enforcement (TE)", size=9, color=MUTED))

    # 4. level (MLS/MCS)
    p.append(rect(620, 60, 180, 70, fill="#ffffff", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(710, 82, "Рівень (MLS / MCS)", size=10, color=FIELD, bold=True))
    p.append(text(710, 102, "s0:c10,c42", size=11, color=FIELD, bold=True))
    p.append(text(710, 120, "Чутливість : Категорії", size=9, color=MUTED))


    # Нижня панель: Прийняття рішення за Type Enforcement та транзиція
    p.append(rect(20, 165, 800, 165, fill="#ffffff", stroke=LINE, sw=1.4, rx=10))
    p.append(text(420, 188, "Взаємодія доменів та транзиція типів (Domain Transition)", size=12, color=INK, bold=True))

    # Батьківський процес
    p.append(rect(40, 205, 200, 105, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=6))
    p.append(text(140, 226, "Батьківський процес", size=10, color=MUTED))
    p.append(text(140, 246, "init_t / systemd", size=11, color=INK, bold=True))
    p.append(text(140, 266, "Викликає execve()", size=9, color=MUTED))
    p.append(text(140, 286, "на двійковий файл", size=9, color=MUTED))

    # Стрілка виконання
    p.append(arrow(240, 257, 305, 257, color=LINE, sw=1.6))
    p.append(text(272, 247, "execve", size=9, color=MUTED))

    # Двійковий файл (точка входу)
    p.append(rect(305, 205, 180, 105, fill="#fee2e2", stroke=POS, sw=1.2, rx=6))
    p.append(text(395, 226, "Двійковий файл (Entrypoint)", size=10, color=POS, bold=True))
    p.append(text(395, 246, "/usr/sbin/httpd", size=10, color=INK, bold=True))
    p.append(text(395, 266, "Тип: httpd_exec_t", size=10, color=POS, bold=True))
    p.append(text(395, 286, "type_transition rule", size=9, color=MUTED))

    # Стрілка транзиції домену
    p.append(arrow(485, 257, 550, 257, color=FIELD, sw=2.0))
    p.append(text(517, 247, "transition", size=9, color=FIELD, bold=True))

    # Новий ізольований процес
    p.append(rect(550, 205, 250, 105, fill="#dcfce7", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(675, 226, "Новий цільовий домен", size=10, color=FIELD, bold=True))
    p.append(text(675, 246, "httpd_t (обмежений)", size=11, color=FIELD, bold=True))
    p.append(text(675, 266, "Доступ тільки до httpd_sys_content_t", size=9, color=INK))
    p.append(text(675, 286, "Заборонено: shadow_t, user_home_t", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "selinux-te-and-mls-labels.svg"), W, H, *p,
           title="Структура мітки безпеки SELinux та механізм транзиції доменів процесів")


if __name__ == "__main__":
    fig_dac_flaw_vs_mac_enforcement()
    fig_blp_vs_biba_duality()
    fig_lsm_hook_architecture()
    fig_selinux_te_and_mls_labels()
    print("Figures generated successfully.")
