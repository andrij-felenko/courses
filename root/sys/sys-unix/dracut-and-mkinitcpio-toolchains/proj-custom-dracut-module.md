# ⚙️ Створення власного модуля dracut та хука mkinitcpio

Практичне розширення функціональності раннього простору користувача вимагає розуміння специфіки створення модулів для конкретного генератора, оскільки просте додавання бінарного файлу без правильної реєстрації залежностей та точок виклику залишить його недоступним під час завантаження.

Ця вставка демонструє розробку допоміжної утиліти перевірки безпеки мовами C та C++, розбір механізмів її динамічного трасування, а також її інтеграцію у вигляді власного модуля для `dracut` та відповідного хука для `mkinitcpio`.

---

## Завдання: Власна перевірка апаратного токена перед монтуванням кореня

Уявимо сценарій корпоративної безпеки: перед тим як розшифровувати кореневий LUKS-контейнер або монтувати кореневу файлову систему, система повинна перевірити наявність спеціального криптографічного маркера (файлу ключа) на підключеному USB-накопичувачі або монтованому носії. Якщо файл ключа з відповідною сигнатурою знайдено та верифіковано, перевірка завершується успішно, і процес завантаження продовжується. У разі відсутності ключа утиліта повертає помилку, зупиняючи завантаження до втручання оператора у режимі аварійної оболонки (*emergency shell*).

Для реалізації цієї задачі потрібні два компоненти:
1. Виконуваний бінарний файл `initramfs-keycheck`, який працюватиме всередині раннього простору користувача.
2. Конфігураційні скрипти для генератора (`dracut` або `mkinitcpio`), які скопіюють утиліту, знайдуть усі її динамічні залежності та зареєструють її виклик на потрібному етапі завантаження.

---

## 1. Написання допоміжної утиліти `initramfs-keycheck`

Утиліта приймає шлях до файла ключа, перевіряє його існування через системні виклики `stat`, відкриває файл, зчитує заголовні байти та зіставляє їх із очікуваною магічною послідовністю.

Програма також розпізнає відсутність CLI-аргументів і здатна самостійно прочитати параметри з `/proc/cmdline` для витягування ключа `keycheck.path=`.

