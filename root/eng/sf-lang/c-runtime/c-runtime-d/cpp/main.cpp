// Голий МК без фреймворку: _write — заглушка, що нічого не робить
// → printf форматує, але байти нікуди не йдуть.

// Щоб printf запрацював — вписати стаб під ваш UART:
extern "C" int _write(int fd, const char* buf, int len) {
    (void)fd;
    uart_send(UART_NUM_0, (const uint8_t*)buf, (size_t)len);
    return len;
}
// Тепер printf("hi\n") → _write → uart_send → UART → монітор порту.
// На ESP32 фреймворк уже поставив цю «підпірку» за вас.
