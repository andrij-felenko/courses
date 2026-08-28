#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

#define SCENARIO_MAX_STEPS       16
#define SCENARIO_ROLLBACK_STACK  16

/* Статуси виконання сценарію */
typedef enum {
    SCENARIO_IDLE = 0,
    SCENARIO_RUNNING,
    SCENARIO_SUCCESS,
    SCENARIO_FAILED,
    SCENARIO_ROLLING_BACK,
    SCENARIO_ABORTED_SAFE
} ScenarioState;

/* Коди помилок виконання */
typedef enum {
    SCENARIO_ERR_NONE = 0,
    SCENARIO_ERR_PRECONDITION,
    SCENARIO_ERR_TIMEOUT,
    SCENARIO_ERR_INVARIANT,
    SCENARIO_ERR_USER_ABORT
} ScenarioError;

/* Фази життєвого циклу окремого кроку */
typedef enum {
    STEP_STATE_IDLE = 0,
    STEP_STATE_PRECHECK,
    STEP_STATE_ENTER,
    STEP_STATE_EXECUTING,
    STEP_STATE_DONE
} StepState;

/* Типи функціональних покажчиків */
typedef void (*ActionFn)(void* ctx);
typedef bool (*PredicateFn)(void* ctx);

/* Структура декларативного кроку сценарію */
typedef struct {
    const char*   name;              /* Назва кроку для логування */
    ActionFn      action;            /* Дія активації */
    PredicateFn   precondition;      /* Передумова (може бути NULL) */
    PredicateFn   postcondition;     /* Постумова (може бути NULL) */
    ActionFn      rollback;          /* Компенсаційна дія при відкаті (може бути NULL) */
    uint32_t      timeout_ms;        /* Таймаут досягнення постумови */
    uint32_t      settle_delay_ms;   /* Затримка стабілізації перед перевіркою */
} ScenarioStep;

/* Дескриптор рушія сценаріїв */
typedef struct {
    const ScenarioStep* steps;
    size_t              step_count;
    size_t              current_step_idx;
    ScenarioState       state;
    ScenarioError       last_error;
    StepState           step_phase;
    uint32_t            step_start_ms;
    void*               context;
    PredicateFn         invariant_checker; /* Наскрізний інваріант безпеки */

    /* Стек дій відкату (LIFO) */
    ActionFn            rollback_stack[SCENARIO_ROLLBACK_STACK];
    size_t              rollback_count;
    size_t              rollback_current_idx;
} ScenarioEngine;

/* Ініціалізація рушія */
void scenario_init(ScenarioEngine* engine, void* context, PredicateFn invariant_checker) {
    if (!engine) return;
    engine->steps = NULL;
    engine->step_count = 0;
    engine->current_step_idx = 0;
    engine->state = SCENARIO_IDLE;
    engine->last_error = SCENARIO_ERR_NONE;
    engine->step_phase = STEP_STATE_IDLE;
    engine->step_start_ms = 0;
    engine->context = context;
    engine->invariant_checker = invariant_checker;
    engine->rollback_count = 0;
    engine->rollback_current_idx = 0;
}

/* Запуск сценарію на виконання */
bool scenario_start(ScenarioEngine* engine, const ScenarioStep* steps, size_t count, uint32_t now_ms) {
    if (!engine || !steps || count == 0 || count > SCENARIO_MAX_STEPS) {
        return false;
    }
    if (engine->state == SCENARIO_RUNNING || engine->state == SCENARIO_ROLLING_BACK) {
        return false; /* Захист від повторного входу (Reentrancy) */
    }

    engine->steps = steps;
    engine->step_count = count;
    engine->current_step_idx = 0;
    engine->state = SCENARIO_RUNNING;
    engine->last_error = SCENARIO_ERR_NONE;
    engine->step_phase = STEP_STATE_PRECHECK;
    engine->step_start_ms = now_ms;
    engine->rollback_count = 0;
    engine->rollback_current_idx = 0;
    return true;
}

/* Примусове скасування сценарію з відкатом */
void scenario_abort(ScenarioEngine* engine, ScenarioError error) {
    if (!engine || engine->state != SCENARIO_RUNNING) return;
    engine->state = SCENARIO_ROLLING_BACK;
    engine->last_error = error;
    engine->rollback_current_idx = engine->rollback_count;
}

/* Періодичний неблокуючий тік рушія */
void scenario_tick(ScenarioEngine* engine, uint32_t now_ms) {
    if (!engine) return;

    /* Обробка фази відкату (Rollback Execution) */
    if (engine->state == SCENARIO_ROLLING_BACK) {
        if (engine->rollback_current_idx > 0) {
            engine->rollback_current_idx--;
            ActionFn undo_action = engine->rollback_stack[engine->rollback_current_idx];
            if (undo_action) {
                undo_action(engine->context);
            }
        } else {
            engine->state = SCENARIO_ABORTED_SAFE;
        }
        return;
    }

    if (engine->state != SCENARIO_RUNNING) {
        return;
    }

    /* 1. Перевірка наскрізних інваріантів безпеки */
    if (engine->invariant_checker && !engine->invariant_checker(engine->context)) {
        scenario_abort(engine, SCENARIO_ERR_INVARIANT);
        return;
    }

    const ScenarioStep* step = &engine->steps[engine->current_step_idx];

    switch (engine->step_phase) {
        case STEP_STATE_PRECHECK:
            if (step->precondition && !step->precondition(engine->context)) {
                scenario_abort(engine, SCENARIO_ERR_PRECONDITION);
                return;
            }
            engine->step_phase = STEP_STATE_ENTER;
            /* Продовжуємо виконання без затримки на наступний блок */
            __attribute__((fallthrough));

        case STEP_STATE_ENTER:
            if (step->action) {
                step->action(engine->context);
            }
            /* Реєстрація компенсатора у LIFO стеку */
            if (step->rollback && engine->rollback_count < SCENARIO_ROLLBACK_STACK) {
                engine->rollback_stack[engine->rollback_count++] = step->rollback;
            }
            engine->step_start_ms = now_ms;
            engine->step_phase = STEP_STATE_EXECUTING;
            break;

        case STEP_STATE_EXECUTING: {
            uint32_t elapsed_ms = (uint32_t)(now_ms - engine->step_start_ms);

            /* Перевірка таймауту виконання кроку */
            if (step->timeout_ms > 0 && elapsed_ms >= step->timeout_ms) {
                scenario_abort(engine, SCENARIO_ERR_TIMEOUT);
                return;
            }

            /* Перевірка витримки часу стабілізації */
            if (elapsed_ms < step->settle_delay_ms) {
                return; /* Очікуємо завершення перехідного процесу */
            }

            /* Перевірка постумови */
            bool step_done = true;
            if (step->postcondition) {
                step_done = step->postcondition(engine->context);
            }

            if (step_done) {
                engine->current_step_idx++;
                if (engine->current_step_idx >= engine->step_count) {
                    engine->state = SCENARIO_SUCCESS;
                    engine->rollback_count = 0; /* Очищення стека після повного успіху */
                } else {
                    engine->step_phase = STEP_STATE_PRECHECK;
                }
            }
            break;
        }

        default:
            engine->state = SCENARIO_FAILED;
            break;
    }
}