:::tabs
```c
/* initramfs-keycheck.c — C реалізація для раннього простору користувача */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>

#define EXPECTED_MAGIC "SECUREKEY2026"
#define MAGIC_LEN 13
#define CMDLINE_PATH "/proc/cmdline"

static void log_msg(const char *level, const char *msg) {
    fprintf(stderr, "[keycheck:%s] %s\n", level, msg);
}

int check_token_file(const char *keypath) {
    struct stat st;

    if (stat(keypath, &st) != 0) {
        fprintf(stderr, "[keycheck:ERR] Cannot stat %s: %s\n", keypath, strerror(errno));
        return 2;
    }

    if (!S_ISREG(st.st_mode)) {
        log_msg("ERR", "Target path is not a regular file");
        return 3;
    }

    if (st.st_size < MAGIC_LEN) {
        log_msg("ERR", "Keyfile size is smaller than required header length");
        return 4;
    }

    int fd = open(keypath, O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "[keycheck:ERR] Open failed for %s: %s\n", keypath, strerror(errno));
        return 5;
    }

    char buffer[MAGIC_LEN + 1];
    ssize_t bytes_read = read(fd, buffer, MAGIC_LEN);
    close(fd);

    if (bytes_read != MAGIC_LEN) {
        log_msg("ERR", "Failed to read required header bytes from keyfile");
        return 6;
    }
    buffer[MAGIC_LEN] = '\0';

    if (memcmp(buffer, EXPECTED_MAGIC, MAGIC_LEN) != 0) {
        log_msg("FAIL", "Invalid magic token sequence inside keyfile!");
        return 7;
    }

    printf("[keycheck:OK] SUCCESS: Valid token verified at %s\n", keypath);
    return 0;
}

int main(int argc, char *argv[]) {
    const char *keypath = NULL;

    if (argc >= 2) {
        keypath = argv[1];
    } else {
        /* Якщо аргумент не передано, пробуємо зчитати keycheck.path з /proc/cmdline */
        int fd = open(CMDLINE_PATH, O_RDONLY);
        if (fd >= 0) {
            char cmdline[1024];
            ssize_t n = read(fd, cmdline, sizeof(cmdline) - 1);
            close(fd);
            if (n > 0) {
                cmdline[n] = '\0';
                char *token = strstr(cmdline, "keycheck.path=");
                if (token) {
                    token += 14;
                    char *end = strchr(token, ' ');
                    if (end) *end = '\0';
                    end = strchr(token, '\n');
                    if (end) *end = '\0';
                    keypath = token;
                }
            }
        }
    }

    if (!keypath || strlen(keypath) == 0) {
        log_msg("WARN", "No keypath specified via CLI or keycheck.path in cmdline");
        return 1;
    }

    return check_token_file(keypath);
}
```
```cpp
// initramfs-keycheck.cpp — Ідіоматична C++ реалізація (RAII, string_view, filesystem, expected)
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <filesystem>
#include <expected>
#include <system_error>

namespace fs = std::filesystem;

constexpr std::string_view EXPECTED_MAGIC = "SECUREKEY2026";
constexpr std::string_view CMDLINE_PATH = "/proc/cmdline";

enum class CheckError {
    MissingArgument,
    FileNotFound,
    NotARegularFile,
    FileTooSmall,
    OpenFailed,
    ReadFailed,
    InvalidMagic
};

std::string_view to_string(CheckError err) noexcept {
    switch (err) {
        case CheckError::MissingArgument: return "No keypath provided via CLI or cmdline";
        case CheckError::FileNotFound:    return "Keyfile path does not exist";
        case CheckError::NotARegularFile: return "Target path is not a regular file";
        case CheckError::FileTooSmall:    return "Keyfile size is smaller than expected header";
        case CheckError::OpenFailed:      return "Failed to open keyfile for reading";
        case CheckError::ReadFailed:      return "Failed to read header bytes";
        case CheckError::InvalidMagic:    return "Magic token mismatch in keyfile header";
    }
    return "Unknown error";
}

class FileHandle {
    int fd_ = -1;
public:
    explicit FileHandle(int fd) noexcept : fd_(fd) {}
    ~FileHandle() { if (fd_ >= 0) ::close(fd_); }
    FileHandle(const FileHandle&) = delete;
    FileHandle& operator=(const FileHandle&) = delete;
    FileHandle(FileHandle&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

std::expected<void, CheckError> verify_keyfile(const fs::path& keypath) {
    std::error_code ec;

    if (!fs::exists(keypath, ec) || ec) {
        return std::unexpected(CheckError::FileNotFound);
    }

    if (!fs::is_regular_file(keypath, ec) || ec) {
        return std::unexpected(CheckError::NotARegularFile);
    }

    if (fs::file_size(keypath, ec) < EXPECTED_MAGIC.size() || ec) {
        return std::unexpected(CheckError::FileTooSmall);
    }

    std::ifstream file(keypath, std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected(CheckError::OpenFailed);
    }

    std::string header(EXPECTED_MAGIC.size(), '\0');
    if (!file.read(header.data(), static_cast<std::streamsize>(header.size()))) {
        return std::unexpected(CheckError::ReadFailed);
    }

    if (header != EXPECTED_MAGIC) {
        return std::unexpected(CheckError::InvalidMagic);
    }

    return {};
}

std::string parse_cmdline_keypath() {
    std::ifstream cmdfile(std::string{CMDLINE_PATH});
    if (!cmdfile.is_open()) return "";

    std::string line;
    if (std::getline(cmdfile, line)) {
        constexpr std::string_view key_prefix = "keycheck.path=";
        auto pos = line.find(key_prefix);
        if (pos != std::string::npos) {
            auto start = pos + key_prefix.size();
            auto end = line.find_first_of(" \n\r", start);
            return line.substr(start, (end == std::string::npos) ? std::string::npos : (end - start));
        }
    }
    return "";
}

int main(int argc, char* argv[]) {
    std::string keypath_str;

    if (argc >= 2) {
        keypath_str = argv[1];
    } else {
        keypath_str = parse_cmdline_keypath();
    }

    if (keypath_str.empty()) {
        std::cerr << "[keycheck:ERR] " << to_string(CheckError::MissingArgument) << "\n";
        return 1;
    }

    const fs::path keypath{keypath_str};
    auto result = verify_keyfile(keypath);

    if (!result) {
        std::cerr << "[keycheck:FAIL] Error verifying " << keypath << ": "
                  << to_string(result.error()) << "\n";
        return static_cast<int>(result.error());
    }

    std::cout << "[keycheck:OK] SUCCESS: Valid token verified at " << keypath << "\n";
    return 0;
}
```
:::

Компіляція програми виконується звичайним компілятором C++ у середовищі розробки:
```bash
# Динамічна компіляція (генератор автоматично виявить залежності від libstdc++.so та libc.so)
g++ -O2 -std=c++23 initramfs-keycheck.cpp -o initramfs-keycheck
```

---

## 2. Реалізація модуля для dracut

