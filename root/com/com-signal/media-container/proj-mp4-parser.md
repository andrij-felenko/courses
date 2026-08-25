# ⚙️ Парсинг атомарної структури ISOBMFF / MP4 на C та C++

Медіаконтейнер ISOBMFF (MP4) будується як ієрархічне дерево вкладених двоїнкових блоків — боксів (атомів). Кожен бокс починається з фіксованого 8-байтового заголовка: 4 байти розрядності розміру (Big-Endian `uint32_t`) та 4 байти текстового тегу типу FourCC.

Для розробки власних демультиплексорів, медіааналізаторів або утиліт швидкого перегляду метаданих необхідний легкий алгоритм розбору боксів. Програмістська задача полягає в тому, щоб реалізувати безпечний парсер бінарного потоку, який рекурсивно проходить дерево атомів (`ftyp`, `moov`, `trak`, `mdia`, `minf`, `stbl`), витягує ідентифікатори боксів, перевіряє межі пам'яті та обчислює їхні точні розміри й байтові зсуви у файлі.

## Архітектура двійкового розбору боксів ISOBMFF

Процес розбору файлу MP4 базується на послідовному зчитуванні заголовків боксів із пам'яті або файлового потоку. Згідно зі стандартом ISO/IEC 14496-12, заголовок боксу має таку базову структуру:

1. **`size` (4 байти, Big-Endian):** Загальний розмір боксу у байтах, включаючи 8 байтів самого заголовка. Якщо `size == 1`, це означає, що реальний розмір є 64-бітним цілим числом і записаний у наступному 8-байтовому полі `largesize`. Якщо `size == 0`, бокс тягнеться до самого кінця файлу.
2. **`type` (4 байти, ASCII):** Чотирибуквений кодовий ідентифікатор FourCC (наприклад `ftyp`, `moov`, `mdat`).

Бокси поділяються на два класи:
- **Листові бокси (Leaf Boxes):** Містять безпосередні метадані або медіабайти (`ftyp`, `mvhd`, `stsz`, `mdat`). Парсер зчитує їхній вміст або просто пропускає його, зміщуючи покажчик на `size` байтів.
- **Контейнерні бокси (Container / Parent Boxes):** Містять усередині свого корисного навантаження інші вкладені бокси (`moov`, `trak`, `mdia`, `minf`, `stbl`). Парсер розпізнає такі бокси за їхнім FourCC-тегом і рекурсивно запускає обробку внутрішнього блоку даних зі зсувом `offset + 8`.

## Програмістська реалізація на C та C++

Нижче наведено дві повноцінні ідіоматичні реалізації парсера боксів MP4: перша мовою C з використанням класичних покажчиків та перевірки меж буфера, а друга мовою C++ з використанням сучасних концепцій C++20 (`std::span`, `std::string_view`, RAII та векторизація даних).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// Читання 32-бітного цілого числа з формати Big-Endian у Little-Endian
static uint32_t read_uint32_be(const uint8_t *buf) {
    return ((uint32_t)buf[0] << 24) |
           ((uint32_t)buf[1] << 16) |
           ((uint32_t)buf[2] << 8)  |
            (uint32_t)buf[3];
}

// Перевірка, чи є бокс контейнером для вкладених боксів
static int is_container_box(const char *type) {
    return (strcmp(type, "moov") == 0 ||
            strcmp(type, "trak") == 0 ||
            strcmp(type, "mdia") == 0 ||
            strcmp(type, "minf") == 0 ||
            strcmp(type, "stbl") == 0);
}

