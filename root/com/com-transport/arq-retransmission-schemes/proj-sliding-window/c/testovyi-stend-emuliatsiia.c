/* Сценарій емуляції ненадійного каналу та роботи Go-Back-N у C */
int main(void) {
    GbnSender tx;
    GbnReceiver rx;
    gbn_sender_init(&tx);
    gbn_receiver_init(&rx);

    printf("========================================\n");
    printf("  Симуляція протоколу Go-Back-N (C)\n");
    printf("========================================\n");
    uint8_t msg[] = "PAYLOAD_BLOCK";

    /* Крок 1. Передавач відправляє пачку з 4 кадрів (номери 0, 1, 2, 3) */
    Frame f[4];
    for (int i = 0; i < 4; ++i) {
        if (gbn_sender_send(&tx, msg, sizeof(msg), &f[i])) {
            printf("[TX] Відправлено Кадр #%d (SendBase=%d, NextSeq=%d)\n",
                   f[i].seq, tx.send_base, tx.next_seq);
        }
    }

    /* Крок 2. Кадри 0 та 1 успішно доходять до приймача */
    Frame ack;
    for (int i = 0; i < 2; ++i) {
        if (gbn_receiver_on_frame(&rx, &f[i], &ack)) {
            printf("[RX] Отримано Кадр #%d -> Відповідь: Кумулятивний ACK %d\n",
                   f[i].seq, ack.ack);
            gbn_sender_on_ack(&tx, &ack);
            printf("[TX] Отримано ACK %d -> SendBase зміщено на %d\n", ack.ack, tx.send_base);
        }
    }

    /* Крок 3. Кадр 2 губиться в каналі зв'язку через заваду */
    printf("\n>>> [КАНАЛ] ✗ Кадр #2 СПОТВОРЕНО / ВТРАЧЕНО! <<<\n\n");

    /* Крок 4. Кадр 3 надходить до приймача */
    if (gbn_receiver_on_frame(&rx, &f[3], &ack)) {
        printf("[RX] Отримано Кадр #3 поза чергою (очікувався #2) -> ВІДКИДАЄМО!\n");
        printf("[RX] Повтор попереднього ACK %d\n", ack.ack);
        gbn_sender_on_ack(&tx, &ack);
    }

    /* Крок 5. Передавач чекає таймауту для неподтвердженого кадру #2 */
    printf("\n[TX] Очікування таймауту RTO для Кадру #2...\n");
    Frame retrans[SEQ_SPACE];
    int count = 0;
    for (int t = 0; t < RTO_TICKS; ++t) {
        count = gbn_sender_tick(&tx, retrans);
        if (count > 0) break;
    }

    /* Крок 6. Спрацював таймаут: передавач повторює ВСЮ пачку від кадру #2 */
    printf("[TX] Спрацював RTO! Відкат назад на N: повтор %d кадрів:\n", count);
    for (int i = 0; i < count; ++i) {
        printf("     -> Повторна передача кадру #%d\n", retrans[i].seq);
    }

    return 0;
}
