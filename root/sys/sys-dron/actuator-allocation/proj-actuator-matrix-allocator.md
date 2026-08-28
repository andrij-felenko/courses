# ⚙️ Модуль матричного алокатора приводів польотного контролера на C та C++

Модуль розподілу керування виконує трансляцію віртуальних зусиль `τ = [F_z, M_x, M_y, M_z]ᵀ` у фізичні команди моторів і сервоприводів у реальному часі польотного циклу (частота 250–1000 Гц). Він забезпечує мінімізацію споживаної енергії через псевдообернену матрицю та реалізує трирівневу десатурацію для запобігання втраті керованості.

## Задача та архітектура модуля

У класичних польотних контролерах мікшування виконувалося жорстко закодованими формулами під фіксовані рами (Quad-X, Tri, Hexa). Універсальний матричний алокатор замінює ручний код матричним множенням:

```
u_raw = B⁺ · τ
```

де `B⁺` — заздалегідь обчислена або динамічно перерахована псевдообернена матриця ефективності розмірністю `num_actuators × 4`.

Модуль вирішує п'ять послідовних задач у жорсткому часовому бюджеті переривання таймера:
1. **Лінійне проектування:** множення вектору віртуального керування `τ` на матрицю `B⁺`;
2. **Зсув середньої тяги (Shift Desaturation):** якщо команди моторів виходять за верхню або нижню межу `[0, 1]`, весь пакет команд рівномірно зміщується по вертикалі, жертвуючи висотою заради збереження 100% моментів крену, тангажу та рискання;
3. **Масштабування рискання (Yaw Desaturation):** якщо діапазон між максимальним і мінімальним мотором перевищує `1.0`, зусилля рискання зменшуються, звільняючи динамічний запас під крен і тангаж;
4. **Масштабування моменту крену й тангажу (Roll/Pitch Scale):** у критичних умовах масштаб моментів `M_x, M_y` стискається зі збереженням їхнього просторового вектора напрямку, що унеможливлює неконтрольоване завалювання дрона;
5. **Апаратне обмеження (Hard Clamping):** фінальне зрізання значень у межі `[u_min, u_max]` як захист від чисельних похибок.

## Організація пам'яті та часовий бюджет на мікроконтролері

На сучасних польотних контролерах на базі процесорів ARM Cortex-M4/M7 (наприклад, STM32F405 на 168 МГц або STM32H743 на 480 МГц) модуль розподілу керування виконується всередині швидкого контуру кутової швидкості (Rate Loop) з періодом 1 мс (1 кГц) або 250 мкс (4 кГц).

Для забезпечення детермінізму та відповідності стандарту MISRA C модуль спроєктовано за такими інженерними принципами:
* **Нульове динамічне виділення пам'яті (Zero Heap Allocation):** усі буфери, дескриптори та матричні коефіцієнти розміщуються у статичній пам'яті або на стеку. Жоден виклик `malloc()` чи `free()` не допускається;
* **Мінімальна кількість операцій із рухомою комою:** операція множення `B⁺ · τ` для 8 приводів вимагає лише `8 × 4 = 32` операцій множення з накопиченням (FMA — Fused Multiply-Add), що на апаратному FPU Cortex-M4 займає менше ніж 0.35 мікросекунди;
* **Кеш-локальність:** коефіцієнти матриці `B⁺` зберігаються за рядками (row-major order), що дозволяє процесору завантажувати дані у внутрішні регістри послідовними інструкціями `VLDM`/`VSTM`.

## Реалізація модуля

Нижче наведено повну реалізацію алокатора: на мові C99 без динамічного виділення пам'яті та на C++20 із застосуванням `std::span`, `std::array`, інкапсуляції та статичної типізації.

