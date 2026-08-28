#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <chrono>
#include <optional>
#include <unordered_map>
#include <queue>
#include <cstring>
#include <cerrno>

#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <poll.h>
#include <signal.h>

// Результат виконання функції
struct ExecutionResult {
    bool success{false};
    bool timed_out{false};
    int exit_code{0};
    std::string response;
    std::string error_log;
    double duration_ms{0.0};
    long max_rss_kb{0};
    bool was_cold_start{false};
};

// RAII-обгортка для файлових дескрипторів
class PipeChannel {
public:
    PipeChannel() {
        int fds[2];
        if (pipe(fds) != 0) {
            throw std::runtime_error("Не вдалося створити pipe: " + std::string(strerror(errno)));
        }
        read_fd_ = fds[0];
        write_fd_ = fds[1];
    }

    ~PipeChannel() {
        close_read();
        close_write();
    }

    void close_read() noexcept {
        if (read_fd_ >= 0) { close(read_fd_); read_fd_ = -1; }
    }

    void close_write() noexcept {
        if (write_fd_ >= 0) { close(write_fd_); write_fd_ = -1; }
    }

    int read_fd() const noexcept { return read_fd_; }
    int write_fd() const noexcept { return write_fd_; }

    PipeChannel(const PipeChannel&) = delete;
    PipeChannel& operator=(const PipeChannel&) = delete;
    PipeChannel(PipeChannel&& o) noexcept : read_fd_(o.read_fd_), write_fd_(o.write_fd_) {
        o.read_fd_ = -1; o.write_fd_ = -1;
    }

private:
    int read_fd_{-1};
    int write_fd_{-1};
};

// Екземпляр ізольованої пісочниці
class SandboxInstance {
public:
    SandboxInstance(std::string binary_path, std::string function_id)
        : binary_path_(std::move(binary_path)), function_id_(std::move(function_id)) {}

    ~SandboxInstance() {
        terminate();
    }

    // Запуск ізольованого дочірнього процесу
    void spawn() {
        // Ігноруємо SIGPIPE у батьківському процесі для безпечного запису в канали
        signal(SIGPIPE, SIG_IGN);

        PipeChannel stdin_pipe;
        PipeChannel stdout_pipe;
        PipeChannel stderr_pipe;

        pid_t pid = fork();
        if (pid < 0) {
            throw std::runtime_error("Помилка fork(): " + std::string(strerror(errno)));
        }

        if (pid == 0) {
            // Дочірній процес (пісочниця)
            dup2(stdin_pipe.read_fd(), STDIN_FILENO);
            dup2(stdout_pipe.write_fd(), STDOUT_FILENO);
            dup2(stderr_pipe.write_fd(), STDERR_FILENO);

            // Закриття зайвих дескрипторів
            stdin_pipe.close_write();
            stdout_pipe.close_read();
            stderr_pipe.close_read();

            // Встановлення змінних оточення пісочниці
            setenv("AWS_LAMBDA_FUNCTION_NAME", function_id_.c_str(), 1);
            setenv("LAMBDA_TASK_ROOT", "/tmp", 1);

            char* const args[] = {const_cast<char*>(binary_path_.c_str()), nullptr};
            execv(binary_path_.c_str(), args);

            // Якщо execv зазнав невдачі
            std::cerr << "Помилка запуску бінарника: " << strerror(errno) << "\n";
            _exit(127);
        }

        // Батьківський процес (виконавець)
        pid_ = pid;
        is_alive_ = true;

        in_fd_ = stdin_pipe.write_fd();
        out_fd_ = stdout_pipe.read_fd();
        err_fd_ = stderr_pipe.read_fd();

        // Робимо дескриптори неблокуючими для безпечного читання через poll()
        fcntl(out_fd_, F_SETFL, fcntl(out_fd_, F_GETFL, 0) | O_NONBLOCK);
        fcntl(err_fd_, F_SETFL, fcntl(err_fd_, F_GETFL, 0) | O_NONBLOCK);

        // Передаємо володіння
        stdin_pipe.close_read();
        stdout_pipe.close_write();
        stderr_pipe.close_write();
    }

    // Виконання одного запиту з жорстким тайм-аутом
    ExecutionResult invoke(std::string_view payload, std::chrono::milliseconds timeout) {
        ExecutionResult res;
        auto start_time = std::chrono::steady_clock::now();

        if (!is_alive_) {
            res.success = false;
            res.error_log = "Пісочниця не активна";
            return res;
        }

        // 1. Відправка корисного навантаження у stdin функції
        std::string input = std::string(payload) + "\n";
        size_t written = 0;
        while (written < input.size()) {
            ssize_t bytes = write(in_fd_, input.data() + written, input.size() - written);
            if (bytes <= 0) {
                if (errno == EPIPE) {
                    res.success = false;
                    res.error_log = "Процес пісочниці аварійно закрив stdin (EPIPE)";
                    is_alive_ = false;
                    return res;
                }
                res.success = false;
                res.error_log = "Помилка запису у канал stdin пісочниці";
                return res;
            }
            written += static_cast<size_t>(bytes);
        }

        // 2. Очікування завершення або вичерпання тайм-ауту через poll()
        struct pollfd pfd[2];
        pfd[0].fd = out_fd_;
        pfd[0].events = POLLIN | POLLHUP;
        pfd[1].fd = err_fd_;
        pfd[1].events = POLLIN | POLLHUP;

        std::string stdout_buffer;
        std::string stderr_buffer;
        bool completed = false;

        while (!completed) {
            auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now() - start_time);
            
            if (elapsed >= timeout) {
                // Перевищено ліміт часу — примусове знищення процесу
                res.timed_out = true;
                terminate();
                break;
            }

            int remaining_ms = static_cast<int>((timeout - elapsed).count());
            int ret = poll(pfd, 2, std::min(remaining_ms, 50));

            if (ret < 0) {
                if (errno == EINTR) continue;
                break;
            }

            if (ret > 0) {
                char buf[4096];
                if (pfd[0].revents & POLLIN) {
                    ssize_t n = read(out_fd_, buf, sizeof(buf));
                    if (n > 0) stdout_buffer.append(buf, n);
                }
                if (pfd[1].revents & POLLIN) {
                    ssize_t n = read(err_fd_, buf, sizeof(buf));
                    if (n > 0) stderr_buffer.append(buf, n);
                }

                // Перевірка завершення процесу
                int status;
                pid_t wp = waitpid(pid_, &status, WNOHANG);
                if (wp == pid_) {
                    is_alive_ = false;
                    completed = true;
                    if (WIFEXITED(status)) {
                        res.exit_code = WEXITSTATUS(status);
                        res.success = (res.exit_code == 0);
                    } else if (WIFSIGNALED(status)) {
                        res.exit_code = 128 + WTERMSIG(status);
                        res.success = false;
                    }
                }
            }
        }

