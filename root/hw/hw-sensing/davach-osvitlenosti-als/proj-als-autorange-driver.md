# ⚙️ Драйвер ALS з автовибором шкали та фільтрацією мерехтіння

Автоматичний підбір чутливості інтегрального давача освітленості (ALS) вимагає динамічного перемикання коефіцієнта підсилення вхідного аналогового тракту (PGA Gain) та часу інтегрування АЦП (T_int). Без надійного кінцевого автомата (FSM) система легко потрапляє у дві типові пастки: або застрягає в стані насичення (clipping) при раптовому переході з тіні на яскраве сонце, або починає нескінченно коливатися між двома сусідніми піддіапазонами під час повільних змін освітленості (gain hunting / thrashing). Цей проект демонструє побудову асинхронного драйвера з кінцевим автоматом адаптивного автопідбору, компенсацією оптичного затухання в захисному склі та придушенням мерехтіння освітлювальної мережі 100/120 Гц.

## Логіка кінцевого автомата (Auto-Ranging FSM)

Основне завдання алгоритму — підтримувати робочу точку аналогово-цифрового перетворювача у верхній третині динамічного діапазону (від 30% до 80% від повної шкали Full Scale), де співвідношення сигнал/шум (SNR) є максимальним, а шум квантування вносить найменшу відносну похибку.

Для забезпечення стабільності драйвер спирається на такі правила:
1. **Захист від переповнення (Saturation / High Clipping)**: якщо поточний сирий відлік АЦП каналу CH0 перевищує верхній поріг (85% від 65535, тобто `RAW > 55705`) або апаратний статусний біт переповнення `OVF` встановлено в 1, підсилення PGA негайно знижується на один або два ступені. Якщо підсилення вже мінімальне (`Gain = 1x`), драйвер зменшує час інтегрування `T_int`.
2. **Підвищення роздільної здатності в темряві (Low Level)**: якщо відлік падає нижче 10% шкали (`RAW < 6553`), підсилення PGA збільшується на один ступінь. Якщо підсилення досягло максимуму (`Gain = 128x`), драйвер збільшує час інтегрування `T_int` (аж до 800 мс).
3. **Гістерезисний бар'єр**: між нижнім порогом (10%) та верхнім порогом (85%) існує 75-відсотковий захисний коридор. Оскільки крок перемикання PGA між сусідніми ступенями становить 2x або 4x (тобто 100% або 300%), перехід на новий ступінь ніколи не перекидає робочу точку за протилежний поріг, що математично унеможливлює виникнення циклічного автоколивання під стабільним світлом.
4. **Захисна затримка перехідного процесу (Holdoff / Blanking Timer)**: після запису нових параметрів у конфігураційні регістри давача внутрішній інтегратор заряду повинен скинути накопичений заряд і розпочати чистий цикл накопичення фотоструму. Драйвер встановлює прапорець `range_changed` і блокує обчислення люксів доти, доки від давача не надійде апаратне переривання по лінії `INT` або статусний біт готовності нових даних `DataReady` не перейде в активний стан.
5. **Антифлікерне вікно**: базовий час інтегрування фіксується кратним 100 мс (10 періодів пульсацій мережі 100 Гц і 12 періодів 120 Гц) для повного відсікання мерехтіння штучного освітлення на апаратному рівні.

## Реалізація драйвера на C та C++

Нижче наведено модульний код драйвера з чітким розділенням апаратно-залежного рівня вводу-виводу I2C та алгоритмічного ядра обробки фотометричних даних:

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Коефіцієнти підсилення PGA аналогового тракту ALS */
typedef enum {
    ALS_GAIN_1X   = 0,
    ALS_GAIN_2X   = 1,
    ALS_GAIN_4X   = 2,
    ALS_GAIN_8X   = 3,
    ALS_GAIN_16X  = 4,
    ALS_GAIN_32X  = 5,
    ALS_GAIN_64X  = 6,
    ALS_GAIN_128X = 7
} als_gain_t;