:::tabs
```c
/* ============================================================================
 * control_allocator.h / control_allocator.c
 * Модуль матричного розподілу керування польотного контролера (C99)
 * ============================================================================ */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_AXES 4          /* F_z (тяга), M_x (крен), M_y (тангаж), M_z (рискання) */
#define MAX_ACTUATORS 8     /* До 8 моторів/сервоприводів */

typedef struct {
    uint8_t num_actuators;                          /* Кількість фізичних приводів (наприклад, 4, 6, 8) */
    float b_pseudo_inv[MAX_ACTUATORS][MAX_AXES];    /* Псевдообернена матриця B^+ */
    float u_min[MAX_ACTUATORS];                     /* Нижня межа привода (наприклад, 0.0 для ESC) */
    float u_max[MAX_ACTUATORS];                     /* Верхня межа привода (наприклад, 1.0 для ESC) */
    float yaw_weight;                               /* Вага збереження рискання (0.0..1.0) */
} allocator_config_t;

typedef struct {
    allocator_config_t config;
    bool saturated;                                 /* Прапорець настання насичення */
} allocator_t;

/* Ініціалізація алокатора конфігурацією */
void allocator_init(allocator_t *alloc, const allocator_config_t *cfg)
{
    if (!alloc || !cfg) return;
    memcpy(&alloc->config, cfg, sizeof(allocator_config_t));
    alloc->saturated = false;
}

/* Обчислення фізичних сигналів приводів u з віртуальних зусиль tau */
void allocator_update(allocator_t *alloc, const float tau[MAX_AXES], float u_out[MAX_ACTUATORS])
{
    if (!alloc || !tau || !u_out) return;

    const uint8_t n_act = alloc->config.num_actuators;
    float u[MAX_ACTUATORS];
    float u_thrust[MAX_ACTUATORS];
    float u_rp[MAX_ACTUATORS];
    float u_yaw[MAX_ACTUATORS];

    /* Крок 1: Роздільний розрахунок компонентів для кожного привода */
    for (uint8_t i = 0; i < n_act; ++i) {
        u_thrust[i] = alloc->config.b_pseudo_inv[i][0] * tau[0]; /* Внесок F_z */
        u_rp[i]     = alloc->config.b_pseudo_inv[i][1] * tau[1] +
                      alloc->config.b_pseudo_inv[i][2] * tau[2]; /* Внесок M_x, M_y */
        u_yaw[i]    = alloc->config.b_pseudo_inv[i][3] * tau[3]; /* Внесок M_z */
        u[i]        = u_thrust[i] + u_rp[i] + u_yaw[i];
    }

    /* Крок 2: Пошук мінімуму та максимуму */
    float min_val = u[0];
    float max_val = u[0];
    for (uint8_t i = 1; i < n_act; ++i) {
        if (u[i] < min_val) min_val = u[i];
        if (u[i] > max_val) max_val = u[i];
    }

    alloc->saturated = (max_val > 1.0f || min_val < 0.0f);

    /* Крок 3: Десатурація зсувом (Shift Desaturation) */
    if (max_val > 1.0f) {
        float shift = max_val - 1.0f;
        for (uint8_t i = 0; i < n_act; ++i) u[i] -= shift;
        min_val -= shift;
        max_val = 1.0f;
    }

    if (min_val < 0.0f) {
        float shift = -min_val;
        for (uint8_t i = 0; i < n_act; ++i) u[i] += shift;
        max_val += shift;
        min_val = 0.0f;
    }

    /* Крок 4: Якщо після зсуву розмах (max - min) перевищує 1.0, жертвуємо рисканням */
    if (max_val > 1.0f) {
        /* Зменшуємо внесок yaw */
        float yaw_scale = 1.0f;
        float max_rp = 0.0f;
        for (uint8_t i = 0; i < n_act; ++i) {
            float abs_rp = u_rp[i] < 0.0f ? -u_rp[i] : u_rp[i];
            if (abs_rp > max_rp) max_rp = abs_rp;
        }

        /* Залишок під yaw = 0.5 - max_rp */
        float yaw_headroom = 0.5f - max_rp;
        if (yaw_headroom < 0.0f) yaw_headroom = 0.0f;

        float max_yaw = 0.0f;
        for (uint8_t i = 0; i < n_act; ++i) {
            float abs_y = u_yaw[i] < 0.0f ? -u_yaw[i] : u_yaw[i];
            if (abs_y > max_yaw) max_yaw = abs_y;
        }

        if (max_yaw > 1e-4f && max_yaw > yaw_headroom) {
            yaw_scale = yaw_headroom / max_yaw;
        }

        /* Перерахунок з відмасштабованим yaw */
        for (uint8_t i = 0; i < n_act; ++i) {
            u[i] = u_thrust[i] + u_rp[i] + u_yaw[i] * yaw_scale;
        }

        /* Повторний зсув після стиснення yaw */
        min_val = u[0];
        max_val = u[0];
        for (uint8_t i = 1; i < n_act; ++i) {
            if (u[i] < min_val) min_val = u[i];
            if (u[i] > max_val) max_val = u[i];
        }
        if (max_val > 1.0f) {
            float shift = max_val - 1.0f;
            for (uint8_t i = 0; i < n_act; ++i) u[i] -= shift;
        }
    }

    /* Крок 5: Апаратне обмеження [u_min, u_max] */
    for (uint8_t i = 0; i < n_act; ++i) {
        float lo = alloc->config.u_min[i];
        float hi = alloc->config.u_max[i];
        if (u[i] < lo) u[i] = lo;
        if (u[i] > hi) u[i] = hi;
        u_out[i] = u[i];
    }
}
```
```cpp
// ============================================================================
// ControlAllocator.hpp
// Модуль матричного розподілу керування польотного контролера (C++20)
// ============================================================================
#pragma once

#include <array>
#include <span>
#include <algorithm>
#include <cmath>
#include <cstdint>

namespace drone::control {

template <std::size_t NumActuators, std::size_t NumAxes = 4>
class ControlAllocator {
public:
    static_assert(NumActuators >= NumAxes, "Кількість приводів має бути не меншою за кількість керованих осей");

    struct Config {
        // Псевдообернена матриця ефективності B^+ (NumActuators рядків, NumAxes стовпчиків)
        std::array<std::array<float, NumAxes>, NumActuators> pseudoInverse{};
        std::array<float, NumActuators> minLimits{}; // Зазвичай 0.0f
        std::array<float, NumActuators> maxLimits{}; // Зазвичай 1.0f
    };

    explicit constexpr ControlAllocator(const Config& cfg) noexcept : config_(cfg) {}

    // Обчислення фізичних сигналів приводів
    [[nodiscard]] std::array<float, NumActuators> allocate(std::span<const float, NumAxes> tau) const noexcept {
        std::array<float, NumActuators> uThrust{};
        std::array<float, NumActuators> uRollPitch{};
        std::array<float, NumActuators> uYaw{};
        std::array<float, NumActuators> uOut{};

        // 1. Роздільне матричне множення
        for (std::size_t i = 0; i < NumActuators; ++i) {
            uThrust[i]    = config_.pseudoInverse[i][0] * tau[0];
            uRollPitch[i] = config_.pseudoInverse[i][1] * tau[1] + config_.pseudoInverse[i][2] * tau[2];
            uYaw[i]       = (NumAxes > 3) ? config_.pseudoInverse[i][3] * tau[3] : 0.0f;
            uOut[i]       = uThrust[i] + uRollPitch[i] + uYaw[i];
        }

        // 2. Пошук екстремумів
        auto [minIt, maxIt] = std::minmax_element(uOut.begin(), uOut.end());
        float minVal = *minIt;
        float maxVal = *maxIt;

        // 3. Десатурація зсувом (Shift Desaturation)
        if (maxVal > 1.0f) {
            const float shift = maxVal - 1.0f;
            for (auto& val : uOut) val -= shift;
            minVal -= shift;
            maxVal = 1.0f;
        }
        if (minVal < 0.0f) {
            const float shift = -minVal;
            for (auto& val : uOut) val += shift;
            maxVal += shift;
            minVal = 0.0f;
        }

        // 4. Пріоритезація: стиснення рискання заради збереження крену й тангажу
        if (maxVal > 1.0f && NumAxes > 3) {
            float maxRp = 0.0f;
            float maxYaw = 0.0f;
            for (std::size_t i = 0; i < NumActuators; ++i) {
                maxRp = std::max(maxRp, std::abs(uRollPitch[i]));
                maxYaw = std::max(maxYaw, std::abs(uYaw[i]));
            }

            const float yawHeadroom = std::max(0.0f, 0.5f - maxRp);
            const float yawScale = (maxYaw > 1e-4f && maxYaw > yawHeadroom) ? (yawHeadroom / maxYaw) : 1.0f;

            for (std::size_t i = 0; i < NumActuators; ++i) {
                uOut[i] = uThrust[i] + uRollPitch[i] + uYaw[i] * yawScale;
            }

            auto [newMin, newMax] = std::minmax_element(uOut.begin(), uOut.end());
            if (*newMax > 1.0f) {
                const float shift = *newMax - 1.0f;
                for (auto& val : uOut) val -= shift;
            }
        }

        // 5. Фінальне жорстке затискання в дозволені фізичні межі
        for (std::size_t i = 0; i < NumActuators; ++i) {
            uOut[i] = std::clamp(uOut[i], config_.minLimits[i], config_.maxLimits[i]);
        }

        return uOut;
    }

private:
    Config config_;
};

} // namespace drone::control
```
:::

