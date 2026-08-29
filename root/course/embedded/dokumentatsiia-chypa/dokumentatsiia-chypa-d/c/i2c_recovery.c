#include "i2c_recovery.h"

#include "rcc.h"
#include "silicon_rev.h"
#include "stm32f4_regs.h"

/* Швидкість шини, на яку налаштовуємо блок і на якій вручну тактуємо SCL. */
#define I2C_BUS_HZ        100000UL
#define I2C_RECOVERY_PULSES 9U   /* стільки біт лишається в регістрі веденого */

static uint32_t s_cpu_hz;
static uint32_t s_apb1_hz;

/* ---------------------------------------------------------------------------
 * Затримки. Точності тут не потрібно — потрібна гарантія «не швидше за
 * 100 кГц», бо ведений на повільній лінії має встигнути відпустити SDA.
 * Тіло циклу — три інструкції на ітерацію (віднімання, порівняння, перехід);
 * volatile-лічильник не дає оптимізатору викинути цикл цілком.
 * ------------------------------------------------------------------------ */
static void delay_us(uint32_t us)
{
    const uint32_t cycles_per_us = (s_cpu_hz != 0UL) ? (s_cpu_hz / 1000000UL) : 16UL;
    volatile uint32_t iterations  = (us * cycles_per_us) / 3UL + 1UL;

    while (iterations != 0UL) {
        --iterations;
        NOP();
    }
}

/* --------------------------------------------------------------------------
 * Ніжки PB6 (SCL) і PB7 (SDA). Поля MODER, OTYPER, PUPDR і AFR — це та сама
 * матриця мультиплексування, яку Datasheet описує таблицею альтернативних
 * функцій, а Reference Manual — картою регістрів порту.
 * ------------------------------------------------------------------------ */
static void pin_set_mode(uint32_t pin, uint32_t mode)
{
    uint32_t reg = GPIOB->MODER;
    reg &= ~(3UL << (pin * 2U));
    reg |= (mode << (pin * 2U));
    GPIOB->MODER = reg;
}

static void pin_set_pull(uint32_t pin, uint32_t pull)
{
    uint32_t reg = GPIOB->PUPDR;
    reg &= ~(3UL << (pin * 2U));
    reg |= (pull << (pin * 2U));
    GPIOB->PUPDR = reg;
}

static void pin_set_open_drain(uint32_t pin)
{
    /* Шина I2C монтажна: жоден пристрій не має права видавати одиницю
     * транзистором, високий рівень створює зовнішній підтяжний резистор. */
    GPIOB->OTYPER |= (1UL << pin);
}

static void pin_set_af(uint32_t pin, uint32_t af)
{
    const uint32_t index = pin / 8U;         /* AFRL для 0..7, AFRH для 8..15 */
    const uint32_t shift = (pin % 8U) * 4U;

    uint32_t reg = GPIOB->AFR[index];
    reg &= ~(0xFUL << shift);
    reg |= (af << shift);
    GPIOB->AFR[index] = reg;
}

/* Запис одного біта без read-modify-write: BSRR має тип доступу W1S/W1C —
 * молодша половина слова встановлює ніжку, старша скидає. Одна інструкція
 * STR, жодного вікна, у якому переривання могло б зіпсувати сусідні ніжки. */
static void pin_write(uint32_t pin, bool high)
{
    GPIOB->BSRR = high ? (1UL << pin) : (1UL << (pin + 16U));
}

/* Читаємо саме IDR, а не ODR: нас цікавить реальний рівень на лінії, який
 * може тримати внизу ведений, а не те, що ми самі туди записали. */
static bool pin_read(uint32_t pin)
{
    return (GPIOB->IDR & (1UL << pin)) != 0UL;
}

/* ---------------------------------------------------------------------------
 * Конфігурація самого блоку. Крок 3 методики: усе пишеться при PE = 0.
 * ------------------------------------------------------------------------ */
static i2c_status_t configure_peripheral(void)
{
    const uint32_t freq_mhz = s_apb1_hz / 1000000UL;

    /* RM0090 §27.6.2: поле FREQ мусить дорівнювати частоті APB1 у мегагерцах
     * і лежати в межах 2..50 (для стандартного режиму — не менше 2). */
    if (freq_mhz < 2UL || freq_mhz > 50UL) {
        return I2C_ERR_BAD_CLOCK;
    }

    I2C1->CR1 &= ~I2C_CR1_PE;       /* блок вимкнено — конфігурувати можна */

    I2C1->CR2 = freq_mhz & I2C_CR2_FREQ_MSK;

    /* Стандартний режим: половина періоду набирається CCR тактами APB1. */
    uint32_t ccr = s_apb1_hz / (2UL * I2C_BUS_HZ);
    if (ccr < 4UL) {
        ccr = 4UL;                  /* мінімум, дозволений довідником */
    }
    I2C1->CCR = ccr;

    /* TRISE — максимальний час наростання фронту в тактах APB1 плюс один. */
    I2C1->TRISE = freq_mhz + 1UL;

    /* Аналоговий фільтр — саме той вузол, чий дефект описує еррата.
     * Вимикати його дозволено лише при PE = 0, і робимо це тільки на
     * уражених ревізіях: на виправленому кремнії фільтр корисний, він
     * давить короткі викиди на лінії. */
    if (silicon_affected_by(ERRATUM_I2C_BUSY_LOCK)) {
        I2C1->FLTR |= I2C_FLTR_ANOFF;
    } else {
        I2C1->FLTR &= ~I2C_FLTR_ANOFF;
    }

    I2C1->CR1 |= I2C_CR1_PE;        /* крок 4: активація */

    return I2C_OK;
}

