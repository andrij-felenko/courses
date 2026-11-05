#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Структура вузла стека */
typedef struct Node {
    uint32_t data;
    struct Node* next;
} Node_t;

/* Тегований вказівник для запобігання ABA (64-бітне вирівняне слово) */
typedef struct {
    Node_t* ptr;
    uint32_t tag;
} __attribute__((aligned(8))) TaggedPointer_t;

/* Голова стека */
typedef struct {
    volatile TaggedPointer_t head;
} LockFreeStack_t;

/* Ініціалізація стека */
void lockfree_stack_init(LockFreeStack_t* stack) {
    stack->head.ptr = NULL;
    stack->head.tag = 0;
}

/* Атомарна операція CAS над 64-бітним тегованим вказівником для ARM Cortex-M */
static inline bool atomic_cas_tagged(volatile TaggedPointer_t* target, 
                                    TaggedPointer_t old_val, 
                                    TaggedPointer_t new_val) {
    uint32_t status;
    uint32_t dummy1, dummy2;

    /* Використання парних інструкцій LDREXD / STREXD для атомарного порівняння та заміни */
    __asm__ volatile (
        "1: LDREXD %0, %1, [%3]\n"       /* Завантажити 64-бітне значення (ptr, tag) */
        "   CMP    %0, %4\n"             /* Порівняти ptr з old_val.ptr */
        "   IT     EQ\n"
        "   CMPEQ  %1, %5\n"             /* Якщо ptr однакові, порівняти tag з old_val.tag */
        "   BNE    2f\n"                 /* Якщо не рівні — вихід з помилкою */
        "   STREXD %2, %6, %7, [%3]\n"   /* Спробувати записати new_val (ptr, tag) */
        "   CMP    %2, #0\n"             /* Перевірити успішність STREXD */
        "   BNE    1b\n"                 /* Якщо конфлікт шини — повторити цикл */
        "   MOV    %2, #0\n"             /* Успіх */
        "   B      3f\n"
        "2: CLREX\n"                     /* Скинути монітор ексклюзивного доступу */
        "   MOV    %2, #1\n"             /* Помилка порівняння */
        "3:\n"
        : "=&r" (dummy1), "=&r" (dummy2), "=&r" (status)
        : "r" (target), "r" (old_val.ptr), "r" (old_val.tag), 
          "r" (new_val.ptr), "r" (new_val.tag)
        : "cc", "memory"
    );

    return (status == 0);
}

/* Безблокове додавання елемента на верхівку стека (Push) */
void lockfree_stack_push(LockFreeStack_t* stack, Node_t* new_node) {
    TaggedPointer_t old_head;
    TaggedPointer_t new_head;

    do {
        old_head.ptr = stack->head.ptr;
        old_head.tag = stack->head.tag;

        new_node->next = old_head.ptr;
        
        new_head.ptr = new_node;
        new_head.tag = old_head.tag + 1; /* Збільшуємо тег версії */

        __dmb(0xF); /* Бар'єр пам'яті для гарантування впорядкованості запису next */
    } while (!atomic_cas_tagged(&stack->head, old_head, new_head));
}

/* Безблокове вилучення елемента з верхівки стека (Pop) */
Node_t* lockfree_stack_pop(LockFreeStack_t* stack) {
    TaggedPointer_t old_head;
    TaggedPointer_t new_head;
    Node_t* node = NULL;

    do {
        old_head.ptr = stack->head.ptr;
        old_head.tag = stack->head.tag;

        if (old_head.ptr == NULL) {
            return NULL; /* Стек порожній */
        }

        node = old_head.ptr;
        new_head.ptr = node->next;
        new_head.tag = old_head.tag + 1; /* Збільшуємо тег версії для запобігання ABA */

    } while (!atomic_cas_tagged(&stack->head, old_head, new_head));

    return node;
}
