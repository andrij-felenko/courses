#include <stdint.h>

#define AUDIT_MAGIC 0x41554454 /* 'AUDT' */
#define HASH_SIZE 32

#pragma pack(push, 1)

struct audit_record_header {
    uint32_t magic;                 /* Магічні байти 'AUDT' */
    uint16_t version;               /* Версія бінарного формату (напр. 1) */
    uint16_t header_size;           /* Розмір заголовка в байтах (128) */
    uint64_t sequence_number;       /* Монотонний порядковий номер запису */
    uint64_t timestamp_nanos;       /* Наносекунди від Unix Epoch (UTC) */
    uint32_t payload_length;        /* Довжина корисного навантаження (JSON/Protobuf) */
    uint32_t key_epoch;             /* Поточна епоха Forward-Secure ключа */
    uint8_t  prev_hash[HASH_SIZE];  /* SHA-256 геш попереднього запису */
    uint8_t  signature[HASH_SIZE];  /* HMAC-SHA256 підпис поточного запису */
    uint8_t  reserved[16];          /* Резерв для майбутніх розширень (вирівнювання) */
};

#pragma pack(pop)