// Рекурсивний розбір боксів у пам'яті
static void parse_mp4_boxes(const uint8_t *buffer, size_t offset, size_t max_offset, int depth) {
    while (offset + 8 <= max_offset) {
        uint32_t box_size = read_uint32_be(buffer + offset);
        char type_str[5] = {0};
        memcpy(type_str, buffer + offset + 4, 4);

        if (box_size == 0) {
            // Розмір 0 означає, що бокс тягнеться до кінця файлу
            box_size = (uint32_t)(max_offset - offset);
        } else if (box_size < 8) {
            // Некоректна довжина заголовка боксу
            break;
        }

        if (offset + box_size > max_offset) {
            printf("Помилка: бокс %s виходить за межі буфера\n", type_str);
            break;
        }

        // Вивід відступів для візуалізації дерева
        for (int i = 0; i < depth; i++) {
            printf("  ");
        }
        printf("Box: [%s] Size: %u, Offset: %zu\n", type_str, box_size, offset);

        // Якщо це контейнерний бокс, заходимо всередину його тіла
        if (is_container_box(type_str)) {
            parse_mp4_boxes(buffer, offset + 8, offset + box_size, depth + 1);
        }

        offset += box_size;
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Використання: %s <шлях_до_файлу.mp4>\n", argv[0]);
        return 1;
    }

    FILE *file = fopen(argv[1], "rb");
    if (!file) {
        perror("Не вдалося відкрити файл");
        return 1;
    }

    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);

    if (file_size < 8) {
        printf("Занадто малий файл MP4\n");
        fclose(file);
        return 1;
    }

    uint8_t *buffer = (uint8_t *)malloc(file_size);
    if (!buffer) {
        printf("Помилка виділення пам'яті\n");
        fclose(file);
        return 1;
    }

    if (fread(buffer, 1, file_size, file) != (size_t)file_size) {
        printf("Помилка зчитання файлу\n");
        free(buffer);
        fclose(file);
        return 1;
    }
    fclose(file);

    printf("=== Дерево боксів ISOBMFF / MP4 ===\n");
    parse_mp4_boxes(buffer, 0, (size_t)file_size, 0);

    free(buffer);
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string_view>
#include <span>
#include <cstdint>
#include <array>

// RAII-клас для безпечного парсингу MP4-файлів у стилі C++20
class Mp4BoxParser {
public:
    struct BoxInfo {
        std::string type;
        uint32_t size;
        size_t offset;
        int depth;
    };

    static std::uint32_t readUint32BE(std::span<const std::uint8_t> data, size_t offset) {
        return (static_cast<std::uint32_t>(data[offset]) << 24) |
               (static_cast<std::uint32_t>(data[offset + 1]) << 16) |
               (static_cast<std::uint32_t>(data[offset + 2]) << 8)  |
                static_cast<std::uint32_t>(data[offset + 3]);
    }

    static bool isContainer(std::string_view type) {
        static constexpr std::array<std::string_view, 5> containers = {
            "moov", "trak", "mdia", "minf", "stbl"
        };
        for (const auto& c : containers) {
            if (c == type) return true;
        }
        return false;
    }

    explicit Mp4BoxParser(std::vector<std::uint8_t> buffer) 
        : buffer_(std::move(buffer)) {}

    std::vector<BoxInfo> parse() const {
        std::vector<BoxInfo> result;
        parseRecursive(std::span<const std::uint8_t>(buffer_), 0, buffer_.size(), 0, result);
        return result;
    }

private:
    std::vector<std::uint8_t> buffer_;

