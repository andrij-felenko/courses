# ⚙️ Створення герметичного переносного бандла для Linux

Цей практичний проект демонструє проектування та створення повністю автономного, переносного двійкового пакета (герметичного бандла) для операційної системи Linux. Мета проекту — перетворити довільну динамічно скомпільовану програму на самодостатній каталог, здатний стабільно запускатися на будь-якому дистрибутиві Linux без прав суперкористувача, без встановлення додаткових системних пакетів та без використання зовнішніх контейнерних рушіїв.

Розробка системних сервісів, клієнтських агентів моніторингу та командних утиліт у середовищі Linux повсякчас стикається з фундаментальною проблемою гетерогенності цільової інфраструктури. Навіть у межах єдиної апаратної архітектури x86-64 сервери замовників можуть працювати під керуванням застарілого CentOS 7, консервативного Debian 11, новітнього Ubuntu 24.04 або легковагого Alpine Linux. Пряме копіювання динамічно скомпільованого двійкового файлу між цими дистрибутивами призводить до миттєвих збоїв ще на етапі запуску через несумісність версійних символів системної бібліотеки glibc або відсутність потрібних файлів `.so` у каталогах пошуку. Створення герметичного бандла усуває цю проблему за рахунок повної локалізації всіх залежностей усередині структури каталогу застосунку.

---

## 1. Постановка задачі та інженерні виклики

Перед системним інженером стоїть завдання: забезпечити надійне розгортання складної мережевої служби `telemetry-agent`, скомпільованої на сучасній робочій станції, на будь-які цільові хости Linux із ядром версії 3.10 і новішим. Служба використовує багатопотоковість, виконує мережевий обмін через OpenSSL, зчитує системні метрики та парсить конфігураційні файли.

Традиційні підходи до розгортання мають низку критичних недоліків:

1. **Повне статичне зв'язування з glibc (`gcc -static`):**
   Хоча статична збірка генерує єдиний двійковий файл, реалізація glibc не є повністю статичною за своєю природою. Функції розпізнавання облікових записів (`getpwnam`) та доменних імен (`getaddrinfo`) використовують модульну архітектуру Name Service Switch (NSS), яка під час виконання через системний виклик `dlopen()` завантажує плагіни `/lib/x86_64-linux-gnu/libnss_files.so.2` та `/lib/x86_64-linux-gnu/libnss_dns.so.2`. Якщо цільова система має іншу версію glibc або побудована на базі musl, мережеві виклики падають з аварією або зазнають фатального збою сегментації. Крім того, статичний бінарник glibc позбавлений можливості завантажувати сторонні драйвери GPU через `dlopen()`.
2. **Статичне зв'язування з musl libc:**
   Збирання з musl створює дійсно автономний бінарник, проте це вимагає повної перекомпіляції всієї кодової бази та всіх сторонніх C/C++ залежностей (OpenSSL, Boost, gRPC) з використанням інструментарію musl. Для великих комерційних проектів або закритих пропрієтарних бібліотек вендорів такий варіант часто є технологічно неможливим.
3. **Контейнеризація (Docker, Podman, OCI):**
   Контейнери ізолюють файлову систему, але вимагають наявності встановленого демона контейнеризації, відповідних прав доступу користувача (або складного налаштування rootless-режиму) та створюють значні накладні витрати пам'яті для простих консольних утиліт.

Інженерне рішення полягає у формуванні **герметичного переносного бандла** (Hermetic Portable Bundle). Це повністю самодостатній каталог, який містить виконуваний файл програми, усі необхідні їй спільні бібліотеки `.so`, налаштовані відносні шляхи пошуку на основі токена `$ORIGIN` та захисний скрипт запуску, який контролює змінні середовища та параметри локалі.

