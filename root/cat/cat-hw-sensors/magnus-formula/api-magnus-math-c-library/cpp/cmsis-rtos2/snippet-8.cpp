#include "cmsis_os2.h"

namespace atmospheric {

// Паралельна обробка даних вологості у середовищі RTOS без блокувань
void EnvironmentTask(void *argument) {
    float temp = 18.0f;
    float rh = 75.0f;

    while (true) {
        auto result = calculateDewPointSafe(temp, rh, PARAMS_WATER);
        if (result.status == Status::Ok) {
            // Безпечна робота з результатами у локальному контексті потоку
        }
        osDelay(1000);
    }
}

} // namespace atmospheric
