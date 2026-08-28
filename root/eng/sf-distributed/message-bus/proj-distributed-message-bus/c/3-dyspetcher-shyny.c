/* Обробник підписника */
typedef void (*MessageHandler)(const MessageEnvelope* env, void* subscriber_context);

typedef struct {
    char topic_pattern[MAX_TOPIC_LEN];
    MessageHandler handler;
    void* context;
} Subscription;

/* Ядро шини повідомлень */
typedef struct {
    Subscription subscriptions[MAX_SUBSCRIBERS];
    size_t sub_count;
    
    InterceptorFunc interceptors[MAX_INTERCEPTORS];
    void* interceptor_contexts[MAX_INTERCEPTORS];
    size_t interceptor_count;
} MessageBus;

void bus_init(MessageBus* bus) {
    bus->sub_count = 0;
    bus->interceptor_count = 0;
}

void bus_add_interceptor(MessageBus* bus, InterceptorFunc fn, void* ctx) {
    if (bus->interceptor_count < MAX_INTERCEPTORS) {
        bus->interceptors[bus->interceptor_count] = fn;
        bus->interceptor_contexts[bus->interceptor_count] = ctx;
        bus->interceptor_count++;
    }
}

void bus_subscribe(MessageBus* bus, const char* pattern, MessageHandler handler, void* ctx) {
    if (bus->sub_count < MAX_SUBSCRIBERS) {
        strncpy(bus->subscriptions[bus->sub_count].topic_pattern, pattern, MAX_TOPIC_LEN - 1);
        bus->subscriptions[bus->sub_count].handler = handler;
        bus->subscriptions[bus->sub_count].context = ctx;
        bus->sub_count++;
    }
}

/* Перевірка збігу теми з шаблоном (підтримка exact match та prefix.*) */
bool topic_matches(const char* pattern, const char* topic) {
    size_t p_len = strlen(pattern);
    if (p_len > 1 && pattern[p_len - 1] == '*' && pattern[p_len - 2] == '.') {
        /* Шаблон "prefix.*" */
        return strncmp(pattern, topic, p_len - 2) == 0;
    }
    return strcmp(pattern, topic) == 0;
}

/* Публікація повідомлення на шину */
bool bus_publish(MessageBus* bus, MessageEnvelope* env) {
    /* 1. Прогін через конвеєр перехоплювачів */
    for (size_t i = 0; i < bus->interceptor_count; ++i) {
        InterceptorResult res = bus->interceptors[i](env, bus->interceptor_contexts[i]);
        if (res != INTERCEPTOR_CONTINUE) {
            return false; /* Повідомлення відхилено перехоплювачем */
        }
    }
    
    /* 2. Маршрутизація підписникам */
    size_t delivered = 0;
    for (size_t i = 0; i < bus->sub_count; ++i) {
        if (topic_matches(bus->subscriptions[i].topic_pattern, env->topic)) {
            bus->subscriptions[i].handler(env, bus->subscriptions[i].context);
            delivered++;
        }
    }
    printf("[Bus:Router] Повідомлення '%s' успішно доставлено %zu підписникам\n", env->topic, delivered);
    return true;
}
