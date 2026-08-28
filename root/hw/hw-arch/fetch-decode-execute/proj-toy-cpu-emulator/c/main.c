uint8_t r[4]    = {0};   // регістри загального призначення
uint8_t mem[256] = {0};  // пам'ять для даних
uint8_t code[]  = { … };  // програма: потік байтів-команд
int ip = 0;              // лічильник команд PC
int running = 1;

while (running) {                          // ── серцебиття ──
    uint8_t op = code[ip++];               // ВИБІРКА: байт за PC, PC += 1
    int d, s, a, n;                        // ДЕКОДУВАННЯ + ВИКОНАННЯ:
    switch (op) {
        case LD:  d=code[ip++]; n=code[ip++];  r[d] = n;          break;
        case LDM: d=code[ip++]; a=code[ip++];  r[d] = mem[a];     break;
        case ST:  s=code[ip++]; a=code[ip++];  mem[a] = r[s];     break;
        case ADD: d=code[ip++]; s=code[ip++];  r[d] = r[d]+r[s];  break;
        case SUB: d=code[ip++]; s=code[ip++];  r[d] = r[d]-r[s];  break;
        case JMP: a=code[ip++];                ip = a;            break;
        case JNZ: s=code[ip++]; a=code[ip++];  if (r[s]) ip = a;  break;
        case HLT:                              running = 0;       break;
    }
}
