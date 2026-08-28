#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#if defined(_WIN32)
#include <windows.h>
static void sleep_ms(uint32_t ms) { Sleep(ms); }
#else
#include <unistd.h>
static void sleep_ms(uint32_t ms) { usleep(ms * 1000); }
#endif

/* ── 1. Монотонний таймер мілісекунд ─────────────────────────────────────── */
static uint64_t get_time_ms(void) {
#if defined(_WIN32)
    static LARGE_INTEGER freq;
    static int init = 0;
    if (!init) {
        QueryPerformanceFrequency(&freq);
        init = 1;
    }
    LARGE_INTEGER counter;
    QueryPerformanceCounter(&counter);
    return (uint64_t)((counter.QuadPart * 1000) / freq.QuadPart);
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
#endif
}

/* ── 2. Координатор розподілених замків ───────────────────────────────────── */
typedef struct {
    char     current_owner[32];
    uint64_t current_token;
    uint64_t lease_deadline_ms;
    uint64_t token_generator;
} LockCoordinator;

typedef struct {
    bool     granted;
    uint64_t token;
    uint64_t ttl_ms;
} LockGrant;

void coordinator_init(LockCoordinator* c) {
    c->current_owner[0] = '\0';
    c->current_token = 0;
    c->lease_deadline_ms = 0;
    c->token_generator = 0;
}

LockGrant coordinator_acquire(LockCoordinator* c, const char* client_id, uint64_t ttl_ms) {
    uint64_t now = get_time_ms();
    LockGrant grant = { .granted = false, .token = 0, .ttl_ms = 0 };

    /* Якщо замок вільний або попередня ліза спливла */
    if (c->current_owner[0] == '\0' || now >= c->lease_deadline_ms) {
        c->token_generator++; /* Атомарний інкремент монотонного лічильника епохи */
        c->current_token = c->token_generator;
        strncpy(c->current_owner, client_id, sizeof(c->current_owner) - 1);
        c->current_owner[sizeof(c->current_owner) - 1] = '\0';
        c->lease_deadline_ms = now + ttl_ms;

        grant.granted = true;
        grant.token = c->current_token;
        grant.ttl_ms = ttl_ms;

        printf("[КООРДИНАТОР] Замок надано '%s' | Токен: %llu | TTL: %llu мс\n",
               client_id, (unsigned long long)grant.token, (unsigned long long)ttl_ms);
    } else {
        printf("[КООРДИНАТОР] Запит від '%s' ВІДХИЛЕНО: замок утримує '%s' (ще %llu мс)\n",
               client_id, c->current_owner, (unsigned long long)(c->lease_deadline_ms - now));
    }
    return grant;
}

/* ── 3. Захищене сховище з валідацією токенів ────────────────────────────── */
typedef struct {
    int64_t  balance;
    uint64_t highest_token_seen;
    uint64_t total_writes;
    uint64_t stale_rejections;
} FencedStorage;

typedef enum {
    WRITE_ACCEPTED,
    WRITE_REJECTED_STALE
} WriteResult;

void storage_init(FencedStorage* s, int64_t initial_balance) {
    s->balance = initial_balance;
    s->highest_token_seen = 0;
    s->total_writes = 0;
    s->stale_rejections = 0;
}

WriteResult storage_write(FencedStorage* s, const char* client_id,
                          uint64_t token, int64_t new_balance) {
    printf("[СХОВИЩЕ] Запит від '%s' | Токен: %llu | Новий баланс: $%lld | Найвищий відомий: %llu\n",
           client_id, (unsigned long long)token, (long long)new_balance,
           (unsigned long long)s->highest_token_seen);

    /* Головний інваріант огорожі: перевірка монотонності */
    if (token >= s->highest_token_seen) {
        s->highest_token_seen = token;
        s->balance = new_balance;
        s->total_writes++;
        printf("[СХОВИЩЕ] -> УСПІХ: токен %llu >= %llu. Баланс оновлено до $%lld\n",
               (unsigned long long)token, (unsigned long long)s->highest_token_seen,
               (long long)s->balance);
        return WRITE_ACCEPTED;
    } else {
        s->stale_rejections++;
        printf("[СХОВИЩЕ] -> ВІДХИЛЕНО (ОГОРОЖА): токен %llu < %llu! Застарілий запис відкинуто.\n",
               (unsigned long long)token, (unsigned long long)s->highest_token_seen);
        return WRITE_REJECTED_STALE;
    }
}

/* ── 4. Демонстраційний сценарій відтворення збою ────────────────────────── */
int main(void) {
    LockCoordinator coordinator;
    FencedStorage storage;

    coordinator_init(&coordinator);
    storage_init(&storage, 5000); /* Початковий баланс: $5000 */

    printf("=== СТАРТ СИМУЛЯЦІЇ РОЗПОДІЛЕНОЇ ОГОРОЖІ ===\n");
    printf("Початковий баланс у сховищі: $%lld\n\n", (long long)storage.balance);

    /* Крок 1: Воркер A бере замок на 300 мс і отримує токен 1 */
    printf("--- Крок 1: Воркер A бере замок ---\n");
    LockGrant grant_a = coordinator_acquire(&coordinator, "Worker-A", 300);
    if (!grant_a.granted) {
        printf("Помилка захоплення замка Воркером A\n");
        return 1;
    }

    /* Крок 2: Воркер A готує транзакцію (списання $2000), але засинає на 500 мс (GC-пауза) */
    printf("\n--- Крок 2: Воркер A засинає в GC-паузі на 500 мс (ліза спливає на 300 мс) ---\n");
    int64_t prepared_balance_a = storage.balance - 2000; /* $5000 - $2000 = $3000 */
    sleep_ms(500);

    /* Крок 3: Воркер B бачить, що ліза A спливла, перехоплює замок і отримує токен 2 */
    printf("\n--- Крок 3: Воркер B перехоплює замок після спливання лізи A ---\n");
    LockGrant grant_b = coordinator_acquire(&coordinator, "Worker-B", 300);
    if (!grant_b.granted) {
        printf("Помилка захоплення замка Воркером B\n");
        return 1;
    }

    /* Крок 4: Воркер B успішно поповнює баланс на $1500 ($5000 + $1500 = $6500) */
    printf("\n--- Крок 4: Воркер B записує новий баланс $6500 із токеном 2 ---\n");
    int64_t new_balance_b = storage.balance + 1500;
    WriteResult res_b = storage_write(&storage, "Worker-B", grant_b.token, new_balance_b);
    if (res_b != WRITE_ACCEPTED) {
        printf("Помилка запису Воркера B\n");
        return 1;
    }

    /* Крок 5: Воркер A прокидається після GC-паузи і відправляє свій застарілий запис $3000 */
    printf("\n--- Крок 5: Воркер A прокидається і надсилає застарілий запис $3000 із токеном 1 ---\n");
    WriteResult res_a = storage_write(&storage, "Worker-A", grant_a.token, prepared_balance_a);

    /* Перевірка результатів */
    printf("\n=== ПІДСУМКИ ТЕСТУ ===\n");
    printf("Фінальний баланс у базі: $%lld (Очікується: $6500)\n", (long long)storage.balance);
    printf("Кількість відхилених застарілих записів: %llu (Очікується: 1)\n",
           (unsigned long long)storage.stale_rejections);

    if (storage.balance == 6500 && storage.stale_rejections == 1) {
        printf(">>> РЕЗУЛЬТАТ: УСПІХ! Токен огорожі врятував дані від затирання. <<<\n");
    } else {
        printf(">>> РЕЗУЛЬТАТ: ВАДА! Дані пошкоджено. <<<\n");
    }

    return 0;
}