i2c_status_t i2c_init(uint32_t apb1_clock_hz, uint32_t cpu_clock_hz)
{
    s_apb1_hz = apb1_clock_hz;
    s_cpu_hz  = cpu_clock_hz;

    /* Крок 1: тактування порту й самого блоку. */
    rcc_ahb1_enable(RCC_AHB1ENR_GPIOBEN);
    rcc_apb1_enable(RCC_APB1ENR_I2C1EN);

    /* Крок 2: матриця виводів. Спершу тип каскаду й підтяжка, аж потім
     * перемикання в режим альтернативної функції — інакше на частку
     * мікросекунди ніжка виїде на лінію в режимі push-pull. */
    pin_set_open_drain(I2C1_SCL_PIN);
    pin_set_open_drain(I2C1_SDA_PIN);
    pin_set_pull(I2C1_SCL_PIN, GPIO_PULL_UP);
    pin_set_pull(I2C1_SDA_PIN, GPIO_PULL_UP);
    pin_set_af(I2C1_SCL_PIN, I2C1_AF);
    pin_set_af(I2C1_SDA_PIN, I2C1_AF);
    pin_set_mode(I2C1_SCL_PIN, GPIO_MODE_AF);
    pin_set_mode(I2C1_SDA_PIN, GPIO_MODE_AF);

    return configure_peripheral();
}

bool i2c_bus_busy(void)
{
    return (I2C1->SR2 & I2C_SR2_BUSY) != 0UL;
}

/* ---------------------------------------------------------------------------
 * Обхід еррати цілком.
 * ------------------------------------------------------------------------ */
i2c_status_t i2c_recover_bus(void)
{
    const uint32_t half_period_us = (1000000UL / I2C_BUS_HZ) / 2UL; /* 5 мкс */

    /* 1. Відібрати лінії в завислого кінцевого автомата. Доки PE = 1, блок
     *    продовжує керувати ніжками через матрицю альтернативних функцій. */
    I2C1->CR1 &= ~I2C_CR1_PE;

    /* 2. Взяти обидві ніжки в ручне керування, відпустивши їх у високий
     *    рівень: open-drain плюс запис одиниці = ніжка нічого не тримає. */
    pin_write(I2C1_SCL_PIN, true);
    pin_write(I2C1_SDA_PIN, true);
    pin_set_mode(I2C1_SCL_PIN, GPIO_MODE_OUTPUT);
    pin_set_mode(I2C1_SDA_PIN, GPIO_MODE_OUTPUT);
    delay_us(half_period_us);

    /* 3. Якщо SCL лежить унизу, коли її ніхто не тримає, — це вже не еррата,
     *    а замикання чи мертвий ведений. Програмного обходу не існує. */
    if (!pin_read(I2C1_SCL_PIN)) {
        /* Ніжки повертаємо блоку, але PE лишається нулем: користуватися
         * шиною однаково не можна, і краще хай вона мовчить. */
        pin_set_mode(I2C1_SCL_PIN, GPIO_MODE_AF);
        pin_set_mode(I2C1_SDA_PIN, GPIO_MODE_AF);
        return I2C_ERR_SCL_STUCK_LOW;
    }

    /* 4. Дев'ять тактів на SCL. Ведений, який завис посеред байта, дорахує
     *    свій зсувний регістр до кінця й відпустить SDA. Кожен такт
     *    перевіряємо лінію — вийти раніше дешевше, ніж дотактувати всі. */
    for (unsigned pulse = 0U; pulse < I2C_RECOVERY_PULSES; ++pulse) {
        if (pin_read(I2C1_SDA_PIN)) {
            break;
        }
        pin_write(I2C1_SCL_PIN, false);
        delay_us(half_period_us);
        pin_write(I2C1_SCL_PIN, true);
        delay_us(half_period_us);
    }

    /* 5. Ведений відпустив лінію посеред кадру, тож шина зараз у невизначеному
     *    стані. Ставимо крапку вручну: STOP — це наростання SDA при високій
     *    SCL. Спершу притискаємо SDA, потім відпускаємо. */
    pin_write(I2C1_SDA_PIN, false);
    delay_us(half_period_us);
    pin_write(I2C1_SCL_PIN, true);
    delay_us(half_period_us);
    pin_write(I2C1_SDA_PIN, true);
    delay_us(half_period_us);

    const bool sda_free = pin_read(I2C1_SDA_PIN);

    /* 6. Повернути ніжки блоку незалежно від результату: лишити периферію
     *    без виводів було б гірше за будь-яку помилку. */
    pin_set_mode(I2C1_SCL_PIN, GPIO_MODE_AF);
    pin_set_mode(I2C1_SDA_PIN, GPIO_MODE_AF);

    if (!sda_free) {
        return I2C_ERR_SDA_STUCK_LOW;
    }

    /* 7. Кінцевий автомат блоку так і стоїть у зависі: тактування ліній його
     *    не зрушило. Єдиний спосіб — програмне скидання бітом SWRST, який
     *    тримає блок під скиданням, доки його не знято вручну. */
    I2C1->CR1 |= I2C_CR1_SWRST;
    delay_us(half_period_us);
    I2C1->CR1 &= ~I2C_CR1_SWRST;
    delay_us(half_period_us);

    /* 8. Скидання стерло всю конфігурацію — набираємо її наново. */
    const i2c_status_t status = configure_peripheral();
    if (status != I2C_OK) {
        return status;
    }

    /* 9. Перевірка, а не віра: якщо BUSY досі піднятий, обхід не спрацював
     *    і викликати передачу не можна. */
    return i2c_bus_busy() ? I2C_ERR_STILL_BUSY : I2C_OK;
}
