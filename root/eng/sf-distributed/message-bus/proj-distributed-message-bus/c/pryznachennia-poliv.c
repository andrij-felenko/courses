#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define MAX_TOPIC_LEN 128
#define MAX_ID_LEN 64
#define MAX_PAYLOAD_SIZE 4096
#define MAX_INTERCEPTORS 8
#define MAX_SUBSCRIBERS 16

/* Структура канонічного конверта повідомлення на шині */
typedef struct {
    char message_id[MAX_ID_LEN];       /* Унікальний UUID повідомлення */
    char topic[MAX_TOPIC_LEN];         /* Ієрархічна тема: "orders.created" */
    char correlation_id[MAX_ID_LEN];   /* Ідентифікатор наскрізного процесу */
    char causation_id[MAX_ID_LEN];     /* ID повідомлення-причини */
    char traceparent[MAX_ID_LEN];      /* W3C Distributed Tracing заголовок */
    uint32_t schema_version;           /* Версія схеми даних (семантична) */
    uint64_t timestamp_us;             /* Часова мітка створення (мікросекунди) */
    
    uint8_t payload[MAX_PAYLOAD_SIZE]; /* Сире бінарне корисне навантаження */
    size_t payload_len;                /* Довжина корисного навантаження */
} MessageEnvelope;

/* Ініціалізація нового конверта */
void envelope_init(MessageEnvelope* env, const char* topic, const char* corr_id, uint32_t version) {
    static uint64_t id_seq = 1000;
    snprintf(env->message_id, MAX_ID_LEN, "msg_%llu", (unsigned long long)++id_seq);
    strncpy(env->topic, topic, MAX_TOPIC_LEN - 1);
    env->topic[MAX_TOPIC_LEN - 1] = '\0';
    
    if (corr_id && strlen(corr_id) > 0) {
        strncpy(env->correlation_id, corr_id, MAX_ID_LEN - 1);
    } else {
        strncpy(env->correlation_id, env->message_id, MAX_ID_LEN - 1);
    }
    env->correlation_id[MAX_ID_LEN - 1] = '\0';
    
    env->causation_id[0] = '\0';
    snprintf(env->traceparent, MAX_ID_LEN, "00-trace%llu-span01-01", (unsigned long long)id_seq);
    env->schema_version = version;
    env->timestamp_us = (uint64_t)time(NULL) * 1000000ULL;
    env->payload_len = 0;
}
