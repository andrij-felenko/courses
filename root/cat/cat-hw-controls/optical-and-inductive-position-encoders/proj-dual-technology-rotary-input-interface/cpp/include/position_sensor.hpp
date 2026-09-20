#pragma once

#include "encoder_types.hpp"
#include <cmath>
#include <string>

namespace controls::encoders {

/**
 * @brief Абстрактний базовий інтерфейс первинного давача положення.
 */
class IPositionSensor {
public:
    virtual ~IPositionSensor() = default;

    /**
     * @brief Зчитати поточне положення давача.
     */
    virtual EncoderPosition read_position() = 0;

    /**
     * @brief Виконати апаратне самотестування давача.
     */
    virtual bool self_test() = 0;

    /**
     * @brief Встановити зсув нульової точки (компенсація похибки).
     */
    virtual void set_zero_offset(double offset_deg) = 0;

    /**
     * @brief Отримати поточний зсув нульової точки.
     */
    virtual double get_zero_offset() const = 0;

    /**
     * @brief Отримати назву типу давача.
     */
    virtual std::string get_sensor_name() const = 0;
};

/**
 * @brief Реалізація оптичного квадратурного енкодера високої роздільної здатності.
 */
class OpticalEncoderSensor : public IPositionSensor {
public:
    explicit OpticalEncoderSensor(int32_t counts_per_rev = 4096);

    EncoderPosition read_position() override;
    bool self_test() override;
    void set_zero_offset(double offset_deg) override;
    double get_zero_offset() const override;
    std::string get_sensor_name() const override { return "Optical Quadrature Encoder"; }

    // Симуляційні методи для випробування та тестування
    void simulate_pulse_input(int32_t delta_pulses);
    void set_hardware_fault(bool fault);
    void set_index_pulse_detected(bool detected);

private:
    int32_t cpr_{4096};
    int32_t pulse_count_{0};
    double zero_offset_deg_{0.0};
    bool index_found_{false};
    SensorHealth health_{SensorHealth::OK};
    uint64_t clock_us_{0};
};

/**
 * @brief Реалізація індуктивного давача кутового переміщення (RVDT).
 */
class InductiveRvdtSensor : public IPositionSensor {
public:
    explicit InductiveRvdtSensor(double v_ref_volts = 5.0, double sensitivity_mv_per_deg = 50.0);

    EncoderPosition read_position() override;
    bool self_test() override;
    void set_zero_offset(double offset_deg) override;
    double get_zero_offset() const override;
    std::string get_sensor_name() const override { return "Inductive RVDT Sensor"; }

    // Симуляційні методи для випробування та тестування
    void simulate_adc_voltage(double voltage_volts);
    void set_hardware_fault(bool fault);

private:
    double v_ref_{5.0};
    double sensitivity_mv_per_deg_{50.0}; // 50 мВ / градус
    double raw_voltage_{2.5};             // 2.5 В відповідає 0 градусів
    double zero_offset_deg_{0.0};
    SensorHealth health_{SensorHealth::OK};
    uint64_t clock_us_{0};
};

} // namespace controls::encoders
