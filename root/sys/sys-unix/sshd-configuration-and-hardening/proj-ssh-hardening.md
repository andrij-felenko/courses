# ⚙️ Скрипт аудиту та автоматичного загартування конфігурації sshd

Цей інструментальний розділ містить готовий скрипт для автоматизованого аудиту чинної конфігурації OpenSSH-сервера, генератор безпечного drop-in файлу налаштувань та правила пакетного фільтра `nftables` для захисту демона на рівні ядра Linux.

Аудит базується на аналізі нормалізованого виводу команди `sshd -T`, що дозволяє перевірити реальний стан параметрів з урахуванням усіх підключених конфігураційних файлів та значень за замовчуванням.

---

## 1. Механіка аудиту через нормалізований дамп `sshd -T`

Прямий синтаксичний розбір текстового файлу `/etc/ssh/sshd_config` сторонніми скриптами або парсерами часто призводить до помилкових висновків. Причини криються в складній семантиці OpenSSH:
* частина директив має значення за замовчуванням, які взагалі не записані у файлі явно;
* директива `Include` завантажує зовнішні файли за алфавітним порядком маски;
* більшість параметрів підпорядковується правилу «перемагає перше входження» (first match wins);
* блоки `Match` динамічно перевизначають параметри залежно від користувача чи IP-адреси.

Щоб отримати достовірну картину без інтерпретації сирого тексту, утиліта аудиту викликає сам бінарний файл `sshd` із прапорцем `-T`. У цьому режимі демон завантажує всі конфігураційні ланцюжки, розкриває макроси, застосовує дефолтні значення і друкує в `stdout` повний словник активних налаштувань. Усі ключі нормалізуються до нижнього регістру, а значення відображаються у канонічному форматі.

