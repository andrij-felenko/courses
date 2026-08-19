# ⚙️ Драйвер SPI/QSPI NOR Flash та налаштування режиму XIP

Керування мікросхемою NOR Flash на рівні мікроконтролера вимагає точного дотримання часових діаграм, станів внутрішнього кінцевого автомата чипа та синхронізації з високовольтними генераторами підкачки заряду. На відміну від статичної пам'яті SRAM, у Flash не можна просто виставити адресу на шину й безпосередньо перезаписати байт: перед кожним записом необхідно зняти апаратне блокування засувки запису (Write Enable), вирівнювати операції за межами 256-байтних фізичних сторінок, враховувати затримки ввімкнення внутрішніх помпових перетворювачів напруги та періодично опитувати регістри стану. Ця практична вставка містить робочий низькорівневий драйвер для стандартних мікросхем SPI/QSPI NOR Flash (сумісний із JEDEC стандартами Winbond W25Q, Macronix MX25, Spansion/Infineon S25FL, GigaDevice GD25), аналізує стандарт автовизначення параметрів SFDP (JESD216), механізми 32-бітної адресації, асинхронні DMA-передачі, захист секторів та розбирає конфігурацію апаратного режиму прямого виконання коду (Execute-in-Place, XIP).

### Стандартна командна модель JEDEC SPI Flash

Більшість сучасних виробників NOR Flash підтримують уніфікований набір команд послідовного протоколу SPI, Dual-SPI та Quad-SPI. Кожна командна транзакція починається зі спадного фронту сигналу вибору мікросхеми `/CS` (Chip Select), після чого по тактовій лінії `SCK` передається однобайтний код інструкції.

Внутрішній логічний автомат чипа дешифрує код команди на першому спадному фронті восьмого тактового імпульсу і конфігурує внутрішні комутатори матриці для відповідної операції:

| Код команди | Назва операції | Формат аргументів | Призначення |
| :--- | :--- | :--- | :--- |
| `0x9F` | Read JEDEC ID | Немає (читання 3 байтів) | Отримання Manufacturer ID, Memory Type, Capacity |
| `0x06` | Write Enable (WREN) | Немає | Встановлення біта WEL (Write Enable Latch) перед записом/стиранням |
| `0x04` | Write Disable (WRDI) | Немає | Скидання біта WEL та захист від випадкової модифікації |
| `0x05` | Read Status Register-1 | Читання 1 байта (постійний потік)| Опитування бітів WIP (Write in Progress) та WEL |
| `0x35` | Read Status Register-2 | Читання 1 байта | Перевірка біта Quad Enable (QE) та захисту блоків |
| `0x01` | Write Status Register-1 | 1 або 2 байти даних | Встановлення бітів конфігурації та захисту |
| `0x03` | Read Data | 3 або 4 байти адреси | Звичайне зчитування байтів (до 33–50 МГц) |
| `0x0B` | Fast Read | Адреса + 1 Dummy-байт (8 тактів) | Високошвидкісне зчитування (до 104–133 МГц) |
| `0xEB` | Fast Read Quad I/O | Адреса (4-bit) + 4–6 Dummy тактів | Читання в режимі QSPI (4 біти за такт, XIP) |
| `0x02` | Page Program | 3–4 байти адреси + 1–256 байтів | Запис до 256 байтів у межах однієї фізичної сторінки |
| `0x20` | Sector Erase (4 KB) | 3 або 4 байти адреси | Стирання сектора 4 КБ (усі біти перетворюються на «1») |
| `0x52` | Block Erase (32 KB) | 3 або 4 байти адреси | Стирання половини блоку 32 КБ |
| `0xD8` | Block Erase (64 KB) | 3 або 4 байти адреси | Стирання повного блоку 64 КБ |
| `0xC7` / `0x60` | Chip Erase | Немає | Повне стирання всього масиву мікросхеми |
| `0x75` | Erase / Program Suspend | Немає | Тимчасове призупинення стирання для термінового читання |
| `0x7A` | Erase / Program Resume | Немає | Відновлення раніше призупиненого стирання |
| `0xB7` | Enter 4-Byte Address Mode | Немає | Перемикання на 32-бітну адресацію для чипів >16 МБ |
| `0xE9` | Exit 4-Byte Address Mode | Немає | Повернення до стандартної 24-бітної адресації |
| `0x5A` | Read SFDP Register | 3 байти адреси + 1 Dummy-байт | Читання стандартизованої таблиці параметрів чипа |

