#include <iostream>
#include <iomanip>

int main() {
    // 1. Базовий пакет
    const std::array<uint8_t, 10> pkt_v1 = {
        0x01, 0x02, 0xE4, 0x0C,
        0x02, 0x04, 0x96, 0x00, 0x00, 0x00
    };

    if (auto res = TlvStreamParser::parse(pkt_v1); res.has_value()) {
        std::cout << "Pkt v1 parsed: V=" << res->voltage_mv.value_or(0)
                  << " mV, I=" << res->current_ma.value_or(0)
                  << " mA, Temp_present=" << res->temperature_c_x100.has_value()
                  << ", Unknown=" << res->unknown_tags_count << "\n";
    }

    // 2. Розширений пакет із невідомим тегом 0x85
    const std::array<uint8_t, 22> pkt_v2 = {
        0x01, 0x02, 0xE4, 0x0C,
        0x85, 0x06, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF,
        0x03, 0x02, 0x2C, 0x09,
        0x04, 0x06, 'N', 'o', 'd', 'e', '-', '7'
    };

    if (auto res = TlvStreamParser::parse(pkt_v2); res.has_value()) {
        std::cout << "Pkt v2 parsed: V=" << res->voltage_mv.value_or(0)
                  << " mV, Temp=" << std::fixed << std::setprecision(2)
                  << (res->temperature_c_x100.value_or(0) / 100.0)
                  << " C, Name='" << res->device_name
                  << "', Unknown=" << res->unknown_tags_count << "\n";
    }

    // 3. Вкладений TLV
    const std::array<uint8_t, 12> pkt_nested = {
        0x05, 0x0A,
        0x10, 0x04, 0xC0, 0xA8, 0x01, 0x64,
        0x11, 0x02, 0x90, 0x1F
    };

    if (auto res = TlvStreamParser::parse(pkt_nested); res.has_value()) {
        std::cout << "Pkt nested parsed: IP_present=" << res->net_cfg.ip_address.has_value()
                  << ", Port=" << res->net_cfg.port.value_or(0) << "\n";
    }

    // 4. Зіпсований пакет
    const std::array<uint8_t, 4> pkt_corrupt = {
        0x01, 0x50, 0xE4, 0x0C
    };

    auto res_corrupt = TlvStreamParser::parse(pkt_corrupt);
    std::cout << "Corrupt packet valid: " << std::boolalpha << res_corrupt.has_value() << "\n";

    return 0;
}
