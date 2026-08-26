# ⚙️ Парсер і валідатор блоків UF2

Коли мікроконтролер переводиться у режим завантажувача й під'єднується до комп'ютера як USB-накопичувач, операційна система розпізнає його як стандартний блоковий пристрій класу USB Mass Storage (MSC). Під час копіювання файлу прошивки провідником або терміналом операційна система надсилає дані не суцільним двійковим потоком, а окремими дисковими секторами фіксованого розміру 512 байтів через команди протоколу SCSI `WRITE (10)`.

Оперативна пам'ять типового мікроконтролера обмежена десятками чи сотнями кілобайтів. Образ прошивки сучасного застосунку може займати від одного до кількох мегабайтів. Завантажувач не має фізичної змоги зберегти весь файл образу в оперативній пам'яті для подальшого розбору й запису. Він змушений обробляти кожен 512-байтний дисковий сектор безпосередньо в момент надходження USB-пакета — розпізнавати службові метадані, перевіряти цілісність, вилучати корисне навантаження й відправляти байти у контролер Flash-пам'яті на льоту.

Формат UF2 (англ. *USB Flashing Format*) створено спеціально для такого потокового безбуферного оновлення. Кожні 256 байтів корисного двійкового коду упаковуються у повністю самодостатній 512-байтний блок, де зашито повний набір метаданих для однозначного запису без звернення до інших секторів.

```
+-----------------------------------------------------------------------+
|  magicStart0  |  magicStart1  |     flags     |      targetAddr       |
|    (4 байта)  |    (4 байта)  |   (4 байта)   |       (4 байта)       |
+---------------+---------------+---------------+-----------------------+
|  payloadSize  |    blockNo    |   numBlocks   | familyID / fileSize   |
|   (256 байт)  |   (індекс)    |  (всього N)   |  (архітектура чипа)   |
+---------------+---------------+---------------+-----------------------+
|                                                                       |
|              data[476] (256 байт прошивки + 220 байт паддінгу)        |
|                                                                       |
+-----------------------------------------------------------------------+
|                               magicEnd                                |
|                               (4 байта)                               |
+-----------------------------------------------------------------------+
```

### Анатомія та інваріанти блоку UF2

Кожен блок UF2 має суворий бінарний контракт, що займає рівно 512 байтів — точний розмір логічного сектора емульованого диска FAT12:
- `magicStart0` (`0x0A324655` — ASCII-символи `"UF2\n"`) та `magicStart1` (`0x9E5D5157`): дві 32-бітні константи на початку блоку, що гарантують відсутність сміття на шині.
- `flags`: бітова маска конфігурації. Найважливіший біт — `0x00002000` (`familyID present`), який сигналізує, що поле на зсуві 28 містить числовий ідентифікатор цільової платформи, а не розмір файлу.
- `targetAddr`: абсолютна адреса у Flash-пам'яті мікроконтролера, куди має бути записаний поточний шматок коду (наприклад, `0x10000000` для зовнішньої QSPI Flash на RP2040 або `0x08000000` для внутрішньої Flash на STM32).
- `payloadSize`: реальна кількість корисних байтів у масиві даних. У стандартних прошивках це число дорівнює 256. Решта байтів масиву `data[476]` заповнюються нулями (паддінг).
- `blockNo`: порядковий номер блоку, починаючи від 0.
- `numBlocks`: загальна кількість блоків у всьому образі прошивки.
- `familyID`: унікальне 32-бітне число сімейства мікроконтролера (наприклад, `0xe48ff56e` для Raspberry Pi RP2040, `0x00ff6919` для STM32F4, `0xc47e5767` для ESP32-S3).
- `magicEnd` (`0x0AB16414`): фінальна магічна мітка в останніх 4 байтах сектора, яка підтверджує, що весь 512-байтний пакет доставлено без обривів.

### Завдання: потокова валідація та вилучення корисних даних

Необхідно реалізувати обробник дискового сектора, який викликається стеком USB MSC під час виконання SCSI-команди `WRITE (10)`. Функція повинна перевіряти сирий буфер, відсікати чужі або пошкоджені файли, контролювати допустимий діапазон адрес пам'яті й повертати вказівник на чисті байти прошивки для безпосереднього запису у Flash.

Функція забезпечує апаратний захист від чотирьох критичних збоїв:
1. Пошкодження даних при передачі або неповна передача сектора через USB-кабель (звірка сигнатур `magicStart0`, `magicStart1`, `magicEnd`).
2. Спроба користувача випадково перетягнути бінарник від іншого мікроконтролера (контроль поля `familyID`).
3. Спроба перезапису критичних завантажувальних або конфігураційних областей (перевірка діапазону `targetAddr` відносно меж Flash).
4. Переповнення буфера через некоректне значення `payloadSize` (> 476 байтів).

