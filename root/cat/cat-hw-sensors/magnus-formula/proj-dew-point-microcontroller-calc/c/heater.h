#ifndef HEATER_H
#define HEATER_H

#include <stdbool.h>

typedef struct {
    bool is_on;
    float hysteresis_c;
    float safety_margin_c; // На скільки градусів вище точки роси тримати температуру
} HeaterState;

void heater_init(HeaterState* heater, float hysteresis, float margin);
void heater_update(HeaterState* heater, float current_temp, float dew_point);

#endif // HEATER_H
