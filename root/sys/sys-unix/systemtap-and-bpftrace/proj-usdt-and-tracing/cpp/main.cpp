// main.cpp — Ідіоматична реалізація мовою C++
#include <iostream>
#include <random>
#include <thread>
#include <chrono>
#include <memory>
#include <string_view>
#include <sys/sdt.h>

class TaskWorker {
public:
    explicit TaskWorker(int worker_id) : worker_id_(worker_id) {}

    void execute_task(int task_id) {
        // RAII-обгортка для автоматичного виклику USDT-маркерів початку та виходу
        struct ScopedTaskProbe {
            int task_id;
            int worker_id;
            int status{0};

            ScopedTaskProbe(int t_id, int w_id) : task_id(t_id), worker_id(w_id) {
                STAP_PROBE2(workpool, task_start, task_id, worker_id);
            }

            ~ScopedTaskProbe() {
                STAP_PROBE3(workpool, task_finish, task_id, worker_id, status);
            }
        } probe{task_id, worker_id_};

        // Імітація обробки завдання з використанням C++11 random та chrono
        static thread_local std::mt19937 gen{std::random_device{}()};
        std::uniform_int_distribution<int> dist_us(10, 100);
        std::uniform_int_distribution<int> dist_err(1, 100);

        std::this_thread::sleep_for(std::chrono::microseconds(dist_us(gen)));

        if (dist_err(gen) == 1) {
            probe.status = -1; // 1% статус помилки
        }
    }

private:
    int worker_id_;
};

int main() {
    std::cout << "C++ TaskWorker Engine запущену [PID: " << getpid() << "]\n";

    auto worker = std::make_unique<TaskWorker>(1);
    int task_counter = 0;

    while (true) {
        worker->execute_task(++task_counter);
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }

    return 0;
}
