# 📡 Довідник інтерфейсу API обчислення випромінювання

Цей документ містить повний референс програмного інтерфейсу (API) обчислювальної бібліотеки `libblackbody`, призначеної для розрахунку спектральних та інтегральних характеристик випромінювання абсолютно чорного тіла у наукових та інженерних додатках. Інтерфейс надає як низькорівневі C-функції для системного та вбудованого програмування, так і сучасну обгортку C++20 із підтримкою обробки помилок через `std::expected` та обчисленнями `constexpr`.

## Архітектурний огляд бібліотеки та дизайн інтерфейсу

Бібліотека `libblackbody` спроектована відповідно до принципів низьких накладних витрат та максимальної обчислювальної стійкості. Основні обчислювальні процедури оперують величинами в міжнародній системі одиниць SI: довжини хвиль задаються в метрах, температура — у Кельвінах, спектральна яскравість — у ватах на квадратний метр на стерадіан на метр `Вт / (м² · ст · м)`, а повна випромінювальна здатність — у ватах на квадратний метр `Вт / м²`.

При розробці високозавантажених оптичних симуляторів, тепловізійних систем та супутникових спектрометрів ключовою вимогою є відсутність побічних ефектів та повна потокобезпечність. Усі функції бібліотеки є чистими функціями без глобального стану (stateless), що дозволяє викликати їх паралельно з багатьох обчислювальних потоків OpenMP або std::jthread без блокувань та мутексів.

Низькорівневий інтерфейс розроблений з дотриманням стандарту C99, що забезпечує пряму сумісність з найпростішими мікроконтролерами без операційної системи. Обгортка C++20 надає виражений типбезпечний API з використанням новітніх можливостей стандарту, таких як `std::expected` та `std::span`.

## Заголовочні файли та типи даних

Для використання бібліотеки системний програміст підключає заголовочний файл `blackbody_radiation.h` для мови C або `blackbody.hpp` для мови C++. Коди помилок представлені у вигляді переліку `bb_status_t` у C та строго типізованого `enum class Status` у C++.

:::tabs
```c
#ifndef BLACKBODY_RADIATION_H
#define BLACKBODY_RADIATION_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Статуси виконання обчислювальних операцій */
typedef enum {
    BB_SUCCESS = 0,
    BB_ERROR_INVALID_TEMP = -1,
    BB_ERROR_INVALID_WAVELENGTH = -2,
    BB_ERROR_INVALID_RANGE = -3,
    BB_ERROR_OVERFLOW = -4,
    BB_ERROR_INTEGRATION_FAILED = -5
} bb_status_t;

#ifdef __cplusplus
}
#endif

#endif /* BLACKBODY_RADIATION_H */
```
```cpp
#ifndef BLACKBODY_HPP
#define BLACKBODY_HPP

#include <cstddef>
#include <expected>
#include <span>
#include <string_view>

namespace blackbody {

/* Статуси виконання обчислювальних операцій C++20 */
enum class Status {
    Success = 0,
    InvalidTemperature = -1,
    InvalidWavelength = -2,
    InvalidRange = -3,
    Overflow = -4,
    IntegrationFailed = -5
};

} // namespace blackbody

#endif // BLACKBODY_HPP
```
:::

---

## Конфігураційні структури та параметри варіювання

Для гнучкого налаштування чисельних методів та передачі фундаментальних фізичних констант використовуються спеціалізовані структури даних. Передача налаштувань через структури дозволяє розширювати інтерфейс бібліотеки у майбутніх версіях без порушення бінарної сумісності ABI (Application Binary Interface).

Ключовим елементом конфігурації інтегрування є вибір між класичним квадратурним методом Сімпсона та адаптивним методом Гаусса-Лежандра. Метод Гаусса-Лежандра рекомендується для високоточних лабораторних обчислень, оскільки він забезпечує експоненційну швидкість збіжності для гладких функцій Планка.

Структура `bb_band_result_t` акумулює не лише обчислену інтегральну яскравість та випромінювальну здатність, але й повертає оцінку похибки квадратури `estimated_error`, що дозволяє автоматично контролювати точність розрахунків під час виконання програм.

