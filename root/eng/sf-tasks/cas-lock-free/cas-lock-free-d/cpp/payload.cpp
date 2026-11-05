#include <atomic>
#include <memory>
#include <vector>

struct Payload {
    std::vector<int> values;
    int revision;
};

class AtomicPublisher {
private:
    std::atomic<Payload*> current_payload_{nullptr};

public:
    ~AtomicPublisher() {
        delete current_payload_.load(std::memory_order_relaxed);
    }

    void publish(Payload* new_data) {
        Payload* expected = current_payload_.load(std::memory_order_relaxed);
        
        while (!current_payload_.compare_exchange_weak(
            expected,
            new_data,
            std::memory_order_release, // Опублікований об'єкт гарантовано повністю ініціалізований
            std::memory_order_relaxed))
        {
            // При невдачі expected оновлюється актуальним вказівником
        }
    }

    Payload* acquire_current() const {
        // Читач бачить усі поля Payload у стані після публікації
        return current_payload_.load(std::memory_order_acquire);
    }
};
