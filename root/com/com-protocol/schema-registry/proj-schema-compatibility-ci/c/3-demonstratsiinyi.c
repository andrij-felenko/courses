int main(void) {
    printf("=== ТЕСТ 1: Перевірка кадрування Wire Format ===\n");
    uint32_t original_schema_id = 42;
    const uint8_t raw_data[] = {0xDE, 0xAD, 0xBE, 0xEF};
    size_t encoded_len = 0;

    uint8_t *frame = wire_encode(original_schema_id, raw_data, sizeof(raw_data), &encoded_len);
    printf("Закодовано кадр довжиною: %zu байтів\n", encoded_len);

    uint32_t decoded_schema_id = 0;
    const uint8_t *decoded_payload = NULL;
    size_t decoded_payload_len = 0;

    if (wire_decode(frame, encoded_len, &decoded_schema_id, &decoded_payload, &decoded_payload_len)) {
        printf("✓ Успішне декодування: Schema ID = %u, Payload Len = %zu\n", decoded_schema_id, decoded_payload_len);
    } else {
        printf("✗ Помилка декодування кадру!\n");
    }
    free(frame);

    printf("\n=== ТЕСТ 2: Перевірка валідатора сумісності ===\n");
    RecordSchema v1 = {
        .fields = {
            {"order_id", TYPE_INT64, false},
            {"amount_cents", TYPE_INT32, false}
        },
        .field_count = 2
    };

    /* Схема V2 з валідною зміною: розширення типу та нове поле з дефолтом */
    RecordSchema v2_valid = {
        .fields = {
            {"order_id", TYPE_INT64, false},
            {"amount_cents", TYPE_INT64, false}, // int32 -> int64 (OK)
            {"currency", TYPE_STRING, true}      // нове поле з дефолтом (OK)
        },
        .field_count = 3
    };

    char err_buf[256];
    if (validate_backward_compatibility(&v1, &v2_valid, err_buf, sizeof(err_buf))) {
        printf("✓ Схема V2 визнана повністю сумісною (BACKWARD)\n");
    } else {
        printf("✗ Помилка валідації: %s\n", err_buf);
    }

    /* Схема V3 з небезпечною зміною: нове поле без дефолту */
    RecordSchema v3_broken = {
        .fields = {
            {"order_id", TYPE_INT64, false},
            {"amount_cents", TYPE_INT32, false},
            {"mandatory_tax_code", TYPE_STRING, false} // НЕМАЄ ДЕФОЛТУ!
        },
        .field_count = 3
    };

    if (!validate_backward_compatibility(&v1, &v3_broken, err_buf, sizeof(err_buf))) {
        printf("✓ Валідатор успішно заблокував дефектну схему: %s\n", err_buf);
    } else {
        printf("✗ Помилка: валідатор пропустив небезпечну схему!\n");
    }

    return 0;
}