Обчислювальне ядро бібліотеки оптимізоване для роботи у реальному часі в системах керування оптичним обладнанням та пірометрами.

:::tabs
```c
/* Структура фізичних констант CODATA 2018 */
typedef struct {
    double h;     /* Стала Планка (Дж·с) */
    double c;     /* Швидкість світла (м/с) */
    double k_b;   /* Стала Больцмана (Дж/К) */
    double sigma; /* Стала Стефана-Больцмана (Вт/(м²·К⁴)) */
    double b_wien;/* Стала зміщення Віна (м·К) */
} bb_constants_t;

/* Налаштування чисельного інтегрування */
typedef struct {
    size_t max_subintervals; /* Максимальна кількість підінтервалів */
    double rel_tolerance;    /* Відносна допустима похибка (наприклад, 1e-8) */
    double abs_tolerance;    /* Абсолютна допустима похибка */
    bool use_gauss_legendre; /* true: Гаусс-Лежандр, false: Сімпсон */
} bb_integration_config_t;

/* Результат обчислення спектрального діапазону */
typedef struct {
    double integrated_radiance; /* Інтегральна яскравість (Вт/(м²·ст)) */
    double integrated_emittance;/* Повна випромінювальна здатність (Вт/м²) */
    double peak_wavelength;     /* Довжина хвилі максимуму (м) */
    double estimated_error;     /* Оцінка похибки чисельного інтегрування */
} bb_band_result_t;
```
```cpp
namespace blackbody {

/* Структура фізичних констант C++20 з constexpr значеннями */
struct Constants {
    static constexpr double h = 6.62607015e-34;
    static constexpr double c = 2.99792458e8;
    static constexpr double k_b = 1.380649e-23;
    static constexpr double sigma = 5.670374e-8;
    static constexpr double b_wien = 2.897771955e-3;
};

/* Налаштування чисельного інтегрування C++20 */
struct IntegrationConfig {
    std::size_t max_subintervals{5000};
    double rel_tolerance{1.0e-8};
    double abs_tolerance{1.0e-12};
    bool use_gauss_legendre{true};
};

/* Результат обчислення спектрального діапазону C++20 */
struct BandResult {
    double integrated_radiance{0.0};
    double integrated_emittance{0.0};
    double peak_wavelength{0.0};
    double estimated_error{0.0};
};

} // namespace blackbody
```
:::

---

## Сигнатури обчислювальних функцій та механізм обробки помилок

Функції API реалізують строгий контроль вхідних аргументів перед виконанням обчислень. Якщо вказано нефізичне значення температури (`T <= 0.0`) або від'ємну довжину хвилі (`λ <= 0.0`), функція негайно повертає відповідний код помилки, не виконуючи небезпечних операцій ділення на нуль або обчислення логарифмів від від'ємних чисел.

У C++20 інтерфейсі використання типом повернення `std::expected<T, Status>` змушує компілятор перевіряти наявність результату до доступу до значення, що унеможливлює помилки розіменування нульових вказівників або невизначену поведінку (undefined behavior).

Функція `bb_wien_peak` знаходить довжину хвилі максимуму випромінювання на основі аналітичного розв'язку трансцендентного рівняння закону Віна, повертаючи значення `λ_max = b / T`.

Функція `bb_energy_density` обчислює об'ємну спектральну густину енергії `u_λ(λ, T) = (4π / c) · B_λ(λ, T)` у вакуумній порожнині при заданій температурі.

