#include <iostream>
#include <iomanip>
#include <vector>
#include "max31865_sensor.hpp"
#include "rtd_math.hpp"

// Симуляція периферії мікроконтролера (SPI шина та системні тики)
class SimulatedMcuHardware {
public:
    uint32_t current_ticks_ms{1000};
    uint8_t registers[8]{};
    bool cs_line_state{true};

    SimulatedMcuHardware() {
        registers[MAX31865Sensor::REG_CONFIG] = 0x00;
        // Початкове значення АЦП для PT100 при 25.0 °C (опір ~109.73 Ом, Rref = 400 Ом)
        // Code = (109.73 / 400.0) * 32768 = 8989 (0x231D)
        uint16_t adc_code = 8989;
        uint16_t raw_reg = (adc_code << 1);
        registers[MAX31865Sensor::REG_RTD_MSB] = static_cast<uint8_t>(raw_reg >> 8);
        registers[MAX31865Sensor::REG_RTD_LSB] = static_cast<uint8_t>(raw_reg & 0xFF);
        registers[MAX31865Sensor::REG_FAULT_STATUS] = 0x00;
    }

    bool spiTransfer(const uint8_t* tx_data, uint8_t* rx_data, size_t length) {
        if (cs_line_state) return false; // CS має бути LOW
        if (length < 2) return false;

        uint8_t cmd = tx_data[0];
        bool is_write = (cmd & 0x80) != 0;
        uint8_t reg_addr = cmd & 0x7F;

        if (reg_addr > 0x07) return false;

        rx_data[0] = 0xFF; // Байт відповіді під час передачі команди

        if (is_write) {
            registers[reg_addr] = tx_data[1];
            // Якщо записано біт CONFIG_FAULT_CLEAR (біт 1), скидаємо регістр 0x07
            if (reg_addr == MAX31865Sensor::REG_CONFIG && (tx_data[1] & MAX31865Sensor::CONFIG_FAULT_CLEAR)) {
                registers[MAX31865Sensor::REG_FAULT_STATUS] = 0x00;
            }
        } else {
            for (size_t i = 1; i < length; ++i) {
                uint8_t current_reg = reg_addr + static_cast<uint8_t>(i - 1);
                rx_data[i] = (current_reg <= 0x07) ? registers[current_reg] : 0x00;
            }
        }
        return true;
    }
};

int main() {
    std::cout << "=========================================================\n";
    std::cout << "  C++ Драйвер MAX31865: PT100/PT1000 RTD-Перетворювач\n";
    std::cout << "=========================================================\n\n";

    SimulatedMcuHardware mcu;

    // Налаштування функцій зворотного виклику для абстракції апаратури
    SpiTransferFn spi_cb = [&mcu](const uint8_t* tx, uint8_t* rx, size_t len) {
        return mcu.spiTransfer(tx, rx, len);
    };
    GpioWriteFn cs_cb = [&mcu](bool state) {
        mcu.cs_line_state = state;
    };
    GetTickMsFn tick_cb = [&mcu]() {
        return mcu.current_ticks_ms;
    };

    // 1. Конфігурація системи вимірювання для 3-дротового PT100
    RtdConfig config{};
    config.type = RtdType::PT100;
    config.wire_mode = WireMode::ThreeWire;
    config.filter = FilterFrequency::Hz50;
    config.r_ref_ohm = 400.0f;
    config.r_0_ohm = 100.0f;
    config.lower_temp_limit = -50.0f;
    config.upper_temp_limit = 200.0f;

    MAX31865Sensor sensor(spi_cb, cs_cb, tick_cb);

    std::cout << "[Крок 1] Ініціалізація драйвера MAX31865...\n";
    if (sensor.begin(config)) {
        std::cout << " -> Драйвер успішно ініціалізовано. Стан FSM: Idle\n\n";
    } else {
        std::cerr << " -> Помилка ініціалізації драйвера!\n";
        return 1;
    }

    // 2. Асинхронний запуск вимірювання
    std::cout << "[Крок 2] Запуск асинхронного перетворення (1-Shot mode)...\n";
    sensor.startAsyncConversion();
    std::cout << " -> Стан FSM: BiasStabilizing (увімкнено VBIAS)\n";

    // Імітація проходження часу 10 мс для стабілізації струму VBIAS
    mcu.current_ticks_ms += 12;
    sensor.processFsm();
    std::cout << " -> Стан FSM після 12 мс: Converting (чекаємо DRDY)\n";

    // Імітація сигналу готовності АЦП від лінії DRDY через переривання EXTI
    std::cout << " -> Згенеровано зовнішнє переривання EXTI (DRDY Pin Low)\n";
    sensor.handleExtiInterrupt();

    // Просування FSM для зчитання даних
    sensor.processFsm();
    std::cout << " -> FSM опрацював дані АЦП. Поточний стан: Idle\n\n";

    // 3. Зчитання та виведення структурованої телеметрії
    std::cout << "[Крок 3] Аналіз підсумкової телеметрії вимірювання:\n";
    auto telemetry_opt = sensor.getLatestTelemetry();
    if (telemetry_opt.has_value()) {
        const auto& t = telemetry_opt.value();
        std::cout << std::fixed << std::setprecision(3);
        std::cout << " +---------------------------------------+\n";
        std::cout << " | Код АЦП (15-біт): " << std::setw(8) << t.raw_adc << "        |\n";
        std::cout << " | Опір RTD:         " << std::setw(8) << t.resistance_ohm << " Ом     |\n";
        std::cout << " | Температура:      " << std::setw(8) << t.temperature_c << " °C     |\n";
        std::cout << " | Статус даних:     " << (t.is_valid ? "  ВАЛІДНІ" : "НЕВАЛІДНІ") << "        |\n";
        std::cout << " | Мітка часу:       " << std::setw(8) << t.timestamp_ms << " мс     |\n";
        std::cout << " +---------------------------------------+\n\n";
    }

    // 4. Демонстрація роботи RAII-захисту RtdFaultGuard при виникненні несправностей
    std::cout << "[Крок 4] Симуляція апаратної несправності (обрив лінії RTD)...\n";
    // Симулюємо запис прапорця обриву лінії (біт 5 в регістрі 0x07)
    mcu.registers[MAX31865Sensor::REG_FAULT_STATUS] = (1 << 5);

    {
        std::cout << " -> Створення об'єкта RtdFaultGuard для автоматичного захисту...\n";
        RtdFaultGuard guard(sensor);

        if (guard.hasFault()) {
            std::cout << " [УВАГА] Виявлено апаратну несправність!\n";
            std::cout << "         Прапор REFIN- > 0.85*VBIAS (обрив FORCE- / коротке на VBIAS): "
                      << (guard.flags().refin_greater_than_085_vbias ? "ТАК" : "НІ") << "\n";
            std::cout << " -> Виконується захисна обробка в системі...\n";
        }
        std::cout << " -> Вихід із захищеного блоку (RAII деструктор скине прапорці помилок)...\n";
    }

    // Перевірка очищення регістра помилок після спрацювання деструктора
    FaultFlags post_fault_flags = sensor.readFaultRegister();
    std::cout << " -> Стан регістра помилок 0x07 після скидання RAII Guard: "
              << (post_fault_flags.anyFault() ? "АКТИВНІ ПОМИЛКИ" : "ОЧИЩЕНО (0x00)") << "\n\n";

    std::cout << "=========================================================\n";
    std::cout << "  Демонстрацію роботи C++ драйвера MAX31865 завершено.\n";
    std::cout << "=========================================================\n";

    return 0;
}
