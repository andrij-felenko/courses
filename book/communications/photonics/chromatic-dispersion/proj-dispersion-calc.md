# ⚙️ Калькулятор бюджету хроматичної дисперсії та розрахунок модуля DCF

Ця практична програмерська вставка надає готову інженерную бібліотеку мовами C та C++ для розрахунку накопиченої хроматичної дисперсії оптичних ліній, оцінки часового розплаву імпульсів, визначення максимальної дальності безкомпенсаційного прогону, вибору довжини компенсаційних модулів DCF, а також реалізації алгоритму цифрової компенсації у DSP.

### Архітектура обчислювального модуля та системний контракт

У практичній розробці оптичного телекомунікаційного обладнання (прошивки трансиверів, оптичні монітори систем управління NMS/EMS, утиліти проектування волоконних ліній) обчислювальний модуль дисперсійного бюджету повинен забезпечувати точне моделювання фізичного тракту без високих обчислювальних накладних витрат.

Системний модуль вирішує чотири основні інженерні задачі розрахунку траси:
1. **Обчислення коефіцієнта `D(λ)`:** використання емпіричної формули ITU-T G.652 для визначення коефіцієнта дисперсії на довільній робочій довжині хвилі `λ` за значеною нульовою точкою `λ₀` та нахилом `S₀`.
2. **Оцінка розширення імпульсу `Δt`:** розрахунок абсолютного часового розмиття імпульсу на виході траси з урахуванням спектральної ширини лазера та довжини лінки.
3. **Розрахунок межі дальності `L_max`:** визначення максимальної відстані без компенсації для заданої бітової швидкості (NRZ чи RZ).
4. **Підбір параметра DCF:** обчислення необхідної довжини катушки DCF для нейтралізації накопиченої додатньої дисперсії траси та розрахунок залишкової дисперсії.

### Математичний контракт формули ITU-T G.652

Згідно зі стандартом ITU-T G.652, залежність коефіцієнта хроматичної дисперсії `D` від довжини хвилі `λ` (в нанометрах) описується емпіричним виразом другого порядку через довжину хвилі нульової дисперсії `λ₀` (зазвичай 1312 нм) та нахил нульової дисперсії `S₀` (зазвичай 0.090…0.092 пс/(нм²·км)):

```text
D(λ) = (S₀ / 4) · [ λ − (λ₀⁴ / λ³) ]
```

Ця формула є точним аналітичним наближенням сумарної матеріальної й хвилеводної дисперсії у робочих вікнах 1310 нм (O-band) та 1550 нм (C-band). Для робочої довжини хвилі `λ = 1550 нм` формула дає коефіцієнт `D = +17.01 пс/(нм·км)`.

### Алгоритм цифрової рівності (DSP FIR Equalizer)

У сучасних цифрових сигнальних процесорах (DSP) когерентних трансиверів 100G/400G цифрова компенсація хроматичної дисперсії реалізується у частотній області за допомогою алгоритму Overlap-Save з використанням швидкого перетворення Фур'є (FFT).

Передавальна функція волоконного тракту довжиною `L` з дисперсією `β₂` виражається фазовим множником:

```text
H_CD(ω) = exp(− i · (β₂ / 2) · ω² · L)
```

Для компенсації накопиченої дисперсії DSP застосовує обратну комплексну передавальну функцію `H_EQ(ω) = H_CD⁻¹(ω)`:

```text
H_EQ(ω) = exp(+ i · (β₂ / 2) · ω² · L)
```

Коефіцієнти цифрового FIR-фільтра `h[n]` обчислюються шляхом зворотного перетворення Фур'є від `H_EQ(ω)`. Кількість тактів (тапів) FIR-фільтра `N_taps` прямо пропорційна накопиченій дисперсії `D_accum`:

```text
N_taps ≈ (2 · π · c / λ²) · |D_accum| · B_s²
```

де `B_s` — символьна швидкість (baud rate). Для каналу 100G QPSK (32 Гбод) на трасі 1000 км (`D_accum = 17 000 пс/нм`) цифровий фільтр вимагає близько 256–512 комплексних тапів.

### Програмна реалізація у прошивці та високорівневому ПЗ

