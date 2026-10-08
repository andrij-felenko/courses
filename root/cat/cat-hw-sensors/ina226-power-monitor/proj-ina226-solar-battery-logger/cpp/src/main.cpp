#include "power_logger.hpp"
#include <iostream>
#include <iomanip>
#include <unordered_map>
#include <cmath>

namespace power_monitor {

/**
 * @brief Симуляція шини I2C для тестування та демонстрації роботи без наявності фізичного заліза.
 */
class SimulatedI2CBus : public I2CBus {
public:
    SimulatedI2CBus() {
        // Заповнення ідентифікаторів виробника та кристала за замовчуванням
        registers_[Ina226Driver::REG_MANUFACTURER_ID] = Ina226Driver::EXPECTED_MANUFACTURER_ID;
        registers_[Ina226Driver::REG_DIE_ID]          = Ina226Driver::EXPECTED_DIE_ID;
        registers_[Ina226Driver::REG_CONFIG]          = 0x4127;
    }

    /**
     * @brief Симуляція фізичного стану системи живлення (напруга акумулятора та струм).
     */
    void set_hardware_state(double bus_voltage_v, double current_a, double r_shunt_ohms) {
        sim_bus_voltage_v_ = bus_voltage_v;
        sim_current_a_ = current_a;
        r_shunt_ohms_ = r_shunt_ohms;
        update_simulated_registers();
    }

    bool write_register(uint8_t dev_addr, uint8_t reg_addr, uint16_t value) override {
        (void)dev_addr; // Маскування невикористаного параметра
        registers_[reg_addr] = value;

        if (reg_addr == Ina226Driver::REG_CALIBRATION) {
            cal_val_ = value;
            if (cal_val_ > 0 && r_shunt_ohms_ > 0.0) {
                current_lsb_ = 0.00512 / (static_cast<double>(cal_val_) * r_shunt_ohms_);
                power_lsb_ = 25.0 * current_lsb_;
            }
            update_simulated_registers();
        }
        return true;
    }

    bool read_register(uint8_t dev_addr, uint8_t reg_addr, uint16_t& value) override {
        (void)dev_addr;
        auto it = registers_.find(reg_addr);
        if (it != registers_.end()) {
            value = it->second;
            return true;
        }
        value = 0;
        return false;
    }

private:
    void update_simulated_registers() {
        // 1. Напруга шини (LSB = 1.25 мВ)
        uint16_t raw_bus = static_cast<uint16_t>(sim_bus_voltage_v_ / 0.00125);
        registers_[Ina226Driver::REG_BUS_VOLTAGE] = raw_bus;

        // 2. Напруга на шунті (LSB = 2.5 мкВ = 0.0000025 В)
        double v_shunt_v = sim_current_a_ * r_shunt_ohms_;
        int16_t raw_shunt = static_cast<int16_t>(v_shunt_v / 0.0000025);
        registers_[Ina226Driver::REG_SHUNT_VOLTAGE] = static_cast<uint16_t>(raw_shunt);

        // 3. Струм та потужність (якщо записано регістр Calibration)
        if (current_lsb_ > 0.0 && power_lsb_ > 0.0) {
            int16_t raw_current = static_cast<int16_t>(sim_current_a_ / current_lsb_);
            registers_[Ina226Driver::REG_CURRENT] = static_cast<uint16_t>(raw_current);

            double p_w = std::abs(sim_current_a_) * sim_bus_voltage_v_;
            uint16_t raw_power = static_cast<uint16_t>(p_w / power_lsb_);
            registers_[Ina226Driver::REG_POWER] = raw_power;
        }
    }

    std::unordered_map<uint8_t, uint16_t> registers_;
    double sim_bus_voltage_v_{12.0};
    double sim_current_a_{0.0};
    double r_shunt_ohms_{0.002};
    uint16_t cal_val_{0};
    double current_lsb_{0.0};
    double power_lsb_{0.0};
};

/**
 * @brief Допоміжна функція форматованого виводу поточних метрик у консоль.
 */
void print_metrics(const std::string& stage_name, const PowerMetrics& m) {
    std::cout << std::left << std::setw(22) << stage_name
              << " | V: " << std::fixed << std::setprecision(3) << std::setw(6) << m.bus_voltage_v << " В"
              << " | I: " << std::setw(7) << m.current_a << " А"
              << " | P: " << std::setw(6) << m.power_w << " Вт"
              << " | +Ah: " << std::setw(7) << m.charge_ah
              << " | -Ah: " << std::setw(7) << m.discharge_ah
              << " | Net Ah: " << std::setw(7) << m.net_ah
              << " | +Wh: " << std::setw(7) << m.charge_wh
              << " | -Wh: " << std::setw(7) << m.discharge_wh
              << " | Net Wh: " << std::setw(7) << m.net_wh << "\n";
}

} // namespace power_monitor

