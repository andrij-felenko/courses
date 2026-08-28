#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define PBFT_DIGEST_SIZE 32
#define PBFT_MAX_REPLICAS 16

typedef struct {
    uint8_t bytes[PBFT_DIGEST_SIZE];
} pbft_digest_t;

typedef enum {
    PBFT_OK                           =  0,
    PBFT_ERR_INVALID_SIGNATURE        = -1,
    PBFT_ERR_INVALID_DIGEST           = -2,
    PBFT_ERR_VIEW_MISMATCH            = -3,
    PBFT_ERR_NOT_PRIMARY              = -4,
    PBFT_ERR_EQUIVOCATION             = -5,
    PBFT_ERR_DUPLICATE_MESSAGE        = -6,
    PBFT_ERR_WATERMARK_OUT_OF_BOUNDS  = -7,
    PBFT_ERR_INSUFFICIENT_QUORUM      = -8,
    PBFT_ERR_CHECKPOINT_INVALID       = -9
} pbft_result_t;

typedef struct {
    uint32_t view;
    uint32_t seq_num;
    pbft_digest_t digest;
    const uint8_t* payload;
    size_t payload_len;
    uint32_t sender_id;
} pbft_pre_prepare_msg_t;

typedef struct {
    uint32_t view;
    uint32_t seq_num;
    pbft_digest_t digest;
    uint32_t sender_id;
} pbft_prepare_msg_t;

typedef struct {
    uint32_t view;
    uint32_t seq_num;
    pbft_digest_t digest;
    uint32_t sender_id;
} pbft_commit_msg_t;

typedef struct {
    uint32_t new_view;
    uint32_t last_checkpoint_seq;
    pbft_digest_t state_digest;
    uint32_t sender_id;
} pbft_view_change_msg_t;

/* Непрозора структура внутрішнього стану репліки */
typedef struct pbft_replica_context pbft_replica_context_t;

/* Ініціалізація контексту репліки */
pbft_result_t pbft_replica_init(pbft_replica_context_t** ctx, uint32_t node_id, uint32_t total_nodes);

/* Обробка трансляції Pre-Prepare від первинного вузла */
pbft_result_t pbft_on_pre_prepare(pbft_replica_context_t* ctx, const pbft_pre_prepare_msg_t* msg, pbft_prepare_msg_t* out_prepare);

/* Обробка підтвердження Prepare від репліки */
pbft_result_t pbft_on_prepare(pbft_replica_context_t* ctx, const pbft_prepare_msg_t* msg, pbft_commit_msg_t* out_commit);

/* Обробка повідомлення Commit від репліки */
pbft_result_t pbft_on_commit(pbft_replica_context_t* ctx, const pbft_commit_msg_t* msg, bool* out_ready_to_execute);

/* Обробка сигналу тайм-ауту та формування повідомлення View-Change */
pbft_result_t pbft_on_view_change_timer(pbft_replica_context_t* ctx, pbft_view_change_msg_t* out_vc);

/* Фіксація завершення виконання транзакції та оновлення стану */
pbft_result_t pbft_mark_executed(pbft_replica_context_t* ctx, uint32_t seq_num);
