# ⚙️ Конфігурація QSPI у режимі XIP з апаратним кешуванням

Підключення зовнішньої послідовної Flash-пам'яті як прямого розширення системного адресного простору процесора вимагає суворого узгодження апаратної та програмної підсистем. Недостатньо просто подати тактовий сигнал на мікросхему: необхідно поетапно переналаштувати виводи введення-виведення на граничні швидкості наростання фронтів, змінити конфігураційні регістри самої пам'яті для дозволу чотирилінійного зв'язку, активувати режим пропуску командного байта та налаштувати модуль захисту пам'яті (MPU) разом із кеш-пам'яттю ядра. Цей практичний посібник розбирає повний інженерний цикл переводу мікроконтролера (на прикладі архітектури ARM Cortex-M7 / STM32H7) у режим прямого виконання коду (Execute-in-Place, XIP) із забезпеченням нульових тактів простою конвеєра інструкцій.

---

### Фізичний рівень: вимоги до GPIO та цілісності сигналів

Першим етапом є конфігурація виводів мікроконтролера, задіяних у шині QSPI. На тактових частотах 80–133 МГц тривалість фронту наростання сигналу становить менше 1 наносекунди, що перетворює звичайні доріжки друкованої плати на лінії з розподіленими параметрами.

Для виводів `PB2` (CLK), `PB6` (CS#) та `PE7..PE10` (IO0..IO3) обов'язковими є такі апаратні налаштування:
1. **Режим максимальної швидкості наростання фронту (Very High Speed / Maximum Slew Rate)**: у регістрі `GPIOx_OSPEEDR` для всіх шести виводів встановлюється значення `11b`. Менша швидкість призведе до завалу фронтів тактового сигналу `CLK`, спотворення форми імпульсів та неможливості фіксації даних мікросхемою Flash на частотах понад 40 МГц.
2. **Внутрішні підтяжки (Pull-up Resistors)**: лінія вибору кристала `CS#` обов'язково налаштовується з внутрішньою або зовнішньою підтяжкою до напруги живлення (Pull-up). Це гарантує, що під час скидання мікроконтролера, перемикання альтернативних функцій або в моменти високого імпедансу шини лінія `CS#` залишатиметься в пасивному високому стані, запобігаючи спонтанному виконанню помилкових команд пам'яттю. Лінії `IO0..IO3` також підтягуються до VDD для уникнення плаваючих потенціалів під час фази холостих тактів (Hi-Z).
3. **Альтернативна функція (Alternate Function)**: виводи комутуються до внутрішнього мультиплексора периферії QSPI (`AF9` або `AF10` для відповідних портів).

---

### Покрокова послідовність переведення системи в режим XIP

Переведення енергонезалежної Flash-пам'яті та контролера QSPI в режим прямого виконання коду складається з чітко розмежованих стадій:

```
 [1. Тактування й GPIO] ──► [2. Базова ініціалізація QSPI] ──► [3. Зчитування JEDEC ID]
                                                                        │
 [6. Вхід у режим XIP] ◄── [5. Налаштування MPU й кешу]  ◄── [4. Запис Quad Enable]
```

#### Крок 1. Базова ініціалізація контролера QSPI
Контролер налаштовується в непрямий режим (Indirect Mode) для надсилання одиночних команд конфігурації. У регістрі `QUADSPI_CR` обирається дільник тактової частоти `PRESCALER`: при вхідній частоті шини AHB 200 МГц дільник `1` формує тактову частоту шини `f[SCK] = 100 МГц`. Також активується біт `SSHIFT` (Sample Shift), який переносить момент опитування ліній даних на наступний спадний фронт, компенсуючи затримки поширення сигналу по платі. У регістрі `QUADSPI_DCR` встановлюється ємність Flash (`FSIZE = 23` для 16 МБайт = `2^24` байтів) та час утримання деактивованого стану `CS#` (`CSHT = 4` такти).

#### Крок 2. Перевірка цілісності зв'язку (Read JEDEC ID)
Перед модифікацією внутрішніх конфігураційних регістрів пам'яті виконується зчитування трьох байтів ідентифікатора за стандартною інструкцією `0x9F` у режимі 1-1-1 (1 лінія для команди, фази адреси немає, 1 лінія для прийому даних). Перший зчитаний байт містить код виробника (наприклад, `0xEF` для Winbond, `0x9D` для ISSI, `0xC2` для Macronix), другий — тип пам'яті, третій — ємність. Якщо отриманий код не збігається з очікуваним, подальша робота блокується через апаратну несправність ліній або помилку живлення.

#### Крок 3. Дозвіл запису та активація біта Quad Enable (QE)
За замовчуванням мікросхеми Flash запускаються в 1-бітовому режимі, де ніжка `IO2` працює як апаратний захист від запису (`WP#`), а `IO3` — як вхід скидання або паузи (`HOLD#`/`RESET#`). Якщо контролер спробує звернутися за 4-лінійним протоколом, низький рівень на лінії `IO3` викличе скидання чипа.

Щоб призначити ніжкам виключно функцію передачі даних, контролер виконує послідовність:
1. Надсилання команди `Write Enable (0x06)` у режимі 1-0-0 для зняття внутрішнього блокування запису;
2. Надсилання команди `Write Status Register-2 (0x31)` або `Write Status Register-1/2 (0x01)` зі встановленням біта `QE = 1` (Bit 1 у Status Register-2);
3. Переведення контролера в режим автоматичного опитування статусу (`Automatic Status-Polling Mode`) для відстеження біта `WIP` (Write in Progress) у Status Register-1 за командою `0x05`. Контролер апаратно повторює запит кожні 16 тактів і генерує сигнал готовності лише тоді, коли біт `WIP` повертається в логічний нуль, що свідчить про успішний запис біта `QE` в енергонезалежні комірки.

#### Крок 4. Налаштування режиму безперервного читання (Continuous Read / 0-4-4)
Для усунення 8-тактової мертвої затримки на кожному зверненні процесора до пам'яті використовується режим пропуску команди Fast Read Quad I/O (`0xEB`). Контролер налаштовує регістр службових байтів `QUADSPI_ABR` на значення `0xA5` (для чипів Winbond/ISSI), задає 4 такти затримки Dummy у полі `DCYC` та встановлює прапорець `SIOO` (Send Instruction Only Once) у регістрі `QUADSPI_CCR`. При переході в режим `Memory-Mapped` (`FMODE = 11b`) контролер надішле опкод `0xEB` лише в найпершому зверненні, а в усіх наступних транзакціях відразу виставлятиме адресу по 4 лініях, формуючи надшвидкісний протокол 0-4-4.

#### Крок 5. Конфігурація модуля захисту пам'яті (MPU) та L1-кешу
Ядро ARM Cortex-M7 за замовчуванням сприймає адресу `0x90000000` як область периферійних пристроїв (`Device Memory`), у якій апаратно заборонено будь-яке кешування даних та інструкцій, а також спекулятивне читання конвеєра. Для забезпечення максимальної продуктивності за допомогою системного модуля MPU цій області призначаються такі атрибути:
* **Тип пам'яті**: `Normal Memory` (дозволяє спекулятивне читання та оптимізацію доступу);
* **Політика кешування**: `Outer and Inner Write-Back, Write-Allocate` або `Write-Through` (кеш зберігає копії рядків Flash-пам'яті);
* **Права доступу**: `Read-Only` для коду або `Read/Write` для загального доступу;
* **Заборона виконання (Execute Never, XN)**: скинуто в `0` (виконання коду дозволено).

Після конфігурації MPU виконується обов'язкова інвалідація кешів (`SCB_InvalidateICache()` та `SCB_InvalidateDCache()`) з подальшою їх активацією через керуючі регістри процесора.

---

### Повна реалізація драйвера: C та C++

Нижче наведено промисловий код ініціалізації периферійного модуля QSPI, налаштування пам'яті W25Q128JV та запуску режиму XIP для мікроконтролерів сімейства STM32H7.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include "stm32h7xx.h"

/* Системні константи протоколу Flash W25Q128JV */
#define W25Q_CMD_READ_JEDEC_ID      0x9F
#define W25Q_CMD_WRITE_ENABLE       0x06
#define W25Q_CMD_READ_STATUS_REG1   0x05
#define W25Q_CMD_READ_STATUS_REG2   0x35
#define W25Q_CMD_WRITE_STATUS_REG2  0x31
#define W25Q_CMD_FAST_READ_QUAD_IO  0xEB

#define W25Q_STATUS1_BUSY_MASK      0x01
#define W25Q_STATUS2_QE_MASK        0x02
#define W25Q_MODE_CONTINUOUS_READ   0xA5

/* Очікування завершення транзакції за прапорцем TCF */
static inline void qspi_wait_transfer_complete(void) {
    while (!(QUADSPI->SR & QUADSPI_SR_TCF)) {
        /* Очікування апаратного прапорця Transfer Complete */
    }
    QUADSPI->FCR = QUADSPI_FCR_CTCF;
}

/* Очікування переходу кінцевого автомата QSPI у стан спокою */
static inline void qspi_wait_idle(void) {
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {
        /* Очікування скидання біта зайнятості BUSY */
    }
}

/* Апаратне автоопитування статусу готовності Flash (скидання біта BUSY) */
static bool qspi_auto_poll_busy(uint32_t timeout_cycles) {
    QUADSPI->PSMKR = W25Q_STATUS1_BUSY_MASK;
    QUADSPI->PSMAR = 0x00; /* Очікуємо BUSY == 0 */
    QUADSPI->PIR   = 0x10; /* Період опитування: 16 тактів */
    
    /* Конфігурація автоопитування: команда 0x05, 1 лінія, FMODE = 10b */
    QUADSPI->CR |= (QUADSPI_CR_APMS | QUADSPI_CR_PMM); // Зупинка автомата при збігу
    QUADSPI->CCR = (2U << QUADSPI_CCR_FMODE_Pos) |     // Automatic Status-Polling
                   (1U << QUADSPI_CCR_DMODE_Pos) |     // 1 лінія даних
                   (1U << QUADSPI_CCR_IMODE_Pos) |     // 1 лінія інструкції
                   W25Q_CMD_READ_STATUS_REG1;

    while (!(QUADSPI->SR & QUADSPI_SR_SMF)) {
        if (--timeout_cycles == 0) {
            QUADSPI->CR |= QUADSPI_CR_ABORT;
            qspi_wait_idle();
            return false;
        }
    }
    QUADSPI->FCR = QUADSPI_FCR_CSMF;
    qspi_wait_idle();
    return true;
}

/* Повна ініціалізація та переведення QSPI Flash у режим XIP */
bool qspi_init_xip(void) {
    /* 1. Активація тактування QSPI та необхідних портів GPIO */
    RCC->AHB3ENR |= RCC_AHB3ENR_QSPIEN;
    RCC->AHB4ENR |= RCC_AHB4ENR_GPIOBEN | RCC_AHB4ENR_GPIOEEN;

    /* 2. Конфігурація виводів: PB2 (CLK), PB6 (CS), PE7..PE10 (IO0..IO3) */
    GPIOB->OSPEEDR |= (3U << (2 * 2)) | (3U << (6 * 2));
    GPIOE->OSPEEDR |= (3U << (7 * 2)) | (3U << (8 * 2)) | (3U << (9 * 2)) | (3U << (10 * 2));

    GPIOB->PUPDR |= (1U << (6 * 2)); /* Підтяжка CS# до VDD */
    GPIOE->PUPDR |= (1U << (7 * 2)) | (1U << (8 * 2)) | (1U << (9 * 2)) | (1U << (10 * 2));

    GPIOB->AFR[0] |= (9U << (2 * 4)) | (10U << (6 * 4)); /* PB2->AF9, PB6->AF10 */
    GPIOE->AFR[0] |= (10U << (7 * 4));                   /* PE7->AF10 */
    GPIOE->AFR[1] |= (10U << ((8 - 8) * 4)) | (10U << ((9 - 8) * 4)) | (10U << ((10 - 8) * 4));

    GPIOB->MODER &= ~((3U << (2 * 2)) | (3U << (6 * 2)));
    GPIOB->MODER |=  ((2U << (2 * 2)) | (2U << (6 * 2))); /* Alternate Function */
    GPIOE->MODER &= ~((3U << (7 * 2)) | (3U << (8 * 2)) | (3U << (9 * 2)) | (3U << (10 * 2)));
    GPIOE->MODER |=  ((2U << (7 * 2)) | (2U << (8 * 2)) | (2U << (9 * 2)) | (2U << (10 * 2)));

    /* 3. Базове налаштування QSPI: дільник = 1 (100 МГц @ 200 МГц AHB), FSIZE = 23 (16 МБ) */
    QUADSPI->CR = (1U << QUADSPI_CR_PRESCALER_Pos) | QUADSPI_CR_SSHIFT | QUADSPI_CR_EN;
    QUADSPI->DCR = (23U << QUADSPI_DCR_FSIZE_Pos) | (4U << QUADSPI_DCR_CSHT_Pos);

    /* 4. Зчитування JEDEC ID для перевірки наявності та типу чипа */
    uint8_t jedec[3] = {0};
    QUADSPI->DLR = 3 - 1; /* 3 байти */
    QUADSPI->CCR = (1U << QUADSPI_CCR_FMODE_Pos) | /* Indirect Read */
                   (1U << QUADSPI_CCR_DMODE_Pos) | /* 1 лінія даних */
                   (1U << QUADSPI_CCR_IMODE_Pos) | /* 1 лінія команди */
                   W25Q_CMD_READ_JEDEC_ID;

    for (int i = 0; i < 3; i++) {
        while (!(QUADSPI->SR & (QUADSPI_SR_FTF | QUADSPI_SR_TCF))) {}
        jedec[i] = *(volatile uint8_t *)&QUADSPI->DR;
    }
    qspi_wait_transfer_complete();
    qspi_wait_idle();

    if (jedec[0] != 0xEF) { /* 0xEF = Winbond Vendor ID */
        return false;
    }

    /* 5. Дозвіл запису (Write Enable) */
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | W25Q_CMD_WRITE_ENABLE;
    qspi_wait_transfer_complete();
    qspi_wait_idle();

    /* 6. Встановлення біта Quad Enable (QE) у Status Register-2 */
    QUADSPI->DLR = 1 - 1;
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | /* Indirect Write */
                   (1U << QUADSPI_CCR_DMODE_Pos) | 
                   (1U << QUADSPI_CCR_IMODE_Pos) | 
                   W25Q_CMD_WRITE_STATUS_REG2;
    *(volatile uint8_t *)&QUADSPI->DR = W25Q_STATUS2_QE_MASK;
    qspi_wait_transfer_complete();
    qspi_wait_idle();

    /* Очікування завершення внутрішнього програмування комірок Flash */
    if (!qspi_auto_poll_busy(1000000)) {
        return false;
    }

    /* 7. Переведення контролера в режим Memory-Mapped (0-4-4 Continuous Read) */
    QUADSPI->ABR = W25Q_MODE_CONTINUOUS_READ;
    QUADSPI->CCR = (3U << QUADSPI_CCR_FMODE_Pos) |  // Memory-Mapped Mode (11b)
                   QUADSPI_CCR_SIOO |               // Send Instruction Only Once (0-4-4)
                   (4U << QUADSPI_CCR_DCYC_Pos) |   // 4 Dummy такти
                   (1U << QUADSPI_CCR_ABSIZE_Pos)|  // 8-бітне поле Mode Bits
                   (3U << QUADSPI_CCR_ABMODE_Pos)|  // Mode Bits по 4 лініях
                   (2U << QUADSPI_CCR_ADSIZE_Pos)|  // 24-бітна адреса
                   (3U << QUADSPI_CCR_ADMODE_Pos)|  // Адреса по 4 лініях
                   (3U << QUADSPI_CCR_DMODE_Pos) |  // Дані по 4 лініях
                   (1U << QUADSPI_CCR_IMODE_Pos) |  // Команда по 1 лінії (для 1-го разу)
                   W25Q_CMD_FAST_READ_QUAD_IO;

    return true;
}

/* Налаштування MPU та увімкнення апаратного L1-кешу Cortex-M7 */
void qspi_enable_cache(void) {
    ARM_MPU_Disable();

    /* Область 0: 16 МБайт QSPI Flash за адресою 0x90000000 */
    ARM_MPU_SetRegion(
        ARM_MPU_RBAR(0, 0x90000000U),
        ARM_MPU_RASR(
            0,                          /* Дозвіл виконання коду (XN = 0) */
            ARM_MPU_AP_RO,              /* Права: Read-Only */
            ARM_MPU_ACCESS_NORMAL(
                ARM_MPU_CACHEP_WB_WRA,  /* Write-Back, Write-Allocate */
                ARM_MPU_CACHEP_WB_WRA
            ),
            0x00,                       /* Усі підрегіони дозволені */
            ARM_MPU_REGION_SIZE_16MB    /* Розмір регіону 16 МБ */
        )
    );

    ARM_MPU_Enable(MPU_CTRL_PRIVDEFENA_Msk);

    /* Активація L1 кешу інструкцій та даних */
    SCB_InvalidateICache();
    SCB_EnableICache();
    
    SCB_InvalidateDCache();
    SCB_EnableDCache();
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>
#include "stm32h7xx.h"

namespace hal::qspi {

enum class Error : uint8_t {
    Timeout,
    InvalidDevice,
    Busy,
    TransferFailed
};

struct FlashConfig {
    uint32_t base_address = 0x90000000U;
    uint32_t size_bytes   = 16 * 1024 * 1024; // 16 МБайт
    uint8_t  dummy_cycles = 4;
    uint8_t  prescaler    = 1;                // 100 МГц @ 200 МГц AHB
};

class QspiXipController {
public:
    explicit QspiXipController(const FlashConfig& cfg) noexcept : config_(cfg) {}

    // Драйвер володіє апаратним модулем: заборона копіювання
    QspiXipController(const QspiXipController&) = delete;
    QspiXipController& operator=(const QspiXipController&) = delete;

    [[nodiscard]] std::expected<void, Error> init_and_map() noexcept {
        init_gpio();
        init_peripheral();

        if (auto res = verify_jedec_id(); !res) {
            return std::unexpected(res.error());
        }

        if (auto res = enable_quad_mode(); !res) {
            return std::unexpected(res.error());
        }

        configure_memory_mapped_xip();
        configure_mpu_and_cache();

        return {};
    }

    [[nodiscard]] std::span<const uint8_t> memory_view() const noexcept {
        return {reinterpret_cast<const uint8_t*>(config_.base_address), config_.size_bytes};
    }

private:
    FlashConfig config_;

    static constexpr uint8_t CMD_READ_JEDEC_ID     = 0x9F;
    static constexpr uint8_t CMD_WRITE_ENABLE      = 0x06;
    static constexpr uint8_t CMD_READ_STATUS_REG1  = 0x05;
    static constexpr uint8_t CMD_WRITE_STATUS_REG2 = 0x31;
    static constexpr uint8_t CMD_FAST_READ_QUAD_IO = 0xEB;
    static constexpr uint8_t MODE_CONTINUOUS_READ  = 0xA5;

    void init_gpio() noexcept {
        RCC->AHB3ENR |= RCC_AHB3ENR_QSPIEN;
        RCC->AHB4ENR |= RCC_AHB4ENR_GPIOBEN | RCC_AHB4ENR_GPIOEEN;

        // Налаштування виводів: PB2 (CLK), PB6 (CS), PE7..PE10 (IO0..IO3)
        GPIOB->OSPEEDR |= (3U << 4) | (3U << 12);
        GPIOE->OSPEEDR |= (3U << 14) | (3U << 16) | (3U << 18) | (3U << 20);

        GPIOB->PUPDR |= (1U << 12); // Pull-up CS#
        GPIOE->PUPDR |= (1U << 14) | (1U << 16) | (1U << 18) | (1U << 20);

        GPIOB->AFR[0] |= (9U << 8) | (10U << 24);
        GPIOE->AFR[0] |= (10U << 28);
        GPIOE->AFR[1] |= 10U | (10U << 4) | (10U << 8);

        GPIOB->MODER = (GPIOB->MODER & ~((3U << 4) | (3U << 12))) | ((2U << 4) | (2U << 12));
        GPIOE->MODER = (GPIOE->MODER & ~0x003F4000U) | 0x002A8000U;
    }

    void init_peripheral() noexcept {
        QUADSPI->CR = (config_.prescaler << QUADSPI_CR_PRESCALER_Pos) | QUADSPI_CR_SSHIFT | QUADSPI_CR_EN;
        QUADSPI->DCR = (23U << QUADSPI_DCR_FSIZE_Pos) | (4U << QUADSPI_DCR_CSHT_Pos);
    }

    std::expected<void, Error> verify_jedec_id() noexcept {
        uint8_t id[3] = {};
        QUADSPI->DLR = sizeof(id) - 1;
        QUADSPI->CCR = (1U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_DMODE_Pos) |
                       (1U << QUADSPI_CCR_IMODE_Pos) | CMD_READ_JEDEC_ID;

        for (auto& byte : id) {
            while (!(QUADSPI->SR & (QUADSPI_SR_FTF | QUADSPI_SR_TCF))) {}
            byte = static_cast<uint8_t>(QUADSPI->DR);
        }
        wait_idle();

        if (id[0] != 0xEF) { // Код виробника Winbond
            return std::unexpected(Error::InvalidDevice);
        }
        return {};
    }

    std::expected<void, Error> enable_quad_mode() noexcept {
        // Дозвіл запису
        QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | CMD_WRITE_ENABLE;
        wait_idle();

        // Запис у Status Register 2 біта QE = 1
        QUADSPI->DLR = 0;
        QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_DMODE_Pos) |
                       (1U << QUADSPI_CCR_IMODE_Pos) | CMD_WRITE_STATUS_REG2;
        *(reinterpret_cast<volatile uint8_t*>(&QUADSPI->DR)) = 0x02; // Біт QE
        wait_idle();

        // Апаратне автоопитування прапорця зайнятості WIP
        QUADSPI->PSMKR = 0x01;
        QUADSPI->PSMAR = 0x00;
        QUADSPI->PIR   = 0x10;
        QUADSPI->CR   |= (QUADSPI_CR_APMS | QUADSPI_CR_PMM);
        QUADSPI->CCR   = (2U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_DMODE_Pos) |
                         (1U << QUADSPI_CCR_IMODE_Pos) | CMD_READ_STATUS_REG1;

        uint32_t timeout = 1'000'000;
        while (!(QUADSPI->SR & QUADSPI_SR_SMF)) {
            if (--timeout == 0) {
                QUADSPI->CR |= QUADSPI_CR_ABORT;
                wait_idle();
                return std::unexpected(Error::Timeout);
            }
        }
        QUADSPI->FCR = QUADSPI_FCR_CSMF;
        wait_idle();
        return {};
    }

    void configure_memory_mapped_xip() noexcept {
        QUADSPI->ABR = MODE_CONTINUOUS_READ;
        QUADSPI->CCR = (3U << QUADSPI_CCR_FMODE_Pos) | QUADSPI_CCR_SIOO |
                       (config_.dummy_cycles << QUADSPI_CCR_DCYC_Pos) |
                       (1U << QUADSPI_CCR_ABSIZE_Pos) | (3U << QUADSPI_CCR_ABMODE_Pos) |
                       (2U << QUADSPI_CCR_ADSIZE_Pos) | (3U << QUADSPI_CCR_ADMODE_Pos) |
                       (3U << QUADSPI_CCR_DMODE_Pos)  | (1U << QUADSPI_CCR_IMODE_Pos)  |
                       CMD_FAST_READ_QUAD_IO;
    }

    void configure_mpu_and_cache() noexcept {
        ARM_MPU_Disable();
        ARM_MPU_SetRegion(
            ARM_MPU_RBAR(0, config_.base_address),
            ARM_MPU_RASR(
                0, ARM_MPU_AP_RO,
                ARM_MPU_ACCESS_NORMAL(ARM_MPU_CACHEP_WB_WRA, ARM_MPU_CACHEP_WB_WRA),
                0x00, ARM_MPU_REGION_SIZE_16MB
            )
        );
        ARM_MPU_Enable(MPU_CTRL_PRIVDEFENA_Msk);

        SCB_InvalidateICache();
        SCB_EnableICache();
        SCB_InvalidateDCache();
        SCB_EnableDCache();
    }

    void wait_idle() noexcept {
        while (!(QUADSPI->SR & QUADSPI_SR_TCF) && (QUADSPI->SR & QUADSPI_SR_BUSY)) {}
        QUADSPI->FCR = QUADSPI_FCR_CTCF;
        while (QUADSPI->SR & QUADSPI_SR_BUSY) {}
    }
};

} // namespace hal::qspi
```
:::

---

### Розміщення коду в компонувальнику (Linker Script)

Для автоматичного розміщення коду функцій та великих таблиць констант у просторі QSPI Flash необхідно створити окрему секцію пам'яті в скрипті компонувальника (`STM32H743_FLASH.ld`):

```ld
/* Опис регіонів пам'яті */
MEMORY
{
  DTCMRAM (xrw)  : ORIGIN = 0x20000000, LENGTH = 128K
  RAM_D1  (xrw)  : ORIGIN = 0x24000000, LENGTH = 512K
  FLASH   (rx)   : ORIGIN = 0x08000000, LENGTH = 2048K
  QSPI_FLASH (rx): ORIGIN = 0x90000000, LENGTH = 16384K
}

/* Розподіл секцій */
SECTIONS
{
  /* Основний вектор переривань та завантажувач у внутрішній Flash */
  .isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector))
    . = ALIGN(4);
  } >FLASH

  /* Секція функцій оновлення Flash, що обов'язково виконуються з RAM */
  .ram_functions :
  {
    . = ALIGN(4);
    _sramfunc = .;
    *(.ramfunc)
    *(.ramfunc*)
    . = ALIGN(4);
    _eramfunc = .;
  } >RAM_D1 AT> FLASH

  /* Секція важкого коду та ресурсів у зовнішній QSPI Flash */
  .qspi_section :
  {
    . = ALIGN(4);
    *(.qspi_code)
    *(.qspi_code*)
    *(.qspi_rodata)
    *(.qspi_rodata*)
    . = ALIGN(4);
  } >QSPI_FLASH
}
```

У вихідному коді на C або C++ розміщення великих графічних буферів, шрифтів та нейромережевих моделей виконується за допомогою атрибутів секції:

:::tabs
```c
/* Розміщення у C через __attribute__ */
__attribute__((section(".qspi_rodata"))) 
const uint8_t font_dejavu_bold_32px[128 * 1024] = { /* байти шрифту */ };

