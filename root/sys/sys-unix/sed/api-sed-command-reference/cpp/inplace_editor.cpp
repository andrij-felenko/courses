#include "inplace_editor.hpp"

#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#if defined(__linux__)
#include <sys/xattr.h>
#endif
#if defined(SED_WITH_SELINUX)
#include <selinux/selinux.h>
#endif

#include <cerrno>
#include <cstring>
#include <utility>
#include <vector>

namespace minised {
namespace {

std::error_code last_error() { return {errno, std::generic_category()}; }

// Дескриптор із власником: жодних close() у гілках виходу.
class ScopedFd {
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_{fd} {}
    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;
    ~ScopedFd() { if (fd_ >= 0) ::close(fd_); }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    std::error_code close_now() noexcept {
        if (fd_ < 0) return {};
        return (::close(std::exchange(fd_, -1)) == 0) ? std::error_code{} : last_error();
    }
private:
    int fd_;
};

// Тимчасовий файл зникає сам, доки коміт не звільнить його через release().
class TempFile {
public:
    TempFile(int fd, std::string path) noexcept : fd_{fd}, path_{std::move(path)} {}
    TempFile(const TempFile&) = delete;
    TempFile& operator=(const TempFile&) = delete;
    ~TempFile() { if (!released_) ::unlink(path_.c_str()); }
    ScopedFd& fd() noexcept { return fd_; }
    [[nodiscard]] const std::string& path() const noexcept { return path_; }
    void release() noexcept { released_ = true; }
private:
    ScopedFd fd_;
    std::string path_;
    bool released_{false};
};

std::error_code write_all(int fd, std::string_view data) {
    while (!data.empty()) {
        const ssize_t n = ::write(fd, data.data(), data.size());
        if (n < 0) {
            if (errno == EINTR) continue;
            return last_error();
        }
        data.remove_prefix(static_cast<std::size_t>(n));
    }
    return {};
}

#if defined(__linux__)
void copy_xattrs(int src_fd, int dst_fd) {
    const ssize_t names_len = ::flistxattr(src_fd, nullptr, 0);
    if (names_len <= 0) return;
    std::vector<char> names(static_cast<std::size_t>(names_len));
    if (::flistxattr(src_fd, names.data(), names.size()) != names_len) return;

    for (const char* n = names.data(); n < names.data() + names.size(); n += std::strlen(n) + 1) {
        const ssize_t vlen = ::fgetxattr(src_fd, n, nullptr, 0);
        if (vlen < 0) continue;
        std::vector<char> value(static_cast<std::size_t>(vlen));
        if (::fgetxattr(src_fd, n, value.data(), value.size()) == vlen)
            ::fsetxattr(dst_fd, n, value.data(), value.size(), 0);   // user.* і POSIX ACL
    }
}
#endif

void copy_metadata(int src_fd, int dst_fd, const struct stat& st) {
    // mkstemp дає 0600 — без fchmod результат втратив би права оригіналу.
    ::fchmod(dst_fd, st.st_mode & 07777);
    // Власник — «за можливості»: без CAP_CHOWN буде EPERM, і це не аварія.
    ::fchown(dst_fd, st.st_uid, st.st_gid);
#if defined(__linux__)
    copy_xattrs(src_fd, dst_fd);
#else
    (void)src_fd;
#endif
#if defined(SED_WITH_SELINUX)
    // Новий inode дістав би тип за правилом переходу каталогу (etc_t замість
    // shadow_t), тому мітку переносимо явно — до rename().
    char* ctx = nullptr;
    if (::fgetfilecon(src_fd, &ctx) >= 0) {
        ::fsetfilecon(dst_fd, ctx);
        ::freecon(ctx);
    }
#endif
}

}  // namespace

std::expected<void, std::error_code> InPlaceEditor::commit(
        const std::filesystem::path& target_in, std::string_view content,
        const Options& opts) {
    std::filesystem::path target = target_in;
    if (opts.follow_symlinks) {
        std::error_code ec;
        auto real = std::filesystem::canonical(target, ec);   // саме посилання лишається цілим
        if (!ec) target = real;
    }

    ScopedFd src{::open(target.c_str(), O_RDONLY)};
    if (!src.valid()) return std::unexpected(last_error());
    struct stat st{};
    if (::fstat(src.get(), &st) != 0) return std::unexpected(last_error());
    if (!S_ISREG(st.st_mode))
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));

    // Тимчасовий файл ЗАВЖДИ в каталозі цілі: rename() не ходить між точками
    // монтування, а з /tmp упав би з EXDEV.
    std::string pattern = target.parent_path().empty()
            ? std::string{"sedXXXXXX"}
            : (target.parent_path() / "sedXXXXXX").string();
    TempFile tmp{::mkstemp(pattern.data()), pattern};
    if (!tmp.fd().valid()) return std::unexpected(last_error());

    copy_metadata(src.get(), tmp.fd().get(), st);
    if (auto ec = write_all(tmp.fd().get(), content)) return std::unexpected(ec);
    if (::fsync(tmp.fd().get()) != 0) return std::unexpected(last_error());  // дані до підміни імені
    if (auto ec = tmp.fd().close_now()) return std::unexpected(ec);

    if (opts.backup_suffix) {
        const std::string backup = target.string() + *opts.backup_suffix;
        ::unlink(backup.c_str());
        // Жорстке посилання лишає старий inode на місці; де це неможливо —
        // падаємо на перейменування, як робить BSD sed.
        if (::link(target.c_str(), backup.c_str()) != 0 &&
            ::rename(target.c_str(), backup.c_str()) != 0)
            return std::unexpected(last_error());
    }

    // Атомарна підміна dentry. Старий inode живий, поки його тримають чужі
    // дескриптори — саме тому tail -f після sed -i більше нічого не бачить.
    if (::rename(tmp.path().c_str(), target.c_str()) != 0)
        return std::unexpected(last_error());
    tmp.release();
    return {};
}

}  // namespace minised
