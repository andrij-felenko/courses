# 📋 Архітектура та API солуера SYK

Ця вставка містить повну специфікацію програмного інтерфейсу (API), архітектурний опис та інженерний опис бібліотеки високоефективного чисельного розв'язання рівнянь Швінгера-Дайсона та точної діагоналізації моделі Зачдева-Є-Кітаєва (SYK).

Бібліотека розроблена для наукових досліджень не-Фермі-рідкого стану у фізиці конденсованого стану, обчислення термодинамічних функцій Гріна у частотному просторі Мацубари, розрахунку ферміонної самоенергії, оцінки квантового показника Ляпунова та залишкової термодинамічної ентропії основного стану.

## 1. Загальна архітектура та вибір проектних рішень

Програмний комплекс солуера SYK побудовано за модульним принципом із чітким розділенням обчислювального ядра, модулів швидкого перетворення Фур'є (FFT) та зовнішніх зв'язуючих інтерфейсів для мов C та C++.

Основним завданням архітектури є забезпечення максимальної числової стійкості при розв'язанні нелінійних інтегро-диференціальних рівнянь у режимі низьких температур (при `β J ≫ 1`), де традиційні ітераційні схеми піддаються сильним паразитивним осциляціям.

### Модульна структура бібліотеки:

1. **Обчислювальний модуль `SD_Solver` (Schwinger-Dyson Engine):**
   Виконує ітераційний розв'язок самоузгодженої системи рівнянь Швінгера-Дайсона. Модуль керує перетворенням полів між евклідовим часовим простором `τ ∈ [0, β]` та дискретними частотами Мацубари `ω_n = (2n + 1)·π / β`. Для запобігання чисельній розбіжності застосовується метод демпфованої релаксації з адаптивним вибором параметра змішування `α`.

2. **Модуль точної діагоналізації `ED_Solver` (Exact Diagonalization Engine):**
   Відповідає за побудову матриці Гамільтоніана для системи `N` Майоранівських ферміонів у квантовому Гільбертовому просторі розмірності `2^(N/2) × 2^(N/2)`. Побудова здійснюється шляхом перетворення Йордана-Віґнера через тензорні добутки спінових матрицій Паулі.

3. **Аналітичний модуль `Chaos_Analyzer`:**
   Призначений для чисельного розрахунку чотириточкових кореляційних функцій, нечасововпорядкованих кореляторів (OTOC) `⟨A(t)B(0)A(t)B(0)⟩`, оцінки квантового показника Ляпунова `λ_L` та розрахунку спектрального формаційного фактора `K(t)`.

## 2. Детальний опис конфігураційних параметрів

Налаштування усіх параметрів чисельного експерименту здійснюється через уніфіковану структуру `SYKSolverConfig`. Усі значення передаються за допомогою вказівника у низькорівневому C API або через об'єкт у C++ API.

### Повний опис полів конфігурації:

- **Кількість ферміонів `N_fermions`:** Повна кількість Майоранівських ферміонів у системі. Повинна бути парним додатним числом (`N = 4, 6, 8, ...`). Для солуера Швінгера-Дайсона параметр `N` використовується для нормування термодинамічних величин та залишкової ентропії `S₀`, тоді як для точної діагоналізації `N` визначає розмірність Гільбертового простору `2^(N/2)`.
- **Порядковість взаємодії `q_body`:** Кількість ферміонів у базі випадкової чотиричастинкової взаємодії. За замовчуванням дорівнює `4`.
- **Обернена температура `beta`:** Величина `β = 1 / (k_B T)` у безрозмірних одиницях `1/J`. Значення `β = 10.0 ... 100.0` відповідають глибокому конформному інфрачервоному режиму.
- **Константа зв'язку `J_coupling`:** Енергетичний масштаб середньоквадратичної взаємодії `J`, що задає дисперсію випадкових гаусових зв'язків.
- **Розмірність сітки `grid_points`:** Кількість дискретних точок сітки Мацубари `M`. Повинна бути строго ступенем двійки (`M = 2^k`, наприклад 512, 1024, 2048, 4096, 8192), що є необхідною умовою для забезпечення максимальної обчислювальної швидкодії алгоритмів швидкого перетворення Фур'є (FFT).
- **Коефіцієнт демпфування `mix_alpha`:** Безрозмірний коефіцієнт демпфування релаксації `α ∈ (0, 1)`. Рекомендовані значення варіюються від `0.01` для наднизьких температур (`β J > 100`) до `0.3` для високотемпературного режиму (`β J < 5`). Малі значення `α` уповільнюють збіжність, але повністю усувають нестійкість розв'язку.
- **Поріг збіжності `tolerance`:** Поріг зупинки ітерацій за максимальним абсолютним відхиленням функцій Гріна між сусідніми кроками.
- **Лиміт ітерацій `max_iters`:** Гранична кількість ітераційних кроків до припинення розрахунку з генерацією помилки.

