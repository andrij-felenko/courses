# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

BLUE_FILL  = "#eaf0fd"
GREEN_FILL = "#eaf6ef"
RED_FILL   = "#fdecea"
WARM_FILL  = "#fff6e5"
GREY_FILL  = "#f4f6f8"


# ── 1. UID/GID mismatch and User Namespaces mapping ─────────────────────────
def fig_uid_mapping_bind_mount():
    W, H = 1200, 620
    p = []

    # Загальний фон
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    p.append(text(W / 2, 32, "Конфлікт числових UID/GID у томах (Bind Mounts) та User Namespaces", size=18, bold=True, color=INK))

    # Ліва колонка: Хостова файлова система
    lx, ly, lw, lh = 30, 60, 350, 530
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(lx + lw / 2, ly + 28, "Хост: Файлова система (Ext4/XFS)", size=15, bold=True, color=INK))

    p.append(fitbox(lx + 15, ly + 50, 320, 60,
                    "Інод /data/app.db на диску:\nЧислові ідентифікатори: UID = 1000, GID = 1000\nПрава доступу: 0600 (-rw-------)",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.1))

    p.append(fitbox(lx + 15, ly + 130, 320, 100,
                    "Перевірка прав у ядрі:\nЯдро не знає імен («developer», «app»).\nФункція generic_permission() порівнює:\n• inode->i_uid (1000 на диску)\n• current_fsuid() процесу, що робить open()",
                    size=12, fill=GREY_FILL, stroke=MUTED, sw=1.1))

    p.append(fitbox(lx + 15, ly + 250, 320, 110,
                    "Файли, створені root у контейнері:\nЯкщо процес у контейнері має UID = 0 (default),\nнові файли на хості отримують UID = 0 (root).\nЗвичайний користувач хоста не може їх\nредагувати або видалити без sudo.",
                    size=12, fill=RED_FILL, stroke=POS, sw=1.2))

    p.append(fitbox(lx + 15, ly + 380, 320, 120,
                    "Файл /etc/subuid на хості:\nФормат: user:subuid_start:count\ndeveloper:100000:65536\nВиділяє діапазон підпорядкованих UID\nдля використання в User Namespace.",
                    size=12, fill=BLUE_FILL, stroke=NEG, sw=1.1))

    # Середня колонка: Простір імен без мапінгу (Конфлікт)
    mx, my, mw, mh = 410, 60, 360, 530
    p.append(rect(mx, my, mw, mh, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    p.append(text(mx + mw / 2, my + 28, "Сценарій А: Звичайний Bind Mount (Без мапінгу)", size=14, bold=True, color=POS))

    p.append(fitbox(mx + 15, my + 50, 330, 65,
                    "Команда запуску:\ndocker run -v /data:/app/data -u 1001 my-app\nПроцес працює від UID 1001 (USER app).",
                    size=12, fill=GREY_FILL, stroke=LINE, sw=1.1))

    p.append(fitbox(mx + 15, my + 135, 330, 130,
                    "Кроки перевірки VFS:\n1. Контейнерний процес викликає open('/app/data/app.db')\n2. current_fsuid() = 1001\n3. inode->i_uid = 1000 (хостовий власник)\n4. 1001 != 1000, біти 'other' = 000 (заборона)\n5. Результат: EACCES (Permission Denied)!",
                    size=12, fill=RED_FILL, stroke=POS, sw=1.3))

    p.append(fitbox(mx + 15, my + 285, 330, 215,
                    "Чому це ламає середовище:\n• Образ створено під фіксованого USER (UID 1000),\n  а на сервері хостовий каталог належить UID 1005.\n• Спроби обійти через chmod 777 відкривають діру в безпеці.\n• Ручне вирівнювання через --user $(id -u):$(id -g)\n  вимагає синхронізації між усіма вузлами.",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.1))

    # Права колонка: User Namespaces та ID-mapped mounts
    rx, ry, rw, rh = 800, 60, 370, 530
    p.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 28, "Сценарій Б: User Namespaces та ID-mapping", size=14, bold=True, color=FIELD))

    p.append(fitbox(rx + 15, ry + 50, 340, 75,
                    "Мапінг UID (/proc/[pid]/uid_map):\nPodman Rootless / userns-remap:\n0 (всередині)  <--->  1000 (на хості)\n1..65535      <--->  100000..165534",
                    size=12, fill=BLUE_FILL, stroke=NEG, sw=1.1))

    p.append(fitbox(rx + 15, ry + 145, 340, 140,
                    "Трансляція в ядрі (make_kuid / from_kuid):\n1. Процес у контейнері бачить себе як root (UID 0)\n2. Ядро транслює UID 0 -> KUID 1000 на хості\n3. open('/data/app.db') виконується з current_fsuid = 1000\n4. 1000 == 1000 -> Доступ надано (OK)!\n5. Нові файли створюються з UID 1000 на хості.",
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.3))

    p.append(fitbox(rx + 15, ry + 305, 340, 195,
                    "ID-mapped mounts (Linux 5.12+):\n• mount_setattr() прив'язує struct user_namespace\n  безпосередньо до точки монтування.\n• Трансляція відбувається на льоту у VFS без\n  переписування файлів на диску (без chown).\n• Безпечний спільний доступ між різними контейнерами.",
                    size=12, fill=GREY_FILL, stroke=MUTED, sw=1.1))

    return render(os.path.join(IMG, "uid-mapping-bind-mount.svg"), W, H, *p)


