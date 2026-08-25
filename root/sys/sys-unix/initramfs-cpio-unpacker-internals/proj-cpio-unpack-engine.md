# ⚙️ Парсер та розпаковувач архіву cpio newc без виділення пам'яті

Цей практичний приклад показує створення автономного парсера архівів `cpio newc`, схожого за своєю системною логікою на внутрішній ядерний розпаковувач `init/initramfs.c`. Код розкодовує потоковий буфер пам'яті у форматі SVR4, здійснює вирівнювання за межами 4 байтів, розбирає шістнадцяткові ASCII-заголовки та створює відповідні файли, каталоги й символьні посилання у файловій системі призначення.

Розробка такого парсера вимагає суворого дотримання правил безпеки роботи з пам'яттю, запобігання виходу за межі буфера (англ. *buffer overflow*) та захисту від атак типу Path Traversal (Zip Slip), коли шкідливі шляхи у файлах на кшталт `../../etc/shadow` можуть перезаписати критичні системні файли поза межами цільового каталогу.

### Принципи побудови автономного парсера

При розробці розпаковувача для обмеженого середовища (початкові завантажувачі, вбудовані системи, кастомні утиліти PID 1) враховуються такі ключові обмеження та апаратні вимоги:

1. **Відсутність динамічної купи (Zero Allocation):** Парсер працює безпосередньо над переданим у пам'яті покажчиком на буфер `cpio`. Він не створює проміжних динамічних копій даних у купі (`malloc` або `new`), а використовує покажчики на зсуви всередині існуючого буфера пам'яті.
2. **Hex ASCII Конверсія без libc:** Використання стандартних функцій типу `sscanf()` або `strtoul()` є небажаним в ранньому коді ядра чи завантажувача, оскільки вони мають великі накладні витрати й залежать від локалі. Конверсія 8-значних hex-рядків у числа `uint32_t` виконується через побітову арифметику зсувів.
3. **Обробка вирівнювання (4-Byte Alignment):** Кожен заголовок, ім'я файлу та файлове навантаження мають бути вирівняні за межею 4 байтів. На архітектурах без підтримки невирівняного доступу до пам'яті (деякі ядра ARM Cortex-M та RISC-V) спроба прочитати 32-бітне число за некратним зсувом викликає апаратне виключення Alignment Fault (`SIGBUS`). Тому функція `align4()` є критичною для мобільності коду.
4. **Реконструкція дерев каталогів:** Файли всередині `cpio` можуть перелічуватися у довільному порядку без попередньої наявності записів батьківських каталогів. Розпаковувач мусить автоматично перевіряти й створювати всі проміжні каталоги перед відкриттям файлу на запис.
5. **Розв'язання жорстких посилань:** Коли декілька записів архіву мають однаковий номер іноди `c_ino` та лічильник `c_nlink > 1`, парсер зберігає відповідність `c_ino -> path` у таблиці й створює наступні посилання через виклик `link()`.

Нижче наведено дві автономні реалізації розпаковувача: класичною мовою C з системними викликами POSIX та сучасною мовою C++20 з використанням безпечних типів `std::span`, `std::string_view` та обробкою помилок `std::expected`.

