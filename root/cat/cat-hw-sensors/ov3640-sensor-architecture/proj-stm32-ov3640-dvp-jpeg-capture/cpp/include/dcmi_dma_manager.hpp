#pragma once

#include <cstdint>
#include <cstddef>
#include <vector>
#include <functional>

namespace camera {

// Тип функції зворотного виклику (callback) при заповненні одного з DMA буферів
using DmaBufferReadyCallback = std::function<void(const uint8_t* buffer, size_t size, uint8_t buffer_index)>;

// Клас DcmiDmaManager забезпечує керування паралельним інтерфейсом DCMI
// та контролером DMA у режимі подвійного буферизування (Ping-Pong Buffer).
class DcmiDmaManager {
public:
    DcmiDmaManager();
    ~DcmiDmaManager();

    // Заборона копіювання для збереження стабільності ресурсів DMA
    DcmiDmaManager(const DcmiDmaManager&) = delete;
    DcmiDmaManager& operator=(const DcmiDmaManager&) = delete;

    // Ініціалізація периферії DCMI та виділення подвійного буфера DMA
    bool init(size_t buffer_size_bytes);

    // Запуск апаратного захоплення відеопотоку
    bool start_capture();

    // Зупинка апаратного захоплення
    bool stop_capture();

    // Реєстрація функції зворотного виклику готовності буфера
    void register_callback(DmaBufferReadyCallback callback);

    // Обробник переривання DMA (викликуваний з ISR або симулятора МК)
    void handle_dma_interrupt(uint8_t buffer_index);

    // Перевірка стану апаратури
    bool is_capturing() const { return capturing_; }
    size_t get_buffer_size() const { return buffer_size_; }

private:
    size_t buffer_size_{0};
    std::vector<uint8_t> ping_buffer_;
    std::vector<uint8_t> pong_buffer_;
    DmaBufferReadyCallback callback_{nullptr};
    bool capturing_{false};
    bool initialized_{false};
};

} // namespace camera
