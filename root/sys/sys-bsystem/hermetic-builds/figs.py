# -*- coding: utf-8 -*-
"""Фігури до теми «Герметичні системи збірки: модель Bazel та Buck2»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"
CLEAN = "#eaf7ef"
PANEL = "#f8fafc"


# ── 1. Негерметична збірка проти герметичної моделі ─────────────────────────
def fig_traditional_vs_hermetic():
    W, H = 1040, 520
    p = []

    p.append(text(520, 32, "Порівняння традиційної та герметичної систем збірки", size=17, bold=True))

    # Ліва колонка: Негерметична збірка (Make / CMake)
    p.append(rect(40, 55, 450, 445, fill=PANEL, stroke=POS, sw=1.5))
    p.append(text(265, 85, "Традиційна система (Make / CMake)", size=15, bold=True, color=POS))

    p.append(fitbox(65, 105, 400, 45, "Неконтрольовані системні канали", size=13, bold=True, fill=DIRTY, stroke=POS))

    p.append(fitbox(65, 160, 190, 42, "Системний /usr/include", size=12, fill=BG))
    p.append(fitbox(275, 160, 190, 42, "Бібліотеки з /usr/lib", size=12, fill=BG))
    p.append(fitbox(65, 210, 190, 42, "Змінні $PATH, $LD_LIB", size=12, fill=BG))
    p.append(fitbox(275, 210, 190, 42, "Мережа: curl / git clone", size=12, fill=BG))
    p.append(fitbox(65, 260, 190, 42, "Локальний компілятор", size=12, fill=BG))
    p.append(fitbox(275, 260, 190, 42, "Час хоста та /tmp", size=12, fill=BG))

    p.append(fitbox(65, 315, 400, 65, "Приховані недекларовані зв'язки:\nрезультат залежить від стану конкретної ОС,\nвстановлених пакунків та версії середовища", size=12, fill=BG, stroke=MUTED))

    p.append(fitbox(65, 395, 400, 45, "«Працює лише на моїй машині»", size=13, bold=True, fill=DIRTY, stroke=POS))
    p.append(fitbox(65, 448, 400, 38, "Кеш спільних збірок розвалюється", size=12, fill=BG, color=POS))

    # Права колонка: Герметична модель (Bazel / Buck2)
    p.append(rect(550, 55, 450, 445, fill=PANEL, stroke=FIELD, sw=1.5))
    p.append(text(775, 85, "Герметична модель (Bazel / Buck2)", size=15, bold=True, color=FIELD))

    p.append(fitbox(575, 105, 400, 45, "Повна ізоляція та явні входи", size=13, bold=True, fill=CLEAN, stroke=FIELD))

    p.append(fitbox(575, 160, 190, 42, "Action Graph: явні файли", size=12, fill=BG))
    p.append(fitbox(785, 160, 190, 42, "Hermetic sysroot із CAS", size=12, fill=BG))
    p.append(fitbox(575, 210, 190, 42, "Очищене середовище", size=12, fill=BG))
    p.append(fitbox(785, 210, 190, 42, "Мережу заблоковано", size=12, fill=BG))
    p.append(fitbox(575, 260, 190, 42, "Hermetic Clang/GCC/Rust", size=12, fill=BG))
    p.append(fitbox(785, 260, 190, 42, "Sandbox: Linux namespaces", size=12, fill=BG))

    p.append(fitbox(575, 315, 400, 65, "Чиста математична функція:\nOutputs = Action(Inputs, Toolchain, Env)\nповна незалежність від конфігурації хоста", size=12, fill=BG, stroke=MUTED))

    p.append(fitbox(575, 395, 400, 45, "100% повторюваність на будь-якому вузлі", size=13, bold=True, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(575, 448, 400, 38, "Безпечний спільний CAS і Remote Execution", size=12, fill=BG, color=FIELD))

    render(os.path.join(IMG, "traditional-vs-hermetic.svg"), W, H, *p,
           title="Традиційна негерметична збірка проти герметичної моделі")


# ── 2. Математична модель герметичної дії ──────────────────────────────────
def fig_hermetic_action_model():
    W, H = 1040, 500
    p = []

    p.append(text(520, 32, "Математична модель герметичної дії (Action Model)", size=17, bold=True))

    # Лівий стовпчик: Чотири входи
    p.append(rect(40, 60, 260, 410, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(170, 88, "Входи дії (Inputs)", size=14.5, bold=True, color=NEG))

    p.append(fitbox(55, 105, 230, 75, "Сирцевий код і заголовки\n(Input Merkle Tree)\nSHA-256 вмісту кожного файлу", size=11.5, fill=BG))
    p.append(fitbox(55, 190, 230, 75, "Hermetic Toolchain\nФіксований двійковий Clang/GCC\nта версія sysroot / libc", size=11.5, fill=BG))
    p.append(fitbox(55, 275, 230, 75, "Команда та прапорці\n[-O2, -fPIC, -DNDEBUG]\nта порядок аргументів", size=11.5, fill=BG))
    p.append(fitbox(55, 360, 230, 95, "Очищене середовище\n(Environment & Platform)\nPATH=/bin, LANG=C, OS=Linux\nархітектура CPU = x86_64", size=11.5, fill=BG))

    # Стрілка зведення до Action Digest
    p.append(arrow(300, 265, 360, 265, color=NEG, sw=2))

    # Центральний блок 1: Action Digest
    p.append(rect(365, 175, 230, 180, fill=CLEAN, stroke=FIELD, sw=2))
    p.append(text(480, 205, "Action Digest", size=15, bold=True, color=FIELD))
    p.append(fitbox(380, 220, 200, 65, "SHA-256 криптографічний геш:\nInputs + Toolchain +\nCommand + Env", size=11.5, fill=BG))
    p.append(fitbox(380, 295, 200, 45, "Унікальний ключ для CAS і AC", size=11.5, bold=True, fill=BG, color=FIELD))

    # Стрілка до Action Runner
    p.append(arrow(595, 265, 655, 265, color=FIELD, sw=2))

    # Центральний блок 2: Action Runner у Sandbox
    p.append(rect(660, 110, 140, 310, fill=PANEL, stroke=LINE, sw=1.8))
    p.append(text(730, 140, "Action Runner", size=14, bold=True))
    p.append(fitbox(670, 160, 120, 95, "Пісочниця\n(Sandbox)\nІзольовані\nNamespaces,\nбез мережі", size=11.5, fill=BG))
    p.append(fitbox(670, 270, 120, 135, "Чиста функція:\nвідсутність\nзовнішніх\nпобічних\nефектів\n(Side-effects)", size=11.5, fill=BG, stroke=FIELD))

    # Стрілка до Outputs
    p.append(arrow(800, 265, 840, 265, color=LINE, sw=2))

    # Правий стовпчик: Детерміновані виходи
    p.append(rect(845, 60, 160, 410, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(925, 88, "Виходи (Outputs)", size=14.5, bold=True, color=FIELD))

    p.append(fitbox(855, 115, 140, 70, "Об'єктні модулі\nmain.o, lib.a\n(SHA-256 Digest)", size=11.5, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(855, 200, 140, 70, "Виконувані файли\nта бібліотеки\n(побайтово сталі)", size=11.5, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(855, 285, 140, 75, "ActionResult\nметадані виходу:\nкод повернення,\nstdout / stderr", size=11.5, fill=BG))
    p.append(fitbox(855, 375, 140, 80, "Збереження\nу CAS сховищі\nза хешем вмісту", size=11.5, bold=True, fill=BG, color=FIELD))

    render(os.path.join(IMG, "hermetic-action-model.svg"), W, H, *p,
           title="Математична модель герметичної дії (Action Model)")


# ── 3. Архітектура пісочниці на рівні ядра Linux ────────────────────────────
def fig_linux_sandbox_architecture():
    W, H = 1040, 520
    p = []

    p.append(text(520, 32, "Анатомія герметичної пісочниці ядра Linux (Linux Sandbox)", size=17, bold=True))

    # Зовнішній контейнер ядра
    p.append(rect(40, 55, 960, 445, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(220, 80, "Хостова операційна система Linux (Ядро / Простір користувача)", size=13.5, bold=True, color=MUTED))

    # Внутрішня ізольована зона пісочниці
    p.append(rect(60, 95, 620, 385, fill=BG, stroke=FIELD, sw=2))
    p.append(text(370, 125, "Ізольований простір пісочниці (Sandbox Isolation)", size=15, bold=True, color=FIELD))

    # Три основні простори імен всередині
    p.append(rect(80, 145, 280, 150, fill=CLEAN, stroke=FIELD, sw=1.3))
    p.append(text(220, 170, "1. Mount Namespace (CLONE_NEWNS)", size=12.5, bold=True, color=FIELD))
    p.append(fitbox(95, 185, 250, 45, "Приватний корінь /sandbox/root\nстворений через pivot_root", size=11.5, fill=BG))
    p.append(fitbox(95, 238, 250, 45, "tmpfs для тимчасових файлів,\nread-only bind mounts для сирців", size=11.5, fill=BG))

    p.append(rect(380, 145, 280, 150, fill=CLEAN, stroke=FIELD, sw=1.3))
    p.append(text(520, 170, "2. Network Namespace (CLONE_NEWNET)", size=12.5, bold=True, color=FIELD))
    p.append(fitbox(395, 185, 250, 45, "Повна відсутність інтерфейсів eth0/wlan\nлише відключений loopback lo", size=11.5, fill=BG))
    p.append(fitbox(395, 238, 250, 45, "Будь-який виклик socket()/connect()\nмиттєво повертає помилку EPERM / ENETDOWN", size=11.5, fill=BG))

    p.append(rect(80, 310, 580, 155, fill=PANEL, stroke=MUTED, sw=1.3))
    p.append(text(370, 335, "3. User Namespace (CLONE_NEWUSER) та Seccomp фільтри", size=12.5, bold=True, color=LINE))
    p.append(fitbox(95, 350, 265, 50, "Мапування UID 0 всередині на\nзвичайний непривілейований UID хоста", size=11.5, fill=BG))
    p.append(fitbox(375, 350, 270, 50, "Заборона системних викликів:\nptrace, reboot, mount, settimeofday", size=11.5, fill=BG))
    p.append(fitbox(95, 408, 550, 45, "Дерево символічних посилань (Symlink Forest):\nкомпілятор бачить лише явно задекларовані входи дії", size=12, bold=True, fill=BG, stroke=FIELD))

    # Права панель: Заблоковані ресурси хоста
    p.append(rect(700, 95, 280, 385, fill=DIRTY, stroke=POS, sw=1.8))
    p.append(text(840, 125, "Заблоковано на рівні ядра", size=14, bold=True, color=POS))

    p.append(fitbox(715, 145, 250, 45, "Хостовий /usr/include та /usr/lib\n(неможливо прочитати заголовки)", size=11.5, fill=BG))
    p.append(fitbox(715, 198, 250, 45, "Каталоги користувача /home\nта конфігурації ~/.bashrc, ~/.ssh", size=11.5, fill=BG))
    p.append(fitbox(715, 251, 250, 45, "Глобальна мережа Internet\n(заборонено curl, git, pip)", size=11.5, fill=BG))
    p.append(fitbox(715, 304, 250, 45, "Системний час хоста\n(стабілізовано через віртуалізацію)", size=11.5, fill=BG))
    p.append(fitbox(715, 357, 250, 45, "Міжпроцесна взаємодія IPC\n(ізоляція спільних черг і пам'яті)", size=11.5, fill=BG))

    p.append(fitbox(715, 415, 250, 50, "Спроба доступу до неоголошеного файлу\nпризводить до негайної помилки ENOENT", size=11.5, bold=True, fill=BG, color=POS))

    render(os.path.join(IMG, "linux-sandbox-architecture.svg"), W, H, *p,
           title="Анатомія герметичної пісочниці ядра Linux")


# ── 4. CAS сховище та конвеєр Remote Build Execution (RBE) ─────────────────
def fig_cas_and_rbe_flow():
    W, H = 1040, 520
    p = []

    p.append(text(520, 32, "Контентно-адресоване сховище (CAS) та конвеєр Remote Execution", size=17, bold=True))

    # Блок 1: Локальний клієнт
    p.append(rect(40, 60, 240, 430, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(160, 88, "1. Клієнт (Bazel / Buck2)", size=14, bold=True, color=NEG))

    p.append(fitbox(55, 105, 210, 55, "Побудова Action Graph\nна основі Starlark правил", size=12, fill=BG))
    p.append(fitbox(55, 170, 210, 65, "Обчислення Action Digest\n(хеш команди, дерева\nвходів, тулчейна та env)", size=12, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(55, 245, 210, 55, "Запит до Action Cache (AC):\n«Чи готова дія з цим хешем?»", size=12, fill=BG))
    p.append(fitbox(55, 310, 210, 80, "Якщо промах кешу:\nзавантаження відсутніх\nблоків коду в CAS\nчерез gRPC протокол", size=12, fill=BG))
    p.append(fitbox(55, 400, 210, 75, "Отримання результату:\nзавантаження артефактів\nабо посилання у CAS", size=12, bold=True, fill=BG, color=FIELD))

    # Стрілка від клієнта до Action Cache
    p.append(arrow(280, 160, 360, 160, color=NEG, sw=2))
    p.append(text(320, 150, "Запит", size=11, italic=True))

    # Блок 2: Action Cache (AC)
    p.append(rect(365, 80, 260, 160, fill=PANEL, stroke=FIELD, sw=1.5))
    p.append(text(495, 105, "2. Action Cache (AC)", size=14, bold=True, color=FIELD))
    p.append(fitbox(380, 120, 230, 45, "Індекс відповідності:\nActionDigest → ActionResultDigest", size=12, fill=BG))
    p.append(fitbox(380, 175, 230, 50, "Cache Hit: повернення результату\n(збірка миттєва, 0 мс на виконання)", size=11.5, bold=True, fill=CLEAN, stroke=FIELD))

    # Стрілка вниз до CAS
    p.append(arrow(495, 240, 495, 290, color=FIELD, sw=2))
    p.append(text(540, 265, "Посилання", size=11, italic=True))

    # Блок 3: Content-Addressed Storage (CAS)
    p.append(rect(365, 295, 260, 195, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(495, 320, "3. CAS (Content-Addressed Storage)", size=13.5, bold=True))
    p.append(fitbox(380, 335, 230, 45, "Незмінне сховище блоків:\nКлюч = SHA-256 вмісту файлу", size=11.5, fill=BG))
    p.append(fitbox(380, 388, 230, 45, "Глобальна дедуплікація:\nспільні блоки для всіх проєктів", size=11.5, fill=BG))
    p.append(fitbox(380, 440, 230, 40, "Зберігає вхідні сирці та готові .o/.a", size=11.5, fill=CLEAN))

    # Стрілка від AC до RBE
    p.append(arrow(625, 160, 710, 160, color=POS, sw=2))
    p.append(text(668, 145, "Cache Miss", size=11, bold=True, color=POS))

    # Блок 4: Remote Build Execution (RBE) Кластер
    p.append(rect(715, 60, 285, 430, fill=PANEL, stroke=LINE, sw=1.5))
    p.append(text(857, 88, "4. RBE Кластер воркерів", size=14, bold=True, color=LINE))

    p.append(fitbox(730, 105, 255, 55, "Пул віддалених воркерів:\nмасштабування на 10 000+ ядер", size=12, fill=BG))
    p.append(fitbox(730, 170, 255, 60, "Завантаження входів із CAS\n(лише тих блоків, яких нема)", size=12, fill=BG))
    p.append(fitbox(730, 240, 255, 75, "Виконання дії в контейнері:\nповна ізоляція (Namespaces),\nдетермінований запуск команди", size=12, bold=True, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(730, 325, 255, 65, "Збереження згенерованих .o\nта stdout/stderr у CAS", size=12, fill=BG))
    p.append(fitbox(730, 400, 255, 75, "Оновлення Action Cache:\nновий ActionResult стає доступним\nдля всіх розробників компанії", size=11.5, bold=True, fill=BG, color=FIELD))

    # Стрілка від RBE назад у CAS
    p.append(arrow(715, 355, 625, 355, color=FIELD, sw=2))

    render(os.path.join(IMG, "cas-and-rbe-flow.svg"), W, H, *p,
           title="Контентно-адресоване сховище та конвеєр Remote Build Execution")


if __name__ == "__main__":
    fig_traditional_vs_hermetic()
    fig_hermetic_action_model()
    fig_linux_sandbox_architecture()
    fig_cas_and_rbe_flow()
    print("готово:", IMG)
