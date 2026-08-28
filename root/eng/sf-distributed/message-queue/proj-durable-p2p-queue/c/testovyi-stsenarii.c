static void *worker_func(void *arg) {
    p2p_queue_t *q = (p2p_queue_t *)arg;
    uint64_t msg_id;
    char payload[MAX_PAYLOAD_SIZE];
    uint32_t len;

    while (p2p_queue_acquire(q, 300 /* оренда на 300 мс */, &msg_id, payload, &len)) {
        payload[len] = '\0';
        printf("[Воркер %lu] Взяв у роботу задачу #%lu: «%s»\n",
               (unsigned long)pthread_self(), (unsigned long)msg_id, payload);

        if (msg_id == 2) {
            printf("[Воркер %lu] ⚡ Імітація аварії на задачі #%lu (не шлемо ACK)!\n",
                   (unsigned long)pthread_self(), (unsigned long)msg_id);
            /* Воркер засинає або падає, не відправляючи ACK */
            usleep(600000);
            continue;
        }

        /* Імітація корисної роботи */
        usleep(50000);

        printf("[Воркер %lu] Успішно завершив задачу #%lu -> ACK\n",
               (unsigned long)pthread_self(), (unsigned long)msg_id);
        p2p_queue_ack(q, msg_id);
    }
    return NULL;
}

int main(void) {
    const char *wal_file = "queue_demo.wal";
    unlink(wal_file);

    p2p_queue_t queue;
    p2p_queue_init(&queue, wal_file);

    printf("=== Старт черги повідомлень Point-to-Point ===\n");

    pthread_t workers[3];
    for (int i = 0; i < 3; ++i) {
        pthread_create(&workers[i], NULL, worker_func, &queue);
    }

    /* Публікація 5 завдань */
    p2p_queue_publish(&queue, "Обробка платіжної транзакції #101", 33);
    p2p_queue_publish(&queue, "Генерація PDF звіту #102", 23);
    p2p_queue_publish(&queue, "Відправка SMS сповіщення #103", 29);
    p2p_queue_publish(&queue, "Індексація каталогу товарів #104", 32);
    p2p_queue_publish(&queue, "Резервне копіювання БД #105", 26);

    /* Цикл моніторингу оренди */
    for (int i = 0; i < 8; ++i) {
        usleep(150000);
        p2p_queue_reclaim_expired(&queue);
    }

    p2p_queue_destroy(&queue);
    for (int i = 0; i < 3; ++i) {
        pthread_join(workers[i], NULL);
    }

    printf("=== Демонстрацію завершено. Журнал збережено на диску ===\n");
    unlink(wal_file);
    return 0;
}
