/* platform_stm32f4.c — порт під STM32F407. Єдиний файл, що знає регістри.
 *
 * Розводка стенда:
 *   PA0  — дільник 10 кОм + NTC 10 кОм (аналоговий вхід)
 *   PA1  — дільник 100к/100к від акумулятора
 *   PB0  — затвор ключа передавача
 *   PB1  — плівковий підігрів плати
 *   PB2  — дозвіл заряду (вхід EN контролера заряду)
 *   PB6  — I2C1_SCL, PB7 — I2C1_SDA (зовнішні підтяжки 4.7 кОм)
 *
 * Жодне очікування апаратної події тут не робиться вічним циклом: у полі
 * зависла шина або мертвий АЦП — це буденність, і кожен такий цикл
 * перетворився б на скидання від сторожового таймера замість помилки.
 */

#include "platform.h"

#include "stm32f4xx.h"

#define LOAD_PORT GPIOB
#define I2C_PORT GPIOB
#define SCL_PIN 6u
#define SDA_PIN 7u

/* Скільки обертів порожнього циклу терпимо, чекаючи прапорця периферії.
 * Число з запасом: при 168 МГц це ≈ 1 мс, довша за будь-яку штатну подію. */
#define SPIN_LIMIT 40000u

static const uint8_t LOAD_PIN[PLAT_LOAD_COUNT] = {0u, 1u, 2u};

static volatile uint32_t s_ticks;
static uint32_t s_core_hz = PLAT_HCLK_BASE_HZ;
static uint32_t s_reset_flags;
static bool s_load_state[PLAT_LOAD_COUNT];

void SysTick_Handler(void)
{
    s_ticks++;
}

/* --- дрібні помічники ---------------------------------------------------- */

static void gpio_mode(GPIO_TypeDef *port, uint8_t pin, uint32_t mode)
{
    port->MODER = (port->MODER & ~(3u << (pin * 2u))) | (mode << (pin * 2u));
}

static void gpio_af(GPIO_TypeDef *port, uint8_t pin, uint32_t af)
{
    const uint8_t idx = pin >> 3u;
    const uint8_t shift = (pin & 7u) * 4u;
    port->AFR[idx] = (port->AFR[idx] & ~(0xFu << shift)) | (af << shift);
}

/* --- ініціалізація ------------------------------------------------------- */

static void backup_domain_init(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_PWREN;
    PWR->CR |= PWR_CR_DBP; /* без цього BKPxR лишаються тільки для читання */

    RCC->CSR |= RCC_CSR_LSION;
    for (uint32_t spin = 0u; spin < SPIN_LIMIT; spin++) {
        if ((RCC->CSR & RCC_CSR_LSIRDY) != 0u) {
            break;
        }
    }

    /* RTCSEL можна записати лише раз на життя батарейки резервного домену:
     * повторний вибір джерела вимагав би скидання домену, а разом із ним
     * стерлася б уся історія аварій — саме те, заради чого домен і взято. */
    if ((RCC->BDCR & RCC_BDCR_RTCEN) == 0u) {
        RCC->BDCR |= RCC_BDCR_RTCSEL_1; /* 0b10 — LSI */
        RCC->BDCR |= RCC_BDCR_RTCEN;
    }
}

static void adc_init(void)
{
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;

    ADC->CCR = (ADC->CCR & ~ADC_CCR_ADCPRE) | ADC_CCR_ADCPRE_0; /* APB2/4 */

    /* 480 тактів на вибірку. Дільник із NTC на 10 кОм має високий вихідний
     * опір; коротка вибірка не встигає зарядити конденсатор пристрою
     * вибірки-зберігання, і замір «пливе» разом із сусіднім каналом. */
    ADC1->SMPR2 |= (7u << (PLAT_ADC_CH_NTC * 3u)) | (7u << (PLAT_ADC_CH_VBAT * 3u));
    ADC1->SQR1 = 0u; /* одна перетворка в послідовності */
    ADC1->CR2 |= ADC_CR2_ADON;
}

void plat_init(void)
{
    /* Прапори скидання знімаємо ОДИН раз і зберігаємо: RMVF стирає їх
     * назавжди, і другий охочий дізнатися причину старту вже нічого не
     * побачить. */
    s_reset_flags = RCC->CSR;
    RCC->CSR |= RCC_CSR_RMVF;

    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN | RCC_AHB1ENR_GPIOBEN;

    gpio_mode(GPIOA, 0u, 3u); /* аналоговий режим */
    gpio_mode(GPIOA, 1u, 3u);

    for (uint8_t i = 0u; i < (uint8_t)PLAT_LOAD_COUNT; i++) {
        LOAD_PORT->BSRR = (uint32_t)1u << (LOAD_PIN[i] + 16u); /* спершу нуль */
        gpio_mode(LOAD_PORT, LOAD_PIN[i], 1u);                 /* потім вихід */
        s_load_state[i] = false;
    }

    backup_domain_init();
    adc_init();

    SystemCoreClock = s_core_hz;
    (void)SysTick_Config(s_core_hz / 1000u);
}

