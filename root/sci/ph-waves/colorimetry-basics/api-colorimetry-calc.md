# 📋 Інтерфейс та структура даних колориметричного обчислювача

Програмний інтерфейс (API) та структури даних бібліотеки обчислення колориметричних параметрів призначені для оптичних вимірювальних систем, спектрометрів, вимірювальних стендів та модулів аналізу джерел освітлення. Інтерфейс забезпечує повний цикл обробки дискретних спектрів випромінювання: від завантаження та первинної валідації масивів довжин хвиль до числового інтегрування із функціями чутливості спостерігача CIE 1931, розрахунку тристимульних значень `XYZ`, координат хроматичності `(x, y)` та `(u', v')`, корельованої колірної температури (CCT), відхилення `Duv` та індексу кольоропередачі CRI (`R[a]` та `R[9]`).

## 1. Концепція архітектури та вимоги до пам'яті

Програмний інтерфейс розроблений із урахуванням використання у двох різнородних обчислювальних середовищах:
- **Низькорівневий C-інтерфейс (`c_colorimetry.h`):** Призначений для вбудованих систем (embedded system), мікроконтролерів із підтримкою FPU (наприклад, ARM Cortex-M4F/M7, ESP32, STM32H7), а також для створення зв'язувальних обгорток (bindings) у мовах Python, C#, Rust. Інтерфейс не здійснює жодних прихованих виділень динамічної пам'яті (`malloc`). Усі робочі структури та масиви передаються за указниками, що гарантує детермінований час виконання та відсутність фрагментації купи.
- **Високорівневий C++20 інтерфейс (`cpp_colorimetry.hpp`):** Призначений для прикладного програмного забезпечення на настільних ПК, науково-дослідних стендах та серверах обробки вимірювальних даних. Використовує семантику переміщення, контейнери `std::vector`, `std::array`, перегляди `std::span` та механізм обробки помилок `std::expected` без генерації винятків (exceptions).

При використанні C-інтерфейсу на мікроконтролерах без блоку обчислень із плаваючою комою подвійної точності (FP64) тип `double` може бути перевизначений через препроцесорний макрос `#define COLORIMETRY_USE_FLOAT` на `float` (FP32), що забезпечує апаратне прискорення інтегрування на FPU Cortex-M4.

## 2. Повний опис структур даних

Для точного представлення дискретного спектрального розподілу потужності (SPD) та збереження обчислених колориметричних параметрів використовуються набір строго визначених структур.

