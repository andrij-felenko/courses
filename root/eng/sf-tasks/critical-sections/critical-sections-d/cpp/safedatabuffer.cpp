#include <mutex>
#include <cstdint>

// Клас захищеної черги повідомлень у RTOS або просторі користувача
class SafeDataBuffer {
private:
    uint32_t buffer_[64];
    size_t head_ = 0;
    size_t count_ = 0;
    mutable std::mutex mutex_;

public:
    bool push(uint32_t item) {
        // RAII-захоплення примітиву взаємного виключення
        std::lock_guard<std::mutex> lock(mutex_);

        if (count_ >= 64) {
            return false; // Буфер заповнений
        }

        buffer_[(head_ + count_) % 64] = item;
        ++count_;
        return true;
        // Замок автоматично вивільняється при виході з функції
    }

    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return count_;
    }
};
