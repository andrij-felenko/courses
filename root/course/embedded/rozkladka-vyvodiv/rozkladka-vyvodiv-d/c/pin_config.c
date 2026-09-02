#include "pin_config.h"

#define PORT_COUNT      8U        /* GPIOA..GPIOH у корпусах LQFP64/LQFP100 */
#define PORT_STRIDE     0x400U    /* блоки портів ідуть через 1 КБ          */
#define GPIO_LCKR_LCKK  (1U << 16)

/*
 * Виданий струм живе між викликами: друга таблиця мусить бачити,
 * скільки міліампер уже роздала перша, інакше бюджет порту фіктивний.
 */
static uint16_t g_port_ma[PORT_COUNT];
static uint16_t g_chip_ma;

static int port_index(const GPIO_TypeDef* port)
{
    if (port == NULL) {
        return -1;
    }

    const uintptr_t base  = (uintptr_t)port;
    const uintptr_t first = (uintptr_t)GPIOA_BASE;
    if (base < first) {
        return -1;
    }

    const uintptr_t offset = base - first;
    if ((offset % PORT_STRIDE) != 0U) {
        return -1;
    }

    const uintptr_t index = offset / PORT_STRIDE;
    return (index < PORT_COUNT) ? (int)index : -1;
}

static bool fail(pin_error_t* err, pin_status_t code, const char* signal,
                 const char* rival, uint32_t value, uint32_t limit)
{
    if (err != NULL) {
        err->code   = code;
        err->signal = signal;
        err->rival  = rival;
        err->value  = value;
        err->limit  = limit;
    }
    return false;
}

/* Системні та резервні ніжки впізнаємо ЗА АДРЕСОЮ, а не за словом у таблиці:
   саме помилковий запис у таблиці ми й ловимо. */
static bool is_swd_pin(const pin_desc_t* d)
{
    return d->port == GPIOA && (d->pin == 13U || d->pin == 14U);
}

static bool is_backup_pin(const pin_desc_t* d)
{
    return d->port == GPIOC && d->pin >= 13U && d->pin <= 15U;
}