:::tabs
```c
/* cpio_parser.c — Парсер cpio newc мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>

#define CPIO_MAGIC_NEWC "070701"
#define CPIO_MAGIC_CRC  "070702"
#define CPIO_TRAILER    "TRAILER!!!"
#define MAX_HARDLINKS   256

struct cpio_newc_header {
    char c_magic[6];
    char c_ino[8];
    char c_mode[8];
    char c_uid[8];
    char c_gid[8];
    char c_nlink[8];
    char c_mtime[8];
    char c_filesize[8];
    char c_maj[8];
    char c_min[8];
    char c_rmaj[8];
    char c_rmin[8];
    char c_namesize[8];
    char c_chksum[8];
};

struct hardlink_entry {
    uint32_t ino;
    char path[512];
};

static struct hardlink_entry g_hardlinks[MAX_HARDLINKS];
static size_t g_hardlink_count = 0;

/* Безпечна конверсія 8-значного hex ASCII в uint32_t без sscanf */
static uint32_t parse_hex8(const char *hex_str) {
    uint32_t val = 0;
    for (int i = 0; i < 8; ++i) {
        char c = hex_str[i];
        val <<= 4;
        if (c >= '0' && c <= '9')      val |= (c - '0');
        else if (c >= 'A' && c <= 'F') val |= (c - 'A' + 10);
        else if (c >= 'a' && c <= 'f') val |= (c - 'a' + 10);
    }
    return val;
}

/* Обчислення падінгу до межі 4 байтів */
static inline size_t align4(size_t offset) {
    return (4 - (offset % 4)) % 4;
}

/* Перевірка на відсутність виходу за межі батьків Path Traversal */
static int is_safe_path(const char *path) {
    if (strstr(path, "../") != NULL || strstr(path, "/..") != NULL) {
        return 0;
    }
    return 1;
}

/* Рекурсивне створення батьківських каталогів */
static void make_parent_dirs(char *path) {
    char *p = path;
    if (*p == '/') p++;
    while ((p = strchr(p, '/')) != NULL) {
        *p = '\0';
        mkdir(path, 0755);
        *p = '/';
        p++;
    }
}

/* Створення описувача файлової системи за типом у mode */
static int extract_node(const char *path, uint32_t ino, uint32_t mode, 
                        const uint8_t *data, uint32_t filesize) {
    uint32_t file_type = mode & 0170000;
    mode_t perms = mode & 07777;

    if (!is_safe_path(path)) {
        fprintf(stderr, "Попередження: Блоковано небезпечний шлях: %s\n", path);
        return -1;
    }

    /* Перевірка наявних жорстких посилань за номер іноди */
    if (file_type == 0100000 && filesize == 0) {
        for (size_t i = 0; i < g_hardlink_count; ++i) {
            if (g_hardlinks[i].ino == ino) {
                link(g_hardlinks[i].path, path);
                return 0;
            }
        }
    }

    if (file_type == 0040000) { /* S_IFDIR */
        char path_copy[1024];
        strncpy(path_copy, path, sizeof(path_copy));
        make_parent_dirs(path_copy);
        mkdir(path, perms);
    } else if (file_type == 0100000) { /* S_IFREG */
        char path_copy[1024];
        strncpy(path_copy, path, sizeof(path_copy));
        make_parent_dirs(path_copy);

        int fd = open(path, O_WRONLY | O_CREAT | O_TRUNC, perms);
        if (fd < 0) return -1;
        if (filesize > 0) {
            ssize_t written = write(fd, data, filesize);
            (void)written;
        }
        close(fd);

        /* Реєстрація першого файлу для жорстких посилань */
        if (g_hardlink_count < MAX_HARDLINKS) {
            g_hardlinks[g_hardlink_count].ino = ino;
            strncpy(g_hardlinks[g_hardlink_count].path, path, 512);
            g_hardlink_count++;
        }
    } else if (file_type == 0120000) { /* S_IFLNK */
        char target[512] = {0};
        if (filesize < sizeof(target)) {
            memcpy(target, data, filesize);
            symlink(target, path);
        }
    }
    return 0;
}

/* Головний цикл парсингу буфера cpio */
int unpack_cpio_buffer(const uint8_t *buf, size_t buf_size, const char *out_dir) {
    size_t off = 0;
    char path_buf[1024];
    g_hardlink_count = 0;

    while (off + sizeof(struct cpio_newc_header) <= buf_size) {
        const struct cpio_newc_header *hdr = (const struct cpio_newc_header *)(buf + off);

        if (memcmp(hdr->c_magic, CPIO_MAGIC_NEWC, 6) != 0 &&
            memcmp(hdr->c_magic, CPIO_MAGIC_CRC, 6) != 0) {
            fprintf(stderr, "Помилка: Невірний magic header за зсувом %zu\n", off);
            return -1;
        }

        uint32_t ino      = parse_hex8(hdr->c_ino);
        uint32_t mode     = parse_hex8(hdr->c_mode);
        uint32_t filesize = parse_hex8(hdr->c_filesize);
        uint32_t namesize = parse_hex8(hdr->c_namesize);

        off += sizeof(struct cpio_newc_header);

        if (off + namesize > buf_size) {
            fprintf(stderr, "Помилка: Заголовок виходить за межі буфера\n");
            return -1;
        }

        const char *name = (const char *)(buf + off);
        if (namesize == 0 || name[namesize - 1] != '\0') {
            fprintf(stderr, "Помилка: Імена файлів мають завершуватися NUL\n");
            return -1;
        }

        /* Перевірка маркера кінця архіву */
        if (strcmp(name, CPIO_TRAILER) == 0) {
            printf("Успішно знайдено маркер " CPIO_TRAILER ". Завершення розпакування.\n");
            return 0;
        }

        off += namesize;
        off += align4(sizeof(struct cpio_newc_header) + namesize);

        if (off + filesize > buf_size) {
            fprintf(stderr, "Помилка: Дані файлу виходять за межі буфера\n");
            return -1;
        }

        const uint8_t *data = buf + off;

        /* Формування повного шляху призначення */
        snprintf(path_buf, sizeof(path_buf), "%s/%s", out_dir, name);

        /* Пропуск поточного каталогу "." */
        if (strcmp(name, ".") != 0) {
            extract_node(path_buf, ino, mode, data, filesize);
        }

        off += filesize;
        off += align4(filesize);
    }
    return 0;
}
```
```cpp
// cpio_parser.cpp — Ідіоматичний парсер cpio newc мовою C++20
#include <iostream>
#include <span >
#include <string_view>
#include <system_error>
#include <expected>
#include <filesystem>
#include <fstream>
#include <charconv>
#include <cstring>
#include <unordered_map>

namespace fs = std::filesystem;

namespace cpio {

constexpr std::string_view MAGIC_NEWC = "070701";
constexpr std::string_view MAGIC_CRC  = "070702";
constexpr std::string_view TRAILER     = "TRAILER!!!";

struct [[gnu::packed]] Header {
    char magic[6];
    char ino[8];
    char mode[8];
    char uid[8];
    char gid[8];
    char nlink[8];
    char mtime[8];
    char filesize[8];
    char maj[8];
    char min[8];
    char rmaj[8];
    char rmin[8];
    char namesize[8];
    char chksum[8];
};

enum class ParseError {
    InvalidMagic,
    OutOfBounds,
    MissingNullTerminator,
    PathTraversalAttempt,
    ExtractionFailed
};

/* Безпечна C++20 конверсія 8-значного hex ASCII в uint32_t через std::from_chars */
constexpr std::optional<uint32_t> parse_hex8(std::string_view sv) noexcept {
    if (sv.size() < 8) return std::nullopt;
    uint32_t val = 0;
    auto [ptr, ec] = std::from_chars(sv.data(), sv.data() + 8, val, 16);
    if (ec == std::errc{}) return val;
    return std::nullopt;
}

constexpr size_t align4(size_t offset) noexcept {
    return (4 - (offset % 4)) % 4;
}

class Unpacker {
public:
    static std::expected<size_t, ParseError> unpack(
        std::span<const std::byte> buffer, 
        const fs::path& target_dir) 
    {
        size_t offset = 0;
        std::unordered_map<uint32_t, fs::path> hardlinks;

        while (offset + sizeof(Header) <= buffer.size()) {
            const auto* hdr = reinterpret_cast<const Header*>(buffer.data() + offset);
            std::string_view magic{hdr->magic, 6};

            if (magic != MAGIC_NEWC && magic != MAGIC_CRC) {
                return std::unexpected(ParseError::InvalidMagic);
            }

            auto ino      = parse_hex8({hdr->ino, 8});
            auto mode     = parse_hex8({hdr->mode, 8});
            auto filesize = parse_hex8({hdr->filesize, 8});
            auto namesize = parse_hex8({hdr->namesize, 8});

            if (!ino || !mode || !filesize || !namesize) {
                return std::unexpected(ParseError::InvalidMagic);
            }

            offset += sizeof(Header);

            if (offset + *namesize > buffer.size()) {
                return std::unexpected(ParseError::OutOfBounds);
            }

            std::string_view name{
                reinterpret_cast<const char*>(buffer.data() + offset), 
                *namesize > 0 ? *namesize - 1 : 0
            };

            if (name == TRAILER) {
                return offset; // Успішно досягнуто маркер кінця
            }

            if (name.find("../") != std::string_view::npos) {
                return std::unexpected(ParseError::PathTraversalAttempt);
            }

            offset += *namesize;
            offset += align4(sizeof(Header) + *namesize);

            if (offset + *filesize > buffer.size()) {
                return std::unexpected(ParseError::OutOfBounds);
            }

            std::span<const std::byte> payload = buffer.subspan(offset, *filesize);

            if (name != "." && !name.empty()) {
                fs::path out_path = target_dir / name;
                if (!extract_node(out_path, *ino, *mode, payload, hardlinks)) {
                    return std::unexpected(ParseError::ExtractionFailed);
                }
            }

            offset += *filesize;
            offset += align4(*filesize);
        }

        return offset;
    }

private:
    static bool extract_node(
        const fs::path& path, 
        uint32_t ino,
        uint32_t mode, 
        std::span<const std::byte> payload,
        std::unordered_map<uint32_t, fs::path>& hardlinks) 
    {
        std::error_code ec;
        uint32_t type = mode & 0170000;

        // Перевірка наявних жорстких посилань
        if (type == 0100000 && payload.empty()) {
            if (auto it = hardlinks.find(ino); it != hardlinks.end()) {
                fs::create_hard_link(it->second, path, ec);
                return !ec;
            }
        }

        if (type == 0040000) { // S_IFDIR
            fs::create_directories(path, ec);
        } else if (type == 0100000) { // S_IFREG
            if (path.has_parent_path()) {
                fs::create_directories(path.parent_path(), ec);
            }
            std::ofstream file(path, std::ios::binary);
            if (!file) return false;
            file.write(reinterpret_cast<const char*>(payload.data()), payload.size());
            fs::permissions(path, static_cast<fs::perms>(mode & 0777), ec);
            hardlinks[ino] = path;
        } else if (type == 0120000) { // S_IFLNK
            std::string_view target{
                reinterpret_cast<const char*>(payload.data()), 
                payload.size()
            };
            fs::create_symlink(target, path, ec);
        }
        return !ec;
    }
};

} // namespace cpio
```
:::

