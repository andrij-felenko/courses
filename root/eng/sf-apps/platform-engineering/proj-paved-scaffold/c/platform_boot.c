// platform_boot.c — реалізація вимощеної дороги. Продуктова
// команда цього не бачить: уся ретельність згорнута сюди.
#include "platform.h"

// ── дрібні внутрішні помічники (реєстрова робота схована тут) ──
static void      clock_select(clk_src_t src);
static bool      clock_wait_stable(uint32_t timeout_loops);
static void      clock_set_pll(uint32_t target_hz);
static void      wdt_configure(uint32_t period_ms);
static bool      uart_log_init(uint16_t baud_kbps);
static void      log_line(const char *msg);   // тихо мовчить, поки журнал не піднято

// Скільки холостих ітерацій чекати стабілізації генератора,
// перш ніж визнати його мертвим. Значення — з errata кремнію,
// узгоджене ОДИН раз для всієї лінійки, а не двадцять різних.
#define CLK_STABILIZE_TIMEOUT  50000u

// Безпечний період watchdog за замовчуванням, якщо команда лишила 0.
#define WDT_DEFAULT_MS         2000u

pb_result_t platform_boot(const platform_cfg_t *cfg) {
    // 0) Найперше — звірити версію. Якщо конфіг зібрано під іншу
    //    розкладку структури, читати його поля НЕБЕЗПЕЧНО: те,
    //    що ми вважаємо за cpu_hz, може бути чужим полем.
    if (cfg == 0 || cfg->abi_version != PLATFORM_ABI_VERSION) {
        // Журналу ще нема, тож сказати нема куди — лишається код.
        return PB_ERR_ABI_MISMATCH;
    }

    // 1) Перевірити діапазони. Дорога не пускає в явно биті значення:
    //    краще чесно впасти тут, ніж загадково зависнути потім.
    if (cfg->cpu_hz < 1000000u || cfg->cpu_hz > 120000000u) {
        return PB_ERR_BAD_CFG;
    }

    // 2) Тактування — серце старту. Спершу обрати джерело,
    //    ДОЧЕКАТИСЯ стабілізації (саме тут ховалася розбіжність
    //    між командами!), тоді підняти множник PLL до потрібної частоти.
    clock_select(cfg->clk_src);
    if (!clock_wait_stable(CLK_STABILIZE_TIMEOUT)) {
        return PB_ERR_CLOCK;   // генератор не завівся — далі йти немає сенсу
    }
    clock_set_pll(cfg->cpu_hz);

    // 3) Журнал — якнайраніше після тактування, щоб решта старту
    //    могла лишати сліди. Швидкість 0 означає «свідомо без журналу».
    if (cfg->log_baud_kbps != 0u) {
        if (!uart_log_init(cfg->log_baud_kbps)) {
            // Журнал — зручність, не серце. Не валимо весь старт;
            // повернемо м'який код, хай команда сама вирішує суворість.
            // (Система при цьому вже тактується — вона жива.)
            return PB_ERR_LOG;
        }
        log_line("platform: clock up, log up");
    }

    // 4) Watchdog — останнім, коли решта вже піднялася: інакше він
    //    може перезавантажити нас посеред власного налаштування.
    if (cfg->watchdog) {
        uint32_t period = (cfg->watchdog_ms != 0u)
                        ? cfg->watchdog_ms
                        : WDT_DEFAULT_MS;   // 0 → безпечний дефолт
        wdt_configure(period);
        log_line("platform: watchdog armed");
    }

    log_line("platform: boot ok");
    return PB_OK;
}
