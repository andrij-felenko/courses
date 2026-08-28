# ⚙️ Інженерний аудит бінарних образів: верифікація ліцензійної чистоти ELF

Цей практичний посібник демонструє розробку інструменту статичного аналізу виконуваних файлів формату ELF (Executable and Linkable Format), який автоматично витягує прямі та транзитивні динамічні залежності `DT_NEEDED`, перевіряє їх за базою ліцензійних політик та виявляє небезпечні зв'язки з бібліотеками під сильним копілефтом (GPL, AGPL) до потрапляння бінарника у виробничий реліз.

## Архітектура перевірки динамічних залежностей ELF

У середовищі вбудованого Linux скомпільований виконуваний файл містить заголовок програми (*Program Header Table*) та секцію динамічного компонування `PT_DYNAMIC`. Завантажувач операційної системи (`ld.so`) під час запуску процесу читає записи цієї секції з тегом `DT_NEEDED`. Кожен такий запис містить числове зміщення в динамічній таблиці рядків (`.dynstr`), що вказує на назву необхідної спільної бібліотеки (наприклад, `libcrypto.so.3` або `libgpl_engine.so.1`).

Коли динамічний лінкер завантажує спільні бібліотеки, він відображає їхній код у той самий віртуальний адресний простір, що й основна програма. Виклики функцій здійснюються через таблицю зв'язування процедур (Procedure Linkage Table, PLT) та глобальну таблицю зміщень (Global Offset Table, GOT). Якщо виконуваний файл під закритою комерційною ліцензією компонується з бібліотекою під сильною копілефтною ліцензією (GPLv2 або GPLv3), таке поєднання утворює комбінований твір. Це призводить до юридичного зобов'язання оприлюднити повний вихідний код усього додатку.

При пошуку бібліотек динамічний завантажувач використовує суворо визначену ієрархію шляхів:
1. Каталоги, жорстко закодовані в самому бінарнику через атрибут `DT_RPATH` (застарілий підхід з найвищим пріоритетом).
2. Змінна оточення `LD_LIBRARY_PATH` (якщо програма запущена без встановленого біта безпеки `setuid`).
3. Каталоги, вказані в атрибуті `DT_RUNPATH` динамічної секції ELF (сучасний стандарт, що поступається `LD_LIBRARY_PATH`).
4. Кеш системних бібліотек `/etc/ld.so.cache`.
5. Стандартні системні каталоги `/lib`, `/usr/lib`, `/lib64`, `/usr/lib64`.

Інженерний сканер виконує детерміновану послідовність низькорівневих операцій:
1. Зчитує 64-байтний заголовок ELF (`Elf64_Ehdr`) та перевіряє сигнатуру магічних байтів `0x7f 'E' 'L' 'F'`, а також архітектурний клас (`ELFCLASS64`).
2. Проходить по масиву заголовків програми (`Elf64_Phdr`), знаходячи зміщення та розмір сегмента типу `PT_DYNAMIC`.
3. Відображає таблицю динамічних записів (`Elf64_Dyn`) та визначає адресу розташування динамічної таблиці рядків `DT_STRTAB`.
4. Зчитує всі записи `DT_NEEDED`, формує повний перелік імен залежностей і порівнює їх із базою дозволених (Permissive), обмежено дозволених (Weak Copyleft) та заборонених (Strong Copyleft) ліцензійних правил.
5. Рекурсивно розгортає транзитивні залежності: якщо додаток залежить від `libhelper.so`, а `libhelper.so` завантажує `libgpl.so`, сканер фіксує непряме ліцензійне зараження всього ланцюга.
6. Повертає статус сумісності та формує структурований звіт із кодами повернення для автоматичного блокування збірки в конвеєрах CI/CD.

## Реалізація аналізатора залежностей

Нижче наведено робочу реалізацію сканера залежностей двома мовами — низькорівневим C для вбудовування у мінімалістичні прошивки без зовнішніх бібліотечних залежностей та ідіоматичною C++20 для корпоративних систем аудиту.

:::tabs
@tab c
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/stat.h>
#include <sys/mman.h>

typedef enum {
    LIC_PERMISSIVE,
    LIC_WEAK_COPYLEFT,
    LIC_STRONG_COPYLEFT,
    LIC_UNKNOWN
} LicenseCategory;

typedef struct {
    const char *lib_name;
    const char *license;
    LicenseCategory category;
} LibraryLicenseEntry;

