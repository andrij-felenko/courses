#include <stdio.h>
#include <stdbool.h>

#define DEQUE_CAPACITY 8

typedef struct {
    int data[DEQUE_CAPACITY];
    int head;
    int tail;
    int count;
} CircularDeque;

// Ініціалізація порожньої черги
void deque_init(CircularDeque *dq) {
    dq->head = 0;
    dq->tail = 0;
    dq->count = 0;
}

// Перевірка на переповнення
bool deque_is_full(const CircularDeque *dq) {
    return dq->count == DEQUE_CAPACITY;
}

// Перевірка на порожнечу
bool deque_is_empty(const CircularDeque *dq) {
    return dq->count == 0;
}

// Додавання на початок (голова рухається ліворуч по колу)
bool deque_push_front(CircularDeque *dq, int value) {
    if (deque_is_full(dq)) return false;
    
    // Зсуваємо head ліворуч по колу лише якщо черга НЕ порожня
    if (!deque_is_empty(dq)) {
        dq->head = (dq->head - 1 + DEQUE_CAPACITY) % DEQUE_CAPACITY;
    }
    
    dq->data[dq->head] = value;
    dq->count++;
    return true;
}

// Додавання в кінець (хвіст рухається праворуч по колу)
bool deque_push_back(CircularDeque *dq, int value) {
    if (deque_is_full(dq)) return false;
    
    // Зсуваємо tail праворуч по колу лише якщо черга НЕ порожня
    if (!deque_is_empty(dq)) {
        dq->tail = (dq->tail + 1) % DEQUE_CAPACITY;
    }
    
    dq->data[dq->tail] = value;
    dq->count++;
    return true;
}

// Вилучення з початку (голова рухається праворуч по колу)
bool deque_pop_front(CircularDeque *dq, int *out_value) {
    if (deque_is_empty(dq)) return false;
    
    *out_value = dq->data[dq->head];
    dq->count--;
    
    // Якщо після вилучення черга не стала порожньою, рухаємо head праворуч
    if (!deque_is_empty(dq)) {
        dq->head = (dq->head + 1) % DEQUE_CAPACITY;
    }
    return true;
}

// Вилучення з кінця (хвіст рухається ліворуч по колу)
bool deque_pop_back(CircularDeque *dq, int *out_value) {
    if (deque_is_empty(dq)) return false;
    
    *out_value = dq->data[dq->tail];
    dq->count--;
    
    // Якщо після вилучення черга не стала порожньою, рухаємо tail ліворуч
    if (!deque_is_empty(dq)) {
        dq->tail = (dq->tail - 1 + DEQUE_CAPACITY) % DEQUE_CAPACITY;
    }
    return true;
}

int main(void) {
    CircularDeque dq;
    deque_init(&dq);

    deque_push_back(&dq, 10);
    deque_push_back(&dq, 20);
    deque_push_front(&dq, 5);  // Стан черги: [5, 10, 20]

    int val;
    printf("Елементи черги з початку: ");
    while (deque_pop_front(&dq, &val)) {
        printf("%d ", val);  // Виведе: 5 10 20
    }
    printf("\n");
    return 0;
}