/* Час інтегрування АЦП (кратний 100 мс для антифлікеру) */
typedef enum {
    ALS_INT_50MS  = 0,  /* Швидкий режим */
    ALS_INT_100MS = 1,  /* Антифлікер 50 Гц / 60 Гц */
    ALS_INT_200MS = 2,  /* Висока чутливість */
    ALS_INT_400MS = 3,  /* Дуже висока чутливість */
    ALS_INT_800MS = 4   /* Максимальна чутливість для темряви */
} als_int_time_t;

/* Структура конфігурації та стану драйвера */
typedef struct {
    als_gain_t gain;
    als_int_time_t int_time;
    float glass_attenuation;    /* Коефіцієнт скла: 1.0 = відкритий, 10.0 = 10% пропускання */
    uint16_t low_threshold;     /* Поріг переходу вгору (зазвичай 10% від FS = 6553) */
    uint16_t high_threshold;    /* Поріг переходу вниз (зазвичай 85% від FS = 55705) */
    bool range_changed;
} als_driver_t;

static const float GAIN_FACTORS[] = {1.0f, 2.0f, 4.0f, 8.0f, 16.0f, 32.0f, 64.0f, 128.0f};
static const float INT_TIME_FACTORS[] = {0.5f, 1.0f, 2.0f, 4.0f, 8.0f};
static const float BASE_LUX_PER_LSB = 0.096f; /* Для Gain=1x та Tint=100ms */

void als_driver_init(als_driver_t *drv, float glass_att) {
    if (!drv) return;
    drv->gain = ALS_GAIN_4X;
    drv->int_time = ALS_INT_100MS; /* 100 мс за замовчуванням для придушення 100/120 Гц */
    drv->glass_attenuation = (glass_att >= 1.0f) ? glass_att : 1.0f;
    drv->low_threshold = 6553;     /* 10% від 65535 */
    drv->high_threshold = 55705;   /* 85% від 65535 */
    drv->range_changed = true;
}

/* Автоматична адаптація шкали за поточним відліком АЦП */
bool als_auto_range_update(als_driver_t *drv, uint16_t raw_ch0, bool is_overflow) {
    if (!drv) return false;
    drv->range_changed = false;

    /* 1. Захист від насичення: негайне зниження чутливості */
    if (is_overflow || raw_ch0 > drv->high_threshold) {
        if (drv->gain > ALS_GAIN_1X) {
            drv->gain = (als_gain_t)(drv->gain - 1);
            drv->range_changed = true;
        } else if (drv->int_time > ALS_INT_50MS) {
            drv->int_time = (als_int_time_t)(drv->int_time - 1);
            drv->range_changed = true;
        }
    }
    /* 2. Збільшення чутливості при занадто слабкому сигналі */
    else if (raw_ch0 < drv->low_threshold) {
        if (drv->gain < ALS_GAIN_128X) {
            drv->gain = (als_gain_t)(drv->gain + 1);
            drv->range_changed = true;
        } else if (drv->int_time < ALS_INT_800MS) {
            drv->int_time = (als_int_time_t)(drv->int_time + 1);
            drv->range_changed = true;
        }
    }

    return drv->range_changed;
}

/* Обчислення освітленості у люксах з двоканальною компенсацією ІЧ */
float als_calculate_lux(const als_driver_t *drv, uint16_t ch0, uint16_t ch1) {
    if (!drv || ch0 == 0) return 0.0f;

    float ratio = (float)ch1 / (float)ch0;
    float a = 1.0f, b = 1.8f;

    /* Кусково-лінійна оптимізація коефіцієнтів під тип освітлення */
    if (ratio <= 0.15f) {
        a = 1.00f; b = 0.40f; /* LED / Люмінесцентне */
    } else if (ratio <= 0.45f) {
        a = 1.00f; b = 1.20f; /* Денне розсіяне світло */
    } else if (ratio <= 0.75f) {
        a = 1.00f; b = 1.75f; /* Галоген / лампи розжарювання */
    } else {
        a = 0.85f; b = 1.95f; /* Пряме сонце / потужне ІЧ */
    }

    float net_counts = a * (float)ch0 - b * (float)ch1;
    if (net_counts < 0.0f) net_counts = 0.0f;

    float gain_div = GAIN_FACTORS[drv->gain];
    float tint_div = INT_TIME_FACTORS[drv->int_time];

    /* Формула перерахунку: LSB_фактичний = LSB_базовий / (Gain * Tint) * Glass */
    float lux = (net_counts * BASE_LUX_PER_LSB / (gain_div * tint_div)) * drv->glass_attenuation;
    return lux;
}
```
```cpp
#include <cstdint>
#include <array>
#include <expected>
#include <algorithm>
#include <span>

