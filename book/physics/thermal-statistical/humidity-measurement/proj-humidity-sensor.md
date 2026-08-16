# ⚙️ Алгоритми термокомпенсації та точки роси

Ця практична вставка містить закончену реалізацію алгоритмів термокомпенсації вимірювань ємнісних сорбційних сенсорів, обчислення тиску насиченої пари, точки роси, абсолютної вологості та ентальпії вологого повітря мовами C та C++.

---

### Фізична та програмна постановка задачі

Мікроелектронні ємнісні сорбційні датчики вологості (наприклад, серій SHT3x, SHT4x або дискретні ємнісні елементи Humicap) вимірюють відносну вологість повітря `RH_raw` через зміну діелектричної проникності полімеру. Чутливий шар полімеру поглинає молекули водяної пари, змінюючи свою діелектрична проникність від значення сухого стану `ε_p ≈ 3.2` до значення вологого стану, оскільки діелектрична проникність рідкої води досягає `ε_H2O ≈ 80.1` при температурі 20°C.

Проте при використанні сорбційних елементів у реальних мікроконтролерних системах виникають дві фундаментальні проблеми:
1. **Температурний дрейф діелектричної проникності самого полімеру:** Полімерний шар має власний позитивний температурний коефіцієнт розширення та зміщення діелектричної сталої `α_T ≈ +0.15% RH/°C`. Якщо не компенсувати цей ефект, при зміні температури від 25°C до 45°C датчик покаже помилкове завищення вологості на 3% RH навіть за незмінного парціального тиску пари.
2. **Експоненціальна нелінійність тиску насичення пари `P_s(T)`:** Сам по собі сигнал відносної вологості `RH` недостатній для аналізу фазових переходів у приладі. Інженерні системи (HVAC, блоки контролю роси у вуличних шафах автоматики) вимагають знання прямої температури точки роси `T_d`, при якій випадає конденсат, а також влаговмісту `w` та питомої ентальпії `h` для розрахунку потужності калориферів і осушувачів.

Розроблений алгоритм розв'язує ці завдання у п'ять послідовних кроків:
1. **Зчитування та валідація:** Приймає з вимірювального каналу температуру `T` (°C) та сиру відносну вологість `RH_raw` (%), перевіряючи фізичні межі дійсності сигналів.
2. **Поліноміальна термокомпенсація:** Застосовує лінійну або квадратичну температурну поправку відносно еталонної температури калібрування (зазвичай 25°C).
3. **Обчислення тиску насичення `P_s(T)`:** Використовує термодинамічне рівняння Магнуса-Тетенса з динамічним перемиканням коефіцієнтів для фази води (`T ≥ 0°C`) або льоду (`T < 0°C`).
4. **Обчислення точки роси `T_d`:** Реалізує зворотне логарифмічне перетворення тиску водяної пари для обчислення точки роси з точністю вище `±0.1°C`.
5. **Розрахунок об'ємних і масових параметрів:** Обчислює абсолютну вологість `ρ_v` (г/м³) та питому ентальпію суміші `h` (кДж/кг сухого повітря).

---

### Апаратний адаптер та інтерфейс обробки

Вбудоване ПЗ мікроконтролера (наприклад, для архітектури STM32 HAL чи ESP-IDF) зв'язується із сенсором через низькорівневий драйвер шини I2C. Для запобігання блокуванню головного обчислювального потоку вимірювання виконуються за допомогою неблокуючого автомата станів (*Finite State Machine*) з транзакціями DMA.

Після закінчення АЦП-конверсії та зчитування 6-байтового каду даних з перевіркою контрольної суми CRC-8, сирі значення переходять до математичного ядра обробки.

Для зберігання індивідуальних коефіцієнтів калібрування сенсора застосовують енергонезалежну пам'ять (Flash або EEPROM). При завантаженні системи мікроконтролер перевіряє цілісність конфігурації за допомогою контрольної суми CRC32. Якщо еталонні коефіцієнти пошкоджено, алгоритм автоматично переходить на базові дефолтні значення паспорта виробника.

---