```
Структура герметичного бандла:
telemetry-bundle/
├── app.sh                  ◄── Скрипт-обгортка (санітизація оточення та захист від збоїв)
├── bin/
│   └── telemetry-agent     ◄── Двійковий файл ELF із RUNPATH = $ORIGIN/../lib
└── lib/                    ◄── Каталог ізольованих спільних бібліотек
    ├── ld-linux-x86-64.so.2◄── Приватний завантажувач (для повної glibc-ізоляції)
    ├── libc.so.6
    ├── libcrypto.so.3
    ├── libm.so.6
    ├── libssl.so.3
    ├── libnss_dns.so.2     ◄── Системний плагін NSS для мережевого резолвінгу
    └── libnss_files.so.2   ◄── Системний плагін NSS для локальних файлів /etc/hosts
```

---

## 2. Архітектурний механізм створення бандла

Формування герметичного пакета базується на чотирьох послідовних інженерних етапах:

### Етап 1: Рекурсивне розв'язання дерева залежностей

Утиліта зчитує всі прямі залежності `DT_NEEDED` із головного двійкового файлу, після чого рекурсивно досліджує динамічні секції кожної знайденої бібліотеки. Це формує повний орієнтований граф залежностей. Якщо головний бінарник залежить від бібліотеки `libssl.so.3`, а та, у свою чергу, залежить від `libcrypto.so.3` та `libc.so.6`, генератор виявляє повний транзитивний ланцюг об'єктів. Рекурсивний обхід виконується з відстеженням уже оброблених вузлів, що запобігає зацикленню у випадках перехресних залежностей.

### Етап 2: Фільтрація системної межі (System Boundary Filtering)

Критично важливо розділяти залежності на дві категорії: прикладні бібліотеки та бібліотеки системно-апаратної межі хоста. До першої категорії належать алгоритмічні бібліотеки, криптографічні рушії та сервісні модулі (`libssl`, `libcrypto`, `libz`, `libprotobuf`), які повністю інкапсульовані в просторі користувача. Їх необхідно обов'язково копіювати в бандл.

До другої категорії належать бібліотеки прямої взаємодії з ядром та графічними адаптерами хоста:
* `linux-vdso.so.1` — віртуальна спільна бібліотека ядра, яка існує лише в оперативній пам'яті кожного процесу і не має фізичного файлу на диску;
* `libGL.so.1`, `libEGL.so.1`, `libvulkan.so.1` — диспетчери графічних API, які перенаправляють виклики на драйвери хоста;
* `libcuda.so.1`, `libnvidia-ml.so.1` — бібліотеки прискорювачів NVIDIA, які вимагають суворої бінарної відповідності версії драйвера ядра `nvidia.ko`;
* `libasound.so.2` — бібліотека аудіопідсистеми ALSA, яка безпосередньо взаємодіє з дескрипторами звукових пристроїв `/dev/snd/*`;
* `libX11.so.6`, `libwayland-client.so.0` — клієнтські протоколи віконних серверів.

Спроба скопіювати апаратні бібліотеки (наприклад, `libcuda.so`) всередину бандла призводить до фатальних збоїв через несумісність структур даних системних викликів `ioctl()` між версією бібліотеки в бандлі та версією завантаженого модуля ядра хоста. Генератор застосовує строгий список виключень `SYSTEM_EXCLUDE` для збереження прозорої взаємодії з апаратним забезпеченням хоста.

### Етап 3: Патчинг заголовків ELF та відносні шляхи `$ORIGIN`

За замовчуванням скомпільований двійковий файл шукає спільні бібліотеки за жорстко зашитими абсолютними шляхами робочої станції або у стандартних системних каталогах `/lib` та `/usr/lib`. За допомогою утиліти `patchelf` динамічна секція бінарника модифікується:
* У бінарнику записується тег `DT_RUNPATH = '$ORIGIN/../lib:$ORIGIN'`.
* У кожній скопійованій бібліотеці всередині каталогу `lib/` записується тег `DT_RUNPATH = '$ORIGIN'`.