# ── 2. Network namespaces and DNS resolution ────────────────────────────────
def fig_container_dns_network_bridge():
    W, H = 1200, 640
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    p.append(text(W / 2, 32, "Мережева ізоляція та розпізнавання імен: Default Bridge проти Custom Network", size=18, bold=True, color=INK))

    # Ліва половина: Default Bridge (docker0)
    lx, ly, lw, lh = 30, 60, 550, 550
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(lx + lw / 2, ly + 28, "Дефолтний міст: docker0 (172.17.0.0/16)", size=15, bold=True, color=POS))

    p.append(fitbox(lx + 20, ly + 50, 510, 65,
                    "Конфігурація DNS (/etc/resolv.conf у контейнері):\nКопіює хостовий resolv.conf (наприклад, nameserver 8.8.8.8 або 1.1.1.1).\nНемає вбудованого DNS-сервера Docker.",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.1))

    p.append(fitbox(lx + 20, ly + 130, 510, 130,
                    "Спроба з'єднання за іменем:\n1. Контейнер web (172.17.0.2) викликає getaddrinfo('db')\n2. Запит надсилається на 8.8.8.8 (зовнішній DNS)\n3. 8.8.8.8 нічого не знає про локальний контейнер 'db'\n4. Відповідь: NXDOMAIN (Name or service not known)\n5. Помилка: З'єднання неможливе без жорстких IP або застарілого --link.",
                    size=12, fill=RED_FILL, stroke=POS, sw=1.2))

    p.append(fitbox(lx + 20, ly + 280, 510, 110,
                    "Пастка 127.0.0.53 (systemd-resolved на хості):\nЯкщо на хості працює systemd-resolved, хостовий resolv.conf містить 127.0.0.53.\nDocker не копіює loopback-адресу, бо всередині netns це адреса самого контейнера,\nі підставляє Google DNS (8.8.8.8) — локальні DNS-імена хоста стають недоступними.",
                    size=12, fill=GREY_FILL, stroke=MUTED, sw=1.1))

    p.append(fitbox(lx + 20, ly + 410, 510, 120,
                    "Чому так зроблено:\nДефолтна мережа docker0 створена для зворотної сумісності.\nDocker свідомо не вмикає автоматичне виявлення сервісів\nу дефолтному мості, щоб запобігти витоку імен між непов'язаними контейнерами.",
                    size=12, fill=WARM_FILL, stroke=MUTED, sw=1.1))

    # Права половина: Custom Network (User-defined Bridge)
    rx, ry, rw, rh = 620, 60, 550, 550
    p.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 28, "Користувацька мережа: my-net (172.20.0.0/16)", size=15, bold=True, color=FIELD))

    p.append(fitbox(rx + 20, ry + 50, 510, 65,
                    "Конфігурація DNS (/etc/resolv.conf у контейнері):\nnameserver 127.0.0.11\noptions ndots:0",
                    size=12, fill=BLUE_FILL, stroke=NEG, sw=1.1))

    p.append(fitbox(rx + 20, ry + 130, 510, 130,
                    "Магія 127.0.0.11 та перехоплення iptables:\n1. Запит getaddrinfo('db') надсилається на 127.0.0.11:53 (UDP)\n2. Правило iptables (ланок OUTPUT/PREROUTING) у netns контейнера\n   перенаправляє пакет на випадковий внутрішній порт dockerd embedded DNS\n3. Embedded DNS резолвить 'db' -> 172.20.0.3 через внутрішній реєстр\n4. Зовнішні запити (api.github.com) пересилаються на upstream DNS хоста.",
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    p.append(fitbox(rx + 20, ry + 280, 510, 110,
                    "Мережевий міст br-xxxx та ізоляція:\nКожна створена мережа дістає окремий Linux Bridge.\nТаблиці iptables містять правила DOCKER-ISOLATION-STAGE-1/2,\nякі забороняють прямий маршрутизований трафік між різними мостами.",
                    size=12, fill=GREY_FILL, stroke=MUTED, sw=1.1))

    p.append(fitbox(rx + 20, ry + 410, 510, 120,
                    "Діагностика збоїв DNS у контейнерах:\n• Перевірка зсередини: dig @127.0.0.11 db або nslookup db\n• Перевірка iptables: iptables-save -t nat | grep 127.0.0.11\n• Перевірка блокування зв'язку: iptables -L FORWARD -n -v",
                    size=12, fill=BLUE_FILL, stroke=NEG, sw=1.1))

    return render(os.path.join(IMG, "container-dns-network-bridge.svg"), W, H, *p)


# ── 3. PID 1 zombie reaper and signal handling ──────────────────────────────
def fig_pid1_zombie_and_signal_lifecycle():
    W, H = 1240, 660
    p = []

    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))
    p.append(text(W / 2, 32, "Анатомія PID 1 у контейнері: Збирач зомбі та обробка сигналів", size=18, bold=True, color=INK))

    # Ліва половина: Проблема процесів-зомбі (Zombie Reaper)
    lx, ly, lw, lh = 30, 60, 570, 570
    p.append(rect(lx, ly, lw, lh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(lx + lw / 2, ly + 28, "Проблема 1: Витік процесів-зомбі (Zombie Reaper)", size=15, bold=True, color=POS))

    p.append(fitbox(lx + 20, ly + 50, 530, 80,
                    "Ієрархія та осиротіння (Double Fork):\nNode.js/Python (PID 1) породжує воркер (PID 10).\nВоркер робить fork() для фонової задачі (PID 25) і завершується.\nЗадача PID 25 стає сиротою. Ядро всиновлює її до PID 1.",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.1))

    p.append(fitbox(lx + 20, ly + 145, 530, 140,
                    "Чому звичайний застосунок ламає модель Unix:\n1. Задача PID 25 завершує роботу і викликає exit(0).\n2. Ядро звільняє пам'ять, але залишає struct task_struct (стан EXIT_ZOMBIE).\n3. Ядро надсилає сигнал SIGCHLD процесу PID 1.\n4. Node.js/Python/Java не мають глобального обробника waitpid(-1, &status, WNOHANG).\n5. Запис про PID 25 назавжди залишається в таблиці процесів ядра.",
                    size=12, fill=RED_FILL, stroke=POS, sw=1.2))

    p.append(fitbox(lx + 20, ly + 300, 530, 120,
                    "Наслідки витоку зомбі:\n• Вичерпання таблиці PID хоста (/proc/sys/kernel/pid_max).\n• Досягнення ліміту cgroups pids.max (cgroup v2).\n• Будь-який наступний виклик fork() повертає EAGAIN:\n  «fork: Resource temporarily unavailable» — контейнер паралізовано.",
                    size=12, fill=GREY_FILL, stroke=MUTED, sw=1.1))

    p.append(fitbox(lx + 20, ly + 435, 530, 115,
                    "Рішення: prctl(PR_SET_CHILD_SUBREAPER, 1) або tini:\nІніціалізатор PID 1 перехоплює всіх сиріт і в циклі\nwhile (waitpid(-1, NULL, WNOHANG) > 0) своєчасно\nвидаляє записи завершених задач.",
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    # Права половина: Обробка сигналів та 10-секундний SIGKILL
    rx, ry, rw, rh = 640, 60, 570, 570
    p.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 28, "Проблема 2: Ігнорування SIGTERM та зависання на 10 с", size=15, bold=True, color=POS))

    p.append(fitbox(rx + 20, ry + 50, 530, 80,
                    "Особливий захист ядра для PID 1:\nДля звичайних процесів дефолтна дія (SIG_DFL) для SIGTERM — завершення.\nАле для PID 1 ядро ігнорує сигнали з дією SIG_DFL,\nщоб захистити систему від випадкової загибелі init.",
                    size=12, fill=WARM_FILL, stroke=LINE, sw=1.1))

    p.append(fitbox(rx + 20, ry + 145, 530, 140,
                    "Хронологія зависання docker stop:\n1. Т = 0.0s: Docker надсилає SIGTERM до PID 1.\n2. Якщо застосунок не зареєстрував обробник sigaction(SIGTERM),\n   ядро відкидає сигнал без жодної дії.\n3. Т = 0..10s: Застосунок продовжує працювати, Docker чекає grace period.\n4. Т = 10.0s: Docker вичерпує таймаут і надсилає безжальний SIGKILL.\n5. Наслідок: Обрив HTTP-з'єднань, пошкодження файлів БД, втрата логів.",
                    size=12, fill=RED_FILL, stroke=POS, sw=1.2))

    p.append(fitbox(rx + 20, ry + 300, 530, 120,
                    "Пастка оболонки (Shell Form у Dockerfile):\nENTRYPOINT ./start.sh запускає /bin/sh як PID 1.\nОболонка sh не пересилає SIGTERM дочірньому процесу (PID 2).\nВиправлення:\n• Використовувати exec ./app у bash-скриптах\n• Використовувати JSON-форму: ENTRYPOINT [\"./app\"]",
                    size=12, fill=GREY_FILL, stroke=MUTED, sw=1.1))

    p.append(fitbox(rx + 20, ry + 435, 530, 115,
                    "Рішення: docker run --init (Tini):\nTini стає PID 1, миттєво пересилає SIGTERM дочірнім процесам,\nчекає їхнього коректного завершення (Graceful Shutdown),\nі запобігає 10-секундному зависанню.",
                    size=12, fill=GREEN_FILL, stroke=FIELD, sw=1.2))

    return render(os.path.join(IMG, "pid1-zombie-and-signal-lifecycle.svg"), W, H, *p)


if __name__ == "__main__":
    fig_uid_mapping_bind_mount()
    fig_container_dns_network_bridge()
    fig_pid1_zombie_and_signal_lifecycle()
    print("All figures generated successfully.")
