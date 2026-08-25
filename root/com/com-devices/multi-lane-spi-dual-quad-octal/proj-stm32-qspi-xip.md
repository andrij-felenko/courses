# Налаштування QSPI для прямого виконання коду (Memory-Mapped XIP)

У багатьох високопродуктивних мікроконтролерних системах на базі ядер ARM Cortex-M7 або RISC-V обсягу внутрішньої пам'яті програм (1–2 МБ) недостатньо для розміщення графічних стеків, шрифтів, текстур або ваг моделей машинного навчання. Інженерним стандартом для розширення пам'яті є підключення зовнішньої мікросхеми Flash через контролер Quad-SPI в апаратному режимі прямого відображення адресного простору (**Memory-Mapped Mode**).

У цьому режимі зовнішня послідовна пам'ять стає прозоро доступною ядру процесора як звичайна внутрішня пам'ять ROM за фіксованими 32-бітними адресами (наприклад, `0x90000000 – 0x9FFFFFFF` у контролерах STM32). Коли процесор виконує команду вибірки інструкції (*Instruction Fetch*) або завантаження даних (*Load*), апаратний контролер QSPI самостійно генерує послідовність транзакцій на фізичній шині, повністю звільняючи програмний код від керування передачею.

---

## 1. Архітектурна будова апаратного контролера QUADSPI

Контролер QUADSPI мікроконтролера STM32 є спеціалізованим шинним мостом між внутрішньою багатошаровою матрицею системних шин (AXI / AHB) та зовнішніми фізичними виводами мікросхеми Flash.

```
                         Внутрішня архітектура QUADSPI
  ┌───────────────────────────────────────────────────────────────────────────┐
  │                           Системна шина AXI / AHB                         │
  └─────────────────────────────────────┬─────────────────────────────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │   Шинний міст та арбітр     │
                         └──────────────┬──────────────┘
                                        │
      ┌─────────────────────────────────┴─────────────────────────────────┐
      │                                                                   │
 ┌────▼─────────────────────────┐                        ┌────────────────▼────┐
 │  Регістри конфігурації       │                        │ Приймальний/        │
 │  • QUADSPI_CR  (керування)   │                        │ передавальний FIFO  │
 │  • QUADSPI_DCR (параметри)   │                        │ (32 байти)          │
 │  • QUADSPI_CCR (фази зв'язку)│                        └────────────────┬────┘
 └────┬─────────────────────────┘                                         │
      │                                                                   │
      └─────────────────────────────────┬─────────────────────────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │ Цифровий автомат транзакцій │
                         │ (Instruction/Addr/Dummy/Data│
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │   Вихідні драйвери GPIO     │
                         │   CS#, SCLK, IO0, IO1,      │
                         │   IO2, IO3                  │
                         └─────────────────────────────┘
```

Контролер підтримує чотири взаємовиключні функціональні режими роботи, які задаються полем `FMODE` у конфігураційному регістрі `QUADSPI_CCR`:
1. **Indirect Write Mode (FMODE = 00b)**: непрямий запис. Процесор або контролер DMA записує байти у регістр даних `QUADSPI_DR`, звідки вони через 32-байтний FIFO передаються на шину. Використовується для конфігурації регістрів Flash та програмування сторінок.
2. **Indirect Read Mode (FMODE = 01b)**: непряме читання. Дані зчитуються з Flash у FIFO, після чого забираються процесором або DMA.
3. **Automatic Polling Mode (FMODE = 10b)**: апаратне періодичне опитування регістрів Flash-пам'яті (наприклад, читання регістра стану `0x05` з маскою зайнятості `WIP`) без завантаження ядра CPU.
4. **Memory-Mapped Mode (FMODE = 11b)**: режим прямого відображення адресного простору. Будь-яке читання за адресою `0x90000000 + Offset` апаратно транслюється у транзакцію швидкого читання `0xEB` (*Fast Read Quad I/O*) на шині QSPI.

---

## 2. Покроковий цикл ініціалізації драйвера

Для активації режиму Memory-Mapped необхідно виконати сувору послідовність налаштування, яка враховує внутрішні стани мікросхеми Flash-пам'яті (розглянуто на прикладі Winbond W25Q128JV).

### Крок 1. Тактування та виводи GPIO

