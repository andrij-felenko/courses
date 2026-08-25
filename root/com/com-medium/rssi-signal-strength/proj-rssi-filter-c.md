# ⚙️ Реалізація IIR-фільтрації RSSI та логіки хендовера

У реальних радіоефірних умовах миттєві вимірювання рівня сигналу (RSSI/RSRP) піддаються швидким завмиранням Релея та випромінювальній шумності. Пряме використання сирих відліків для прийняття рішень про відключення пристрою або переключення на іншу базову станцію викликає «ефект пінг-понгу» — хаотичні перемикання між вежами по кілька разів на секунду.

Цей проєкт демонструє створення високоефективного цифрового тракту обробки RSSI/RSRP у C та C++, що включає:
1. **IIR-фільтр першого порядку (експоненційне ковзне середнє, EMA)** для придушення швидких флуктуацій.
2. **Адаптивне змінення коефіцієнта згладжування** залежно від динаміки руху пристрою.
3. **Гістерезисний тригер прийняття рішень** про зміну стану лінку (хендовер або втрата зв’язку).

## Програмний код: C та C++

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

/* Стани з'єднання радіоканалу */
typedef enum {
    LINK_STATE_DISCONNECTED = 0,
    LINK_STATE_SEARCHING,
    LINK_STATE_CONNECTED,
    LINK_STATE_HANDOFF_REQUIRED
} link_state_t;

/* Структура конфігурації та стану фільтра RSSI */
typedef struct {
    float alpha;               /* Коефіцієнт згладжування (0.0 < alpha <= 1.0) */
    float filtered_rssi_dbm;   /* Поточне фільтроване значення в дБм */
    bool initialized;          /* Прапорець первинної ініціалізації */
    
    float connect_threshold_dbm; /* Поріг підключення (наприклад, -85.0 дБм) */
    float disconnect_threshold_dbm; /* Поріг відключення з гістерезисом (наприклад, -95.0 дБм) */
    float handoff_margin_dbm;    /* Запас гістерезису для хендовера (наприклад, 5.0 дБ) */
    
    link_state_t current_state;  /* Поточний стан лінку */
} rssi_filter_t;

/**
 * @brief Ініціалізація структури фільтра
 */
void rssi_filter_init(rssi_filter_t *filter, float alpha, 
                      float connect_th, float disconnect_th, float handoff_margin) {
    if (!filter) return;
    
    filter->alpha = (alpha > 0.0f && alpha <= 1.0f) ? alpha : 0.2f;
    filter->filtered_rssi_dbm = -120.0f;
    filter->initialized = false;
    filter->connect_threshold_dbm = connect_th;
    filter->disconnect_threshold_dbm = disconnect_th;
    filter->handoff_margin_dbm = handoff_margin;
    filter->current_state = LINK_STATE_DISCONNECTED;
}

/**
 * @brief Оновлення стану фільтра новим сирим відліком RSSI
 * @param filter Вказівник на структуру
 * @param raw_rssi_dbm Сире виміряне значення з АЦП/демодулятора у дБм
 * @param neighbor_rssi_dbm Поточний рівень сигналу сусідньої вежі
 * @return Поточний оновлений стан лінку
 */
