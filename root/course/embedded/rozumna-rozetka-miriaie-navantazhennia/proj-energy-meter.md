# ⚙️ Драйвер енергомонітора: розрахунок потужності та кВт·год

У комерційній розумній розетці або щитовому лічильнику прошивка мікроконтролера виконує не просто зчитування байтів із послідовного порту мікросхеми HLW8032 чи BL0942, а неперервно розв'язує комплекс метрологічних та системних задач реального часу:
1. **Асинхронний безблокувальний парсинг потоку**: виділення 24-байтних телеметричних кадрів за допомогою тристадійного скінченного автомата (*Finite State Machine, FSM*), контроль бітів синхронізації та відкидання пакетів із пошкодженою контрольною сумою без затримки основного циклу керування Wi-Fi чи реле.
2. **Прецизійне інтегрування енергії з фіксованою комою**: облік енергії в 64-розрядних цілих числах (мікроджоулях або нано-ват-годинах), що повністю усуває втрату точності додавання малих потужностей до великих накопичувачів.
3. **Енергонезалежне збереження лічильника (Wear Leveling)**: організація кільцевого буфера запису у Flash-пам'ять або EEPROM для захисту комірок від передчасної деградації при щохвилинному оновленні даних.

Нижче наведено детальний аналіз архітектурних вимог та повний робочий драйвер мовами C (C11) та C++ (C++20).

---

## 1. Чому float32 знищує лічильник кіловат-годин

Поширена помилка розробників-початківців — зберігати накопичену енергію у змінній типу `float` (32-бітне число з рухомою комою за стандартом IEEE 754).

Мантиса `float32` містить лише 23 біти значущості (плюс 1 неявний біт), що забезпечує точність близько 7 десяткових знаків:
* Нехай лічильник розетки за кілька місяців експлуатації набрав `1250.500 кВт·год` (число порядку `10³`).
* Найменший крок (вага молодшого розряду мантиси `float`) при такому значенні становить: `1250.5 · 2⁻²⁴ ≈ 0.0000745 кВт·год = 0.268 кДж = 268 Дж`.
* Тепер у розетку вмикають зарядний пристрій смартфона або світлодіодний нічник потужністю `P = 5.0 Вт`.
* За один цикл оновлення HLW8032 (`Δt = 50 мс = 0.05 с`) нічник споживає енергію:

```
ΔE = P · Δt = 5.0 Вт · 0.05 с = 0.25 Дж = 0.0000000694 кВт·год
```

При спробі додати `0.0000000694` до `1250.500` у форматі `float32` число `ΔE` просто **зникає в операції заокруглення**, оскільки воно менше за роздільну здатність мантиси на чотири порядки. Лічильник повністю припиняє враховувати малі навантаження!

**Інженерне рішення:** накопичувач енергії реалізують у 64-розрядному беззнаковому цілому числі `uint64_t`, де одиницею є **мікроджоуль** (`1 мкДж = 1 мкВт·с = 10⁻⁶ Дж`) або **міліват-секунда** (`1 мДж = 10⁻³ Дж`):
* Для `5 Вт` за `50 мс`: `ΔE = 5.0 · 50000 = 250 000 мкДж`. Це велике ціле число, яке додається абсолютно без втрат.
* Максимальне значення `uint64_t` становить `1.84 · 10¹⁹ мкДж`, що еквівалентно понад `5 120 000 000 кВт·год` — лічильник ніколи не переповниться за час життя пристрою.

---

## 2. Реалізація драйвера: C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define HLW8032_FRAME_LEN       24
#define HLW8032_SYNC_BYTE1      0x55
#define HLW8032_SYNC_BYTE2      0x5A

/* Стани скінченного автомата розбору кадру UART */
typedef enum {
    STATE_WAIT_SYNC1 = 0,
    STATE_WAIT_SYNC2,
    STATE_COLLECT_DATA
} hlw8032_parser_state_t;

