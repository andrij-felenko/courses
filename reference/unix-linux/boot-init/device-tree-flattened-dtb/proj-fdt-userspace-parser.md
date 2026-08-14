# ⚙️ Парсер бінарного DTB у користувацькому просторі

Цей проєкт демонструє практичну реалізацію автономного парсера файлів бінарного дерева пристроїв (`.dtb`) у користувацькому просторі без використання зовнішніх сторонніх бібліотек (таких як `libfdt`). Програма перевіряє сигнатуру заголовка `0xd00dfeed`, конвертує значення з порядку байтів Big-Endian у хостовий порядок процессора, валідує межі буфера пам'яті та ітеративно обходить токени блоку структур для відтворення та виведення ієрархії вузлів і властивостей.

## 1. Постановка задачі та апаратний контекст

Під час розробки системного ПЗ низького рівня (наприклад, власних первинних завантажувачів, мікроядерних систем, гіпервізорів або діагностичних утилит для розгортання образів у Linux) часто виникає потреба прочитати бінарний DTB файл безпосередньо з диска або з адреси у фізичній пам'яті.

Формат FDT зберігає всі 32-бітні цілі числа в порядку **Big-Endian**. Тож парсер повинен виконувати конвертацію байтів через `be32toh()` у мові C або через регульований байт-свап у мові C++ для коректного обчислення розмірів і зсувів у пам'яті.

Окрім того, сирий бінарний файл DTB містить три незалежні блоки:
1. Заголовок `struct fdt_header`.
2. Блок структур `dt_struct`, у якому вузли та властивості записані послідовними тегами `FDT_BEGIN_NODE`, `FDT_PROP`, `FDT_END_NODE`.
3. Блок рядків `dt_strings`, де містяться назви всіх властивостей.

Парсер повинен зчитувати тег `FDT_PROP`, витягувати зсув `nameoff`, знаходити рядок за цією адресою у блоці рядків, а потім пропускати `len` байтів даних властивості з обов'язковим урахуванням 4-байтового вирівнювання (`alignment`).

## 2. Архітектура та математика вирівнювання даних у FDT

Усі елементи блоку структур FDT вирівнюються за межею **4 байти** (32 біти). Якщо рядок назви вузла або бінарні дані властивості мають довжину, не кратну 4 байтам, компілятор `dtc` додає в бінарний потік нульові падінг-байти (`\0`).

Математично обчислення вирівняного розміру у байтах виконується за формулою:

```
aligned_len = (len + 3) & ~3U;
```

Для просування вказівника `uint32_t *pstruct` по 32-бітних словах буфера вирівняний розмір ділиться на 4:

```
words_to_skip = aligned_len / 4;
pstruct += words_to_skip;
```

Якщо не враховувати вирівнювання, вказівник зсунеться на непарну кількість байтів, що призведе до зчитування сміття замість наступного токена, а на архітектурах із суворим контролем вирівнювання (таких як старі ядра ARMv5 або MIPS) викликає апаратне виключення `alignment fault`.

## 3. Реалізація парсера мовами C та C++

Нижче наведено робочий приклад реалізації парсера двома мовами у вигляді роздільних вкладок.

Приклад для мови **C** спирається на функціональний підхід, низькорівневе приведення вказівників, явне виділення пам'яті викликами `malloc()` / `free()` та обробку бінарних даних за допомогою системної функції `be32toh()`.

Приклад для мови **C++** показує ідіоматичний сучасний підхід: використання RAII для керування файлами та буферами, безпечне обертання буфера у контейнер `std::vector<uint8_t>`, застосування `std::string_view` для уникнення зайвого копіювання рядків, тип `std::expected` (C++23) для строгої обробки помилок без винятків та `std::byteswap` для конвертації endianness.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <endian.h>

#define FDT_MAGIC       0xd00dfeed
#define FDT_BEGIN_NODE  0x00000001
#define FDT_END_NODE    0x00000002
#define FDT_PROP        0x00000003
#define FDT_NOP         0x00000004
#define FDT_END         0x00000009

