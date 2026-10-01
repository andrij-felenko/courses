#include <iostream>
#include <vector>
#include <libusb-1.0/libusb.h>

class AsyncReader {
public:
    static constexpr uint8_t BULK_IN_EP = 0x82;
    static constexpr size_t BUF_SIZE = 64;

    static void LIBUSB_CALL onReceive(libusb_transfer* transfer) {
        if (transfer->status == LIBUSB_TRANSFER_COMPLETED) {
            std::cout << "Отримано " << transfer->actual_length << " байт" << std::endl;
            libusb_submit_transfer(transfer);
        } else {
            std::cerr << "Збій асинхронного транспорту: " << transfer->status << std::endl;
            libusb_free_transfer(transfer);
        }
    }

    static int start(libusb_device_handle* dev, std::vector<uint8_t>& buf) {
        libusb_transfer* transfer = libusb_alloc_transfer(0);
        if (!transfer) return -1;

        libusb_fill_bulk_transfer(
            transfer, dev, BULK_IN_EP,
            buf.data(), static_cast<int>(buf.size()),
            onReceive, nullptr, 1000
        );

        return libusb_submit_transfer(transfer);
    }
};
