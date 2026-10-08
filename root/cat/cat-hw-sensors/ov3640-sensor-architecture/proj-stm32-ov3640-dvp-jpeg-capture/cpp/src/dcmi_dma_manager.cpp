#include "dcmi_dma_manager.hpp"
#include <iostream>
#include <algorithm>

namespace camera {

DcmiDmaManager::DcmiDmaManager() = default;

DcmiDmaManager::~DcmiDmaManager() {
    stop_capture();
}

bool DcmiDmaManager::init(size_t buffer_size_bytes) {
    if (buffer_size_bytes == 0) {
        return false;
    }

    buffer_size_ = buffer_size_bytes;
    
    // Виділення оперативної пам'яті SRAM/PSRAM під два Ping-Pong буфери DMA
    ping_buffer_.resize(buffer_size_, 0);
    pong_buffer_.resize(buffer_size_, 0);

    // Конфігурація сигналів синхронізації DCMI (PCLK, HREF, VSYNC)
    // Та налаштування контролера DMA на вирівняні адреси пам'яті
    initialized_ = true;
    return true;
}

bool DcmiDmaManager::start_capture() {
    if (!initialized_) {
        return false;
    }
    // Активація модуля DCMI та дозволу переривань DMA
    capturing_ = true;
    return true;
}

bool DcmiDmaManager::stop_capture() {
    if (!capturing_) {
        return true;
    }
    // Деактивація апаратного потоку DCMI/DMA
    capturing_ = false;
    return true;
}

void DcmiDmaManager::register_callback(DmaBufferReadyCallback callback) {
    callback_ = std::move(callback);
}

void DcmiDmaManager::handle_dma_interrupt(uint8_t buffer_index) {
    if (!capturing_ || !callback_) {
        return;
    }

    // Отримання вказівника на відповідний активний буфер
    const uint8_t* ptr = (buffer_index == 0) ? ping_buffer_.data() : pong_buffer_.data();

    // Асинхронний викликуваний callback передає дані без блокировки переривання
    callback_(ptr, buffer_size_, buffer_index);
}

} // namespace camera
