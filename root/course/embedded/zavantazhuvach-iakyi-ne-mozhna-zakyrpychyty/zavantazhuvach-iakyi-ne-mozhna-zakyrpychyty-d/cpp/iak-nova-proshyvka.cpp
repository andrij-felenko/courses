#include <cstdint>

void app_main() noexcept
{
    // 1. Рання ініціалізація заліза
    hardware_early_init();
    watchdog_feed();

    // 2. Комплексний самотест підсистем
    const bool sensors_ready = sensors_self_test();
    const bool network_ready = network_stack_connect();

    if (sensors_ready && network_ready) {
        // Успіх: переводимо слот у стан Confirmed
        bootloader_mark_image_confirmed();
    } else {
        // Збій: зациклюємося без годування сторожа для ініціації відкату
        log_error("POST failure on new firmware. Triggering rollback...");
        while (true) {
            // Watchdog скине процесор через таймаут
        }
    }

    // 3. Основний виробничий цикл
    while (true) {
        watchdog_feed();
        process_telemetry();
    }
}