### Програмна реалізація

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Структура результатів обчислення стану вологого повітря */
typedef struct {
    float temperature_c;       /* Температура повітря, °C */
    float relative_humidity;   /* Компенсована відносна вологість, % */
    float vapor_pressure_pa;   /* Парціальний тиск водяної пари, Па */
    float sat_pressure_pa;     /* Тиск насиченої пари, Па */
    float dew_point_c;         /* Температура точки роси, °C */
    float absolute_humidity_g; /* Абсолютна вологість, г/м³ */
    float enthalpy_kj;         /* Ентальпія вологого повітря, кДж/кг */
    bool  is_valid;            /* Прапорець коректності обчислень */
} humidity_result_t;

/* Параметри компенсації датчика (задаються у паспорті елемента) */
typedef struct {
    float temp_coeff;          /* Температурний коефіцієнт (% RH / °C) */
    float cal_temp_c;          /* Температура калібрування (зазвичай 25°C) */
} humidity_sensor_cal_t;

/* Рівняння Магнуса для тиску насиченої пари */
static float calc_saturation_pressure(float temp_c) {
    float a, b, c;
    if (temp_c >= 0.0f) {
        a = 611.21f;
        b = 17.502f;
        c = 240.97f;
    } else {
        a = 611.15f;
        b = 22.452f;
        c = 272.55f;
    }
    return a * expf((b * temp_c) / (c + temp_c));
}

/* Обчислення точки роси за виразом Магнуса */
static float calc_dew_point(float temp_c, float rh_percent) {
    if (rh_percent <= 0.01f) {
        rh_percent = 0.01f;
    } else if (rh_percent > 100.0f) {
        rh_percent = 100.0f;
    }
    
    float b = (temp_c >= 0.0f) ? 17.502f : 22.452f;
    float c = (temp_c >= 0.0f) ? 240.97f : 272.55f;
    
    float gamma = (b * temp_c) / (c + temp_c) + logf(rh_percent / 100.0f);
    return (c * gamma) / (b - gamma);
}

/* Головна функція обробки даних датчика */
bool process_humidity_measurement(
    float temp_c, 
    float rh_raw, 
    const humidity_sensor_cal_t *cal, 
    humidity_result_t *out_res
) {
    if (!out_res) {
        return false;
    }
    
    /* Перевірка виходу за фізичні межі */
    if (temp_c < -50.0f || temp_c > 100.0f || rh_raw < -10.0f || rh_raw > 110.0f) {
        out_res->is_valid = false;
        return false;
    }

    /* 1. Температурна компенсація сирого значення вологості */
    float cal_temp = cal ? cal->cal_temp_c : 25.0f;
    float temp_coeff = cal ? cal->temp_coeff : 0.15f;
    
    float rh_comp = rh_raw - (temp_c - cal_temp) * temp_coeff;
    if (rh_comp < 0.0f) rh_comp = 0.0f;
    if (rh_comp > 100.0f) rh_comp = 100.0f;

    /* 2. Обчислення термодинамічних параметрів */
    float p_sat = calc_saturation_pressure(temp_c);
    float p_v = (rh_comp / 100.0f) * p_sat;
    float dew_point = calc_dew_point(temp_c, rh_comp);
    
    /* Абсолютна вологість: ρ_v = 2.1667 * P_v / (T + 273.15) */
    float abs_hum = 2.1667f * (p_v / (temp_c + 273.15f));
    
    /* Влаговміст w (г/кг): при P_atm = 101325 Па */
    float p_atm = 101325.0f;
    float w_g_kg = 621.98f * (p_v / (p_atm - p_v));
    
    /* Ентальпія h (кДж/кг) */
    float enthalpy = 1.006f * temp_c + (w_g_kg / 1000.0f) * (2501.0f + 1.86f * temp_c);

    /* Заповнення результату */
    out_res->temperature_c = temp_c;
    out_res->relative_humidity = rh_comp;
    out_res->sat_pressure_pa = p_sat;
    out_res->vapor_pressure_pa = p_v;
    out_res->dew_point_c = dew_point;
    out_res->absolute_humidity_g = abs_hum;
    out_res->enthalpy_kj = enthalpy;
    out_res->is_valid = true;

    return true;
}

