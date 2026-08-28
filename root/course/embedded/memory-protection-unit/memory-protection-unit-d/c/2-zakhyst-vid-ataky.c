bool mpu_validate_buffer(const void *buffer, size_t length, bool write_access) {
    uintptr_t start = (uintptr_t)buffer;
    uintptr_t end   = start + length;
    if (end < start || !buffer || length == 0) return false;

    /* Перевірка чи лежить буфер у дозволеному стеку або приватній пам'яті задачі */
    if (start >= task->stack_usable_base && end <= task->stack_limit) return true;
    if (start >= task->private_data_base && end <= task->private_data_limit) return true;

    return false; /* Спроба передати покажчик на чужу пам'ять! */
}
