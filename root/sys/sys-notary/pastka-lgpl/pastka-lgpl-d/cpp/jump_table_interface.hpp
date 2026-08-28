// jump_table_interface.hpp — Інтерфейс виклику LGPL-модуля у Flash
#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace embedded_modular {

inline constexpr uintptr_t LGPL_MODULE_BASE_ADDR = 0x08080000;
inline constexpr uint32_t LGPL_MAGIC = 0x4C47504C;

struct DriverVTable {
    uint32_t magic_header;
    uint32_t api_version;
    int (*init)() noexcept;
    int (*compress)(const uint8_t *in, size_t in_len, uint8_t *out, size_t *out_len) noexcept;
    int (*decompress)(const uint8_t *in, size_t in_len, uint8_t *out, size_t *out_len) noexcept;
};

enum class DriverError {
    ModuleNotFound,
    VersionMismatch,
    ExecutionFailed
};

class LgplModuleBridge {
public:
    static std::expected<LgplModuleBridge, DriverError> bind() noexcept {
        auto *vtable = reinterpret_cast<const DriverVTable*>(LGPL_MODULE_BASE_ADDR);
        if (!vtable || vtable->magic_header != LGPL_MAGIC) {
            return std::unexpected(DriverError::ModuleNotFound);
        }
        if (vtable->api_version != 1) {
            return std::unexpected(DriverError::VersionMismatch);
        }
        return LgplModuleBridge(vtable);
    }

    std::expected<size_t, DriverError> compress(std::span<const uint8_t> in, 
                                               std::span<uint8_t> out) const noexcept {
        size_t written = out.size();
        int rc = vtable_->compress(in.data(), in.size(), out.data(), &written);
        if (rc != 0) {
            return std::unexpected(DriverError::ExecutionFailed);
        }
        return written;
    }

private:
    explicit LgplModuleBridge(const DriverVTable *vtable) noexcept : vtable_(vtable) {}
    const DriverVTable *vtable_;
};

} // namespace embedded_modular
