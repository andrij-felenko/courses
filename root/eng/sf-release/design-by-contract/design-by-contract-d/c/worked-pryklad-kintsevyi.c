#include <assert.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PROTO_CAP 256

typedef enum { ST_IDLE, ST_HEADER, ST_BODY, ST_DONE, ST_COUNT } proto_state_t;

typedef struct {
    proto_state_t state;
    uint8_t  body[PROTO_CAP];
    uint16_t body_len;        // оголошена в заголовку довжина тіла
    uint16_t got;             // скільки байтів тіла вже прийнято
} proto_t;

// ІНВАРІАНТ МОДУЛЯ: зв'язує стан і дані в узгоджений стан.
// Те, що мусить бути істинним на КОЖНІЙ межі публічного API.
static bool proto_invariant(const proto_t *fsm) {
    if (fsm->state >= ST_COUNT) return false;       // стан завжди дозволений
    if (fsm->body_len > PROTO_CAP) return false;    // довжина в межах ємності
    if (fsm->got > fsm->body_len)  return false;    // прийнято не більше за оголошене
    // у стані BODY ще не добрали тіло; у DONE — добрали рівно стільки, скільки треба
    if (fsm->state == ST_BODY && fsm->got >= fsm->body_len) return false;
    if (fsm->state == ST_DONE && fsm->got != fsm->body_len) return false;
    return true;
}

// Публічний метод: згодувати автомату один байт тіла.
// Передумова: ми справді в стані прийому тіла. Постумова: лічильник зріс на 1,
// а стан коректно перейшов у DONE рівно тоді, коли тіло добране.
esp_err_t proto_feed_body(proto_t *fsm, uint8_t byte) {
    // ПЕРЕДУМОВА — борг викликача: годувати тіло можна лише у стані BODY.
    assert(fsm != NULL);
    assert(proto_invariant(fsm));            // інваріант на ВХОДІ
    assert(fsm->state == ST_BODY);           // передумова стану

    uint16_t got_before = fsm->got;          // знімок «до» руками (немає `old`)

    fsm->body[fsm->got] = byte;              // ← тут інваріант на мить «в дорозі»:
    fsm->got++;                              //   got зріс, а стан ще ST_BODY...
    if (fsm->got == fsm->body_len) {         //   ...і якщо тіло добране —
        fsm->state = ST_DONE;                //   відновлюємо узгодженість переходом
    }

    // ПОСТУМОВА — борг функції: рівно на один байт більше, і стан узгоджено.
    assert(fsm->got == got_before + 1);
    assert(proto_invariant(fsm));            // інваріант на ВИХОДІ
    return ESP_OK;
}
