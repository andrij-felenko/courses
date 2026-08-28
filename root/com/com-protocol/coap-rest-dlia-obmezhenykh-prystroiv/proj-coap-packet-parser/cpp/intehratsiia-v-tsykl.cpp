#include <iostream>
#include <cstring>

int main() {
    const uint8_t raw_req[] = {
        0x41, 0x01, 0x12, 0x34,
        0xAB,
        0xB7, 's', 'e', 'n', 's', 'o', 'r', 's',
        0x04, 't', 'e', 'm', 'p'
    };

    auto result = coap::PacketView::parse(raw_req);
    if (!result.has_value()) {
        return 1;
    }

    const auto& pkt = result.value();
    if (pkt.code == 1 && pkt.option_count == 2) {
        auto opt = pkt.find_option(11); // Uri-Path
        if (opt.has_value() && opt->as_string() == "sensors") {
            return 0; // Тест пройдено успішно
        }
    }

    return 1;
}