static bool check_one(const pin_desc_t* d, pin_error_t* err)
{
    if (port_index(d->port) < 0) {
        return fail(err, PIN_ERR_UNKNOWN_PORT, d->signal, NULL, 0U, 0U);
    }
    if (d->pin > 15U) {
        return fail(err, PIN_ERR_PIN_RANGE, d->signal, NULL, d->pin, 15U);
    }

    /* 1. Шина налагодження. Дозволено лише те, чим вона є: AF0. */
    if (is_swd_pin(d)) {
        if (d->klass != PIN_CLASS_SYSTEM) {
            return fail(err, PIN_ERR_CLASS_MISMATCH, d->signal, "PA13/PA14 = SWD",
                        (uint32_t)d->klass, (uint32_t)PIN_CLASS_SYSTEM);
        }
        if (d->mode != PIN_MODE_ALT || d->af != 0U) {
            return fail(err, PIN_ERR_DEBUG_PIN, d->signal, "SWDIO/SWCLK",
                        (uint32_t)d->mode, (uint32_t)PIN_MODE_ALT);
        }
    } else if (d->klass == PIN_CLASS_SYSTEM) {
        return fail(err, PIN_ERR_CLASS_MISMATCH, d->signal, NULL,
                    (uint32_t)PIN_CLASS_SYSTEM, 0U);
    }

    /* 2. Домен резервного живлення: слабкі ключі й повільні фронти. */
    if (is_backup_pin(d)) {
        if (d->klass != PIN_CLASS_BACKUP) {
            return fail(err, PIN_ERR_CLASS_MISMATCH, d->signal, "PC13..PC15 = Backup",
                        (uint32_t)d->klass, (uint32_t)PIN_CLASS_BACKUP);
        }
        if (d->mode == PIN_MODE_ALT) {
            return fail(err, PIN_ERR_BACKUP_ALT, d->signal, NULL, d->af, 0U);
        }
        if (d->speed != PIN_SPEED_LOW) {
            return fail(err, PIN_ERR_BACKUP_SPEED, d->signal, NULL,
                        (uint32_t)d->speed, (uint32_t)PIN_SPEED_LOW);
        }
        if (d->load_ma > PIN_BACKUP_MAX_MA) {
            return fail(err, PIN_ERR_BACKUP_CURRENT, d->signal, NULL,
                        d->load_ma, PIN_BACKUP_MAX_MA);
        }
    } else if (d->klass == PIN_CLASS_BACKUP) {
        return fail(err, PIN_ERR_CLASS_MISMATCH, d->signal, NULL,
                    (uint32_t)PIN_CLASS_BACKUP, 0U);
    }

    /* 3. Аналоговий тракт існує лише там, де кремній завів його на АЦП. */
    if (d->mode == PIN_MODE_ANALOG && d->klass != PIN_CLASS_TTA) {
        return fail(err, PIN_ERR_ANALOG_ON_DIGITAL, d->signal, NULL,
                    (uint32_t)d->klass, (uint32_t)PIN_CLASS_TTA);
    }

    /* 4. Номер альтернативної функції. */
    if (d->mode == PIN_MODE_ALT) {
        if (d->af > 15U) {
            return fail(err, PIN_ERR_AF_RANGE, d->signal, NULL, d->af, 15U);
        }
    } else if (d->af != 0U) {
        /* AF у режимі виходу нічого не робить, зате приховує помилку копіювання. */
        return fail(err, PIN_ERR_AF_UNUSED, d->signal, NULL, d->af, 0U);
    }

    /* 5. Крутизна фронту. Звичайний вихід не має права на Very High,
          а все, що реально тягне струм (LED, реле, оптопара), — на Low. */
    if (d->mode == PIN_MODE_OUTPUT && d->speed == PIN_SPEED_VERY_HIGH) {
        return fail(err, PIN_ERR_SLEW_TOO_FAST, d->signal, NULL,
                    (uint32_t)d->speed, (uint32_t)PIN_SPEED_HIGH);
    }
    if (d->load_ma > 0U && d->speed != PIN_SPEED_LOW) {
        return fail(err, PIN_ERR_SLEW_TOO_FAST, d->signal, NULL,
                    (uint32_t)d->speed, (uint32_t)PIN_SPEED_LOW);
    }

    /* 6. Струм окремої ніжки (домен RTC уже перевірено суворішою межею). */
    if (!is_backup_pin(d) && d->load_ma > PIN_MAX_CURRENT_MA) {
        return fail(err, PIN_ERR_PIN_CURRENT, d->signal, NULL,
                    d->load_ma, PIN_MAX_CURRENT_MA);
    }

    return true;
}

static const char* first_signal_on_port(const pin_desc_t* layout, size_t count, int index)
{
    for (size_t i = 0U; i < count; ++i) {
        if (port_index(layout[i].port) == index) {
            return layout[i].signal;
        }
    }
    return NULL;
}

static bool check_layout(const pin_desc_t* layout, size_t count, pin_error_t* err,
                         uint16_t* port_add, uint32_t* chip_add)
{
    for (size_t i = 0U; i < PORT_COUNT; ++i) {
        port_add[i] = 0U;
    }
    *chip_add = 0U;

    for (size_t i = 0U; i < count; ++i) {
        const pin_desc_t* d = &layout[i];

        if (!check_one(d, err)) {
            return false;
        }

        /* Головний конфлікт теми: дві функції на одній фізичній ніжці.
           Мультиплексор пропустить лише останній запис — тихо. */
        for (size_t j = 0U; j < i; ++j) {
            if (layout[j].port == d->port && layout[j].pin == d->pin) {
                return fail(err, PIN_ERR_DUPLICATE, d->signal, layout[j].signal,
                            d->pin, 0U);
            }
        }

        port_add[port_index(d->port)] += d->load_ma;
        *chip_add += d->load_ma;
    }

    for (size_t i = 0U; i < PORT_COUNT; ++i) {
        const uint32_t total = (uint32_t)g_port_ma[i] + port_add[i];
        if (total > PORT_MAX_CURRENT_MA) {
            return fail(err, PIN_ERR_PORT_CURRENT,
                        first_signal_on_port(layout, count, (int)i), NULL,
                        total, PORT_MAX_CURRENT_MA);
        }
    }

    const uint32_t chip_total = (uint32_t)g_chip_ma + *chip_add;
    if (chip_total > CHIP_MAX_CURRENT_MA) {
        return fail(err, PIN_ERR_CHIP_CURRENT, layout[0].signal, NULL,
                    chip_total, CHIP_MAX_CURRENT_MA);
    }

    return true;
}

