#include <iostream>
#include <string>
#include <system_error>
#include <cstring>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/btrfs.h>

class BtrfsScrubController {
private:
    int fd_ = -1;

public:
    explicit BtrfsScrubController(const std::string& mount_point) {
        fd_ = ::open(mount_point.c_str(), O_RDONLY | O_DIRECTORY);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Не вдалося відкрити точку монтування Btrfs: " + mount_point);
        }
    }

    ~BtrfsScrubController() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // RAII керування дескриптором
    BtrfsScrubController(const BtrfsScrubController&) = delete;
    BtrfsScrubController& operator=(const BtrfsScrubController&) = delete;

    [[nodiscard]] btrfs_scrub_progress startScrub(std::uint64_t devid, bool read_only = false) {
        btrfs_ioctl_scrub_args args{};
        args.devid = devid;
        args.start = 0;
        args.end = static_cast<std::uint64_t>(-1);
        args.flags = read_only ? BTRFS_SCRUB_READONLY : 0;

        if (::ioctl(fd_, BTRFS_IOC_SCRUB, &args) < 0) {
            throw std::system_error(errno, std::generic_category(), 
                                   "Помилка виконання ioctl BTRFS_IOC_SCRUB");
        }

        return args.progress;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <точка_монтування> <devid>\n";
        return EXIT_FAILURE;
    }

    try {
        std::string mount_point = argv[1];
        std::uint64_t devid = std::stoull(argv[2]);

        BtrfsScrubController controller(mount_point);
        std::cout << "Запуск Btrfs Scrub (C++ RAII) для devid=" << devid << "...\n";

        auto progress = controller.startScrub(devid);

        std::cout << "Scrub завершено успішно!\n"
                  << "Даних оброблено: " << (progress.data_bytes_scrubbed / (1024 * 1024)) << " МіБ\n"
                  << "Метаданих оброблено: " << (progress.tree_bytes_scrubbed / (1024 * 1024)) << " МіБ\n"
                  << "Виявлено помилок CRC32c: " << progress.csum_errors << "\n"
                  << "Виправлено з дзеркала RAID: " << progress.corrected_errors << "\n"
                  << "Невідновлюваних збоїв: " << progress.uncorrectable_errors << std::endl;

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << std::endl;
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