struct fdt_header {
    uint32_t magic;
    uint32_t totalsize;
    uint32_t off_dt_struct;
    uint32_t off_dt_strings;
    uint32_t off_mem_rsvmap;
    uint32_t version;
    uint32_t last_comp_version;
    uint32_t boot_cpuid_phys;
    uint32_t size_dt_strings;
    uint32_t size_dt_struct;
};

static uint32_t align4(uint32_t val) {
    return (val + 3) & ~3U;
}

static void print_indent(int depth) {
    for (int i = 0; i < depth; ++i) {
        printf("  ");
    }
}

static int parse_fdt_buffer(const uint8_t *buf, size_t buf_size) {
    if (buf_size < sizeof(struct fdt_header)) {
        fprintf(stderr, "Помилка: буфер занадто малий для заголовка\n");
        return -1;
    }

    const struct fdt_header *hdr = (const struct fdt_header *)buf;
    uint32_t magic = be32toh(hdr->magic);
    if (magic != FDT_MAGIC) {
        fprintf(stderr, "Помилка: некоректне сигнатурне число 0x%x (очікувалося 0x%x)\n",
                magic, FDT_MAGIC);
        return -1;
    }

    uint32_t totalsize = be32toh(hdr->totalsize);
    uint32_t off_struct = be32toh(hdr->off_dt_struct);
    uint32_t off_strings = be32toh(hdr->off_dt_strings);

    printf("FDT Header: totalsize=%u, struct_offset=%u, strings_offset=%u\n",
           totalsize, off_struct, off_strings);

    const uint32_t *pstruct = (const uint32_t *)(buf + off_struct);
    const char *pstrings = (const char *)(buf + off_strings);

    int depth = 0;
    int running = 1;

    while (running) {
        uint32_t tag = be32toh(*pstruct++);

        switch (tag) {
        case FDT_BEGIN_NODE: {
            const char *name = (const char *)pstruct;
            if (*name == '\0') {
                name = "/";
            }
            print_indent(depth);
            printf("Node: %s {\n", name);
            depth++;

            size_t name_len = strlen((const char *)pstruct) + 1;
            pstruct += align4(name_len) / 4;
            break;
        }
        case FDT_END_NODE:
            depth--;
            print_indent(depth);
            printf("};\n");
            break;

        case FDT_PROP: {
            uint32_t len = be32toh(*pstruct++);
            uint32_t nameoff = be32toh(*pstruct++);
            const char *prop_name = pstrings + nameoff;

            print_indent(depth);
            printf("Property '%s' (len=%u)\n", prop_name, len);

            pstruct += align4(len) / 4;
            break;
        }
        case FDT_NOP:
            break;

        case FDT_END:
            running = 0;
            break;

        default:
            fprintf(stderr, "Помилка: невідомий токен 0x%08x\n", tag);
            return -1;
        }
    }

    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Використання: %s <file.dtb>\n", argv[0]);
        return 1;
    }

    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        perror("Не вдалося відкрити файл");
        return 1;
    }

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);

    uint8_t *buf = (uint8_t *)malloc(size);
    if (!buf) {
        fclose(f);
        return 1;
    }

    if (fread(buf, 1, size, f) != (size_t)size) {
        perror("Помилка читання файлу");
        free(buf);
        fclose(f);
        return 1;
    }
    fclose(f);

    int res = parse_fdt_buffer(buf, size);

    free(buf);
    return res;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <cstdint>
#include <bit>
#include <expected>
#include <stdexcept>