int main() {
    using namespace power_monitor;

    std::cout << "===============================================================================\n";
    std::cout << "   ЦИФРОВИЙ МОНІТОР ЖИВЛЕННЯ INA226: ДВОНАПРЯМЛЕНИЙ ОБЛІК І ЕНЕРГОЗБЕРЕЖЕННЯ  \n";
    std::cout << "===============================================================================\n\n";

    // Параметри апаратного забезпечення
    constexpr double R_SHUNT_OHMS = 0.002;        // Шунт 2 мОм (0.002 Ом)
    constexpr double MAX_EXPECTED_CURRENT_A = 15.0; // Максимальний струм 15 А

    SimulatedI2CBus i2c_bus;
    Ina226Driver driver(i2c_bus, Ina226Driver::DEFAULT_I2C_ADDR);
    PowerLogger logger(driver);

    // Ініціалізація та калібрування
    if (!logger.init(R_SHUNT_OHMS, MAX_EXPECTED_CURRENT_A)) {
        std::cerr << "Помилка ініціалізації монітора живлення INA226!\n";
        return 1;
    }

    std::cout << "Калібрування успішне!\n";
    std::cout << "  - Значення CAL: 0x" << std::hex << driver.get_calibration_raw() << std::dec << " (" << driver.get_calibration_raw() << ")\n";
    std::cout << "  - Current LSB:  " << driver.get_current_lsb() * 1e6 << " мкА/LSB\n";
    std::cout << "  - Power LSB:    " << driver.get_power_lsb() * 1e3 << " мВт/LSB\n\n";

    std::cout << "--- ЕТАП 1: Моделювання процесу ЗАРЯДУ акумулятора (+3.5 А, 12.6 В) ---\n";
    i2c_bus.set_hardware_state(12.60, 3.50, R_SHUNT_OHMS);
    
    constexpr double DT_SEC = 60.0; // Крок оновлення 60 секунд (1 хвилина)
    for (int i = 1; i <= 5; ++i) {
        logger.update(DT_SEC);
        print_metrics("Заряд (хв " + std::to_string(i) + ")", logger.get_metrics());
    }

    std::cout << "\n--- ЕТАП 2: Моделювання процесу РОЗРЯДУ під навантаженням (-5.2 А, 11.8 В) ---\n";
    i2c_bus.set_hardware_state(11.80, -5.20, R_SHUNT_OHMS);

    for (int i = 1; i <= 5; ++i) {
        logger.update(DT_SEC);
        print_metrics("Розряд (хв " + std::to_string(i + 5) + ")", logger.get_metrics());
    }

    std::cout << "\n--- ЕТАП 3: Демонстрація сплячого режиму (Power-Down Mode) ---\n";
    std::cout << "Переведення INA226 у сплячий режим...\n";
    logger.enter_sleep();
    std::cout << "Стан сну: " << (logger.is_sleeping() ? "СПИТЬ (Power-Down)" : "АКТИВНИЙ") << "\n";

    // Спроба оновлення під час сну повинна повертати false
    bool update_res = logger.update(DT_SEC);
    std::cout << "Результат update() під час сну: " << (update_res ? "УСПІХ" : "ВІДХИЛЕНО (Збереження енергії)") << "\n";

    std::cout << "Пробудження INA226...\n";
    logger.wake_up();
    std::cout << "Стан сну: " << (logger.is_sleeping() ? "СПИТЬ" : "АКТИВНИЙ (Continuous Mode)") << "\n";

    // Оновлення після пробудження
    i2c_bus.set_hardware_state(12.10, 1.20, R_SHUNT_OHMS);
    logger.update(DT_SEC);
    print_metrics("Після пробудження", logger.get_metrics());

    std::cout << "\n===============================================================================\n";
    std::cout << "                       ПІДСУМКОВИЙ ЗВІТ МОНІТОРИНГУ                            \n";
    std::cout << "===============================================================================\n";
    const auto& final_m = logger.get_metrics();
    std::cout << " Загальний тривалість моніторингу: " << final_m.total_time_sec << " с (" << final_m.total_time_sec / 60.0 << " хв)\n";
    std::cout << " Накопичено при заряді (+Ah):     " << final_m.charge_ah << " А·год\n";
    std::cout << " Віддано при розряді (-Ah):       " << final_m.discharge_ah << " А·год\n";
    std::cout << " Підсумковий баланс ємності (Net): " << final_m.net_ah << " А·год\n";
    std::cout << " Накопичена енергія заряду (+Wh):  " << final_m.charge_wh << " Вт·год\n";
    std::cout << " Спожита енергія розряду (-Wh):   " << final_m.discharge_wh << " Вт·год\n";
    std::cout << " Підсумковий баланс енергії (Net): " << final_m.net_wh << " Вт·год\n";
    std::cout << "===============================================================================\n";

    return 0;
}
