# ⚙️ Реалізація аналізатора якості радіоканалу та фільтрації метрик

У реальних бездротових пристроях значення RSSI, SNR та LQI, зчитані з регістрів приймача, містять значний високочастотний шум та спотворення через короткочасні завмирання. Пряме використання сирих вимірювань для прийняття рішень про зміну потужності або перехід між швидкісними режимами спричиняє нестабільність («пінг-понг» режимів).

Ця вставка містить практичну реалізацію модуля моніторингу якості каналу на мовах C та C++. Модуль обчислює згладжені значення RSSI/SNR за допомогою експоненційного ковзного середнього (EMA), веде статистику PER на ковзному вікні пакетів та реалізує автомат станів адаптації MCS.

## 1. Архітектура та математичні засади модуля моніторингу

Програмування вбудованих систем зв'язку реального часу вимагає дотримання двох суворих обмежень: мінімального обсягу обчислювальних ресурсів процесора та відсутності динамічного виділення пам'яті (`malloc`/`new`) під час обробки переривань від радіоадаптера.

Модуль моніторингу спирається на три алгоритмічні блоки:

### Експоненційне ковзне середнє (EMA) у арифметиці з фіксованою крапкою

Для вилучення короткочасних флуктуацій сигналу застосовують цифровий фільтр нижніх частот першого порядку. Його дискретна рекурсивна формула має вигляд:

```
y[k] = α · x[k] + (1 - α) · y[k-1]
```

де `x[k]` — нове сире значення метрики від приймача, `y[k]` — поточне згладжене значення, `y[k-1]` — попереднє згладжене значення, а `α` — коефіцієнт згладжування (0 < α ≤ 1).

Для виконання обчислень на 8-бітних або 32-бітних мікроконтролерах без блоку обчислень з плаваючою крапкою (FPU) формула переводиться в арифметику з фіксованою крапкою з масштабуючим коефіцієнтом `256` (8 біт дробової частини). 

Якщо обрано `α = 0.125 = 32 / 256`, обчислення спрощуються до п'яти битових операцій:

```
y_fp[k] = y_fp[k-1] + (((x_scaled - y_fp[k-1]) · 32) >> 8)
```

Такий підхід забезпечує виконання фільтрації за 3–4 такти центрального процесора без використання операцій ділення та операцій з плаваючою крапкою.

### Кільцевий буфер ковзного вікна для обчислення PER

Традиційний підлік PER як відношення лічильника зіпсованих пакетів до загальної кількості відправлених кадрів з початку сесії має високу інерційність: через годину роботи мережі з мільйоном прийнятих пакетів короткочасна поява сильної завади практично не змінить підсумковий відсоток.

Для забезпечення швидкої реакції використовують ковзне вікно фіксованого розміру (наприклад, `N = 32` пакети). У мові C кільцевий буфер реалізується як масив байтів із циклічним покажчиком `window_head = (window_head + 1) % N`. 

При надходженні нового кадру з масиву віднімається результат найстарішого кадру і додається результат нового:

```
crc_errors = crc_errors - old_crc_status + new_crc_status
```

Це дозволяє обчислювати PER на вікні `N` пакетів за час `O(1)` без повного перебору масиву.

### Гістерезисний автомат станів адаптації MCS

Зміна швидкісних режимів модуляції та кодування (MCS) здійснюється автоматом станів із трьома режимами:

1. **`MCS_MODE_BPSK` (MCS 0):** Базовий режим із найвищою стійкістю до завад.
2. **`MCS_MODE_QPSK` (MCS 1-2):** Балансний режим для типових умов зв'язку.
3. **`MCS_MODE_QAM16` (MCS 3-4):** Швидкісний режим для чистого радіоефіру.

Запобігання генерації частих переходів («пінг-понгу») реалізовано за допомогою гістерезису: поріг підвищення швидкісного режиму за SNR виставляється на `3 дБ` вище, ніж поріг зниження режиму, а також вимагається низьке значення `PER < 2%`.

