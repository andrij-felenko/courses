int32_t run(uint8_t *code) {
    int32_t stack[16];           // наш стек значень
    int sp = 0;                  // покажчик верхівки (скільки значень на стеку)
    uint8_t *pc = code;          // «лічильник команд»

    for (;;) {
        uint8_t op = *pc++;      // вибірка команди + зсув покажчика
        switch (op) {            // декодування й диспетчеризація
        case OP_PUSH:
            stack[sp++] = *pc++; // покласти наступний байт-число на стек
            break;
        case OP_ADD: {
            int32_t b = stack[--sp];   // зняти верхній
            int32_t a = stack[--sp];   // зняти наступний
            stack[sp++] = a + b;       // покласти суму
            break;
        }
        case OP_MUL: {
            int32_t b = stack[--sp];
            int32_t a = stack[--sp];
            stack[sp++] = a * b;       // покласти добуток
            break;
        }
        case OP_HALT:
            return stack[sp - 1];      // результат — на верхівці
        }
    }
}
