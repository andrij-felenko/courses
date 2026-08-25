# ⚙️ Парсер секції .note.gnu.build-id та видобування відбитка бінарника

Коли системна утиліта налагодження (`gdb`, `perf` чи демон збору аварійних дампів `systemd-coredump`) аналізує скомпільований бінарник або образ пам'яті процесу, їй потрібно витягти унікальний відбиток збірки — Build ID, а також перевірити наявність секції лінкування `.gnu_debuglink`. Прямий парсинг структури ELF у пам'яті безпосередньо через системний виклик `mmap` дозволяє отримати ці метадані за частки мікросекунди без запуску важких зовнішніх утиліт на зразок `readelf` чи `objdump`.

Нижче наведено робочу реалізацію, яка відображає вхідний бінарний файл у пам'ять, валідує заголовок ELF64, проходить таблицею заголовків секцій (Section Header Table) і знаходить:
1. Секцію приміток `.note.gnu.build-id` (тип `SHT_NOTE`), з якої вичитує структуру `Elf64_Nhdr`, перевіряє ім'я власника `"GNU"` та виводить 160-бітний або 128-бітний шістнадцятковий хеш.
2. Секцію зв'язування `.gnu_debuglink`, звідки вилучає ASCII-ім'я відокремленого налагоджувального файлу та 32-бітну контрольну суму CRC32.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <elf.h>

#ifndef NT_GNU_BUILD_ID
#define NT_GNU_BUILD_ID 3
#endif

// Вирівнювання зміщення дескриптора примітки до межі 4 або 8 байтів
static inline size_t align_up(size_t offset, size_t alignment) {
    return (offset + alignment - 1) & ~(alignment - 1);
}

// Видобування Build ID із сирого буфера секції приміток (SHT_NOTE / PT_NOTE)
static bool extract_build_id_from_note(const uint8_t *note_data, size_t note_size,
                                      char *hex_out, size_t hex_max) {
    size_t offset = 0;
    while (offset + sizeof(Elf64_Nhdr) <= note_size) {
        const Elf64_Nhdr *nhdr = (const Elf64_Nhdr *)(note_data + offset);
        offset += sizeof(Elf64_Nhdr);

        const char *name = (const char *)(note_data + offset);
        offset = align_up(offset + nhdr->n_namesz, 4);

        const uint8_t *desc = note_data + offset;
        offset = align_up(offset + nhdr->n_descsz, 4);

        if (offset > note_size) {
            break; // Захист від пошкоджених зміщень у заголовку
        }

        // Перевіряємо тип примітки NT_GNU_BUILD_ID та ім'я "GNU"
        if (nhdr->n_type == NT_GNU_BUILD_ID && nhdr->n_namesz == 4 &&
            strncmp(name, "GNU", 4) == 0) {
            if (nhdr->n_descsz * 2 + 1 > hex_max) {
                return false;
            }
            for (uint32_t i = 0; i < nhdr->n_descsz; ++i) {
                snprintf(hex_out + (i * 2), 3, "%02x", desc[i]);
            }
            hex_out[nhdr->n_descsz * 2] = '\0';
            return true;
        }
    }
    return false;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях-до-elf-бінарника>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *filepath = argv[1];
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття файлу");
        return EXIT_FAILURE;
    }

    struct stat st;
    if (fstat(fd, &st) < 0 || st.st_size < (off_t)sizeof(Elf64_Ehdr)) {
        perror("Некоректний розмір файлу");
        close(fd);
        return EXIT_FAILURE;
    }

    const uint8_t *mapped = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd); // Дескриптор більше не потрібен після mmap
    if (mapped == MAP_FAILED) {
        perror("Помилка mmap");
        return EXIT_FAILURE;
    }

    // Валідація магічних байтів ELF
    const Elf64_Ehdr *ehdr = (const Elf64_Ehdr *)mapped;
    if (memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "Помилка: файл не є форматом ELF.\n");
        munmap((void *)mapped, st.st_size);
        return EXIT_FAILURE;
    }

    if (ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
        fprintf(stderr, "Помилка: підтримується лише 64-бітний ELF (ELFCLASS64).\n");
        munmap((void *)mapped, st.st_size);
        return EXIT_FAILURE;
    }

    // Перевірка меж таблиці заголовків секцій
    if (ehdr->e_shoff == 0 || ehdr->e_shoff + ehdr->e_shnum * sizeof(Elf64_Shdr) > (size_t)st.st_size) {
        fprintf(stderr, "Помилка: пошкоджена або відсутня таблиця секцій (SHT).\n");
        munmap((void *)mapped, st.st_size);
        return EXIT_FAILURE;
    }

    const Elf64_Shdr *shdrs = (const Elf64_Shdr *)(mapped + ehdr->e_shoff);
    const Elf64_Shdr *shstrtab_hdr = &shdrs[ehdr->e_shstrndx];
    const char *shstrtab = (const char *)(mapped + shstrtab_hdr->sh_offset);

    char build_id_hex[128] = {0};
    bool found_build_id = false;
    char debuglink_name[256] = {0};
    uint32_t debuglink_crc = 0;
    bool found_debuglink = false;

    for (uint16_t i = 0; i < ehdr->e_shnum; ++i) {
        const char *sec_name = shstrtab + shdrs[i].sh_name;
        
        // 1. Пошук .note.gnu.build-id
        if (shdrs[i].sh_type == SHT_NOTE && strcmp(sec_name, ".note.gnu.build-id") == 0) {
            const uint8_t *sec_data = mapped + shdrs[i].sh_offset;
            size_t sec_size = shdrs[i].sh_size;
            if (extract_build_id_from_note(sec_data, sec_size, build_id_hex, sizeof(build_id_hex))) {
                found_build_id = true;
            }
        }

        // 2. Пошук .gnu_debuglink
        if (strcmp(sec_name, ".gnu_debuglink") == 0 && shdrs[i].sh_size >= 5) {
            const uint8_t *sec_data = mapped + shdrs[i].sh_offset;
            size_t sec_size = shdrs[i].sh_size;
            
            // Назва файлу завершується нульовим байтом, а останні 4 байти — CRC32
            size_t name_len = strnlen((const char *)sec_data, sec_size - 4);
            if (name_len < sizeof(debuglink_name)) {
                memcpy(debuglink_name, sec_data, name_len);
                debuglink_name[name_len] = '\0';
                // Останні 4 байти секції — CRC32 у форматі little-endian
                debuglink_crc = *(const uint32_t *)(sec_data + sec_size - 4);
                found_debuglink = true;
            }
        }
    }

    printf("Аналіз бінарника: %s\n", filepath);
    if (found_build_id) {
        printf("  [✓] Build ID:       %s\n", build_id_hex);
        printf("      Канонічний шлях: /usr/lib/debug/.build-id/%.2s/%s.debug\n",
               build_id_hex, build_id_hex + 2);
    } else {
        printf("  [✗] Build ID:       відсутній\n");
    }

    if (found_debuglink) {
        printf("  [✓] gnu_debuglink:  %s (CRC32: 0x%08x)\n", debuglink_name, debuglink_crc);
    } else {
        printf("  [✗] gnu_debuglink:  відсутній\n");
    }

    munmap((void *)mapped, st.st_size);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <format>
