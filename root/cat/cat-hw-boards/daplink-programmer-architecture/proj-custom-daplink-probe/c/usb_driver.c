#include "daplink_board.h"
#include <string.h>

#define USB_PACKET_SIZE       64U
#define USB_BUFFER_COUNT      4U

// Структура кільцевого буфера для обміну пакетами CMSIS-DAP через USB
typedef struct {
    uint8_t data[USB_BUFFER_COUNT][USB_PACKET_SIZE];
    volatile uint8_t head;
    volatile uint8_t tail;
    volatile uint8_t count;
} USB_PacketBuffer_t;

static USB_PacketBuffer_t rx_buffer = {0};
static USB_PacketBuffer_t tx_buffer = {0};

// Дескриптор пристрою USB Composite (CMSIS-DAP v1 HID / WinUSB v2)
static const uint8_t usb_device_descriptor[18] = {
    0x12,       // bLength (18 байтів)
    0x01,       // bDescriptorType (Device)
    0x00, 0x02, // bcdUSB (USB 2.0)
    0x00,       // bDeviceClass (Composite)
    0x00,       // bDeviceSubClass
    0x00,       // bDeviceProtocol
    64,         // bMaxPacketSize0 (64 байти)
    0x83, 0x04, // idVendor (0x0483 STMicroelectronics)
    0x3B, 0x57, // idProduct (0x573B DAPLink Debugger)
    0x00, 0x01, // bcdDevice (1.00)
    0x01,       // iManufacturer (Індекс стрічки виробника)
    0x02,       // iProduct (Індекс стрічки продукту)
    0x03,       // iSerialNumber (Індекс серійного номера)
    0x01        // bNumConfigurations
};

// Ініціалізація периферійного модуля USB та буферів обміну
void usb_driver_init(void) {
    rx_buffer.head = 0;
    rx_buffer.tail = 0;
    rx_buffer.count = 0;

    tx_buffer.head = 0;
    tx_buffer.tail = 0;
    tx_buffer.count = 0;

    // Вмикаємо тактування модуля USB в RCC_APB1ENR (bit 23)
    RCC->APB1ENR |= (1U << 23);
}

// Запис пакета у вхідний буфер при отриманні USB-переривання
bool usb_rx_push(const uint8_t *packet) {
    if (rx_buffer.count >= USB_BUFFER_COUNT) {
        return false; // Буфер переповнений
    }
    memcpy(rx_buffer.data[rx_buffer.head], packet, USB_PACKET_SIZE);
    rx_buffer.head = (rx_buffer.head + 1U) % USB_BUFFER_COUNT;
    rx_buffer.count++;
    return true;
}

// Вичитання пакета з буфера прийому для обробки командами CMSIS-DAP
bool usb_rx_pop(uint8_t *packet) {
    if (rx_buffer.count == 0) {
        return false; // Порожній буфер
    }
    memcpy(packet, rx_buffer.data[rx_buffer.tail], USB_PACKET_SIZE);
    rx_buffer.tail = (rx_buffer.tail + 1U) % USB_BUFFER_COUNT;
    rx_buffer.count--;
    return true;
}

// Відправка пакета відповіді хосту через передавальний буфер
bool usb_tx_send(const uint8_t *packet) {
    if (tx_buffer.count >= USB_BUFFER_COUNT) {
        return false;
    }
    memcpy(tx_buffer.data[tx_buffer.head], packet, USB_PACKET_SIZE);
    tx_buffer.head = (tx_buffer.head + 1U) % USB_BUFFER_COUNT;
    tx_buffer.count++;
    return true;
}
