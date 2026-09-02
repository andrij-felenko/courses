#include "switch_root.hpp"

#include <array>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <format>
#include <print>
#include <utility>

#include <dirent.h>
#include <fcntl.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/vfs.h>
#include <unistd.h>

#ifndef RAMFS_MAGIC
#define RAMFS_MAGIC 0x858458f6
#endif
#ifndef TMPFS_MAGIC
#define TMPFS_MAGIC 0x01021994
#endif

namespace boot {
namespace {

// Дескриптор із власником: жодних close() у гілках виходу.
class Fd {
public:
    explicit Fd(int fd = -1) noexcept : fd_{fd} {}
    Fd(const Fd&) = delete;
    Fd& operator=(const Fd&) = delete;
    Fd(Fd&& other) noexcept : fd_{std::exchange(other.fd_, -1)} {}
    Fd& operator=(Fd&& other) noexcept
    {
        if (this != &other) {
            reset();
            fd_ = std::exchange(other.fd_, -1);
        }
        return *this;
    }
    ~Fd() { reset(); }

    int  get() const noexcept { return fd_; }
    bool valid() const noexcept { return fd_ >= 0; }
    int  release() noexcept { return std::exchange(fd_, -1); }
    void reset() noexcept
    {
        if (fd_ >= 0)
            ::close(fd_);
        fd_ = -1;
    }

private:
    int fd_{-1};
};

// DIR* із власником; поглинає переданий дескриптор.
class DirStream {
public:
    explicit DirStream(Fd fd) : dir_{fd.valid() ? ::fdopendir(fd.get()) : nullptr}
    {
        if (dir_ != nullptr)
            fd.release();  // тепер дескриптор належить DIR*
    }
    DirStream(const DirStream&) = delete;
    DirStream& operator=(const DirStream&) = delete;
    ~DirStream()
    {
        if (dir_ != nullptr)
            ::closedir(dir_);
    }

