// Налаштування конфігурації dead-time для об'єктно-орієнтованого C++ інтерфейсу
#include <Arduino.h>

class HalfBridgeDriver {
private:
    uint32_t deadTimeNs;
public:
    explicit HalfBridgeDriver(uint32_t dt_ns) : deadTimeNs(dt_ns) {}

    void configureDeadTimeTimer() {
        // Обчислення кількості тактів таймера для забезпечення безпечного мертвого часу
        uint32_t timerTicks = (F_CPU / 1000000000UL) * deadTimeNs;
        // Запис у регістр апаратного генератора dead-time (концептуальний приклад)
        #if defined(TIM1)
        TIM1->BDTR &= ~(0xFF);
        TIM1->BDTR |= (timerTicks & 0xFF);
        #endif
    }
};
