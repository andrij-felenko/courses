#include <mutex>
#include <chrono>

void complex_processing(std::mutex& mtx) {
    // 1. Відкладене захоплення: м'ютекс запам'ятовано, але lock() ще НЕ викликано
    std::unique_lock<std::mutex> lock(mtx, std::defer_lock);

    // Виконання довгої підготовки БЕЗ захоплення замка
    do_heavy_setup();

    // 2. Явне захоплення замка у потрібний момент
    lock.lock();

    // Робота з критичною секцією
    modify_shared_resource();

    // 3. Дострокове тимчасове розблокування для звільнення ниток-конкурентів
    lock.unlock();

    do_unrelated_work();

    // 4. Спроба повторного захоплення з таймаутом
    if (lock.try_lock_for(std::chrono::milliseconds(100))) {
        // Успішно захоплено знову
    }
} // Деструктор unique_lock перевіряє, чи захоплено м'ютекс, і якщо так — викликає unlock()
