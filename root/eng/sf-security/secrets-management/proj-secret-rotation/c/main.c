#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/mman.h>
#include <time.h>

#define SECRET_MAX_LEN 256

/* Структура захищеного облікового запису */
typedef struct {
    char username[SECRET_MAX_LEN];
    char password[SECRET_MAX_LEN];
    char lease_id[SECRET_MAX_LEN];
    time_t expires_at;
    _Atomic int ref_count;
} secret_entry_t;

/* Стан менеджера секретів */
typedef struct {
    _Atomic(secret_entry_t*) active_secret;
    pthread_t worker_thread;
    atomic_bool running;
    int rotation_interval_sec;
} secret_manager_t;

/* Безпечне виділення пам'яті з блокуванням у RAM */
static secret_entry_t* secure_entry_create(const char* user, const char* pass, const char* lease, int ttl_sec) {
    long page_size = sysconf(_SC_PAGESIZE);
    size_t alloc_size = (sizeof(secret_entry_t) + page_size - 1) & ~(page_size - 1);

    secret_entry_t* entry = NULL;
    if (posix_memalign((void**)&entry, page_size, alloc_size) != 0) {
        return NULL;
    }

    /* Заборона вивантаження сторінки у swap */
    if (mlock(entry, alloc_size) != 0) {
        free(entry);
        return NULL;
    }

    /* Виключення з дампу пам'яті під час аварії */
#ifdef MADV_DONTDUMP
    madvise(entry, alloc_size, MADV_DONTDUMP);
#endif

    strncpy(entry->username, user, SECRET_MAX_LEN - 1);
    entry->username[SECRET_MAX_LEN - 1] = '\0';

    strncpy(entry->password, pass, SECRET_MAX_LEN - 1);
    entry->password[SECRET_MAX_LEN - 1] = '\0';

    strncpy(entry->lease_id, lease, SECRET_MAX_LEN - 1);
    entry->lease_id[SECRET_MAX_LEN - 1] = '\0';

    entry->expires_at = time(NULL) + ttl_sec;
    atomic_init(&entry->ref_count, 1);

    return entry;
}

/* Гарантоване очищення пам'яті перед звільненням */
static void secure_entry_release(secret_entry_t* entry) {
    if (!entry) return;

    if (atomic_fetch_sub(&entry->ref_count, 1) == 1) {
        long page_size = sysconf(_SC_PAGESIZE);
        size_t alloc_size = (sizeof(secret_entry_t) + page_size - 1) & ~(page_size - 1);

        /* Гарантоване занулення буфера без оптимізацій компілятора */
        explicit_bzero(entry, sizeof(secret_entry_t));

        munlock(entry, alloc_size);
        free(entry);
    }
}

/* Емуляція отримання нового динамічного секрету з Vault */
static secret_entry_t* fetch_secret_from_vault(int version) {
    char user[SECRET_MAX_LEN];
    char pass[SECRET_MAX_LEN];
    char lease[SECRET_MAX_LEN];

    snprintf(user, sizeof(user), "app_user_v%d", version);
    snprintf(pass, sizeof(pass), "vault_gen_pass_%lx_%d", (unsigned long)time(NULL), version);
    snprintf(lease, sizeof(lease), "database/creds/app-role/%d", version);

    /* TTL = 10 секунд для демонстрації ротації */
    return secure_entry_create(user, pass, lease, 10);
}

/* Фоновий потік ротації та оновлення оренди */
static void* rotation_worker(void* arg) {
    secret_manager_t* mgr = (secret_manager_t*)arg;
    int version = 1;

    while (atomic_load(&mgr->running)) {
        sleep(mgr->rotation_interval_sec);

        if (!atomic_load(&mgr->running)) break;

        version++;
        secret_entry_t* new_sec = fetch_secret_from_vault(version);
        if (new_sec) {
            /* Атомарна підміна покажчика на новий секрет */
            secret_entry_t* old_sec = atomic_exchange(&mgr->active_secret, new_sec);
            printf("[Worker] Ротація: новий користувач %s (Lease: %s)\n", 
                   new_sec->username, new_sec->lease_id);

            /* Зменшуємо лічильник посилань попереднього секрету */
            secure_entry_release(old_sec);
        }
    }
    return NULL;
}

/* Ініціалізація менеджера */
int secret_manager_init(secret_manager_t* mgr, int rotation_interval_sec) {
    mgr->rotation_interval_sec = rotation_interval_sec;
    atomic_init(&mgr->running, true);

    secret_entry_t* initial_secret = fetch_secret_from_vault(1);
    if (!initial_secret) return -1;

    atomic_init(&mgr->active_secret, initial_secret);

    if (pthread_create(&mgr->worker_thread, NULL, rotation_worker, mgr) != 0) {
        secure_entry_release(initial_secret);
        return -1;
    }
    return 0;
}

/* Отримання поточного секрету клієнтом (Lock-free) */
secret_entry_t* secret_manager_acquire(secret_manager_t* mgr) {
    secret_entry_t* sec = atomic_load(&mgr->active_secret);
    if (sec) {
        atomic_fetch_add(&sec->ref_count, 1);
    }
    return sec;
}

/* Повернення секрету після використання */
void secret_manager_release(secret_entry_t* sec) {
    secure_entry_release(sec);
}

/* Зупинка менеджера та очищення ресурсів */
void secret_manager_destroy(secret_manager_t* mgr) {
    atomic_store(&mgr->running, false);
    pthread_join(mgr->worker_thread, NULL);

    secret_entry_t* sec = atomic_exchange(&mgr->active_secret, NULL);
    secure_entry_release(sec);
}

int main(void) {
    secret_manager_t mgr;
    if (secret_manager_init(&mgr, 3) != 0) {
        fprintf(stderr, "Не вдалося ініціалізувати менеджер секретів\n");
        return 1;
    }

    /* Емуляція роботи застосунку протягом 8 секунд */
    for (int i = 0; i < 4; i++) {
        secret_entry_t* sec = secret_manager_acquire(&mgr);
        if (sec) {
            printf("[Main App] Запит %d: активний логін = %s, пароль = %s\n", 
                   i + 1, sec->username, sec->password);
            secret_manager_release(sec);
        }
        sleep(2);
    }

    secret_manager_destroy(&mgr);
    printf("[Main App] Менеджер успішно зупинено, пам'ять очищено.\n");
    return 0;
}
