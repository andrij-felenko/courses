#ifndef DFU_PROTO_H
#define DFU_PROTO_H

#include <stddef.h>
#include <stdint.h>

/* Класові запити USB DFU 1.1 — поле bRequest пакета SETUP
   (bmRequestType = 0x21 для Host->Dev, 0xA1 для Dev->Host). */
#define DFU_DETACH    0x00u
#define DFU_DNLOAD    0x01u
#define DFU_UPLOAD    0x02u
#define DFU_GETSTATUS 0x03u
#define DFU_CLRSTATUS 0x04u
#define DFU_GETSTATE  0x05u
#define DFU_ABORT     0x06u

/* Розмір блоку передачі; те саме число стоїть у wTransferSize дескриптора. */
#define DFU_TRANSFER_SIZE 1024u

/* Стани кінцевого автомата (поле bState відповіді DFU_GETSTATUS). */
typedef enum {
    DFU_STATE_APP_IDLE            = 0x00u,
    DFU_STATE_APP_DETACH          = 0x01u,
    DFU_STATE_IDLE                = 0x02u,
    DFU_STATE_DNLOAD_SYNC         = 0x03u,
    DFU_STATE_DNBUSY              = 0x04u,
    DFU_STATE_DNLOAD_IDLE         = 0x05u,
    DFU_STATE_MANIFEST_SYNC       = 0x06u,
    DFU_STATE_MANIFEST            = 0x07u,
    DFU_STATE_MANIFEST_WAIT_RESET = 0x08u,
    DFU_STATE_UPLOAD_IDLE         = 0x09u,
    DFU_STATE_ERROR               = 0x0Au
} dfu_state_t;

/* Коди помилок (поле bStatus). Значення — зі специфікації DFU 1.1. */
typedef enum {
    DFU_OK               = 0x00u,
    DFU_ERR_TARGET       = 0x01u,
    DFU_ERR_FILE         = 0x02u,
    DFU_ERR_WRITE        = 0x03u,
    DFU_ERR_ERASE        = 0x04u,
    DFU_ERR_CHECK_ERASED = 0x05u,
    DFU_ERR_PROG         = 0x06u,
    DFU_ERR_VERIFY       = 0x07u,
    DFU_ERR_ADDRESS      = 0x08u,
    DFU_ERR_NOTDONE      = 0x09u,
    DFU_ERR_FIRMWARE     = 0x0Au,
    DFU_ERR_VENDOR       = 0x0Bu,
    DFU_ERR_USBR         = 0x0Cu,
    DFU_ERR_POR          = 0x0Du,
    DFU_ERR_UNKNOWN      = 0x0Eu,
    DFU_ERR_STALLEDPKT   = 0x0Fu
} dfu_status_t;

/* Функціональний дескриптор DFU — 9 байтів, віддається у складі конфігурації. */
typedef struct __attribute__((packed)) {
    uint8_t  bLength;         /* Розмір дескриптора = 9 байтів */
    uint8_t  bDescriptorType; /* Тип = 0x21 (DFU Functional Descriptor) */
    uint8_t  bmAttributes;    /* bit0 bitCanDnload, bit1 bitCanUpload,
                                 bit2 bitManifestationTolerant, bit3 bitWillDetach */
    uint16_t wDetachTimeOut;  /* Скільки мс чекати на USB Reset після DFU_DETACH */
    uint16_t wTransferSize;   /* Розмір одного блоку даних */
    uint16_t bcdDFUVersion;   /* Версія специфікації = 0x0110 (DFU 1.1) */
} dfu_functional_descriptor_t;

#define DFU_FUNC_DESC_TYPE 0x21u

extern const dfu_functional_descriptor_t dfu_functional_descriptor;

/* Відповідь на DFU_GETSTATUS — рівно шість байтів на дроті. */
#define DFU_GETSTATUS_LEN 6u

typedef struct {
    dfu_status_t status;
    uint32_t     poll_timeout_ms; /* На дроті лише 24 біти, Little-Endian */
    dfu_state_t  state;
    uint8_t      string_index;    /* Індекс рядка з поясненням помилки, 0 = немає */
} dfu_status_report_t;

void dfu_pack_status(const dfu_status_report_t *report, uint8_t out[DFU_GETSTATUS_LEN]);

/* Розширення ST DfuSe: команда їде тілом DFU_DNLOAD з wBlockNum = 0. */
typedef enum {
    DFUSE_SET_ADDRESS    = 0x21u,
    DFUSE_ERASE          = 0x41u,
    DFUSE_READ_UNPROTECT = 0x92u
} dfuse_kind_t;

typedef struct {
    dfuse_kind_t kind;
    uint32_t     address;    /* Значуще для SET_ADDRESS і посекторного ERASE */
    uint8_t      mass_erase; /* ERASE без адреси = стерти всю область застосунку */
} dfuse_command_t;

dfu_status_t dfuse_parse_command(const uint8_t *payload, size_t len, dfuse_command_t *out);

uint32_t dfu_le32(const uint8_t *p);

#endif /* DFU_PROTO_H */
