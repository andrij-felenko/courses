#include <chrono>

/* Безпечний патерн: передача кванта часу планувальнику операційної системи */
class SensorTimeAbstraction {
public:
    static void non_blocking_delay(std::chrono::microseconds duration) {
        if (duration >= std::chrono::milliseconds(1)) {
            // Виклик системного переведення задачі в сон: vTaskDelay / k_sleep
        } else {
            // Апаратний мікросекундний таймер DWT
        }
    }
};
