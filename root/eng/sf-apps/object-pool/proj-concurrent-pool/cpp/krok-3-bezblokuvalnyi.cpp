struct Conn {
    // ... справжні поля з'єднання ...
    Conn* next_free;                       // ← лінк вільного списку живе В об'єкті:
};                                         //   поки Conn вільний, його тіло не потрібне

class LockFreeStack {
    std::atomic<Conn*> head{nullptr};
public:
    void push(Conn* n) {
        Conn* old = head.load(std::memory_order_relaxed);
        do {
            n->next_free = old;                          // готуємо ланку на поточну вершину
        } while (!head.compare_exchange_weak(
                     old, n,
                     std::memory_order_release,          // успіх: ПУБЛІКУЄМО n (крок 4)
                     std::memory_order_relaxed));        // невдача: old перечитано автоматично
    }

    Conn* pop() {
        Conn* old = head.load(std::memory_order_acquire);
        while (old && !head.compare_exchange_weak(
                          old, old->next_free,
                          std::memory_order_acquire,     // успіх: БАЧИМО те, що опублікував push
                          std::memory_order_acquire)) {
            // old оновлено поточним head — цикл повторюється
        }
        return old;                                      // nullptr, якщо стек порожній
    }
};
