#pragma once

#include <cstdint>
#include <cstddef>
#include <atomic>

namespace embedded {

/**
 * @brief Перелічування станів апаратного контролера DMA/SPI.
 */
enum class HardwareState {
    Uninitialized,
    Ready,
    Transmitting,
    Error
};

/**
 * @brief Структура конфігурації апаратних периферійних модулів (SPI та DMA).
 */
struct SpiDmaConfig {
    uintptr_t spi_peripheral_addr{0x40013000};  // Базова адреса регістра SPI (наприклад, SPI1)
    uint8_t   dma_channel{3};                   // Канал або потік DMA
    uint16_t  gpio_pin{7};                      // Номер виводу MOSI (наприклад, PA7)
    uint32_t  baud_rate_prescaler{8};           // Подільник частоти тактування SPI для отримання ~2.4 МГц
    bool      enable_circular_mode{false};      // Кільцевий режим DMA (за замовчуванням вимкнено)
};

/**
 * @brief Апаратна RAII-обгортка для керування периферією мікроконтролера (SPI та DMA).
 * 
 * Клас автоматично налаштовує ресурси периферії при ініціалізації та безпечно
 * зупиняє фонову передачу й деактивує модулі в деструкторі. Забороняє копіювання
 * для запобігання дублюванню ресурсів.
 */
class DmaSpiHardware {
public:
    explicit DmaSpiHardware(const SpiDmaConfig& config);
    ~DmaSpiHardware();

    // Заборона копіювання (RAII семантика)
    DmaSpiHardware(const DmaSpiHardware&) = delete;
    DmaSpiHardware& operator=(const DmaSpiHardware&) = delete;

    // Дозвіл переміщення
    DmaSpiHardware(DmaSpiHardware&& other) noexcept;
    DmaSpiHardware& operator=(DmaSpiHardware&& other) noexcept;

    /**
     * @brief Ініціалізація периферійних модулів SPI та DMA.
     * @return true у разі успішної конфігурації апаратури, інакше false.
     */
    bool init();

    /**
     * @brief Безпечне деініціалізування периферії та зупинка поточних передач.
     */
    void deinit();

    /**
     * @brief Запуск асинхронної передачі блоку даних через DMA у SPI.
     * @param data Вказівник на буфер даних.
     * @param length Розмір даних у байтах.
     * @return true якщо передачу успішно запущено, false якщо апаратура зайнята або не ініціалізована.
     */
    bool startTransmitDma(const uint8_t* data, std::size_t length);

    /**
     * @brief Перевірка, чи виконується фонова передача DMA у даний момент.
     */
    bool isBusy() const;

    /**
     * @brief Отримання поточного стану апаратного шару.
     */
    HardwareState getState() const;

    /**
     * @brief Обробник переривання завершення передачі DMA (Transfer Complete ISR).
     * Викликається з апаратного вектора переривань DMA.
     */
    void handleTransferCompleteIsr();

    /**
     * @brief Обробник переривання помилки передачі DMA (Transfer Error ISR).
     */
    void handleTransferErrorIsr();

private:
    SpiDmaConfig config_;
    std::atomic<HardwareState> state_{HardwareState::Uninitialized};
    volatile bool is_initialized_{false};
    const uint8_t* current_tx_buffer_{nullptr};
    std::size_t current_tx_length_{0};
};

} // namespace embedded