static void enable_port_clock(int index)
{
    RCC->AHB1ENR |= (1U << (uint32_t)index);
    /* Читання назад: шина AHB застосовує запис із затримкою в такт. */
    (void)RCC->AHB1ENR;
}

static void write_pin(const pin_desc_t* d)
{
    GPIO_TypeDef*  g   = d->port;
    const uint32_t two = (uint32_t)d->pin * 2U;
    const uint32_t one = (uint32_t)d->pin;

    /* Порядок навмисний: усе, крім MODER, ставимо ДО перемикання режиму.
       Інакше ніжка на кілька тактів віддається блоку зі старим AF. */
    if (d->mode == PIN_MODE_ALT) {
        const uint32_t idx   = one >> 3U;             /* AFRL або AFRH   */
        const uint32_t shift = (one & 7U) * 4U;       /* 4 біти на ніжку */
        g->AFR[idx] = (g->AFR[idx] & ~(0xFU << shift)) | ((uint32_t)d->af << shift);
    }

    if (d->otype == PIN_OPEN_DRAIN) {
        g->OTYPER |= (1U << one);
    } else {
        g->OTYPER &= ~(1U << one);
    }

    g->OSPEEDR = (g->OSPEEDR & ~(0x3U << two)) | ((uint32_t)d->speed << two);
    g->PUPDR   = (g->PUPDR   & ~(0x3U << two)) | ((uint32_t)d->pull  << two);
    g->MODER   = (g->MODER   & ~(0x3U << two)) | ((uint32_t)d->mode  << two);
}

bool pin_apply_layout(const pin_desc_t* layout, size_t count, pin_error_t* err)
{
    (void)fail(err, PIN_OK, NULL, NULL, 0U, 0U);

    if (layout == NULL || count == 0U) {
        return true;
    }

    uint16_t port_add[PORT_COUNT];
    uint32_t chip_add = 0U;

    if (!check_layout(layout, count, err, port_add, &chip_add)) {
        return false;
    }

    /* Жодного запису в регістр вище цього рядка. */
    for (size_t i = 0U; i < count; ++i) {
        enable_port_clock(port_index(layout[i].port));
    }
    for (size_t i = 0U; i < count; ++i) {
        write_pin(&layout[i]);
    }

    for (size_t i = 0U; i < PORT_COUNT; ++i) {
        g_port_ma[i] = (uint16_t)(g_port_ma[i] + port_add[i]);
    }
    g_chip_ma = (uint16_t)(g_chip_ma + chip_add);

    return true;
}

/* Після скидання PA15 і PB4 підтягнуті вгору, PB3 — вниз: це залишки JTAG.
   Віддаємо ніжки під звичайний GPIO — вхід без підтяжки, AF0 очищено. */
static void release_to_gpio(GPIO_TypeDef* port, uint8_t pin)
{
    const uint32_t two   = (uint32_t)pin * 2U;
    const uint32_t idx   = (uint32_t)pin >> 3U;
    const uint32_t shift = ((uint32_t)pin & 7U) * 4U;

    port->MODER    &= ~(0x3U << two);   /* 0b00 = вхід */
    port->PUPDR    &= ~(0x3U << two);
    port->OSPEEDR  &= ~(0x3U << two);
    port->AFR[idx] &= ~(0xFU << shift);
}