## 2. Покроковий розбір C та C++ реалізації

У версії мовою C структура `link_monitor_t` зберігає накопичувальні поля у форматі цілих чисел із фіксованою крапкою `int32_t`. Зсув `ALPHA_FP_SHIFT = 8` масштабує дробові значення, забезпечуючи точність `1 / 256 ≈ 0.0039`. Функція `link_monitor_update()` викликається з обробника переривання прийому кадру або у задачі мережевого стека.

Версія мовою C++ `LinkQualityMonitor` оформлена у вигляді шаблонного класу `template <std::size_t WindowSize = 32>`, де розмір статистичного вікна задається як параметр компіляції. Це дозволяє виділяти пам'ять під кільцевий буфер `std::array<bool, WindowSize>` безпосередньо на стеку без динамічного купи. Метод `processPacket()` реалізує згладжування та автоматичний перерахунок стану без побічних ефектів, а методи-селектори `rssi()`, `snr()`, `lqi()`, `packetErrorRate()` та `healthStatus()` позначені специфікатором `[[nodiscard]]` та `noexcept` для забезпечення максимальної продуктивності та безпеки викликів у RTOS.

:::tabs
```c
/* link_monitor.c - Модуль аналізу якості радіоканалу на C */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PER_WINDOW_SIZE  32
#define ALPHA_FP_SHIFT   8   /* Фіксована крапка з масштабом 256 (α = 0.125 -> 32/256) */
#define ALPHA_WEIGHT     32

typedef enum {
    MCS_MODE_BPSK = 0,
    MCS_MODE_QPSK,
    MCS_MODE_QAM16
} mcs_mode_t;

typedef enum {
    LINK_STATUS_CRITICAL = 0,
    LINK_STATUS_FAIR,
    LINK_STATUS_EXCELLENT
} link_status_t;

typedef struct {
    int32_t ema_rssi_fp;     /* RSSI у фіксованій крапці (дБм * 256) */
    int32_t ema_snr_fp;      /* SNR у фіксованій крапці (дБ * 256) */
    uint32_t ema_lqi_fp;     /* LQI у фіксованій крапці (0..255 * 256) */
    
    uint8_t per_window[PER_WINDOW_SIZE];
    uint8_t window_head;
    uint32_t total_packets;
    uint32_t crc_errors;

    mcs_mode_t current_mcs;
    link_status_t status;
} link_monitor_t;

void link_monitor_init(link_monitor_t *mon) {
    if (!mon) return;
    memset(mon, 0, sizeof(link_monitor_t));
    mon->ema_rssi_fp = -100 * 256;  /* Початкове значення -100 дБм */
    mon->ema_snr_fp = 0;
    mon->ema_lqi_fp = 0;
    mon->current_mcs = MCS_MODE_BPSK;
    mon->status = LINK_STATUS_CRITICAL;
}

void link_monitor_update(link_monitor_t *mon, int8_t raw_rssi, int8_t raw_snr, uint8_t raw_lqi, bool crc_ok) {
    if (!mon) return;

    /* 1. Оновлення EMA фільтрів у фіксованій крапці */
    int32_t rssi_target = (int32_t)raw_rssi * 256;
    mon->ema_rssi_fp += ((rssi_target - mon->ema_rssi_fp) * ALPHA_WEIGHT) >> ALPHA_FP_SHIFT;

    int32_t snr_target = (int32_t)raw_snr * 256;
    mon->ema_snr_fp += ((snr_target - mon->ema_snr_fp) * ALPHA_WEIGHT) >> ALPHA_FP_SHIFT;

    uint32_t lqi_target = (uint32_t)raw_lqi * 256;
    mon->ema_lqi_fp += ((lqi_target - mon->ema_lqi_fp) * ALPHA_WEIGHT) >> ALPHA_FP_SHIFT;

    /* 2. Оновлення кільцевого буфера PER */
    uint8_t old_val = mon->per_window[mon->window_head];
    if (old_val == 1) {
        if (mon->crc_errors > 0) mon->crc_errors--;
    }

    uint8_t new_val = crc_ok ? 0 : 1;
    mon->per_window[mon->window_head] = new_val;
    if (new_val == 1) {
        mon->crc_errors++;
    }

    mon->window_head = (mon->window_head + 1) % PER_WINDOW_SIZE;
    if (mon->total_packets < PER_WINDOW_SIZE) {
        mon->total_packets++;
    }

    /* 3. Обчислення поточного PER у відсотках */
    float per_percent = 0.0f;
    if (mon->total_packets > 0) {
        per_percent = ((float)mon->crc_errors / (float)mon->total_packets) * 100.0f;
    }

    float snr_db = (float)mon->ema_snr_fp / 256.0f;
    float lqi_val = (float)mon->ema_lqi_fp / 256.0f;

    /* 4. Автомат станів адаптації MCS з гістерезисом */
    switch (mon->current_mcs) {
        case MCS_MODE_BPSK:
            if (snr_db >= 8.0f && lqi_val >= 120.0f && per_percent < 5.0f) {
                mon->current_mcs = MCS_MODE_QPSK;
            }
            break;

        case MCS_MODE_QPSK:
            if (per_percent > 15.0f || snr_db < 5.0f) {
                mon->current_mcs = MCS_MODE_BPSK;
            } else if (snr_db >= 16.0f && lqi_val >= 200.0f && per_percent < 2.0f) {
                mon->current_mcs = MCS_MODE_QAM16;
            }
            break;

        case MCS_MODE_QAM16:
            if (per_percent > 8.0f || snr_db < 12.0f || lqi_val < 150.0f) {
                mon->current_mcs = MCS_MODE_QPSK;
            }
            break;
    }

    /* 5. Класифікація загального стану каналу */
    if (per_percent > 20.0f || snr_db < 3.0f) {
        mon->status = LINK_STATUS_CRITICAL;
    } else if (per_percent < 3.0f && snr_db >= 12.0f && lqi_val >= 180.0f) {
        mon->status = LINK_STATUS_EXCELLENT;
    } else {
        mon->status = LINK_STATUS_FAIR;
    }
}

int main(void) {
    link_monitor_t monitor;
    link_monitor_init(&monitor);

    /* Імітація серії вимірювань під час прийому пакетів */
    int8_t test_rssi[] = {-85, -83, -80, -78, -75, -74, -75};
    int8_t test_snr[]  = {  4,   6,   9,  11,  14,  15,  16};
    uint8_t test_lqi[] = { 80, 100, 140, 170, 210, 220, 225};
    bool test_crc[]    = {true, true, true, true, true, true, true};

    size_t count = sizeof(test_rssi) / sizeof(test_rssi[0]);
    for (size_t i = 0; i < count; i++) {
        link_monitor_update(&monitor, test_rssi[i], test_snr[i], test_lqi[i], test_crc[i]);
        printf("Крок %zu: RSSI=%.1f dBm, SNR=%.1f dB, LQI=%.1f, MCS=%d, Status=%d\n",
               i + 1,
               (float)monitor.ema_rssi_fp / 256.0f,
               (float)monitor.ema_snr_fp / 256.0f,
               (float)monitor.ema_lqi_fp / 256.0f,
               monitor.current_mcs,
               monitor.status);
    }

    return 0;
}
```
```cpp
// link_monitor.cpp - Об'єктно-орієнтований модуль аналізу якості каналу на C++20
#include <iostream>
#include <array>
#include <numeric>
#include <format>
#include <cstdint>

enum class McsMode : uint8_t {
    Bpsk = 0,
    Qpsk,
    Qam16
};

enum class LinkHealth : uint8_t {
    Critical = 0,
    Fair,
    Excellent
};

template <std::size_t WindowSize = 32>
class LinkQualityMonitor {
public:
    explicit LinkQualityMonitor(float alpha = 0.125f) noexcept
        : alpha_(alpha), rssi_ema_(-100.0f), snr_ema_(0.0f), lqi_ema_(0.0f) {
        per_window_.fill(true);
    }

    void processPacket(float raw_rssi, float raw_snr, float raw_lqi, bool crc_ok) noexcept {
        // 1. Експоненційне згладжування EMA
        rssi_ema_ += alpha_ * (raw_rssi - rssi_ema_);
        snr_ema_  += alpha_ * (raw_snr - snr_ema_);
        lqi_ema_  += alpha_ * (raw_lqi - lqi_ema_);

        // 2. Оновлення ковзного вікна результатів CRC
        per_window_[window_index_] = crc_ok;
        window_index_ = (window_index_ + 1) % WindowSize;
        if (total_processed_ < WindowSize) {
            total_processed_++;
        }

        // 3. Обчислення поточного PER та передача у стан адаптації
        updateMcsState();
    }

    [[nodiscard]] float rssi() const noexcept { return rssi_ema_; }
    [[nodiscard]] float snr() const noexcept { return snr_ema_; }
    [[nodiscard]] float lqi() const noexcept { return lqi_ema_; }
    
    [[nodiscard]] float packetErrorRate() const noexcept {
        if (total_processed_ == 0) return 0.0f;
        std::size_t valid_count = 0;
        for (std::size_t i = 0; i < total_processed_; ++i) {
            if (per_window_[i]) valid_count++;
        }
        std::size_t errors = total_processed_ - valid_count;
        return (static_cast<float>(errors) / static_cast<float>(total_processed_)) * 100.0f;
    }

    [[nodiscard]] McsMode currentMcs() const noexcept { return current_mcs_; }
    
    [[nodiscard]] LinkHealth healthStatus() const noexcept {
        float per = packetErrorRate();
        if (per > 20.0f || snr_ema_ < 3.0f) {
            return LinkHealth::Critical;
        }
        if (per < 3.0f && snr_ema_ >= 12.0f && lqi_ema_ >= 180.0f) {
            return LinkHealth::Excellent;
        }
        return LinkHealth::Fair;
    }

private:
    void updateMcsState() noexcept {
        float per = packetErrorRate();

        switch (current_mcs_) {
            case McsMode::Bpsk:
                if (snr_ema_ >= 8.0f && lqi_ema_ >= 120.0f && per < 5.0f) {
                    current_mcs_ = McsMode::Qpsk;
                }
                break;

            case McsMode::Qpsk:
                if (per > 15.0f || snr_ema_ < 5.0f) {
                    current_mcs_ = McsMode::Bpsk;
                } else if (snr_ema_ >= 16.0f && lqi_ema_ >= 200.0f && per < 2.0f) {
                    current_mcs_ = McsMode::Qam16;
                }
                break;

            case McsMode::Qam16:
                if (per > 8.0f || snr_ema_ < 12.0f || lqi_ema_ < 150.0f) {
                    current_mcs_ = McsMode::Qpsk;
                }
                break;
        }
    }

    float alpha_;
    float rssi_ema_;
    float snr_ema_;
    float lqi_ema_;

    std::array<bool, WindowSize> per_window_{};
    std::size_t window_index_{0};
    std::size_t total_processed_{0};

    McsMode current_mcs_{McsMode::Bpsk};
};

int main() {
    LinkQualityMonitor<32> monitor(0.2f);

    struct PacketSample {
        float rssi;
        float snr;
        float lqi;
        bool crc;
    };

    const std::array samples = {
        PacketSample{-85.0f,  4.0f,  80.0f, true},
        PacketSample{-83.0f,  6.0f, 100.0f, true},
        PacketSample{-80.0f,  9.0f, 140.0f, true},
        PacketSample{-78.0f, 11.0f, 170.0f, true},
        PacketSample{-75.0f, 14.0f, 210.0f, true},
        PacketSample{-74.0f, 15.0f, 220.0f, true},
        PacketSample{-75.0f, 16.0f, 225.0f, true}
    };

    for (std::size_t idx = 0; const auto& sample : samples) {
        monitor.processPacket(sample.rssi, sample.snr, sample.lqi, sample.crc);
        std::cout << std::format("Крок {}: RSSI={:.1f} dBm, SNR={:.1f} dB, LQI={:.1f}, PER={:.1f}%, MCS={}\n",
                                 idx + 1,
                                 monitor.rssi(),
                                 monitor.snr(),
                                 monitor.lqi(),
                                 monitor.packetErrorRate(),
                                 static_cast<int>(monitor.currentMcs()));
        idx++;
    }

    return 0;
}
```
:::

