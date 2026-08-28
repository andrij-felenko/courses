# ⚙️ Клієнтський менеджер роумінгу та фільтрації RSSI на вбудованому SoC

Вбудовані мікроконтролери та системи на кристалі з підтримкою Wi-Fi (зокрема сімейства Espressif ESP32, ESP32-S3, ESP32-C3, Realtek Ameba, TI SimpleLink) за замовчуванням мають спрощену логіку клієнтської станції. Після первинного з'єднання з точкою доступу радіотракт залишається на обраному BSSID до повної втрати фізичного лінку (англ. *Beacon Loss / Link Timeout*). Навіть якщо пристрій перемістився впритул до іншої точки доступу тієї самої мережі SSID із вчетверо вищим рівнем сигналу, стандартний драйвер не ініціює перехід, доки рівень поточної точки не впаде нижче порогу чутливості приймача (-88..-92 dBm).

Така поведінка є критичною вадою для рухомих пристроїв: складських AGV-роботів, безпілотних платформ, дронів або ручних промислових терміналів. Створення спеціалізованого клієнтського менеджера роумінгу на базі операційної системи реального часу (FreeRTOS) дозволяє реалізувати автономний, безшовний хендовер із неблокувальним фоновим скануванням, цифровою фільтрацією сигналу та надійним захистом від ефекту «пінг-понгу».

### 1. Архітектурні вимоги та модель взаємодії з RTOS

Вбудовані системи Wi-Fi мають суттєві апаратні та програмні обмеження, які необхідно враховувати при розробці клієнтського менеджера:
* **Один спільний радіотракт (Single RF Core):** чип не може одночасно передавати корисні дані на робочому каналі та сканувати інші частоти. Кожна зміна каналу для відправки `Probe Request` вимагає переналаштування синтезатора частоти PLL і призупиняє прийом пакетів поточної асоціації на рівні MAC-рівня.
* **Обмеження пам'яті стека LwIP:** під час сканування сусідніх каналів прикладні задачі FreeRTOS продовжують генерувати вихідний мережевий трафік (наприклад, MQTT-телеметрію або UDP-відеопотік). Пакети накопичуються в кільцевих буферах `pbuf`. Якщо сканування затягується довше 100–150 мс, пул буферів вичерпується, викликаючи критичну помилку `ERR_MEM` і скидання з'єднань.
* **Подієва модель драйвера:** взаємодія з підсистемою Wi-Fi повинна відбуватися асинхронно через стандартний цикл системних подій `esp_event_loop`. Блокування обробників подій функціями затримки (`vTaskDelay`) неприпустиме, оскільки це призводить до зависання системного завдання Wi-Fi.

Схема керування будується як окреме системне завдання з низьким пріоритетом, яке періодично зчитує показники радіотракту, фільтрує шум і запускає асинхронне сканування:

```
[Системне опитування RSSI] ──> [Цифровий фільтр EWMA] ──> [Порівняння з Threshold (-75 dBm)]
                                                                    │
                                                  (Сигнал слабкий, старт FSM)
                                                                    ▼
[Черга LwIP pbuf] <── [Обмеження scan_time] <── [Асинхронний скан esp_wifi_scan_start]
                                                                    │
                                                  (Подія WIFI_EVENT_SCAN_DONE)
                                                                    ▼
[Перевірка гістерезису Δ ≥ 6 dB] <── [Зважена оцінка кандидатів (Score)]
             │
   (Знайдено кращу AP)
             ▼
[esp_wifi_set_config(bssid)] ──> [Швидка реасоціація] ──> [Gratuitous ARP у мережу]
```

### 2. Алгоритм зваженої оцінки кандидатів (Scoring Function)

Для вибору оптимальної точки доступу недостатньо порівнювати лише сирий рівень потужності RSSI. Менеджер застосовує багатофакторну оцінку якості:

```
Score(AP) = W_rssi · (RSSI - RSSI_min) + W_band · Is_5GHz - W_load · Channel_Load - W_cochan · CoChannel_Penalty
```

де:
* `W_rssi = 1.0` — базова вага рівня сигналу в dBm;
* `W_band = 12.0` — ваговий бонус за використання діапазону 5 ГГц (де рівень завад значно нижчий, ніж у перевантаженому діапазоні 2.4 ГГц);
* `W_load = 0.2` — коефіцієнт штрафу за завантаженість каналу з інформаційного елемента BSS Load;
* `W_cochan = 4.0` — штраф за роботу на каналах із високим рівнем інтерференції від сусідніх сторонніх мереж.

### 3. Повна реалізація менеджера роумінгу на C (ESP-IDF) та C++20

