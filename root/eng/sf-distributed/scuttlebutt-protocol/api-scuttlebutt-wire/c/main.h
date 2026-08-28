#ifndef SCUTTLEBUTT_API_H
#define SCUTTLEBUTT_API_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define SCUTTLEBUTT_MAGIC 0x53435554
#define SCUTTLEBUTT_PROTO_VERSION 1

typedef enum {
    SCUTTLEBUTT_MSG_SYN  = 0x01,
    SCUTTLEBUTT_MSG_ACK  = 0x02,
    SCUTTLEBUTT_MSG_ACK2 = 0x03
} ScuttlebuttMsgType;

typedef enum {
    SCUTTLEBUTT_OK = 0,
    SCUTTLEBUTT_ERR_INVALID_MAGIC = -1,
    SCUTTLEBUTT_ERR_BAD_CHECKSUM  = -2,
    SCUTTLEBUTT_ERR_BUFFER_OVERFLOW = -3,
    SCUTTLEBUTT_ERR_CORRUPT_PAYLOAD = -4
} ScuttlebuttStatus;

/* Непрозора структура рушія */
typedef struct ScuttlebuttContext ScuttlebuttContext;

/* Конфігураційні параметри рушія */
typedef struct {
    uint32_t gossip_interval_ms; /* Інтервал раундів пліток (за замовчуванням: 1000) */
    uint32_t mtu_limit_bytes;    /* Максимальний розмір корисного навантаження (1200..1400) */
    uint32_t failure_timeout_ms; /* Час визнання вузла мертвим (за замовчуванням: 10000) */
} ScuttlebuttConfig;

/* Створення та ініціалізація рушія */
ScuttlebuttContext* scuttlebutt_create(const char *local_node_id,
                                       uint64_t generation_epoch,
                                       const ScuttlebuttConfig *config);

/* Звільнення ресурсів */
void scuttlebutt_destroy(ScuttlebuttContext *ctx);

/* Оновлення локального ключа (інкрементує версію вузла) */
ScuttlebuttStatus scuttlebutt_set_local_state(ScuttlebuttContext *ctx,
                                             const char *key,
                                             const void *val,
                                             size_t val_len);

/* Отримання значення за ключем для вказаного вузла */
ScuttlebuttStatus scuttlebutt_get_state(const ScuttlebuttContext *ctx,
                                       const char *node_id,
                                       const char *key,
                                       void *out_val,
                                       size_t *out_val_len,
                                       uint64_t *out_version);

/* Генерація повідомлення SYN для надсилання обраному піру */
ScuttlebuttStatus scuttlebutt_build_syn(ScuttlebuttContext *ctx,
                                       uint8_t *out_buf,
                                       size_t max_buf_len,
                                       size_t *out_written);

/* Обробка отриманого повідомлення будь-якого типу */
ScuttlebuttStatus scuttlebutt_process_message(ScuttlebuttContext *ctx,
                                             const uint8_t *in_buf,
                                             size_t in_len,
                                             uint8_t *out_reply_buf,
                                             size_t max_reply_len,
                                             size_t *out_reply_len);

#endif /* SCUTTLEBUTT_API_H */
