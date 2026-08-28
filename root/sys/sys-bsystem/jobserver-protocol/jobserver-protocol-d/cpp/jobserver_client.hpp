// jobserver_client.hpp — Modern C++20/C++23 RAII Client
#pragma once

#include <string>
#include <string_view>
#include <optional>
#include <memory>
#include <cstdlib>
#include <system_error>

#if defined(_WIN32)
#include <windows.h>
#else
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#endif

namespace build_system {

enum class JobserverMode {
    None,
    Pipe,
    Fifo,
    Semaphore
};

class JobserverClient {
public:
    // RAII охоронець для автоматичного повернення токена
    class TokenGuard {
    public:
        TokenGuard(JobserverClient& client, char token, bool is_implicit) noexcept
            : client_(&client), token_(token), is_implicit_(is_implicit) {}

        ~TokenGuard() {
            release();
        }

        TokenGuard(const TokenGuard&) = delete;
        TokenGuard& operator=(const TokenGuard&) = delete;

        TokenGuard(TokenGuard&& other) noexcept
            : client_(other.client_), token_(other.token_), is_implicit_(other.is_implicit_) {
            other.client_ = nullptr;
        }

        TokenGuard& operator=(TokenGuard&& other) noexcept {
            if (this != &other) {
                release();
                client_ = other.client_;
                token_ = other.token_;
                is_implicit_ = other.is_implicit_;
                other.client_ = nullptr;
            }
            return *this;
        }

        void release() noexcept {
            if (client_) {
                client_->release_token(token_, is_implicit_);
                client_ = nullptr;
            }
        }

        [[nodiscard]] char token() const noexcept { return token_; }
        [[nodiscard]] bool is_implicit() const noexcept { return is_implicit_; }

    private:
        JobserverClient* client_{nullptr};
        char token_{'+'};
        bool is_implicit_{false};
    };

    JobserverClient() {
        init_from_env();
    }

    ~JobserverClient() {
        close();
    }

    JobserverClient(const JobserverClient&) = delete;
    JobserverClient& operator=(const JobserverClient&) = delete;

    [[nodiscard]] JobserverMode mode() const noexcept { return mode_; }

    // Спроба захопити токен з поверненням RAII обгортки
    [[nodiscard]] std::optional<TokenGuard> try_acquire() {
        // 1. Неявний власний слот
        if (has_implicit_token_) {
            has_implicit_token_ = false;
            return TokenGuard(*this, '+', true);
        }

        if (mode_ == JobserverMode::None) {
            return std::nullopt;
        }

#if defined(_WIN32)
        if (mode_ == JobserverMode::Semaphore && sem_handle_) {
            DWORD res = WaitForSingleObject(sem_handle_, 0);
            if (res == WAIT_OBJECT_0) {
                return TokenGuard(*this, '+', false);
            }
        }
#else
        if ((mode_ == JobserverMode::Pipe || mode_ == JobserverMode::Fifo) && read_fd_ >= 0) {
            char buf = 0;
            ssize_t n = read(read_fd_, &buf, 1);
            if (n == 1) {
                return TokenGuard(*this, buf, false);
            }
        }
#endif
        return std::nullopt;
    }

private:
    void release_token(char token, bool is_implicit) noexcept {
        if (is_implicit) {
            has_implicit_token_ = true;
            return;
        }

        if (mode_ == JobserverMode::None) {
            return;
        }

#if defined(_WIN32)
        if (mode_ == JobserverMode::Semaphore && sem_handle_) {
            ReleaseSemaphore(sem_handle_, 1, nullptr);
        }
#else
        if ((mode_ == JobserverMode::Pipe || mode_ == JobserverMode::Fifo) && write_fd_ >= 0) {
            while (true) {
                ssize_t written = write(write_fd_, &token, 1);
                if (written < 0 && errno == EINTR) {
                    continue;
                }
                break;
            }
        }
#endif
    }

    void init_from_env() {
        const char* raw_flags = std::getenv("MAKEFLAGS");
        if (!raw_flags) {
            raw_flags = std::getenv("MFLAGS");
        }
        if (!raw_flags) {
            return;
        }

        std::string_view flags(raw_flags);
        auto auth_pos = flags.find("--jobserver-auth=");
        if (auth_pos == std::string_view::npos) {
            auth_pos = flags.find("--jobserver-fds=");
        }
        if (auth_pos == std::string_view::npos) {
            return;
        }

        auto eq_pos = flags.find('=', auth_pos);
        if (eq_pos == std::string_view::npos) {
            return;
        }

        std::string_view val = flags.substr(eq_pos + 1);
        auto end_pos = val.find_first_of(" \t\n");
        if (end_pos != std::string_view::npos) {
            val = val.substr(0, end_pos);
        }

#if defined(_WIN32)
        if (val.starts_with("semaphore:")) {
            val.remove_prefix(10);
        }
        std::string sem_name(val);
        sem_handle_ = OpenSemaphoreA(SYNCHRONIZE | SEMAPHORE_MODIFY_STATE, FALSE, sem_name.c_str());
        if (sem_handle_) {
            mode_ = JobserverMode::Semaphore;
        }
#else
        if (val.starts_with("fifo:")) {
            std::string fifo_path(val.substr(5));
            int fd = open(fifo_path.c_str(), O_RDWR | O_CLOEXEC | O_NONBLOCK);
            if (fd >= 0) {
                read_fd_ = fd;
                write_fd_ = fd;
                mode_ = JobserverMode::Fifo;
            }
        } else {
            int rfd = -1, wfd = -1;
            std::string str_val(val);
            if (sscanf(str_val.c_str(), "%d,%d", &rfd, &wfd) == 2) {
                int fl = fcntl(rfd, F_GETFL, 0);
                if (fl >= 0) {
                    fcntl(rfd, F_SETFL, fl | O_NONBLOCK);
                    read_fd_ = rfd;
                    write_fd_ = wfd;
                    mode_ = JobserverMode::Pipe;
                }
            }
        }
#endif
    }

    void close() noexcept {
#if defined(_WIN32)
        if (sem_handle_) {
            CloseHandle(sem_handle_);
            sem_handle_ = nullptr;
        }
#else
        if (mode_ == JobserverMode::Fifo && read_fd_ >= 0) {
            ::close(read_fd_);
            read_fd_ = -1;
            write_fd_ = -1;
        }
#endif
        mode_ = JobserverMode::None;
    }

    JobserverMode mode_{JobserverMode::None};
    bool has_implicit_token_{true};
#if defined(_WIN32)
    HANDLE sem_handle_{nullptr};
#else
    int read_fd_{-1};
    int write_fd_{-1};
#endif
};

} // namespace build_system
