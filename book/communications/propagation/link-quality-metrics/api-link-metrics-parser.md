# 📋 Інтерфейс та структура даних метрик якості радіолінку

Вставка містить системну специфікацію та програмні інтерфейси (API) для збору, обробки, класифікації та експорту метрик якості бездротового радіоканалу. Модуль розроблений для застосування у вбудованих системах реального часу (RTOS), моніторингових службах ОС Linux та стеках бездротових протоколів (Wi-Fi, LoRaWAN, IEEE 802.15.4, BLE).

## 1. Архітектурне призначення та принципи побудови API

У розробці драйверів радіочастотних трансиверів та мережевих протоколів інтерфейс збору метрик виконує роль містка між апаратним фізичним рівнем (PHY) та рівнями управління доступом до середовища (MAC) і маршрутизації (NET). 

Фізичний трансивер після декодування кожного кадру генерує апаратне переривання та записує у свої внутрішні регістри сирі значення потужності і чистоти фази. Обов'язок представленого API полягає у виконанні чотирьох послідовних задач:

1. **Нормалізація та приведення одиниць:** Перетворення сирих регістрових значень трансивера у фізичні одиниці (децибел-мілівати, децибели, проміле).
2. **Фільтрація та віконне усереднення:** Згладжування високочастотних флуктуацій за допомогою низькочастотних фільтрів та ковзних вікон.
3. **Статистичний аналіз втрат:** Ведення обліку успішно прийнятих кадрів, помилок контрольної суми (CRC) та таймаутів очікування відповіді.
4. **Форматування телеметрії:** Експорт зібраної статистики у стандартизовані формати (JSON, binary struct, sysfs) для систем вищого рівня.

Проектні рішення даного API враховують суворі вимоги розробки програмного забезпечення вбудованих систем: мінімізацію обсягу оперативної пам'яті, гарантовану відсутність динамічного виділення кучі у контексті переривань та повну потокобезпечність (Thread-Safety) при передачі даних між завданнями RTOS.

## 2. Детальний опис полів структур даних та вирівнювання пам'яті

Структура даних `radio_link_metrics_t` (або `RadioLinkMetrics` у C++) є компактним контейнером, розрахованим на мінімальне споживання пам'яті та безпечне передавання між перериваннями та основними потоками виконання.

Розмір структури свідомо обмежено 8 байтами для забезпечення ідеального вирівнювання за межами слів 32-бітних процесорних архітектур (ARM Cortex-M, RISC-V, ESP32). Це уможливлює виконання копіювання структури за один або два такти процесора через батилеві машинні інструкції LDRD/STRD без використання блокувальних мутексів.

| Поле структури | Тип даних | Діапазон значень | Одиниці вимірювання | Фізичний зміст та особливості обробки |
| :--- | :--- | :--- | :--- | :--- |
| `rssi_dbm_x10` | `int16_t` | `-1400 .. 0` | 0.1 дБм | Сира потужність у вхідному коаксіальному роз'ємі або антені. Значення `-854` відповідає `-85.4 дБм`. Використовується тип `int16_t` для уникнення обчислень із плаваючою крапкою на мікроконтролерах без FPU. |
| `snr_db_x10` | `int16_t` | `-200 .. +400` | 0.1 дБ | Відношення корисного сигналу до шумової підлоги. Від'ємні значення можливі для розширеного спектра (LoRa/DSSS). |
| `lqi` | `uint8_t` | `0 .. 255` | Безрозмірний | Апаратний індикатор якості лінку від демодулятора чіпа. Значення `255` відповідає нульовому EVM та повній кореляції преамбули. |
| `per_permille` | `uint16_t` | `0 .. 1000` | ‰ (проміле) | Частка втрачених або зіпсованих пакетів на статистичному вікні. `1000` відповідає 100% втраті зв'язку (1000‰). |
| `health` | `enum` | `0 .. 3` | Категорія | Перераховний тип стану каналу (`CRITICAL`, `DEGRADED`, `GOOD`, `EXCELLENT`), сформований комбінованим класифікатором. |

## 3. Опис станів інтегрального класифікатора якості каналу

Класифікатор стану каналу `link_health_t` об'єднує сукупність незалежних метрик у чотири рівні якості для швидкого прийняття рішень вищими протокольними рівнями:

* **`LINK_HEALTH_CRITICAL` (0):** Канал непридатний для передачі даних. Рівень PER перевищує 15–20% або SNR знаходиться нижче порогу демодуляції. Рекомендовано знизити швидкість MCS, збільшити потужність або ініціювати пошук нового маршруту.
* **`LINK_HEALTH_DEGRADED` (1):** Зв'язок наявний, проте виявлено підвищений рівень завад або граничне згасання. Спостерігаються поодинокі втрати пакетів (PER 5–15%).
* **`LINK_HEALTH_GOOD` (2):** Задовільний стан каналу. Забезпечується стабільна передача даних із низьким рівнем помилок (PER < 5%), проте значення SNR або LQI мають запас менше 10 дБ до межі деградації.
* **`LINK_HEALTH_EXCELLENT` (3):** Ідеальні умови зв'язку. Високий SNR (> 15 дБ), LQI близький до максимуму (> 200), відсутність помилок CRC. Дозволено використання максимальних швидкісних режимів модуляції (16-QAM, 64-QAM).