    void parseRecursive(std::span<const std::uint8_t> data, 
                        size_t offset, 
                        size_t maxOffset, 
                        int depth, 
                        std::vector<BoxInfo>& outBoxes) const {
        while (offset + 8 <= maxOffset) {
            uint32_t boxSize = readUint32BE(data, offset);
            std::string typeStr(reinterpret_cast<const char*>(data.data() + offset + 4), 4);

            if (boxSize == 0) {
                boxSize = static_cast<uint32_t>(maxOffset - offset);
            } else if (boxSize < 8) {
                break;
            }

            if (offset + boxSize > maxOffset) {
                break;
            }

            outBoxes.push_back({typeStr, boxSize, offset, depth});

            if (isContainer(typeStr)) {
                parseRecursive(data, offset + 8, offset + boxSize, depth + 1, outBoxes);
            }

            offset += boxSize;
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <файл.mp4>\n";
        return 1;
    }

    std::ifstream file(argv[1], std::ios::binary | std::ios::ate);
    if (!file) {
        std::cerr << "Помилка відкриття файлу: " << argv[1] << "\n";
        return 1;
    }

    const auto fileSize = file.tellg();
    file.seekg(0, std::ios::beg);

    std::vector<std::uint8_t> buffer(fileSize);
    if (!file.read(reinterpret_cast<char*>(buffer.data()), fileSize)) {
        std::cerr << "Помилка зчитання даних\n";
        return 1;
    }

    Mp4BoxParser parser(std::move(buffer));
    const auto boxes = parser.parse();

    std::cout << "=== Дерево боксів ISOBMFF / MP4 (C++20) ===\n";
    for (const auto& box : boxes) {
        for (int i = 0; i < box.depth; ++i) std::cout << "  ";
        std::cout << "Box: [" << box.type << "] Size: " << box.size 
                  << ", Offset: " << box.offset << "\n";
    }

    return 0;
}
```
:::

## Аналіз деталей реалізації та порівняння парадигм C та C++

Наведений програмістський проект демонструє різницю у підходах до системного програмування між низькорівневою мовою C та сучасним стандартом C++20:

### 1. Перетворення порядків байтів (Endiansness Conversion)

Оскільки стандарт ISOBMFF вимагає збереження полів розмірів та типів у формати Big-Endian (Network Byte Order), а сучасні процесори архітектури x86/x64 та ARM працюють у формати Little-Endian, пряме зчитання `uint32_t` з буфера поверне спотворені дані.

У функції `read_uint32_be` застосовується бітове зміщення (`<< 24`, `<< 16`, `<< 8`), яке явним чином збирає 32-бітне число з чотирьох послідовних байтів пам'яті незалежно від архітектури ЦП. У C++20 для цієї задачі можна додатково використовувати стандартну бітову функцію `std::byteswap` із заголовка `<bit>`.

### 2. Безпека роботи з пам'яттю та абстракція даних

У версії мовою C виклик `parse_mp4_boxes` приймає сирий вказівник `const uint8_t *buffer` та змінну максимального зсуву `max_offset`. Програміст змушений вручну перевіряти вихід за межі масиву на кожній ітерації.

У версії на C++20 клас `Mp4BoxParser` оперує легким об'єктом-зрізом `std::span<const std::uint8_t>`. `std::span` не володіє пам'яттю сам по собі, але об'єднує вказівник та розмір у єдиний безпечний об'єкт, усуваючи необхідність передачі окремих змінних довжини через параметри методів.

Порівняння підходів у коді:

- **Порівняння рядків FourCC:** У C використовується функція `strcmp()` над тимчасовим 5-байтовим масивом `char type_str[5]`. У C++ застосовується `std::string_view`, що дозволяє виконувати порівняння з `constexpr` масивом `containers` без жодного виділення динамічної пам'яті у купі (Heap).
- **Управління файлами:** У C використовується `FILE*`, `fopen()`, `fseek()` та `fclose()`, які вимагають дбайливої обробки помилок у кожній гілці відмови. У C++ застосовується `std::ifstream` з автоматичним закриттям файлу у деструкторі.

## Аналіз безпеки та захист від пошкоджених даних

При обробці бінарних медіафайлів з невідомих джерел парсер виступає першою лінією оборони проти атак класу Buffer Overflow та Denial of Service. 

Ключові механізми захисту, реалізовані в коді:

1. **Суворий контроль меж масиву (Bounds Checking):** Перед кожним зчитанням полів `size` та `type` перевіряється умова `offset + 8 <= max_offset`. Це унеможливлює вихід покажчика за межі виділеної оперативної пам'яті.
2. **Захист від нескінченних циклів:** Якщо в пошкодженому файлі записано `box_size < 8` (що менше за розмір самого заголовка), цикл розбору негайно зупиняється (`break`), запобігаючи нескінченному зацикленню парсера на одному й тому самому зсуві.
3. **Захист від забігання боксу за межі файлу:** Перевірка `offset + box_size > max_offset` виявляє фальсифіковані заголовки боксів, чий розрахований розмір вказує на байти поза межами завантаженого буфера.
4. **Управління ресурсами в C++20:** Використання контейнерів `std::vector` та обгортки `std::span` гарантує автоматичне вилучення буферів з пам'яті при виході з області видимості за принципом RAII (Resource Acquisition Is Initialization) навіть у випадку виникнення винятків під час файлового введення-виведення.

## Практична оптимізація для файлів великого обсягу

Для обробки медіафайлів розміром у десятки гігабайтів (наприклад, нестиснених відеозаписів 4K) завантаження всього файлу в оперативну пам'яті за допомогою `malloc` або `std::vector` є неефективним і може викликати помилку `Out of Memory`.

У промислових декодерах замість повного зчитування у буфер використовують концепцію **проектування файлів у пам'ять (Memory-Mapped Files)**:
- У системі Linux / POSIX застосовують системний виклик `mmap()`;
- У операційній системі Windows використовують комбінацію викликів `CreateFileMapping()` та `MapViewOfFile()`.

Проектування дозволяє операційній системі відобразити файл MP4 у віртуальний адресний простір процесу. Парсер працює з покажчиками на байти так само, як у наведеному вище коді, але фізичні сторінки дискового кешу завантажуються в оперативну пам'ять динамічно за запитом ядра ОС, що забезпечує найвищу швидкість розбору при мінімальних витратах RAM.
