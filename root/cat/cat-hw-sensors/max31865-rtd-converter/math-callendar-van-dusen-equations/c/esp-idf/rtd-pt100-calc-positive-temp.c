#include <math.h>
#include <stdbool.h>

// Коефіцієнти Каллендара — Ван Дюзена за стандартом IEC 60751
#define RTD_R0 100.0          // Номінальний опір PT100 за 0 °C (Ом)
#define RTD_A  3.9083e-3      // Коефіцієнт A (°C⁻¹)
#define RTD_B  -5.7750e-7     // Коефіцієнт B (°C⁻²)

/**
 * @brief Обчислення температури t >= 0 °C за виміряним опором RTD
 * @param r_ohms Виміряний опір у омах
 * @param temp_out Вказівник для збереження обчисленої температури
 * @return true якщо опір у межах додатного діапазону, false при помилці
 */
bool rtd_pt100_calc_positive_temp(double r_ohms, double *temp_out) {
    if (r_ohms < RTD_R0 || temp_out == NULL) {
        return false; // Помилка: опір менший за R0 (температура від'ємна)
    }

    double r_ratio = r_ohms / RTD_R0;
    double abs_b = -RTD_B;
    double discriminant = (RTD_A * RTD_A) + (4.0 * abs_b * (r_ratio - 1.0));

    if (discriminant < 0.0) {
        return false; // Фізично неможливий від'ємний дискримінант
    }

    // Аналітична формула для t >= 0 °C
    *temp_out = (RTD_A - sqrt(discriminant)) / (2.0 * RTD_B);
    return true;
}
