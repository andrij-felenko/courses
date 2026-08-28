#include <span>
#include <cstdint>

bool mpu_validate_buffer(std::span<const uint8_t> buffer, bool write_access) noexcept {
    if (buffer.empty()) return false;
    auto start = reinterpret_cast<uintptr_t>(buffer.data());
    auto end   = start + buffer.size_bytes();
    if (end < start) return false;

    if (start >= task->stack_usable_base && end <= task->stack_limit) return true;
    if (start >= task->private_data_base && end <= task->private_data_limit) return true;

    return false;
}
