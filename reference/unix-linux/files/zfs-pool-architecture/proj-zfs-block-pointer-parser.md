# ⚙️ Практичний розбір структури Вказівника Блоку (blkptr_t) та обчислення Fletcher4

Цей проєкт присвячено практичній реалізації розбору низькорівневої структури Вказівника Блоку (Block Pointer — `blkptr_t`) ZFS мовами C та C++, витягуванню віртуальних адрес даних (DVA), декодуванню бітових полів властивостей та обчисленню 256-бітної контрольної суми за допомогою алгоритму Fletcher4.

## Архітектурний контекст `blkptr_t`

Вказівник Блоку (`blkptr_t`) — це фундаментальна 128-байтова структура даних, яка слугує ребрами самовідновлюваного дерева Меркла в ZFS. Кожен вузол метаданих (dnode або непрямий блок) містить масив вказівників `blkptr_t`, що вказують на дитячі блоки даних або нижчі рівні метаданих.

Структура `blkptr_t` виконує три критичні функції в архітектурі пулу:

1. **Багаторазова фізична адресація (Multi-DVA Redundancy):** Кожен `blkptr_t` може зберігати до трьох незалежних Віртуальних Адрес Даних (**DVA — Data Virtual Address**). Це дозволяє реалізовувати дзеркалювання або збереження кількох копій блоку на рівні окремого вказівника (`copies=1..3`), навіть якщо сам VDEV не є дзеркалом. Перше поле `dva[0]` вказує на основну копію блоку, а `dva[1]` та `dva[2]` зберігають дублюючі фізичні адреси на інших VDEV або в інших Metaslab.
2. **Управління виділеним та логічним простором:** Зберігає логічний несжиманий розмір блоку (LSIZE), фізичний стиснутий розмір (PSIZE) та загальний виділений обсяг секторів на диску (ASIZE). Завдяки цьому SPA та DMU точно знають, скільки пам'яті потрібно виділити в RAM для розпакованого блоку й скільки байтів прочитати з дискового носія. Співвідношення LSIZE до PSIZE дає точний коефіцієнт стиснення даного конкретного блоку.
3. **Захист цілісності та транзакційний контроль:** Зберігає 256-бітний хеш вмісту дитячого блоку (обчислений алгоритмами Fletcher4, SHA-256 або BLAKE3) та номер транзакційної групи народження блоку (**Birth TXG**). Наявність Birth TXG дозволяє ZFS порівнювати вік блоків під час реалізації CoW-снапшотів та інкрементальної реплікації `zfs send/receive`.

## Деталізація полів структури `blkptr_t`

Структура `blkptr_t` має фіксований розмір 128 байтів (1024 біти) й розбита на наступні поля:

- `blk_dva[3]` (48 байтів): Масив із трьох елементів `dva_t`. Кожен елемент DVA складається з двох 64-бітних слів: `dva_word0` зберігає 32-бітний ідентифікатор VDEV та 32-бітний зсув у секторах; `dva_word1` містить 24-бітний виділений розмір (ASIZE) та 40 бітів прапорців (включаючи стан GANG-блоків).
- `blk_prop` (8 байтів): Упаковане 64-бітне бітове поле властивостей блоку:
  - Біти 0..15: Логічний розмір minus 1 `(LSIZE / 512) - 1`.
  - Біти 16..31: Фізичний розмір minus 1 `(PSIZE / 512) - 1`.
  - Біти 32..39: Ідентифікатор алгоритму стиснення (0 = uncompressed, 2 = lzjb, 15 = lz4, 16 = zstd).
  - Біти 40..47: Ідентифікатор алгоритму контрольної суми (2 = off, 3 = fletcher2, 4 = fletcher4, 5 = sha256, 14 = blake3).
  - Біт 63: Порядок байтів (0 = Little-Endian, 1 = Big-Endian).
- `blk_pad[2]` (16 байтів): Зарезервовані нульові поля для майбутніх розширень протоколу ZFS.
- `blk_birth` (8 байтів): Порядковий номер транзакційної групи (TXG), у якій даний блок був фізично записаний на диск.
- `blk_fill` (8 байтів): Лічильник заповнених об'єктів dnode для непрямих блоків метаданих.
- `blk_cksum` (32 байти): 256-бітна контрольна сума вмісту дитячого блоку.

