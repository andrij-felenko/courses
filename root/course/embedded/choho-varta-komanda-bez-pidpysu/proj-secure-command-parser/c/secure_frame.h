#ifndef SECURE_FRAME_H
#define SECURE_FRAME_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "hmac_sha256.h"

/* Кадр: заголовок 18 Б | навантаження N Б | тег 32 Б.
 * Заголовок і навантаження разом ідуть під HMAC. */
#define SECURE_FRAME_MAGIC     0xA55AU
#define SECURE_HEADER_SIZE     18U
#define SECURE_TAG_SIZE        HMAC_SHA256_TAG_SIZE
#define SECURE_FRAME_OVERHEAD  (SECURE_HEADER_SIZE + SECURE_TAG_SIZE)

/* Розмір ковзного вікна дорівнює розрядності маски: більше не влізе. */
#define REPLAY_WINDOW_SIZE     64ULL

typedef enum {
    SECURE_OK = 0,
    SECURE_ERR_BUFFER_TOO_SMALL,
    SECURE_ERR_INVALID_MAGIC,
    SECURE_ERR_PAYLOAD_MISMATCH,
    SECURE_ERR_AUTH_FAILED,
    SECURE_ERR_TIMESTAMP_EXPIRED,
    SECURE_ERR_REPLAY_DETECTED
} SecureStatus;

const char *secure_status_str(SecureStatus status);

/*
 * Ковзне вікно захисту від повтору: старший прийнятий лічильник і бітова
 * маска на 64 позиції нижче за нього. Біт 0 маски — сам max_seq.
 * Шістнадцять байтів стану на канал, жодного виділення пам'яті.
 */
typedef struct {
    uint64_t max_seq;
    uint64_t bitmap;
} ReplayWindow;

void replay_window_init(ReplayWindow *win);
/* true — лічильник ще не бачили і він не застарілий. Стану не змінює. */
bool replay_window_check(const ReplayWindow *win, uint64_t seq);
/* Фіксувати лише ПІСЛЯ успішної перевірки тегу: інакше підроблений кадр
 * із величезним лічильником зсуне вікно й відсіче справжні команди. */
void replay_window_commit(ReplayWindow *win, uint64_t seq);

/*
 * Стан одного захищеного каналу. Ключ не копіюється — структура тримає
 * вказівник, тож ключ мусить жити не менше за канал (зазвичай це масив
 * у Flash або в захищеній області RAM).
 */
typedef struct {
    const uint8_t *key;
    size_t         key_len;
    uint32_t       max_drift_s;   /* допустиме розходження годинників, секунд */
    ReplayWindow   window;
} SecureChannel;

/* Розібрана команда. payload вказує ВСЕРЕДИНУ вхідного буфера: копії немає,
 * тож дані дійсні рівно доти, доки живий буфер приймача. */
typedef struct {
    uint8_t         msg_type;
    uint64_t        seq_num;
    uint32_t        timestamp;
    const uint8_t  *payload;
    uint16_t        payload_len;
} SecureCommand;

void secure_channel_init(SecureChannel *ch, const uint8_t *key, size_t key_len,
                         uint32_t max_drift_s);

/*
 * Повний конвеєр приймача: рамка → тег → час → вікно → видача команди.
 * out заповнюється тільки при SECURE_OK.
 */
SecureStatus secure_frame_parse(SecureChannel *ch,
                                const uint8_t *frame, size_t frame_len,
                                uint32_t now_s,
                                SecureCommand *out);

#endif /* SECURE_FRAME_H */
