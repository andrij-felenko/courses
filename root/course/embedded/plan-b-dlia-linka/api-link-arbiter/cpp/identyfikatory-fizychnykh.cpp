#include <cstdint>

namespace link_api {

enum class BearerId : uint8_t {
    Primary  = 0,  // Високошвидкісний канал (2.4 ГГц Wi-Fi / 5.8 ГГц OFDM)
    Fallback = 1,  // Резервний далекобійний канал (Sub-GHz LoRa / FSK)
    Relay    = 2,  // Естафетний ретранслятор (Mesh вузол)
    Count    = 3
};

} // namespace link_api
