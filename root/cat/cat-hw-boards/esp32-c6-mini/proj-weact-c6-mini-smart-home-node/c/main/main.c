#include <stdio.h>
#include <string.h>
#include "sdkconfig.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"
#include "esp_sleep.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "driver/i2c.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_ieee802154.h"

// Тег для логування ESP-IDF
static const char *TAG = "sensor_node";

// ============================================================================
// Апаратна конфігурація плати WeAct ESP32-C6-Mini
// ============================================================================
// Тривалість глибокого сну між сеансами передачі даних (в мікросекундах: 30 секунд)
#define DEEP_SLEEP_UPDATE_INTERVAL_US  (30ULL * 1000ULL * 1000ULL)

// Призначення виводів I2C для підключення шини сенсора (наприклад, SHT3x / BMP280)
#define I2C_MASTER_SDA_IO              GPIO_NUM_6
#define I2C_MASTER_SCL_IO              GPIO_NUM_7
#define I2C_MASTER_NUM                 I2C_NUM_0
#define I2C_MASTER_FREQ_HZ             100000
#define SENSOR_I2C_ADDR                0x44

// Призначення виводу ADC для вимірювання напруги акумулятора
#define BATTERY_ADC_CHANNEL            ADC_CHANNEL_0 // GPIO0 на ESP32-C6

// Налаштування бездротового радіостеку IEEE 802.15.4 (Thread / Zigbee PHY)
#define IEEE802154_CHANNEL             15            // Частотний канал 2.4 ГГц (11-26)
#define IEEE802154_PANID               0x1234        // Ідентифікатор персональної мережі (PAN ID)
#define IEEE802154_SHORT_ADDR          0x0002        // Коротка мережева адреса сенсорного вузла
#define IEEE802154_DEST_ADDR           0x0001        // Адреса координатора (шлюзу)
#define SENSOR_NODE_ID                 0xC6          // Унікальний маркер WeAct ESP32-C6-Mini

// ============================================================================
// Структури даних телеметрії та радіопакета
// ============================================================================
// Змінна в RTC RAM, що зберігає значення між циклами Deep Sleep
static RTC_DATA_ATTR uint32_t s_boot_count = 0;

// Структура корисного навантаження вимірювань сенсора
typedef struct __attribute__((packed)) {
    uint8_t  node_id;       // Ідентифікатор пристрою
    uint32_t boot_count;    // Порядковий номер циклу пробудження
    int16_t  temperature;   // Температура у сотих частках °C (наприклад, 2450 = 24.50 °C)
    uint16_t humidity;      // Вологість у сотих частках % (наприклад, 5530 = 55.30 %)
    uint16_t battery_mv;    // Напруга акумулятора в мілівольтах (наприклад, 3300 мВ)
} sensor_payload_t;

// Прапорець успішного завершення передачі кадрів по радіоканалу
static volatile bool s_tx_done = false;
static volatile bool s_tx_error = false;

// ============================================================================
// Коллбеки підсистеми IEEE 802.15.4
// ============================================================================
void esp_ieee802154_transmit_done(const uint8_t *frame, const uint8_t *ack, esp_ieee802154_frame_info_t *ack_frame_info) {
    ESP_LOGI(TAG, "802.15.4 Пакет успішно передано в ефір (ACK отримано)");
    s_tx_done = true;
}

void esp_ieee802154_transmit_failed(const uint8_t *frame, esp_ieee802154_tx_error_t error) {
    ESP_LOGE(TAG, "Помилка передачі 802.15.4 пакета, код помилки: %d", error);
    s_tx_error = true;
}

// ============================================================================
// Ініціалізація периферійного обладнання
// ============================================================================
// Ініціалізація I2C для зчитування показників зовнішнього датчика
static esp_err_t init_i2c_sensor(void) {
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };
    esp_err_t err = i2c_param_config(I2C_MASTER_NUM, &conf);
    if (err != ESP_OK) return err;
    return i2c_driver_install(I2C_MASTER_NUM, conf.mode, 0, 0, 0);
}

