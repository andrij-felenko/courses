// Шлях 1: стоп іде тією самою чергою, що й усі команди й телеметрія.
// Простий і дешевий — але час спрацювання НЕ гарантований під навантаженням.

typedef enum { CMD_THROTTLE, CMD_ARM, CMD_STOP, CMD_TELEM_REQ } cmd_kind_t;

typedef struct {
    cmd_kind_t kind;
    int16_t    payload;
} command_t;

static RingBuffer  g_cmd_queue;   // спільна черга: сюди падають І команди, І запити телеметрії

// Викликається з ISR радіо: команда лише кладеться в чергу, не виконується тут.
void radio_isr(void) {
    command_t c;
    if (radio_read(&c)) {
        ring_push(&g_cmd_queue, &c);   // «стоп» лягає в хвіст — за всім, що вже в черзі
    }
}

// Головний цикл обробника: одна команда за прохід. Поки він серіалізує
// телеметрію (довгий UART-кадр), черга стоїть — і «стоп» чекає разом з усіма.
void command_loop(void) {
    command_t c;
    while (ring_pop(&g_cmd_queue, &c)) {
        switch (c.kind) {
            case CMD_STOP:      motors_set_all(0);          break;
            case CMD_THROTTLE:  motors_set_throttle(c.payload); break;
            case CMD_TELEM_REQ: telemetry_send_frame();     break;  // ← тримає UART ~44 мс
            case CMD_ARM:       motors_arm();               break;
        }
    }
}
