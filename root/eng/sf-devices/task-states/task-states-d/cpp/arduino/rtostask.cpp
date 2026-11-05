#include <Arduino.h>

// C++ обгортка для задачі RTOS
class RtosTask {
private:
    TaskHandle_t handle;

public:
    RtosTask() : handle(nullptr) {}

    void suspend() {
        if (handle != nullptr) {
            vTaskSuspend(handle); // Перехід у стан Suspended
        }
    }

    void resume() {
        if (handle != nullptr) {
            vTaskResume(handle); // Відновлення до стану Ready
        }
    }

    // Системний виклик очікування події (перехід у стан Blocked)
    static void sleepMs(uint32_t ms) {
        vTaskDelay(pdMS_TO_TICKS(ms));
    }
};
