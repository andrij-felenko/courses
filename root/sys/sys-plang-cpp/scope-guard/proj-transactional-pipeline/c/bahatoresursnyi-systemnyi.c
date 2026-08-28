#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pthread.h>
#include <stdbool.h>

typedef struct {
    pthread_mutex_t lock;
    int counter;
} SharedRegion;

bool init_shared_service_c(const char* shm_name, size_t size) {
    int fd = -1;
    SharedRegion* ptr = (SharedRegion*)MAP_FAILED;
    bool shm_created = false;

    // 1. Створення спільного сегмента
    fd = shm_open(shm_name, O_CREAT | O_RDWR | O_EXCL, 0600);
    if (fd < 0) {
        return false;
    }
    shm_created = true;

    // 2. Встановлення розміру сегмента
    if (ftruncate(fd, (off_t)size) != 0) {
        goto fail;
    }

    // 3. Відображення в адресний простір процесу
    ptr = (SharedRegion*)mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (ptr == MAP_FAILED) {
        goto fail;
    }

    // 4. Ініціалізація міжпроцесного м'ютекса
    pthread_mutexattr_t mattr;
    pthread_mutexattr_init(&mattr);
    pthread_mutexattr_setpshared(&mattr, PTHREAD_PROCESS_SHARED);

    if (pthread_mutex_init(&ptr->lock, &mattr) != 0) {
        pthread_mutexattr_destroy(&mattr);
        goto fail;
    }
    pthread_mutexattr_destroy(&mattr);

    ptr->counter = 0;
    close(fd);
    return true;

fail:
    if (ptr != MAP_FAILED) {
        munmap(ptr, size);
    }
    if (fd >= 0) {
        close(fd);
    }
    if (shm_created) {
        shm_unlink(shm_name);
    }
    return false;
}
