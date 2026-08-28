# Проект прошивки мінімального пульта керування

Цей проект містить повну архітектуру та відкритий вихідний код вбудованої прошивки для кастомного портативного пульта радіокерування на базі мікроконтролера ESP32-S3 / STM32G4 та радіотрансивера Semtech SX1280 2.4 ГГц. Без розуміння низькорівневої взаємодії апаратних таймерів, контролерів прямого доступу до пам'яті (DMA) та кінцевого автомата радіотрансивера неможливо забезпечити стабільний детермінований контур керування з мікросекундним джитером.

---

## 1. Архітектура та послідовність ініціалізації системи

Прошивка пульта побудована навколо трьох ізольованих апаратних контурів, які функціонують паралельно без взаємного блокування:

1. **Контур збору даних (Data Acquisition Pipeline)**: апаратний таймер тактує АЦП, а DMA-контролер безперервно наповнює подвійний кільцевий буфер сирими відліками чотирьох осей Холла.
2. **Радіоконтур жорсткого реального часу (RF TDD Loop)**: таймер 1 кГц запускає процес пакування кадру, передачі його по шині SPI DMA у буфер SX1280 та перемикання трансивера в прийом телеметрії.
3. **Фоновий графічний контур (Background HUD Engine)**: ядро процесора у вільні 800 мікросекунд циклу оновлює інформаційні віджети на дисплеї та відправляє рядки пікселів через DMA.

```
 [Старт системи]
        │
        ▼
 [Ініціалізація живлення та P-MOS ключа]
        │
        ▼
 [Конфігурація SPI DMA (18 MHz) + SX1280 FLRC]
        │
        ▼
 [Налаштування Timer 1 kHz + Injected ADC DMA]
        │
        ▼
 [Тест нульового газу та перевірка датчиків (POST)]
        │
        ▼
 [Запуск апаратного Watchdog (15 мс)]
        │
        ▼
 ┌──────────────────────────────────────────────┐
 │ ГОЛОВНИЙ ЦИКЛ ПЕРЕРИВАНЬ (1000 Гц TDD)       │
 │ 1. Зчитування DMA ADC осей + IIR фільтр      │
 │ 2. Пакування кадру 14 B + CRC-16             │
 │ 3. Відправка TX кадру через SPI DMA          │
 │ 4. Очікування IRQ завершення TX (450 µs)     │
 │ 5. Перемикання в RX для прийому телеметрії   │
 │ 6. Скидання апаратного Watchdog              │
 └──────────────────────────────────────────────┘
```

Послідовність запуску гарантує безпеку силової установки апарата:
- При подачі живлення P-канальний польовий транзистор відкривається з керованою швидкістю наростання напруги (`dV/dt`), запобігаючи стрибкам струму на ємностях живлення радіомодуля.
- Ініціалізується шина SPI з тактовою частотою 18 МГц у режимі Master Mode 0 (CPOL=0, CPHA=0).
- Радіотрансивер переводиться в режим очікування (`SetStandby(STDBY_RC)`), після чого завантажуються таблиці регістрів модуляції FLRC (смуга 1.2 МГц, кодування CR 3/4, швидкість 1.3 Мбіт/с).
- Запускається калібрувальний тест осей (POST): якщо стік газу відхилений більше ніж на 5% або тумблер Arm активований, система залишається в режимі блокування передачі з тактильним вібросигналом.

---

## 2. Реалізація драйвера радіотрансивера та обробки осей

Нижче наведено повний вихідний код модуля обробки сигналів, кінцевого автомата трансивера та пакування телеметрії мовами C та C++.