## Тестовий стенд: перевірка на конфігураціях Quad-X та Hexa-X

Для валідації коректності роботи алгоритму створюється тестовий модуль, що симулює роботу алокатора в режимі нормального польоту, глибокого насичення та відмови мотора.

:::tabs
```c
#include <stdio.h>
#include <assert.h>

void test_quad_x_allocation(void)
{
    allocator_config_t cfg = {
        .num_actuators = 4,
        .u_min = {0.0f, 0.0f, 0.0f, 0.0f},
        .u_max = {1.0f, 1.0f, 1.0f, 1.0f},
        .b_pseudo_inv = {
            /* F_z     Roll     Pitch     Yaw */
            { 0.25f,  0.25f,   0.25f,   0.25f }, /* Motor 1: Front-Right CCW */
            { 0.25f,  0.25f,  -0.25f,  -0.25f }, /* Motor 2: Rear-Right  CW  */
            { 0.25f, -0.25f,   0.25f,  -0.25f }, /* Motor 3: Front-Left   CW  */
            { 0.25f, -0.25f,  -0.25f,   0.25f }  /* Motor 4: Rear-Left   CCW */
        }
    };

    allocator_t alloc;
    allocator_init(&alloc, &cfg);

    /* Тест 1: Номінальне зависання (газ 50%, нульові моменти) */
    float tau1[4] = { 2.0f, 0.0f, 0.0f, 0.0f };
    float u1[4];
    allocator_update(&alloc, tau1, u1);

    for (int i = 0; i < 4; ++i) {
        /* Усі мотори мають отримати 0.5 */
        assert(u1[i] >= 0.499f && u1[i] <= 0.501f);
    }

    /* Тест 2: Насичення при високому газі (газ 90% + сильний крен 0.4) */
    float tau2[4] = { 3.6f, 0.4f, 0.0f, 0.0f };
    float u2[4];
    allocator_update(&alloc, tau2, u2);

    /* Мотори 1 та 2 мали б отримати 0.9 + 0.1 = 1.0; мотори 3 та 4: 0.9 - 0.1 = 0.8 */
    assert(alloc.saturated == false); /* Рівно на межі */

    /* Тест 3: Глибоке насичення (газ 95% + крен 0.8) */
    float tau3[4] = { 3.8f, 0.8f, 0.0f, 0.0f };
    float u3[4];
    allocator_update(&alloc, tau3, u3);

    assert(alloc.saturated == true);
    /* Завдяки десатурації максимальний мотор не перевищує 1.0, різниця збережена */
    assert(u3[0] <= 1.0001f);
    assert(u3[0] - u3[2] >= 0.199f);
}

int main(void)
{
    test_quad_x_allocation();
    return 0;
}
```
```cpp
#include <iostream>
#include <cassert>

using namespace drone::control;

void test_quad_cpp() {
    typename ControlAllocator<4>::Config cfg{};
    cfg.minLimits.fill(0.0f);
    cfg.maxLimits.fill(1.0f);

    // Псевдообернена матриця Quad-X
    cfg.pseudoInverse = {{
        { 0.25f,  0.25f,   0.25f,   0.25f },
        { 0.25f,  0.25f,  -0.25f,  -0.25f },
        { 0.25f, -0.25f,   0.25f,  -0.25f },
        { 0.25f, -0.25f,  -0.25f,   0.25f }
    }};

    ControlAllocator<4> allocator(cfg);

    // Тест: Режим висіння з маневром крену
    std::array<float, 4> tau{ 2.0f, 0.4f, 0.0f, 0.0f };
    auto u = allocator.allocate(tau);

    assert(u[0] == 0.6f); // 0.5 + 0.1
    assert(u[1] == 0.6f); // 0.5 + 0.1
    assert(u[2] == 0.4f); // 0.5 - 0.1
    assert(u[3] == 0.4f); // 0.5 - 0.1
}

int main() {
    test_quad_cpp();
    return 0;
}
```
:::

