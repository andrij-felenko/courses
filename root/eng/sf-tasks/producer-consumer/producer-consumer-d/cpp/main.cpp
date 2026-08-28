#include <semaphore>
#include <mutex>

constexpr std::ptrdiff_t BUFFER_CAPACITY = 16;
std::counting_semaphore<BUFFER_CAPACITY> empty_slots(BUFFER_CAPACITY);
std::counting_semaphore<BUFFER_CAPACITY> full_slots(0);
std::mutex mtx;

void producer(Data item) {
    empty_slots.acquire(); // Очікування вільного слота
    {
        std::lock_guard<std::mutex> lock(mtx);
        enqueue(std::move(item));
    }
    full_slots.release();  // Сповіщення про наявність даних
}

Data consumer() {
    full_slots.acquire();  // Очікування заповненого слота
    Data item;
    {
        std::lock_guard<std::mutex> lock(mtx);
        item = dequeue();
    }
    empty_slots.release(); // Звільнення слота для виробників
    return item;
}