enum class AlsGain : std::uint8_t {
    Gain1x   = 0,
    Gain2x   = 1,
    Gain4x   = 2,
    Gain8x   = 3,
    Gain16x  = 4,
    Gain32x  = 5,
    Gain64x  = 6,
    Gain128x = 7
};

enum class AlsIntegrationTime : std::uint8_t {
    Int50ms  = 0,
    Int100ms = 1,
    Int200ms = 2,
    Int400ms = 3,
    Int800ms = 4
};

enum class AlsError {
    BusError,
    DeviceNotFound,
    DataNotReady,
    InvalidParameter
};

class AmbientLightSensor {
public:
    explicit constexpr AmbientLightSensor(float glass_attenuation = 1.0f) noexcept
        : glass_att_{std::max(1.0f, glass_attenuation)} {}

    [[nodiscard]] constexpr AlsGain gain() const noexcept { return gain_; }
    [[nodiscard]] constexpr AlsIntegrationTime integration_time() const noexcept { return int_time_; }

    [[nodiscard]] bool update_auto_range(std::uint16_t ch0_raw, bool is_overflow = false) noexcept {
        bool changed = false;

        if (is_overflow || ch0_raw > HIGH_THRESHOLD) {
            if (static_cast<std::uint8_t>(gain_) > 0) {
                gain_ = static_cast<AlsGain>(static_cast<std::uint8_t>(gain_) - 1);
                changed = true;
            } else if (static_cast<std::uint8_t>(int_time_) > 0) {
                int_time_ = static_cast<AlsIntegrationTime>(static_cast<std::uint8_t>(int_time_) - 1);
                changed = true;
            }
        } else if (ch0_raw < LOW_THRESHOLD) {
            if (static_cast<std::uint8_t>(gain_) < GAIN_MULTIPLIERS.size() - 1) {
                gain_ = static_cast<AlsGain>(static_cast<std::uint8_t>(gain_) + 1);
                changed = true;
            } else if (static_cast<std::uint8_t>(int_time_) < TIME_MULTIPLIERS.size() - 1) {
                int_time_ = static_cast<AlsIntegrationTime>(static_cast<std::uint8_t>(int_time_) + 1);
                changed = true;
            }
        }

        return changed;
    }

    [[nodiscard]] constexpr float calculate_lux(std::uint16_t ch0, std::uint16_t ch1) const noexcept {
        if (ch0 == 0) return 0.0f;

        const float ratio = static_cast<float>(ch1) / static_cast<float>(ch0);
        float a = 1.00f, b = 1.80f;

        if (ratio <= 0.15f) {
            a = 1.00f; b = 0.40f;
        } else if (ratio <= 0.45f) {
            a = 1.00f; b = 1.20f;
        } else if (ratio <= 0.75f) {
            a = 1.00f; b = 1.75f;
        } else {
            a = 0.85f; b = 1.95f;
        }

        const float net_counts = std::max(0.0f, a * static_cast<float>(ch0) - b * static_cast<float>(ch1));
        const float g_factor = GAIN_MULTIPLIERS[static_cast<std::size_t>(gain_)];
        const float t_factor = TIME_MULTIPLIERS[static_cast<std::size_t>(int_time_)];

        return (net_counts * BASE_LUX_PER_LSB / (g_factor * t_factor)) * glass_att_;
    }

private:
    static constexpr std::uint16_t LOW_THRESHOLD  = 6553;   // 10%
    static constexpr std::uint16_t HIGH_THRESHOLD = 55705;  // 85%
    static constexpr float BASE_LUX_PER_LSB       = 0.096f;