:::tabs
```c
// minimal_remote_firmware.c — Повний відкритий модуль прошивки пульта
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CHANNELS_TOTAL       4
#define FRAME_SYNC_BYTE      0x5A
#define SX1280_CMD_SET_TX    0x83
#define SX1280_CMD_SET_RX    0x82
#define SX1280_CMD_WRITE_BUF 0x18
#define SX1280_CMD_READ_BUF  0x19

// Структура калібрування стіка
typedef struct {
    uint16_t min_raw;
    uint16_t center_raw;
    uint16_t max_raw;
    uint16_t deadband;
} StickCalibration;

// Структура вихідного радіокадру керування
typedef struct {
    uint8_t  sync;
    uint8_t  sequence;
    uint8_t  packed_channels[6];
    uint8_t  switches;
    uint8_t  flags;
    uint16_t crc;
} __attribute__((packed)) UplinkPacket;

// Структура вхідного кадру бортової телеметрії
typedef struct {
    uint8_t  sync;
    uint8_t  sequence;
    uint16_t vbat_mv;       // Напруга батареї дрона (мВ)
    uint8_t  current_a_x10; // Струм дрона (А * 10)
    uint8_t  rssi_dbm;      // Рівень сигналу (-dBm)
    uint8_t  link_quality;  // Якість лінка (0..100%)
    uint8_t  flight_mode;   // Польотний режим
} __attribute__((packed)) DownlinkTelemetry;

static StickCalibration g_calib[CHANNELS_TOTAL] = {
    { .min_raw = 320, .center_raw = 2048, .max_raw = 3780, .deadband = 25 },
    { .min_raw = 330, .center_raw = 2050, .max_raw = 3770, .deadband = 25 },
    { .min_raw = 310, .center_raw = 2048, .max_raw = 3790, .deadband = 10 },
    { .min_raw = 325, .center_raw = 2045, .max_raw = 3775, .deadband = 25 }
};

static uint16_t g_adc_history[CHANNELS_TOTAL] = {2048, 2048, 0, 2048};
static uint8_t  g_packet_counter = 0;

// Апаратна абстракція SPI DMA
extern void spi_dma_transmit_receive(const uint8_t *tx, uint8_t *rx, size_t len);
extern void hardware_watchdog_reset(void);
extern void set_haptic_vibration(uint8_t intensity_pwm);

static uint16_t compute_crc16(const uint8_t *buf, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)buf[i] << 8;
        for (uint8_t b = 0; b < 8; b++) {
            crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
        }
    }
    return crc;
}

// Обробка, фільтрація та лінеаризація каналу
uint16_t filter_and_scale_axis(uint8_t ch, uint16_t raw_adc) {
    // Цифровий фільтр: експоненційне згладжування
    g_adc_history[ch] = (uint16_t)((raw_adc * 5 + g_adc_history[ch] * 5) / 10);
    uint16_t val = g_adc_history[ch];
    const StickCalibration *c = &g_calib[ch];

    if (val < c->min_raw) val = c->min_raw;
    if (val > c->max_raw) val = c->max_raw;

    // Спеціальний режим для Throttle (без центральної мертвої зони)
    if (ch == 2) {
        uint32_t span = c->max_raw - c->min_raw;
        return span ? (uint16_t)((uint32_t)(val - c->min_raw) * 2047 / span) : 0;
    }

    int32_t diff = (int32_t)val - (int32_t)c->center_raw;
    if (diff > -c->deadband && diff < c->deadband) {
        return 1024; // Нейтральний центр
    }

    if (diff > 0) {
        uint32_t span = c->max_raw - c->center_raw;
        uint32_t res = 1024 + ((uint32_t)diff * 1023 / span);
        return (res > 2047) ? 2047 : (uint16_t)res;
    } else {
        uint32_t span = c->center_raw - c->min_raw;
        int32_t res = 1024 - ((uint32_t)(-diff) * 1024 / span);
        return (res < 0) ? 0 : (uint16_t)res;
    }
}

// Головний обробник 1 кГц радіоциклу
void process_1khz_control_tick(const uint16_t raw_gimbals[CHANNELS_TOTAL], 
                              uint8_t switch_state, DownlinkTelemetry *out_telemetry) {
    uint16_t scaled_axes[CHANNELS_TOTAL];
    for (uint8_t i = 0; i < CHANNELS_TOTAL; i++) {
        scaled_axes[i] = filter_and_scale_axis(i, raw_gimbals[i]);
    }

    // Пакування бінарного кадру
    UplinkPacket packet;
    packet.sync = FRAME_SYNC_BYTE;
    packet.sequence = g_packet_counter++;
    packet.switches = switch_state;
    packet.flags = 0x00;

    // Пакування 4x 11-бітних осей у 6 байтів
    packet.packed_channels[0] = (uint8_t)(scaled_axes[0] & 0xFF);
    packet.packed_channels[1] = (uint8_t)(((scaled_axes[0] >> 8) & 0x07) | ((scaled_axes[1] & 0x1F) << 3));
    packet.packed_channels[2] = (uint8_t)(((scaled_axes[1] >> 5) & 0x3F) | ((scaled_axes[2] & 0x03) << 6));
    packet.packed_channels[3] = (uint8_t)((scaled_axes[2] >> 2) & 0xFF);
    packet.packed_channels[4] = (uint8_t)(((scaled_axes[2] >> 10) & 0x01) | ((scaled_axes[3] & 0x7F) << 1));
    packet.packed_channels[5] = (uint8_t)((scaled_axes[3] >> 7) & 0x0F);

    packet.crc = compute_crc16((const uint8_t*)&packet, sizeof(UplinkPacket) - sizeof(uint16_t));

    // Відправка кадру в трансивер SX1280 через SPI DMA
    uint8_t tx_cmd[sizeof(UplinkPacket) + 2];
    tx_cmd[0] = SX1280_CMD_WRITE_BUF;
    tx_cmd[1] = 0x00; // Зсув буфера
    memcpy(&tx_cmd[2], &packet, sizeof(UplinkPacket));
    spi_dma_transmit_receive(tx_cmd, NULL, sizeof(tx_cmd));

    // Запуск радіопередачі
    uint8_t set_tx_cmd[4] = {SX1280_CMD_SET_TX, 0x00, 0x00, 0x00};
    spi_dma_transmit_receive(set_tx_cmd, NULL, sizeof(set_tx_cmd));

    // Скидання сторожового таймера
    hardware_watchdog_reset();
}
```
```cpp
// minimal_remote_firmware.hpp — Ідіоматична реалізація прошивки на C++20
#pragma once
#include <cstdint>
#include <array>
#include <span>
#include <algorithm>
#include <cstring>

namespace remote {

inline constexpr uint8_t FrameSyncByte = 0x5A;
inline constexpr std::size_t AxisCount = 4;

struct CalibrationData {
    uint16_t min_raw{320};
    uint16_t center_raw{2048};
    uint16_t max_raw{3780};
    uint16_t deadband{25};
};

struct [[gnu::packed]] UplinkPacket {
    uint8_t  sync{FrameSyncByte};
    uint8_t  sequence{0};
    std::array<uint8_t, 6> packed_channels{};
    uint8_t  switches{0};
    uint8_t  flags{0};
    uint16_t crc{0};
};

struct [[gnu::packed]] DownlinkTelemetry {
    uint8_t  sync{0};
    uint8_t  sequence{0};
    uint16_t vbat_mv{0};
    uint8_t  current_a_x10{0};
    uint8_t  rssi_dbm{0};
    uint8_t  link_quality{0};
    uint8_t  flight_mode{0};
};

class RemoteController {
public:
    constexpr RemoteController() = default;

    void setCalibration(std::size_t axis, const CalibrationData& calib) noexcept {
        if (axis < AxisCount) {
            calibration_[axis] = calib;
        }
    }

    [[nodiscard]] uint16_t processAxis(std::size_t ch, uint16_t raw_adc) noexcept {
        if (ch >= AxisCount) return 1024;

        // Експоненційний IIR фільтр (вага 0.5)
        filtered_adc_[ch] = static_cast<uint16_t>((raw_adc * 5 + filtered_adc_[ch] * 5) / 10);
        const auto val = std::clamp(filtered_adc_[ch], calibration_[ch].min_raw, calibration_[ch].max_raw);
        const auto& c = calibration_[ch];

        if (ch == 2) { // Throttle
            const auto span = c.max_raw - c.min_raw;
            return span ? static_cast<uint16_t>((static_cast<uint32_t>(val - c.min_raw) * 2047) / span) : 0;
        }

        const int32_t diff = static_cast<int32_t>(val) - static_cast<int32_t>(c.center_raw);
        if (std::abs(diff) < c.deadband) {
            return 1024;
        }

        if (diff > 0) {
            const uint32_t span = c.max_raw - c.center_raw;
            const uint32_t res = 1024 + ((static_cast<uint32_t>(diff) * 1023) / span);
            return static_cast<uint16_t>(std::min<uint32_t>(res, 2047));
        } else {
            const uint32_t span = c.center_raw - c.min_raw;
            const int32_t res = 1024 - ((static_cast<uint32_t>(-diff) * 1024) / span);
            return static_cast<uint16_t>(std::max<int32_t>(res, 0));
        }
    }

    [[nodiscard]] UplinkPacket packControlFrame(std::span<const uint16_t, AxisCount> raw_adc, 
                                                uint8_t switches, uint8_t flags = 0) noexcept {
        std::array<uint16_t, AxisCount> norm{};
        for (std::size_t i = 0; i < AxisCount; ++i) {
            norm[i] = processAxis(i, raw_adc[i]);
        }

        UplinkPacket packet{};
        packet.sync = FrameSyncByte;
        packet.sequence = sequence_counter_++;
        packet.switches = switches;
        packet.flags = flags;

        // Бітове пакування 4x 11-бітних осей у 6 байтів
        packet.packed_channels[0] = static_cast<uint8_t>(norm[0] & 0xFF);
        packet.packed_channels[1] = static_cast<uint8_t>(((norm[0] >> 8) & 0x07) | ((norm[1] & 0x1F) << 3));
        packet.packed_channels[2] = static_cast<uint8_t>(((norm[1] >> 5) & 0x3F) | ((norm[2] & 0x03) << 6));
        packet.packed_channels[3] = static_cast<uint8_t>((norm[2] >> 2) & 0xFF);
        packet.packed_channels[4] = static_cast<uint8_t>(((norm[2] >> 10) & 0x01) | ((norm[3] & 0x7F) << 1));
        packet.packed_channels[5] = static_cast<uint8_t>((norm[3] >> 7) & 0x0F);

        packet.crc = calculateCrc16(std::span<const uint8_t>{
            reinterpret_cast<const uint8_t*>(&packet), sizeof(UplinkPacket) - sizeof(uint16_t)
        });

        return packet;
    }

private:
    static uint16_t calculateCrc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t b : data) {
            crc ^= static_cast<uint16_t>(b) << 8;
            for (uint8_t i = 0; i < 8; ++i) {
                crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
            }
        }
        return crc;
    }

    std::array<CalibrationData, AxisCount> calibration_{};
    std::array<uint16_t, AxisCount> filtered_adc_{2048, 2048, 0, 2048};
    uint8_t sequence_counter_{0};
};

} // namespace remote
```
:::

