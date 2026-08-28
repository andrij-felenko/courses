#include <iostream>
#include <string_view>
#include <array>
#include <optional>
#include <cstdint>

// У C++20 задачу єдиного джерела правди розв'язують через типізовані constexpr-таблиці
// без використання макропідстановок у точках генерації логіки.

enum class TelemetryCmd : uint8_t {
    Ping       = 0x01,
    GetStatus  = 0x02,
    SetConfig  = 0x03,
    Reboot     = 0xFF,
    Invalid    = 0x00
};

struct CommandMeta {
    TelemetryCmd cmd;
    std::string_view name;
    bool requires_auth;
};

// Єдине джерело правди як constexpr-масив структур
inline constexpr std::array<CommandMeta, 4> CommandRegistry{{
    { TelemetryCmd::Ping,      "ping",       false },
    { TelemetryCmd::GetStatus, "get_status", false },
    { TelemetryCmd::SetConfig, "set_config", true  },
    { TelemetryCmd::Reboot,    "reboot",     true  }
}};

// Пошук текстової назви команди (працює і під час компіляції, і під час виконання)
[[nodiscard]] constexpr std::string_view to_string(TelemetryCmd cmd) noexcept {
    for (const auto& entry : CommandRegistry) {
        if (entry.cmd == cmd) return entry.name;
    }
    return "UNKNOWN";
}

// Перевірка вимоги автентифікації
[[nodiscard]] constexpr bool requires_auth(TelemetryCmd cmd) noexcept {
    for (const auto& entry : CommandRegistry) {
        if (entry.cmd == cmd) return entry.requires_auth;
    }
    return true; // Безпечний дефолт
}

// Парсер рядка в значення перелічення
[[nodiscard]] constexpr std::optional<TelemetryCmd> from_string(std::string_view str) noexcept {
    for (const auto& entry : CommandRegistry) {
        if (entry.name == str) return entry.cmd;
    }
    return std::nullopt;
}

int main() {
    constexpr std::string_view input_command = "set_config";
    const auto cmd_opt = from_string(input_command);

    if (cmd_opt.has_value()) {
        const auto cmd = *cmd_opt;
        std::cout << "Знайдено команду: " << to_string(cmd)
                  << " (код: 0x" << std::hex << static_cast<unsigned>(cmd) << std::dec << ")\n";
        std::cout << "Потрібна автентифікація: "
                  << (requires_auth(cmd) ? "ТАК" : "НІ") << "\n";
    } else {
        std::cout << "Команду «" << input_command << "» не розпізнано!\n";
    }
    return 0;
}