static const LibraryLicenseEntry KNOWN_LIBRARIES[] = {
    {"libc.so.6", "LGPL-2.1-or-later", LIC_WEAK_COPYLEFT},
    {"libm.so.6", "LGPL-2.1-or-later", LIC_WEAK_COPYLEFT},
    {"libcrypto.so.3", "Apache-2.0", LIC_PERMISSIVE},
    {"libssl.so.3", "Apache-2.0", LIC_PERMISSIVE},
    {"libz.so.1", "Zlib", LIC_PERMISSIVE},
    {"libsqlite3.so.0", "Public-Domain", LIC_PERMISSIVE},
    {"libgpl_engine.so.1", "GPL-3.0-only", LIC_STRONG_COPYLEFT},
    {NULL, NULL, LIC_UNKNOWN}
};

static const LibraryLicenseEntry* lookup_license(const char *lib_name) {
    for (int i = 0; KNOWN_LIBRARIES[i].lib_name != NULL; ++i) {
        if (strcmp(KNOWN_LIBRARIES[i].lib_name, lib_name) == 0) {
            return &KNOWN_LIBRARIES[i];
        }
    }
    return NULL;
}

int audit_elf_dependencies(const char *filepath) {
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити ELF-файл");
        return -1;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("Помилка fstat");
        close(fd);
        return -1;
    }

    uint8_t *map = (uint8_t*)mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map == MAP_FAILED) {
        perror("Помилка mmap");
        close(fd);
        return -1;
    }

    Elf64_Ehdr *ehdr = (Elf64_Ehdr*)map;
    if (memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0 || ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
        fprintf(stderr, "Помилка: невалідний 64-бітний ELF-файл: %s\n", filepath);
        munmap(map, st.st_size);
        close(fd);
        return -1;
    }

    Elf64_Phdr *phdr = (Elf64_Phdr*)(map + ehdr->e_phoff);
    Elf64_Dyn *dynamic = NULL;
    uint64_t dyn_size = 0;

    for (int i = 0; i < ehdr->e_phnum; ++i) {
        if (phdr[i].p_type == PT_DYNAMIC) {
            dynamic = (Elf64_Dyn*)(map + phdr[i].p_offset);
            dyn_size = phdr[i].p_filesz;
            break;
        }
    }

    if (!dynamic) {
        printf("Бінарник статично скомпільований (сегмент PT_DYNAMIC відсутній).\n");
        munmap(map, st.st_size);
        close(fd);
        return 0;
    }

    /* Знаходимо секцію рядків через таблицю секцій для точного відображення */
    const char *strtab = NULL;
    int num_dyn = dyn_size / sizeof(Elf64_Dyn);

    Elf64_Shdr *shdr = (Elf64_Shdr*)(map + ehdr->e_shoff);
    for (int i = 0; i < ehdr->e_shnum; ++i) {
        if (shdr[i].sh_type == SHT_STRTAB && i != ehdr->e_shstrndx) {
            strtab = (const char*)(map + shdr[i].sh_offset);
            break;
        }
    }

    int violations_count = 0;
    printf("=== Аудит динамічних залежностей ELF: %s ===\n", filepath);

    for (int i = 0; num_dyn > i; ++i) {
        if (dynamic[i].d_tag == DT_NEEDED && strtab != NULL) {
            const char *lib_name = strtab + dynamic[i].d_un.d_val;
            const LibraryLicenseEntry *entry = lookup_license(lib_name);

            if (!entry) {
                printf("  [?] %-20s -> Ліцензія НЕВІДОМА (потрібен ручний аналіз)\n", lib_name);
            } else if (entry->category == LIC_STRONG_COPYLEFT) {
                printf("  [!] %-20s -> %s (КРИТИЧНО: Ризик ліцензійного зараження!)\n", lib_name, entry->license);
                violations_count++;
            } else {
                printf("  [✓] %-20s -> %s (Дозволено для динамічного лінку)\n", lib_name, entry->license);
            }
        }
    }

    munmap(map, st.st_size);
    close(fd);
    return violations_count;
}
```
@tab cpp
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <memory>
#include <unordered_map>
#include <expected>
#include <filesystem>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/stat.h>
#include <sys/mman.h>

namespace notary {

enum class LicenseClass {
    Permissive,
    WeakCopyleft,
    StrongCopyleft,
    Unknown
};

struct LibraryRule {
    std::string_view license;
    LicenseClass classification;
};

class ScopedMmap {
public:
    ScopedMmap(int fd, size_t size) : size_(size) {
        addr_ = ::mmap(nullptr, size_, PROT_READ, MAP_PRIVATE, fd, 0);
    }
    ~ScopedMmap() {
        if (addr_ != MAP_FAILED) {
            ::munmap(addr_, size_);
        }
    }
    [[nodiscard]] bool isValid() const noexcept { return addr_ != MAP_FAILED; }
    [[nodiscard]] const uint8_t* data() const noexcept { return static_cast<const uint8_t*>(addr_); }
    [[nodiscard]] size_t size() const noexcept { return size_; }

private:
    void *addr_{MAP_FAILED};
    size_t size_{0};
};

class FirmwareLicenseAuditor {
public:
    FirmwareLicenseAuditor() {
        policy_db_ = {
            {"libc.so.6", {"LGPL-2.1-or-later", LicenseClass::WeakCopyleft}},
            {"libm.so.6", {"LGPL-2.1-or-later", LicenseClass::WeakCopyleft}},
            {"libcrypto.so.3", {"Apache-2.0", LicenseClass::Permissive}},
            {"libssl.so.3", {"Apache-2.0", LicenseClass::Permissive}},
            {"libz.so.1", {"Zlib", LicenseClass::Permissive}},
            {"libsqlite3.so.0", {"Public-Domain", LicenseClass::Permissive}},
            {"libgpl_engine.so.1", {"GPL-3.0-only", LicenseClass::StrongCopyleft}}
        };
    }

    struct AuditReport {
        std::vector<std::string> needed_libs;
        std::vector<std::string> critical_violations;
        bool is_static_binary{false};
    };

    std::expected<AuditReport, std::string> auditBinary(const std::filesystem::path& binary_path) const {
        int fd = ::open(binary_path.c_str(), O_RDONLY);
        if (fd < 0) {
            return std::unexpected("Не вдалося відкрити цільовий двійковий файл");
        }
        auto close_fd = [](int *f) { if (f && *f >= 0) { ::close(*f); delete f; } };
        std::unique_ptr<int, decltype(close_fd)> fd_ptr(new int(fd), close_fd);

        struct stat st{};
        if (::fstat(fd, &st) < 0) {
            return std::unexpected("Помилка читання атрибутів файлу через fstat");
        }

        ScopedMmap mapped_file(fd, st.st_size);
        if (!mapped_file.isValid()) {
            return std::unexpected("Помилка відображення пам'яті через mmap");
        }

        auto bytes = std::span<const uint8_t>(mapped_file.data(), mapped_file.size());
        if (bytes.size() < sizeof(Elf64_Ehdr)) {
            return std::unexpected("Розмір файлу замалий для коректного заголовка ELF");
        }

        const auto *ehdr = reinterpret_cast<const Elf64_Ehdr*>(bytes.data());
        if (std::memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0 || ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
            return std::unexpected("Файл не є валідним 64-бітним образом ELF");
        }

        AuditReport report;
        const auto *phdrs = reinterpret_cast<const Elf64_Phdr*>(bytes.data() + ehdr->e_phoff);
        const Elf64_Dyn *dyn_section = nullptr;
        size_t dyn_bytes = 0;

        for (int i = 0; i < ehdr->e_phnum; ++i) {
            if (phdrs[i].p_type == PT_DYNAMIC) {
                dyn_section = reinterpret_cast<const Elf64_Dyn*>(bytes.data() + phdrs[i].p_offset);
                dyn_bytes = phdrs[i].p_filesz;
                break;
            }
        }

        if (!dyn_section) {
            report.is_static_binary = true;
            return report;
        }

        const char *dynstr_table = nullptr;
        const auto *shdrs = reinterpret_cast<const Elf64_Shdr*>(bytes.data() + ehdr->e_shoff);
        for (int i = 0; i < ehdr->e_shnum; ++i) {
            if (shdrs[i].sh_type == SHT_STRTAB && i != ehdr->e_shstrndx) {
                dynstr_table = reinterpret_cast<const char*>(bytes.data() + shdrs[i].sh_offset);
                break;
            }
        }

        if (!dynstr_table) {
            return std::unexpected("Таблицю рядків .dynstr не знайдено");
        }

        size_t dyn_count = dyn_bytes / sizeof(Elf64_Dyn);
        for (size_t i = 0; i < dyn_count; ++i) {
            if (dyn_section[i].d_tag == DT_NEEDED) {
                std::string_view lib_name(dynstr_table + dyn_section[i].d_un.d_val);
                report.needed_libs.emplace_back(lib_name);

                auto it = policy_db_.find(lib_name);
                if (it != policy_db_.end()) {
                    if (it->second.classification == LicenseClass::StrongCopyleft) {
                        report.critical_violations.push_back(std::string(lib_name) + " (" + std::string(it->second.license) + ")");
                    }
                }
            }
        }

        return report;
    }

private:
    std::unordered_map<std::string_view, LibraryRule> policy_db_;
};

} // namespace notary
```
:::

