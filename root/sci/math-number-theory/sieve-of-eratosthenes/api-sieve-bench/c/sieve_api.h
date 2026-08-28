/* sieve_api.h — C Interface specification for libsieve */
#ifndef SIEVE_API_H
#define SIEVE_API_H

#include <stdint.h>
#include <size_t.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок виконання */
typedef enum {
    SIEVE_SUCCESS             =  0,
    SIEVE_ERR_INVALID_RANGE   = -1,
    SIEVE_ERR_OUT_OF_MEMORY   = -2,
    SIEVE_ERR_OVERFLOW        = -3,
    SIEVE_ERR_THREAD_FAILURE  = -4
} sieve_status_t;

/* Варіанти оптимізації колесом факторів */
typedef enum {
    SIEVE_WHEEL_NONE = 0, /* Без колеса (просіювання всіх чисел) */
    SIEVE_WHEEL_2    = 1, /* Просіювання непарних чисел (mod 2) */
    SIEVE_WHEEL_30   = 2, /* Колесо Modulo 30 (8 кандидатів із 30) */
    SIEVE_WHEEL_210  = 3  /* Колесо Modulo 210 (48 кандидатів із 210) */
} sieve_wheel_t;

/* Структура конфігурації просіювання */
typedef struct {
    uint64_t start_n;        /* Початкова межа інтервалу L */
    uint64_t end_n;          /* Кінцева межа інтервалу R */
    uint32_t segment_size;   /* Розмір сегмента у байтах (0 = авто під L1) */
    uint32_t thread_count;   /* Кількість потоків (0 = усі доступні ядра) */
    sieve_wheel_t wheel;     /* Тип колеса факторів */
    bool      count_only;    /* Зберігати лише кількість, не зберігати прості */
} sieve_config_t;

/* Результат обчислень */
typedef struct {
    uint64_t total_primes;   /* Кількість знайдених простих чисел π(R) - π(L-1) */
    uint64_t execution_us;   /* Час виконання у мікросекундах */
    uint64_t bytes_allocated;/* Загальний обсяг спожитої оперативної пам'яті */
    uint64_t* primes_array;  /* Масив знайдених чисел (NULL якщо count_only = true) */
    size_t   array_capacity; /* Ємність виділеного масиву */
} sieve_result_t;

/* Ініціалізація замовчувань для конфігурації */
sieve_config_t sieve_default_config(void);

/* Виконання просіювання згідно з конфігурацією */
sieve_status_t sieve_execute(const sieve_config_t* config, sieve_result_t* result);

/* Звільнення ресурсів результату */
void sieve_free_result(sieve_result_t* result);

/* Отримання текстового опису коду помилки */
const char* sieve_error_string(sieve_status_t status);

#ifdef __cplusplus
}
#endif

#endif /* SIEVE_API_H */