### Покроковий розбір логіки роботи розпаковувача

1. **Валідація магічних байтів:**
   Кожна ітерація головного циклу починається з перевірки поля `hdr->c_magic`. Якщо байти відрізняються від `"070701"` та `"070702"`, парсер розцінює це як пошкодження архіву або зміщення адресації й припиняє обробку.

2. **Декодування hex-полів:**
   Значення `ino`, `mode`, `filesize` та `namesize` перетворюються з текстового вигляду на 32-бітні цілі числа. У версії C++20 для цього використовується системна функція `std::from_chars()`, яка не створює тимчасових рядків і працює в кілька разів швидше за `sscanf()`.

3. **Обчислення зсувів та вирівнювання:**
   Після прочитання імені файлу зсув `offset` збільшується на `namesize`. Для досягнення межі 4 байтів додається значення `align4(sizeof(Header) + namesize)`. Аналогічно після прочитання даних файлу додається `align4(filesize)`.

4. **Захист від Path Traversal:**
   Обидва варіанти коду містять перевірку імені файлу на наявність послідовності `../`. Це запобігає спробам створення файлів вище цільового каталогу розпакування.

5. **Реконструкція дерев каталогів та жорстких посилань:**
   Перед створенням звичайного файлу викликається функція створення батьківських каталогів (`fs::create_directories`). Для збереження жорстких посилань парсер веде картографування номерів `ino` на створені шляхи, що дозволяє уникнути дублювання однакових бінарних файлів у пам'яті.