uint32_t plat_reset_flags_raw(void)
{
    return s_reset_flags;
}

/* --- час ----------------------------------------------------------------- */

uint32_t plat_millis(void)
{
    return s_ticks;
}

void plat_delay_us(uint32_t us)
{
    /* Тіло циклу — чотири такти ядра (віднімання, порівняння, перехід
     * і читання volatile). Точність тут не потрібна: найкоротша затримка
     * у проєкті — півперіод ручного тактування шини, 5 мкс. */
    volatile uint32_t loops = (s_core_hz / 4000000u) * us;
    while (loops != 0u) {
        loops--;
    }
}

/* --- тактування ---------------------------------------------------------- */

void plat_set_core_divider(uint8_t div_log2)
{
    static const uint32_t HPRE[5] = {0u, 8u, 9u, 10u, 11u}; /* /1 /2 /4 /8 /16 */

    if (div_log2 > 4u) {
        div_log2 = 4u;
    }

    RCC->CFGR = (RCC->CFGR & ~RCC_CFGR_HPRE) | (HPRE[div_log2] << RCC_CFGR_HPRE_Pos);
    s_core_hz = PLAT_HCLK_BASE_HZ >> div_log2;
    SystemCoreClock = s_core_hz;

    /* SysTick рахує від HCLK, тож після зміни дільника мілісекунда стала б
     * удвічі-вчетверо довшою, а разом з нею — усі періоди в головному циклі. */
    (void)SysTick_Config(s_core_hz / 1000u);
}

uint32_t plat_core_hz(void)
{
    return s_core_hz;
}

/* --- навантаження -------------------------------------------------------- */

void plat_load_set(plat_load_t load, bool on)
{
    if ((unsigned)load >= (unsigned)PLAT_LOAD_COUNT) {
        return;
    }
    const uint8_t pin = LOAD_PIN[load];
    LOAD_PORT->BSRR = on ? ((uint32_t)1u << pin) : ((uint32_t)1u << (pin + 16u));
    s_load_state[load] = on;
}

bool plat_load_get(plat_load_t load)
{
    return ((unsigned)load < (unsigned)PLAT_LOAD_COUNT) ? s_load_state[load] : false;
}

/* --- вимірювання --------------------------------------------------------- */

bool plat_adc_read(uint8_t channel, uint16_t *counts)
{
    if (counts == 0) {
        return false;
    }

    ADC1->SR &= ~ADC_SR_EOC;
    ADC1->SQR3 = channel;
    ADC1->CR2 |= ADC_CR2_SWSTART;

    for (uint32_t spin = 0u; spin < SPIN_LIMIT; spin++) {
        if ((ADC1->SR & ADC_SR_EOC) != 0u) {
            *counts = (uint16_t)ADC1->DR;
            return true;
        }
    }
    return false;
}

/* --- резервна пам'ять ---------------------------------------------------- */

/* BKP0R..BKP19R лежать у пам'яті підряд, тож індексуються як масив. */
static volatile uint32_t *bkp_word(uint8_t index)
{
    return &(&RTC->BKP0R)[index];
}

bool plat_bkp_read(uint8_t index, uint32_t *value)
{
    if (index >= PLAT_BKP_WORDS || value == 0) {
        return false;
    }
    *value = *bkp_word(index);
    return true;
}

bool plat_bkp_write(uint8_t index, uint32_t value)
{
    if (index >= PLAT_BKP_WORDS) {
        return false;
    }
    *bkp_word(index) = value;
    return true;
}

/* --- шина I2C ------------------------------------------------------------ */

static plat_i2c_status_t i2c_wait(volatile uint32_t *reg, uint32_t mask)
{
    for (uint32_t spin = 0u; spin < SPIN_LIMIT; spin++) {
        if ((*reg & mask) != 0u) {
            return PLAT_I2C_OK;
        }
        if ((I2C1->SR1 & I2C_SR1_AF) != 0u) {
            I2C1->SR1 &= ~I2C_SR1_AF;
            I2C1->CR1 |= I2C_CR1_STOP;
            return PLAT_I2C_NACK; /* раба немає, але лінії живі */
        }
    }
    return PLAT_I2C_TIMEOUT;
}

void plat_i2c_init(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;

    /* Повне скидання блока. Після порятунку шини периферія лишається
     * у стані посеред транзакції, і без SWRST перший же START зависає. */
    I2C1->CR1 = I2C_CR1_SWRST;
    I2C1->CR1 = 0u;

    gpio_mode(I2C_PORT, SCL_PIN, 2u); /* альтернативна функція */
    gpio_mode(I2C_PORT, SDA_PIN, 2u);
    gpio_af(I2C_PORT, SCL_PIN, 4u); /* AF4 — I2C1 */
    gpio_af(I2C_PORT, SDA_PIN, 4u);
    I2C_PORT->OTYPER |= (1u << SCL_PIN) | (1u << SDA_PIN); /* відкритий стік */

    I2C1->CR2 = 42u;   /* APB1 = 42 МГц */
    I2C1->CCR = 210u;  /* 42 МГц / (2 · 100 кГц) — стандартний режим */
    I2C1->TRISE = 43u; /* 1 мкс фронту при 42 МГц */
    I2C1->CR1 |= I2C_CR1_PE;
}