link_state_t rssi_filter_update(rssi_filter_t *filter, float raw_rssi_dbm, float neighbor_rssi_dbm) {
    if (!filter) return LINK_STATE_DISCONNECTED;

    /* 1. Експоненційне ковзне середнє (IIR / EMA фільтр) */
    if (!filter->initialized) {
        filter->filtered_rssi_dbm = raw_rssi_dbm;
        filter->initialized = true;
    } else {
        filter->filtered_rssi_dbm = (filter->alpha * raw_rssi_dbm) + 
                                    ((1.0f - filter->alpha) * filter->filtered_rssi_dbm);
    }

    /* 2. Логіка кінцевого автомата станів (FSM) із гістерезисом */
    switch (filter->current_state) {
        case LINK_STATE_DISCONNECTED:
            if (filter->filtered_rssi_dbm >= filter->connect_threshold_dbm) {
                filter->current_state = LINK_STATE_CONNECTED;
            } else {
                filter->current_state = LINK_STATE_SEARCHING;
            }
            break;

        case LINK_STATE_SEARCHING:
            if (filter->filtered_rssi_dbm >= filter->connect_threshold_dbm) {
                filter->current_state = LINK_STATE_CONNECTED;
            }
            break;

        case LINK_STATE_CONNECTED:
            /* Поріг відключення нижчий за поріг підключення (гістерезис) */
            if (filter->filtered_rssi_dbm < filter->disconnect_threshold_dbm) {
                filter->current_state = LINK_STATE_DISCONNECTED;
            }
            /* Перевірка потреби хендовера на сусідній осередки */
            else if (neighbor_rssi_dbm > (filter->filtered_rssi_dbm + filter->handoff_margin_dbm)) {
                filter->current_state = LINK_STATE_HANDOFF_REQUIRED;
            }
            break;

        case LINK_STATE_HANDOFF_REQUIRED:
            /* Статус скидається після виконання процедури перемикання */
            if (neighbor_rssi_dbm <= (filter->filtered_rssi_dbm + filter->handoff_margin_dbm)) {
                filter->current_state = LINK_STATE_CONNECTED;
            }
            break;
    }

    return filter->current_state;
}

