extern uint32_t millis(void);          // монотонний час у мілісекундах
extern void     uart_write(uint8_t);

#define RPC_TIMEOUT_MS  50u            // скільки чекати відповідь
#define RPC_RETRIES     3u             // скільки разів повторити запит

// Стан клієнтського виклику.
typedef enum {
    CALL_IDLE,        // вільний — можна починати новий виклик
    CALL_WAITING,     // запит відіслано, чекаємо відповідь або таймаут
    CALL_DONE,        // відповідь прийшла — value готове
    CALL_FAILED,      // вичерпали повтори — віддалена сторона мовчить
} call_state_t;

typedef struct {
    call_state_t state;
    uint8_t      id;            // ID цього виклику (для звірки відповіді)
    uint8_t      func;          // що викликали (на випадок повтору)
    int32_t      arg;
    uint32_t     t_sent;        // коли востаннє відіслали запит
    uint8_t      tries;         // скільки разів уже слали
    int32_t      value;         // результат (значущий при CALL_DONE)
    uint8_t      status;        // код результату з відповіді
} rpc_call_t;

static rpc_call_t g_call = { CALL_IDLE };
static uint8_t    g_next_id = 1;       // лічильник ID запитів (по колу)
