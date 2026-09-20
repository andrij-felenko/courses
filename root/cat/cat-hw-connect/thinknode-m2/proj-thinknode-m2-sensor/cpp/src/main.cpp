#include <Arduino.h>
#include <RadioLib.h>
#include <string>
#include "driver/temperature_sensor.h"
#include "config.h"

// Структура для зберігання показань сенсорів
struct SensorReadings {
    float mcu_temperature;

    std::string to_string() const {
        return "Temp: " + std::to_string(mcu_temperature) + "C";
    }
};

// Клас, що інкапсулює логіку сенсорного вузла
class SensorNode {
public:
    SensorNode(int cs, int irq, int rst, int busy) 
        : radio_module(cs, irq, rst, busy), radio(&radio_module) {}

    ~SensorNode() {
        if (temp_sensor) {
            temperature_sensor_disable(temp_sensor);
            temperature_sensor_uninstall(temp_sensor);
        }
    }

    bool initialize() {
        // Ініціалізація внутрішнього температурного сенсора ESP32-S3
        temperature_sensor_config_t temp_sensor_config = TEMPERATURE_SENSOR_CONFIG_DEFAULT(-10, 80);
        temperature_sensor_install(&temp_sensor_config, &temp_sensor);
        temperature_sensor_enable(temp_sensor);

        // Ініціалізація радіомодуля SX1262
        int state = radio.begin(
            config::frequency_mhz, 
            config::bandwidth_khz, 
            config::spreading_factor, 
            config::coding_rate, 
            0x12, // Синхронізаційне слово
            config::tx_power_dbm
        );
        return state == RADIOLIB_ERR_NONE;
    }

    SensorReadings read_sensors() {
        float temp_c = 0.0f;
        if (temp_sensor) {
            temperature_sensor_get_celsius(temp_sensor, &temp_c);
        }
        return SensorReadings{temp_c};
    }

    bool send_data(const SensorReadings& data) {
        std::string payload = data.to_string();
        int state = radio.transmit(payload.c_str());
        return state == RADIOLIB_ERR_NONE;
    }

    void sleep_radio() {
        radio.sleep();
    }

private:
    Module radio_module;
    SX1262 radio;
    temperature_sensor_handle_t temp_sensor = nullptr;
};

void setup() {
    Serial.begin(115200);
    Serial.println("Пробудження вузла...");

    SensorNode node(config::pin_lora_cs, config::pin_lora_dio1, config::pin_lora_rst, config::pin_lora_busy);

    if (node.initialize()) {
        auto data = node.read_sensors();
        Serial.printf("Зібрані дані: %s\n", data.to_string().c_str());
        
        if (node.send_data(data)) {
            Serial.println("Пакет відправлено успішно.");
        } else {
            Serial.println("Помилка відправки пакета.");
        }
        node.sleep_radio();
    } else {
        Serial.println("Помилка ініціалізації вузла.");
    }

    Serial.printf("Перехід у глибокий сон на %llu секунд...\n", config::deep_sleep_duration_us / 1000000ULL);
    
    esp_sleep_enable_timer_wakeup(config::deep_sleep_duration_us);
    esp_deep_sleep_start();
}

void loop() {
    // Основний цикл не використовується через глибокий сон
}
