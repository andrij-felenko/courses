/* flight_recorder.c - Реалізація модуля бортового реєстратора (C) */
#include "flight_recorder.h"

/* Розміщення буфера у незанулюваній секції оперативної пам'яті */
__attribute__((section(".noinit"))) static BlackBoxRamStorage_t g_blackbox;

/* Зовнішні системні функції платформи */
extern uint32_t get_system_uptime_ms(void);
extern void disable_interrupts(void);
extern void enable_interrupts(void);

static uint16_t crc16_ccitt(const uint8_t* data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

void flight_recorder_init(void) {
    if (g_blackbox.magic != BLACKBOX_MAGIC_HEADER) {
        /* Холодний старт після повного знеструмлення */
        g_blackbox.magic = BLACKBOX_MAGIC_HEADER;
        g_blackbox.boot_count = 1;
        g_blackbox.crash_count = 0;
        g_blackbox.head_index = 0;
        g_blackbox.is_frozen = 0;
        memset((void*)g_blackbox.events, 0, sizeof(g_blackbox.events));
    } else {
        /* Теплий старт після програмного скидання або Watchdog */
        g_blackbox.boot_count++;
        g_blackbox.is_frozen = 0; /* Розблокування буфера для нової сесії */
    }
}

void flight_recorder_log(SubsystemID_t subsys, EventID_t evt, uint16_t fsm, const void* payload, uint8_t len) {
    if (g_blackbox.is_frozen) {
        return; /* Запис заблоковано аварійним знімком */
    }

    disable_interrupts();
    uint32_t idx = g_blackbox.head_index;
    g_blackbox.head_index = (idx + 1) % BLACKBOX_BUFFER_CAPACITY;
    enable_interrupts();

    FlightEvent_t* slot = &g_blackbox.events[idx];
    slot->timestamp_ms = get_system_uptime_ms();
    slot->subsystem_id = (uint8_t)subsys;
    slot->event_id = (uint8_t)evt;
    slot->fsm_state = fsm;

    memset(slot->payload, 0, sizeof(slot->payload));
    if (payload && len > 0) {
        uint8_t copy_len = (len > sizeof(slot->payload)) ? sizeof(slot->payload) : len;
        memcpy(slot->payload, payload, copy_len);
    }

    slot->crc16 = crc16_ccitt((const uint8_t*)slot, 14);
}

void flight_recorder_panic(uint8_t reason_code, uint32_t fault_addr, uint32_t pc) {
    disable_interrupts();
    g_blackbox.is_frozen = 1; /* Миттєве заморожування буфера */
    g_blackbox.crash_count++;

    uint32_t idx = g_blackbox.head_index;
    FlightEvent_t* crash_slot = &g_blackbox.events[idx];
    crash_slot->timestamp_ms = get_system_uptime_ms();
    crash_slot->subsystem_id = SUBSYS_CORE;
    crash_slot->event_id = EVT_CRASH_PANIC;
    crash_slot->fsm_state = (uint16_t)reason_code;

    /* Збереження адрес інструкції PC та помилки пам'яті */
    memcpy(&crash_slot->payload[0], &pc, 4);
    memcpy(&crash_slot->payload[4], &fault_addr, 2);

    crash_slot->crc16 = crc16_ccitt((const uint8_t*)crash_slot, 14);
}

bool flight_recorder_has_valid_dump(void) {
    return (g_blackbox.magic == BLACKBOX_MAGIC_HEADER && g_blackbox.crash_count > 0);
}

const BlackBoxRamStorage_t* flight_recorder_get_storage(void) {
    return &g_blackbox;
}
