/* flight_recorder_core.h — двійковий інтерфейс бортового реєстратора.
 * Розкладка структур тут — це формат файла дампа: будь-яка зміна полів
 * зобов'язує змінити й декодер py/decode_blackbox.py. */
#ifndef FLIGHT_RECORDER_CORE_H
#define FLIGHT_RECORDER_CORE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define BLACKBOX_MAGIC_HEADER  0x424F5831U /* 'BOX1' */
#define BLACKBOX_BUFFER_SIZE   256U        /* 256 кадрів * 16 байтів = 4096 байтів */
#define BLACKBOX_BUFFER_MASK   (BLACKBOX_BUFFER_SIZE - 1U)
#define BLACKBOX_PAYLOAD_SIZE  6U

typedef enum {
    SUBSYS_CORE     = 0x00,
    SUBSYS_POWER    = 0x01,
    SUBSYS_NAV      = 0x02,
    SUBSYS_ACTUATOR = 0x03,
    SUBSYS_COMM     = 0x04
} BlackBoxSubsystem_t;

typedef enum {
    EVT_NONE           = 0x00,
    EVT_BOOT_OK        = 0x01,
    EVT_FSM_TRANSITION = 0x02,
    EVT_BUS_NACK       = 0x03,
    EVT_BUS_TIMEOUT    = 0x04,
    EVT_VOLTAGE_WARN   = 0x05,
    EVT_TEMP_CRITICAL  = 0x06,
    /* Три кадри аварії: разом вони вміщують увесь стан збою, який 6 байтів
     * корисного вантажу одного кадру втримати не можуть. */
    EVT_FAULT_CONTEXT  = 0xFC, /* LR повернення + номер винятку IPSR */
    EVT_FAULT_ADDR     = 0xFD, /* MMFAR/BFAR + прапорці їхньої дійсності */
    EVT_HARDFAULT      = 0xFE, /* PC збою + молодша половина CFSR */
    EVT_PANIC_ABORT    = 0xFF  /* програмна паніка (assert, стек RTOS) */
} BlackBoxEventCode_t;

/* Що показало ядро в момент винятку. Заповнює hardfault_trap.c. */
typedef struct {
    uint32_t pc;          /* адреса інструкції, на якій усе стало */
    uint32_t lr;          /* адреса повернення зі стекового кадру */
    uint32_t psr;         /* xPSR; молодші 9 бітів — номер винятку IPSR */
    uint32_t exc_return;  /* LR обробника: за 2-м бітом видно MSP чи PSP */
    uint32_t cfsr;        /* Configurable Fault Status */
    uint32_t hfsr;        /* HardFault Status */
    uint32_t fault_addr;  /* MMFAR або BFAR, якщо їхній біт дійсності стоїть */
    uint8_t  addr_valid;  /* біт0 — MMARVALID, біт1 — BFARVALID */
} BlackBoxFault_t;

/* 16-байтний двійковий кадр події. packed прибирає діри вирівнювання,
 * aligned(4) не дає масиву стати на непарну адресу — інакше Cortex-M0+
 * упіймав би пастку непарного доступу на першому ж записі. */
typedef struct __attribute__((packed, aligned(4))) {
    uint32_t timestamp_ms;
    uint8_t  subsystem;
    uint8_t  event_code;
    uint16_t fsm_state;
    uint8_t  payload[BLACKBOX_PAYLOAD_SIZE];
    uint16_t crc16; /* CRC-16/CCITT-FALSE над першими 14 байтами кадру */
} BlackBoxFrame_t;

/* Том реєстратора в секції .noinit. header_crc покриває ЛИШЕ незмінну частину
 * заголовка (magic, boot_counter, crash_counter, capacity): head_index росте на
 * кожному записі, і перераховувати CRC щоразу коштувало б більше за сам запис.
 * Цілісність head_index декодер судить діапазоном, кадрів — їхніми CRC. */
typedef struct __attribute__((packed, aligned(4))) {
    uint32_t magic;
    uint32_t boot_counter;
    uint32_t crash_counter;
    uint32_t capacity;            /* щоб декодер не вгадував місткість буфера */
    volatile uint32_t head_index; /* наступний вільний слот */
    volatile uint32_t is_frozen;  /* 1 — буфер заморожено після аварії */
    uint16_t header_crc;
    uint16_t reserved;
    BlackBoxFrame_t frames[BLACKBOX_BUFFER_SIZE];
} BlackBoxStorage_t;

typedef enum {
    BB_BOOT_COLD  = 0, /* пам'ять не пережила знеструмлення — том заведено з нуля */
    BB_BOOT_WARM  = 1, /* тепле скидання, хронологія попередньої сесії ціла */
    BB_BOOT_CRASH = 2  /* попередня сесія впала; буфер заморожено, чекає на вивантаження */
} BlackBoxBootKind_t;

/* Підняти том. Після BB_BOOT_CRASH запис лишається заблокованим, доки
 * застосунок не вивантажить дамп і не викличе blackbox_release(). */
BlackBoxBootKind_t blackbox_init(void);

/* Розморозити буфер після того, як аварійний знімок оброблено. */
void blackbox_release(void);

/* Записати подію. Безпечно з будь-якого обробника переривання. */
void flight_recorder_log(BlackBoxSubsystem_t subsys,
                         BlackBoxEventCode_t code,
                         uint16_t fsm,
                         const void* data,
                         uint8_t len);

/* Зафіксувати аварію трьома кадрами й заморозити буфер. Не повертається до
 * звичайного режиму: після неї застосунок або скидає ядро, або вивантажує дамп. */
void blackbox_panic(const BlackBoxFault_t* fault);

/* Програмна паніка без апаратного винятку (провалений assert, переповнення стека). */
void blackbox_panic_abort(uint16_t reason, uint32_t context);

bool blackbox_is_crash_dump_present(void);
const BlackBoxStorage_t* blackbox_get_storage_ptr(void);
size_t blackbox_get_storage_size(void);

/* CRC-16/CCITT-FALSE — той самий поліном рахує й декодер на комп'ютері. */
uint16_t blackbox_crc16(const uint8_t* buffer, size_t size);

#ifdef __cplusplus
}
#endif

#endif /* FLIGHT_RECORDER_CORE_H */
