/*
 * frame_pipeline.c — конвеєр обробки мережевого кадру на статичній пам'яті.
 *
 * Арена тримає все тимчасове одного кадру, пул — довгоживучі сесії.
 * Динамічної купи в програмі немає жодного байта; printf у main — це
 * хостовий вивід демонстрації, у прошивці на його місці кільцевий журнал.
 */
#include "alloc.h"

#include <stdio.h>
#include <string.h>

#define MAX_SESSIONS      8u
#define FRAME_ARENA_BYTES 1024u
#define SESSION_KEY_LEN   32u
#define FRAME_HEADER_LEN  5u    /* тип (1 Б) + номер сесії (4 Б, big-endian) */
#define NOTE_LEN          64u

typedef struct {
    uint32_t id;
    uint32_t last_active_ms;
    uint8_t  key[SESSION_KEY_LEN];
} client_session_t;

typedef enum {
    FRAME_OPEN  = 0x01,
    FRAME_DATA  = 0x02,
    FRAME_CLOSE = 0x03
} frame_type_t;

typedef enum {
    FRAME_OK = 0,
    FRAME_ERR_TOO_SHORT,
    FRAME_ERR_ARENA_FULL,
    FRAME_ERR_POOL_EXHAUSTED,
    FRAME_ERR_NO_SESSION,
    FRAME_ERR_DUPLICATE,
    FRAME_ERR_BAD_TYPE
} frame_result_t;

/* Уся пам'ять підсистеми — статичні масиви, розписані у відомості бюджету.
   Вирівнювання обов'язкове: у тілі вільних блоків живе список. */
static _Alignas(uintptr_t) uint8_t s_session_mem[MAX_SESSIONS * sizeof(client_session_t)];
static _Alignas(uintptr_t) uint8_t s_frame_mem[FRAME_ARENA_BYTES];

static fixed_pool_t      s_session_pool;
static memory_arena_t    s_frame_arena;
static client_session_t *s_sessions[MAX_SESSIONS];

bool           system_memory_init(void);
frame_result_t process_incoming_frame(const uint8_t *raw, size_t len, uint32_t now_ms);
void           memory_report(void);

bool system_memory_init(void)
{
    memset(s_sessions, 0, sizeof s_sessions);
    if (!pool_init(&s_session_pool, s_session_mem, sizeof s_session_mem,
                   sizeof(client_session_t))) {
        return false;
    }
    return arena_init(&s_frame_arena, s_frame_mem, sizeof s_frame_mem);
}

static uint32_t read_be32(const uint8_t *p)
{
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8)  | (uint32_t)p[3];
}

static client_session_t **session_slot(uint32_t id)
{
    for (size_t i = 0u; i < MAX_SESSIONS; ++i) {
        if (s_sessions[i] != NULL && s_sessions[i]->id == id) {
            return &s_sessions[i];
        }
    }
    return NULL;
}

static client_session_t **empty_slot(void)
{
    for (size_t i = 0u; i < MAX_SESSIONS; ++i) {
        if (s_sessions[i] == NULL) {
            return &s_sessions[i];
        }
    }
    return NULL;
}

/* Умовне «дешифрування»: тут важливий не шифр, а те, що відкритий текст
   лежить в арені й зникає разом із кадром, не лишаючи слідів у купі. */
static void decrypt_into(uint8_t *dst, const uint8_t *src, size_t len, uint8_t mask)
{
    for (size_t i = 0u; i < len; ++i) {
        dst[i] = (uint8_t)(src[i] ^ mask);
    }
}

static void log_note(const char *text)
{
    printf("    журнал: %s\n", text);
}

