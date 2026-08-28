#include "platform.h"

int main(void) {
    // Беремо вимощену дорогу як основу...
    platform_cfg_t cfg = PLATFORM_DEFAULT_CFG;

    // ...і зсуваємося з неї лише в одному місці: цей пристрій
    // без кварцу, тактуємо внутрішнім RC. Усе інше — як у всіх.
    cfg.clk_src = CLK_SRC_INTERNAL;

    pb_result_t r = platform_boot(&cfg);
    if (r != PB_OK) {
        // Платформа вже назвала причину (код + слід у журналі).
        // Тут — лише безпечна зупинка; watchdog перезавантажить пристрій.
        for (;;) { }
    }

    app_run();   // з цієї миті — власне продукт команди
    return 0;
}