:::tabs
```c
/* c_colorimetry.h - Повний C-інтерфейс колориметричного модуля */
#ifndef C_COLORIMETRY_H
#define C_COLORIMETRY_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#define COLORIMETRY_SPECTRUM_MIN_WL  380
#define COLORIMETRY_SPECTRUM_MAX_WL  780
#define COLORIMETRY_CRI_SAMPLE_COUNT 15

/* Перелік кодів помилок для C API */
typedef enum {
    COLORIMETRY_OK                  =  0, /* Успішне виконання обчислення */
    COLORIMETRY_ERR_NULL_PTR        = -1, /* Передано нульовий указник */
    COLORIMETRY_ERR_INVALID_WL      = -2, /* Діапазон довжин хвиль не покриває 380..780 нм */
    COLORIMETRY_ERR_INVALID_STEP    = -3, /* Непідтримуваний крок сітки (дозволено 1 або 5 нм) */
    COLORIMETRY_ERR_ZERO_INTEGRAL   = -4, /* Сума тристимульних значень дорівнює нулю */
    COLORIMETRY_ERR_OUT_OF_RANGE    = -5  /* Значення CCT виходить за межі 1000K..25000K */
} colorimetry_error_t;

/* Дискретний спектральний розподіл потужності (SPD) */
typedef struct {
    uint16_t start_wavelength_nm; /* Початкова довжина хвилі (зазвичай 380 нм) */
    uint16_t step_wavelength_nm;  /* Крок дискретизації сітки (1 нм або 5 нм) */
    size_t   count;               /* Кількість дискретних відліків у масиві */
    const double* power_values;   /* Масив спектральної густини потужності (Вт/(м²·нм)) */
} spectral_data_t;

/* Тристимульний вектор CIE 1931 XYZ */
typedef struct {
    double X; /* Червона уявна складова (абсолютна або відносна) */
    double Y; /* Фотометрична яскравість у кд/м² (або відносний світловий потік) */
    double Z; /* Синя уявна складова */
} tristimulus_xyz_t;

/* Двовимірні координати хроматичності */
typedef struct {
    double x;       /* Координата x стандарту CIE 1931 */
    double y;       /* Координата y стандарту CIE 1931 */
    double u_prime; /* Рівномірна координата u' стандарту CIE 1976 UCS */
    double v_prime; /* Рівномірна координата v' стандарту CIE 1976 UCS */
} chromaticity_coords_t;

/* Результат обчислення корельованої колірної температури */
typedef struct {
    double cct_kelvin; /* Обчислена колірна температура у Кельвінах */
    double duv;        /* Ортогональне відхилення від лінії чорного тіла */
    bool   is_valid;   /* Прапорець достовірності обчислення */
} cct_result_t;

/* Результати обчислення індексу кольоропередачі CRI */
typedef struct {
    double R_a; /* Загальний індекс кольоропередачі (середнє R1..R8) */
    double R_i[COLORIMETRY_CRI_SAMPLE_COUNT]; /* Окремі індекси R1..R15 */
    double R_9; /* Спеціальний індекс для насиченого червоного колірного зразка */
} cri_result_t;

#endif /* C_COLORIMETRY_H */
```
```cpp
// cpp_colorimetry.hpp - Об'єктно-орієнтований C++20 інтерфейс
#ifndef CPP_COLORIMETRY_HPP
#define CPP_COLORIMETRY_HPP

#include <vector>
#include <array>
#include <span>
#include <expected>
#include <cstdint>
#include <string_view>

namespace colorimetry {

constexpr uint16_t MinWavelengthNm = 380;
constexpr uint16_t MaxWavelengthNm = 780;
constexpr size_t   CriSampleCount  = 15;

enum class ErrorCode : int32_t {
    NullPointer       = -1,
    InvalidWavelength = -2,
    InvalidStep       = -3,
    ZeroIntegral      = -4,
    OutOfRange        = -5
};

struct SpectralData {
    uint16_t start_wavelength_nm{380};
    uint16_t step_wavelength_nm{5};
    std::vector<double> power_values{};

    [[nodiscard]] bool is_valid() const noexcept {
        if (power_values.empty() || (step_wavelength_nm != 1 && step_wavelength_nm != 5)) {
            return false;
        }
        const auto end_wl = start_wavelength_nm + (power_values.size() - 1) * step_wavelength_nm;
        return start_wavelength_nm <= MinWavelengthNm && end_wl >= MaxWavelengthNm;
    }
};

struct TristimulusXYZ {
    double X{0.0};
    double Y{0.0};
    double Z{0.0};
};

struct ChromaticityCoords {
    double x{0.0};
    double y{0.0};
    double u_prime{0.0};
    double v_prime{0.0};
};

struct CCTResult {
    double cct_kelvin{0.0};
    double duv{0.0};
    bool   is_valid{false};
};

struct CRIResult {
    double R_a{0.0};
    std::array<double, CriSampleCount> R_i{};
    double R_9{0.0};
};

} // namespace colorimetry

#endif // CPP_COLORIMETRY_HPP
```
:::

## 3. Детальний опис функцій та алгоритмічні контракти

Кожна функція модуля реалізує чітко визначений крок обчислювального конвеєра. Нижче деталізовано правила їх використання, інваріанти та можливі виняткові ситуації.

### 3.1 Обчислення тристимульних значень `XYZ`

Функція виконує чисельне інтегрування дискретного спектра `S(λ)` із кривими чутливості спостерігача CIE 1931 `x̄(λ)`, `ȳ(λ)`, `z̄(λ)`.

:::tabs
```c
/**
 * @brief Обчислює тристимульні значення XYZ за дискретним спектром випромінювання.
 * 
 * Функція перевіряє цілісність масиву spectrum, завантажує внутрішні таблиці
 * функцій чутливості CIE 1931 та виконує інтегрування методом трапецій.
 * 
 * @param[in]  spectrum Указник на валідну структуру спектральних даних.
 * @param[out] out_xyz  Указник на об'єкт для збереження тристимульних значень.
 * @return COLORIMETRY_OK при успіху або відповідний код помилки.
 */
colorimetry_error_t colorimetry_compute_xyz(
    const spectral_data_t* spectrum,
    tristimulus_xyz_t*      out_xyz
);
```
```cpp
/**
 * @brief Обчислює тристимульні значення XYZ за дискретним спектром.
 * 
 * @param spectrum Валідний об'єкт спектральних даних.
 * @return std::expected з TristimulusXYZ або кодом помилки ErrorCode.
 */
[[nodiscard]] std::expected<TristimulusXYZ, ErrorCode> compute_xyz(
    const SpectralData& spectrum
) noexcept;
```
:::

