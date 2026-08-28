#include <cstdint>
#include <span>
#include <optional>

namespace reloc {

enum class ArmRelocType : std::uint32_t {
    None = 0,
    Abs32 = 2,
    ThumbCall = 10
};

[[nodiscard]] bool apply_relocation(std::span<std::uint8_t> code_buffer, 
                                     std::size_t offset, 
                                     std::uintptr_t symbol_address, 
                                     ArmRelocType type) noexcept {
    if (offset + sizeof(std::uint32_t) > code_buffer.size()) {
        return false;
    }

    auto* target = reinterpret_cast<std::uint32_t*>(code_buffer.data() + offset);

    if (type == ArmRelocType::Abs32) {
        *target += static_cast<std::uint32_t>(symbol_address);
        return true;
    }

    return false;
}

} // namespace reloc
