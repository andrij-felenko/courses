#include <iostream>
#include <memory>
#include <stdexcept>
#include <libusb-1.0/libusb.h>

class CH340Device {
private:
    libusb_context* ctx_ = nullptr;
    libusb_device_handle* dev_ = nullptr;
    static constexpr uint16_t VID = 0x1A86;
    static constexpr uint16_t PID = 0x7523;

public:
    CH340Device() {
        if (libusb_init(&ctx_) < 0) {
            throw std::runtime_error("Не вдалося ініціалізувати libusb");
        }
        dev_ = libusb_open_device_with_vid_pid(ctx_, VID, PID);
        if (!dev_) {
            libusb_exit(ctx_);
            throw std::runtime_error("Пристрій CH340 не знайдено");
        }
        if (libusb_kernel_driver_active(dev_, 0) == 1) {
            libusb_detach_kernel_driver(dev_, 0);
        }
        if (libusb_claim_interface(dev_, 0) < 0) {
            libusb_close(dev_);
            libusb_exit(ctx_);
            throw std::runtime_error("Не вдалося захопити USB-інтерфейс");
        }
    }

    ~CH340Device() {
        if (dev_) {
            libusb_release_interface(dev_, 0);
            libusb_close(dev_);
        }
        if (ctx_) {
            libusb_exit(ctx_);
        }
    }

    void setHandshake(bool dtr, bool rts) {
        uint16_t value = 0;
        if (dtr) value |= (1 << 5) | (1 << 0);
        else     value |= (1 << 5);
        if (rts) value |= (1 << 6) | (1 << 1);
        else     value |= (1 << 6);

        int res = libusb_control_transfer(
            dev_,
            LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE | LIBUSB_ENDPOINT_OUT,
            0xA4, value, 0, nullptr, 0, 1000
        );

        if (res < 0) {
            throw std::runtime_error("Помилка виконання контрольного транзакції");
        }
    }
};

int main() {
    try {
        CH340Device ch340;
        ch340.setHandshake(true, false);
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
    return 0;
}
