#include <stdint.h>

typedef struct SerialState {
    uint16_t divider;
    uint8_t  rbr;
    uint8_t  ier;
    uint8_t  iir;
    uint8_t  lcr;
    uint8_t  mcr;
    uint8_t  lsr;
    uint8_t  msr;
    uint8_t  scr;
} SerialState;

/* Декларативний опис структури серіалізації для QEMU VMState */
typedef struct VMStateField {
    const char *name;
    size_t offset;
    size_t size;
} VMStateField;

typedef struct VMStateDescription {
    const char *name;
    int version_id;
    int minimum_version_id;
    const VMStateField *fields;
} VMStateDescription;

static const VMStateField vmstate_serial_fields[] = {
    { "divider", offsetof(SerialState, divider), sizeof(uint16_t) },
    { "rbr",     offsetof(SerialState, rbr),     sizeof(uint8_t) },
    { "ier",     offsetof(SerialState, ier),     sizeof(uint8_t) },
    { "iir",     offsetof(SerialState, iir),     sizeof(uint8_t) },
    { "lcr",     offsetof(SerialState, lcr),     sizeof(uint8_t) },
    { "mcr",     offsetof(SerialState, mcr),     sizeof(uint8_t) },
    { "lsr",     offsetof(SerialState, lsr),     sizeof(uint8_t) },
    { "msr",     offsetof(SerialState, msr),     sizeof(uint8_t) },
    { "scr",     offsetof(SerialState, scr),     sizeof(uint8_t) },
    { NULL, 0, 0 }
};

static const VMStateDescription vmstate_serial = {
    .name = "serial",
    .version_id = 3,
    .minimum_version_id = 2,
    .fields = vmstate_serial_fields
};
