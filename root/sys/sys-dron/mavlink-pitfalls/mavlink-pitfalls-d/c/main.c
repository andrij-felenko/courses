/* КАТАСТРОФІЧНА ПОМИЛКА: Невирівняне приведення покажчика */
void handle_raw_buffer_c(const uint8_t *raw_stream) {
    /* Заголовок MAVLink 1 має довжину 6 байтів: STX, LEN, SEQ, SYS, COMP, MSG_ID.
       Корисне навантаження починається за зміщенням raw_stream + 6. */
    const mavlink_attitude_t *att = (const mavlink_attitude_t *)(raw_stream + 6);

    /* Якщо raw_stream вирівняний на 4 байти (наприклад 0x20000000), 
       то адреса att стає 0x20000006 — НЕ КРАТНА 4! */
    float r = att->roll; /* HardFault на ARM Cortex-M0/M4! */
}
