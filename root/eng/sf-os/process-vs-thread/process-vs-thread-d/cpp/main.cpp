#include <iostream>
#include <vector>
#include <thread>
#include <numeric>
#include <span>
#include <system_error>
#include <unistd.h>
#include <sys/wait.h>

constexpr size_t ARRAY_SIZE = 1'000'000;

// Обчислення суми частини масиву через std::span
long long calculate_sum(std::span<const int> slice) noexcept {
    return std::accumulate(slice.begin(), slice.end(), 0LL);
}

int main() {
    std::vector<int> data(ARRAY_SIZE, 1);
    const size_t mid = ARRAY_SIZE / 2;

    std::cout << "--- ВАРІАНТ 1: Обчислення через ПОТОКИ (C++ std::jthread) ---\n";
    long long thread_part_sum = 0;
    {
        std::span<const int> second_half(data.data() + mid, ARRAY_SIZE - mid);
        // jthread отримує прямий доступ до пам'яті вектора
        std::jthread worker([second_half, &thread_part_sum]() {
            thread_part_sum = calculate_sum(second_half);
        });

        // Головний потік обчислює свою половину
        std::span<const int> first_half(data.data(), mid);
        long long main_part_sum = calculate_sum(first_half);

        // worker автоматично приєднується (join) при виході з блоку видимості
        std::cout << "Результат через потоки: "
                  << (main_part_sum + thread_part_sum) << "\n\n";
    }

    std::cout << "--- ВАРІАНТ 2: Обчислення через ПРОЦЕСИ (fork + pipe) ---\n";
    int pipefd[2];
    if (::pipe(pipefd) < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка створення pipe");
    }

    pid_t pid = ::fork();
    if (pid < 0) {
        throw std::system_error(errno, std::generic_category(), "Помилка fork");
    }

    if (pid == 0) {
        // Дочірній процес
        ::close(pipefd[0]);
        std::span<const int> second_half(data.data() + mid, ARRAY_SIZE - mid);
        long long child_sum = calculate_sum(second_half);

        ::write(pipefd[1], &child_sum, sizeof(child_sum));
        ::close(pipefd[1]);
        ::_exit(0);
    }

    // Батьківський процес
    ::close(pipefd[1]);
    std::span<const int> first_half(data.data(), mid);
    long long parent_sum = calculate_sum(first_half);

    long long child_result = 0;
    ::read(pipefd[0], &child_result, sizeof(child_result));
    ::close(pipefd[0]);

    int status = 0;
    ::waitpid(pid, &status, 0);

    std::cout << "Результат через процеси: "
              << (parent_sum + child_result) << '\n';

    return 0;
}
