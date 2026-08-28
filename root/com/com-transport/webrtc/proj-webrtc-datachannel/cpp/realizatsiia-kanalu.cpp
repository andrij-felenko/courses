// C++ обробник команд польоту на стороні бортового комп'ютера

#pragma pack(push, 1)
struct ControlCommandPacket {
    uint16_t throttle_pwm; // 1000..2000 мкс
    uint16_t roll_pwm;     // 1000..2000 мкс
    uint16_t pitch_pwm;    // 1000..2000 мкс
    uint16_t yaw_pwm;      // 1000..2000 мкс
    uint8_t arm_switch;    // 0 = Off, 1 = On
    uint8_t mode_switch;   // 0 = PosHold, 1 = Manual
};
#pragma pack(pop)

class FlightCommandParser {
public:
    // Обробка вхідного пакету команд із сокета WebRTC
    void on_data_received(std::span<const std::byte> packet) {
        if (packet.size() != sizeof(ControlCommandPacket)) {
            // Ігноруємо некоректні розміри
            return;
        }

        ControlCommandPacket cmd{};
        std::memcpy(&cmd, packet.data(), sizeof(ControlCommandPacket));

        // Санітизація діапазонів сигналів ШІМ перед відправкою на польотний контролер
        cmd.throttle_pwm = std::clamp<uint16_t>(cmd.throttle_pwm, 1000, 2000);
        cmd.roll_pwm     = std::clamp<uint16_t>(cmd.roll_pwm, 1000, 2000);
        cmd.pitch_pwm    = std::clamp<uint16_t>(cmd.pitch_pwm, 1000, 2000);
        cmd.yaw_pwm      = std::clamp<uint16_t>(cmd.yaw_pwm, 1000, 2000);

        dispatch_to_flight_controller(cmd);
    }

private:
    void dispatch_to_flight_controller(const ControlCommandPacket& cmd) {
        // Передача структури по UART/MAVLink на польотний контролер (STM32/ArduPilot)
        // Обробка виконується в реальному часі без затримок черги
    }
};
