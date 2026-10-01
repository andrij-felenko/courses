#include <stdio.h>
#include <stdlib.h>
#include <libusb-1.0/libusb.h>

#define CH340_BULK_IN_EP 0x82
#define BUF_SIZE 64

// Зворотний виклик асинхронної транзакції прийому
static void LIBUSB_CALL cb_bulk_in(struct libusb_transfer *transfer) {
    if (transfer->status == LIBUSB_TRANSFER_COMPLETED) {
        printf("Прийнято %d байт з CH340\n", transfer->actual_length);
        // Повторне відправлення транзакції для безперервного фонового читання
        libusb_submit_transfer(transfer);
    } else {
        fprintf(stderr, "Помилка асинхронного читання: %d\n", transfer->status);
        libusb_free_transfer(transfer);
    }
}

// Запуск фонового читання
int start_async_read(libusb_device_handle *dev, uint8_t *buffer) {
    struct libusb_transfer *transfer = libusb_alloc_transfer(0);
    if (!transfer) return -1;

    libusb_fill_bulk_transfer(
        transfer,
        dev,
        CH340_BULK_IN_EP,
        buffer,
        BUF_SIZE,
        cb_bulk_in,
        NULL,
        1000 // Таймаут 1000 мс
    );

    return libusb_submit_transfer(transfer);
}