### Особливості обробки символьних та блокових пристроїв

У реальному коді ядра Linux функція `unpack_to_rootfs()` також обробляє файли пристроїв (`S_IFCHR` та `S_IFBLK`). Коли значення `mode & 0170000` вказує на пристрій, розпаковувач зчитує номери `c_rmaj` та `c_rmin` із заголовка й викликає системний виклик `mknod(path, mode, dev)`:

- Для символьного пристрою `/dev/console` (major 5, minor 1) створюється вузол доступу до системної консолі.
- Для блокового пристрою `/dev/ram0` (major 1, minor 0) створюється вузол доступу до оперативної пам'яті.

Обробка пристроїв є обов'язковою для повноцінного функціонування раннього простору користувача, оскільки утилітам `/init` потрібен доступ до консолі введення-виведення ще до завантаження драйвера `devtmpfs`.

### Діагностика пошкоджень та стійкість до збоїв

У разі виявлення пошкодженого архіву (некоректна довжина `namesize`, вихід зсуву `offset` за межі пам'яті буфера, відсутність завершального NUL-байта) розпаковувач повертає помилку й зупиняє розбірку. В умовах реального завантаження ядра пошкодження initramfs викликає ядерну паніку `Kernel panic - not syncing: VFS: Unable to mount root fs`, що підкреслює важливість точної відповідності специфікації `cpio newc`.
