/**
 * @brief Пряме кодування двох 64-бітних цілих чисел у код Кантора.
 * 
 * @param x Перше натуральне число.
 * @param y Друге натуральне число.
 * @param out_code Вказівник на змінну для збереження результату <x, y>.
 * @return int AH_SUCCESS або AH_ERR_INTEGER_OVERFLOW.
 */
int ah_cantor_encode(uint64_t x, uint64_t y, uint64_t* out_code);

/**
 * @brief Декодування коду Кантора на вихідну пару чисел (обернена бієкція).
 * 
 * @param code Код парування.
 * @param out_x Вказівник на першу відновлену змінну.
 * @param out_y Вказівник на другу відновлену змінну.
 * @return int AH_SUCCESS або AH_ERR_INVALID_ARGUMENT.
 */
int ah_cantor_decode(uint64_t code, uint64_t* out_x, uint64_t* out_y);