---

### Робота внутрішнього автомата запису та помпи заряду

Програмування та стирання комірок NOR Flash вимагають високих напруг (`+9..+12 В` для керуючих затворів та `+5 В` для стоків), які генеруються внутрішніми інтегрованими помпами заряду (Charge Pumps) на перемикальних конденсаторах. Коли хост надсилає команду `Sector Erase (0x20)` або `Page Program (0x02)`, всередині чипа запускається автономний апаратний цикл:

1. **Фаза увімкнення та стабілізації помпи:** генератор високої напруги виходить на робочий рівень за `10–50 мкс`.
2. **Фаза подачі високовольтного імпульсу:** на матрицю подається імпульс напруги фіксованої тривалості (для CHE — мікросекунди, для FN — мілісекунди).
3. **Внутрішня верифікація (Internal Program/Erase Verify):** контролер мікросхеми автономно зчитує змінені комірки за допомогою внутрішнього компаратора і порівнює порогову напругу із закладеним опорним рівнем. Якщо поріг не досяг норми, автомат генерує повторний імпульс.
4. **Завершення операції:** після досягнення цільового заряду помпа вимикається, високовольтні шини розряджаються на землю, а біт `WIP (Write In Progress)` у регістрі стану скидається в `0`.

Оскільки мікросхема під час виконання цього циклу фізично не здатна обслуговувати звичайні запити читання матриці, єдиною дозволеною операцією на шині SPI залишається періодичне опитування регістра стану командою `0x05`.

---

### Реалізація драйвера NOR Flash у C та C++

Наведений нижче драйвер містить повний стек функцій: ініціалізацію з перевіркою JEDEC ID, очікування готовності (WIP polling), стирання сектора, безпечний посторінковий запис довільного масиву даних (із коректним розбиттям на 256-байтні сторінки без переповнення) та швидке зчитування.

