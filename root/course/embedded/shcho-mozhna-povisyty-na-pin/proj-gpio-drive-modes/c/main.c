/* main.c — усе докупи в порядку, який не клацає навантаженням на старті.
 *
 * Плата: світлодіод-індикатор на PC13 (вмикається нулем), релейний модуль на
 * PB0 (теж активний нуль), шина I2C на PB8/PB9 із зовнішніми підтяжками 4.7 кОм. */
#include "gpio_regs.h"
#include "load_pin.h"
#include "opendrain.h"

#include <stddef.h>

static const load_pin_t g_led = {
    .port = GPIO_PORT_C, .pin = 13, .active_low = true, .speed = GPIO_SPEED_LOW
};

static const load_pin_t g_relay = {
    .port = GPIO_PORT_B, .pin = 0, .active_low = true, .speed = GPIO_SPEED_LOW
};

static const od_line_t g_scl = {
    .port = GPIO_PORT_B, .pin = 8, .speed = GPIO_SPEED_MEDIUM, .rise_loops = 200
};

static const od_line_t g_sda = {
    .port = GPIO_PORT_B, .pin = 9, .speed = GPIO_SPEED_MEDIUM, .rise_loops = 200
};

/* На мікроконтролері без відлагоджувального каналу нема куди друкувати,
 * тому код зупинки лишаємо в змінній: її видно в GDB і в дампі пам'яті. */
static volatile int g_fault_code = 0;

static void halt(int code)
{
    /* Спершу гасимо все, що керує потужністю, і лише тоді стаємо. */
    (void)load_pin_park(&g_relay);
    (void)load_pin_park(&g_led);
    (void)od_line_release(&g_scl);
    (void)od_line_release(&g_sda);

    g_fault_code = code;
    for (;;) {
    }
}

/* Демонстрація того, що лінія справді керована: притиснути, переконатися в
 * нулі, відпустити, дочекатися одиниці. Так виявляється завелика підтяжка
 * або зайва ємність — фронт не встигає за відведений час. */
static bool wiggle(const od_line_t *line)
{
    bool level = false;

    if (od_line_drive_low(line) != GPIO_OK) {
        return false;
    }
    gpio_spin(line->rise_loops);
    if (od_line_level(line, &level) != GPIO_OK || level) {
        return false;
    }

    if (od_line_release(line) != GPIO_OK) {
        return false;
    }
    gpio_spin(line->rise_loops);
    if (od_line_level(line, &level) != GPIO_OK || !level) {
        return false;
    }

    return true;
}

int main(void)
{
    /* 1. Виходи під навантаження — раніше за все інше. */
    if (load_pin_init(&g_led) != GPIO_OK) {
        halt(1);
    }
    if (load_pin_init(&g_relay) != GPIO_OK) {
        halt(2);
    }

    /* 2. Шина з відкритим стоком. */
    if (od_line_init(&g_scl) != GPIO_OK || od_line_init(&g_sda) != GPIO_OK) {
        halt(3);
    }

    /* 3. Перевірка проводки — до першого обміну, а не після дивних NACK. */
    if (od_line_check(&g_scl) != OD_WIRING_OK) {
        halt(4);
    }
    if (od_line_check(&g_sda) != OD_WIRING_OK) {
        halt(5);
    }
    if (!wiggle(&g_sda)) {
        halt(6);
    }

    /* 4. Робочий цикл: індикатор блимає, реле вмикається раз на цикл і має
     *    вдосталь часу у вимкненому стані — механіка не любить швидкого
     *    клацання, а живлення не любить пускового струму котушки. */
    unsigned tick = 0;
    for (;;) {
        if (load_pin_toggle(&g_led) != GPIO_OK) {
            halt(7);
        }

        if (tick % 40u == 0u) {
            if (load_pin_set(&g_relay, true) != GPIO_OK) {
                halt(8);
            }
        } else if (tick % 40u == 4u) {
            if (load_pin_set(&g_relay, false) != GPIO_OK) {
                halt(9);
            }
        }

        gpio_spin(400000u);
        ++tick;
    }
}
