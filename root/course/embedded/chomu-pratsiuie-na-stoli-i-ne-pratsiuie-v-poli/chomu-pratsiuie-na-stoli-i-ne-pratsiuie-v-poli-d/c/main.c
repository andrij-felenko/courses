/* main.c — польовий модуль моніторингу середовища.
 *
 * Порядок старту тут не випадковий: спершу з'ясувати, ЧОМУ ми взагалі
 * стартували, і лише потім вмикати те, що споживає струм. Прилад, який
 * піднімає радіо до читання прапорів скидання, у циклі Brownout-перезапусків
 * так і не доживе до діагностики самого себе.
 */

#include "fault_log.h"
#include "i2c_rescue.h"
#include "platform.h"
#include "supervisor.h"

#define SENSOR_ADDR 0x44u /* давач вологості на зовнішній шині */
#define SENSOR_REG_STATUS 0x00u

#define STEP_PERIOD_MS 100u
#define BUS_CHECK_PERIOD_MS 1000u
#define RADIO_PERIOD_MS 30000u
#define RADIO_BURST_MS 300u
#define WATCHDOG_MS 4000u

/* Стільки марних порятунків шини поспіль — і перезапускаємось цілком. */
#define BUS_GIVE_UP 5u

static supervisor_t g_sup;
static i2c_bus_t g_bus;
static boot_report_t g_boot;

/* Скидання за власним рішенням: спершу знімаємо навантаження, щоб під час
 * перезапуску шина не тримала імпульс струму, і лише тоді б'ємо по AIRCR. */
static void controlled_reset(const supervisor_t *sup, uint32_t now_ms)
{
    plat_load_set(PLAT_LOAD_RADIO, false);
    plat_load_set(PLAT_LOAD_HEATER, false);
    plat_load_set(PLAT_LOAD_CHARGER, false);

    fault_log_append(RESET_CAUSE_SOFTWARE, sup->last_temp_c, sup->idle_mv,
                     now_ms - sup->started_ms);
    plat_delay_us(2000u);
    plat_system_reset();
}

int main(void)
{
    plat_init();

    /* Сторожовий таймер піднімаємо ДО першої довгої операції: якщо
     * ініціалізація впаде на завислій шині, нас перезапустить залізо. */
    plat_watchdog_start(WATCHDOG_MS);

    fault_log_open(&g_boot);

    const uint32_t boot_ms = plat_millis();
    const bool safe_start = fault_log_needs_safe_start(&g_boot);

    i2c_bus_init(&g_bus, SENSOR_ADDR);
    supervisor_init(&g_sup, safe_start, boot_ms);

    /* Перший запис — сам факт старту з його причиною. Температури й напруги
     * ще не знаємо, тому пишемо нулі: подія важливіша за подробиці, і саме
     * за цим рядком потім видно ланцюг нічних перезапусків. */
    fault_log_append(g_boot.cause, 0, 0u, 0u);

    uint32_t next_step = boot_ms;
    uint32_t next_bus_check = boot_ms + BUS_CHECK_PERIOD_MS;
    uint32_t next_radio = boot_ms + RADIO_PERIOD_MS;
    uint32_t radio_until = 0u;
    bool radio_on = false;

    for (;;) {
        plat_watchdog_kick();

        const uint32_t now = plat_millis();

        /* --- крок політики середовища --- */
        if ((int32_t)(now - next_step) >= 0) {
            next_step = now + STEP_PERIOD_MS;

            field_sample_t sample;
            (void)supervisor_sample(&sample); /* часткові дані теж корисні:
                                               * супервізор сам вирішує, чи він осліп */
            supervisor_step(&g_sup, &sample, now);
        }

        /* --- нагляд за зовнішньою шиною --- */
        if ((int32_t)(now - next_bus_check) >= 0) {
            next_bus_check = now + BUS_CHECK_PERIOD_MS;

            const bus_health_t health = i2c_bus_check(&g_bus);
            if (health == BUS_HEALTH_OK || health == BUS_HEALTH_RECOVERED) {
                uint8_t raw[2] = {0u, 0u};
                (void)i2c_bus_read(&g_bus, SENSOR_REG_STATUS, raw, sizeof raw);
            } else if (g_bus.recover_streak >= BUS_GIVE_UP) {
                /* Дев'ять тактів не допомогли п'ять разів поспіль: тримає не
                 * раб, а щось на платі — конденсат, дендрит, тріщина в пайці.
                 * Лишився повний перезапуск із перезаливкою периферії; якщо
                 * і він не поможе, наступний старт побачить лічильник
                 * сторожових скидань і піде в обережний режим. */
                controlled_reset(&g_sup, now);
            }
        }

        /* --- сеанс зв'язку --- */
        if (!radio_on && (int32_t)(now - next_radio) >= 0) {
            if (supervisor_radio_acquire(&g_sup) == SUP_RADIO_ALLOWED) {
                radio_on = true;
                radio_until = now + RADIO_BURST_MS;
                next_radio = now + RADIO_PERIOD_MS;
            } else {
                /* Відмову не «пропускаємо» до наступного повного періоду:
                 * мороз і перегрів минають за хвилини, і сеанс краще
                 * спробувати раніше, ніж за півгодини. */
                next_radio = now + RADIO_PERIOD_MS / 6u;
            }
        }

        if (radio_on &&
            ((int32_t)(now - radio_until) >= 0 || !plat_load_get(PLAT_LOAD_RADIO))) {
            /* Друга умова — це коли передавач зняли не ми, а supervisor_step
             * через просадку шини. Звільнення все одно проходить через
             * супервізор: він на цьому замірі уточнює внутрішній опір. */
            supervisor_radio_release(&g_sup);
            radio_on = false;
        }
    }
}
