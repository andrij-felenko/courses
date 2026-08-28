#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

/* Універсальний тип замикання: приймає int, повертає int */
typedef int (*int_invoke_fn)(void *env, int arg);
typedef void (*int_destroy_fn)(void *env);

typedef struct {
    int_invoke_fn  invoke;   /* покажчик на машинний код перехідника */
    void          *env;      /* покажчик на блок захоплених змінних */
    int_destroy_fn destroy;  /* деструктор для очищення оточення */
} int_closure_t;

/* Виклик замикання через розпакування оточення */
static inline int closure_call(const int_closure_t *c, int arg) {
    return c->invoke(c->env, arg);
}

/* Звільнення ресурсів замикання */
static inline void closure_free(int_closure_t *c) {
    if (c->destroy && c->env) {
        c->destroy(c->env);
        c->env = NULL;
    }
}

/* =========================================================================
 * Приклад: Фабрика замикань-накопичувачів (Stateful Accumulator)
 * ========================================================================= */

typedef struct {
    int current_sum;
    int step_multiplier;
} accumulator_env_t;

/* Статична функція виклику: знає точну структуру оточення */
static int accumulator_invoke(void *raw_env, int val) {
    accumulator_env_t *env = (accumulator_env_t *)raw_env;
    env->current_sum += val * env->step_multiplier;
    return env->current_sum;
}

/* Деструктор середовища */
static void accumulator_destroy(void *raw_env) {
    free(raw_env);
}

/* Функція-фабрика, що повертає замикання на купі (Upward Funarg) */
int_closure_t make_accumulator(int initial_val, int multiplier) {
    accumulator_env_t *env = (accumulator_env_t *)malloc(sizeof(accumulator_env_t));
    if (!env) {
        perror("malloc failed");
        exit(EXIT_FAILURE);
    }
    env->current_sum = initial_val;
    env->step_multiplier = multiplier;

    int_closure_t c = {
        .invoke = accumulator_invoke,
        .env = env,
        .destroy = accumulator_destroy
    };
    return c;
}

int main(void) {
    /* Створюємо два незалежні екземпляри замикання зі своїм станом */
    int_closure_t acc1 = make_accumulator(10, 1);  /* стартує з 10, множник 1 */
    int_closure_t acc2 = make_accumulator(0, 10);  /* стартує з 0, множник 10 */

    printf("acc1(5)  -> %d (очікувано: 15)\n", closure_call(&acc1, 5));
    printf("acc1(3)  -> %d (очікувано: 18)\n", closure_call(&acc1, 3));

    printf("acc2(2)  -> %d (очікувано: 20)\n", closure_call(&acc2, 2));
    printf("acc2(4)  -> %d (очікувано: 60)\n", closure_call(&acc2, 4));

    /* Повторний виклик acc1 підтверджує повну ізольованість пам'яті */
    printf("acc1(2)  -> %d (очікувано: 20)\n", closure_call(&acc1, 2));

    closure_free(&acc1);
    closure_free(&acc2);
    return 0;
}
