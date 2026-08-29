/* flight_recorder_core.c — ядро реєстратора: кільцевий буфер у .noinit,
 * запис за сталий час і фіксація аварії. */
#include "flight_recorder_core.h"
#include "mcu_port.h"

#include <string.h>

/* Секція .noinit виключена зі списку тих, що їх занулює стартовий код crt0,
 * тому вміст переживає і NVIC_SystemReset(), і скидання сторожовим таймером. */
__attribute__((section(".noinit"))) BlackBoxStorage_t g_bb_ram;

/* Незмінна частина заголовка, яку покриває header_crc: перші 16 байтів. */
#define BLACKBOX_HEADER_CRC_LEN 16U

uint16_t blackbox_crc16(const uint8_t* buffer, size_t size) {
    uint16_t crc = 0xFFFFU;
    for (size_t i = 0; i < size; ++i) {
        crc ^= ((uint16_t)buffer[i] << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000U) {
                crc = (uint16_t)((crc << 1) ^ 0x1021U);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}

static void seal_header(void) {
    g_bb_ram.header_crc = blackbox_crc16((const uint8_t*)&g_bb_ram, BLACKBOX_HEADER_CRC_LEN);
}

static bool header_is_sane(void) {
    if (g_bb_ram.magic != BLACKBOX_MAGIC_HEADER) {
        return false;
    }
    if (g_bb_ram.capacity != BLACKBOX_BUFFER_SIZE) {
        return false; /* том писала інша версія прошивки — розкладка кадрів інша */
    }
    if (g_bb_ram.head_index >= BLACKBOX_BUFFER_SIZE) {
        return false;
    }
    return g_bb_ram.header_crc == blackbox_crc16((const uint8_t*)&g_bb_ram, BLACKBOX_HEADER_CRC_LEN);
}

static void raise_fresh_volume(void) {
    memset((void*)&g_bb_ram, 0, sizeof(g_bb_ram));
    g_bb_ram.magic        = BLACKBOX_MAGIC_HEADER;
    g_bb_ram.capacity     = BLACKBOX_BUFFER_SIZE;
    g_bb_ram.boot_counter = 1;
    seal_header();
}

static void put_u32(uint8_t* dst, uint32_t value) {
    dst[0] = (uint8_t)(value & 0xFFU);
    dst[1] = (uint8_t)((value >> 8) & 0xFFU);
    dst[2] = (uint8_t)((value >> 16) & 0xFFU);
    dst[3] = (uint8_t)((value >> 24) & 0xFFU);
}

static void put_u16(uint8_t* dst, uint16_t value) {
    dst[0] = (uint8_t)(value & 0xFFU);
    dst[1] = (uint8_t)((value >> 8) & 0xFFU);
}

/* HFSR стиснутий у три біти: 0 — VECTTBL (збій читання таблиці векторів),
 * 1 — FORCED (налаштований виняток ескалювали в HardFault), 2 — DEBUGEVT. */
static uint16_t pack_hfsr(uint32_t hfsr) {
    uint16_t flags = 0;
    if ((hfsr & (1U << 1)) != 0U)  { flags |= 0x01U; }
    if ((hfsr & (1U << 30)) != 0U) { flags |= 0x02U; }
    if ((hfsr & (1U << 31)) != 0U) { flags |= 0x04U; }
    return flags;
}

static void fill_frame(BlackBoxFrame_t* frame,
                       BlackBoxSubsystem_t subsys,
                       BlackBoxEventCode_t code,
                       uint16_t fsm,
                       const void* data,
                       uint8_t len) {
    frame->timestamp_ms = mcu_get_uptime_ms();
    frame->subsystem    = (uint8_t)subsys;
    frame->event_code   = (uint8_t)code;
    frame->fsm_state    = fsm;

    memset(frame->payload, 0, sizeof(frame->payload));
    if (data != NULL && len > 0U) {
        uint8_t copy_size = (len > BLACKBOX_PAYLOAD_SIZE) ? (uint8_t)BLACKBOX_PAYLOAD_SIZE : len;
        memcpy(frame->payload, data, copy_size);
    }
    /* CRC ставимо ОСТАННІМ: доки він не збігається, декодер вважає кадр
     * недописаним — саме так виглядає слот, що його застало вимкнення. */
    frame->crc16 = blackbox_crc16((const uint8_t*)frame, 14U);
}

/* Захопити слот. Уся критична секція — це читання й інкремент індексу:
 * тіло кадру заповнюється вже поза нею, бо слот належить нам одноосібно. */
static uint32_t claim_slot(void) {
    uint32_t primask = mcu_enter_critical();
    uint32_t slot = g_bb_ram.head_index;
    g_bb_ram.head_index = (slot + 1U) & BLACKBOX_BUFFER_MASK;
    mcu_exit_critical(primask);
    return slot;
}

BlackBoxBootKind_t blackbox_init(void) {
    if (!header_is_sane()) {
        raise_fresh_volume();
        return BB_BOOT_COLD;
    }

    g_bb_ram.boot_counter++;
    seal_header();

    if (g_bb_ram.is_frozen != 0U) {
        /* Попередня сесія впала. Буфер лишається замороженим, щоб перші ж
         * записи нового запуску не затерли хронологію катастрофи. */
        return BB_BOOT_CRASH;
    }
    return BB_BOOT_WARM;
}

void blackbox_release(void) {
    g_bb_ram.is_frozen = 0U;
}

void flight_recorder_log(BlackBoxSubsystem_t subsys,
                         BlackBoxEventCode_t code,
                         uint16_t fsm,
                         const void* data,
                         uint8_t len) {
    if (g_bb_ram.is_frozen != 0U) {
        return;
    }
    fill_frame(&g_bb_ram.frames[claim_slot()], subsys, code, fsm, data, len);
}

/* Запис у панічному контексті: переривання вже вимкнені, прапорець заморозки
 * ігноруємо (він ставиться після останнього кадру аварії). */
static void panic_frame(BlackBoxEventCode_t code, uint16_t fsm, const uint8_t payload[BLACKBOX_PAYLOAD_SIZE]) {
    uint32_t slot = g_bb_ram.head_index;
    g_bb_ram.head_index = (slot + 1U) & BLACKBOX_BUFFER_MASK;
    fill_frame(&g_bb_ram.frames[slot], SUBSYS_CORE, code, fsm, payload, BLACKBOX_PAYLOAD_SIZE);
}

void blackbox_panic(const BlackBoxFault_t* fault) {
    (void)mcu_enter_critical(); /* назад до звичайного режиму дороги немає */

    if (!header_is_sane()) {
        /* Виняток стався до blackbox_init() або рознесло сам заголовок.
         * Піднімаємо том з нуля, щоб кадри аварії все одно лягли в пам'ять. */
        raise_fresh_volume();
    }

    uint8_t payload[BLACKBOX_PAYLOAD_SIZE];

    /* Кадр 1: де стало ядро і що каже молодша половина CFSR (MMFSR + BFSR). */
    put_u32(&payload[0], fault->pc);
    put_u16(&payload[4], (uint16_t)(fault->cfsr & 0xFFFFU));
    panic_frame(EVT_HARDFAULT, (uint16_t)(fault->cfsr >> 16), payload); /* fsm_state = UFSR */

    /* Кадр 2: адреса, на якій розсипалась шина або спрацював MPU. */
    put_u32(&payload[0], fault->fault_addr);
    put_u16(&payload[4], (uint16_t)fault->addr_valid);
    panic_frame(EVT_FAULT_ADDR, pack_hfsr(fault->hfsr), payload);

    /* Кадр 3: контекст — звідки прийшли й на якому стеку були. */
    put_u32(&payload[0], fault->lr);
    put_u16(&payload[4], (uint16_t)(fault->psr & 0x1FFU)); /* IPSR: номер винятку */
    panic_frame(EVT_FAULT_CONTEXT, (uint16_t)(fault->exc_return & 0xFFFFU), payload);

    g_bb_ram.crash_counter++;
    g_bb_ram.is_frozen = 1U;
    seal_header();
}

void blackbox_panic_abort(uint16_t reason, uint32_t context) {
    (void)mcu_enter_critical();

    if (!header_is_sane()) {
        raise_fresh_volume();
    }

    uint8_t payload[BLACKBOX_PAYLOAD_SIZE];
    put_u32(&payload[0], context);
    put_u16(&payload[4], 0U);
    panic_frame(EVT_PANIC_ABORT, reason, payload);

    g_bb_ram.crash_counter++;
    g_bb_ram.is_frozen = 1U;
    seal_header();
}

bool blackbox_is_crash_dump_present(void) {
    return header_is_sane() && g_bb_ram.crash_counter > 0U && g_bb_ram.is_frozen != 0U;
}

const BlackBoxStorage_t* blackbox_get_storage_ptr(void) {
    return &g_bb_ram;
}

size_t blackbox_get_storage_size(void) {
    return sizeof(BlackBoxStorage_t);
}
