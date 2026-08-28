// command_loop.h — надійна доставка ОДНОЇ команди борту
#include <stdint.h>
#include <stdbool.h>
#include "mavlink.h"   // згенерований діалект (common / ardupilotmega)

typedef enum {
    CMD_IDLE = 0,      // немає активної команди
    CMD_WAITING,       // відправлено, чекаємо COMMAND_ACK
    CMD_DONE,          // прийнято й виконано (ACCEPTED)
    CMD_FAILED         // відхилено / не підтримано / вичерпано спроби
} cmd_state_t;

typedef struct {
    cmd_state_t state;

    // ── кого й що ми наказуємо (задається при старті команди) ──────────
    uint8_t  target_sys;    // SYS борту, якому шлемо
    uint8_t  target_comp;   // COMP на борту (1 = автопілот)
    uint16_t command;       // MAV_CMD_* — номер команди
    float    params[7];     // param1..param7 для COMMAND_LONG

    // ── лічильники повтору ─────────────────────────────────────────────
    uint8_t  confirmation;  // росте з кожним повтором (поле пакета)
    uint8_t  attempts_left; // скільки ще повторів дозволено
    uint32_t deadline_ms;   // абсолютний час, коли мовчанку вважати втратою

    // ── налаштування (розумні типові значення) ─────────────────────────
    uint32_t timeout_ms;    // базовий таймаут очікування ACK
    uint8_t  max_attempts;  // усього спроб (перша + повтори)

    // ── підсумок для оператора ─────────────────────────────────────────
    uint8_t  last_result;   // останній MAV_RESULT з ACK
    uint8_t  progress;      // 0..100 при IN_PROGRESS (UINT8_MAX = невідомо)
} cmd_loop_t;