:::tabs
```c
/* nor_flash.h — Низькорівневий драйвер SPI NOR Flash мовою C */
#ifndef NOR_FLASH_H
#define NOR_FLASH_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define NOR_PAGE_SIZE       256U
#define NOR_SECTOR_SIZE     4096U
#define NOR_BLOCK_SIZE      65536U

#define CMD_READ_ID         0x9FU
#define CMD_WRITE_ENABLE    0x06U
#define CMD_WRITE_DISABLE   0x04U
#define CMD_READ_STATUS_1   0x05U
#define CMD_READ_DATA       0x03U
#define CMD_FAST_READ       0x0BU
#define CMD_PAGE_PROGRAM    0x02U
#define CMD_SECTOR_ERASE_4K 0x20U
#define CMD_BLOCK_ERASE_64K 0xD8U
#define CMD_CHIP_ERASE      0xC7U

#define STATUS_WIP_BIT      (1U << 0)  /* Write In Progress */
#define STATUS_WEL_BIT      (1U << 1)  /* Write Enable Latch */

typedef struct {
    void (*cs_assert)(void);
    void (*cs_deassert)(void);
    uint8_t (*spi_transfer_byte)(uint8_t byte);
    void (*spi_transmit)(const uint8_t *data, size_t len);
    void (*spi_receive)(uint8_t *data, size_t len);
    void (*delay_us)(uint32_t us);
} nor_spi_hal_t;

typedef struct {
    const nor_spi_hal_t *hal;
    uint8_t mfg_id;
    uint8_t memory_type;
    uint8_t capacity_id;
    uint32_t total_size_bytes;
} nor_flash_t;

typedef enum {
    NOR_OK = 0,
    NOR_ERR_TIMEOUT,
    NOR_ERR_INVALID_PARAM,
    NOR_ERR_ID_MISMATCH
} nor_status_t;

/* Публічний API драйвера */
nor_status_t nor_init(nor_flash_t *dev, const nor_spi_hal_t *hal);
nor_status_t nor_read(nor_flash_t *dev, uint32_t addr, uint8_t *buf, size_t len);
nor_status_t nor_erase_sector(nor_flash_t *dev, uint32_t sector_addr);
nor_status_t nor_erase_block(nor_flash_t *dev, uint32_t block_addr);
nor_status_t nor_write(nor_flash_t *dev, uint32_t addr, const uint8_t *data, size_t len);
nor_status_t nor_wait_busy(nor_flash_t *dev, uint32_t timeout_ms);

#endif /* NOR_FLASH_H */

/* nor_flash.c — Реалізація функцій драйвера NOR Flash */
#include "nor_flash.h"

static nor_status_t nor_write_enable(nor_flash_t *dev) {
    dev->hal->cs_assert();
    dev->hal->spi_transfer_byte(CMD_WRITE_ENABLE);
    dev->hal->cs_deassert();
    return NOR_OK;
}

nor_status_t nor_wait_busy(nor_flash_t *dev, uint32_t timeout_ms) {
    uint32_t elapsed_us = 0;
    const uint32_t timeout_us = timeout_ms * 1000U;

    while (elapsed_us <= timeout_us) {
        dev->hal->cs_assert();
        dev->hal->spi_transfer_byte(CMD_READ_STATUS_1);
        uint8_t status = dev->hal->spi_transfer_byte(0xFF);
        dev->hal->cs_deassert();

        if ((status & STATUS_WIP_BIT) == 0) {
            return NOR_OK; /* Чип завершив операцію */
        }

        dev->hal->delay_us(50);
        elapsed_us += 50;
    }
    return NOR_ERR_TIMEOUT;
}

nor_status_t nor_init(nor_flash_t *dev, const nor_spi_hal_t *hal) {
    if (!dev || !hal) return NOR_ERR_INVALID_PARAM;
    dev->hal = hal;

    dev->hal->cs_deassert();
    dev->hal->delay_us(1000); /* Стабілізація живлення після скидання */

    /* Читання ідентифікатора JEDEC ID */
    dev->hal->cs_assert();
    dev->hal->spi_transfer_byte(CMD_READ_ID);
    dev->mfg_id = dev->hal->spi_transfer_byte(0xFF);
    dev->memory_type = dev->hal->spi_transfer_byte(0xFF);
    dev->capacity_id = dev->hal->spi_transfer_byte(0xFF);
    dev->hal->cs_deassert();

    /* Якщо всі байти 0x00 або 0xFF — чип не відповідає на шині */
    if ((dev->mfg_id == 0x00 && dev->capacity_id == 0x00) ||
        (dev->mfg_id == 0xFF && dev->capacity_id == 0xFF)) {
        return NOR_ERR_ID_MISMATCH;
    }

    /* Розрахунок ємності: capacity_id = N відповідає 2^N байтів */
    if (dev->capacity_id >= 0x10 && dev->capacity_id <= 0x22) {
        dev->total_size_bytes = 1UL << dev->capacity_id;
    } else {
        dev->total_size_bytes = 0;
    }

    return nor_wait_busy(dev, 100);
}

nor_status_t nor_read(nor_flash_t *dev, uint32_t addr, uint8_t *buf, size_t len) {
    if (!dev || !buf || len == 0) return NOR_ERR_INVALID_PARAM;
    if (addr + len > dev->total_size_bytes) return NOR_ERR_INVALID_PARAM;

    nor_status_t st = nor_wait_busy(dev, 500);
    if (st != NOR_OK) return st;

    dev->hal->cs_assert();
    dev->hal->spi_transfer_byte(CMD_FAST_READ);
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 16));
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 8));
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 0));
    dev->hal->spi_transfer_byte(0xFF); /* 1 Dummy-байт для Fast Read */

    dev->hal->spi_receive(buf, len);
    dev->hal->cs_deassert();

    return NOR_OK;
}

nor_status_t nor_erase_sector(nor_flash_t *dev, uint32_t sector_addr) {
    if (!dev) return NOR_ERR_INVALID_PARAM;
    sector_addr &= ~(NOR_SECTOR_SIZE - 1U); /* Вирівнювання на границю 4 КБ */

    nor_status_t st = nor_wait_busy(dev, 500);
    if (st != NOR_OK) return st;

    nor_write_enable(dev);

    dev->hal->cs_assert();
    dev->hal->spi_transfer_byte(CMD_SECTOR_ERASE_4K);
    dev->hal->spi_transfer_byte((uint8_t)(sector_addr >> 16));
    dev->hal->spi_transfer_byte((uint8_t)(sector_addr >> 8));
    dev->hal->spi_transfer_byte((uint8_t)(sector_addr >> 0));
    dev->hal->cs_deassert();

    return nor_wait_busy(dev, 500); /* Сектор стирається до 300–500 мс */
}

/* Внутрішній запис однієї сторінки (не більше 256 байтів у межах однієї сторінки) */
static nor_status_t nor_page_program(nor_flash_t *dev, uint32_t addr,
                                     const uint8_t *data, size_t len) {
    if (len > NOR_PAGE_SIZE) return NOR_ERR_INVALID_PARAM;

    nor_status_t st = nor_wait_busy(dev, 100);
    if (st != NOR_OK) return st;

    nor_write_enable(dev);

    dev->hal->cs_assert();
    dev->hal->spi_transfer_byte(CMD_PAGE_PROGRAM);
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 16));
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 8));
    dev->hal->spi_transfer_byte((uint8_t)(addr >> 0));
    dev->hal->spi_transmit(data, len);
    dev->hal->cs_deassert();

    return nor_wait_busy(dev, 50); /* Сторінка пишеться до 1–3 мс */
}

/* Безпечний запис масиву довільної довжини з розбиттям по межах сторінок 256 Б */
nor_status_t nor_write(nor_flash_t *dev, uint32_t addr, const uint8_t *data, size_t len) {
    if (!dev || !data || len == 0) return NOR_ERR_INVALID_PARAM;
    if (addr + len > dev->total_size_bytes) return NOR_ERR_INVALID_PARAM;

    while (len > 0) {
        /* Обчислення кількості байтів, що вміщуються до кінця поточної сторінки */
        uint32_t page_offset = addr % NOR_PAGE_SIZE;
        size_t chunk = NOR_PAGE_SIZE - page_offset;
        if (chunk > len) chunk = len;

        nor_status_t st = nor_page_program(dev, addr, data, chunk);
        if (st != NOR_OK) return st;

        addr += chunk;
        data += chunk;
        len  -= chunk;
    }
    return NOR_OK;
}
```
```cpp
// nor_flash.hpp — Ідіоматичний C++20 драйвер для SPI/QSPI NOR Flash
#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>
#include <chrono>

namespace memory::flash {

inline constexpr size_t PageSize    = 256;
inline constexpr size_t SectorSize  = 4096;
inline constexpr size_t BlockSize   = 65536;

enum class Command : uint8_t {
    ReadId          = 0x9F,
    WriteEnable     = 0x06,
    WriteDisable    = 0x04,
    ReadStatus1     = 0x05,
    FastRead        = 0x0B,
    PageProgram     = 0x02,
    SectorErase4K   = 0x20,
    BlockErase64K   = 0xD8,
    ChipErase       = 0xC7
};

enum class Error : uint8_t {
    Timeout,
    InvalidAddress,
    DeviceNotResponding,
    WriteProtected
};

struct JedecId {
    uint8_t manufacturer;
    uint8_t memory_type;
    uint8_t capacity_code;

    [[nodiscard]] constexpr size_t capacityBytes() const noexcept {
        if (capacity_code >= 0x10 && capacity_code <= 0x22) {
            return size_t{1} << capacity_code;
        }
        return 0;
    }
};

/* Концепт апаратного SPI транспорту */
template <typename T>
concept SpiBus = requires(T bus, uint8_t byte, std::span<const uint8_t> tx, std::span<uint8_t> rx) {
    { bus.select() } -> std::same_as<void>;
    { bus.deselect() } -> std::same_as<void>;
    { bus.transfer(byte) } -> std::same_as<uint8_t>;
    { bus.write(tx) } -> std::same_as<void>;
    { bus.read(rx) } -> std::same_as<void>;
    { bus.delay(std::chrono::microseconds{}) } -> std::same_as<void>;
};

template <SpiBus Bus>
class NorFlashDriver {
public:
    explicit NorFlashDriver(Bus& bus) noexcept : bus_(bus) {}

    [[nodiscard]] std::expected<JedecId, Error> init() noexcept {
        bus_.deselect();
        bus_.delay(std::chrono::milliseconds{1});

        auto id = readJedecId();
        if ((id.manufacturer == 0x00 && id.capacity_code == 0x00) ||
            (id.manufacturer == 0xFF && id.capacity_code == 0xFF)) {
            return std::unexpected(Error::DeviceNotResponding);
        }

        total_size_ = id.capacityBytes();
        if (auto res = waitBusy(std::chrono::milliseconds{100}); !res) {
            return std::unexpected(res.error());
        }

        return id;
    }

    [[nodiscard]] std::expected<void, Error> read(uint32_t address,
                                                  std::span<uint8_t> dest) noexcept {
        if (address + dest.size() > total_size_) {
            return std::unexpected(Error::InvalidAddress);
        }
        if (auto res = waitBusy(std::chrono::milliseconds{200}); !res) {
            return res;
        }

        auto lock = makeBusLock();
        bus_.transfer(static_cast<uint8_t>(Command::FastRead));
        sendAddress(address);
        bus_.transfer(0xFF); // 1 Dummy byte
        bus_.read(dest);

        return {};
    }

    [[nodiscard]] std::expected<void, Error> eraseSector(uint32_t sector_addr) noexcept {
        sector_addr &= ~(SectorSize - 1);
        if (sector_addr >= total_size_) {
            return std::unexpected(Error::InvalidAddress);
        }
        if (auto res = waitBusy(std::chrono::milliseconds{200}); !res) {
            return res;
        }

        writeEnable();

        {
            auto lock = makeBusLock();
            bus_.transfer(static_cast<uint8_t>(Command::SectorErase4K));
            sendAddress(sector_addr);
        }

        return waitBusy(std::chrono::milliseconds{500});
    }

    [[nodiscard]] std::expected<void, Error> write(uint32_t address,
                                                   std::span<const uint8_t> data) noexcept {
        if (address + data.size() > total_size_) {
            return std::unexpected(Error::InvalidAddress);
        }

        size_t offset = 0;
        while (offset < data.size()) {
            uint32_t current_addr = address + static_cast<uint32_t>(offset);
            uint32_t page_offset  = current_addr % PageSize;
            size_t chunk_len      = std::min(data.size() - offset, PageSize - page_offset);

            if (auto res = programPage(current_addr, data.subspan(offset, chunk_len)); !res) {
                return res;
            }

            offset += chunk_len;
        }
        return {};
    }

private:
    Bus& bus_;
    size_t total_size_{0};

    struct BusLock {
        Bus& b;
        explicit BusLock(Bus& bus) noexcept : b(bus) { b.select(); }
        ~BusLock() noexcept { b.deselect(); }
        BusLock(const BusLock&) = delete;
        BusLock& operator=(const BusLock&) = delete;
    };

    [[nodiscard]] BusLock makeBusLock() noexcept { return BusLock(bus_); }

    void sendAddress(uint32_t addr) noexcept {
        bus_.transfer(static_cast<uint8_t>(addr >> 16));
        bus_.transfer(static_cast<uint8_t>(addr >> 8));
        bus_.transfer(static_cast<uint8_t>(addr >> 0));
    }

    void writeEnable() noexcept {
        auto lock = makeBusLock();
        bus_.transfer(static_cast<uint8_t>(Command::WriteEnable));
    }

    [[nodiscard]] JedecId readJedecId() noexcept {
        auto lock = makeBusLock();
        bus_.transfer(static_cast<uint8_t>(Command::ReadId));
        return JedecId{
            .manufacturer  = bus_.transfer(0xFF),
            .memory_type   = bus_.transfer(0xFF),
            .capacity_code = bus_.transfer(0xFF)
        };
    }

    [[nodiscard]] std::expected<void, Error> waitBusy(std::chrono::milliseconds timeout) noexcept {
        const auto deadline_us = std::chrono::duration_cast<std::chrono::microseconds>(timeout).count();
        int64_t elapsed_us = 0;

        while (elapsed_us <= deadline_us) {
            uint8_t status = 0;
            {
                auto lock = makeBusLock();
                bus_.transfer(static_cast<uint8_t>(Command::ReadStatus1));
                status = bus_.transfer(0xFF);
            }

            if ((status & 0x01) == 0) { // WIP == 0
                return {};
            }

            bus_.delay(std::chrono::microseconds{50});
            elapsed_us += 50;
        }
        return std::unexpected(Error::Timeout);
    }

    [[nodiscard]] std::expected<void, Error> programPage(uint32_t addr,
                                                         std::span<const uint8_t> chunk) noexcept {
        if (auto res = waitBusy(std::chrono::milliseconds{100}); !res) {
            return res;
        }

        writeEnable();

        {
            auto lock = makeBusLock();
            bus_.transfer(static_cast<uint8_t>(Command::PageProgram));
            sendAddress(addr);
            bus_.write(chunk);
        }

        return waitBusy(std::chrono::milliseconds{10});
    }
};

} // namespace memory::flash
```
:::

