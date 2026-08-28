#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define DROP_RATE_PERCENT 30
#define LEASE_DURATION_MS 500
#define MAX_RETRIES 5

typedef enum {
    MSG_ORDER_REQ,
    MSG_PAYMENT_ACK,
    MSG_ACK_TO_ACK,
    MSG_ACK_TO_ACK_TO_ACK
} MsgType;

typedef struct {
    MsgType type;
    uint64_t order_id;
    uint64_t idempotency_key;
    uint64_t timestamp_ms;
    bool committed;
} Packet;

/* Допоміжна функція отримання монотонного часу в мілісекундах */
static uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Симуляція ненадійного мережевого каналу */
static bool send_network_packet(const Packet *pkt, const char *sender, const char *receiver) {
    int roll = rand() % 100;
    if (roll < DROP_RATE_PERCENT) {
        printf("  [МЕРЕЖА: ВТРАТА] Пакет типу %d від %s до %s загублено в каналі!\n",
               pkt->type, sender, receiver);
        return false;
    }
    printf("  [МЕРЕЖА: ДОСТАВЛЕНО] Пакет типу %d від %s успішно дійшов до %s.\n",
           pkt->type, sender, receiver);
    return true;
}

/* 1. Демонстрація наївного протоколу нескінченних квитанцій */
static void run_naive_ack_ladder(uint64_t order_id) {
    printf("\n=== 1. НАЇВНИЙ ПРОТОКОЛ: Нескінченна драбина квитування ===\n");
    
    Packet req = { .type = MSG_ORDER_REQ, .order_id = order_id, .committed = false };
    printf("Крок 1: Магазин надсилає запит на оплату замовлення #%lu...\n", order_id);
    
    if (!send_network_packet(&req, "Магазин", "Банк")) {
        printf("Магазин не знає, чи отримав Банк наказ. Магазин блокується.\n");
        return;
    }

    Packet ack1 = { .type = MSG_PAYMENT_ACK, .order_id = order_id, .committed = true };
    printf("Крок 2: Банк провів оплату та надсилає ACK1 Магазину...\n");
    if (!send_network_packet(&ack1, "Банк", "Магазин")) {
        printf("Банк списав кошти, але Магазин не отримав ACK1! Банк не знає, що робити.\n");
        return;
    }

    Packet ack2 = { .type = MSG_ACK_TO_ACK, .order_id = order_id, .committed = true };
    printf("Крок 3: Магазин отримав ACK1 і надсилає ACK2 (підтвердження на підтвердження)...\n");
    if (!send_network_packet(&ack2, "Магазин", "Банк")) {
        printf("ACK2 загубився! Банк не впевнений, чи Магазин знає про оплату. Глухий кут.\n");
        return;
    }

    printf("Результат: Обидва вузли отримали по пакету, але останній відправник усе одно не має 100%% гарантії!\n");
}

/* 2. Прагматичний інженерний протокол: Часова оренда + Ідемпотентний токен */
typedef struct {
    uint64_t idempotency_key;
    bool is_paid;
    uint64_t lease_expiry_ms;
} BankRecord;

static void run_pragmatic_lease_protocol(uint64_t order_id, uint64_t key) {
    printf("\n=== 2. ПРАГМАТИЧНИЙ ПРОТОКОЛ: Часова оренда та ідемпотентність ===\n");
    
    BankRecord bank_db = { .idempotency_key = key, .is_paid = false, .lease_expiry_ms = 0 };
    bool order_completed = false;
    
    for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        uint64_t now = get_monotonic_ms();
        printf("Спроба #%d: Магазин відправляє запит (Ключ=%lu, Оренда=%d мс)...\n",
               attempt, key, LEASE_DURATION_MS);
        
        Packet req = {
            .type = MSG_ORDER_REQ,
            .order_id = order_id,
            .idempotency_key = key,
            .timestamp_ms = now + LEASE_DURATION_MS
        };

        if (send_network_packet(&req, "Магазин", "Банк")) {
            /* Обробка на боці Банку з перевіркою ідемпотентності */
            if (!bank_db.is_paid) {
                bank_db.is_paid = true;
                bank_db.lease_expiry_ms = req.timestamp_ms;
                printf("  [Банк]: Нова транзакція. Кошти зарезервовано за орендою до t=%lu мс.\n",
                       bank_db.lease_expiry_ms);
            } else {
                printf("  [Банк]: Повторний запит із відомим ключем %lu. Повертаємо кешований успіх.\n", key);
            }

            Packet ack = {
                .type = MSG_PAYMENT_ACK,
                .order_id = order_id,
                .idempotency_key = key,
                .committed = true
            };

            if (send_network_packet(&ack, "Банк", "Магазин")) {
                printf("  [Магазин]: Отримано квитанцію про успішну оплату! Замовлення видано клієнту.\n");
                order_completed = true;
                break;
            } else {
                printf("  [Магазин]: Відповідь від банку загубилася. Магазин чекає таймаут для повтору...\n");
            }
        } else {
            printf("  [Магазин]: Запит не дійшов до банку. Очікування таймауту...\n");
        }
    }

    if (order_completed) {
        printf("\nУспіх: Протокол успішно завершив узгодження без нескінченних квитанцій.\n");
    } else {
        printf("\nТаймаут: Вичерпано всі %d спроб. Запуск компенсаційної процедури саги.\n", MAX_RETRIES);
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    
    printf("Симуляція задачі двох генералів у розподіленій платіжній системі\n");
    printf("Ймовірність втрати пакета в мережі: %d%%\n", DROP_RATE_PERCENT);
    
    run_naive_ack_ladder(1001ULL);
    run_pragmatic_lease_protocol(1002ULL, 987654321ULL);
    
    return 0;
}
