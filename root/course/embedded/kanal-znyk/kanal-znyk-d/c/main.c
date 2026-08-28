#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define FLASH_SECTOR_SIZE     4096
#define FLASH_TOTAL_SECTORS   1024
#define FRAME_MAGIC           0xA55A
#define COMMIT_TOKEN_VALID    0xAA55AA55
#define COMMIT_TOKEN_EMPTY    0xFFFFFFFF

#define BACKOFF_BASE_SEC      10
#define BACKOFF_MAX_SEC       3600
#define BULK_BATCH_SIZE       16

typedef enum {
    RECORD_CLASS_NORMAL   = 0x01,
    RECORD_CLASS_DECIMATED= 0x02,
    RECORD_CLASS_ALARM    = 0x04,
    RECORD_CLASS_SUMMARY  = 0x08
} RecordClass;

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint32_t seq_num;
    uint32_t timestamp;
    uint16_t flags;
    uint16_t payload_len;
} FrameHeader;

typedef struct {
    uint32_t crc32;
    uint32_t commit_token;
} FrameFooter;
#pragma pack(pop)

typedef enum {
    SYNC_IDLE_ONLINE,
    SYNC_BACKOFF_SLEEP,
    SYNC_PROBE_LINK,
    SYNC_SEND_LIVE,
    SYNC_BULK_SYNC
} SyncState;

typedef struct {
    SyncState state;
    uint32_t head_sector;
    uint32_t head_offset;
    uint32_t tail_sector;
    uint32_t tail_offset;
    uint32_t backoff_attempt;
    uint32_t sleep_remaining_sec;
    uint32_t next_seq_num;
    uint32_t total_buffered_records;
} StorageSyncManager;

/* Апаратні абстракції платформи */
extern uint32_t hardware_crc32(const uint8_t *data, size_t len);
extern uint32_t hardware_random_uniform(uint32_t min, uint32_t max);
extern bool radio_transmit_packet(const uint8_t *buf, size_t len, uint32_t timeout_ms);
extern bool flash_raw_write(uint32_t addr, const uint8_t *buf, size_t len);
extern bool flash_raw_read(uint32_t addr, uint8_t *buf, size_t len);
extern bool flash_raw_erase_sector(uint32_t sector_index);

static uint32_t calculate_backoff_sleep(uint32_t attempt) {
    uint32_t max_interval = BACKOFF_BASE_SEC << (attempt > 10 ? 10 : attempt);
    if (max_interval > BACKOFF_MAX_SEC) {
        max_interval = BACKOFF_MAX_SEC;
    }
    /* Full Jitter: випадкове число в діапазоні [BACKOFF_BASE_SEC, max_interval] */
    return hardware_random_uniform(BACKOFF_BASE_SEC, max_interval);
}

void storage_manager_init(StorageSyncManager *mgr) {
    memset(mgr, 0, sizeof(StorageSyncManager));
    mgr->state = SYNC_IDLE_ONLINE;
    mgr->head_sector = 0;
    mgr->head_offset = 0;
    mgr->tail_sector = 0;
    mgr->tail_offset = 0;
    mgr->next_seq_num = 1;
}

bool storage_write_record(StorageSyncManager *mgr, RecordClass rclass,
                          uint32_t timestamp, const uint8_t *payload, uint16_t len) {
    size_t total_size = sizeof(FrameHeader) + len + sizeof(FrameFooter);
    
    /* Перевірка на переповнення сектора: перехід до наступного */
    if (mgr->head_offset + total_size > FLASH_SECTOR_SIZE) {
        uint32_t next_sec = (mgr->head_sector + 1) % FLASH_TOTAL_SECTORS;
        
        /* Якщо наступний сектор - це хвіст, увімкнути переповнення */
        if (next_sec == mgr->tail_sector) {
            if (rclass & RECORD_CLASS_ALARM) {
                /* Аварійні записи: примусове витіснення хвоста */
                mgr->tail_sector = (mgr->tail_sector + 1) % FLASH_TOTAL_SECTORS;
                mgr->tail_offset = 0;
                flash_raw_erase_sector(next_sec);
            } else {
                /* Звичайні виміри: скидання при переповненні */
                return false;
            }
        }
        
        mgr->head_sector = next_sec;
        mgr->head_offset = 0;
        
        /* Випереджальне фонове стирання наступного за ним сектора */
        uint32_t erase_ahead_sec = (mgr->head_sector + 1) % FLASH_TOTAL_SECTORS;
        if (erase_ahead_sec != mgr->tail_sector) {
            flash_raw_erase_sector(erase_ahead_sec);
        }
    }

    uint32_t base_addr = mgr->head_sector * FLASH_SECTOR_SIZE + mgr->head_offset;
    
    FrameHeader hdr = {
        .magic = FRAME_MAGIC,
        .seq_num = mgr->next_seq_num++,
        .timestamp = timestamp,
        .flags = (uint16_t)rclass,
        .payload_len = len
    };
    
    /* 1. Розрахунок контрольної суми */
    uint32_t crc = hardware_crc32((const uint8_t *)&hdr, sizeof(FrameHeader));
    crc = hardware_crc32(payload, len);
    
    FrameFooter ftr = {
        .crc32 = crc,
        .commit_token = COMMIT_TOKEN_EMPTY /* залишається 0xFFFFFFFF */
    };
    
    /* 2. Послідовний запис заголовка, даних та підвалу */
    flash_raw_write(base_addr, (const uint8_t *)&hdr, sizeof(FrameHeader));
    flash_raw_write(base_addr + sizeof(FrameHeader), payload, len);
    flash_raw_write(base_addr + sizeof(FrameHeader) + len, (const uint8_t *)&ftr, sizeof(FrameFooter));
    
    /* 3. Атомарний коміт: прошиваємо Commit Token */
    uint32_t commit_token = COMMIT_TOKEN_VALID;
    uint32_t commit_addr = base_addr + sizeof(FrameHeader) + len + offsetof(FrameFooter, commit_token);
    flash_raw_write(commit_addr, (const uint8_t *)&commit_token, sizeof(uint32_t));
    
    mgr->head_offset += total_size;
    mgr->total_buffered_records++;
    return true;
}

