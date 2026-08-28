# ⚙️ Утиліта перевірки чистоти й відтворності релізного артефакту

Будь-який автоматизований випуск потребує незалежного інструмента, який інспектує готовий двійковий артефакт перед передачею на конвеєр чи заводський стенд. Цей проєкт реалізує консольну утиліту перевірки образу прошивки, яка аналізує ELF-заголовок, перевіряє ліміти секцій Flash та RAM, шукає сліди брудного стану системи контролю версій і валідує контрольну суму.

## Задача й архітектура перевірки

Під час компіляції прошивки для мікроконтролерів ARM Cortex-M або RISC-V вихідний файл у форматі ELF (*Executable and Linkable Format*) містить повну структуру образу: таблицю заголовків програми (англ. *Program Headers*), таблицю секцій (англ. *Section Headers*), таблицю символів і рядків. Перед тим як утиліта `objcopy` перетворить цей файл на «сирий» бінарник `.bin` для подальшого прошивання у мікроконтролер, артефакт повинен пройти сувору інспекцію.

Утиліта-воротар повинна автоматично відповісти на чотири критичні запитання:
1. **Чи є файл валідним 32-бітним ELF-файлом для цільової вбудованої архітектури?** Перевіряються магічні байти `0x7F 'E' 'L' 'F'`, 32-розрядний формат (клас `ELFCLASS32`), порядок байтів `little-endian` та тип файлу `ET_EXEC`.
2. **Чи вкладається сума розмірів секцій коду й констант (`.text` + `.rodata` + `.data`) у фізичний обсяг Flash мікроконтролера?** Важливо пам'ятати, що секція ініціалізованих глобальних змінних `.data` зберігається у Flash, звідки копіюється в RAM під час запуску в процедурі `Reset_Handler`.
3. **Чи вкладається сума ініціалізованих та нульових змінних (`.data` + `.bss`) у фізичний обсяг оперативної пам'яті (RAM)?** Перевищення ліміту призводить до перекриття стека викликів і миттєвого зависання пристрою під час виконання першої ж функції.
4. **Чи не містить рядок версії у секції констант позначки `-dirty`, яка свідчить про незафіксовані локальні зміни в Git?** Якщо розробник збирав прошивку з незбереженими файлами, утиліта `git describe` додає суфікс `-dirty`, який потрапляє у бінарні константи `.rodata`.

Якщо бодай одна умова порушена, утиліта друкує діагностичне повідомлення у стандартний потік помилок `stderr` і негайно завершується з ненульовим кодом виходу (`exit code 1`), зупиняючи весь релізний конвеєр.

## Реалізація верифікатора

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define ELF_MAGIC0       0x7F
#define ELF_MAGIC1       'E'
#define ELF_MAGIC2       'L'
#define ELF_MAGIC3       'F'

#define FLASH_LIMIT_BYTES (512 * 1024)   /* 512 КБ Flash */
#define RAM_LIMIT_BYTES   (128 * 1024)   /* 128 КБ RAM   */

typedef struct {
    uint8_t  e_ident[16];
    uint16_t e_type;
    uint16_t e_machine;
    uint32_t e_version;
    uint32_t e_entry;
    uint32_t e_phoff;
    uint32_t e_shoff;
    uint32_t e_flags;
    uint16_t e_ehsize;
    uint16_t e_phentsize;
    uint16_t e_phnum;
    uint16_t e_shentsize;
    uint16_t e_shnum;
    uint16_t e_shstrndx;
} Elf32_Header;

typedef struct {
    uint32_t sh_name;
    uint32_t sh_type;
    uint32_t sh_flags;
    uint32_t sh_addr;
    uint32_t sh_offset;
    uint32_t sh_size;
    uint32_t sh_link;
    uint32_t sh_info;
    uint32_t sh_addralign;
    uint32_t sh_entsize;
} Elf32_SectionHeader;

