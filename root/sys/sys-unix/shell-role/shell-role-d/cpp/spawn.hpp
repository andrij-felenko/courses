// Запуск ланки конвеєра через posix_spawn(3).
#pragma once

#include <unistd.h>

#include <span>
#include <string>
#include <vector>

struct StageIo {
    int in_fd = STDIN_FILENO;
    int out_fd = STDOUT_FILENO;
    std::span<const int> close_fds{};
    ::pid_t pgid = 0;              // 0 — нащадок стає лідером власної групи
};

// Кидає std::system_error; повертає PID нащадка.
::pid_t spawn_stage(const std::string& path,
                    std::span<const std::string> args,
                    const StageIo& io);