Під час запуску програми динамічний завантажувач ядра автоматично розгортає спеціальний токен `$ORIGIN` у реальний абсолютний шлях до каталогу, в якому розташовано файл. Якщо програма встановлена в `/opt/telemetry/bin/telemetry-agent`, рядок `$ORIGIN/../lib` однозначно вказує на `/opt/telemetry/lib`. Це гарантує повну релокабельність: каталог бандла можна перемістити в будь-яке місце файлової системи (наприклад, у домашній каталог користувача `/home/user/bundle` або тимчасову теку `/tmp/bundle`), і завантажувач безпомилково знайде власні бібліотеки.

### Етап 4: Прямий запуск через приватний інтерпретатор

Якщо цільовий хост має застарілу версію glibc (наприклад, glibc 2.17 на CentOS 7), на якій скомпільована програма з залежністю від glibc 2.34 взагалі не здатна запуститися через системний `/lib64/ld-linux-x86-64.so.2`, бандл застосовує стратегію **прямого виклику інтерпретатора** (*Direct Loader Invocation*).

Замість того, щоб покладатися на сегмент `PT_INTERP` бінарника, лаунчер викликає скомпільований динамічний завантажувач із каталогу бандла як звичайний виконуваний файл, передаючи йому цільову програму та список бібліотек аргументами:

```sh
exec "$SELF_DIR/lib/ld-linux-x86-64.so.2" --library-path "$SELF_DIR/lib" "$SELF_DIR/bin/telemetry-agent" "$@"
```

Цей механізм повністю ізолює процес: ядро завантажує приватний `ld-linux.so`, який використовує приватну `libc.so.6` версії 2.38 із каталогу бандла, взаємодіючи з ядром хоста виключно через стандартні системні виклики. Оскільки бінарний інтерфейс системних викликів ядра Linux гарантує абсолютну зворотну сумісність на десятиліття, програма стабільно працює на будь-якому дистрибутиві.

### Етап 5: Санітизація оточення у лаунчері (`app.sh`)

Стартовий скрипт `app.sh` виступає захисним шлюзом між оточенням хоста та ізольованим двійковим процесом:
1. **Фіксація локалі:** примусово встановлює змінні `LC_ALL=C.UTF-8` та `LANG=C.UTF-8`. Це запобігає збоям парсингу UTF-8 рядків на мінімальних серверах без локальних мовних пакетів та гарантує використання крапки як десяткового роздільника при обробці числових даних.
2. **Захист від затінення `LD_LIBRARY_PATH`:** видаляє або очищає користувацьку змінну `LD_LIBRARY_PATH`, блокуючи випадкове підвантаження несумісних системних бібліотек.
3. **Безшовна трансляція аргументів:** виконує бінарник через системний виклик оболонки `exec`, що заміщує процес оболонки цільовим процесом зі збереженням ідентифікатора PID, коректною обробкою сигналів `SIGTERM`/`SIGINT` та передачею вихідного коду повернення.

---

## 3. Програмна реалізація генератора бандлів

Нижче наведено повний вихідний код інструментарію. Перший модуль на мові Python автоматизує сканування залежностей, фільтрацію апаратних бібліотек, копіювання файлів та модифікацію заголовків ELF. Другий модуль містить низькорівневу утиліту перевірки заголовків ELF мовами C та C++.

### 3.1. Генератор переносного пакета на Python

