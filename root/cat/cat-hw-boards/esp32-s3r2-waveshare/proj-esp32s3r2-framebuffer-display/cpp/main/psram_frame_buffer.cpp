#include "psram_frame_buffer.hpp"
#include <cstring>
#include <stdexcept>

static const char* TAG = "PsramFrameBuffer";

namespace graphics {

PsramFrameBuffer::PsramFrameBuffer(uint16_t width, uint16_t height, uint8_t bytes_per_pixel)
    : width_(width), height_(height), bytes_per_pixel_(bytes_per_pixel) {
    
    buffer_size_ = static_cast<size_t>(width_) * height_ * bytes_per_pixel_;

    ESP_LOGI(TAG, "Виділення пам'яті під подвійний буфер (%dx%d, %d BPP), розмір кадру: %u байт",
             width_, height_, bytes_per_pixel_, (unsigned int)buffer_size_);

    // Виділяємо два буфери у зовнішній псевдостатичній пам'яті PSRAM з вирівнюванням під DMA
    buffer_a_ = static_cast<uint16_t*>(heap_caps_malloc(
        buffer_size_, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA | MALLOC_CAP_8BIT));
    
    buffer_b_ = static_cast<uint16_t*>(heap_caps_malloc(
        buffer_size_, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA | MALLOC_CAP_8BIT));

    if (!buffer_a_ || !buffer_b_) {
        ESP_LOGE(TAG, "Помилка виділення пам'яті в PSRAM! (buffer_a=%p, buffer_b=%p)", buffer_a_, buffer_b_);
        if (buffer_a_) heap_caps_free(buffer_a_);
        if (buffer_b_) heap_caps_free(buffer_b_);
        throw std::bad_alloc();
    }

    // Очищаємо виділені кадри в чорний колір
    std::memset(buffer_a_, 0, buffer_size_);
    std::memset(buffer_b_, 0, buffer_size_);

    draw_buffer_ = buffer_a_;
    display_buffer_ = buffer_b_;

    ESP_LOGI(TAG, "Успішно виділено кадрові буфери в PSRAM: A=%p, B=%p", buffer_a_, buffer_b_);
}

PsramFrameBuffer::~PsramFrameBuffer() {
    if (buffer_a_) {
        heap_caps_free(buffer_a_);
        buffer_a_ = nullptr;
    }
    if (buffer_b_) {
        heap_caps_free(buffer_b_);
        buffer_b_ = nullptr;
    }
    ESP_LOGI(TAG, "Пам'ять кадрових буферів у PSRAM звільнено");
}

PsramFrameBuffer::PsramFrameBuffer(PsramFrameBuffer&& other) noexcept
    : width_(other.width_),
      height_(other.height_),
      bytes_per_pixel_(other.bytes_per_pixel_),
      buffer_size_(other.buffer_size_),
      buffer_a_(other.buffer_a_),
      buffer_b_(other.buffer_b_),
      draw_buffer_(other.draw_buffer_),
      display_buffer_(other.display_buffer_),
      trans_(other.trans_),
      trans_in_flight_(other.trans_in_flight_) {
    
    other.buffer_a_ = nullptr;
    other.buffer_b_ = nullptr;
    other.draw_buffer_ = nullptr;
    other.display_buffer_ = nullptr;
    other.buffer_size_ = 0;
    other.trans_in_flight_ = false;
}

PsramFrameBuffer& PsramFrameBuffer::operator=(PsramFrameBuffer&& other) noexcept {
    if (this != &other) {
        if (buffer_a_) heap_caps_free(buffer_a_);
        if (buffer_b_) heap_caps_free(buffer_b_);

        width_ = other.width_;
        height_ = other.height_;
        bytes_per_pixel_ = other.bytes_per_pixel_;
        buffer_size_ = other.buffer_size_;
        buffer_a_ = other.buffer_a_;
        buffer_b_ = other.buffer_b_;
        draw_buffer_ = other.draw_buffer_;
        display_buffer_ = other.display_buffer_;
        trans_ = other.trans_;
        trans_in_flight_ = other.trans_in_flight_;

        other.buffer_a_ = nullptr;
        other.buffer_b_ = nullptr;
        other.draw_buffer_ = nullptr;
        other.display_buffer_ = nullptr;
        other.buffer_size_ = 0;
        other.trans_in_flight_ = false;
    }
    return *this;
}

void PsramFrameBuffer::swap_buffers() noexcept {
    std::swap(draw_buffer_, display_buffer_);
}

esp_err_t PsramFrameBuffer::flush_async(spi_device_handle_t spi) {
    if (trans_in_flight_) {
        esp_err_t ret = wait_until_idle(spi);
        if (ret != ESP_OK) return ret;
    }

    std::memset(&trans_, 0, sizeof(spi_transaction_t));
    trans_.length = buffer_size_ * 8; // Розмір в бітах
    trans_.tx_buffer = display_buffer_;

    esp_err_t ret = spi_device_queue_trans(spi, &trans_, portMAX_DELAY);
    if (ret == ESP_OK) {
        trans_in_flight_ = true;
    } else {
        ESP_LOGE(TAG, "Помилка черги SPI DMA транзакції: %s", esp_err_to_name(ret));
    }
    return ret;
}

esp_err_t PsramFrameBuffer::wait_until_idle(spi_device_handle_t spi) {
    if (!trans_in_flight_) return ESP_OK;

    spi_transaction_t* completed_trans = nullptr;
    esp_err_t ret = spi_device_get_trans_result(spi, &completed_trans, portMAX_DELAY);
    if (ret == ESP_OK) {
        trans_in_flight_ = false;
    } else {
        ESP_LOGE(TAG, "Помилка очікування завершення DMA: %s", esp_err_to_name(ret));
    }
    return ret;
}

} // namespace graphics