---

### Налаштування апаратного режиму Execute-in-Place (XIP)

Режим **XIP (Execute-in-Place)** перетворює зовнішню мікросхему Quad-SPI / Octal-SPI NOR Flash на невіддільну частину лінійного адресного простору мікроконтролера (наприклад, віртуальний або фізичний діапазон `0x90000000–0x9FFFFFFF` в архітектурах ARM Cortex-M або `0x3C000000` в ESP32). Процесорне ядро виставляє стандартні транзакції вибірки інструкцій (Instruction Fetch) по внутрішній шині AXI/AHB, а спеціалізований апаратний контролер пам'яті (QSPI/OCTOSPI controller) самостійно транслює їх у високошвидкісні серійні пачки імпульсів без жодного втручання програмного коду.

#### Конфігурація безперервного читання (Continuous Read / Performance Enhance Mode)

У базовому протоколі Fast Read Quad I/O кожна транзакція читання вимагає надсилання 1 байта команди (`0xEB`), 3–4 байтів адреси та 4–6 тактів очікування (Dummy cycles). Це створює паразитно високі накладні витрати: передача команди забирає додаткові 8 тактів на кожне вичитування кеш-лінії (32 байти).

Режим **Continuous Read Mode** оптимізує цей процес:
1. Під час першої транзакції надсилається команда `0xEB`, адреса, а у фазі фіктивного очікування (Dummy) передається спеціальний байт конфігурації (Mode Byte, наприклад `0x20` для чипів Winbond або `0xA5` для Macronix);
2. Внутрішній автомат мікросхеми Flash переходить у стан очікування адреси: сигнал `/CS` деактивується, але чип «пам'ятає», що наступна операція також буде Fast Read;
3. Під час усіх наступних звернень процесора контролер **не передає байт команди `0xEB` взагалі**, а одразу виставляє 24-бітну адресу на 4 паралельні лінії `IO[3:0]`. Затримка зчитування кожної інструкції скорочується з 16 до 8 тактів.

