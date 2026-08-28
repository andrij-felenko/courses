#include <iostream>
#include <stop_token>
#include <thread>

void worker(std::stop_token stoken) {
    while (!stoken.stop_requested()) {
        std::cout << "Потік працює...\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    std::cout << "Отримано сигнал скасування. Чистий вихід із потоку.\n";
}

int main() {
    std::stop_source ssource;
    std::stop_token stoken = ssource.get_token();

    std::jthread th(worker, stoken);

    std::this_thread::sleep_for(std::chrono::milliseconds(150));
    ssource.request_stop(); // Ініціація скасування

    th.join();
    return 0;
}
