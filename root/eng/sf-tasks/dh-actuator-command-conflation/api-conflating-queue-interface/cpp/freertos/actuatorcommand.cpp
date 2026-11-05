#include <cstdint>
#include <atomic>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace Hardware {

struct ActuatorCommand {
    uint16_t pulseWidthUs;
    uint8_t  direction;
};

class ConflatingActuatorDriver {
public:
    ConflatingActuatorDriver() : driverTaskHandle_(nullptr) {
        hasNewData_.store(false, std::memory_order_relaxed);
    }

    void init(TaskHandle_t taskHandle) {
        driverTaskHandle_ = taskHandle;
    }

    // Вставка команди з атомарним згортанням проміжних станів
    void pushCommand(uint16_t pulseUs, uint8_t dir) {
        ActuatorCommand cmd{pulseUs, dir};
        
        // Запис у слот з атомарним розповсюдженням прапорця
        slotData_ = cmd;
        hasNewData_.store(true, std::memory_order_release);

        if (driverTaskHandle_ != nullptr) {
            xTaskNotifyGive(driverTaskHandle_);
        }
    }

    // Виконання циклу обробки драйвера
    void processLoop() {
        for (;;) {
            ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

            if (hasNewData_.exchange(false, std::memory_order_acq_rel)) {
                ActuatorCommand cmd = slotData_;
                
                // Обмеження діапазону для захисту виконавчого механізму
                if (cmd.pulseWidthUs < 1000) cmd.pulseWidthUs = 1000;
                if (cmd.pulseWidthUs > 2000) cmd.pulseWidthUs = 2000;

                commitToRegisters(cmd);
            }
        }
    }

private:
    void commitToRegisters(const ActuatorCommand& cmd) {
        // Запис у регістри порівняння таймера периферії
        // TIM1->CCR1 = cmd.pulseWidthUs;
    }

    ActuatorCommand          slotData_{1500, 1};
    std::atomic<bool>        hasNewData_;
    TaskHandle_t             driverTaskHandle_;
};

} // namespace Hardware
