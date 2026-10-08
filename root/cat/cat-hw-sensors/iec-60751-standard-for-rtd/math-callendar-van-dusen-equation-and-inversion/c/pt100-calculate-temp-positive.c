#include <math.h>

#define RTD_R0 100.0f
#define CVD_A  3.9083e-3f
#define CVD_B  -5.775e-7f

// Обчислення температури (t >= 0 °C) за виміряним опором R
float pt100_calculate_temp_positive(float r_measured) {
    if (r_measured < RTD_R0) {
        // Опір менше 100 Ом відповідає від'ємним температурам
        return -1.0f; // Потрібно використовувати алгоритми для t < 0 °C
    }
    
    float ratio = r_measured / RTD_R0;
    float discriminant = (CVD_A * CVD_A) - (4.0f * CVD_B * (1.0f - ratio));
    
    // Аналітичний розв'язок квадратного рівняння
    float temp = (-CVD_A + sqrtf(discriminant)) / (2.0f * CVD_B);
    return temp;
}