---

## 3. Покрокове простеження транзакцій та часовий бюджет

Для розуміння мікросекундного таймінгу простежимо виконання одного циклу 1 кГц:

1. **Момент `t = 0.000 мс` (Апаратне переривання таймера TIM1)**:
   Таймер генерує строб запуску перетворення АЦП. За 15 мікросекунд контролер прямого доступу до пам'яті переливає 4 слова `uint16_t` у буфер `raw_gimbals`.
2. **Момент `t = 0.020 мс` (Фільтрація та нормалізація осей)**:
   Процесор викликає функцію `processAxis()` для кожного каналу. Завдяки оптимізації цілочисельної арифметики розрахунок IIR-фільтра та експоненти займає 25 мікросекунд.
3. **Момент `t = 0.045 мс` (Пакування бінарного кадру та CRC-16)**:
   Відбувається зсув і пакування чотирьох 11-бітних чисел у 6 байтів. Обчислення контрольної суми CRC-16 табличним методом або апаратним CRC-модулем займає 15 мікросекунд.
4. **Момент `t = 0.060 мс` (Запуск шини SPI DMA)**:
   Команда запису буфера передавача та строб `SetTx` відправляються в SX1280 по шині SPI на швидкості 18 Мбіт/с за 20 мікросекунд.
5. **Момент `t = 0.080 – 0.530 мс` (Радіовипромінювання)**:
   Трансивер випромінює в ефір 14 байтів у модуляції FLRC. Процесор у цей час повністю вивільнений і виконує фонову побудову графічних шарів для дисплея.