```
Традиційний Fast Read Quad I/O (14–16 тактів накладних витрат):
/CS : __|¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯|__
IO  :   [ CMD 0xEB (8 тактів) ][ Адреса 24-bit (6 тактів) ][ Dummy (6) ][ Дані (64) ]

Режим Continuous Read XIP (без команди 0xEB, 6–8 тактів накладних витрат):
/CS : __|¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯|__
IO  :   [ Адреса 24-bit (6 тактів) ][ Dummy + Mode (6) ][ Дані 32 байти (64 такти) ]
```

#### Робота апаратного кешу інструкцій (Instruction Cache)

Оскільки час вибірки з QSPI Flash на частоті 80 МГц становить приблизно `70–90 нс`, виконання коду на процесорі з тактовою частотою 200–480 МГц без кешування призводило б до постійних зупинок конвеєра (Wait States). Для ліквідації цієї затримки контролер пам'яті обов'язково інтегрують із двонаправленим кешем інструкцій (наприклад, ART Accelerator у STM32 або I-Cache в ESP32):
* При попаданні в кеш (Cache Hit) інструкція віддається за 0 тактів очікування (на повній частоті ядра);
* При промаху (Cache Miss) контролер зчитує цілу лінію кешу (32 або 64 байти) з пріоритетом критичного слова (Critical Word First), дозволяючи процесору продовжити виконання команди ще до того, як завантажиться решта лінії.

