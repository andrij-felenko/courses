#include <Arduino.h>
#include <atomic>

struct Node {
    uint32_t value;
    Node* next;
};

// Структура версіонованого вказівника
struct TaggedPointer {
    Node* ptr;
    uint32_t tag;
};

class LockFreeStack {
private:
    std::atomic<TaggedPointer> head;

public:
    LockFreeStack() {
        head.store({nullptr, 0}, std::memory_order_relaxed);
    }

    // Безблоковий pop із захистом від ABA через tagged pointer
    bool pop(uint32_t& out_value) {
        TaggedPointer expected = head.load(std::memory_order_relaxed);
        uint32_t backoff = 1;

        while (expected.ptr != nullptr) {
            TaggedPointer desired;
            desired.ptr = expected.ptr->next;
            desired.tag = expected.tag + 1; // Новий тег гарантує відсутність ABA

            if (head.compare_exchange_weak(
                    expected,
                    desired,
                    std::memory_order_acquire,
                    std::memory_order_relaxed)) {
                out_value = expected.ptr->value;
                return true;
            }

            // Колізійна пауза (backoff) для зниження навантаження на шину
            for (uint32_t i = 0; i < backoff; ++i) {
                yield(); // Адаптивна поступальність для системи
            }
            if (backoff < 32) backoff *= 2;
        }

        return false;
    }
};
