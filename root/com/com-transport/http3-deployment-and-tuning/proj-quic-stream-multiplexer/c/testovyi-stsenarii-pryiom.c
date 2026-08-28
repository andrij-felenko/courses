int main(void) {
    quic_stream_t stream;
    quic_stream_init(&stream, 0, 65536); // Stream 0 (Client Bidi), Max Data 64KB

    printf("=== ДЕМОНСТРАЦІЯ ДЕФРАГМЕНТАЦІЇ QUIC ТА QPACK (C) ===\n\n");

    /* 1. Прибуває датаграма 2 (зсув 10..21) — дірка попереду */
    uint8_t pkt2_data[] = "World_HTTP3!";
    printf("1. Отримано пакет 2 (Offset=10, Len=12)\n");
    quic_stream_insert_frame(&stream, 10, pkt2_data, sizeof(pkt2_data) - 1, false);

    uint8_t out_buf[128];
    size_t n = quic_stream_read_contiguous(&stream, out_buf, sizeof(out_buf));
    printf("   Прочитано байтів: %zu (очікуємо 0 через дірку на Offset=0)\n\n", n);

    /* 2. Прибуває датаграма 1 (зсув 0..9) з індексом QPACK 15 (GET) */
    uint8_t pkt1_data[] = {0x0F, 'H', 'e', 'l', 'l', 'o', '_', 'Q', 'U', 'I'};
    printf("2. Отримано пакет 1 (Offset=0, Len=10)\n");
    quic_stream_insert_frame(&stream, 0, pkt1_data, sizeof(pkt1_data), false);

    n = quic_stream_read_contiguous(&stream, out_buf, sizeof(out_buf));
    printf("   Прочитано байтів: %zu (дірку заповнено!)\n", n);
    if (n > 0) {
        qpack_decode_static_indexed(out_buf[0]); // Перший байт — QPACK Index 15
        printf("   Вміст потоку: %.*s\n\n", (int)(n - 1), out_buf + 1);
    }

    quic_stream_free(&stream);
    return 0;
}