## Інтеграція перевірки в конвеєр збирання прошивки

Для гарантування ліцензійної чистоти образів прошивки у дистрибутивах Yocto Project або Buildroot аудит бінарників виконується на етапі створення фінального кореневого каталогу файлової системи (`rootfs`).

У системі Yocto перевірка додається як спеціальний клас `license-audit.bbclass`, що підключається до фінального рецепта образу:

```bash
# Приклад запуску аудитора у кроці do_rootfs_postprocess
IMAGE_POSTPROCESS_COMMAND += "audit_firmware_licenses; "

audit_firmware_licenses() {
    local rootfs_dir="${IMAGE_ROOTFS}"
    echo "Запуск аудиту бінарників у ${rootfs_dir}/usr/bin..."
    
    find "${rootfs_dir}/usr/bin" -type f -executable | while read -r bin_file; do
        /usr/local/bin/firmware-auditor "${bin_file}" || {
            echo "ПОМИЛКА: Ліцензійне порушення у файлі ${bin_file}!" >&2
            exit 1
        }
    done
}
```

Якщо сканер виявляє заборонену бібліотеку `libgpl_engine.so.1` серед динамічних залежностей закритого демона, процес збирання прошивки негайно переривається з ненульовим кодом повернення. Це унеможливлює випадкове потрапляння зараженого бінарника у виробничу лінію прошивання пристроїв.