При побудові телекомунікаційного програмного забезпечення розрізняють два середовища виконання:
- **Низькорівнева прошивка трансивера (Firmware):** код повинен виконуватися за строго детермінований час без динамічного виділення пам'яті у купі (`heap`). Модуль на C99 задовольняє вимогам стандарту MISRA C та використовує передачу результатів через покажчики на вихідні структури `LinkDispersionResult`.
- **Високорівневі NMS/EMS системи управління мережею (Control Plane):** системи розрахунку трас та планування DWDM мереж вимагають строгого дотримання безпеки типів та безисключительной обробки помилок. Модуль на C++20 використовує обгортку `std::expected`, яка дозволяє повернути статус помилки `CalculationError` без використання механізму exceptions, що забезпечує високу продуктивність та сумісність із високозавантаженими серверами управління.

### Послідовність виклику інженерних функцій

При обробці траси програма виконує наступну послідовність кроків:
1. Завантаження або ініціалізація профілю волокна (`FiberParams` у C або `FiberProfile` у C++).
2. Обчислення точного коефіцієнта дисперсії `D(λ)` для вибраної довжини хвилі генерації лазера.
3. Розрахунок загальної накопиченої дисперсії `D_accum` та прогнозованого часового розширення оптичного імпульсу `Δt`.
4. Порівняння результату із граничною терпимістю трансивера (`max_allowed_dispersion_ps_nm`).
5. Якщо ліміт перевищено, обчислення необхідного модуля пасивної компенсації `L_dcf` або розрахунок кількості тапів FIR-фільтра цифрового DSP процесора.

### Реалізація інженерної бібліотеки (C та C++)

Нижче наведено повний робочий код бібліотеки двома мовами: C (чистий процедурний C99) та C++ (сучасний ідіоматичний C++20).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

// Параметри оптичного волокна
typedef struct {
    double zero_disp_wavelength_nm; // Точка нульової дисперсії λ₀ (напр. 1310.0 нм)
    double zero_disp_slope;         // Нахил дисперсії S₀ (напр. 0.092 пс/(нм²·км))
    double attenuation_db_km;       // Загасання α (напр. 0.20 дБ/км)
} FiberParams;

// Результати розрахунку траси
typedef struct {
    double dispersion_coeff;        // Коефіцієнт D(λ), пс/(нм·км)
    double accumulated_dispersion;  // Загальна накопичена дисперсія, пс/нм
    double pulse_broadening_ps;     // Часове розширення імпульсу Δt, пс
    double max_uncompensated_km;    // Максимальна дальність без компенсації, км
    bool dispersion_limit_exceeded; // Прапорець перевищення бюджету
} LinkDispersionResult;

// Емпіричний розрахунок D(λ) за стандартом ITU-T G.652
double calc_fiber_dispersion(const FiberParams* fiber, double wavelength_nm) {
    if (!fiber || wavelength_nm <= 0.0) return 0.0;
    
    double lambda0 = fiber->zero_disp_wavelength_nm;
    double s0 = fiber->zero_disp_slope;
    
    // Формула G.652: D(λ) = (S₀ / 4) * (λ - λ₀⁴ / λ³)
    double lambda_ratio = pow(lambda0, 4.0) / pow(wavelength_nm, 3.0);
    return (s0 / 4.0) * (wavelength_nm - lambda_ratio);
}

// Розрахунок аналізу дисперсійного бюджету траси
bool analyze_link_dispersion(const FiberParams* fiber,
                            double wavelength_nm,
                            double link_length_km,
                            double spectral_width_nm,
                            double bit_rate_gbps,
                            double max_allowed_dispersion_ps_nm,
                            LinkDispersionResult* out_result) {
    if (!fiber || !out_result || link_length_km <= 0.0) {
        return false;
    }

    double d_coeff = calc_fiber_dispersion(fiber, wavelength_nm);
    double accum_disp = d_coeff * link_length_km;
    
    // Часове розширення імпульсу Δt = |D| * Δλ * L
    double broadening_ps = fabs(d_coeff) * spectral_width_nm * link_length_km;
    
    // Оцінка граничної дальності за критерієм B² * |D| * L <= 104000 (для 1550 нм)
    // Або через затримку 25% від тривалості біта T_bit = 1000 / bit_rate_gbps
    double bit_period_ps = 1000.0 / bit_rate_gbps;
    double max_allowed_broadening_ps = 0.25 * bit_period_ps;
    
    double max_len_km = 0.0;
    if (fabs(d_coeff) > 1e-6 && spectral_width_nm > 1e-6) {
        max_len_km = max_allowed_broadening_ps / (fabs(d_coeff) * spectral_width_nm);
    }
    
    out_result->dispersion_coeff = d_coeff;
    out_result->accumulated_dispersion = accum_disp;
    out_result->pulse_broadening_ps = broadening_ps;
    out_result->max_uncompensated_km = max_len_km;
    out_result->dispersion_limit_exceeded = (fabs(accum_disp) > max_allowed_dispersion_ps_nm);

    return true;
}