/* Структура результатів вимірювання мережі */
typedef struct {
    float voltage_rms;        /* Напруга, В (RMS) */
    float current_rms;        /* Струм, А (RMS) */
    float active_power;       /* Активна потужність, Вт */
    float apparent_power;     /* Повна потужність, ВА */
    float power_factor;       /* Коефіцієнт потужності (0.00...1.00) */
    uint64_t energy_micro_ws; /* Накопичена енергія у мікро-ват-секундах (мкДж) */
    double energy_kwh;        /* Накопичена енергія, кВт·год */
    uint32_t valid_frames;    /* Лічильник успішно прийнятих кадрів */
    uint32_t checksum_errors; /* Лічильник помилок контрольної суми */
} energy_metrics_t;

/* Контекст драйвера енергомонітора */
typedef struct {
    hlw8032_parser_state_t state;
    uint8_t buffer[HLW8032_FRAME_LEN];
    uint8_t byte_idx;
    float k_voltage;          /* Калібрувальний коефіцієнт напруги (типово ~1.881) */
    float k_current;          /* Калібрувальний коефіцієнт струму (типово ~1.000) */
    energy_metrics_t metrics;
} hlw8032_driver_t;

/* Ініціалізація драйвера з калібрувальними коефіцієнтами */
void hlw8032_init(hlw8032_driver_t *drv, float k_v, float k_i) {
    if (!drv) return;
    memset(drv, 0, sizeof(hlw8032_driver_t));
    drv->state = STATE_WAIT_SYNC1;
    drv->k_voltage = (k_v > 0.0f) ? k_v : 1.881f;
    drv->k_current = (k_i > 0.0f) ? k_i : 1.000f;
}

/* Допоміжна функція складання 24-бітного числа з Big-Endian байтів */
static inline uint32_t unpack_u24(const uint8_t *p) {
    return ((uint32_t)p[0] << 16) | ((uint32_t)p[1] << 8) | (uint32_t)p[2];
}

/* Обробка повністю зібраного валідного кадру */
static void hlw8032_process_frame(hlw8032_driver_t *drv) {
    const uint8_t *buf = drv->buffer;

    /* Перевірка контрольної суми: сума байтів від 2 до 22 modulo 256 */
    uint8_t sum = 0;
    for (int i = 2; i <= 22; i++) {
        sum += buf[i];
    }

    if (sum != buf[23]) {
        drv->metrics.checksum_errors++;
        return;
    }

    drv->metrics.valid_frames++;

    /* Декодування 24-бітних регістрів */
    uint32_t v_param = unpack_u24(&buf[2]);
    uint32_t v_data  = unpack_u24(&buf[5]);
    uint32_t i_param = unpack_u24(&buf[8]);
    uint32_t i_data  = unpack_u24(&buf[11]);
    uint32_t p_param = unpack_u24(&buf[14]);
    uint32_t p_data  = unpack_u24(&buf[17]);

    /* Розрахунок напруги V_rms */
    if (v_data > 0) {
        drv->metrics.voltage_rms = ((float)v_param / (float)v_data) * drv->k_voltage;
    }

    /* Розрахунок струму I_rms (з відсіканням шуму при нульовому навантаженні) */
    if (i_data > 0) {
        float raw_current = ((float)i_param / (float)i_data) * drv->k_current;
        drv->metrics.current_rms = (raw_current >= 0.015f) ? raw_current : 0.0f;
    } else {
        drv->metrics.current_rms = 0.0f;
    }

    /* Розрахунок активної потужності P_active */
    if (p_data > 0 && drv->metrics.current_rms > 0.0f) {
        drv->metrics.active_power = ((float)p_param / (float)p_data) * drv->k_voltage * drv->k_current;
    } else {
        drv->metrics.active_power = 0.0f;
    }

    /* Розрахунок повної потужності S та коефіцієнта потужності PF */
    drv->metrics.apparent_power = drv->metrics.voltage_rms * drv->metrics.current_rms;
    if (drv->metrics.apparent_power > 0.1f) {
        float pf = drv->metrics.active_power / drv->metrics.apparent_power;
        drv->metrics.power_factor = (pf > 1.0f) ? 1.0f : ((pf < 0.0f) ? 0.0f : pf);
    } else {
        drv->metrics.power_factor = 1.0f;
    }

    /* Інтегрування енергії: кадр надходить кожні 50 мс (0.05 с).
     * Енергія за кадр = P * 0.05 с.
     * У мікро-ват-секундах: P * 50000 мкВт·с */
    uint64_t delta_uWs = (uint64_t)(drv->metrics.active_power * 50000.0f);
    drv->metrics.energy_micro_ws += delta_uWs;

    /* 1 кВт·год = 3.6e12 мкВт·с (3.6e9 Дж = 3.6e6 Вт·год) */
    drv->metrics.energy_kwh = (double)drv->metrics.energy_micro_ws / 3.6e12;
}