Класифікатор здійснює перевірку метрик у порядку спадання критичності: першочергово перевіряються статистичні втрати кадрів (PER), далі енергетичний запас (SNR), і лише потім якість сузір'я (LQI).

## 4. Двомовний програмний інтерфейс (C та C++)

Нижче наведено повну специфікацію заголовкових файлів та інтерфейсних структур на мовах C та C++. Симетрична реалізація дозволяє розробникам обирати ідіоматичний підхід відповідно до вибраної платформи розробки.

:::tabs
```c
/* link_metrics_api.h - C API структури даних та функції розбору метрик */
#ifndef LINK_METRICS_API_H
#define LINK_METRICS_API_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    LINK_HEALTH_CRITICAL = 0,
    LINK_HEALTH_DEGRADED = 1,
    LINK_HEALTH_GOOD     = 2,
    LINK_HEALTH_EXCELLENT= 3
} link_health_t;

typedef struct {
    int16_t rssi_dbm_x10;    /* RSSI у децибел-міліватах * 10 (-1200 .. 0) */
    int16_t snr_db_x10;      /* SNR у децибелах * 10 (-200 .. +400) */
    uint8_t lqi;             /* Апаратний LQI (0 .. 255) */
    uint16_t per_permille;   /* PER у проміле (0 = 0.0%, 1000 = 100.0%) */
    link_health_t health;    /* Класифікований стан */
} radio_link_metrics_t;

typedef struct {
    uint32_t rx_success_count;
    uint32_t rx_crc_error_count;
    uint32_t rx_timeout_count;
    radio_link_metrics_t current_metrics;
} link_stats_report_t;

/**
 * @brief Ініціалізація структури звіту метрик.
 * @param report Вказівник на структуру звіту.
 */
void link_metrics_init(link_stats_report_t *report);

/**
 * @brief Оновлення метрик при отриманні нового кадру.
 * @param report Вказівник на структуру звіту.
 * @param raw_rssi_x10 Сирий RSSI у 0.1 дБм.
 * @param raw_snr_x10 Сирий SNR у 0.1 дБ.
 * @param raw_lqi Апаратне значення LQI (0..255).
 * @param crc_passed Прапор успішного перевірочного коду CRC.
 */
void link_metrics_update_frame(link_stats_report_t *report,
                               int16_t raw_rssi_x10,
                               int16_t raw_snr_x10,
                               uint8_t raw_lqi,
                               bool crc_passed);

/**
 * @brief Форматування телеметричного рядка звіту у буфер JSON.
 * @param report Вказівник на структуру звіту.
 * @param buf Буфер для запису текстового рядка.
 * @param buf_len Максимальна довжина буфера у байтах.
 * @return Кількість записаних байтів або -1 при помилці.
 */
int link_metrics_to_json(const link_stats_report_t *report, char *buf, size_t buf_len);

#ifdef __cplusplus
}
#endif

#endif /* LINK_METRICS_API_H */
```
```cpp
// link_metrics_api.hpp - C++20 API інтерфейс для моніторингу та телеметрії лінку
#ifndef LINK_METRICS_API_HPP
#define LINK_METRICS_API_HPP

#include <cstdint>
#include <string>
#include <string_view>
#include <span>
#include <optional>

namespace comms::metrics {

enum class LinkHealth : uint8_t {
    Critical = 0,
    Degraded,
    Good,
    Excellent
};

[[nodiscard]] constexpr std::string_view to_string(LinkHealth health) noexcept {
    switch (health) {
        case LinkHealth::Critical:  return "CRITICAL";
        case LinkHealth::Degraded:  return "DEGRADED";
        case LinkHealth::Good:      return "GOOD";
        case LinkHealth::Excellent: return "EXCELLENT";
    }
    return "UNKNOWN";
}

struct RadioLinkMetrics {
    float rssi_dbm{-100.0f};
    float snr_db{0.0f};
    uint8_t lqi{0};
    float per_percent{0.0f};
    LinkHealth health{LinkHealth::Critical};
};

struct PacketFrameSample {
    float rssi_dbm;
    float snr_db;
    uint8_t lqi;
    bool crc_valid;
};

class ILinkMetricsCollector {
public:
    virtual ~ILinkMetricsCollector() = default;

    virtual void recordSample(const PacketFrameSample& sample) noexcept = 0;
    [[nodiscard]] virtual RadioLinkMetrics snapshot() const noexcept = 0;
    [[nodiscard]] virtual std::string formatJsonReport() const = 0;
};

class LinkMetricsCollector final : public ILinkMetricsCollector {
public:
    explicit LinkMetricsCollector(std::size_t history_depth = 64)
        : history_depth_(history_depth) {}

    void recordSample(const PacketFrameSample& sample) noexcept override {
        total_frames_++;
        if (!sample.crc_valid) {
            crc_errors_++;
        }

        // Оновлення ковзних показників
        metrics_.rssi_dbm += 0.1f * (sample.rssi_dbm - metrics_.rssi_dbm);
        metrics_.snr_db  += 0.1f * (sample.snr_db - metrics_.snr_db);
        metrics_.lqi     = static_cast<uint8_t>(metrics_.lqi + 0.1f * (sample.lqi - metrics_.lqi));

        if (total_frames_ > 0) {
            metrics_.per_percent = (static_cast<float>(crc_errors_) / static_cast<float>(total_frames_)) * 100.0f;
        }

        classifyHealth();
    }

    [[nodiscard]] RadioLinkMetrics snapshot() const noexcept override {
        return metrics_;
    }

    [[nodiscard]] std::string formatJsonReport() const override {
        return std::string("{\"rssi\":") + std::to_string(metrics_.rssi_dbm) +
               ",\"snr\":" + std::to_string(metrics_.snr_db) +
               ",\"lqi\":" + std::to_string(metrics_.lqi) +
               ",\"per\":" + std::to_string(metrics_.per_percent) +
               ",\"health\":\"" + std::string(to_string(metrics_.health)) + "\"}";
    }

private:
    void classifyHealth() noexcept {
        if (metrics_.per_percent > 15.0f || metrics_.snr_db < 2.0f) {
            metrics_.health = LinkHealth::Critical;
        } else if (metrics_.per_percent > 5.0f || metrics_.snr_db < 8.0f) {
            metrics_.health = LinkHealth::Degraded;
        } else if (metrics_.snr_db < 15.0f || metrics_.lqi < 180) {
            metrics_.health = LinkHealth::Good;
        } else {
            metrics_.health = LinkHealth::Excellent;
        }
    }

    std::size_t history_depth_;
    std::size_t total_frames_{0};
    std::size_t crc_errors_{0};
    RadioLinkMetrics metrics_{};
};

} // namespace comms::metrics

#endif // LINK_METRICS_API_HPP
```
:::