int main(void) {
    humidity_sensor_cal_t cal = { .temp_coeff = 0.15f, .cal_temp_c = 25.0f };
    humidity_result_t res;

    float t_in = 30.0f;
    float rh_in = 50.0f;

    if (process_humidity_measurement(t_in, rh_in, &cal, &res)) {
        printf("--- Термодинамічний стан вологого повітря ---\n");
        printf("Температура:          %.2f °C\n", res.temperature_c);
        printf("Відносна вологість:   %.2f %%\n", res.relative_humidity);
        printf("Тиск насичення:       %.2f Па\n", res.sat_pressure_pa);
        printf("Парціальний тиск:     %.2f Па\n", res.vapor_pressure_pa);
        printf("Точка роси:           %.2f °C\n", res.dew_point_c);
        printf("Абсолютна вологість:  %.2f г/м³\n", res.absolute_humidity_g);
        printf("Ентальпія повітря:    %.2f кДж/кг\n", res.enthalpy_kj);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <optional>
#include <expected>
#include <string_view>
#include <algorithm>

namespace physics {

struct SensorCalibration {
    float temp_coefficient{0.15f}; // % RH / °C
    float ref_temperature_c{25.0f};
};

struct PsychrometricState {
    float temperature_c;       // °C
    float relative_humidity;   // %
    float sat_vapor_pressure;  // Pa
    float vapor_pressure;      // Pa
    float dew_point_c;         // °C
    float absolute_humidity;   // g/m³
    float enthalpy_kj_kg;      // kJ/kg
};

enum class HumidityError {
    TemperatureOutOfRange,
    HumidityOutOfRange,
    InvalidPressure
};

class HumidityCalculator {
public:
    explicit constexpr HumidityCalculator(SensorCalibration cal = {}) noexcept
        : cal_(cal) {}

    [[nodiscard]] std::expected<PsychrometricState, HumidityError> calculate(
        float temp_c, float rh_raw, float atm_pressure_pa = 101325.0f
    ) const noexcept {
        if (temp_c < -50.0f || temp_c > 100.0f) {
            return std::unexpected(HumidityError::TemperatureOutOfRange);
        }
        if (rh_raw < -10.0f || rh_raw > 110.0f) {
            return std::unexpected(HumidityError::HumidityOutOfRange);
        }
        if (atm_pressure_pa < 30000.0f || atm_pressure_pa > 150000.0f) {
            return std::unexpected(HumidityError::InvalidPressure);
        }

        // 1. Термокомпенсація вологості
        float rh_comp = rh_raw - (temp_c - cal_.ref_temperature_c) * cal_.temp_coefficient;
        rh_comp = std::clamp(rh_comp, 0.0f, 100.0f);

        // 2. Розрахунок тиску насичення
        float p_sat = calc_saturation_pressure(temp_c);
        float p_v = (rh_comp / 100.0f) * p_sat;

        // 3. Розрахунок точки роси
        float dew_point = calc_dew_point(temp_c, rh_comp);

        // 4. Абсолютна вологість та ентальпія
        float abs_hum = 2.1667f * (p_v / (temp_c + 273.15f));
        float w_kg_kg = 0.62198f * (p_v / (atm_pressure_pa - p_v));
        float enthalpy = 1.006f * temp_c + w_kg_kg * (2501.0f + 1.86f * temp_c);

        return PsychrometricState{
            .temperature_c = temp_c,
            .relative_humidity = rh_comp,
            .sat_vapor_pressure = p_sat,
            .vapor_pressure = p_v,
            .dew_point_c = dew_point,
            .absolute_humidity = abs_hum,
            .enthalpy_kj_kg = enthalpy
        };
    }

private:
    SensorCalibration cal_;

    [[nodiscard]] static constexpr float calc_saturation_pressure(float temp_c) noexcept {
        float a = (temp_c >= 0.0f) ? 611.21f : 611.15f;
        float b = (temp_c >= 0.0f) ? 17.502f : 22.452f;
        float c = (temp_c >= 0.0f) ? 240.97f : 272.55f;
        return a * std::exp((b * temp_c) / (c + temp_c));
    }

    [[nodiscard]] static float calc_dew_point(float temp_c, float rh_percent) noexcept {
        float safe_rh = std::clamp(rh_percent, 0.01f, 100.0f);
        float b = (temp_c >= 0.0f) ? 17.502f : 22.452f;
        float c = (temp_c >= 0.0f) ? 240.97f : 272.55f;

        float gamma = (b * temp_c) / (c + temp_c) + std::log(safe_rh / 100.0f);
        return (c * gamma) / (b - gamma);
    }
};

} // namespace physics

int main() {
    using namespace physics;
    
    HumidityCalculator calc{SensorCalibration{.temp_coefficient = 0.15f, .ref_temperature_c = 25.0f}};
    
    auto result = calc.calculate(30.0f, 50.0f);
    if (result) {
        const auto& state = *result;
        std::cout << "--- Термодинамічний стан (C++17/23) ---\n";
        std::cout << "Температура:          " << state.temperature_c << " °C\n";
        std::cout << "Відносна вологість:   " << state.relative_humidity << " %\n";
        std::cout << "Тиск насичення:       " << state.sat_vapor_pressure << " Па\n";
        std::cout << "Парціальний тиск:     " << state.vapor_pressure << " Па\n";
        std::cout << "Точка роси:           " << state.dew_point_c << " °C\n";
        std::cout << "Абсолютна вологість:  " << state.absolute_humidity << " г/м³\n";
        std::cout << "Ентальпія повітря:    " << state.enthalpy_kj_kg << " кДж/кг\n";
    }
    return 0;
}
```
:::

---

### Аналіз алгоритмічних пасток та оптимізацій

При практичному впровадженні цих алгоритмів у реальне мікроконтролерне ПЗ (наприклад, для ядра ARM Cortex-M0/M4 чи ESP32) слід враховувати такі інженерні нюанси:

1. **Заморожування сенсора та точка інею (Frost Point):** При температурах нижче 0°C рівноважний тиск пари над льодом `P_ice(T)` є нижчим, ніж над переохолодженою водою `P_water(T)`. Обчислення точки роси за формулою для води нижче 0°C призводить до системної похибки до `0.5 - 1.2°C`. У поданій програмній реалізації застосовано автоматичне динамічне перемикання коефіцієнтів `b` та `c` у функції `calc_saturation_pressure` при `T < 0°C`.
2. **Економіка математичних обчислень у Cortex-M0 (без апаратного FPU):** Обчислення функції `expf()` та `logf()` вимагає від софтверної бібліотеки `libm` кількох сотень тактів процесора. Для систем із жорстким часовим циклом (наприклад, PID-контролерів з частотою 100 Гц) функції `expf()` та `logf()` замінюють на поліноміальну апроксимацію Чебишова або таблиці пошуку (LUT — Look-Up Table) із білінійною інтерполяцією.
3. **Самонагрівання сенсора струмом вимірювання:** Живлення ємнісної схеми вимірювачем з високою частотою струму може викликати локальне виділення тепла Джоуля на чипі (на `0.2 - 0.5°C`). Оскільки тиск насичення `P_s(T)` зростає на `~6%` на кожен градус Цельсія, локальне нагрівання штучно занижує виміряну відносну вологість:
   ```
   RH_measured = RH_real · (P_s(T_real) / P_s(T_local))
   ```
   Для запобігання цій пастці слід застосовувати імпульсний режим живлення сенсора із вимкненням аналогового тракту між циклами вимірювання.
4. **Фільтрація та придушення шумів:** Через конвекційні турбулентні пульсації повітря миттєве значення вологості коливається. Рекомендується застосовувати цифровий експоненціальний ковзний усереднювач (EMA): `RH_filtered = α · RH_new + (1 - α) · RH_prev` з коефіцієнтом сгладжування `α = 0.05 - 0.1`.
5. **Обробка виключень та RAII у C++17:** У реалізації C++ замість повернення кодових помилок у вигляді вихідного параметра застосовано тип `std::expected<PsychrometricState, HumidityError>`. Це гарантує, що зумовлена помилка буде явно оброблена на етапі компіляції без виклику винятків `C++ exceptions`, що вкрай важливо для RTOS систем із суворими часовими рамками.
