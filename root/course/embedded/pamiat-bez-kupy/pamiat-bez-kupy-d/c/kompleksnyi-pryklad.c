/* Приклад використання вбудованого диспетчера кадрів на мові C */

typedef struct {
    uint32_t session_id;
    uint32_t last_active_ms;
    uint8_t encryption_key[32];
} client_session_t;

/* Статичне розміщення пам'яті на етапі компіляції (0 байтів динамічної купи!) */
#define MAX_SESSIONS 8
#define FRAME_SCRATCH_SIZE 1024

static uint8_t s_session_pool_mem[MAX_SESSIONS * sizeof(client_session_t)];
static uint8_t s_frame_arena_mem[FRAME_SCRATCH_SIZE];

static fixed_pool_t s_session_pool;
static memory_arena_t s_frame_arena;

void system_memory_init(void) {
    pool_init(&s_session_pool, s_session_pool_mem, sizeof(client_session_t), MAX_SESSIONS);
    arena_init(&s_frame_arena, s_frame_arena_mem, FRAME_SCRATCH_SIZE);
}

/* Обробка кадру повідомлення */
bool process_incoming_frame(const uint8_t* raw_payload, size_t length) {
    /* 1. Початок транзакції кадру: скидаємо тимчасову арену */
    arena_reset(&s_frame_arena);

    /* 2. Виділяємо проміжні буфери з арени без ризику витоків */
    uint8_t* decrypted_buf = (uint8_t*)arena_alloc(&s_frame_arena, length);
    char* json_string = (char*)arena_alloc(&s_frame_arena, 256);
    if (!decrypted_buf || !json_string) {
        return false; /* Арена замала для цього пакета */
    }

    /* ... імітація дешифрування та парсингу ... */
    memcpy(decrypted_buf, raw_payload, length);

    /* 3. Якщо пакет вимагає створення нової постійної сесії — беремо слот з пула */
    bool is_new_connection = (raw_payload[0] == 0x01);
    if (is_new_connection) {
        client_session_t* session = (client_session_t*)pool_alloc(&s_session_pool);
        if (!session) {
            return false; /* Пул активних сесій заповнений */
        }
        session->session_id = 1001;
        session->last_active_ms = 12000;
        memcpy(session->encryption_key, decrypted_buf, 32);
    }

    /* 4. Завершення обробки кадру: тимчасова пам'ять автоматично зникає
          при наступному виклику arena_reset(). Жодних free() не потрібно! */
    return true;
}