---

### Високошвидкісні шини Octal SPI та режим DTR (Double Transfer Rate)

Подальший розвиток технології XIP привів до створення 8-бітних інтерфейсів **Octal SPI (OSPI)** та протоколу **HyperBus**.

У режимі **DTR (Double Transfer Rate)** передача даних здійснюється по обох фронтах тактового сигналу `SCK` — як по наростаючому, так і по спадному:
1. За один тактовий період передається `2 байти` даних (8 бітів на наростаючому фронті + 8 бітів на спадному);
2. На частоті шини `200 МГц` пікова пропускна здатність сягає `400 МБ/с`, що повністю нівелює різницю між внутрішньою та зовнішньою пам'яттю коду;
3. Для компенсації затримок поширення сигналу по друкованій платі вводиться додаткова диференційна лінія стробування даних **DQS (Data Strobe)**, яку генерує сама мікросхема Flash синфазно з вихідними даними. Контролер мікроконтролера використовує DQS як строб фіксації даних, усуваючи фазове тремтіння (jitter).

Також сучасні контролери Octal SPI підтримують апаратне шифрування та дешифрування пам'яті на льоту (On-The-Fly Decryption, наприклад рушій AES-128/256 CTR у режимі OTFDEC), що захищає комерційну прошивку від несанкціонованого копіювання чи зчитування з контактів друкованої плати логічним аналізатором.

---

### Асинхронні фонові операції та взаємодія з DMA

