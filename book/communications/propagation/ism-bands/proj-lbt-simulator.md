# ⚙️ Алгоритм Listen-Before-Talk (LBT) та контроль Duty Cycle у радіомодулі

У неліцензованому ISM-діапазоні хаотична одночасна передача багатьох пристроїв спричиняє руйнівні колізії, що вимагає практичної реалізації протоколу Listen-Before-Talk (LBT) та обліковця дозволеного робочого циклу (Duty Cycle) для жорсткого контролю випромінювання.

### Архітектура контролера випромінювання ISM-трансивера

У неліцензованому радіоефірі мікроконтролер не має права активувати підсилювач потужності (PA — *Power Amplifier*) трансивера наосліп. Пряма відправка даних без попередньої оцінки стану каналу призводить до руйнівних колізій із сусідніми вузлами та порушення регуляторного законодавства (зокрема норм ETSI EN 300 220 та FCC Part 15).

Перед виконанням кожної передачі програмне забезпечення здійснює дворівневу перевірку стану системи:
1. **Перевірка робочого циклу (Duty Cycle Guard):** Модуль аналізує накопичений час мовлення у поточному часовому вікні (наприклад, 1 година = 3600 секунд). Якщо пристрій вичерпав свій добовий чи погодинний бюджет мовлення (наприклад, 36 секунд для 1% Duty Cycle), передавач програмно блокується до завершення поточного вікна.
2. **Перевірка вільного каналу (LBT / CCA):** Приймач трансивера переводиться у режим вимірювання енергії ефіру (CCA — *Clear Channel Assessment*). Зчитується покроковий рівень RSSI (англ. *Received Signal Strength Indicator*) в обраному частотному каналі. Якщо рівень сигналу перевищує встановлений поріг завад (наприклад, `-85 dBm`), канал вважається зайнятим іншим пристроєм, і передача відкладається.

### Механізм випадкової паузи (Random Exponential Backoff)

Якщо перевірка LBT виявила зайнятий канал, пристрій не повинен повторювати спробу негайно: безупинне опитування ефіру витрачає енергію батареї та створює додаткове навантаження на мікроконтролер. Натомість реалізується алгоритм випадкової паузи:
* Пристрій обирає випадковий інтервал часу (Backoff Interval) у межах вікна конкуренції `[0, CW]`, де `CW` — поточний розмір вікна (Contention Window).
* Після кожної невдалої спроби розмір вікна `CW` подвоюється аж до досягнення `CW_max` (наприклад, від 16 мс до 1024 мс).
* Після завершення затримки процедура LBT повторюється. Якщо канал вільний, пакет негайно відправляється, а розмір вікна `CW` скидається до початкового значення `CW_min`.

### Робота з апаратними регістрами радіотрансивера

У реальних радіомодулях (таких як Semtech SX1261/SX1262, TI CC1101 або Microchip AT86RF212B) вимірювання RSSI здійснюється апаратно. Мікроконтролер по шині SPI відправляє команду початку вимірювання (наприклад, `SetRx()` чи `OpMode = RX`), чекає час встановлення синтезатора частот (t_synth ≈ 100–200 мкс), після чого зчитує значення з апаратного регістра `RSSI_REG`. Отримане сире значення перераховується у dBm за формулою з даташиту: `RSSI_dBm = -157 + RegisterValue`.

### Програмна реалізація контролера передачі

Нижче наведено ідіоматичну реалізацію контролера випромінювання для вбудованих систем на мовах C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

#define DUTY_CYCLE_LIMIT_MS 36000U  // 1% від 1 години (36 000 мс)
#define WINDOW_ONE_HOUR_MS   3600000U // 1 година в мілісекундах
#define RSSI_THRESHOLD_DBM   -85     // Поріг вільного каналу в dBm
#define LBT_SAMPLE_COUNT     5       // Кількість замірів RSSI

typedef struct {
    uint32_t total_tx_time_ms;
    uint32_t window_start_ms;
} duty_cycle_tracker_t;

// Ініціалізація трекера робочого циклу
void duty_cycle_init(duty_cycle_tracker_t *tracker, uint32_t current_time_ms) {
    tracker->total_tx_time_ms = 0;
    tracker->window_start_ms = current_time_ms;
}

