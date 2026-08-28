/**
 * @file syscall_stubs.h
 * @brief Інтерфейс системних заглушок Newlib для вбудованих систем
 */
#ifndef SYSCALL_STUBS_H
#define SYSCALL_STUBS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <sys/stat.h>
#include <sys/types.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief Розмір захисного зазору між вершиною купи та стеком (у байтах) */
#define SYS_STACK_SAFETY_MARGIN_BYTES  1024U

/** @brief Розмір кільцевого буфера передачі UART stdout (у байтах) */
#define SYS_UART_TX_RING_BUFFER_SIZE   512U

/** @brief Розмір кільцевого буфера прийому UART stdin (у байтах) */
#define SYS_UART_RX_RING_BUFFER_SIZE   128U

/**
 * @brief Статистика використання динамічної пам'яті
 */
typedef struct {
    uint32_t heap_start_addr;     /**< Початкова адреса купи (_end) */
    uint32_t heap_current_addr;   /**< Поточна межа виділеної купи */
    uint32_t heap_limit_addr;     /**< Статична межа з linker script */
    uint32_t stack_current_sp;    /**< Поточний вказівник стека ядра SP */
    uint32_t allocated_bytes;     /**< Загальна кількість виділених байтів */
    uint32_t free_margin_bytes;   /**< Вільний залишок RAM до бар'єра стека */
    uint32_t allocation_failures; /**< Лічильник невдалих викликів malloc */
} sys_heap_stats_t;

/**
 * @brief Ініціалізація апаратної периферії та буферів для Newlib
 */
void syscalls_init(void);

/**
 * @brief Отримання поточної діагностики стану купи та стека
 * @param[out] stats Структура для запису статистики
 */
void syscalls_get_heap_stats(sys_heap_stats_t *stats);

/**
 * @brief Прямий неблокуючий запис байта в апаратний порт (для ISR та панік)
 * @param c Байт для відправки
 */
void syscalls_uart_putc_raw(uint8_t c);

/**
 * @brief Примусове скидання всіх буферів передачі
 */
void syscalls_flush_stdout(void);

#ifdef __cplusplus
}
#endif

#endif /* SYSCALL_STUBS_H */
