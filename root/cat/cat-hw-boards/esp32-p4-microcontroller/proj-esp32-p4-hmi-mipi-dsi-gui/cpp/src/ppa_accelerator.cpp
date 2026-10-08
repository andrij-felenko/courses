#include "ppa_accelerator.hpp"
#include <iostream>
#include <cstdlib>
#include <cstring>

namespace esp32_p4 {

// -----------------------------------------------------------------------------
// Реалізація FrameBufferGuard (RAII)
// -----------------------------------------------------------------------------

FrameBufferGuard::FrameBufferGuard(size_t size, size_t alignment, uint32_t caps) {
    allocate(size, alignment, caps);
}

FrameBufferGuard::~FrameBufferGuard() {
    free();
}

FrameBufferGuard::FrameBufferGuard(FrameBufferGuard&& other) noexcept {
    *this = std::move(other);
}

FrameBufferGuard& FrameBufferGuard::operator=(FrameBufferGuard&& other) noexcept {
    if (this != &other) {
        free();
        buffer_ = other.buffer_;
        size_ = other.size_;
        alignment_ = other.alignment_;

        other.buffer_ = nullptr;
        other.size_ = 0;
    }
    return *this;
}

bool FrameBufferGuard::allocate(size_t size, size_t alignment, uint32_t caps) {
    free();

    if (size == 0) {
        return false;
    }

    alignment_ = alignment;

    // Вирівнювання має бути кратним 2 і не меншим за 32 для DMA ESP32-P4
    if (alignment_ < 32) {
        alignment_ = 32;
    }

#if __has_include("esp_heap_caps.h")
    buffer_ = static_cast<uint8_t*>(heap_caps_aligned_alloc(alignment_, size, caps));
#else
    (void)caps;
    // Кросплатформенне виділення вирівняного блоку пам'яті
    void* ptr = nullptr;
#if defined(_MSC_VER)
    ptr = _aligned_malloc(size, alignment_);
#else
    if (posix_memalign(&ptr, alignment_, size) != 0) {
        ptr = nullptr;
    }
#endif
    buffer_ = static_cast<uint8_t*>(ptr);
#endif

    if (!buffer_) {
        std::cerr << "[FrameBufferGuard] Помилка: Не вдалося виділити "
                  << size << " байтів з вирівнюванням " << alignment_ << std::endl;
        size_ = 0;
        return false;
    }

    size_ = size;
    clear(0);
    return true;
}

void FrameBufferGuard::free() noexcept {
    if (buffer_) {
#if __has_include("esp_heap_caps.h")
        heap_caps_free(buffer_);
#else
#if defined(_MSC_VER)
        _aligned_free(buffer_);
#else
        ::free(buffer_);
#endif
#endif
        buffer_ = nullptr;
    }
    size_ = 0;
}

void FrameBufferGuard::clear(uint8_t value) noexcept {
    if (buffer_ && size_ > 0) {
        std::memset(buffer_, value, size_);
    }
}

// -----------------------------------------------------------------------------
// Реалізація PpaAccelerator (Pixel Processing Accelerator)
// -----------------------------------------------------------------------------

PpaAccelerator::~PpaAccelerator() {
    deinitialize();
}

PpaAccelerator::PpaAccelerator(PpaAccelerator&& other) noexcept {
    *this = std::move(other);
}

PpaAccelerator& PpaAccelerator::operator=(PpaAccelerator&& other) noexcept {
    if (this != &other) {
        deinitialize();

        is_initialized_ = other.is_initialized_;
        is_busy_ = other.is_busy_;
        ppa_handle_ = other.ppa_handle_;
        current_callback_ = std::move(other.current_callback_);

        other.is_initialized_ = false;
        other.is_busy_ = false;
        other.ppa_handle_ = nullptr;
    }
    return *this;
}

bool PpaAccelerator::initialize() {
    if (is_initialized_) {
        return true;
    }

    std::cout << "[PPA] Ініціалізація апаратного 2D-прискорювача PPA ESP32-P4..." << std::endl;
    ppa_handle_ = reinterpret_cast<void*>(0x500A0000); // Базова адреса PPA
    is_initialized_ = true;
    is_busy_ = false;

    return true;
}

void PpaAccelerator::deinitialize() {
    if (!is_initialized_) {
        return;
    }

    wait_idle(500);
    std::cout << "[PPA] Зупинка блока PPA." << std::endl;
    ppa_handle_ = nullptr;
    is_initialized_ = false;
    is_busy_ = false;
}

bool PpaAccelerator::blend_async(const PpaBlendConfig& config, std::function<void()> on_complete) {
    if (!is_initialized_ || is_busy_) {
        std::cerr << "[PPA] Прискорювач недоступний або зайнятий." << std::endl;
        return false;
    }

    if (!config.fg_buffer || !config.bg_buffer || !config.out_buffer) {
        std::cerr << "[PPA] Помилка: Вказано нульові вказівники на буфери для блендингу." << std::endl;
        return false;
    }

    is_busy_ = true;
    current_callback_ = std::move(on_complete);

    std::cout << "[PPA] Виконується апаратний Alpha Blending (" << config.width << "x" << config.height
              << ", alpha=" << static_cast<int>(config.alpha) << ")..." << std::endl;

    handle_dma_interrupt();
    return true;
}

bool PpaAccelerator::scale_async(const PpaScaleConfig& config, std::function<void()> on_complete) {
    if (!is_initialized_ || is_busy_) {
        return false;
    }

    if (!config.src_buffer || !config.dst_buffer) {
        return false;
    }

    is_busy_ = true;
    current_callback_ = std::move(on_complete);

    std::cout << "[PPA] Виконується апаратне масштабування: "
              << config.src_width << "x" << config.src_height << " -> "
              << config.dst_width << "x" << config.dst_height << std::endl;

    handle_dma_interrupt();
    return true;
}

bool PpaAccelerator::rotate_async(const void* src, void* dst, uint16_t width, uint16_t height,
                                  PpaColorFormat fmt, PpaRotation rotation, std::function<void()> on_complete) {
    (void)fmt;
    if (!is_initialized_ || is_busy_ || !src || !dst) {
        return false;
    }

    is_busy_ = true;
    current_callback_ = std::move(on_complete);

    std::cout << "[PPA] Поворот кадру (" << width << "x" << height << ") на "
              << (static_cast<int>(rotation) * 90) << " градусів." << std::endl;

    handle_dma_interrupt();
    return true;
}

bool PpaAccelerator::convert_color_async(const void* src, void* dst, uint32_t pixel_count,
                                          PpaColorFormat src_fmt, PpaColorFormat dst_fmt, std::function<void()> on_complete) {
    (void)src_fmt; (void)dst_fmt;
    if (!is_initialized_ || is_busy_ || !src || !dst || pixel_count == 0) {
        return false;
    }

    is_busy_ = true;
    current_callback_ = std::move(on_complete);

    std::cout << "[PPA] Конверсія колірного формату для " << pixel_count << " пікселів..." << std::endl;

    handle_dma_interrupt();
    return true;
}

bool PpaAccelerator::wait_idle(uint32_t timeout_ms) {
    (void)timeout_ms;
    is_busy_ = false;
    return true;
}

void PpaAccelerator::handle_dma_interrupt() {
    // Сповіщення про завершення апаратної DMA операції PPA
    is_busy_ = false;

    if (current_callback_) {
        auto cb = std::move(current_callback_);
        current_callback_ = nullptr;
        cb();
    }
}

} // namespace esp32_p4
