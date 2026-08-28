/* Статус результату перехоплювача */
typedef enum {
    INTERCEPTOR_CONTINUE = 0,
    INTERCEPTOR_DROP = 1,
    INTERCEPTOR_ERROR = 2
} InterceptorResult;

/* Покажчик на функцію-перехоплювач */
typedef InterceptorResult (*InterceptorFunc)(MessageEnvelope* env, void* user_data);

/* 1. Перехоплювач валідації схеми */
InterceptorResult schema_validator_interceptor(MessageEnvelope* env, void* user_data) {
    uint32_t min_version = *(uint32_t*)user_data;
    if (env->schema_version < min_version) {
        printf("[Interceptor:Schema] ВІДХИЛЕНО: версія v%u застаріла (потрібна >= v%u)\n", 
               env->schema_version, min_version);
        return INTERCEPTOR_DROP;
    }
    printf("[Interceptor:Schema] OK: версія v%u сумісна\n", env->schema_version);
    return INTERCEPTOR_CONTINUE;
}

/* 2. Перехоплювач трасування та логування */
InterceptorResult tracing_logger_interceptor(MessageEnvelope* env, void* user_data) {
    (void)user_data;
    printf("[Interceptor:Tracing] Обробка [%s] Тема='%s' Trace='%s' Corr='%s'\n",
           env->message_id, env->topic, env->traceparent, env->correlation_id);
    return INTERCEPTOR_CONTINUE;
}

/* 3. Перехоплювач дедуплікації (кеш ідентифікаторів) */
typedef struct {
    char seen_ids[32][MAX_ID_LEN];
    size_t count;
} DedupCache;

InterceptorResult dedup_interceptor(MessageEnvelope* env, void* user_data) {
    DedupCache* cache = (DedupCache*)user_data;
    for (size_t i = 0; i < cache->count; ++i) {
        if (strcmp(cache->seen_ids[i], env->message_id) == 0) {
            printf("[Interceptor:Dedup] ВІДХИЛЕНО: дублікат повідомлення %s\n", env->message_id);
            return INTERCEPTOR_DROP;
        }
    }
    if (cache->count < 32) {
        strncpy(cache->seen_ids[cache->count++], env->message_id, MAX_ID_LEN - 1);
    }
    return INTERCEPTOR_CONTINUE;
}
