// Код продуктової команди: увесь нудний старт — один рядок.
#include "platform.h"

int main(void) {
    platform_cfg_t cfg = PLATFORM_DEFAULT_CFG;   // беремо вимощену дорогу як є
    if (platform_boot(&cfg) != 0) {
        // Платформа сама лишила слід у журналі — тут лише безпечна зупинка.
        for (;;) { /* watchdog перезавантажить пристрій */ }
    }

    app_run();     // з цієї миті — власне продукт команди
    return 0;
}
