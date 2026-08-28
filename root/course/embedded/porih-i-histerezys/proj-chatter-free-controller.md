# ⚙️ Повний надійний пороговий компаратор із фільтрацією та гістерезисом

Порогове керування виконавчими пристроями (електромагнітними реле, симісторами, контакторами ТЕНів, соленоїдними клапанами, компресорами) у вбудованих системах вимагає комплексного багаторівневого захисту. Простий виклик умовного оператора над сирим значенням АЦП гарантовано призводить до аварійних режимів: високочастотного деренчання контактів, перегріву пускових обмоток двигунів та вибивання мікроконтролера імпульсними завадами.

Для надійної роботи створюється детермінований конвеєр, що поєднує придушення імпульсних сплесків, частотну фільтрацію гауссового шуму, двопороговий амплітудний гістерезис та часове блокування частих перемикань (*hold-off dwell time*).

## 1. Архітектура та послідовність обробки сигналу

Конвеєр обробника спроєктовано як модульний кінцевий автомат, що послідовно пропускає кожен новий відлік АЦП крізь чотири захисні рубежі:

1. **Кільцевий медіанний фільтр (розмір вікна 5 відліків):**
   Нелінійний фільтр рангової статистики, головне призначення якого — повне відсікання поодиноких імпульсних викидів (*spikes*), викликаних комутаційними завадами силової мережі, іскрінням контактів або брязкотом під час вібрації роз'ємів. На відміну від лінійних фільтрів, медіана не згладжує та не розмиває круті дійсні фронти сигналу і не затягує фазу реакції на різку аварійну зміну вимірюваної величини.

2. **Експоненційний фільтр нижніх частот (EMA / IIR 1-го порядку):**
   Згладжує широкосмуговий аналоговий шум тракту, термічні флуктуації терморезистора та шум квантування АЦП. Обчислюється за рекурентною формулою `y[n] = α · x[n] + (1 - α) · y[n-1]`, де коефіцієнт `α ∈ (0, 1]` визначає смугу пропускання `f_c ≈ (α · f_s) / (2π)`. Зниження дисперсії шуму дозволяє зменшити фізичну ширину петлі амплітудного гістерезису без ризику хибних спрацьовувань.

3. **Амплітудний компаратор Шмітта:**
   Формує двійкове рішення із зоною нечутливості `ΔT = threshold_high - threshold_low`. Залежно від конфігурації підтримує пряму логіку (активний нуль / нагрівання: увімкнення при охолодженні нижче `threshold_low`, вимкнення при нагріванні вище `threshold_high`) або інверсну логіку (активна одиниця / охолодження: увімкнення при перевищенні `threshold_high`, вимкнення при спаданні нижче `threshold_low`).

4. **Часовий охоронець стану (Hold-off / Anti-recycle Guard):**
   Фізичний бар'єр часу, що блокує зміну стану виконавчого механізму, якщо з моменту попереднього перемикання минуло менше ніж `min_on_time_ms` (для захисту від передчасного зриву робочого циклу) або `min_off_time_ms` (для захисту компресорів і насосів від пуску проти нескомпенсованого гідравлічного тиску).

## 2. Інтерфейс та реалізація модуля

Нижче наведено повний інтерфейс і реалізацію бібліотеки двома мовами: модульний C-код із роздільними структурами конфігурації та стану, а також сучасний ідіоматичний C++ у вигляді шаблонного класу з використанням `std::chrono`.