    DIR* get() const noexcept { return dir_; }

private:
    DIR* dir_{nullptr};
};

SwitchFailure fail(SwitchError code, std::string_view call, std::string_view arg)
{
    return SwitchFailure{code, std::format("{}({}): {}", call, arg, std::strerror(errno))};
}

// Точка монтування: пристрій відрізняється від пристрою батьківського каталогу.
bool is_mount_point(const std::filesystem::path& path)
{
    struct ::stat here{};
    struct ::stat up{};
    if (::stat(path.c_str(), &here) != 0)
        return false;
    if (::stat((path / "..").c_str(), &up) != 0)
        return false;
    return here.st_dev != up.st_dev || here.st_ino == up.st_ino;
}

void purge_dir(int dfd, ::dev_t root_dev)
{
    Fd copy{::dup(dfd)};  // fdopendir з'їдає дескриптор, тож віддаємо копію
    DirStream dir{std::move(copy)};
    if (dir.get() == nullptr) {
        std::println(stderr, "switch_root: fdopendir: {}", std::strerror(errno));
        return;
    }

    while (const ::dirent* entry = ::readdir(dir.get())) {
        const std::string_view name{entry->d_name};
        if (name == "." || name == "..")
            continue;

        struct ::stat sb{};
        if (::fstatat(dfd, entry->d_name, &sb, AT_SYMLINK_NOFOLLOW) != 0)
            continue;
        if (sb.st_dev != root_dev)
            continue;  // чужа ФС: новий корінь і перенесені псевдо-ФС недоторканні

        const bool is_dir = S_ISDIR(sb.st_mode);
        if (is_dir) {
            Fd sub{::openat(dfd, entry->d_name,
                            O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC)};
            if (sub.valid())
                purge_dir(sub.get(), root_dev);
            else
                std::println(stderr, "switch_root: openat({}): {}", name, std::strerror(errno));
        }

        if (::unlinkat(dfd, entry->d_name, is_dir ? AT_REMOVEDIR : 0) != 0 && errno != ENOENT)
            std::println(stderr, "switch_root: {}({}): {}", is_dir ? "rmdir" : "unlink", name,
                         std::strerror(errno));
    }
}

constexpr std::array<std::string_view, 4> kPseudoMounts{"/dev", "/proc", "/sys", "/run"};

}  // namespace

std::string SwitchFailure::message() const
{
    std::string_view what = "невідома помилка";
    switch (code) {
    case SwitchError::NotMountPoint: what = "новий корінь не є точкою монтування"; break;
    case SwitchError::NoInit:        what = "у новому корені немає виконуваного init"; break;
    case SwitchError::NotRamfs:      what = "поточний корінь не ramfs/tmpfs"; break;
    case SwitchError::OpenRoot:      what = "не вдалося відкрити старий корінь"; break;
    case SwitchError::MoveFailed:    what = "MS_MOVE не вдався"; break;
    case SwitchError::Chdir:         what = "chdir не вдався"; break;
    case SwitchError::Chroot:        what = "chroot не вдався"; break;
    case SwitchError::Exec:          what = "exec не вдався"; break;
    }
    return detail.empty() ? std::string{what} : std::format("{}: {}", what, detail);
}

Result<void> SwitchRoot::verify(const std::filesystem::path& init_path) const
{
    if (!is_mount_point(new_root_))
        return std::unexpected{SwitchFailure{SwitchError::NotMountPoint, new_root_.string()}};

    const auto full = new_root_ / init_path.relative_path();
    if (::access(full.c_str(), X_OK) != 0)
        return std::unexpected{fail(SwitchError::NoInit, "access", full.string())};

    return {};
}

Result<void> SwitchRoot::move_pseudo_mounts() const
{
    for (const auto source : kPseudoMounts) {
        const std::filesystem::path src{source};
        if (!is_mount_point(src)) {
            // /run в аскетичному initramfs може й не бути змонтованим.
            std::println(stderr, "switch_root: {} не змонтовано, пропускаємо", source);
            continue;
        }

        const auto target = new_root_ / src.relative_path();
        std::error_code ec;
        std::filesystem::create_directories(target, ec);  // мовчки, якщо вже є

        if (::mount(src.c_str(), target.c_str(), nullptr, MS_MOVE, nullptr) != 0) {
            auto failure = fail(SwitchError::MoveFailed, "mount MS_MOVE", source);
            if (source == "/run") {
                std::println(stderr, "switch_root: {}", failure.message());
                continue;  // без /run систему ще можна підняти
            }
            return std::unexpected{std::move(failure)};
        }
    }
    return {};
}

Result<void> SwitchRoot::purge_old_root() const
{
    Fd root{::open("/", O_RDONLY | O_DIRECTORY | O_CLOEXEC)};
    if (!root.valid())
        return std::unexpected{fail(SwitchError::OpenRoot, "open", "/")};

    struct ::statfs sfs{};
    if (::fstatfs(root.get(), &sfs) != 0)
        return std::unexpected{fail(SwitchError::OpenRoot, "fstatfs", "/")};

    // Запобіжник: чистити можна лише файлову систему в пам'яті.
    if (sfs.f_type != static_cast<decltype(sfs.f_type)>(RAMFS_MAGIC) &&
        sfs.f_type != static_cast<decltype(sfs.f_type)>(TMPFS_MAGIC))
        return std::unexpected{SwitchFailure{SwitchError::NotRamfs, "тип ФС кореня не в пам'яті"}};

    struct ::stat sb{};
    if (::fstat(root.get(), &sb) != 0)
        return std::unexpected{fail(SwitchError::OpenRoot, "fstat", "/")};

    purge_dir(root.get(), sb.st_dev);
    return {};
}

Result<void> SwitchRoot::pivot() const
{
    if (::chdir(new_root_.c_str()) != 0)
        return std::unexpected{fail(SwitchError::Chdir, "chdir", new_root_.string())};
    // Атомарний крок: змонтований диск стає коренем системи.
    if (::mount(".", "/", nullptr, MS_MOVE, nullptr) != 0)
        return std::unexpected{fail(SwitchError::MoveFailed, "mount MS_MOVE", "/")};
    if (::chroot(".") != 0)
        return std::unexpected{fail(SwitchError::Chroot, "chroot", ".")};
    if (::chdir("/") != 0)
        return std::unexpected{fail(SwitchError::Chdir, "chdir", "/")};
    return {};
}

Result<void> SwitchRoot::run(const std::filesystem::path& init_path,
                             std::span<const std::string> args) const
{
    if (auto ok = verify(init_path); !ok)
        return ok;
    if (auto ok = move_pseudo_mounts(); !ok)
        return ok;

    if (auto ok = purge_old_root(); !ok) {
        if (ok.error().code != SwitchError::NotRamfs)
            return ok;
        // Не фатально: не звільнимо пам'ять, зате нічого не зіпсуємо.
        std::println(stderr, "switch_root: {} — пропускаємо очищення", ok.error().message());
    }

    if (auto ok = pivot(); !ok)
        return ok;

    std::vector<char*> raw;
    raw.reserve(args.size() + 2);
    std::string init_str = init_path.string();
    raw.push_back(init_str.data());
    for (const auto& arg : args)
        raw.push_back(const_cast<char*>(arg.c_str()));
    raw.push_back(nullptr);

    ::execv(init_str.c_str(), raw.data());

    // Керування повернулося — образ не замінився, PID 1 лишився нашим.
    return std::unexpected{fail(SwitchError::Exec, "execv", init_str)};
}

}  // namespace boot