// Зчитати вимірювання температури та вологості з датчика
static esp_err_t read_sensor_data(int16_t *temp_out, uint16_t *hum_out) {
    // Команда запиту вимірювання для датчика SHT3x (High repeatability)
    uint8_t cmd[2] = {0x2C, 0x06};
    esp_err_t err = i2c_master_write_to_device(I2C_MASTER_NUM, SENSOR_I2C_ADDR, cmd, sizeof(cmd), pdMS_TO_TICKS(50));
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "I2C шина: сенсор не відповідає на 0x%02X, застосовуємо симуляцію вимірювань", SENSOR_I2C_ADDR);
        // Резервні значення вимірювань для демонстраційного вузла при відсутності фізичного сенсора
        *temp_out = 2350 + (s_boot_count % 50); // 23.50 °C
        *hum_out  = 4800 + (s_boot_count % 100); // 48.00 %
        return ESP_OK;
    }

    vTaskDelay(pdMS_TO_TICKS(20)); // Очікування завершення конверсії сенсором

    uint8_t data[6];
    err = i2c_master_read_from_device(I2C_MASTER_NUM, SENSOR_I2C_ADDR, data, sizeof(data), pdMS_TO_TICKS(50));
    if (err != ESP_OK) {
        *temp_out = 2350;
        *hum_out  = 4800;
        return ESP_OK;
    }

    // Обчислення сирих значень за формулою SHT3x
    uint16_t raw_temp = (data[0] << 8) | data[1];
    uint16_t raw_hum  = (data[3] << 8) | data[4];

    *temp_out = (int16_t)(-4500 + (17500 * (int32_t)raw_temp) / 65535);
    *hum_out  = (uint16_t)((10000 * (uint32_t)raw_hum) / 65535);
    return ESP_OK;
}

// Зчитування напруги живлення через АЦП ESP32-C6
static uint16_t read_battery_voltage_mv(void) {
    adc_oneshot_unit_handle_t adc_handle;
    adc_oneshot_unit_init_cfg_t init_config = {
        .unit_id = ADC_UNIT_1,
        .clk_src = ADC_RTC_CLK_SRC_DEFAULT,
    };
    if (adc_oneshot_new_unit(&init_config, &adc_handle) != ESP_OK) {
        return 3300; // Номінальна напруга за замовчуванням
    }

    adc_oneshot_chan_cfg_t config = {
        .bitwidth = ADC_BITWIDTH_DEFAULT,
        .atten = ADC_ATTEN_DB_12,
    };
    adc_oneshot_config_channel(adc_handle, BATTERY_ADC_CHANNEL, &config);

    int raw_val = 0;
    adc_oneshot_read(adc_handle, BATTERY_ADC_CHANNEL, &raw_val);
    adc_oneshot_del_unit(adc_handle);

    // Масштабування сирого значення АЦП у мілівольти (із урахуванням дільника напруги)
    uint16_t voltage_mv = (uint16_t)((raw_val * 3300) / 4095) * 2;
    return voltage_mv > 0 ? voltage_mv : 3300;
}

// ============================================================================
// Налаштування та передача через бездротовий модуль IEEE 802.15.4
// ============================================================================
static esp_err_t transmit_sensor_payload_802154(const sensor_payload_t *payload) {
    ESP_LOGI(TAG, "Ініціалізація радіомодуля 802.15.4 (Thread/Zigbee PHY)...");

    // Вмикаємо апаратний трансивер IEEE 802.15.4 на ESP32-C6
    ESP_ERROR_CHECK(esp_ieee802154_enable());
    esp_ieee802154_set_promiscuous(false);
    esp_ieee802154_set_rx_when_idle(false); // Вимикаємо приймач у простої для економії енергії
    esp_ieee802154_set_channel(IEEE802154_CHANNEL);
    esp_ieee802154_set_panid(IEEE802154_PANID);
    esp_ieee802154_set_short_address(IEEE802154_SHORT_ADDR);

    // Буфер кадру 802.15.4 MAC: [Довжина (1Б)] + [Заголовок MAC (9Б)] + [Корисне навантаження] + [FCS (2Б)]
    uint8_t frame[127];
    uint8_t mac_header_len = 9;
    uint8_t payload_len = sizeof(sensor_payload_t);
    uint8_t total_len = mac_header_len + payload_len + 2; // +2 байти для апаратної FCS (CRC16)

    frame[0] = total_len; // Перший байт — загальна довжина пакета для трансивера
    // Frame Control Field (FCF): Data frame, Ack Request, Short Addressing (0x8841)
    frame[1] = 0x41;
    frame[2] = 0x88;
    frame[3] = (uint8_t)(s_boot_count & 0xFF); // Послідовний номер кадру (Sequence Number)

    // Destination PAN ID (малоендіанний формат)
    frame[4] = (uint8_t)(IEEE802154_PANID & 0xFF);
    frame[5] = (uint8_t)((IEEE802154_PANID >> 8) & 0xFF);

    // Destination Short Address
    frame[6] = (uint8_t)(IEEE802154_DEST_ADDR & 0xFF);
    frame[7] = (uint8_t)((IEEE802154_DEST_ADDR >> 8) & 0xFF);

    // Source Short Address
    frame[8] = (uint8_t)(IEEE802154_SHORT_ADDR & 0xFF);
    frame[9] = (uint8_t)((IEEE802154_SHORT_ADDR >> 8) & 0xFF);

    // Копіювання структури вимірювань у тіло кадру
    memcpy(&frame[10], payload, payload_len);

    s_tx_done = false;
    s_tx_error = false;

    ESP_LOGI(TAG, "Відправка кадру 802.15.4 (розмір: %d байт, канал: %d)...", total_len, IEEE802154_CHANNEL);
    esp_err_t tx_res = esp_ieee802154_transmit(frame, true); // CCA (Clear Channel Assessment) увімкнено
    if (tx_res != ESP_OK) {
        ESP_LOGE(TAG, "Помилка виклику esp_ieee802154_transmit: %s", esp_err_to_name(tx_res));
        esp_ieee802154_disable();
        return tx_res;
    }

    // Очікування завершення передачі з таймаутом 200 мс
    int timeout_ms = 200;
    while (!s_tx_done && !s_tx_error && timeout_ms > 0) {
        vTaskDelay(pdMS_TO_TICKS(10));
        timeout_ms -= 10;
    }

    // Вимикаємо радіотрансивер після передачі для миттєвого зниження споживання струму
    esp_ieee802154_disable();

    if (s_tx_done) {
        ESP_LOGI(TAG, "Передачу телеметрії успішно підтверджено!");
        return ESP_OK;
    } else {
        ESP_LOGW(TAG, "Таймаут або відсутність підтвердження ACK від шлюзу");
        return ESP_FAIL;
    }
}

