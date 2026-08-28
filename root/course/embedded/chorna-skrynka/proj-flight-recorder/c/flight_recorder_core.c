/* flight_recorder_core.c - Реалізація функцій запису та контролю цілісності (C) */
#include "flight_recorder_core.h"
#include <string.h>

/* Розміщення в спеціальній незанулюваній секції оперативної пам'яті */
__attribute__((section(".noinit"))) static BlackBoxStorage_t g_bb_ram;

/* Апаратні системні виклики мікроконтролера */
extern uint32_t mcu_get_uptime_ms(void);
extern uint32_t mcu_enter_critical(void);
extern void mcu_exit_critical(uint32_t primask);

static uint16_t calculate_crc16(const uint8_t* buffer, size_t size) {
    uint16_t crc = 0xFFFFU;
    for (size_t i = 0; i < size; ++i) {
        crc ^= ((uint16_t)buffer[i] << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000U) {
                crc = (crc << 1) ^ 0x1021U;
            } else {
                crc = (crc << 1);
            }
        }
    }
    return crc;
}

void blackbox_init(void) {
    if (g_bb_ram.magic != BLACKBOX_MAGIC_HEADER) {
        /* Перше увімкнення після повного знеструмлення */
        g_bb_ram.magic = BLACKBOX_MAGIC_HEADER;
        g_bb_ram.boot_counter = 1;
        g_bb_ram.crash_counter = 0;
        g_bb_ram.head_index = 0;
        g_bb_ram.is_frozen = 0;
        memset((void*)g_bb_ram.frames, 0, sizeof(g_bb_ram.frames));
    } else {
        /* Перезапуск після програмного скидання або аварійного винятку */
        g_bb_ram.boot_counter++;
        g_bb_ram.is_frozen = 0; /* Розблокування буфера для нової сесії */
    }
}

void blackbox_record(BlackBoxSubsystem_t subsys, BlackBoxEventCode_t code, uint16_t fsm, const void* data, uint8_t len) {
    if (g_bb_ram.is_frozen != 0) {
        return; /* Запис заблоковано для збереження аварійного знімка */
    }

    uint32_t primask = mcu_enter_critical();
    uint32_t slot_idx = g_bb_ram.head_index;
    g_bb_ram.head_index = (slot_idx + 1U) & BLACKBOX_BUFFER_MASK;
    mcu_exit_critical(primask);

    BlackBoxFrame_t* frame = &g_bb_ram.frames[slot_idx];
    frame->timestamp_ms = mcu_get_uptime_ms();
    frame->subsystem = (uint8_t)subsys;
    frame->event_code = (uint8_t)code;
    frame->fsm_state = fsm;

    memset(frame->payload, 0, sizeof(frame->payload));
    if (data != NULL && len > 0) {
        uint8_t copy_size = (len > sizeof(frame->payload)) ? (uint8_t)sizeof(frame->payload) : len;
        memcpy(frame->payload, data, copy_size);
    }

    frame->crc16 = calculate_crc16((const uint8_t*)frame, 14);
}

void blackbox_emergency_panic(uint8_t reason, uint32_t pc, uint32_t fault_addr) {
    mcu_enter_critical();
    g_bb_ram.is_frozen = 1; /* Атомарне заморожування буфера */
    g_bb_ram.crash_counter++;

    uint32_t slot_idx = g_bb_ram.head_index;
    BlackBoxFrame_t* panic_frame = &g_bb_ram.frames[slot_idx];
    panic_frame->timestamp_ms = mcu_get_uptime_ms();
    panic_frame->subsystem = (uint8_t)SUBSYS_CORE;
    panic_frame->event_code = (uint8_t)EVT_HARDFAULT;
    panic_frame->fsm_state = (uint16_t)reason;

    memcpy(&panic_frame->payload[0], &pc, sizeof(uint32_t));
    memcpy(&panic_frame->payload[4], &fault_addr, 2);

    panic_frame->crc16 = calculate_crc16((const uint8_t*)panic_frame, 14);
}

bool blackbox_is_crash_dump_present(void) {
    return (g_bb_ram.magic == BLACKBOX_MAGIC_HEADER && g_bb_ram.crash_counter > 0);
}

const BlackBoxStorage_t* blackbox_get_storage_ptr(void) {
    return &g_bb_ram;
}
