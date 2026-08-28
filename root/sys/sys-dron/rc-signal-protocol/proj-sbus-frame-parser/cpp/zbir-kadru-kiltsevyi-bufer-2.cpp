#define SBUS_LEN     25
#define SBUS_HEADER  0x0F
#define SBUS_FOOTER  0x00

typedef enum { ST_SEEK, ST_COLLECT } sbus_state_t;

typedef struct {
    sbus_state_t state;
    uint8_t frame[SBUS_LEN];
    uint8_t idx;              // скільки байтів кадру вже набрано
} sbus_parser_t;

static sbus_parser_t ps;

// Прожовує все, що накопичилось у кільцевому буфері. Коли зібрано цілий
// валідний кадр — кладе його в out_frame і повертає 1 (можна кликати
// повторно, доки вертає 1: за один прохід кадрів може набратися кілька).
int sbus_poll(uint8_t out_frame[SBUS_LEN]) {
    uint8_t b;
    while (rb_get(&b)) {
        switch (ps.state) {

        case ST_SEEK:
            // У пошуку старту викидаємо все, крім заголовка.
            if (b == SBUS_HEADER) {
                ps.frame[0] = b;
                ps.idx = 1;
                ps.state = ST_COLLECT;
            }
            break;

        case ST_COLLECT:
            ps.frame[ps.idx++] = b;
            if (ps.idx == SBUS_LEN) {
                // Кадр набрано повністю — перевіряємо хвіст.
                ps.state = ST_SEEK;               // хай там що — далі знову шукаємо старт
                if (ps.frame[SBUS_LEN - 1] == SBUS_FOOTER) {
                    for (int i = 0; i < SBUS_LEN; i++) out_frame[i] = ps.frame[i];
                    return 1;                     // валідний кадр
                }
                // Хвіст не 0x00 → десинхрон. Кадр викидаємо, лишаємось у SEEK.
            }
            break;
        }
    }
    return 0;   // цілого кадру поки нема
}
