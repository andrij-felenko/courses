/* main.c — маршрут із п'яти кроків, пройдений кодом.
 *
 * Datasheet          → ніжки PB6/PB7 і номер альтернативної функції 4;
 * Reference Manual   → шини, тактування, карта регістрів, порядок ініціалізації;
 * Programming Manual → NVIC, пріоритет вектора, бар'єри DSB/ISB;
 * Errata Sheet       → ревізія кремнію й обхід зависання шини I2C.
 */
#include <stdbool.h>
#include <stdint.h>

#include "i2c_recovery.h"
#include "rcc.h"
#include "silicon_rev.h"
#include "stm32f4_regs.h"
#include "timer.h"

/* Числа з Datasheet і розділу тактування Reference Manual для плати з
 * кварцом 8 МГц і PLL на 168 МГц. Таймери APB1 бачать подвоєну частоту
 * шини, бо дільник APB1 не одиничний (RM0090 §6.2). */
#define CPU_CLOCK_HZ        168000000UL
#define APB1_CLOCK_HZ        42000000UL
#define TIM2_CLOCK_HZ        84000000UL

/* Останній код помилки лишаємо в пам'яті: у пристрої без консолі це єдине,
 * що побачить інженер, підключившись налагоджувачем до зупиненої плати. */
volatile uint32_t g_last_error;

static void halt(uint32_t code)
{
    g_last_error = code;
    for (;;) {
        /* Тут у справжньому виробі спрацював би сторожовий таймер. */
    }
}

int main(void)
{
    const silicon_info_t *chip = silicon_info();

    /* Перше питання до заліза: а це взагалі той чип, під який набрано карту
     * регістрів і таблицю еррати? Чужий DEV_ID означає, що всі наші зміщення
     * вказують у порожнечу. */
    if (!chip->recognised) {
        halt(0xDEAD0001UL);
    }

    /* Ревізія вирішує, які обходи вмикати. На новому кремнії гілки нижче
     * просто не виконаються — і старт не сповільниться. */
    const bool i2c_lock_possible = silicon_affected_by(ERRATUM_I2C_BUSY_LOCK);

    if (i2c_init(APB1_CLOCK_HZ, CPU_CLOCK_HZ) != I2C_OK) {
        halt(0xDEAD0002UL);
    }

    /* Шина може бути зайнята вже на старті: пристрій міг перезавантажитися
     * посеред кадру, лишивши веденого з недорахованим байтом. */
    if (i2c_bus_busy()) {
        if (!i2c_lock_possible) {
            /* Ревізія не уражена, а BUSY стоїть — обхід еррати тут ні до чого,
             * але сама послідовність звільнення шини лишається правильною. */
            g_last_error = 0x1BADC0DEUL;
        }
        if (i2c_recover_bus() != I2C_OK) {
            halt(0xDEAD0003UL);
        }
    }

    if (timer_1khz_start(TIM2_CLOCK_HZ) != TIMER_OK) {
        halt(0xDEAD0004UL);
    }

    uint32_t last_second = timer_ticks();

    for (;;) {
        const uint32_t now = timer_ticks();

        /* Віднімання без порівняння «більше»: коли лічильник переповниться
         * через 49 діб, різниця беззнакових усе одно лишиться правильною. */
        if ((now - last_second) >= 1000UL) {
            last_second += 1000UL;

            /* Раз на секунду перевіряємо, чи не завис контролер шини знову:
             * еррата спрацьовує не на старті, а посеред роботи. */
            if (i2c_bus_busy()) {
                (void)i2c_recover_bus();
            }
        }
    }
}
