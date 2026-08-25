# ⚙️ Реалізація блокового CoW-оверлею та розв'язання ланцюжка шарів

Щоб зрозуміти, як промислові формати віртуальних дисків (зокрема QCOW2 у QEMU/KVM або VHDX у Hyper-V) здійснюють миттєву фіксацію знімків та створюють зв'язані клони віртуальних машин, необхідно спуститися на рівень блокового драйвера і побудувати діючий механізм трансляції секторів. У цій практичній роботі ми спроектуємо, детально розберемо та реалізуємо з нуля повнофункціональний мініатюрний блоковий драйвер дельта-оверлею з підтримкою копіювання при записі (Redirect-on-Write), каскадного рекурсивного спуску по ланцюжку базових файлів (Backing Chain Traversal), взаємного блокування шарів та операції зворотного злиття змін (Block Commit).

---

## 1. Архітектура формату та формат бінарного заголовка

Віртуальний диск базового рівня (`base.raw`) є суцільним масивом секторів фіксованого розміру (за стандартом 512 байтів).

Файл оверлею (`overlay.cow`) складається з трьох послідовних секцій:
1. **Заголовок фіксованого розміру (Header, 512 байтів):** містить магічне число `0x434F5731` (`COW1`), версію формату, загальну кількість логічних секторів віртуального диска, зміщення таблиці розподілу, розмір бітової карти та рядок шляху до батьківського файлу (`backing_file`).
2. **Бітова карта виділення (Allocation Bitmap):** масив бітів, де кожен біт відповідає одному логічному сектору віртуального диска (`0` — сектор не модифіковано в оверлеї, читати з батька; `1` — сектор записано в оверлей, читати з локального файлу).
3. **Область даних секторів (Data Payloads):** фізичні блоки даних розміром 512 байтів, розташовані за зміщеннями, що відповідають їхнім логічним номерам.

### Бінарна структура заголовка оверлею

```
+-----------------------------------------------------------------------+
|  Зсув (байти) | Розмір | Поле заголовка   | Призначення               |
+---------------+--------+------------------+---------------------------+
|  0x00..0x03   | 4      | magic            | Сигнатура 'COW1'          |
|  0x04..0x07   | 4      | version          | Версія формату (= 1)      |
|  0x08..0x0F   | 8      | total_sectors    | Кількість секторів        |
|  0x10..0x17   | 8      | bitmap_offset    | Зсув бітової карти (=512) |
|  0x18..0x1F   | 8      | bitmap_bytes     | Розмір бітової карти      |
|  0x20..0x27   | 8      | data_offset      | Початок області секторів  |
|  0x28..0x127  | 256    | backing_path     | Шлях до батьківського файлу|
|  0x128..0x1FF | 216    | reserved         | Резерв під розширення     |
+-----------------------------------------------------------------------+
```

### Фізичне вирівнювання структур даних та прямий ввід-вивід

Критично важливою вимогою для будь-якого блокового драйвера є строге вирівнювання всіх метаданих та областей корисного навантаження по фізичних межах секторів диска (зазвичай 512 байтів або 4096 байтів).

Якщо область секторів даних `data_offset` починається за непарним зсувом (наприклад, `512 + 137 = 649` байтів), кожна операція запису в оверлей перетинатиме фізичні сектори носія хоста. Це призводить до внутрішньої апаратної ампліфікації: накопичувач змушений зчитувати два фізичні сектори, модифікувати проміжні байти і виконувати два фізичні записи. 

Тому наш драйвер вирівнює розмір бітової карти `bitmap_bytes` до найближчого кратного значення `SECTOR_SIZE`. Навіть якщо для диска на 100 секторів потрібно лише 13 байтів бітової карти, під неї виділяється повний сектор розміром 512 байтів. Завдяки цьому область `data_offset` гарантовано починається з кратного зміщення `1024`, що уможливлює використання високопродуктивного прямого вводу-виводу з прапорцем `O_DIRECT`.

---

## 2. Реалізація структур даних та відкриття ланцюжка

Драйвер повинен вміти рекурсивно відкривати ланцюжок від активного оверлею до найглибшого базового образу, формуючи зв'язний список відкритих дескрипторів.

Структура `CowNode` представляє один окремий шар у дисковому ланцюжку. Якщо файл містить сигнатуру `COW1`, він позначається як оверлей (`is_overlay = true`), а його бітова карта завантажується в оперативну пам'ять для забезпечення миттєвого тестування стану секторів за час `O(1)`. Якщо файл не містить заголовка оверлею, драйвер вважає його сирим плоским диском (`raw disk image`) і розміщує на дні ланцюжка як кінцевий термінальний вузол.

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
#include <errno.h>

#define COW_MAGIC 0x434F5731
#define COW_VERSION 1
#define SECTOR_SIZE 512
#define MAX_PATH_LEN 256

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint32_t version;
    uint64_t total_sectors;
    uint64_t bitmap_offset;
    uint64_t bitmap_bytes;
    uint64_t data_offset;
    char backing_path[MAX_PATH_LEN];
    uint8_t reserved[216];
} CowHeader;
#pragma pack(pop)

typedef struct CowNode {
    int fd;
    bool is_overlay;
    CowHeader header;
    uint8_t *bitmap;
    struct CowNode *backing_node;
} CowNode;

static inline bool bitmap_test(const uint8_t *bm, uint64_t sector) {
    return (bm[sector / 8] & (1 << (sector % 8))) != 0;
}