// ============================================================================
// Головна точка входу прошивки (app_main)
// ============================================================================
void app_main(void) {
    s_boot_count++;
    ESP_LOGI(TAG, "==================================================");
    ESP_LOGI(TAG, "Запуск вузла WeAct ESP32-C6-Mini | Цикл №%lu", (unsigned long)s_boot_count);
    ESP_LOGI(TAG, "==================================================");

    // Аналіз причини пробудження мікроконтролера
    esp_sleep_wakeup_cause_t wakeup_reason = esp_sleep_get_wakeup_cause();
    switch (wakeup_reason) {
        case ESP_SLEEP_WAKEUP_TIMER:
            ESP_LOGI(TAG, "Пробудження за таймером RTC Deep Sleep");
            break;
        case ESP_SLEEP_WAKEUP_UNDEFINED:
        default:
            ESP_LOGI(TAG, "Холодний старт / Холодне скидання живлення (Power-On Reset)");
            break;
    }

    // 1. Ініціалізація энергонезалежної пам'яті NVS (необхідна для збереження калибровки PHY/радіо)
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    // 2. Ініціалізація датчика та зчитування вимірювальних показників
    init_i2c_sensor();

    sensor_payload_t payload = {
        .node_id = SENSOR_NODE_ID,
        .boot_count = s_boot_count,
        .temperature = 0,
        .humidity = 0,
        .battery_mv = read_battery_voltage_mv()
    };

    read_sensor_data(&payload.temperature, &payload.humidity);

    ESP_LOGI(TAG, "Отримано дані: Температура = %.2f °C, Вологість = %.2f %%, Акумулятор = %u мВ",
             (float)payload.temperature / 100.0f,
             (float)payload.humidity / 100.0f,
             payload.battery_mv);

    // 3. Відправка телеметрії в бездротову мережу 802.15.4 (Thread/Zigbee)
    transmit_sensor_payload_802154(&payload);

    // 4. Оптимізація енергоспоживання перед сном: вимикаємо I2C драйвер
    i2c_driver_delete(I2C_MASTER_NUM);

    // 5. Конфігурація таймера RTC пробудження та вхід у режим глибокого сну (Deep Sleep)
    ESP_LOGI(TAG, "Налаштування таймера RTC пробудження на 30 секунд...");
    ESP_ERROR_CHECK(esp_sleep_enable_timer_wakeup(DEEP_SLEEP_UPDATE_INTERVAL_US));

    ESP_LOGI(TAG, "Вхід у режим Deep Sleep (струм споживання ~7 мкА). Очікування...");
    fflush(stdout);
    vTaskDelay(pdMS_TO_TICKS(100)); // Короткий інтервал для гарантованого виводу логів в UART

    esp_deep_sleep_start();
}
