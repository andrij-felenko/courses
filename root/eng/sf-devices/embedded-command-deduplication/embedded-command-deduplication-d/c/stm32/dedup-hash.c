#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define DEDUP_CACHE_SIZE        64U   /* Кількість записів у кільцевому буфері FIFO */
#define DEDUP_HASH_TABLE_SIZE   127U  /* Розмір хеш-таблиці (просте число для зменшення колізій) */
#define DEDUP_MAX_PROBES        8U    /* Максимальна глибина лінійного зондування */
#define DEDUP_RESPONSE_MAX_LEN  16U   /* Максимальний розмір збереженої відповіді */

/* Стан транзакції */
typedef enum {
    TX_STATE_EMPTY = 0,
    TX_STATE_PROCESSING,
    TX_STATE_COMPLETED,
    TX_STATE_FAILED
} TxState_t;

/* Дескриптор транзакції */
typedef struct {
    uint32_t tx_id;
    uint16_t sender_id;
    TxState_t state;
    uint32_t timestamp_ms;
    uint8_t response[DEDUP_RESPONSE_MAX_LEN];
    uint8_t response_len;
} TxDescriptor_t;

/* Структура дедуплікатора у статичній пам'яті */
typedef struct {
    TxDescriptor_t ring_buffer[DEDUP_CACHE_SIZE]; /* Кільцевий буфер FIFO */
    uint16_t hash_table[DEDUP_HASH_TABLE_SIZE];   /* Хеш-таблиця індексів буфера */
    uint16_t head_idx;                            /* Позиція для запису нового елемента */
    uint16_t count;                               /* Поточна кількість елементів */
} CommandDedupCache_t;

/* Статичне виділення пам'яті у секції .bss (без malloc) */
static CommandDedupCache_t g_dedup_cache;

/* Просте обчислення хешу від TxID */
static inline uint16_t dedup_hash(uint32_t tx_id) {
    return (uint16_t)(tx_id % DEDUP_HASH_TABLE_SIZE);
}

/* Ініціалізація кешу */
void command_dedup_init(void) {
    memset(&g_dedup_cache, 0, sizeof(g_dedup_cache));
    for (uint32_t i = 0; i < DEDUP_HASH_TABLE_SIZE; i++) {
        g_dedup_cache.hash_table[i] = 0xFFFFU; /* 0xFFFF означає порожній бакет */
    }
}

/* Пошук або виділення місця для транзакції (детермінований O(1)) */
TxState_t command_dedup_check_and_insert(uint32_t tx_id, uint16_t sender_id, uint32_t current_time_ms, uint16_t* out_slot) {
    uint16_t start_bucket = dedup_hash(tx_id);
    
    /* 1. Пошук існуючої транзакції в хеш-таблиці з лінійним зондуванням */
    for (uint16_t probe = 0; probe < DEDUP_MAX_PROBES; probe++) {
        uint16_t bucket = (start_bucket + probe) % DEDUP_HASH_TABLE_SIZE;
        uint16_t slot = g_dedup_cache.hash_table[bucket];
        
        if (slot == 0xFFFFU) {
            break; /* Досягнуто порожнього бакета, транзакція відсутня */
        }
        
        TxDescriptor_t* desc = &g_dedup_cache.ring_buffer[slot];
        if (desc->tx_id == tx_id && desc->sender_id == sender_id && desc->state != TX_STATE_EMPTY) {
            *out_slot = slot;
            return desc->state; /* Hit: повертаємо поточний стан (PROCESSING або COMPLETED) */
        }
    }
    
    /* 2. Miss: виділення нового слота у кільцевому буфері FIFO */
    uint16_t new_slot = g_dedup_cache.head_idx;
    TxDescriptor_t* new_desc = &g_dedup_cache.ring_buffer[new_slot];
    
    /* Якщо витісняємо старий елемент, очищаємо його з хеш-таблиці */
    if (new_desc->state != TX_STATE_EMPTY) {
        uint16_t old_bucket = dedup_hash(new_desc->tx_id);
        for (uint16_t probe = 0; probe < DEDUP_MAX_PROBES; probe++) {
            uint16_t b = (old_bucket + probe) % DEDUP_HASH_TABLE_SIZE;
            if (g_dedup_cache.hash_table[b] == new_slot) {
                g_dedup_cache.hash_table[b] = 0xFFFFU;
                break;
            }
        }
    }
    
    /* Ініціалізація нового дескриптора */
    new_desc->tx_id = tx_id;
    new_desc->sender_id = sender_id;
    new_desc->state = TX_STATE_PROCESSING;
    new_desc->timestamp_ms = current_time_ms;
    new_desc->response_len = 0;
    
    /* Вставка нового індексу в хеш-таблицю */
    for (uint16_t probe = 0; probe < DEDUP_MAX_PROBES; probe++) {
        uint16_t bucket = (start_bucket + probe) % DEDUP_HASH_TABLE_SIZE;
        if (g_dedup_cache.hash_table[bucket] == 0xFFFFU) {
            g_dedup_cache.hash_table[bucket] = new_slot;
            break;
        }
    }
    
    /* Зсув голови кільцевого буфера FIFO */
    g_dedup_cache.head_idx = (g_dedup_cache.head_idx + 1U) % DEDUP_CACHE_SIZE;
    if (g_dedup_cache.count < DEDUP_CACHE_SIZE) {
        g_dedup_cache.count++;
    }
    
    *out_slot = new_slot;
    return TX_STATE_EMPTY; /* Повертаємо EMPTY як ознаку нового пакета */
}

/* Фіксація результату виконання транзакції */
void command_dedup_commit_response(uint16_t slot, const uint8_t* resp_data, uint8_t resp_len) {
    if (slot >= DEDUP_CACHE_SIZE) return;
    
    TxDescriptor_t* desc = &g_dedup_cache.ring_buffer[slot];
    if (resp_len > DEDUP_RESPONSE_MAX_LEN) {
        resp_len = DEDUP_RESPONSE_MAX_LEN;
    }
    memcpy(desc->response, resp_data, resp_len);
    desc->response_len = resp_len;
    desc->state = TX_STATE_COMPLETED;
}
