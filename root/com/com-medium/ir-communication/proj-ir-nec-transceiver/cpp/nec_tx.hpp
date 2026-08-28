// nec_tx.hpp - Генератор кадру C++ з RAII контролем носія
#pragma once

#include <cstdint>

namespace ir {

class NecTransmitter {
public:
    explicit NecTransmitter(void (*enable_carrier)(), void (*disable_carrier)(), void (*delay_func)(uint32_t))
        : enable_carrier_{enable_carrier}, disable_carrier_{disable_carrier}, delay_us_{delay_func} {}

    void send_frame(uint8_t address, uint8_t command) const {
        const uint32_t raw = static_cast<uint32_t>(address) |
                            (static_cast<uint32_t>(static_cast<uint8_t>(~address)) << 8) |
                            (static_cast<uint32_t>(command) << 16) |
                            (static_cast<uint32_t>(static_cast<uint8_t>(~command)) << 24);

        // Преамбула
        send_burst(9000, 4500);

        // 32 біти даних
        for (uint8_t i = 0; i < 32; ++i) {
            if (raw & (1UL << i)) {
                send_burst(560, 1690); // Біт '1'
            } else {
                send_burst(560, 560);  // Біт '0'
            }
        }

        // Кінцевий маркер
        send_burst(560, 0);
    }

    void send_repeat() const {
        send_burst(9000, 2250);
        send_burst(560, 0);
    }

private:
    void send_burst(uint32_t burst_us, uint32_t space_us) const {
        enable_carrier_();
        delay_us_(burst_us);
        disable_carrier_();
        if (space_us > 0) {
            delay_us_(space_us);
        }
    }

    void (*enable_carrier_)();
    void (*disable_carrier_)();
    void (*delay_us_)(uint32_t);
};

} // namespace ir
