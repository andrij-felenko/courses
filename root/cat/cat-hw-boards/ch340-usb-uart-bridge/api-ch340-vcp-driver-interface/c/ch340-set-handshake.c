#include <stdio.h>
#include <stdlib.h>
#include <libusb-1.0/libusb.h>

#define CH340_VID 0x1A86
#define CH340_PID 0x7523

// Налаштування ліній DTR та RTS через вендорний запит 0xA4
int ch340_set_handshake(libusb_device_handle *dev, uint8_t dtr, uint8_t rts) {
    uint16_t value = 0;
    
    // Формування маски керування та рівнів сигналів
    if (dtr) value |= (1 << 5) | (1 << 0);
    else     value |= (1 << 5);
    
    if (rts) value |= (1 << 6) | (1 << 1);
    else     value |= (1 << 6);

    // Відправка вендорного Setup-пакета на Control Endpoint 0
    int res = libusb_control_transfer(
        dev,
        LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE | LIBUSB_ENDPOINT_OUT,
        0xA4,    // bRequest для маніпуляції лініями
        value,   // wValue з маскою сигналів
        0,       // wIndex
        NULL, 0, // Немає додаткових даних
        1000     // Таймаут 1000 мс
    );

    return res >= 0 ? 0 : res;
}

int main(void) {
    libusb_context *ctx = NULL;
    libusb_device_handle *dev = NULL;

    if (libusb_init(&ctx) < 0) return 1;

    dev = libusb_open_device_with_vid_pid(ctx, CH340_VID, CH340_PID);
    if (!dev) {
        fprintf(stderr, "Пристрій CH340 не знайдено\n");
        libusb_exit(ctx);
        return 1;
    }

    // Від'єднання системного драйвера при наявності
    if (libusb_kernel_driver_active(dev, 0) == 1) {
        libusb_detach_kernel_driver(dev, 0);
    }

    if (libusb_claim_interface(dev, 0) < 0) {
        libusb_close(dev);
        libusb_exit(ctx);
        return 1;
    }

    // Встановлення DTR=1, RTS=0
    ch340_set_handshake(dev, 1, 0);

    libusb_release_interface(dev, 0);
    libusb_close(dev);
    libusb_exit(ctx);
    return 0;
}
