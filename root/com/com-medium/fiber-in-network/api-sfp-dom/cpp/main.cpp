#include <iostream>
#include <cstdint>
#include <cmath>
#include <span>
#include <expected>
#include <format>
#include <string_view>

namespace photonics::sff8472 {

struct DomTelemetry {
    float temperature_c{0.0f};
    float vcc_volts{0.0f};
    float tx_bias_ma{0.0f};
    float tx_power_mw{0.0f};
    float tx_power_dbm{-40.0f};
    float rx_power_mw{0.0f};
    float rx_power_dbm{-40.0f};
    bool data_ready{false};
    bool rx_los{false};
    bool tx_fault{false};
};

class Sff8472Decoder {
public:
    [[nodiscard]] static std::expected<DomTelemetry, std::string_view>
    parse_page_a2(std::span<const uint8_t, 128> page_a2) noexcept {
        DomTelemetry data{};

        // 1. Температура
        const auto raw_temp = static_cast<int16_t>((page_a2[96] << 8) | page_a2[97]);
        data.temperature_c = static_cast<float>(raw_temp) / 256.0f;

        // 2. Напруга VCC
        const auto raw_vcc = static_cast<uint16_t>((page_a2[98] << 8) | page_a2[99]);
        data.vcc_volts = static_cast<float>(raw_vcc) / 10000.0f;

        // 3. Струм зміщення лазера
        const auto raw_bias = static_cast<uint16_t>((page_a2[100] << 8) | page_a2[101]);
        data.tx_bias_ma = static_cast<float>(raw_bias) / 500.0f;

        // 4. Оптична потужність TX
        const auto raw_tx = static_cast<uint16_t>((page_a2[102] << 8) | page_a2[103]);
        data.tx_power_mw = static_cast<float>(raw_tx) / 10000.0f;
        if (data.tx_power_mw > 1e-5f) {
            data.tx_power_dbm = 10.0f * std::log10(data.tx_power_mw);
        }

        // 5. Оптична потужність RX
        const auto raw_rx = static_cast<uint16_t>((page_a2[104] << 8) | page_a2[105]);
        data.rx_power_mw = static_cast<float>(raw_rx) / 10000.0f;
        if (data.rx_power_mw > 1e-5f) {
            data.rx_power_dbm = 10.0f * std::log10(data.rx_power_mw);
        }

        // 6. Прапорці стану
        data.data_ready = (page_a2[110] & 0x01) == 0;
        data.tx_fault   = (page_a2[112] & (1 << 2)) != 0;
        data.rx_los     = (page_a2[112] & (1 << 1)) != 0;

        return data;
    }
};

} // namespace photonics::sff8472

int main() {
    using namespace photonics::sff8472;

    uint8_t page_a2_data[128] = {0};
    page_a2_data[96] = 0x23; page_a2_data[97] = 0x00; // 35.0 °C
    page_a2_data[98] = 0x81; page_a2_data[99] = 0x48; // 3.31 В
    page_a2_data[100] = 0x24; page_a2_data[101] = 0x40; // 18.5 мА
    page_a2_data[102] = 0x31; page_a2_data[103] = 0x34; // +1.0 дБм
    page_a2_data[104] = 0x00; page_a2_data[105] = 0xC8; // -17.0 дБм

    auto dom_result = Sff8472Decoder::parse_page_a2(page_a2_data);

    if (dom_result) {
        const auto& d = dom_result.value();
        std::cout << std::format("=== ДІАГНОСТИКА SFP МОДУЛЯ (C++23) ===\n");
        std::cout << std::format("Температура:      {:.2f} °C\n", d.temperature_c);
        std::cout << std::format("Напруга живлення: {:.2f} В\n", d.vcc_volts);
        std::cout << std::format("Струм зміщення:   {:.2f} мА\n", d.tx_bias_ma);
        std::cout << std::format("Вихідна потужність TX: {:.3f} мВт ({:.2f} дБм)\n", d.tx_power_mw, d.tx_power_dbm);
        std::cout << std::format("Приймана потужність RX: {:.4f} мВт ({:.2f} дБм)\n", d.rx_power_mw, d.rx_power_dbm);
        std::cout << std::format("Статус RX LOS:    {}\n", d.rx_los ? "АВАРІЯ (НЕМАЄ СИГНАЛУ)" : "ОК (СИГНАЛ Є)");
    } else {
        std::cerr << "Помилка декодування сторінки A2h: " << dom_result.error() << '\n';
    }

    return 0;
}