#include <span>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <elf.h>

#ifndef NT_GNU_BUILD_ID
#define NT_GNU_BUILD_ID 3
#endif

// RAII-обгортка над покажчиком mmap для безпечного звільнення ресурсу
class MemoryMappedFile {
public:
    static std::expected<MemoryMappedFile, std::string> open(std::string_view path) {
        int fd = ::open(path.data(), O_RDONLY);
        if (fd < 0) {
            return std::unexpected(std::format("Не вдалося відкрити файл: {}", std::strerror(errno)));
        }

        struct stat st{};
        if (::fstat(fd, &st) < 0 || st.st_size < static_cast<off_t>(sizeof(Elf64_Ehdr))) {
            ::close(fd);
            return std::unexpected("Файл замалий або пошкоджений");
        }

        void *addr = ::mmap(nullptr, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
        ::close(fd);

        if (addr == MAP_FAILED) {
            return std::unexpected(std::format("Помилка mmap: {}", std::strerror(errno)));
        }

        return MemoryMappedFile(static_cast<const uint8_t *>(addr), static_cast<size_t>(st.st_size));
    }

    ~MemoryMappedFile() {
        if (data_ != nullptr) {
            ::munmap(const_cast<uint8_t *>(data_), size_);
        }
    }

    MemoryMappedFile(const MemoryMappedFile &) = delete;
    MemoryMappedFile &operator=(const MemoryMappedFile &) = delete;

    MemoryMappedFile(MemoryMappedFile &&other) noexcept
        : data_(other.data_), size_(other.size_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }

    MemoryMappedFile &operator=(MemoryMappedFile &&other) noexcept {
        if (this != &other) {
            if (data_) ::munmap(const_cast<uint8_t *>(data_), size_);
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::span<const uint8_t> bytes() const noexcept {
        return {data_, size_};
    }

private:
    MemoryMappedFile(const uint8_t *data, size_t size) : data_(data), size_(size) {}
    const uint8_t *data_{nullptr};
    size_t size_{0};
};

struct DebugMetadata {
    std::optional<std::string> build_id;
    std::optional<std::string> debuglink_name;
    std::optional<uint32_t> debuglink_crc;
};

// Парсер структури ELF64
class ElfInspector {
public:
    static std::expected<DebugMetadata, std::string> inspect(std::span<const uint8_t> buffer) {
        if (buffer.size() < sizeof(Elf64_Ehdr)) {
            return std::unexpected("Розмір буфера менший за розмір Elf64_Ehdr");
        }

        const auto *ehdr = reinterpret_cast<const Elf64_Ehdr *>(buffer.data());
        if (std::memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
            return std::unexpected("Сигнатура файлу не відповідає стандарту ELF");
        }

        if (ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
            return std::unexpected("Підтримуються лише 64-бітні бінарники (ELFCLASS64)");
        }

        if (ehdr->e_shoff == 0 || ehdr->e_shoff + ehdr->e_shnum * sizeof(Elf64_Shdr) > buffer.size()) {
            return std::unexpected("Таблиця секцій SHT виходить за межі файлу");
        }

        const auto *shdrs = reinterpret_cast<const Elf64_Shdr *>(buffer.data() + ehdr->e_shoff);
        const auto &shstrtab_hdr = shdrs[ehdr->e_shstrndx];
        const char *shstrtab = reinterpret_cast<const char *>(buffer.data() + shstrtab_hdr.sh_offset);

        DebugMetadata meta;

        for (size_t i = 0; i < ehdr->e_shnum; ++i) {
            std::string_view sec_name = shstrtab + shdrs[i].sh_name;

            if (shdrs[i].sh_type == SHT_NOTE && sec_name == ".note.gnu.build-id") {
                auto note_span = buffer.subspan(shdrs[i].sh_offset, shdrs[i].sh_size);
                meta.build_id = parse_build_id_note(note_span);
            } else if (sec_name == ".gnu_debuglink" && shdrs[i].sh_size >= 5) {
                auto sec_span = buffer.subspan(shdrs[i].sh_offset, shdrs[i].sh_size);
                const char *raw_str = reinterpret_cast<const char *>(sec_span.data());
                size_t name_len = ::strnlen(raw_str, sec_span.size() - 4);
                meta.debuglink_name = std::string(raw_str, name_len);

                uint32_t crc = 0;
                std::memcpy(&crc, sec_span.data() + sec_span.size() - 4, sizeof(uint32_t));
                meta.debuglink_crc = crc;
            }
        }

        return meta;
    }

private:
    static size_t align_up(size_t val, size_t alignment) noexcept {
        return (val + alignment - 1) & ~(alignment - 1);
    }

    static std::optional<std::string> parse_build_id_note(std::span<const uint8_t> note_span) {
        size_t offset = 0;
        while (offset + sizeof(Elf64_Nhdr) <= note_span.size()) {
            const auto *nhdr = reinterpret_cast<const Elf64_Nhdr *>(note_span.data() + offset);
            offset += sizeof(Elf64_Nhdr);

            std::string_view name(reinterpret_cast<const char *>(note_span.data() + offset), nhdr->n_namesz);
            offset = align_up(offset + nhdr->n_namesz, 4);

            const uint8_t *desc = note_span.data() + offset;
            offset = align_up(offset + nhdr->n_descsz, 4);

            if (offset > note_span.size()) {
                break;
            }

            if (nhdr->n_type == NT_GNU_BUILD_ID && nhdr->n_namesz == 4 && name.starts_with("GNU")) {
                std::string hex_str;
                hex_str.reserve(nhdr->n_descsz * 2);
                for (size_t j = 0; j < nhdr->n_descsz; ++j) {
                    hex_str += std::format("{:02x}", desc[j]);
                }
                return hex_str;
            }
        }
        return std::nullopt;
    }
};

int main(int argc, char *argv[]) {
    if (argc < 2) {
        std::cerr << std::format("Використання: {} <шлях-до-elf-бінарника>\n", argv[0]);
        return EXIT_FAILURE;
    }

    auto mapped_res = MemoryMappedFile::open(argv[1]);
    if (!mapped_res) {
        std::cerr << std::format("Помилка: {}\n", mapped_res.error());
        return EXIT_FAILURE;
    }

    auto meta_res = ElfInspector::inspect(mapped_res->bytes());
    if (!meta_res) {
        std::cerr << std::format("Помилка аналізу ELF: {}\n", meta_res.error());
        return EXIT_FAILURE;
    }

    const auto &meta = *meta_res;
    std::cout << std::format("Аналіз бінарника: {}\n", argv[1]);

    if (meta.build_id) {
        std::cout << std::format("  [✓] Build ID:       {}\n", *meta.build_id);
        std::cout << std::format("      Канонічний шлях: /usr/lib/debug/.build-id/{}/{}.debug\n",
                                 meta.build_id->substr(0, 2), meta.build_id->substr(2));
    } else {
        std::cout << "  [✗] Build ID:       відсутній\n";
    }

    if (meta.debuglink_name && meta.debuglink_crc) {
        std::cout << std::format("  [✓] gnu_debuglink:  {} (CRC32: 0x{:08x})\n",
                                 *meta.debuglink_name, *meta.debuglink_crc);
    } else {
        std::cout << "  [✗] gnu_debuglink:  відсутній\n";
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 2. Покроковий розбір низькорівневих механізмів парсингу

### Вирівнювання дескрипторів приміток у стандарті ELF

Специфікація формату ELF вимагає строгого вирівнювання структур у пам'яті. Для секцій приміток типу `SHT_NOTE` та сегментів `PT_NOTE` використовується особливе правило падінгу:
1. Заголовок примітки `Elf64_Nhdr` має фіксований розмір 12 байтів (три 32-бітних беззнакових цілих: `n_namesz`, `n_descsz`, `n_type`).
2. Рядок імені власника (`name`) довжиною `n_namesz` байтів розміщується безпосередньо після заголовка. Після нього обов'язково додаються байти вирівнювання до найближчої 4-байтової межі (для систем GNU Linux) або 8-байтової межі (для систем Solaris/FreeBSD 64-bit).
3. Тіло дескриптора (`desc`) довжиною `n_descsz` байтів також доповнюється нулями до 4-байтової межі перед наступним записом примітки.

Функція `align_up(offset, alignment)` обчислює коректне зміщення за формулою бітової арифметики:

```
(offset + alignment - 1) & ~(alignment - 1)
```

Якщо це вирівнювання не враховувати, покажчик на дескриптор зміщується, через що програма зчитує сміттєві байти замість криптографічного хешу SHA-1 або генерує апаратне виключення неналаштованого доступу (*unaligned memory access fault*) на архітектурах зі строгими вимогами до вирівнювання пам'яті (ARMv6, SPARC).

### Парсинг структури `.gnu_debuglink` та перевірка CRC32

Секція `.gnu_debuglink` формується утилітою `objcopy --add-gnu-debuglink`. На відміну від стандартних таблиць ELF, вона не має окремого заголовка:
* Початок секції містить ASCII-рядок імені відокремленого налагоджувального файлу (наприклад, `app.debug\0`).
* Довжина рядка з нульовим символом визначається функцією `strnlen()`.
* Завершальні 4 байти секції (розраховані як `sec_size - 4`) містять 32-бітну контрольну суму CRC-32 файлу `app.debug` у форматі little-endian.

Для перевірки відповідності знайденого файлу налагоджувач зчитує весь вміст `app.debug` блоками по 64 КБ і розраховує контрольну суму за класичним поліномом IEEE 802.3 `0xEDB88320`. Якщо обчислений результат збігається зі значенням у секції `.gnu_debuglink`, файл визнається дійсним.

### Порівняння ідіом мов C та C++

* **Керування ресурсами пам'яті**: У прикладі на C виклик `mmap()` вимагає явного ручного звільнення через `munmap()` на кожній гілці завершення (`return EXIT_FAILURE`). У версії C++20 клас `MemoryMappedFile` реалізує ідіому RAII (*Resource Acquisition Is Initialization*), гарантуючи звільнення відображених сторінок пам'яті деструктором навіть у разі виникнення помилок чи дострокового виходу з функції.
* **Безпека меж буферів**: Замість небезпечної адресної арифметики сирих покажчиків (`uint8_t *`), код на C++ використовує об'єкти `std::span<const uint8_t>`, які передають неволодіючий зріз пам'яті з фіксованим розміром і запобігають переповненню буфера (*buffer overflow*).
* **Монадична обробка помилок**: Шаблон `std::expected<T, E>` дозволяє повертати результат парсингу або текстове повідомлення про помилку без використання механізму винятків (*exceptions*), що зберігає детермінізм та швидкість системного коду.

### Зчитування Build ID з пам'яті працюючого процесу через допоміжний вектор та dl_iterate_phdr

Коли утиліта працює всередині самого процесу (наприклад, агент збору метрик або обробник сигналів аварії), звертатися до файлової системи через `open()` необов'язково. Ядро Linux передає процесу таблицю заголовків програми через допоміжний вектор (*auxiliary vector*, системні виклики `getauxval(AT_PHDR)` та `getauxval(AT_PHNUM)`). 

Для дослідження завантажених спільних бібліотек динамічний лінкер надає функцію `dl_iterate_phdr()`:

:::tabs
```c
#define _GNU_SOURCE
#include <link.h>
#include <stdio.h>
#include <stdint.h>

static int callback(struct dl_phdr_info *info, size_t size, void *data) {
    printf("Завантажений модуль: %s (базова адреса: 0x%lx)\n",
           info->dlpi_name[0] ? info->dlpi_name : "головний бінарник",
           info->dlpi_addr);
    for (int i = 0; i < info->dlpi_phnum; ++i) {
        if (info->dlpi_phdr[i].p_type == PT_NOTE) {
            const uint8_t *note_addr = (const uint8_t *)(info->dlpi_addr + info->dlpi_phdr[i].p_vaddr);
            // Виклик функції вилучення Build ID прямо з пам'яті
        }
    }
    return 0;
}
```
```cpp
#include <link.h>
#include <iostream>
#include <string_view>
#include <format>
#include <span>

static int callback(dl_phdr_info *info, size_t, void *) {
    std::string_view name = (info->dlpi_name && info->dlpi_name[0]) ? info->dlpi_name : "головний бінарник";
    std::cout << std::format("Завантажений модуль: {} (базова адреса: 0x{:x})\n", name, info->dlpi_addr);
    
    std::span<const Elf64_Phdr> phdrs(info->dlpi_phdr, info->dlpi_phnum);
    for (const auto &phdr : phdrs) {
        if (phdr.p_type == PT_NOTE) {
            const auto *note_addr = reinterpret_cast<const uint8_t *>(info->dlpi_addr + phdr.p_vaddr);
            // Виклик C++ методу вилучення Build ID
        }
    }
    return 0;
}
```
:::

Програма може пройтися масивом `Elf64_Phdr`, знайти сегмент із типом `PT_NOTE` та викликати функцію `extract_build_id_from_note` безпосередньо над віртуальною пам'яттю процесу без жодного дискового введення-виведення.

### Збірка та верифікація тестового бінарника

Для перевірки роботи парсера тестову програму можна скомпілювати з явним увімкненням генерації відбитка:

```bash
# Компіляція C-версії з генерацією SHA-1 Build ID
gcc -O2 -g -Wl,--build-id=sha1 -o build_id_inspector_c extractor.c

# Компіляція C++-версії за стандартом C++20
g++ -std=c++20 -O2 -g -Wl,--build-id=sha1 -o build_id_inspector_cpp extractor.cpp

# Звірка результатів зі стандартною утилітою GNU readelf
readelf -n /usr/bin/python3
./build_id_inspector_cpp /usr/bin/python3
```

У разі успішного виконання утиліта повертає нульовий код завершення `EXIT_SUCCESS` і друкує рядок Build ID разом із канонічним шляхом до файлу символів у сховищі `/usr/lib/debug/.build-id/`. Якщо вхідний файл не містить секції примітки (наприклад, скомпільований старим компонувальником із прапорцем `-Wl,--build-id=none`), програма коректно сповіщає про відсутність відбитка та повертає код стану без аварійного збою.

### Обробка крайових випадків та пошкоджених файлів

Утиліти аналізу ELF-бінарників мають бути захищені від навмисно спотворених або пошкоджених файлів:
1. **Перевірка магічних байтів (`ELFMAG`)**: Перші 4 байти файлу мають містити послідовність `0x7f 'E' 'L' 'F'`. Якщо байти не збігаються, операція негайно переривається.
2. **Перевірка меж таблиці секцій (`e_shoff`)**: Поле `e_shoff` вказує на зміщення SHT від початку файлу. Програма перевіряє умову `e_shoff + e_shnum * sizeof(Elf64_Shdr) <= file_size`, захищаючи процес від виходу за межі відображеної пам'яті (*SIGSEGV*).
3. **Статично скомпільовані бінарники без SHT**: Якщо бінарник було піддано максимальному очищенню з видаленням самої таблиці секцій (`e_shoff == 0`), секції приміток можна знайти шляхом ітерації за сегментами завантаження `PT_NOTE` у таблиці заголовків програми (*Program Header Table*, PHT), на яку вказує поле `e_phoff`.
