int main(void) {
    /* Тестовий двійковий дамп: CLNP + адреси NSAP + TP4 DT-TPDU + Дані "HELLO OSI" */
    const uint8_t sample_packet[] = {
        /* Фіксована частина CLNP (9 байтів) */
        0x81,                   /* NLPID = CLNP (0x81) */
        0x19,                   /* LI = 25 байтів заголовка */
        0x01,                   /* Version = 1 */
        0x1E,                   /* Lifetime = 30 (15 секунд) */
        0x1C,                   /* Flags = Non-segmented, Type = Data (0x1C) */
        0x00, 0x27,             /* Segment Length = 39 байтів */
        0xE6, 0xCB,             /* Checksum Fletcher-16 */

        /* Адреса призначення (7 байтів): 49.0001.001A.2B3C.4D5E.01 */
        0x07,                   /* DAL = 7 байтів */
        0x49, 0x00, 0x01, 0x00, 0x1A, 0x2B, 0x01,

        /* Адреса джерела (7 байтів): 49.0001.00AA.BBCC.DDEE.01 */
        0x07,                   /* SAL = 7 байтів */
        0x49, 0x00, 0x01, 0x00, 0xAA, 0xBB, 0x01,

        /* Транспортний блок TP4 DT-TPDU (5 байтів) */
        0x04,                   /* TPDU LI = 4 байти */
        0xF0,                   /* Type = DT-TPDU (0xF0) */
        0x12, 0x34,             /* Destination Reference = 0x1234 */
        0x85,                   /* EOT=1, TPDU-NR = 5 */

        /* Корисні дані (Payload): "HELLO OSI" */
        'H', 'E', 'L', 'L', 'O', ' ', 'O', 'S', 'I'
    };

    printf("=== ДЕМОНСТРАЦІЯ РОЗБОРУ СТЕКУ CLNP / TP4 ===\n");
    
    clnp_packet_t clnp;
    if (!clnp_parse(sample_packet, sizeof(sample_packet), &clnp)) {
        printf("ПОМИЛКА: Не вдалося розібрати заголовок CLNP або пошкоджено суму!\n");
        return 1;
    }

    printf("[CLNP] NLPID: 0x%02X (CLNP)\n", clnp.nlpid);
    printf("[CLNP] Довжина заголовка: %u байтів, Повна довжина сегмента: %u байтів\n",
           clnp.header_len, clnp.segment_len);
    printf("[CLNP] Lifetime: %u (%.1f с), Прапорці: 0x%02X\n",
           clnp.lifetime, clnp.lifetime * 0.5, clnp.flags);
    
    printf("[CLNP] Призначення NSAP: ");
    print_nsap(clnp.dst_nsap, clnp.dst_nsap_len);
    printf("\n");

    printf("[CLNP] Джерело NSAP:      ");
    print_nsap(clnp.src_nsap, clnp.src_nsap_len);
    printf("\n");

    /* Розбір вкладеного TP4 */
    tp4_dt_packet_t tp4;
    if (!tp4_parse_dt(clnp.payload, clnp.payload_len, &tp4)) {
        printf("ПОМИЛКА: Не вдалося розібрати заголовок TP4!\n");
        return 1;
    }

    printf("\n[TP4] Тип TPDU: 0x%02X (Data TPDU)\n", tp4.type);
    printf("[TP4] Destination Reference: 0x%04X\n", tp4.dst_ref);
    printf("[TP4] Порядковий номер (TPDU-NR): %u, Прапорець EOT: %s\n",
           tp4.tpdu_nr, tp4.eot ? "TRUE (останній)" : "FALSE");
    printf("[TP4] Розмір корисних даних: %zu байтів\n", tp4.data_len);
    printf("[TP4] Дані: \"%.*s\"\n", (int)tp4.data_len, (const char *)tp4.data);

    return 0;
}