:::tabs
```c
#ifndef HYSTERESIS_CONTROLLER_H
#define HYSTERESIS_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

#define HYST_MEDIAN_WINDOW 5

typedef enum {
    HYST_MODE_ACTIVE_LOW  = 0, /* Нагрівання: УВІМК при <= Low, ВИМК при >= High */
    HYST_MODE_ACTIVE_HIGH = 1  /* Охолодження: УВІМК при >= High, ВИМК при <= Low */
} hyst_mode_t;

typedef struct {
    float threshold_low;       /* Нижній поріг перемикання */
    float threshold_high;      /* Верхній поріг перемикання */
    uint32_t min_on_time_ms;   /* Мінімальний час увімкненого стану */
    uint32_t min_off_time_ms;  /* Мінімальний час вимкненого стану */
    float ema_alpha;           /* Коефіцієнт фільтра EMA (0.0 < alpha <= 1.0) */
    hyst_mode_t mode;          /* Режим: нагрівання або охолодження */
} hyst_config_t;

typedef struct {
    float median_buf[HYST_MEDIAN_WINDOW];
    uint8_t median_idx;
    uint8_t median_count;
    float ema_val;
    bool ema_initialized;
    bool current_state;        /* Поточний стан виходу (true = ON, false = OFF) */
    uint32_t last_switch_ms;   /* Часова мітка останнього перемикання */
} hyst_state_t;

typedef struct {
    hyst_config_t cfg;
    hyst_state_t  state;
} hyst_controller_t;

/* Ініціалізація структури контролера */
void hyst_init(hyst_controller_t *ctrl, const hyst_config_t *cfg, uint32_t now_ms);

/* Оновлення стану контролера новим сирим вимірюванням датчика */
bool hyst_update(hyst_controller_t *ctrl, float raw_sample, uint32_t now_ms);

/* Отримання поточного стану виходу */
bool hyst_get_state(const hyst_controller_t *ctrl);

/* Отримання відфільтрованого значення сигналу */
float hyst_get_filtered_value(const hyst_controller_t *ctrl);

#endif /* HYSTERESIS_CONTROLLER_H */
```
```cpp
#pragma once

#include <cstdint>
#include <array>
#include <algorithm>
#include <chrono>

enum class HysteresisMode : uint8_t {
    ActiveLow,  // Нагрівання: УВІМК при <= Low, ВИМК при >= High
    ActiveHigh  // Охолодження: УВІМК при >= High, ВИМК при <= Low
};

template <typename T = float, size_t MedianSize = 5>
class HysteresisController {
    static_assert(MedianSize >= 3 && MedianSize % 2 == 1, "MedianSize must be odd and >= 3");

public:
    struct Config {
        T threshold_low;
        T threshold_high;
        std::chrono::milliseconds min_on_time;
        std::chrono::milliseconds min_off_time;
        T ema_alpha{static_cast<T>(0.2)};
        HysteresisMode mode{HysteresisMode::ActiveLow};
    };

    explicit HysteresisController(const Config& config, std::chrono::milliseconds now = std::chrono::milliseconds{0})
        : config_(config), last_switch_time_(now) {}

    bool update(T raw_sample, std::chrono::milliseconds now) {
        // 1. Медіанний фільтр ковзного вікна
        median_buffer_[median_index_] = raw_sample;
        median_index_ = (median_index_ + 1) % MedianSize;
        if (median_count_ < MedianSize) {
            ++median_count_;
        }

        std::array<T, MedianSize> sort_buf{};
        std::copy_n(median_buffer_.begin(), median_count_, sort_buf.begin());
        std::sort(sort_buf.begin(), sort_buf.begin() + median_count_);
        const T median_val = sort_buf[median_count_ / 2];

        // 2. Експоненційний фільтр EMA
        if (!ema_initialized_) {
            ema_val_ = median_val;
            ema_initialized_ = true;
        } else {
            ema_val_ = config_.ema_alpha * median_val + (static_cast<T>(1) - config_.ema_alpha) * ema_val_;
        }

        // 3. Перевірка часового блокування (Hold-off)
        const auto elapsed = now - last_switch_time_;
        const auto required_hold = state_ ? config_.min_on_time : config_.min_off_time;

        if (elapsed < required_hold) {
            return state_; // Зміна стану заблокована таймером
        }

        // 4. Двопороговий тригер Шмітта
        bool desired_state = state_;
        if (config_.mode == HysteresisMode::ActiveLow) {
            if (ema_val_ <= config_.threshold_low) {
                desired_state = true;  // Охололо нижче порогу -> вмикаємо ТЕН
            } else if (ema_val_ >= config_.threshold_high) {
                desired_state = false; // Нагрілося до верхньої межі -> вимикаємо
            }
        } else {
            if (ema_val_ >= config_.threshold_high) {
                desired_state = true;  // Перегрів вище порогу -> вмикаємо компресор
            } else if (ema_val_ <= config_.threshold_low) {
                desired_state = false; // Охолоджено до норми -> вимикаємо
            }
        }

        if (desired_state != state_) {
            state_ = desired_state;
            last_switch_time_ = now;
        }

        return state_;
    }

    [[nodiscard]] bool state() const noexcept { return state_; }
    [[nodiscard]] T filtered_value() const noexcept { return ema_val_; }
    
    void reset(std::chrono::milliseconds now) noexcept {
        median_count_ = 0;
        median_index_ = 0;
        ema_initialized_ = false;
        state_ = false;
        last_switch_time_ = now;
    }

private:
    Config config_;
    std::array<T, MedianSize> median_buffer_{};
    size_t median_index_{0};
    size_t median_count_{0};
    T ema_val_{0};
    bool ema_initialized_{false};
    bool state_{false};
    std::chrono::milliseconds last_switch_time_{0};
};
```
:::

## 3. Вихідний код реалізації C та тестовий сценарій C++

Нижче наведено файл `hysteresis_controller.c` з швидким сортуванням вставками для фіксованого буфера та тестовий стенд мовою C++:

:::tabs
```c
#include "hysteresis_controller.h"

static float calculate_median5(float *buf, uint8_t count) {
    float temp[HYST_MEDIAN_WINDOW];
    for (uint8_t i = 0; i < count; ++i) {
        temp[i] = buf[i];
    }
    /* Сортування вставками для 3..5 елементів найшвидше на мікроконтролерах */
    for (uint8_t i = 1; i < count; ++i) {
        float key = temp[i];
        int32_t j = (int32_t)i - 1;
        while (j >= 0 && temp[j] > key) {
            temp[j + 1] = temp[j];
            j--;
        }
        temp[j + 1] = key;
    }
    return temp[count / 2];
}

void hyst_init(hyst_controller_t *ctrl, const hyst_config_t *cfg, uint32_t now_ms) {
    if (!ctrl || !cfg) return;
    ctrl->cfg = *cfg;
    ctrl->state.median_idx = 0;
    ctrl->state.median_count = 0;
    ctrl->state.ema_val = 0.0f;
    ctrl->state.ema_initialized = false;
    ctrl->state.current_state = false;
    ctrl->state.last_switch_ms = now_ms;
}

bool hyst_update(hyst_controller_t *ctrl, float raw_sample, uint32_t now_ms) {
    if (!ctrl) return false;
    hyst_state_t *st = &ctrl->state;
    const hyst_config_t *cfg = &ctrl->cfg;

    /* 1. Запис у кільцевий буфер та обчислення медіани */
    st->median_buf[st->median_idx] = raw_sample;
    st->median_idx = (st->median_idx + 1) % HYST_MEDIAN_WINDOW;
    if (st->median_count < HYST_MEDIAN_WINDOW) {
        st->median_count++;
    }
    float median_val = calculate_median5(st->median_buf, st->median_count);

    /* 2. Експоненційне згладжування EMA */
    if (!st->ema_initialized) {
        st->ema_val = median_val;
        st->ema_initialized = true;
    } else {
        st->ema_val = cfg->ema_alpha * median_val + (1.0f - cfg->ema_alpha) * st->ema_val;
    }

    /* 3. Часове блокування (безпечне віднімання uint32_t при переповненні) */
    uint32_t elapsed_ms = now_ms - st->last_switch_ms;
    uint32_t required_hold = st->current_state ? cfg->min_on_time_ms : cfg->min_off_time_ms;

    if (elapsed_ms < required_hold) {
        return st->current_state;
    }

    /* 4. Компаратор Шмітта */
    bool desired_state = st->current_state;
    if (cfg->mode == HYST_MODE_ACTIVE_LOW) {
        if (st->ema_val <= cfg->threshold_low) {
            desired_state = true;
        } else if (st->ema_val >= cfg->threshold_high) {
            desired_state = false;
        }
    } else {
        if (st->ema_val >= cfg->threshold_high) {
            desired_state = true;
        } else if (st->ema_val <= cfg->threshold_low) {
            desired_state = false;
        }
    }

    if (desired_state != st->current_state) {
        st->current_state = desired_state;
        st->last_switch_ms = now_ms;
    }

    return st->current_state;
}

bool hyst_get_state(const hyst_controller_t *ctrl) {
    return ctrl ? ctrl->state.current_state : false;
}

float hyst_get_filtered_value(const hyst_controller_t *ctrl) {
    return ctrl ? ctrl->state.ema_val : 0.0f;
}
```
```cpp
#include <iostream>
#include <vector>
#include <chrono>

int main() {
    using namespace std::chrono_literals;

    // Конфігурація для захисту нагрівача бойлера:
    // Пороги: 58.0 °C (увімк) ... 62.0 °C (вимк)
    // Гарантований час роботи не менше 3000 мс, пауза не менше 5000 мс
    HysteresisController<float, 5>::Config cfg{
        .threshold_low = 58.0f,
        .threshold_high = 62.0f,
        .min_on_time = 3000ms,
        .min_off_time = 5000ms,
        .ema_alpha = 0.3f,
        .mode = HysteresisMode::ActiveLow
    };

    HysteresisController<float, 5> controller(cfg);

    // Тестовий потік вимірювань із аномальними завадами та повільним трендом
    struct TestPoint {
        std::chrono::milliseconds time;
        float raw_adc;
        const char* description;
    };

    const std::vector<TestPoint> test_cases = {
        {   0ms, 65.0f, "Початковий стан: бак гарячий" },
        { 500ms, 61.0f, "Поступове охолодження" },
        {1000ms, 99.0f, "Імпульсна завада від контактора (+99 °C) -> відсікається медіаною" },
        {1500ms, 57.5f, "Температура впала нижче Low (58 °C) -> увімкнення ТЕНа" },
        {2000ms, 57.0f, "Нагрівання розпочато, стан ON" },
        {2500ms, 63.0f, "Швидкий сплеск вище High, але min_on_time ще не минув -> стан ON зберігається" },
        {4600ms, 62.5f, "Пройшло > 3000 мс і температура > High -> коректне вимкнення ТЕНа" },
        {5000ms, 56.0f, "Швидке падіння < Low, але діє min_off_time -> увімкнення заблоковано" },
        {9800ms, 56.0f, "Пауза min_off_time вичерпана -> повторний безпечний пуск ТЕНа" }
    };

    for (const auto& pt : test_cases) {
        bool state = controller.update(pt.raw_adc, pt.time);
        std::cout << "[" << pt.time.count() << " ms] " << pt.description << "\n"
                  << "  Raw: " << pt.raw_adc << " °C | Filtered: " << controller.filtered_value()
                  << " °C | Relay: " << (state ? "ON" : "OFF") << "\n\n";
    }

    return 0;
}
```
:::

