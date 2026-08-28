#include <iostream>
#include <cstdint>
#include <string_view>
#include <span>

struct HeartbeatMessage {
    uint32_t custom_mode{0};
    uint8_t  type{0};
    uint8_t  autopilot{0};
    uint8_t  base_mode{0};
    uint8_t  system_status{0};
    uint8_t  mavlink_version{0};

    [[nodiscard]] constexpr bool is_armed() const noexcept {
        return (base_mode & 0x80) != 0;
    }

    [[nodiscard]] constexpr bool has_custom_mode() const noexcept {
        return (base_mode & 0x01) != 0;
    }

    [[nodiscard]] std::string_view type_string() const noexcept {
        switch (type) {
            case 2:  return "Квадрокоптер (QUADROTOR)";
            case 1:  return "Літак (FIXED_WING)";
            case 6:  return "Наземна станція (GCS)";
            case 10: return "Наземний ровер (GROUND_ROVER)";
            default: return "Універсальний вузол";
        }
    }
};

class HeartbeatHandler {
public:
    static void handle(uint8_t sysid, uint8_t compid, const HeartbeatMessage& hb) noexcept {
        std::cout << "Отримано HEARTBEAT від [SYS " << static_cast<int>(sysid) 
                  << ", COMP " << static_cast<int>(compid) << "]:\n";
        std::cout << "  Тип апарата:  " << hb.type_string() << "\n";
        std::cout << "  Стан моторів: " << (hb.is_armed() ? "ARMED (НЕБЕЗПЕЧНО)" : "DISARMED (БЕЗПЕЧНО)") << "\n";
        std::cout << "  Статус:       " << (hb.system_status == 4 ? "ACTIVE (Політ)" : "Очікування/Тест") << "\n";

        if (hb.has_custom_mode() && hb.autopilot == 12) {
            const uint8_t main_mode = static_cast<uint8_t>((hb.custom_mode >> 16) & 0xFF);
            std::cout << "  Режим PX4:    0x" << std::hex << static_cast<int>(main_mode) << " (POSCTL)\n" << std::dec;
        }
    }
};