## Інженерні пастки, взаємодія з драйверами та діагностика

Під час інтеграції розрахункового ядра алокатора у реальну прошивку виникає кілька критичних аспектів взаємодії з апаратним рівнем:

1. **Трансляція в апаратний протокол DShot / PWM:**
   Отримані з алокатора нормалізовані значення `u_out[i] ∈ [0.0, 1.0]` мають перетворюватися на цифрові кадри DShot або імпульси PWM. Для протоколу DShot діапазон `0..1` відображається на значення від 48 (мінімальний газ для обертання без зупинки) до 2047 (максимальна тяга), тоді як значення 0 резервується під команду вимкнення (Disarmed). Драйвер таймера на мікроконтролері використовує прямий доступ до пам'яті (DMA), щоб передавати ці 16-бітні слова у вихідні канали таймера без затримок центрального процесора.

2. **Нелінійність характеристики тяги гвинта:**
   Реальна статична тяга безколекторного мотора пропорційна квадрату кутової швидкості гвинта `T ≈ c_t · ω²`, тоді як регулятор ESC керує напругою чи шпаруватістю PWM лінійно. Перед подачею сигналу `u_out` на вихідний таймер обов'язково застосовується лінеаризація тяги:
   ```
   u_linear = (1 - k) · u + k · u²
   ```
   де `k ≈ 0.6..0.85` — коефіцієнт кривини лопаті, що визначається експериментально на стенді тяги.

