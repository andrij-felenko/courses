# ⚙️ Алгоритми розрахунку вологості та точки роси

Ця вставка містить повноцінний практичний розбір та програмну реалізацію алгоритмів обчислення тиску насиченої водяної пари, відносної вологості за психрометричними даними та температури точки роси. Описаний код призначений для використання у вбудованих системах, автономних метеостанціях, промислових контролерах мікроклімату, системах опалення, вентиляції та кондиціювання (HVAC) і серверних системах моніторингу центрів обробки даних (ЦОД).

## 1. Математичні та фізичні засади алгоритмів

Програмування термодинамічних розрахунків параметрів вологого повітря спирається на три послідовні математичні блоки:

1. **Обчислення тиску насичення водяної пари `e_s(T)`** за формулою Августа-Рош-Магнуса:
   ```
   e_s(T) = 6.112 · exp( (17.67 · T) / (243.5 + T) )
   ```
2. **Розрахунок відносної вологості `RH` за показами психрометра**:
   ```
   e = e_s(T_w) - 0.000662 · p · (T_dry - T_wet)
   RH = (e / e_s(T_dry)) · 100%
   ```
3. **Обчислення температури точки роси `T_d(T, RH)`**:
   ```
   γ(T, RH) = ln(RH / 100) + (17.67 · T) / (243.5 + T)
   T_d = (243.5 · γ) / (17.67 - γ)
   ```

### Порівняльний аналіз математичних наближень
У метеорології та приладобудуванні використовуються кілька формул наближення тиску насичення. Вибір конкретного алгоритму залежить від обчислювальної потужності цільової платформи та вимог до точності:

- **Формула Августа-Рош-Магнуса (1871/1966)**: забезпечує абсолютну похибку менше `0.1%` у діапазоні від `-40 °C` до `+50 °C`. Завдяки простоті є стандартом для мікроконтролерних систем та вбудованих драйверів.
- **Рівняння Ардена Бака (Arden Buck, 1981)**: використовує складніший показник степеня й дає похибку менше `0.05%` у діапазоні від `-40 °C` до `+50 °C`, ураховуючи також залежність тиску насичення від атмосферного тиску (фактор підвищення тиску *enhancement factor*).
- **Рівняння Гоффа-Гретча (Goff-Gratch, 1946)**: фундаментальне стандартне рівняння Всесвітньої метеорологічної організації, що розгортає ряд логарифмічних та експоненційних доданків від точки потрійної рівноваги води. Вимагає значної кількості операцій із плаваючою комою подвійної точності (`double`).

---

## 2. Архітектура програмного модуля та обробка даних

У реальних промислових системах моніторингу середовища обчислювальний модуль вологості вбудовується в конвеєр обробки даних (*data pipeline*), який складається з чотирьох послідовних етапів:

1. **Збирання первинних даних з АЦП та первинне фільтрування**: зчитування сирих кодів температури та вологості з давачів через шину I2C або аналогові канали. На цьому етапі застосовується медіанний фільтр для видалення імпульсних завад від комутації силового обладнання.
2. **Температурна компенсація та лінеаризація**: перетворення сирих кодів АЦП у фізичні значення температури `T_dry` (°C) та вологості `RH` (%) за зашитими у пам'ять калібрувальними коефіцієнтами.
3. **Термодинамічний обчислювальний ядро**: виконання аналітичних формул для визначення парціального тиску водяної пари `e`, тиску насичення `e_s` та точки роси `T_d`.
4. **Перевірка аварійних порогів та виконавчі команди**: порівняння точки роси з температурою холодних поверхонь обладнання. Якщо `T_d` наближається до температури стінок шафи керування ближе ніж на 2 °C, модуль видає команду на вмикання дренажного осушувача або підігрівача для відвернення конденсації.

---

## 3. Покроковий розбір алгоритмічної логіки

Обчислювальний процес у програмному модулі будується за такою суворою послідовністю:

1. **Перевірка коректності вхідних даних (Sanity Check)**: 
   - Температура вологого термометра `T_wet` не може перевищувати температуру сухого термометра `T_dry` (фізично випаровування не може нагрівати ґніт вище навколишнього середовища).
   - Значення відносної вологості має лежати строго у межах `(0, 100%]`.
   - Атмосферний тиск має перебувати у фізично можливих межах (300…1200 гПа).
