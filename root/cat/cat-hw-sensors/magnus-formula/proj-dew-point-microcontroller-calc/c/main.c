#include <stdio.h>
#include "dew_point.h"
#include "heater.h"

int main(void) {
    float temp = 15.0f;
    float humidity = 80.0f; // Відносна вологість у %

    HeaterState heater;
    heater_init(&heater, 2.0f, 3.0f); // Гістерезис 2°C, тримаємо на 3°C вище точки роси

    printf("Поточна температура: %.1f°C, Вологість: %.1f%%\n", temp, humidity);

    float dp_math = dew_point_math(temp, humidity);
    float dp_fast = dew_point_fast(temp, humidity);

    printf("Точка роси (math.h): %.2f°C\n", dp_math);
    printf("Точка роси (швидка): %.2f°C\n", dp_fast);

    heater_update(&heater, temp, dp_math);
    printf("Стан нагрівача: %s\n", heater.is_on ? "УВІМКНЕНО" : "ВИМКНЕНО");

    // Імітуємо нагрівання
    temp = 18.0f;
    heater_update(&heater, temp, dp_math);
    printf("Температура після нагрівання: %.1f°C\n", temp);
    printf("Стан нагрівача: %s\n", heater.is_on ? "УВІМКНЕНО" : "ВИМКНЕНО");

    return 0;
}
