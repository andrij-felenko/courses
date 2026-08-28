#include <iostream>
#include <thread>
#include <mutex>
#include <chrono>
#include <cstdint>
#include <pthread.h>
#include <unistd.h>
#include <sys/prctl.h>

struct Account {
    uint64_t account_id;
    double balance;
    std::mutex lock;
};

struct TransferTask {
    uint64_t tx_id;
    Account& src;
    Account& dst;
    double amount;
    volatile bool cancel_flag{false};
};

static Account g_account_a{101, 10000.0, {}};
static Account g_account_b{202, 10000.0, {}};

static void worker_func_1(TransferTask& task) {
    pthread_setname_np(pthread_self(), "tx-worker-A2B");
    std::cout << "[Worker 1] Стартує переказ #" << task.tx_id
              << ": рахунок " << task.src.account_id << " -> " << task.dst.account_id << "\n";

    task.src.lock.lock();
    std::cout << "[Worker 1] Захоплено рахунок " << task.src.account_id << ", пауза перед захопленням...\n";
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << "[Worker 1] Спроба захопити рахунок " << task.dst.account_id << "...\n";
    task.dst.lock.lock();

    task.src.balance -= task.amount;
    task.dst.balance += task.amount;

    task.dst.lock.unlock();
    task.src.lock.unlock();
    std::cout << "[Worker 1] Переказ #" << task.tx_id << " успішно завершено!\n";
}

static void worker_func_2(TransferTask& task) {
    pthread_setname_np(pthread_self(), "tx-worker-B2A");
    std::cout << "[Worker 2] Стартує переказ #" << task.tx_id
              << ": рахунок " << task.src.account_id << " -> " << task.dst.account_id << "\n";

    task.src.lock.lock();
    std::cout << "[Worker 2] Захоплено рахунок " << task.src.account_id << ", пауза перед захопленням...\n";
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << "[Worker 2] Спроба захопити рахунок " << task.dst.account_id << "...\n";
    task.dst.lock.lock();

    task.src.balance -= task.amount;
    task.dst.balance += task.amount;

    task.dst.lock.unlock();
    task.src.lock.unlock();
    std::cout << "[Worker 2] Переказ #" << task.tx_id << " успішно завершено!\n";
}

int main() {
    prctl(PR_SET_PTRACER, PR_SET_PTRACER_ANY, 0, 0, 0);

    std::cout << "=== Платіжний вузол запущено (PID: " << getpid() << ") ===\n";
    std::cout << "Адреси м'ютексів: Account A (" << &g_account_a.lock
              << "), Account B (" << &g_account_b.lock << ")\n";

    TransferTask task1{9001, g_account_a, g_account_b, 150.0};
    TransferTask task2{9002, g_account_b, g_account_a, 300.0};

    std::thread th1(worker_func_1, std::ref(task1));
    std::thread th2(worker_func_2, std::ref(task2));

    th1.join();
    th2.join();

    std::cout << "Усі транзакції завершено. Баланс A: " << g_account_a.balance
              << ", B: " << g_account_b.balance << "\n";
    return 0;
}