// Оновлення часового вікна та перевірка доступності бюджету часу
bool duty_cycle_can_transmit(duty_cycle_tracker_t *tracker, uint32_t current_time_ms, uint32_t packet_toa_ms) {
    // Якщо минула година, скидаємо лічильник мовлення
    if (current_time_ms - tracker->window_start_ms >= WINDOW_ONE_HOUR_MS) {
        tracker->total_tx_time_ms = 0;
        tracker->window_start_ms = current_time_ms;
    }
    
    return (tracker->total_tx_time_ms + packet_toa_ms) <= DUTY_CYCLE_LIMIT_MS;
}

// Запис витраченого часу передачі
void duty_cycle_record_tx(duty_cycle_tracker_t *tracker, uint32_t packet_toa_ms) {
    tracker->total_tx_time_ms += packet_toa_ms;
}

// Симуляція вимірювання RSSI приймачем (у реальності — зчитування з регістру трансивера)
int16_t radio_read_rssi(void) {
    // Демонстраційне значення: -92 dBm (ефір вільний)
    return -92;
}

// Слухання ефіру перед передачею (Listen Before Talk)
bool lbt_is_channel_clear(int16_t threshold_dbm, uint8_t samples) {
    for (uint8_t i = 0; i < samples; i++) {
        int16_t rssi = radio_read_rssi();
        if (rssi > threshold_dbm) {
            return false; // Канал зайнятий іншим пристроєм
        }
    }
    return true; // Канал чистий
}

// Головна функція спроби передачі пакета
bool ism_transmit_packet(duty_cycle_tracker_t *tracker, uint32_t current_time_ms, uint32_t packet_toa_ms) {
    // 1. Перевірка обмеження Duty Cycle
    if (!duty_cycle_can_transmit(tracker, current_time_ms, packet_toa_ms)) {
        printf("[ISM Error] Перевищено ліміт Duty Cycle (1%%)! Передачу блоковано.\n");
        return false;
    }

    // 2. Перевірка чистоти ефіру за допомогою LBT
    if (!lbt_is_channel_clear(RSSI_THRESHOLD_DBM, LBT_SAMPLE_COUNT)) {
        printf("[ISM Warning] Канал зайнятий (LBT fail). Застосовуємо backoff.\n");
        return false;
    }

    // 3. Виконання передачі
    printf("[ISM Tx] Канал чистий. Передача пакета тривалістю %u мс...\n", packet_toa_ms);
    duty_cycle_record_tx(tracker, packet_toa_ms);
    printf("[ISM Status] Витрачено бюджету: %u / %u мс на годину.\n",
           tracker->total_tx_time_ms, DUTY_CYCLE_LIMIT_MS);
    
    return true;
}
```
```cpp
#include <iostream>
#include <cstdint>
#include <chrono>
#include <vector>

class IsmTransmissionController {
public:
    static constexpr uint32_t DutyCycleLimitMs = 36000;   // 1% на годину (36 000 мс)
    static constexpr uint32_t WindowOneHourMs   = 3600000; // 3 600 000 мс
    static constexpr int16_t  RssiThresholdDbm   = -85;     // дБм
    static constexpr uint8_t  LbtSampleCount     = 5;

    explicit IsmTransmissionController(uint32_t startTimeMs = 0)
        : totalTxTimeMs_(0), windowStartMs_(startTimeMs) {}

    bool canTransmit(uint32_t currentTimeMs, uint32_t packetToaMs) {
        updateWindow(currentTimeMs);
        return (totalTxTimeMs_ + packetToaMs) <= DutyCycleLimitMs;
    }

    bool transmitPacket(uint32_t currentTimeMs, uint32_t packetToaMs) {
        if (!canTransmit(currentTimeMs, packetToaMs)) {
            std::cout << "[ISM Error] Перевищено ліміт Duty Cycle (1%)! Передачу блоковано.\n";
            return false;
        }

        if (!isChannelClear()) {
            std::cout << "[ISM Warning] Канал зайнятий (LBT fail). Застосовуємо backoff.\n";
            return false;
        }

        std::cout << "[ISM Tx] Канал чистий. Передача пакета тривалістю " << packetToaMs << " мс...\n";
        totalTxTimeMs_ += packetToaMs;
        std::cout << "[ISM Status] Витрачено бюджету: " << totalTxTimeMs_
                  << " / " << DutyCycleLimitMs << " мс на годину.\n";
        return true;
    }