bool pin_secure_debug_port(pin_error_t* err)
{
    (void)fail(err, PIN_OK, NULL, NULL, 0U, 0U);

    RCC->AHB1ENR |= (1U << 0) | (1U << 1);   /* GPIOA, GPIOB */
    (void)RCC->AHB1ENR;

    release_to_gpio(GPIOA, 15U);  /* JTDI      */
    release_to_gpio(GPIOB, 3U);   /* JTDO/SWO — трасування втрачаємо свідомо */
    release_to_gpio(GPIOB, 4U);   /* NJTRST    */

    const uint32_t swd = (1U << 13) | (1U << 14);

    if ((GPIOA->LCKR & GPIO_LCKR_LCKK) != 0U) {
        return true;   /* замок уже стоїть і тримається до скидання */
    }

    /*
     * Послідовність LCKR з довідника: запис 1+біти, 0+біти, 1+біти,
     * потім читання. Її не можна переривати — переривання посеред
     * послідовності лишить ніжки незамкненими.
     */
    const uint32_t primask = __get_PRIMASK();
    __disable_irq();

    GPIOA->LCKR = GPIO_LCKR_LCKK | swd;
    GPIOA->LCKR = swd;
    GPIOA->LCKR = GPIO_LCKR_LCKK | swd;
    (void)GPIOA->LCKR;
    const uint32_t confirm = GPIOA->LCKR;

    __set_PRIMASK(primask);

    if ((confirm & GPIO_LCKR_LCKK) == 0U) {
        return fail(err, PIN_ERR_LOCK_FAILED, "SWDIO/SWCLK", NULL, confirm, GPIO_LCKR_LCKK);
    }

    /* Тепер MODER/AFR цих двох ніжок апаратно нерухомі: навіть чужа
       бібліотечна GPIO_Init() уже не відріже програматор. */
    return true;
}

const char* pin_status_text(pin_status_t code)
{
    switch (code) {
    case PIN_OK:                    return "гаразд";
    case PIN_ERR_UNKNOWN_PORT:      return "невідомий порт GPIO";
    case PIN_ERR_PIN_RANGE:         return "номер ніжки поза 0..15";
    case PIN_ERR_DEBUG_PIN:         return "спроба забрати ніжку SWD";
    case PIN_ERR_CLASS_MISMATCH:    return "клас не збігається з таблицею виводів";
    case PIN_ERR_ANALOG_ON_DIGITAL: return "аналоговий режим на цифровій ніжці";
    case PIN_ERR_AF_RANGE:          return "номер альтернативної функції > 15";
    case PIN_ERR_AF_UNUSED:         return "AF заданий поза режимом ALT";
    case PIN_ERR_SLEW_TOO_FAST:     return "надлишкова крутизна фронту";
    case PIN_ERR_BACKUP_ALT:        return "альтернативна функція в домені RTC";
    case PIN_ERR_BACKUP_SPEED:      return "домен RTC не тримає такої швидкості";
    case PIN_ERR_BACKUP_CURRENT:    return "понад 3 мА на ніжці домену RTC";
    case PIN_ERR_PIN_CURRENT:       return "перевищено струм однієї ніжки";
    case PIN_ERR_PORT_CURRENT:      return "перевищено струм порту";
    case PIN_ERR_CHIP_CURRENT:      return "перевищено струм кристала";
    case PIN_ERR_DUPLICATE:         return "дві функції на одній ніжці";
    case PIN_ERR_LOCK_FAILED:       return "замок LCKR не підтвердився";
    default:                        return "невідомий стан";
    }
}

uint16_t pin_port_budget_ma(const GPIO_TypeDef* port)
{
    const int index = port_index(port);
    return (index < 0) ? 0U : g_port_ma[index];
}

uint16_t pin_chip_budget_ma(void)
{
    return g_chip_ma;
}