:::tabs
```c
/* 
 * Обчислення точкової спектральної яскравості B_λ(λ, T)
 * λ_meters — довжина хвилі в метрах
 * temp_kelvin — температура в Кельвінах
 * out_radiance — вказівник на змінну для запису результату (Вт/(м²·ст·м))
 */
bb_status_t bb_spectral_radiance(double lambda_meters, double temp_kelvin, double *out_radiance);

/* 
 * Обчислення спектральної густини енергії в об'ємі u_λ(λ, T)
 */
bb_status_t bb_energy_density(double lambda_meters, double temp_kelvin, double *out_density);

/* 
 * Пошук довжини хвилі максимуму (Закон зміщення Віна)
 */
bb_status_t bb_wien_peak(double temp_kelvin, double *out_lambda_max);

/* 
 * Комплексне інтегрування спектра у діапазоні [lambda_min, lambda_max]
 */
bb_status_t bb_integrate_band(
    double temp_kelvin,
    double lambda_min,
    double lambda_max,
    const bb_integration_config_t *config,
    bb_band_result_t *out_result
);
```
```cpp
namespace blackbody {

/* 
 * Точкова спектральна яскравість B_λ(λ, T) у C++20
 */
[[nodiscard]] constexpr std::expected<double, Status> spectral_radiance(
    double lambda_meters, double temp_kelvin) noexcept;

/* 
 * Об'ємна спектральна густина енергії u_λ(λ, T)
 */
[[nodiscard]] constexpr std::expected<double, Status> energy_density(
    double lambda_meters, double temp_kelvin) noexcept;

/* 
 * Довжина хвилі максимуму випромінювання (Закон Віна)
 */
[[nodiscard]] constexpr std::expected<double, Status> wien_peak(
    double temp_kelvin) noexcept;

/* 
 * Комплексне інтегрування спектра у діапазоні
 */
[[nodiscard]] std::expected<BandResult, Status> integrate_band(
    double temp_kelvin,
    double lambda_min,
    double lambda_max,
    const IntegrationConfig& config = {}) noexcept;

} // namespace blackbody
```
:::

---

## Таблиця обмежень та граничних умов

Нижче наведено допустимі діапазони значень вхідних параметрів та специфікацію поведінки ядра при виході за їхні межі:

| Параметр | Одиниця вимірювання | Мінімальне значення | Максимальне значення | Поведінка при порушенні |
| :--- | :--- | :--- | :--- | :--- |
| `temp_kelvin` | Кельвін (K) | `> 0.0` (напр. `1.0e-6`) | `1.0e9` | Повертає `BB_ERROR_INVALID_TEMP` |
| `lambda_meters` | Метр (м) | `> 0.0` (напр. `1.0e-12`) | `1.0` | Повертає `BB_ERROR_INVALID_WAVELENGTH` |
| `lambda_min` | Метр (м) | `> 0.0` | `< lambda_max` | Повертає `BB_ERROR_INVALID_RANGE` |
| `x = h c / λ k T` | Безрозмірний | `0.0` | `700.0` | При `x > 700.0` повертає `0.0` (Overflow guard) |

---

## Приклад використання API в інженерних проектах

Нижче наведено повні робочі приклади інтеграції обчислювального модуля у консольний C-додаток та C++20 додаток для розрахунку сонячного випромінювання у видимому діапазоні спектра.

У прикладах виконується розрахунок точкової яскравості на довжині хвилі 500 нм, обчислюється пікова довжина хвилі Віна та виконується чисельне інтегрування випромінювальної здатності в діапазоні видимого світла від 380 нм до 780 нм.

