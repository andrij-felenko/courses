/* C: Низькорівневий рушій крипто-політики з явним управлінням буферами */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef enum {
    DATA_CLASS_A_E2E = 1,
    DATA_CLASS_B_EDGE = 2,
    DATA_CLASS_C_SSE = 3
} dh_data_class_t;

typedef struct {
    dh_data_class_t data_class;
    uint8_t* payload;
    size_t payload_len;
    uint8_t* out_buffer;
    size_t out_capacity;
    size_t out_len;
} crypto_job_t;

typedef enum {
    CRYPTO_OK = 0,
    CRYPTO_ERR_POLICY_VIOLATION = -1,
    CRYPTO_ERR_NO_MEMORY = -2,
    CRYPTO_ERR_BUFFER_TOO_SMALL = -3
} crypto_result_t;

/* Безпечне обнулення пам'яті, яке не оптимізується компілятором */
static void secure_memzero(void* ptr, size_t len) {
    volatile uint8_t* p = (volatile uint8_t*)ptr;
    while (len--) {
        *p++ = 0;
    }
}

/* Симуляція генерації та шифрування DEK через KMS */
static crypto_result_t apply_serverside_envelope(crypto_job_t* job) {
    uint8_t dummy_dek[32];
    size_t i;
    
    if (job->out_capacity < job->payload_len + 64) {
        return CRYPTO_ERR_BUFFER_TOO_SMALL;
    }

    /* 1. Генеруємо одноразовий DEK */
    for (i = 0; i < 32; ++i) dummy_dek[i] = (uint8_t)(rand() % 256);

    /* 2. Записуємо префікс конверта SSE: [MAGIC_SSE][CLASS_C][DEK_HEADER][CIPHERTEXT] */
    memcpy(job->out_buffer, "SSE_ENV", 7);
    job->out_buffer[7] = (uint8_t)job->data_class;
    
    /* XOR-симуляція AES-GCM шифрування для прикладу */
    for (i = 0; i < job->payload_len; ++i) {
        job->out_buffer[8 + i] = job->payload[i] ^ dummy_dek[i % 32];
    }
    job->out_len = 8 + job->payload_len;

    /* 3. Гарантовано очищаємо відкритий DEK у пам'яті (Zeroization) */
    secure_memzero(dummy_dek, sizeof(dummy_dek));
    return CRYPTO_OK;
}

crypto_result_t process_crypto_policy(crypto_job_t* job) {
    if (!job || !job->payload || !job->out_buffer) {
        return CRYPTO_ERR_POLICY_VIOLATION;
    }

    switch (job->data_class) {
        case DATA_CLASS_A_E2E:
            /* E2E: Сервер не шифрує і не розшифровує — лише копіює непрозорий шифротекст */
            if (job->out_capacity < job->payload_len) return CRYPTO_ERR_BUFFER_TOO_SMALL;
            memcpy(job->out_buffer, job->payload, job->payload_len);
            job->out_len = job->payload_len;
            return CRYPTO_OK;

        case DATA_CLASS_C_SSE:
            /* SSE: Виконуємо конвертне шифрування на сервері */
            return apply_serverside_envelope(job);

        case DATA_CLASS_B_EDGE:
            /* Edge: Передається без змін на локальний хаб */
            if (job->out_capacity < job->payload_len) return CRYPTO_ERR_BUFFER_TOO_SMALL;
            memcpy(job->out_buffer, job->payload, job->payload_len);
            job->out_len = job->payload_len;
            return CRYPTO_OK;

        default:
            return CRYPTO_ERR_POLICY_VIOLATION;
    }
}
