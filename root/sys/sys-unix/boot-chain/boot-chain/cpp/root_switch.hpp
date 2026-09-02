#pragma once

#include <cstddef>
#include <filesystem>
#include <span>

#include <sys/types.h>

namespace boot {

// Один прохід переходу з initramfs на справжній корінь.
//
// Кожен відкритий метод — це крок фази 5, і викликати їх треба саме в тому
// порядку, у якому вони оголошені. Там, де відкотитися вже неможливо, методи
// кидають std::system_error або std::runtime_error; там, де чистка лише
// "за можливості", — повертають кількість невдач.
class RootSwitch {
public:
    explicit RootSwitch(std::filesystem::path new_root);

    // PID 1, стара rootfs у пам'яті, новий корінь — окрема ФС, init запускний.
    void verify(const std::filesystem::path& init) const;

    // Знімає з дерева монтувань спільне поширення: MS_MOVE його не терпить.
    void make_mount_tree_private() const;

    // /dev, /proc, /sys, /run → MS_MOVE у новий корінь.
    std::size_t move_special_mounts() const;

    // Поточний каталог має пережити стирання старої ФС.
    void chdir_to_new_root() const;

    // Рекурсивне стирання того, що лишилося на старому пристрої.
    std::size_t wipe_old_root() const;

    // mount(".", "/", MS_MOVE) + chroot(".") + chdir("/").
    void pivot() const;

    // /dev/console нового кореня на дескрипторах 0, 1, 2.
    void reopen_console() const;

    // execve без fork: номер процесу лишається той самий.
    [[noreturn]] void exec_init(std::span<char* const> init_argv) const;

private:
    std::filesystem::path new_root_;
    dev_t old_root_dev_;
};

}  // namespace boot
