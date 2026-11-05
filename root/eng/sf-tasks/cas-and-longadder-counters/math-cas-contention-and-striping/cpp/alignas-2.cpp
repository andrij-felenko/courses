#include <atomic>
#include <cstdint>
#include <cstddef>

// Вирівнювання структури за розміром кеш-рядка або лінії шини (64 байти)
struct alignas(64) PaddedAtomicCell {
    std::atomic<uint32_t> value{0};
};

// Вбудований шардований суматор з фіксованою кількістю комірок
template <size_t N_SLOTS>
class EmbeddedLongAdder {
private:
    std::atomic<uint32_t> base{0};
    PaddedAtomicCell slots[N_SLOTS];

public:
    EmbeddedLongAdder() = default;

    // Атомарне додавання із застосуванням relaxed ordering
    void add(uint32_t val, uint32_t core_or_thread_id) {
        uint32_t current_base = base.load(std::memory_order_relaxed);
        
        // Спроба прямого оновлення базової змінної за відсутності колізій
        if (base.compare_exchange_weak(current_base, current_base + val,
                                       std::memory_order_relaxed,
                                       std::memory_order_relaxed)) {
            return;
        }

        // При конфлікті оновлюємо окремий шардований осередок
        size_t slot_idx = core_or_thread_id % N_SLOTS;
        slots[slot_idx].value.fetch_add(val, std::memory_order_relaxed);
    }

    // Зчитування сумарного значення
    uint32_t read_sum() const {
        uint32_t total = base.load(std::memory_order_relaxed);
        for (size_t i = 0; i < N_SLOTS; ++i) {
            total += slots[i].value.load(std::memory_order_relaxed);
        }
        return total;
    }
};