static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_образу.elf>\n", argv[0]);
        return 2;
    }

    const char *filepath = argv[1];
    FILE *f = fopen(filepath, "rb");
    if (!f) {
        fprintf(stderr, "ПОМИЛКА: Неможливо відкрити файл '%s'\n", filepath);
        return 1;
    }

    Elf32_Header header;
    if (fread(&header, sizeof(Elf32_Header), 1, f) != 1) {
        fprintf(stderr, "ПОМИЛКА: Не вдалося прочитати заголовок ELF\n");
        fclose(f);
        return 1;
    }

    if (header.e_ident[0] != ELF_MAGIC0 || header.e_ident[1] != ELF_MAGIC1 ||
        header.e_ident[2] != ELF_MAGIC2 || header.e_ident[3] != ELF_MAGIC3) {
        fprintf(stderr, "ВІДХИЛЕНО: Файл не є коректним ELF-артефактом\n");
        fclose(f);
        return 1;
    }

    if (fseek(f, header.e_shoff, SEEK_SET) != 0) {
        fprintf(stderr, "ПОМИЛКА: Не вдалося перейти до таблиці секцій\n");
        fclose(f);
        return 1;
    }

    Elf32_SectionHeader *sh_table = malloc(sizeof(Elf32_SectionHeader) * header.e_shnum);
    if (!sh_table) {
        fprintf(stderr, "ПОМИЛКА: Брак пам'яті для таблиці секцій\n");
        fclose(f);
        return 1;
    }

    if (fread(sh_table, sizeof(Elf32_SectionHeader), header.e_shnum, f) != header.e_shnum) {
        fprintf(stderr, "ПОМИЛКА: Не вдалося прочитати секції ELF\n");
        free(sh_table);
        fclose(f);
        return 1;
    }

    /* Читання таблиці імен секцій */
    Elf32_SectionHeader *str_sh = &sh_table[header.e_shstrndx];
    char *sh_names = malloc(str_sh->sh_size);
    if (!sh_names) {
        free(sh_table);
        fclose(f);
        return 1;
    }

    fseek(f, str_sh->sh_offset, SEEK_SET);
    if (fread(sh_names, 1, str_sh->sh_size, f) != str_sh->sh_size) {
        fprintf(stderr, "ПОМИЛКА: Помилка читання імен секцій\n");
        free(sh_names);
        free(sh_table);
        fclose(f);
        return 1;
    }

    uint32_t flash_used = 0;
    uint32_t ram_used = 0;
    bool has_dirty_metadata = false;

    for (int i = 0; i < header.e_shnum; ++i) {
        const char *name = &sh_names[sh_table[i].sh_name];
        uint32_t size = sh_table[i].sh_size;

        if (strcmp(name, ".text") == 0 || strcmp(name, ".rodata") == 0) {
            flash_used += size;
        } else if (strcmp(name, ".data") == 0) {
            flash_used += size;
            ram_used += size;
        } else if (strcmp(name, ".bss") == 0) {
            ram_used += size;
        }

        /* Перевірка наявності dirty-рядка у секції rodata */
        if (strcmp(name, ".rodata") == 0 && size > 0) {
            uint8_t *rodata_buf = malloc(size);
            if (rodata_buf) {
                fseek(f, sh_table[i].sh_offset, SEEK_SET);
                if (fread(rodata_buf, 1, size, f) == size) {
                    for (size_t k = 0; k + 6 <= size; ++k) {
                        if (memcmp(&rodata_buf[k], "-dirty", 6) == 0) {
                            has_dirty_metadata = true;
                            break;
                        }
                    }
                }
                free(rodata_buf);
            }
        }
    }

    free(sh_names);
    free(sh_table);

    /* Розрахунок CRC32 всього файлу */
    fseek(f, 0, SEEK_END);
    long file_size = ftell(f);
    fseek(f, 0, SEEK_SET);

    uint8_t *full_file = malloc(file_size);
    if (!full_file) {
        fclose(f);
        return 1;
    }
    fread(full_file, 1, file_size, f);
    fclose(f);

    uint32_t image_crc = calculate_crc32(full_file, file_size);
    free(full_file);

    printf("=== ЗВІТ РЕЛІЗНОГО АРТЕФАКТУ: %s ===\n", filepath);
    printf("  Flash: %u / %u байтів (%.1f%%)\n", flash_used, FLASH_LIMIT_BYTES, (float)flash_used * 100.0f / FLASH_LIMIT_BYTES);
    printf("  RAM:   %u / %u байтів (%.1f%%)\n", ram_used, RAM_LIMIT_BYTES, (float)ram_used * 100.0f / RAM_LIMIT_BYTES);
    printf("  CRC32: 0x%08X\n", image_crc);

    if (has_dirty_metadata) {
        fprintf(stderr, "ВІДХИЛЕНО: Знайдено мітку '-dirty'! Образ зібрано з незакоміченими змінами.\n");
        return 1;
    }

    if (flash_used > FLASH_LIMIT_BYTES) {
        fprintf(stderr, "ВІДХИЛЕНО: Перевищено бюджет Flash на %u байтів!\n", flash_used - FLASH_LIMIT_BYTES);
        return 1;
    }

    if (ram_used > RAM_LIMIT_BYTES) {
        fprintf(stderr, "ВІДХИЛЕНО: Перевищено бюджет RAM на %u байтів!\n", ram_used - RAM_LIMIT_BYTES);
        return 1;
    }

    printf("РЕЗУЛЬТАТ: Образ валідний, чистий та придатний до випуску.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <string>
#include <span>
#include <cstdint>
#include <expected>
#include <algorithm>

constexpr uint8_t ELF_MAGIC0 = 0x7F;
constexpr uint8_t ELF_MAGIC1 = 'E';
constexpr uint8_t ELF_MAGIC2 = 'L';
constexpr uint8_t ELF_MAGIC3 = 'F';

constexpr uint32_t FLASH_LIMIT_BYTES = 512 * 1024;
constexpr uint32_t RAM_LIMIT_BYTES   = 128 * 1024;

#pragma pack(push, 1)
struct Elf32_Header {
    uint8_t  e_ident[16];
    uint16_t e_type;
    uint16_t e_machine;
    uint32_t e_version;
    uint32_t e_entry;
    uint32_t e_phoff;
    uint32_t e_shoff;
    uint32_t e_flags;
    uint16_t e_ehsize;
    uint16_t e_phentsize;
    uint16_t e_phnum;
    uint16_t e_shentsize;
    uint16_t e_shnum;
    uint16_t e_shstrndx;
};

struct Elf32_SectionHeader {
    uint32_t sh_name;
    uint32_t sh_type;
    uint32_t sh_flags;
    uint32_t sh_addr;
    uint32_t sh_offset;
    uint32_t sh_size;
    uint32_t sh_link;
    uint32_t sh_info;
    uint32_t sh_addralign;
    uint32_t sh_entsize;
};
#pragma pack(pop)

struct ArtifactStats {
    uint32_t flash_used{0};
    uint32_t ram_used{0};
    uint32_t crc32{0};
    bool is_dirty{false};
};

[[nodiscard]] constexpr uint32_t compute_crc32(std::span<const uint8_t> data) noexcept {
    uint32_t crc = 0xFFFFFFFF;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(crc & 1)));
        }
    }
    return ~crc;
}

