#include <stdint.h>

#define SNOWFLAKE_EPOCH 1288834974657ULL

/* Збирання 64-бітного ідентифікатора */
uint64_t snowflake_pack(uint64_t timestamp_ms, uint8_t dc_id, uint8_t worker_id, uint16_t seq) {
    return ((timestamp_ms - SNOWFLAKE_EPOCH) << 22)
         | (((uint64_t)dc_id & 0x1F) << 17)
         | (((uint64_t)worker_id & 0x1F) << 12)
         | ((uint64_t)seq & 0x0FFF);
}

/* Вилучення Unix-часу в мілісекундах */
uint64_t snowflake_extract_time(uint64_t id) {
    return (id >> 22) + SNOWFLAKE_EPOCH;
}

/* Вилучення ідентифікатора вузла */
uint8_t snowflake_extract_worker(uint64_t id) {
    return (uint8_t)((id >> 12) & 0x1F);
}

/* Вилучення ідентифікатора датацентру */
uint8_t snowflake_extract_datacenter(uint64_t id) {
    return (uint8_t)((id >> 17) & 0x1F);
}
