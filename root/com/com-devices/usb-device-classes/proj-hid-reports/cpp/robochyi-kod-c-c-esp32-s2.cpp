#include "Adafruit_TinyUSB.h"   // або esp_tinyusb.h на ESP-IDF

// Модифікатори (byte 0, бітові маски)
#define KEY_LCTRL  0x01
#define KEY_LSHIFT 0x02
#define KEY_LALT   0x04
#define KEY_LGUI   0x08   // Win/Cmd — ліва
#define KEY_RCTRL  0x10
#define KEY_RSHIFT 0x20
#define KEY_RALT   0x40
#define KEY_RGUI   0x80

// Usage ID (Keyboard/Keypad page 0x07), вибірка
#define KEY_A  0x04
#define KEY_R  0x15
#define KEY_NONE 0x00

typedef struct __attribute__((packed)) {
    uint8_t modifier;   // byte 0: бітова маска модифікаторів
    uint8_t reserved;   // byte 1: завжди 0x00
    uint8_t keys[6];    // byte 2..7: до 6 одночасних usage ID
} kbd_report_t;

// Дескриптор звіту — цей «бланк» стек віддає хосту при енумерації.
// TUD_HID_REPORT_DESC_KEYBOARD() розгортається у повний набір HID-item-байтів.
uint8_t const desc_hid_report[] = { TUD_HID_REPORT_DESC_KEYBOARD() };

Adafruit_USBD_HID usb_hid;
