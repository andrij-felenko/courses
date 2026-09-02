#include "root_switch.hpp"

#include "mount_ops.hpp"
#include "posix.hpp"
#include "wipe.hpp"

#include <cerrno>
#include <stdexcept>
#include <string>
#include <vector>

#include <linux/magic.h>
#include <sys/mount.h>
#include <sys/vfs.h>

namespace fs = std::filesystem;

namespace {

bool lives_in_memory(const fs::path& path)
{
    struct ::statfs sb {};
    if (::statfs(path.c_str(), &sb) != 0)
        boot::fail("statfs " + path.string());

    const auto magic = static_cast<unsigned long>(sb.f_type);
    return magic == RAMFS_MAGIC || magic == TMPFS_MAGIC;
}

}  // namespace

namespace boot {

RootSwitch::RootSwitch(fs::path new_root)
    : new_root_(std::move(new_root)), old_root_dev_(lstat_of("/").st_dev)
{
}

void RootSwitch::verify(const fs::path& init) const
{
    if (::getpid() != 1)
        throw std::runtime_error("мусить виконуватися процесом PID 1, а не "
                                 + std::to_string(::getpid()));

    // Порожній шлях і "/" зробили б із наступних кроків стирання живої
    // системи замість переходу.
    if (new_root_.empty() || new_root_ == "/")
        throw std::runtime_error("новий корінь \"" + new_root_.string()
                                 + "\" не має сенсу");

    // Якщо старий корінь раптом на носії, крок стирання зніс би диск.
    if (!lives_in_memory("/"))
        throw std::runtime_error("поточний корінь не ramfs і не tmpfs — "
                                 "стирати його не можна");

    std::error_code ec;
    if (!fs::is_directory(new_root_, ec))
        throw std::runtime_error(new_root_.string() + " не є каталогом");

    // Однаковий номер пристрою означає, що /sysroot — просто порожній каталог
    // у пам'яті: сховище не зібралося, і переходити нікуди.
    if (lstat_of(new_root_).st_dev == old_root_dev_)
        throw std::runtime_error(new_root_.string()
                                 + " лежить на тій самій ФС, що й старий корінь"
                                   " — справжнє сховище не змонтоване");

    // relative_path() зрізає провідний '/': шлях потрібен від нового кореня.
    const fs::path init_path = new_root_ / init.relative_path();
    if (::access(init_path.c_str(), X_OK) != 0)
        fail("не запускається " + init_path.string());
}

void RootSwitch::make_mount_tree_private() const
{
    mounts::make_tree_private();
}

std::size_t RootSwitch::move_special_mounts() const
{
    return mounts::move_special(new_root_);
}

void RootSwitch::chdir_to_new_root() const
{
    checked(::chdir(new_root_.c_str()), "chdir " + new_root_.string());
}

std::size_t RootSwitch::wipe_old_root() const
{
    // Дескриптор старого кореня беремо ДО chroot: після нього шляху туди вже
    // не буде, а chdir_to_new_root() нас звідти щойно вивів.
    const UniqueFd old_root = open_dir(AT_FDCWD, "/");
    if (!old_root)
        fail("open /");

    return wipe::filesystem(old_root);
}

void RootSwitch::pivot() const
{
    // pivot_root() тут повернув би EINVAL: rootfs є первинним коренем
    // простору імен монтувань, тому підміняємо сам кореневий вузол.
    checked(::mount(".", "/", nullptr, MS_MOVE, nullptr), "mount --move . /");
    checked(::chroot("."), "chroot .");
    checked(::chdir("/"), "chdir /");
}

void RootSwitch::reopen_console() const
{
    // Дескриптори 0, 1, 2 процес дістав від ядра ще у фазі 3 і вказують вони
    // на консоль старої rootfs. Після підміни кореня відкриваємо консоль
    // заново — вже з нового дерева. Крок необов'язковий: не вийшло, значить
    // лишаються успадковані.
    // O_NOCTTY: керівним терміналом консоль зробить системний менеджер.
    UniqueFd console(::open("/dev/console", O_RDWR | O_NOCTTY));
    if (!console) {
        const int err = errno;
        warn("open /dev/console (лишаю успадковані 0, 1, 2)", err);
        return;
    }

    for (const int target : {STDIN_FILENO, STDOUT_FILENO, STDERR_FILENO}) {
        // dup2 сам закриває ціль, а dup2(fd, fd) — тотожність, не помилка.
        if (::dup2(console.get(), target) < 0) {
            const int err = errno;
            warn("dup2 /dev/console", err);
        }
    }

    // Якщо котрийсь зі стандартних дескрипторів був закритий, open міг сісти
    // просто на нього — тоді закривати нічого, ним володіє вже сам процес.
    if (console.get() <= STDERR_FILENO)
        static_cast<void>(console.release());
}

void RootSwitch::exec_init(std::span<char* const> init_argv) const
{
    std::vector<char*> argv(init_argv.begin(), init_argv.end());
    argv.push_back(nullptr);

    // Ні fork, ні posix_spawn: код процесу заміщується на місці, номер 1
    // лишається за ним, а дескриптори 0, 1, 2 переживають execve
    // і дістаються системному менеджеру вже відкритими.
    ::execv(argv.front(), argv.data());
    fail(std::string("execv ") + argv.front());
}

}  // namespace boot