## Механізм обчислення контрольної суми Fletcher4

Алгоритм Fletcher4 в ZFS — це 256-бітна адаптація класичного алгоритму Флетчера, оптимізована для обробки 64-бітних слів. Замість обчислення повільних криптографічних хешів (таких як SHA-256), Fletcher4 виконує чотири накопичувальні паралельні суми за модулем `2^64`:

```
A = ∑ data[i]
B = ∑ A[i]
C = ∑ B[i]
D = ∑ C[i]
```

Завдяки чотириразовому накопиченню сум Fletcher4 виявляє будь-які поодинокі, подвійні та багатобітові зсуви, транспозиції слів та серії нульових секторів з мінімальним навантаженням на центральний процесор (понад 5 ГБ/с на ядро CPU). У сучасних ядрах Linux використання векторних інструкцій AVX-512 та ARM NEON дозволяє обчислювати Fletcher4 на швидкості системної шини RAM.

## Код розбору `blkptr_t` та перевірки Fletcher4

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Структура Віртуальної Адреси Даних (DVA - 16 байтів) */
typedef struct dva {
    uint64_t dva_word0; /* vdev (32 біти) | offset (32 біти) */
    uint64_t dva_word1; /* asize (24 біти) | flags (40 бітів) */
} dva_t;

/* Розширене обчислення контрольної суми Fletcher4 (256 бітів) */
typedef struct zio_cksum {
    uint64_t zc_word[4];
} zio_cksum_t;

/* Повна структура Вказівника Блоку ZFS (128 байтів) */
typedef struct blkptr {
    dva_t        blk_dva[3];    /* До 3 віртуальних адрес носія (48 байтів) */
    uint64_t     blk_prop;      /* Властивості: endian, compression, checksum, type, lsize, psize */
    uint64_t     blk_pad[2];    /* Зарезервовано */
    uint64_t     blk_birth;     /* Порядковий номер транзакції створення (Birth TXG) */
    uint64_t     blk_fill;      /* Лічильник заповнених dnodes */
    zio_cksum_t  blk_cksum;     /* 256-бітна контрольна сума вмісту дитячого блоку */
} blkptr_t;

/* Витягування полів із бітового поля blk_prop */
static inline uint32_t blkptr_get_lsize(const blkptr_t *bp) {
    return (uint32_t)((bp->blk_prop & 0xFFFFULL) + 1) * 512;
}

static inline uint32_t blkptr_get_psize(const blkptr_t *bp) {
    return (uint32_t)(((bp->blk_prop >> 16) & 0xFFFFULL) + 1) * 512;
}

static inline uint8_t blkptr_get_checksum_type(const blkptr_t *bp) {
    return (uint8_t)((bp->blk_prop >> 40) & 0xFFULL);
}

static inline uint8_t blkptr_get_compression_type(const blkptr_t *bp) {
    return (uint8_t)((bp->blk_prop >> 32) & 0xFFULL);
}

/* 
 * Алгоритм Fletcher4: 256-бітне накопичувальне підсумовування 64-бітних слів.
 * Вважається найшвидшим алгоритмом перевірки цілісності ZFS.
 */
zio_cksum_t zio_checksum_fletcher4(const uint64_t *buf, uint64_t size_bytes) {
    zio_cksum_t zc = {{0, 0, 0, 0}};
    uint64_t words = size_bytes / sizeof(uint64_t);
    uint64_t a = 0, b = 0, c = 0, d = 0;

    for (uint64_t i = 0; i < words; i++) {
        a += buf[i];
        b += a;
        c += b;
        d += c;
    }

    zc.zc_word[0] = a;
    zc.zc_word[1] = b;
    zc.zc_word[2] = c;
    zc.zc_word[3] = d;
    return zc;
}

