// cpp
#include <iostream>
#include <string>
#include <string_view>
#include <system_error>
#include <memory>
#include <filesystem>
#include <algorithm>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/btrfs.h>
#include <linux/fs.h>

namespace fs = std::filesystem;

// Ідіоматична RAII-обгортка для безпечного управління файловими дескрипторами
class FileDescriptor {
    int fd_{-1};
public:
    explicit FileDescriptor(int fd) : fd_(fd) {}
    ~FileDescriptor() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& rhs) noexcept : fd_(rhs.fd_) {
        rhs.fd_ = -1;
    }

    FileDescriptor& operator=(FileDescriptor&& rhs) noexcept {
        if (this != &rhs) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = rhs.fd_;
            rhs.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

class BtrfsManager {
public:
    static void create_subvolume(const fs::path& parent_dir, std::string_view subvol_name) {
        FileDescriptor dir_fd(::open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY));
        if (!dir_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити батьківську директорію");
        }

        struct btrfs_ioctl_vol_args args{};
        const size_t copy_len = std::min(subvol_name.size(), static_cast<size_t>(BTRFS_PATH_NAME_MAX));
        std::copy_n(subvol_name.begin(), copy_len, args.name);
        args.name[copy_len] = '\0';

        if (::ioctl(dir_fd.get(), BTRFS_IOC_SUBVOL_CREATE, &args) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl(BTRFS_IOC_SUBVOL_CREATE)");
        }

        std::cout << "[+] Субтом '" << subvol_name << "' успішно створено в '" << parent_dir.string() << "'\n";
    }

    static void create_readonly_snapshot(const fs::path& src_subvol, const fs::path& parent_dir, std::string_view snap_name) {
        FileDescriptor src_fd(::open(src_subvol.c_str(), O_RDONLY | O_DIRECTORY));
        if (!src_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити джерельний субтом");
        }

        FileDescriptor parent_fd(::open(parent_dir.c_str(), O_RDONLY | O_DIRECTORY));
        if (!parent_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити батьківську директорію");
        }

        struct btrfs_ioctl_vol_args_v2 args2{};
        args2.fd = src_fd.get();
        args2.flags = BTRFS_SUBVOL_RDONLY;
        const size_t copy_len = std::min(snap_name.size(), static_cast<size_t>(BTRFS_SUBVOL_NAME_MAX));
        std::copy_n(snap_name.begin(), copy_len, args2.name);
        args2.name[copy_len] = '\0';

        if (::ioctl(parent_fd.get(), BTRFS_IOC_SNAP_CREATE_V2, &args2) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl(BTRFS_IOC_SNAP_CREATE_V2)");
        }

        std::cout << "[+] Read-Only знімок '" << snap_name << "' успішно створено\n";
    }

    static void reflink_clone_file(const fs::path& src_path, const fs::path& dst_path) {
        FileDescriptor src_fd(::open(src_path.c_str(), O_RDONLY));
        if (!src_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити джерельний файл");
        }

        FileDescriptor dst_fd(::open(dst_path.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0644));
        if (!dst_fd.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося створити цільовий файл");
        }

        if (::ioctl(dst_fd.get(), FICLONE, src_fd.get()) < 0) {
            fs::remove(dst_path);
            throw std::system_error(errno, std::generic_category(), "Помилка ioctl(FICLONE)");
        }

        std::cout << "[+] Файл '" << src_path.string() << "' клоновано через FICLONE у '" << dst_path.string() << "'\n";
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <точка_монтування_btrfs>\n";
        return EXIT_FAILURE;
    }

    try {
        const fs::path mnt = argv[1];
        const fs::path subvol_path = mnt / "subvol_demo";

        BtrfsManager::create_subvolume(mnt, "subvol_demo");

        const fs::path src_file = mnt / "source.bin";
        const fs::path dst_file = subvol_path / "cloned.bin";

        {
            FileDescriptor tmp_fd(::open(src_file.c_str(), O_WRONLY | O_CREAT | O_TRUNC, 0644));
            if (tmp_fd.valid()) {
                const std::string payload = "Btrfs CoW Reflink Payload Data\n";
                ::write(tmp_fd.get(), payload.data(), payload.size());
            }
        }

        BtrfsManager::reflink_clone_file(src_file, dst_file);
        BtrfsManager::create_readonly_snapshot(subvol_path, mnt, "subvol_demo_snap");

    } catch (const std::exception& ex) {
        std::cerr << "[ERR] Помилка виконання: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