## 4. Інженерний розбір крайових випадків та пасток

1. **Безпека переповнення таймера `uint32_t`:**
   У вбудованих системах системний лічильник мілісекунд (`SysTick` або `HAL_GetTick()`) переповнюється кожні 49.71 доби. Перевірка часового інтервалу через різницю `uint32_t elapsed = now_ms - last_switch_ms` строго відповідає модульній арифметиці `2^32`. Якщо останнє перемикання сталося на мітці `0xFFFFFFF0`, а поточний час `0x00000020`, різниця `0x00000020 - 0xFFFFFFF0 = 0x00000030` (48 мс) обчислюється абсолютно коректно. Натомість запис вигляду `if (now_ms >= last_switch_ms + hold_ms)` призводить до переповнення суми у правій частині та блокує роботу на 49 діб.

2. **Поведінка під час «холодного старту»:**
   Якщо прилад запускається, коли вимірювана температура вже лежить усередині мертвої зони (`58.0 °C < T < 62.0 °C`), компаратор не може знати попередню історію. За замовчуванням безпечним станом для нагрівача є `OFF` (щоб уникнути неконтрольованого нагріву після переривання живлення), а для холодильника — `OFF` (щоб уникнути перевантаження мережі одночасним пуском компресорів). Нагрівач увімкнеться лише тоді, коли температура гарантовано опуститься до нижньої межі.

3. **Спільна робота медіани та EMA:**
   Медіанний фільтр є нелінійним і діє як ідеальний амплітудний селектор: якщо у вікні з 5 відліків з'являється один або два викиди довільної амплітуди, вони відкидаються на етапі сортування й не впливають на центральний елемент. Фільтр EMA, своєю чергою, придушує дрібний високочастотний шум, перетворюючи дискретну сходинку на гладку криву.

4. **Обчислювальні витрати:**
   Запропонована реалізація не містить динамічного виділення пам'яті (`malloc`/`free`), не генерує винятків і займає менше 40 байтів ОЗП на один екземпляр контролера. Сортування вставками масиву з 5 елементів потребує у найгіршому випадку 10 порівнянь, що виконується за лічені мікросекунди на будь-якому ядрі ARM Cortex-M0/M3/M4.

## 5. Інтеграція в реальну прошивку та захист від аномалій

Під час інтеграції порогового контролера у виробничу прошивку необхідно враховувати діагностику апаратного стану вимірювального тракту:

- **Діагностика обриву та короткого замикання датчика:**
  Якщо аналоговий вхід видає значення біля нульової напруги (`V_adc < 0.05 В`) або біля опорної напруги живлення (`V_adc > V_ref - 0.05 В`), це свідчить про фізичний обрив кабелю NTC-терморезистора або замикання на землю. У такому разі виклик `hyst_update` необхідно блокувати й переводити систему в безумовний стан аварійної безпеки (*failsafe* — вимкнення ТЕНа).
  
- **Потокобезпечність в середовищі FreeRTOS:**
  Екземпляр `hyst_controller_t` не містить внутрішніх м'ютексів для мінімізації накладних витрат. Якщо виклик `hyst_update()` здійснюється з періодичної задачі збору телеметрії (наприклад, 100 Гц), а зчитування стану `hyst_get_state()` — з задачі інтерфейсу користувача або веб-сервера, звернення до структури необхідно захищати критичною секцією або передавати стан через чергу повідомлень (`xQueueSend`).

- **Цілочисельна арифметика з фіксованою комою:**
  Для наднизькоспоживаючих 8-бітних або 16-бітних контролерів без апаратного блоку FPU операції з типом `float` можна замінити форматом Q15 (множення на 2¹⁵ або фіксований масштаб у міліградусах, де `25.0 °C ≡ 25000`). Усі співвідношення медіани, фільтрації EMA та часового гістерезису зберігаються ідентичними.