int main(void) {
    blkptr_t bp;
    memset(&bp, 0, sizeof(bp));

    /* Налаштування тестового вказівника блоку */
    bp.blk_prop = (127ULL) | (63ULL << 16) | (2ULL << 32) | (7ULL << 40); /* LSIZE=64KB, PSIZE=32KB, LZ4, Fletcher4 */
    bp.blk_birth = 1042500ULL;
    bp.blk_dva[0].dva_word0 = (1ULL << 32) | 0x800000ULL; /* VDEV=1, Offset=8MB */

    printf("=== ДЕКОДУВАННЯ ZFS BLKPTR_T ===\n");
    printf("Логічний розмір (LSIZE): %u байтів\n", blkptr_get_lsize(&bp));
    printf("Фізичний розмір (PSIZE): %u байтів\n", blkptr_get_psize(&bp));
    printf("Тег стиснення: %u (LZ4)\n", blkptr_get_compression_type(&bp));
    printf("Тег контрольної суми: %u (Fletcher4)\n", blkptr_get_checksum_type(&bp));
    printf("Birth TXG: %lu\n", bp.blk_birth);
    printf("DVA[0] VDEV ID: %u, Offset: 0x%lx\n", 
           (uint32_t)(bp.blk_dva[0].dva_word0 >> 32), 
           (unsigned long)(bp.blk_dva[0].dva_word0 & 0xFFFFFFFFULL));

    /* Тестовий блок даних 1024 байти (128 слів по 64 біти) */
    uint64_t sample_data[128];
    for (int i = 0; i < 128; i++) {
        sample_data[i] = 0xDEADBEEF00000000ULL | (uint64_t)i;
    }

    zio_cksum_t sum = zio_checksum_fletcher4(sample_data, sizeof(sample_data));
    printf("\n=== ОБЧИСЛЕНУ ЧЕКСУМУ FLETCHER4 ===\n");
    printf("ZC[0]: 0x%016lx\nZC[1]: 0x%016lx\nZC[2]: 0x%016lx\nZC[3]: 0x%016lx\n",
           sum.zc_word[0], sum.zc_word[1], sum.zc_word[2], sum.zc_word[3]);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <cstdint>
#include <iomanip>
#include <expected>
#include <system_error>

namespace zfs {

struct DataVirtualAddress {
    uint32_t vdev_id{0};
    uint64_t offset_sectors{0};
    uint32_t allocated_sectors{0};

    [[nodiscard]] uint64_t byte_offset() const noexcept {
        return offset_sectors * 512ULL;
    }
};

struct Checksum256 {
    std::array<uint64_t, 4> words{0, 0, 0, 0};

    bool operator==(const Checksum256& other) const noexcept = default;
};

enum class CompressionAlgorithm : uint8_t {
    Inherit = 0,
    On = 1,
    Lzjb = 2,
    Empty = 3,
    Gzip = 4,
    Lz4 = 15,
    Zstd = 16
};

enum class ChecksumAlgorithm : uint8_t {
    Inherit = 0,
    On = 1,
    Off = 2,
    Fletcher2 = 3,
    Fletcher4 = 4,
    Sha256 = 5,
    Blake3 = 14
};

class BlockPointer {
private:
    std::array<DataVirtualAddress, 3> dva_{};
    uint32_t logical_size_bytes_{0};
    uint32_t physical_size_bytes_{0};
    CompressionAlgorithm compression_{CompressionAlgorithm::Lz4};
    ChecksumAlgorithm checksum_{ChecksumAlgorithm::Fletcher4};
    uint64_t birth_txg_{0};
    Checksum256 expected_checksum_{};

public:
    BlockPointer(uint32_t lsize, uint32_t psize, CompressionAlgorithm comp, ChecksumAlgorithm cksum, uint64_t txg)
        : logical_size_bytes_(lsize), physical_size_bytes_(psize), compression_(comp), checksum_(cksum), birth_txg_(txg) {}

    void set_dva(size_t index, DataVirtualAddress dva) {
        if (index < dva_.size()) {
            dva_[index] = dva;
        }
    }

    [[nodiscard]] uint32_t logical_size() const noexcept { return logical_size_bytes_; }
    [[nodiscard]] uint32_t physical_size() const noexcept { return physical_size_bytes_; }
    [[nodiscard]] CompressionAlgorithm compression() const noexcept { return compression_; }
    [[nodiscard]] ChecksumAlgorithm checksum_type() const noexcept { return checksum_; }
    [[nodiscard]] uint64_t birth_txg() const noexcept { return birth_txg_; }
    [[nodiscard]] const auto& dvas() const noexcept { return dva_; }

    void set_expected_checksum(Checksum256 cksum) noexcept { expected_checksum_ = cksum; }
    [[nodiscard]] Checksum256 expected_checksum() const noexcept { return expected_checksum_; }
};

class Fletcher4Calculator {
public:
    [[nodiscard]] static Checksum256 compute(std::span<const uint64_t> data) noexcept {
        uint64_t a = 0, b = 0, c = 0, d = 0;
        for (const uint64_t val : data) {
            a += val;
            b += a;
            c += b;
            d += c;
        }
        return Checksum256{{a, b, c, d}};
    }

    [[nodiscard]] static std::expected<bool, std::errc> verify(std::span<const uint64_t> data, const Checksum256& expected) noexcept {
        if (data.empty()) {
            return std::unexpected(std::errc::invalid_argument);
        }
        const Checksum256 computed = compute(data);
        return (computed == expected);
    }
};

} // namespace zfs

int main() {
    using namespace zfs;

    BlockPointer bp(65536, 32768, CompressionAlgorithm::Lz4, ChecksumAlgorithm::Fletcher4, 1042500ULL);
    bp.set_dva(0, DataVirtualAddress{.vdev_id = 1, .offset_sectors = 16384, .allocated_sectors = 64});

    std::cout << "=== OOP ОБГОРТКА ZFS BLKPTR_T (C++23) ===\n";
    std::cout << "Логічний розмір: " << bp.logical_size() << " B\n";
    std::cout << "Фізичний розмір: " << bp.physical_size() << " B\n";
    std::cout << "Birth TXG: " << bp.birth_txg() << "\n";
    std::cout << "DVA[0] VDEV: " << bp.dvas()[0].vdev_id 
              << ", Байт-зсув: 0x" << std::hex << bp.dvas()[0].byte_offset() << std::dec << "\n";

    std::vector<uint64_t> payload(128);
    for (size_t i = 0; i < payload.size(); ++i) {
        payload[i] = 0xDEADBEEF00000000ULL | i;
    }

    const Checksum256 computed = Fletcher4Calculator::compute(payload);
    bp.set_expected_checksum(computed);

    const auto verification_result = Fletcher4Calculator::verify(payload, bp.expected_checksum());
    if (verification_result.has_value() && verification_result.value()) {
        std::cout << "\nСтатус цілісності блоку: УСПІШНО (Fletcher4 Збігається)\n";
        std::cout << "ZC[0]: 0x" << std::hex << std::setw(16) << std::setfill('0') << computed.words[0] << "\n";
    } else {
        std::cout << "\nПомилка цілісності блоку! (Bit Rot / Data Corruption)\n";
    }

    return 0;
}
```
:::

## Аналіз реалізації, порядку байтів та вирівнювання

При роботі зі структурами `blkptr_t` на реальних дискових носіях необхідно враховувати два критичних системних аспекти:

1. **Порядок байтів (Endianness):** ZFS є кросплатформною файловою системою. Якщо пул був створений на сервері SPARC (Big-Endian), а потім імпортований на платформу x86_64 або ARM64 (Little-Endian), найвищий біт поля `blk_prop` буде встановлений в 1. Програма розбору повинна перевіряти цей біт і виконувати порядок інверсії байтів (`bswap64`) для всіх 64-бітних полів `blkptr_t` перед їх інтерпретацією.
2. **Вирівнювання пам'яті (Memory Alignment):** Алгоритм `zio_checksum_fletcher4` вимагає, щоб буфер даних був вирівняний по 8-байтовій межі (`uint64_t`). Передача невирівняного буфера в SIMD-оптимізовану версію Fletcher4 (AVX2/AVX-512) призведе до паніки ядра або збою `SIGBUS` у просторі користувача.
3. **Обробка помилок та реакція підсистеми ZIO:** Якщо обчислена значенням `Fletcher4Calculator::compute()` контрольна сума не збігається з вмістом `blk_cksum`, рівень I/O ZFS (ZIO) скасовує передачу даного блоку вищим шарам і формує внутрішній запит на самовідновлення (self-healing read) із дублюючих DVA або повертає код `ECKSUM`.