void storage_sync_step(StorageSyncManager *mgr, uint32_t current_time,
                       const uint8_t *latest_sample, uint16_t sample_len) {
    switch (mgr->state) {
    case SYNC_IDLE_ONLINE: {
        /* Спроба прямої передачі нового відліку */
        if (!radio_transmit_packet(latest_sample, sample_len, 500)) {
            /* Канал зник: буферизуємо поточний відлік і входимо в відкат */
            storage_write_record(mgr, RECORD_CLASS_NORMAL, current_time, latest_sample, sample_len);
            mgr->backoff_attempt = 1;
            mgr->sleep_remaining_sec = calculate_backoff_sleep(mgr->backoff_attempt);
            mgr->state = SYNC_BACKOFF_SLEEP;
        }
        break;
    }

    case SYNC_BACKOFF_SLEEP: {
        /* Новий вимір продовжує записуватися в Flash під час сну каналу */
        storage_write_record(mgr, RECORD_CLASS_NORMAL, current_time, latest_sample, sample_len);
        
        if (mgr->sleep_remaining_sec > 60) {
            mgr->sleep_remaining_sec -= 60;
        } else {
            mgr->sleep_remaining_sec = 0;
            mgr->state = SYNC_PROBE_LINK;
        }
        break;
    }

    case SYNC_PROBE_LINK: {
        uint8_t probe_byte = 0x7E;
        if (radio_transmit_packet(&probe_byte, 1, 1000)) {
            /* Шлюз відповів: переходимо до відправки живого стану */
            mgr->backoff_attempt = 0;
            mgr->state = SYNC_SEND_LIVE;
        } else {
            /* Шлюз недоступний: збільшуємо відкат і спимо далі */
            mgr->backoff_attempt++;
            mgr->sleep_remaining_sec = calculate_backoff_sleep(mgr->backoff_attempt);
            mgr->state = SYNC_BACKOFF_SLEEP;
        }
        break;
    }

    case SYNC_SEND_LIVE: {
        /* 1. Негайно відправити свіжі дані (Live First) */
        if (radio_transmit_packet(latest_sample, sample_len, 500)) {
            mgr->state = (mgr->total_buffered_records > 0) ? SYNC_BULK_SYNC : SYNC_IDLE_ONLINE;
        } else {
            mgr->state = SYNC_BACKOFF_SLEEP;
        }
        break;
    }

    case SYNC_BULK_SYNC: {
        /* 2. Пакетне викачування архіву з сектора Tail */
        uint8_t batch_buffer[512];
        size_t batch_bytes = 0;
        uint32_t records_packed = 0;
        uint32_t read_offset = mgr->tail_offset;

        while (records_packed < BULK_BATCH_SIZE && mgr->total_buffered_records > 0) {
            FrameHeader hdr;
            uint32_t addr = mgr->tail_sector * FLASH_SECTOR_SIZE + read_offset;
            flash_raw_read(addr, (uint8_t *)&hdr, sizeof(FrameHeader));
            
            if (hdr.magic != FRAME_MAGIC) {
                break;
            }
            
            size_t frame_total = sizeof(FrameHeader) + hdr.payload_len + sizeof(FrameFooter);
            if (batch_bytes + frame_total > sizeof(batch_buffer)) {
                break;
            }
            
            flash_raw_read(addr, batch_buffer + batch_bytes, frame_total);
            batch_bytes += frame_total;
            read_offset += frame_total;
            records_packed++;
        }

        if (batch_bytes > 0 && radio_transmit_packet(batch_buffer, batch_bytes, 1500)) {
            /* Сервер підтвердив блок: просуваємо хвіст */
            mgr->tail_offset = read_offset;
            if (mgr->tail_offset >= FLASH_SECTOR_SIZE) {
                mgr->tail_sector = (mgr->tail_sector + 1) % FLASH_TOTAL_SECTORS;
                mgr->tail_offset = 0;
            }
            mgr->total_buffered_records -= records_packed;
            
            if (mgr->total_buffered_records == 0) {
                mgr->state = SYNC_IDLE_ONLINE;
            }
        } else {
            /* Збій під час синхронізації: повернення у сон */
            mgr->state = SYNC_BACKOFF_SLEEP;
            mgr->backoff_attempt = 1;
            mgr->sleep_remaining_sec = calculate_backoff_sleep(mgr->backoff_attempt);
        }
        break;
    }
    }
}
