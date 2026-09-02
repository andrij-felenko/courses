// Ексклюзивний замок завдання: захист від накладання двох запусків.
#pragma once

#include "posix.hpp"

#include <filesystem>
#include <optional>

namespace minicron {

class JobLock {
public:
    // std::nullopt — попередній запуск ще працює; системна помилка — виняток.
    static std::optional<JobLock> try_acquire(const std::filesystem::path& path);

    JobLock(JobLock&&) noexcept = default;
    JobLock& operator=(JobLock&&) noexcept = default;
    JobLock(const JobLock&) = delete;
    JobLock& operator=(const JobLock&) = delete;
    // Деструктора не пишемо: замок знімається закриттям дескриптора, а це
    // робить UniqueFd — зокрема й тоді, коли розкручується стек винятку.
    ~JobLock() = default;

    [[nodiscard]] const std::filesystem::path& path() const noexcept { return path_; }

private:
    JobLock(UniqueFd fd, std::filesystem::path path)
        : fd_(std::move(fd)), path_(std::move(path)) {}

    UniqueFd fd_;
    std::filesystem::path path_;
};

}  // namespace minicron
