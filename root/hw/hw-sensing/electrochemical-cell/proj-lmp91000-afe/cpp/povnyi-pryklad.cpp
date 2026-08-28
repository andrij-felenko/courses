#include <chrono>
#include <thread>
#include <iostream>

struct HardwareI2cAdapter {
    bool write_register(uint8_t reg, uint8_t val) noexcept {
        return true;
    }
    bool read_register(uint8_t reg, uint8_t* val) noexcept {
        *val = 0x01;
        return true;
    }
};

extern float readAdcVoltageFromChannel() noexcept;

void runGasMonitorApplication() {
    using namespace sensing;
    HardwareI2cAdapter i2cBus;

    SensorParameters coParams{
        .gain = TIA_Gain::Gain_120k,
        .rload = RLoad::R_10Ohm,
        .internalZero = InternalZero::Zero_20Pct,
        .biasSign = BiasSign::Negative,
        .biasMag = BiasMagnitude::Bias_0Pct,
        .vrefVolts = 3.30f,
        .sensitivityNaPerPpm = 70.0f,
        .baselineCurrentNa = 2.5f
    };

    LMP91000 sensor(i2cBus, coParams);

    auto initResult = sensor.initialize();
    if (!initResult.has_value()) {
        return;
    }

    while (true) {
        sensor.setMode(OperationMode::TemperatureTiaOn, false);
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        float vTemp = readAdcVoltageFromChannel();
        float currentTemp = LMP91000<HardwareI2cAdapter>::rawToTemperature(vTemp);

        sensor.setMode(OperationMode::Amperometric3Lead, false);
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        float vGas = readAdcVoltageFromChannel();

        float coConcentrationPpm = sensor.calculateGasPpm(vGas, currentTemp);

        if (coConcentrationPpm > 35.0f) {
            /* Обробка небезпечної концентрації CO */
        }

        sensor.setMode(OperationMode::DeepSleep, true);
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }
}
