#include <math.h>

// Обчислення абсолютної висоти над рівнем моря за ISA (в метрах)
float calculate_altitude_absolute(float pressure_hpa) {
    if (pressure_hpa <= 0.0f) return 0.0f;
    const float p0 = 1013.25f; // Стандартний тиск на рівні моря (hPa)
    return 44330.77f * (1.0f - powf(pressure_hpa / p0, 0.19029495f));
}

// Обчислення відносної висоти відносно опорного тиску та температури
float calculate_altitude_relative(float pressure_hpa, float ref_pressure_hpa, float temp_celsius) {
    if (pressure_hpa <= 0.0f || ref_pressure_hpa <= 0.0f) return 0.0f;
    
    // Спрощена відносна формула
    float h_std = 44330.77f * (1.0f - powf(pressure_hpa / ref_pressure_hpa, 0.19029495f));
    
    // Температурна корекція відносно ISA стаціонарних 15°C (288.15 K)
    float temp_kelvin = temp_celsius + 273.15f;
    float temp_correction = temp_kelvin / 288.15f;
    
    return h_std * temp_correction;
}
