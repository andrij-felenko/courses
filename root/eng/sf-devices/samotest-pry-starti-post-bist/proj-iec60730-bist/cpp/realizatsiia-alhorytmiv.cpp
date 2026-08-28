#include "iec60730_bist.hpp"
#include <concepts>
#include <algorithm>

namespace safety {

namespace {

// RAII обгортка блокування переривань
class InterruptGuard {
public:
    InterruptGuard() noexcept {
        __asm__ volatile ("mrs %0, primask\n cpsid i" : "=r" (primask_) :: "memory");
    }
    ~InterruptGuard() noexcept {
        __asm__ volatile ("msr primask, %0" :: "r" (primask_) : "memory");
    }
    InterruptGuard(const InterruptGuard&) = delete;
    InterruptGuard& operator=(const InterruptGuard&) = delete;

private:
    std::uint32_t primask_{0};
};

// Ядро алгоритму March C- над std::span
bool execute_march_c(std::span<volatile std::uint32_t> slice) noexcept {
    // M0: ⇕ (w0)
    for (auto& word : slice) {
        word = 0x00000000U;
    }

    // M1: ⇑ (r0, w1)
    for (std::size_t i = 0; i < slice.size(); ++i) {
        if (slice[i] != 0x00000000U) return false;
        slice[i] = 0xFFFFFFFFU;
    }

    // M2: ⇑ (r1, w0)
    for (std::size_t i = 0; i < slice.size(); ++i) {
        if (slice[i] != 0xFFFFFFFFU) return false;
        slice[i] = 0x00000000U;
    }

    // M3: ⇓ (r0, w1)
    for (std::size_t i = slice.size(); i > 0; --i) {
        const std::size_t idx = i - 1;
        if (slice[idx] != 0x00000000U) return false;
        slice[idx] = 0xFFFFFFFFU;
    }

    // M4: ⇓ (r1, w0)
    for (std::size_t i = slice.size(); i > 0; --i) {
        const std::size_t idx = i - 1;
        if (slice[idx] != 0xFFFFFFFFU) return false;
        slice[idx] = 0x00000000U;
    }

    // M5: ⇕ (r0)
    for (const auto& word : slice) {
        if (word != 0x00000000U) return false;
    }

    return true;
}

constexpr std::uint32_t update_crc32(std::uint32_t crc, std::uint8_t byte) noexcept {
    crc ^= byte;
    for (int i = 0; i < 8; ++i) {
        crc = (crc & 1) ? ((crc >> 1) ^ 0xEDB88320U) : (crc >> 1);
    }
    return crc;
}

} // namespace

template <std::size_t SliceWords>
Status RamSliceScanner<SliceWords>::scan_next_slice() noexcept {
    if (region_.empty()) {
        return Status::Ok;
    }

    const std::size_t remaining = region_.size() - current_offset_;
    const std::size_t count = std::min(remaining, SliceWords);

    auto target_span = region_.subspan(current_offset_, count);

    bool march_passed = false;
    {
        InterruptGuard lock; // Атомарне тестування

        // 1. Зберегти початкові дані
        std::copy_n(target_span.data(), count, backup_buffer_.begin());

        // 2. Виконати March C-
        std::span<volatile std::uint32_t> vol_span(
            reinterpret_cast<volatile std::uint32_t*>(target_span.data()), count);
        march_passed = execute_march_c(vol_span);

        // 3. Відновити стан пам'яті
        std::copy_n(backup_buffer_.begin(), count, target_span.data());
    }

    if (!march_passed) {
        return Status::ErrRamMarchC;
    }

    current_offset_ += count;
    if (current_offset_ >= region_.size()) {
        current_offset_ = 0; // Перехід до початку масиву
    }

    return Status::Ok;
}

FlashCrcScanner::StepResult FlashCrcScanner::scan_quantum() noexcept {
    if (flash_.empty()) {
        return {Status::Ok, true};
    }

    const std::size_t remaining = flash_.size() - processed_;
    const std::size_t chunk = std::min(remaining, quantum_);

    auto sub = flash_.subspan(processed_, chunk);
    for (std::uint8_t b : sub) {
        running_crc_ = update_crc32(running_crc_, b);
    }

    processed_ += chunk;
    if (processed_ >= flash_.size()) {
        const std::uint32_t final_crc = ~running_crc_;
        if (final_crc != expected_crc_) {
            return {Status::ErrFlashCrc, true};
        }
        reset();
        return {Status::Ok, true};
    }

    return {Status::Ok, false};
}

[[noreturn]] void enter_safe_state(Status reason) noexcept {
    __asm__ volatile ("cpsid i" ::: "memory");

    // Вимкнення критичної периферії: контактори, ШІМ, нагрівачі
    // Фіксація коду помилки у Retain RAM
    (void)reason;

    for (;;) {
        __asm__ volatile ("wfi");
    }
}

// Явна інстанціація типового сканера
template class RamSliceScanner<16>;

} // namespace safety
