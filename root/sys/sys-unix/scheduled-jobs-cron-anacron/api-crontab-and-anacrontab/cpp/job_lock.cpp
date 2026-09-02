#include "job_lock.hpp"

#include <cerrno>
#include <format>
#include <iostream>
#include <string>

#include <fcntl.h>
#include <sys/file.h>
#include <unistd.h>

namespace minicron {

std::optional<JobLock> JobLock::try_acquire(const std::filesystem::path& path)
{
    // O_CLOEXEC: замок належить нашому процесові, а не команді, яку ми
    // запустимо через exec, — інакше він жив би, доки живе будь-який нащадок.
    UniqueFd fd{::open(path.c_str(), O_RDWR | O_CREAT | O_CLOEXEC, 0600)};
    if (!fd.valid()) {
        throw_errno(std::format("open {}", path.string()));
    }

    // LOCK_NB: не чекаємо в черзі. Чекати тут означало б назбирати за ніч
    // десяток процесів, які прокинуться разом і поб'ються за диск.
    if (::flock(fd.get(), LOCK_EX | LOCK_NB) != 0) {
        if (errno == EWOULDBLOCK) {
            return std::nullopt;
        }
        throw_errno(std::format("flock {}", path.string()));
    }

    // Вміст файлу на замок не впливає — це підказка адміністраторові, який
    // побачить файл у /var/lock і захоче знати, хто його тримає.
    const std::string pid_line = std::format("{}\n", ::getpid());
    if (::ftruncate(fd.get(), 0) != 0 ||
        ::write(fd.get(), pid_line.data(), pid_line.size()) < 0) {
        std::cerr << std::format("minicron: не вдалося записати PID у {}\n", path.string());
    }

    return JobLock{std::move(fd), path};
}

}  // namespace minicron
