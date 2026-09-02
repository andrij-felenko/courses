// switch_root: перенесення псевдо-ФС, знищення rootfs, атомарна заміна кореня
// й exec справжнього init. Кожен крок повертає std::expected з поясненням.
#pragma once

#include <expected>
#include <filesystem>
#include <span>
#include <string>
#include <string_view>
#include <vector>

namespace boot {

enum class SwitchError {
    NotMountPoint,  // новий корінь не є точкою монтування
    NoInit,         // у новому корені немає виконуваного init
    NotRamfs,       // поточний "/" не ramfs/tmpfs — чистити не можна
    OpenRoot,       // не відкрився старий корінь
    MoveFailed,     // MS_MOVE не вдався
    Chdir,
    Chroot,
    Exec
};

struct SwitchFailure {
    SwitchError code{};
    std::string detail;  // назва виклику й текст errno

    std::string message() const;
};

template <class T>
using Result = std::expected<T, SwitchFailure>;

class SwitchRoot {
public:
    explicit SwitchRoot(std::filesystem::path new_root) : new_root_{std::move(new_root)} {}

    // 1. Новий корінь — окреме монтування, всередині є виконуваний init.
    Result<void> verify(const std::filesystem::path& init_path) const;
    // 2. MS_MOVE для /dev, /proc, /sys, /run у новий корінь.
    Result<void> move_pseudo_mounts() const;
    // 3. Деструктивний обхід rootfs: усе, що на тій самій ФС, іде геть.
    Result<void> purge_old_root() const;
    // 4. chdir + MS_MOVE(".", "/") + chroot(".") + chdir("/").
    Result<void> pivot() const;
    // 1–5 разом; за успіху не повертається — процес уже виконує новий init.
    Result<void> run(const std::filesystem::path& init_path,
                     std::span<const std::string> args) const;

private:
    std::filesystem::path new_root_;
};

}  // namespace boot
