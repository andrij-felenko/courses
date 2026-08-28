#include <pthread.h>

// 1. Статична ініціалізація (тільки зі стандартними атрибутами)
pthread_mutex_t g_static_lock = PTHREAD_MUTEX_INITIALIZER;

// 2. Динамічна ініціалізація (дозволяє налаштовувати атрибути)
void init_dynamic_mutex(void) {
    pthread_mutex_t dynamic_lock;
    pthread_mutexattr_t attr;
    
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_ERRORCHECK);
    
    pthread_mutex_init(&dynamic_lock, &attr);
    
    pthread_mutexattr_destroy(&attr); // Атрибути можна знищити одразу після ініціалізації
    pthread_mutex_destroy(&dynamic_lock);
}
