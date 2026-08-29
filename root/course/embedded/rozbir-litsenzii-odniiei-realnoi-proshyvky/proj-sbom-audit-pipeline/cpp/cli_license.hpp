// cli_license.hpp — команди `license` та `about` службової консолі.
#ifndef FW_CLI_LICENSE_HPP
#define FW_CLI_LICENSE_HPP

#include <array>

#include "console.hpp"

namespace fw {

// `license`      — таблиця компонентів;
// `license mbed` — картка одного компонента з повним застереженням.
CommandResult license_command(std::string_view args, WriterRef out);

// `about` — виріб, версія прошивки й SHA-256 паспорта SBOM цієї збірки.
CommandResult about_command(std::string_view args, WriterRef out);

// Набір команд віддаємо готовим: Console бере його як std::span і нічого
// не реєструє в рантаймі — таблиця цілком constexpr і живе у Flash.
inline constexpr std::array<Command, 2> kFirmwareCommands{{
    { "license", "склад прошивки й ліцензії; license <назва> — подробиці", &license_command },
    { "about",   "виріб, версія, хеш паспорта SBOM",                       &about_command   },
}};

}  // namespace fw

#endif  // FW_CLI_LICENSE_HPP
