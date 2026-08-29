#ifndef ACTUATOR_H
#define ACTUATOR_H

/* Виконавча частина: реле, крокова каретка, дозувальний насос, калібрування.
 * Головна властивість — НЕБЛОКУЮЧІСТЬ: actuator_start() лише подає струм і
 * повертається, а завершення ловить actuator_poll() з головного циклу. Саме
 * тому фаза 2 квитування асинхронна: у момент прийому пакета результату ще
 * не існує. Тут привід змодельовано, але інтерфейс той самий, що й у драйвера
 * з переривання по кінцевику. */

#include <stdint.h>
#include <stdbool.h>

#include "cmd_proto.h"

#define ACT_STEP_RATE_HZ   400    /* кроків на секунду */
#define ACT_DISPENSE_MS_ML 100    /* мілісекунд на мілілітр */
#define ACT_CALIBRATE_MS   1500

typedef enum {
    ACT_IDLE = 0,
    ACT_BUSY,
    ACT_DONE,
    ACT_FAILED
} act_status_t;

typedef struct {
    act_status_t status;
    int32_t      detail;   /* досягнута позиція, налита доза, зміряний зсув */
    int32_t      error;    /* cmd_err_t при ACT_FAILED */
} act_result_t;

void actuator_init(void);

/* Подати команду на залізо. Повертає E_OK, якщо рух почався (або миттєва
 * дія вже виконана), інакше — причину відмови ще до подачі струму. */
cmd_err_t actuator_start(uint8_t type, const uint8_t *payload, uint8_t len);

/* Опитування з головного циклу. Термінальний результат віддається РІВНО
 * ОДИН раз, після чого привід повертається в ACT_IDLE. */
act_result_t actuator_poll(void);

/* Аварійна зупинка: знімає струм із драйвера, лишаючи механізм там, де він є. */
void actuator_abort(void);

/* Гомінг після невизначеного стану (наприклад, після скидання живлення). */
void actuator_home(void);

int32_t actuator_position(void);

/* Керування моделлю заліза для сценаріїв заняття. */
void actuator_set_supply_ok(bool ok);
void actuator_set_stall_at(int32_t position);   /* INT32_MIN — перешкоди немає */

#endif /* ACTUATOR_H */
