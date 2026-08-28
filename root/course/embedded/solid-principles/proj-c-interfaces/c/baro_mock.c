// baro_mock.c — реалізація baro_t без заліза: віддає сценарій по кроках (для тестів).
#include "baro.h"

// Один крок сценарію: який код повернути і (якщо OK) яке значення тиску.
typedef struct {
    baro_status_t status;
    uint32_t      pa;
} baro_step_t;

typedef struct {
    baro_t             base;
    const baro_step_t *script;   // масив кроків, заданий тестом
    int                len;      // скільки кроків у сценарії
    int                i;        // індекс наступного кроку
    int                calls;    // лічильник викликів read (для перевірок у тесті)
} baro_mock_t;

static baro_status_t mock_read(baro_t *self, uint32_t *out_pa) {
    baro_mock_t *m = (baro_mock_t *)self;
    m->calls++;
    if (m->i >= m->len) {
        return BARO_ERR_BUS;            // сценарій вичерпано — поводимось як мертва шина
    }
    baro_step_t step = m->script[m->i++];
    if (step.status == BARO_OK) {
        *out_pa = step.pa;             // чіпаємо вихід лише на OK — як справжні драйвери
    }
    return step.status;                // віддаємо запланований код (зокрема й помилку)
}

static void mock_close(baro_t *self) { (void)self; }   // нічого не тримаємо

static const baro_vtable_t MOCK_VT = { .read = mock_read, .close = mock_close };

// Ініціалізувати мок заданим сценарієм. Без malloc — структуру дає тест на стеку.
void baro_mock_init(baro_mock_t *m, const baro_step_t *script, int len) {
    m->base.vt = &MOCK_VT;
    m->script  = script;
    m->len     = len;
    m->i       = 0;
    m->calls   = 0;
}