2. **Обчислення проміжних тисків насичення**:
   - Окремо обчислюється `e_s(T_wet)` для вологого термометра та `e_s(T_dry)` для сухого.
3. **Обчислення фактичного парціального тиску `e`**:
   - Застосовується психрометрична формула Августа з урахуванням атмосферного тиску.
4. **Обчислення точки роси**:
   - За допомогою логарифмування обчислюється безрозмірний коефіцієнт `γ(T, RH)`, з якого виражається температура `T_d`.

---

## 4. Багатомовна реалізація алгоритмів

Нижче наведено повністю ідіоматичні реалізації бібліотеки розрахунку параметрів вологості чотирма мовами програмування.

:::tabs
```cpp
#include <cmath>
#include <expected>
#include <iostream>
#include <format>
#include <algorithm>

namespace humidity {

// Константи алгоритму Магнуса та психрометрії
constexpr double MAGNUS_A = 6.112;    // гПа
constexpr double MAGNUS_B = 17.67;
constexpr double MAGNUS_C = 243.5;    // °C
constexpr double PSYCHRO_A = 0.000662; // К⁻¹

enum class CalculationError {
    InvalidTemperature,
    InvalidHumidity,
    InvalidPressure
};

// Обчислення тиску насиченої пари (гПа)
[[nodiscard]] constexpr double saturation_vapor_pressure(double temp_celsius) noexcept {
    return MAGNUS_A * std::exp((MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius));
}

// Розрахунок точки роси (°C) із перевіркою діапазонів входів
[[nodiscard]] std::expected<double, CalculationError> dew_point(double temp_celsius, double relative_humidity_pct) noexcept {
    if (relative_humidity_pct <= 0.0 || relative_humidity_pct > 100.0) {
        return std::unexpected(CalculationError::InvalidHumidity);
    }
    if (temp_celsius < -80.0 || temp_celsius > 85.0) {
        return std::unexpected(CalculationError::InvalidTemperature);
    }

    const double gamma = std::log(relative_humidity_pct / 100.0) + 
                         (MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius);
    
    return (MAGNUS_C * gamma) / (MAGNUS_B - gamma);
}

// Розрахунок відносної вологості за показами психрометра
[[nodiscard]] std::expected<double, CalculationError> relative_humidity_psychrometric(
    double t_dry, double t_wet, double pressure_hpa = 1013.25) noexcept {
    
    if (t_wet > t_dry) {
        return std::unexpected(CalculationError::InvalidTemperature);
    }
    if (pressure_hpa < 300.0 || pressure_hpa > 1200.0) {
        return std::unexpected(CalculationError::InvalidPressure);
    }

    const double e_s_wet = saturation_vapor_pressure(t_wet);
    const double e_s_dry = saturation_vapor_pressure(t_dry);
    const double actual_e = e_s_wet - PSYCHRO_A * pressure_hpa * (t_dry - t_wet);

    const double rh = (actual_e / e_s_dry) * 100.0;
    return std::clamp(rh, 0.0, 100.0);
}

} // namespace humidity

int main() {
    constexpr double t_dry = 25.0;
    constexpr double t_wet = 18.5;
    constexpr double pressure = 1013.25;

    const auto rh_res = humidity::relative_humidity_psychrometric(t_dry, t_wet, pressure);
    if (rh_res) {
        std::cout << std::format("Сухий: {:.1f}°C, Вологий: {:.1f}°C -> RH = {:.2f}%\n", 
                                 t_dry, t_wet, *rh_res);
        
        const auto td_res = humidity::dew_point(t_dry, *rh_res);
        if (td_res) {
            std::cout << std::format("Точка роси T_d = {:.2f}°C\n", *td_res);
        }
    }
    return 0;
}
```
```c
#include <stdio.h>
#include <math.h>

#define MAGNUS_A 6.112
#define MAGNUS_B 17.67
#define MAGNUS_C 243.5
#define PSYCHRO_A 0.000662

typedef struct {
    double relative_humidity_pct;
    double actual_vapor_pressure_hpa;
    double saturation_vapor_pressure_hpa;
    double dew_point_celsius;
} humidity_result_t;

// Обчислення тиску насиченої пари (гПа)
double calc_saturation_vapor_pressure(double temp_celsius) {
    return MAGNUS_A * exp((MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius));
}

// Розрахунок точки роси (°C)
double calc_dew_point(double temp_celsius, double rh_pct) {
    if (rh_pct <= 0.0) return -999.0;
    double gamma = log(rh_pct / 100.0) + (MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius);
    return (MAGNUS_C * gamma) / (MAGNUS_B - gamma);
}

// Повний психрометричний розрахунок
int calc_psychrometric_data(double t_dry, double t_wet, double pressure_hpa, humidity_result_t *out_res) {
    if (!out_res || t_wet > t_dry) return -1;

    double e_s_wet = calc_saturation_vapor_pressure(t_wet);
    double e_s_dry = calc_saturation_vapor_pressure(t_dry);
    double e_actual = e_s_wet - PSYCHRO_A * pressure_hpa * (t_dry - t_wet);

    double rh = (e_actual / e_s_dry) * 100.0;
    if (rh < 0.0) rh = 0.0;
    if (rh > 100.0) rh = 100.0;

    out_res->relative_humidity_pct = rh;
    out_res->actual_vapor_pressure_hpa = e_actual;
    out_res->saturation_vapor_pressure_hpa = e_s_dry;
    out_res->dew_point_celsius = calc_dew_point(t_dry, rh);

    return 0;
}

int main(void) {
    humidity_result_t res;
    double t_dry = 25.0;
    double t_wet = 18.5;
    double pressure = 1013.25;

    if (calc_psychrometric_data(t_dry, t_wet, pressure, &res) == 0) {
        printf("Психрометрія (C): T_dry = %.1f C, T_wet = %.1f C\n", t_dry, t_wet);
        printf("  RH = %.2f %%\n", res.relative_humidity_pct);
        printf("  e  = %.2f hPa (e_s = %.2f hPa)\n", res.actual_vapor_pressure_hpa, res.saturation_vapor_pressure_hpa);
        printf("  Td = %.2f C\n", res.dew_point_celsius);
    }
    return 0;
}
```
```py
import math
from typing import Tuple, Optional

MAGNUS_A = 6.112    # гПа
MAGNUS_B = 17.67
MAGNUS_C = 243.5    # °C
PSYCHRO_A = 0.000662 # К⁻¹

def saturation_vapor_pressure(temp_celsius: float) -> float:
    """Обчислення тиску насиченої водяної пари (гПа)."""
    return MAGNUS_A * math.exp((MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius))

def dew_point(temp_celsius: float, relative_humidity_pct: float) -> Optional[float]:
    """Обчислення температури точки роси (°C)."""
    if not (0.0 < relative_humidity_pct <= 100.0):
        return None
    gamma = math.log(relative_humidity_pct / 100.0) + (MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius)
    return (MAGNUS_C * gamma) / (MAGNUS_B - gamma)

def psychrometric_relative_humidity(t_dry: float, t_wet: float, pressure_hpa: float = 1013.25) -> Tuple[float, float]:
    """Обчислення відносної вологості (%) та точки роси (°C) за психрометром."""
    if t_wet > t_dry:
        raise ValueError("Температура вологого термометра не може бути вищою за сухий")
    
    e_s_wet = saturation_vapor_pressure(t_wet)
    e_s_dry = saturation_vapor_pressure(t_dry)
    actual_e = e_s_wet - PSYCHRO_A * pressure_hpa * (t_dry - t_wet)
    
    rh = max(0.0, min(100.0, (actual_e / e_s_dry) * 100.0))
    td = dew_point(t_dry, rh)
    return rh, td

if __name__ == "__main__":
    t_dry, t_wet, p = 25.0, 18.5, 1013.25
    rh, td = psychrometric_relative_humidity(t_dry, t_wet, p)
    print(f"Психрометрія (Python): T_dry={t_dry}°C, T_wet={t_wet}°C -> RH={rh:.2f}%, T_d={td:.2f}°C")
```
```ts
const MAGNUS_A = 6.112;
const MAGNUS_B = 17.67;
const MAGNUS_C = 243.5;
const PSYCHRO_A = 0.000662;

export interface HumidityMetrics {
    relativeHumidityPct: number;
    dewPointCelsius: number;
    actualVaporPressureHpa: number;
    saturationVaporPressureHpa: number;
}

export function saturationVaporPressure(tempCelsius: number): number {
    return MAGNUS_A * Math.exp((MAGNUS_B * tempCelsius) / (MAGNUS_C + tempCelsius));
}

export function dewPoint(tempCelsius: number, relativeHumidityPct: number): number | null {
    if (relativeHumidityPct <= 0 || relativeHumidityPct > 100) return null;
    const gamma = Math.log(relativeHumidityPct / 100) + (MAGNUS_B * tempCelsius) / (MAGNUS_C + tempCelsius);
    return (MAGNUS_C * gamma) / (MAGNUS_B - gamma);
}

export function calculatePsychrometrics(tDry: number, tWet: number, pressureHpa: number = 1013.25): HumidityMetrics {
    if (tWet > tDry) throw new Error("tWet cannot exceed tDry");
    
    const eSWet = saturationVaporPressure(tWet);
    const eSDry = saturationVaporPressure(tDry);
    const actualE = eSWet - PSYCHRO_A * pressureHpa * (tDry - tWet);
    
    const rh = Math.min(100, Math.max(0, (actualE / eSDry) * 100));
    const td = dewPoint(tDry, rh) ?? 0;
    
    return {
        relativeHumidityPct: rh,
        dewPointCelsius: td,
        actualVaporPressureHpa: actualE,
        saturationVaporPressureHpa: eSDry
    };
}

// Приклад виклику
const res = calculatePsychrometrics(25.0, 18.5, 1013.25);
console.log(`TS Result: RH=${res.relativeHumidityPct.toFixed(2)}%, Td=${res.dewPointCelsius.toFixed(2)}°C`);
```
:::

