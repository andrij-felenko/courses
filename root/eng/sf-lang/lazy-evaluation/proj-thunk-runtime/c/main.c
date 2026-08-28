#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Стани життєвого циклу санка
typedef enum {
    THUNK_UNTOUCHED,   // Необчислений: містить функцію та оточення
    THUNK_EVALUATING,  // Blackhole: обчислюється прямо зараз (захист від циклів)
    THUNK_EVALUATED    // Обчислений: вузол мутовано, містить готове значення
} ThunkState;

typedef struct Thunk Thunk;

// Сигнатура функції обчислення: приймає вказівник на оточення, повертає ціле число
typedef long long (*ComputeFn)(void *env);
typedef void (*FreeEnvFn)(void *env);

struct Thunk {
    ThunkState state;
    union {
        struct {
            ComputeFn fn;
            void *env;
            FreeEnvFn free_env;
        } unevaluated;
        long long value;
    } data;
    size_t ref_count; // Лічильник посилань для спільного володіння
};

// Створення нового санка
Thunk* thunk_create(ComputeFn fn, void *env, FreeEnvFn free_env) {
    Thunk *t = (Thunk*)malloc(sizeof(Thunk));
    if (!t) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    t->state = THUNK_UNTOUCHED;
    t->data.unevaluated.fn = fn;
    t->data.unevaluated.env = env;
    t->data.unevaluated.free_env = free_env;
    t->ref_count = 1;
    return t;
}

// Створення вже готового значення (оптимізація для констант)
Thunk* thunk_value(long long val) {
    Thunk *t = (Thunk*)malloc(sizeof(Thunk));
    if (!t) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    t->state = THUNK_EVALUATED;
    t->data.value = val;
    t->ref_count = 1;
    return t;
}

// Форсування санка (Force / Eval)
long long thunk_force(Thunk *t) {
    if (!t) return 0;

    // Швидкий шлях: значення вже готове (O(1) читання з пам'яті)
    if (t->state == THUNK_EVALUATED) {
        return t->data.value;
    }

    // Захист від зациклення: якщо ми зайшли в той самий санк двічі
    if (t->state == THUNK_EVALUATING) {
        fprintf(stderr, "[Runtime Error] <<loop>>: виявлено пряму циклічну залежність санка!\n");
        exit(EXIT_FAILURE);
    }

    // Перехід у стан Blackhole
    t->state = THUNK_EVALUATING;
    ComputeFn fn = t->data.unevaluated.fn;
    void *env = t->data.unevaluated.env;
    FreeEnvFn free_env = t->data.unevaluated.free_env;

    // Виконання обчислення
    long long res = fn(env);

    // Звільнення захопленого оточення (GC promptness)
    if (free_env && env) {
        free_env(env);
    }

    // Мутація вузла графа на місці (Update)
    t->state = THUNK_EVALUATED;
    t->data.value = res;

    return res;
}

Thunk* thunk_retain(Thunk *t) {
    if (t) t->ref_count++;
    return t;
}

void thunk_release(Thunk *t) {
    if (!t) return;
    if (--t->ref_count == 0) {
        if (t->state == THUNK_UNTOUCHED && t->data.unevaluated.free_env && t->data.unevaluated.env) {
            t->data.unevaluated.free_env(t->data.unevaluated.env);
        }
        free(t);
    }
}

// --- Лінивий нескінченний потік (Lazy Stream) ---
typedef struct StreamNode StreamNode;

struct StreamNode {
    long long head;
    Thunk *tail_thunk; // Санк, що повертає наступний (StreamNode*)
};

typedef struct {
    long long a;
    long long b;
} FibEnv;

long long fib_stream_compute(void *env_ptr);

Thunk* make_fib_thunk(long long a, long long b) {
    FibEnv *env = (FibEnv*)malloc(sizeof(FibEnv));
    env->a = a;
    env->b = b;
    return thunk_create(fib_stream_compute, env, free);
}

static size_t g_eval_count = 0;

long long fib_stream_compute(void *env_ptr) {
    g_eval_count++;
    FibEnv *env = (FibEnv*)env_ptr;
    long long current = env->a;
    long long next = env->b;

    StreamNode *node = (StreamNode*)malloc(sizeof(StreamNode));
    node->head = current;
    node->tail_thunk = make_fib_thunk(next, current + next);

    // Повертаємо адресу вузла у вигляді цілого числа (вказівник)
    return (long long)node;
}

// Взяття перших N елементів зі списку
void stream_take(Thunk *stream_thunk, size_t n) {
    Thunk *curr_thunk = thunk_retain(stream_thunk);
    printf("Перші %zu чисел Фібоначчі: [", n);

    for (size_t i = 0; i < n; i++) {
        StreamNode *node = (StreamNode*)thunk_force(curr_thunk);
        printf("%lld%s", node->head, (i + 1 < n) ? ", " : "");

        Thunk *next_thunk = thunk_retain(node->tail_thunk);
        thunk_release(curr_thunk);
        curr_thunk = next_thunk;
    }
    printf("]\n");
    thunk_release(curr_thunk);
}

int main(void) {
    printf("=== Демонстрація рушія санків на C ===\n");

    // 1. Створення нескінченного потоку Фібоначчі: fib(0, 1)
    Thunk *fibs = make_fib_thunk(0, 1);

    // 2. Беремо перші 10 елементів
    stream_take(fibs, 10);
    printf("Кількість реальних обчислень вузлів: %zu (точно 10)\n", g_eval_count);

    // 3. Беремо перші 5 елементів з ТОГО САМОГО потоку (перевірка мемоізації)
    size_t prev_evals = g_eval_count;
    stream_take(fibs, 5);
    printf("Нових обчислень для перших 5 вузлів: %zu (всі взяті з кешу!)\n", g_eval_count - prev_evals);

    thunk_release(fibs);
    return 0;
}