Шина QSPI працює на високих частотах (до 100–133 МГц), тому виводи GPIO повинні бути налаштовані у режим альтернативної функції (Alternate Function AF9/AF10) з максимальною швидкістю наростання фронту (*Very High Slew Rate*):
* `PB2` → `QUADSPI_CLK` (тактовий сигнал SCLK);
* `PB6` / `PB10` → `QUADSPI_BK1_NCS` (вибір кристала CS#);
* `PD11` → `QUADSPI_BK1_IO0` (лінія даних IO0);
* `PD12` → `QUADSPI_BK1_IO1` (лінія даних IO1);
* `PE2` → `QUADSPI_BK1_IO2` (лінія даних IO2 / WP#);
* `PD13` → `QUADSPI_BK1_IO3` (лінія даних IO3 / HOLD#).

### Крок 2. Базові параметри контролера (Регістри CR та DCR)

У регістрі керування `QUADSPI_CR` та конфігурації пристрою `QUADSPI_DCR` встановлюються фізичні властивості каналу зв'язку:
* **Дільник тактової частоти (`PRESCALER`)**: визначає частоту SCLK. При частоті ядра шини 200 МГц значення `PRESCALER = 1` задає частоту шини `200 / (1 + 1) = 100 МГц`.
* **Зсув вибірки (`SSHIFT`)**: на частотах понад 80 МГц вмикається вибірка на півтакту пізніше (`SSHIFT = 1`), що компенсує затримку сигналу на друкованій платі та внутрішніх буферах Flash.
* **Час утримання CS# у високому стані (`CSHT`)**: задає мінімальну паузу між транзакціями `t[CS_HIGH]` (поле `CSHT = 4` задає 4 такти SCLK паузи, що перевищує мінімальні 30 нс для відновлення логіки Flash).
* **Розмір адресного простору (`FSIZE`)**: задає ємність мікросхеми за формулою `Розмір = 2^(FSIZE + 1) байтів`. Для мікросхеми ємністю 16 МБайт (128 Мбіт) встановлюється значення `FSIZE = 23` (оскільки `2^(23 + 1) = 2^24 = 16 777 216 байтів`).

### Крок 3. Перевірка фізичного зв'язку (JEDEC ID)

Перед активацією 4-бітного режиму драйвер надсилає команду `0x9F` (*Read JEDEC ID*) в 1-бітовому режимі `1-1-1`. Flash-пам'ять повертає 3 байти:
* Байт 0: Ідентифікатор виробника (`0xEF` для Winbond, `0x20` для Micron, `0x9D` для ISSI);
* Байт 1: Тип пам'яті (наприклад, `0x40` для SPI Flash);
* Байт 2: Ємність кристала (`0x18` для 128 Мбіт = 16 МБайт).

Невідповідність цих байтів свідчить про апаратний дефект монтажу (непропай ліній SCLK/CS# або короткі замикання).

### Крок 4. Активація біта Quad Enable (QE)

За замовчуванням виводи мікросхеми 3 та 7 працюють як входи апаратного блокування запису `WP#` та призупинення `HOLD#`. Щоб перемкнути їх у режим високошвидкісних ліній даних `IO2` та `IO3`, необхідно встановити енергонезалежний біт `QE` (*Quad Enable*) у другому регістрі стану (*Status Register 2*, біт S9):
1. Надсилається команда дозволу запису `0x06` (*Write Enable*).
2. Апаратним автоопитуванням перевіряється встановлення біта `WEL` (*Write Enable Latch*) у першому регістрі стану.
3. Надсилається команда запису другого регістра стану `0x31` зі значенням біта `QE = 1`.
4. Запускається автоопитування біта `WIP` (*Write In Progress*) команди `0x05`, поки внутрішній цикл програмування енергонезалежних комірок стану (займає від 5 до 15 мс) не завершиться.

### Крок 5. Конфігурація швидкого читання 1-4-4

Контролер налаштовується на виконання інструкції `0xEB` (*Fast Read Quad I/O*):
* `IMODE = 1 line` (опкод `0xEB` передається по лінії IO0);
* `ADMODE = 4 lines`, `ADSIZE = 24-bit` (адреса передається по 4 лініях за 6 тактів);
* `ABMODE = 4 lines`, `ABSIZE = 8-bit`, значення `0x20` (байт режиму вмикає Continuous Read Mode);
* `DCYC = 6` (6 тактів очікування Dummy для частоти 100 МГц);
* `DMODE = 4 lines` (зчитування даних по 4 лініях);
* `SIOO = 1` (*Send Instruction Only Once* — контролер надсилає опкод `0xEB` лише під час першого звернення; у всіх наступних транзакціях опкод опускається, заощаджуючи 8 тактів на кожній транзакції).

### Крок 6. Перехід у режим Memory-Mapped

Викликається переведення апаратного блока у функціональний стан прямого відображення. Контролер займає шину і чекає на транзакції читання від ядра CPU або контролера DMA.

---

## 3. Програмна реалізація драйвера QSPI XIP

Нижче наведено повну реалізацію ініціалізації та активації режиму прямого відображення для мікроконтролерів STM32 (родини STM32F7 / STM32H7) мовами C (STM32 HAL) та C++ (сучасна обгортка з RAII та суворою типізацією).

:::tabs
```c
#include "stm32h7xx_hal.h"
#include <stdbool.h>
#include <stdint.h>

#define QSPI_FLASH_BASE_ADDR    0x90000000U
#define QSPI_FLASH_SIZE_BYTES   0x01000000U /* 16 МБайт (128 Мбіт) */

/* Опкоди Flash-пам'яті Winbond W25Q128JV */
#define CMD_WRITE_ENABLE        0x06
#define CMD_READ_STATUS_REG1    0x05
#define CMD_READ_STATUS_REG2    0x35
#define CMD_WRITE_STATUS_REG2   0x31
#define CMD_READ_JEDEC_ID       0x9F
#define CMD_FAST_READ_QUAD_IO   0xEB

#define STATUS2_QE_BIT          (1U << 1) /* Біт Quad Enable (S9) */

static QSPI_HandleTypeDef hqspi;

/**
 * @brief Очікування завершення внутрішньої операції Flash (WIP = 0)
 */
static HAL_StatusTypeDef qspi_wait_busy(uint32_t timeout_ms)
{
    QSPI_CommandTypeDef cmd = {0};
    QSPI_AutoPollingTypeDef cfg = {0};

    cmd.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
    cmd.Instruction       = CMD_READ_STATUS_REG1;
    cmd.AddressMode       = QSPI_ADDRESS_NONE;
    cmd.AlternateByteMode = QSPI_ALTERNATE_BYTES_NONE;
    cmd.DataMode          = QSPI_DATA_1_LINE;
    cmd.DummyCycles       = 0;
    cmd.DdrMode           = QSPI_DDR_MODE_DISABLE;
    cmd.SIOOMode          = QSPI_SIOO_INST_EVERY_CMD;

    /* Очікуємо, поки біт 0 (Write In Progress) регістра стану стане 0 */
    cfg.Match           = 0x00;
    cfg.Mask            = 0x01;
    cfg.MatchMode       = QSPI_MATCH_MODE_AND;
    cfg.StatusBytesSize = 1;
    cfg.Interval        = 0x10;
    cfg.AutomaticStop   = QSPI_AUTOMATIC_STOP_ENABLE;

    return HAL_QSPI_AutoPolling(&hqspi, &cmd, &cfg, timeout_ms);
}

/**
 * @brief Перевірка та увімкнення біта Quad Enable (QE)
 */
static HAL_StatusTypeDef qspi_enable_quad_mode(void)
{
    QSPI_CommandTypeDef cmd = {0};
    uint8_t status2 = 0;

    /* 1. Читаємо другий регістр стану */
    cmd.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
    cmd.Instruction       = CMD_READ_STATUS_REG2;
    cmd.AddressMode       = QSPI_ADDRESS_NONE;
    cmd.AlternateByteMode = QSPI_ALTERNATE_BYTES_NONE;
    cmd.DataMode          = QSPI_DATA_1_LINE;
    cmd.NbData            = 1;
    cmd.DummyCycles       = 0;

    if (HAL_QSPI_Command(&hqspi, &cmd, HAL_QSPI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
        return HAL_ERROR;
    if (HAL_QSPI_Receive(&hqspi, &status2, HAL_QSPI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
        return HAL_ERROR;

    /* Якщо біт QE вже встановлений — виходимо */
    if ((status2 & STATUS2_QE_BIT) != 0)
        return HAL_OK;

    /* 2. Надсилаємо Write Enable */
    cmd.Instruction = CMD_WRITE_ENABLE;
    cmd.DataMode    = QSPI_DATA_NONE;
    if (HAL_QSPI_Command(&hqspi, &cmd, HAL_QSPI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
        return HAL_ERROR;

    /* 3. Записуємо оновлений Status Register 2 з встановленим бітом QE */
    status2 |= STATUS2_QE_BIT;
    cmd.Instruction = CMD_WRITE_STATUS_REG2;
    cmd.DataMode    = QSPI_DATA_1_LINE;
    cmd.NbData      = 1;

    if (HAL_QSPI_Command(&hqspi, &cmd, HAL_QSPI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
        return HAL_ERROR;
    if (HAL_QSPI_Transmit(&hqspi, &status2, HAL_QSPI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
        return HAL_ERROR;

    return qspi_wait_busy(1000);
}

/**
 * @brief Активація режиму Memory-Mapped (Execute-in-Place)
 */
HAL_StatusTypeDef qspi_init_memory_mapped(void)
{
    hqspi.Instance = QUADSPI;
    hqspi.Init.ClockPrescaler     = 1;          /* 200 МГц / (1 + 1) = 100 МГц */
    hqspi.Init.FifoThreshold      = 4;
    hqspi.Init.SampleShifting     = QSPI_SAMPLE_SHIFTING_HALFCYCLE;
    hqspi.Init.FlashSize          = 23;         /* 2^(23+1) = 2^24 = 16 МБайт */
    hqspi.Init.ChipSelectHighTime = QSPI_CS_HIGH_TIME_4_CYCLE;
    hqspi.Init.ClockMode          = QSPI_CLOCK_MODE_0;
    hqspi.Init.FlashID            = QSPI_FLASH_ID_1;
    hqspi.Init.DualFlash          = QSPI_DUALFLASH_DISABLE;

    if (HAL_QSPI_Init(&hqspi) != HAL_OK)
        return HAL_ERROR;

    if (qspi_enable_quad_mode() != HAL_OK)
        return HAL_ERROR;

    /* Налаштування команди швидкого читання Fast Read Quad I/O 1-4-4 */
    QSPI_CommandTypeDef s_command = {0};
    s_command.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
    s_command.Instruction       = CMD_FAST_READ_QUAD_IO;
    s_command.AddressMode       = QSPI_ADDRESS_4_LINES;
    s_command.AddressSize       = QSPI_ADDRESS_24_BITS;
    s_command.AlternateByteMode = QSPI_ALTERNATE_BYTES_4_LINES;
    s_command.AlternateBytesSize= QSPI_ALTERNATE_BYTES_8_BITS;
    s_command.AlternateBytes    = 0x20;         /* Режим Continuous Read */
    s_command.DummyCycles       = 6;            /* 6 dummy-тактів для 100 МГц */
    s_command.DataMode          = QSPI_DATA_4_LINES;
    s_command.DdrMode           = QSPI_DDR_MODE_DISABLE;
    s_command.SIOOMode          = QSPI_SIOO_INST_ONLY_FIRST_CMD;

    QSPI_MemoryMappedTypeDef s_mem_mapped_cfg = {0};
    s_mem_mapped_cfg.TimeOutActivation = QSPI_TIMEOUT_COUNTER_DISABLE;

    /* Переведення апаратного контролера у режим прямого відображення */
    return HAL_QSPI_MemoryMapped(&hqspi, &s_command, &s_mem_mapped_cfg);
}
```
```cpp
#include "stm32h7xx_hal.h"
#include <concepts>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

enum class QspiError : uint8_t {
    HardwareFault,
    Timeout,
    InvalidDevice,
    WriteProtected
};

class QspiXipController {
public:
    static constexpr uintptr_t FlashBaseAddress = 0x90000000U;
    static constexpr size_t    FlashSizeBytes   = 16 * 1024 * 1024; // 16 MB

    explicit QspiXipController(QUADSPI_TypeDef* instance = QUADSPI) noexcept
        : instance_(instance) {
        hqspi_.Instance = instance_;
    }

    ~QspiXipController() noexcept {
        if (is_mapped_) {
            HAL_QSPI_Abort(&hqspi_);
            HAL_QSPI_DeInit(&hqspi_);
        }
    }

    QspiXipController(const QspiXipController&) = delete;
    QspiXipController& operator=(const QspiXipController&) = delete;
    QspiXipController(QspiXipController&&) noexcept = default;
    QspiXipController& operator=(QspiXipController&&) noexcept = default;

    [[nodiscard]] std::expected<void, QspiError> initialize(uint8_t prescaler = 1) noexcept {
        hqspi_.Init.ClockPrescaler     = prescaler;
        hqspi_.Init.FifoThreshold      = 4;
        hqspi_.Init.SampleShifting     = QSPI_SAMPLE_SHIFTING_HALFCYCLE;
        hqspi_.Init.FlashSize          = 23; // 16 МБ (2^(23+1))
        hqspi_.Init.ChipSelectHighTime = QSPI_CS_HIGH_TIME_4_CYCLE;
        hqspi_.Init.ClockMode          = QSPI_CLOCK_MODE_0;
        hqspi_.Init.FlashID            = QSPI_FLASH_ID_1;
        hqspi_.Init.DualFlash          = QSPI_DUALFLASH_DISABLE;

        if (HAL_QSPI_Init(&hqspi_) != HAL_OK) {
            return std::unexpected(QspiError::HardwareFault);
        }

        if (auto res = enable_quad_mode(); !res) {
            return res;
        }

        if (auto res = enter_memory_mapped_mode(); !res) {
            return res;
        }

        is_mapped_ = true;
        return {};
    }

    [[nodiscard]] static std::span<const uint8_t> memory_view() noexcept {
        return {reinterpret_cast<const uint8_t*>(FlashBaseAddress), FlashSizeBytes};
    }

    template<typename T>
    [[nodiscard]] static const T* get_pointer_at(uintptr_t offset) noexcept {
        if (offset + sizeof(T) > FlashSizeBytes) return nullptr;
        return reinterpret_cast<const T*>(FlashBaseAddress + offset);
    }

private:
    static constexpr uint8_t CmdWriteEnable      = 0x06;
    static constexpr uint8_t CmdReadStatusReg1   = 0x05;
    static constexpr uint8_t CmdReadStatusReg2   = 0x35;
    static constexpr uint8_t CmdWriteStatusReg2  = 0x31;
    static constexpr uint8_t CmdFastReadQuadIo   = 0xEB;
    static constexpr uint8_t Status2QeBit        = (1U << 1);

    QUADSPI_TypeDef* instance_;
    QSPI_HandleTypeDef hqspi_{};
    bool is_mapped_{false};

    [[nodiscard]] std::expected<void, QspiError> wait_busy(uint32_t timeout_ms = 1000) noexcept {
        QSPI_CommandTypeDef cmd{};
        cmd.InstructionMode   = QSPI_INSTRUCTION_1_LINE;
        cmd.Instruction       = CmdReadStatusReg1;
        cmd.AddressMode       = QSPI_ADDRESS_NONE;
        cmd.AlternateByteMode = QSPI_ALTERNATE_BYTES_NONE;
        cmd.DataMode          = QSPI_DATA_1_LINE;

        QSPI_AutoPollingTypeDef cfg{};
        cfg.Match           = 0x00;
        cfg.Mask            = 0x01;
        cfg.MatchMode       = QSPI_MATCH_MODE_AND;
        cfg.StatusBytesSize = 1;
        cfg.Interval        = 0x10;
        cfg.AutomaticStop   = QSPI_AUTOMATIC_STOP_ENABLE;

        if (HAL_QSPI_AutoPolling(&hqspi_, &cmd, &cfg, timeout_ms) != HAL_OK) {
            return std::unexpected(QspiError::Timeout);
        }
        return {};
    }

    [[nodiscard]] std::expected<void, QspiError> enable_quad_mode() noexcept {
        QSPI_CommandTypeDef cmd{};
        cmd.InstructionMode = QSPI_INSTRUCTION_1_LINE;
        cmd.Instruction     = CmdReadStatusReg2;
        cmd.DataMode        = QSPI_DATA_1_LINE;
        cmd.NbData          = 1;

        uint8_t status2 = 0;
        if (HAL_QSPI_Command(&hqspi_, &cmd, 100) != HAL_OK ||
            HAL_QSPI_Receive(&hqspi_, &status2, 100) != HAL_OK) {
            return std::unexpected(QspiError::HardwareFault);
        }

        if (status2 & Status2QeBit) return {};

        cmd.Instruction = CmdWriteEnable;
        cmd.DataMode    = QSPI_DATA_NONE;
        if (HAL_QSPI_Command(&hqspi_, &cmd, 100) != HAL_OK) {
            return std::unexpected(QspiError::HardwareFault);
        }

        status2 |= Status2QeBit;
        cmd.Instruction = CmdWriteStatusReg2;
        cmd.DataMode    = QSPI_DATA_1_LINE;
        cmd.NbData      = 1;

        if (HAL_QSPI_Command(&hqspi_, &cmd, 100) != HAL_OK ||
            HAL_QSPI_Transmit(&hqspi_, &status2, 100) != HAL_OK) {
            return std::unexpected(QspiError::HardwareFault);
        }

        return wait_busy(1000);
    }

    [[nodiscard]] std::expected<void, QspiError> enter_memory_mapped_mode() noexcept {
        QSPI_CommandTypeDef cmd{};
        cmd.InstructionMode    = QSPI_INSTRUCTION_1_LINE;
        cmd.Instruction        = CmdFastReadQuadIo;
        cmd.AddressMode        = QSPI_ADDRESS_4_LINES;
        cmd.AddressSize        = QSPI_ADDRESS_24_BITS;
        cmd.AlternateByteMode  = QSPI_ALTERNATE_BYTES_4_LINES;
        cmd.AlternateBytesSize = QSPI_ALTERNATE_BYTES_8_BITS;
        cmd.AlternateBytes     = 0x20; // Continuous Read Mode
        cmd.DummyCycles        = 6;
        cmd.DataMode           = QSPI_DATA_4_LINES;
        cmd.SIOOMode           = QSPI_SIOO_INST_ONLY_FIRST_CMD;

        QSPI_MemoryMappedTypeDef cfg{};
        cfg.TimeOutActivation = QSPI_TIMEOUT_COUNTER_DISABLE;

        if (HAL_QSPI_MemoryMapped(&hqspi_, &cmd, &cfg) != HAL_OK) {
            return std::unexpected(QspiError::HardwareFault);
        }
        return {};
    }
};
```
:::

---

## 4. Конфігурація Memory Protection Unit (MPU) та кешу

Для досягнення максимальної швидкодії виконання коду на тактовій частоті ядра 480 МГц зовнішня пам'ять обов'язково повинна обслуговуватися внутрішнім процесорним кешем L1 (I-Cache та D-Cache). Без активації кешування кожне звернення процесора до пам'яті викликатиме окрему пакетну транзакцію на шині QSPI з очікуванням Dummy-тактів, сповільнюючи виконання програми у 5–10 разів.

### Налаштування регіону MPU

За замовчуванням ядро ARM Cortex-M7 розглядає невідомі адресні простори як пам'ять типу `Device` або `Strongly-Ordered`, де кешування, спекулятивне читання та буферизація суворо заборонені.

Для увімкнення кешування адресний діапазон `0x90000000 – 0x90FFFFFF` необхідно явно зареєструвати у блоці MPU:

:::tabs
```c
void mpu_config_qspi_xip(void)
{
    MPU_Region_InitTypeDef MPU_InitStruct = {0};

    HAL_MPU_Disable();

    MPU_InitStruct.Enable           = MPU_REGION_ENABLE;
    MPU_InitStruct.Number           = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress      = QSPI_FLASH_BASE_ADDR;
    MPU_InitStruct.Size             = MPU_REGION_SIZE_16MB;
    MPU_InitStruct.SubRegionDisable = 0x00;
    MPU_InitStruct.TypeExtField     = MPU_TEX_LEVEL0;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec      = MPU_INSTRUCTION_ACCESS_ENABLE;
    MPU_InitStruct.IsShareable      = MPU_ACCESS_NOT_SHAREABLE;
    MPU_InitStruct.IsCacheable      = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable     = MPU_ACCESS_NOT_BUFFERABLE; /* Write-Through */

    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}
```
```cpp
void mpu_config_qspi_xip() noexcept
{
    MPU_Region_InitTypeDef MPU_InitStruct{};

    HAL_MPU_Disable();

    MPU_InitStruct.Enable           = MPU_REGION_ENABLE;
    MPU_InitStruct.Number           = MPU_REGION_NUMBER0;
    MPU_InitStruct.BaseAddress      = QspiXipController::FlashBaseAddress;
    MPU_InitStruct.Size             = MPU_REGION_SIZE_16MB;
    MPU_InitStruct.SubRegionDisable = 0x00;
    MPU_InitStruct.TypeExtField     = MPU_TEX_LEVEL0;
    MPU_InitStruct.AccessPermission = MPU_REGION_FULL_ACCESS;
    MPU_InitStruct.DisableExec      = MPU_INSTRUCTION_ACCESS_ENABLE;
    MPU_InitStruct.IsShareable      = MPU_ACCESS_NOT_SHAREABLE;
    MPU_InitStruct.IsCacheable      = MPU_ACCESS_CACHEABLE;
    MPU_InitStruct.IsBufferable     = MPU_ACCESS_NOT_BUFFERABLE;

    HAL_MPU_ConfigRegion(&MPU_InitStruct);
    HAL_MPU_Enable(MPU_PRIVILEGED_DEFAULT);
}
```
:::

### Когерентність кешу при модифікації Flash

Кеш інструкцій I-Cache не підтримує апаратне відстеження змін у зовнішній Flash-пам'яті. Якщо програма оновлює прошивку, завантажує динамічні плагіни або перепрошиває сектори:
1. Перед записом виходять із режиму прямого відображення.
2. Після завершення запису та повторної активації режиму Memory-Mapped виконують примусову інвалідацію кешів процесора:

:::tabs
```c
SCB_InvalidateICache();
SCB_InvalidateDCache();
```
```cpp
SCB_InvalidateICache();
SCB_InvalidateDCache();
```
:::

---

## 5. Інтеграція в скрипт лінкувальника (Linker Script)

Для розміщення важких ресурсів або коду функцій безпосередньо у зовнішній Flash-пам'яті модифікується скрипт компонування GNU LD (`linker.ld`).

У блоці опису пам'яті оголошується регіон `QSPI_FLASH`:

```
MEMORY
{
  FLASH      (rx)  : ORIGIN = 0x08000000, LENGTH = 2048K  /* Внутрішня Flash */
  QSPI_FLASH (rx)  : ORIGIN = 0x90000000, LENGTH = 16384K /* Зовнішня QSPI */
  DTCMRAM    (rwx) : ORIGIN = 0x20000000, LENGTH = 128K
  RAM_D1     (rwx) : ORIGIN = 0x24000000, LENGTH = 512K
}

SECTIONS
{
  /* Секція для розміщення великих константних масивів та графіки у QSPI */
  .qspi_data :
  {
    . = ALIGN(4);
    *(.qspi_data*)
    *(.rodata.font_*)
    *(.rodata.image_*)
    . = ALIGN(4);
  } > QSPI_FLASH

  /* Секція для виконання коду функцій з QSPI Flash */
  .qspi_text :
  {
    . = ALIGN(4);
    *(.qspi_text*)
    . = ALIGN(4);
  } > QSPI_FLASH
}
```

У вихідному коді програми відповідні об'єкти позначаються атрибутом секції компилятора:

:::tabs
```c
__attribute__((section(".qspi_data")))
const uint8_t large_texture_map[1024 * 1024] = { 0xAA, 0xBB, /* ... */ };

__attribute__((section(".qspi_text")))
void neural_network_inference_heavy(const float* input, float* output)
{
    /* Важкий обчислювальний код, що виконується з QSPI Flash */
}
```
```cpp
[[gnu::section(".qspi_data")]]
const uint8_t large_texture_map[1024 * 1024] = { 0xAA, 0xBB, /* ... */ };

[[gnu::section(".qspi_text")]]
void neural_network_inference_heavy(const float* input, float* output) noexcept
{
    /* Важкий обчислювальний код, що виконується з QSPI Flash */
}
```
:::

---

## 6. Часовий аналіз та налагодження логічним аналізатором

Під час звернення ядра процесора до адреси `0x90001240` при виникненні промаху кешу (Cache Miss) на шині QSPI розгортається наступна послідовність сигналів:

```
        Часова діаграма пакетного завантаження рядка кешу L1 (32 байти)
  CS#  ──┐                                                                   ┌──
         │◄─ 80 нс ─►│◄─ 60 нс ─►│◄─ 20 нс ─►│◄─ 60 нс ─►│◄─── 240 нс ───►│   │
  SCLK ───┌─┐─┌─┐─┌─┐─┌─┐─┌─┐─┌─┐─┌─┐─┌─┐─┌─┐─┌─┐─┌─┐─┌─┐─┌─┐─┌─┐─...─┌─┐─────
          │1│ │ │8│   │9│ │ │14│  │15│ │16│  │17│ │ │22│  │23│ │24│   │86│
          └───┴───┘   └───┴────┘  └───┴───┘  └───┴───┴─┘  └───┴───┘   └──┘
  IO0..3 ── 0xEB ────── Адреса ──── Mode ─────  Dummy  ──── D0..D31 (32B) ────
```

### Хронологія пакетної транзакції

1. **0.00 мкс (Активація CS#)**: сигнал CS# опускається в нуль. За час `t[CSS] = 20 нс` вхідні ключі Flash виходять зі сну.
2. **0.02 мкс (Фаза інструкції)**: якщо це перша транзакція, контролер видає 8 бітів опкоду `0xEB` по лінії IO0 (8 тактів при 100 МГц = 80 нс). У наступних транзакціях у режимі Continuous Read ця фаза займає 0 нс.
3. **0.10 мкс (Фаза адреси)**: контролер паралельно видає 24 біти адреси `0x001240` по лініях `IO0..IO3` за 6 тактів (60 нс).
4. **0.16 мкс (Фаза режиму)**: видається конфігураційний байт `0x20` за 2 такти (20 нс).
5. **0.18 мкс (Холості такти Dummy)**: лінії переходять у стан Hi-Z на 6 тактів (60 нс). За цей час аналогові схеми Flash зчитують перше слово з матриці.
6. **0.24 мкс (Фаза даних)**: Flash-пам'ять видає 32 байти даних (64 нібли за 64 такти = 640 нс).
7. **0.88 мкс (Деактивація CS#)**: сигнал CS# піднімається у логічну одиницю; рядок кешу повністю заповнено.

Сумарний час реакції на промах кешу становить близько 880 нс. Усі наступні сотні звернень до інструкцій всередині цього рядка виконуються з внутрішнього кешу за 0 тактів очікування на частоті 480 МГц.

---

## 7. Апаратне автоопитування (Auto-Polling Mode) без блокування процесора

Під час виконання операцій стирання сектора (триває 45–400 мс) або програмування сторінки (0.4–0.8 мс) програмний код не повинен витрачати обчислювальні ресурси ядра на циклічне опитування регістра стану в режимі активного очікування (*Busy-Wait Loop*).

Контролер QUADSPI містить апаратний блок автоопитування (**Automatic Polling Mode**):
* У регістрі `QUADSPI_PSMAR` встановлюється очікуване значення бітів (наприклад, `0x00` для біта `WIP`);
* У регістрі `QUADSPI_PSMKR` встановлюється маска перевірки (наприклад, `0x01` для виділення біта `WIP`);
* У регістрі `QUADSPI_PIR` задається інтервал між автоматичними транзакціями (наприклад, кожні 256 тактів шини);
* Вмикається прапорець `SMIE` (*Status Match Interrupt Enable*).

Після запуску автоопитування контролер QUADSPI повністю бере на себе надсилання команди `0x05` та перевірку результату. Ядро процесора може перейти у режим енергозбереження `WFI` (*Wait For Interrupt*) або виконувати інші обчислювальні задачі. Щойно біт `WIP` скинеться в нуль, апаратний блок сформує апаратне переривання `Status Match`, і драйвер миттєво відновить роботу.

---

## 8. Аварійне відновлення після збоїв та скидання (Glitch Recovery)

Якщо в системі відбулося неочікуване програмне скидання процесора (`NVIC_SystemReset()`) або спрацював сторонній сторожовий таймер, мікросхема Flash-пам'яті не зазнає апаратного скидання по живленню і залишається у стані **Continuous Read Mode** (очікує адресу замість опкоду) або в режимі **QPI** (очікує опкод по 4 лініях замість 1).

Якщо новий завантажувач після старту спробує надіслати стандартну команду `0x9F` (*Read JEDEC ID*) в 1-бітовому режимі `1-1-1`, Flash-пам'ять інтерпретує перші байти команди як зсув адреси та поверне випадкові дані, що призведе до збою ініціалізації.

Для гарантованого відновлення зв'язку під час старту драйвера застосовується процедура виходу з завислого стану:
1. Сигнал CS# опускається в нуль.
2. Контролер генерує від 8 до 16 тактів SCLK, утримуючи всі лінії `IO0..IO3` у стані високої логічної одиниці (`0xFF`). Це повідомляє внутрішньому автомату Flash про завершення неперервного режиму.
3. Сигнал CS# піднімається в одиницю.
4. Надсилається послідовність програмного скидання: команда `0x66` (*Reset Enable*) з наступною командою `0x99` (*Reset Device*).
5. Витримується пауза `t[RST] = 35 мкс`, після чого Flash-пам'ять гарантовано повертається у базовий однобітовий стан `1-1-1`.

---

## 9. Асинхронне програмування сторінок через DMA

Для високошвидкісного запису великих обсягів даних (наприклад, під час оновлення прошивки по бездротовому інтерфейсу OTA) використовується непрямий режим запису (**Indirect Write Mode**) у поєднанні з прямим доступом до пам'яті (**DMA**):
1. **Налаштування регістрів QUADSPI**: у регістрі `QUADSPI_DLR` встановлюється точна кількість байтів передачі (наприклад, 256 байтів для сторінки). У регістрі `QUADSPI_CCR` вмикається команда швидкого запису `0x32` (*Quad Page Program*), розрядність адреси 24 біти та 4 лінії даних.
2. **Конфігурація потоку DMA**: потік DMA (наприклад, `MDMA` у STM32H7) конфігурується у режимі «пам'ять-периферія» з джерелом у внутрішній SRAM та адресою призначення у регістрі `QUADSPI_DR`.
3. **Активація прапорця DMAEN**: встановлення біта `DMAEN` у регістрі `QUADSPI_CR` активує генерацію запитів DMA щоразу, коли 32-байтний вхідний FIFO контролера звільняє місце для нової порції слів.
4. **Подвійна буферизація (Double Buffering)**: поки DMA асинхронно викачує поточний 256-байтний буфер на шину QSPI, обчислювальне ядро процесора паралельно готує та розшифровує наступний пакет даних у другому буфері оперативної пам'яті.

Після передачі останнього байта сторінки контролер QUADSPI автоматично піднімає сигнал `CS#` та генерує переривання завершення передачі `TC` (*Transfer Complete*), після чого драйвер перемикається в режим автоопитування біта зайнятості `WIP`.

---

## 10. Релокація таблиці векторів переривань (VTOR) та прошивка через відлагоджувач

У системах, де основна програма або операційна система реального часу (FreeRTOS, Zephyr) повністю розміщується у зовнішній Flash-пам'яті, а внутрішня Flash містить лише компактний первинний завантажувач:
1. Завантажувач виконує ініціалізацію тактування, GPIO та переводить контролер QUADSPI у режим `Memory-Mapped Mode`.
2. Виконується релокація таблиці векторів переривань записом нової базової адреси у системний регістр ядра ARM Cortex-M:

:::tabs
```c
SCB->VTOR = QSPI_FLASH_BASE_ADDR;
__DSB();
__ISB();
```
```cpp
SCB->VTOR = QspiXipController::FlashBaseAddress;
__DSB();
__ISB();
```
:::

3. Після виконання бар'єрів інструкцій та даних (`__DSB()`, `__ISB()`) процесорне ядро починає вибірку обробників переривань та стеків виклику безпосередньо з адресного простору `0x90000000`, перетворюючи зовнішню Flash-пам'ять на повноцінне системне сховище коду.

4. **Пріоритезація переривань та захист від помилок шини**:
   * Обробник помилок шини `BusFault_Handler` та системних винятків `HardFault_Handler` рекомендується залишати у внутрішній пам'яті SRAM або внутрішній Flash, щоб гарантувати коректне перехоплення аварійних ситуацій навіть у разі фізичного пошкодження або відключення зовнішньої мікросхеми QSPI.
   * Для переривань із критичними вимогами до часу реакції (наприклад, ШІМ-керування силовими ключами інвертора або обробка сигналів енкодера) відповідні функції ISR позначаються атрибутом секції `.ramfunc` для виконання з нульовою затримкою безпосередньо з надшвидкої пам'яті ITCM RAM.
   * Для прошивки образу коду безпосередньо у зовнішню QSPI Flash через відлагоджувачі SEGGER J-Link або OpenOCD використовується спеціалізований алгоритм завантаження (*Flash Loader Algorithm*, файл `.stldr` або `.FLM`), який попередньо ініціалізує контролер QSPI перед початком сесії запису.