---

## 5. Оптимізація для вбудованих систем (MCU) та крайові випадки

При розробці високопродуктивного ПЗ для вбудованих мікроконтролерів (AVR, STM32, ESP32) слід ураховувати такі обчислювальні нюанси та граничні умови:

### 1. Апроксимація через Look-Up Tables (LUT)
Обчислення натуральних логарифмів `ln()` та експонент `exp()` на 8-бітних МК без математичного співпроцесора (FPU) вимагає виконання сотень тактів через бібліотеки емуляції плаваючої коми. Для запобігання перевантаженню процесора застосовують такі рішення:
- У пам'ять ПЗП (Flash) зашивають розраховану таблицю тисків насичення з кроком в `1 °C` від `-40 °C` до `+60 °C`. Значення між вузлами таблиці обчислюються за допомогою швидкої лінійної або кубічної сплайн-інтерполяції.
- Апроксимація логарифма поліномом Тейлора або алгоритмом CORDIC.

### 2. Захист від від'ємних температур та криги
При температурах нижче `0 °C` поверхня ґнота психрометра може вкритися льодом. Оскільки тиск насиченої пари над льодом `e_s,ice` є нижчим, ніж над переохолодженою водою `e_s,water`, недотримання цього фактора викликає систематичну похибку вимірювань до `10…15%`. Алгоритм має автоматично перемикати коефіцієнти Магнуса на `b_ice = 22.587`, `c_ice = 273.86` при фіксації замерзання ґнота.

### 3. Тестування та граничні випадки (Unit Testing)
Під час розробки модулів розрахунку вологості обов'язково покривають модуль модульними тестами для таких критичних умов:
- **`RH = 100%`**: точка роси `T_d` має бути з точністю до `0.01 °C` рівною температурі повітря `T`.
- **`T_dry = T_wet`**: відносна вологість має дорівнювати строго `100%`.
- **Екстремальний тиск (високогір'я)**: перевірка роботи психрометричного модуля при тиску `p = 600` гПа (на висоті 4000 м).

### 4. Питома точність плаваючої коми IEEE 754
Для медичних та метрологічних обчислень рекомендується використовувати тип `double` (64-бітне значення IEEE 754 з 53-бітною мантисою). Використання single-precision `float` (32-бітне значення з 24-бітною мантисою) призводить до втрати точності під час обчислення різниці `T_dry - T_wet`, якщо ця різниця є малою (< 0.2 °C), що дає накопичену похибку визначення відносної вологості до ±1.2% RH.
