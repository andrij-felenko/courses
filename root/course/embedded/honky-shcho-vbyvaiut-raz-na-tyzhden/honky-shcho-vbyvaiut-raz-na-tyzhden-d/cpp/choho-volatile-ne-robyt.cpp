#include <cstdint>
#include <array>

// НАЇВНИЙ, НЕБЕЗПЕЧНИЙ КОД
inline volatile bool g_data_ready{false};
inline volatile std::array<std::uint32_t, 4> g_shared_sensor_data{};

extern std::uint32_t read_adc_ch0() noexcept;
extern std::uint32_t read_adc_ch1() noexcept;
extern std::uint32_t read_adc_ch2() noexcept;
extern std::uint32_t read_adc_ch3() noexcept;
extern void transmit_telemetry(const std::uint32_t *data, std::size_t size) noexcept;

// Головний цикл
void update_sensor() noexcept {
    g_shared_sensor_data[0] = read_adc_ch0();
    g_shared_sensor_data[1] = read_adc_ch1();
    g_shared_sensor_data[2] = read_adc_ch2();
    g_shared_sensor_data[3] = read_adc_ch3();
    
    // Розробник сподівається, що це безпечно сповістить переривання
    g_data_ready = true;
}

// Обробник переривання періодичного опитування
extern "C" void TIM2_IRQHandler() noexcept {
    if (g_data_ready) {
        // ГОНКА: дані можуть бути передані неповністю сформованими
        transmit_telemetry(const_cast<const std::uint32_t *>(g_shared_sensor_data.data()), 
                           g_shared_sensor_data.size());
        g_data_ready = false;
    }
}
