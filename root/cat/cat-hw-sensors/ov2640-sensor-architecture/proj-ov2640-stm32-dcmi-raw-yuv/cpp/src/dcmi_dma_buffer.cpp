#include "dcmi_dma_buffer.hpp"
#include <chrono>
#include <cstring>
#include <iostream>

namespace ov2640 {

static uint64_t getCurrentTimeUs() {
    auto now = std::chrono::steady_clock::now();
    return static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::microseconds>(now.time_since_epoch()).count());
}

DcmiDmaBuffer::DcmiDmaBuffer(size_t buffer_count, size_t buffer_capacity_bytes)
    : buffer_count_(buffer_count < 2 ? 2 : buffer_count),
      buffer_capacity_(buffer_capacity_bytes),
      active_write_index_(0),
      active_read_index_(0),
      frame_counter_(0),
      is_capturing_(false) {}

DcmiDmaBuffer::~DcmiDmaBuffer() {
    stopCapture();
}

bool DcmiDmaBuffer::init() {
    buffers_.clear();
    memory_pools_.clear();

    buffers_.resize(buffer_count_);

    for (size_t i = 0; i < buffer_count_; ++i) {
        // Виділення суцільного блоку оперативної пам'яті під кадр (RAM / PSRAM)
        auto raw_storage = std::make_unique<uint8_t[]>(buffer_capacity_);
        buffers_[i].data = raw_storage.get();
        buffers_[i].capacity = buffer_capacity_;
        buffers_[i].length = 0;
        buffers_[i].sequence_number = 0;
        buffers_[i].timestamp_us = 0;
        buffers_[i].is_valid = false;

        memory_pools_.push_back(std::move(raw_storage));
    }

    active_write_index_ = 0;
    active_read_index_ = 0;
    frame_counter_ = 0;
    return true;
}

bool DcmiDmaBuffer::startCapture() {
    if (memory_pools_.empty()) {
        return false;
    }
    is_capturing_ = true;
    active_write_index_ = 0;
    return true;
}

void DcmiDmaBuffer::stopCapture() {
    is_capturing_ = false;
}

void DcmiDmaBuffer::setFrameCallback(FrameReadyCallback callback) {
    frame_callback_ = callback;
}

void DcmiDmaBuffer::handleDmaHalfTransferInterrupt() {
    // Реакція на апаратне переривання пів-трансферу DMA у кільцевому буфері
    if (!is_capturing_) return;
}

void DcmiDmaBuffer::handleDmaTransferCompleteInterrupt() {
    // Автоматична зміна буфера при завершенні циклу DMA
    if (!is_capturing_) return;
}

void DcmiDmaBuffer::handleDcmiVsyncInterrupt() {
    // Сигнал вертикальної синхронізації VSYNC означає межу між кадрами
    if (!is_capturing_) return;
}

void DcmiDmaBuffer::handleDcmiFrameInterrupt(size_t actual_received_bytes) {
    if (!is_capturing_) return;

    FrameBuffer& current_buf = buffers_[active_write_index_];
    current_buf.length = (actual_received_bytes > current_buf.capacity) ? current_buf.capacity : actual_received_bytes;
    current_buf.sequence_number = ++frame_counter_;
    current_buf.timestamp_us = getCurrentTimeUs();
    current_buf.is_valid = (current_buf.length > 0);

    // Якщо зареєстровано колбек, сповіщаємо про готовий кадр
    if (frame_callback_ && current_buf.is_valid) {
        frame_callback_(current_buf);
    }

    advanceBufferIndex();
}

const FrameBuffer& DcmiDmaBuffer::getBuffer(size_t index) const {
    if (index >= buffers_.size()) {
        return buffers_[0];
    }
    return buffers_[index];
}

void DcmiDmaBuffer::advanceBufferIndex() {
    active_read_index_ = active_write_index_;
    active_write_index_ = (active_write_index_ + 1) % buffer_count_;
}

} // namespace ov2640
