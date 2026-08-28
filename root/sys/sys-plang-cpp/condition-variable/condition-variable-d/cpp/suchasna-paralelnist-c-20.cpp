#include <iostream>
#include <thread>
#include <condition_variable>
#include <mutex>
#include <chrono>

std::condition_variable_any cv;
std::mutex mtx;
bool data_ready = false;

void worker_thread(std::stop_token stoken) {
    std::unique_lock<std::mutex> lock(mtx);
    
    // C++20: wait приймає stop_token.
    // Якщо надходить сигнал скасування, wait() негайно розблоковується!
    bool success = cv.wait(lock, stoken, []{ return data_ready; });
    
    if (stoken.stop_requested()) {
        std::cout << "Потік отримав сигнал скасування! Вихід.\n";
        return;
    }
    
    std::cout << "Дані успішно оброблені!\n";
}

int main() {
    std::jthread worker(worker_thread);
    
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    // Автоматично надсилаємо сигнал скасування та будимо умовну змінну
    worker.request_stop(); 
    // При виході з main jthread автоматично зробить join()
}