static plat_i2c_status_t i2c_start(uint8_t addr7, bool read)
{
    if ((I2C1->SR2 & I2C_SR2_BUSY) != 0u) {
        return PLAT_I2C_BUSY; /* лінію хтось тримає ще до нашого старту */
    }

    I2C1->CR1 |= I2C_CR1_START;
    plat_i2c_status_t st = i2c_wait(&I2C1->SR1, I2C_SR1_SB);
    if (st != PLAT_I2C_OK) {
        return st;
    }

    I2C1->DR = (uint8_t)((addr7 << 1u) | (read ? 1u : 0u));
    st = i2c_wait(&I2C1->SR1, I2C_SR1_ADDR);
    if (st != PLAT_I2C_OK) {
        return st;
    }

    (void)I2C1->SR1; /* читання SR1+SR2 знімає ADDR */
    (void)I2C1->SR2;
    return PLAT_I2C_OK;
}

plat_i2c_status_t plat_i2c_probe(uint8_t addr7)
{
    const plat_i2c_status_t st = i2c_start(addr7, false);
    I2C1->CR1 |= I2C_CR1_STOP;
    return st;
}

plat_i2c_status_t plat_i2c_read_reg(uint8_t addr7, uint8_t reg, uint8_t *buf, uint8_t len)
{
    if (buf == 0 || len == 0u) {
        return PLAT_I2C_NACK;
    }

    plat_i2c_status_t st = i2c_start(addr7, false);
    if (st != PLAT_I2C_OK) {
        return st;
    }

    I2C1->DR = reg;
    st = i2c_wait(&I2C1->SR1, I2C_SR1_BTF);
    if (st != PLAT_I2C_OK) {
        return st;
    }

    I2C1->CR1 |= I2C_CR1_ACK;
    st = i2c_start(addr7, true); /* повторний START, тепер на читання */
    if (st != PLAT_I2C_OK) {
        I2C1->CR1 |= I2C_CR1_STOP;
        return st;
    }

    for (uint8_t i = 0u; i < len; i++) {
        if (i + 1u == len) {
            /* Останній байт квитуємо запереченням і одразу ставимо STOP:
             * інакше раб почне віддавати наступний і затримає SDA внизу. */
            I2C1->CR1 &= ~I2C_CR1_ACK;
            I2C1->CR1 |= I2C_CR1_STOP;
        }
        st = i2c_wait(&I2C1->SR1, I2C_SR1_RXNE);
        if (st != PLAT_I2C_OK) {
            I2C1->CR1 |= I2C_CR1_STOP;
            return st;
        }
        buf[i] = (uint8_t)I2C1->DR;
    }
    return PLAT_I2C_OK;
}

void plat_i2c_pins_take(void)
{
    I2C1->CR1 &= ~I2C_CR1_PE; /* периферія відпускає ніжки */
    gpio_mode(I2C_PORT, SCL_PIN, 1u);
    gpio_mode(I2C_PORT, SDA_PIN, 1u);
    I2C_PORT->OTYPER |= (1u << SCL_PIN) | (1u << SDA_PIN);
    I2C_PORT->BSRR = (1u << SCL_PIN) | (1u << SDA_PIN); /* обидві відпущені */
}

void plat_i2c_pins_release(void)
{
    plat_i2c_init(); /* SWRST плюс повернення ніжок під AF4 */
}

void plat_i2c_scl_write(bool high)
{
    I2C_PORT->BSRR = high ? (1u << SCL_PIN) : (1u << (SCL_PIN + 16u));
}

void plat_i2c_sda_write(bool high)
{
    I2C_PORT->BSRR = high ? (1u << SDA_PIN) : (1u << (SDA_PIN + 16u));
}

bool plat_i2c_scl_read(void)
{
    return (I2C_PORT->IDR & (1u << SCL_PIN)) != 0u;
}

bool plat_i2c_sda_read(void)
{
    return (I2C_PORT->IDR & (1u << SDA_PIN)) != 0u;
}

/* --- сторожовий таймер і скидання ---------------------------------------- */

void plat_watchdog_start(uint32_t timeout_ms)
{
    /* IWDG живиться від власного LSI ≈32 кГц і не спиняється разом
     * із зірваним основним тактуванням — саме тому він, а не таймер ядра. */
    IWDG->KR = 0x5555u;              /* дозвіл запису PR/RLR */
    IWDG->PR = 3u;                   /* /32 → приблизно 1 кГц */
    IWDG->RLR = (timeout_ms > 4095u) ? 4095u : timeout_ms;
    IWDG->KR = 0xAAAAu;              /* перезавантажити лічильник */
    IWDG->KR = 0xCCCCu;              /* пуск; зупинити вже не можна */
}

void plat_watchdog_kick(void)
{
    IWDG->KR = 0xAAAAu;
}

void plat_system_reset(void)
{
    NVIC_SystemReset();
}
