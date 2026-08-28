// Складання пакета: заголовок 0xF + кількість + N повідомлень по 25 байтів.
// out — буфер, куди пишемо; повертаємо фактичну довжину пакета в байтах.
static int build_pack(uint8_t *out, int out_cap,
                      const char *uas_id, const char *operator_id,
                      const gps_fix_t *pos) {
    // 3 повідомлення: Basic ID + Location + Operator ID.
    const int n = 3;

    // Місткість буфера: 3 байти заголовка пакета + n × 25. Перевіряємо ЗАВЖДИ.
    const int need = 3 + n * ODID_MSG_SIZE;
    if (n > ODID_PACK_MAX || need > out_cap)
        return 0;               // не влізе — краще нічого, ніж поламаний пакет

    put_header(out, MSG_PACK);              // out[0]: тип 0xF, версія
    out[1] = ODID_MSG_SIZE;                 // out[1]: розмір одного повідомлення (25)
    out[2] = (uint8_t)n;                    // out[2]: скільки повідомлень далі

    uint8_t *slot = &out[3];                // перше повідомлення — одразу за заголовком
    enc_basic_id(slot, uas_id);      slot += ODID_MSG_SIZE;
    enc_location(slot, pos);         slot += ODID_MSG_SIZE;
    enc_operator(slot, operator_id); slot += ODID_MSG_SIZE;

    return need;                            // готова довжина для передачі в радіо
}
