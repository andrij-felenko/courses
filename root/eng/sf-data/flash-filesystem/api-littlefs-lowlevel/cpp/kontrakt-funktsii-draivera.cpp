// Інтерфейсний контракт функцій блокового пристрою мовою C++
#include <cstdint>
#include <cstddef>
#include <span>

class ILfsBlockDevice {
public:
    virtual ~ILfsBlockDevice() = default;
    [[nodiscard]] virtual int read(uint32_t block, uint32_t off, std::span<uint8_t> buffer) const noexcept = 0;
    [[nodiscard]] virtual int prog(uint32_t block, uint32_t off, std::span<const uint8_t> buffer) noexcept = 0;
    [[nodiscard]] virtual int erase(uint32_t block) noexcept = 0;
    [[nodiscard]] virtual int sync() noexcept = 0;
};
