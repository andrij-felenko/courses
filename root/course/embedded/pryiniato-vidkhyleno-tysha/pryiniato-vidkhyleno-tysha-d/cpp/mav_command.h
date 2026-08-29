#pragma once

// Типи повідомлень MAVLink, потрібні для транзакції «команда — квитанція»:
// COMMAND_LONG (msgid 76), COMMAND_INT (msgid 75), COMMAND_ACK (msgid 77).

#include <cmath>
#include <cstdint>
#include <stdexcept>

// Коди переліку MAV_RESULT — поле result у COMMAND_ACK.
enum class MavResult : std::uint8_t {
    Accepted            = 0,
    TemporarilyRejected = 1,
    Denied              = 2,
    Unsupported         = 3,
    Failed              = 4,
    InProgress          = 5,
    Cancelled           = 6,
    CommandLongOnly     = 7,
    CommandIntOnly      = 8,
};

inline const char* result_name(MavResult r) {
    switch (r) {
        case MavResult::Accepted:            return "ACCEPTED";
        case MavResult::TemporarilyRejected: return "TEMPORARILY_REJECTED";
        case MavResult::Denied:              return "DENIED";
        case MavResult::Unsupported:         return "UNSUPPORTED";
        case MavResult::Failed:              return "FAILED";
        case MavResult::InProgress:          return "IN_PROGRESS";
        case MavResult::Cancelled:           return "CANCELLED";
        case MavResult::CommandLongOnly:     return "COMMAND_LONG_ONLY";
        case MavResult::CommandIntOnly:      return "COMMAND_INT_ONLY";
    }
    return "?";
}

// Підмножина словника MAV_CMD, яку вживає цей приклад.
namespace mav_cmd {
inline constexpr std::uint16_t NavLoiterUnlim     = 17;     // навігаційна: лише COMMAND_INT
inline constexpr std::uint16_t NavTakeoff         = 22;
inline constexpr std::uint16_t DoSetMode          = 176;
inline constexpr std::uint16_t DoDigicamControl   = 203;    // спуск затвора — неідемпотентна
inline constexpr std::uint16_t DoGripper          = 211;    // захоплення/скидання вантажу
inline constexpr std::uint16_t ComponentArmDisarm = 400;
inline constexpr std::uint16_t DoStartMagCal      = 42424;  // довга операція з прогресом
}  // namespace mav_cmd

// Прапорець param1 у DO_SET_MODE: далі в param2 їде номер користувацького режиму.
inline constexpr float kCustomModeEnabled = 1.0f;
// Магічне число ArduPilot: примусове глушіння моторів у повітрі.
inline constexpr float kForceDisarmMagic = 21196.0f;

// Системи відліку COMMAND_INT (перелік MAV_FRAME).
enum class MavFrame : std::uint8_t {
    Global               = 0,
    GlobalRelativeAlt    = 3,
    GlobalInt            = 5,
    GlobalRelativeAltInt = 6,
};

// COMMAND_LONG: сім параметрів float32, є лічильник повторів confirmation.
struct CommandLong {
    std::uint8_t  target_system    = 1;
    std::uint8_t  target_component = 1;
    std::uint16_t command          = 0;
    std::uint8_t  confirmation     = 0;
    float         param[7]         = {0, 0, 0, 0, 0, 0, 0};

    // Поля ЗАГОЛОВКА кадру, не тіла повідомлення: хто відправив. Їх виставляє клієнт.
    std::uint8_t src_system    = 255;
    std::uint8_t src_component = 190;
};

// COMMAND_INT: координати цілими ×1e7, поля confirmation НЕМАЄ.
struct CommandInt {
    std::uint8_t  target_system    = 1;
    std::uint8_t  target_component = 1;
    MavFrame      frame            = MavFrame::GlobalRelativeAltInt;
    std::uint16_t command          = 0;
    std::uint8_t  current          = 0;
    std::uint8_t  autocontinue     = 0;
    float         param1 = 0, param2 = 0, param3 = 0, param4 = 0;
    std::int32_t  x = 0;   // широта × 1e7
    std::int32_t  y = 0;   // довгота × 1e7
    float         z = 0;   // висота в метрах за обраним frame

    std::uint8_t src_system    = 255;
    std::uint8_t src_component = 190;
};

// COMMAND_ACK: квитанція на конкретний номер команди.
struct CommandAck {
    std::uint16_t command          = 0;
    MavResult     result           = MavResult::Accepted;
    std::uint8_t  progress         = 255;  // 255 — прогрес не підтримується
    std::int32_t  result_param2    = 0;    // код причини відмови
    std::uint8_t  target_system    = 255;  // кому адресовано (станція)
    std::uint8_t  target_component = 190;
    std::uint8_t  src_system       = 1;    // із заголовка: хто відповів
    std::uint8_t  src_component    = 1;
};

// Градуси → ціле ×1e7. Крок такого числа — 1.1 см по місцевості й не залежить
// від значення, на відміну від float32, який на широті 50° має крок ~42 см.
inline std::int32_t deg_to_1e7(double deg) {
    if (!(deg >= -180.0 && deg <= 180.0)) {
        throw std::out_of_range("координата поза межами [-180; 180] градусів");
    }
    return static_cast<std::int32_t>(std::llround(deg * 1e7));
}

inline double deg_from_1e7(std::int32_t scaled) {
    return static_cast<double>(scaled) / 1e7;
}

// Навігаційні накази несуть координати, тож мають іти лише через COMMAND_INT.
inline bool requires_command_int(std::uint16_t command) {
    return command == mav_cmd::NavLoiterUnlim;
}

// Канал, у який клієнт віддає кадри. На борту чи в наземній станції за ним
// стоїть серіалізація MAVLink і запис у порт модема.
class ILink {
public:
    virtual ~ILink() = default;
    virtual void send(const CommandLong& frame) = 0;
    virtual void send(const CommandInt& frame)  = 0;
};
