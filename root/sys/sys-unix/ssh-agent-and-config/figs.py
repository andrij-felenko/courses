# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми 'Агент, ~/.ssh/config і перехід через бастіон (ProxyJump)'."""

import sys, os

# 4 рівні вгору до кореня репо, де лежить scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_ssh_agent_protocol():
    """Архітектура ssh-agent: комунікація клієнта з демоном через UNIX-сокет без розкриття закритого ключа."""
    w, h = 980, 530
    frags = []

    # Загальна рамка полотна
    frags.append(rect(10, 10, 960, 510, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(490, 36, "МЕХАНІЗМ ПІДПИСУ SSH-AGENT: ЧОМУ ЗАКРИТИЙ КЛЮЧ НЕ ЗАЛИШАЄ ПАМ'ЯТЬ ДЕМОНА", size=13, color="#0f172a", bold=True))

    # Зона 1: Локальна машина клієнта
    frags.append(rect(25, 55, 595, 450, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(320, 78, "ЛОКАЛЬНА РОБОЧА СТАНЦІЯ (LOCAL HOST)", size=12, color="#334155", bold=True))

    # Блок: Процес ssh (клієнт)
    frags.append(rect(40, 95, 250, 190, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(165, 118, "Процес клієнта (ssh / git)", size=11, color="#1e40af", bold=True))
    frags.append(fitbox(50, 130, 230, 45, "1. Зчитує $SSH_AUTH_SOCK\n2. Отримує challenge від сервера\n3. Формує запит на підпис", size=10, pad=4, fill="#ffffff", stroke="#93c5fd"))
    frags.append(fitbox(50, 185, 230, 90, "Клієнт НЕ має доступу\nдо відкритого закритого ключа.\nВін лише ретранслює\nкриптографічний виклик\nта отримує готовий підпис.", size=9, pad=4, fill="#dbeafe", stroke="#2563eb", color="#1e3a8a"))

    # Блок: Демон ssh-agent
    frags.append(rect(345, 95, 260, 395, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    frags.append(text(475, 118, "Демон ssh-agent (PID)", size=11, color="#166534", bold=True))
    frags.append(fitbox(355, 130, 240, 60, "Захищена оперативна пам'ять:\n- Розшифровані ключі (Ed25519/RSA)\n- Виклик mlock() (захист від swap)\n- Захист від coredump", size=9, pad=4, fill="#ffffff", stroke="#86efac"))
    frags.append(fitbox(355, 200, 240, 75, "Контроль доступу та життя:\n- Таймаут життя (ssh-add -t 1h)\n- Підтвердження (ssh-add -c)\n  -> виклик SSH_ASKPASS\n- Видалення з пам'яті (ssh-add -D)", size=9, pad=4, fill="#ffffff", stroke="#86efac"))
    frags.append(fitbox(355, 285, 240, 85, "Обробник криптографії:\n1. Знаходить ключ за відкритим блобом\n2. Перевіряє права/підтвердження\n3. Обчислює цифровий підпис\n   (Ed25519_sign / RSA_sign)", size=9, pad=4, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True))
    frags.append(fitbox(355, 380, 240, 95, "Жоден байт закритого ключа\nніколи не передається через сокет\nі не записується на диск.\nНазовні виходить лише підпис.", size=9, pad=4, fill="#fef2f2", stroke="#ef4444", color="#991b1b", bold=True))

    # Блок: UNIX Domain Socket
    frags.append(rect(40, 305, 250, 185, fill="#faf5ff", stroke="#a855f7", sw=1.5, rx=6))
    frags.append(text(165, 325, "UNIX-сокет $SSH_AUTH_SOCK", size=11, color="#6b21a8", bold=True))
    frags.append(fitbox(50, 335, 230, 40, "Шлях: /tmp/ssh-XXXXXX/agent.PID\nПрава каталогу: 0700 (тільки UID)", size=9, pad=3, fill="#ffffff", stroke="#d8b4fe"))
    frags.append(fitbox(50, 385, 230, 95, "Протокол агента (Agent Wire Protocol):\n-> SSH_AGENTC_REQUEST_IDENTITIES\n<- SSH_AGENT_IDENTITIES_ANSWER\n-> SSH_AGENTC_SIGN_REQUEST (data)\n<- SSH_AGENT_SIGN_RESPONSE (sig)", size=9, pad=4, fill="#f3e8ff", stroke="#9333ea", color="#581c87"))

    # Стрілка між клієнтом і сокетом
    frags.append(arrow(165, 285, 165, 305, color="#7c3aed", sw=2.0))
    # Стрілка між сокетом і агентом
    frags.append(arrow(290, 395, 345, 395, color="#7c3aed", sw=2.0))

    # Зона 2: Віддалений сервер SSH
    frags.append(rect(635, 55, 330, 450, fill="#fff7ed", stroke="#fdba74", sw=1.5, rx=8))
    frags.append(text(800, 78, "ВІДДАЛЕНИЙ СЕРВЕР (SSHD)", size=12, color="#9a3412", bold=True))

    frags.append(fitbox(645, 95, 310, 65, "1. Генерує випадковий виклик\n   (Challenge / Session ID)\n2. Надсилає виклик клієнту\n   для підтвердження володіння ключем", size=10, pad=4, fill="#ffffff", stroke="#f97316"))
    frags.append(fitbox(645, 170, 310, 85, "3. Отримує готовий підпис від клієнта\n4. Звіряє підпис із відкритим ключем\n   у файлі ~/.ssh/authorized_keys\n5. Успіх: відкриває сеанс користувача", size=10, pad=4, fill="#ffedd5", stroke="#ea580c", color="#7c2d12", bold=True))

    frags.append(fitbox(645, 265, 310, 225, "ЧОМУ FORWARDAGENT НЕБЕЗПЕЧНИЙ:\nЯкщо на сервері ввімкнено ForwardAgent yes,\nвіддалений sshd створює проксі-сокет\nдо твого локального агента.\n\nЗловмисник із правами root на цьому сервері\nможе підключатися до прокинутого сокета\nі підписувати будь-які запити до інших\nтвоїх машин від твого імені, доки відкритий сеанс!\n\nДля переходу через сервери замість цього\nслід використовувати безпечний ProxyJump.", size=9, pad=5, fill="#fef2f2", stroke="#ef4444", color="#991b1b", bold=True))

    render(os.path.join(OUT_DIR, "ssh-agent-protocol.svg"), w, h, *frags)


def fig_proxyjump_tunnel():
    """Схема наскрізного тунелювання ProxyJump через сервер-бастіон."""
    w, h = 980, 500
    frags = []

    frags.append(rect(10, 10, 960, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(490, 36, "АРХІТЕКТУРА PROXYJUMP: НАСКРІЗНИЙ ЗАШИФРОВАНИЙ ТУНЕЛЬ ЧЕРЕЗ БАСТІОН", size=13, color="#0f172a", bold=True))

    # Вузол 1: Клієнтська машина
    frags.append(rect(25, 65, 280, 405, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    frags.append(text(165, 90, "КЛІЄНТ (РОБОЧА СТАНЦІЯ)", size=11, color="#1e40af", bold=True))
    frags.append(fitbox(35, 105, 260, 65, "Команда запуску:\nssh -J bastion.corp target.internal\nабо директива у ~/.ssh/config:\nProxyJump bastion.corp", size=9, pad=4, fill="#ffffff", stroke="#3b82f6"))
    frags.append(fitbox(35, 180, 260, 95, "Шар 1 (Зовнішній):\n- З'єднання з bastion:22\n- Автентифікація на бастіоні\n- Запит каналу direct-tcpip\n  (до target.internal:22)", size=9, pad=4, fill="#dbeafe", stroke="#2563eb", color="#1e3a8a"))
    frags.append(fitbox(35, 285, 260, 105, "Шар 2 (Наскрізний внутрішній):\n- Ініціалізація SSH-сеансу до target\n- Обмін ключами KEX безпосередньо з target\n- Автентифікація власним ключем target\n- Наскрізне симетричне шифрування", size=9, pad=4, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True))
    frags.append(fitbox(35, 400, 260, 55, "Бастіон НЕ має доступу\nдо ключів та сеансу target!", size=9, pad=3, fill="#ffffff", stroke="#86efac", color="#166534", bold=True))

    # Вузол 2: Сервер-бастіон
    frags.append(rect(340, 65, 300, 405, fill="#faf5ff", stroke="#d8b4fe", sw=1.5, rx=8))
    frags.append(text(490, 90, "БАСТІОН / JUMP HOST (ПУБЛІЧНИЙ IP)", size=11, color="#6b21a8", bold=True))
    frags.append(fitbox(355, 105, 270, 75, "Мережевий інтерфейс:\n- Зовнішній IP (доступний з Інтернету)\n- Внутрішній IP (у приватній підмережі)\n- Слухає sshd на порту 22", size=9, pad=4, fill="#ffffff", stroke="#a855f7"))
    frags.append(fitbox(355, 190, 270, 115, "Канал direct-tcpip в дії:\n1. Приймає канальний запит від клієнта\n2. Викликає connect() до 10.0.1.50:22\n3. Здійснює прозоре пересилання байтів\n   між каналом SSH та TCP-сокетом\n4. Жодної дешифрації внутрішнього SSH!", size=9, pad=5, fill="#f3e8ff", stroke="#9333ea", color="#581c87", bold=True))
    frags.append(fitbox(355, 315, 270, 140, "ЧОМУ PROXYJUMP КРАЩИЙ ЗА PROXYCOMMAND NC:\n- Не запускає окремий дочірній процес nc/ssh\n- Використовує штатний мультиплексований\n  канал direct-tcpip протоколу OpenSSH\n- Менше накладних витрат на форки та пайпи\n- Підтримує каскади: ProxyJump b1,b2,b3", size=9, pad=5, fill="#ffffff", stroke="#c084fc", color="#581c87"))

    # Вузол 3: Цільовий сервер
    frags.append(rect(675, 65, 280, 405, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    frags.append(text(815, 90, "ЦІЛЬОВИЙ СЕРВЕР (10.0.1.50)", size=11, color="#166534", bold=True))
    frags.append(fitbox(685, 105, 260, 75, "Ізольована внутрішня мережа:\n- Приватна IP-адреса 10.0.1.50\n- Відсутній прямий маршрут з Інтернету\n- Приймає вхідний TCP-порт 22", size=9, pad=4, fill="#ffffff", stroke="#22c55e"))
    frags.append(fitbox(685, 190, 260, 115, "Термінація SSH-сеансу:\n- Бачить вхідне TCP-з'єднання з IP бастіону\n- Але виконує криптографічне рукостискання\n  безпосередньо з вихідним клієнтом\n- Звіряє ключ клієнта в authorized_keys\n- Відкриває захищену PTY/shell сесію", size=9, pad=5, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True))
    frags.append(fitbox(685, 315, 260, 140, "Безпека архітектури:\nНавіть якщо бастіон скомпрометовано,\nзловмисник бачить лише шифротекст\nі не може підслухати або підробити\nтрафік між клієнтом і цільовим вузлом\n(за умови валідації host key цілі).", size=9, pad=5, fill="#fef2f2", stroke="#ef4444", color="#991b1b"))

    # Стрілки тунелювання
    frags.append(arrow(305, 220, 340, 220, color="#2563eb", sw=2.5))
    frags.append(arrow(640, 220, 675, 220, color="#16a34a", sw=2.5))

    render(os.path.join(OUT_DIR, "proxyjump-tunnel.svg"), w, h, *frags)


def fig_connection_multiplexing():
    """Мультиплексування з'єднань через ControlMaster і локальний сокет керування."""
    w, h = 980, 500
    frags = []

    frags.append(rect(10, 10, 960, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(490, 36, "МУЛЬТИПЛЕКСУВАННЯ OPENSSH (CONTROLMASTER): ОДНЕ TCP-З'ЄДНАННЯ НА ДЕСЯТКИ СЕАНСІВ", size=13, color="#0f172a", bold=True))

    # Ліва колонка: Клієнтська сторона
    frags.append(rect(25, 60, 520, 415, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(285, 83, "ЛОКАЛЬНА РОБОЧА СТАНЦІЯ (OPENSSH CLIENTS)", size=12, color="#334155", bold=True))

    # Майстер-процес
    frags.append(rect(40, 100, 235, 160, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=6))
    frags.append(text(157, 122, "SSH Master Process", size=11, color="#1e40af", bold=True))
    frags.append(fitbox(50, 133, 215, 115, "Перший виклик (ControlMaster auto):\n- Виконує повний TCP + SSH Handshake\n- Створює керівний UNIX-сокет ControlPath\n- ControlPersist 10m: залишається демоном\n  у фоні після завершення першої сесії\n- Тримає одне живе TCP-з'єднання", size=9, pad=4, fill="#ffffff", stroke="#93c5fd"))

    # Слейв-процеси
    frags.append(rect(40, 275, 235, 185, fill="#f0fdf4", stroke="#22c55e", sw=1.5, rx=6))
    frags.append(text(157, 297, "Slave Clients (Git / SCP / CLI)", size=11, color="#166534", bold=True))
    frags.append(fitbox(50, 310, 215, 140, "Наступні виклики ssh / scp / rsync:\n- Перевіряють наявність ControlPath\n- Підключаються до локального UNIX-сокета\n- Запитують відкриття нового каналу\n- Час старту: 2-5 мс замість 200-500 мс!\n- Нульові витрати на повторну авторизацію\n- Ідеально для Ansible та CI/CD", size=9, pad=4, fill="#dcfce7", stroke="#16a34a", color="#14532d", bold=True))

    # Локальний сокет ControlPath
    frags.append(rect(300, 170, 230, 180, fill="#faf5ff", stroke="#a855f7", sw=1.5, rx=6))
    frags.append(text(415, 195, "Сокет ControlPath", size=11, color="#6b21a8", bold=True))
    frags.append(fitbox(310, 210, 210, 45, "~/.ssh/sockets/%r@%h:%p\n(права 0600 на сокет)", size=9, pad=3, fill="#ffffff", stroke="#d8b4fe"))
    frags.append(fitbox(310, 265, 210, 75, "Передає дескриптори та\nкерівні команди:\nssh -O check (статус)\nssh -O stop (м'яка зупинка)\nssh -O exit (негайний вихід)", size=9, pad=4, fill="#f3e8ff", stroke="#9333ea", color="#581c87"))

    # Стрілки взаємодії всередині локальної машини
    frags.append(arrow(275, 180, 300, 220, color="#3b82f6", sw=2.0))
    frags.append(arrow(275, 340, 300, 280, color="#22c55e", sw=2.0))

    # Права колонка: Мережа та Віддалений SSH-сервер
    frags.append(rect(570, 60, 385, 415, fill="#fff7ed", stroke="#fdba74", sw=1.5, rx=8))
    frags.append(text(762, 83, "ВІДДАЛЕНИЙ СЕРВЕР (SSHD)", size=12, color="#9a3412", bold=True))

    frags.append(fitbox(585, 100, 355, 90, "Єдине TCP-з'єднання (порт 22):\n- Один TCP Handshake (SYN -> SYN-ACK -> ACK)\n- Одне узгодження шифрів та KEX (Diffie-Hellman)\n- Одна перевірка автентифікації користувача\n- Сервер бачить лише один клієнтський процес", size=10, pad=5, fill="#ffffff", stroke="#f97316"))

    frags.append(fitbox(585, 205, 355, 130, "Мультиплексовані SSH-канали (SSH Channels):\n[Канал 0]: Інтерактивна оболонка (Shell session)\n[Канал 1]: Передавання файлу (SCP / SFTP subsystem)\n[Канал 2]: Команда Git (git-receive-pack)\n[Канал 3]: Виклик Ansible ad-hoc модуля\nВсі канали працюють паралельно в одному потоці TCP.", size=9, pad=5, fill="#ffedd5", stroke="#ea580c", color="#7c2d12", bold=True))

    frags.append(fitbox(585, 350, 355, 110, "Крайові випадки та обриви:\nЯкщо мережа розривається або падає Master,\nусі активні канали обриваються одночасно.\nSlave-клієнт при зникненні Master автоматично\nстворює новий Master (при ControlMaster auto)\nпісля очищення мертвого сокета.", size=9, pad=5, fill="#fef2f2", stroke="#ef4444", color="#991b1b"))

    render(os.path.join(OUT_DIR, "connection-multiplexing.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_ssh_agent_protocol()
    fig_proxyjump_tunnel()
    fig_connection_multiplexing()
    print("Фігури успішно згенеровано в", OUT_DIR)