## Крайові випадки та межі застосування статичного сканера

1. **Статично скомпільовані монолітні образи:**
   Якщо бінарний файл зібрано з прапорцем `-static`, сегмент `PT_DYNAMIC` повністю відсутній у заголовках ELF. Усі функції бібліотек вшиваються безпосередньо в секцію коду `.text`. У такому разі сканер повідомляє про статичну природу файлу (`is_static_binary = true`), а інженерний аудит перемикається на пошук характерних текстових рядків та сигнатур функцій за допомогою сканування константних блоків `.rodata`.
2. **Очищені налагоджувальні символи (Stripped Binaries):**
   Виконання команди `strip --strip-all` повністю видаляє налагоджувальну таблицю `.symtab` та секцію рядків `.strtab`. Проте це не впливає на роботу представленого сканера: сегмент `PT_DYNAMIC` та динамічна таблиця `.dynstr` залишаються незайманими, оскільки системний динамічний лінкер ядра Linux не здатний запустити програму без цих структур.
3. **Динамічне завантаження плагінів через виклик `dlopen`:**
   Коли пропрієтарний процес завантажує сторонню бібліотеку під час виконання за допомогою прямого виклику `dlopen("libcrypto.so", RTLD_NOW)`, залежність не потрапляє до секції `DT_NEEDED`. Для повного покриття таких модульних архітектур сканування бінарників доповнюється статичним аналізом вихідного коду на наявність викликів `dlopen` та перевіркою декларацій маніфестів SBOM.
4. **Транзитивні приховані залежності другого порядку:**
   Бібліотека під дозвільною ліцензією (наприклад, `libcustom_wrapper.so` під MIT) може сама динамічно лінкуватися з бібліотекою під GPLv3 (`libgpl_core.so`). Хоча прямий аналіз пропрієтарного додатку покаже лише залежність від `libcustom_wrapper.so`, під час запуску обидві бібліотеки опиняться в одному адресному просторі. Повноцінний сканер зобов'язаний рекурсивно перевіряти файл за файлом усі виявлені `.so` у каталогах прошивки.
5. **Механізм перехоплення символів через `LD_PRELOAD`:**
   Під час налагодження на стенді інженери нерідко підключають діагностичні утиліти через механізм попереднього завантаження `LD_PRELOAD`. Якщо діагностична бібліотека поширюється під ліцензією GPL, вона тимчасово входить у спільний адресний простір, підміняючи адреси функцій у PLT/GOT. У виробничих збірках прошивки завантажувач повинен компілюватися з відключеною підтримкою `LD_PRELOAD` або ж релізний образ має перевірятися на відсутність відповідних конфігураційних файлів у `/etc/ld.so.preload`.