[[nodiscard]] std::expected<ArtifactStats, std::string> inspect_elf(std::span<const uint8_t> file_bytes) {
    if (file_bytes.size() < sizeof(Elf32_Header)) {
        return std::unexpected("Файл занадто малий для заголовка ELF");
    }

    const auto& header = *reinterpret_cast<const Elf32_Header*>(file_bytes.data());
    if (header.e_ident[0] != ELF_MAGIC0 || header.e_ident[1] != ELF_MAGIC1 ||
        header.e_ident[2] != ELF_MAGIC2 || header.e_ident[3] != ELF_MAGIC3) {
        return std::unexpected("Некоректний ELF-магічний підпис");
    }

    if (header.e_shoff + header.e_shnum * sizeof(Elf32_SectionHeader) > file_bytes.size()) {
        return std::unexpected("Таблиця секцій виходить за межі файлу");
    }

    const auto* sh_table = reinterpret_cast<const Elf32_SectionHeader*>(file_bytes.data() + header.e_shoff);
    if (header.e_shstrndx >= header.e_shnum) {
        return std::unexpected("Некоректний індекс таблиці імен секцій");
    }

    const auto& str_sh = sh_table[header.e_shstrndx];
    if (str_sh.sh_offset + str_sh.sh_size > file_bytes.size()) {
        return std::unexpected("Таблиця імен секцій виходить за межі файлу");
    }

    const char* sh_names = reinterpret_cast<const char*>(file_bytes.data() + str_sh.sh_offset);

    ArtifactStats stats{};
    stats.crc32 = compute_crc32(file_bytes);

    for (size_t i = 0; i < header.e_shnum; ++i) {
        const auto& sh = sh_table[i];
        if (sh.sh_name >= str_sh.sh_size) continue;
        
        std::string_view name(sh_names + sh.sh_name);
        uint32_t size = sh.sh_size;

        if (name == ".text" || name == ".rodata") {
            stats.flash_used += size;
        } else if (name == ".data") {
            stats.flash_used += size;
            stats.ram_used += size;
        } else if (name == ".bss") {
            stats.ram_used += size;
        }

        if (name == ".rodata" && sh.sh_offset + size <= file_bytes.size()) {
            std::string_view rodata(reinterpret_cast<const char*>(file_bytes.data() + sh.sh_offset), size);
            if (rodata.find("-dirty") != std::string_view::npos) {
                stats.is_dirty = true;
            }
        }
    }

    return stats;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_образу.elf>\n";
        return 2;
    }

    std::ifstream file(argv[1], std::ios::binary | std::ios::ate);
    if (!file) {
        std::cerr << "ПОМИЛКА: Неможливо відкрити файл '" << argv[1] << "'\n";
        return 1;
    }

    const auto file_size = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<uint8_t> buffer(file_size);
    if (!file.read(reinterpret_cast<char*>(buffer.data()), file_size)) {
        std::cerr << "ПОМИЛКА: Не вдалося прочитати вміст файлу\n";
        return 1;
    }

    auto result = inspect_elf(buffer);
    if (!result) {
        std::cerr << "ВІДХИЛЕНО: " << result.error() << "\n";
        return 1;
    }

    const auto& stats = *result;
    std::cout << "=== ЗВІТ РЕЛІЗНОГО АРТЕФАКТУ: " << argv[1] << " ===\n";
    std::cout << "  Flash: " << stats.flash_used << " / " << FLASH_LIMIT_BYTES << " байтів\n";
    std::cout << "  RAM:   " << stats.ram_used << " / " << RAM_LIMIT_BYTES << " байтів\n";
    std::cout << "  CRC32: 0x" << std::hex << stats.crc32 << std::dec << "\n";

    if (stats.is_dirty) {
        std::cerr << "ВІДХИЛЕНО: Знайдено мітку '-dirty'! Образ містить незакомічені зміни.\n";
        return 1;
    }

    if (stats.flash_used > FLASH_LIMIT_BYTES || stats.ram_used > RAM_LIMIT_BYTES) {
        std::cerr << "ВІДХИЛЕНО: Пробито апаратний бюджет пам'яті!\n";
        return 1;
    }

    std::cout << "РЕЗУЛЬТАТ: Образ верифіковано успішно.\n";
    return 0;
}
```
:::

## Детальний розбір реалізації та відмінностей між мовами

Обидва варіанти утиліти вирішують одну інженерну задачу, але демонструють принципову різницю в підходах до управління пам'яттю та безпеки.

У варіанті на мові C ми працюємо з ручним виділенням динамічної пам'яті через `malloc` і `free`, а також із низькорівневим файловим вводом-виводом через покажчики `FILE*`. Заголовок ELF та таблиця секцій зчитуються послідовно через зміщення покажчика файлу `fseek()`. Кожне виділення буфера під рядки секцій або таблиці вимагає обов'язкової ручної перевірки на `NULL` та звільнення пам'яті перед кожною точкою виходу з функції, щоб уникнути витоків ресурсів.

У варіанті на C++20 архітектура побудована на безпечних сучасних концепціях:
- **Управління ресурсами за принципом RAII:** використання `std::vector<uint8_t>` повністю усуває ручне звільнення пам'яті, гарантуючи деалокацію буфера навіть у разі виникнення помилок під час розбору структури.
- **Незмінні зрізи пам'яті без копіювання (`std::span` та `std::string_view`):** функція `inspect_elf` приймає `std::span<const uint8_t>`, що дозволяє безпечно зазирати у структури ELF без створення проміжних копій у купі. Пошук текстових міток (наприклад, перевірка рядка `"-dirty"`) виконується методом `std::string_view::find`, що працює за константний час без завершального нульового байта `\0`.
- **Типізована обробка помилок через `std::expected`:** замість повернення магічних числових кодів помилок або винятків функція повертає об'єкт `std::expected<ArtifactStats, std::string>`, який змушує викликача явно перевірити успішність операції перед доступом до полів статистики.

## Інтеграція у релізний конвеєр CMake та Makefile

Щоб утиліта виконувала роль автоматичних воріт, її додають у фінальний крок формування прошивки. У `CMakeLists.txt` це реалізується через команду користувацької пост-обробки (англ. *custom command*):

```cmake
# Додавання верифікації після завершення лінкування
add_custom_command(TARGET ${PROJECT_NAME}.elf POST_BUILD
    COMMAND release_verifier ${CMAKE_BINARY_DIR}/${PROJECT_NAME}.elf
    COMMENT "Верифікація бюджетів пам'яті та чистоти артефакту перед випуском"
    VERBATIM
)
```

Якщо верифікатор знаходить перевищення ліміту Flash хоча б на один байт або виявляє, що прошивка зібрана з незакоміченими файлами, збірка обривається з помилкою лінкування, не дозволяючи згенерувати фінальний файл `.bin`.

## Пастки та крайові випадки верифікації

Під час вбудовування валідатора в реальний конвеєр звертайте увагу на такі системні нюанси:
1. **Вирівнювання секцій (Alignment Padding):** Компонувальник лінкера вирівнює секції пам'яті за межею 4, 8 або 16 байтів відповідно до вимог шини мікроконтролера. Через це арифметична сума розмірів секцій у заголовках ELF може бути на кілька десятків байтів меншою за розмір реального бінарного файлу на диску.
2. **Сегменти завантаження проти секцій:** ELF-файл містить два різні погляди на структуру пам'яті: секції (для компонувальника) та сегменти завантаження (англ. *Program Headers, Phdr* з типом `PT_LOAD`). Деякі мікроконтролерні проєкти використовують складні лінкер-скрипти, де секція коду розміщується у Flash, але в процесі старту копіюється у внутрішню швидку пам'ять процесора (наприклад, `ITCM RAM`). Такі секції повинні одночасно враховуватися і у бюджеті Flash, і у бюджеті RAM.
3. **Налагоджувальні секції DWARF:** Секції `.debug_info`, `.debug_line`, `.debug_frame` та `.comment` містять налагоджувальну інформацію для відлагоджувача GDB. Вони присутні у файлі `.elf`, але мають знятий прапорець завантаження `SHF_ALLOC` і не потрапляють у фізичну пам'ять мікроконтролера. Верифікатор повинен аналізувати прапорці секцій і не додавати розмір налагоджувальних таблиць до фізичного обсягу коду.
