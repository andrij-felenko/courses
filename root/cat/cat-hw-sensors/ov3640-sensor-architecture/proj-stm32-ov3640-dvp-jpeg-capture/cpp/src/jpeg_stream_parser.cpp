#include "jpeg_stream_parser.hpp"
#include <algorithm>
#include <iostream>

namespace camera {

constexpr uint8_t MARKER_PREFIX = 0xFF;
constexpr uint8_t MARKER_SOI    = 0xD8; // Start of Image
constexpr uint8_t MARKER_EOI    = 0xD9; // End of Image

JpegStreamParser::JpegStreamParser(size_t max_frame_size_bytes)
    : max_frame_size_(max_frame_size_bytes) {
    frame_accumulator_.reserve(64 * 1024);
}

void JpegStreamParser::reset() {
    frame_accumulator_.clear();
    state_ = State::SEARCHING_SOI;
    frame_ready_ = false;
    previous_byte_ = 0x00;
}

void JpegStreamParser::append_byte(uint8_t byte) {
    if (frame_accumulator_.size() >= max_frame_size_) {
        // Виявлено переповнення SRAM: скидаємо стан та фіксуємо помилку
        state_ = State::OVERFLOW_ERROR;
        overflow_counter_++;
        frame_accumulator_.clear();
        return;
    }
    frame_accumulator_.push_back(byte);
}

void JpegStreamParser::process_dma_chunk(const uint8_t* chunk, size_t chunk_size) {
    if (!chunk || chunk_size == 0) {
        return;
    }

    for (size_t i = 0; i < chunk_size; ++i) {
        uint8_t current_byte = chunk[i];

        switch (state_) {
            case State::SEARCHING_SOI:
            case State::OVERFLOW_ERROR:
                // Виявлення двобайтового маркеру SOI (0xFFD8)
                if (previous_byte_ == MARKER_PREFIX && current_byte == MARKER_SOI) {
                    frame_accumulator_.clear();
                    frame_accumulator_.push_back(MARKER_PREFIX);
                    frame_accumulator_.push_back(MARKER_SOI);
                    state_ = State::ACCUMULATING_JPEG;
                    frame_ready_ = false;
                }
                break;

            case State::ACCUMULATING_JPEG:
                append_byte(current_byte);

                // Перевірка на маркер EOI (0xFFD9)
                if (previous_byte_ == MARKER_PREFIX && current_byte == MARKER_EOI) {
                    state_ = State::FRAME_COMPLETE;
                    frame_ready_ = true;
                    frame_counter_++;
                }
                break;

            case State::FRAME_COMPLETE:
                // Нові дані очікують зчитування поточного кадру
                break;
        }

        previous_byte_ = current_byte;
    }
}

FrameBuffer JpegStreamParser::get_latest_frame() {
    FrameBuffer fb;
    if (state_ == State::FRAME_COMPLETE && frame_ready_) {
        fb.data = frame_accumulator_.data();
        fb.size = frame_accumulator_.size();
        fb.format = ImageFormat::JPEG;
        fb.sequence_id = frame_counter_;
        fb.is_valid = true;
    } else {
        fb.is_valid = false;
    }
    return fb;
}

} // namespace camera