### Реалізація: C та ідіоматичний C++

Нижче наведено модулі валідатора. У версії на C++ використовується `std::span` для виключення помилок адресного розрахунку, `std::expected` для повернення строгих типізованих статусів без магічних кодів помилок та `constexpr` константи замість небезпечних директив препроцесора `#define`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define UF2_MAGIC_START0   0x0A324655UL  // "UF2\n"
#define UF2_MAGIC_START1   0x9E5D5157UL
#define UF2_MAGIC_END      0x0AB16414UL
#define UF2_FLAG_FAMILY_ID 0x00002000UL
#define UF2_BLOCK_SIZE     512
#define UF2_MAX_PAYLOAD    476

typedef enum {
    UF2_PARSE_OK = 0,
    UF2_ERR_NULL_PTR,
    UF2_ERR_BAD_MAGIC_START,
    UF2_ERR_BAD_MAGIC_END,
    UF2_ERR_FAMILY_MISMATCH,
    UF2_ERR_PAYLOAD_TOO_LARGE,
    UF2_ERR_INVALID_ADDRESS,
    UF2_ERR_TOTAL_BLOCKS_ZERO
} uf2_status_t;

typedef struct {
    uint32_t magic_start0;
    uint32_t magic_start1;
    uint32_t flags;
    uint32_t target_addr;
    uint32_t payload_size;
    uint32_t block_no;
    uint32_t num_blocks;
    uint32_t family_id;
    uint8_t  data[UF2_MAX_PAYLOAD];
    uint32_t magic_end;
} __attribute__((packed)) uf2_raw_block_t;

typedef struct {
    uint32_t target_address;
    uint32_t payload_length;
    uint32_t block_index;
    uint32_t total_blocks;
    const uint8_t *data_ptr;
} uf2_block_info_t;

