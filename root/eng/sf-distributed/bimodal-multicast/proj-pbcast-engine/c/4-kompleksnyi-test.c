int main(void) {
    pbcast_buffer_t node_a, node_b;
    pbcast_buffer_init(&node_a, 1, 100);
    pbcast_buffer_init(&node_b, 1, 100);

    const char *msg1 = "Payload #101";
    const char *msg2 = "Payload #102";
    const char *msg3 = "Payload #103 (Lost on A)";
    const char *msg4 = "Payload #104";

    /* Вузол B отримує всі пакети 101..104 */
    pbcast_buffer_insert(&node_b, 101, (const uint8_t*)msg1, strlen(msg1));
    pbcast_buffer_insert(&node_b, 102, (const uint8_t*)msg2, strlen(msg2));
    pbcast_buffer_insert(&node_b, 103, (const uint8_t*)msg3, strlen(msg3));
    pbcast_buffer_insert(&node_b, 104, (const uint8_t*)msg4, strlen(msg4));

    /* Вузол A втратив #103 */
    pbcast_buffer_insert(&node_a, 101, (const uint8_t*)msg1, strlen(msg1));
    pbcast_buffer_insert(&node_a, 102, (const uint8_t*)msg2, strlen(msg2));
    pbcast_buffer_insert(&node_a, 104, (const uint8_t*)msg4, strlen(msg4));

    printf("Стан вузла A перед gossip: LowWatermark=%llu, Mask=0x%llx\n",
           (unsigned long long)node_a.low_watermark, (unsigned long long)node_a.received_mask);

    /* Вузол B надсилає свій дайджест вузлу A */
    uint64_t missing[16];
    size_t missing_count = 0;
    pbcast_process_digest(&node_a, node_b.low_watermark, node_b.received_mask, missing, &missing_count, 16);

    printf("Вузол A виявив пропуски: %zu шт. Перший номер: %llu\n",
           missing_count, missing_count > 0 ? (unsigned long long)missing[0] : 0);

    /* Ретрансляція пакета #103 від B до A */
    if (missing_count > 0 && missing[0] == 103) {
        size_t s_idx = 103 % PBCAST_BUFFER_CAPACITY;
        pbcast_buffer_insert(&node_a, 103, node_b.slots[s_idx].payload, node_b.slots[s_idx].payload_len);
    }

    printf("Стан вузла A після ремонту: LowWatermark=%llu, Mask=0x%llx (Збіжність досягнута!)\n",
           (unsigned long long)node_a.low_watermark, (unsigned long long)node_a.received_mask);

    return 0;
}
