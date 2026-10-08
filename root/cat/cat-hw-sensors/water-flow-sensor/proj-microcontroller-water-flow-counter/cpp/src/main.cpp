#include <iostream>
#include <chrono>
#include <thread>
#include "water_flow_sensor.hpp"
#include "power_monitor.hpp"
#include "oled_display.hpp"
#include "mqtt_telemetry.hpp"

// Симуляція надходження імпульсів від Холлівського давача витратоміра
void simulate_water_flow(uint32_t current_time_ms) {
    // Симулюємо відкритий кран з 1-ї по 10-ту секунду (близько 40 Гц = ~5.3 л/хв)
    if (current_time_ms > 1000 && current_time_ms < 10000) {
        for (int p = 0; p < 4; ++p) {
            WaterFlowSensor::handle_interrupt();
        }
    }
}

int main() {
    std::cout << "=== Вбудована система обліку витрати води (G1/2\" Турбіна + Холл) ===\n\n";

    const uint8_t FLOW_SENSOR_PIN = 4;
    const uint8_t BATTERY_ADC_PIN = 34;
    const float YF_S201_K_FACTOR = 7.5f; // K-factor (Гц / (л/хв))

    WaterFlowSensor flow_sensor(FLOW_SENSOR_PIN, YF_S201_K_FACTOR);
    PowerMonitor power_monitor(BATTERY_ADC_PIN);
    OledDisplay oled_display(0x3C);
    MqttTelemetry mqtt_client("mqtt://broker.hivemq.com:1883", "water_meter_node1", "telemetry/water_meter");

    // Ініціалізація програмних модулів
    flow_sensor.begin();
    power_monitor.begin();
    oled_display.begin();
    mqtt_client.begin();

    std::cout << "\n[INFO] Підключення апаратного переривання ISR на GPIO pin " 
              << static_cast<int>(FLOW_SENSOR_PIN) << " (RISING edge)\n";

    auto start_time = std::chrono::steady_clock::now();

    // Основний цикловий потік мікроконтролера (Main Loop)
    for (int i = 0; i < 15; ++i) {
        auto now = std::chrono::steady_clock::now();
        uint32_t current_time_ms = static_cast<uint32_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count()
        );

        // 1. Генерація імпульсів давача (в реальному МК викликається апаратним перериванням)
        simulate_water_flow(current_time_ms);

        // 2. Моніторинг живлення
        power_monitor.update(current_time_ms);

        // 3. Динамічне коригування періоду відправки при зміні стану живлення
        if (power_monitor.is_low_power_mode()) {
            mqtt_client.set_publish_interval(10000); // 10 секунд при низькому заряді
        } else {
            mqtt_client.set_publish_interval(3000);  // 3 секунди при нормальному живленні
        }

        // 4. Оновлення лічильників та розрахунок витрати води
        flow_sensor.update(current_time_ms);

        // 5. Локальне відображення метрик на OLED-дисплеї
        FlowMetrics metrics = flow_sensor.get_metrics();
        oled_display.render(metrics, power_monitor.get_power_state(), current_time_ms);

        // 6. Відправка телеметрії в MQTT-брокер
        mqtt_client.publish_telemetry(metrics, power_monitor.get_voltage(), current_time_ms);

        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

    std::cout << "\n=== Облік витрати води успішно виконано ===\n";
    return 0;
}
