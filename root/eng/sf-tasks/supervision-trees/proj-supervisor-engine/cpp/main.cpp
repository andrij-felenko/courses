#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <memory>
#include <functional>
#include <system_error>
#include <thread>
#include <algorithm>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>

enum class Strategy {
    OneForOne,
    RestForOne
};

enum class RestartType {
    Permanent,
    Transient,
    Temporary
};

struct ChildSpec {
    std::string name;
    std::function<void()> worker_fn;
    RestartType restart_type{RestartType::Permanent};
    pid_t pid{-1};
    bool is_alive{false};
};

class Supervisor {
public:
    Supervisor(Strategy strategy, int max_restarts, std::chrono::seconds max_time)
        : strategy_(strategy), max_restarts_(max_restarts), max_time_(max_time) {}

    ~Supervisor() {
        shutdown_all();
    }

    void add_child(std::string name, std::function<void()> fn, RestartType restart = RestartType::Permanent) {
        children_.push_back(ChildSpec{std::move(name), std::move(fn), restart, -1, false});
    }

    void run() {
        for (size_t i = 0; i < children_.size(); ++i) {
            if (!start_child(i)) {
                throw std::runtime_error("Не вдалося запустити нащадка: " + children_[i].name);
            }
        }

        while (has_living_children()) {
            int status = 0;
            pid_t died_pid = ::waitpid(-1, &status, 0);
            if (died_pid < 0) {
                if (errno == EINTR) continue;
                break;
            }

            auto it = std::find_if(children_.begin(), children_.end(),
                                   [died_pid](const ChildSpec& c) { return c.pid == died_pid; });
            if (it == children_.end()) continue;

            size_t child_idx = std::distance(children_.begin(), it);
            ChildSpec& spec = children_[child_idx];
            spec.is_alive = false;

            bool is_normal = WIFEXITED(status) && (WEXITSTATUS(status) == 0);
            std::cout << "[SUPERVISOR] Процес '" << spec.name << "' завершився. "
                      << "Нормально=" << std::boolalpha << is_normal << "\n";

            bool need_restart = (spec.restart_type == RestartType::Permanent) ||
                                (spec.restart_type == RestartType::Transient && !is_normal);

            if (!need_restart) {
                std::cout << "[SUPERVISOR] Процес '" << spec.name << "' не вимагає відновлення.\n";
                continue;
            }

            check_restart_budget();

            if (strategy_ == Strategy::OneForOne) {
                start_child(child_idx);
            } else if (strategy_ == Strategy::RestForOne) {
                for (size_t i = children_.size(); i-- > child_idx + 1; ) {
                    stop_child(i);
                }
                start_child(child_idx);
                for (size_t i = child_idx + 1; i < children_.size(); ++i) {
                    start_child(i);
                }
            }
        }
    }

private:
    bool start_child(size_t index) {
        ChildSpec& spec = children_[index];
        pid_t pid = ::fork();
        if (pid < 0) return false;
        if (pid == 0) {
            ::signal(SIGINT, SIG_DFL);
            ::signal(SIGTERM, SIG_DFL);
            spec.worker_fn();
            ::_exit(0);
        }
        spec.pid = pid;
        spec.is_alive = true;
        std::cout << "[SUPERVISOR] Запущено '" << spec.name << "' [PID " << pid << "]\n";
        return true;
    }

    void stop_child(size_t index) {
        ChildSpec& spec = children_[index];
        if (!spec.is_alive) return;

        std::cout << "[SUPERVISOR] Зупинка '" << spec.name << "' [PID " << spec.pid << "]\n";
        ::kill(spec.pid, SIGTERM);

        for (int i = 0; i < 20; ++i) {
            int status = 0;
            pid_t res = ::waitpid(spec.pid, &status, WNOHANG);
            if (res == spec.pid) {
                spec.is_alive = false;
                return;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }

        ::kill(spec.pid, SIGKILL);
        ::waitpid(spec.pid, nullptr, 0);
        spec.is_alive = false;
    }

    void check_restart_budget() {
        auto now = std::chrono::steady_clock::now();
        
        // Відкидаємо аварії, старіші за max_time_
        std::erase_if(crash_history_, [now, this](const auto& tp) {
            return now - tp > max_time_;
        });

        crash_history_.push_back(now);

        if (static_cast<int>(crash_history_.size()) > max_restarts_) {
            std::cerr << "[SUPERVISOR] Перевищено ліміт перезапусків! Ескалація аварії.\n";
            shutdown_all();
            throw std::runtime_error("Supervisor crash limit exceeded");
        }
    }

    void shutdown_all() {
        for (size_t i = children_.size(); i-- > 0; ) {
            stop_child(i);
        }
    }

    bool has_living_children() const {
        return std::any_of(children_.begin(), children_.end(),
                           [](const ChildSpec& c) { return c.is_alive; });
    }

    Strategy strategy_;
    int max_restarts_;
    std::chrono::seconds max_time_;
    std::vector<ChildSpec> children_;
    std::vector<std::chrono::steady_clock::time_point> crash_history_;
};