:::tabs
```c
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"

#define TAG "ROAM_MGR"

#define ROAM_RSSI_THRESHOLD_DBM   (-75)  /* Поріг активації пошуку нової AP */
#define ROAM_HYSTERESIS_MARGIN_DB (6)    /* Обов'язковий запас сигналу кандидата */
#define ROAM_EWMA_ALPHA_PERCENT   (20)   /* Коефіцієнт згладжування 0.2 (20%) */
#define ROAM_HOLDOFF_PERIOD_MS    (5000) /* Мінімальний інтервал між переходами */
#define ROAM_POLL_INTERVAL_MS     (1000) /* Інтервал опитування RSSI */

typedef enum {
    ROAM_STATE_INIT,
    ROAM_STATE_CONNECTED,
    ROAM_STATE_SCANNING,
    ROAM_STATE_HANDOVER
} roam_state_t;

typedef struct {
    roam_state_t state;
    char target_ssid[33];
    uint8_t current_bssid[6];
    uint8_t current_channel;
    int8_t current_rssi_filtered;
    int64_t last_handover_timestamp_us;
} roam_manager_t;

static roam_manager_t s_mgr;

static void update_rssi_filter(int8_t raw_rssi) {
    if (s_mgr.current_rssi_filtered == 0) {
        s_mgr.current_rssi_filtered = raw_rssi;
    } else {
        /* EWMA: RSSI[k] = α · Raw + (1 - α) · RSSI[k-1] у цілочисельній арифметиці */
        int32_t weighted = (raw_rssi * ROAM_EWMA_ALPHA_PERCENT) + 
                           (s_mgr.current_rssi_filtered * (100 - ROAM_EWMA_ALPHA_PERCENT));
        s_mgr.current_rssi_filtered = (int8_t)(weighted / 100);
    }
}

static void evaluate_scan_results_and_roam(void) {
    uint16_t ap_count = 0;
    esp_wifi_scan_get_ap_num(&ap_count);
    if (ap_count == 0) {
        s_mgr.state = ROAM_STATE_CONNECTED;
        return;
    }

    wifi_ap_record_t *records = (wifi_ap_record_t *)malloc(sizeof(wifi_ap_record_t) * ap_count);
    if (!records) {
        s_mgr.state = ROAM_STATE_CONNECTED;
        return;
    }

    if (esp_wifi_scan_get_ap_records(&ap_count, records) != ESP_OK) {
        free(records);
        s_mgr.state = ROAM_STATE_CONNECTED;
        return;
    }

    int8_t best_score = -127;
    uint8_t best_bssid[6] = {0};
    uint8_t best_channel = 0;
    bool candidate_found = false;

    const int8_t required_rssi = s_mgr.current_rssi_filtered + ROAM_HYSTERESIS_MARGIN_DB;

    for (int i = 0; i < ap_count; ++i) {
        /* Перевірка відповідності імені мережі */
        if (strcmp((const char *)records[i].ssid, s_mgr.target_ssid) != 0) {
            continue;
        }
        /* Ігнорування поточної точки доступу */
        if (memcmp(records[i].bssid, s_mgr.current_bssid, 6) == 0) {
            continue;
        }

        /* Перевірка порогу гістерезису */
        if (records[i].rssi >= required_rssi) {
            int8_t score = records[i].rssi;
            if (records[i].primary > 14) {
                score += 10; /* Бонус за діапазон 5 ГГц */
            }

            if (score > best_score) {
                best_score = score;
                memcpy(best_bssid, records[i].bssid, 6);
                best_channel = records[i].primary;
                candidate_found = true;
            }
        }
    }

    free(records);

    if (candidate_found) {
        int64_t now_us = esp_timer_get_time();
        if ((now_us - s_mgr.last_handover_timestamp_us) < (ROAM_HOLDOFF_PERIOD_MS * 1000LL)) {
            ESP_LOGW(TAG, "Кандидат знайдений, але таймер затримки ще активний. Перехід скасовано.");
            s_mgr.state = ROAM_STATE_CONNECTED;
            return;
        }

        ESP_LOGI(TAG, "Ініціація хендоверу на BSSID %02x:%02x:%02x:%02x:%02x:%02x (Канал %d, RSSI %d dBm)",
                 best_bssid[0], best_bssid[1], best_bssid[2],
                 best_bssid[3], best_bssid[4], best_bssid[5], best_channel, best_score);

        s_mgr.state = ROAM_STATE_HANDOVER;
        s_mgr.last_handover_timestamp_us = now_us;

        wifi_config_t wifi_cfg;
        esp_wifi_get_config(WIFI_IF_STA, &wifi_cfg);
        wifi_cfg.sta.bssid_set = 1;
        memcpy(wifi_cfg.sta.bssid, best_bssid, 6);
        wifi_cfg.sta.channel = best_channel;

        esp_wifi_set_config(WIFI_IF_STA, &wifi_cfg);
        esp_wifi_disconnect();
        esp_wifi_connect();
    } else {
        s_mgr.state = ROAM_STATE_CONNECTED;
    }
}

static void roam_monitor_task(void *arg) {
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(ROAM_POLL_INTERVAL_MS));

        if (s_mgr.state != ROAM_STATE_CONNECTED) {
            continue;
        }

        wifi_ap_record_t ap_info;
        if (esp_wifi_sta_get_ap_info(&ap_info) == ESP_OK) {
            memcpy(s_mgr.current_bssid, ap_info.bssid, 6);
            s_mgr.current_channel = ap_info.primary;
            update_rssi_filter(ap_info.rssi);

            ESP_LOGD(TAG, "Моніторинг: Сирий RSSI = %d dBm, Згладжений = %d dBm",
                     ap_info.rssi, s_mgr.current_rssi_filtered);

            if (s_mgr.current_rssi_filtered < ROAM_RSSI_THRESHOLD_DBM) {
                ESP_LOGI(TAG, "Сигнал нижче порогу (%d dBm). Старт неблокувального сканування...",
                         s_mgr.current_rssi_filtered);
                s_mgr.state = ROAM_STATE_SCANNING;

                wifi_scan_config_t scan_cfg = {
                    .ssid = (uint8_t *)s_mgr.target_ssid,
                    .bssid = NULL,
                    .channel = 0,
                    .show_hidden = false,
                    .scan_type = WIFI_SCAN_TYPE_ACTIVE,
                    .scan_time.active.min = 15,
                    .scan_time.active.max = 30
                };
                esp_wifi_scan_start(&scan_cfg, false);
            }
        }
    }
}

static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_SCAN_DONE) {
        if (s_mgr.state == ROAM_STATE_SCANNING) {
            evaluate_scan_results_and_roam();
        }
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_CONNECTED) {
        wifi_event_sta_connected_t *evt = (wifi_event_sta_connected_t *)event_data;
        memcpy(s_mgr.current_bssid, evt->bssid, 6);
        s_mgr.current_channel = evt->channel;
        s_mgr.state = ROAM_STATE_CONNECTED;
        ESP_LOGI(TAG, "З'єднання встановлено з BSSID: %02x:%02x:%02x:%02x:%02x:%02x на каналі %d",
                 evt->bssid[0], evt->bssid[1], evt->bssid[2],
                 evt->bssid[3], evt->bssid[4], evt->bssid[5], evt->channel);
    } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        s_mgr.state = ROAM_STATE_INIT;
        s_mgr.current_rssi_filtered = 0;
        esp_wifi_connect();
    }
}

void roam_manager_start(const char *ssid) {
    memset(&s_mgr, 0, sizeof(s_mgr));
    strncpy(s_mgr.target_ssid, ssid, sizeof(s_mgr.target_ssid) - 1);
    s_mgr.state = ROAM_STATE_INIT;

    esp_event_handler_instance_register(WIFI_EVENT, ESP_EVENT_ANY_ID,
                                        &wifi_event_handler, NULL, NULL);
    xTaskCreate(roam_monitor_task, "roam_monitor", 4096, NULL, 5, NULL);
}
```
```cpp
#include <cstdint>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <optional>
#include <chrono>
#include <algorithm>
#include <span>

namespace wifi {

using MacAddress = std::array<uint8_t, 6>;

struct ApCandidate {
    MacAddress bssid{};
    int8_t rssi{0};
    uint8_t channel{0};
    std::string ssid;

    [[nodiscard]] constexpr bool is_5ghz() const noexcept {
        return channel > 14;
    }
};

class RssiFilter {
public:
    explicit constexpr RssiFilter(float alpha = 0.2f) noexcept : alpha_(alpha) {}

    void update(int8_t raw_rssi) noexcept {
        if (!initialized_) {
            value_ = static_cast<float>(raw_rssi);
            initialized_ = true;
        } else {
            value_ = alpha_ * static_cast<float>(raw_rssi) + (1.0f - alpha_) * value_;
        }
    }

    [[nodiscard]] int8_t value() const noexcept {
        return static_cast<int8_t>(value_);
    }

    void reset() noexcept {
        initialized_ = false;
        value_ = 0.0f;
    }

private:
    float alpha_{0.2f};
    float value_{0.0f};
    bool initialized_{false};
};

class RoamingEngine {
public:
    struct Config {
        int8_t threshold_dbm{-75};
        int8_t hysteresis_db{6};
        int8_t band_5ghz_bonus_db{10};
        std::chrono::milliseconds holdoff_time{5000};
    };

    explicit RoamingEngine(std::string_view target_ssid, Config cfg = {})
        : target_ssid_(target_ssid), config_(cfg) {}

    void on_beacon_rssi(int8_t raw_rssi) noexcept {
        filter_.update(raw_rssi);
    }

    [[nodiscard]] bool should_trigger_scan() const noexcept {
        return filter_.value() < config_.threshold_dbm;
    }

    [[nodiscard]] std::optional<ApCandidate> select_best_candidate(
        std::span<const ApCandidate> scan_results,
        const MacAddress& current_bssid,
        std::chrono::steady_clock::time_point now) noexcept 
    {
        if (now - last_handover_time_ < config_.holdoff_time) {
            return std::nullopt; /* Захист від частих перемикань за таймером */
        }

        const int8_t required_rssi = filter_.value() + config_.hysteresis_db;
        const ApCandidate* best = nullptr;
        int16_t best_score = -32768;

        for (const auto& candidate : scan_results) {
            if (candidate.ssid != target_ssid_) {
                continue;
            }
            if (candidate.bssid == current_bssid) {
                continue;
            }

            if (candidate.rssi >= required_rssi) {
                int16_t score = candidate.rssi;
                if (candidate.is_5ghz()) {
                    score += config_.band_5ghz_bonus_db;
                }

                if (!best || score > best_score) {
                    best_score = score;
                    best = &candidate;
                }
            }
        }

        if (best) {
            last_handover_time_ = now;
            return *best;
        }

        return std::nullopt;
    }

    [[nodiscard]] int8_t filtered_rssi() const noexcept {
        return filter_.value();
    }

    void reset() noexcept {
        filter_.reset();
    }

private:
    std::string target_ssid_;
    Config config_;
    RssiFilter filter_;
    std::chrono::steady_clock::time_point last_handover_time_{};
};

} // namespace wifi
```
:::

