#ifndef TASK_ISOLATOR_HPP
#define TASK_ISOLATOR_HPP

#include "MpuTypes.hpp"
#include "MpuDevice.hpp"
#include <functional>

namespace embedded::mpu {

struct TaskSecurityProfile {
    uint32_t     task_id{0};
    MemoryRegion stack_region{};
    MemoryRegion guard_region{};
    MemoryRegion private_data_region{};
    std::string_view name{};
};

class TaskIsolator {
public:
    using FaultHandler = std::function<void(const FaultReport&)>;

    explicit TaskIsolator(MpuDevice& device) noexcept : device_(device) {}

    [[nodiscard]] std::expected<void, ConfigError> setup_static_environment(
        std::span<const MemoryRegion> static_regions) noexcept;

    [[nodiscard]] std::expected<TaskSecurityProfile, ConfigError> create_task_profile(
        uint32_t task_id,
        std::span<uint8_t> stack_buffer,
        size_t guard_size_bytes,
        std::span<uint8_t> private_data_buffer,
        std::string_view name) noexcept;

    void switch_task(const TaskSecurityProfile& task) noexcept;

    [[nodiscard]] bool validate_user_buffer(std::span<const uint8_t> buffer,
                                            bool write_access) const noexcept;

    void set_fault_handler(FaultHandler handler) noexcept {
        fault_handler_ = std::move(handler);
    }

    void handle_memmanage(StackFrame* frame, uint32_t exc_return) noexcept;

private:
    MpuDevice& device_;
    const TaskSecurityProfile* active_task_{nullptr};
    FaultHandler fault_handler_{};
};

/* RAII-обгортка для тимчасового підвищення привілеїв у критичних секціях */
class PrivilegeEscalator {
public:
    PrivilegeEscalator() noexcept {
#if defined(__GNUC__) || defined(__clang__)
        __asm volatile(
            "mrs %0, control\n"
            "bic r1, %0, #1 \n"
            "msr control, r1\n"
            "isb            \n"
            : "=r"(saved_control_)
            :
            : "r1", "memory"
        );
#endif
    }

    ~PrivilegeEscalator() noexcept {
#if defined(__GNUC__) || defined(__clang__)
        __asm volatile(
            "msr control, %0\n"
            "isb            \n"
            :
            : "r"(saved_control_)
            : "memory"
        );
#endif
    }

    PrivilegeEscalator(const PrivilegeEscalator&) = delete;
    PrivilegeEscalator& operator=(const PrivilegeEscalator&) = delete;

private:
    uint32_t saved_control_{0};
};

} // namespace embedded::mpu

#endif // TASK_ISOLATOR_HPP
