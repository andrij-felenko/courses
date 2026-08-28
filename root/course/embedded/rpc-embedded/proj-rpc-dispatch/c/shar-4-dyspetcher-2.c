// Виконати функцію за номером. Заповнює *value й повертає код результату.
// func ПРИЙШОВ ІЗ ДРОТУ — перевіряємо межу, перш ніж торкатись таблиці.
static uint8_t dispatch(uint8_t func, int32_t arg, int32_t *value) {
    if (func >= RPC_COUNT) {               // номера такого нема в таблиці
        *value = 0;
        return RPC_ERR_BADFUNC;            // НЕ чіпаємо TABLE[func]!
    }
    *value = TABLE[func](arg);             // увесь диспетчер — цей рядок
    return RPC_OK;
}