frame_result_t process_incoming_frame(const uint8_t *raw, size_t len, uint32_t now_ms)
{
    /* 1. Кадр починається зі скидання арени: усе тимчасове попереднього
          кадру зникло однією операцією, і жоден ранній return не міг
          лишити по собі витоку. */
    arena_reset(&s_frame_arena);

    if (raw == NULL || len < FRAME_HEADER_LEN) {
        return FRAME_ERR_TOO_SHORT;
    }

    const uint8_t  type     = raw[0];
    const uint32_t id       = read_be32(&raw[1]);
    const size_t   body_len = len - FRAME_HEADER_LEN;

    /* 2. Тіло кадру розшифровуємо в нижній бік арени. */
    uint8_t *body = NULL;
    if (body_len > 0u) {
        body = (uint8_t *)arena_alloc_array(&s_frame_arena, body_len, sizeof(uint8_t), 4u);
        if (body == NULL) {
            return FRAME_ERR_ARENA_FULL;   /* кадр більший за бюджет арени */
        }
        decrypt_into(body, raw + FRAME_HEADER_LEN, body_len, 0x5Au);
    }

    /* 3. Рядок діагностики беремо з ВЕРХНЬОГО курсора: він живе лічені
          мікросекунди й не має відбирати місце в розбору кадру. */
    char *note = (char *)arena_alloc_scratch_aligned(&s_frame_arena, NOTE_LEN, 4u);
    if (note == NULL) {
        return FRAME_ERR_ARENA_FULL;
    }
    (void)snprintf(note, NOTE_LEN, "тип=0x%02X сесія=%lu тіло=%lu Б",
                   (unsigned)type, (unsigned long)id, (unsigned long)body_len);

    frame_result_t result = FRAME_OK;

    switch (type) {
    case FRAME_OPEN: {
        if (body_len < SESSION_KEY_LEN) {
            result = FRAME_ERR_TOO_SHORT;
            break;
        }
        if (session_slot(id) != NULL) {
            result = FRAME_ERR_DUPLICATE;
            break;
        }
        client_session_t **slot = empty_slot();
        if (slot == NULL) {
            result = FRAME_ERR_POOL_EXHAUSTED;
            break;
        }
        client_session_t *session = (client_session_t *)pool_alloc(&s_session_pool);
        if (session == NULL) {
            result = FRAME_ERR_POOL_EXHAUSTED;  /* ліміт сесій вичерпано — відмова, не аварія */
            break;
        }
        session->id             = id;
        session->last_active_ms = now_ms;
        memcpy(session->key, body, SESSION_KEY_LEN);
        *slot = session;
        break;
    }

    case FRAME_DATA: {
        client_session_t **slot = session_slot(id);
        if (slot == NULL) {
            result = FRAME_ERR_NO_SESSION;
            break;
        }
        (*slot)->last_active_ms = now_ms;
        /* «Обробка»: контрольна сума тіла в тимчасовій пам'яті арени. */
        uint32_t sum = 0u;
        for (size_t i = 0u; i < body_len; ++i) {
            sum += body[i];
        }
        (void)sum;
        break;
    }

    case FRAME_CLOSE: {
        client_session_t **slot = session_slot(id);
        if (slot == NULL) {
            result = FRAME_ERR_NO_SESSION;
            break;
        }
        (void)pool_free(&s_session_pool, *slot);
        *slot = NULL;                          /* дисципліна: звільнив — занулив */
        break;
    }

    default:
        result = FRAME_ERR_BAD_TYPE;
        break;
    }

    log_note(note);
    /* 4. Жодного free() наприкінці: уся тимчасова пам'ять зникне сама на
          початку наступного кадру. */
    return result;
}

void memory_report(void)
{
    printf("Пул сесій:   зайнято %lu з %lu, найгірший запас %lu блоків\n",
           (unsigned long)(pool_block_count(&s_session_pool) - pool_free_count(&s_session_pool)),
           (unsigned long)pool_block_count(&s_session_pool),
           (unsigned long)pool_min_free_count(&s_session_pool));
    printf("Арена кадру: пік %lu з %lu байтів (%lu%% бюджету)\n",
           (unsigned long)arena_peak(&s_frame_arena),
           (unsigned long)FRAME_ARENA_BYTES,
           (unsigned long)(arena_peak(&s_frame_arena) * 100u / FRAME_ARENA_BYTES));
}