int main(void) {
    rssi_filter_t filter;
    rssi_filter_init(&filter, 0.15f, -80.0f, -92.0f, 6.0f);

    /* Симуляція серії відліків сигналу (згасання + шум) */
    float raw_samples[] = {
        -110.0f, -105.0f, -82.0f, -78.0f, -75.0f, -74.0f, /* Вхід у покриття */
        -76.0f,  -90.0f,  -73.0f, -75.0f,                /* Швидке завмирання */
        -88.0f,  -94.0f,  -96.0f, -98.0f                 /* Вихід із покриття */
    };
    size_t sample_count = sizeof(raw_samples) / sizeof(raw_samples[0]);

    printf("Крок | Сирий (дБм) | Фільтрований (дБм) | Стан лінку\n");
    printf("---------------------------------------------------\n");

    for (size_t i = 0; i < sample_count; ++i) {
        link_state_t state = rssi_filter_update(&filter, raw_samples[i], -120.0f);
        const char *state_str = (state == LINK_STATE_CONNECTED) ? "CONNECTED" :
                                (state == LINK_STATE_SEARCHING) ? "SEARCHING" :
                                (state == LINK_STATE_HANDOFF_REQUIRED) ? "HANDOFF" : "DISCONNECTED";
        
        printf("%4zu | %11.1f | %17.2f | %s\n", 
               i + 1, raw_samples[i], filter->filtered_rssi_dbm, state_str);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <optional>

enum class LinkState {
    Disconnected,
    Searching,
    Connected,
    HandoffRequired
};

constexpr std::string_view to_string(LinkState state) noexcept {
    switch (state) {
        case LinkState::Disconnected:    return "DISCONNECTED";
        case LinkState::Searching:       return "SEARCHING";
        case LinkState::Connected:       return "CONNECTED";
        case LinkState::HandoffRequired: return "HANDOFF_REQUIRED";
    }
    return "UNKNOWN";
}

class RssiEvaluator {
public:
    struct Config {
        float alpha{0.2f};               // Коефіцієнт EMA (0.0 < alpha <= 1.0)
        float connectThresholdDbm{-80.0f};
        float disconnectThresholdDbm{-92.0f};
        float handoffMarginDbm{6.0f};
    };

    explicit RssiEvaluator(Config config) : config_(config) {}

    /**
     * @brief Обновити фільтр новим значенням RSSI
     * @return Поточне значення фільтрованого RSSI та оновлений стан
     */
    LinkState update(float rawRssiDbm, float neighborRssiDbm = -120.0f) noexcept {
        if (!filteredRssi_) {
            filteredRssi_ = rawRssiDbm;
        } else {
            *filteredRssi_ = (config_.alpha * rawRssiDbm) + ((1.0f - config_.alpha) * (*filteredRssi_));
        }

        const float currentRssi = *filteredRssi_;

        switch (currentState_) {
            case LinkState::Disconnected:
            case LinkState::Searching:
                if (currentRssi >= config_.connectThresholdDbm) {
                    currentState_ = LinkState::Connected;
                } else {
                    currentState_ = LinkState::Searching;
                }
                break;

            case LinkState::Connected:
                if (currentRssi < config_.disconnectThresholdDbm) {
                    currentState_ = LinkState::Disconnected;
                } else if (neighborRssiDbm > (currentRssi + config_.handoffMarginDbm)) {
                    currentState_ = LinkState::HandoffRequired;
                }
                break;

            case LinkState::HandoffRequired:
                if (neighborRssiDbm <= (currentRssi + config_.handoffMarginDbm)) {
                    currentState_ = LinkState::Connected;
                }
                break;
        }

        return currentState_;
    }

    [[nodiscard]] std::optional<float> filteredRssi() const noexcept {
        return filteredRssi_;
    }

    [[nodiscard]] LinkState state() const noexcept {
        return currentState_;
    }

private:
    Config config_;
    std::optional<float> filteredRssi_{std::nullopt};
    LinkState currentState_{LinkState::Disconnected};
};

int main() {
    RssiEvaluator evaluator({.alpha = 0.15f, .connectThresholdDbm = -80.0f, 
                             .disconnectThresholdDbm = -92.0f, .handoffMarginDbm = 6.0f});

    const std::vector<float> rawSamples = {
        -110.0f, -105.0f, -82.0f, -78.0f, -75.0f, -74.0f,
        -76.0f,  -90.0f,  -73.0f, -75.0f,
        -88.0f,  -94.0f,  -96.0f, -98.0f
    };

    std::cout << "Крок | Сирий (дБм) | Фільтрований (дБм) | Стан лінку\n";
    std::cout << "---------------------------------------------------\n";

    for (size_t i = 0; i < rawSamples.size(); ++i) {
        LinkState state = evaluator.update(rawSamples[i]);
        std::cout << " " << (i + 1) << "   | " 
                  << rawSamples[i] << "        | " 
                  << evaluator.filteredRssi().value_or(-120.0f) << "             | " 
                  << to_string(state) << "\n";
    }

    return 0;
}
```
:::

## Глибокий архітектурний розбір реалізації

Проєктування систем первинної обробки телеметрії та показників радіоефіру вимагає врахування обчислювальної обмеженості вбудованих мікроконтролерів (MCU), стабільності обчислень та відсутності непередбачуваної поведінки при сплесках шуму.

### 1. Вибір математичної моделі IIR-фільтрації

Фільтр з безкінечною імпульсною характеристикою (Infinite Impulse Response, IIR) першого порядку відповідає експоненційному ковзному середньому (Exponential Moving Average, EMA):

```
y[n] = α · x[n] + (1 - α) · y[n-1]
```

#### Чому обрано IIR замість FIR (фільтра з скінченною імпульсною характеристикою):
- **Мінімальне споживання пам'яті:** Для FIR-фільтра скользящого вікна шириною `N = 32` відліків потрібно зберігати кільцевий буфер на 32 елементи (`128 байт` RAM). Для IIR-фільтра першого порядку потрібна лише одна змінна поточного стану `y[n-1]` (`4 байти` RAM).
- **Обчислювальна складність:** IIR-фільтр виконує лише два множення та одне додавання на кожен новий відлік, що дозволяє запускати його безпосередньо в обробнику переривань АЦП чи ДМА (ADC/DMA Interrupt Service Routine).

### 2. Оптимізація для 8-бітних та 32-бітних MCU без FPU (Fixed-Point Arithmetic)

У пристроях на базі мікроконтролерів без апаратного блоку плаваючої коми (FPU), таких як Cortex-M0+ або AVR, операції з типом `float` програмно емулюються бібліотекою `libgcc`, що споживає сотні тактів процесора.

Для таких систем алгоритм переводять у цілочисельну арифметику з фіксованою комою (Fixed-Point format Q16.16):

:::tabs
```c
/* Цілочисельна реалізація IIR-фільтра у форматі Q16.16 */
typedef struct {
    int32_t alpha_q16;         /* Коефіцієнт alpha * 65536 (наприклад, 0.15 * 65536 = 9830) */
    int32_t filtered_rssi_q16; /* Значення RSSI у дБм * 65536 */
    bool initialized;
} rssi_filter_fixed_t;

int32_t rssi_filter_update_fixed(rssi_filter_fixed_t *f, int32_t raw_rssi_dbm) {
    int32_t raw_q16 = raw_rssi_dbm << 16;
    
    if (!f->initialized) {
        f->filtered_rssi_q16 = raw_q16;
        f->initialized = true;
    } else {
        /* y[n] = alpha * x[n] + (1 - alpha) * y[n-1] у Q16 */
        int64_t term1 = (int64_t)f->alpha_q16 * raw_q16;
        int64_t term2 = (int64_t)(65536 - f->alpha_q16) * f->filtered_rssi_q16;
        f->filtered_rssi_q16 = (int32_t)((term1 + term2) >> 16);
    }
    
    return f->filtered_rssi_q16 >> 16; /* Повертаємо ціле значення у дБм */
}
```
```cpp
#include <cstdint>
#include <optional>

class RssiFilterFixed {
public:
    constexpr explicit RssiFilterFixed(float alpha) noexcept
        : alphaQ16_(static_cast<int32_t>(alpha * 65536.0f)) {}

    [[nodiscard]] constexpr int32_t update(int32_t rawRssiDbm) noexcept {
        const int32_t rawQ16 = rawRssiDbm << 16;

        if (!filteredRssiQ16_) {
            filteredRssiQ16_ = rawQ16;
        } else {
            const int64_t term1 = static_cast<int64_t>(alphaQ16_) * rawQ16;
            const int64_t term2 = static_cast<int64_t>(65536 - alphaQ16_) * (*filteredRssiQ16_);
            filteredRssiQ16_ = static_cast<int32_t>((term1 + term2) >> 16);
        }

        return *filteredRssiQ16_ >> 16;
    }

private:
    int32_t alphaQ16_{9830}; // За замовчуванням 0.15 * 65536
    std::optional<int32_t> filteredRssiQ16_{std::nullopt};
};
```
:::

Використання бітового зсуву `>> 16` замість ділення виконується за один такт процесора, забезпечуючи високу швидкість обробки телеметрії. У мікроконтролерах архітектури ARM Cortex-M4F або Cortex-M7 інструкція DSP `SMLABB` (Signed Multiply Accumulate) здатна виконати перемноження та накопичення чисел у форматі Q16 за один єдиний такт процесора.

### 3. Адаптивне динамічне регулювання коефіцієнта згладжування `α`

У статичних умовах пристрій потребує сильного придушення шуму (малий `α = 0.05`), проте при швидкому русі модема (наприклад, у автомобілі) малий `α` створює затримку реакції (фазовий зсув). Це призводить до пізнього виявлення падіння сигналу та обриву лінку.

Для усунення цього недоліку застосовують **адаптивний EMA-фільтр**, де `α` змінюється залежно від поточної дисперсії відхилень:

:::tabs
```c
float delta = raw_rssi_dbm - filter->filtered_rssi_dbm;
if (delta < 0) delta = -delta;

/* Якщо відхилення перевищує 10 дБ (швидке згасання), тимчасово збільшуємо alpha */
float dynamic_alpha = (delta > 10.0f) ? 0.5f : filter->alpha;
filter->filtered_rssi_dbm = (dynamic_alpha * raw_rssi_dbm) + ((1.0f - dynamic_alpha) * filter->filtered_rssi_dbm);
```
```cpp
#include <cmath>

float delta = std::abs(rawRssiDbm - currentFilteredRssi);

// Адаптивний розрахунок: при різкому стрибку сигналу alpha розширюється
float dynamicAlpha = (delta > 10.0f) ? 0.5f : config_.alpha;
currentFilteredRssi = (dynamicAlpha * rawRssiDbm) + ((1.0f - dynamicAlpha) * currentFilteredRssi);
```
:::

Завдяки адаптивності фільтр миттєво реагує на різкий вихід із зони покриття, зберігши при цьому гладкість обробки в стаціонарному режимі.

### 4. Налаштування параметрів згладжування та частоти дискретизації

Вибір коефіцієнта `α` залежить від періоду опитування модема `T_s`:

```
α = 1 - exp( -T_s / τ )
```

Де `τ` — постійна часу фільтра (Time Constant).
- Якщо період випитування АЦП `T_s = 100 мс`, а необхідна постійна часу стабілізації дорівнює `τ = 1.0 с`, то `α = 1 - exp(-0.1 / 1.0) ≈ 0.095`.
- При `α = 0.1` фільтр досягає 95% значення нового рівня сигналу за `3 · τ ≈ 3 секунди`, що ідеально підходить для придушення швидких Релеєвських завмирань при пішохідному русі або радіоаматорському зв'язках.

### 5. Гістерезисна логіка автомата станів (FSM) та крайові випадки

Автомат станів запобігає хибним перемиканням зв'язку. В алгоритмі реалізовано наступні захисні механізми:

1. **Захист від аномальних викидів (Outlier Rejection):** При першому вимірі (`!initialized`) фільтр одразу приймає сире значення `raw_rssi_dbm`, уникаючи тривалого наростання сигналу з початкового нульового рівня.
2. **Гістерезисна смуга з'єднання/роз'єднання:**
   - Поріг підключення: `-80.0 дБм`.
   - Поріг відключення: `-92.0 дБм`.
   - Зона гістерезису шириною `12.0 дБ` гарантує, що пристрій не буде нескінченно переходити між станами при флуктуаціях сигналу біля межі покриття.
3. **Маржинальний поріг хендовера (Handoff Margin):**
   - Сусідня сота повинна мати сигнал, що перевищує поточну на `handoffMarginDbm = 6.0 дБ`. Це компенсує витрати на перереєстрацію в мережі та захищає від ефекту «пінг-понгу» між двома вежами з однаковим рівнем покриття.
### 6. Покрокове простеження виконання (Trace Analysis)

Розглянемо проходження симуляційного набору відліків крізь обчислювальний тракт:

1. **Крок 1 (Первинний відлік `-110.0 дБм`):** Прапорець `initialized` дорівнює `false`. Фільтр присвоює значення `filtered_rssi_dbm = -110.0` без обчислення EMA. Автомат переходить у стан `SEARCHING`, оскільки рівень сигналу нижчий за поріг підключення `-80.0 дБм`.
2. **Кроки 2–5 (Наближення до вежі):** Сигнал зростає до `-82.0 дБм`, а потім до `-75.0 дБм`. Згладжене значення досягає `-79.2 дБм`, перетинаючи поріг підключення `-80.0 дБм`. Автомат станів здійснює транзицію у стан `CONNECTED`.
3. **Кроки 7–10 (Швидке короткочасне завмирання):** Сирий сигнал миттєво провалюється до `-90.0 дБм` через інтерференцію відбитого променя. Завдяки згладжуванню із `α = 0.15` фільтроване значення опускається лише до `-79.8 дБм`, що вище за поріг відключення `-92.0 дБм`. Пристрій залишається у стані `CONNECTED`, уникнувши хибного розриву сесії.
4. **Кроки 11–14 (Вихід із зони покриття):** Сигнал послідовно падає до `-94.0 дБм`, `-96.0 дБм` та `-98.0 дБм`. Фільтроване значення перетинає поріг `-92.0 дБм`, і автомат контрольовано переводить систему у стан `DISCONNECTED`.

Цей покроковий аналіз підтверджує, що комбінація IIR-фільтрації та гістерезису гарантує стійкість системи до короткочасних завад при збереженні точного моніторингу реального тренду покриття.