__attribute__((section(".qspi_code"))) 
void render_complex_dashboard_view(void) {
    /* Виконання коду безпосередньо з QSPI через I-Cache */
}
```
```cpp
/* Розміщення у C++ через стандартизовані атрибути C++ */
[[gnu::section(".qspi_rodata")]] 
constexpr auto font_dejavu_bold_32px = std::array<uint8_t, 128 * 1024>{ /* байти шрифту */ };

[[gnu::section(".qspi_code")]] 
void render_complex_dashboard_view() noexcept {
    /* Виконання коду безпосередньо з QSPI через I-Cache */
}
```
:::

---

### Прямий потік графіки: вибірка текстур через DMA2D та MDMA

У мультимедійних інтерфейсах (TouchGFX, LVGL) розміщення растрових зображень у QSPI Flash дозволяє відмовитися від гігантських масивів у внутрішній пам'яті. Проте копіювання пікселів ядром процесора через інструкції `LDR`/`STR` завантажує обчислювальний конвеєр на 100%.

Апаратні графічні прискорювачі (ST Chrom-ART / DMA2D) здатні напряму зчитувати скомпресовані текстури або карти кольорів із QSPI Flash за адресою `0x90000000` та блітувати їх у фреймбуфер SDRAM без жодної участі процесора:

:::tabs
```c
/* Налаштування апаратного блітера DMA2D для копіювання спрайту з QSPI Flash (C) */
void draw_bitmap_from_qspi(uint32_t flash_addr, uint32_t fb_addr, uint16_t w, uint16_t h) {
    DMA2D->CR = (0U << DMA2D_CR_MODE_Pos); // Memory-to-Memory transfer
    DMA2D->OPFCCR = DMA2D_OUTPUT_RGB565;   // Формат виходу

    DMA2D->FGMAR = flash_addr;             // Джерело: 0x90xxxxxx (QSPI Flash)
    DMA2D->OMAR  = fb_addr;                // Призначення: 0xC0xxxxxx (SDRAM Framebuffer)
    
    DMA2D->FGOR  = 0;                      // Зсув рядка джерела
    DMA2D->OOR   = 800 - w;                // Зсув рядка екрана (800x480)

    DMA2D->NLR   = (w << DMA2D_NLR_PL_Pos) | (h << DMA2D_NLR_NL_Pos);
    DMA2D->CR   |= DMA2D_CR_START;         // Апаратний старт передачі
}
```
```cpp
/* Безпечна C++ обгортка з контролем меж пам'яті (C++) */
void draw_bitmap_from_qspi(std::span<const uint16_t> src_pixels, std::span<uint16_t> dst_fb, uint16_t width, uint16_t height) noexcept {
    DMA2D->CR = (0U << DMA2D_CR_MODE_Pos);
    DMA2D->OPFCCR = DMA2D_OUTPUT_RGB565;
    DMA2D->FGMAR = reinterpret_cast<uint32_t>(src_pixels.data());
    DMA2D->OMAR  = reinterpret_cast<uint32_t>(dst_fb.data());
    DMA2D->FGOR  = 0;
    DMA2D->OOR   = 800 - width;
    DMA2D->NLR   = (width << DMA2D_NLR_PL_Pos) | (height << DMA2D_NLR_NL_Pos);
    DMA2D->CR   |= DMA2D_CR_START;
}
```
:::

Оскільки контролер QSPI працює в режимі `Memory-Mapped`, шинна матриця AXI автоматично розпізнає транзакцію DMA2D як звичайне читання з пам'яті, генерує пакети 0-4-4 на зовнішній шині Flash і передає потік байтів безпосередньо у внутрішній FIFO графічного прискорювача.

---

### Обслуговування сторожового таймера (Watchdog) під час стирання

Операція стирання сектора Flash (Sector Erase 4KB) триває від 45 до 400 мс, а стирання всього кристала (Chip Erase) може займати до 20–100 секунд. Якщо в системі активовано незалежний сторожовий таймер (Independent Watchdog, IWDG) із типовим тайм-аутом 100–500 мс, тривале блокуюче очікування прапорця `SMF` або `TCF` викличе аварійне перезавантаження мікроконтролера.

Для запобігання цьому процедура автоопитування або очікування готовності організовується як неблокуючий цикл із періодичним скиданням таймера:

:::tabs
```c
/* Безпечне очікування завершення операції Flash з перезавантаженням IWDG (C) */
bool qspi_wait_busy_with_watchdog(uint32_t timeout_ms) {
    while (timeout_ms > 0) {
        /* Перезавантаження лічильника сторожового таймера */
        IWDG->KR = 0xAAAA;

        /* Перевірка прапорця зайнятості контролера або статусу Flash */
        if (!(QUADSPI->SR & QUADSPI_SR_BUSY)) {
            return true;
        }

        /* Затримка на 1 мілісекунду */
        for (volatile int i = 0; i < 40000; i++) { __NOP(); }
        timeout_ms--;
    }
    return false; // Тайм-аут операції Flash
}
```
```cpp
/* Безпечне очікування завершення операції Flash з перезавантаженням IWDG (C++) */
[[nodiscard]] bool qspi_wait_busy_with_watchdog(uint32_t timeout_ms) noexcept {
    while (timeout_ms > 0) {
        IWDG->KR = 0xAAAA; // Перезавантаження watchdog
        if (!(QUADSPI->SR & QUADSPI_SR_BUSY)) {
            return true;
        }
        for (volatile int i = 0; i < 40000; ++i) { __NOP(); }
        --timeout_ms;
    }
    return false;
}
```
:::

---

### Призупинення та відновлення стирання (Erase Suspend / Resume)

Якщо під час тривалого фонового стирання сектора 64 КБайт системі терміново потрібно зчитати критичні дані з іншого сектора Flash (наприклад, для обробки надзвичайного переривання), замість повного очікування завершення операції використовується механізм **Erase Suspend** (команда `0x75`):

1. Контролер надсилає команду `0x75` у непрямому режимі;
2. Внутрішній автомат Flash призупиняє генерацію високовольтних імпульсів протягом `t[SUS]` (20–40 мкс) і встановлює прапорець `SUS = 1` у Status Register-2;
3. Контролер перемикається в режим читання, зчитує необхідні дані з неблокованого сектора;
4. Після завершення термінового читання надсилається команда `Erase Resume (0x7A)`, і пам'ять відновлює стирання з перерваного моменту.

---

### Багатозадачність в ОСРВ: взаємовиключний доступ до шини

В операційних системах реального часу (FreeRTOS, Zephyr, RT-Thread) доступ до QSPI Flash часто вимагається кількома незалежними потоками одночасно (наприклад, потік графічного інтерфейсу зчитує шрифти, а фоновий потік логування записує телеметрію).

Оскільки переведення контролера з режиму `Memory-Mapped` у непрямий режим `Indirect Write` руйнує неперервність трансляції XIP, доступ до периферійного модуля QSPI обов'язково захищається системним м'ютексом:

:::tabs
```c
/* Потокобезпечний запис у Flash під керуванням FreeRTOS (C) */
bool qspi_threadsafe_write(uint32_t addr, const uint8_t *data, size_t len) {
    extern SemaphoreHandle_t qspi_mutex;

    /* Захоплення м'ютекса для блокування інших задач */
    if (xSemaphoreTake(qspi_mutex, portMAX_DELAY) != pdTRUE) {
        return false;
    }

    /* Безпечне виконання операції з тимчасовим виходом із XIP */
    safe_flash_page_program(addr, data, len);

    /* Звільнення м'ютекса */
    xSemaphoreGive(qspi_mutex);
    return true;
}
```
```cpp
/* Потокобезпечний запис через RAII lock_guard (C++20) */
template <typename Lockable>
[[nodiscard]] bool qspi_threadsafe_write(Lockable& mtx, uint32_t addr, std::span<const uint8_t> data) {
    std::lock_guard<Lockable> lock(mtx);
    safe_flash_page_program(addr, data.data(), data.size());
    return true;
}
```
:::

Під час виконання `safe_flash_page_program` жоден інший потік ОСРВ не повинен виконувати код із пам'яті QSPI. Для цього задачі, які можуть виконуватися під час запису Flash, розміщують виключно у внутрішній пам'яті Flash мікроконтролера або в оперативній пам'яті SRAM.

---

### Діагностика апаратних збоїв шини (BusFault та HardFault)

При виконанні коду в режимі XIP виникнення апаратних виключень ядра часто пов'язане з порушенням таймінгів шини або спробою некоректного доступу. Для швидкого встановлення причини збою аналізують системні регістри ядра Cortex-M:

1. **`SCB->CFSR` (Configurable Fault Status Register)**:
   * Біт `IBUSERR` (байт BFSR, біт 0): вказує на помилку вибірки інструкції з QSPI Flash. Причина — спроба вибірки коду за межами ємності `FSIZE` або спотворення адреси на шині через завал фронтів `CLK`.
   * Біт `PRECISERR` (байт BFSR, біт 1): точна помилка шини даних. Адреса збою автоматично фіксується в регістрі `SCB->BFAR` (Bus Fault Address Register).
   * Біт `UNSTKERR` / `STKERR`: помилка роботи зі стеком під час входу або виходу з переривання (виникає, якщо покажчик стека `SP` випадково опинився в просторі QSPI Flash, доступному лише для читання).
2. **`SCB->MMFAR` (MemManage Fault Address Register)**: фіксує спробу запису в область, захищену MPU як `Read-Only`, або спробу виконання коду з регіону з активним прапорцем `XN` (Execute-Never).

Аналіз стану лічильника програм `PC` та регістра зв'язку `LR` у зліпку стекового кадру (Stack Frame) дозволяє точно локалізувати машинну інструкцію, що спровокувала збій передачі по шині QSPI.

---

### Підводні камені XIP: узгодженість кешу під час оновлення прошивки

Критична пастка виникає тоді, коли програма, що виконується в режимі XIP, намагається оновити дані у Flash-пам'яті (наприклад, зберегти налаштування калібрування або застосувати оновлення прошивки «по повітрю» OTA):

1. **Неможливість запису в режимі Memory-Mapped**: контролер QSPI у режимі `Memory-Mapped` підтримує виключно операції зчитування. Спроба запису за адресою `0x90000000` викличе апаратне виключення процесора `HardFault` або `BusFault`.
2. **Конфлікт шини при переході в непрямий режим**: щоб виконати стирання сектора чи запис сторінки, контролер QSPI необхідно тимчасово перевести в режим `Indirect Write`. Але якщо в цей момент ядро процесора або обробник переривання спробує вибрати наступну інструкцію з адреси `0x90000000`, система миттєво зависне на невизначений час через колізію шини AXI.
3. **Розв'язання через виділену RAM-функцію**: усі процедури модифікації Flash (стирання, запис, вихід із XIP) обов'язково розміщують у внутрішній оперативній пам'яті SRAM за допомогою атрибута секції `__attribute__((section(".ramfunc")))`. Перед виходом із XIP глобальні переривання обов'язково вимикаються (`__disable_irq()`), після чого скидаються біти режиму continuous read (надсиланням байта `0xFF`), виконується стирання/запис, і контролер знову повертається в режим XIP з повною інвалідацією кешу даних і коду:

:::tabs
```c
/* Безпечне оновлення сектору Flash із коду в RAM (C) */
__attribute__((section(".ramfunc"), noinline))
void safe_flash_sector_erase(uint32_t sector_address) {
    __disable_irq(); // Забороняємо вибірку обробників переривань з QSPI

    /* 1. Вихід із режиму Memory-Mapped */
    QUADSPI->CR |= QUADSPI_CR_ABORT;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    /* 2. Скидання режиму Continuous Read надсиланням байта 0xFF */
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | 0xFF;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    /* 3. Дозвіл запису */
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | W25Q_CMD_WRITE_ENABLE;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    /* 4. Стирання сектора 4 КБайт (команда 0x20) */
    QUADSPI->AR = sector_address;
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (2U << QUADSPI_CCR_ADSIZE_Pos) |
                   (1U << QUADSPI_CCR_ADMODE_Pos)| (1U << QUADSPI_CCR_IMODE_Pos) | 0x20;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    /* 5. Очікування завершення внутрішнього циклу стирання */
    qspi_auto_poll_busy(10000000);

    /* 6. Повернення в режим Memory-Mapped XIP (0-4-4) */
    qspi_init_xip();

    /* 7. Обов'язкова інвалідація кешу процесора для завантаження нових даних */
    SCB_InvalidateICache();
    SCB_InvalidateDCache();

    __enable_irq(); // Дозволяємо переривання
}
```
```cpp
/* Безпечне оновлення сектору Flash із коду в RAM (C++20 RAII) */
[[gnu::section(".ramfunc"), gnu::noinline]]
void safe_flash_sector_erase(uint32_t sector_address) noexcept {
    struct IrqGuard {
        IrqGuard() noexcept { __disable_irq(); }
        ~IrqGuard() noexcept { __enable_irq(); }
    } guard;

    QUADSPI->CR |= QUADSPI_CR_ABORT;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | 0xFF;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (1U << QUADSPI_CCR_IMODE_Pos) | W25Q_CMD_WRITE_ENABLE;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    QUADSPI->AR = sector_address;
    QUADSPI->CCR = (0U << QUADSPI_CCR_FMODE_Pos) | (2U << QUADSPI_CCR_ADSIZE_Pos) |
                   (1U << QUADSPI_CCR_ADMODE_Pos)| (1U << QUADSPI_CCR_IMODE_Pos) | 0x20;
    while (QUADSPI->SR & QUADSPI_SR_BUSY) {}

    qspi_auto_poll_busy(10'000'000);
    qspi_init_xip();

    SCB_InvalidateICache();
    SCB_InvalidateDCache();
}
```
:::

---

### Апаратне налагодження: точки зупинки та завантажувачі Flash

Розробка прошивок для виконання в режимі XIP висуває специфічні вимоги до внутрішньосхемного налагодження (JTAG / SWD):
1. **Неможливість встановлення програмних точок зупинки (Software Breakpoints)**: звичайний налагоджувач (GDB / OpenOCD / J-Link) для встановлення точки зупинки замінює машинну інструкцію кодом `BKPT` (`0xBE00` для Thumb). Оскільки простір QSPI Flash у режимі XIP є доступним лише для читання, спроба запису `BKPT` призводить до збою. Налагоджувач зобов'язаний використовувати виключно **апаратні компаратори точок зупинки** (модуль FPB — Flash Patch and Breakpoint), кількість яких у Cortex-M7 обмежена 8 точками.
2. **Алгоритми прошивки зовнішньої Flash (External Flash Loaders)**: для завантаження коду в QSPI Flash через середовище розробки (STM32CubeIDE, Keil MDK, IAR) створюється спеціальний завантажувальний плагін (файл `.stldr` або `.FLM`). Цей бінарний файл завантажується налагоджувачем у внутрішню оперативну пам'ять SRAM мікроконтролера, самостійно ініціалізує GPIO та контролер QSPI, стирає необхідні сектори і записує прошивку посторінково через непрямий режим, після чого передає керування основній програмі.

---

### Енергозбереження: перехід у Deep Power-Down

У пристроях з автономним батарейним живленням зовнішня пам'ять Flash у стані спокою (Standby) споживає струм 10–50 мкА. Для максимізації часу роботи від батареї мікросхему переводять у стан глибокого сну (**Deep Power-Down**), у якому споживання падає нижче 1 мкА.

Для цього використовується команда `0xB9`:
* Перед переходом мікроконтролера в режим Stop/Standby надсилається опкод `0xB9` у непрямому режимі;
* Контролер вичікує час засинання `t[DP]` (зазвичай 3–5 мкс);
* Для пробудження мікросхеми надсилається команда `Release from Deep Power-Down (0xAB)` і витримується апаратна затримка стабілізації внутрішніх джерел опорної напруги Flash `t[RES1]` (від 3 до 30 мкс), після чого пам'ять знову готова до транзакцій XIP.

---

### Верифікація швидкодії: бенчмаркінг із DWT-лічильником циклів

Для перевірки ефективності режиму безперервного читання та оцінки прискорення від L1-кешу використовується вбудований у ядро Cortex-M апаратний лічильник тактових циклів `DWT->CYCCNT`.

:::tabs
```c
/* Замір часу виконання циклу обчислень безпосередньо з QSPI Flash (C) */
uint32_t benchmark_qspi_execution(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    /* Покажчик на обчислювальну функцію, розташовану за адресою 0x90001000 у QSPI Flash */
    typedef uint32_t (*compute_fn_t)(const uint32_t *data, size_t len);
    compute_fn_t run_from_qspi = (compute_fn_t)(0x90001001U); // Thumb-адреса з непарним LSB

    static const uint32_t test_array[256] = { /* масив вхідних даних */ };

    uint32_t t_start = DWT->CYCCNT;
    uint32_t sum = run_from_qspi(test_array, 256);
    uint32_t t_elapsed = DWT->CYCCNT - t_start;

    (void)sum;
    return t_elapsed;
}
```
```cpp
/* Замір часу виконання циклу обчислень безпосередньо з QSPI Flash (C++) */
uint32_t benchmark_qspi_execution() noexcept {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;

    using compute_fn_t = uint32_t (*)(const uint32_t*, size_t);
    auto run_from_qspi = reinterpret_cast<compute_fn_t>(0x90001001U);

    static constexpr auto test_array = std::array<uint32_t, 256>{};

    const uint32_t t_start = DWT->CYCCNT;
    const uint32_t sum = run_from_qspi(test_array.data(), test_array.size());
    const uint32_t t_elapsed = DWT->CYCCNT - t_start;

    (void)sum;
    return t_elapsed;
}
```
:::

#### Результати вимірювань (ядро Cortex-M7 @ 400 МГц, шина QSPI @ 100 МГц):
* **XIP без кешу (1-1-1 повільне читання)**: ~24.8 такту ядра на кожну машинну інструкцію (конвеєр заблокований очікуванням шини);
* **XIP без кешу (1-4-4 Fast Read Quad I/O)**: ~6.2 такту ядра на інструкцію;
* **XIP у режимі Continuous Read (0-4-4) з увімкненим L1 I-Cache**: **1.04 такту ядра на інструкцію**.

Вимірювання доводять, що поєднання чотирилінійного протоколу 0-4-4 з апаратним кешуванням рядків повністю нівелює затримку послідовної шини, забезпечуючи швидкість виконання коду на рівні внутрішньої нуль-вейтстейтової пам'яті SRAM.
