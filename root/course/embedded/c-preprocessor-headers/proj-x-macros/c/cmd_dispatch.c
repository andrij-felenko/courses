// cmd_dispatch.c
#include "cmd.h"

typedef void (*cmd_handler_t)(const uint8_t *payload, uint16_t len);

// Оголошення обробників — теж можна згенерувати зі списку, щоб не забути жодного.
#define X(code, id, name, handler)   void handler(const uint8_t *, uint16_t);
CMD_TABLE(X)
#undef X

// Сама таблиця: [код] → функція.
#define X(code, id, name, handler)   [CMD_##id] = handler,
static const cmd_handler_t CMD_HANDLER[] = {
    CMD_TABLE(X)
};
#undef X

// Диспетчер: за прийнятим байтом знайти й викликати обробник.
void cmd_dispatch(cmd_id_t id, const uint8_t *payload, uint16_t len) {
    if ((unsigned)id >= (sizeof CMD_HANDLER / sizeof CMD_HANDLER[0])
        || !CMD_HANDLER[id]) {
        log_printf("невідома команда 0x%02X\n", id);   // не падаємо на дірі
        return;
    }
    CMD_HANDLER[id](payload, len);
}
