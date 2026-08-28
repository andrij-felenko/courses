// C++ representation for IPC v3 Header
#include <cstdint>

struct alignas(4) IpcCmdHeader {
    std::uint32_t size{sizeof(IpcCmdHeader)};
    std::uint32_t cmd{0};

    [[nodiscard]] constexpr std::uint32_t getCategory() const noexcept {
        return (cmd >> 28) & 0x0F;
    }
    [[nodiscard]] constexpr std::uint32_t getCommand() const noexcept {
        return (cmd >> 16) & 0x0FFF;
    }
};