    [[nodiscard]] uint32_t getRemainingBudgetMs(uint32_t currentTimeMs) {
        updateWindow(currentTimeMs);
        return DutyCycleLimitMs > totalTxTimeMs_ ? (DutyCycleLimitMs - totalTxTimeMs_) : 0;
    }

private:
    uint32_t totalTxTimeMs_;
    uint32_t windowStartMs_;

    void updateWindow(uint32_t currentTimeMs) {
        if (currentTimeMs - windowStartMs_ >= WindowOneHourMs) {
            totalTxTimeMs_ = 0;
            windowStartMs_ = currentTimeMs;
        }
    }

    [[nodiscard]] int16_t readRssi() const {
        // Симуляція чистого ефіру (-92 дБм)
        return -92;
    }

    [[nodiscard]] bool isChannelClear() const {
        for (uint8_t i = 0; i < LbtSampleCount; ++i) {
            if (readRssi() > RssiThresholdDbm) {
                return false;
            }
        }
        return true;
    }
};
```
:::

### Потенційні підводні камені реалізації

* **Температурний дрейф калібрування RSSI:** Рівень фонового шуму пристрою залежить від температури навколишнього середовища. При зміні температури від -20°C до +60°C показання RSSI в тому самому ефірі можуть зміщуватися на 3–5 дБ. Помилкова настройка занадто низького порогу LBT призведе до того, що пристрій вважатиме вільний канал зайнятим і припинить передачу.
* **Затримка перемикання режимів (TX/RX Transition Time):** Апаратне перемикання трансивера з режиму зчитування LBT (RX) у режим передачі (TX) займає від 100 до 300 мікросекунд. За цей короткими час інший вузол в ефірі може успети почати мовлення, що спричинить колізію.
* **Сковзне вікно проти фіксованого:** Використання жорсткого фіксованого вікна тривалістю 1 година може спричинить сплеск випромінювання на межі двох годин (наприклад, 36 секунд передачі наприкінці першої години та одразу 36 секунд на початку другої). Для точної відповідності стандартам у промислових пристроях застосовують кільцевий буфер часових міток (Sliding Window Bucket).


### Динамічне управління робочим циклом за допомогою Leaky Bucket

У складних автономних системах замість жорсткого скидання лічильника раз на годину застосовують алгоритм «протікаючого відра» (Leaky Bucket). У цій моделі накопичений час мовлення списується не одномоментно, а безперервно зменшується зі швидкістю, пропорційною дозволеному відсотку Duty Cycle:

* Бюджетний накопичувач збільшується на тривалість кожної передачі `ToA`.
* У кожному такті часу (наприклад, щосекунди) вміст накопичувача зменшується на `0.01` секунди (для ліміту 1%).
* Якщо поточний рівень накопичувача плюс тривалість планованого пакета перевищує максимальну ємність `Capacity = 36 секунд`, передача блокується.

Такий підхід повністю усуває крайові сплески мовлення та забезпечує рівномірне навантаження на радіоефір протягом усієї доби.

### Управління апаратним перемикачем антени (RF Antenna Switch)

Під час виконання алгоритму LBT мікроконтролер повинен узгоджено керувати не лише регістрами трансивера, а й зовнішніми високовольтними або ВЧ-перемикачами антени (RF Switch, наприклад чіпами PE4259 чи SKY13317). 

Перед початком вимірювання RSSI мікроконтролер виставляє керувальний сигнал GPIO_RF_SW = LOW (підключення антени до входу приймача LNA). Якщо перевірка LBT пройшла успішно, мікроконтролер перемикає GPIO_RF_SW = HIGH (підключення антени до виходу підсилювача потужності PA) із обов'язковою витримкою затримки перемикання ВЧ-ключа 	_sw ≈ 2–5 мікросекунд. Недотримання цієї затримки призводить до того, що підсилювач потужності вмикається на розімкнене навантаження, викликаючи високий коефіцієнт стоячої хвилі по напрузі (КСВН / VSWR) та ризик пошкодження вихідного транзистора передавача.