Нижче наведено повноцінний скрипт на мові Python, який аналізує вивід `sshd -T`, звіряє параметри з безпековим профілем і повертає відповідний код виходу для використання в конвеєрах CI/CD або системах моніторингу.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sshd-audit.py — утиліта аудиту конфігурації OpenSSH.
Зчитує нормалізований вивід 'sshd -T' та зіставляє параметри
із затвердженим базовим профілем загартування.
"""

import subprocess
import sys

# Очікувані безпечні параметри
SECURITY_BASELINE = {
    "passwordauthentication": {
        "expected": "no",
        "severity": "CRITICAL",
        "desc": "Парольна автентифікація дозволяє підбір паролів (brute-force)",
    },
    "kbdinteractiveauthentication": {
        "expected": "no",
        "severity": "HIGH",
        "desc": "Клавіатурно-інтерактивний вхід може пропускати паролі через PAM",
    },
    "permitemptypasswords": {
        "expected": "no",
        "severity": "CRITICAL",
        "desc": "Дозвіл входу без пароля",
    },
    "permitrootlogin": {
        "expected": ["no", "prohibit-password"],
        "severity": "CRITICAL",
        "desc": "Прямий вхід суперкористувача за паролем має бути заборонений",
    },
    "strictmodes": {
        "expected": "yes",
        "severity": "HIGH",
        "desc": "Перевірка прав доступу до ~/.ssh та authorized_keys",
    },
    "maxauthtries": {
        "expected": lambda v: int(v) <= 3,
        "expected_str": "<= 3",
        "severity": "MEDIUM",
        "desc": "Ліміт спроб автентифікації на з'єднання",
    },
    "logingracetime": {
        "expected": lambda v: int(v) <= 30,
        "expected_str": "<= 30s",
        "severity": "MEDIUM",
        "desc": "Таймаут неавтентифікованого з'єднання",
    },
    "x11forwarding": {
        "expected": "no",
        "severity": "LOW",
        "desc": "Прокидання X11 несе ризик перехоплення віконних подій",
    },
}

# Небезпечні криптографічні алгоритми, присутність яких неприпустима
WEAK_CRYPTO = {
    "ciphers": ["cbc", "3des", "arcfour", "cast128", "blowfish"],
    "kexalgorithms": ["diffie-hellman-group1-sha1", "diffie-hellman-group14-sha1", "group-exchange-sha1"],
    "macs": ["md5", "sha1", "96"],
}


def get_sshd_config():
    """Викликає 'sshd -T' та повертає словник параметрів."""
    try:
        res = subprocess.run(["sshd", "-T"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except FileNotFoundError:
        print("[!] Помилка: утиліту 'sshd' не знайдено в системі.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[!] Помилка виконання 'sshd -T': {e.stderr}", file=sys.stderr)
        sys.exit(1)

    cfg = {}
    for line in res.stdout.splitlines():
        line = line.strip()
        if not line or " " not in line:
            continue
        key, val = line.split(" ", 1)
        cfg[key.lower()] = val.strip()
    return cfg


def audit_config(cfg):
    """Звіряє налаштування з профілем безпеки."""
    issues = []

    # 1. Базові параметри
    for key, rule in SECURITY_BASELINE.items():
        val = cfg.get(key)
        if val is None:
            issues.append(("UNKNOWN", f"Параметр '{key}' відсутній у конфігурації", rule["severity"]))
            continue

        exp = rule["expected"]
        matched = False
        if callable(exp):
            try:
                matched = exp(val)
            except ValueError:
                matched = False
            exp_display = rule["expected_str"]
        elif isinstance(exp, list):
            matched = val in exp
            exp_display = " | ".join(exp)
        else:
            matched = val == exp
            exp_display = exp

        if not matched:
            issues.append((rule["severity"], f"{key}: поточне '{val}' != очікуване '{exp_display}' ({rule['desc']})"))

    # 2. Криптографічний аудит
    for category, forbidden_patterns in WEAK_CRYPTO.items():
        actual_val = cfg.get(category, "")
        elements = [x.strip() for x in actual_val.split(",") if x.strip()]
        for elem in elements:
            for bad in forbidden_patterns:
                if bad in elem.lower():
                    issues.append(("HIGH", f"Слабкий криптографічний алгоритм у '{category}': {elem}"))

    return issues


def main():
    print("=== Аудит конфігурації OpenSSH Daemon (sshd -T) ===")
    cfg = get_sshd_config()
    issues = audit_config(cfg)

    if not issues:
        print("[✓] Конфігурація sshd відповідає суворому профілю безпеки. Дефектів не виявлено.")
        sys.exit(0)

    print(f"[!] Знайдено зауважень: {len(issues)}\n")
    for sev, msg in issues:
        print(f"  [{sev:8s}] {msg}")

    print("\nРекомендація: додайте безпечний профіль у /etc/ssh/sshd_config.d/99-hardening.conf")
    sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## 2. Модульний підхід через drop-in файли конфігурації

Редагування основного файлу `/etc/ssh/sshd_config` вручну створює проблеми під час оновлення дистрибутива: пакети Debian (`dpkg`) або Red Hat (`rpm`) виявляють змінений конфіг і пропонують або зберегти старий файл, або перезаписати його новим шаблоном розробників (створюючи файли `.dpkg-dist` чи `.rpmnew`).

Сучасний стандарт системного адміністрування полягає у використанні drop-in каталогу `/etc/ssh/sshd_config.d/`. Якщо головний файл починається рядком `Include /etc/ssh/sshd_config.d/*.conf`, будь-який створений у цьому каталозі файл завантажується першим. Оскільки `sshd` фіксує значення параметра при першому читанні, файл `99-hardening.conf` надійно перекриває системні налаштування за замовчуванням без жодного втручання в пакетний конфігураційний файл.

```text
# /etc/ssh/sshd_config.d/99-hardening.conf
# Суворий профіль безпеки системного демона OpenSSH

# 1. Мережеві обмеження та сокети
Port 22
Protocol 2
AddressFamily inet
LoginGraceTime 30
MaxAuthTries 3
MaxSessions 2
MaxStartups 10:30:60

# 2. Автентифікація та доступ
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitEmptyPasswords no
PermitRootLogin prohibit-password
StrictModes yes
IgnoreRhosts yes

# 3. Обмеження середовища та тунелів
X11Forwarding no
AllowTcpForwarding no
AllowAgentForwarding no
PermitUserEnvironment no
DisableForwarding yes

# 4. L7 Keepalive та контроль сесії
ClientAliveInterval 300
ClientAliveCountMax 2

# 5. Сучасний криптографічний набір
KexAlgorithms sntrup761x25519-sha512@openssh.com,curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,umac-128-etm@openssh.com
HostKeyAlgorithms ssh-ed25519,rsa-sha2-512,rsa-sha2-256
```

### Запобігання блокуванню адміністратора при переконфігурації
Помилка в синтаксисі або некоректно виставлені права на `authorized_keys` можуть призвести до повної втрати віддаленого доступу до сервера. Щоб гарантувати безперервність керування, застосовується суворий протокол оновлення конфігурації:

1. **Синтаксичний тест:** команда `sshd -t` парсить усі включені файли. Якщо знайдено невідому директиву або помилку в аргументах, утиліта друкує номер рядка й повертає ненульовий код помилки. Перезавантажувати службу в разі помилки суворо заборонено.
2. **Паралельна тестова сесія:** перед надсиланням сигналу перезавантаження адміністратор відкриває додаткову сесію термінала і залишає її активною.
3. **Безпечний релоад:** команда `systemctl reload sshd` надсилає демону сигнал `SIGHUP`. Головний слухач перечитує файли для наступних вхідних з'єднань, але всі активні сесії, PTY та процеси користувачів залишаються недоторканими.
4. **Тест нового підключення:** у новому вікні виконується тестовий вхід за ключем: `ssh -v -i ~/.ssh/id_ed25519 user@server`. Лише після успішного входу попередню сесію можна закривати.

---

## 3. Захист на рівні ядра через динамічні набори `nftables`

Традиційні утиліти динамічного блокування, такі як `fail2ban` або `sshguard`, працюють у просторі користувача. Вони вичитують текстові повідомлення з системного журналу (`/var/log/auth.log` або сокета `systemd-journald`), знаходять регулярними виразами рядки невдалих спроб і викликають утиліти фаєрвола для додавання IP-адреси порушника.

Між моментом здійснення спроби входу та реакцією утиліти проходить від 1 до 5 секунд затримки. За цей час автоматизований ботнет у багатопотоковому режимі встигає відкрити сотні нових TCP-з'єднань, змушуючи ядро та `sshd` витрачати пам'ять і процесорний час на створення дочірніх процесів через `fork()`.

Підсистема `nftables` ядра Linux дозволяє реалізувати захист із нульовою затримкою без участі простору користувача. Завдяки механізму dynamic sets та вбудованим лічильникам станів (meters), ядро самостійно відстежує частоту створення нових з'єднань (`ct state new`) для кожної IP-адреси. Якщо ліміт перевищено, IP-адреса автоматично додається у внутрішній набір заблокованих адрес із заданим таймаутом життя.

```text
#!/usr/sbin/nft -f

table inet ssh_guard {
    # Динамічний набір заблокованих IP-адрес із таймаутом
    set ssh_denylist {
        type ipv4_addr
        size 65535
        flags timeout
    }

    # Лічильник з'єднань з однієї адреси
    set ssh_meter {
        type ipv4_addr
        size 65535
        flags dynamic, timeout
        timeout 60s
    }

    chain input {
        type filter hook input priority filter; policy accept;

        # Відкидати пакети від уже заблокованих джерел
        ip saddr @ssh_denylist drop

        # Дозволити встановлені та споріднені з'єднання
        ct state established,related accept

        # Обробка нових TCP-з'єднань до порту SSH
        tcp dport 22 ct state new {
            # Якщо за 60s надійшло > 4 з'єднань — додати адресу в denylist на 10 хвилин
            update @ssh_meter { ip saddr limit rate over 4/minute } add @ssh_denylist { ip saddr timeout 10m } log prefix "[SSH_BRUTEFORCE_DROP]: " drop
            
            # Дозволити легітимні підключення в межах ліміту
            accept
        }
    }
}
```

Для застосування правил створений файл підключається командою `nft -f /etc/nftables/ssh-guard.nft` або включається до основного файлу `/etc/nftables.conf`. 

Переваги такого підходу:
* пакет відкидається на рівні мережевого драйвера ядра без створення дескриптора сокета;
* пам'ять під динамічний набір виділяється ядром фіксованими блоками;
* заблоковані адреси автоматично видаляються з пам'яті ядра після завершення 10-хвилинного інтервалу без необхідності запуску фонових cron-задач чи демонів.

---

## 4. Інтеграція перевірок у конвеєр автоматизації CI/CD

В інфраструктурі, керованій через Ansible, Terraform або хмарні образи cloud-init, загартування OpenSSH має бути валідованим етапом збирання системи. Будь-яка зміна в шаблонах конфігурації автоматично перевіряється набором тестів перед розгортанням у робоче середовище.

Типовий крок тестування в пайплайні перевіряє не лише загальний стан, а й поведінку блоків `Match` для різних контекстів підключення. Для цього прапорець `-C` емулює вхідні параметри:

```bash
# Тест глобальної конфігурації для звичайного користувача
sshd -T -C "user=alice,host=internal.corp,addr=10.0.1.15" | grep "passwordauthentication no"

# Тест умовного блоку для зовнішнього підключення
sshd -T -C "user=bob,host=external.net,addr=203.0.113.50" | grep "maxauthtries 3"

# Тест конфігурації ізольованої SFTP-групи
sshd -T -C "user=ftpuser,group=sftponly,host=srv.local,addr=192.168.1.5" | grep "chrootdirectory"
```

Якщо будь-яка з перевірок повертає неочікуване значення, збирання образу переривається з ненульовим кодом повернення. Це виключає ситуацію, коли через випадковий рядок у drop-in конфігурації на публічних серверах відновлюється парольний доступ або вмикається вразливий шифр.
