#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <string_view>

namespace elf {

inline constexpr std::size_t IdentSize = 16;

enum class FileType : std::uint16_t {
    None = 0,
    Relocatable = 1,
    Executable = 2,
    SharedObject = 3
};

enum class MachineArchitecture : std::uint16_t {
    Arm = 40,
    RiscV = 243,
    Xtensa = 94
};

struct Header32 {
    std::array<std::uint8_t, IdentSize> ident;
    FileType type;
    MachineArchitecture machine;
    std::uint32_t version;
    std::uint32_t entry_address;
    std::uint32_t ph_offset;
    std::uint32_t sh_offset;
    std::uint32_t flags;
    std::uint16_t header_size;
    std::uint16_t ph_entry_size;
    std::uint16_t ph_count;
    std::uint16_t sh_entry_size;
    std::uint16_t sh_count;
    std::uint16_t sh_str_index;

    [[nodiscard]] constexpr bool is_valid(std::size_t file_size) const noexcept {
        if (file_size < sizeof(Header32)) return false;
        if (ident[0] != 0x7F || ident[1] != 'E' || ident[2] != 'L' || ident[3] != 'F') {
            return false;
        }
        if (ident[4] != 1 || version != 1) return false;

        if (ph_offset != 0) {
            const auto ph_end = static_cast<std::uint64_t>(ph_offset) +
                                (static_cast<std::uint64_t>(ph_entry_size) * ph_count);
            if (ph_end > file_size) return false;
        }
        if (sh_offset != 0) {
            const auto sh_end = static_cast<std::uint64_t>(sh_offset) +
                                (static_cast<std::uint64_t>(sh_entry_size) * sh_count);
            if (sh_end > file_size) return false;
        }
        return true;
    }

    [[nodiscard]] constexpr bool is_arm() const noexcept {
        return machine == MachineArchitecture::Arm;
    }

    [[nodiscard]] constexpr bool is_riscv() const noexcept {
        return machine == MachineArchitecture::RiscV;
    }
};

} // namespace elf