## 3. Специфікація інтерфейсу API (C та C++)

Для забезпечення гнучкості розробки надається низькорівневий C API із процедурним стилем та непрозорими вказівниками, а також об'єктно-орієнтований C++17 API із підтримкою RAII, винятків та контейнерів `std::vector`.

:::tabs
```c
/* C API специфікація заголовного файлу syk_solver.h */
#include <complex.h>
#include <stdint.h>

typedef enum {
    SYK_SUCCESS = 0,                  /* Успішне виконання операції */
    SYK_ERROR_INVALID_PARAM = -1,     /* Некоректні параметри конфігурації */
    SYK_ERROR_OUT_OF_MEMORY = -2,     /* Недостатньо оперативної пам'яті */
    SYK_ERROR_CONVERGENCE_FAILED = -3,/* Не вдалося досягти збіжності */
    SYK_ERROR_NULL_POINTER = -4       /* Передано нульовий вказівник */
} syk_status_t;

typedef struct {
    uint32_t N_fermions;
    uint32_t q_body;
    double beta;
    double J_coupling;
    uint32_t grid_points;
    double mix_alpha;
    double tolerance;
    uint32_t max_iters;
} SYKSolverConfig;

typedef struct syk_solver_handle_t syk_solver_handle_t;

syk_status_t syk_solver_create(const SYKSolverConfig* config, syk_solver_handle_t** handle_out);
syk_status_t syk_solver_run(syk_solver_handle_t* handle);
syk_status_t syk_solver_get_g_tau(const syk_solver_handle_t* handle, double* out_tau_grid, double* out_g_tau);
syk_status_t syk_solver_get_sigma_omega(const syk_solver_handle_t* handle, double complex* out_sigma_omega);
void syk_solver_destroy(syk_solver_handle_t* handle);
```
```cpp
// C++17 API специфікація заголовного файлу syk_solver.hpp
#pragma once
#include <vector>
#include <complex>
#include <memory>
#include <string>
#include <stdexcept>

namespace syk {

enum class ErrorCode {
    InvalidParam,
    OutOfMemory,
    ConvergenceFailed,
    NullPointer
};

class SolverException : public std::runtime_error {
public:
    explicit SolverException(ErrorCode code, const std::string& msg)
        : std::runtime_error(msg), m_code(code) {}

    [[nodiscard]] ErrorCode code() const noexcept { return m_code; }

private:
    ErrorCode m_code;
};

struct SYKSolverConfig {
    std::size_t N_fermions{16};
    std::size_t q_body{4};
    double beta{10.0};
    double J_coupling{1.0};
    std::size_t grid_points{1024};
    double mix_alpha{0.1};
    double tolerance{1e-8};
    std::size_t max_iters{1000};
};

class SYKSolver {
public:
    explicit SYKSolver(const SYKSolverConfig& config);
    ~SYKSolver() noexcept;

    SYKSolver(const SYKSolver&) = delete;
    SYKSolver& operator=(const SYKSolver&) = delete;

    SYKSolver(SYKSolver&&) noexcept;
    SYKSolver& operator=(SYKSolver&&) noexcept;

    std::size_t solve();

    [[nodiscard]] const std::vector<double>& g_tau() const noexcept;
    [[nodiscard]] const std::vector<std::complex<double>>& g_omega() const noexcept;
    [[nodiscard]] const std::vector<std::complex<double>>& sigma_omega() const noexcept;

    [[nodiscard]] double compute_residual_entropy() const;

private:
    struct Impl;
    std::unique_ptr<Impl> m_impl;
};

} // namespace syk
```
:::

## 4. Механізми виділення пам'яті, ниткобезпечність та інтеграція

Солуер SYK оптимізований для використання у багатониточних обчислювальних середовищах із виділенням пам'яті на вирівняних межах (aligned memory allocation):

