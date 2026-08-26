# ⚙️ Алгоритм відновлення завислої шини I2C

Коли вбудований периферійний модуль I2C входить у стан апаратного блокування через дефект кремнію (наприклад, хибне спрацьовування аналогового фільтра або переповнення буфера переривання) або зовнішній ведений сенсор застрягає посеред передачі байта, утримуючи лінію даних SDA в низькому логічному рівні, стандартні функції читання та запису стають безпорадними. Жодна команда старту транзакції не може бути виконана, доки лінія SDA притиснута до землі, а сам апаратний блок контролера вважає шину постійно зайнятою (`BUSY = 1`). Для виведення шини та мікроконтролера з цього глухого кута необхідна чітка низькорівнева процедура відновлення.

## Фізика застрягання шини: чому слейв тримає лінію

Шина I2C побудована за схемотехнікою відкритого колектора (Open-Drain): спокійний стан ліній SCL та SDA формується зовнішніми підтягувальними резисторами до напруги живлення (3.3 В або 5 В). Жоден пристрій на шині не може примусово видати високий рівень напруги — вихідні транзистори вміють лише притягувати лінію до землі (логічний 0) або переходити у високоімпедансний стан (Hi-Z, що відповідає логічній 1 завдяки резисторам підтяжки).

Коли мікроконтролер виконує читання даних із зовнішнього датчика, датчик послідовно передає 8 бітів даних, виставляючи кожен біт на лінію SDA за тактовим імпульсом SCL від мастера. Якщо в процесі передачі байта (наприклад, після 3-го біта) мікроконтролер скидається за сторожовим таймером (Watchdog), зависає через кремнієвий збій або обриває транзакцію, зовнішній датчик нічого про це не знає. Його внутрішній скінченний автомат продовжує чекати наступного такту на лінії SCL.

Якщо поточний передаваний біт був нулем, вихідний польовий транзистор датчика залишається відкритим і намертво притискає лінію SDA до землі. Коли мікроконтролер перезавантажується і намагається ініціалізувати свій апаратний блок I2C, модуль бачить низький рівень на лінії SDA і фіксує помилку шини (`BUSY = 1` або `BERR = 1`). Апаратний блок відмовляється генерувати тактові імпульси SCL на зайнятій лінії. Виникає замкнене коло: слейв чекає такту SCL, щоб відпустити SDA, а мастер не дає такту SCL, бо SDA притиснута до нуля.

## Покроковий інженерний алгоритм відновлення

Для розриву цього циклу необхідно тимчасово відібрати керування виводами у апаратного блока I2C і виконати ручне тактування через загальні порти вводу-виводу (GPIO).

Алгоритм складається з п'яти послідовних фаз:

1. **Примусове апаратне скидання периферійного модуля**: через регістри керування тактуванням та скиданням (RCC) встановлюється біт скидання модуля I2C (наприклад, `RCC_APB1RSTR_I2C1RST`). Це скидає всі внутрішні тригери та скінченний автомат аналогового фільтра контролера в початковий стан.
2. **Переведення виводів у режим звичайного GPIO з відкритим стоком**: виводи SCL та SDA конфігуруються як виходи Open-Drain. Початково обидва виводи встановлюються у високий логічний рівень (транзистори закриті).
3. **Генерація серії тактових імпульсів на лінії SCL (Clock Toggling)**: процесор вручну формує до дев'яти тактових імпульсів на лінії SCL із часовими затримками близько 5 мкс (що відповідає швидкості 100 кГц). При кожному переході SCL із низького рівня у високий зовнішній ведений чип зсуває свій вихідний регістр на один біт. Програма опитує стан лінії SDA після кожного такту: щойно датчик передасть останній біт або сформує стан NACK, він закриє вихідний транзистор, і лінія SDA підніметься до 3.3 В. Якщо це сталося раніше 9 тактів, цикл можна завершити достроково.
4. **Формування стану STOP вручну**: при високому рівні на лінії SCL лінія SDA спочатку примусово притискається до нуля (LOW), витримується пауза, після чого відпускається у високий рівень (HIGH). Цей перехід із 0 в 1 при високому рівні SCL є стандартизованою умовою STOP в протоколі I2C і переводить усі підключені датчики в режим очікування нової адреси.
5. **Верифікація та реініціалізація периферії**: перевіряється вхідний регістр GPIO. Якщо обидві лінії знаходяться на рівні логічної 1, виводи повертаються до режиму альтернативної функції (Alternate Function Open-Drain), скидання RCC знімається, і модуль I2C налаштовується заново. Якщо після 9 тактів лінія SDA залишається притиснутою до нуля — на платі присутнє фізичне коротке замикання або вийшов із ладу один із чипів.

## Крайові випадки та часові параметри

