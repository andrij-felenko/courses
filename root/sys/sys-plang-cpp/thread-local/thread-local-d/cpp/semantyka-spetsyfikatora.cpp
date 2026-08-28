#include <iostream>
#include <thread>
#include <string>

// 1. Глобальна thread_local змінна із зовнішнім зв'язуванням (External Linkage)
thread_local int per_thread_counter = 0;

// 2. Статична змінна рівня одиниці трансляції (Internal Linkage)
static thread_local std::string per_thread_tag = "unnamed";

void worker(int thread_id) {
    // 3. Блочна thread_local змінна: неявно static, ініціалізується ліниво
    thread_local int invocation_count = 0;

    per_thread_counter += 10;
    per_thread_tag = "worker-" + std::to_string(thread_id);
    invocation_count++;

    std::cout << "Thread " << thread_id 
              << ": counter=" << per_thread_counter 
              << ", tag=" << per_thread_tag 
              << ", invocations=" << invocation_count 
              << ", address=" << &per_thread_counter << '\n';
}

int main() {
    std::jthread t1(worker, 1);
    std::jthread t2(worker, 2);
    t1.join();
    t2.join();
    worker(0); // Виконання в головному потоці
}
