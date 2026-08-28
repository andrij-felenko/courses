#include <string.h>

// Ідентифікація НАШОЇ сторони (наземна станція чи борт-ретранслятор)
#define MY_SYS   255   // 255 — типовий SYS для GCS
#define MY_COMP  MAV_COMP_ID_MISSIONPLANNER   // 190; або свій COMP

// Абстракція виведення байтів у канал (UART / сокет / радіомодем).
// Реалізуй під свою платформу; повертає кількість відданих байтів.
extern int link_write(const uint8_t *buf, int len);

// Поточний монотонний час у мілісекундах (millis() на Arduino,
// HAL_GetTick() на STM32 тощо). МОНОТОННИЙ — не «час доби».
extern uint32_t now_ms(void);

// Відправити поточний наказ у канал зі значенням confirmation зі стану.
static void cmd_send_now(cmd_loop_t *c)
{
    mavlink_command_long_t cl = {0};
    cl.target_system    = c->target_sys;
    cl.target_component = c->target_comp;
    cl.command          = c->command;
    cl.confirmation     = c->confirmation;   // 0 на першому, ++ на повторах
    cl.param1 = c->params[0];  cl.param2 = c->params[1];
    cl.param3 = c->params[2];  cl.param4 = c->params[3];
    cl.param5 = c->params[4];  cl.param6 = c->params[5];
    cl.param7 = c->params[6];

    mavlink_message_t msg;
    mavlink_msg_command_long_encode(MY_SYS, MY_COMP, &msg, &cl);

    uint8_t buf[MAVLINK_MAX_PACKET_LEN];
    int len = mavlink_msg_to_send_buffer(buf, &msg);
    link_write(buf, len);

    c->deadline_ms = now_ms() + c->timeout_ms;  // засікли годинник очікування
}

// Запустити НОВУ команду. Повертає false, якщо цикл уже зайнятий.
bool cmd_start(cmd_loop_t *c, uint8_t sys, uint8_t comp,
               uint16_t command, const float params[7])
{
    if (c->state == CMD_WAITING)
        return false;                 // одна команда за раз на цей цикл

    c->target_sys   = sys;
    c->target_comp  = comp;
    c->command      = command;
    memcpy(c->params, params, sizeof(c->params));

    c->confirmation   = 0;            // перша передача
    c->attempts_left  = c->max_attempts - 1;  // одна спроба вже витрачається зараз
    c->last_result    = 0xFF;         // «поки невідомо»
    c->progress       = UINT8_MAX;
    c->state          = CMD_WAITING;

    cmd_send_now(c);                  // ← перший постріл, confirmation = 0
    return true;
}