У dracut кожен модуль проектується у вигляді окремої директорії всередині директорії `/usr/lib/dracut/modules.d/`. Префікс імені визначає порядок завантаження. Створимо модуль `95keycheck`.

Число `95` обрано свідомо: воно гарантує, що модуль виконуватиметься після базових модулів системного середовища (`00systemd`, `10i18n`), але до безпосередньої спроби монтування кореневої файлової системи у каталозі `95rootfs-block`.

### 2.1 Файл опису модуля: `/usr/lib/dracut/modules.d/95keycheck/module-setup.sh`

Конфігураційний файл `module-setup.sh` є головною точкою входу для dracut під час збирання образу. Він керує викликом предикатів перевірки та реєстрацією системних ресурсів.

```sh
#!/bin/bash
# module-setup.sh для модуля 95keycheck у dracut

# Перевірка, чи слід включати модуль у завантажувальний образ
check() {
    # Включати модуль лише якщо бинарник initramfs-keycheck присутній у системі
    type initramfs-keycheck >/dev/null 2>&1 || return 1
    return 0
}

# Визначення залежностей від інших модулів dracut
depends() {
    echo "udev-rules"
    return 0
}

# Встановлення файлів та скриптів виконання у cpio-архів
install() {
    # Скопіювати бінарний файл перевірки (dracut автоматично виконає ldd і копіює бібліотеки)
    inst_multiple initramfs-keycheck

    # Зареєструвати скрипт виконання у черзі initqueue перед монтуванням
    inst_hook initqueue/online 50 "$moddir/verify-key.sh"
}
```

### 2.2 Скрипт виконання в initramfs: `/usr/lib/dracut/modules.d/95keycheck/verify-key.sh`

Скрипт розширює чергу виконання `initqueue/online`. Він отримує керування щоразу, коли в системі з'являється новий мережевий або блоковий пристрій.

```sh
#!/bin/sh
# verify-key.sh — виконується в initramfs під час події initqueue

type getarg >/dev/null 2>&1 || . /lib/dracut-lib.sh

# Зчитати параметр з командного рядка ядра (наприклад, keycheck.path=/key.bin)
KEY_PATH=$(getarg keycheck.path=)

if [ -n "$KEY_PATH" ]; then
    echo "dracut: Starting token verification at $KEY_PATH..."
    if ! initramfs-keycheck "$KEY_PATH"; then
        echo "dracut: FATAL key verification failed! Halting boot."
        warn "Token validation failure: $KEY_PATH"
        emergency_shell
    fi
fi
```

Для виклику генерації нового образу в dracut виконують команду з перекриттям наявного архіву:
```bash
dracut --force --add keycheck /boot/initramfs-linux.img
```

---

## 3. Реалізація хука для mkinitcpio

У mkinitcpio архітектура модуля розділяється на два ізольованих файли: інсталяційний (що працює в середовищі хост-системи) та скрипт виконання (що потрапляє всередину cpio-архіву).

### 3.1 Інсталяційний скрипт: `/usr/lib/initcpio/install/keycheck`

Інсталяційний скрипт виконується інтерпретатором Bash при складанні cpio-архіву.

```bash
#!/bin/bash
# /usr/lib/initcpio/install/keycheck — інсталяційний файл mkinitcpio

build() {
    # Додати бінарник перевірки (mkinitcpio відстежить залежні .so бібліотеки через ldd)
    add_binary "initramfs-keycheck"

    # Додати скрипт виконання в рантайм раннього простору користувача
    add_runscript
}

help() {
    cat <<HELPEOF
Цей хук додає перевірку апаратного токена ключа перед монтуванням кореня.
Вимагає налаштування параметра keycheck.path= в cmdline ядра.
HELPEOF
}
```

### 3.2 Скрипт виконання в initramfs: `/usr/lib/initcpio/hooks/keycheck`

Скрипт рантайму виконується всередині початкового простору користувача під час виконання головного сценарію `/init`.

```bash
#!/bin/bash
# /usr/lib/initcpio/hooks/keycheck — виконавець хука в рантаймі mkinitcpio

run_hook() {
    # Зчитати параметр keycheck.path із командного рядка
    for arg in $CMDLINE; do
        case "$arg" in
            keycheck.path=*)
                KEY_PATH="${arg#*=}"
                ;;
        esac
    done

    if [ -n "$KEY_PATH" ]; then
        echo "mkinitcpio: Verifying key at $KEY_PATH..."
        if ! initramfs-keycheck "$KEY_PATH"; then
            echo "mkinitcpio: Key check failed! Falling back to rescue shell."
            launch_interactive_shell
        fi
    fi
}
```

