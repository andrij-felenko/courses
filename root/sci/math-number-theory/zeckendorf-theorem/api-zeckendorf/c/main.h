/**
 * @brief Кодує число N у розклад Цекендорфа (бітовий масив)
 * @param n Число для кодування (N >= 1)
 * @param out_bits Вказівник на масив для запису бітів (0 або 1)
 * @param max_len Розмір масиву out_bits
 * @param out_len Вказівник на змінну для запису кількості записаних бітів
 * @return ZECK_SUCCESS або відповідний код помилки
 */
ZeckStatus zeckendorf_encode_raw(uint64_t n, uint8_t *out_bits, size_t max_len, size_t *out_len);

/**
 * @brief Декодує бітовий масив Цекендорфа у 64-бітове ціле число
 * @param bits Вказівник на бітовий масив
 * @param len Кількість бітів у масиві
 * @param out_n Вказівник на змінну для результату
 * @return ZECK_SUCCESS або ZECK_ERROR_INVALID_STREAM (якщо виявлено сусідні одиниці)
 */
ZeckStatus zeckendorf_decode_raw(const uint8_t *bits, size_t len, uint64_t *out_n);
