#include <Arduino.h>
#include <cstdint>

class HardwareTimeSlicer {
public:
    enum class TaskId : uint8_t {
        kTaskA = 0,
        kTaskB = 1
    };

    static void InitTickTimer(uint32_t period_ms) {
        // Налаштування системного таймера Arduino / ARM SysTick
        uint32_t ticks = (SystemCoreClock / 1000) * period_ms;
        SysTick_Config(ticks);
    }

    static inline volatile TaskId current_task = TaskId::kTaskA;
    static inline volatile uint32_t tick_counter = 0;
};

// Перевизначення системного обробника тіка
extern "C" void SysTick_Handler(void) {
    HardwareTimeSlicer::tick_counter++;
    if (HardwareTimeSlicer::tick_counter >= 10) { // Квант = 10 мс
        HardwareTimeSlicer::tick_counter = 0;
        if (HardwareTimeSlicer::current_task == HardwareTimeSlicer::TaskId::kTaskA) {
            HardwareTimeSlicer::current_task = HardwareTimeSlicer::TaskId::kTaskB;
        } else {
            HardwareTimeSlicer::current_task = HardwareTimeSlicer::TaskId::kTaskA;
        }
    }
}

void setup() {
    HardwareTimeSlicer::InitTickTimer(1); // Тік 1 мс
}

void loop() {
    if (HardwareTimeSlicer::current_task == HardwareTimeSlicer::TaskId::kTaskA) {
        // Виконання кванта Задачі A
    } else {
        // Виконання кванта Задачі B
    }
}
