#include <stdint.h>

/* Керуючий заголовок кадру Block Ack */
typedef struct {
    uint16_t ba_control;        /* Біти: [0..0] Ack Policy, [1..4] Multi-TID, [5..15] Compressed */
    uint16_t starting_seq_ctrl; /* Біти: [0..3] Номер фрагмента (завжди 0), [4..15] Starting Seq Num */
    uint64_t ba_bitmap;         /* 64-бітова маска підтверджень: біт k = 1 означає успішний прийом MPDU (SSN + k) */
} __attribute__((packed)) Ieee80211BlockAckFrame;

/* Запит блокового підтвердження (Block Ack Request - BAR) */
typedef struct {
    uint16_t bar_control;       /* Керуючі прапорці TID та політики */
    uint16_t starting_seq_ctrl; /* Початковий номер послідовності (Starting Sequence Number - SSN) */
} __attribute__((packed)) Ieee80211BlockAckReqFrame;