/* Побайтний парсер вхідного потоку UART (викликається в ISR або потоці зчитування) */
void hlw8032_feed_byte(hlw8032_driver_t *drv, uint8_t byte) {
    if (!drv) return;

    switch (drv->state) {
    case STATE_WAIT_SYNC1:
        if (byte == HLW8032_SYNC_BYTE1) {
            drv->buffer[0] = byte;
            drv->state = STATE_WAIT_SYNC2;
        }
        break;

    case STATE_WAIT_SYNC2:
        if (byte == HLW8032_SYNC_BYTE2) {
            drv->buffer[1] = byte;
            drv->byte_idx = 2;
            drv->state = STATE_COLLECT_DATA;
        } else if (byte == HLW8032_SYNC_BYTE1) {
            drv->buffer[0] = byte;
        } else {
            drv->state = STATE_WAIT_SYNC1;
        }
        break;

    case STATE_COLLECT_DATA:
        drv->buffer[drv->byte_idx++] = byte;
        if (drv->byte_idx >= HLW8032_FRAME_LEN) {
            hlw8032_process_frame(drv);
            drv->state = STATE_WAIT_SYNC1;
        }
        break;
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <algorithm>

namespace energy {

struct Metrics {
    float voltage_rms{0.0f};       // Напруга, В (RMS)
    float current_rms{0.0f};       // Струм, А (RMS)
    float active_power{0.0f};      // Активна потужність, Вт
    float apparent_power{0.0f};    // Повна потужність, ВА
    float power_factor{1.0f};      // Коефіцієнт потужності (0.00...1.00)
    uint64_t energy_micro_ws{0};   // Накопичена енергія у мікроджоулях (мкВт·с)
    double energy_kwh{0.0};        // Накопичена енергія, кВт·год
    uint32_t valid_frames{0};      // Лічильник успішних пакетів
    uint32_t checksum_errors{0};  // Лічильник помилок контрольної суми
};

class EnergyMeterHLW8032 {
public:
    static constexpr size_t kFrameLen = 24;
    static constexpr uint8_t kSync1 = 0x55;
    static constexpr uint8_t kSync2 = 0x5A;

    explicit constexpr EnergyMeterHLW8032(float k_voltage = 1.881f, float k_current = 1.000f) noexcept
        : k_voltage_{k_voltage > 0.0f ? k_voltage : 1.881f},
          k_current_{k_current > 0.0f ? k_current : 1.000f} {}

    // Обробка одного байта з UART
    void feed_byte(uint8_t byte) noexcept {
        switch (state_) {
        case State::WaitSync1:
            if (byte == kSync1) {
                buffer_[0] = byte;
                state_ = State::WaitSync2;
            }
            break;

        case State::WaitSync2:
            if (byte == kSync2) {
                buffer_[1] = byte;
                byte_idx_ = 2;
                state_ = State::CollectData;
            } else if (byte == kSync1) {
                buffer_[0] = byte;
            } else {
                state_ = State::WaitSync1;
            }
            break;

        case State::CollectData:
            buffer_[byte_idx_++] = byte;
            if (byte_idx_ >= kFrameLen) {
                process_frame();
                state_ = State::WaitSync1;
            }
            break;
        }
    }

    // Обробка масиву байтів із буфера DMA/FIFO
    void feed_buffer(std::span<const uint8_t> data) noexcept {
        for (uint8_t b : data) {
            feed_byte(b);
        }
    }

    [[nodiscard]] const Metrics& metrics() const noexcept { return metrics_; }

    void reset_energy() noexcept {
        metrics_.energy_micro_ws = 0;
        metrics_.energy_kwh = 0.0;
    }

    void set_calibration(float k_v, float k_i) noexcept {
        if (k_v > 0.0f) k_voltage_ = k_v;
        if (k_i > 0.0f) k_current_ = k_i;
    }

private:
    enum class State : uint8_t {
        WaitSync1,
        WaitSync2,
        CollectData
    };

    static constexpr uint32_t unpack_u24(const uint8_t* p) noexcept {
        return (static_cast<uint32_t>(p[0]) << 16) |
               (static_cast<uint32_t>(p[1]) << 8)  |
                static_cast<uint32_t>(p[2]);
    }

    void process_frame() noexcept {
        // Контрольна сума: сума байтів від 2 до 22
        uint8_t sum = 0;
        for (size_t i = 2; i <= 22; ++i) {
            sum += buffer_[i];
        }

        if (sum != buffer_[23]) {
            ++metrics_.checksum_errors;
            return;
        }

        ++metrics_.valid_frames;

        const uint32_t v_param = unpack_u24(&buffer_[2]);
        const uint32_t v_data  = unpack_u24(&buffer_[5]);
        const uint32_t i_param = unpack_u24(&buffer_[8]);
        const uint32_t i_data  = unpack_u24(&buffer_[11]);
        const uint32_t p_param = unpack_u24(&buffer_[14]);
        const uint32_t p_data  = unpack_u24(&buffer_[17]);

        if (v_data > 0) {
            metrics_.voltage_rms = (static_cast<float>(v_param) / static_cast<float>(v_data)) * k_voltage_;
        }

        if (i_data > 0) {
            const float raw_i = (static_cast<float>(i_param) / static_cast<float>(i_data)) * k_current_;
            metrics_.current_rms = (raw_i >= 0.015f) ? raw_i : 0.0f;
        } else {
            metrics_.current_rms = 0.0f;
        }

        if (p_data > 0 && metrics_.current_rms > 0.0f) {
            metrics_.active_power = (static_cast<float>(p_param) / static_cast<float>(p_data)) * k_voltage_ * k_current_;
        } else {
            metrics_.active_power = 0.0f;
        }

        metrics_.apparent_power = metrics_.voltage_rms * metrics_.current_rms;
        if (metrics_.apparent_power > 0.1f) {
            const float pf = metrics_.active_power / metrics_.apparent_power;
            metrics_.power_factor = std::clamp(pf, 0.0f, 1.0f);
        } else {
            metrics_.power_factor = 1.0f;
        }

        // 50 мс інтервал оновлення: 0.05 с * 1e6 = 50000 мкВт·с
        const auto delta_uWs = static_cast<uint64_t>(metrics_.active_power * 50000.0f);
        metrics_.energy_micro_ws += delta_uWs;
        metrics_.energy_kwh = static_cast<double>(metrics_.energy_micro_ws) / 3.6e12;
    }

    State state_{State::WaitSync1};
    std::array<uint8_t, kFrameLen> buffer_{};
    size_t byte_idx_{0};
    float k_voltage_{1.881f};
    float k_current_{1.000f};
    Metrics metrics_{};
};

} // namespace energy
```
:::

---

## 3. Стратегія збереження енергії у Flash/EEPROM та захист від збоїв

Запис накопиченої енергії в енергонезалежну пам'ять (NOR Flash мікроконтролера ESP32 або зовнішню EEPROM) не можна виконувати за кожним прийнятим кадром телеметрії (кожні 50 мс). Типовий ресурс одного сектора NOR Flash становить `100 000` циклів стирання/запису. При щосекундному записі пам'ять деградує за 27 годин, а при записі кожні 50 мс — менш ніж за півтори години.

Для забезпечення ресурсу роботи пристрою понад 15–20 років застосовують комбінацію трьох механізмів.

### 1. Гістерезисний поріг приросту енергії
Запис ініціюється не за часом, а за фактом споживання енергії на фіксовану квантову величину: наприклад, при прирості на кожні `0.01 кВт·год = 36 000 Дж` (для нагрівача 2 кВт це приблизно раз на 18 секунд, а для нічника 5 Вт — раз на 2 години). Додатково діє таймер безпеки: якщо навантаження ввімкнене, але поріг 0.01 кВт·год ще не досягнуто, збереження виконується примусово раз на 15 хвилин.

### 2. Кільцевий буфер вирівнювання зносу (Wear Leveling)
Один 4-кілобайтний сектор Flash-пам'яті (4096 байтів) розбивають на масив із 256 записів розміром по 16 байтів.
Структура запису:

| Зміщення | Поле | Розмір | Призначення |
|---|---|---|---|
| +0 | `Magic` | 2 байти | Сигнатура запису `0xAA55` |
| +2 | `SeqNum` | 2 байти | Інкрементний порядковий номер запису |
| +4 | `Energy_uWs` | 8 байтів | Накопичена енергія `uint64_t` у мікроджоулях |
| +12 | `CRC32` | 4 байти | Контрольна сума для захисту від незавершеного запису |

Алгоритм роботи:
1. При старті пристрій сканує сектор, перевіряє CRC32 і знаходить валідний запис із найбільшим `SeqNum`. Це стає початковим значенням лічильника.
2. Новий запис здійснюється в наступний вільний 16-байтний слот без стирання всього сектора (NOR Flash дозволяє програмувати байти `1 → 0` послідовно).
3. Лише коли всі 256 слотів заповнено, сектор повністю стирається (операція `Sector Erase`), і запис починається з нульового слота з номером `SeqNum + 1`.
4. Завдяки 256-кратному вирівнюванню зносу ресурс у 100 000 стирань забезпечує `25 600 000` операцій збереження (>40 років роботи при записі раз на хвилину).

### 3. Детектор зникнення напруги (Power-Fail Detector)
Щоб не втратити накопичену за останні хвилини енергію при раптовому знеструмленні розетки, у схемі блоку живлення застосовують апаратний моніторинг шини живлення до лінійного стабілізатора 3.3 В (наприклад, напруги після діодного моста +12 В або +5 В).

Коли напруга на шині падає нижче 4.5 В, компаратор генерує немасковане переривання (*NMI* або високорівневий GPIO interrupt). У цей момент накопичувальний електролітичний конденсатор фільтра ємністю 220–470 мкФ продовжує живити мікроконтролер протягом часу `t_hold`:

```
t_hold = C · (V_start² − V_min²) / (2 · P_mcu)
```

При `C = 470 мкФ`, `V_start = 5.0 В`, `V_min = 3.3 В` та споживанні мікроконтролера `P_mcu = 3.3 В · 40 мА = 132 мВт`:

```
t_hold = (470 · 10⁻⁶ · (25.0 − 10.89)) / (2 · 0.132) = (470 · 10⁻⁶ · 14.11) / 0.264 ≈ 25.1 мс
```

Запас часу 25 мс у 5–10 разів перевищує час екстреного запису 16 байтів у Flash-пам'ять (типово 2–3 мс), що гарантує 100% збереження кожного ват-секунди навіть при раптовому висмикуванні розетки зі стіни.