### 4. Практичні пастки та розбір помилок реалізації

1. **Вичерпання черги буферів LwIP під час активного сканування:** Коли радіомодуль перемикається між каналами 1..11, стек продовжує приймати вихідні TCP-пакети від додатків. Оскільки передача в ефір неможлива, буфери `pbuf` заповнюють усю вільну оперативну пам'ять. Якщо скан триває довше 120 мс, черга переповнюється і повертає `ERR_MEM`. Рішення: обмежувати час активного зондування каналу параметром `scan_time.active.max = 25 мс` або призупиняти передачу некритичних даних перед запуском сканування.
2. **Зайві запити DHCP Discover після хендоверу:** Помилковий виклик `esp_netif_dhcpc_start()` після реасоціації скидає наявну IP-адресу та змушує клієнт чекати на `DHCP Offer`, додаючи 500–2000 мс непотрібної затримки. Якщо всі точки належать одному L2-сегменту, IP-адреса залишається валідною, а комутаторам достатньо отримати один `Gratuitous ARP`.
3. **Зависання на прихованих SSID (Hidden Networks):** Якщо мережа приховує SSID у beacon-кадрах, пасивне сканування повертає порожні рядки. Менеджер роумінгу повинен виконувати виключно пряме активне зондування із зазначенням цільового імені в полі `scan_cfg.ssid`.
4. **Конфлікт каналів DFS (Radar Detection):** Спроба виконати активний скан із передачею `Probe Request` на каналах 52–144 блокується радіоконтролером згідно з нормами регуляторів. На цих каналах можливе лише пасивне прослуховування або прицільне використання даних 802.11k Neighbor Report.
5. **Втрата синхронізації лічильників Replay Counter при WPA2:** Якщо під час швидкої реасоціації драйвер не оновлює стан криптографічного блоку, перші пакети з нової AP можуть бути відкинуті апаратним блоком CCMP через невідповідність 48-бітного лічильника `Packet Number (PN)`, що спричиняє обрив TCP-сесії.
6. **Шторм повторних підключень при граничному сигналі (Handover Flapping):** Якщо мобільний пристрій зупиняється точно посередині між двома точками доступу без таймера затримки (Holdoff Timer), різниця сигналів коливається біля порогу `Δ`, викликаючи безперервні цикли підключення-відключення щосекунди. Застосування `ROAM_HOLDOFF_PERIOD_MS = 5000` повністю усуває цю проблему.
7. **Блокування системного Event Loop:** Виклик блокувального сканування `esp_wifi_scan_start(..., true)` безпосередньо з контексту обробника подій Wi-Fi спричиняє взаємне блокування (Deadlock), оскільки подія `WIFI_EVENT_SCAN_DONE` не може бути доставлена у зайнятий потік.
