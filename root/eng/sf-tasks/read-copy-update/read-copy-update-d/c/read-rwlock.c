#include <pthread.h>
#include <stdatomic.h>
#include <stdlib.h>

// Класичний підхід із використанням rwlock (виклики створюють інвалідацію кеш-ліній)
typedef struct {
    int data[100];
} ConfigData;

typedef struct {
    ConfigData *data;
    pthread_rwlock_t lock;
} SharedConfigRW;

int read_rwlock(SharedConfigRW *cfg, int index) {
    pthread_rwlock_rdlock(&cfg->lock); // Атомарний інкремент лічильника читачів -> cache line bouncing
    int val = cfg->data->data[index];
    pthread_rwlock_unlock(&cfg->lock); // Атомарний декремент -> повторна інвалідація кешу
    return val;
}

// Ідеальний пасивний читач (нуль записів у спільну пам'ять)
typedef struct {
    _Atomic(ConfigData *) data_ptr;
} SharedConfigPassive;

int read_passive(SharedConfigPassive *cfg, int index) {
    // Звичайне читання атомарного вказівника без захоплення замків і без модифікації пам'яті
    ConfigData *ptr = atomic_load_explicit(&cfg->data_ptr, memory_order_consume);
    return ptr->data[index];
}