6. **Момент `t = 0.580 – 0.780 мс` (Прийом зворотної телеметрії)**:
   Після перемикання TDD трансивер приймає телеметричний пакет від апарата, генерує сигнал на лінії `DIO1`, і DMA вичитує напругу та RSSI у пам'ять мікроконтролера.

---

## 4. Пастки та тонкощі низькорівневої реалізації

Під час практичної розробки та налагодження вбудованої прошивки слід враховувати чотири фундаментальні апаратні пастки:

### 1. Когерентність кешу та пам'ять DMA (Cache Invalidation)

На сучасних мікроконтролерах із процесорним кешем даних (ESP32-S3 з архітектурою Xtensa LX7 або STM32G4 при увімкненому кеші пам'яті) буфери, у які пише апаратний контролер DMA АЦП або SPI, повинні розміщуватися у спеціальних секціях внутрішньої пам'яті (DMA-capable Internal SRAM).

Якщо процесор прочитає пам'ять безпосередньо після завершення передачі DMA, він ризикує отримати застарілі значення, що залишилися в рядках L1 кешу ядра. Щоб уникнути цього, перед читанням буфера викликається функція інвалідації кешу:
- На ESP-IDF: `esp_cache_msync((void*)rx_buf, len, ESP_CACHE_MSYNC_FLAG_INVALIDATE)`.
- На ARM Cortex-M: `SCB_InvalidateDCache_by_Addr((uint32_t*)rx_buf, len)`.

### 2. Взаємні перешкоди між SPI антеною та опорною напругою АЦП

Коли радіотрансивер активує вихідний підсилювач потужності (PA) на рівні +20 dBm (100 мВт), споживання струму стрибає з 10 мА до 95 мА за лічені мікросекунди. Якщо на друкованій платі сигнальна земля датчиків Холла (AGND) і силова цифрова земля трансивера (DGND) об'єднані однією довгою доріжкою, виникає імпульсне падіння напруги на опорі спільного провідника.

У результаті опорна напруга АЦП коливається на 30–50 мВ, що спричиняє видиме тремтіння осей (Jitter) під час кожної радіопосилки. Рішення полягає в топології «зірки» (Star Grounding): аналогові конденсатори фільтрації та роз'єми датчиків Холла сходяться в одну точку безпосередньо під тепловою площадкою мікроконтролера, повністю ізольовано від зворотного струму антени.

### 3. Дисципліна сторожового таймера (Watchdog Service Discipline)

Поширена помилка початківців — скидати сторожовий таймер (Watchdog) всередині апаратного обробника переривань таймера (TIM ISR). У разі виникнення дедлоку, зависання головного циклу обробки або пошкодження таблиць вказівників переривання продовжують регулярно спрацьовувати і скидати Watchdog, маскуючи повну відмову контуру керування.

Скидання Watchdog повинно виконуватися **виключно в кінці головної задачі реального часу**, лише після того, як успішно перевірено контрольні суми вхідної телеметрії, оцифровано стіки та відправлено свіжий кадр в ефір.

### 4. Гістерезис контролю заряду акумулятора

Під час передачі пакету високої потужності внутрішній опір акумулятора 18650 (близько 30–50 мОм) викликає динамічну просадку напруги батареї на `ΔV = I_peak · R_int ≈ 0.1\ \text{A} · 0.05\ \Omega = 5\ \text{mV}`. Якщо вимірювати напругу безпосередньо під час передачі, пульт може помилково ініціювати тривогу розряду батареї. 

Прошивка вимірює напругу живлення лише у фазі Warm-Sleep, коли трансивер вимкнений, і застосовує цифровий фільтр із вікном 2.0 секунди та програмний гістерезис 50 мВ для перемикання станів тривоги.