- **Алгоритмічний інваріант:** Інтегрування проводиться строго у межах довжин хвиль від 380 нм до 780 нм. Якщо спектр вимірювача має ширший діапазон (наприклад, 350..1050 нм), значення поза межами 380..780 нм ігноруються.
- **Обробка помилок:** Якщо указник `spectrum` дорівнює `NULL`, повертається `COLORIMETRY_ERR_NULL_PTR`. Якщо початкова довжина хвилі більша за 380 нм або кінцева менша за 780 нм, повертається `COLORIMETRY_ERR_INVALID_WL`.

### 3.2 Перетворення до координат хроматичності

Функція здійснює нормувальну проекцію тривимірного вектора `XYZ` на двовимірну хроматичну площину `x, y` та обчислює рівномірні координати `u', v'`.

:::tabs
```c
/**
 * @brief Розраховує 2D-координати хроматичності x, y (CIE 1931) та u', v' (CIE 1976 UCS).
 * 
 * @param[in]  xyz        Указник на вихідний вектор XYZ.
 * @param[out] out_chroma Указник на об'єкт для збереження координат.
 * @return COLORIMETRY_OK при успіху або COLORIMETRY_ERR_ZERO_INTEGRAL, якщо X+Y+Z == 0.
 */
colorimetry_error_t colorimetry_compute_chromaticity(
    const tristimulus_xyz_t* xyz,
    chromaticity_coords_t*   out_chroma
);
```
```cpp
/**
 * @brief Розраховує 2D-координати хроматичності x, y та u', v'.
 * 
 * @param xyz Вхідний тристимульний вектор XYZ.
 * @return std::expected з ChromaticityCoords або ErrorCode.
 */
[[nodiscard]] std::expected<ChromaticityCoords, ErrorCode> compute_chromaticity(
    const TristimulusXYZ& xyz
) noexcept;
```
:::

- **Формули розрахунку:**
  ```
  x = X / (X + Y + Z)
  y = Y / (X + Y + Z)
  u' = 4X / (X + 15Y + 3Z) = 4x / (-2x + 12y + 3)
  v' = 9Y / (X + 15Y + 3Z) = 9y / (-2x + 12y + 3)
  ```
- **Захист від ділення на нуль:** Якщо сума `X + Y + Z < 1e-12` (темновий сигнал або абсолютна темрява), розрахунок зупиняється з кодом `COLORIMETRY_ERR_ZERO_INTEGRAL`.

### 3.3 Обчислення CCT та відхилення Duv

Функція визначає корельовану колірну температуру в Кельвінах та перпендикулярне відхилення від планківського локусу.

:::tabs
```c
/**
 * @brief Обчислює корельовану колірну температуру (CCT) та відхилення Duv.
 * 
 * Використовує поєднання поліноміальної формули МакКамі для швидкої первинної оцінки
 * та чисельний метод Охно для знаходження точної проекції на лінію чорного тіла.
 * 
 * @param[in]  chroma  Указник на координати хроматичності.
 * @param[out] out_cct Указник на результат CCT.
 * @return COLORIMETRY_OK при успіху або COLORIMETRY_ERR_OUT_OF_RANGE.
 */
colorimetry_error_t colorimetry_compute_cct(
    const chromaticity_coords_t* chroma,
    cct_result_t*                out_cct
);
```
```cpp
/**
 * @brief Обчислює корельовану колірну температуру (CCT) та відхилення Duv.
 * 
 * @param chroma Координати хроматичності x, y, u', v'.
 * @return std::expected з CCTResult або ErrorCode.
 */
[[nodiscard]] std::expected<CCTResult, ErrorCode> compute_cct(
    const ChromaticityCoords& chroma
) noexcept;
```
:::

- **Межі достовірності:** Алгоритм вважає результати валідними (`is_valid = true`) для колірних температур у діапазоні від 1000 K до 25000 K та при відхиленні `|Duv| ≤ 0.05`. При більших відхиленнях джерело світла є надто кольоровим (наприклад, зелений або червоний LED), і поняття колірної температури втрачає фізичний сенс.

