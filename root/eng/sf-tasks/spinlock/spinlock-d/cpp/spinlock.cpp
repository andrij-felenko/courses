#include <atomic>

// Клас спін-замка для забезпечення взаємного виключення потоків
class Spinlock {
private:
    // ATOMIC_FLAG_INIT гарантує, що прапорець початково скинутий у false
    std::atomic_flag flag = ATOMIC_FLAG_INIT;

public:
    // Метод захоплення замка
    void lock() noexcept {
        // test_and_set повертає попереднє значення прапорця.
        // Перебуваємо в циклі, доки повернуте значення дорівнює true.
        while (flag.test_and_set(std::memory_order_acquire)) {
            // Процесорльне ядро продовжує виконувати цикл активного очікування
        }
    }

    // Метод звільнення замка
    void unlock() noexcept {
        // Атомарно скидаємо прапорець у false із семантикою release
        flag.clear(std::memory_order_release);
    }
};
