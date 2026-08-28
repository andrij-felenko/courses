#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/poll.h>
#include <linux/usbdevice_fs.h>

class UsbDeviceHandle {
    int fd_{-1};
    int interface_num_{0};

public:
    explicit UsbDeviceHandle(const std::string& path, int interface_num = 0)
        : interface_num_(interface_num) {
        fd_ = ::open(path.c_str(), O_RDWR);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити USB-пристрій");
        }

        if (::ioctl(fd_, USBDEVFS_CLAIMINTERFACE, &interface_num_) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Помилка захоплення інтерфейсу через usbfs");
        }
    }

    ~UsbDeviceHandle() noexcept {
        if (fd_ >= 0) {
            ::ioctl(fd_, USBDEVFS_RELEASEINTERFACE, &interface_num_);
            ::close(fd_);
        }
    }

    UsbDeviceHandle(const UsbDeviceHandle&) = delete;
    UsbDeviceHandle& operator=(const UsbDeviceHandle&) = delete;

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
};

struct UrbTransfer {
    usbdevfs_urb urb{};
    std::vector<uint8_t> buffer;
    std::size_t id{0};

    explicit UrbTransfer(std::size_t id_val, std::size_t size, uint8_t endpoint)
        : buffer(size, 0), id(id_val) {
        urb.type = USBDEVFS_URB_TYPE_BULK;
        urb.endpoint = endpoint;
        urb.buffer = buffer.data();
        urb.buffer_length = static_cast<int>(buffer.size());
        urb.usercontext = this;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " /dev/bus/usb/001/002\n";
        return EXIT_FAILURE;
    }

    try {
        UsbDeviceHandle device(argv[1], 0);
        constexpr std::size_t kNumUrbs = 4;
        constexpr std::size_t kBufferSize = 64;
        constexpr uint8_t kEndpointIn = 0x81;

        std::vector<std::unique_ptr<UrbTransfer>> transfers;
        transfers.reserve(kNumUrbs);

        /* Відправлення асинхронних пакетів через RAII контексти */
        for (std::size_t i = 0; i < kNumUrbs; ++i) {
            auto transfer = std::make_unique<UrbTransfer>(i, kBufferSize, kEndpointIn);
            if (::ioctl(device.native_handle(), USBDEVFS_SUBMITURB, &transfer->urb) < 0) {
                throw std::system_error(errno, std::generic_category(), "Помилка відправки USBDEVFS_SUBMITURB");
            }
            std::cout << "[+] Асинхронний URB #" << i << " надіслано в usbcore\n";
            transfers.push_back(std::move(transfer));
        }

        /* Цикл очікування подій через poll() */
        std::size_t completed = 0;
        ::pollfd pfd{ .fd = device.native_handle(), .events = POLLOUT, .revents = 0 };

        while (completed < kNumUrbs) {
            int ret = ::poll(&pfd, 1, 2000);
            if (ret < 0) {
                throw std::system_error(errno, std::generic_category(), "Помилка poll()");
            } else if (ret == 0) {
                std::cerr << "Таймаут очікування USBFS подій\n";
                break;
            }

            ::usbdevfs_urb* reaped{nullptr};
            while (::ioctl(device.native_handle(), USBDEVFS_REAPURBNDELAY, &reaped) == 0) {
                auto* st = static_cast<UrbTransfer*>(reaped->usercontext);
                std::cout << "[✓] URB #" << st->id << " завершено: status="
                          << reaped->status << ", actual_length=" << reaped->actual_length << "\n";
                completed++;
            }
        }

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