uf2_status_t uf2_parse_and_validate_block(
    const uint8_t *sector_buf,
    uint32_t expected_family_id,
    uint32_t flash_start_addr,
    uint32_t flash_size_bytes,
    uf2_block_info_t *out_info
) {
    if (!sector_buf || !out_info) {
        return UF2_ERR_NULL_PTR;
    }

    const uf2_raw_block_t *blk = (const uf2_raw_block_t *)sector_buf;

    // Перевірка магічних сигнатур початку блоку
    if (blk->magic_start0 != UF2_MAGIC_START0 || blk->magic_start1 != UF2_MAGIC_START1) {
        return UF2_ERR_BAD_MAGIC_START;
    }

    // Перевірка магічної сигнатури кінця блоку
    if (blk->magic_end != UF2_MAGIC_END) {
        return UF2_ERR_BAD_MAGIC_END;
    }

    // Перевірка Family ID, якщо виставлено прапорець сімейства чіпа
    if ((blk->flags & UF2_FLAG_FAMILY_ID) != 0) {
        if (blk->family_id != expected_family_id) {
            return UF2_ERR_FAMILY_MISMATCH;
        }
    }

    // Перевірка ліміту корисного навантаження (типово 256 байт)
    if (blk->payload_size == 0 || blk->payload_size > UF2_MAX_PAYLOAD) {
        return UF2_ERR_PAYLOAD_TOO_LARGE;
    }

    if (blk->num_blocks == 0) {
        return UF2_ERR_TOTAL_BLOCKS_ZERO;
    }

    // Перевірка діапазону адрес Flash пам'яті
    uint32_t flash_end_addr = flash_start_addr + flash_size_bytes;
    if (blk->target_addr < flash_start_addr ||
        (blk->target_addr + blk->payload_size) > flash_end_addr) {
        return UF2_ERR_INVALID_ADDRESS;
    }

    out_info->target_address = blk->target_addr;
    out_info->payload_length = blk->payload_size;
    out_info->block_index = blk->block_no;
    out_info->total_blocks = blk->num_blocks;
    out_info->data_ptr = blk->data;

    return UF2_PARSE_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace uf2 {

inline constexpr uint32_t MagicStart0   = 0x0A324655UL;  // "UF2\n"
inline constexpr uint32_t MagicStart1   = 0x9E5D5157UL;
inline constexpr uint32_t MagicEnd      = 0x0AB16414UL;
inline constexpr uint32_t FlagFamilyId  = 0x00002000UL;
inline constexpr size_t   BlockSize     = 512;
inline constexpr size_t   MaxPayload    = 476;

enum class ParseError : uint8_t {
    BadBufferLength,
    BadMagicStart,
    BadMagicEnd,
    FamilyMismatch,
    PayloadTooLarge,
    InvalidAddress,
    TotalBlocksZero
};

struct BlockInfo {
    uint32_t targetAddress;
    uint32_t blockIndex;
    uint32_t totalBlocks;
    std::span<const uint8_t> payload;
};

struct [[gnu::packed]] RawBlock {
    uint32_t magicStart0;
    uint32_t magicStart1;
    uint32_t flags;
    uint32_t targetAddr;
    uint32_t payloadSize;
    uint32_t blockNo;
    uint32_t numBlocks;
    uint32_t familyId;
    uint8_t  data[MaxPayload];
    uint32_t magicEnd;
};

[[nodiscard]] std::expected<BlockInfo, ParseError> parseAndValidateBlock(
    std::span<const uint8_t, BlockSize> sector,
    uint32_t expectedFamilyId,
    uint32_t flashStartAddr,
    uint32_t flashSizeBytes
) noexcept {
    const auto* blk = reinterpret_cast<const RawBlock*>(sector.data());

    if (blk->magicStart0 != MagicStart0 || blk->magicStart1 != MagicStart1) {
        return std::unexpected(ParseError::BadMagicStart);
    }

    if (blk->magicEnd != MagicEnd) {
        return std::unexpected(ParseError::BadMagicEnd);
    }

    if ((blk->flags & FlagFamilyId) != 0) {
        if (blk->familyId != expectedFamilyId) {
            return std::unexpected(ParseError::FamilyMismatch);
        }
    }

    if (blk->payloadSize == 0 || blk->payloadSize > MaxPayload) {
        return std::unexpected(ParseError::PayloadTooLarge);
    }

    if (blk->numBlocks == 0) {
        return std::unexpected(ParseError::TotalBlocksZero);
    }

    const uint32_t flashEndAddr = flashStartAddr + flashSizeBytes;
    if (blk->targetAddr < flashStartAddr ||
        (blk->targetAddr + blk->payloadSize) > flashEndAddr) {
        return std::unexpected(ParseError::InvalidAddress);
    }

    return BlockInfo{
        .targetAddress = blk->targetAddr,
        .blockIndex = blk->blockNo,
        .totalBlocks = blk->numBlocks,
        .payload = std::span<const uint8_t>(blk->data, blk->payloadSize)
    };
}

} // namespace uf2
```
:::

### Інженерні пастки та тонкощі роботи у вбудованих системах

1. **Непослідовна доставка дискових секторів операційними системами.** Операційні системи (зокрема Windows під час роботи кешування запису або macOS при роботі служби індексації Spotlight) записують файли на накопичувач не строго від 0-го до N-го сектора. Файловий менеджер може спершу створити службові записи каталогу (`.DS_Store`, `Thumbs.db`), оновити секційну таблицю FAT, а самі блоки `.uf2` надсилати в довільному порядку. Завантажувач **ніколи не повинен перевіряти умову `block_no == previous_block_no + 1`**. Кожен сектор пишеться у Flash виключно за власною адресою `target_addr`.
2. **Невідповідність гранул стирання та запису Flash.** Фізична NOR Flash пам'ять стирається секторами по 4096 байтів (4 КБ), тоді як блок UF2 містить лише 256 байтів корисних даних. Якщо завантажувач стиратиме 4-кілобайтний сектор перед кожним записом блоку UF2, він неминуче знищить раніше записані сусідні 256-байтні шматки. Тому завантажувач веде облік адрес і виконує команду стирання `Sector Erase (4KB)` **лише тоді, коли адреса `target_addr` перетинає межу чергових 4096 байтів** (`target_addr % 4096 == 0`).
3. **Фільтрація службових секторів ОС без повідомлення про помилку.** Коли операційна система намагається створити системні службові файли або модифікувати таблицю розміщення файлів FAT, вона шле звичайні 512-байтні сектори. Оскільки ці сектори не містять магічних констант `UF2_MAGIC_START0` та `UF2_MAGIC_END`, функція валідації повертає помилку `UF2_ERR_BAD_MAGIC_START`. На рівні обробника SCSI завантажувач зобов'язаний повернути статус `GOOD` (успіх), просто проігнорувавши запис у Flash. Якщо повернути статус помилки `CHECK_CONDITION`, операційна система перерве операцію копіювання файлу й повідомить користувача про збій накопичувача.
4. **Контроль завершення оновлення через бітову карту.** Щоб точно знати, коли прошивку завантажено повністю, завантажувач утримує в оперативній пам'яті бітову маску (наприклад, масив `uint32_t block_mask[N/32]`), де кожен біт позначає успішно записаний блок. Лише коли всі `num_blocks` бітів виставлені в одиницю, завантажувач завершує транзакцію: скидає кеші ліній даних, коректно відключає внутрішній USB-контролер (ініціюючи USB disconnect) і викликає системне перезавантаження через функцію ядра `NVIC_SystemReset()`.
