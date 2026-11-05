#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Вимога суворого 8-байтового вирівнювання для 64-бітної інструкції LDREXD/STREXD */
typedef struct Node {
    uint32_t value;
    struct Node* next;
} Node_t;

/* Тегований вказівник: адреса (32 біти) + версійна мітка (32 біти) */
typedef struct {
    Node_t* ptr;
    uint32_t tag;
} __attribute__((aligned(8))) TaggedPtr_t;

/* Структурна голова стека */
typedef struct {
    volatile TaggedPtr_t head;
} LockFreeStack_t;

/* Бар'єр пам'яті DMB для ARM Cortex-M */
static inline void memory_barrier(void) {
    __asm__ volatile ("dmb 0xF" ::: "memory");
}

/* Низькорівнева реалізація DWCAS через LDREXD / STREXD */
static inline bool atomic_cas_tagged(volatile TaggedPtr_t* target, TaggedPtr_t expected, TaggedPtr_t desired) {
    uint32_t status;
    TaggedPtr_t current;

    __asm__ volatile (
        "1: LDREXD  %0, %1, [%3]\n"       /* Зчитуємо 64 біти: ptr у %0, tag у %1 */
        "   CMP     %0, %4\n"             /* Порівнюємо поточний ptr з очікуваним ptr */
        "   BNE     2f\n"                 /* Якщо не рівні — вихід */
        "   CMP     %1, %5\n"             /* Порівнюємо поточний tag з очікуваним tag */
        "   BNE     2f\n"                 /* Якщо не рівні — вихід */
        "   STREXD  %2, %6, %7, [%3]\n"   /* Спроба атомарного запису desired у target */
        "   CMP     %2, #0\n"             /* Перевірка прапорця успіху STREXD (0 = success) */
        "   BNE     1b\n"                 /* Якщо збій через переривання — повторюємо спробу */
        "   MOV     %2, #1\n"             /* Успішна заміна, status = 1 */
        "   B       3f\n"
        "2: CLREX\n"                      /* Скидаємо ексклюзивний монітор при незбігу */
        "   MOV     %2, #0\n"             /* status = 0 */
        "3:\n"
        : "=&r" (current.ptr), "=&r" (current.tag), "=&r" (status)
        : "r" (target), "r" (expected.ptr), "r" (expected.tag), "r" (desired.ptr), "r" (desired.tag)
        : "cc", "memory"
    );

    return (status != 0);
}

void lockfree_stack_init(LockFreeStack_t* stack) {
    stack->head.ptr = NULL;
    stack->head.tag = 0;
}

void lockfree_stack_push(LockFreeStack_t* stack, Node_t* node) {
    TaggedPtr_t old_head, new_head;
    do {
        old_head = stack->head;
        memory_barrier();
        node->next = old_head.ptr;
        new_head.ptr = node;
        new_head.tag = old_head.tag + 1; /* Збільшуємо тег версії */
        memory_barrier();
    } while (!atomic_cas_tagged(&stack->head, old_head, new_head));
}

Node_t* lockfree_stack_pop(LockFreeStack_t* stack) {
    TaggedPtr_t old_head, new_head;
    Node_t* node;
    do {
        old_head = stack->head;
        memory_barrier();
        if (old_head.ptr == NULL) {
            return NULL;
        }
        node = old_head.ptr;
        new_head.ptr = node->next;
        new_head.tag = old_head.tag + 1; /* Збільшуємо тег версії */
        memory_barrier();
    } while (!atomic_cas_tagged(&stack->head, old_head, new_head));

    return node;
}