static inline void bitmap_set(uint8_t *bm, uint64_t sector) {
    bm[sector / 8] |= (1 << (sector % 8));
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <span>
#include <array>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>

constexpr uint32_t COW_MAGIC = 0x434F5731;
constexpr uint32_t COW_VERSION = 1;
constexpr size_t SECTOR_SIZE = 512;
constexpr size_t MAX_PATH_LEN = 256;

#pragma pack(push, 1)
struct CowHeader {
    uint32_t magic{COW_MAGIC};
    uint32_t version{COW_VERSION};
    uint64_t total_sectors{0};
    uint64_t bitmap_offset{SECTOR_SIZE};
    uint64_t bitmap_bytes{0};
    uint64_t data_offset{0};
    char backing_path[MAX_PATH_LEN]{0};
    uint8_t reserved[216]{0};
};
#pragma pack(pop)

static_assert(sizeof(CowHeader) == SECTOR_SIZE, "CowHeader must be exactly 512 bytes");

class CowNode {
public:
    int fd{-1};
    bool is_overlay{false};
    CowHeader header{};
    std::vector<uint8_t> bitmap{};
    std::unique_ptr<CowNode> backing_node{nullptr};

    ~CowNode() noexcept {
        if (fd >= 0) {
            ::close(fd);
        }
    }

    CowNode() = default;
    CowNode(const CowNode&) = delete;
    CowNode& operator=(const CowNode&) = delete;

    CowNode(CowNode&& other) noexcept 
        : fd(other.fd), is_overlay(other.is_overlay), header(other.header),
          bitmap(std::move(other.bitmap)), backing_node(std::move(other.backing_node)) {
        other.fd = -1;
    }

    CowNode& operator=(CowNode&& other) noexcept {
        if (this != &other) {
            if (fd >= 0) ::close(fd);
            fd = other.fd;
            is_overlay = other.is_overlay;
            header = other.header;
            bitmap = std::move(other.bitmap);
            backing_node = std::move(other.backing_node);
            other.fd = -1;
        }
        return *this;
    }

    [[nodiscard]] bool is_sector_allocated(uint64_t sector) const noexcept {
        if (!is_overlay || bitmap.empty() || (sector / 8) >= bitmap.size()) {
            return false;
        }
        return (bitmap[sector / 8] & (1 << (sector % 8))) != 0;
    }

    void mark_sector_allocated(uint64_t sector) noexcept {
        if ((sector / 8) < bitmap.size()) {
            bitmap[sector / 8] |= (1 << (sector % 8));
        }
    }
};
```
:::

---

## 3. Створення нового шару оверлею (Create Overlay)

Операція створення оверлею (`cow_create_overlay`) є наріжним каменем миттєвого створення знімків та зв'язаних клонів. Її обчислювальна складність становить `O(1)` відносно розміру диска, оскільки на диск записується лише фіксований заголовок та ініціалізується нульова бітова карта.

Під час створення оверлею:
1. Базовий файл не відкривається на запис і не змінюється жодним байтом.
2. Новий файл оверлею створюється з системним прапорцем `O_CREAT | O_TRUNC | O_CLOEXEC`.
3. Заголовок ініціалізується метаданими: зберігається абсолютний або відносний рядок `backing_path`, що вказує на батьківський файл.
4. Область бітової карти заповнюється нульовими байтами (`calloc`), що означає повну чистоту оверлею: жоден сектор ще не перенаправлено.
5. Викликається системний виклик `fdatasync()`, що гарантує фізичний запис метаданих заголовка на пластини накопичувача або у флеш-пам'ять SSD до повернення керування.

:::tabs
```c
int cow_create_overlay(const char *overlay_path, const char *backing_path, uint64_t total_sectors) {
    int fd = open(overlay_path, O_RDWR | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    if (fd < 0) {
        return -1;
    }

    uint64_t bm_bytes = (total_sectors + 7) / 8;
    // Вирівнюємо розмір бітової карти по межі 512 байтів
    uint64_t bm_sectors = (bm_bytes + SECTOR_SIZE - 1) / SECTOR_SIZE;
    uint64_t aligned_bm_bytes = bm_sectors * SECTOR_SIZE;

    CowHeader hdr;
    memset(&hdr, 0, sizeof(hdr));
    hdr.magic = COW_MAGIC;
    hdr.version = COW_VERSION;
    hdr.total_sectors = total_sectors;
    hdr.bitmap_offset = sizeof(CowHeader);
    hdr.bitmap_bytes = aligned_bm_bytes;
    hdr.data_offset = hdr.bitmap_offset + aligned_bm_bytes;
    strncpy(hdr.backing_path, backing_path, MAX_PATH_LEN - 1);

    if (pwrite(fd, &hdr, sizeof(hdr), 0) != sizeof(hdr)) {
        close(fd);
        return -1;
    }

    // Записуємо нульову бітову карту
    uint8_t *zero_bm = (uint8_t *)calloc(1, aligned_bm_bytes);
    if (!zero_bm) {
        close(fd);
        return -1;
    }

    if ((uint64_t)pwrite(fd, zero_bm, aligned_bm_bytes, hdr.bitmap_offset) != aligned_bm_bytes) {
        free(zero_bm);
        close(fd);
        return -1;
    }

    free(zero_bm);
    fdatasync(fd);
    close(fd);
    return 0;
}
```
```cpp
std::expected<void, std::error_code> create_cow_overlay(
    std::string_view overlay_path,
    std::string_view backing_path,
    uint64_t total_sectors
) {
    int fd = ::open(overlay_path.data(), O_RDWR | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    uint64_t bm_bytes = (total_sectors + 7) / 8;
    uint64_t bm_sectors = (bm_bytes + SECTOR_SIZE - 1) / SECTOR_SIZE;
    uint64_t aligned_bm_bytes = bm_sectors * SECTOR_SIZE;

    CowHeader hdr{};
    hdr.magic = COW_MAGIC;
    hdr.version = COW_VERSION;
    hdr.total_sectors = total_sectors;
    hdr.bitmap_offset = sizeof(CowHeader);
    hdr.bitmap_bytes = aligned_bm_bytes;
    hdr.data_offset = hdr.bitmap_offset + aligned_bm_bytes;
    
    size_t copy_len = std::min(backing_path.size(), MAX_PATH_LEN - 1);
    std::memcpy(hdr.backing_path, backing_path.data(), copy_len);
    hdr.backing_path[copy_len] = '\0';

    if (::pwrite(fd, &hdr, sizeof(hdr), 0) != sizeof(hdr)) {
        int err = errno;
        ::close(fd);
        return std::unexpected(std::error_code(err, std::generic_category()));
    }

    std::vector<uint8_t> zero_bm(aligned_bm_bytes, 0);
    if (static_cast<uint64_t>(::pwrite(fd, zero_bm.data(), zero_bm.size(), hdr.bitmap_offset)) != aligned_bm_bytes) {
        int err = errno;
        ::close(fd);
        return std::unexpected(std::error_code(err, std::generic_category()));
    }

    ::fdatasync(fd);
    ::close(fd);
    return {};
}
```
:::

---

## 4. Рекурсивне відкриття та розв'язання ланцюжка (Open Chain)

Коли віртуальна машина запускається з оверлеєм, блоковий драйвер зобов'язаний розібрати весь ланцюжок залежностей до найглибшої бази.

Процес відкриття ланцюжка (`cow_open_chain`) виконується рекурсивно:
1. Драйвер відкриває активний файл оверлею. Якщо файл вдається відкрити на запис (`O_RDWR`), він може виступати активним шаром.
2. Зчитується перші 512 байтів заголовка. Якщо сигнатура відповідає `COW_MAGIC`:
   - Зчитується бітова карта розміром `bitmap_bytes` із файлового зміщення `bitmap_offset`.
   - Витягується рядок `backing_path`.
   - Драйвер рекурсивно викликає `cow_open_chain(backing_path)`, створюючи наступний вузол `backing_node`. Батьківський файл відкривається в режимі **суворого Read-Only (`O_RDONLY`)** для захисту від випадкової модифікації.
3. Якщо сигнатура відсутня, вузол маркується як плоский сирий диск (`RAW`), на якому ланцюжок зупиняється.

:::tabs
```c
CowNode *cow_open_chain(const char *image_path) {
    int fd = open(image_path, O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        // Спроба відкрити в режимі Read-Only (для базових образів)
        fd = open(image_path, O_RDONLY | O_CLOEXEC);
        if (fd < 0) return NULL;
    }

    CowNode *node = (CowNode *)calloc(1, sizeof(CowNode));
    if (!node) {
        close(fd);
        return NULL;
    }
    node->fd = fd;

    CowHeader hdr;
    if (pread(fd, &hdr, sizeof(hdr), 0) == sizeof(hdr) && hdr.magic == COW_MAGIC) {
        node->is_overlay = true;
        node->header = hdr;
        node->bitmap = (uint8_t *)malloc(hdr.bitmap_bytes);
        if (!node->bitmap) {
            close(fd);
            free(node);
            return NULL;
        }

        if ((uint64_t)pread(fd, node->bitmap, hdr.bitmap_bytes, hdr.bitmap_offset) != hdr.bitmap_bytes) {
            free(node->bitmap);
            close(fd);
            free(node);
            return NULL;
        }

        if (strlen(hdr.backing_path) > 0) {
            node->backing_node = cow_open_chain(hdr.backing_path);
            if (!node->backing_node) {
                fprintf(stderr, "Помилка відкриття backing-файлу: %s\n", hdr.backing_path);
                free(node->bitmap);
                close(fd);
                free(node);
                return NULL;
            }
        }
    } else {
        // Сирий образ (RAW)
        node->is_overlay = false;
        off_t size = lseek(fd, 0, SEEK_END);
        node->header.total_sectors = (size > 0) ? (size / SECTOR_SIZE) : 0;
    }

    return node;
}

void cow_close_chain(CowNode *node) {
    if (!node) return;
    if (node->backing_node) {
        cow_close_chain(node->backing_node);
    }
    if (node->bitmap) {
        free(node->bitmap);
    }
    if (node->fd >= 0) {
        close(node->fd);
    }
    free(node);
}
```
```cpp
std::expected<std::unique_ptr<CowNode>, std::error_code> open_cow_chain(std::string_view image_path) {
    int fd = ::open(image_path.data(), O_RDWR | O_CLOEXEC);
    if (fd < 0) {
        fd = ::open(image_path.data(), O_RDONLY | O_CLOEXEC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
    }

    auto node = std::make_unique<CowNode>();
    node->fd = fd;

    CowHeader hdr{};
    if (::pread(fd, &hdr, sizeof(hdr), 0) == sizeof(hdr) && hdr.magic == COW_MAGIC) {
        node->is_overlay = true;
        node->header = hdr;
        node->bitmap.resize(hdr.bitmap_bytes);

        if (static_cast<uint64_t>(::pread(fd, node->bitmap.data(), hdr.bitmap_bytes, hdr.bitmap_offset)) != hdr.bitmap_bytes) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (std::strlen(hdr.backing_path) > 0) {
            auto backing_res = open_cow_chain(hdr.backing_path);
            if (!backing_res) {
                return std::unexpected(backing_res.error());
            }
            node->backing_node = std::move(*backing_res);
        }
    } else {
        node->is_overlay = false;
        off_t size = ::lseek(fd, 0, SEEK_END);
        node->header.total_sectors = (size > 0) ? (size / SECTOR_SIZE) : 0;
    }

    return node;
}
```
:::

---

## 5. Алгоритми читання та перенаправлення запису (Read/Write Traversal)

Для забезпечення багатопотокової безпеки та відсутності гонитви зміщень у файлових дескрипторах наш драйвер використовує виключно позиційні системні виклики `pread(2)` та `pwrite(2)` замість пари `lseek(2)` + `read(2)`. Це дозволяє кільком потокам vCPU одночасно звертатися до одного відкритого файлу диска без блокувань глобального файлового покажчика позиції ядра.

### Механіка каскадного читання (`cow_read_sector`)

Під час запиту на читання сектора `LBA`:
1. Перевіряється біт у локальній бітовій карті активного шару: `bitmap_test(sector)`.
2. Якщо біт дорівнює `1` (сектор виділено), драйвер обчислює точне фізичне зміщення у файлі:
   `Physical_Offset = data_offset + (LBA * SECTOR_SIZE)`.
   Дані зчитуються безпосередньо з файлу оверлею і повертаються гостю.
3. Якщо біт дорівнює `0` (сектор чистий), драйвер рекурсивно передає виклик батьківському шару `backing_node`.
4. Спуск триває доти, доки сектор не буде знайдено в одному з проміжних знімків або у фінальному базовому образі. Якщо навіть у базовому образі сектор не виділено, буфер заповнюється нулями.

### Механіка запису з перенаправленням (`cow_write_sector`)

Запис завжди спрямовується **виключно в найвищий активний шар оверлею**:
1. Байти записуються за фізичним зміщенням `data_offset + (LBA * SECTOR_SIZE)` у файлі оверлею.
2. Якщо цей сектор раніше не виділявся (біт був `0`), драйвер встановлює біт у бітовій карті в оперативній пам'яті (`bitmap_set`).
3. Нове значення байта бітової карти записується на диск за зміщенням `bitmap_offset + (sector / 8)`.

:::tabs
```c
int cow_read_sector(CowNode *chain, uint64_t sector, uint8_t *buf) {
    if (!chain || sector >= chain->header.total_sectors) {
        return -EINVAL;
    }

    if (chain->is_overlay) {
        if (bitmap_test(chain->bitmap, sector)) {
            // Сектор модифіковано в цьому оверлеї
            off_t offset = chain->header.data_offset + (sector * SECTOR_SIZE);
            if (pread(chain->fd, buf, SECTOR_SIZE, offset) != SECTOR_SIZE) {
                return -EIO;
            }
            return 0;
        }

        // Сектор не виділено: спускаємося по ланцюжку
        if (chain->backing_node) {
            return cow_read_sector(chain->backing_node, sector, buf);
        }

        // Якщо батьківського файлу немає — повертаємо нульовий сектор
        memset(buf, 0, SECTOR_SIZE);
        return 0;
    } else {
        // Читання із сирого образу
        off_t offset = sector * SECTOR_SIZE;
        if (pread(chain->fd, buf, SECTOR_SIZE, offset) != SECTOR_SIZE) {
            return -EIO;
        }
        return 0;
    }
}

int cow_write_sector(CowNode *chain, uint64_t sector, const uint8_t *buf) {
    if (!chain || !chain->is_overlay || sector >= chain->header.total_sectors) {
        return -EINVAL;
    }

    off_t data_off = chain->header.data_offset + (sector * SECTOR_SIZE);
    if (pwrite(chain->fd, buf, SECTOR_SIZE, data_off) != SECTOR_SIZE) {
        return -EIO;
    }

    // Якщо сектор ще не був позначений як виділений — оновлюємо бітову карту
    if (!bitmap_test(chain->bitmap, sector)) {
        bitmap_set(chain->bitmap, sector);

        uint64_t byte_idx = sector / 8;
        off_t bm_file_off = chain->header.bitmap_offset + byte_idx;

        if (pwrite(chain->fd, &chain->bitmap[byte_idx], 1, bm_file_off) != 1) {
            return -EIO;
        }
    }

    return 0;
}
```
```cpp
std::expected<void, std::error_code> cow_read_sector(
    const CowNode& chain,
    uint64_t sector,
    std::span<uint8_t, SECTOR_SIZE> buffer
) {
    if (sector >= chain.header.total_sectors) {
        return std::unexpected(std::error_code(EINVAL, std::generic_category()));
    }

    if (chain.is_overlay) {
        if (chain.is_sector_allocated(sector)) {
            off_t offset = chain.header.data_offset + (sector * SECTOR_SIZE);
            if (::pread(chain.fd, buffer.data(), SECTOR_SIZE, offset) != static_cast<ssize_t>(SECTOR_SIZE)) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            return {};
        }

        if (chain.backing_node) {
            return cow_read_sector(*chain.backing_node, sector, buffer);
        }

        std::fill(buffer.begin(), buffer.end(), 0);
        return {};
    } else {
        off_t offset = sector * SECTOR_SIZE;
        if (::pread(chain.fd, buffer.data(), SECTOR_SIZE, offset) != static_cast<ssize_t>(SECTOR_SIZE)) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }
}

std::expected<void, std::error_code> cow_write_sector(
    CowNode& chain,
    uint64_t sector,
    std::span<const uint8_t, SECTOR_SIZE> buffer
) {
    if (!chain.is_overlay || sector >= chain.header.total_sectors) {
        return std::unexpected(std::error_code(EINVAL, std::generic_category()));
    }

    off_t data_off = chain.header.data_offset + (sector * SECTOR_SIZE);
    if (::pwrite(chain.fd, buffer.data(), SECTOR_SIZE, data_off) != static_cast<ssize_t>(SECTOR_SIZE)) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (!chain.is_sector_allocated(sector)) {
        chain.mark_sector_allocated(sector);

        uint64_t byte_idx = sector / 8;
        off_t bm_file_off = chain.header.bitmap_offset + byte_idx;

        if (::pwrite(chain.fd, &chain.bitmap[byte_idx], 1, bm_file_off) != 1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
    }

    return {};
}
```
:::

---

## 6. Консолідація шарів: зворотне злиття (Block Commit)

Операція `cow_commit_to_backing` забезпечує злиття накопичених дельт активного оверлею в його батьківський шар:

1. Драйвер проходить циклом по всіх логічних секторах диска від `0` до `total_sectors - 1`.
2. За допомогою бітової карти визначаються лише ті сектори, які зазнали модифікації в поточному оверлеї (`bitmap_test == true`).
3. Модифікований сектор зчитується з оверлею і записується в батьківський вузол `backing_node`. Якщо батьківський вузол є оверлеєм, викликається `cow_write_sector`; якщо сирим диском — прямий `pwrite`.
4. Після перенесення всіх блоків викликається `fdatasync()` для батьківського файлу, що гарантує збереження злитих даних.
5. Бітова карта оверлею повністю зануляється, а оновлені нульові байти скидаються на диск. Оверлей знову стає порожнім і чистим, продовжуючи посилатися на оновлену базу.

:::tabs
```c
int cow_commit_to_backing(CowNode *overlay) {
    if (!overlay || !overlay->is_overlay || !overlay->backing_node) {
        return -EINVAL;
    }

    uint8_t buffer[SECTOR_SIZE];
    uint64_t total = overlay->header.total_sectors;

    for (uint64_t s = 0; s < total; ++s) {
        if (bitmap_test(overlay->bitmap, s)) {
            off_t src_off = overlay->header.data_offset + (s * SECTOR_SIZE);
            if (pread(overlay->fd, buffer, SECTOR_SIZE, src_off) != SECTOR_SIZE) {
                return -EIO;
            }

            if (overlay->backing_node->is_overlay) {
                if (cow_write_sector(overlay->backing_node, s, buffer) != 0) {
                    return -EIO;
                }
            } else {
                off_t dst_off = s * SECTOR_SIZE;
                if (pwrite(overlay->backing_node->fd, buffer, SECTOR_SIZE, dst_off) != SECTOR_SIZE) {
                    return -EIO;
                }
            }
        }
    }

    // Синхронізуємо дані на постійному носії
    fdatasync(overlay->backing_node->fd);

    // Очищаємо бітову карту оверлею
    memset(overlay->bitmap, 0, overlay->header.bitmap_bytes);
    if ((uint64_t)pwrite(overlay->fd, overlay->bitmap, overlay->header.bitmap_bytes, 
                         overlay->header.bitmap_offset) != overlay->header.bitmap_bytes) {
        return -EIO;
    }

    fdatasync(overlay->fd);
    return 0;
}
```
```cpp
std::expected<void, std::error_code> cow_commit_to_backing(CowNode& overlay) {
    if (!overlay.is_overlay || !overlay.backing_node) {
        return std::unexpected(std::error_code(EINVAL, std::generic_category()));
    }

    std::array<uint8_t, SECTOR_SIZE> buffer{};
    uint64_t total = overlay.header.total_sectors;

    for (uint64_t s = 0; s < total; ++s) {
        if (overlay.is_sector_allocated(s)) {
            off_t src_off = overlay.header.data_offset + (s * SECTOR_SIZE);
            if (::pread(overlay.fd, buffer.data(), SECTOR_SIZE, src_off) != static_cast<ssize_t>(SECTOR_SIZE)) {
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }

            if (overlay.backing_node->is_overlay) {
                auto res = cow_write_sector(*overlay.backing_node, s, buffer);
                if (!res) return res;
            } else {
                off_t dst_off = s * SECTOR_SIZE;
                if (::pwrite(overlay.backing_node->fd, buffer.data(), SECTOR_SIZE, dst_off) != static_cast<ssize_t>(SECTOR_SIZE)) {
                    return std::unexpected(std::error_code(errno, std::generic_category()));
                }
            }
        }
    }

    ::fdatasync(overlay.backing_node->fd);

    std::fill(overlay.bitmap.begin(), overlay.bitmap.end(), 0);
    if (static_cast<uint64_t>(::pwrite(overlay.fd, overlay.bitmap.data(), 
                                      overlay.bitmap.size(), 
                                      overlay.header.bitmap_offset)) != overlay.bitmap.size()) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ::fdatasync(overlay.fd);
    return {};
}
```
:::

---

## 7. Покрокове трасування операцій на прикладі трирівневого ланцюжка

Розглянемо практичний сценарій роботи драйвера з трирівневим ланцюжком: `active.cow` -> `snap1.cow` -> `base.raw`. Нехай диск складається з 8 секторів, а початковий базовий диск містить байти `0xAA` у кожному секторі.

### Таблиця станів секторів у шарах

| Сектор LBA | Базовий диск (`base.raw`) | Знімок 1 (`snap1.cow`) | Активний оверлей (`active.cow`) | Результат читання (`cow_read`) |
| :--- | :--- | :--- | :--- | :--- |
| **0** | `0xAA` | не виділено (`0`) | не виділено (`0`) | `0xAA` (зчитується з `base.raw`) |
| **1** | `0xAA` | виділено: `0xBB` (`1`) | не виділено (`0`) | `0xBB` (зчитується зі `snap1.cow`) |
| **2** | `0xAA` | не виділено (`0`) | виділено: `0xCC` (`1`) | `0xCC` (зчитується з `active.cow`) |
| **3** | `0xAA` | виділено: `0xB3` (`1`) | виділено: `0xC3` (`1`) | `0xC3` (найновіший із `active.cow`) |

### Хід виконання запиту читання сектора #1

1. Драйвер викликає `cow_read_sector(active_node, 1, buf)`.
2. В активному оверлеї перевіряється біт: `bitmap_test(active_node->bitmap, 1) == false`.
3. Оскільки біт дорівнює нулю, драйвер рекурсивно переходить до батька: `cow_read_sector(snap1_node, 1, buf)`.
4. У `snap1_node` перевіряється біт: `bitmap_test(snap1_node->bitmap, 1) == true`.
5. Драйвер обчислює зміщення: `offset = snap1_node->header.data_offset + (1 * 512)`.
6. Виконується виклик `pread()` для дескриптора `snap1.cow`, зчитується байт `0xBB`, і рекурсія повертає успіх. Спуск до `base.raw` не потрібен.

---

## 8. Повний тестовий стенд: перевірка життєвого циклу

Нижче наведено самодостатню програму для перевірки створення оверлею, запису секторів, читання крізь ланцюжок та фінального злиття.

:::tabs
```c
int main(void) {
    const char *base_img = "test_base.raw";
    const char *snap_img = "test_snap1.cow";
    const uint64_t total_sec = 16;

    // 1. Створюємо базовий образ розміром 16 секторів, заповнений 0xAA
    int base_fd = open(base_img, O_RDWR | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
    uint8_t base_data[SECTOR_SIZE];
    memset(base_data, 0xAA, sizeof(base_data));
    for (int i = 0; i < (int)total_sec; ++i) {
        pwrite(base_fd, base_data, SECTOR_SIZE, i * SECTOR_SIZE);
    }
    close(base_fd);

    // 2. Створюємо оверлей snap1 поверх base
    if (cow_create_overlay(snap_img, base_img, total_sec) != 0) {
        fprintf(stderr, "Помилка створення оверлею\n");
        return 1;
    }

    // 3. Відкриваємо ланцюжок
    CowNode *chain = cow_open_chain(snap_img);
    if (!chain) {
        fprintf(stderr, "Помилка відкриття ланцюжка\n");
        return 1;
    }

    // 4. Записуємо в сектор #3 оверлею значення 0xCC
    uint8_t mod_data[SECTOR_SIZE];
    memset(mod_data, 0xCC, sizeof(mod_data));
    cow_write_sector(chain, 3, mod_data);

    // 5. Читаємо сектор #0 (повинен повернути 0xAA з бази)
    uint8_t read_buf[SECTOR_SIZE];
    cow_read_sector(chain, 0, read_buf);
    printf("Сектор 0: 0x%02X (очікується 0xAA)\n", read_buf[0]);

    // 6. Читаємо сектор #3 (повинен повернути 0xCC з оверлею)
    cow_read_sector(chain, 3, read_buf);
    printf("Сектор 3: 0x%02X (очікується 0xCC)\n", read_buf[0]);

    // 7. Виконуємо Block Commit у базовий образ
    cow_commit_to_backing(chain);
    cow_close_chain(chain);

    // 8. Перевіряємо, що в базовому образі сектор #3 тепер містить 0xCC
    base_fd = open(base_img, O_RDONLY | O_CLOEXEC);
    pread(base_fd, read_buf, SECTOR_SIZE, 3 * SECTOR_SIZE);
    printf("База після commit (сектор 3): 0x%02X (очікується 0xCC)\n", read_buf[0]);
    close(base_fd);

    // Очищення тестових файлів
    unlink(snap_img);
    unlink(base_img);
    return 0;
}
```
```cpp
int main() {
    const std::string base_img = "test_base.raw";
    const std::string snap_img = "test_snap1.cow";
    constexpr uint64_t total_sec = 16;

    // 1. Створюємо базовий образ розміром 16 секторів, заповнений 0xAA
    {
        int base_fd = ::open(base_img.c_str(), O_RDWR | O_CREAT | O_TRUNC | O_CLOEXEC, 0644);
        std::array<uint8_t, SECTOR_SIZE> base_data{};
        base_data.fill(0xAA);
        for (size_t i = 0; i < total_sec; ++i) {
            ::pwrite(base_fd, base_data.data(), SECTOR_SIZE, i * SECTOR_SIZE);
        }
        ::close(base_fd);
    }

    // 2. Створюємо оверлей snap1 поверх base
    auto create_res = create_cow_overlay(snap_img, base_img, total_sec);
    if (!create_res) {
        std::cerr << "Помилка створення оверлею: " << create_res.error().message() << '\n';
        return 1;
    }

    // 3. Відкриваємо ланцюжок
    auto chain_res = open_cow_chain(snap_img);
    if (!chain_res) {
        std::cerr << "Помилка відкриття ланцюжка: " << chain_res.error().message() << '\n';
        return 1;
    }
    auto& chain = *chain_res;

    // 4. Записуємо в сектор #3 оверлею значення 0xCC
    std::array<uint8_t, SECTOR_SIZE> mod_data{};
    mod_data.fill(0xCC);
    auto write_res = cow_write_sector(*chain, 3, mod_data);
    if (!write_res) {
        std::cerr << "Помилка запису в сектор 3\n";
        return 1;
    }

    // 5. Читаємо сектор #0 (повинен повернути 0xAA з бази)
    std::array<uint8_t, SECTOR_SIZE> read_buf{};
    cow_read_sector(*chain, 0, read_buf);
    std::cout << "Сектор 0: 0x" << std::hex << static_cast<int>(read_buf[0]) << " (очікується 0xaa)\n";

    // 6. Читаємо сектор #3 (повинен повернути 0xCC з оверлею)
    cow_read_sector(*chain, 3, read_buf);
    std::cout << "Сектор 3: 0x" << std::hex << static_cast<int>(read_buf[0]) << " (очікується 0xcc)\n";

    // 7. Виконуємо Block Commit у базовий образ
    cow_commit_to_backing(*chain);
    chain.reset(); // Закриваємо файлові дескриптори перед перевіркою

    // 8. Перевіряємо, що в базовому образі сектор #3 тепер містить 0xCC
    int base_fd = ::open(base_img.c_str(), O_RDONLY | O_CLOEXEC);
    ::pread(base_fd, read_buf.data(), SECTOR_SIZE, 3 * SECTOR_SIZE);
    std::cout << "База після commit (сектор 3): 0x" << std::hex << static_cast<int>(read_buf[0]) 
              << " (очікується 0xcc)\n" << std::dec;
    ::close(base_fd);

    // Очищення тестових файлів
    ::unlink(snap_img.c_str());
    ::unlink(base_img.c_str());
    return 0;
}
```
:::

---

## 9. Практичні пастки та крайові випадки при розробці блокових оверлеїв

1. **Неатомарний запис бітової карти та даних (Torn Writes):** якщо процес або живлення вимкнеться після запису байтів сектора, але до збереження оновленого байта бітової карти, дані будуть загублені («фантомний запис»). Якщо ж оновити бітову карту раніше за сектор, після збою оверлей вважатиме заповненим сектор із невизначеним сміттям. Промислові формати (QCOW2) вирішують цю проблему через журнал метаданих або обов'язковий порядок викликів `pwrite(data)` -> `fdatasync()` -> `pwrite(bitmap)` -> `fdatasync()`.
2. **Вимоги до прямого вводу-виводу (Direct I/O):** використання прапорця `O_DIRECT` для обходу кешу хоста вимагає, щоб як вказівник буфера в пам'яті (`posix_memalign`), так і зміщення у файлі були строго кратні розміру фізичного сектора накопичувача (4096 байтів для сучасних дисків Advanced Format).
3. **Конкурентний доступ до батьківського файлу:** відкриття базового образу з правом запису (`O_RDWR`) кількома оверлеями одночасно гарантовано призводить до пошкодження даних. Батьківські шари ланцюжка завжди відкриваються виключно в режимі `O_RDONLY` із встановленням консультативних замків `fcntl(fd, F_SETLK, &fl)` для запобігання випадковій мутації сторонніми процесами.
4. **Масштабування метаданих:** використання простої лінійної бітової карти ефективне для невеликих дисків (для 1 ТБ диска бітова карта займає 256 МБ). Для дисків великого обсягу формати переходить на дворівневі дерева покажчиків L1/L2 з розміром кластера 64 КБ, що скорочує розмір таблиць розміщення в тисячі разів.
5. **Вичерпання дискового простору на хості (ENOSPC Handling):** тонкі дельта-оверлеї ростуть динамічно під час запису. Якщо фізичний розділ хоста переповнюється, черговий виклик `pwrite()` повертає помилку `ENOSPC`. Промислові гіпервізори не повертають помилку I/O всередину гостьової ОС (оскільки це призведе до переведення файлової системи гостя в аварійний режим Read-Only), а автоматично призупиняють виконання vCPU віртуальної машини у стан паузи (`PAUSED_ENOSPC`) та надсилають сповіщення системі моніторингу. Після звільнення або розширення сховища виконання гостя відновлюється без жодного збою.

---

## 10. Порівняння архітектур метаданих: лінійні карти проти дворівневих дерев L1/L2

Хоча лінійна бітова карта, реалізована в нашому навчальному драйвері, забезпечує найпростішу алгоритмічну модель, у промислових форматах на зразок QCOW2 використовується складніша дворівнева радіксна ієрархія (L1 Table та L2 Tables).

### Архітектурні відмінності моделей розміщення

| Характеристика | Лінійна бітова карта (Linear Bitmap) | Дворівневі таблиці L1/L2 (QCOW2) |
| :--- | :--- | :--- |
| **Одиниця виділення** | Окремий сектор (512 байтів) | Кластер (зазвичай 64 КБ = 128 секторів) |
| **Фізичне розміщення даних** | Статичне зміщення `data_offset + LBA*512` | Динамічне розміщення кластерів у хвості файлу |
| **Підтримка розрідженості** | Файл має повний віртуальний розмір | Файл займає лише реально записані кластери |
| **Витрати пам'яті на метадані** | 1 біт на сектор (256 КБ на 1 ГБ диска) | 8 байтів на кластер 64 КБ (128 КБ на 1 ГБ диска) |
| **Підтримка внутрішніх знімків** | Неможлива без клонування всього файлу | Підтримується копіюванням таблиці L1 з CoW-покажчиками |

У дворівневій моделі QCOW2 логічна адреса розкладається на три складові:
1. Старші біти адресують запис у таблиці першого рівня (L1 Table), яка постійно зберігається в оперативній пам'яті хоста.
2. Запис L1 вказує на фізичне зміщення відповідної таблиці другого рівня (L2 Table) у файлі образу. Таблиці L2 підвантажуються в динамічний LRU-кеш гіпервізора за потребою.
3. Запис у таблиці L2 містить 64-бітне зміщення початку кластера на диску, старший біт якого прапорцем позначає стан копіювання при записі (CoW flag).

Така організація дозволяє QCOW2 підтримувати диски обсягом до 2 петабайтів з мінімальними накладними витратами на зберігання невиділених областей.

---

## 11. Асинхронний ввід-вивід та інтеграція з io_uring

У високопродуктивних системах синхронні системні виклики `pread`/`pwrite` створюють неприпустимі накладні витрати через перемикання контексту ядра (context switch overhead). Сучасний блоковий бекенд QEMU транслює операції оверлею через інтерфейс асинхронних черг ядра Linux **`io_uring`**.

```
[vCPU Thread] ──(1. Підготовка SQE: IORING_OP_READV)──> [io_uring Submission Queue]
                                                                  │
                                                     (2. Ядро Linux: асинхронний I/O)
                                                                  │
[vCPU Thread] <──(3. Отримання CQE: результат)──────── [io_uring Completion Queue]
```

1. Драйвер формує векторні запити читання (`struct iovec`), об'єднуючи суміжні незайняті сектори в один неперервний діапазон.
2. Замість виконання `N` блокуючих викликів драйвер додає запис у кільцевий буфер відправки (Submission Queue Entry, SQE).
3. Ядро Linux асинхронно зчитує дані з батьківського файлу або оверлею через прямий доступ до пам'яті (DMA), мінімізуючи навантаження на процесор хоста.
4. Після завершення операції запис у кільцевому буфері завершення (Completion Queue Entry, CQE) пробуджує потік віртуального контролера `virtio-blk`, передаючи прочитані байти в адресний простір гостьової ОС.

---

## 12. Підтримка операцій TRIM/DISCARD та розріджені ділянки

Коли всередині гостьової операційної системи видаляються тимчасові файли або виконується системна утиліта `fstrim(8)`, гостьовий контролер надсилає блокові команди `DISCARD` / `UNMAP`.

Щоб тонкий дельта-оверлей не зберігав застарілі непотрібні сектори і вивільняв фізичне місце на накопичувачі хоста, драйвер реалізує перфорацію дірок (Hole Punching) через системний виклик `fallocate(2)` з прапорцями `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`.

Під час отримання команди скидання сектора:
1. Драйвер обнуляє відповідний біт у бітовій карті (`bitmap[sector / 8] &= ~(1 << (sector % 8))`).
2. Викликається `fallocate(fd, FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE, offset, SECTOR_SIZE)`, змушуючи файлову систему хоста вивільнити фізичні блоки носія.
3. При наступному читанні цього сектора драйвер автоматично повернеться до читання з батьківського базового образу, відновлюючи первинний стан без зайвих витрат дискової ємності.

---

## 13. Оптимізація сканування бітової карти через машинні інструкції POPCNT та CLZ

Під час виконання послідовного читання великих блоків даних (наприклад, потокове читання 1 мегабайта = 2048 секторів) побітова перевірка через функцію `bitmap_test` у циклі створює 2048 ітерацій з розгалуженнями процесора.

Для максимальної швидкодії сучасні драйвери сканують бітову карту машинними машинними словами (64-бітними регістрами `uint64_t`):
- Якщо все 64-бітне слово дорівнює `0x0000000000000000`, це означає, що весь діапазон із 64 секторів (32 КБ) гарантовано не виділений в оверлеї. Драйвер миттєво зчитує всі 32 КБ з батьківського файлу одним прямим системним викликом, минаючи 64 окремі перевірки.
- Якщо 64-бітне слово дорівнює `0xFFFFFFFFFFFFFFFF`, усі 64 сектори повністю записані в активному оверлеї і зчитуються з нього суцільним блоком.
- Для змішаних слів застосовують апаратну процесорну інструкцію підрахунку хвостових нулів `_tzcnt_u64` (або вбудовану функцію компілятора `__builtin_ctzll`), яка за один такт процесора знаходить зміщення першого модифікованого сектора.

Така векторна оптимізація збільшує пропускну здатність читання через шар оверлею в 10–15 разів, наближаючи продуктивність віртуального диска до швидкості прямого доступу до фізичного накопичувача.