### 3.4 Обчислення індексу кольоропередачі CRI (Ra, R9)

Функція синтезує спектр порівняльного еталонного джерела `S_r(λ)` за значенням CCT та розраховує хроматичні зміщення для 15 стандартних колірних зразків.

:::tabs
```c
/**
 * @brief Розраховує загальний індекс кольоропередачі R_a та спеціальні індекси R1..R15.
 * 
 * @param[in]  spectrum Указник на спектр випробовуваного джерела.
 * @param[in]  cct_info Попередньо обчислені дані CCT та Duv.
 * @param[out] out_cri  Указник на структуру для збереження результатів CRI.
 * @return COLORIMETRY_OK при успіху або відповідний код помилки.
 */
colorimetry_error_t colorimetry_compute_cri(
    const spectral_data_t* spectrum,
    const cct_result_t*    cct_info,
    cri_result_t*          out_cri
);
```
```cpp
/**
 * @brief Розраховує індекси кольоропередачі R_a та R1..R15.
 * 
 * @param spectrum Спектр джерела світла.
 * @param cct_info Дані колірної температури CCT.
 * @return std::expected з CRIResult або ErrorCode.
 */
[[nodiscard]] std::expected<CRIResult, ErrorCode> compute_cri(
    const SpectralData& spectrum,
    const CCTResult&    cct_info
) noexcept;
```
:::

- **Вибір еталонного джерела:**
  - Якщо `CCT < 5000 K`: Використовується планківський спектр випромінювання чорного тіла при температурі `T = CCT`.
  - Якщо `CCT ≥ 5000 K`: Використовується математична модель стандартного фазового денного світла CIE (CIE Daylight Illuminant Series D) при даній температурі.
- **Обчислення зразків:** Здійснюється розрахунок векторів у просторі CIE 1964 `W*U*V*`, виконання адаптаційного зміщення за фон Крізом (von Kries chromatic adaptation transform) та обчислення евклідової відстані `ΔE[i]` для кожного зразка. `R[a]` обчислюється як середнє арифметичне значень `R1`..`R8`.

## 4. Інтерполяція спектрів та обробка нерегулярних сіток

У реальних спектрометрах із Лінійними фотодіодними масивами (Linear CCD/CMOS Array) оптичні довжини хвиль окремих пікселів не лежать на регулярній сітці з кроком 1 нм або 5 нм. Фотодіоди мають нелінійну калібрувальну дисперсійну криву, описувану поліномом третього степеня:

```
λ(i) = a₀ + a₁ · i + a₂ · i² + a₃ · i³
```

Перед передачею сирих спектральних даних у колориметричний модуль бібліотека виконує попередню сплайн-інтерполяцію або лінійну інтерполяцію на стандартну сітку з кроком `Δλ = 1 нм` або `5 нм`.

Лінійна інтерполяція між двома сусідніми пікселями `(λ_k, S_k)` та `(λ_{k+1}, S_{k+1})` здійснюється за формулою:

```
S(λ) = S_k + (S_{k+1} - S_k) · ((λ - λ_k) / (λ_{k+1} - λ_k))
```

Це дозволяє використовувати швидке табличне сумування без обчислення трансендентних функцій під час інтегрування.

## 5. Потокобезпечність, прискорення SIMD та інтеграція

1. **Безстатусна реалізація (Reentrancy and Thread Safety):** Усі функції бібліотеки є строго безстатусними (pure, stateless functions). Вони не містять глобальних змінних, які б модифікувалися під час виконання, і не використовують статичні буфери. Це дозволяє безпечно викликати обчислювальні функції паралельно з кількох потоків обробки без додаткового застосування м'ютексів чи критичних секцій.
2. **Нерухомі таблиці даних (ROM Compatibility):** Табульовані масиви спектрів `CIE 1931 2° CMF` та спектральних відбиттів `TCS01..TCS15` оголошені як `static const` та розміщуються в сегменті постійної пам'яті (Flash/ROM), що важливо для контролерів із обмеженим обсягом оперативної пам'яті (RAM).
3. **SIMD / NEON Прискорення:** На процесорах ARM Cortex-A (Raspberry Pi, промислові контролери) інтегрування масивів `S(λ) · x̄(λ)` прискорюється за допомогою 128-бітних інструкцій NEON (використання `vmlaq_f32` для паралельного перемножування 4 точок спектра за один такт процесора).
