#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <system_error>
#include <filesystem>
#include <span>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/sysmacros.h>
#include <sys/xattr.h>
#include <linux/fs.h>

namespace fs = std::filesystem;

class ScopedFd {
public:
    explicit ScopedFd(int fd = -1) noexcept : m_fd(fd) {}
    ~ScopedFd() { reset(); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            reset(other.m_fd);
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
        m_fd = new_fd;
    }

private:
    int m_fd;
};

class VfsCloner {
public:
    static constexpr size_t BufferSize = 65536;

    static void copySparseData(int src_fd, int dst_fd, off_t total_size) {
        off_t offset = 0;
        std::vector<char> buffer(BufferSize);

        while (offset < total_size) {
            off_t data_start = ::lseek(src_fd, offset, SEEK_DATA);
            if (data_start == -1) {
                if (errno == ENXIO) break; // Більше немає даних
                throw std::system_error(errno, std::generic_category(), "lseek SEEK_DATA failed");
            }

            off_t hole_start = ::lseek(src_fd, data_start, SEEK_HOLE);
            if (hole_start == -1) {
                hole_start = total_size;
            }

            if (::lseek(dst_fd, data_start, SEEK_SET) == -1) {
                throw std::system_error(errno, std::generic_category(), "lseek dst SEEK_SET failed");
            }

            off_t remaining = hole_start - data_start;
            ::lseek(src_fd, data_start, SEEK_SET);

            while (remaining > 0) {
                size_t to_read = std::min(static_cast<size_t>(remaining), BufferSize);
                ssize_t n_read = ::read(src_fd, buffer.data(), to_read);
                if (n_read <= 0) {
                    if (n_read < 0 && errno == EINTR) continue;
                    throw std::system_error(errno, std::generic_category(), "read failed");
                }

                ssize_t written = 0;
                while (written < n_read) {
                    ssize_t n_write = ::write(dst_fd, buffer.data() + written, n_read - written);
                    if (n_write <= 0) {
                        if (n_write < 0 && errno == EINTR) continue;
                        throw std::system_error(errno, std::generic_category(), "write failed");
                    }
                    written += n_write;
                }
                remaining -= n_read;
            }
            offset = hole_start;
        }

        if (::ftruncate(dst_fd, total_size) == -1) {
            throw std::system_error(errno, std::generic_category(), "ftruncate failed");
        }
    }

    static void copyXattrs(const std::string& src_path, const std::string& dst_path) {
        ssize_t list_len = ::llistxattr(src_path.c_str(), nullptr, 0);
        if (list_len <= 0) {
            if (list_len == 0 || errno == ENOTSUP || errno == ENODATA) return;
            throw std::system_error(errno, std::generic_category(), "llistxattr failed");
        }

        std::vector<char> list_buf(list_len);
        list_len = ::llistxattr(src_path.c_str(), list_buf.data(), list_buf.size());
        if (list_len < 0) {
            throw std::system_error(errno, std::generic_category(), "llistxattr read failed");
        }

        const char* current_attr = list_buf.data();
        while (current_attr < list_buf.data() + list_len) {
            ssize_t val_len = ::lgetxattr(src_path.c_str(), current_attr, nullptr, 0);
            if (val_len > 0) {
                std::vector<char> val_buf(val_len);
                if (::lgetxattr(src_path.c_str(), current_attr, val_buf.data(), val_buf.size()) == val_len) {
                    ::lsetxattr(dst_path.c_str(), current_attr, val_buf.data(), val_buf.size(), 0);
                }
            } else if (val_len == 0) {
                ::lsetxattr(dst_path.c_str(), current_attr, "", 0, 0);
            }
            current_attr += std::strlen(current_attr) + 1;
        }
    }

    static void cloneNode(const std::string& src_path, const std::string& dst_path) {
        struct statx stx{};
        unsigned int mask = STATX_TYPE | STATX_MODE | STATX_UID | STATX_GID |
                            STATX_ATIME | STATX_MTIME | STATX_SIZE;

        if (::statx(AT_FDCWD, src_path.c_str(), AT_SYMLINK_NOFOLLOW, mask, &stx) != 0) {
            throw std::system_error(errno, std::generic_category(), "statx failed for " + src_path);
        }

        mode_t type = stx.stx_mode & S_IFMT;

        if (S_ISREG(type)) {
            ScopedFd src_fd(::open(src_path.c_str(), O_RDONLY | O_NOFOLLOW));
            if (!src_fd.valid()) {
                throw std::system_error(errno, std::generic_category(), "open src failed: " + src_path);
            }

            ScopedFd dst_fd(::open(dst_path.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0600));
            if (!dst_fd.valid()) {
                throw std::system_error(errno, std::generic_category(), "open dst failed: " + dst_path);
            }

            loff_t in_off = 0, out_off = 0;
            ssize_t reflink_res = ::copy_file_range(src_fd.get(), &in_off, dst_fd.get(), &out_off, stx.stx_size, 0);
            if (reflink_res < 0 || static_cast<size_t>(reflink_res) < stx.stx_size) {
                ::lseek(src_fd.get(), 0, SEEK_SET);
                ::lseek(dst_fd.get(), 0, SEEK_SET);
                copySparseData(src_fd.get(), dst_fd.get(), stx.stx_size);
            }
        } else if (S_ISDIR(type)) {
            if (::mkdir(dst_path.c_str(), 0700) != 0 && errno != EEXIST) {
                throw std::system_error(errno, std::generic_category(), "mkdir failed: " + dst_path);
            }
        } else if (S_ISLNK(type)) {
            std::vector<char> link_target(PATH_MAX);
            ssize_t len = ::readlink(src_path.c_str(), link_target.data(), link_target.size() - 1);
            if (len < 0) {
                throw std::system_error(errno, std::generic_category(), "readlink failed: " + src_path);
            }
            link_target[len] = '\0';

            if (::symlink(link_target.data(), dst_path.c_str()) != 0) {
                throw std::system_error(errno, std::generic_category(), "symlink failed: " + dst_path);
            }
        } else if (S_ISFIFO(type)) {
            if (::mkfifo(dst_path.c_str(), 0600) != 0) {
                throw std::system_error(errno, std::generic_category(), "mkfifo failed: " + dst_path);
            }
        } else if (S_ISCHR(type) || S_ISBLK(type)) {
            dev_t dev = makedev(stx.stx_rdev_major, stx.stx_rdev_minor);
            if (::mknod(dst_path.c_str(), type | 0600, dev) != 0) {
                throw std::system_error(errno, std::generic_category(), "mknod failed: " + dst_path);
            }
        }

        // Копіювання xattr, ACL та контекстів безпеки
        copyXattrs(src_path, dst_path);

        // Відновлення власника
        ::fchownat(AT_FDCWD, dst_path.c_str(), stx.stx_uid, stx.stx_gid, AT_SYMLINK_NOFOLLOW);

        // Відновлення прав
        if (!S_ISLNK(type)) {
            ::fchmodat(AT_FDCWD, dst_path.c_str(), stx.stx_mode & 07777, 0);
        }

        // Відновлення міток часу
        struct timespec times[2]{};
        times[0].tv_sec = stx.stx_atime.tv_sec;
        times[0].tv_nsec = stx.stx_atime.tv_nsec;
        times[1].tv_sec = stx.stx_mtime.tv_sec;
        times[1].tv_nsec = stx.stx_mtime.tv_nsec;

        ::utimensat(AT_FDCWD, dst_path.c_str(), times, AT_SYMLINK_NOFOLLOW);
    }
};
