#include <thread>
#include <iostream>

int compute_payload() {
    // Важке обчислення
    return 42;
}

int main() {
    // Ззвичайний запуск: повернене значення compute_payload() ігнорується!
    std::thread t(compute_payload);
    t.join();
    // Як прочитати 42 у головному потоці?
}