Під час виконання тривалих операцій стирання сектора (`40–200 мс`) або посторінкового запису блокуюче очікування (busy polling) у циклі процесора марнує мільйони обчислювальних тактів. У професійних вбудованих архітектурах взаємодія організовується асинхронно через контролери прямого доступу до пам'яті (DMA) та системні таймери:

```
[Ядро процесора] --(ініціює DMA)--> [Контролер QSPI / DMA]
       |                                     |
       v (продовжує інші задачі RTOS)        v (передає команду й дані)
[Задача RTOS спить] <--(переривання IRQ)--- [Flash завершила запис / WIP=0]
```

1. **Фоновий запис сторінки:** процесор передає покажчик на буфер у дескриптор DMA і перемикає поточну задачу операційної системи реального часу (RTOS) у стан сну;
2. **Апаратна передача:** контролер DMA самостійно видає команду `0x02`, адресу та прокачує 256 байтів по лініях SPI без участі центрального процесора;
3. **Опитування завершення за таймером:** замість безперервного читання регістра стану задача RTOS прокидається по періодичному таймеру (кожні `500 мкс`), перевіряє стан біта `WIP` і, якщо операція завершена, повертає керування додатку. Це знижує завантаження процесора під час масового запису з 100% до менш ніж 0.5%.

---

### Адресація пам'яті понад 16 МБ: перехід до 4-байтних адрес

Традиційний протокол SPI Flash використовує 24-бітну адресу (`3 байти`), що обмежує максимальний адресний простір величиною `2²⁴ = 16 777 216 байтів` (16 Мегабайтів або 128 Мегабітів). Для чипів ємністю 256 Мбіт (32 МБ), 512 Мбіт (64 МБ) та 1 Гбіт (128 МБ) застосовують два альтернативні підходи адресації:

#### 1. Глобальний режим 4-Byte Address Mode (`0xB7` / `0xE9`)
Хост видає команду `0xB7 (Enter 4-Byte Address Mode)`, після чого чип інтерпретує всі наступні стандартні команди (`0x03`, `0x0B`, `0x02`, `0x20`) як такі, що приймають 4 байти адреси (`32 біти`). Для повернення назад використовується команда `0xE9`.

> ⚠️ **Пастка теплого перезавантаження (Warm Reset Trap):** Якщо мікроконтролер перевів Flash у 4-байтний режим, а потім зазнав програмного скидання (Watchdog Reset або скидання кнопкою без зняття живлення `VCC`), процесор почне виконувати Bootloader ROM, надсилаючи стандартні 3-байтні команди. Чип Flash, залишаючись у 4-байтному стані, зсуне отриману адресу на 8 бітів, що призведе до зчитування невірних векторів переривань та повного зависання пристрою. Для захисту в ініціалізацію Bootloader обов'язково додають команду скидання `0x66` + `0x99` (Software Reset) або команду `0xE9`.

#### 2. Спеціалізовані команди прямої 4-байтної адресації
Щоб уникнути ризику зависання при перезавантаженні, чипи підтримують паралельний набір інструкцій, які завжди приймають 4 байти адреси незалежно від поточного стану регістра адресації:
* `0x13` — Read Data (4-Byte Address);
* `0x0C` — Fast Read (4-Byte Address);
* `0xEC` — Fast Read Quad I/O (4-Byte Address);
* `0x12` — Page Program (4-Byte Address);
* `0x21` — Sector Erase 4 KB (4-Byte Address);
* `0xDC` — Block Erase 64 KB (4-Byte Address).

Використання цих спеціалізованих команд є найбільш надійною інженерною практикою для обсягів понад 16 МБ.

---

### Апаратний захист секторів та збереження параметрів

NOR Flash часто ділять на дві функціональні зони: статичну зону мікропрограми (Firmware Code) та динамічну зону енергонезалежних налаштувань (NVRAM Configuration).

#### Апаратний захист від випадкового запису

Для запобігання пошкодженню коду завантажувача у разі збоїв живлення або зависання процесора мікросхема має багаторівневий захист:
1. **Апаратний пін `/WP` (Write Protect):** при підтяжці до GND апаратно забороняє зміну бітів конфігурації у регістрах стану.
2. **Біти захисту блоків (Block Protect Bits, BP0..BP3):** дозволяють заблокувати від стирання та запису верхню або нижню половину, чверть або перші кілька секторів кристала.
3. **Регістри безпеки одноразового програмування (OTP Security Registers):** окремі виділені сторінки (зазвичай 3 блоки по 256 байтів), які після запису можна апаратно «спалити» бітом `OTP Lock`, перетворивши їх на незмінну фабричну ROM (для збереження серійних номерів, ключів шифрування та сертифікатів безпеки).

