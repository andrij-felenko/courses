#include <Arduino.h>
#include <FreeRTOS.h>
#include <queue.h>

class DeferredWorkItem {
public:
    using Callback_t = void (*)(void*);

    DeferredWorkItem() : func_(nullptr), arg_(nullptr) {}
    DeferredWorkItem(Callback_t func, void* arg) : func_(func), arg_(arg) {}

    void execute() const {
        if (func_ != nullptr) {
            func_(arg_);
        }
    }

private:
    Callback_t func_;
    void* arg_;
};

struct AccelerometerData {
    int16_t x;
    int16_t y;
    int16_t z;
};

static AccelerometerData g_accel_data;
static DeferredWorkItem g_accel_work;

void handle_accel_event(void* arg) {
    AccelerometerData* data = static_cast<AccelerometerData*>(arg);
    // Обчислення вектора прискорення у фоновому режимі
    (void)data;
}

void setup_work_item() {
    g_accel_work = DeferredWorkItem(handle_accel_event, &g_accel_data);
}

bool submit_work_isr(QueueHandle_t queue, BaseType_t& higher_woken) {
    return xQueueSendFromISR(queue, &g_accel_work, &higher_woken) == pdTRUE;
}