Скрипт `bundle_maker.py` реалізує конвеєр автоматизованої підготовки автономного каталогу:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bundle_maker.py: Автоматизований збирач герметичних переносних бандлів для Linux."""

import os
import sys
import shutil
import subprocess
import re

# Бібліотеки, які не слід бандлити (мають надаватися хостом/драйверами)
SYSTEM_EXCLUDE = {
    "linux-vdso.so.1",
    "libGL.so.1",
    "libEGL.so.1",
    "libcuda.so.1",
    "libnvidia-ml.so.1",
    "libvulkan.so.1",
    "libX11.so.6",
    "libasound.so.2",
    "libdrm.so.2",
    "libwayland-client.so.0"
}

def resolve_dependencies(binary_path):
    """Рекурсивно збирає всі залежності .so за допомогою ldd."""
    deps = {}
    ldd_output = subprocess.check_output(["ldd", binary_path], universal_newlines=True)
    
    for line in ldd_output.splitlines():
        line = line.strip()
        if not line:
            continue
        
        # Формат: libname.so => /path/to/libname.so (0x...)
        match = re.match(r"^(.*?)\s*=>\s*(.*?)\s*\(0x[0-9a-fA-F]+\)$", line)
        if match:
            soname, target_path = match.group(1).strip(), match.group(2).strip()
            if target_path and target_path != "not found" and soname not in SYSTEM_EXCLUDE:
                deps[soname] = target_path
        else:
            # Формат: /lib64/ld-linux-x86-64.so.2 (0x...)
            match_interp = re.match(r"^(/.*?)\s*\(0x[0-9a-fA-F]+\)$", line)
            if match_interp:
                interp_path = match_interp.group(1).strip()
                soname = os.path.basename(interp_path)
                if soname not in SYSTEM_EXCLUDE:
                    deps[soname] = interp_path
                    
    return deps

def create_bundle(binary_path, output_dir):
    """Створює структуру бандла, копіює файли та налаштовує DT_RUNPATH."""
    abs_binary = os.path.abspath(binary_path)
    binary_name = os.path.basename(abs_binary)
    
    bin_dir = os.path.join(output_dir, "bin")
    lib_dir = os.path.join(output_dir, "lib")
    
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(lib_dir, exist_ok=True)
    
    print(f"[*] Аналіз залежностей для {abs_binary}...")
    deps = resolve_dependencies(abs_binary)
    
    # 1. Копіювання головного бінарника
    dest_binary = os.path.join(bin_dir, binary_name)
    shutil.copy2(abs_binary, dest_binary)
    os.chmod(dest_binary, 0o755)
    print(f"[+] Скопійовано бінарник -> {dest_binary}")
    
    # 2. Копіювання бібліотек
    for soname, src_path in deps.items():
        if os.path.isfile(src_path):
            dest_lib = os.path.join(lib_dir, soname)
            # Якщо це symlink — копіюємо реальний файл та розгортаємо посилання
            real_src = os.path.realpath(src_path)
            shutil.copy2(real_src, dest_lib)
            os.chmod(dest_lib, 0o755)
            print(f"  -> Бібліотека {soname} ({src_path})")
            
    # 3. Модифікація DT_RUNPATH для бінарника та бібліотек
    print("[*] Модифікація заголовків DT_RUNPATH ($ORIGIN/../lib)...")
    subprocess.run(["patchelf", "--set-rpath", "$ORIGIN/../lib:$ORIGIN", dest_binary], check=True)
    
    for lib_file in os.listdir(lib_dir):
        lib_full_path = os.path.join(lib_dir, lib_file)
        if os.path.isfile(lib_full_path):
            try:
                subprocess.run(["patchelf", "--set-rpath", "$ORIGIN", lib_full_path], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                pass
                
    # 4. Генерація стартового скрипта app.sh
    launcher_path = os.path.join(output_dir, "app.sh")
    launcher_content = f"""#!/usr/bin/env sh
# Автогенерований герметичний лаунчер для {binary_name}
set -e

# Визначення абсолютного каталогу бандла
SELF_DIR="\$(cd "\$(dirname "\$0")" && pwd)"

