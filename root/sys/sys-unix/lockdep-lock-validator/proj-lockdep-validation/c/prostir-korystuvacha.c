/* POSIX C Implementation: Ручне сортування адрес для запобігання ABBA */
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdint.h>
#include <unistd.h>

typedef struct {
    pthread_mutex_t mutex;
    int id;
} resource_t;

/* Безпечна функція захоплення двох ресурсів із сортуванням за адресами */
void acquire_two_resources_safe(resource_t *r1, resource_t *r2) {
    resource_t *first = r1;
    resource_t *second = r2;

    if (r1 == r2) {
        /* Запобігання повторному взяттю одного й того ж лока */
        pthread_mutex_lock(&r1->mutex);
        return;
    }

    /* Динамічне впорядкування за адресами в пам'яті (Lock Ordering) */
    if ((uintptr_t)r1 > (uintptr_t)r2) {
        first = r2;
        second = r1;
    }

    pthread_mutex_lock(&first->mutex);
    pthread_mutex_lock(&second->mutex);

    /* Критична секція */
    printf("C-Safe: Acquired resources %d and %d in strict address order (%p < %p)\n", 
           first->id, second->id, (void*)first, (void*)second);

    pthread_mutex_unlock(&second->mutex);
    pthread_mutex_unlock(&first->mutex);
}

int main(void) {
    resource_t a = { .id = 1 };
    resource_t b = { .id = 2 };
    
    pthread_mutex_init(&a.mutex, NULL);
    pthread_mutex_init(&b.mutex, NULL);

    /* Викликаємо з різним порядком аргументів у двох викликах */
    acquire_two_resources_safe(&a, &b);
    acquire_two_resources_safe(&b, &a);

    pthread_mutex_destroy(&a.mutex);
    pthread_mutex_destroy(&b.mutex);
    return 0;
}
