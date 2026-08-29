#include "low_power_pins.h"

/* Виводи, які НЕ можна кидати в аналоговий режим.
 *
 * PA0 — кнопка й вхід пробудження EXTI0. Аналоговий режим від'єднує тригер
 *       Шмітта, і плата перестає бачити фронт: зовні це виглядає як мертвий
 *       виріб, який оживає лише зняттям живлення.
 * PB12 — затвор силового ключа. Він мусить лишатися виходом і тримати одиницю
 *       весь сон: відпустиш його в Hi-Z — затвор підтягнеться витоком, ключ
 *       привідкриється, і датчики почнуть живитися посеред «глибокого сну».
 */
#define KEEP_WAKE_BUTTON (1U << 0)  /* PA0 */
#define KEEP_LOAD_SWITCH (1U << 12) /* PB12 */

typedef struct {
    gpio_t  *port;
    uint32_t keep_mask; /* по одному біту на вивід */
} port_desc_t;

static const port_desc_t k_ports[] = {
    { GPIOA, KEEP_WAKE_BUTTON },
    { GPIOB, KEEP_LOAD_SWITCH },
    { GPIOC, 0U },
};

#define PORT_COUNT (sizeof(k_ports) / sizeof(k_ports[0]))

typedef struct {
    uint32_t moder;
    uint32_t pupdr;
    uint32_t odr;
} port_backup_t;

static port_backup_t g_backup[PORT_COUNT];
static bool g_isolated;

/* Розгортає бітову маску виводів у маску двобітових полів MODER/PUPDR. */
static uint32_t pins_to_field_mask(uint32_t pin_mask)
{
    uint32_t field = 0U;
    for (unsigned pin = 0U; pin < 16U; pin++) {
        if ((pin_mask & (1UL << pin)) != 0U) {
            field |= (3UL << (pin * 2U));
        }
    }
    return field;
}

static void port_isolate(const port_desc_t *d, port_backup_t *bk)
{
    bk->moder = d->port->MODER;
    bk->pupdr = d->port->PUPDR;
    bk->odr   = d->port->ODR;

    uint32_t keep = pins_to_field_mask(d->keep_mask);

    /* Спершу MODER, потім PUPDR — і це не дрібниця.
     * Аналоговий режим від'єднує вхідний буфер; якщо зняти підтяжку раніше,
     * вивід лишиться цифровим входом із плаваючим рівнем і почне сіпатися
     * біля порога, а кожне сіпання це наскрізний струм у вхідному інверторі. */
    d->port->MODER = (bk->moder & keep) | (0xFFFFFFFFUL & ~keep);
    d->port->PUPDR = (bk->pupdr & keep); /* решта — нуль, тобто без підтяжки */
}

static void port_restore(const port_desc_t *d, const port_backup_t *bk)
{
    /* Рівні виходів повертаємо ДО режимів: інакше вивід на мить стане виходом
     * зі старим вмістом засувки й смикне лінію. Виводи зі списку винятків
     * лишаємо як є — вони не спали, і їхній поточний рівень свіжіший. */
    uint32_t keep = d->keep_mask;
    d->port->ODR = (bk->odr & ~keep) | (d->port->ODR & keep);

    d->port->PUPDR = bk->pupdr;
    d->port->MODER = bk->moder;
}

void lp_pins_enter_sleep(void)
{
    for (unsigned n = 0U; n < PORT_COUNT; n++) {
        port_isolate(&k_ports[n], &g_backup[n]);
    }

    /* Сигнальні лінії шин уже відпущено в Hi-Z у bus_quiesce_all() — саме
     * відпущено, а не зведено в нуль. Зводити в нуль можна лише поки датчик
     * іще живиться; після розмикання ключа нуль на лінії стає стоком для
     * заряду блокувальних ємностей через нижній захисний діод. */

    /* Блок налагодження. Поки в DBGMCU_CR стоять DBG_SLEEP/STOP/STANDBY,
     * ядро в Stop лишає ввімкненим тактове дерево налагодження — плата спить,
     * а споживає міліампери. На столі це ховається за струмом самого
     * налагоджувача, і вилазить аж на батарейці. */
    DBGMCU_CR &= ~(DBGMCU_CR_DBG_SLEEP | DBGMCU_CR_DBG_STOP | DBGMCU_CR_DBG_STANDBY);

    g_isolated = true;
}

void lp_pins_restore(void)
{
    if (!g_isolated) {
        return; /* прокинулися не зі сну — відновлювати нічого */
    }

    for (unsigned n = 0U; n < PORT_COUNT; n++) {
        port_restore(&k_ports[n], &g_backup[n]);
    }

    g_isolated = false;
}

bool lp_pins_is_isolated(void)
{
    return g_isolated;
}