// Розрахунок потрібної довжини волокна DCF для компенсації
double calc_dcf_required_length(double accum_disp_ps_nm, double dcf_disp_coeff_ps_nm_km) {
    if (fabs(dcf_disp_coeff_ps_nm_km) < 1e-6) return 0.0;
    // L_dcf = - D_accum / D_dcf
    return -accum_disp_ps_nm / dcf_disp_coeff_ps_nm_km;
}

int main(void) {
    // Стандартні параметри волокна SMF-28 (G.652.D)
    FiberParams smf28 = {
        .zero_disp_wavelength_nm = 1312.0,
        .zero_disp_slope = 0.090,
        .attenuation_db_km = 0.20
    };

    double wavelength = 1550.0;     // 1550 нм (C-band)
    double link_len = 80.0;         // 80 км траса
    double laser_linewidth = 0.1;   // DFB-лазер Δλ = 0.1 нм
    double bit_rate = 10.0;         // 10 Гбіт/с
    double sfp_max_cd = 800.0;      // Ліміт SFP+ ER = 800 пс/нм

    LinkDispersionResult res;
    if (analyze_link_dispersion(&smf28, wavelength, link_len, laser_linewidth, 
                                bit_rate, sfp_max_cd, &res)) {
        printf("=== Аналіз оптичної траси %.1f км (1550 нм) ===\n", link_len);
        printf("Коефіцієнт D(λ):          %.2f пс/(нм·км)\n", res.dispersion_coeff);
        printf("Накопичена дисперсія:     %.1f пс/нм\n", res.accumulated_dispersion);
        printf("Розширення імпульсу Δt:  %.2f пс\n", res.pulse_broadening_ps);
        printf("Макс. безкомпенс. дальність: %.1f км\n", res.max_uncompensated_km);
        printf("Перевищення бюджету CD:   %s\n", res.dispersion_limit_exceeded ? "ТАК (ПОТРІБНА КОМПЕНСАЦІЯ)" : "НІ");

        if (res.dispersion_limit_exceeded) {
            double dcf_coeff = -100.0; // Модуль DCF з D = -100 пс/(нм·км)
            double dcf_len = calc_dcf_required_length(res.accumulated_dispersion, dcf_coeff);
            printf("Необхідна довжина DCF:    %.2f км (при D_dcf = %.1f)\n", dcf_len, dcf_coeff);
        }
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <expected>
#include <string_view>
#include <format>

namespace optical_network {

enum class CalculationError {
    InvalidWavelength,
    InvalidLength,
    ZeroDispersionCoefficients
};

struct FiberProfile {
    std::string_view name{"Generic SMF"};
    double zero_disp_wavelength_nm{1312.0};
    double zero_disp_slope{0.090};
    double attenuation_db_km{0.20};
};

struct LinkAnalysis {
    double dispersion_coeff_ps_nm_km{0.0};
    double accumulated_dispersion_ps_nm{0.0};
    double pulse_broadening_ps{0.0};
    double max_reach_km{0.0};
    bool requires_compensation{false};
};

class DispersionCalculator {
public:
    // Обчислення коефіцієнта D(λ) за формулою G.652
    [[nodiscard]] static constexpr double calculate_d(const FiberProfile& fiber, double wavelength_nm) noexcept {
        const double l0 = fiber.zero_disp_wavelength_nm;
        const double s0 = fiber.zero_disp_slope;
        const double l0_4_over_l3 = std::pow(l0, 4.0) / std::pow(wavelength_nm, 3.0);
        return (s0 / 4.0) * (wavelength_nm - l0_4_over_l3);
    }

    // Повний аналіз лінки
    [[nodiscard]] static std::expected<LinkAnalysis, CalculationError> analyze(
        const FiberProfile& fiber,
        double wavelength_nm,
        double link_length_km,
        double spectral_width_nm,
        double bit_rate_gbps,
        double max_cd_tolerance_ps_nm) noexcept 
    {
        if (wavelength_nm <= 0.0) return std::unexpected(CalculationError::InvalidWavelength);
        if (link_length_km <= 0.0) return std::unexpected(CalculationError::InvalidLength);

        const double d_coeff = calculate_d(fiber, wavelength_nm);
        const double accum_cd = d_coeff * link_length_km;
        const double broadening = std::abs(d_coeff) * spectral_width_nm * link_length_km;

        const double bit_period_ps = 1000.0 / bit_rate_gbps;
        const double max_allowed_broadening = 0.25 * bit_period_ps;

        double max_reach = 0.0;
        if (std::abs(d_coeff) > 1e-6 && spectral_width_nm > 1e-6) {
            max_reach = max_allowed_broadening / (std::abs(d_coeff) * spectral_width_nm);
        }

        return LinkAnalysis{
            .dispersion_coeff_ps_nm_km = d_coeff,
            .accumulated_dispersion_ps_nm = accum_cd,
            .pulse_broadening_ps = broadening,
            .max_reach_km = max_reach,
            .requires_compensation = (std::abs(accum_cd) > max_cd_tolerance_ps_nm)
        };
    }

    // Розрахунок довжини модуля DCF
    [[nodiscard]] static constexpr double calculate_dcf_length(double accum_cd_ps_nm, double dcf_d_coeff) noexcept {
        if (std::abs(dcf_d_coeff) < 1e-6) return 0.0;
        return -accum_cd_ps_nm / dcf_d_coeff;
    }
};

} // namespace optical_network

int main() {
    using namespace optical_network;

    constexpr FiberProfile smf28{
        .name = "Corning SMF-28e+",
        .zero_disp_wavelength_nm = 1312.0,
        .zero_disp_slope = 0.090,
        .attenuation_db_km = 0.19
    };

    constexpr double wavelength_nm = 1550.0;
    constexpr double length_km = 100.0;
    constexpr double spectral_width_nm = 0.1;
    constexpr double bit_rate_gbps = 10.0;
    constexpr double max_cd_tolerance = 800.0;

    auto result = DispersionCalculator::analyze(smf28, wavelength_nm, length_km, 
                                                 spectral_width_nm, bit_rate_gbps, max_cd_tolerance);

    if (result) {
        std::cout << std::format("=== Аналіз лінії {} (Довжина {} км) ===\n", smf28.name, length_km);
        std::cout << std::format("Коефіцієнт D(λ):          {:.2f} пс/(нм·км)\n", result->dispersion_coeff_ps_nm_km);
        std::cout << std::format("Накопичена дисперсія:     {:.1f} пс/нм\n", result->accumulated_dispersion_ps_nm);
        std::cout << std::format("Розширення імпульсу Δt:  {:.2f} пс\n", result->pulse_broadening_ps);
        std::cout << std::format("Максимальна досяжність:  {:.1f} км\n", result->max_reach_km);
        std::cout << std::format("Статус компенсації:      {}\n", 
                                 result->requires_compensation ? "ПОТРІБЕН МОДУЛЬ DCF" : "У МЕЖАХ ДОПУСКУ");

        if (result->requires_compensation) {
            constexpr double dcf_d = -120.0;
            double dcf_len = DispersionCalculator::calculate_dcf_length(result->accumulated_dispersion_ps_nm, dcf_d);
            std::cout << std::format("Необхідна катушка DCF:    {:.2f} км (при D = {:.1f} пс/(нм·км))\n", dcf_len, dcf_d);
        }
    } else {
        std::cerr << "Помилка розрахунку оптичної лінії!\n";
    }

    return 0;
}
```
:::

### Тестування та верифікація граничних випадків

При розробці автоматизованих тестових сюїтів для перевірки обчислювального модуля рекомендується покривати наступні граничні випадки:
1. **Робота точно на довжині хвилі нульової дисперсії (`λ = λ₀ = 1312 нм`):** Коефіцієнт `D(λ)` мусить бути строго рівним `0.00 пс/(нм·км)`, а накопичена дисперсія — `0.0 пс/нм`.
2. **Вхідні дані з нульовою довжиною хвилі або від'ємною довжиною траси:** Модуль C повертає `false`, а модуль C++20 повертає помилку через статус `std::unexpected(CalculationError::InvalidWavelength)`.
3. **Розрахунок для довжин хвиль у S-діапазоні (1460 нм) та L-діапазоні (1625 нм):** Модуль коректно перераховує зміну нахилу дисперсії `S(λ)`, гарантуючи точність аналізу для широких спектральних DWDM ліній.
4. **Валідація коректності компенсації DCF:** Сума `accumulated_dispersion + (dcf_len * dcf_d_coeff)` мусить дорівнювати нулю із точністю до floating-point похибки `1e-9`.
5. **Інтеграційне моніторингове тестування:** Модуль тестується на сумісність із потоковими логами telemetry sysfs у Linux для автоматичного регулювання коефіцієнтів компенсації адаптивних DSP.