        auto end_time = std::chrono::steady_clock::now();
        res.duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
        res.response = stdout_buffer;
        res.error_log = stderr_buffer;

        // Збір статистики споживання пам'яті через getrusage
        struct rusage usage{};
        getrusage(RUSAGE_CHILDREN, &usage);
        res.max_rss_kb = usage.ru_maxrss;

        return res;
    }

    void terminate() noexcept {
        if (is_alive_ && pid_ > 0) {
            // М'яка спроба зупинки
            kill(pid_, SIGTERM);
            
            // Очікування 100 мс
            usleep(100'000);
            
            int status;
            if (waitpid(pid_, &status, WNOHANG) == 0) {
                // Примусове знищення процесу
                kill(pid_, SIGKILL);
                waitpid(pid_, &status, 0);
            }
            is_alive_ = false;
        }

        if (in_fd_ >= 0) { close(in_fd_); in_fd_ = -1; }
        if (out_fd_ >= 0) { close(out_fd_); out_fd_ = -1; }
        if (err_fd_ >= 0) { close(err_fd_); err_fd_ = -1; }
    }

    bool is_alive() const noexcept { return is_alive_; }
    pid_t pid() const noexcept { return pid_; }

private:
    std::string binary_path_;
    std::string function_id_;
    pid_t pid_{-1};
    bool is_alive_{false};
    int in_fd_{-1};
    int out_fd_{-1};
    int err_fd_{-1};
};

// Менеджер пулу теплих пісочниць
class FaaSWorkerPool {
public:
    explicit FaaSWorkerPool(size_t max_warm_instances_per_function = 4)
        : max_warm_(max_warm_instances_per_function) {}

    ExecutionResult dispatch(const std::string& function_id, 
                             const std::string& binary_path,
                             std::string_view payload, 
                             std::chrono::milliseconds timeout) {
        std::unique_ptr<SandboxInstance> sandbox;
        bool cold_start = false;

        // 1. Пошук теплого екземпляра у черзі
        auto& queue = warm_pools_[function_id];
        while (!queue.empty()) {
            sandbox = std::move(queue.front());
            queue.pop();
            if (sandbox && sandbox->is_alive()) {
                break;
            }
            sandbox.reset();
        }

        // 2. Якщо теплий екземпляр відсутній — виконуємо холодний старт
        if (!sandbox) {
            cold_start = true;
            sandbox = std::make_unique<SandboxInstance>(binary_path, function_id);
            sandbox->spawn();
        }

        // 3. Виконання запиту
        ExecutionResult res = sandbox->invoke(payload, timeout);
        res.was_cold_start = cold_start;

        // 4. Повернення екземпляра в теплий пул, якщо він живий і не зазнав аварії
        if (sandbox->is_alive() && !res.timed_out && res.success) {
            if (queue.size() < max_warm_) {
                queue.push(std::move(sandbox));
            } else {
                sandbox->terminate();
            }
        }

        return res;
    }

private:
    size_t max_warm_;
    std::unordered_map<std::string, std::queue<std::unique_ptr<SandboxInstance>>> warm_pools_;
};

int main() {
    std::cout << "[FaaS Worker] Диспетчер готовий до обробки подій\n";
    FaaSWorkerPool pool(2);

    // Симуляція першого виклику (Холодний старт)
    std::cout << "\n--- Запит #1 (Холодний старт) ---\n";
    auto res1 = pool.dispatch("echo-service", "/bin/cat", "{\"event\": \"order_created\"}", std::chrono::milliseconds(2000));
    std::cout << "Успіх: " << std::boolalpha << res1.success << "\n"
              << "Холодний старт: " << res1.was_cold_start << "\n"
              << "Час виконання: " << res1.duration_ms << " мс\n"
              << "Відповідь: " << res1.response;

    // Симуляція повторного виклику (Теплий запуск)
    std::cout << "\n--- Запит #2 (Теплий запуск) ---\n";
    auto res2 = pool.dispatch("echo-service", "/bin/cat", "{\"event\": \"payment_received\"}", std::chrono::milliseconds(2000));
    std::cout << "Успіх: " << std::boolalpha << res2.success << "\n"
              << "Холодний старт: " << res2.was_cold_start << "\n"
              << "Час виконання: " << res2.duration_ms << " мс\n"
              << "Відповідь: " << res2.response;

    return 0;
}
