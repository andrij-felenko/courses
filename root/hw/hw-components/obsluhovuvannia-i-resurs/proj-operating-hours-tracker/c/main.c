#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FLASH_SECTOR_SIZE   4096U
#define RECORD_MAGIC        0xA55A

/* 32-байтна структура збереження життєвого циклу */
typedef struct __attribute__((packed)) {
    uint16_t magic;            /* Сигнатура валідності (0xA55A) */
    uint16_t sequence_id;      /* Монотонно зростаючий лічильник записів */
    uint32_t flight_time_sec;  /* Напрацювання в польоті під навантаженням (секунди) */
    uint32_t total_milliamp_s; /* Інтеграл струму: міліампер-секунди (кулони) */
    uint16_t power_cycles;     /* Кількість увімкнень живлення (холодні старти) */
    uint16_t connector_cycles; /* Оцінка підключень силового роз'єму */
    uint16_t max_temp_c;       /* Зафіксована пікова температура (°C · 10) */
    uint16_t esc_vibration_idx;/* Середній індекс вібраційного навантаження */
    uint8_t  reserved[12];     /* Запас для майбутніх метрик */
    uint16_t crc16;            /* Контрольна сума CRC-CCITT */
} LifeRecord;

/* Прототипи апаратного рівня (HAL) */
extern bool hal_flash_read(uint32_t address, void* buffer, size_t length);
extern bool hal_flash_write(uint32_t address, const void* data, size_t length);
extern bool hal_flash_erase_sector(uint32_t sector_address);

static uint16_t crc16_ccitt(const uint8_t* data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

typedef struct {
    uint32_t sector_base_addr;
    uint32_t current_slot_idx;
    LifeRecord active_state;
} WearTracker;

bool wear_tracker_init(WearTracker* tracker, uint32_t sector_addr) {
    tracker->sector_base_addr = sector_addr;
    tracker->current_slot_idx = 0;
    memset(&tracker->active_state, 0, sizeof(LifeRecord));

    uint16_t max_seq = 0;
    bool found_valid = false;
    uint32_t num_slots = FLASH_SECTOR_SIZE / sizeof(LifeRecord);

    /* Сканування сектора для пошуку найсвіжішого валідного запису */
    for (uint32_t i = 0; i < num_slots; i++) {
        LifeRecord rec;
        uint32_t slot_addr = sector_addr + i * sizeof(LifeRecord);
        if (!hal_flash_read(slot_addr, &rec, sizeof(LifeRecord))) {
            return false;
        }

        if (rec.magic == RECORD_MAGIC) {
            uint16_t expected_crc = crc16_ccitt((const uint8_t*)&rec, sizeof(LifeRecord) - sizeof(uint16_t));
            if (rec.crc16 == expected_crc) {
                if (!found_valid || rec.sequence_id >= max_seq) {
                    max_seq = rec.sequence_id;
                    tracker->active_state = rec;
                    tracker->current_slot_idx = i;
                    found_valid = true;
                }
            }
        }
    }

    if (found_valid) {
        /* Переходимо до наступного вільного слота */
        tracker->current_slot_idx = (tracker->current_slot_idx + 1) % num_slots;
    } else {
        /* Сектор порожній або пошкоджений: ініціалізуємо новий */
        hal_flash_erase_sector(sector_addr);
        tracker->active_state.magic = RECORD_MAGIC;
        tracker->active_state.sequence_id = 1;
        tracker->current_slot_idx = 0;
    }

    return true;
}

bool wear_tracker_commit(WearTracker* tracker) {
    uint32_t num_slots = FLASH_SECTOR_SIZE / sizeof(LifeRecord);

    /* Якщо дійшли до кінця сектора — стираємо та починаємо з 0 */
    if (tracker->current_slot_idx == 0 && tracker->active_state.sequence_id > 1) {
        if (!hal_flash_erase_sector(tracker->sector_base_addr)) {
            return false;
        }
    }

    tracker->active_state.magic = RECORD_MAGIC;
    tracker->active_state.sequence_id++;
    tracker->active_state.crc16 = crc16_ccitt(
        (const uint8_t*)&tracker->active_state,
        sizeof(LifeRecord) - sizeof(uint16_t)
    );

    uint32_t target_addr = tracker->sector_base_addr + tracker->current_slot_idx * sizeof(LifeRecord);
    if (!hal_flash_write(target_addr, &tracker->active_state, sizeof(LifeRecord))) {
        return false;
    }

    tracker->current_slot_idx = (tracker->current_slot_idx + 1) % num_slots;
    return true;
}

void wear_tracker_add_flight_time(WearTracker* tracker, uint32_t seconds, uint32_t current_ma) {
    tracker->active_state.flight_time_sec += seconds;
    tracker->active_state.total_milliamp_s += seconds * current_ma;
}