При реалізації відновлення шини слід враховувати три критичні нюанси:
- **Мінімальна тривалість напівперіоду такту:** час утримання низького та високого рівня на SCL під час ручного тактування повинен складати щонайменше 4.7 мкс для режиму Standard Mode (100 кГц) або 1.3 мкс для Fast Mode (400 кГц). Занадто короткі імпульси можуть бути відфільтровані вхідними фільтрами датчика як шум.
- **Підтягувальні резистори:** якщо на платі встановлено завеликі резистори підтяжки (наприклад, 10 кОм при ємності шини 200 пФ), фронт наростання сигналу SDA буде пологим. Програмі необхідно давати додатковий час на стабілізацію сигналу перед перевіркою рівня.
- **Декілька ведених пристроїв:** якщо на одній шині підключено декілька мікросхем, 9 тактів тактування безпечні для всіх: пристрої, які не брали участі в транзакції, просто проігнорують зміни на шині без попередньої адресації.

Нижче наведено практичні реалізації алгоритму для мікроконтролерів STM32.

:::tabs
```c
#include "stm32f10x.h"
#include <stdbool.h>
#include <stdint.h>

#define I2C_TIMEOUT_CYCLES  10000U

/* Проста затримка для формування фронтів I2C (близько 5 мкс при 72 МГц) */
static void delay_cycles(volatile uint32_t count) {
    while (count--) {
        __NOP();
    }
}

/**
 * @brief Повне апаратне та програмне відновлення шини I2C1
 * @return true, якщо шина успішно звільнена і модуль ініціалізовано
 */
bool i2c1_bus_recover_and_init(void) {
    /* 1. Примусове апаратне скидання периферії I2C1 через RCC */
    RCC->APB1RSTR |= RCC_APB1RSTR_I2C1RST;
    delay_cycles(100);
    RCC->APB1RSTR &= ~RCC_APB1RSTR_I2C1RST;

    /* 2. Увімкнення тактування портів GPIOB та I2C1 */
    RCC->APB2ENR |= RCC_APB2ENR_IOPBEN;
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;

    /* 3. Конфігурація PB6 (SCL) та PB7 (SDA) як GPIO Open-Drain 10 МГц */
    /* Очищення бітів MODE6, CNF6, MODE7, CNF7 (0xF << 24 | 0xF << 28) */
    GPIOB->CRL &= ~(0xFF000000U);
    /* 0x7 = Open-Drain вихід 10 МГц (CNF=01b, MODE=01b) */
    GPIOB->CRL |= (0x77000000U);

    /* Початковий стан: відпускаємо обидві лінії в HIGH */
    GPIOB->BSRR = GPIO_BSRR_BS6 | GPIO_BSRR_BS7;
    delay_cycles(200);

    /* 4. Генерація до 9 тактів SCL, якщо SDA затиснутий зовнішнім слейвом */
    for (uint8_t i = 0; i < 9; ++i) {
        /* Якщо лінія SDA вже відпущена в HIGH — ведений пристрій вільний */
        if (GPIOB->IDR & GPIO_IDR_IDR7) {
            break;
        }

        /* Імпульс на SCL: LOW -> пауза -> HIGH -> пауза */
        GPIOB->BSRR = GPIO_BSRR_BR6;
        delay_cycles(200);
        GPIOB->BSRR = GPIO_BSRR_BS6;
        delay_cycles(200);
    }

    /* 5. Генерація ручного стану STOP: SDA LOW, SCL HIGH -> SDA HIGH */
    GPIOB->BSRR = GPIO_BSRR_BR7; /* SDA = 0 */
    delay_cycles(200);
    GPIOB->BSRR = GPIO_BSRR_BS6; /* SCL = 1 */
    delay_cycles(200);
    GPIOB->BSRR = GPIO_BSRR_BS7; /* SDA = 1 (STOP condition) */
    delay_cycles(200);

    /* Перевірка, чи звільнилася шина (обидві лінії мають бути в 1) */
    if ((GPIOB->IDR & (GPIO_IDR_IDR6 | GPIO_IDR_IDR7)) != (GPIO_IDR_IDR6 | GPIO_IDR_IDR7)) {
        return false; /* Апаратне коротке замикання або несправний чип на платі */
    }

    /* 6. Переведення PB6/PB7 у режим Alternate Function Open-Drain (0xB = CNF=11b, MODE=01b) */
    GPIOB->CRL &= ~(0xFF000000U);
    GPIOB->CRL |= (0xBB000000U);

    /* 7. Ініціалізація регістрів I2C1 на частоту 100 кГц (APB1 = 36 МГц) */
    I2C1->CR1 = I2C_CR1_SWRST; /* Програмне скидання всередині блоку */
    delay_cycles(50);
    I2C1->CR1 = 0;

    I2C1->CR2 = 36;             /* Вхідна частота APB1 = 36 МГц */
    I2C1->CCR = 180;            /* 100 кГц: 36 МГц / (2 * 100 кГц) = 180 */
    I2C1->TRISE = 37;           /* Максимальний час наростання: 36 + 1 */
    I2C1->CR1 |= I2C_CR1_PE;    /* Увімкнення модуля */

    return true;
}
```
```cpp
#include <concepts>
#include <cstdint>
#include <span>

namespace embedded::hw {

/* Конфігураційні константи для шини I2C STM32F103 */
struct I2cBusConfig {
    static constexpr uint32_t Apb1ClockHz = 36'000'000U;
    static constexpr uint32_t BusSpeedHz  = 100'000U;
    static constexpr uint32_t DelayCount  = 200U;
};

enum class RecoveryResult : uint8_t {
    Success,
    BusLineStuckLow,
    HardwareFault
};

class I2c1BusRecovery {
public:
    explicit I2c1BusRecovery() = default;

    /* Заборона копіювання апаратного драйвера */
    I2c1BusRecovery(const I2c1BusRecovery&) = delete;
    I2c1BusRecovery& operator=(const I2c1BusRecovery&) = delete;

    [[nodiscard]] static RecoveryResult recover_and_initialize() noexcept {
        reset_peripheral_rcc();
        enable_clocks();
        configure_pins_as_gpio();

        release_lines_high();
        delay(I2cBusConfig::DelayCount);

        /* Вибивання дев'яти тактів для звільнення SDA веденим чипом */
        for (uint8_t cycle = 0; cycle < 9; ++cycle) {
            if (is_sda_high()) {
                break;
            }
            toggle_scl_pulse();
        }

        generate_stop_condition();

        /* Перевірка стану ліній: якщо хоча б одна в нулі — шина фізично пошкоджена */
        if (!is_scl_high() || !is_sda_high()) {
            return RecoveryResult::BusLineStuckLow;
        }

        configure_pins_as_alternate_function();
        initialize_i2c_registers();

        return RecoveryResult::Success;
    }

private:
    static void delay(volatile uint32_t count) noexcept {
        while (count--) {
            asm volatile("nop");
        }
    }

    static void reset_peripheral_rcc() noexcept {
        RCC->APB1RSTR |= RCC_APB1RSTR_I2C1RST;
        delay(100);
        RCC->APB1RSTR &= ~RCC_APB1RSTR_I2C1RST;
    }

    static void enable_clocks() noexcept {
        RCC->APB2ENR |= RCC_APB2ENR_IOPBEN;
        RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;
    }

    static void configure_pins_as_gpio() noexcept {
        GPIOB->CRL &= ~(0xFF000000U);
        GPIOB->CRL |= (0x77000000U); /* Open-Drain Output 10 MHz */
    }

    static void configure_pins_as_alternate_function() noexcept {
        GPIOB->CRL &= ~(0xFF000000U);
        GPIOB->CRL |= (0xBB000000U); /* Alternate Function Open-Drain */
    }

    static void release_lines_high() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BS6 | GPIO_BSRR_BS7;
    }

    static bool is_sda_high() noexcept {
        return (GPIOB->IDR & GPIO_IDR_IDR7) != 0;
    }

    static bool is_scl_high() noexcept {
        return (GPIOB->IDR & GPIO_IDR_IDR6) != 0;
    }

    static void toggle_scl_pulse() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BR6; /* SCL -> 0 */
        delay(I2cBusConfig::DelayCount);
        GPIOB->BSRR = GPIO_BSRR_BS6; /* SCL -> 1 */
        delay(I2cBusConfig::DelayCount);
    }

    static void generate_stop_condition() noexcept {
        GPIOB->BSRR = GPIO_BSRR_BR7; /* SDA -> 0 */
        delay(I2cBusConfig::DelayCount);
        GPIOB->BSRR = GPIO_BSRR_BS6; /* SCL -> 1 */
        delay(I2cBusConfig::DelayCount);
        GPIOB->BSRR = GPIO_BSRR_BS7; /* SDA -> 1 (STOP) */
        delay(I2cBusConfig::DelayCount);
    }

    static void initialize_i2c_registers() noexcept {
        I2C1->CR1 = I2C_CR1_SWRST;
        delay(50);
        I2C1->CR1 = 0;

        constexpr uint32_t freq_mhz = I2cBusConfig::Apb1ClockHz / 1'000'000U;
        constexpr uint32_t ccr_val  = I2cBusConfig::Apb1ClockHz / (2U * I2cBusConfig::BusSpeedHz);

        I2C1->CR2 = freq_mhz;
        I2C1->CCR = ccr_val;
        I2C1->TRISE = freq_mhz + 1U;
        I2C1->CR1 |= I2C_CR1_PE;
    }
};

} // namespace embedded::hw
```
:::