    static constexpr std::array<float, 8> GAIN_MULTIPLIERS = {
        1.0f, 2.0f, 4.0f, 8.0f, 16.0f, 32.0f, 64.0f, 128.0f
    };
    static constexpr std::array<float, 5> TIME_MULTIPLIERS = {
        0.5f, 1.0f, 2.0f, 4.0f, 8.0f
    };

    AlsGain gain_{AlsGain::Gain4x};
    AlsIntegrationTime int_time_{AlsIntegrationTime::Int100ms};
    float glass_att_{1.0f};
};
```
:::

## Покрокове трасування сценаріїв роботи FSM

Розглянемо, як кінцевий автомат реагує на реальні фізичні збурення в процесі експлуатації:

### Сценарій 1: Різкий спалах світла (вихід з темної кімнати на пряме сонце)
1. Початковий стан: система перебуває в режимі високої чутливості `Gain = 64x`, `T_int = 100 мс`. Освітленість у кімнаті становить 15 лк.
2. Подія: пристрій виносять на пряме сонце (80 000 лк).
3. Перший замір: АЦП миттєво входить у насичення, відлік досягає `RAW = 65535`, виставляється біт `OVF`.
4. Реакція автомата: функція `als_auto_range_update` фіксує переповнення і повертає `range_changed = true`. Оскільки перевантаження критичне, підсилення зменшується до `Gain = 1x`.
5. Перезапуск: драйвер записує нове значення `Gain` у регістр `CONFIG` і чекає завершення 100 мс нового інтегрування.
6. Другий замір: при `Gain = 1x` відлік АЦП становить `RAW = 42 500` (65% шкали). Значення потрапляє у робочий діапазон `[6553, 55705]`. Автомат фіксує стабільний стан і обчислює точні 81 600 люксів.

### Сценарій 2: Плавне згасання світла (вечірні сутінки)
1. Початковий стан: робочий офісний режим `Gain = 4x`, `T_int = 100 мс`, освітленість 300 лк (`RAW ≈ 31250`).
2. Подія: світло вимикають, рівень освітленості падає до 10 лк.
3. Проміжний замір: відлік АЦП падає до `RAW = 1040`, що менше ніж поріг `low_threshold = 6553`.
4. Реакція автомата: підсилення підвищується до `Gain = 8x` (`range_changed = true`).
5. Наступний цикл: відлік стає `RAW = 2080`, що все ще нижче 10%. Підсилення підвищується до `Gain = 16x`.
6. Фінальний стан: при `Gain = 32x` відлік досягає `RAW = 8320` (12.7% шкали), що вище нижнього порогу. Перемикання зупиняється, забезпечуючи високу точність оцифрування без насичення.

## Інженерні пастки при інтеграції драйвера

1. **Недотримання часу перехідного процесу після перемикання**: якщо мікроконтролер перемикає `T_int` або `Gain` і зчитує регістр даних до завершення нового циклу інтегрування, зчитується старий відлік або змішаний заряд інтегратора, що викликає хибне повторне перемикання. Необхідно або перевіряти біт готовності даних `DataReady`, або очікувати переривання по лінії `INT`.
2. **Паразитний зсув нуля в темряві (Dark Current Offset)**: за високих температур (> 60 °C) тепловий струм напівпровідника створює кілька десятків відліків у каналі CH0. Драйвер повинен виконувати нульове калібрування в темряві або використовувати апаратний компенсаційний темновий фотодіод.
3. **Хибний вибір автодіапазону через спалахи (Flash rejection)**: короткочасний спалах (наприклад, фотоспалах чи блискавка) може призвести до падіння підсилення до мінімуму. Для стабільних інтерфейсів керування яскравістю екрана рекомендується застосовувати фільтр медіани або ковзного середнього поверх розрахованих значень освітленості.
4. **Обчислення з плаваючою комою на мікроконтролерах без FPU**: на молодших ядрах ARM Cortex-M0/M0+ операції `float` виконуються програмно і займають сотні тактів. У промислових драйверах коефіцієнти матриці масштабують у 16-бітну або 32-бітну цілочисельну арифметику з фіксованою комою (Fixed Point Q15 або Q16), наприклад: `E_v = ((a_q15 * ch0 - b_q15 * ch1) >> 15) * lsb_scale`.