### Управління оперативною пам'яттю:
1. **Вирівнювання масивів:** Усі масиви функцій Гріна `G_omega` та `Sigma_omega` виділяються з вирівнюванням на 64-байтні межі (наприклад через `posix_memalign` або `_mm_malloc`), що дозволяє компілятору задіяти векторні інструкції AVX-512 та FMA для швидкого обчислення комплексних добутків.
2. **Ниткобезпечність (Thread Safety):** Екземпляри `syk_solver_handle_t` та `syk::SYKSolver` є повністю ізольованими у пам'яті й не використовують глобального стану. Це дозволяє паралельно запускати тисячі солуерів у різних нитках OpenMP чи `std::thread` для проведення параметричного сканування по температурі `T`.
3. **Інтеграція з бібліотекою FFTW3:** У внутрішній реалізації перетворення Фур'є між уявним часом та частотою використовується бібіліотека FFTW3 у режимі `FFTW_MEASURE` із збереженням обчислених планів (FFTW plans) усередині структури дескриптора.

## 5. Механізми логування, діагностики та обробки крайових випадків

Для забезпечення надійності при масовому параметричному скануванні у бібліотеці передбачено систему логування та обробку виняткових крайових станів:

- **Діагностика некоректних частотних хвостів:** При розрахунку на сітках із недостатньою кількістю точок `M < 256` високі частоти Мацубари не встигають вийти на асимптотичний режим `1 / (i·ω_n)`. У такому разі модуль логування видає попередження та пропонує збільшити `grid_points`.
- **Автоматична адаптація релаксації:** Якщо у процесі розрахунку зміна норми відхилення `max |G_{k+1} - G_k|` починає зростати протягом трьох послідовних ітерацій, солуер автоматично зменшує коефіцієнт демпфування вдвічі (`α = α / 2`) та продовжує ітераційний процес без зупинки.
- **Експорт у наукові формати даних:** Обчислені функції Гріна та спектральні функції можуть бути записані у файли формату HDF5 або CSV для подальшої візуалізації у середовищах Python (Matplotlib), Julia або ROOT.

## 6. Детальні приклади використання C та C++ API

Приклад показує створення конфігурації, ініціалізацію солуера, виконання обчислювального циклу та зчитування функцій Гріна з виведенням у стандартний потік:

:::tabs
```c
/* Повний приклад використання C API */
#include <stdio.h>
#include <stdlib.h>
#include "syk_solver.h"

int main(void) {
    SYKSolverConfig cfg = {
        .N_fermions = 16,
        .q_body = 4,
        .beta = 20.0,
        .J_coupling = 1.0,
        .grid_points = 512,
        .mix_alpha = 0.15,
        .tolerance = 1e-7,
        .max_iters = 500
    };

    syk_solver_handle_t* solver = NULL;
    syk_status_t st = syk_solver_create(&cfg, &solver);
    if (st != SYK_SUCCESS) {
        fprintf(stderr, "Помилка створення солуера: %d\n", st);
        return 1;
    }

    printf("Запуск ітераційного солуера SYK на C API...\n");
    st = syk_solver_run(solver);
    if (st == SYK_SUCCESS) {
        printf("Солуер успішно досяг збіжності!\n");

        double* tau_grid = (double*)malloc(sizeof(double) * cfg.grid_points);
        double* g_tau = (double*)malloc(sizeof(double) * cfg.grid_points);

        syk_solver_get_g_tau(solver, tau_grid, g_tau);
        printf("G(tau = beta/2) = %.8f\n", g_tau[cfg.grid_points / 2]);

        free(tau_grid);
        free(g_tau);
    } else {
        fprintf(stderr, "Помилка обчислення: не досягнуто збіжності!\n");
    }

    syk_solver_destroy(solver);
    return 0;
}
```
```cpp
// Повний приклад використання C++17 API
#include <iostream>
#include <iomanip>
#include "syk_solver.hpp"

int main() {
    try {
        syk::SYKSolverConfig cfg;
        cfg.beta = 20.0;
        cfg.grid_points = 512;
        cfg.mix_alpha = 0.15;
        cfg.tolerance = 1e-7;

        std::cout << "Запуск ітераційного солуера SYK на C++17 API...\n";
        syk::SYKSolver solver(cfg);
        
        std::size_t iters = solver.solve();
        std::cout << "Солуер успішно збігся за " << iters << " ітерацій!\n";

        const auto& g_tau = solver.g_tau();
        std::cout << std::fixed << std::setprecision(8);
        std::cout << "Значення G(tau = beta/2) = " << g_tau[cfg.grid_points / 2] << "\n";
        std::cout << "Залишкова ентропія S0/N = " << solver.compute_residual_entropy() << "\n";

    } catch (const syk::SolverException& e) {
        std::cerr << "Помилка виконання солуера: " << e.what() 
                  << " (Код помилки: " << static_cast<int>(e.code()) << ")\n";
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Стандартний виняток: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

Ця архітектура дає змогу легко інтегрувати солуер SYK у високопродуктивні обчислювальні комплекси для фізичного моделювання квантових масивів та голографічних чорних дір.