Після створення файлів новий хук додають до списку `HOOKS` у файлі `/etc/mkinitcpio.conf`:
```bash
HOOKS=(base udev autodetect modconf block keycheck encrypt lvm2 filesystems fsck)
```

Та запускають перебудову завантажувального образу:
```bash
mkinitcpio -p linux
```

---

## 4. Механіка динамічного трасування бібліотек генераторами

Коли `dracut` (через функцію `inst_multiple`) або `mkinitcpio` (через функцію `add_binary`) додає бінарний файл `initramfs-keycheck` до обраного CPIO-структури, обидва генератори викликають внутрішній парсер залежностей.

Розглянемо, як цей процес відбувається на рівні системних викликів та утиліт:

```
[Початок: add_binary / inst_multiple "initramfs-keycheck"]
           │
           v
[Аналіз ELF-заголовків (readelf -d або ldd)]
           │
           ├──> Знайдено libstdc++.so.6  ──> Пошук у /usr/lib/ ──> Копіювати в cpio
           ├──> Знайдено libm.so.6       ──> Пошук у /lib64/   ──> Копіювати в cpio
           ├──> Знайдено libc.so.6       ──> Пошук у /lib64/   ──> Копіювати в cpio
           └──> Знайдено ld-linux-x86-64 ──> Пошук у /lib64/   ──> Копіювати в cpio
           │
           v
[Рекурсивна перевірка залежностей для кожної знайденої .so бібліотеки]
           │
           v
[Створення символьних посилань (symlinks) у директоріях /lib64/ та /usr/lib/]
```

Якщо утиліту зкомпільовано динамічно, генератор не лише скопіює саму утиліту у `/usr/bin/initramfs-keycheck`, але й відтворить у cpio-архіві повне дерево shared-бібліотек:
- `/lib64/ld-linux-x86-64.so.2` (динамічний завантажувач ELF).
- `/usr/lib/libstdc++.so.6` (стандартна бібліотека C++).
- `/usr/lib/libm.so.6` (математична бібліотека).
- `/usr/lib/libc.so.6` (стандартна бібліотека C).

Якщо хоча б одну з цих бібліотек не буде скопійовано (наприклад, через відсутність файлу у системному каталозі або помилку опису шляхів), виклик утиліти у ранньому просторі користувача завершиться помилкою `No such file or directory`, навіть якщо самий файл `initramfs-keycheck` фізично присутній у rootfs.

---

## 5. Діагностика та тестування у середовищі QEMU

Після генерації файлу initramfs важливо провести перевірку цілісності обраного архіву та випробувати його роботу у віртуальному середовищі.

### Інспекція вмісту CPIO-образу

Для перевірки образу dracut використовують утиліту `lsinitrd`, яка розпаковує шапку cpio на льоту:
```bash
lsinitrd /boot/initramfs-linux.img | grep -E 'keycheck|verify-key|libstdc++'
```

Для перевірки образу mkinitcpio або initramfs-tools використовують `bsdtar` або `cpio`:
```bash
bsdtar -tf /boot/initramfs-linux.img | grep -E 'keycheck|libstdc++'
```

Також можна повністю розпакувати cpio-архів у тимчасову директорію для ручного аналізу прав доступу та конфігурацій:
```bash
mkdir /tmp/initramfs-inspect && cd /tmp/initramfs-inspect
zstd -d -c /boot/initramfs-linux.img | cpio -idmv
ls -la usr/bin/initramfs-keycheck
```

### Запуск тестування у віртуальній машині QEMU

Запуск отриманого образу в емуляторі QEMU з передачею тестових параметрів командного рядка ядра дозволяє перевірити спрацьовування перевірки без ризику пошкодити робочу систему:

```bash
# Тест 1: Успішна перевірка (файл /key.bin створено у тимчасовому диску або вшито)
qemu-system-x86_64 \
  -kernel /boot/vmlinuz-linux \
  -initrd /boot/initramfs-linux.img \
  -append "console=ttyS0 keycheck.path=/key.bin rd.break=pre-mount" \
  -nographic

# Тест 2: Помилка перевірки (файл ключа відсутній) -> Перехід у emergency shell
qemu-system-x86_64 \
  -kernel /boot/vmlinuz-linux \
  -initrd /boot/initramfs-linux.img \
  -append "console=ttyS0 keycheck.path=/nonexistent.bin" \
  -nographic
```

У разі відсутності файлу `/nonexistent.bin` утиліта поверне код помилки, а скрипт виконання перехопить її та передасть керування аварійній оболонці `emergency_shell` (у dracut) або `launch_interactive_shell` (у mkinitcpio), підтверджуючи коректність побудованої системи захисту.
