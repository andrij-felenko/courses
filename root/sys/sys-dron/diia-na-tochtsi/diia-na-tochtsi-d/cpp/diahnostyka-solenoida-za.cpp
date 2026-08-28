#include <cstdint>

namespace drone::payload {

// Класифікація результату спрацьовування соленоїда за профілем струму
enum class SolenoidStatus : uint8_t {
    Released = 0,        // успішний скид (виявлено індуктивний провал)
    OpenCircuit,         // обрив ланцюга (струм відсутній)
    MechanicalJam,       // заклинювання сердечника (провал відсутній)
    OvercurrentShort     // коротке замикання (струм понад поріг)
};

} // namespace drone::payload
