#include <coroutine>

Task process_coroutine() {
    // Звернення до пам'яті Потоку 1
    thread_local_buffer.push_back("Data Part 1");

    co_await async_io_operation(); // Призупинення. Відновлення у Потоці 2!

    // НЕБЕЗПЕКА: Тепер ми читаємо буфер Потоку 2, де наших даних немає!
    send_data(thread_local_buffer);
}
