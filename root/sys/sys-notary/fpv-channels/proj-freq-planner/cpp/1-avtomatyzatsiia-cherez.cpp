#include <cstdint>
#include <array>

/* Ідіоматична структура пакета конфігурації VTX у C++ */
struct alignas(1) MspVtxConfigPayload {
    uint8_t  vtx_type{1};         // 1 = SmartAudio, 2 = Tramp
    uint16_t frequency_mhz{5658}; // Несуча частота
    uint8_t  power_level{1};      // Індекс рівня потужності
    uint8_t  pit_mode{0};         // 0 = Off, 1 = On
    uint8_t  band{5};             // 5 = Raceband
    uint8_t  channel{1};          // 1 = R1
};