# Санітизація оточення
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Запуск бінарника з передачею всіх аргументів
exec "\$SELF_DIR/bin/{binary_name}" "\$@"
"""
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(launcher_content)
    os.chmod(launcher_path, 0o755)
    print(f"[+] Лаунчер згенеровано -> {launcher_path}")
    print("[✓] Герметичний бандл успішно створено!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Використання: {sys.argv[0]} <шлях_до_бінарника> <вихідний_каталог>")
        sys.exit(1)
    create_bundle(sys.argv[1], sys.argv[2])
```

---

### 3.2. Низькорівневий інспектор заголовків ELF (C та C++)

Утиліта `elf_inspector` призначена для швидкої валідації зібраного двійкового файлу. Вона відображає файл у пам'ять за допомогою системного виклику `mmap()`, знаходить секцію `SHT_DYNAMIC` та сканує всі динамічні теги, перевіряючи наявність правильного шляху `DT_RUNPATH` і відсутність небезпечного застарілого `DT_RPATH`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/stat.h>
#include <sys/mman.h>

/* Інспекція заголовків ELF та динамічних тегів RUNPATH / RPATH */
int inspect_elf(const char *filepath) {
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття файлу");
        return -1;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("Помилка fstat");
        close(fd);
        return -1;
    }

    uint8_t *map = (uint8_t *)mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map == MAP_FAILED) {
        perror("Помилка mmap");
        close(fd);
        return -1;
    }

    Elf64_Ehdr *ehdr = (Elf64_Ehdr *)map;
    if (memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "Файл не є валідним ELF\n");
        munmap(map, st.st_size);
        close(fd);
        return -1;
    }

    Elf64_Shdr *sections = (Elf64_Shdr *)(map + ehdr->e_shoff);
    Elf64_Shdr *dyn_shdr = NULL;
    Elf64_Shdr *str_shdr = NULL;

    for (int i = 0; i < ehdr->e_shnum; i++) {
        if (sections[i].sh_type == SHT_DYNAMIC) {
            dyn_shdr = &sections[i];
        }
    }

    if (!dyn_shdr) {
        printf("Бінарник є статичним або не має секції .dynamic\n");
        munmap(map, st.st_size);
        close(fd);
        return 0;
    }

    str_shdr = &sections[dyn_shdr->sh_link];
    const char *dynstr = (const char *)(map + str_shdr->sh_offset);
    Elf64_Dyn *dyn_entries = (Elf64_Dyn *)(map + dyn_shdr->sh_offset);
    size_t count = dyn_shdr->sh_size / sizeof(Elf64_Dyn);

    int has_rpath = 0, has_runpath = 0;
    for (size_t i = 0; i < count; i++) {
        if (dyn_entries[i].d_tag == DT_RPATH) {
            has_rpath = 1;
            printf("[!] Знайдено DT_RPATH: %s\n", dynstr + dyn_entries[i].d_un.d_val);
        } else if (dyn_entries[i].d_tag == DT_RUNPATH) {
            has_runpath = 1;
            printf("[✓] Знайдено DT_RUNPATH: %s\n", dynstr + dyn_entries[i].d_un.d_val);
        }
    }

    if (!has_runpath && !has_rpath) {
        printf("[-] У бінарнику немає записів RPATH або RUNPATH\n");
    }

    munmap(map, st.st_size);
    close(fd);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <elf_binary>\n", argv[0]);
        return 1;
    }
    return inspect_elf(argv[1]) == 0 ? 0 : 1;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/stat.h>
#include <sys/mman.h>

// RAII обгортка для безпечного відображення файлу через mmap
class MappedFile {
public:
    static std::expected<MappedFile, std::string> open_file(std::string_view path) {
        int fd = ::open(path.data(), O_RDONLY);
        if (fd < 0) {
            return std::unexpected("Не вдалося відкрити файл: " + std::string(path));
        }

        struct stat st{};
        if (::fstat(fd, &st) < 0) {
            ::close(fd);
            return std::unexpected("Помилка fstat для файлу: " + std::string(path));
        }

        void *ptr = ::mmap(nullptr, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
        ::close(fd);

        if (ptr == MAP_FAILED) {
            return std::unexpected("Помилка відображення пам'яті mmap");
        }

        return MappedFile(ptr, st.st_size);
    }

    ~MappedFile() {
        if (data_ != nullptr && size_ > 0) {
            ::munmap(data_, size_);
        }
    }

    MappedFile(const MappedFile &) = delete;
    MappedFile &operator=(const MappedFile &) = delete;

    MappedFile(MappedFile &&other) noexcept : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    [[nodiscard]] std::span<const uint8_t> bytes() const {
        return {static_cast<const uint8_t *>(data_), size_};
    }

private:
    MappedFile(void *data, size_t size) : data_(data), size_(size) {}
    void *data_{nullptr};
    size_t size_{0};
};

// Інспекція структури динамічної секції ELF
std::expected<void, std::string> inspect_elf(std::string_view filepath) {
    auto file_res = MappedFile::open_file(filepath);
    if (!file_res) {
        return std::unexpected(file_res.error());
    }

    auto span = file_res->bytes();
    if (span.size() < sizeof(Elf64_Ehdr)) {
        return std::unexpected("Розмір файлу замалий для заголовка ELF");
    }

    const auto *ehdr = reinterpret_cast<const Elf64_Ehdr *>(span.data());
    if (std::string_view(reinterpret_cast<const char *>(ehdr->e_ident), SELFMAG) != ELFMAG) {
        return std::unexpected("Файл не містить валідного підпису ELF");
    }

    if (ehdr->e_shoff + ehdr->e_shnum * sizeof(Elf64_Shdr) > span.size()) {
        return std::unexpected("Пошкоджена таблиця секцій ELF");
    }

    const auto *sections = reinterpret_cast<const Elf64_Shdr *>(span.data() + ehdr->e_shoff);
    const Elf64_Shdr *dyn_shdr = nullptr;

    for (int i = 0; i < ehdr->e_shnum; ++i) {
        if (sections[i].sh_type == SHT_DYNAMIC) {
            dyn_shdr = &sections[i];
            break;
        }
    }

    if (!dyn_shdr) {
        std::cout << "Бінарник є статичним або не містить секції .dynamic\n";
        return {};
    }

    const auto &str_shdr = sections[dyn_shdr->sh_link];
    const char *dynstr = reinterpret_cast<const char *>(span.data() + str_shdr.sh_offset);
    const auto *dyn_entries = reinterpret_cast<const Elf64_Dyn *>(span.data() + dyn_shdr->sh_offset);
    size_t count = dyn_shdr->sh_size / sizeof(Elf64_Dyn);

    bool has_rpath = false;
    bool has_runpath = false;

    for (size_t i = 0; i < count; ++i) {
        if (dyn_entries[i].d_tag == DT_RPATH) {
            has_rpath = true;
            std::cout << "[!] Знайдено DT_RPATH: " << (dynstr + dyn_entries[i].d_un.d_val) << "\n";
        } else if (dyn_entries[i].d_tag == DT_RUNPATH) {
            has_runpath = true;
            std::cout << "[✓] Знайдено DT_RUNPATH: " << (dynstr + dyn_entries[i].d_un.d_val) << "\n";
        }
    }

    if (!has_runpath && !has_rpath) {
        std::cout << "[-] У бінарнику відсутні записи RPATH / RUNPATH\n";
    }

    return {};
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <elf_binary>\n";
        return 1;
    }

    auto res = inspect_elf(argv[1]);
    if (!res) {
        std::cerr << "Помилка: " << res.error() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 4. Пастки та крайові випадки при створенні бандлів

Під час проектування переносних пакетів слід враховувати такі специфічні інженерні пастки:

### 4.1. Пастка плагінів Name Service Switch (NSS)

Функції системного розпізнавання імен користувачів `getpwnam()` та мережевих доменів `getaddrinfo()` у бібліотеці glibc не містять монолітної логіки всередині `libc.so.6`. Замість цього вони динамічно викликають внутрішню функцію `dlopen()` для підвантаження зовнішніх системних плагінів:
* `/lib/x86_64-linux-gnu/libnss_files.so.2` — для читання локального конфігураційного файлу `/etc/hosts` та бази користувачів `/etc/passwd`;
* `/lib/x86_64-linux-gnu/libnss_dns.so.2` — для виконання віддалених DNS-запитів через системний резолвер;
* `/lib/x86_64-linux-gnu/libresolv.so.2` — допоміжна бібліотека роботи з протоколом DNS.

Оскільки цих плагінів немає у списку `DT_NEEDED` двійкового файлу, стандартне сканування залежностей через `ldd` їх не виявляє. Якщо на цільовому сервері встановлено несумісну версію glibc або базовий дистрибутив Alpine Linux без glibc, будь-яка спроба виконати мережевий запит призведе до краху процесу через неможливість завантажити бібліотеку NSS потрібної версії.

*Інженерне рішення:* генератор бандла повинен примусово копіювати файли `libnss_files.so.2`, `libnss_dns.so.2` та `libresolv.so.2` у каталог `lib/` бандла при підготовці мережевих застосунків.

### 4.2. Ланцюжки символьних посилань (.so Symlinks)

У сучасних дистрибутивах Linux спільні бібліотеки організовані у вигляді каскадних символьних посилань:
`libssl.so -> libssl.so.3 -> libssl.so.3.0.0`

Якщо утиліта збирання пакета скопіює лише верхнє символьне посилання без реального фізичного файлу, на цільовій машині таке посилання перетвориться на «висяче» (dangling symlink), оскільки воно вказуватиме на неіснуючий системний шлях хоста. При спробі старту динамічний завантажувач негайно видасть помилку `cannot open shared object file: No such file or directory`.

*Інженерне рішення:* алгоритм копіювання зобов'язаний розгортати кожне посилання до реального фізичного файлу за допомогою функції `os.path.realpath()`, зберігаючи повноцінні копії бінарних об'єктів у каталозі `lib/`.

### 4.3. Блокування `$ORIGIN` у привілейованих програмах

Якщо двійковий файл має встановлений біт підвищення привілеїв `setuid` чи `setgid` (або розширені файлові права Linux *capabilities* на кшталт `CAP_NET_RAW`), ядро встановлює прапорець `AT_SECURE = 1` у допоміжному векторі процесу `auxv`. У цьому режимі динамічний завантажувач повністю блокує розгортання токена `$ORIGIN` у відносні шляхи для захисту від атак локального користувача, який міг би створити каталог зі шкідливою бібліотекою та отримати права суперкористувача `root`.

*Інженерне рішення:* привілейовані системні бінарники не слід розповсюджувати у вигляді переносних бандлів; для них слід використовувати нативні системні пакети дистрибутива (`.deb` або `.rpm`) із встановленням у стандартні захищені каталоги `/usr/bin` та `/usr/lib`, або запускати їх через ізольовані системні служби systemd.

### 4.4. Несумісність драйверів прискорювачів та GPU

Якщо програма використовує технології апаратного прискорення графіки або нейромережевих обчислень (OpenGL, Vulkan, CUDA), копіювання бібліотек `libGL.so` чи `libcuda.so` всередину бандла гарантовано викличе збій запуску на іншій машині. Бібліотека `libcuda.so.1` має відповідати точній версії драйвера ядра NVIDIA, встановленого на хості.

*Інженерне рішення:* апаратні бібліотеки обов'язково додаються до списку виключень `SYSTEM_EXCLUDE` і завантажуються із системних шляхів хостової ОС.

### 4.5. Управління сторонніми ресурсами та шляхами даних

Якщо додаток під час роботи зчитує статичні конфігураційні схеми, сертифікати або шаблони (наприклад, файли `cacert.pem`, схеми GSettings або модулі Python), використання жорстко зашитих шляхів `/usr/share/app` призведе до помилки їхньої відсутності на хості клієнта.

*Інженерне рішення:* лаунчер `app.sh` зобов'язаний експортувати відносні змінні оточення, що вказують на підкаталоги бандла:
```sh
export SSL_CERT_FILE="$SELF_DIR/share/ssl/cacert.pem"
export APP_CONFIG_DIR="$SELF_DIR/etc"
```

---

## 5. Чек-лист перевірки якості та автоматизована верифікація

Перед релізом переносного пакета необхідно перевірити його відповідність наступним інженерним критеріям:

1. **Відсутність абсолютних шляхів RPATH:** команда `readelf -d ./bin/telemetry-agent | grep RPATH` не повинна повертати жодного фіксованого каталогу компіляційної машини.
2. **Наявність токена `$ORIGIN` у RUNPATH:** рядок `DT_RUNPATH` має містити виключно вираз `$ORIGIN/../lib:$ORIGIN`.
3. **Успішне проходження тесту в чистому контейнері:** запуск скрипта `./app.sh` у мінімальному контейнері `docker run --rm -v $(pwd):/test debian:10 /test/app.sh` повинен виконуватися без помилок пошуку бібліотек.
4. **Коректне завершення процесів:** перевірка відсутності витоків пам'яті та дескрипторів при передачі сигналів `SIGTERM` та `SIGINT` до лаунчера `app.sh`.

Для автоматизації верифікації в конвеєрах CI/CD рекомендується використовувати матричний скрипт валідації:

```sh
#!/usr/bin/env bash
set -euo pipefail

DISTROS=("debian:10" "debian:11" "ubuntu:20.04" "ubuntu:22.04" "almalinux:8" "alpine:latest")

for DISTRO in "${DISTROS[@]}"; do
    echo "[*] Тестування бандла у середовищі $DISTRO..."
    docker run --rm -v "$(pwd)/dist:/app" "$DISTRO" /app/app.sh --version
    echo "[✓] Успішно пройдено для $DISTRO"
done
```

Такий підхід забезпечує абсолютну впевненість у тому, що сформований переносний бандл гарантовано запуститься на цільових системах клієнтів незалежно від встановлених дистрибутивних версій системних бібліотек.

### 4.6. Версіонування стандартної бібліотеки C++ (libstdc++.so.6 та Dual ABI)

Якщо проект розробляється на C++, бінарник залежить не лише від `libc.so.6`, але й від стандартної бібліотеки часу виконання C++ (`libstdc++.so.6`). Бібліотека `libstdc++` використовує власну систему версіонування символів (вузли на кшталт `GLIBCXX_3.4.29`, `GLIBCXX_3.4.30`, `GLIBCXX_3.4.32` та `CXXABI_1.3.13`).

Крім того, починаючи з випуску GCC 5.1, стандартна бібліотека C++ підтримує подвійний двійковий інтерфейс (Dual ABI, контрольований макросом `_GLIBCXX_USE_CXX11_ABI=1`). Якщо скомпілювати один компонент із новим ABI (де `std::string` та `std::list` відповідають стандарту C++11 без механізму COW), а сторонню бібліотеку лінкувати зі старим ABI, програма впаде на етапі запуску з помилкою `undefined symbol` через різницю в манглованих іменах символів.

*Інженерне рішення:* бандлер повинен копіювати відповідну версію `libstdc++.so.6` безпосередньо в каталог `lib/` бандла, забезпечуючи її узгодженість із `libc.so.6` та усуваючи будь-які конфлікти версій C++ рантайму хоста.

### 4.7. Динамічні плагіни та виклики dlopen() під час роботи застосунку

Багато архітектурних систем (наприклад, графічні рушії, бази даних, системи збору метрик або мережеві адаптери) використовують модульну структуру, підвантажуючи додаткові спільні бібліотеки за запитом за допомогою функції `dlopen("plugin_custom.so", RTLD_NOW | RTLD_GLOBAL)`.

Оскільки ці плагіни не зафіксовані в статичній таблиці `DT_NEEDED` головного виконуваного файлу, стандартний рекурсивний аналіз через `ldd` їх не виявляє. Якщо плагін спробує завантажити сторонню бібліотеку, яка відсутня на цільовій машині, виклик `dlopen()` поверне нульовий вказівник `NULL`, а виклик `dlerror()` повідомить про відсутність залежності.

*Інженерне рішення:* бандлер повинен підтримувати каталог плагінів `plugins/` всередині бандла. Для кожного файлу плагіна утиліта `patchelf` встановлює `DT_RUNPATH = '$ORIGIN/../lib:$ORIGIN'`, а головна програма під час ініціалізації налаштовує відносний шлях пошуку плагінів відносно каталогу бінарника.