/* ------------------------------------------------------------------ */
/*  Демонстрація                                                        */
/* ------------------------------------------------------------------ */

static const char *result_name(frame_result_t r)
{
    switch (r) {
    case FRAME_OK:                 return "OK";
    case FRAME_ERR_TOO_SHORT:      return "кадр закороткий";
    case FRAME_ERR_ARENA_FULL:     return "арена переповнена";
    case FRAME_ERR_POOL_EXHAUSTED: return "пул сесій вичерпано";
    case FRAME_ERR_NO_SESSION:     return "невідома сесія";
    case FRAME_ERR_DUPLICATE:      return "сесія вже відкрита";
    case FRAME_ERR_BAD_TYPE:       return "невідомий тип кадру";
    default:                       return "?";
    }
}

static size_t build_frame(uint8_t *out, size_t cap, uint8_t type, uint32_t id,
                          const uint8_t *body, size_t body_len)
{
    if (out == NULL || cap < FRAME_HEADER_LEN + body_len) {
        return 0u;
    }
    out[0] = type;
    out[1] = (uint8_t)(id >> 24);
    out[2] = (uint8_t)(id >> 16);
    out[3] = (uint8_t)(id >> 8);
    out[4] = (uint8_t)id;
    for (size_t i = 0u; i < body_len; ++i) {
        out[FRAME_HEADER_LEN + i] = (uint8_t)(body[i] ^ 0x5Au);  /* «шифруємо» */
    }
    return FRAME_HEADER_LEN + body_len;
}

static void run(const char *label, const uint8_t *frame, size_t len, uint32_t now_ms)
{
    const frame_result_t r = process_incoming_frame(frame, len, now_ms);
    printf("%-22s -> %s\n", label, result_name(r));
}

int main(void)
{
    static uint8_t rx[2048];
    static uint8_t key[SESSION_KEY_LEN];
    static uint8_t blob[1500];
    char label[48];

    if (!system_memory_init()) {
        fputs("Не вдалося розмітити статичну пам'ять\n", stderr);
        return 1;
    }

    for (size_t i = 0u; i < SESSION_KEY_LEN; ++i) {
        key[i] = (uint8_t)(0x40u + i);
    }
    memset(blob, 0x11, sizeof blob);

    /* 1. Відкриваємо стільки сесій, скільки має пул, і ще одну зайву. */
    for (uint32_t id = 1u; id <= MAX_SESSIONS + 1u; ++id) {
        const size_t n = build_frame(rx, sizeof rx, FRAME_OPEN, id, key, SESSION_KEY_LEN);
        (void)snprintf(label, sizeof label, "OPEN сесія %lu", (unsigned long)id);
        run(label, rx, n, id * 100u);
    }

    /* 2. Дані у відому й у невідому сесію. */
    size_t n = build_frame(rx, sizeof rx, FRAME_DATA, 3u, blob, 200u);
    run("DATA сесія 3", rx, n, 1000u);
    n = build_frame(rx, sizeof rx, FRAME_DATA, 42u, blob, 8u);
    run("DATA сесія 42", rx, n, 1100u);

    /* 3. Закриваємо сесію 3 — блок повертається в пул і слот знову вільний. */
    n = build_frame(rx, sizeof rx, FRAME_CLOSE, 3u, NULL, 0u);
    run("CLOSE сесія 3", rx, n, 1200u);
    n = build_frame(rx, sizeof rx, FRAME_OPEN, 9u, key, SESSION_KEY_LEN);
    run("OPEN сесія 9", rx, n, 1300u);

    /* 4. Кадр, більший за арену: підсистема відмовляє, пам'ять ціла. */
    n = build_frame(rx, sizeof rx, FRAME_DATA, 1u, blob, sizeof blob);
    run("DATA 1500 Б", rx, n, 1400u);

    /* 5. Обрубаний кадр. */
    run("уламок 3 Б", rx, 3u, 1500u);

    memory_report();
    return 0;
}