:::tabs
```c
#include <stdio.h>
#include "blackbody_radiation.h"

int main(void) {
    double T = 5778.0; /* Ефективна температура Сонця */
    double radiance = 0.0;
    double lambda_peak = 0.0;

    /* Обчислення яскравості на довжині хвилі 500 нм */
    bb_status_t status = bb_spectral_radiance(500.0e-9, T, &radiance);
    if (status != BB_SUCCESS) {
        printf("Помилка обчислення: %d\n", status);
        return 1;
    }

    bb_wien_peak(T, &lambda_peak);
    printf("Спектральна яскравість на 500 нм: %.3e Вт/(м²·ст·м)\n", radiance);
    printf("Пік випромінювання Віна:          %.2f нм\n", lambda_peak * 1.0e9);

    /* Інтегрування у видимому діапазоні (380 - 780 нм) */
    bb_integration_config_t cfg = {
        .max_subintervals = 2000,
        .rel_tolerance = 1.0e-6,
        .abs_tolerance = 1.0e-10,
        .use_gauss_legendre = true
    };
    bb_band_result_t res;
    if (bb_integrate_band(T, 380.0e-9, 780.0e-9, &cfg, &res) == BB_SUCCESS) {
        printf("Потужність у видимому спектрі:   %.2f Вт/м²\n", res.integrated_emittance);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include "blackbody.hpp"

int main() {
    constexpr double temp_sun = 5778.0;

    // Обчислення яскравості C++20
    auto rad_res = blackbody::spectral_radiance(500.0e-9, temp_sun);
    if (!rad_res) {
        std::cerr << "Помилка обчислення: " << static_cast<int>(rad_res.error()) << '\n';
        return 1;
    }

    auto peak_res = blackbody::wien_peak(temp_sun);
    std::cout << std::scientific << std::setprecision(3);
    std::cout << "Спектральна яскравість на 500 нм: " << *rad_res << " Вт/(м²·ст·м)\n";
    if (peak_res) {
        std::cout << "Пік випромінювання Віна:          " << (*peak_res * 1.0e9) << " нм\n";
    }

    // Інтегрування у видимому діапазоні
    blackbody::IntegrationConfig cfg{.max_subintervals = 2000, .use_gauss_legendre = true};
    auto band_res = blackbody::integrate_band(temp_sun, 380.0e-9, 780.0e-9, cfg);
    if (band_res) {
        std::cout << "Потужність у видимому спектрі:   " << band_res->integrated_emittance << " Вт/м²\n";
    }

    return 0;
}
```
:::

## Детальний аналіз продуктивності, потокобезпечності та виділення пам'яті

При практичній реалізації високонавантажених обчислень (наприклад, у супутникових геоінформаційних системах аналізу температурних карт поверхні Землі) важливим фактором є відсутність виділення динамічної пам'яті (`malloc` / `new`) у гарячому циклі обчислень.

1. **Відсутність динамічної пам'яті:**
   Усі точкові функції `bb_spectral_radiance` та `blackbody::spectral_radiance` виконуються виключно на стеку процесора без виклику системних менеджерів пам'яті. Це гарантує детермінований час виконання кожної ітерації порядку 5–10 наносекунд на сучасних процесорах x86_64.

2. **SIMD векторизація:**
   Для обробки масивів довжин хвиль (спектрів з тисячами точок) рекомендується передавати послідовні буфери пам'яті. Компілятори C та C++ (GCC, Clang, MSVC) за наявності прапорів оптимізації `-O3 -march=native` автоматично векторизують обчислення `expm1(x)` за допомогою векторних інструкцій AVX2 / AVX-512, збільшуючи обчислювальну продуктивність у 4–8 разів.

3. **Сумісність ABI між мовами:**
   Завдяки дотриманню C-сумісного ABI бінарна бібліотека `libblackbody.so` або `blackbody.dll` може бути безпосередньо підключена до проєктів мовами Python (через `ctypes` або `cffi`), Rust (через `bindgen`), C# (через `P/Invoke`) та Fortran без написання проміжних обгорток.

4. **Тестування та верифікація:**
   Модульні тести (unit tests) перевіряють збіжність інтеграла по всьому спектру `[0..∞]` зі значенням закону Стефана-Больцмана `σ T⁴`. При використанні конфігурації з 5000 підінтервалами відносне відхилення чисельного інтеграла від теорії становить не більше `10⁻⁸`, що задовольняє найстрогішим метрологічним стандартам.

5. **Обробка винятків та крайових випадків у вбудованих системах:**
   Для застосування в бортових обчислювачах та мікроконтролерах із суворими вимогами до безпеки (стандарти MISRA C та ISO 26262) C-інтерфейс бібліотеки свідомо відмовляється від використання механізму `setjmp`/`longjmp` та C++ винятків (exceptions), обмежуючись строгою перевіркою кодів повернення `bb_status_t`.