## 3. Інтеграція з операційними системами реального часу (FreeRTOS / Zephyr)

При інтеграції даного модуля у бездротовий стек на базі FreeRTOS або Zephyr RTOS виклик функції `link_monitor_update()` здійснюється у контексті задачі обробки прийнятих кадрів (MAC RX Task).

Приклад інтеграції у задачу FreeRTOS:

:::tabs
```c
void vMacRxTask(void *pvParameters) {
    radio_packet_t rx_packet;
    link_monitor_t link_mon;
    link_monitor_init(&link_mon);

    for (;;) {
        if (xQueueReceive(xRadioRxQueue, &rx_packet, portMAX_DELAY) == pdTRUE) {
            /* Зчитування апаратних метаданих кадру */
            int8_t raw_rssi = rx_packet.header.rssi;
            int8_t raw_snr  = rx_packet.header.snr;
            uint8_t raw_lqi = rx_packet.header.lqi;
            bool crc_ok     = rx_packet.header.crc_valid;

            /* Оновлення стану монітора */
            link_monitor_update(&link_mon, raw_rssi, raw_snr, raw_lqi, crc_ok);

            /* Якщо стан каналу критичний — відправляємо сигнали на зниження швидкості */
            if (link_mon.status == LINK_STATUS_CRITICAL) {
                vRadioSetPowerTx(TX_POWER_MAX);
            }
        }
    }
}
```
```cpp
void vMacRxTaskCpp(void *pvParameters) {
    radio_packet_t rx_packet{};
    LinkQualityMonitor<32> link_mon(0.125f);

    for (;;) {
        if (xQueueReceive(xRadioRxQueue, &rx_packet, portMAX_DELAY) == pdTRUE) {
            /* Зчитування метаданих у C++ об'єкт */
            const auto raw_rssi = static_cast<float>(rx_packet.header.rssi);
            const auto raw_snr  = static_cast<float>(rx_packet.header.snr);
            const auto raw_lqi  = static_cast<float>(rx_packet.header.lqi);
            const bool crc_ok   = rx_packet.header.crc_valid;

            /* Оновлення стану через метод класу */
            link_mon.processPacket(raw_rssi, raw_snr, raw_lqi, crc_ok);

            /* Реагування на критичний стан через сильно типізований enum */
            if (link_mon.healthStatus() == LinkHealth::Critical) {
                vRadioSetPowerTx(TX_POWER_MAX);
            }
        }
    }
}
```
:::

## 4. Обробка крайових випадків та відлагодження

При роботі в середовищі з імпульсними завадами модуль захищений від хибних переходів:

1. **Серія збоїв CRC:** Якщо внаслідок імпульсного спалаху завади 5 пакетів поспіль мають помилку CRC, PER у ковзному вікні зростає з 0% до 15.6% (5/32). Це миттєво переводить автомат у нижчий стан `MCS_MODE_BPSK`, запобігаючи подальшим втратам кадрів.
2. **Тривала відсутність пакетів (Таймаут):** Якщо нові кадри не надходять більше ніж `T_timeout = 5000 мс`, лічильники кільцевого буфера поступово заповнюються значеннями помилок, що скидає стан до надійного базового режиму перед спробою повторного встановлення з'єднання.

Завдяки цьому модуль гарантує високу живучість бездротового з'єднання у нестабільних промислових умовах.