#### Організація журналу параметрів у NOR Flash

Оскільки сектор NOR Flash стирається цілком (мінімум 4 КБ), оновлення одного 4-байтного параметра конфігурації не можна робити прямим перезаписом на місці. Пряме стирання сектора на кожну зміну параметра вичерпає ресурс `100 000` циклів за кілька місяців.

Замість цього застосовують журнально-структуровані файлові системи (наприклад, **LittleFS**, **SPIFFS** або власні структури Key-Value):
* Сектор заповнюється записами послідовно від початку до кінця новими порціями;
* При зміні значення старий запис інвалідується (шляхом запису байта статусу `0x00` поверх `0xFF`), а нове значення дописується в наступні вільні байти сторінки;
* Повне стирання сектора 4 КБ та збирання сміття виконується лише тоді, коли весь сектор вичерпує вільний простір. Це збільшує ефективний ресурс роботи накопичувача параметрів у сотні разів.

---

### Автовизначення параметрів через стандарт SFDP (JESD216)

Щоб вбудовані операційні системи (Linux MTD, Zephyr, FreeRTOS) могли працювати з будь-якою мікросхемою NOR Flash без жорсткого зашивання таблиць ідентифікаторів у код, організація JEDEC прийняла стандарт **SFDP (Serial Flash Discoverable Parameters, JESD216)**.

За адресою `0x000000` у службовому просторі SFDP (доступному за командою `0x5A`) записана стандартизована структура заголовків:
* **Підпис SFDP:** чотири байти `0x50, 0x44, 0x46, 0x53` (ASCII рядок `"SFDP"`);
* **Таблиця базових параметрів (Basic Flash Parameter Table, BFPT):** містить точну кількість адресних байтів (3 або 4 байти), структуру секторів (наявність стирання 4 КБ, 32 КБ, 64 КБ та відповідні коди команд), кількість тактів очікування для режимів `Fast Read 1-4-4` та розташування біта активації Quad Enable (QE) у регістрах стану.

Використання SFDP дозволяє універсальному драйверу самостійно налаштувати оптимальну частоту, кількість dummy-тактів та режим XIP для чипів будь-якого вендора без ризику помилки конфігурації.

---

### Типові інженерні пастки при розробці драйверів NOR Flash

#### 1. Пастка циклічного переповнення сторінки (Page Wrap Trap)
Внутрішній буфер програмування NOR Flash жорстко прив'язаний до молодших 8 бітів адреси `addr[7:0]`. Якщо спробувати записати масив із 64 байтів за початковою адресою `0x0000FE` (254-й байт нульової сторінки), перші 2 байти запишуться за адресами `0x0000FE` та `0x0000FF`, а наступні 62 байти запишуться **не в наступну сторінку**, а з адреси `0x000000` (перезапишуть початок тієї самої нульової сторінки!). Чип не генерує жодного апаратного прапорця помилки, тихо спотворюючи раніше записані дані. Саме тому функція `nor_write` зобов'язана динамічно обчислювати доступний залишок сторінки: `chunk = PageSize - (addr % PageSize)`.

#### 2. Одноразовий характер засувки WEL
Команда `Write Enable (0x06)` встановлює біт `WEL` у регістрі стану рівно на **одну** наступну команду модифікації матриці. Як тільки операція `Page Program` або `Sector Erase` фізично стартує, біт `WEL` апаратно скидається в `0`. Будь-яка спроба виконати другий запис поспіль без повторної відправки коду `0x06` буде мовчки проігнорована чипом.

#### 3. Блокування читання коду під час стирання (Erase Suspend / Resume)
Фізичне стирання сектора триває сотні мілісекунд (`50–400 мс`). Якщо в цей час мікроконтролер отримає апаратне переривання, функція-обробник якого розміщена в тій самій мікросхемі NOR Flash у режимі XIP, процесор прочитає некоректні дані шини або отримає апаратний збій шини (HardFault / BusFault). Для запобігання аварії контролер видає команду **Erase Suspend (0x75)**: внутрішній автомат заморожує високовольтну помпу, переводить матрицю в режим читання за `20–40 мкс`, дозволяє процесору виконати критичний код обробника переривання, після чого повертає стирання командою **Erase Resume (0x7A)**.
