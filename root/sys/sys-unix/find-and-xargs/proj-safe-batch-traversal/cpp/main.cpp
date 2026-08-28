#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <filesystem>
#include <memory>
#include <span>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

namespace fs = std::filesystem;

class WorkerPool {
public:
    explicit WorkerPool(std::size_t max_workers) : max_workers_(max_workers) {}

    ~WorkerPool() {
        wait_all();
    }

    void spawn(const std::string& command, const std::vector<std::string>& batch) {
        if (batch.empty()) return;

        while (active_workers_ >= max_workers_) {
            reap_one(true);
        }

        std::vector<char*> raw_args;
        raw_args.reserve(batch.size() + 2);
        raw_args.push_back(const_cast<char*>(command.c_str()));
        for (const auto& arg : batch) {
            raw_args.push_back(const_cast<char*>(arg.c_str()));
        }
        raw_args.push_back(nullptr);

        pid_t pid = fork();
        if (pid == 0) {
            ::execvp(raw_args[0], raw_args.data());
            ::_exit(127);
        } else if (pid > 0) {
            ++active_workers_;
            reap_nonblocking();
        } else {
            throw std::system_error(errno, std::generic_category(), "fork failed");
        }
    }

    void wait_all() {
        while (active_workers_ > 0) {
            reap_one(true);
        }
    }

private:
    std::size_t max_workers_;
    std::size_t active_workers_{0};

    void reap_nonblocking() {
        while (active_workers_ > 0) {
            int status = 0;
            pid_t pid = ::waitpid(-1, &status, WNOHANG);
            if (pid > 0) {
                --active_workers_;
            } else {
                break;
            }
        }
    }

    void reap_one(bool blocking) {
        int status = 0;
        int flags = blocking ? 0 : WNOHANG;
        pid_t pid = ::waitpid(-1, &status, flags);
        if (pid > 0) {
            --active_workers_;
        }
    }
};

void process_tree(const fs::path& root, const std::string& command, std::size_t batch_size) {
    WorkerPool pool(4);
    std::vector<std::string> current_batch;
    current_batch.reserve(batch_size);

    std::error_code ec;
    auto iter = fs::recursive_directory_iterator(root, fs::directory_options::skip_permission_denied, ec);
    auto end_iter = fs::recursive_directory_iterator();

    for (; iter != end_iter && !ec; iter.increment(ec)) {
        if (ec) {
            ec.clear();
            continue;
        }

        const auto& entry = *iter;
        if (entry.is_regular_file(ec) && entry.path().extension() == ".log") {
            current_batch.push_back(entry.path().string());
            if (current_batch.size() >= batch_size) {
                pool.spawn(command, current_batch);
                current_batch.clear();
            }
        }
    }

    if (!current_batch.empty()) {
        pool.spawn(command, current_batch);
    }
}

int main(int argc, char* argv[]) {
    try {
        fs::path target_dir = (argc > 1) ? argv[1] : ".";
        process_tree(target_dir, "gzip", 64);
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
