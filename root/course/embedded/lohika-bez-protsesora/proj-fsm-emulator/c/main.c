#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <assert.h>

/* Кодування станів автомата */
typedef enum {
    STATE_IDLE   = 0, /* 00: Очікування */
    STATE_PURGE  = 1, /* 01: Продування камери */
    STATE_IGNITE = 2, /* 10: Розпал та перевірка полум'я */
    STATE_RUN    = 3  /* 11: Штатна робота */
} fsm_state_t;

/* Вхідні сигнали автомата */
typedef struct {
    bool start; /* Кнопка пуску */
    bool done;  /* Сигнал завершення продувки від таймера */
    bool flame; /* Оптичний давач наявності полум'я */
    bool abort; /* Аварійний стоп / скидання */
} fsm_inputs_t;

/* Вихідні силові сигнали моделі Мура */
typedef struct {
    bool fan;   /* Вентилятор примусової тяги */
    bool valve; /* Електромагнітний клапан газу */
    bool spark; /* Високовольтний запальник */
    bool ok;    /* Індикатор нормальної роботи */
} fsm_outputs_t;

/* -------------------------------------------------------------
 * 1. Високорівнева еталонна модель (Golden Model)
 * ------------------------------------------------------------- */
typedef struct {
    fsm_state_t state;
} golden_fsm_t;

void golden_fsm_init(golden_fsm_t *fsm) {
    fsm->state = STATE_IDLE;
}

fsm_outputs_t golden_fsm_get_outputs(const golden_fsm_t *fsm) {
    fsm_outputs_t out = {0};
    switch (fsm->state) {
        case STATE_IDLE:
            out.fan = false; out.valve = false; out.spark = false; out.ok = false;
            break;
        case STATE_PURGE:
            out.fan = true;  out.valve = false; out.spark = false; out.ok = false;
            break;
        case STATE_IGNITE:
            out.fan = true;  out.valve = true;  out.spark = true;  out.ok = false;
            break;
        case STATE_RUN:
            out.fan = true;  out.valve = true;  out.spark = false; out.ok = true;
            break;
    }
    return out;
}

void golden_fsm_tick(golden_fsm_t *fsm, fsm_inputs_t in) {
    if (in.abort) {
        fsm->state = STATE_IDLE;
        return;
    }
    switch (fsm->state) {
        case STATE_IDLE:
            if (in.start) fsm->state = STATE_PURGE;
            break;
        case STATE_PURGE:
            if (in.done) fsm->state = STATE_IGNITE;
            break;
        case STATE_IGNITE:
            if (in.flame) fsm->state = STATE_RUN;
            else fsm->state = STATE_IDLE; /* Зрив запалювання */
            break;
        case STATE_RUN:
            if (!in.flame) fsm->state = STATE_IDLE; /* Згасання полум'я */
            break;
    }
}

/* -------------------------------------------------------------
 * 2. Повентильний емулятор дискретної схеми 74HC
 * ------------------------------------------------------------- */
typedef struct {
    bool q1; /* Старший D-тригер (IC1B) */
    bool q0; /* Молодший D-тригер (IC1A) */
} discrete_fsm_t;

void discrete_fsm_init(discrete_fsm_t *fsm) {
    fsm->q1 = false;
    fsm->q0 = false;
}

fsm_outputs_t discrete_fsm_get_outputs(const discrete_fsm_t *fsm) {
    fsm_outputs_t out;
    /* Дешифратор виходів Мура на вентилях:
     * Fan   = Q1 OR Q0
     * Valve = Q1
     * Spark = Q1 AND NOT(Q0)
     * Ok    = Q1 AND Q0
     */
    out.fan   = fsm->q1 || fsm->q0;
    out.valve = fsm->q1;
    out.spark = fsm->q1 && !fsm->q0;
    out.ok    = fsm->q1 && fsm->q0;
    return out;
}

void discrete_fsm_tick(discrete_fsm_t *fsm, fsm_inputs_t in) {
    bool q1 = fsm->q1;
    bool q0 = fsm->q0;

    /* Рівняння комбінаційної логіки наступного стану:
     * D1 = (NOT(Q1) AND Q0 AND Done) OR (Q1 AND Flame AND NOT(Abort))
     * D0 = (NOT(Q1) AND NOT(Q0) AND Start AND NOT(Abort)) OR
     *      (NOT(Q1) AND Q0 AND NOT(Done) AND NOT(Abort)) OR
     *      (Q1 AND NOT(Q0) AND Flame AND NOT(Abort))
     */
    bool d1 = (!q1 && q0 && in.done && !in.abort) ||
              (q1 && in.flame && !in.abort);

    bool d0 = (!q1 && !q0 && in.start && !in.abort) ||
              (!q1 && q0 && !in.done && !in.abort) ||
              (q1 && !q0 && in.flame && !in.abort);

    /* Тактовий фронт: засувка в D-тригери 74HC74 */
    fsm->q1 = d1;
    fsm->q0 = d0;
}

/* -------------------------------------------------------------
 * 3. Тестова верифікація та порівняння такт за тактом
 * ------------------------------------------------------------- */
int main(void) {
    golden_fsm_t golden;
    discrete_fsm_t discrete;

    golden_fsm_init(&golden);
    discrete_fsm_init(&discrete);

    /* Тестовий сценарій: успішний пуск -> робота -> аварійний зрив полум'я */
    fsm_inputs_t test_vectors[] = {
        { .start = false, .done = false, .flame = false, .abort = false }, /* Такт 0: IDLE */
        { .start = true,  .done = false, .flame = false, .abort = false }, /* Такт 1: Пуск -> PURGE */
        { .start = false, .done = false, .flame = false, .abort = false }, /* Такт 2: Продувка триває */
        { .start = false, .done = true,  .flame = false, .abort = false }, /* Такт 3: Продувка завершена -> IGNITE */
        { .start = false, .done = false, .flame = true,  .abort = false }, /* Такт 4: Полум'я є -> RUN */
        { .start = false, .done = false, .flame = true,  .abort = false }, /* Такт 5: Стабільна робота */
        { .start = false, .done = false, .flame = false, .abort = false }, /* Такт 6: Згасання полум'я -> IDLE */
        { .start = false, .done = false, .flame = false, .abort = false }  /* Такт 7: Повернення в IDLE */
    };

    size_t num_steps = sizeof(test_vectors) / sizeof(test_vectors[0]);

    for (size_t step = 0; step < num_steps; ++step) {
        fsm_inputs_t in = test_vectors[step];

        fsm_outputs_t out_g = golden_fsm_get_outputs(&golden);
        fsm_outputs_t out_d = discrete_fsm_get_outputs(&discrete);

        uint8_t state_d = (discrete.q1 ? 2 : 0) | (discrete.q0 ? 1 : 0);

        /* Перевірка повної відповідності стану та виходів */
        assert((uint8_t)golden.state == state_d);
        assert(out_g.fan == out_d.fan);
        assert(out_g.valve == out_d.valve);
        assert(out_g.spark == out_d.spark);
        assert(out_g.ok == out_d.ok);

        /* Такт годинника */
        golden_fsm_tick(&golden, in);
        discrete_fsm_tick(&discrete, in);
    }

    return 0;
}
