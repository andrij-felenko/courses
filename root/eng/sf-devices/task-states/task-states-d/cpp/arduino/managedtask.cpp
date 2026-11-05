#include <Arduino.h>
#include <FreeRTOS.h>
#include <task.h>

// C++ клас управління станами та запобігання голодуванню
class ManagedTask {
private:
    TaskHandle_t handle;
    bool isSuspended;

public:
    ManagedTask() : handle(nullptr), isSuspended(false) {}

    void setHandle(TaskHandle_t h) { handle = h; }

    void suspend() {
        if (handle && !isSuspended) {
            vTaskSuspend(handle); // Перехід у стан Suspended
            isSuspended = true;
        }
    }

    void resume() {
        if (handle && isSuspended) {
            vTaskResume(handle); // Перехід у стан Ready
            isSuspended = false;
        }
    }

    // Добровільна передача процесорного кванта (yield)
    static void yieldCurrentTask() {
        taskYIELD();
    }
};
