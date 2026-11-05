#pragma once

#include "SensorFilter.hpp"
#include "MagnusEngine.hpp"

// Координатор роботи системи: фільтрує дані, розраховує точку роси
// та приймає рішення про увімкнення нагрівача для запобігання конденсації.
class DewPointDetector {
public:
    // safety_margin: додатковий запас в градусах Цельсія (наприклад, 2.0).
    // Нагрівач вмикатиметься, коли температура середовища наближатиметься до точки роси.
    explicit DewPointDetector(float safety_margin = 2.0f);

    // Обробка нових "сирих" показників з давачів.
    // Повертає true, якщо нагрівач має бути увімкненим.
    bool processReading(float raw_temperature, float raw_humidity);

    [[nodiscard]] float getLastDewPoint() const;
    [[nodiscard]] float getFilteredTemperature() const;
    [[nodiscard]] float getFilteredHumidity() const;

private:
    SensorFilter temp_filter_;
    SensorFilter hum_filter_;
    MagnusEngine engine_;
    
    float safety_margin_;
    float last_dew_point_;
    float filtered_temp_;
    float filtered_hum_;
    bool heater_on_;
};
