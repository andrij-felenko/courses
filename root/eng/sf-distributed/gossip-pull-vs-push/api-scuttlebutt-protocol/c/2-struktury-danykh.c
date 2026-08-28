#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define SCUTTLEBUTT_MAGIC        0x5343
#define SCUTTLEBUTT_PROTO_VER    0x01
#define SCUTTLEBUTT_MAX_MTU      1400

/* Запис дайджесту версій вузла */
typedef struct {
    uint32_t endpoint_id;    /* Унікальний ID цільового сервера */
    uint64_t generation;     /* Епоха/мітка старту процесу (Unix epoch мс) */
    uint64_t max_version;    /* Монотонний лічильник локальних змін стану */
} DigestEntry;

/* Запис дельти стану (конкретна мутація атрибута) */
typedef struct {
    uint32_t endpoint_id;    /* ID сервера-власника стану */
    uint16_t key_id;         /* Ідентифікатор ключа (Status, Tokens, Schema) */
    uint64_t generation;     /* Епоха власника стану */
    uint64_t version;        /* Точний порядковий номер версії */
    uint16_t value_len;      /* Довжина корисного навантаження */
    uint8_t  value[0];       /* Байти значення (гнучкий масив C99) */
} DeltaEntry;