namespace fdt {

constexpr uint32_t FDT_MAGIC      = 0xd00dfeed;
constexpr uint32_t FDT_BEGIN_NODE = 0x00000001;
constexpr uint32_t FDT_END_NODE   = 0x00000002;
constexpr uint32_t FDT_PROP       = 0x00000003;
constexpr uint32_t FDT_NOP        = 0x00000004;
constexpr uint32_t FDT_END        = 0x00000009;

struct Header {
    uint32_t magic;
    uint32_t totalsize;
    uint32_t off_dt_struct;
    uint32_t off_dt_strings;
    uint32_t off_mem_rsvmap;
    uint32_t version;
    uint32_t last_comp_version;
    uint32_t boot_cpuid_phys;
    uint32_t size_dt_strings;
    uint32_t size_dt_struct;
};

// Конвертація з Big-Endian у хостовий порядок байтів
constexpr uint32_t from_be32(uint32_t val) noexcept {
    if constexpr (std::endian::native == std::endian::little) {
        return std::byteswap(val);
    }
    return val;
}

class Parser {
public:
    explicit Parser(std::vector<uint8_t> buffer) : data_(std::move(buffer)) {}

    std::expected<void, std::string> parse() {
        if (data_.size() < sizeof(Header)) {
            return std::unexpected("Буфер занадто малий для заголовка FDT");
        }

        const auto* hdr = reinterpret_cast<const Header*>(data_.data());
        if (from_be32(hdr->magic) != FDT_MAGIC) {
            return std::unexpected("Некоректна сигнатура FDT Header");
        }

        const uint32_t off_struct = from_be32(hdr->off_dt_struct);
        const uint32_t off_strings = from_be32(hdr->off_dt_strings);

        if (off_struct >= data_.size() || off_strings >= data_.size()) {
            return std::unexpected("Зсуви заголовка виходять за межі файлу");
        }

        const auto* pstruct = reinterpret_cast<const uint32_t*>(data_.data() + off_struct);
        const char* pstrings = reinterpret_cast<const char*>(data_.data() + off_strings);

        std::size_t depth = 0;
        bool running = true;

        while (running) {
            uint32_t tag = from_be32(*pstruct++);

            switch (tag) {
            case FDT_BEGIN_NODE: {
                std::string_view name(reinterpret_cast<const char*>(pstruct));
                if (name.empty()) {
                    name = "/";
                }
                print_indent(depth);
                std::cout << "Node: " << name << " {\n";
                depth++;

                std::size_t name_bytes = name.size() + 1;
                std::size_t padded = (name_bytes + 3) & ~3U;
                pstruct += padded / 4;
                break;
            }
            case FDT_END_NODE:
                if (depth > 0) depth--;
                print_indent(depth);
                std::cout << "};\n";
                break;

            case FDT_PROP: {
                uint32_t len = from_be32(*pstruct++);
                uint32_t nameoff = from_be32(*pstruct++);
                std::string_view prop_name(pstrings + nameoff);

                print_indent(depth);
                std::cout << "Property '" << prop_name << "' (len=" << len << ")\n";

                std::size_t padded = (len + 3) & ~3U;
                pstruct += padded / 4;
                break;
            }
            case FDT_NOP:
                break;

            case FDT_END:
                running = false;
                break;

            default:
                return std::unexpected("Знайдено невідомий токен у блоці структур");
            }
        }

        return {};
    }

private:
    static void print_indent(std::size_t depth) {
        for (std::size_t i = 0; i < depth; ++i) {
            std::cout << "  ";
        }
    }

