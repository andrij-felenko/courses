#include <array>
#include <span>
#include <cstdint>
#include <concepts>
#include <functional>

/**
 * @brief Концепт споживача блоків відліків АЦП
 */
template <typename T>
concept SampleConsumer = requires(T consumer, std::span<const uint16_t> block) {
    { consumer.on_block_ready(block) } -> std::same_as<void>;
};

/**
 * @brief Диспетчер подвійного буфера АЦП на базі DMA
 * @tparam BufferSize Загальний розмір буфера (мусить бути парним і кратним розміру рядка кешу 32 байти)
 */
template <std::size_t BufferSize>
class AdcCircularBuffer {
    static_assert(BufferSize % 2 == 0, "Розмір буфера мусить ділитися на 2 для роботи Half/Full DMA");
    static_assert((BufferSize * sizeof(uint16_t)) % 32 == 0, "Буфер мусить бути вирівняний по лінії D-Cache 32 байти");

public:
    static constexpr std::size_t HalfSize = BufferSize / 2;

    AdcCircularBuffer() = default;

    /* Заборона копіювання через володіння апаратним буфером */
    AdcCircularBuffer(const AdcCircularBuffer&) = delete;
    AdcCircularBuffer& operator=(const AdcCircularBuffer&) = delete;

    /**
     * @brief Отримати покажчик на сирий масив для апаратного налаштування DMA
     */
    [[nodiscard]] constexpr uint16_t* raw_data() noexcept {
        return m_buffer.data();
    }

    [[nodiscard]] constexpr std::size_t size() const noexcept {
        return BufferSize;
    }

    /**
     * @brief Викликається з обробника Half-Transfer ISR
     */
    void handle_half_complete_isr() noexcept {
        m_half_pending = true;
    }

    /**
     * @brief Викликається з обробника Full-Transfer ISR
     */
    void handle_full_complete_isr() noexcept {
        m_full_pending = true;
    }

    /**
     * @brief Опитування та передача готових половин буфера у споживач
     */
    template <SampleConsumer Consumer>
    void process_pending(Consumer& consumer) {
        if (m_half_pending) {
            m_half_pending = false;
            // Для ядер з D-Cache (Cortex-M7) інвалідуємо першу половину буфера
            #if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
            SCB_InvalidateDCache_by_Addr(reinterpret_cast<uint32_t*>(m_buffer.data()), HalfSize * sizeof(uint16_t));
            #endif
            consumer.on_block_ready(std::span<const uint16_t>(m_buffer.data(), HalfSize));
        }
        if (m_full_pending) {
            m_full_pending = false;
            #if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
            SCB_InvalidateDCache_by_Addr(reinterpret_cast<uint32_t*>(m_buffer.data() + HalfSize), HalfSize * sizeof(uint16_t));
            #endif
            consumer.on_block_ready(std::span<const uint16_t>(m_buffer.data() + HalfSize, HalfSize));
        }
    }

private:
    alignas(32) std::array<uint16_t, BufferSize> m_buffer{};
    volatile bool m_half_pending{false};
    volatile bool m_full_pending{false};
};

/**
 * @brief Приклад обробника спектрального аналізатора
 */
class SpectralProcessor {
public:
    void on_block_ready(std::span<const uint16_t> block) {
        // block.data() містить гарантовано стабільні за часом відліки
        // Виконання ШПФ над block.size() елементами
    }
};
