#pragma once

#include <expected>
#include <optional>
#include <system_error>

namespace tty {

// Ядрова struct termios2 і <termios.h> в одному файлі не збираються, тож
// назовні звідси стирчать самі числа: жодного ядрового типу в заголовку.
struct KernelLayout {
    unsigned long size;            // sizeof(struct termios2)
    unsigned long nccs;            // 19 у ядрі проти 32 у бібліотеці
    unsigned long cc_offset;
    unsigned long ispeed_offset;
    unsigned long ospeed_offset;
    unsigned long cbaud;           // маска поля швидкості в c_cflag
    unsigned long bother;          // «швидкість задано числом, а не кодом»
};

// nullopt — termios2 на цій системі немає.
std::optional<KernelLayout> kernel_layout() noexcept;

// Справжня швидкість лінії числом, а не константою Bxxx.
std::expected<unsigned long, std::error_code> line_speed(int fd) noexcept;

// Ставить довільну швидкість через BOTHER; повертає ту, яку ядро
// насправді змогло виставити.
std::expected<unsigned long, std::error_code> set_line_speed(int fd,
                                                             unsigned long rate) noexcept;

}  // namespace tty