## 5. Порівняльний аналіз шаблонів проектування C та C++

Вибір між Си-інтерфейсом та C++-абстракцією визначається архітектурою вбудованої системи:

1. **C API (`radio_link_metrics_t`):** Використовує підхід прозорої POD-структури (*Plain Old Data*). Усі покрокові маніпуляції виконуються чистими функціями, які приймають вказівник на екземпляр. Переваги: нульові накладні витрати на таблиці віртуальних методів (vtable), повна сумісність із комбінованими C/C++ проектами та легка інтеграція з операційними системами FreeRTOS і Zephyr.
2. **C++20 API (`LinkMetricsCollector`):** Використовує поліморфний інтерфейс `ILinkMetricsCollector` з інкапсуляцією стану всередині класу. Застосування специфікаторів `constexpr`, `noexcept` та `[[nodiscard]]` гарантує перевірку правил обробки на етапі компіляції. Використання `std::string_view` унеможливлює виділення динамічної пам'яті при форматуванні текстових маркерів станів.

## 6. Інтеграція з віртуальною файловою системою Linux (sysfs/procfs)

У драйверах бездротових мережевих адаптерів ОС Linux (наприклад, драйвери `mac80211`, `ath9k`, `iwlwifi`) сформована статистика якості каналу експортується у простір користувача через підсистему `nl80211` та віртуальні файли `sysfs`.

Типовий шлях експорту метрик поточного з'єднання має вигляд:

```
/sys/class/net/wlan0/phy80211/link_quality
```

При зчитуванні даного файла ядро повертає текстову структуру, в якій узагальнено апаратний LQI, згладжений RSSI та по поточні показники збоїв кадру:

```
link_quality: 70/70
signal_level: -52 dBm
noise_level:  -95 dBm
snr:          43 dB
rx_packets:   145209
rx_errors:    12
per:          0.008%
```

Інтерфейс системних команд утиліти `iw` звертається до ядерного сокета `Netlink` (`NL80211_CMD_GET_STATION`) для зчитування бінарного контейнера даних, аналогічного структурі `radio_link_metrics_t`. Це дозволяє утилітам системного моніторингу (наприклад, `Prometheus node_exporter` або `Wavemon`) відображати графіки стану радіоефіру у реальному часі.

## 7. Інтеграція з протоколами телеметрії MQTT та CoAP

Для пристроїв Інтернету речей (IoT) сформований звіт експортується у вигляд компактного пакету JSON або бінарного протоколу CBOR/Protobuf. Прикладом стандартизованого топіка MQTT для телеметрії стану радіоканалу є:

```
tele/node_node_04a2/link_status
```

Згенероване кодом `link_metrics_to_json()` або `formatJsonReport()` корисне навантаження дозволяє серверу аналітики вести довгостроковий моніторинг покриття бездротової мережі:

```json
{
  "rssi_dbm": -78.5,
  "snr_db": 14.2,
  "lqi": 195,
  "per_percent": 0.15,
  "health": "GOOD",
  "packets_total": 45210,
  "crc_errors": 68
}
```

Використання строго визначеної структури даних та єдиного API забезпечує повну сумісність між різними апаратними платформами трансиверів та мережевими операційними системами.
