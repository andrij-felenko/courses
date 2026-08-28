#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>

#define MAX_MSG_ID_LEN 64
#define CACHE_CAPACITY 1024

/* Типи результатів обробки */
typedef enum {
    CONSUME_OK_PROCESSED,    /* Повідомлення нове, успішно оброблено */
    CONSUME_OK_DUPLICATE,    /* Повідомлення дублікатне, пропущено без помилки */
    CONSUME_ERR_TRANSACTION  /* Помилка сховища / бази даних */
} ConsumeStatus;

/* Структура повідомлення */
typedef struct {
    char id[MAX_MSG_ID_LEN];
    long account_id;
    double amount;
} PaymentMessage;

/* Запис ковзного вікна дедуплікації в оперативній пам'яті (L1) */
typedef struct {
    char id[MAX_MSG_ID_LEN];
    time_t seen_at;
    bool in_use;
} CacheEntry;

/* Імітація бази даних споживача (L2) */
typedef struct {
    double balance;
    char processed_inbox[CACHE_CAPACITY][MAX_MSG_ID_LEN];
    size_t inbox_count;
    bool in_transaction;
} MockDatabase;

/* Стан надійного споживача */
typedef struct {
    MockDatabase db;
    CacheEntry l1_cache[CACHE_CAPACITY];
    time_t window_ttl_seconds;
} ReliableConsumer;

/* Ініціалізація споживача */
void consumer_init(ReliableConsumer *c, double initial_balance, time_t ttl_sec) {
    memset(c, 0, sizeof(ReliableConsumer));
    c->db.balance = initial_balance;
    c->window_ttl_seconds = ttl_sec;
}

/* Перевірка швидкого кешу в пам'яті */
static bool l1_cache_contains(ReliableConsumer *c, const char *msg_id, time_t now) {
    for (size_t i = 0; i < CACHE_CAPACITY; ++i) {
        if (c->l1_cache[i].in_use) {
            if (now - c->l1_cache[i].seen_at > c->window_ttl_seconds) {
                c->l1_cache[i].in_use = false; /* Протухлий запис */
                continue;
            }
            if (strncmp(c->l1_cache[i].id, msg_id, MAX_MSG_ID_LEN) == 0) {
                return true;
            }
        }
    }
    return false;
}

/* Додавання запису до кешу пам'яті */
static void l1_cache_insert(ReliableConsumer *c, const char *msg_id, time_t now) {
    size_t victim_idx = 0;
    time_t oldest_time = now + 1;

    for (size_t i = 0; i < CACHE_CAPACITY; ++i) {
        if (!c->l1_cache[i].in_use) {
            victim_idx = i;
            break;
        }
        if (c->l1_cache[i].seen_at < oldest_time) {
            oldest_time = c->l1_cache[i].seen_at;
            victim_idx = i;
        }
    }

    strncpy(c->l1_cache[victim_idx].id, msg_id, MAX_MSG_ID_LEN - 1);
    c->l1_cache[victim_idx].id[MAX_MSG_ID_LEN - 1] = '\0';
    c->l1_cache[victim_idx].seen_at = now;
    c->l1_cache[victim_idx].in_use = true;
}

/* Атомарна обробка в межах локальної транзакції */
ConsumeStatus consumer_process_message(ReliableConsumer *c, const PaymentMessage *msg) {
    time_t now = time(NULL);

    /* Крок 1: Швидка перевірка в кеші L1 */
    if (l1_cache_contains(c, msg->id, now)) {
        return CONSUME_OK_DUPLICATE;
    }

    /* Крок 2: Початок транзакції БД */
    c->db.in_transaction = true;

    /* Крок 3: Перевірка та вставка в таблицю Inbox БД (L2) */
    for (size_t i = 0; i < c->db.inbox_count; ++i) {
        if (strncmp(c->db.processed_inbox[i], msg->id, MAX_MSG_ID_LEN) == 0) {
            c->db.in_transaction = false; /* Відкат транзакції */
            l1_cache_insert(c, msg->id, now); /* Оновлюємо L1 кеш */
            return CONSUME_OK_DUPLICATE;
        }
    }

    /* Крок 4: Виконання бізнес-мутації */
    c->db.balance += msg->amount;

    /* Фіксація ключа в Inbox */
    if (c->db.inbox_count < CACHE_CAPACITY) {
        strncpy(c->db.processed_inbox[c->db.inbox_count], msg->id, MAX_MSG_ID_LEN - 1);
        c->db.processed_inbox[c->db.inbox_count][MAX_MSG_ID_LEN - 1] = '\0';
        c->db.inbox_count++;
    }

    /* Крок 5: Коміт транзакції БД */
    c->db.in_transaction = false;

    /* Крок 6: Оновлення L1 кешу після успіху */
    l1_cache_insert(c, msg->id, now);

    return CONSUME_OK_PROCESSED;
}

int main(void) {
    ReliableConsumer consumer;
    consumer_init(&consumer, 1000.0, 300); /* Початковий баланс 1000 грн, TTL 300 с */

    PaymentMessage msg1 = {"tx_9981_order_44", 101, 250.0};
    PaymentMessage duplicate = {"tx_9981_order_44", 101, 250.0};
    PaymentMessage msg2 = {"tx_9982_order_45", 101, 100.0};

    printf("Початковий баланс: %.2f грн\n", consumer.db.balance);

    /* Перша доставка msg1 */
    ConsumeStatus st1 = consumer_process_message(&consumer, &msg1);
    printf("Спроба 1 (msg1): %s, Баланс: %.2f грн\n",
           st1 == CONSUME_OK_PROCESSED ? "ОБРОБЛЕНО" : "ДУБЛІКАТ", consumer.db.balance);

    /* Мережевий повтор msg1 через збій ACK */
    ConsumeStatus st_dup = consumer_process_message(&consumer, &duplicate);
    printf("Спроба 2 (повтор msg1): %s, Баланс: %.2f грн\n",
           st_dup == CONSUME_OK_PROCESSED ? "ОБРОБЛЕНО" : "ДУБЛІКАТ (відсічено)", consumer.db.balance);

    /* Нове повідомлення msg2 */
    ConsumeStatus st2 = consumer_process_message(&consumer, &msg2);
    printf("Спроба 3 (msg2): %s, Баланс: %.2f грн\n",
           st2 == CONSUME_OK_PROCESSED ? "ОБРОБЛЕНО" : "ДУБЛІКАТ", consumer.db.balance);

    return 0;
}