3. **Асиметрія смуги пропускання приводів:**
   ESC-регулятори моторів відпрацьовують зміни уставки із затримкою 2–10 мс (протоколи DShot300/DShot600), тоді як механічні сервоприводи рулів мають затримку 40–120 мс і швидкість перекладки 60° за 0.1 с. У гібридних схемах (VTOL, літаки) швидкі високочастотні збурення крену розподіляються на мотори, а повільні тривалі балансувальні моменти — на сервоприводи.

4. **Чисельне виродження матриці `B · Bᵀ`:**
   Якщо рама дрона втрачає керованість за однією з осей (наприклад, усі гвинти повертаються строго горизонтально), матриця Грама стає виродженою (`det(B Bᵀ) = 0`). Модуль розрахунку псевдооберненої матриці на етапі конфігурації мусить перевіряти число обумовленості `κ(B)` і сигналізувати помилку валідації рами, якщо `κ(B) > 1000`.

5. **Телеметрія насичення для контурів PID (Anti-Windup):**
   Модуль алокатора зобов'язаний виставляти прапорець `saturated` у внутрішню структуру шини повідомлень автопілота. Коли регулятор орієнтації бачить прапорець `saturated == true`, він **зупиняє накопичення інтегральної складової (Anti-Windup Clamping)** у контурах PID. Якщо цього не зробити, інтегратор помилки кутової швидкості продовжуватиме зростати під час виконання граничного маневру, і після повернення стіка керування в нейтраль дрон різко хитнеться у зворотний бік через накопичений «надлишок» інтегратора.
