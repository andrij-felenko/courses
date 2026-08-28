/* Трансформований код після інструментування KCSAN */
void increment_counter(u32 *counter_ptr) {
    u32 val;

    /* 1. Інструментування читання */
    __tsan_read4(counter_ptr);
    val = *counter_ptr;

    val += 1;

    /* 2. Інструментування запису */
    __tsan_write4(counter_ptr);
    *counter_ptr = val;
}
