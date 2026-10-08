#pragma once

#include "ov3640_registers.hpp"
#include <cstdint>
#include <cstddef>
#include <vector>

namespace camera {

// Допоміжна структура метаданих отриманого кадру
struct FrameBuffer {
    const uint8_t* data{nullptr};
    size_t size{0};
    ImageFormat format{ImageFormat::JPEG};
    uint32_t sequence_id{0};
    bool is_valid{false};
};

// Клас JpegStreamParser здійснює потоковий аналіз бінарного потоку DMA,
// шукаючи маркери початку (SOI: 0xFFD8) та кінця (EOI: 0xFFD9) JPEG-кадру.
class JpegStreamParser {
public:
    explicit JpegStreamParser(size_t max_frame_size_bytes = 256 * 1024);
    ~JpegStreamParser() = default;

    // Обробка чергового фрагмента даних з кільцевого буфера DMA
    void process_dma_chunk(const uint8_t* chunk, size_t chunk_size);

    // Перевірка наявності повністю сформованого кадру
    bool has_complete_frame() const { return frame_ready_; }

    // Отримання сформованого кадру
    FrameBuffer get_latest_frame();

    // Скидання стану парсера та відновлення синхронізації після помилок
    void reset();

    // Лічильник оброблених кадрів та переповнень
    uint32_t get_frame_counter() const { return frame_counter_; }
    size_t get_overflow_count() const { return overflow_counter_; }

private:
    enum class State {
        SEARCHING_SOI,
        ACCUMULATING_JPEG,
        FRAME_COMPLETE,
        OVERFLOW_ERROR
    };

    size_t max_frame_size_;
    std::vector<uint8_t> frame_accumulator_;
    State state_{State::SEARCHING_SOI};
    bool frame_ready_{false};
    uint8_t previous_byte_{0x00};
    uint32_t frame_counter_{0};
    size_t overflow_counter_{0};

    void append_byte(uint8_t byte);
};

} // namespace camera