    std::vector<uint8_t> data_;
};

} // namespace fdt

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <file.dtb>\n";
        return 1;
    }

    std::ifstream file(argv[1], std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        std::cerr << "Не вдалося відкрити DTB файл\n";
        return 1;
    }

    const auto size = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<uint8_t> buffer(size);
    if (!file.read(reinterpret_cast<char*>(buffer.data()), size)) {
        std::cerr << "Помилка читання даних\n";
        return 1;
    }

    fdt::Parser parser(std::move(buffer));
    if (auto result = parser.parse(); !result) {
        std::cerr << "Помилка парсингу: " << result.error() << '\n';
        return 1;
    }

    return 0;
}
```
:::

## 4. Аналіз алгоритму та обробка крайових випадків

Під час обробки бінарного файлу DTB парсер виконує такі ключові кроки:

1. **Валідація сигнатури (Magic Check):** Першим кроком зчитуються 4 байти і порівнюються з константою `0xd00dfeed`. Це захищає програму від спроби розпарсити довільний бінарний файл або пошкоджений образ пам'яті.
2. **Перевірка меж буфера (Bounds Checking):** Зсуви `off_dt_struct` та `off_dt_strings` зчитуються з заголовка та звіряються із загальним розміром завантаженого буфера. Якщо зсув перевищує розмір буфера, реалізація на C++ повертає `std::unexpected`, запобігаючи виходу за межі виділеної пам'яті (`out-of-bounds read`).
3. **Ітеративний стек вкладеності (Depth Tracking):** Замість використання рекурсивних викликів функцій (які можуть призвести до переповнення стеку викликів `stack overflow` при глибокому дереві вузлів), парсер використовує ітеративний цикл `while`. Змінна `depth` відстежує поточну глибину вкладеності: `FDT_BEGIN_NODE` збільшує її на 1, а `FDT_END_NODE` зменшує на 1.
4. **Витяг назв властивостей із блоку рядків:** Токен `FDT_PROP` містить 32-бітне число `nameoff`. Парсер додає це значення до адреси початку блоку рядків `pstrings + nameoff`. Оскільки блок `dt_strings` містить звичайні null-терміновані ASCII-рядки, створення `std::string_view(pstrings + nameoff)` у C++ виконується без жодного виділення пам'яті у купі (`zero-allocation`).

## 5. Обробка динамічних оверлеїв (.dtbo) та рехендлінг phandle

У складніших системах бінарний файл DTB може містити додаткові спеціалізовані вузли верхнього рівня:
- `__symbols__`: Містить текстову таблицю відповідностей між символьними мітками сирцевого `.dts` файлу та їхніми згенерованими числовими значеннями `phandle` у DTB.
- `__fixups__`: Описує місця у виразах властивостей оверлея, де чисельні значення `phandle` повинні бути замінені на нові адреси після підключення до основного дерева в ядрі.
- `__local_fixups__`: Вказує внутрішні локальні перехресні посилання всередині самого оверлея.

При написанні розширеного парсера оверлеїв алгоритм спочатку зчитує вузол `__symbols__` базового дерева, зберігає карту `std::unordered_map<std::string, uint32_t>`, а потім при застосуванні `.dtbo` файлу патчить відповідні комірки пам'яті у блоці `dt_struct` перед його остаточним розгортанням.

## 6. Компіляція, запуск та практичне використання

Для перевірки роботи програми в реальній системі Linux можна використати згенерований ядром DTB або витягнути його з файлової системи `/sys/firmware/fdt` (якщо включена конфігурація ядра `CONFIG_PROC_DEVICETREE` або `CONFIG_OF_KOBJ`):

```bash
# Компіляція прикладу мовою C
gcc -O2 -Wall -Wextra proj-fdt-parser.c -o fdt_parser_c

# Компіляція прикладу мовою C++ (вимагає C++23 для std::byteswap та std::expected)
g++ -std=c++23 -O2 -Wall -Wextra proj-fdt-parser.cpp -o fdt_parser_cpp

# Запуск на бінарному блобі ядра Linux
./fdt_parser_cpp /sys/firmware/fdt
```

Програма виведе повне дерево вузлів і назви властивостей, аналогічно до роботи системного компілятора `dtc -I dtb -O dts`.

### 6.1. Практичні пастки розробки у користувацькому просторі

1. **Невирівняні читання `uint32_t`:** На деяких вбудованих платформах прямий розіменування вказівника `const uint32_t *pstruct` за некратними 4 адресами викликає аварійне завершення процесу `SIGBUS`. Рекомендовано або виконувати вирівнювання через `align4()`, або копіювати байти через `memcpy()`.
2. **Пошкоджені рядки без нуль-термінатора:** Якщо файл `.dtb` пошкоджено, рядок у блоці рядків або назва вузла може не містити нульового байта `\0`. Для безпечного парсингу у промисловому коді додають додаткову перевірку, що довжина прочитаного рядка не виходить за межі секції `size_dt_strings`.
