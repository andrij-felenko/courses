#include "TaskIsolator.hpp"

namespace embedded::mpu {

std::expected<void, ConfigError> TaskIsolator::setup_static_environment(
    std::span<const MemoryRegion> static_regions) noexcept {

    for (const auto& reg : static_regions) {
        auto res = device_.program_region(reg);
        if (!res) {
            return res;
        }
    }
    return {};
}

std::expected<TaskSecurityProfile, ConfigError> TaskIsolator::create_task_profile(
    uint32_t task_id,
    std::span<uint8_t> stack_buffer,
    size_t guard_size_bytes,
    std::span<uint8_t> private_data_buffer,
    std::string_view name) noexcept {

    if (stack_buffer.empty() || stack_buffer.size() <= guard_size_bytes) {
        return std::unexpected(ConfigError::InvalidSizeNotPowerOfTwo);
    }

    TaskSecurityProfile profile{};
    profile.task_id = task_id;
    profile.name = name;

    const uintptr_t stack_base = reinterpret_cast<uintptr_t>(stack_buffer.data());

    /* 1. Стек регіон */
    profile.stack_region = MemoryRegion{
        .region_index   = 5U,
        .base_address   = stack_base,
        .size_bytes     = stack_buffer.size(),
        .permission     = AccessPermission::PrivRwUnprivRw,
        .attribute      = MemoryAttribute::NormalWriteBack,
        .execute_never  = true,
        .subregion_mask = 0U
    };

    /* 2. Захисна смуга стека (No Access) */
    profile.guard_region = MemoryRegion{
        .region_index   = 6U,
        .base_address   = stack_base,
        .size_bytes     = guard_size_bytes,
        .permission     = AccessPermission::NoAccess,
        .attribute      = MemoryAttribute::NormalWriteBack,
        .execute_never  = true,
        .subregion_mask = 0U
    };

    /* 3. Приватні дані (якщо є) */
    if (!private_data_buffer.empty()) {
        profile.private_data_region = MemoryRegion{
            .region_index   = 7U,
            .base_address   = reinterpret_cast<uintptr_t>(private_data_buffer.data()),
            .size_bytes     = private_data_buffer.size(),
            .permission     = AccessPermission::PrivRwUnprivRw,
            .attribute      = MemoryAttribute::NormalWriteBack,
            .execute_never  = true,
            .subregion_mask = 0U
        };
    }

    return profile;
}

void TaskIsolator::switch_task(const TaskSecurityProfile& task) noexcept {
    active_task_ = &task;
    const MemoryRegion* priv_ptr = (task.private_data_region.size_bytes > 0)
                                 ? &task.private_data_region
                                 : nullptr;
    device_.fast_switch_task_regions(task.stack_region, task.guard_region, priv_ptr);
}

bool TaskIsolator::validate_user_buffer(std::span<const uint8_t> buffer,
                                        bool write_access) const noexcept {
    (void)write_access;
    if (buffer.empty()) {
        return false;
    }

    if (!active_task_) {
        return true; /* Виклик з ядра */
    }

    const uintptr_t buf_start = reinterpret_cast<uintptr_t>(buffer.data());
    const size_t len = buffer.size();

    /* Стек (вище захисної смуги) */
    const uintptr_t stack_start = active_task_->stack_region.base_address + active_task_->guard_region.size_bytes;
    const uintptr_t stack_end   = active_task_->stack_region.end_address();
    if (buf_start >= stack_start && (buf_start + len) <= stack_end) {
        return true;
    }

    /* Приватні дані */
    if (active_task_->private_data_region.size_bytes > 0) {
        if (active_task_->private_data_region.contains_range(buf_start, len)) {
            return true;
        }
    }

    return false;
}

void TaskIsolator::handle_memmanage(StackFrame* frame, uint32_t exc_return) noexcept {
    constexpr uintptr_t scb_base = 0xE000ED00UL;
    volatile uint32_t& cfsr  = *reinterpret_cast<volatile uint32_t*>(scb_base + 0x28UL);
    volatile uint32_t& mmfar = *reinterpret_cast<volatile uint32_t*>(scb_base + 0x34UL);

    const uint32_t raw_cfsr = cfsr;
    const uint8_t  mmfsr    = static_cast<uint8_t>(raw_cfsr & 0xFFU);

    FaultReport report{};
    report.mmfsr_flags   = mmfsr;
    report.address_valid = ((mmfsr & (1U << 7)) != 0U);
    report.fault_address = report.address_valid ? mmfar : 0U;
    report.occurred_in_unprivileged_thread = ((exc_return & (1UL << 2)) != 0U);

    if (frame) {
        report.instruction_pc = frame->pc;
        report.return_address = frame->lr;
        report.psr_state      = frame->xpsr;
    }

    if (mmfsr & (1U << 0)) {
        report.reason_description = "Спроба вибірки інструкції з непідтримуваного або XN регіону (IACCVIOL)";
    } else if (mmfsr & (1U << 1)) {
        report.reason_description = "Порушення прав доступу читання або запису даних (DACCVIOL)";
    } else if (mmfsr & (1U << 3)) {
        report.reason_description = "Збій розгортання стек-фрейму при виході з переривання (MUNSTKERR)";
    } else if (mmfsr & (1U << 4)) {
        report.reason_description = "Збій збереження стек-фрейму під час входу у виняток (MSTKERR)";
    } else if (mmfsr & (1U << 5)) {
        report.reason_description = "Помилка ледачого збереження регістрів FPU (MLSPERR)";
    } else {
        report.reason_description = "Невідоме порушення підсистеми захисту пам'яті";
    }

    if (fault_handler_) {
        fault_handler_(report);
    }

    /* Очищення бітів помилки записом 1 */
    cfsr = (raw_cfsr & 0xFFUL);
    MpuDevice::memory_barrier();
    MpuDevice::instruction_barrier();
}

} // namespace embedded::mpu
