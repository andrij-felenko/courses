void telemetry_example(void) {
    uint8_t buffer[64];
    cbor_writer_t writer = {
        .data = buffer,
        .capacity = sizeof(buffer),
        .offset = 0
    };

    // Серіалізація словника з 3 полями:
    // { 1: 1714560000, 2: "DHT22", 3: true }
    cbor_write_map_header(&writer, 3);

    cbor_write_uint(&writer, 1); // ключ 1 (timestamp)
    cbor_write_uint(&writer, 1714560000ULL);

    cbor_write_uint(&writer, 2); // ключ 2 (sensor_name)
    cbor_write_tstr(&writer, "DHT22", 5);

    cbor_write_uint(&writer, 3); // ключ 3 (status_ok)
    cbor_write_bool(&writer, true);

    // Десеріалізація (Zero-Copy)
    cbor_reader_t reader = {
        .data = buffer,
        .size = writer.offset,
        .offset = 0
    };

    cbor_value_t item;
    if (cbor_read_next(&reader, &item) == CBOR_OK && item.type == CBOR_TYPE_MAP) {
        size_t pairs = item.as.container_len;
        for (size_t i = 0; i < pairs; ++i) {
            cbor_value_t key, val;
            cbor_read_next(&reader, &key);
            cbor_read_next(&reader, &val);

            if (key.type == CBOR_TYPE_UINT && key.as.uint_val == 2) {
                // val.as.slice вказує безпосередньо в buffer без копіювання
                const uint8_t *name_ptr = val.as.slice.ptr;
                size_t name_len = val.as.slice.len;
                (void)name_ptr;
                (void)name_len;
            }
        }
    }
}
