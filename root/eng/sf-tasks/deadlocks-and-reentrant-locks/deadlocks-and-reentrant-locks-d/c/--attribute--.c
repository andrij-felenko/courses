#include "cmsis_gcc.h"
#include "FreeRTOS.h"
#include "task.h"

// Структура низькорівневого реентрантного замка з вирівнюванням по 32-байтовій межі лінії кешу
typedef struct __attribute__((aligned(32))) {
    TaskHandle_t volatile owner_task;      // Вказівник на TCB задачі-власника
    uint32_t volatile recursion_count;     // Лічильник вкладених захоплень
    uint32_t volatile spinlock_flag;       // Атомарний прапорець для локального захисту
    StaticSemaphore_t xMutexBuffer;        // Буфер для семафора ОС (повільний шлях)
    SemaphoreHandle_t xSlowPathSemaphore;  // Семафор для блокування задач
} LowLevelReentrantLock_t;

// Ініціалізація замка
void reentrant_lock_init(LowLevelReentrantLock_t *lock) {
    lock->owner_task = NULL;
    lock->recursion_count = 0;
    lock->spinlock_flag = 0;
    lock->xSlowPathSemaphore = xSemaphoreCreateBinaryStatic(&(lock->xMutexBuffer));
}

// Атомарне захоплення спинлока на рівні шини ARM Cortex-M
static inline void spinlock_acquire(uint32_t volatile *flag) {
    while (1) {
        // LDREX зчитує прапорець та ставить апаратну позначку на монітор
        if (__LDREXW(flag) == 0) {
            // Спроба записати 1 у прапорець
            if (__STREXW(1, flag) == 0) {
                __DMB(); // Бар'єр пам'яті: завершити всі шинні транзакції
                return;  // Захоплення успішне
            }
        }
        __CLREX(); // Очищення апаратного монітора перед наступною спробою
    }
}

// Атомарне звільнення спинлока
static inline void spinlock_release(uint32_t volatile *flag) {
    __DMB(); // Бар'єр пам'яті перед відкриттям
    *flag = 0;
}

// Процедура захоплення реентрантного замка
bool reentrant_lock_acquire(LowLevelReentrantLock_t *lock, uint32_t timeout_ms) {
    TaskHandle_t current_task = xTaskGetCurrentTaskHandle();
    
    spinlock_acquire(&(lock->spinlock_flag));
    
    // ШВИДКИЙ ШЛЯХ 1: Замок вільний
    if (lock->owner_task == NULL) {
        lock->owner_task = current_task;
        lock->recursion_count = 1;
        spinlock_release(&(lock->spinlock_flag));
        return true;
    }
    
    // ШВИДКИЙ ШЛЯХ 2: Поточна задача вже є власником
    if (lock->owner_task == current_task) {
        lock->recursion_count++; // Простий інкремент без виклику системного планувальника
        spinlock_release(&(lock->spinlock_flag));
        return true;
    }
    
    spinlock_release(&(lock->spinlock_flag));
    
    // ПОВІЛЬНИЙ ШЛЯХ: Замок захоплено іншою задачею
    TickType_t ticks = (timeout_ms == portMAX_DELAY) ? portMAX_DELAY : pdMS_TO_TICKS(timeout_ms);
    if (xSemaphoreTake(lock->xSlowPathSemaphore, ticks) == pdTRUE) {
        spinlock_acquire(&(lock->spinlock_flag));
        lock->owner_task = current_task;
        lock->recursion_count = 1;
        spinlock_release(&(lock->spinlock_flag));
        return true;
    }
    
    return false; // Таймаут очікування замка
}

// Процедура звільнення реентрантного замка
bool reentrant_lock_release(LowLevelReentrantLock_t *lock) {
    TaskHandle_t current_task = xTaskGetCurrentTaskHandle();
    
    spinlock_acquire(&(lock->spinlock_flag));
    
    // Перевірка права власності
    if (lock->owner_task != current_task) {
        spinlock_release(&(lock->spinlock_flag));
        return false; // Помилка: спроба звільнити чужий замок
    }
    
    lock->recursion_count--;
    
    // Якщо глибина рекурсії > 0, замок залишається за поточною задачею
    if (lock->recursion_count > 0) {
        spinlock_release(&(lock->spinlock_flag));
        return true;
    }
    
    // Повне звільнення замка (глибина досягла 0)
    lock->owner_task = NULL;
    spinlock_release(&(lock->spinlock_flag));
    
    // Передаємо сигнал системній черзі для розблокування чекаючої задачі
    xSemaphoreGive(lock->xSlowPathSemaphore);
    return true;
}
