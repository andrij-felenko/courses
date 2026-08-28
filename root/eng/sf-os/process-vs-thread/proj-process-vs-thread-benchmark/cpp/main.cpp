#include <iostream>
#include <chrono>
#include <thread>
#include <vector>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <fstream>
#include <string>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/wait.h>

constexpr int ITERATIONS = 5000;
constexpr int PING_PONG_COUNT = 10000;

// Отримання VmRSS процесу через procfs
long get_rss_kb() {
    std::ifstream status_file("/proc/self/status");
    std::string line;
    while (std::getline(status_file, line)) {
        if (line.rfind("VmRSS:", 0) == 0) {
            return std::stol(line.substr(6));
        }
    }
    return -1;
}

// ── ТЕСТ 1: Швидкість створення та очікування ─────────────────────────────
void test_creation_latency() {
    std::cout << "=== ТЕСТ 1: Швидкість створення та завершення (" << ITERATIONS << " ітерацій) ===\n";

    // Вимірювання процесів (fork + waitpid)
    auto start = std::chrono::steady_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        pid_t pid = ::fork();
        if (pid == 0) {
            ::_exit(0);
        } else if (pid > 0) {
            int status = 0;
            ::waitpid(pid, &status, 0);
        }
    }
    auto proc_duration = std::chrono::duration_cast<std::chrono::microseconds>(
        std::chrono::steady_clock::now() - start).count();
    double proc_avg_us = static_cast<double>(proc_duration) / ITERATIONS;

    // Вимірювання потоків через std::jthread
    start = std::chrono::steady_clock::now();
    for (int i = 0; i < ITERATIONS; ++i) {
        std::jthread worker([]() {
            // Порожнє тіло для виміру накладних витрат
        });
        // jthread автоматично викликає join() у своєму деструкторі
    }
    auto thread_duration = std::chrono::duration_cast<std::chrono::microseconds>(
        std::chrono::steady_clock::now() - start).count();
    double thread_avg_us = static_cast<double>(thread_duration) / ITERATIONS;

    std::cout << "  Процеси (fork + wait):   сер. час = " << proc_avg_us << " мкс\n";
    std::cout << "  Потоки (std::jthread):   сер. час = " << thread_avg_us << " мкс\n";
    std::cout << "  -> Потоки створюються у " << (proc_avg_us / thread_avg_us)
              << "x швидше за процеси\n\n";
}

// ── ТЕСТ 2: Затримка передачі даних (Pipe проти Shared Memory) ───────────
void test_ipc_vs_shared_mem() {
    std::cout << "=== ТЕСТ 2: Затримка передачі даних (" << PING_PONG_COUNT << " обмінів) ===\n";

    // 1. Міжпроцесний обмін через пайпи
    int p2c[2], c2p[2];
    if (::pipe(p2c) < 0 || ::pipe(c2p) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка pipe");
    }

    auto start = std::chrono::steady_clock::now();
    pid_t pid = ::fork();
    if (pid == 0) {
        ::close(p2c[1]); ::close(c2p[0]);
        uint64_t val = 0;
        for (int i = 0; i < PING_PONG_COUNT; ++i) {
            if (::read(p2c[0], &val, sizeof(val)) <= 0) break;
            val++;
            if (::write(c2p[1], &val, sizeof(val)) <= 0) break;
        }
        ::close(p2c[0]); ::close(c2p[1]);
        ::_exit(0);
    } else {
        ::close(p2c[0]); ::close(c2p[1]);
        uint64_t val = 0;
        for (int i = 0; i < PING_PONG_COUNT; ++i) {
            if (::write(p2c[1], &val, sizeof(val)) <= 0) break;
            if (::read(c2p[0], &val, sizeof(val)) <= 0) break;
        }
        int status = 0;
        ::waitpid(pid, &status, 0);
        ::close(p2c[1]); ::close(c2p[0]);
    }
    auto pipe_us = std::chrono::duration_cast<std::chrono::microseconds>(
        std::chrono::steady_clock::now() - start).count();
    double pipe_latency = static_cast<double>(pipe_us) / (PING_PONG_COUNT * 2);

    // 2. Багатопотоковий обмін через спільну пам'ять із м'ютексом
    std::mutex mtx;
    std::condition_variable cv;
    uint64_t shared_val = 0;
    int turn = 0; // 0 - черга головного, 1 - черга воркера

    start = std::chrono::steady_clock::now();
    {
        std::jthread worker([&]() {
            for (int i = 0; i < PING_PONG_COUNT; ++i) {
                std::unique_lock<std::mutex> lock(mtx);
                cv.wait(lock, [&]() { return turn == 1; });
                shared_val++;
                turn = 0;
                cv.notify_one();
            }
        });

        for (int i = 0; i < PING_PONG_COUNT; ++i) {
            std::unique_lock<std::mutex> lock(mtx);
            cv.wait(lock, [&]() { return turn == 0; });
            shared_val++;
            turn = 1;
            cv.notify_one();
        }
    } // worker jthread join() викликається тут автоматично
    auto thread_us = std::chrono::duration_cast<std::chrono::microseconds>(
        std::chrono::steady_clock::now() - start).count();
    double thread_latency = static_cast<double>(thread_us) / (PING_PONG_COUNT * 2);

    std::cout << "  Міжпроцесний обмін (Pipe IPC):     сер. затримка = " << pipe_latency << " мкс\n";
    std::cout << "  Спільна пам'ять (std::mutex + cv): сер. затримка = " << thread_latency << " мкс\n";
    std::cout << "  -> Спільна пам'ять у " << (pipe_latency / thread_latency)
              << "x швидша за системні канали\n\n";
}

// ── ТЕСТ 3: Демонстрація ізоляції збоїв ───────────────────────────────────
void test_fault_isolation() {
    std::cout << "=== ТЕСТ 3: Демонстрація ізоляції збоїв (SIGSEGV) ===\n";

    pid_t pid = ::fork();
    if (pid == 0) {
        std::cout << "  [Дочірній процес] Навмисний запис за покажчиком nullptr...\n";
        volatile int *bad_ptr = nullptr;
        *bad_ptr = 42; // Генерує апаратний page fault -> SIGSEGV
        ::_exit(0);
    } else {
        int status = 0;
        ::waitpid(pid, &status, 0);
        if (WIFSIGNALED(status)) {
            std::cout << "  [Батьківський процес] Нащадок упав від сигналу "
                      << WTERMSIG(status) << " (" << ::strsignal(WTERMSIG(status)) << ")\n";
            std::cout << "  [Батьківський процес] Батьківський процес живий і неушкоджений!\n";
        }
    }
    std::cout << "  -> У багатопотоковому режимі такий самий збій призвів би до аварійного "
                 "завершення всієї програми.\n\n";
}

int main() {
    std::cout << "=================================================================\n";
    std::cout << "  БЕНЧМАРК: ПРОЦЕСИ ПРОТИ ПОТОКІВ НА LINUX (C++20)\n";
    std::cout << "=================================================================\n\n";

    std::cout << "Базовий обсяг RSS процесу: " << get_rss_kb() << " КБ\n\n";

    test_creation_latency();
    test_ipc_vs_shared_mem();
    test_fault_isolation();

    return 0;
}
